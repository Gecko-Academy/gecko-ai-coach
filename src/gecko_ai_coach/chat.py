"""The coach, shaped for a chat: one message in, one reply out.

    from gecko_ai_coach.chat import published_pages, reply_to

    pages = published_pages()                 # the live course, fetched once
    print(reply_to("where do I submit my work", {}, pages)["reply"])

WHY THIS IS ITS OWN MODULE. The CLI prints, the MCP server speaks JSON-RPC, and a
bot sends messages -- three transports over one decision. The decision lives here
so all three answer the same way, and so it can be tested without a network, a
token, or a model.

WHAT IT IS NOT. It holds no token, opens no socket, and knows nothing about
Telegram. `api/index.py` and `scripts/telegram_poll.py` carry that, and both call
this.

THE FOUR OUTCOMES are session 5's, in the bootcamp this serves: `answered`,
`repeated_call`, `budget`, `refused`. A person reading a reply can tell which one
they got without being told.
"""

from __future__ import annotations

import io
import os
import re
import tarfile
import time
import urllib.request
from pathlib import Path

from gecko_ai_coach import corpus
from gecko_ai_coach.coach import answer
from gecko_ai_coach.retrieve import Document

#: The published course. A tarball rather than 81 requests, and `main` rather
#: than a pinned commit: a learner asking about this week must not be answered
#: from last week's pages.
COURSE_TARBALL = (
    "https://codeload.github.com/Gecko-Academy/dev3pack-cohort-2026-09/tar.gz/refs/heads/main"
)

#: Telegram rejects anything longer. The number is theirs, not ours.
MESSAGE_LIMIT = 4096

#: Questions per chat, per window. A chat is a stranger with a keyboard.
BUDGET = 8
WINDOW_SECONDS = 60 * 60

#: A message shaped like an order to the model rather than a question about the
#: course. Dropped, and never explained back: an attacker who learns which
#: sentence was caught learns what to write next.
INSTRUCTION = re.compile(
    r"(?:ignore|disregard)[\s\S]{0,40}?(?:previous|above|prior)\s+instructions"
    r"|(?:send|print|reveal|show)[\s\S]{0,40}?(?:token|api[ _-]?key|secret|password|\.env)"
    r"|^\s*(?:system|assistant|developer)\s*:",
    re.IGNORECASE | re.MULTILINE,
)

WELCOME = (
    "I answer questions about the Dev3Pack course, from the course pages themselves.\n\n"
    "Ask me something like:\n"
    "  · where do I submit my work\n"
    "  · what is a bounded tool\n"
    "  · how do I run a model on my laptop\n\n"
    "Every answer names the page it came from, and I say so when the pages do not "
    "cover something."
)

_CACHE: dict[str, object] = {}


def published_pages(url: str = COURSE_TARBALL, max_age: int = 3600) -> list[Document]:
    """Every published course page, fetched once and kept in memory.

    Cached for `max_age` because a serverless instance is reused while warm, and
    the pages change weekly rather than per message. A cold start pays about a
    second; every message after it pays nothing.
    """
    now = time.time()
    if _CACHE.get("pages") and now - float(_CACHE.get("fetched", 0)) < max_age:
        return _CACHE["pages"]  # type: ignore[return-value]

    with urllib.request.urlopen(url, timeout=60) as response:  # noqa: S310 - pinned https host
        archive = tarfile.open(fileobj=io.BytesIO(response.read()))

    documents: list[Document] = []
    for member in archive.getmembers():
        if "/units/en/" not in member.name or not member.name.endswith((".md", ".mdx")):
            continue
        if "/solutions/" in member.name:
            continue  # never, under any circumstances
        handle = archive.extractfile(member)
        if handle is None:
            continue
        doc_id = member.name.split("/units/en/", 1)[1].rsplit(".", 1)[0]
        text = handle.read().decode("utf-8", "replace")
        documents.append(
            Document(
                doc_id=doc_id,
                title=corpus._title_of(text, doc_id),
                text=corpus._strip_components(text),
                url=f"https://gecko-academy.github.io/dev3pack-cohort-2026-09/{doc_id}",
            )
        )
    _CACHE["pages"], _CACHE["fetched"] = documents, now
    return documents


