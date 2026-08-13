from autogen_agentchat.messages import TextMessage
from agents.shopping_agent import shopping_agent


async def handle_chat(conversation: list[TextMessage]) -> str:
    """Delegate general shopping advice and greetings to the Shopping Assistant."""
    try:
        response = await shopping_agent.on_messages(
            conversation,
            cancellation_token=None,
        )
        return response.chat_message.content
    except Exception:
        return "I'm having trouble responding right now. How else can I help with your shopping?"