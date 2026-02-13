# ABOUTME: Tests for tree module — code node storage and retrieval in SQLite.
# ABOUTME: Verifies CRUD, parent-child queries, FTS, and cross-reference resolution.

import pytest
from pathlib import Path


@pytest.fixture
def tree_db(tmp_path):
    """Provide a database connection with code tree tables initialized."""
    from agent_memory.db import init_db
    db_path = tmp_path / "tree_test.db"
    conn = init_db(db_path)
    return conn


@pytest.fixture
def sample_nodes():
    """Provide sample CodeNodes for testing storage."""
    from agent_memory.parser import CodeNode
    method1 = CodeNode(
        name="add", qualified_name="Calculator.add", node_type="function",
        file_path="calc.py", start_line=4, end_line=6,
        signature="def add(self, a, b)", docstring="Add two numbers.",
        body_hash="hash_add",
    )
    method2 = CodeNode(
        name="subtract", qualified_name="Calculator.subtract", node_type="function",
        file_path="calc.py", start_line=8, end_line=10,
        signature="def subtract(self, a, b)", docstring="",
        body_hash="hash_sub",
    )
    cls = CodeNode(
        name="Calculator", qualified_name="Calculator", node_type="class",
        file_path="calc.py", start_line=1, end_line=10,
        signature="class Calculator", docstring="A calculator.",
        body_hash="hash_cls",
        children=[method1, method2],
    )
    return cls


# --- Schema creation ---

def test_code_tables_created(tree_db):
    """init_db creates code_nodes, code_nodes_fts, code_refs, code_files tables."""
    cursor = tree_db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' "
        "AND name LIKE 'code_%' ORDER BY name"
    )
    tables = {row[0] for row in cursor.fetchall()}
    assert "code_nodes" in tables
    assert "code_nodes_fts" in tables
    assert "code_refs" in tables
    assert "code_files" in tables


# --- Store and retrieve ---

def test_store_nodes(tree_db, sample_nodes):
    """store_nodes inserts nodes and children into code_nodes."""
    from agent_memory.tree import store_nodes
    store_nodes(tree_db, [sample_nodes], repo_path="/repo")
    cursor = tree_db.execute("SELECT COUNT(*) FROM code_nodes")
    count = cursor.fetchone()[0]
    # 1 class + 2 methods = 3
    assert count == 3


def test_store_nodes_parent_child(tree_db, sample_nodes):
    """Children reference their parent's ID."""
    from agent_memory.tree import store_nodes, get_children
    store_nodes(tree_db, [sample_nodes], repo_path="/repo")

    # Get the class node
    cursor = tree_db.execute(
        "SELECT id FROM code_nodes WHERE name = 'Calculator'"
    )
    cls_id = cursor.fetchone()[0]

    children = get_children(tree_db, cls_id)
    assert len(children) == 2
    names = {c["name"] for c in children}
    assert "add" in names
    assert "subtract" in names


def test_get_node(tree_db, sample_nodes):
    """get_node returns full node data by ID."""
    from agent_memory.tree import store_nodes, get_node
    store_nodes(tree_db, [sample_nodes], repo_path="/repo")

    cursor = tree_db.execute(
        "SELECT id FROM code_nodes WHERE name = 'Calculator'"
    )
    cls_id = cursor.fetchone()[0]

    node = get_node(tree_db, cls_id)
    assert node is not None
    assert node["name"] == "Calculator"
    assert node["node_type"] == "class"
    assert node["docstring"] == "A calculator."
    assert node["signature"] == "class Calculator"


def test_get_roots(tree_db, sample_nodes):
    """get_roots returns only top-level nodes (no parent)."""
    from agent_memory.tree import store_nodes, get_roots
    store_nodes(tree_db, [sample_nodes], repo_path="/repo")

    roots = get_roots(tree_db, repo_path="/repo")
    assert len(roots) == 1
    assert roots[0]["name"] == "Calculator"


