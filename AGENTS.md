# LogScope — 日志问题定位 agent

基于 opencode，输入**长日志 + 相关代码库**，定位到**哪一行代码**有问题。与 Rei 同级独立项目（不交叉）。

## 成品接线（不自造）

| 角色 | 成品 | 形态 |
|---|---|---|
| 代码图 + 回溯 | **code-review-graph**（CRG） | CLI `code-review-graph`（`~/.local/bin/`），`--repo <R>` 任意路径 |
| 上下文兜底 | **opencode-dcp**（DCP） | 全局插件，自动 |
| 日志结构化（v1） | bash grep+sed 模板归并（借 Drain3 思路） | log-triage 内置；升级可装 Drain3 或接 MCP log server |

## 核心思想

**日志是数据源，不是上下文。** 先 `log-triage` 把长日志压成有界 digest（错误/栈帧/时间线/符号，~28:1 压缩）→ 用 digest 里的符号让 `code-tracer` 沿 CRG 代码图反向回溯 → 定位 `file:line`。**只定位，不分类**（不判我方/客户/报错≠现象——代码不管谁的都丢进来分析）。

## 用法

- 命令：`/diag <日志文件|文本> --repo <R> [--wiki <W>]`
- CRG 子命令（code-tracer 用，都带 `--repo <R>`）：`build` / `update` / `status` / `detect-changes --brief` / `search` / `query callers_of` / `impact` / `flow` / `visualize`。
- CRG 不在 PATH 时用全路径 `$HOME/.local/bin/code-review-graph`（Windows 生产走 Git Bash，`$HOME` 解析为 `C:\Users\<你>`，Git Bash 自动补 `.exe`，写法不变）。
- 改完 `.opencode/` 或 `opencode.json` 后**重启 opencode** 才生效（配置仅启动时加载一次）。

## 约定

- **只定位不分类**：目标就是定位到代码行，不做责任归属。
- **不自动 commit/push**：只产报告，修复留给人。
- **日志可能含客户数据**：分析在本机/内网；代码不外发；LLM 走公司内网 glm-5.2。
- **经验沉淀进 `完成情况.md`**，不灌本文件 / skills。

## 模型配置

`model` / `small_model` 由全局 opencode 配置提供（指向公司内网 glm-5.2 端点）。本仓 `opencode.json` 不写死模型。
