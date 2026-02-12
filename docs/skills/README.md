# Skills Overview

ABOUTME: Overview documentation for toolkit skill files.
ABOUTME: Explains what skills are and lists all available skills.

Skills are reference files installed to `~/.claude/skills/` that teach Claude when and how to use specific CLI tools. Unlike commands (slash commands you invoke) or agents (subagent types), skills are passive knowledge that Claude draws on automatically when relevant.

## Available Skills

| Skill | CLI Tool | Description |
|-------|----------|-------------|
| [just-bash](just-bash.md) | `just-bash` | Sandboxed bash with 75+ commands, read-only FS, no network |
| [agent-memory](agent-memory.md) | `agent-memory` | Local hybrid search (vector + BM25) over all memory files |

## How Skills Work

1. The installer copies `.md` files from `plugins/toolkit/skills/` to `~/.claude/skills/`
2. Claude reads these files when it needs guidance on using the corresponding tool
3. Skills contain usage patterns, security notes, and workflow examples

## Installation

Skills are installed automatically by the toolkit installer. To install manually:

```bash
cp plugins/toolkit/skills/*.md ~/.claude/skills/
```
