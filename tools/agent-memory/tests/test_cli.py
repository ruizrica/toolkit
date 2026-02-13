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
    """Running with no args shows logo and help and exits cleanly."""
    stdout, stderr, code = _run_cli()
    assert code == 0
    assert "usage" in stdout.lower() or "agent-memory" in stdout.lower()


def test_cli_no_args_shows_logo():
    """Running with no args displays the MEMORY ASCII logo."""
    stdout, stderr, code = _run_cli()
    assert code == 0
    assert "▄██████▄" in stdout
    assert "████▀" in stdout


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


def test_cli_add_prints_full_id(tmp_path):
    """add prints the full chunk ID, not a truncated version."""
    db_path = tmp_path / "test.db"
    env = {"AGENT_MEMORY_DB": str(db_path)}

    stdout, stderr, code = _run_cli(
        "add", "full id test",
        env_overrides=env,
    )
    assert code == 0
    # Output should contain a full 64-char hex hash (SHA-256)
    # Format: "Added: <full_id>"
    line = stdout.strip()
    assert line.startswith("Added: ")
    chunk_id = line.split("Added: ")[1]
    assert len(chunk_id) == 64
    assert "..." not in chunk_id


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


# --- get subcommand ---


def test_cli_get_exact_id(tmp_path):
    """get retrieves a memory by exact ID."""
    db_path = tmp_path / "test.db"
    env = {"AGENT_MEMORY_DB": str(db_path)}

    # Add a memory and capture the ID
    stdout, _, code = _run_cli("add", "get test content", env_overrides=env)
    assert code == 0
    chunk_id = stdout.strip().split("Added: ")[1]

    # Get by exact ID
    stdout, stderr, code = _run_cli("get", chunk_id, env_overrides=env)
    assert code == 0
    assert "get test content" in stdout


def test_cli_get_json(tmp_path):
    """get --json outputs valid JSON with expected fields."""
    db_path = tmp_path / "test.db"
    env = {"AGENT_MEMORY_DB": str(db_path)}

    stdout, _, _ = _run_cli("add", "json get test", env_overrides=env)
    chunk_id = stdout.strip().split("Added: ")[1]

    stdout, stderr, code = _run_cli("get", chunk_id, "--json", env_overrides=env)
    assert code == 0
    data = json.loads(stdout)
    assert data["id"] == chunk_id
    assert data["text"] == "json get test"
    assert "source" in data
    assert "created_at" in data


def test_cli_get_by_prefix(tmp_path):
    """get finds a memory using a unique ID prefix."""
    db_path = tmp_path / "test.db"
    env = {"AGENT_MEMORY_DB": str(db_path)}

    stdout, _, _ = _run_cli("add", "prefix get test", env_overrides=env)
    chunk_id = stdout.strip().split("Added: ")[1]
    prefix = chunk_id[:12]

    stdout, stderr, code = _run_cli("get", prefix, env_overrides=env)
    assert code == 0
    assert "prefix get test" in stdout


def test_cli_get_not_found(tmp_path):
    """get exits with error for non-existent ID."""
    db_path = tmp_path / "test.db"
    env = {"AGENT_MEMORY_DB": str(db_path)}

    stdout, stderr, code = _run_cli("get", "nonexistent_id_12345", env_overrides=env)
    assert code != 0
    assert "not found" in stderr.lower()


def test_cli_get_text_output_format(tmp_path):
    """get text output shows ID, Source, and Text fields."""
    db_path = tmp_path / "test.db"
    env = {"AGENT_MEMORY_DB": str(db_path)}

    stdout, _, _ = _run_cli("add", "format test", env_overrides=env)
    chunk_id = stdout.strip().split("Added: ")[1]

    stdout, _, code = _run_cli("get", chunk_id, env_overrides=env)
    assert code == 0
    assert "ID:" in stdout
    assert "Source:" in stdout
    assert "Text:" in stdout


# --- list subcommand ---


