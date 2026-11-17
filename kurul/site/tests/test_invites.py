"""Delegated invitations: can_invite, invited_by, POST /api/invites, admin views, migration."""

import sqlite3

from conftest import A, H, Env, token_from

from kurul_site import db as kdb


def grant(co, uid, value=True):
    return co.patch(f"/api/admin/users/{uid}", json={"can_invite": value}, headers=H)


def inviter(env, email="inv@example.org", co=None):
    """A member with the invitation right, plus the coordinator client."""
    co = co or env.coordinator()
    m = env.member("Prof. Inviter", email)
    assert grant(co, m.me["id"]).status_code == 200
    m.me = m.get("/api/me").json()
    return m, co


def invite(c, email, name="Prof. New"):
    return c.post("/api/invites", json={"email": email, "name": name}, headers=H)


def test_me_and_admin_toggle(env):
    co = env.coordinator()
    m = env.member()
    assert m.me["can_invite"] is False
    assert co.me["can_invite"] is True
    # only the coordinator may toggle; header required; only booleans; only members
    assert m.patch(f"/api/admin/users/{m.me['id']}", json={"can_invite": True}, headers=H).status_code == 403
    assert co.patch(f"/api/admin/users/{m.me['id']}", json={"can_invite": True}).status_code == 403
    assert grant(co, m.me["id"], "yes").status_code == 400
    assert co.patch(f"/api/admin/users/{m.me['id']}", json={"can_invite": True, "role": "coordinator"},
                    headers=H).status_code == 400
    assert grant(co, co.me["id"]).status_code == 400
    assert grant(co, 9999).status_code == 404
    r = grant(co, m.me["id"])
    assert r.status_code == 200 and r.json()["can_invite"] is True and r.json()["role"] == "member"
    assert m.get("/api/me").json()["can_invite"] is True
    assert grant(co, m.me["id"], False).json()["can_invite"] is False
    assert m.get("/api/me").json()["can_invite"] is False


def test_member_without_right_gets_403(env):
    m = env.member()
    r = invite(m, "new@example.org")
    assert r.status_code == 403
    assert m.post("/api/invites", json={"email": "new@example.org", "name": "X"}).status_code == 403  # no XRW
    assert env.client().post("/api/invites", json={"email": "n@example.org", "name": "X"},
                             headers=H).status_code == 401
    with env.db() as db:
        assert db.execute("SELECT COUNT(*) FROM users WHERE email='new@example.org'").fetchone()[0] == 0
        assert db.execute("SELECT COUNT(*) FROM invites WHERE email='new@example.org'").fetchone()[0] == 0


def test_member_invite_creates_member_and_link(env):
    m, co = inviter(env)
    sent_before = len(env.board.mailer.sent)
    r = invite(m, " New@Example.org ", "Prof. New")
    assert r.status_code == 200, r.text
    j = r.json()
    assert j["created"] is True and j["emailed"] is False and "/auth/verify?token=" in j["login_url"]
    # sent through the mail path (logged without SMTP)
    sent = env.board.mailer.sent[sent_before:]
    assert len(sent) == 1 and sent[0]["to"] == "new@example.org"
    assert j["login_url"] in sent[0]["text"] and "Prof. Inviter" in sent[0]["text"]
    # the link signs the invitee in as a plain member with no invite right
    n = env.login(env.client(), token_from(j["login_url"]))
    me = n.get("/api/me").json()
    assert me["role"] == "member" and me["name"] == "Prof. New" and me["can_invite"] is False
    with env.db() as db:
        row = db.execute("SELECT * FROM users WHERE email='new@example.org'").fetchone()
        assert row["invited_by"] == m.me["id"] and row["role"] == "member" and row["can_invite"] == 0
        exp = db.execute("SELECT expires_at FROM login_tokens WHERE user_id=?", (row["id"],)).fetchone()[0]
    assert exp > kdb.in_iso(days=6)
    # invitee cannot invite
    assert invite(n, "other@example.org").status_code == 403
    # no announcement in the board feed
    assert n.get("/api/messages?root=none").json()["messages"] == []
    # admin sees who invited whom
    users = {u["email"]: u for u in co.get("/api/admin/users").json()["users"]}
    assert users["new@example.org"]["invited_by"] == {"id": m.me["id"], "name": "Prof. Inviter"}
    assert users["inv@example.org"]["can_invite"] is True
    invs = co.get("/api/admin/invites").json()["invites"]
    assert invs[0]["email"] == "new@example.org" and invs[0]["outcome"] == "created"
    assert invs[0]["invited_by"]["id"] == m.me["id"] and invs[0]["user"]["name"] == "Prof. New"
    assert m.get("/api/admin/invites").status_code == 403


