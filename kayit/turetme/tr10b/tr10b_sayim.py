#!/usr/bin/env python3
"""TR-10b üstveri sayımı (kör): USGS sünme ölçerlerinde depremsiz 5 yıllık pencerelerde 2 yıllık sünme hızı
değişiminin taban dağılımı için kaç istasyon-pencere, istasyon, site ve fay kesimi var?

SINAV KOŞULMAZ. Hiçbir sünme ölçer veri dosyasının (DAY, 10MIN, MIC, CL10, HDR, jl) İÇERİĞİ okunmaz.
Okunanlar yalnız: USGS indirme sayfası (istasyon tablosu ve bağlantılar), arşivin README dosyası (biçim belgesi,
dosya tarih aralıkları listesi, aygıt notları), her veri bağlantısına HEAD isteği (boy ve Last-Modified).
ComCat sorguları 2025-12-31'de biter (tr2_sayim.sorgu assert eder). 2026 deprem verisi kördür.

Kullanım (depo kökünden):
  python3 -I -B kayit/turetme/tr10b/tr10b_sayim.py say <ham_dizin> <cikti.json> <tr10_ham_dizin>
  python3 -I -B kayit/turetme/tr10b/tr10b_sayim.py beklenti            # yalnız yapay gürültü, veri okumaz
  python3 -I -B kayit/turetme/tr10b/tr10b_sayim.py denetim_on <N_sw>   # kod denetimi eşiklerinin yapay doğrulaması

<ham_dizin> içinde önbellek: head_sonuc.tsv (HEAD sonuçları), README_CREEP.txt, comcat_m45.csv.
<tr10_ham_dizin> içinde: usgs_download.html (TR-10 anlık görüntüsü, sha256 74b3eb43…).
"""
import csv
import datetime as dt
import hashlib
import html
import json
import math
import os
import re
import sys
import urllib.request

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(KOK, "tr2"))
import tr2_sayim as T2  # noqa: E402  (sorgu: bitiş assert'i; mesafe_az)

ARSIV = "https://escweb.wr.usgs.gov/share/langbein/Archive/CREEP/"
README_URL = ARSIV + "README"
SAYFA_SHA = "74b3eb437b530436231e9758fe3d1c18d71c09c351530820e08bc32bb0f0edc1"
KESIM_TARIH = dt.date(2025, 12, 31)          # kırpma; 2026 hiçbir yerde kullanılmaz

# ---------------------------------------------------------------- önceden sabit tasarım sabitleri
EPOK_YIL = list(range(1973, 2024, 5))        # T = Y-10-01; pencere [Y-5, Y) su yılı; menteşe Y-2
UC_YARI = 15                                 # uç noktası değeri: P ± 15 gün (31 gün) medyanı
# Sakinlik (istasyon noktasına uzaklık; ComCat type=earthquake):
S1 = dict(M=5.0, R=50.0, Z=30.0, once=2, sonra=2)      # yakın orta olay: [w0-2y, T+2y]
S2 = dict(M=6.0, R=150.0, Z=40.0, once=5, sonra=2)     # bölgesel M6: [w0-5y, T+2y]
S3 = dict(M=7.0, R=500.0, Z=70.0, once=2, sonra=0)     # uzak M7 (tetiklenmiş sünme): [w0-2y, T]
K_TAMPON = 30                                          # K olayı [w0-30 g, T] içindeyse pencere düşer
# B kural seti (kırık boyuna ölçekli; A ile birlikte önceden yazılır, ikisi de raporlanır):
#  B1: geçmiş/iç etki: M>=4,5, z<=30, uzaklık <= max(10 km, 5 L(M)) (L: Wells-Coppersmith doğrultu atımlı,
#      tr2_sayim.L_km), zaman [w0-2y, T];
#  B2: hedef olay öncesi dışlama (TR-10 tanımı): M>=5,5, z<=30, <=50 km, zaman (T, T+2y];
#  B3: uzak büyük (dinamik tetikleme): M>=7,0, z<=70, <=500 km, zaman [w0, T].
B1 = dict(M=4.5, R=None, RL=5.0, Rmin=10.0, Z=30.0, once=2, sonra=0)
B2 = dict(M=5.5, R=50.0, Z=30.0, once=None, sonra=2)
B3 = dict(M=7.0, R=500.0, Z=70.0, once=0, sonra=0)

# Fay kesimi (bağımsızlık bloğu): fay + enlem sınırları önceden sabit.
def kesim(fay, la):
    if fay.startswith("Calaveras"):
        return "CAL_Hollister"
    if fay.startswith("Hayward"):
        return "HAY"
    if la >= 36.70:
        return "SAF_SJB"          # San Juan Bautista–Cienega
    if la >= 36.00:
        return "SAF_sunen_orta"   # Frank Lewis–Slack Canyon
    if la >= 35.70:
        return "SAF_Parkfield"
    return "SAF_guney_gecis"      # Cholame–Carrizo (Twisselman, Panorama Hills)

# "Big Creep" düşük çözünürlüklü eş ölçerler ana sayıma girmez (README: "Telemetried but not edited").
BIG_CREEP = {"XMBC", "TABC"}

