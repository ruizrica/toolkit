# ABOUTME: Tree-sitter-based extraction of code structure (classes, functions, imports).
# ABOUTME: Produces CodeNode trees from source files for any supported language.

import hashlib
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class CodeNode:
    """A structural element extracted from source code."""
    name: str
    qualified_name: str
    node_type: str  # "class", "function", "import", "interface", "type_alias"
    file_path: str
    start_line: int
    end_line: int
    signature: str = ""
    docstring: str = ""
    body_hash: str = ""
    children: list["CodeNode"] = field(default_factory=list)
    refs: list[dict] = field(default_factory=list)


# Extension → tree-sitter language name
_EXTENSION_MAP: dict[str, str] = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".rs": "rust",
    ".go": "go",
    ".java": "java",
    ".rb": "ruby",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c",
    ".hpp": "cpp",
    ".cs": "c_sharp",
    ".swift": "swift",
    ".kt": "kotlin",
    ".lua": "lua",
    ".sh": "bash",
    ".bash": "bash",
}


def detect_language(file_path: str) -> str | None:
    """Detect programming language from file extension.

    Returns the tree-sitter language name or None if unsupported.
    """
    from pathlib import Path
    suffix = Path(file_path).suffix.lower()
    return _EXTENSION_MAP.get(suffix)


def _body_hash(source: bytes, start_byte: int, end_byte: int) -> str:
    """Compute SHA-256 hash of a node's body text."""
    body = source[start_byte:end_byte]
    return hashlib.sha256(body).hexdigest()[:16]


def _get_node_text(node, source: bytes) -> str:
    """Extract the text of a tree-sitter node."""
    return source[node.start_byte:node.end_byte].decode("utf-8", errors="replace")


def _find_child_by_type(node, type_name: str):
    """Find first child of a given type."""
    for child in node.children:
        if child.type == type_name:
            return child
    return None


def _find_children_by_type(node, type_name: str) -> list:
    """Find all children of a given type."""
    return [c for c in node.children if c.type == type_name]


def _extract_name(node, source: bytes) -> str:
    """Extract the name identifier from a definition node."""
    name_node = _find_child_by_type(node, "identifier")
    if name_node is None:
        name_node = _find_child_by_type(node, "property_identifier")
    if name_node is None:
        name_node = _find_child_by_type(node, "type_identifier")
    if name_node:
        return _get_node_text(name_node, source)
    return ""


def _extract_signature(node, source: bytes) -> str:
    """Extract the first line of a definition as its signature."""
    text = _get_node_text(node, source)
    # For decorated definitions, find the actual def/class line
    lines = text.split("\n")
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("def ", "async def ", "class ", "function ",
                                "interface ", "type ", "export ", "const ")):
            return stripped.rstrip("{").rstrip(":").strip()
    return lines[0].strip()


def _extract_string_content(string_node, source: bytes) -> str:
    """Extract text content from a tree-sitter string node.

    Handles both old-style flat string nodes and new-style nodes with
    string_start/string_content/string_end children.
    """
    # New tree-sitter: string has string_content child
    content_child = _find_child_by_type(string_node, "string_content")
    if content_child:
        return _get_node_text(content_child, source).strip()
    # Old tree-sitter: string is flat text with quotes
    raw = _get_node_text(string_node, source)
    for q in ('"""', "'''"):
        if raw.startswith(q) and raw.endswith(q):
            return raw[3:-3].strip()
    for q in ('"', "'"):
        if raw.startswith(q) and raw.endswith(q):
            return raw[1:-1].strip()
    return raw


def _extract_python_docstring(node, source: bytes) -> str:
    """Extract docstring from a Python class or function body."""
    body = _find_child_by_type(node, "block")
    if body is None:
        return ""
    for child in body.children:
        if child.type == "expression_statement":
            string_node = child.children[0] if child.children else None
            if string_node and string_node.type == "string":
                return _extract_string_content(string_node, source)
        elif child.type == "string":
            # Newer tree-sitter grammars put docstrings directly in block
            return _extract_string_content(child, source)
        elif child.type not in ("comment", "newline"):
            break
    return ""


