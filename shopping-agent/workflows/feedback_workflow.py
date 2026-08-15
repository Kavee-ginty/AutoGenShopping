from typing import Optional

from backend.fake_store import find_product, find_products, save_feedback
from tools.submit_feedback import submit_feedback
from tools.llm_parse_feedback import parse_with_llm, parse_with_llm_async
# use backend.find_products for candidate matching
import re


NUMBER_WORDS = {
    'one': 1,
    'two': 2,
    'three': 3,
    'four': 4,
    'five': 5,
}


def _extract_rating(text: str) -> Optional[int]:
    # handle patterns like 'four out of 5' or '4 out of 5' capturing the first number
    m = re.search(r"\b(?P<left>(?:one|two|three|four|five|[1-5]))\b\s*(?:/5|out of\s*(?:[1-5]|one|two|three|four|five)|stars?)", text, re.I)
    if m:
        left = m.group('left').lower()
        if left.isdigit():
            return int(left)
        return NUMBER_WORDS.get(left)

    # numeric like '4', '4/5', '4 stars'
    m = re.search(r'([1-5])\s*(?:/5|stars?)?', text, re.I)
    if m:
        return int(m.group(1))

    # word like 'four'
    m = re.search(r'\b(one|two|three|four|five)\b', text, re.I)
    if m:
        return NUMBER_WORDS.get(m.group(1).lower())

    return None


def _extract_product(text: str) -> Optional[str]:
    # product: label
    m = re.search(r'product\s*[:\-]\s*(.+?)(?:[,.]|$)', text, re.I)
    if m:
        return m.group(1).strip().strip('"\'')
    # quoted
    m = re.search(r'["“](.+?)["”]', text)
    if m:
        return m.group(1).strip()
    # match against catalog
    for p in [prod['name'] for prod in __import__('backend.fake_store', fromlist=['PRODUCTS']).PRODUCTS]:
        if p.lower() in text.lower():
            return p
    return None
    return None


def _extract_comment(text: str, product: Optional[str], rating: Optional[int]) -> Optional[str]:
    comment = text
    if rating is not None:
        # remove rating mentions including word forms like 'four out of 5' or '4/5'
        comment = re.sub(
            r"\b(?:[1-5]|one|two|three|four|five)\b\s*(?:/5|out of\s*(?:[1-5]|one|two|three|four|five)|stars?)?",
            '',
            comment,
            flags=re.I,
        )
    if product:
        comment = comment.replace(product, '')
    comment = re.sub(r'product\s*[:\-]', '', comment, flags=re.I)
    return comment.strip(' .,-\n') or None


def _build_search_query(text: str) -> str:
    """Create a short search query from free text by removing ratings and filler words."""
    if not text:
        return ""
    # remove rating mentions like '4/5', '4 out of 5', '4 stars'
    text = re.sub(r"[1-5]\s*(?:/5|out of 5|stars?)", "", text, flags=re.I)
    # remove punctuation
    text = re.sub(r'["\'.,!?;:\(\)\[\]/\\]', " ", text)
    # basic stopwords
    stop = {"the", "a", "an", "i", "we", "you", "my", "your", "to", "for", "of", "and", "is", "it", "this", "that", "very", "but", "please", "give", "rating", "rate", "rated", "out"}
    # remove number words
    stop.update({k for k in NUMBER_WORDS.keys()})
    words = [w.lower() for w in text.split() if w.strip()]
    words = [w for w in words if w not in stop and not w.isdigit()]
    # take up to 4 meaningful words
    query = " ".join(words[:4])
    return query.strip()


def _is_valid_comment(text: Optional[str]) -> bool:
    if not text:
        return False
    s = text.strip().lower()
    # ignore short boilerplate phrases that indicate intent rather than a comment
    boilerplate = (
        "i want to",
        "i want",
        "i'd like",
        "i want to rate",
        "i want to give",
        "i want to give feedback",
        "i want to submit feedback",
        "i want to give a rating",
        "submit feedback",
        "give feedback",
        "rate",
        "rating",
    )
    if any(b in s for b in boilerplate):
        return False
    # require at least one non-stopword character and not just digits
    if len(s) < 3:
        return False
    if s.isdigit():
        return False
    return True


def _looks_like_product_token(comment: str, product_name: str | None) -> bool:
    """Return True if the comment appears to be just a product token or matches the product name parts."""
    if not comment:
        return False
    s = comment.strip().lower()
    if not s:
        return False
    # single short word that matches product_name tokens
    if product_name:
        pname = product_name.lower()
        if s == pname:
            return True
        # compare against words in product name
        for w in pname.split():
            if s == w:
                return True
    # short single-word comments are likely not real comments
    if len(s.split()) == 1 and len(s) <= 6:
        return True
    return False


