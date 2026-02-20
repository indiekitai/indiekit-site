---
title: "MCP: Give Claude Desktop Superpowers"
date: 2026-02-13
description: "What is Model Context Protocol? How to let AI agents call your APIs directly. A practical guide with IndieKit MCP servers."
tags: ["MCP", "AI", "Claude", "English"]
lang: en
---

Ever wished Claude could actually *do* things instead of just talking about them?

That's what MCP (Model Context Protocol) enables.

## What is MCP?

MCP is a standard that lets AI:

1. **Discover tools** - Know what actions are available
2. **Call tools** - Execute real operations
3. **Get results** - Receive operation outcomes

Think of it like USB for AI - a universal interface.

## IndieKit MCP Servers

We've built several MCP servers you can use:

### indiekit-mcp

Access all IndieKit tools from Claude:

```bash
pip install indiekit-mcp
```

Tools included:
- Create short links
- Save code snippets
- Convert documents
- Check service status

### indiekit-notion-mcp

Let Claude manage your Notion workspace:

```bash
pip install indiekit-notion-mcp
```

Tools included:
- Search pages
- Create pages
- Update content
- Query databases

### indiekit-doc2md

Convert documents to Markdown:

```bash
pip install indiekit-doc2md
```

Tools included:
- Convert PDF to Markdown
- Convert Word to Markdown
- Fetch web pages as Markdown

## Setup

Edit your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "indiekit": {
      "command": "indiekit-mcp"
    },
    "notion": {
      "command": "notion-mcp",
      "env": {
        "NOTION_API_KEY": "your-key"
      }
    },
    "doc2md": {
      "command": "doc2md-mcp"
    }
  }
}
```

Restart Claude Desktop. Done.

## Usage Examples

Just ask Claude:

- "Shorten this link: https://..."
- "Convert this PDF to Markdown"
- "Search my Notion for project notes"
- "Create a new Notion page titled..."

Claude automatically calls the right MCP tool.

## Why MCP Matters

This is the future of AI agents.

Current AI can only talk. With MCP, it can act:
- Organize your files
- Update databases
- Publish content
- Monitor services

## Build Your Own

Want Claude to call your API? Check our code:

- [indiekit-mcp](https://github.com/indiekitai/indiekit-mcp)
- [notion-mcp](https://github.com/indiekitai/notion-mcp)

It's just tool schemas + call handlers. A few dozen lines.

---

**Learn more**: [MCP Documentation](https://modelcontextprotocol.io)

**GitHub**: [indiekitai](https://github.com/indiekitai)
