"""C2 bilinen cevaplar: maskeler, PPE, ortak ETAS ve geçmiş sızıntısı."""
import hashlib
import json
import sys
from dataclasses import asdict, replace
from types import ModuleType

import numpy as np
import pandas as pd
import pytest
from scipy import stats

from knotenlinie.eepas.model import Parametreler, EEPAS, ArkaPlan, GUN
from knotenlinie.eepas.ortak import (Alan, GecmisFiltresi, FiltreliModel, OrtakJanus,
    gunluk_puan, EEPASOnhesap, eepas_ayarla_ortak, tamlik_sec, olcum_satiri, utc)
from knotenlinie.eepas.janus import bilgi_kazanci
from knotenlinie.eepas import c2


def grid():
    # Orta hücre yok: bounding-box integrali bu maskenin integrali değildir.
    return pd.DataFrame([[10., 11., 40., 41.], [12., 13., 40., 41.]],
                        columns=['boylam_min', 'boylam_max', 'enlem_min', 'enlem_max'])


def frame(times=(), mags=(), lons=None, depths=None):
    n = len(times)
    return pd.DataFrame({'zaman': utc(list(times)), 'mw': mags,
                         'boylam': [10.5]*n if lons is None else lons,
                         'enlem': [40.5]*n, 'derinlik': [10.]*n if depths is None else depths})


def alan():
    return Alan(grid(), [4.95, 5.05, 6.05])


def test_alan_maskesi_ve_yarim_acik_sinir():
    a = alan()
    d = frame(['2010-01-01']*6, [5.]*6, [10., 10.999, 11., 12., 12.999, 13.])
    assert a.indeks(d).tolist() == [0, 0, -1, 1, 1, -1]
    with pytest.raises(ValueError, match='örtüşen'):
        Alan(pd.concat([grid(), grid().iloc[[0]]]), [4.95, 6.])
    with pytest.raises(ValueError, match='büyüklük'):
        Alan(grid(), [4.9, 6.])


def test_ayarla_ayni_gecmis_filtresi_kamusal_arayuzde():
    a = alan()
    f = GecmisFiltresi('1985-01-01', 0., 70., True)
    d = frame(['1984-01-01', '2009-01-01', '2009-02-01', '2009-03-01', '2009-04-01'],
              [3.]*5, [10.5, 11.5, 10.5, 10.5, 12.5], [10, 10, 71, 70, 10])
    seen = []
    def callback(t0, t1, past, g, m):
        seen.append(past.copy())
        return np.ones((len(g), len(m)-1))
    cb = FiltreliModel(callback, a, f).beklenen
    cb(utc('2010-01-01'), utc('2010-01-02'), d, grid(), [4.95, 6.05])
    assert seen[0].zaman.tolist() == [utc('2009-03-01'), utc('2009-04-01')]
    f2 = GecmisFiltresi('1985-01-01', 0., 70., False)
    assert len(f2.uygula(d, a)) == 1
    # Gelecek satırı alan/derinlik filtresiyle kaybolsa bile reddedilir.
    future = frame(['2010-01-01'], [3.], [11.5], [99.])
    with pytest.raises(ValueError, match='Geçmiş'):
        cb(utc('2010-01-01'), utc('2010-01-02'), future, grid(), [4.95, 6.05])
    bad = frame(['2016-01-01'], [3.])
    with pytest.raises(ValueError, match='2015'):
        f.uygula(bad, a)


