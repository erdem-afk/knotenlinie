"""Deney AJ: dallanma kısıtlı R (İtalya günlük). n(θ) ≤ n_max, n_max 2006–2010'da seçilir.

Aşamalar (kural: records/AJ/KURAL.md, puanlamadan önce yazıldı):
  sec    ≤2005 kısıtlı ayarlar, 2006–2010 defterleri, M≥2,95 logL ile n_max seçimi (SECIM.json)
  son    seçileni ≤2010 ile yeniden kur, 2011–2015 defterini yaz (SON_KURULUM.json)
  olcum  defterlerden ölçüm (OLCUM.json); AJ ve E7 − ETAS-LM / − R-ortak-kaskad
Ölçüm defterlerden hesaplanır (U/AE ile aynı kod); R ve ETAS-LM defterleri U'nundur.
"""
from __future__ import annotations

import os
for _k in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ.setdefault(_k, '2')

import argparse
import gc
import shutil
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from knotenlinie.etas_hiyerarsi import ceza as Z
from knotenlinie.etas_kisitli import mle as K
from knotenlinie.karsilastir.gunluk_ae import (_json, _oku, defter_kaydet, defter_uret, italya_model, kenarlar,
                                         ortak_veri, yukle)
from knotenlinie.karsilastir.gunluk_r import rss_byte
from knotenlinie.karsilastir.gunluk_u import DEFTER as U_DEFTER, ETAS_LM, R_ORTAK, _satir
from knotenlinie.ortak_zemin.veri import VERI, sha256
from knotenlinie.yollar import KAYIT, KOSU, kayit_hazirla
from knotenlinie.skor_defteri.defter import KOK
from knotenlinie.skor_defteri.karisim import log_olabilirlik

OUT = KOSU / 'AJ'   # frozen inputs are seeded from records/AJ/ by kayit_hazirla
KURAL = KAYIT / 'AJ' / 'KURAL.md'   # frozen rule, read only
DEFTER = KOK / 'AJ'
AYAR = DEFTER / 'ayar'
R_JSON = {'sec': VERI / 'ortak/uzun/etas_s_le2005.json', 'son': VERI / 'ortak/uzun/etas_ortak.json'}
ESIKLER = (2.95, 3.95, 4.95)
AD = 'AJ'
LM_J = dict(mu=0.59973, K=0.02828, c=0.01461, alpha=0.56458, p=1.16, D=1.10, q=1.5, gamma=0.0)


def aday_adi(n_max):
    return f'AJ-n{K.ad(n_max)}'


def kural_kapisi():
    yol = KURAL
    if not yol.exists():
        raise SystemExit('Önce AJ/KURAL.md yazılmalı')
    return sha256(yol)


