<p align="center">
  <img src="../../assets/rlm.png" alt="RLM Subcall" width="120">
</p>

# RLM Subcall Agent

A sub-LLM used inside Recursive Language Model (RLM) loops. Analyzes document chunks and extracts query-relevant information as structured JSON. This agent is typically invoked by the `/rlm` command, not directly.

## When to Use

This agent is automatically invoked by the `/rlm` command. Direct use is typically for:

- Processing individual chunks of large documents
- Extracting specific information from text segments
- Parallel analysis of document sections
- Custom RLM-style workflows

## Capabilities

- **Chunk Analysis** - Process individual document segments
- **Information Extraction** - Extract query-relevant data
- **Structured Output** - Return findings as JSON
- **Confidence Assessment** - Rate certainty of findings
- **Gap Identification** - Note what's missing from the chunk

## Invocation

```
Task tool with:
- subagent_type: "toolkit:rlm-subcall"
- model: haiku
- prompt: "Query: What are the termination clauses?\nChunk file: .claude/rlm_state/chunks/chunk_0001.txt"
```

## Input Format

The agent receives:
- A user query to answer
- Either a file path to a chunk or raw chunk text

## Output Format

Returns JSON only with this schema:

```json
{
  "chunk_id": "chunk_0001.txt",
  "relevant": [
    {
      "point": "Key finding or fact",
      "evidence": "Short quote with approximate location",
      "confidence": "high|medium|low"
    }
  ],
  "missing": ["What couldn't be determined from this chunk"],
  "suggested_next_queries": ["Optional sub-questions for other chunks"],
  "answer_if_complete": "If this chunk alone answers the query, put answer here, otherwise null"
}
```

## Example Response

```json
{
  "chunk_id": "chunk_0002.txt",
  "relevant": [
    {
      "point": "Payment due within 30 days",
      "evidence": "Section 4.2: 'All invoices shall be paid within thirty (30) days'",
      "confidence": "high"
    },
    {
      "point": "Late payment penalty of 1.5%",
      "evidence": "Section 4.3 mentions '1.5% monthly interest on overdue amounts'",
      "confidence": "high"
    }
  ],
  "missing": ["Payment methods not specified in this chunk"],
  "suggested_next_queries": ["What payment methods are accepted?"],
  "answer_if_complete": null
}
```

## Processing Rules

1. **Do not speculate** beyond what's in the chunk
2. **Keep evidence short** - Aim for <25 words per evidence field
3. **If given a file path** - Read it with the Read tool first
4. **If chunk is irrelevant** - Return empty `relevant` list
5. **Be precise** - Include line numbers or section names when visible
6. **Stay focused** - Only extract what relates to the query

## Confidence Levels

| Level | When to Use |
|-------|-------------|
| high | Direct quote or explicit statement |
| medium | Clear implication from context |
| low | Inference or partial information |

## Integration with /rlm

The `/rlm` command:
1. Chunks the large document
2. Spawns multiple rlm-subcall agents in parallel
3. Collects all JSON responses
4. Synthesizes findings into a final answer

## Limitations

- Cannot spawn other agents
- Limited to analyzing the provided chunk
- Must return JSON only (no additional text)
- Designed for Haiku model (cost-effective)

## Requirements

- **Read tool access** - For reading chunk files
- **Haiku model** - Optimized for this model

## See Also

- [/rlm](../commands/rlm.md) - The parent RLM workflow
- [gemini-agent](gemini.md) - Alternative for large documents (1M tokens)
