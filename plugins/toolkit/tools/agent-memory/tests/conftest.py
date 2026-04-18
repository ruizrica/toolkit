# ABOUTME: Shared pytest fixtures for agent-memory tests.
# ABOUTME: Provides tmp DB, sample markdown files, and test configuration.

import pytest


@pytest.fixture
def tmp_dir(tmp_path):
    """Provide a temporary directory for test files."""
    return tmp_path


@pytest.fixture
def sample_memory_dir(tmp_path):
    """Create a sample memory directory structure with test markdown files."""
    memory_dir = tmp_path / "agent-memory"
    daily_dir = memory_dir / "daily-logs"
    sessions_dir = memory_dir / "sessions"
    daily_dir.mkdir(parents=True)
    sessions_dir.mkdir(parents=True)

    # Sample daily log
    (daily_dir / "2026-02-11.md").write_text(
        "# 2026-02-11\n\n"
        "## Session 1\n\n"
        "- Decided to use FastEmbed for local embeddings\n"
        "- Implemented hybrid search with 0.7 vector + 0.3 BM25\n"
    )

    # Sample session snapshot
    (sessions_dir / "project-20260211T1000.md").write_text(
        "# Session: project\n\n"
        "Working on agent-memory CLI tool.\n"
        "Key decision: use SQLite with sqlite-vec for vector storage.\n"
    )

    # Sample MEMORY.md in a project dir
    projects_dir = tmp_path / "projects" / "myproject" / "memory"
    projects_dir.mkdir(parents=True)
    (projects_dir / "MEMORY.md").write_text(
        "# Project Memory\n\n"
        "## Conventions\n\n"
        "- Always use TDD\n"
        "- Prefer simple solutions\n"
    )

    return tmp_path


@pytest.fixture
def tmp_db(tmp_path):
    """Provide a path for a temporary SQLite database."""
    return tmp_path / "test_memory.db"
