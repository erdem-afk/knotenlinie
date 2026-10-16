"""Ortak taban korunumu, bilinen T/IG ve yalnız ayar penceresinde seçim."""
import numpy as np
import pandas as pd
import pytest
from scipy import stats

from knotenlinie.crs.dalga2 import alici_paylari, melez, skor_ozeti, olc, girdi_kontrol
from knotenlinie.crs.italya import etas_gunluk, crs_gunluk, poisson_logl
from knotenlinie.crs.arayuz import Model
from tests.crs.test_crs import fixture


def test_melez_ortak_arka_plani_korur():
    e = np.array([[3., 5.], [4., 6.]])
    b = np.array([1., 2.])
    pay = np.eye(2)
    r = np.array([[2., .5], [3., .25]])
    np.testing.assert_array_equal(melez(e, b, r, pay, 0.), e)
    np.testing.assert_allclose(melez(e, b, np.ones((2, 2)), pay, 1.), e)
    expected = e+.25*b*(r-1)
    np.testing.assert_allclose(melez(e, b, r, pay, .25), expected)
    # ETAS tetikleme aynı: toplamdan modüle edilen arka planı çıkar.
    got = melez(e, b, r, pay, 1.)
    np.testing.assert_allclose(got-b*r, e-b)
    with pytest.raises(ValueError):
        melez(e, b, r, pay*.5, 1.)
    with pytest.raises(ValueError):
        melez(e, [10., 20.], r, pay, .25)


def test_bilinen_ig_se_p_integral_ve_bos_hucreler():
    # İlk hücrede iki olay: her olay ayrı eşleşme; ikinci hücre boş.
    n = np.array([[2, 0], [0, 1]])
    e = np.array([[2., 1.], [1., 1.]])
    base = np.ones((2, 2))
    result = skor_ozeti([2., 2., 1.], [1., 1., 1.], e.sum(), base.sum())
    expected_ig = (2*np.log(2)-1)/3
    expected_se = np.log(2)/3
    assert result['N'] == 3
    np.testing.assert_allclose(result['IG'], expected_ig)
    np.testing.assert_allclose(result['SE'], expected_se)
    np.testing.assert_allclose(result['p'], 2*stats.t.sf(abs(expected_ig/expected_se), 2))
    np.testing.assert_allclose(result['IG'], (poisson_logl(e, n)-poisson_logl(base, n))/3)


def test_esit_modeller_ve_tek_olay():
    result = skor_ozeti([1., 2.], [1., 2.], 5., 5.)
    assert result['IG'] == result['SE'] == 0.
    assert result['p'] == 1.
    assert result['GA95'] == [0., 0.]
    result = skor_ozeti([2.], [1.], 5., 4.)
    assert result['SE'] is None and result['p'] is None
    assert skor_ozeti([], [], 1., 1.)['IG'] is None
    with pytest.raises(ValueError):
        skor_ozeti([0.], [1.], 1., 1.)


def test_toplu_yol_01derece_tek_gun_arayuzle_ayni():
    f, h, _, p = fixture()
    g = pd.DataFrame({'boylam_min': [12., 14.], 'boylam_max': [12.1, 14.1],
                      'enlem_min': [42., 44.], 'enlem_max': [42.1, 44.1]})
    base = Model(p, h, f)
    days = pd.date_range('2009-01-01T00:00:00Z', periods=5, freq='D')
    e, u, _ = etas_gunluk(base, h, g, days)
    # CRS tarafında ayrı KDE yapılmaz: arka plan doğrudan taban μu.
    pay = alici_paylari(g, f)
    ts = pd.DatetimeIndex(['2009-01-01T12:00:00Z'])
    ds = np.array([[10000., -20000.]])
    ratios = crs_gunluk(days, ts, ds, 100000., f.tau_dot_pa_gun.to_numpy())
    got = melez(e, p['mu']*u, ratios, pay, .25)
    for i, a in enumerate(days):
        daily_base = base.beklenen(a, a+pd.Timedelta(days=1), h[h.zaman < a], g, [4., np.inf])[:, 0]
        np.testing.assert_allclose(got[i], daily_base+.25*p['mu']*u*(pay @ ratios[i]-1), rtol=2e-12)
    # Blok başlangıcı kayması Omori yaşını değiştirmesin.
    e2 = etas_gunluk(base, h, g, days[2:])[0]
    np.testing.assert_allclose(e2, e[2:], rtol=2e-12)


