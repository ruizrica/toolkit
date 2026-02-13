# ABOUTME: Tests for parser module — tree-sitter-based code structure extraction.
# ABOUTME: Verifies language detection, Python/TS parsing, nested structures, and edge cases.

import pytest


# --- Language detection ---

def test_detect_language_python():
    """Detects Python from .py extension."""
    from agent_memory.parser import detect_language
    assert detect_language("src/main.py") == "python"


def test_detect_language_typescript():
    """Detects TypeScript from .ts and .tsx extensions."""
    from agent_memory.parser import detect_language
    assert detect_language("src/app.ts") == "typescript"
    assert detect_language("src/App.tsx") == "typescript"


def test_detect_language_javascript():
    """Detects JavaScript from .js and .jsx extensions."""
    from agent_memory.parser import detect_language
    assert detect_language("src/index.js") == "javascript"
    assert detect_language("src/App.jsx") == "javascript"


def test_detect_language_rust():
    """Detects Rust from .rs extension."""
    from agent_memory.parser import detect_language
    assert detect_language("src/main.rs") == "rust"


def test_detect_language_go():
    """Detects Go from .go extension."""
    from agent_memory.parser import detect_language
    assert detect_language("main.go") == "go"


def test_detect_language_unknown():
    """Returns None for unsupported extensions."""
    from agent_memory.parser import detect_language
    assert detect_language("file.xyz") is None
    assert detect_language("Makefile") is None


# --- CodeNode dataclass ---

def test_code_node_fields():
    """CodeNode has all required fields."""
    from agent_memory.parser import CodeNode
    node = CodeNode(
        name="MyClass",
        qualified_name="module.MyClass",
        node_type="class",
        file_path="src/main.py",
        start_line=1,
        end_line=10,
        signature="class MyClass:",
        docstring="A test class.",
        body_hash="abc123",
    )
    assert node.name == "MyClass"
    assert node.qualified_name == "module.MyClass"
    assert node.node_type == "class"
    assert node.children == []
    assert node.refs == []


# --- Python parsing ---

def test_parse_python_function():
    """Parses a simple Python function."""
    from agent_memory.parser import parse_file
    source = b'''def hello(name: str) -> str:
    """Greet someone."""
    return f"Hello, {name}!"
'''
    nodes = parse_file(source, "test.py")
    assert len(nodes) == 1
    assert nodes[0].name == "hello"
    assert nodes[0].node_type == "function"
    assert "hello" in nodes[0].signature
    assert nodes[0].docstring == "Greet someone."


def test_parse_python_class_with_methods():
    """Parses a Python class with methods."""
    from agent_memory.parser import parse_file
    source = b'''class Calculator:
    """A simple calculator."""

    def add(self, a, b):
        """Add two numbers."""
        return a + b

    def subtract(self, a, b):
        return a - b
'''
    nodes = parse_file(source, "calc.py")
    assert len(nodes) == 1
    cls = nodes[0]
    assert cls.name == "Calculator"
    assert cls.node_type == "class"
    assert cls.docstring == "A simple calculator."
    assert len(cls.children) == 2
    assert cls.children[0].name == "add"
    assert cls.children[0].node_type == "function"
    assert cls.children[0].docstring == "Add two numbers."
    assert cls.children[1].name == "subtract"


def test_parse_python_nested_class():
    """Parses nested class definitions."""
    from agent_memory.parser import parse_file
    source = b'''class Outer:
    class Inner:
        def method(self):
            pass
'''
    nodes = parse_file(source, "nested.py")
    assert len(nodes) == 1
    outer = nodes[0]
    assert outer.name == "Outer"
    assert len(outer.children) == 1
    inner = outer.children[0]
    assert inner.name == "Inner"
    assert inner.node_type == "class"
    assert len(inner.children) == 1
    assert inner.children[0].name == "method"


def test_parse_python_imports():
    """Parses Python import statements."""
    from agent_memory.parser import parse_file
    source = b'''import os
from pathlib import Path
from typing import Optional, List
'''
    nodes = parse_file(source, "imports.py")
    import_nodes = [n for n in nodes if n.node_type == "import"]
    assert len(import_nodes) >= 2


def test_parse_python_async_function():
    """Parses async function definitions."""
    from agent_memory.parser import parse_file
    source = b'''async def fetch_data(url: str) -> dict:
    """Fetch data from URL."""
    pass
'''
    nodes = parse_file(source, "async_test.py")
    assert len(nodes) == 1
    assert nodes[0].name == "fetch_data"
    assert nodes[0].node_type == "function"
    assert "async" in nodes[0].signature


def test_parse_python_decorated_function():
    """Parses decorated function definitions."""
    from agent_memory.parser import parse_file
    source = b'''@staticmethod
def my_static():
    pass

@property
def name(self):
    return self._name
'''
    nodes = parse_file(source, "decorated.py")
    assert len(nodes) == 2
    assert nodes[0].name == "my_static"
    assert nodes[1].name == "name"


