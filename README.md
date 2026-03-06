[English](README.md) | [中文](README.zh-CN.md)

# IndieKit

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

独立开发者的 AI 工具包。

**Live**: https://indiekit.ai

## 📦 主要工具（npm）

| 工具 | 描述 | npm |
|------|------|-----|
| **pg-dash** | PostgreSQL 监控 + 健康检查 + EXPLAIN + 锁监控 + MCP（23 tools） | `@indiekitai/pg-dash` |
| **pg-safe-migrate** | PostgreSQL migration 安全检查（strong_migrations JS 版） | `@indiekitai/pg-safe-migrate` |

```bash
npx @indiekitai/pg-dash check postgres://localhost/mydb
npx @indiekitai/pg-safe-migrate check ./migrations/
```

## 🌐 Web 服务

| 工具 | 描述 | URL |
|------|------|-----|
| HN Digest | AI 中文 HN 每日精选 | [hn.indiekit.ai](https://hn.indiekit.ai) |
| Uptime Ping | API 健康监控 + Telegram 告警 | [up.indiekit.ai](https://up.indiekit.ai) |
| Tiny Link | 短链接 + 点击统计 | [s.indiekit.ai](https://s.indiekit.ai) |

## 🚀 本地运行

```bash
cd indiekit-site
uv sync
uv run uvicorn src.main:app --reload --port 8085
```

## License

MIT
