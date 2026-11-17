"""A tiny in-process implementation of the site's agent API (SPEC.md section 5) for tests.

Human-side actions (posting, forwarding, card buttons, coordinator actions) are Python methods
that apply the site effects of SPEC section 6 and emit the events of section 5.
"""

from __future__ import annotations

import json
import re
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

AGENT_ID = 100


class FakeSite:
    def __init__(self, token: str = "test-token"):
        self.token = token
        self.lock = threading.Condition()
        self.users = {AGENT_ID: {"id": AGENT_ID, "name": "Knotenlinie agent", "role": "agent"}}
        self.messages: dict[int, dict] = {}
        self.questions: dict[str, dict] = {}
        self.feasibility: dict[str, dict] = {}
        self.suggestions: list[dict] = []
        self.events: list[dict] = []
        self.calls: list[tuple[str, str, object]] = []
        self.fail_next = 0  # respond 500 to this many agent calls (transient fault injection)
        self.fail_prefix = ""  # ... only calls whose path starts with this
        self.next_mid = 1
        self.next_fid = 1
        self.running = 0
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), self._handler())
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()

    # ------------------------------------------------------------------------------------------
    # data helpers
    # ------------------------------------------------------------------------------------------

    def add_user(self, uid: int, name: str, role: str = "member"):
        self.users[uid] = {"id": uid, "name": name, "role": role}

    def emit(self, etype: str, payload: dict) -> int:
        with self.lock:
            eid = len(self.events) + 1
            self.events.append({"id": eid, "type": etype, "payload": payload})
            self.lock.notify_all()
            return eid

    def _new_message(self, author_id, body=None, root_id=None, card=None, visible_to=None) -> dict:
        with self.lock:
            mid = self.next_mid
            self.next_mid += 1
            m = {"id": mid, "root_id": root_id, "author_id": author_id, "body": body or "",
                 "kind": "card" if card else "text", "card": card, "visible_to": visible_to,
                 "created_at": f"2026-11-17T10:{mid:02d}:00Z", "hidden_at": None, "action_taken": None}
            self.messages[mid] = m
            return m

    def _view(self, m: dict) -> dict:
        u = self.users.get(m["author_id"], {"id": m["author_id"], "name": "?", "role": "member"})
        v = {"id": m["id"], "root_id": m["root_id"], "kind": m["kind"], "created_at": m["created_at"],
             "author": dict(u), "visible_to": m["visible_to"]}
        if m["hidden_at"]:
            v["hidden"] = True
        else:
            v["body"] = m["body"]
            if m["card"]:
                v["card"] = m["card"]
        q = next((q for q in self.questions.values() if q["root_message_id"] == m["id"]), None)
        if q:
            v["question"] = {"id": q["id"], "status": q["status"], "path": q["path"], "queue_pos": None}
        return v

    def cards(self, ctype: str | None = None) -> list[dict]:
        return [m for m in self.messages.values() if m["kind"] == "card" and m["author_id"] == AGENT_ID
                and (ctype is None or m["card"]["type"] == ctype)]

    def agent_texts(self) -> list[dict]:
        return [m for m in self.messages.values() if m["kind"] == "text" and m["author_id"] == AGENT_ID]

    def agent_posts(self) -> list[dict]:
        return [m for m in self.messages.values() if m["author_id"] == AGENT_ID]

    # ------------------------------------------------------------------------------------------
    # human side (site effects of SPEC sections 4 and 6)
    # ------------------------------------------------------------------------------------------

    def member_post(self, uid: int, body: str, root_id=None) -> int:
        m = self._new_message(uid, body=body, root_id=root_id)
        self.emit("message.created", {"message_id": m["id"], "root_id": root_id, "author_id": uid,
                                      "mention": bool(re.search(r"@knotenlinie", body, re.I))})
        return m["id"]

    def hide(self, mid: int):
        self.messages[mid]["hidden_at"] = "now"
        self.messages[mid]["body"] = ""

    def forward(self, by: int, mid: int, note: str | None = None) -> int:
        fid = self.next_fid
        self.next_fid += 1
        self.emit("message.forwarded", {"forward_id": fid, "message_id": mid, "by_user_id": by, "note": note})
        return fid

    def _create_question(self, root_mid, restated, author_id, forwarder_id=None, note=None) -> dict:
        qid = f"Q-{len(self.questions) + 1:03d}"
        q = {"id": qid, "root_message_id": root_mid, "restated": restated, "author_id": author_id,
             "forwarder_id": forwarder_id, "note": note, "status": "recorded", "path": None}
        self.questions[qid] = q
        return q

    def card_action(self, card_mid: int, action: str, by: int, text: str | None = None):
        m = self.messages[card_mid]
        c = m["card"]
        m["action_taken"] = action
        t = c["type"]
        if t in ("suggest", "confirm"):
            if action == "yes":
                qm = self.messages[c["quoted_message_id"]]
                fwd = by if t == "confirm" else None
                q = self._create_question(qm["id"], c["restated"], qm["author_id"], fwd)
                self.emit("question.confirmed", {"question_id": q["id"]})
            else:
                self.suggestions.append({"message_id": c.get("quoted_message_id"), "outcome": "declined"})
        q = self._question_for_card(m)
        if t == "plan" and action == "approve" and q:
            f = self.feasibility.get(q["id"], {})
            if f.get("decision") != "auto":
                q["status"] = "on_hold"
                allowed = False
            elif self.running >= 3:
                q["status"] = "queued"
                allowed = False
            else:
                q["status"] = "frozen"
                allowed = True
            self.emit("plan.approved", {"question_id": q["id"], "by_user_id": by, "run_allowed": allowed})
        if t == "answer_record" and action == "test_anyway" and q:
            q["path"], q["status"] = "test", "recorded"
        self.emit("card.action", {"message_id": card_mid, "action": action, "by_user_id": by,
                                  **({"text": text} if text else {})})

    def _question_for_card(self, m) -> dict | None:
        return next((q for q in self.questions.values() if q["root_message_id"] == m["root_id"]), None)

    def release(self, qid: str):
        self.emit("run.released", {"question_id": qid})

    def hold(self, qid: str, reason: str):
        self.questions[qid]["status"] = "on_hold"
        self.emit("question.held", {"question_id": qid, "reason": reason})

    # ------------------------------------------------------------------------------------------
    # HTTP
    # ------------------------------------------------------------------------------------------

    def _handler(self):
        site = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def _send(self, code, obj):
                raw = json.dumps(obj).encode()
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def _body(self):
                n = int(self.headers.get("Content-Length") or 0)
                return json.loads(self.rfile.read(n) or b"{}") if n else {}

            def _route(self, method):
                u = urllib.parse.urlparse(self.path)
                qs = dict(urllib.parse.parse_qsl(u.query))
                body = self._body() if method in ("POST", "PUT", "PATCH") else None
                if self.headers.get("Authorization") != f"Bearer {site.token}":
                    return self._send(401, {"error": "unauthorized"})
                site.calls.append((method, u.path, body))
                if site.fail_next > 0 and u.path.startswith(site.fail_prefix):
                    site.fail_next -= 1
                    return self._send(500, {"error": "injected"})
                try:
                    code, obj = site.route(method, u.path, qs, body)
                except KeyError as e:
                    code, obj = 404, {"error": f"not found {e}"}
                return self._send(code, obj)

            def do_GET(self):
                self._route("GET")

            def do_POST(self):
                self._route("POST")

            def do_PUT(self):
                self._route("PUT")

            def do_PATCH(self):
                self._route("PATCH")

        return H

    def route(self, method, path, qs, body):
        if method == "GET" and path == "/api/agent/events":
            after, wait = int(qs.get("after", 0)), float(qs.get("wait", 0))
            end = time.time() + wait
            with self.lock:
                while True:
                    evs = [e for e in self.events if e["id"] > after]
                    if evs or time.time() >= end:
                        break
                    self.lock.wait(timeout=max(0.01, end - time.time()))
                return 200, {"events": evs, "last": len(self.events)}
        m = re.fullmatch(r"/api/agent/thread/(\d+)", path)
        if method == "GET" and m:
            mid = int(m.group(1))
            msg = self.messages[mid]
            root = self.messages[msg["root_id"]] if msg["root_id"] else msg
            replies = [x for x in self.messages.values() if x["root_id"] == root["id"]]
            return 200, {"root": self._view(root), "replies": [self._view(x) for x in replies]}
        if method == "GET" and path == "/api/agent/recent":
            lim = int(qs.get("limit", 30))
            tops = [x for x in self.messages.values() if x["root_id"] is None and x["kind"] == "text"]
            return 200, {"messages": [self._view(x) for x in tops[-lim:]]}
        m = re.fullmatch(r"/api/agent/questions/(Q-\d+)", path)
        if method == "GET" and m:
            return 200, self.questions[m.group(1)]
        if method == "POST" and path == "/api/agent/messages":
            if not body.get("body") and not body.get("card"):
                return 400, {"error": "empty"}
            msg = self._new_message(AGENT_ID, body=body.get("body"), root_id=body.get("root_id"),
                                    card=body.get("card"), visible_to=body.get("visible_to"))
            self.emit("message.created", {"message_id": msg["id"], "root_id": msg["root_id"],
                                          "author_id": AGENT_ID, "mention": False})
            return 200, {"id": msg["id"]}
        if method == "POST" and path == "/api/agent/questions":
            q = self._create_question(body["root_message_id"], body["restated"], body["author_id"],
                                      body.get("forwarder_id"), body.get("note"))
            return 200, {"id": q["id"]}
        if method == "PATCH" and m:
            q = self.questions[m.group(1)]
            for k in ("status", "path", "restated"):
                if k in body:
                    q[k] = body[k]
            return 200, {"ok": True}
        m = re.fullmatch(r"/api/agent/feasibility/(Q-\d+)", path)
        if method == "PUT" and m:
            qid = m.group(1)
            self.questions[qid]
            f = dict(body)
            f["decision"] = "auto" if body["est_cost_eur"] < 10 and not body["touches_blind"] else "needs_coordinator"
            self.feasibility[qid] = f
            return 200, {"decision": f["decision"]}
        if method == "POST" and path == "/api/agent/suggestions":
            self.suggestions.append(body)
            return 200, {"ok": True}
        return 404, {"error": "no route"}
