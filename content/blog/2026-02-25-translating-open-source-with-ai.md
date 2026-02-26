---
title: "Porting Open Source Libraries Across Languages with AI"
date: 2026-02-25
description: "We translated 6 libraries from Python, Rust, and Go into TypeScript in a single day using AI coding agents. 228 tests, all passing. Here's why translation is the sweet spot for AI-assisted development."
tags: ["AI", "coding", "TypeScript", "open-source", "English"]
lang: en
---

There's a [great article by 宝玉](https://baoyu.io/blog/ai/ai-coding-agent-sweet-spots) floating around about finding the "sweet spot" for AI coding agents — tasks where AI excels rather than struggles. After a lot of experimentation, we think we've found one of the best: **translating existing open-source libraries from one language to another**.

Last week, we ported 6 libraries into TypeScript in a single day. 228 tests total, all passing. Here's what we learned.

## Why Translation Is the Sweet Spot

Most AI coding advice focuses on greenfield projects — "build me an app from scratch." But that's actually one of the *harder* tasks for AI. The spec is fuzzy, the architecture decisions are subjective, and the AI has to invent things from nothing.

Translation is the opposite. You start with:

1. **A clear spec** — the source code *is* the spec. Every function, every edge case, every behavior is explicitly defined.
2. **Validated demand** — if a library has thousands of stars in Python, there's probably demand for a TypeScript version.
3. **Existing tests** — the original project's test suite tells you exactly what "correct" looks like. You just need to translate the tests too.
4. **Bounded scope** — a library is a self-contained unit. No databases, no deployment, no UI. Just pure logic with clear inputs and outputs.

This is exactly the kind of well-defined, mechanically complex but conceptually straightforward work where AI agents shine. The AI doesn't need taste or product intuition. It needs to understand two languages and faithfully convert between them.

## What We Built

Six projects, four source languages, one target (TypeScript), one day:

### [pg-inspect](https://github.com/indiekitai/pg-inspect)
**Python ([schemainspect](https://github.com/djrobstep/schemainspect)) → TypeScript**

PostgreSQL schema introspection. Connects to a database and extracts detailed information about tables, columns, indexes, constraints, enums, sequences, functions — everything you need to diff or migrate schemas. The original is a key dependency in the Python migration ecosystem.

### [throttled](https://github.com/indiekitai/throttled)
**Python ([throttled-py](https://github.com/urain39/throttled-py)) → TypeScript**

Rate limiting with multiple strategies: fixed window, sliding window, token bucket, leaky bucket, and GCRA. Supports in-memory and Redis backends. Clean, well-tested library — a perfect translation candidate.

### [just-ts](https://github.com/indiekitai/just-ts)
**Rust ([just](https://github.com/casey/just)) → TypeScript**

A command runner (think `make`, but sane). This was the most ambitious translation — Just is a full parser + interpreter written in Rust, with a rich feature set. The TypeScript version runs as a Node.js CLI tool with the same syntax and semantics.

### [pg-diff](https://github.com/indiekitai/pg-diff)
**Python ([migra](https://github.com/djrobstep/migra)) → TypeScript**

Schema diffing for PostgreSQL. Takes two database schemas (using pg-inspect under the hood) and generates the SQL migration to get from one to the other. The natural companion to pg-inspect.

### [lipgloss-ts](https://github.com/indiekitai/lipgloss-ts)
**Go ([lipgloss](https://github.com/charmbracelet/lipgloss)) → TypeScript**

Terminal styling from the Charm ecosystem. Lipgloss provides a declarative, composable API for styling terminal output — colors, borders, padding, alignment. The Go version is beloved; now Node.js developers can use the same API.

### [pg-top](https://github.com/indiekitai/pg-top)
**Python ([pg_activity](https://github.com/dalibo/pg_activity)) → TypeScript**

A `top`-like monitor for PostgreSQL. Shows running queries, locks, blocking sessions, and database statistics in a real-time terminal UI. Translated from Python's pg_activity with a TUI built using lipgloss-ts.

## The Process

After doing this six times, a clear pattern emerged:

### 1. Scan
Read the entire source project. Understand the architecture, the module structure, the public API. AI is great at this — feed it the whole codebase and ask for a summary.

### 2. Spec
Generate a translation spec: which modules map to which files, how do language-specific idioms translate (Python's `__init__.py` → `index.ts`, Rust's `impl` blocks → classes, Go's goroutines → async/await), and what the test strategy looks like.

### 3. Translate
Module by module, translate the source. Start with leaf dependencies (utilities, types) and work toward the core logic. The AI handles ~90% of the translation correctly on the first pass. The remaining 10% is usually:
- Language-specific idioms that don't map cleanly
- Subtle type system differences
- Standard library functions that need manual equivalents

### 4. Test
Translate the test suite. Run it. Fix failures. This is where the real debugging happens, but it's *directed* debugging — you know exactly what should pass, and the error messages tell you what's wrong.

### 5. Polish
Clean up TypeScript-specific concerns: add proper types (not just `any` everywhere), configure `tsconfig.json`, add exports, write a README. Ship it.

The whole cycle takes 2-4 hours per library for a moderately complex project. Simpler ones (like throttled) take under an hour.

## Results

| Project | Source | Tests | Status |
|---------|--------|-------|--------|
| pg-inspect | Python | 42 | ✅ All passing |
| throttled | Python | 35 | ✅ All passing |
| just-ts | Rust | 61 | ✅ All passing |
| pg-diff | Python | 28 | ✅ All passing |
| lipgloss-ts | Go | 37 | ✅ All passing |
| pg-top | Python | 25 | ✅ All passing |
| **Total** | | **228** | ✅ |

All six projects translated and tested in a single day. That's not a flex — it's a statement about how well-suited this task is for AI agents.

## Lessons Learned

**Tests are everything.** The single biggest factor in translation success is having a comprehensive test suite in the source project. Without tests, you're guessing whether your translation is correct. With tests, you have an oracle.

**Some languages translate better than others.** Python → TypeScript is the smoothest path. The languages share a lot of structural similarity (dynamic-ish, interpreted, similar stdlib patterns). Rust → TypeScript requires more creativity — ownership semantics, pattern matching, and traits don't have direct equivalents. Go → TypeScript is somewhere in between.

**Libraries translate better than applications.** A library with a clean API and no I/O dependencies is ideal. Applications with database connections, HTTP servers, and file system access require much more adaptation.

**The AI is better at translation than generation.** When you ask an AI to write something from scratch, it has to make hundreds of small design decisions. When you ask it to translate, most decisions are already made. It just needs to express the same logic in a different syntax.

**Type systems help, actually.** TypeScript's type system catches a lot of translation bugs at compile time. A function that returns `Optional[str]` in Python becomes `string | null` in TypeScript, and the compiler yells at you if you forget to handle the null case. This is a net positive for translation accuracy.

**Don't translate line-by-line.** The best translations are *idiomatic*. A Python list comprehension should become a `.map().filter()` chain, not a for loop. Rust's `match` expressions should use TypeScript's switch or object lookup patterns. The AI is surprisingly good at this when you prompt it correctly.

## What's Next

We're continuing to build out the TypeScript ecosystem with translated libraries. If you have a Python, Rust, or Go library you'd love to see in TypeScript, [open an issue](https://github.com/indiekitai) or reach out.

The bigger insight is about AI-assisted development in general: instead of asking "what can AI build from scratch?", ask "what existing work can AI help me *translate*, *adapt*, or *port*?" The answers might surprise you.

---

*All projects are open source and available on [GitHub](https://github.com/indiekitai). Contributions welcome.*
