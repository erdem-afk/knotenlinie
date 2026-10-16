"""Deney W sürücüsü: kısa süreli tamlık (STAI), J/R günlük çerçevesi.

Aşamalar (her biri tekrar başlatılabilir; biten koşular ``defter/W/_ham`` altından okunur):

* ``ayar``   — W-a ve W-b: ETAS+STAI birlikte MLE, ≤2005 (R: ``etas_s_le2005.json``).
* ``secim``  — R, W-a, W-b'yi 2006–2010'da (M≥2,95) koşar; beş adayın logL tablosu; seçim.
* ``olcum``  — seçileni ≤2010 ile yeniden kurar; 2011–2015'te W, R-ortak-kaskad, ETAS-LM
  koşar; W − R ve W − ETAS-LM (M≥2,95/3,95/4,95) ölçülür.

Hedef (ii) gerçek oran: W parametreleriyle R'nin kaskad tahmini. Hedef (i) gözlenecek
oran: (ii) × q̄(gün, kutu) (``etas_stai.arayuz.q_gunluk``). İkisi aynı koşudan türer.
"""
from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import gammaln

from knotenlinie.etas_lm.arayuz import ETASLM
from knotenlinie.etas_stai import ayar as stai_ayar
from knotenlinie.etas_stai.arayuz import q_gunluk
from knotenlinie.etas_uzun.arayuz import TamGecmis, UzunETAS
from knotenlinie.karsilastir.blok import blok_ozeti
from knotenlinie.karsilastir.kosucu import Model, kos, olay_kutulari, utc
from knotenlinie.karsilastir.ortak4 import gecmis_ayari, rss_byte, uzaklik_km
from knotenlinie.karsilastir.puan import tutarlilik
from knotenlinie.ortak_zemin.veri import VERI, json_yaz, katalog_oku, sha256
from knotenlinie.yollar import KAYIT, KOSU, kayit_hazirla

BAS_SEL, SON_SEL = '2006-01-01T00:00:00Z', '2011-01-01T00:00:00Z'
BAS, SON = '2011-01-01T00:00:00Z', '2016-01-01T00:00:00Z'
TOHUM = 20261005
EDGES = np.r_[np.round(np.arange(2.95, 9.0, 0.1), 2), np.inf]
ESIKLER = (2.95, 3.95, 4.95)
STAI_DIR = VERI / 'ortak/stai'
UZUN = VERI / 'ortak/uzun'
DEFTER = VERI / 'defter/W'
HAM = DEFTER / '_ham'
OUT = KOSU / 'W'   # frozen inputs are seeded from records/W/ by kayit_hazirla
KURAL = KAYIT / 'W' / 'KURAL.md'   # frozen rule, read only


# --- koşu kaydı --------------------------------------------------------------------------

class Kayit:
    """``beklenen`` çağrılarını sarar: gün×kutu toplamı ve (hücre,kutu) toplamlarını biriktirir.

    ``qlar``: ad -> (ngun, nkutu) matris ya da None (çarpan yok). Her çağrı bir gündür.
    """

    def __init__(self, fn, qlar=None):
        self.fn, self.qlar = fn, qlar or {'ii': None}
        self.gun = 0
        self.gunluk = []
        self.toplam = {}

    def __call__(self, a, b, gecmis, izgara, m_kenarlar):
        lam = self.fn(a, b, gecmis, izgara, m_kenarlar)
        self.gunluk.append(lam.sum(axis=0))
        for ad, q in self.qlar.items():
            x = lam if q is None else lam * q[self.gun][None, :]
            self.toplam[ad] = x.copy() if ad not in self.toplam else self.toplam[ad] + x
        self.gun += 1
        return lam


