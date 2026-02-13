# ABOUTME: Tests for summarizer module — bottom-up code summary generation.
# ABOUTME: Verifies fallback summaries, summary storage, and CLI command.

import pytest
from pathlib import Path
from types import SimpleNamespace


@pytest.fixture
def summarizer_db(tmp_path):
    """Provide a DB with indexed code nodes for summarizer tests."""
    from agent_memory.db import init_db
    from agent_memory.parser import CodeNode
    from agent_memory.tree import store_nodes

    db_path = tmp_path / "summarizer_test.db"
    conn = init_db(db_path)

    method = CodeNode(
        name="add", qualified_name="Calculator.add", node_type="function",
        file_path="calc.py", start_line=4, end_line=6,
        signature="def add(self, a, b)", docstring="Add two numbers.",
        body_hash="h1",
    )
    cls = CodeNode(
        name="Calculator", qualified_name="Calculator", node_type="class",
        file_path="calc.py", start_line=1, end_line=10,
        signature="class Calculator", docstring="A simple calculator.",
        body_hash="h2",
        children=[method],
    )
    func = CodeNode(
        name="read_file", qualified_name="read_file", node_type="function",
        file_path="utils.py", start_line=1, end_line=3,
        signature="def read_file(path: str) -> str",
        docstring="Read a file and return contents.",
        body_hash="h3",
    )

    store_nodes(conn, [cls, func], repo_path="/repo")
    return conn, db_path


# --- Fallback summary generation ---

def test_generate_fallback_summary():
    """generate_fallback_summary creates summary from signature + docstring."""
    from agent_memory.summarizer import generate_fallback_summary
    summary = generate_fallback_summary(
        name="add",
        node_type="function",
        signature="def add(self, a, b)",
        docstring="Add two numbers.",
    )
    assert "add" in summary.lower()
    assert len(summary) > 0


def test_generate_fallback_summary_no_docstring():
    """Fallback summary works when docstring is empty."""
    from agent_memory.summarizer import generate_fallback_summary
    summary = generate_fallback_summary(
        name="process", node_type="function",
        signature="def process(data: dict)",
        docstring="",
    )
    assert "process" in summary.lower()
    assert len(summary) > 0


def test_generate_fallback_summary_class():
    """Fallback summary for class nodes."""
    from agent_memory.summarizer import generate_fallback_summary
    summary = generate_fallback_summary(
        name="Calculator", node_type="class",
        signature="class Calculator",
        docstring="A simple calculator.",
    )
    assert "Calculator" in summary
    assert len(summary) > 0


# --- Summarize nodes (bottom-up, using fallback) ---

def test_summarize_nodes_updates_db(summarizer_db):
    """summarize_nodes updates the summary column in code_nodes."""
    conn, db_path = summarizer_db
    from agent_memory.summarizer import summarize_nodes

    count = summarize_nodes(conn)
    assert count > 0

    # Check summaries were written
    cursor = conn.execute(
        "SELECT summary FROM code_nodes WHERE name = 'add'"
    )
    summary = cursor.fetchone()[0]
    assert len(summary) > 0


def test_summarize_nodes_updates_fts(summarizer_db):
    """summarize_nodes updates FTS entries with summaries."""
    conn, db_path = summarizer_db
    from agent_memory.summarizer import summarize_nodes

    summarize_nodes(conn)

    # FTS should now find by summary terms
    cursor = conn.execute(
        "SELECT name FROM code_nodes_fts WHERE code_nodes_fts MATCH 'add'"
    )
    results = cursor.fetchall()
    assert len(results) >= 1


def test_summarize_nodes_bottom_up(summarizer_db):
    """Leaf nodes are summarized before parent nodes."""
    conn, db_path = summarizer_db
    from agent_memory.summarizer import summarize_nodes

    summarize_nodes(conn)

    # Both method and class should have summaries
    cursor = conn.execute(
        "SELECT name, summary FROM code_nodes ORDER BY depth DESC"
    )
    rows = cursor.fetchall()
    for name, summary in rows:
        assert len(summary) > 0, f"Node {name} has no summary"


# --- CLI command ---

def test_cmd_code_summarize(summarizer_db, monkeypatch, capsys):
    """code-summarize CLI command generates summaries."""
    conn, db_path = summarizer_db
    conn.close()

    monkeypatch.setenv("AGENT_MEMORY_DB", str(db_path))

    from agent_memory.cli import cmd_code_summarize
    args = SimpleNamespace()
    cmd_code_summarize(args)

    captured = capsys.readouterr()
    assert "summar" in captured.out.lower()
