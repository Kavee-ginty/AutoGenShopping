from backend.fake_store import find_products


def search_product(query: str) -> str:
    """Search for products by name.

    Args:
        query: The product name to search for.
    """
    query = (query or "").strip()

    if not query:
        return "What product should I search for?"

    products = find_products(query)

    if not products:
        return "No products found."

    lines = []

    for product in products:
        lines.append(
            f"{product['id']}: {product['name']} - "
            f"LKR {product['price']:,} (stock: {product['stock']})"
        )

    return "\n".join(lines)
