"""Deney AB: ML üyesi (hücre-gün Poisson gradyan artırma), İtalya günlük.

Aşamalar:
  sec     ≤2005 eğit, 8 aday (2 varyant × 4 ayar) 2006–2010 M≥2,95 logL'iyle seç;
          seçilenin 2006–2010 defterini yaz (SECIM.json)
  son     seçileni ≤2010 ile yeniden eğit, 2011–2015 defterini yaz
  olcum   defterlerden ölçüm (OLCUM.json)
Kural: records/AB/KURAL.md (puanlamadan önce yazıldı).
"""
from __future__ import annotations

import os
for _k in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ.setdefault(_k, '2')

import argparse
import gc
import json
from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd
from scipy.special import gammaln

from knotenlinie.karsilastir.gunluk_r import kaynak_oku
from knotenlinie.karsilastir.kosucu import Model, olay_kutulari, utc
from knotenlinie.karsilastir.gunluk_u import (DEFTER as U_DEFTER, ETAS_LM, R_ORTAK, _satir, _yaz)
from knotenlinie.ml_uye.egitim import egit, egitim_gunleri, egitim_kumesi, hedef_olaylari
from knotenlinie.ml_uye.ozellik import OzellikHesap, TUM_ADLAR, gun_no
from knotenlinie.ml_uye.r_ozellik import RIndeks, gun_ts, r_hesapla
from knotenlinie.ml_uye.uye import MLUye, kutu_payi
from knotenlinie.ortak_zemin.arayuz import ayar_tabani
from knotenlinie.ortak_zemin.veri import VERI, katalog_oku, sha256
from knotenlinie.yollar import KAYIT, KOSU, kayit_hazirla
from knotenlinie.skor_defteri.defter import KOK, defter_oku, defter_yaz, kos_defter

OUT = KOSU / 'AB'   # frozen inputs are seeded from records/AB/ by kayit_hazirla
KURAL = KAYIT / 'AB' / 'KURAL.md'   # frozen rule, read only
DEFTER = KOK / 'AB'
AYAR = DEFTER / 'ayar'
KATALOG = 'ortak/italya_katalog_le2015.csv'
R_JSON = {'sec': VERI / 'ortak/uzun/etas_s_le2005.json', 'son': VERI / 'ortak/uzun/etas_ortak.json'}
SON_AYAR = {'sec': '2006-01-01', 'son': '2011-01-01'}
PENCERE = {'2006-2010': ('2006-01-01T00:00:00Z', '2011-01-01T00:00:00Z'),
           '2011-2015': ('2011-01-01T00:00:00Z', '2016-01-01T00:00:00Z')}
TOHUM = 20261012
P_GUN, Q_HUCRE = 0.25, 0.25
EGITIM_BAS = '1995-01-01'
NAME = 'ML-uye'
KONFIG = {'K1': dict(lr=.05, yaprak=8, iter=200, min_yaprak=400),
          'K2': dict(lr=.05, yaprak=16, iter=200, min_yaprak=400),
          'K3': dict(lr=.1, yaprak=8, iter=100, min_yaprak=400),
          'K4': dict(lr=.1, yaprak=16, iter=100, min_yaprak=400)}
VARYANT = {'ML-saf': 35, 'ML-artik': 36}      # kullanılan sütun sayısı (son sütun R)
ESIKLER = (2.95, 3.95, 4.95)


def kenarlar():
    return np.r_[np.round(2.95 + 0.1 * np.arange(61), 2), np.inf]


def b_oku(yol):
    return float(json.loads(Path(yol).read_text())['b']['deger'])


def gunler_aralik(bas, son):
    return np.arange(int(gun_no(utc(bas))), int(gun_no(utc(son))))