def test_gunluk_puan_bilinen_maskeli_poisson():
    a = alan()
    d = frame(['2011-01-01T12:00Z', '2011-01-02T12:00Z', '2011-01-02T13:00Z'],
              [5., 5.2, 5.], [10.5, 12.5, 11.5])
    seen = []
    rates = np.array([[1., 2.], [3., 4.]])
    def callback(t0, t1, past, g, m):
        assert (past.zaman < t0).all()
        seen.append(len(past))
        return rates
    lam, total = gunluk_puan(callback, d, a, '2011-01-01', '2011-01-03')
    np.testing.assert_equal(lam, [1., 4.])
    assert total == 20.  # Boş hücre/gün/kutuların hepsi toplamda cezalanır.
    assert seen == [0, 1]
    r = olcum_satiri('Janus-C2', 'italya', lam*2, 40., lam, total)
    assert r['N'] == 2 and r['IG'] == pytest.approx(np.log(2)-10)
    assert r['SE'] == 0 and r['p'] == 0
    with pytest.raises(ValueError, match='sıfır'):
        gunluk_puan(lambda *args: np.zeros((2, 2)), d, a, '2011-01-01', '2011-01-03')


@pytest.mark.parametrize('delay', [1., 50.])
def test_onhesap_maskede_kamusal_gunluk_yola_esit(delay):
    a = alan()
    d = frame(['2009-01-01', '2009-11-01', '2010-01-01T12:00Z', '2010-01-02T12:00Z'],
              [3., 4., 5., 5.2], [10.5, 12.5, 10.5, 12.5])
    bg = ArkaPlan(a.kutu, d.iloc[:1])
    p = Parametreler(gecikme=delay, mu=.2, r0=.4)
    ep = EEPAS(p, a.kutu, bg)
    pre = EEPASOnhesap(ep, d, a, '2010-01-01', '2010-01-04')
    for q in (p, replace(p, mu=.6, aT=p.aT+.4, olcek=3.)):
        got, gi = pre.puan(q)
        ref, ri = gunluk_puan(EEPAS(q, a.kutu, bg).beklenen, d, a, '2010-01-01', '2010-01-04')
        np.testing.assert_allclose(got, ref, rtol=1e-12)
        assert gi == pytest.approx(ri, rel=1e-12)
    with pytest.raises(ValueError, match='yalnız'):
        pre.puan(replace(p, sigmaA=2.))


def test_onhesap_integral_bos_gecmis_bilinen_cevap():
    a = alan()
    p = Parametreler(mu=1., r0=.7, olcek=2., m0=2.95)
    ep = EEPAS(p, a.kutu)
    pre = EEPASOnhesap(ep, frame(), a, '2010-01-01', '2010-01-11')
    lam, total = pre.puan(p)
    # Izgara bounding box'un 2/3'ünü kaplar. GR kapalı aralık kütlesi.
    expected = 2*.7*10*(2/3)*(10**(-2)-10**(-3.1))
    assert len(lam) == 0 and total == pytest.approx(expected)


def test_ppe_tabani_ve_binned_profil_mle():
    a = alan()
    d = frame(['2010-01-01T12:00Z', '2010-01-02T12:00Z'], [5., 5.2], [10.5, 12.5])
    p = Parametreler(m0=2.95, mu=.1, r0=.7)  # 3 günde 50 gün gecikmeli öncü katkısı yok: PPE-Poisson dünya.
    ep = EEPAS(p, a.kutu)
    pre = EEPASOnhesap(ep, d, a, '2010-01-01', '2010-01-04')
    q, res = eepas_ayarla_ortak(pre)
    lam, total = pre.puan(q)
    assert res['basari'] and q.mu >= .05
    assert total == pytest.approx(2., rel=1e-12)
    assert res['logL'] == pytest.approx(np.log(lam).sum()-2.)
    with pytest.raises(ValueError, match='pozitif PPE'):
        eepas_ayarla_ortak(pre, ppe_alt=0)
    outside = EEPASOnhesap(ep, d, a, '2011-01-01', '2011-01-04')
    with pytest.raises(ValueError, match='2010'):
        eepas_ayarla_ortak(outside)


def test_janus_ortak_etas_ayarsiz_karisim():
    e = lambda *args: np.array([[2., 6.]])
    t = lambda *args: np.array([[4., 2.]])
    for w in (0., .3, 1.):
        np.testing.assert_equal(OrtakJanus(e, t, w).beklenen(), w*e()+(1-w)*t())
    with pytest.raises(ValueError):
        OrtakJanus(e, t, 1.1)


