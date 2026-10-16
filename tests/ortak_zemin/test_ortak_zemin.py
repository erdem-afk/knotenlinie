"""Bilinen cevaplı oran/logL, mühür-kesim ve Python birimi regresyonları."""
import json

import numpy as np
import pandas as pd
import pytest

from knotenlinie.etas import model as M
from knotenlinie.ortak_zemin.arayuz import DuzETAS, ayar_tabani, model_yukle, omori_kutle
from knotenlinie.ortak_zemin.arka_plan import arka_plan_sec, kde_histogram
from knotenlinie.ortak_zemin.mle import ALFA_PAY, DALLANMA_UST, kisitlar
from knotenlinie.ortak_zemin.ayar import b_ayarla, buyukluk_cozunurlugu, dallanma, tamlik_sec
from knotenlinie.ortak_zemin.dogrulama import poisson_logl
from tests._veri import veri_gerek
from knotenlinie.ortak_zemin.veri import (VERI, IZGARA, KOLONLAR, AYAR_SON, csep_izgara,
                                     hucre_indeks, katalog_dogrula, katalog_oku, sha256)


def grid():
    return pd.DataFrame([[-1, 0, -1, 0], [0, 1, -1, 0], [-1, 0, 0, 1], [0, 1, 0, 1]], columns=IZGARA)


def params(K=0.03):
    box = [-1, 1, -1, 1]
    return {'parametreler': {'mu': 2.0, 'K': K, 'c': 1.0, 'alpha': 0.2, 'p': 2.0,
                            'D': 10.0, 'q': 2.0, 'gamma': 0.0},
            'mc': 2.0, 'b': {'deger': 1.0}, 'kutu': box,
            'ayar_baslangic': '2000-01-01T00:00:00Z', 'normalizasyon': M.NORMALIZASYON,
            'metrik': M.yerel_metrik(box).kayit(),
            'arka_plan': {'x_kenar': [-1, 0, 1], 'y_kenar': [-1, 0, 1],
                          'yogunluk': [[0.25, 0.25], [0.25, 0.25]]}}


def history(time='2010-01-01T00:00:00Z', mw=2.5):
    return pd.DataFrame([[pd.Timestamp(time), 0.0, 0.0, 10.0, mw]], columns=KOLONLAR)


def empty():
    return pd.DataFrame(columns=KOLONLAR)


A, B = pd.Timestamp('2010-01-02', tz='UTC'), pd.Timestamp('2010-01-03', tz='UTC')


def test_omori_analitik():
    assert omori_kutle(1, 2, 1, 2) == pytest.approx(1 / 6)
    assert omori_kutle(1000000, 1000000 + 1e-5, 0.01, 1.01) > 0
    with pytest.raises(ValueError):
        omori_kutle(-1, 2, 1, 2)


def test_duzgun_poisson_toplam_ve_magnitude():
    model = DuzETAS(params(K=0), grid())
    got = model.beklenen(A, B, empty(), grid(), [2, 3, np.inf])
    assert got.shape == (4, 2)
    np.testing.assert_allclose(got, [[0.45, 0.05]] * 4)
    assert got.sum() == pytest.approx(2)


def test_surekli_gr_b_bir_regresyon():
    # b=1 GR'nin deterministik kuantilleri: örnekleme şansı testi gizlemez.
    mc, n = 2.0, 10000
    u = (np.arange(n) + 0.5) / n
    mags = mc - np.log10(1 - u)
    b = b_ayarla(mags, mc)
    assert b['dm'] == 0
    assert b['deger'] == pytest.approx(1, abs=1e-3)
    assert b['beta'] == pytest.approx(np.log(10), abs=3e-3)
    p = params(K=0); p['b'] = b
    got = DuzETAS(p, grid()).beklenen(A, B, empty(), grid(), [mc, mc + 1, np.inf])
    np.testing.assert_allclose(got.sum(axis=0), [1.8, 0.2], atol=1e-4)


@pytest.mark.parametrize('dm', [0.1, 0.01])
def test_yuvarlanmis_gr_gercek_cozunurluk(dm):
    mc, n = 2.0, 10000
    # mc dahil geometrik dağılım: merkezleri dm kadar ayrık GR örneği.
    mags = mc + dm * np.floor(-np.log10(1 - (np.arange(n) + 0.5) / n) / dm)
    b = b_ayarla(mags, mc)
    assert b['dm'] == dm
    assert b['cozunurluk']['n'] == n
    assert b['deger'] == pytest.approx(1, abs=0.005)
    expected = np.log10(np.e) / (mags.mean() - mc + dm / 2)
    assert b['deger'] == pytest.approx(expected)


def test_kismi_izgara_surekli_ve_gecersiz_cozunurluk():
    m = np.r_[np.arange(3, 4, 0.01), 3.123456789]
    resolution = buyukluk_cozunurlugu(m)
    assert resolution['dm'] == 0
    assert 0.98 < resolution['izgara_uyum_paylari']['0.01'] < 1
    for invalid in [[], [3], [3, 3], [3, np.nan], [[3, 4]]]:
        with pytest.raises(ValueError):
            buyukluk_cozunurlugu(invalid)


