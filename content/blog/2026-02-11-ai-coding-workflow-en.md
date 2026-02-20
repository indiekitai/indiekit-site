---
title: "How I Built 8 SaaS Tools in One Night with AI"
date: 2026-02-11
description: "My workflow for building with Claude Code CLI. From idea to deployment in hours, not weeks."
tags: ["AI", "coding", "workflow", "English"]
lang: en
---

People ask how I built 8 tools so fast. Here's the workflow.

## The Setup

- **Editor**: Claude Code CLI (terminal-based)
- **Stack**: Python + FastAPI (simple, fast)
- **Hosting**: Single $6/month VPS
- **Deploy**: systemd (no Docker complexity)

## The Process

### 1. Start with a Clear Spec

Don't say "build me a URL shortener."

Say:
```
Build a URL shortener with:
- POST /api/links - create short link
- GET /{code} - redirect
- GET /api/links/{code}/stats - click stats
- JSON file storage in data/
- FastAPI + uvicorn
```

The clearer your spec, the better the output.

### 2. Small Iterations

Don't try to build everything at once.

```
1. Basic redirect working? ✓
2. Add stats tracking
3. Add custom codes
4. Add expiration
```

Test each piece before moving on.

### 3. Let AI Handle Boilerplate

AI excels at:
- Project structure
- Error handling
- API documentation
- Standard patterns

You focus on:
- Business logic decisions
- Edge cases
- Integration points

### 4. JSON for MVPs

PostgreSQL is overkill for most MVPs.

```python
# This is enough for thousands of users
with open("data/links.json", "r") as f:
    links = json.load(f)
```

Migrate to a database when you actually need it.

### 5. Deploy Simply

```bash
# /etc/systemd/system/myapp.service
[Service]
ExecStart=/usr/bin/uvicorn src.main:app --port 8080
Restart=always
```

That's it. No Kubernetes. No Docker compose files.

## What I Learned

### AI is Good At:
- Generating code from specs
- Following patterns
- Writing tests
- Documentation

### AI Needs Help With:
- Architecture decisions
- Understanding your specific context
- Edge cases you haven't mentioned
- Integration with existing systems

### The Multiplier Effect

A single developer with AI can:
- Prototype in hours, not days
- Ship more features
- Maintain larger codebases
- Focus on what matters

But you still need to:
- Know what to build
- Review the output
- Handle deployment
- Talk to users

## My Stack for Fast Shipping

| Layer | Choice | Why |
|-------|--------|-----|
| Language | Python | Fast to write, AI knows it well |
| Framework | FastAPI | Async, auto-docs, simple |
| Storage | JSON → PostgreSQL | Start simple, scale when needed |
| Deploy | systemd | Zero overhead |
| CDN | Cloudflare | Free, fast, secure |

## Try It Yourself

1. Pick a small problem
2. Write a clear spec
3. Use Claude Code or similar
4. Ship in a day

The barrier to building is lower than ever. Go make something.

---

**See what I built**: [indiekit.ai](https://indiekit.ai)

**GitHub**: [indiekitai](https://github.com/indiekitai)