def test_role_cannot_be_escalated(env):
    m, _ = inviter(env)
    r = m.post("/api/invites", json={"email": "x@example.org", "name": "X", "role": "coordinator",
                                     "can_invite": True}, headers=H)
    assert r.status_code == 200
    with env.db() as db:
        row = db.execute("SELECT role, can_invite FROM users WHERE email='x@example.org'").fetchone()
    assert tuple(row) == ("member", 0)


def test_validation(env):
    m, _ = inviter(env)
    for email, name in [("bad", "X"), ("a@b", "X"), ("a b@example.org", "X"), ("x" * 250 + "@example.org", "X"),
                        ("ok@example.org", ""), ("ok@example.org", "   "), ("ok@example.org", "N" * 81),
                        ("ok@example.org", "Line\nTwo"), (123, "X"), ("ok@example.org", ["X"])]:
        r = m.post("/api/invites", json={"email": email, "name": name}, headers=H)
        assert r.status_code == 400, (email, name)
    assert m.post("/api/invites", json=["x"], headers=H).status_code in (400, 422)
    assert invite(m, "ok@example.org", "N" * 80).status_code == 200


def test_existing_email_no_duplicate(env):
    m, co = inviter(env)
    other, _ = inviter(env, "other-inv@example.org", co)
    first = invite(m, "dup@example.org", "Prof. Dup").json()
    # another member: generic answer, no link, nothing changed
    r = invite(other, "DUP@example.org", "Someone Else")
    assert r.status_code == 200
    j = r.json()
    assert j == {"created": False, "already_invited": True,
                 "message": "This address has already been invited to the board."}
    # someone the caller did not invite (here: the other inviter): also generic
    r = invite(other, "inv@example.org")
    assert r.status_code == 200 and r.json()["already_invited"] is True
    # the original inviter gets a fresh link
    j2 = invite(m, "dup@example.org", "Changed Name").json()
    assert j2["created"] is False and j2["login_url"] != first["login_url"]
    # the coordinator too (as before), via the admin route
    j3 = co.post("/api/admin/invites", json={"email": "dup@example.org", "name": "Y"}, headers=H).json()
    assert j3["created"] is False and "login_url" in j3
    with env.db() as db:
        rows = db.execute("SELECT name, invited_by, role FROM users WHERE email='dup@example.org'").fetchall()
        outcomes = [r[0] for r in db.execute("SELECT outcome FROM invites WHERE email='dup@example.org' ORDER BY id")]
    assert len(rows) == 1 and tuple(rows[0]) == ("Prof. Dup", m.me["id"], "member")
    assert outcomes == ["created", "exists", "new_link", "new_link"]


def test_rate_limit_per_inviter(env):
    env.settings.invite_rate_per_day = 3
    m, co = inviter(env)
    other, _ = inviter(env, "other-inv@example.org", co)
    codes = [invite(m, f"r{i}@example.org").status_code for i in range(5)]
    assert codes == [200, 200, 200, 429, 429]
    # "already invited" answers count too (no free probing)
    assert invite(other, "r0@example.org").status_code == 200
    # another inviter has their own budget; the coordinator is not limited
    assert invite(other, "s1@example.org").status_code == 200
    for i in range(5):
        assert co.post("/api/invites", json={"email": f"c{i}@example.org", "name": "C"}, headers=H).status_code == 200
    # the window rolls: old invites stop counting
    with env.db() as db:
        db.execute("UPDATE invites SET created_at='2000-01-01T00:00:00Z' WHERE invited_by=?", (m.me["id"],))
    assert invite(m, "r9@example.org").status_code == 200
    # revoking the right stops further invites
    grant(co, m.me["id"], False)
    assert invite(m, "r10@example.org").status_code == 403


def test_coordinator_invite_records_invited_by(env):
    co = env.coordinator()
    r = co.post("/api/admin/invites", json={"email": "b@example.org", "name": "Prof. B"}, headers=H)
    assert r.status_code == 200
    j = r.json()
    assert set(j) == {"user_id", "created", "login_url"} and j["created"] is True
    with env.db() as db:
        assert db.execute("SELECT invited_by FROM users WHERE id=?", (j["user_id"],)).fetchone()[0] == co.me["id"]
    invs = co.get("/api/admin/invites").json()["invites"]
    assert invs[0]["invited_by"]["role"] == "coordinator"


