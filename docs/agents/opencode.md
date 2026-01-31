<p align="center">
  <img src="../../assets/opencode.png" alt="OpenCode" width="120">
</p>

# OpenCode Agent

A specialized agent that interfaces with OpenCode CLI to provide access to 75+ AI models through OpenRouter. Enables intelligent model selection based on task requirements, performance needs, and cost optimization.

## When to Use

- Comparing outputs from different AI models
- Optimizing cost/performance ratios
- Accessing the latest AI models from any provider
- Switching between providers without vendor lock-in
- Selecting task-specific models for coding, documentation, or analysis
- Budget-constrained projects needing free/cheap options

## Capabilities

- **Multi-Model Access** - Switch between 75+ models via OpenRouter
- **Cost Optimization** - Select models based on performance/cost ratio
- **Task-Specific Selection** - Choose optimal models for specific tasks
- **Provider Agnostic** - Seamlessly switch between Anthropic, OpenAI, Google, Meta
- **Real-Time Model Updates** - Access new models immediately upon release
- **Vendor Independence** - Complete flexibility in model selection

## Invocation

```
Task tool with:
- subagent_type: "toolkit:opencode-agent"
- prompt: "Refactor this authentication module using Claude 3.5 Sonnet"
```

## Model Selection Strategy

### For Coding Tasks

| Tier | Model | Use Case |
|------|-------|----------|
| Premium | `anthropic/claude-3.5-sonnet` | Critical code, complex debugging |
| Standard | `openai/gpt-4o` | General development |
| Budget | `deepseek/deepseek-coder` | Routine coding |
| Free | `qwen/qwen-2.5-coder-32b` | Zero-budget projects |

### For Documentation

| Tier | Model | Use Case |
|------|-------|----------|
| Premium | `openai/gpt-4-turbo` | Comprehensive API docs |
| Budget | `mistralai/mixtral-8x7b` | README files |
| Free | `meta-llama/llama-3-8b` | Code comments |

### For Architecture Design

| Tier | Model | Use Case |
|------|-------|----------|
| Premium | `anthropic/claude-3-opus` | Microservices design |
| Open Source | `openai/gpt-oss-120b` | System architecture |
| Budget | `meta-llama/llama-3-70b` | Component design |

## Examples

**Model Comparison:**
```
Prompt: "Implement this sorting algorithm using GPT-4o, Claude 3.5 Sonnet, and GPT-OSS-120B for comparison"
```

**Cost-Optimized Analysis:**
```
Prompt: "Analyze this codebase using a budget-friendly model like DeepSeek Coder"
```

**Premium Task:**
```
Prompt: "Using Claude 3.5 Sonnet, refactor this complex authentication module"
```

## Command Patterns

### Basic Usage
```bash
# Default model
opencode -p "Your prompt"

# Specific model
opencode --model "anthropic/claude-3.5-sonnet" -p "Your prompt"

# Model discovery
opencode /models
```

## Cost Reference

Approximate costs per million tokens:

| Model | Cost |
|-------|------|
| Claude 3.5 Sonnet | $15 |
| GPT-4o | $10 |
| GPT-OSS-120B | $2 |
| Llama 3 70B | $0.9 |
| Mixtral 8x7B | $0.6 |
| Mistral 7B | $0.2 |
| Qwen 2.5 Coder | $0 |

## Progressive Escalation

Start with budget models and escalate only when necessary:

1. Try with `mistralai/mistral-7b` first
2. Escalate to `mixtral-8x7b` if needed
3. Use `claude-3.5-sonnet` for complex requirements

## Task Routing

| Task Type | Recommended Model |
|-----------|-------------------|
| Code | anthropic/claude-3.5-sonnet |
| Math | google/gemini-pro |
| Creative | anthropic/claude-3-opus |
| SQL | defog/sqlcoder |
| General | mistralai/mixtral-8x7b |

## Requirements

- **OpenCode CLI** - Auto-installed: `curl -fsSL https://opencode.ai/install | bash`
- **OpenRouter API Key** - For model access
- **Network Access** - Required for API calls

## See Also

- [codex-agent](codex.md) - OpenAI Codex specifically
- [groq-agent](groq.md) - Fast inference alternative
- [Models List](https://openrouter.ai/models) - All available models
