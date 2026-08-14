import json
from pathlib import Path

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
        "status": "Packed and ready for delivery",
        "item": "Classic Chocolate Fudge Gateaux Cake",
    },
    {
        "id": "ORD-1002",
        "status": "Out for delivery",
        "item": "Lumirosa Pink Rose Chrysanthemum Bouquet",
    },
    {
        "id": "ORD-1003",
        "status": "Delivered",
        "item": "Golden Grocery Treats Hamper",
    },
]

CART = []

# Persist feedback to a simple JSON file so entries survive restarts
FEEDBACK_FILE = Path(__file__).parent / "feedback.json"
try:
    if FEEDBACK_FILE.exists():
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
            FEEDBACK = json.load(f)
            if not isinstance(FEEDBACK, list):
                FEEDBACK = []
    else:
        FEEDBACK = []
except Exception:
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
    entry = {
        "product_id": product_id,
        "rating": rating,
        "comment": comment,
    }
    FEEDBACK.append(entry)
    # persist to disk; best-effort (don't crash on IO errors)
    try:
        FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
            json.dump(FEEDBACK, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


