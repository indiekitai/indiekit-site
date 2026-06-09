---
title: "从提示 Agent 到设计循环：codex-orchestrator 的由来"
date: 2026-06-09
description: "我在一个真实 POS 重写项目里，如何把 Codex 从单个写代码助手，逐步改造成可巡检、可验收、能持续推进路线图的多会话工程循环。"
tags: ["AI编程", "Codex", "Loop Engineering", "Agent", "开源"]
featured: true
---

最近刷到 Addy Osmani 写的 [Loop Engineering](https://x.com/addyosmani/status/2064127981161959567)，第一反应是：这几乎就是我最近一段时间在真实项目里摸出来的东西。

不是“让 AI 帮我写一段代码”。

而是：当 AI 已经能写很多代码之后，工程师真正需要设计的是一个循环。这个循环会拆任务、开隔离环境、定时巡检、发现卡住、验收分支、合并干净结果，然后继续推进路线图。

我把这套流程整理成了一个 Codex skill，叫 [codex-orchestrator](https://github.com/indiekitai/codex-orchestrator)。

它不是一个很酷的玩具。它来自一个很普通但很真实的问题：一个大型项目重写到中后段以后，单个 AI coding session 开始不够用了。

## 单个 Agent 为什么不够

一开始用 AI 写代码很自然：你给一个明确需求，它读代码、改代码、跑测试、提交结果。

这在小任务里很好用。

但项目一大，问题马上变成另一种：

- 一个功能横跨多个模块，单 session 上下文越来越长。
- 两个任务同时做，很容易抢同一个目录或同一个协议文件。
- 某个 session 卡住了，但你不一定及时看到。
- AI 说“完成了”，但可能只是 local proof，不是 device proof，更不是 production proof。
- 路线图里还有很多任务，但你每次都要手动想“下一步派什么”。
- 任务完成后，真正花时间的是 review、merge、push、cleanup 和文档同步。

换句话说，瓶颈不再是“AI 会不会写代码”。

瓶颈变成了“这些 AI 写出来的东西，能不能被工程化地组织、验证和吸收”。

## 我真正需要的不是更多代码，而是更好的循环

后来我开始把自己从“反复提示 Agent 的人”，往“设计 Agent 工作循环的人”移动。

这个循环大概是这样：

1. 从路线图里选一个足够清晰、边界明确的任务。
2. 为它创建独立 worktree 和独立 branch。
3. 启动一个新的 Codex session，只让它做这个任务。
4. prompt 里明确禁止它再开子 Agent，避免二级失控。
5. 要求它提交代码，但不要 merge、push、cleanup。
6. 统领 session 定时巡检所有 active sessions 和 worktrees。
7. 任务完成后，统领 session 从 reviewer 角度验收 diff、文档、证据和测试。
8. 通过后才 merge 到 main、push、删除 worktree 和本地分支。
9. 如果 slot 空出来，就继续按路线图补派下一个安全任务。

这就是 codex-orchestrator 的核心。

它不是让 AI 自由发挥，而是把 AI 放进一个可控的工程循环里。

## Worktree 是这套方法的地基

并行做任务时，最容易出问题的是共享工作区。

一个 Agent 改协议，另一个 Agent 改 UI；一个还没提交，另一个已经开始基于旧 main 工作；最后你得到的不是并行开发，而是一堆互相污染的 diff。

所以 codex-orchestrator 默认要求：每个 delegated task 都有自己的 worktree、branch 和 session。

这带来几个好处：

- 每个任务的 diff 都能单独 review。
- 失败任务可以保留 worktree，不污染 main。
- 完成任务可以 merge 后清理，不留下长期垃圾分支。
- 同时跑两个任务时，可以明确判断写集是否冲突。

这听起来像很普通的 Git 纪律，但 AI coding 场景里它变得更重要。因为 AI 很快，快到如果没有隔离，它也会很快制造混乱。

## Heartbeat 解决的是“无人看管时怎么办”

另一个关键是 heartbeat。

人不可能一直盯着所有 session。尤其是晚上、吃饭、通勤，或者只是想让它自己推进一些不需要人工操作的任务。

所以我给统领 session 加了定时巡检规则：

- 读当前 repo 状态。
- 读 `git worktree list`。
- 动态发现 active / pending / completed task。
- 如果 session 完成并提交，就进入验收流程。
- 如果 worktree setup 失败，就报告 blocker。
- 如果任务还在跑且没有实质变化，就保持安静。
- 如果全部清空且 main 干净，就按路线图派下一批。

这里有一个实践教训：heartbeat prompt 不能写死历史 task ID。

任务可能几分钟就完成，但定时器如果还在反复盯着旧 ID，后面就会越来越乱。更好的方式是动态发现：从 thread、worktree、branch、commit、repo 文档里判断当前真实状态。

## 验收比生成代码更重要

codex-orchestrator 里，我最看重的不是“派发任务”，而是“验收任务”。

一个 delegated session 最后必须交付：

- branch / commit
- worktree path
- changed files
- gates run
- artifacts path
- self-review
- residual risks
- evidence label

统领 session 不直接相信这些描述，而是再读一遍 diff。

我会检查：

- 是否越界改了 forbidden paths。
- 是否同步了 `PROGRESS.md`、roadmap 和 review docs。
- 是否把 proxy/local evidence 写成了 direct proof。
- 是否有测试或运行证据支撑。
- 是否有残留 dirty work。
- 是否需要 merge/rebase main。

这一步非常重要。

因为 AI 最容易犯的不是“不会写代码”，而是“把弱证据说成强证据”。例如 local test passed 不等于真机通过，SENT 不等于 ACKED，proxy proof 不等于 direct proof。

所以我后来固定了 `direct / proxy / blocked` 三类证据口径。

如果证据不够，就写 blocked。blocked 不是失败，它是诚实的工程状态。

## 人还在循环里，而且位置更关键

这套流程不是“让 AI 自动开发，我不用管了”。

恰恰相反，它要求人做更高价值的事情：

- 定义边界。
- 判断任务能不能并行。
- 识别哪些东西必须人工验收。
- 决定产品策略。
- 审查证据是否可信。
- 在关键时刻介入硬件、支付、部署、生产环境。

比如打印机、支付终端、真实设备这些场景，AI 不能自己拔 USB、打开打印机盖子、确认 PAX 设备上的退款。它需要在正确的 checkpoint 用中文语音通知我，然后等我完成动作。

这不是“全自动”，而是“可监督的自动化”。

我觉得这也是 Loop Engineering 最容易被误解的地方：它不是取消工程师，而是把工程师从低层提示迁移到循环设计、风险控制和最终验收上。

## 为什么我要把它开源

codex-orchestrator 不是一个复杂框架。它本质上是一份 skill / runbook。

但它记录了一套我在真实工程里反复打磨出来的工作方式：

- 如何把大任务拆成可委派任务。
- 如何限制 Agent 不要越界。
- 如何用 worktree 隔离并行开发。
- 如何用 heartbeat 处理长时间无人值守。
- 如何让 Agent 自审，但不把自审当最终结论。
- 如何由统领 session 做 reviewer、merger 和 cleanup owner。
- 如何防止“浅切片”太多，真正推动一个功能闭环。

这些东西单独看都不神奇。

但组合起来以后，Codex 从“一个写代码助手”变成了一个可以持续推进路线图的工程循环。

这也是我开源它的原因：我相信未来很多 AI coding 的差距，不会只来自模型强弱，而会来自你能不能设计出稳定、可审计、可恢复的工作循环。

项目地址：

[https://github.com/indiekitai/codex-orchestrator](https://github.com/indiekitai/codex-orchestrator)

如果你也在用 Codex App 做大型项目，或者正在从“让 AI 写代码”走向“让 AI 持续推进工程”，这套方法应该会有用。

最后一句话，也是我现在对 AI coding 最真实的感受：

不要只提示 Agent。设计循环，然后继续当那个负责工程判断的人。
