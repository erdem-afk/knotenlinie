"""@handles: derivation, migration, PATCH /api/me, /api/members, and mention notifications."""

import sqlite3

import pytest

from conftest import H, Env, token_from

from kurul_site import db as kdb
from kurul_site import handles


# ---------------------------------------------------------------- derivation

@pytest.mark.parametrize("name, base", [
    ("Prof. Dr. Ayşe Yılmaz", "ayseyilmaz"),
    ("Doç. Dr. Çağrı Öztürk", "cagriozturk"),
    ("İlker Şahin", "ilkersahin"),
    ("Assoc. Prof. Gülşen Ünal", "gulsenunal"),
    ("Asst. Prof. Dr. Işıl Doğan", "isildogan"),
    ("Dr. Öğr. Üyesi Hüseyin Ekşi", "huseyineksi"),
    ("Prof. Dr. Ayşe Nur Yılmaz", "ayseyilmaz"),        # given name + surname
    ("José Müller-Lüdenscheidt", "joseludenscheidt"),
    ("Søren Kierkegaard", "sorenkierkegaard"),
    ("Prof. Beta", "beta"),
    ("Knotenlinie", "knotenlinie"),
    ("Prof. Dr.", ""),
    ("Ö", ""),
    ("李四", ""),
    ("A Very Long Firstname Andaverylongsurname", "aandaverylongsurname"),
])
def test_base_handle(name, base):
    assert handles.base_handle(name) == base
    if base:
        assert handles.HANDLE_RE.match(base)


def test_fold_turkish():
    assert handles.fold("ÇĞIİÖŞÜ çğıiöşü") == "cgiiosu cgiiosu"


def test_mention_tokens():
    t = handles.mention_tokens
    assert t("hi @AyseYilmaz, and @coordinator.") == {"ayseyilmaz", "coordinator"}
    assert t("mail ayse@ayseyilmaz.org or x.@beta") == set()
    assert t("(@beta) @@beta @b @" + "x" * 25) == {"beta"}
    assert t("@beta_2\n@ünal") == {"beta_2"}


def handle_of(env, uid):
    with env.db() as db:
        return db.execute("SELECT handle FROM users WHERE id=?", (uid,)).fetchone()[0]


def test_new_users_get_unique_handles(env):
    co = env.coordinator()
    assert co.me["handle"] == "boardcoordinator"
    a = env.member("Prof. Dr. Ayşe Yılmaz", "a1@example.org")
    b = env.member("Ayşe Yılmaz", "a2@example.org")
    c = env.member("Dr. Ayse YILMAZ", "a3@example.org")
    assert (a.me["handle"], b.me["handle"], c.me["handle"]) == ("ayseyilmaz", "ayseyilmaz2", "ayseyilmaz3")
    # reserved names are never derived; a nameless (all-title) name falls back to member<id>
    adm = env.member("Admin", "adm@example.org")
    assert adm.me["handle"] == "admin2"
    t = env.member("Prof. Dr.", "t@example.org")
    assert t.me["handle"] == f"member{t.me['id']}"
    with env.db() as db:
        assert db.execute("SELECT handle FROM users WHERE role='agent'").fetchone()[0] == "knotenlinie"
    # long names: suffix keeps within 24 characters
    l1 = env.member("Abcdefghijklm Nopqrstuvwxyz", "l1@example.org")
    l2 = env.member("Abcdefghijklm Nopqrstuvwxyz", "l2@example.org")
    assert (l1.me["handle"], l2.me["handle"]) == ("abcdefghijklmnopqrstuvwx", "abcdefghijklmnopqrstuvw2")


# ---------------------------------------------------------------- migration

def schema_without_handle() -> str:
    s = kdb.SCHEMA
    a = s.index("  -- @handle for mentions")
    b = s.index("handle TEXT NULL\n", a) + len("handle TEXT NULL\n")
    s = s[:a] + s[b:]
    s = s.replace("invited_by INTEGER NULL REFERENCES users(id),\n);", "invited_by INTEGER NULL REFERENCES users(id)\n);")
    assert "handle" not in s
    return s


