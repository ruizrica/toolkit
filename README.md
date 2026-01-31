<p align="center">
  <img src="toolkit.png" alt="Toolkit" width="400">
</p>

<p align="center">
  <strong>A Claude Code plugin with multi-agent orchestration, TDD workflows, and advanced productivity commands.</strong>
</p>

---

## Installation

```bash
# Clone this repository
git clone https://github.com/ruizrica/toolkit.git

# Install the toolkit plugin
claude plugins add ./toolkit/plugins/toolkit
```

### Setup Scripts (Required for /handbook and /review)

```bash
mkdir -p ~/.claude/slash_commands
cp plugins/toolkit/scripts/handbook.py ~/.claude/slash_commands/
cp plugins/toolkit/scripts/coderabbit_workflow.py ~/.claude/slash_commands/
```

---

## Commands (12)

### Core Commands

| Command | Description |
|---------|-------------|
| `/team` | Coordinate multi-agent team for parallel feature implementation |
| `/review` | CodeRabbit review + parallel fixes + verification |
| `/handbook` | Generate comprehensive AI-optimized project handbook |
| `/@implement` | Process @implement comments in code into documentation |
| `/haiku` | Spawn team of 10 Haiku agents managed by Opus |
| `/rlm` | Recursive Language Model workflow for large documents |
| `/gherkin` | Extract business rules from code into Gherkin specs |

### Session Management

| Command | Description |
|---------|-------------|
| `/compact` | Save minimal session state before `/clear` |
| `/restore` | Restore session from `.plans/session-state.json` |

### Git Workflow

| Command | Description |
|---------|-------------|
| `/setup` | Create WIP branch and worktree for isolated development |
| `/save` | Commit changes, merge WIP to main, cleanup worktree |
| `/stable` | Create stable checkpoint with tags and documentation |

---

## Optional MCP Commands (6)

These commands require external MCP servers (Commander or Photon):

### Commander MCP

| Command | Description |
|---------|-------------|
| `/commander-task` | Plan and execute single task with full tracking |
| `/commander-plan` | Break down features into CodeRabbit-style microtasks |
| `/commander-execute` | Execute pending tasks with intelligent orchestration |

### Photon MCP

| Command | Description |
|---------|-------------|
| `/photon-compact` | Compact session state to Photon memory |
| `/photon-restore` | Restore session from Photon snapshot |
| `/photon-index` | Index codebase for semantic search |

---

## Agents (9)

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
| **rlm-subcall** | Chunk analysis for RLM workflow | Processing large documents in chunks |

### Using Agents

Agents are invoked via the Task tool:

```
Task tool with:
- subagent_type: "toolkit:gemini-agent"
- prompt: "Analyze the authentication module..."
```

---

## Command Details

### /team - Multi-Agent Coordination

Spawns multiple specialized agents to work on a feature in parallel:

```bash
/team Implement user authentication with OAuth support
```

**Workflow:**
1. Analyzes task and breaks into parallel work streams
2. Spawns relevant agents (gemini, cursor, codex, qwen, etc.)
3. Coordinates implementation across agents
4. Synthesizes results

### /haiku - Haiku Team

Orchestrates a team of 10 Haiku agents managed by Opus:

```bash
/haiku Analyze and document all API endpoints
```

**Team Structure:**
- 1 Opus orchestrator
- 4 Context Haiku agents (parallel context gathering)
- 4 Implementation Haiku agents (parallel execution)
- 2 Validator Haiku agents (verification)

### /review - CodeRabbit Review Workflow

Orchestrates complete code review and fix workflow:

```bash
/review --base main --type committed
```

**Options:**
- `--base <branch>` - Branch to compare against (default: main)
- `--type <all|committed|uncommitted>` - What to review

**Workflow:**
1. Run CodeRabbit review
2. Parse review comments
3. Create parallel fix tasks
4. Apply fixes concurrently
5. Verify all issues resolved

### /gherkin - Business Logic Capture

