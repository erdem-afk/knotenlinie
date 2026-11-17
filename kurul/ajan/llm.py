"""The single entry point for model calls: llm(job, prompt, cwd, tools).

Real implementation: the Claude Code CLI in headless print mode. Flags were taken from
`claude --help` of version 2.1.x (no --max-turns exists there; a subprocess timeout bounds a call).

KURUL_LLM=fake selects FakeLLM (see fake_llm.py), used by all tests.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import time
from pathlib import Path

from .log import log

PROMPT_DIR = Path(__file__).resolve().parent / "prompts"

# Jobs that run on the fast model; all others use the main model.
FAST_JOBS = {"classify", "restate"}
READ_ONLY = ["Read", "Grep", "Glob"]
# Copied into usage.jsonl when present in the CLI's JSON result.
USAGE_FIELDS = ("total_cost_usd", "duration_ms", "duration_api_ms", "num_turns")
TOKEN_FIELDS = ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
ALL_RISKY = ["Bash", "Edit", "Write", "NotebookEdit", "WebFetch", "WebSearch", "Task", "Agent"]


class LLMError(Exception):
    pass


def load_prompt(name: str) -> str:
    return (PROMPT_DIR / f"{name}.txt").read_text(encoding="utf-8")


def parse_json(text: str) -> dict:
    """Pull the first JSON object out of model text (tolerates code fences and prose)."""
    if text is None:
        raise LLMError("empty model output")
    t = text.strip()
    m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", t, re.S)
    if m:
        t = m.group(1)
    try:
        v = json.loads(t)
        if isinstance(v, dict):
            return v
    except json.JSONDecodeError:
        pass
    start = t.find("{")
    while start != -1:
        depth, in_str, esc = 0, False, False
        for i in range(start, len(t)):
            c = t[i]
            if in_str:
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == '"':
                    in_str = False
            elif c == '"':
                in_str = True
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    try:
                        v = json.loads(t[start:i + 1])
                        if isinstance(v, dict):
                            return v
                    except json.JSONDecodeError:
                        break
                    break
        start = t.find("{", start + 1)
    raise LLMError("no JSON object in model output")


class ClaudeCLI:
    def __init__(self, cfg):
        self.cfg = cfg
        self.rules = load_prompt("rules")

    def model_for(self, job: str) -> str:
        return self.cfg.model_fast if job in FAST_JOBS else self.cfg.model_main

    def command(self, job: str, tools: list[str]) -> list[str]:
        tools = list(tools or [])
        cmd = [self.cfg.claude_bin, "-p",
               "--output-format", "json",
               "--model", self.model_for(job),
               "--tools", ",".join(tools),          # "" = no tools at all
               "--permission-mode", "dontAsk",       # anything not allowed is denied, never prompted
               "--permission-prompts", "none",
               "--restricted",                       # no shell/web unless named; file tools confined to cwd
               "--strict-mcp-config",                # no MCP servers
               "--no-session-persistence",
               "--disable-slash-commands",
               "--append-system-prompt", self.rules]
        if tools:
            cmd += ["--allowedTools", ",".join(tools)]
        denied = [t for t in ALL_RISKY if t not in tools]
        if denied:
            cmd += ["--disallowedTools", ",".join(denied)]
        return cmd

    def __call__(self, job: str, prompt: str, cwd, tools: list[str] | None = None) -> str:
        tools = list(tools or [])
        cmd = self.command(job, tools)
        env = {k: v for k, v in os.environ.items()
               if k not in ("KURUL_AGENT_TOKEN",) and not k.startswith("KURUL_SESSION")}
        timeout = self.cfg.run_timeout if job == "run" else self.cfg.llm_timeout
        t0 = time.time()
        try:
            p = subprocess.run(cmd, input=prompt, cwd=str(cwd), env=env, capture_output=True,
                               text=True, timeout=timeout)
        except subprocess.TimeoutExpired as e:
            self.record_usage(job, time.time() - t0, None, "timeout")
            raise LLMError(f"{job}: timed out after {timeout}s") from e
        except OSError as e:
            raise LLMError(f"{job}: cannot start claude: {e}") from e
        dt = round(time.time() - t0, 1)
        if p.returncode != 0 and not p.stdout.strip():
            self.record_usage(job, dt, None, f"exit {p.returncode}")
            raise LLMError(f"{job}: exit {p.returncode}: {p.stderr.strip()[:300]}")
        try:
            out = json.loads(p.stdout)
        except json.JSONDecodeError as e:
            self.record_usage(job, dt, None, "output not JSON")
            raise LLMError(f"{job}: CLI output is not JSON: {p.stdout[:200]}") from e
        if isinstance(out, list):  # defensive: some versions emit a list of messages
            out = next((m for m in reversed(out) if isinstance(m, dict) and m.get("type") == "result"), {})
        log("llm_call", job=job, model=self.model_for(job), seconds=dt,
            turns=out.get("num_turns"), is_error=out.get("is_error"), subtype=out.get("subtype"))
        self.record_usage(job, dt, out, None)
        if out.get("is_error") or out.get("subtype") not in (None, "success"):
            raise LLMError(f"{job}: {out.get('subtype')}: {str(out.get('result'))[:300]}")
        if out.get("structured_output") is not None:
            return json.dumps(out["structured_output"], ensure_ascii=False)
        return out.get("result") or ""


    def record_usage(self, job: str, seconds: float, out: dict | None, error: str | None) -> None:
        """Append one line per model call to KURUL_STATE_DIR/usage.jsonl (best effort, never raises).

        Token and cost fields are copied only when the CLI's JSON result carries them."""
        rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "job": job,
               "model": self.model_for(job), "seconds": round(seconds, 1)}
        out = out or {}
        ok = error is None and not out.get("is_error") and out.get("subtype") in (None, "success")
        rec["ok"] = ok
        if error or not ok:
            rec["error"] = error or str(out.get("subtype"))
        for k in USAGE_FIELDS:
            if isinstance(out.get(k), (int, float)):
                rec[k] = out[k]
        u = out.get("usage")
        if isinstance(u, dict):
            for k in TOKEN_FIELDS:
                if isinstance(u.get(k), (int, float)):
                    rec[k] = u[k]
        if isinstance(out.get("modelUsage"), dict):  # actual model ids behind the alias
            rec["models"] = sorted(str(m) for m in out["modelUsage"])
        try:
            path = Path(self.cfg.state_dir) / "usage.jsonl"
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        except OSError as e:
            log("usage_write_failed", level="warning", error=str(e)[:200])


def make_llm(cfg):
    if cfg.llm == "fake":
        from .fake_llm import FakeLLM
        return FakeLLM()
    return ClaudeCLI(cfg)
