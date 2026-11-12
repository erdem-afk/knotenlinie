"""TR-6a: ComCat `finite-fault` ürününün seçimi, indirilip dondurulması (manifest kaydı: ürün kimliği, code,
updateTime, öteki ürünler, dosya, sha256), ayrıştırılması (basic_inversion.param, yoksa .fsp) ve moment sağlaması.
Ön kayıt sürüm 3 §3.3 ("Sonlu fay modeli"), İNCELEME-2 K9.

Sonlu fay ürünleri olay sonrası SİSMİSİTE verisi değildir (kaynak modelidir); tarih sınırı katalog olaylarına
uygulanır, kaynak modele uygulanmaz. Gerçek indirme yalnız manifest aşamasında (`tr6a_kosu.py manifest`) yapılır;
bu modülün sınamaları yalnız yerel yapay dosyalarla koşar. Koşu yeniden indirmez: arşivdeki dosya sha256'sı
doğrulanarak okunur (`arsivden_oku`).

Birimler (biçimden; başlıkta yazılı değilse varsayılır ve sağlanır): basic_inversion.param kayma cm, moment dyn·cm,
derinlik km; .fsp kayma m, moment N·m, derinlik km. Varsayım, satır başına ima edilen rijitlik μ = moment / (kayma ×
alan) ile denetlenir: [5, 100] GPa dışında kalan satır varsa BicimHata (birim kayması ΔCFF'yi 100 kat bozardı).

Kodlayıcı okumaları 9-11 (TR-6a_KODLAYICI-OKUMALARI.md): alt fay koordinatının anlamı ve "başlıktaki M0" başlıkta
yoksa kod tahmin etmez: KOORDINAT_KARARI / M0_KAYNAGI_KARARI (kök oturumun Ek 1 kararı) boşsa BicimHata ile durur.
"""
import datetime as dt
import hashlib
import json
import math
import os
import re
import urllib.parse

DETAY_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query?"
MOMENT_TOLERANS = 0.10
MU_ARALIK_GPA = (5.0, 100.0)
# Ek 1 kararları (kök oturum; veri öncesi). None: başlık söylemiyorsa dur.
KOORDINAT_KARARI = None          # "merkez" | "ust_kenar"  (yalnız başlık söylemiyorsa kullanılır)
M0_KAYNAGI_KARARI = None         # "fsp_basligi" (aynı ürünün .fsp başlığındaki Mo) | None


class BicimHata(Exception):
    """Sonlu fay dosyası biçimi beklenmedik: koşu durur (veri yok sayılmaz); ileti dosya içeriği taşımaz."""


class VeriYok(Exception):
    """Ön kayıt §3.3: ürün/dosya yok ya da moment sağlaması tutmadı -> olay 'veri yok'."""


def sha256_bayt(b):
    return hashlib.sha256(b).hexdigest()


# ------------------------------------------------------------------ ürün seçimi
def ffm_urunleri(detay):
    """Olay ayrıntı (geojson) yanıtındaki finite-fault ürünleri, yanıttaki sırayla."""
    return list(((detay.get("properties") or {}).get("products") or {}).get("finite-fault") or [])


def urun_ozeti(u):
    return dict(id=u.get("id"), code=u.get("code"), source=u.get("source"), updateTime=u.get("updateTime"),
                preferredWeight=u.get("preferredWeight"))


def icerik_sec(urun):
    """basic_inversion.param; yoksa .fsp (ad sırasıyla ilk); ikisi de yoksa None."""
    ic = urun.get("contents") or {}
    for ad in sorted(ic):
        if ad.split("/")[-1] == "basic_inversion.param":
            return ad, ic[ad]
    fsp = sorted(a for a in ic if a.lower().endswith(".fsp"))
    if fsp:
        return fsp[0], ic[fsp[0]]
    return None, None


def fsp_icerigi(urun):
    ic = urun.get("contents") or {}
    fsp = sorted(a for a in ic if a.lower().endswith(".fsp"))
    return (fsp[0], ic[fsp[0]]) if fsp else (None, None)


# ------------------------------------------------------------------ ayrıştırma
_SAYI = r"[-+]?\d+(?:\.\d*)?(?:[eE][-+]?\d+)?"


