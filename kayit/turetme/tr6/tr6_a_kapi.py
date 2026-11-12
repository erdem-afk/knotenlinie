"""TR-6 (a) ayağı güç kapısı, ikinci sayım: Aσ literatürden sabitlenir, gölge lobu öncül sismisitesi en iyi açık
katalogla yeniden sayılır. Hüküm satırı (olay sonrası oran, ters çözüm) YOKTUR; hiçbir olay sonrası sorgu yapılmaz.

1) Aσ tablosu: yayımlanmış hız-durum (Dieterich 1994) kestirimleri; doğrulama durumu satırda. Ön kayıt değeri:
   doğal kosismik tektonik dizilerin doğrulanmış değerlerinin medyanı (çalışma başına bir değer, yazarın tercih ettiği
   satır, üst sınır kendi değerinde). Duyarlılık: aynı kümenin çeyrekleri.
2) Katalog: tr6_a_sayim.json'daki 155 olayın (ComCat finite-fault, 1990-2025, M>=6, derinlik<=30 km) her biri için
   alıcı halka [L/2+10 km, 2L] içinde, olaydan önceki [t-1826 g, t-30 g] penceresinde, her erişilebilir açık katalogda:
   - 3 örnek pencere (45 g; t-4,5 y, t-2,5 y, t-0,5 y merkezli): Mc = MAXC+0,2 (>=50 olaylı pencerelerin en büyüğü;
     yoksa birleşik örnek), n_tahmin = örnekteki Mc üstü sayı x (pencere süresi / örnek süresi);
   - n_tahmin eşiklere yakınsa (0,33..3 kat) tam sayım (yıllık parçalar; ComCat'te count servisi).
   Derinlik: ana satır <= 40 km (alıcılar 7,5 km; dalan levha içi derin olaylar sayılmaz); bilgi satırı tüm derinlik.
   Duyarlılık: aynı satırlar Mc + 0,5 ile (halka geneli MAXC açık deniz lobları için iyimser olabilir).
   Gölge lobu yıllık arka plan: N0 = 0,25 x n / T (lob payı 0,5 x arka plan payı 0,5; tr6_a_sayim.py ile aynı beyan).
3) Kapı: N0 >= gereken (Δτ = -10 kPa, 1 yıl, %80 güç, tek yanlı α 0,05); bağımsız küme (300 km / 5 yıl);
   gereken K tam binom hesabıyla (p0 0,5, p1 0,75).

KÖR KURAL: her sorgunun bitişi olaydan 30 gün önce (en geç 2025-12-01); 2026 verisi istenmez. Olay sonrası veri yok.
Kullanım: python3 -I -B tr6_a_kapi.py <cikti.json> <onbellek_dizini> [olay_kimliği ...]  (kimlik: deneme alt kümesi)
Ham yanıtlar onbellek_dizini'ne URL özetiyle yazılır (depo dışı); yeniden koşu ağa gitmez.
"""
import datetime as dt, hashlib, json, math, os, re, subprocess, sys, threading, time, urllib.error, urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
import numpy as np

