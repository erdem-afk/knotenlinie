"""Deney N: sabit 2 çekirdek × 2 kaskad, yalnız 2011–2015 J çerçevesi."""
from __future__ import annotations
import argparse
import gc
import json
from pathlib import Path
import sys
import time
import numpy as np
import pandas as pd
from knotenlinie.etas import model as M
from knotenlinie.etas_mc25.tamlik import tani
from knotenlinie.etas_mc25.mle import Olabilirlik,ayarla
from knotenlinie.etas_mc25.arayuz import yukle,SigGecmis,DIZIN
from knotenlinie.ortak_zemin.ayar import b_ayarla,gr_ayar_paylari,dallanma
from knotenlinie.ortak_zemin.arka_plan import arka_plan_sec
from knotenlinie.ortak_zemin.arayuz import ayar_tabani
from knotenlinie.ortak_zemin.veri import VERI,katalog_oku,sha256,json_yaz
from knotenlinie.yollar import KOSU, kayit_hazirla
from knotenlinie.etas_lm.arayuz import ETASLM
from knotenlinie.etas_lm import cekirdek as LM
from .kosucu import Model,kos,karsilastir,utc
from .ortak4 import AyriGecmis,gecmis_ayari,gecmis_filtrele,ayristir,rss_byte
from .gunluk_j import BAS,SON,TOHUM,esik_kosu,tek_model_ozeti
from .puan import holm

OUT = KOSU / 'N'   # kayit_hazirla seeds frozen inputs from records/N/ when that folder exists
VARIANTS=('ortak-dogrudan','ortak-kaskad','lm-dogrudan','lm-kaskad')


def kur(cat,grid,*,maksiter=300):
    start=time.monotonic()
    DIZIN.mkdir(parents=True,exist_ok=True)
    train=cat[(cat.zaman<utc(BAS))&(cat.derinlik<30)]
    completeness=tani(train)
    json_yaz(DIZIN/'tamlik.json',completeness)
    year=completeness['baslangic_yili']; epoch=pd.Timestamp(f'{year}-01-01',tz='UTC')
    d=train[(train.zaman>=epoch)&(train.mw>=2.5)].reset_index(drop=True)
    kutu=(grid.enlem_min.min(),grid.enlem_max.max(),grid.boylam_min.min(),grid.boylam_max.max())
    b=b_ayarla(d.mw.to_numpy(),2.5)
    hist=arka_plan_sec(d,kutu,utc(BAS))
    T=float((utc(BAS)-epoch)/pd.Timedelta(days=1))
    t=((d.zaman-epoch)/pd.Timedelta(days=1)).to_numpy(float)
    L=Olabilirlik(t,d.mw.to_numpy(float),d.boylam.to_numpy(float),d.enlem.to_numpy(float),
                 2.5,b['deger'],T,kutu,M.arka_plan_degeri(d.boylam,d.enlem,hist))
    for tur in ('ortak','lm'):
        print('MLE',tur,'N',len(d),'başlangıç',year,'KDE',hist['bant_km'],hist['zemin_payi'],flush=True)
        fit=ayarla(L,tur,maksiter=maksiter)
        fit.update(mc=2.5,b=b,baslangic_yili=year,ayar_baslangic=epoch.isoformat(),ayar_bitis=BAS,
                   ayar_max_zaman=d.zaman.max().isoformat(),ayar_n=len(d),kutu=kutu,
                   arka_plan=hist,metrik=M.yerel_metrik(kutu).kayit(),normalizasyon=M.NORMALIZASYON,
                   tamlik=completeness,gr_ayar_paylari=gr_ayar_paylari(d.mw,2.5,b['deger']),
                   katalog_sha256=sha256(VERI/'ortak/italya_katalog_le2015.csv'),
                   izgara_sha256=sha256(VERI/'ortak/italya_izgara.csv'),duvar_saniye=time.monotonic()-start)
        json_yaz(DIZIN/f'etas_{tur}.json',fit)
        print('MLE bitti',tur,fit['parametreler'],'n',fit['dallanma'],'s',time.monotonic()-start,flush=True)
    del L
    gc.collect()


