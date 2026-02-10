# just-bash

ABOUTME: Documentation for the just-bash skill - sandboxed bash execution for AI agents.
ABOUTME: Covers installation, usage, security model, and when to use it vs regular Bash.

## What is it?

A sandboxed bash interpreter from [Vercel Labs](https://github.com/vercel-labs/just-bash) that provides safe command execution with:
- **Read-only filesystem** via OverlayFS
- **No network access**
- **75+ built-in commands** (jq, xan, rg, awk, sed, grep, find, etc.)
- **In-memory writes** that never touch disk

## Installation

```bash
npm install -g just-bash
```

The toolkit installer handles this automatically.

## When to Use

| Use just-bash | Use regular Bash |
|---------------|-----------------|
| Exploring files safely | git operations |
| Data processing (CSV, JSON) | npm/pip/package managers |
| Testing shell scripts | Running dev servers |
| Bulk file analysis | Anything needing network |
| Untrusted input processing | Real filesystem writes |

## Quick Examples

```bash
# Safe file exploration
just-bash -c 'find . -name "*.ts" | wc -l'

# JSON processing
just-bash -c 'cat data.json | jq ".items[] | .name"'

# CSV analysis
just-bash -c 'xan frequency data.csv -s status'

# Test writes safely (in-memory only)
just-bash --allow-write -c 'echo test > /tmp/file && cat /tmp/file'

# Scope to a project
just-bash -c 'find . -type d | head -20' --root /path/to/project

# JSON output for parsing
just-bash --json -c 'echo hello'
```

## Skill File Location

Installed to `~/.claude/skills/just-bash.md` - Claude reads this to understand when and how to use the tool.

## Known Issues (v1.0.0)

- `yq` broken - "Dynamic require of process" error
- `sqlite3` broken - "DataView constructor" error
- `jq` older build - missing `-R` and `-s` flags
- No process substitution (`<()` syntax)

## Resources

- GitHub: https://github.com/vercel-labs/just-bash
- npm: https://www.npmjs.com/package/just-bash
