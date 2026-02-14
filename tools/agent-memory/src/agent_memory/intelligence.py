# ABOUTME: Claude Agent SDK intelligence features — ask and summarize.
# ABOUTME: 100% optional; core search works without this module.
# ABOUTME: OAuth token support: Set AGENT_MEMORY_OAUTH_TOKEN in .env file

import glob
import os
import sqlite3
from pathlib import Path

from .config import get_memory_dir
from .search import search_hybrid


def _load_oauth_token() -> str | None:
    """Load OAuth token from environment or .env file.

    Checks multiple locations for .env file:
    1. Current working directory
    2. Project root (where .git or agent-memory is)
    3. Parent directories

    Maps AGENT_MEMORY_OAUTH_TOKEN to CLAUDE_CODE_OAUTH_TOKEN for SDK compatibility.
    Returns the token if found, None otherwise.
    Ignores placeholder values like "your_oauth_token_here".
    """
    # Try loading from .env file if python-dotenv is available
    try:
        from dotenv import load_dotenv

        # Find .env in multiple locations (in priority order)
        env_paths = []

        # First: Check project root (up to 5 levels up looking for .git)
        current = Path.cwd()
        for _ in range(5):
            if (current / ".git").exists():
                if (current / ".env").exists():
                    env_paths.append(current / ".env")
                break
            parent = current.parent
            if parent == current:
                break
            current = parent

        # Second: Check this module's package root (agent-memory folder)
        module_dir = Path(__file__).parent.parent.parent  # up to agent-memory root
        if module_dir.exists() and (module_dir / ".env") not in env_paths:
            env_paths.append(module_dir / ".env")

        # Third: Current working directory (lowest priority, often has placeholder)
        cwd_env = Path.cwd() / ".env"
        if cwd_env not in env_paths:
            env_paths.append(cwd_env)

        # Load from first existing .env file (without overriding existing env vars)
        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(env_path, override=False)
                break

    except ImportError:
        pass  # dotenv is optional

    # Check for agent-memory specific token first
    token = os.environ.get("AGENT_MEMORY_OAUTH_TOKEN")

    # Check for SDK-compatible token
    if not token:
        token = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")

    # Ignore placeholder tokens (but allow actual tokens that may start with sk-)
    if token and (token.startswith("your_") or token == ""):
        return None

    # If we found a token, ensure CLAUDE_CODE_OAUTH_TOKEN is set for SDK compatibility
    if token and not os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"):
        os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = token

    return token


def _get_anthropic_client():
    """Get Anthropic client using OAuth token if available.

    When CLAUDE_CODE_OAUTH_TOKEN is set, Anthropic() is called with NO parameters.
    SDK automatically reads CLAUDE_CODE_OAUTH_TOKEN from environment.
    """
    import anthropic

    oauth_token = _load_oauth_token()

    if oauth_token:
        # OAuth token available: SDK reads CLAUDE_CODE_OAUTH_TOKEN automatically
        return anthropic.Anthropic()
    else:
        # No OAuth token: try API key from environment (ANTHROPIC_API_KEY)
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if api_key:
            return anthropic.Anthropic(api_key=api_key)
        # No auth available - Anthropic() will raise appropriate error
        return anthropic.Anthropic()


def _query_with_sdk(prompt: str) -> str:
    """Query Claude using Claude Agent SDK query() function (preferred).

    This function automatically handles OAuth tokens when CLAUDE_CODE_OAUTH_TOKEN
    is set in the environment. Falls back to direct Anthropic client if SDK
    query() is not available.
    """
    oauth_token = _load_oauth_token()

    # Try SDK query() first (handles OAuth automatically)
    try:
        from claude_agent_sdk import AssistantMessage, ResultMessage, query
        from claude_agent_sdk.types import TextBlock

        response_text = ""
        sdk_error = None

        # query() handles OAuth tokens automatically when CLAUDE_CODE_OAUTH_TOKEN is set
        async def _run_query():
            nonlocal response_text, sdk_error
            try:
                async for message in query(prompt=prompt):
                    if isinstance(message, AssistantMessage):
                        for block in message.content:
                            if isinstance(block, TextBlock):
                                response_text += block.text
                    elif isinstance(message, ResultMessage):
                        if message.result:
                            response_text = message.result
                return response_text
            except Exception as e:
                sdk_error = e
                raise

        # Run the async query
        import asyncio

        return asyncio.run(_run_query())

    except ImportError as e:
        # SDK query() not available, fall back to direct Anthropic client
        pass
    except Exception as e:
        # SDK query() failed, check if it's an auth error
        error_msg = str(e).lower()
        if "auth" in error_msg or "token" in error_msg or "credential" in error_msg:
            raise RuntimeError(f"SDK query failed with auth error: {e}") from e
        # Other SDK error, fall back to direct client
        pass

    # Fall back to Anthropic client with OAuth/API key handling
    client = _get_anthropic_client()
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def _build_context(conn: sqlite3.Connection, query: str) -> list[str]:
    """Search memories and return context strings for the LLM."""
    results = search_hybrid(conn, query, limit=10, min_score=0.1)
    return [r.text for r in results]


