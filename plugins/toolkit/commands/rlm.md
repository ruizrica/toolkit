---
description: "Run a Recursive Language Model workflow for processing large documents that exceed context limits"
argument-hint: "[context=<path> query=<question>]"
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, Task
---

# RLM (Recursive Language Model Workflow)

Use this command when processing very large context files (docs, logs, transcripts, codebases) that won't fit in chat context.

## Architecture

- **Root LLM (You)**: Orchestrate the workflow, synthesize results
- **Python REPL** (`rlm_repl.py`): External environment for chunking and state
- **Sub-LLM** (`rlm-subcall` agent): Haiku-powered chunk analysis

## Inputs

Parse `$ARGUMENTS` for:
- `context=<path>` (required): path to the large context file
- `query=<question>` (required): what the user wants to know

If arguments are missing, ask the user for:
1. The context file path
2. Their query/question

## Step-by-Step Procedure

### 1. Initialize the REPL

```bash
python3 ~/.claude/plugins/cache/toolkit/toolkit/scripts/rlm_repl.py init <context_path>
python3 ~/.claude/plugins/cache/toolkit/toolkit/scripts/rlm_repl.py status
```

### 2. Scout the Context

```bash
python3 ~/.claude/plugins/cache/toolkit/toolkit/scripts/rlm_repl.py exec -c "print(peek(0, 3000))"
python3 ~/.claude/plugins/cache/toolkit/toolkit/scripts/rlm_repl.py exec -c "print(peek(len(content)-3000, len(content)))"
```

### 3. Choose a Chunking Strategy

- **Semantic chunking**: If format is clear (markdown headings, JSON, log timestamps)
- **Character chunking**: Default fallback (size ~100000-200000 chars, optional overlap)

### 4. Materialize Chunks

```bash
python3 ~/.claude/plugins/cache/toolkit/toolkit/scripts/rlm_repl.py exec <<'PY'
paths = write_chunks('.claude/rlm_state/chunks', size=150000, overlap=500)
print(f"Created {len(paths)} chunks")
print(paths)
PY
```

### 5. Sub-call Loop (Delegate to rlm-subcall)

For each chunk file, spawn the `rlm-subcall` agent:

```
Task tool with:
- subagent_type: "toolkit:rlm-subcall"
- model: haiku
- prompt: Include the query and chunk file path
```

**IMPORTANT**: Spawn multiple agents in parallel when possible for efficiency.

Example prompt for subcall:
```
Query: [user's question]
Chunk file: [chunk path]

Read the chunk and extract information relevant to the query. Return JSON only.
```

### 6. Synthesis

Once all chunks are analyzed:
1. Collect all subagent results
2. Merge findings, resolving conflicts
3. Synthesize final answer in main conversation
4. Quote specific evidence where needed

## Helper Functions Available in REPL

- `peek(start=0, end=1000)` - View a slice of content
- `grep(pattern, max_matches=20, window=120)` - Search with context
- `chunk_indices(size=200000, overlap=0)` - Get chunk boundaries
- `write_chunks(out_dir, size, overlap)` - Write chunk files
- `add_buffer(text)` - Store intermediate results

## Guardrails

- **Never** paste large raw chunks into main chat
- Use REPL to locate exact excerpts; quote only what's needed
- Subagents cannot spawn other subagents
- Keep scratch files under `.claude/rlm_state/`

## Example Workflow

```
User: /rlm context=./large_contract.pdf query="What are the termination clauses?"

You:
1. Initialize REPL with the file
2. Peek at structure to understand format
3. Create ~5 chunks of 150k chars each
4. Spawn 5 rlm-subcall agents IN PARALLEL
5. Collect JSON results from each
6. Synthesize: "The contract contains 3 termination clauses..."
```
