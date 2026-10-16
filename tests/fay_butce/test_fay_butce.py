"""Bilinen cevaplı moment, uzay, Poisson ve zaman sızıntısı testleri."""
import json

import numpy as np
import pandas as pd
import pytest
from scipy.integrate import quad
from scipy.special import ndtr

from knotenlinie.fay_butce import arayuz
from knotenlinie.fay_butce.butce import (KM_DERECE,YIL_SANIYE,moment_hizi,gr_oranlari,
    iz_ornekle,gauss_kutular,yillik,karisim,izgara_dogrula)
from knotenlinie.fay_butce.skor import log_olabilirlik,bilgi_kazanci,ayarla,sayim
from knotenlinie.fay_butce.taban import Duzlestirilmis
from knotenlinie.fay_butce.veri import fay_oku,cpti_oku
from knotenlinie.fay_butce.komut import italya_izgara, main, _yaz


def grid():
    return pd.DataFrame(dict(boylam_min=[-1,0],boylam_max=[0,1],enlem_min=[-1,-1],enlem_max=[1,1]))


def fay():
    return pd.DataFrame([dict(id='a',iz=[[[-0.01,0],[0.01,0]]],alan_km2=200,kayma_mm_yil=1,mmax=6.5,katman='CSS')])


def test_birim_bilinen():
    assert moment_hizi(200,1)==6e15
    assert moment_hizi(200,0)==0
    with pytest.raises(ValueError): moment_hizi(200,-1)


@pytest.mark.parametrize('b',[0,0.9,1,1.5,2])
def test_gr_moment_korunur_ve_kutu_integrali(b):
    mdot,mmin,mmax = 6e15,2.4,6.5
    k=np.array([2.0,2.4,4.95,5.1,6.5,7])
    oran=gr_oranlari(mdot,k,mmax,b=b,mmin=mmin)
    denominator=quad(lambda m:10**(1.5*m+9.1)*10**(-b*(m-mmin)),mmin,mmax)[0]
    expected=[]
    recovered=0
    for lo,hi in zip(k[:-1],k[1:]):
        lo,hi=max(lo,mmin),min(hi,mmax)
        if hi<=lo:
            expected.append(0); continue
        mass=quad(lambda m:10**(-b*(m-mmin)),lo,hi)[0]
        expected.append(mdot*mass/denominator)
        mean=quad(lambda m:10**(1.5*m+9.1)*10**(-b*(m-mmin)),lo,hi)[0]/mass
        recovered+=oran[len(expected)-1]*mean
    np.testing.assert_allclose(oran,expected,rtol=1e-10,atol=0)
    assert recovered==pytest.approx(mdot,rel=1e-10)
    assert oran[0]==oran[-1]==0


def test_esik_momenti_yeniden_dagitmaz():
    all_rate=gr_oranlari(1e16,[2.4,4.95,6.5],6.5)
    high_rate=gr_oranlari(1e16,[4.95,6.5],6.5)
    assert high_rate[0]==all_rate[1]


@pytest.mark.parametrize('kwargs',[dict(b=-1),dict(mmin=7),dict(b=np.nan)])
def test_gr_gecersiz(kwargs):
    with pytest.raises(ValueError):gr_oranlari(1e16,[4.95,5.05],6.5,**kwargs)


def test_gauss_bilinen_cevap_ve_kuyruk():
    g=grid();s=KM_DERECE
    w=gauss_kutular([[0,0]],[1],g,s)
    expected=(ndtr(1)-ndtr(0))*(ndtr(1)-ndtr(-1))
    np.testing.assert_allclose(w,[expected,expected],rtol=1e-14)
    assert w.sum()<1 # bölge kuyruğu geri yığılmaz
    big=pd.DataFrame(dict(boylam_min=[-10],boylam_max=[10],enlem_min=[-10],enlem_max=[10]))
    assert gauss_kutular([[0,0]],[1],big,s)[0]==pytest.approx(1)