class Kosum:
    """Bir modelin bir dönemdeki koşusu; hedef (i) ve (ii) buradan türer."""

    def __init__(self, ad, bas, son, olaylar, lam, gunluk, gozlem, toplam, q, logL_kos):
        self.ad, self.bas, self.son = ad, bas, son
        self.olaylar, self.lam, self.gunluk = olaylar, np.asarray(lam, float), np.asarray(gunluk, float)
        self.gozlem, self.toplam, self.q, self.logL_kos = gozlem, toplam, q, logL_kos
        self.gun = ((olaylar.zaman - utc(bas)) / pd.Timedelta(days=1)).to_numpy(float).astype(int)
        self.hucre = olaylar['hucre'].to_numpy(int)
        self.kutu = olaylar['kutu'].to_numpy(int)

    def lam_olay(self, v):
        if v == 'i' and self.q is not None:
            return self.lam * self.q[self.gun, self.kutu]
        return self.lam

    def lam_gunluk(self, v):
        if v == 'i' and self.q is not None:
            return self.gunluk * self.q
        return self.gunluk


def kos_et(fn, ayarlar, bas, son, cat, grid, ad, q=None):
    kayit = Kayit(fn, {'ii': None, 'i': q} if q is not None else {'ii': None})
    run = kos([Model(ad, kayit, True, ayarlar)], bas, son, cat, grid, EDGES, bolge='italya', derinlik=(0, 30))[ad]
    ngun = int((utc(son) - utc(bas)) / pd.Timedelta(days=1))
    gunluk = np.asarray(kayit.gunluk, float)
    if gunluk.shape[0] != ngun:
        raise ValueError(f'{ad}: gün sayısı {gunluk.shape[0]} != {ngun}')
    ev, ci, mi = olay_kutulari(run.olaylar, grid, EDGES, (0, 30))
    if not ev.equals(run.olaylar.reset_index(drop=True)):
        raise ValueError('olay sırası kapısı')
    ev = ev.assign(hucre=ci, kutu=mi)
    return Kosum(ad, bas, son, ev, run.olay_oranlari, gunluk, run.gozlem, kayit.toplam, q, float(run.logL))


def ham_yaz(k, dizin=None):
    dizin = Path(dizin or HAM)
    dizin.mkdir(parents=True, exist_ok=True)
    tab = {f'toplam_{a}': x for a, x in k.toplam.items()}
    np.savez_compressed(dizin / f'{k.ad}__{k.bas[:4]}.npz', lam=k.lam, gunluk=k.gunluk, gozlem=k.gozlem,
                        q=np.empty(0) if k.q is None else k.q, logL_kos=k.logL_kos, **tab)
    k.olaylar.to_csv(dizin / f'{k.ad}__{k.bas[:4]}__olay.csv.gz', index=False, compression='gzip')


def ham_oku(ad, bas, son, dizin=None):
    dizin = Path(dizin or HAM)
    z = np.load(dizin / f'{ad}__{bas[:4]}.npz')
    ev = pd.read_csv(dizin / f'{ad}__{bas[:4]}__olay.csv.gz')
    ev['zaman'] = pd.to_datetime(ev['zaman'], utc=True, format='mixed')
    q = z['q'] if z['q'].size else None
    toplam = {k[7:]: z[k] for k in z.files if k.startswith('toplam_')}
    return Kosum(ad, bas, son, ev, z['lam'], z['gunluk'], z['gozlem'], toplam, q, float(z['logL_kos']))


# --- puanlama ---------------------------------------------------------------------------

def kutu_no(alt):
    return int(np.flatnonzero(np.isclose(EDGES[:-1], alt, rtol=0, atol=1e-10))[0])


def ozet(k, v, alt):
    """Bir koşu+hedef için eşik üstü N, Λ, logL ve günlük bileşenler."""
    j = kutu_no(alt)
    keep = k.kutu >= j
    lam = k.lam_olay(v)[keep]
    gun, hucre, kutu = k.gun[keep], k.hucre[keep], k.kutu[keep]
    kat = k.lam_gunluk(v)[:, j:].sum(axis=1)
    Lam = float(kat.sum())
    if not len(lam) or not np.isfinite(lam).all() or (lam <= 0).any():
        return dict(N=int(keep.sum()), Lambda=Lam, logL=-np.inf, lam=lam, gun=gun, kat=kat, keep=keep)
    _, n = np.unique(np.column_stack([gun, hucre, kutu]), axis=0, return_counts=True)
    ll = float(np.log(lam).sum() - Lam - gammaln(n + 1).sum())
    return dict(N=int(keep.sum()), Lambda=Lam, logL=ll, lam=lam, gun=gun, kat=kat, keep=keep)


