"""D2 bilinen cevaplar: arka plan, günlük skor, ayar ve kaynak kapıları."""
import json

import numpy as np
import pandas as pd
import pytest
from scipy.stats import t as student_t

from knotenlinie.fay_butce import arayuz
from knotenlinie.fay_butce.etas import ETASFay, OrtakTaban, degistir, ayarla, olcum, gunluk
from knotenlinie.fay_butce.veri import fay_oku, kaynak_kapisi, DISS_SHA256, sha256
from knotenlinie.fay_butce.komut2 import main, katalog_oku


def grid():
    return pd.DataFrame(dict(boylam_min=[0.,1.],boylam_max=[1.,2.],
                             enlem_min=[0.,0.],enlem_max=[1.,1.]))


def catalog():
    return pd.DataFrame(dict(zaman=pd.to_datetime(['2010-01-01T12:00Z','2010-01-02T12:00Z'],utc=True),
                             boylam=[.5,1.5],enlem=[.5,.5],mw=[5.,5.],derinlik=[10.,10.]))


class SahteETAS:
    def __init__(self):
        self.gecmis = []

    def arka_plan_beklenen(self, *args):
        return np.array([[2.],[1.]])

    def beklenen(self, bas, son, gecmis, izgara, kenarlar):
        assert not len(gecmis) or (gecmis.zaman<bas).all()
        self.gecmis.append(len(gecmis))
        # Bilinen ebeveyn tetiklemesi; w=1'de dahi kalmalı.
        return self.arka_plan_beklenen()+len(gecmis)*np.array([[0.],[4.]])


def source(tmp_path):
    p = tmp_path/'fay.json'
    p.write_text(json.dumps(dict(features=[dict(properties=dict(idsource='a',
        created='20000101',updated='20100601',srmin=1,srmax=1,dipmin=45,dipmax=45,
        mindepth=1,maxdepth=10,maxmag=6.5),
        geometry=dict(type='LineString',coordinates=[[.1,.5],[.8,.5]]))])))
    return p


def test_tetikleme_ve_buyukluk_toplamlari_aynen():
    bg = np.array([[2.,4.],[1.,2.]])
    triggering = np.array([[8.,2.],[6.,4.]])
    base = bg+triggering
    np.testing.assert_array_equal(degistir(base,bg,[.25,.75],0),base)
    full = degistir(base,bg,[.25,.75],1)
    np.testing.assert_allclose(full,triggering+np.array([[.75,1.5],[2.25,4.5]]))
    np.testing.assert_allclose(full.sum(axis=0),base.sum(axis=0))
    mix = degistir(base,bg,[.25,.75],.3)
    np.testing.assert_allclose(mix,.7*base+.3*full)


@pytest.mark.parametrize('bg,u,w',[(np.array([[3.],[1.]]),[1,1],.5),
                                   (np.array([[2.],[1.]]),[0,0],.5),
                                   (np.array([[2.],[1.]]),[1,1],-1)])
def test_gecersiz_arka_plan(bg,u,w):
    with pytest.raises(ValueError):
        degistir(np.array([[2.],[1.]]),bg,u,w)


def test_tam_poisson_ig_se_p_bilinen():
    log = np.array([1.,2.,3.])
    r = olcum(np.exp(log),np.ones(3),5.,8.)
    assert r['IG'] == pytest.approx(3.)  # (6+8-5)/3
    assert r['SE'] == pytest.approx(1/np.sqrt(3))
    assert r['p'] == pytest.approx(2*student_t.sf(3*np.sqrt(3),2))
    assert r['delta_logL'] == pytest.approx(9.)
    assert r['integral_farki'] == 3


def test_sifir_kimlik_desteksiz_ve_tek_olay():
    r = olcum([1,2],[1,2],4,4)
    assert (r['IG'],r['SE'],r['p']) == (0,0,1)
    assert olcum([0],[1],1,1)['IG']=='-inf'
    assert olcum([2],[1],2,1)['SE'] is None


def test_sentetik_w075_geri_kazanim():
    # Saf taban [0.8,0.2], fay [0.2,0.8]; w=.75 -> [0.35,0.65].
    a = np.r_[np.full(35,.8),np.full(65,.2)]
    f = np.r_[np.full(35,.2),np.full(65,.8)]
    fit = ayarla(a,{10:f},100,{10:100},baslangic='2000-01-01T00:00Z',bitis='2011-01-01T00:00Z')
    assert fit['agirlik']==pytest.approx(.75,abs=1e-7)
    with pytest.raises(ValueError,match='≤2010'):
        ayarla(a,{10:f},100,{10:100},baslangic='2010-01-01T00:00Z',bitis='2012-01-01T00:00Z')


