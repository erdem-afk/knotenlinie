"""The board service: ties storage, auth, notifications and domain rules together."""

from __future__ import annotations

import asyncio
import logging
import re
from typing import Any

from . import core
from .config import Settings
from .core import ApiError, jdumps, jloads
from .db import Store, in_iso, now_iso
from .mail import Mailer, notify
from .security import Hasher, RateLimiter, new_token

log = logging.getLogger("kurul")

LOGIN_MINUTES = 30
LONG_LINK_MINUTES = 7 * 24 * 60
SESSION_DAYS = 60
EMAIL_RE = re.compile(r"^[^@\s]{1,64}@[^@\s]{1,255}\.[^@\s]{2,}$")


class Bus:
    """Wakes long-polls and SSE streams when an event is committed (single process)."""

    def __init__(self):
        self.loop: asyncio.AbstractEventLoop | None = None
        self._ev: asyncio.Event | None = None

    def attach(self, loop: asyncio.AbstractEventLoop) -> None:
        self.loop = loop
        self._ev = asyncio.Event()

    def bump(self) -> None:
        if self.loop is None:
            return
        try:
            self.loop.call_soon_threadsafe(self._fire)
        except RuntimeError:
            pass

    def _fire(self) -> None:
        if self._ev is not None:
            self._ev.set()
        self._ev = asyncio.Event()

    def snapshot(self) -> asyncio.Event | None:
        return self._ev

    @staticmethod
    async def wait(ev: asyncio.Event | None, timeout: float) -> None:
        if ev is None:
            await asyncio.sleep(timeout)
            return
        try:
            await asyncio.wait_for(ev.wait(), timeout)
        except asyncio.TimeoutError:
            pass