UA = "Mozilla/5.0 (compatible; research-client)"
KOR = dt.datetime(2026, 1, 1)
ZA, ZB = 1.6448536, 0.8416212
PENCERE_G, DISLA_G = 1826, 30
ORNEK_G, ORNEK_MERKEZ_Y = 45, (4.5, 2.5, 0.5)
DERIN_KM = 40.0
LOB_PAYI = 0.25
MC_EK = 0.5            # duyarlılık: halka geneli MAXC, gölge lobu (çoğu açık deniz) için iyimser olabilir
BURAYA = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------------ 1. Aσ literatür tablosu
# durum: "ozet" = OpenAlex özetinde sayı var; "tam" = açık tam metinde okundu; "ikincil" = başka bir açık tam metnin
# aktarımı (kendi metni kapalı ya da sayıyı özette vermiyor); "dogrulanamadi"; "cevrilemez" (Aσ değil, A ya da nitel).
# sinif: "K" = doğal kosismik tektonik dizi (ön kayıt medyanı yalnız bunlardan); "V" volkanik/sürü; "Y" yavaş kayma;
# "I" indüklenmiş; "-" kestirim değil.
LIT = [
    dict(bolge="Landers 1992, G. Kaliforniya", ortam="doğrultu atımlı, kıta içi", kpa=17, aralik="≈17",
         yontem="erken artçılarla en çok olabilirlik, gerilme belirsizliği (CV 0,95) dahil",
         kaynak="Hainzl vd. 2009, 10.1029/2008jb006011", durum="ozet", sinif="K"),
    dict(bolge="Landers 1992 ve G. Kaliforniya 1986-2003", ortam="doğrultu atımlı, kıta içi", kpa=40, aralik="40",
         yontem="ileri CRS modeli; Cocco 2010 kullandığı 0,04 MPa'yı 'Toda 2005 ile tutarlı' diye aktarıyor",
         kaynak="Toda vd. 2005, 10.1029/2004jb003415", durum="ikincil", sinif="K",
         not_="sayı Cocco vd. 2010 açık tam metninden (GFZ deposu); Toda 2005 özeti sayı vermiyor, Wiley 403"),
    dict(bolge="Kobe 1995, Japonya", ortam="doğrultu atımlı, kıta içi", kpa=35, aralik="35 ± 15",
         yontem="artçı oranı - ΔCFF ilişkisi, hız-durum", kaynak="Toda vd. 1998, 10.1029/98jb00765",
         durum="ikincil", sinif="K", not_="Hainzl-Steacy-Marsan 2010 (CORSSA), Hainzl vd. 2010 ve 2024 tam metinleri"),
    dict(bolge="Kagoshima 1997 çifti, Japonya", ortam="doğrultu atımlı, kıta içi", kpa=40, aralik="40",
         yontem="hız-durum ileri model (aç-kapa)", kaynak="Toda & Stein 2003, 10.1029/2003jb002527",
         durum="ikincil", sinif="K", not_="Cocco vd. 2010 tam metni: 'As = 0.04 MPa [Toda and Stein, 2003]'"),
    dict(bolge="Umbria-Marche 1997, Orta İtalya", ortam="normal, Apenin", kpa=40, aralik="40",
         yontem="en çok olabilirlik ayarı", kaynak="Catalli vd. 2008, 10.1029/2007jb005356",
         durum="ozet", sinif="K"),
    dict(bolge="Japonya 1970-2003 bölgesel sismisite", ortam="karışık (dalma-batma + kabuk)", kpa=12, aralik="12",
         yontem="fiziksel-istatistiksel kümelenme modeli", kaynak="Console vd. 2006 (BSSA; DOI okunmadı)",
         durum="ikincil", sinif="K", not_="CORSSA 2010 ve Hainzl vd. 2024 tam metinleri"),
    dict(bolge="Tohoku 2011, Japonya", ortam="dalma-batma megathrust", kpa=18, aralik="18 (belirsizliksiz model 100)",
         yontem="CRS, Monte Carlo gerilme belirsizliği; Tablo 2", kaynak="Cattania vd. 2014, 10.1002/2014jb011183",
         durum="tam", sinif="K", not_="GFZ deposu tam metni, Tablo 2"),
    dict(bolge="Parkfield 2004, Kaliforniya", ortam="doğrultu atımlı, levha sınırı", kpa=4,
         aralik="4 (belirsizliksiz model 8)", yontem="CRS, Monte Carlo; Tablo 2",
         kaynak="Cattania vd. 2014, 10.1002/2014jb011183", durum="tam", sinif="K"),
    dict(bolge="Orta İtalya 2016-2017 (Amatrice-Norcia)", ortam="normal, Apenin", kpa=20, aralik="≈20",
         yontem="CRS parametre eniyileme", kaynak="Mancini vd. 2019, 10.1029/2019jb017874", durum="ikincil",
         sinif="K", not_="Hainzl vd. 2024 tam metni; kendi açık kopyası Cloudflare sınaması verdi, atlatılmadı"),
    dict(bolge="G. Kaliforniya, 6 büyük ana şok", ortam="doğrultu atımlı ağırlıklı", kpa=10,
         aralik="< 10 (küçük bölmelerde ≈ 5); üst sınır", yontem="a-pozitif yeniden kurulmuş erken artçı oranı, c-değeri",
         kaynak="Hainzl, Page & van der Elst 2024, 10.1785/0220240176", durum="ozet", sinif="K",
         not_="üst sınır; medyana 10 olarak girer (tutucu: Aσ'yı büyütür)"),
    dict(bolge="Izu adaları 2000 sürüsü", ortam="volkanik dayk sürüsü", kpa=10, aralik="10",
         yontem="gerilme hızı - sismisite oranı", kaynak="Toda vd. 2002, 10.1038/nature00997", durum="ikincil",
         sinif="V", not_="CORSSA 2010, Hainzl vd. 2024; Nature özeti OpenAlex'te yok"),
    dict(bolge="Westmorland 2020 sürüsü, Salton", ortam="sığ yavaş kayma + akışkan", kpa=0.8, aralik="0,4-1,2",
         yontem="yavaş kaymayla sürülen hız-durum", kaynak="Sirorattanakul vd. 2022, 10.1029/2022jb024693",
         durum="ikincil", sinif="Y", not_="Hainzl vd. 2024 tam metni; özet sayı vermiyor"),
    dict(bolge="Val d'Agri (Pertusillo barajı)", ortam="baraj kaynaklı", kpa=0.8, aralik="0,8",
         yontem="poroelastik + hız-durum", kaynak="Rinaldi vd. 2020, 10.1016/j.jrmge.2020.04.003",
         durum="ikincil", sinif="I", not_="Hainzl vd. 2024 tam metni"),
    dict(bolge="Bárðarbunga 2014 dayk", ortam="volkanik dayk", kpa=None, aralik="A 1e-5..0,01 (boyutsuz)",
         yontem="Bayesçi, voksel başına", kaynak="Heimisson & Segall 2020, 10.1029/2019jb018141",
         durum="cevrilemez", sinif="-", not_="EarthArXiv tam metni; σ0 ayrı parametre, Aσ'ya çevrilmedi"),
    dict(bolge="Landers sentetik (çoklu alıcı)", ortam="doğrultu atımlı", kpa=None, aralik="10/50/100 taranmış",
         yontem="benzetim; 17 kPa'nın 'etkin uydurma parametresi' olduğu yorumu",
         kaynak="Hainzl, Zöller & Wang 2010, 10.1029/2008jb006224", durum="cevrilemez", sinif="-"),
    dict(bolge="Kilauea güney yamacı", ortam="volkan yamacı ayrılma yüzeyi", kpa=None, aralik="-",
         yontem="sismisite oranı gerilme ölçer", kaynak="Dieterich, Cayol & Okubo 2000, 10.1038/35044054",
         durum="dogrulanamadi", sinif="V", not_="özet yok, açık tam metin yok"),
    dict(bolge="Kilauea yavaş kaymaları", ortam="ayrılma yüzeyi yavaş kayma", kpa=None, aralik="-",
         yontem="yavaş kayma - sürü", kaynak="Segall vd. 2006, 10.1038/nature04938", durum="dogrulanamadi", sinif="Y"),
    dict(bolge="Salton Trough 1990-2009", ortam="yavaş kayma / sürü", kpa=None, aralik="-",
         yontem="ETAS + hız-durum veri özümleme", kaynak="Llenos & McGuire 2011, 10.1029/2010jb007537; "
         "Llenos vd. 2009, 10.1016/j.epsl.2009.02.011", durum="dogrulanamadi", sinif="Y",
         not_="özette sayı yok; Wiley 403 / Elsevier özet yok"),
    dict(bolge="Japonya CSEP", ortam="karışık", kpa=None, aralik="-", yontem="CRS ileri tahmin",
         kaynak="Toda & Enescu 2011, 10.5047/eps.2011.01.004", durum="dogrulanamadi", sinif="K",
         not_="Springer istemci sınaması; özet sayı vermiyor"),
    dict(bolge="Canterbury 2010-2012", ortam="doğrultu atımlı, kıta içi", kpa=None, aralik="-",
         yontem="CRS ileri tahmin", kaynak="Cattania vd. 2018, 10.1785/0220180033", durum="dogrulanamadi",
         sinif="K", not_="GFZ tam metni indirildi; Aσ sayısı metin çıkarımında okunamadı"),
    dict(bolge="Reno-Mogul 2008 sürüsü", ortam="sürü", kpa=None, aralik="-", yontem="Bayesçi T-rate",
         kaynak="Jiang, Trugman & González 2026, 10.1029/2026jb033922", durum="dogrulanamadi", sinif="V"),
    dict(bolge="Nepal mevsimsel", ortam="Himalaya bindirmesi", kpa=None, aralik="nitel",
         yontem="sonlu fay benzetimi: tek kayma bloğu modeli aσ'yı ciddi düşük kestirebilir",
         kaynak="Ader vd. 2014, 10.1093/gji/ggu144", durum="cevrilemez", sinif="-"),
]