def test_cli_list_text_output(tmp_path):
    """list without --json shows text output."""
    db_path = tmp_path / "test.db"
    env = {"AGENT_MEMORY_DB": str(db_path)}

    _run_cli("add", "list text test", env_overrides=env)

    stdout, stderr, code = _run_cli("list", env_overrides=env)
    assert code == 0
    assert "list text test" in stdout


def test_cli_list_empty(tmp_path):
    """list on empty database shows 'no memories' message."""
    db_path = tmp_path / "test.db"
    env = {"AGENT_MEMORY_DB": str(db_path)}

    stdout, stderr, code = _run_cli("list", env_overrides=env)
    assert code == 0
    assert "no memories" in stdout.lower()


def test_cli_list_source_filter(tmp_path):
    """list --source filters memories by source type."""
    db_path = tmp_path / "test.db"
    env = {"AGENT_MEMORY_DB": str(db_path)}

    _run_cli("add", "daily item", "--source", "daily", env_overrides=env)
    _run_cli("add", "session item", "--source", "session", env_overrides=env)

    stdout, _, code = _run_cli("list", "--source", "daily", "--json", env_overrides=env)
    assert code == 0
    data = json.loads(stdout)
    assert len(data) == 1
    assert data[0]["source"] == "daily"


def test_cli_list_limit(tmp_path):
    """list --limit constrains result count."""
    db_path = tmp_path / "test.db"
    env = {"AGENT_MEMORY_DB": str(db_path)}

    for i in range(5):
        _run_cli("add", f"limit item {i}", env_overrides=env)

    stdout, _, code = _run_cli("list", "--limit", "2", "--json", env_overrides=env)
    assert code == 0
    data = json.loads(stdout)
    assert len(data) == 2


def test_cli_list_json_empty(tmp_path):
    """list --json on empty database returns empty JSON array."""
    db_path = tmp_path / "test.db"
    env = {"AGENT_MEMORY_DB": str(db_path)}

    stdout, _, code = _run_cli("list", "--json", env_overrides=env)
    assert code == 0
    data = json.loads(stdout)
    assert data == []


# --- add subcommand ---


def test_cli_add_with_tags(tmp_path):
    """add --tags stores tags in the path field."""
    db_path = tmp_path / "test.db"
    env = {"AGENT_MEMORY_DB": str(db_path)}

    stdout, _, code = _run_cli(
        "add", "tagged content", "--tags", "workflow,tdd",
        env_overrides=env,
    )
    assert code == 0

    stdout, _, code = _run_cli("list", "--json", env_overrides=env)
    data = json.loads(stdout)
    assert len(data) == 1
    assert "workflow,tdd" in data[0]["path"]


def test_cli_add_with_source(tmp_path):
    """add --source sets the source type."""
    db_path = tmp_path / "test.db"
    env = {"AGENT_MEMORY_DB": str(db_path)}

    _run_cli("add", "sourced content", "--source", "daily", env_overrides=env)

    stdout, _, code = _run_cli("list", "--json", env_overrides=env)
    data = json.loads(stdout)
    assert data[0]["source"] == "daily"


def test_cli_add_idempotent(tmp_path):
    """Adding the same content twice doesn't create duplicates (INSERT OR REPLACE)."""
    db_path = tmp_path / "test.db"
    env = {"AGENT_MEMORY_DB": str(db_path)}

    _run_cli("add", "idempotent content", env_overrides=env)
    _run_cli("add", "idempotent content", env_overrides=env)

    stdout, _, _ = _run_cli("list", "--json", env_overrides=env)
    data = json.loads(stdout)
    assert len(data) == 1


# --- search subcommand ---


def test_cli_search_text_output(tmp_path, sample_memory_dir):
    """search without --json shows text output with scores."""
    db_path = tmp_path / "test.db"
    env = {
        "AGENT_MEMORY_DB": str(db_path),
        "AGENT_MEMORY_DIR": str(sample_memory_dir / "agent-memory"),
    }

    _run_cli(
        "index", "--path", str(sample_memory_dir / "agent-memory" / "daily-logs"),
        env_overrides=env,
    )

    stdout, stderr, code = _run_cli("search", "FastEmbed", env_overrides=env)
    assert code == 0
    # Text output has score format like [0.xxx]
    assert "[" in stdout


