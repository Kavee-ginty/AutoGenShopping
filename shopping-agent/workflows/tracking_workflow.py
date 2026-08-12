import re

from tools.track_order import track_order

ORDER_ID_PATTERN = re.compile(r"(ORD-\d+|\b\d+\b)", re.IGNORECASE)


def extract_order_id(message: str) -> str | None:
    """Find an order ID pattern in the user's message."""
    match = ORDER_ID_PATTERN.search(message)

    if not match:
        return None

    return match.group(1)


def normalize_order_id(raw_id: str) -> str:
    """Convert a raw ID match into ORD-XXXX format."""
    raw_id = raw_id.upper()

    if raw_id.startswith("ORD-"):
        digits = raw_id[4:]
    else:
        digits = raw_id

    return f"ORD-{digits.zfill(4)}"


def handle_tracking(message: str) -> str:
    """Extract order ID and fetch order tracking status."""
    raw_id = extract_order_id(message)

    if not raw_id:
        return (
            "Please provide your Order ID (e.g. ORD-1001) "
            "so I can check its delivery status."
        )

    order_id = normalize_order_id(raw_id)

    try:
        return track_order(order_id)
    except Exception:
        return "Sorry, I couldn't check that order right now. Please try again."
