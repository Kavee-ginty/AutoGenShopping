from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ModelFamily
from autogen_ext.models.openai import OpenAIChatCompletionClient

from llm_config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    MODEL,
)
from tools.add_to_cart import add_to_cart
from tools.search_product import search_product
from tools.submit_feedback import submit_feedback
from tools.track_order import track_order
from tools.view_cart import view_cart

# Use the OpenAI-compatible client against OpenRouter's API
model_client = OpenAIChatCompletionClient(
    api_key=OPENROUTER_API_KEY,
    base_url=OPENROUTER_BASE_URL,
    model=MODEL,
    model_info={
        "vision": False,
        "function_calling": True,
        "json_output": False,
        "structured_output": False,
        "family": ModelFamily.UNKNOWN,
    },
)

shopping_agent = AssistantAgent(
    name="ShoppingAssistant",
    model_client=model_client,
    tools=[search_product, add_to_cart, view_cart, track_order, submit_feedback],
    system_message="""
You are a friendly shopping assistant.

Your job is to help customers decide what to buy. Ask what they need, then ask
useful follow-up questions about budget, preferences, and how they plan to use
the product. Help them compare options using general knowledge when you can.

You have access to these tools, and you must use them instead of guessing:

- search_product(query): find products. Use it when the user asks to search,
  find, or buy a product.
- add_to_cart(product_name, quantity): add a product to the cart.
- view_cart(): show what is currently in the cart.
- track_order(order_id): check the status of an order.
- submit_feedback(product_name, rating, comment): record feedback about a product.

When the user asks for something a tool can do, call the right tool and report
its result back to the user in a natural way. If the user changes or cancels a
request, do not call a tool.

Keep replies to 2-4 short sentences.
Ask at most one follow-up question at a time.
Do not write long explanations unless the user asks for details.

Default reply style:
- 2-4 short sentences.
- One question maximum.
- No long paragraphs.
- Use bullet points only when comparing options.
""",
)
