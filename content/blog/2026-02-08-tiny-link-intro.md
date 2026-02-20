---
title: "Tiny Link：自托管短链接服务"
date: 2026-02-08
description: "不想用 bit.ly？自己搭一个短链接服务，带点击统计。"
tags: ["工具", "短链接", "自托管"]
---

用过 bit.ly 吗？好用，但：

- 免费版有限制
- 链接数据在别人手里
- 自定义域名要付费

不如自己搭一个。

## Tiny Link 是什么

一个自托管的短链接服务：

- **生成短链接**：长 URL → 短 URL
- **点击统计**：谁点了、什么时候点的
- **自定义短码**：`s.indiekit.ai/github` 而不是随机字符
- **过期时间**：可选，链接到期自动失效

## 使用方式

```bash
# 创建短链接（自动生成短码）
curl -X POST https://s.indiekit.ai/api/links \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/indiekitai/tiny-link"}'

# 返回 {"code": "a1b2c3", "short_url": "https://s.indiekit.ai/a1b2c3"}

# 自定义短码
curl -X POST https://s.indiekit.ai/api/links \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/indiekitai", "code": "github"}'
```

## 统计功能

```bash
curl https://s.indiekit.ai/api/links/github/stats
```

返回：

```json
{
  "code": "github",
  "clicks": 42,
  "created_at": "2026-02-08T10:00:00Z",
  "last_clicked": "2026-02-14T15:30:00Z",
  "referrers": {
    "twitter.com": 20,
    "direct": 15,
    "google.com": 7
  }
}
```

## 为什么自托管

1. **数据隐私**：你的链接数据不会被第三方分析
2. **无限制**：想创建多少链接都行
3. **品牌域名**：用自己的域名，看起来更专业
4. **完全免费**：除了服务器成本

## 部署

```bash
git clone https://github.com/indiekitai/tiny-link
cd tiny-link
cp .env.example .env
# 编辑 .env 设置 BASE_URL
uvicorn src.main:app --port 8083
```

---

**在线体验**：[s.indiekit.ai](https://s.indiekit.ai)

**GitHub**：[indiekitai/tiny-link](https://github.com/indiekitai/tiny-link)
