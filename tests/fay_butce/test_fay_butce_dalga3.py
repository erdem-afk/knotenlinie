"""D3 bilinen cevaplar: holdout, üst eşik ve düzgün-zemin karşılaştırması."""
import json
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from knotenlinie.fay_butce import komut3
from knotenlinie.fay_butce.etas import gunluk
from tests.fay_butce.test_etas import SahteETAS, grid, catalog
from knotenlinie.fay_butce.veri import sha256


def sample():
    # Kronolojik sırada: üst eşik olayları yalnız 0 ve 2.
    return dict(olay_mw=np.array([5., 4.1, 5.1]), olay_taban=np.array([1., 2., 4.]),
                olay_fay={'fay': np.array([3., 4., 2.]), 'zemin': np.array([2., 2., 2.])},
                toplam_taban=10., toplam_fay={'fay': 10., 'zemin': 10.})


def test_d3_gunluk_olay_buyuklukleri_skor_sirasinda():
    cat = catalog().iloc[::-1].copy()
    cat['mw'] = [5.2, 4.2]
    r = gunluk(SahteETAS(), {10: np.array([.25, .75])}, cat, grid(), [3.95, np.inf],
               '2010-01-01T00:00Z', '2010-01-03T00:00Z')
    np.testing.assert_array_equal(r['olay_mw'], [4.2, 5.2])
    np.testing.assert_array_equal(r['olay_taban'], [2., 5.])


def test_zemin_alan_agirligi():
    g = grid()
    g.loc[1, 'boylam_max'] = 3.
    np.testing.assert_allclose(komut3.zemin_sekli(g), [1/3, 2/3])


def test_ust_esik_gr_suzme_ve_ayni_agirlik():
    a, total, base, nt = komut3.karisim_skoru(sample(), 'fay', .5, esik=4.95,
                                             secim_esigi=3.95, b=1.)
    np.testing.assert_allclose(a, [.2, .3])
    np.testing.assert_allclose(base, [.1, .4])
    assert total == pytest.approx(1.) and nt == pytest.approx(1.)
    # w=.5 aynı kalır; ana satırda üç olay, ek satırda iki olay.
    main = komut3.puanla(sample(), 'fay', {'agirlik': .5}, {'agirlik': 0.},
                         esik=3.95, secim_esigi=3.95, b=1.)
    extra = komut3.puanla(sample(), 'fay', {'agirlik': .5}, {'agirlik': 0.},
                          esik=4.95, secim_esigi=3.95, b=1.)
    assert main['N'] == 3 and extra['N'] == 2
    assert extra['IG'] == pytest.approx(np.log(1.5)/2)
    assert extra['SE'] == pytest.approx(abs(np.log(2)-np.log(.75))/2)


def test_kontrol_farki_bilinen_ve_kimlik():
    r = komut3.puanla(sample(), 'fay', {'agirlik': .5}, {'agirlik': 1.},
                      esik=3.95, secim_esigi=3.95, b=1.)
    assert r['IG'] == pytest.approx(np.log(2.25)/3)
    assert r['kontrol']['IG'] == 0.
    # A=[2,3,3], kontrol=[2,2,2]; bağımsız el hesabı.
    assert r['kontrol_karsi']['IG'] == pytest.approx(2*np.log(1.5)/3)
    assert r['kontrol_karsi']['SE'] == pytest.approx(np.log(1.5)/3)
    assert r['beklenen_toplam'] == r['kontrol']['beklenen_toplam'] == 10.
    same = komut3.puanla(sample(), 'fay', {'agirlik': 0.}, {'agirlik': 0.},
                         esik=3.95, secim_esigi=3.95, b=1.)
    for result in (same, same['kontrol_karsi'], same['kontrol']):
        assert (result['IG'], result['SE'], result['p']) == (0., 0., 1.)


def test_integral_kontrol_de_korunur():
    s = sample()
    s['toplam_fay']['zemin'] = 13.
    r = komut3.puanla(s, 'fay', {'agirlik': 0.}, {'agirlik': 1.},
                      esik=3.95, secim_esigi=3.95, b=1.)
    # Olay log farkı -log2+log1+log2=0; kontrol toplamı 3 fazla.
    assert r['kontrol_karsi']['IG'] == pytest.approx(1.)
    assert r['kontrol_karsi']['integral_farki'] == 3.


