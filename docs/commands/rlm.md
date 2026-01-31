<p align="center">
  <img src="../../assets/rlm.png" alt="RLM" width="120">
</p>

# /rlm

Run a Recursive Language Model workflow for processing large documents that exceed context limits. This command chunks large files and analyzes them in parallel using sub-agents.

## Usage

```bash
/rlm context=<path> query=<question>
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `context` | Yes | Path to the large context file |
| `query` | Yes | What you want to know about the document |

## How It Works

### Architecture

```
┌─────────────────────────────────────┐
│        Root LLM (Orchestrator)      │
│  Manages workflow, synthesizes      │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│        Python REPL (rlm_repl.py)    │
│  Chunking, state, helper functions  │
└───────────────┬─────────────────────┘
                │
    ┌───────────┼───────────┐
    ▼           ▼           ▼
┌────────┐ ┌────────┐ ┌────────┐
│Haiku 1 │ │Haiku 2 │ │Haiku N │  ← Parallel analysis
└────────┘ └────────┘ └────────┘
```

### Step-by-Step Process

1. **Initialize** - Load the document into the REPL environment
2. **Scout** - Peek at the beginning and end to understand structure
3. **Chunk** - Split the document using semantic or character-based chunking
4. **Analyze** - Spawn Haiku agents to process chunks in parallel
5. **Synthesize** - Merge findings into a cohesive answer

## Examples

```bash
# Analyze a large contract
/rlm context=./large_contract.pdf query="What are the termination clauses?"

# Process a transcript
/rlm context=./meeting_transcript.txt query="What decisions were made?"

# Analyze a codebase dump
/rlm context=./codebase.txt query="How is authentication implemented?"
```

## Chunking Strategies

| Strategy | When to Use |
|----------|-------------|
| **Semantic** | Document has clear structure (headings, sections) |
| **Character** | Default fallback, size ~100k-200k chars |
| **Overlap** | When context between chunks is important |

## REPL Helper Functions

Available in the Python REPL environment:

| Function | Description |
|----------|-------------|
| `peek(start, end)` | View a slice of content |
| `grep(pattern, max_matches, window)` | Search with context |
| `chunk_indices(size, overlap)` | Get chunk boundaries |
| `write_chunks(out_dir, size, overlap)` | Write chunk files |
| `add_buffer(text)` | Store intermediate results |

## Sub-Agent Output Format

Each chunk analyzer returns structured JSON:

```json
{
  "chunk_id": "chunk_0001.txt",
  "relevant": [
    {
      "point": "Key finding",
      "evidence": "Quote from document",
      "confidence": "high"
    }
  ],
  "missing": ["What couldn't be determined"],
  "suggested_next_queries": ["Follow-up questions"],
  "answer_if_complete": null
}
```

## Guardrails

- **Never** paste large raw chunks into main chat
- Use REPL to locate exact excerpts
- Sub-agents cannot spawn other sub-agents
- Scratch files stored in `.claude/rlm_state/`

## File Support

| Format | Support |
|--------|---------|
| `.txt` | Full support |
| `.md` | Full support |
| `.pdf` | Converted to text |
| `.docx` | Converted to text |

## When to Use

- Documents exceeding context limits (>100k tokens)
- Legal documents requiring thorough analysis
- Meeting transcripts with specific queries
- Large codebases exported as text

## See Also

- [gemini-agent](../agents/gemini.md) - Alternative for large codebases (1M tokens)