def lit_ozet():
    dog = [r for r in LIT if r["kpa"] is not None and r["durum"] in ("ozet", "tam", "ikincil")]
    k = np.array([r["kpa"] for r in dog if r["sinif"] == "K"], float)
    hepsi = np.array([r["kpa"] for r in dog], float)
    q1, med, q3 = np.percentile(k, [25, 50, 75])
    return dict(
        K_degerler_kPa=sorted(k.tolist()), K_n=int(len(k)), K_medyan=float(med), K_q1=float(q1), K_q3=float(q3),
        K_min=float(k.min()), K_max=float(k.max()),
        hepsi_n=int(len(hepsi)), hepsi_medyan=float(np.median(hepsi)), hepsi_min=float(hepsi.min()),
        hepsi_max=float(hepsi.max()),
        sabit_kPa=float(round(med)), duyarlilik_kPa=[float(round(q1)), float(round(q3))],
        dogrulanamadi=[r["kaynak"] for r in LIT if r["durum"] == "dogrulanamadi"])


def gereken_n0(oran):
    k = (ZA + ZB * math.sqrt(oran)) / (1 - oran)
    return k * k


# ------------------------------------------------------------------ ağ ve önbellek
_kilit = threading.Lock()


def getir(url, onb, zaman_asimi=600, deneme=6):
    # TR-6a ön kaydı sürüm 3 (§9 adım 3, İNCELEME-2 K8): TR-6a önbelleği (tr6a_onbellek_kor.arsivden_ac ile açılmış,
    # ".tr6a_kor" işaretli dizin) bu işlevle maskesiz açılamaz; tek okuma yolu tr6a_onbellek_kor.oku_sorgu'dur.
    if os.path.exists(os.path.join(onb, ".tr6a_kor")):
        raise PermissionError("TR-6a önbelleği maskesiz açılamaz: tr6a_onbellek_kor.oku_sorgu kullanılır")
    h = hashlib.sha256(url.encode()).hexdigest()[:24]
    yol = os.path.join(onb, h + ".txt")
    if os.path.exists(yol):
        return open(yol, encoding="utf-8", errors="replace").read()
    son = None
    for i in range(deneme):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=zaman_asimi) as r:
                kod = r.status
                b = r.read()
            metin = "" if kod == 204 else b.decode("utf-8", errors="replace")
            break
        except urllib.error.HTTPError as e:
            if e.code in (204, 404) and "fdsnws" in url:
                metin = ""
                break
            son = f"HTTP {e.code}"
            if e.code in (400, 401, 403):
                raise RuntimeError(son)
        except Exception as e:
            son = type(e).__name__
        time.sleep(min(120, 5 * 2 ** i))
    else:
        raise RuntimeError(f"erişilemedi ({son})")
    with _kilit:
        with open(yol, "w", encoding="utf-8") as f:
            f.write(metin)
        with open(os.path.join(onb, "URL_LISTESI.tsv"), "a", encoding="utf-8") as f:
            f.write(f"{h}\t{hashlib.sha256(metin.encode()).hexdigest()}\t{url}\n")
    return metin


