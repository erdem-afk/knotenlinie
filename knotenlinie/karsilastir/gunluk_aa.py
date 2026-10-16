"""Deney AA: STEP tipi günlük model (İtalya), skor defteri ve ölçüm.

Aşamalar:
  sec     12 önceden listelenmiş hiperparametre kombinasyonu, ≤2005 kurulum, 2006–2010
          M≥2,95 logL; en iyisi AA/SECIM.json'a ve 2006–2010 defterine yazılır
  defter  seçilen kombinasyon ≤2010 ile yeniden kurulur, 2011–2015 defteri yazılır
  olcum   yalnız defterlerden: STEP − ETAS-LM / R-ortak-kaskad, korelasyonlar, E1
  hepsi   tamamı

KURAL.md bu çalışmadan önce yazılmıştır; sha'sı çıktılara girer.
"""
from __future__ import annotations

import os
for _k in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ.setdefault(_k, '2')

import argparse
import itertools
import json
from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd
from scipy import stats

from knotenlinie.karsilastir.gunluk_r import rss_byte
from knotenlinie.karsilastir.gunluk_u import (_kenarlar, _marjinal_yol, _satir, _yaz,
                                        BAS6, BAS11, SON6, SON11, DERINLIK, ESIKLER,
                                        ETAS_LM, R_ORTAK)
from knotenlinie.karsilastir.kosucu import Model
from knotenlinie.ortak_zemin.veri import VERI, katalog_oku, sha256
from knotenlinie.yollar import KAYIT, KOSU, kayit_hazirla
from knotenlinie.skor_defteri.defter import KOK as DEFTER_KOK
from knotenlinie.skor_defteri.defter import alt_sutun, defter_oku, defter_yaz, kos_defter
from knotenlinie.skor_defteri.karisim import log_olabilirlik
from knotenlinie.step.arayuz import STEP

OUT = KOSU / 'AA'   # frozen inputs are seeded from records/AA/ by kayit_hazirla
KURAL = KAYIT / 'AA' / 'KURAL.md'   # frozen rule, read only
DEFTER = DEFTER_KOK / 'AA'
U_DEFTER = DEFTER_KOK / 'U'
ADI = 'STEP'
KATALOG = 'ortak/italya_katalog_le2015.csv'
IZGARA = 'ortak/italya_izgara.csv'
GRID_HIPER = list(itertools.product((3.5, 4.0, 4.5), (8, 20), (5.0, 20.0)))   # KURAL.md


def hiper_ad(h):
    return f'mseq{h[0]}_nmin{h[1]}_n0{h[2]}'


# Post-hoc varyant (koşu klasörüne yazılan EK.md; kayıt dışı): hiyerarşik ebeveyn, 2005+ M>=2,5 kaynak, Mseq=2,5
EK_AD = 'STEP-h'
EK_KW = dict(hiyerarsi=True, mc_kaynak=2.5)
EK_H = (2.5, 8, 5.0)


def model_kur(cat, grid, son, h, ad=ADI, **kw):
    m = STEP(cat[cat.zaman < pd.Timestamp(son)], grid, son=son, mseq=h[0], n_min=h[1], n0=h[2], **kw)
    box = m.kutu
    ayar = dict(sinir=(box[2], box[3], box[0], box[1]), baslangic_yil=1985, derinlik_max=30)
    return m, Model(ad, m.beklenen, True, ayar)


def kos_donem(cat, grid, donem, h, *, gun_siniri=None, ad=ADI, **kw):
    bas, son = (BAS6, SON6) if donem == '2006-2010' else (BAS11, SON11)
    if gun_siniri:
        son = (pd.Timestamp(bas) + pd.Timedelta(days=gun_siniri)).isoformat()
    m, model = model_kur(cat, grid, bas, h, ad, **kw)
    t0 = time.monotonic()
    d = kos_defter([model], bas, son, cat, grid, _kenarlar(), derinlik=DERINLIK, bolge='italya',
                   ilerleme=300)[ad]
    d.ek['sure_s'] = time.monotonic() - t0
    d.ek['metadata'] = m.metadata
    return d


