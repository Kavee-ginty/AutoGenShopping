import re
from typing import Optional

from tools.add_to_cart import add_to_cart
from tools.clear_cart import clear_cart_items
from tools.remove_from_cart import remove_from_cart
from tools.view_cart import view_cart

try:
    from .product_context import (
        get_last_mentioned_product_id,
        get_suggested_product_ids,
    )
except Exception:
    # Fallbacks if product_context is not present for some reason.
    def get_last_mentioned_product_id() -> Optional[str]:
        return None

    def get_suggested_product_ids() -> list:
        return []


def _extract_quantity(message: str) -> int:
    match = re.search(r"\b(\d+)\b", message)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return 1
    return 1


def _find_product_id_in_text(message: str) -> Optional[str]:
    # Product ids use patterns like kp11; match letters+digits as a single token
    match = re.search(r"\b[a-zA-Z]{1,5}\d{1,6}\b", message, flags=re.IGNORECASE)
    if match:
        return match.group(0)
    return None


def handle_cart(intent: str, message: str) -> str:
    """Handle viewing, adding, and removing items in the cart."""
    if intent == "view_cart":
        return view_cart()

    if intent == "clear_cart":
        return clear_cart_items()

    quantity = _extract_quantity(message)
    product_id = _find_product_id_in_text(message)

    if not product_id and re.search(r"\b(this|that|the one|that cake|that item)\b", message, flags=re.IGNORECASE):
        product_id = get_last_mentioned_product_id()

        if not product_id:
            suggestions = get_suggested_product_ids()
            if not suggestions:
                return "Which product would you like to update? Please specify a product ID (e.g., kp11)."
            if len(suggestions) > 1:
                return "Which one? Use the product ID (e.g. kp11)."

    product_text = product_id
    if not product_text:
        product_text = message.lower()
        for phrase in [
            "add to cart",
            "add",
            "put in cart",
            "buy",
            "to cart",
            "remove from cart",
            "remove",
            "delete",
            "take out",
            "from cart",
        ]:
            product_text = product_text.replace(phrase, "")
        product_text = re.sub(r"\b\d+\b", "", product_text).strip()

    if not product_text:
        if intent == "remove_from_cart":
            return "Please specify which product you would like to remove from the cart. Use a product ID like kp11 if possible."
        return "Please specify which product you would like to add to your cart. Use a product ID like kp11 if possible."

    try:
        if intent == "remove_from_cart":
            return remove_from_cart(product_text, quantity)
        return add_to_cart(product_text, quantity)
    except Exception:
        if intent == "remove_from_cart":
            return "Sorry, I couldn't remove that product from the cart right now."
        return "Sorry, I couldn't add that product to the cart right now."
