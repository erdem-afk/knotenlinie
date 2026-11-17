import json
import threading
import time

from fastapi.testclient import TestClient

from conftest import A, H


def feed(c):
    return c.get("/api/messages?root=none").json()["messages"]


def test_post_mention_and_limits(env):
    a = env.member()
    mid = env.post(a, "Hello @KnotenLinie, a question")
    env.post(a, "plain hello")
    evs = env.events(types={"message.created"})
    assert evs[0]["payload"] == {"message_id": mid, "root_id": None, "author_id": a.me["id"],
                                 "author_role": "member", "mention": True}
    assert evs[1]["payload"]["mention"] is False
    assert a.post("/api/messages", json={"body": "x" * 4001}, headers=H).status_code == 400
    assert a.post("/api/messages", json={"body": "   "}, headers=H).status_code == 400
    # replies go to a top-level root only
    rid = env.post(a, "reply", root_id=mid)
    assert a.post("/api/messages", json={"body": "nested", "root_id": rid}, headers=H).status_code == 400
    top = feed(a)
    assert [m["id"] for m in top] == [mid, mid + 1] and top[0]["reply_count"] == 1
    th = a.get(f"/api/messages?root={mid}").json()
    assert th["root"]["id"] == mid and [m["id"] for m in th["messages"]] == [rid]


def test_message_rate_limit(env):
    env.settings.message_rate_per_min = 5
    a = env.member()
    codes = [a.post("/api/messages", json={"body": f"m{i}"}, headers=H).status_code for i in range(7)]
    assert codes[:5] == [200] * 5 and codes[5:] == [429, 429]


def test_private_card_visibility(env):
    a = env.member()
    b = env.member("Prof. B", "b@example.org")
    co = env.coordinator()
    mid = env.post(a, "Is X larger than Y?")
    card = env.agent_post(root_id=mid, card={"type": "suggest", "restated": "Is X > Y?"})
    fa = feed(a)[0]
    assert fa["private_replies"][0]["id"] == card
    assert fa["private_replies"][0]["visible_to"] == a.me["id"]
    assert fa["private_replies"][0]["can_act"] == ["yes", "no"]
    assert fa["reply_count"] == 0
    for other in (b, co):
        f = feed(other)[0]
        assert "private_replies" not in f
        assert other.get(f"/api/messages?root={mid}").json()["messages"] == []
        assert env.act(other, card, "yes").status_code == 404
    # live events: B does not learn about the private card
    ev_b, _ = env.board.visible_events(b.me, 0)
    ev_a, _ = env.board.visible_events(a.me, 0)
    assert card not in [e.get("message_id") for e in ev_b]
    assert card in [e.get("message_id") for e in ev_a]
    # the agent sees it
    th = env.agent.get(f"/api/agent/thread/{mid}", headers=A).json()
    assert th["replies"][0]["card"]["type"] == "suggest"


def test_suggest_rules(env):
    a = env.member()
    b = env.member("Prof. B", "b@example.org")
    mid = env.post(a, "Is X larger than Y?")
    # suggest card may only be shown to the author
    r = env.agent.post("/api/agent/messages", headers=A,
                       json={"root_id": mid, "card": {"type": "suggest", "restated": "?"}, "visible_to": b.me["id"]})
    assert r.status_code == 400
    card = env.agent_post(root_id=mid, card={"type": "suggest", "restated": "Is X > Y?"})
    # never offered twice
    r = env.agent.post("/api/agent/messages", headers=A, json={"root_id": mid, "card": {"type": "suggest", "restated": "?"}})
    assert r.status_code == 409
    assert env.act(a, card, "no").status_code == 200
    assert env.act(a, card, "yes").status_code == 409
    with env.db() as db:
        row = db.execute("SELECT outcome FROM suggestion_log WHERE message_id=?", (mid,)).fetchone()
    assert row["outcome"] == "declined"
    r = env.agent.post("/api/agent/suggestions", headers=A, json={"message_id": mid, "outcome": "offered"})
    assert r.status_code == 409
    co = env.coordinator()
    s = co.get("/api/admin/suggestions").json()
    assert s["suggest"]["declined"] == 1 and s["suggest"]["accepted"] == 0