# README "Comments specific to various creepmeters" ve durum tablosundan dondurulmuş K olayları
# (kopma, yeniden sıfırlama, sensör/çubuk değişimi, taşma, çarpma, göçük, sahte aralık, güvenilmezlik).
# Tarih bilinmeyen gün ayın 1'i, bilinmeyen ay yılın 1 Ocak'ı alınır (tutucu: aralık başı).
K_OLAY = [
    ("CRR1", "1998-02-10", "sensör arızası, ölçek değişimi"),
    ("CRR1", "1999-12-02", "telemetri silindi + 5,9 mm eklendi (1999-12-02..2000-02-21)"),
    ("CRR1", "2004-09-28", "Parkfield taşma, tel kaydırıldı"),
    ("CWN1", "2003-06-04", "ankraj sıkıldı, ≈2 mm olası ötelenme"),
    ("CWN1", "2012-04-20", "çarpma, mil eğik"),
    ("CWN1", "2013-03-19", "çubuk değişti"),
    ("CWC3", "2000-01-01", "2000'den beri güvenilmez (cıvata)"),
    ("WKR1", "2004-09-28", "Parkfield taşma"),
    ("WKR1", "2004-11-01", "ölçek düzeltmesi 2004-11..2005-02"),
    ("XGH1", "1997-12-01", "sahte sol yanal hareket 1997-12..1998-04, zorlanmış ötelenme"),
    ("XHR2", "2004-06-01", "kanal göçtü, ölçer terk"),
    ("XHSW", "1998-12-01", "boru tele değiyor"),
    ("XHSW", "2010-07-01", "boru göçtü, elektronik söküldü"),
    ("XMD1", "2004-09-28", "Parkfield taşma; elektronik %50 kayıt"),
    ("XMM1", "1996-03-07", "elektronik değişimi, olası ötelenme"),
    ("XMM1", "1993-01-01", "1993-1996 kalibrasyon hatası"),
    ("XMM1", "1986-01-01", "1986-1988 olası kalibrasyon hatası"),
    ("XMM1", "2004-09-28", "Parkfield taşma"),
    ("XMM1", "2005-09-01", "kanal ayrıldı, tel değişti"),
    ("XMR1", "2010-07-01", "kanal göçtü"),
    ("XMR1", "2010-10-01", "kemirgen, ≥1 mm uyuşmazlık"),
    ("XPK1", "1998-12-01", "boru tele değiyor"),
    ("XPK1", "2004-09-28", "tel koptu, sıfır kayboldu"),
    ("XRSW", "1998-08-01", "tel koptu, bilinmeyen ötelenme (1999-01'e dek)"),
    ("XRSW", "2005-09-01", "tel koptu, terk"),
    ("XSC1", "1997-03-06", "transdüser değişti, bağ belirsiz"),
    ("XSJ2", "2006-07-01", "tel koptu"),
    ("XSJ3", "2007-02-15", "yeni sıfır"),
    ("XTA1", "2004-09-28", "Parkfield taşma"),
    ("XVA1", "2004-09-28", "Parkfield taşma"),
    ("XFL1", "1995-03-11", "1999'da tel koptu, terk (DAY 1995-03'te bitiyor)"),
    ("XMBC", "2011-01-12", "potansiyometre arızası, çevrimdışı"),
]
# Son veren (terminal) K olayları: tarihten sonraki bütün pencereler de düşer (terk, kalıcı güvenilmezlik,
# kod değişimi: XPK1→XPK2, XSJ2→XSJ3, XHR2→XHR3).
K_SON = {("CWC3", "2000-01-01"), ("XHR2", "2004-06-01"), ("XHSW", "2010-07-01"), ("XRSW", "2005-09-01"),
         ("XFL1", "1995-03-11"), ("XPK1", "2004-09-28"), ("XSJ2", "2006-07-01"), ("XMBC", "2011-01-12")}
# D olayları: 2006-2008 DCP/elektronik değişimi (ölçek ve ötelenme README'de veriliyor). Ana sayımda kalır,
# bilgi satırında düşer.
D_OLAY = [("XSC1", "2007-01-23"), ("XMM1", "2007-05-08"), ("XMD1", "2006-11-29"), ("XVA1", "2006-11-28"),
          ("XPK2", "2006-11-28"), ("XTA1", "2006-11-30"), ("WKR1", "2006-11-30"), ("CRR1", "2007-04-19"),
          ("XGH1", "2006-11-29"), ("XSJ3", "2007-11-28"), ("CWN1", "2008-05-29"), ("XMR1", "2008-05-28")]


def gun(s):
    return dt.date.fromisoformat(s)


def yil_ekle(d, n):
    try:
        return d.replace(year=d.year + n)
    except ValueError:
        return d.replace(year=d.year + n, day=28)


