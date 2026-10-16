"""Sentetik bilinen dünyada defter ↔ koşucu eşitliği."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from knotenlinie.karsilastir.kosucu import Model, kos, karsilastir
from knotenlinie.skor_defteri.defter import alt_indeks, defter_oku, defter_yaz, kos_defter


def _grid():
    return pd.DataFrame(dict(
        boylam_min=[10.0, 10.1, 10.0, 10.1],
        boylam_max=[10.1, 10.2, 10.1, 10.2],
        enlem_min=[40.0, 40.0, 40.1, 40.1],
        enlem_max=[40.1, 40.1, 40.2, 40.2]))


def _edges():
    return np.r_[np.round(2.95 + 0.1 * np.arange(21), 2), np.inf]


def _katalog():
    return pd.DataFrame(dict(
        zaman=pd.to_datetime(['2011-01-01T03:00:00Z', '2011-01-02T05:00:00Z',
                              '2011-01-02T06:00:00Z', '2011-01-03T01:00:00Z'], utc=True),
        enlem=[40.05, 40.05, 40.15, 40.05],
        boylam=[10.05, 10.15, 10.05, 10.05],
        derinlik=[5.0, 8.0, 10.0, 6.0],
        mw=[3.0, 3.2, 4.0, 3.1]))


def test_defter_kosucu_esit():
    grid, edges, cat = _grid(), _edges(), _katalog()
    shape = (len(grid), len(edges) - 1)
    a = np.zeros(shape) + 0.01
    a[:, alt_indeks(3.95):] += 0.001
    b = np.zeros(shape) + 0.02
    b[:, alt_indeks(3.95):] += 0.0005
    # Statik model: dönem toplamı döner; koşucu gün sayısına böler.
    def mk(arr):
        def beklenen(baslangic, bitis, gecmis, izgara, m_kenarlar):
            gun = int((bitis - baslangic) / pd.Timedelta(days=1))
            return arr * gun
        return beklenen
    m1 = Model('m1', mk(a), zamana_bagli=False)
    m2 = Model('m2', mk(b), zamana_bagli=False)
    t0, t1 = '2011-01-01T00:00:00Z', '2011-01-04T00:00:00Z'
    kosu = kos([m1, m2], t0, t1, cat, grid, edges, derinlik=(0, 30))
    kars = karsilastir(kosu['m1'], kosu['m2'])
    defter = kos_defter([m1, m2], t0, t1, cat, grid, edges, derinlik=(0, 30))
    for ad in ('m1', 'm2'):
        assert defter[ad].logL == pytest.approx(kosu[ad].logL, rel=1e-12, abs=1e-12)
        assert np.allclose(defter[ad].olay['lam'].to_numpy(float), kosu[ad].olay_oranlari,
                           rtol=1e-12, atol=1e-14)
        assert np.allclose(defter[ad].beklenen, kosu[ad].beklenen, rtol=1e-12, atol=1e-14)
    from knotenlinie.skor_defteri.karisim import log_olabilirlik
    fark_defter = (log_olabilirlik([defter['m1']], [1.0], 2.95)
                   - log_olabilirlik([defter['m2']], [1.0], 2.95))
    fark_kosucu = kosu['m1'].logL - kosu['m2'].logL
    assert fark_defter == pytest.approx(fark_kosucu, rel=1e-12, abs=1e-12)
    assert kars['IG'] == pytest.approx(fark_kosucu / kars['N'], rel=1e-12, abs=1e-12)


def test_defter_tur_donus(tmp_path):
    grid, edges, cat = _grid(), _edges(), _katalog()
    def beklenen(baslangic, bitis, gecmis, izgara, m_kenarlar):
        return np.full((len(grid), len(edges) - 1), 0.02)
    d = kos_defter([Model('m', beklenen, zamana_bagli=False)], '2011-01-01T00:00:00Z',
                   '2011-01-04T00:00:00Z', cat, grid, edges, derinlik=(0, 30))['m']
    defter_yaz(d, tmp_path, '2011-2015')
    ok = defter_oku('m', tmp_path, '2011-2015')
    assert ok.N == d.N
    assert np.allclose(ok.olay['lam'], d.olay['lam'])
    assert np.allclose(ok.gun[['Lam295', 'Lam395', 'Lam495']],
                       d.gun[['Lam295', 'Lam395', 'Lam495']])
    assert np.allclose(ok.gun['Lam295'], ok.gun['Lam395'] + ok.gun['Lam295'] - ok.gun['Lam395'])


def _dinamik(taban_a, ek_a, taban_b, ek_b):
    """Geçmişe bağlı iki model: oran geçmişteki olay sayısıyla artar; kutu başına tanımlı."""
    def mk(taban, ek):
        def beklenen(baslangic, bitis, gecmis, izgara, m_kenarlar):
            gun = (bitis - baslangic) / pd.Timedelta(days=1)
            alt = np.asarray(m_kenarlar, float)[:-1]
            kutu = taban + ek * (alt >= 3.95 - 1e-9)
            return np.tile(kutu, (len(izgara), 1)) * gun * (1.0 + 0.5 * len(gecmis))
        return beklenen
    return mk(taban_a, ek_a), mk(taban_b, ek_b)


def test_dinamik_esik_ve_karisim_kosucuyla_esit():
    """3,95 eşiği ve doğrusal karışım: defterden hesap, koşucu çıktısıyla 1e-9 içinde."""
    from knotenlinie.skor_defteri.karisim import log_olabilirlik, ozet
    grid, edges, cat = _grid(), _edges(), _katalog()
    fa, fb = _dinamik(0.004, 0.002, 0.003, 0.0005)
    ayar = dict(sinir=(10, 10.2, 40, 40.2), baslangic_yil=1990, derinlik_max=30)
    t0, t1 = '2011-01-01T00:00:00Z', '2011-01-04T00:00:00Z'
    ma, mb = Model('a', fa, True, ayar), Model('b', fb, True, ayar)
    w = [0.3, 0.7]
    mix = Model('mix', lambda *x: w[0] * fa(*x) + w[1] * fb(*x), True, ayar)
    ded = kos_defter([ma, mb], t0, t1, cat, grid, edges, derinlik=(0, 30))
    for alt in (2.95, 3.95):
        e = edges[alt_indeks(alt):]
        kosu = kos([ma, mb, mix], t0, t1, cat, grid, e, derinlik=(0, 30))
        for ad in ('a', 'b'):
            assert log_olabilirlik([ded[ad]], [1.0], alt) == pytest.approx(kosu[ad].logL, rel=1e-9, abs=1e-9)
        assert log_olabilirlik([ded['a'], ded['b']], w, alt) == pytest.approx(kosu['mix'].logL, rel=1e-9, abs=1e-9)
        kars = karsilastir(kosu['mix'], kosu['b'])
        s = ozet([ded['a'], ded['b']], ded['b'], alt, agirliklar=w)
        assert s['N'] == kars['N']
        assert s['IG'] == pytest.approx(kars['IG'], rel=1e-9, abs=1e-12)
        assert s['IG_olay'] == pytest.approx(kars['IG_olay'], rel=1e-9, abs=1e-12)
        assert s['Lambda_aday'] == pytest.approx(kosu['mix'].beklenen.sum(), rel=1e-12)


def test_olcek_kosucu_dogrudan_esit():
    """Sabit ölçek c: defterden logL, S'nin analitik ölçeğiyle ve doğrudan koşuyla aynı."""
    from knotenlinie.skor_defteri.karisim import log_olabilirlik
    grid, edges, cat = _grid(), _edges(), _katalog()
    fa, _ = _dinamik(0.01, 0.0, 0.01, 0.0)
    ayar = dict(sinir=(10, 10.2, 40, 40.2), baslangic_yil=1990, derinlik_max=30)
    t0, t1 = '2011-01-01T00:00:00Z', '2011-01-04T00:00:00Z'
    c = 1.7
    ded = kos_defter([Model('a', fa, True, ayar)], t0, t1, cat, grid, edges, derinlik=(0, 30))['a']
    dogrudan = kos([Model('ac', lambda *x: c * fa(*x), True, ayar)], t0, t1, cat, grid, edges,
                   derinlik=(0, 30))['ac']
    assert log_olabilirlik([ded], [1.0], 2.95, olcekler=[c]) == pytest.approx(dogrudan.logL, rel=1e-9, abs=1e-9)
