"""Deney AG: sonlu kaynak çekirdeği (X-b-5,5) yan tezgâhın D1 modeline eklenir.

Deney X'in (`knotenlinie/etas_sonlu/`) İtalya'da seçilmiş biçimi: M >= M_s ebeveynin
doğrudan uzaysal çekirdeği, ebeveynin gün başından önceki artçılarının temel
bileşen ekseni boyunca (en az 10 olay, <=3 gün, <=L km) Wells–Coppersmith 1994
boyunda bir şeride yayılır; yalnız uzaysal dağılım değişir, üretkenlik (K, α, c, p)
ve zaman çekirdeği değişmez. Doğrultu bulunamazsa ebeveyn izotrop kalır.

Tezgâh kesmesi ile tutarlılık: şeridin her düğüm çekirdeği, tabanın izotrop
çekirdeğiyle aynı ``R <= rmax`` kırpmasından (düğümden ölçülür) geçer, kırpılmış
çekirdek yeniden normalize edilmez; zaman kesmesi (``tmax``) taban gibi uygulanır.
D1 parametreleri aynen alınır (yeniden MLE yok).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from knotenlinie.etas import model as M
from knotenlinie.etas_sonlu.model import serit_noktalari
from knotenlinie.etas_sonlu.wc94 import kirik_boyu_km
from knotenlinie.etas_sonlu.yon import Yon

from . import kesme as K
from .model import GUN, YanModel, _hizli_dogrula, _utc


def serit_integrali(lon_dugum, lat_dugum, D_km, q, kutu_alt, dx, met, rmax_km=None):
    """Düğüm çekirdeklerinin hücre integrallerinin ortalaması: (nla, nlo)."""
    tam = K.kesik_hucre_integralleri(lon_dugum, lat_dugum, np.full(len(lon_dugum), float(D_km)),
                                     q, kutu_alt, dx, metrik=met, blok=len(lon_dugum),
                                     rmax_km=rmax_km)
    return tam.mean(axis=0)


class SonluYan:
    """D1 (ya da başka bir `YanModel`) üstüne X-b-M_s düzeltmesi; ortak `beklenen` imzası.

    Taban önbelleği paylaşılır: düzeltme = Σ_j w_j (şerit_j − izotrop_j), w_j üretkenlik
    × Omori ağırlığı (tabanla aynı). Büyük ebeveyn yoksa ya da doğrultu bulunamazsa
    çıktı tabanla bit düzeyinde aynıdır.
    """

    def __init__(self, taban: YanModel, *, m_s=5.5, artci_pencere_gun=3.0, artci_min=10,
                 ad='X'):
        self.taban = taban
        self.ad = ad
        self.m_s = float(m_s)
        self.yon = Yon(None, artci_pencere_gun=artci_pencere_gun, artci_min=artci_min)
        self._serit = {}
        self._hid = None
        self._hid_key = None
        self.metadata = dict(taban.metadata, sonlu=dict(tip='b', m_s=self.m_s,
                                                        artci_pencere_gun=float(artci_pencere_gun),
                                                        artci_min=int(artci_min)))
        self.kayit = {}  # ebeveyn anahtarı -> (zaman, mw, doğrultu, artçı sayısı)

    def _sifirla_onbellek(self):
        self.taban._sifirla_onbellek()
        self._serit = {}

    def _hucre_kimligi(self, grid):
        key = grid[['boylam_min', 'boylam_max', 'enlem_min', 'enlem_max']].to_numpy(float).tobytes()
        if key != self._hid_key:
            m = self.taban
            xe, ye = M.hucre_kenarlari(m.kutu, m.dx)
            ix = np.rint((grid.boylam_min.to_numpy(float) - xe[0]) / m.dx).astype(int)
            iy = np.rint((grid.enlem_min.to_numpy(float) - ye[0]) / m.dx).astype(int)
            hid = np.full((len(ye) - 1, len(xe) - 1), -1, np.int64)
            hid[iy, ix] = np.arange(len(grid))
            self._hid, self._hid_key = hid, key
        return self._hid

    def _kutu(self, lon, lat, ekstra_km, xe, ye):
        m = self.taban
        nla, nlo = len(ye) - 1, len(xe) - 1
        if m.rmax_km is None:
            return 0, nla, 0, nlo
        r = m.rmax_km + ekstra_km
        dla = r / 100.0 + m.dx
        dlo = r / (100.0 * np.cos(np.radians(min(89.0, abs(lat) + dla)))) + m.dx
        ix0 = int(np.searchsorted(xe, lon - dlo, side='right')) - 1
        ix1 = int(np.searchsorted(xe, lon + dlo, side='left'))
        iy0 = int(np.searchsorted(ye, lat - dla, side='right')) - 1
        iy1 = int(np.searchsorted(ye, lat + dla, side='left'))
        return max(iy0, 0), min(iy1, nla), max(ix0, 0), min(ix1, nlo)

    def _delta(self, history, j, a, grid, key):
        """Ebeveyn j için (hücre indeksleri, şerit − izotrop) ya da None (izotrop)."""
        if key in self._serit:
            return self._serit[key]
        m = self.taban
        mw = float(history.mw.iloc[j])
        L = float(kirik_boyu_km(mw))
        yon = self.yon.yon('b', history, j, a, m._mekan_met, L)
        if yon is None:
            self._serit[key] = None
            return None
        D_i = float(M.mekan_olcegi(m.th['D'], m.th['gamma'], [mw], m.mc0)[0])
        lon, lat, _ = serit_noktalari(yon['merkez_lon'], yon['merkez_lat'], yon['dogrultu'],
                                      L, m._mekan_met, D_i)
        xe, ye = M.hucre_kenarlari(m.kutu, m.dx)
        iy0, iy1, ix0, ix1 = self._kutu(yon['merkez_lon'], yon['merkez_lat'], L / 2.0 + 1.0, xe, ye)
        hid = self._hucre_kimligi(grid)
        den = np.zeros(len(grid))
        if iy1 > iy0 and ix1 > ix0:
            alt = (ye[iy0], ye[iy1], xe[ix0], xe[ix1])
            sat = serit_integrali(lon, lat, D_i, m.th['q'], alt, m.dx, m._mekan_met, m.rmax_km)
            rows = hid[iy0:iy1, ix0:ix1]
            tut = (rows >= 0) & (sat > 1e-12)
            den[rows[tut]] = sat[tut]
        ip = m._ip
        iso = np.zeros(len(grid))
        iso[m._fi[ip[j]:ip[j + 1]]] = m._fv[ip[j]:ip[j + 1]]
        d = den - iso
        nz = np.flatnonzero(d)
        sonuc = (nz, d[nz], dict(dogrultu=float(yon['dogrultu']), artci_n=int(yon['artci_n']), mw=mw))
        self._serit[key] = sonuc
        return sonuc

    def duzeltme_hucre(self, history, age, w, a, grid):
        """Hücre başına düzeltme vektörü (tabanın `cell` toplamına eklenir)."""
        m = self.taban
        mw = history.mw.to_numpy(float)
        sec = mw >= self.m_s - 1e-9
        if m.tmax_gun is not None:
            sec &= age < m.tmax_gun
        d_cell = np.zeros(len(grid))
        pen = pd.Timedelta(days=self.yon.artci_pencere_gun)
        for j in np.flatnonzero(sec):
            t_p = history.zaman.iloc[j]
            gun_anahtar = min(a, t_p + pen)
            key = (t_p.value, round(float(history.boylam.iloc[j]), 9),
                   round(float(history.enlem.iloc[j]), 9), float(mw[j]), gun_anahtar.value)
            r = self._delta(history, j, a, grid, key)
            if r is None:
                continue
            d_cell[r[0]] += w[j] * r[1]
            self.kayit[key] = (str(t_p), float(mw[j]), r[2]['dogrultu'], r[2]['artci_n'])
        return d_cell

    def beklenen(self, baslangic, bitis, gecmis, izgara, m_kenarlar):
        m = self.taban
        out = m.beklenen(baslangic, bitis, gecmis, izgara, m_kenarlar)
        a, z = _utc(baslangic), _utc(bitis)
        if not len(gecmis) or m.th['K'] <= 0:
            return out
        grid = izgara[['boylam_min', 'boylam_max', 'enlem_min', 'enlem_max']].reset_index(drop=True)
        history = _hizli_dogrula(gecmis)
        history = history[(history.zaman < a) & (history.mw >= m.mc0)].reset_index(drop=True)
        if not len(history) or not (history.mw.to_numpy(float) >= self.m_s - 1e-9).any():
            return out
        duration = float((z - a) / GUN)
        age = ((a - history.zaman) / GUN).to_numpy(float)
        if m.tmax_gun is None:
            om = (M._omori_ilke(age + duration, m.th['c'], m.th['p'])[0] -
                  M._omori_ilke(age, m.th['c'], m.th['p'])[0])
        else:
            ust = np.minimum(age + duration, m.tmax_gun)
            om = np.where(age < m.tmax_gun,
                          M._omori_ilke(ust, m.th['c'], m.th['p'])[0] -
                          M._omori_ilke(age, m.th['c'], m.th['p'])[0], 0.0)
        w = m.th['K'] * 10 ** (m.th['alpha'] * (history.mw.to_numpy(float) - m.mc0)) * om
        m._mekan(history, grid)  # taban zaten kurdu; önbellek boş değilse bedava
        d_cell = self.duzeltme_hucre(history, age, w, a, grid)
        if not d_cell.any():
            return out
        edges = np.asarray(m_kenarlar, float)
        mcd = m.mc_det(a, history)
        m1 = np.maximum(edges[:-1], mcd)
        m2 = np.maximum(edges[1:], mcd)
        alt = 10 ** (-m.b * (m1 - m.mc0))
        ust_ = np.where(np.isinf(m2), 0.0, 10 ** (-m.b * (m2 - m.mc0)))
        yeni = out + d_cell[:, None] * (alt - ust_)[None, :]
        if not np.isfinite(yeni).all() or (yeni < -1e-15).any():
            raise ValueError('X beklenen sonlu/negatif değil')
        return np.maximum(yeni, 0.0)
