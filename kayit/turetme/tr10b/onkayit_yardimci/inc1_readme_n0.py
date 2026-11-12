# TR-10b ön kayıt sürüm 2, §10.4 "README modeli satırı" için önceden hesaplanan beklenti (İNCELEME-1 E2).
# Yalnız yapay gürültü: README "Noise model for Creepmeters" tablosundaki (n, A) ile güç yasası serisi
# (tr10b_sayim.pl_seri), uç ölçüsü (tr10b_sayim.dv_uc), tam maske, 2013 ızgarası. Hiçbir veri dosyası okunmaz.
#
# Kullanım (depo kökünden):
#   python3 -I -B kayit/turetme/tr10b/onkayit_yardimci/inc1_readme_n0.py <inc1 listeler.json> [çekiliş=1500] [tohum=99]
import json
import os
import re
import sys

import numpy as np

BURA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(BURA))
import tr10b_sayim as K  # noqa: E402

lj = sys.argv[1]
M = int(sys.argv[2]) if len(sys.argv) > 2 else 1500
tohum = int(sys.argv[3]) if len(sys.argv) > 3 else 99
C1 = 1.78

# README tablosu: tr10b_sayim.beklenti içindeki TAB'ın aynısı (kaynak metinden okunur; elle kopya yok)
src = open(os.path.join(os.path.dirname(BURA), "tr10b_sayim.py"), encoding="utf-8").read()
TAB = {k: (float(n), float(a)) for k, n, a in
       re.findall(r'\("([A-Z0-9]{4})", (\d\.\d\d), (\d+\.\d\d), -?\d+\.\d\)', src)}
assert len(TAB) == 18, TAB

d = json.load(open(lj, encoding="utf-8"))["sonuc"]
BU = d["INC1_listeler"]["B_U"]
BR2 = {(k, y) for k, y, *_ in d["INC1_listeler"]["B_R2"]}
R_sw = [(k, y) for k, y, *_ in BU if k in TAB]
print(f"B_U'da kodu README tablosunda olan istasyon-pencere: {len(R_sw)} (B_R2'de: {sum(1 for x in R_sw if x in BR2)});"
      f" istasyonlar: {sorted({k for k, _ in R_sw})}")

# yer-pencere alt kümesi R (veri öncesi; temsilci SAYIM ozet kuralıyla: en erken ilk gözlem, eşitlikte kod)
ist = d["INC1_ist"]
sp = {}
for k, y, tur, kes, site in sorted(BU, key=lambda x: (ist[x[0]]["ilk"], x[0])):
    sp.setdefault((site, y), k)
R_yp = sorted((k, y) for (site, y), k in sp.items() if k in TAB)
print(f"B_U yer-pencereleri {len(sp)}; temsilcisi README kodlu (R, veri öncesi üst sınır): {len(R_yp)};"
      f" T ≥ 2008 alt kümesi: {sum(1 for k, y in R_yp if y >= 2008)}")
print("   R dışında kalan README kodlu istasyon-pencereler (eş konumlu temsilci başka):",
      sorted(set(R_sw) - set(R_yp)))

P, n, i0, iH, iT = K.gunler(2013)
maske = np.ones(n, bool)
rng = np.random.default_rng(tohum)
dag = {}
for kod in sorted({k for k, _ in R_sw}):
    ust, A = TAB[kod]
    v = np.empty(M)
    for j in range(M):
        v[j] = abs(K.dv_uc(K.pl_seri(n, ust, A, rng, np), maske, i0, iH, iT, np)["dv"])
    dag[kod] = v
    print(f"  {kod} (n {ust:.2f}, A {A:.2f}): q50 {np.quantile(v, .5):.2f}  q95 {np.quantile(v, .95):.1f}")


def havuz(sw):
    h = np.concatenate([dag[k] for k, _ in sw])
    q50, q95 = np.quantile(h, [.5, .95])
    return q50, q95, q95 / C1, q95 / q50


for ad, sw in (("24 istasyon-pencere (B_U ∩ README kodu)", R_sw), (f"R yer-pencere ({len(R_yp)})", R_yp),
               ("R, T ≥ 2008", [x for x in R_yp if x[1] >= 2008])):
    q50, q95, b, kap = havuz(sw)
    print(f"{ad}: q50 {q50:.2f}; q95 {q95:.2f}; b* = q95 / {C1} = {b:.2f}; κ {kap:.2f}")
print(f"karşılaştırma: b ≈ 3 için q95 ≈ 3 × {C1} = {3 * C1:.2f} mm/yıl")

# README tablosunun B listesinde olmayan istasyonları (aynı üreteç akışının devamıyla; yukarıdaki sayıları değiştirmez):
# n > 2 olan 12 istasyonun q95 aralığı için
for kod in sorted(set(TAB) - set(dag)):
    ust, A = TAB[kod]
    v = np.array([abs(K.dv_uc(K.pl_seri(n, ust, A, rng, np), maske, i0, iH, iT, np)["dv"]) for _ in range(M)])
    dag[kod] = v
    print(f"  {kod} (n {ust:.2f}, A {A:.2f}): q50 {np.quantile(v, .5):.2f}  q95 {np.quantile(v, .95):.1f}")
q = {k: float(np.quantile(v, .95)) for k, v in dag.items()}
n2 = sorted(k for k in TAB if TAB[k][0] > 2.0)
print(f"n > 2 olan {len(n2)} istasyonun q95 aralığı: {min(q[k] for k in n2):.1f}–{max(q[k] for k in n2):.1f} mm/yıl;"
      f" n = 2 olanlarınki: {min(q[k] for k in TAB if TAB[k][0] == 2.0):.1f}–{max(q[k] for k in TAB if TAB[k][0] == 2.0):.1f}")
