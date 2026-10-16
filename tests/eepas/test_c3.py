"""C3 bilinen cevaplar: ayar bölmesi, düzgün kontrol ve eşik aktarımı."""
from copy import deepcopy
import json

import numpy as np
import pandas as pd
import pytest

from knotenlinie.eepas import c3
from knotenlinie.eepas.ortak import Alan, tamlik_sec, utc
from knotenlinie.eepas.model import ArkaPlan, GUN
from tests.eepas.test_ortak import grid, frame


def test_alt_hedef_acikca_secilmeli():
    with pytest.raises(ValueError):
        Alan(grid(), [3.95, 4.95, 9.05])
    a = c3.alan_yap(grid(), 'italya')
    assert a.m_kenarlar[0] == 3.95
    assert len(a.m_kenarlar) == 52
    assert c3.alan_yap(grid(), 'italya', 4.95).m_kenarlar[-1] == 9.05


def test_tamlik_2005_sonu_ileriyi_kullanmaz(monkeypatch):
    from knotenlinie.etas import tamlik
    seen = []
    def mc(m, **_):
        seen.extend(m)
        return {'mc': max(m)}
    monkeypatch.setattr(tamlik, 'mc_wiemer_wyss', mc)
    d = frame(['1996-01-01', '2001-01-01', '2006-01-01', '2011-01-01'],
              [2.6, 2.8, 5.0, 8.0])
    m0, r = tamlik_sec(d, '1996-01-01', 'italya', n_min=1,
                       son='2006-01-01', hedef_alt=np.float64(3.95))
    json.dumps(r, allow_nan=False)
    assert m0 == 3.0 and max(seen) == 2.8
    assert r['hedef_oncu_farki'] == pytest.approx(.95)
    assert not r['fark_1_5_kapisi']
    assert r['bitis_haric'] == c3.BOLME.isoformat()


def test_duzgun_profil_hizi_ve_bos_hucre_telafisi():
    a = Alan(grid(), [3.95, 4.95, 5.95], hedef_alt=3.95)
    d = frame(['2010-01-01T12:00Z', '2010-01-02T12:00Z'], [4., 5.], [10.5, 12.5])
    lam, total, rate = c3.duzgun_puan(d, a, '2010-01-01', '2010-01-03', 2.95, 1.)
    # Her hücre kutunun 1/3'ü; GR kutuları .09 ve .009. Maskede 2/3 kütle.
    expected_rate = 2/(2*(2/3)*.099)
    assert rate == pytest.approx(expected_rate)
    np.testing.assert_allclose(lam, expected_rate*np.array([.03, .003]))
    assert total == pytest.approx(2.)
    dv = frame(['2011-01-01T12:00Z']*10, [4.]*10)
    _, valid_total, valid_rate = c3.duzgun_puan(dv, a, '2011-01-01', '2011-01-05',
                                              2.95, 1., hiz=rate)
    assert valid_total == pytest.approx(4.) and valid_rate == rate  # N=10 ile yeniden ayar yok.
    with pytest.raises(ValueError, match='<=2010'):
        c3.duzgun_puan(dv, a, '2011-01-01', '2011-01-05', 2.95, 1.)


def test_agirlik_bolmesi_ve_bilinen_uc_optimum():
    e = np.array([2., 2.])
    t = np.array([1., 1.])
    r = c3.sec(e, t, 2., 2., c3.BOLME, c3.AYAR_SONU)
    assert r['agirlik'] == 1.
    zero = c3.sec(e, t, 200., 2., c3.BOLME, c3.AYAR_SONU)
    assert zero['agirlik'] == 0.
    for lo, hi in [('2005-01-01', '2011-01-01'), ('2011-01-01', '2016-01-01')]:
        with pytest.raises(ValueError, match='bölmesinde'):
            c3.sec(e, t, 2., 2., lo, hi)


