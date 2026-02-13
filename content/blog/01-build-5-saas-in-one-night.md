---
title: "我用 AI 一晚上做了 5 个 SaaS 工具"
date: "2026-02-13"
description: "从零开始，3 小时内用 AI 构建 5 个完整的 SaaS 工具，总计 2300+ 行代码。这是我的经验分享。"
tags: ["AI", "独立开发", "SaaS", "Claude"]
---

凌晨 2 点，我决定做个实验：能不能用 AI 在一晚上做出几个可用的 SaaS 工具？

结果：**3 小时，5 个工具，2314 行代码**。

## 做了什么

| 工具 | 功能 | 代码行数 |
|------|------|----------|
| HN Digest | AI 生成中文 Hacker News 摘要 | 724 |
| Uptime Ping | API 健康监控 + Telegram 告警 | 610 |
| Webhook Relay | Webhook 转发到 Telegram | 410 |
| Tiny Link | 短链接 + 点击统计 | 270 |
| Quick Paste | 代码分享 + 语法高亮 | 300 |

每个工具都是完整可用的：有 API、有数据持久化、有 Docker 支持。

## 技术选型

为了快，我选择了最简单的栈：

- **FastAPI**：Python Web 框架，写起来飞快
- **JSON 文件存储**：不需要数据库，简单粗暴
- **Cloudflare**：DNS + CDN + SSL 一站搞定
- **DigitalOcean**：$6/月的服务器够用了

关键决策：**不追求完美，追求能用**。

## 每个工具的思路

### 1. HN Digest

痛点：Hacker News 每天那么多帖子，英文的，看不过来。

解决：
1. 用 HN API 抓取 Top 30 故事
2. 用 Claude 生成中文摘要 + 分类 + 重要性评分
3. 每天一份，JSON 存储历史

核心代码 100 行左右，加上 API 和存储大概 700 行。

### 2. Uptime Ping

痛点：服务挂了不知道，用户告诉你才发现。

解决：
1. 定时 HTTP 检查（默认 1 分钟）
2. 状态变化时发 Telegram 通知
3. 记录响应时间，统计 uptime

用 APScheduler 做定时任务，简单有效。

### 3. Webhook Relay

痛点：GitHub、Stripe 的 webhook 想收到通知，但不想搭复杂的后端。

解决：
1. 接收任意 webhook
2. 自动识别 GitHub/Stripe 格式并美化
3. 转发到 Telegram

核心就是一个 POST 接口，但加了格式化和多 channel 支持。

### 4. Tiny Link

痛点：bit.ly 要登录，数据不在自己手里。

解决：
1. 生成随机短码或自定义
2. 记录点击数、访客 IP、User-Agent
3. 支持过期时间

最简单的一个，200 多行搞定。

### 5. Quick Paste

痛点：分享代码片段，gist 太重，pastebin 广告多。

解决：
1. 粘贴代码，生成链接
2. Pygments 语法高亮
3. 支持阅后即焚

## 部署

全部跑在一台 $6/月的 DigitalOcean Droplet 上：

```
indiekit.ai     → 主站
hn.indiekit.ai  → HN Digest (:8080)
up.indiekit.ai  → Uptime Ping (:8081)
hook.indiekit.ai → Webhook Relay (:8082)
s.indiekit.ai   → Tiny Link (:8083)
p.indiekit.ai   → Quick Paste (:8084)
```

Nginx 反向代理，systemd 管理进程，开机自启。

## 经验总结

1. **AI 写代码是真的快**。但你得知道要什么，AI 负责实现。
2. **MVP 不需要数据库**。JSON 文件在小规模下完全够用。
3. **Cloudflare 是神器**。免费 SSL、CDN、DDoS 防护。
4. **先做出来再说**。完美是 good 的敌人。

## 下一步

- 写更多内容，做 SEO
- 看看有没有人用
- 如果有人用，再考虑付费功能

---

工具都是免费的，欢迎试用：

- [HN Digest](https://hn.indiekit.ai) - AI 中文 HN 精选
- [Uptime Ping](https://up.indiekit.ai) - 服务监控
- [Webhook Relay](https://hook.indiekit.ai) - Webhook 转发
- [Tiny Link](https://s.indiekit.ai) - 短链接
- [Quick Paste](https://p.indiekit.ai) - 代码分享
