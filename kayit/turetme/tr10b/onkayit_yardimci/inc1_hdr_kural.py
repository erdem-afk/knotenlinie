# TR-10b ön kayıt sürüm 2, §6.4 madde 3 HDR kuralının (İNCELEME-1 E1 düzeltme metni) README üzerinde sınanması.
#
# Vekil metin: README'nin "Comments specific to various creepmeters" bölümü (yazarın zaten okuduğu üstveri; K_OLAY
# listesi ondan çıkarıldı). HDR dosyalarının kendisi bu betikte AÇILMAZ.
#
# Çekirdek işlevler (notlara_bol, tarih, onekler, tur, isle) §6.4 madde 3'ün metnini harfiyen uygular ve HDR adımında
# aynen kullanılır. README'ye özgü olan tek şey istasyon atamasıdır (README tek dosyada birçok istasyonu taşır;
# HDR'de not, bulunduğu .hdr1 dosyasının istasyonuna aittir): bir paragrafın ilk satırının ilk sözcüğü bilinen bir
# istasyon koduysa istasyon o olur; kod tek başına bir satırsa o satır nottan çıkarılır.
#
# Kullanım (depo kökünden):
#   python3 -I -B kayit/turetme/tr10b/onkayit_yardimci/inc1_hdr_kural.py <README_CREEP.txt> <inc1 listeler.json>
import datetime as dt
import json
import os
import re
import subprocess
import sys

BURA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(BURA))
import tr10b_sayim as KS  # noqa: E402

SON_GUN = dt.date(2023, 10, 16)

# ------------------------------------------------------------------ not birimi
AYRAC = re.compile(r"[-=*_ \t]*")


def notlara_bol(satirlar):
    """Not birimi: boş satırla ya da yalnız -, =, *, _ ve boşluktan oluşan satırla ayrılan paragraf.
    Dosyada hiç boş satır yoksa her satır bir nottur. Dönüş: [(ilk_satir_no, [satırlar])]."""
    if not any(AYRAC.fullmatch(s) for s in satirlar):
        return [(i, [s]) for i, s in enumerate(satirlar)]
    par, cur, bas = [], [], None
    for i, s in enumerate(satirlar + [""]):
        if AYRAC.fullmatch(s):
            if cur:
                par.append((bas, cur))
            cur, bas = [], None
        else:
            if bas is None:
                bas = i
            cur.append(s)
    return par


# ------------------------------------------------------------------ tarih
AY = dict(jan=1, feb=2, mar=3, apr=4, may=5, jun=6, jul=7, aug=8, sep=9, oct=10, nov=11, dec=12)
MON = (r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?|sep(?:t(?:ember)?|tember)?|"
       r"oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\.?")
YIL = r"(19\d\d|20\d\d)"
B = r"(?<![a-z0-9])"          # önünde harf ya da rakam yok
E = r"(?![a-z0-9])"           # ardında harf ya da rakam yok (tarih sonu)


def _ay(s):
    return AY[s[:3].lower()]


def _yy(s):
    return int(s) if len(s) == 4 else (1900 + int(s) if int(s) > 30 else 2000 + int(s))


TAM = [  # (desen, kurucu); sıra yalnız aynı konumda başlayan eşleşmelerde önceliği verir
    (B + YIL + r"-(\d\d)-(\d\d)" + E, lambda m: dt.date(int(m[1]), int(m[2]), int(m[3]))),
    (B + YIL + r"/(\d\d)/(\d\d)" + E, lambda m: dt.date(int(m[1]), int(m[2]), int(m[3]))),
    (B + r"(\d{1,2})/(\d{1,2})/(\d{4}|\d{2})" + E, lambda m: dt.date(_yy(m[3]), int(m[1]), int(m[2]))),
    (B + r"(\d{1,2})\s+(" + MON + r")\s+" + YIL + E, lambda m: dt.date(int(m[3]), _ay(m[2]), int(m[1]))),
    (B + r"(" + MON + r")\s+(\d{1,2}),?\s+" + YIL + E, lambda m: dt.date(int(m[3]), _ay(m[1]), int(m[2]))),
    (B + r"(" + MON + r")(?:\s*[-–—]\s*" + MON + r")?,?\s+" + YIL + E, lambda m: dt.date(int(m[2]), _ay(m[1]), 1)),
    (B + YIL + r"[ .:](\d{3})" + E, lambda m: dt.date(int(m[1]), 1, 1) + dt.timedelta(days=int(m[2]) - 1)
     if 1 <= int(m[2]) <= 366 else None),
]
YALIN = re.compile(B + r"(19[6-9]\d|20[01]\d|202[0-3])" + E)


def tarih(metin):
    """En solda başlayan tam tarih; yoksa en soldaki yalın yıl (1960–2023) → 1 Ocak; yoksa None.
    Dönüş: (tarih, 'tam' | 'yalin') ya da (None, None)."""
    m_ = metin.lower()
    aday = []
    for sira, (p, f) in enumerate(TAM):
        for m in re.finditer(p, m_):
            try:
                d = f(m)
            except (ValueError, KeyError):
                d = None
            if d is not None:
                aday.append((m.start(), sira, d))
    if aday:
        return min(aday)[2], "tam"
    m = YALIN.search(m_)
    return (dt.date(int(m[1]), 1, 1), "yalin") if m else (None, None)


