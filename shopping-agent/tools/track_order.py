from datetime import date

from backend.fake_store import find_order


def add_labeled_line(lines: list[str], label: str, value: str | None) -> None:
    """Append a labeled line only when the value is present."""
    if value:
        lines.append(f"{label}: {value}")


def format_history_lines(history: list) -> list[str]:
    """Format tracking history as plain text lines."""
    if not history:
        return []

    lines = ["Tracking history:"]

    for entry in history:
        if not isinstance(entry, dict):
            continue

        date = entry.get("date")
        update = entry.get("update")

        if date and update:
            lines.append(f"  {date} - {update}")
        elif date:
            lines.append(f"  {date}")
        elif update:
            lines.append(f"  {update}")

    if len(lines) == 1:
        return []

    return lines


def format_arrival_line(
    estimated_delivery: str | None, status: str | None
) -> str | None:
    """Return a plain-text arrival countdown, or None to skip."""
    if status == "Delivered" or not estimated_delivery:
        return None

    try:
        delivery_date = date.fromisoformat(estimated_delivery)
    except ValueError:
        return None

    days = (delivery_date - date.today()).days

    if days > 1:
        return f"Arrives in {days} days"
    if days == 1:
        return "Arrives in 1 day"
    if days == 0:
        return "Arriving today"

    return "Delivery date passed"


def format_cancel_line(status: str | None) -> str | None:
    """Return cancel-eligibility text based on order status."""
    if not status:
        return None

    if status in {"Out for delivery", "Delivered"}:
        return "This order can no longer be cancelled."

    return "This order can still be cancelled."


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

    lines: list[str] = []
    status = order.get("status")

    order_number = order.get("id")
    if order_number:
        lines.append(f"Order {order_number}")

    add_labeled_line(lines, "Item", order.get("item"))
    add_labeled_line(lines, "Status", status)
    add_labeled_line(lines, "Delivery service", order.get("delivery_service"))
    add_labeled_line(lines, "Estimated delivery", order.get("estimated_delivery"))

    if status == "Delayed":
        add_labeled_line(lines, "Delay reason", order.get("delay_reason"))

    arrival_line = format_arrival_line(order.get("estimated_delivery"), status)
    if arrival_line:
        lines.append(arrival_line)

    cancel_line = format_cancel_line(status)
    if cancel_line:
        lines.append(cancel_line)

    history = order.get("tracking_history")
    if isinstance(history, list):
        lines.extend(format_history_lines(history))

    return "\n".join(lines)
