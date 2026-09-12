import asyncio
from mcp import Client
import json

TOOLS = {
    "list_categories": "kapruka_list_categories",
    "get_product": "kapruka_get_product",
    "search_products": "kapruka_search_products",
    "create_order": "kapruka_create_order",
    "track_order": "kapruka_track_order",
    "options_card": "kapruka_render_options_card",
    "delivery_cities": "kapruka_list_delivery_cities",
    "check_delivery": "kapruka_check_delivery",
}

async def tool_calling(tool: str, param: dict, response_format: str = "json") -> dict:
    if tool not in TOOLS:
        return {"status": "failed", "message": "tool not found"}
    
    async with Client("https://mcp.kapruka.com/mcp") as client:
        result = await client.call_tool(TOOLS[tool], {"params": {**param, "response_format": response_format}})
        
        if result.is_error:
            return {"status": "failed", "message": result.content[0].text}
        else:
            if response_format == "json":
                return {"status": "success", "message": json.loads(result.content[0].text)}
            else:
                return {"status": "success", "message": result.content[0].text}
                
