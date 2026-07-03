---
title: "I Ported Python's Best PostgreSQL Tools to TypeScript"
date: 2026-07-03
description: "Python has schemainspect, migra, pg_activity. TypeScript has... not much. So I ported them: pg-toolkit is 5 PostgreSQL tools in one npx command — health checks, schema inspection, diff, activity monitor, type generation — every one of them also an MCP server."
tags: ["PostgreSQL", "TypeScript", "Open Source", "MCP", "Developer Tools"]
lang: en
featured: true
---

Python has excellent PostgreSQL tooling — schemainspect, migra, pg_activity. TypeScript has... not much. So I ported them.

## The Problem

If you're a Node/TS developer working with PostgreSQL, your options are:

- **Schema inspection?** Write raw `information_schema` queries or use Prisma's heavy ORM
- **Schema diff?** Nothing. You compare manually or switch to Python
- **Health checks?** Copy-paste SQL snippets from blog posts
- **Activity monitoring?** Open pgAdmin or SSH into the server

Python developers have had elegant solutions for years. TypeScript developers deserve the same.

## What I Built

**pg-toolkit** — a unified CLI and SDK that brings 5 PostgreSQL tools together:

1. **doctor** — 20+ health checks with scoring and auto-generated fix SQL
2. **inspect** — Full schema inspection (tables, views, functions, indexes, enums, triggers, RLS...)
3. **diff** — Compare two databases, generate migration SQL (ALTER/CREATE/DROP)
4. **top** — Real-time activity monitor (like pg_activity but in your terminal)
5. **types** — Generate TypeScript types from your database schema

One `npx` command. No Python. No Docker. No config files.

## The Interesting Part: Porting Decisions

### schemainspect → pg-inspect

- Original: 2000+ lines of Python, deeply coupled to SQLAlchemy
- My version: Pure SQL queries, returns plain objects, zero ORM dependency
- Lesson: The hardest part wasn't the SQL — it was understanding which `information_schema` views actually give you complete information (spoiler: they don't, you need `pg_catalog`)

### migra → pg-diff

- Original: beautiful Python code by Robert Lechte
- Challenge: migra's diff algorithm is surprisingly subtle — handling dependency order (can't drop a type before the column that uses it) took 3x longer than expected
- Safe mode: `--safe` flag that never generates DROP statements. Because production.

### pg_activity → pg-top

- Original: ncurses-based Python TUI
- My version: Uses lipgloss-ts (itself a port of Go's lipgloss) for styling
- Meta moment: A TypeScript port using a TypeScript port of a Go library to display PostgreSQL stats

## Why Not Just Use the Python Originals?

Fair question. If you're already in a Python environment, those tools are great. But:

1. **Your deploy pipeline is probably Node-based** — adding Python just for DB tools is friction
2. **Programmatic access** — `import { doctor } from '@indiekitai/pg-toolkit'` works in your existing codebase
3. **MCP support** — Every tool works as an MCP server, so AI agents (Claude, Cursor) can inspect and diagnose your database directly
4. **Single dependency** — One `npm install` instead of managing Python virtualenvs

## The MCP Angle

This is what I'm most excited about. Every tool in pg-toolkit exposes an MCP server. Your AI coding agent can:

- Inspect your actual database schema before writing queries
- Run health checks and suggest optimizations
- Compare staging vs production schemas
- Monitor running queries

Not "AI-powered" (no LLMs inside). Just well-structured tools that AI agents can use.

## Numbers

- 7 packages, all published on npm under `@indiekitai/`
- ~100 tests across the suite
- Works with PostgreSQL 12+
- Zero native dependencies (pure TypeScript + node-postgres)

## Try It

```bash
npx @indiekitai/pg-toolkit doctor postgres://localhost/mydb
```

GitHub: https://github.com/indiekitai/pg-toolkit · npm: https://www.npmjs.com/package/@indiekitai/pg-toolkit

---

*Feedback welcome. This is v0.2 — rough edges exist.*
