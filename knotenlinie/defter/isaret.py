"""Sign convention: a channel declares its own, the writer converts once.

The stored convention is fixed: the stress tensor and the normal stress are
tension positive, and the shear stress is the component of the traction along the
DISS rake direction.  Each channel declares the convention of its own
computation and converts it to the stored convention while writing, so a silently flipped normal
stress cannot turn a closing channel into an opening one.  The conversion happens
exactly once, in the writer; the reader never re-converts.

The declaration has two closed axes.  Missing axes take the stored default; an unknown
key or value is an error, never a guess.
"""
from __future__ import annotations

from typing import Dict

import numpy as np

NORMAL_KURALLARI = ("tension_positive", "compression_positive")
KAYMA_KURALLARI = ("rake_positive", "rake_negative")
ISARET_VARSAYILAN: Dict[str, str] = {
    "normal": "tension_positive",
    "kayma": "rake_positive",
}


def isaret_dogrula(isaret) -> Dict[str, str]:
    """Validate and complete a sign declaration; never guess an unknown value."""
    if isaret is None:
        return dict(ISARET_VARSAYILAN)
    if not isinstance(isaret, dict):
        raise ValueError(f"işaret beyanı sözlük olmalı, alındı: {type(isaret).__name__}")
    bilinmeyen = sorted(set(isaret) - set(ISARET_VARSAYILAN))
    if bilinmeyen:
        raise ValueError(f"işaret beyanında bilinmeyen eksen: {bilinmeyen}")
    normal = isaret.get("normal", ISARET_VARSAYILAN["normal"])
    kayma = isaret.get("kayma", ISARET_VARSAYILAN["kayma"])
    if normal not in NORMAL_KURALLARI:
        raise ValueError(f"geçersiz normal kuralı {normal!r}; beklenen: {list(NORMAL_KURALLARI)}")
    if kayma not in KAYMA_KURALLARI:
        raise ValueError(f"geçersiz kayma kuralı {kayma!r}; beklenen: {list(KAYMA_KURALLARI)}")
    return {"normal": normal, "kayma": kayma}


def isaret_uygula(tau, sigma_n, isaret) -> tuple:
    """Convert channel-convention tau and sigma_n to the stored convention, exactly once."""
    kural = isaret_dogrula(isaret)
    tau3 = np.array(tau, dtype=np.float64, copy=True)
    sn3 = np.array(sigma_n, dtype=np.float64, copy=True)
    if kural["normal"] == "compression_positive":
        sn3 = -sn3
    if kural["kayma"] == "rake_negative":
        tau3 = -tau3
    return tau3, sn3


def s3_mi(isaret) -> bool:
    """True when the declaration is the stored default (tension positive, rake positive)."""
    return isaret_dogrula(isaret) == ISARET_VARSAYILAN
