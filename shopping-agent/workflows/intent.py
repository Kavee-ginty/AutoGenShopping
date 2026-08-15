import asyncio

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
    "cancel_order",
    "submit_feedback",
    "chat",
}


async def classify_intent(message: str) -> str | None:
    """Use the intent classifier agent to choose the correct workflow."""
    if not message.strip():
        return "chat"

    text = message.lower().strip()
    if "pay now" in text or ("pay" in text and "cart" in text):
        return "checkout"
    if "checkout" in text or "place order" in text or "complete order" in text:
        return "checkout"
    if "clear cart" in text or "empty cart" in text:
        return "clear_cart"
    if "remove" in text and "cart" in text:
        return "remove_from_cart"
    if "view cart" in text or "show cart" in text or "cart total" in text:
        return "view_cart"

    for attempt in range(3):
        try:
            response = await intent_classifier_agent.on_messages(
                [TextMessage(content=message, source="User")],
                cancellation_token=None,
            )

            intent = response.chat_message.content.strip().lower()

            if intent not in VALID_INTENTS:
                return "chat"

            return intent
        except Exception:
            if attempt < 2:
                await asyncio.sleep(10)

    # Keyword-based fallback if LLM is unavailable
    msg = message.lower()
    if any(x in msg for x in ("search", "find", "looking for", "look for")):
        return "search_product"
    if any(x in msg for x in ("add to cart", "add", "cart")) and "feedback" not in msg:
        return "add_to_cart"
    if any(x in msg for x in ("view cart", "show cart", "my cart")):
        return "view_cart"
    if any(x in msg for x in ("track", "tracking", "order status", "where is my")):
        return "track_order"
    if any(x in msg for x in ("rate", "rating", "feedback", "give feedback", "review")):
        return "submit_feedback"
    return "chat"