def ornek():
    f, _, _, _ = fixture()
    g = pd.DataFrame({'boylam_min': [12., 14.], 'boylam_max': [12.1, 14.1],
                      'enlem_min': [42., 44.], 'enlem_max': [42.1, 44.1]})
    d = pd.DataFrame({'zaman': pd.to_datetime(['2010-12-30T12:00:00Z',
                                               '2012-01-02T12:00:00Z',
                                               '2012-01-02T13:00:00Z']),
                      'enlem': [42.05]*3, 'boylam': [12.05]*3,
                      'derinlik': [8.]*3, 'mw': [5.]*3})
    return f, g, d


def kos(d, f, g, blok=128, neutral=False):
    calls = []
    def etas(days):
        calls.append(len(days))
        return np.full((len(days), len(g)), 2.)
    def kaynak(history, faults):
        first = history.iloc[0].zaman
        return pd.DatetimeIndex([first]), np.full((1, len(faults)), 0. if neutral else -100000.)
    result = olc(d, g, f, baslangic='2010-12-30T00:00:00Z', m0=4., b=1.,
                 arka_plan=np.full(len(g), 2.), etas_blok=etas,
                 asigmalar=(100000.,), agirliklar=(0., .25, 1.),
                 blok_gun=blok, kaynak_hesabi=kaynak)
    assert max(calls) <= blok
    return result


def test_secim_yalniz_2010_ve_blok_boyundan_bagimsiz():
    f, g, d = ornek()
    first = kos(d, f, g)
    assert first['crs_secili']['agirlik'] == 1.
    assert first['N'] == 2  # aynı gün/hücrede iki doğrulama olayı
    altered = d.copy()
    altered.loc[1:, 'mw'] = 4.0
    second = kos(altered, f, g)
    assert first['crs_secili'] == second['crs_secili']
    assert second['N'] == 0 and second['IG'] is None
    other_block = kos(d, f, g, blok=257)
    for key in ('IG', 'SE', 'p', 'beklenen_toplam', 'beklenen_taban', 'logL'):
        np.testing.assert_allclose(first[key], other_block[key], atol=1e-10)
    assert first['tarama'] == other_block['tarama']
    np.testing.assert_allclose(first['IG'], (first['logL']-first['logL_taban'])/first['N'], atol=1e-10)
    # Seyrek kompansatörün bağımsız tam hücre×gün hesabıyla eşitliği.
    days = pd.date_range('2010-12-30T00:00:00Z', '2015-12-31T00:00:00Z', freq='D')
    ri = crs_gunluk(days, pd.DatetimeIndex([d.zaman.iloc[0]]),
                    np.full((1, len(f)), -100000.), 100000., f.tau_dot_pa_gun.to_numpy())
    dense = melez(np.full((len(days), len(g)), 2.), np.full(len(g), 2.),
                  ri, alici_paylari(g, f), 1.)
    counts = np.zeros((len(days), len(g)), dtype=int)
    counts[int((d.zaman.iloc[1]-days[0])/pd.Timedelta(days=1)), 0] = 2
    mask = days >= pd.Timestamp('2011-01-01T00:00:00Z')
    np.testing.assert_allclose(first['beklenen_toplam'], (dense[mask]*10**(-.95)).sum(), atol=1e-10)
    np.testing.assert_allclose(first['logL'], poisson_logl(dense[mask]*10**(-.95), counts[mask]), atol=1e-10)


def test_notr_dunyada_secilen_null_tam_esit():
    f, g, d = ornek()
    result = kos(d, f, g, neutral=True)
    assert result['crs_secili']['agirlik'] == 0.
    assert result['IG'] == result['SE'] == 0.
    assert result['p'] == 1.
    assert result['beklenen_toplam'] == result['beklenen_taban']
    assert result['logL'] == result['logL_taban']


def test_girdi_kapisi_ve_eksik_dosya(tmp_path):
    _, missing = girdi_kontrol(tmp_path)
    assert len(missing) == 3
    (tmp_path/'italya_katalog_le2015.csv').write_text('zaman,enlem,boylam,derinlik,mw\n')
    _, missing = girdi_kontrol(tmp_path)
    assert [p.rsplit('/', 1)[-1] for p in missing] == ['etas_italya_le2010.json', 'italya_izgara.csv']


def test_gelecek_baslangic_ve_gecersiz_agirlik_reddi():
    f, g, d = ornek()
    with pytest.raises(ValueError):
        olc(d, g, f, baslangic='2011-01-01T00:00:00Z', m0=4., b=1.,
            arka_plan=np.ones(2), etas_blok=lambda days: np.ones((len(days), 2)))
    with pytest.raises(ValueError):
        olc(d, g, f, baslangic='2010-12-30T00:00:00Z', m0=4., b=1.,
            arka_plan=np.ones(2), etas_blok=lambda days: np.ones((len(days), 2)),
            agirliklar=(.25, 1.))
