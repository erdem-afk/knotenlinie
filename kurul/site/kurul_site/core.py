"""Domain logic: messages, cards, questions, the run queue, feasibility.

Every function that writes takes a `Tx` (see db.py). Functions that only read take
anything with `.one()` / `.all()`.
"""

from __future__ import annotations

import json
import re
from typing import Any

from .db import Tx, in_iso, now_iso
from .security import new_token

# ---------------------------------------------------------------- vocabularies

STATUS_LABELS = {
    "recorded": "Recorded",
    "plan_drafted": "Plan drafted",
    "waiting_approval": "Waiting for your approval",
    "frozen": "Frozen",
    "running": "Running",
    "answered": "Answered",
    "answered_record": "Answered from the record",
    "in_ledger": "In ledger",
    "on_hold": "On hold",
    "not_feasible": "Not feasible",
    "withdrawn": "Withdrawn",
    "queued": "Queued",
}
STATUSES = set(STATUS_LABELS)
PATHS = {"record", "test"}
SLOT_STATUSES = ("running", "frozen")
FINISHED = {"answered", "answered_record", "in_ledger", "not_feasible", "withdrawn"}
APPROVABLE = {"recorded", "plan_drafted", "waiting_approval"}

CARD_ACTIONS: dict[str, tuple[str, ...]] = {
    "suggest": ("yes", "no"),
    "confirm": ("yes", "no"),
    "plan": ("approve", "change"),
    "answer_record": ("test_anyway", "not_answered"),
    "answer_test": (),
    "notice": (),
}
PRIVATE_CARD_TYPES = ("suggest", "confirm")

MENTION_RE = re.compile(r"@knotenlinie\b", re.IGNORECASE)
MAX_BODY = 4000
MAX_FIELD = 8000


class ApiError(Exception):
    def __init__(self, status: int, detail: str):
        super().__init__(detail)
        self.status = status
        self.detail = detail


def jloads(s: str | None) -> Any:
    return json.loads(s) if s else None


def jdumps(o: Any) -> str:
    return json.dumps(o, ensure_ascii=False, separators=(",", ":"))


# ---------------------------------------------------------------- users

def users_map(db) -> dict[int, dict]:
    return {r["id"]: dict(r) for r in db.all("SELECT * FROM users")}


def user_brief(u: dict | None) -> dict:
    if not u:
        return {"id": None, "name": "Unknown", "role": "member"}
    return {"id": u["id"], "name": u["name"], "role": u["role"]}


def agent_id(db) -> int:
    r = db.one("SELECT id FROM users WHERE role='agent' ORDER BY id LIMIT 1")
    if not r:
        raise ApiError(500, "agent user missing")
    return r["id"]


def coordinators(db) -> list[dict]:
    return [dict(r) for r in db.all("SELECT * FROM users WHERE role='coordinator'")]


def ensure_bootstrap(tx: Tx, coordinator_email: str, bootstrap_hash: str | None) -> bool:
    """Create the coordinator and agent users on first start. Returns True if created."""
    created = False
    if not tx.one("SELECT 1 FROM users WHERE role='agent'"):
        tx.execute("INSERT INTO users(email,name,role,public_name_ok,created_at) VALUES (?,?,?,?,?)",
                   ("agent@invalid", "Knotenlinie", "agent", 1, now_iso()))
    if not tx.one("SELECT 1 FROM users WHERE role='coordinator'"):
        email = coordinator_email.strip().lower() or "coordinator@invalid"
        existing = tx.one("SELECT id FROM users WHERE email=?", (email,))
        if existing:
            tx.execute("UPDATE users SET role='coordinator' WHERE id=?", (existing["id"],))
            uid = existing["id"]
        else:
            cur = tx.execute(
                "INSERT INTO users(email,name,role,public_name_ok,created_at) VALUES (?,?,?,?,?)",
                (email, "Board Coordinator", "coordinator", None, now_iso()))
            uid = cur.lastrowid
        if bootstrap_hash:
            tx.execute("INSERT OR IGNORE INTO login_tokens(token_hash,user_id,expires_at,used_at) "
                       "VALUES (?,?,?,NULL)", (bootstrap_hash, uid, in_iso(days=7)))
        created = True
    return created


