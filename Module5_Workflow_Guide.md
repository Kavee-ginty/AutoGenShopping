# Module 5 Developer Guide: Shopping Workflows & Architecture Blueprint

Welcome to the **Shopping Agent Project**! This guide is designed for developers joining the repository to implement **Module 5: Shopping Workflows**. 

The goal of Module 5 is to move business logic out of `app.py` and into modular, single-responsibility workflow files that interface with python tools and the backend.

---

## 📑 Table of Contents
1. [Core Philosophy & Architecture](#1-core-philosophy--architecture)
2. [Global Settings & Environment Variables](#2-global-settings--environment-variables)
3. [Strict Layering & MCP Blueprinting](#3-strict-layering--mcp-blueprinting)
4. [Detailed Workflow Specifications](#4-detailed-workflow-specifications)
   - [Search Workflow (`search_workflow.py`)](#search-workflow-search_workflowpy)
   - [Cart Workflow (`cart_workflow.py`)](#cart-workflow-cart_workflowpy)
   - [Tracking Workflow (`tracking_workflow.py`)](#tracking-workflow-tracking_workflowpy)
   - [Feedback Workflow (`feedback_workflow.py`)](#feedback-workflow-feedback_workflowpy)
   - [Chat Workflow (`chat_workflow.py`)](#chat-workflow-chat_workflowpy)
5. [Intent Classifier Prerequisite & Router Integration (`app.py`)](#5-intent-classifier-prerequisite--router-integration-apppy)
6. [Team Coding Rules & Conventions](#6-team-coding-rules--conventions)
7. [Real-World Execution Trace Example](#7-real-world-execution-trace-example)

---

## 1. Core Philosophy & Architecture

As outlined in `AGENTS.md`, our primary goals are **Simplicity, Readability, Correctness, and Learning Value**. 

- **Beginner-Friendly**: Write explicit code. Avoid complex OOP inheritance, deep abstractions, generic workflow engines, or clever one-liners.
- **Functionality First**: Workflows should be simple functions that accept string inputs and return clear text responses.
- **Single Responsibility**: Each workflow file handles exactly one intent domain.

### System Architecture Flow

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
   ▼               ▼               ▼               ▼               ▼
tools/search_    tools/add_      tools/track_    tools/submit_   agents/
product.py       to_cart.py      order.py        feedback.py     shopping_agent
   │               │               │               │               │
   └───────────────┴───────┬───────┴───────────────┘               │
                           ▼                                       │
                backend/fake_store.py                              │
             (Swapped to MCP in Module 6)                          │
                           │                                       │
                           └───────────────────┬───────────────────┘
                                               ▼
                                      User Text Response
```

---

## 2. Global Settings & Environment Variables

Workflows **must never hardcode environment configurations** or instantiate their own LLM clients. All shared configurations and instances belong in their designated files.

### Configuration Imports Cheat Sheet:

| Resource | File Source | Import Statement |
| :--- | :--- | :--- |
| **OpenRouter Key & Model Name** | `llm_config.py` | `from llm_config import OPENROUTER_API_KEY, MODEL` |
| **Model Client (LLM)** | `agents/shopping_agent.py` | `from agents.shopping_agent import model_client` |
| **Shopping Agent (Assistant)** | `agents/shopping_agent.py` | `from agents.shopping_agent import shopping_agent` |
| **Tools** | `tools/` | `from tools.<tool_name> import <function_name>` |

---

## 3. Strict Layering & MCP Blueprinting

To prepare for **Module 6 (Kapruka MCP Integration)**:
- **Rule 1**: Workflow functions **MUST NOT** import `backend/fake_store.py` directly.
- **Rule 2**: Workflow functions **MUST ONLY** import functions from `tools/`.

When we upgrade to Kapruka MCP in Module 6, we will modify the python files inside `tools/` to call the MCP server. **Your workflow files in `workflows/` will remain completely unchanged.**

---

## 4. Detailed Workflow Specifications

### Search Workflow (`workflows/search_workflow.py`)

* **Target Intent**: `search_product`
* **Tool Dependency**: `from tools.search_product import search_product`

#### Implementation Responsibilities:
1. Extract search terms from input (e.g. strip common prefix words like *"search for"*, *"find"*, *"I want to buy"*).
2. Validate that a search query exists. If empty, return a friendly prompt asking what product the user wants to find.
3. Call `search_product(query)`.
4. Return formatted product results.

#### Sample Code Blueprint:
```python
from tools.search_product import search_product

def handle_search(message: str) -> str:
    """Extract query keywords and invoke search tool."""
    # Clean noise words
    query = message.lower()
    for prefix in ["search for", "search", "find", "buy", "look for"]:
        if query.startswith(prefix):
            query = query[len(prefix):].strip()
            break
            
    query = query.strip()

    if not query:
        return "What product are you looking for today?"

    return search_product(query)
```

---

### Cart Workflow (`workflows/cart_workflow.py`)

* **Target Intents**: `add_to_cart`, `view_cart`
* **Tool Dependencies**: 
  - `from tools.add_to_cart import add_to_cart`
  - `from tools.view_cart import view_cart`

#### How Cart Data Operates in Development:
The cart uses an in-memory list (`CART = []`) in `backend/fake_store.py`. Items added via `add_to_cart()` persist during the active process session so developers can add multiple items and view subtotal summaries without needing a database.

#### Implementation Responsibilities:
1. Route between viewing cart vs. adding to cart.
2. For `add_to_cart`: Parse item name and optional numeric quantity (default to 1 if unspecified).
3. Call `add_to_cart(product_name, quantity)`.
4. For `view_cart`: Call `view_cart()` tool directly.

#### Sample Code Blueprint:
```python
import re
from tools.add_to_cart import add_to_cart
from tools.view_cart import view_cart

def handle_cart(intent: str, message: str) -> str:
    """Handle viewing and adding items to the shopping cart."""
    if intent == "view_cart":
        return view_cart()

    # Extract quantity if specified (e.g., "add 2 cakes")
    quantity = 1
    match = re.search(r'\b(\d+)\b', message)
    if match:
        quantity = int(match.group(1))

    # Strip action phrases to find product name
    product_name = message.lower()
    for phrase in ["add to cart", "add", "put in cart", "buy"]:
        product_name = product_name.replace(phrase, "")
    
    # Clean remaining digits and whitespace
    product_name = re.sub(r'\b\d+\b', '', product_name).strip()

    if not product_name:
        return "Please specify which product you would like to add to your cart."

    return add_to_cart(product_name, quantity)
```

---

### Tracking Workflow (`workflows/tracking_workflow.py`)

* **Target Intent**: `track_order`
* **Tool Dependency**: `from tools.track_order import track_order`

#### How Trackable Orders Work in Development:
Because full checkout/payment flows are introduced in later modules, `backend/fake_store.py` provides pre-seeded test orders (`ORDERS`) so developers can test the tracking workflow immediately:

| Order ID | Status | Item |
| :--- | :--- | :--- |
| `ORD-1001` | *Packed and ready for delivery* | Classic Chocolate Fudge Gateaux Cake |
| `ORD-1002` | *Out for delivery* | Lumirosa Pink Rose Chrysanthemum Bouquet |
| `ORD-1003` | *Delivered* | Golden Grocery Treats Hamper |

If a user asks about an unknown order (e.g. `ORD-9999`), `track_order()` returns `"Order ORD-9999 not found."`

#### Implementation Responsibilities:
1. Scan text for order ID patterns (e.g., `ORD-1001` or digits like `1001`).
2. If order ID is missing, inform the user and request their order number.
3. Call `track_order(order_id)`.

#### Sample Code Blueprint:
```python
import re
from tools.track_order import track_order

def handle_tracking(message: str) -> str:
    """Extract order ID and fetch order tracking status."""
    # Look for patterns like ORD-1001 or standalone 4-digit numbers
    match = re.search(r'(ORD-\d{4}|\b\d{4}\b)', message.upper())

    if not match:
        return "Please provide your Order ID (e.g., ORD-1001) so I can check its delivery status."

    order_id = match.group(1)
    if not order_id.startswith("ORD-"):
        order_id = f"ORD-{order_id}"

    return track_order(order_id)
```

---

### Feedback Workflow (`workflows/feedback_workflow.py`)

* **Target Intent**: `submit_feedback`
* **Tool Dependency**: `from tools.submit_feedback import submit_feedback`

#### Implementation Responsibilities:
1. Extract rating number (1 to 5 stars).
2. Extract product name and review comment text.
3. Provide default values if information is partially missing.
4. Call `submit_feedback(product_name, rating, comment)`.

#### Sample Code Blueprint:
```python
import re
from tools.submit_feedback import submit_feedback

def handle_feedback(message: str) -> str:
    """Extract review details and record customer feedback."""
    # Find rating integer between 1 and 5
    match = re.search(r'\b([1-5])\b', message)
    rating = int(match.group(1)) if match else 5

    # Extract product name or fallback to generic
    product_name = "General Service"
    if "for" in message.lower():
        parts = message.lower().split("for")
        if len(parts) > 1:
            product_name = parts[1].split()[0].capitalize()

    comment = message.strip()
    return submit_feedback(product_name, rating, comment)
```

---

### Chat Workflow (`workflows/chat_workflow.py`)

* **Target Intent**: `chat` (Fallback / General Advice)
* **Dependency**: `from agents.shopping_agent import shopping_agent`

#### Implementation Responsibilities:
1. Asynchronous workflow execution.
2. Passes conversation history to `shopping_agent.on_messages()`.
3. Handles retries or exceptions gracefully without crashing.

#### Sample Code Blueprint:
```python
from autogen_agentchat.messages import TextMessage
from agents.shopping_agent import shopping_agent

async def handle_chat(conversation: list[TextMessage]) -> str:
    """Delegate general shopping advice and greetings to the AutoGen Shopping Assistant."""
    try:
        response = await shopping_agent.on_messages(
            conversation,
            cancellation_token=None,
        )
        return response.chat_message.content
    except Exception as err:
        return "I'm having trouble responding right now. How else can I help with your shopping?"
```

---

## 5. Intent Classifier Prerequisite & Router Integration (`app.py`)

### Module 4 Prerequisite: `workflows/intent.py`
Before workflows can execute in Module 5, **Module 4** must classify the incoming user message into one of the recognized intents using the LLM classifier:

```python
# workflows/intent.py
from autogen_core.models import SystemMessage, UserMessage
from agents.shopping_agent import model_client

VALID_INTENTS = {
    "search_product",
    "add_to_cart",
    "view_cart",
    "track_order",
    "submit_feedback",
    "chat",
}

INTENT_SYSTEM_PROMPT = """
You are an intent classification engine for an e-commerce shopping platform.
Classify the user's input message into EXACTLY ONE of the following categories:
- search_product
- add_to_cart
- view_cart
- track_order
- submit_feedback
- chat

Respond ONLY with the category key name. Do NOT include extra words or punctuation.
"""

async def classify_intent(message: str) -> str:
    """Classify user message intent asynchronously using AutoGen model_client."""
    if not message.strip():
        return "chat"
    try:
        response = await model_client.create(
            messages=[
                SystemMessage(content=INTENT_SYSTEM_PROMPT),
                UserMessage(content=message, source="User"),
            ]
        )
        intent = response.content.strip().lower()
        return intent if intent in VALID_INTENTS else "chat"
    except Exception:
        return "chat"
```

---

### What Does "Routing in `app.py`" Mean?

"Routing" means `app.py` acts as the **central traffic controller** of the application. 

Instead of passing every user prompt directly to the LLM agent, `app.py`:
1. Sends the raw prompt to `classify_intent(user_text)`.
2. Inspects the returned `intent` string.
3. **Routes** (dispatches) the request to the matching Module 5 workflow function.

### Full `app.py` Integration Example

```python
# app.py
import asyncio
import sys
from autogen_agentchat.messages import TextMessage

from workflows.intent import classify_intent
from workflows.search_workflow import handle_search
from workflows.cart_workflow import handle_cart
from workflows.tracking_workflow import handle_tracking
from workflows.feedback_workflow import handle_feedback
from workflows.chat_workflow import handle_chat

sys.stdout.reconfigure(encoding="utf-8")

async def process_user_input(user_text: str, conversation: list) -> str:
    """Route user input to the correct workflow based on Module 4 intent classification."""
    
    # Step 1: Classify user intent via Module 4 LLM Classifier
    intent = await classify_intent(user_text)
    
    # Step 2: Route message to corresponding Module 5 Workflow
    if intent == "search_product":
        return handle_search(user_text)

    elif intent in {"add_to_cart", "view_cart"}:
        return handle_cart(intent, user_text)

    elif intent == "track_order":
        return handle_tracking(user_text)

    elif intent == "submit_feedback":
        return handle_feedback(user_text)

    else:
        # Fallback for 'chat' -> pass conversation history to LLM ShoppingAssistant agent
        conversation.append(TextMessage(content=user_text, source="User"))
        reply = await handle_chat(conversation)
        conversation.append(TextMessage(content=reply, source="ShoppingAssistant"))
        return reply

async def main():
    print("Shopping Assistant ready. Type 'exit' to quit.")
    conversation = []

    while True:
        user_text = input("You: ").strip()
        if user_text.lower() in {"exit", "quit"}:
            print("Assistant: Bye!")
            break
        if not user_text:
            continue

        response = await process_user_input(user_text, conversation)
        print(f"Assistant: {response}\n")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 6. Team Coding Rules & Conventions

Before submitting pull requests for Module 5 workflows, verify:

1. **Fail Gracefully**: Workflows must **never** throw unhandled exceptions or crash `app.py`. Wrap risky logic in try-except blocks and return human-readable error messages.
2. **Explicit Type Hints**: Use simple Python type hints (`message: str -> str`).
3. **No Unnecessary Abstractions**: Use plain Python functions. Do not create unnecessary Workflow classes or custom state machines.
4. **Clean File Naming**: Name files in `workflows/` using lowercase snake_case (e.g. `search_workflow.py`, `cart_workflow.py`).
5. **No Direct Backend Access**: Verify that your workflow imports from `tools/` and **never** from `backend.fake_store`.

---

## 7. Real-World Execution Trace Example

To understand the practical advantage of combining **Module 4 (LLM Intent Classifier)** and **Module 5 (Workflow Logic)**, consider this multi-turn user conversation:

### Sample Conversation
```text
You: i want to track an irder
Assistant: Please provide your Order ID (e.g., ORD-1001) so I can check its delivery status.

You: 1001
Assistant: ORD-1001: Classic Chocolate Fudge Gateaux Cake - Packed and ready for delivery.
```

### Execution Trace & Edge-Case Handling Breakdown

| Turn & Input | Behind-the-Scenes Action | Why Module 4 & 5 Handled It Smoothly |
| :--- | :--- | :--- |
| **Turn 1: `"i want to track an irder"`** | 1. `classify_intent()` recognizes typo `"irder"` $\rightarrow$ outputs `track_order`.<br>2. `handle_tracking()` finds no ID pattern $\rightarrow$ requests Order ID. | **LLM Classifier Resilience**: Tolerates spelling mistakes without breaking. |
| **Turn 2: `"1001"`** | 1. `classify_intent()` routes `"1001"` $\rightarrow$ `track_order`.<br>2. `handle_tracking()` matches `1001` $\rightarrow$ auto-normalizes to `ORD-1001`.<br>3. `track_order("ORD-1001")` returns status. | **Workflow ID Normalization**: Prevents *"Order not found"* errors when users omit the `ORD-` prefix. |

Happy Coding! 🚀