def test_user_invited_event_coordinator_only(env):
    m, co = inviter(env)
    start = env.board.last_event_id()
    uid = invite(m, "ev@example.org").json()["user_id"]
    evs = env.events(after=start, types={"user.invited"})
    assert len(evs) == 1 and evs[0]["payload"] == {"user_id": uid, "invited_by": m.me["id"]}
    assert [e["type"] for e in env.board.visible_events(co.me, start)[0]] == ["user.invited"]
    assert env.board.visible_events(m.me, start)[0] == []
    assert m.get(f"/api/events?after={start}").json()["events"] == []
    # a fresh link for an existing address is not a new invitation event
    invite(m, "ev@example.org")
    assert len(env.events(after=start, types={"user.invited"})) == 1


def test_link_not_returned_when_smtp_configured(env):
    m, _ = inviter(env)
    env.board.mailer.smtp_url = "smtp://127.0.0.1:1"
    env.board.mailer._deliver = lambda *a: None  # never touch the network in tests
    j = invite(m, "mail@example.org").json()
    assert j["created"] is True and j["emailed"] is True and "login_url" not in j
    assert env.board.mailer.sent[-1]["to"] == "mail@example.org"


OLD_USERS = """CREATE TABLE IF NOT EXISTS users(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('member','coordinator','agent')),
  public_name_ok INTEGER NULL,
  created_at TEXT NOT NULL
);"""


def old_schema() -> str:
    """The schema as it was before delegated invitations (no can_invite / invited_by / invites)."""
    s = kdb.SCHEMA
    a = s.index("CREATE TABLE IF NOT EXISTS users(")
    b = s.index(");", a) + 2
    s = s[:a] + OLD_USERS + s[b:]
    s = s[:s.index("-- every invitation attempt")]
    assert "can_invite" not in s and "invites" not in s
    return s


def test_in_place_migration(tmp_path):
    path = tmp_path / "k.db"
    conn = sqlite3.connect(path)
    conn.executescript(old_schema())
    conn.executescript("""
      INSERT INTO users(email,name,role,public_name_ok,created_at) VALUES
        ('agent@invalid','Knotenlinie','agent',1,'2026-01-01T00:00:00Z'),
        ('coordinator@invalid','Board Coordinator','coordinator',1,'2026-01-01T00:00:00Z'),
        ('old@example.org','Prof. Old','member',0,'2026-01-02T00:00:00Z');
      INSERT INTO messages(author_id,body,kind,created_at) VALUES (3,'old message','text','2026-01-03T00:00:00Z');
      INSERT INTO meta(key,value) VALUES ('marker','kept');
    """)
    conn.commit()
    assert "can_invite" not in {r[1] for r in conn.execute("PRAGMA table_info(users)")}
    conn.close()

    env = Env(tmp_path)  # starts the app on the existing file
    with env.db() as db:
        cols = {r[1]: r for r in db.execute("PRAGMA table_info(users)")}
        assert "can_invite" in cols and "invited_by" in cols
        assert cols["can_invite"]["notnull"] == 1 and cols["can_invite"]["dflt_value"] == "0"
        assert db.execute("SELECT name FROM sqlite_master WHERE name='invites'").fetchone()
        rows = [tuple(r) for r in db.execute("SELECT id,email,name,role,public_name_ok,can_invite,invited_by "
                                             "FROM users ORDER BY id")]
        assert rows == [(1, "agent@invalid", "Knotenlinie", "agent", 1, 0, None),
                        (2, "coordinator@invalid", "Board Coordinator", "coordinator", 1, 0, None),
                        (3, "old@example.org", "Prof. Old", "member", 0, 0, None)]
        assert db.execute("SELECT body FROM messages").fetchone()[0] == "old message"
        assert db.execute("SELECT value FROM meta WHERE key='marker'").fetchone()[0] == "kept"
    # the old member still signs in and works; the coordinator can grant the right
    url = env.board.invite({"email": "old@example.org", "name": "ignored"})["login_url"]
    old = env.login(env.client(), token_from(url))
    me = old.get("/api/me").json()
    assert me["name"] == "Prof. Old" and me["can_invite"] is False
    assert old.get("/api/messages?root=none").json()["messages"][0]["body"] == "old message"
    # a second start is a no-op
    env2 = Env(tmp_path)
    with env2.db() as db:
        assert db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 3
    # agent API still fine
    assert env2.agent.get("/api/agent/recent", headers=A).status_code == 200
