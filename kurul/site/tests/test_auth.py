import re

from conftest import A, H, Env, token_from


def test_request_does_not_reveal_and_sends_link(env):
    env.board.invite({"email": "a@example.org", "name": "Prof. A"})
    c = env.client()
    before = len(env.board.mailer.sent)
    r1 = c.post("/auth/request", json={"email": "nobody@example.org"}, headers=H)
    r2 = c.post("/auth/request", json={"email": "A@Example.org "}, headers=H)
    assert r1.status_code == r2.status_code == 200
    assert r1.json() == r2.json()
    sent = env.board.mailer.sent[before:]
    assert len(sent) == 1 and sent[0]["to"] == "a@example.org"
    link = re.search(r"http://localhost:8000/auth/verify\?token=\S+", sent[0]["text"]).group(0)
    tok = token_from(link)
    # raw token is never stored
    with env.db() as db:
        stored = [r["token_hash"] for r in db.execute("SELECT token_hash FROM login_tokens")]
    assert tok not in stored and all(len(s) == 64 for s in stored)


def test_verify_flow_single_use_and_cookie_flags(env):
    url = env.board.invite({"email": "a@example.org", "name": "Prof. A"})["login_url"]
    tok = token_from(url)
    c = env.client()
    # GET only shows a button; it does not consume the token (mail scanners)
    g = c.get(f"/auth/verify?token={tok}")
    assert g.status_code == 200 and 'name="token"' in g.text and "Prof. A" in g.text
    assert c.get("/api/me").status_code == 401
    r = c.post("/auth/verify", data={"token": tok, "next": "/?thread=5"}, follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/?thread=5"
    sc = r.headers["set-cookie"].lower()
    assert "httponly" in sc and "samesite=lax" in sc and "secure" not in sc  # localhost
    assert c.get("/api/me").json()["name"] == "Prof. A"
    # second use fails
    c2 = env.client()
    r2 = c2.post("/auth/verify", data={"token": tok}, follow_redirects=False)
    assert r2.status_code == 400
    assert c2.get("/api/me").status_code == 401
    # logout
    assert c.post("/auth/logout", headers=H).status_code == 200
    assert c.get("/api/me").status_code == 401


def test_open_redirect_blocked(env):
    url = env.board.invite({"email": "a@example.org", "name": "Prof. A"})["login_url"]
    r = env.client().post("/auth/verify", data={"token": token_from(url), "next": "//evil.example"},
                          follow_redirects=False)
    assert r.headers["location"] == "/"


def test_expired_token(env):
    url = env.board.invite({"email": "a@example.org", "name": "Prof. A"})["login_url"]
    with env.db() as db:
        db.execute("UPDATE login_tokens SET expires_at='2000-01-01T00:00:00Z'")
    r = env.client().post("/auth/verify", data={"token": token_from(url)}, follow_redirects=False)
    assert r.status_code == 400


def test_secure_cookie_on_https(tmp_path):
    e = Env(tmp_path, base_url="https://board.example.org")
    r = e.client().post("/auth/verify", data={"token": "boot-token-abc"}, follow_redirects=False)
    assert "secure" in r.headers["set-cookie"].lower()


def test_bootstrap_once(env):
    c = env.coordinator()
    assert c.me["role"] == "coordinator" and c.me["name"] == "Board Coordinator"
    r = env.client().post("/auth/verify", data={"token": "boot-token-abc"}, follow_redirects=False)
    assert r.status_code == 400
    with env.db() as db:
        roles = sorted(r["role"] for r in db.execute("SELECT role FROM users"))
        agent = db.execute("SELECT name FROM users WHERE role='agent'").fetchone()
    assert roles == ["agent", "coordinator"] and agent["name"] == "Knotenlinie"
    # restarting the app does not create another coordinator or re-arm the token
    from kurul_site.app import create_app
    app2 = create_app(env.settings)
    from fastapi.testclient import TestClient
    r = TestClient(app2).post("/auth/verify", data={"token": "boot-token-abc"}, follow_redirects=False)
    assert r.status_code == 400


def test_agent_cannot_log_in(env):
    before = len(env.board.mailer.sent)
    env.client().post("/auth/request", json={"email": "agent@invalid"}, headers=H)
    assert len(env.board.mailer.sent) == before


def test_xrw_header_required(env):
    c = env.member()
    r = c.post("/api/messages", json={"body": "hi"})
    assert r.status_code == 403
    assert c.patch("/api/me", json={"name": "X"}).status_code == 403
    assert env.client().post("/auth/request", json={"email": "a@example.org"}).status_code == 403


def test_login_rate_limits(env):
    env.board.invite({"email": "a@example.org", "name": "Prof. A"})
    c = env.client()
    before = len(env.board.mailer.sent)
    codes = [c.post("/auth/request", json={"email": "a@example.org"}, headers=H).status_code for _ in range(5)]
    assert codes == [200] * 5
    assert len(env.board.mailer.sent) - before == env.settings.login_rate_per_email  # silently capped
    codes = [c.post("/auth/request", json={"email": f"x{i}@example.org"}, headers=H).status_code
             for i in range(10)]
    assert 429 in codes  # per-IP limit


def test_me_patch_and_first_login(env):
    c = env.member()
    assert c.me["public_name_ok"] is None
    r = c.patch("/api/me", json={"name": "Prof. A B", "public_name_ok": False}, headers=H)
    assert r.json()["public_name_ok"] is False and r.json()["name"] == "Prof. A B"
    assert c.patch("/api/me", json={"name": ""}, headers=H).status_code == 400
    assert c.patch("/api/me", json={"public_name_ok": "yes"}, headers=H).status_code == 400


def test_security_headers_and_pages(env):
    c = env.client()
    r = c.get("/login")
    csp = r.headers["content-security-policy"]
    assert "default-src 'self'" in csp and "script-src 'self'" in csp
    assert r.headers["x-content-type-options"] == "nosniff"
    assert c.get("/", follow_redirects=False).status_code == 303
    m = env.member()
    assert m.get("/").status_code == 200
    assert m.get("/admin", follow_redirects=False).headers["location"] == "/"


def test_body_size_limit(env):
    c = env.member()
    r = c.post("/api/messages", content=b'{"body":"' + b"x" * 70000 + b'"}',
               headers={**H, "Content-Type": "application/json"})
    assert r.status_code == 413


def test_agent_auth(env, tmp_path):
    c = env.client()
    assert c.get("/api/agent/recent").status_code == 401
    assert c.get("/api/agent/recent", headers={"Authorization": "Bearer wrong"}).status_code == 401
    assert c.get("/api/agent/recent", headers=A).status_code == 200
    # a member session does not open the agent API
    m = env.member()
    assert m.get("/api/agent/recent").status_code == 401
    sub = tmp_path / "noagent"
    sub.mkdir()
    e2 = Env(sub, agent_token="")
    assert e2.client().get("/api/agent/recent", headers=A).status_code == 503


def test_admin_requires_coordinator(env):
    m = env.member()
    assert m.get("/api/admin/users").status_code == 403
    assert m.post("/api/admin/invites", json={"email": "b@example.org", "name": "B"}, headers=H).status_code == 403
    co = env.coordinator()
    r = co.post("/api/admin/invites", json={"email": "b@example.org", "name": "Prof. B"}, headers=H)
    assert r.status_code == 200 and r.json()["created"] is True
    b = env.login(env.client(), token_from(r.json()["login_url"]))
    assert b.get("/api/me").json()["name"] == "Prof. B"
    users = co.get("/api/admin/users").json()["users"]
    assert {u["role"] for u in users} == {"member", "coordinator", "agent"}
    assert co.post("/api/admin/invites", json={"email": "bad", "name": "X"}, headers=H).status_code == 400
