---
title: "从提示 Agent 到设计循环：codex-orchestrator 的由来"
date: 2026-06-09
description: "Loop Engineering 实战：我如何把 Codex / Claude Code 从单个写代码助手，组织成 worktree 隔离、heartbeat 巡检、可验收合并的多 Agent 工程循环。"
tags: ["AI编程", "Codex", "Claude Code", "Loop Engineering", "AI Agent Orchestration", "开源"]
featured: true
---

最近刷到 Addy Osmani 写的 [Loop Engineering](https://x.com/addyosmani/status/2064127981161959567)，第一反应是：这几乎就是我最近一段时间在真实项目里摸出来的东西。

不是“让 AI 帮我写一段代码”。

而是：当 AI 已经能写很多代码之后，工程师真正需要设计的是一个循环。这个循环会拆任务、开隔离环境、定时巡检、发现卡住、验收分支、合并干净结果，然后继续推进路线图。

我把这套流程整理成了一个 Codex skill，叫 [codex-orchestrator](https://github.com/indiekitai/codex-orchestrator)。

它不是一个很酷的玩具。它来自一个很普通但很真实的问题：一个大型项目重写到中后段以后，单个 AI coding session 开始不够用了。

## 2026-06-11 更新：它已经不只是一个 skill 文档了

这篇文章发出后，我又连续用 codex-orchestrator 跑了几轮真实项目和自身迭代。现在这个项目比最初的描述更进一步：它仍然是 Codex App-first 的 skill，但已经多了一层 Go helper CLI，用来保存和恢复循环状态。

新增的核心不是“更自动地写代码”，而是让循环更可观察、更可审查：

- `.codex-orchestrator/ledger.json` 记录 delegated task 的状态、worktree、branch、pending setup id、预算和验收历史。
- `codex-orchestrator observe --json` 可以把当前队列归类成 pending setup、active、dirty、completed-unreviewed、blocked、cleanup-needed、cleaned。
- `run-routine pr-reviewer` 会基于 ledger 和 git truth 做本地静态验收清单，包括 allowed / forbidden paths、review docs、证据标签和 `git diff --check`。
- `run-routine docs-drift-checker` 会检查 runnable routine、JSON spec 和关键文档是否同步，并增加了 post-merge docs drift guard。
- `run-routine evidence-label-auditor` 会扫描 docs / review / handoff，防止把 local/static/proxy 证据写成 direct/pre/prod/device/payment proof。
- `policy check` 和本地 fixture eval 开始把“不要在主 checkout fallback、不要用旧 heartbeat task id、不要把弱证据升级成强证据”这些经验固化成可跑的规则。
- `roadmap-next-task-suggester` 会根据 roadmap、routine specs 和 ledger 状态，判断还有没有安全的下一项。

所以它现在更像一个很轻量的 App-first orchestration layer：Codex App 负责真正创建 worktree session 和执行任务；helper 负责持久 ledger、repo truth 观察、routine 检查、policy/eval 和 heartbeat 报告。

我刻意没有把它做成 Homebrew / npm 那种先装工具再学习命令的路线。更自然的入口还是：把 GitHub 地址发给 Codex App，让 Codex 自己阅读仓库、安装 skill、解释 helper 的用途，然后先做 dry run。

这也让我对 Loop Engineering 的理解更清楚了一点：Loop 的难点不是“循环执行提示词”，而是每一轮都能回答这几个问题：

- 现在真实状态是什么？
- 哪个 worker 已经可验收？
- 哪些证据只是 local/static，不能写成 direct？
- 合并后文档有没有漂移？
- 如果队列空了，是继续派发，还是应该停下来等人定义下一阶段？

这些问题比“让 Agent 多写几行代码”重要得多。

## 2026-06-11 晚上更新：v0.3.1，把 GitHub 首屏和真实案例补齐

今天又把仓库往“别人第一次看到就能理解”的方向收了一轮，发布到
`v0.3.1`。

这次不是继续堆 helper 功能，而是补上三个更重要的产品化点：

- README 首屏重新组织：一句话讲清楚它是 **Codex App-first Loop Engineering for real repositories**。
- 明确边界：它不是 daemon，不是 Homebrew/npm 优先的安装工具，不是 Agent OS，也不是不经 review 就自动合并代码的 bot。
- 新增一篇 TastyFuture 脱敏案例文章，解释这套循环在真实 POS 项目里怎么处理 task contract、worktree 隔离、heartbeat 对账、completed-unreviewed、review/merge/cleanup 和 evidence label。

我越来越觉得，codex-orchestrator 真正要卖的不是“多开几个 Agent”，而是把 AI coding 产生的工作变成可审查、可拒绝、可恢复、可继续推进的工程交付单元。

这也解释了为什么我没有把入口设计成“先安装 CLI”。更自然的体验应该是：

> 在你的项目里打开 Codex App，把 GitHub 地址交给它，让 Codex 自己读取仓库、安装 skill、解释 helper 是否有用，然后先做 dry run。

如果用户一上来就需要学一堆命令，这个东西就已经偏离了 Codex App-first 的初衷。

这次更新后，仓库里的 Quick Start、中文 README、案例文章和 release notes 基本对齐了：先让人看懂循环，再谈 helper 能提供哪些本地 ledger、status、routine 和 policy/eval 辅助。


## 如果你在搜 Loop Engineering / Codex / Claude Code

这篇文章讲的不是某一个模型的 prompt 技巧，而是面向 Codex、Claude Code 这类 AI coding agent 的工程编排方式。

我自己把它理解成几个关键词：Loop Engineering、Codex orchestration、Claude Code orchestration、multi-agent coding workflow、worktree isolation、heartbeat monitor、review and merge loop。

如果你现在的问题是“怎么让 Codex 或 Claude Code 不只是写一段代码，而是持续推进一个大型模块”，codex-orchestrator 解决的就是这个层面的问题。

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


## FAQ：它和 Claude Code 有什么关系？

**codex-orchestrator 只适用于 Codex 吗？**

这个仓库本身是为 OpenAI Codex App 写的 skill，所以实现细节偏 Codex：Codex session、Codex heartbeat、Codex worktree task。

但背后的方法论不是 Codex 专属。Claude Code、Cursor Agent、其他 coding agent 也会遇到同样的问题：并行任务如何隔离、长时间任务如何巡检、完成后如何验收、弱证据如何标注、失败分支如何清理。

**为什么文章里同时提 Codex 和 Claude Code？**

因为我真正想表达的是 Loop Engineering：围绕 AI coding agent 设计工程循环。Codex 是我这套实现的主要载体，Claude Code 是同一类问题的另一个常见使用场景。

**它是不是 multi-agent framework？**

不是传统意义上的框架。它更像一个可执行的工程 runbook：告诉统领 session 怎么派发、怎么巡检、怎么 review、怎么 merge，以及什么时候必须停下来等人。

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
