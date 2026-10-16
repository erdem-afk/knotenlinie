"""Weichert (1980) GR kestiricisi ve dönemsel tamlık (Stepp 1972).

Deney Z2, Z'nin kesik GR oranını uzun bir kümesizleştirilmiş katalogdan Weichert
(1980) ile kestirir. Weichert kestiricisi eşit olmayan tamlık dönemlerini
ayrık büyüklük kutuları üzerinden Poisson olabilirliğiyle birleştirir:

    n_i ~ Poisson(A * T_i * q_i(b)),   q_i(b) = 10^(-b(m_i-m1)) - 10^(-b(m_{i+1}-m1))

Burada `T_i` i'inci kutunun gözlenebilir olduğu **etkin süre**dir: tamlık eşiği
`Mc <= m_i` olan dönemlerin süreleri toplamı. `A` m1 eşiğindeki yıllık orandır;
profilli MLE `A = N / sum(T_i q_i(b))` ile b üzerinde tek boyutlu aramaya iner.
Tamlık eşikleri 0,1 ızgarasında olduğundan bir kutuya düşen her gözlem o kutunun
etkin süresine girer; kutu/olay uyuşmazlığı yoktur.

Dönemsel tamlık tablosu birincil olarak yayımlanmış CPTI/Stucchi tablosudur
(`CPTI_TAMLIK`); `stepp_tamlik` aynı tabloyu veriden kestiren Stepp (1972)
referans-pencere yedeğidir. `sikilastir` Z2 duyarlılık (ii) için tabloyu bir
kademe sıkılaştırır.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar
from scipy.special import xlogy

#: Yayımlanmış CPTI tamlık tablosu: (baslangic_yil, bitis_yil_haric, Mc).
#: Kaynak atfı Stucchi ve ark. (2011) / CPTI11 MPS04 tamlık çizelgesi; records/Z2/KURAL.md.
CPTI_TAMLIK = (
    (1000, 1348, 6.5),
    (1348, 1450, 6.1),
    (1450, 1500, 5.7),
    (1500, 1600, 5.5),
    (1600, 1750, 5.3),
    (1750, 1850, 5.0),
    (1850, 1870, 4.7),
    (1870, 1900, 4.5),
    (1900, 1940, 4.3),
    (1940, 1970, 4.1),
    (1970, 1980, 4.0),
    (1980, 2400, 3.5),
)

DM = 0.1


class WeichertHatasi(ValueError):
    """Weichert/Stepp girdisi veya tablosu geçersiz."""


def tablo_dogrula(tablo):
    """Dönem tablosu: artan, örtüşmeyen, Mc sonlu."""
    t = [(float(a), float(b), float(mc)) for a, b, mc in tablo]
    if not t:
        raise WeichertHatasi('tamlık tablosu boş')
    for i, (a, b, mc) in enumerate(t):
        if not (b > a) or not np.isfinite(mc):
            raise WeichertHatasi(f'dönem geçersiz: {a}-{b} Mc={mc}')
        if i and a < t[i - 1][1]:
            raise WeichertHatasi('tamlık dönemleri örtüşüyor')
    return t


def mc_ata(tablo, yil):
    """Her olayın yılına düşen dönem Mc'si; tablo dışı NaN."""
    t = tablo_dogrula(tablo)
    y = np.asarray(yil, float)
    mc = np.full(y.shape, np.nan)
    for a, b, m in t:
        sec = (y >= a) & (y < b)
        mc[sec] = m
    return mc


def etkin_sure(tablo, kenarlar, *, bas, son):
    """Kutu başına etkin yıl: Mc <= kutu alt kenarı olan dönemlerin süresi."""
    t = tablo_dogrula(tablo)
    k = np.asarray(kenarlar, float)
    if k.ndim != 1 or len(k) < 2:
        raise WeichertHatasi('büyüklük kenarları geçersiz')
    T = np.zeros(len(k) - 1)
    for a, b, mc in t:
        a, b = max(a, float(bas)), min(b, float(son) + 1)
        if b <= a:
            continue
        ic = k[:-1] >= mc - 1e-9
        T[ic] += b - a
    return T


