from mcp.server.fastmcp import FastMCP

import math

mcp = FastMCP("General Tools MCP Server")


# ── Tool 1: Calculator ────────────────────────────────────────────────────────
@mcp.tool()
def calculator(expression: str) -> str:
    """
    Evaluate a basic math expression and return the result.
    Example: '2 + 3 * 4', '(10 / 2) ** 2'
    """
    try:
        allowed = {k: v for k, v in vars(math).items()}
        result = eval(expression, {"__builtins__": {}}, allowed)  # noqa: S307
        return f"Result: {result}"
    except Exception as e:
        return f"Error evaluating expression: {e}"


# ── Tool 2: String Utilities ──────────────────────────────────────────────────
@mcp.tool()
def string_info(text: str) -> dict:
    """
    Return useful information about a string:
    character count, word count, uppercase, lowercase, reversed.
    """
    return {
        "original": text,
        "char_count": len(text),
        "word_count": len(text.split()),
        "uppercase": text.upper(),
        "lowercase": text.lower(),
        "reversed": text[::-1],
    }


# ── Tool 3: Key-Value Store (in-memory) ───────────────────────────────────────
_store: dict[str, str] = {}


@mcp.tool()
def kv_set(key: str, value: str) -> str:
    """Store a value under a key."""
    _store[key] = value
    return f"Stored '{key}' = '{value}'"


@mcp.tool()
def kv_get(key: str) -> str:
    """Retrieve a value by key."""
    if key in _store:
        return f"'{key}' = '{_store[key]}'"
    return f"Key '{key}' not found."


@mcp.tool()
def kv_list() -> dict:
    """List all stored key-value pairs."""
    return _store if _store else {"message": "Store is empty."}


# ── Resource: Server info ─────────────────────────────────────────────────────
@mcp.resource("info://server")
def server_info() -> str:
    """Static resource describing this MCP server."""
    return (
        "General Tools MCP Server\n"
        "Tools: calculator, string_info, kv_set, kv_get, kv_list\n"
        "Transport: stdio"
    )


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    mcp.run(transport="stdio")