# ---------------------------------------------------------------- üstveri: sayfa
def sayfa_istasyonlar(tr10_ham):
    fn = os.path.join(tr10_ham, "usgs_download.html")
    b = open(fn, "rb").read()
    assert hashlib.sha256(b).hexdigest() == SAYFA_SHA, "indirme sayfası anlık görüntüsü değişmiş"
    t = b.decode("utf-8", "replace")
    a = t.find("Creepmeter"); z = t.find("Dilatometer", a)
    fay, out = None, []
    for r in re.findall(r"<tr.*?</tr>", t[a:z], re.S):
        h3 = re.search(r"<h3>(.*?)</h3>", r)
        if h3:
            fay = h3.group(1).strip(); continue
        td = re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)
        if len(td) < 9:
            continue
        hucre = lambda x: html.unescape(re.sub(r"<[^>]+>", " ", x)).strip()
        kod = hucre(td[1])
        lnk = [re.findall(r'href="([^"]+)"', x) for x in td[5:9]]
        s = dict(ad=hucre(td[0]), kod=kod, lat=float(hucre(td[2])), lon=float(hucre(td[3])),
                 ilk_ham=hucre(td[4]), fay=fay,
                 dosya={"HDR": lnk[0], "MIC": lnk[1], "10MIN": lnk[2], "DAY": lnk[3]})
        y = re.findall(r"\d{2,4}", s["ilk_ham"])[-1]
        y = int(y) if len(y) == 4 else (1900 + int(y) if int(y) > 30 else 2000 + int(y))
        ay = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9,
              "Oct": 10, "Nov": 11, "Dec": 12}
        m = re.match(r"([A-Z][a-z]{2})", s["ilk_ham"])
        s["ilk"] = dt.date(y, ay[m.group(1)] if m else 1, 1)
        out.append(s)
    for s in out:   # SJN1 boylamı sayfada 0 (TR-10 notu); yalnız uzaklık için XSJ2 boylamı
        if s["lon"] == 0.0:
            s["lon"] = next(x["lon"] for x in out if x["kod"] == "XSJ2"); s["not"] = "boylam sayfada 0; XSJ2'den"
    return out


# ---------------------------------------------------------------- üstveri: HEAD
def head_sonuclari(ham, ist):
    fn = os.path.join(ham, "head_sonuc.tsv")
    if not os.path.exists(fn):
        rows = []
        for s in ist:
            for tur, ls in s["dosya"].items():
                for u in ls:
                    req = urllib.request.Request(u, method="HEAD")
                    try:
                        with urllib.request.urlopen(req, context=T2.CTX, timeout=60) as r:
                            rows.append((u, str(r.status), r.headers.get("Content-Length", ""),
                                         r.headers.get("Last-Modified", "")))
                    except Exception as e:  # noqa
                        rows.append((u, "hata:" + type(e).__name__, "", ""))
        open(fn, "w").write("".join("\t".join(r) + "\n" for r in rows))
    H = {}
    for ln in open(fn):
        p = ln.rstrip("\n").split("\t")
        lm = None
        if len(p) > 3 and p[3]:
            lm = dt.datetime.strptime(p[3], "%a, %d %b %Y %H:%M:%S GMT").date()
        H[p[0]] = dict(boy=int(p[2]) if len(p) > 2 and p[2] else None, lm=lm)
    return H


# ---------------------------------------------------------------- üstveri: README (biçim belgesi)
def readme_araliklar(ham):
    fn = os.path.join(ham, "README_CREEP.txt")
    if not os.path.exists(fn):
        with urllib.request.urlopen(README_URL, context=T2.CTX, timeout=60) as r:
            open(fn, "wb").write(r.read())
    t = open(fn, encoding="utf-8", errors="replace").read()
    out, bolum = {}, None
    pat = re.compile(r"^(\w+)\.(m|day|r|sc): \d\d:\d\d (\d\d) (\w{3}) (\d{4}) \d+ -> \d\d:\d\d (\d\d) (\w{3}) (\d{4})")
    ay = {m: i + 1 for i, m in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split())}
    for ln in t.splitlines():
        if ln.strip() in ("MIC", "DAY", "CL10", "PKF_EQ"):
            bolum = ln.strip(); continue
        m = pat.match(ln.strip())
        if m and bolum:
            kod = m.group(1).upper()
            a = dt.date(int(m.group(5)), ay[m.group(4)], int(m.group(3)))
            b = dt.date(int(m.group(8)), ay[m.group(7)], int(m.group(6)))
            out.setdefault(kod, {}).setdefault(bolum, []).append((a, b))
    return out, hashlib.sha256(open(fn, "rb").read()).hexdigest()