def test_anne_quadrant_analitik_kutle_ve_kuyruk():
    p = params()
    model = DuzETAS(p, grid())
    got = model.beklenen(A, B, history(), grid(), [2, 3, np.inf])
    G = M.mekan_kutu_integrali([0], [0], [10], 2, p['kutu'], metrik=model.met)[0]
    expected = 2 + 0.03 * 10 ** 0.1 * (1 / 6) * G
    assert got.sum() == pytest.approx(expected, abs=1e-12)
    np.testing.assert_allclose(got[:, 0], expected * 0.9 / 4, atol=1e-12)
    # Alt hücreye koşullama yok: tam uzay kütlesinin dörtte biri.
    sub = model.beklenen(A, B, history(), grid().iloc[[0]], [2, np.inf])
    assert sub.sum() == pytest.approx(expected / 4, abs=1e-12)
    assert G < 1


def test_cache_yeni_anne_ve_gecmis_degisimi():
    model = DuzETAS(params(), grid())
    model.beklenen(A, B, history(), grid(), [2, np.inf])
    before = model._spatial
    assert len(before) == 16  # Kapasite, mevcut anne sayısından ayrı.
    h = pd.concat([history(), history('2010-01-01T12:00:00Z', 3.0)], ignore_index=True)
    actual = model.beklenen(A, B, h, grid(), [2, np.inf])
    assert model._spatial is before  # Her yeni anne tüm matrisi kopyalamaz.
    fresh = DuzETAS(params(), grid()).beklenen(A, B, h, grid(), [2, np.inf])
    np.testing.assert_array_equal(actual, fresh)
    changed = history(mw=3.0)
    np.testing.assert_allclose(model.beklenen(A, B, changed, grid(), [2, np.inf]),
                               DuzETAS(params(), grid()).beklenen(A, B, changed, grid(), [2, np.inf]))


def test_gecmis_sirasi_ve_us_ns():
    model = DuzETAS(params(), grid())
    h = pd.concat([history('2010-01-01T12:00:00Z'), history()], ignore_index=True)
    ns = h.copy(); us = h.copy()
    ns['zaman'] = ns['zaman'].dt.as_unit('ns')
    us['zaman'] = us['zaman'].dt.as_unit('us')
    np.testing.assert_array_equal(model.beklenen(A, B, ns, grid(), [2, np.inf]),
                                  model.beklenen(A, B, us, grid(), [2, np.inf]))


@pytest.mark.parametrize('h', [history('2010-01-02T00:00:00Z'),
                              history('2010-01-03T00:00:00Z', mw=0)])
def test_gelecek_esit_an_da_reddedilir(h):
    with pytest.raises(ValueError, match='geleceği'):
        DuzETAS(params(), grid()).beklenen(A, B, h, grid(), [2, np.inf])


def test_2015_kesim_ve_bos_zaman():
    # Sentetik sınır testi, gerçek kapalı olay okunmaz.
    with pytest.raises(ValueError, match='zaman kapısı'):
        katalog_dogrula(history('2016-01-01T00:00:00Z'))
    h = history(); h['zaman'] = pd.NaT
    with pytest.raises(ValueError, match='zaman kapısı'):
        katalog_dogrula(h)


def test_dallanma_log10_katsayisi():
    th = params()['parametreler']
    assert dallanma(th, 1) == pytest.approx(0.03 / 0.8)
    th['alpha'] = 1.1
    assert np.isinf(dallanma(th, 1))  # alpha<beta tek başına yeterli değil!
    p = params(); p['parametreler']['K'] = 2
    with pytest.raises(ValueError, match='alt-kritik'):
        DuzETAS(p, grid())


def test_poisson_bilinen_logl_ve_sifir():
    assert poisson_logl([2, 1, 0], [1, 2, 0]) == pytest.approx(-3)
    assert poisson_logl([0], [0]) == 0
    assert poisson_logl([0], [1]) == -np.inf
    assert poisson_logl([2], [3]) == pytest.approx(3 * np.log(2) - 2 - np.log(6))
    for r, n in [([-1], [1]), ([np.nan], [0]), ([1], [0.5]), ([1, 2], [1])]:
        with pytest.raises(ValueError):
            poisson_logl(r, n)


def test_magnitude_alt_mixture_reddi():
    model = DuzETAS(params(), grid())
    for edges in [[1.9, 3], [2, 2], [2, np.nan], [2, np.inf, np.inf]]:
        with pytest.raises(ValueError, match='Büyüklük'):
            model.beklenen(A, B, empty(), grid(), edges)


def test_arka_plan_sifir_floor_yok():
    p = params(K=0); p['arka_plan']['yogunluk'] = [[1, 0], [0, 0]]
    got = DuzETAS(p, grid()).beklenen(A, B, empty(), grid(), [2, np.inf])
    np.testing.assert_array_equal(got.ravel(), [2, 0, 0, 0])