def create_login_token(tx: Tx, hasher, user_id: int, minutes: float) -> str:
    token = new_token()
    tx.execute("INSERT INTO login_tokens(token_hash,user_id,expires_at,used_at) VALUES (?,?,?,NULL)",
               (hasher(token), user_id, in_iso(minutes=minutes)))
    return token


# ---------------------------------------------------------------- cards

def _s(v: Any, name: str, required: bool = False, limit: int = MAX_FIELD) -> str:
    if v is None or v == "":
        if required:
            raise ApiError(400, f"card field '{name}' is required")
        return ""
    if not isinstance(v, str):
        raise ApiError(400, f"card field '{name}' must be a string")
    if len(v) > limit:
        raise ApiError(400, f"card field '{name}' is too long")
    return v


def _url(v: Any, name: str, required: bool = False) -> str:
    u = _s(v, name, required, 2000)
    if u and not re.match(r"^https?://[^\s]+$", u, re.IGNORECASE):
        raise ApiError(400, f"card field '{name}' must be an http(s) URL")
    return u


def _int(v: Any, name: str, required: bool = False) -> int | None:
    if v is None:
        if required:
            raise ApiError(400, f"card field '{name}' is required")
        return None
    if isinstance(v, bool) or not isinstance(v, int):
        raise ApiError(400, f"card field '{name}' must be an integer")
    return v


def _links(v: Any, name: str) -> list[dict]:
    if v is None:
        return []
    if not isinstance(v, list) or len(v) > 50:
        raise ApiError(400, f"card field '{name}' must be a list (max 50)")
    out = []
    for i, item in enumerate(v):
        if not isinstance(item, dict):
            raise ApiError(400, f"card field '{name}[{i}]' must be an object")
        out.append({"label": _s(item.get("label"), f"{name}[{i}].label", True, 200),
                    "url": _url(item.get("url"), f"{name}[{i}].url", False)})
    return out


def clean_card(card: Any) -> dict:
    """Validate an agent card and keep only the known fields."""
    if not isinstance(card, dict):
        raise ApiError(400, "card must be an object")
    t = card.get("type")
    if t not in CARD_ACTIONS:
        raise ApiError(400, f"unknown card type {t!r}")
    if t == "suggest":
        qid = card.get("quoted_message_id")
        if qid is None:
            qid = card.get("message_id")  # accepted alias
        return {"type": t, "restated": _s(card.get("restated"), "restated", True),
                "quoted_message_id": _int(qid, "quoted_message_id")}
    if t == "confirm":
        return {"type": t, "restated": _s(card.get("restated"), "restated", True),
                "quoted_message_id": _int(card.get("quoted_message_id"), "quoted_message_id", True)}
    if t == "plan":
        return {"type": t,
                "draft_no": _int(card.get("draft_no"), "draft_no", True),
                "question": _s(card.get("question"), "question", True),
                "data": _s(card.get("data"), "data"),
                "rule": _s(card.get("rule"), "rule"),
                "smallest_effect": _s(card.get("smallest_effect"), "smallest_effect"),
                "full_plan_url": _url(card.get("full_plan_url"), "full_plan_url") or None,
                "public_feasibility": _s(card.get("public_feasibility"), "public_feasibility")}
    if t == "answer_record":
        pts = card.get("points") or []
        if not isinstance(pts, list) or len(pts) > 50:
            raise ApiError(400, "card field 'points' must be a list (max 50)")
        points = []
        for i, p in enumerate(pts):
            if not isinstance(p, dict):
                raise ApiError(400, f"card field 'points[{i}]' must be an object")
            points.append({"text": _s(p.get("text"), f"points[{i}].text", True),
                           "refs": _links(p.get("refs"), f"points[{i}].refs")})
        return {"type": t, "summary": _s(card.get("summary"), "summary", True),
                "points": points, "limits": _s(card.get("limits"), "limits")}
    if t == "answer_test":
        return {"type": t, "verdict": _s(card.get("verdict"), "verdict", True, 500),
                "summary": _s(card.get("summary"), "summary", True),
                "links": _links(card.get("links"), "links"),
                "limits": _s(card.get("limits"), "limits")}
    # notice
    return {"type": t, "text": _s(card.get("text"), "text", True),
            "quoted_message_id": _int(card.get("quoted_message_id"), "quoted_message_id")}


