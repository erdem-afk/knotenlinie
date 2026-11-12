#!/usr/bin/env python3
"""TR-10b aday listeleri: ön kaydın (sürüm 2) §4 tablosundan okunur, kanonik sha256 ile doğrulanır.

Sakinlik ya da kapsam YENİDEN HESAPLANMAZ. Listeler yalnız ön kayıt metninden (B ve A) ve dondurulmuş
`tr10b_listeler.json`'dan (B_R2, A_R2, B1 geçmiş 5 y alt kümeleri; §4 ve §11 madde 9 bu alt kümeleri yalnız sha256
ile tanımlar, üyeleri metinde yazılı değildir) okunur; her biri ön kayıttaki sha256 ile denetlenir, uyuşmazlıkta
`ListeHata` atılır.

Kanonik biçim (§4): her istasyon-pencere için f"{KOD}|{Y}\\n", satırlar sıralanır, birleştirilir, UTF-8 SHA-256.

Ön kayıt dosyası dondurulduktan sonra sonuna ek alabilir (§6.4 madde 4: "Ek: HDR K/D olayları"). Bu yüzden
denetim dosyanın tamamına değil, dondurulmuş ilk MD_DONMUS_BOY baytına yapılır (kodlayıcı okuması).

Kullanım (depo kökünden; yalnız denetim):
  python3 -I -B kayit/turetme/tr10b/tr10b_listeler.py [--json kayit/turetme/tr10b/tr10b_listeler.json]
"""
import hashlib
import json
import os
import re
import sys

BURA = os.path.dirname(os.path.abspath(__file__))
DEPO = os.path.abspath(os.path.join(BURA, "..", "..", ".."))
MD_YOL = os.path.join(DEPO, "kayit", "onkayit", "TR-10b_sunme-taban-dagilimi_ONKAYIT.md")
MD_SHA = "6993ae4a6432f482d0507dde5e479ade18bf4517adbd5540584bbeec51b64da4"
MD_DONMUS_BOY = 77114
JSON_YOL = os.path.join(BURA, "tr10b_listeler.json")

LISTE_SHA = {
    "B": "17f120d295447f7aa102f3d8d18c223e7f0822ac9ca0467e6690b5c094997101",
    "A": "c027949015ff962f9e8ec56990f2808642c1a39c81c725c9bb615f094857a422",
    "B_R2": "560b49c1c634202a5451c85da8e26fb87059fe6e025a1956f53989cece6d036d",
    "A_R2": "cc238e03b244ec752928c705967647830e859b92d0c9e11f23df427e44b71426",
    "B1_gecmis5": "33b8eafab4782c417c70f55a1606aecdf4fb1466e2c96817a53f2ef453d20b52",
}
# §4 ve §11 madde 9'daki sayılar: istasyon-pencere, istasyon
LISTE_BOY = {"B": (78, 35), "A": (38, 30), "B_R2": (42, 23), "A_R2": (22, 19), "B1_gecmis5": (52, 30)}
UST_KUME = {"A": "B", "B_R2": "B", "A_R2": "A", "B1_gecmis5": "B"}
KESIM_ADI = {"CAL_Hollister": "CAL_Hollister", "HAY": "HAY", "SAF_SJB": "SAF_SJB", "SAF_sunen_orta": "SAF_sunen_orta",
             "SAF_Parkfield": "SAF_Parkfield", "SAF_guney_gecis": "SAF_guney_gecis"}


class ListeHata(Exception):
    pass


def kanonik(ciftler):
    return hashlib.sha256("".join(sorted(f"{k}|{y}\n" for k, y in ciftler)).encode("utf-8")).hexdigest()


def md_oku(md_yol=MD_YOL, md_sha=MD_SHA, boy=MD_DONMUS_BOY):
    b = open(md_yol, "rb").read()
    if len(b) < boy or hashlib.sha256(b[:boy]).hexdigest() != md_sha:
        raise ListeHata("ön kayıt metninin dondurulmuş kısmı (ilk %d bayt) sha256 ile uyuşmuyor" % boy)
    return b[:boy].decode("utf-8")


_YIL = re.compile(r"\b(19[6-9]\d|20[0-2]\d)\b")


def _epoklar(s):
    return [int(x) for x in _YIL.findall(s)]


