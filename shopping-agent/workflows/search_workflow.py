import re

from tools.get_product_details import get_product_details
from tools.search_product import format_product_list, search_matching_products
from workflows.product_context import (
    get_last_mentioned_product_id,
    get_suggested_product_ids,
    remember_products,
)

_search_state = {
    "category": None,
    "budget": None,
    "occasion": None,
    "for_who": None,
    "awaiting": None,
}

PREFIXES = [
    "i want to buy",
    "i want a",
    "i want",
    "i need a",
    "i need",
    "search for",
    "look for",
    "show me",
    "search",
    "find",
    "buy",
]

CATEGORY_WORDS = [
    ("air fryer", "air fryer"),
    ("soft toys", "soft toys"),
    ("soft toy", "soft toys"),
    ("grocery hampers", "grocery hampers"),
    ("grocery hamper", "grocery hampers"),
    ("gift sets", "gift sets"),
    ("gift set", "gift sets"),
    ("home and lifestyle", "home and lifestyle"),
    ("utensil", "home and lifestyle"),
    ("flowers", "flowers"),
    ("flower", "flowers"),
    ("bouquet", "flowers"),
    ("cakes", "cakes"),
    ("cake", "cakes"),
    ("hamper", "grocery hampers"),
    ("toys", "soft toys"),
    ("toy", "soft toys"),
    ("electronics", "electronics"),
]

OCCASION_WORDS = ["birthday", "wedding", "party"]
FOR_WHO_WORDS = {
    "brother": "brother",
    "sister": "sister",
    "boy": "boy",
    "girl": "girl",
    "child": "child",
    "kid": "child",
    "kids": "child",
    "mom": "mom",
    "dad": "dad",
}
DETAIL_WORDS = (
    "stock",
    "rating",
    "ratings",
    "feedback",
    "review",
    "reviews",
    "details",
    "detail",
)
CAKE_CATEGORIES = {"cake", "cakes"}


def reset_search_state() -> None:
    _search_state["category"] = None
    _search_state["budget"] = None
    _search_state["occasion"] = None
    _search_state["for_who"] = None
    _search_state["awaiting"] = None


def is_awaiting_search(message: str = "") -> bool:
    """Return True if search is waiting for a follow-up answer."""
    awaiting = _search_state["awaiting"]
    text = (message or "").lower().strip()

    if awaiting == "budget":
        if extract_budget(text) is not None:
            return True
        if extract_occasion(text) or extract_for_who(text):
            return True
        if extract_category(text, fallback=False) is not None:
            return True
        _search_state["awaiting"] = None
        return False

    if awaiting == "occasion":
        if extract_occasion(text) or extract_for_who(text):
            return True
        if extract_category(text, fallback=False) is not None:
            return True
        _search_state["awaiting"] = None
        return False

    if awaiting == "details":
        if "cart" in text or text.startswith("add "):
            return False
        if is_details_request(text):
            return True
        return False

    if _search_state["category"] and extract_budget(text) is not None:
        return True

    return False


def strip_prefixes(message: str) -> str:
    query = (message or "").lower().strip()

    for prefix in PREFIXES:
        if query.startswith(prefix):
            return query[len(prefix) :].strip()

    return query


def extract_category(message: str, fallback: bool = False) -> str | None:
    text = (message or "").lower()

    for word, category in CATEGORY_WORDS:
        if re.search(rf"\b{re.escape(word)}\b", text):
            return category

    # Follow-up answers like "my little brother" are not a new category.
    if extract_for_who(text) or extract_occasion(text):
        return None

    if is_details_request(text):
        return None

    has_prefix = any(text.startswith(prefix) for prefix in PREFIXES)

    if has_prefix or fallback:
        leftover = strip_prefixes(text)
        leftover = re.sub(r"\d[\d,]*", " ", leftover)
        leftover = leftover.replace("lkr", " ").replace("rs", " ")
        leftover = leftover.replace("under", " ").replace("below", " ").replace("around", " ")
        leftover = leftover.replace("my", " ").replace("little", " ")
        leftover = " ".join(leftover.split())

        if leftover:
            return leftover

    return None


def extract_budget(message: str) -> int | None:
    match = re.search(r"(\d[\d,]*)", message or "")

    if not match:
        return None

    try:
        return int(match.group(1).replace(",", ""))
    except ValueError:
        return None


