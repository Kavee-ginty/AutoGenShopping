from backend.fake_store import get_cart_items, get_cart_total


def view_cart(show_items: bool = True) -> str:
    """Show the current contents of the cart or just the total."""
    cart_items = get_cart_items()
    total = get_cart_total()

    if not cart_items:
        if show_items:
            return "Your cart is empty."
        return f"Total: LKR {total:,}"

    if not show_items:
        return f"Total: LKR {total:,}"

    lines = []
    subtotal = 0

    for index, item in enumerate(cart_items, start=1):
        lines.append(
            f"{index}. {item['name']} x {item['quantity']} - "
            f"LKR {item['line_total']:,}"
        )
        subtotal += item["line_total"]

    lines.append(f"Subtotal: LKR {subtotal:,}")
    lines.append(f"Total: LKR {total:,}")

    return "\n".join(lines)
