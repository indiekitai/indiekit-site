---
title: "AI 编程不缺模型，缺的是外层控制系统"
date: 2026-06-14
description: "我为什么写 codex-orchestrator：从一次真实项目编排开始，把 Codex App 变成可巡检、可验收、可恢复的工程循环。"
tags: ["AI编程", "Codex", "Loop Engineering", "AI Agent", "工程实践", "开源"]
featured: true
---

最近几周，我越来越强烈地感觉到：AI 编程的瓶颈已经不只是模型能力。

模型当然还有差距。不同模型在推理、代码风格、上下文稳定性上都不一样。但对很多真实工程任务来说，今天的模型已经“够能干”了。真正难的是另一件事：

> 当 AI 已经能连续写代码、改代码、跑测试以后，我们怎么管理它产生的工作？

这就是我写 [codex-orchestrator](https://github.com/indiekitai/codex-orchestrator) 的原因。

它不是又一个“更会写代码”的工具。它更像是 Codex App 外面的一层工程控制系统：负责拆任务、隔离 worktree、记录状态、定时巡检、发现卡住、验收分支、合并干净结果、清理现场，然后继续推进路线图。

## 起点：不是想做产品，只是想让 Codex 多干点活

最开始的问题很朴素。

我在做一个比较大的项目重写，模块很多：前台、后台、移动端、后端服务、报表、支付、打印、同步、权限。单个 Codex session 可以完成一个小任务，但当项目变大以后，问题开始变成：

- 一个 session 上下文越来越长，后面容易记混。
- 两个任务同时做，可能改到同一个协议、同一个数据库模型、同一个 UI 入口。
- 某个 worker 卡住了，我不一定及时看到。
- AI 说“完成了”，但有时只是本地测试过了，不是真机、不是真环境、更不是生产证据。
- 任务做完后，真正麻烦的是 review、merge、push、cleanup 和文档同步。

所以我一开始做的不是写工具，而是写规则。

每个任务单独开 worktree。worker 只负责提交自己的 branch。它不能 merge、不能 push、不能清理 worktree。统领 session 负责巡检、验收、合并、推送和清理。

这个流程跑起来以后，我很快发现：规则写在聊天里不够。

聊天会压缩，任务 ID 会过期，heartbeat 会漏跑，worker 状态和 git 状态会不一致。于是 codex-orchestrator 从一个 skill 文档，慢慢长出了一层 Go helper CLI。

## 关键转变：不要把 Agent 当成神奇员工，要当成可验收的交付单元

很多人说“多 Agent 协作”，听起来像多招几个 AI 员工。

我后来觉得这个比喻不太对。

更准确的理解是：每个 worker branch 都应该是一个可验收、可拒绝、可清理的交付单元。

也就是说，worker 完成后，不是看它说了什么，而是看这些东西：

- 它在哪个 worktree？
- 它在哪个 branch？
- 它从哪个 base commit 开始？
- 它改了哪些文件？
- 它有没有碰 forbidden paths？
- 它跑了哪些 gate？
- 它有没有写 self-review？
- 它的证据是 direct、proxy、local，还是 blocked？
- 它是否留下 dirty worktree？

这套检查比“让 AI 再聪明一点”更实际。

因为在真实项目里，AI 最危险的地方往往不是不会写代码，而是把证据说过头。比如：

- local test passed 被写成 runtime proof。
- static check 被写成 direct proof。
- proxy evidence 被写成 pre/prod evidence。
- “页面能打开”被写成“业务闭环完成”。

codex-orchestrator 里一直强调 evidence label，就是为了挡住这种过度乐观。

## 为什么需要 ledger

最开始我以为，让统领 session 记住当前任务就够了。

后来发现不够。

一个长跑的编排流程里，状态会散在很多地方：

- 当前聊天上下文。
- Codex App 的 thread 状态。
- worktree 是否真的创建成功。
- branch 是否正确。
- worker 有没有 clean commit。
- main 有没有 ahead origin。
- review 文档有没有写。
- task 是否已经 merge/push/cleanup。

这些东西只靠聊天记忆，很快会乱。

所以 helper 里有了 `.codex-orchestrator/ledger.json`。它不是为了替代 Codex App，而是为了给 Codex App 的外层循环一个本地状态账本。

一个任务从 pending setup，到 active，到 completed-unreviewed，到 accepted、merged、pushed、cleaned，应该有迹可循。

这解决的不是“AI 怎么写代码”，而是“明天早上醒来，我怎么知道昨晚到底发生了什么”。

## Heartbeat 也不是魔法

我曾经以为，有 heartbeat 就能无人值守。

后来被现实教育了。

Codex App 的 heartbeat 可以定时唤醒 thread，但它不等于操作系统级 daemon。电脑睡眠、App 没调度、automation 没投递，都可能导致中间有空档。

所以现在我更保守地描述它：

- heartbeat 是 Codex App 层面的定时唤醒。
- helper 的 heartbeat report 是本地静态记录。
- watchdog 只能作为本机辅助监控。
- 如果机器没醒、App 没唤醒，helper 事后才能发现 gap，不能提前证明不会漏。

这听起来不酷，但更真实。

工程系统不是靠一句“全自动”变可靠的。可靠性来自承认边界，然后给边界加观测、日志、告警和恢复策略。

## 状态页为什么重要

另一个很深的教训是：没有状态页，人就像盲人。

编排系统一直在跑，但你不知道它现在是在：

- 等 worker 写代码；
- 等 worktree setup；
- 等 review；
- 已经 merge 但没 push；
- cleanup 有残留；
- 当前 feature package 已经收口；
- 还是只是有 available slots，但不应该继续派发。

早期我只看命令输出和聊天总结，后来发现这对长期使用不够。

于是加了 `status.md` 和 `status.html`。它们不是漂亮 dashboard，而是让人快速判断：

- 当前主线是什么；
- 当前 worker 是谁；
- 现在能不能验收；
- 有没有需要人操作；
- 当前是 active、drain 还是 paused；
- 最近有没有 missed heartbeat；
- 下一步是继续、等待、验收，还是停止派发。

状态页的目标不是炫技，而是降低“我不知道它在干什么”的焦虑。

## 最大的坑：为了填满并发槽而乱派任务

codex-orchestrator 最早有一个很诱人的错误：既然默认最多两个 worker，那有空槽是不是就该派一个？

真实使用下来，这会把项目做乱。

因为“安全可做”和“值得现在做”不是一回事。

如果今天的主线是 Customer checkout，就不应该为了填满并发槽，顺手派一个 Staff/RBAC，再派一个 KDS，再派一个报表。每个任务都能验收，但日报写出来像东一榔头西一棒槌。

后来我把规则改成 feature package 优先：

- 先定一个产品模块或功能闭环。
- 同一阶段尽量围绕这个 package 连续推进。
- 只有当前 package blocked、closed，或者需要 shared blocker removal，才切到下一个。
- available slots 只是容量，不是派发许可。

这是一个很重要的变化。

AI 编排不是多开几个 session，而是推进一个功能闭环。

## 为什么说它是 Loop Engineering

我理解的 Loop Engineering，不是写一个 while 循环让 Agent 一直跑。

它至少包括这些东西：

- 目标：这一轮到底要完成什么。
- 状态：真实 repo/worktree/ledger 现在是什么。
- 反馈：测试、构建、浏览器、设备、日志、review。
- 验收：谁来判断 worker branch 可不可以合并。
- 退出条件：什么时候继续，什么时候暂停，什么时候 blocked。
- 记忆：经验怎么沉淀成规则、fixture、policy，而不是只留在聊天里。

codex-orchestrator 做的就是这层外循环。

Codex App 仍然是执行者。它读代码、改代码、跑测试、提交 branch。

codex-orchestrator 是外层纪律：让每个 worker 的工作可恢复、可审查、可拒绝、可合并、可清理。

## 它现在不是什么

我不想把这个项目说得过头。

它现在不是：

- 一个完全自动的 daemon。
- 一个替代 Codex App 的客户端。
- 一个多 Agent 操作系统。
- 一个能保证电脑睡眠后继续运行的后台服务。
- 一个不经 review 就自动合并代码的 bot。
- 一个通用项目管理平台。

更准确地说，它是一个 Codex App-first 的工程编排工作流，加一个本地 helper。

skill 负责让 Codex App 学会这套工作方式。helper 负责 ledger、status、preflight、routine、policy/eval、self-update 这些本地辅助能力。

真正创建 session、读代码、写代码、执行 worker 的，仍然是 Codex App。

## 模型越来越接近，外层系统会越来越重要

我最近一个感受是：模型之间当然还有差距，但很多工程场景里，差距已经不是最主要的问题。

当模型都足够能写代码以后，差异会更多体现在：

- 谁能更好地定义任务；
- 谁能让模型在正确边界里工作；
- 谁能更快发现错误；
- 谁能把失败变成规则；
- 谁能让多个 session 的产出被稳定吸收进主分支。

这也是为什么我对 codex-orchestrator 这个方向越来越确定。

它不是押注某一个模型。它是在押注一个判断：AI coding 会越来越像一个需要控制系统的工程过程。

模型是发动机。

但真实项目还需要方向盘、仪表盘、刹车、行车记录仪和维修手册。

## 下一步我想做什么

接下来我会把重点放在四件事上。

第一，让状态页更像真正的驾驶舱。少一点机器字段，多一点人能直接看懂的判断：现在在做哪个产品包，为什么等，为什么不派发，哪里需要人。

第二，把失败沉淀成 fixture。每次遇到“pendingWorktreeId 没落账”“availableSlots 误导派发”“local proof 被写成 direct”这种问题，都应该能变成 policy/eval，而不是只靠我下次记得。

第三，把异模型 review 做成更自然的 checkpoint。小切片不一定需要，但一个 feature package 收口后，很适合生成 review pack，交给另一个模型做第二视角审查。

第四，继续用真实项目打磨。只有真实长跑才会暴露这些问题：heartbeat 漏跑、worker setup race、ledger 滞后、status 误导、文档漂移、证据过度声明。demo 很难测出来。

## 结语

codex-orchestrator 的由来，其实不是“我想做一个开源工具”。

它是我在真实项目里被这些问题反复打到以后，逐步整理出来的一套工程纪律。

一开始只是几条 prompt 规则。

后来变成 skill。

再后来有了 helper、ledger、status、routine、policy、eval、self-update。

但核心一直没变：

> 不要只让 AI 写更多代码。要让 AI 的工作进入一个可观察、可验收、可恢复、可持续推进的工程循环。

如果你也在用 Codex App 做真实项目，而不是只做一次性小任务，可以试试：

[github.com/indiekitai/codex-orchestrator](https://github.com/indiekitai/codex-orchestrator)