def test_hucre_yari_acik_maskesi():
    h = history(); h = pd.concat([h] * 5, ignore_index=True)
    h['boylam'] = [-1, 0, 1, -0.1, -1.1]
    h['enlem'] = [-1, 0, 0, 0, 0]
    np.testing.assert_array_equal(hucre_indeks(h, grid()), [0, 3, -1, 2, -1])
    with pytest.raises(ValueError, match='tekrarlı'):
        hucre_indeks(h, pd.concat([grid(), grid().iloc[[0]]]))


def test_ayar_kesimi_tamlik():
    with pytest.raises(ValueError, match='≤2010'):
        tamlik_sec(history('2011-01-01T00:00:00Z'), 1985, 2)


def test_csep_mask_ve_merkez(tmp_path):
    path = tmp_path / 'forecast.xml'
    path.write_text('''<root xmlns="urn:test"><forecastData>
    <defaultCellDimension lonRange="0.1" latRange="0.1"/>
    <depthLayer min="0" max="70"><cell lon="12" lat="42" mask="1"/>
    <cell lon="13" lat="43" mask="0"/></depthLayer></forecastData></root>''')
    np.testing.assert_allclose(csep_izgara(path).to_numpy(), [[11.95, 12.05, 41.95, 42.05]])


@veri_gerek('ortak/italya_katalog_le2015.csv', 'ortak/italya_izgara.csv',
            'ortak/etas_italya_le2005.json', 'ortak/etas_italya_le2010.json')
def test_teslim_parametreleri_ve_hashlar():
    # Sayım/skor tekrarını koşmaz: teslim edilen iki dosyanın ayar ve hash kapısı.
    ortak = VERI / 'ortak'
    for name, end in [('italya', '2006-01-01'), ('italya', '2011-01-01')]:
        cutoff = pd.Timestamp(end, tz='UTC')
        path = ortak / f'etas_{name}_le{cutoff.year - 1}.json'
        assert path.exists(), f'Teslim eksik: {path}'
        p = json.loads(path.read_text())
        assert p['basari'] and p['alt_kritik'] and p['dallanma'] < 1
        assert p['dallanma'] == pytest.approx(dallanma(p['parametreler'], p['b']['deger']))
        assert pd.Timestamp(p['ayar_max_zaman']) < cutoff
        assert pd.Timestamp(p['ayar_bitis']) == cutoff
        for code, hash_value in p['kod_sha256'].items():
            assert sha256(code) == hash_value
        assert p['katalog_sha256'] == sha256(ortak / f'{name}_katalog_le2015.csv')
        assert p['izgara_sha256'] == sha256(ortak / f'{name}_izgara.csv')
        cat = katalog_oku(ortak / f'{name}_katalog_le2015.csv')
        mags = cat.loc[(cat.zaman >= pd.Timestamp(p['ayar_baslangic'])) &
                       (cat.zaman < cutoff) & (cat.mw >= p['mc']), 'mw'].to_numpy()
        resolution = buyukluk_cozunurlugu(mags)
        assert resolution == p['b']['cozunurluk']
        assert p['b']['dm'] == resolution['dm'] == {'italya': 0.01}[name]
        expected_b = np.log10(np.e) / (mags.mean() - p['mc'] + resolution['dm'] / 2)
        assert p['b']['deger'] == pytest.approx(expected_b)
        assert p['beta'] == pytest.approx(expected_b * np.log(10))
        assert p['b']['beta'] == pytest.approx(p['beta'])
        for row in p['gr_ayar_paylari']:
            assert row['N'] == int(np.sum(mags >= row['m_alt']))
            assert row['gr_pay'] == pytest.approx(10 ** (-expected_b * (row['m_alt'] - p['mc'])))
            assert row['gr_gozlenen_orani'] == pytest.approx(row['gr_pay'] / row['gozlenen_pay'])
        model = model_yukle(name, ortak, son=end)
        h = p['arka_plan']
        assert h['zemin_payi'] > 0
        assert h['kde_n'] == len(mags) == p['ayar_n']
        selection = h['secim']
        assert selection['kurulum_n'] + selection['secim_n'] == len(mags)
        assert pd.Timestamp(selection['secim_bitis_haric']) == cutoff
        assert pd.Timestamp(selection['kurulum_bitis_haric']) == cutoff - pd.DateOffset(years=5)
        assert pd.Timestamp(selection['yeniden_kurulum_max_zaman']) < cutoff
        assert selection['en_iyi'] == max(selection['adaylar'], key=lambda r: r['logL_konum'])
        assert (model._arka_plan(model.izgara.to_numpy()) > 0).all()
        with pytest.raises(ValueError, match='ayar bitişinden'):
            model.beklenen(cutoff - pd.Timedelta(days=1), cutoff, empty(), model.izgara, [4.95, np.inf])
