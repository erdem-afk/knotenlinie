"""Analitik dünya, NHPP geri kazanımı, geçmiş kapısı ve skor normalizasyonu."""
import numpy as np
import pandas as pd
import pytest
from scipy.integrate import quad

from knotenlinie.crs import arayuz
from knotenlinie.crs.oran import basamak, gevset, oran, integral, basamak_orani, geri_kazan
from knotenlinie.crs.arayuz import Model, durum_integrali, buyukluk_paylari
from knotenlinie.crs.italya import poisson_logl, bilgi_kazanci, crs_gunluk, etas_gunluk
from knotenlinie.crs.girdi import k9_basamaklari
from knotenlinie.defter.geometri import fay_vektorleri


@pytest.mark.parametrize("s", [-300000., -1000., 0., 1000., 300000.])
def test_tek_basamak_analitik(s):
    a, td = 100000., 2500.
    ta = a/td
    t = np.array([0., .01, 1., 10., 300.])
    dogru = 1/(1+(np.exp(-s/a)-1)*np.exp(-t/ta))
    np.testing.assert_allclose(basamak_orani(t, s, a, td), dogru, rtol=1e-12)
    for dt in [1e-4, 1., 100., 10000.]:
        sonuc = integral(-s/a, dt, ta)
        numeric = quad(lambda u: 1/(1+(np.exp(-s/a)-1)*np.exp(-u/ta)), 0, dt)[0]
        np.testing.assert_allclose(sonuc, numeric, rtol=1e-10)


def test_asiri_gerilme_kirpilmiyor():
    assert np.isfinite(integral(-1000., 1., 100.))
    assert integral(-1000., 1., 100.) > 99000.
    assert integral(1000., 1., 100.) == 0.
    np.testing.assert_allclose(integral(0., [0., 1., 1e6], 100.), [0., 1., 1e6])
    for f in [lambda: integral(0., -1., 100.), lambda: basamak(0., 100., 0.), lambda: gevset(0., 1., -1.)]:
        with pytest.raises(ValueError):
            f()


def test_durum_basamaklari_toplanmaz():
    a = pd.Timestamp("2009-01-02T00:00:00Z"); z = a+pd.Timedelta(days=2)
    ts = pd.DatetimeIndex([a-pd.Timedelta(days=1), a-pd.Timedelta(hours=12)])
    ds = np.array([[10000., -10000.], [20000., -20000.]])
    lx = basamak(gevset(basamak(np.zeros(2), ds[0], 100000.), .5, 100.), ds[1], 100000.)
    lx = gevset(lx, .5, 100.)
    np.testing.assert_allclose(durum_integrali(a, z, ts, ds, 100000., [1000., 1000.]), integral(lx, 2., 100.))
    with pytest.raises(ValueError):
        durum_integrali(ts[-1], z, ts, ds, 100000., [1000., 1000.])


def test_nhpp_geri_kazanim():
    # Bağımsız inceltme: sabit üst sınır, üreticide oran.py çağrısı yok.
    rng = np.random.default_rng(4917)
    a, ta, s, r, T = 80000., 40., 120000., 30., 300.
    ust = r*np.exp(s/a)
    t = rng.uniform(0, T, rng.poisson(ust*T))
    lam = r/(1+(np.exp(-s/a)-1)*np.exp(-t/ta))
    t = np.sort(t[rng.uniform(0, 1, len(t)) < lam/ust])
    fit = geri_kazan(t, T, s, r)
    assert fit["basari"]
    assert abs(fit["asigma_pa"]/a-1) < .15
    assert abs(fit["ta_gun"]/ta-1) < .25


def test_bilinen_poisson_dunyasi():
    n = np.array([[2, 0], [0, 1]])
    e = np.array([[2., 1.], [1., 1.]])
    b = np.ones((2, 2))
    dogru = 2*np.log(2)-1
    np.testing.assert_allclose(bilgi_kazanci(e, b, n), dogru/3.)
    np.testing.assert_allclose(poisson_logl(e, n), 2*np.log(2)-5-np.log(2))
    assert poisson_logl(np.zeros((2, 2)), n) == -np.inf
    assert poisson_logl(np.zeros((2, 2)), np.zeros((2, 2))) == 0
    with pytest.raises(ValueError):
        bilgi_kazanci(e, b, np.zeros((2, 2)))
    with pytest.raises(ValueError):
        poisson_logl(np.ones(1), np.array([np.inf]))


def fixture():
    f = pd.DataFrame({"id": ["f1", "f2"], "centroid_lat": [42., 44.], "centroid_lon": [12., 14.],
                      "depth_central_km": [8., 8.], "strike_central_deg": [140., 140.],
                      "dip_central_deg": [45., 45.], "rake_central_deg": [-90., -90.],
                      "tau_dot_pa_gun": [1000., 2000.]})
    n, s = fay_vektorleri(f.strike_central_deg, f.dip_central_deg, f.rake_central_deg)
    f[["normal_n", "normal_e", "normal_d"]] = n
    f[["slip_n", "slip_e", "slip_d"]] = s
    h = pd.DataFrame({"zaman": pd.to_datetime(["2009-01-01T12:00:00Z", "2009-01-02T12:00:00Z"]),
                      "enlem": [42.1, 43.9], "boylam": [12.1, 14.1], "derinlik": [8., 8.],
                      "mw": [5.5, 4.2], "event_id": ["a", "b"]})
    g = pd.DataFrame({"boylam_min": [6., 13.], "boylam_max": [13., 20.],
                      "enlem_min": [35., 35.], "enlem_max": [48., 48.]})
    p = dict(mu=.5, K=.01, c=.05, p=1.2, alpha=.7, D=10., q=1.5, gamma=.5)
    return f, h, g, p


