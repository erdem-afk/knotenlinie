"""Shared test harness: a fake site, a fake model and a worker wired together."""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from ajan import log as alog
from ajan.config import Config
from ajan.fake_llm import FakeLLM
from ajan.state import State
from ajan.worker import Worker

from .fakesite import FakeSite

FIXTURE_REPO = Path(__file__).resolve().parent / "fixtures" / "repo"

PROF_A, PROF_B, DR_C, COORD = 1, 2, 3, 9


class Harness(unittest.TestCase):
    cfg_overrides: dict = {}

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="ajan-test-"))
        self.site = FakeSite()
        self.site.add_user(PROF_A, "Prof. A")
        self.site.add_user(PROF_B, "Prof. B")
        self.site.add_user(DR_C, "Dr. C")
        self.site.add_user(COORD, "Board Coordinator", role="coordinator")
        self.logs = alog.capture(True)
        self.worker = None
        self.worker = self.make_worker()

    def tearDown(self):
        alog.capture(False)
        self.worker.state.close()
        self.site.close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def make_cfg(self, **kw) -> Config:
        env = {"KURUL_BASE_URL": self.site.url, "KURUL_AGENT_TOKEN": "test-token", "KURUL_REPO": str(FIXTURE_REPO),
               "KURUL_LLM": "fake", "KURUL_STATE_DIR": str(self.tmp / "state"),
               "KURUL_REPO_URL": "https://github.com/example-owner/example-repo", "KURUL_REPO_REF": "main",
               "KURUL_BLOCKED_NAMES": "Testname Coordinator", "KURUL_BACKOFF_BASE": "0", "KURUL_POLL_WAIT": "0"}
        env.update({k: str(v) for k, v in {**self.cfg_overrides, **kw}.items()})
        return Config.from_env(env)

    def make_worker(self, llm=None, git=None, **kw) -> Worker:
        if getattr(self, "worker", None) is not None:
            self.worker.state.close()
        cfg = self.make_cfg(**kw)
        self.llm = llm or FakeLLM()
        return Worker(cfg, llm=self.llm, state=State(cfg.state_dir), sleep=lambda s: None, git=git)

    def restart(self, **kw) -> Worker:
        """Simulate a process restart: new Worker on the same state directory."""
        self.worker = self.make_worker(llm=self.llm, **kw)
        return self.worker

    def pump(self, rounds: int = 10) -> None:
        for _ in range(rounds):
            if self.worker.poll_once(0) == 0:
                return

    def jobs(self) -> list[str]:
        return [c["job"] for c in self.llm.calls]

    def agent_calls(self, method=None, prefix=None):
        return [c for c in self.site.calls if (method is None or c[0] == method)
                and (prefix is None or c[1].startswith(prefix))]

    def logged(self, event):
        return [r for r in self.logs if r["event"] == event]
