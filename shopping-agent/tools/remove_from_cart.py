from backend.fake_store import (
    find_product,
    find_products,
    get_cart_quantity,
    remove_cart_item,
)


def remove_from_cart(product_name: str, quantity: int = 1) -> str:
    """Remove a product from the cart.

    Args:
        product_name: The product to remove.
        quantity: How many to remove. Defaults to 1.
    """
    product_name = (product_name or "").strip()

    if not product_name:
        return "Which product should I remove from the cart?"

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return "Quantity must be a whole number."

    if quantity < 1:
        return "Quantity must be at least 1."

    product = find_product(product_name)

    if not product:
        matches = find_products(product_name)

        if len(matches) > 1:
            return "I found more than one product. Please use the product ID."

        return "That product is not in your cart."

    cart_quantity = get_cart_quantity(product["id"])

    if cart_quantity == 0:
        return f"{product['name']} is not in your cart."

    if quantity > cart_quantity:
        quantity = cart_quantity

    remove_cart_item(product["id"], quantity)

    return f"Removed {quantity} x {product['name']} from the cart."
