"""Ortak `beklenen` imzası; seçilmiş sonlu-kaynak varyantını X/SECIM.json'dan yükler.

Seçim kaydı `records/X/SECIM.json` içinde durur (`parametreler`, `gcmt`, `tip`, `m_s`);
göreli yollar veri köküne (`KNOTENLINIE_DATA`) göre çözülür.  Kayıt yoksa model yüklenmez.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from knotenlinie.ortak_zemin.veri import VERI, izgara_dogrula

from . import gcmt as _gcmt
from .model import SonluETAS
from .yon import Yon

from knotenlinie.yollar import KAYIT  # noqa: E402

SECIM = KAYIT / 'X/SECIM.json'


def _veri_yolu(yol):
    """A record path: absolute as written, otherwise relative to the data root."""
    p = Path(yol)
    return p if p.is_absolute() else VERI / p


def yukle(secim=SECIM):
    """`SECIM.json`'dan tek bir `SonluETAS` kurar."""
    s = json.loads(Path(secim).read_text())
    grid = pd.read_csv(VERI / 'ortak/italya_izgara.csv')
    izgara_dogrula(grid)
    p = json.loads(_veri_yolu(s['parametreler']).read_text())
    gdf = _gcmt.oku(_veri_yolu(s['gcmt'])) if s.get('gcmt') else None
    yon = Yon(gdf, **s.get('yon_ayari', {}))
    return SonluETAS(p, grid, yon=yon, tip=s['tip'], m_s=float(s['m_s']),
                     adim=int(s.get('adim', 32)), nesil=int(s.get('nesil', 10)))


_MODEL = None


def beklenen(baslangic, bitis, gecmis, izgara, m_kenarlar):
    """Ortak imza; geçmişi `ebeveynler` ile süzer (R-ortak ile aynı)."""
    global _MODEL
    if _MODEL is None:
        _MODEL = yukle()
    return _MODEL.beklenen(baslangic, bitis, gecmis, izgara, m_kenarlar)
