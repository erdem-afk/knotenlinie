# TR-10b ön kayıt sürüm 2: İNCELEME-1 K1, K3, Ö4 ve K8 düzeltmelerinin getirdiği küçük sayıların yeniden üretimi.
# Yalnız aritmetik ve yapay seri; hiçbir veri dosyası okunmaz.
#
# Kullanım (depo kökünden):
#   python3 -I -B kayit/turetme/tr10b/onkayit_yardimci/inc1_kucuk_hesap.py
import math
import os
import sys

import numpy as np

BURA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(BURA))
import tr10b_sayim as K  # noqa: E402

EPOK = (1973, 1978, 1998, 2003, 2008, 2013, 2018)

# Ö4: Chihshang r_c, ön kaydın r tanımıyla (payda pencere ortalama hızı: taban 3 y, yakın 2 y ağırlıklı)
v5 = (3 * 22 + 2 * 14) / 5
print(f"Ö4: v5 = (3·22 + 2·14)/5 = {v5:.1f} mm/yıl; r_c = −8 / {v5:.1f} = {-8 / v5:.4f}; (−8/22 = {-8 / 22:.4f})")

# K3: κ'nın Gauss değeri ve 4000 çekilişlik q95'in MC hatası (|N(0, σ)|, σ = c1 / 1,96)
z95, z75 = 1.959964, 0.6744898
print(f"K3: κ_Gauss = {z95} / {z75} = {z95 / z75:.4f}")
sig = 1.78 / z95
f = 2 * math.exp(-z95 ** 2 / 2) / math.sqrt(2 * math.pi) / sig
for n in (4000, 100000):
    se = math.sqrt(0.95 * 0.05 / n) / f
    print(f"    q95 MC hatası, {n} çekiliş: ±{se:.4f}" + (f"; 1,732 sapması {(1.7789 - 1.732) / se:.2f} sd (1,7789'a göre)"
                                                         if n == 4000 else ""))

# K1 (a3), (a4) ve ρ eklemenin deterministik sınırı
print("\nK1 (a3) medyan denetimi, (a4) gün kayması denetimi (tam maske, günlük katman):")
for Y in EPOK:
    P, n, i0, iH, iT = K.gunler(Y)
    t2, t3 = (iT - iH) / 365.25, (iH - i0) / 365.25
    m = np.ones(n, bool)
    x = np.full(n, 3.0); x[iT] = 503.0
    a3 = K.dv_uc(x, m, i0, iH, iT, np)["dv"]
    ort = lambda i: float(np.mean(x[i - 15:i + 16]))
    a3_ort = (ort(iT) - ort(iH)) / t2 - (ort(iH) - ort(i0)) / t3
    g = np.arange(n)
    a4a = K.dv_uc(10.0 * (g >= iH), m, i0, iH, iT, np)["dv"]
    a4b = K.dv_uc(10.0 * (g >= iH + 1), m, i0, iH, iT, np)["dv"]
    r_g = 5 * 15 / 365.25
    r_10 = 5 * (15 + 143 / 144) / 365.25
    alt = lambda r: 5 - 2 * r / t2 - r / t3
    print(f"  {Y}: a3 medyan {a3:+.2e}, ortalamayla {a3_ort:.3f}; a4 hata {abs(a4a + 10 / t3):.1e} / "
          f"{abs(a4b - 10 / t2):.1e} (değerler {a4a:.4f}, {a4b:.4f}); ρ günlük ≤ {r_g:.4f} → "
          f"[{alt(r_g):.4f}, {5 + r_g / t2:.4f}]; 10MIN satırına eklenirse ρ ≤ {r_10:.4f} → alt {alt(r_10):.4f}")

# K8: 10MIN'de günde 144 satır (aynı günlük değere ±0,01 mm beyaz gürültü), günlük medyan → Δv;
# günde bir satırlık yazımla fark
rng = np.random.default_rng(20261112)
for Y in (2013, 1978):
    P, n, i0, iH, iT = K.gunler(Y)
    m = np.ones(n, bool)
    en = {"gauss sd 0,01": 0.0, "düzgün ±0,01": 0.0}
    for _ in range(300):
        x = K.pl_seri(n, 2.0, 3.0, rng, np) + 0.1 * rng.standard_normal(n)
        d1 = K.dv_uc(x, m, i0, iH, iT, np)["dv"]
        for ad, gur in (("gauss sd 0,01", lambda: 0.01 * rng.standard_normal((n, 144))),
                        ("düzgün ±0,01", lambda: rng.uniform(-0.01, 0.01, (n, 144)))):
            xg = np.median(x[:, None] + gur(), axis=1)
            en[ad] = max(en[ad], abs(K.dv_uc(xg, m, i0, iH, iT, np)["dv"] - d1))
    print(f"K8 {Y}: 144 satır/gün ile günde bir satır arasındaki en büyük |Δv farkı| (300 seri):",
          {k: round(v, 5) for k, v in en.items()}, "eşik 0,005")