def _kutular(mw, kenarlar):
    k = np.asarray(kenarlar, float)
    i = np.searchsorted(k, mw, side='right') - 1
    return i


def _q(b, kenarlar):
    k = np.asarray(kenarlar, float)
    m1 = k[0]
    return 10.0 ** (-b * (k[:-1] - m1)) - 10.0 ** (-b * (k[1:] - m1))


def weichert_mle(mw, yil, tablo, *, kenarlar, bas=None, son=None, b_sinir=(0.2, 2.5)):
    """Eşit olmayan tamlıkta Weichert (1980) profilli Poisson MLE.

    Döner: b, A (m1 yıllık oranı), oran_mref (mref=4.95), N, kutular, T.
    """
    t = tablo_dogrula(tablo)
    k = np.asarray(kenarlar, float)
    mw = np.asarray(mw, float)
    yil = np.asarray(yil, float)
    if not np.isfinite(mw).all() or not np.isfinite(yil).all():
        raise WeichertHatasi('mw/yıl sonlu olmalı')
    bas = float(t[0][0]) if bas is None else float(bas)
    son = float(son) if son is not None else min(b for _, b, _ in t) - 1
    mc = mc_ata(t, yil)
    ic = np.isfinite(mc) & (mw >= mc)
    if ic.sum() < 10:
        raise WeichertHatasi('tam gözlem az')
    idx = _kutular(mw[ic], k)
    n = np.bincount(idx, minlength=len(k) - 1).astype(float)
    T = etkin_sure(t, k, bas=bas, son=son)

    def nll(b):
        p = _q(b, k)
        den = float(np.sum(T * p))
        if den <= 0:
            return np.inf
        A = float(n.sum()) / den
        lam = A * T * p
        return float(np.sum(lam - xlogy(n, lam)))

    fit = minimize_scalar(nll, bounds=tuple(b_sinir), method='bounded',
                          options={'xatol': 1e-12})
    b = float(fit.x)
    p = _q(b, k)
    A = float(n.sum()) / float(np.sum(T * p))
    return dict(b=b, A=A, m1=float(k[0]), oran_mref=float(A * 10.0 ** (-b * (4.95 - k[0]))),
                N=int(n.sum()), n=n.tolist(), T=T.tolist(), b_sinirda=bool(
                    min(b - b_sinir[0], b_sinir[1] - b) < 1e-3),
                yontem='Weichert (1980) kutulu profilli Poisson MLE')


def stepp_tamlik(yil, mw, son, *, m_esikler=(4.5, 5.0, 5.5, 6.0, 6.5),
                 ref=20, adim=5, z=1.0, en_az_yil=40, en_az_olay=8):
    """Stepp (1972) referans-pencere yedeği; eşik başına tamlık başlangıcı.

    Referans, `son-ref..son` penceresinin yıllık oranıdır. Her aday başlangıç
    için `[t0, son]` oranı referansla Poisson birleşik z'siyle karşılaştırılır;
    |z|<=z olan en erken t0 alınır. Eşikler büyükten küçüğe sıralanır ve daha
    büyük M'nin tamlığı daha erken olamaz kuralı uygulanır. Durağan hız
    varsayımı veride bozulursa tablo kararsızdır; bu yedek bir tanıdır.
    """
    y = np.asarray(yil, float)
    m = np.asarray(mw, float)
    if not np.isfinite(y).all() or not np.isfinite(m).all():
        raise WeichertHatasi('Stepp girdisi sonlu olmalı')
    if ref <= 0 or adim <= 0 or not 0 < z:
        raise WeichertHatasi('Stepp parametreleri geçersiz')
    son = float(son)
    sonuc = {}
    for thr in sorted(m_esikler, reverse=True):
        yy = y[m >= thr]
        if len(yy) < en_az_olay:
            sonuc[thr] = None
            continue
        nref = int(((yy > son - ref) & (yy <= son)).sum())
        if nref < 3:
            sonuc[thr] = None
            continue
        lam = nref / ref
        se_ref = np.sqrt(nref) / ref
        bulundu = None
        for t0 in range(int(np.floor(yy.min())), int(son - en_az_yil) + 1, adim):
            n = int(((yy >= t0) & (yy <= son)).sum())
            T = son + 1 - t0
            l = n / T
            se = np.sqrt(n) / T
            zz = (l - lam) / np.sqrt(se * se + se_ref * se_ref)
            if abs(zz) <= z:
                bulundu = t0
                break
        sonuc[thr] = bulundu
    # Daha büyük eşik daha erken tam olur: t0 büyükten küçüğe artmayan olmalı.
    esikler = sorted([t for t in m_esikler if sonuc.get(t) is not None], reverse=True)
    if not esikler:
        raise WeichertHatasi('Stepp hiçbir eşikte tamlık bulamadı')
    baslangic = []
    onceki = None
    for thr in esikler:
        t0 = sonuc[thr]
        if onceki is not None:
            t0 = min(t0, onceki)
        baslangic.append(t0)
        onceki = t0
    out = []
    for j, (thr, t0) in enumerate(zip(esikler, baslangic)):
        bit = baslangic[j - 1] if j > 0 else son + 1
        if bit > t0:
            out.append((float(t0), float(bit), float(thr)))
    return out


