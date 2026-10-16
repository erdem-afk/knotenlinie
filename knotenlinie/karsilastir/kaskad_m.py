"""Experiment M: donmuş ortak ETAS gün içi kaskadının 2011–2015 ölçümü."""
from __future__ import annotations

import argparse
import gc
import json
from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd

from knotenlinie.kaskad.arayuz import KaskadETAS
from knotenlinie.etas_lm.arayuz import ETASLM
from knotenlinie.etas_lm.arka_plan import SON as AYAR_SON
from knotenlinie.ortak_zemin.arayuz import ayar_tabani
from knotenlinie.ortak_zemin.veri import VERI, katalog_oku, sha256
from knotenlinie.yollar import KOSU, kayit_hazirla
from .kosucu import Model, kos, karsilastir, utc
from .ortak4 import AyriGecmis, gecmis_ayari, gecmis_filtrele, ayristir, rss_byte
from .gunluk_j import BAS, SON, TOHUM, esik_kosu, tek_model_ozeti
from .komut import json_temiz

OUT = KOSU / 'M'   # kayit_hazirla seeds frozen inputs from records/M/ when that folder exists


def yakinsama(model, cat, ayar, edges):
    """İlk gün ve en büyük doğrulama olayını izleyen gün; ayar/seçim değil."""
    hcat = gecmis_filtrele(cat, ayar)
    window = hcat[(hcat.zaman >= utc(BAS)) & (hcat.zaman < utc(SON)-pd.Timedelta(days=1))]
    peak = window.loc[window.mw.idxmax(), 'zaman'].normalize()+pd.Timedelta(days=1)
    rows = []
    original = model.adim, model.nesil
    for a in sorted(set([utc(BAS), peak])):
        h = hcat[hcat.zaman < a]
        z = a+pd.Timedelta(days=1)
        model.adim, model.nesil = original
        first = model.beklenen(a,z,h,model.izgara,edges)
        model.adim, model.nesil = original[0]*2, original[1]
        time_fine = model.beklenen(a,z,h,model.izgara,edges)
        model.adim, model.nesil = original[0], original[1]*2
        gen_fine = model.beklenen(a,z,h,model.izgara,edges)
        def diff(fine):
            return dict(Lambda=float(fine.sum()), goreli_L1=float(np.abs(first-fine).sum()/fine.sum()),
                        goreli_Lambda=float((fine.sum()-first.sum())/fine.sum()))
        rows.append(dict(gun=a.isoformat(), Lambda=float(first.sum()),
                         zaman_sik=diff(time_fine), nesil_sik=diff(gen_fine)))
    model.adim, model.nesil = original
    # Mekân ve GR ayrı sıklaştırılır; uniform-hücre temsil hatasını ölçmez.
    a, z = utc(BAS), utc(BAS)+pd.Timedelta(days=1)
    h = hcat[hcat.zaman < a]
    first = model.beklenen(a,z,h,model.izgara,edges)
    for label, space, gr in [('uzay_sik', model.uzay_dugum*2, model.gr_dugum),
                             ('GR_sik', model.uzay_dugum, model.gr_dugum*2)]:
        fine_model = KaskadETAS(model.taban,adim=model.adim,nesil=model.nesil,
                               uzay_dugum=space,gr_dugum=gr)
        fine = fine_model.beklenen(a,z,h,model.izgara,edges)
        rows[0][label] = dict(Lambda=float(fine.sum()), goreli_L1=float(np.abs(first-fine).sum()/fine.sum()),
                             goreli_Lambda=float((fine.sum()-first.sum())/fine.sum()))
        del fine_model
        gc.collect()
    return dict(adimlar=[original[0],original[0]*2], nesiller=[original[1],original[1]*2],
                uzay_dugumler=[model.uzay_dugum,model.uzay_dugum*2],
                GR_dugumler=[model.gr_dugum,model.gr_dugum*2], gunler=rows,
                notu='Tanı; doğrulamadan parametre/sayısal ayar seçilmez')


def cift(aday, taban, clusters):
    pair = karsilastir(aday,taban)
    pair['ayristirma'] = ayristir(aday,taban,clusters)
    return pair