def local_pages(root: str | Path | None = None) -> list[Document]:
    """The pages in a clone, for running the bot against a working copy."""
    return corpus.load(Path(root or os.environ.get("COACH_PAGES", "units/en")))


def chunks(text: str, limit: int = MESSAGE_LIMIT) -> list[str]:
    """Split on blank lines, then lines, and never mid-word."""
    parts: list[str] = []
    current = ""
    for block in text.split("\n\n"):
        if len(current) + len(block) + 2 <= limit:
            current = f"{current}\n\n{block}" if current else block
            continue
        if current:
            parts.append(current)
        while len(block) > limit:
            cut = block.rfind("\n", 0, limit)
            cut = cut if cut > 0 else block.rfind(" ", 0, limit)
            parts.append(block[: cut if cut > 0 else limit])
            block = block[cut if cut > 0 else limit :].lstrip()
        current = block
    if current:
        parts.append(current)
    return parts or [""]


def _normalise(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", text.lower()))


def reply_to(text: str, state: dict, documents: list[Document], now: float | None = None) -> dict:
    """One message in, one reply out, and the reason it ended that way.

    A refusal also carries ``refusal_kind``, because the three are not the same
    thing and only one of them is worth a human's attention. ``too_short`` is a
    typo. ``guard`` is somebody trying to talk to the model instead of the course.
    ``not_covered`` is the course failing to answer a real question, which is the
    only one that should ever reach anybody.

    Added as a NEW key rather than by splitting ``stopped_because``: two tests pin
    that value for two different refusals, and a caller that only wants to know
    whether it refused should not have to learn three names.

    `state` is this chat's own dict and is modified in place: the count, the
    window it belongs to, and the last question asked. A caller that keeps one
    dict per chat gets a budget and a repeat guard for free.
    """
    now = time.time() if now is None else now
    message = text.strip()

    if message.startswith("/start") or message.startswith("/help"):
        return {"stopped_because": "answered", "reply": WELCOME, "pages": []}

    if len(message.split()) < 2:
        return {
            "stopped_because": "refused",
            "refusal_kind": "too_short",
            "reply": "Ask me a question about the course — a few words, the way you would say it.",
            "pages": [],
        }

    if INSTRUCTION.search(message):
        # Answered as if it were an ordinary question nobody can answer. The
        # guard is not announced.
        return {
            "stopped_because": "refused",
            "refusal_kind": "guard",
            "reply": "I only answer questions about the Dev3Pack course pages.",
            "pages": [],
        }

    if now - float(state.get("window", 0)) > WINDOW_SECONDS:
        state["window"], state["calls"] = now, 0

    if _normalise(message) == state.get("last"):
        return {
            "stopped_because": "repeated_call",
            "reply": (
                "You just asked that, and my answer has not changed. Try asking it a different way."
            ),
            "pages": [],
        }
    state["last"] = _normalise(message)

    if int(state.get("calls", 0)) >= BUDGET:
        minutes = max(1, int((WINDOW_SECONDS - (now - float(state["window"]))) / 60))
        return {
            "stopped_because": "budget",
            "reply": (
                f"stopped: {BUDGET} questions an hour is my budget, so one person cannot "
                f"use me up. Ask again in about {minutes} minutes."
            ),
            "pages": [],
        }
    state["calls"] = int(state.get("calls", 0)) + 1

    found = answer(message, documents, top_k=2)
    if found.refused or not found.passages:
        return {
            "stopped_because": "refused",
            "refusal_kind": "not_covered",
            "reply": (
                "NOT IN THESE PAGES.\n\nNothing in the course covers that. If a week has not "
                "opened yet, its pages are not here either."
            ),
            "pages": [],
        }

    body: list[str] = []
    for scored in found.passages:
        chunk = scored.chunk
        body.append(f"{chunk.text.strip()}\n\n— {chunk.title}\n{chunk.url or chunk.doc_id}")
    return {
        "stopped_because": "answered",
        "reply": "\n\n———\n\n".join(body),
        "pages": list(found.pages),
    }


__all__ = [
    "BUDGET",
    "COURSE_TARBALL",
    "MESSAGE_LIMIT",
    "WELCOME",
    "chunks",
    "local_pages",
    "published_pages",
    "reply_to",
]
