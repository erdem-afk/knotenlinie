"""The frozen-plan run (only with KURUL_AUTORUN=1).

Kept deliberately conservative and separate from the rest of the worker:
1. independent review of the approved plan (read-only model call);
2. freeze: plan file + sha256 written to kayit/kurul/Q-nnn/ in a dedicated git worktree of
   KURUL_REPO on branch kurul/q-nnn, committed (never pushed; the team pushes);
3. a single run in that worktree (open data, local compute; the prompt forbids blind data);
4. answer_test card, ledger line appended to kayit/adaylar.jsonl in the worktree, commit;
5. status frozen -> running -> answered -> in_ledger.
Every step is keyed so a restart never repeats a finished step (the run itself is never repeated).
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path
from urllib.parse import quote

from . import cards, guard
from .llm import READ_ONLY
from .log import log
from .prompting import fill
from .texts import text

RUN_TOOLS = ["Read", "Grep", "Glob", "Write", "Edit", "Bash"]
VERDICTS = {"H0", "H1", "ayirt-edilemez", "guc-yok", "veri-yok"}


class Git:
    """Thin git wrapper; tests inject a fake with the same methods."""

    def __init__(self, repo: Path):
        self.repo = Path(repo)

    def _run(self, args, cwd):
        p = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            raise RuntimeError(f"git {' '.join(args)}: {p.stderr.strip()[:300]}")
        return p.stdout.strip()

    def worktree(self, branch: str, path: Path) -> Path:
        if not (Path(path) / ".git").exists():
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            self._run(["worktree", "add", "-b", branch, str(path), "HEAD"], self.repo)
        return Path(path)

    def commit(self, wt: Path, paths: list[str], message: str) -> str:
        self._run(["add", "--", *paths], wt)
        self._run(["-c", "user.name=Knotenlinie agent", "-c", "user.email=agent@invalid",
                   "commit", "-m", message, "--", *paths], wt)
        return self._run(["rev-parse", "HEAD"], wt)


def plan_markdown(q: dict, sha: str | None = None) -> str:
    p = q["plan"]
    lines = [f"# {q['qid']} test plan (draft {q.get('draft_no')})", "",
             f"Question (as confirmed): {q.get('restated')}", "",
             f"Question as we understood it: {p['question']}", "", f"Data: {p['data']}", "",
             f"Rule fixed in advance: {p['rule']}", "", f"Smallest effect we could see: {p['smallest_effect']}", ""]
    return "\n".join(lines)


def run_question(w, q: dict) -> str:
    cfg, client, st = w.cfg, w.client, w.state
    qid, root_id, lang = q["qid"], q["root_message_id"], q.get("lang") or "en"
    git = w.git or Git(cfg.repo)
    data = guard.data_block([("the question, as confirmed by the member", q.get("restated") or "")])
    plan_txt = json.dumps(q["plan"], ensure_ascii=False, indent=1)

    # 1. Independent review -----------------------------------------------------------------
    review = w.ask(f"review:{qid}:{q.get('draft_no')}", "review",
                   fill("review", QID=qid, PLAN=plan_txt, DATA=data), cfg.repo, READ_ONLY, lambda o: [])
    if review is None:
        raise RuntimeError("review produced no output")
    if not review.get("ok"):
        issues = " ".join(str(x) for x in (review.get("blocking") or [])[:3])
        msg = text("review_failed", lang, issues=issues)
        if w.violations(msg):
            msg = text("review_failed", lang, issues="")
        w.post(f"review_failed:{qid}:{q.get('draft_no')}", root_id, card=cards.notice(msg), qid=qid)
        w.once(f"patch:{qid}:review_back:{q.get('draft_no')}",
               lambda: client.patch_question(qid, status="waiting_approval"))
        st.save_question(qid, {"status": "waiting_approval", "review": review})
        log("review_failed", question_id=qid, blocking=len(review.get("blocking") or []))
        return "review_failed"

    # 2. Freeze -------------------------------------------------------------------------------
    branch = f"kurul/{qid.lower()}"
    wt = git.worktree(branch, Path(cfg.state_dir) / "worktrees" / qid)
    rel = f"kayit/kurul/{qid}"

    def freeze():
        d = Path(wt) / rel
        d.mkdir(parents=True, exist_ok=True)
        (d / "plan.json").write_text(plan_txt + "\n", encoding="utf-8")
        (d / "plan.md").write_text(plan_markdown(q), encoding="utf-8")
        sha = hashlib.sha256((d / "plan.json").read_bytes()).hexdigest()
        (d / "freeze.json").write_text(json.dumps({
            "question_id": qid, "plan_file": f"{rel}/plan.json", "sha256": sha,
            "frozen_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "review": {"ok": True, "minor": review.get("minor") or []}}, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8")
        commit = git.commit(wt, [rel], f"kurul: freeze {qid} plan (sha256 {sha[:12]})")
        return {"sha": sha, "commit": commit}
    frozen = w.once(f"freeze:{qid}", freeze)
    w.once(f"patch:{qid}:frozen", lambda: client.patch_question(qid, status="frozen"))
    w.post(f"running:{qid}", root_id, card=cards.notice(text("running", lang)), qid=qid)
    w.once(f"patch:{qid}:running", lambda: client.patch_question(qid, status="running"))
    st.save_question(qid, {"status": "running", "plan_sha256": frozen["sha"]})
    st.set_step(f"started:{qid}")

    # 3. Single run ---------------------------------------------------------------------------
    work_dir = f"{rel}/run"
    (Path(wt) / work_dir).mkdir(parents=True, exist_ok=True)
    if w.state.has_step(f"run_attempted:{qid}") and not w.state.has_step(f"llm:run:{qid}"):
        # A previous attempt started and did not finish: never run twice; hand to the team.
        w.post(f"run_failed:{qid}", root_id, card=cards.notice(text("run_failed", lang)), qid=qid)
        return "run_interrupted"
    w.state.set_step(f"run_attempted:{qid}")
    prompt = fill("run", QID=qid, SHA=frozen["sha"], PLAN_PATH=f"{rel}/plan.json", WORK_DIR=work_dir,
                  PLAN=plan_txt, DATA=data)
    try:
        out = w.ask(f"run:{qid}", "run", prompt, wt, RUN_TOOLS,
                    lambda o: [o.get("summary"), o.get("limits")])
    except Exception as e:
        log("run_failed", level="error", question_id=qid, error=str(e)[:300])
        out = None
    if out is None or out.get("verdict") not in VERDICTS | {"cannot_run"}:
        w.post(f"run_failed:{qid}", root_id, card=cards.notice(text("run_failed", lang)), qid=qid)
        return "run_failed"
    if out["verdict"] == "cannot_run":
        w.post(f"cannot_run:{qid}", root_id, card=cards.notice(out.get("summary") or text("run_failed", lang)),
               qid=qid)
        w.once(f"patch:{qid}:not_feasible", lambda: client.patch_question(qid, status="not_feasible"))
        st.save_question(qid, {"status": "not_feasible"})
        return "not_feasible"

    # 4. Answer card --------------------------------------------------------------------------
    files = [f for f in (out.get("files") or []) if isinstance(f, str) and (Path(wt) / f).is_file()
             and not f.startswith("/") and ".." not in f]
    links = []
    for f in [f"{rel}/plan.json"] + files[:6]:
        link = {"label": f.split("/")[-1]}
        if cfg.repo_url:
            link["url"] = f"{cfg.repo_url}/blob/{quote(branch)}/{quote(f)}"
        links.append(link)
    card = cards.answer_test(out["verdict"], out.get("summary") or "", links, out.get("limits") or "")
    w.post(f"answer_test:{qid}", root_id, card=card, qid=qid)
    w.once(f"patch:{qid}:answered", lambda: client.patch_question(qid, status="answered"))

    # 5. Ledger line --------------------------------------------------------------------------
    def ledger_line():
        led = Path(wt) / cfg.ledger_path
        row = {"kimlik": f"KURUL-{qid}", "kol": "kurul", "ad": (q.get("restated") or "")[:140],
               "soru": q.get("restated") or "", "tur": "istatistik", "durum": "kapandi", "hukum": out["verdict"],
               "tarih": time.strftime("%Y-%m-%d", time.gmtime()),
               "sonuc": (out.get("ledger") or {}).get("sonuc") or out.get("summary") or "",
               "ders": (out.get("ledger") or {}).get("ders") or "",
               "soran": "Board member", "maliyet_eur": 0,
               "kayit": f"{rel}/plan.json (sha256 {frozen['sha']}); {rel}/run/",
               "etiket": ["kurul", qid]}
        with open(led, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        return git.commit(wt, [rel, cfg.ledger_path], f"kurul: {qid} result and ledger line")
    w.once(f"ledger:{qid}", ledger_line)
    w.once(f"patch:{qid}:in_ledger", lambda: client.patch_question(qid, status="in_ledger"))
    st.save_question(qid, {"status": "in_ledger", "verdict": out["verdict"]})
    return "in_ledger"