def test_satir_iki_taban_icin_bagimsiz_cevap():
    lam = np.array([2., 8.])
    base = np.array([1., 2.])
    control = np.array([1., 4.])
    row = c3.satir('Janus-C3', 'italya', 3.95, lam, 12., base, 8.,
                   control, 10., .2, .3, np.log(2))
    assert row['IG'] == pytest.approx((np.log(2)+np.log(4))/2-2)
    assert row['SE'] == pytest.approx(np.log(2)/2)
    assert row['kontrole_karsi']['IG'] == pytest.approx(np.log(2)-1)
    assert row['kontrole_karsi']['SE'] == 0.
    assert row['kontrole_karsi']['p'] == 0.
    assert row['logL'] == pytest.approx(np.log(16)-12-np.log(2))


def test_c3_ayar_ve_aktarim_akisi_sahte_t_ile(monkeypatch, tmp_path):
    calls = []
    class FakeT:
        def __init__(self, end):
            self.izgara = grid()
            self.mc = 3.1
            self.p = {'ayar_baslangic': '1985-01-01'}
            self.end = utc(end)
        def beklenen(self, a, b, past, g, edges):
            assert utc(a) >= self.end
            assert (past.zaman < utc(a)).all()
            mag = 10**(-.9*(edges[:-1]-3.1))-10**(-.9*(edges[1:]-3.1))
            return .05*np.array([.4, .6])[:, None]*mag
    def loader(region, path, *, son):
        calls.append(son)
        return FakeT(son)
    monkeypatch.setattr(c3, 'ayar_tabani', loader)
    # Binned constant ETAS, analitik toplam; tam günlük yol ayrıca C2 testlerinde sınanır.
    def score(cb, d, alan, a, b):
        targets, ci, mi = c3.hedefler(d, alan, a, b)
        rates = cb(utc(a), utc(a)+GUN, d.loc[d.zaman < utc(a)], alan.izgara, alan.m_kenarlar)
        return rates[ci, mi], float((utc(b)-utc(a))/GUN)*rates.sum()
    monkeypatch.setattr(c3, 'gunluk_puan', score)
    warm = frame(pd.date_range('2001-01-01', periods=100, freq='D'),
                 np.linspace(2.9, 3.7, 100))
    warm = pd.concat([warm, frame(['2002-01-01'], [4.1])], ignore_index=True)
    fit = frame(['2006-01-02', '2007-01-01', '2008-01-01', '2010-01-01'],
                [4.1, 4.3, 5.1, 5.2], [10.5, 12.5, 10.5, 12.5])
    valid = frame(['2011-01-02', '2011-01-02'], [4.2, 5.2], [10.5, 12.5])
    data = pd.concat([warm, fit, valid], ignore_index=True)
    monkeypatch.setattr(c3, 'kesik_oku', lambda _: data.copy())
    def comp(d, start, region, **kwargs):
        assert (d.zaman < c3.BOLME).all()
        assert kwargs['son'] == c3.BOLME
        return 2.8, {'m0': 2.8, 'fark_1_5_kapisi': False}
    monkeypatch.setattr(c3, 'tamlik_sec', comp)
    cfg = c3.ayarla('italya', tmp_path, 200)
    assert cfg['ayar_ozet']['N'] == 4
    assert cfg['eepas']['n_ayar'] == 4
    assert cfg['ayar_ozet']['EEPAS_toplam'] == pytest.approx(4.)
    assert len(cfg['ppe_merkezler']) == 1  # Holdout/validasyon PPE'ye girmedi.
    snapshot = deepcopy(cfg)
    out = c3.dogrula(cfg, tmp_path)
    assert cfg == snapshot  # Eşik aktarımı doğrulamada hiçbir parametreyi değiştirmez.
    janus = [r for r in out['satirlar'] if r['aday'] == 'Janus-C3']
    assert [r['N'] for r in janus] == [2, 1]
    assert janus[0]['agirlik'] == janus[1]['agirlik'] == cfg['janus']['agirlik']
    assert janus[1]['secim_m_alt'] == 3.95
    assert calls == ['2006-01-01', '2011-01-01']
    json.dumps({'ayar': cfg, 'olcum': out}, allow_nan=False)
    assert not janus[0]['aday_kapisi'] and janus[1]['aday_kapisi']
    ctl = [r for r in out['satirlar'] if r['aday'] == 'ortak taban + düzgün zemin']
    assert all(r['kontrole_karsi']['IG'] == 0 and r['kontrole_karsi']['p'] in (1., None)
               for r in ctl)