def test_suggest_yes_creates_question(env):
    a = env.member()
    qid, root = env.question_via_suggest(a)
    assert qid == "Q-001"
    evs = env.events(types={"question.confirmed", "card.action"})
    assert [e["type"] for e in evs] == ["question.confirmed", "card.action"]
    assert evs[0]["payload"]["question_id"] == "Q-001"
    top = feed(a)[0]
    assert top["id"] == root and top["question"]["status"] == "recorded"
    qs = a.get("/api/questions").json()["questions"]
    assert qs[0]["id"] == "Q-001" and qs[0]["author"] == "Prof. A"


def test_hide_wipes_text(env):
    a = env.member()
    b = env.member("Prof. B", "b@example.org")
    mid = env.post(a, "secret words")
    assert b.post(f"/api/messages/{mid}/hide", headers=H).status_code == 403
    assert a.post(f"/api/messages/{mid}/hide", headers=H).status_code == 200
    with env.db() as db:
        row = db.execute("SELECT body, hidden_at FROM messages WHERE id=?", (mid,)).fetchone()
    assert row["body"] == "" and row["hidden_at"]
    for c in (a, b, env.coordinator()):
        m = feed(c)[0]
        assert m["hidden"] is True and "body" not in m and m["author"]["name"] == "Prof. A"
    th = env.agent.get(f"/api/agent/thread/{mid}", headers=A).json()
    assert th["root"]["hidden"] is True and th["root"]["body"] is None
    rec = env.agent.get("/api/agent/recent", headers=A).json()["messages"]
    assert "secret" not in json.dumps(rec)
    assert b.post(f"/api/messages/{mid}/forward", json={}, headers=H).status_code == 400


def test_hide_ledger_question_anonymises(env):
    a = env.member()
    qid, root = env.question_via_suggest(a)
    env.agent.patch(f"/api/agent/questions/{qid}", json={"status": "in_ledger", "path": "record"}, headers=A)
    a.post(f"/api/messages/{root}/hide", headers=H)
    evs = env.events(types={"question.anonymised"})
    assert evs[0]["payload"] == {"question_id": qid}
    q = a.get("/api/questions").json()["questions"][0]
    assert q["status"] == "in_ledger" and q["author"] == "Board member"
    aq = env.agent.get(f"/api/agent/questions/{qid}", headers=A).json()
    assert aq["anonymised"] is True and aq["author"]["public_name"] == "Board member"


def test_hide_voids_open_suggestion(env):
    a = env.member()
    mid = env.post(a, "Is X larger than Y?")
    card = env.agent_post(root_id=mid, card={"type": "suggest", "restated": "Is X > Y?"})
    a.post(f"/api/messages/{mid}/hide", headers=H)
    assert env.act(a, card, "yes").status_code == 409


def test_forward_and_confirm(env):
    a = env.member()
    b = env.member("Prof. B", "b@example.org")
    mid = env.post(a, "The 1999 sequence would be the place to look.")
    r = b.post(f"/api/messages/{mid}/forward", json={"note": "Did the b-value drop before 1999?"}, headers=H)
    assert r.status_code == 200
    ev = env.events(types={"message.forwarded"})[0]["payload"]
    assert ev["message_id"] == mid and ev["by_user_id"] == b.me["id"] and ev["note"].startswith("Did")
    # empty note allowed
    assert a.post(f"/api/messages/{mid}/forward", json={}, headers=H).status_code == 200
    assert env.events(types={"message.forwarded"})[1]["payload"]["note"] is None
    # forwarded event goes only to the forwarder
    assert not [e for e in env.board.visible_events(a.me, 0)[0] if e["type"] == "message.forwarded"
                and e.get("message_id") == mid and e["id"] == env.events(types={"message.forwarded"})[0]["id"]]
    card = env.agent_post(root_id=mid, card={"type": "confirm", "restated": "Did b drop?", "quoted_message_id": mid},
                          visible_to=b.me["id"])
    assert env.act(a, card, "yes").status_code == 404  # private to B
    r = env.act(b, card, "yes")
    assert r.status_code == 200
    qid = r.json()["question_id"]
    q = env.agent.get(f"/api/agent/questions/{qid}", headers=A).json()
    assert q["author_id"] == a.me["id"] and q["forwarder_id"] == b.me["id"]
    assert q["note"] == "Did the b-value drop before 1999?"
    # confirm without visible_to defaults to the latest forwarder
    mid2 = env.post(a, "another")
    b.post(f"/api/messages/{mid2}/forward", json={}, headers=H)
    c2 = env.agent_post(root_id=mid2, card={"type": "confirm", "restated": "?", "quoted_message_id": mid2})
    with env.db() as db:
        assert db.execute("SELECT visible_to FROM messages WHERE id=?", (c2,)).fetchone()[0] == b.me["id"]


