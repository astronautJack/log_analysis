---
description: 日志问题定位（WF）。log-triage 流分长日志 → wiki-reader 取上下文 → code-tracer 沿代码图回溯定位 file:line → 自校正复核 → 报告。只定位不分类。
agent: logscope-dev
---
定位日志问题到代码行。

参数：$ARGUMENTS
用法：/diag <日志文件路径|日志文本> [--repo <repo>] [--wiki <wiki>]
- 日志：文件绝对路径，或用引号包的文本
- --repo：相关代码仓绝对路径（必填）
- --wiki：目标仓的 wiki 目录（可选，有则用、无则退回源码）

流程（logscope-dev 编排）：log-triage 长日志→有界 digest+预览指针（原始日志落 /tmp/logscope/，不灌上下文）→ wiki-reader 取调用链/契约 → code-tracer CRG 新鲜度门+search/query callers_of/impact/flow 定位 file:line → 自校正复核证据链（≤3 次）→ 报告（哪行+置信度+证据链 log行号+file:line+图边）→ 🛑人审。
