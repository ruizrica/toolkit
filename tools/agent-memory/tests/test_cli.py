# ABOUTME: Tests for cli module — argparse entry point and subcommands.
# ABOUTME: Verifies CLI argument parsing, --json output, and subcommand routing.

import json
import subprocess
import sys
from pathlib import Path


def _run_cli(*args, env_overrides=None):
    """Run agent-memory CLI as a subprocess, returning (stdout, stderr, returncode)."""
    import os

    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)

    src_dir = str(Path(__file__).parent.parent / "src")
    env["PYTHONPATH"] = src_dir + os.pathsep + env.get("PYTHONPATH", "")

    result = subprocess.run(
        [sys.executable, "-m", "agent_memory"] + list(args),
        capture_output=True,
        text=True,
        env=env,
        cwd=str(Path(__file__).parent.parent),
    )
    return result.stdout, result.stderr, result.returncode


def test_cli_no_args():
    """Running with no args shows help and exits cleanly."""
    stdout, stderr, code = _run_cli()
    assert code == 0
    assert "usage" in stdout.lower() or "agent-memory" in stdout.lower()


def test_cli_help():
    """--help shows usage information."""
    stdout, stderr, code = _run_cli("--help")
    assert code == 0
    assert "search" in stdout.lower()
    assert "index" in stdout.lower()


def test_cli_status(tmp_path):
    """status subcommand shows database info."""
    db_path = tmp_path / "test.db"
    stdout, stderr, code = _run_cli(
        "status",
        env_overrides={"AGENT_MEMORY_DB": str(db_path)},
    )
    assert code == 0


def test_cli_status_json(tmp_path):
    """status --json outputs valid JSON."""
    db_path = tmp_path / "test.db"
    stdout, stderr, code = _run_cli(
        "status", "--json",
        env_overrides={"AGENT_MEMORY_DB": str(db_path)},
    )
    assert code == 0
    data = json.loads(stdout)
    assert "chunks" in data
    assert "files" in data


def test_cli_add_and_list(tmp_path):
    """add + list roundtrip works."""
    db_path = tmp_path / "test.db"
    env = {"AGENT_MEMORY_DB": str(db_path)}

    # Add
    stdout, stderr, code = _run_cli(
        "add", "Test memory content",
        env_overrides=env,
    )
    assert code == 0

    # List
    stdout, stderr, code = _run_cli(
        "list", "--json",
        env_overrides=env,
    )
    assert code == 0
    data = json.loads(stdout)
    assert len(data) >= 1
    assert any("Test memory content" in item["text"] for item in data)


def test_cli_search_json(tmp_path, sample_memory_dir):
    """search --json outputs valid JSON array."""
    db_path = tmp_path / "test.db"
    env = {
        "AGENT_MEMORY_DB": str(db_path),
        "AGENT_MEMORY_DIR": str(sample_memory_dir / "agent-memory"),
    }

    # Index first
    stdout, stderr, code = _run_cli(
        "index",
        "--path", str(sample_memory_dir / "agent-memory" / "daily-logs"),
        env_overrides=env,
    )
    assert code == 0

    # Search
    stdout, stderr, code = _run_cli(
        "search", "FastEmbed", "--json",
        env_overrides=env,
    )
    assert code == 0
    data = json.loads(stdout)
    assert isinstance(data, list)


def test_cli_search_modes(tmp_path, sample_memory_dir):
    """search accepts --vector and --keyword flags."""
    db_path = tmp_path / "test.db"
    env = {
        "AGENT_MEMORY_DB": str(db_path),
        "AGENT_MEMORY_DIR": str(sample_memory_dir / "agent-memory"),
    }

    _run_cli(
        "index",
        "--path", str(sample_memory_dir / "agent-memory" / "daily-logs"),
        env_overrides=env,
    )

    # Keyword mode
    stdout, stderr, code = _run_cli(
        "search", "FastEmbed", "--keyword", "--json",
        env_overrides=env,
    )
    assert code == 0

    # Vector mode
    stdout, stderr, code = _run_cli(
        "search", "embeddings", "--vector", "--json",
        env_overrides=env,
    )
    assert code == 0


def test_cli_index_custom_path(tmp_path, sample_memory_dir):
    """index --path indexes only the specified path."""
    db_path = tmp_path / "test.db"
    daily_dir = sample_memory_dir / "agent-memory" / "daily-logs"
    env = {"AGENT_MEMORY_DB": str(db_path)}

    stdout, stderr, code = _run_cli(
        "index", "--path", str(daily_dir),
        env_overrides=env,
    )
    assert code == 0
    assert "indexed" in stdout.lower() or "Indexed" in stdout


def test_cli_ask_without_sdk(tmp_path):
    """ask subcommand fails gracefully without Agent SDK."""
    db_path = tmp_path / "test.db"
    stdout, stderr, code = _run_cli(
        "ask", "what do I know?",
        env_overrides={"AGENT_MEMORY_DB": str(db_path)},
    )
    # Should fail with helpful message (SDK not installed)
    assert code != 0 or "install" in (stdout + stderr).lower()