# ------------------------------------------------------------------ önekler ve tür
K_ONEK = ["reset", "re-set", "rezero", "re-zero", "zero", "broke", "break", "snap", "replac", "new wire", "new rod",
          "new sensor", "new transducer", "new lvdt", "removed", "relocat", "reinstall", "re-install", "reposition",
          "offset", "repair", "damage", "vandal", "collapse", "caved", "cave-in", "cave in", "flood", "rodent",
          "gopher", "out of range", "overrange", "over-range", "ran out", "calibrat", "recalibrat", "re-calibrat",
          "miscalibrat", "mis-calibrat", "fail", "unreliab", "touch", "tighten", "loosen", "bump", "peg", "tension",
          "slid", "offline", "glitch", "spurious", "bogus", "delet", "abandon", "destroy", "decommission",
          "no longer"]
K_TAM = ["moved", "bent"]                     # yalnız tam sözcük
D_ONEK = ["electronic", "dcp", "scale factor", "gain"]
K_RE = re.compile(B + "(" + "|".join(map(re.escape, K_ONEK)) + ")|" + B + "(" + "|".join(K_TAM) + ")" + E)
D_RE = re.compile(B + "(" + "|".join(map(re.escape, D_ONEK)) + ")")
CREEP_EVENT = re.compile(B + r"(creeps?|events?)" + E)   # madde 4 sayacı: tam sözcük


def normal(metin):
    return re.sub(r"\s+", " ", metin.lower()).strip()


def onekler(metin):
    m = normal(metin)
    return sorted({x.group(0) for x in K_RE.finditer(m)}), sorted({x.group(0) for x in D_RE.finditer(m)})


def tur(metin):
    k, d = onekler(metin)
    return ("K", k) if k else (("D", d) if d else (None, []))


# ------------------------------------------------------------------ bir istasyonun notlarını olaylara çevir
def isle(notlar, ilk_gozlem):
    """notlar: [(satir_no, metin)] tek istasyon, dosya sırasıyla. Dönüş: olay listesi; her olay bir tarih (a = b)
    ya da tarihsiz not için [a, b] aralığı taşır."""
    tarihli = [(i, tarih(m)[0]) for i, (_, m) in enumerate(notlar)]
    olay = []
    for i, (sn, m) in enumerate(notlar):
        d, cins = tarih(m)
        if d is not None and d > SON_GUN:
            continue                                   # 2023-10-16 sonrası: önek aranmaz
        t, es = tur(m)
        if t is None:
            continue
        if d is not None:
            a = b = d
        else:
            onc = [x for j, x in tarihli[:i] if x is not None]
            son = [x for j, x in tarihli[i + 1:] if x is not None]
            a = onc[-1] if onc else ilk_gozlem
            b = son[0] if son else SON_GUN
            a, b = min(a, b), max(a, b)                # notlar tarih sırasında değilse uçlar yer değiştirir
        olay.append(dict(satir=sn, tur=t, es=es, a=a, b=b, tarihsiz=d is None, cins=cins,
                         creep_event=bool(CREEP_EVENT.search(normal(m))), metin=normal(m)[:70]))
    return olay


def dusen_epoklar(o):
    """Olayın düşürdüğü epoklar: [w0 − 30 g, T + 15 g] aralığı olay tarihini (ya da tarihsiz aralığı) içeren/kesen."""
    out = []
    for Y in KS.EPOK_YIL:
        P = KS.pencere(Y)
        lo, hi = P["w0"] - dt.timedelta(days=30), P["T"] + dt.timedelta(days=15)
        if o["a"] <= hi and o["b"] >= lo:
            out.append(Y)
    return out


# ------------------------------------------------------------------ README vekili
def readme_notlari(yol, kodlar):
    L = open(yol, encoding="utf-8", errors="replace").read().splitlines()
    a = next(i for i, x in enumerate(L) if x.startswith("Comments specific"))
    z = next(i for i, x in enumerate(L) if x.startswith("The following is a list of files"))
    L = L[a + 1:z]
    ist, out = None, {}
    for sn, p in notlara_bol(L):
        ilk = p[0].split()
        if ilk and ilk[0] in kodlar:
            ist = ilk[0]
            if len(ilk) == 1:
                p = p[1:]
        if not p or ist is None:
            continue
        out.setdefault(ist, []).append((a + 1 + sn + 1, " ".join(s.strip() for s in p)))
    return out


