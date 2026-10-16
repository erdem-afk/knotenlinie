"""Hücre-gün özellikleri: yalnız gün başından önceki olaylardan.

Olaylar M>=3,1 (HORUS tamlığı 1985'ten beri; R/N ebeveyn eşiğiyle aynı) ve
derinlik [0,30) km. İlk tasarımdaki M>=2,5 eşiği kullanılmaz: 2005 öncesi katalog
M<3,1'de eksik olduğundan 2,5 sayımı eğitim (≤2005) ve puanlama (2006+)
arasında anlam kaydırırdı. Düşük eşik 3,1, yüksek eşik 3,5.

Özellik sırası (ADLAR): 30 sayım (yarıçap 10/30/100 km × eşik × pencere
1/7/30/365/3650 gün), 50 km içinde son 30 gündeki en büyük M ve ondan geçen süre,
en yakın M>=4,5 olayın uzaklığı ve yaşı, arka plan log oranı (KDE), isteğe bağlı
R'nin log oranı. Eksik değer NaN (HistGradientBoosting yerli işler).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import sparse
from scipy.spatial import cKDTree

EPOCH = pd.Timestamp('1985-01-01', tz='UTC')
RE = 6371.0
MC_ALT = 3.1
MC_UST = 3.5
M_BUYUK = 4.5
PENCERELER = (1, 7, 30, 365, 3650)
YARICAPLAR = (10, 30, 100)
YARICAP_MAKS = 50
HUCRE_ESIK_KM = 12.0
KDE_BANT_KM = 20.0
KDE_KESIM_KM = 60.0
KDE_ZEMIN = 1e-3

ADLAR = ['n_r%d_m%s_w%d' % (r, ('3.1' if m == MC_ALT else '3.5'), w)
         for r in YARICAPLAR for m in (MC_ALT, MC_UST) for w in PENCERELER]
ADLAR += ['maxM_30g_50km', 'yas_maxM_30g_50km', 'uzak_M45', 'yas_M45', 'kde_log']
R_AD = 'R_log'
TUM_ADLAR = ADLAR + [R_AD]


def xyz(enlem, boylam):
    la, lo = np.radians(np.asarray(enlem, float)), np.radians(np.asarray(boylam, float))
    return RE * np.column_stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])


def gun_no(zaman):
    """UTC zaman damgası ya da dizisi → 1985-01-01'den gün (float)."""
    z = pd.to_datetime(zaman, utc=True)
    if isinstance(z, pd.Timestamp):
        return float((z - EPOCH) / pd.Timedelta(days=1))
    return np.asarray((z - EPOCH) / pd.Timedelta(days=1), float)


class Olaylar:
    """Zamana göre sıralı olay dizileri (yalnız M>=3,1, derinlik [0,30), >=1985)."""

    def __init__(self, t, mw, hucre, xyz_, enlem, boylam):
        o = np.argsort(t, kind='stable')
        self.t, self.mw, self.hucre = t[o], mw[o], hucre[o]
        self.xyz, self.enlem, self.boylam = xyz_[o], enlem[o], boylam[o]
        self.b45 = np.flatnonzero(self.mw >= M_BUYUK - 1e-9)

    def __len__(self):
        return len(self.t)


