from backend.fake_store import clear_cart, get_cart_total


def clear_cart_items() -> str:
    """Empty the whole cart."""
    clear_cart()
    return "Your cart is now empty."
