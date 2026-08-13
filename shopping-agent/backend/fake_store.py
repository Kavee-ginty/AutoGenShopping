PRODUCTS = [
    {
        "id": "kp1",
        "name": "Classic Chocolate Fudge Gateaux Cake",
        "category": "cakes",
        "price": 5600,
        "stock": 6,
    },
    {
        "id": "kp2",
        "name": "Lumirosa Pink Rose Chrysanthemum Bouquet",
        "category": "flowers",
        "price": 14900,
        "stock": 4,
    },
    {
        "id": "kp3",
        "name": "Golden Grocery Treats Hamper",
        "category": "grocery hampers",
        "price": 25300,
        "stock": 3,
    },
    {
        "id": "kp4",
        "name": "Sanford 6 In 1 Multifunctional Air Fryer",
        "category": "electronics",
        "price": 47500,
        "stock": 5,
    },
    {
        "id": "kp5",
        "name": "Garfield Plush Soft Toy - 16 Inches",
        "category": "soft toys",
        "price": 3500,
        "stock": 10,
    },
    {
        "id": "kp6",
        "name": "Executive Office Notebook Gift Box",
        "category": "gift sets",
        "price": 5900,
        "stock": 8,
    },
    {
        "id": "kp7",
        "name": "Ikea Gnarp 3 Piece Kitchen Utensil Set",
        "category": "home and lifestyle",
        "price": 1500,
        "stock": 12,
    },
    {
        "id": "kp8",
        "name": "Royal Ribbon Red Velvet Layer Cake",
        "category": "cakes",
        "price": 6200,
        "stock": 5,
    },
    {
        "id": "kp9",
        "name": "Heavenly Ribbon Black Forest Gateau Cake",
        "category": "cakes",
        "price": 4900,
        "stock": 8,
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
]

CART = []
FEEDBACK = []


def clean_text(value: str) -> str:
    return (value or "").lower().strip()


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


def save_feedback(product_id: str, rating: int, comment: str) -> None:
    FEEDBACK.append(
        {
            "product_id": product_id,
            "rating": rating,
            "comment": comment,
        }
    )
