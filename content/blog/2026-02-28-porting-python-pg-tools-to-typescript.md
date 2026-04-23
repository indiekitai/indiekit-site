---
title: "I Ported Python's Best PostgreSQL Tools to TypeScript"
slug: porting-python-pg-tools-to-typescript
date: 2026-02-28
tags: [postgresql, typescript, open-source, developer-tools]
description: "Python has schemainspect, migra, pg_activity for PostgreSQL. TypeScript had nothing comparable. So I ported them all into one toolkit."
---

# I Ported Python's Best PostgreSQL Tools to TypeScript

Python has excellent PostgreSQL tooling — [schemainspect](https://github.com/djrobstep/schemainspect), [migra](https://github.com/djrobstep/migra), [pg_activity](https://github.com/dalibo/pg_activity). TypeScript has... not much. So I ported them.

## The Gap

If you're a Node/TypeScript developer working with PostgreSQL, your options are slim:

- **Schema inspection?** Write raw `information_schema` queries or pull in Prisma just for introspection
- **Schema diff?** Nothing. Compare manually or switch to Python
- **Health checks?** Copy-paste SQL snippets from Stack Overflow
- **Activity monitoring?** Open pgAdmin or SSH into the server

Python developers have had elegant, composable solutions for years. I wanted the same thing in TypeScript.

## What I Built

[**pg-toolkit**](https://github.com/indiekitai/pg-toolkit) — one CLI and SDK that brings 5 PostgreSQL tools together:

```bash
npx @indiekitai/pg-toolkit doctor postgres://localhost/mydb
```

```
🏥 Database Health Report — mydb
Overall Score: 82/100

✅ Cache Hit Ratio .............. 99.2%  (excellent)
⚠️  Unused Indexes .............. 3 found
✅ Connection Usage ............. 12/100
❌ Table Bloat .................. 2 tables need VACUUM
✅ Long Transactions ............ none

📋 Fix Script Generated → fix.sql (4 statements)
```

Five commands, each solving a real problem:

1. **doctor** — 20+ health checks, 0–100 scoring, auto-generated fix SQL
2. **inspect** — Full schema inspection: tables, views, functions, indexes, enums, triggers, RLS policies
3. **diff** — Compare two databases, output migration SQL (ALTER/CREATE/DROP)
4. **top** — Real-time activity monitor, like `htop` for your database
5. **types** — Generate TypeScript interfaces from your schema

No Python runtime. No Docker. One `npx` command.

## Porting Decisions

Each tool started as a well-known Python project. Here's what I learned translating them to TypeScript.

### schemainspect → pg-inspect

The [original](https://github.com/djrobstep/schemainspect) is tightly coupled to SQLAlchemy. My version talks directly to PostgreSQL via `pg_catalog` queries — no ORM, plain objects out.

The surprising lesson: `information_schema` views look complete but aren't. For things like RLS policies, trigger definitions, and composite types, you need `pg_catalog` system tables. The Python version knew this; I had to rediscover it.

Result: ~2100 lines of TypeScript, 20 tests, covering tables, views, functions, indexes, sequences, enums, triggers, constraints, extensions, privileges, types, domains, collations, and RLS.

### migra → pg-diff

[migra](https://github.com/djrobstep/migra) by Robert Lechte (djrobstep) is one of those tools that looks simple until you try to rebuild it. The core challenge is dependency ordering: you can't drop a type before the column that uses it, can't create a function before the type it returns.

I added a `--safe` flag that never generates DROP statements — because nobody wants to accidentally drop a production table from a diff gone wrong.

### pg_activity → pg-top

The [original](https://github.com/dalibo/pg_activity) is a full ncurses TUI in Python. My version is simpler — snapshot mode for scripts, a live refresh mode for terminals. Uses [lipgloss-ts](https://github.com/indiekitai/lipgloss-ts) (itself a port of Go's [lipgloss](https://github.com/charmbracelet/lipgloss)) for styling.

Yes, that's a TypeScript port using a TypeScript port of a Go library to display PostgreSQL stats. We live in interesting times.

## Why Not Just Use the Python Originals?

Honest question. If you're already in a Python shop, those tools are great — use them. But if your stack is Node/TypeScript:

1. **No Python runtime needed** — your CI probably doesn't have it, and adding it just for DB tools is friction
2. **Programmatic access** — `import { doctor } from '@indiekitai/pg-toolkit'` in your existing codebase. Write health checks into your test suite, generate types in your build step
3. **Single package** — one `npm install` instead of three `pip install` + virtualenv management
4. **MCP support** — every tool works as an [MCP](https://modelcontextprotocol.io/) server, so AI coding agents can inspect and diagnose your database directly

## The MCP Part

This is where it gets interesting. All tools in pg-toolkit expose an MCP server:

```json
{
  "mcpServers": {
    "pg-toolkit": {
      "command": "npx",
      "args": ["@indiekitai/pg-toolkit", "mcp"],
      "env": { "DATABASE_URL": "postgresql://localhost/mydb" }
    }
  }
}
```

Your AI coding agent (Claude, Cursor, Windsurf, etc.) can:

- Inspect your actual schema before writing queries
- Run health checks and suggest optimizations
- Compare staging vs production
- Monitor running queries in real time

Not "AI-powered" — no LLMs inside. Just structured tools that agents happen to use well.

## Numbers

- 7 npm packages under `@indiekitai/`
- ~100 tests across the suite
- PostgreSQL 12+ compatible
- Zero native dependencies (pure TypeScript + node-postgres)

## Try It

```bash
npx @indiekitai/pg-toolkit doctor postgres://localhost/mydb
```

Takes about 3 seconds. Tells you what's wrong and how to fix it.

**GitHub:** [github.com/indiekitai/pg-toolkit](https://github.com/indiekitai/pg-toolkit)
**npm:** `npm install @indiekitai/pg-toolkit`

This is v0.2. Rough edges exist. Feedback welcome — open an issue or find me on [HN](https://news.ycombinator.com/user?id=indiekitai).

---

**Update — 2026-04-23 (late evening)**: Two months after this TypeScript suite post, only one tool survives — and its shape changed through the day. Morning: archived the 7-package suite, kept a focused [pg-health](https://github.com/indiekitai/pg-health) Python CLI. Afternoon: tried to split Web Dashboard (pg-dash) vs CLI+MCP (pg-health) — that split died within hours when I realized I only had one user (myself). Evening: consolidated everything back into [pg-dash](https://github.com/indiekitai/pg-dash) v0.11.0 as a single tool: Web Dashboard + CLI + MCP in one npm install. pg-health PyPI yanked, GitHub archived. Full retrospective of the one-day fork-and-merge: [pg-health 的一天生命周期](/blog/2026-04-23-pg-health-intro).
