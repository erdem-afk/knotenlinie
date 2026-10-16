"""Bilinen cevaplar, sızıntı reddi ve koşullu sentetik geri kazanım."""
import json
from dataclasses import replace

import numpy as np
import pandas as pd
import pytest
from scipy.integrate import quad

from knotenlinie.eepas.model import (Parametreler, EEPAS, ArkaPlan, zaman_yogunlugu,
    zaman_kutlesi, buyukluk_yogunlugu, buyukluk_kutlesi, eta, normal_aralik,
    kutu_izgara, log_olabilirlik, ayarla, EPOCH, GUN, LN10)
from knotenlinie.eepas.janus import ETASModel, Janus, agirlik_ayarla, bilgi_kazanci
from knotenlinie.eepas.benzetim import uret
from knotenlinie.eepas import arayuz
from knotenlinie.etas import model as ETAS

BOX = (39.,43.,10.,15.)


def frame(t=(),m=(),lo=None,la=None):
    n = len(t)
    return pd.DataFrame({'zaman':EPOCH+pd.to_timedelta(np.asarray(t),unit='D'),
                         'mw':m,'boylam':np.full(n,12.5) if lo is None else lo,
                         'enlem':np.full(n,41) if la is None else la,'derinlik':np.full(n,10.)})


def etas(bg=None):
    return ETASModel({'mu':0.03,'K':0.02,'c':0.1,'alpha':0.8,'p':1.2,
                      'D':10.,'q':1.5,'gamma':0.2},2.95,1.,BOX,bg)


def test_zaman_yogunlugu_ve_gecikme():
    p = Parametreler(aT=1,bT=0.5,sigmaT=0.3,gecikme=0)
    median = 10**(p.aT+p.bT*3)
    assert zaman_kutlesi(0,median,3,p)==pytest.approx(.5)
    assert zaman_yogunlugu(median,3,p)==pytest.approx(1/(median*.3*LN10*np.sqrt(2*np.pi)))
    for delay in (0,50):
        q = replace(p,gecikme=delay)
        val = quad(lambda logt: float(zaman_yogunlugu(np.exp(logt),3,q)*np.exp(logt)),
                   np.log(max(delay,1e-10)),np.log(1e7))[0]
        assert val==pytest.approx(float(zaman_kutlesi(0,1e7,3,q)),rel=1e-9)
    assert np.all(zaman_yogunlugu(np.array([-1,0,49.999]),3,Parametreler())==0)
    assert zaman_kutlesi(-100,-1,3,p)==0


def test_normal_sag_kuyruk():
    assert normal_aralik(9.,10.)>0
    assert normal_aralik(9.,10.)==pytest.approx(float(normal_aralik(-10.,-9.)),rel=1e-14)


@pytest.mark.parametrize('bM',[0.8,1.,1.2])
def test_eta_telafi_gr_kimligi(bM):
    p = Parametreler(bM=bM)
    beta = p.b*LN10
    for target in (4.95,6.5):
        v = quad(lambda parent: beta*np.exp(-beta*(parent-p.m0))*eta(parent,p)*
                 buyukluk_yogunlugu(target,parent,p),p.m0,15,epsabs=1e-12)[0]
        assert v==pytest.approx(beta*np.exp(-beta*(target-p.m0)),rel=2e-9)


@pytest.mark.parametrize('telafi',[False,True])
def test_buyukluk_integrali(telafi):
    p = Parametreler(telafi=telafi)
    mass = buyukluk_kutlesi([4.95,5.05,9.05],[3.,5.],p)
    for j,(lo,hi) in enumerate(((4.95,5.05),(5.05,9.05))):
        for k,m in enumerate((3.,5.)):
            ref = quad(lambda v: buyukluk_yogunlugu(v,m,p),lo,hi,epsabs=1e-12)[0]
            assert mass[j,k]==pytest.approx(ref,rel=1e-10,abs=1e-13)


def test_beklenen_ppe_bos_gecmis_ve_logl():
    p = Parametreler(mu=1,r0=.7,olcek=2)
    ep = EEPAS(p,BOX)
    g = kutu_izgara(BOX)
    expected = 2*.7*10*(10**(-2)-10**(-3))
    got = ep.beklenen(EPOCH,EPOCH+10*GUN,frame(),g,[4.95,5.95])
    assert got.shape==(1,1)
    assert got.sum()==pytest.approx(expected)
    targets = frame([1,2,7],[5.,5.3,5.5])
    ell = np.log(ep.yogunluk(targets,frame())).sum()-expected
    assert log_olabilirlik(ep,targets,frame(),0,10,[4.95,5.95])==pytest.approx(ell)


