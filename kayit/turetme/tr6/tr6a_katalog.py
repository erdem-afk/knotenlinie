"""TR-6a katalog katmanı: sorgu kurma (ISC, ComCat, EMSC, GeoNet, KOERI; ComCat moment tensörleri), tarih/körlük
denetimi, satır sınırında sorgu bölme, ayrıştırma, büyüklük kuralları ("0 büyüklük"), MAXC, Mc_lob, alt pencere
Mc_son, Gardner-Knopoff kümesizleştirme (lob içi, 730 g ön tampon), pencere sayıları ve koşullu binom oyu.
Ön kayıt sürüm 3 §3.5, §3.6, §4.1, §4.3, §5 madde 1, §9 adım 3.

Körlük (kesin):
- Hiçbir istek bitişi 2025-12-31T23:59:59'u aşamaz; aşan istek KorIhlal ile reddedilir (ağa gitmeden).
- Aşama sınırı: manifest aşamasında katalog istekleri birimin t0 − 30 g sınırını aşamaz (`sinir=`); olay sonrası
  istekler yalnız `tr6a_kosu.py son-indir` aşamasında ve son pencere sonuna dek yapılır.
- Ayrıştırmada 2026-01-01 ve sonrası satırlar sayılmadan atılır.
- Ad hoc (tanı, denetim) okumalar yalnız `maskeli_oku` ile, tr6a_onbellek_kor maskesiyle (başka havuz olaylarının
  olay sonrası pencereleri [t_A, t_A + 365 g) × 4 L_A (ya da R_A) içindeki satırlar döndürülmeden atılır). Manifest
  ve koşu bir adayın sayılarını yalnız o adayın kendi indirmesinden ve kendi pencere/lob tanımlarıyla üretir (§9 adım 3;
  `kendi_indirmesini_oku`).
- User-Agent geneldir; 401/403 yeniden denenmez, atlatılmaz.

Zaman birimi: gün (1970-01-01T00:00:00'dan, kesirli). Pencereler [a, b).
"""
import datetime as dt
import hashlib
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import numpy as np

BURAYA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURAYA)
import tr6_sayim as SAYIM          # noqa: E402  (kumesizlestir: başvuru uygulaması, eşdeğerlik sınaması için)
import tr6_a_kapi as KAPI          # noqa: E402  (maxc, uzaklik_km, DERIN_KM; ağ kodu çağrılmaz)

UA = "Mozilla/5.0 (compatible; research-client)"
VERI_SONU = dt.datetime(2025, 12, 31, 23, 59, 59)
KOR = dt.datetime(2026, 1, 1)
EPOK = dt.datetime(1970, 1, 1)
LIMIT = 20000
LIMIT_PAY = 0.99
PARCA_G = 366                      # yıllık parça (Ek 1 ile aynı)
DERIN_KM = KAPI.DERIN_KM           # 40
TAMPON_G = 730
MC_ESIK_EPS = 1e-6
SIFIR_BUYUKLUK = 0.05
ALT_PENCERE = {
    "A2": ((30, 45), (45, 60), (60, 90), (90, 180), (180, 365)),
    "yedek_a": ((30, 40), (40, 50), (50, 60), (60, 90), (90, 180), (180, 365)),
    "yedek_b": ((30, 40), (40, 50), (50, 60), (60, 90), (90, 180), (180, 365)),
    "yedek_c": ((90, 180), (180, 365)),
}
MC_SON_EK = {"A2": 0.2, "yedek_a": 0.2, "yedek_b": 0.4, "yedek_c": 0.2}
SON_BASLANGIC_G = {"A2": 30, "yedek_a": 30, "yedek_b": 30, "yedek_c": 90}
ALT_EN_AZ = 50


class KorIhlal(Exception):
    """Tarih ya da aşama sınırını aşan istek: ağa gidilmez."""


class BicimHata(Exception):
    """Katalog yanıtı beklenmeyen biçimde: koşu durur. İleti satır içeriği taşımaz."""


class VeriYok(Exception):
    """§5 madde 1: satır sınırı 1 günlük parçada da aşıldı / eşitlik sağlanmadı -> olay 'veri yok'."""


def gun(z):
    """datetime -> gün (1970'ten, kesirli)."""
    if isinstance(z, str):
        z = dt.datetime.fromisoformat(z)
    return (z - EPOK).total_seconds() / 86400.0


