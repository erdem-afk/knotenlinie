# İNCELEME-1 (TR-10b_INCELEME-1.md §D) betiğinin kopyası; özgün yer: scratchpad/inc10b/hdr_karsilastir.py.
# Değişiklik yalnız yol düzeltmesi (depo içinden çalışsın diye); hesap aynen.
import re, sys, datetime as dt, subprocess
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__)))))
import tr10b_sayim as KS
out = subprocess.run([sys.executable, "-I", "-B", __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)), "hdr_kural.py"), sys.argv[1]], capture_output=True, text=True).stdout
AY = dict(jan=1,feb=2,mar=3,apr=4,may=5,jun=6,jul=7,aug=8,sep=9,oct=10,nov=11,dec=12)
def ct(s):
    if s == "None": return None
    m = re.match(r"([A-Za-z]+)\.? (\d{1,2}),? (\d{4})", s)
    if m: return dt.date(int(m[3]), AY[m[1][:3].lower()], int(m[2]))
    m = re.match(r"([A-Za-z]+) (\d{4})", s)
    if m: return dt.date(int(m[2]), AY[m[1][:3].lower()], 1)
    return None
blok = out.split("=== ")[1:]
for b in blok:
    satir = b.splitlines(); bas = satir[0]; ol = [x.split("\t") for x in satir[1:] if x.strip()]
    ol = [(x[0], ct(x[1]), x[2]) for x in ol]
    ad = {o[0] for o in ol}
    dogru = yanlis_tur = kac = 0; son_yanlis = []
    for kod, t, _ in KS.K_OLAY:
        if kod not in ad: continue
        t = dt.date.fromisoformat(t)
        h = [o for o in ol if o[0] == kod and o[1] and o[1] <= t and (t - o[1]).days <= 366]
        if any(o[2] == "K" for o in h): dogru += 1
        elif h: yanlis_tur += 1
        else: kac += 1
    son = [(o[0], o[1]) for o in ol if o[2] == "SON"]
    print(bas, "| K olarak tarihli yakalanan:", dogru, "| yanlış türle:", yanlis_tur, "| kaçan/tarihsiz:", kac, "| SON:", son)
