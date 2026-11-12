# tr10b_sayim.say'i aynen çalıştırır; yalnız sonuç sözlüğüne U ve R2 aday listelerini ekler (kod metni değişmez,
# yalnız bir satır eklenerek exec edilir). Çıktı scratch'e.
import sys, os, json, hashlib
KOD = "/home/user/knotenlinie/kayit/turetme/tr10b/tr10b_sayim.py"
src = open(KOD).read()
anchor = '    sonuc["B_ana_liste"] = sorted('
assert src.count(anchor) == 1
ek = ('    sonuc["EK_listeler"] = {ad: sorted((x["kod"], x["Y"], x["tur"], x["kesim"], x["site"]) for x in degerlendir(**kw))\n'
      '        for ad, kw in {"B_U": dict(kapsam_sen="U", kurallar=KB), "A_U": dict(kapsam_sen="U"),\n'
      '                       "B_R2": dict(kurallar=KB), "A_R2": dict(), "B_R": dict(kapsam_sen="R", kurallar=KB),\n'
      '                       "A_R": dict(kapsam_sen="R")}.items()}\n'
      '    sonuc["EK_ozet"] = {k: ozet([dict(kod=a, Y=b, tur=c, kesim=d, site=e) for a, b, c, d, e in v]) for k, v in sonuc["EK_listeler"].items()}\n')
src = src.replace(anchor, ek + anchor)
sys.argv = [KOD]
g = {"__name__": "tr10b_ek", "__file__": KOD}
exec(compile(src, KOD, "exec"), g)
import io, contextlib
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    g["say"](sys.argv_ham if False else os.environ["HAM"], os.environ["OUT"], os.environ["TR10HAM"])
