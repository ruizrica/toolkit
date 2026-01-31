# Toolkit

A marketplace of Claude Code plugins featuring multi-agent orchestration, TDD workflows, and advanced productivity commands.

## Plugins

| Plugin | Description |
|--------|-------------|
| **[toolkit](plugins/toolkit/)** | Complete power-user configuration with 8 specialized agents, 6 core commands, and 7 optional MCP commands |

## Features

- **8 Specialized Agents** - Leverage different AI models and tools for specific tasks
- **6 Core Commands** - Productivity workflows for common development tasks
- **7 Optional MCP Commands** - Advanced orchestration requiring external MCP servers
- **TDD-First Philosophy** - Global instructions emphasizing test-driven development
- **Context Fork Support** - All commands use Claude Code 2.1's isolated context feature

## Quick Start

### Installation

```bash
# Clone this marketplace
git clone https://github.com/ruizrica/toolkit.git

# Install the toolkit plugin
claude plugins add ./toolkit/plugins/toolkit
```

### Setup Scripts (Required for /handbook and /review)

The `/handbook` and `/review` commands require Python scripts:

```bash
# Copy scripts to your Claude slash_commands directory
mkdir -p ~/.claude/slash_commands
cp plugins/toolkit/scripts/handbook.py ~/.claude/slash_commands/
cp plugins/toolkit/scripts/coderabbit_workflow.py ~/.claude/slash_commands/
```

---

## Commands Reference

### Core Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `/team` | Coordinate multi-agent team for parallel feature implementation | `/team [feature description]` |
| `/review` | CodeRabbit review + parallel fixes + verification | `/review [--base main] [--type all]` |
| `/handbook` | Generate comprehensive project handbook | `/handbook [--path .] [--output HANDBOOK.md]` |
| `/@implement` | Process @implement comments into documentation | `/@implement [file or directory]` |
| `/save` | Git: stage, commit, rebase, merge | `/save` |
| `/stable` | Create stable checkpoint with tags/branches | `/stable [checkpoint name]` |

### Optional MCP Commands

These commands require external MCP servers (Commander, Photon):

| Command | Description | Requires |
|---------|-------------|----------|
| `/commander-task` | Plan and execute single task with full tracking | Commander MCP |
| `/commander-plan` | Break down features into CodeRabbit-style microtasks | Commander MCP |
| `/commander-execute` | Execute pending tasks with intelligent orchestration | Commander MCP |
| `/photon-compact` | Compact session state before context limits | Photon MCP |
| `/photon-restore` | Restore session from Photon snapshot | Photon MCP |
| `/photon-index` | Index codebase for semantic search | Photon MCP |
| `/haiku` | Spawn team of Haiku agents managed by Opus | - |

---

## Agents Reference

### Available Agents

| Agent | Specialty | Best For |
|-------|-----------|----------|
| **gemini-agent** | Large codebase analysis (1M tokens), Google Search | Monorepos >100KB, security audits, architecture docs |
| **cursor-agent** | Advanced code review, refactoring, sessions | Complex refactoring, intelligent code analysis |
| **codex-agent** | Natural language → code, multi-language | Code generation, bug fixing, code translation |
| **qwen-agent** | Agentic coding, workflow automation | Large codebase understanding, git automation |
| **opencode-agent** | 75+ AI models via OpenRouter | Model comparison, cost optimization |
| **groq-agent** | Fast inference, lightweight tasks | Quick code completions, rapid iteration |
| **crush-agent** | Media compression/optimization | Image/video optimization, compression quality |
| **droid-agent** | Enterprise code generation | Architecture analysis, enterprise workflows |

### Using Agents

Agents are invoked via the Task tool:

```
Use Task tool with:
- subagent_type: "gemini-agent"
- prompt: "Analyze the authentication module..."
```

Or reference in commands for automatic selection based on task type.

---

## Command Details

### /team - Multi-Agent Coordination

Spawns multiple agents to work on a feature in parallel:

```bash
/team Implement user authentication with OAuth support
```

**Workflow:**
1. Parses feature requirements
2. Creates parallel agent tasks
3. Coordinates implementation across agents
4. Synthesizes results

### /review - CodeRabbit Review Workflow

Orchestrates complete code review and fix workflow:

```bash
/review --base main --type committed
```

**Options:**
- `--base <branch>` - Branch to compare against (default: main)
- `--type <all|committed|uncommitted>` - What to review
- `--verify-only` - Run verification without fixes

**Workflow:**
1. Run CodeRabbit review
2. Parse review comments
3. Create parallel fix tasks
4. Apply fixes concurrently
5. Verify all issues resolved
6. Commit changes

