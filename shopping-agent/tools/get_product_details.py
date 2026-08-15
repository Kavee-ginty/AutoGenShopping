from backend.fake_store import (
    average_rating,
    find_product,
    get_product_feedback,
)


def _feedback_lines(product: dict) -> list[str]:
    rating = average_rating(product["id"])
    feedback_items = get_product_feedback(product["id"])
    lines = [f"{product['id']}: {product['name']}"]

    if rating is None:
        lines.append("Rating: No ratings yet.")
        return lines

    lines.append(f"Rating: {rating:.1f}/5 from {len(feedback_items)} review(s).")

    if feedback_items:
        lines.append("Feedback:")
        for item in feedback_items:
            comment = item.get("comment") or "No comment."
            lines.append(f"- {item['rating']}/5: {comment}")

    return lines


def get_product_details(product_name: str, kind: str = "all") -> str:
    """Show stock or customer feedback for a product.

    Args:
        product_name: Product ID or name.
        kind: "stock", "feedback", or "all".
    """
    product_name = (product_name or "").strip()

    if not product_name:
        return "Which product would you like details for?"

    product = find_product(product_name)

    if not product:
        return "Product not found. Please search for it first."

    if kind == "stock":
        return f"{product['name']} has {product['stock']} in stock."

    if kind == "feedback":
        return "\n".join(_feedback_lines(product))

    lines = [f"{product['name']} has {product['stock']} in stock."]
    lines.extend(_feedback_lines(product))
    return "\n".join(lines)
