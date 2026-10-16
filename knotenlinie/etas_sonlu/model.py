"""Sonlu kaynak kaskadı: R'nin uzaysal çekirdeği M>=M_s ebeveynlerde şeride yayılır.

R (`knotenlinie/etas_uzun/`) değiştirilmez; `KaskadETAS` burada genişletilir.
`temel` R'nin günlük hesabını birebir üretir, `duzeltme` yalnız büyük
ebeveynlerin doğrudan uzaysal satırını WC94 şeridi boyunca konvolüsyonla
değiştirir.  Horner özyinelemesi doğrusal olduğundan düzeltme de aynı
`gecis` operatöründen geçirilir; üretkenlik ve ETAS parametreleri değişmez.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import scipy.fft as SF
from scipy.signal import fftconvolve

from knotenlinie.etas import model as M
from knotenlinie.etas_uzun.arayuz import ebeveynler
from knotenlinie.kaskad.arayuz import KaskadETAS
from knotenlinie.kaskad.cekirdek import zaman_katsayilari
from knotenlinie.ortak_zemin.arayuz import DuzETAS, utc
from knotenlinie.ortak_zemin.veri import SON, izgara_dogrula, katalog_dogrula

from .wc94 import kirik_boyu_km
from .yon import Yon

DX = 0.1


def dugum_sayisi(L_km, D_km, *, ust=15):
    """Şerit düğüm sayısı: aralık ~D/2, tek sayı, [3, ust] içinde."""
    aralik = max(float(D_km) / 2.0, 0.5)
    n = int(np.ceil(float(L_km) / aralik) + 1)
    n = max(3, min(int(ust), n))
    if n % 2 == 0:
        n = min(int(ust), n + 1)
    if n % 2 == 0:
        n -= 1
    return int(n)


def serit_noktalari(merkez_lon, merkez_lat, dogrultu_deg, L_km, met, D_km):
    """Şerit düğümlerinin boylam/enlemi ve düğüm sayısı."""
    K = dugum_sayisi(L_km, D_km)
    r = np.linspace(-float(L_km) / 2.0, float(L_km) / 2.0, K)
    th = np.radians(float(dogrultu_deg))
    dlon = r * np.sin(th) / met.kx
    dlat = r * np.cos(th) / met.ky
    return np.asarray(merkez_lon, float) + dlon, np.asarray(merkez_lat, float) + dlat, K


class SonluKaskad(KaskadETAS):
    """KaskadETAS + büyük ebeveyn için şerit çekirdeği."""

    def __init__(self, taban, *, yon=None, adim=32, nesil=10, pat_cache=None):
        super().__init__(taban, adim=adim, nesil=nesil)
        xe, ye = M.hucre_kenarlari(self.taban.kutu, DX)
        self._ix = np.rint((self.g[:, 0] - xe[0]) / DX).astype(int)
        self._iy = np.rint((self.g[:, 2] - ye[0]) / DX).astype(int)
        if (self._ix < 0).any() or (self._iy < 0).any():
            raise ValueError('Hedef hücre ebeveyn kutusunda değil')
        if (self._ix >= len(xe) - 1).any() or (self._iy >= len(ye) - 1).any():
            raise ValueError('Hedef hücre ebeveyn kutusunda değil')
        self.yon = yon
        self._pat = {} if pat_cache is None else pat_cache

    def _fft_bilgi(self):
        if getattr(self, '_kfft', None) is None:
            n = (self.shape[0] + self.kernel.shape[0] - 1,
                 self.shape[1] + self.kernel.shape[1] - 1)
            self._full = n
            self._kfft = SF.rfft2(self.kernel, s=n)
            self._sy = (self.kernel.shape[0] - 1) // 2
            self._sx = (self.kernel.shape[1] - 1) // 2
        return self._full, self._kfft, self._sy, self._sx

    def _gecis_blok(self, blok):
        """İşaretli alan bloğu için kırpmasız, toplu kaskad geçişi ((V, C) -> (V, C))."""
        blok = np.atleast_2d(blok)
        full, kfft, sy, sx = self._fft_bilgi()
        ny, nx = self.shape
        field = np.zeros((blok.shape[0], ny, nx))
        field[:, self.iy, self.ix] = blok
        F = SF.rfft2(field, s=full, axes=(1, 2))
        conv = SF.irfft2(F * kfft[None], s=full, axes=(1, 2))
        out = conv[:, sy:sy + ny, sx:sx + nx][:, self.iy, self.ix]
        if not np.isfinite(out).all():
            raise ValueError('Sonlu düzeltmede sonlu olmayan FFT')
        return out

    def _gecis_isaretli(self, cell):
        return self._gecis_blok(np.asarray(cell)[None])[0]

    # --- R'nin günlük gövdesi (KaskadETAS.beklenen ile aynı) ----------------

    def temel(self, baslangic, bitis, gecmis, izgara, m_kenarlar):
        a, z = utc(baslangic), utc(bitis)
        if not self.taban.ayar_son <= a < z <= SON or z - a > pd.Timedelta(days=1):
            raise ValueError('Yalnız ayar sonrası ≤2015, en fazla bir gün')
        h = katalog_dogrula(gecmis)
        if (h.zaman >= a).any():
            raise ValueError('Geçmiş gün başından önce olmalı')
        g, _, _, _ = izgara_dogrula(izgara)
        try:
            idx = np.array([self.lookup[tuple(row)] for row in np.round(g, 9)], int)
        except KeyError as e:
            raise ValueError('Hedef donmuş destek dışında') from e
        edges = np.asarray(m_kenarlar, float)
        if (edges.ndim != 1 or len(edges) < 2 or not np.isfinite(edges[:-1]).all()
                or np.isnan(edges[-1]) or (np.diff(edges) <= 0).any() or edges[0] < self.mc):
            raise ValueError('Geçersiz büyüklük kutuları')
        h = h[(h.mw >= self.mc) & (h.zaman >= self.taban.baslangic)].reset_index(drop=True)
        age = ((a - h.zaman) / pd.Timedelta(days=1)).to_numpy(float)
        duration = float((z - a) / pd.Timedelta(days=1))
        coeff = zaman_katsayilari(age, h.mw.to_numpy(float), duration, self.taban.th,
                                  self.b, self.mc, self.adim, self.nesil)
        background = self.taban.th['mu'] * self.taban._arka_plan(self.g)
        spatial = None
        if len(h) and self.taban.th['K'] > 0:
            spatial = self.taban._mekan(h, self.g)
            raw = coeff[:, :-1] @ spatial
            raw += coeff[:, -1, None] * background[None, :]
        else:
            raw = coeff[:, -1, None] * background[None, :]
        cell = raw[-1].copy()
        for gen in range(len(raw) - 2, -1, -1):
            cell = raw[gen] + self.gecis(cell)
        if cell.sum() and self.nesil:
            self.max_last_ratio = max(self.max_last_ratio, float(raw[-1].sum()) / float(cell.sum()))
        mag = 10 ** (-self.b * (edges[:-1] - self.mc)) - 10 ** (-self.b * (edges[1:] - self.mc))
        out = cell[idx, None] * mag[None, :]
        if not np.isfinite(out).all() or (out < 0).any():
            raise ValueError('Geçersiz beklenen')
        ctx = dict(h=h, coeff=coeff, spatial=spatial, idx=idx, mag=mag, edges=edges, a=a, z=z)
        return out, ctx

    # --- şerit çekirdeği ---------------------------------------------------

    def _serpme(self, mw, yon, L, key):
        if key in self._pat:
            return self._pat[key]
        D_i = float(M.mekan_olcegi(self.taban.th['D'], self.taban.th['gamma'], [mw], self.mc)[0])
        lon, lat, K = serit_noktalari(yon['merkez_lon'], yon['merkez_lat'], yon['dogrultu'],
                                      L, self.taban.met, D_i)
        full = M.mekan_hucre_integralleri(lon, lat, np.full(K, D_i), self.taban.th['q'],
                                          self.taban.kutu, DX, metrik=self.taban.met, blok=K)
        row = np.asarray(full.mean(axis=0)[self._iy, self._ix], float)
        self._pat[key] = row
        return row

    def duzeltme_kaynak(self, ctx, tip, m_s):
        """Düzeltmenin kaynak alanı `draw` (nesil+1, C); None ise değişiklik yok."""
        if self.yon is None or ctx['spatial'] is None or self.taban.th['K'] <= 0:
            return None
        h = ctx['h']
        mw = h.mw.to_numpy(float)
        buyuk = np.flatnonzero(mw >= float(m_s))
        if not len(buyuk):
            return None
        spatial = ctx['spatial']
        delta = np.zeros((len(buyuk), spatial.shape[1]))
        for kk, j in enumerate(buyuk):
            L = float(kirik_boyu_km(mw[j]))
            a = ctx['a']
            t_p = h.iloc[j].zaman
            pencere = pd.Timedelta(days=1.0 if tip == 'a' else self.yon.artci_pencere_gun)
            gun_key = min(a, t_p + pencere)
            key = (h.iloc[j].zaman.value, round(float(h.iloc[j].boylam), 9),
                   round(float(h.iloc[j].enlem), 9), float(mw[j]), tip, gun_key.value)
            yon = self.yon.yon(tip, h, j, a, self.taban.met, L)
            if yon is None:
                continue
            delta[kk] = self._serpme(mw[j], yon, L, key) - spatial[j]
        if not np.any(delta):
            return None
        return ctx['coeff'][:, :-1][:, buyuk] @ delta

    def duzeltme_coklu(self, ctx, kaynaklar):
        """Birden çok varyantın kaynağını tek toplu Horner'da düzeltmeye çevirir."""
        aktif = [(i, d) for i, d in enumerate(kaynaklar) if d is not None]
        sonuc = [None] * len(kaynaklar)
        if not aktif:
            return sonuc
        stack = np.stack([d for _, d in aktif], axis=0)
        cell = stack[:, -1, :].copy()
        for gen in range(stack.shape[1] - 2, -1, -1):
            cell = stack[:, gen, :] + self._gecis_blok(cell)
        out = cell[:, ctx['idx'], None] * ctx['mag'][None, None, :]
        if not np.isfinite(out).all():
            raise ValueError('Geçersiz sonlu düzeltme')
        for k, (i, _) in enumerate(aktif):
            sonuc[i] = out[k]
        return sonuc

    def duzeltme(self, ctx, tip, m_s):
        """Büyük ebeveyn satırlarının şerit eksi izotrop farkı; None ise değişiklik yok."""
        return self.duzeltme_coklu(ctx, [self.duzeltme_kaynak(ctx, tip, m_s)])[0]


class SonluETAS:
    """Ortak `beklenen` imzası: R tabanı + seçilmiş (tip, M_s) sonlu düzeltme."""

    def __init__(self, parametreler, izgara, *, yon=None, tip='b', m_s=5.5, adim=32, nesil=10):
        self.taban = DuzETAS(parametreler, izgara)
        self.kaskad = SonluKaskad(self.taban, yon=yon, adim=adim, nesil=nesil)
        self.kutu = self.taban.kutu
        self.mc = self.taban.mc
        self.tip = tip
        self.m_s = float(m_s)
        self.metadata = dict(self.taban.p, sonlu=dict(tip=tip, m_s=float(m_s)))

    def beklenen(self, baslangic, bitis, gecmis, izgara, m_kenarlar):
        h = ebeveynler(gecmis, self.kutu)
        out, ctx = self.kaskad.temel(baslangic, bitis, h, izgara, m_kenarlar)
        d = self.kaskad.duzeltme(ctx, self.tip, self.m_s)
        return out if d is None else out + d