def zaman(g):
    return EPOK + dt.timedelta(days=float(g))


def iso_ms(z):
    return z.strftime("%Y-%m-%dT%H:%M:%S.") + f"{z.microsecond // 1000:03d}"


# ================================================================== servisler ve istek kurma
class Servis:
    ad = ""
    taban = ""
    latlon = ("latitude", "longitude")
    limit_var = True
    ekstra = {}
    km_param = False

    def url(self, la, lo, R_km, t0, t1, taban_m, limit=LIMIT):
        q = {self.latlon[0]: f"{la:.4f}", self.latlon[1]: f"{lo:.4f}"}
        if self.km_param:
            q["maxradiuskm"] = f"{R_km:.3f}"
        else:
            q["maxradius"] = f"{R_km / 111.195:.4f}"
        q.update(starttime=iso_ms(t0), endtime=iso_ms(t1), minmagnitude=f"{taban_m:.2f}", format="text")
        if self.limit_var:
            q["limit"] = limit
        q.update(self.ekstra)
        return self.taban + "query?" + urllib.parse.urlencode(q)

    def satir_say(self, metin):
        return sum(1 for s in metin.splitlines() if s.strip() and not s.startswith("#"))


class ComCat(Servis):
    ad = "ComCat"
    taban = "https://earthquake.usgs.gov/fdsnws/event/1/"
    ekstra = {"eventtype": "earthquake"}
    km_param = True


class ISC(Servis):
    ad = "ISC"
    taban = "https://www.isc.ac.uk/fdsnws/event/1/"


class EMSC(Servis):
    ad = "EMSC"
    taban = "https://www.seismicportal.eu/fdsnws/event/1/"
    latlon = ("lat", "lon")


class GeoNet(Servis):
    ad = "GeoNet"
    taban = "https://service.geonet.org.nz/fdsnws/event/1/"
    limit_var = False


_SATIR_KOERI = re.compile(r"^\s*\d{6}\t\d{14}\t\d{4}\.\d\d\.\d\d\t")


class KOERI(Servis):
    """Kandilli zeqdb: yalnız kutu sorgusu, gün çözünürlüğü; daire süzgeci yerelde; limit parametresi yok."""
    ad = "KOERI"
    taban = "http://www.koeri.boun.edu.tr/sismo/zeqdb/submitRecSearchT.asp"
    limit_var = False

    def url(self, la, lo, R_km, t0, t1, taban_m, limit=None):
        dla = R_km / 111.195
        dlo = dla / max(0.2, math.cos(math.radians(la)))
        q = dict(bYear=t0.year, bMont=f"{t0.month:02d}", bDay=f"{t0.day:02d}", eYear=t1.year,
                 eMont=f"{t1.month:02d}", eDay=f"{t1.day:02d}", EnMin=f"{la - dla:.2f}", EnMax=f"{la + dla:.2f}",
                 BoyMin=f"{lo - dlo:.2f}", BoyMax=f"{lo + dlo:.2f}", MAGMin=f"{taban_m:.1f}", MAGMax="9.0",
                 DerMin="0", DerMax="500", Tip="Deprem", ofName="tr6.txt")
        return self.taban + "?" + urllib.parse.urlencode(q)

    def satir_say(self, metin):
        return sum(1 for s in re.sub(r"<[^>]+>", "\n", metin).splitlines() if _SATIR_KOERI.match(s))


SERVIS = {s.ad: s for s in (ComCat(), ISC(), EMSC(), GeoNet(), KOERI())}
SECIM_SIRASI = ("ISC", "ComCat", "GeoNet", "EMSC", "KOERI")


def tarih_denetle(t0, t1, sinir=None):
    """İstek [t0, t1]: t1 ≤ 2025-12-31T23:59:59 ve (verildiyse) t1 ≤ sinir. Aşarsa KorIhlal (ağa gidilmez)."""
    if t1 > VERI_SONU or t0 >= KOR or t1 >= KOR:
        raise KorIhlal(f"istek bitişi {t1.isoformat()} > {VERI_SONU.isoformat()}")
    if sinir is not None and t1 > sinir:
        raise KorIhlal(f"istek bitişi {t1.isoformat()} aşama sınırını ({sinir.isoformat()}) aşıyor")
    if t0 > t1:
        raise KorIhlal("istek başı bitişten sonra")


