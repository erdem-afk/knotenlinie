"""Fay kaynak tabloları: İtalya DISS 3.2.0 (ISS + CSS).

Her kaynak: kimlik, katman (ISS/CSS), yüzey izdüşümü poligonu, düzlem alanı,
kayma hızı (aralık orta değeri), Mmax, son olay (kesirli yıl ya da NaN),
ebeveyn CSS. Moment bütçesinde ISS, ebeveyn CSS'nin içindedir: ISS kendi Ṁ₀'ını
taşır, ebeveyn CSS'ye kalan max(Ṁ₀_CSS − ΣṀ₀_ISS, 0) verilir (çift sayım yok).

Zaman kesimi D (kesirli yıl; 2006.0 ya da 2011.0): son olay D'den önce olmalı;
`latesteq > D` ve (`created > D` ya da `updated > D`) olan ISS düşer (kaynak,
sonraki depremle tanımlanmış/güncellenmiş). CSS'ler jeolojik içeriktir, kesime
bakılmaz (DISS 3.2.0 parametreleri 2015 sürümüdür; sızıntı notu raporda).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from shapely.geometry import shape

from knotenlinie.fay_butce.veri import fay_oku, cpti_oku
from knotenlinie.fay_zaman.moment import moment_hizi

from knotenlinie.yollar import VERI  # noqa: E402
AYLAR = {m: i for i, m in enumerate(
    ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'], 1)}
_TARIH = re.compile(r'(\d{1,2})\s+([A-Za-z]{3})[a-z]*\s+(\d{3,4})(?!\d)')
KOLONLAR = ['id', 'ad', 'katman', 'poligon', 'alan_km2', 'kayma_mm_yil', 'mmax',
            'son_yil', 'ebeveyn', 'kaynak_son']


def yil_kesir(yil, ay=1, gun=1):
    return float(yil) + (int(ay) - 1) / 12.0 + (int(gun) - 1) / 365.25


def son_olay_yili(metin):
    """DISS `latesteq` metninden kesirli yıl; aralık/belirsiz/'Unknown' → None.

    Yalnız 'GG Ay YYYY' (ek '(1/2)' serbest) biçimi kesin tarihtir.
    """
    if not isinstance(metin, str):
        return None
    t = metin.strip()
    if re.search(r'B\.?C|before|unknown|ca\.|around', t, flags=re.I):
        return None
    m = _TARIH.search(t)
    if not m or m.group(2).lower() not in AYLAR:
        return None
    # '530-900 A.D.' gibi aralıklar GG Ay YYYY biçimi içermez; yukarıda elenir.
    return yil_kesir(int(m.group(3)), AYLAR[m.group(2).lower()], int(m.group(1)))


def _yil_alan(s):
    s = str(s)
    return int(s[:4]) + 0.0 if len(s) >= 4 and s[:4].isdigit() else float('nan')


def _gecerli(poly):
    if not poly.is_valid:
        poly = poly.buffer(0)
    return poly


def _cpti_ilis(poly, mmax, D, cpti, yaricap=0.05, dm=0.5):
    """CPTI15 ≤D ilişkilendirmesi: poligon (+0,05°) içinde, Mw ≥ Mmax−0,5, en yeni."""
    if cpti is None:
        return None
    from shapely.geometry import Point
    g = poly.buffer(yaricap)
    c = cpti[(cpti.zaman.dt.year + cpti.zaman.dt.dayofyear / 366.0 < D) & (cpti.mw >= mmax - dm)]
    best = None
    for z, lo, la in zip(c.zaman, c.boylam, c.enlem):
        if g.contains(Point(lo, la)):
            y = yil_kesir(z.year, z.month, z.day)
            best = y if best is None or y > best else best
    return best


def italya(D, cpti=True):
    """İtalya: DISS 3.2.0 CSS (tümü) + ISS (zaman kesimi kuralı). Döner (tablo, günlük)."""
    gunluk = dict(iss_toplam=0, iss_dusen_sonraki_olay=[], iss_cpti_iliskili=[], iss_son_bilinen=0)
    css_f = fay_oku(VERI / 'diss320/csstop320.geojson', surum='DISS3.2.0')
    pln = {f['properties']['idsource']: _gecerli(shape(f['geometry']))
           for f in json.load(open(VERI / 'diss320/csspln320.geojson'))['features']}
    rows = []
    for r in css_f.itertuples(index=False):
        if r.id not in pln:
            continue
        rows.append(dict(id=r.id, ad=r.id, katman='CSS', poligon=pln[r.id], alan_km2=r.alan_km2,
                         kayma_mm_yil=r.kayma_mm_yil, mmax=r.mmax, son_yil=np.nan,
                         ebeveyn=None, kaynak_son=None))
    cp = None
    if cpti:
        cp = cpti_oku(VERI / 'kesik-2015/CPTI15_v4.0_le2015.csv', ilk_yil=1000)
    for f in json.load(open(VERI / 'diss320/iss320.geojson'))['features']:
        p = f['properties']
        gunluk['iss_toplam'] += 1
        son = son_olay_yili(p['latesteq'])
        cr, up = _yil_alan(p['created']), _yil_alan(p['updated'])
        if son is not None and son >= D and (cr >= D or up >= D):
            gunluk['iss_dusen_sonraki_olay'].append(p['idsource'])
            continue
        try:
            v0, v1 = float(p['srmin']), float(p['srmax'])
            L, W, mmax = float(p['length']), float(p['width']), float(p['maxmag'])
        except (TypeError, ValueError):
            continue
        poly = _gecerli(shape(f['geometry']))
        kaynak = None
        if son is not None:
            if son < D:
                kaynak = 'DISS'
            else:
                son = None  # son olay ayar tarihinden sonra: ayar anında bilinmiyor → Poisson
        elif cp is not None:  # DISS tarihi belirsiz/yok: CPTI15 ≤D ilişkilendirmesi
            y = _cpti_ilis(poly, mmax, D, cp)
            if y is not None:
                son, kaynak = y, 'CPTI15'
                gunluk['iss_cpti_iliskili'].append(p['idsource'])
        if son is not None:
            gunluk['iss_son_bilinen'] += 1
        rows.append(dict(id=p['idsource'], ad=p['sourcename'], katman='ISS', poligon=poly,
                         alan_km2=L * W, kayma_mm_yil=(v0 + v1) / 2.0, mmax=mmax,
                         son_yil=son if son is not None else np.nan, ebeveyn=None,
                         kaynak_son=kaynak))
    return ebeveyn_ata(pd.DataFrame(rows, columns=KOLONLAR)), gunluk


def ebeveyn_ata(t, esik=0.5):
    """ISS'e, poligonunun en az `esik` payı içinde kalan en çok örtüşen CSS'yi ata.

    Önceden atanmış ebeveyn korunur; CSS tablosunda yoksa None olur."""
    t = t.copy().reset_index(drop=True)
    css = t[t.katman == 'CSS']
    kimlikler = set(css.id)
    for i in t.index[t.katman == 'ISS']:
        mevcut = t.at[i, 'ebeveyn']
        if isinstance(mevcut, str):
            t.at[i, 'ebeveyn'] = mevcut if mevcut in kimlikler else None
            continue
        pi = t.at[i, 'poligon']
        en, pay = None, 0.0
        for j in css.index:
            a = pi.intersection(css.at[j, 'poligon']).area / pi.area if pi.area > 0 else 0.0
            if a > pay:
                en, pay = css.at[j, 'id'], a
        t.at[i, 'ebeveyn'] = en if pay >= esik else None
    return t


def moment_dagit(t, baglasim=1.0):
    """Kaynak başına Ṁ₀ (N m/yıl): ISS kendi, ebeveyn CSS kalan (≥0)."""
    t = t.copy()
    t['mdot_ham'] = [moment_hizi(a, s, baglasim=baglasim) if s > 0 else 0.0
                     for a, s in zip(t.alan_km2, t.kayma_mm_yil)]
    t['mdot'] = t['mdot_ham']
    iss = t[(t.katman == 'ISS') & t.ebeveyn.notna()]
    for pid, g in iss.groupby('ebeveyn'):
        j = t.index[(t.katman == 'CSS') & (t.id == pid)]
        t.loc[j, 'mdot'] = np.maximum(t.loc[j, 'mdot_ham'].to_numpy() - g.mdot_ham.sum(), 0.0)
    return t
