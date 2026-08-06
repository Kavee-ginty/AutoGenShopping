# Shopping Agent ToDo

This file is the handoff guide for continuing development from Module 1 onward.

Current status: Module 0 is working. The repo uses OpenRouter.

## Quick Start

From the repo root:

```powershell
cd shopping-agent
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python app.py
```

Edit `.env` before running:

```env
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
MODEL=google/gemma-4-26b-a4b-it:free
```

Expected result:

```text
Hello there! How can I help you with your shopping today?
```

## Current Code

Important files:

```text
shopping-agent/
    app.py
    llm_config.py
    requirements.txt
    agents/
        shopping_agent.py
    backend/
    mcp/
    prompts/
    tools/
    workflows/
```

What each file does now:

- `app.py`: starts the app and sends one test message.
- `llm_config.py`: loads OpenRouter settings from `.env`.
- `agents/shopping_agent.py`: creates the AutoGen `AssistantAgent`.

Use these environment variables:

```python
OPENROUTER_API_KEY
OPENROUTER_BASE_URL
MODEL
```

## Important AutoGen Version Note

This project is using the newer AutoGen packages:

```text
autogen-agentchat
autogen-ext[openai]
```

Use imports like this:

```python
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
```

Do not copy old tutorial code directly if it uses:

```python
from autogen import AssistantAgent, UserProxyAgent
```


## OpenRouter Model Setup

OpenRouter is OpenAI-compatible, but AutoGen does not recognize OpenRouter model names automatically. That is why `model_info` is required.

Current setup:

```python
model_client = OpenAIChatCompletionClient(
    api_key=OPENROUTER_API_KEY,
    base_url=OPENROUTER_BASE_URL,
    model=MODEL,
    model_info={
        "vision": False,
        "function_calling": False,
        "json_output": False,
        "structured_output": False,
        "family": ModelFamily.UNKNOWN,
    },
)
```

Keep `function_calling` as `False` for the current free Gemma model unless you test a tool call successfully.

If Module 2 needs real AutoGen tool calling, switch to a model that supports tool calls and then update:

```python
"function_calling": True
```

Only set a capability to `True` after the model actually supports it.

## Development Rules

Keep the project simple:

- Finish one module before starting the next one.
- Do not add multiple agents until Module 7.
- Do not add MCP until Module 6.
- Do not add memory until it is needed.
- Prefer one clear Python function over a framework.
- If something fails, return a friendly message instead of crashing.

The target architecture stays:

```text
User
-> Shopping Assistant
-> Intent Classification
-> Workflow
-> Python Tool
-> Kapruka MCP
```

## Module 1: Shopping Conversation

Goal: make the app feel like a simple shopping chatbot with no tools.

Files to edit:

```text
shopping-agent/app.py
shopping-agent/agents/shopping_agent.py
```

Tasks:

- Replace the hard-coded `"Hello!"` test with a terminal chat loop.
- Keep one `ShoppingAssistant`.
- Improve the system message so the assistant asks shopping-related questions.
- Do not add tools yet.

Example `app.py` shape:

```python
import asyncio
import sys

from autogen_agentchat.messages import TextMessage

from agents.shopping_agent import shopping_agent

sys.stdout.reconfigure(encoding="utf-8")


async def main():
    print("Shopping assistant is ready. Type 'exit' to stop.")

    while True:
        user_text = input("You: ").strip()

        if user_text.lower() in {"exit", "quit"}:
            print("Assistant: Bye!")
            break

        response = await shopping_agent.on_messages(
            [TextMessage(content=user_text, source="User")],
            cancellation_token=None,
        )

        print("Assistant:", response.chat_message.content)


if __name__ == "__main__":
    asyncio.run(main())
```

Example system message:

```python
system_message="""
You are a friendly shopping assistant.

Help customers search for products, compare options, and decide what to buy.

For now, you do not have access to a product database.
If the user asks for real products, explain that product search will be added in the next modules.

Keep responses short and friendly.
"""
```

Done when:

- The user can type multiple messages.
- The assistant answers in a shopping-assistant style.
- The app exits cleanly when the user types `exit`.

## Module 2: Tool Calling

Goal: teach the assistant to call simple Python functions.

Important: the current Gemma free model may not support tool calling through OpenRouter. If tool calls fail, use the manual workflow version below until a tool-capable model is selected.

Create:

```text
shopping-agent/tools/shopping_tools.py
```

Start with dummy tools:

```python
def search_products(query: str) -> str:
    """Search for products by name."""
    return f"Dummy search results for: {query}"


def add_to_cart(product_name: str) -> str:
    """Add a product to the cart."""
    return f"Added {product_name} to the cart."


def track_order(order_id: str) -> str:
    """Track an order by ID."""
    return f"Order {order_id} is being processed."
```

If using a tool-capable model, register the tools in `agents/shopping_agent.py`:

