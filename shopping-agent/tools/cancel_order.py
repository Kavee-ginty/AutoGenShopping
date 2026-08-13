from backend.fake_store import cancel_order_by_id, find_order


def normalize_status(status: str | None) -> str:
    """Normalize status text for comparisons."""
    return (status or "").strip().lower()


def cancel_order(order_id: str, reason: str = "No reason provided") -> str:
    """Cancel an order by ID.

    Args:
        order_id: The ID of the order to cancel.
        reason: Why the customer is cancelling the order.
    """
    if not isinstance(order_id, str) or not order_id.strip():
        return "Which order would you like to cancel?"

    order_id = order_id.strip()

    order = find_order(order_id)

    if order is None:
        return f"Order {order_id} not found."

    previous_status = order.get("status") or ""
    normalized_status = normalize_status(previous_status)
    order_number = order.get("id") or order_id

    if normalized_status == "cancelled":
        return f"Order {order_number} is already cancelled."

    if normalized_status in {"out for delivery", "delivered"}:
        return (
            f"Order {order_number} can no longer be cancelled - "
            f"it's already {previous_status}."
        )

    cancel_order_by_id(order_id, reason)

    return f"Order {order_number} has been cancelled successfully."
