"""Deterministic stand-in for the model (KURUL_LLM=fake). Used by every test; makes no network calls.

It reads only the member data blocks of the prompt, so text outside them never changes its
behaviour. Test markers inside member text steer it:
  [[conf=0.80]]                 classify: question with this confidence
  [[fake:violate=<rule>]]       put a rule-breaking sentence in the output (probability, prediction,
                                cost, infra, name); [[fake:violate=<rule>@<job>]] only in that job
  [[fake:clarify]]              respond: out-of-domain clarify path
  [[fake:record=ID,ID]]         respond: record answer citing these ids
  fail-review (plain word)      review: blocking problem (survives restating)
  [[fake:bad_json]]             any job: output that is not JSON
"""

from __future__ import annotations

import json
import re

from .guard import extract_data_blocks

VIOLATIONS = {
    "probability": "The probability of an M7 earthquake in Istanbul within the next 30 years is 64%.",
    "prediction": "This is a prediction of the next rupture.",
    "cost": "The run will cost about 40 EUR.",
    "infra": "It runs on our Hetzner machine under /srv/knotenlinie.",
    "name": "The coordinator Testname Coordinator will check it.",
}

_Q_WORDS = re.compile(r"\b(do|does|did|is|are|was|were|has|have|can|could|will|mı|mi|mu|mü|midir|mıdır|"
                      r"var mı|oluyor mu)\b", re.I)
_REQ_WORDS = re.compile(r"\b(test|check|compare|sınay|sına|deneyin|bakın|karşılaştır)\w*", re.I)
_GREET = re.compile(r"\b(good morning|hello|thanks|thank you|günaydın|merhaba|teşekkür)\w*", re.I)


def _strip(t: str) -> str:
    return re.sub(r"\[\[[^\]]*\]\]", "", t).strip()


def _items(block: str) -> list[tuple[str, str]]:
    out, head, buf = [], None, []
    for line in block.splitlines():
        m = re.match(r"^\[(.*)\]$", line)
        if m:
            if head is not None:
                out.append((head, "\n".join(buf).strip()))
            head, buf = m.group(1), []
        else:
            buf.append(line)
    if head is not None:
        out.append((head, "\n".join(buf).strip()))
    return out