```python
from tools.shopping_tools import add_to_cart, search_products, track_order

shopping_agent = AssistantAgent(
    name="ShoppingAssistant",
    model_client=model_client,
    tools=[search_products, add_to_cart, track_order],
    system_message="You are a friendly shopping assistant. Use tools when needed.",
)
```

If the model does not support tool calling yet, call the functions manually from `app.py` for learning:

```python
from tools.shopping_tools import search_products

if user_text.lower().startswith("search "):
    query = user_text[7:]
    print("Assistant:", search_products(query))
    continue
```

Done when:

- `search rice cooker` returns a dummy product-search response.
- The app does not crash for empty or strange input.

## Module 3: Fake Shopping Backend

Goal: replace dummy strings with local fake data.

Create:

```text
shopping-agent/backend/fake_store.py
```

Example:

```python
PRODUCTS = [
    {"id": "p1", "name": "Rice Cooker", "price": 14990, "stock": 5},
    {"id": "p2", "name": "Wireless Mouse", "price": 3990, "stock": 12},
    {"id": "p3", "name": "Tea Pack", "price": 1200, "stock": 30},
]


def find_products(query: str) -> list[dict]:
    query = query.lower().strip()
    return [product for product in PRODUCTS if query in product["name"].lower()]
```

Then update `tools/shopping_tools.py`:

```python
from backend.fake_store import find_products


def search_products(query: str) -> str:
    """Search for products by name."""
    products = find_products(query)

    if not products:
        return "No products found."

    lines = []
    for product in products:
        lines.append(f'{product["id"]}: {product["name"]} - LKR {product["price"]}')

    return "\n".join(lines)
```

Done when:

- Product search returns real fake-store items.
- Unknown products return `"No products found."`.

## Module 4: Intent Classification

Goal: decide which workflow should handle the user's message.

Do not create a classifier agent yet. Use a simple Python function first.

Create:

```text
shopping-agent/workflows/intent.py
```

Example:

```python
def classify_intent(message: str) -> str:
    message = message.lower()

    if "track" in message or "order" in message:
        return "track_order"

    if "cart" in message or "add" in message:
        return "add_to_cart"

    if "search" in message or "find" in message or "buy" in message:
        return "search_product"

    return "chat"
```

Done when:

- Search messages go to search.
- Cart messages go to cart.
- Tracking messages go to tracking.
- General messages still go to the assistant.

## Module 5: Shopping Workflows

Goal: put shopping actions into separate workflow files.

Create only the files needed:

```text
shopping-agent/workflows/search.py
shopping-agent/workflows/cart.py
shopping-agent/workflows/tracking.py
```

Example `workflows/search.py`:

```python
from tools.shopping_tools import search_products


def handle_search(message: str) -> str:
    query = message.replace("search", "").replace("find", "").strip()

    if not query:
        return "What product should I search for?"

    return search_products(query)
```

Example router in `app.py`:

```python
from workflows.intent import classify_intent
from workflows.search import handle_search

intent = classify_intent(user_text)

if intent == "search_product":
    print("Assistant:", handle_search(user_text))
    continue
```

Done when:

- Each shopping task has a small workflow function.
- `app.py` routes to workflows before asking the AI.

## Module 6: Kapruka MCP Integration

Goal: replace the fake backend with Kapruka MCP.

Do not change the workflows first. Replace the tool implementation behind them.

Keep this shape:

```text
workflow -> tool function -> fake backend or MCP
```

Example direction:

```python
def search_products(query: str) -> str:
    """Search products using Kapruka MCP."""
    # Replace fake_store lookup here when the MCP server is ready.
    return "Kapruka MCP search will go here."
```

Done when:

- Workflows still call `search_products()`.
- Only the tool internals know whether data comes from fake data or MCP.

## Module 7: Multiple Agents

Goal: add specialized agents only if workflows are no longer enough.

Do not start here.

Possible future agents:

- Shopping assistant
- Intent classifier
- Customer support assistant

Add a second agent only when one assistant plus workflows becomes hard to understand.

## Module 8: Production Improvements

Goal: polish after the learning modules work.

Possible tasks:

- Better error messages
- Logging
- Tests
- Safer config validation
- Conversation memory
- Deployment notes

Do not add these early.

## Small Checks Before Sharing

Run:

```powershell
cd shopping-agent
venv\Scripts\activate
python app.py
```

Check:

- `.env` is not committed.
- `.env.example` has placeholders only.
- README and this file describe the OpenRouter setup.
- The app starts from a fresh clone after `pip install -r requirements.txt`.

## References

Checked on 2026-08-06:

- AutoGen official install docs: https://github.com/microsoft/autogen
- AutoGen model docs: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/models.html
- AutoGen migration guide for OpenAI-compatible APIs: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/migration-guide.html
