# IndieKit

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

独立开发者的 AI 工具包。

**Live**: https://indiekit.ai

## 🔧 工具

| 工具 | 描述 | URL |
|------|------|-----|
| HN Digest | AI 中文 HN 每日精选 | [hn.indiekit.ai](https://hn.indiekit.ai) |
| Uptime Ping | API 健康监控 + Telegram 告警 | [up.indiekit.ai](https://up.indiekit.ai) |
| Webhook Relay | Webhook 转发到 Telegram | [hook.indiekit.ai](https://hook.indiekit.ai) |
| Tiny Link | 短链接 + 点击统计 | [s.indiekit.ai](https://s.indiekit.ai) |
| Quick Paste | 代码分享 + 语法高亮 | [p.indiekit.ai](https://p.indiekit.ai) |
| AI CS SaaS | 多租户 AI 客服 + RAG | [cs.indiekit.ai](https://cs.indiekit.ai) |
| Doc2MD | PDF/Word/网页 → Markdown | [d.indiekit.ai](https://d.indiekit.ai) |

## 📦 MCP Servers

让 AI Agent 直接使用这些工具：

```bash
pip install indiekit-mcp
pip install indiekit-notion-mcp
pip install indiekit-doc2md
```

## 🚀 本地运行

```bash
cd indiekit-site
uv sync
uv run uvicorn src.main:app --reload --port 8085
```

## License

MIT