def card_target_id(msg: dict, card: dict) -> int | None:
    """The member message a suggest/confirm card is about."""
    if card["type"] == "suggest":
        return card.get("quoted_message_id") or card.get("message_id") or msg["root_id"] or msg["id"]
    if card["type"] == "confirm":
        return card.get("quoted_message_id")
    return None


def thread_root_of(msg: dict) -> int:
    return msg["root_id"] or msg["id"]


def question_for_root(db, root_id: int) -> dict | None:
    r = db.one("SELECT * FROM questions WHERE root_message_id=?", (root_id,))
    return dict(r) if r else None


def latest_plan_id(db, root_id: int) -> int | None:
    rows = db.all("SELECT id, card_json FROM messages WHERE root_id=? AND kind='card' "
                  "ORDER BY id DESC", (root_id,))
    for r in rows:
        c = jloads(r["card_json"]) or {}
        if c.get("type") == "plan":
            return r["id"]
    return None


def card_actors(db, msg: dict, card: dict) -> set[int]:
    t = card["type"]
    if t in PRIVATE_CARD_TYPES:
        return {msg["visible_to"]} if msg["visible_to"] else set()
    if t in ("plan", "answer_record"):
        q = question_for_root(db, thread_root_of(msg))
        if not q:
            return set()
        return {x for x in (q["author_id"], q["forwarder_id"]) if x}
    return set()


def card_blocked(db, msg: dict, card: dict) -> str | None:
    """Why a card cannot be acted on any more (besides already being acted on)."""
    if card["type"] == "plan":
        if latest_plan_id(db, thread_root_of(msg)) != msg["id"]:
            return "superseded"
        q = question_for_root(db, thread_root_of(msg))
        if q and q["status"] not in APPROVABLE:
            return "closed"
    if card["type"] == "answer_record":
        q = question_for_root(db, thread_root_of(msg))
        if q and q["path"] == "test":
            return "closed"
    return None


# ---------------------------------------------------------------- serialisation

def question_out(q: dict, viewer_id: int | None, users: dict, feas: dict | None) -> dict:
    author = users.get(q["author_id"])
    fwd = users.get(q["forwarder_id"]) if q["forwarder_id"] else None
    mine = viewer_id in (q["author_id"], q["forwarder_id"])
    label = STATUS_LABELS[q["status"]]
    if q["status"] == "waiting_approval" and not mine:
        label = "Waiting for approval"
    if q["status"] == "queued" and q["queue_pos"]:
        label = f"Queued (position {q['queue_pos']})"
    return {
        "id": q["id"], "status": q["status"], "status_label": label, "path": q["path"],
        "queue_pos": q["queue_pos"], "restated": q["restated"],
        "root_message_id": q["root_message_id"],
        "author": "Board member" if q["anonymised"] else (author["name"] if author else "Unknown"),
        "forwarder": fwd["name"] if fwd else None,
        "mine": mine, "hold_reason": q["hold_reason"],
        "public_summary": (feas or {}).get("public_summary") or None,
        "created_at": q["created_at"], "updated_at": q["updated_at"],
    }