# ---------------------------------------------------------------- kapsam modeli (içerik okunmadan)
def kapsam(s, H, RM):
    """Üç kapsam senaryosu (içerik okunmadan):
    'R'  katı: README dosya listesi (2013 anlık görüntüsü) aralıkları; 10MIN dosyası bugün güncelleniyorsa
         (Last-Modified >= 2026-01-01) telemetri sonu 2025-12-31'e uzar (README 2011: 10MIN "all time");
         README'de telemetri aralığı olmayan etkin 10MIN istasyonunda başlangıç sayfadaki ilk gözlem.
    'R2' ana: R + OFR 2024-1011 özeti ("mid-2020"e dek veri): README aralığı 2013'e ulaşan (son >= 2012-01-01)
         DAY/CL10 ve MIC aralıkları, dosyanın Last-Modified tarihi >= 2020-07-01 ise 2020-06-30'a uzar;
         etkin olmayan 10MIN dosyası (Last-Modified < 2026) varsa telemetri aralığı Last-Modified tarihine
         dek uzar (günlük eklenen dosyada Last-Modified ≈ son veri günü varsayımı); README telemetri aralığı
         yoksa başlangıç sayfadaki ilk gözlem.
    'U'  üst sınır: sayfadaki ilk gözlem → dosyaların en geç Last-Modified tarihi (dosya kendi değişiklik
         tarihinden sonraki veriyi taşıyamaz); tek kayıt türü ayrımı yok."""
    kod = s["kod"]
    lm = {tur: max([H[u]["lm"] for u in ls if H.get(u) and H[u]["lm"]] or [None], key=lambda x: x or dt.date.min)
          for tur, ls in s["dosya"].items() if tur != "HDR"}
    etkin10 = bool(lm.get("10MIN")) and lm["10MIN"] >= dt.date(2026, 1, 1)
    r = RM.get(kod, {})
    # README aralığının başı sayfadaki ilk gözlemden önceyse (ör. XSC1 DAY 1969, kurulum 1979) ilk gözlemle kırpılır.
    kirp = lambda ivs: [(max(a, s["ilk"]), b) for a, b in ivs if b > s["ilk"]]
    tele0 = kirp([iv for b in ("DAY", "CL10") for iv in r.get(b, [])])
    man0 = kirp(list(r.get("MIC", [])))
    # R
    if etkin10:
        tele = [(min([x[0] for x in tele0] or [s["ilk"]]), KESIM_TARIH)]
    else:
        tele = list(tele0)
    man = list(man0)
    # R2
    OFR_SON = dt.date(2020, 6, 30)
    tele2, man2 = list(tele), list(man)
    yasar = bool(tele0) and max(x[1] for x in tele0) >= dt.date(2012, 1, 1)   # README anında çalışıyordu
    if not etkin10 and yasar:
        son2 = OFR_SON if (lm.get("DAY") or lm.get("10MIN") or dt.date.min) >= dt.date(2020, 7, 1) else max(
            x[1] for x in tele0)
        # 2020-07-09 toplu arşiv tarihidir (79 dosyada aynı); daha geç ama 2026'dan önceki bir 10MIN tarihi
        # (CWN1 2023-12, XGH1 2023-06) telemetrinin o tarihte durduğu varsayımıyla son kabul edilir.
        if lm.get("10MIN") and lm["10MIN"] > dt.date(2020, 12, 31):
            son2 = min(lm["10MIN"], KESIM_TARIH)
        tele2 = [(min(x[0] for x in tele0), son2)]
    if man0 and max(x[1] for x in man0) >= dt.date(2012, 1, 1) and (lm.get("MIC") or dt.date.min) >= dt.date(2020, 7, 1):
        man2 = [(min(x[0] for x in man0), OFR_SON)]
    U_son = max([d for d in lm.values() if d] or [s["ilk"]])
    U_son = min(U_son, KESIM_TARIH)
    return dict(R_tele=tele, R_man=man, R2_tele=tele2, R2_man=man2, U=(s["ilk"], U_son), etkin10=etkin10,
                lm={k: (v.isoformat() if v else None) for k, v in lm.items()})


def icinde(ivs, a, b):
    return any(x[0] <= a and b <= x[1] for x in ivs)


# ---------------------------------------------------------------- ComCat
def olaylar(ham):
    fn = os.path.join(ham, "comcat_m45.csv")
    if not os.path.exists(fn):
        t = T2.sorgu({"format": "csv", "starttime": "1955-01-01", "endtime": T2.BITIS, "minmagnitude": 4.5,
                      "minlatitude": 30.5, "maxlatitude": 42.5, "minlongitude": -128.0, "maxlongitude": -113.0,
                      "orderby": "time-asc", "limit": 20000})
        open(fn, "w").write(t)
    out = []
    for r in csv.DictReader(open(fn)):
        if r["type"] != "earthquake" or not r["mag"]:
            continue
        d = dt.date.fromisoformat(r["time"][:10])
        assert d <= KESIM_TARIH
        out.append(dict(id=r["id"], t=d, lat=float(r["latitude"]), lon=float(r["longitude"]),
                        z=float(r["depth"] or 0), m=float(r["mag"]), yer=r["place"]))
    return out, hashlib.sha256(open(fn, "rb").read()).hexdigest()


# ---------------------------------------------------------------- pencere ve sakinlik
def pencere(Y):
    T = dt.date(Y, 10, 1)
    return dict(Y=Y, w0=dt.date(Y - 5, 10, 1), H=dt.date(Y - 2, 10, 1), T=T,
                ilk=dt.date(Y - 5, 10, 1) - dt.timedelta(days=UC_YARI), son=T + dt.timedelta(days=UC_YARI))


def ihlaller(s, P, E, kurallar):
    """Pencereyi düşüren olaylar: [(kural, olay)]."""
    out = []
    for ad, k in kurallar.items():
        if k["once"] is None:      # yalnız gelecek: (T, T+sonra]
            a = P["T"] + dt.timedelta(days=1)
        else:
            a = yil_ekle(P["w0"], -k["once"])
        b = yil_ekle(P["T"], k["sonra"])
        for e in E:
            if e["m"] >= k["M"] and e["z"] <= k["Z"] and a <= e["t"] <= b:
                R = k["R"] if k.get("R") is not None else max(k["Rmin"], k["RL"] * T2.L_km(e["m"]))
                if T2.mesafe_az(s["lat"], s["lon"], e["lat"], e["lon"])[0] <= R:
                    out.append((ad, e))
    return out


def k_ihlal(kod, P, liste):
    a = P["w0"] - dt.timedelta(days=K_TAMPON)
    return [x for x in liste if x[0] == kod and (a <= gun(x[1]) <= P["T"] or
                                                  ((x[0], x[1]) in K_SON and gun(x[1]) <= P["T"]))]


