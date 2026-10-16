"""Deney H ortak arayüzü: sabit bütçe veya D2 ortak ETAS arka planı."""
from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

from .butce import YIL_SANIYE, yillik, karisim
from .veri import fay_oku, kaynak_kapisi


class FayButce:
    """Sabit faylar + opsiyonel sabit taban; çağrıda katalogla yeniden ayar yok."""

    def __init__(self, faylar, *, sigma_km=10, b=1.0, mmin=2.4,
                 taban=None, agirlik=1.0, toplam_esitle=False):
        if not np.isfinite(agirlik) or not 0 <= agirlik <= 1:
            raise ValueError('ağırlık [0,1] olmalı')
        if taban is None and agirlik != 1:
            raise ValueError('karışım tabanı yok')
        self.faylar = faylar.copy(deep=True)
        self.sigma_km, self.b, self.mmin = sigma_km, b, mmin
        self.taban, self.agirlik, self.toplam_esitle = taban, agirlik, toplam_esitle
        self._cache = None

    def beklenen(self, baslangic, bitis, gecmis, izgara, m_kenarlar):
        bas, son = pd.Timestamp(baslangic), pd.Timestamp(bitis)
        if bas.tzinfo is None or son.tzinfo is None or son < bas:
            raise ValueError('zaman aralığı UTC ve sıralı olmalı')
        kaynak_kapisi(self.faylar, son-pd.Timedelta(nanoseconds=1))
        # Zaman bağımsız: gecmis okunmaz, tabana da aynı boş geçmiş verilir.
        bos = pd.DataFrame(columns=['zaman','enlem','boylam','derinlik','mw'])
        sure = (son-bas).total_seconds()/YIL_SANIYE
        if self.agirlik == 0:
            return karisim(self.taban(bas,son,bos,izgara,m_kenarlar),
                           np.zeros((len(izgara),len(m_kenarlar)-1)), 0)
        anahtar = (izgara[['boylam_min','boylam_max','enlem_min','enlem_max']].to_numpy(float).tobytes(),
                   np.asarray(m_kenarlar,float).tobytes())
        if self._cache is None or self._cache[0] != anahtar:
            self._cache = (anahtar, yillik(self.faylar, izgara, m_kenarlar,
                              sigma_km=self.sigma_km, b=self.b, mmin=self.mmin))
        fay = self._cache[1] * sure
        if self.taban is None:
            return fay
        return karisim(self.taban(bas,son,bos,izgara,m_kenarlar), fay,
                       self.agirlik, toplam_esitle=self.toplam_esitle)


_MODEL = None


def yapilandir(faylar, **ayarlar):
    """Açık, süreç içi bağlama; herhangi bir ``beklenen`` taban olarak geçirilebilir."""
    global _MODEL
    _MODEL = FayButce(faylar, **ayarlar)
    return _MODEL


def ayar_oku(yol):
    """Koşucu ayarı: sabit fay GeoJSON + önceden dondurulmuş KDE (GEAR1 tabanı bu sürümde yok)."""
    from .taban import Duzlestirilmis
    d = json.loads(Path(yol).read_text(encoding='utf-8'))
    if d.get('taban') == 'ortak_etas':
        from .etas import ayar_oku as etas_oku
        global _MODEL
        _MODEL = etas_oku(yol)
        return _MODEL
    fay = fay_oku(d['fay_yolu'], surum=d['surum'], en_gec=d.get('kaynak_en_gec'))
    if d['taban'] == 'duzlestirilmis':
        # Bu dosyada yalnız ≤1990 eğitim olayları vardır, açık pencere yok.
        t = pd.read_csv(d['egitim_yolu'])
        t['zaman'] = pd.to_datetime(t['zaman'], utc=True)
        taban = Duzlestirilmis(t, baslangic=d['egitim_baslangic'],
                              bitis=d['egitim_bitis'], sigma_km=d['taban_sigma_km'],
                              b=d.get('b',1), mmin=d['esik']).beklenen
    else:
        raise ValueError(f"bilinmeyen taban {d['taban']!r}; sessiz yerine geçme yok")
    return yapilandir(fay, taban=taban, agirlik=d['agirlik'], sigma_km=d['sigma_km'],
                      b=d.get('b',1), mmin=d.get('mmin',2.4),
                      toplam_esitle=d.get('toplam_esitle',False))


def beklenen(baslangic, bitis, gecmis, izgara, m_kenarlar):
    """[baslangic,bitis) hücre×büyüklük sayısı; D2 geçmişi ETAS'a geçirir."""
    global _MODEL
    if _MODEL is None:
        yol = os.environ.get('KNOTENLINIE_FAY_AYAR')
        if not yol:
            raise RuntimeError('önce yapilandir(...) veya KNOTENLINIE_FAY_AYAR ayarı gerekli')
        ayar_oku(yol)
    return _MODEL.beklenen(baslangic, bitis, gecmis, izgara, m_kenarlar)
