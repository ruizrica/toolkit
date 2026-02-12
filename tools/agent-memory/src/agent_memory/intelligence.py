# ABOUTME: Claude Agent SDK intelligence features — ask and summarize.
# ABOUTME: 100% optional; core search works without this module.

import glob
import sqlite3
from pathlib import Path

from .config import get_memory_dir
from .search import search_hybrid


def _build_context(conn: sqlite3.Connection, query: str) -> list[str]:
    """Search memories and return context strings for the LLM."""
    results = search_hybrid(conn, query, limit=10, min_score=0.1)
    return [r.text for r in results]


def _collect_daily_logs() -> list[str]:
    """Read recent daily log files and return their contents."""
    memory_dir = get_memory_dir()
    daily_dir = memory_dir / "daily-logs"
    pattern = str(daily_dir / "*.md")
    files = sorted(glob.glob(pattern), reverse=True)[:7]  # Last 7 days

    contents = []
    for f in files:
        text = Path(f).read_text(encoding="utf-8")
        if text.strip():
            contents.append(text)
    return contents


def ask_memories(question: str) -> None:
    """Ask a question about memories using Claude Agent SDK."""
    try:
        import anthropic
    except ImportError:
        raise ImportError(
            "Install claude-agent-sdk for intelligence features: "
            "pip install agent-memory[intelligence]"
        )

    from .config import get_db_path
    from .db import init_db

    conn = init_db(get_db_path())
    context = _build_context(conn, question)
    conn.close()

    if not context:
        print("No relevant memories found.")
        return

    context_text = "\n\n---\n\n".join(context)
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Based on the following memory context, answer this question: {question}\n\n"
                    f"Context:\n{context_text}"
                ),
            }
        ],
    )
    print(response.content[0].text)


def summarize_daily_logs() -> None:
    """Summarize recent daily logs using Claude Agent SDK."""
    try:
        import anthropic
    except ImportError:
        raise ImportError(
            "Install claude-agent-sdk for intelligence features: "
            "pip install agent-memory[intelligence]"
        )

    logs = _collect_daily_logs()
    if not logs:
        print("No daily logs found to summarize.")
        return

    combined = "\n\n---\n\n".join(logs)
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": (
                    "Summarize the following daily log entries into concise, "
                    "well-organized notes suitable for a MEMORY.md file. "
                    "Group by topic, remove duplicates, keep only stable facts "
                    "and important decisions.\n\n"
                    f"Daily logs:\n{combined}"
                ),
            }
        ],
    )
    print(response.content[0].text)