# ---------------------------------------------------------------- sayım
def say(ham, cikti, tr10_ham):
    os.makedirs(ham, exist_ok=True)
    ist = sayfa_istasyonlar(tr10_ham)
    H = head_sonuclari(ham, ist)
    RM, readme_sha = readme_araliklar(ham)
    E, cc_sha = olaylar(ham)
    for s in ist:
        s["kesim"] = kesim(s["fay"], s["lat"])
        s["site"] = f"{s['lat']:.3f},{s['lon']:.3f}"
        s["kapsam"] = kapsam(s, H, RM)
    P_list = [pencere(Y) for Y in EPOK_YIL]
    assert max(P["son"] for P in P_list) <= KESIM_TARIH
    assert max(yil_ekle(P["T"], 2) for P in P_list) <= KESIM_TARIH

    def degerlendir(kapsam_sen="R2", kurallar=None, k_ac=True, d_ac=False, mic=True, big=False):
        kurallar = {"S1": S1, "S2": S2, "S3": S3} if kurallar is None else kurallar
        sw = []
        for s in ist:
            if s["kod"] in BIG_CREEP and not big:
                continue
            for P in P_list:
                kp = s["kapsam"]
                if kapsam_sen == "U":
                    tur = "tele/man" if (kp["U"][0] <= P["ilk"] and P["son"] <= kp["U"][1]) else None
                else:
                    on = "R2_" if kapsam_sen == "R2" else "R_"
                    tur = ("tele" if icinde(kp[on + "tele"], P["ilk"], P["son"]) else
                           ("man" if mic and icinde(kp[on + "man"], P["ilk"], P["son"]) else None))
                if not tur:
                    continue
                if k_ac and k_ihlal(s["kod"], P, K_OLAY):
                    continue
                if d_ac and k_ihlal(s["kod"], P, D_OLAY):
                    continue
                if ihlaller(s, P, E, kurallar):
                    continue
                sw.append(dict(kod=s["kod"], Y=P["Y"], tur=tur, site=s["site"], kesim=s["kesim"]))
        return sw

    def ozet(sw):
        # site-pencere: aynı site ve epokta tek istasyon (en erken ilk gözlem, eşitlikte kod sırası)
        ilk = {s["kod"]: s["ilk"] for s in ist}
        sp = {}
        for x in sorted(sw, key=lambda x: (ilk[x["kod"]], x["kod"])):
            sp.setdefault((x["site"], x["Y"]), x)
        spv = list(sp.values())
        return {"istasyon_pencere": len(sw), "istasyon": len({x["kod"] for x in sw}),
                "site_pencere": len(spv), "site": len({x["site"] for x in spv}),
                "kesim": len({x["kesim"] for x in spv}),
                "kesim_basina_site_pencere": dict(sorted(
                    ((k, sum(1 for x in spv if x["kesim"] == k)) for k in {x["kesim"] for x in spv}))),
                "epok_basina_site_pencere": {Y: sum(1 for x in spv if x["Y"] == Y) for Y in EPOK_YIL},
                "tur": {t: sum(1 for x in spv if x["tur"] == t) for t in sorted({x["tur"] for x in spv})}}

    sdict_on = {s["kod"]: s for s in ist}
    sonuc = {}
    ana = degerlendir()
    sonuc["ana"] = ozet(ana)
    # kapsam (sakinlik ve K olmadan): elemenin tabanı
    sonuc["kapsam_yalniz_R"] = ozet(degerlendir("R", kurallar={}, k_ac=False))
    sonuc["kapsam_yalniz_R2"] = ozet(degerlendir("R2", kurallar={}, k_ac=False))
    sonuc["kapsam_yalniz_U"] = ozet(degerlendir("U", kurallar={}, k_ac=False))
    deg = {
        "U_ust_sinir_kapsam": dict(kapsam_sen="U"),
        "R_kati_kapsam": dict(kapsam_sen="R"),
        "S1_kapali": dict(kurallar={"S2": S2, "S3": S3}),
        "S2_kapali": dict(kurallar={"S1": S1, "S3": S3}),
        "S3_kapali": dict(kurallar={"S1": S1, "S2": S2}),
        "S1_S2_S3_kapali": dict(kurallar={}),
        "S1_M4.5": dict(kurallar={"S1": dict(S1, M=4.5), "S2": S2, "S3": S3}),
        "S1_R30": dict(kurallar={"S1": dict(S1, R=30.0), "S2": S2, "S3": S3}),
        "S2_R100": dict(kurallar={"S1": S1, "S2": dict(S2, R=100.0), "S3": S3}),
        "S3_once5_sonra2": dict(kurallar={"S1": S1, "S2": S2, "S3": dict(S3, once=5, sonra=2)}),
        "K_kapali": dict(k_ac=False),
        "D_acik_(DCP_degisimi_duser)": dict(d_ac=True),
        "yalniz_telemetri_(MIC_yok)": dict(mic=False),
        "Big_Creep_dahil": dict(big=True),
    }
    sonuc["degiskeler"] = {k: ozet(degerlendir(**v)) for k, v in deg.items()}
    KB = {"B1": B1, "B2": B2, "B3": B3}
    sonuc["B_ana"] = ozet(degerlendir(kurallar=KB))
    degB = {
        "B_U_ust_sinir_kapsam": dict(kapsam_sen="U", kurallar=KB),
        "B_R_kati_kapsam": dict(kapsam_sen="R", kurallar=KB),
        "B1_kapali": dict(kurallar={"B2": B2, "B3": B3}),
        "B2_kapali": dict(kurallar={"B1": B1, "B3": B3}),
        "B3_kapali": dict(kurallar={"B1": B1, "B2": B2}),
        "B1_RL10": dict(kurallar={"B1": dict(B1, RL=10.0), "B2": B2, "B3": B3}),
        "B1_RL3": dict(kurallar={"B1": dict(B1, RL=3.0), "B2": B2, "B3": B3}),
        "B1_M4.0": dict(kurallar={"B1": dict(B1, M=4.0), "B2": B2, "B3": B3}),
        "B1_once5": dict(kurallar={"B1": dict(B1, once=5), "B2": B2, "B3": B3}),
        "B3_R300": dict(kurallar={"B1": B1, "B2": B2, "B3": dict(B3, R=300.0)}),
        "B_yalniz_telemetri": dict(kurallar=KB, mic=False),
        "B_D_acik": dict(kurallar=KB, d_ac=True),
    }
    sonuc["B_degiskeler"] = {k: ozet(degerlendir(**v)) for k, v in degB.items()}
    tabB = degerlendir(kurallar={}, k_ac=True)
    sayB = {}
    for x in tabB:
        ih = ihlaller(sdict_on[x["kod"]], pencere(x["Y"]), E, KB)
        for kural, e in ih:
            z = sayB.setdefault(e["id"], dict(t=e["t"].isoformat(), m=e["m"], yer=e["yer"], kurallar=set(), sw=set()))
            z["kurallar"].add(kural); z["sw"].add((x["kod"], x["Y"]))
    sonuc["B_eleyen_olaylar_ilk25"] = sorted(({"tarih": v["t"], "M": v["m"], "yer": v["yer"],
                                              "kural": sorted(v["kurallar"]), "eledigi": len(v["sw"])}
                                             for v in sayB.values()), key=lambda r: -r["eledigi"])[:25]
    sonuc["B_ana_liste"] = sorted(((x["kod"], x["Y"], x["tur"], x["kesim"]) for x in degerlendir(kurallar=KB)))

    # hangi olay ne kadar eliyor (kapsamı R olan, K'den geçen istasyon-pencereler üzerinden)
    tab = degerlendir(kurallar={}, k_ac=True)
    sayac, tek = {}, {}
    sdict = {s["kod"]: s for s in ist}
    for x in tab:
        P = pencere(x["Y"]); ih = ihlaller(sdict[x["kod"]], P, E, {"S1": S1, "S2": S2, "S3": S3})
        ids = {e["id"] for _, e in ih}
        for kural, e in ih:
            z = sayac.setdefault(e["id"], dict(t=e["t"].isoformat(), m=e["m"], yer=e["yer"], kurallar=set(),
                                               sw=set()))
            z["kurallar"].add(kural); z["sw"].add((x["kod"], x["Y"]))
        if len(ids) == 1:
            i = next(iter(ids)); tek[i] = tek.get(i, 0) + 1
    eleyen = sorted(({"id": k, "tarih": v["t"], "M": v["m"], "yer": v["yer"], "kural": sorted(v["kurallar"]),
                      "eledigi_istasyon_pencere": len(v["sw"]), "tek_neden": tek.get(k, 0)}
                     for k, v in sayac.items()), key=lambda r: -r["eledigi_istasyon_pencere"])
    sonuc["eleyen_olaylar_ilk40"] = eleyen[:40]
    sonuc["eleme_kural_basina"] = {}
    for kural in ("S1", "S2", "S3"):
        n = 0
        for x in tab:
            if ihlaller(sdict[x["kod"]], pencere(x["Y"]), E, {kural: {"S1": S1, "S2": S2, "S3": S3}[kural]}):
                n += 1
        sonuc["eleme_kural_basina"][kural] = n
    sonuc["eleme_K"] = len(degerlendir(kurallar={}, k_ac=False)) - len(tab)

    istasyon_tablo = []
    for s in ist:
        kp = s["kapsam"]
        istasyon_tablo.append(dict(
            kod=s["kod"], ad=s["ad"], fay=s["fay"], kesim=s["kesim"], lat=s["lat"], lon=s["lon"],
            ilk_gozlem_sayfa=s["ilk_ham"], dosyalar=[t for t, ls in s["dosya"].items() if ls],
            boy={t: [H[u]["boy"] for u in ls if u in H] for t, ls in s["dosya"].items() if ls},
            last_modified=kp["lm"], etkin_10MIN=kp["etkin10"],
            R2_tele=[(a.isoformat(), z.isoformat()) for a, z in kp["R2_tele"]],
            R2_man=[(a.isoformat(), z.isoformat()) for a, z in kp["R2_man"]],
            readme={b: [(a.isoformat(), z.isoformat()) for a, z in ivs] for b, ivs in RM.get(s["kod"], {}).items()},
            ana_site_pencere=sum(1 for x in ana if x["kod"] == s["kod"]), not_=s.get("not", "")))
    meta = {"sayfa_sha256": SAYFA_SHA, "readme_sha256": readme_sha, "comcat_sha256": cc_sha,
            "comcat_olay_N": len(E), "epoklar": EPOK_YIL, "S1": S1, "S2": S2, "S3": S3, "B1": B1, "B2": B2, "B3": B3,
            "big_creep_disarida": sorted(BIG_CREEP), "K_olay_N": len(K_OLAY), "K_son_N": len(K_SON)}
    json.dump({"meta": meta, "sonuc": sonuc, "istasyonlar": istasyon_tablo,
               "ana_liste": sorted(ana, key=lambda x: (x["kod"], x["Y"]))},
              open(cikti, "w"), ensure_ascii=False, indent=1, default=str)
    print(json.dumps({"meta": meta, "sonuc": {k: v for k, v in sonuc.items()
                                              if k not in ("eleyen_olaylar_ilk40", "B_eleyen_olaylar_ilk25")}},
                     ensure_ascii=False, indent=1, default=str))
    print("Eleyen olaylar (ilk 25):")
    for r in eleyen[:25]:
        print(r["tarih"], r["M"], r["yer"], r["kural"], r["eledigi_istasyon_pencere"], "tek neden:", r["tek_neden"])
    print("İstasyon tablosu:")
    for r in istasyon_tablo:
        print(r["kod"], r["kesim"], r["ilk_gozlem_sayfa"], r["dosyalar"], r["last_modified"], r["etkin_10MIN"],
              {b: [f"{a[:7]}→{z[:7]}" for a, z in v] for b, v in r["readme"].items()}, "ana:", r["ana_site_pencere"])


