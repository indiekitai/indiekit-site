---
title: "PostgreSQL CTE + JSON_AGG: 一条 SQL 干掉 N+1，延迟降 97%"
slug: postgresql-json-agg-kills-n-plus-1
date: 2026-02-26
description: "EAV 模式下 N+1 查询让 API 延迟飙到 1 秒+？用 CTE + JSON_AGG 一条 SQL 搞定，延迟从 1200ms 降到 35ms。"
tags: ["PostgreSQL", "性能优化", "N+1", "SQL", "后端"]
---

## 问题：EAV 模式下的 N+1 噩梦

如果你用过 EAV（Entity-Attribute-Value）模式存储动态字段，你一定经历过这种痛苦：

```
获取 100 条记录 → 1 次查询
每条记录获取属性 → 100 次查询
总计：101 次查询 → 1200ms+
```

典型场景：一个表单系统，`submissions` 表存提交记录，`field_values` 表存每个字段的值。要展示一个列表页，你得先查提交列表，再逐条查每条提交的所有字段值。

ORM 通常会"贴心地"帮你做这件事 —— 一条一条查。结果就是：**数据越多，越慢**。100 条记录还能忍，1000 条直接超时。

## 解法：CTE + JSON_AGG，一条 SQL 搞定

核心思路：用 CTE 先聚合子表数据为 JSON，再 JOIN 回主表。**一次往返，全部拿到。**

```sql
-- 1. CTE: 把每个 submission 的所有 field_values 聚合成 JSON 数组
WITH field_data AS (
  SELECT
    fv.submission_id,
    JSON_AGG(
      JSON_BUILD_OBJECT(
        'field_id',    fv.field_id,
        'field_name',  f.name,
        'value',       fv.value
      )
      ORDER BY f.sort_order  -- 按字段顺序排列
    ) AS fields
  FROM field_values fv
  JOIN fields f ON f.id = fv.field_id
  GROUP BY fv.submission_id
)
-- 2. 主查询：JOIN 聚合结果
SELECT
  s.id,
  s.created_at,
  s.status,
  COALESCE(fd.fields, '[]'::json) AS fields  -- 没有字段值时返回空数组
FROM submissions s
LEFT JOIN field_data fd ON fd.submission_id = s.id
WHERE s.form_id = $1
ORDER BY s.created_at DESC
LIMIT 100;
```

**一条 SQL，返回的每一行都带着完整的字段数据。** 应用层直接 `JSON.parse(row.fields)` 就能用。

## 性能对比

| 方案 | 查询次数 | 100 条耗时 | 1000 条耗时 |
|------|---------|-----------|------------|
| N+1 逐条查询 | N+1 | ~1200ms | ~12s（超时） |
| 预加载 (Eager Load) | 2 | ~80ms | ~400ms |
| **CTE + JSON_AGG** | **1** | **~35ms** | **~120ms** |

关键优势：
- **网络往返从 N+1 降到 1** —— 这才是延迟的大头
- **数据库可以充分优化** —— 一条查询比 100 条小查询更容易走索引
- **应用层代码更简洁** —— 不需要手动拼装数据

## 什么时候该用

**适合的场景：**
- EAV 模式（动态字段、表单系统、CMS）
- 一对多关系的列表页展示
- 需要把子表数据嵌套返回给前端的 API
- 数据量大，对延迟敏感

**不适合的场景：**
- 子表数据量巨大（单条记录有上千个子项）—— JSON 会很大，考虑分页
- 需要对子表数据做复杂过滤/排序 —— 在 CTE 里加条件会增加复杂度
- 简单的一对一关系 —— 直接 JOIN 就行，不需要 JSON_AGG

## 进阶：JSONB_AGG + 索引

如果你用 `JSONB_AGG` 代替 `JSON_AGG`，返回的是 JSONB 类型，可以在 PostgreSQL 侧直接用 `@>`、`?` 等操作符做查询。配合 GIN 索引，甚至可以对聚合结果做高效过滤。

```sql
-- 用 JSONB_AGG 获取更强的查询能力
JSONB_AGG(
  JSONB_BUILD_OBJECT('field_id', fv.field_id, 'value', fv.value)
) AS fields
```

## 致谢

这个技巧来自 [Forma](https://github.com/Lychee-Technology/forma) 项目 —— 一个开源的表单构建器。它在处理动态表单字段时大量使用了 CTE + JSON_AGG 模式，把 N+1 问题彻底消灭。如果你在做类似的表单/CMS 系统，推荐看看它的 SQL 层实现。

---

**一条 SQL 能解决的事，别让 ORM 帮你查 101 次。**
