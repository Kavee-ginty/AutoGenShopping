# Remembers the last order the user tracked or started cancelling
# so phrases like "that order" can reuse it.

_last_mentioned_order_id: str | None = None


def remember_order_id(order_id: str) -> None:
    """Store an order ID as the current conversation context."""
    global _last_mentioned_order_id
    _last_mentioned_order_id = order_id


def get_last_mentioned_order_id() -> str | None:
    """Return the last order ID the user mentioned, if any."""
    return _last_mentioned_order_id
