---
title: "MCP Servers：让 Claude Desktop 直接用你的工具"
date: 2026-02-14
description: "Model Context Protocol 是什么？怎么让 AI 直接调用你的 API？IndieKit MCP 实战指南。"
tags: ["MCP", "AI", "Claude", "工具"]
---

你有没有想过：为什么 Claude 不能直接帮你发邮件、查数据库、操作文件？

因为它没有"手"。

MCP（Model Context Protocol）就是给 AI 装上"手"的协议。

## MCP 是什么

简单说，MCP 是一个标准，让 AI 能够：

1. **发现工具**：知道有哪些功能可用
2. **调用工具**：执行具体操作
3. **获取结果**：拿到操作结果

就像 USB 接口一样，有了标准，所有设备都能互联。

## IndieKit 的 MCP Servers

我们提供了几个 MCP Server：

### indiekit-mcp

让 Claude 直接使用 IndieKit 的所有工具：

```bash
pip install indiekit-mcp
```

功能：
- 创建短链接
- 保存代码片段
- 转换文档
- 查看服务状态

### indiekit-notion-mcp

让 Claude 管理你的 Notion：

```bash
pip install indiekit-notion-mcp
```

功能：
- 搜索页面
- 创建页面
- 更新内容
- 管理数据库

### indiekit-doc2md（内置 MCP）

```bash
pip install indiekit-doc2md
```

功能：
- 转换 PDF/Word/HTML 到 Markdown
- 抓取网页内容

## 配置 Claude Desktop

编辑 `claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "indiekit": {
      "command": "indiekit-mcp",
      "env": {
        "INDIEKIT_API_URL": "https://indiekit.ai"
      }
    },
    "notion": {
      "command": "notion-mcp",
      "env": {
        "NOTION_API_KEY": "your-notion-key"
      }
    },
    "doc2md": {
      "command": "doc2md-mcp"
    }
  }
}
```

重启 Claude Desktop，就能用了。

## 使用示例

对 Claude 说：

- 「帮我把这个链接转成短链：https://...」
- 「把这个 PDF 转成 Markdown」
- 「在我的 Notion 里搜索关于项目管理的页面」
- 「创建一个新的 Notion 页面，标题是...」

Claude 会自动调用对应的 MCP 工具。

## 为什么 MCP 重要

这是 AI Agent 的未来。

现在的 AI 只能"说"，有了 MCP 就能"做"。

想象一下：
- AI 帮你整理文件
- AI 帮你更新数据库
- AI 帮你发布内容
- AI 帮你监控服务

这些都需要 MCP。

## 自己写 MCP Server

想让 Claude 调用你自己的 API？参考我们的代码：

- [indiekit-mcp](https://github.com/indiekitai/indiekit-mcp)
- [notion-mcp](https://github.com/indiekitai/notion-mcp)

核心就是定义工具 schema 和实现调用逻辑，几十行代码就能搞定。

---

**了解更多**：[MCP 官方文档](https://modelcontextprotocol.io)

**GitHub**：[indiekitai](https://github.com/indiekitai)
