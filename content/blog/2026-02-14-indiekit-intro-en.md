---
title: "IndieKit: 8 AI Tools Built in One Night"
date: 2026-02-14
description: "Free and open source toolkit for indie hackers. URL shortener, uptime monitoring, webhook relay, and more."
tags: ["IndieKit", "tools", "open source", "English"]
lang: en
---

I challenged myself: how many useful tools could I build in one session using Claude Code CLI?

The result: **8 working tools**, all deployed and running.

## The Tools

| Tool | What it does | URL |
|------|--------------|-----|
| **HN Digest** | AI-generated Chinese summaries of Hacker News | [hn.indiekit.ai](https://hn.indiekit.ai) |
| **Uptime Ping** | API monitoring with Telegram alerts | [up.indiekit.ai](https://up.indiekit.ai) |
| **Webhook Relay** | Forward any webhook to Telegram | [hook.indiekit.ai](https://hook.indiekit.ai) |
| **Tiny Link** | URL shortener with click stats | [s.indiekit.ai](https://s.indiekit.ai) |
| **Quick Paste** | Pastebin with syntax highlighting | [p.indiekit.ai](https://p.indiekit.ai) |
| **AI CS SaaS** | Multi-tenant AI customer service with RAG | [cs.indiekit.ai](https://cs.indiekit.ai) |
| **Doc2MD** | Convert PDF/Word/HTML to Markdown | [d.indiekit.ai](https://d.indiekit.ai) |
| **MCP Servers** | Let Claude Desktop use these tools directly | [/mcp](/mcp) |

## Tech Stack

- **Python + FastAPI** - Simple and fast
- **PostgreSQL + pgvector** - For RAG embeddings
- **Gemini API** - Text embeddings
- **JSON storage** - For simple tools (no DB overhead)
- **Cloudflare** - DNS, CDN, SSL

Total: ~7,000 lines of code.

## All on PyPI

```bash
pip install indiekit-doc2md
pip install indiekit-mcp
pip install indiekit-notion-mcp
pip install indiekit-hn-digest
pip install indiekit-uptime-ping
pip install indiekit-webhook-relay
pip install indiekit-tiny-link
pip install indiekit-quick-paste
```

## What Worked

1. **Clear specs upfront** → better AI output
2. **Small iterations** → catch bugs early
3. **JSON for MVPs** → no database overhead
4. **Build for agents** → MCP support from day one

## Cost

- Domain: $35/year
- Server: $6/month
- API calls: ~$10/month

Under $20/month total.

## Open Source

Everything is on GitHub: [github.com/indiekitai](https://github.com/indiekitai)

Feel free to use, fork, or contribute!

---

**Try it**: [indiekit.ai](https://indiekit.ai)
