"""SQLite storage: schema, connections and write transactions.

One connection per unit of work. Writes run inside BEGIN IMMEDIATE, so the
queue rule and other read-modify-write steps are serialised across threads.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

from . import handles

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS users(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('member','coordinator','agent')),
  public_name_ok INTEGER NULL,
  created_at TEXT NOT NULL,
  -- delegated invitation right (members only; the coordinator can always invite)
  can_invite INTEGER NOT NULL DEFAULT 0,
  invited_by INTEGER NULL REFERENCES users(id),
  -- @handle for mentions: lower-case [a-z0-9_]{2,24}; unique index created in init_db
  handle TEXT NULL,
  -- when the user dismissed the first-login "How this works" explainer; NULL = not seen yet
  onboarded_at TEXT NULL
);

CREATE TABLE IF NOT EXISTS login_tokens(
  token_hash TEXT PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  expires_at TEXT NOT NULL,
  used_at TEXT NULL
);

CREATE TABLE IF NOT EXISTS sessions(
  token_hash TEXT PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  expires_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS messages(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  root_id INTEGER NULL REFERENCES messages(id),
  author_id INTEGER NOT NULL REFERENCES users(id),
  body TEXT NOT NULL DEFAULT '',
  kind TEXT NOT NULL CHECK (kind IN ('text','card')),
  card_json TEXT NULL,
  visible_to INTEGER NULL REFERENCES users(id),
  created_at TEXT NOT NULL,
  hidden_at TEXT NULL,
  -- site-owned card state (choice taken, by whom); never written by the agent
  card_state_json TEXT NULL,
  -- set on a top-level copy of a thread reply that became a question root
  moved_from INTEGER NULL REFERENCES messages(id)
);
CREATE INDEX IF NOT EXISTS messages_root ON messages(root_id, id);

CREATE TABLE IF NOT EXISTS forwards(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  message_id INTEGER NOT NULL REFERENCES messages(id),
  by_user_id INTEGER NOT NULL REFERENCES users(id),
  note TEXT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS questions(
  id TEXT PRIMARY KEY,
  root_message_id INTEGER NOT NULL REFERENCES messages(id),
  author_id INTEGER NOT NULL REFERENCES users(id),
  forwarder_id INTEGER NULL REFERENCES users(id),
  note TEXT NULL,
  restated TEXT NOT NULL,
  status TEXT NOT NULL,
  path TEXT NULL,
  queue_pos INTEGER NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  -- site bookkeeping
  plan_approved_at TEXT NULL,
  hold_reason TEXT NULL,
  anonymised INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS questions_root ON questions(root_message_id);

CREATE TABLE IF NOT EXISTS feasibility(
  question_id TEXT PRIMARY KEY REFERENCES questions(id),
  public_summary TEXT NOT NULL DEFAULT '',
  private_detail TEXT NOT NULL DEFAULT '',
  est_cost_eur REAL NULL,
  touches_blind INTEGER NOT NULL DEFAULT 0,
  decision TEXT NOT NULL,
  decided_at TEXT NULL
);

CREATE TABLE IF NOT EXISTS events(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  type TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS idempotency(
  key TEXT PRIMARY KEY,
  message_id INTEGER NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS suggestion_log(
  message_id INTEGER NOT NULL,
  outcome TEXT NOT NULL CHECK (outcome IN ('offered','accepted','declined')),
  source TEXT NOT NULL DEFAULT 'suggest',
  created_at TEXT NOT NULL,
  PRIMARY KEY (message_id, source)
);

-- every invitation attempt that passed validation (audit trail and per-inviter rate limit)
CREATE TABLE IF NOT EXISTS invites(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NULL REFERENCES users(id),
  invited_by INTEGER NULL REFERENCES users(id),
  email TEXT NOT NULL,
  outcome TEXT NOT NULL CHECK (outcome IN ('created','new_link','exists')),
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS invites_by ON invites(invited_by, created_at);
"""


def now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def now_iso() -> str:
    return iso(now())


def in_iso(**delta: float) -> str:
    return iso(now() + timedelta(**delta))


