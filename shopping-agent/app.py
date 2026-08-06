import asyncio
import sys

from autogen_agentchat.agents import UserProxyAgent
from autogen_agentchat.messages import TextMessage

from agents.shopping_agent import shopping_agent

sys.stdout.reconfigure(encoding="utf-8")


async def main():

    user = UserProxyAgent("User")

    response = await shopping_agent.on_messages(
        [TextMessage(content="Hello!", source="User")],
        cancellation_token=None,
    )

    print(response.chat_message.content)


if __name__ == "__main__":
    asyncio.run(main())
