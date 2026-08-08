import asyncio
import sys

from autogen_agentchat.messages import TextMessage

from agents.shopping_agent import shopping_agent

sys.stdout.reconfigure(encoding="utf-8")


async def get_assistant_reply(conversation):
    """Ask the agent, retrying if the free model returns an empty response."""
    for attempt in range(3):
        try:
            response = await shopping_agent.on_messages(
                conversation,
                cancellation_token=None,
            )
            return response.chat_message.content
        except Exception:
            if attempt < 2:
                await asyncio.sleep(10)

    return "Sorry, the assistant is unavailable right now. Please try again."


async def main():
    print("Shopping assistant is ready. Type 'exit' to stop.")

    # Keep the full conversation so follow-up messages make sense.
    conversation = []

    while True:
        user_text = input("You: ").strip()

        if user_text.lower() in {"exit", "quit"}:
            print("Assistant: Bye!")
            break

        if not user_text:
            print("Assistant: Please type a message, or 'exit' to stop.")
            continue

        conversation.append(TextMessage(content=user_text, source="User"))

        assistant_text = await get_assistant_reply(conversation)
        conversation.append(
            TextMessage(content=assistant_text, source="ShoppingAssistant")
        )
        if len(conversation) > 20:
            conversation = conversation[-20:]

        print("Assistant:", assistant_text)
        print()


if __name__ == "__main__":
    asyncio.run(main())
