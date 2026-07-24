#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""drain3_triage.py — Drain3 日志结构化 + **跨 run 持久化模板**。

用户每次 /diag 调本脚本，模板自动存到 `templates/<profile>.json` 并跨 run 累积：
  - pre-existing 簇 = 已知模式（之前 run 见过）
  - 本次「新见」簇（change_type=cluster_created）= 潜在异常/信号，单独高亮

用法:
  uv run --with drain3 python scripts/drain3_triage.py <logfile> [--top N] [--profile NAME]
  --profile 默认 = 日志文件名（去扩展名）。模板库落 `templates/<profile>.json`。

只喂 hilog 的 message 给 Drain3；HiSysEvent JSON + faultlog 栈帧单独结构化。
"""
import sys
import re
import json
import os
import argparse
from drain3 import TemplateMiner

try:
    from drain3.file_persistence import FilePersistence
    _HAS_PERSIST = True
except Exception:
    _HAS_PERSIST = False

HILOG_RE = re.compile(
    r'^(\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d+)\s+(\d+)\s+(\d+)\s+([DIWEF])\s+'
    r'([AC0D][0-9A-F]{3,5})/([^:]+):\s*(.*)$'
)
NATIVE_RE = re.compile(
    r'^\s*#(\d+)\s+pc\s+([0-9a-f]{8,16}|0x[0-9a-f]+)\s+(\S+\.so)(\([0-9a-f]+\))?'
)
ARKTS_RE = re.compile(
    r'^\s*at\s+(\S+)(?:\s+(\S+))?\s+\(([^:]+):(\d+):(\d+)\)'
)

PROFILE_DIR = os.path.expanduser("~/.logscope/templates")


def get_miner(profile):
    """带持久化的 TemplateMiner——跨 run 累积模板。"""
    if _HAS_PERSIST and profile:
        os.makedirs(PROFILE_DIR, exist_ok=True)
        path = os.path.join(PROFILE_DIR, f"{profile}.json")
        return TemplateMiner(persistence_handler=FilePersistence(path)), path
    return TemplateMiner(), None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('logfile')
    ap.add_argument('--top', type=int, default=50)
    ap.add_argument('--profile', default=None,
                    help='模板库名（默认=日志文件名去扩展名）；落 templates/<profile>.json')
    args = ap.parse_args()

    if args.profile is None:
        args.profile = os.path.splitext(os.path.basename(args.logfile))[0]

    miner, db_path = get_miner(args.profile)

    clusters = {}      # cid -> {template, size, rep_line_no, rep_raw, domain, tag, level, is_new}
    new_clusters = []  # 本次新见的簇 cid（change_type=cluster_created）
    hisysevents = []
    fault_frames = []
    line_no = 0
    fed = 0

    def feed(content, line_no, line, dom='', tag='', lvl=''):
        nonlocal fed
        r = miner.add_log_message(content)
        cid = r['cluster_id']
        is_new = (r.get('change_type') == 'cluster_created')
        if cid not in clusters:
            clusters[cid] = {'template': r['template_mined'], 'size': r['cluster_size'],
                             'rep_line_no': line_no, 'rep_raw': content,
                             'domain': dom, 'tag': tag, 'level': lvl, 'is_new': is_new}
            if is_new:
                new_clusters.append(cid)
        else:
            clusters[cid]['size'] = r['cluster_size']
            clusters[cid]['template'] = r['template_mined']
        fed += 1

    with open(args.logfile, encoding='utf-8', errors='replace') as f:
        for raw in f:
            line_no += 1
            line = raw.rstrip('\n')
            if not line.strip():
                continue

            if line.lstrip().startswith('{'):
                try:
                    obj = json.loads(line)
                    if 'domain' in obj and 'name' in obj:
                        hisysevents.append((line_no, obj.get('domain', ''), obj.get('name', ''),
                                            obj.get('type', ''), obj.get('level', ''),
                                            obj.get('params', {})))
                        continue
                except Exception:
                    pass

            m = HILOG_RE.match(line)
            if m:
                _dt, _pid, _tid, lvl, dom, tag, msg = m.groups()
                feed(msg, line_no, line, dom, tag, lvl)
                continue

            nm = NATIVE_RE.match(line)
            if nm:
                fault_frames.append(('native', line_no, nm.group(1), nm.group(2), nm.group(3), nm.group(4) or ''))
                continue
            am = ARKTS_RE.match(line)
            if am:
                fault_frames.append(('arkts', line_no, am.group(1), am.group(2) or '', am.group(3), am.group(4), am.group(5)))
                continue

            feed(line, line_no, line)

    # ---- 输出 ----
    persist_note = f"（持久化：{db_path}，跨 run 累积）" if db_path else "（无持久化）"
    print(f"=== Drain3 结构化：{line_no} 行 / 喂 {fed} 行 → {len(clusters)} 模板簇 {persist_note} ===\n")

    if new_clusters:
        print(f"=== ⚠ 本次新见 {len(new_clusters)} 簇（pre-existing 之外的新模式=潜在信号）===")
        for cid in new_clusters:
            c = clusters[cid]
            meta = f"dom={c['domain']} tag={c['tag']} lvl={c['level']}" if c['domain'] else 'plain'
            print(f"[c{cid}] {meta}")
            print(f"    template: {c['template']}")
            print(f"    rep@L{c['rep_line_no']}: {c['rep_raw'][:120]}")
        print()

    print("=== 全部模板簇（按 size 降序）===")
    for cid, c in sorted(clusters.items(), key=lambda kv: -kv[1]['size'])[:args.top]:
        meta = f"dom={c['domain']} tag={c['tag']} lvl={c['level']}" if c['domain'] else 'plain'
        tag_new = " [NEW]" if c['is_new'] else ""
        print(f"[c{cid}] size={c['size']}{tag_new} {meta}")
        print(f"    template: {c['template']}")
        print(f"    rep@L{c['rep_line_no']}: {c['rep_raw'][:120]}")

    if hisysevents:
        print(f"\n=== HiSysEvent 事件（{len(hisysevents)} 条）===")
        for ln, dom, name, typ, lvl, params in hisysevents:
            keys = {k: params[k] for k in ('FILE', 'LINE', 'CALLER', 'REASON', 'MSG', 'FUNCTION') if k in params}
            print(f"L{ln} [{typ}/{lvl}] {dom}/{name} 锚点={json.dumps(keys, ensure_ascii=False)}")

    if fault_frames:
        print(f"\n=== faultlog 栈帧（{len(fault_frames)} 条）===")
        for fr in fault_frames:
            if fr[0] == 'native':
                print(f"L{fr[1]} native #{fr[2]} pc={fr[3]} so={fr[4]} buildId={fr[5]}")
            else:
                print(f"L{fr[1]} arkts at {fr[2]} {fr[3]} ({fr[4]}:{fr[5]}:{fr[6]})")


if __name__ == '__main__':
    main()
