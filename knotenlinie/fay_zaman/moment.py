"""Moment dengesi ve büyüklük dağılımları (karakteristik YC85-tipi, kesik GR).

Ṁ₀ = μ·A·ṡ (N m/yıl). Büyüklük yoğunluğu f(m) = c·exp(−β m) parçalarından
oluşur; ölçek S, ∫ S·f(m)·M₀(m) dm = Ṁ₀ olacak biçimde seçilir (bütün moment
[m_alt, m_ust] aralığındaki olaylarla taşınır, bağlaşım ortak parametredir).
M₀(m) = 10^(1,5 m + 9,05) (Hanks–Kanamori 1979).
"""
from __future__ import annotations

import numpy as np

MU_PA = 3e10
LN10 = np.log(10.0)
M0_SABIT = 9.05


class MomentHatasi(ValueError):
    """Moment/MFD girdisi geçersiz."""


def moment_hizi(alan_km2, kayma_mm_yil, mu_pa=MU_PA, baglasim=1.0):
    """Ṁ₀ = baglasim·μ·A·ṡ, N m/yıl (A km², ṡ mm/yıl)."""
    a, s = float(alan_km2), float(kayma_mm_yil)
    if not (np.isfinite(a) and np.isfinite(s)) or a <= 0 or s < 0:
        raise MomentHatasi('alan pozitif, kayma negatif olmayan olmalı')
    return float(baglasim) * mu_pa * (a * 1e6) * (s * 1e-3)


def m0(m):
    return 10.0 ** (1.5 * np.asarray(m, float) + M0_SABIT)


def parcalar(tur, m_alt, m_ust, b, karakteristik_genislik=0.5, duz_alt=1.5):
    """Yoğunluk parçaları [(lo, hi, c, beta)], f = c·exp(−beta·m).

    'gr': kesik GR, beta = b ln10. 'kar': YC85-tipi — Mmax−duz_alt altında GR(b);
    Mmax−duz_alt … Mmax arası, GR'nin Mmax−duz_alt noktasındaki yoğunluğunda
    düz (karakteristik bölge Mmax−genişlik … Mmax bunun içindedir; basitleştirme:
    süreklilik kuralı, YC85'in tam sabitleri değil).
    """
    if not (np.isfinite(m_alt) and np.isfinite(m_ust)) or m_ust <= m_alt:
        raise MomentHatasi('m_ust > m_alt gerekli')
    if not np.isfinite(b) or b <= 0:
        raise MomentHatasi('b pozitif olmalı')
    beta = b * LN10
    if tur == 'gr':
        return [(m_alt, m_ust, 1.0, beta)]
    if tur == 'kar':
        mp = m_ust - duz_alt
        if mp <= m_alt:
            return [(m_alt, m_ust, 1.0, 0.0)]
        c_duz = np.exp(-beta * mp)
        return [(m_alt, mp, 1.0, beta), (mp, m_ust, c_duz, 0.0)]
    raise MomentHatasi('bilinmeyen MFD türü')


def _int_exp(kappa, lo, hi):
    lo, hi = np.asarray(lo, float), np.asarray(hi, float)
    if abs(kappa) < 1e-12:
        return hi - lo
    return (np.exp(kappa * hi) - np.exp(kappa * lo)) / kappa


def parca_integral(parca, lo, hi, agirlik='sayi'):
    """Parça üzerinde [lo,hi] ∩ parça aralığı integrali; 'sayi' ∫f, 'moment' ∫f·M₀."""
    a, b_, c, beta = parca
    lo = np.clip(np.asarray(lo, float), a, b_)
    hi = np.clip(np.asarray(hi, float), a, b_)
    hi = np.maximum(hi, lo)
    if agirlik == 'sayi':
        return c * _int_exp(-beta, lo, hi)
    return c * 10.0 ** M0_SABIT * _int_exp(1.5 * LN10 - beta, lo, hi)


def olcek(parca_listesi, mdot):
    """S: ∫ S·f·M₀ dm = Ṁ₀."""
    tum = sum(float(parca_integral(p, p[0], p[1], 'moment')) for p in parca_listesi)
    if tum <= 0:
        raise MomentHatasi('moment integrali sıfır')
    return float(mdot) / tum


def kutu_sayilari(parca_listesi, S, kenarlar, lo=None, hi=None):
    """[kenar_i, kenar_{i+1}) ∩ [lo,hi] kutu başına yıllık olay sayısı."""
    k = np.asarray(kenarlar, float)
    alt = k[:-1].copy()
    ust = np.where(np.isfinite(k[1:]), k[1:], 1e3)
    if lo is not None:
        alt = np.maximum(alt, lo)
    if hi is not None:
        ust = np.minimum(ust, hi)
    ust = np.maximum(ust, alt)
    out = np.zeros(len(alt))
    for p in parca_listesi:
        out += parca_integral(p, alt, ust, 'sayi')
    return S * out
