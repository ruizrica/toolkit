# Agents Overview

The toolkit ships **5 specialized agents** that can be invoked as slash commands. Each agent wraps a different external CLI and is optimized for specific use cases.

> **v1.3.0 — refined release.** The agent roster was pruned from 9 to 5. Dropped: `qwen-agent`, `groq-agent`, `crush-agent` (out-of-scope media optimization), and `rlm-subcall` (orphaned with `/rlm`). The surviving 5 cover large-context analysis, review/refactoring, code generation, enterprise workflows, and multi-model routing — no more overlap.

## Quick Reference

| Agent | Specialty | CLI Tool | Best For |
|-------|-----------|----------|----------|
| [gemini-agent](gemini.md) | Large codebase analysis | Gemini CLI | Monorepos >100KB, 1M-token context, web search |
| [cursor-agent](cursor.md) | Code review, refactoring | Cursor CLI | Complex refactoring, session management |
| [codex-agent](codex.md) | Natural language → code | Codex CLI | Code generation, translation across languages |
| [droid-agent](droid.md) | Enterprise development | Droid CLI | Architecture, Jira/Notion/Slack integration |
| [opencode-agent](opencode.md) | Multi-model access | OpenCode CLI | Access to 75+ models via OpenRouter, cost optimization |

---

## How to Invoke Agents

Invoke any agent as a slash command with the `toolkit:` prefix:

```bash
/toolkit:gemini-agent Analyze the authentication module for security issues
```

Format: `/toolkit:<agent-name> <your prompt>`.

---

## By Capability

| Need | Agent |
|------|-------|
| Massive context (>100 KB, whole-repo reviews) | [gemini-agent](gemini.md) — 1M tokens |
| Real-time web search during analysis | [gemini-agent](gemini.md) |
| Session continuity across prompts | [cursor-agent](cursor.md) |
| Model comparison or cost control | [opencode-agent](opencode.md) |
| Enterprise integrations (Jira, Notion, Slack) | [droid-agent](droid.md) |
| Cross-language code translation | [codex-agent](codex.md) |

---

## By Cost

**Budget / free options**
- [opencode-agent](opencode.md) — access to free models like Qwen 2.5 Coder, DeepSeek Coder
- [cursor-agent](cursor.md) — default model is well-optimized for common work

**Standard**
- [cursor-agent](cursor.md) — everyday review and refactoring

**Premium**
- [gemini-agent](gemini.md) — Gemini 2.5 Pro for massive codebases
- [codex-agent](codex.md) — OpenAI Codex models for complex generation
- [droid-agent](droid.md) — enterprise-grade capabilities

---

## Comparison Matrix

| Feature | gemini | cursor | codex | droid | opencode |
|---------|:------:|:------:|:-----:|:-----:|:--------:|
| Large context (≥256 K) | ✅ 1M | ❌ | ❌ | ❌ | depends |
| Web search | ✅ | ❌ | ❌ | ❌ | ❌ |
| Session management | ❌ | ✅ | ❌ | ❌ | ❌ |
| Multi-model routing | ❌ | ❌ | ❌ | ❌ | ✅ |
| Enterprise integrations | ❌ | ❌ | ❌ | ✅ | ❌ |
| Speed | Medium | Medium | Medium | Medium | Varies by model |

---

## When To Use Which

- **Research / whole-repo analysis** → `gemini-agent` (biggest context)
- **Targeted code review and refactoring** → `cursor-agent`
- **Generating new code from spec / translating between languages** → `codex-agent`
- **Enterprise workflows touching Jira/Notion/Slack** → `droid-agent`
- **Need a specific model or want to compare outputs** → `opencode-agent`

If you want a team to work on something in parallel, use [`/team`](../commands/team.md) — it dispatches to multiple agents at once.
