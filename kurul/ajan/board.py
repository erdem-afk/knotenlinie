"""Tolerant readers for message and thread objects returned by the agent API.

SPEC v0 does not fix the JSON shape of GET /api/agent/thread; this accepts
{root, replies} or {messages}, and author as an object or as flat author_* fields.
"""

from __future__ import annotations

import re


def norm_msg(m: dict | None) -> dict | None:
    if not m:
        return None
    a = m.get("author") if isinstance(m.get("author"), dict) else {}
    author_name = a.get("name") if a else (m.get("author_name") or (m.get("author") if isinstance(m.get("author"), str) else None))
    q = m.get("question") if isinstance(m.get("question"), dict) else None
    return {
        "id": m.get("id"),
        "root_id": m.get("root_id"),
        "body": "" if m.get("hidden") or m.get("hidden_at") else (m.get("body") or ""),
        "hidden": bool(m.get("hidden") or m.get("hidden_at")),
        "kind": m.get("kind") or ("card" if m.get("card") or m.get("card_json") else "text"),
        "card": m.get("card") or m.get("card_json"),
        "author_id": a.get("id", m.get("author_id")) if a else m.get("author_id"),
        "author_name": author_name or "",
        "author_role": (a.get("role") if a else None) or m.get("author_role") or "",
        "question": q,
        "created_at": m.get("created_at"),
    }


def parse_thread(resp: dict) -> tuple[dict | None, list[dict]]:
    if not isinstance(resp, dict):
        return None, []
    if "root" in resp:
        root = norm_msg(resp.get("root"))
        replies = [norm_msg(x) for x in resp.get("replies") or resp.get("messages") or []]
    else:
        msgs = [norm_msg(x) for x in resp.get("messages") or []]
        root = next((x for x in msgs if not x["root_id"]), msgs[0] if msgs else None)
        replies = [x for x in msgs if x is not root]
    if root and root.get("question") is None and isinstance(resp.get("question"), dict):
        root["question"] = resp["question"]
    return root, [r for r in replies if r]


def parse_recent(resp) -> list[dict]:
    items = resp.get("messages") if isinstance(resp, dict) else resp
    return [norm_msg(x) for x in (items or []) if isinstance(x, dict)]


def is_agent(m: dict) -> bool:
    return (m.get("author_role") or "").lower() == "agent"


def label(m: dict, target: bool = False) -> str:
    who = m.get("author_name") or f"user {m.get('author_id')}"
    role = m.get("author_role") or "member"
    t = " TARGET" if target else ""
    return f"message {m.get('id')} by {who} ({role}){t}"


def as_text(m: dict) -> str:
    """Plain text view of a message for prompts (cards flattened)."""
    if m.get("hidden"):
        return "(message hidden)"
    if m.get("kind") == "card" and isinstance(m.get("card"), dict):
        c = m["card"]
        parts = [f"card {c.get('type')}"]
        for k in ("restated", "question", "data", "rule", "smallest_effect", "summary", "limits", "text",
                  "verdict"):
            if c.get(k):
                parts.append(f"{k}: {c[k]}")
        for p in c.get("points") or []:
            parts.append(f"- {p.get('text')}")
        return "\n".join(parts)
    return m.get("body") or ""


def mentions(body: str, handle: str = "knotenlinie") -> bool:
    return bool(re.search(r"@" + re.escape(handle) + r"\b", body or "", re.I))
