---
title: "开源：多 Agent 编排纪律核心（orchestration-playbook）"
date: 2026-07-03
description: "把 53 批次、95 个 agent、7 万行代码长跑里蒸馏出的编排纪律解绑成一份 3000 字、不依赖任何工具的 playbook：证据四级制、派发契约十条、验收铁律、ORC-01~18 反模式表。抄进你的 CLAUDE.md 就能用。"
tags: ["AI编程", "多Agent", "开源", "Loop Engineering", "工程实践"]
featured: true
---

[English version](/blog/2026-07-03-orchestration-playbook-en)

我把 codex-orchestrator / claude-orchestrator / kimi-orchestrator 三个项目里共享的那套编排纪律，抽成了一个独立的、不绑定任何 harness 的仓库：

**[indiekitai/orchestration-playbook](https://github.com/indiekitai/orchestration-playbook)**

## 为什么要单独抽出来

三个 orchestrator 是给三种 harness（Codex App / Claude Code / Kimi Code）写的运行时——ledger、心跳、pack、routine 这些是各家的适配细节。但真正让多 agent 并行不翻车的，从来不是这些机制，而是背后那套纪律。此前它埋在三份加起来 130KB 的 SKILL.md 里，新读者分不清哪 20% 是命根子、哪 80% 是我的项目特有沉淀。

现在核心被压到 3000 字以内，而且**每一条背后都是真实事故**：

- **证据四级制**（direct / proxy / local / blocked，禁止升级）——因为一个 local 单测被逐步"升级"成了生产验证
- **派发契约十条**——因为"边界不清就派"的每一种结局我都见过
- **验收铁律**："worker 的已 commit 不可信"——因为 worker 报告 commit 完成、实际改动停在工作区、worktree 被删、全部重做
- **ORC-01~18 反模式表**——从"幽灵 commit"到"把动作当进展"，每条一个编号，review 时点名比写散文快

## 不装任何工具就能用

这个仓库刻意做成"可以被抄走"的形态。最小采用路径四步：把证据四级制和验收铁律抄进你的 CLAUDE.md / AGENTS.md；派任务时拿契约十条当 checklist；每合并一个特征包跑一次异模型 review；review 时用 ORC 编号点名问题。

需要完整运行时再去看三个适配层仓库——但大多数人需要的其实只是纪律本身。

## 附带一份真实案例档案

仓库里的 [CASE-STUDY](https://github.com/indiekitai/orchestration-playbook/blob/main/CASE-STUDY.zh-CN.md) 是今天刚发生的事：拆一个 18782 行的 Go 单文件，初版方案的全部机械门禁（编译 + vet + 138 测试 + 符号校验）都拦不住一颗运行时自省的暗雷，最后是异模型 review 抓住的。IMPL、16 条 review findings、拆分 commit 全部公开可核对——不是演示脚本，是真实仓库里的真实提交。完整故事在[上一篇](/blog/2026-07-03-multi-model-review-refactor)。

如果你在用任何 coding agent 干超过一个下午的活，这份 playbook 里大概率有你已经踩过、或者即将踩的坑。
