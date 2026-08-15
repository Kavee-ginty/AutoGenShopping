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
   - [Kapruka MCP Server (`mcp/kapruka_server.py`)](#kapruka-mcp-server-mcpkapruka_serverpy)
   - [MCP Client Bridge (`mcp/mcp_client.py`)](#mcp-client-bridge-mcpmcp_clientpy)
   - [Dual-Mode Tools Layer (`tools/*.py`)](#dual-mode-tools-layer-toolspy)
7. [Parallel Developer Workload Division (Zero-Conflict Strategy)](#7-parallel-developer-workload-division-zero-conflict-strategy)
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

### Modular Data Flow Architecture

```text
               User Input
                   │
                   ▼
     app.py (Select Mode 1 or 2)
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
        ┌──────────┴──────────┐                                    │
        │ Check DATA_MODE     │                                    │
        └─────┬─────────┬─────┘                                    │
    (1: local)         (2: mcp)                                    │
        │                 │                                        │
        ▼                 ▼ [JSON-RPC over Stdio]                  │
backend/fake_store.py   mcp/mcp_client.py                          │
                          │                                        │
                          ▼                                        │
             mcp/kapruka_server.py (Module 6)                      │
                          │                                        │
                          ▼                                        │
              Kapruka E-Commerce Backend                           │
                                                                   │
                   └───────────────────┬───────────────────────────┘
                                       ▼
                              User Text Response
```

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
    kapruka_server.py    # Exposes Kapruka shopping tools via FastMCP / MCP SDK
    catalog_tools.py     # Product search & feedback MCP tool implementations (Dev A)
    order_cart_tools.py  # Cart management & order tracking MCP tool implementations (Dev B)
    mcp_client.py        # Client connection bridge (Dev B)
```

---

## 6. Detailed Implementation Specifications

### Startup Mode Selector (`app.py` & `config.py`)

In [`config.py`](file:///d:/Uni/AutoGen/shopping-agent/config.py):
```python
# config.py
import os

DATA_MODE = os.getenv("DATA_MODE", "fake_store").lower().strip()

def set_data_mode(choice: str) -> str:
    global DATA_MODE
    DATA_MODE = "mcp" if choice.strip() == "2" else "fake_store"
    os.environ["DATA_MODE"] = DATA_MODE
    return DATA_MODE
```

In [`app.py`](file:///d:/Uni/AutoGen/shopping-agent/app.py):
```python
def select_data_mode() -> str:
    print("=" * 55)
    print("Select Shopping Data Backend:")
    print("  1. Local (Fake Store)")
    print("  2. MCP (Kapruka MCP Integration)")
    print("=" * 55)
    choice = input("Select mode (1 or 2): ").strip()
    return set_data_mode(choice)
```

---

### Dual-Mode Tools Layer (`tools/*.py`)

Tool functions in `tools/` check `DATA_MODE` to dispatch between Fake Store vs. MCP:

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

## 7. Parallel Developer Workload Division (Zero-Conflict Strategy)

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

---

## 8. Interactive Conversation & Execution Trace Example

The following trace shows a real terminal chat session running in **MCP Mode (Option 2)** once Module 6 is complete:

### Terminal Trace

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
kp9: Heavenly Ribbon Black Forest Gateau Cake - LKR 4,900 (stock: 8)
kp10: Mini Chocolate Cupcake Box - LKR 1,800 (stock: 15)

You: add 2 classic chocolate fudge gateaux cake to cart
Detected intent: add_to_cart

Assistant: Added 2 x Classic Chocolate Fudge Gateaux Cake to your Kapruka shopping cart.

You: view my cart
Detected intent: view_cart

Assistant: 
Your Shopping Cart (Kapruka MCP Backend):
- Classic Chocolate Fudge Gateaux Cake (x2) - LKR 11,200
Total Charged Subtotal: LKR 11,200

You: track order 1001
Detected intent: track_order

Assistant: 
Order ORD-1001 (Classic Chocolate Fudge Gateaux Cake):
Status: Packed and ready for delivery
Estimated Delivery: 2026-08-14 via Kapruka Delivery

You: 5 stars for fudge cake tasted amazing
Detected intent: submit_feedback

Assistant: Thank you for your review! Feedback recorded for Classic Chocolate Fudge Gateaux Cake with rating 5/5 stars.

You: exit
Assistant: Bye!
```

---

## 9. Team Coding Rules & Conventions

1. **Do NOT Delete Fake Store**: Keep `backend/fake_store.py` intact for Option 1 (`DATA_MODE="fake_store"`).
2. **Strict File Ownership**: Dev A and Dev B touch **only** their assigned files.
3. **Keep Imports Decoupled**: `workflows/` must **never** import `mcp/` or `backend/`. `tools/` is the single adapter layer.
4. **Fail Gracefully**: If the MCP server process fails to launch or returns an error, the tool must catch the exception and return a friendly user message.

---

## 10. Verification & Checklist

- [ ] Run `python app.py`, select Option `1`, and verify Local (Fake Store) interaction.
- [ ] Run `python app.py`, select Option `2`, and verify MCP interaction.
- [ ] Merge `feature/mcp-catalog-feedback` and `feature/mcp-client-orders` into `dev` cleanly with zero merge conflicts.
