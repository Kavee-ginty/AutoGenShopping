from backend.fake_store import get_cart_items, get_cart_total


def view_cart() -> str:
    """Show the current contents of the cart."""
    cart_items = get_cart_items()

    if not cart_items:
        return "Your cart is empty."

    lines = []
    total = 0

    for index, item in enumerate(cart_items, start=1):
        lines.append(
            f"{index}. {item['name']} x {item['quantity']} - "
            f"LKR {item['line_total']:,}"
        )
        total += item["line_total"]

    total = get_cart_total()
    lines.append(f"Subtotal: LKR {total:,}")
    lines.append(f"Total: LKR {total:,}")

    return "\n".join(lines)
