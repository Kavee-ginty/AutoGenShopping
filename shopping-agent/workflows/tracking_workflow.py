import re

from tools.track_order import track_order

ORDER_PREFIX_PATTERN = re.compile(r"ORD-\d+", re.IGNORECASE)
BARE_NUMBER_PATTERN = re.compile(r"\b\d{4,}\b")


def extract_order_id(message: str) -> str | None:
    """Find an order ID pattern in the user's message."""
    prefix_match = ORDER_PREFIX_PATTERN.search(message)
    if prefix_match:
        return prefix_match.group(0)

    number_match = BARE_NUMBER_PATTERN.search(message)
    if number_match:
        return number_match.group(0)

    return None


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
    message = (message or "").strip()
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