# ---------------------------------------------------------------- yapay gürültü: ölçü ve beklenti
def _np():
    import numpy as np
    return np


def gunler(Y):
    P = pencere(Y)
    n = (P["son"] - P["ilk"]).days + 1
    t = lambda d: (d - P["ilk"]).days
    return P, n, t(P["w0"]), t(P["H"]), t(P["T"])


def pl_seri(n, ust, A, rng, np):
    """Güç yasası gürültüsü (Langbein/Williams kesirli integral), indis ust, genlik A mm/yıl^(ust/4); günlük."""
    dT = 1.0 / 365.25
    h = np.ones(n)
    for k in range(1, n):
        h[k] = h[k - 1] * (k - 1 + ust / 2.0) / k
    w = rng.standard_normal(n)
    return A * dT ** (ust / 4.0) * np.convolve(w, h)[:n]


def uc_deger(x, maske, i, np, man=False):
    """Uç noktası değeri: [i-15, i+15] günlerindeki geçerli günlerin medyanı; < 10 gün ise None."""
    a, b = max(0, i - UC_YARI), i + UC_YARI + 1
    v = x[a:b][maske[a:b]]
    if len(v) < 10:
        return None
    return float(np.median(v))


def dv_uc(x, maske, i0, iH, iT, np):
    """Ana ölçü: Δv = (u(T)-u(H))/τ2 - (u(H)-u(w0))/τ3, τ gerçek gün sayısı/365,25. Ayrıca v5 (pencere hızı)."""
    u0, uH, uT = (uc_deger(x, maske, i, np) for i in (i0, iH, iT))
    if None in (u0, uH, uT):
        return None
    t2, t3 = (iT - iH) / 365.25, (iH - i0) / 365.25
    return dict(dv=(uT - uH) / t2 - (uH - u0) / t3, v5=(uT - u0) / (t2 + t3))