### /handbook - Project Documentation

Generates comprehensive AI-optimized project handbook:

```bash
/handbook --path ./my-project --output HANDBOOK.md
```

**Options:**
- `--path <path>` - Project path (default: current directory)
- `--output <file>` - Output filename
- `--verbose` - Show detailed progress

**Output Structure:**
- Layer 1: System Overview (Purpose, Tech Stack, Architecture)
- Layer 2: Module Map (Core Modules, Data Layer, Utilities)
- Layer 3: Integration Guide (APIs, Interfaces, Configuration)
- Layer 4: Extension Points (Design Patterns, Customization Areas)

### /@implement - Code Comment Processing

Processes @implement directives in code files:

```bash
/@implement src/utils/
```

**Before:**
```typescript
// @implement: Add email validation function
```

**After:**
```typescript
/**
 * Validates email format using RFC 5322 standard
 * @param email - Email address to validate
 * @returns true if valid format
 */
function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}
```

### /save - Git Workflow

Streamlined git workflow command:

```bash
/save
```

**Actions:**
1. Stage all changes
2. Generate descriptive commit message
3. Rebase from main branch
4. Merge to main

### /stable - Checkpoint Creation

Creates stable checkpoint with documentation:

```bash
/stable v1.0-auth-complete
```

**Creates:**
- Git tag with annotation
- Feature branch backup
- Checkpoint documentation

---

## Context Fork

All commands use `context: fork` (Claude Code 2.1 feature) which:

- Runs commands in **isolated sub-agent context**
- Keeps main conversation **clean and uncluttered**
- Returns only **final results** to main thread
- Uses **general-purpose** agent type for broad capabilities

---

## CLAUDE.md Philosophy

The included `CLAUDE.md` establishes:

### Core Principles
- Pragmatic, simplicity-first approach
- Smallest changes to achieve goals
- Never rewrite without permission
- TDD for all development

### Code Standards
- ABOUTME comments in all files
- Match existing code style
- No over-engineering
- Root cause debugging only

### Testing Requirements
- Write failing tests first
- Unit, integration, AND E2E tests
- Never mock in E2E tests
- Test output must be pristine

---

## Directory Structure

```
toolkit/
├── .claude-plugin/
│   └── marketplace.json      # Marketplace manifest
├── plugins/
│   └── toolkit/              # Main plugin
│       ├── plugin.json       # Plugin metadata
│       ├── agents/           # 8 specialized agents
│       │   ├── gemini-agent.md
│       │   ├── cursor-agent.md
│       │   ├── codex-agent.md
│       │   ├── qwen-agent.md
│       │   ├── opencode-agent.md
│       │   ├── groq-agent.md
│       │   ├── crush-agent.md
│       │   └── droid-agent.md
│       ├── commands/         # 6 core commands
│       │   ├── team.md
│       │   ├── review.md
│       │   ├── handbook.md
│       │   ├── @implement.md
│       │   ├── save.md
│       │   └── stable.md
│       ├── scripts/          # Python scripts for commands
│       │   ├── handbook.py
│       │   └── coderabbit_workflow.py
│       └── optional/         # MCP-dependent commands
│           ├── commander-task.md
│           ├── commander-plan.md
│           ├── commander-execute.md
│           ├── photon-compact.md
│           ├── photon-restore.md
│           ├── photon-index.md
│           └── haiku.md
├── CLAUDE.md                 # Global instructions template
├── README.md                 # This documentation
├── README.html               # HTML version
└── LICENSE                   # MIT license
```

---

## Requirements

### Core Commands
- Claude Code 2.1+
- Python 3.8+ (for /handbook and /review scripts)

### Optional MCP Commands
- **Commander MCP** - Task orchestration server
- **Photon MCP** - Memory and semantic search server

---

## Customization

### Modifying Commands

Edit markdown files in `commands/` directory. Command frontmatter format:

```yaml
---
description: "What the command does"
argument-hint: "[arguments format]"
allowed-tools: ["Tool1", "Tool2"]
context: fork
agent: general-purpose
---
```

### Adding Agents

Create new `.md` files in `agents/` directory. Agent format:

```yaml
---
name: my-agent
description: What this agent specializes in
model: claude-sonnet-4-5
---

# Agent Name

System prompt and instructions...
```

### Updating CLAUDE.md

Modify `CLAUDE.md` to match your team's conventions and workflows.

---

## License

MIT License - See [LICENSE](LICENSE) file.

---

## Credits

Created by Ricardo for productive Claude Code development workflows.