def test_iz_uzunluk_ve_agirlik():
    p,w,L=iz_ornekle([[[0,0],[1,0]],[[1,0],[3,0]]],adim_km=1000)
    np.testing.assert_allclose(p,[[.5,0],[2,0]])
    np.testing.assert_allclose(w,[1/3,2/3])
    assert L==pytest.approx(3*KM_DERECE)


def test_iz_bolunme_degisimsiz():
    p,w,L=iz_ornekle([[[0,0],[.02,0]]],adim_km=1)
    assert w.sum()==pytest.approx(1)
    assert len(p)==3
    assert L==pytest.approx(.02*KM_DERECE)


def test_yillik_dogrusal_ve_kesim():
    f=fay();g=grid(); k=[4.95,5.05,6.5,7]
    a=yillik(f,g,k)
    f['kayma_mm_yil']=2
    np.testing.assert_allclose(yillik(f,g,k),2*a)
    np.testing.assert_array_equal(a[:,-1],0)
    f=pd.concat([f.assign(katman='CSS'),f.assign(id='b',katman='ISS')])
    with pytest.raises(ValueError,match='çift sayım'):yillik(f,g,k)


def test_beklenen_zaman_ve_gecmis_okunmaz():
    model=arayuz.yapilandir(fay())
    g=grid();k=[4.95,5.05];t=pd.Timestamp('2011-01-01',tz='UTC')
    dt=pd.Timedelta(seconds=YIL_SANIYE)
    a=arayuz.beklenen(t,t+dt,object(),g,k)
    np.testing.assert_allclose(model.beklenen(t,t+2*dt,None,g,k),2*a)
    np.testing.assert_array_equal(model.beklenen(t,t,None,g,k),np.zeros((2,1)))
    with pytest.raises(ValueError):model.beklenen(t+dt,t,None,g,k)
    with pytest.raises(ValueError):model.beklenen(pd.Timestamp('2011-01-01'),t,None,g,k)


def test_karisim_kimlik_ve_toplam():
    a=np.array([[1,2],[3,4.]]);f=np.array([[9,8],[0,0.]])
    np.testing.assert_array_equal(karisim(a,f,0),a)
    np.testing.assert_array_equal(karisim(a,f,1),f)
    assert karisim(a,f,.4,toplam_esitle=True).sum()==pytest.approx(a.sum())
    for w in [-1,np.nan,1.1]:
        with pytest.raises(ValueError):karisim(a,f,w)


def test_poisson_bilinen_cevap():
    a=np.array([[2.,1.]]);b=np.array([[1.,1.]]);n=np.array([[3,0]])
    assert log_olabilirlik(a,n)==pytest.approx(3*np.log(2)-3)
    r=bilgi_kazanci(a,b,n)
    assert r['ig_nat_olay']==pytest.approx(np.log(2)-1/3)
    assert r['integral_farki']==-1
    assert log_olabilirlik(np.zeros((1,2)),n)==-np.inf
    assert log_olabilirlik(np.zeros((1,2)),np.zeros((1,2)))==0


def test_sentetik_agirlik_geri_kazanim():
    # 100 olayın %80'i solda; taban=.5, fay=.9 -> gerçek w=.75.
    a=np.array([[50.],[50.]]);f=np.array([[90.],[10.]])
    r=ayarla(a,{10:f},np.array([[80],[20]]),baslangic='2000-01-01T00:00Z',bitis='2011-01-01T00:00Z')
    assert r['agirlik']==pytest.approx(.75,abs=1e-7)
    gain=bilgi_kazanci(karisim(a,f,r['agirlik']),a,np.array([[80],[20]]))
    assert gain['ig_nat_olay']==pytest.approx(.8*np.log(1.6)+.2*np.log(.4),abs=1e-12)
    with pytest.raises(ValueError,match='≤2010'):
        ayarla(a,{10:f},np.array([[80],[20]]),baslangic='2011-01-01T00:00Z',bitis='2012-01-01T00:00Z')


def test_agirlik_sifir_sinir():
    a=np.array([[80.],[20.]]);f=np.array([[20.],[80.]])
    r=ayarla(a,{10:f},np.array([[80],[20]]),baslangic='1991-01-01T00:00Z',bitis='2011-01-01T00:00Z')
    assert r['agirlik']==0