def _koordinat_anlami(basliklar):
    for s in basliklar:
        k = s.lower()
        if "coordinate" in k or "location" in k:
            if "top" in k and "center" in k:
                return "ust_kenar"
            if "center" in k or "centre" in k:
                return "merkez"
    return None


def param_ayristir(metin):
    """USGS basic_inversion.param. Dönüş dict(bicim, altfaylar [dict], basliklar, koordinat_baslik, M0_baslik)."""
    satirlar = metin.splitlines()
    basliklar = [s for s in satirlar if s.startswith("#")]
    segs, alt, seg, dx, dy, veri = [], [], 0, None, None, False
    for no, s in enumerate(satirlar, 1):
        t = s.strip()
        if not t:
            continue
        if t.startswith("#"):
            veri = False
            m = re.search(r"Fault_segment\s*=\s*(\d+).*?Dx\s*=\s*(" + _SAYI + r")\s*km.*?Dy\s*=\s*(" + _SAYI
                          + r")\s*km", t)
            if m:
                seg, dx, dy = int(m.group(1)), float(m.group(2)), float(m.group(3))
                segs.append(dict(segment=seg, dx=dx, dy=dy))
            if re.match(r"#\s*Lat\.?\s+Lon\.?\s+depth\s+slip", t, re.I):
                veri = True
            continue
        if not veri:
            continue                      # sınır köşe satırları (Lon. Lat. Depth)
        a = t.split()
        if len(a) < 11:
            raise BicimHata(f"param: veri satırı {no} alan sayısı {len(a)} < 11")
        try:
            la, lo, de, sl, rk, st, dp = (float(a[i]) for i in range(7))
            mo = float(a[10])
        except ValueError:
            raise BicimHata(f"param: veri satırı {no} sayısal değil") from None
        if dx is None:
            raise BicimHata("param: segment başlığı (Dx, Dy) yok")
        alt.append(dict(segment=seg, enlem=la, boylam=lo, derinlik=de, kayma=sl / 100.0, rake=rk, dogrultu=st,
                        egim=dp, uzunluk=dx, genislik=dy, moment=mo * 1e-7, satir=no))
    if not alt:
        raise BicimHata("param: alt fay satırı yok")
    m0 = None
    for s in basliklar:
        m = re.search(r"\b(?:Mo|M0)\s*[=:]\s*(" + _SAYI + r")\s*(N[\.\-·]?m|dyne?[\.\-·]?cm)?", s)
        if m:
            m0 = float(m.group(1)) * (1e-7 if (m.group(2) or "").lower().startswith("dyn") else 1.0)
    return dict(bicim="param", altfaylar=alt, segmentler=segs, basliklar=basliklar,
                koordinat_baslik=_koordinat_anlami(basliklar), M0_baslik=m0)