def yaz(d, donem):
    defter_yaz(d, DEFTER, donem)
    np.savez_compressed(_marjinal_yol_aa(donem, d.ad), beklenen=d.beklenen, gozlem=d.gozlem,
                        logL=np.array([d.logL]))


def _marjinal_yol_aa(donem, ad=ADI):
    return DEFTER / f'{ad}__{donem}__marjinal.npz'


def yukle(ad, dizin, donem):
    d = defter_oku(ad, dizin, donem)
    with np.load(dizin / f'{ad}__{donem}__marjinal.npz') as z:
        d.beklenen, d.gozlem, d.logL = z['beklenen'], z['gozlem'], float(z['logL'][0])
    return d


def kural_sha():
    yol = KURAL
    if not yol.exists():
        raise SystemExit('Önce AA/KURAL.md yazılmalı')
    return sha256(yol)


def asama_sec(cat, grid, gun_siniri=None):
    sonuc = []
    en, en_ll = None, -np.inf
    for h in GRID_HIPER:
        t0 = time.monotonic()
        d = kos_donem(cat, grid, '2006-2010', h, gun_siniri=gun_siniri)
        ll = log_olabilirlik([d], [1.0], 2.95) if not gun_siniri else d.logL
        ll395 = log_olabilirlik([d], [1.0], 3.95) if not gun_siniri else None
        satir = dict(hiper=dict(mseq=h[0], n_min=h[1], n0=h[2]), logL_295=ll, logL_395=ll395,
                     N295=int((d.olay.mw >= 2.95 - 1e-9).sum()), Lam295=float(d.gun['Lam295'].sum()),
                     Lam395=float(d.gun['Lam395'].sum()), sure_s=time.monotonic() - t0,
                     genel_RJ=d.ek['metadata']['genel_RJ'], arka_plan=d.ek['metadata']['arka_plan'])
        sonuc.append(satir)
        print('SEC', hiper_ad(h), 'logL295=%.4f Lam295=%.2f Lam395=%.2f s=%.0f RSS=%.2fGB' % (
            ll, satir['Lam295'], satir['Lam395'], satir['sure_s'], rss_byte() / 1e9), flush=True)
        if ll > en_ll:                         # eşitlikte listedeki ilk
            en, en_ll, en_d = h, ll, d
    if gun_siniri:
        return None
    yaz(en_d, '2006-2010')
    secim = dict(secilen=dict(mseq=en[0], n_min=en[1], n0=en[2]), logL_295=en_ll, satirlar=sonuc,
                 kural_SHA256=kural_sha(), olcut='2006-2010 M>=2.95 Poisson logL, ≤2005 kurulum',
                 not_='2011-2015 açılmadan yazıldı; ölçümden sonra değişmez')
    _yaz(OUT / 'SECIM.json', secim)
    return secim


def asama_defter(cat, grid):
    sec = json.loads((OUT / 'SECIM.json').read_text())
    if sec['kural_SHA256'] != kural_sha():
        raise SystemExit('SECIM.json KURAL.md ile uyuşmuyor')
    s = sec['secilen']
    h = (s['mseq'], s['n_min'], s['n0'])
    d = kos_donem(cat, grid, '2011-2015', h)
    print('2011-2015', hiper_ad(h), 'N=%d logL=%.4f Lam295=%.2f Lam395=%.2f s=%.0f' % (
        d.N, d.logL, d.gun['Lam295'].sum(), d.gun['Lam395'].sum(), d.ek['sure_s']), flush=True)
    yaz(d, '2011-2015')
    _yaz(OUT / 'MODEL_2011.json', d.ek['metadata'])
    return d


def korelasyon(d, adlar, alt):
    """Olay başına log λ (M>=alt, aynı hedefler) korelasyon matrisi."""
    ref = d[adlar[0]].olay
    mask = ref.mw.to_numpy(float) >= alt - 1e-9
    L = np.vstack([np.log(d[a].lam()[mask]) for a in adlar])
    out = {}
    for i, j in itertools.combinations(range(len(adlar)), 2):
        out[f'{adlar[i]}|{adlar[j]}'] = dict(
            pearson=float(np.corrcoef(L[i], L[j])[0, 1]),
            spearman=float(stats.spearmanr(L[i], L[j])[0]),
            N=int(mask.sum()),
            fark_sd=float(np.std(L[i] - L[j])))
    return out