def test_sayim_yari_acik():
    e=pd.DataFrame(dict(boylam=[-.5,0,1],enlem=[0,0,0],mw=[5,5.05,5]))
    n,dis=sayim(e,grid(),[4.95,5.05,5.15])
    np.testing.assert_array_equal(n,[[1,0],[0,1]])
    assert dis==1
    with pytest.raises(ValueError):izgara_dogrula(pd.concat([grid(),grid()]))


def test_sabit_kde_zaman_kesimi():
    e=pd.DataFrame(dict(zaman=pd.to_datetime(['1990-01-01'],utc=True),boylam=[0.],enlem=[0.],mw=[5.]))
    m=Duzlestirilmis(e,baslangic='1980-01-01T00:00Z',bitis='1991-01-01T00:00Z')
    t=pd.Timestamp('2011-01-01',tz='UTC');k=[4.95,5.05]
    a=m.beklenen(t,t+pd.Timedelta(seconds=YIL_SANIYE),object(),grid(),k)
    assert a.shape==(2,1) and np.all(a>0)
    with pytest.raises(ValueError):Duzlestirilmis(e,baslangic='1980-01-01T00:00Z',bitis='2012-01-01T00:00Z')
    with pytest.raises(ValueError):Duzlestirilmis(e,baslangic='1980-01-01T00:00Z',bitis='1990-01-01T00:00Z')


def _geojson(tmp_path,**degisiklik):
    p=dict(idsource='a',created='20000101',updated='20100601',srmin=1,srmax=3,
           dipmin=30,dipmax=30,mindepth=1,maxdepth=11,maxmag=6.5)
    p.update(degisiklik)
    d=dict(features=[dict(properties=p,geometry=dict(type='LineString',coordinates=[[0,0],[1,0]]))])
    f=tmp_path/'fay.json';f.write_text(json.dumps(d));return f


def test_geojson_alan_bilinen_ve_kaynak_kesim(tmp_path):
    p=_geojson(tmp_path)
    f=fay_oku(p,surum='DISS3.2.0')
    assert f.alan_km2.iloc[0]==pytest.approx(KM_DERECE*20)
    assert f.kayma_mm_yil.iloc[0]==2
    assert len(fay_oku(p,surum='DISS3.2.0',en_gec='2010-01-01T00:00Z'))==0
    p=_geojson(tmp_path,srmin=None)
    assert fay_oku(p,surum='DISS3.2.0').attrs['atilan'][0]['neden']=='eksik sayısal alan'
    with pytest.raises(ValueError,match='DISS3.2.0'):
        fay_oku(p,surum='baska-surum')


def test_geojson_muhur(tmp_path):
    p=_geojson(tmp_path,updated='20210101')
    with pytest.raises(ValueError,match='mühür'):fay_oku(p,surum='DISS3.2.0')


def test_italya_sablon_merkez(tmp_path):
    p=tmp_path/'grid.xml'
    p.write_text('<root><defaultCellDimension latRange="0.1" lonRange="0.1"/><cell lon="5.55" lat="44.95"/></root>')
    g=italya_izgara(p)
    assert list(g.iloc[0])==[5.5,5.6,44.9,45.0]


def test_cpti_kesik(tmp_path):
    p=tmp_path/'CPTI15_v4.0_le2015.csv'
    d=pd.DataFrame(dict(Year=[2001],Mo=[1],Da=[1],LatDef=[42],LonDef=[12],MwDef=[5],DepDef=[10]))
    d.to_csv(p,index=False)
    assert cpti_oku(p).mw.iloc[0]==5
    d['Year']=2016;d.to_csv(p,index=False)
    with pytest.raises(ValueError,match='kör'):cpti_oku(p)