def test_kontrol_ayni_optimizer_sentetik_w075():
    a = np.r_[np.full(35, .8), np.full(65, .2)]
    f = np.r_[np.full(35, .2), np.full(65, .8)]
    tuning = dict(olay_taban=a, olay_fay={'zemin': f}, toplam_taban=100., toplam_fay={'zemin': 100.})
    assert komut3.sec(tuning, {0.: 'zemin'})['agirlik'] == pytest.approx(.75, abs=1e-7)


def test_hash_kapisi_once_ve_sonra(tmp_path):
    p = tmp_path/'safe.csv'; p.write_text('safe')
    expected = {'katalog': sha256(p)}
    assert komut3._girdi_kontrol({'katalog': p}, expected) == expected
    p.write_text('changed')
    with pytest.raises(ValueError, match='SHA256'):
        komut3._girdi_kontrol({'katalog': p}, expected)


def test_bolge_iki_taban_ve_dogrulamadan_secim_yok(tmp_path, monkeypatch):
    # Gerçek CLI akışı; ayar [8,2] vs fay [2,8] -> w=1.
    # Doğrulama ters sonucu verse bile w=1 kalır.
    for key in list(komut3.TESLIM):
        if key.startswith(('italya_', 'etas_italya_')):
            f = tmp_path/key
            f.write_text('test')
            monkeypatch.setitem(komut3.TESLIM, key, sha256(f))
    g = grid(); g.to_csv(tmp_path/'italya_izgara.csv', index=False)
    monkeypatch.setitem(komut3.TESLIM, 'italya_izgara.csv', sha256(tmp_path/'italya_izgara.csv'))
    source = tmp_path/'fault.json'; source.write_text('test')
    monkeypatch.setattr(komut3, 'DISS_SHA256', sha256(source))
    monkeypatch.setattr(komut3, 'katalog_oku', lambda _: catalog())
    monkeypatch.setattr(komut3, 'fay_oku', lambda *args, **kwargs: pd.DataFrame({'id': ['a']}))
    monkeypatch.setattr(komut3.ETASFay, 'sekil', lambda *args: np.array([.2, .8]))
    model_calls, daily_calls = [], []
    def model(bolge, root, *, son):
        model_calls.append(son)
        return SimpleNamespace(mc=4.4, b=1., baslangic=pd.Timestamp('2000-01-01', tz='UTC'),
                               ayar_son=pd.Timestamp(son, tz='UTC'),
                               p=dict(katalog_sha256=sha256(tmp_path/'italya_katalog_le2015.csv'),
                                      izgara_sha256=sha256(tmp_path/'italya_izgara.csv'), dallanma=.5,
                                      arka_plan=dict(bant_km=10, zemin_payi=.01)))
    monkeypatch.setattr(komut3, 'ayar_tabani', model)
    def daily(taban, shapes, parents, g, edges, bas, son, **kw):
        daily_calls.append((taban.model.ayar_son, bas, son))
        tuning = bas == komut3.AYAR_BAS
        assert taban.model.ayar_son == bas
        assert list(edges) == [3.95, np.inf]
        return dict(olay_mw=np.array([5., 5.]), olay_taban=np.array([8., 2.]),
                    olay_fay={k: np.array([20., 80.]) if tuning and k != 'zemin'
                              else np.array([2., 1.]) for k in shapes},
                    toplam_taban=10., toplam_fay={k: 10. for k in shapes}, dis=0)
    monkeypatch.setattr(komut3, 'gunluk', daily)
    rows = komut3.bolge_kos('italya', tmp_path, source, tmp_path/'output')
    assert model_calls == ['2006-01-01', '2011-01-01']
    assert daily_calls == [(komut3.AYAR_BAS, komut3.AYAR_BAS, komut3.AYAR_SON),
                           (komut3.AYAR_SON, komut3.AYAR_SON, komut3.SON)]
    assert rows[0]['agirlik'] == 1.
    assert rows[0]['IG'] == pytest.approx(np.log(.25*.5)/2)
    cfg = json.loads((tmp_path/'output/d3-italya-tam/ayar.json').read_text())
    assert cfg['agirlik'] == 1.
    assert cfg['etas_yolu'].endswith('etas_italya_le2010.json')
    assert cfg['sekil_esik'] == 3.95