def test_hucre_toplami_ve_zaman_bolme():
    p = Parametreler()
    ep = EEPAS(p,BOX)
    past = frame([-300,-10],[3.4,5.])
    g = pd.DataFrame([[10,12.5,39,41],[12.5,15,39,41],[10,12.5,41,43],[12.5,15,41,43]],
                     columns=kutu_izgara(BOX).columns)
    one = ep.beklenen_sayisal(0,400,past,kutu_izgara(BOX),[4.95,6.05])
    split = ep.beklenen_sayisal(0,400,past,g,[4.95,5.5,6.05])
    halves = ep.beklenen_sayisal(0,200,past,g,[4.95,6.05])+ep.beklenen_sayisal(200,400,past,g,[4.95,6.05])
    assert split.sum()==pytest.approx(one.sum(),rel=1e-12)
    assert halves.sum()==pytest.approx(one.sum(),rel=1e-12)
    assert np.all(split>=0)
    # Olay tam başlangıçta/gelecekteyse reddedilir; sessiz filtrelenmez.
    for mod in (ep,etas(),Janus(ep,etas(),.4)):
        with pytest.raises(ValueError,match='Geçmiş'):
            mod.beklenen(EPOCH,EPOCH+GUN,frame([0],[5.]),g,[4.95,6.])
        with pytest.raises(ValueError):
            mod.beklenen(EPOCH,EPOCH+GUN,frame(),g,[6.,5.])


def test_ppe_kutu_normalizasyonu():
    bg = ArkaPlan(BOX,frame([-100,-10],[5.,5.],[10.,14.9],[39.,42.9]),bant=30)
    assert bg.kutle(kutu_izgara(BOX)).sum()==pytest.approx(1)
    assert bg.yogunluk([0],[0])[0]==0
    g = kutu_izgara((38,44,9,16))
    assert bg.kutle(g).sum()==pytest.approx(1)
    assert bg.kutle(kutu_izgara((0,1,0,1))).sum()==0


def test_eepas_compensator_tek_oncu():
    p = Parametreler(mu=0,telafi=False,aT=1,bT=.5,sigmaA=3,bA=.3)
    ep = EEPAS(p,BOX)
    past = frame([-100],[3.])
    expected = (eta(3,p)*zaman_kutlesi(100,500,3,p)*buyukluk_kutlesi([4.95,6.],np.array([3.]),p)[0,0])
    sig = p.sigmaA*10**(p.bA*3/2)
    x0,x1,y0,y1 = ep.met.kutu_km()
    expected *= normal_aralik(x0/sig,x1/sig)*normal_aralik(y0/sig,y1/sig)
    assert ep.beklenen_sayisal(0,400,past,kutu_izgara(BOX),[4.95,6.]).sum()==pytest.approx(expected)


def test_etas_import_ve_sicak_gecmis_integrali():
    et = etas()
    past = frame([-100],[3.4])
    mu,K,c,alpha,p,D,q,gamma = et.theta
    I = ETAS._omori_ilke(np.array([101.]),c,p)[0]-ETAS._omori_ilke(np.array([100.]),c,p)[0]
    di = ETAS.mekan_olcegi(D,gamma,np.array([3.4]),et.m0)
    G = ETAS.mekan_kutu_integrali([12.5],[41.],di,q,BOX,metrik=et.met)
    base = mu+K*10**(alpha*(3.4-et.m0))*I*G
    mg = 10**(-2)-10**(-3)
    out = et.beklenen_sayisal(0,1,past,kutu_izgara(BOX),[4.95,5.95])
    assert out.sum()==pytest.approx(float(base[0]*mg),rel=1e-12)
    target = frame([.5],[5.])
    h = ETAS.mekan_cekirdegi(np.array([0.]),D,q,gamma,np.array([3.4]),et.m0)[0]
    ref = (mu/et.arka_plan.alan+K*10**(alpha*(3.4-et.m0))/(100.5+c)**p*h)*LN10*10**(-(5-et.m0))
    assert et.yogunluk(target,past)[0]==pytest.approx(ref)