def test_migration_fills_handles(tmp_path):
    path = tmp_path / "k.db"
    conn = sqlite3.connect(path)
    conn.executescript(schema_without_handle())
    conn.executescript("""
      INSERT INTO users(email,name,role,public_name_ok,created_at) VALUES
        ('agent@invalid','Knotenlinie','agent',1,'2026-01-01T00:00:00Z'),
        ('coordinator@invalid','Board Coordinator','coordinator',1,'2026-01-01T00:00:00Z'),
        ('a@example.org','Prof. Dr. Ayşe Yılmaz','member',1,'2026-01-02T00:00:00Z'),
        ('b@example.org','Ayşe Yılmaz','member',NULL,'2026-01-02T00:00:00Z'),
        ('c@example.org','Doç. Dr. Çağrı Öztürk','member',0,'2026-01-02T00:00:00Z'),
        ('d@example.org','Everyone','member',0,'2026-01-02T00:00:00Z'),
        ('e@example.org','Dr.','member',0,'2026-01-02T00:00:00Z');
      INSERT INTO messages(author_id,body,kind,created_at) VALUES (3,'old message','text','2026-01-03T00:00:00Z');
    """)
    conn.commit()
    assert "handle" not in {r[1] for r in conn.execute("PRAGMA table_info(users)")}
    conn.close()

    env = Env(tmp_path)
    with env.db() as db:
        rows = [tuple(r) for r in db.execute("SELECT id, name, handle FROM users ORDER BY id")]
        assert db.execute("SELECT name FROM sqlite_master WHERE name='users_handle'").fetchone()
    assert [r[2] for r in rows] == ["knotenlinie", "boardcoordinator", "ayseyilmaz", "ayseyilmaz2",
                                    "cagriozturk", "everyone2", "member7"]
    # a second start changes nothing; a user-chosen handle survives restarts
    m = env.login(env.client(), token_from(env.board.invite({"email": "b@example.org", "name": "x"})["login_url"]))
    assert m.patch("/api/me", json={"handle": "ayse_y"}, headers=H).json()["handle"] == "ayse_y"
    env2 = Env(tmp_path)
    with env2.db() as db:
        assert [r[0] for r in db.execute("SELECT handle FROM users ORDER BY id")] == [
            "knotenlinie", "boardcoordinator", "ayseyilmaz", "ayse_y", "cagriozturk", "everyone2", "member7"]
        assert db.execute("SELECT body FROM messages").fetchone()[0] == "old message"
        # the unique index is case-insensitive
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("UPDATE users SET handle='AYSEYILMAZ' WHERE id=5")


def test_migration_from_oldest_schema(tmp_path):
    from test_invites import old_schema  # before can_invite and handle
    conn = sqlite3.connect(tmp_path / "k.db")
    conn.executescript(old_schema())
    conn.execute("INSERT INTO users(email,name,role,public_name_ok,created_at) "
                 "VALUES ('x@example.org','Prof. Ümit Kılıç','member',1,'2026-01-01T00:00:00Z')")
    conn.commit()
    conn.close()
    env = Env(tmp_path)
    with env.db() as db:
        assert db.execute("SELECT handle FROM users WHERE email='x@example.org'").fetchone()[0] == "umitkilic"
        assert db.execute("SELECT handle FROM users WHERE role='agent'").fetchone()[0] == "knotenlinie"


# ---------------------------------------------------------------- PATCH /api/me, /api/members

def test_patch_handle(env):
    a = env.member("Prof. Dr. Ayşe Yılmaz", "a@example.org")
    b = env.member("Prof. Beta", "b@example.org")
    assert a.me["handle"] == "ayseyilmaz"
    patch = lambda c, v: c.patch("/api/me", json={"handle": v}, headers=H)  # noqa: E731
    r = patch(a, " @Ayse_Y ")
    assert r.status_code == 200 and r.json()["handle"] == "ayse_y"
    assert a.get("/api/me").json()["handle"] == "ayse_y"
    for bad in ("a", "x" * 25, "ayşe", "ayse y", "ayse-y", "", 12):
        assert patch(a, bad).status_code == 400, bad
    for reserved in ("knotenlinie", "Coordinator", "agent", "admin", "everyone", "all", "here", "board"):
        r = patch(b, reserved)
        assert r.status_code == 409 and "reserved" in r.json()["detail"], reserved
    r = patch(b, "AYSE_Y")
    assert r.status_code == 409 and "taken" in r.json()["detail"]
    # a failed handle change writes nothing else either
    r = b.patch("/api/me", json={"name": "Prof. Beta Renamed", "handle": "ayse_y"}, headers=H)
    assert r.status_code == 409 and b.get("/api/me").json()["name"] == "Prof. Beta"
    # unchanged handle (any case) is fine; the old handle becomes free
    assert patch(a, "AYSE_Y").status_code == 200
    assert patch(b, "ayseyilmaz").json()["handle"] == "ayseyilmaz"
    # header still required
    assert b.patch("/api/me", json={"handle": "beta"}).status_code == 403


