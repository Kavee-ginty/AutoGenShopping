from datetime import date

from backend.fake_store import find_order


def add_labeled_line(lines: list[str], label: str, value: str | None) -> None:
    """Append a labeled line only when the value is present."""
    if value:
        lines.append(f"{label}: {value}")


def normalize_status(status: str | None) -> str:
    """Normalize status text for comparisons."""
    return (status or "").strip().lower()


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
    if normalize_status(status) in {"delivered", "cancelled"} or not estimated_delivery:
        return None

    try:
        delivery_date = date.fromisoformat(estimated_delivery)
    except (ValueError, TypeError):
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

    normalized_status = normalize_status(status)

    if normalized_status == "cancelled":
        return "This order has already been cancelled."

    if normalized_status in {"out for delivery", "delivered"}:
        return "This order can no longer be cancelled."

    return "This order can still be cancelled."


def track_order(order_id: str) -> str:
    """Track an order by ID.

    Args:
        order_id: The ID of the order to track.
    """
    if not isinstance(order_id, str) or not order_id.strip():
        return "Which order would you like to track?"

    order_id = order_id.strip()

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

    if normalize_status(status) == "cancelled":
        add_labeled_line(lines, "Cancelled on", order.get("cancelled_date"))
        add_labeled_line(lines, "Cancellation reason", order.get("cancelled_reason"))

    add_labeled_line(lines, "Delivery service", order.get("delivery_service"))
    add_labeled_line(lines, "Estimated delivery", order.get("estimated_delivery"))

    if normalize_status(status) == "delayed":
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

    if not lines:
        shown_id = order.get("id") or order_id
        return f"Order {shown_id} found but no details are available."

    return "\n".join(lines)