def handle_feedback(message: str) -> str:
    # support a simple single-session pending state for multi-turn collection
    global _PENDING
    try:
        _PENDING
    except NameError:
        _PENDING = {"product": None, "rating": None, "comment": None, "awaiting": None}

    # If we're waiting for a specific field, treat this message as an answer
    if _PENDING.get("awaiting"):
        awaiting = _PENDING["awaiting"]
        if awaiting == "product":
            # If the user replied with a short numeric value, treat it as rating, not product
            possible_rating = _extract_rating(message)
            if possible_rating and len(message.strip().split()) == 1:
                _PENDING["rating"] = possible_rating
                return "Which product is the feedback about? Please give the product name or SKU."

            prod = _extract_product(message)
            if prod:
                _PENDING["product"] = prod
            else:
                _PENDING["product"] = message.strip()
            # also try to parse rating/comment from the same reply, but don't overwrite existing values with None
            r = _extract_rating(message)
            if r is not None:
                _PENDING["rating"] = r
            c = _extract_comment(message, _PENDING.get("product"), _PENDING.get("rating"))
            if c:
                _PENDING["comment"] = c
        elif awaiting == "rating":
            r = _extract_rating(message)
            _PENDING["rating"] = r
            # also try to parse product if user supplied it
            p = _extract_product(message)
            if p:
                _PENDING["product"] = p
        elif awaiting == "comment_opt":
            prod = _PENDING.get("product")
            rating_val = _PENDING.get("rating")
            ans = message.strip().lower()
            if ans in ("no", "n", "nope", "nah", "not now"):
                resp = submit_feedback(prod, rating_val, "")
                if isinstance(resp, str) and resp.lower().startswith("product not found"):
                    # try to suggest candidates
                    query = _build_search_query(prod)
                    candidates = []
                    if query:
                        candidates = find_products(query)[:5]
                    if not candidates:
                        words = [w for w in (query or prod).split() if len(w) > 2]
                        seen_ids = set()
                        for w in words:
                            for c in find_products(w)[:5]:
                                if c['id'] not in seen_ids:
                                    candidates.append(c)
                                    seen_ids.add(c['id'])
                                if len(candidates) >= 5:
                                    break
                            if candidates:
                                break

                    if len(candidates) == 1:
                        selected = candidates[0]['name']
                        resp2 = submit_feedback(selected, rating_val, "")
                        _PENDING = {"product": None, "rating": None, "comment": None, "awaiting": None}
                        return resp2

                    if len(candidates) > 1:
                        names = [c['name'] for c in candidates]
                        _PENDING = {"product": prod, "rating": rating_val, "comment": None, "awaiting": "product_choice", "candidates": names}
                        options = '\n'.join([f"{i+1}. {n}" for i, n in enumerate(names)])
                        return f"I couldn't find that product exactly. I found multiple products that might match:\n{options}\nPlease reply with the number or exact name."

                    _PENDING = {"product": prod, "rating": rating_val, "comment": None, "awaiting": "product"}
                    return (
                        "Product not found. Please provide the exact product name or SKU, "
                        "or run a search (e.g., 'search for chocolate cake')."
                    )
                _PENDING = {"product": None, "rating": None, "comment": None, "awaiting": None}
                return resp
            if ans in ("yes", "y", "sure", "ok", "okay", "yeah"):
                _PENDING["awaiting"] = "comment"
                return "Please enter your comment now."
            # otherwise treat the reply as the comment text
            _PENDING["comment"] = message.strip()
            resp = submit_feedback(prod, rating_val, _PENDING["comment"])
            if isinstance(resp, str) and resp.lower().startswith("product not found"):
                # try to suggest candidates (same logic as above)
                query = _build_search_query(prod)
                candidates = []
                if query:
                    candidates = find_products(query)[:5]
                if not candidates:
                    words = [w for w in (query or prod).split() if len(w) > 2]
                    seen_ids = set()
                    for w in words:
                        for c in find_products(w)[:5]:
                            if c['id'] not in seen_ids:
                                candidates.append(c)
                                seen_ids.add(c['id'])
                            if len(candidates) >= 5:
                                break
                        if candidates:
                            break

                if len(candidates) == 1:
                    selected = candidates[0]['name']
                    resp2 = submit_feedback(selected, rating_val, _PENDING["comment"])
                    _PENDING = {"product": None, "rating": None, "comment": None, "awaiting": None}
                    return resp2

                if len(candidates) > 1:
                    names = [c['name'] for c in candidates]
                    _PENDING = {"product": prod, "rating": rating_val, "comment": _PENDING["comment"], "awaiting": "product_choice", "candidates": names}
                    options = '\n'.join([f"{i+1}. {n}" for i, n in enumerate(names)])
                    return f"I couldn't find that product exactly. I found multiple products that might match:\n{options}\nPlease reply with the number or exact name."

                _PENDING = {"product": prod, "rating": rating_val, "comment": _PENDING["comment"], "awaiting": "product"}
                return (
                    "Product not found. Please provide the exact product name or SKU, "
                    "or run a search (e.g., 'search for chocolate cake')."
                )

            _PENDING = {"product": None, "rating": None, "comment": None, "awaiting": None}
            return resp
        elif awaiting == "comment":
            prod = _PENDING.get("product")
            rating_val = _PENDING.get("rating")
            _PENDING["comment"] = message.strip()
            resp = submit_feedback(prod, rating_val, _PENDING["comment"])
            if isinstance(resp, str) and resp.lower().startswith("product not found"):
                query = _build_search_query(prod)
                candidates = []
                if query:
                    candidates = find_products(query)[:5]
                if not candidates:
                    words = [w for w in (query or prod).split() if len(w) > 2]
                    seen_ids = set()
                    for w in words:
                        for c in find_products(w)[:5]:
                            if c['id'] not in seen_ids:
                                candidates.append(c)
                                seen_ids.add(c['id'])
                            if len(candidates) >= 5:
                                break
                        if candidates:
                            break

                if len(candidates) == 1:
                    selected = candidates[0]['name']
                    resp2 = submit_feedback(selected, rating_val, _PENDING["comment"])
                    _PENDING = {"product": None, "rating": None, "comment": None, "awaiting": None}
                    return resp2

                if len(candidates) > 1:
                    names = [c['name'] for c in candidates]
                    _PENDING = {"product": prod, "rating": rating_val, "comment": _PENDING["comment"], "awaiting": "product_choice", "candidates": names}
                    options = '\n'.join([f"{i+1}. {n}" for i, n in enumerate(names)])
                    return f"I couldn't find that product exactly. I found multiple products that might match:\n{options}\nPlease reply with the number or exact name."

                _PENDING = {"product": prod, "rating": rating_val, "comment": _PENDING["comment"], "awaiting": "product"}
                return (
                    "Product not found. Please provide the exact product name or SKU, "
                    "or run a search (e.g., 'search for chocolate cake')."
                )

            _PENDING = {"product": None, "rating": None, "comment": None, "awaiting": None}
            return resp
        elif awaiting == "product_choice":
            # user selecting from candidate list
            candidates = _PENDING.get("candidates") or []
            choice = message.strip()
            # accept word numbers like 'one', 'two'
            choice_l = choice.lower()
            if not choice.isdigit() and choice_l in NUMBER_WORDS:
                # map 'one'->1 etc.
                choice = str(NUMBER_WORDS[choice_l])
            # accept numeric choice
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(candidates):
                    selected = candidates[idx]
                    # if we already have a comment that doesn't look like a product token, submit; otherwise ask user if they'd like to add one
                    existing_comment = _PENDING.get('comment')
                    if _is_valid_comment(existing_comment) and not _looks_like_product_token(existing_comment, selected):
                        resp = submit_feedback(selected, _PENDING.get('rating'), existing_comment or "")
                        _PENDING = {"product": None, "rating": None, "comment": None, "awaiting": None}
                        return resp
                    # no valid comment yet: set product and ask about comment
                    _PENDING["product"] = selected
                    _PENDING["awaiting"] = "comment_opt"
                    return "Would you like to add a comment? (yes/no)"
            # accept exact name
            for c in candidates:
                if choice.lower() == c.lower():
                    existing_comment = _PENDING.get('comment')
                    if _is_valid_comment(existing_comment) and not _looks_like_product_token(existing_comment, c):
                        resp = submit_feedback(c, _PENDING.get('rating'), existing_comment or "")
                        _PENDING = {"product": None, "rating": None, "comment": None, "awaiting": None}
                        return resp
                    _PENDING["product"] = c
                    _PENDING["awaiting"] = "comment_opt"
                    return "Would you like to add a comment? (yes/no)"
            # otherwise ask again
            return "Please reply with the number or exact product name from the list above."

        # clear awaiting to allow re-evaluation
        _PENDING["awaiting"] = None

        # re-evaluate filled fields
        product = _PENDING.get("product")
        rating = _PENDING.get("rating")
        comment = _PENDING.get("comment") or None

        # If product+rating present but no valid comment known, ask if user wants to add one
        if product and rating and not _is_valid_comment(comment):
            _PENDING["awaiting"] = "comment_opt"
            return "Would you like to add a comment? (yes/no)"

        if product and rating and _is_valid_comment(comment):
            # Try to submit; if product not found, try to suggest matches
            resp = submit_feedback(product, rating, comment or "")
            if isinstance(resp, str) and resp.lower().startswith("product not found"):
                # Try to find candidate products using the search tool
                query = _build_search_query(product)
                candidates = []
                # try the full cleaned query first
                if query:
                    candidates = find_products(query)[:5]

                # if nothing, try searching by individual words
                if not candidates:
                    words = [w for w in (query or product).split() if len(w) > 2]
                    seen_ids = set()
                    for w in words:
                        for c in find_products(w)[:5]:
                            if c['id'] not in seen_ids:
                                candidates.append(c)
                                seen_ids.add(c['id'])
                            if len(candidates) >= 5:
                                break
                        if candidates:
                            break

                if len(candidates) == 1:
                    selected = candidates[0]['name']
                    resp2 = submit_feedback(selected, rating, comment or "")
                    _PENDING = {"product": None, "rating": None, "comment": None, "awaiting": None}
                    return resp2

                if len(candidates) > 1:
                    names = [c['name'] for c in candidates]
                    _PENDING = {"product": product, "rating": rating, "comment": comment, "awaiting": "product_choice", "candidates": names}
                    options = '\n'.join([f"{i+1}. {n}" for i, n in enumerate(names)])
                    return f"I found multiple products that might match:\n{options}\nPlease reply with the number or exact name."

                # no candidates found -- ask user to clarify or run search
                _PENDING = {"product": product, "rating": rating, "comment": comment, "awaiting": "product"}
                return (
                    "I couldn't find that product. Please provide the exact product name or SKU, "
                    "or run a search (e.g., 'search for chocolate cake')."
                )

            _PENDING = {"product": None, "rating": None, "comment": None, "awaiting": None}
            return resp

        # still missing something
        if not product:
            _PENDING["awaiting"] = "product"
            return "Which product is the feedback about? Please give the product name or SKU."

        if not rating:
            _PENDING["awaiting"] = "rating"
            return "What rating would you give this product (1–5)?"

    # no pending state — parse freshly (heuristic)
    # First, try best-effort LLM parse (sync helper) — may return None if unavailable.
    llm_parsed = parse_with_llm(message)
    if llm_parsed:
        rating = llm_parsed.get("rating")
        product = llm_parsed.get("product")
        comment = llm_parsed.get("comment")
    else:
        rating = _extract_rating(message)
        product = _extract_product(message)
        comment = _extract_comment(message, product, rating)

    # If both missing, ask for both and start pending
    if not product and not rating:
        _PENDING = {"product": None, "rating": None, "comment": comment, "awaiting": "product"}
        return "Please tell me which product you're rating and the rating (1–5). You can also add a comment."

    # If product missing, prompt for it and save rating/comment
    if not product:
        _PENDING = {"product": None, "rating": rating, "comment": comment, "awaiting": "product"}
        return "Which product is the feedback about? Please give the product name or SKU."

    # If rating missing, prompt for it and save product/comment
    if not rating:
        _PENDING = {"product": product, "rating": None, "comment": comment, "awaiting": "rating"}
        return "What rating would you give this product (1–5)?"

    # Both found: submit only if comment is valid; otherwise ask about comment
    if product and rating:
        if _is_valid_comment(comment):
            return submit_feedback(product, rating, comment or "")
        _PENDING = {"product": product, "rating": rating, "comment": None, "awaiting": "comment_opt"}
        return "Would you like to add a comment? (yes/no)"


async def handle_feedback_async(message: str) -> str:
    """Async entrypoint usable from async callers (CLI main). Tries the async LLM parser first."""
    # Try async LLM parse first (best-effort)
    parsed = await parse_with_llm_async(message)
    if parsed:
        # seed the same logic by calling the sync handler with a normalized message
        # If parsed contains product+rating, directly attempt submit
        prod = parsed.get("product")
        rating = parsed.get("rating")
        comment = parsed.get("comment")
        if prod and rating:
            resp = submit_feedback(prod, rating, comment or "")
            # if product not found, fallback to heuristic flow
            if isinstance(resp, str) and resp.lower().startswith("product not found"):
                # fall through to the sync handler so it prompts the user
                return handle_feedback(message)
            return resp

    # fallback to sync handler which includes heuristics and multi-turn state
    return handle_feedback(message)


def is_awaiting_feedback() -> bool:
    """Return True when a feedback collection is in progress and awaiting user input."""
    try:
        return bool(_PENDING and _PENDING.get("awaiting"))
    except NameError:
        return False
