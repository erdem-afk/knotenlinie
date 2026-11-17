"""Read-only access to the research ledger in the KURUL_REPO checkout (whatever branch it is on)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import quote

from .guard import fold
from .log import log

# Ledger states whose verdict is final enough to answer from.
CLOSED = {"kapandi", "elendi", "birlesti", "kapali-sartli"}


class Ledger:
    def __init__(self, repo: Path, ledger_path: str = "kayit/adaylar.jsonl", repo_url: str = "",
                 repo_ref: str = "main"):
        self.repo = Path(repo)
        self.file = self.repo / ledger_path
        self.repo_url = repo_url.rstrip("/")
        self.repo_ref = repo_ref
        self._rows: list[dict] = []
        self._mtime = None

    def rows(self) -> list[dict]:
        try:
            m = self.file.stat().st_mtime
        except OSError:
            if self._mtime is not None or not self._rows:
                log("ledger_missing", level="warning", path=str(self.file))
            self._rows, self._mtime = [], None
            return []
        if m != self._mtime:
            out = []
            for n, line in enumerate(self.file.read_text(encoding="utf-8").splitlines(), 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    log("ledger_bad_line", level="warning", line=n)
            self._rows, self._mtime = out, m
        return self._rows

    def by_id(self) -> dict[str, dict]:
        return {r.get("kimlik"): r for r in self.rows() if r.get("kimlik")}

    def get(self, kimlik: str) -> dict | None:
        return self.by_id().get(kimlik)

    def is_closed(self, kimlik: str) -> bool:
        r = self.get(kimlik)
        return bool(r) and r.get("durum") in CLOSED

    def search(self, text: str, limit: int = 8) -> list[dict]:
        """Crude keyword overlap; only a hint list for the model, which searches itself."""
        words = {w for w in re.findall(r"\w{4,}", fold(text))}
        if not words:
            return []
        scored = []
        for r in self.rows():
            blob = fold(" ".join(str(r.get(k, "")) for k in ("ad", "soru", "etiket", "ders", "sonuc")))
            s = sum(1 for w in words if w in blob)
            if s:
                scored.append((s, r))
        scored.sort(key=lambda x: -x[0])
        return [r for _, r in scored[:limit]]

    def files_for(self, kimlik: str) -> list[str]:
        """Repo-relative files for an entry: paths named in its `kayit` field that exist, else
        pre-registration files named after the id."""
        r = self.get(kimlik) or {}
        result, prereg, named = [], [], []
        # 1. result notes of the run: kayit/turetme/<id lower, no dash>/*sonuc*.md
        d = self.repo / "kayit" / "turetme" / re.sub(r"[^a-z0-9]", "", kimlik.lower())
        if d.is_dir():
            result = [str(f.relative_to(self.repo)) for f in sorted(d.glob("*sonuc*.md"))]
        # 2. the pre-registration named after the id (exact id, not a sibling like TR-13 for TR-13b)
        d = self.repo / "kayit" / "onkayit"
        if d.is_dir():
            prereg = [str(f.relative_to(self.repo)) for f in sorted(d.glob(f"{kimlik}_*ONKAYIT.md"))]
        # 3. files named in the entry's `kayit` field
        for part in re.split(r"[;\n]", str(r.get("kayit", ""))):
            p = part.strip().rstrip(".,")
            p = re.sub(r"\s*\(.*\)$", "", p)
            if p and "/" in p and not p.startswith("/") and ".." not in p and (self.repo / p).is_file():
                named.append(p)
        out = []
        for p in result + prereg + named:
            if p not in out:
                out.append(p)
        return out

    def ref(self, kimlik: str) -> dict:
        """{label, url?}: url is the public repo path of the entry's main file when known."""
        ref = {"label": kimlik}
        files = self.files_for(kimlik)
        if self.repo_url and files:
            ref["url"] = f"{self.repo_url}/blob/{quote(self.repo_ref)}/{quote(files[0])}"
        return ref

    def summary_line(self, r: dict) -> str:
        return f"{r.get('kimlik')} [{r.get('durum')}/{r.get('hukum')}] {r.get('ad', '')}"