def olc_bolge(bolge, args):
    start = time.monotonic()
    path = VERI/'ortak'/f'{bolge}_katalog_le2015.csv'
    cat = katalog_oku(path)
    base = ayar_tabani(bolge,son='2011-01-01')
    if sha256(path) != base.p['katalog_sha256']:
        raise ValueError('Donmuş katalog SHA256 uyuşmuyor')
    grid = base.izgara.copy()
    if bolge != 'italya':
        raise ValueError(f'M: yalnız italya tanımlı, {bolge!r} değil')
    edges = np.r_[np.round(np.arange(3.95,9.0,.1),2),np.inf]
    depth = (0,30)
    ayar = gecmis_ayari(base,bolge)
    clusters = gecmis_filtrele(cat,ayar)
    cascade = KaskadETAS(base,adim=args.adim,nesil=args.nesil)
    convergence = yakinsama(cascade,cat,ayar,edges)
    # Tanı günleri sayısal kuyruk maksimumuna dahil edilmez.
    cascade.max_last_ratio = cascade.max_remainder_ratio = 0.
    models = [Model('ortak-ETAS',AyriGecmis(base,cat,ayar).beklenen,True,ayar),
              Model('kaskad-ETAS',AyriGecmis(cascade,cat,ayar).beklenen,True,ayar)]
    runs = kos(models,BAS,SON,cat,grid,edges,bolge=bolge,derinlik=depth)
    meta = dict(cascade.metadata, son_nesil_ham_payi_ust_max=cascade.max_last_ratio,
                atlanan_kuyruk_goreli_ust_max=cascade.max_remainder_ratio,
                mc=base.mc,b=base.b, parametreler=base.th, gecmis=ayar)
    del models, cascade, base
    gc.collect()
    print(bolge,'ortak+kaskad tamamlandı',time.monotonic()-start,'RSS GB',rss_byte()/1e9,flush=True)
    lm = ETASLM(cat[cat.zaman < AYAR_SON],grid,adim=32,nesil=10)
    box = lm.met.kutu
    lm_ayar = dict(sinir=(box[2],box[3],box[0],box[1]),baslangic_yil=2005,derinlik_max=30)
    runs.update(kos([Model('ETAS-LM-yeniden-kurulum',lm.beklenen,True,lm_ayar)],
                    BAS,SON,cat,grid,edges,bolge=bolge,derinlik=depth))
    lm_meta = dict(lm.metadata,son_nesil_ham_payi_ust_max=lm.max_last_ratio)
    del lm
    gc.collect()
    rows = []
    for alt in (3.95,4.95):
        sub = {name: esik_kosu(run,grid,edges,alt) for name,run in runs.items()}
        summaries = {name: tek_model_ozeti(run,args.tekrar) for name,run in sub.items()}
        candidate = sub['kaskad-ETAS']
        for name in ('ortak-ETAS','ETAS-LM-yeniden-kurulum'):
            rows.append(dict(bolge=bolge,M_alt=alt,N=len(candidate.olaylar),
                             aday=summaries['kaskad-ETAS'],taban=summaries[name],
                             cift=cift(candidate,sub[name],clusters)))
    print(bolge,'ölçüm tamamlandı',time.monotonic()-start,flush=True)
    return dict(bolge=bolge,hucre=len(grid),derinlik=depth,
                m_kenarlar=[float(x) if np.isfinite(x) else '+inf' for x in edges],
                kaskad=meta,ETAS_LM=lm_meta,yakinsama=convergence,satirlar=rows,
                duvar_saniye=time.monotonic()-start)


def main():
    kayit_hazirla('M')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--cikti',type=Path,default=OUT/'OLCUM.json')
    ap.add_argument('--tekrar',type=int,default=10000)
    ap.add_argument('--adim',type=int,default=32)
    ap.add_argument('--nesil',type=int,default=10)
    ap.add_argument('--bolge',choices=['italya'],default='italya')
    args = ap.parse_args()
    start = time.monotonic()
    results = [olc_bolge(b,args) for b in (args.bolge,)]
    sources = [VERI/'ortak'/f'italya_{s}' for s in ('katalog_le2015.csv','izgara.csv')]
    sources += [VERI/'ortak'/'etas_italya_le2010.json']
    codes = sorted(Path('knotenlinie/kaskad').glob('*.py')) + [Path(__file__),Path('knotenlinie/karsilastir/kosucu.py'),
            Path('knotenlinie/karsilastir/puan.py'),Path('knotenlinie/ortak_zemin/arayuz.py'),
            Path('knotenlinie/etas/model.py'),Path('knotenlinie/etas_lm/arayuz.py'),Path('knotenlinie/etas_lm/cekirdek.py')]
    out = dict(durum='PROVISIONAL; bağımsız skor incelemesi bekler',baslangic=BAS,bitis_haric=SON,
               tekrar=args.tekrar,tohum=TOHUM,M_tohum=TOHUM+1,bolgeler=results,
               IG_tanimi='kaskad − taban: ortalama log(lambda_kaskad/lambda_taban) − (Lambda_kaskad−Lambda_taban)/N',
               NSM_notu='N analitik iki Poisson kuyruğu; S/M sabit N, zamandan toplanmış oran, 10000 multinomial. Günlük adaptif modelde operasyonel tanı; koşulsuz ETAS testi değil.',
               p_notu='Ham iki yönlü T/W; kümelenme altında bağımsızlık varsayımı, üstünlük hükmü değil.',
               kumelenme_tanimi='H4: aynı okuyucunun bölgesel hemen önceki M>=4.5 olayı; tam zaman <olay, <=30 gün ve <=50 km. İntegral gruplara keyfî dağıtılmaz.',
               kapilar='Yalnız ≤2015 kataloglar; ayar <2011; gün başı geçmiş; doğrulamadan parametre ayarı yok.',
               kaynak_SHA256={str(p):sha256(p) for p in sources},kod_SHA256={str(p):sha256(p) for p in codes},
               duvar_saniye=time.monotonic()-start,rss_tepe_byte=rss_byte(),python=sys.version,
               numpy=np.__version__,pandas=pd.__version__)
    args.cikti.parent.mkdir(parents=True,exist_ok=True)
    args.cikti.write_text(json.dumps(json_temiz(out),ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(args.cikti,'s=',out['duvar_saniye'],'RSS GB',rss_byte()/1e9,flush=True)


if __name__ == '__main__':
    main()
