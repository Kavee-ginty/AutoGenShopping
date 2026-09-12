import asyncio
from mcp_tools.mcp_client import tool_calling

def get_categories() -> str:
    result = asyncio.run(tool_calling("list_categories", {"depth": 1}, "markdown"))
    return result['message']

def delivery_cities(query: str) -> str:
    result = asyncio.run(tool_calling("delivery_cities", {"query": query, "limit": 25}, "markdown"))
    return result['message']

def search_products(search_query: str, max_price: float, category: str = "", limit: int = 10, currency : str = "LKR", in_stock : bool = 0,  sort: str = "relevance", include_stubs : bool = 0) -> str:
    result = asyncio.run(tool_calling("search_products", {"q": search_query, "category": category, "limit": limit,
"cursor": "a", "currency": currency, "min_price": 0.0, "max_price": max_price, "in_stock_only": in_stock, "sort": sort, "include_stubs": include_stubs}, "markdown"))
    return result['message']

def _normalize_mcp_product(item: dict) -> dict:
    price_info = item.get("price") or {}
    amount = price_info.get("amount")
    price = int(amount) if amount is not None else 0

    if item.get("in_stock"):
        stock = item.get("stock_level") or "available"
    else:
        stock = 0

    return {
        "id": item.get("id", ""),
        "name": item.get("name", ""),
        "price": price,
        "stock": stock,
    }

def search_products_list(search_query: str, max_price: float, category: str = "", limit: int = 10, currency: str = "LKR", in_stock: bool = False, sort: str = "relevance", include_stubs: bool = False) -> list[dict]:
    result = asyncio.run(tool_calling("search_products", {"q": search_query, "category": category, "limit": limit,
"cursor": "a", "currency": currency, "min_price": 0.0, "max_price": max_price, "in_stock_only": in_stock, "sort": sort, "include_stubs": include_stubs}, "json"))

    if result["status"] != "success":
        return []

    message = result["message"]
    if not isinstance(message, dict):
        return []

    return [_normalize_mcp_product(item) for item in message.get("results", [])]

def get_product(p_id: str, currency : str = "LKR", type : str = "") -> str:
    result = asyncio.run(tool_calling("get_product", {"product_id": p_id, "currency": currency, "type": type}, "markdown"))
    return result['message']

def track_order(order_number: str) -> str:
    result = asyncio.run(tool_calling("track_order", {"order_number": order_number}, "markdown"))
    return result['message']

def create_order(p_id: str, recipient: str,address: str, city: str, date: str, sender: str, location_type: str = "house", msg: str = "", quantity: int = 1, instructions: str = "", icing_text: str = "", currency : str = "LKR") -> str:
    cart = [{"product_id": p_id, "quantity": quantity, "icing_text": icing_text}]
    kcity = delivery_cities(city)
    delivery = address + kcity + location_type + date + instructions

    result = asyncio.run(tool_calling("create_order", { "fcart": cart,"recipient": recipient, "delivery": delivery, "sender": sender, "gift_message": msg, "currency": currency}, "markdown"))
    return result['message']
