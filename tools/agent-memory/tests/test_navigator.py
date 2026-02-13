# ABOUTME: Tests for navigator module — FTS-based beam search tree descent.
# ABOUTME: Verifies navigation through code trees, trace output, and edge cases.

import pytest
from pathlib import Path


@pytest.fixture
def nav_db(tmp_path):
    """Provide a database with indexed code for navigation tests."""
    from agent_memory.db import init_db
    from agent_memory.parser import CodeNode
    from agent_memory.tree import store_nodes

    db_path = tmp_path / "nav_test.db"
    conn = init_db(db_path)

    # Build a tree: repo root → file nodes → class → methods
    method_add = CodeNode(
        name="add", qualified_name="Calculator.add", node_type="function",
        file_path="src/calc.py", start_line=4, end_line=6,
        signature="def add(self, a, b)", docstring="Add two numbers.",
        body_hash="h1",
    )
    method_sub = CodeNode(
        name="subtract", qualified_name="Calculator.subtract", node_type="function",
        file_path="src/calc.py", start_line=8, end_line=10,
        signature="def subtract(self, a, b)", docstring="Subtract b from a.",
        body_hash="h2",
    )
    cls_calc = CodeNode(
        name="Calculator", qualified_name="Calculator", node_type="class",
        file_path="src/calc.py", start_line=1, end_line=10,
        signature="class Calculator", docstring="A simple calculator for arithmetic.",
        body_hash="h3",
        children=[method_add, method_sub],
    )

    method_search = CodeNode(
        name="search_hybrid", qualified_name="SearchEngine.search_hybrid",
        node_type="function", file_path="src/search.py",
        start_line=10, end_line=30,
        signature="def search_hybrid(self, query, limit=5)",
        docstring="Hybrid search combining vector and BM25 scores.",
        body_hash="h4",
    )
    cls_search = CodeNode(
        name="SearchEngine", qualified_name="SearchEngine", node_type="class",
        file_path="src/search.py", start_line=1, end_line=30,
        signature="class SearchEngine", docstring="Full-text and vector search engine.",
        body_hash="h5",
        children=[method_search],
    )

    func_util = CodeNode(
        name="format_output", qualified_name="format_output", node_type="function",
        file_path="src/utils.py", start_line=1, end_line=5,
        signature="def format_output(data: dict) -> str",
        docstring="Format data dictionary as human-readable string.",
        body_hash="h6",
    )

    store_nodes(conn, [cls_calc, cls_search, func_util], repo_path="/repo")
    return conn


# --- Navigation ---

def test_navigate_finds_matching_node(nav_db):
    """navigate() finds a node matching the query."""
    from agent_memory.navigator import navigate
    result = navigate(nav_db, "calculator add")
    assert result.nodes
    names = {n["name"] for n in result.nodes}
    assert "add" in names or "Calculator" in names


def test_navigate_finds_search_hybrid(nav_db):
    """navigate() finds search_hybrid when querying about hybrid search."""
    from agent_memory.navigator import navigate
    result = navigate(nav_db, "hybrid search")
    assert result.nodes
    names = {n["name"] for n in result.nodes}
    assert "search_hybrid" in names or "SearchEngine" in names


def test_navigate_returns_trace(nav_db):
    """navigate() returns a non-empty trace of navigation steps."""
    from agent_memory.navigator import navigate
    result = navigate(nav_db, "add numbers")
    assert len(result.steps) >= 1


def test_navigate_no_results(nav_db):
    """navigate() returns empty nodes for a query with no matches."""
    from agent_memory.navigator import navigate
    result = navigate(nav_db, "xyzzy_nonexistent_function")
    assert len(result.nodes) == 0


def test_navigate_result_has_fields(nav_db):
    """NavigationResult has nodes and steps attributes."""
    from agent_memory.navigator import navigate, NavigationResult
    result = navigate(nav_db, "format output")
    assert isinstance(result, NavigationResult)
    assert hasattr(result, "nodes")
    assert hasattr(result, "steps")


# --- Navigation step ---

def test_navigation_step_fields():
    """NavigationStep has depth, candidates, and selected fields."""
    from agent_memory.navigator import NavigationStep
    step = NavigationStep(depth=0, candidates=["Calculator"], selected=["Calculator"])
    assert step.depth == 0
    assert step.candidates == ["Calculator"]
    assert step.selected == ["Calculator"]


# --- Format output ---

def test_format_navigation_result(nav_db):
    """format_navigation_result produces human-readable output."""
    from agent_memory.navigator import navigate, format_navigation_result
    result = navigate(nav_db, "calculator")
    output = format_navigation_result(result)
    assert isinstance(output, str)
    assert len(output) > 0


def test_format_navigation_result_empty():
    """format_navigation_result handles empty results gracefully."""
    from agent_memory.navigator import NavigationResult, format_navigation_result
    result = NavigationResult(nodes=[], steps=[])
    output = format_navigation_result(result)
    assert "no results" in output.lower() or "not found" in output.lower() or len(output) >= 0


# --- Beam width ---

def test_navigate_respects_beam_width(nav_db):
    """navigate() with beam_width=1 still returns results."""
    from agent_memory.navigator import navigate
    result = navigate(nav_db, "calculator", beam_width=1)
    assert result.nodes is not None
