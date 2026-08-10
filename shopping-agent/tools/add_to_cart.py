from backend.fake_store import (
    add_cart_item,
    find_product,
    find_products,
    get_cart_quantity,
)


def add_to_cart(product_name: str, quantity: int = 1) -> str:
    """Add a product to the cart.

    Args:
        product_name: The name of the product to add.
        quantity: How many to add. Defaults to 1.
    """
    product_name = (product_name or "").strip()

    if not product_name:
        return "Which product should I add to the cart?"

    # The model may pass the quantity as a string, so convert it first.
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

        return "Product not found. Please search for it first."

    cart_quantity = get_cart_quantity(product["id"])

    if cart_quantity + quantity > product["stock"]:
        available = product["stock"] - cart_quantity
        if available < 1:
            return f"{product['name']} is out of stock."

        return f"Only {available} more available for {product['name']}."

    add_cart_item(product["id"], quantity)

    return f"Added {quantity} x {product['name']} to the cart."