def test_janus_uclar_ve_ig_bilinen():
    ep,et = EEPAS(Parametreler(),BOX),etas()
    past = frame([-400],[4.])
    args = (EPOCH,EPOCH+100*GUN,past,kutu_izgara(BOX),[4.95,6.])
    for w in (0,1,.37):
        np.testing.assert_allclose(Janus(ep,et,w).beklenen(*args),w*ep.beklenen(*args)+(1-w)*et.beklenen(*args))
    a = np.array([1.,2.,4.,8.])
    b = np.array([2.,1.,1.,2.])
    r = bilgi_kazanci(a,b,10,8)
    assert r['ig']==pytest.approx(np.log(a/b).mean()-.5)
    assert r['aralik95'][0]<r['ig']<r['aralik95'][1]
    identity = bilgi_kazanci(a,a,10,10)
    assert identity['ig']==0 and identity['p']==1
    with pytest.raises(ValueError):
        bilgi_kazanci([0],[1],1,1)
    assert bilgi_kazanci([],[],0,0)['ig'] is None
    assert agirlik_ayarla(a,a,10,10)['tanimlanabilir'] is False
    assert agirlik_ayarla([2,3],[1,1],1,1)['agirlik']==1
    assert agirlik_ayarla([1,1],[2,3],1,1)['agirlik']==0


def test_janus_agirlik_geri_kazanim():
    # Gerçek iki adaptörün hücre oranları, bağımsız Poisson örneklemi.
    ep,et = EEPAS(Parametreler(r0=.01),BOX),etas()
    past = frame([-1000,-100],[4.5,5.])
    grid = pd.DataFrame([[lo,lo+.5,la,la+.5] for lo in np.arange(10,15,.5)
                         for la in np.arange(39,43,.5)],columns=kutu_izgara(BOX).columns)
    e = ep.beklenen_sayisal(0,100,past,grid,[4.95,5.5,6.05]).ravel()
    t = et.beklenen_sayisal(0,100,past,grid,[4.95,5.5,6.05]).ravel()
    # Farklı hızları koru: integral düzeltmesi ağırlık tahmininin parçasıdır.
    scale = 50000/((.37*e+.63*t).sum())
    e,t = e*scale,t*scale
    counts = np.random.default_rng(473).poisson(.37*e+.63*t)
    r = agirlik_ayarla(np.repeat(e,counts),np.repeat(t,counts),e.sum(),t.sum())
    assert abs(r['agirlik']-.37)<.025


def test_arayuz_ayarsiz(monkeypatch):
    monkeypatch.setattr(arayuz,'_MODEL',None)
    with pytest.raises(RuntimeError):
        arayuz.beklenen(None,None,None,None,None)
    ep = EEPAS(Parametreler(),BOX)
    callback = arayuz.yapilandir(ep)
    args = (EPOCH,EPOCH+GUN,frame(),kutu_izgara(BOX),[4.95,6.])
    np.testing.assert_equal(callback(*args),arayuz.beklenen(*args))


def test_eepas_sentetik_geri_kazanim():
    rng = np.random.default_rng(471)
    past = frame(rng.uniform(-2500,-60,70),rng.uniform(2.95,5.5,70),
                 rng.uniform(10.3,14.7,70),rng.uniform(39.3,42.7,70))
    truth = Parametreler(r0=.003,mu=.2,olcek=4000,aT=1.,bT=.48,sigmaT=.45,
                         sigmaA=1.8,bA=.4,aM=1.1,bM=1,sigmaM=.35)
    ep = EEPAS(truth,BOX)
    targets = uret(ep,past,0,5000,[4.2,7.5],seed=474)
    start = replace(truth,mu=.35,olcek=1,aM=.9,bM=1.05,sigmaM=.44,
                    aT=1.2,bT=.42,sigmaT=.55,sigmaA=2.5,bA=.35)
    fit,r = ayarla(targets,past,0,5000,[4.2,7.5],start,BOX,
                   serbest=('mu','aM','bM','sigmaM','aT','bT','sigmaT','sigmaA','bA'),
                   maksiter=250,baslangiclar=[start])
    assert r['basari'],r
    assert abs(fit.p.mu-truth.mu)<.09
    assert abs(fit.p.aM-truth.aM)<.2
    assert abs(fit.p.bM-truth.bM)<.05
    assert abs(fit.p.sigmaM/truth.sigmaM-1)<.1
    assert abs(fit.p.bT-truth.bT)<.05
    assert abs(fit.p.sigmaT/truth.sigmaT-1)<.1
    assert abs(fit.p.bA-truth.bA)<.05
    assert abs(fit.p.aT-truth.aT)<.15
    assert abs(fit.p.sigmaA/truth.sigmaA-1)<.18
    assert abs(fit.p.olcek/truth.olcek-1)<.16
    assert fit.beklenen_sayisal(0,5000,past,kutu_izgara(BOX),[4.2,7.5]).sum()==pytest.approx(len(targets),rel=1e-10)


