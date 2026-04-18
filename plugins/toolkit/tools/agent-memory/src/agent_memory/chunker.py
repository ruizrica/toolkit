# ABOUTME: Markdown-aware text chunking for agent-memory indexing.
# ABOUTME: Splits markdown files at heading boundaries with configurable size and overlap.

import re
from dataclasses import dataclass

from .config import CHUNK_MAX_CHARS, CHUNK_OVERLAP_CHARS

HEADING_RE = re.compile(r"^#{1,6}\s", re.MULTILINE)


@dataclass
class Chunk:
    """A chunk of text from a markdown file with position metadata."""
    text: str
    start_line: int
    end_line: int
    source_path: str


def chunk_markdown(
    text: str,
    source_path: str,
    max_chars: int = CHUNK_MAX_CHARS,
    overlap_chars: int = CHUNK_OVERLAP_CHARS,
) -> list[Chunk]:
    """Split markdown text into chunks respecting heading boundaries.

    Splits on headings first, then splits oversized sections by size.
    Returns empty list for blank/whitespace-only input.
    """
    if not text or not text.strip():
        return []

    lines = text.splitlines(keepends=True)
    sections = _split_at_headings(lines)
    chunks = []

    for start_line, section_lines in sections:
        section_text = "".join(section_lines).strip()
        if not section_text:
            continue

        if len(section_text) <= max_chars:
            end_line = start_line + len(section_lines) - 1
            chunks.append(Chunk(
                text=section_text,
                start_line=start_line,
                end_line=end_line,
                source_path=source_path,
            ))
        else:
            sub_chunks = _split_by_size(
                section_lines, start_line, max_chars, overlap_chars, source_path
            )
            chunks.extend(sub_chunks)

    return chunks


def _split_at_headings(lines: list[str]) -> list[tuple[int, list[str]]]:
    """Split lines into sections at heading boundaries.

    Returns list of (start_line_1indexed, lines) tuples.
    """
    sections: list[tuple[int, list[str]]] = []
    current_start = 1
    current_lines: list[str] = []

    for i, line in enumerate(lines):
        if HEADING_RE.match(line) and current_lines:
            sections.append((current_start, current_lines))
            current_start = i + 1
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((current_start, current_lines))

    return sections


def _split_by_size(
    lines: list[str],
    start_line: int,
    max_chars: int,
    overlap_chars: int,
    source_path: str,
) -> list[Chunk]:
    """Split a section's lines into size-limited chunks with overlap."""
    chunks = []
    current_chars = 0
    current_lines: list[str] = []
    chunk_start = start_line

    for i, line in enumerate(lines):
        line_len = len(line)
        if current_chars + line_len > max_chars and current_lines:
            chunk_text = "".join(current_lines).strip()
            if chunk_text:
                chunks.append(Chunk(
                    text=chunk_text,
                    start_line=chunk_start,
                    end_line=chunk_start + len(current_lines) - 1,
                    source_path=source_path,
                ))

            # Find overlap: walk backwards from end of current_lines
            overlap_text = ""
            overlap_lines: list[str] = []
            for back_line in reversed(current_lines):
                if len(overlap_text) + len(back_line) > overlap_chars:
                    break
                overlap_lines.insert(0, back_line)
                overlap_text = back_line + overlap_text

            current_lines = overlap_lines + [line]
            chunk_start = start_line + i - len(overlap_lines)
            current_chars = sum(len(ln) for ln in current_lines)
        else:
            current_lines.append(line)
            current_chars += line_len

    if current_lines:
        chunk_text = "".join(current_lines).strip()
        if chunk_text:
            chunks.append(Chunk(
                text=chunk_text,
                start_line=chunk_start,
                end_line=chunk_start + len(current_lines) - 1,
                source_path=source_path,
            ))

    return chunks
