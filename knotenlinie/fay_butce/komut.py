"""İtalya 2011–2015 küçük iç doğrulama koşusu; kör pencere açılmaz."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd

from .butce import YIL_SANIYE, yillik, karisim
from .skor import sayim, ayarla, bilgi_kazanci
from .taban import Duzlestirilmis
from .veri import fay_oku, cpti_oku, sha256


def italya_izgara(yol):
    """pyCSEP İtalya şablonunun orta noktalarını 0.1° hücreye çevir."""
    r = ET.parse(yol).getroot()
    dim = next(x for x in r.iter() if x.tag.endswith('defaultCellDimension'))
    dx, dy = float(dim.attrib['lonRange']), float(dim.attrib['latRange'])
    cells = [x.attrib for x in r.iter() if x.tag.endswith('cell')]
    return pd.DataFrame([dict(boylam_min=round(float(c['lon'])-dx/2,8),
                             boylam_max=round(float(c['lon'])+dx/2,8),
                             enlem_min=round(float(c['lat'])-dy/2,8),
                             enlem_max=round(float(c['lat'])+dy/2,8)) for c in cells])


def _yaz(yol, d):
    # Desteksiz bir doğrulama olayı gerçek -inf skorudur, yazıcı hatası değil.
    def seri(x):
        if isinstance(x, dict):
            return {k:seri(v) for k,v in x.items()}
        if isinstance(x, (list, tuple)):
            return [seri(v) for v in x]
        if isinstance(x, float) and np.isinf(x):
            return '-inf' if x < 0 else 'inf'
        return x  # NaN halen allow_nan=False ile reddedilir.
    Path(yol).write_text(json.dumps(seri(d), indent=2, ensure_ascii=False, allow_nan=False)+'\n', encoding='utf-8')


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--fay', required=True)
    p.add_argument('--katalog', required=True)
    p.add_argument('--izgara', required=True)
    p.add_argument('--cikti', required=True)
    p.add_argument('--kaynak-en-gec', help='opsiyonel kaynak güncelleme kesimi (UTC ISO)')
    p.add_argument('--son-kutu-acik', action='store_true', help='son kenarı +inf yap (açık üst kutu)')
    args = p.parse_args(argv)
    out = Path(args.cikti)
    out.mkdir(parents=True, exist_ok=True)
    fay = fay_oku(args.fay, surum='DISS3.2.0', en_gec=args.kaynak_en_gec)
    katalog = cpti_oku(args.katalog)
    grid = italya_izgara(args.izgara)
    edges = np.round(np.arange(4.95, 9.051, 0.1), 8)
    if args.son_kutu_acik:
        edges[-1] = np.inf
    katalog = katalog.loc[katalog.mw >= edges[0]].copy()
    t0,t1,t2,t3 = [pd.Timestamp(s,tz='UTC') for s in ('1950-01-01','1991-01-01','2011-01-01','2016-01-01')]
    egitim = katalog.loc[katalog.zaman < t1].copy()
    ayar = katalog.loc[(katalog.zaman>=t1)&(katalog.zaman<t2)]
    dogrulama = katalog.loc[(katalog.zaman>=t2)&(katalog.zaman<t3)]
    # Eğitim de aynı bölgeye kesilir; dış hücre olayları KDE hızına eklenmez.
    from .butce import izgara_dogrula
    a = izgara_dogrula(grid)
    keep = [np.any((a[:,0]<=r.boylam)&(r.boylam<a[:,1])&(a[:,2]<=r.enlem)&(r.enlem<a[:,3]))
            for r in egitim.itertuples(index=False)]
    egitim = egitim.loc[keep]
    egitim_yolu = out/'egitim_le1990.csv'
    egitim.to_csv(egitim_yolu, index=False)
    taban = Duzlestirilmis(egitim, baslangic=t0,bitis=t1).beklenen
    taban_adi = 'duzlestirilmis'
    bos = egitim.iloc[:0]
    base_ayar = taban(t1,t2,bos,grid,edges)
    base_val = taban(t2,t3,bos,grid,edges)
    counts_ayar,dis_ayar = sayim(ayar,grid,edges)
    counts_val,dis_val = sayim(dogrulama,grid,edges)
    raw = {s:yillik(fay,grid,edges,sigma_km=s) for s in (5,10,20,40)}
    yil_ayar = (t2-t1).total_seconds()/YIL_SANIYE
    aday = {s:r*yil_ayar for s,r in raw.items()}
    sonuclar = {}
    for mod in ('fiziksel','toplam_esit'):
        esitle = mod == 'toplam_esit'
        fit = ayarla(base_ayar,aday,counts_ayar,baslangic=t1,bitis=t2,toplam_esitle=esitle)
        # Var olan hesap yeniden kullanılabilir: doğrulama olayları üreticiye gitmez.
        raw_val = raw[fit['sigma_km']] * ((t3-t2).total_seconds()/YIL_SANIYE)
        pred = karisim(base_val,raw_val,fit['agirlik'],toplam_esitle=esitle)
        sonuclar[mod] = dict(ayar=fit,dogrulama=bilgi_kazanci(pred,base_val,counts_val),
                             fay_ham_yillik=float(raw[fit['sigma_km']].sum()))
        config = dict(fay_yolu=str(Path(args.fay).resolve()),surum='DISS3.2.0',
                      taban='duzlestirilmis',
                      agirlik=fit['agirlik'],sigma_km=fit['sigma_km'],toplam_esitle=esitle,
                      b=1,mmin=2.4,esik=4.95,egitim_yolu=str(egitim_yolu.resolve()),
                      egitim_baslangic=t0.isoformat(),egitim_bitis=t1.isoformat(),taban_sigma_km=30)
        if args.kaynak_en_gec:
            config['kaynak_en_gec'] = args.kaynak_en_gec
        _yaz(out/f'ayar_{mod}.json',config)
    _yaz(out/'sonuc.json',dict(taban=taban_adi,izgara_hucre=len(grid),
          kenarlar=[float(m) if np.isfinite(m) else 'inf' for m in edges],
          egitim_olay=len(egitim),ayar_olay=int(counts_ayar.sum()),
          dogrulama_olay=int(counts_val.sum()),ayar_dis=dis_ayar,dogrulama_dis=dis_val,
          fay_sayisi=len(fay),atilan_fay=fay.attrs['atilan'],sonuclar=sonuclar,
          kaynak_sha256={k:sha256(v) for k,v in vars(args).items() if k in ('fay','katalog','izgara')},
          notlar=['Büyüklük MwDef; derinlik bilinmeyen CPTI satırları tutuldu.',
                  'DISS3.2.0 2015 sürümü: tam küme 2012 bilgisini içerebilir; hüküm değil.',
                  'KDE: eğitim 1950–1990, ayar 1991–2010; doğrulama 2011–2015.']))
    print(out/'sonuc.json')


if __name__ == '__main__':
    main()
