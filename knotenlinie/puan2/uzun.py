"""Uzun vade (AH) yeniden okuma: AH kodundan olay/hücre λ'ları, bizim model − HAZFX/TripleS/MPS04 (İtalya)."""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from knotenlinie.karsilastir import uzun_ah as AHK
from knotenlinie.karsilastir import uzun_z
from knotenlinie.karsilastir.puan import eslestirilmis
from knotenlinie.karsilastir.puan import kosullu_test

from . import KANIT_DUZEYI
from .ikili import ikili_kosullu_test, ikili_logL
from .nbd import a_kestir, pencere_sayimlari
from .satir import hukum_eski, hukum_yeni, n_testleri, w_yan

TOHUM_S, TOHUM_SI = 20261005, 20261007
TEKRAR = 10000
TARIH0 = '1985-01-01'
TARIH1 = '2011-01-01'
PENCERE_GUN = 1826


def a_uzun(h, tur, k):
    """KURAL.md §1 (uzun vade): kümesiz/bütün katalog, M≥4,95, AH bölge kutusu ve derinliği."""
    frame = h['kumesiz'] if tur == 'kumesiz' else h['katalog']
    t0, t1 = uzun_z.utc(TARIH0), uzun_z.utc(TARIH1)
    ev, _, mi = uzun_z.hedefler(frame, h['izgara'], h['edges'], h['cfg']['derinlik'], t0, t1)
    ev = ev[np.asarray(mi) >= k]
    gun = ((ev.zaman - t0) / pd.Timedelta(days=1)).to_numpy(float)
    r = a_kestir(pencere_sayimlari(gun, 0.0, (t1 - t0) / pd.Timedelta(days=1), PENCERE_GUN, 30))
    r['olay'] = int(len(ev))
    return r


def satir(lam_a, lam_r, ci, mi, k, n_hucre, ad_a, ad_r, bolge, tur, a, bootstrap):
    sec = mi >= k
    ci_k = ci[sec]
    obs = np.bincount(ci_k, minlength=n_hucre)
    N = int(len(ci_k))
    La, Lr = float(lam_a.sum()), float(lam_r.sum())
    r = uzun_z.olay_ig(lam_a[ci_k], lam_r[ci_k], La, Lr, tekrar=bootstrap)
    out = dict(satir=f'{ad_a} - {ad_r}', aday=ad_a, taban=ad_r, esik=4.95, bolge=bolge, donem='2011-2015', hedef=tur,
               N=N, Lambda_aday=La, Lambda_taban=Lr, IG=r.get('IG'), IG_olay=r.get('IG_olay'),
               integral=r.get('integral'), SE_blok=r.get('SE_blok'), z_blok=r.get('z'),
               SE_HAC=None, z_HAC=None, kanit_duzeyi=KANIT_DUZEYI,
               not_='tek zaman penceresi: HAC tanımsız; SE_blok olay bootstrap (uzun_z.olay_ig)')
    if N >= 2 and (lam_a[ci_k] > 0).all() and (lam_r[ci_k] > 0).all():
        e = eslestirilmis(lam_a[ci_k], lam_r[ci_k], La, Lr)
        wy = w_yan(lam_a[ci_k], lam_r[ci_k], La, Lr)
        wnot = wy.pop('not_', None)
        if wnot:
            out['not_'] = out['not_'] + '; ' + wnot
        out.update(T=e['T'], p_T=e['p_T'], W=e['W'], p_W=e['p_W'], **wy)
    else:
        out.update(T=None, p_T=None, W=None, p_W=None, p_W_tam=None, bag_var=None, p_W_perm=None)
    out['eski_hukum'] = hukum_eski(out['IG'], out['z_blok'])
    # KURAL §5 + Ek 1: N kuralı (N<30 → asimptotik p_W, aksi p_T); HAC tanımsız, şart değil.
    out['yeni_hukum'] = hukum_yeni(out['IG'], out['z_blok'], None, out['p_T'], out['p_W'], N, hac_gerekli=False)
    # ikili: hücre-bazlı tek pencere (pyCSEP protokolü ile aynı; tam fark)
    lna, lnt = ikili_logL(lam_a, obs), ikili_logL(lam_r, obs)
    out.update(lnL_ikili_aday=lna, lnL_ikili_taban=lnt,
               IG_ikili=(lna - lnt) / N if N and np.isfinite(lna) and np.isfinite(lnt) else None)
    t = n_testleri(La, N, a['a'])
    out['tutarlilik_aday'] = dict(
        **t, Lambda=La,
        S_Poisson=kosullu_test(lam_a, obs, tekrar=TEKRAR, tohum=TOHUM_S),
        S_ikili=ikili_kosullu_test(lam_a, obs, tekrar=TEKRAR, tohum=TOHUM_SI),
        N_NBD_a_x0_5=n_testleri(La, N, a['a'] * 0.5)['N_NBD'], N_NBD_a_x2=n_testleri(La, N, a['a'] * 2)['N_NBD'])
    out['a'] = a
    return out


def olc(bootstrap=2000, ilerleme=print):
    z = json.loads((uzun_z.Z_DIR / 'OLCUM.json').read_text(encoding='utf-8'))
    secim = json.loads((AHK.AH_KAYIT / 'SECIM.json').read_text(encoding='utf-8'))
    ad_sec = secim['secili']
    v = {x[0]: x for x in AHK.VARYANTLAR}
    satirlar = []
    for bolge in ('italya',):
        h = AHK.hazirla(bolge, 'ayar2010', z['bolgeler'][bolge]['secim'])
        model = AHK.model_kur(h, v[ad_sec][1], v[ad_sec][2], ad='AH-' + ad_sec)
        a = AHK.AYARLAR['ayar2010']
        t0, t1 = uzun_z.utc(a['t0']), uzun_z.utc(a['t1'])
        edges, izgara = h['edges'], h['izgara']
        k = int(np.searchsorted(edges, 4.95, side='right') - 1)
        n = len(izgara)
        lam_a = model.beklenen(t0, t1, None, izgara, edges)[:, k:].sum(axis=1)
        ref = {}
        for ad, yol in h['cfg']['tabanlar']:
            tb = uzun_z.taban_yukle(ad, yol)
            ref[ad] = tb.beklenen(t0, t1, None, izgara, tb.m_kenarlar).sum(axis=1)
        for tur in ('kumesiz', 'tum'):
            _, ci, mi = AHK.hedef(h, tur)
            aa = a_uzun(h, tur, k)
            ilerleme(bolge, tur, 'a=%.4f m=%.2f vmr=%.2f olay=%d' % (aa['a'], aa['ortalama'], aa.get('vmr', 0), aa['olay']))
            for rad, lam_r in ref.items():
                if rad == 'Z2':
                    continue
                satirlar.append(satir(lam_a, lam_r, ci, mi, k, n, 'AH-' + ad_sec, rad, bolge, tur, aa, bootstrap))
    return dict(satirlar=satirlar)