def egitim_verisi(hesap, cat, raw, grid, asama):
    son = SON_AYAR[asama]
    cat_a = cat[cat.zaman < utc(son + 'T00:00:00Z')]
    ol = hesap.olaylar(cat_a)
    d0, d1 = int(gun_no(utc(EGITIM_BAS + 'T00:00:00Z'))), int(gun_no(utc(son + 'T00:00:00Z')))
    pg, ph = hedef_olaylari(hesap, cat_a, d0, d1)
    gun, bay = egitim_gunleri(pg, d0, d1, P_GUN, TOHUM)
    print(asama, 'eğitim: pozitif', len(pg), 'gün', len(gun), 'örnek gün', int(bay.sum()), flush=True)
    r = r_hesapla(R_JSON[asama], raw, grid, gun, yol=AYAR / f'r_egitim_{asama}.npz', ayar_ici=True)
    t1 = gun_no(utc(son + 'T00:00:00Z'))
    kk = {f: hesap.kde_log(ol, 0, t1, haric_yil_mod=f) for f in range(4)}
    kde = hesap.kde_log(ol, 0, t1)
    X, y, w, _, _ = egitim_kumesi(hesap, ol, pg, ph, gun, bay, kk, r, P_GUN, Q_HUCRE, TOHUM)
    print(asama, 'eğitim satırı', X.shape, flush=True)
    return X, y, w, kde


def sec_akis(hesap, cat, raw, grid, adaylar, kde, b, rindeks, orn_q=0.02):
    """2006–2010 günlük akış: özellik bir kez, her aday için M≥2,95 logL (log n! hariç)."""
    bas, son = PENCERE['2006-2010']
    t0, t1 = utc(bas), utc(son)
    ol = hesap.olaylar(cat[cat.zaman < t1])
    hedef = cat[(cat.zaman >= t0) & (cat.zaman < t1)]
    edges = kenarlar()
    hedef, ci, mi = olay_kutulari(hedef, grid, edges, (0, 30))
    gun_e = np.floor(gun_no(hedef.zaman)).astype(int)
    pay = kutu_payi(edges, b)
    psum = float(pay.sum())
    g3 = hedef.mw.to_numpy(float) >= 3.1 - 1e-6
    rng = np.random.default_rng(TOHUM + 7)
    acc_e = {k: 0.0 for k in adaylar}
    acc_L = {k: 0.0 for k in adaylar}
    xs, ys, ws = [], [], []
    d0 = int(gun_no(t0))
    gunler = gunler_aralik(bas, son)
    zaman0 = time.monotonic()
    for i, d in enumerate(gunler):
        rl = np.log(np.maximum(rindeks(gun_ts(d)).astype(float), 1e-12))
        X = hesap.hesapla(ol, float(d), kde, rl)
        idx = np.flatnonzero(gun_e == d)
        for k, (m, cols) in adaylar.items():
            mu = np.maximum(m.predict(X[:, cols]), 1e-12)
            acc_L[k] += float(mu.sum()) * psum
            if len(idx):
                acc_e[k] += float(np.log(mu[ci[idx]] * pay[mi[idx]]).sum())
        # önem örneği: M≥3,1 olay hücreleri + rastgele hücrelerin orn_q'su
        cnt = np.bincount(ci[idx][g3[idx]], minlength=hesap.n)
        pos = np.flatnonzero(cnt > 0)
        sif = np.flatnonzero((cnt == 0) & (rng.random(hesap.n) < orn_q))
        xs.append(np.vstack([X[pos], X[sif]]))
        ys.append(np.r_[cnt[pos], np.zeros(len(sif))])
        ws.append(np.r_[np.ones(len(pos)), np.full(len(sif), 1.0 / orn_q)])
        if i and i % 300 == 0:
            print('  seçim akışı gün %d/%d, %.0f s' % (i, len(gunler), time.monotonic() - zaman0), flush=True)
    logL = {k: acc_e[k] - acc_L[k] for k in adaylar}
    return logL, acc_L, (np.vstack(xs), np.concatenate(ys), np.concatenate(ws)), len(hedef)


def permutasyon(model, cols, Xv, yv, wv, tohum=TOHUM):
    """Ağırlıklı Poisson sapma artışı (özellik başına bir permütasyon)."""
    rng = np.random.default_rng(tohum)

    def dev(mu):
        t = np.where(yv > 0, yv * np.log(np.maximum(yv, 1e-300) / mu), 0.0)
        return float(2 * (wv * (t - (yv - mu))).sum())

    X = Xv[:, cols]
    taban = dev(np.maximum(model.predict(X), 1e-12))
    out = {}
    for j, c in enumerate(cols):
        Xp = X.copy()
        Xp[:, j] = Xp[rng.permutation(len(Xp)), j]
        out[TUM_ADLAR[c]] = dev(np.maximum(model.predict(Xp), 1e-12)) - taban
    return taban, out


