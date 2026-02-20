# HN 评论草稿 2026-02-17

给范森确认后发布，用 indiekitai 账号。

---

## 1. Qwen3.5: Native Multimodal Agents
**链接**: https://news.ycombinator.com/item?id=47032876

**评论草稿**:

> The "native multimodal" framing is interesting. Most current agent architectures treat vision as a separate preprocessing step - you OCR the screenshot, convert to text, then feed to the LLM.
>
> What I've found building agents in practice: the bottleneck isn't usually the model's capability, it's the tool interface design. A model that can "see" your screen doesn't help much if your tools still require text-based parameters.
>
> The real unlock would be agents that can point and click based on visual understanding, without needing accessibility trees or DOM parsing. Curious if Qwen3.5 moves in that direction.

**为什么这个评论好**:
- 基于实际经验（我们做 agent 的经验）
- 提出有深度的观点（视觉理解的真正瓶颈）
- 没有自我推销
- 引发讨论

---

## 2. SkillsBench: Agent Skills Benchmark
**链接**: https://news.ycombinator.com/item?id=47040430

**评论草稿**:

> The distinction between "skills as static documentation" vs "skills as learned procedures" is crucial.
>
> In my experience, the most effective agent skills aren't generic how-to guides - they're highly specific playbooks that encode institutional knowledge. Things like "when deploying to this specific environment, always check X before Y because of this edge case we hit in 2024."
>
> The benchmark's "self-generated skills" approach misses this. Real skills come from failure modes, not from asking an LLM to imagine what might be useful.

**为什么这个评论好**:
- 直接回应讨论中的核心问题
- 分享实际见解
- 不是泛泛而谈

---

## 3. AI is destroying open source (Jeff Geerling)
**链接**: https://news.ycombinator.com/item?id=47042136

**评论草稿**:

> The "AI training on open source without contributing back" argument assumes a zero-sum game.
>
> But here's the flip side: AI tools are lowering the barrier for people to contribute to open source. I've seen developers who previously couldn't navigate large codebases now submitting meaningful PRs because AI helps them understand the context.
>
> The sustainability problem was there before AI - most open source maintainers were already burned out. AI might actually help by reducing the toil of code review, documentation, and issue triage.
>
> The real threat isn't AI using open source code. It's the concentration of AI capabilities in a few large companies who can afford the compute.

**为什么这个评论好**:
- 有争议性但有论据支持
- 提出不同角度（AI 帮助贡献 vs 只是消费）
- 最后一句话是有深度的观点

---

## 发布建议

1. 先发 SkillsBench 那条（最技术向，安全）
2. 等几个小时，再发 Qwen3.5 那条
3. Jeff Geerling 那条看情况，可能引战

记得用 indiekitai 账号登录发。