def test_parse_python_line_numbers():
    """Verifies correct start/end line numbers."""
    from agent_memory.parser import parse_file
    source = b'''# comment

def first():
    pass

def second():
    x = 1
    y = 2
    return x + y
'''
    nodes = parse_file(source, "lines.py")
    funcs = [n for n in nodes if n.node_type == "function"]
    assert len(funcs) == 2
    assert funcs[0].start_line == 3
    assert funcs[1].start_line == 6
    assert funcs[1].end_line == 9


def test_parse_python_body_hash():
    """Each node has a non-empty body_hash."""
    from agent_memory.parser import parse_file
    source = b'''def foo():
    return 42
'''
    nodes = parse_file(source, "hash_test.py")
    assert nodes[0].body_hash
    assert len(nodes[0].body_hash) > 0


# --- TypeScript parsing ---

def test_parse_typescript_function():
    """Parses a TypeScript function declaration."""
    from agent_memory.parser import parse_file
    source = b'''function greet(name: string): string {
    return `Hello, ${name}!`;
}
'''
    nodes = parse_file(source, "greet.ts")
    funcs = [n for n in nodes if n.node_type == "function"]
    assert len(funcs) == 1
    assert funcs[0].name == "greet"


def test_parse_typescript_class():
    """Parses a TypeScript class with methods."""
    from agent_memory.parser import parse_file
    source = b'''class UserService {
    constructor(private db: Database) {}

    async getUser(id: string): Promise<User> {
        return this.db.find(id);
    }
}
'''
    nodes = parse_file(source, "service.ts")
    classes = [n for n in nodes if n.node_type == "class"]
    assert len(classes) == 1
    assert classes[0].name == "UserService"
    methods = classes[0].children
    assert len(methods) >= 1


def test_parse_typescript_interface():
    """Parses TypeScript interface declarations."""
    from agent_memory.parser import parse_file
    source = b'''interface User {
    id: string;
    name: string;
    email?: string;
}
'''
    nodes = parse_file(source, "types.ts")
    ifaces = [n for n in nodes if n.node_type == "interface"]
    assert len(ifaces) == 1
    assert ifaces[0].name == "User"


def test_parse_typescript_type_alias():
    """Parses TypeScript type alias declarations."""
    from agent_memory.parser import parse_file
    source = b'''type Result<T> = {
    data: T;
    error?: string;
};
'''
    nodes = parse_file(source, "types.ts")
    types = [n for n in nodes if n.node_type == "type_alias"]
    assert len(types) == 1
    assert types[0].name == "Result"


def test_parse_typescript_arrow_function():
    """Parses exported arrow functions (variable declarations)."""
    from agent_memory.parser import parse_file
    source = b'''const add = (a: number, b: number): number => a + b;

export const multiply = (a: number, b: number): number => {
    return a * b;
};
'''
    nodes = parse_file(source, "funcs.ts")
    funcs = [n for n in nodes if n.node_type == "function"]
    assert len(funcs) >= 1


def test_parse_typescript_imports():
    """Parses TypeScript import statements."""
    from agent_memory.parser import parse_file
    source = b'''import { Router } from 'express';
import type { Request, Response } from 'express';
'''
    nodes = parse_file(source, "imports.ts")
    imports = [n for n in nodes if n.node_type == "import"]
    assert len(imports) >= 1


# --- Auto language detection ---

def test_parse_file_auto_detects_language():
    """parse_file auto-detects language from file extension."""
    from agent_memory.parser import parse_file
    source = b'''def auto_detected():
    pass
'''
    nodes = parse_file(source, "auto.py")
    assert len(nodes) == 1
    assert nodes[0].name == "auto_detected"


def test_parse_file_unsupported_language():
    """parse_file returns empty list for unsupported languages."""
    from agent_memory.parser import parse_file
    nodes = parse_file(b"some content", "file.xyz")
    assert nodes == []


def test_parse_file_empty_source():
    """parse_file handles empty source gracefully."""
    from agent_memory.parser import parse_file
    nodes = parse_file(b"", "empty.py")
    assert nodes == []


# --- Qualified names ---

def test_qualified_names_nested():
    """Nested nodes get qualified names with dot-separated path."""
    from agent_memory.parser import parse_file
    source = b'''class MyClass:
    def my_method(self):
        pass
'''
    nodes = parse_file(source, "qualified.py")
    cls = nodes[0]
    method = cls.children[0]
    assert cls.qualified_name == "MyClass"
    assert method.qualified_name == "MyClass.my_method"


def test_parse_file_imports_tree_sitter():
    """parse_file can import tree-sitter-language-pack (dependency is installed)."""
    from tree_sitter_language_pack import get_parser
    parser = get_parser("python")
    tree = parser.parse(b"def hello(): pass\n")
    assert tree.root_node is not None
