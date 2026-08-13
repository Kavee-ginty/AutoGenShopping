from datetime import date

PRODUCTS = [
    {
        "id": "kp1",
        "name": "Classic Chocolate Fudge Gateaux Cake",
        "category": "cakes",
        "price": 5600,
        "stock": 6,
        "occasions": ["birthday", "party"],
        "for": ["boy", "girl", "child", "brother", "sister"],
    },
    {
        "id": "kp2",
        "name": "Lumirosa Pink Rose Chrysanthemum Bouquet",
        "category": "flowers",
        "price": 14900,
        "stock": 4,
        "occasions": ["birthday", "wedding", "party"],
        "for": ["girl", "sister", "mom"],
    },
    {
        "id": "kp3",
        "name": "Golden Grocery Treats Hamper",
        "category": "grocery hampers",
        "price": 25300,
        "stock": 3,
        "occasions": ["party"],
        "for": ["mom", "dad"],
    },
    {
        "id": "kp4",
        "name": "Sanford 6 In 1 Multifunctional Air Fryer",
        "category": "electronics",
        "price": 47500,
        "stock": 5,
        "occasions": [],
        "for": ["mom", "dad"],
    },
    {
        "id": "kp5",
        "name": "Garfield Plush Soft Toy - 16 Inches",
        "category": "soft toys",
        "price": 3500,
        "stock": 10,
        "occasions": ["birthday"],
        "for": ["boy", "girl", "child", "brother", "sister"],
    },
    {
        "id": "kp6",
        "name": "Executive Office Notebook Gift Box",
        "category": "gift sets",
        "price": 5900,
        "stock": 8,
        "occasions": [],
        "for": ["dad"],
    },
    {
        "id": "kp7",
        "name": "Ikea Gnarp 3 Piece Kitchen Utensil Set",
        "category": "home and lifestyle",
        "price": 1500,
        "stock": 12,
        "occasions": [],
        "for": ["mom", "dad"],
    },
    {
        "id": "kp8",
        "name": "Royal Ribbon Red Velvet Layer Cake",
        "category": "cakes",
        "price": 6200,
        "stock": 5,
        "occasions": ["birthday", "wedding", "party"],
        "for": ["girl", "sister"],
    },
    {
        "id": "kp9",
        "name": "Heavenly Ribbon Black Forest Gateau Cake",
        "category": "cakes",
        "price": 4900,
        "stock": 8,
        "occasions": ["birthday", "party"],
        "for": ["boy", "girl", "child"],
    },
    {
        "id": "kp10",
        "name": "Mini Chocolate Cupcake Box",
        "category": "cakes",
        "price": 1800,
        "stock": 15,
        "occasions": ["birthday", "party"],
        "for": ["boy", "girl", "child", "brother", "sister"],
    },
    {
        "id": "kp11",
        "name": "Kids Cartoon Birthday Cake",
        "category": "cakes",
        "price": 2500,
        "stock": 7,
        "occasions": ["birthday"],
        "for": ["boy", "child", "brother"],
    },
    {
        "id": "kp12",
        "name": "Simple Vanilla Tea Cake",
        "category": "cakes",
        "price": 1500,
        "stock": 10,
        "occasions": ["birthday", "party"],
        "for": ["boy", "girl", "child", "brother", "sister"],
    },
    {
        "id": "kp13",
        "name": "Butter Icing Birthday Cake",
        "category": "cakes",
        "price": 2900,
        "stock": 6,
        "occasions": ["birthday"],
        "for": ["boy", "girl", "child", "brother"],
    },
]

ORDERS = [
    {
        "id": "ORD-1001",
        "item": "Classic Chocolate Fudge Gateaux Cake",
        "status": "Packed and ready for delivery",
        "order_date": "2026-08-10",
        "estimated_delivery": "2026-08-14",
        "delivery_service": "Kapruka Delivery",
        "tracking_history": [
            {"date": "2026-08-10", "update": "Order placed"},
            {"date": "2026-08-11", "update": "Preparing order"},
            {"date": "2026-08-12", "update": "Packed and ready for delivery"},
        ],
    },
    {
        "id": "ORD-1002",
        "item": "Lumirosa Pink Rose Chrysanthemum Bouquet",
        "status": "Out for delivery",
        "order_date": "2026-08-09",
        "estimated_delivery": "2026-08-13",
        "delivery_service": "Domex",
        "tracking_history": [
            {"date": "2026-08-09", "update": "Order packed"},
            {"date": "2026-08-10", "update": "Handed to courier"},
            {"date": "2026-08-13", "update": "Out for delivery"},
        ],
    },
    {
        "id": "ORD-1003",
        "item": "Golden Grocery Treats Hamper",
        "status": "Delivered",
        "order_date": "2026-08-06",
        "estimated_delivery": "2026-08-11",
        "delivery_service": "Pronto",
        "tracking_history": [
            {"date": "2026-08-08", "update": "Packed and ready for delivery"},
            {"date": "2026-08-10", "update": "Out for delivery"},
            {"date": "2026-08-11", "update": "Delivered"},
        ],
    },
    {
        "id": "ORD-1004",
        "item": "Sanford 6 In 1 Multifunctional Air Fryer",
        "status": "Delayed",
        "delay_reason": "Weather conditions",
        "order_date": "2026-08-08",
        "estimated_delivery": "2026-08-16",
        "delivery_service": "Koombiyo",
        "tracking_history": [
            {"date": "2026-08-08", "update": "Order packed"},
            {"date": "2026-08-09", "update": "Handed to courier"},
            {"date": "2026-08-12", "update": "Delayed due to weather conditions"},
        ],
    },
]

