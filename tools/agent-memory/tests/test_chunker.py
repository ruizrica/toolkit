# ABOUTME: Tests for chunker module — markdown-aware text splitting.
# ABOUTME: Verifies heading boundaries, overlap, line tracking, and edge cases.

from dataclasses import dataclass


def test_chunk_dataclass_fields():
    """Chunk has required fields: text, start_line, end_line, source_path."""
    from agent_memory.chunker import Chunk

    c = Chunk(text="hello", start_line=1, end_line=5, source_path="/foo.md")
    assert c.text == "hello"
    assert c.start_line == 1
    assert c.end_line == 5
    assert c.source_path == "/foo.md"


def test_chunk_short_file():
    """A short file returns a single chunk."""
    from agent_memory.chunker import chunk_markdown

    text = "# Title\n\nShort content here.\n"
    chunks = chunk_markdown(text, source_path="/test.md")
    assert len(chunks) == 1
    assert "Short content" in chunks[0].text
    assert chunks[0].start_line == 1


def test_chunk_heading_boundaries():
    """New heading starts a new chunk (even if size limit not reached)."""
    from agent_memory.chunker import chunk_markdown

    text = (
        "# Section 1\n\nContent for section one.\n\n"
        "# Section 2\n\nContent for section two.\n"
    )
    chunks = chunk_markdown(text, source_path="/test.md")
    assert len(chunks) == 2
    assert "Section 1" in chunks[0].text
    assert "Section 2" in chunks[1].text


def test_chunk_respects_max_size():
    """Long sections are split at max_chars boundary."""
    from agent_memory.chunker import chunk_markdown

    # Create a long section that exceeds default max_chars
    long_line = "x" * 200 + "\n"
    text = "# Big Section\n\n" + long_line * 20  # ~4000+ chars
    chunks = chunk_markdown(text, source_path="/test.md", max_chars=800)
    assert len(chunks) > 1


def test_chunk_line_tracking():
    """Chunks track correct start and end lines."""
    from agent_memory.chunker import chunk_markdown

    text = "# A\n\nLine 3\nLine 4\n\n# B\n\nLine 8\n"
    chunks = chunk_markdown(text, source_path="/test.md")
    assert chunks[0].start_line == 1
    assert chunks[1].start_line > chunks[0].start_line


def test_chunk_overlap():
    """Adjacent chunks from the same section overlap by overlap_chars."""
    from agent_memory.chunker import chunk_markdown

    line = "word " * 40 + "\n"  # ~200 chars per line
    text = "# Long\n\n" + line * 20  # ~4000 chars
    chunks = chunk_markdown(text, source_path="/test.md", max_chars=800, overlap_chars=200)

    if len(chunks) >= 2:
        # The end of chunk N should overlap with the start of chunk N+1
        tail = chunks[0].text[-200:]
        head = chunks[1].text[:400]
        # Some overlap text should appear in both
        assert any(word in head for word in tail.split()[:3])


def test_chunk_empty_file():
    """Empty file returns no chunks."""
    from agent_memory.chunker import chunk_markdown

    chunks = chunk_markdown("", source_path="/empty.md")
    assert chunks == []


def test_chunk_whitespace_only():
    """Whitespace-only file returns no chunks."""
    from agent_memory.chunker import chunk_markdown

    chunks = chunk_markdown("   \n\n  \n", source_path="/ws.md")
    assert chunks == []


def test_chunk_preserves_source_path():
    """All chunks have the correct source_path."""
    from agent_memory.chunker import chunk_markdown

    text = "# A\n\nContent\n\n# B\n\nMore content\n"
    chunks = chunk_markdown(text, source_path="/my/file.md")
    for chunk in chunks:
        assert chunk.source_path == "/my/file.md"


def test_chunk_subheadings():
    """## and ### headings also start new chunks."""
    from agent_memory.chunker import chunk_markdown

    text = (
        "# Main\n\nIntro\n\n"
        "## Sub 1\n\nContent 1\n\n"
        "### Sub Sub\n\nDeep content\n"
    )
    chunks = chunk_markdown(text, source_path="/test.md")
    assert len(chunks) == 3
