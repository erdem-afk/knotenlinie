"""s1_puan.py'den p_bw (aynı tanım)."""
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

