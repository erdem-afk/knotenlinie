#!/usr/bin/env python3
"""TR-6c İNCELEME-2: küme düzeyi yanlış "H1" oranının bağımsız yeniden kurulumu (yalnız yapay veri).
Girdi: inc_c2_kayit.py kayıtları (tohum 8811). Senaryo: N aday küme aynı λ'da + önsayımın 2 kenar kümesi.
Yazarın tr6c_z2.py benzetiminden bağımsız yazıldı; yalnız incelenen kodun işlevleri (KO.p0_kestir, KO.testere,
S.kritik, S.K_ALT, S.P0_UST) ve kenar H0 D olasılığı (tr6c_z2.kenar_pD, prova hattı) ortaktır.
Havuz: v1 = yalnız gerçek kapıyı geçenlerin sahteleri; a2 = bütün adayların sahteleri (her sahte kendi kapısıyla).
"en zayıf" = en küçük kapı N0. δ: D = 0 olan gerçek oy 2δ olasılıkla 1 olur (yazarın kaydırma tanımı).
Kullanım: python3 -I -B kayit/turetme/tr6/inc_c2/inc_c2_alfa.py <kayıt.json> <N aday> <tekrar> <tohum> <çıktı.json>"""
import json
import math
import os
import sys

import numpy as np

BURA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(BURA))
import tr6a_kosu as KO                # noqa: E402
import tr6a_onkayit_sayilar as S      # noqa: E402
import tr6c_z2 as Z                   # noqa: E402

yol, N, n, tohum, cikti = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
d = json.load(open(yol, encoding="utf-8"))
a = np.array(d["satir"], float)
kapi, N0k, vy, D, J, Sh = (a[:, i] for i in range(6))
kum, _, _ = Z.onsayim()
kenar = [x for x in kum if x > 500.0]
pk = np.array([Z.kenar_pD(x, d["dunya"]) for x in kenar])
_kr, _tz = {}, {}


def kritik(K, p0):
    if (K, p0) not in _kr:
        _kr[(K, p0)] = S.kritik(K, p0)
    return _kr[(K, p0)]


def testere(K, p0):
    if (K, p0) not in _tz:
        _tz[(K, p0)] = KO.testere(K, p0)["atilan"]
    return _tz[(K, p0)]


out = dict(kayit=os.path.basename(yol), dunya=d["dunya"], lam=d["lam"], N_aday=N, kenar=kenar, tekrar=n, tohum=tohum,
           sonuc={})
for delta in (0.0, 0.02):
    rng = np.random.default_rng([tohum, N, int(delta * 1000)])
    s = rng.integers(0, len(D), (n, N))
    Dg = D[s]
    if delta:
        Dg = np.where((Dg == 0) & (rng.random(Dg.shape) < 2 * delta), 1, Dg)
    gec = (kapi[s] == 1) & (vy[s] == 0)
    Dk = (rng.random((n, len(kenar))) < pk[None, :]).sum(1)
    for yol_ad in ("v1", "a2"):
        if yol_ad == "a2":
            Jh, Shh = J[s].sum(1), Sh[s].sum(1)
        else:
            Jh, Shh = (J[s] * gec).sum(1), (Sh[s] * gec).sum(1)
        h1 = olcu = gy = 0
        Ks = []
        for t in range(n):
            g = np.where(gec[t])[0]
            K = len(g) + len(kenar)
            Ks.append(K)
            p0, _ = KO.p0_kestir(int(Shh[t]), int(Jh[t]))
            if K < S.K_ALT:
                gy += 1
                continue
            if p0 > S.P0_UST:
                olcu += 1
                continue
            at = testere(K, p0)
            sira = g[np.argsort(N0k[s[t, g]], kind="stable")]
            X = Dg[t, sira[at:]].sum() + Dk[t]
            if X >= kritik(K - at, p0):
                h1 += 1
        out["sonuc"][f"{yol_ad} δ {delta:g}"] = dict(yanlis_H1=round(h1 / n, 4), se=round(math.sqrt(h1) / n, 4),
                                                     olcu_yanli=round(olcu / n, 4), guc_yok=round(gy / n, 4),
                                                     K_ort=round(float(np.mean(Ks)), 2), J_ort=round(float(Jh.mean()), 1))
json.dump(out, open(cikti, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(out["sonuc"], ensure_ascii=False))
