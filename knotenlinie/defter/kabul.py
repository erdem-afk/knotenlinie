"""Acceptance gate and seal block: what may be published, and under which proof.

A channel does not enter the ledger before it meets its declared acceptance
number; if no published number exists, an independent second calculation
(analytic or another software) counts as acceptance, and that is stated explicitly.
The gate is data, not a comment: an acceptance record that did not pass, names an
unknown kind of evidence, or carries no evidence at all is a hard error, raised by the
writer before any file is created.

The seal enters as: a channel declaring
``deprem_girdisi=True`` must carry a clean ``scripts/muhur.py`` attestation, otherwise
the writer refuses.
"""
from __future__ import annotations

from typing import Dict

KABUL_TURLERI = ("yayimlanmis", "bagimsiz_hesap")


class KabulHatasi(ValueError):
    """Acceptance gate: the channel did not pass its acceptance number."""


def kabul_dogrula(kabul) -> Dict[str, object]:
    """An acceptance record must have passed and must name its evidence."""
    if not isinstance(kabul, dict):
        raise KabulHatasi("Kabul kaydı yok; kanal kabul sayısını tutturmadan yayımlanamaz")
    if kabul.get("gecti") is not True:
        raise KabulHatasi(f"Kabul kapısı geçilmedi: gecti={kabul.get('gecti')!r}")
    if kabul.get("tur") not in KABUL_TURLERI:
        raise KabulHatasi(
            f"Kabul türü geçersiz ({kabul.get('tur')!r}); "
            f"yayımlanmış sayı ya da bağımsız ikinci hesap olmalı: {list(KABUL_TURLERI)}"
        )
    if not str(kabul.get("kanit", "")).strip():
        raise KabulHatasi("Kabul kaydında kanıt (kanit) boş")
    return kabul


def muhur_blogu(deprem_girdisi: bool, muhur) -> Dict[str, object]:
    """Seal block; an earthquake-fed channel needs a clean attestation."""
    if not deprem_girdisi:
        return {"gerekli": False, "durum": None, "komut": None, "kok": None}
    if not isinstance(muhur, dict) or muhur.get("durum") != "clean":
        raise KabulHatasi(
            "deprem_girdisi=True ama temiz mühür kanıtı yok; "
            "scripts/muhur.py çıktısı 'durum': 'clean' olarak verilmeli"
        )
    for alan in ("komut", "kok", "tarih"):
        if not str(muhur.get(alan, "")).strip():
            raise KabulHatasi(f"mühür kanıtında '{alan}' boş")
    return {
        "gerekli": True,
        "durum": "clean",
        "komut": str(muhur["komut"]),
        "kok": str(muhur["kok"]),
        "tarih": str(muhur["tarih"]),
    }