def fdsn_ayristir(metin):
    """FDSN text: zaman, enlem, boylam, derinlik, büyüklük. Deprem olmayan tür (patlama, ocak) atılır."""
    t, la, lo, de, m = [], [], [], [], []
    for s in metin.splitlines():
        if not s or s.startswith("#"):
            continue
        a = [x.strip() for x in s.split("|")]
        if len(a) < 11 or not a[10]:
            continue
        tur = a[13].lower() if len(a) > 13 else ""
        if tur and "earthquake" not in tur and tur not in ("ke", "se"):
            continue
        try:
            z = dt.datetime.fromisoformat(a[1].replace("Z", "")[:19])
            if z >= KOR:
                continue
            t.append(z); la.append(float(a[2])); lo.append(float(a[3]))
            de.append(float(a[4]) if a[4] else 10.0); m.append(float(a[10]))
        except ValueError:
            continue
    return dict(t=t, la=np.array(la), lo=np.array(lo), de=np.array(de), m=np.array(m))


SATIR_KOERI = re.compile(r"^\s*\d{6}\t\d{14}\t\d{4}\.\d\d\.\d\d\t")


def koeri_ayristir(metin):
    duz = re.sub(r"<[^>]+>", "\n", metin)
    t, la, lo, de, m = [], [], [], [], []
    for s in duz.splitlines():
        if not SATIR_KOERI.match(s):
            continue
        a = s.strip("\r\n ").split("\t")
        try:
            z = dt.datetime.fromisoformat(a[2].replace(".", "-") + "T" + a[3][:8])
            if z >= KOR:
                continue
            t.append(z); la.append(float(a[4])); lo.append(float(a[5])); de.append(float(a[6])); m.append(float(a[7]))
        except (ValueError, IndexError):
            continue
    return dict(t=t, la=np.array(la), lo=np.array(lo), de=np.array(de), m=np.array(m)), ("Liste sonu" in duz)


