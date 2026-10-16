"""Zamandan bağımsız uzun vadeli modeller: KDE sismisite + kesik GR.

U0 sabit bantlı Gauss KDE'dir. U1 uyarlamalı bantlıdır (Helmstetter, Kagan ve
Jackson 2007): her olayın bandı k'inci en yakın komşusuna olan uzaklıktır.
U2 seçilen U1 ile DISS 3.2.0 fay moment bütçesi şeklinin konveks karışımıdır
(donmuş kayıttaki U3, GEAR1 şekli karışımı, bu sürümde yoktur; ağırlığı 0 idi).
Karışım ağırlıkları yalnız 2006-2010 ayar olaylarıyla seçilir (bkz. records/Z/KURAL.md).

Şekil hücre kütlesine normalleştirilir (ızgara içinde toplam 1). Kütle kaybı
Gauss kuyruklarının bölge dışına taşmasıdır; yeniden normalleştirme açıkça
kaydedilir. Düzgün zemin payı `zemin_payi` sıfır hücreleri ve kuyruğu taşır.
Büyüklük dağılımı kesik Gutenberg-Richter'dır; b ve M>=mmin toplam oranı
yalnız ayar (<=2005 / <=2010) verisinden gelir.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

from .kumesiz import kumesizlestir, yerel_km, KumesizHatasi

SUTUNLAR = ['zaman', 'enlem', 'boylam', 'derinlik', 'mw']
IZGARA = ['boylam_min', 'boylam_max', 'enlem_min', 'enlem_max']
KM_ENLEM = 110.57
KM_BOYLAM = 111.32
YIL_GUN = 365.25


class UzunVadeHatasi(ValueError):
    """Uzun vadeli model girdisi geçersiz."""


def izgara_dogrula(izgara):
    a = izgara[IZGARA].to_numpy(float)
    if (len(a) == 0 or not np.isfinite(a).all() or (a[:, 0] >= a[:, 1]).any()
            or (a[:, 2] >= a[:, 3]).any()):
        raise UzunVadeHatasi('ızgara hücreleri geçersiz')
    return a


def hucre_merkez_km(a, merkez=None):
    lon = 0.5 * (a[:, 0] + a[:, 1])
    lat = 0.5 * (a[:, 2] + a[:, 3])
    x, y = yerel_km(lat, lon, merkez=merkez)
    alan = (KM_BOYLAM * np.cos(np.deg2rad(lat)) * (a[:, 1] - a[:, 0])
            * KM_ENLEM * (a[:, 3] - a[:, 2]))
    return x, y, alan


def aki_utsu_b(mw, mmin, dm=0.1):
    """Aki–Utsu MLE; (mean(m) - (mmin - dm/2)) paydası."""
    m = np.asarray(mw, float)
    m = m[m >= mmin]
    if len(m) < 10:
        raise UzunVadeHatasi('b için yeterli olay yok')
    ort = float(np.mean(m)) - (mmin - dm / 2.0)
    if ort <= 0:
        raise UzunVadeHatasi('b paydası pozitif değil')
    return float(np.log10(np.e) / ort)


def gr_oranlari(rate_ust, b, mmin, kenarlar):
    """M>=mmin toplam oranından kutu başına yıllık oran (kesik GR)."""
    k = np.asarray(kenarlar, float)
    if (k.ndim != 1 or len(k) < 2 or not np.isfinite(k[:-1]).all()
            or np.isnan(k[-1]) or (np.diff(k) <= 0).any()):
        raise UzunVadeHatasi('büyüklük kenarları geçersiz')
    if not np.isfinite([rate_ust, b, mmin]).all() or b <= 0:
        raise UzunVadeHatasi('oran/b/mmin geçersiz')
    alt = np.maximum(k[:-1], mmin)
    ust = k[1:]
    pay = 10.0 ** (-b * (alt - mmin))
    payda = np.zeros_like(pay)
    sonlu = np.isfinite(ust)
    payda[sonlu] = 10.0 ** (-b * (ust[sonlu] - mmin))
    oran = rate_ust * (pay - payda)
    oran = np.where(ust <= mmin, 0.0, oran)
    return np.maximum(oran, 0.0)


def _gauss_kutle(noktalar_km, sigma_km, merkez_km, alan, *, yaricap_kati=4.0):
    """Her olayın Gauss yoğunluğunu hücre merkezlerinde örnekleyip kütle topla."""
    px, py = noktalar_km[:, 0], noktalar_km[:, 1]
    cx, cy = merkez_km[0], merkez_km[1]
    sigma = np.asarray(sigma_km, float)
    if np.any(sigma <= 0) or not np.isfinite(sigma).all():
        raise UzunVadeHatasi('bant genişliği pozitif sonlu olmalı')
    agac = cKDTree(np.column_stack([cx, cy]))
    kütle = np.zeros(len(cx))
    iki_pi = 2.0 * np.pi
    for i in range(len(px)):
        s = float(sigma[i] if sigma.ndim else sigma)
        idx = np.asarray(agac.query_ball_point([px[i], py[i]], yaricap_kati * s), int)
        if idx.size == 0:
            continue
        dx = cx[idx] - px[i]
        dy = cy[idx] - py[i]
        kütle[idx] += np.exp(-0.5 * (dx * dx + dy * dy) / (s * s)) / (iki_pi * s * s) * alan[idx]
    return kütle


def sekil_kde(noktalar, izgara, *, sigma_km=None, k_komsu=None, sigma_min_km=2.0,
              sigma_max_km=300.0, zemin_payi=0.0, merkez=None):
    """Hücre kütlesi şekli; istenirse uyarlamalı bant. Normalize edilmiş döner."""
    a = izgara_dogrula(izgara)
    p = np.asarray(noktalar, float)
    if p.ndim != 2 or p.shape[1] != 2 or len(p) == 0 or not np.isfinite(p).all():
        raise UzunVadeHatasi('noktalar geçersiz')
    if not 0 <= zemin_payi < 1:
        raise UzunVadeHatasi('zemin payı [0,1) içinde olmalı')
    if merkez is None:
        merkez = (float(np.mean(p[:, 1])), float(np.mean(p[:, 0])))
    x, y = yerel_km(p[:, 1], p[:, 0], merkez=merkez)
    cx, cy, alan = hucre_merkez_km(a, merkez=merkez)
    if (sigma_km is None) == (k_komsu is None):
        raise UzunVadeHatasi('sigma_km ya da k_komsu bir tanesi verilmeli')
    if k_komsu is not None:
        if int(k_komsu) != k_komsu or k_komsu < 1:
            raise UzunVadeHatasi('komşu sayısı pozitif tam olmalı')
        agac_n = cKDTree(np.column_stack([x, y]))
        d, _ = agac_n.query(np.column_stack([x, y]), k=int(k_komsu) + 1)
        sigma = np.clip(d[:, -1], sigma_min_km, sigma_max_km)
    else:
        sigma = np.full(len(p), float(sigma_km))
    kütle = _gauss_kutle(np.column_stack([x, y]), sigma, (cx, cy), alan)
    toplam = kütle.sum()
    if toplam <= 0:
        raise UzunVadeHatasi('KDE kütlesi sıfır')
    sekil = kütle / toplam
    if zemin_payi > 0:
        sekil = (1.0 - zemin_payi) * sekil + zemin_payi / len(sekil)
    return sekil


def noktalar(katalog, izgara):
    """Katalog olaylarının ızgara hücrelerine düşen (boylam, enlem) noktaları."""
    a = izgara_dogrula(izgara)
    lo, la = katalog['boylam'].to_numpy(float), katalog['enlem'].to_numpy(float)
    anahtar = {(round(r[0], 6), round(r[2], 6)): i for i, r in enumerate(a)}
    ic = np.zeros(len(katalog), bool)
    for n, (x, y) in enumerate(zip(lo, la)):
        ana = (round(np.floor(round(x, 6) * 10) / 10, 6),
               round(np.floor(round(y, 6) * 10) / 10, 6))
        i = anahtar.get(ana)
        if i is not None and a[i, 0] <= x < a[i, 1] and a[i, 2] <= y < a[i, 3]:
            ic[n] = True
    return np.column_stack([lo[ic], la[ic]])


def fay_sekli(izgara, m_kenarlar, faylar, *, esik, sigma_km=10.0, b=1.0, mmin=2.4):
    """DISS fay moment bütçesi şekli; M>=esik hücre kütlesi normalize."""
    from knotenlinie.fay_butce.butce import yillik
    ham = yillik(faylar, izgara, m_kenarlar, sigma_km=sigma_km, b=b, mmin=mmin)
    k = np.asarray(m_kenarlar, float)
    j = int(np.searchsorted(k, esik, side='right') - 1)
    ust = ham[:, j:].sum(axis=1)
    toplam = ust.sum()
    if toplam <= 0:
        raise UzunVadeHatasi('fay şekli sıfır')
    return ust / toplam


def karistir(sekil, katki, agirlik):
    """İki normalize şeklin konveks karışımı; agirlik katkının payıdır."""
    if not 0 <= agirlik <= 1:
        raise UzunVadeHatasi('karışım ağırlığı [0,1] içinde olmalı')
    s, k = np.asarray(sekil, float), np.asarray(katki, float)
    if s.shape != k.shape:
        raise UzunVadeHatasi('karışım şekilleri aynı boyutta olmalı')
    out = (1.0 - agirlik) * s + agirlik * k
    t = out.sum()
    if t <= 0:
        raise UzunVadeHatasi('karışım toplamı sıfır')
    return out / t


class UzunVade:
    """Zamandan bağımsız hücre/kutu beklenen sayısı; geçmişi okumaz."""

    def __init__(self, sekil, izgara, *, b, mmin, rate_ust, ad='U', metadata=None):
        self.sekil = np.asarray(sekil, float)
        self.izgara = izgara[IZGARA].reset_index(drop=True).copy()
        self.b, self.mmin, self.rate_ust = float(b), float(mmin), float(rate_ust)
        self.ad = ad
        self.metadata = dict(metadata or {}, b=self.b, mmin=self.mmin, rate_ust=self.rate_ust)
        if self.sekil.shape != (len(self.izgara),) or self.sekil.sum() <= 0:
            raise UzunVadeHatasi('şekil/ızgara uyuşmuyor')

    def beklenen(self, baslangic, bitis, gecmis, izgara, m_kenarlar):
        """[başlangıç,bitiş) hücre×kutu beklenen sayısı; gecmis kullanılmaz."""
        g = np.round(izgara_dogrula(izgara), 12)
        if g.shape != self.izgara.to_numpy(float).shape or not np.array_equal(
                g, np.round(self.izgara.to_numpy(float), 12)):
            raise UzunVadeHatasi('tahmin ızgarası modelin eğitim ızgarasıyla aynı olmalı')
        bas, son = pd.Timestamp(baslangic), pd.Timestamp(bitis)
        if bas.tzinfo is None or son.tzinfo is None or son < bas:
            raise UzunVadeHatasi('zaman aralığı UTC ve artan olmalı')
        yil = (son - bas).total_seconds() / (86400.0 * YIL_GUN)
        oran = gr_oranlari(self.rate_ust, self.b, self.mmin, m_kenarlar)
        return self.sekil[:, None] * oran[None, :] * yil


def kur(katalog_egitim, izgara, *, mmin, m_kenarlar, baslangic, bitis, yontem='gk74',
        bant_km=None, k_komsu=None, zemin_payi=0.002, faylar=None, w_fay=0.0,
        b=None, mmin_b=None, ad='U', metadata=None):
    """Eğitim kataloğunu kümesizleştirip uzun vadeli model kurar."""
    if m_kenarlar is None:
        raise UzunVadeHatasi('m_kenarlar gerekli')
    bas, son = pd.Timestamp(baslangic), pd.Timestamp(bitis)
    if bas.tzinfo is None or son.tzinfo is None or not bas < son:
        raise UzunVadeHatasi('eğitim penceresi UTC ve artan olmalı')
    k = katalog_egitim[SUTUNLAR].copy()
    k['zaman'] = pd.to_datetime(k['zaman'], utc=True)
    if k.empty:
        raise UzunVadeHatasi('eğitim kataloğu boş')
    kk = kumesizlestir(k, yontem)
    kk = kk[(kk['mw'] >= mmin) & (kk['zaman'] >= bas) & (kk['zaman'] < son)].reset_index(drop=True)
    if kk.empty:
        raise UzunVadeHatasi('kümesiz eğitim kataloğu boş')
    yil = (son - bas).total_seconds() / (86400.0 * YIL_GUN)
    if yil <= 0:
        raise UzunVadeHatasi('eğitim süresi sıfır')
    b = aki_utsu_b(kk['mw'], mmin_b if mmin_b is not None else mmin) if b is None else float(b)
    nokta = noktalar(kk, izgara)
    if len(nokta) == 0:
        raise UzunVadeHatasi('ızgara içinde eğitim olayı yok')
    sekil = sekil_kde(nokta, izgara, sigma_km=bant_km, k_komsu=k_komsu,
                      zemin_payi=zemin_payi)
    if faylar is not None and w_fay > 0:
        sekil = karistir(sekil, fay_sekli(izgara, m_kenarlar, faylar, esik=m_kenarlar[0]),
                         w_fay)
    rate_ust = len(kk) / yil
    meta = dict(metadata or {}, yontem=yontem, bant_km=bant_km, k_komsu=k_komsu,
                zemin_payi=zemin_payi, w_fay=w_fay,
                egitim_n=len(kk), egitim_yil=yil, kumesiz_tur=yontem,
                egitim_baslangic=bas.isoformat(), egitim_bitis=son.isoformat())
    return UzunVade(sekil, izgara, b=b, mmin=mmin, rate_ust=rate_ust, ad=ad, metadata=meta)