def fsp_ayristir(metin):
    """SRCMOD/USGS .fsp. Kayma m, SF_MOMENT N·m. Doğrultu/eğim segment başlığından ya da 'Mech' satırından."""
    satirlar = metin.splitlines()
    basliklar = [s for s in satirlar if s.lstrip().startswith("%")]
    alt, sut = [], None
    dog = egim = None
    dx = dz = None
    m0 = None
    seg = 0
    for no, s in enumerate(satirlar, 1):
        t = s.strip()
        if not t:
            continue
        if t.startswith("%"):
            m = re.search(r"STRI?KE?\s*=\s*(" + _SAYI + r").*?DIP\s*=\s*(" + _SAYI + r")", t, re.I)
            if m:
                dog, egim = float(m.group(1)), float(m.group(2))
            m = re.search(r"SEGMENT\s*#\s*(\d+)", t, re.I)
            if m:
                seg = int(m.group(1))
            m = re.search(r"\bDx\s*=\s*(" + _SAYI + r")\s*km.*?\bDz\s*=\s*(" + _SAYI + r")\s*km", t, re.I)
            if m:
                dx, dz = float(m.group(1)), float(m.group(2))
            m = re.search(r"\bMo\s*=\s*(" + _SAYI + r")\s*(Nm|N-m|N·m|dyne?-?cm)?", t)
            if m:
                m0 = float(m.group(1)) * (1e-7 if (m.group(2) or "").lower().startswith("dyn") else 1.0)
            k = t.lstrip("% ").split()
            if "LAT" in k and "LON" in k and "SLIP" in k:
                sut = k
            continue
        if sut is None:
            raise BicimHata(f"fsp: sütun başlığı olmadan veri satırı {no}")
        a = t.split()
        if len(a) < len(sut):
            raise BicimHata(f"fsp: veri satırı {no} alan sayısı")
        try:
            r = {k: float(a[i]) for i, k in enumerate(sut)}
        except ValueError:
            raise BicimHata(f"fsp: veri satırı {no} sayısal değil") from None
        if dog is None or dx is None:
            raise BicimHata("fsp: doğrultu/eğim ya da Dx/Dz başlıkta yok")
        alt.append(dict(segment=seg, enlem=r["LAT"], boylam=r["LON"], derinlik=r["Z"], kayma=r["SLIP"],
                        rake=r.get("RAKE", float("nan")), dogrultu=dog, egim=egim, uzunluk=dx, genislik=dz,
                        moment=r.get("SF_MOMENT"), satir=no))
    if not alt:
        raise BicimHata("fsp: alt fay satırı yok")
    return dict(bicim="fsp", altfaylar=alt, segmentler=None, basliklar=basliklar,
                koordinat_baslik=_koordinat_anlami(basliklar), M0_baslik=m0)


def birim_denetimi(alt):
    """İma edilen rijitlik μ = moment / (kayma × alan) [5, 100] GPa içinde (kayma > 0 ve moment var)."""
    disari = 0
    for a in alt:
        if a.get("moment") and a["kayma"] > 0:
            mu = a["moment"] / (a["kayma"] * a["uzunluk"] * a["genislik"] * 1e6) / 1e9
            if not (MU_ARALIK_GPA[0] <= mu <= MU_ARALIK_GPA[1]):
                disari += 1
    if disari:
        raise BicimHata(f"birim denetimi: {disari} alt fayda ima edilen rijitlik [5, 100] GPa dışında")


def moment_saglamasi(ayr, M0_baslik):
    """§3.3: alt fay momentleri toplamı başlıktaki M0'ın %10'u içinde. Dönüş dict; tutmazsa VeriYok."""
    top = sum(a["moment"] or 0.0 for a in ayr["altfaylar"])
    if not M0_baslik or M0_baslik <= 0:
        raise BicimHata("başlıkta M0 yok (okuma 10: M0_KAYNAGI_KARARI gerekir)")
    oran = top / M0_baslik
    r = dict(M0_altfay_toplam_Nm=top, M0_baslik_Nm=M0_baslik, oran=round(oran, 6),
             gecti=abs(oran - 1) <= MOMENT_TOLERANS)
    if not r["gecti"]:
        raise VeriYok(f"moment sağlaması tutmadı (oran {oran:.3f})")
    return r


def coz(metin_ana, ad_ana, metin_fsp=None):
    """Seçilen dosyayı ayrıştırır, birim ve moment sağlamasını yapar, koordinat anlamını belirler."""
    ayr = param_ayristir(metin_ana) if ad_ana.split("/")[-1] == "basic_inversion.param" else fsp_ayristir(metin_ana)
    birim_denetimi(ayr["altfaylar"])
    koor = ayr["koordinat_baslik"]
    kaynak_koor = "baslik"
    if koor is None:
        if KOORDINAT_KARARI is None:
            raise BicimHata("alt fay koordinat anlamı başlıkta yok (okuma 9: KOORDINAT_KARARI gerekir)")
        koor, kaynak_koor = KOORDINAT_KARARI, "Ek 1 kararı"
    M0 = ayr["M0_baslik"]
    kaynak_m0 = "baslik"
    if M0 is None:
        if M0_KAYNAGI_KARARI == "fsp_basligi" and metin_fsp:
            M0 = fsp_ayristir(metin_fsp)["M0_baslik"]
            kaynak_m0 = "Ek 1 kararı: aynı ürünün .fsp başlığı"
        else:
            raise BicimHata("başlıkta M0 yok (okuma 10: M0_KAYNAGI_KARARI gerekir)")
    ms = moment_saglamasi(ayr, M0)
    for a in ayr["altfaylar"]:
        a["koordinat"] = koor
    return dict(bicim=ayr["bicim"], altfaylar=ayr["altfaylar"], koordinat=koor, koordinat_kaynagi=kaynak_koor,
                M0_kaynagi=kaynak_m0, moment=ms, n_altfay=len(ayr["altfaylar"]),
                n_segment=len({a["segment"] for a in ayr["altfaylar"]}),
                dikeye_yakin=sum(1 for a in ayr["altfaylar"]
                                 if 1e-6 <= abs(math.cos(math.radians(a["egim"]))) < 1e-3))