Extract business rules from code into living Gherkin documentation:

```bash
/gherkin ./src/pages                              # Code analysis only
/gherkin ./src --url http://localhost:3000        # Code + visual analysis
/gherkin validate ./src --against .specs/auth.feature  # Validate implementation
```

**Features:**
- Parallel Haiku agents analyze pages, components, APIs, and UI
- Generates `.specs/` folder with feature files
- Supports validation mode to check code against specs
- Uses `agent-browser` for visual analysis (auto-installed if needed)

### /rlm - Recursive Language Model

Process very large documents that exceed context limits:

```bash
/rlm context=./large_contract.pdf query="What are the termination clauses?"
```

**Architecture:**
- Root LLM orchestrates the workflow
- Python REPL handles chunking and state
- Sub-LLM (Haiku) analyzes chunks in parallel
- Results synthesized into final answer

### /handbook - Project Documentation

Generates comprehensive AI-optimized project handbook:

```bash
/handbook --path ./my-project --output HANDBOOK.md
```

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

### /setup + /save - Git Worktree Workflow

Isolated development using git worktrees:

```bash
/setup   # Creates wip-YYYYMMDD-HHMMSS branch and ../project-wip worktree
# ... do your work ...
/save    # Commits, merges to main, cleans up worktree and branch
```

**Benefits:**
- Keep main branch clean
- Isolated development environment
- Automatic cleanup on merge

### /compact + /restore - Session Management

Save and restore session state across `/clear`:

```bash
/compact  # Before /clear - saves state to .plans/session-state.json
/clear    # Clear context
/restore  # Resume seamlessly - immediately continues work
```

### /stable - Checkpoint Creation

Creates stable checkpoint with documentation:

```bash
/stable v1.0-auth-complete
```

**Creates:**
- Annotated git tag: `stable-YYYYMMDD-HHMMSS`
- Checkpoint branch
- Checkpoint documentation

---

## Directory Structure

```
toolkit/
├── .claude-plugin/
│   └── marketplace.json      # Marketplace manifest
├── plugins/
│   └── toolkit/              # Main plugin
│       ├── .claude-plugin/
│       │   └── plugin.json   # Plugin metadata
│       ├── agents/           # 9 specialized agents
│       │   ├── gemini-agent.md
│       │   ├── cursor-agent.md
│       │   ├── codex-agent.md
│       │   ├── qwen-agent.md
│       │   ├── opencode-agent.md
│       │   ├── groq-agent.md
│       │   ├── crush-agent.md
│       │   ├── droid-agent.md
│       │   └── rlm-subcall.md
│       ├── commands/         # 12 commands
│       │   ├── team.md
│       │   ├── review.md
│       │   ├── handbook.md
│       │   ├── @implement.md
│       │   ├── setup.md
│       │   ├── save.md
│       │   ├── stable.md
│       │   ├── haiku.md
│       │   ├── rlm.md
│       │   ├── compact.md
│       │   ├── restore.md
│       │   └── gherkin.md
│       ├── scripts/          # Python scripts
│       │   ├── handbook.py
│       │   ├── coderabbit_workflow.py
│       │   └── rlm_repl.py
│       └── optional/         # MCP-dependent commands
│           ├── commander-task.md
│           ├── commander-plan.md
│           ├── commander-execute.md
│           ├── photon-compact.md
│           ├── photon-restore.md
│           └── photon-index.md
├── CLAUDE.md                 # Global instructions template
├── toolkit.png               # Logo
└── LICENSE                   # MIT license
```

---

## Requirements

### Core Commands
- Claude Code 2.1+
- Python 3.8+ (for /handbook, /review, /rlm scripts)

### Optional
- **agent-browser** - For /gherkin visual analysis (`npm install -g agent-browser`)
- **Commander MCP** - For task orchestration commands
- **Photon MCP** - For memory and semantic search commands

---

## License

MIT License - See [LICENSE](LICENSE) file.
