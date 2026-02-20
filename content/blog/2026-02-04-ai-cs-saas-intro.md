---
title: "AI CS SaaS：给你的产品加个 AI 客服"
date: 2026-02-04
description: "多租户 AI 客服系统，基于 RAG 检索。上传文档，AI 就能回答用户问题。"
tags: ["AI", "客服", "RAG", "SaaS"]
---

做产品最烦的事之一：回答重复的用户问题。

「怎么注册？」「怎么付款？」「xxx 功能在哪？」

每天都有人问，每次都要回答。

## AI CS SaaS 做什么

一个 AI 客服系统：

1. **上传你的文档**（FAQ、帮助文档、产品说明）
2. **AI 学习这些内容**（RAG 向量检索）
3. **用户提问时自动回答**

就这么简单。

## 核心功能

### 多租户

一个系统可以服务多个产品：

- 租户 A：电商平台的客服
- 租户 B：SaaS 产品的客服
- 租户 C：游戏的客服

每个租户的知识库完全隔离。

### RAG 检索

不是让 AI 瞎编，而是基于你的文档回答：

1. 用户提问
2. 从知识库检索相关内容
3. AI 基于检索结果生成回答

这样回答既准确又可控。

### 对话历史

支持多轮对话，AI 会记住上下文：

```
用户：怎么退款？
AI：您可以在订单页面点击"申请退款"...

用户：要多久到账？
AI：根据您的支付方式，一般 3-5 个工作日...
```

## API 使用

```bash
# 创建租户
curl -X POST https://cs.indiekit.ai/api/tenants \
  -H "Content-Type: application/json" \
  -d '{"name": "My Product", "api_key": "your-key"}'

# 上传文档
curl -X POST https://cs.indiekit.ai/api/documents \
  -H "Authorization: Bearer your-key" \
  -F "file=@faq.md"

# 提问
curl -X POST https://cs.indiekit.ai/api/chat \
  -H "Authorization: Bearer your-key" \
  -H "Content-Type: application/json" \
  -d '{"message": "怎么注册账号？"}'
```

## 技术栈

- **FastAPI**：API 框架
- **PostgreSQL + pgvector**：向量存储
- **Gemini Embedding**：文本向量化
- **Claude/GPT**：生成回答

## 适合谁

- **独立开发者**：产品用户多了，客服忙不过来
- **小团队**：想要 AI 客服但不想从零搭建
- **企业**：多产品线需要统一的客服系统

## 定价

目前免费使用，后续可能推出付费版本增加更多功能。

---

**API 文档**：[cs.indiekit.ai/docs](https://cs.indiekit.ai/docs)

**GitHub**：[indiekitai](https://github.com/indiekitai)（即将开源）
