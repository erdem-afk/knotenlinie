"""Moment koruyan kesik GR ve fay üst kenarından hücreye Gauss yayılımı."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.special import ndtr

KM_DERECE = np.pi * 6371.0 / 180.0
MU_PA = 30e9
YIL_SANIYE = 365.25 * 86400.0


def _pozitif(x, ad, sifir=False):
    x = np.asarray(x, dtype=float)
    if not np.isfinite(x).all() or np.any(x < 0 if sifir else x <= 0):
        raise ValueError(f"{ad}: sonlu ve {'negatif olmayan' if sifir else 'pozitif'} olmalı")
    return x


def moment_hizi(alan_km2, kayma_mm_yil, mu_pa=MU_PA):
    """µ [Pa] × A [km²→m²] × v [mm/yıl→m/yıl], N m/yıl."""
    return (_pozitif(alan_km2, 'alan') * _pozitif(kayma_mm_yil, 'kayma', True)
            * _pozitif(mu_pa, 'modül') * 1e3)


def kenarlar_dogrula(kenarlar):
    k = np.asarray(kenarlar, dtype=float)
    if (k.ndim != 1 or len(k) < 2 or not np.isfinite(k[:-1]).all()
            or np.isnan(k[-1]) or k[-1] == -np.inf or np.any(np.diff(k) <= 0)):
        raise ValueError('büyüklük kenarları kesin artan olmalı; yalnız son +inf olabilir')
    return k


def _integral(egim, alt, ust):
    """∫ exp(egim x) dx; egim=0 analitik limiti."""
    if abs(egim) < 1e-12:
        return ust - alt
    return np.exp(egim * alt) * np.expm1(egim * (ust - alt)) / egim


def gr_oranlari(mdot, m_kenarlar, mmax, *, b=1.0, mmin=2.4):
    """Her kutuda yıllık sayı; tüm [mmin,mmax] momenti mdot'a eşittir.

    Alt eşik bağımsızdır: istenen kutular dışındaki küçük olayların momenti
    gözlenen kutulara yeniden dağıtılmaz. Üst sınır sert kesiktir.
    """
    k = kenarlar_dogrula(m_kenarlar)
    mdot = float(_pozitif(mdot, 'moment', True))
    if not np.isfinite([mmax, mmin, b]).all() or mmax <= mmin or b < 0:
        raise ValueError('mmax > mmin ve b >= 0 gerekli')
    alt = np.clip(k[:-1], mmin, mmax) - mmin
    ust = np.clip(k[1:], mmin, mmax) - mmin
    beta = b * np.log(10.0)
    payda = 10.0 ** (1.5 * mmin + 9.1) * _integral(
        (1.5 - b) * np.log(10.0), 0.0, mmax - mmin)
    return mdot * _integral(-beta, alt, ust) / payda


def izgara_dogrula(izgara):
    cols = ['boylam_min', 'boylam_max', 'enlem_min', 'enlem_max']
    a = izgara[cols].to_numpy(dtype=float)
    if (len(a) == 0 or not np.isfinite(a).all() or np.any(a[:, 0] >= a[:, 1])
            or np.any(a[:, 2] >= a[:, 3]) or np.any(np.abs(a[:, :2]) > 180)
            or np.any(np.abs(a[:, 2:]) >= 90)):
        raise ValueError('ızgara: geçersiz dikdörtgen')
    # Aynı kütleyi iki kez sayacak örtüşen hücreleri reddet.
    for i, r in enumerate(a):
        s = a[i + 1:]
        if np.any((s[:, 0] < r[1] - 1e-10) & (s[:, 1] > r[0] + 1e-10)
                  & (s[:, 2] < r[3] - 1e-10) & (s[:, 3] > r[2] + 1e-10)):
            raise ValueError('ızgara hücreleri örtüşüyor')
    return a


def iz_ornekle(iz, adim_km=2.0):
    """MultiLineString koordinatlarını uzunluk ağırlıklı segment orta noktalarına ayır."""
    _pozitif(adim_km, 'adım')
    noktalar, agirliklar = [], []
    for parca in iz:
        c = np.asarray(parca, dtype=float)
        if c.ndim != 2 or c.shape[1] != 2 or len(c) < 2 or not np.isfinite(c).all():
            raise ValueError('fay izi geçersiz')
        if np.any(np.abs(c[:, 0]) > 180) or np.any(np.abs(c[:, 1]) >= 90):
            raise ValueError('fay izi koordinatı geçersiz')
        for a, z in zip(c[:-1], c[1:]):
            uzunluk = KM_DERECE * np.hypot((z[0] - a[0]) * np.cos(np.deg2rad((a[1]+z[1])/2)), z[1]-a[1])
            if uzunluk <= 0:
                continue
            n = max(1, int(np.ceil(uzunluk / adim_km)))
            noktalar.extend(a + ((np.arange(n)+0.5)/n)[:, None] * (z-a))
            agirliklar.extend([uzunluk/n]*n)
    if not noktalar:
        raise ValueError('fay izi sıfır uzunlukta')
    w = np.asarray(agirliklar)
    return np.asarray(noktalar), w / w.sum(), float(w.sum())


def gauss_kutular(noktalar, agirliklar, izgara, sigma_km, *, dogrulanmis=False):
    """Hücre integral ağırlıkları; bölge dışına giden kuyruk geri normalleştirilmez."""
    a = izgara if dogrulanmis else izgara_dogrula(izgara)
    p = np.asarray(noktalar, dtype=float)
    w = _pozitif(agirliklar, 'nokta ağırlıkları', True)
    _pozitif(sigma_km, 'sigma')
    if (p.ndim != 2 or p.shape[1] != 2 or len(p) != len(w) or w.ndim != 1
            or not np.isfinite(p).all() or np.any(np.abs(p[:, 0]) > 180)
            or np.any(np.abs(p[:, 1]) >= 90)):
        raise ValueError('nokta/ağırlık boyutu geçersiz')
    sonuc = np.zeros(len(a))
    for j in range(0, len(p), 64):
        q = p[j:j+64]
        sx = sigma_km / (KM_DERECE * np.cos(np.deg2rad(q[:, 1])))
        sy = sigma_km / KM_DERECE
        x = (ndtr((a[None, :, 1]-q[:, None, 0])/sx[:, None])
             - ndtr((a[None, :, 0]-q[:, None, 0])/sx[:, None]))
        y = (ndtr((a[None, :, 3]-q[:, None, 1])/sy)
             - ndtr((a[None, :, 2]-q[:, None, 1])/sy))
        sonuc += w[j:j+64] @ (x*y)
    return sonuc


def yillik(faylar, izgara, m_kenarlar, *, sigma_km=10.0, b=1.0, mmin=2.4, mu_pa=MU_PA):
    """Fay tablosu: id, iz, alan_km2, kayma_mm_yil, mmax; CSS+ISS birlikte yok."""
    a = izgara_dogrula(izgara)
    k = kenarlar_dogrula(m_kenarlar)
    if faylar['id'].duplicated().any():
        raise ValueError('tekrarlanan fay kimliği')
    if 'katman' in faylar and len(set(faylar['katman'])) > 1:
        raise ValueError('CSS+ISS toplamı çift sayım: tek katman seçin')
    sonuc = np.zeros((len(a), len(k)-1))
    for r in faylar.itertuples(index=False):
        p, w, _ = iz_ornekle(r.iz)
        uzay = gauss_kutular(p, w, a, sigma_km, dogrulanmis=True)
        oran = gr_oranlari(moment_hizi(r.alan_km2, r.kayma_mm_yil, mu_pa), k,
                          r.mmax, b=b, mmin=mmin)
        sonuc += uzay[:, None] * oran[None, :]
    return sonuc


def karisim(taban, fay, agirlik, *, toplam_esitle=False):
    """Konveks karışım; isteğe bağlı şekil deneyi tabanın toplamını korur."""
    a = _pozitif(taban, 'taban', True)
    f = _pozitif(fay, 'fay', True)
    if a.shape != f.shape or not np.isfinite(agirlik) or not 0 <= agirlik <= 1:
        raise ValueError('karışım şekli/ağırlığı geçersiz')
    if agirlik == 0:
        return a.copy()
    if toplam_esitle:
        if f.sum() <= 0:
            raise ValueError('fay toplamı sıfır')
        f = f * (a.sum()/f.sum())
    return (1-agirlik)*a + agirlik*f
