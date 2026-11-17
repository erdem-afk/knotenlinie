"""@-handles: derivation from names, validation, uniqueness, and mention parsing.

No imports from the rest of the package, so db.py (migration) and core.py can both use it.
Handles are stored lower-case; comparisons are case-insensitive.
"""

from __future__ import annotations

import re
import unicodedata

HANDLE_RE = re.compile(r"^[a-z0-9_]{2,24}$")
MAX_LEN = 24

# Never assignable to a person. `knotenlinie` is the agent's own handle; `coordinator` is an alias for
# every user with role coordinator; the rest are kept free for broadcast-style aliases.
RESERVED = frozenset({"knotenlinie", "coordinator", "agent", "admin", "everyone", "all", "here", "board"})
AGENT_HANDLE = "knotenlinie"
COORDINATOR_ALIAS = "coordinator"

# Academic and courtesy titles dropped when deriving a handle (after ASCII folding).
TITLES = frozenset({
    "prof", "professor", "dr", "doc", "docent", "assoc", "asst", "assist", "yrd", "ogr", "uyesi",
    "ars", "gor", "phd", "md", "mr", "mrs", "ms", "dipl", "ing", "emer", "emeritus",
})

# Letters that do not decompose into base letter + combining mark under NFKD.
_FOLD = str.maketrans({
    "ı": "i", "İ": "i", "ß": "ss", "æ": "ae", "Æ": "ae", "ø": "o", "Ø": "o", "đ": "d", "Đ": "d",
    "ð": "d", "Ð": "d", "ł": "l", "Ł": "l", "œ": "oe", "Œ": "oe", "þ": "th", "Þ": "th", "ħ": "h", "Ħ": "h",
})

# A @handle token in message text: not preceded by a word character, '.', '+', '-' or '@' (so the
# '@' inside an e-mail address never counts), and not followed by a word character.
MENTION_TOKEN_RE = re.compile(r"(?<![\w.+\-@])@([A-Za-z0-9_]{2,24})(?![\w@])")


def fold(s: str) -> str:
    """Lower-case ASCII approximation: ç→c, ğ→g, ı→i, İ→i, ö→o, ş→s, ü→u, é→e, ß→ss, ..."""
    s = (s or "").translate(_FOLD)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower()


def name_words(name: str) -> list[str]:
    return [w for w in re.split(r"[^a-z0-9]+", fold(name)) if w and w not in TITLES]


def base_handle(name: str) -> str:
    """Given name + surname, folded, titles dropped, no separator. '' when nothing usable is left."""
    words = name_words(name)
    if not words:
        return ""
    base = words[0] + words[-1] if len(words) > 1 else words[0]
    base = base[:MAX_LEN]
    return base if len(base) >= 2 else ""


def normalise(value) -> str | None:
    """A handle typed by a user: strip spaces and one leading '@', lower-case. None if not text."""
    if not isinstance(value, str):
        return None
    v = value.strip()
    if v.startswith("@"):
        v = v[1:]
    return v.lower()


def _taken(conn, handle: str, user_id: int | None) -> bool:
    return conn.execute("SELECT 1 FROM users WHERE handle=? COLLATE NOCASE AND id<>?",
                        (handle, user_id or -1)).fetchone() is not None


def unique_handle(conn, name: str, user_id: int) -> str:
    """The derived handle for this user: base, then base2, base3, ...; fallback member<id>."""
    base = base_handle(name) or f"member{user_id}"
    cand, n = base, 2
    while cand in RESERVED or _taken(conn, cand, user_id):
        suffix = str(n)
        cand = base[:MAX_LEN - len(suffix)] + suffix
        n += 1
    return cand


def assign(conn, user_id: int, name: str, role: str) -> str:
    """Give a freshly inserted user its handle. The agent gets `knotenlinie` when it is free."""
    if role == "agent" and not _taken(conn, AGENT_HANDLE, user_id):
        h = AGENT_HANDLE
    else:
        h = unique_handle(conn, name, user_id)
    conn.execute("UPDATE users SET handle=? WHERE id=?", (h, user_id))
    return h


def check_available(conn, handle: str, user_id: int) -> str | None:
    """Why this handle cannot be taken by user_id: 'format', 'reserved', 'taken'; None if fine."""
    if not HANDLE_RE.match(handle):
        return "format"
    if handle in RESERVED:
        return "reserved"
    if _taken(conn, handle, user_id):
        return "taken"
    return None


def mention_tokens(text: str) -> set[str]:
    """Lower-cased @handle tokens in a message body."""
    return {m.group(1).lower() for m in MENTION_TOKEN_RE.finditer(text or "")}
