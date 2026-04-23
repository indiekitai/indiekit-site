---
title: "pg-health：从 7 个包回到 1 个工具"
slug: pg-health-intro
date: 2026-04-23
description: "PostgreSQL 健康检查：LLM Advisor 给修复 SQL、Quick Fix 一键执行、MCP 让 AI agent 直接看 DB 状态。自部署，连接字符串不离开你的机器。"
tags: ["PostgreSQL", "工具", "开源", "MCP", "AI Agent"]
---

两个月前我[写过一篇](/blog/porting-python-pg-tools-to-typescript)——把 Python 生态的 schemainspect、migra、pg_activity 移植到 TypeScript，做成了 7 个 npm 包的 pg-toolkit。

然后我把那批 repo 全 archived 了。

今天说的是从灰烬里长出来的一个工具：**pg-health**。

## 反思那次失败

pg-toolkit 的问题不在代码，在**产品定位**。我当时想的是"TypeScript 开发者没有这些工具，我来做"。做完才发现：

- **90% 的人连 psql 都不常用**，何况一整套 CLI
- **10% 真有问题的人**，最痛的不是缺 schema diff 或活动监控，而是"发现问题后不知道怎么修"——**建议 + 修复**才是钩子
- **7 个 npm 包** = 7 个各自 0 star，合起来还不如一个有故事的

砍到一个工具，只做一件事：**体检 + 开药方 + 你确认后吃药**。

## 先说清楚：pg-health ≠ 取代 pg-dash

