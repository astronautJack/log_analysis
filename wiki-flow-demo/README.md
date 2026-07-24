---
title: multimedia_av_session 业务流 wiki
source_repo: multimedia_av_session
crg_commit: a4ec47de96f7
generated_by: /wiki-flow
generated_at: 2026-07-24
flows_total: 50
flows_indexed: 44
flows_skipped: 6
pages: 8
error_points: 49
error_events: 13
---

# multimedia_av_session 业务流 wiki

由 `/wiki-flow` 基于 CRG 代码图 + `hisysevent.yaml` 自动生成，供 `/diag` 的 **wiki-reader 索引式检索**使用：日志报错 → 查事件名 → 直达 `file:line` + 调用链上下文。

## 生成元信息

- 源仓：`multimedia_av_session`（OpenHarmony AVSession / 投屏，cpp + js + c，567 文件）
- CRG commit：`a4ec47de96f7`（8282 节点 / 74273 边，图已新鲜，未触发 build/update）
- 覆盖流：50 个执行流按业务前缀分组成 8 个生命周期
  - 已索引：44 个业务流
  - 跳过：6 个纯 fuzz/test 流（`LLVMFuzzerTestOneInput` ×4、`AVServiceProxySendRequestTest`、`AvSessionCallbackClientTests`）
- 错误索引：49 条去重 HiSysEvent 上报点，覆盖 13 个事件
- 生成方式：2 个 flow-writer subagent 并行写 8 页 + 主编排聚合 `error_index.md`

## 业务流页索引

| 业务流页 | 业务域 | 生命周期 | 流数 | 主要错误/诊断事件 |
|---|---|---|---|---|
| [cast-lifecycle.md](cast-lifecycle.md) | Cast | 投屏发起 → 远端音频投递 → 投屏控制器建立与命令同步 | 5 | `REMOTE_CONTROL_FAILED`、`SESSION_CAST`、`SESSION_CAST_CONTROL` |
| [device-connect-lifecycle.md](device-connect-lifecycle.md) | DeviceConnect | SA 启动 → 服务/代理连接 → 设备就绪 → 离线通知 | 7 | `SESSION_SERVICE_START`、`FOCUS_CHANGE` |
| [command-control-lifecycle.md](command-control-lifecycle.md) | CommandControl | 系统命令下发 → 支持命令增删 → 命令校验/统计 | 5 | `CONTROL_PERMISSION_DENIED`、`CONTROL_COMMAND_FAILED`、`CONTROL_COMMAND_FAILED_RATE` |
| [event-callback-lifecycle.md](event-callback-lifecycle.md) | EventCallback | 事件接收 → 媒体/元数据变更 → 焦点/状态上报 | 8 | `FOCUS_CHANGE`、`AVSESSION_WRONG_STATE`、`PLAYING_AVSESSION_STATS` |
| [avsession-lifecycle.md](avsession-lifecycle.md) | AVSession | 会话初始化 → 激活/历史获取 → 销毁/迁移 | 8 | `SESSION_API_BEHAVIOR`、`SESSION_LIFECYCLE_STATISTICS`、`CONTROL_COMMAND_FAILED` |
| [client-listener-lifecycle.md](client-listener-lifecycle.md) | ClientListener | 客户端死亡观察 → 监听初始化 → 队列推进 | 3 | `CONTROL_COMMAND_FAILED`（死亡注册失败；其余仅 hilog） |
| [ui-frontend-lifecycle.md](ui-frontend-lifecycle.md) | UIFrontend | 前端 UI 状态/标题构建（HomeMusic / VolumePanel） | 4 | 无 FAULT/SECURITY（纯前端 JS 本地逻辑） |
| [serialization-lifecycle.md](serialization-lifecycle.md) | Serialization | 数据 marshalling → 存储事件上报 | 4 | `PLAYING_AVSESSION_STATS`（存储超限/周期上报） |

## 错误索引（/diag 入口）

➡️ [error_index.md](error_index.md)

按 HiSysEvent 事件名分节，每条给出：上报 `file:line` · 类型 · 级别 · 触发流 · 错误条件 · 所在业务流页。跨多页的同一上报点已去重合并。

## 如何被 /diag 使用

1. `/diag <日志> --repo multimedia_av_session`
2. log-triage 把长日志压成 digest，标出 claimed error 的 **HiSysEvent 事件名**（如 `CONTROL_PERMISSION_DENIED`）。
3. wiki-reader 先查小索引 `error_index.md` → 命中事件名 → 直接拿到上报 `file:line` + 触发流 + 所在业务流页（不必读全量 wiki）。
4. 需要调用链上下文时，按需读单页的 mermaid 调用序列 + 逐步错误上报，定位近一步到位。

## 每页结构

- **frontmatter**：`business_domain` / `lifecycle` / `flows` / `entry_points` / `hisysevent_events` / `crg_commit`
- **概述**：该生命周期干什么、关键入口、典型报错方向
- **调用序列**：mermaid `flowchart LR`，节点 = `函数名<br/>相对路径:行号`，按 CRG flow path 顺序连接；单域多流时分段，超 15 步截断
- **逐步错误上报**：按调用序列顺序，列出每步可能抛的错 / 上报的 HiSysEvent + `file:line` + 错误条件（引源码行）
- **错误目录**：表格 + `<!-- ERR: 事件|类型|级别|流|file:line|条件 -->` 锚点（聚合工具按锚点扫 `error_index.md`）

## 重新生成

```bash
# 在 logscope-dev opencode 会话里
/wiki-flow /tmp/opencode/multimedia_av_session /home/dlrow_hl/log_analysis/wiki-flow-demo
```

改仓内代码后：先 `code-review-graph update --repo <R>` 刷新图，再重跑 `/wiki-flow`（会按最新 commit 重写各页 frontmatter 的 `crg_commit`）。