def test_se_ve_p_uygulamadan_bagimsiz():
    x = np.array([1., 2., 3., 5.])
    r = bilgi_kazanci(np.exp(x), np.ones(4), 12., 8.)
    se = x.std(ddof=1)/2
    ig = x.mean()-1
    assert r['se'] == pytest.approx(se)
    assert r['ig'] == pytest.approx(ig)
    assert r['p'] == pytest.approx(2*stats.t.sf(abs(ig/se), 3))
    assert bilgi_kazanci([], [], 0., 0.)['se'] is None
    assert bilgi_kazanci([2.], [1.], 0., 0.)['se'] is None


def test_tamlik_yalniz_ayar_dilimlerinden(monkeypatch):
    from knotenlinie.etas import tamlik
    # Her dilimin en yüksek büyüklüğünü Mc yapan sahte yöntem: val 9 hiçbir etki yapmamalı.
    monkeypatch.setattr(tamlik, 'mc_wiemer_wyss', lambda m, **kwargs: {'mc': float(max(m))})
    d = frame(['1985-01-01', '1990-01-01', '1995-01-01', '2000-01-01', '2005-01-01', '2011-01-01'],
              [2.4, 2.5, 2.7, 2.8, 2.6, 9.])
    m0, res = tamlik_sec(d, '1985-01-01', 'italya', n_min=1)
    assert m0 == 3. and res['fark_1_5_kapisi']
    assert res['hedef_oncu_farki'] == pytest.approx(1.95)
    assert sum(r['n'] for r in res['dilimler']) == 5
    with pytest.raises(ValueError, match='tamlık için'):
        tamlik_sec(d, '1985-01-01', 'italya')


def etas_spec(tmp_path, monkeypatch):
    cfg = {'fit': {'end': '2011-01-01T00:00Z', 'nbranch': .3, 'success': True},
           'history': {'start': '1985-01-01', 'low': 0., 'high': 70., 'inclusive': True}}
    path = tmp_path/'etas_italya_le2010.json'
    path.write_text(json.dumps(cfg))
    spec = {'dosya': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'yukleyici': '_c2_sahte_t:dosyadan', 'anahtarlar': {
                'ayar_bitis': 'fit.end', 'dallanma': 'fit.nbranch', 'basari': 'fit.success',
                'baslangic': 'history.start', 'derinlik_min': 'history.low',
                'derinlik_max': 'history.high', 'ust_dahil': 'history.inclusive'}}
    mod = ModuleType('_c2_sahte_t')
    mod.dosyadan = lambda _: lambda t0, t1, past, g, m: np.ones((len(g), len(m)-1))
    monkeypatch.setitem(sys.modules, mod.__name__, mod)
    return cfg, path, spec


def test_t_teslim_dondurma_kapilari(tmp_path, monkeypatch):
    cfg, path, spec = etas_spec(tmp_path, monkeypatch)
    cb, filt = c2.etas_teslim_oku(spec)
    assert callable(cb) and filt.derinlik_max == 70.
    for end, branch, success in [('2011-01-02', .3, True), ('2011-01-01', 1., True),
                                 ('2011-01-01', .3, False)]:
        cfg['fit'] = {'end': end, 'nbranch': branch, 'success': success}
        path.write_text(json.dumps(cfg))
        spec['sha256'] = c2.sha256(path)
        with pytest.raises(ValueError, match='dondurulmuş ETAS'):
            c2.etas_teslim_oku(spec)
    spec['sha256'] = '0'*64
    with pytest.raises(ValueError, match='sha256'):
        c2.etas_teslim_oku(spec)