def md_listeleri(metin):
    """§4 tablosundan B ve A listelerini ve kesim atamasını okur.
    Satır biçimi: '| Kesim | KOD y, y (y); KOD y (–); K1, K2, K3: her biri y, y (y) |'."""
    a = metin.index("| Kesim | İstasyon: B epokları (A epokları) |")
    z = metin.index("\n\n", a)
    B, A, kesim = set(), set(), {}
    for sat in metin[a:z].splitlines()[2:]:
        h = [x.strip() for x in sat.strip().strip("|").split("|")]
        if len(h) != 2:
            raise ListeHata("§4 tablo satırı beklenmedik: " + sat)
        kes, govde = h
        if kes not in KESIM_ADI:
            raise ListeHata("bilinmeyen kesim: " + kes)
        for parca in [p.strip() for p in govde.split(";") if p.strip()]:
            m = re.fullmatch(r"(.+?):\s*her biri\s+([^()]*)\(([^()]*)\)", parca)
            if m:
                kodlar = [k.strip() for k in m.group(1).split(",")]
                bE, aE = m.group(2), m.group(3)
            else:
                m = re.fullmatch(r"([A-Z0-9]{4})\s+([^()]*)\(([^()]*)\)", parca)
                if not m:
                    raise ListeHata("§4 hücresi ayrıştırılamadı: " + parca)
                kodlar, bE, aE = [m.group(1)], m.group(2), m.group(3)
            for k in kodlar:
                if not re.fullmatch(r"[A-Z0-9]{4}", k):
                    raise ListeHata("istasyon kodu beklenmedik: " + k)
                kesim[k] = kes
                for y in _epoklar(bE):
                    B.add((k, y))
                for y in _epoklar(aE):
                    A.add((k, y))
    return sorted(B), sorted(A), kesim


def listeleri_yukle(md_yol=MD_YOL, json_yol=JSON_YOL):
    """Dönüş: dict(listeler={ad: [(KOD, Y)]}, istasyon={KOD: üstveri}, kesim={KOD: kesim}, json_sha256, md_sha256).
    Her liste ön kayıttaki sha256 ve boylarla denetlenir; alt küme ilişkileri denetlenir."""
    metin = md_oku(md_yol)
    B, A, kesim = md_listeleri(metin)
    jb = open(json_yol, "rb").read()
    j = json.loads(jb.decode("utf-8"))
    L = {"B": B, "A": A}
    for ad in ("B_R2", "A_R2", "B1_gecmis5"):
        L[ad] = sorted((k, int(y)) for k, y in j["listeler"][ad])
    for ad, v in L.items():
        if kanonik(v) != LISTE_SHA[ad]:
            raise ListeHata(f"{ad} listesi kanonik sha256 ile uyuşmuyor")
        if (len(v), len({k for k, _ in v})) != LISTE_BOY[ad]:
            raise ListeHata(f"{ad} listesinin boyu ön kayıttakiyle uyuşmuyor")
        if ad in UST_KUME and not set(v) <= set(L[UST_KUME[ad]]):
            raise ListeHata(f"{ad} ⊄ {UST_KUME[ad]}")
    # JSON'daki B ve A da metindekiyle aynı olmalı (çift kayıt tutarlılığı)
    for ad in ("B", "A"):
        if sorted((k, int(y)) for k, y in j["listeler"][ad]) != L[ad]:
            raise ListeHata(f"tr10b_listeler.json içindeki {ad} metindekinden farklı")
    ist = j["istasyon"]
    for k in {k for k, _ in B}:
        if k not in ist:
            raise ListeHata("istasyon üstverisi eksik: " + k)
        if ist[k]["kesim"] != kesim[k]:
            raise ListeHata(f"{k}: JSON kesimi ({ist[k]['kesim']}) §4 tablosundakiyle ({kesim[k]}) uyuşmuyor")
    return dict(listeler=L, istasyon=ist, kesim=kesim, json_sha256=hashlib.sha256(jb).hexdigest(),
                md_sha256=MD_SHA)


if __name__ == "__main__":
    jy = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else JSON_YOL
    r = listeleri_yukle(json_yol=jy)
    for ad, v in r["listeler"].items():
        print(f"{ad}: {len(v)} istasyon-pencere, {len({k for k, _ in v})} istasyon; sha256 {kanonik(v)} (uyuşuyor)")
    print("tr10b_listeler.json sha256", r["json_sha256"])
