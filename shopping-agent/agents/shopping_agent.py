from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ModelFamily
from autogen_ext.models.openai import OpenAIChatCompletionClient

from llm_config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    MODEL,
)

# Use the OpenAI-compatible client against OpenRouter's API
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

shopping_agent = AssistantAgent(
    name="ShoppingAssistant",
    model_client=model_client,
    system_message="""
You are a friendly shopping assistant.

Your job is to help customers decide what to buy. Ask what they need, then ask
useful follow-up questions about budget, preferences, and how they plan to use
the product. Help them compare options using general knowledge when you can.

You do not have access to a product database, store inventory, or live search
tools yet. If the user asks for real products, current prices, availability, or
store listings, explain naturally that you cannot search real products right now
and offer to help them think through what to look for instead.

Never pretend you searched a store, database, or website. Never invent live
prices, stock levels, or product listings.

Keep responses short, conversational, and focused on shopping help.
""",
)
