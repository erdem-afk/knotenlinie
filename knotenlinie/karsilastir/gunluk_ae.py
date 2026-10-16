"""Deney AE: hiyerarşik büzülme (İtalya R-tipi ETAS → dış çekirdek), günlük çerçeve.

Aşamalar (kural: records/AE/KURAL.md, puanlamadan önce yazıldı):
  cekirdek  bölge ayarlarından (≤2005 'sec', ≤2010 'son') çekirdek JSON'ları
  sec       ≤2005 cezalı ayarlar (varyant × τ), 2006–2010 defterleri, M≥2,95 logL ile seçim (SECIM.json)
  son       seçileni ≤2010 ile yeniden kur, 2011–2015 defterini yaz (SON_KURULUM.json)
  olcum     defterlerden ölçüm (OLCUM.json); AE ve E6 − ETAS-LM / − R-ortak-kaskad
Ölçüm defterlerden hesaplanır (U/AB ile aynı kod); R ve ETAS-LM defterleri U'nundur.
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

from knotenlinie.etas_hiyerarsi import cekirdek as C
from knotenlinie.etas_hiyerarsi import ceza as Z
from knotenlinie.etas_uzun.arayuz import TamGecmis, UzunETAS
from knotenlinie.karsilastir.gunluk_r import kaynak_oku, rss_byte
from knotenlinie.karsilastir.gunluk_u import (DEFTER as U_DEFTER, ETAS_LM, R_ORTAK, _satir, _yaz, nsm_mixture)
from knotenlinie.karsilastir.kosucu import Model
from knotenlinie.karsilastir.ortak4 import gecmis_ayari
from knotenlinie.ortak_zemin.arayuz import ayar_tabani
from knotenlinie.ortak_zemin.veri import VERI, katalog_oku, sha256
from knotenlinie.yollar import KAYIT, KOSU, kayit_hazirla
from knotenlinie.skor_defteri.defter import KOK, alt_indeks, defter_oku, defter_yaz, kos_defter
from knotenlinie.skor_defteri.karisim import log_olabilirlik

OUT = KOSU / 'AE'   # frozen inputs are seeded from records/AE/ by kayit_hazirla
KURAL = KAYIT / 'AE' / 'KURAL.md'   # frozen rule, read only
DEFTER = KOK / 'AE'
HIY = VERI / 'ortak/hiyerarsi'
KATALOG = 'ortak/italya_katalog_le2015.csv'
PENCERE = {'2006-2010': ('2006-01-01T00:00:00Z', '2011-01-01T00:00:00Z'),
           '2011-2015': ('2011-01-01T00:00:00Z', '2016-01-01T00:00:00Z')}
R_JSON = {'sec': VERI / 'ortak/uzun/etas_s_le2005.json', 'son': VERI / 'ortak/uzun/etas_ortak.json'}
SON_AYAR = {'sec': '2006-01-01', 'son': '2011-01-01'}
YIL_SON = {'sec': 2005, 'son': 2010}
BOLGELER = ('scsn', 'geonet')   # dış çekirdekler (yan tezgâh ayarları)
ESIKLER = (2.95, 3.95, 4.95)
VARYANTLAR = ('A', 'B')
TAU_SONLU = (0.8, 0.4, 0.2, 0.1, 0.05)       # sıcak başlangıç sırası (büyükten küçüğe)
AD = 'AE'


def kenarlar():
    return np.r_[np.round(2.95 + 0.1 * np.arange(61), 2), np.inf]


def aday_adi(varyant, tau, onek='AE'):
    return f'{onek}-{varyant}-t{tau:g}'


def _json(yol, nesne):
    _yaz(yol, nesne)


def _oku(yol):
    return json.loads(Path(yol).read_text())


# --------------------------------------------------------------------------- #
# Çekirdek
# --------------------------------------------------------------------------- #
def cekirdek_asama(asama):
    y = YIL_SON[asama]
    kayit = [_oku(HIY / f'cekirdek_{b}_le{y}.json') for b in BOLGELER]
    havuz_i = _oku(HIY / 'cekirdek_italya_1985_2004.json')
    A = C.havuz(kayit, gevsek=True)
    A_sikı = C.havuz(kayit, gevsek=False)
    B = C.tek_cekirdek(havuz_i)
    sonuc = dict(asama=asama, ayar_yili_son=y, A=A, A_siki_tanimli=A_sikı is not None, B=B,
                 bolgeler=[{k: v for k, v in r.items() if k not in ('x', 'baslangic_sonuclari', 'bilgi')} for r in kayit],
                 bolge_bilgi={r['ad']: r['bilgi'] for r in kayit}, havuz_italya=havuz_i, m_ref=C.M_REF)
    _json(HIY / f'cekirdek_{asama}.json', sonuc)
    return sonuc


def ek1_cekirdek(cek_sec):
    """KAYIT DIŞI EK-1: K_ref bileşeni de cezalanır (dallanma kapısı yok)."""
    kay = [dict(r, dallanma=0.0) for r in cek_sec['bolgeler']]
    A = C.havuz(kay, gevsek=True)
    hi = dict(cek_sec['havuz_italya'], dallanma=0.0)
    return dict(A=A, B=C.tek_cekirdek(hi))


# --------------------------------------------------------------------------- #
# Model / defter
# --------------------------------------------------------------------------- #
def italya_model(p, grid, raw, ad):
    m = UzunETAS(p, grid, adim=32, nesil=10)
    s = gecmis_ayari(m, 'italya')
    s['derinlik_max'] = 30
    return Model(ad, TamGecmis(m, raw).beklenen, True, s)


def defter_uret(model, donem, cat, grid, *, bolge='italya', ilerleme=300, bas_son=None):
    bas, son = bas_son or PENCERE[donem]
    t = time.monotonic()
    d = kos_defter([model], bas, son, cat, grid, kenarlar(), derinlik=(0, 30), bolge=bolge,
                   ilerleme=ilerleme)[model.ad]
    print(donem, model.ad, 'N=%d logL=%.4f Lam295=%.2f Lam395=%.2f s=%.0f RSS=%.2fGB' % (
        d.N, d.logL, d.gun['Lam295'].sum(), d.gun['Lam395'].sum(), time.monotonic() - t, rss_byte() / 1e9),
        flush=True)
    return d


def defter_kaydet(d, donem, dizin=None):
    dizin = dizin or DEFTER
    defter_yaz(d, dizin, donem)
    np.savez_compressed(Path(dizin) / f'{d.ad}__{donem}__marjinal.npz', beklenen=d.beklenen, gozlem=d.gozlem,
                        logL=np.array([d.logL]))


def yukle(ad, dizin, donem):
    d = defter_oku(ad, dizin, donem)
    with np.load(Path(dizin) / f'{ad}__{donem}__marjinal.npz') as z:
        d.beklenen, d.gozlem, d.logL = z['beklenen'], z['gozlem'], float(z['logL'][0])
    return d


def ortak_veri():
    cat = katalog_oku(VERI / KATALOG)
    raw, paths, report = kaynak_oku()
    grid = ayar_tabani('italya', son='2006-01-01').izgara
    return cat, raw, grid, paths


def kural_kapisi():
    yol = KURAL
    if not yol.exists():
        raise SystemExit('Önce AE/KURAL.md yazılmalı')
    return sha256(yol)


# --------------------------------------------------------------------------- #
# Aşama sec
# --------------------------------------------------------------------------- #
def asama_sec(args, ek=False):
    kural = kural_kapisi()
    onek = 'EK1' if ek else 'AE'
    ddir = DEFTER / 'ek1' if ek else DEFTER
    adir = HIY / ('ek1_sec' if ek else 'ae_sec')
    ddir.mkdir(parents=True, exist_ok=True)
    adir.mkdir(parents=True, exist_ok=True)
    cek = _oku(HIY / 'cekirdek_sec.json')
    if ek:
        cek = ek1_cekirdek(cek)
    cat, raw, grid, _ = ortak_veri()
    L, meta = Z.italya_L(raw, grid, '2006-01-01')
    rj = _oku(R_JSON['sec'])
    x_r = np.array(rj['x'])
    # özdeşlik kapısı: τ=∞ nesnesi R'nin kaydıyla aynı logL'yi vermeli
    ll_r = float(-L.objectif(x_r, 'ortak')[0] * len(L.t))
    print('R ≤2005 logL kayıt %.6f, yeniden %.6f' % (rj['logL'], ll_r), flush=True)
    if abs(ll_r - rj['logL']) > 1e-6 * abs(rj['logL']):
        raise SystemExit('Italya_L R kaydıyla eşleşmiyor')
    sonuc = {}
    for v in VARYANTLAR:
        cv = cek[v]
        if cv is None:
            print('varyant', v, 'tanımsız', flush=True)
            continue
        x0 = x_r
        for tau in TAU_SONLU:
            ad = aday_adi(v, tau, onek)
            yol = adir / f'{ad}.json'
            if yol.exists():
                fit = _oku(yol)
                x0 = np.array(fit['x'])
            else:
                t0 = time.monotonic()
                fit = Z.ayarla_ceza(L, cv['tema'], tau, x0, maksiter=args.maksiter, maske=cv['maske'])
                fit['duvar_saniye'] = time.monotonic() - t0
                _json(yol, fit)
                x0 = np.array(fit['x'])
            print(ad, 'logL=%.2f ceza=%.2f n=%.6f nit=%d basari=%s' % (
                fit['logL'], fit['ceza'], fit['dallanma'], fit['nit'], fit['basari']), flush=True)
            sonuc[ad] = dict(varyant=v, tau=tau, fit_logL=fit['logL'], ceza=fit['ceza'], dallanma=fit['dallanma'],
                             basari=fit['basari'], parametreler=fit['parametreler'])
    # 2006–2010 puanlama: yalnız ayar başarılı adaylar; sıra sabit (KURAL: τ büyükten küçüğe, A sonra B)
    for ad in list(sonuc):
        yol_def = ddir / f'{ad}__2006-2010__marjinal.npz'
        if yol_def.exists():
            d = yukle(ad, ddir, '2006-2010')
        else:
            fit = _oku(adir / f'{ad}.json')
            p = Z.model_p(rj, fit)
            mod = italya_model(p, grid, raw, ad)
            d = defter_uret(mod, '2006-2010', cat, grid)
            defter_kaydet(d, '2006-2010', ddir)
            del mod
            gc.collect()
        sonuc[ad]['logL_295'] = log_olabilirlik([d], [1.0], 2.95)
        sonuc[ad]['logL_395'] = log_olabilirlik([d], [1.0], 3.95)
        sonuc[ad]['Lambda295'] = float(d.gun['Lam295'].sum())
        sonuc[ad]['Lambda395'] = float(d.gun['Lam395'].sum())
    dR = yukle(R_ORTAK, U_DEFTER, '2006-2010')
    sonuc['R (τ=∞)'] = dict(varyant='-', tau=float('inf'), logL_295=log_olabilirlik([dR], [1.0], 2.95),
                            logL_395=log_olabilirlik([dR], [1.0], 3.95), Lambda295=float(dR.gun['Lam295'].sum()),
                            Lambda395=float(dR.gun['Lam395'].sum()), dallanma=rj['dallanma'])
    en = max(sonuc, key=lambda k: sonuc[k]['logL_295'])
    res = dict(secilen=en, adaylar=sonuc, kural_SHA256=kural, secim='2006–2010 M≥2,95 logL (log n! hariç), ≤2005 ayar ve çekirdek',
               cekirdek_sec_SHA256=sha256(HIY / 'cekirdek_sec.json'), R_x_kaynak=str(R_JSON['sec']),
               R_logL_yeniden=ll_r, N_295_2006_2010=int(len(dR.olay)))
    _json(OUT / ('EK1_SECIM.json' if ek else 'SECIM.json'), res)
    print('SEÇİLEN', en, {k: round(v['logL_295'], 3) for k, v in sonuc.items()}, flush=True)


# --------------------------------------------------------------------------- #
# Aşama son
# --------------------------------------------------------------------------- #
def asama_son(args):
    kural = kural_kapisi()
    sec = _oku(OUT / 'SECIM.json')
    if sec['kural_SHA256'] != kural:
        raise SystemExit('KURAL.md seçimden sonra değişmiş')
    en = sec['secilen']
    cat, raw, grid, _ = ortak_veri()
    rj = _oku(R_JSON['son'])
    if en.startswith('R '):
        # AE = R: U'nun R-ortak-kaskad 2011–2015 defteri AE adıyla kopyalanır (özdeş içerik)
        import shutil
        DEFTER.mkdir(parents=True, exist_ok=True)
        for ek in ('olay.csv.gz', 'gun.csv.gz', 'marjinal.npz'):
            shutil.copyfile(U_DEFTER / f'{R_ORTAK}__2011-2015__{ek}', DEFTER / f'{AD}__2011-2015__{ek}')
        d = yukle(AD, DEFTER, '2011-2015')
        print('Seçilen R (τ=∞): AE = R-ortak-kaskad; defter kopyalandı, logL=%.4f' % d.logL, flush=True)
        _json(OUT / 'SON_KURULUM.json', dict(secilen=en, parametreler=rj['parametreler'], dallanma=rj['dallanma'],
                                             not_='AE = R-ortak-kaskad (τ=∞ seçildi); ≤2010 ayarı etas_ortak.json',
                                             defter_logL_2011_2015=d.logL, N=d.N,
                                             Lambda295=float(d.gun['Lam295'].sum()),
                                             Lambda395=float(d.gun['Lam395'].sum())))
        return
    v, tau = sec['adaylar'][en]['varyant'], sec['adaylar'][en]['tau']
    cek = _oku(HIY / 'cekirdek_son.json')[v]
    if cek is None:
        raise SystemExit('Seçilen varyantın ≤2010 çekirdeği tanımsız')
    L, meta = Z.italya_L(raw, grid, '2011-01-01')
    x_r = np.array(rj['x'])
    ll_r = float(-L.objectif(x_r, 'ortak')[0] * len(L.t))
    print('R ≤2010 logL kayıt %.6f, yeniden %.6f' % (rj['logL'], ll_r), flush=True)
    if abs(ll_r - rj['logL']) > 1e-6 * abs(rj['logL']):
        raise SystemExit('Italya_L R(≤2010) kaydıyla eşleşmiyor')
    x0 = x_r
    kayit = None
    for t_ in sorted([t for t in TAU_SONLU if t >= tau], reverse=True):   # aynı sıcak başlangıç zinciri
        kayit = Z.ayarla_ceza(L, cek['tema'], t_, x0, maksiter=args.maksiter, maske=cek['maske'])
        x0 = np.array(kayit['x'])
        print('son zincir τ=%g logL=%.2f ceza=%.2f n=%.6f' % (t_, kayit['logL'], kayit['ceza'], kayit['dallanma']),
              flush=True)
    _json(HIY / 'ae_son.json', kayit)
    p = Z.model_p(rj, kayit)
    mod = italya_model(p, grid, raw, AD)
    d = defter_uret(mod, '2011-2015', cat, grid)
    defter_kaydet(d, '2011-2015')
    _json(OUT / 'SON_KURULUM.json', dict(secilen=en, varyant=v, tau=tau, parametreler=kayit['parametreler'],
                                         dallanma=kayit['dallanma'], logL_fit=kayit['logL'], ceza=kayit['ceza'],
                                         defter_logL_2011_2015=d.logL, N=d.N,
                                         Lambda295=float(d.gun['Lam295'].sum()), Lambda395=float(d.gun['Lam395'].sum()),
                                         cekirdek_SHA256=sha256(HIY / 'cekirdek_son.json')))


# --------------------------------------------------------------------------- #
# Aşama olcum
# --------------------------------------------------------------------------- #
def tema_dogal(tema, mc0=Z.MC0_ITALYA):
    """Çekirdek temasını (K_ref, ..., log(γ+ofs)) İtalya Mc0'ında doğal parametrelere çevirir."""
    t = np.array([np.nan if x is None else x for x in tema], float)
    alpha, gamma = np.exp(t[2]), np.exp(t[6]) - C.GAMMA_OFS
    dm = C.M_REF - mc0
    return dict(K=float(np.exp(t[0]) / 10 ** (alpha * dm)), c=float(np.exp(t[1])), alpha=float(alpha),
                p=float(np.exp(t[3])), D=float(np.exp(t[4]) / 10 ** (gamma * dm)), q=float(np.exp(t[5])),
                gamma=float(gamma))