def extract_occasion(message: str) -> str | None:
    text = (message or "").lower()

    for occasion in OCCASION_WORDS:
        if re.search(rf"\b{occasion}\b", text):
            return occasion

    return None


def extract_for_who(message: str) -> str | None:
    text = (message or "").lower()

    for word, value in FOR_WHO_WORDS.items():
        if re.search(rf"\b{word}\b", text):
            return value

    return None


def is_details_request(message: str) -> bool:
    text = (message or "").lower()

    for word in DETAIL_WORDS:
        if re.search(rf"\b{word}\b", text):
            return True

    if re.search(r"\bkp\d+\b", text):
        return True

    if re.search(r"\b(this|that)\b", text) and get_suggested_product_ids():
        return True

    return False


def looks_like_new_search(message: str) -> bool:
    text = (message or "").lower()

    if is_details_request(text):
        return False

    category = extract_category(text, fallback=False)

    if not category:
        return False

    current = _search_state["category"]
    if current and category != current:
        return True

    for prefix in PREFIXES:
        if text.startswith(prefix):
            return True

    return False


def update_state_from_message(message: str, fallback_category: bool = False) -> None:
    category = extract_category(message, fallback=fallback_category)
    budget = extract_budget(message)
    occasion = extract_occasion(message)
    for_who = extract_for_who(message)

    if category:
        _search_state["category"] = category
    if budget is not None:
        _search_state["budget"] = budget
    if occasion:
        _search_state["occasion"] = occasion
    if for_who:
        _search_state["for_who"] = for_who


def needs_cake_occasion() -> bool:
    category = _search_state["category"] or ""
    is_cake = category in CAKE_CATEGORIES or "cake" in category
    has_occasion = _search_state["occasion"] or _search_state["for_who"]
    return is_cake and not has_occasion


def run_filtered_search() -> str:
    try:
        products = search_matching_products(
            _search_state["category"],
            budget_max=_search_state["budget"],
            occasion=_search_state["occasion"],
            for_who=_search_state["for_who"],
            limit=5,
        )
    except Exception:
        _search_state["awaiting"] = None
        return "I couldn't search for products right now. Please try again."

    if not products:
        _search_state["awaiting"] = None
        remember_products([])
        return (
            "No products found for those filters. "
            "Want to try a higher budget or a different occasion?"
        )

    remember_products([product["id"] for product in products])
    _search_state["awaiting"] = "details"

    lines = [
        "Here are a few matches:",
        format_product_list(products),
        "Want stock, rating, or feedback for one of these? Use the product ID.",
    ]
    return "\n".join(lines)


def detail_kind(message: str) -> str:
    text = (message or "").lower()

    if re.search(r"\b(stock|in stock)\b", text):
        return "stock"

    if re.search(r"\b(feedback|review|reviews|rating|ratings)\b", text):
        return "feedback"

    return "all"


def handle_product_details(message: str) -> str:
    kind = detail_kind(message)
    match = re.search(r"\bkp\d+\b", message or "", re.IGNORECASE)
    if match:
        product_key = match.group(0).lower()
        remember_products([product_key])
        try:
            return get_product_details(product_key, kind)
        except Exception:
            return "I couldn't load those product details right now. Please try again."

    last_id = get_last_mentioned_product_id()
    if last_id:
        try:
            return get_product_details(last_id, kind)
        except Exception:
            return "I couldn't load those product details right now. Please try again."

    suggested = get_suggested_product_ids()
    if suggested:
        return (
            "Which product do you mean? "
            f"Use a product ID such as {suggested[0]}."
        )

    return "Please search for a product first."


def handle_search(message: str) -> str:
    """Ask for missing filters, then search and show up to 5 matches."""
    message = (message or "").strip()

    if not message:
        return "What product are you looking for today?"

    if (
        _search_state["awaiting"] == "details"
        and is_details_request(message)
        and not looks_like_new_search(message)
    ):
        return handle_product_details(message)

    new_category = extract_category(message, fallback=True)
    if (
        _search_state["category"]
        and new_category
        and new_category != _search_state["category"]
    ):
        reset_search_state()

    update_state_from_message(message, fallback_category=True)

    if not _search_state["category"]:
        _search_state["awaiting"] = None
        return "What product are you looking for today?"

    if _search_state["budget"] is None:
        _search_state["awaiting"] = "budget"
        return "Around what budget range?"

    if needs_cake_occasion():
        _search_state["awaiting"] = "occasion"
        return "What kind of party is it, or who are you buying it for?"

    return run_filtered_search()
