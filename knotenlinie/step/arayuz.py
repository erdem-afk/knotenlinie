"""STEP tipi günlük model; ortak ``beklenen`` imzası.

Kaynaklar: genel + diziye özgü Reasenberg–Jones ve Akaike ağırlıklı birleştirme
Gerstenberger ve ark. (2005, Nature 435) ile Woessner ve ark. (2010, STEP-LG)
yöntemlerinden, bellekten ve kısaltılarak uyarlanmıştır; özgün STEP kodu ya da
Lolli–Gasperini (2003) tablosu bu çalışmada erişilemedi. Her bileşenin uyarlaması
``KURAL.md``'de yazılıdır.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from knotenlinie.karsilastir.puan import PuanHatasi

from .ayar import arka_hucre, arka_plan_kur, dizi_agirliklari, jenerik_kur
from .cekirdek import omori_integral
from .dizi import DiziIsleyici

EPOCH = pd.Timestamp('1985-01-01', tz='UTC')
MC = 3.1
IZGARA = ['boylam_min', 'boylam_max', 'enlem_min', 'enlem_max']


def utc(x):
    t = pd.Timestamp(x)
    if t.tzinfo is None:
        raise PuanHatasi('Zaman açıkça UTC taşımalı')
    return t.tz_convert('UTC')


def gun(t):
    return float((utc(t) - EPOCH) / pd.Timedelta(days=1))


class STEP:
    """Ayar: ``katalog_ayar`` (zaman < son). Tahmin: beklenen(a, z, gecmis, izgara, m_kenarlar)."""

    def __init__(self, katalog_ayar, izgara, *, son, mseq=4.0, n_min=8, n0=5.0, mc=MC,
                 mc_kaynak=None, kaynak_bas='2005-01-01', hiyerarsi=False, mm_kes=False):
        self.son = pd.Timestamp(son)
        self.son = self.son.tz_localize('UTC') if self.son.tzinfo is None else self.son.tz_convert('UTC')
        self.mseq, self.n_min, self.n0, self.mc = float(mseq), int(n_min), float(n0), float(mc)
        self.hiyerarsi = bool(hiyerarsi)
        self.mm_kes = bool(mm_kes)
        self.mc_kaynak = None if mc_kaynak is None else float(mc_kaynak)
        self.kaynak_bas = pd.Timestamp(kaynak_bas, tz='UTC')
        self.g = np.round(izgara[IZGARA].to_numpy(float), 12)
        self.kutu = (float(self.g[:, 2].min()), float(self.g[:, 3].max()),
                     float(self.g[:, 0].min()), float(self.g[:, 1].max()))
        k = self._suz(katalog_ayar)
        if len(k) and k.zaman.max() >= self.son:
            raise PuanHatasi('STEP ayar kataloğu ayar sonundan sonrasını içeriyor')
        isl = DiziIsleyici(self.mseq, self.mc, self.hiyerarsi)
        for t, lo, la, m in self._satirlar(k):
            isl.ekle(t, lo, la, m)
        t_son = gun(self.son)
        self.jen = jenerik_kur(isl.tum, t_son, self.mc)
        self.arka = arka_plan_kur(isl.arka, EPOCH, t_son, self.mc, self.kutu, self.son)
        self.bg_hucre = arka_hucre(self.arka['hist'], self.g)
        self.metadata = dict(
            ozgun_tahmin=False, mc_kaynak=self.mc_kaynak, hiyerarsi=self.hiyerarsi, mm_kes=self.mm_kes, mseq=self.mseq, n_min=self.n_min, n0=self.n0, mc=self.mc,
            ayar_son=self.son.isoformat(), genel_RJ={x: self.jen[x] for x in
                                                    ('a', 'b', 'p', 'c', 'logL', 'n_dizi', 'n_uye', 'yakinsadi')},
            arka_plan=dict(mu_gun=self.arka['mu_gun'], b=self.arka['b'], n=self.arka['n'],
                           bant_km=self.arka['hist']['bant_km'], zemin_payi=self.arka['hist']['zemin_payi']),
            ayar_olay_sayisi=len(k), derinlik_min=0, derinlik_max=30,
            derinlik_tanimi='[0,30) km')
        self._isl = None
        self._n = 0
        self._son_t = None

    # ---- veri ------------------------------------------------------------
    def _suz(self, kat):
        k = kat[['zaman', 'enlem', 'boylam', 'derinlik', 'mw']].copy()
        k['zaman'] = pd.to_datetime(k['zaman'], utc=True)
        la0, la1, lo0, lo1 = self.kutu
        esik = self.mc - 1e-9
        if self.mc_kaynak is not None:
            esik = np.where(k.zaman >= self.kaynak_bas, self.mc_kaynak - 1e-9, self.mc - 1e-9)
        m = ((k.zaman >= EPOCH) & (k.mw >= esik) & (k.derinlik >= 0) & (k.derinlik < 30) &
             (k.boylam >= lo0) & (k.boylam <= lo1) & (k.enlem >= la0) & (k.enlem <= la1))
        return k[m].sort_values('zaman', kind='stable').reset_index(drop=True)

    @staticmethod
    def _satirlar(k):
        t = ((k.zaman - EPOCH) / pd.Timedelta(days=1)).to_numpy(float)
        return zip(t, k.boylam.to_numpy(float), k.enlem.to_numpy(float), k.mw.to_numpy(float))

    # ---- tahmin ----------------------------------------------------------
    def beklenen(self, baslangic, bitis, gecmis, izgara, m_kenarlar):
        a, z = utc(baslangic), utc(bitis)
        if not a < z or a < self.son:
            raise PuanHatasi('STEP: tahmin ayar sonundan sonra ve artan olmalı')
        if not np.array_equal(np.round(izgara[IZGARA].to_numpy(float), 12), self.g):
            raise PuanHatasi('STEP: kurulum ızgarası uyuşmuyor')
        e = np.asarray(m_kenarlar, float)
        if e.ndim != 1 or len(e) < 2 or (np.diff(e) <= 0).any():
            raise PuanHatasi('STEP: büyüklük kenarları artan olmalı')
        h = self._suz(gecmis)
        if len(h) and h.zaman.iloc[-1] >= a:
            raise PuanHatasi('STEP: geçmiş gün başından önce olmalı')
        t = ((h.zaman - EPOCH) / pd.Timedelta(days=1)).to_numpy(float)
        if (self._isl is None or len(h) < self._n or
                (self._n and t[self._n - 1] != self._son_t)):
            self._isl, self._n, self._son_t = DiziIsleyici(self.mseq, self.mc, self.hiyerarsi), 0, None
        yeni = h.iloc[self._n:]
        for tt, lo, la, m in zip(t[self._n:], yeni.boylam.to_numpy(float),
                                 yeni.enlem.to_numpy(float), yeni.mw.to_numpy(float)):
            self._isl.ekle(tt, lo, la, m)
        if len(h):
            self._n, self._son_t = len(h), float(t[-1])
        d0 = gun(a)
        sure = float((z - a) / pd.Timedelta(days=1))
        isl = self._isl
        isl.temizle(d0)
        jen = self.jen
        b, c = jen['b'], jen['c']
        lo, hi = e[:-1], e[1:]
        ust = np.where(np.isinf(hi), 0.0, 10.0 ** (-b * hi))
        gs = 10.0 ** (-b * lo) - ust
        C = np.zeros(len(self.g))
        satir, gmat = [], []
        for s in isl.aktif:
            yas = d0 - s.t
            if yas < 0 or yas > s.tgk:
                continue
            son = min(yas + sure, s.tgk)
            A = 0.0
            for w, ak, pk in dizi_agirliklari(s, yas, jen, self.mc, self.n_min):
                if w > 0:
                    A += w * 10.0 ** (ak + b * s.m) * float(omori_integral(yas, son, c, pk))
            if A <= 0:
                continue
            n = len(s.uye_t)
            Km, S = isl.uzay(s, self.g)
            om = n / (n + self.n0)
            sp = Km if n == 0 else (1 - om) * Km + om * S / n
            if self.mm_kes:
                # artçılar ana şoktan küçüktür: [lo, hi) ∩ [., Mm) kesilir
                h2 = np.minimum(hi, s.m)
                g_s = np.where(lo < s.m, 10.0 ** (-b * lo) - 10.0 ** (-b * h2), 0.0)
                satir.append(A * sp)
                gmat.append(g_s)
            else:
                C += A * sp
        bb = self.arka['b']
        hb = 10.0 ** (-bb * (lo - self.mc)) - np.where(np.isinf(hi), 0.0, 10.0 ** (-bb * (hi - self.mc)))
        cell_bg = self.arka['mu_gun'] * sure * self.bg_hucre
        if self.mm_kes and satir:
            out = np.asarray(satir).T @ np.asarray(gmat) + cell_bg[:, None] * hb[None, :]
        else:
            out = C[:, None] * gs[None, :] + cell_bg[:, None] * hb[None, :]
        if not np.isfinite(out).all() or (out < 0).any():
            raise PuanHatasi('STEP: beklenen sonlu/negatif olmayan değil')
        return out
