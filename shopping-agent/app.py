import asyncio
import sys
import warnings

from workflows.intent import classify_intent
from tools.search_product import search_product
from tools.add_to_cart import add_to_cart
from tools.view_cart import view_cart
from tools.track_order import track_order
from tools.submit_feedback import submit_feedback

from autogen_agentchat.messages import TextMessage

warnings.filterwarnings(
    "ignore",
    message=r"Resolved model mismatch:.*",
)

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

        intent = await classify_intent(user_text)
        # print("Detected intent:", intent)

        if intent == "search_product":
            print("Assistant:", search_product(user_text))
            print()
            continue

        if intent == "add_to_cart":
            print("Assistant:", add_to_cart(user_text))
            print()
            continue

        if intent == "view_cart":
            print("Assistant:", view_cart())
            print()
            continue

        if intent == "track_order":
            print("Assistant:", track_order(user_text))
            print()
            continue

        if intent == "submit_feedback":
            print(
                "Assistant:",
                "Please tell me the product name, rating from 1 to 5, and your comment.",
            )
            print()
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
