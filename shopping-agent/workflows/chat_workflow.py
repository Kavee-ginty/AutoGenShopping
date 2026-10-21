from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken

from agents.product_explainer_agent import explainer_agent
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


async def explain_with_report(user_text: str, report: str) -> str:
    """Ask the Product Explainer to answer from a web report."""
    prompt = (
        f"Customer question: {user_text}\n\n"
        f"Web report:\n{report}\n\n"
        "Answer from the report only."
    )
    response = await explainer_agent.on_messages(
        [TextMessage(content=prompt, source="User")],
        cancellation_token=CancellationToken(),
    )
    return response.chat_message.to_text()
