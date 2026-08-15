from backend.fake_store import find_products, find_products_filtered


def format_product_list(products: list[dict]) -> str:
    lines = []

    for product in products:
        lines.append(
            f"{product['id']}: {product['name']} - "
            f"LKR {product['price']:,} (stock: {product['stock']})"
        )

    return "\n".join(lines)


def search_matching_products(
    query: str,
    budget_max: int | None = None,
    occasion: str | None = None,
    for_who: str | None = None,
    limit: int = 5,
) -> list[dict]:
    """Find products using optional budget and occasion filters."""
    query = (query or "").strip()

    if not query:
        return []

    if budget_max is None and not occasion and not for_who:
        return find_products(query)[:limit]

    return find_products_filtered(
        category=query,
        budget_max=budget_max,
        occasion=occasion,
        for_who=for_who,
        limit=limit,
    )


def search_product(
    query: str,
    budget_max: int | None = None,
    occasion: str | None = None,
    for_who: str | None = None,
    limit: int = 5,
) -> str:
    """Search for products by name.

    Args:
        query: The product name or category to search for.
        budget_max: Optional maximum price in LKR.
        occasion: Optional occasion tag such as birthday.
        for_who: Optional audience tag such as boy.
        limit: Maximum number of products to return.
    """
    query = (query or "").strip()

    if not query:
        return "What product should I search for?"

    products = search_matching_products(
        query,
        budget_max=budget_max,
        occasion=occasion,
        for_who=for_who,
        limit=limit,
    )

    if not products:
        return "No products found."

    return format_product_list(products)