def sikilastir(tablo, kademe=0.5):
    """Her dönem Mc'sini bir kademe yükselt (Z2 duyarlılık ii)."""
    t = tablo_dogrula(tablo)
    return [(a, b, mc + kademe) for a, b, mc in t]


def gk74_mask(yil, enlem, boylam, derinlik, mw, *, simetrik=True, gun_yil=365.25):
    """Gardner–Knopoff (1974) arka plan maskesi, girdi sırasına göre.

    Z'nin `kumesiz._mainshock_penceresi` mantığının aynısı; tek fark zaman
    eksenidir. CPTI15 1005'te başlar ve pandas nanosecond aralığı 1678'de
    başladığından gerçek takvim zamanı kurulamaz; zaman kesirli yıl × 365,25
    gün olarak alınır. GK74 pencereleri gün–yıl düzeyinde olduğundan bu
    yaklaşım pencereyi değiştirmez. Pencereler `kumesiz.pencere`den gelir.
    """
    from scipy.spatial import cKDTree

    from .kumesiz import pencere, yerel_km

    y = np.asarray(yil, float)
    la = np.asarray(enlem, float)
    lo = np.asarray(boylam, float)
    z = np.asarray(derinlik, float)
    m = np.asarray(mw, float)
    if not (np.isfinite(y).all() and np.isfinite(la).all() and np.isfinite(lo).all()
            and np.isfinite(z).all() and np.isfinite(m).all()):
        raise WeichertHatasi('gk74 girdisi sonlu olmalı')
    sira = np.argsort(y, kind='stable')
    y, la, lo, z, m = y[sira], la[sira], lo[sira], z[sira], m[sira]
    n = len(y)
    if n == 0:
        return np.zeros(0, bool)
    t = (y - y[0]) * float(gun_yil)
    x, yy = yerel_km(la, lo)
    dt, dr = pencere('gk74', m)
    agac = cKDTree(np.column_stack([x, yy]))
    silindi = np.zeros(n, bool)
    for i in np.argsort(-m, kind='stable'):
        if silindi[i]:
            continue
        idx = np.asarray(agac.query_ball_point([x[i], yy[i]], float(dr[i])), int)
        idx = idx[idx != i]
        if idx.size == 0:
            continue
        fark = t[idx] - t[i]
        zaman_ok = np.abs(fark) < dt[i] if simetrik else ((fark > 0) & (fark < dt[i]))
        dx = x[idx] - x[i]
        dy = yy[idx] - yy[i]
        dz = z[idx] - z[i]
        uzak_ok = np.sqrt(dx * dx + dy * dy + dz * dz) < dr[i]
        sec = zaman_ok & uzak_ok & (m[idx] < m[i]) & (~silindi[idx])
        silindi[idx[sec]] = True
    arka = ~silindi
    out = np.empty(n, bool)
    out[sira] = arka
    return out


def tablo_araligi(tablo, bas, son):
    """Dönem tablosunu [bas, son] aralığına kırp ve sırala."""
    t = tablo_dogrula(tablo)
    out = []
    for a, b, mc in t:
        aa, bb = max(a, float(bas)), min(b, float(son) + 1)
        if bb > aa:
            out.append((aa, bb, mc))
    return out
