from mcp_tools.functions import get_categories


def show_categories() -> str:
    """Fetch available categories from Kapruka MCP."""
    return get_categories()
