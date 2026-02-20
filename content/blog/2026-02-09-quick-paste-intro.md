---
title: "Quick Paste：代码分享就该这么简单"
date: 2026-02-09
description: "自托管的 Pastebin，支持语法高亮和阅后即焚。"
tags: ["工具", "代码分享", "Pastebin"]
---

想分享一段代码，你会怎么做？

- 截图？不能复制
- 直接发文字？没有高亮，难看
- GitHub Gist？太重了

Quick Paste 就是为这个场景设计的。

## 功能

- **语法高亮**：500+ 语言支持（Pygments）
- **阅后即焚**：看一次就删除
- **自动过期**：设置过期时间
- **Raw 模式**：直接获取原始文本

## 使用方式

```bash
# 创建代码片段
curl -X POST https://p.indiekit.ai/api/paste \
  -H "Content-Type: application/json" \
  -d '{
    "content": "def hello():\n    print(\"Hello World\")",
    "language": "python"
  }'

# 返回 {"id": "abc123", "url": "https://p.indiekit.ai/abc123"}
```

## 阅后即焚

分享敏感信息（密码、API Key）时特别有用：

```bash
curl -X POST https://p.indiekit.ai/api/paste \
  -H "Content-Type: application/json" \
  -d '{
    "content": "SECRET_KEY=abc123",
    "burn_after_read": true
  }'
```

对方打开链接看一次后，内容自动删除。

## 命令行集成

加到你的 shell 配置里：

```bash
# ~/.bashrc 或 ~/.zshrc
paste() {
  curl -s -X POST https://p.indiekit.ai/api/paste \
    -H "Content-Type: application/json" \
    -d "{\"content\": $(cat | jq -Rs .), \"language\": \"${1:-text}\"}" \
    | jq -r .url
}

# 使用
cat script.py | paste python
# 输出: https://p.indiekit.ai/abc123
```

## 为什么不用 pastebin.com

1. **广告太多**
2. **免费版限制**
3. **数据在别人手里**
4. **不能自定义域名**

## 部署

```bash
git clone https://github.com/indiekitai/quick-paste
cd quick-paste
uvicorn src.main:app --port 8084
```

---

**在线体验**：[p.indiekit.ai](https://p.indiekit.ai)

**GitHub**：[indiekitai/quick-paste](https://github.com/indiekitai/quick-paste)