def main():
    readme, lj = sys.argv[1:3]
    d = json.load(open(lj, encoding="utf-8"))
    istb = d["sonuc"]["INC1_ist"]
    kodlar = set(istb) | {k for k, *_ in KS.K_OLAY}
    N = readme_notlari(readme, kodlar)
    olaylar = {}
    for ist, notlar in N.items():
        ilk = dt.date.fromisoformat(istb[ist]["ilk"]) if ist in istb else dt.date(1960, 1, 1)
        olaylar[ist] = isle(notlar, ilk)
    print("Olaylar (README vekili; yeni kural):")
    for ist in sorted(olaylar):
        for o in olaylar[ist]:
            ar = o["a"].isoformat() if not o["tarihsiz"] else f"[{o['a']} → {o['b']}] (tarihsiz)"
            print(f"  {ist}\tsatır {o['satir']}\t{o['tur']}\t{ar}\t{o['cins'] or ''}\t{o['es']}\t{o['metin'][:55]}")

    # 1) K_OLAY olay düzeyi: aynı istasyonda, olay tarihinden ≤ 366 gün önceki tarihli K olayı (İNCELEME-1 ölçütü)
    print("\nK_OLAY karşılaştırması (README yorum bölümünde açıklaması bulunan olaylar):")
    yak = top = 0
    kacan = []
    for kod, t, ac in KS.K_OLAY:
        if kod not in olaylar:
            print("   yorum yok:", kod, t)
            continue
        t = dt.date.fromisoformat(t); top += 1
        hit = [o for o in olaylar[kod] if o["tur"] == "K" and not o["tarihsiz"] and o["a"] <= t
               and (t - o["a"]).days <= 366]
        yak += bool(hit)
        if not hit:
            kacan.append((kod, t))
        print("  ", kod, t, ("BULUNDU " + hit[0]["a"].isoformat()) if hit else "KAÇTI", "|", ac)
    print(f"yakalanan {yak} / {top}; kaçan {kacan}")
    print("sahte son veren olay: 0 (kural son veren tür üretmez); eski son veren sözcüklerini taşıyan K olayı:",
          sum(1 for v in olaylar.values() for o in v
              if any(w in o["metin"] for w in ("abandon", "removed", "destroy", "decommission", "no longer"))))

    # 2) epok düzeyi: K_OLAY'ın düşürdüğü (istasyon, epok)lar ile kuralın düşürdükleri (bütün epoklar, aday olsun olmasın)
    kol = set()
    for kod, t, _ in KS.K_OLAY:
        if kod in olaylar:
            t = dt.date.fromisoformat(t)
            kol |= {(kod, Y) for Y in dusen_epoklar(dict(a=t, b=t))}
    kur = {(ist, Y) for ist, v in olaylar.items() for o in v if o["tur"] == "K" for Y in dusen_epoklar(o)}
    print(f"\nEpok düzeyi: K_OLAY {len(kol)} (istasyon, epok); kural {len(kur)}; ortak {len(kol & kur)}")
    print("   K_OLAY'da olup kuralda olmayan:", sorted(kol - kur))
    print("   kuralda olup K_OLAY'da olmayan:", sorted(kur - kol))

    # 3) aday listelerine etkisi (K_OLAY zaten uygulanmış listeler; kural fazladan ne düşürür)
    for ad in ("B_U", "A_U", "B_R2"):
        L = {(k, y) for k, y, *_ in d["sonuc"]["INC1_listeler"][ad]}
        print(f"{ad}: kuralın K olaylarıyla düşen {sorted(L & kur)}; D olaylarıyla ('D dışarıda' bilgi satırı) "
              f"düşen {sorted(L & {(i, Y) for i, v in olaylar.items() for o in v if o['tur'] == 'D' for Y in dusen_epoklar(o)})}")
    print("madde 4 sayacı (README vekili): K olaylarından notunda 'creep(s)'/'event(s)' sözcüğü geçen:",
          [(i, o["a"].isoformat()) for i, v in olaylar.items() for o in v if o["tur"] == "K" and o["creep_event"]])

    # 4) taslak (sürüm 1) kuralının aynı listelere etkisi: İNCELEME-1 inc10b/hdr_kural.py çıktısındaki son veren olaylar
    out = subprocess.run([sys.executable, "-I", "-B", os.path.join(BURA, "inc10b", "hdr_kural.py"), readme],
                         capture_output=True, text=True, check=True).stdout
    BU = {(k, y) for k, y, *_ in d["sonuc"]["INC1_listeler"]["B_U"]}
    for blok in out.split("=== ")[1:]:
        bas = blok.splitlines()[0]
        son = []
        for x in blok.splitlines()[1:]:
            p = x.split("\t")
            if len(p) > 2 and p[2] == "SON" and p[1] != "None":
                m = re.match(r"([A-Za-z]+)\.? (?:(\d{1,2}),? )?(\d{4})", p[1])
                son.append((p[0], dt.date(int(m[3]), AY[m[1][:3].lower()], int(m[2] or 1))))
        dus = sorted((k, y) for k, y in BU for kk, t in son if k == kk and t <= KS.pencere(y)["T"])
        print(f"sürüm 1 kuralı ({bas.strip()}): son veren {son}; B_U'dan düşen {dus}")


if __name__ == "__main__":
    main()