def test_question_for_reply_gets_own_root(env):
    a = env.member()
    b = env.member("Prof. B", "b@example.org")
    top = env.post(b, "chat")
    reply = env.post(a, "Is X larger than Y?", root_id=top)
    # worker style: root_id = the quoted message's root, card carries quoted_message_id
    card = env.agent_post(root_id=top, card={"type": "suggest", "restated": "Is X > Y?", "quoted_message_id": reply})
    r = env.act(a, card, "yes").json()
    assert r["root_message_id"] not in (top, reply)
    root = feed(a)[-1]
    assert root["id"] == r["root_message_id"] and root["body"] == "Is X larger than Y?"
    assert root["author"]["name"] == "Prof. A" and root["moved_from"] == reply
    assert root["question"]["id"] == r["question_id"]
    created = [e for e in env.events(types={"message.created"}) if e["payload"]["message_id"] == root["id"]][0]
    assert created["payload"]["moved_from"] == reply and created["payload"]["mention"] is False
    conf = env.events(types={"question.confirmed"})[-1]["payload"]
    assert conf == {"question_id": r["question_id"], "root_message_id": root["id"], "restated": "Is X > Y?",
                    "author_id": a.me["id"], "forwarder_id": None, "note": None}
    # the same reply cannot become a second question
    b.post(f"/api/messages/{reply}/forward", json={}, headers=H)
    c2 = env.agent_post(root_id=top, card={"type": "confirm", "restated": "?", "quoted_message_id": reply},
                        visible_to=b.me["id"])
    assert env.act(b, c2, "yes").json()["question_id"] == r["question_id"]


def test_suggest_top_level_with_null_root(env):
    a = env.member()
    mid = env.post(a, "Is X larger than Y?")
    card = env.agent_post(root_id=None, card={"type": "suggest", "restated": "Is X > Y?", "quoted_message_id": mid})
    f = feed(a)
    assert len(f) == 1 and f[0]["private_replies"][0]["id"] == card
    r = env.act(a, card, "yes").json()
    assert r["root_message_id"] == mid
    # no suggestion on a message that already is a question
    mid2 = env.post(a, "other")
    env.agent.post("/api/agent/questions", headers=A, json={"root_message_id": mid2, "restated": "o",
                                                             "author_id": a.me["id"]})
    rr = env.agent.post("/api/agent/messages", headers=A,
                        json={"card": {"type": "suggest", "restated": "o", "quoted_message_id": mid2}})
    assert rr.status_code == 409