def _extract_python_nodes(
    tree_node, source: bytes, file_path: str, prefix: str = ""
) -> list[CodeNode]:
    """Walk a tree-sitter Python AST and extract structural nodes."""
    nodes: list[CodeNode] = []

    for child in tree_node.children:
        if child.type in ("function_definition", "decorated_definition"):
            actual = child
            if child.type == "decorated_definition":
                # The actual definition is the last child
                for sub in child.children:
                    if sub.type in ("function_definition", "class_definition"):
                        actual = sub
                        break

            if actual.type == "class_definition":
                # Decorated class — handle below
                name = _extract_name(actual, source)
                qname = f"{prefix}{name}" if not prefix else f"{prefix}.{name}"
                sig = _extract_signature(child, source)
                doc = _extract_python_docstring(actual, source)
                bhash = _body_hash(source, child.start_byte, child.end_byte)
                children = _extract_python_nodes(actual, source, file_path, qname)
                # Only keep methods and nested classes
                body_children = []
                body = _find_child_by_type(actual, "block")
                if body:
                    body_children = _extract_python_nodes(
                        body, source, file_path, qname
                    )
                nodes.append(CodeNode(
                    name=name, qualified_name=qname, node_type="class",
                    file_path=file_path,
                    start_line=child.start_point[0] + 1,
                    end_line=child.end_point[0] + 1,
                    signature=sig, docstring=doc, body_hash=bhash,
                    children=body_children,
                ))
                continue

            name = _extract_name(actual, source)
            if not name:
                continue
            qname = f"{prefix}.{name}" if prefix else name
            sig = _extract_signature(child, source)
            doc = _extract_python_docstring(actual, source)
            bhash = _body_hash(source, child.start_byte, child.end_byte)
            nodes.append(CodeNode(
                name=name, qualified_name=qname, node_type="function",
                file_path=file_path,
                start_line=child.start_point[0] + 1,
                end_line=child.end_point[0] + 1,
                signature=sig, docstring=doc, body_hash=bhash,
            ))

        elif child.type == "class_definition":
            name = _extract_name(child, source)
            if not name:
                continue
            qname = f"{prefix}.{name}" if prefix else name
            sig = _extract_signature(child, source)
            doc = _extract_python_docstring(child, source)
            bhash = _body_hash(source, child.start_byte, child.end_byte)
            # Recurse into class body for methods and nested classes
            body = _find_child_by_type(child, "block")
            body_children = []
            if body:
                body_children = _extract_python_nodes(
                    body, source, file_path, qname
                )
            nodes.append(CodeNode(
                name=name, qualified_name=qname, node_type="class",
                file_path=file_path,
                start_line=child.start_point[0] + 1,
                end_line=child.end_point[0] + 1,
                signature=sig, docstring=doc, body_hash=bhash,
                children=body_children,
            ))

        elif child.type in ("import_statement", "import_from_statement"):
            text = _get_node_text(child, source)
            nodes.append(CodeNode(
                name=text.strip(), qualified_name=text.strip(),
                node_type="import", file_path=file_path,
                start_line=child.start_point[0] + 1,
                end_line=child.end_point[0] + 1,
                signature=text.strip(),
                body_hash=_body_hash(source, child.start_byte, child.end_byte),
            ))

    return nodes


