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

    # code-index
    p_ci = sub.add_parser("code-index", help="Index a codebase for tree navigation")
    p_ci.add_argument("path", help="Root path of the codebase to index")

    # code-nav
    p_cn = sub.add_parser("code-nav", help="Navigate code tree to find relevant code")
    p_cn.add_argument("query", help="Search query for navigation")
    p_cn.add_argument("--json", action="store_true", dest="as_json", help="JSON output")

    # code-tree
    p_ct = sub.add_parser("code-tree", help="Display code tree structure")
    p_ct.add_argument("path", nargs="?", default=None, help="Filter by file path")
    p_ct.add_argument("--json", action="store_true", dest="as_json", help="JSON output")

    # code-refs
    p_cr = sub.add_parser("code-refs", help="Show cross-references for a code node")
    p_cr.add_argument("node_id", help="Node ID to show references for")
    p_cr.add_argument("--json", action="store_true", dest="as_json", help="JSON output")

    # code-summarize
    sub.add_parser("code-summarize", help="Generate summaries for indexed code nodes")

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
    print(f"Added: {chunk_id}")


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


def cmd_code_index(args) -> None:
    """Index a codebase for tree navigation."""
    from .code_indexer import index_codebase
    from .config import get_db_path
    from .db import init_db

    conn = init_db(get_db_path())
    stats = index_codebase(conn, args.path)
    conn.close()

    print(f"Indexed {stats.files_indexed} files, {stats.nodes_created} nodes")
    if stats.files_skipped:
        print(f"Skipped {stats.files_skipped} unchanged files")
    if stats.files_indexed > 0 and stats.nodes_created == 0:
        print(
            "Warning: No code nodes were extracted. "
            "Is tree-sitter-language-pack installed? "
            "Install with: pip install tree-sitter-language-pack",
            file=sys.stderr,
        )


def cmd_code_nav(args) -> None:
    """Navigate code tree to find relevant code."""
    from .config import get_db_path
    from .db import init_db
    from .navigator import format_navigation_result, navigate

    conn = init_db(get_db_path())
    result = navigate(conn, args.query)
    conn.close()

    if getattr(args, "as_json", False):
        data = {
            "nodes": result.nodes,
            "steps": [
                {
                    "depth": s.depth,
                    "candidates": s.candidates,
                    "selected": s.selected,
                }
                for s in result.steps
            ],
        }
        print(json.dumps(data, indent=2))
    else:
        print(format_navigation_result(result))


def cmd_code_tree(args) -> None:
    """Display code tree structure."""
    from .config import get_db_path
    from .db import init_db
    from .tree import get_children, get_roots

    conn = init_db(get_db_path())
    roots = get_roots(conn)

    if getattr(args, "as_json", False):
        def _tree_to_dict(node_dict):
            children = get_children(conn, node_dict["id"])
            node_dict["children"] = [_tree_to_dict(c) for c in children]
            return node_dict

        tree_data = [_tree_to_dict(r) for r in roots]
        print(json.dumps(tree_data, indent=2))
    else:
        def _print_tree(node_dict, indent=0):
            prefix = "  " * indent
            ntype = node_dict.get("node_type", "?")
            name = node_dict.get("name", "?")
            file_path = node_dict.get("file_path", "")
            line = node_dict.get("start_line", "")
            print(f"{prefix}[{ntype}] {name}  ({file_path}:{line})")
            children = get_children(conn, node_dict["id"])
            for child in children:
                _print_tree(child, indent + 1)

        if not roots:
            print("No code nodes indexed.")
        for root in roots:
            _print_tree(root)

    conn.close()


def cmd_code_refs(args) -> None:
    """Show cross-references for a code node."""
    from .config import get_db_path
    from .db import init_db
    from .tree import get_node, resolve_refs

    conn = init_db(get_db_path())
    node_id = int(args.node_id)

    node = get_node(conn, node_id)
    if node is None:
        print(f"Node not found: {node_id}", file=sys.stderr)
        conn.close()
        sys.exit(1)

    refs = resolve_refs(conn, node_id)
    conn.close()

    if getattr(args, "as_json", False):
        print(json.dumps(refs, indent=2))
    else:
        if not refs:
            print(f"No references from {node['name']}.")
        for ref in refs:
            target = ref.get("target_name", "?")
            ref_type = ref.get("ref_type", "?")
            line = ref.get("line", "?")
            print(f"  [{ref_type}] {target} (line {line})")


def cmd_code_summarize(args) -> None:
    """Generate summaries for indexed code nodes."""
    from .config import get_db_path
    from .db import init_db
    from .summarizer import summarize_nodes

    conn = init_db(get_db_path())
    count = summarize_nodes(conn)
    conn.close()

    print(f"Summarized {count} code nodes")


LOGO = r"""
▄██████▄ ▄████▄  ▄██████▄ ▄████▄ ██▄███ ██  ██
██ ██ ██ ██▄▄██  ██ ██ ██ ██  ██ ██▀▀   ██  ██
██ ██ ██ ██▄▄▄▄  ██ ██ ██ ██▄▄██ ██     ██▄▄██
▀▀ ▀▀ ▀▀  ▀▀▀▀▀  ▀▀ ▀▀ ▀▀  ▀▀▀▀  ▀▀      ▀▀▀██
                                         ████▀

Created by Ricardo Ruiz - 2026
ruizrica.io
""".strip()


def main() -> None:
    """CLI entry point."""
    parser = _build_parser()
    args = parser.parse_args()

    if args.command is None:
        print(LOGO)
        print()
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
        "code-index": cmd_code_index,
        "code-nav": cmd_code_nav,
        "code-tree": cmd_code_tree,
        "code-refs": cmd_code_refs,
        "code-summarize": cmd_code_summarize,
    }

    handler = commands.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()