def test_agent_contract_shapes(env):
    a = env.member()
    b = env.member("Prof. B", "b@example.org")
    a.patch("/api/me", json={"public_name_ok": False}, headers=H)
    mid = env.post(a, "@knotenlinie question?")
    rep = env.post(b, "a reply", root_id=mid)
    r = env.agent.post("/api/agent/questions", headers=A,
                       json={"root_message_id": mid, "restated": "Q?", "author_id": a.me["id"]}).json()
    conf = env.events(types={"question.confirmed"})[-1]["payload"]
    assert conf["question_id"] == r["id"] and conf["restated"] == "Q?" and conf["author_id"] == a.me["id"]
    env.feas(r["id"], 3)
    q = env.agent.get(f"/api/agent/questions/{r['id']}", headers=A).json()
    assert q["author_public_name_ok"] is False and q["public_summary"].startswith("Open data")
    assert q["status"] == "recorded" and q["feasibility_decision"] == "auto"
    # thread resolves a reply id; shapes
    th = env.agent.get(f"/api/agent/thread/{rep}", headers=A).json()
    root = th["root"]
    assert root["id"] == mid and root["hidden"] is False and root["body"].startswith("@knotenlinie")
    assert root["author"] == {"id": a.me["id"], "name": "Prof. A", "role": "member", "public_name_ok": False,
                              "public_name": "Board member"}
    assert root["question"] == {"id": r["id"], "status": "recorded", "path": None}
    assert th["replies"][0]["kind"] == "text" and th["replies"][0]["card"] is None and th["replies"][0]["visible_to"] is None
    assert th["author_public_name_ok"] is False
    rec = env.agent.get("/api/agent/recent", headers=A).json()["messages"]
    assert rec[0]["id"] == mid and rec[0]["question"]["id"] == r["id"]
    # forwarded payload has root_id
    b.post(f"/api/messages/{rep}/forward", json={"note": "n"}, headers=A | H)
    fw = env.events(types={"message.forwarded"})[-1]["payload"]
    assert fw["root_id"] == mid and fw["message_id"] == rep
    # agent messages emit message.created with author_role
    env.agent_post(root_id=mid, body="ok")
    assert env.events(types={"message.created"})[-1]["payload"]["author_role"] == "agent"


def test_idempotency_and_private_text(env):
    a = env.member()
    mid = env.post(a, "x")
    hdr = {**A, "Idempotency-Key": "job-17-reply"}
    r1 = env.agent.post("/api/agent/messages", headers=hdr, json={"root_id": mid, "body": "one line",
                                                                  "visible_to": a.me["id"]})
    r2 = env.agent.post("/api/agent/messages", headers=hdr, json={"root_id": mid, "body": "one line",
                                                                  "visible_to": a.me["id"]})
    assert r1.json()["id"] == r2.json()["id"]
    with env.db() as db:
        assert db.execute("SELECT COUNT(*) FROM messages WHERE root_id=?", (mid,)).fetchone()[0] == 1
    assert feed(a)[0]["private_replies"][0]["body"] == "one line"


def test_plan_card_actions_and_authorization(env):
    a = env.member()
    b = env.member("Prof. B", "b@example.org")
    co = env.coordinator()
    qid, root = env.question_via_suggest(a)
    p1 = env.plan(root, 1)
    assert env.act(b, p1, "approve").status_code == 403
    assert env.act(co, p1, "approve").status_code == 403
    assert env.act(a, p1, "change").status_code == 400  # needs text
    assert env.act(a, p1, "nonsense").status_code == 400
    r = env.act(a, p1, "change", "Use M 5.5")
    assert r.status_code == 200
    ev = env.events(types={"card.action"})[-1]["payload"]
    assert ev == {"message_id": p1, "action": "change", "by_user_id": a.me["id"], "text": "Use M 5.5"}
    p2 = env.plan(root, 2)
    p3 = env.plan(root, 3)
    assert env.act(a, p2, "approve").status_code == 409  # superseded by draft 3
    th = a.get(f"/api/messages?root={root}").json()["messages"]
    by_id = {m["id"]: m for m in th}
    assert by_id[p2]["card_blocked"] == "superseded" and by_id[p3]["can_act"] == ["approve", "change"]
    assert [m for m in b.get(f"/api/messages?root={root}").json()["messages"] if m["id"] == p3][0]["can_act"] == []
    env.feas(qid, 0)
    r = env.act(a, p3, "approve")
    assert r.status_code == 200 and r.json()["run_allowed"] is True and r.json()["status"] == "frozen"
    assert env.act(a, p3, "approve").status_code == 409


def test_forwarder_may_approve(env):
    a = env.member()
    b = env.member("Prof. B", "b@example.org")
    mid = env.post(a, "msg")
    b.post(f"/api/messages/{mid}/forward", json={"note": "n"}, headers=H)
    card = env.agent_post(root_id=mid, card={"type": "confirm", "restated": "?", "quoted_message_id": mid},
                          visible_to=b.me["id"])
    r = env.act(b, card, "yes").json()
    p = env.plan(r["root_message_id"])
    env.feas(r["question_id"], 0)
    assert env.act(b, p, "approve").status_code == 200