def test_get_path_to_root(tree_db, sample_nodes):
    """get_path_to_root walks up from a child to the root."""
    from agent_memory.tree import store_nodes, get_path_to_root
    store_nodes(tree_db, [sample_nodes], repo_path="/repo")

    cursor = tree_db.execute(
        "SELECT id FROM code_nodes WHERE name = 'add'"
    )
    add_id = cursor.fetchone()[0]

    path = get_path_to_root(tree_db, add_id)
    names = [p["name"] for p in path]
    assert names == ["add", "Calculator"]


# --- FTS search ---

def test_fts_search(tree_db, sample_nodes):
    """FTS5 table allows searching by name, signature, docstring."""
    from agent_memory.tree import store_nodes
    store_nodes(tree_db, [sample_nodes], repo_path="/repo")

    cursor = tree_db.execute(
        "SELECT name FROM code_nodes_fts WHERE code_nodes_fts MATCH 'calculator'"
    )
    results = cursor.fetchall()
    assert len(results) >= 1


def test_fts_search_by_docstring(tree_db, sample_nodes):
    """FTS finds nodes by docstring content."""
    from agent_memory.tree import store_nodes
    store_nodes(tree_db, [sample_nodes], repo_path="/repo")

    cursor = tree_db.execute(
        "SELECT name FROM code_nodes_fts WHERE code_nodes_fts MATCH 'numbers'"
    )
    results = cursor.fetchall()
    assert len(results) >= 1


# --- Cross-references ---

def test_store_refs(tree_db):
    """store_refs inserts reference records."""
    from agent_memory.tree import store_refs
    store_refs(tree_db, [
        {"source_id": 1, "target_name": "os.path", "ref_type": "import", "line": 1},
        {"source_id": 1, "target_name": "Calculator", "ref_type": "call", "line": 5},
    ])
    cursor = tree_db.execute("SELECT COUNT(*) FROM code_refs")
    assert cursor.fetchone()[0] == 2


def test_resolve_refs(tree_db, sample_nodes):
    """resolve_refs matches target_name to actual nodes."""
    from agent_memory.tree import store_nodes, store_refs, resolve_refs
    store_nodes(tree_db, [sample_nodes], repo_path="/repo")

    cursor = tree_db.execute(
        "SELECT id FROM code_nodes WHERE name = 'add'"
    )
    add_id = cursor.fetchone()[0]

    store_refs(tree_db, [
        {"source_id": add_id, "target_name": "Calculator", "ref_type": "call", "line": 5},
    ])

    refs = resolve_refs(tree_db, add_id)
    assert len(refs) == 1
    assert refs[0]["target_name"] == "Calculator"
    assert refs[0]["target_id"] is not None


# --- Depth tracking ---

def test_node_depth(tree_db, sample_nodes):
    """Nodes store correct depth (0 for root, 1 for children, etc.)."""
    from agent_memory.tree import store_nodes
    store_nodes(tree_db, [sample_nodes], repo_path="/repo")

    cursor = tree_db.execute(
        "SELECT name, depth FROM code_nodes ORDER BY depth, name"
    )
    rows = {row[0]: row[1] for row in cursor.fetchall()}
    assert rows["Calculator"] == 0
    assert rows["add"] == 1
    assert rows["subtract"] == 1


# --- Re-indexing (idempotent) ---

def test_store_nodes_replaces_on_reindex(tree_db, sample_nodes):
    """Storing nodes for the same file replaces previous entries."""
    from agent_memory.tree import store_nodes
    store_nodes(tree_db, [sample_nodes], repo_path="/repo")

    cursor = tree_db.execute("SELECT COUNT(*) FROM code_nodes")
    count1 = cursor.fetchone()[0]

    # Store again (simulating re-index)
    store_nodes(tree_db, [sample_nodes], repo_path="/repo")

    cursor = tree_db.execute("SELECT COUNT(*) FROM code_nodes")
    count2 = cursor.fetchone()[0]
    assert count2 == count1
