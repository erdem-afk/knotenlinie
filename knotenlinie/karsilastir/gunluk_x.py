"""Deney X: sonlu kaynak çekirdeğinin J çerçevesinde ölçümü (İtalya günlük).

Seçim: son=2006 (S'nin <=2005 R ayarı) ile 2006-2010 M>=2,95 logL'i üstünden
{R, X-a, X-b} x M_s in {5,0; 5,5} arasından bir varyant.  Seçilen <=2010 ile
yeniden kurulur ve 2011-2015'te bir kez puanlanır (R-ortak-kaskad ve ETAS-LM
tabanlarına karşı).  Bütün puanlanan modeller için olay/gün defteri yazılır.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import resource
import sys
import time

import numpy as np
import pandas as pd
from scipy.special import gammaln

from knotenlinie.etas import katalog as K
from knotenlinie.etas import model as M
from knotenlinie.etas_lm.arayuz import ETASLM
from knotenlinie.etas_sonlu import gcmt as G
from knotenlinie.etas_sonlu import defter as DF
from knotenlinie.etas_sonlu.model import SonluKaskad
from knotenlinie.etas_sonlu.yon import Yon
from knotenlinie.etas_uzun.arayuz import ebeveynler
from knotenlinie.karsilastir.gunluk_j import esik_kosu
from knotenlinie.karsilastir.blok import blok_ozeti
from knotenlinie.karsilastir.kosucu import (KESIM, Kosu, Model, geometri, karsilastir,
                                      katalog_kontrol, kos, olay_kutulari, utc)
from knotenlinie.karsilastir.puan import holm
from knotenlinie.ortak_zemin.arayuz import DuzETAS
from knotenlinie.ortak_zemin.veri import VERI, katalog_dogrula, katalog_oku, sha256, json_yaz
from knotenlinie.yollar import KAYIT, KOSU, kayit_hazirla

OUT = KOSU / 'X'   # frozen inputs are seeded from records/X/ by kayit_hazirla
KURAL = KAYIT / 'X' / 'KURAL.md'   # frozen rule, read only
DEFTER = KOSU / 'defter/X'
DIZIN = VERI / 'ortak/uzun'
GCMT_YOL = VERI / 'kesik-2015/gcmt_le2015.ndk'
KATALOG = VERI / 'ortak/italya_katalog_le2015.csv'
IZGARA = VERI / 'ortak/italya_izgara.csv'
SEL_BAS, SEL_SON = '2006-01-01T00:00:00Z', '2011-01-01T00:00:00Z'
OLC_BAS, OLC_SON = '2011-01-01T00:00:00Z', '2016-01-01T00:00:00Z'
TOHUM = 20261005
MS_LISTE = (5.0, 5.5)
YON_TIPLERI = ('a', 'b')
DERINLIK = (0.0, 30.0)
KUTU = (35.8, 47.9, 5.5, 19.5)


def kenarlar():
    return np.r_[np.round(np.arange(2.95, 9.0, .1), 2), np.inf]


def rss():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1 if sys.platform == 'darwin' else 1024)


def kaynak_oku():
    paths = [VERI / 'kesik-2015/horus' / f'horus_{y}.txt' for y in range(1985, 2016)]
    raw, report = K.horus_oku([str(p) for p in paths])
    if report['atilan_kesim']:
        raise ValueError('HORUS 2016+ kapısı')
    raw = katalog_dogrula(raw.rename(columns=dict(time_utc='zaman', lat='enlem',
                                                  lon='boylam', depth_km='derinlik', mag='mw')))
    if (raw.zaman >= KESIM).any():
        raise ValueError('HORUS 2016+ kapısı')
    return raw, paths, report


def _cerceve(bas, son, m, grid, g):
    t0, t1 = utc(bas), utc(son)
    return (t0.isoformat(), t1.isoformat(), tuple(DERINLIK),
            hashlib.sha256(g.tobytes() + np.round(m, 12).tobytes()).hexdigest(), 'italya')


def _hedef_kutulari(cat, bas, son, grid, m):
    t0, t1 = utc(bas), utc(son)
    katalog = katalog_kontrol(cat)
    hedef_all = katalog[(katalog.zaman >= t0) & (katalog.zaman < t1)]
    return olay_kutulari(hedef_all, grid, m, DERINLIK)


def coklu_kos(k, temel_ad, temel, varyantlar, bas, son, cat, grid, edges):
    """Tek gün döngüsünde R ve bütün sonlu varyantlar; temel hesap paylaşılır."""
    g, m = geometri(grid, edges)
    shape = (len(g), len(m) - 1)
    cerceve = _cerceve(bas, son, m, grid, g)
    hedef, ci, mi = _hedef_kutulari(cat, bas, son, grid, m)
    t0 = utc(bas)
    gozlem = np.zeros(shape, dtype=int)
    np.add.at(gozlem, (ci, mi), 1)
    gun_idx = ((hedef.zaman - t0) / pd.Timedelta(days=1)).to_numpy(float).astype(int)
    ndays = int((utc(son) - t0) / pd.Timedelta(days=1))
    isimler = [temel_ad] + list(varyantlar)
    olay_lam = {n: np.empty(len(hedef)) for n in isimler}
    toplam = {n: np.zeros(shape) for n in isimler}
    gun_bins = {n: np.zeros((ndays, shape[1])) for n in isimler}
    ll = {n: 0.0 for n in isimler}
    t_start = time.monotonic()
    for d in range(ndays):
        a = t0 + pd.Timedelta(days=d)
        z = a + pd.Timedelta(days=1)
        stop = int(k.zaman.searchsorted(a, side='left'))
        h = k.iloc[:stop]
        out0, ctx = temel.temel(a, z, h, grid, edges)
        lamlar = {temel_ad: out0}
        adlar = list(varyantlar)
        kaynaklar = [varyantlar[n][0].duzeltme_kaynak(ctx, varyantlar[n][1], varyantlar[n][2])
                     for n in adlar]
        duzeltmeler = temel.duzeltme_coklu(ctx, kaynaklar)
        for n, dd in zip(adlar, duzeltmeler):
            lamlar[n] = out0 if dd is None else out0 + dd
        idx = np.flatnonzero(gun_idx == d)
        for n, lam in lamlar.items():
            toplam[n] += lam
            gun_bins[n][d] = lam.sum(axis=0)
            ll[n] -= float(lam.sum())
            if len(idx):
                rates = lam[ci[idx], mi[idx]]
                olay_lam[n][idx] = rates
                if (rates == 0).any():
                    ll[n] = -np.inf
                else:
                    ll[n] += float(np.log(rates).sum())
                _, cnt = np.unique(ci[idx] * shape[1] + mi[idx], return_counts=True)
                ll[n] -= float(gammaln(cnt + 1).sum())
        if d % 50 == 0:
            print(f'  gun {d}/{ndays} {round(time.monotonic() - t_start, 1)}s', flush=True)
    runs = {n: Kosu(n, toplam[n], gozlem.copy(), olay_lam[n], ll[n], hedef.copy(), cerceve)
            for n in isimler}
    return runs, gun_bins, hedef, ci, mi, gun_idx, ndays


def tek_kos(beklenen, ad, bas, son, cat, grid, edges, gecmis_k):
    """Tek model (ETAS-LM) için gün bütünlerini de veren koşucu kopyası."""
    g, m = geometri(grid, edges)
    shape = (len(g), len(m) - 1)
    cerceve = _cerceve(bas, son, m, grid, g)
    hedef, ci, mi = _hedef_kutulari(cat, bas, son, grid, m)
    t0 = utc(bas)
    gozlem = np.zeros(shape, dtype=int)
    np.add.at(gozlem, (ci, mi), 1)
    gun_idx = ((hedef.zaman - t0) / pd.Timedelta(days=1)).to_numpy(float).astype(int)
    ndays = int((utc(son) - t0) / pd.Timedelta(days=1))
    olay_lam = np.empty(len(hedef))
    toplam = np.zeros(shape)
    gun_bins = np.zeros((ndays, shape[1]))
    ll = 0.0
    for d in range(ndays):
        a = t0 + pd.Timedelta(days=d)
        z = a + pd.Timedelta(days=1)
        h = gecmis_k[gecmis_k.zaman < a].copy(deep=True)
        lam = beklenen(a, z, h, grid.copy(deep=True), m.copy())
        if lam.shape != shape:
            raise ValueError('Tek koşu şekli uyuşmuyor')
        toplam += lam
        gun_bins[d] = lam.sum(axis=0)
        ll -= float(lam.sum())
        idx = np.flatnonzero(gun_idx == d)
        if len(idx):
            rates = lam[ci[idx], mi[idx]]
            olay_lam[idx] = rates
            if (rates == 0).any():
                ll = -np.inf
            else:
                ll += float(np.log(rates).sum())
            _, cnt = np.unique(ci[idx] * shape[1] + mi[idx], return_counts=True)
            ll -= float(gammaln(cnt + 1).sum())
    return Kosu(ad, toplam, gozlem, olay_lam, ll, hedef, cerceve), gun_bins


def defter_yaz(donem, runs, gun_bins, hedef, ci, mi, ndays, bas, edges):
    j395 = int(np.flatnonzero(np.isclose(edges[:-1], 3.95, atol=1e-10, rtol=0))[0])
    gunler = pd.date_range(utc(bas), periods=ndays, freq='D')
    gs = hedef.zaman.dt.strftime('%Y-%m-%d').to_numpy()
    for n in runs:
        olay = DF.olay_cercevesi(hedef, ci, mi, runs[n].olay_oranlari, gs)
        gun = DF.gun_cercevesi(gunler, gun_bins[n][:, :].sum(axis=1), gun_bins[n][:, j395:].sum(axis=1))
        DF.yaz(DEFTER, n, donem, olay, gun)


def satir_yap(aday, taban, donem, esik, runs, gun_bins, hedef, gun_idx, ndays, grid, edges):
    a = esik_kosu(runs[aday], grid, edges, esik)
    b = esik_kosu(runs[taban], grid, edges, esik)
    cift = karsilastir(a, b)
    j = int(np.flatnonzero(np.isclose(edges[:-1], esik, atol=1e-10, rtol=0))[0])
    keep = hedef.mw.to_numpy(float) >= esik - 1e-12
    x = np.log(a.olay_oranlari) - np.log(b.olay_oranlari)
    n = int(keep.sum())
    D = np.zeros(ndays)
    N = np.zeros(ndays, int)
    np.add.at(D, gun_idx[keep], x)
    np.add.at(N, gun_idx[keep], 1)
    delta = gun_bins[aday][:, j:].sum(axis=1) - gun_bins[taban][:, j:].sum(axis=1)
    gunler = pd.date_range(utc(SEL_BAS if donem == '2006-2010' else OLC_BAS), periods=ndays, freq='D')
    blok = blok_ozeti(D - delta, N, gunler)
    if n and not np.isclose((a.logL - b.logL) / n, blok['IG'], rtol=1e-9, atol=1e-9):
        raise ValueError(f'{aday}/{taban}/{donem}/{esik}: defter IG != koşucu logL farkı')
    return dict(aday=aday, taban=taban, donem=donem, esik=float(esik), N=n,
                Lambda_aday=float(a.beklenen.sum()), Lambda_taban=float(b.beklenen.sum()),
                IG=blok['IG'], IG_olay=float(x.mean()) if n else None,
                integral=float(-delta.sum() / n) if n else None,
                SE_blok=blok['SE_blok'], z=blok['z'], p_tek=blok['p_tek'],
                blok_sayisi=blok.get('blok_sayisi'),
                NSM_aday=a.tutarlilik(tekrar=10000, tohum=TOHUM),
                NSM_taban=b.tutarlilik(tekrar=10000, tohum=TOHUM + 1),
                p_T=cift['p_T'], p_W=cift['p_W'], logL_aday=a.logL, logL_taban=b.logL)


def buyuk_ebeveyn_maske(hedef, k, met, *, gun=30.0, km=100.0):
    p5 = k[k.mw >= 5.0].reset_index(drop=True)
    if not len(p5):
        return np.zeros(len(hedef), bool)
    xp, yp = met.km(p5.boylam.to_numpy(float), p5.enlem.to_numpy(float))
    out = np.zeros(len(hedef), bool)
    for i, row in enumerate(hedef.itertuples(index=False)):
        lo = row.zaman - pd.Timedelta(days=gun)
        j0 = int(p5.zaman.searchsorted(lo, side='left'))
        j1 = int(p5.zaman.searchsorted(row.zaman, side='left'))
        if j1 > j0:
            x0, y0 = met.km(row.boylam, row.enlem)
            d = np.hypot(xp[j0:j1] - x0, yp[j0:j1] - y0)
            out[i] = bool((d <= km).any())
    return out


def alt_kume_satiri(aday, taban, esik, runs, gun_bins, hedef, grid, edges, k, met):
    a = esik_kosu(runs[aday], grid, edges, esik)
    b = esik_kosu(runs[taban], grid, edges, esik)
    j = int(np.flatnonzero(np.isclose(edges[:-1], esik, atol=1e-10, rtol=0))[0])
    esikli = hedef.mw.to_numpy(float) >= esik - 1e-12
    keep = buyuk_ebeveyn_maske(hedef, k, met)[esikli]  # a.olay_oranlari eşiğe süzülmüş
    if not keep.any():
        return dict(N=0, IG_olay=None, IG=None, integral=None)
    x = np.log(a.olay_oranlari) - np.log(b.olay_oranlari)
    delta = float((gun_bins[aday][:, j:].sum() - gun_bins[taban][:, j:].sum()).sum())
    n = int(keep.sum())
    return dict(N=n, IG_olay=float(x[keep].mean()),
                IG=float(x[keep].mean() - delta / n), integral=float(-delta / n))


def defter_dogrula(donem, runs, taban):
    """Defterden okunan logL farkı (taban'a göre) koşucununkiyle 1e-9 göreli içinde eşleşmeli.

    log(n!) modelden bağımsız olduğundan fark: (Σ log lam − Σ Lam295)_aday − (…)_taban.
    """
    def skor(n):
        o = pd.read_csv(DEFTER / f'{n}__{donem}__olay.csv.gz')
        g = pd.read_csv(DEFTER / f'{n}__{donem}__gun.csv.gz')
        return float(np.log(o['lam'].to_numpy(float)).sum() - g['Lam295'].sum()), len(o), len(g)
    s0, n0, g0 = skor(taban)
    cikti = {}
    for n in runs:
        if n == taban:
            continue
        s1, n1, g1 = skor(n)
        defter_fark = s1 - s0
        kosucu_fark = float(runs[n].logL - runs[taban].logL)
        tol = 1e-9 * max(1.0, abs(kosucu_fark))
        ok = bool(abs(defter_fark - kosucu_fark) <= tol and n1 == n0 and g1 == g0)
        cikti[n] = dict(taban=taban, defter_fark=defter_fark, kosucu_fark=kosucu_fark,
                        olay_sayisi=n1, gun_sayisi=g1, tamam=ok)
        if not ok:
            raise ValueError(f'Defter logL farkı koşucuyla eşleşmiyor: {n}/{taban}/{donem}')
    return cikti


def yon_ozeti(k, yon, met, bas, son, m_alt=5.0):
    """Dönemdeki M>=m_alt ebeveynler için a/b yönlerinin kullanılabilirliği (a = t+3 gün)."""
    from knotenlinie.etas_sonlu.wc94 import kirik_boyu_km
    t0, t1 = utc(bas), utc(son)
    idx = np.flatnonzero((k.zaman >= t0).to_numpy() & (k.zaman < t1).to_numpy()
                         & (k.mw >= m_alt).to_numpy())
    n = ya = yb = both = 0
    fark = []
    for j in idx:
        row = k.iloc[int(j)]
        a = (row.zaman + pd.Timedelta(days=3)).ceil('D')
        L = float(kirik_boyu_km(row.mw))
        da = yon.yon('a', k, int(j), a, met, L)
        db = yon.yon('b', k, int(j), a, met, L)
        n += 1
        ya += da is not None
        yb += db is not None
        if da is not None and db is not None:
            both += 1
            fark.append(abs(((da['dogrultu'] - db['dogrultu'] + 90) % 180) - 90))
    return dict(donem=[bas, son], M_alt=m_alt, ebeveyn=n, a_yon=ya, b_yon=yb, ikisi=both,
                a_b_dogrultu_farki_medyan_derece=float(np.median(fark)) if fark else None)


def _varyant_kur(taban, yon, pat):
    return SonluKaskad(taban, yon=yon, pat_cache=pat)


def secim_asamasi(raw, k, grid, edges, yon, pat):
    p = json.loads((DIZIN / 'etas_s_le2005.json').read_text())
    taban = DuzETAS(p, grid)
    temel = SonluKaskad(taban, yon=None, pat_cache=pat)
    varyantlar = {f'X-{tip}-{ms}': (_varyant_kur(taban, yon, pat), tip, ms)
                  for tip in YON_TIPLERI for ms in MS_LISTE}
    cat = katalog_oku(KATALOG)
    runs, gun_bins, hedef, ci, mi, gun_idx, ndays = coklu_kos(
        k, 'R-le2005', temel, varyantlar, SEL_BAS, SEL_SON, cat, grid, edges)
    return dict(p=p, runs=runs, gun_bins=gun_bins, hedef=hedef, ci=ci, mi=mi,
                gun_idx=gun_idx, ndays=ndays)


def secim_yap(secim):
    """En yüksek 2006-2010 M>=2,95 logL; beraberlikte R, sonra küçük M_s, sonra yol a."""
    tablo = {n: float(r.logL) for n, r in secim['runs'].items()}
    def anahtar(n):
        if not n.startswith('X-'):
            return (tablo[n], 1, 0.0, 0)
        tip, ms = n.rsplit('-', 2)[1], float(n.rsplit('-', 2)[2])
        return (tablo[n], 0, -ms, 1 if tip == 'a' else 0)
    secilen = max(tablo, key=anahtar)
    return tablo, secilen


def olcum_asamasi(raw, k, grid, edges, yon, pat, secilen):
    pat.clear()  # seçim modelleri başka D/gamma taşır; desen anahtarları modele bağlı değil
    p = json.loads((DIZIN / 'etas_ortak.json').read_text())
    taban = DuzETAS(p, grid)
    temel = SonluKaskad(taban, yon=None, pat_cache=pat)
    if secilen is None or secilen.startswith('R-'):
        varyantlar = {}
    else:
        tip, ms = secilen.rsplit('-', 2)[1], float(secilen.rsplit('-', 2)[2])
        varyantlar = {secilen: (_varyant_kur(taban, yon, pat), tip, ms)}
    cat = katalog_oku(KATALOG)
    runs, gun_bins, hedef, ci, mi, gun_idx, ndays = coklu_kos(
        k, 'R-ortak-kaskad', temel, varyantlar, OLC_BAS, OLC_SON, cat, grid, edges)
    lm = ETASLM(cat[cat.zaman < utc(OLC_BAS)], grid, adim=32, nesil=10)
    box = lm.met.kutu
    gecmis_k = katalog_kontrol(cat)
    gecmis_k = gecmis_k[(gecmis_k.boylam >= box[2]) & (gecmis_k.boylam < box[3]) &
                        (gecmis_k.enlem >= box[0]) & (gecmis_k.enlem < box[1]) &
                        (gecmis_k.derinlik >= 0) & (gecmis_k.derinlik <= 30)]
    lm_run, lm_bins = tek_kos(lm.beklenen, 'ETAS-LM', OLC_BAS, OLC_SON, cat, grid, edges, gecmis_k)
    runs['ETAS-LM'] = lm_run
    gun_bins['ETAS-LM'] = lm_bins
    return dict(p=p, runs=runs, gun_bins=gun_bins, hedef=hedef, ci=ci, mi=mi,
                gun_idx=gun_idx, ndays=ndays, lm=lm)


def holm_aile(satirlar):
    """Her taban için üç eşik üstünde tek Holm ailesi."""
    for ref in ('R-ortak-kaskad', 'ETAS-LM'):
        sec = [r for r in satirlar if r['taban'] == ref]
        for field in ('p_T', 'p_W'):
            for r, v in zip(sec, holm([r[field] for r in sec])):
                r[field + '_Holm3'] = v


def _veri_goreli(yol):
    """Data-root-relative string for a record (absolute if outside the data root)."""
    try:
        return str(Path(yol).resolve().relative_to(Path(VERI).resolve()))
    except ValueError:
        return str(yol)


def main():
    kayit_hazirla('X')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--asama', choices=('secim', 'olcum', 'hepsi'), default='hepsi')
    ap.add_argument('--cikti', type=Path, default=OUT / 'OLCUM.json')
    args = ap.parse_args()
    if not (KURAL).exists():
        raise ValueError('Hesaptan önce X/KURAL.md yazılmalı')
    OUT.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    grid = pd.read_csv(IZGARA)
    raw, paths, horus = kaynak_oku()
    gdf = G.oku(GCMT_YOL)
    yon = Yon(gdf)
    pat = {}
    edges = kenarlar()
    k = ebeveynler(raw, KUTU)
    print('kaynak', len(raw), 'gcmt', len(gdf), 'k', len(k), 'RSS', rss() / 1e9, flush=True)
    sonuc = dict(durum='PROVISIONAL; bağımsız skor-kodu incelemesi bekler; kör hüküm değil',
                 baslangic_secim=SEL_BAS, bitis_secim_haric=SEL_SON,
                 baslangic_olcum=OLC_BAS, bitis_olcum_haric=OLC_SON,
                 hucre=len(grid), m_kenarlar=[float(x) if np.isfinite(x) else '+inf' for x in edges],
                 M_s_liste=list(MS_LISTE), yollar=list(YON_TIPLERI), tohum=TOHUM,
                 IG_tanimi='blok_ozeti: gun kazanci = olay log-orani − gunluk integral farki; IG = toplam/N',
                 yon_kurali='a: GCMT (zaman +-60 s, <=50 km, merkez<gun basi); ilk gun artci uyumu, '
                            'artci yoksa ilk duzlem. b: <=L km, <=3 gun artci PCA, >=10 olay; yoksa izotrop.',
                 WC94='log10(RLD_km) = -2.44 + 0.59 Mw (WC94 Tablo 2A, butun turler)',
                 defter_dizini=str(DEFTER),
                 kaynak_SHA256={str(paths[0]): sha256(paths[0]), str(GCMT_YOL): sha256(GCMT_YOL),
                                str(KATALOG): sha256(KATALOG), str(IZGARA): sha256(IZGARA),
                                str(DIZIN / 'etas_s_le2005.json'): sha256(DIZIN / 'etas_s_le2005.json'),
                                str(DIZIN / 'etas_ortak.json'): sha256(DIZIN / 'etas_ortak.json')})
    if args.asama in ('secim', 'hepsi'):
        s = secim_asamasi(raw, k, grid, edges, yon, pat)
        tablo, secilen = secim_yap(s)
        defter_yaz('2006-2010', s['runs'], s['gun_bins'], s['hedef'], s['ci'], s['mi'],
                   s['ndays'], SEL_BAS, edges)
        sonuc['defter_dogrulama_2006_2010'] = defter_dogrula('2006-2010', s['runs'], 'R-le2005')
        met_k = M.yerel_metrik(KUTU)
        sonuc['yon_ozeti_2006_2010'] = yon_ozeti(k, yon, met_k, SEL_BAS, SEL_SON)
        sonuc['secim'] = dict(tablo=tablo, secilen=secilen,
                              kural='En yüksek 2006-2010 M>=2,95 logL; beraberlikte R, '
                                    'sonra küçük M_s, sonra yol a')
        sonuc['secim_satirlari'] = [
            satir_yap(n, 'R-le2005', '2006-2010', e, s['runs'], s['gun_bins'], s['hedef'],
                      s['gun_idx'], s['ndays'], grid, edges)
            for n in s['runs'] for e in (2.95, 3.95, 4.95)]
        json_yaz(OUT / 'SECIM.json', dict(parametreler=_veri_goreli(DIZIN / 'etas_s_le2005.json'),
                                          parametreler_olcum=_veri_goreli(DIZIN / 'etas_ortak.json'),
                                          gcmt=_veri_goreli(GCMT_YOL),
                                          tip=None if secilen.startswith('R-') else secilen.rsplit('-', 2)[1],
                                          m_s=None if secilen.startswith('R-') else float(secilen.rsplit('-', 2)[2]),
                                          secim_tablosu=tablo, kural_sha256=sha256(KURAL),
                                          secim_satirlari=sonuc['secim_satirlari'],
                                          defter_dogrulama_2006_2010=sonuc['defter_dogrulama_2006_2010'],
                                          yon_ozeti_2006_2010=sonuc['yon_ozeti_2006_2010']))
        print('SEÇİM', secilen, tablo, round(time.monotonic() - start, 1), flush=True)
    if args.asama == 'secim':
        return
    sec = json.loads((OUT / 'SECIM.json').read_text())
    if sec.get('kural_sha256') != sha256(KURAL):
        raise ValueError('KURAL.md değişmiş; seçim kaydı geçersiz')
    for anahtar in ('secim_satirlari', 'defter_dogrulama_2006_2010', 'yon_ozeti_2006_2010'):
        sonuc[anahtar] = sec[anahtar]
    sonuc['secim'] = dict(tablo=sec['secim_tablosu'], secilen=None if sec.get('tip') is None else
                          f"X-{sec['tip']}-{sec['m_s']}", kural_sha256=sec['kural_sha256'])
    secilen = None if sec.get('tip') is None else f"X-{sec['tip']}-{sec['m_s']}"
    o = olcum_asamasi(raw, k, grid, edges, yon, pat, secilen)
    defter_yaz('2011-2015', o['runs'], o['gun_bins'], o['hedef'], o['ci'], o['mi'],
               o['ndays'], OLC_BAS, edges)
    met = M.yerel_metrik(KUTU)
    aday = secilen if secilen and secilen in o['runs'] else 'R-ortak-kaskad'
    satirlar = []
    for esik in (2.95, 3.95, 4.95):
        for ref in ('R-ortak-kaskad', 'ETAS-LM'):
            if aday == ref:
                continue
            r = satir_yap(aday, ref, '2011-2015', esik, o['runs'], o['gun_bins'], o['hedef'],
                          o['gun_idx'], o['ndays'], grid, edges)
            if ref == 'R-ortak-kaskad':
                r['buyuk_ebeveyn_altkume'] = alt_kume_satiri(aday, ref, esik, o['runs'],
                                                             o['gun_bins'], o['hedef'], grid, edges, k, met)
            satirlar.append(r)
    holm_aile(satirlar)
    sonuc['defter_dogrulama_2011_2015'] = defter_dogrula('2011-2015', o['runs'], 'R-ortak-kaskad')
    sonuc['yon_ozeti_2011_2015'] = yon_ozeti(k, yon, met, OLC_BAS, OLC_SON)
    sonuc['olcum_satirlari'] = satirlar
    sonuc['secilen'] = secilen
    sonuc['ETAS_LM'] = o['lm'].metadata
    sonuc['duvar_saniye'] = time.monotonic() - start
    sonuc['rss_tepe_byte'] = rss()
    sonuc['python'] = sys.version
    sonuc['numpy'] = np.__version__
    sonuc['pandas'] = pd.__version__
    json_yaz(args.cikti, sonuc)
    print(args.cikti, 's=', round(sonuc['duvar_saniye'], 1), 'RSS=', rss() / 1e9, flush=True)


if __name__ == '__main__':
    main()