def test_cli_search_no_results(tmp_path):
    """search with no matching data shows 'no results' message."""
    db_path = tmp_path / "test.db"
    env = {"AGENT_MEMORY_DB": str(db_path)}

    stdout, stderr, code = _run_cli(
        "search", "xyznonexistent12345", env_overrides=env,
    )
    assert code == 0
    assert "no results" in stdout.lower()


def test_cli_search_limit(tmp_path, sample_memory_dir):
    """search --limit constrains result count."""
    db_path = tmp_path / "test.db"
    env = {
        "AGENT_MEMORY_DB": str(db_path),
        "AGENT_MEMORY_DIR": str(sample_memory_dir / "agent-memory"),
    }

    _run_cli(
        "index", "--path", str(sample_memory_dir / "agent-memory" / "daily-logs"),
        env_overrides=env,
    )

    stdout, _, code = _run_cli(
        "search", "embeddings", "--limit", "1", "--json",
        env_overrides=env,
    )
    assert code == 0
    data = json.loads(stdout)
    assert len(data) <= 1


def test_cli_search_json_result_fields(tmp_path, sample_memory_dir):
    """search --json results have all expected fields."""
    db_path = tmp_path / "test.db"
    env = {
        "AGENT_MEMORY_DB": str(db_path),
        "AGENT_MEMORY_DIR": str(sample_memory_dir / "agent-memory"),
    }

    _run_cli(
        "index", "--path", str(sample_memory_dir / "agent-memory" / "daily-logs"),
        env_overrides=env,
    )

    stdout, _, code = _run_cli(
        "search", "FastEmbed", "--json", env_overrides=env,
    )
    assert code == 0
    data = json.loads(stdout)
    if data:
        item = data[0]
        assert "id" in item
        assert "text" in item
        assert "path" in item
        assert "source" in item
        assert "score" in item
        assert "start_line" in item
        assert "end_line" in item


def test_cli_search_special_chars(tmp_path):
    """search handles FTS5-special characters without crashing."""
    db_path = tmp_path / "test.db"
    env = {"AGENT_MEMORY_DB": str(db_path)}

    # Add some content to search against
    _run_cli("add", "tree-sitter and sqlite-vec", env_overrides=env)

    for query in ["tree-sitter", "c++", "NOT OR AND", 'term*']:
        stdout, stderr, code = _run_cli(
            "search", query, "--keyword", env_overrides=env,
        )
        assert code == 0, f"search crashed on query: {query}"


# --- status subcommand ---


def test_cli_status_text_output_fields(tmp_path):
    """status text output shows Chunks, Files, Last indexed, and DB fields."""
    db_path = tmp_path / "test.db"
    env = {"AGENT_MEMORY_DB": str(db_path)}

    # Add a memory so the DB exists
    _run_cli("add", "status test", env_overrides=env)

    stdout, _, code = _run_cli("status", env_overrides=env)
    assert code == 0
    assert "Chunks:" in stdout
    assert "Files:" in stdout
    assert "Last indexed:" in stdout
    assert "DB:" in stdout


def test_cli_status_json_fields(tmp_path):
    """status --json has all expected fields."""
    db_path = tmp_path / "test.db"
    env = {"AGENT_MEMORY_DB": str(db_path)}

    stdout, _, code = _run_cli("status", "--json", env_overrides=env)
    assert code == 0
    data = json.loads(stdout)
    assert "chunks" in data
    assert "files" in data
    assert "last_indexed" in data
    assert "db_path" in data
    assert "db_size_bytes" in data


