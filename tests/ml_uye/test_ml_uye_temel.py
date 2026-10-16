"""ML üyesi: nedensellik, GR kutu payı, Poisson yansızlığı, defter–koşucu eşleşmesi."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from knotenlinie.karsilastir.kosucu import Model, kos
from knotenlinie.ml_uye.egitim import egit, egitim_gunleri, egitim_kumesi, hedef_olaylari
from knotenlinie.ml_uye.ozellik import ADLAR, OzellikHesap, gun_no
from knotenlinie.ml_uye.uye import MLUye, kutu_payi
from knotenlinie.skor_defteri.defter import kos_defter


def _grid(n=6):
    lon = 10.0 + 0.1 * np.arange(n)
    return pd.DataFrame(dict(boylam_min=lon, boylam_max=lon + 0.1,
                             enlem_min=np.full(n, 40.0), enlem_max=np.full(n, 40.1)))


def _kat(seed=1, n=300, bas='2008-01-01', gun=400):
    rng = np.random.default_rng(seed)
    t0 = pd.Timestamp(bas, tz='UTC')
    z = t0 + pd.to_timedelta(np.sort(rng.random(n) * gun), unit='D')
    return pd.DataFrame(dict(zaman=z, enlem=40.05 + 0 * z.day,
                             boylam=10.0 + 0.6 * rng.random(n), derinlik=rng.uniform(1, 20, n),
                             mw=3.0 + rng.exponential(0.5, n)))


class Sahte:
    """predict: ilk özellikten (10 km, 3,1, 1 gün sayımı) türeyen sabit kural."""
    def predict(self, X):
        return 0.01 + 0.02 * np.nan_to_num(X[:, 0])


def test_nedensellik_gelecek_olay_ozelligi_degistirmez():
    g = _grid()
    h = OzellikHesap(g)
    kat = _kat()
    a = pd.Timestamp('2008-09-01', tz='UTC')
    t0 = gun_no(a)
    kde = np.zeros(len(g), np.float32)
    ol_tam = h.olaylar(kat)
    ol_gecmis = h.olaylar(kat[kat.zaman < a])
    # a ve sonrasındaki olayları bozmak (büyüklük, konum) özelliği değiştirmez
    bozuk = kat.copy()
    s = bozuk.zaman >= a
    bozuk.loc[s, 'mw'] += 3.0
    bozuk.loc[s, 'boylam'] = 10.05
    ol_bozuk = h.olaylar(bozuk)
    X0 = h.hesapla(ol_gecmis, t0, kde)
    for ol in (ol_tam, ol_bozuk):
        np.testing.assert_array_equal(X0, h.hesapla(ol, t0, kde))
    # tam sınırda (a anında) olay da girmez
    ek = pd.concat([kat[kat.zaman < a], pd.DataFrame(dict(zaman=[a], enlem=[40.05], boylam=[10.05],
                                                         derinlik=[5.0], mw=[5.0]))])
    np.testing.assert_array_equal(X0, h.hesapla(h.olaylar(ek), t0, kde))
    assert X0.shape[1] == len(ADLAR)


def test_uye_gecmis_disi_olay_etkisiz():
    g = _grid()
    h = OzellikHesap(g)
    kat = _kat()
    uye = MLUye('t', Sahte(), range(len(ADLAR)), h, np.zeros(len(g)), 1.0)
    a = pd.Timestamp('2008-09-01', tz='UTC')
    e = np.r_[np.round(2.95 + 0.1 * np.arange(61), 2), np.inf]
    l1 = uye.beklenen(a, a + pd.Timedelta(days=1), kat[kat.zaman < a], g, e)
    l2 = uye.beklenen(a, a + pd.Timedelta(days=1), kat, g, e)     # gelecek dahil verilse de kesilir
    np.testing.assert_array_equal(l1, l2)


def test_kutu_payi_gr():
    e = np.r_[np.round(2.95 + 0.1 * np.arange(61), 2), np.inf]
    p = kutu_payi(e, 1.0)
    assert p.sum() == pytest.approx(10 ** (1.0 * (3.1 - 2.95)), rel=1e-12)
    j = int(np.flatnonzero(np.isclose(e, 3.95))[0])
    assert p[j:].sum() == pytest.approx(10 ** (-(3.95 - 3.1)), rel=1e-12)


def test_poisson_yansizlik_bilinen_dunya():
    pytest.importorskip('sklearn')
    """Bilinen oranlı dünya: oran = exp(a + b·x). Ağırlıklı alt örnek yansız, tahmin doğru."""
    rng = np.random.default_rng(0)
    n = 600_000
    x = rng.normal(size=n)
    oran = np.exp(-6.0 + 1.2 * x)
    y = rng.poisson(oran).astype(float)
    p, q = 0.25, 0.25
    pos = y > 0
    ornek = (rng.random(n) < p * q)
    sec = pos | ornek
    w = np.where(pos, 1.0, 1.0 / (p * q))[sec]
    X = np.column_stack([x, rng.normal(size=n)])[sec].astype(np.float32)
    m = egit(X, y[sec].astype(np.float32), w, [0, 1],
             dict(lr=.1, yaprak=8, iter=100, min_yaprak=200))
    mu = m.predict(X)
    assert (w * mu).sum() / (w * y[sec]).sum() == pytest.approx(1.0, abs=0.05)
    # gerçek oranla uyum: eğim yönü ve düzeyi (x bölmelerinde toplam)
    xs = X[:, 0]
    for lo, hi in ((-3, -1), (-1, 0), (0, 1), (1, 3)):
        k = (xs >= lo) & (xs < hi)
        assert (w[k] * mu[k]).sum() / (w[k] * y[sec][k]).sum() == pytest.approx(1.0, abs=0.2)


def test_egitim_gunleri_ve_agirlik():
    g = _grid()
    h = OzellikHesap(g)
    kat = _kat(n=200, bas='2000-01-01', gun=1000)
    d0, d1 = int(gun_no(pd.Timestamp('2000-01-01', tz='UTC'))), int(gun_no(pd.Timestamp('2002-09-01', tz='UTC')))
    pg, ph = hedef_olaylari(h, kat, d0, d1)
    gun, bay = egitim_gunleri(pg, d0, d1, 0.3, 1)
    assert set(np.unique(pg)) <= set(gun)
    ol = h.olaylar(kat)
    kk = {f: np.zeros(len(g), np.float32) for f in range(4)}
    X, y, w, gs, hs = egitim_kumesi(h, ol, pg, ph, gun, bay, kk, None, 0.3, 0.5, 3)
    assert y.sum() == len(pg)
    assert set(np.unique(w[y == 0])) <= {1.0 / (0.3 * 0.5)}


def test_defter_kosucu_logL_esit():
    g = _grid()
    h = OzellikHesap(g)
    kat = _kat(gun=200, bas='2011-01-01')
    uye = MLUye('ml', Sahte(), range(len(ADLAR)), h, np.zeros(len(g)), 0.95)
    ayar = dict(sinir=(9.0, 12.0, 39.0, 41.0), baslangic_yil=2011, derinlik_max=30)
    mod = Model('ml', uye.beklenen, True, ayar)
    e = np.r_[np.round(2.95 + 0.1 * np.arange(61), 2), np.inf]
    t0, t1 = '2011-03-01T00:00:00Z', '2011-03-21T00:00:00Z'
    a = kos([mod], t0, t1, kat, g, e, derinlik=(0, 30))['ml']
    d = kos_defter([mod], t0, t1, kat, g, e, derinlik=(0, 30))['ml']
    assert d.logL == pytest.approx(a.logL, rel=1e-9, abs=1e-9)
    from knotenlinie.skor_defteri.karisim import log_olabilirlik
    assert log_olabilirlik([d], [1.0], 2.95) == pytest.approx(a.logL, rel=1e-9, abs=1e-9)