# ------------------------------------------------------------------ servisler
def iso(z):
    return z.strftime("%Y-%m-%dT%H:%M:%S")


class Servis:
    ad = ""
    latlon = ("latitude", "longitude")
    taban = ""
    ekstra = {}
    limit_var = True

    def uygun(self, o):
        return True

    def sorgu(self, o, t0, t1, mmin=None, limit=20000):
        r1, r2 = o["halka_km"]
        q = {self.latlon[0]: f"{o['enlem']:.4f}", self.latlon[1]: f"{o['boylam']:.4f}",
             "minradius": f"{r1 / 111.195:.4f}", "maxradius": f"{r2 / 111.195:.4f}",
             "starttime": iso(t0), "endtime": iso(t1), "format": "text"}
        if limit and self.limit_var:
            q["limit"] = limit
        if mmin is not None:
            q["minmagnitude"] = f"{mmin:.2f}"
        q.update(self.ekstra)
        return self.taban + "query?" + urllib.parse.urlencode(q)

    def oku(self, o, t0, t1, onb, mmin=None, limit=20000):
        d = fdsn_ayristir(getir(self.sorgu(o, t0, t1, mmin, limit), onb))
        return d, bool(self.limit_var and limit and len(d["m"]) >= limit)


class ComCat(Servis):
    ad = "ComCat"
    taban = "https://earthquake.usgs.gov/fdsnws/event/1/"
    ekstra = {"eventtype": "earthquake"}

    def sayim(self, o, t0, t1, mc, onb, maxdepth=None):
        r1, r2 = o["halka_km"]
        q = dict(latitude=o["enlem"], longitude=o["boylam"], minradiuskm=r1, maxradiuskm=r2, starttime=iso(t0),
                 endtime=iso(t1), minmagnitude=f"{mc - 0.05:.2f}", eventtype="earthquake")
        if maxdepth:
            q["maxdepth"] = maxdepth
        return int(getir(self.taban + "count?" + urllib.parse.urlencode(q), onb).strip())


class ISC(Servis):
    ad = "ISC"
    taban = "https://www.isc.ac.uk/fdsnws/event/1/"


class EMSC(Servis):
    ad = "EMSC"
    taban = "https://www.seismicportal.eu/fdsnws/event/1/"
    latlon = ("lat", "lon")

    def uygun(self, o):
        return 28 <= o["enlem"] <= 50 and -15 <= o["boylam"] <= 50


class GeoNet(Servis):
    ad = "GeoNet"
    taban = "https://service.geonet.org.nz/fdsnws/event/1/"
    limit_var = False          # servis 'limit' parametresini reddediyor (400)

    def uygun(self, o):
        return -52 <= o["enlem"] <= -25 and (o["boylam"] >= 160 or o["boylam"] <= -172)


class INGV(Servis):
    ad = "INGV"
    taban = "https://webservices.ingv.it/fdsnws/event/1/"

    def uygun(self, o):
        return 35 <= o["enlem"] <= 48 and 5 <= o["boylam"] <= 20


class KOERI(Servis):
    """Kandilli zeqdb: yalnız kutu sorgusu, yavaş; halka süzgeci yerelde. Türkiye ve yakını."""
    ad = "KOERI"
    URL = "http://www.koeri.boun.edu.tr/sismo/zeqdb/submitRecSearchT.asp"

    def uygun(self, o):
        return 35 <= o["enlem"] <= 43 and 25 <= o["boylam"] <= 45

    def oku(self, o, t0, t1, onb, mmin=None, limit=None):
        r2 = o["halka_km"][1]
        dla = r2 / 111.195
        dlo = dla / max(0.2, math.cos(math.radians(o["enlem"])))
        q = dict(bYear=t0.year, bMont=f"{t0.month:02d}", bDay=f"{t0.day:02d}", eYear=t1.year, eMont=f"{t1.month:02d}",
                 eDay=f"{t1.day:02d}", EnMin=f"{o['enlem'] - dla:.2f}", EnMax=f"{o['enlem'] + dla:.2f}",
                 BoyMin=f"{o['boylam'] - dlo:.2f}", BoyMax=f"{o['boylam'] + dlo:.2f}",
                 MAGMin=f"{(mmin or 0.0):.1f}", MAGMax="9.0", DerMin="0", DerMax="500", Tip="Deprem",
                 ofName="tr6.txt")
        url = self.URL + "?" + urllib.parse.urlencode(q)
        for i in range(4):
            metin = getir(url, onb, zaman_asimi=900)
            d, tam = koeri_ayristir(metin)
            if tam:
                return d, False
            # yarım sayfa: önbellekten sil, yeniden dene
            os.remove(os.path.join(onb, hashlib.sha256(url.encode()).hexdigest()[:24] + ".txt"))
            time.sleep(20 * (i + 1))
        raise RuntimeError("KOERI yarım sayfa")


