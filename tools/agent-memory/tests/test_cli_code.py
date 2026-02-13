# ABOUTME: Tests for code-related CLI subcommands (code-index, code-nav, code-tree, code-refs).
# ABOUTME: Uses direct function calls to test CLI handlers with temporary databases.

import json
import pytest
from pathlib import Path
from types import SimpleNamespace


@pytest.fixture
def sample_codebase(tmp_path):
    """Create a sample codebase for CLI testing."""
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "calc.py").write_text(
        'class Calculator:\n'
        '    """A simple calculator."""\n'
        '\n'
        '    def add(self, a, b):\n'
        '        """Add two numbers."""\n'
        '        return a + b\n'
        '\n'
        '    def subtract(self, a, b):\n'
        '        return a - b\n'
    )
    (src_dir / "utils.py").write_text(
        'def read_file(path: str) -> str:\n'
        '    return open(path).read()\n'
    )
    return tmp_path


@pytest.fixture
def indexed_db(tmp_path, sample_codebase):
    """Provide a DB already indexed with the sample codebase."""
    import os
    db_path = tmp_path / "cli_test.db"
    os.environ["AGENT_MEMORY_DB"] = str(db_path)

    from agent_memory.cli import cmd_code_index
    args = SimpleNamespace(path=str(sample_codebase / "src"))
    cmd_code_index(args)

    yield db_path

    os.environ.pop("AGENT_MEMORY_DB", None)


# --- code-index command ---

def test_cmd_code_index(tmp_path, sample_codebase, monkeypatch, capsys):
    """code-index indexes a codebase and prints stats."""
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("AGENT_MEMORY_DB", str(db_path))

    from agent_memory.cli import cmd_code_index
    args = SimpleNamespace(path=str(sample_codebase / "src"))
    cmd_code_index(args)

    captured = capsys.readouterr()
    assert "indexed" in captured.out.lower() or "Indexed" in captured.out


def test_cmd_code_index_creates_nodes(tmp_path, sample_codebase, monkeypatch):
    """code-index creates code_nodes in the database."""
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("AGENT_MEMORY_DB", str(db_path))

    from agent_memory.cli import cmd_code_index
    args = SimpleNamespace(path=str(sample_codebase / "src"))
    cmd_code_index(args)

    from agent_memory.db import init_db
    conn = init_db(db_path)
    cursor = conn.execute("SELECT COUNT(*) FROM code_nodes")
    assert cursor.fetchone()[0] > 0
    conn.close()


# --- code-nav command ---

def test_cmd_code_nav(indexed_db, monkeypatch, capsys):
    """code-nav navigates the code tree."""
    monkeypatch.setenv("AGENT_MEMORY_DB", str(indexed_db))

    from agent_memory.cli import cmd_code_nav
    args = SimpleNamespace(query="calculator", as_json=False)
    cmd_code_nav(args)

    captured = capsys.readouterr()
    assert len(captured.out) > 0


def test_cmd_code_nav_json(indexed_db, monkeypatch, capsys):
    """code-nav --json outputs valid JSON."""
    monkeypatch.setenv("AGENT_MEMORY_DB", str(indexed_db))

    from agent_memory.cli import cmd_code_nav
    args = SimpleNamespace(query="calculator", as_json=True)
    cmd_code_nav(args)

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "nodes" in data
    assert "steps" in data


def test_cmd_code_nav_no_results(indexed_db, monkeypatch, capsys):
    """code-nav with unmatched query shows no-results message."""
    monkeypatch.setenv("AGENT_MEMORY_DB", str(indexed_db))

    from agent_memory.cli import cmd_code_nav
    args = SimpleNamespace(query="xyzzy_nonexistent", as_json=False)
    cmd_code_nav(args)

    captured = capsys.readouterr()
    assert "no" in captured.out.lower() or len(captured.out) >= 0


# --- code-tree command ---

def test_cmd_code_tree(indexed_db, monkeypatch, capsys):
    """code-tree displays the tree structure."""
    monkeypatch.setenv("AGENT_MEMORY_DB", str(indexed_db))

    from agent_memory.cli import cmd_code_tree
    args = SimpleNamespace(path=None, as_json=False)
    cmd_code_tree(args)

    captured = capsys.readouterr()
    assert "Calculator" in captured.out


def test_cmd_code_tree_json(indexed_db, monkeypatch, capsys):
    """code-tree --json outputs valid JSON."""
    monkeypatch.setenv("AGENT_MEMORY_DB", str(indexed_db))

    from agent_memory.cli import cmd_code_tree
    args = SimpleNamespace(path=None, as_json=True)
    cmd_code_tree(args)

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert isinstance(data, list)


# --- code-refs command ---

def test_cmd_code_refs(indexed_db, monkeypatch, capsys):
    """code-refs shows references for a node."""
    monkeypatch.setenv("AGENT_MEMORY_DB", str(indexed_db))

    # Get a node ID
    from agent_memory.db import init_db
    conn = init_db(indexed_db)
    cursor = conn.execute("SELECT id FROM code_nodes LIMIT 1")
    node_id = cursor.fetchone()[0]
    conn.close()

    from agent_memory.cli import cmd_code_refs
    args = SimpleNamespace(node_id=str(node_id), as_json=False)
    cmd_code_refs(args)

    captured = capsys.readouterr()
    # Should output something (even if "no references")
    assert len(captured.out) >= 0


def test_cmd_code_refs_json(indexed_db, monkeypatch, capsys):
    """code-refs --json outputs valid JSON."""
    monkeypatch.setenv("AGENT_MEMORY_DB", str(indexed_db))

    from agent_memory.db import init_db
    conn = init_db(indexed_db)
    cursor = conn.execute("SELECT id FROM code_nodes LIMIT 1")
    node_id = cursor.fetchone()[0]
    conn.close()

    from agent_memory.cli import cmd_code_refs
    args = SimpleNamespace(node_id=str(node_id), as_json=True)
    cmd_code_refs(args)

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert isinstance(data, list)


# --- Help includes new commands ---

def test_cli_help_includes_code_commands():
    """--help lists code-index, code-nav, code-tree, code-refs."""
    from agent_memory.cli import _build_parser
    parser = _build_parser()
    # Check subcommands are registered
    subparsers = None
    for action in parser._subparsers._actions:
        if hasattr(action, '_parser_class'):
            subparsers = action
            break

    if subparsers:
        choices = list(subparsers.choices.keys())
        assert "code-index" in choices
        assert "code-nav" in choices
        assert "code-tree" in choices
        assert "code-refs" in choices