[pg-dash](https://github.com/indiekitai/pg-dash) 没在这次清理里。它活得好好的，因为和 pg-health 的定位**完全不同**：

- **pg-dash**（TypeScript）跑在 CI / pre-deploy，在问题进生产前拦截。`npx @indiekitai/pg-dash check-migration` 是典型场景——PR 里加了个迁移，pipeline 里跑一下，不安全就红。
- **pg-health**（Python）坐在 psql 旁边，人在环里诊断 + 修复。凌晨三点 P1 告警，你 SSH 上去 `pg-health check`，看到 bloat，`pg-health fix` 带 dry-run 让你看 SQL，apply。

我自己 Cutie 项目这两个月一直在用 pg-dash 做 CI 守门员，这篇文章不是取代它，是介绍它的**补位**。两个工具都带 MCP Server，所以你的 AI agent 可以同时看到 CI 状态和实时健康——一个产品线，两条战线。

## pg-health 是什么

一条命令扫完你的 PG，列出所有问题，每个问题给具体的修复 SQL：

```bash
pipx install pg-health
pg-health check "postgresql://user:pass@host/db"
```

输出大概长这样（完整 demo 在 [pg.indiekit.ai](https://pg.indiekit.ai)）：

```
❌ CRITICAL  Table Bloat
   public.orders: 28.4% bloat (~15 GB wasted).
   💡 VACUUM FULL public.orders during maintenance window,
      or use pg_repack for zero-downtime rewrite.

⚠️  WARNING   FK Missing Indexes
   2 FKs without indexes: events.user_id, sessions.user_id.
   💡 CREATE INDEX CONCURRENTLY ON events(user_id);
      CREATE INDEX CONCURRENTLY ON sessions(user_id);

✅ OK        Connection Usage
   47 / 200 (23.5%).
```

20+ 种检查，每个 warning 和 critical 都带修复 SQL。这是和常规 health checker 的第一个区别。

## 三个真正的差异化

### 1. LLM Advisor：不止报告，还给药方

传统工具（pgbadger、pg_top、你自己写的那堆 check）只会说"bloat 超阈值了"。pg-health 说"bloat 超阈值了，这是具体哪张表、wasted 多少 GB、用哪条 SQL 修"。

这部分是 **pganalyze 的付费功能**（Index Advisor、Tuning Advice，起步 $149/月）。我做了个开源版。

### 2. Quick Fix：从建议到执行

```bash
# 预览要执行的 SQL
pg-health fix unused-indexes --dry-run

# 预览没问题，执行
pg-health fix unused-indexes
```

可以修的问题：未使用索引（DROP INDEX）、高 bloat 表（VACUUM/REINDEX）、过期的 autovacuum 统计、重复索引。每次都先 dry-run 把 SQL 甩给你看，你 ack 了才跑。

### 3. MCP Server：让 AI agent 直接看 DB

这部分是和上次 pg-toolkit 唯一接得上的地方。pg-health 带一个 MCP server，Claude Desktop / Cursor / 任何 MCP client 都能接：

```bash
pipx install "pg-health[mcp]"
pg-health-mcp
```

配置到 Claude Desktop：

```json
{
  "mcpServers": {
    "pg-health": {
      "command": "pg-health-mcp",
      "env": { "DATABASE_URL": "postgresql://..." }
    }
  }
}
```

然后你对 Claude 说 "orders 表最近慢了，帮我看看"——它会自己调 pg-health 的工具扫 DB、查索引、看 bloat，给你定位问题 + 对应 SQL。不是空谈"AI 助手"，是结构化工具 + agent 自然用。

## Self-hosted：连接字符串不离开你的机器

[pg.indiekit.ai](https://pg.indiekit.ai) 本身不接受你填连接字符串——那页是给你看 demo 报告和下载 CLI 的 landing page。

真正的检查跑在你本地的 `pg-health` CLI 里。你的连接字符串从来不会经过我的服务器。

这点是和 pganalyze、Datadog DBM 的核心区别——后者都是 SaaS，你的 DB 元数据要发过去。pg-health 是你自己跑。

## 对标表

| | pganalyze | Datadog DBM | pg-health |
|---|---|---|---|
| 价格 | $149+/月 | $70+/host/月 | 免费 |
| 托管 | SaaS | SaaS | 自部署 |
| 建议 + 修复 SQL | ✅ | 部分 | ✅ |
| 一键执行修复 | ❌ | ❌ | ✅ |
| MCP server | ❌ | ❌ | ✅ |
| 数据离开你机器 | ✅ | ✅ | ❌ |
| 历史趋势 | ✅ | ✅ | ✅（SQLite 本地） |

不是说 pg-health 要取代 pganalyze——那家公司的产品做得非常好，企业买有它的道理。但**个人开发者、小团队、开源项目**，没必要为这个付 $149/月。

## 通知和历史

```bash
pg-health check "$DATABASE_URL" \
  --notify telegram --notify slack \
  --history ~/.pg-health/history.db
```

SQLite 本地存历史，`pg-health trend cache_hit_ratio --days 30` 能看任何指标的走势。跑成 cron 每天一次就是轻量的 DB 监控。

## 为什么现在拿出来

代码 2 月底就基本写完了，躺在服务器上自用了两个月。上周盘点的时候发现一个事——之前 [pg.indiekit.ai](https://pg.indiekit.ai) 的版本让访问者填连接字符串在**服务端**跑检查，意味着我的服务器能被当跳板扫别人的内网 PG。修掉以后顺便想明白：**工具成熟 ≠ 发出去**。写完不发，等于没做。

所以这篇博客。

## 链接

- **GitHub**：[indiekitai/pg-health](https://github.com/indiekitai/pg-health)
- **在线 demo**：[pg.indiekit.ai](https://pg.indiekit.ai)
- **安装**：`pipx install pg-health`（v2.0 起 MCP 默认装上，不用再 `[mcp]` extra）

欢迎在 GitHub 提 issue。第一次写类似规模的工具，肯定有粗糙的地方——真实反馈最有价值。

---

**Update — 2026-04-23 晚**：上面写的"pg-dash 跑 CI / pg-health 在 psql 旁"的分工，在发布几小时后就被修订了。更准确的切分是**有无 Web UI**——pg-dash 是 Web Dashboard，pg-health 是 CLI + MCP。`check-migration` 和 `explain` 已经从 pg-dash 迁到 pg-health v2.0，pg-dash 未来（v1.0）会剥离所有 CLI/MCP 功能变成纯面板产品。`pipx install pg-health` 默认带 MCP server，老的 `pg_dash_*` tool 名字保留 3 个月兼容期。
