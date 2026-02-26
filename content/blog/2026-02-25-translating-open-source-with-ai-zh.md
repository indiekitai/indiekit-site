---
title: "从 Python/Rust/Go 翻译到 TypeScript：AI Agent 的甜蜜点"
date: 2026-02-25
description: "一天之内用 AI 把 6 个开源库从 Python、Rust、Go 翻译成 TypeScript，228 个测试全部通过。"
tags: ["AI", "coding", "TypeScript", "开源"]
lang: zh
---

最近看到宝玉老师写的关于 AI coding agent "甜蜜点"的文章，深有感触。我们实践下来发现，**把现有的开源库从一种语言翻译到另一种语言**，可能是目前 AI 编程最完美的应用场景。

## 为什么是"翻译"？

让 AI 从零写一个项目，难点在于：需求模糊、架构主观、需要发明创造。但翻译完全不同：

- **源代码就是需求文档**——每个函数、每个边界情况都已经定义好了
- **需求已验证**——一个 Python 库有几千个 star，TypeScript 版本肯定有人用
- **测试已就绪**——原项目的测试套件就是"正确答案"
- **范围明确**——库是自包含的，纯逻辑，没有部署、没有 UI

这恰好是 AI 擅长的：机械复杂但概念清晰的工作。

## 一天，六个项目

| 项目 | 源语言 | 原项目 | 测试数 |
|------|--------|--------|--------|
| [pg-inspect](https://github.com/indiekitai/pg-inspect) | Python | schemainspect | 42 |
| [throttled](https://github.com/indiekitai/throttled) | Python | throttled-py | 35 |
| [just-ts](https://github.com/indiekitai/just-ts) | Rust | casey/just | 61 |
| [pg-diff](https://github.com/indiekitai/pg-diff) | Python | migra | 28 |
| [lipgloss-ts](https://github.com/indiekitai/lipgloss-ts) | Go | charmbracelet/lipgloss | 37 |
| [pg-top](https://github.com/indiekitai/pg-top) | Python | pg_activity | 25 |
| **合计** | | | **228 ✅** |

## 流程

做了六次之后，总结出标准流程：

1. **扫描**——让 AI 阅读整个源项目，理解架构和模块结构
2. **规划**——生成翻译规格：模块映射、语言习惯转换（`__init__.py` → `index.ts`，`impl` → class 等）
3. **翻译**——从叶子依赖开始，逐模块翻译。AI 首轮能搞定 ~90%
4. **测试**——翻译测试套件，运行，修 bug。这一步是真正的调试，但方向明确
5. **打磨**——加类型、配置 tsconfig、写 README、发布

中等复杂度的库，2-4 小时搞定。简单的不到一小时。

## 经验

**测试是一切。** 有完善测试套件的项目，翻译成功率极高；没测试的，全靠猜。

**Python → TypeScript 最顺滑。** 两种语言结构相似，翻译最自然。Rust → TS 需要更多创造力（所有权、模式匹配没有直接对应）。Go → TS 居中。

**AI 翻译比创作强。** 从零开始要做几百个设计决策，翻译时大部分决策已经做好了。AI 只需换一种语法表达同样的逻辑。

**不要逐行翻译，要地道。** Python 的列表推导应该变成 `.map().filter()`，Rust 的 `match` 应该用 TypeScript 的 switch 或对象查找。正确引导 AI，它能写出地道的目标语言代码。

## 思考

与其问"AI 能从零做什么"，不如问"有哪些现有的好东西，AI 可以帮我翻译、适配、移植？"这个思路打开之后，可做的事情非常多。

所有项目开源在 [GitHub](https://github.com/indiekitai)，欢迎贡献。