SERVISLER = [ComCat(), ISC(), EMSC(), GeoNet(), INGV(), KOERI()]


# ------------------------------------------------------------------ Mc ve sayım
def uzaklik_km(la0, lo0, la, lo):
    p1, p2 = math.radians(la0), np.radians(la)
    dl = np.radians(lo - lo0)
    c = np.sin(p1) * np.sin(p2) + np.cos(p1) * np.cos(p2) * np.cos(dl)
    return 6371.0 * np.arccos(np.clip(c, -1, 1))


def halka_maske(o, d, derin):
    if len(d["m"]) == 0:
        return np.zeros(0, bool)
    r = uzaklik_km(o["enlem"], o["boylam"], d["la"], d["lo"])
    mk = (r >= o["halka_km"][0]) & (r <= o["halka_km"][1])
    if derin:
        mk &= d["de"] <= DERIN_KM
    return mk


def maxc(m):
    b = np.round(m, 1)
    v, c = np.unique(b, return_counts=True)
    return float(v[np.argmax(c)])


def katalog_olc(srv, o, onb, n_alt, n_ust):
    t = dt.datetime.fromisoformat(o["zaman"])
    p0, p1 = t - dt.timedelta(days=PENCERE_G), t - dt.timedelta(days=DISLA_G)
    assert p1 < KOR
    T = (p1 - p0).days / 365.25
    ornek, kesik = [], False
    for y in ORNEK_MERKEZ_Y:
        a = t - dt.timedelta(days=y * 365.25 + ORNEK_G / 2)
        b = a + dt.timedelta(days=ORNEK_G)
        a, b = max(a, p0), min(b, p1)
        d, k = srv.oku(o, a, b, onb)
        kesik |= k
        ornek.append(d)
    mcs = []
    for d in ornek:
        mk = halka_maske(o, d, True)
        if mk.sum() >= 50:
            mcs.append(maxc(d["m"][mk]) + 0.2)
    birlesik = np.concatenate([d["m"][halka_maske(o, d, True)] for d in ornek])
    if mcs:
        mc, mc_kural = max(mcs), "max(pencere MAXC+0,2)"
    elif len(birlesik) >= 50:
        mc, mc_kural = maxc(birlesik) + 0.2, "birleşik MAXC+0,2"
    elif len(birlesik) >= 20:
        mc, mc_kural = maxc(birlesik) + 0.3, "birleşik (<50) MAXC+0,3"
    else:
        return dict(katalog=srv.ad, mc=None, mc_kural=f"yetersiz örnek ({len(birlesik)})", n=0, n_tum=0,
                    tur="yetersiz", T_yil=T, N0=0.0)
    ornek_g = sum(ORNEK_G for _ in ORNEK_MERKEZ_Y)
    n_or = sum(int(((d["m"] >= mc - 1e-6) & halka_maske(o, d, True)).sum()) for d in ornek)
    n_or_tum = sum(int(((d["m"] >= mc - 1e-6) & halka_maske(o, d, False)).sum()) for d in ornek)
    olcek = (p1 - p0).days / ornek_g
    n_t, n_t_tum = n_or * olcek, n_or_tum * olcek
    n_t05 = sum(int(((d["m"] >= mc + MC_EK - 1e-6) & halka_maske(o, d, True)).sum()) for d in ornek) * olcek
    sonuc = dict(katalog=srv.ad, mc=round(mc, 2), mc_kural=mc_kural, ornek_kesik=kesik, n_ornek=n_or,
                 n_tahmin=round(n_t, 1), T_yil=round(T, 3))
    if n_alt <= n_t <= n_ust or kesik:
        if isinstance(srv, ComCat):
            n = srv.sayim(o, p0, p1, mc, onb, DERIN_KM)
            n_tum = srv.sayim(o, p0, p1, mc, onb)
            n05 = srv.sayim(o, p0, p1, mc + MC_EK, onb, DERIN_KM)
            alt_sinir = False
        else:
            n, n_tum, n05, alt_sinir = 0, 0, 0, False
            a = p0
            while a < p1:
                b = min(p1, a + dt.timedelta(days=366))
                d, k = srv.oku(o, a, b, onb, mmin=mc - 0.05)
                ok = d["m"] >= mc - 1e-6
                n += int((ok & halka_maske(o, d, True)).sum())
                n_tum += int((ok & halka_maske(o, d, False)).sum())
                n05 += int(((d["m"] >= mc + MC_EK - 1e-6) & halka_maske(o, d, True)).sum())
                alt_sinir |= k
                a = b
                if n >= 3 * n_ust:
                    alt_sinir = True
                    break
        sonuc.update(n=n, n_tum=n_tum, n_mc05=n05, tur="tam sayım" + (" (alt sınır)" if alt_sinir else ""))
    else:
        sonuc.update(n=round(n_t, 1), n_tum=round(n_t_tum, 1), n_mc05=round(n_t05, 1), tur="örnekten tahmin")
    sonuc["N0"] = round(LOB_PAYI * sonuc["n"] / T, 2)
    sonuc["N0_tum_derinlik"] = round(LOB_PAYI * sonuc["n_tum"] / T, 2)
    sonuc["N0_mc05"] = round(LOB_PAYI * sonuc["n_mc05"] / T, 2)
    return sonuc