def gun_korelasyon(d, adlar, kol):
    G = np.vstack([d[a].gun[kol].to_numpy(float) for a in adlar])
    out = {}
    for i, j in itertools.combinations(range(len(adlar)), 2):
        out[f'{adlar[i]}|{adlar[j]}'] = dict(pearson_log=float(np.corrcoef(np.log(G[i]), np.log(G[j]))[0, 1]),
                                            spearman=float(stats.spearmanr(G[i], G[j])[0]))
    return out


def asama_olcum(ADI=ADI, cikti='OLCUM.json', ek=False):
    kural = kural_sha()
    d11 = {ADI: yukle(ADI, DEFTER, '2011-2015')}
    for a in (ETAS_LM, R_ORTAK):
        d11[a] = yukle(a, U_DEFTER, '2011-2015')
    satirlar = []
    for alt in ESIKLER:
        for taban in (ETAS_LM, R_ORTAK):
            satirlar.append(_satir(d11, [ADI], taban, alt, [1.0], 'tekil'))
    # E1 (Topluluk 2 kuralı), eşit ağırlık; Holm uygulanmadı
    e1 = [R_ORTAK, ETAS_LM, ADI]
    for alt in ESIKLER:
        for taban in (ETAS_LM, R_ORTAK):
            s = _satir(d11, e1, taban, alt, [1 / 3] * 3, 'esit (E1, Topluluk 2 kuralı; Holm yok)')
            satirlar.append(s)
    # referans: R+LM eşit (U)
    for alt in ESIKLER:
        satirlar.append(_satir(d11, [R_ORTAK, ETAS_LM], ETAS_LM, alt, [.5, .5], 'esit (U T1, referans)'))
    adlar = [ADI, R_ORTAK, ETAS_LM]
    kor = {str(alt): korelasyon(d11, adlar, alt) for alt in ESIKLER}
    gkor = {k: gun_korelasyon(d11, adlar, k) for k in ('Lam295', 'Lam395')}
    # STEP'in bütün-dönem tutarlılığı ve M-dağılımı: N/S/M zaten satirlar'da
    tekil = {a: dict(N295=int((d.olay.mw >= 2.95 - 1e-9).sum()), N395=int((d.olay.mw >= 3.95 - 1e-9).sum()),
                     N495=int((d.olay.mw >= 4.95 - 1e-9).sum()),
                     Lam295=float(d.gun['Lam295'].sum()), Lam395=float(d.gun['Lam395'].sum()),
                     Lam495=float(d.gun['Lam495'].sum()),
                     logL295=log_olabilirlik([d], [1.0], 2.95), logL395=log_olabilirlik([d], [1.0], 3.95))
             for a, d in d11.items()}
    d6 = {ADI: yukle(ADI, DEFTER, '2006-2010')}
    for a in (ETAS_LM, R_ORTAK):
        d6[a] = yukle(a, U_DEFTER, '2006-2010')
    tekil6 = {a: dict(N295=int((d.olay.mw >= 2.95 - 1e-9).sum()), Lam295=float(d.gun['Lam295'].sum()),
                      Lam395=float(d.gun['Lam395'].sum()), logL295=log_olabilirlik([d], [1.0], 2.95))
              for a, d in d6.items()}
    # Tanı (seçimde kullanılmaz): STEP yüzeyi c = N_gözlenen / Λ_STEP (2006–2010, eşik başına) ile ölçeklenir
    tani = {}
    for alt in ESIKLER:
        kol = alt_sutun(alt)
        n6 = int((d6[ADI].olay.mw >= alt - 1e-9).sum())
        c = n6 / float(d6[ADI].gun[kol].sum())
        satir = {}
        for taban in (ETAS_LM, R_ORTAK):
            x = _satir(d11, [ADI], taban, alt, [1.0], 'tani-olcekli', olcek=[c])
            e = _satir(d11, e1, taban, alt, [1 / 3] * 3, 'tani-olcekli E1', olcek=[1.0, 1.0, c])
            satir[taban] = dict(tekil=x, E1=e)
        tani[str(alt)] = dict(c=c, N_2006_2010=n6, satirlar=satir)
    sec = json.loads((OUT / 'SECIM.json').read_text())
    if ek:
        sec = dict(secilen=dict(mseq=EK_H[0], n_min=EK_H[1], n0=EK_H[2], **EK_KW))
    res = dict(durum=('POST-HOC (EK.md); ' if ek else '') + 'PROVISIONAL; geliştirme penceresi ölçümü; bağımsız skor-kodu incelemesi bekler; kör hüküm değil',
               satirlar=satirlar, tani_olcekli=tani, korelasyon_olay_log_lambda=kor, korelasyon_gunluk_Lambda=gkor,
               tekil_2011_2015=tekil, tekil_2006_2010=tekil6, secilen=sec['secilen'],
               model_2011=json.loads((OUT / ('MODEL_2011-EK.json' if ek else 'MODEL_2011.json')).read_text()),
               bilesen_kabul_kurali='R-ortak-kaskad e karşı M>=2,95 IG>0 ve z>1,645; M>=3,95 IG>0',
               IG_tanimi='ortalama log(λ_aday/λ_taban) − (Λ_aday−Λ_taban)/N; haftalık blok SE, tek yönlü z',
               kural_SHA256=kural, secim_SHA256=sha256(OUT / 'SECIM.json'),
               ek_SHA256=(sha256(OUT / 'EK.md') if ek else None),
               defter_SHA256={p.name: sha256(p) for p in sorted(DEFTER.glob('*__20*')) if (p.name.startswith(ADI + '__'))},
               kod_SHA256={str(p): sha256(p) for p in sorted(Path('knotenlinie/step').glob('*.py')) + [Path(__file__)]},
               python=sys.version, numpy=np.__version__, pandas=pd.__version__, rss_tepe_byte=rss_byte())
    _yaz(OUT / cikti, res)
    print(cikti, 'yazıldı', flush=True)