def test_cli_status_reflects_add(tmp_path):
    """status shows updated counts after adding memories."""
    db_path = tmp_path / "test.db"
    env = {"AGENT_MEMORY_DB": str(db_path)}

    # Check initial count
    stdout, _, _ = _run_cli("status", "--json", env_overrides=env)
    initial = json.loads(stdout)["chunks"]

    # Add a memory
    _run_cli("add", "count test", env_overrides=env)

    # Check updated count
    stdout, _, _ = _run_cli("status", "--json", env_overrides=env)
    after = json.loads(stdout)["chunks"]
    assert after == initial + 1


# --- index subcommand ---


def test_cli_index_reports_skipped(tmp_path, sample_memory_dir):
    """index skips unchanged files on re-run and reports it."""
    db_path = tmp_path / "test.db"
    daily_dir = sample_memory_dir / "agent-memory" / "daily-logs"
    env = {"AGENT_MEMORY_DB": str(db_path)}

    # First run
    _run_cli("index", "--path", str(daily_dir), env_overrides=env)

    # Second run — files unchanged
    stdout, _, code = _run_cli("index", "--path", str(daily_dir), env_overrides=env)
    assert code == 0
    assert "skipped" in stdout.lower()


def test_cli_index_single_file(tmp_path):
    """index --path pointing to a single file indexes just that file."""
    db_path = tmp_path / "test.db"
    md_file = tmp_path / "single.md"
    md_file.write_text("# Single File\n\nThis is a single file for indexing.\n")
    env = {"AGENT_MEMORY_DB": str(db_path)}

    stdout, _, code = _run_cli("index", "--path", str(md_file), env_overrides=env)
    assert code == 0
    assert "indexed" in stdout.lower() or "Indexed" in stdout

    # Verify chunk was created
    stdout, _, _ = _run_cli("status", "--json", env_overrides=env)
    data = json.loads(stdout)
    assert data["chunks"] >= 1


# --- summarize subcommand ---


def test_cli_summarize_without_sdk(tmp_path):
    """summarize fails gracefully without Agent SDK."""
    db_path = tmp_path / "test.db"
    stdout, stderr, code = _run_cli(
        "summarize",
        env_overrides={"AGENT_MEMORY_DB": str(db_path)},
    )
    assert code != 0 or "install" in (stdout + stderr).lower()


# --- code-index subcommand ---


def test_cli_code_index_subprocess(tmp_path):
    """code-index indexes a codebase and prints stats."""
    db_path = tmp_path / "test.db"
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "hello.py").write_text("def hello():\n    return 'world'\n")
    env = {"AGENT_MEMORY_DB": str(db_path)}

    stdout, stderr, code = _run_cli(
        "code-index", str(src_dir), env_overrides=env,
    )
    assert code == 0
    assert "indexed" in stdout.lower() or "Indexed" in stdout


# --- code-tree subcommand ---


def test_cli_code_tree_empty(tmp_path):
    """code-tree on empty database shows 'no code nodes' message."""
    db_path = tmp_path / "test.db"
    env = {"AGENT_MEMORY_DB": str(db_path)}

    stdout, stderr, code = _run_cli("code-tree", env_overrides=env)
    assert code == 0
    assert "no code nodes" in stdout.lower()


def test_cli_code_tree_json_empty(tmp_path):
    """code-tree --json on empty database returns empty JSON array."""
    db_path = tmp_path / "test.db"
    env = {"AGENT_MEMORY_DB": str(db_path)}

    stdout, stderr, code = _run_cli("code-tree", "--json", env_overrides=env)
    assert code == 0
    data = json.loads(stdout)
    assert data == []


# --- code-refs subcommand ---


def test_cli_code_refs_not_found(tmp_path):
    """code-refs exits with error for non-existent node ID."""
    db_path = tmp_path / "test.db"
    env = {"AGENT_MEMORY_DB": str(db_path)}

    stdout, stderr, code = _run_cli("code-refs", "99999", env_overrides=env)
    assert code != 0
    assert "not found" in stderr.lower()


# --- code-summarize subcommand ---


