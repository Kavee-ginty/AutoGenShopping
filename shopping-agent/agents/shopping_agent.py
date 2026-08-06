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

Your job is to help customers purchase products.

Keep responses short and friendly.
""",
)
