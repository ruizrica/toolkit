<p align="center">
  <img src="../../assets/groq.png" alt="Groq" width="120">
</p>

# Groq Agent

A specialized agent that interfaces with groq-code-cli to provide lightning-fast code generation and assistance. Uses Groq's high-speed inference API for minimal latency, designed to be lightweight, hackable, and customizable.

## When to Use

- Speed is the primary concern for code generation
- Simple, direct code assistance is needed
- Quick prototyping and iteration is required
- You want a customizable, hackable CLI
- Minimal overhead and complexity is desired
- Fast response times are critical for workflow

## Capabilities

- **Lightning-Fast Generation** - Leveraging Groq's speed for instant code creation
- **Minimalist CLI** - Lightweight, hackable CLI framework
- **Quick Iterations** - Rapid prototyping and code refinement
- **Custom System Messages** - Tailoring AI behavior with custom prompts
- **Debug Logging** - Tracking and debugging AI interactions
- **Proxy Support** - Working through various network configurations
- **Temperature Control** - Fine-tuning generation creativity

## Invocation

```
Task tool with:
- subagent_type: "toolkit:groq-agent"
- prompt: "Quickly generate a React component for a user profile"
```

## Examples

**Quick Code Generation:**
```
Prompt: "Write a Python function to calculate fibonacci numbers"
```

**Fast Iteration:**
```
Prompt: "Help me iterate quickly on this algorithm implementation"
```

**Custom Behavior:**
```
Prompt: "As an expert Python developer, optimize this code for performance"
```

## Command Patterns

### Basic Code Generation
```bash
groq "Write a Python function to calculate fibonacci numbers"
```

### Custom System Messages
```bash
groq -s "You are an expert Python developer" "Optimize this code for performance"
```

### Temperature Control
```bash
# High creativity (1.0 default)
groq -t 1.5 "Generate creative variable names for a space game"

# Low creativity (more deterministic)
groq -t 0.2 "Fix this syntax error"
```

### Debug Mode
```bash
groq -d "Debug why this function returns null"
```

### Proxy Configuration
```bash
# HTTP proxy
groq --proxy http://proxy:8080 "Generate API endpoint"

# SOCKS5 proxy
groq --proxy socks5://proxy:1080 "Create database schema"
```

## Key Operating Principles

1. **Speed First** - Prioritize quick responses and minimal latency
2. **Keep It Simple** - Work within the streamlined feature set
3. **Customization Ready** - The CLI is designed to be modified
4. **Direct Execution** - Use simple, direct commands
5. **Debug When Needed** - Enable debug logging for troubleshooting

## Temperature Guide

| Temperature | Use Case |
|-------------|----------|
| 0.2 | Syntax fixes, deterministic output |
| 0.5 | Balanced creativity and accuracy |
| 1.0 | Default - general purpose |
| 1.5 | Creative naming, experimental code |

## Requirements

- **groq-code-cli** - Auto-installed: `npm install -g groq-code-cli@latest`
- **Groq API Key** - Set via `groq config set GROQ_API_KEY`
- **Node.js** - For npm installation

## Error Handling

| Issue | Solution |
|-------|----------|
| CLI not found | Run `npm link` after building |
| API key missing | Set via `groq config set GROQ_API_KEY` |
| Network issues | Configure proxy with `--proxy` flag |
| Debugging needed | Enable with `-d` flag |

## When NOT to Use

- Complex multi-step workflows requiring orchestration
- Tasks needing extensive context management
- Session persistence and conversation history
- Advanced code analysis requiring deep reasoning
- Integration with version control systems
- Tasks requiring specific non-Groq models

## See Also

- [opencode-agent](opencode.md) - Multi-model access
- [codex-agent](codex.md) - More capable code generation
- [/team](../commands/team.md) - Multi-agent coordination
