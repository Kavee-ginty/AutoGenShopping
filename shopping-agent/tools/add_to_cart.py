from tools.store import CART


def add_to_cart(product_name: str, quantity: int = 1) -> str:
    """Add a product to the cart.

    Args:
        product_name: The name of the product to add.
        quantity: How many to add. Defaults to 1.
    """
    product_name = product_name.strip()

    if not product_name:
        return "Which product should I add to the cart?"

    # The model may pass the quantity as a string, so convert it first.
    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return "Quantity must be a whole number."

    if quantity < 1:
        return "Quantity must be at least 1."

    CART.append({"name": product_name, "quantity": quantity})

    return f"Added {product_name} to the cart."