def test_answer_cards(env):
    a = env.member()
    b = env.member("Prof. B", "b@example.org")
    qid, root = env.question_via_suggest(a)
    env.agent.patch(f"/api/agent/questions/{qid}", json={"status": "answered_record", "path": "record"}, headers=A)
    ar = env.agent_post(root_id=root, card={
        "type": "answer_record", "summary": "No usable signal.",
        "points": [{"text": "Closed before running.", "refs": [{"label": "TR-1", "url": "https://example.org/tr1"}]}],
        "limits": "Not run."})
    assert env.act(b, ar, "test_anyway").status_code == 403
    r = env.act(a, ar, "test_anyway")
    assert r.status_code == 200
    q = env.agent.get(f"/api/agent/questions/{qid}", headers=A).json()
    assert q["status"] == "recorded" and q["path"] == "test"
    ar2 = env.agent_post(root_id=root, card={"type": "answer_record", "summary": "s", "points": [], "limits": ""})
    assert env.act(a, ar2, "not_answered").status_code == 409  # path is test now
    at = env.agent_post(root_id=root, card={"type": "answer_test", "verdict": "No effect", "summary": "s",
                                            "links": [{"label": "result", "url": "https://example.org/r"}],
                                            "limits": "one region"})
    assert env.act(a, at, "approve").status_code == 400
    # answer notification went out (logged without SMTP)
    assert any("answer has arrived" in m["subject"] for m in env.board.mailer.sent)


def test_not_answered_with_text(env):
    a = env.member()
    qid, root = env.question_via_suggest(a)
    ar = env.agent_post(root_id=root, card={"type": "answer_record", "summary": "s"})
    assert env.act(a, ar, "not_answered", "I meant onshore only").status_code == 200
    ev = env.events(types={"card.action"})[-1]["payload"]
    assert ev["action"] == "not_answered" and ev["text"] == "I meant onshore only"


def test_card_validation(env):
    a = env.member()
    mid = env.post(a, "x")
    bad = [
        {"type": "nope"},
        {"type": "plan", "question": "q"},  # no draft_no
        {"type": "plan", "draft_no": 1, "question": "q", "full_plan_url": "javascript:alert(1)"},
        {"type": "answer_test", "verdict": "v", "summary": "s", "links": [{"label": "x", "url": "data:text/html,1"}]},
        {"type": "notice"},
    ]
    for card in bad:
        r = env.agent.post("/api/agent/messages", headers=A, json={"root_id": mid, "card": card})
        assert r.status_code == 400, card
    # unknown fields are dropped; card text is stored as data
    cid = env.agent_post(root_id=mid, card={"type": "notice", "text": "<img src=x onerror=alert(1)>", "html": "<b>"})
    m = a.get(f"/api/messages?root={mid}").json()["messages"][0]
    assert m["id"] == cid and m["card"] == {"type": "notice", "text": "<img src=x onerror=alert(1)>",
                                            "quoted_message_id": None}


def test_status_changes_and_cost_privacy(env):
    a = env.member()
    qid, root = env.question_via_suggest(a)
    assert env.agent.patch(f"/api/agent/questions/{qid}", json={"status": "bogus"}, headers=A).status_code == 400
    assert env.agent.patch(f"/api/agent/questions/{qid}", json={"path": "x"}, headers=A).status_code == 400
    r = env.agent.patch(f"/api/agent/questions/{qid}", json={"status": "waiting_approval", "path": "test"}, headers=A)
    assert r.json()["status"] == "waiting_approval"
    assert any("waiting for your approval" in m["subject"] for m in env.board.mailer.sent)
    env.feas(qid, 42.5, False)
    q = feed(a)[0]["question"]
    assert q["status"] == "waiting_approval" and q["public_summary"].startswith("Open data")
    blob = json.dumps(a.get("/api/messages?root=none").json()) + json.dumps(a.get("/api/questions").json()) \
        + json.dumps(a.get(f"/api/messages?root={root}").json())
    assert "secret detail" not in blob and "42.5" not in blob and "est_cost" not in blob
    assert a.get("/api/admin/feasibility").status_code == 403
    rep = env.coordinator().get("/api/admin/feasibility").json()["reports"][0]
    assert rep["private_detail"] == "secret detail" and rep["est_cost_eur"] == 42.5
    assert not [e for e in env.board.visible_events(a.me, 0)[0] if e["type"] == "feasibility.updated"]