def test_gunluk_integral_hizli_yol_kamusal_arayuzla_ayni():
    from knotenlinie.eepas.dogrulama import gunluk_integraller
    # Gündüz gelen olay aynı gün kullanılmaz, sonraki gün kullanılabilir.
    past = frame([-1000,.5,1.9],[4.,4.5,5.])
    for mod in (EEPAS(Parametreler(gecikme=0),BOX),etas()):
        got = gunluk_integraller(mod,past,0,3,[4.95,6.05])
        ref = []
        for day in range(3):
            s = past.loc[past.zaman<EPOCH+day*GUN]
            ref.append(mod.beklenen(EPOCH+day*GUN,EPOCH+(day+1)*GUN,s,kutu_izgara(BOX),[4.95,6.05]).sum())
        np.testing.assert_allclose(got,ref,rtol=1e-12)


def test_etas_mle_duzgun_poisson_bilinen_cevap_json():
    from knotenlinie.eepas.janus import etas_ayarla
    targets = frame(np.arange(13)*7+1,np.linspace(3,4,13))
    mod,r = etas_ayarla(targets,frame(),0,100,[2.95,9.05],2.95,1.,BOX,maksiter=3)
    expected_mu = 13/(100*(1-10**(-(9.05-2.95))))
    assert mod.theta[0]==pytest.approx(expected_mu,rel=1e-4)
    # numpy.bool_ nedeniyle sonuçların kaybolması regresyonu.
    json.dumps(r,allow_nan=False)


def test_donusum_dogrulama_eslesmelerini_gormez():
    from knotenlinie.eepas.katalog import donusum_ayarla
    times = pd.to_datetime(['2008-01-01']*60+['2011-01-01']*60,utc=True)
    x = np.tile(np.linspace(2,5,30),4)
    typ = ['ML']*30+['Md']*30+['ML']*30+['Md']*30
    c = pd.DataFrame({'time_utc':times,'mag':1+.8*x})
    c.loc[60:,'mag'] = -50  # gelecekteki sahte büyüklük değişikliği ayarı etkilemez
    i = pd.DataFrame({'time_utc':times,'mag':x,'mag_type':typ})
    r = donusum_ayarla(c,i,[(j,j) for j in range(120)])
    for typ in ('ML','Md'):
        assert r[typ]['n']==30
        assert r[typ]['egim']==pytest.approx(.8)
        assert r[typ]['sabit']==pytest.approx(1)


def test_izgara_beklentileri_ve_t_puanlama():
    from knotenlinie.eepas.dogrulama import ic_dogrulama
    ep = EEPAS(Parametreler(mu=1,r0=.2),BOX)
    data = pd.concat([frame([-100],[4.]),pd.DataFrame({
        'zaman':pd.to_datetime(['2011-01-01T12:00:00Z','2011-01-02T12:00:00Z']),
        'mw':[5.,5.2],'boylam':[12.1,12.2],'enlem':[41.1,41.2],'derinlik':[10.,10.]})],ignore_index=True)
    scores = ic_dogrulama({'EEPAS':ep,'ETAS':ep},data,
                          pd.Timestamp('2011-01-01',tz='UTC'),pd.Timestamp('2011-01-03',tz='UTC'))
    assert scores['n']==2
    assert scores['tablo']['EEPAS']['etas_karsisinda']['ig']==0
    assert scores['tablo']['EEPAS']['etas_karsisinda']['p']==1


def test_dosyadan_bagimsiz_arayuz_ve_ayar_kapisi(tmp_path):
    from dataclasses import asdict
    ep,et = EEPAS(Parametreler(),BOX),etas()
    cfg = {'kutu':BOX,'hazir':True,'ayar_bitis':'2011-01-01T00:00:00Z',
           'ppe_merkezler':[],'ppe_bant':25.,'ppe_duzgun_pay':.05,
           'eepas':{'parametreler':asdict(ep.p)},
           'etas':{'parametreler':dict(zip(ETAS.UZAY_ADLARI,et.theta)),'m0':et.m0,'b':et.b},
           'janus':{'agirlik':.37}}
    path = tmp_path/'model.json'
    path.write_text(json.dumps({'italya_model':cfg}))
    args = (EPOCH,EPOCH+100*GUN,frame([-500],[4.]),kutu_izgara(BOX),[4.95,6.05])
    for tur,mod in [('eepas',ep),('etas',et),('janus',Janus(ep,et,.37))]:
        np.testing.assert_allclose(arayuz.dosyadan(path,tur)(*args),mod.beklenen(*args))
    cfg['hazir'] = False
    path.write_text(json.dumps(cfg))
    with pytest.raises(ValueError,match='Yakınsamamış'):
        arayuz.dosyadan(path)
    cfg['hazir'] = True
    cfg['ayar_bitis'] = '2011-01-02T00:00:00Z'
    path.write_text(json.dumps(cfg))
    with pytest.raises(ValueError,match='2010'):
        arayuz.dosyadan(path)