def test_k9_gercek_okada():
    f, h, _, _ = fixture()
    ts, ds = k9_basamaklari(h, f)
    assert len(ts) == 1
    assert ds.shape == (1, 2)
    assert np.isfinite(ds).all()
    assert np.any(ds != 0)


def test_arayuz_sifir_ve_nedensellik(monkeypatch):
    f, h, g, p = fixture()
    # Nötr dünyada ETAS+CRS tam olarak ETAS; arka plan iki kere eklenmez.
    def stub(history, faults):
        events = history[history.mw >= 5.]
        return pd.DatetimeIndex(events.zaman), np.zeros((len(events), len(faults)))
    monkeypatch.setattr(arayuz, "k9_basamaklari", stub)
    base = Model(p, h, f, b=1.)
    mix = Model(p, h, f, b=1., agirlik=1.)
    a = pd.Timestamp("2009-01-03T00:00:00Z"); z = a+pd.Timedelta(days=1)
    arayuz.kur(mix)
    np.testing.assert_allclose(arayuz.beklenen(a, z, h, g, [4.95, 5.5, np.inf]), base.beklenen(a, z, h, g, [4.95, 5.5, np.inf]), rtol=1e-12)
    u, pay, _ = mix.uzay(g, h)
    np.testing.assert_allclose(u.sum(), 1., rtol=1e-12)
    np.testing.assert_allclose(pay.sum(axis=1), 1.)
    with pytest.raises(ValueError):
        mix.beklenen(h.zaman.iloc[-1], z, h, g, [4.95, np.inf])
    with pytest.raises(ValueError):
        mix.beklenen(a.tz_localize(None), z, h, g, [4.95, np.inf])
    with pytest.raises(ValueError):
        Model(p, h.assign(zaman=pd.to_datetime(["2011-01-01T00:00:00Z"]*2)), f)


def test_batch_ortak_arayuz_ayni():
    f, h, g, p = fixture()
    m = Model(p, h, f, b=1., agirlik=.25)
    days = pd.date_range("2009-01-01T00:00:00Z", periods=5, freq="D")
    e, u, pay = etas_gunluk(m, h, g, days)
    ts, ds = k9_basamaklari(h, f)
    ri = crs_gunluk(days, ts, ds, m.asigma_pa, f.tau_dot_pa_gun.to_numpy())
    expected = (e+.25*p["mu"]*u[None, :]*(ri @ pay.T-1.))*10**(-.95)
    for i, a in enumerate(days):
        got = m.beklenen(a, a+pd.Timedelta(days=1), h[h.zaman<a], g, [4.95, np.inf])
        np.testing.assert_allclose(got[:, 0], expected[i], rtol=2e-12, atol=1e-15)


def test_golge_ve_artis_arka_plani_degisir(monkeypatch):
    f, h, g, p = fixture()
    a = pd.Timestamp("2009-01-03T00:00:00Z")
    # İki alıcıda aynı basamak: hücrelerin payı ne olursa olsun aynı oran.
    p = dict(p, K=1e-20)
    base = Model(p, h, f)
    f = f.assign(tau_dot_pa_gun=1000.)
    for s in (-100000., 100000.):
        monkeypatch.setattr(arayuz, "k9_basamaklari", lambda history, faults: (
            pd.DatetimeIndex([a-pd.Timedelta(days=1)]), np.full((1, 2), s)))
        mix = Model(p, h, f, agirlik=1.)
        got = mix.beklenen(a, a+pd.Timedelta(days=1), h, g, [4., np.inf])[:, 0]
        ref = base.beklenen(a, a+pd.Timedelta(days=1), h, g, [4., np.inf])[:, 0]
        lx = np.log(1+(np.exp(-s/100000.)-1)*np.exp(-1/100.))
        numeric = quad(lambda t: 1/(1+(np.exp(lx)-1)*np.exp(-t/100.)), 0, 1)[0]
        np.testing.assert_allclose(got/ref, numeric, rtol=1e-12)
        assert (got < ref).all() if s < 0 else (got > ref).all()


def test_batch_gelecek_degismesi_gecmisi_etkilemez():
    f, h, g, p = fixture()
    m = Model(p, h, f)
    days = pd.date_range("2009-01-01T00:00:00Z", periods=3, freq="D")
    future = h.iloc[[0]].assign(zaman=days[-1], mw=6., event_id="future")
    d = pd.concat([h, future], ignore_index=True)
    e1 = etas_gunluk(m, h, g, days)[0]
    e2 = etas_gunluk(m, d, g, days)[0]
    np.testing.assert_allclose(e1, e2, rtol=1e-12)
    ts = pd.DatetimeIndex([days[-1]])
    np.testing.assert_allclose(crs_gunluk(days, ts, np.full((1, 2), 100000.), 100000., [1000., 1000.]), 1.)


def test_sonlu_parametre_kapisi():
    f, h, _, p = fixture()
    with pytest.raises(ValueError):
        Model(dict(p, p=np.inf), h, f)
    with pytest.raises(ValueError):
        Model(p, h, f, asigma_pa=np.inf)


def test_magnitud_kutulari():
    np.testing.assert_allclose(buyukluk_paylari([4., 5., 6., np.inf], 4., 1.), [.9, .09, .01])
    with pytest.raises(ValueError):
        buyukluk_paylari([3., 4.], 4., 1.)
