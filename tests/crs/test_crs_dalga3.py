"""F3: sızıntısız iki taban, bilinen yoğun skor, düzgün zemin ve tek seçim."""
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from knotenlinie.crs.dalga3 import (AYAR_BAS, AYAR_SON, SON, adaylar, bolme_olc,
                              duzgun_arka_plan, sec, satirlar)
from knotenlinie.crs.dalga2 import alici_paylari, melez
from knotenlinie.crs.italya import crs_gunluk, poisson_logl, sayim
from tests.crs.test_crs import fixture
from knotenlinie.crs.ortak_taban import TopluOrtak, OrtakCRS
from tests.crs.test_ortak_taban import SahteT, omori
from knotenlinie.crs.arayuz import Model


def ornek():
    f, _, _, _ = fixture()
    g = pd.DataFrame({'boylam_min': [12., 14.], 'boylam_max': [12.1, 14.1],
                      'enlem_min': [42., 44.], 'enlem_max': [42.1, 44.1]})
    d = pd.DataFrame({'zaman': pd.to_datetime(['2005-12-31T12:00:00Z',
                                               '2006-01-02T12:00:00Z',
                                               '2006-01-02T13:00:00Z',
                                               '2012-01-02T12:00:00Z',
                                               '2012-01-02T13:00:00Z']),
                      'enlem': [42.05]*5, 'boylam': [12.05]*5,
                      'derinlik': [8.]*5, 'mw': [5., 4., 5., 4., 5.]})
    return f, g, d


def batch(g, start, counts=True):
    b = np.array([.5, 1.5])
    return SimpleNamespace(taban=SimpleNamespace(p={'ayar_bitis': start.isoformat()},
                                                baslangic=pd.Timestamp('2005-01-01', tz='UTC')),
                           m0=3.1, b=1., izgara=g, arka_plan=b,
                           gunluk=lambda days: np.tile(b+np.array([.2, .4]), (len(days), 1)))


def kaynak(history, faults):
    return pd.DatetimeIndex([history.zaman.iloc[0]]), np.full((1, len(faults)), -100000.)


def test_duzgun_km2_ve_butce_korunur():
    _, g, _ = ornek()
    b = np.array([1., 3.])
    u = duzgun_arka_plan(g, b)
    assert u[0] > u[1]  # alt enlem aynı derece hücrede daha büyük alan
    assert u.sum() == pytest.approx(b.sum())
    assert np.all(u > 0)
    with pytest.raises(ValueError):
        duzgun_arka_plan(g, [-1., 2.])


@pytest.mark.parametrize('start,end', [(AYAR_BAS, AYAR_SON), (AYAR_SON, SON)])
def test_seyrek_tam_poisson_ve_null_esitligi(start, end):
    f, g, d = ornek()
    d = d[d.zaman < end]
    b = batch(g, start)
    candidates = [dict(tur='ortak', agirlik=0.),
                  dict(tur='crs', asigma_pa=100000., agirlik=.25),
                  dict(tur='duzgun', agirlik=.5),
                  dict(tur='crs', asigma_pa=100000., agirlik=0.)]
    scores, meta = bolme_olc(b, d, f, start, end, (3.95, 4.95), candidates,
                            blok_gun=128, kaynak_hesabi=kaynak)
    days = pd.date_range(start, end-pd.Timedelta(days=1), freq='D')
    e = b.gunluk(days)
    ts, ds = kaynak(d, f)
    ri = crs_gunluk(days, ts, ds, 100000., f.tau_dot_pa_gun.to_numpy())
    crs = melez(e, b.arka_plan, ri, alici_paylari(g, f), .25)
    uniform = e+.5*(duzgun_arka_plan(g, b.arka_plan)-b.arka_plan)
    for m in (3.95, 4.95):
        n = sayim(d, g, days, m)
        fraction = 10**(-b.b*(m-b.m0))
        for i, dense in enumerate((e, crs, uniform, e)):
            rate = dense*fraction
            assert scores[m][i]['logL'] == pytest.approx(poisson_logl(rate, n), abs=1e-9)
            assert scores[m][i]['beklenen_toplam'] == pytest.approx(rate.sum(), abs=1e-10)
            assert scores[m][i]['N'] == n.sum()
        assert scores[m][0] == {**scores[m][3], 'aday': candidates[0]}
        assert scores[m][0]['beklenen_toplam'] == scores[m][2]['beklenen_toplam']
    assert meta['taban_arka_plan_toplami'] == pytest.approx(meta['duzgun_arka_plan_toplami'])