def ozet(run,tekrar):
    result=tek_model_ozeti(run,tekrar)
    result['Lambda_bolu_N']=result['Lambda']/result['N'] if result['N'] else None
    return result


def olc(cat,grid,args):
    start=time.monotonic()
    edges=np.r_[np.round(np.arange(3.95,9.,.1),2),np.inf]
    base=ayar_tabani('italya',son='2011-01-01')
    if sha256(VERI/'ortak/italya_katalog_le2015.csv')!=base.p['katalog_sha256']:
        raise ValueError('J taban katalog hashı uyuşmuyor')
    ayar=gecmis_ayari(base,'italya');clusters=gecmis_filtrele(cat,ayar)
    runs=kos([Model('ortak-ETAS',AyriGecmis(base,cat,ayar).beklenen,True,ayar)],BAS,SON,cat,grid,edges,bolge='italya',derinlik=(0,30))
    base_meta=dict(parametreler=base.th,mc=base.mc,b=base.b,dallanma=dallanma(base.th,base.b),gecmis=ayar)
    del base;gc.collect()
    print('Ortak skor bitti',time.monotonic()-start,flush=True)
    lm=ETASLM(cat[cat.zaman<utc(BAS)],grid,adim=32,nesil=10)
    box=lm.met.kutu
    lm_ayar=dict(sinir=(box[2],box[3],box[0],box[1]),baslangic_yil=2005,derinlik_max=30)
    runs.update(kos([Model('ETAS-LM',lm.beklenen,True,lm_ayar)],BAS,SON,cat,grid,edges,bolge='italya',derinlik=(0,30)))
    lm_meta=dict(lm.metadata,dallanma_kesilmemis=float(LM.K*LM.C**(1-LM.P)/(LM.P-1)*LM.B*np.log(10)/(LM.B*np.log(10)-LM.ALPHA)))
    del lm;gc.collect()
    print('LM skor bitti',time.monotonic()-start,flush=True)
    params={}; convergence={}
    for tur in ('ortak','lm'):
        p=json.loads((DIZIN/f'etas_{tur}.json').read_text())
        params[tur]=p
        model=yukle(tur,grid,kaskad=True,adim=args.adim,nesil=args.nesil)
        settings=gecmis_ayari(model.taban,'italya');settings['derinlik_max']=30
        # Aynı taban/cache; doğrudan ve kaskad ayrı sabit satırlar.
        for cascade in (False,True):
            name=tur+('-kaskad' if cascade else '-dogrudan')
            candidate=model if cascade else model.taban
            runs.update(kos([Model(name,SigGecmis(candidate,cat,settings).beklenen,True,settings)],
                            BAS,SON,cat,grid,edges,bolge='italya',derinlik=(0,30)))
            print(name,'bitti',time.monotonic()-start,'RSS',rss_byte()/1e9,flush=True)
        # İlk gün; parametre/sayısal ayar seçimi değil. Kuyruk tanısı gerçek koşudan.
        convergence[tur]=dict(model.metadata,son_nesil_ham_payi_ust_max=model.max_last_ratio,
                              atlanan_kuyruk_goreli_ust_max=model.max_remainder_ratio)
        a=utc(BAS);h=gecmis_filtrele(cat,settings);h=h[(h.zaman<a)&(h.derinlik<30)&(h.mw>=2.5)]
        first=model.beklenen(a,a+pd.Timedelta(days=1),h,grid,edges)
        model.adim*=2
        fine=model.beklenen(a,a+pd.Timedelta(days=1),h,grid,edges)
        convergence[tur]['ilk_gun_zaman_L1']=float(abs(first-fine).sum()/fine.sum())
        del model,candidate;gc.collect()
    rows=[]
    for alt in (3.95,4.95):
        sub={name:esik_kosu(run,grid,edges,alt) for name,run in runs.items()}
        summaries={name:ozet(run,args.tekrar) for name,run in sub.items()}
        comparisons={}
        for name in VARIANTS:
            comparisons[name]={}
            for ref in ('ETAS-LM','ortak-ETAS'):
                c=karsilastir(sub[name],sub[ref])
                c['ayristirma']=ayristir(sub[name],sub[ref],clusters)
                comparisons[name][ref]=c
        for ref in ('ETAS-LM','ortak-ETAS'):
            for field in ('p_T','p_W'):
                adjusted=holm([comparisons[name][ref][field] for name in VARIANTS])
                for name,value in zip(VARIANTS,adjusted):comparisons[name][ref][field+'_Holm4']=value
        rows.append(dict(M_alt=alt,modeller=summaries,ciftler=comparisons))
    return dict(satirlar=rows,parametreler=params,ortak=base_meta,ETAS_LM=lm_meta,kaskad_tani=convergence,
                tamlik=json.loads((DIZIN/'tamlik.json').read_text()),duvar_saniye=time.monotonic()-start)


