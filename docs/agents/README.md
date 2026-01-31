# Agents Overview

The Toolkit includes 9 specialized agents that can be invoked via the Task tool. Each agent is optimized for specific use cases and leverages different AI models and CLI tools.

## Quick Reference

| Agent | Specialty | CLI Tool | Best For |
|-------|-----------|----------|----------|
| [gemini-agent](gemini.md) | Large codebase analysis | Gemini CLI | Monorepos >100KB, 1M token context |
| [cursor-agent](cursor.md) | Code review, refactoring | Cursor CLI | Complex refactoring, sessions |
| [codex-agent](codex.md) | Natural language → code | Codex CLI | Code generation, translation |
| [qwen-agent](qwen.md) | Agentic coding workflows | Qwen CLI | Workflow automation, git ops |
| [opencode-agent](opencode.md) | Multi-model access | OpenCode CLI | Model comparison, cost optimization |
| [groq-agent](groq.md) | Fast inference | Groq CLI | Quick completions, rapid iteration |
| [crush-agent](crush.md) | Media optimization | Crush CLI | Image/video compression |
| [droid-agent](droid.md) | Enterprise development | Droid CLI | Architecture, enterprise integration |
| [rlm-subcall](rlm-subcall.md) | Document chunk analysis | N/A | RLM workflow support |

---

## How to Invoke Agents

Agents are invoked via the Task tool with the `toolkit:` prefix:

```
Task tool with:
- subagent_type: "toolkit:gemini-agent"
- prompt: "Analyze the authentication module for security issues"
```

---

## Selection Guide

### By Task Type

**Large Codebase Analysis**
- [gemini-agent](gemini.md) - Best for codebases >100KB with 1M token context window
- [droid-agent](droid.md) - Enterprise-grade analysis with transparent review

**Code Generation**
- [codex-agent](codex.md) - Natural language to code conversion
- [groq-agent](groq.md) - Fast, lightweight code generation
- [opencode-agent](opencode.md) - Access to 75+ models for comparison

**Code Review & Refactoring**
- [cursor-agent](cursor.md) - Advanced review with session continuity
- [droid-agent](droid.md) - Enterprise workflows with approval process

**Workflow Automation**
- [qwen-agent](qwen.md) - Git automation, batch operations
- [droid-agent](droid.md) - Jira/Notion/Slack integration

**Media Processing**
- [crush-agent](crush.md) - Image and video compression

**Document Processing**
- [rlm-subcall](rlm-subcall.md) - Chunk analysis for RLM workflow

---

### By Speed vs. Capability

| Priority | Agent | Notes |
|----------|-------|-------|
| Speed | [groq-agent](groq.md) | Fastest inference, minimal latency |
| Speed | [opencode-agent](opencode.md) | Free/budget models available |
| Balance | [cursor-agent](cursor.md) | Good balance of speed and capability |
| Balance | [qwen-agent](qwen.md) | Strong reasoning with good speed |
| Capability | [gemini-agent](gemini.md) | Largest context window (1M tokens) |
| Capability | [codex-agent](codex.md) | Best for complex code generation |
| Capability | [droid-agent](droid.md) | Enterprise features, review workflow |

---

### By Cost Consideration

**Free/Budget Options**
- [opencode-agent](opencode.md) - Access to free models like Qwen 2.5 Coder
- [groq-agent](groq.md) - Fast and cost-effective

**Standard**
- [cursor-agent](cursor.md) - Default model is well-optimized
- [qwen-agent](qwen.md) - ModelScope offers free tier

**Premium**
- [gemini-agent](gemini.md) - Gemini 2.5 Pro for massive codebases
- [codex-agent](codex.md) - OpenAI Codex models
- [droid-agent](droid.md) - Enterprise-grade capabilities

---

## Agent Comparison Matrix

| Feature | gemini | cursor | codex | qwen | opencode | groq | crush | droid |
|---------|--------|--------|-------|------|----------|------|-------|-------|
| Large Context | ✅ 1M | ❌ | ❌ | ✅ 256K | ❌ | ❌ | N/A | ❌ |
| Web Search | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | N/A | ❌ |
| Sessions | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | N/A | ❌ |
| Multi-Model | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | N/A | ❌ |
| Enterprise | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | N/A | ✅ |
| Offline | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| Speed | Medium | Medium | Medium | Medium | Varies | Fast | Fast | Medium |

---

## Common Patterns

### Investigation → Implementation

1. Use [gemini-agent](gemini.md) to analyze codebase architecture
2. Use [codex-agent](codex.md) to generate new code
3. Use [cursor-agent](cursor.md) to review and refactor

### Cost-Optimized Workflow

1. Start with [groq-agent](groq.md) for quick prototypes
2. Use [opencode-agent](opencode.md) with budget models for iteration
3. Escalate to premium models only when needed

### Enterprise Workflow

1. Use [droid-agent](droid.md) with Jira integration
2. Follow transparent review process
3. Maintain audit trail

---

## Requirements

Most agents auto-install their CLI tools. Common requirements:

- **Node.js 18+** - For npm-based CLIs
- **Python 3.8+** - For some agents
- **API Keys** - Each agent requires appropriate API credentials

See individual agent documentation for specific setup instructions.
