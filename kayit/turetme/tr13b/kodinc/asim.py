"""Bağımsız inceleme: asimetri (a) tanımsız z ve (b) N >= 50 şartı. Yalnız yapay ETAS; gerçek katalog yok.
Kullanım: python3 -I -B asim.py <cikti.npz> <havuz> <veri0> <veriF> <N_kipi: tablo|dusuk> <tohum>
"""
import multiprocessing as mp
import os
import sys
import time

import numpy as np

sys.dont_write_bytecode = True
KOD = "/home/user/knotenlinie/kayit/turetme/tr13b"
sys.path.insert(0, KOD)
import tr13b_kosu as K  # noqa: E402

# ön kayıt §2 tablosu (üstveri; Ishigaki düşmüş): (i, küme, R, doyma sonrası N3bg)
UYE = [(0, 397, 66.5, 86), (1, 160, 102.1, 96), (2, 303, 102.1, 97), (3, 395, 277.4, 90), (4, 397, 135.8, 99),
       (5, 1141, 156.7, 89), (7, 727, 117.8, 100), (8, 802, 57.7, 74), (9, 901, 117.8, 84), (10, 942, 425.6, 91),
       (11, 979, 135.8, 91), (12, 1139, 319.9, 98), (13, 1035, 180.7, 86), (14, 1139, 88.5, 98),
       (15, 1144, 57.7, 89)]


def is_kal(a):
    tohum, R, N, dal = a
    K.dallanma(dal)
    return K.kalibre(np.random.default_rng(tohum), N, R, 40)["Nh"]


def is_bolge(a):
    anahtar, tohum, R, Nh, dal, f, n = a
    K.dallanma(dal)
    rng = np.random.default_rng(tohum)
    return anahtar, np.array([K.yapay_bolge(rng, Nh, R, f, K.B_REF) for _ in range(n)], float).reshape(-1, 3)


def main(cikti, nh, n0, nf, kip, tohum):
    t0 = time.time()
    uye = [(i, k, R, (55 if kip == "dusuk" else N)) for i, k, R, N in UYE]
    kal_is, kal_ad = [], []
    for j, (i, k, R, N) in enumerate(uye):
        for di, d in enumerate(K.DALLANMA):
            kal_is.append((tohum + 100 * j + di, R, N, d)); kal_ad.append(f"s{i}_{di}")
        kal_is.append((tohum + 100 * j + 9, R, N, 0.6)); kal_ad.append(f"v{i}")
    with mp.get_context("fork").Pool(4) as P:
        Nh = dict(zip(kal_ad, P.map(is_kal, kal_is, chunksize=1)))
        print("kalibrasyon", round(time.time() - t0), flush=True)
        isler = []
        for j, (i, k, R, N) in enumerate(uye):
            for di, d in enumerate(K.DALLANMA):
                for p in range(4):
                    isler.append((f"s{i}_{di}_{p}", tohum + 100 * j + 20 + 4 * di + p, R, Nh[f"s{i}_{di}"], d, 0.0,
                                  K.parca_boylari(nh, 4)[p]))
            for p in range(2):
                isler.append((f"v{i}_0_{p}", tohum + 100 * j + 40 + p, R, Nh[f"v{i}"], 0.6, 0.0, n0 // 2))
                isler.append((f"v{i}_f_{p}", tohum + 100 * j + 50 + p, R, Nh[f"v{i}"], 0.6, 0.4, nf // 2))
        isler.sort(key=lambda a: -a[2])
        out = {}
        for ad, arr in P.imap_unordered(is_bolge, isler, chunksize=1):
            out[ad] = arr
    birles = {}
    for ad in out:
        b = ad.rsplit("_", 1)[0]
        birles.setdefault(b, []).append(out[ad])
    kay = {b: np.concatenate(v) for b, v in birles.items()}
    kay["uye"] = np.array(uye, float)
    np.savez(cikti, **kay)
    print("bitti", round(time.time() - t0), "s", flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0], int(a[1]), int(a[2]), int(a[3]), a[4], int(a[5]))
