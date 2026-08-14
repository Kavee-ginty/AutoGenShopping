from autogen_agentchat.messages import TextMessage

from agents.intent_classifier_agent import intent_classifier_agent


VALID_INTENTS = {
    "search_product",
    "add_to_cart",
    "view_cart",
    "track_order",
    "submit_feedback",
    "chat",
}


async def classify_intent(message: str) -> str:
    """Use the intent classifier agent to choose the correct workflow."""
    if not message.strip():
        return "chat"
    try:
        response = await intent_classifier_agent.on_messages(
            [TextMessage(content=message, source="User")],
            cancellation_token=None,
        )

        intent = response.chat_message.content.strip().lower()
    except Exception:
        # LLM unavailable or errored (rate limit, network); fall back to heuristics
        intent = None

    if not intent:
        # simple keyword-based fallback
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

    if intent not in VALID_INTENTS:
        return "chat"

    return intent