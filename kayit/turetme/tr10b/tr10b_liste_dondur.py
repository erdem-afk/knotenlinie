#!/usr/bin/env python3
"""TR-10b: aday listelerini ve istasyon üstverisini koşu için dondurur (`tr10b_listeler.json`).

Yalnız üstveri: `onkayit_yardimci/inc1_listeler.py`'nin depo dışına yazdığı JSON (ön kaydın §19'daki yolu; sakinlik
orada `tr10b_sayim.say` ile değiştirilmeden hesaplandı) ve indirme sayfası anlık görüntüsü (sha256 assert'li). Bu
betik sakinliği hesaplamaz; listeleri kopyalar ve ön kaydın kanonik sha256'larıyla denetler. Hiçbir veri dosyası
açılmaz.

Kullanım (depo kökünden):
  python3 -I -B kayit/turetme/tr10b/tr10b_liste_dondur.py <inc1 listeler.json> <tr10_ham_dizin> [<cikti>]
Çıktı varsayılanı kayit/turetme/tr10b/tr10b_listeler.json; "x" kipinde yazılır (varsa durur).
"""
import json
import os
import sys

BURA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURA)
import tr10b_listeler as TL  # noqa: E402
import tr10b_sayim as KS  # noqa: E402

TURLER = ("DAY", "10MIN", "MIC")


def main():
    lj, tr10_ham = sys.argv[1:3]
    cikti = sys.argv[3] if len(sys.argv) > 3 else TL.JSON_YOL
    d = json.load(open(lj, encoding="utf-8"))["sonuc"]
    ad_es = {"B": "B_U", "A": "A_U", "B_R2": "B_R2", "A_R2": "A_R2", "B1_gecmis5": "B_U_B1_gecmis5"}
    L = {ad: sorted((k, int(y)) for k, y, *_ in d["INC1_listeler"][kay]) for ad, kay in ad_es.items()}
    for ad, v in L.items():
        assert TL.kanonik(v) == TL.LISTE_SHA[ad], ad
    B_md, A_md, kesim_md = TL.md_listeleri(TL.md_oku())
    assert B_md == L["B"] and A_md == L["A"], "md tablosu ile inc1 listeleri farklı"
    sayfa = {s["kod"]: s for s in KS.sayfa_istasyonlar(tr10_ham)}     # sha256 assert'li
    ist = {}
    for k in sorted({k for k, _ in L["B"]}):
        s, i1 = sayfa[k], d["INC1_ist"][k]
        assert (s["lat"], s["lon"], s["ilk"].isoformat()) == (i1["lat"], i1["lon"], i1["ilk"])
        kes = KS.kesim(s["fay"], s["lat"])
        assert kes == kesim_md[k] == i1["kesim"], k
        ist[k] = dict(lat=s["lat"], lon=s["lon"], ilk=s["ilk"].isoformat(), ilk_sayfa=s["ilk_ham"], fay=s["fay"],
                      kesim=kes, site=f"{s['lat']:.3f},{s['lon']:.3f}", not_=s.get("not", ""),
                      dosya={t: list(s["dosya"][t]) for t in TURLER},
                      hdr=list(s["dosya"]["HDR"]))
        assert ist[k]["site"] == i1["site"]
    n = {t: sum(len(v["dosya"][t]) for v in ist.values()) for t in TURLER}
    assert n == {"DAY": 16, "10MIN": 21, "MIC": 29}, n                 # §2.2: 66 dosya
    out = dict(aciklama="TR-10b aday listeleri (ön kayıt sürüm 2 §4, §11 madde 9) ve istasyon üstverisi; "
                        "tr10b_liste_dondur.py ile üretildi; sakinlik yeniden hesaplanmadı.",
               kaynak=dict(sayfa_sha256=KS.SAYFA_SHA, liste_sha256=TL.LISTE_SHA),
               listeler={ad: [[k, y] for k, y in v] for ad, v in L.items()},
               istasyon=ist, dosya_sayisi=n)
    metin = json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    with open(cikti, "x", encoding="utf-8") as f:
        f.write(metin)
    print("yazıldı:", cikti, n)


if __name__ == "__main__":
    main()