class OzellikHesap:
    """Izgaraya bağlı sabit yapılar (komşuluk matrisleri, ağaç) ve günlük hesap."""

    def __init__(self, izgara):
        g = izgara[['boylam_min', 'boylam_max', 'enlem_min', 'enlem_max']].to_numpy(float)
        self.izgara = g
        self.n = len(g)
        self.lon_c = (g[:, 0] + g[:, 1]) / 2
        self.lat_c = (g[:, 2] + g[:, 3]) / 2
        self.xyz_c = xyz(self.lat_c, self.lon_c)
        self.agac = cKDTree(self.xyz_c)
        self.A = {}
        for r in sorted(set(YARICAPLAR) | {YARICAP_MAKS}):
            d = self.agac.sparse_distance_matrix(self.agac, r, output_type='coo_matrix')
            a = sparse.coo_matrix((np.ones(d.nnz, np.float32), (d.row, d.col)), shape=(self.n, self.n)).tocsr()
            # öz hücre (uzaklık 0) sparse_distance_matrix'te yer almayabilir
            a = a + sparse.identity(self.n, dtype=np.float32, format='csr') - a.multiply(sparse.identity(self.n, dtype=np.float32, format='csr'))
            a.sort_indices()
            self.A[r] = a.tocsr()
        self._kde_w = None

    # ---- hücre eşleme -------------------------------------------------------
    def hucre_kutu(self, enlem, boylam):
        """Kosucu ile aynı yarı açık kutu kuralı; ızgara dışı -1."""
        enlem, boylam = np.round(np.asarray(enlem, float), 12), np.round(np.asarray(boylam, float), 12)
        out = np.full(len(enlem), -1, int)
        if not len(enlem):
            return out
        _, idx = self.agac.query(xyz(enlem, boylam), k=4)
        g = np.round(self.izgara, 12)
        for j in range(idx.shape[1] - 1, -1, -1):
            c = idx[:, j]
            ok = (g[c, 0] <= boylam) & (boylam < g[c, 1]) & (g[c, 2] <= enlem) & (enlem < g[c, 3])
            out[ok] = c[ok]
        return out

    def hucre_yakin(self, enlem, boylam):
        """En yakın hücre merkezi (özellik sayımı için); > HUCRE_ESIK_KM ise -1."""
        if not len(enlem):
            return np.zeros(0, int)
        d, i = self.agac.query(xyz(enlem, boylam), distance_upper_bound=HUCRE_ESIK_KM)
        return np.where(np.isfinite(d), i, -1).astype(int)

    # ---- olay hazırlığı -------------------------------------------------------
    def olaylar(self, df):
        """DataFrame (zaman, enlem, boylam, derinlik, mw) → Olaylar."""
        z = pd.to_datetime(df['zaman'], utc=True)
        mw = df['mw'].to_numpy(float)
        dp = df['derinlik'].to_numpy(float)
        use = ((mw >= MC_ALT - 1e-6) & (dp >= 0) & (dp < 30) & (z >= EPOCH).to_numpy())
        d = df[use]
        t = gun_no(z[use])
        la, lo = d['enlem'].to_numpy(float), d['boylam'].to_numpy(float)
        return Olaylar(np.asarray(t, float), d['mw'].to_numpy(float), self.hucre_yakin(la, lo),
                       xyz(la, lo), la, lo)

    # ---- KDE ------------------------------------------------------------------
    def _kde_matris(self):
        if self._kde_w is None:
            d = self.agac.sparse_distance_matrix(self.agac, KDE_KESIM_KM, output_type='coo_matrix')
            w = np.exp(-0.5 * (d.data / KDE_BANT_KM) ** 2).astype(np.float32)
            m = sparse.coo_matrix((w, (d.row, d.col)), shape=(self.n, self.n)).tocsr()
            self._kde_w = m + sparse.identity(self.n, dtype=np.float32, format='csr') - \
                m.multiply(sparse.identity(self.n, dtype=np.float32, format='csr'))
            # öz hücre ağırlığı 1 (uzaklık 0 → exp(0)=1)
        return self._kde_w

    def kde_log(self, ol, t_bas, t_son, haric_yil_mod=None, mod=4):
        """Arka plan log oranı: [t_bas, t_son) olaylarının 20 km Gauss yumuşatması.

        ``haric_yil_mod=f``: yılı (yıl % mod == f) olan olaylar dışarıda bırakılır
        (eğitim satırı için çapraz-uyum: satırın kendi olayı yoğunluğa girmez).
        """
        s = (ol.t >= t_bas) & (ol.t < t_son) & (ol.hucre >= 0)
        if haric_yil_mod is not None:
            yil = (EPOCH + pd.to_timedelta(ol.t, unit='D')).year.to_numpy()
            s &= (yil % mod) != haric_yil_mod
        say = np.bincount(ol.hucre[s], minlength=self.n).astype(np.float64)
        yog = self._kde_matris() @ say
        yog = yog / max(yog.mean(), 1e-300)
        return np.log(yog + KDE_ZEMIN).astype(np.float32)

    # ---- günlük özellik -------------------------------------------------------
    def hesapla(self, ol, t0, kde, r_log=None):
        """t0 (gün no) başlangıçlı gün için (n, F) float32. Yalnız t < t0 olayları."""
        hi = int(np.searchsorted(ol.t, t0, side='left'))
        lo = int(np.searchsorted(ol.t, t0 - PENCERELER[-1], side='left'))
        t, m, c = ol.t[lo:hi], ol.mw[lo:hi], ol.hucre[lo:hi]
        yas = t0 - t
        var = c >= 0
        cols = []
        C = np.zeros((self.n, 2 * len(PENCERELER)), np.float32)
        j = 0
        for ust in (False, True):
            ms = var & (m >= (MC_UST - 1e-9 if ust else MC_ALT - 1e-6))
            for w in PENCERELER:
                s = ms & (yas <= w)
                if s.any():
                    C[:, j] = np.bincount(c[s], minlength=self.n)
                j += 1
        for r in YARICAPLAR:
            cols.append(self.A[r] @ C)          # (n, 10): [alt×5 pencere, üst×5 pencere]
        sayim = np.hstack(cols)                 # r × (alt,üst) × pencere sırası
        # en büyük M, 50 km, son 30 gün
        mx = np.full(self.n, np.nan, np.float32)
        ya = np.full(self.n, np.nan, np.float32)
        s = var & (yas <= 30)
        if s.any():
            A = self.A[YARICAP_MAKS]
            ce, me, ye = c[s], m[s], yas[s]
            bas, son = A.indptr[ce], A.indptr[ce + 1]
            ln = son - bas
            tot = int(ln.sum())
            pos = np.repeat(bas - np.concatenate([[0], np.cumsum(ln)[:-1]]), ln) + np.arange(tot)
            hc = A.indices[pos]
            hm = np.repeat(me, ln)
            hy = np.repeat(ye, ln)
            mxv = np.full(self.n, -np.inf)
            np.maximum.at(mxv, hc, hm)
            eş = hm >= mxv[hc] - 1e-12
            yav = np.full(self.n, np.inf)
            np.minimum.at(yav, hc[eş], hy[eş])
            var_h = np.isfinite(mxv)
            mx[var_h] = mxv[var_h]
            ya[var_h] = yav[var_h]
        # en yakın M>=4,5 (1985'ten beri)
        uz = np.full(self.n, np.nan, np.float32)
        y45 = np.full(self.n, np.nan, np.float32)
        b = ol.b45[ol.b45 < hi]
        if len(b):
            d, i = cKDTree(ol.xyz[b]).query(self.xyz_c)
            uz = d.astype(np.float32)
            y45 = (t0 - ol.t[b][i]).astype(np.float32)
        parts = [sayim, mx[:, None], ya[:, None], uz[:, None], y45[:, None],
                 np.asarray(kde, np.float32)[:, None]]
        if r_log is not None:
            parts.append(np.asarray(r_log, np.float32)[:, None])
        return np.hstack(parts).astype(np.float32)
