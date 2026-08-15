import asyncio
import json
import re
from typing import Optional, Dict, Any

from autogen_agentchat.messages import TextMessage


async def parse_with_llm_async(message: str, retries: int = 2, timeout: int = 8) -> Optional[Dict[str, Any]]:
    """Best-effort async LLM parse using the project `shopping_agent`.

    Returns a dict like {"product": str|None, "rating": int|None, "comment": str|None}
    or None on failure. This is strictly best-effort and will not raise.
    """
    try:
        # import here so tools don't require the agent at import-time
        from agents.shopping_agent import shopping_agent

        prompt = (
            "Extract the product name, rating (1-5) and optional comment from the following user message."
            " Return strictly a JSON object with keys: product, rating, comment. Use null for missing fields."
            f"\n\nMessage: {message}"
        )

        conv = [TextMessage(content=prompt, source="User")]

        for attempt in range(retries + 1):
            try:
                resp = await shopping_agent.on_messages(conv)
                text = resp.chat_message.content
                # heuristically find a JSON object in the assistant reply
                m = re.search(r"\{[\s\S]*\}", text)
                if m:
                    blob = m.group(0)
                else:
                    blob = text.strip()

                # try to coerce into json
                try:
                    parsed = json.loads(blob)
                except Exception:
                    # attempt to fix common issues (single quotes -> double)
                    try:
                        parsed = json.loads(blob.replace("'", '"'))
                    except Exception:
                        parsed = None

                if parsed and isinstance(parsed, dict):
                    # normalize keys
                    return {
                        "product": parsed.get("product") or parsed.get("product_name") or None,
                        "rating": parsed.get("rating") if isinstance(parsed.get("rating"), int) else None,
                        "comment": parsed.get("comment") or None,
                    }

            except Exception:
                await asyncio.sleep(1)
                continue

    except Exception:
        return None

    return None


def parse_with_llm(message: str, retries: int = 2, timeout: int = 8) -> Optional[Dict[str, Any]]:
    """Synchronous wrapper that attempts to run the async parser when no event loop is running.

    Returns None if unable to run (e.g., running inside an event loop).
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # don't run nested event loop — caller should use async API instead
            return None
    except Exception:
        # fallback to running
        pass

    try:
        return asyncio.run(parse_with_llm_async(message, retries=retries, timeout=timeout))
    except Exception:
        return None
