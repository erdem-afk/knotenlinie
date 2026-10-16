"""D2 iç doğrulama: ortak ETAS, ≤2010 ayar, 2011–2015 günlük skor."""
from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .etas import OrtakTaban, ETASFay, gunluk, ayarla, olcum, ACIK_SON
from .komut import italya_izgara, _yaz
from .veri import fay_oku, sha256, DISS_SHA256


def katalog_oku(yol):
    """Yalnız ortak le2015 katalogları; zaman sütununu önce denetle."""
    yol = Path(yol)
    if yol.name not in ('italya_katalog_le2015.csv',):
        raise ValueError('deney T ortak katalog adı gerekli')
    times = pd.to_datetime(pd.read_csv(yol, usecols=['zaman']).zaman, utc=True, errors='raise')
    if times.isna().any() or (times >= ACIK_SON).any():
        raise ValueError('ortak katalog kör/mühürlü satır içeriyor; kullanmayın')
    d = pd.read_csv(yol, usecols=['zaman','enlem','boylam','derinlik','mw'])
    d['zaman'] = times
    if not np.isfinite(d[['enlem','boylam','mw']].to_numpy(float)).all():
        raise ValueError('ortak katalog koordinatı/Mw geçersiz')
    return d.sort_values('zaman',kind='stable').reset_index(drop=True)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ortak', required=True, help='deney T ortak veri dizini')
    p.add_argument('--bolge', choices=['italya'], required=True)
    p.add_argument('--etas-fabrika', default='knotenlinie.fay_butce.etas:ortak_yukle',
                   help='modul:fonksiyon; varsayılan deney T gerçek modeli')
    p.add_argument('--fay', required=True)
    p.add_argument('--izgara', required=True, help='İtalya XML veya ortak sütunlu CSV')
    p.add_argument('--kaynak-en-gec', required=True, help='2016-01-01 tam / 2011-01-01 kaynak≤2010')
    p.add_argument('--ayar-baslangic', help='yoksa ortak ETAS ayar başlangıcı; yalnız ≤2010')
    p.add_argument('--cikti', required=True, help='D/ altındaki sonuç dizini')
    args = p.parse_args(argv)
    root, out = Path(args.ortak), Path(args.cikti)
    catfile = root/f'{args.bolge}_katalog_le2015.csv'
    etasfile = root/f'etas_{args.bolge}_le2010.json'
    missing = [str(f) for f in (catfile,etasfile) if not f.is_file()]
    if missing:
        raise FileNotFoundError('deney T ortak girdi kapısı kapalı: '+', '.join(missing))
    source_end = pd.to_datetime(args.kaynak_en_gec,utc=True)
    if pd.isna(source_end) or source_end > ACIK_SON:
        raise ValueError('--kaynak-en-gec en geç 2016-01-01 olmalı')
    paths = dict(katalog=catfile,etas=etasfile,fay=args.fay,izgara=args.izgara)
    input_hashes = {k:sha256(v) for k,v in paths.items()}
    etas_meta = json.loads(etasfile.read_text(encoding='utf-8'))
    t0 = pd.to_datetime(args.ayar_baslangic or etas_meta['ayar_baslangic'],utc=True)
    t1, t2 = pd.Timestamp('2011-01-01',tz='UTC'), ACIK_SON
    if pd.isna(t0) or not pd.to_datetime(etas_meta['ayar_baslangic'],utc=True) <= t0 < t1:
        raise ValueError('ayar başlangıcı ortak ETAS aralığında ve ≤2010 olmalı')
    if pd.to_datetime(etas_meta['ayar_bitis'],utc=True) > t1 or etas_meta['mc'] > 4.95:
        raise ValueError('ortak ETAS ≤2010 / M≥4.95 kapısı kapalı')
    for key, path in (('katalog_sha256',catfile),('izgara_sha256',args.izgara)):
        if sha256(path) != etas_meta[key]:
            raise ValueError(f'ortak ETAS {key} uyuşmuyor')
    surum = 'DISS3.2.0'
    expected_hash = DISS_SHA256
    fay = fay_oku(args.fay,surum=surum,en_gec=source_end,beklenen_sha256=expected_hash)
    katalog = katalog_oku(catfile)
    # Ortak ETAS da aynısını yapar: Mc altı ve ayar başlangıcı öncesi ebeveyn
    # üretkenliği sıfırdır. Bu satırları her gün tekrar parse/sort etme.
    katalog = katalog.loc[(katalog.mw >= etas_meta['mc']) &
                          (katalog.zaman >= pd.to_datetime(etas_meta['ayar_baslangic'],utc=True))].copy()
    grid = italya_izgara(args.izgara) if Path(args.izgara).suffix=='.xml' else pd.read_csv(args.izgara)
    # Arka plan/tetikleme GR'si aynı: M>=4.95 tek kutuya birleşince IG değişmez.
    edges = np.array([4.95,np.inf])
    mod, fn = args.etas_fabrika.split(':')
    taban = OrtakTaban(getattr(importlib.import_module(mod),fn)(str(etasfile)))
    shapes = {s:ETASFay(taban,fay,agirlik=1.,sigma_km=s).sekil(grid) for s in (5,10,20,40)}
    tuning = gunluk(taban,shapes,katalog,grid,edges,t0,t1)
    fit = ayarla(tuning['olay_taban'],tuning['olay_fay'],tuning['toplam_taban'],
                 tuning['toplam_fay'],baslangic=t0,bitis=t1)
    sigma, w = fit['sigma_km'], fit['agirlik']
    validation = gunluk(taban,{sigma:shapes[sigma]},katalog,grid,edges,t1,t2)
    score = olcum((1-w)*validation['olay_taban']+w*validation['olay_fay'][sigma],
                  validation['olay_taban'],
                  (1-w)*validation['toplam_taban']+w*validation['toplam_fay'][sigma],
                  validation['toplam_taban'])
    row = dict(aday=f'ETAS+{surum}'+('-kaynak-le2010' if source_end<=t1 else '-tam'),
               bolge=args.bolge,**score,agirlik=w,sigma_km=sigma,
               ayar=fit,ayar_baslangic=t0.isoformat(),ayar_bitis=t1.isoformat(),
               etas_mc=etas_meta['mc'],etas_dallanma=etas_meta['dallanma'],
               ayar_N=len(tuning['olay_taban']),ayar_dis=tuning['dis'],
               dogrulama_dis=validation['dis'],izgara_hucre=len(grid),
               fay_sayisi=len(fay),kaynak_en_gec=source_end.isoformat(),
               pencere=['2011-01-01','2016-01-01'],esik=4.95,
               kaynak_sha256=input_hashes,
               notlar=['p: eşleştirilmiş iki yönlü T-test, kümelenme bağımsızlığı bozabilir.',
                       'Yalnız uzay karışır; ETAS mu/GR/tetikleme aynen; toplam korunur.',
                       '2011–2015 iç doğrulamadır; yerleşik modeli geçme hükmü değildir.'])
    config = dict(taban='ortak_etas',etas_fabrika=args.etas_fabrika,etas_yolu=str(etasfile.resolve()),
                  fay_yolu=str(Path(args.fay).resolve()),surum=surum,fay_sha256=expected_hash,
                  kaynak_en_gec=source_end.isoformat(),agirlik=w,sigma_km=sigma,sekil_esik=4.95)
    if input_hashes != {k:sha256(v) for k,v in paths.items()}:
        raise ValueError('koşu sırasında ortak girdi değişti; sonuç yazılmadı')
    out.mkdir(parents=True,exist_ok=True)
    _yaz(out/'sonuc.json',row)
    _yaz(out/'ayar.json',config)
    print(out/'sonuc.json')


if __name__ == '__main__':
    main()
