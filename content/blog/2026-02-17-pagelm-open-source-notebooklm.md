---
title: "PageLM：NotebookLM 的开源替代，把 PDF 变成测验和播客"
date: 2026-02-17
description: "Google NotebookLM 很火，但有开源替代吗？PageLM 让你自己部署一个 AI 学习助手，支持多种大模型后端。"
tags: ["AI", "学习工具", "开源", "NotebookLM"]
---

Google 的 NotebookLM 火了一阵子——上传文档，AI 帮你总结、生成播客、回答问题。但它有几个问题：

- 数据要传到 Google
- 只能用 Gemini
- 功能受限于官方更新节奏

如果你想要一个**自己能控制的版本**，PageLM 是目前最成熟的开源替代。

## PageLM 是什么

[PageLM](https://github.com/CaviraOSS/PageLM) 是一个开源的 AI 学习平台，核心功能：

1. **上传文档**（PDF、Word、Markdown、TXT）
2. **AI 自动生成**：
   - 📝 结构化笔记（Cornell 笔记法）
   - 🎴 Flashcards（用于间隔重复记忆）
   - ❓ 测验题（带提示和解释）
   - 🎙️ AI 播客（把内容转成音频对话）

简单说：丢一堆资料进去，它帮你变成各种学习材料。

## 支持多种 AI 后端

这是比 NotebookLM 更灵活的地方：

| 后端 | 说明 |
|------|------|
| Google Gemini | 默认选项，免费额度够用 |
| OpenAI GPT | GPT-4/4o |
| Anthropic Claude | Claude 3.5 |
| xAI Grok | |
| Ollama | **本地运行**，数据不出门 |
| OpenRouter | 多模型聚合 |

如果你对数据隐私有要求，用 Ollama 本地跑是最安全的。

## 额外功能

除了核心的文档转学习材料，PageLM 还有：

- **语音转写**：录音转文字，整理成笔记
- **作业规划器**：AI 帮你安排学习计划
- **考试模拟**：模拟真实考试环境
- **AI 辩论**：和 AI 练习辩论技巧
- **学习伴侣**：个性化 AI 助手

功能有点多，但核心还是文档 → 学习材料这条线。

## 怎么部署

PageLM 是 Node.js + React 项目，本地跑：

```bash
git clone https://github.com/CaviraOSS/PageLM.git
cd PageLM
npm install
npm run dev
```

需要配置 AI API key（Gemini/OpenAI/Claude 选一个）。

如果想用 Ollama 本地模型，先装好 Ollama，然后在设置里选 Ollama 后端。

## 适合谁用

- **学生**：期末复习、考试准备
- **自学者**：把技术文档变成 Flashcards
- **内容创作者**：快速把资料变成播客脚本
- **隐私敏感用户**：用 Ollama 本地跑，数据不上传

## 和 NotebookLM 对比

| | NotebookLM | PageLM |
|---|---|---|
| 开源 | ❌ | ✅ |
| 自部署 | ❌ | ✅ |
| 多模型支持 | ❌ 只有 Gemini | ✅ 6+ 后端 |
| 本地运行 | ❌ | ✅ Ollama |
| 测验生成 | ❌ | ✅ |
| Flashcards | ❌ | ✅ |
| 播客生成 | ✅ | ✅ |

PageLM 功能更多，但 NotebookLM 的播客质量目前还是更好（Google 的 TTS 确实强）。

## 总结

如果你：
- 想自己控制数据
- 想用 Claude/GPT 而不是 Gemini
- 需要测验和 Flashcards 功能

PageLM 值得一试。1.4k stars，社区活跃，更新频繁。

🔗 **GitHub**: https://github.com/CaviraOSS/PageLM