def test_feasibility_decision_rule(env):
    a = env.member()
    cases = [(0, False, "auto"), (9.99, False, "auto"), (10, False, "needs_coordinator"),
             (5, True, "needs_coordinator"), (120, True, "needs_coordinator")]
    for i, (cost, blind, want) in enumerate(cases):
        qid, _ = env.question_via_suggest(a, f"question {i}?")
        assert env.feas(qid, cost, blind) == want, (cost, blind)
    r = env.agent.put("/api/agent/feasibility/Q-001", headers=A, json={"public_summary": "s", "est_cost_eur": "x",
                                                                         "touches_blind": False})
    assert r.status_code == 400
    assert env.agent.put("/api/agent/feasibility/Q-999", headers=A,
                         json={"public_summary": "s", "est_cost_eur": 1, "touches_blind": False}).status_code == 404


def test_needs_coordinator_then_approve_run(env):
    a = env.member()
    co = env.coordinator()
    qid, root = env.question_via_suggest(a)
    env.feas(qid, 25, False)
    p = env.plan(root)
    r = env.act(a, p, "approve").json()
    assert r["run_allowed"] is False and r["status"] == "on_hold"
    ev = env.events(types={"plan.approved"})[-1]["payload"]
    assert ev == {"question_id": qid, "by_user_id": a.me["id"], "run_allowed": False}
    r = co.post(f"/api/admin/questions/{qid}/approve_run", headers=H).json()
    assert r["status"] == "frozen" and r["released"] is True
    th = a.get(f"/api/messages?root={root}").json()["messages"]
    assert th[-1]["card"]["text"].startswith("Run approved by the board coordinator")
    assert env.events(types={"run.released"})[-1]["payload"] == {"question_id": qid}


def test_hold_and_release(env):
    a = env.member()
    co = env.coordinator()
    qid, root = env.question_via_suggest(a)
    env.feas(qid, 0)
    env.act(a, env.plan(root), "approve")
    assert co.post(f"/api/admin/questions/{qid}/hold", json={}, headers=H).status_code == 400
    r = co.post(f"/api/admin/questions/{qid}/hold", json={"reason": "Check the catalogue licence first."}, headers=H)
    assert r.json()["status"] == "on_hold"
    assert env.events(types={"question.held"})[-1]["payload"] == {"question_id": qid,
                                                                  "reason": "Check the catalogue licence first."}
    th = a.get(f"/api/messages?root={root}").json()["messages"]
    assert th[-1]["card"]["text"] == "Run on hold: Check the catalogue licence first."
    assert th[-1]["author"]["role"] == "coordinator"
    # the agent cannot resume a held question
    assert env.agent.patch(f"/api/agent/questions/{qid}", json={"status": "running"}, headers=A).status_code == 409
    r = co.post(f"/api/admin/questions/{qid}/release", headers=H).json()
    assert r["status"] == "frozen"
    th = a.get(f"/api/messages?root={root}").json()["messages"]
    assert th[-1]["card"]["text"].startswith("Run released by the board coordinator")
    assert co.post(f"/api/admin/questions/{qid}/release", headers=H).status_code == 409