def connect(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path, timeout=10, isolation_level=None, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=10000")
    return conn


def init_db(path: str) -> None:
    conn = connect(path)
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.executescript(SCHEMA)
        cols = {r[1] for r in conn.execute("PRAGMA table_info(messages)")}
        if "moved_from" not in cols:  # databases created before this column existed
            conn.execute("ALTER TABLE messages ADD COLUMN moved_from INTEGER NULL REFERENCES messages(id)")
        cols = {r[1] for r in conn.execute("PRAGMA table_info(users)")}
        if "can_invite" not in cols:  # databases created before delegated invitations
            conn.execute("ALTER TABLE users ADD COLUMN can_invite INTEGER NOT NULL DEFAULT 0")
        if "invited_by" not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN invited_by INTEGER NULL REFERENCES users(id)")
        if "handle" not in cols:  # databases created before @handles
            conn.execute("ALTER TABLE users ADD COLUMN handle TEXT NULL")
        if "onboarded_at" not in cols:  # databases created before the first-login explainer
            conn.execute("ALTER TABLE users ADD COLUMN onboarded_at TEXT NULL")
        migrate_handles(conn)
    finally:
        conn.close()


def migrate_handles(conn: sqlite3.Connection) -> None:
    """Give every user without a handle its derived one (oldest first), then enforce uniqueness.

    Idempotent: only NULL handles are filled, and the index is created IF NOT EXISTS.
    """
    conn.execute("BEGIN IMMEDIATE")
    try:
        for r in conn.execute("SELECT id, name, role FROM users WHERE handle IS NULL ORDER BY id").fetchall():
            handles.assign(conn, r["id"], r["name"], r["role"])
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS users_handle ON users(handle COLLATE NOCASE)")
        conn.execute("COMMIT")
    except BaseException:
        conn.execute("ROLLBACK")
        raise


class Tx:
    """A write transaction. Collects events and after-commit callbacks."""

    def __init__(self, store: "Store"):
        self.store = store
        self.conn = connect(store.path)
        self.emitted = False
        self._after: list[Callable[[], None]] = []

    def __enter__(self) -> "Tx":
        self.conn.execute("BEGIN IMMEDIATE")
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        try:
            if exc_type is None:
                self.conn.execute("COMMIT")
            else:
                self.conn.execute("ROLLBACK")
        finally:
            self.conn.close()
        if exc_type is None:
            if self.emitted:
                self.store.on_event()
            for fn in self._after:
                try:
                    fn()
                except Exception:  # never fail a committed request on a side effect
                    import logging
                    logging.getLogger("kurul").exception("after-commit callback failed")

    def execute(self, sql: str, params: tuple | list = ()) -> sqlite3.Cursor:
        return self.conn.execute(sql, params)

    def one(self, sql: str, params: tuple | list = ()) -> sqlite3.Row | None:
        return self.conn.execute(sql, params).fetchone()

    def all(self, sql: str, params: tuple | list = ()) -> list[sqlite3.Row]:
        return self.conn.execute(sql, params).fetchall()

    def emit(self, type_: str, payload: dict[str, Any]) -> int:
        cur = self.conn.execute(
            "INSERT INTO events(type, payload_json, created_at) VALUES (?,?,?)",
            (type_, json.dumps(payload, ensure_ascii=False), now_iso()),
        )
        self.emitted = True
        return int(cur.lastrowid)

    def after_commit(self, fn: Callable[[], None]) -> None:
        self._after.append(fn)


class Read:
    """A read-only unit of work (autocommit; WAL gives a consistent snapshot per statement)."""

    def __init__(self, store: "Store"):
        self.conn = connect(store.path)

    def __enter__(self) -> "Read":
        return self

    def __exit__(self, *a) -> None:
        self.conn.close()

    def execute(self, sql: str, params: tuple | list = ()) -> sqlite3.Cursor:
        return self.conn.execute(sql, params)

    def one(self, sql: str, params: tuple | list = ()) -> sqlite3.Row | None:
        return self.conn.execute(sql, params).fetchone()

    def all(self, sql: str, params: tuple | list = ()) -> list[sqlite3.Row]:
        return self.conn.execute(sql, params).fetchall()


class Store:
    def __init__(self, path: str, on_event: Callable[[], None] = lambda: None):
        self.path = path
        self.on_event = on_event
        init_db(path)

    def tx(self) -> Tx:
        return Tx(self)

    def read(self) -> Read:
        return Read(self)