def _card_out(db, m: dict, viewer_id: int | None, users: dict) -> dict:
    card = jloads(m["card_json"]) or {}
    state = jloads(m["card_state_json"])
    out: dict[str, Any] = {"card": card}
    if state:
        st = dict(state)
        if st.get("by"):
            st["by_name"] = users.get(st["by"], {}).get("name")
        out["card_state"] = st
    blocked = None if state else card_blocked(db, m, card)
    if blocked:
        out["card_blocked"] = blocked
    actors = card_actors(db, m, card)
    out["can_act"] = list(CARD_ACTIONS.get(card.get("type"), ())) if (
        viewer_id in actors and not state and not blocked) else []
    if card.get("type") in ("plan", "answer_record") and not state and not blocked:
        out["actors"] = sorted(users[a]["name"] for a in actors if a in users)
    return out


def message_out(db, m: dict, viewer_id: int | None, users: dict) -> dict:
    base = {"id": m["id"], "root_id": m["root_id"], "author": user_brief(users.get(m["author_id"])),
            "created_at": m["created_at"]}
    if m["hidden_at"]:
        base["hidden"] = True
        return base
    base.update({"kind": m["kind"], "visible_to": m["visible_to"]})
    if m.get("moved_from"):
        base["moved_from"] = m["moved_from"]
    if m["visible_to"]:
        base["visible_to_name"] = users.get(m["visible_to"], {}).get("name")
    if m["kind"] == "text":
        base["body"] = m["body"]
    else:
        base.update(_card_out(db, m, viewer_id, users))
    return base


def feas_map(db) -> dict[str, dict]:
    return {r["question_id"]: dict(r) for r in db.all("SELECT * FROM feasibility")}


def top_level_out(db, rows: list, viewer_id: int, users: dict) -> list[dict]:
    feas = feas_map(db)
    out = []
    for r in rows:
        m = dict(r)
        o = message_out(db, m, viewer_id, users)
        rc = db.one("SELECT COUNT(*) AS n, MAX(created_at) AS last FROM messages "
                    "WHERE root_id=? AND visible_to IS NULL", (m["id"],))
        o["reply_count"] = rc["n"]
        o["last_reply_at"] = rc["last"]
        q = question_for_root(db, m["id"])
        if q:
            o["question"] = question_out(q, viewer_id, users, feas.get(q["id"]))
        priv = db.all("SELECT * FROM messages WHERE root_id=? AND visible_to=? ORDER BY id",
                      (m["id"], viewer_id))
        if priv:
            o["private_replies"] = [message_out(db, dict(p), viewer_id, users) for p in priv]
        out.append(o)
    return out


VISIBLE = "(visible_to IS NULL OR visible_to = ?)"


def list_feed(db, viewer_id: int, after: int | None, before: int | None, limit: int) -> list[dict]:
    users = users_map(db)
    if after is not None:
        rows = db.all(f"SELECT * FROM messages WHERE root_id IS NULL AND {VISIBLE} AND id>? "
                      "ORDER BY id ASC LIMIT ?", (viewer_id, after, limit))
    else:
        cond, params = "", [viewer_id]
        if before is not None:
            cond, params = " AND id<?", [viewer_id, before]
        rows = db.all(f"SELECT * FROM messages WHERE root_id IS NULL AND {VISIBLE}{cond} "
                      "ORDER BY id DESC LIMIT ?", (*params, limit))[::-1]
    return top_level_out(db, rows, viewer_id, users)


def get_visible(db, msg_id: int, viewer_id: int) -> dict:
    r = db.one(f"SELECT * FROM messages WHERE id=? AND {VISIBLE}", (msg_id, viewer_id))
    if not r:
        raise ApiError(404, "message not found")
    return dict(r)


def list_thread(db, root_id: int, viewer_id: int, after: int | None, limit: int) -> dict:
    root = get_visible(db, root_id, viewer_id)
    if root["root_id"] is not None:
        raise ApiError(400, "not a thread root")
    users = users_map(db)
    rows = db.all(f"SELECT * FROM messages WHERE root_id=? AND {VISIBLE} AND id>? ORDER BY id LIMIT ?",
                  (root_id, viewer_id, after or 0, limit))
    return {"root": top_level_out(db, [root], viewer_id, users)[0],
            "messages": [message_out(db, dict(r), viewer_id, users) for r in rows]}


