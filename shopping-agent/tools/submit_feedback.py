from backend.fake_store import find_product, save_feedback


def submit_feedback(product_name: str, rating: int, comment: str = "") -> str:
    """Submit feedback for a product.

    Args:
        product_name: The name of the product the feedback is about.
        rating: A score from 1 to 5.
        comment: Optional written feedback.
    """
    product_name = (product_name or "").strip()
    comment = (comment or "").strip()

    if not product_name:
        return "Which product is the feedback about?"

    # The model may pass the rating as a string, so convert it first.
    try:
        rating = int(rating)
    except (TypeError, ValueError):
        return "Rating must be a whole number from 1 to 5."

    if rating < 1 or rating > 5:
        return "Rating must be a number from 1 to 5."

    product = find_product(product_name)

    if not product:
        return "Product not found. Please search for it first."

    save_feedback(product["id"], rating, comment)

    if comment:
        return (
            f"Thanks! Feedback for {product['name']} "
            f"(rating {rating}/5): {comment}"
        )

    return f"Thanks! Feedback for {product['name']} (rating {rating}/5)."