def asama_sec(args):
    kural = kural_kapisi()
    DEFTER.mkdir(parents=True, exist_ok=True)
    AYAR.mkdir(parents=True, exist_ok=True)
    cat, raw, grid, _ = ortak_veri()
    L, meta = Z.italya_L(raw, grid, '2006-01-01')
    rj = _oku(R_JSON['sec'])
    x_r = np.array(rj['x'])
    ll_r = float(-L.objectif(x_r, 'ortak')[0] * len(L.t))
    print('R ≤2005 logL kayıt %.6f, yeniden %.6f' % (rj['logL'], ll_r), flush=True)
    if abs(ll_r - rj['logL']) > 1e-6 * abs(rj['logL']):
        raise SystemExit('Italya_L R kaydıyla eşleşmiyor')
    sonuc = {}
    for n_max in K.ADAYLAR[:-1]:
        ad = aday_adi(n_max)
        yol = AYAR / f'{ad}_sec.json'
        if yol.exists():
            fit = _oku(yol)
        else:
            t0 = time.monotonic()
            fit = K.ayarla_kisitli(L, n_max, x_r, maksiter=args.maksiter)
            fit['duvar_saniye'] = time.monotonic() - t0
            _json(yol, fit)
        print(ad, 'logL=%.2f n=%.6f sinirda=%s nit=%d basari=%s' % (
            fit['logL'], fit['dallanma'], fit['sinirda'], fit['nit'], fit['basari']), flush=True)
        sonuc[ad] = dict(n_max=n_max, fit_logL=fit['logL'], dallanma=fit['dallanma'], sinirda=fit['sinirda'],
                         basari=fit['basari'], parametreler=fit['parametreler'])
    for ad in list(sonuc):
        if (DEFTER / f'{ad}__2006-2010__marjinal.npz').exists():
            d = yukle(ad, DEFTER, '2006-2010')
        else:
            p = K.model_p(rj, _oku(AYAR / f'{ad}_sec.json'))
            mod = italya_model(p, grid, raw, ad)
            d = defter_uret(mod, '2006-2010', cat, grid)
            defter_kaydet(d, '2006-2010', DEFTER)
            del mod
            gc.collect()
        sonuc[ad]['logL_295'] = log_olabilirlik([d], [1.0], 2.95)
        sonuc[ad]['logL_395'] = log_olabilirlik([d], [1.0], 3.95)
        sonuc[ad]['Lambda295'] = float(d.gun['Lam295'].sum())
        sonuc[ad]['Lambda395'] = float(d.gun['Lam395'].sum())
    dR = yukle(R_ORTAK, U_DEFTER, '2006-2010')
    sonuc['R (serbest)'] = dict(n_max=K.SERBEST, fit_logL=rj['logL'], dallanma=rj['dallanma'], sinirda=True,
                                logL_295=log_olabilirlik([dR], [1.0], 2.95), logL_395=log_olabilirlik([dR], [1.0], 3.95),
                                Lambda295=float(dR.gun['Lam295'].sum()), Lambda395=float(dR.gun['Lam395'].sum()))
    en = max(sonuc, key=lambda k: sonuc[k]['logL_295'])
    _json(OUT / 'SECIM.json', dict(
        secilen=en, adaylar=sonuc, kural_SHA256=kural, secim='2006–2010 M≥2,95 logL (log n! hariç), ≤2005 ayar',
        R_x_kaynak=str(R_JSON['sec']), R_logL_yeniden=ll_r, N_295_2006_2010=int(len(dR.olay))))
    print('SEÇİLEN', en, {k: round(v['logL_295'], 3) for k, v in sonuc.items()}, flush=True)


def asama_son(args):
    kural = kural_kapisi()
    sec = _oku(OUT / 'SECIM.json')
    if sec['kural_SHA256'] != kural:
        raise SystemExit('KURAL.md seçimden sonra değişmiş')
    en = sec['secilen']
    rj = _oku(R_JSON['son'])
    if en.startswith('R '):
        DEFTER.mkdir(parents=True, exist_ok=True)
        for ek in ('olay.csv.gz', 'gun.csv.gz', 'marjinal.npz'):
            shutil.copyfile(U_DEFTER / f'{R_ORTAK}__2011-2015__{ek}', DEFTER / f'{AD}__2011-2015__{ek}')
        d = yukle(AD, DEFTER, '2011-2015')
        _json(OUT / 'SON_KURULUM.json', dict(secilen=en, parametreler=rj['parametreler'], dallanma=rj['dallanma'],
                                             not_='AJ = R-ortak-kaskad (serbest seçildi)', defter_logL_2011_2015=d.logL,
                                             N=d.N, Lambda295=float(d.gun['Lam295'].sum()),
                                             Lambda395=float(d.gun['Lam395'].sum())))
        return
    n_max = sec['adaylar'][en]['n_max']
    cat, raw, grid, _ = ortak_veri()
    L, meta = Z.italya_L(raw, grid, '2011-01-01')
    x_r = np.array(rj['x'])
    ll_r = float(-L.objectif(x_r, 'ortak')[0] * len(L.t))
    print('R ≤2010 logL kayıt %.6f, yeniden %.6f' % (rj['logL'], ll_r), flush=True)
    if abs(ll_r - rj['logL']) > 1e-6 * abs(rj['logL']):
        raise SystemExit('Italya_L R(≤2010) kaydıyla eşleşmiyor')
    fit = K.ayarla_kisitli(L, n_max, x_r, maksiter=args.maksiter)
    print('son', en, 'logL=%.2f n=%.6f sinirda=%s' % (fit['logL'], fit['dallanma'], fit['sinirda']), flush=True)
    AYAR.mkdir(parents=True, exist_ok=True)
    _json(AYAR / 'AJ_son.json', fit)
    mod = italya_model(K.model_p(rj, fit), grid, raw, AD)
    d = defter_uret(mod, '2011-2015', cat, grid)
    defter_kaydet(d, '2011-2015', DEFTER)
    _json(OUT / 'SON_KURULUM.json', dict(secilen=en, n_max=n_max, parametreler=fit['parametreler'],
                                         dallanma=fit['dallanma'], sinirda=fit['sinirda'], logL_fit=fit['logL'],
                                         R_logL_fit=rj['logL'], defter_logL_2011_2015=d.logL, N=d.N,
                                         Lambda295=float(d.gun['Lam295'].sum()), Lambda395=float(d.gun['Lam395'].sum())))