def list_questions(db, viewer_id: int) -> list[dict]:
    users = users_map(db)
    feas = feas_map(db)
    out = []
    for q in db.all("SELECT * FROM questions ORDER BY created_at DESC, id DESC"):
        o = question_out(dict(q), viewer_id, users, feas.get(q["id"]))
        rc = db.one("SELECT COUNT(*) AS n FROM messages WHERE root_id=? AND visible_to IS NULL",
                    (q["root_message_id"],))
        o["reply_count"] = rc["n"]
        out.append(o)
    return out


# ---------------------------------------------------------------- agent view

def agent_author(u: dict | None) -> dict:
    b = user_brief(u)
    if u:
        b["public_name_ok"] = None if u["public_name_ok"] is None else bool(u["public_name_ok"])
        b["public_name"] = u["name"] if u["public_name_ok"] == 1 else "Board member"
    return b


def agent_message_out(db, m: dict, users: dict) -> dict:
    """Agent view of one message: the same shape for roots, replies and recent messages."""
    q = question_for_root(db, m["id"]) if m["root_id"] is None else None
    o = {"id": m["id"], "root_id": m["root_id"], "author": agent_author(users.get(m["author_id"])),
         "created_at": m["created_at"], "hidden": bool(m["hidden_at"]), "body": None,
         "kind": m["kind"], "card": None, "card_state": None, "visible_to": m["visible_to"],
         "moved_from": m.get("moved_from"),
         "question": {"id": q["id"], "status": q["status"], "path": q["path"]} if q else None}
    if m["hidden_at"]:
        return o
    if m["kind"] == "text":
        o["body"] = m["body"]
    else:
        o["card"] = jloads(m["card_json"])
        o["card_state"] = jloads(m["card_state_json"])
    return o


def agent_question_out(q: dict, users: dict, feas: dict | None) -> dict:
    d = {k: q[k] for k in ("id", "root_message_id", "author_id", "forwarder_id", "note", "restated",
                           "status", "path", "queue_pos", "created_at", "updated_at",
                           "hold_reason")}
    d["anonymised"] = bool(q["anonymised"])
    d["plan_approved"] = bool(q["plan_approved_at"])
    a = users.get(q["author_id"])
    d["author"] = agent_author(a)
    ok = None if not a or a["public_name_ok"] is None else bool(a["public_name_ok"])
    if q["anonymised"]:
        ok = False
        d["author"]["public_name"] = "Board member"
        d["author"]["public_name_ok"] = False
    d["author_public_name_ok"] = ok
    f = feas or {}
    d["public_summary"] = f.get("public_summary") or None
    d["feasibility_decision"] = f.get("decision")
    return d


def confirmed_payload(q: dict) -> dict:
    return {"question_id": q["id"], "root_message_id": q["root_message_id"], "restated": q["restated"],
            "author_id": q["author_id"], "forwarder_id": q["forwarder_id"], "note": q["note"]}


# ---------------------------------------------------------------- writes

def post_message(tx: Tx, author_id: int, *, body: str = "", root_id: int | None = None,
                 card: dict | None = None, visible_to: int | None = None,
                 moved_from: int | None = None) -> int:
    kind = "card" if card else "text"
    cur = tx.execute(
        "INSERT INTO messages(root_id,author_id,body,kind,card_json,visible_to,created_at,moved_from) "
        "VALUES (?,?,?,?,?,?,?,?)",
        (root_id, author_id, body if kind == "text" else "", kind,
         jdumps(card) if card else None, visible_to, now_iso(), moved_from))
    mid = int(cur.lastrowid)
    role = tx.one("SELECT role FROM users WHERE id=?", (author_id,))
    payload = {"message_id": mid, "root_id": root_id, "author_id": author_id,
               "author_role": role["role"] if role else None,
               # a moved copy is not a new request to the agent
               "mention": bool(kind == "text" and not moved_from and MENTION_RE.search(body or ""))}
    if moved_from:
        payload["moved_from"] = moved_from
    tx.emit("message.created", payload)
    return mid