class FakeLLM:
    def __init__(self):
        self.calls: list[dict] = []

    def __call__(self, job, prompt, cwd, tools=None):
        self.calls.append({"job": job, "prompt": prompt, "cwd": str(cwd), "tools": list(tools or [])})
        blocks = extract_data_blocks(prompt)
        items = [it for b in blocks for it in _items(b)]
        data = "\n".join(t for _, t in items)
        if "[[fake:bad_json]]" in data:
            return "Sorry, I cannot do that."
        target = next((t for h, t in items if "TARGET" in h), items[-1][1] if items else "")
        bad = None
        for rule, only in re.findall(r"\[\[fake:violate=(\w+)(?:@(\w+))?\]\]", data):
            if not only or only == job:
                bad = VIOLATIONS.get(rule)
        lang = "tr" if re.search(r"[çğışöüİ]|hocam", data, re.I) else "en"
        fn = getattr(self, "job_" + job, None)
        out = fn(prompt, items, target, bad, lang) if fn else {"text": "ok"}
        return json.dumps(out, ensure_ascii=False)

    # -- jobs ------------------------------------------------------------------------------------

    def job_classify(self, prompt, items, target, bad, lang):
        m = re.search(r"\[\[conf=([\d.]+)\]\]", target)
        t = _strip(target)
        if m:
            isq, conf = True, float(m.group(1))
        elif _GREET.search(t) and "?" not in t:
            isq, conf = False, 0.05
        elif ("?" in t and _Q_WORDS.search(t)) or _REQ_WORDS.search(t):
            isq, conf = True, 0.93
        else:
            isq, conf = False, 0.1
        restated = (t + (" " + bad if bad else "")) if isq else ""
        return {"is_question": isq, "confidence": conf, "restated": restated, "lang": lang, "injection": False}

    def job_restate(self, prompt, items, target, bad, lang):
        note = next((t for h, t in items if h.startswith("note")), "")
        msg = next((t for h, t in items if "forwarded message" in h), "")
        src = _strip(note) or _strip(msg)
        ok = ("?" in src) or bool(_REQ_WORDS.search(src))
        if not ok:
            return {"testable": False, "restated": "", "lang": lang,
                    "reason": "Bu mesajda sınanabilir bir soru yok." if lang == "tr"
                    else "There is no testable question in this message.", "injection": False}
        return {"testable": True, "restated": src + (" " + bad if bad else ""), "reason": "", "lang": lang,
                "injection": False}

    def _plan(self, question, bad, lang, extra_rule=""):
        tbd = ("Tam planda, elde edilebilecek olay sayısıyla belirlenecek." if lang == "tr"
               else "To be determined in the full plan, with the number of events available.")
        return {"question": question, "data": "An open earthquake catalogue and open focal mechanisms.",
                "rule": "Which events count, the baseline and what counts as yes, no or cannot tell are fixed "
                        "before any data are opened." + extra_rule,
                "smallest_effect": tbd,
                "public_feasibility": (bad or "Open data were found; a plan within a day, a run within weeks."),
                "feasibility": {"public_summary": "Open data found; run within weeks.",
                                "private_detail": "Open catalogue available; no blind data; local compute; "
                                                  "estimated 0 EUR.",
                                "est_cost_eur": 0, "touches_blind": False}}

    def job_respond(self, prompt, items, target, bad, lang):
        data = "\n".join(t for _, t in items)
        question = _strip(next((t for h, t in items if h.startswith("restated")), data))
        forced = "asked for a new test" in prompt
        if "[[fake:clarify]]" in data and not forced:
            return {"path": "clarify", "lang": lang,
                    "text": (bad + " " if bad else "") + "We have no data or pipeline for structural questions; "
                    "how would you like it framed?", "injection": False}
        rec = re.search(r"\[\[fake:record=([\w,\-]+)\]\]", data)
        if (rec or "GNSS" in data) and not forced:
            ids = rec.group(1).split(",") if rec else ["TR-1", "TR-11"]
            return {"path": "record", "lang": lang,
                    "summary": "Yes, and we found no usable signal." + (" " + bad if bad else ""),
                    "points": [{"text": f"Entry {i} addresses this.", "ids": [i]} for i in ids],
                    "limits": "Part of this was never run, so it is not evidence of absence.", "injection": False}
        p = self._plan(question, bad, lang)
        p.update({"path": "test", "lang": lang, "intro": "I found no earlier test of this in our ledger, so it "
                  "needs a new test.", "related_ids": [], "injection": False})
        return p

    def job_revise_plan(self, prompt, items, target, bad, lang):
        question = _strip(items[0][1]) if items else ""
        change = _strip(next((t for h, t in items if "change request" in h), ""))
        p = self._plan(question, bad, lang, extra_rule=" Revised: " + change)
        p.update({"note": "I changed the rule as you asked.", "lang": lang, "injection": False})
        return p

    def job_thread_reply(self, prompt, items, target, bad, lang):
        t = _strip(target).lower()
        if "change" in t or "değiş" in t:
            return {"action": "revise", "change_request": _strip(target), "text": "", "lang": lang,
                    "injection": False}
        if "?" in t:
            return {"action": "reply", "change_request": "", "lang": lang, "injection": False,
                    "text": "The rule line of the plan fixes this before any data are opened." + (
                        " " + bad if bad else "")}
        return {"action": "none", "change_request": "", "text": "", "lang": lang, "injection": False}

    def job_mention_reply(self, prompt, items, target, bad, lang):
        txt = ("Merhaba Hocam. Defterimizden cevap verebilir ya da yeni bir sınama planı yazabilirim."
               if lang == "tr" else "Hello. I can answer from our ledger or draft a new test plan.")
        return {"text": txt + (" " + bad if bad else ""), "lang": lang, "injection": False}

    def job_review(self, prompt, items, target, bad, lang):
        if "fail-review" in prompt:
            return {"ok": False, "blocking": ["The magnitude cut is not fixed in advance."], "minor": []}
        return {"ok": True, "blocking": [], "minor": ["State the declustering method."]}

    def job_run(self, prompt, items, target, bad, lang):
        return {"verdict": "H0", "summary": "No difference was found between the two groups." + (
            " " + bad if bad else ""), "limits": "One region only.", "files": [],
                "ledger": {"sonuc": "Fark yok (fake).", "ders": "Fake run."}, "lang": lang}
