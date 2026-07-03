---
title: "Three Models, One Landmine: Insuring an AI Refactor"
date: 2026-07-03
description: "Splitting an 18,782-line Go file can blow up even when compile and tests stay green. This time I had GPT, DeepSeek, and Kimi adversarially review the same plan — each caught what the others structurally could not."
tags: ["AI Coding", "Code Review", "Multi-Model", "Refactoring", "Loop Engineering", "Engineering Practice"]
lang: en
featured: true
---

[中文版](/blog/2026-07-03-multi-model-review-refactor)

The `main.go` of [codex-orchestrator](https://github.com/indiekitai/codex-orchestrator) had grown to 18,782 lines. 593 functions, 106 types, all in one file. Today I split it up.

The split itself is not the point of this post. The point is the hour before the plan was finalized: I had three models from three different families adversarially review the same refactoring plan, and each caught problems the others **structurally could not have caught** — including one landmine that would silently break two production features while compile, vet, the full test suite, and format checks all stayed green.

## A plan that looked solid

Some context first. When you split an 18,782-line file, the big fear is losing things in transit: a function vanishing mid cut-and-paste, a comment separated from its declaration. So the first draft of my plan centered on a set of mechanical acceptance gates:

- `go build` / `go vet` / full test suite (138 tests) green
- A top-level symbol inventory via `grep "^func \|^type "` before and after, diff must be empty
- `help` output byte-identical

Compiler + tests + symbol parity check. Three layers of insurance. I thought that was rigorous.

Then I fed the plan to three reviewers: Codex (GPT — given only the plan text, no repo access), Pi (DeepSeek — allowed to read the repo), and Kimi (K2.7 — allowed to read the repo). Same prompt, run independently, none seeing the others' conclusions.

## Each model caught something different

**Codex dismantled my "mechanical guarantee."** Looking at nothing but the plan text, it found three holes: `grep "^func "` misses method declarations, and worse, it never enumerates the entries inside `const`/`type`/`var` blocks; splitting a `const` block resets `iota` and breaks implicit value inheritance — and my plan literally contained the dangerous instruction to "move the global parts of the const blocks"; and package-level variable initialization order changes across files. All three are meta-problems: the verification itself was unreliable. Its fix: generate an AST manifest with `go/parser` — every declaration (receiver included), every spec inside every block, a hash of every doc comment — and diff it before and after.

**Pi found the landmine.** It read the actual code and discovered that two production code paths **read the source text of `main.go` at runtime** — the `docs-drift-checker` and `roadmap-next-task-suggester` routines enumerate runnable routines by parsing the `case "..."` strings inside `cmdRunRoutine`. The plan deleted main.go. After deletion: compile passes (string paths don't participate in compilation), tests pass (they build their own fixtures in temp dirs), help output unchanged, symbol parity unchanged — **every gate I designed waves it through** — and both routines crash in production.

**Kimi produced a better fix than Pi's.** Pi suggested changing the hardcoded path to scan all `.go` files, but Kimi pointed out that this cascades into evidence-text and test-assertion changes — modifying behavior in service of a "zero behavior change" refactor, which is backwards. Its proposal: don't delete main.go. Keep it as a 40-line shell containing only `cmdRunRoutine` plus a comment explaining that this function must stay in this file because two runtime self-inspections depend on it. Zero code change, zero semantic change. It also verified that the const block at line 16,144 was actually the policy-rule ID table, correcting an attribution contradiction in my plan.

Note that this division of labor was not something I orchestrated — it fell out of the difference in vantage points: **the model that only sees the plan attacks the plan's internal logic; the models that can read code attack the gap between plan and reality.** However smart a single model is, it can only stand in one place.

## Revise, execute, accept

With the three sets of findings merged (four P1s, seven P2s), the plan went to v2: grep replaced by AST manifest, const blocks moved whole or not at all, main.go kept as a thin shell, plus a static check watching the shell's integrity. Execution went to a cheaper-model worker in an isolated worktree, with ten gates that all had to pass before handoff.

At acceptance time I did not take the worker's word for it — every gate was re-run in its worktree, and the `help` output and test-name set were diffed against the main branch one by one. That discipline was learned the hard way: I have been burned more than once by a worker reporting "committed" when nothing was.

Final result: 21 production files + 10 test files, the largest at 1,670 lines; a 1,982-entry declaration manifest identical before and after; all 138 tests present. "Zero behavior change" stopped being a slogan and became a stack of reviewable empty diffs.

## Why "three models" and not "a more careful me"

You could argue that careful reading would have found those two runtime self-inspections. In theory, yes. But "careful" is not an engineering guarantee. Using human (or single-model) diligence as the safety net for an 18,782-line file is the same logic as skipping the seatbelt because you drive carefully.

In [the previous post](/blog/2026-06-14-codex-orchestrator-control-system-en) I argued that AI coding is not short on model capability — it is short on an outer control system. This is a concrete cross-section of that argument: **review is part of the control system, and single-model review has structural blind spots** — not because the model is weak, but because it shares its priors with the model that wrote the plan. Switch model families and the blind spot changes shape; stack three families and what slips through gets very small.

The cost? Three reviews ran in parallel, about fifteen minutes total, two of them on subscription quota I was already paying for. The alternative was two features failing silently and a late-night debugging session.

The math is easy. Remembering to do the math every time is the hard part.
