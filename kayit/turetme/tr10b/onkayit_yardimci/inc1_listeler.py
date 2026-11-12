# TR-10b ön kayıt sürüm 2 (İNCELEME-1 düzeltmeleri) için aday listelerinin yeniden üretimi.
# tr10b_sayim.say değiştirilmeden çalıştırılır; kod metnine yalnız sonuç sözlüğüne liste ekleyen satırlar eklenerek
# exec edilir (depo dosyası değişmez). Yalnız üstveri okunur: indirme sayfası anlık görüntüsü, HEAD önbelleği,
# README (dosya aralıkları), ComCat önbelleği. Hiçbir sünme ölçer veri dosyası ya da HDR dosyası açılmaz.
#
# Kullanım (depo kökünden):
#   python3 -I -B kayit/turetme/tr10b/onkayit_yardimci/inc1_listeler.py <ham_dizin> <tr10_ham_dizin> <cikti.json>
# Çıktı JSON'u depo dışına (scratch) yazılır; öteki inc1_* betikleri onu okur.
import contextlib
import hashlib
import io
import json
import os
import sys

BURA = os.path.dirname(os.path.abspath(__file__))
KOD = os.path.join(os.path.dirname(BURA), "tr10b_sayim.py")
ham, tr10_ham, cikti = sys.argv[1:4]

src = open(KOD, encoding="utf-8").read()
anchor = '    sonuc["B_ana_liste"] = sorted('
assert src.count(anchor) == 1
ek = (
    '    _K = {"B_U": dict(kapsam_sen="U", kurallar=KB), "A_U": dict(kapsam_sen="U"),\n'
    '          "B_R2": dict(kurallar=KB), "A_R2": dict(),\n'
    '          "B_U_B1_gecmis5": dict(kapsam_sen="U", kurallar={"B1": dict(B1, once=5), "B2": B2, "B3": B3})}\n'
    '    sonuc["INC1_listeler"] = {ad: sorted([x["kod"], x["Y"], x["tur"], x["kesim"], x["site"]]\n'
    '                                         for x in degerlendir(**kw)) for ad, kw in _K.items()}\n'
    '    sonuc["INC1_ozet"] = {ad: ozet([dict(kod=a, Y=b, tur=c, kesim=d, site=e) for a, b, c, d, e in v])\n'
    '                          for ad, v in sonuc["INC1_listeler"].items()}\n'
    '    sonuc["INC1_ist"] = {s["kod"]: dict(lat=s["lat"], lon=s["lon"], ilk=s["ilk"].isoformat(), site=s["site"],\n'
    '                                        kesim=s["kesim"], fay=s["fay"]) for s in ist}\n'
)
src = src.replace(anchor, ek + anchor)
sys.argv = [KOD]
g = {"__name__": "tr10b_inc1", "__file__": KOD}
exec(compile(src, KOD, "exec"), g)
with contextlib.redirect_stdout(io.StringIO()):
    g["say"](ham, cikti, tr10_ham)
d = json.load(open(cikti, encoding="utf-8"))
s = d["sonuc"]
L, O = s["INC1_listeler"], s["INC1_ozet"]


def kanonik(liste):
    return hashlib.sha256("".join(sorted(f"{k}|{y}\n" for k, y, *_ in liste)).encode("utf-8")).hexdigest()


print("meta:", {k: d["meta"][k] for k in ("sayfa_sha256", "readme_sha256", "comcat_sha256", "comcat_olay_N")})
for ad, v in L.items():
    o = O[ad]
    print(f"{ad}: istasyon-pencere {o['istasyon_pencere']}, istasyon {o['istasyon']}, yer-pencere "
          f"{o['site_pencere']}, yer {o['site']}, kesim {o['kesim']}; sha256 {kanonik(v)}")
    print("   kesim başına yer-pencere:", o["kesim_basina_site_pencere"])
    print("   epok başına yer-pencere:", {k: n for k, n in o["epok_basina_site_pencere"].items() if n})

kume = lambda ad: {(k, y) for k, y, *_ in L[ad]}
print("A_U ⊂ B_U:", kume("A_U") <= kume("B_U"), "| B_R2 ⊂ B_U:", kume("B_R2") <= kume("B_U"),
      "| A_R2 ⊂ A_U:", kume("A_R2") <= kume("A_U"), "| B1 geçmiş 5 y ⊂ B_U:", kume("B_U_B1_gecmis5") <= kume("B_U"))

# K4: U'nun R2'ye eklediği adaylar
fark = sorted(kume("B_U") - kume("B_R2"))
print(f"\nB_U − B_R2: {len(fark)} istasyon-pencere; yer-pencere farkı "
      f"{O['B_U']['site_pencere'] - O['B_R2']['site_pencere']}")
gr = {}
for k, y in fark:
    gr.setdefault(k, []).append(y)
for k in sorted(gr):
    print("  ", k, gr[k])
gruplar = {
    "HW* elle ölçerleri 1973 ve 2003–2013": lambda k, y: k.startswith("HW"),
    "HLC1, HLD1, SHR2 2013–2018": lambda k, y: k in ("HLC1", "HLD1", "SHR2"),
    "TWR1, XPH1 2013–2018": lambda k, y: k in ("TWR1", "XPH1"),
    "XDL2 2013 ve 2018": lambda k, y: k == "XDL2",
    "BIT1, XMP1, XMP2 1998": lambda k, y: k in ("BIT1", "XMP1", "XMP2"),
    "XHR1 2018": lambda k, y: k == "XHR1",
}
toplam = 0
for ad, f in gruplar.items():
    n = sum(1 for k, y in fark if f(k, y)); toplam += n
    print(f"   {ad}: {n}")
print("   gruplanan toplam:", toplam, "/", len(fark))

# Ö3: B1 geçmiş 5 y alt kümesi
o5 = O["B_U_B1_gecmis5"]
print("\nB1 geçmiş 5 y: 2013 epoğu yer-pencere", O["B_U"]["epok_basina_site_pencere"]["2013"], "→",
      o5["epok_basina_site_pencere"]["2013"], "; Parkfield", O["B_U"]["kesim_basina_site_pencere"]["SAF_Parkfield"],
      "→", o5["kesim_basina_site_pencere"].get("SAF_Parkfield"))
