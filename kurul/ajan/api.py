"""Client for the site's agent API (SPEC.md section 5). urllib only."""

from __future__ import annotations

import json
import socket
import time
import urllib.error
import urllib.parse
import urllib.request

from .log import log


class ApiError(Exception):
    def __init__(self, status: int, msg: str):
        super().__init__(f"HTTP {status}: {msg}")
        self.status = status


class TransientError(Exception):
    """Network trouble or a 5xx/429; the caller may retry later."""


class SiteClient:
    def __init__(self, base_url: str, token: str, *, timeout: float = 40.0, tries: int = 4,
                 backoff_base: float = 1.0, backoff_max: float = 30.0, sleep=time.sleep):
        self.base = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.tries = max(1, tries)
        self.backoff_base = backoff_base
        self.backoff_max = backoff_max
        self.sleep = sleep

    # -- transport -------------------------------------------------------------------------

    def _once(self, method: str, path: str, body=None, timeout: float | None = None, headers=None):
        data = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(self.base + path, data=data, method=method)
        req.add_header("Authorization", f"Bearer {self.token}")
        req.add_header("Accept", "application/json")
        req.add_header("User-Agent", "kurul-ajan/0.1")
        if data is not None:
            req.add_header("Content-Type", "application/json")
        for k, v in (headers or {}).items():
            req.add_header(k, v)
        try:
            with urllib.request.urlopen(req, timeout=timeout or self.timeout) as r:
                raw = r.read()
                return json.loads(raw.decode("utf-8")) if raw else {}
        except urllib.error.HTTPError as e:
            text = ""
            try:
                text = e.read().decode("utf-8", "replace")[:300]
            except Exception:
                pass
            if e.code >= 500 or e.code == 429:
                raise TransientError(f"HTTP {e.code} {path}: {text}") from e
            raise ApiError(e.code, f"{method} {path}: {text}") from e
        except (urllib.error.URLError, socket.timeout, ConnectionError, TimeoutError) as e:
            raise TransientError(f"{method} {path}: {e}") from e
        except json.JSONDecodeError as e:
            raise TransientError(f"{method} {path}: bad JSON") from e

    def _call(self, method: str, path: str, body=None, *, retry: bool = True, timeout=None, headers=None):
        tries = self.tries if retry else 1
        for i in range(tries):
            try:
                return self._once(method, path, body, timeout=timeout, headers=headers)
            except TransientError as e:
                if i == tries - 1:
                    raise
                delay = min(self.backoff_max, self.backoff_base * (2 ** i))
                log("api_retry", level="warning", method=method, path=path, attempt=i + 1,
                    delay=delay, error=str(e)[:200])
                self.sleep(delay)

    # -- endpoints ---------------------------------------------------------------------------

    def events(self, after: int, wait: int = 25) -> dict:
        q = urllib.parse.urlencode({"after": after, "wait": wait})
        return self._call("GET", f"/api/agent/events?{q}", retry=False, timeout=wait + 20)

    def thread(self, root_id) -> dict:
        return self._call("GET", f"/api/agent/thread/{urllib.parse.quote(str(root_id))}")

    def recent(self, limit: int = 30) -> dict:
        return self._call("GET", f"/api/agent/recent?limit={int(limit)}")

    def question(self, qid: str) -> dict | None:
        """Not in SPEC v0; used when an event payload lacks question details. None on 404/405."""
        try:
            return self._call("GET", f"/api/agent/questions/{urllib.parse.quote(qid)}")
        except ApiError as e:
            if e.status in (404, 405):
                return None
            raise

    def post_message(self, root_id, body: str | None = None, card: dict | None = None,
                     visible_to=None, idempotency_key: str | None = None) -> dict:
        payload = {"root_id": root_id}
        if body is not None:
            payload["body"] = body
        if card is not None:
            payload["card"] = card
        if visible_to is not None:
            payload["visible_to"] = visible_to
        headers = {"Idempotency-Key": idempotency_key} if idempotency_key else None
        return self._call("POST", "/api/agent/messages", payload, headers=headers)

    def create_question(self, root_message_id, restated: str, author_id, forwarder_id=None,
                        note=None) -> dict:
        payload = {"root_message_id": root_message_id, "restated": restated, "author_id": author_id}
        if forwarder_id is not None:
            payload["forwarder_id"] = forwarder_id
        if note is not None:
            payload["note"] = note
        return self._call("POST", "/api/agent/questions", payload)

    def patch_question(self, qid: str, **fields) -> dict:
        body = {k: v for k, v in fields.items() if v is not None}
        return self._call("PATCH", f"/api/agent/questions/{urllib.parse.quote(qid)}", body)

    def put_feasibility(self, qid: str, public_summary: str, private_detail: str,
                        est_cost_eur: float, touches_blind: bool) -> dict:
        body = {"public_summary": public_summary, "private_detail": private_detail,
                "est_cost_eur": float(est_cost_eur), "touches_blind": bool(touches_blind)}
        return self._call("PUT", f"/api/agent/feasibility/{urllib.parse.quote(qid)}", body)

    def suggestion(self, message_id, outcome: str) -> dict:
        # The site logs "offered" itself when the card is posted; a 409 here means it is already recorded.
        try:
            return self._call("POST", "/api/agent/suggestions", {"message_id": message_id, "outcome": outcome})
        except ApiError as e:
            if e.status == 409:
                return {"ok": True, "already": True}
            raise
