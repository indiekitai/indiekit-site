---
title: "Open-Sourced: The Multi-Agent Orchestration Discipline (orchestration-playbook)"
date: 2026-07-03
description: "The orchestration discipline distilled from a 53-batch, ~95-agent, ~70k-line production run, unbundled into a 3,000-word tool-free playbook: four-level evidence discipline, the ten-field dispatch contract, acceptance iron rules, and the ORC-01~18 anti-pattern table. Copy it into your CLAUDE.md and go."
tags: ["AI Coding", "Multi-Agent", "Open Source", "Loop Engineering", "Engineering Practice"]
lang: en
featured: true
---

[中文版](/blog/2026-07-03-orchestration-playbook)

I've extracted the orchestration discipline shared by codex-orchestrator / claude-orchestrator / kimi-orchestrator into a standalone, harness-agnostic repository:

**[indiekitai/orchestration-playbook](https://github.com/indiekitai/orchestration-playbook)**

## Why unbundle it

The three orchestrators are runtimes for three harnesses (Codex App / Claude Code / Kimi Code) — ledgers, heartbeats, packs, routines are per-harness adapter details. But what actually keeps parallel agents from crashing into each other was never those mechanisms; it's the discipline behind them. Until now it was buried across three SKILL.md files totaling 130KB, where a new reader couldn't tell which 20% is load-bearing and which 80% is sediment specific to my projects.

The core is now under 3,000 words, and **every rule is backed by a real incident**:

- **The four-level evidence discipline** (direct / proxy / local / blocked, upgrading forbidden) — because a local unit test once got quietly "promoted" into production proof
- **The ten-field dispatch contract** — because I've seen every ending of "dispatch first, clarify boundaries later"
- **Acceptance iron rules**: "a worker's 'committed' is not evidence" — because a worker once reported the commit done while the changes sat uncommitted in the worktree; the worktree got removed and everything was redone
- **The ORC-01~18 anti-pattern table** — from "phantom commit" to "motion mistaken for progress", one ID each; pointing at numbers beats writing prose in reviews

## Usable with zero tooling

The repo is deliberately shaped to be copied. The minimum adoption path is four steps: copy the evidence discipline and acceptance rules into your CLAUDE.md / AGENTS.md; use the ten contract fields as a checklist when handing tasks to agents; run one cross-model review per merged feature package; point at ORC IDs when reviewing.

Go to the three adapter repos when you want the full runtime — but most people only need the discipline itself.

## It ships with a real case file

The [CASE-STUDY](https://github.com/indiekitai/orchestration-playbook/blob/main/CASE-STUDY.md) in the repo happened today: splitting an 18,782-line Go file, where every mechanical gate in the first plan (compile + vet + 138 tests + symbol parity) would have waved through a runtime self-inspection landmine — caught only by cross-model review. The IMPL, all 16 review findings, and the split commits are public and checkable — not a demo script, real commits in a real repository. Full story in [the previous post](/blog/2026-07-03-multi-model-review-refactor-en).

If you're running any coding agent on work longer than an afternoon, this playbook likely contains a trap you've already hit — or are about to.