def next_question_id(tx: Tx) -> str:
    n = 0
    for r in tx.all("SELECT id FROM questions"):
        try:
            n = max(n, int(r["id"].split("-", 1)[1]))
        except (IndexError, ValueError):
            pass
    return f"Q-{n + 1:03d}"


def question_root_for(tx: Tx, target: dict, restated: str, author_id: int) -> int:
    """A question needs its own top-level thread root.

    A plain top-level member message becomes the root itself. A reply inside a thread is copied
    to a new top-level message with the same text and original author, marked as moved from the
    thread. Hidden messages and messages that already anchor a question are refused.
    """
    if target["hidden_at"]:
        raise ApiError(409, "the message was hidden")
    if target["kind"] != "text":
        raise ApiError(400, "only text messages can become questions")
    if target["root_id"] is None:
        existing = question_for_root(tx, target["id"])
        if existing:
            raise ApiError(409, f"message already anchors {existing['id']}")
        return target["id"]
    return post_message(tx, target["author_id"], body=target["body"], moved_from=target["id"])


def question_for_target(db, target_id: int) -> dict | None:
    """The question anchored on this message, directly or on its moved top-level copy."""
    r = db.one("SELECT q.* FROM questions q JOIN messages m ON m.id=q.root_message_id "
               "WHERE m.id=? OR m.moved_from=? ORDER BY q.created_at LIMIT 1", (target_id, target_id))
    return dict(r) if r else None


def create_question(tx: Tx, *, root_message_id: int, restated: str, author_id: int,
                    forwarder_id: int | None = None, note: str | None = None) -> str:
    qid = next_question_id(tx)
    t = now_iso()
    tx.execute("INSERT INTO questions(id,root_message_id,author_id,forwarder_id,note,restated,status,"
               "path,queue_pos,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
               (qid, root_message_id, author_id, forwarder_id, note, restated, "recorded", None, None,
                t, t))
    return qid


def get_question(db, qid: str) -> dict:
    r = db.one("SELECT * FROM questions WHERE id=?", (qid,))
    if not r:
        raise ApiError(404, "question not found")
    return dict(r)


def slots_used(tx: Tx, exclude: str | None = None) -> int:
    r = tx.one("SELECT COUNT(*) AS n FROM questions WHERE status IN ('running','frozen') "
               "AND path='test' AND id<>?", (exclude or "",))
    return r["n"]


def renumber_queue(tx: Tx) -> None:
    rows = tx.all("SELECT id FROM questions WHERE status='queued' ORDER BY queue_pos, created_at")
    for i, r in enumerate(rows, 1):
        tx.execute("UPDATE questions SET queue_pos=? WHERE id=?", (i, r["id"]))


def set_status(tx: Tx, qid: str, status: str, **extra: Any) -> None:
    cols = {"status": status, "updated_at": now_iso(), **extra}
    if status != "queued":
        cols["queue_pos"] = None
    if status != "on_hold":
        cols.setdefault("hold_reason", None)
    sets = ", ".join(f"{k}=?" for k in cols)
    tx.execute(f"UPDATE questions SET {sets} WHERE id=?", (*cols.values(), qid))
    tx.emit("question.updated", {"question_id": qid, "status": status})


def fill_slots(tx: Tx, max_running: int) -> None:
    """Release queued questions into free run slots, oldest position first."""
    renumber_queue(tx)
    while slots_used(tx) < max_running:
        r = tx.one("SELECT id FROM questions WHERE status='queued' ORDER BY queue_pos LIMIT 1")
        if not r:
            break
        set_status(tx, r["id"], "frozen", path="test")
        tx.emit("run.released", {"question_id": r["id"]})
        renumber_queue(tx)


def start_or_queue(tx: Tx, qid: str, max_running: int) -> bool:
    """Put an approved test into a slot (frozen) or the queue. True when it may run now."""
    if slots_used(tx, exclude=qid) < max_running:
        set_status(tx, qid, "frozen", path="test", hold_reason=None)
        return True
    pos = (tx.one("SELECT MAX(queue_pos) AS m FROM questions WHERE status='queued'")["m"] or 0) + 1
    set_status(tx, qid, "queued", path="test", queue_pos=pos, hold_reason=None)
    return False


