"""Deney AG testleri: sonlu kaynak çekirdeği (X-b-5,5) yan tezgâhta.

Bilinen cevaplı sentetik dünyalar: kütle korunumu, doğrultulu dizide şerit logL > izotrop,
büyük ebeveyn yoksa X = D1 birebir, defter–koşucu logL kimliği 1e-9.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from knotenlinie.etas import model as MM
from knotenlinie.etas_sonlu.wc94 import kirik_boyu_km
from knotenlinie.etas_sonlu.yon import Yon
from knotenlinie.etas_sonlu.model import serit_noktalari
from knotenlinie.karsilastir import gunluk_ag as AG
from knotenlinie.karsilastir import gunluk_y as GY
from knotenlinie.yan_tezgah import kesme as K
from knotenlinie.yan_tezgah import model as YM
from knotenlinie.yan_tezgah.sonlu import SonluYan, serit_integrali

KUTU = (34.0, 35.5, -119.0, -117.5)
TH = dict(mu=0.02, K=.05, c=.02, alpha=.8, p=1.2, D=0.5, q=1.5, gamma=.05)


def _izgara(kutu, dx=0.1):
    la0, la1, lo0, lo1 = kutu
    enlem = np.round(np.arange(la0, la1, dx), 6)
    boylam = np.round(np.arange(lo0, lo1, dx), 6)
    return pd.DataFrame([(lo, lo + dx, la, la + dx) for la in enlem for lo in boylam],
                        columns=['boylam_min', 'boylam_max', 'enlem_min', 'enlem_max'])


def _model(rmax=100.0, tmax=365.25, epoch='2010-01-01'):
    return YM.YanModel(ad='D1', p=dict(parametreler=dict(TH)), mc0=2.5, b=1.0, hedef=2.5,
                       bolge='scsn', donem_mc=[], hkj=False, m_buyuk=5.0, hkj_gun=30.0,
                       epoch=pd.Timestamp(epoch, tz='UTC'), rmax_km=rmax, tmax_gun=tmax)


def _dizi(aci_deg, n=40, mw_ana=6.3, tohum=5, sacilma_km=0.8):
    """Ana şok + aci_deg doğrultusunda n artçı (ilk 2 gün); geçmiş çerçevesi."""
    rng = np.random.default_rng(tohum)
    met = MM.yerel_metrik(KUTU)
    lon0, lat0 = -118.25, 34.75
    L = float(kirik_boyu_km(mw_ana))
    s = rng.uniform(-L / 2, L / 2, n)
    th = np.radians(aci_deg)
    e = s * np.sin(th) + rng.normal(0, sacilma_km, n)
    k = s * np.cos(th) + rng.normal(0, sacilma_km, n)
    lon = lon0 + e / met.kx
    lat = lat0 + k / met.ky
    t0 = pd.Timestamp('2012-03-01T00:00:00Z')
    zaman = [t0] + [t0 + pd.Timedelta(hours=float(h)) for h in np.sort(rng.uniform(0.1, 48.0, n))]
    d = pd.DataFrame(dict(zaman=zaman, enlem=np.r_[lat0, lat], boylam=np.r_[lon0, lon],
                          derinlik=5.0, mw=np.r_[mw_ana, 2.6 + rng.exponential(0.3, n)]))
    return d, (lon0, lat0), met


def test_serit_kutle_korunumu():
    """Kırpmasız şerit ve izotrop çekirdek aynı toplam kütleyi verir (merkez kutu içinde)."""
    met = MM.yerel_metrik(KUTU)
    xe, ye = MM.hucre_kenarlari(KUTU, 0.1)
    alt = (ye[0], ye[-1], xe[0], xe[-1])
    D, q, L = 1.2, 1.5, 20.0
    lon, lat, nd = serit_noktalari(-118.25, 34.75, 30.0, L, met, D)
    sat = serit_integrali(lon, lat, D, q, alt, 0.1, met, None)
    iso = K.kesik_hucre_integralleri([-118.25], [34.75], D, q, alt, 0.1, metrik=met, rmax_km=None)[0]
    assert nd >= 3 and nd % 2 == 1
    assert abs(sat.sum() - iso.sum()) < 2e-3
    assert 0.95 < sat.sum() <= 1.0 + 1e-9
    # kırpılmış (100 km): kırpılmış çekirdek yeniden normalize edilmez, toplam <= kırpmasız
    satk = serit_integrali(lon, lat, D, q, alt, 0.1, met, 100.0)
    assert satk.sum() <= sat.sum() + 1e-12 and (satk >= 0).all()


def test_dogrultu_pca_hatasi_10_dereceden_az():
    d, (lon0, lat0), met = _dizi(40.0)
    yon = Yon(None, artci_pencere_gun=3.0, artci_min=10)
    a = pd.Timestamp('2012-03-02T00:00:00Z')
    h = d[d.zaman < a].reset_index(drop=True)
    r = yon.yon('b', h, 0, a, met, float(kirik_boyu_km(6.3)))
    assert r is not None
    fark = abs(((r['dogrultu'] - 40.0) + 90.0) % 180.0 - 90.0)
    assert fark < 10.0


def test_serit_logl_izotropu_gecer_dogrultulu_dizide():
    """Çocuklar şerit yoğunluğundan çekilince şerit logL > izotrop (KL > 0), kesmeli de."""
    met = MM.yerel_metrik(KUTU)
    xe, ye = MM.hucre_kenarlari(KUTU, 0.1)
    alt = (ye[0], ye[-1], xe[0], xe[-1])
    Lk = float(kirik_boyu_km(6.5))
    D = 1.0
    lon, lat, _ = serit_noktalari(-118.25, 34.75, 50.0, Lk, met, D)
    for rmax in (None, 100.0):
        sat = serit_integrali(lon, lat, D, 1.5, alt, 0.1, met, rmax)
        iso = K.kesik_hucre_integralleri([-118.25], [34.75], D, 1.5, alt, 0.1, metrik=met,
                                         rmax_km=rmax)[0]
        rng = np.random.default_rng(0)
        p = sat.ravel() / sat.sum()
        n = rng.multinomial(2000, p)
        ll_s = float((n * np.log(np.maximum(sat.ravel() / sat.sum(), 1e-300))).sum())
        ll_i = float((n * np.log(np.maximum(iso.ravel() / iso.sum(), 1e-300))).sum())
        assert ll_s > ll_i + 50.0


def test_x_buyuk_ebeveyn_yoksa_d1_birebir():
    m = _model()
    d, _, _ = _dizi(40.0, mw_ana=4.0)  # M < 5,5: şerit yok
    x = SonluYan(m, m_s=5.5)
    grid = _izgara(KUTU)
    a = pd.Timestamp('2012-03-02T00:00:00Z')
    edges = np.array([2.5, 2.6, 2.8, np.inf])
    h = d[d.zaman < a].reset_index(drop=True)
    b = m.beklenen(a, a + pd.Timedelta(days=1), h, grid, edges)
    c = x.beklenen(a, a + pd.Timedelta(days=1), h, grid, edges)
    assert np.array_equal(b, c)


def test_x_yon_yoksa_izotrop_kalir():
    """M6 ebeveyn var ama <10 artçı: doğrultu yok, çıktı D1 ile aynı."""
    m = _model()
    d, _, _ = _dizi(40.0, n=5)
    x = SonluYan(m, m_s=5.5)
    grid = _izgara(KUTU)
    a = pd.Timestamp('2012-03-02T00:00:00Z')
    edges = np.array([2.5, 2.7, np.inf])
    h = d[d.zaman < a].reset_index(drop=True)
    b = m.beklenen(a, a + pd.Timedelta(days=1), h, grid, edges)
    c = x.beklenen(a, a + pd.Timedelta(days=1), h, grid, edges)
    assert np.array_equal(b, c)


def test_x_serit_dogrultu_boyunca_yogunlasir_ve_kutle_korunur():
    m = _model(rmax=None, tmax=None)
    d, (lon0, lat0), met = _dizi(0.0, n=60, mw_ana=6.5)  # kuzey-güney şerit
    x = SonluYan(m, m_s=5.5)
    grid = _izgara(KUTU)
    a = pd.Timestamp('2012-03-02T12:00:00Z')
    edges = np.array([2.5, np.inf])
    h = d[d.zaman < a].reset_index(drop=True)
    b = m.beklenen(a, a + pd.Timedelta(days=1), h, grid, edges)[:, 0]
    c = x.beklenen(a, a + pd.Timedelta(days=1), h, grid, edges)[:, 0]
    assert abs(c.sum() - b.sum()) / b.sum() < 5e-3  # kütle korunumu (üretkenlik değişmez)
    cx = grid.boylam_min.to_numpy() + 0.05
    cy = grid.enlem_min.to_numpy() + 0.05
    L = float(kirik_boyu_km(6.5))
    dy_km = (cy - lat0) * 111.0
    dx_km = (cx - lon0) * 111.0 * np.cos(np.radians(lat0))
    eksen = (np.abs(dx_km) < 6.0) & (np.abs(dy_km) > 0.3 * L / 2) & (np.abs(dy_km) < 0.9 * L / 2)
    dik = (np.abs(dy_km) < 6.0) & (np.abs(dx_km) > 0.3 * L / 2) & (np.abs(dx_km) < 0.9 * L / 2)
    assert (c - b)[eksen].sum() > 0 and (c - b)[dik].sum() < 0
    assert c.min() >= 0


def test_defter_logl_kosucu_ile_1e9():
    """Koşucu logL farkı (X − D1) ile defterden hesaplanan fark 1e-9 göreli içinde."""
    import tempfile
    from pathlib import Path
    m = _model()
    d, _, _ = _dizi(40.0, n=60, mw_ana=7.0)
    rng = np.random.default_rng(1)
    zb = pd.Timestamp('2012-03-01T00:00:00Z') + pd.to_timedelta(rng.uniform(0, 8, 40), unit='D')
    arka = pd.DataFrame(dict(zaman=zb, enlem=rng.uniform(34.0, 35.4, 40), boylam=rng.uniform(-118.9, -117.6, 40),
                             derinlik=5.0, mw=2.5 + rng.exponential(0.4, 40)))
    d2, _, _ = _dizi(40.0, n=60, mw_ana=7.0, tohum=9)  # sonraki günlerde aynı doğrultuda olaylar
    d2 = d2.iloc[1:].copy()
    d2['zaman'] = pd.Timestamp('2012-03-02T00:00:00Z') + pd.to_timedelta(rng.uniform(0, 6.5, len(d2)), unit='D')
    kat = pd.concat([d, arka, d2]).sort_values('zaman').reset_index(drop=True)
    kat = kat[kat.zaman < pd.Timestamp('2012-03-09T00:00:00Z')]
    x = SonluYan(m, m_s=5.5)
    grid = _izgara(KUTU)
    edges = GY.kenarlar(2.5)
    bas, son = '2012-03-02T00:00:00Z', '2012-03-09T00:00:00Z'
    r1 = GY.gunluk_kos(m, bas, son, kat, grid, edges, (0.0, 30.0))
    r1['ad'] = 'D1'
    rx = GY.gunluk_kos(x, bas, son, kat, grid, edges, (0.0, 30.0))
    assert rx['logL'] > r1['logL'] - 1e-9  # doğrultulu dizide X >= D1 (aynı veri)
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        GY._defter_yaz(td, 'D1', 'scsn', 't', r1, 2.5, 2.6)
        GY._defter_yaz(td, 'X', 'scsn', 't', rx, 2.5, 2.6)
        o1 = pd.read_csv(td / 'D1__scsn__t__olay.csv.gz')
        g1 = pd.read_csv(td / 'D1__scsn__t__gun.csv.gz')
        ox = pd.read_csv(td / 'X__scsn__t__olay.csv.gz')
        gx = pd.read_csv(td / 'X__scsn__t__gun.csv.gz')
    defter_fark = (np.log(ox.lam).sum() - gx.Lam_hedef.sum()) - (np.log(o1.lam).sum() - g1.Lam_hedef.sum())
    kosucu_fark = rx['logL'] - r1['logL']
    assert abs(defter_fark - kosucu_fark) <= 1e-9 * max(1.0, abs(kosucu_fark))
    r = GY.cift_ozet(rx, r1, 2.5, tekrar=50)
    assert np.isclose(kosucu_fark / r['N'], r['IG'], rtol=1e-9, atol=1e-9)


def test_buyuk_ebeveyn_maskesi():
    met = MM.yerel_metrik(KUTU)
    kat = pd.DataFrame(dict(zaman=pd.to_datetime(['2012-01-01T00:00:00Z', '2012-01-10T00:00:00Z',
                                                  '2012-03-01T00:00:00Z', '2012-01-05T00:00:00Z'], utc=True),
                            enlem=[34.5, 34.5, 34.5, 35.6], boylam=[-118.0] * 3 + [-118.0],
                            derinlik=5.0, mw=[6.0, 3.0, 3.0, 3.0]))
    hedef = kat.iloc[[1, 2, 3]].reset_index(drop=True)
    mk = AG.buyuk_ebeveyn_maske(hedef, kat, met, mw_esik=5.5)
    # 1: 9 gün sonra, aynı yer -> evet; 2: 60 gün -> hayır; 3: 4 gün sonra ama ~100 km'den uzak
    assert mk.tolist() == [True, False, False]
