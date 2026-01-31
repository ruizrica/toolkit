<p align="center">
  <img src="../../assets/cursor.png" alt="Cursor" width="120">
</p>

# Cursor Agent

A specialized agent that interfaces with Cursor CLI to provide advanced code analysis and generation capabilities. Excels at leveraging Cursor's optimized default model for sophisticated code tasks with session continuity.

## When to Use

- Advanced code generation beyond simple templates
- Complex code analysis requiring deep understanding
- Multi-step reasoning tasks with context retention
- Session continuity for ongoing work
- Intelligent refactoring with pattern recognition
- Comprehensive code reviews with multiple aspects
- Git workflow integration

## Capabilities

- **Advanced Code Generation** - Sophisticated code creation using Cursor's models
- **Comprehensive Code Review** - Security, performance, and quality analysis
- **Intelligent Refactoring** - Smart code improvements following best practices
- **Session Management** - Resume and continue previous AI conversations
- **Git Integration** - Seamless workflow with version control
- **Test Generation** - Creating comprehensive test suites
- **Bug Fixing** - Identifying and resolving complex issues

## Invocation

```
Task tool with:
- subagent_type: "toolkit:cursor-agent"
- prompt: "Review the authentication module for security vulnerabilities"
```

## Examples

**Code Review:**
```
Prompt: "Review this code for security vulnerabilities, performance issues, code quality, best practices, and potential bugs"
```

**Refactoring:**
```
Prompt: "Refactor this code to follow SOLID principles, improve readability, optimize performance, and add proper error handling"
```

**Session Continuation:**
```
Prompt: "Continue working on the payment integration we discussed in the previous session"
```

## Command Patterns

### Basic Analysis
```bash
cursor-agent -p "analyze this codebase for security vulnerabilities"
```

### Session Management
```bash
# Resume latest conversation
cursor-agent resume

# List sessions
cursor-agent ls

# Continue specific session
cursor-agent --resume="session-id"
```

### Git Integration
```bash
# Generate commit message
git diff --staged | cursor-agent -p "Generate detailed commit message"

# Review PR
git diff main...feature-branch | cursor-agent -p "Review this PR"
```

## Key Operating Principles

1. **Always use the default model** - Never specify `-m` or `--model` flags
2. **Focus on prompt quality** - Craft clear, specific prompts
3. **Leverage session continuity** - Use for complex multi-step tasks
4. **Stream long operations** - Use `--stream` flag for real-time feedback
5. **Integrate with Git** - Use diff pipes for PR reviews and commits

## Requirements

- **Cursor CLI** - Auto-installed if missing: `curl https://cursor.com/install -fsS | bash`
- **Network Access** - Required for API calls

## When NOT to Use

- Simple file operations (use basic file tools)
- Quick searches (use grep or find)
- Offline work (requires network)
- Deterministic outputs (AI models are probabilistic)
- Real-time execution requirements

## See Also

- [gemini-agent](gemini.md) - Large context analysis
- [codex-agent](codex.md) - Code generation
- [/review](../commands/review.md) - Code review workflow