def mt_url(la, lo, r1_km, r2_km, t0):
    """§3.3 karar 6: halkada [L/2 + 10, 2L], 0-40 km, [1976-01-01, t0), moment-tensor ürünü olan olaylar."""
    q = dict(latitude=f"{la:.4f}", longitude=f"{lo:.4f}", minradiuskm=f"{r1_km:.3f}", maxradiuskm=f"{r2_km:.3f}",
             mindepth="0", maxdepth=f"{DERIN_KM:g}", starttime="1976-01-01T00:00:00.000",
             endtime=iso_ms(t0 - dt.timedelta(milliseconds=1)), producttype="moment-tensor", format="geojson",
             limit=LIMIT, eventtype="earthquake")
    return ComCat.taban + "query?" + urllib.parse.urlencode(q)


# ================================================================== ağ
class Getirici:
    """Nazik HTTP istemcisi: genel UA, istekler arasında bekleme, 401/403/400 yeniden denenmez ve atlatılmaz.
    Her yanıt hedef dizine sha256 adıyla yazılır ve kayıt listesine eklenir. Tarih denetimi çağıranın işidir."""

    def __init__(self, hedef, bekleme=1.0, deneme=4, zaman_asimi=600, ac=None, gunluk=None):
        self.hedef, self.bekleme, self.deneme, self.zaman_asimi = hedef, bekleme, deneme, zaman_asimi
        self.kayitlar = []
        self._ac = ac or urllib.request.urlopen
        os.makedirs(hedef, exist_ok=True)
        # Günlük (isteğe bağlı): aynı ham dizinde yarıda kalan bir aşama sürdürülürken aynı URL yeniden istenmez;
        # dosya sha256 doğrulanarak okunur (aşamayı bölmek için; yeni istek yapmaz).
        self.gunluk, self._gun = gunluk, {}
        if gunluk and os.path.exists(gunluk):
            with open(gunluk, encoding="utf-8") as f:
                for s in f:
                    if s.strip():
                        k = json.loads(s)
                        self._gun[k["url"]] = k

    def __call__(self, url):
        k = self._gun.get(url)
        if k is not None:
            yol = os.path.join(self.hedef, k["sha256"][:2], k["sha256"] + ".txt")
            with open(yol, "rb") as f:
                b = f.read()
            if hashlib.sha256(b).hexdigest() != k["sha256"]:
                raise BicimHata(f"günlükteki ham dosya sha256 tutmuyor: {k['sha256'][:12]}")
            self.kayitlar.append(dict(k, gunlukten=True))
            return b
        son = None
        for i in range(self.deneme):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA})
                with self._ac(req, timeout=self.zaman_asimi) as r:
                    kod = getattr(r, "status", 200)
                    b = r.read()
                if kod == 204:
                    b = b""
                break
            except urllib.error.HTTPError as e:
                if e.code in (204,) or (e.code == 404 and "fdsnws" in url):
                    b = b""
                    break
                if e.code in (400, 401, 403):
                    raise RuntimeError(f"HTTP {e.code} (atlatılmaz)") from None
                son = f"HTTP {e.code}"
            except Exception as e:                                    # noqa: BLE001
                son = type(e).__name__
            time.sleep(min(120, self.bekleme * 5 * 2 ** i))
        else:
            raise RuntimeError(f"erişilemedi ({son})")
        h = hashlib.sha256(b).hexdigest()
        yol = os.path.join(self.hedef, h[:2], h + ".txt")
        os.makedirs(os.path.dirname(yol), exist_ok=True)
        if not os.path.exists(yol):
            with open(yol, "wb") as f:
                f.write(b)
        kay = dict(url=url, sha256=h, boyut=len(b), zaman=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"))
        self.kayitlar.append(kay)
        if self.gunluk:
            with open(self.gunluk, "a", encoding="utf-8") as f:
                f.write(json.dumps(kay) + "\n")
            self._gun[url] = kay
        time.sleep(self.bekleme)
        return b


# ================================================================== parçalı indirme ve satır sınırı (§5 madde 1)
def parcali_indir(srv, la, lo, R_km, t_bas, t_bit, taban_m, getir, sinir=None, en_kisa_g=1.0):
    """[t_bas, t_bit) aralığını yıllık parçalarla ister; satır sınırı kuralı uygulanır. Dönüş dict(metinler
    [(url, metin)], bolunen (sayı), istek (sayı)). getir(url) -> bytes."""
    metinler, sayac = [], dict(bolunen=0, istek=0)
    bit_inc = t_bit - dt.timedelta(milliseconds=1)
    tarih_denetle(t_bas, bit_inc, sinir)

    def iste(a, b):
        tarih_denetle(a, b, sinir)
        u = srv.url(la, lo, R_km, a, b, taban_m)
        sayac["istek"] += 1
        m = getir(u).decode("utf-8", errors="replace")
        return u, m

    def limitli(a, b):
        u, m = iste(a, b)
        n = srv.satir_say(m)
        if n >= LIMIT_PAY * LIMIT:
            if (b - a).total_seconds() <= en_kisa_g * 86400 + 1:
                raise VeriYok(f"{srv.ad}: 1 günlük parçada satır sınırı aşıldı")
            sayac["bolunen"] += 1
            orta = a + (b - a) / 2
            orta = orta.replace(microsecond=(orta.microsecond // 1000) * 1000)
            limitli(a, orta - dt.timedelta(milliseconds=1))
            limitli(orta, b)
        else:
            metinler.append((u, m))

    def esitlikli(a, b, butun=None):
        if butun is None:
            butun = iste(a, b)
        n = srv.satir_say(butun[1])
        if (b - a).total_seconds() <= en_kisa_g * 86400 + 1:
            # 1 günlük parça: yarılarla denetlenemez; KOERI gün çözünürlüklüdür
            yar = None
        else:
            orta = a + (b - a) / 2
            orta = orta.replace(microsecond=(orta.microsecond // 1000) * 1000)
            if srv.ad == "KOERI":
                orta = dt.datetime(orta.year, orta.month, orta.day)
                if orta <= a:
                    orta = a + dt.timedelta(days=1)
            y1 = iste(a, orta - dt.timedelta(milliseconds=1) if srv.ad != "KOERI" else orta - dt.timedelta(days=1))
            y2 = iste(orta, b)
            yar = (orta, y1, y2)
        if yar is None:
            raise VeriYok(f"{srv.ad}: 1 günlük parçada yarı eşitliği denetlenemedi")
        orta, y1, y2 = yar
        if srv.satir_say(y1[1]) + srv.satir_say(y2[1]) == n:
            metinler.append(butun)
            return
        sayac["bolunen"] += 1
        esitlikli(a, orta - dt.timedelta(milliseconds=1) if srv.ad != "KOERI" else orta - dt.timedelta(days=1), y1)
        esitlikli(orta, b, y2)

    a = t_bas
    while a < t_bit:
        b = min(t_bit, a + dt.timedelta(days=PARCA_G))
        b_inc = b - dt.timedelta(milliseconds=1) if srv.ad != "KOERI" else b - dt.timedelta(days=1)
        if srv.ad == "KOERI" and b_inc < a:
            b_inc = a
        if srv.limit_var:
            limitli(a, b_inc)
        else:
            esitlikli(a, b_inc)
        a = b
    return dict(metinler=metinler, bolunen=sayac["bolunen"], istek=sayac["istek"])


# ================================================================== ayrıştırma ve büyüklük kuralları (§3.5)
def _tur_gecer(tur):
    tur = tur.lower()
    return not tur or "earthquake" in tur or tur in ("ke", "se")


def fdsn_ayristir(metin):
    """FDSN text. tr6_a_kapi.fdsn_ayristir ile aynı tür süzgeci ve derinlik varsayılanı (boş -> 10 km); ondan farkı:
    büyüklük türü ve boş büyüklük (NaN) korunur (kural 1/2 sayımı için), biçim hatası durdurur, ≥ 2026 satırlar
    sayılmadan atılır."""
    kim, t, la, lo, de, m, mt = [], [], [], [], [], [], []
    for no, s in enumerate(metin.splitlines(), 1):
        if not s.strip() or s.startswith("#"):
            continue
        a = [x.strip() for x in s.split("|")]
        if len(a) < 11:
            raise BicimHata(f"FDSN satırı {no}: alan sayısı {len(a)} < 11")
        if not _tur_gecer(a[13] if len(a) > 13 else ""):
            continue
        try:
            z = dt.datetime.fromisoformat(a[1].replace("Z", "")[:26])
            if z >= KOR:
                continue
            t.append(gun(z)); la.append(float(a[2])); lo.append(float(a[3]))
            de.append(float(a[4]) if a[4] else 10.0)
            m.append(float(a[10]) if a[10] else math.nan)
        except ValueError:
            raise BicimHata(f"FDSN satırı {no}: sayısal alan çözülemedi") from None
        kim.append(a[0]); mt.append(a[9])
    return dict(id=kim, t=np.array(t), la=np.array(la), lo=np.array(lo), de=np.array(de), m=np.array(m),
                mtip=np.array(mt, dtype=object))


def koeri_ayristir(metin):
    duz = re.sub(r"<[^>]+>", "\n", metin)
    kim, t, la, lo, de, m, mt = [], [], [], [], [], [], []
    for s in duz.splitlines():
        if not _SATIR_KOERI.match(s):
            continue
        a = s.strip("\r\n ").split("\t")
        try:
            z = dt.datetime.fromisoformat(a[2].replace(".", "-") + "T" + a[3][:8])
            if z >= KOR:
                continue
            t.append(gun(z)); la.append(float(a[4])); lo.append(float(a[5])); de.append(float(a[6]))
            m.append(float(a[7]))
        except (ValueError, IndexError):
            raise BicimHata("KOERI satırı çözülemedi") from None
        kim.append(a[1]); mt.append("KOERI")
    if "Liste sonu" not in duz and kim:
        raise BicimHata("KOERI yanıtı yarım (Liste sonu yok)")
    return dict(id=kim, t=np.array(t), la=np.array(la), lo=np.array(lo), de=np.array(de), m=np.array(m),
                mtip=np.array(mt, dtype=object))


def birlestir(parcalar):
    """Parçaları birleştirir; aynı olay kimliği bir kez (parça sınırı tekrarı). Zaman sırasına dizer."""
    if not parcalar:
        return bos_katalog()
    d = {k: np.concatenate([p[k] for p in parcalar]) if k != "id" else sum((list(p[k]) for p in parcalar), [])
         for k in parcalar[0]}
    kim = np.array(d["id"], dtype=object)
    _, ilk = np.unique(kim, return_index=True)
    ilk = np.sort(ilk)
    o = ilk[np.argsort(d["t"][ilk], kind="stable")]
    return {k: (np.asarray(v, dtype=object)[o] if k in ("id", "mtip") else np.asarray(v)[o]) for k, v in d.items()}


def bos_katalog():
    return dict(id=np.array([], dtype=object), t=np.zeros(0), la=np.zeros(0), lo=np.zeros(0), de=np.zeros(0),
                m=np.zeros(0), mtip=np.array([], dtype=object))


def ayristir(katalog, metinler):
    f = koeri_ayristir if katalog == "KOERI" else fdsn_ayristir
    return birlestir([f(m) for _, m in metinler])


def buyukluk_kurallari(d, taban_m):
    """§3.5: (1) büyüklük boş -> at; (2) tür boş ve büyüklük ≤ 0,05 -> at; (3) büyüklük < taban -> at.
    Dönüş (tut maskesi, sayılar dict(kural1, kural2, kural3))."""
    m = d["m"]
    tur_bos = np.array([not str(x).strip() for x in d["mtip"]], bool) if len(m) else np.zeros(0, bool)
    k1 = np.isnan(m)
    k2 = ~k1 & tur_bos & (m <= SIFIR_BUYUKLUK + 1e-12)
    k3 = ~k1 & ~k2 & (m < taban_m - 1e-9)
    return ~(k1 | k2 | k3), dict(kural1=int(k1.sum()), kural2=int(k2.sum()), kural3=int(k3.sum()))


def secim(d, maske):
    return {k: (v[maske] if not isinstance(v, list) else [x for x, s in zip(v, maske) if s]) for k, v in d.items()}


# ================================================================== körleştirme (ad hoc okumalar, §9 adım 3)
def kor_maske(d, havuz, sahip, R_A=None, maske_gun=365, maske_L=4.0):
    """True = tutulur. Havuz olayı A (sahip dışı) için t_A ≤ t < t_A + 365 g ve uzaklık ≤ max(4 L_A, R_A) satırlar
    atılır. tr6a_onbellek_kor._maske ile aynı kural; R_A (manifestte kırık izinden) verilirse genişletilir."""
    n = len(d["m"])
    tut = np.ones(n, bool)
    for a in havuz:
        if a["id"] == sahip:
            continue
        ta = gun(a["zaman"])
        zm = (d["t"] >= ta) & (d["t"] < ta + maske_gun)
        if not zm.any():
            continue
        yar = max(maske_L * a["L_km"], (R_A or {}).get(a["id"], 0.0))
        r = KAPI.uzaklik_km(a["enlem"], a["boylam"], d["la"][zm], d["lo"][zm])
        tut[np.nonzero(zm)[0][r <= yar]] = False
    return tut


def maskeli_oku(kayit, onb):
    """Ek 1 önbelleğinin tek okuma yolu (tr6a_onbellek_kor.oku_sorgu). Yalnız tanı amaçlı."""
    import tr6a_onbellek_kor as KOR_MOD
    return KOR_MOD.oku_sorgu(kayit, onb=onb)


def kendi_indirmesini_oku(dizin, kayitlar):
    """Manifestin ve koşunun bir adayın kendi indirmesini okuyan TEK işlevi (§9 adım 3, İNCELEME-2 K8 `open(`
    denetimi). kayitlar: [dict(url, sha256)]; her dosyanın sha256'sı doğrulanır."""
    out = []
    for k in kayitlar:
        yol = os.path.join(dizin, k["sha256"][:2], k["sha256"] + ".txt")
        with open(yol, "rb") as f:
            b = f.read()
        if hashlib.sha256(b).hexdigest() != k["sha256"]:
            raise BicimHata(f"ham dosya sha256 tutmuyor: {k['sha256'][:12]}")
        out.append((k["url"], b.decode("utf-8", errors="replace")))
    return out


# ================================================================== Mc (§3.5)
def maxc(m):
    """tr6_a_kapi.maxc ile aynı: 0,1 kutu (np.round), en sık kutu; eşitlikte küçük olan."""
    return KAPI.maxc(np.asarray(m, float))


def maxc_sayim(kutular, sayilar):
    """Aynı kural, kutu histogramı üzerinde (kutular artan, np.round(m, 1) değerleri)."""
    kutular, sayilar = np.asarray(kutular, float), np.asarray(sayilar)
    return float(kutular[int(np.argmax(sayilar))])


def r2(x):
    return float(round(x + 1e-12, 2))


def mc_lob(m_lob_on, mc_halka):
    """max(Mc_halka, MAXC(lobun ön penceresindeki olaylar) + 0,2); < 50 olayda Mc_halka + 0,3."""
    m = np.asarray(m_lob_on, float)
    if len(m) < ALT_EN_AZ:
        return r2(mc_halka + 0.3), dict(kural="<50 olay", n=int(len(m)))
    return r2(max(mc_halka, maxc(m) + 0.2)), dict(kural="MAXC+0,2", n=int(len(m)), maxc=maxc(m))


def alt_pencereler(koken, son_bit, kural="A2"):
    """Alt pencereler [koken + a, koken + b) (gün); sonuncusu son_bit'te biter; boş (sıfır uzunluklu) olan atlanır."""
    out = []
    pp = ALT_PENCERE[kural]
    for i, (a, b) in enumerate(pp):
        s, e = koken + a, (son_bit if i == len(pp) - 1 else min(koken + b, son_bit))
        if e > s:
            out.append((s, e))
    return out


def mc_son_hist(histler, mc_lob_deger, ek=0.2):
    """histler: alt pencere başına (kutular, sayılar). Birleştirme: 50'den az olaylı pencere sonrakiyle; sonuncusu
    50'ye ulaşmazsa bir öncekiyle; hiçbir birleşim 50'ye ulaşmazsa Mc_lob + 0,3. Dönüş (Mc_son, döküm)."""
    gruplar, cari = [], None

    def topla(a, b):
        if a is None:
            return b
        k = np.union1d(a[0], b[0])
        s = np.zeros(len(k))
        for kk, ss in (a, b):
            s[np.searchsorted(k, kk)] += ss
        return k, s
    for h in histler:
        cari = topla(cari, h)
        if cari[1].sum() >= ALT_EN_AZ:
            gruplar.append(cari)
            cari = None
    if cari is not None and cari[1].sum() > 0:
        if gruplar:
            gruplar[-1] = topla(gruplar[-1], cari)
        else:
            gruplar = []
    if not gruplar:
        return r2(mc_lob_deger + 0.3), dict(kural="hiçbir birleşim 50'ye ulaşmadı")
    mcs = [r2(maxc_sayim(*g) + ek) for g in gruplar]
    return r2(max(mcs)), dict(kural="alt pencere", gruplar=[dict(n=int(g[1].sum()), mc=x) for g, x in zip(gruplar, mcs)])


def hist(m):
    b = np.round(np.asarray(m, float), 1)
    v, c = np.unique(b, return_counts=True)
    return v, c


def mc_son(t_bolge, m_bolge, koken, son_bit, mc_lob_deger, kural="A2"):
    """§3.5 madde 2: Mc_son = alt pencerelerin MAXC + 0,2'sinin en büyüğü (bölgenin bütün hücreleri)."""
    hs = []
    for s, e in alt_pencereler(koken, son_bit, kural):
        mk = (t_bolge >= s) & (t_bolge < e)
        hs.append(hist(m_bolge[mk]))
    return mc_son_hist(hs, mc_lob_deger, MC_SON_EK[kural])


# ================================================================== kümesizleştirme (§3.6)
def kumesizlestir(t_gun, la, lo, m):
    """tr6_sayim.kumesizlestir ile aynı Gardner-Knopoff (1974) pencere yöntemi (büyükten küçüğe, kararlı sıra; önce ve
    sonra; |Δt| ≤ g, r ≤ d, m_j ≤ m_i; bağımlı olay ana olay olamaz). Zaman sırasına dizilmiş girdi beklenir.
    Hızlı uygulama: adaylar zaman penceresiyle (searchsorted) bulunur. Dönüş: bağımsız maskesi."""
    t_gun, la, lo, m = (np.asarray(a, float) for a in (t_gun, la, lo, m))
    n = len(m)
    if n == 0:
        return np.ones(0, bool)
    if np.any(np.diff(t_gun) < 0):
        raise ValueError("kumesizlestir: zaman sırası bekleniyor")
    d = 10 ** (0.1238 * m + 0.983)
    g = np.where(m >= 6.5, 10 ** (0.032 * m + 2.7389), 10 ** (0.5409 * m - 0.547))
    lo_i = np.searchsorted(t_gun, t_gun - g, "left")
    hi_i = np.searchsorted(t_gun, t_gun + g, "right")
    sla, cla, rlo = np.sin(np.radians(la)), np.cos(np.radians(la)), np.radians(lo)
    sira = np.argsort(-m, kind="stable")
    rutbe = np.empty(n, np.int64)
    rutbe[sira] = np.arange(n)
    # 1) durağan koşulları (zaman, büyüklük, uzaklık) sağlayan bütün (i -> j) kenarları, parçalı ve vektörel
    sayi = hi_i - lo_i
    ki, kj = [], []
    bas = 0
    while bas < n:
        top = np.cumsum(sayi[bas:])
        son = bas + max(1, int(np.searchsorted(top, 4_000_000, "right")))
        idx = np.arange(bas, son)
        c = sayi[idx]
        P = int(c.sum())
        if P:
            ii = np.repeat(idx, c)
            ofs = np.repeat(np.cumsum(c) - c, c)
            jj = lo_i[ii] + (np.arange(P) - ofs)
            ok = (jj != ii) & (m[jj] <= m[ii]) & (np.abs(t_gun[jj] - t_gun[ii]) <= g[ii])
            ii, jj = ii[ok], jj[ok]
            x = sla[ii] * sla[jj] + cla[ii] * cla[jj] * np.cos(rlo[jj] - rlo[ii])
            ok = 6371.0 * np.arccos(np.clip(x, -1, 1)) <= d[ii]
            ki.append(ii[ok])
            kj.append(jj[ok])
        bas = son
    bagimli = np.zeros(n, bool)
    if not ki:
        return ~bagimli
    ki, kj = np.concatenate(ki), np.concatenate(kj)
    if len(ki) == 0:
        return ~bagimli
    # 2) büyükten küçüğe (kararlı) sıra: bağımlı olmayan ana olay kenarlarındaki olayları bağımlı yapar
    o = np.argsort(rutbe[ki], kind="stable")
    ki, kj = ki[o], kj[o]
    sinir = np.flatnonzero(np.diff(ki)) + 1
    for a, b in zip(np.concatenate([[0], sinir]), np.concatenate([sinir, [len(ki)]])):
        if not bagimli[ki[a]]:
            bagimli[kj[a:b]] = True
    return ~bagimli


def kumesizlestir_basvuru(t_gun, la, lo, m):
    """tr6_sayim.kumesizlestir'in kendisi (eşdeğerlik sınaması için)."""
    t = (np.datetime64("1970-01-01T00:00:00") +
         np.round(np.asarray(t_gun) * 86400).astype("timedelta64[s]")).astype("datetime64[s]")
    return SAYIM.kumesizlestir(dict(t=t, lat=np.asarray(la), lon=np.asarray(lo), m=np.asarray(m)), "GK74")


# ================================================================== koşullu binom oyu (§4.3) ve binom
_LF = np.zeros(1)


def _lf(n):
    global _LF
    if len(_LF) <= n + 1:
        _LF = np.concatenate([[0.0], np.cumsum(np.log(np.arange(1, 2 * n + 3)))])
    return _LF


def binom_cdf(k, n, p):
    """P(Binom(n, p) ≤ k), kesin (log uzayında toplam)."""
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    LF = _lf(n)
    i = np.arange(0, k + 1)
    lp = LF[n] - LF[i] - LF[n - i] + i * math.log(p) + (n - i) * math.log1p(-p)
    mx = lp.max()
    return float(min(1.0, math.exp(mx) * np.exp(lp - mx).sum()))


def oy(n_on, n_son, pi):
    """D = n ≥ 1 ve F(n_son; n, π) ≤ 0,5; A = n ≥ 1 ve P(Binom ≥ n_son) ≤ 0,5 (tr6a_onkayit_sayilar.Oy ile aynı 1e-12
    toleransı)."""
    n = n_on + n_son
    if n == 0:
        return 0, 0
    D = int(binom_cdf(n_son, n, pi) <= 0.5 + 1e-12)
    A = int(1.0 - binom_cdf(n_son - 1, n, pi) <= 0.5 + 1e-12)
    return D, A


def p_dusus_kosullu(n, pi):
    """P(D = 1 | n) = F(b*(n); n, π), b* en büyük b: F(b) ≤ 0,5 (koşullu Poisson-binom satırı için)."""
    if n == 0:
        return 0.0
    lo, hi = -1, n
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if binom_cdf(mid, n, pi) <= 0.5 + 1e-12:
            lo = mid
        else:
            hi = mid
    return binom_cdf(lo, n, pi) if lo >= 0 else 0.0


def poisson_binom_ust(x, ps):
    """P(Σ Bernoulli(p_i) ≥ x)."""
    f = np.zeros(len(ps) + 1)
    f[0] = 1.0
    for p in ps:
        f[1:] = f[1:] * (1 - p) + f[:-1] * p
        f[0] *= (1 - p)
    return float(f[x:].sum())


# ================================================================== lob hesabı (§3.5, §3.6, §4.1)
def ust(m, mc):
    return m >= mc - MC_ESIK_EPS


def pencere_sayisi(E, lob, pen, mc, kumesiz=True):
    """E: aday olayları (t, la, lo, m, lob maskeleri için hücre), lob: olay maskesi. pen: dict(on=(a, b),
    son=(s, e) ya da None, son_katalog=c). Ön katalog [a − 730, b), son katalog [c, e); yalnız lob içi ve Mc üstü
    olaylar ana olay/bağımlı olabilir. Dönüş (n_on, n_son)."""
    a, b = pen["on"]
    mk = lob & ust(E["m"], mc)
    on_k = mk & (E["t"] >= a - TAMPON_G) & (E["t"] < b)
    n_on = _say(E, on_k, a, b, kumesiz)
    if pen.get("son") is None:
        return n_on, None
    s, e = pen["son"]
    son_k = mk & (E["t"] >= pen["son_katalog"]) & (E["t"] < e) & ~E.get("ana_sok", np.zeros(len(mk), bool))
    return n_on, _say(E, son_k, s, e, kumesiz)


def _say(E, k, a, b, kumesiz):
    idx = np.nonzero(k)[0]
    if kumesiz and len(idx):
        bag = kumesizlestir(E["t"][idx], E["la"][idx], E["lo"][idx], E["m"][idx])
        idx = idx[bag]
    t = E["t"][idx]
    return int(((t >= a) & (t < b)).sum())