def mekanizma(o, onb):
    u = "https://earthquake.usgs.gov/fdsnws/event/1/query?" + urllib.parse.urlencode(
        dict(eventid=o["id"], format="geojson"))
    try:
        p = json.loads(getir(u, onb))["properties"]["products"]
    except Exception as e:
        return dict(sinif="bilinmiyor", neden=type(e).__name__)
    for anah in ("moment-tensor", "focal-mechanism"):
        for pr in p.get(anah, []):
            q = pr.get("properties", {})
            try:
                r1, d1 = float(q["nodal-plane-1-rake"]), float(q["nodal-plane-1-dip"])
                d2 = float(q.get("nodal-plane-2-dip", d1))
            except (KeyError, ValueError):
                continue
            r = (r1 + 180) % 360 - 180
            if abs(r) <= 30 or abs(r) >= 150:
                s = "doğrultu atımlı"
            elif r > 0:
                s = "ters, düşük eğimli (megathrust dahil)" if min(d1, d2) <= 30 else "ters (diğer)"
            else:
                s = "normal"
            return dict(sinif=s, rake=r1, dip=[d1, d2], kaynak=anah)
    return dict(sinif="bilinmiyor", neden="moment tensörü yok")


# ------------------------------------------------------------------ kümeleme ve güç
def kumele(olaylar, km=300.0, gun=1826):
    kl = []
    for e in sorted(olaylar, key=lambda x: x["zaman"]):
        t = dt.datetime.fromisoformat(e["zaman"])
        for c in kl:
            if any(float(uzaklik_km(e["enlem"], e["boylam"], np.array([x["enlem"]]), np.array([x["boylam"]]))[0])
                   < km and abs((t - dt.datetime.fromisoformat(x["zaman"])).days) < gun for x in c):
                c.append(e)
                break
        else:
            kl.append([e])
    return kl


def binom_ust(k, n, p):
    return float(sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1)))


def gereken_K(p1=0.75, alfa=0.05, guc=0.8):
    tablo, ilk, kalici = [], None, None
    for K in range(5, 81):
        c = next(c for c in range(K + 2) if binom_ust(c, K, 0.5) <= alfa)
        g = binom_ust(c, K, p1)
        tablo.append(dict(K=K, kritik=c, alfa_gercek=round(binom_ust(c, K, 0.5), 4), guc=round(g, 4)))
        if g >= guc and ilk is None:
            ilk = K
    for i in range(len(tablo)):
        if all(r["guc"] >= guc for r in tablo[i:]):
            kalici = tablo[i]["K"]
            break
    normal = ((ZA * 0.5 + ZB * math.sqrt(p1 * (1 - p1))) / (p1 - 0.5)) ** 2
    return dict(ilk_K=ilk, kalici_K=kalici, normal_yaklasim=round(normal, 2),
                tablo=[r for r in tablo if 18 <= r["K"] <= 30])


