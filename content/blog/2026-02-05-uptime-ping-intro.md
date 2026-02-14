---
title: "Uptime Ping：最简单的 API 监控方案"
date: 2026-02-05
description: "免费、自托管的服务监控工具。服务挂了？Telegram 立刻通知你。"
tags: ["工具", "监控", "DevOps"]
---

服务挂了，用户告诉你还是监控告诉你？

如果是用户告诉你，那就晚了。

## Uptime Ping 是什么

一个轻量级的 API 健康监控服务：

- **定时检查**你的服务是否在线
- **响应变慢**？自动标记为 degraded
- **服务挂了**？Telegram 立刻通知你
- **统计 Uptime**，知道你的服务有多稳定

## 快速开始

```bash
# 添加要监控的服务
curl -X POST https://up.indiekit.ai/config/endpoints \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-api.com/health", "name": "My API"}'

# 查看状态
curl https://up.indiekit.ai/status
```

## 告警效果

服务状态变化时，你会收到这样的消息：

```
🔴 服务宕机

🔗 https://api.example.com/health
📊 up → down
❗ Expected 200, got 503
🕐 2026-02-14T10:30:00
```

恢复时也会通知：

```
🟢 服务恢复

🔗 https://api.example.com/health
📊 down → up
⏱️ 停机时长：3分钟
```

## 为什么不用 UptimeRobot？

UptimeRobot 很好，但：

1. **免费版限制多**（50 个监控点）
2. **数据在别人服务器**
3. **不能自定义告警格式**

Uptime Ping 完全自托管，你的数据你做主。

## 特点

- ✅ 1 分钟检查间隔
- ✅ 响应时间追踪
- ✅ degraded 状态识别（慢但没挂）
- ✅ Uptime 百分比统计
- ✅ JSON 文件存储，零数据库依赖

## 自己部署

```bash
git clone https://github.com/indiekitai/uptime-ping
cd uptime-ping
cp .env.example .env
# 编辑 .env 添加 Telegram 配置
uvicorn src.main:app --port 8081
```

---

**在线体验**：[up.indiekit.ai](https://up.indiekit.ai)

**GitHub**：[indiekitai/uptime-ping](https://github.com/indiekitai/uptime-ping)
