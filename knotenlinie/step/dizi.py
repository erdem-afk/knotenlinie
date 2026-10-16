"""Nedensel dizi ataması ve dizi başına uzay vektörleri.

Kural (KURAL.md): M>=Mc olaylar zaman sırasıyla işlenir. Olay e, kendisinden kesin
büyük, Gardner–Knopoff zaman ve uzay penceresi içinde bir ana şokun dizisine
atanır (birden çok aday varsa en büyük ana şok). Atanamayan ve M>=Mseq olan olay
yeni ana şoktur; atanamayan her olay (ana şoklar dahil) "arka plan" olayıdır
(atanmış artçılar dışındaki bildirim = ayıklanmış katalog). Yalnız geçmişe bakar.
"""
from __future__ import annotations

import numpy as np

from .cekirdek import (cekirdek_olcegi, gk_sure, gk_yaricap, hucre_kutlesi,
                       uzaklik_km)


class Dizi:
    __slots__ = ('id', 't', 'boylam', 'enlem', 'm', 'tgk', 'rgk', 'uye_t', 'uye_m',
                 'uye_lon', 'uye_lat', 'Km', 'S', 'uzay_n', 'son_a')

    def __init__(self, i, t, boylam, enlem, m):
        self.id = i
        self.t, self.boylam, self.enlem, self.m = t, boylam, enlem, m
        self.tgk = float(gk_sure(m))
        self.rgk = float(gk_yaricap(m))
        self.uye_t, self.uye_m, self.uye_lon, self.uye_lat = [], [], [], []
        self.Km = None
        self.S = None
        self.uzay_n = 0


class DiziIsleyici:
    def __init__(self, mseq, mc_arka=0.0, hiyerarsi=False):
        self.mseq = float(mseq)
        self.hiyerarsi = bool(hiyerarsi)
        self.mc_arka = float(mc_arka)
        self.aktif = []
        self.tum = []
        self.arka = []          # (t, boylam, enlem, m) atanamayan küçük olaylar
        self.n = 0
        self._son = None

    def temizle(self, t):
        """Penceresi dolan dizilerin uzay vektörlerini serbest bırakır."""
        kalan = []
        for s in self.aktif:
            if t - s.t <= s.tgk:
                kalan.append(s)
            else:
                s.Km = s.S = None
        self.aktif = kalan

    def ekle(self, t, boylam, enlem, m):
        self.temizle(t)
        en = None
        for s in self.aktif:
            if s.m > m and 0.0 <= t - s.t <= s.tgk:
                if en is not None:
                    # varsayılan: en büyük ana şok; hiyerarşi: en yakın (en küçük) ebeveyn
                    if (s.m >= en.m) if self.hiyerarsi else (s.m <= en.m):
                        continue
                if uzaklik_km(s.enlem, s.boylam, enlem, boylam) <= s.rgk:
                    en = s
        self.n += 1
        self._son = (t, boylam, enlem, m)
        if en is not None:
            en.uye_t.append(t - en.t)
            en.uye_m.append(m)
            en.uye_lon.append(boylam)
            en.uye_lat.append(enlem)
            if not (self.hiyerarsi and m >= self.mseq):
                return en
        if m >= self.mseq:
            s = Dizi(len(self.tum), t, boylam, enlem, m)
            self.tum.append(s)
            self.aktif.append(s)
            if en is None and m >= self.mc_arka - 1e-9:
                self.arka.append((t, boylam, enlem, m))
            return s
        if m >= self.mc_arka - 1e-9:
            self.arka.append((t, boylam, enlem, m))
        return None

    def uzay(self, s, izgara_dizi):
        """Dizinin ana şok çekirdeği ve üye-bulutu toplamı (tembel, artımlı)."""
        if s.Km is None:
            d = float(cekirdek_olcegi(s.m))
            s.Km = hucre_kutlesi(izgara_dizi, s.boylam, s.enlem, d, 2.0 * s.rgk)
            s.S = np.zeros(len(izgara_dizi))
            s.uzay_n = 0
        while s.uzay_n < len(s.uye_t):
            j = s.uzay_n
            mj = s.uye_m[j]
            d = float(cekirdek_olcegi(mj))
            s.S += hucre_kutlesi(izgara_dizi, s.uye_lon[j], s.uye_lat[j], d,
                                 2.0 * float(gk_yaricap(mj)))
            s.uzay_n += 1
        return s.Km, s.S
