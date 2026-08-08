def track_order(order_id: str) -> str:
    """Track an order by ID.

    Args:
        order_id: The ID of the order to track.
    """
    order_id = (order_id or "").strip()

    if not order_id:
        return "Which order would you like to track?"

    # Dummy status for now. Module 3 adds real order tracking.
    return f"Order {order_id} is being processed."
