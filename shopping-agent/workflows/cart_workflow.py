import re
from typing import Optional

from tools.add_to_cart import add_to_cart
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
    """Handle viewing and adding items to the shopping cart.

    - `view_cart` calls the `view_cart()` tool.
    - `add_to_cart` parses product id/name and optional quantity, resolves
      "this/that" using `product_context`, and calls `add_to_cart()` tool.
    """
    if intent == "view_cart":
        return view_cart()

    # Only add_to_cart remains
    quantity = _extract_quantity(message)

    # Prefer explicit product id like kp11
    product_id = _find_product_id_in_text(message)

    # If user used a demonstrative (this/that) and no id found, try context
    if not product_id and re.search(r"\b(this|that|the one|that cake|that item)\b", message, flags=re.IGNORECASE):
        product_id = get_last_mentioned_product_id()

        if not product_id:
            suggestions = get_suggested_product_ids()
            if not suggestions:
                return "Which product would you like to add? Please specify a product ID (e.g., kp11)."
            if len(suggestions) > 1:
                return "Which one? Use the product ID (e.g. kp11)."

    # If still no product id, attempt to extract a name-like phrase
    product_text = product_id
    if not product_text:
        # Remove common action phrases
        product_text = message.lower()
        for phrase in ["add to cart", "add", "put in cart", "buy", "to cart"]:
            product_text = product_text.replace(phrase, "")
        # Remove numeric quantity tokens
        product_text = re.sub(r"\b\d+\b", "", product_text).strip()

    if not product_text:
        return "Please specify which product you would like to add to your cart. Use a product ID like kp11 if possible."

    # Call the tool (it handles unknown product names/ids and quantity validation)
    try:
        result = add_to_cart(product_text, quantity)
    except Exception:
        result = "Sorry, I couldn't add that product to the cart right now."

    return result