def beklenti(yazdir=True):
    """README tablosundaki istasyon gürültü parametreleriyle (güç yasası indisi n, genlik A) uç noktası
    ölçüsünün N0 altında |Δv| dağılımı. Bandpass bileşeni ve beyaz gürültü dahil değil (bkz. belge §4)."""
    np = _np()
    # README "Noise model for Creepmeters" (2004 öncesi kestirim; hakemli değil): kod, n, A, seküler hız
    TAB = [("XSC1", 2.27, 1.44, 21.4), ("XMM1", 2.00, 2.64, 20.0), ("XMD1", 2.57, 6.47, 11.6),
           ("XVA1", 2.00, 2.85, 7.9), ("XPK1", 2.00, 2.92, 9.5), ("XTA1", 2.71, 2.19, 6.9),
           ("WKR1", 2.36, 2.96, 9.8), ("CRR1", 2.00, 2.20, 2.8), ("XGH1", 2.23, 1.49, 4.2),
           ("X461", 2.74, 4.33, -1.1), ("XRSW", 2.39, 1.23, -0.1), ("XHSW", 2.12, 2.04, -0.8),
           ("XSH1", 2.53, 8.94, 6.9), ("XSJ2", 2.45, 3.47, 7.6), ("XHR2", 2.32, 3.80, 13.5),
           ("CWN1", 2.45, 2.18, 12.4), ("CWC3", 2.00, 3.92, 11.7), ("XMR1", 2.00, 4.57, 17.0)]
    P, n, i0, iH, iT = gunler(2003)
    maske = np.ones(n, bool)
    rng = np.random.default_rng(20261112)
    M = 2000
    sat, havuz, havuz_r = [], [], []
    for kod, ust, A, v in TAB:
        d = []
        for _ in range(M):
            x = pl_seri(n, ust, A, rng, np)
            d.append(dv_uc(x, maske, i0, iH, iT, np)["dv"])
        d = np.abs(np.array(d))
        sat.append((kod, ust, A, v, float(np.quantile(d, 0.5)), float(np.quantile(d, 0.95))))
        havuz.append(d)
        if v >= 2.0:
            havuz_r.append(d / v)
    havuz = np.concatenate(havuz); havuz_r = np.concatenate(havuz_r)
    # saf rastgele yürüyüş birim genlik (A = 1 mm/yıl^0,5): analitik sd = sqrt(1/2 + 1/3) = 0,913
    rw = []
    for _ in range(4000):
        x = pl_seri(n, 2.0, 1.0, rng, np)
        rw.append(dv_uc(x, maske, i0, iH, iT, np)["dv"])
    rw = np.array(rw)
    out = dict(tablo=sat, havuz_q50=float(np.quantile(havuz, .5)), havuz_q90=float(np.quantile(havuz, .9)),
               havuz_q95=float(np.quantile(havuz, .95)),
               havuz_r_q50=float(np.quantile(havuz_r, .5)), havuz_r_q95=float(np.quantile(havuz_r, .95)),
               rw1_sd=float(rw.std()), rw1_q95_abs=float(np.quantile(np.abs(rw), .95)))
    if yazdir:
        print("kod n A v_seküler | N0 medyan|Δv| q95|Δv| (mm/yıl)")
        for r in sat:
            print("%s %.2f %.2f %5.1f | %.2f %.2f" % r)
        print(json.dumps({k: v for k, v in out.items() if k != "tablo"}, indent=1))
    return out