def main():
    kayit_hazirla('N')
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--asama',choices=['ayar','olcum','hepsi'],default='hepsi')
    ap.add_argument('--cikti',type=Path,default=OUT/'OLCUM.json')
    ap.add_argument('--tekrar',type=int,default=10000)
    ap.add_argument('--adim',type=int,default=32)
    ap.add_argument('--nesil',type=int,default=10)
    ap.add_argument('--maksiter',type=int,default=300)
    args=ap.parse_args();OUT.mkdir(parents=True,exist_ok=True)
    cat=katalog_oku(VERI/'ortak/italya_katalog_le2015.csv')
    grid=pd.read_csv(VERI/'ortak/italya_izgara.csv')
    if args.asama in ('ayar','hepsi'):kur(cat,grid,maksiter=args.maksiter)
    if args.asama=='ayar':return
    result=olc(cat,grid,args)
    sources=[VERI/'ortak/italya_katalog_le2015.csv',VERI/'ortak/italya_izgara.csv',VERI/'ortak/etas_italya_le2010.json']
    sources+=list(DIZIN.glob('*.json'))
    code=list(Path('knotenlinie/etas_mc25').glob('*.py'))+[Path(__file__),Path('knotenlinie/karsilastir/kosucu.py'),Path('knotenlinie/karsilastir/puan.py'),Path('knotenlinie/kaskad/arayuz.py'),Path('knotenlinie/kaskad/cekirdek.py'),Path('knotenlinie/ortak_zemin/arayuz.py'),Path('knotenlinie/etas/model.py')]
    result.update(durum='PROVISIONAL; bağımsız skor-kodu incelemesi bekler; kör üstünlük hükmü değil',
                  baslangic=BAS,bitis_haric=SON,derinlik=[0,30],hucre=len(grid),varyantlar=VARIANTS,
                  tekrar=args.tekrar,tohum=TOHUM,M_tohum=TOHUM+1,
                  IG_tanimi='aday − taban; mean log(lambda_aday/lambda_taban) − (Lambda_aday−Lambda_taban)/N',
                  Holm='Her eşik, referans ve T/W için sabit dört varyant ailesi; ek eşik keşifseldir',
                  kumelenme='J/H4 bölgesel hemen önceki M≥4.5, tam zaman <hedef, ≤30g/50km; herhangi önceki duyarlılığı da yazılır; integral gruplara dağıtılmaz',
                  NSM_notu='N analitik iki Poisson kuyruğu; S/M sabit N 10000 multinomial, tohum 20261005/20261006; adaptif modelde operasyonel tanı, koşulsuz ETAS testi değil',
                  p_notu='İki yönlü T/W, olay bağımsızlığı varsayar; kümelenmede ihtiyatlı yorumlanır',
                  kapilar='Yalnız ≤2015 katalog; tamlık/b/KDE/MLE <2011; kaynak ebeveynler [0,30), günlük başlangıç öncesi; 2016+ erişim/indirme yok',
                  kaynak_SHA256={str(p):sha256(p) for p in sources},kod_SHA256={str(p):sha256(p) for p in code},
                  rss_tepe_byte=rss_byte(),python=sys.version,numpy=np.__version__,pandas=pd.__version__)
    json_yaz(args.cikti,result)
    print(args.cikti,'RSS GB',rss_byte()/1e9,flush=True)

if __name__=='__main__':main()
