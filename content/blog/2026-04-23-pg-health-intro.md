---
title: "pg-health 的一天生命周期：为什么我又把它合并回 pg-dash"
slug: pg-health-intro
date: 2026-04-23
description: "上午发了 pg-health，下午决定合并回 pg-dash。为什么我推翻自己当天的决定。"
tags: ["PostgreSQL", "工具", "开源", "产品决策", "复盘"]
---

早上我在这里发了一篇 pg-health 的介绍文章。下午我把它合并回了 pg-dash，这篇博文被改写成了你现在看到的这版。

一天时间，我推翻了自己的决定。记录一下。

## 发生了什么

今天的时间线：

- **上午** 发布 pg-health v1.0（Python CLI + MCP），定位是"pg-dash 的 Python 交互式分身"
- **下午** 重构成 v2.0，从 pg-dash 迁移 `check-migration` / `explain` 等功能过来
- **晚上** 把 pg-health 整个合并回 pg-dash。PyPI 包 yank、GitHub repo archive、npm 的 pg-dash 发了 v0.11.0 作为合并后的单一产品

中间只隔了几个小时。

## 为什么要合并

早上我给两个工具划分工："pg-dash 做 Web Dashboard、pg-health 做 CLI + MCP"。然后发了博客讲两条战线。

下午我自己把两个名字搞混了——问 Claude "pg-health 是我一直在用的数据库工具是吗"，被纠正"你用的是 pg-dash"。

那一刻我应该立刻停下来问：**为什么要维护两个产品？**

没有。我当时选择的路径是"调整分工再划分得更清楚"，投入了 4-5 个小时做 v2.0 重构（代码迁移、发布、博客、文档）。

到了晚上盘点时才想明白——**只有我一个用户**。分工这件事在有多个用户、多个使用场景、多个团队配合的时候才有意义。我一个独立开发者自用的工具，强行拆两个：

- 两个 repo 要维护
- 两套测试要跑
- 两个 package 要发布（npm + PyPI）
- 两个 README 要同步
- 两份 CHANGELOG 要写
- 我自己都会把名字搞混

**为一个不存在的用户群做架构是纯粹的浪费。**

## 技术数据也支持合并

事后去对比两边代码：

- **pg-health 有 4597 行 Python**，但**只有约 600 行是真独有**（今天新写的 `migration_checker.py` 和 `explain.py`，而这两者本来也是从 pg-dash 的 TypeScript 版移植过来的）
- 剩下的 4000 行本质上是 pg-dash 已有功能的 Python 重写：20+ health checks、LLM advisor、Quick Fix、通知（Telegram / Slack / Webhook / Email）、SQLite 历史
- **pg-dash 一直都是总集**：React Web UI + Hono server + advisor + check + fix + MCP + alerts + query stats collector + schema tracking，14747 行 TypeScript

pg-health 的真实角色：**pg-dash 已有功能的 Python 重新实现**。没有独立的产品身份。

## 合并执行（给好奇的人）

- `pipx install pg-health` 的 v1.0.0 和 v2.0.0 被 yank
- GitHub `indiekitai/pg-health` 归档
- pg-dash 恢复到全功能一体（v0.11.0）——Web Dashboard + CLI + MCP 一个包搞定
- indiekit.ai 首页回到单一产品定位
- 更细节地：当天还额外撤回了一次错误的 "pg-dash v1.0 strip CLI/MCP" 改动，那是合并决定之前朝错误方向走的一小步

如果你因为这篇文章的上一个版本装了 pg-health，用 `npx @indiekitai/pg-dash` 替代。所有 CLI 命令和 MCP tool 都还在，只是名字前缀从 `pg_health_*` 回到 `pg_dash_*`：

```bash
pipx uninstall pg-health
npm install -g @indiekitai/pg-dash
```

`~/.claude/mcp.json` 把 `pg-health` 那段改成 pg-dash：

```jsonc
"pg-dash": {
  "command": "npx",
  "args": ["-y", "@indiekitai/pg-dash-mcp"],
  "env": { "DATABASE_URL": "..." }
}
```

## 今天学到的

1. **默认怀疑"拆分"**。只有用户数量和使用场景的复杂度真的要求分工时，才拆；否则合并永远是更便宜的选项
2. **独立开发者 ≠ 小团队**。给自己做工具 vs 给团队做工具，设计原则完全不同。我差点搞混了
3. **当天推翻当天的决定不丢人**。博客发布后几小时就推翻，比强行维护一个错误的产品线半年要便宜得多
4. **问对问题**。如果早上有人问我"你这个工具分两个是为了谁"，我根本答不出名字（只有自己）——那就不应该拆

---

**GitHub**：[indiekitai/pg-dash](https://github.com/indiekitai/pg-dash)（唯一在维护的 PG 工具）

**安装**：`npx @indiekitai/pg-dash check "postgresql://..."`

这种复盘之后还会写。独立开发者做决策的噪音很多，记下来给后面的自己看。