# ------------------------------------------------------------------ indirme ve dondurma
def detay_url(olay_id):
    return DETAY_URL + urllib.parse.urlencode(dict(eventid=olay_id, format="geojson"))


def indir(olay_id, hedef, getir_bayt, simdi=None):
    """Bir üyenin ürününü indirip hedef/ffm/<olay_id>/ altına yazar. getir_bayt(url) -> bytes (401/403'te
    istisna; atlatılmaz). Dönüş: manifest kaydı (yalnız üstveri, sha256). Ürün/dosya yoksa kayıt 'veri yok'."""
    d = os.path.join(hedef, "ffm", olay_id)
    os.makedirs(d, exist_ok=True)
    simdi = simdi or dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    b = getir_bayt(detay_url(olay_id))
    with open(os.path.join(d, "detay.geojson"), "xb") as f:
        f.write(b)
    kayit = dict(olay=olay_id, detay_url=detay_url(olay_id), detay_sha256=sha256_bayt(b), indirme_zamani=simdi)
    detay = json.loads(b.decode("utf-8"))
    ur = ffm_urunleri(detay)
    if not ur:
        kayit.update(durum="veri yok", neden="finite-fault ürünü yok")
        return kayit
    ter = ur[0]
    kayit.update(urun=urun_ozeti(ter), oteki_urunler=[urun_ozeti(u) for u in ur[1:]])
    ad, ic = icerik_sec(ter)
    if ad is None:
        kayit.update(durum="veri yok", neden="basic_inversion.param ve .fsp yok")
        return kayit
    dosyalar = []
    for ad_, ic_ in [(ad, ic)] + ([fsp_icerigi(ter)] if not ad.lower().endswith(".fsp") else []):
        if ad_ is None:
            continue
        bb = getir_bayt(ic_["url"])
        yerel = re.sub(r"[^A-Za-z0-9._-]", "_", ad_)
        with open(os.path.join(d, yerel), "xb") as f:
            f.write(bb)
        dosyalar.append(dict(ad=ad_, yerel=os.path.join("ffm", olay_id, yerel), url=ic_["url"],
                             sha256=sha256_bayt(bb), boyut=len(bb)))
    kayit.update(durum="indirildi", dosya=dosyalar[0], ek_dosyalar=dosyalar[1:])
    return kayit


def arsivden_oku(kayit, arsiv_kok):
    """Arşivdeki dosyayı sha256 ile doğrular ve çözer. VeriYok / BicimHata yükseltebilir."""
    if kayit.get("durum") != "indirildi":
        raise VeriYok(kayit.get("neden", "veri yok"))
    metinler = {}
    for df in [kayit["dosya"]] + kayit.get("ek_dosyalar", []):
        b = open(os.path.join(arsiv_kok, df["yerel"]), "rb").read()
        if sha256_bayt(b) != df["sha256"]:
            raise BicimHata(f"sonlu fay dosyası sha256 tutmuyor: {df['yerel']}")
        metinler[df["ad"]] = b.decode("utf-8", errors="replace")
    ana = kayit["dosya"]["ad"]
    fsp = next((m for a, m in metinler.items() if a.lower().endswith(".fsp") and a != ana), None)
    r = coz(metinler[ana], ana, fsp)
    for a in r["altfaylar"]:
        a["uye"] = kayit["olay"]
    return r
