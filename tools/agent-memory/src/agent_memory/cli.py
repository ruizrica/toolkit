# ABOUTME: CLI entry point for agent-memory — fast argparse with lazy imports.
# ABOUTME: All heavy imports (fastembed, sqlite-vec) are deferred to subcommand handlers.

import argparse
import json
import sys


def _build_parser() -> argparse.ArgumentParser:
    """Build the argparse parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="agent-memory",
        description="Local hybrid search memory system for Claude Code",
    )
    sub = parser.add_subparsers(dest="command")

    # search
    p_search = sub.add_parser("search", help="Search memories")
    p_search.add_argument("query", help="Search query text")
    p_search.add_argument("--vector", action="store_true", help="Vector-only search")
    p_search.add_argument("--keyword", action="store_true", help="BM25-only search")
    p_search.add_argument("--limit", type=int, default=5, help="Max results")
    p_search.add_argument("--json", action="store_true", dest="as_json", help="JSON output")

    # index
    p_index = sub.add_parser("index", help="Index memory files")
    p_index.add_argument("--path", help="Specific path to index (glob: *.md)")

    # status
    p_status = sub.add_parser("status", help="Show database status")
    p_status.add_argument("--json", action="store_true", dest="as_json", help="JSON output")

    # add
    p_add = sub.add_parser("add", help="Add a memory")
    p_add.add_argument("content", help="Memory content text")
    p_add.add_argument("--tags", default="", help="Comma-separated tags")
    p_add.add_argument("--source", default="manual", help="Source type")

    # get
    p_get = sub.add_parser("get", help="Get a memory by ID")
    p_get.add_argument("id", help="Chunk ID")
    p_get.add_argument("--json", action="store_true", dest="as_json", help="JSON output")

    # list
    p_list = sub.add_parser("list", help="List memories")
    p_list.add_argument("--source", help="Filter by source type")
    p_list.add_argument("--limit", type=int, default=20, help="Max results")
    p_list.add_argument("--json", action="store_true", dest="as_json", help="JSON output")

    # ask (intelligence)
    p_ask = sub.add_parser("ask", help="Ask a question about your memories")
    p_ask.add_argument("question", help="Question to ask")

    # summarize (intelligence)
    sub.add_parser("summarize", help="Summarize daily logs into MEMORY.md")

    # install
    sub.add_parser("install", help="Download embedding model")

    return parser


def cmd_status(args) -> None:
    """Show database status — fast path, no embedder needed."""
    from .config import get_db_path
    from .db import init_db, meta_get

    db_path = get_db_path()
    conn = init_db(db_path)

    chunk_count = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    file_count = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
    last_indexed = meta_get(conn, "last_indexed", "never")
    db_size = db_path.stat().st_size if db_path.exists() else 0

    conn.close()

    info = {
        "chunks": chunk_count,
        "files": file_count,
        "last_indexed": last_indexed,
        "db_path": str(db_path),
        "db_size_bytes": db_size,
    }

    if getattr(args, "as_json", False):
        print(json.dumps(info, indent=2))
    else:
        print(f"Chunks: {chunk_count}")
        print(f"Files:  {file_count}")
        print(f"Last indexed: {last_indexed}")
        print(f"DB: {db_path} ({db_size:,} bytes)")


def cmd_index(args) -> None:
    """Index memory files."""
    from .config import get_db_path, get_scan_patterns
    from .db import init_db, meta_set
    from .indexer import index_all

    import datetime

    conn = init_db(get_db_path())

    if args.path:
        from pathlib import Path
        p = Path(args.path)
        if p.is_dir():
            patterns = [str(p / "*.md")]
        else:
            patterns = [str(p)]
    else:
        patterns = get_scan_patterns()

    stats = index_all(conn, patterns)
    meta_set(conn, "last_indexed", datetime.datetime.now().isoformat())
    conn.close()

    print(f"Indexed {stats.files_indexed} files, {stats.chunks_created} chunks")
    if stats.files_skipped:
        print(f"Skipped {stats.files_skipped} unchanged files")


def cmd_search(args) -> None:
    """Search memories."""
    from .config import get_db_path
    from .db import init_db

    conn = init_db(get_db_path())

    if args.keyword:
        from .search import search_keyword
        results = search_keyword(conn, args.query, limit=args.limit)
    elif args.vector:
        from .search import search_vector
        results = search_vector(conn, args.query, limit=args.limit)
    else:
        from .search import search_hybrid
        results = search_hybrid(conn, args.query, limit=args.limit)

    conn.close()

    if args.as_json:
        data = [
            {
                "id": r.chunk_id,
                "text": r.text,
                "path": r.path,
                "source": r.source,
                "score": round(r.score, 4),
                "start_line": r.start_line,
                "end_line": r.end_line,
            }
            for r in results
        ]
        print(json.dumps(data, indent=2))
    else:
        if not results:
            print("No results found.")
        for r in results:
            print(f"[{r.score:.3f}] {r.source}:{r.path}")
            print(f"  {r.text[:120]}...")
            print()


def cmd_add(args) -> None:
    """Add a memory."""
    from .config import get_db_path
    from .crud import add_memory
    from .db import init_db

    conn = init_db(get_db_path())
    chunk_id = add_memory(conn, args.content, source=args.source, tags=args.tags)
    conn.close()
    print(f"Added: {chunk_id[:12]}...")


def cmd_get(args) -> None:
    """Get a memory by ID."""
    from .config import get_db_path
    from .crud import get_memory
    from .db import init_db

    conn = init_db(get_db_path())
    result = get_memory(conn, args.id)
    conn.close()

    if result is None:
        print(f"Not found: {args.id}", file=sys.stderr)
        sys.exit(1)

    if getattr(args, "as_json", False):
        print(json.dumps(result, indent=2))
    else:
        print(f"ID: {result['id']}")
        print(f"Source: {result['source']}")
        print(f"Text: {result['text']}")


def cmd_list(args) -> None:
    """List memories."""
    from .config import get_db_path
    from .crud import list_memories
    from .db import init_db

    conn = init_db(get_db_path())
    results = list_memories(conn, source=args.source, limit=args.limit)
    conn.close()

    if args.as_json:
        print(json.dumps(results, indent=2))
    else:
        if not results:
            print("No memories found.")
        for r in results:
            print(f"[{r['source']}] {r['id'][:12]}... {r['text'][:80]}")


def cmd_ask(args) -> None:
    """Ask a question about memories (requires Agent SDK)."""
    try:
        from .intelligence import ask_memories
    except ImportError:
        print(
            "Install claude-agent-sdk for intelligence features: "
            "pip install agent-memory[intelligence]",
            file=sys.stderr,
        )
        sys.exit(1)
    ask_memories(args.question)


def cmd_summarize(args) -> None:
    """Summarize daily logs (requires Agent SDK)."""
    try:
        from .intelligence import summarize_daily_logs
    except ImportError:
        print(
            "Install claude-agent-sdk for intelligence features: "
            "pip install agent-memory[intelligence]",
            file=sys.stderr,
        )
        sys.exit(1)
    summarize_daily_logs()


def cmd_install(args) -> None:
    """Download the embedding model."""
    print("Downloading embedding model...")
    from .embedder import _get_model
    _get_model()
    print("Model ready.")


def main() -> None:
    """CLI entry point."""
    parser = _build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    commands = {
        "search": cmd_search,
        "index": cmd_index,
        "status": cmd_status,
        "add": cmd_add,
        "get": cmd_get,
        "list": cmd_list,
        "ask": cmd_ask,
        "summarize": cmd_summarize,
        "install": cmd_install,
    }

    handler = commands.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()