LM_J = dict(mu=0.59973, K=0.02828, c=0.01461, alpha=0.56458, p=1.16, D=1.10, q=1.5, gamma=0.0)


def asama_olcum(args):
    kural = kural_kapisi()
    sec = _oku(OUT / 'SECIM.json')
    d = {R_ORTAK: yukle(R_ORTAK, U_DEFTER, '2011-2015'), ETAS_LM: yukle(ETAS_LM, U_DEFTER, '2011-2015')}
    en = sec['secilen']
    ae_r = en.startswith('R ')
    ae_var = True
    satir = []
    if ae_var:
        d[AD] = yukle(AD, DEFTER, '2011-2015')
        for alt in ESIKLER:
            for taban in ((ETAS_LM,) if ae_r else (ETAS_LM, R_ORTAK)):
                satir.append(_satir(d, [AD], taban, alt, [1.0], 'tekil'))
        # E6: eşit {AE, ETAS-LM}; − LM hüküm, − R yan satır; U'nun eşit R+LM satırı yanında
        for alt in ESIKLER:
            for taban in (ETAS_LM, R_ORTAK):
                s = _satir(d, [AD, ETAS_LM], taban, alt, [0.5, 0.5], 'esit')
                s['topluluk'] = 'E6'
                satir.append(s)
    for alt in ESIKLER:
        for taban in (ETAS_LM, R_ORTAK):
            s = _satir(d, [R_ORTAK, ETAS_LM], taban, alt, [0.5, 0.5], 'esit')
            s['topluluk'] = 'U-T1 eşit (R+LM)'
            satir.append(s)
    rj_son = _oku(R_JSON['son'])
    tablo = dict(R=rj_son['parametreler'], LM_J=LM_J)
    son = _oku(OUT / 'SON_KURULUM.json') if ae_var else None
    cek_son = _oku(HIY / 'cekirdek_son.json')
    tablo['AE'] = son['parametreler']
    for v in VARYANTLAR:
        if cek_son.get(v):
            tablo[f'cekirdek_{v}_dogal_Mc0_2.5'] = tema_dogal(cek_son[v]['tema'])
            tablo[f'cekirdek_{v}_maske'] = cek_son[v]['maske']
    res = dict(satirlar=satir, secim=sec, parametre_tablosu=tablo, son_kurulum=son,
               durum='PROVISIONAL; bağımsız skor-kodu incelemesi yok; kör hüküm değil',
               defter_SHA256={p.name: sha256(p) for p in sorted(DEFTER.glob(f'{AD}__*'))},
               kural_SHA256=kural, python=sys.version, numpy=np.__version__, pandas=pd.__version__)
    _json(OUT / 'OLCUM.json', res)
    for s in satir:
        print(s.get('topluluk') or s['aday'], s['taban'], s['esik'], 'N', s['N'],
              'IG %.4f ± %.4f z %.2f' % (s['IG'], s['SE_blok'], s['z']), flush=True)


