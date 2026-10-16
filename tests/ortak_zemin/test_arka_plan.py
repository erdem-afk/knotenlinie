"""KDE kütle/birim, zamansal sızıntı ve alt-kritik optimizasyon regresyonları."""
import json
import numpy as np
import pandas as pd
import pytest
from scipy.special import ndtr

from knotenlinie.etas import model as M
from knotenlinie.ortak_zemin import ayar
from knotenlinie.ortak_zemin.arayuz import DuzETAS, ayar_tabani
from knotenlinie.ortak_zemin.arka_plan import arka_plan_sec, kde_histogram
from knotenlinie.ortak_zemin.mle import DALLANMA_UST, ALFA_PAY, kisitlar
from knotenlinie.ortak_zemin.veri import IZGARA, KOLONLAR, VERI, katalog_oku
from tests._veri import veri_gerek

BOX = (-1., 1., -1., 1.)


def sample():
    years = [1990, 1999, 2001, 2003, 2005, 2008, 2012]
    return pd.DataFrame([[pd.Timestamp(f'{y}-07-01', tz='UTC'),
                          -0.5 + 0.1 * i, -0.4 + 0.1 * i, 10., 3.2 + 0.1 * i]
                         for i, y in enumerate(years)], columns=KOLONLAR)


def test_kde_analitik_integral_ve_zemin():
    h, eps = 20., 0.02
    hist = kde_histogram([0], [0], BOX, h, eps, dx=1)
    density = hist['yogunluk']
    np.testing.assert_allclose(density, 0.25, atol=1e-14)
    assert density.sum() == pytest.approx(1)
    # Simetri olmayan anne: Gauss CDF'si ile bağımsız tek-hücre hesabı.
    hist = kde_histogram([0.2], [-0.3], BOX, h, eps, dx=1)
    met = M.yerel_metrik(BOX)
    px = (ndtr((0 - 0.2) * met.kx / h) - ndtr((-1 - 0.2) * met.kx / h)) / (
        ndtr((1 - 0.2) * met.kx / h) - ndtr((-1 - 0.2) * met.kx / h))
    py = (ndtr((0 + 0.3) * met.ky / h) - ndtr((-1 + 0.3) * met.ky / h)) / (
        ndtr((1 + 0.3) * met.ky / h) - ndtr((-1 + 0.3) * met.ky / h))
    assert hist['yogunluk'][0, 0] == pytest.approx((1 - eps) * px * py + eps / 4)
    assert hist['yogunluk'].sum() == pytest.approx(1)
    assert (hist['yogunluk'] >= eps / 4).all()


def test_kde_kutu_siniri_blok_ve_kutle():
    x = [-1, 1, 0.9, -0.5]; y = [-1, 1, -0.3, 0.6]
    a = kde_histogram(x, y, BOX, 5, 0.01, blok=1)
    b = kde_histogram(x, y, BOX, 5, 0.01, blok=128)
    np.testing.assert_allclose(a['yogunluk'], b['yogunluk'], atol=1e-14)
    assert (a['yogunluk'] * np.diff(a['x_kenar'])[:, None] * np.diff(a['y_kenar'])[None, :]).sum() == pytest.approx(1)
    for x, y, band, eps in [([], [], 5, .1), ([2], [0], 5, .1), ([0], [0], 0, .1),
                            ([0], [0], 5, 0), ([np.nan], [0], 5, .1)]:
        with pytest.raises(ValueError):
            kde_histogram(x, y, BOX, band, eps)


def test_kde_secim_yalniz_zamansal_holdout_ve_refit():
    d = sample(); d = d[d.zaman < pd.Timestamp('2011', tz='UTC')]
    got = arka_plan_sec(d, BOX, '2011-01-01', bantlar=(10., 40.), zeminler=(.01, .1))
    s = got['secim']
    assert s['kurulum_n'] == 5 and s['secim_n'] == 1
    assert got['kde_n'] == 6
    train, hold = d.iloc[:5], d.iloc[5:]
    scores = []
    for h in (10., 40.):
        for eps in (.01, .1):
            hist = kde_histogram(train.boylam, train.enlem, BOX, h, eps)
            u = M.arka_plan_degeri(hold.boylam.to_numpy(), hold.enlem.to_numpy(), hist)
            scores.append(float(np.log(u / M.yerel_metrik(BOX).jakobiyen).sum()))
    np.testing.assert_allclose([r['logL_konum'] for r in s['adaylar']], scores)
    assert s['en_iyi']['logL_konum'] == max(scores)
    refit = kde_histogram(d.boylam, d.enlem, BOX, got['bant_km'], got['zemin_payi'])
    np.testing.assert_array_equal(got['yogunluk'], refit['yogunluk'])
    with pytest.raises(ValueError, match='son sınırını'):
        arka_plan_sec(sample(), BOX, '2011-01-01')
    with pytest.raises(ValueError, match='2006/2011'):
        arka_plan_sec(d, BOX, '2016-01-01')


