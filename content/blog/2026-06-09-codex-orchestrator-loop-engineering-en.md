---
title: "Loop Engineering for Codex and Claude Code: Why I Built codex-orchestrator"
date: 2026-06-09
description: "A practical Loop Engineering workflow for Codex, Claude Code, AI coding agents, worktree isolation, heartbeat monitoring, and supervised multi-session review/merge loops."
tags: ["AI Coding", "Codex", "Claude Code", "Loop Engineering", "AI Agent Orchestration", "Open Source"]
lang: en
featured: true
---

I recently read Addy Osmani's piece on [Loop Engineering](https://x.com/addyosmani/status/2064127981161959567), and it immediately matched something I had been building in practice.

Not just prompting an AI agent to write code.

The real shift is designing the loop around the agent: how work is split, isolated, monitored, reviewed, merged, recovered, and moved forward without turning a large codebase into chaos.

That is the idea behind [codex-orchestrator](https://github.com/indiekitai/codex-orchestrator), a Codex skill I recently open-sourced.

It came from a simple problem: in a real multi-module rewrite, a single coding session was no longer enough.


## If you are searching for Loop Engineering, Codex, or Claude Code

This post is not about a single prompt trick. It is about engineering the loop around AI coding agents such as OpenAI Codex, Claude Code, Cursor Agent, or any tool that can work inside a repository.

The relevant keywords are: Loop Engineering, Codex orchestration, Claude Code orchestration, AI agent orchestration, multi-agent coding workflow, worktree isolation, heartbeat monitoring, and review/merge automation.

If your problem is not "can the agent write code?" but "how do I safely keep several coding agents moving through a large roadmap?", this is the layer codex-orchestrator is trying to address.

## The single-agent workflow breaks down

For small tasks, the workflow is straightforward.

You give Codex a focused request. It reads the code, makes a scoped change, runs a test, and reports back.

That works well.

But as the project gets larger, the bottleneck changes. The hard part is no longer whether the model can generate code. The hard part is whether the generated work can be organized, reviewed, trusted, merged, and kept aligned with the roadmap.

The failures start to look like this:

- One session accumulates too much context and starts losing the thread.
- Two tasks accidentally touch the same contract or directory.
- A worker session gets stuck, but nobody notices for hours.
- An agent says a task is done, but the proof is only local, not runtime or device-level.
- A roadmap has many safe next tasks, but choosing and dispatching them still depends on manual attention.
- The expensive part becomes review, merge, push, cleanup, and documentation sync.

At that point, asking for "more code" is not enough.

You need an engineering loop.

## What codex-orchestrator does

`codex-orchestrator` is not a daemon or a SaaS product. It is a Codex skill and runbook for supervising multiple Codex sessions in a disciplined way.

The core loop is:

1. Pick a bounded task from the roadmap.
2. Create a separate worktree and branch.
3. Start a fresh Codex session for that task.
4. Tell the worker not to launch subagents or use another orchestrator.
5. Require the worker to commit, but not merge, push, or clean up.
6. Use heartbeat checks to inspect active sessions, worktrees, branches, and commits.
7. When a task finishes, review the diff from the orchestrator session.
8. Verify allowed paths, forbidden paths, docs, tests, artifacts, and residual risks.
9. Merge only after review passes.
10. Push main, clean the worktree, delete the local branch, and dispatch the next task if safe.

This turns Codex from a single coding assistant into a supervised multi-session engineering loop.

The human is still in charge. The loop just removes a lot of repetitive coordination work.

## Worktrees are the foundation

Parallel AI coding without isolation quickly becomes messy.

If two agents share the same working directory, they can overwrite each other's assumptions, mix unrelated diffs, and make review nearly impossible.

So codex-orchestrator treats separate worktrees as a default, not an optimization.

Each task gets:

- its own worktree,
- its own branch,
- its own Codex session,
- its own final handoff,
- and its own review/merge decision.

That gives the orchestrator a clean unit of work. A failed task can be left in place for inspection. A successful task can be merged and cleaned up. A blocked task can stay blocked without contaminating main.

This is ordinary Git discipline, but it becomes much more important when agents can produce changes quickly.

Speed without isolation is just faster confusion.

## Heartbeats make the loop persistent

A major part of the workflow is the heartbeat.

The orchestrator periodically wakes up and checks the real state of the project:

- `git status`
- `git worktree list`
- delegated session status
- recent commits
- expected branches
- pending setup failures
- completed handoffs
- roadmap and progress docs

One lesson from practice: heartbeat prompts should not depend on hardcoded historical task IDs.

Tasks may finish in minutes. If the automation keeps watching old IDs, the loop drifts. The better pattern is dynamic discovery: infer active, pending, completed, stale, or blocked tasks from repo truth, thread status, worktree state, branch names, and commit history.

The orchestrator should follow reality, not an old prompt.

## Review is more important than dispatch

The most important part of this workflow is not launching agents.

It is reviewing them.

Every delegated worker is expected to provide a final handoff with:

- task ID,
- branch and commit,
- worktree path,
- changed files,
- gates run,
- artifact paths,
- self-review,
- residual risks,
- and evidence labels.

But the orchestrator does not blindly trust the handoff.

It rereads the diff. It checks whether the worker touched forbidden paths. It verifies that documentation stayed synchronized. It checks whether proof was labeled honestly.

This matters because AI agents often do not fail by writing obviously broken code. They fail by overstating confidence.

A local unit test is not production proof. A proxy signal is not direct device evidence. A "sent" state is not the same as a durable acknowledgment.

For that reason, the workflow uses explicit evidence labels:

- `direct`: observed on the real target surface,
- `proxy`: useful but indirect evidence,
- `blocked`: not proven, with the reason recorded.

`blocked` is not a failure. It is an honest engineering state.

## The loop does not replace the engineer

This workflow is not about removing the engineer from software development.

It moves the engineer to a higher-leverage position.

The human still decides:

- what should be built,
- which tasks are safe to parallelize,
- which contracts must be serialized,
- which proof is strong enough,
- when hardware or production access is required,
- and when a result should not be merged.

In real projects, some steps still require human action: operating a payment terminal, unplugging a device, opening a printer cover, confirming a deploy window, or deciding a product policy.

The loop can notify, pause, and wait. It cannot replace judgment.

That distinction is important. A good orchestrator does not create unsupervised chaos. It creates supervised momentum.


## FAQ: Is this only for Codex? What about Claude Code?

**Is codex-orchestrator only for OpenAI Codex?**

The repository is packaged as a Codex skill, so the concrete workflow is written for Codex App sessions, Codex worktrees, and Codex heartbeat-style monitoring.

But the underlying pattern is broader. Claude Code, Cursor Agent, and other coding agents run into the same operational problems: task isolation, stale sessions, parallel branches, review discipline, proof quality, and cleanup ownership.

**Why mention both Codex and Claude Code?**

Because the core idea is Loop Engineering for AI coding agents. Codex is the implementation surface I used first. Claude Code is another common surface where the same orchestration discipline applies.

**Is this a multi-agent framework?**

Not in the traditional sense. It is closer to an executable engineering runbook: how to dispatch work, monitor it, review it, merge it, and stop when human input or stronger evidence is required.

## Why I open-sourced it

I open-sourced codex-orchestrator because the pattern feels broadly useful.

Many engineers are already past the first stage of AI coding. We know the agent can write code. The next question is whether we can build repeatable systems around that ability.

For me, the valuable pattern was not one clever prompt. It was the combination of:

- bounded task contracts,
- worktree isolation,
- heartbeat monitoring,
- dynamic task discovery,
- worker self-review,
- orchestrator review,
- merge/push/cleanup ownership,
- honest evidence labels,
- and roadmap-driven continuation.

Individually, none of these are magic.

Together, they turn AI coding from a chat interaction into an engineering workflow.

The repo is here:

[https://github.com/indiekitai/codex-orchestrator](https://github.com/indiekitai/codex-orchestrator)

If you are using Codex App for large modules, multi-session development, overnight implementation queues, or long-running project slices, this may save you from reinventing the same loop.

The short version:

Do not just prompt the agent.

Design the loop. Stay the engineer.