def nsm(k, v, alt, tekrar):
    j = kutu_no(alt)
    return tutarlilik(k.toplam[v][:, j:], k.gozlem[:, j:], tekrar=tekrar, tohum=TOHUM)


def cift(ka, va, kb, vb, alt, ad, taban, tekrar=None):
    a, b = ozet(ka, va, alt), ozet(kb, vb, alt)
    if a['N'] != b['N'] or a['N'] == 0:
        return dict(aday=ad, taban=taban, M_alt=alt, N=a['N'], IG=None, durum='N eşleşmiyor/sıfır')
    if not (np.isfinite(a['logL']) and np.isfinite(b['logL'])):
        return dict(aday=ad, taban=taban, M_alt=alt, N=a['N'], IG=None, durum='sıfır oran')
    nd = a['kat'].shape[0]
    lr = np.log(a['lam']) - np.log(b['lam'])
    gunluk = np.bincount(a['gun'], weights=lr, minlength=nd) - (a['kat'] - b['kat'])
    gunler = pd.date_range(ka.bas, ka.son, freq='D', inclusive='left')
    blok = blok_ozeti(gunluk, np.bincount(a['gun'], minlength=nd), gunler, n=a['N'])
    row = dict(aday=ad, taban=taban, M_alt=float(alt), N=a['N'], Lambda_aday=a['Lambda'], Lambda_taban=b['Lambda'],
               IG=(a['logL'] - b['logL']) / a['N'], IG_olay=float(lr.sum() / a['N']),
               integral=-(a['Lambda'] - b['Lambda']) / a['N'], SE_blok=blok['SE_blok'], z=blok['z'],
               p_tek=blok['p_tek'], blok_sayisi=blok.get('blok_sayisi'), GA95=blok.get('GA95'),
               logL_aday=a['logL'], logL_taban=b['logL'])
    if tekrar:
        row['NSM_aday'] = nsm(ka, va, alt, tekrar)
        row['NSM_taban'] = nsm(kb, vb, alt, tekrar)
    return row


def dizi_bayragi(olaylar, raw):
    """Hedefin önceki 30 gün ve 50 km içinde M≥5 olayı var mı? (HORUS, kesin önceki zaman)."""
    p = raw[raw.mw >= 5.0].sort_values('zaman').reset_index(drop=True)
    if not len(p):
        return np.zeros(len(olaylar), bool)
    pz = p.zaman.dt.tz_convert('UTC').dt.tz_localize(None).to_numpy(dtype='datetime64[ns]')
    bayrak = np.zeros(len(olaylar), bool)
    for i, row in enumerate(olaylar.itertuples(index=False)):
        z = np.datetime64(row.zaman.tz_convert('UTC').tz_localize(None))
        stop = int(np.searchsorted(pz, z, side='left'))
        start = int(np.searchsorted(pz, z - np.timedelta64(30, 'D'), side='left'))
        if stop <= start:
            continue
        w = p.iloc[start:stop]
        d = uzaklik_km(row.enlem, row.boylam, w.enlem.to_numpy(float), w.boylam.to_numpy(float))
        bayrak[i] = bool((d <= 50).any())
    return bayrak


def dizi_ig(ka, va, kb, vb, alt, bayrak):
    """Dizi alt kümesinde olay log-oranı (integral dağıtılmaz) ve tamamlayıcısı."""
    a, b = ozet(ka, va, alt), ozet(kb, vb, alt)
    f = bayrak[a['keep']]
    lr = np.log(a['lam']) - np.log(b['lam'])
    out = dict(M_alt=float(alt), N_dizi=int(f.sum()), N_diger=int((~f).sum()))
    out['IG_olay_dizi'] = float(lr[f].mean()) if f.any() else None
    out['IG_olay_diger'] = float(lr[~f].mean()) if (~f).any() else None
    out['log_oran_toplam_dizi'] = float(lr[f].sum())
    out['log_oran_toplam_diger'] = float(lr[~f].sum())
    return out


# --- defter -----------------------------------------------------------------------------

