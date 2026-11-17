#!/usr/bin/env python3
"""TR-6c İNCELEME-2: bağımsız deneme kayıtları (yalnız yapay veri; yazarın tr6c_z2.py'sinden bağımsız yazıldı).
Tek birimli yapay dünyada (TR-6c §C3, kural (d)) verilen λ'da her deneme için: gerçek kapı, kapı N0, veri yok, gerçek D,
geçerli sahte sayısı J ve sahte düşüş oyu toplamı S. Tohum bağlayıcı/tanı olamaz.
Kullanım: python3 -I -B kayit/turetme/tr6/inc_c2/inc_c2_kayit.py <i|ii> <λ> <deneme> <tohum> <çıktı.json>"""
import json
import os
import sys

import numpy as np

BURA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(BURA))
import tr6a_yapay as Y               # noqa: E402

dunya, lam, n, tohum, cikti = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
Y.tohum_denetle_c(tohum, False)
sp = dict(N0=lam, dtau="sifir", ikincil_bolge=True)
if dunya == "ii":
    sp["ikincil_lob"] = True
T = Y.tek_birim_c()
rng = np.random.default_rng([tohum, int(round(lam * 100)), 1 if dunya == "i" else 2])
sat = []
for _ in range(n):
    r = T.deneme(rng, sp, sahte=True, ham=True)
    s = r.get("sahte", [])
    sat.append([int(r["kapi"]), round(float(r["N0_kapi"]), 3), int(bool(r["veri_yok"])), -1 if r["veri_yok"] else int(r["D"]), len(s),
                int(sum(x[0] for x in s))])
json.dump(dict(dunya=dunya, lam=lam, tohum=tohum, deneme=n, alan=["kapi", "N0_kapi", "veri_yok", "D", "J", "S"], satir=sat),
          open(cikti, "w"), separators=(",", ":"))