def test_gunluk_bilinen_skor_ve_gecmis():
    taban = SahteETAS()
    r = gunluk(taban,{10:np.array([.25,.75])},catalog(),grid(),[4.95,np.inf],
               '2010-01-01T00:00Z','2010-01-03T00:00Z')
    np.testing.assert_array_equal(r['olay_taban'],[2.,5.])
    np.testing.assert_array_equal(r['olay_fay'][10],[.75,6.25])
    assert r['toplam_taban']==r['toplam_fay'][10]==10.
    assert taban.gecmis==[0,1] and r['dis']==0
    score = olcum(r['olay_fay'][10],r['olay_taban'],10,10)
    assert score['IG']==pytest.approx((np.log(.75/2)+np.log(6.25/5))/2)


def test_ortak_taban_bos_gecmis_arka_plan():
    model = OrtakTaban(SahteETAS())
    model.model.arka_plan_beklenen = lambda *args: np.array([[2.],[1.]])
    np.testing.assert_array_equal(model.arka_plan_beklenen(None,None,catalog(),grid(),[4.95,np.inf]),[[2],[1]])
    class SadeceETAS:
        def beklenen(self,bas,son,past,g,k):
            assert len(past)==0
            return np.array([[1.],[2.]])
    fallback = OrtakTaban(SadeceETAS())
    np.testing.assert_array_equal(fallback.arka_plan_beklenen(None,None,catalog(),grid(),[4.95,np.inf]),[[1],[2]])


def test_model_arayuzu_kimlik_ve_kapi(tmp_path):
    f = fay_oku(source(tmp_path),surum='DISS3.2.0',en_gec='2016-01-01')
    t = pd.Timestamp('2010-01-01',tz='UTC')
    model = ETASFay(SahteETAS(),f,agirlik=0,sigma_km=10)
    np.testing.assert_array_equal(model.beklenen(t,t+pd.Timedelta(days=1),catalog().iloc[:0],grid(),[4.95,np.inf]),[[2],[1]])
    with pytest.raises(ValueError,match='geçmiş'):
        model.beklenen(t,t+pd.Timedelta(days=1),catalog(),grid(),[4.95,np.inf])
    with pytest.raises(ValueError,match='sha256'):
        model.beklenen(pd.Timestamp('2016-01-01',tz='UTC'),pd.Timestamp('2016-01-02',tz='UTC'),catalog(),grid(),[4.95,np.inf])
    model.agirlik = .5
    out = model.beklenen(t,t+pd.Timedelta(days=1),catalog().iloc[:0],grid(),[4.95,np.inf])
    assert out.shape==(2,1) and out.sum()==pytest.approx(3.)


def test_sha_kapisi_okumadan_once(tmp_path):
    p = source(tmp_path)
    with pytest.raises(ValueError,match='sha256'):
        fay_oku(p,surum='DISS3.2.0',beklenen_sha256=DISS_SHA256)
    f = fay_oku(p,surum='DISS3.2.0',beklenen_sha256=sha256(p),en_gec='2016-01-01')
    with pytest.raises(ValueError,match='sha256'):
        kaynak_kapisi(f,pd.Timestamp('2016-01-01',tz='UTC'))
    f.attrs['sha256'] = DISS_SHA256  # Sentetik doğrulanmış provenance.
    kaynak_kapisi(f,pd.Timestamp('2016-01-01',tz='UTC'))
    f.attrs['kaynak_en_gec'] = '2017-01-01T00:00Z'
    with pytest.raises(ValueError,match='kaynak-en-gec'):
        kaynak_kapisi(f,pd.Timestamp('2016-01-01',tz='UTC'))
    f.attrs['kaynak_en_gec'] = None
    with pytest.raises(ValueError,match='kaynak-en-gec'):
        kaynak_kapisi(f,pd.Timestamp('2016-01-01',tz='UTC'))


def test_eski_arayuz_de_kor_kapili(tmp_path):
    f = fay_oku(source(tmp_path),surum='DISS3.2.0')
    model = arayuz.FayButce(f)
    t = pd.Timestamp('2016-01-01',tz='UTC')
    with pytest.raises(ValueError,match='kaynak-en-gec'):
        model.beklenen(t,t+pd.Timedelta(days=1),None,grid(),[4.95,np.inf])
    with pytest.raises(ValueError,match='kaynak-en-gec'):
        model.beklenen(t-pd.Timedelta(days=1),t+pd.Timedelta(days=1),None,grid(),[4.95,np.inf])


def test_kesik_katalog_ve_kor_kosucu(tmp_path):
    p = tmp_path/'italya_katalog_le2015.csv'
    catalog().to_csv(p,index=False)
    assert len(katalog_oku(p))==2
    d = catalog();d['zaman']=pd.Timestamp('2016-01-01',tz='UTC');d.to_csv(p,index=False)
    with pytest.raises(ValueError,match='kör'):
        katalog_oku(p)
    with pytest.raises(ValueError,match='kör'):
        gunluk(SahteETAS(),{},d,grid(),[4.95,np.inf],'2015-01-01T00:00Z','2016-01-02T00:00Z')


