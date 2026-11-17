"""python -m ajan  (from kurul/), or  PYTHONPATH=kurul python -m ajan

  python -m ajan            run the worker loop
  python -m ajan check      validate configuration and print the CLI command that would be used
"""

import json
import sys

from .config import Config
from .worker import main

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        cfg = Config.from_env()
        problems = cfg.check()
        from .llm import ClaudeCLI, READ_ONLY
        cmd = ClaudeCLI(cfg).command("respond", READ_ONLY) if cfg.llm == "claude" else ["(fake)"]
        cmd = [c if len(c) < 120 else c[:60] + "…" for c in cmd]
        print(json.dumps({"problems": problems, "llm": cfg.llm, "autorun": cfg.autorun,
                          "respond_command": cmd}, ensure_ascii=False, indent=1))
        sys.exit(1 if problems else 0)
    sys.exit(main())
