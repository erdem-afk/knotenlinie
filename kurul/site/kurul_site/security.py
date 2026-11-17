"""Token hashing, rate limiting and HTTP hardening middleware."""

from __future__ import annotations

import hashlib
import hmac
import secrets
import threading
import time
from collections import defaultdict, deque

CSP = (
    "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
    "connect-src 'self'; font-src 'self'; object-src 'none'; base-uri 'none'; "
    "form-action 'self'; frame-ancestors 'none'"
)

SECURITY_HEADERS = [
    (b"content-security-policy", CSP.encode()),
    (b"x-content-type-options", b"nosniff"),
    (b"x-frame-options", b"DENY"),
    (b"referrer-policy", b"no-referrer"),
    (b"permissions-policy", b"camera=(), microphone=(), geolocation=()"),
    (b"cross-origin-opener-policy", b"same-origin"),
]


def new_token() -> str:
    return secrets.token_urlsafe(32)


class Hasher:
    """sha256 of a token, keyed with the session secret (HMAC-SHA256)."""

    def __init__(self, secret: str):
        self.key = secret.encode()

    def __call__(self, token: str) -> str:
        return hmac.new(self.key, token.encode(), hashlib.sha256).hexdigest()


def same(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode(), b.encode())


class RateLimiter:
    """Sliding-window counter in memory (single process)."""

    def __init__(self):
        self._hits: dict[str, deque] = defaultdict(deque)
        self._lock = threading.Lock()

    def hit(self, key: str, limit: int, window_s: float) -> bool:
        """Record a hit; return False when the limit is exceeded."""
        t = time.monotonic()
        with self._lock:
            q = self._hits[key]
            while q and q[0] <= t - window_s:
                q.popleft()
            if len(q) >= limit:
                return False
            q.append(t)
            if len(self._hits) > 50000:  # crude bound on memory
                for k in [k for k, v in self._hits.items() if not v][:10000]:
                    del self._hits[k]
            return True

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


class HardeningMiddleware:
    """Adds security headers and enforces request body size limits (pure ASGI)."""

    def __init__(self, app, human_limit: int = 64 * 1024, agent_limit: int = 512 * 1024,
                 csrf_exempt: tuple[str, ...] = ("/auth/verify",)):
        self.app = app
        self.human_limit = human_limit
        self.agent_limit = agent_limit
        self.csrf_exempt = csrf_exempt

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        is_agent = scope["path"].startswith("/api/agent/")
        limit = self.agent_limit if is_agent else self.human_limit
        # Every state-changing human request must carry X-Requested-With: kurul. Browsers cannot
        # send a custom header cross-site without a CORS preflight, which we never grant.
        if (scope["method"] not in ("GET", "HEAD", "OPTIONS") and not is_agent
                and scope["path"] not in self.csrf_exempt):
            xrw = dict(scope.get("headers", [])).get(b"x-requested-with", b"")
            if xrw.lower() != b"kurul":
                return await _reply(send, 403, b'{"detail":"missing X-Requested-With header"}')
        for k, v in scope.get("headers", []):
            if k == b"content-length":
                try:
                    if int(v) > limit:
                        return await _too_large(send)
                except ValueError:
                    return await _too_large(send)

        received = 0

        async def limited_receive():
            nonlocal received
            msg = await receive()
            if msg["type"] == "http.request":
                received += len(msg.get("body", b""))
                if received > limit:
                    raise _BodyTooLarge()
            return msg

        async def send_with_headers(msg):
            if msg["type"] == "http.response.start":
                headers = list(msg.get("headers", []))
                present = {k.lower() for k, _ in headers}
                for k, v in SECURITY_HEADERS:
                    if k not in present:
                        headers.append((k, v))
                msg = dict(msg, headers=headers)
            await send(msg)

        try:
            await self.app(scope, limited_receive, send_with_headers)
        except _BodyTooLarge:
            await _too_large(send)


class _BodyTooLarge(Exception):
    pass


async def _too_large(send):
    await _reply(send, 413, b'{"detail":"request body too large"}')


async def _reply(send, status: int, body: bytes):
    await send({"type": "http.response.start", "status": status,
                "headers": [(b"content-type", b"application/json"),
                            (b"content-length", str(len(body)).encode())] + SECURITY_HEADERS})
    await send({"type": "http.response.body", "body": body})