def uye_kur(hesap, model, cols, kde, b, rindeks):
    return MLUye(NAME, model, cols, hesap, kde, b, r_fn=rindeks if cols[-1] == 35 else None)


def defter_uret(donem, uye, cat, grid):
    bas, son = PENCERE[donem]
    ayar = dict(sinir=(5.5, 19.5, 35.8, 47.9), baslangic_yil=1985, derinlik_max=30)
    mod = Model(NAME, uye.beklenen, True, ayar)
    t = time.monotonic()
    d = kos_defter([mod], bas, son, cat, grid, kenarlar(), derinlik=(0, 30), bolge='italya', ilerleme=300)[NAME]
    print(donem, NAME, 'N=%d logL=%.4f Lam295=%.2f Lam395=%.2f s=%.0f' % (
        d.N, d.logL, d.gun['Lam295'].sum(), d.gun['Lam395'].sum(), time.monotonic() - t), flush=True)
    defter_yaz(d, DEFTER, donem)
    np.savez_compressed(DEFTER / f'{NAME}__{donem}__marjinal.npz', beklenen=d.beklenen, gozlem=d.gozlem,
                        logL=np.array([d.logL]))
    return d


def yukle(ad, dizin, donem):
    d = defter_oku(ad, dizin, donem)
    with np.load(dizin / f'{ad}__{donem}__marjinal.npz') as z:
        d.beklenen, d.gozlem, d.logL = z['beklenen'], z['gozlem'], float(z['logL'][0])
    return d


def ortak_veri():
    cat = katalog_oku(VERI / KATALOG)
    raw, paths, report = kaynak_oku()
    grid = ayar_tabani('italya', son='2006-01-01').izgara
    return cat, raw, grid, paths


def asama_sec():
    AYAR.mkdir(parents=True, exist_ok=True)
    cat, raw, grid, paths = ortak_veri()
    hesap = OzellikHesap(grid)
    b = b_oku(R_JSON['sec'])
    X, y, w, kde = egitim_verisi(hesap, cat, raw, grid, 'sec')
    adaylar, bilgi = {}, {}
    for v, nc in VARYANT.items():
        for kn, cfg in KONFIG.items():
            t = time.monotonic()
            cols = list(range(nc))
            m = egit(X, y, w, cols, cfg)
            ad = f'{v}/{kn}'
            adaylar[ad] = (m, cols)
            mu = m.predict(X[:, cols])
            bilgi[ad] = dict(egitim_kalibrasyon=float((w * mu).sum() / (w * y).sum()), sure_s=time.monotonic() - t)
            print('fit', ad, bilgi[ad], flush=True)
    del X, y, w
    gc.collect()
    bas, son = PENCERE['2006-2010']
    gun6 = gunler_aralik(bas, son)
    r6 = r_hesapla(R_JSON['sec'], raw, grid, gun6, yol=AYAR / 'r_2006-2010.npz')
    rindeks = RIndeks(gun6, r6)
    logL, LamS, (Xv, yv, wv), nev = sec_akis(hesap, cat, raw, grid, adaylar, kde, b, rindeks)
    en = max(logL, key=logL.get)
    for k in adaylar:
        bilgi[k].update(logL_295_2006_2010=logL[k], Lambda295=LamS[k])
    print('SEÇİM', {k: round(v, 3) for k, v in logL.items()}, '->', en, flush=True)
    model, cols = adaylar[en]
    taban, onem = permutasyon(model, cols, Xv, yv, wv)
    v, kn = en.split('/')
    uye = uye_kur(hesap, model, cols, kde, b, rindeks)
    d = defter_uret('2006-2010', uye, cat, grid)
    res = dict(secilen=en, varyant=v, konfig=kn, konfig_degerleri=KONFIG[kn], N_295_2006_2010=int(nev),
               adaylar=bilgi, ozellik_onemi_sapma_artisi=onem, onem_taban_sapma=taban,
               onem_ornek_satir=int(len(yv)), defter_logL_2006_2010=d.logL,
               akis_logL_hatasi_gammaln_haric=None, kural_SHA256=sha256(KURAL),
               b_2006=b, egitim_bas=EGITIM_BAS, p_gun=P_GUN, q_hucre=Q_HUCRE, tohum=TOHUM)
    # akış logL'i ↔ defter logL'i: fark yalnız log(n!) (hedef başına aynı hücre-kutu-gün çokluğu)
    key = d.olay['gun'].astype(str) + '|' + d.olay['hucre'].astype(str) + '|' + d.olay['kutu'].astype(str)
    _, say = np.unique(key.to_numpy(), return_counts=True)
    res['akis_logL_hatasi_gammaln_haric'] = float(d.logL - (logL[en] - gammaln(say + 1).sum()))
    _yaz(OUT / 'SECIM.json', res)
    print('SECIM.json yazıldı; akış↔defter fark', res['akis_logL_hatasi_gammaln_haric'], flush=True)


