import re

from tools.track_order import track_order
from workflows.order_context import remember_order_id

ORDER_PREFIX_PATTERN = re.compile(r"\bORD[-\s]?\d+\b", re.IGNORECASE)
BARE_NUMBER_PATTERN = re.compile(r"\b\d{3,}\b")
TRACKING_KEYWORD_PATTERN = re.compile(
    r"#|\b(?:order|track|ord)\b",
    re.IGNORECASE,
)
NEARBY_KEYWORD_WINDOW = 40


def has_nearby_tracking_keyword(message: str, number_start: int) -> bool:
    """Return True if a tracking keyword appears just before the number."""
    window_start = max(0, number_start - NEARBY_KEYWORD_WINDOW)
    preceding_text = message[window_start:number_start]
    return TRACKING_KEYWORD_PATTERN.search(preceding_text) is not None


def extract_order_id(message: str) -> str | None:
    """Find an order ID pattern in the user's message."""
    prefix_match = ORDER_PREFIX_PATTERN.search(message)
    if prefix_match:
        return prefix_match.group(0)

    number_matches = list(BARE_NUMBER_PATTERN.finditer(message))
    if not number_matches:
        return None

    for number_match in number_matches:
        if has_nearby_tracking_keyword(message, number_match.start()):
            return number_match.group(0)

    return number_matches[0].group(0)


def normalize_order_id(raw_id: str) -> str:
    """Convert a raw ID match into ORD-XXXX format."""
    raw_id = raw_id.upper().strip()

    if raw_id.startswith("ORD"):
        digits = raw_id[3:].lstrip("- ").strip()
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
        result = track_order(order_id)
    except Exception:
        return "Sorry, I couldn't check that order right now. Please try again."

    if result != "Order not found.":
        remember_order_id(order_id)

    return result