def test_ayar_son_siniri_b_kde_ve_MLEye_sizar_mi(tmp_path, monkeypatch):
    d = pd.concat([sample(), sample()], ignore_index=True)
    grid = pd.DataFrame([[-1, 0, -1, 0], [0, 1, -1, 0], [-1, 0, 0, 1], [0, 1, 0, 1]], columns=IZGARA)
    path = tmp_path / 'italya_katalog_le2015.csv'
    d.to_csv(path, index=False)
    grid.to_csv(tmp_path / 'italya_izgara.csv', index=False)
    monkeypatch.setattr(ayar, 'tamlik_sec', lambda *args: {'mc': 3.1})
    captures = []
    def fake_mle(t, mags, x, y, mc, beta, t0, T, box, u, **kw):
        captures.append((t.copy(), mags.copy(), u.copy(), T, beta))
        return {'basari': True, 'parametreler': {'mu': .1, 'K': .001, 'c': 1.,
                    'alpha': .1, 'p': 2., 'D': 10., 'q': 2., 'gamma': 0.}}
    monkeypatch.setattr(M, 'mle_uzay_zaman', fake_mle)
    first = ayar.ayarla('italya', tmp_path, son='2006-01-01')
    d.loc[d.zaman >= pd.Timestamp('2006', tz='UTC'), ['mw', 'boylam']] = [9.99, -0.9]
    d.to_csv(path, index=False)
    second = ayar.ayarla('italya', tmp_path, son='2006-01-01')
    assert first['b'] == second['b']
    assert first['arka_plan']['secim'] == second['arka_plan']['secim']
    assert first['ayar_n'] == second['ayar_n'] == 10
    assert first['arka_plan']['secim']['kurulum_n'] == 4
    assert first['arka_plan']['secim']['secim_n'] == 6
    for left, right in zip(captures[0], captures[1]):
        np.testing.assert_array_equal(left, right)


def test_alt_kritik_kisitlar_gercek_dallanmayla_ayni():
    b, beta = 1., np.log(10)
    for K, alpha in [(.1, .3), (1., .8), (.01, 1.1)]:
        th = np.array([.2, K, 1., alpha, 2., 10., 2., .1])
        x = M._theta_dan_x(th, beta)
        g = kisitlar(x, beta, b)
        assert g[0] == pytest.approx(b - alpha - ALFA_PAY)
        if alpha < b:
            n = K / (1 - alpha)
            assert g[1] == pytest.approx(np.log(DALLANMA_UST / n))
        assert bool((g >= 0).all()) == bool(alpha <= b - ALFA_PAY and K / max(b - alpha, 1e-12) <= DALLANMA_UST)


def test_kde_dis_u_MLE_kompansator_birim_esligi():
    hist = kde_histogram([-.2], [.3], BOX, 20., .05)
    xs, ys = np.array([-.2, .8]), np.array([.3, -.8])
    u = M.arka_plan_degeri(xs, ys, hist)
    th = np.array([2., 0., 1., .2, 2., 10., 2., 0.])
    got = M.logL_uzay_zaman(th, [1., 2.], [3., 3.], xs, ys, 3., 2.3, 0., 5., BOX, u_olay=u)
    expected = np.log(2 * u / M.yerel_metrik(BOX).jakobiyen).sum() - 2 * 5
    assert got == pytest.approx(expected)


@veri_gerek('ortak/italya_katalog_le2015.csv', 'ortak/italya_izgara.csv',
            'ortak/etas_italya_le2005.json', 'ortak/etas_italya_le2010.json')
def test_ayar_tabani_bolge_secici_paritesi():
    for end in ['2006-01-01', '2011-01-01']:
        chooser = ayar_tabani(son=end)
        direct = ayar_tabani('italya', son=end)
        a = pd.Timestamp(end, tz='UTC'); z = a + pd.Timedelta(days=1)
        cat = katalog_oku(VERI / 'ortak/italya_katalog_le2015.csv')
        # Arka plan bilinen cevabı; ağır anne integrali bu testte gerekmez.
        h = cat.iloc[:0]
        actual = chooser.beklenen(a, z, h, direct.izgara, [4.95, np.inf])
        expected = direct.beklenen(a, z, h, direct.izgara, [4.95, np.inf])
        np.testing.assert_array_equal(actual, expected)
        assert (actual > 0).all()
