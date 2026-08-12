from autogen_agentchat.agents import AssistantAgent

from agents.shopping_agent import model_client


intent_classifier_agent = AssistantAgent(
    name="IntentClassifier",
    model_client=model_client,
    system_message="""
You classify shopping customer messages into one intent.

Return only one of these intent names:

- search_product
- add_to_cart
- view_cart
- track_order
- submit_feedback
- chat

Rules:
- Use search_product when the user wants to find, search, browse, or buy a product.
- Use add_to_cart when the user wants to add an item to the cart.
- Use view_cart when the user wants to see the cart or checkout basket.
- Use track_order when the user asks about an order or delivery status.
- Use submit_feedback when the user wants to review, rate, complain about, or give feedback.
- Use chat for greetings, general questions, or anything that does not match a shopping action.

Return only the intent name.
Do not explain your answer.
""",
)