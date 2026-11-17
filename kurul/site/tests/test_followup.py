"""First-login explainer, "Waiting for the team", coordinator-only mail, and clean shutdown of long-polls."""

import signal
import sqlite3
import threading
import time

from fastapi.testclient import TestClient

from conftest import A, H, Env

from kurul_site import db as kdb
from kurul_site.app import install_stop_hook


# ---------------------------------------------------------------- onboarding

def test_onboarded_flag(env):
    a = env.member()
    assert a.me["onboarded_at"] is None
    for bad in (False, "yes", 1):
        assert a.patch("/api/me", json={"onboarded": bad}, headers=H).status_code == 400
    r = a.patch("/api/me", json={"onboarded": True}, headers=H)
    assert r.status_code == 200 and r.json()["onboarded_at"]
    first = r.json()["onboarded_at"]
    time.sleep(1.1)
    # idempotent: the first time is kept
    assert a.patch("/api/me", json={"onboarded": True}, headers=H).json()["onboarded_at"] == first
    assert a.get("/api/me").json()["onboarded_at"] == first
    assert a.patch("/api/me", json={"onboarded": True}).status_code == 403  # header required


def test_onboarded_migration(tmp_path):
    s = kdb.SCHEMA
    a = s.index("  -- when the user dismissed")
    b = s.index("onboarded_at TEXT NULL\n", a) + len("onboarded_at TEXT NULL\n")
    old = s[:a] + s[b:]
    old = old.replace("handle TEXT NULL,\n);", "handle TEXT NULL\n);")
    assert "onboarded" not in old
    conn = sqlite3.connect(tmp_path / "k.db")
    conn.executescript(old)
    conn.execute("INSERT INTO users(email,name,role,public_name_ok,created_at,handle) "
                 "VALUES ('x@example.org','Prof. X','member',1,'2026-01-01T00:00:00Z','profx')")
    conn.commit()
    conn.close()
    env = Env(tmp_path)
    env.coordinator()  # still signs in
    with env.db() as db:
        cols = {r[1] for r in db.execute("PRAGMA table_info(users)")}
        assert "onboarded_at" in cols
        assert db.execute("SELECT onboarded_at, handle FROM users WHERE email='x@example.org'").fetchone()[:] == (None, "profx")
    Env(tmp_path)  # second start is a no-op


# ---------------------------------------------------------------- waiting for the team

def approved_question(env, a, cost=0.0, blind=False):
    qid, root = env.question_via_suggest(a)
    env.feas(qid, cost=cost, blind=blind)
    plan = env.plan(root)
    r = env.act(a, plan, "approve")
    assert r.status_code == 200, r.text
    return qid, r.json()


def test_waiting_for_team(env):
    co = env.coordinator()
    a = env.member()
    assert co.get("/api/admin/waiting").json() == {"count": 0, "question_ids": []}
    assert a.get("/api/admin/waiting").status_code == 403
    # auto decision: approval freezes it -> waiting for the team (the worker queues it for the project team)
    q1, res = approved_question(env, a)
    assert res["status"] == "frozen"
    # needs_coordinator before approval: waiting too; after approval it is on hold
    q2, root2 = env.question_via_suggest(a, "Second question about aftershock decay?")
    env.feas(q2, cost=50.0)
    # a question still in plain discussion is not waiting
    env.question_via_suggest(a, "Third question, still being discussed?")
    w = co.get("/api/admin/waiting").json()
    assert w == {"count": 2, "question_ids": [q1, q2]}
    reports = {r["question_id"]: r for r in co.get("/api/admin/feasibility").json()["reports"]}
    assert reports[q1]["waiting_for_team"] and reports[q2]["waiting_for_team"]
    assert not reports["Q-003"]["waiting_for_team"]
    assert reports[q2]["private_detail"] == "secret detail" and reports[q2]["est_cost_eur"] == 50.0
    assert reports[q1]["updated_at"]
    # finished questions leave the list
    env.agent.patch(f"/api/agent/questions/{q1}", json={"status": "answered"}, headers=A)
    assert co.get("/api/admin/waiting").json()["question_ids"] == [q2]


