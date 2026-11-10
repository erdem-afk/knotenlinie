"""S6 sentetik çözünürlük testi (kural S1-S6-KURAL.md, sha 167ef5b4…).
İki segment, 1000 yıl, segment başına tekrar 250 yıl (Poisson). Ortak kırılma payı f.
Ortak olmayan olayların %20'sine 0–30 yıl içinde komşu segmentte tetiklenmiş eş eklenir.
Türbidit yaşlarına N(0, σ) hata. Eşzamanlı: |Δt| < 2σ√2. f=0,1 ile f=0,5 olabilirlik oranı
testi (eşzamanlı çift sayısı istatistiği, sıfır dağılımı f=0,1 simülasyonundan), α=0,05, güç.
"""
import numpy as np
rng = np.random.default_rng(20261110)
T, TR, PTET = 1000.0, 250.0, 0.20

def katalog(f):
    # toplam segment-olay oranı 1/TR her segmentte; ortak olaylar iki segmentte birden sayılır
    lam_ortak = f / TR
    lam_tek = (1 - f) / TR
    ortak = rng.uniform(0, T, rng.poisson(lam_ortak * T))
    a = list(ortak); b = list(ortak)
    for seg, other in ((a, b), (b, a)):
        tek = rng.uniform(0, T, rng.poisson(lam_tek * T))
        seg.extend(tek)
        for t in tek:
            if rng.random() < PTET:
                other.append(t + rng.uniform(0, 30))
    return np.array(a), np.array(b)

def es_sayisi(a, b, s):
    a = a + rng.normal(0, s, len(a)); b = b + rng.normal(0, s, len(b))
    esik = 2 * s * np.sqrt(2)
    used = set(); n = 0
    for t in a:
        d = np.abs(b - t); d[list(used)] = np.inf if used else d[list(used)]
        j = int(np.argmin(d)) if len(d) else -1
        if j >= 0 and d[j] < esik:
            used.add(j); n += 1
    tot = len(a) + len(b) - n
    return n / max(1, tot)  # eşzamanlı olay payı

def guc(s, nsim=4000):
    h0 = np.array([es_sayisi(*katalog(0.1), s) for _ in range(nsim)])
    h1 = np.array([es_sayisi(*katalog(0.5), s) for _ in range(nsim)])
    kritik = np.quantile(h0, 0.95)
    return float(np.mean(h1 > kritik)), float(np.mean(h0)), float(np.mean(h1))

if __name__ == "__main__":
    import json
    out = {}
    for s in (30, 60, 100):
        g, m0, m1 = guc(s)
        out[s] = {"guc": round(g, 3), "es_payi_f01": round(m0, 3), "es_payi_f05": round(m1, 3)}
        print(f"σ={s:3d} yıl  güç={g:.3f}  eşzamanlı pay f=0,1: {m0:.3f}  f=0,5: {m1:.3f}")
    json.dump(out, open("s6_sentetik_sonuc.json", "w"), indent=1)
