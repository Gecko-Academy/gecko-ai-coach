"""The Vercel entrypoint: Telegram POSTs one message here, the coach answers it.

ONE ENTRYPOINT, ON PURPOSE. Vercel's Python builder wants a single handler per
project rather than a file per route, so everything arrives here.

WHY A WEBHOOK MAY HOLD THE TOKEN AND STILL BE SAFE. Anyone can POST to this URL.
So nothing is trusted until the `X-Telegram-Bot-Api-Secret-Token` header —
set during `setWebhook`, echoed by Telegram on every call — matches ours under a
constant-time compare. Without it, this endpoint would answer strangers with our
bot's voice.

STATE IS BEST EFFORT. Vercel reuses a warm instance, so the per-chat budget below
survives nearby messages and resets on a cold start. That is the same trade the
reference bot accepted: better than nothing, and never the only defence.
"""

from __future__ import annotations

import hmac
import json
import os
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from gecko_ai_coach.chat import published_pages  # noqa: E402
from gecko_ai_coach.telegram import handle_update  # noqa: E402

#: Warm-instance state: the pages, and one dict per chat.
CHATS: dict = {}


def _authorised(headers) -> bool:
    expected = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "").strip()
    if not expected:
        return False  # fail closed: an unset secret is an open endpoint
    sent = headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    return hmac.compare_digest(sent, expected)


class handler(BaseHTTPRequestHandler):  # noqa: N801 - the name Vercel looks for
    def _reply(self, code: int, body: str = "ok") -> None:
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(body.encode())

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler's spelling
        """A health check that proves the pages load, and says nothing else."""
        try:
            self._reply(200, f"gecko-ai-coach: {len(published_pages())} pages")
        except Exception as error:  # noqa: BLE001
            self._reply(500, f"pages unavailable: {type(error).__name__}")

    def do_POST(self) -> None:  # noqa: N802
        if not _authorised(self.headers):
            # 200, not 401: an attacker learns nothing, and Telegram never retries
            # a delivery we deliberately ignored.
            self._reply(200, "ignored")
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            update = json.loads(self.rfile.read(length) or b"{}")
        except Exception as error:  # noqa: BLE001
            self._reply(200, f"unreadable: {type(error).__name__}")
            return

        try:
            handle_update(update, published_pages(), CHATS)
        except Exception as error:  # noqa: BLE001 - one bad turn must not stop the bot
            print(f"update failed: {type(error).__name__}")
        # Always 200: a non-2xx makes Telegram redeliver the same message for hours.
        self._reply(200)
