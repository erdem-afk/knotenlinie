"""Deney T'nin DuzETAS'ına salt-okur bağlayıcı; yeni arka plan/ETAS ayarı yok."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .arayuz import buyukluk_paylari, gecmis_dogrula, pencere_dogrula, durum_integrali
from .dalga2 import alici_paylari
from .girdi import AYAR_SON, SON, k9_basamaklari
from .italya import etas_gunluk

AYAR_SONLARI = ('2006-01-01T00:00:00Z', '2011-01-01T00:00:00Z')


class TopluOrtak:
    """T'nin kendi arka planını/uzay integrallerini bir kez hesapla."""
    def __init__(self, taban, katalog, omori_kutle, *, ayar_son=AYAR_SON):
        end = pd.Timestamp(ayar_son)
        if end not in tuple(pd.Timestamp(t) for t in AYAR_SONLARI) or pd.Timestamp(
                taban.p['ayar_bitis']) != end:
            raise ValueError('ortak ayar sonu açık 2006/2011 seçimiyle uyuşmuyor')
        self.taban = taban
        self.parametre = taban.th.copy()
        self.m0, self.b = taban.mc, taban.b
        self.omori_kutle = omori_kutle
        self.katalog = gecmis_dogrula(katalog, SON)
        self.katalog = self.katalog[(self.katalog.zaman >= taban.baslangic)
                                    & (self.katalog.mw >= self.m0)].reset_index(drop=True)
        self.izgara = taban.izgara.copy()
        grid = self.izgara.to_numpy(float)
        self.u = taban._arka_plan(grid)
        self.arka_plan = self.parametre['mu']*self.u
        # T'nin bir çağrıda tüm ebeveyn satırlarını listede tutup vstack yapması
        # üç tam kopya gerektirir. Küçük bloklar aynı integrali, tek kalıcı matrise yazar.
        self.kernel = np.empty((len(self.katalog), len(grid)))
        for a in range(0, len(self.katalog), 16):
            z = min(a+16, len(self.katalog))
            self.kernel[a:z] = taban._mekan(self.katalog.iloc[a:z].reset_index(drop=True), grid)

    def uzay(self, izgara, gecmis):
        if (not np.array_equal(izgara.to_numpy(float), self.izgara.to_numpy(float))
                or not gecmis[['zaman', 'boylam', 'enlem', 'mw']].reset_index(drop=True).equals(
                    self.katalog[['zaman', 'boylam', 'enlem', 'mw']])):
            raise ValueError('önhesaplı ortak grid/geçmiş uyuşmuyor')
        # etas_gunluk CRS payını kullanmaz; alıcı karışımı ayrı hesaplanır.
        return self.u, None, self.kernel

    def gunluk(self, gunler):
        return etas_gunluk(self, self.katalog, self.izgara, gunler,
                           omori_kutle=self.omori_kutle)[0]


class OrtakCRS:
    """Deney H'nin ortak imzası: ortak ETAS + yalnız onun arka planına CRS."""
    def __init__(self, taban, faylar, *, asigma_pa, agirlik, ayar_son=AYAR_SON):
        end = pd.Timestamp(ayar_son)
        if end not in tuple(pd.Timestamp(t) for t in AYAR_SONLARI) or pd.Timestamp(
                taban.p['ayar_bitis']) != end:
            raise ValueError('ortak taban ayar sonu açık 2006/2011 seçimiyle uyuşmuyor')
        if not np.isfinite([asigma_pa, agirlik]).all() or asigma_pa <= 0 or not 0 <= agirlik <= 1:
            raise ValueError('CRS Aσ/ağırlık geçersiz')
        self.taban, self.faylar = taban, faylar
        self.asigma_pa, self.agirlik = asigma_pa, agirlik

    def beklenen(self, baslangic, bitis, gecmis, izgara, m_kenarlar):
        a, z = pencere_dogrula(baslangic, bitis)
        h = gecmis_dogrula(gecmis, a)
        h = h[(h.zaman >= self.taban.baslangic) & (h.mw >= self.taban.mc)]
        e = self.taban.beklenen(a, z, h, izgara, m_kenarlar)
        if self.agirlik == 0:
            return e
        grid = izgara.to_numpy(float)
        dt = (z-a)/pd.Timedelta(days=1)
        arka = self.taban.th['mu']*self.taban._arka_plan(grid)
        ts, ds = k9_basamaklari(h, self.faylar)
        ri = durum_integrali(a, z, ts, ds, self.asigma_pa,
                             self.faylar.tau_dot_pa_gun.to_numpy())
        pay = alici_paylari(izgara, self.faylar)
        mag = buyukluk_paylari(m_kenarlar, self.taban.mc, self.taban.b)
        tetikleme = np.maximum(e-(arka*dt)[:, None]*mag[None, :], 0.)
        mod = (1-self.agirlik)*dt+self.agirlik*(pay @ ri)
        out = tetikleme+(arka*mod)[:, None]*mag[None, :]
        if not np.isfinite(out).all() or (out < 0).any():
            raise ValueError('melez beklentisi geçersiz')
        return out
