---
title: "Webhook Relay：把所有通知集中到 Telegram"
date: 2026-02-07
description: "GitHub push、Stripe 付款、自定义事件...一个 URL 搞定所有 webhook，转发到 Telegram。"
tags: ["工具", "Webhook", "Telegram"]
---

你的服务有多少个 webhook 需要接收？

GitHub、Stripe、Vercel、Sentry...每个都要单独处理，烦不烦？

## Webhook Relay 做什么

一句话：**接收任何 webhook，转发到 Telegram**。

不管是 GitHub 的 push 事件、Stripe 的支付通知，还是你自己服务的告警，都可以用同一个方式处理。

## 使用方式

```bash
# 创建一个 channel
curl -X POST https://hook.indiekit.ai/channels \
  -H "Content-Type: application/json" \
  -d '{"name": "GitHub Repo"}'

# 返回 {"id": "abc123", "url": "/hook/abc123"}
```

然后把 `https://hook.indiekit.ai/hook/abc123` 填到 GitHub Webhook 设置里就行了。

## 智能格式化

Webhook Relay 会自动识别常见的 webhook 格式，美化后发送：

**GitHub Push:**
```
[My Repo] 🔨 Push to main
By: octocat
Commits: 3
  • Fix login bug
  • Add dark mode
  • Update README
```

**Stripe 付款:**
```
[Payments] 💳 payment_intent.succeeded
Amount: $99.00 USD
Customer: john@example.com
```

## 为什么要这个

1. **集中管理**：所有通知一个地方看
2. **手机友好**：Telegram 随时能看
3. **可追溯**：所有 webhook 都有日志
4. **零代码**：不用写任何处理逻辑

## 自己部署

```bash
git clone https://github.com/indiekitai/webhook-relay
cd webhook-relay
cp .env.example .env
# 编辑 .env 添加 Telegram 配置
uvicorn src.main:app --port 8082
```

---

**在线体验**：[hook.indiekit.ai](https://hook.indiekit.ai)

**GitHub**：[indiekitai/webhook-relay](https://github.com/indiekitai/webhook-relay)