def test_buyukluk_kutusu_birlestirme_ig_ayni():
    # Ancak ortak GR ise birleştirme tam eşdeğerdir.
    gr = np.array([.25,.75])
    base = np.array([10.,7.])[:,None]*gr
    bg = np.array([2.,1.])[:,None]*gr
    pred = degistir(base,bg,[.25,.75],.4)
    collapsed = degistir(base.sum(axis=1,keepdims=True),bg.sum(axis=1,keepdims=True),[.25,.75],.4)
    a = olcum(pred[[0,1],[0,1]],base[[0,1],[0,1]],pred.sum(),base.sum())
    b = olcum(collapsed[:,0],base.sum(axis=1),collapsed.sum(),base.sum())
    assert a['IG']==pytest.approx(b['IG'])
    assert a['SE']==pytest.approx(b['SE'])


def test_d2_ayar_ortak_arayuzde(tmp_path,monkeypatch):
    import sys, types
    mod = types.ModuleType('sahte_taban_d2')
    mod.yukle = lambda yol: SahteETAS()
    monkeypatch.setitem(sys.modules,'sahte_taban_d2',mod)
    monkeypatch.setattr(arayuz,'_MODEL',None)
    source_file = source(tmp_path)
    from knotenlinie.fay_butce import etas as fay_etas
    monkeypatch.setattr(fay_etas,'DISS_SHA256',sha256(source_file))
    cfg = dict(taban='ortak_etas',etas_fabrika='sahte_taban_d2:yukle',etas_yolu='sahte',
               fay_yolu=str(source_file),surum='DISS3.2.0',fay_sha256=sha256(source_file),
               kaynak_en_gec='2016-01-01',agirlik=.5,sigma_km=10)
    p = tmp_path/'ayar.json';p.write_text(json.dumps(cfg))
    model = arayuz.ayar_oku(p)
    assert isinstance(model,ETASFay)
    t = pd.Timestamp('2010-01-02',tz='UTC')
    out = arayuz.beklenen(t,t+pd.Timedelta(days=1),catalog().iloc[:1],grid(),[4.95,np.inf])
    assert out.sum()==pytest.approx(7.)


def test_cli_sonuc_ve_girdi_degisimi_kapisi(tmp_path,monkeypatch):
    import sys, types
    from knotenlinie.fay_butce import komut2
    cat = tmp_path/'italya_katalog_le2015.csv';catalog().to_csv(cat,index=False)
    g = tmp_path/'italya_izgara.csv';grid().to_csv(g,index=False)
    f = source(tmp_path)
    et = tmp_path/'etas_italya_le2010.json'
    et.write_text(json.dumps(dict(ayar_baslangic='2000-01-01T00:00Z',ayar_bitis='2011-01-01T00:00Z',
        mc=4.4,dallanma=.5,katalog_sha256=sha256(cat),izgara_sha256=sha256(g))))
    mod = types.ModuleType('sahte_taban_d2_cli');mod.yukle = lambda yol: SahteETAS()
    monkeypatch.setitem(sys.modules,mod.__name__,mod)
    monkeypatch.setattr(komut2,'DISS_SHA256',sha256(f))
    def fake(taban,shapes,*args,**kwargs):
        return dict(olay_taban=np.array([2.,1.]),olay_fay={s:np.array([1.,2.]) for s in shapes},
                    toplam_taban=3.,toplam_fay={s:3. for s in shapes},dis=0)
    monkeypatch.setattr(komut2,'gunluk',fake)
    argv = ['--ortak',str(tmp_path),'--bolge','italya','--etas-fabrika',mod.__name__+':yukle',
            '--fay',str(f),'--izgara',str(g),'--kaynak-en-gec','2016-01-01']
    komut2.main(argv+['--cikti',str(tmp_path/'ok')])
    assert json.loads((tmp_path/'ok'/'sonuc.json').read_text())['N']==2
    def changing(*args,**kwargs):
        cat.write_text(cat.read_text()+'\n')
        return fake(*args,**kwargs)
    monkeypatch.setattr(komut2,'gunluk',changing)
    with pytest.raises(ValueError,match='girdi değişti'):
        komut2.main(argv+['--cikti',str(tmp_path/'bad')])
    assert not (tmp_path/'bad').exists()


def test_cli_ortak_girdi_kapisi(tmp_path):
    with pytest.raises(FileNotFoundError,match='deney T'):
        main(['--ortak',str(tmp_path),'--bolge','italya','--etas-fabrika','yok:oku',
              '--fay','yok','--izgara','yok','--kaynak-en-gec','2016-01-01',
              '--ayar-baslangic','2000-01-01','--cikti',str(tmp_path/'out')])
    assert not (tmp_path/'out').exists()
