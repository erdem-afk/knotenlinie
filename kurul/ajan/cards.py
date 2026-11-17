"""Card builders (SPEC.md section 6). Every card is plain structured text; no HTML or markdown."""

from __future__ import annotations

import re

CARD_FIELDS = {
    "suggest": {"restated"},
    "confirm": {"restated", "quoted_message_id"},
    "plan": {"draft_no", "question", "data", "rule", "smallest_effect", "public_feasibility"},
    "answer_record": {"summary", "points", "limits"},
    "answer_test": {"verdict", "summary", "links", "limits"},
    "notice": {"text"},
}

_MD = re.compile(r"(\*\*|__|`|^#+\s|<[a-zA-Z/][^>]*>)", re.M)


def plain(s) -> str:
    """Strip markdown/HTML-ish decoration a model may add; collapse whitespace."""
    s = "" if s is None else str(s)
    s = _MD.sub("", s)
    return re.sub(r"[ \t]+", " ", s).strip()


def suggest(restated: str, quoted_message_id) -> dict:
    # quoted_message_id is not in SPEC v0 for suggest; added so the site can tie the card to the message.
    return {"type": "suggest", "restated": plain(restated), "quoted_message_id": quoted_message_id}


def confirm(restated: str, quoted_message_id) -> dict:
    return {"type": "confirm", "restated": plain(restated), "quoted_message_id": quoted_message_id}


def plan(draft_no: int, p: dict, full_plan_url: str | None = None) -> dict:
    c = {"type": "plan", "draft_no": int(draft_no),
         "question": plain(p.get("question")), "data": plain(p.get("data")), "rule": plain(p.get("rule")),
         "smallest_effect": plain(p.get("smallest_effect")),
         "public_feasibility": plain(p.get("public_feasibility"))}
    if full_plan_url:
        c["full_plan_url"] = full_plan_url
    return c


def answer_record(summary: str, points: list[dict], limits: str) -> dict:
    return {"type": "answer_record", "summary": plain(summary),
            "points": [{"text": plain(p["text"]), "refs": p["refs"]} for p in points],
            "limits": plain(limits)}


def answer_test(verdict: str, summary: str, links: list[dict], limits: str) -> dict:
    return {"type": "answer_test", "verdict": plain(verdict), "summary": plain(summary),
            "links": links, "limits": plain(limits)}


def notice(text: str) -> dict:
    return {"type": "notice", "text": plain(text)}


def valid(card: dict) -> bool:
    t = card.get("type")
    need = CARD_FIELDS.get(t)
    if need is None:
        return False
    for k in need:
        v = card.get(k)
        if v is None or (isinstance(v, str) and not v.strip()):
            return False
    if t == "answer_record":
        if not card["points"]:
            return False
        for p in card["points"]:
            if not p.get("text") or not p.get("refs"):
                return False
            for r in p["refs"]:
                if not r.get("label") or ("url" in r and not str(r["url"]).startswith("https://")):
                    return False
    return True
