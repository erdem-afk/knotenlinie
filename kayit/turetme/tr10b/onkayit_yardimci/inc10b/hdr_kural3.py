# İNCELEME-1 (TR-10b_INCELEME-1.md §D) betiğinin kopyası; özgün yer: scratchpad/inc10b/hdr_kural3.py.
# Değişiklik yalnız yol düzeltmesi (depo içinden çalışsın diye); hesap aynen.
# İncelemenin önerdiği HDR kuralının (E1 düzeltme metni) README "Comments specific" bölümünde sınanması.
import re, sys, datetime as dt
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__)))))
import tr10b_sayim as KS
L = open(sys.argv[1], encoding="utf-8", errors="replace").read().splitlines()
a = next(i for i, x in enumerate(L) if x.startswith("Comments specific"))
z = next(i for i, x in enumerate(L) if x.startswith("The following is a list of files"))
L = L[a+1:z]
AY = dict(jan=1,feb=2,mar=3,apr=4,may=5,jun=6,jul=7,aug=8,sep=9,oct=10,nov=11,dec=12)
MN = r"(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?|sept?(?:ember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\.?"
Y = r"(19[6-9]\d|20[0-2]\d)"
yy = lambda s: int(s) if len(s) == 4 else (1900+int(s) if int(s) > 30 else 2000+int(s))
TAM = [
 (r"\b"+Y+r"-(\d\d)-(\d\d)\b", lambda m: dt.date(int(m[1]),int(m[2]),int(m[3]))),
 (r"\b"+Y+r"/(\d\d)/(\d\d)\b", lambda m: dt.date(int(m[1]),int(m[2]),int(m[3]))),
 (r"\b(\d{1,2})/(\d{1,2})/(\d{4}|\d{2})\b", lambda m: dt.date(yy(m[3]),int(m[1]),int(m[2]))),
 (r"\b(\d{1,2})[ -]"+MN+r"[ ,-]*"+Y+r"\b", lambda m: dt.date(int(m[3]),AY[m[2][:3].lower()],int(m[1]))),
 (r"\b"+MN+r"\s+(\d{1,2}),?\s+"+Y+r"\b", lambda m: dt.date(int(m[3]),AY[m[1][:3].lower()],int(m[2]))),
 (r"\b"+MN+r"(?:\s*-\s*"+MN+r")?,?\s+"+Y+r"\b", lambda m: dt.date(int(m[3]),AY[m[1][:3].lower()],1)),
 (r"\b"+Y+r"[ .:](\d{3})\b", lambda m: dt.date(int(m[1]),1,1)+dt.timedelta(days=int(m[2])-1)),
]
def tarih(s):
    c = []
    for p, f in TAM:
        for m in re.finditer(p, s, re.I):
            try: c.append((m.start(), f(m)))
            except Exception: pass
    if c: return min(c)[1]
    m = re.search(r"\b"+Y+r"\b", s)
    return dt.date(int(m[1]),1,1) if m else None
K = (r"\b(re-?set|re-?zero|zero|broke|break|snap|replac|new (?:wire|rod|sensor|transducer|lvdt)|moved\b|relocat|"
     r"re-?install|reposition|offset|repair|damage|vandal|collapse|caved|cave-in|cave in|flood|rodent|gopher|"
     r"out of range|over-?range|ran out|re-?calibrat|mis-?calibrat|calibrat|fail|unreliab|touch|tighten|loosen|bent\b|"
     r"bump|peg|tension|slid|offline|glitch|spurious|bogus|delet|abandon|removed|destroy|decommission|no longer)")
D = r"\b(electronic|dcp|scale factor|gain)"
par, cur = [], []
for s in L + [""]:
    if s.strip() == "" or re.fullmatch(r"[-=*_ ]+", s.strip()):
        if cur: par.append(cur); cur = []
    else: cur.append(s.strip())
ist, olay = None, []
for p in par:
    if re.fullmatch(r"[A-Z0-9]{4}", p[0]): ist = p[0]; p = p[1:]
    if p and p[0].startswith("XMBC "): ist = "XMBC"
    if not p: continue
    m = " ".join(p); ml = m.lower()
    k = re.findall(K, ml); d = re.findall(D, ml)
    if k or d: olay.append((ist, tarih(m), "K" if k else "D", sorted(set(k or d)), m[:60]))
for o in olay: print(*o, sep="\t")
# K_OLAY ile karşılaştırma (yorum bölümünde adı geçen istasyonlar)
ad = {o[0] for o in olay}
print("\nK_OLAY karşılaştırması (yorumu olan istasyonlar):")
yak = kac = 0
for kod, t, ac in KS.K_OLAY:
    if kod not in ad: print("  yorum yok:", kod, t); continue
    t = dt.date.fromisoformat(t)
    hit = [o for o in olay if o[0] == kod and o[2] == "K" and o[1] and o[1] <= t and (t - o[1]).days <= 366]
    ok = bool(hit); yak += ok; kac += 1
    print("  ", kod, t, "BULUNDU" if ok else "KAÇTI", hit[0][1] if hit else "", ac)
print("yakalanan", yak, "/", kac)
