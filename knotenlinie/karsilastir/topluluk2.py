"""Topluluk 2 kuralı: eşit ağırlıklı karışımlar E1–E5, yalnız skor defterlerinden.

Kural üyeler puanlanmadan önce yazıldı (12 Ekim): E1={R,LM,STEP}, E2={R,LM,ML}, E3={R,LM,STEP,ML}, E4=E3+X,
E5={R,STEP,ML}. Hüküm satırı her biri − ETAS-LM, M≥3,95, 2011–2015; geliştirme M≥2,95; Holm beşi üstünde.
Kurulamayan üyeyi içeren karışım "tanımsız" yazılır.

    python3 -m knotenlinie.karsilastir.topluluk2 --ml AB/<model adı> --cikti $KNOTENLINIE_RUNS/AC/OLCUM.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from knotenlinie.karsilastir.puan import PuanHatasi, holm
from knotenlinie.skor_defteri.defter import GUN_EK, KOK, Defter, defter_oku
from knotenlinie.skor_defteri.karisim import ozet

UYELER = {'R': 'U/R-ortak-kaskad', 'LM': 'U/ETAS-LM', 'STEP': 'AA/STEP', 'X': 'X/X-b-5.5'}
KARISIMLAR = {'E1': ['R', 'LM', 'STEP'], 'E2': ['R', 'LM', 'ML'], 'E3': ['R', 'LM', 'STEP', 'ML'],
              'E4': ['R', 'LM', 'STEP', 'ML', 'X'], 'E5': ['R', 'STEP', 'ML']}
ESIKLER = (2.95, 3.95, 4.95)
DONEM = '2011-2015'


def oku(yol):
    """defter_oku; ortak defter biçiminde M≥4,95 sütunu (U'nun eki) yoksa onu NaN alır, 4,95 satırı tanımsız olur."""
    deney, ad = yol.split('/', 1)
    try:
        return defter_oku(ad, KOK / deney, DONEM)
    except PuanHatasi as e:
        if GUN_EK not in str(e):
            raise
    o = pd.read_csv(KOK / deney / f'{ad}__{DONEM}__olay.csv.gz')
    o['zaman'] = pd.to_datetime(o['zaman'], utc=True, format='mixed')
    if o['zaman'].isna().any() or (o['zaman'] >= pd.Timestamp('2016-01-01', tz='UTC')).any():
        raise PuanHatasi(f'{yol}: olay defterinde 2016+ veya eksik zaman')
    for k in ('enlem', 'boylam', 'mw', 'lam'):
        o[k] = pd.to_numeric(o[k], errors='raise').astype(float)
    for k in ('hucre', 'kutu'):
        o[k] = o[k].astype(int)
    o['gun'] = o['gun'].astype(str)
    if (o['lam'] <= 0).any():
        raise PuanHatasi(f'{yol}: olay defteri pozitif λ istiyor')
    g = pd.read_csv(KOK / deney / f'{ad}__{DONEM}__gun.csv.gz')
    for k in ('Lam295', 'Lam395'):
        g[k] = pd.to_numeric(g[k], errors='raise').astype(float)
    g[GUN_EK] = np.nan
    g['gun'] = g['gun'].astype(str)
    return Defter(ad, o, g)


def satir(defterler, taban, alt):
    k = ozet(defterler, taban, alt)
    return {a: k[a] for a in ('N', 'Lambda_aday', 'Lambda_taban', 'IG', 'IG_olay', 'integral',
                              'SE_blok', 'z', 'p_tek', 'blok_sayisi')}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--ml', required=True, help='ML üyesinin defteri, ör. AB/ML-saf')
    ap.add_argument('--cikti', required=True)
    args = ap.parse_args(argv)
    yollar = dict(UYELER, ML=args.ml)
    defter, hata = {}, {}
    for uye, yol in yollar.items():
        try:
            defter[uye] = oku(yol)
        except (PuanHatasi, OSError) as e:
            hata[uye] = str(e)
    taban = defter['LM']
    sonuc = {'kural': 'Topluluk 2 kuralı (eşit ağırlık)', 'donem': DONEM,
             'uyeler': yollar, 'kurulamayan': hata, 'satirlar': {}}
    for ad, uyeler in KARISIMLAR.items():
        eksik = [u for u in uyeler if u not in defter]
        if eksik:
            sonuc['satirlar'][ad] = {'durum': 'tanımsız', 'eksik': eksik}
            continue
        esikler = {}
        for a in ESIKLER:
            if a == 4.95 and any(defter[u].gun[GUN_EK].isna().any() for u in uyeler):
                esikler[str(a)] = {'durum': 'tanımsız', 'sebep': 'üye defterinde Lam495 yok'}
            else:
                esikler[str(a)] = satir([defter[u] for u in uyeler], taban, a)
        sonuc['satirlar'][ad] = {'uyeler': uyeler, 'durum': 'tanımlı', 'esikler': esikler}
    # Holm beş karışımın hepsi üstünde; tanımsız karışım p=1 sayılır (kural).
    adlar = list(KARISIMLAR)
    p = [sonuc['satirlar'][a]['esikler']['3.95']['p_tek'] if sonuc['satirlar'][a]['durum'] == 'tanımlı' else None
         for a in adlar]
    for a, ph in zip(adlar, holm(p)):
        if sonuc['satirlar'][a]['durum'] != 'tanımlı':
            sonuc['satirlar'][a]['p_holm5'] = float(ph)
            continue
        s = sonuc['satirlar'][a]['esikler']['3.95']
        s['p_holm5'] = float(ph)
        s['basari'] = bool(s['IG'] is not None and s['IG'] > 0 and (s['z'] or 0) > 1.645 and ph < 0.05)
    Path(args.cikti).parent.mkdir(parents=True, exist_ok=True)
    Path(args.cikti).write_text(json.dumps(sonuc, ensure_ascii=False, indent=1))
    for a, s in sonuc['satirlar'].items():
        if s['durum'] != 'tanımlı':
            print(a, s)
            continue
        for e in ('3.95', '2.95'):
            r = s['esikler'][e]
            print(f"{a} − LM M≥{e}: IG {r['IG']:+.4f} ± {r['SE_blok']:.4f} z {r['z']:+.2f}"
                  + (f" Holm {r['p_holm5']:.3f}" if 'p_holm5' in r else ''))


if __name__ == '__main__':
    main()