def test_ayar_2011_satirini_ve_yanlis_tabani_reddeder():
    f, g, d = ornek()
    with pytest.raises(ValueError):
        bolme_olc(batch(g, AYAR_BAS), d, f, AYAR_BAS, AYAR_SON, (3.95,), adaylar())
    with pytest.raises(ValueError, match='bölme'):
        bolme_olc(batch(g, AYAR_SON), d[d.zaman < AYAR_SON], f,
                  AYAR_BAS, AYAR_SON, (3.95,), adaylar())
    with pytest.raises(ValueError, match='pozitif'):
        bolme_olc(batch(g, AYAR_BAS), d[d.zaman < AYAR_SON], f,
                  AYAR_BAS, AYAR_SON, (3.95,), adaylar(), blok_gun=0)


def test_secim_tek_esikten_validation_yalniz_secili_adaylar():
    f, g, d = ornek()
    train, _ = bolme_olc(batch(g, AYAR_BAS), d[d.zaman < AYAR_SON], f,
                         AYAR_BAS, AYAR_SON, (3.95,), adaylar(),
                         blok_gun=256, kaynak_hesabi=kaynak)
    selected = sec(train[3.95])
    frozen = [dict(tur='ortak', agirlik=0.), selected['crs'], selected['duzgun']]
    def val(cat, block):
        v, _ = bolme_olc(batch(g, AYAR_SON), cat, f, AYAR_SON, SON, (3.95, 4.95),
                         frozen, blok_gun=block, kaynak_hesabi=kaynak)
        return satirlar(v, selected)
    first = val(d, 256)
    second = val(d, 127)
    for r, s in zip(first, second):
        for k in ('IG', 'SE', 'p', 'logL', 'beklenen_toplam'):
            assert r[k] == pytest.approx(s[k], abs=1e-10)
        assert r['IG'] == pytest.approx((r['logL']-r['logL_taban'])/r['N'])
        assert r['duzgun_kontrole_karsi']['IG'] == pytest.approx(
            (r['logL']-r['kontrol']['logL'])/r['N'])
        assert r['agirlik'] == selected['crs']['agirlik']
        assert r['kontrol']['agirlik'] == selected['duzgun']['agirlik']
    changed = d.copy()
    changed.loc[changed.zaman >= AYAR_SON, 'mw'] = 3.1
    altered = val(changed, 256)
    assert all(r['N'] == 0 and r['IG'] is None for r in altered)
    assert all(r['agirlik'] == first[0]['agirlik'] for r in altered)


def test_esit_ayar_null_lehine():
    rows = [dict(aday=c, logL=-5.) for c in adaylar()]
    assert all(c['agirlik'] == 0 for c in sec(rows).values())


def test_2006_taban_acik_secilir_gercek_omoriyle_ayni():
    f, h, g, p = fixture()
    t = SahteT(Model(p, h, f), g)
    t.p['ayar_bitis'] = AYAR_BAS.isoformat()
    with pytest.raises(ValueError):
        TopluOrtak(t, h, omori)  # varsayılan ≤2010 eski çağrılar korunur
    b = TopluOrtak(t, h, omori, ayar_son=AYAR_BAS)
    days = pd.date_range('2009-01-01T00:00:00Z', periods=3)
    null = OrtakCRS(t, f, asigma_pa=30000., agirlik=0., ayar_son=AYAR_BAS)
    e = b.gunluk(days)
    for i, a in enumerate(days):
        got = null.beklenen(a, a+pd.Timedelta(days=1), h[h.zaman < a], g, [b.m0, np.inf])
        np.testing.assert_allclose(e[i], got[:, 0], rtol=2e-12)
