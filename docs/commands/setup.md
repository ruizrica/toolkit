# /setup

Bootstrap command for project initialization and memory-first context setup.

## Usage

```bash
/setup
```

## What it does

1. Validates that the current directory is inside a git repository.
2. Checks for `agent-memory` in `PATH` and fails fast with a clear message if missing.
3. Runs `agent-memory index` over the repository.
4. Creates project context files if missing:
   - `claude.md`
   - `agents.md` (reference only, no duplicated context content)
5. Prints a compact post-setup summary and next `/worktree` usage steps.

## Idempotent behavior

- If `claude.md` already exists, the command skips re-writing it.
- If `agents.md` already exists, the command skips re-writing it.
- Re-running `/setup` is safe and should not overwrite existing files.

## Constraints satisfied

- Memory tool primacy is explicitly documented in generated `claude.md`.
- `agent-memory` is required and checked before any file generation.
- Both `claude.md` and `agents.md` are created only when absent.
- Git repository validation runs before any operations.

## Generated `claude.md` includes

- Primary context guidance: use memory lookup before file reads.
- Memory query guidance using commands such as `agent-memory query`, `agent-memory recall`, and related variants.
- Stack and structure notes for this repository.
- Coding conventions and architectural notes.

## Generated `agents.md` format

`agents.md` is intentionally minimal and references the context file only:

```markdown
# Agent Configuration

See [claude.md](./claude.md) for project context, coding standards, and memory tool usage guidelines.

## Memory Tool Usage
This project uses the agent-memory CLI. Refer to claude.md for detailed instructions on context retrieval.
```

## Example output

```text
Running agent-memory index ...
agent-memory index complete.

Setup summary:
- agent-memory index: done
- claude context file: created (./claude.md)
- agents file: created (./agents.md)

Next steps:
1) Run /worktree to create your first isolated worktree (auto-generates branch)
2) Run /worktree again for additional worktrees, or use /worktree [path] [branch] for custom names
```

## See Also

- [/worktree](worktree.md) - create isolated worktrees
- [/save](save.md) - commit, merge, and cleanup workflows