def decision_for(tx: Tx, qid: str) -> str:
    f = tx.one("SELECT decision FROM feasibility WHERE question_id=?", (qid,))
    return f["decision"] if f else "needs_coordinator"


WAITING_FOR_COORDINATOR = "Waiting for the coordinator's approval to run."


def approve_plan(tx: Tx, q: dict, by_user_id: int, max_running: int) -> bool:
    if q["status"] not in APPROVABLE:
        raise ApiError(409, f"question is {q['status']}; the plan cannot be approved now")
    tx.execute("UPDATE questions SET plan_approved_at=?, path='test' WHERE id=?", (now_iso(), q["id"]))
    decision = decision_for(tx, q["id"])
    if decision in ("auto", "approved"):
        run_allowed = start_or_queue(tx, q["id"], max_running)
    elif decision == "held":
        set_status(tx, q["id"], "on_hold", path="test")
        run_allowed = False
    else:
        set_status(tx, q["id"], "on_hold", path="test", hold_reason=WAITING_FOR_COORDINATOR)
        run_allowed = False
    tx.emit("plan.approved", {"question_id": q["id"], "by_user_id": by_user_id,
                              "run_allowed": run_allowed})
    return run_allowed


def coordinator_allow(tx: Tx, qid: str, max_running: int, *, release: bool,
                      by_user_id: int | None = None) -> dict:
    """approve_run / release: mark the run as approved and start or queue it if the plan is approved."""
    q = get_question(tx, qid)
    if q["status"] in FINISHED:
        raise ApiError(409, f"question is {q['status']}")
    if release and q["status"] != "on_hold":
        raise ApiError(409, "question is not on hold")
    t = now_iso()
    if tx.one("SELECT 1 FROM feasibility WHERE question_id=?", (qid,)):
        tx.execute("UPDATE feasibility SET decision='approved', decided_at=? WHERE question_id=?", (t, qid))
    else:
        tx.execute("INSERT INTO feasibility(question_id,decision,decided_at) VALUES (?,?,?)",
                   (qid, "approved", t))
    released = False
    if q["status"] == "on_hold":
        if q["plan_approved_at"]:
            released = start_or_queue(tx, qid, max_running)
            if released:
                tx.emit("run.released", {"question_id": qid})
        else:
            has_plan = latest_plan_id(tx, q["root_message_id"]) is not None
            set_status(tx, qid, "waiting_approval" if has_plan else "recorded", hold_reason=None)
        fill_slots(tx, max_running)
    else:
        tx.emit("question.updated", {"question_id": qid, "status": q["status"]})
    q2 = get_question(tx, qid)
    if by_user_id:
        text = ("Run released by the board coordinator." if release
                else "Run approved by the board coordinator.")
        if q2["status"] == "queued":
            text += f" It waits in the queue (position {q2['queue_pos']})."
        post_message(tx, by_user_id, root_id=q["root_message_id"], card={"type": "notice", "text": text})
    return {"question_id": qid, "status": q2["status"], "queue_pos": q2["queue_pos"],
            "released": released}


def hold(tx: Tx, qid: str, reason: str, by_user_id: int, max_running: int) -> None:
    q = get_question(tx, qid)
    if q["status"] in FINISHED:
        raise ApiError(409, f"question is {q['status']}")
    t = now_iso()
    if tx.one("SELECT 1 FROM feasibility WHERE question_id=?", (qid,)):
        tx.execute("UPDATE feasibility SET decision='held', decided_at=? WHERE question_id=?", (t, qid))
    else:
        tx.execute("INSERT INTO feasibility(question_id,decision,decided_at) VALUES (?,?,?)",
                   (qid, "held", t))
    set_status(tx, qid, "on_hold", hold_reason=reason)
    tx.emit("question.held", {"question_id": qid, "reason": reason})
    post_message(tx, by_user_id, root_id=q["root_message_id"],
                 card={"type": "notice", "text": f"Run on hold: {reason}"})
    fill_slots(tx, max_running)


