---
title: "小项目用什么数据库？JSON vs SQLite vs Postgres 实战对比"
slug: database-choices
date: 2026-02-06
description: "不是所有项目都需要 Postgres。这篇帮你根据实际需求选择合适的数据存储方案。"
tags: ["数据库", "架构", "独立开发", "技术选型"]
---

# 小项目用什么数据库？JSON vs SQLite vs Postgres 实战对比

"用什么数据库"是最常见的技术选型问题之一。

我的答案是：**取决于规模和需求**。不是所有项目都需要 Postgres。

## 三个选项

### 1. JSON 文件

最简单的方案。数据直接存成 JSON 文件。

```python
import json
from pathlib import Path

DATA_FILE = Path("data.json")

def load():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return []

def save(data):
    DATA_FILE.write_text(json.dumps(data, indent=2))
```

**优点**：
- 零依赖，零配置
- 人类可读，方便调试
- 部署简单（就是个文件）
- 备份就是复制文件

**缺点**：
- 并发写入有风险
- 数据量大了性能差
- 没有查询语言

**适合**：
- MVP / 原型
- 数据量 < 10,000 条
- 单实例部署
- 配置存储

**IndieKit 的选择**：5 个工具全用 JSON 存储。因为数据量小，单机部署，够用了。

### 2. SQLite

嵌入式关系数据库。一个文件，SQL 支持。

```python
import sqlite3

conn = sqlite3.connect("data.db")
conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT UNIQUE
    )
""")
```

**优点**：
- 依然是单文件，部署简单
- 完整 SQL 支持
- 性能不错（读 >> 写场景）
- Python 标准库自带

**缺点**：
- 写入有锁（高并发写场景不行）
- 备份稍麻烦（要处理事务）

**适合**：
- 数据量 10,000 - 1,000,000
- 读多写少
- 需要复杂查询
- 单机部署

**进化路径**：很多项目从 SQLite 起步，等需要了再迁移到 Postgres。迁移成本不高因为都是 SQL。

### 3. PostgreSQL

完整的关系数据库服务器。

```python
import psycopg2

conn = psycopg2.connect("postgresql://user:pass@localhost/db")
cur = conn.cursor()
cur.execute("SELECT * FROM users WHERE email = %s", (email,))
```

**优点**：
- 久经考验，功能完整
- 高并发读写
- 复杂查询、事务、索引
- 扩展丰富（全文搜索、JSON、GIS）

**缺点**：
- 需要单独的服务器进程
- 配置和运维成本
- 小项目 overkill

**适合**：
- 数据量 > 1,000,000
- 高并发写入
- 多实例部署
- 需要复杂功能（全文搜索等）

## 决策树

```
你的数据量？
├── < 10,000 条 → JSON 文件
├── 10,000 - 1,000,000 条
│   ├── 读多写少 → SQLite
│   └── 写也很多 → Postgres
└── > 1,000,000 条 → Postgres
```

## 实战建议

### 1. 从简单开始

大多数新项目，JSON 够了。等遇到瓶颈再换。

过早优化是万恶之源。我见过太多项目第一天就上 K8s + 分库分表，然后半年后还是 100 个用户。

### 2. JSON 的并发问题解决方案

如果担心并发写入：

```python
import fcntl

def save_atomic(data):
    with open(DATA_FILE, 'w') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        json.dump(data, f)
        fcntl.flock(f, fcntl.LOCK_UN)
```

或者用 `write-then-rename` 模式确保原子性：

```python
import tempfile
import os

def save_atomic(data):
    fd, tmp = tempfile.mkstemp(dir=DATA_FILE.parent)
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(data, f)
        os.rename(tmp, DATA_FILE)
    except:
        os.unlink(tmp)
        raise
```

### 3. SQLite 生产可用吗？

**可以**。很多知名服务用 SQLite：

- Pieter Levels 的多个产品
- Litestream 的实时复制方案
- Rails 8 默认推荐 SQLite

关键是理解限制：单机、读多写少。

### 4. 迁移策略

从 JSON → SQLite：

```python
# 一次性脚本
import json, sqlite3

data = json.load(open("data.json"))
conn = sqlite3.connect("data.db")

for item in data:
    conn.execute(
        "INSERT INTO items (id, name) VALUES (?, ?)",
        (item["id"], item["name"])
    )
conn.commit()
```

从 SQLite → Postgres：

```bash
# 用 pgloader（自动转换）
pgloader data.db postgresql://user:pass@host/db
```

## 特殊场景

### 需要全文搜索？

- JSON：自己实现（简单场景用 `in` 判断）
- SQLite：FTS5 扩展
- Postgres：内置 `tsvector` 或 pg_trgm

### 需要多实例？

- JSON：不行
- SQLite：Litestream 复制到 S3
- Postgres：原生支持主从复制

### 需要实时同步？

考虑 Firebase / Supabase（Postgres）/ PlanetScale（MySQL）这类托管服务。

## 我的选择

| 项目 | 数据存储 | 原因 |
|------|----------|------|
| IndieKit 工具 | JSON | 数据量小，单机 |
| 个人博客 | Markdown 文件 | 就是内容 |
| SaaS MVP | SQLite | 快速验证 |
| 正式产品 | Postgres | 长期可扩展 |

## 总结

**别想太多**。

- 几千条数据 → JSON
- 几十万条 → SQLite
- 更大或复杂需求 → Postgres

先上线，再优化。

---

*有问题欢迎讨论。*
