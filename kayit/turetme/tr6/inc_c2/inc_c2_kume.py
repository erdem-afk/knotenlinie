#!/usr/bin/env python3
"""TR-6c İNCELEME-2: §C3a kalibrasyon kümeleri (kapıdan önce, bütün adaylar) ile K_kapı kümelerinin karşılaştırması.
Yalnız dondurulmuş olay listesi (tr6a_olay_listesi.json: zaman, konum, kaba_N0 = olay öncesi önsayım) kullanılır;
katalog açılmaz. Kümeleme kodun kendisi (KAPI.kumele, 300 km / 1826 g); temsilci = kümenin ilk birimi (kume_seti).
Kullanım: python3 -I -B kayit/turetme/tr6/inc_c2/inc_c2_kume.py > çıktı.json"""
import json
import os
import sys

BURA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(BURA))
import tr6_a_kapi as KAPI            # noqa: E402
import tr6a_onkayit_sayilar as S     # noqa: E402

L = json.load(open(os.path.join(os.path.dirname(BURA), "tr6a_olay_listesi.json"), encoding="utf-8"))
ad = [b for b in L["birimler"] if b.get("kosu_adayi") and b.get("kaba_secim")]
kapi = [b for b in ad if b["kaba_N0"] >= 31.36]
N0 = {b["id"]: b["kaba_N0"] for b in ad}


def kumeler(bl):
    out = []
    for c in KAPI.kumele(sorted(bl, key=lambda b: b["zaman"])):
        uy = {x for b in c for x in b["uyeler"]}
        out.append(dict(temsilci=c[0]["id"], birimler=[b["id"] for b in c],
                        bilinen=bool(uy & set(S.BILINEN_CIKAN))))
    return out


kk, ka = kumeler(kapi), kumeler(ad)
tem_k = {c["temsilci"] for c in kk}
tem_a = {c["temsilci"] for c in ka}
fark = []
for c in kk:
    ev = next(x for x in ka if c["temsilci"] in x["birimler"])
    if ev["temsilci"] != c["temsilci"] or set(ev["birimler"]) != set(c["birimler"]):
        fark.append(dict(kapi_kumesi=c, kalibrasyon_kumesi=ev, temsilci_N0=N0[ev["temsilci"]],
                         kapi_temsilci_N0=N0[c["temsilci"]]))
print(json.dumps(dict(aday_birim=len(ad), kapi_birim=len(kapi), kapi_kume=len(kk), kalibrasyon_kume=len(ka),
                      farkli=fark, kenar_birimleri=[u for u, x in N0.items() if x > 500]), ensure_ascii=False, indent=1))
