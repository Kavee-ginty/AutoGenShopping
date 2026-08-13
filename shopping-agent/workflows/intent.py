from autogen_agentchat.messages import TextMessage

from agents.intent_classifier_agent import intent_classifier_agent


VALID_INTENTS = {
    "search_product",
    "add_to_cart",
    "view_cart",
    "remove_from_cart",
    "clear_cart",
    "track_order",
    "submit_feedback",
    "chat",
}


async def classify_intent(message: str) -> str:
    """Use the intent classifier agent to choose the correct workflow."""
    if not message.strip():
        return "chat"

    response = await intent_classifier_agent.on_messages(
        [TextMessage(content=message, source="User")],
        cancellation_token=None,
    )

    intent = response.chat_message.content.strip().lower()

    if intent not in VALID_INTENTS:
        return "chat"

    return intent