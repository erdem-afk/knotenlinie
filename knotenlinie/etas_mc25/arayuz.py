"""Mc2.5 arayüzü; mevcut hücre integrali ve kaskad koduna dokunmaz."""
import json
from pathlib import Path
from knotenlinie.ortak_zemin.arayuz import DuzETAS
from knotenlinie.kaskad.arayuz import KaskadETAS
from knotenlinie.ortak_zemin.veri import VERI

DIZIN=VERI/'ortak/mc25'


def yukle(tur,izgara,*,kaskad=False,adim=32,nesil=10):
    p=json.loads((DIZIN/f'etas_{tur}.json').read_text())
    base=DuzETAS(p,izgara)
    return KaskadETAS(base,adim=adim,nesil=nesil) if kaskad else base


class SigGecmis:
    """Hedef sabit, ebeveyn [0,30) km; ≤30 sarmalayıcıya sınır düzeltmesi."""
    def __init__(self,model,katalog,ayar):
        from knotenlinie.karsilastir.ortak4 import AyriGecmis
        self.wrapper=AyriGecmis(model,katalog[katalog.derinlik<30],ayar)

    def beklenen(self,a,z,h,g,e):
        return self.wrapper.beklenen(a,z,h,g,e)