def _collect_daily_logs() -> list[str]:
    """Read recent daily log files and return their contents."""
    memory_dir = get_memory_dir()
    daily_dir = memory_dir / "daily-logs"
    pattern = str(daily_dir / "*.md")
    files = sorted(glob.glob(pattern), reverse=True)[:7]  # Last 7 days

    contents = []
    for f in files:
        text = Path(f).read_text(encoding="utf-8")
        if text.strip():
            contents.append(text)
    return contents


def ask_memories(question: str) -> None:
    """Ask a question about memories using Claude Agent SDK.

    Uses OAuth token if AGENT_MEMORY_OAUTH_TOKEN or CLAUDE_CODE_OAUTH_TOKEN
    is set in environment/.env file. Falls back to ANTHROPIC_API_KEY.
    """
    # Pre-load OAuth token to check availability
    oauth_token = _load_oauth_token()
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not oauth_token and not api_key:
        print(
            "Error: No authentication method available.\n"
            "Set one of the following:\n"
            "  - AGENT_MEMORY_OAUTH_TOKEN (recommended, uses Max Plan)\n"
            "  - CLAUDE_CODE_OAUTH_TOKEN\n"
            "  - ANTHROPIC_API_KEY\n"
            "Add to .env file or export as environment variable.",
            file=__import__("sys").stderr,
        )
        __import__("sys").exit(1)

    from .config import get_db_path
    from .db import init_db

    conn = init_db(get_db_path())
    context = _build_context(conn, question)
    conn.close()

    if not context:
        print("No relevant memories found.")
        return

    context_text = "\n\n---\n\n".join(context)
    prompt = (
        f"Based on the following memory context, answer this question: {question}\n\n"
        f"Context:\n{context_text}"
    )

    try:
        response_text = _query_with_sdk(prompt)
        print(response_text)
    except Exception as e:
        error_msg = str(e)
        if "authentication" in error_msg.lower() or "auth" in error_msg.lower():
            print(
                f"Authentication error: {e}\n\n"
                "Please verify your OAuth token or API key:\n"
                "  1. Check .env file has valid AGENT_MEMORY_OAUTH_TOKEN\n"
                "  2. Or set CLAUDE_CODE_OAUTH_TOKEN environment variable\n"
                "  3. Or set ANTHROPIC_API_KEY for API key authentication",
                file=__import__("sys").stderr,
            )
        else:
            print(f"Error querying Claude: {e}", file=__import__("sys").stderr)
        __import__("sys").exit(1)


def summarize_daily_logs() -> None:
    """Summarize recent daily logs using Claude Agent SDK.

    Uses OAuth token if AGENT_MEMORY_OAUTH_TOKEN or CLAUDE_CODE_OAUTH_TOKEN
    is set in environment/.env file. Falls back to ANTHROPIC_API_KEY.
    """
    # Pre-load OAuth token to check availability
    oauth_token = _load_oauth_token()
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not oauth_token and not api_key:
        print(
            "Error: No authentication method available.\n"
            "Set one of the following:\n"
            "  - AGENT_MEMORY_OAUTH_TOKEN (recommended, uses Max Plan)\n"
            "  - CLAUDE_CODE_OAUTH_TOKEN\n"
            "  - ANTHROPIC_API_KEY\n"
            "Add to .env file or export as environment variable.",
            file=__import__("sys").stderr,
        )
        __import__("sys").exit(1)

    logs = _collect_daily_logs()
    if not logs:
        print("No daily logs found to summarize.")
        return

    combined = "\n\n---\n\n".join(logs)
    prompt = (
        "Summarize the following daily log entries into concise, "
        "well-organized notes suitable for a MEMORY.md file. "
        "Group by topic, remove duplicates, keep only stable facts "
        "and important decisions.\n\n"
        f"Daily logs:\n{combined}"
    )

    try:
        response_text = _query_with_sdk(prompt)
        print(response_text)
    except Exception as e:
        error_msg = str(e)
        if "authentication" in error_msg.lower() or "auth" in error_msg.lower():
            print(
                f"Authentication error: {e}\n\n"
                "Please verify your OAuth token or API key:\n"
                "  1. Check .env file has valid AGENT_MEMORY_OAUTH_TOKEN\n"
                "  2. Or set CLAUDE_CODE_OAUTH_TOKEN environment variable\n"
                "  3. Or set ANTHROPIC_API_KEY for API key authentication",
                file=__import__("sys").stderr,
            )
        else:
            print(f"Error querying Claude: {e}", file=__import__("sys").stderr)
        __import__("sys").exit(1)
