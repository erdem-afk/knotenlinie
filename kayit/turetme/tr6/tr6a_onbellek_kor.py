"""TR-6a: Ek 1 ham önbelleğinin (ve manifest ön indirmelerinin) TEK okuma yolu, B3 körlük maskesiyle.

Ön kayıt sürüm 2 §9 adım 3 (B3 kuralı): bir adayın olay öncesi indirmesi başka bir havuz olayının (A) olay sonrası
penceresini kapsayabilir. Bu modül her satırı, döndürmeden ÖNCE, şu maskeden geçirir ve maskelenen satırlar için hiçbir
özet (sayı, histogram, harita) üretmez, döndürmez, yazmaz:

    satır atılır  <=>  bir havuz olayı A için  t_A <= t_satır < t_A + 365 g  ve  dış merkez uzaklığı <= 4 L_A

(A: tr6a_olay_listesi.json'daki 155 havuz olayının hepsi, koşu adayı olsun olmasın; 4 L_A, bölge yarıçapı 2 L_A ile
kırık izinin dış merkezden en uzak noktasının (≤ 2 L_A varsayımı) toplamının üst sınırıdır.) Sorgunun sahibi olan
olayın kendi penceresi zaten t_B − 30 g'de biter. Başka hiçbir kod önbellek dosyasını doğrudan açmamalıdır; ham dosyalar
insan gözüyle satır satır incelenmez.

Kullanım (kütüphane): oku_sorgu(hash) -> (sahip_id, katalog, satirlar);  satirlar: dict(t, la, lo, de, m, mtip)
Ağ erişimi yok. Yalnız numpy + standart kitaplık.
"""
import datetime as dt, json, math, os, re, urllib.parse
import numpy as np

BURAYA = os.path.dirname(os.path.abspath(__file__))
ONBELLEK = "/tmp/claude-0/-home-user/635decb6-3930-5a4d-9c31-b6f30d64fb94/scratchpad/tr6a/onbellek"
MASKE_GUN, MASKE_L = 365, 4.0
KOR = dt.datetime(2026, 1, 1)
_SATIR_KOERI = re.compile(r"^\s*\d{6}\t\d{14}\t\d{4}\.\d\d\.\d\d\t")


def _uzaklik(la0, lo0, la, lo):
    p1, p2 = math.radians(la0), np.radians(la)
    c = np.sin(p1) * np.sin(p2) + np.cos(p1) * np.cos(p2) * np.cos(np.radians(lo - lo0))
    return 6371.0 * np.arccos(np.clip(c, -1, 1))


def havuz():
    return json.load(open(os.path.join(BURAYA, "tr6a_olay_listesi.json"), encoding="utf-8"))["olaylar"]


def _maske(d, hav, sahip):
    """True = tutulur. Maskelenen satırlar hakkında hiçbir bilgi dışarı çıkmaz."""
    n = len(d["m"])
    tut = np.ones(n, bool)
    if n == 0:
        return tut
    ts = np.array([x.timestamp() for x in d["t"]])
    for a in hav:
        if a["id"] == sahip:
            continue
        ta = dt.datetime.fromisoformat(a["zaman"]).timestamp()
        zm = (ts >= ta) & (ts < ta + MASKE_GUN * 86400.0)
        if not zm.any():
            continue
        r = _uzaklik(a["enlem"], a["boylam"], d["la"][zm], d["lo"][zm])
        idx = np.nonzero(zm)[0][r <= MASKE_L * a["L_km"]]
        tut[idx] = False
    return tut


def _fdsn(metin):
    t, la, lo, de, m, mt = [], [], [], [], [], []
    for s in metin.splitlines():
        if not s or s.startswith("#"):
            continue
        a = [x.strip() for x in s.split("|")]
        if len(a) < 11:
            continue
        tur = a[13].lower() if len(a) > 13 else ""
        if tur and "earthquake" not in tur and tur not in ("ke", "se"):
            continue
        try:
            z = dt.datetime.fromisoformat(a[1].replace("Z", "")[:19])
            if z >= KOR:
                continue
            mm = float(a[10]) if a[10] else math.nan
            t.append(z); la.append(float(a[2])); lo.append(float(a[3]))
            de.append(float(a[4]) if a[4] else 10.0); m.append(mm); mt.append(a[9])
        except ValueError:
            continue
    return dict(t=t, la=np.array(la), lo=np.array(lo), de=np.array(de), m=np.array(m), mtip=mt)


