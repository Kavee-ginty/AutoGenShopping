"""Simple product context storage for the last search results and selection.

This module keeps the last suggested product IDs and the last explicitly
mentioned product ID (e.g., after viewing details). Workflows can read and
update this context to resolve phrases like "that" or "this cake".
"""

from typing import List, Optional

_last_suggested_ids: List[str] = []
_last_mentioned_product_id: Optional[str] = None


def set_suggested_product_ids(ids: List[str]) -> None:
    """Store the most recent suggested product IDs from search results.

    If exactly one id is provided, also set it as the last mentioned product.
    """
    global _last_suggested_ids, _last_mentioned_product_id
    _last_suggested_ids = list(ids) if ids else []
    _last_mentioned_product_id = _last_suggested_ids[0] if len(_last_suggested_ids) == 1 else None


def get_suggested_product_ids() -> List[str]:
    return list(_last_suggested_ids)


def set_last_mentioned_product_id(product_id: str | None) -> None:
    global _last_mentioned_product_id
    _last_mentioned_product_id = product_id


def get_last_mentioned_product_id() -> Optional[str]:
    return _last_mentioned_product_id