def main():
    kayit_hazirla('AA')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--asama', choices=('sec', 'defter', 'olcum', 'hepsi', 'ek'), default='hepsi')
    ap.add_argument('--gun-siniri', type=int, default=None, help='yalnız duman testi; hiçbir şey yazmaz')
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    DEFTER.mkdir(parents=True, exist_ok=True)
    kural_sha()
    cat = katalog_oku(VERI / KATALOG)
    grid = pd.read_csv(VERI / IZGARA)
    basla = time.monotonic()
    if args.asama == 'ek':
        for donem in ('2006-2010', '2011-2015'):
            d = kos_donem(cat, grid, donem, EK_H, gun_siniri=args.gun_siniri, ad=EK_AD, **EK_KW)
            print(donem, EK_AD, 'N=%d logL=%.4f Lam295=%.2f Lam395=%.2f s=%.0f' % (
                d.N, d.logL, d.gun['Lam295'].sum(), d.gun['Lam395'].sum(), d.ek['sure_s']), flush=True)
            if args.gun_siniri:
                return
            yaz(d, donem)
            if donem == '2011-2015':
                _yaz(OUT / 'MODEL_2011-EK.json', d.ek['metadata'])
        asama_olcum(EK_AD, 'OLCUM-EK.json', ek=True)
        return
    if args.asama in ('sec', 'hepsi'):
        asama_sec(cat, grid, args.gun_siniri)
        print('sec bitti', time.monotonic() - basla, flush=True)
        if args.gun_siniri:
            return
    if args.asama in ('defter', 'hepsi'):
        asama_defter(cat, grid)
        print('defter bitti', time.monotonic() - basla, flush=True)
    if args.asama in ('olcum', 'hepsi'):
        asama_olcum()


if __name__ == '__main__':
    main()
