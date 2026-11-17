"""Event loop and per-event jobs (SPEC.md section 7)."""

from __future__ import annotations

import hashlib
import json
import os
import signal
import time
import traceback
from pathlib import Path

from . import cards, guard
from .api import ApiError, SiteClient, TransientError
from .board import as_text, is_agent, label, mentions, parse_recent, parse_thread
from .config import Config
from .ledger import Ledger
from .llm import READ_ONLY, LLMError, make_llm, parse_json
from .log import excerpt, log
from .prompting import fill
from .state import State
from .texts import LANG_NAME, text

PLAN_STATES = {None, "", "recorded", "plan_drafted", "waiting_approval"}

# Files in KURUL_STATE_DIR read by the ops scripts in deploy/ (health check, updater).
HEARTBEAT_FILE = "heartbeat"   # epoch seconds of the last successful long-poll
BUSY_FILE = "busy.json"        # present while an event is being processed: {pid, event_id, type, since}


class Skip(Exception):
    """Event cannot be processed and should not be retried."""


class Worker:
    def __init__(self, cfg: Config, client: SiteClient | None = None, llm=None, state: State | None = None,
                 ledger: Ledger | None = None, sleep=time.sleep, git=None):
        self.cfg = cfg
        self.client = client or SiteClient(cfg.base_url, cfg.agent_token, backoff_base=cfg.backoff_base,
                                           backoff_max=cfg.backoff_max)
        self.llm = llm or make_llm(cfg)
        self.state = state or State(cfg.state_dir)
        self.ledger = ledger or Ledger(cfg.repo, cfg.ledger_path, cfg.repo_url, cfg.repo_ref)
        self.sleep = sleep
        self.git = git
        self.stop = False
        self.scratch = Path(cfg.state_dir) / "scratch"  # empty cwd for tool-less jobs
        self.scratch.mkdir(parents=True, exist_ok=True)

    # =========================================================================================
    # Loop
    # =========================================================================================

    def run_forever(self) -> None:
        def _stop(*_):
            self.stop = True
            log("stopping")
        signal.signal(signal.SIGTERM, _stop)
        signal.signal(signal.SIGINT, _stop)
        self._clear_busy()  # a marker left by a killed process is stale
        log("started", last_event_id=self.state.last_event_id(), llm=self.cfg.llm, autorun=self.cfg.autorun,
            ledger_rows=len(self.ledger.rows()))
        failures = 0
        while not self.stop:
            try:
                self.poll_once(self.cfg.poll_wait)
                failures = 0
            except (TransientError, ApiError) as e:
                failures += 1
                delay = min(self.cfg.backoff_max, self.cfg.backoff_base * (2 ** min(failures, 6)))
                log("poll_failed", level="warning", error=str(e)[:300], retry_in=delay)
                self._sleep_interruptible(delay)
            except Exception as e:  # never die on an unexpected error
                failures += 1
                log("poll_crashed", level="error", error=repr(e)[:300], trace=traceback.format_exc()[-1500:])
                self._sleep_interruptible(min(self.cfg.backoff_max, 5.0 * failures))
        log("stopped", last_event_id=self.state.last_event_id())

    def _sleep_interruptible(self, seconds: float) -> None:
        end = time.time() + seconds
        while not self.stop and time.time() < end:
            self.sleep(min(1.0, max(0.0, end - time.time())))

    def poll_once(self, wait: int = 0) -> int:
        resp = self.client.events(self.state.last_event_id(), wait)
        self._heartbeat()
        events = sorted(resp.get("events") or [], key=lambda e: int(e.get("id", 0)))
        for ev in events:
            if self.stop:
                break
            self.process(ev)
        last = resp.get("last")
        if not events and isinstance(last, int):
            self.state.set_last_event_id(last)
        return len(events)

    # Ops markers (best effort; never break the loop) ------------------------------------------

    def _heartbeat(self) -> None:
        try:
            _write_atomic(Path(self.cfg.state_dir) / HEARTBEAT_FILE, f"{time.time():.0f}\n")
        except OSError as e:
            log("heartbeat_failed", level="warning", error=str(e)[:200])

    def _set_busy(self, eid: int, etype: str) -> None:
        try:
            _write_atomic(Path(self.cfg.state_dir) / BUSY_FILE, json.dumps(
                {"pid": os.getpid(), "event_id": eid, "type": etype, "since": round(time.time())}) + "\n")
        except OSError:
            pass

    def _clear_busy(self) -> None:
        try:
            (Path(self.cfg.state_dir) / BUSY_FILE).unlink(missing_ok=True)
        except OSError:
            pass

    def process(self, ev: dict) -> str:
        eid = int(ev.get("id", 0))
        etype = ev.get("type", "?")
        if self.state.is_handled(eid):
            self.state.set_last_event_id(eid)
            return "duplicate"
        self._set_busy(eid, etype)
        try:
            return self._process(ev, eid, etype)
        finally:
            self._clear_busy()

    def _process(self, ev: dict, eid: int, etype: str) -> str:
        outcome = "error"
        for attempt in range(1, self.cfg.event_attempts + 1):
            try:
                outcome = self.dispatch(etype, ev.get("payload") or {}, eid) or "ok"
                break
            except Skip as e:
                outcome = f"skipped: {e}"
                break
            except (TransientError, LLMError) as e:
                log("event_retry", level="warning", event_id=eid, type=etype, attempt=attempt, error=str(e)[:300])
                if attempt < self.cfg.event_attempts:
                    self.sleep(min(self.cfg.backoff_max, self.cfg.backoff_base * (2 ** attempt)))
                    continue
                outcome = "failed"
            except Exception as e:
                log("event_error", level="error", event_id=eid, type=etype, error=repr(e)[:300],
                    trace=traceback.format_exc()[-1500:])
                outcome = "error"
                break
        self.state.mark_handled(eid, etype, outcome)
        self.state.set_last_event_id(eid)
        log("event_done", event_id=eid, type=etype, outcome=outcome)
        return outcome

    def dispatch(self, etype: str, p: dict, eid: int):
        h = {
            "message.created": self.on_message,
            "message.forwarded": self.on_forward,
            "question.confirmed": self.on_confirmed,
            "card.action": self.on_card_action,
            "plan.approved": self.on_plan_approved,
            "run.released": self.on_run_released,
            "question.held": self.on_held,
            "question.anonymised": self.on_anonymised,
        }.get(etype)
        if h is None:
            return "ignored"
        return h(p, eid)

    # =========================================================================================
    # Helpers: checks, posting, model calls
    # =========================================================================================

    def violations(self, obj) -> list[str]:
        return guard.check_obj(obj, blocked_names=self.cfg.blocked_names, blocked_terms=self.cfg.blocked_terms,
                               local_paths=[str(self.cfg.repo), str(self.cfg.state_dir)])

    def post(self, key: str, root_id, body: str | None = None, card: dict | None = None, visible_to=None,
             qid: str | None = None, meta: dict | None = None):
        """Post once per key. Returns the message id, or None when blocked by a rule."""
        done = self.state.step("post:" + key)
        if done is not None:
            return done
        content = card if card is not None else body
        bad = self.violations(content)
        if bad:
            log("post_blocked", level="warning", key=key, rules=bad)
            return None
        if card is not None and not cards.valid(card):
            log("card_invalid", level="warning", key=key, card_type=card.get("type"))
            return None
        if card is None:
            body = cards.plain(body)
        r = self.client.post_message(root_id, body=body, card=card, visible_to=visible_to, idempotency_key=key)
        mid = r.get("id")
        self.state.record_own(mid)
        self.state.set_step("post:" + key, mid)
        if card is not None:
            self.state.record_card(mid, card["type"], qid, dict(meta or {}, card=card))
        log("posted", key=key, message_id=mid, kind="card" if card else "text",
            card_type=card.get("type") if card else None, visible_to=visible_to)
        return mid

    def once(self, key: str, fn):
        """Run a side effect once per key (status changes, feasibility, files)."""
        if self.state.has_step(key):
            return self.state.step(key)
        v = fn()
        self.state.set_step(key, v if v is not None else True)
        return v

    def ask(self, key: str | None, job: str, prompt: str, cwd, tools, public_fields) -> dict | None:
        """Call the model, parse JSON, post-check member-facing fields; retry once with feedback.
        The accepted output is cached under `key` so a replayed event does not call the model again."""
        if key and self.state.has_step("llm:" + key):
            return self.state.step("llm:" + key)
        p = prompt
        out = None
        for attempt in (1, 2):
            raw = self.llm(job, p, cwd, tools)
            try:
                cand = parse_json(raw)
            except LLMError:
                log("model_output_unparsable", level="warning", job=job, attempt=attempt)
                p = prompt + "\n\nYour previous output was not a single JSON object. Output only the JSON object."
                continue
            if cand.get("injection"):
                out = cand
                break
            bad = self.violations(public_fields(cand))
            if not bad:
                out = cand
                break
            log("model_output_rejected", level="warning", job=job, attempt=attempt, rules=bad)
            p = (prompt + "\n\nYour previous output broke these rules: " + ", ".join(bad) +
                 ". Rewrite it so that every member-facing field follows all rules. Output only the JSON object.")
        if out is not None and key:
            self.state.set_step("llm:" + key, out)
        return out

    def report_injection(self, where: str, message_id=None, text_=None, qid=None) -> str:
        rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "kind": "injection_suspected",
               "where": where, "message_id": message_id, "question_id": qid, "excerpt": excerpt(text_, 300)}
        log("injection_suspected", level="warning", where=where, message_id=message_id, question_id=qid)
        try:
            with open(Path(self.cfg.state_dir) / "coordinator.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        except OSError:
            pass
        return "injection"

    def fetch_message(self, message_id, root_id=None):
        root, replies = parse_thread(self.client.thread(root_id or message_id))
        allm = ([root] if root else []) + replies
        msg = next((m for m in allm if str(m["id"]) == str(message_id)), None)
        return msg, root, replies

    @staticmethod
    def lang_of(*texts) -> str:
        for t in texts:
            if t and t.strip():
                return guard.detect_lang(t)
        return "en"

    def addr(self, name, lang) -> str:
        return guard.address(name, lang)

    # =========================================================================================
    # message.created
    # =========================================================================================

    def on_message(self, p: dict, eid: int):
        mid = p.get("message_id")
        if mid is None:
            raise Skip("no message_id")
        if self.state.is_own(mid):
            return "own"
        msg, root, replies = self.fetch_message(mid, p.get("root_id"))
        if msg is None:
            raise Skip("message not found")
        if is_agent(msg) or msg["kind"] == "card":
            return "agent_message"
        if msg["hidden"] or not msg["body"].strip():
            return "hidden_or_empty"
        q = self.question_for_root(root) if p.get("root_id") or msg["root_id"] else None
        if q:
            return self.on_question_thread_message(q, msg, root, replies)
        if p.get("mention") or mentions(msg["body"], self.cfg.handle):
            return self.on_mention(msg, root, replies)
        return self.maybe_suggest(msg, root, replies)

    def question_for_root(self, root):
        if not root:
            return None
        q = self.state.question_by_root(root["id"])
        if q:
            if root.get("question") and root["question"].get("status"):
                q = self.state.save_question(q["qid"], {"status": root["question"]["status"],
                                                        "path": root["question"].get("path") or q.get("path")})
            return q
        rq = root.get("question")
        if rq and rq.get("id"):
            return self.state.save_question(rq["id"], {
                "root_message_id": root["id"], "author_id": root["author_id"], "author_name": root["author_name"],
                "status": rq.get("status"), "path": rq.get("path"),
                "lang": self.lang_of(root["body"]), "restated": rq.get("restated") or root["body"]})
        return None

    def _context(self, msg, root, replies, n=5):
        if msg["root_id"]:
            before = [m for m in ([root] + replies) if m and m["id"] != msg["id"]
                      and str(m.get("created_at") or "") <= str(msg.get("created_at") or "~")]
            return before[-n:]
        try:
            recent = parse_recent(self.client.recent(limit=12))
        except (ApiError, TransientError):
            return []
        before = [m for m in recent if m["id"] != msg["id"] and _lt(m["id"], msg["id"])]
        before.sort(key=lambda m: _key(m["id"]))
        return before[-n:]

    def _classify(self, msg, root, replies, mention: bool):
        ctx = self._context(msg, root, replies)
        items = [(label(m), as_text(m)) for m in ctx] + [(label(msg, target=True), msg["body"])]
        note = ("The member addressed the agent directly with @" + self.cfg.handle + ". A direct question to "
                "the agent counts if data or the ledger could answer it; greetings, thanks and questions about "
                "what the agent can do do not count." if mention else
                "Nobody addressed the agent. Stay silent unless the message is clearly a testable question or "
                "test request.")
        prompt = fill("classify", DATA=guard.data_block(items), CONTEXT_NOTE=note)
        key = f"classify:{msg['id']}:{'m' if mention else 's'}"
        return self.ask(key, "classify", prompt, self.scratch, [],
                        lambda o: o.get("restated", "") if o.get("is_question") else "")

    def maybe_suggest(self, msg, root, replies):
        mid = msg["id"]
        if self.state.offered(mid):
            return "already_offered"
        if len(msg["body"].strip()) < 12:
            return "too_short"
        if guard.looks_like_injection(msg["body"]):
            return self.report_injection("message", mid, msg["body"])
        out = self._classify(msg, root, replies, mention=False)
        if out is None:
            return "no_output"
        if out.get("injection"):
            return self.report_injection("message(model)", mid, msg["body"])
        try:
            conf = max(0.0, min(1.0, float(out.get("confidence", 0))))
        except (TypeError, ValueError):
            conf = 0.0
        isq = out.get("is_question") is True
        restated = (out.get("restated") or "").strip()
        log("classified", message_id=mid, is_question=isq, confidence=conf, threshold=self.cfg.suggest_threshold)
        if not (isq and restated and conf >= self.cfg.suggest_threshold):
            return "silent"
        card = cards.suggest(restated, mid)
        cid = self.post(f"suggest:{mid}", msg["root_id"], card=card, visible_to=msg["author_id"],
                        meta={"message_id": mid, "author_id": msg["author_id"], "restated": restated,
                              "lang": out.get("lang") or self.lang_of(msg["body"])})
        if cid is None:
            return "blocked"
        self.state.record_offer(mid, cid)
        self.once(f"suggestion_logged:{mid}", lambda: self.client.suggestion(mid, "offered"))
        return "suggested"

    def on_mention(self, msg, root, replies):
        mid = msg["id"]
        if guard.looks_like_injection(msg["body"]):
            return self.report_injection("mention", mid, msg["body"])
        out = self._classify(msg, root, replies, mention=True)
        if out is None:
            return "no_output"
        if out.get("injection"):
            return self.report_injection("mention(model)", mid, msg["body"])
        try:
            conf = float(out.get("confidence", 0))
        except (TypeError, ValueError):
            conf = 0.0
        lang = self.lang_of(msg["body"])
        if out.get("is_question") is True and (out.get("restated") or "").strip() and conf >= self.cfg.mention_threshold:
            restated = cards.plain(out["restated"])
            if self.violations(restated):
                log("restated_blocked", level="warning", message_id=mid)
                return "blocked"

            def create():
                return self.client.create_question(mid, restated, msg["author_id"]).get("id")
            qid = self.once(f"mention_question:{mid}", create)
            self.state.save_question(qid, {"root_message_id": mid, "author_id": msg["author_id"],
                                           "author_name": msg["author_name"], "restated": restated,
                                           "lang": lang, "status": "recorded"})
            self.process_question(qid)
            return "question_created"
        # Not a question: brief answer in the thread.
        items = [(label(m), as_text(m)) for m in self._context(msg, root, replies, 3)]
        items.append((label(msg, target=True), msg["body"]))
        prompt = fill("mention_reply", DATA=guard.data_block(items), LANG_NAME=LANG_NAME[lang],
                      ADDRESS=self.addr(msg["author_name"], lang))
        r = self.ask(f"mention_reply:{mid}", "mention_reply", prompt, self.cfg.repo, READ_ONLY,
                     lambda o: o.get("text", ""))
        if r is None:
            return "no_output"
        if r.get("injection"):
            return self.report_injection("mention(model)", mid, msg["body"])
        if not (r.get("text") or "").strip():
            return "silent"
        self.post(f"mention_reply:{mid}", msg["root_id"] or mid, body=r["text"])
        return "replied"

    def on_question_thread_message(self, q, msg, root, replies):
        mid, qid = msg["id"], q["qid"]
        if guard.looks_like_injection(msg["body"]):
            return self.report_injection("question_thread", mid, msg["body"], qid)
        lang = q.get("lang") or self.lang_of(msg["body"])
        lang = self.lang_of(msg["body"]) or lang
        items = [(label(m), as_text(m)) for m in ([root] + replies) if m and m["id"] != mid][-8:]
        items.append((label(msg, target=True), msg["body"]))
        ours = json.dumps(q.get("plan") or q.get("answer") or {}, ensure_ascii=False)
        prompt = fill("thread_reply", QID=qid, STATUS=q.get("status") or "", PATH=q.get("path") or "",
                      LANG_NAME=LANG_NAME[lang], ADDRESS=self.addr(msg["author_name"], lang), OURS=ours,
                      DATA=guard.data_block(items))
        out = self.ask(f"thread_reply:{mid}", "thread_reply", prompt, self.cfg.repo, READ_ONLY,
                       lambda o: o.get("text", "") if o.get("action") == "reply" else "")
        if out is None:
            return "no_output"
        if out.get("injection"):
            return self.report_injection("question_thread(model)", mid, msg["body"], qid)
        action = out.get("action")
        if action == "revise" and q.get("plan") and q.get("status") in PLAN_STATES:
            return self.revise(qid, out.get("change_request") or msg["body"], key=f"msg{mid}", lang=lang,
                               name=msg["author_name"])
        if action in ("reply", "revise") and (out.get("text") or "").strip():
            self.post(f"thread_reply:{mid}", q["root_message_id"], body=out["text"])
            return "replied"
        return "silent"

    # =========================================================================================
    # message.forwarded
    # =========================================================================================

    def on_forward(self, p: dict, eid: int):
        fid, mid, by, note = p.get("forward_id"), p.get("message_id"), p.get("by_user_id"), p.get("note") or ""
        if mid is None:
            raise Skip("no message_id")
        msg, root, replies = self.fetch_message(mid, p.get("root_id"))
        if msg is None:
            raise Skip("forwarded message not found")
        body = msg["body"] or ""
        if guard.looks_like_injection(note) or guard.looks_like_injection(body):
            return self.report_injection("forward", mid, note + "\n" + body)
        items = []
        if note.strip():
            items.append((f"note by the forwarding member (user {by})", note))
        items.append((label(msg) + " (the forwarded message)", body or "(message hidden)"))
        prompt = fill("restate", DATA=guard.data_block(items))
        out = self.ask(f"restate:{fid or mid}", "restate", prompt, self.scratch, [],
                       lambda o: [o.get("restated", ""), o.get("reason", "")])
        if out is None:
            return "no_output"
        if out.get("injection"):
            return self.report_injection("forward(model)", mid, note + "\n" + body)
        lang = self.lang_of(note, body)
        root_id = msg["root_id"]
        if out.get("testable") is True and (out.get("restated") or "").strip():
            card = cards.confirm(out["restated"], mid)
            cid = self.post(f"confirm:{fid or mid}", root_id, card=card, visible_to=by,
                            meta={"message_id": mid, "forwarder_id": by, "author_id": msg["author_id"],
                                  "note": note, "restated": out["restated"], "lang": lang})
            return "confirm_posted" if cid else "blocked"
        reason = (out.get("reason") or "").strip()
        line = text("not_testable", lang, addr=self.addr(None, lang))
        if reason and not self.violations(reason):
            line = (self.addr(None, lang) + reason) if lang == "tr" else reason
        self.post(f"not_testable:{fid or mid}", root_id, body=line, visible_to=by)
        return "not_testable"

    # =========================================================================================
    # question.confirmed and the record/plan decision
    # =========================================================================================

    def on_confirmed(self, p: dict, eid: int):
        qid = p.get("question_id")
        if not qid:
            raise Skip("no question_id")
        self.resolve_question(qid, p)
        return self.process_question(qid)

    def resolve_question(self, qid: str, payload: dict | None = None) -> dict:
        q = self.state.question(qid) or {}
        info = {}
        for src in (payload or {}, (payload or {}).get("question") or {}):
            for k in ("root_message_id", "restated", "author_id", "forwarder_id", "note", "status", "path"):
                if src.get(k) is not None:
                    info[k] = src[k]
        if not (q.get("root_message_id") or info.get("root_message_id")):
            got = self.client.question(qid)
            got = (got or {}).get("question", got) or {}
            for k in ("root_message_id", "restated", "author_id", "forwarder_id", "note", "status", "path"):
                if got.get(k) is not None:
                    info.setdefault(k, got[k])
        if not (q.get("root_message_id") or info.get("root_message_id")):
            for m in parse_recent(self.client.recent(limit=50)):
                if m.get("question") and m["question"].get("id") == qid:
                    info["root_message_id"] = m["id"]
                    info.setdefault("author_id", m["author_id"])
                    break
        if not (q.get("root_message_id") or info.get("root_message_id")):
            raise Skip(f"cannot resolve {qid}: no root message")
        q = self.state.save_question(qid, info)
        if not q.get("lang") or not q.get("author_name"):
            root, _ = parse_thread(self.client.thread(q["root_message_id"]))
            body = (root or {}).get("body") or ""
            q = self.state.save_question(qid, {
                "lang": q.get("lang") or self.lang_of(body, q.get("note"), q.get("restated")),
                "author_name": (root or {}).get("author_name") or q.get("author_name") or "",
                "author_id": q.get("author_id") or (root or {}).get("author_id"),
                "restated": q.get("restated") or body})
        return q

    def process_question(self, qid: str, force_plan: bool = False, clarification: str | None = None,
                         round_key: str = "1"):
        q = self.state.question(qid) or self.resolve_question(qid)
        lang = q.get("lang") or "en"
        root_id = q["root_message_id"]
        addr = self.addr(q.get("author_name"), lang)
        self.post(f"ack:{qid}", root_id, body=text("ack", lang, addr=addr, qid=qid))
        if q.get("status") in (None, ""):
            q = self.state.save_question(qid, {"status": "recorded"})

        root, replies = parse_thread(self.client.thread(root_id))
        items = []
        if root:
            items.append((label(root) + " (the question as the member wrote it)", as_text(root)))
        if q.get("note"):
            items.append(("note by the forwarding member", q["note"]))
        items.append(("restated question, confirmed by the member", q.get("restated") or ""))
        for m in [r for r in replies if not is_agent(r)][-4:]:
            items.append((label(m), as_text(m)))
        if clarification:
            items.append(("the member says the earlier answer did not answer the question", clarification))
        if any(guard.looks_like_injection(t) for _, t in items):
            self.report_injection("question", root_id, " | ".join(t for _, t in items), qid)
            return "injection"
        cands = self.ledger.search(" ".join([q.get("restated") or "", (root or {}).get("body") or ""]))
        cand_txt = "\n".join("- " + self.ledger.summary_line(r) for r in cands) or "- (none found by keyword)"
        force_note = ""
        if force_plan:
            force_note = ("The member asked for a new test even though the record may cover it (or the record "
                          "did not answer it). Choose path \"test\" (or \"clarify\" if it cannot be planned). "
                          "Mention related ledger entries in intro.")
        prompt = fill("respond", QID=qid, LANG_NAME=LANG_NAME[lang], ADDRESS=addr, FORCE_NOTE=force_note,
                      CANDIDATES=cand_txt, DATA=guard.data_block(items))
        out = self.ask(f"respond:{qid}:{round_key}", "respond", prompt, self.cfg.repo, READ_ONLY,
                       _respond_public)
        if out is None:
            self.post(f"neutral:{qid}:{round_key}", root_id, card=cards.notice(text("neutral", lang)), qid=qid)
            return "no_output"
        if out.get("injection"):
            return self.report_injection("question(model)", root_id, q.get("restated"), qid)
        path = out.get("path")
        if path == "record" and not force_plan:
            res = self.post_record_answer(q, out, round_key)
            if res != "invalid":
                return res
        if path == "clarify":
            self.post(f"clarify:{qid}:{round_key}", root_id, body=out.get("text") or text("neutral", lang))
            return "clarify"
        if path == "test":
            return self.post_plan(q, out, draft_no=(q.get("draft_no") or 0) + 1, key=f"{qid}:{round_key}",
                                  intro=out.get("intro"))
        if path == "record" and not round_key.endswith(":plan"):
            # A record answer that cannot be tied to closed ledger entries (or a record answer when a
            # test was asked for): ask once more for a plan.
            return self.process_question(qid, force_plan=True, round_key=round_key + ":plan")
        log("respond_unusable", level="warning", question_id=qid, path=path)
        self.post(f"neutral:{qid}:{round_key}", root_id, card=cards.notice(text("neutral", lang)), qid=qid)
        return "unusable"

    def post_record_answer(self, q: dict, out: dict, round_key: str):
        qid, root_id = q["qid"], q["root_message_id"]
        points = []
        for pt in out.get("points") or []:
            ids = [i for i in (pt.get("ids") or []) if isinstance(i, str)]
            ok = [i for i in ids if self.ledger.is_closed(i)]
            if not ids or len(ok) != len(ids) or not (pt.get("text") or "").strip():
                log("record_point_dropped", level="warning", question_id=qid, ids=ids)
                continue
            points.append({"text": pt["text"], "refs": [self.ledger.ref(i) for i in ok]})
        if not points or not (out.get("summary") or "").strip() or not (out.get("limits") or "").strip():
            log("record_answer_invalid", level="warning", question_id=qid)
            return "invalid"
        card = cards.answer_record(out["summary"], points, out["limits"])
        cid = self.post(f"answer_record:{qid}:{round_key}", root_id, card=card, qid=qid)
        if cid is None:
            return "blocked"
        self.once(f"patch:{qid}:answered_record:{round_key}",
                  lambda: self.client.patch_question(qid, status="answered_record", path="record"))
        self.state.save_question(qid, {"status": "answered_record", "path": "record", "answer": card})
        return "answered_record"

    def post_plan(self, q: dict, out: dict, draft_no: int, key: str, intro: str | None = None, note=None):
        qid, root_id = q["qid"], q["root_message_id"]
        plan = {k: cards.plain(out.get(k)) for k in
                ("question", "data", "rule", "smallest_effect", "public_feasibility")}
        if not all(plan.values()):
            log("plan_incomplete", level="warning", question_id=qid)
            self.post(f"neutral:{key}", root_id, card=cards.notice(text("neutral", q.get("lang"))), qid=qid)
            return "plan_incomplete"
        card = cards.plan(draft_no, plan)
        if self.violations(card):
            log("plan_blocked", level="warning", question_id=qid, rules=self.violations(card))
            return "blocked"
        lead = intro or note
        if lead and lead.strip():
            self.post(f"plan_intro:{key}", root_id, body=lead)
        cid = self.post(f"plan:{key}", root_id, card=card, qid=qid, meta={"draft_no": draft_no})
        if cid is None:
            return "blocked"
        feas = out.get("feasibility") or {}
        try:
            cost = max(0.0, float(feas.get("est_cost_eur", 0) or 0))
        except (TypeError, ValueError):
            cost = 10.0  # unknown cost is treated as needing the coordinator
        public = cards.plain(feas.get("public_summary") or plan["public_feasibility"])
        if self.violations(public):
            public = plan["public_feasibility"]
        private = str(feas.get("private_detail") or "")
        self.once(f"feasibility:{key}", lambda: self.client.put_feasibility(
            qid, public, private, cost, bool(feas.get("touches_blind"))))
        self.once(f"patch:{key}:waiting", lambda: self.client.patch_question(qid, status="waiting_approval",
                                                                             path="test"))
        self.state.save_question(qid, {"status": "waiting_approval", "path": "test", "plan": plan,
                                       "draft_no": draft_no, "plan_card_id": cid,
                                       "feasibility": {"est_cost_eur": cost,
                                                       "touches_blind": bool(feas.get("touches_blind"))}})
        return f"plan_draft_{draft_no}"

    # =========================================================================================
    # card.action
    # =========================================================================================

    def on_card_action(self, p: dict, eid: int):
        cid, action, by, txt = p.get("message_id"), p.get("action"), p.get("by_user_id"), p.get("text") or ""
        card = self.state.card(cid)
        if card is None:
            log("card_unknown", level="warning", message_id=cid, action=action)
            return "unknown_card"
        ctype, qid, data = card["type"], card["qid"], card["data"]
        if ctype == "suggest":
            self.state.offer_outcome(data.get("message_id"), "accepted" if action == "yes" else "declined")
            return f"suggest_{action}"
        if ctype == "confirm":
            return f"confirm_{action}"
        if ctype == "plan" and action == "change":
            if guard.looks_like_injection(txt):
                return self.report_injection("plan_change", cid, txt, qid)
            q = self.state.question(qid) or {}
            lang = self.lang_of(txt) if txt.strip() else q.get("lang", "en")
            return self.revise(qid, txt, key=f"card{cid}:{eid}", lang=lang)
        if ctype == "answer_record" and action == "test_anyway":
            self.state.save_question(qid, {"status": "recorded", "path": "test"})
            return self.process_question(qid, force_plan=True, round_key=f"anyway:{cid}")
        if ctype == "answer_record" and action == "not_answered":
            if guard.looks_like_injection(txt):
                return self.report_injection("not_answered", cid, txt, qid)
            q = self.state.question(qid) or {}
            lang = self.lang_of(txt) if txt.strip() else q.get("lang", "en")
            self.post(f"not_answered_ack:{cid}:{eid}", q.get("root_message_id"),
                      body=text("unclear_answer", lang))
            return self.process_question(qid, clarification=txt or None, round_key=f"again:{cid}:{eid}")
        return f"{ctype}_{action}_noop"

    def revise(self, qid: str, change_text: str, key: str, lang: str | None = None, name: str | None = None):
        q = self.state.question(qid)
        if not q or not q.get("plan"):
            log("revise_without_plan", level="warning", question_id=qid)
            return "no_plan"
        if q.get("status") not in PLAN_STATES:
            log("revise_after_freeze", level="warning", question_id=qid, status=q.get("status"))
            return "frozen"
        lang = lang or q.get("lang") or "en"
        draft = q.get("draft_no") or 1
        items = [("the question, as confirmed by the member", q.get("restated") or ""),
                 ("the member's change request", change_text or "(no text given)")]
        prompt = fill("revise_plan", QID=qid, DRAFT_NO=draft, NEXT_DRAFT=draft + 1, LANG_NAME=LANG_NAME[lang],
                      ADDRESS=self.addr(name or q.get("author_name"), lang),
                      PLAN=json.dumps(q["plan"], ensure_ascii=False, indent=1), DATA=guard.data_block(items))
        out = self.ask(f"revise:{qid}:{key}", "revise_plan", prompt, self.cfg.repo, READ_ONLY, _plan_public)
        if out is None:
            return "no_output"
        if out.get("injection"):
            return self.report_injection("revise(model)", None, change_text, qid)
        return self.post_plan(q, out, draft_no=draft + 1, key=f"{qid}:rev:{key}", note=out.get("note"))

    # =========================================================================================
    # plan.approved / run.released / held / anonymised
    # =========================================================================================

    def on_plan_approved(self, p: dict, eid: int):
        qid = p.get("question_id")
        if not qid:
            raise Skip("no question_id")
        if not p.get("run_allowed"):
            self.state.save_question(qid, {"status": "approved_waiting"})
            log("run_not_allowed_yet", question_id=qid)
            return "waiting_release"
        return self.start_run(qid)

    def on_run_released(self, p: dict, eid: int):
        qid = p.get("question_id")
        if not qid:
            raise Skip("no question_id")
        self.state.save_question(qid, {"held": False})
        return self.start_run(qid)

    def on_held(self, p: dict, eid: int):
        qid = p.get("question_id")
        self.state.save_question(qid, {"held": True, "hold_reason": p.get("reason") or "", "status": "on_hold"})
        log("question_held", question_id=qid)
        return "held"

    def on_anonymised(self, p: dict, eid: int):
        qid = p.get("question_id")
        self.state.save_question(qid, {"anonymised": True})
        log("question_anonymised", question_id=qid)
        return "anonymised"

    def start_run(self, qid: str):
        if self.state.has_step(f"started:{qid}"):
            return "already_started"
        q = self.state.question(qid)
        if not q or not q.get("plan"):
            q = self.resolve_question(qid)
        if not q.get("plan"):
            log("run_without_plan", level="warning", question_id=qid)
            return "no_plan"
        if q.get("held"):
            return "held"
        if self.cfg.autorun:
            from .run_job import run_question
            return run_question(self, q)
        return self.queue_for_team(q)

    def queue_for_team(self, q: dict) -> str:
        qid, root_id, lang = q["qid"], q["root_message_id"], q.get("lang") or "en"
        plan_json = json.dumps(q["plan"], ensure_ascii=False, sort_keys=True, indent=1)
        sha = hashlib.sha256(plan_json.encode("utf-8")).hexdigest()
        self.once(f"patch:{qid}:frozen", lambda: self.client.patch_question(qid, status="frozen"))

        def write():
            d = Path(self.cfg.state_dir) / "kuyruk"
            d.mkdir(parents=True, exist_ok=True)
            req = {"question_id": qid, "root_message_id": root_id, "author_id": q.get("author_id"),
                   "forwarder_id": q.get("forwarder_id"), "restated": q.get("restated"), "lang": lang,
                   "draft_no": q.get("draft_no"), "plan": q["plan"], "plan_sha256": sha,
                   "feasibility": q.get("feasibility"), "review": "pending (project team)",
                   "requested_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
            tmp = d / f".{qid}.json.tmp"
            tmp.write_text(json.dumps(req, ensure_ascii=False, indent=1), encoding="utf-8")
            os.replace(tmp, d / f"{qid}.json")
            return str(d / f"{qid}.json")
        path = self.once(f"queue_file:{qid}", write)
        self.post(f"queued:{qid}", root_id, card=cards.notice(text("queued", lang)), qid=qid)
        self.state.save_question(qid, {"status": "frozen", "plan_sha256": sha})
        self.state.set_step(f"started:{qid}")
        log("queued_for_team", question_id=qid, file=path)
        return "queued_for_team"


# ---------------------------------------------------------------------------------------------

def _write_atomic(path: Path, data: str) -> None:
    tmp = path.with_name("." + path.name + ".tmp")
    tmp.write_text(data, encoding="utf-8")
    os.replace(tmp, path)


def _respond_public(o: dict):
    if o.get("path") == "record":
        return [o.get("summary"), [p.get("text") for p in o.get("points") or []], o.get("limits")]
    if o.get("path") == "clarify":
        return o.get("text")
    return _plan_public(o) + [o.get("intro")]


def _plan_public(o: dict):
    f = o.get("feasibility") or {}
    return [o.get(k) for k in ("question", "data", "rule", "smallest_effect", "public_feasibility", "note")] + \
        [f.get("public_summary")]


def _key(x):
    try:
        return (0, int(x))
    except (TypeError, ValueError):
        return (1, str(x))


def _lt(a, b) -> bool:
    return _key(a) < _key(b)


def main() -> int:
    cfg = Config.from_env()
    problems = cfg.check()
    for pr in problems:
        log("config_problem", level="error" if "ledger" not in pr else "warning", problem=pr)
    if any("ledger" not in pr for pr in problems):
        return 2
    Worker(cfg).run_forever()
    return 0
