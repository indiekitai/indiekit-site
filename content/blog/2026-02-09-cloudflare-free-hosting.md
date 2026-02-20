---
title: "Cloudflare 零成本建站：DNS + CDN + SSL 一站搞定"
slug: cloudflare-free-hosting
date: 2026-02-09
description: "不花钱让你的网站更快更安全。手把手配置 Cloudflare 免费功能：DNS、CDN、SSL、DDoS 防护。"
tags: ["Cloudflare", "部署", "教程", "免费"]
---


Cloudflare 免费计划能给你什么？

- ✅ DNS 托管
- ✅ 全球 CDN
- ✅ 免费 SSL 证书（自动续期）
- ✅ DDoS 防护
- ✅ 基础防火墙
- ✅ 简单的页面规则

这些对独立开发者来说**够用了**。

## 第一步：迁移 DNS 到 Cloudflare

### 1. 注册账号

去 [cloudflare.com](https://cloudflare.com) 注册，免费的。

### 2. 添加网站

点 "Add a Site"，输入你的域名（比如 `example.com`）。

选择 **Free 计划**，继续。

### 3. 更新 DNS 服务器

Cloudflare 会给你两个 nameserver，类似：

```
ada.ns.cloudflare.com
bob.ns.cloudflare.com
```

去你的域名注册商（比如 Namecheap、GoDaddy、Cloudflare Registrar），把 nameserver 改成这两个。

⚠️ **DNS 传播需要时间**：通常几分钟到 48 小时。实际上大多数情况下 5-30 分钟就好了。

### 4. 配置 DNS 记录

迁移完成后，添加你需要的记录：

```
类型    名称    内容              代理状态
A       @       你的服务器IP        ☁️ 已代理
A       www     你的服务器IP        ☁️ 已代理
A       api     你的服务器IP        ☁️ 已代理
```

**☁️ 橙色云朵 = 流量走 Cloudflare（有 CDN + 保护）**
**☁️ 灰色云朵 = DNS Only（直连服务器）**

一般都开橙色，除非有特殊需求（比如邮件服务器）。

## 第二步：配置 SSL

### 1. 选择加密模式

进入 **SSL/TLS** → **Overview**。

选择 **Full (strict)**：

```
浏览器 ←→ Cloudflare ←→ 你的服务器
        (加密)          (加密)
```

这是最安全的模式，但需要你的服务器也有 SSL 证书。

### 2. 服务器端证书

两个选择：

**选项 A：用 Cloudflare Origin Certificate**

在 **SSL/TLS** → **Origin Server** 生成证书，有效期最长 15 年。

```bash
# 在服务器上保存证书
sudo mkdir -p /etc/cloudflare
sudo nano /etc/cloudflare/cert.pem   # 粘贴证书
sudo nano /etc/cloudflare/key.pem    # 粘贴私钥
```

Nginx 配置：

```nginx
server {
    listen 443 ssl;
    server_name example.com;
    
    ssl_certificate /etc/cloudflare/cert.pem;
    ssl_certificate_key /etc/cloudflare/key.pem;
    
    # ...
}
```

**选项 B：用 Let's Encrypt**

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d example.com -d www.example.com
```

自动续期，免费。

### 3. 强制 HTTPS

在 **SSL/TLS** → **Edge Certificates** 开启：

- ✅ **Always Use HTTPS**：自动重定向 HTTP → HTTPS
- ✅ **Automatic HTTPS Rewrites**：修复页面内的 http:// 链接

## 第三步：优化性能

### 1. 开启缓存

**Caching** → **Configuration**：

- Caching Level: **Standard**
- Browser Cache TTL: **4 hours**（或更长）

### 2. 压缩

**Speed** → **Optimization**：

- ✅ Auto Minify（JS、CSS、HTML）
- ✅ Brotli 压缩

### 3. 自定义缓存规则

对于静态资源，设置更长的缓存时间：

**Rules** → **Page Rules**（免费 3 条）：

```
URL: *example.com/static/*
设置: Cache Level → Cache Everything
      Edge Cache TTL → 1 month
```

## 第四步：安全防护

### 1. 防火墙规则

**Security** → **WAF** → **Custom rules**：

免费计划有 5 条规则。常用的：

```
# 屏蔽恶意 Bot
(cf.client.bot) → Block

# 只允许特定国家访问后台
(http.request.uri.path contains "/admin" and not ip.geoip.country in {"CN" "US"}) → Block
```

### 2. Rate Limiting

限制请求频率防止滥用：

```
# 登录接口限流
URL: *example.com/api/login*
阈值: 10 requests/minute
动作: Block for 1 hour
```

免费计划有基础限流功能。

### 3. Bot 防护

**Security** → **Bots**：

开启 **Bot Fight Mode**（免费）。自动识别和阻止恶意机器人。

## 实用技巧

### 1. 开发时绕过 CDN

调试时不想等缓存？两个方法：

```bash
# 方法 1：清除缓存
Cloudflare → Caching → Configuration → Purge Everything

# 方法 2：开发模式（临时禁用缓存）
Cloudflare → Caching → Configuration → Development Mode
```

### 2. 查看真实 IP

流量经过 Cloudflare 后，服务器看到的是 Cloudflare 的 IP。

获取真实用户 IP：

```python
# FastAPI 示例
from fastapi import Request

@app.get("/")
def index(request: Request):
    real_ip = request.headers.get("CF-Connecting-IP")
    return {"ip": real_ip}
```

Nginx 配置：

```nginx
# 从 Cloudflare header 获取真实 IP
set_real_ip_from 103.21.244.0/22;
set_real_ip_from 103.22.200.0/22;
# ... 更多 Cloudflare IP 段
real_ip_header CF-Connecting-IP;
```

### 3. 子域名通配符

Pro 计划才有 `*.example.com` 证书。

免费计划的解决方案：手动添加每个子域名的 DNS 记录。

```
A    hn      服务器IP    ☁️ 已代理
A    api     服务器IP    ☁️ 已代理
A    blog    服务器IP    ☁️ 已代理
```

### 4. 重定向

用 Page Rules 做重定向：

```
URL: www.example.com/*
设置: Forwarding URL (301)
目标: https://example.com/$1
```

## 成本对比

| 需求 | 自己搞 | 用 Cloudflare |
|------|--------|---------------|
| SSL 证书 | Let's Encrypt（免费但要配置） | 自动（免费） |
| CDN | $20+/月 | 免费 |
| DDoS 防护 | 昂贵 | 免费 |
| DNS | $5/月 | 免费 |

## IndieKit 的配置

```
域名: indiekit.ai (Cloudflare Registrar)
SSL: Full (strict) + Origin Certificate
CDN: 已启用，全球 CDN
缓存: 静态资源 1 周
安全: Bot Fight Mode + 基础防火墙规则
```

月费用：**$0**

---

*Cloudflare 免费计划对独立开发者绝对够用。先用起来，等有钱了再考虑升级。*
