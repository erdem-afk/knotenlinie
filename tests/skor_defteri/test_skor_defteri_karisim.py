"""Sentetik defterlerde karışım logL, ağırlık seçimi ve gün kazancı."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.special import gammaln

from knotenlinie.skor_defteri.defter import Defter
from knotenlinie.skor_defteri.karisim import agirlik_sec, gun_kazanci, log_olabilirlik


def _sentetik():
    """3 gün, 5 olay, 3 model; bilinen λ ve Λ."""
    gunler = ['2011-01-01', '2011-01-02', '2011-01-03']
    olay = pd.DataFrame(dict(
        zaman=pd.to_datetime(['2011-01-01T02:00:00Z', '2011-01-01T04:00:00Z',
                              '2011-01-02T03:00:00Z', '2011-01-03T05:00:00Z',
                              '2011-01-03T06:00:00Z'], utc=True),
        enlem=[40.0] * 5, boylam=[10.0] * 5,
        mw=[3.0, 3.2, 3.1, 4.0, 3.0],
        hucre=[0] * 5, kutu=[1, 3, 2, 11, 1],
        gun=['2011-01-01', '2011-01-01', '2011-01-02', '2011-01-03', '2011-01-03']))
    lam = np.array([[0.10, 0.20, 0.05, 0.40, 0.02],
                    [0.05, 0.05, 0.50, 0.02, 0.10],
                    [0.30, 0.01, 0.20, 0.03, 0.30]])
    gun = pd.DataFrame(dict(gun=gunler,
                            Lam295=[1.0, 2.0, 0.5],
                            Lam395=[0.2, 1.0, 0.1],
                            Lam495=[0.01, 0.05, 0.005]))
    out = []
    for k in range(3):
        o = olay.copy()
        o['lam'] = lam[k]
        out.append(Defter(f'm{k}', o, gun.copy()))
    return out, lam, gun


def _dogrudan(lam, gun, w, alt=2.95):
    mask = np.array([True] * 5)  # tüm olaylar M>=2.95
    Lam = sum(w[k] * gun['Lam295'].to_numpy(float) for k in range(3))
    top = w @ lam
    say = np.ones(5)  # her (gün,hücre,kutu) en çok bir olay
    return float(np.log(top[mask]).sum() - Lam.sum() - gammaln(say + 1).sum())


def test_karisim_logL_dogrudan():
    defterler, lam, gun = _sentetik()
    for w in ([0.5, 0.3, 0.2], [1.0, 0.0, 0.0], [1 / 3, 1 / 3, 1 / 3]):
        assert log_olabilirlik(defterler, w, 2.95) == _dogrudan(lam, gun, np.array(w))


def test_agirlik_sec_en_iyi():
    defterler, lam, gun = _sentetik()
    sonuc = agirlik_sec(defterler, 2.95)
    w = np.array(sonuc['agirliklar'])
    assert np.isclose(w.sum(), 1.0)
    assert (w >= 0).all()
    ref = log_olabilirlik(defterler, w, 2.95)
    assert ref == sonuc['logL'] or abs(ref - sonuc['logL']) < 1e-9
    for deneme in ([1, 0, 0], [0, 1, 0], [0, 0, 1], [1 / 3, 1 / 3, 1 / 3]):
        assert ref >= log_olabilirlik(defterler, deneme, 2.95) - 1e-9


def test_gun_kazanci_ozdeslik():
    defterler, lam, gun = _sentetik()
    k = gun_kazanci(defterler[0:1], defterler[1], 2.95, agirliklar=[1.0])
    sol = log_olabilirlik(defterler[0:1], [1.0], 2.95) - log_olabilirlik([defterler[1]], [1.0], 2.95)
    # log(n!) her iki tarafta aynı (aynı gözlem), bu yüzden fark D.sum()'a eşit.
    assert k['D'].sum() == sol or abs(k['D'].sum() - sol) < 1e-9
    assert k['IG'] >= -10 and k['Lambda_aday'] > 0 and k['Lambda_taban'] > 0
    # Karışım ağırlıklı: olay terimi + integral = IG.
    kk = gun_kazanci(defterler, defterler[2], 2.95, agirliklar=[0.4, 0.4, 0.2])
    assert abs((kk['IG_olay'] + kk['integral']) - kk['IG']) < 1e-12


def test_ozet_blok_se_ve_z():
    """ozet: haftalık blok SE'si blok_ozeti ile aynı gün kazancından gelir; z=IG/SE."""
    from knotenlinie.karsilastir.blok import blok_ozeti
    from knotenlinie.skor_defteri.karisim import ozet
    defterler, lam, gun = _sentetik()
    s = ozet(defterler[:2], defterler[2], 2.95, agirliklar=[0.6, 0.4])
    k = gun_kazanci(defterler[:2], defterler[2], 2.95, agirliklar=[0.6, 0.4])
    b = blok_ozeti(k['D'], k['n'], k['gunler'], n=k['N'])
    assert s['SE_blok'] == b['SE_blok'] and s['z'] == b['z']
    assert abs(s['IG'] - k['D'].sum() / k['N']) < 1e-15


def test_esik_maskesi_ve_olcek():
    """3,95 eşiğinde yalnız M≥3,95 olay girer; ölçek λ ve Λ'yı birlikte çarpar."""
    defterler, lam, gun = _sentetik()
    ll = log_olabilirlik([defterler[0]], [1.0], 3.95)
    olay = np.log(lam[0, 3]) - gun['Lam395'].sum()  # tek M>=3,95 olay: indeks 3 (mw=4,0)
    assert abs(ll - olay) < 1e-12
    c = 2.5
    ll_c = log_olabilirlik([defterler[0]], [1.0], 3.95, olcekler=[c])
    assert abs(ll_c - (np.log(c * lam[0, 3]) - c * gun['Lam395'].sum())) < 1e-12


def test_olaysiz_pencere_tanimsiz_ama_hatasiz():
    """M eşiğinin üstünde olay yoksa IG None döner, hata vermez (N=0)."""
    defterler, lam, gun = _sentetik()
    k = gun_kazanci(defterler[:1], defterler[1], 4.95, agirliklar=[1.0])
    assert k['N'] == 0 and k['IG'] is None
