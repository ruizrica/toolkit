# Commands Overview

The Toolkit provides 14 commands organized into three categories: Core Commands for development workflows, Session Management for context preservation, and Git Workflow for version control.

## Quick Reference

| Command | Description | Category |
|---------|-------------|----------|
| [/team](team.md) | Multi-agent parallel implementation | Core |
| [/haiku](haiku.md) | 10 Haiku agents managed by Opus | Core |
| [/review](review.md) | CodeRabbit review + parallel fixes | Core |
| [/handbook](handbook.md) | Generate AI-optimized project docs | Core |
| [/@implement](implement.md) | Process @implement comments | Core |
| [/rlm](rlm.md) | Large document processing | Core |
| [/gherkin](gherkin.md) | Extract business rules to Gherkin | Core |
| [/kiro](kiro.md) | Spec-driven development with Kiro methodology | Core |
| [/compact](compact.md) | Memory-aware session compact (daily log + state) | Session |
| [/compact-min](compact.md#compact-min) | Ultra-minimal session compact (fast, no memory) | Session |
| [/restore](restore.md) | Restore session with daily log bootstrap | Session |
| [/setup](setup.md) | Create WIP branch and worktree | Git |
| [/save](save.md) | Commit, merge, cleanup worktree | Git |
| [/stable](stable.md) | Create stable checkpoint | Git |

---

## Core Commands

Commands for feature development, code review, and documentation.

### Multi-Agent Coordination

- **[/team](team.md)** - Coordinate multiple specialized agents to implement features in parallel. Automatically decomposes tasks and assigns to appropriate agents.

- **[/haiku](haiku.md)** - Spawn a team of 10 Haiku agents orchestrated by Opus. Uses a phased approach: context gathering → implementation → validation.

### Code Review

- **[/review](review.md)** - Run CodeRabbit review, parse comments, create parallel fix tasks, and verify all issues are resolved.

### Documentation

- **[/handbook](handbook.md)** - Generate comprehensive project handbook with four layers: System Overview, Module Map, Integration Guide, and Extension Points.

- **[/@implement](implement.md)** - Find @implement comments in code and convert them to proper documentation while implementing the requested functionality.

### Large Document Processing

- **[/rlm](rlm.md)** - Recursive Language Model workflow for processing documents that exceed context limits. Chunks documents and analyzes them in parallel.

### Specification

- **[/gherkin](gherkin.md)** - Extract business rules from code into living Gherkin documentation. Supports both code analysis and visual analysis via browser.

### Spec-Driven Development

- **[/kiro](kiro.md)** - Spec-driven development using the Kiro methodology. Generates EARS-format requirements, design documents, and task breakdowns through interactive Q&A phases, then executes with parallel agents (Cursor or Haiku).

---

## Session Management

Commands for preserving context across `/clear` operations.

- **[/compact](compact.md)** - Memory-aware session compact. Writes a daily log entry to `~/.claude/agent-memory/daily-logs/`, saves session state to `.plans/session-state.json`, and optionally updates MEMORY.md with stable facts discovered during the session.

- **[/compact-min](compact.md#compact-min)** - Ultra-minimal session compact. Writes only `.plans/session-state.json` with no memory system writes. Faster when you just need a quick checkpoint.

- **[/restore](restore.md)** - Restore session from saved state and immediately continue working. Bootstraps context from today's and yesterday's daily logs. Supports multiple schema versions.

**Workflow:**
```bash
/compact      # Save state + write daily log
/clear        # Clear context
/restore      # Resume with daily log context
```

For a faster checkpoint without memory writes:
```bash
/compact-min  # Save state only
```

---

## Git Workflow

Commands for isolated development using git worktrees.

- **[/setup](setup.md)** - Create a WIP branch and worktree for isolated development. The worktree is created in `.specbook/worktrees/` within the project directory.

- **[/save](save.md)** - Commit all changes, merge WIP branch to main, and cleanup the worktree and branch. Handles merge conflicts interactively.

- **[/stable](stable.md)** - Create a stable checkpoint with an annotated tag, checkpoint branch, and comprehensive documentation.

**Workflow:**
```bash
/setup      # Create isolated worktree
# ... develop feature ...
/save       # Merge back to main
/stable     # Optional: create checkpoint
```

---

## Optional Commands

Some commands require external MCP servers. See [Optional Commands](../optional/README.md) for:

- **Commander MCP**: `/commander-task`, `/commander-plan`, `/commander-execute`
- **Photon MCP**: `/photon-compact`, `/photon-restore`, `/photon-index`