class Board:
    def __init__(self, settings: Settings, mailer: Mailer | None = None):
        self.settings = settings
        self.bus = Bus()
        self.store = Store(settings.db_path, on_event=self.bus.bump)
        self.hash = Hasher(settings.session_secret or self._persisted_secret())
        self.mailer = mailer or Mailer(settings.smtp_url, settings.mail_from)
        self.limiter = RateLimiter()
        self._bootstrap()

    # ------------------------------------------------------------ setup

    def _persisted_secret(self) -> str:
        with self.store.tx() as tx:
            r = tx.one("SELECT value FROM meta WHERE key='session_secret'")
            if r:
                return r["value"]
            s = new_token()
            tx.execute("INSERT INTO meta(key,value) VALUES ('session_secret',?)", (s,))
        log.warning("KURUL_SESSION_SECRET is not set; using a generated secret stored in the database")
        return s

    def _bootstrap(self) -> None:
        token = self.settings.bootstrap_token
        generated = False
        if not token:
            token, generated = new_token(), True
        with self.store.tx() as tx:
            created = core.ensure_bootstrap(tx, self.settings.coordinator_email, self.hash(token))
        if created:
            if generated:
                log.warning("Coordinator created. One-time login link (7 days): %s",
                            self.login_url(token))
            else:
                log.warning("Coordinator created. Sign in once with %s/auth/verify?token=<KURUL_BOOTSTRAP_TOKEN>",
                            self.settings.base_url)

    def login_url(self, token: str, next_path: str | None = None) -> str:
        u = f"{self.settings.base_url}/auth/verify?token={token}"
        if next_path:
            from urllib.parse import quote
            u += "&next=" + quote(next_path, safe="")
        return u

    # ------------------------------------------------------------ auth

    def request_login(self, email: str, ip: str) -> None:
        if not self.limiter.hit(f"login-ip:{ip}", self.settings.login_rate_per_ip, 900):
            raise ApiError(429, "too many requests; try again in a few minutes")
        email = (email or "").strip().lower()
        if not EMAIL_RE.match(email):
            return
        if not self.limiter.hit(f"login-email:{email}", self.settings.login_rate_per_email, 900):
            log.info("login request rate-limited for an address")
            return
        with self.store.tx() as tx:
            u = tx.one("SELECT * FROM users WHERE email=? AND role IN ('member','coordinator')", (email,))
            if not u:
                log.info("login requested for an address that is not invited")
                return
            token = core.create_login_token(tx, self.hash, u["id"], LOGIN_MINUTES)
        link = self.login_url(token)
        self.mailer.send(u["email"], "Your sign-in link for Knotenlinie Board",
                         f"Hello {u['name']},\n\nOpen this link to sign in to Knotenlinie Board. "
                         f"It works once and expires in {LOGIN_MINUTES} minutes.\n\n{link}\n\n"
                         "If you did not ask for it, you can ignore this email.\n")

    def peek_login_token(self, token: str) -> dict | None:
        if not token or len(token) > 200:
            return None
        with self.store.read() as db:
            r = db.one("SELECT u.* FROM login_tokens t JOIN users u ON u.id=t.user_id "
                       "WHERE t.token_hash=? AND t.used_at IS NULL AND t.expires_at>? "
                       "AND u.role IN ('member','coordinator')", (self.hash(token), now_iso()))
        return dict(r) if r else None

    def consume_login_token(self, token: str) -> str | None:
        """Mark the token used and open a session. Returns the session token."""
        if not token or len(token) > 200:
            return None
        h = self.hash(token)
        with self.store.tx() as tx:
            r = tx.one("SELECT t.user_id FROM login_tokens t JOIN users u ON u.id=t.user_id "
                       "WHERE t.token_hash=? AND t.used_at IS NULL AND t.expires_at>? "
                       "AND u.role IN ('member','coordinator')", (h, now_iso()))
            if not r:
                return None
            tx.execute("UPDATE login_tokens SET used_at=? WHERE token_hash=?", (now_iso(), h))
            session = new_token()
            from .db import in_iso
            tx.execute("INSERT INTO sessions(token_hash,user_id,expires_at) VALUES (?,?,?)",
                       (self.hash(session), r["user_id"], in_iso(days=SESSION_DAYS)))
            tx.execute("DELETE FROM sessions WHERE expires_at<?", (now_iso(),))
        return session

    def session_user(self, session: str | None) -> dict | None:
        if not session or len(session) > 200:
            return None
        with self.store.read() as db:
            r = db.one("SELECT u.* FROM sessions s JOIN users u ON u.id=s.user_id "
                       "WHERE s.token_hash=? AND s.expires_at>? AND u.role IN ('member','coordinator')",
                       (self.hash(session), now_iso()))
        return dict(r) if r else None

    def logout(self, session: str | None) -> None:
        if session:
            with self.store.tx() as tx:
                tx.execute("DELETE FROM sessions WHERE token_hash=?", (self.hash(session),))

    # ------------------------------------------------------------ me

    @staticmethod
    def me_out(u: dict) -> dict:
        return {"id": u["id"], "name": u["name"], "email": u["email"], "role": u["role"],
                "public_name_ok": None if u["public_name_ok"] is None else bool(u["public_name_ok"]),
                "can_invite": u["role"] == "coordinator" or bool(u.get("can_invite"))}

    def update_me(self, user: dict, data: dict) -> dict:
        sets: dict[str, Any] = {}
        if "name" in data and data["name"] is not None:
            name = str(data["name"]).strip()
            if not (1 <= len(name) <= 80):
                raise ApiError(400, "name must be 1 to 80 characters")
            sets["name"] = name
        if "public_name_ok" in data and data["public_name_ok"] is not None:
            if not isinstance(data["public_name_ok"], bool):
                raise ApiError(400, "public_name_ok must be true or false")
            sets["public_name_ok"] = int(data["public_name_ok"])
        with self.store.tx() as tx:
            if sets:
                tx.execute(f"UPDATE users SET {', '.join(k + '=?' for k in sets)} WHERE id=?",
                           (*sets.values(), user["id"]))
                tx.emit("user.updated", {"user_id": user["id"],
                                         "public_name_ok": bool(sets.get("public_name_ok",
                                                                         user["public_name_ok"]))})
            u = dict(tx.one("SELECT * FROM users WHERE id=?", (user["id"],)))
        return self.me_out(u)

    def members(self) -> list[dict]:
        with self.store.read() as db:
            return [core.user_brief(dict(r)) for r in
                    db.all("SELECT * FROM users ORDER BY CASE role WHEN 'member' THEN 0 "
                           "WHEN 'coordinator' THEN 1 ELSE 2 END, name")]

    # ------------------------------------------------------------ notifications

    def _notify_users(self, tx, user_ids, kind: str, subject: str, line: str, root_id: int) -> None:
        users = core.users_map(tx)
        jobs = []
        for uid in {u for u in user_ids if u}:
            u = users.get(uid)
            if not u or u["role"] == "agent":
                continue
            token = core.create_login_token(tx, self.hash, uid, LONG_LINK_MINUTES)
            jobs.append((u, self.login_url(token, f"/?thread={root_id}")))
        tx.after_commit(lambda: [notify(self.mailer, u, kind, subject, line, link) for u, link in jobs])

    def _short(self, s: str, n: int = 90) -> str:
        s = " ".join((s or "").split())
        return s if len(s) <= n else s[: n - 1] + "…"

    # ------------------------------------------------------------ messages (humans)

    def post_message(self, user: dict, body: Any, root_id: Any) -> dict:
        if not isinstance(body, str) or not body.strip():
            raise ApiError(400, "message is empty")
        if len(body) > core.MAX_BODY:
            raise ApiError(400, f"message is longer than {core.MAX_BODY} characters")
        if root_id is not None and (isinstance(root_id, bool) or not isinstance(root_id, int)):
            raise ApiError(400, "root_id must be an integer")
        if not self.limiter.hit(f"msg:{user['id']}", self.settings.message_rate_per_min, 60):
            raise ApiError(429, "you are sending messages too quickly; wait a moment")
        with self.store.tx() as tx:
            if root_id is not None:
                root = core.get_visible(tx, root_id, user["id"])
                if root["root_id"] is not None:
                    raise ApiError(400, "replies go to the thread's first message")
            mid = core.post_message(tx, user["id"], body=body.rstrip(), root_id=root_id)
            # Mentions by name -> notification
            mentioned = []
            for u in tx.all("SELECT * FROM users WHERE role IN ('member','coordinator') AND id<>?",
                            (user["id"],)):
                name = u["name"].strip()
                if len(name) >= 3 and re.search(r"(?<!\w)@?" + re.escape(name) + r"(?!\w)", body,
                                                re.IGNORECASE):
                    mentioned.append(u["id"])
            if mentioned:
                self._notify_users(tx, mentioned, "mention",
                                   f"{user['name']} mentioned you on Knotenlinie Board",
                                   f"{user['name']} wrote: \"{self._short(body, 140)}\"",
                                   root_id or mid)
        return {"id": mid}

    def hide(self, user: dict, msg_id: int) -> None:
        with self.store.tx() as tx:
            core.hide_message(tx, msg_id, user["id"])

    def forward(self, user: dict, msg_id: int, note: Any) -> dict:
        if note is not None and not isinstance(note, str):
            raise ApiError(400, "note must be text")
        note = (note or "").strip()
        if len(note) > core.MAX_BODY:
            raise ApiError(400, "note is too long")
        if not self.limiter.hit(f"fwd:{user['id']}", 10, 60):
            raise ApiError(429, "too many forwards; wait a moment")
        with self.store.tx() as tx:
            m = core.get_visible(tx, msg_id, user["id"])
            if m["kind"] != "text" or m["hidden_at"]:
                raise ApiError(400, "only visible text messages can be forwarded")
            cur = tx.execute("INSERT INTO forwards(message_id,by_user_id,note,created_at) VALUES (?,?,?,?)",
                             (msg_id, user["id"], note or None, now_iso()))
            fid = int(cur.lastrowid)
            tx.emit("message.forwarded", {"forward_id": fid, "message_id": msg_id,
                                          "root_id": m["root_id"] or m["id"],
                                          "by_user_id": user["id"], "note": note or None})
        return {"forward_id": fid}

    # ------------------------------------------------------------ card actions

    def _log_suggestion(self, tx, message_id: int, outcome: str, source: str) -> None:
        tx.execute("INSERT INTO suggestion_log(message_id,outcome,source,created_at) VALUES (?,?,?,?) "
                   "ON CONFLICT(message_id,source) DO UPDATE SET outcome=excluded.outcome",
                   (message_id, outcome, source, now_iso()))

    def card_action(self, user: dict, msg_id: int, action: Any, text: Any) -> dict:
        if not isinstance(action, str):
            raise ApiError(400, "action is required")
        if text is not None and not isinstance(text, str):
            raise ApiError(400, "text must be a string")
        text = (text or "").strip()
        if len(text) > core.MAX_BODY:
            raise ApiError(400, "text is too long")
        if not self.limiter.hit(f"act:{user['id']}", 30, 60):
            raise ApiError(429, "too many actions; wait a moment")
        maxr = self.settings.max_running
        with self.store.tx() as tx:
            m = core.get_visible(tx, msg_id, user["id"])
            if m["kind"] != "card" or m["hidden_at"]:
                raise ApiError(400, "not a card")
            card = jloads(m["card_json"]) or {}
            ctype = card.get("type")
            if action not in core.CARD_ACTIONS.get(ctype, ()):
                raise ApiError(400, f"'{action}' is not an action of a {ctype} card")
            if m["card_state_json"]:
                raise ApiError(409, "this card has already been answered")
            if user["id"] not in core.card_actors(tx, m, card):
                raise ApiError(403, "you cannot act on this card")
            blocked = core.card_blocked(tx, m, card)
            if blocked:
                raise ApiError(409, f"this card is {blocked}")
            state: dict[str, Any] = {"action": action, "by": user["id"], "at": now_iso()}
            result: dict[str, Any] = {}

            if ctype in core.PRIVATE_CARD_TYPES:
                target_id = core.card_target_id(m, card)
                tr = tx.one("SELECT * FROM messages WHERE id=?", (target_id,))
                if not tr:
                    raise ApiError(409, "the message no longer exists")
                target = dict(tr)
                if action == "yes":
                    if target["hidden_at"]:
                        raise ApiError(409, "the message was hidden")
                    existing = core.question_for_target(tx, target["id"])
                    if existing:
                        qid, root = existing["id"], existing["root_message_id"]
                    else:
                        forwarder = note = None
                        if ctype == "confirm":
                            forwarder = user["id"] if user["id"] != target["author_id"] else None
                            f = tx.one("SELECT note FROM forwards WHERE message_id=? AND by_user_id=? "
                                       "ORDER BY id DESC LIMIT 1", (target["id"], user["id"]))
                            note = f["note"] if f else None
                        root = core.question_root_for(tx, target, card["restated"], target["author_id"])
                        qid = core.create_question(tx, root_message_id=root, restated=card["restated"],
                                                   author_id=target["author_id"], forwarder_id=forwarder,
                                                   note=note)
                        tx.emit("question.confirmed", core.confirmed_payload(core.get_question(tx, qid)))
                    state["question_id"] = qid
                    state["root_message_id"] = root
                    result.update(question_id=qid, root_message_id=root)
                self._log_suggestion(tx, target["id"], "accepted" if action == "yes" else "declined", ctype)

            elif ctype == "plan":
                q = core.question_for_root(tx, core.thread_root_of(m))
                if action == "approve":
                    run_allowed = core.approve_plan(tx, q, user["id"], maxr)
                    q2 = core.get_question(tx, q["id"])
                    result.update(question_id=q["id"], run_allowed=run_allowed, status=q2["status"],
                                  queue_pos=q2["queue_pos"])
                else:
                    if not text:
                        raise ApiError(400, "please say what should change")
                    state["text"] = text

            elif ctype == "answer_record":
                q = core.question_for_root(tx, core.thread_root_of(m))
                if action == "test_anyway":
                    core.set_status(tx, q["id"], "recorded", path="test", plan_approved_at=None)
                    result.update(question_id=q["id"], status="recorded", path="test")
                elif text:
                    state["text"] = text

            tx.execute("UPDATE messages SET card_state_json=? WHERE id=?", (jdumps(state), msg_id))
            payload = {"message_id": msg_id, "action": action, "by_user_id": user["id"]}
            if state.get("text"):
                payload["text"] = state["text"]
            tx.emit("card.action", payload)
        return {"ok": True, **result}

    # ------------------------------------------------------------ admin

    def admin_users(self) -> list[dict]:
        with self.store.read() as db:
            rows = db.all("SELECT u.*, i.name AS invited_by_name, "
                          "(SELECT MAX(created_at) FROM messages WHERE author_id=u.id) AS last_message_at "
                          "FROM users u LEFT JOIN users i ON i.id=u.invited_by ORDER BY u.id")
            return [self._admin_user_out(r) for r in rows]

    @staticmethod
    def _admin_user_out(r) -> dict:
        return {"id": r["id"], "email": r["email"], "name": r["name"], "role": r["role"],
                "public_name_ok": None if r["public_name_ok"] is None else bool(r["public_name_ok"]),
                "created_at": r["created_at"], "last_message_at": r["last_message_at"],
                "can_invite": r["role"] == "coordinator" or bool(r["can_invite"]),
                "invited_by": ({"id": r["invited_by"], "name": r["invited_by_name"]}
                               if r["invited_by"] is not None else None)}

    def admin_set_user(self, user_id: int, data: dict) -> dict:
        if not isinstance(data, dict) or set(data) != {"can_invite"}:
            raise ApiError(400, "send {can_invite: true|false}")
        if not isinstance(data["can_invite"], bool):
            raise ApiError(400, "can_invite must be true or false")
        with self.store.tx() as tx:
            u = tx.one("SELECT role FROM users WHERE id=?", (user_id,))
            if not u:
                raise ApiError(404, "user not found")
            if u["role"] != "member":
                raise ApiError(400, "only members have a changeable invitation right")
            tx.execute("UPDATE users SET can_invite=? WHERE id=?", (int(data["can_invite"]), user_id))
        with self.store.read() as db:
            r = db.one("SELECT u.*, i.name AS invited_by_name, "
                       "(SELECT MAX(created_at) FROM messages WHERE author_id=u.id) AS last_message_at "
                       "FROM users u LEFT JOIN users i ON i.id=u.invited_by WHERE u.id=?", (user_id,))
            return self._admin_user_out(r)

    def admin_invites(self, limit: int = 500) -> list[dict]:
        with self.store.read() as db:
            rows = db.all("SELECT v.*, u.name AS user_name, b.name AS by_name, b.role AS by_role "
                          "FROM invites v LEFT JOIN users u ON u.id=v.user_id "
                          "LEFT JOIN users b ON b.id=v.invited_by ORDER BY v.id DESC LIMIT ?", (limit,))
            return [{"id": r["id"], "created_at": r["created_at"], "email": r["email"],
                     "outcome": r["outcome"],
                     "user": {"id": r["user_id"], "name": r["user_name"]} if r["user_id"] else None,
                     "invited_by": ({"id": r["invited_by"], "name": r["by_name"], "role": r["by_role"]}
                                    if r["invited_by"] is not None else None)}
                    for r in rows]

    @staticmethod
    def _clean_invite(data: Any) -> tuple[str, str]:
        if not isinstance(data, dict):
            raise ApiError(400, "send {email, name}")
        email = data.get("email")
        name = data.get("name")
        email = email.strip().lower() if isinstance(email, str) else ""
        name = name.strip() if isinstance(name, str) else ""
        if len(email) > 254 or not EMAIL_RE.match(email):
            raise ApiError(400, "please enter a valid email address")
        if not (1 <= len(name) <= 80):
            raise ApiError(400, "please enter a name (up to 80 characters)")
        if any(ord(c) < 32 or 0x7F <= ord(c) < 0xA0 or c in "\u2028\u2029" for c in name):
            raise ApiError(400, "the name must be a single line of text")
        return email, name

    def invite(self, data: dict, inviter: dict | None = None) -> dict:
        """Invite a member. inviter None = internal call (tests, scripts), treated like the coordinator.

        The invitee is always a new `member`; an existing address is never changed or duplicated.
        """
        by_coordinator = inviter is None or inviter["role"] == "coordinator"
        if not by_coordinator and not (inviter["role"] == "member" and inviter.get("can_invite")):
            raise ApiError(403, "you cannot invite colleagues; ask the coordinator")
        email, name = self._clean_invite(data)
        inviter_id = inviter["id"] if inviter else None
        mail_job = None
        with self.store.tx() as tx:
            if not by_coordinator:
                n = tx.one("SELECT COUNT(*) AS n FROM invites WHERE invited_by=? AND created_at>?",
                           (inviter_id, in_iso(days=-1)))["n"]
                if n >= self.settings.invite_rate_per_day:
                    raise ApiError(429, f"you can send up to {self.settings.invite_rate_per_day} "
                                        "invitations a day; please try again tomorrow")
            u = tx.one("SELECT * FROM users WHERE email=?", (email,))
            if u:
                if by_coordinator:
                    if u["role"] == "agent":
                        raise ApiError(400, "that address belongs to the agent")
                    may_link = True
                else:
                    may_link = u["role"] == "member" and u["invited_by"] == inviter_id
                tx.execute("INSERT INTO invites(user_id,invited_by,email,outcome,created_at) VALUES (?,?,?,?,?)",
                           (u["id"] if may_link else None, inviter_id, email,
                            "new_link" if may_link else "exists", now_iso()))
                if not may_link:
                    return {"created": False, "already_invited": True,
                            "message": "This address has already been invited to the board."}
                uid, invitee_name, created = u["id"], u["name"], False
            else:
                uid = int(tx.execute(
                    "INSERT INTO users(email,name,role,public_name_ok,created_at,can_invite,invited_by) "
                    "VALUES (?,?,'member',NULL,?,0,?)", (email, name, now_iso(), inviter_id)).lastrowid)
                invitee_name, created = name, True
                tx.execute("INSERT INTO invites(user_id,invited_by,email,outcome,created_at) VALUES (?,?,?,?,?)",
                           (uid, inviter_id, email, "created", now_iso()))
                tx.emit("user.invited", {"user_id": uid, "invited_by": inviter_id})
            token = core.create_login_token(tx, self.hash, uid, LONG_LINK_MINUTES)
            link = self.login_url(token)
            if not by_coordinator:
                text = (f"Hello {invitee_name},\n\n{inviter['name']} invited you to Knotenlinie Board, "
                        "the board chat of the Knotenlinie project.\n\nOpen this link to sign in. "
                        f"It works once and expires in 7 days.\n\n{link}\n\n"
                        "If you do not want to join, you can ignore this email.\n")
                mail_job = (email, text)
                tx.after_commit(lambda: self.mailer.send(mail_job[0], "You are invited to Knotenlinie Board",
                                                         mail_job[1]))
        if by_coordinator:
            return {"user_id": uid, "created": created, "login_url": link}
        out: dict[str, Any] = {"user_id": uid, "created": created, "emailed": self.mailer.enabled}
        if not self.mailer.enabled:
            # Without SMTP the email only reaches the server log, so the inviter passes the link on.
            out["login_url"] = link
        return out

    def admin_feasibility(self) -> list[dict]:
        with self.store.read() as db:
            users = core.users_map(db)
            feas = core.feas_map(db)
            out = []
            for q in db.all("SELECT * FROM questions ORDER BY created_at DESC, id DESC"):
                f = feas.get(q["id"]) or {}
                out.append({
                    "question_id": q["id"], "restated": q["restated"], "status": q["status"],
                    "status_label": core.STATUS_LABELS.get(q["status"], q["status"]),
                    "path": q["path"], "queue_pos": q["queue_pos"], "hold_reason": q["hold_reason"],
                    "root_message_id": q["root_message_id"], "plan_approved": bool(q["plan_approved_at"]),
                    "author": users.get(q["author_id"], {}).get("name"),
                    "forwarder": users.get(q["forwarder_id"], {}).get("name") if q["forwarder_id"] else None,
                    "has_report": bool(f.get("public_summary") or f.get("private_detail")),
                    "public_summary": f.get("public_summary"), "private_detail": f.get("private_detail"),
                    "est_cost_eur": f.get("est_cost_eur"),
                    "touches_blind": None if not f else bool(f.get("touches_blind")),
                    "decision": f.get("decision"), "decided_at": f.get("decided_at"),
                })
            return out

    def admin_hold(self, user: dict, qid: str, reason: Any) -> dict:
        reason = str(reason or "").strip()
        if not reason:
            raise ApiError(400, "please give a reason; it is shown in the thread")
        if len(reason) > 1000:
            raise ApiError(400, "reason is too long")
        with self.store.tx() as tx:
            core.hold(tx, qid, reason, user["id"], self.settings.max_running)
            q = core.get_question(tx, qid)
        return {"question_id": qid, "status": q["status"]}

    def admin_allow(self, user: dict, qid: str, release: bool) -> dict:
        with self.store.tx() as tx:
            return core.coordinator_allow(tx, qid, self.settings.max_running, release=release,
                                          by_user_id=user["id"])

    def admin_suggestions(self) -> dict:
        with self.store.read() as db:
            out: dict[str, dict] = {}
            for src in ("suggest", "confirm"):
                counts = {"offered": 0, "accepted": 0, "declined": 0}
                for r in db.all("SELECT outcome, COUNT(*) AS n FROM suggestion_log WHERE source=? "
                                "GROUP BY outcome", (src,)):
                    counts[r["outcome"]] = r["n"]
                counts["total"] = sum(counts.values())
                answered = counts["accepted"] + counts["declined"]
                counts["accept_rate"] = round(counts["accepted"] / answered, 3) if answered else None
                out[src] = counts
            return out

    # ------------------------------------------------------------ agent API

    def agent_events(self, after: int, limit: int = 200) -> list[dict]:
        with self.store.read() as db:
            return [{"id": r["id"], "type": r["type"], "payload": jloads(r["payload_json"]),
                     "created_at": r["created_at"]}
                    for r in db.all("SELECT * FROM events WHERE id>? ORDER BY id LIMIT ?", (after, limit))]

    def last_event_id(self) -> int:
        with self.store.read() as db:
            return db.one("SELECT COALESCE(MAX(id),0) AS m FROM events")["m"]

    def agent_thread(self, root_id: int) -> dict:
        with self.store.read() as db:
            r = db.one("SELECT * FROM messages WHERE id=?", (root_id,))
            if not r:
                raise ApiError(404, "message not found")
            if r["root_id"] is not None:
                r = db.one("SELECT * FROM messages WHERE id=?", (r["root_id"],))
            users = core.users_map(db)
            root = dict(r)
            q = core.question_for_root(db, root["id"])
            feas = core.feas_map(db)
            qout = core.agent_question_out(q, users, feas.get(q["id"])) if q else None
            return {"root": core.agent_message_out(db, root, users),
                    "replies": [core.agent_message_out(db, dict(x), users) for x in
                                db.all("SELECT * FROM messages WHERE root_id=? ORDER BY id", (root["id"],))],
                    "question": qout,
                    "author_public_name_ok": qout["author_public_name_ok"] if qout else None,
                    "forwards": [dict(f) for f in db.all(
                        "SELECT f.* FROM forwards f JOIN messages m ON m.id=f.message_id "
                        "WHERE m.id=? OR m.root_id=? ORDER BY f.id", (root["id"], root["id"]))]}

    def agent_recent(self, limit: int) -> list[dict]:
        with self.store.read() as db:
            users = core.users_map(db)
            rows = db.all("SELECT * FROM messages WHERE root_id IS NULL ORDER BY id DESC LIMIT ?", (limit,))
            out = []
            for r in rows[::-1]:
                o = core.agent_message_out(db, dict(r), users)
                o["reply_count"] = db.one("SELECT COUNT(*) AS n FROM messages WHERE root_id=?",
                                          (r["id"],))["n"]
                out.append(o)
            return out

    def agent_question(self, qid: str) -> dict:
        with self.store.read() as db:
            q = core.get_question(db, qid)
            return core.agent_question_out(q, core.users_map(db), core.feas_map(db).get(qid))

    def agent_post(self, data: dict, idem_key: str | None = None) -> dict:
        if idem_key is not None:
            idem_key = idem_key.strip()
            if not idem_key or len(idem_key) > 200:
                raise ApiError(400, "Idempotency-Key must be 1 to 200 characters")
            with self.store.read() as db:
                r = db.one("SELECT message_id FROM idempotency WHERE key=?", (idem_key,))
            if r:
                return {"id": r["message_id"], "duplicate": True}
        root_id = data.get("root_id")
        body = data.get("body")
        card = data.get("card")
        visible_to = data.get("visible_to")
        if (body is None or body == "") == (card is None):
            raise ApiError(400, "send exactly one of body or card")
        if body is not None and (not isinstance(body, str) or len(body) > 20000):
            raise ApiError(400, "body must be text of at most 20000 characters")
        for name, v in (("root_id", root_id), ("visible_to", visible_to)):
            if v is not None and (isinstance(v, bool) or not isinstance(v, int)):
                raise ApiError(400, f"{name} must be an integer")
        with self.store.tx() as tx:
            if idem_key:
                r = tx.one("SELECT message_id FROM idempotency WHERE key=?", (idem_key,))
                if r:
                    return {"id": r["message_id"], "duplicate": True}
            if root_id is not None:
                r = tx.one("SELECT * FROM messages WHERE id=?", (root_id,))
                if not r:
                    raise ApiError(404, "root message not found")
                root_id = r["root_id"] or r["id"]
            if visible_to is not None:
                vu = tx.one("SELECT * FROM users WHERE id=?", (visible_to,))
                if not vu or vu["role"] == "agent":
                    raise ApiError(400, "visible_to is not a board user")
            cleaned = core.clean_card(card) if card is not None else None
            if cleaned and cleaned["type"] == "suggest":
                tid = cleaned.get("quoted_message_id") or root_id
                if not tid:
                    raise ApiError(400, "a suggest card needs quoted_message_id (or root_id)")
                t = tx.one("SELECT * FROM messages WHERE id=?", (tid,))
                if not t or t["hidden_at"] or t["kind"] != "text":
                    raise ApiError(409, "the message is missing, hidden or not text")
                if visible_to is None:
                    visible_to = t["author_id"]
                if visible_to != t["author_id"]:
                    raise ApiError(400, "a suggest card is visible only to the message's author")
                log_row = tx.one("SELECT outcome FROM suggestion_log WHERE message_id=? AND source='suggest'",
                                 (tid,))
                if log_row and log_row["outcome"] != "offered":
                    raise ApiError(409, "a suggestion was already answered for this message")
                for c in tx.all("SELECT card_json FROM messages WHERE kind='card' AND visible_to=?",
                                (visible_to,)):
                    cc = jloads(c["card_json"]) or {}
                    if cc.get("type") == "suggest" and (cc.get("quoted_message_id") == tid):
                        raise ApiError(409, "a suggestion was already offered for this message")
                if core.question_for_target(tx, tid):
                    raise ApiError(409, "this message is already a question")
                cleaned["quoted_message_id"] = tid
                if root_id is None:
                    root_id = t["root_id"] or t["id"]
                self._log_suggestion(tx, tid, "offered", "suggest")
            if cleaned and cleaned["type"] == "confirm":
                qm = tx.one("SELECT * FROM messages WHERE id=?", (cleaned["quoted_message_id"],))
                if not qm:
                    raise ApiError(404, "quoted message not found")
                if visible_to is None:
                    f = tx.one("SELECT by_user_id FROM forwards WHERE message_id=? ORDER BY id DESC LIMIT 1",
                               (qm["id"],))
                    if not f:
                        raise ApiError(400, "nobody forwarded that message; give visible_to")
                    visible_to = f["by_user_id"]
                elif not tx.one("SELECT 1 FROM forwards WHERE message_id=? AND by_user_id=?",
                                (qm["id"], visible_to)):
                    raise ApiError(400, "visible_to did not forward that message")
                if root_id is None:
                    root_id = qm["root_id"] or qm["id"]
            mid = core.post_message(tx, core.agent_id(tx), body=body or "", root_id=root_id,
                                    card=cleaned, visible_to=visible_to)
            if idem_key:
                tx.execute("INSERT INTO idempotency(key,message_id,created_at) VALUES (?,?,?)",
                           (idem_key, mid, now_iso()))
            if cleaned and cleaned["type"] in ("answer_record", "answer_test") and root_id:
                q = core.question_for_root(tx, root_id)
                if q:
                    self._notify_users(tx, [q["author_id"], q["forwarder_id"]], "answer",
                                       f"An answer has arrived ({q['id']})",
                                       f"Your question: \"{self._short(q['restated'])}\"\n"
                                       "The agent has posted an answer in the thread.", root_id)
        return {"id": mid}

    def agent_create_question(self, data: dict) -> dict:
        rid = data.get("root_message_id")
        aid = data.get("author_id")
        fid = data.get("forwarder_id")
        restated = data.get("restated")
        note = data.get("note")
        for name, v in (("root_message_id", rid), ("author_id", aid)):
            if isinstance(v, bool) or not isinstance(v, int):
                raise ApiError(400, f"{name} must be an integer")
        if fid is not None and (isinstance(fid, bool) or not isinstance(fid, int)):
            raise ApiError(400, "forwarder_id must be an integer")
        if not isinstance(restated, str) or not restated.strip() or len(restated) > core.MAX_FIELD:
            raise ApiError(400, "restated is required")
        if note is not None and not isinstance(note, str):
            raise ApiError(400, "note must be text")
        with self.store.tx() as tx:
            t = tx.one("SELECT * FROM messages WHERE id=?", (rid,))
            if not t:
                raise ApiError(404, "message not found")
            for uid in (aid, fid):
                if uid is not None:
                    u = tx.one("SELECT role FROM users WHERE id=?", (uid,))
                    if not u or u["role"] == "agent":
                        raise ApiError(400, "author_id/forwarder_id must be board users")
            existing = core.question_for_target(tx, rid)
            if existing:
                raise ApiError(409, f"message already anchors {existing['id']}")
            root = core.question_root_for(tx, dict(t), restated.strip(), aid)
            qid = core.create_question(tx, root_message_id=root, restated=restated.strip(), author_id=aid,
                                       forwarder_id=fid, note=note)
            tx.emit("question.confirmed", core.confirmed_payload(core.get_question(tx, qid)))
        return {"id": qid, "root_message_id": root}

    def agent_patch_question(self, qid: str, data: dict) -> dict:
        status = data.get("status")
        path = data.get("path", ...)
        restated = data.get("restated")
        if status is not None and status not in core.STATUSES:
            raise ApiError(400, f"unknown status {status!r}")
        if path is not ... and path is not None and path not in core.PATHS:
            raise ApiError(400, f"unknown path {path!r}")
        if restated is not None and (not isinstance(restated, str) or not restated.strip()):
            raise ApiError(400, "restated must be non-empty text")
        maxr = self.settings.max_running
        with self.store.tx() as tx:
            q = core.get_question(tx, qid)
            new_path = q["path"] if path is ... else path
            if path is not ... and path != q["path"]:
                tx.execute("UPDATE questions SET path=?, updated_at=? WHERE id=?", (path, now_iso(), qid))
            if restated is not None:
                tx.execute("UPDATE questions SET restated=?, updated_at=? WHERE id=?",
                           (restated.strip(), now_iso(), qid))
            if status is not None and status != q["status"]:
                if q["status"] == "on_hold" and status in ("frozen", "running", "queued"):
                    raise ApiError(409, "the question is on hold; the coordinator must release it")
                if (status in core.SLOT_STATUSES and new_path == "test"
                        and q["status"] not in core.SLOT_STATUSES
                        and core.slots_used(tx, exclude=qid) >= maxr):
                    raise ApiError(409, f"{maxr} test runs are already active; the question must queue")
                extra: dict[str, Any] = {}
                if status == "queued":
                    extra["queue_pos"] = (tx.one("SELECT MAX(queue_pos) AS m FROM questions "
                                                 "WHERE status='queued'")["m"] or 0) + 1
                core.set_status(tx, qid, status, **extra)
                if status == "waiting_approval":
                    self._notify_users(tx, [q["author_id"], q["forwarder_id"]], "plan_waiting",
                                       f"A test plan is waiting for your approval ({qid})",
                                       f"Your question: \"{self._short(q['restated'])}\"\n"
                                       "We wrote a test plan. Nothing runs until you approve it.",
                                       q["root_message_id"])
            elif path is not ... or restated is not None:
                tx.emit("question.updated", {"question_id": qid, "status": q["status"]})
            core.fill_slots(tx, maxr)
            q2 = core.get_question(tx, qid)
        return {"id": qid, "status": q2["status"], "path": q2["path"], "queue_pos": q2["queue_pos"]}

    def agent_feasibility(self, qid: str, data: dict) -> dict:
        with self.store.tx() as tx:
            res = core.upsert_feasibility(tx, qid, data, self.settings.max_running)
            q = core.get_question(tx, qid)
            subj = (f"Feasibility report {qid}: needs your decision" if res["decision"] == "needs_coordinator"
                    else f"Feasibility report {qid}")
            coords = [c["id"] for c in core.coordinators(tx)]
            self._notify_users(tx, coords, "feasibility", subj,
                               f"Question: \"{self._short(q['restated'])}\"\n"
                               f"Estimated cost: {float(data['est_cost_eur']):.2f} EUR. "
                               f"Blind data: {'yes' if data.get('touches_blind') else 'no'}. "
                               f"Decision: {res['decision']}.", q["root_message_id"])
        return res

    def agent_suggestion(self, data: dict) -> dict:
        mid = data.get("message_id")
        outcome = data.get("outcome")
        if isinstance(mid, bool) or not isinstance(mid, int):
            raise ApiError(400, "message_id must be an integer")
        if outcome not in ("offered", "accepted", "declined"):
            raise ApiError(400, "outcome must be offered, accepted or declined")
        with self.store.tx() as tx:
            if not tx.one("SELECT 1 FROM messages WHERE id=?", (mid,)):
                raise ApiError(404, "message not found")
            row = tx.one("SELECT outcome FROM suggestion_log WHERE message_id=? AND source='suggest'", (mid,))
            if row and outcome == "offered":
                raise ApiError(409, f"already logged as {row['outcome']}; never re-offer")
            self._log_suggestion(tx, mid, outcome, "suggest")
        return {"ok": True}

    # ------------------------------------------------------------ live events (humans)

    HUMAN_HIDDEN_TYPES = {"user.updated"}

    def visible_events(self, viewer: dict, after: int, limit: int = 200) -> tuple[list[dict], int]:
        """Events the viewer may know about, reduced to ids and type; plus the last id scanned."""
        out = []
        last = after
        with self.store.read() as db:
            for r in db.all("SELECT * FROM events WHERE id>? ORDER BY id LIMIT ?", (after, limit)):
                last = r["id"]
                p = jloads(r["payload_json"]) or {}
                t = r["type"]
                if t in self.HUMAN_HIDDEN_TYPES:
                    continue
                if t in ("feasibility.updated", "user.invited") and viewer["role"] != "coordinator":
                    continue
                if t == "message.forwarded" and p.get("by_user_id") != viewer["id"]:
                    continue
                if t in ("message.created", "card.action"):
                    m = db.one("SELECT visible_to, root_id FROM messages WHERE id=?", (p.get("message_id"),))
                    if not m or (m["visible_to"] and m["visible_to"] != viewer["id"]):
                        continue
                    p = {**p, "root_id": m["root_id"]}
                slim = {"id": r["id"], "type": t}
                for k in ("message_id", "root_id", "question_id"):
                    if p.get(k) is not None:
                        slim[k] = p[k]
                out.append(slim)
        return out, last
