# LogScope 依赖

三个外部依赖（`setup.sh` / `setup.ps1` 一键装）：

| 依赖 | 生态 | 装法 | 落点 |
|---|---|---|---|
| **code-review-graph** (CRG) | Python（PyPI） | `uv tool install code-review-graph` | `~/.local/bin/code-review-graph` |
| **opencode-dcp** (DCP) | JS（npm） | `npm install -g @tarquinen/opencode-dcp@latest` | npm 全局 + 项目 `opencode.json` 的 `plugin` 引用 |
| **logscope-triage** | Python（本仓自产） | `uv tool install --force .`（from 仓根 `pyproject.toml`） | `~/.local/bin/logscope-triage` |

**为什么不能统一 npm**：CRG + logscope-triage 是 Python（PyPI/uv），DCP 是 JS（npm）。所以 setup 用 **uv + npm 混合**。

## 前置

- **node ≥ 18 / npm**：DCP 用（node 自带 npm）。
- **uv**：CRG + logscope-triage 用；装法见 README（`curl -LsSf https://astral.sh/install.sh | sh` / Win `irm https://astral.sh/install.ps1 | iex`）。
- **git**：agent 用。
- **opencode** ≥ 1.18。
- **glm-5.2 端点**：公司内网 LLM（全局 opencode 配置提供）。

## 跑 setup

```bash
# Linux/macOS
bash .opencode/setup.sh
# Windows PowerShell
.\\.opencode\\setup.ps1
```

## 落点说明

- CRG / logscope-triage：`~/.local/bin/`（确保在 PATH；uv 安装器通常已加）。
- DCP：npm 全局 + 项目 `opencode.json` 的 `"plugin": ["@tarquinen/opencode-dcp@latest"]` 引用（跟 `.opencode` 走）。
- **模板库**：`~/.logscope/templates/`（home，跨 cwd/run/Windows 累积，不入仓）。
- **临时日志**：`~/.logscope/tmp/`（home，跨平台）。

## 改源后重装

- logscope-triage 改 `src/logscope_triage/` 后：`uv tool install --force .`（或重跑 setup）。
- agents/commands/config 改后：**重启 opencode** 才生效（配置启动时加载一次）。
- DCP 阈值改 `~/.config/opencode/dcp.jsonc` 后：**重启 opencode** 才生效（否则旧固定阈值误触压缩）。
