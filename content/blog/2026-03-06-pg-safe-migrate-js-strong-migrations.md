---
title: "I Built the JavaScript Equivalent of Ruby's strong_migrations"
slug: pg-safe-migrate-js-strong-migrations
date: 2026-03-06
tags: [postgresql, javascript, typescript, migrations, open-source, ci]
description: "Ruby has strong_migrations (4k stars, battle-tested at Instacart). JavaScript has nothing. So I built pg-safe-migrate — a CLI and library that catches unsafe PostgreSQL migrations before they reach production."
---

# I Built the JavaScript Equivalent of Ruby's strong_migrations

Ruby developers have had [strong_migrations](https://github.com/ankane/strong_migrations) for years. It hooks into ActiveRecord and blocks migrations that would cause downtime: `CREATE INDEX` without `CONCURRENTLY`, `ADD COLUMN NOT NULL` without a default, `ALTER COLUMN TYPE` that rewrites the entire table.

It has 4,000 GitHub stars and is standard practice at companies like Instacart. It works because it intercepts migrations *before* they run, not after production is on fire.

JavaScript has nothing like it. Until now.

## The Problem

Every Node.js team running PostgreSQL has done this at least once:

```sql
-- In production migration:
CREATE INDEX idx_orders_user_id ON orders (user_id);
```

This locks the `orders` table for the entire index build. On a table with 10 million rows, that's minutes. Every query hitting that table blocks. Your application times out. The on-call engineer wakes up.

The correct version:

```sql
CREATE INDEX CONCURRENTLY idx_orders_user_id ON orders (user_id);
```

The difference is one word. No linter catches it. No code review reliably catches it. You need a tool that *knows PostgreSQL semantics*.

## What pg-safe-migrate Checks

```bash
npx @indiekitai/pg-safe-migrate check ./migrations/015_add_index.sql
```

```
Checking: migrations/015_add_index.sql

  ✗ [DANGER] Create Index Without Concurrently (line 1)
    CREATE INDEX idx_orders_user_id ON orders (user_id);
    ↳ Locks the table for reads and writes during index creation.
    ↳ Fix: CREATE INDEX CONCURRENTLY idx_orders_user_id ON orders (user_id);

Summary: 1 danger, 0 warnings, 0 info — NOT SAFE
```

Exit code 1. Your CI fails. The bad migration doesn't reach production.

### The 15 Checks

**🔴 DANGER — Will cause downtime**

| Check | What happens | Safe alternative |
|-------|-------------|-----------------|
| `CREATE INDEX` without `CONCURRENTLY` | Locks table writes during build | `CREATE INDEX CONCURRENTLY` |
| `ADD COLUMN NOT NULL` without `DEFAULT` | Table rewrite in PG < 11 | Add nullable, backfill, add NOT NULL |
| `ALTER COLUMN TYPE` | Rewrites entire table | New column → backfill → rename |
| `ADD FOREIGN KEY` without `NOT VALID` | Full scan + lock | Add `NOT VALID`, then `VALIDATE CONSTRAINT` |
| `ADD UNIQUE CONSTRAINT` (not via index) | Full scan + lock | `CREATE UNIQUE INDEX CONCURRENTLY` → `USING INDEX` |
| `SET NOT NULL` on existing column | Full table scan | `CHECK CONSTRAINT NOT VALID` pattern |
| `DROP TABLE` | Destructive, irreversible | Remove app code first |
| `TRUNCATE` | ACCESS EXCLUSIVE lock | Batched DELETE |

**🟡 WARNING — Risky**

| Check | Problem |
|-------|---------|
| `RENAME COLUMN` | Breaks ORM caching |
| `RENAME TABLE` | Breaks all queries using old name |
| `DROP COLUMN` | ORM attribute caching |
| `ADD CHECK CONSTRAINT` without `NOT VALID` | Full table scan |

**🔵 INFO — Best practices**

- More than 3 `ALTER TABLE` in one migration
- `UPDATE` without `WHERE` (backfill timeout risk)
- Index on 4+ columns (diminishing returns)

## Using It

**Check a single file:**
```bash
pg-safe-migrate check ./migrations/015_add_index.sql
```

**Check all migrations in a directory:**
```bash
pg-safe-migrate check ./migrations/
```

**JSON output for scripts:**
```bash
pg-safe-migrate check migration.sql --json
```

**List all checks:**
```bash
pg-safe-migrate list-checks
```

**Exit codes:** `0` = safe, `1` = DANGER, `2` = WARNING (no dangers)

## CI Integration

```yaml
# .github/workflows/migrate.yml
- name: Check migration safety
  run: npx @indiekitai/pg-safe-migrate check ./migrations/ --json
```

This runs without a database connection. Pure static analysis. Fast, dependency-free, works in any CI environment.

## Programmatic Use

```typescript
import { checkMigration } from "@indiekitai/pg-safe-migrate";

const sql = readFileSync("./migrations/015.sql", "utf-8");
const result = checkMigration(sql);

if (!result.safe) {
  console.log(`Found ${result.summary.danger} dangerous operations`);
  for (const issue of result.issues) {
    console.log(`${issue.severity}: ${issue.message}`);
    console.log(`Fix: ${issue.suggestion}`);
  }
}
```

## MCP Server (for Claude / Cursor)

```json
{
  "mcpServers": {
    "pg-safe-migrate": {
      "command": "pg-safe-migrate-mcp"
    }
  }
}
```

Your AI agent can check migration safety before suggesting you run them:
- `check_migration(sql)` — returns issues and summary
- `list_checks()` — explains all 15 checks
- `explain_check(name)` — detailed explanation for one check

Ask Claude Code: *"Is this migration safe to run?"* → it calls `check_migration` → tells you what to fix.

## Why No Database Connection?

strong_migrations connects to your database to check table sizes and estimate lock duration. pg-safe-migrate is intentionally database-free by design.

The reason: the most dangerous time to run a migration safety check is *before* you have a staging database set up. In a fresh CI environment, against a new branch, you want feedback immediately. No connection string required.

If you want row-count-aware analysis (e.g., "this index will lock for ~4 minutes because there are 8M rows"), that's in [pg-dash check-migration](https://github.com/indiekitai/pg-dash) — same checks, plus live database analysis.

## Ruby Has strong_migrations. Now JavaScript Does Too.

```bash
npm install -g @indiekitai/pg-safe-migrate
pg-safe-migrate check ./migrations/
```

**GitHub:** [github.com/indiekitai/pg-safe-migrate](https://github.com/indiekitai/pg-safe-migrate)
**npm:** `@indiekitai/pg-safe-migrate`

If you're running Prisma, Drizzle, node-pg-migrate, or raw SQL migrations in a Node.js/TypeScript project, add this to your CI. It takes 10 seconds and will eventually save you from a 3am incident.