def defter_yaz(k, v, donem, dizin=None):
    """Skor defteri: olay (M≥2,95 hedefler) ve gün dosyaları. ``lam`` hedef v'ye göre."""
    dizin = Path(dizin or DEFTER)
    dizin.mkdir(parents=True, exist_ok=True)
    ad = k.ad
    olay = pd.DataFrame(dict(
        zaman=k.olaylar.zaman.dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        enlem=k.olaylar.enlem.to_numpy(float), boylam=k.olaylar.boylam.to_numpy(float),
        mw=k.olaylar.mw.to_numpy(float), hucre=k.hucre, kutu=k.kutu,
        gun=k.olaylar.zaman.dt.strftime('%Y-%m-%d'), lam=k.lam_olay(v)))
    lg = k.lam_gunluk(v)
    gunler = [(utc(k.bas) + pd.Timedelta(days=d)).strftime('%Y-%m-%d') for d in range(lg.shape[0])]
    j395 = kutu_no(3.95)
    gun = pd.DataFrame(dict(gun=gunler, Lam295=lg.sum(axis=1), Lam395=lg[:, j395:].sum(axis=1)))
    olay.to_csv(dizin / f'{ad}__{donem}__olay.csv.gz', index=False, compression='gzip')
    gun.to_csv(dizin / f'{ad}__{donem}__gun.csv.gz', index=False, compression='gzip')
    return olay, gun


def defter_logL(olay, gun, alt=2.95):
    """Defterden logL (log n! dahil; koşucu ile aynı tanım)."""
    if alt == 2.95:
        top, keep = float(gun.Lam295.sum()), np.ones(len(olay), bool)
    else:
        top, keep = float(gun.Lam395.sum()), (olay.mw.to_numpy(float) >= alt - 1e-12) & (olay.kutu.to_numpy() >= kutu_no(3.95))
    o = olay[keep]
    n = o.groupby(['gun', 'hucre', 'kutu']).size().to_numpy(float)
    return float(np.log(o.lam.to_numpy(float)).sum() - top - gammaln(n + 1).sum())


# --- modeller ---------------------------------------------------------------------------

def model_yap(p, raw, grid, *, adim=32, nesil=10):
    taban = UzunETAS(p, grid, adim=adim, nesil=nesil)
    ayarlar = gecmis_ayari(taban, 'italya')
    ayarlar['derinlik_max'] = 30
    return TamGecmis(taban, raw).beklenen, ayarlar


def yukle(path):
    return json.loads(Path(path).read_text())


# --- aşamalar ---------------------------------------------------------------------------

def raw_oku(son_yil):
    from knotenlinie.karsilastir.gunluk_s import kaynak_oku
    return kaynak_oku(son_yil)[0]


def ayar(grid, raw, args, tur_listesi=('a', 'b'), yil=2005):
    STAI_DIR.mkdir(parents=True, exist_ok=True)
    out = {}
    for tur in tur_listesi:
        path = STAI_DIR / f'etas_stai_{tur}_le{yil}.json'
        if path.exists() and not args.yeniden:
            out[tur] = yukle(path)
            continue
        r_path = UZUN / ('etas_s_le2005.json' if yil == 2005 else 'etas_ortak.json')
        r_fit = yukle(r_path)
        son = SON_SEL if yil == 2005 else BAS
        theta0 = None
        if yil == 2010 and tur == 'b':
            onceki = STAI_DIR / 'etas_stai_b_le2005.json'
            theta0 = yukle(onceki).get('stai_theta') if onceki.exists() else None
        t0 = time.monotonic()
        fit, L = stai_ayar.kur(r_fit, raw, grid, son, tur, maksiter=args.maksiter, theta0=theta0)
        fit['KURAL_SHA256'] = sha256(KURAL)
        fit['R_kaynak'] = str(r_path)
        json_yaz(path, fit)
        out[tur] = fit
        print(f'{path.name}: theta={fit["stai_theta"]} logL={fit["logL"]:.2f} (R parametresinde {fit["W_logL_R_parametresinde"]:.2f}) '
              f'nit={fit["nit"]} n={fit["dallanma"]:.6f} s={time.monotonic() - t0:.0f} RSS={rss_byte() / 1e9:.2f}GB', flush=True)
        del L
        gc.collect()
    return out


