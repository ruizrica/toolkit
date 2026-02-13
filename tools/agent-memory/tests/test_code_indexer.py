# ABOUTME: Tests for code_indexer module — codebase discovery, parsing, and tree storage pipeline.
# ABOUTME: Verifies discover → parse → store workflow with change detection.

import pytest
from pathlib import Path


@pytest.fixture
def sample_codebase(tmp_path):
    """Create a sample codebase with Python and TypeScript files."""
    # Python file
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "calc.py").write_text(
        '# ABOUTME: Calculator module.\n'
        '# ABOUTME: Provides basic arithmetic.\n'
        '\n'
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
        'import os\n'
        'from pathlib import Path\n'
        '\n'
        'def read_file(path: str) -> str:\n'
        '    """Read a file and return contents."""\n'
        '    return Path(path).read_text()\n'
    )

    # TypeScript file
    (src_dir / "app.ts").write_text(
        'interface User {\n'
        '    id: string;\n'
        '    name: string;\n'
        '}\n'
        '\n'
        'function greet(user: User): string {\n'
        '    return `Hello, ${user.name}!`;\n'
        '}\n'
    )

    # Non-code file (should be ignored)
    (src_dir / "README.md").write_text("# Project\n\nSome docs.\n")
    (src_dir / "data.json").write_text('{"key": "value"}\n')

    # Nested directory
    lib_dir = src_dir / "lib"
    lib_dir.mkdir()
    (lib_dir / "helpers.py").write_text(
        'def format_name(first: str, last: str) -> str:\n'
        '    return f"{first} {last}"\n'
    )

    return tmp_path


@pytest.fixture
def code_db(tmp_path):
    """Provide a database connection for code indexing tests."""
    from agent_memory.db import init_db
    db_path = tmp_path / "code_test.db"
    return init_db(db_path)


# --- File discovery ---

def test_discover_code_files(sample_codebase):
    """discover_code_files finds .py, .ts, .js files recursively."""
    from agent_memory.code_indexer import discover_code_files
    files = discover_code_files(str(sample_codebase / "src"))
    extensions = {f.suffix for f in files}
    assert ".py" in extensions
    assert ".ts" in extensions
    assert ".md" not in extensions
    assert ".json" not in extensions


def test_discover_code_files_recursive(sample_codebase):
    """discover_code_files finds files in subdirectories."""
    from agent_memory.code_indexer import discover_code_files
    files = discover_code_files(str(sample_codebase / "src"))
    names = {f.name for f in files}
    assert "helpers.py" in names


def test_discover_code_files_respects_gitignore(sample_codebase):
    """discover_code_files skips common ignored directories."""
    from agent_memory.code_indexer import discover_code_files
    # Create a node_modules directory
    nm_dir = sample_codebase / "src" / "node_modules" / "pkg"
    nm_dir.mkdir(parents=True)
    (nm_dir / "index.js").write_text("module.exports = 42;\n")

    files = discover_code_files(str(sample_codebase / "src"))
    paths = {str(f) for f in files}
    assert not any("node_modules" in p for p in paths)


# --- Full indexing pipeline ---

def test_index_codebase(code_db, sample_codebase):
    """index_codebase processes files and stores code nodes."""
    from agent_memory.code_indexer import index_codebase
    stats = index_codebase(code_db, str(sample_codebase / "src"))

    assert stats.files_indexed > 0
    assert stats.nodes_created > 0

    # Verify nodes exist
    cursor = code_db.execute("SELECT COUNT(*) FROM code_nodes")
    assert cursor.fetchone()[0] > 0


def test_index_codebase_creates_correct_tree(code_db, sample_codebase):
    """Indexed nodes have correct parent-child relationships."""
    from agent_memory.code_indexer import index_codebase
    index_codebase(code_db, str(sample_codebase / "src"))

    # Calculator class should have 2 method children
    cursor = code_db.execute(
        "SELECT id FROM code_nodes WHERE name = 'Calculator'"
    )
    cls_row = cursor.fetchone()
    assert cls_row is not None

    cursor = code_db.execute(
        "SELECT name FROM code_nodes WHERE parent_id = ?", (cls_row[0],)
    )
    children = {row[0] for row in cursor.fetchall()}
    assert "add" in children
    assert "subtract" in children


def test_index_codebase_populates_fts(code_db, sample_codebase):
    """Indexing populates the FTS table for keyword search."""
    from agent_memory.code_indexer import index_codebase
    index_codebase(code_db, str(sample_codebase / "src"))

    cursor = code_db.execute(
        "SELECT name FROM code_nodes_fts "
        "WHERE code_nodes_fts MATCH 'calculator'"
    )
    results = cursor.fetchall()
    assert len(results) >= 1


def test_index_codebase_records_files(code_db, sample_codebase):
    """Indexing records file metadata in code_files for change detection."""
    from agent_memory.code_indexer import index_codebase
    index_codebase(code_db, str(sample_codebase / "src"))

    cursor = code_db.execute("SELECT COUNT(*) FROM code_files")
    count = cursor.fetchone()[0]
    assert count > 0


# --- Change detection ---

def test_index_codebase_skips_unchanged(code_db, sample_codebase):
    """Running index_codebase twice skips unchanged files."""
    from agent_memory.code_indexer import index_codebase
    stats1 = index_codebase(code_db, str(sample_codebase / "src"))
    stats2 = index_codebase(code_db, str(sample_codebase / "src"))

    assert stats1.files_indexed > 0
    assert stats2.files_skipped > 0
    assert stats2.files_indexed == 0


def test_index_codebase_reindexes_changed(code_db, sample_codebase):
    """Modified files are re-indexed on second run."""
    from agent_memory.code_indexer import index_codebase
    index_codebase(code_db, str(sample_codebase / "src"))

    # Modify a file
    calc = sample_codebase / "src" / "calc.py"
    calc.write_text(
        'class Calculator:\n'
        '    def multiply(self, a, b):\n'
        '        return a * b\n'
    )

    stats2 = index_codebase(code_db, str(sample_codebase / "src"))
    assert stats2.files_indexed >= 1


# --- Stats ---

def test_index_stats_fields(code_db, sample_codebase):
    """CodeIndexStats has expected fields."""
    from agent_memory.code_indexer import index_codebase
    stats = index_codebase(code_db, str(sample_codebase / "src"))
    assert hasattr(stats, "files_indexed")
    assert hasattr(stats, "files_skipped")
    assert hasattr(stats, "nodes_created")
