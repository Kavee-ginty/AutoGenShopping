from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

from llm_config import (
    AZURE_API_KEY,
    AZURE_ENDPOINT,
    AZURE_DEPLOYMENT,
    AZURE_API_VERSION,
)

model_client = AzureOpenAIChatCompletionClient(
    azure_endpoint=AZURE_ENDPOINT,
    api_key=AZURE_API_KEY,
    azure_deployment=AZURE_DEPLOYMENT,
    api_version=AZURE_API_VERSION,
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