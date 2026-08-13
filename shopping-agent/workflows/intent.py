from autogen_agentchat.messages import TextMessage

from agents.intent_classifier_agent import intent_classifier_agent


VALID_INTENTS = {
    "search_product",
    "add_to_cart",
    "view_cart",
    "remove_from_cart",
    "clear_cart",
    "checkout",
    "track_order",
    "submit_feedback",
    "chat",
}


async def classify_intent(message: str) -> str:
    """Use the intent classifier agent to choose the correct workflow."""
    if not message.strip():
        return "chat"

    text = message.lower().strip()
    if "pay now" in text or "pay" in text and "cart" in text:
        return "checkout"
    if "checkout" in text or "place order" in text or "complete order" in text:
        return "checkout"
    if "clear cart" in text or "empty cart" in text:
        return "clear_cart"
    if "remove" in text and "cart" in text:
        return "remove_from_cart"
    if "view cart" in text or "show cart" in text or "cart total" in text:
        return "view_cart"

    response = await intent_classifier_agent.on_messages(
        [TextMessage(content=message, source="User")],
        cancellation_token=None,
    )

    intent = response.chat_message.content.strip().lower()

    if intent not in VALID_INTENTS:
        return "chat"

    return intent