def test_c2_dosyadan_filtreli_bagimsiz_callable(tmp_path, monkeypatch):
    _, _, spec = etas_spec(tmp_path, monkeypatch)
    a = alan()
    cfg = {'hazir': True, 'ayar_bitis': '2011-01-01', 'izgara': grid().to_dict('list'),
           'm_kenarlar': a.m_kenarlar.tolist(), 'etas_teslim': spec,
           'gecmis_filtresi': asdict(GecmisFiltresi('1985-01-01', 0., 70., True)),
           'eepas': {'parametreler': asdict(Parametreler(mu=.05)), 'ppe_mu_alt': .05},
           'ppe_merkezler': [], 'ppe_bant': 25., 'ppe_duzgun_pay': .05,
           'janus': {'agirlik': .4}}
    path = tmp_path/'model2.json'
    path.write_text(json.dumps(cfg))
    args = (utc('2011-01-01'), utc('2011-01-02'), frame(['2009-01-01'], [4.], [11.5]),
            grid(), a.m_kenarlar)
    et, ep, ja = [c2.dosyadan(path, k) for k in ('etas', 'eepas', 'janus')]
    np.testing.assert_allclose(ja(*args), .4*ep(*args)+.6*et(*args))
    cfg['eepas']['parametreler']['mu'] = 0
    path.write_text(json.dumps(cfg))
    with pytest.raises(ValueError, match='PPE'):
        c2.dosyadan(path)


def test_kosucu_uc_uca_sahte_t_ile_bilinen_logl(tmp_path, monkeypatch):
    _, etas_path, spec = etas_spec(tmp_path, monkeypatch)
    monkeypatch.setattr(c2, 'KESIM', utc('2011-01-03'))
    def mc(df, start, region):
        # Üretimde <=2010 ile seçilen eşiğin bağımsız sabit sentetik karşılığı.
        return 2.8, {'m0': 2.8, 'fark_1_5_kapisi': True}
    monkeypatch.setattr(c2, 'tamlik_sec', mc)
    parents = frame(pd.date_range('2010-01-03', periods=100, freq='D'), [3.]*100)
    d = pd.concat([frame(['2009-01-01', '2010-01-01T12:00Z', '2010-01-02T12:00Z',
                          '2011-01-01T12:00Z', '2011-01-01T13:00Z'], [5.]*5), parents], ignore_index=True)
    catalog = tmp_path/'italya_katalog_le2015.csv'
    d.to_csv(catalog, index=False)
    gp = tmp_path/'italya_izgara.csv'
    grid().to_csv(gp, index=False)
    package = {'bolge': 'italya', 'katalog': str(catalog), 'katalog_sha256': c2.sha256(catalog),
               'izgara': str(gp), 'izgara_sha256': c2.sha256(gp), 'm_kenarlar': [4.95, 5.05, 6.05],
               'etas_teslim': spec, 'ayar_baslangic': '2010-01-01', 'tamlik_baslangic': '2009-01-01'}
    before = etas_path.read_bytes()
    cfg, result = c2.kosu_bolge(package)
    assert etas_path.read_bytes() == before  # Ortak ETAS parametreleri değiştirilmedi.
    assert cfg['eepas']['parametreler']['mu'] >= .05
    assert 0 <= cfg['janus']['agirlik'] <= 1
    assert cfg['ayar_bitis'] == '2011-01-01T00:00:00+00:00'
    assert result['log_factoriel'] == pytest.approx(np.log(2))
    assert result['logL']['ETAS'] == pytest.approx(-8-np.log(2))
    row = result['satirlar'][0]
    jlam = np.array(result['olay_beklenen']['Janus'])
    assert row['N'] == 2
    assert row['IG'] == pytest.approx(np.log(jlam).mean()-(row['beklenen_toplam']-8)/2)
    json.dumps({'model': cfg, 'sonuc': result}, allow_nan=False)


def test_eksik_t_verisi_sifir_olay_demek_degil(tmp_path):
    obj = c2.bekleyen(tmp_path)
    assert obj['durum'] == 'bekliyor'
    for b in obj['bolgeler']:
        assert len(b['eksik_dosyalar']) == 2
        assert b['satirlar'][0]['N'] is None and b['satirlar'][0]['IG'] is None
    json.dumps(obj, allow_nan=False)
