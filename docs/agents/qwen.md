<p align="center">
  <img src="../../assets/qwen.png" alt="Qwen" width="120">
</p>

# Qwen Agent

A specialized agent that interfaces with qwen-code CLI to provide state-of-the-art agentic coding capabilities using Alibaba's Qwen3-Coder models. Excels at complex software engineering tasks that require multi-turn reasoning, tool usage, and environment interaction.

## When to Use

- Complex software engineering tasks requiring planning
- Large codebase analysis beyond simple file reading
- Multi-step workflows with environment interaction
- Intelligent refactoring with pattern recognition
- Automated git and GitHub operations
- Batch file operations and transformations
- Tasks requiring deep code understanding and reasoning
- Real-world SWE tasks (SWE-Bench style)

## Capabilities

- **Agentic Coding** - Multi-turn interactions with environments for real-world tasks
- **Large Codebase Understanding** - Analyzing code beyond traditional context limits (256K tokens, 1M with extrapolation)
- **Workflow Automation** - Automating git operations, PR handling, development tasks
- **Intelligent Refactoring** - Pattern recognition and dependency management
- **Architecture Analysis** - Deep understanding of system design and dependencies
- **File Operations** - Batch processing and intelligent file management
- **Tool Integration** - Seamless interaction with development environments

## Invocation

```
Task tool with:
- subagent_type: "toolkit:qwen-agent"
- prompt: "Analyze the architecture of this project and find optimization opportunities"
```

## Examples

**Architecture Analysis:**
```
Prompt: "Describe the main pieces of this system's architecture and how they interact"
```

**Workflow Automation:**
```
Prompt: "Analyze git commits from the last 7 days, grouped by feature, and create a changelog"
```

**Intelligent Refactoring:**
```
Prompt: "Refactor this legacy module to use dependency injection while maintaining backward compatibility"
```

## Command Patterns

### Architecture Analysis
```bash
qwen "Describe the main pieces of this system's architecture"
qwen "What are the key dependencies and how do they interact?"
```

### Intelligent Refactoring
```bash
qwen "Refactor this function to improve readability and performance"
qwen "Convert this class to use dependency injection"
```

### Git Workflow Automation
```bash
qwen "Analyze git commits from the last 7 days, grouped by feature"
qwen "Create a detailed changelog from recent commits"
qwen "Find all TODO comments and create GitHub issues for them"
```

### File Operations
```bash
qwen "Rename all test files to follow the *.test.ts pattern"
qwen "Find and remove all console.log statements from production code"
```

## Context Configuration

Create `QWEN.md` files in your project for context:

```markdown
# Project: My TypeScript Library

## Coding Standards
- Use TypeScript strict mode
- Follow functional programming patterns
- Comprehensive error handling required

## Architecture
- Service layer pattern
- Repository pattern for data access
```

Context files are hierarchical - directory-level inherits from parent.

## Available Tools

- **File System Tools** - Read, write, list, search files
- **Shell Tool** - Execute shell commands
- **Web Tools** - Fetch URLs and search the web
- **Memory Tool** - Persist information across sessions
- **Todo Tool** - Manage structured task lists
- **Multi-File Read** - Process multiple files simultaneously

## Requirements

- **qwen-code CLI** - Auto-installed: `npm install -g @qwen-code/qwen-code@latest`
- **Node.js 20+** - Required for CLI
- **API Key** - Alibaba Cloud or ModelScope credentials

## When NOT to Use

- Simple, single-file code generation
- Quick syntax fixes or simple completions
- Tasks not requiring advanced reasoning
- Operations where token usage must be minimal
- Real-time or latency-critical operations

## See Also

- [gemini-agent](gemini.md) - Alternative for large context
- [droid-agent](droid.md) - Enterprise workflows
- [/team](../commands/team.md) - Multi-agent coordination
