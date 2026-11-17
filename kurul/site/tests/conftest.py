import sys
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from kurul_site.app import create_app  # noqa: E402
from kurul_site.config import Settings  # noqa: E402

AGENT_TOKEN = "test-agent-token-0123456789"
H = {"X-Requested-With": "kurul"}
A = {"Authorization": f"Bearer {AGENT_TOKEN}"}


def token_from(url: str) -> str:
    return parse_qs(urlsplit(url).query)["token"][0]


class Env:
    def __init__(self, tmp_path, **overrides):
        kw = dict(db_path=str(tmp_path / "k.db"), base_url="http://localhost:8000", agent_token=AGENT_TOKEN,
                  session_secret="test-secret", bootstrap_token="boot-token-abc")
        kw.update(overrides)
        self.settings = Settings(**kw)
        self.app = create_app(self.settings)
        self.board = self.app.state.board
        self.agent = TestClient(self.app)

    def client(self) -> TestClient:
        return TestClient(self.app)

    def login(self, client: TestClient, token: str) -> TestClient:
        r = client.post("/auth/verify", data={"token": token, "next": "/"}, follow_redirects=False)
        assert r.status_code == 303, r.text
        return client

    def member(self, name="Prof. A", email="a@example.org") -> TestClient:
        url = self.board.invite({"email": email, "name": name})["login_url"]
        c = self.login(self.client(), token_from(url))
        c.me = c.get("/api/me").json()
        return c

    def coordinator(self) -> TestClient:
        c = self.login(self.client(), "boot-token-abc")
        c.me = c.get("/api/me").json()
        return c

    def post(self, c, body, root_id=None):
        r = c.post("/api/messages", json={"body": body, "root_id": root_id}, headers=H)
        assert r.status_code == 200, r.text
        return r.json()["id"]

    def agent_post(self, **data):
        r = self.agent.post("/api/agent/messages", json=data, headers=A)
        assert r.status_code == 200, r.text
        return r.json()["id"]

    def act(self, c, mid, action, text=None):
        return c.post(f"/api/cards/{mid}/action", json={"action": action, "text": text}, headers=H)

    def events(self, after=0, types=None):
        r = self.agent.get(f"/api/agent/events?after={after}&wait=0", headers=A)
        assert r.status_code == 200
        evs = r.json()["events"]
        return [e for e in evs if types is None or e["type"] in types]

    def db(self):
        import sqlite3
        conn = sqlite3.connect(self.settings.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def question_via_suggest(self, c, body="Do strike-slip mainshocks produce fewer aftershocks?"):
        mid = self.post(c, body)
        card = self.agent_post(root_id=mid, card={"type": "suggest", "restated": body})
        r = self.act(c, card, "yes")
        assert r.status_code == 200, r.text
        return r.json()["question_id"], r.json()["root_message_id"]

    def plan(self, root, draft=1):
        return self.agent_post(root_id=root, card={"type": "plan", "draft_no": draft, "question": "Q?",
                                                   "data": "open catalogue", "rule": "fixed",
                                                   "smallest_effect": "x", "public_feasibility": "data found"})

    def feas(self, qid, cost=0.0, blind=False):
        r = self.agent.put(f"/api/agent/feasibility/{qid}", headers=A,
                           json={"public_summary": "Open data found; about a week.",
                                 "private_detail": "secret detail", "est_cost_eur": cost, "touches_blind": blind})
        assert r.status_code == 200, r.text
        return r.json()["decision"]


@pytest.fixture
def env(tmp_path):
    return Env(tmp_path)
