from tools.search_product import search_product
from .product_context import set_suggested_product_ids


def handle_search(message: str) -> str:
    """Extract query keywords and invoke search tool.

    Stores up to 5 suggested product IDs in `product_context` so follow-up
    commands like "add that cake to cart" can be resolved.
    """
    # Clean noise words
    query = (message or "").lower()
    for prefix in ["search for", "search", "find", "buy", "look for"]:
        if query.startswith(prefix):
            query = query[len(prefix):].strip()
            break

    query = query.strip()

    # Remove surrounding quotes if the user included them
    if (query.startswith('"') and query.endswith('"')) or (
        query.startswith("'") and query.endswith("'")
    ):
        query = query[1:-1].strip()

    if not query:
        # Do not set suggestions when no query provided
        set_suggested_product_ids([])
        return "What product are you looking for today?"

    result_text = search_product(query)

    # Parse product IDs from the formatted result lines like "kp11: Name - LKR ..."
    suggested_ids = []
    for line in (result_text or "").splitlines():
        line = line.strip()
        if not line:
            continue
        if ":" in line:
            pid = line.split(":", 1)[0].strip()
            if pid:
                suggested_ids.append(pid)

    # Keep up to 5 suggestions
    set_suggested_product_ids(suggested_ids[:5])

    return result_text
