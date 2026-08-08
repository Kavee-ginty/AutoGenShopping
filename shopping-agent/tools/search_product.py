def search_product(query: str) -> str:
    """Search for products by name.

    Args:
        query: The product name to search for.
    """
    query = query.strip()

    if not query:
        return "What product should I search for?"

    # Dummy results for now. Module 3 adds real fake-store data.
    return f"Dummy search results for: {query}"
