import re

from tools.cancel_order import cancel_order

ORDER_PREFIX_PATTERN = re.compile(r"\bORD[-\s]?\d+\b", re.IGNORECASE)
BARE_NUMBER_PATTERN = re.compile(r"\b\d{3,}\b")
CANCEL_KEYWORD_PATTERN = re.compile(
    r"#|\b(?:order|cancel|ord)\b",
    re.IGNORECASE,
)
NEARBY_KEYWORD_WINDOW = 40


def has_nearby_cancel_keyword(message: str, number_start: int) -> bool:
    """Return True if a cancel-related keyword appears just before the number."""
    window_start = max(0, number_start - NEARBY_KEYWORD_WINDOW)
    preceding_text = message[window_start:number_start]
    return CANCEL_KEYWORD_PATTERN.search(preceding_text) is not None


def extract_order_id(message: str) -> str | None:
    """Find an order ID pattern in the user's message."""
    prefix_match = ORDER_PREFIX_PATTERN.search(message)
    if prefix_match:
        return prefix_match.group(0)

    number_matches = list(BARE_NUMBER_PATTERN.finditer(message))
    if not number_matches:
        return None

    for number_match in number_matches:
        if has_nearby_cancel_keyword(message, number_match.start()):
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


def handle_cancel(message: str) -> str:
    """Extract order ID and cancel the order."""
    message = (message or "").strip()
    raw_id = extract_order_id(message)

    if not raw_id:
        return (
            "Please provide your Order ID (e.g. ORD-1001) "
            "so I can cancel it."
        )

    order_id = normalize_order_id(raw_id)

    try:
        return cancel_order(order_id)
    except Exception:
        return "Sorry, I couldn't cancel that order right now. Please try again."
