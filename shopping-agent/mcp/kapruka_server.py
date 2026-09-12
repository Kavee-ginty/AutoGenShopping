# Kapruka MCP Server Entrypoint Skeleton

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    FastMCP = None

mcp = FastMCP("Kapruka Shopping Service") if FastMCP else None

# Developer A registers catalog_tools here:
# from mcp.catalog_tools import register_catalog_tools
# register_catalog_tools(mcp)

# Developer B registers order_cart_tools here:
# from mcp.order_cart_tools import register_order_cart_tools
# register_order_cart_tools(mcp)

if __name__ == "__main__":
    if mcp:
        mcp.run()
    else:
        print("MCP SDK not installed. Run 'pip install mcp'")
