# Module 6 Developer Guide: Kapruka MCP Integration & Architecture Blueprint

Welcome to **Module 6: Kapruka MCP Integration** of the **Shopping Agent Project**!

This guide provides a comprehensive step-by-step roadmap for developers transitioning our Shopping Assistant from a local fake backend (`backend/fake_store.py`) to a standardized **Model Context Protocol (MCP)** integration with the Kapruka e-commerce ecosystem.

---

## 📑 Table of Contents
1. [Core Philosophy & Architecture](#1-core-philosophy--architecture)
2. [What is Model Context Protocol (MCP)?](#2-what-is-model-context-protocol-mcp)
3. [Strict Layering & Zero-Workflow-Touch Rule](#3-strict-layering--zero-workflow-touch-rule)
4. [Kapruka MCP Architecture & Component Design](#4-kapruka-mcp-architecture--component-design)
5. [Detailed Implementation Specifications](#5-detailed-implementation-specifications)
   - [MCP Dependencies & Setup](#mcp-dependencies--setup)
   - [Kapruka MCP Server (`mcp/kapruka_server.py`)](#kapruka-mcp-server-mcpkapruka_serverpy)
   - [MCP Client Bridge (`mcp/mcp_client.py`)](#mcp-client-bridge-mcpmcp_clientpy)
   - [Updating Tools Layer (`tools/*.py`)](#updating-tools-layer-toolspy)
6. [Parallel Developer Workload Division (Zero-Conflict Strategy)](#6-parallel-developer-workload-division-zero-conflict-strategy)
7. [Team Coding Rules & Conventions](#7-team-coding-rules--conventions)
8. [Verification & Verification Checklist](#8-verification--verification-checklist)

---

## 1. Core Philosophy & Architecture

As defined in [`AGENTS.md`](file:///d:/Uni/AutoGen/AGENTS.md), our primary goals remain **Simplicity, Readability, Correctness, and Learning Value**.

- **Beginner-Friendly**: Keep MCP server and client setups simple and explicit.
- **Strict Layering**: Decouple intent routing, workflows, tools, and protocols.
- **Workflow Stability**: Workflow handlers in `workflows/` **MUST NOT** be modified when integrating MCP. Only tool implementations in `tools/` change their backend transport.

### Modular Data Flow Architecture

```text
               User Input
                   │
                   ▼
         app.py (Chat Loop)
                   │
                   ▼
     workflows/intent.py (Module 4)
      [Intent Classification via LLM]
                   │
   ┌───────────────┼───────────────┬───────────────┬───────────────┐
   ▼               ▼               ▼               ▼               ▼
search_workflow  cart_workflow  tracking_wf     feedback_wf     chat_workflow
 (Module 5)      (Module 5)     (Module 5)      (Module 5)      (Module 5)
   │               │               │               │               │
   └───────────────┼───────────────┴───────────────┘               │
                   ▼                                               │
             tools/*.py (Module 2)                                 │
   (search_product, add_to_cart, track_order, etc.)                │
                   │                                               │
                   ▼ [JSON-RPC over Stdio / Async Client]           │
          mcp/mcp_client.py                                        │
                   │                                               │
                   ▼                                               │
       mcp/kapruka_server.py (Module 6)                            │
      [Kapruka MCP Protocol Server]                                │
                   │                                               │
                   ▼                                               │
       Kapruka Store Service / Backend                             │
                                                                   │
                   └───────────────────┬───────────────────────────┘
                                       ▼
                              User Text Response
```

---

## 2. What is Model Context Protocol (MCP)?

**Model Context Protocol (MCP)** is an open standard created by Anthropic that enables AI models and application frameworks to safely interact with external data sources, tools, and services using standardized JSON-RPC 2.0 messages over standard I/O (stdio) or HTTP/SSE transports.

### Key Concepts in MCP:
1. **MCP Server**: Exposes resources, prompts, and callable tools (e.g. searching products, tracking orders, submitting feedback).
2. **MCP Client**: Discovers server capabilities, invokes tools with arguments, and receives structured execution results.
3. **Tool Schema**: Describes function parameters (JSON Schema) so agents/tools know how to format parameters correctly.

---

## 3. Strict Layering & Zero-Workflow-Touch Rule

In **Module 5**, workflows were constructed to call standard Python functions in `tools/` rather than accessing `backend/fake_store.py` directly:

- `workflows/search_workflow.py` $\rightarrow$ calls `tools.search_product.search_product()`
- `workflows/cart_workflow.py` $\rightarrow$ calls `tools.add_to_cart.add_to_cart()` and `tools.view_cart.view_cart()`
- `workflows/tracking_workflow.py` $\rightarrow$ calls `tools.track_order.track_order()`
- `workflows/feedback_workflow.py` $\rightarrow$ calls `tools.submit_feedback.submit_feedback()`

### The Golden Rule of Module 6:
> **Workflows in `workflows/` DO NOT CHANGE.**
> The transition to MCP occurs entirely inside `tools/` and `mcp/`. The workflows remain 100% agnostic to whether data is sourced from a fake dictionary or an active Kapruka MCP Server.

---

## 4. Kapruka MCP Architecture & Component Design

Module 6 introduces a new directory `shopping-agent/mcp/` containing:

```text
shopping-agent/mcp/
    __init__.py
    kapruka_server.py    # Exposes Kapruka shopping tools via FastMCP / MCP SDK
    catalog_tools.py     # Product search & feedback MCP tool implementations (Dev A)
    order_cart_tools.py  # Cart management & order tracking MCP tool implementations (Dev B)
    mcp_client.py        # Client connection bridge (Dev B)
```

---

## 5. Detailed Implementation Specifications

### MCP Dependencies & Setup

Add `mcp` (Official Python MCP SDK) to `requirements.txt`:

```text
autogen-agentchat
autogen-ext[openai]
mcp>=1.0.0
```

---

### Kapruka MCP Server (`mcp/kapruka_server.py`)

Using `FastMCP` from the `mcp` package for a beginner-friendly setup:

```python
# mcp/kapruka_server.py
from mcp.server.fastmcp import FastMCP
from mcp.catalog_tools import register_catalog_tools
from mcp.order_cart_tools import register_order_cart_tools

mcp = FastMCP("Kapruka Shopping Service")

# Register modular tools defined by Dev A and Dev B
register_catalog_tools(mcp)
register_order_cart_tools(mcp)

if __name__ == "__main__":
    mcp.run()
```

---

### MCP Client Bridge (`mcp/mcp_client.py`)

The client bridge handles spawning or connecting to `kapruka_server.py` and calling tools:

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

### Updating Tools Layer (`tools/*.py`)

Tool functions in `tools/` will now wrap calls to `mcp_client.py` synchronously or asynchronously, keeping the public function signature identical for workflows:

```python
# tools/search_product.py
import asyncio
from mcp.mcp_client import call_kapruka_tool

def search_product(query: str, budget_max: int | None = None) -> str:
    """Search Kapruka products via MCP server."""
    try:
        results = asyncio.run(call_kapruka_tool(
            "search_kapruka_products", 
            {"query": query, "budget_max": budget_max}
        ))
        return str(results)
    except Exception as err:
        return f"MCP Search failed: {err}"
```

---

## 6. Parallel Developer Workload Division (Zero-Conflict Strategy)

To allow 2 developers to work on Module 6 **simultaneously without Git merge conflicts**, the workload is split cleanly along functional boundaries with **zero overlapping file edits**.

```text
                                     dev Branch
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 ▼                                               ▼
   feature/mcp-catalog-feedback                    feature/mcp-client-orders
         (Developer A)                                   (Developer B)
                 │                                               │
   ├── mcp/catalog_tools.py                        ├── mcp/mcp_client.py
   ├── tools/search_product.py                     ├── mcp/order_cart_tools.py
   ├── tools/get_product_details.py                ├── tools/add_to_cart.py
   └── tools/submit_feedback.py                    ├── tools/view_cart.py
                                                   ├── tools/track_order.py
                                                   └── tools/cancel_order.py
                 │                                               │
                 └───────────────────────┬───────────────────────┘
                                         ▼
                                  No File Overlap
                               (0 Git Merge Conflicts)
```

### 👤 Developer A: Product Catalog & Feedback Domain
* **Branch Name**: `feature/mcp-catalog-feedback`
* **Assigned Files**:
  1. `mcp/catalog_tools.py` **[NEW]**: Implements `search_kapruka_products`, `get_product_details`, `submit_kapruka_feedback` tools.
  2. `tools/search_product.py` **[MODIFY]**: Updates tool implementation to call MCP `search_kapruka_products`.
  3. `tools/get_product_details.py` **[MODIFY]**: Updates tool implementation to call MCP `get_product_details`.
  4. `tools/submit_feedback.py` & `tools/llm_parse_feedback.py` **[MODIFY]**: Updates feedback tools to route through MCP client.

### 👤 Developer B: Client Infrastructure, Cart & Orders Domain
* **Branch Name**: `feature/mcp-client-orders`
* **Assigned Files**:
  1. `mcp/mcp_client.py` **[NEW]**: Implements async Stdio Client Session bridge `call_kapruka_tool()`.
  2. `mcp/order_cart_tools.py` **[NEW]**: Implements `manage_kapruka_cart`, `get_kapruka_order_status`, `cancel_kapruka_order` MCP tools.
  3. `tools/add_to_cart.py`, `tools/view_cart.py`, `tools/remove_from_cart.py`, `tools/clear_cart.py` **[MODIFY]**: Updates cart tools to route through MCP client.
  4. `tools/track_order.py`, `tools/cancel_order.py` **[MODIFY]**: Updates tracking & cancellation tools to route through MCP client.

---

## 7. Team Coding Rules & Conventions

1. **Strict File Ownership**: Dev A and Dev B touch **only** their assigned files.
2. **Keep Imports Decoupled**: `workflows/` must **never** import `mcp/` or `backend/`. `tools/` is the single adapter layer.
3. **Fail Gracefully**: If the MCP server process fails to launch or returns an error, the tool must catch the exception and return a friendly user message.
4. **Explicit Data Schema**: Use JSON-serializable dictionaries for tool arguments.

---

## 8. Verification & Verification Checklist

- [ ] `mcp/kapruka_server.py` runs standalone via `python mcp/kapruka_server.py`.
- [ ] `mcp/mcp_client.py` successfully initializes stdio session and invokes tools.
- [ ] `tools/` function signatures match Module 2/5 specs so workflows require zero changes.
- [ ] Merge `feature/mcp-catalog-feedback` and `feature/mcp-client-orders` into `dev` cleanly with zero merge conflicts.
- [ ] Running `python app.py` allows full end-to-end shopping interaction backed by Kapruka MCP.
