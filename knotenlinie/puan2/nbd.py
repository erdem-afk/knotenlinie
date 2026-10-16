"""Negatif binom (NB2) sayı testi: V(Λ) = Λ + a·Λ²; Zechar 2010 δ1/δ2."""
from __future__ import annotations

import numpy as np
from scipy import stats

from knotenlinie.karsilastir.puan import PuanHatasi, n_testi


def varyans(toplam, a):
    if a < 0 or not np.isfinite(a):
        raise PuanHatasi('a >= 0 ve sonlu olmalı')
    return float(toplam + a * toplam * toplam)


def nbd_n_testi(toplam, n, *, a=None, varyans_degeri=None, alfa=0.05):
    """İki kuyruk: δ1=P(X>=N), δ2=P(X<=N); geçer ⇔ min >= alfa/2.

    ``a`` (NB2 aşırı yayılma) ya da doğrudan ``varyans_degeri`` verilir. V <= Λ ise
    Poisson'a düşer. pyCSEP ile aynı: upsilon=Λ/V, tau=Λ²/(V−Λ).
    """
    lam = float(toplam)
    if not np.isfinite(lam) or lam < 0 or int(n) != n or n < 0 or not 0 < alfa < 1:
        raise PuanHatasi('NBD N-testi girdisi geçersiz')
    if (a is None) == (varyans_degeri is None):
        raise PuanHatasi('a ya da varyans_degeri (biri) verilmeli')
    v = varyans(lam, a) if a is not None else float(varyans_degeri)
    if lam == 0 or v <= lam * (1 + 1e-15):
        p = n_testi(lam, n, alfa)
        return dict(beklenen=lam, N=int(n), varyans=lam, ust_kuyruk=p['ust_kuyruk'],
                    alt_kuyruk=p['alt_kuyruk'], gecti=p['gecti'], dagilim='poisson')
    tau = lam * lam / (v - lam)
    ups = lam / v
    ust = float(stats.nbinom.sf(n - 1, tau, ups))
    alt = float(stats.nbinom.cdf(n, tau, ups))
    return dict(beklenen=lam, N=int(n), varyans=v, ust_kuyruk=ust, alt_kuyruk=alt,
                gecti=bool(min(ust, alt) >= alfa / 2), dagilim='nbd', tau=float(tau), upsilon=float(ups))


def pencere_sayimlari(zaman_gun, baslangic_gun, bitis_gun, uzunluk_gun, kayma_gun=30):
    """Olay günleri (gün numarası, float) için kayan pencere sayıları.

    Pencere i: [b_i, b_i+uzunluk), b_i = baslangic + kayma·i, b_i + uzunluk <= bitis.
    """
    t = np.sort(np.asarray(zaman_gun, float))
    bas = np.arange(baslangic_gun, bitis_gun - uzunluk_gun + 1e-9, kayma_gun)
    if len(bas) < 2:
        raise PuanHatasi('Dağılım kestirimi için en az iki pencere gerekir')
    return (np.searchsorted(t, bas + uzunluk_gun, side='left') -
            np.searchsorted(t, bas, side='left')).astype(float)


def a_kestir(sayimlar):
    """KURAL.md §1: a = max(0, (v − m)/m²), v ddof=1."""
    x = np.asarray(sayimlar, float)
    if len(x) < 2:
        raise PuanHatasi('En az iki pencere gerekir')
    m, v = float(x.mean()), float(x.var(ddof=1))
    if m <= 0:
        return dict(a=0.0, ortalama=m, varyans=v, pencere=int(len(x)), not_='ortalama 0')
    return dict(a=max(0.0, (v - m) / (m * m)), ortalama=m, varyans=v, pencere=int(len(x)),
                vmr=v / m)
