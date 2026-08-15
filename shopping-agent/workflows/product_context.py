_last_mentioned_product_ids: list[str] = []


def remember_products(product_ids: list[str]) -> None:
    """Store suggested product IDs as the current conversation context."""
    global _last_mentioned_product_ids
    _last_mentioned_product_ids = list(product_ids)


def get_last_mentioned_product_id() -> str | None:
    """Return the last suggested product ID, if any."""
    if not _last_mentioned_product_ids:
        return None

    if len(_last_mentioned_product_ids) == 1:
        return _last_mentioned_product_ids[0]

    return None


def get_suggested_product_ids() -> list[str]:
    """Return all product IDs from the last search suggestion list."""
    return list(_last_mentioned_product_ids)
