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
- remove_from_cart
- clear_cart
- track_order
- submit_feedback
- chat

Rules:
- Use search_product ONLY when the user asks for a specific product, item name, or category explicitly (e.g., "search for cakes", "find air fryer", "show me soft toys").
- Use add_to_cart when the user wants to add an item to the cart.
- Use view_cart when the user wants to see the cart or checkout basket.
- Use remove_from_cart when the user wants to remove, delete, take out, or reduce an item in the cart.
- Use clear_cart when the user wants to empty the whole cart or remove everything from the cart.
- Use track_order when the user asks about an order or delivery status.
- Use submit_feedback when the user wants to review, rate, complain about, or give feedback.
- Use chat for greetings, open-ended gift requests or advice (e.g., "I am looking for a birthday gift", "what should I buy?"), recommendations, general questions, or anything that requires interactive follow-up questions.

Return only the intent name.
Do not explain your answer.
""",
)