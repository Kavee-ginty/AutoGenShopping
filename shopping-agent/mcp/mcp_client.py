import asyncio
import sys
from pathlib import Path

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    # mcp library fallback placeholder until pip install mcp is run
    ClientSession = None
    StdioServerParameters = None
    stdio_client = None

SERVER_SCRIPT = str(Path(__file__).parent / "kapruka_server.py")


async def call_kapruka_tool(tool_name: str, arguments: dict):
    """Generic async helper function to invoke tools on the Kapruka MCP Server."""
    if stdio_client is None:
        raise RuntimeError(
            "The 'mcp' package is not installed. Please run 'pip install mcp'."
        )

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[SERVER_SCRIPT],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return result.content
