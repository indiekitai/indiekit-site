---
title: "HN Digest：用 AI 帮你读 Hacker News"
date: 2026-02-06
description: "每天花 5 分钟了解科技圈最新动态。AI 自动抓取、翻译、总结 Hacker News 热门文章。"
tags: ["工具", "AI", "Hacker News"]
---

作为开发者，你可能每天都会刷 Hacker News。但说实话，大部分文章标题看不懂要点，点进去又是长篇英文。

HN Digest 就是为解决这个问题而生的。

## 它做什么

1. **自动抓取** HN Top/Best/Show 的热门故事
2. **AI 生成中文摘要**，一句话告诉你这篇文章讲什么
3. **智能分类**（编程、创业、科技新闻...）
4. **重要性评分**，优先看最值得看的

## 使用方式

直接访问 [hn.indiekit.ai](https://hn.indiekit.ai) 就能看到今日摘要。

也可以用 API：

```bash
# 获取今日摘要
curl https://hn.indiekit.ai/digest

# Markdown 格式（适合笔记软件）
curl https://hn.indiekit.ai/digest/markdown
```

## 示例输出

```
📰 Show HN: 我用 Rust 重写了 Git

一位开发者花了 6 个月用 Rust 重写了 Git 的核心功能。
性能提升 3 倍，内存占用减少 50%。
项目已开源，支持所有主流 Git 操作。

🏷️ 编程 | ⭐ 重要性 5/5 | 💬 234 评论
```

## 为什么做这个

我自己每天早上都会花 15-20 分钟刷 HN，但效率很低。很多文章点进去发现不是我关心的领域。

有了 AI 摘要后，5 分钟就能过完当天的重点，需要深入了解的再点进去看。

## 技术栈

- Python + FastAPI
- Claude API 生成摘要
- JSON 文件存储（够用了）
- 每日自动运行

## 开源

代码在 [GitHub](https://github.com/indiekitai/hn-digest)，欢迎 Star 和贡献。

---

**试试看**：[hn.indiekit.ai](https://hn.indiekit.ai)