def secim(grid, raw, cat, args):
    fits = ayar(grid, raw, args)
    HAM.mkdir(parents=True, exist_ok=True)
    koslar = {}
    r_fit = yukle(UZUN / 'etas_s_le2005.json')
    plan = [('R', r_fit, None)] + [(f'W-{t}', fits[t], t) for t in ('a', 'b')]
    for ad, p, tur in plan:
        dosya = HAM / f'{ad}__2006.npz'
        if dosya.exists():
            koslar[ad] = ham_oku(ad, BAS_SEL, SON_SEL)
            print(ad, '2006–2010 hazır (önceden)', flush=True)
            continue
        t0 = time.monotonic()
        q = q_gunluk(p, raw, EDGES, BAS_SEL, SON_SEL) if tur else None
        fn, ayarlar = model_yap(p, raw, grid, adim=args.adim, nesil=args.nesil)
        k = kos_et(fn, ayarlar, BAS_SEL, SON_SEL, cat, grid, ad, q)
        ham_yaz(k)
        koslar[ad] = k
        print(f'{ad} 2006–2010: N(≥2,95)={len(k.olaylar)} logL_kos={k.logL_kos:.3f} s={time.monotonic() - t0:.0f} '
              f'RSS={rss_byte() / 1e9:.2f}GB', flush=True)
        gc.collect()
    aday = [('R', 'R', 'ii'), ('W-a-i', 'W-a', 'i'), ('W-a-ii', 'W-a', 'ii'), ('W-b-i', 'W-b', 'i'), ('W-b-ii', 'W-b', 'ii')]
    tablo = []
    for ad, kn, v in aday:
        k = koslar[kn]
        r = {'aday': ad}
        for alt in ESIKLER[:2]:
            o = ozet(k, v, alt)
            r[f'N_{alt}'], r[f'Lambda_{alt}'], r[f'logL_{alt}'] = o['N'], o['Lambda'], o['logL']
        tablo.append(r)
        defter_yaz_ad(k, v, ad, '2006-2010')
    en_iyi = max(tablo, key=lambda r: (r['logL_2.95'], r['aday'] == 'R'))
    ref = next(r for r in tablo if r['aday'] == 'R')
    secilen = en_iyi['aday'] if en_iyi['logL_2.95'] > ref['logL_2.95'] else 'R'
    out = dict(durum='2006–2010 seçimi; 2011–2015 açılmadı', KURAL_SHA256=sha256(KURAL),
               baslangic=BAS_SEL, bitis_haric=SON_SEL, M_alt=2.95, tablo=tablo, secilen=secilen,
               kural='en büyük 2006–2010 M≥2,95 logL; eşitlikte R',
               fit_dosyalari={t: sha256(STAI_DIR / f'etas_stai_{t}_le2005.json') for t in ('a', 'b')},
               stai_theta={t: fits[t].get('stai_theta') for t in ('a', 'b')},
               parametre={t: fits[t]['parametreler'] for t in ('a', 'b')} | {'R': r_fit['parametreler']})
    json_yaz(OUT / 'SECIM.json', out)
    print('SEÇİM:', secilen, flush=True)
    for r in tablo:
        print(r, flush=True)
    return out


def defter_yaz_ad(k, v, ad, donem):
    kopya = Kosum(ad, k.bas, k.son, k.olaylar, k.lam, k.gunluk, k.gozlem, k.toplam, k.q, k.logL_kos)
    return defter_yaz(kopya, v, donem)


def w_kos(tur, grid, raw15, cat, args, koslar):
    """W-tur için ≤2010 yeniden kurulum + 2011–2015 koşusu (tek koşu; hedef i ve ii ondan türer)."""
    ad = f'W-{tur}'
    if (HAM / f'{ad}__2011.npz').exists():
        koslar[ad] = ham_oku(ad, BAS, SON)
        return
    t0 = time.monotonic()
    fits = ayar(grid, raw15, args, tur_listesi=(tur,), yil=2010)
    p = fits[tur]
    q = q_gunluk(p, raw15, EDGES, BAS, SON)
    fn, ayarlar = model_yap(p, raw15, grid, adim=args.adim, nesil=args.nesil)
    k = kos_et(fn, ayarlar, BAS, SON, cat, grid, ad, q)
    ham_yaz(k)
    koslar[ad] = k
    print(f'{ad} 2011–2015: N={len(k.olaylar)} logL_kos={k.logL_kos:.3f} s={time.monotonic() - t0:.0f}', flush=True)
    gc.collect()