def _koeri(metin):
    duz = re.sub(r"<[^>]+>", "\n", metin)
    t, la, lo, de, m, mt = [], [], [], [], [], []
    for s in duz.splitlines():
        if not _SATIR_KOERI.match(s):
            continue
        a = s.strip("\r\n ").split("\t")
        try:
            z = dt.datetime.fromisoformat(a[2].replace(".", "-") + "T" + a[3][:8])
            if z >= KOR:
                continue
            t.append(z); la.append(float(a[4])); lo.append(float(a[5])); de.append(float(a[6]))
            m.append(float(a[7])); mt.append("KOERI")
        except (ValueError, IndexError):
            continue
    return dict(t=t, la=np.array(la), lo=np.array(lo), de=np.array(de), m=np.array(m), mtip=mt)


def sorgu_listesi(onb=ONBELLEK):
    """URL_LISTESI.tsv'den olay satırı sorguları (count servisi ve geojson hariç) ve sahip olayları."""
    hav = havuz()
    konum = {(round(o["enlem"], 4), round(o["boylam"], 4)): o for o in hav}
    out = []
    for s in open(os.path.join(onb, "URL_LISTESI.tsv"), encoding="utf-8"):
        h, _, url = s.rstrip("\n").split("\t")
        u = urllib.parse.urlparse(url)
        q = dict(urllib.parse.parse_qsl(u.query))
        if "koeri" in u.netloc:
            kat = "KOERI"
            la = round((float(q["EnMin"]) + float(q["EnMax"])) / 2, 2)
            adaylar = [o for o in hav if abs(o["enlem"] - la) < 0.011 and
                       abs(o["boylam"] - (float(q["BoyMin"]) + float(q["BoyMax"])) / 2) < 0.011]
            bitis = dt.datetime(int(q["eYear"]), int(q["eMont"]), int(q["eDay"]))
        elif u.path.endswith("/query") and "eventid" not in q:
            kat = {"earthquake.usgs.gov": "ComCat", "www.isc.ac.uk": "ISC", "www.seismicportal.eu": "EMSC",
                   "service.geonet.org.nz": "GeoNet", "webservices.ingv.it": "INGV"}[u.netloc]
            la = float(q.get("latitude", q.get("lat"))); lo = float(q.get("longitude", q.get("lon")))
            o = konum.get((round(la, 4), round(lo, 4)))
            adaylar = [o] if o else []
            bitis = dt.datetime.fromisoformat(q["endtime"])
        else:
            continue
        # sahip: sorgu bitişi t_B − 30 g'yi aşmayan, konumu tutan olay (aynı konumda birden çok olay varsa en erken uyan)
        sahip = [o for o in adaylar if bitis <= dt.datetime.fromisoformat(o["zaman"]) - dt.timedelta(days=29)]
        out.append(dict(hash=h, katalog=kat, sahip=sahip[0]["id"] if sahip else None, url=url))
    return out


def oku_sorgu(kayit, onb=ONBELLEK, _hav=[]):
    """Tek okuma yolu: dosyayı ayrıştırır, B3 maskesini uygular, yalnız tutulan satırları döndürür."""
    if not _hav:
        _hav.extend(havuz())
    if kayit["sahip"] is None:
        raise ValueError("sahibi bulunamayan sorgu okunmaz (maske kurulamaz)")
    metin = open(os.path.join(onb, kayit["hash"] + ".txt"), encoding="utf-8", errors="replace").read()
    d = _koeri(metin) if kayit["katalog"] == "KOERI" else _fdsn(metin)
    tut = _maske(d, _hav, kayit["sahip"])
    return dict(t=[x for x, k in zip(d["t"], tut) if k], la=d["la"][tut], lo=d["lo"][tut], de=d["de"][tut],
                m=d["m"][tut], mtip=[x for x, k in zip(d["mtip"], tut) if k])
