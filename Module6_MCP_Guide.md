# Module 6 Developer Guide: Kapruka MCP Integration & Architecture Blueprint

Welcome to **Module 6: Kapruka MCP Integration** of the **Shopping Agent Project**!

This guide provides a comprehensive step-by-step roadmap for developers transitioning our Shopping Assistant from a local fake backend (`backend/fake_store.py`) to a standardized **Model Context Protocol (MCP)** integration with the Kapruka e-commerce ecosystem, with **interactive startup selection for Dual Data Modes (1: Local / Fake Store, 2: MCP)**.

---

## 📑 Table of Contents
1. [Core Philosophy & Architecture](#1-core-philosophy--architecture)
2. [Dual Backend Modes & Interactive Selection](#2-dual-backend-modes--interactive-selection)
3. [What is Model Context Protocol (MCP)?](#3-what-is-model-context-protocol-mcp)
4. [Strict Layering & Zero-Workflow-Touch Rule](#4-strict-layering--zero-workflow-touch-rule)
5. [Kapruka MCP Architecture & Component Design](#5-kapruka-mcp-architecture--component-design)
6. [Detailed Implementation Specifications](#6-detailed-implementation-specifications)
   - [MCP Dependencies & Configuration Setup](#mcp-dependencies--configuration-setup)
   - [Startup Mode Selector (`app.py` & `config.py`)](#startup-mode-selector-apppy--configpy)
   - [Base Kapruka MCP Server (`mcp/kapruka_server.py`)](#base-kapruka-mcp-server-mcpkapruka_serverpy)
   - [Base MCP Client Bridge (`mcp/mcp_client.py`)](#base-mcp-client-bridge-mcpmcp_clientpy)
   - [Developer A Module (`mcp/catalog_tools.py`)](#developer-a-module-mcpcatalog_toolspy)
   - [Developer B Module (`mcp/order_cart_tools.py`)](#developer-b-module-mcporder_cart_toolspy)
   - [Dual-Mode Tools Layer (`tools/*.py`)](#dual-mode-tools-layer-toolspy)
7. [Zero-Dependency Parallel Workload Division (No Blocking)](#7-zero-dependency-parallel-workload-division-no-blocking)
8. [Interactive Conversation & Execution Trace Example](#8-interactive-conversation--execution-trace-example)
9. [Team Coding Rules & Conventions](#9-team-coding-rules--conventions)
10. [Verification & Checklist](#10-verification--checklist)

---

## 1. Core Philosophy & Architecture

As defined in [`AGENTS.md`](file:///d:/Uni/AutoGen/AGENTS.md), our primary goals remain **Simplicity, Readability, Correctness, and Learning Value**.

- **Beginner-Friendly**: Keep MCP server and client setups simple and explicit.
- **Strict Layering**: Decouple intent routing, workflows, tools, and protocols.
- **Workflow Stability**: Workflow handlers in `workflows/` **MUST NOT** be modified when integrating MCP. Only tool implementations in `tools/` change their backend transport.

---

## 2. Dual Backend Modes & Interactive Selection

> [!IMPORTANT]
> **Interactive Startup Choice**:
> When running `python app.py`, the application prompts the user to select between modes:
> 
> ```text
> =======================================================
> Select Shopping Data Backend:
>   1. Local (Fake Store)
>   2. MCP (Kapruka MCP Integration)
> =======================================================
> Select mode (1 or 2):
> ```

- **Option 1 (`fake_store`)**: Calls `backend/fake_store.py` directly inside Python tools for fast local testing without network/server overhead.
- **Option 2 (`mcp`)**: Routes tool invocations through `mcp/mcp_client.py` via JSON-RPC Stdio transport to `mcp/kapruka_server.py`.

---

## 3. What is Model Context Protocol (MCP)?

**Model Context Protocol (MCP)** is an open standard created by Anthropic that enables AI models and application frameworks to safely interact with external data sources, tools, and services using standardized JSON-RPC 2.0 messages over standard I/O (stdio) or HTTP/SSE transports.

---

## 4. Strict Layering & Zero-Workflow-Touch Rule

In **Module 5**, workflows were constructed to call standard Python functions in `tools/` rather than accessing `backend/fake_store.py` directly.

### The Golden Rule of Module 6:
> **Workflows in `workflows/` DO NOT CHANGE.**
> The workflows remain 100% agnostic to whether the user chose Option 1 (Local) or Option 2 (MCP) at startup.

---

## 5. Kapruka MCP Architecture & Component Design

Module 6 introduces a new directory `shopping-agent/mcp/` containing:

```text
shopping-agent/mcp/
    __init__.py
    kapruka_server.py    # Shared FastMCP server entrypoint (Base Skeleton)
    mcp_client.py        # Shared Stdio client bridge (Base Skeleton)
    catalog_tools.py     # Product search & details MCP tools (Dev A)
    order_cart_tools.py  # Cart management, orders, tracking & feedback MCP tools (Dev B)
```

---

## 6. Detailed Implementation Specifications

### Startup Mode Selector (`app.py` & `config.py`)

In [`config.py`](file:///d:/Uni/AutoGen/shopping-agent/config.py):
```python
import os

DATA_MODE = os.getenv("DATA_MODE", "fake_store").lower().strip()

def set_data_mode(choice: str) -> str:
    global DATA_MODE
    DATA_MODE = "mcp" if choice.strip() == "2" else "fake_store"
    os.environ["DATA_MODE"] = DATA_MODE
    return DATA_MODE
```

---

### Base Kapruka MCP Server (`mcp/kapruka_server.py`)

```python
# mcp/kapruka_server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Kapruka Shopping Service")

# Dev A registers catalog tools:
# from mcp.catalog_tools import register_catalog_tools
# register_catalog_tools(mcp)

# Dev B registers order/cart tools:
# from mcp.order_cart_tools import register_order_cart_tools
# register_order_cart_tools(mcp)

if __name__ == "__main__":
    mcp.run()
```

---

### Base MCP Client Bridge (`mcp/mcp_client.py`)

```python
# mcp/mcp_client.py
import asyncio
import sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_SCRIPT = str(Path(__file__).parent / "kapruka_server.py")

async def call_kapruka_tool(tool_name: str, arguments: dict):
    """Invoke a tool on the Kapruka MCP Server via stdio transport."""
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[SERVER_SCRIPT],
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return result.content
```

---

### Developer A Module (`mcp/catalog_tools.py`)

```python
# mcp/catalog_tools.py
from backend.fake_store import find_products_filtered, find_product

def register_catalog_tools(mcp):
    @mcp.tool()
    def search_kapruka_products(query: str, budget_max: int = None) -> list[dict]:
        """Search products by name/category and budget."""
        return find_products_filtered(category=query, budget_max=budget_max)

    @mcp.tool()
    def get_kapruka_product_details(product_name: str) -> dict:
        """Fetch details for a specific product name or ID."""
        product = find_product(product_name)
        return product or {"error": "Product not found"}
```

---

### Developer B Module (`mcp/order_cart_tools.py`)

```python
# mcp/order_cart_tools.py
from backend.fake_store import (
    add_cart_item,
    get_cart_items,
    find_order,
    cancel_order_by_id,
    save_feedback,
)

def register_order_cart_tools(mcp):
    @mcp.tool()
    def manage_kapruka_cart(action: str, product_id: str = None, quantity: int = 1) -> str:
        """Add items or view cart contents."""
        if action == "add":
            add_cart_item(product_id, quantity)
            return f"Added {quantity} x {product_id} to Kapruka cart."
        elif action == "view":
            items = get_cart_items()
            return str(items) if items else "Your cart is empty."
        return "Invalid action."

    @mcp.tool()
    def get_kapruka_order_status(order_id: str) -> dict:
        """Fetch tracking status for order ID."""
        order = find_order(order_id)
        return order or {"error": f"Order {order_id} not found"}

    @mcp.tool()
    def submit_kapruka_feedback(product_id: str, rating: int, comment: str) -> str:
        """Submit customer feedback and rating."""
        save_feedback(product_id, rating, comment)
        return f"Feedback saved for {product_id} with rating {rating}/5."
```

---

### Dual-Mode Tools Layer (`tools/*.py`)

```python
# tools/search_product.py
import asyncio
from config import DATA_MODE
from backend.fake_store import find_products_filtered, format_product_list

def search_product(query: str, budget_max: int | None = None) -> str:
    """Search products using active DATA_MODE ('fake_store' or 'mcp')."""
    if DATA_MODE == "mcp":
        from mcp.mcp_client import call_kapruka_tool
        try:
            results = asyncio.run(call_kapruka_tool(
                "search_kapruka_products", 
                {"query": query, "budget_max": budget_max}
            ))
            return str(results)
        except Exception as err:
            return f"MCP Search failed: {err}"
            
    # Default: Fake Store Mode (Option 1)
    products = find_products_filtered(category=query, budget_max=budget_max)
    if not products:
        return "No products found."
    return format_product_list(products)
```

---

## 7. Zero-Dependency Parallel Workload Division (No Blocking)

```text
                             Base Skeleton on dev
                 (mcp/kapruka_server.py & mcp/mcp_client.py)
                                      │
                 ┌────────────────────┴────────────────────┐
                 ▼                                         ▼
   feature/mcp-catalog-search                 feature/mcp-cart-orders
         (Developer A)                              (Developer B)
                 │                                         │
   ├── mcp/catalog_tools.py                   ├── mcp/order_cart_tools.py
   ├── tools/search_product.py                ├── tools/add_to_cart.py
   └── tools/get_product_details.py           ├── tools/view_cart.py
                                              ├── tools/remove_from_cart.py
                                              ├── tools/clear_cart.py
                                              ├── tools/track_order.py
                                              ├── tools/cancel_order.py
                                              └── tools/submit_feedback.py
                 │                                         │
                 └────────────────────┬────────────────────┘
                                      ▼
                               0 Line Overlap
                            (0 Dependency Blocking)
```

---

## 8. Interactive Conversation & Execution Trace Example

```text
$ python app.py
=======================================================
Select Shopping Data Backend:
  1. Local (Fake Store)
  2. MCP (Kapruka MCP Integration)
=======================================================
Select mode (1 or 2): 2
--> Mode set to: MCP (Kapruka MCP Integration)

Shopping assistant is ready. Type 'exit' to stop.

You: search for chocolate cakes
Detected intent: search_product

Assistant: 
kp1: Classic Chocolate Fudge Gateaux Cake - LKR 5,600 (stock: 6)
kp8: Royal Ribbon Red Velvet Layer Cake - LKR 6,200 (stock: 5)

You: add 2 classic chocolate fudge gateaux cake to cart
Detected intent: add_to_cart

Assistant: Added 2 x Classic Chocolate Fudge Gateaux Cake to your Kapruka shopping cart.

You: view my cart
Detected intent: view_cart

Assistant: 
Your Shopping Cart (Kapruka MCP Backend):
- Classic Chocolate Fudge Gateaux Cake (x2) - LKR 11,200
Total Charged Subtotal: LKR 11,200

You: exit
Assistant: Bye!
```

---

## 9. Team Coding Rules & Conventions

1. **Do NOT Delete Fake Store**: Keep `backend/fake_store.py` intact for Option 1 (`DATA_MODE="fake_store"`).
2. **Strict File Ownership**: Dev A and Dev B touch **only** their assigned files.
3. **Keep Imports Decoupled**: `workflows/` must **never** import `mcp/` or `backend/`. `tools/` is the single adapter layer.

---

## 10. Verification & Checklist

- [ ] Commit base skeleton `mcp/mcp_client.py` and `mcp/kapruka_server.py` to `dev`.
- [ ] Dev A and Dev B branch from `dev` and work simultaneously with zero blocking.
- [ ] Merge `feature/mcp-catalog-search` and `feature/mcp-cart-orders` into `dev` cleanly with zero merge conflicts.
