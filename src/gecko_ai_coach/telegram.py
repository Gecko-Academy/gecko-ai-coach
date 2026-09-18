"""Telegram, and nothing else: one API call, and the two ways to receive.

    ai-coach telegram --poll            # your laptop, no host, no domain
    ai-coach telegram --set-webhook https://<your-app>.vercel.app/api

WHAT IT HOLDS. The token, read from the environment and never printed. Every
failure prints the TYPE of the error, because the URL of a Bot API call carries
the token in it and a logged traceback would carry it too.

WHAT IT DOES NOT HOLD. The decision. `chat.reply_to` answers; this module carries
the answer to a person.
"""

from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request

from gecko_ai_coach.chat import chunks, reply_to
from gecko_ai_coach.retrieve import Document


class TelegramError(Exception):
    """A Bot API call failed. The message never carries the URL, which carries the token."""


#: Where a token may live, in order. The environment first, because a deployment
#: has no keychain; then the OS keychain, because a laptop should not need a
#: dotfile. `keyring` is optional: without it, the environment is the only lane.
#: `gecko auth set COACH_BOT_TOKEN` writes service `gecko:<slot>`, user `gecko`.
#: COACH_BOT_TOKEN is deliberately first and TELEGRAM_BOT_TOKEN is deliberately
#: ABSENT: on the machine this was built on, that slot held a bot already serving
#: real people, and one token is one bot, one webhook, one identity. A coach that
#: quietly adopted it would have answered somebody else's users — and taken their
#: bot offline the moment it set a webhook.
KEYCHAIN_ENTRIES = (
    ("gecko:COACH_BOT_TOKEN", "gecko"),
    ("gecko-ai-coach", "COACH_BOT_TOKEN"),
)


def token(env: dict[str, str] | None = None, *, keychain: bool = True) -> str:
    """The bot token: the environment, then the OS keychain. Never a file in the repo.

    Returns an empty string rather than raising, so a caller can say what to do
    about it. The value is never printed, logged, or put in an error message: the
    Bot API URL embeds it, which is why `call` prints only an error's type.
    """
    source = env or os.environ
    found = (source.get("COACH_BOT_TOKEN") or source.get("TELEGRAM_BOT_TOKEN") or "").strip()
    if found or not keychain or env is not None:
        return found
    try:
        import keyring  # noqa: PLC0415 - optional, and only on this path
    except ImportError:
        return ""
    for service, user in KEYCHAIN_ENTRIES:
        try:
            stored = keyring.get_password(service, user)
        except Exception:  # noqa: BLE001 - a locked or absent keychain is "no token"
            continue
        if stored and stored.strip():
            return stored.strip()
    return ""


def call(method: str, *, timeout: int = 40, env: dict[str, str] | None = None, **params) -> dict:
    """One Bot API call. Returns {} on failure: a bot must not die on one bad turn."""
    secret = token(env)
    if not secret:
        raise TelegramError(
            "no bot token: set COACH_BOT_TOKEN, or `gecko auth set COACH_BOT_TOKEN`"
        )
    data = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None}).encode()
    url = f"https://api.telegram.org/bot{secret}/{method}"
    try:
        with urllib.request.urlopen(url, data=data, timeout=timeout) as response:  # noqa: S310
            return json.loads(response.read())
    except Exception as error:  # noqa: BLE001 - offline, timeout, HTTP: all are "no reply"
        print(f"telegram {method}: {type(error).__name__}")
        return {}


def send(chat_id: int | str, text: str, **extra) -> None:
    """Send one reply, split into as many messages as Telegram's limit needs."""
    for part in chunks(text):
        call("sendMessage", chat_id=chat_id, text=part, **extra)


def handle_update(update: dict, documents: list[Document], chats: dict) -> str | None:
    """Answer one update. Returns the stop reason, or None when there is nothing to answer.

    Anything that is not a text message is ignored in silence: a photo, a sticker
    or a member joining is not a question, and a reply to one is noise.
    """
    message = update.get("message") or update.get("edited_message") or {}
    text = message.get("text")
    chat_id = (message.get("chat") or {}).get("id")
    if not text or chat_id is None:
        return None

    state = chats.setdefault(chat_id, {})
    answer = reply_to(text, state, documents)
    send(chat_id, answer["reply"])
    return str(answer["stopped_because"])


def poll(documents: list[Document], seconds: int = 25, rounds: int | None = None) -> None:
    """Long polling: ask Telegram for messages, answer them, repeat.

    No server, no domain, no certificate — the connection is made outwards. Run it
    on a laptop with the terminal open, or in a container with no ports at all.
    """
    me = call("getMe").get("result", {})
    if not me:
        raise TelegramError("could not reach Telegram — is TELEGRAM_BOT_TOKEN right?")
    print(f"listening as @{me.get('username', '?')}. Ctrl-C to stop.")

    offset, round_number = 0, 0
    while rounds is None or round_number < rounds:
        round_number += 1
        updates = call("getUpdates", offset=offset, timeout=seconds).get("result", [])
        for update in updates:
            # FIRST, so one message that breaks the handler is not redelivered for ever.
            offset = update["update_id"] + 1
            stopped = handle_update(update, documents, poll.chats)  # type: ignore[attr-defined]
            if stopped:
                who = (update.get("message", {}).get("chat") or {}).get("id")
                print(f"  [{who}] {stopped}")
        if not updates:
            time.sleep(1)


poll.chats = {}  # type: ignore[attr-defined]  # chat_id -> its budget and last question


def set_webhook(url: str, secret: str | None = None) -> dict:
    """Point Telegram at a hosted endpoint. `secret` is echoed back on every call."""
    result = call(
        "setWebhook",
        url=url,
        secret_token=secret or os.environ.get("TELEGRAM_WEBHOOK_SECRET", "").strip() or None,
        allowed_updates=json.dumps(["message"]),
        drop_pending_updates="true",
    )
    if not result.get("ok"):
        raise TelegramError(f"setWebhook refused: {result.get('description', 'no reply')}")
    return result


def delete_webhook() -> dict:
    """Stop the webhook, so long polling works again. The two are mutually exclusive."""
    return call("deleteWebhook", drop_pending_updates="true")


__all__ = [
    "TelegramError",
    "call",
    "delete_webhook",
    "handle_update",
    "poll",
    "send",
    "set_webhook",
    "token",
]
