"""Donmuş ortak tabanın yalnız beklenen-değer gün içi kaskad sarmalayıcısı."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.signal import fftconvolve

from knotenlinie.ortak_zemin.arayuz import ayar_tabani, utc, omori_kutle
from knotenlinie.ortak_zemin.veri import IZGARA, SON, izgara_dogrula, katalog_dogrula
from .cekirdek import mekan_kernel, zaman_katsayilari, ortalama_uretkenlik


class KaskadETAS:
    """H_bas sabit; gün içi gerçek olay yok, parametre ayarı yok.

    Her nesilde donmuş destek dışındaki kütle kayıp (LM ile aynı yaklaşım).
    Mc üstündeki tüm beklenen olaylar ebeveyn olur; skor eşiği ebeveyn
    eşiği değildir. Büyüklükler iid kesilmemiş GR, doğrudan anneler tam
    konum ve büyüklükleriyle tabanın kendi hücre integrallerini kullanır.
    """
    def __init__(self, taban, *, adim=32, nesil=10, uzay_dugum=4, gr_dugum=32):
        for n in (adim, nesil, uzay_dugum, gr_dugum):
            if int(n) != n or n < 0:
                raise ValueError('Geçersiz sayısal ayar')
        if min(adim, uzay_dugum, gr_dugum) < 1:
            raise ValueError('Pozitif kuadratür sayısı gerekli')
        self.taban = taban
        self.mc, self.b, self.p, self.kutu = taban.mc, taban.b, taban.p, taban.kutu
        self.izgara = taban.izgara.copy()
        self.adim, self.nesil = int(adim), int(nesil)
        self.uzay_dugum, self.gr_dugum = int(uzay_dugum), int(gr_dugum)
        self.g, origin, size, _ = izgara_dogrula(self.izgara)
        self.ix, self.iy = np.rint((self.g[:, [0, 2]]-origin)/size).astype(int).T
        nx, ny = self.ix.max()+1, self.iy.max()+1
        self.shape = (ny, nx)
        self.kernel = mekan_kernel(nx, ny, size[0]*taban.met.kx, size[1]*taban.met.ky,
                                   taban.th, self.b, uzay_dugum=uzay_dugum, gr_dugum=gr_dugum)
        self.lookup = {tuple(row): i for i, row in enumerate(np.round(self.g, 9))}
        self.max_last_ratio = self.max_remainder_ratio = 0.0
        self.metadata = dict(zaman_adimi=adim, ek_nesil=nesil, uzay_GL_dugum=uzay_dugum,
                             GR_Laguerre_dugum=gr_dugum, GR='kesilmemiş [Mc,+inf)',
                             ortalama_uretkenlik=ortalama_uretkenlik(taban.th, self.b),
                             dis_kutle='her nesilde donmuş destek dışında kayıp; renormalizasyon yok',
                             kaynak_hucre='uniform; hedef integral tabanın radyal CDF kuadratürü',
                             parametre_ayari=False)

    def gecis(self, cell):
        field = np.zeros(self.shape)
        field[self.iy, self.ix] = cell
        out = fftconvolve(field, self.kernel, mode='same')[self.iy, self.ix]
        if out.min() < -1e-12 * max(1, float(np.max(cell))):
            raise ValueError('Negatif FFT kütlesi')
        return np.maximum(out, 0)

    def beklenen(self, baslangic, bitis, gecmis, izgara, m_kenarlar):
        a, z = utc(baslangic), utc(bitis)
        if not self.taban.ayar_son <= a < z <= SON or z-a > pd.Timedelta(days=1):
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
        if edges.ndim != 1 or len(edges) < 2 or not np.isfinite(edges[:-1]).all() or np.isnan(edges[-1]) or (np.diff(edges) <= 0).any() or edges[0] < self.mc:
            raise ValueError('Geçersiz büyüklük kutuları')
        h = h[(h.mw >= self.mc) & (h.zaman >= self.taban.baslangic)].reset_index(drop=True)
        age = ((a-h.zaman)/pd.Timedelta(days=1)).to_numpy(float)
        duration = float((z-a)/pd.Timedelta(days=1))
        coeff = zaman_katsayilari(age, h.mw.to_numpy(float), duration, self.taban.th,
                                 self.b, self.mc, self.adim, self.nesil)
        background = self.taban.th['mu'] * self.taban._arka_plan(self.g)
        if len(h) and self.taban.th['K'] > 0:
            raw = coeff[:, :-1] @ self.taban._mekan(h, self.g)
            raw += coeff[:, -1, None] * background[None, :]
        else:
            raw = coeff[:, -1, None] * background[None, :]
        cell = raw[-1].copy()
        for gen in range(len(raw)-2, -1, -1):
            cell = raw[gen] + self.gecis(cell)
        if cell.sum() and self.nesil:
            last = float(raw[-1].sum()) / float(cell.sum())
            r = ortalama_uretkenlik(self.taban.th, self.b) * float(omori_kutle(0, duration, self.taban.th['c'], self.taban.th['p']))
            self.max_last_ratio = max(self.max_last_ratio, last)
            self.max_remainder_ratio = max(self.max_remainder_ratio, last*r/(1-r))
        mag = 10**(-self.b*(edges[:-1]-self.mc)) - 10**(-self.b*(edges[1:]-self.mc))
        out = cell[idx, None] * mag[None, :]
        if not np.isfinite(out).all() or (out < 0).any():
            raise ValueError('Geçersiz beklenen')
        return out


_MODELLER = {}


def beklenen(baslangic, bitis, gecmis, izgara, m_kenarlar):
    """Ortak imza; yalnız son=2011 donmuş tabanları sarmalar."""
    target = set(map(tuple, np.round(izgara[IZGARA].to_numpy(float), 9)))
    matches = []
    for bolge in ('italya',):
        if bolge not in _MODELLER:
            _MODELLER[bolge] = KaskadETAS(ayar_tabani(bolge, son='2011-01-01'))
        model = _MODELLER[bolge]
        if target and target <= set(model.lookup):
            matches.append(model)
    if len(matches) != 1:
        raise ValueError('Tek ortak bölge desteği gerekli')
    return matches[0].beklenen(baslangic, bitis, gecmis, izgara, m_kenarlar)
