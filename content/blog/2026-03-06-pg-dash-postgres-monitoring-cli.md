---
title: "pg-dash: A Free CLI Alternative to pganalyze for PostgreSQL Monitoring"
slug: pg-dash-postgres-monitoring-cli
date: 2026-03-06
tags: [postgresql, cli, open-source, developer-tools, monitoring]
description: "pganalyze costs $149/month. pg-dash is free, runs in one npx command, and comes with 23 MCP tools for AI-assisted optimization. Here's what it does."
---

# pg-dash: A Free CLI Alternative to pganalyze for PostgreSQL Monitoring

pganalyze is excellent. It's also $149/month minimum, requires a SaaS signup, and gives you a web dashboard — which is great if you have a budget and want dashboards. If you just want to know what's wrong with your PostgreSQL database and fix it, that's a lot of overhead.

I built [pg-dash](https://github.com/indiekitai/pg-dash) as a different bet: a single CLI command that runs a full health check, works offline, integrates into CI, and exposes everything as MCP tools for AI coding agents.

```bash
npx @indiekitai/pg-dash check postgres://localhost/mydb
```

That's it. No signup. No account. No dashboard to configure.

## What It Checks

pg-dash runs 46+ automated checks across four categories:

**Performance**
- Cache hit ratio (sequential and index scan)
- Table and index bloat
- Missing indexes (queries from `pg_stat_statements` that do full scans)
- Unused indexes consuming write overhead
- Connection utilization

**Maintenance**
- Tables that need VACUUM or ANALYZE
- Dead tuple accumulation
- Autovacuum health and last-run times
- Long-running transactions holding locks

**Schema**
- Tables without primary keys
- Columns with unconstrained TEXT where a type would be appropriate
- FK relationships without supporting indexes

**Security**
- Public schema permissions
- Superuser accounts in use
- pg_hba.conf exposure

Each check comes with a severity (error/warning/info), a one-line explanation, and — for most — a specific SQL fix you can run. Not "consider adding an index." Literally `CREATE INDEX CONCURRENTLY idx_orders_user_id ON orders (user_id);`.

## The Commands

```bash
# Health check (one-shot, works in CI)
pg-dash check postgres://...

# Check a migration file before running it
pg-dash check-migration ./migrations/015_add_index.sql

# EXPLAIN ANALYZE a slow query in your terminal
pg-dash explain "SELECT * FROM orders WHERE user_id = $1" postgres://...

# Real-time lock + long-query monitor
pg-dash watch-locks postgres://...

# Compare two environments
pg-dash diff-env --source postgres://local/db --target postgres://staging/db

# Track schema changes over time
pg-dash schema-diff postgres://...
```

The `explain` command is the one I use most day-to-day. Web-based EXPLAIN visualizers (explain.dalibo.com, pgexplain.dev) are fine, but copy-pasting a query into a browser every time a slow query shows up in logs gets old. `pg-dash explain` runs directly against your DB and shows a color-coded tree in the terminal with recommendations:

```
Query: SELECT * FROM orders WHERE user_id = $1

Limit   cost=3.01..3.04 actual=0.060ms rows=10/10
└─ Sort cost=3.01..3.09 actual=0.057ms rows=10/32
  └─ Seq Scan on orders cost=0.00..2.32 actual=0.023ms rows=32/32

── Summary ──────────────────────────────────────
  Execution time:  12.340ms
  Seq Scans:       orders

── Recommendations ──────────────────────────────
  ⚠  Seq Scan on "orders" (32 rows). Consider adding an index on user_id.
```

Red = Seq Scan on large tables. Green = Index Scan. Yellow = Hash Join. The tree tells you where time is going faster than reading raw EXPLAIN output.

## CI Integration

Health checks in CI catch regressions before they hit production:

```yaml
- name: PostgreSQL health check
  run: npx @indiekitai/pg-dash check $DATABASE_URL --ci --threshold 70
```

The `--ci` flag emits GitHub Actions annotations (`::error::`, `::warning::`). The `--threshold` flag sets the score below which the step fails. Run this after migrations in your deploy pipeline and you'll catch bloat, missing indexes, and lock-prone migrations before they become incidents.

The `--diff` flag compares against a previous run and reports only what changed:

```bash
pg-dash check $DATABASE_URL --diff --format md
```

Useful for PR comments: "since last run, 2 new issues found."

## Migration Safety

Before running a migration, check it:

```bash
pg-dash check-migration ./migrations/015_add_index.sql postgres://...
```

Static analysis catches:
- `CREATE INDEX` without `CONCURRENTLY` (locks writes)
- `ADD COLUMN NOT NULL` without `DEFAULT` (table rewrite)
- `ALTER COLUMN TYPE` (rewrites entire table)
- `ADD FOREIGN KEY` without `NOT VALID`
- `RENAME COLUMN` / `RENAME TABLE` (breaks app code)

With a database connection, it goes further: estimates actual lock duration based on real row counts, validates that REFERENCES tables exist.

If you want migration safety without the rest of pg-dash, there's also [@indiekitai/pg-safe-migrate](https://github.com/indiekitai/pg-safe-migrate) — a standalone zero-dependency checker for CI.

## The MCP Part

pg-dash ships with 23 MCP tools, which means your AI coding assistant (Claude, Cursor, Windsurf) can talk directly to your database:

```json
{
  "mcpServers": {
    "pg-dash": {
      "command": "pg-dash-mcp",
      "args": ["postgres://localhost/mydb"]
    }
  }
}
```

Then in Claude Code: *"Check if there are any missing indexes"* → calls `pg_dash_check_indexes` → returns analysis → suggests `CREATE INDEX CONCURRENTLY`.

This is the part pganalyze can't do. It has great dashboards, but your AI agent can't query it. pg-dash is tool-first by design.

## Comparison

| | pganalyze | Grafana+Prometheus | pgAdmin | pg-dash |
|--|--|--|--|--|
| Price | $149+/mo | Free | Free | Free |
| Setup | SaaS signup | 3 services | Complex UI | One command |
| CI-ready | ❌ | ❌ | ❌ | ✅ |
| MCP / AI tools | ❌ | ❌ | ❌ | 23 tools |
| EXPLAIN CLI | ❌ | ❌ | ❌ | ✅ |
| Lock monitor | ❌ | ✅ | ❌ | ✅ |
| Migration check | ❌ | ❌ | ❌ | ✅ |

pganalyze has better historical query tracking and deeper AWS RDS integration. If those matter, pay for pganalyze. If you want something that works in 10 seconds without a credit card, try pg-dash.

## Try It

```bash
npx @indiekitai/pg-dash check postgres://localhost/mydb
```

**GitHub:** [github.com/indiekitai/pg-dash](https://github.com/indiekitai/pg-dash)
**npm:** `@indiekitai/pg-dash`

This is v0.5. Feedback and issues welcome.
