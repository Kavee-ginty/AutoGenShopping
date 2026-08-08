from tools.store import CART


def view_cart() -> str:
    """Show the current contents of the cart."""
    if not CART:
        return "Your cart is empty."

    lines = []
    for index, item in enumerate(CART, start=1):
        lines.append(f"{index}. {item['name']} x {item['quantity']}")

    return "\n".join(lines)