# ------------------------------------------------------------------ ana
def main():
    cikti, onb = sys.argv[1], sys.argv[2]
    os.makedirs(onb, exist_ok=True)
    lit = lit_ozet()
    asig = sorted({lit["sabit_kPa"], *lit["duyarlilik_kPa"], 10.0, 20.0, 30.0, 50.0})
    esik = {a: gereken_n0(math.exp(-10.0 / a)) for a in asig}
    olaylar = json.load(open(os.path.join(BURAYA, "tr6_a_sayim.json")))["olaylar"]
    if sys.argv[3:]:
        olaylar = [o for o in olaylar if o["id"] in sys.argv[3:]]
    T = (PENCERE_G - DISLA_G) / 365.25
    n_alt = min(esik.values()) * T / LOB_PAYI / 3
    n_ust = max(esik.values()) * T / LOB_PAYI * 3
    sonuc = {o["id"]: dict(o, kataloglar={}, hatalar={}) for o in olaylar}

    def isle(srv, liste):
        for o in liste:
            if not srv.uygun(o):
                continue
            try:
                sonuc[o["id"]]["kataloglar"][srv.ad] = katalog_olc(srv, o, onb, n_alt, n_ust)
            except Exception as e:
                sonuc[o["id"]]["hatalar"][srv.ad] = str(e)[:120]
            print(srv.ad, o["id"], json.dumps(sonuc[o["id"]]["kataloglar"].get(srv.ad,
                  sonuc[o["id"]]["hatalar"].get(srv.ad)), ensure_ascii=False), flush=True)

    isler = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        for srv in SERVISLER:
            if isinstance(srv, ISC):          # ISC yavaş: üç akış
                isler += [ex.submit(isle, srv, olaylar[i::3]) for i in range(3)]
            else:
                isler.append(ex.submit(isle, srv, olaylar))
        isler.append(ex.submit(lambda: [sonuc[o["id"]].__setitem__("mekanizma", mekanizma(o, onb))
                                        for o in olaylar]))
        for f in isler:
            f.result()

    # en iyi katalog: Mc üstü (derinlik <= 40 km) sayısı en büyük olan; en düşük Mc ayrıca yazılır
    for s in sonuc.values():
        k = {a: v for a, v in s["kataloglar"].items() if v.get("mc") is not None}
        if not k:
            s["en_iyi"] = None
            continue
        en = max(k, key=lambda a: k[a]["N0"])
        s["en_iyi"] = dict(katalog=en, N0=k[en]["N0"], mc=k[en]["mc"], tur=k[en]["tur"],
                           en_dusuk_mc_katalog=min(k, key=lambda a: k[a]["mc"]))

    def kapi(secici):
        out = {}
        for a in asig:
            sec = [s for s in sonuc.values() if secici(s) >= esik[a]]
            kl = kumele(sec)
            dok = {}
            for c in kl:
                tem = max(c, key=lambda x: x["M"])
                m = tem.get("mekanizma", {}).get("sinif", "bilinmiyor")
                dok[m] = dok.get(m, 0) + 1
            out[f"{a:g}"] = dict(esik_N0=round(esik[a], 2), olay=len(sec), kume=len(kl), dokum=dok,
                                 kumeler=[[x["id"] for x in c] for c in kl])
        return out

    gk = gereken_K()
    kapilar = {
        "ComCat_eski (M>=2,5, tüm derinlik; tr6_a_sayim)": kapi(lambda s: s["golge_N0_yil"]),
        "ComCat_Mc (<=40 km)": kapi(lambda s: s["kataloglar"].get("ComCat", {}).get("N0", 0)),
        "ISC_Mc (<=40 km)": kapi(lambda s: s["kataloglar"].get("ISC", {}).get("N0", 0)),
        "en_iyi_acik (<=40 km)": kapi(lambda s: (s["en_iyi"] or {}).get("N0", 0)),
        "en_iyi_acik (<=40 km, Mc+0,5 duyarlılık)": kapi(
            lambda s: max([v.get("N0_mc05", 0) for v in s["kataloglar"].values()] or [0])),
        "en_iyi_acik (tüm derinlik, bilgi)": kapi(
            lambda s: max([v.get("N0_tum_derinlik", 0) for v in s["kataloglar"].values()] or [0])),
    }
    json.dump(dict(aciklama=__doc__, literatur=LIT, literatur_ozet=lit, asigma_kPa=asig,
                   esik_N0={f"{a:g}": esik[a] for a in asig}, gereken_K=gk, kapilar=kapilar,
                   olaylar=list(sonuc.values())), open(cikti, "w"), indent=1, ensure_ascii=False)
    print(json.dumps(dict(literatur_ozet=lit, gereken_K={k: v for k, v in gk.items() if k != "tablo"},
                          kapi={k: {a: (v[a]["kume"], v[a]["dokum"]) for a in v} for k, v in kapilar.items()}),
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
