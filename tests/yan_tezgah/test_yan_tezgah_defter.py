"""Skor defteri: yaz-oku turu ve defterden IG'nin koşucu IG'siyle 1e-9 eşleşmesi."""
from __future__ import annotations

import numpy as np
import pandas as pd

from knotenlinie.karsilastir import gunluk_y as G


def _sahte_kosu(ad, lam, gunluk, logL, edges, days, mw):
    n = len(lam)
    olaylar = pd.DataFrame(dict(
        zaman=pd.to_datetime(days[:n], utc=True), enlem=np.full(n, 34.0),
        boylam=np.full(n, -118.0), derinlik=np.full(n, 5.0), mw=mw))
    return dict(ad=ad, events=olaylar, ci=np.zeros(n, int), mi=np.zeros(n, int),
                gun=np.zeros(n, int), lam=np.asarray(lam, float),
                toplam=np.asarray(gunluk, float)[:, None], gunluk=np.asarray(gunluk, float)[:, None],
                logL=float(logL), gun_sayisi=len(days), edges=np.asarray(edges, float),
                days=pd.DatetimeIndex(days))


def test_defter_ig_kimligi(tmp_path):
    days = pd.date_range('2012-01-01', periods=4, freq='D')
    mw = np.array([2.0, 2.1, 2.3, 2.2])
    edges = np.array([2.0, 2.1, 2.2, np.inf])
    lam_a = np.array([0.10, 0.20, 0.30, 0.40])
    lam_b = np.array([0.08, 0.15, 0.25, 0.50])
    gun_a = np.array([0.10, 0.20, 0.30, 0.40])
    gun_b = np.array([0.08, 0.15, 0.25, 0.50])
    logL_a = float(np.log(lam_a).sum() - gun_a.sum())
    logL_b = float(np.log(lam_b).sum() - gun_b.sum())
    a = _sahte_kosu('A', lam_a, gun_a, logL_a, edges, days, mw)
    b = _sahte_kosu('B', lam_b, gun_b, logL_b, edges, days, mw)
    r = G.cift_ozet(a, b, 2.0, tekrar=50)
    assert np.isclose((logL_a - logL_b) / 4, r['IG'], rtol=1e-9, atol=1e-9)
    G._defter_yaz(tmp_path, 'A', 'scsn', 'test', a, 2.0, 2.1)
    G._defter_yaz(tmp_path, 'B', 'scsn', 'test', b, 2.0, 2.1)
    oa = pd.read_csv(tmp_path / 'A__scsn__test__olay.csv.gz')
    ga = pd.read_csv(tmp_path / 'A__scsn__test__gun.csv.gz')
    ob = pd.read_csv(tmp_path / 'B__scsn__test__olay.csv.gz')
    gb = pd.read_csv(tmp_path / 'B__scsn__test__gun.csv.gz')
    logr = np.log(oa.lam.values) - np.log(ob.lam.values)
    ig_defter = logr.mean() - (ga.Lam_hedef.sum() - gb.Lam_hedef.sum()) / len(logr)
    assert np.isclose(ig_defter, r['IG'], rtol=1e-9, atol=1e-9)
