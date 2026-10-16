"""İtalya günlük 2011–2015 yeniden okuma: defterlerden, model koşmadan."""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd

from knotenlinie.karsilastir.puan import kosullu_test
from knotenlinie.ortak_zemin.veri import VERI, katalog_oku
from knotenlinie.skor_defteri import karisim as K
from knotenlinie.skor_defteri.defter import KOK, alt_indeks, defter_oku

from . import KANIT_DUZEYI
from .ikili import ikili_kosullu_test
from .nbd import a_kestir, pencere_sayimlari
from .satir import ikili_ig, kazanc_satiri, n_testleri

ESIKLER = (2.95, 3.95, 4.95)
TEKRAR = 10000
TOHUM_S, TOHUM_M, TOHUM_SI, TOHUM_LI = 20261005, 20261006, 20261007, 20261008
PENCERE_GUN = 1826  # 2011-01-01 .. 2016-01-01
TARIH0 = pd.Timestamp('1985-01-01', tz='UTC')
TARIH1 = pd.Timestamp('2011-01-01', tz='UTC')
U, AJ_D = KOK / 'U', KOK / 'AJ'
R_AD, LM_AD, AJ_AD = 'R-ortak-kaskad', 'ETAS-LM', 'AJ'


def a_italya(alt, katalog=None, izgara=None):
    """KURAL.md §1: eşik başına a; ≤2010 HORUS, CSEP İtalya ızgarası, [0,30) km."""
    from knotenlinie.karsilastir.kosucu import olay_kutulari
    kat = katalog_oku(VERI / 'ortak/italya_katalog_le2015.csv') if katalog is None else katalog
    izg = pd.read_csv(VERI / 'ortak/italya_izgara.csv') if izgara is None else izgara
    kat = kat[(kat.zaman >= TARIH0) & (kat.zaman < TARIH1)]
    kenar = np.r_[np.round(2.95 + 0.1 * np.arange(61), 2), np.inf]
    ev, _, _ = olay_kutulari(kat, izg, kenar, (0.0, 30.0))
    ev = ev[ev.mw >= alt - 1e-9]
    gun = ((ev.zaman - TARIH0) / pd.Timedelta(days=1)).to_numpy(float)
    toplam_gun = (TARIH1 - TARIH0) / pd.Timedelta(days=1)
    sayim = pencere_sayimlari(gun, 0.0, toplam_gun, PENCERE_GUN, 30)
    r = a_kestir(sayim)
    r['olay'] = int(len(ev))
    r['esik'] = alt
    return r


class Model:
    """Bir aday/taban: defter listesi + ağırlık → olay λ, Λ, marjinal."""

    def __init__(self, ad, defterler, agirlik, marjinaller):
        self.ad, self.defterler, self.agirlik, self.marj = ad, list(defterler), list(agirlik), marjinaller

    def beklenen(self, alt):
        j = alt_indeks(alt)
        return sum(w * m['beklenen'][:, j:] for w, m in zip(self.agirlik, self.marj))

    def gozlem(self, alt):
        return self.marj[0]['gozlem'][:, alt_indeks(alt):]


def _marj(dizin, ad):
    z = np.load(dizin / f'{ad}__2011-2015__marjinal.npz')
    return dict(beklenen=z['beklenen'], gozlem=z['gozlem'], logL=float(z['logL'][0]))


def yukle():
    d = {R_AD: defter_oku(R_AD, U), LM_AD: defter_oku(LM_AD, U), AJ_AD: defter_oku(AJ_AD, AJ_D)}
    m = {R_AD: _marj(U, R_AD), LM_AD: _marj(U, LM_AD), AJ_AD: _marj(AJ_D, AJ_AD)}
    return d, m


def model_tablo(d, m):
    M = {}
    M['R'] = Model('R', [d[R_AD]], [1.0], [m[R_AD]])
    M['LM'] = Model('LM', [d[LM_AD]], [1.0], [m[LM_AD]])
    M['AJ'] = Model('AJ', [d[AJ_AD]], [1.0], [m[AJ_AD]])
    M['T1-esit'] = Model('T1-esit', [d[R_AD], d[LM_AD]], [.5, .5], [m[R_AD], m[LM_AD]])
    M['E7'] = Model('E7', [d[AJ_AD], d[LM_AD]], [.5, .5], [m[AJ_AD], m[LM_AD]])
    return M


def tutarlilik_modeli(model, alt, a, *, tekrar=TEKRAR):
    """Bir modelin bir eşikteki N (Poisson, NBD), S, M ve ikili S/L testleri."""
    lam, gz = model.beklenen(alt), model.gozlem(alt)
    N = int(gz.sum())
    out = n_testleri(float(lam.sum()), N, a)
    out['Lambda'] = float(lam.sum())
    out['S_Poisson'] = kosullu_test(lam.sum(axis=1), gz.sum(axis=1), tekrar=tekrar, tohum=TOHUM_S)
    out['M_Poisson'] = kosullu_test(lam.sum(axis=0), gz.sum(axis=0), tekrar=tekrar, tohum=TOHUM_M)
    out['S_ikili'] = ikili_kosullu_test(lam.sum(axis=1), gz.sum(axis=1), tekrar=tekrar, tohum=TOHUM_SI)
    out['L_ikili'] = ikili_kosullu_test(lam, gz, tekrar=tekrar, tohum=TOHUM_LI)
    return out


SATIRLAR = [('R', 'LM'), ('AJ', 'LM'), ('T1-esit', 'LM'), ('E7', 'LM')]


def olc(tekrar=TEKRAR, ilerleme=print):
    d, m = yukle()
    M = model_tablo(d, m)
    a_esik = {alt: a_italya(alt) for alt in ESIKLER}
    ilerleme('a:', {k: round(v['a'], 4) for k, v in a_esik.items()})
    tut = {}
    satirlar = []
    for alt in ESIKLER:
        for ad_a, ad_t in SATIRLAR:
            ma, mt = M[ad_a], M[ad_t]
            k = K.gun_kazanci(ma.defterler, mt.defterler[0], alt, ma.agirlik)
            lam_o, _, mask = K.bilesen(ma.defterler, ma.agirlik, alt)
            r = kazanc_satiri(k, lam_o[mask], mt.defterler[0].lam()[mask], None, None)
            r.update(satir=f'{ad_a} - {ad_t}', aday=ad_a, taban=ad_t, esik=alt, bolge='italya', donem='2011-2015')
            r.update(ikili_ig(ma.defterler, ma.agirlik, mt.defterler[0], alt))
            for ad in (ad_a, ad_t):
                if (ad, alt) not in tut:
                    t0 = time.monotonic()
                    tut[(ad, alt)] = tutarlilik_modeli(M[ad], alt, a_esik[alt]['a'], tekrar=tekrar)
                    # duyarlılık: a×0.5 ve a×2 (hükme girmez)
                    for c in (0.5, 2.0):
                        tut[(ad, alt)][f'N_NBD_a_x{c}'] = n_testleri(
                            tut[(ad, alt)]['Lambda'], int(M[ad].gozlem(alt).sum()), a_esik[alt]['a'] * c)['N_NBD']
                    ilerleme(f'  tutarlılık {ad} {alt}: {time.monotonic() - t0:.0f} s')
            r['tutarlilik_aday'] = tut[(ad_a, alt)]
            r['tutarlilik_taban'] = tut[(ad_t, alt)]
            satirlar.append(r)
    return dict(satirlar=satirlar, a=a_esik)
