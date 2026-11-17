"""The CLI adapter, exercised against a stand-in `claude` script (no real model calls)."""

import json
import os
import shutil
import stat
import tempfile
import unittest
from pathlib import Path

from ajan.config import Config
from ajan.llm import READ_ONLY, ClaudeCLI, LLMError, make_llm, parse_json

STUB = r"""#!/usr/bin/env python3
import json, os, sys
prompt = sys.stdin.read()
rec = {"argv": sys.argv[1:], "prompt": prompt, "cwd": os.getcwd(),
       "has_token": "KURUL_AGENT_TOKEN" in os.environ}
open(os.environ["STUB_OUT"], "w").write(json.dumps(rec))
mode = os.environ.get("STUB_MODE", "ok")
if mode == "error":
    print(json.dumps({"type": "result", "subtype": "error_max_turns", "is_error": True, "result": ""}))
elif mode == "crash":
    sys.stderr.write("boom"); sys.exit(3)
else:
    print(json.dumps({"type": "result", "subtype": "success", "is_error": False, "num_turns": 1,
                      "result": "```json\n{\"is_question\": false, \"confidence\": 0.1}\n```"}))
"""


class CLI(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="ajan-llm-"))
        self.stub = self.tmp / "claude"
        self.stub.write_text(STUB)
        self.stub.chmod(self.stub.stat().st_mode | stat.S_IEXEC)
        self.out = self.tmp / "rec.json"
        os.environ["STUB_OUT"] = str(self.out)
        os.environ["KURUL_AGENT_TOKEN"] = "secret"
        self.cfg = Config.from_env({"KURUL_CLAUDE_BIN": str(self.stub), "KURUL_MODEL_FAST": "fastmodel",
                                    "KURUL_MODEL_MAIN": "mainmodel", "KURUL_STATE_DIR": str(self.tmp / "s")})

    def tearDown(self):
        for k in ("STUB_OUT", "STUB_MODE", "KURUL_AGENT_TOKEN"):
            os.environ.pop(k, None)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_classify_has_no_tools_and_fast_model(self):
        cmd = ClaudeCLI(self.cfg).command("classify", [])
        self.assertEqual(cmd[1], "-p")
        self.assertEqual(cmd[cmd.index("--output-format") + 1], "json")
        self.assertEqual(cmd[cmd.index("--model") + 1], "fastmodel")
        self.assertEqual(cmd[cmd.index("--tools") + 1], "")
        self.assertNotIn("--allowedTools", cmd)
        self.assertIn("Bash", cmd[cmd.index("--disallowedTools") + 1])
        for f in ("--restricted", "--strict-mcp-config", "--no-session-persistence", "--append-system-prompt"):
            self.assertIn(f, cmd)
        self.assertEqual(cmd[cmd.index("--permission-mode") + 1], "dontAsk")

    def test_respond_is_read_only(self):
        cmd = ClaudeCLI(self.cfg).command("respond", READ_ONLY)
        self.assertEqual(cmd[cmd.index("--model") + 1], "mainmodel")
        self.assertEqual(cmd[cmd.index("--tools") + 1], "Read,Grep,Glob")
        self.assertEqual(cmd[cmd.index("--allowedTools") + 1], "Read,Grep,Glob")
        denied = cmd[cmd.index("--disallowedTools") + 1].split(",")
        for t in ("Bash", "Edit", "Write", "WebFetch", "WebSearch"):
            self.assertIn(t, denied)

    def test_invocation_passes_prompt_on_stdin_and_hides_token(self):
        cli = ClaudeCLI(self.cfg)
        out = cli("classify", "hello prompt", self.tmp, [])
        self.assertEqual(parse_json(out), {"is_question": False, "confidence": 0.1})
        rec = json.loads(self.out.read_text())
        self.assertEqual(rec["prompt"], "hello prompt")
        self.assertEqual(Path(rec["cwd"]).resolve(), self.tmp.resolve())
        self.assertFalse(rec["has_token"])

    def test_errors_raise(self):
        cli = ClaudeCLI(self.cfg)
        os.environ["STUB_MODE"] = "error"
        with self.assertRaises(LLMError):
            cli("respond", "x", self.tmp, READ_ONLY)
        os.environ["STUB_MODE"] = "crash"
        with self.assertRaises(LLMError):
            cli("respond", "x", self.tmp, READ_ONLY)

    def test_fake_selected_by_env(self):
        from ajan.fake_llm import FakeLLM
        self.assertIsInstance(make_llm(Config.from_env({"KURUL_LLM": "fake"})), FakeLLM)


class ParseJson(unittest.TestCase):
    def test_variants(self):
        self.assertEqual(parse_json('{"a": 1}'), {"a": 1})
        self.assertEqual(parse_json('Here:\n```json\n{"a": {"b": "}"}}\n```'), {"a": {"b": "}"}})
        self.assertEqual(parse_json('prefix {"a": 2} suffix'), {"a": 2})
        with self.assertRaises(LLMError):
            parse_json("no json here")


if __name__ == "__main__":
    unittest.main()