def _extract_ts_nodes(
    tree_node, source: bytes, file_path: str, prefix: str = ""
) -> list[CodeNode]:
    """Walk a tree-sitter TypeScript/JavaScript AST and extract structural nodes."""
    nodes: list[CodeNode] = []

    for child in tree_node.children:
        # Export wrappers
        if child.type == "export_statement":
            inner = _extract_ts_nodes(child, source, file_path, prefix)
            nodes.extend(inner)
            continue

        if child.type == "function_declaration":
            name = _extract_name(child, source)
            if not name:
                continue
            qname = f"{prefix}.{name}" if prefix else name
            sig = _extract_signature(child, source)
            bhash = _body_hash(source, child.start_byte, child.end_byte)
            nodes.append(CodeNode(
                name=name, qualified_name=qname, node_type="function",
                file_path=file_path,
                start_line=child.start_point[0] + 1,
                end_line=child.end_point[0] + 1,
                signature=sig, body_hash=bhash,
            ))

        elif child.type == "class_declaration":
            name = _extract_name(child, source)
            if not name:
                # Try type_identifier for TS classes
                ti = _find_child_by_type(child, "type_identifier")
                if ti:
                    name = _get_node_text(ti, source)
            if not name:
                continue
            qname = f"{prefix}.{name}" if prefix else name
            sig = _extract_signature(child, source)
            bhash = _body_hash(source, child.start_byte, child.end_byte)
            # Recurse into class body
            body = _find_child_by_type(child, "class_body")
            body_children = []
            if body:
                body_children = _extract_ts_class_members(
                    body, source, file_path, qname
                )
            nodes.append(CodeNode(
                name=name, qualified_name=qname, node_type="class",
                file_path=file_path,
                start_line=child.start_point[0] + 1,
                end_line=child.end_point[0] + 1,
                signature=sig, body_hash=bhash,
                children=body_children,
            ))

        elif child.type in ("interface_declaration",):
            name = _extract_name(child, source)
            if not name:
                ti = _find_child_by_type(child, "type_identifier")
                if ti:
                    name = _get_node_text(ti, source)
            if not name:
                continue
            qname = f"{prefix}.{name}" if prefix else name
            sig = _extract_signature(child, source)
            bhash = _body_hash(source, child.start_byte, child.end_byte)
            nodes.append(CodeNode(
                name=name, qualified_name=qname, node_type="interface",
                file_path=file_path,
                start_line=child.start_point[0] + 1,
                end_line=child.end_point[0] + 1,
                signature=sig, body_hash=bhash,
            ))

        elif child.type == "type_alias_declaration":
            name = _extract_name(child, source)
            if not name:
                ti = _find_child_by_type(child, "type_identifier")
                if ti:
                    name = _get_node_text(ti, source)
            if not name:
                continue
            qname = f"{prefix}.{name}" if prefix else name
            sig = _extract_signature(child, source)
            bhash = _body_hash(source, child.start_byte, child.end_byte)
            nodes.append(CodeNode(
                name=name, qualified_name=qname, node_type="type_alias",
                file_path=file_path,
                start_line=child.start_point[0] + 1,
                end_line=child.end_point[0] + 1,
                signature=sig, body_hash=bhash,
            ))

        elif child.type in ("import_statement",):
            text = _get_node_text(child, source)
            nodes.append(CodeNode(
                name=text.strip(), qualified_name=text.strip(),
                node_type="import", file_path=file_path,
                start_line=child.start_point[0] + 1,
                end_line=child.end_point[0] + 1,
                signature=text.strip(),
                body_hash=_body_hash(source, child.start_byte, child.end_byte),
            ))

        elif child.type in ("lexical_declaration",):
            # const/let/var with arrow functions
            for decl in child.children:
                if decl.type == "variable_declarator":
                    name_node = _find_child_by_type(decl, "identifier")
                    if not name_node:
                        continue
                    # Check if value is arrow function
                    value = None
                    for sub in decl.children:
                        if sub.type == "arrow_function":
                            value = sub
                            break
                    if value:
                        name = _get_node_text(name_node, source)
                        qname = f"{prefix}.{name}" if prefix else name
                        sig = _extract_signature(child, source)
                        bhash = _body_hash(source, child.start_byte, child.end_byte)
                        nodes.append(CodeNode(
                            name=name, qualified_name=qname, node_type="function",
                            file_path=file_path,
                            start_line=child.start_point[0] + 1,
                            end_line=child.end_point[0] + 1,
                            signature=sig, body_hash=bhash,
                        ))

    return nodes


def _extract_ts_class_members(
    body_node, source: bytes, file_path: str, prefix: str
) -> list[CodeNode]:
    """Extract methods and properties from a TypeScript/JS class body."""
    members: list[CodeNode] = []
    for child in body_node.children:
        if child.type in ("method_definition", "public_field_definition"):
            name = _extract_name(child, source)
            if not name:
                # Try property_identifier
                pi = _find_child_by_type(child, "property_identifier")
                if pi:
                    name = _get_node_text(pi, source)
            if not name:
                continue
            qname = f"{prefix}.{name}"
            sig = _get_node_text(child, source).split("\n")[0].strip()
            bhash = _body_hash(source, child.start_byte, child.end_byte)
            members.append(CodeNode(
                name=name, qualified_name=qname, node_type="function",
                file_path=file_path,
                start_line=child.start_point[0] + 1,
                end_line=child.end_point[0] + 1,
                signature=sig, body_hash=bhash,
            ))
    return members


# Language → extraction function
_EXTRACTORS: dict[str, callable] = {
    "python": _extract_python_nodes,
    "typescript": _extract_ts_nodes,
    "javascript": _extract_ts_nodes,  # JS uses same AST structure
}


def parse_file(
    source: bytes, file_path: str, language: str | None = None
) -> list[CodeNode]:
    """Parse a source file and extract structural code nodes.

    Auto-detects language from file extension if not provided.
    Returns empty list for unsupported or empty files.
    """
    if not source:
        return []

    if language is None:
        language = detect_language(file_path)
    if language is None:
        return []

    extractor = _EXTRACTORS.get(language)
    if extractor is None:
        return []

    try:
        from tree_sitter_language_pack import get_parser
    except ImportError:
        logger.warning(
            "tree-sitter-language-pack is not installed. "
            "Code parsing will be skipped. "
            "Install with: pip install tree-sitter-language-pack"
        )
        return []

    parser = get_parser(language)
    tree = parser.parse(source)

    return extractor(tree.root_node, source, file_path)
