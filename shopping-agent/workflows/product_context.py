"""Simple product context storage for the last search results and selection."""

from typing import List, Optional

_last_mentioned_product_ids: list[str] = []


def remember_products(product_ids: list[str]) -> None:
    """Store suggested product IDs as the current conversation context."""
    global _last_mentioned_product_ids
    _last_mentioned_product_ids = list(product_ids) if product_ids else []


def set_suggested_product_ids(ids: List[str]) -> None:
    """Alias for remember_products for backward compatibility."""
    remember_products(ids)


def set_last_mentioned_product_id(product_id: str | None) -> None:
    """Set a single product as the current context."""
    global _last_mentioned_product_ids
    if product_id:
        _last_mentioned_product_ids = [product_id]
    else:
        _last_mentioned_product_ids = []


def get_last_mentioned_product_id() -> Optional[str]:
    """Return the last suggested product ID if there is exactly one in context."""
    if not _last_mentioned_product_ids:
        return None

    if len(_last_mentioned_product_ids) == 1:
        return _last_mentioned_product_ids[0]

    return None


def get_suggested_product_ids() -> list[str]:
    """Return all product IDs from the last search suggestion list."""
    return list(_last_mentioned_product_ids)