def test_three_running_queue_rule(env):
    a = env.member()
    qs = []
    for i in range(5):
        qid, root = env.question_via_suggest(a, f"question {i}?")
        env.feas(qid, 0)
        qs.append((qid, env.plan(root)))
    results = [env.act(a, p, "approve").json() for _, p in qs]
    assert [r["status"] for r in results] == ["frozen", "frozen", "frozen", "queued", "queued"]
    assert [r["queue_pos"] for r in results[3:]] == [1, 2]
    assert [r["run_allowed"] for r in results] == [True, True, True, False, False]
    ids = [q for q, _ in qs]
    env.agent.patch(f"/api/agent/questions/{ids[0]}", json={"status": "running"}, headers=A)
    # the agent cannot jump the queue
    assert env.agent.patch(f"/api/agent/questions/{ids[3]}", json={"status": "running"}, headers=A).status_code == 409
    after = env.events()[-1]["id"]
    env.agent.patch(f"/api/agent/questions/{ids[0]}", json={"status": "answered"}, headers=A)
    rel = env.events(after, types={"run.released"})
    assert [e["payload"]["question_id"] for e in rel] == [ids[3]]
    st = {q["id"]: q for q in a.get("/api/questions").json()["questions"]}
    assert st[ids[3]]["status"] == "frozen" and st[ids[4]]["status"] == "queued" and st[ids[4]]["queue_pos"] == 1
    # withdrawing a frozen one releases the next
    env.agent.patch(f"/api/agent/questions/{ids[1]}", json={"status": "withdrawn"}, headers=A)
    st = {q["id"]: q for q in a.get("/api/questions").json()["questions"]}
    assert st[ids[4]]["status"] == "frozen"
    running = [q for q in st.values() if q["status"] in ("running", "frozen")]
    assert len(running) == 3


def test_agent_question_and_thread(env):
    a = env.member()
    mid = env.post(a, "@knotenlinie have GNSS velocities been checked?")
    r = env.agent.post("/api/agent/questions", headers=A,
                       json={"root_message_id": mid, "restated": "GNSS?", "author_id": a.me["id"]})
    assert r.status_code == 200 and r.json() == {"id": "Q-001", "root_message_id": mid}
    assert env.agent.post("/api/agent/questions", headers=A,
                          json={"root_message_id": mid, "restated": "x", "author_id": a.me["id"]}).status_code == 409
    env.agent_post(root_id=mid, body="Recorded as Q-001.")
    th = env.agent.get(f"/api/agent/thread/{mid}", headers=A).json()
    assert th["question"]["id"] == "Q-001" and th["replies"][0]["author"]["role"] == "agent"
    assert th["root"]["author"]["name"] == "Prof. A" and th["root"]["body"].startswith("@knotenlinie")
    m = feed(a)[0]
    assert m["question"]["id"] == "Q-001" and m["reply_count"] == 1


def test_events_long_poll(env):
    a = env.member()
    base = env.board.last_event_id()  # the member's user.invited event
    t0 = time.time()
    r = env.agent.get(f"/api/agent/events?after={base}&wait=0", headers=A).json()
    assert r["events"] == [] and r["last"] == base and time.time() - t0 < 1
    env.post(a, "hello")
    r = env.agent.get(f"/api/agent/events?after={base}&wait=25", headers=A).json()
    assert len(r["events"]) == 1 and r["last"] == r["events"][0]["id"]
    last = r["last"]
    t0 = time.time()
    r = env.agent.get(f"/api/agent/events?after={last}&wait=1", headers=A).json()
    assert r["events"] == [] and r["last"] == last and 0.9 <= time.time() - t0 < 3
    # wakes up promptly when an event arrives
    with TestClient(env.app) as c:
        def later():
            time.sleep(0.4)
            env.board.post_message(a.me, "wake up", None)
        threading.Thread(target=later).start()
        t0 = time.time()
        r = c.get(f"/api/agent/events?after={last}&wait=20", headers=A).json()
        assert len(r["events"]) == 1 and time.time() - t0 < 2.5


def test_poll_fallback_endpoint(env):
    a = env.member()
    r = a.get("/api/events").json()
    head = r["last"]
    env.post(a, "x")
    r = a.get(f"/api/events?after={head}").json()
    assert r["events"][0]["type"] == "message.created" and "author_id" not in r["events"][0]


def test_mention_by_name_notifies(env):
    a = env.member()
    env.member("Prof. Beta", "beta@example.org")
    before = len(env.board.mailer.sent)
    env.post(a, "What do you think, Prof. Beta?")
    sent = env.board.mailer.sent[before:]
    assert len(sent) == 1 and sent[0]["to"] == "beta@example.org" and "/auth/verify?token=" in sent[0]["text"]
