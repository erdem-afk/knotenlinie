#!/usr/bin/env python3
"""TR-2 §4 ETAS yönü: küme başına p_i = R_sessiz / (R_sessiz + R_yoğun), [0,05, 0,95] aralığına kırpılır.

Sonraki/önceki olay bilgisi KULLANMAZ. Girdi: manifest (birincil id, dış merkez, Mw, L, stk, sessiz taraf) ve
ham anlık görüntüdeki artçı dosyaları.

  R_taraf = Σ_j 10^(1,0·(M_j − 4)) · Σ_hücre (r_jh² + c_j²)^(−1,5) · 4 km²
  j: birincil (dış merkezde, M = Mw) + 30 günlük artçı bulutunun tamamı ((t0, t0+30 g], ≤ 3 L, M ≥ 4, M < Mw;
     |s| < 5 km olanlar dahil).
  c_j = max(5 km, 0,5·L(M_j)); L Wells–Coppersmith.
  (s, d): birincil dış merkezine göre `eksen_bilesen`; r_jh bu düzlemde Öklid uzaklığı.
  Hücre merkezleri: |s| = 0,5 L + 1 + 2k, d = −D + 1 + 2m (D = max(L, 30 km)); merkezi kutuda (0,5 L ≤ |s| ≤ 5 L,
  |d| ≤ D) kalanlar. Arka plan ve zaman çekirdeği yok.

Kullanım: python3 -I -B tr2_etas.py <ham_dizin> [--manifest tr2_manifest.csv] [--cikti tr2_etas_p.csv]
"""
import csv
import math
import os
import sys

sys.dont_write_bytecode = True
BURA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURA)
import tr2_sayim as S  # noqa: E402
import tr2_manifest as MF  # noqa: E402

UST, VERIM, M_REF = 1.5, 1.0, 4.0
C_MIN_KM, C_L_KAT = 5.0, 0.5
HUCRE_KM = 2.0
P_ALT, P_UST = 0.05, 0.95


def hucreler(L):
    """İki yanın hücre merkezleri: (s>0 listesi, s<0 listesi), her biri (s, d)."""
    D = max(S.SON_D_L * L, S.SON_D_KM)
    s_list, k = [], 0
    while True:
        s = S.SON_S_MIN_L * L + HUCRE_KM / 2 + HUCRE_KM * k
        if s > S.SON_S_MAX_L * L:
            break
        s_list.append(s)
        k += 1
    d_list, m = [], 0
    while True:
        d = -D + HUCRE_KM / 2 + HUCRE_KM * m
        if d > D:
            break
        d_list.append(d)
        m += 1
    # merkez kutuda mı (s alt sınırı yapı gereği sağlanır; yine de açıkça sınanır)
    poz = [(s, d) for s in s_list for d in d_list
           if S.SON_S_MIN_L * L <= s <= S.SON_S_MAX_L * L and abs(d) <= D]
    neg = [(-s, d) for s, d in poz]
    return poz, neg


def R_taraf(kaynaklar, hucre):
    """kaynaklar: [(s_j, d_j, M_j)]."""
    tot = 0.0
    for sj, dj, mj in kaynaklar:
        c = max(C_MIN_KM, C_L_KAT * S.L_km(mj))
        verim = 10 ** (VERIM * (mj - M_REF))
        tot += verim * sum(((sh - sj) ** 2 + (dh - dj) ** 2 + c * c) ** (-UST) for sh, dh in hucre) \
            * HUCRE_KM * HUCRE_KM
    return tot


def p_ham(b, art, stk, sessiz):
    """Kırpılmamış p. b: {'lat','lon','mw'}; art: [(lat, lon, M)]; sessiz: +1 / −1."""
    L = S.L_km(b["mw"])
    kaynak = [(0.0, 0.0, b["mw"])]
    for la, lo, m in art:
        s, d = S.eksen_bilesen(b, la, lo, stk)
        kaynak.append((s, d, m))
    poz, neg = hucreler(L)
    Rp, Rn = R_taraf(kaynak, poz), R_taraf(kaynak, neg)
    Rs, Ry = (Rp, Rn) if sessiz == 1 else (Rn, Rp)
    return Rs / (Rs + Ry)


def kirp(p):
    return min(P_UST, max(P_ALT, p))


def main(ham, manifest, cikti):
    sat = list(csv.DictReader(open(manifest)))
    out, hamlar = [], []
    for r in sat:
        b = {"id": r["birincil_id"], "lat": float(r["dis_merkez_lat"]), "lon": float(r["dis_merkez_lon"]),
             "mw": float(r["mw"])}
        art, _ = MF.artci_oku(ham, b)
        p = p_ham(b, art, float(r["stk"]), int(r["sessiz_isaret"]))
        hamlar.append(p)
        out.append((r["kume"], r["birincil_id"], kirp(p)))
    with open(cikti, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["kume", "birincil_id", "p_i"])
        for k, i, p in out:
            w.writerow([k, i, f"{p:.6f}"])
    import statistics
    ps = sorted(p for _, _, p in out)
    q1, q2, q3 = statistics.quantiles(ps, n=4, method="inclusive")
    print({"N": len(ps), "en_kucuk": round(ps[0], 4), "q25": round(q1, 4), "medyan": round(q2, 4),
           "q75": round(q3, 4), "en_buyuk": round(ps[-1], 4),
           "kirpilan_alt": sum(p < P_ALT for p in hamlar), "kirpilan_ust": sum(p > P_UST for p in hamlar),
           "ham_en_kucuk": round(min(hamlar), 4), "ham_en_buyuk": round(max(hamlar), 4)})


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("ham")
    ap.add_argument("--manifest", default=os.path.join(BURA, "tr2_manifest.csv"))
    ap.add_argument("--cikti", default=os.path.join(BURA, "tr2_etas_p.csv"))
    a = ap.parse_args()
    main(a.ham, a.manifest, a.cikti)
