# FeedCraft：用 AI 增强你的 RSS 订阅

> RSS 阅读的痛点：全英文看不过来、只有摘要没全文、信息太杂。FeedCraft 用 AI 解决这些问题，而且开源可自部署。

## 痛点场景

订阅了一堆英文 RSS，但：

1. **全英文** — 快速浏览困难，得一篇篇点进去
2. **只有摘要** — 很多源只给前两段，想看全文得跳转
3. **信息过载** — 混着软文和水文，筛选成本高

传统方案要么人肉处理，要么写一堆脚本。

## FeedCraft 的解法

[FeedCraft](https://github.com/Colin-XKL/FeedCraft) 是个 RSS 中间件，在你和 RSS 源之间加一层处理：

```
原始 RSS → FeedCraft → 增强后的 RSS → 你的阅读器
```

核心能力：

| 功能 | 说明 |
|------|------|
| 全文提取 | 自动抓取文章全文，不用跳转 |
| AI 翻译 | 标题/内容翻译，支持沉浸式双语 |
| AI 摘要 | 自动生成中文摘要 |
| AI 筛选 | 用自然语言定义过滤规则 |
| 去广告 | AI 清理文章中的营销内容 |

## 快速体验

不需要部署，直接用官方 demo：

```
# 翻译标题
https://feed-craft.colinx.one/craft/translate-title?input_url=你的RSS地址

# 提取全文
https://feed-craft.colinx.one/craft/fulltext?input_url=你的RSS地址

# 生成摘要
https://feed-craft.colinx.one/craft/summary?input_url=你的RSS地址
```

把处理后的地址添加到你的 RSS 阅读器就行。

## 架构设计

FeedCraft 有三个核心概念：

### 1. AtomCraft（原子工艺）

单个处理操作，内置的有：

- `proxy` — 直接代理，不处理
- `limit` — 限制文章数量
- `fulltext` — 提取全文（Readability 算法）
- `fulltext-plus` — 浏览器渲染后提取（处理 JS 页面）
- `translate-title` — 翻译标题
- `translate-content` — 翻译内容
- `translate-content-immersive` — 沉浸式翻译（原文+译文）
- `summary` — AI 生成摘要
- `ignore-advertorial` — 过滤软文

### 2. FlowCraft（组合工艺）

多个 AtomCraft 串联：

```
fulltext → ignore-advertorial → summary → translate-title
```

一条龙处理：提取全文 → 过滤软文 → 生成摘要 → 翻译标题

### 3. Recipe（配方）

给特定 RSS 源指定处理方式，生成新的订阅地址：

```
Recipe: "my-hn-digest"
  源: https://hnrss.org/frontpage
  处理: summary + translate-title
  输出: https://your-feedcraft/recipe/my-hn-digest
```

## 自部署

Docker Compose 一键部署：

```yaml
version: "3"
services:
  feedcraft:
    image: ghcr.io/colin-xkl/feed-craft
    ports:
      - "10088:80"
    volumes:
      - ./feed-craft-db:/usr/local/feed-craft/db
    environment:
      FC_PUPPETEER_HTTP_ENDPOINT: http://browserless:3000
      FC_REDIS_URI: redis://redis:6379/
      FC_LLM_API_BASE: https://api.openai.com/v1  # 或其他兼容接口
      FC_LLM_API_KEY: sk-xxx
      FC_LLM_API_MODEL: gpt-3.5-turbo
      FC_DEFAULT_TARGET_LANG: zh-CN

  redis:
    image: redis:6-alpine

  browserless:
    image: browserless/chrome
    environment:
      USE_CHROME_STABLE: true
```

需要三个组件：
- **FeedCraft** 本体
- **Redis** 缓存
- **Browserless** 浏览器渲染（处理 JS 页面）

## 技术实现

看了下源码，核心依赖：

| 库 | 用途 |
|----|------|
| `gofeed` | RSS 解析 |
| `go-readability` | 全文提取（Mozilla Readability 的 Go 实现） |
| `langchaingo` | LLM 调用（支持 OpenAI 兼容接口） |
| `goquery` | HTML 解析 |
| `html-to-markdown` | HTML 转 Markdown |

全文提取用的是 Readability 算法，和浏览器的"阅读模式"原理相同。

## 适用场景

✅ **适合**：
- 订阅英文技术博客，需要快速浏览
- RSS 源只给摘要，想看全文
- 信息源太杂，需要 AI 帮忙筛选
- 想给团队共享处理后的 RSS

❌ **不适合**：
- 对实时性要求极高（中间处理有延迟）
- 源本身质量很高不需要处理
- 不想付 LLM API 费用

## 类似项目

| 项目 | 特点 |
|------|------|
| [RSSHub](https://github.com/DIYgod/RSSHub) | RSS 生成，不做内容处理 |
| [Full-Text RSS](https://github.com/fivefilters/full-text-rss) | 只做全文提取 |
| [FeedCraft](https://github.com/Colin-XKL/FeedCraft) | 全文 + AI 翻译/摘要/筛选 |

FeedCraft 的优势是把 AI 能力集成进来了，而且架构设计（AtomCraft/FlowCraft/Recipe）很灵活。

## 总结

FeedCraft 解决了 RSS 阅读的几个核心痛点：

1. **全文提取** — 不用跳转看完整内容
2. **AI 翻译** — 英文源也能快速浏览
3. **AI 摘要** — 30 秒判断值不值得细看
4. **AI 筛选** — 自动过滤水文软文

开源 + 可自部署 + 支持任意 OpenAI 兼容 LLM，值得一试。

**链接**：
- GitHub: https://github.com/Colin-XKL/FeedCraft
- Demo: https://feed-craft.colinx.one
- 文档: https://feed-craft-doc.vercel.app/zh
