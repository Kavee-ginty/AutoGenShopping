import asyncio
import sys
import warnings

from workflows.intent import classify_intent
from workflows.search_workflow import handle_search
from workflows.cart_workflow import handle_cart
from workflows.tracking_workflow import handle_tracking
from workflows.feedback_workflow import handle_feedback, handle_feedback_async, is_awaiting_feedback
from workflows.chat_workflow import handle_chat

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

        # If a feedback collection is already in progress, route message to feedback handler
        if is_awaiting_feedback():
            try:
                result = await handle_feedback_async(user_text)
            except Exception:
                result = handle_feedback(user_text)

            if not result:
                print("Assistant: [feedback_workflow is empty/unimplemented]")
                print()
                continue
            print("Assistant:", result)
            print()
            continue

        intent = await classify_intent(user_text)
        print("Detected intent:", intent)

        if intent == "search_product":
            result = handle_search(user_text)
            if not result:
                print("Assistant: [search_workflow is empty/unimplemented]")
                print()
                continue
            print("Assistant:", result)
            print()
            continue

        if intent in {"add_to_cart", "view_cart"}:
            result = handle_cart(intent, user_text)
            if not result:
                print("Assistant: [cart_workflow is empty/unimplemented]")
                print()
                continue
            print("Assistant:", result)
            print()
            continue

        if intent == "track_order":
            result = handle_tracking(user_text)
            if not result:
                print("Assistant: [tracking_workflow is empty/unimplemented]")
                print()
                continue
            print("Assistant:", result)
            print()
            continue

        if intent == "submit_feedback":
            # Use async feedback handler (it will fall back to sync heuristics)
            try:
                from workflows.feedback_workflow import handle_feedback_async

                result = await handle_feedback_async(user_text)
            except Exception:
                # fallback to the synchronous handler
                result = handle_feedback(user_text)

            if not result:
                print("Assistant: [feedback_workflow is empty/unimplemented]")
                print()
                continue
            print("Assistant:", result)
            print()
            continue

        temp_conversation = conversation + [
            TextMessage(content=user_text, source="User")
        ]
        assistant_text = await handle_chat(temp_conversation)

        if not assistant_text:
            print("Assistant: [chat_workflow is empty/unimplemented]")
            print()
            continue

        conversation.append(TextMessage(content=user_text, source="User"))
        conversation.append(
            TextMessage(content=assistant_text, source="ShoppingAssistant")
        )
        if len(conversation) > 20:
            conversation = conversation[-20:]

        print("Assistant:", assistant_text)
        print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, EOFError):
        print("\nAssistant: Bye!")
        sys.exit(0)
