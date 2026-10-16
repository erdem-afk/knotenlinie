"""Model: kütle korunumu, Poisson kimliği, toplam sınırı, BPT çarpanı, bilinen cevaplı skor."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from shapely.geometry import box

from knotenlinie.fay_zaman import bpt, moment as mom
from knotenlinie.fay_zaman.model import FayKatmani, FayZaman, yil_float
from knotenlinie.uzun_vade.duzgunlestir import UzunVade

KENAR = np.r_[np.round(np.arange(4.95, 9.0, 0.1), 2), np.inf]
BAS, BIT = pd.Timestamp('2011-01-01', tz='UTC'), pd.Timestamp('2016-01-01', tz='UTC')


def _izgara(n=4):
    r = [(10 + 0.1 * i, 10.1 + 0.1 * i, 40 + 0.1 * j, 40.1 + 0.1 * j)
         for i in range(n) for j in range(n)]
    return pd.DataFrame(r, columns=['boylam_min', 'boylam_max', 'enlem_min', 'enlem_max'])


def _tablo(son=np.nan, mdot=2e16, mmax=6.8, poly=None, katman='ISS'):
    poly = poly if poly is not None else box(10.12, 40.12, 10.17, 40.17)
    return pd.DataFrame([dict(id='S1', ad='S1', katman=katman, poligon=poly, alan_km2=100.0,
                              kayma_mm_yil=1.0, mmax=mmax, son_yil=son, ebeveyn=None,
                              kaynak_son=None, mdot=mdot)])


def _bg(iz, rate=1.0):
    sekil = np.full(len(iz), 1.0 / len(iz))
    return UzunVade(sekil, iz, b=1.0, mmin=4.95, rate_ust=rate, ad='bg')


def test_katman_moment_ve_kutle_korunumu():
    iz = _izgara()
    kt = FayKatmani(_tablo(), iz, mfd='gr', b=1.0, bpt=False)
    poi, td = kt.hucre_dizisi(KENAR, yil_float(BAS), 5.0)
    assert poi.sum() == pytest.approx(td.sum(), rel=1e-12)   # BPT kapalı → aynı
    # kutu başına ağırlıklı moment (kutu içi düzgün olmayan GR: ince kenar) ≈ 5 yıl × Ṁ₀
    ince = np.r_[np.round(np.arange(5.45, 6.8 + 1e-9, 0.005), 3), np.inf]
    pr = kt.kaynaklar[0]['parcalar']
    n = mom.kutu_sayilari(pr, kt.kaynaklar[0]['S'], ince, lo=5.45, hi=6.8)
    orta = 0.5 * (ince[:-2] + ince[1:-1])
    moment = (n[:-1] * mom.m0(orta)).sum()
    assert moment == pytest.approx(2e16, rel=2e-3)
    # tüm kütle ızgara içinde → hücre toplamı = kaynak toplamı × 5 yıl
    assert poi.sum() == pytest.approx(kt.kaynaklar[0]['S'] * sum(
        float(mom.parca_integral(p, 5.45, 6.8)) for p in pr) * 5.0, rel=1e-9)


def test_poisson_kimligi_son_olay_yok_ya_da_bpt_kapali():
    iz = _izgara()
    a = FayKatmani(_tablo(son=np.nan), iz, mfd='kar', b=1.0, bpt=True).hucre_dizisi(KENAR, 2011.0, 5.0)
    b = FayKatmani(_tablo(son=1990.0), iz, mfd='kar', b=1.0, bpt=False).hucre_dizisi(KENAR, 2011.0, 5.0)
    assert np.allclose(a[0], a[1]) and np.allclose(b[0], b[1])


def test_bpt_carpani_karakteristik_kisma_uygulanir():
    iz = _izgara()
    kt = FayKatmani(_tablo(son=2005.0), iz, mfd='gr', b=1.0, bpt=True)
    s = kt.kaynaklar[0]
    mu = 1.0 / s['lam_kar']
    g = bpt.carpan(mu, 0.5, 2011.0 - 2005.0, 5.0)
    poi, td = kt.hucre_dizisi(KENAR, 2011.0, 5.0)
    toplam, kar = kt.kutu(KENAR)[0]
    beklenen = ((toplam - kar) + g * kar).sum() * 5.0
    assert td.sum() == pytest.approx(beklenen, rel=1e-10)
    # karakteristik olmayan kutular (Mmax−0,5 altı) değişmez
    j = int(np.searchsorted(KENAR, 6.0))  # 6,0 < Mmax−0,5=6,3
    assert td[:, j].sum() == pytest.approx(poi[:, j].sum(), rel=1e-12)


def test_toplam_siniri_ve_cifte_sayim():
    iz = _izgara()
    for mdot in (1e13, 5e19):   # F<W ve F>W
        bg = _bg(iz, rate=1.0)
        m = FayZaman(FayKatmani(_tablo(mdot=mdot), iz, mfd='gr', b=1.0, bpt=False), bg)
        out = m.beklenen(BAS, BIT, None, iz, KENAR)
        W = bg.beklenen(BAS, BIT, None, iz, KENAR)
        j = int(np.searchsorted(KENAR, 5.45))
        assert np.allclose(out[:, j:].sum(axis=0), W[:, j:].sum(axis=0), rtol=1e-10)  # bölge toplamı W
        assert np.allclose(out[:, :j], W[:, :j], rtol=1e-12)                          # alt kutular aynı
        assert (out >= 0).all()
    # pay üst sınırı 0,5: fay katmanı en çok yarı
    m = FayZaman(FayKatmani(_tablo(mdot=5e19), iz, mfd='gr', b=1.0, bpt=False), _bg(iz), pay_ust=0.5)
    m.beklenen(BAS, BIT, None, iz, KENAR)
    assert min(m.son_tani['olcek']) < 1.0
    bg_pay = np.array(m.son_tani['fac'])
    j = int(np.searchsorted(KENAR, 5.45))
    assert bg_pay[j:j + 3] == pytest.approx([0.5] * 3, rel=1e-9)


def test_fay_yok_ise_arka_plan_aynen():
    iz = _izgara()
    t = _tablo(poly=box(30, 30, 30.1, 30.1))   # tamamen ızgara dışı
    kt = FayKatmani(t, iz, mfd='gr', b=1.0, bpt=False)
    assert kt.atilan['izgara_disi'] == 1 and len(kt.kaynaklar) == 0
    m = FayZaman(kt, _bg(iz))
    assert np.allclose(m.beklenen(BAS, BIT, None, iz, KENAR), _bg(iz).beklenen(BAS, BIT, None, iz, KENAR))


def test_mmax_alti_kaynak_atilir():
    kt = FayKatmani(_tablo(mmax=5.4), _izgara(), mfd='gr', b=1.0)
    assert kt.atilan['mmax_alt'] == 1 and not kt.kaynaklar
