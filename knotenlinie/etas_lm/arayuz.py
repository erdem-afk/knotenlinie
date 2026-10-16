"""ETAS-LM yaklaşık koşullu günlük ortalaması; ortak beklenen imzası."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.signal import fftconvolve

from knotenlinie.karsilastir.kosucu import katalog_kontrol, utc, KESIM, geometri
from knotenlinie.ortak_zemin.veri import IZGARA, izgara_dogrula
from .arka_plan import BAS, SON, kur, km_izgara
from .cekirdek import MC, B, D, K, C, P, ALPHA, hucre_kutlesi, zaman_katsayilari, ortalama_uretkenlik


class ETASLM:
    """Gün içi kızları gözlemden değil doğrusal dallanma beklentisinden ekler.

    Gerçek ebeveyn→hücre analitik. Kız→hücre geçişi kaynak hücrede uniform
    kuadratür, zaman product-integration: özgün 1000 thinning örneği değil.
    Mekânsal dış kütle her nesilde kayıp. Parametre ayarı yok.
    """
    def __init__(self, katalog_ayar, izgara, *, adim=32, nesil=10, uzay_dugum=4):
        if adim < 1 or int(adim) != adim or nesil < 0 or int(nesil) != nesil or uzay_dugum < 1 or int(uzay_dugum) != uzay_dugum:
            raise ValueError('Geçersiz sayısal ayar')
        self.izgara = izgara[IZGARA].copy().reset_index(drop=True)
        self.background, self.met, bg = kur(katalog_ayar, self.izgara)
        self.adim, self.nesil = int(adim), int(nesil)
        self.grid_km = km_izgara(self.izgara, self.met)
        g, origin, size, _ = izgara_dogrula(self.izgara)
        keys = np.rint((g[:, [0, 2]]-origin)/size).astype(int)
        self.ix, self.iy = keys.T
        nx, ny = self.ix.max()+1, self.iy.max()+1
        self.shape = (ny, nx)
        dx, dy = size * [self.met.kx, self.met.ky]
        xx, yy = np.meshgrid(np.arange(-nx+1, nx)*dx, np.arange(-ny+1, ny)*dy)
        rect = np.column_stack([(xx-dx/2).ravel(), (xx+dx/2).ravel(), (yy-dy/2).ravel(), (yy+dy/2).ravel()])
        nodes, weights = np.polynomial.legendre.leggauss(uzay_dugum)
        kernel = np.zeros(len(rect))
        for i, x in enumerate(nodes):
            for j, y in enumerate(nodes):
                kernel += weights[i]*weights[j]/4 * hucre_kutlesi(x*dx/2, y*dy/2, rect)
        self.kernel = kernel.reshape(xx.shape)
        self._keys = []
        self._spatial = np.empty((0, len(g)))
        self.max_last_ratio = 0.0
        self.metadata = dict(ozgun_tahmin=False, durum='PROVISIONAL: HORUS-Mw + açık bant/sayısal varsayımları',
                             kaynak='Lombardi & Marzocchi 2010, doi:10.4401/ag-4848, Eq1/3, Table1',
                             tetikleme=dict(K_gun=K, c_gun=C, p=P, alpha_dogal=ALPHA, d_km=D, q=1.5, mc=MC, b=B,
                                           mu_yil_makale=237, ortalama_uretkenlik=ortalama_uretkenlik()),
                             arka_plan=bg, zaman_adimi=adim, nesil=nesil, uzay_GL_dugum=uzay_dugum,
                             kiz_mmax=9.0, derinlik_min=0, derinlik_max=30,
                             derinlik_tanimi='sığ kaynak/hedef [0,30); s162 >30 yazımı s159 ile tutarsız: <30 alındı')

    def _mekan(self, h):
        keys = list(map(tuple, h[['zaman', 'boylam', 'enlem', 'mw']].to_numpy()))
        if keys[:len(self._keys)] != self._keys:
            self._keys = []
            self._spatial = np.empty((0, len(self.izgara)))
        if len(keys) > len(self._keys):
            if len(keys) > len(self._spatial):
                capacity = max(16, 1 << (len(keys)-1).bit_length())
                new = np.empty((capacity, len(self.izgara)))
                new[:len(self._keys)] = self._spatial[:len(self._keys)]
                self._spatial = new
            for i in range(len(self._keys), len(keys)):
                row = h.iloc[i]
                x, y = self.met.km(row.boylam, row.enlem)
                self._spatial[i] = hucre_kutlesi(x, y, self.grid_km)
            self._keys = keys
        return self._spatial[:len(keys)]

    def gecis(self, cell):
        field = np.zeros(self.shape)
        field[self.iy, self.ix] = cell
        # FFT yuvarlama (~1e-16) dışında kütle tabanlaması yok.
        out = fftconvolve(field, self.kernel, mode='same')[self.iy, self.ix]
        if out.min() < -1e-12 * max(1, cell.max()):
            raise ValueError('Negatif FFT kütlesi')
        return np.maximum(out, 0)

    def beklenen(self, baslangic, bitis, gecmis, izgara, m_kenarlar):
        a, z = utc(baslangic), utc(bitis)
        if not SON <= a < z <= KESIM or z-a > pd.Timedelta(days=1):
            raise ValueError('≤2016 kapısı; en fazla bir günlük tahmin')
        h = katalog_kontrol(gecmis)
        if (h.zaman >= a).any():
            raise ValueError('Geçmiş gün başından önce olmalı')
        g, edges = geometri(izgara, m_kenarlar)
        if not np.array_equal(g, np.round(self.izgara.to_numpy(float), 12)) or edges[0] < MC:
            raise ValueError('Kurulum ızgarası/Mc uyuşmuyor')
        h = h[(h.zaman >= BAS) & (h.mw >= MC) & (h.derinlik >= 0) & (h.derinlik < 30)].reset_index(drop=True)
        age = ((a-h.zaman)/pd.Timedelta(days=1)).to_numpy(float)
        duration = float((z-a)/pd.Timedelta(days=1))
        coeff = zaman_katsayilari(age, h.mw.to_numpy(float), duration, self.adim, self.nesil)
        spatial = self._mekan(h)
        # BLAS tek thread koşuda: (11,N)@(N,hücre), <1GB kalıcı matris.
        raw = coeff[:, :-1] @ spatial + coeff[:, -1, None] * self.background[None, :]
        # Horner: Σ P^g raw[g], yalnız nesil sayısı kadar FFT.
        cell = raw[-1].copy()
        for generation in range(len(raw)-2, -1, -1):
            cell = raw[generation] + self.gecis(cell)
        # P alt-stokastik olduğundan son neslin ham kütlesi üst sınırdır.
        if cell.sum():
            self.max_last_ratio = max(self.max_last_ratio, float(raw[-1].sum())/float(cell.sum()))
        mag = 10**(-B*(edges[:-1]-MC)) - 10**(-B*(edges[1:]-MC))
        return cell[:, None] * mag[None, :]


_MODEL = None


def beklenen(baslangic, bitis, gecmis, izgara, m_kenarlar):
    """Varsayılan sabit arka plan yalnız ≤2010 katalogdan yüklenir."""
    global _MODEL
    if _MODEL is None:
        from knotenlinie.ortak_zemin.veri import VERI, katalog_oku
        cat = katalog_oku(VERI/'ortak/italya_katalog_le2015.csv')
        _MODEL = ETASLM(cat[cat.zaman < SON], izgara)
    return _MODEL.beklenen(baslangic, bitis, gecmis, izgara, m_kenarlar)
