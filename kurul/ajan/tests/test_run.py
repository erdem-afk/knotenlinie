"""KURUL_AUTORUN=1 path, with a fake git (no git command is run by the tests)."""

import json
from pathlib import Path

from .util import PROF_A, Harness

Q = "Do strike-slip mainshocks in Turkey produce fewer aftershocks than normal-faulting ones of the same size?"


class FakeGit:
    def __init__(self):
        self.commits = []
        self.worktrees = []

    def worktree(self, branch, path):
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        (path / "kayit").mkdir(exist_ok=True)
        (path / "kayit" / "adaylar.jsonl").write_text("", encoding="utf-8")
        self.worktrees.append((branch, str(path)))
        return path

    def commit(self, wt, paths, message):
        self.commits.append((list(paths), message))
        return f"c{len(self.commits)}"


class AutoRun(Harness):
    cfg_overrides = {"KURUL_AUTORUN": "1"}

    def setUp(self):
        super().setUp()
        self.git = FakeGit()
        self.worker = self.make_worker(git=self.git)

    def _approve(self, body=Q):
        self.site.member_post(PROF_A, body)
        self.pump()
        self.site.card_action(self.site.cards("suggest")[0]["id"], "yes", PROF_A)
        self.pump()
        self.site.card_action(self.site.cards("plan")[0]["id"], "approve", PROF_A)
        self.pump()

    def test_review_freeze_run_answer_ledger(self):
        statuses = []
        orig = self.worker.client.patch_question

        def patch(qid, **f):
            if "status" in f:
                statuses.append(f["status"])
            return orig(qid, **f)
        self.worker.client.patch_question = patch
        self._approve()
        self.assertEqual(statuses, ["waiting_approval", "frozen", "running", "answered", "in_ledger"])
        self.assertEqual([c for c in self.jobs() if c in ("review", "run")], ["review", "run"])
        run_call = [c for c in self.llm.calls if c["job"] == "run"][0]
        self.assertEqual(run_call["tools"], ["Read", "Grep", "Glob", "Write", "Edit", "Bash"])
        wt = Path(self.git.worktrees[0][1])
        self.assertEqual(self.git.worktrees[0][0], "kurul/q-001")
        frz = json.loads((wt / "kayit/kurul/Q-001/freeze.json").read_text())
        import hashlib
        self.assertEqual(frz["sha256"], hashlib.sha256((wt / "kayit/kurul/Q-001/plan.json").read_bytes()).hexdigest())
        self.assertIn(frz["sha256"], run_call["prompt"])
        line = json.loads((wt / "kayit/adaylar.jsonl").read_text().strip())
        self.assertEqual(line["kimlik"], "KURUL-Q-001")
        self.assertEqual(line["hukum"], "H0")
        self.assertEqual(line["soran"], "Board member")
        self.assertEqual(len(self.git.commits), 2)
        ans = self.site.cards("answer_test")
        self.assertEqual(len(ans), 1)
        self.assertEqual(ans[0]["card"]["verdict"], "H0")
        self.assertTrue(ans[0]["card"]["links"][0]["url"].startswith(
            "https://github.com/example-owner/example-repo/blob/kurul/q-001/"))
        self.assertEqual(self.site.questions["Q-001"]["status"], "in_ledger")
        self.assertFalse((self.worker.cfg.state_dir / "kuyruk" / "Q-001.json").exists())
        # Never twice.
        self.site.release("Q-001")
        self.pump()
        self.assertEqual([c for c in self.jobs() if c == "run"], ["run"])

    def test_review_failure_sends_plan_back(self):
        self._approve(Q + " (fail-review)")
        self.assertNotIn("run", self.jobs())
        self.assertEqual(self.git.commits, [])
        self.assertEqual(self.site.questions["Q-001"]["status"], "waiting_approval")
        self.assertIn("magnitude cut", self.site.cards("notice")[0]["card"]["text"])

    def test_held_question_does_not_run(self):
        self.site.member_post(PROF_A, Q)
        self.pump()
        self.site.card_action(self.site.cards("suggest")[0]["id"], "yes", PROF_A)
        self.pump()
        self.site.hold("Q-001", "budget check")
        self.pump()
        self.site.card_action(self.site.cards("plan")[0]["id"], "approve", PROF_A)
        self.pump()
        self.assertNotIn("review", self.jobs())
