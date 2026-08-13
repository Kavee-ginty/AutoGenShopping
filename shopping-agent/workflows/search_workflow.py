from tools.search_product import search_product


def handle_search(message: str) -> str:
    """Extract query keywords and invoke search tool."""
    query = (message or "").lower()

    # Longer prefixes first so "search for" is not reduced to leftover "for".
    for prefix in ["i want to buy", "search for", "look for", "search", "find", "buy"]:
        if query.startswith(prefix):
            query = query[len(prefix) :].strip()
            break

    query = query.strip()

    if not query:
        return "What product are you looking for today?"

    try:
        return search_product(query)
    except Exception:
        return "I couldn't search for products right now. Please try again."