def test_members_has_handles_not_emails(env):
    env.coordinator()
    a = env.member("Prof. Dr. Ayşe Yılmaz", "a@example.org")
    r = a.get("/api/members")
    assert r.status_code == 200
    members = r.json()["members"]
    assert all(set(m) == {"id", "name", "handle", "role"} for m in members)
    assert "a@example.org" not in r.text and "@invalid" not in r.text
    by = {m["handle"]: m for m in members}
    assert by["ayseyilmaz"]["role"] == "member" and by["knotenlinie"]["role"] == "agent"
    assert by["boardcoordinator"]["role"] == "coordinator"
    assert env.client().get("/api/members").status_code == 401


def test_admin_users_show_handle(env):
    co = env.coordinator()
    env.member("Prof. Dr. Ayşe Yılmaz", "a@example.org")
    users = co.get("/api/admin/users").json()["users"]
    assert {u["handle"] for u in users} >= {"ayseyilmaz", "boardcoordinator", "knotenlinie"}


# ---------------------------------------------------------------- mentions

@pytest.fixture
def menv(tmp_path):
    # a real coordinator address, so coordinator notifications reach the mailer
    return Env(tmp_path, coordinator_email="coord@example.org")


def sent_to(env, before):
    return sorted(m["to"] for m in env.board.mailer.sent[before:])


def test_handle_mentions_notify(menv):
    env = menv
    co = env.coordinator()
    a = env.member("Prof. Dr. Ayşe Yılmaz", "a@example.org")
    b = env.member("Prof. Beta", "b@example.org")
    c = env.member("Gamma Delta", "c@example.org")

    n = len(env.board.mailer.sent)
    mid = env.post(b, "Hocam @AyseYilmaz, what do you think? cc @gammadelta and @nobody")
    assert sent_to(env, n) == ["a@example.org", "c@example.org"]
    assert "mentioned you" in env.board.mailer.sent[-1]["subject"]
    assert f"thread%3D{mid}" in env.board.mailer.sent[-1]["text"]

    # handle + full name in one message: one mail, not two; the author is never notified
    n = len(env.board.mailer.sent)
    env.post(b, "Prof. Beta here, asking @ayseyilmaz (Prof. Dr. Ayşe Yılmaz) and myself @beta")
    assert sent_to(env, n) == ["a@example.org"]

    # @coordinator reaches every coordinator, also from a thread reply; not the coordinator posting
    n = len(env.board.mailer.sent)
    env.post(a, "@coordinator please have a look", root_id=mid)
    assert sent_to(env, n) == ["coord@example.org"]
    n = len(env.board.mailer.sent)
    env.post(co, "@coordinator note to self, and @boardcoordinator")
    assert sent_to(env, n) == []

    # e-mail addresses and unknown handles notify nobody
    n = len(env.board.mailer.sent)
    env.post(c, "write to x@ayseyilmaz.org or beta@beta.org")
    assert sent_to(env, n) == []

    # a changed handle is the one that works
    assert a.patch("/api/me", json={"handle": "ayse"}, headers=H).status_code == 200
    n = len(env.board.mailer.sent)
    env.post(b, "@ayseyilmaz old handle")
    assert sent_to(env, n) == []
    env.post(b, "@ayse new handle")
    assert sent_to(env, n) == ["a@example.org"]


def test_knotenlinie_flag_unchanged(env):
    a = env.member("Prof. Dr. Ayşe Yılmaz", "a@example.org")
    env.member("Prof. Beta", "b@example.org")
    ids = [env.post(a, "@knotenlinie is this testable?"), env.post(a, "@beta and @coordinator only"),
           env.post(a, "Hey @KNOTENLINIE"), env.post(a, "mail knotenlinie@example.org")]
    evs = {e["payload"]["message_id"]: e["payload"] for e in env.events(types={"message.created"})}
    assert [evs[i]["mention"] for i in ids] == [True, False, True, False]
    assert set(evs[ids[0]]) == {"message_id", "root_id", "author_id", "author_role", "mention"}
