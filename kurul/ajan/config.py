"""Configuration from environment variables (SPEC.md section 8, plus worker-local extras)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _bool(v: str | None, default: bool = False) -> bool:
    if v is None or v.strip() == "":
        return default
    return v.strip().lower() in ("1", "true", "yes", "on")


def _float(v: str | None, default: float) -> float:
    try:
        return float(v) if v not in (None, "") else default
    except ValueError:
        return default


def _list(v: str | None) -> list[str]:
    if not v:
        return []
    return [x.strip() for x in v.split(",") if x.strip()]


@dataclass
class Config:
    base_url: str = ""
    agent_token: str = ""
    repo: Path = Path(".")
    llm: str = "claude"  # "claude" | "fake"
    autorun: bool = False
    model_fast: str = "haiku"
    model_main: str = "opus"
    state_dir: Path = Path("state")
    suggest_threshold: float = 0.85
    mention_threshold: float = 0.6
    repo_url: str = ""  # public GitHub base, e.g. https://github.com/OWNER/REPO
    repo_ref: str = "main"  # branch or tag used in public links
    ledger_path: str = "kayit/adaylar.jsonl"
    blocked_names: list[str] = field(default_factory=list)  # personal names never posted
    blocked_terms: list[str] = field(default_factory=list)  # extra internal names never posted
    claude_bin: str = "claude"
    llm_timeout: float = 900.0
    run_timeout: float = 6 * 3600.0
    poll_wait: int = 25
    backoff_base: float = 1.0
    backoff_max: float = 60.0
    event_attempts: int = 3
    handle: str = "knotenlinie"

    @classmethod
    def from_env(cls, env: dict | None = None) -> "Config":
        e = os.environ if env is None else env
        state = e.get("KURUL_STATE_DIR") or os.path.join(
            os.path.expanduser("~"), ".local", "state", "kurul-ajan")
        return cls(
            base_url=(e.get("KURUL_BASE_URL") or "").rstrip("/"),
            agent_token=e.get("KURUL_AGENT_TOKEN") or "",
            repo=Path(e.get("KURUL_REPO") or ".").resolve(),
            llm=(e.get("KURUL_LLM") or "claude").strip().lower(),
            autorun=_bool(e.get("KURUL_AUTORUN"), False),
            model_fast=e.get("KURUL_MODEL_FAST") or "haiku",
            model_main=e.get("KURUL_MODEL_MAIN") or "opus",
            state_dir=Path(state),
            suggest_threshold=_float(e.get("KURUL_SUGGEST_THRESHOLD"), 0.85),
            mention_threshold=_float(e.get("KURUL_MENTION_THRESHOLD"), 0.6),
            repo_url=(e.get("KURUL_REPO_URL") or "").rstrip("/"),
            repo_ref=e.get("KURUL_REPO_REF") or "main",
            ledger_path=e.get("KURUL_LEDGER_PATH") or "kayit/adaylar.jsonl",
            blocked_names=_list(e.get("KURUL_BLOCKED_NAMES")),
            blocked_terms=_list(e.get("KURUL_BLOCKED_TERMS")),
            claude_bin=e.get("KURUL_CLAUDE_BIN") or "claude",
            llm_timeout=_float(e.get("KURUL_LLM_TIMEOUT"), 900.0),
            run_timeout=_float(e.get("KURUL_RUN_TIMEOUT"), 6 * 3600.0),
            poll_wait=int(_float(e.get("KURUL_POLL_WAIT"), 25)),
            backoff_base=_float(e.get("KURUL_BACKOFF_BASE"), 1.0),
            backoff_max=_float(e.get("KURUL_BACKOFF_MAX"), 60.0),
        )

    def check(self) -> list[str]:
        """Return a list of configuration problems (empty when usable)."""
        problems = []
        if not self.base_url:
            problems.append("KURUL_BASE_URL is not set")
        elif not (self.base_url.startswith("https://") or self.base_url.startswith("http://127.")
                  or self.base_url.startswith("http://localhost")):
            problems.append("KURUL_BASE_URL must be https:// (plain http only for localhost)")
        if not self.agent_token:
            problems.append("KURUL_AGENT_TOKEN is not set")
        if self.llm not in ("claude", "fake"):
            problems.append("KURUL_LLM must be 'claude' or 'fake'")
        if not (self.repo / self.ledger_path).is_file():
            problems.append(f"ledger not found under KURUL_REPO ({self.ledger_path})")
        return problems