def denetim_on(N_sw, tekrar=300):
    """Kod denetimi eşiklerinin yapay veriyle önceden doğrulanması (gerçek veri yok).
    (a) gürültüsüz doğrusal + menteşe + yıllık/altı aylık + pencere içi basamak, tam ve boşluklu maske:
        Δv hatası;
    (b) N_sw istasyon-pencerelik yapay N0 (rastgele yürüyüş b = 3 mm/yıl^0,5) kümesinde q95|Δv| / q95_N0 oranının
        dağılımı (payda: ayrı, 200 000 çekilişlik MC);
    (c) pozitif kontrol: yapay seriye max(0, t-H) × 5 mm/yıl eklenince d = Δv_eklenen - Δv_özgün dağılımı."""
    np = _np()
    rng = np.random.default_rng(20261113)
    P, n, i0, iH, iT = gunler(2003)
    t = np.arange(n) / 365.25

    def maske_uret():
        m = np.ones(n, bool)
        k = 0
        while k < n:   # ortalama %10 eksik, 1-20 günlük delikler, en uzun 20 gün
            if rng.random() < 0.01:
                L = rng.integers(1, 21); m[k:k + L] = False; k += L
            k += 1
        return m
    # (a)
    hata = []
    for _ in range(500):
        m = maske_uret()
        x = (3.0 + 7.0 * t + 4.0 * np.maximum(0, t - (iH / 365.25)) + 2.0 * np.sin(2 * np.pi * t + 1)
             + 0.7 * np.cos(4 * np.pi * t) + 3.0 * (np.arange(n) >= iH - 200))
        r = dv_uc(x, m, i0, iH, iT, np)
        if r:
            hata.append(r["dv"] - (4.0 + (-3.0 / ((iH - i0) / 365.25))))
    hata = np.abs(np.array(hata))
    m1 = np.ones(n, bool)
    x = (3.0 + 7.0 * t + 4.0 * np.maximum(0, t - (iH / 365.25)) + 2.0 * np.sin(2 * np.pi * t + 1)
         + 0.7 * np.cos(4 * np.pi * t) + 3.0 * (np.arange(n) >= iH - 200))
    hata_tam = abs(dv_uc(x, m1, i0, iH, iT, np)["dv"] - (4.0 + (-3.0 / ((iH - i0) / 365.25))))
    x = 3.0 + 7.0 * t + 4.0 * np.maximum(0, t - (iH / 365.25)) + 3.0 * (np.arange(n) >= iH - 200)
    hata_tam_mevsimsiz = abs(dv_uc(x, m1, i0, iH, iT, np)["dv"] - (4.0 + (-3.0 / ((iH - i0) / 365.25))))
    # (b)
    b = 3.0
    ref = []
    for _ in range(20000):
        x = pl_seri(n, 2.0, b, rng, np) + 0.1 * rng.standard_normal(n)
        ref.append(abs(dv_uc(x, np.ones(n, bool), i0, iH, iT, np)["dv"]))
    q95_N0 = float(np.quantile(ref, 0.95))
    oran = []
    for _ in range(tekrar):
        d = []
        while len(d) < N_sw:
            x = pl_seri(n, 2.0, b, rng, np) + 0.1 * rng.standard_normal(n)
            r = dv_uc(x, maske_uret(), i0, iH, iT, np)
            if r:
                d.append(abs(r["dv"]))
        oran.append(float(np.quantile(d, 0.95)) / q95_N0)
    oran = np.array(oran)
    # (c)
    dd = []
    for _ in range(2000):
        m = maske_uret()
        x = pl_seri(n, 2.0, b, rng, np) + 0.1 * rng.standard_normal(n)
        r0 = dv_uc(x, m, i0, iH, iT, np)
        r1 = dv_uc(x + 5.0 * np.maximum(0, t - iH / 365.25), m, i0, iH, iT, np)
        if r0 and r1:
            dd.append(r1["dv"] - r0["dv"])
    dd = np.array(dd)
    out = {"a_gurultusuz_max_hata_mm_yil": float(hata.max()), "a_N": int(len(hata)),
           "a_q99_hata": float(np.quantile(hata, .99)), "a_tam_maske_hata": float(hata_tam),
           "a_tam_maske_mevsimsiz_hata": float(hata_tam_mevsimsiz), "N_sw": N_sw, "tekrar": tekrar,
           "b_q95_N0": q95_N0, "b_oran_ortalama": float(oran.mean()), "b_oran_sd": float(oran.std()),
           "b_oran_q0.1_q99.9": [float(np.quantile(oran, .001)), float(np.quantile(oran, .999))],
           "b_oran_min_max": [float(oran.min()), float(oran.max())],
           "c_medyan_d": float(np.median(dd)), "c_q0.5_q99.5_d": [float(np.quantile(dd, .005)),
                                                                   float(np.quantile(dd, .995))],
           "c_max_sapma": float(np.abs(dd - 5).max())}
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    if sys.argv[1] == "say":
        say(sys.argv[2], sys.argv[3], sys.argv[4])
    elif sys.argv[1] == "beklenti":
        beklenti()
    elif sys.argv[1] == "denetim_on":
        denetim_on(int(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 300)
