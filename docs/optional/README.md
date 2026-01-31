# Optional MCP Commands

These commands require external MCP (Model Context Protocol) servers. They extend the Toolkit with advanced task management and semantic search capabilities.

---

## Commander MCP Commands

Commander MCP provides enterprise-grade task management with real-time dashboards and agent coordination.

### /commander-task

Plan and execute a single task with full Commander tracking.

**Usage:**
```bash
/commander-task Implement user authentication with OAuth
```

**Features:**
- Uses planning agents for context gathering
- Creates tracked task in Commander dashboard
- Implements directly with progress logging
- Updates task status automatically

### /commander-plan

Break down an active plan into CodeRabbit-style microtasks using deep codebase analysis.

**Usage:**
```bash
/commander-plan Create payment processing module
```

**Features:**
- Analyzes codebase to understand structure
- Creates wave-based task groups
- Generates detailed task prompts
- Coordinates parallel agent execution

### /commander-execute

Execute pending tasks from Commander with intelligent orchestration.

**Usage:**
```bash
/commander-execute
```

**Features:**
- Dependency analysis and ordering
- Work type classification
- Execution guards and validation
- Automatic status updates

### Commander Setup

Add to your MCP configuration (`~/.claude/mcp.json`):

```json
{
  "mcpServers": {
    "commander": {
      "command": "node",
      "args": ["/path/to/commander-mcp/dist/server.js"],
      "env": {
        "COMMANDER_WS_URL": "ws://localhost:9002"
      }
    }
  }
}
```

---

## Photon MCP Commands

Photon MCP provides codebase indexing, semantic search, and persistent memory across sessions.

### /photon-compact

Compact session state to Photon memory for long-term persistence.

**Usage:**
```bash
/photon-compact
```

**Features:**
- Saves session context to Photon database
- Creates searchable memory entries
- Enables cross-session context retrieval
- More persistent than file-based compaction

### /photon-restore

Restore session from Photon snapshot with semantic search expansion.

**Usage:**
```bash
/photon-restore
```

**Features:**
- Retrieves session from Photon memory
- Supports semantic query expansion
- Restores task list and context
- Immediately continues work

### /photon-index

Index codebase for semantic search capabilities.

**Usage:**
```bash
/photon-index ./src
```

**Features:**
- Creates vector embeddings for code
- Enables semantic code search
- Supports pattern detection
- Powers analyze operations

### Photon Setup

Add to your MCP configuration (`~/.claude/mcp.json`):

```json
{
  "mcpServers": {
    "photon": {
      "command": "node",
      "args": ["/path/to/photon-mcp/dist/server.js"],
      "env": {
        "PHOTON_DB_URL": "postgresql://localhost:5432/photon",
        "PHOTON_PROJECT": "my-project"
      }
    }
  }
}
```

---

## Comparison

| Feature | Commander | Photon |
|---------|-----------|--------|
| Task Management | ✅ Full tracking | ❌ |
| Dashboard | ✅ Real-time | ❌ |
| Semantic Search | ❌ | ✅ Full |
| Code Indexing | ❌ | ✅ |
| Memory Persistence | Task-based | Semantic |
| Agent Coordination | ✅ Wave-based | ❌ |
| Session Compaction | ❌ | ✅ |

---

## When to Use Each

**Use Commander when:**
- Managing complex multi-agent workflows
- Need real-time progress dashboards
- Coordinating wave-based task execution
- Enterprise task tracking requirements

**Use Photon when:**
- Need semantic code search
- Want persistent memory across sessions
- Building knowledge base of project insights
- Analyzing large codebases with vector search

**Use Both when:**
- Full-featured enterprise development
- Complex projects with multiple agents
- Long-running development cycles
- Need both task tracking and semantic memory