def test_ayar_dosyasi_ve_arayuz(tmp_path):
    geo=_geojson(tmp_path)
    training=tmp_path/'egitim.csv'
    pd.DataFrame(dict(zaman=['1990-01-01T00:00Z'],boylam=[0],enlem=[0],mw=[5])).to_csv(training,index=False)
    config=dict(fay_yolu=str(geo),surum='DISS3.2.0',taban='duzlestirilmis',
                egitim_yolu=str(training),egitim_baslangic='1980-01-01T00:00Z',
                egitim_bitis='1991-01-01T00:00Z',taban_sigma_km=30,esik=4.95,
                sigma_km=10,agirlik=.2)
    p=tmp_path/'ayar.json';p.write_text(json.dumps(config))
    arayuz.ayar_oku(p)
    t=pd.Timestamp('2011-01-01',tz='UTC')
    x=arayuz.beklenen(t,t+pd.Timedelta(days=365),object(),grid(),[4.95,5.05])
    assert x.shape==(2,1) and np.all(x>=0)


def test_acik_son_buyukluk_kutusu():
    np.testing.assert_allclose(gr_oranlari(1e16,[4.95,6,np.inf],6.5),
                               gr_oranlari(1e16,[4.95,6,9.05],6.5))
    with pytest.raises(ValueError):gr_oranlari(1e16,[4.95,np.inf,np.inf],6.5)


def test_gecerli_taban_sifir_agirlik_kimligi():
    target=np.array([[1.,2.],[3.,4.]])
    def taban(bas,son,history,grid,edges):
        assert len(history)==0
        return target.copy()
    model=arayuz.FayButce(fay(),taban=taban,agirlik=0)
    t=pd.Timestamp('2011-01-01',tz='UTC')
    np.testing.assert_array_equal(model.beklenen(t,t+pd.Timedelta(days=1),object(),grid(),[4.95,5.05,5.15]),target)


@pytest.mark.parametrize('noktalar,agirliklar,sigma',[
    ([[0,90]],[1],10),([[0,0]],[[1]],10),([[0,0]],[1],0),([[0,0]],[np.nan],10)])
def test_gauss_gecersiz(noktalar,agirliklar,sigma):
    with pytest.raises(ValueError):gauss_kutular(noktalar,agirliklar,grid(),sigma)


def test_komut_kucuk_uc_donem(tmp_path):
    geo=_geojson(tmp_path)
    xml=tmp_path/'grid.xml'
    xml.write_text('<root><defaultCellDimension latRange="0.1" lonRange="0.1"/><cell lon="0.55" lat="0.05"/></root>')
    cat=tmp_path/'CPTI15_v4.0_le2015.csv'
    pd.DataFrame(dict(Year=[1950,1991,2012],Mo=[1]*3,Da=[1]*3,LatDef=[.05]*3,
                      LonDef=[.55]*3,MwDef=[5.]*3,DepDef=[10.]*3)).to_csv(cat,index=False)
    out=tmp_path/'out'
    main(['--fay',str(geo),'--katalog',str(cat),'--izgara',str(xml),'--cikti',str(out),
          '--kaynak-en-gec','2011-01-01T00:00:00Z','--son-kutu-acik'])
    d=json.loads((out/'sonuc.json').read_text())
    assert d['kenarlar'][-1]=='inf'
    assert d['egitim_olay']==d['ayar_olay']==d['dogrulama_olay']==1
    for s in d['sonuclar'].values():
        assert np.isfinite(s['dogrulama']['ig_nat_olay'])
    config=json.loads((out/'ayar_fiziksel.json').read_text())
    assert config['kaynak_en_gec']=='2011-01-01T00:00:00Z'
    arayuz.ayar_oku(out/'ayar_fiziksel.json')


def test_desteksiz_dogrulama_skoru_kaybolmaz(tmp_path):
    r=bilgi_kazanci(np.array([[0.]]),np.array([[1.]]),np.array([[1]]))
    assert r['ig_nat_olay']==-np.inf
    p=tmp_path/'sonuc.json';_yaz(p,r)
    assert json.loads(p.read_text())['ig_nat_olay']=='-inf'
    with pytest.raises(ValueError):_yaz(p,dict(hata=np.nan))