def asama_olcum(args):
    kural = kural_kapisi()
    sec = _oku(OUT / 'SECIM.json')
    d = {R_ORTAK: yukle(R_ORTAK, U_DEFTER, '2011-2015'), ETAS_LM: yukle(ETAS_LM, U_DEFTER, '2011-2015'),
         AD: yukle(AD, DEFTER, '2011-2015')}
    aj_r = sec['secilen'].startswith('R ')
    satir = []
    for alt in ESIKLER:
        for taban in ((ETAS_LM,) if aj_r else (ETAS_LM, R_ORTAK)):
            satir.append(_satir(d, [AD], taban, alt, [1.0], 'tekil'))
    for alt in ESIKLER:
        for taban in (ETAS_LM, R_ORTAK):
            s = _satir(d, [AD, ETAS_LM], taban, alt, [0.5, 0.5], 'esit')
            s['topluluk'] = 'E7'
            satir.append(s)
    for s in satir:
        s['Lambda_bolu_N'] = s['Lambda_aday'] / s['N']
        s['Lambda_bolu_N_taban'] = s['Lambda_taban'] / s['N']
    son = _oku(OUT / 'SON_KURULUM.json')
    rj = _oku(R_JSON['son'])
    tablo = dict(R=rj['parametreler'], R_dallanma=rj['dallanma'], AJ=son['parametreler'], AJ_dallanma=son['dallanma'],
                 LM_J=LM_J)
    _json(OUT / 'OLCUM.json', dict(
        satirlar=satir, secim=sec, parametre_tablosu=tablo, son_kurulum=son,
        durum='PROVISIONAL; bağımsız skor-kodu incelemesi yok; kör hüküm değil',
        defter_SHA256={p.name: sha256(p) for p in sorted(DEFTER.glob(f'{AD}__*'))},
        kural_SHA256=kural, python=sys.version, numpy=np.__version__, pandas=pd.__version__, rss_byte=rss_byte()))
    for s in satir:
        print(s.get('topluluk') or s['aday'], s['taban'], s['esik'], 'N', s['N'],
              'IG %.4f ± %.4f z %.2f  Lam %.1f/%.1f' % (s['IG'], s['SE_blok'], s['z'], s['Lambda_aday'],
                                                        s['Lambda_taban']), flush=True)


def main():
    kayit_hazirla('AJ')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--asama', choices=('sec', 'son', 'olcum'), required=True)
    ap.add_argument('--maksiter', type=int, default=300)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    {'sec': asama_sec, 'son': asama_son, 'olcum': asama_olcum}[a.asama](a)


if __name__ == '__main__':
    main()