def upsert_feasibility(tx: Tx, qid: str, data: dict, max_running: int) -> dict:
    q = get_question(tx, qid)
    try:
        cost = float(data.get("est_cost_eur"))
    except (TypeError, ValueError):
        raise ApiError(400, "est_cost_eur must be a number")
    if cost != cost or cost < 0:
        raise ApiError(400, "est_cost_eur must be a non-negative number")
    blind = data.get("touches_blind")
    if not isinstance(blind, (bool, int)):
        raise ApiError(400, "touches_blind must be a boolean")
    blind = bool(blind)
    pub = _s(data.get("public_summary"), "public_summary", True, 2000)
    priv = _s(data.get("private_detail"), "private_detail", False, 20000)
    rule = "auto" if (cost < 10 and not blind) else "needs_coordinator"
    old = tx.one("SELECT * FROM feasibility WHERE question_id=?", (qid,))
    decision = rule
    if old and old["decision"] == "held":
        decision = "held"
    elif old and old["decision"] == "approved" and rule != "auto":
        # The coordinator's approval stands only if the new estimate is no worse.
        if (old["est_cost_eur"] is not None and cost <= old["est_cost_eur"]
                and (not blind or old["touches_blind"])):
            decision = "approved"
    t = now_iso()
    tx.execute("INSERT INTO feasibility(question_id,public_summary,private_detail,est_cost_eur,"
               "touches_blind,decision,decided_at) VALUES (?,?,?,?,?,?,?) "
               "ON CONFLICT(question_id) DO UPDATE SET public_summary=excluded.public_summary, "
               "private_detail=excluded.private_detail, est_cost_eur=excluded.est_cost_eur, "
               "touches_blind=excluded.touches_blind, decision=excluded.decision, "
               "decided_at=excluded.decided_at",
               (qid, pub, priv, cost, int(blind), decision, t))
    tx.emit("feasibility.updated", {"question_id": qid, "decision": decision})
    # A plan approved before its feasibility report arrived was parked; release it if now allowed.
    if (q["status"] == "on_hold" and q["plan_approved_at"] and decision == "auto"
            and q["hold_reason"] == WAITING_FOR_COORDINATOR):
        if start_or_queue(tx, qid, max_running):
            tx.emit("run.released", {"question_id": qid})
    return {"question_id": qid, "decision": decision}


def hide_message(tx: Tx, msg_id: int, user_id: int) -> None:
    r = tx.one("SELECT * FROM messages WHERE id=?", (msg_id,))
    if not r or (r["visible_to"] and r["visible_to"] != user_id):
        raise ApiError(404, "message not found")
    m = dict(r)
    if m["author_id"] != user_id or m["kind"] != "text":
        raise ApiError(403, "you can only hide your own messages")
    if m["hidden_at"]:
        return
    t = now_iso()
    tx.execute("UPDATE messages SET body='', hidden_at=? WHERE id=?", (t, msg_id))
    # Open suggestion/confirm cards about this message can no longer create a question.
    for c in tx.all("SELECT * FROM messages WHERE kind='card' AND card_state_json IS NULL "
                    "AND visible_to IS NOT NULL"):
        card = jloads(c["card_json"]) or {}
        if card.get("type") in PRIVATE_CARD_TYPES and card_target_id(dict(c), card) == msg_id:
            tx.execute("UPDATE messages SET card_state_json=? WHERE id=?",
                       (jdumps({"void": "hidden", "at": t}), c["id"]))
    tx.emit("message.hidden", {"message_id": msg_id, "root_id": m["root_id"]})
    q = question_for_root(tx, msg_id)
    if q and q["status"] == "in_ledger" and not q["anonymised"]:
        tx.execute("UPDATE questions SET anonymised=1, updated_at=? WHERE id=?", (t, q["id"]))
        tx.emit("question.anonymised", {"question_id": q["id"]})
