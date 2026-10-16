"""Uzun ETAS ortak imzası; Mc kapısı ebeveynin kendi döneminde."""
import json
import numpy as np
import pandas as pd
from knotenlinie.ortak_zemin.arayuz import DuzETAS, utc
from knotenlinie.ortak_zemin.veri import VERI, katalog_dogrula
from knotenlinie.kaskad.arayuz import KaskadETAS

DIZIN = VERI/'ortak/uzun'


def ebeveynler(cat, kutu, son=None):
    c = katalog_dogrula(cat)
    la0, la1, lo0, lo1 = kutu
    mc = np.where(c.zaman < pd.Timestamp('2005-01-01', tz='UTC'), 3.1, 2.5)
    use = ((c.zaman >= pd.Timestamp('1985-01-01', tz='UTC')) &
           (c.boylam >= lo0) & (c.boylam < lo1) & (c.enlem >= la0) & (c.enlem < la1) &
           (c.derinlik >= 0) & (c.derinlik < 30) & (c.mw >= mc))
    if son is not None: use &= c.zaman < utc(son)
    return c[use].reset_index(drop=True)


class UzunETAS:
    def __init__(self, p, grid, *, adim=32, nesil=10):
        self.taban = DuzETAS(p, grid)
        self.model = KaskadETAS(self.taban, adim=adim, nesil=nesil)
        self.mc, self.b, self.p, self.kutu = self.taban.mc, self.taban.b, self.taban.p, self.taban.kutu

    def beklenen(self, a, z, h, grid, edges):
        return self.model.beklenen(a, z, ebeveynler(h, self.kutu), grid, edges)


class TamGecmis:
    """Hedef kataloğundan bağımsız, maskenin dışını da içeren donmuş geçmiş."""
    def __init__(self, model, cat):
        self.model = model; self.k = ebeveynler(cat, model.kutu)

    def beklenen(self, a, z, h, grid, edges):
        stop = self.k.zaman.searchsorted(utc(a), side='left')
        return self.model.beklenen(a, z, self.k.iloc[:stop], grid, edges)


def yukle(tur, grid, **kwargs):
    return UzunETAS(json.loads((DIZIN/f'etas_{tur}.json').read_text()), grid, **kwargs)


_MODEL = None

def beklenen(baslangic, bitis, gecmis, izgara, m_kenarlar):
    global _MODEL
    if _MODEL is None:
        grid = pd.read_csv(VERI/'ortak/italya_izgara.csv')
        _MODEL = yukle('ortak', grid)
    return _MODEL.beklenen(baslangic, bitis, gecmis, izgara, m_kenarlar)