def asama_son():
    cat, raw, grid, paths = ortak_veri()
    sec = json.loads((OUT / 'SECIM.json').read_text())
    if sec['kural_SHA256'] != sha256(KURAL):
        raise SystemExit('KURAL.md seçimden sonra değişmiş')
    hesap = OzellikHesap(grid)
    b = b_oku(R_JSON['son'])
    X, y, w, kde = egitim_verisi(hesap, cat, raw, grid, 'son')
    nc = VARYANT[sec['varyant']]
    cols = list(range(nc))
    m = egit(X, y, w, cols, KONFIG[sec['konfig']])
    mu = m.predict(X[:, cols])
    kal = float((w * mu).sum() / (w * y).sum())
    print('son kurulum', sec['secilen'], 'kalibrasyon', kal, flush=True)
    del X, y, w
    gc.collect()
    bas, son = PENCERE['2011-2015']
    gun11 = gunler_aralik(bas, son)
    r11 = r_hesapla(R_JSON['son'], raw, grid, gun11, yol=AYAR / 'r_2011-2015.npz')
    uye = uye_kur(hesap, m, cols, kde, b, RIndeks(gun11, r11))
    d = defter_uret('2011-2015', uye, cat, grid)
    _yaz(OUT / 'SON_KURULUM.json', dict(secilen=sec['secilen'], egitim_kalibrasyon=kal, b_2011=b,
                                        defter_logL_2011_2015=d.logL, N=d.N,
                                        Lambda295=float(d.gun['Lam295'].sum()),
                                        Lambda395=float(d.gun['Lam395'].sum())))


def olay_korelasyon(d, adlar, alt):
    from scipy.stats import spearmanr
    mask = d[NAME].olay['mw'].to_numpy(float) >= alt - 1e-9
    ml = np.log(d[NAME].lam()[mask])
    out = {}
    for a in adlar:
        x = np.log(d[a].lam()[mask])
        out[a] = dict(pearson=float(np.corrcoef(ml, x)[0, 1]), spearman=float(spearmanr(ml, x)[0]), N=int(mask.sum()))
    return out


def asama_olcum():
    sec = json.loads((OUT / 'SECIM.json').read_text())
    d = {NAME: yukle(NAME, DEFTER, '2011-2015')}
    for a in (R_ORTAK, ETAS_LM):
        d[a] = yukle(a, U_DEFTER, '2011-2015')
    satir = []
    for alt in ESIKLER:
        for taban in (ETAS_LM, R_ORTAK):
            s = _satir(d, [NAME], taban, alt, [1.0], 'tekil')
            satir.append(s)
    kor = {str(alt): olay_korelasyon(d, [R_ORTAK, ETAS_LM], alt) for alt in ESIKLER}
    res = dict(satirlar=satir, olay_logLam_korelasyon=kor, secim=sec,
               durum='PROVISIONAL; bağımsız skor-kodu incelemesi bekler; kör hüküm değil',
               defter_SHA256={p.name: sha256(p) for p in sorted(DEFTER.glob(f'{NAME}__*'))},
               kural_SHA256=sha256(KURAL), python=sys.version, numpy=np.__version__,
               pandas=pd.__version__)
    _yaz(OUT / 'OLCUM.json', res)
    for s in satir:
        print(s['taban'], s['esik'], 'N', s['N'], 'IG %.4f ± %.4f z %.2f' % (s['IG'], s['SE_blok'], s['z']), flush=True)
    print(json.dumps(kor, indent=1))


def main():
    kayit_hazirla('AB')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--asama', choices=('sec', 'son', 'olcum'), required=True)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    {'sec': asama_sec, 'son': asama_son, 'olcum': asama_olcum}[a.asama]()


if __name__ == '__main__':
    main()
