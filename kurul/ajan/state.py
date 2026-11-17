"""Local worker state in one SQLite file under KURUL_STATE_DIR.

- meta: last event id
- handled: event ids already processed (with outcome)
- steps: side effects already done ("ack:Q-007", ...), so a replayed event never posts twice
- offers: messages we already offered a suggestion card for (one offer per message, ever)
- cards: card message ids we posted, with their type and question, for card.action events
- questions: per-question notes (root, author, language, current plan, draft number)
"""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS handled(event_id INTEGER PRIMARY KEY, type TEXT, outcome TEXT, at REAL);
CREATE TABLE IF NOT EXISTS steps(key TEXT PRIMARY KEY, value TEXT, at REAL);
CREATE TABLE IF NOT EXISTS offers(message_id TEXT PRIMARY KEY, card_id TEXT, outcome TEXT, at REAL);
CREATE TABLE IF NOT EXISTS cards(card_id TEXT PRIMARY KEY, type TEXT, qid TEXT, data TEXT, at REAL);
CREATE TABLE IF NOT EXISTS questions(qid TEXT PRIMARY KEY, data TEXT, at REAL);
CREATE TABLE IF NOT EXISTS own_messages(message_id TEXT PRIMARY KEY);
"""


class State:
    def __init__(self, state_dir: Path):
        self.dir = Path(state_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.path = self.dir / "ajan.sqlite3"
        self._lock = threading.Lock()
        self.db = sqlite3.connect(str(self.path), check_same_thread=False, isolation_level=None)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript(SCHEMA)

    def close(self):
        self.db.close()

    def _x(self, sql, args=()):
        with self._lock:
            return self.db.execute(sql, args).fetchall()

    # last event id -----------------------------------------------------------------------
    def last_event_id(self) -> int:
        r = self._x("SELECT value FROM meta WHERE key='last_event_id'")
        return int(r[0][0]) if r else 0

    def set_last_event_id(self, eid: int) -> None:
        if eid > self.last_event_id():
            self._x("INSERT OR REPLACE INTO meta(key,value) VALUES('last_event_id',?)", (str(eid),))

    # handled events ----------------------------------------------------------------------
    def is_handled(self, eid: int) -> bool:
        return bool(self._x("SELECT 1 FROM handled WHERE event_id=?", (eid,)))

    def mark_handled(self, eid: int, etype: str, outcome: str) -> None:
        self._x("INSERT OR REPLACE INTO handled VALUES(?,?,?,?)", (eid, etype, outcome, time.time()))

    # steps (idempotent side effects) -----------------------------------------------------
    def step(self, key: str):
        r = self._x("SELECT value FROM steps WHERE key=?", (key,))
        return json.loads(r[0][0]) if r else None

    def has_step(self, key: str) -> bool:
        return bool(self._x("SELECT 1 FROM steps WHERE key=?", (key,)))

    def set_step(self, key: str, value=True) -> None:
        self._x("INSERT OR REPLACE INTO steps VALUES(?,?,?)", (key, json.dumps(value), time.time()))

    def del_step(self, key: str) -> None:
        self._x("DELETE FROM steps WHERE key=?", (key,))

    # offers ------------------------------------------------------------------------------
    def offered(self, message_id) -> bool:
        return bool(self._x("SELECT 1 FROM offers WHERE message_id=?", (str(message_id),)))

    def record_offer(self, message_id, card_id=None, outcome="offered") -> None:
        self._x("INSERT OR REPLACE INTO offers VALUES(?,?,?,?)",
                (str(message_id), None if card_id is None else str(card_id), outcome, time.time()))

    def offer_outcome(self, message_id, outcome: str) -> None:
        self._x("UPDATE offers SET outcome=? WHERE message_id=?", (outcome, str(message_id)))

    # cards -------------------------------------------------------------------------------
    def record_card(self, card_id, ctype: str, qid: str | None, data: dict) -> None:
        self._x("INSERT OR REPLACE INTO cards VALUES(?,?,?,?,?)",
                (str(card_id), ctype, qid, json.dumps(data, ensure_ascii=False), time.time()))

    def card(self, card_id) -> dict | None:
        r = self._x("SELECT type,qid,data FROM cards WHERE card_id=?", (str(card_id),))
        if not r:
            return None
        return {"type": r[0][0], "qid": r[0][1], "data": json.loads(r[0][2])}

    # own messages ------------------------------------------------------------------------
    def record_own(self, message_id) -> None:
        self._x("INSERT OR IGNORE INTO own_messages VALUES(?)", (str(message_id),))

    def is_own(self, message_id) -> bool:
        return bool(self._x("SELECT 1 FROM own_messages WHERE message_id=?", (str(message_id),)))

    # questions ---------------------------------------------------------------------------
    def question(self, qid: str) -> dict | None:
        r = self._x("SELECT data FROM questions WHERE qid=?", (qid,))
        return json.loads(r[0][0]) if r else None

    def save_question(self, qid: str, data: dict) -> dict:
        cur = self.question(qid) or {}
        cur.update(data)
        cur["qid"] = qid
        self._x("INSERT OR REPLACE INTO questions VALUES(?,?,?)",
                (qid, json.dumps(cur, ensure_ascii=False), time.time()))
        return cur

    def question_by_root(self, root_id) -> dict | None:
        for (d,) in self._x("SELECT data FROM questions"):
            q = json.loads(d)
            if str(q.get("root_message_id")) == str(root_id):
                return q
        return None
