#!/usr/bin/env python3
"""TR-6c İNCELEME-1: bir prova hücresinin bağımsız tohumla yeniden koşulması (yalnız yapay veri).

Yazarın `hucre_parcasi_c` / `hucre_ozeti_c` işlevleri kullanılır (bağlayıcı olmayan inceleme tohumu 8801). Ek olarak:
- p̂₀ yalnız gerçek kapıyı geçen denemelerin sahte oylarından (gerçek koşudaki havuzun karşılığı) − P(D | kapı);
- C1′'nün yerine önerilen iki yanlı ölçüt: kümesizleştirmesiz (D4) P(D | kapı) − kesin Poisson;
- hat P(D | kapı) − kesin Poisson.

Kullanım: python3 -I -B kayit/turetme/tr6/inc_c/inc_c_hucre.py <hücre> <deneme> <çıktı.json>
"""
import json
import math
import os
import sys

import numpy as np

BURA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(BURA))
import tr6a_yapay as Y               # noqa: E402

TOHUM = 8801
ad, n, cikti = sys.argv[1], int(sys.argv[2]), sys.argv[3]
assert TOHUM not in Y.BAGLAYICI_TOHUMLAR + Y.BAGLAYICI_TOHUMLAR_C + Y.TANI_TOHUMLARI
parcalar = [Y.hucre_parcasi_c(ad, TOHUM, p) for p in range(-(-n // Y.PARCA_C))]
oz = Y.hucre_ozeti_c(ad, parcalar)
X = np.array([s for p in parcalar for s in p["satir"]], dtype=float)
c = {k: X[:, i] for i, k in enumerate(Y.ALAN_C)}
var = c["veri_yok"] == 0
kv = var & (c["kapi"] == 1)
N0, _ = Y.hucre_spec_c(ad)
N0k = N0 * 10 ** (-Y.MC_FARKI_C)
ek = {}
f = Y._fark_se(c["SD"][kv], c["J"][kv], c["D"][kv])
if f:
    ek["C1_kapi_kosullu_havuz"] = dict(p0=round(f[0], 5), P_D_kapi=round(f[1], 5), fark=round(f[2], 5),
                                       se=round(f[3], 5), z=round(f[2] / f[3], 2))
for adx, col in (("ham_D4", "Dh"), ("hat", "D")):
    x = c[col][kv]
    bek = Y.kesin_c(N0k)
    se = math.sqrt(bek * (1 - bek) / len(x))
    ek[f"{adx}_P_D_kapi_eksi_kesin"] = dict(deger=round(float(x.mean()), 5), kesin=round(bek, 5), se=round(se, 5),
                                            z=round((float(x.mean()) - bek) / se, 2))
with open(cikti, "w", encoding="utf-8") as fh:
    json.dump(dict(hucre=ad, tohum=TOHUM, deneme=n, ozet=oz, ek=ek), fh, ensure_ascii=False, indent=1)
