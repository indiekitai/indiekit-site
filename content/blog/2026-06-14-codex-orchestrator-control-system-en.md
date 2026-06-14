---
title: "AI Coding Does Not Need More Model Hype. It Needs Control Systems."
date: 2026-06-14
description: "Why I built codex-orchestrator: a Codex App-first control layer for worktree isolation, persistent ledgers, heartbeat monitoring, review packs, and evidence-labeled engineering loops."
tags: ["AI Coding", "Codex", "Loop Engineering", "AI Agents", "Engineering", "Open Source"]
lang: en
featured: true
---

[中文版本](/blog/2026-06-14-codex-orchestrator-control-system)

Over the past few weeks, one idea has become increasingly clear to me:

AI coding is no longer limited only by model capability.

Models still differ. Some reason better. Some write cleaner code. Some hold context more reliably. But for many real engineering tasks, today’s models are already good enough to do useful work.

The harder question is:

> Once an AI agent can keep writing code, changing code, and running tests, how do we manage the work it produces?

That is why I built [codex-orchestrator](https://github.com/indiekitai/codex-orchestrator).

It is not another tool that tries to make the model write more code. It is a control layer around Codex App: split work, isolate it in worktrees, persist task state, wake up on a heartbeat, detect stuck sessions, review completed branches, merge clean work, clean up after workers, and keep moving through a roadmap.

## It started as a practical problem

I did not start by trying to build a product.

I was working on a large multi-module rewrite. The project had frontend apps, backend services, mobile surfaces, reporting, payments, printing, sync, permissions, and device-facing flows.

A single Codex session worked well for small tasks. But as the project grew, a different class of problem appeared:

- One long-running session accumulated too much context.
- Two independent tasks could accidentally touch the same contract, database model, or UI entry point.
- A worker session could get stuck without me noticing.
- An agent might say “done” when the evidence was only local, not runtime, device, pre-production, or production proof.
- After code was written, the expensive part was still review, merge, push, cleanup, and documentation sync.

So the first version of codex-orchestrator was not a CLI. It was a set of rules.

Each delegated task should run in its own worktree and branch. A worker should only commit to its own branch. It should not merge, push, or clean up its worktree. The orchestrator session should monitor, review, merge, push, and clean up.

That worked well enough to reveal the next problem: rules inside chat are not durable.

Chat context gets compressed. Task IDs go stale. Heartbeats can be missed. Worker state and Git state can disagree. So the project slowly grew from a Codex skill into a small Go helper CLI.

## Treat worker branches as reviewable delivery units

“Multi-agent coding” often sounds like hiring a few extra AI employees.

I now think that is the wrong mental model.

The better model is this: every worker branch is a reviewable, rejectable, recoverable delivery unit.

When a worker says it is finished, I do not want to trust the sentence. I want to inspect the unit:

- Which worktree did it use?
- Which branch did it commit to?
- Which base commit did it start from?
- Which files changed?
- Did it touch forbidden paths?
- Which gates did it run?
- Did it write a self-review?
- Is the evidence direct, proxy, local, or blocked?
- Is the worktree clean?

That checklist is often more valuable than asking the model to be a little smarter.

In real projects, the most dangerous failure is not always bad code generation. It is overclaiming evidence:

- A local test is described as runtime proof.
- A static check is described as direct proof.
- Proxy evidence is promoted to pre-production or production evidence.
- A page opening in a browser is described as a completed business flow.

This is why codex-orchestrator has an evidence-label discipline. The labels are not decoration. They are part of the safety model.

## Why a ledger matters

At first, I thought the orchestrator session could simply remember what was going on.

That did not scale.

In a long-running loop, state spreads across many surfaces:

- the current chat context;
- the Codex App thread;
- whether a worktree was actually created;
- whether the branch is correct;
- whether the worker has a clean commit;
- whether `main` is ahead of `origin/main`;
- whether review docs exist;
- whether the task was merged, pushed, and cleaned.

If that state only lives in chat, it eventually becomes unreliable.

So codex-orchestrator uses a local `.codex-orchestrator/ledger.json`.

The ledger does not replace Codex App. It gives the outer loop a durable local task record. A task can move from pending setup, to active, to completed-unreviewed, to accepted, merged, pushed, and cleaned.

This is not about making AI write code. It is about answering a very practical question:

> When I wake up tomorrow morning, how do I know what actually happened overnight?

## Heartbeat is useful, but it is not magic

I used to think that adding a heartbeat would make the loop unattended.

Reality was more humbling.

Codex App can wake a thread on a schedule, but that is not the same as an operating-system-level daemon. The machine may sleep. The app may not dispatch the automation. The thread may not get a wakeup.

So I now describe this more conservatively:

- Codex App heartbeat is an app-level wakeup mechanism.
- The helper’s heartbeat report is local/static evidence.
- A watchdog can improve local visibility, but it is still a local helper.
- If the machine or app does not wake up, the helper can only report the gap after it runs again.

That may sound less exciting, but it is more honest.

Reliable engineering systems are not built by declaring “fully autonomous.” They are built by naming boundaries, then adding observation, logs, alerts, and recovery paths around those boundaries.

## The status page is not a dashboard. It is a visibility layer.

One lesson surprised me: without a status page, the human operator feels blind.

The loop may be running, but you cannot quickly tell whether it is:

- waiting for a worker;
- waiting for worktree setup;
- ready for review;
- merged but not pushed;
- stuck with cleanup residue;
- done with the current feature package;
- or merely showing available slots even though it should not dispatch more work.

Early on, I relied on command output and chat summaries. That was not enough.

So codex-orchestrator now writes `status.md` and `status.html`. They are not meant to be fancy dashboards. They are meant to answer the operational questions:

- What is the current feature lane?
- Which worker is active?
- Is anything ready for review?
- Does this need a human?
- Is the loop active, draining, or paused?
- Was there a missed heartbeat?
- Should the loop continue, wait, review, or stop dispatching?

The goal is simple: reduce the anxiety of not knowing what the agent system is doing.

## The biggest trap: dispatching just because capacity exists

One early mistake was very tempting.

If the system allows two concurrent workers and only one is active, should it dispatch another?

Not necessarily.

“Safe to run” and “worth running now” are different things.

If the current feature package is Customer Checkout, the orchestrator should not randomly dispatch a Staff/RBAC task, then a KDS task, then a reporting task just because those tasks do not conflict at the file level.

Each task may be individually reviewable, but the daily progress report will look scattered.

So I changed the rule: feature package first.

- Pick a product module or feature package.
- Keep moving within that package.
- Switch only when the package is closed, blocked, owner-gated, or when a shared blocker must be removed.
- Treat available slots as capacity, not permission.

This was one of the most important product lessons:

> AI orchestration is not “open more sessions.” It is “advance a feature loop.”

## What I mean by Loop Engineering

I do not think Loop Engineering means writing a `while` loop around an agent.

It means designing the outer system around the agent:

- the goal;
- the current state;
- the feedback surface;
- the reviewer;
- the merge decision;
- the stop condition;
- the way failures become rules, fixtures, or policy checks.

Codex App remains the executor. It reads code, edits files, runs tests, and commits branches.

codex-orchestrator provides the operating discipline around that executor. It makes the work reviewable, recoverable, rejectable, mergeable, and cleanable.

## What it is not

I do not want to overstate the project.

codex-orchestrator is not:

- a fully autonomous daemon;
- a replacement for Codex App;
- a multi-agent operating system;
- a guarantee that work continues while your computer sleeps;
- a bot that merges code without review;
- a general project management platform.

The accurate description is smaller and more useful:

It is a Codex App-first engineering orchestration workflow, plus a local helper.

The skill teaches Codex App how to run the workflow. The helper provides ledger state, status pages, preflight checks, routines, policy/eval checks, and self-update support.

Codex App still creates the sessions, reads the code, writes the code, and runs the worker tasks.

## As models converge, control systems matter more

My current intuition is that model differences will still matter, but the leverage will increasingly move outward.

When models are all capable enough to write code, the differentiator becomes:

- who defines the work better;
- who keeps the model inside the right boundaries;
- who detects mistakes faster;
- who turns repeated failures into rules;
- who can absorb multiple worker outputs into the main branch safely.

That is why I am increasingly confident in this direction.

codex-orchestrator is not a bet on one model. It is a bet on a pattern:

> AI coding needs control systems.

The model is the engine.

Real projects still need steering, instruments, brakes, logs, and maintenance procedures.

## What comes next

I want to keep improving four areas.

First, the status page should become more human-readable. Less raw machine state, more direct answers: what is happening, why are we waiting, why are we not dispatching, and where is human input required?

Second, failures should become fixtures. If we see `pendingWorktreeId` not recorded, `availableSlots` encouraging a bad dispatch, or local proof being overclaimed as direct proof, that should become a policy/eval case.

Third, external model review should become a natural checkpoint. Small slices may not need it. But when a feature package closes, generating a review pack for another model is useful.

Fourth, I want to keep testing it on real projects. Demos rarely expose the hard problems: missed heartbeats, setup races, stale ledgers, misleading status pages, documentation drift, and evidence overclaims.

## Closing

codex-orchestrator did not start as an open-source product idea.

It started as a set of engineering habits I needed in order to use Codex App on a real project without losing control of the codebase.

First it was a prompt pattern.

Then it became a skill.

Then it gained a helper, a ledger, a status page, routines, policy checks, eval fixtures, and self-update.

But the core idea has stayed the same:

> Do not just make AI write more code. Put AI work into an observable, reviewable, recoverable engineering loop.

If you use Codex App for real projects rather than one-off edits, you can try it here:

[github.com/indiekitai/codex-orchestrator](https://github.com/indiekitai/codex-orchestrator)

