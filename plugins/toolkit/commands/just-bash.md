---
description: "Run commands in a sandboxed bash environment (read-only FS, no network)"
argument-hint: "[bash command or task description to run safely in sandbox]"
allowed-tools: ["Bash", "Read", "Glob", "Grep"]
---

# Just Bash - Sandboxed Execution

Run the user's command or task inside the `just-bash` sandbox. This provides a read-only filesystem, no network access, and in-memory-only writes.

## User's Request

$ARGUMENTS

## How to Execute

Translate the user's request into one or more `just-bash` commands and run them via the Bash tool.

### Command Format

```bash
# Simple command
just-bash -c 'COMMAND' --root /path/to/project

# Multi-line script
just-bash -c '
COMMAND1
COMMAND2
' --root /path/to/project

# When writes are needed (in-memory only, nothing touches disk)
just-bash --allow-write -c 'COMMAND' --root /path/to/project

# JSON output for structured results
just-bash --json -c 'COMMAND' --root /path/to/project
```

### Key Options

- `--root <path>` - Mount a specific directory (default: cwd). Always set this to the project root.
- `--allow-write` - Enable in-memory writes (safe, nothing reaches disk)
- `--json` - Output as JSON: `{"stdout", "stderr", "exitCode"}`
- `-e, --errexit` - Exit on first error
- `--python` - Enable python3

## Available Tools

### Reliable (tested, working)
- **Text**: `awk` `sed` `grep` `egrep` `fgrep` `rg` `cut` `tr` `sort` `uniq` `wc` `head` `tail` `tac` `rev` `nl` `fold` `column` `comm` `join` `paste` `split` `strings`
- **Data**: `jq` (JSON - older build, no `-R`/`-s` flags) `xan` (CSV)
- **Files**: `ls` `find` `cat` `cp` `mv` `rm` `mkdir` `rmdir` `ln` `touch` `chmod` `stat` `file` `tree` `du` `basename` `dirname` `readlink`
- **Compression**: `gzip` `gunzip` `zcat` `tar`
- **Checksums**: `md5sum` `sha1sum` `sha256sum` `base64`
- **Utilities**: `date` `seq` `expr` `env` `printenv` `whoami` `hostname` `sleep` `timeout` `time` `which` `xargs` `tee` `diff`

### Broken in v1.0.0 (do NOT use)
- `yq` - "Dynamic require of process" error
- `sqlite3` - "DataView constructor" error

### Limitations
- No network (no curl, wget, npm, git, pip)
- No process substitution (`<()` syntax)
- `jq` missing `-R` (raw input) and `-s` (slurp) flags
- `tree` missing some flags (e.g. `--dirsfirst`)
- No interactive commands (no vim, nano, less)

## Execution Rules

1. **Always use `--root`** to scope to the correct project directory
2. If the user gives a natural language task, translate it to bash commands
3. If a command fails, try an alternative approach using available tools
4. For multi-step tasks, chain commands in a single `just-bash -c '...'` call
5. Present results clearly to the user
6. Do NOT use `yq` or `sqlite3` - they are broken in v1.0.0
