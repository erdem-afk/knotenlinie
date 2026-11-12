# İNCELEME-1 (TR-10b_INCELEME-1.md §D) betiğinin kopyası; özgün yer: scratchpad/inc10b/ek_liste.py.
# Değişiklik yalnız yol düzeltmesi (depo içinden çalışsın diye); hesap aynen.
# tr10b_sayim.say aynen; yalnız sonuç sözlüğüne "B_U, B1 geçmiş 5 y" listesi eklenir (depo dosyası değişmez).
import sys, os, json, hashlib, io, contextlib
KOD = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "tr10b_sayim.py")
HAM, TR10HAM, CIKTI = sys.argv[1:4]   # kullanım: ek_liste.py <ham_dizin> <tr10_ham_dizin> <cikti.json>
src = open(KOD).read()
anchor = '    sonuc["B_ana_liste"] = sorted('
assert src.count(anchor) == 1
ek = ('    sonuc["EK5"] = sorted((x["kod"], x["Y"], x["kesim"], x["site"]) for x in degerlendir(kapsam_sen="U", kurallar={"B1": dict(B1, once=5), "B2": B2, "B3": B3}))\n'
      '    sonuc["EK5_ozet"] = ozet([dict(kod=a, Y=b, tur="u", kesim=c, site=d) for a, b, c, d in sonuc["EK5"]])\n')
src = src.replace(anchor, ek + anchor)
sys.argv = [KOD]
g = {"__name__": "tr10b_ek", "__file__": KOD}
exec(compile(src, KOD, "exec"), g)
out = CIKTI
with contextlib.redirect_stdout(io.StringIO()):
    g["say"](HAM, out, TR10HAM)
s = json.load(open(out))["sonuc"]
L = s["EK5"]
print(len(L), hashlib.sha256("".join(sorted(f"{k}|{y}\n" for k, y, *_ in L)).encode()).hexdigest())
print({k: s["EK5_ozet"][k] for k in ("site_pencere", "site", "kesim", "kesim_basina_site_pencere", "epok_basina_site_pencere")})
print(sorted((k, y) for k, y, *_ in L))
