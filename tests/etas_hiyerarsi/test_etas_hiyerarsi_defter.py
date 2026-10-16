"""AE koşucusu: defter ↔ koşucu logL (1e-9), çekirdek temasının doğal parametreye dönüşü, E6 karışımı."""
import numpy as np
import pandas as pd
import pytest

from knotenlinie.etas_hiyerarsi import cekirdek as C
from knotenlinie.karsilastir import gunluk_ae as AE
from knotenlinie.karsilastir.kosucu import Model, kos
from knotenlinie.skor_defteri.defter import alt_indeks
from knotenlinie.skor_defteri.karisim import log_olabilirlik


def _grid():
    return pd.DataFrame(dict(boylam_min=[10.0, 10.1, 10.0, 10.1], boylam_max=[10.1, 10.2, 10.1, 10.2],
                             enlem_min=[40.0, 40.0, 40.1, 40.1], enlem_max=[40.1, 40.1, 40.2, 40.2]))


def _katalog():
    return pd.DataFrame(dict(
        zaman=pd.to_datetime(['2011-01-01T03:00:00Z', '2011-01-02T05:00:00Z', '2011-01-02T06:00:00Z',
                              '2011-01-03T01:00:00Z'], utc=True),
        enlem=[40.05, 40.05, 40.15, 40.05], boylam=[10.05, 10.15, 10.05, 10.05],
        derinlik=[5.0, 8.0, 10.0, 6.0], mw=[3.0, 3.2, 4.0, 3.1]))


def _model(ad, taban, ek):
    ayar = dict(sinir=(10, 10.2, 40, 40.2), baslangic_yil=1990, derinlik_max=30)

    def beklenen(a, b, gecmis, izgara, m_kenarlar):
        gun = (b - a) / pd.Timedelta(days=1)
        alt = np.asarray(m_kenarlar, float)[:-1]
        kutu = taban + ek * (alt >= 3.95 - 1e-9)
        return np.tile(kutu, (len(izgara), 1)) * gun * (1.0 + 0.5 * len(gecmis))
    return Model(ad, beklenen, True, ayar)


def test_defter_uret_kosucuyla_esit():
    grid, cat, edges = _grid(), _katalog(), AE.kenarlar()
    ae, lm = _model('ae', 0.004, 0.002), _model('lm', 0.003, 0.0005)
    bs = ('2011-01-01T00:00:00Z', '2011-01-04T00:00:00Z')
    d = AE.defter_uret(ae, '2011-2015', cat, grid, bas_son=bs, ilerleme=None)
    dl = AE.defter_uret(lm, '2011-2015', cat, grid, bas_son=bs, ilerleme=None)
    kosu = kos([ae, lm], bs[0], bs[1], cat, grid, edges, derinlik=(0, 30))
    assert d.logL == pytest.approx(kosu['ae'].logL, rel=1e-9, abs=1e-9)
    assert log_olabilirlik([d], [1.0], 2.95) == pytest.approx(kosu['ae'].logL, rel=1e-9, abs=1e-9)
    # E6: eşit {AE, LM} defterden = doğrudan karışım koşusu
    w = [0.5, 0.5]
    mix = Model('e6', lambda *x: 0.5 * ae.beklenen(*x) + 0.5 * lm.beklenen(*x), True, ae.gecmis_ayarlari)
    k6 = kos([mix], bs[0], bs[1], cat, grid, edges, derinlik=(0, 30))['e6']
    assert log_olabilirlik([d, dl], w, 2.95) == pytest.approx(k6.logL, rel=1e-9, abs=1e-9)
    assert 'Lam495' in d.gun.columns and d.gun['Lam495'].le(d.gun['Lam395']).all()


def test_tema_dogal_gidis_donus():
    th = dict(mu=.5, K=.03, c=.02, alpha=.55, p=1.15, D=2.1, q=1.7, gamma=.08)
    g = C.tema(th, 2.5)
    d = AE.tema_dogal(g.tolist(), 2.5)
    for k in ('K', 'c', 'alpha', 'p', 'D', 'q', 'gamma'):
        assert d[k] == pytest.approx(th[k], rel=1e-12)


def test_havuz_gevsek_K_kapisi():
    a = dict(ad='a', tema=[1., 2., 3., 4., 5., 6., 7.], tema_var=[1.] * 7, dallanma=.999999, basari=True)
    b = dict(ad='b', tema=[3., 2., 3., 4., 5., 6., 7.], tema_var=[1.] * 7, dallanma=.5, basari=True)
    h = C.havuz([a, b], gevsek=True)
    assert h['tema'][0] == pytest.approx(3.0)      # K_ref yalnız dallanması kritik olmayan b'den
    assert h['maske'] == [True] * 7
    h2 = C.havuz([a], gevsek=True)
    assert h2['maske'][0] is False and h2['tema'][0] is None   # K_ref için bölge kalmadı
    assert C.havuz([a], gevsek=False) is None
