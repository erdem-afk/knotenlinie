"""Fill prompt templates. Placeholders are {{NAME}}; filled in one pass so member text that happens
to contain {{...}} is never expanded."""

from __future__ import annotations

import re

from .llm import load_prompt

_PH = re.compile(r"\{\{([A-Z_]+)\}\}")


def fill(name: str, **values) -> str:
    tpl = load_prompt(name)

    def rep(m):
        k = m.group(1)
        return str(values.get(k, "")) if k in values else m.group(0)

    out = _PH.sub(rep, tpl)
    missing = set(_PH.findall(tpl)) - set(values)
    if missing:
        raise KeyError(f"prompt {name}: missing {sorted(missing)}")
    return out
