"""S1 puanlama (kural S1-S6-KURAL.md + Ek 1). Önce ateşleme kapısı (yalnız geometriden), sonra tek koşu.
Kullanım: python3 s1_puan.py envanter.json cikti.json
"""
import json, sys, math
import numpy as np
rng = np.random.default_rng(20261110)
BINS = [(10, 2.7), (20, 1.35), (30, 1.3), (40, 0.1), (1e9, 0.08)]  # θ<10→5°, [10,20)→15°, … ≥40→45°
R0 = 0.46

def p_bw(g, kirp=(0.02, 0.98)):
    if g["tur"] == "basamak":
        pr = max(0.0, 1.89 - 0.31 * g["d_km"])
    elif g["tur"] == "bukum":
        pr = next(v for ust, v in BINS if g["aci"] < ust)
    elif g["tur"] == "mekanizma":
        return min(max(4 / 75, kirp[0]), kirp[1])
    p = pr / (1 + pr)
    return min(max(p, kirp[0]), kirp[1])

def ll(p, y):
    return math.log(p if y else 1 - p)

env = json.load(open(sys.argv[1]))
G = [(e["olay"], g) for e in env for g in e["gecitler"] if g.get("puan", True) and g["tur"] in ("basamak", "bukum", "mekanizma")]
olaylar = sorted({o for o, _ in G})
print("puanlanan geçit:", len(G), " geçti:", sum(g["gecti"] for _, g in G), " durdu:", sum(not g["gecti"] for _, g in G), " olay:", len(olaylar))

# --- ateşleme kapısı: sonuçlar BW'den çekilir (BW doğru varsayımı), olay bloklu SE ---
def dL(sonuc):
    per = {o: 0.0 for o in olaylar}
    for (o, g), y in zip(G, sonuc):
        per[o] += ll(p_bw(g), y) - ll(R0, y)
    return per
sim = []
for _ in range(4000):
    y = [rng.random() < p_bw(g) for _, g in G]
    sim.append(sum(dL(y).values()))
sim = np.array(sim)
beklenen, se = float(sim.mean()), float(sim.std())
kapi = "ACIK" if beklenen >= 2 * se else "KAPALI (önceden ayırt edilemez)"
print(f"ateşleme kapısı: beklenen ΔL {beklenen:.2f} nat, SE {se:.2f} → {kapi}")

# --- tek koşu ---
y = [g["gecti"] for _, g in G]
per = dL(y); top = sum(per.values())
bs = []
for _ in range(10000):
    secim = rng.choice(olaylar, len(olaylar))
    bs.append(sum(per[o] for o in secim))
lo, hi = np.percentile(bs, [2.5, 97.5])
print(f"ΔL = L(BW) − L(R0) = {top:.2f} nat; geçit başına {top/len(G):.3f}; olay bloklu %95 [{lo:.2f}, {hi:.2f}]")
for o in olaylar: print("   ", o, round(per[o], 2))
# bilgi satırları
alt = {}
for tur in ("basamak", "bukum"):
    for gec in (True, False):
        s_ = [ll(p_bw(g), g["gecti"]) - ll(R0, g["gecti"]) for _, g in G if g["tur"] == tur and g["gecti"] == gec]
        alt[f"{tur}_{'gecti' if gec else 'durdu'}"] = {"n": len(s_), "dL": round(sum(s_), 2)}
print("alt kırılım (bilgi):", alt)
kal = []
for a, b in ((0, .2), (.2, .5), (.5, .8), (.8, 1.01)):
    s_ = [(p_bw(g), g["gecti"]) for _, g in G if a <= p_bw(g) < b]
    if s_: kal.append({"kutu": f"{a}-{b}", "n": len(s_), "beklenen_gecis": round(sum(p for p, _ in s_), 2), "gozlenen_gecis": sum(v for _, v in s_)})
print("kalibrasyon (bilgi):", kal)
r1 = sum(y) / len(y)
L_r1 = sum(ll(r1, v) for v in y); L_bw = sum(ll(p_bw(g), g["gecti"]) for _, g in G)
print(f"R1 (örneklem içi oran {r1:.2f}) − BW: {L_r1 - L_bw:.2f} nat (bilgi)")
duy = {}
for k in ((0.01, 0.99), (0.05, 0.95)):
    duy[str(k)] = round(sum(ll(p_bw(g, k), g["gecti"]) - ll(R0, g["gecti"]) for _, g in G), 2)
print("kırpma duyarlılığı (bilgi):", duy)
json.dump({"n": len(G), "olay": olaylar, "kapi": {"beklenen": beklenen, "se": se, "durum": kapi},
           "dL": top, "ci95": [float(lo), float(hi)], "olay_basina": per, "alt": alt, "kalibrasyon": kal,
           "R1_eksi_BW": L_r1 - L_bw, "kirpma": duy}, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
