#!/usr/bin/env python3
"""TR-6c İNCELEME-1: kapı seçim yanlılığının sahte kalibrasyonla soğurulup soğurulmadığı (yalnız yapay veri).

Gerçek koşuda sahte oylar yalnız gerçek kapıyı geçen kümelerden gelir (TR-6a §4.6: "K_kapı'nın her kümesi"). Sahte son
pencereler gerçek ön pencerenin içindedir; gerçek kapı (n_on ≥ 155) yüksek ön sayımı seçtiğinde sahte son sayımlar da
yüksek olur. Bu betik (i) ve (ii) dünyalarında, kapıya yakın N0'larda aynı gerçekleşmeden şunları yazar:
  P(D | kapı), p̂₀ (bütün denemelerin sahteleri: TR-6c §C3 tanımı), p̂₀ (yalnız gerçek kapıyı geçenlerin sahteleri:
  gerçek koşunun havuzu) ve farklar (SE: yazarın `_fark_se` biçimi).

Kullanım: python3 -I -B kayit/turetme/tr6/inc_c/inc_c_kapi.py <dünya i|ii> <N0> <deneme> <tohum> <çıktı.json>
"""
import json
import os
import sys

import numpy as np

BURA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(BURA))
import tr6a_yapay as Y               # noqa: E402

dunya, N0, n, tohum, cikti = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
assert tohum not in Y.BAGLAYICI_TOHUMLAR + Y.BAGLAYICI_TOHUMLAR_C + Y.TANI_TOHUMLARI
sp = dict(N0=N0, dtau="sifir", ikincil_bolge=True)
if dunya == "ii":
    sp["ikincil_lob"] = True
T = Y.tek_birim_c()
rng = np.random.default_rng([tohum, int(N0 * 100), 1 if dunya == "i" else 2])
sat = []
for _ in range(n):
    r = T.deneme(rng, sp, sahte=True, ham=True)
    s = r.get("sahte", [])
    if r["veri_yok"]:
        continue
    sat.append((int(r["kapi"]), r["D"], len(s), sum(x[0] for x in s), r["N0_kapi"]))
X = np.array(sat, float)
kp, D, J, SD = X[:, 0] == 1, X[:, 1], X[:, 2], X[:, 3]
out = dict(dunya=dunya, N0=N0, deneme=n, tohum=tohum, veri_var=len(X), kapi_payi=round(float(kp.mean()), 4))
for ad, sec in (("hepsi", np.ones(len(X), bool)), ("kapi_gecen", kp), ("kapi_gecmeyen", ~kp)):
    f = Y._fark_se(SD[sec], J[sec], D[kp])
    out[f"p0_{ad}"] = None if f is None else dict(p0=round(f[0], 5), P_D_kapi=round(f[1], 5), fark=round(f[2], 5),
                                                  se=round(f[3], 5), z=round(f[2] / f[3], 2),
                                                  J_ort=round(float(J[sec].mean()), 3))
with open(cikti, "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False))
