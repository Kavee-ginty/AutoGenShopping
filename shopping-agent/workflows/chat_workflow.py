from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken

from agents.shopping_agent import shopping_agent


async def handle_chat(conversation: list[TextMessage]) -> str:
    """Delegate general shopping advice and greetings to the Shopping Assistant."""
    try:
        response = await shopping_agent.on_messages(
            conversation,
            cancellation_token=CancellationToken(),
        )
        chat_message = response.chat_message
        if isinstance(chat_message, TextMessage):
            return chat_message.content
        return chat_message.to_text()
    except Exception:
        return "I'm having trouble responding right now. How else can I help with your shopping?"
