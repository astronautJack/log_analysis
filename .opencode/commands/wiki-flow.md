---
description: 生成业务流 wiki（按生命周期组织调用链 + 错误目录，给 /diag 当 log→code 直达电梯）。
agent: logscope-dev
---
为代码仓生成业务流 wiki。

参数：$ARGUMENTS
用法：/wiki-flow <repo> [out-dir] [flow-prefix]
- repo：目标仓绝对路径（必填）
- out-dir：wiki 输出目录（**默认当前 opencode 打开目录**，即 cwd）
- flow-prefix：只生成某业务域（如 `Cast`/`StartCast`/`AVSession`），省略 = 全部流自动按前缀分组

流程（logscope-dev → flow-writer）：CRG 新鲜度门（问用户 build/update/不跑）→ `flows` 取执行流按前缀分组成生命周期 → 每生命周期 `flow --source` + `query callees_of` 下钻 + grep HiSysEvent/hilog 报错点 → 写页（调用序列 mermaid + 逐步错误上报 + 错误目录 + frontmatter）→ `error_index.md`（聚合错误目录，给 /diag 索引式检索）+ `README` 索引。

> 生成后 `/diag` 的 wiki-reader 读这些业务流页：日志报错 → 查错误目录 → 直达 `file:line` + 调用链上下文，定位近一步到位。