# ---------------------------------------------------------------- coordinator-only mail

def test_coordinator_mail_silent_without_smtp(tmp_path):
    env = Env(tmp_path, coordinator_email="coord@example.org")
    a = env.member()
    n = len(env.board.mailer.sent)
    approved_question(env, a, cost=50.0)
    assert [m for m in env.board.mailer.sent[n:]] == []  # no feasibility, no plan_approved, nothing logged
    with env.db() as db:  # and no sign-in links minted for mails that are not sent
        coord = db.execute("SELECT id FROM users WHERE role='coordinator'").fetchone()[0]
        assert db.execute("SELECT COUNT(*) FROM login_tokens WHERE user_id=?", (coord,)).fetchone()[0] == 1


def test_coordinator_mail_with_smtp(tmp_path):
    env = Env(tmp_path, coordinator_email="coord@example.org", smtp_url="smtp://127.0.0.1:1")
    env.board.mailer._deliver = lambda *a: None  # never touch the network in tests
    a = env.member()
    n = len(env.board.mailer.sent)
    qid, res = approved_question(env, a, cost=50.0)
    sent = env.board.mailer.sent[n:]
    assert {m["to"] for m in sent} == {"coord@example.org"}  # never a member
    subjects = [m["subject"] for m in sent]
    assert any(s.startswith(f"Feasibility report {qid}: needs your decision") for s in subjects)
    assert f"Plan approved: {qid} is waiting for your approval to run" in subjects
    approved = next(m for m in sent if m["subject"].startswith("Plan approved"))
    assert "Prof. A approved the test plan" in approved["text"] and "/auth/verify?token=" in approved["text"]
    assert "a@example.org" not in approved["text"]
    # an auto-run plan says frozen
    n = len(env.board.mailer.sent)
    q2, res = approved_question(env, a)
    assert res["status"] == "frozen"
    assert f"Plan approved: {q2} is frozen and ready to run" in [m["subject"] for m in env.board.mailer.sent[n:]]


def test_notify_never_sends_coordinator_kinds_to_members():
    from kurul_site.mail import Mailer, notify
    m = Mailer("smtp://127.0.0.1:1", "x <x@invalid>")
    m._deliver = lambda *a: None
    notify(m, {"id": 5, "email": "m@example.org", "role": "member"}, "plan_approved", "s", "l", "u")
    notify(m, {"id": 5, "email": "m@example.org", "role": "member"}, "feasibility", "s", "l", "u")
    assert m.sent == []
    notify(m, {"id": 1, "email": "c@example.org", "role": "coordinator"}, "plan_approved", "s", "l", "u")
    assert [x["to"] for x in m.sent] == ["c@example.org"]


# ---------------------------------------------------------------- shutdown

def test_long_poll_ends_cleanly_when_stopping(env):
    """A long-poll open while the server stops must get a normal empty answer quickly.

    Before the fix, uvicorn cancelled it after --timeout-graceful-shutdown and answered HTTP 500.
    """
    with TestClient(env.app) as c:  # runs the lifespan, so the bus is attached
        head = c.get("/api/agent/events?after=0&wait=0", headers=A).json()["last"]
        out = {}

        def poll():
            t = time.monotonic()
            r = c.get(f"/api/agent/events?after={head}&wait=20", headers=A)
            out.update(status=r.status_code, body=r.json(), took=time.monotonic() - t)

        th = threading.Thread(target=poll)
        th.start()
        time.sleep(0.5)
        env.board.bus.close()
        th.join(10)
        assert out["status"] == 200 and out["body"]["events"] == [] and out["took"] < 4, out


def test_stop_hook_chains_to_previous_handler():
    calls = []
    old = signal.signal(signal.SIGTERM, lambda s, f: calls.append("server"))
    try:
        restore = install_stop_hook(lambda: calls.append("hook"))
        signal.raise_signal(signal.SIGTERM)
        assert calls == ["hook", "server"]
        restore()
        signal.raise_signal(signal.SIGTERM)
        assert calls == ["hook", "server", "server"]
    finally:
        signal.signal(signal.SIGTERM, old)