def olcum(grid, raw15, cat, args):
    t00 = time.monotonic()
    sec = yukle(OUT / 'SECIM.json')
    if sec['KURAL_SHA256'] != sha256(KURAL):
        raise ValueError('KURAL SHA uyuşmuyor')
    secilen = sec['secilen']
    kesif = [x for x in args.kesif.split(',') if x]
    print('Seçilen:', secilen, ' keşif:', kesif, flush=True)
    HAM.mkdir(parents=True, exist_ok=True)
    koslar = {}
    if (HAM / 'R-ortak-kaskad__2011.npz').exists():
        koslar['R-ortak-kaskad'] = ham_oku('R-ortak-kaskad', BAS, SON)
    else:
        t0 = time.monotonic()
        fn, ayarlar = model_yap(yukle(UZUN / 'etas_ortak.json'), raw15, grid, adim=args.adim, nesil=args.nesil)
        k = kos_et(fn, ayarlar, BAS, SON, cat, grid, 'R-ortak-kaskad')
        ham_yaz(k)
        koslar['R-ortak-kaskad'] = k
        print(f'R-ortak-kaskad 2011–2015: N={len(k.olaylar)} logL_kos={k.logL_kos:.3f} s={time.monotonic() - t0:.0f}', flush=True)
        gc.collect()
    if (HAM / 'ETAS-LM__2011.npz').exists():
        koslar['ETAS-LM'] = ham_oku('ETAS-LM', BAS, SON)
    else:
        t0 = time.monotonic()
        lm = ETASLM(cat[cat.zaman < utc(BAS)], grid, adim=args.adim, nesil=args.nesil)
        box = lm.met.kutu
        ayarlar = dict(sinir=(box[2], box[3], box[0], box[1]), baslangic_yil=2005, derinlik_max=30)
        k = kos_et(lm.beklenen, ayarlar, BAS, SON, cat, grid, 'ETAS-LM')
        ham_yaz(k)
        koslar['ETAS-LM'] = k
        print(f'ETAS-LM 2011–2015: N={len(k.olaylar)} logL_kos={k.logL_kos:.3f} s={time.monotonic() - t0:.0f}', flush=True)
        del lm
        gc.collect()
    turler = []
    if secilen != 'R':
        turler.append(secilen.split('-')[1])
    turler += [x.split('-')[1] for x in kesif if x.split('-')[1] not in turler]
    for tur in turler:
        w_kos(tur, grid, raw15, cat, args, koslar)
    # puanlanacak adaylar: (ad, koşu, hedef, rol)
    adaylar = []
    if secilen == 'R':
        adaylar.append(('R-ortak-kaskad', 'R-ortak-kaskad', 'ii', 'secilen'))
    else:
        adaylar.append((secilen, f'W-{secilen.split("-")[1]}', secilen.split('-')[2], 'secilen'))
    for x in kesif:
        for v in ('i', 'ii'):
            ad = f'{x}-{v}'
            if ad != secilen:
                adaylar.append((ad, x, v, 'kesif'))
    # defterler
    defter_yaz_ad(koslar['R-ortak-kaskad'], 'ii', 'R-ortak-kaskad', '2011-2015')
    defter_yaz_ad(koslar['ETAS-LM'], 'ii', 'ETAS-LM', '2011-2015')
    for ad, kn, v, rol in adaylar:
        if kn != 'R-ortak-kaskad':
            defter_yaz_ad(koslar[kn], v, ad, '2011-2015')
    # N/S/M: model başına bir kez
    nsm_cache = {}

    def nsm_al(k, v, ad, alt):
        anahtar = (ad, alt)
        if anahtar not in nsm_cache:
            nsm_cache[anahtar] = nsm(k, v, alt, args.tekrar)
        return nsm_cache[anahtar]

    satirlar, dizi = [], []
    hedef_kos = koslar['R-ortak-kaskad']
    bayrak = dizi_bayragi(hedef_kos.olaylar, raw15)
    for ad, kn, v, rol in adaylar:
        for alt in ESIKLER:
            for taban in ('R-ortak-kaskad', 'ETAS-LM'):
                r = cift(koslar[kn], v, koslar[taban], 'ii', alt, ad, taban)
                r['rol'] = rol
                r['pencere'] = 'tam'
                r['dönem'] = '2011-2015'
                r['NSM_aday'] = nsm_al(koslar[kn], v, ad, alt)
                r['NSM_taban'] = nsm_al(koslar[taban], 'ii', taban, alt)
                satirlar.append(r)
                d = dizi_ig(koslar[kn], v, koslar[taban], 'ii', alt, bayrak)
                d.update(aday=ad, taban=taban, rol=rol)
                dizi.append(d)
    # her W adayının R'ye karşı toplam hedef-özet satırı (Λ/N)
    ozet_n = {ad: {str(alt): {k2: v2 for k2, v2 in ozet(koslar[kn], v, alt).items()
                              if k2 in ('N', 'Lambda', 'logL')} for alt in ESIKLER}
              for ad, kn, v, rol in adaylar}
    for ad in ('R-ortak-kaskad', 'ETAS-LM'):
        ozet_n[ad] = {str(alt): {k2: v2 for k2, v2 in ozet(koslar[ad], 'ii', alt).items()
                                 if k2 in ('N', 'Lambda', 'logL')} for alt in ESIKLER}
    wpar = {}
    for tur in turler:
        f = yukle(STAI_DIR / f'etas_stai_{tur}_le2010.json')
        wpar[f'W-{tur}'] = dict(parametreler=f['parametreler'], stai_theta=f.get('stai_theta'), logL=f['logL'],
                                R_logL=f['R_logL'], W_logL_R_parametresinde=f['W_logL_R_parametresinde'],
                                dallanma=f['dallanma'])
    out = dict(durum='PROVISIONAL; bağımsız skor-kodu incelemesi bekler', KURAL_SHA256=sec['KURAL_SHA256'],
               baslangic=BAS, bitis_haric=SON, derinlik=[0, 30], hucre=len(grid),
               M_kenarlar=[float(e) if np.isfinite(e) else '+inf' for e in EDGES], secilen=secilen,
               kesif_adaylari=kesif, satirlar=satirlar, dizi_alt_kume=dizi, ozet=ozet_n,
               dizi_N=int(bayrak.sum()), N_hedef=int(len(bayrak)), tekrar=args.tekrar, tohum=TOHUM,
               IG_tanimi='ortalama log(λ_aday/λ_taban) − (Λ_aday−Λ_taban)/N',
               blok_SE='UTC Pazartesi haftaları; (b/(b−1)) Σ(D_w−IG·N_w)²/N²; tek yönlü z',
               dizi_tanimi='hedefe göre kesin önceki M≥5 HORUS olayı ≤30 gün ve ≤50 km; integral dağıtılmaz',
               W_2010_kurulum=wpar, R_2010_parametre=yukle(UZUN / 'etas_ortak.json')['parametreler'],
               duvar_saniye=time.monotonic() - t00, rss_tepe_byte=rss_byte(), python=sys.version)
    json_yaz(OUT / 'OLCUM.json', out)
    print('OLCUM yazıldı', flush=True)
    return out


def main():
    kayit_hazirla('W')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--asama', choices=('ayar', 'secim', 'olcum'), required=True)
    ap.add_argument('--maksiter', type=int, default=150)
    ap.add_argument('--adim', type=int, default=32)
    ap.add_argument('--nesil', type=int, default=10)
    ap.add_argument('--tekrar', type=int, default=10000)
    ap.add_argument('--yeniden', action='store_true')
    ap.add_argument('--kesif', default='', help="seçim dışı, bilgi amaçlı W biçimleri: ör. 'W-a,W-b'")
    args = ap.parse_args()
    grid = pd.read_csv(VERI / 'ortak/italya_izgara.csv')
    cat = katalog_oku(VERI / 'ortak/italya_katalog_le2015.csv')
    if args.asama in ('ayar', 'secim'):
        raw = raw_oku(2010)
        if args.asama == 'ayar':
            ayar(grid, raw, args)
        else:
            secim(grid, raw, cat, args)
    else:
        raw15 = raw_oku(2015)
        olcum(grid, raw15, cat, args)


if __name__ == '__main__':
    main()