# --------------------------------------------------------------------------- #
# KAYIT DIŞI EK-1: K_ref de cezalı; seçilen ≤2010'la yeniden kurulur, 2011–2015'te bir kez puanlanır
# --------------------------------------------------------------------------- #
def ek1_son(args):
    sec = _oku(OUT / 'EK1_SECIM.json')
    en = sec['secilen']
    if en.startswith('R '):
        print('EK-1 seçimi R; 2011–2015 puanlaması yok', flush=True)
        return
    v, tau = sec['adaylar'][en]['varyant'], sec['adaylar'][en]['tau']
    cek = ek1_cekirdek(_oku(HIY / 'cekirdek_son.json'))[v]
    cat, raw, grid, _ = ortak_veri()
    rj = _oku(R_JSON['son'])
    L, meta = Z.italya_L(raw, grid, '2011-01-01')
    x0 = np.array(rj['x'])
    kayit = None
    for t_ in sorted([t for t in TAU_SONLU if t >= tau], reverse=True):
        kayit = Z.ayarla_ceza(L, cek['tema'], t_, x0, maksiter=args.maksiter, maske=cek['maske'])
        x0 = np.array(kayit['x'])
        print('EK1 son zincir τ=%g logL=%.2f ceza=%.2f n=%.6f' % (t_, kayit['logL'], kayit['ceza'], kayit['dallanma']),
              flush=True)
    _json(HIY / 'ek1_son.json', kayit)
    ddir = DEFTER / 'ek1'
    mod = italya_model(Z.model_p(rj, kayit), grid, raw, 'EK1')
    d = defter_uret(mod, '2011-2015', cat, grid)
    defter_kaydet(d, '2011-2015', ddir)
    dd = {R_ORTAK: yukle(R_ORTAK, U_DEFTER, '2011-2015'), ETAS_LM: yukle(ETAS_LM, U_DEFTER, '2011-2015'), 'EK1': d}
    satir = []
    for alt in ESIKLER:
        for taban in (ETAS_LM, R_ORTAK):
            satir.append(_satir(dd, ['EK1'], taban, alt, [1.0], 'tekil'))
            s = _satir(dd, ['EK1', ETAS_LM], taban, alt, [0.5, 0.5], 'esit')
            s['topluluk'] = 'E6-EK1'
            satir.append(s)
    res = dict(durum='KAYIT DIŞI (EK-1); hükmün yerine geçmez', secim=sec, parametreler=kayit['parametreler'],
               dallanma=kayit['dallanma'], ceza=kayit['ceza'], logL_fit=kayit['logL'], satirlar=satir,
               Lambda295=float(d.gun['Lam295'].sum()), Lambda395=float(d.gun['Lam395'].sum()),
               defter_SHA256={q.name: sha256(q) for q in sorted(ddir.glob('EK1__2011-2015*'))})
    _json(OUT / 'EK1_OLCUM.json', res)
    for r in satir:
        print(r.get('topluluk') or r['aday'], r['taban'], r['esik'], 'N', r['N'],
              'IG %.4f ± %.4f z %.2f Lam %.1f/%.1f' % (r['IG'], r['SE_blok'], r['z'], r['Lambda_aday'], r['Lambda_taban']), flush=True)


def main():
    kayit_hazirla('AE')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--asama', choices=('cekirdek-sec', 'cekirdek-son', 'sec', 'son', 'olcum', 'ek1-sec', 'ek1-son'), required=True)
    ap.add_argument('--maksiter', type=int, default=300)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if a.asama == 'cekirdek-sec':
        cekirdek_asama('sec')
    elif a.asama == 'cekirdek-son':
        cekirdek_asama('son')
    elif a.asama == 'sec':
        asama_sec(a)
    elif a.asama == 'ek1-sec':
        asama_sec(a, ek=True)
    elif a.asama == 'ek1-son':
        ek1_son(a)
    elif a.asama == 'son':
        asama_son(a)
    else:
        asama_olcum(a)


if __name__ == '__main__':
    main()
