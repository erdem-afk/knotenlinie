# İNCELEME-1 (TR-10b_INCELEME-1.md §D) betiğinin kopyası; özgün yer: scratchpad/inc10b/hdr_kural.py.
# Değişiklik yalnız yol düzeltmesi (depo içinden çalışsın diye); hesap aynen.
# TR-10b taslak §6.4 kuralının README "Comments specific" bölümüne mekanik uygulanması (HDR biçimine vekil).
import re, sys
L = open(sys.argv[1], encoding="utf-8", errors="replace").read().splitlines()
a = next(i for i, x in enumerate(L) if x.startswith("Comments specific"))
z = next(i for i, x in enumerate(L) if x.startswith("The following is a list of files"))
L = L[a+1:z]
MON = r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
def tarih(s, gevsek):
    pats = [r"\b\d{4}-\d{2}-\d{2}\b", r"\b\d{4}/\d{2}/\d{2}\b", r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
            r"\b\d{1,2} " + MON + r" \d{4}\b", r"\b" + MON + r" \d{1,2} \d{4}\b", r"\b" + MON + r" \d{4}\b",
            r"\b\d{4} \d{3}\b"]
    if gevsek:   # tam ay adı, nokta, virgül, büyük harf
        M2 = r"(Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|June?|July?|Aug(ust)?|Sept?(ember)?|Oct(ober)?|Nov(ember)?|Dec(ember)?)\.?"
        pats += [r"\b" + M2 + r" \d{1,2},? \d{4}\b", r"\b" + M2 + r",? \d{4}\b"]
    fl = 0 if not gevsek else re.I
    for p in pats:
        m = re.search(p, s, fl)
        if m: return m.group(0)
    return None
K = ["reset","re-set","rezero","re-zero","zeroed","new zero","broke","broken","break","snapped","replaced","replace",
     "new wire","new rod","new sensor","new transducer","new lvdt","moved","relocat","reinstall","re-install",
     "reposition","offset","repair","damaged","vandal","collapse","flood","rodent","out of range","overrange",
     "over-range","ran out","recalibrat"]
SON = ["abandon","removed","destroyed","decommission","no longer"]
D = ["electronics","dcp","scale factor","gain"]
for gevsek in (False, True):
    print("=== tarih tanıma:", "taslak (katı, 3 harfli ay, virgülsüz)" if not gevsek else "gevşek (tam ay adı, virgül)")
    ist, notlar, cur = None, [], None
    for i, s in enumerate(L):
        t = s.strip()
        if re.fullmatch(r"[A-Z0-9]{4}", t) or (t[:4].isupper() and t[:4].isalnum() and len(t) > 3 and t[4:5] in (" ", "") and not tarih(t, gevsek)):
            ist = t[:4]; cur = None; continue
        d = tarih(t, gevsek)
        if d:
            cur = dict(ist=ist, tarih=d, satir=i, metin=[t]); notlar.append(cur)
        elif cur is not None:
            cur["metin"].append(t)
        else:
            notlar.append(dict(ist=ist, tarih=None, satir=i, metin=[t]))
    for n in notlar:
        m = " ".join(n["metin"]).lower()
        k = [w for w in K if w in m]; so = [w for w in SON if w in m]; dd = [w for w in D if w in m]
        tur = "SON" if so else ("K" if k else ("D" if dd else None))
        if tur:
            print(f"{n['ist']}\t{n['tarih']}\t{tur}\t{k+so+dd}\t{n['metin'][0][:60]}")