CART = []
FEEDBACK = [
    {
        "product_id": "kp1",
        "rating": 5,
        "comment": "Rich chocolate, perfect for birthdays.",
    },
    {
        "product_id": "kp10",
        "rating": 5,
        "comment": "Great value cupcakes for a kids party.",
    },
    {
        "product_id": "kp11",
        "rating": 4,
        "comment": "My little brother loved the cartoon design.",
    },
    {
        "product_id": "kp12",
        "rating": 4,
        "comment": "Simple and tasty. Good for a small budget.",
    },
]


def clean_text(value: str) -> str:
    return (value or "").lower().strip()


def matches_category(product: dict, category: str) -> bool:
    category = clean_text(category)
    name = clean_text(product["name"])
    product_category = clean_text(product["category"])
    short_category = category.rstrip("s")

    return (
        category in name
        or category in product_category
        or short_category in name
        or short_category in product_category
    )


def find_products(query: str) -> list[dict]:
    query = clean_text(query)

    if not query:
        return []

    results = []

    for product in PRODUCTS:
        name = clean_text(product["name"])
        category = clean_text(product["category"])

        if query in name or query in category:
            results.append(product)

    return results


def find_products_filtered(
    category: str,
    budget_max: int | None = None,
    occasion: str | None = None,
    for_who: str | None = None,
    limit: int = 5,
) -> list[dict]:
    category = clean_text(category)
    occasion = clean_text(occasion) if occasion else ""
    for_who = clean_text(for_who) if for_who else ""

    results = []

    for product in PRODUCTS:
        if category and not matches_category(product, category):
            continue

        if budget_max is not None and product["price"] > budget_max:
            continue

        if occasion:
            occasions = [clean_text(item) for item in product.get("occasions", [])]
            if occasion not in occasions:
                continue

        if for_who:
            audience = [clean_text(item) for item in product.get("for", [])]
            if for_who not in audience:
                continue

        results.append(product)
        if len(results) >= limit:
            break

    return results


def get_product_feedback(product_id: str) -> list[dict]:
    return [item for item in FEEDBACK if item["product_id"] == product_id]


def average_rating(product_id: str) -> float | None:
    items = get_product_feedback(product_id)

    if not items:
        return None

    total = 0
    for item in items:
        total += item["rating"]

    return total / len(items)


def find_product(product_name: str) -> dict | None:
    product_name = clean_text(product_name)

    if not product_name:
        return None

    for product in PRODUCTS:
        if product_name == clean_text(product["id"]):
            return product

        if product_name == clean_text(product["name"]):
            return product

    matches = find_products(product_name)

    if len(matches) == 1:
        return matches[0]

    return None


def get_cart_quantity(product_id: str) -> int:
    quantity = 0

    for item in CART:
        if item["product_id"] == product_id:
            quantity += item["quantity"]

    return quantity


def add_cart_item(product_id: str, quantity: int) -> None:
    for item in CART:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            return

    CART.append({"product_id": product_id, "quantity": quantity})


def get_cart_items() -> list[dict]:
    cart_items = []

    for item in CART:
        product = find_product(item["product_id"])

        if product:
            cart_items.append(
                {
                    "id": product["id"],
                    "name": product["name"],
                    "price": product["price"],
                    "quantity": item["quantity"],
                    "line_total": product["price"] * item["quantity"],
                }
            )

    return cart_items


def find_order(order_id: str) -> dict | None:
    order_id = clean_text(order_id)

    if not order_id:
        return None

    for order in ORDERS:
        if clean_text(order["id"]) == order_id:
            return order

    return None


INELIGIBLE_CANCEL_STATUSES = {
    "out for delivery",
    "delivered",
    "cancelled",
}


def cancel_order_by_id(
    order_id: str, reason: str = "No reason provided"
) -> dict | None:
    order = find_order(order_id)

    if order is None:
        return None

    status = (order.get("status") or "").strip().lower()

    if status in INELIGIBLE_CANCEL_STATUSES:
        return order

    today = date.today().isoformat()

    order["status"] = "Cancelled"
    order["cancelled_reason"] = reason
    order["cancelled_date"] = today

    history = order.get("tracking_history")
    if not isinstance(history, list):
        history = []
        order["tracking_history"] = history

    history.append(
        {
            "date": today,
            "update": f"Order cancelled by customer (REASON :- {reason})",
        }
    )

    return order


def save_feedback(product_id: str, rating: int, comment: str) -> None:
    FEEDBACK.append(
        {
            "product_id": product_id,
            "rating": rating,
            "comment": comment,
        }
    )
