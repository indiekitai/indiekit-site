---
title: "Doc2MD：让 AI Agent 也能读文档"
date: 2026-02-12
description: "PDF、Word、网页一键转 Markdown。专为 AI Agent 设计的文档转换工具。"
tags: ["工具", "AI", "MCP", "文档"]
---

你有没有试过让 Claude 读一个 PDF？

它会告诉你：抱歉，我看不了附件。

Doc2MD 解决的就是这个问题。

## 它做什么

把各种文档格式转换成 Markdown：

| 输入 | 输出 |
|------|------|
| PDF | Markdown |
| Word (.docx) | Markdown |
| HTML | Markdown |
| 网页 URL | Markdown |

## 为什么是 Markdown

因为 AI Agent 爱 Markdown：

- **结构清晰**：标题、列表、代码块
- **Token 效率高**：比 HTML 省 80% token
- **通用格式**：所有 AI 都能理解

## API 使用

```bash
# 转换网页
curl "https://d.indiekit.ai/convert/url?url=https://example.com"

# 转换 PDF
curl -X POST https://d.indiekit.ai/convert/pdf \
  -F "file=@document.pdf"

# 转换 Word
curl -X POST https://d.indiekit.ai/convert/docx \
  -F "file=@document.docx"
```

## Cloudflare Markdown for Agents

Doc2MD 支持 Cloudflare 的新特性：如果目标网站启用了 Markdown for Agents，会直接返回 Markdown，不需要额外转换。

这意味着更快的速度和更好的格式。

## MCP 集成

安装后可以直接在 Claude Desktop 里用：

```bash
pip install indiekit-doc2md
```

配置 `claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "doc2md": {
      "command": "doc2md-mcp"
    }
  }
}
```

然后对 Claude 说：「帮我把这个 PDF 转成 Markdown」

## 作为 Python 库

```python
from doc2md import convert_url, convert_pdf

# 转换网页
md = await convert_url("https://example.com")

# 转换 PDF
with open("doc.pdf", "rb") as f:
    md = convert_pdf(f.read())
```

## 谁需要这个

- **AI 开发者**：让 Agent 能读取各种文档
- **内容创作者**：快速把文档转成博客格式
- **研究人员**：批量处理论文 PDF

---

**在线体验**：[d.indiekit.ai](https://d.indiekit.ai)

**PyPI**：`pip install indiekit-doc2md`

**GitHub**：[indiekitai/doc2md](https://github.com/indiekitai/doc2md)
