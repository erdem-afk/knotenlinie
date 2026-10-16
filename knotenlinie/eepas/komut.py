"""python -m knotenlinie.eepas.komut {italya,sentetik}."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from dataclasses import replace, asdict

import numpy as np
import pandas as pd

from .model import Parametreler, ArkaPlan, EEPAS, ayarla, zaman_gun, kutu_izgara
from .janus import etas_ayarla, janus_ayarla, ETASModel
from .katalog import italya_oku, oncu_esigi, kesik_oku, AYAR_SONU
from .dogrulama import ic_dogrulama
from .benzetim import uret
from knotenlinie.yollar import KOSU, VERI


def yaz(yol, data):
    path = Path(yol)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def gercek(args):
    start = time.monotonic()
    if args.bolge!='italya':
        raise ValueError(f'yalnız italya tanımlı, {args.bolge!r} değil')
    df,meta = italya_oku(args.veri)
    box = (35.,48.,6.,20.)
    df = df.loc[df.derinlik<=70].copy()
    mc,comp = oncu_esigi(df)
    if mc>=4.95:
        raise ValueError('Tamlık eşiği hedefe ulaşıyor; EEPAS öncü kapısı kapalı')
    train = df.loc[df.zaman<AYAR_SONU].copy()
    t0,t1 = zaman_gun([args.ayar_baslangic,AYAR_SONU])
    targets = train.loc[(train.zaman>=args.ayar_baslangic)&(train.mw>=4.95)&(train.mw<9.05)].copy()
    parents = train.loc[train.mw>=mc].copy()
    precursor_fit = parents.loc[parents.zaman>=args.ayar_baslangic]
    if len(targets)<20 or len(precursor_fit)<100:
        raise ValueError('Bölgesel ayar için yetersiz olay')
    b = float(np.log10(np.e)/(precursor_fit.mw.mean()-mc))
    r0 = len(precursor_fit)/(t1-t0)
    warmup = train.loc[(train.zaman<args.ayar_baslangic)&(train.mw>=4.95)]
    bg = ArkaPlan(box,warmup,bant=25,duzgun_pay=.05)
    p = Parametreler(m0=mc,b=b,r0=r0)
    ep,er = ayarla(targets,parents,t0,t1,[4.95,9.05],p,box,bg,maksiter=args.maksiter)
    print('EEPAS',er['basari'],er['parametreler'],flush=True)
    et,tr = etas_ayarla(targets,parents,t0,t1,[4.95,9.05],mc,b,box,bg,maksiter=args.maksiter)
    print('ETAS',tr['basari'],tr['parametreler'],flush=True)
    ja,jr = janus_ayarla(ep,et,targets,parents,t0,t1,[4.95,9.05])
    cfg = {'bolge':args.bolge,'kutu':box,'ayar_baslangic':args.ayar_baslangic,
           'ayar_bitis':AYAR_SONU.isoformat(),'ppe_merkezler':bg.merkezler.values.tolist(),
           'ppe_bant':bg.bant,'ppe_duzgun_pay':bg.duzgun_pay,'eepas':er,'etas':tr,'janus':jr,
           'girdi':meta,'tamlik':comp,'n_ayar_hedef':len(targets),'n_oncu':len(parents),
           'n_ppe':len(warmup),'derinlik_ust':70,'hazir':er['basari'] and tr['basari']}
    yaz(Path(args.cikti)/'model.json',cfg)
    if not cfg['hazir']:
        raise RuntimeError('MLE yakınsamadı; model kaydedildi ama doğrulama/skor yürütülmedi')
    scores = ic_dogrulama({'EEPAS':ep,'Janus':ja,'ETAS':et},df,
                         pd.Timestamp('2011-01-01',tz='UTC'),pd.Timestamp('2016-01-01',tz='UTC'))
    scores['sure_saniye'] = time.monotonic()-start
    scores['uyari'] = 'Kaba İtalya kutusu ve proxy Mw; ana CSEP kıyası/kör test değildir'
    yaz(Path(args.cikti)/'dogrulama.json',scores)
    print(json.dumps(scores['tablo'],ensure_ascii=False,indent=2))


def sentetik(args):
    from .model import EPOCH
    rng = np.random.default_rng(471)
    n = 70
    parents = pd.DataFrame({'zaman':EPOCH+pd.to_timedelta(rng.uniform(-2500,-60,n),unit='D'),
                            'mw':rng.uniform(2.95,5.5,n),'boylam':rng.uniform(10.3,14.7,n),
                            'enlem':rng.uniform(39.3,42.7,n),'derinlik':10.})
    box = (39.,43.,10.,15.)
    truth = Parametreler(r0=.003,mu=.2,olcek=4000,aT=1.,bT=.48,sigmaT=.45,
                         sigmaA=1.8,bA=.4,aM=1.1,bM=1,sigmaM=.35)
    ep = EEPAS(truth,box)
    targets = uret(ep,parents,0,5000,[4.2,7.5],seed=474)
    start = replace(truth,mu=.35,olcek=1,aM=.9,bM=1.05,sigmaM=.44,
                    aT=1.2,bT=.42,sigmaT=.55,sigmaA=2.5,bA=.35)
    keys = ('mu','aT','sigmaA') if not args.tum_parametreler else ('mu','aM','bM','sigmaM','aT','bT','sigmaT','sigmaA','bA')
    fit,res = ayarla(targets,parents,0,5000,[4.2,7.5],start,box,serbest=keys,
                    maksiter=args.maksiter,baslangiclar=[start])
    yaz(Path(args.cikti)/'sentetik.json',{'n':len(targets),'seed':474,'dogru':asdict(truth),
                                         'sonuc':res,'tur':'Sabit dış öncülere koşullu Poisson; ebeveyn etiketleri MLEye verilmedi'})
    print(json.dumps({'n':len(targets),'dogru':asdict(truth),'sonuc':res},indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bolge',choices=['italya','sentetik'])
    parser.add_argument('--veri',default=str(VERI / 'kesik-2015'))
    parser.add_argument('--katalog')
    parser.add_argument('--kutu',nargs=4,type=float)
    parser.add_argument('--ayar-baslangic',default='1995-01-01T00:00:00Z')
    parser.add_argument('--cikti',default=str(KOSU / 'C/kosu'))
    parser.add_argument('--maksiter',type=int,default=300)
    parser.add_argument('--tum-parametreler',action='store_true')
    args = parser.parse_args()
    if args.bolge=='sentetik':
        sentetik(args)
    else:
        gercek(args)


if __name__=='__main__':
    main()
