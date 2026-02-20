# Show HN Draft (Updated 2026-02-13)

## Title

**Show HN: IndieKit – 8 AI tools I built in one night, all free and open source**

---

## Post Body

Hey HN,

I challenged myself: how many useful tools could I build in one session using Claude Code CLI?

Result: **8 working tools**, all deployed at https://indiekit.ai:

1. **HN Digest** (hn.indiekit.ai) – AI-generated Chinese summaries of top HN stories
2. **Uptime Ping** (up.indiekit.ai) – API monitoring with Telegram alerts
3. **Webhook Relay** (hook.indiekit.ai) – Forward any webhook to Telegram
4. **Tiny Link** (s.indiekit.ai) – URL shortener with analytics
5. **Quick Paste** (p.indiekit.ai) – Code sharing with syntax highlighting
6. **AI CS SaaS** (cs.indiekit.ai) – Multi-tenant AI customer service with RAG
7. **Doc2MD** (d.indiekit.ai) – Convert PDF/Word/HTML/URLs to Markdown (supports Cloudflare's Markdown for Agents)
8. **MCP Servers** – Let Claude Desktop directly use these tools via Model Context Protocol

**Stack**: Python/FastAPI, PostgreSQL+pgvector, Gemini API, Cloudflare, ~7,000 lines total.

**All published to PyPI**:
- `pip install indiekit-doc2md`
- `pip install indiekit-mcp`
- `pip install indiekit-notion-mcp`

**What worked**:
- Clear specs upfront → better AI output
- Small iterations → catch bugs early
- JSON storage for MVPs → no DB overhead
- Building for agents, not just humans (MCP support)

**Costs**: $35/yr domain, $6/mo server, ~$10 API calls. Under $20/mo total.

GitHub: https://github.com/indiekitai

Questions:
- Which tools would you actually use?
- What's missing for indie hackers?
- Is "agent-first" tooling the next wave?

---

## 发布步骤

1. 去 https://news.ycombinator.com/submit
2. Title: `Show HN: IndieKit – 8 AI tools I built in one night, all free and open source`
3. URL: `https://indiekit.ai`
4. 点 Submit
5. 然后在评论区贴 Post Body 内容
