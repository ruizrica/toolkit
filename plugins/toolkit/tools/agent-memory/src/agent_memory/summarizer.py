# ABOUTME: Bottom-up summary generation for code nodes.
# ABOUTME: Uses fallback auto-summary (signature + docstring); optional LLM enhancement.

import sqlite3


def generate_fallback_summary(
    name: str,
    node_type: str,
    signature: str,
    docstring: str,
) -> str:
    """Generate a summary from signature and docstring without LLM.

    Produces a concise one-line description suitable for FTS indexing.
    """
    parts = []
    if node_type == "class":
        parts.append(f"Class {name}")
    elif node_type == "function":
        parts.append(f"Function {name}")
    elif node_type == "interface":
        parts.append(f"Interface {name}")
    elif node_type == "type_alias":
        parts.append(f"Type {name}")
    else:
        parts.append(f"{node_type} {name}")

    if docstring:
        # Use first sentence of docstring
        first_sentence = docstring.split(".")[0].strip()
        if first_sentence:
            parts.append(f"- {first_sentence}")
    elif signature and signature != name:
        parts.append(f"({signature})")

    return " ".join(parts)


def summarize_nodes(
    conn: sqlite3.Connection,
    use_llm: bool = False,
) -> int:
    """Generate summaries for all code nodes bottom-up (leaves first).

    Updates the summary column in code_nodes and refreshes FTS entries.
    Returns the number of nodes summarized.
    """
    # Get all nodes ordered by depth descending (leaves first)
    cursor = conn.execute(
        "SELECT id, name, node_type, signature, docstring, depth "
        "FROM code_nodes ORDER BY depth DESC, id"
    )
    rows = cursor.fetchall()

    count = 0
    for row in rows:
        node_id, name, node_type, signature, docstring, depth = row

        summary = generate_fallback_summary(name, node_type, signature, docstring)

        # For parent nodes, append child summary info
        child_cursor = conn.execute(
            "SELECT name, summary FROM code_nodes WHERE parent_id = ? "
            "ORDER BY start_line",
            (node_id,),
        )
        children = child_cursor.fetchall()
        if children:
            child_names = [c[0] for c in children]
            summary += f". Contains: {', '.join(child_names)}"

        # Update the node
        conn.execute(
            "UPDATE code_nodes SET summary = ? WHERE id = ?",
            (summary, node_id),
        )

        count += 1

    # Rebuild FTS index to reflect updated summaries
    _rebuild_code_fts(conn)

    conn.commit()
    return count


def _rebuild_code_fts(conn: sqlite3.Connection) -> None:
    """Rebuild the code_nodes_fts index from the code_nodes table."""
    conn.execute(
        "INSERT INTO code_nodes_fts(code_nodes_fts) VALUES('rebuild')"
    )
