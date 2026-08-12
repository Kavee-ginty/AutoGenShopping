from backend.fake_store import find_order


def track_order(order_id: str) -> str:
    """Track an order by ID.

    Args:
        order_id: The ID of the order to track.
    """
    order_id = (order_id or "").strip()

    if not order_id:
        return "Which order would you like to track?"

    order = find_order(order_id)

    if not order:
        return "Order not found."

    return f"{order['id']}: {order['status']} for {order['item']}."