def test_cli_code_summarize_empty(tmp_path):
    """code-summarize on empty database completes without error."""
    db_path = tmp_path / "test.db"
    env = {"AGENT_MEMORY_DB": str(db_path)}

    stdout, stderr, code = _run_cli("code-summarize", env_overrides=env)
    assert code == 0
    assert "summarized" in stdout.lower()


# --- error handling ---


def test_cli_search_missing_query(tmp_path):
    """search without a query argument fails with error."""
    db_path = tmp_path / "test.db"
    stdout, stderr, code = _run_cli(
        "search",
        env_overrides={"AGENT_MEMORY_DB": str(db_path)},
    )
    assert code != 0


def test_cli_get_missing_id(tmp_path):
    """get without an ID argument fails with error."""
    db_path = tmp_path / "test.db"
    stdout, stderr, code = _run_cli(
        "get",
        env_overrides={"AGENT_MEMORY_DB": str(db_path)},
    )
    assert code != 0


def test_cli_add_missing_content(tmp_path):
    """add without content argument fails with error."""
    db_path = tmp_path / "test.db"
    stdout, stderr, code = _run_cli(
        "add",
        env_overrides={"AGENT_MEMORY_DB": str(db_path)},
    )
    assert code != 0


def test_cli_code_index_missing_path(tmp_path):
    """code-index without path argument fails with error."""
    db_path = tmp_path / "test.db"
    stdout, stderr, code = _run_cli(
        "code-index",
        env_overrides={"AGENT_MEMORY_DB": str(db_path)},
    )
    assert code != 0


def test_cli_code_refs_missing_node_id(tmp_path):
    """code-refs without node_id argument fails with error."""
    db_path = tmp_path / "test.db"
    stdout, stderr, code = _run_cli(
        "code-refs",
        env_overrides={"AGENT_MEMORY_DB": str(db_path)},
    )
    assert code != 0


# --- end-to-end roundtrip ---


def test_cli_add_get_roundtrip(tmp_path):
    """Full add → get → verify roundtrip via CLI."""
    db_path = tmp_path / "test.db"
    env = {"AGENT_MEMORY_DB": str(db_path)}

    # Add
    stdout, _, code = _run_cli(
        "add", "roundtrip test content", "--source", "daily", "--tags", "test",
        env_overrides=env,
    )
    assert code == 0
    chunk_id = stdout.strip().split("Added: ")[1]

    # Get by full ID as JSON
    stdout, _, code = _run_cli("get", chunk_id, "--json", env_overrides=env)
    assert code == 0
    data = json.loads(stdout)
    assert data["text"] == "roundtrip test content"
    assert data["source"] == "daily"
    assert "test" in data["path"]

    # Verify it appears in list
    stdout, _, _ = _run_cli("list", "--source", "daily", "--json", env_overrides=env)
    data = json.loads(stdout)
    assert any(item["id"] == chunk_id for item in data)

    # Verify it appears in search
    stdout, _, _ = _run_cli("search", "roundtrip", "--keyword", "--json", env_overrides=env)
    data = json.loads(stdout)
    assert any("roundtrip" in item["text"] for item in data)


def test_cli_index_search_roundtrip(tmp_path):
    """Full index → search roundtrip via CLI."""
    db_path = tmp_path / "test.db"
    md_dir = tmp_path / "docs"
    md_dir.mkdir()
    (md_dir / "guide.md").write_text(
        "# User Guide\n\n"
        "## Authentication\n\n"
        "Use OAuth2 for authentication with JWT tokens.\n"
        "Configure the client_id and client_secret in settings.\n"
    )
    env = {"AGENT_MEMORY_DB": str(db_path)}

    # Index
    stdout, _, code = _run_cli("index", "--path", str(md_dir), env_overrides=env)
    assert code == 0

    # Search should find the content
    stdout, _, code = _run_cli(
        "search", "OAuth authentication", "--json", env_overrides=env,
    )
    assert code == 0
    data = json.loads(stdout)
    assert len(data) >= 1
    assert any("OAuth" in item["text"] or "authentication" in item["text"].lower() for item in data)
