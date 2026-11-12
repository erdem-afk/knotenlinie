#!/usr/bin/env python3
"""TR-10b HDR adımı (ön kayıt sürüm 2 §6.4; §14 madde 2). HDR dosyaları ÜSTVERİDİR; hiçbir kayma/veri dosyası
açılmaz, hiçbir hız hesaplanmaz.

Kural kodu `onkayit_yardimci/inc1_hdr_kural.py`'nin çekirdek işlevleridir (notlara_bol, tarih, onekler, tur, isle);
burada DEĞİŞTİRİLMEDEN içe aktarılır. README'ye özgü istasyon ataması kullanılmaz: not, bulunduğu .hdr1 dosyasının
istasyonuna aittir (§6.4 madde 3).

BİÇİM UYARLAMASI (§6.4 madde 5; yalnız not birimi ve tarih tanıma; yalnız ekler). HDR dosyalarında README'de
olmayan bir tablo biçimi var: "N 201402120040 Wire Reset", "S N 2016j3431450 ...", "T ...", "M 2024j1981750 ...",
"N 24j310232000 ..." (bir ya da iki tek harfli bayrak + zaman damgası + metin). Kuralın paragraf birimi bu satırları
tek bir nota toplar ve zaman damgasını tanımaz; tablo bu yüzden tarihsiz tek bir not olur. Uyarlama:
  (1) not birimi: paragraf içindeki her TABLO SATIRI (ardından gelen, boşlukla başlayan ve tablo satırı olmayan devam
      satırlarıyla) ayrı bir nottur; paragrafın öteki satırları, tablo satırlarıyla bölünen her ardışık parça için,
      ayrı bir not olarak kalır (ör. "Times of possible offsets:" başlığı). Tablo satırı olmayan paragraflar
      değişmez; hiç boş satırı olmayan dosyada her satır yine bir nottur.
  (2) tarih tanıma: üç zaman damgası biçimi TAM tarih biçimlerine EKLENİR: YYYYAAGGssdd (12 rakam), YYYYjGGGssdd
      (yılın günü), YYjGGGssddss (iki haneli yıl, §6.4'teki 19xx/20xx kuralıyla). En soldaki tam tarih kuralı
      aynen geçerlidir. Mevcut biçimlerin hiçbiri çıkarılmaz.
Önek listeleri, tür kuralı, tarihsiz not kuralı ve `isle` değişmez. Uyarlama `inc1_hdr_kural` modülünün
`notlara_bol` ve `tarih` adlarına, işlevlerin kendisi değiştirilmeden, sarmalayıcı olarak bağlanır (`uyarlamayi_kur`).
README sınaması uyarlanmış kuralla koşulur ve başvuru çıktısını bayt bayt yeniden üretmelidir (madde 5 (ii)).

Alt komutlar (depo kökünden, `python3 -I -B`):
  readme  <README_CREEP.txt> <inc1 listeler.json>
      Kuralı README "Comments specific to various creepmeters" bölümünde koşar (inc1_hdr_kural.py'nin kendisi) ve
      çıktıyı `onkayit_yardimci/inc1_hdr_kural_basvuru.txt` ile (iki başlık satırı dışında) bayt bayt karşılaştırır.
      Uyuşmazsa çıkış kodu 2.
  indir   <hedef_dizin> <dizin_HDR2025.html> [--manifest kayit/turetme/tr10b/tr10b_manifest_hdr.json]
      Sırayla indirir: sayfada bağlantısı olan 29 CREEP/HDR/*.hdr1 (alfabetik), CREEP/HDR2025/ altındaki 30 *.hdr1
      (dizin listesinden; alfabetik), CREEP/HDR/caveat.txt. `._*` ve HDRx.tar indirilmez. İstekler arası 2 sn,
      genel User-Agent; 401/403/404 yeniden denenmez ve atlatılmaz. Manifest "x" kipinde bir kez yazılır.
  uygula  <hdr_dizini> [--manifest ...] [--cikti-dizin kayit/turetme/tr10b]
      Her dosyanın sha256'sını manifestle denetler (uyuşmazsa durur), kuralı §6.4 madde 2 sırasıyla uygular,
      `tr10b_hdr_olaylar.csv` ve `tr10b_hdr_etki.json` dosyalarını bellekte kurup "x" kipinde bir kez yazar.
"""
import csv
import datetime as dt
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

BURA = os.path.dirname(os.path.abspath(__file__))
YARDIMCI = os.path.join(BURA, "onkayit_yardimci")
sys.path.insert(0, BURA)
sys.path.insert(0, YARDIMCI)
import inc1_hdr_kural as HK  # noqa: E402  (çekirdek işlevler; değiştirilmez)
import tr10b_listeler as TL  # noqa: E402
import tr10b_sayim as KS  # noqa: E402

ARSIV = "https://escweb.wr.usgs.gov/share/langbein/Archive/CREEP/"
BASVURU = os.path.join(YARDIMCI, "inc1_hdr_kural_basvuru.txt")
MANIFEST = os.path.join(BURA, "tr10b_manifest_hdr.json")
UA = "Mozilla/5.0 (compatible; metadata-fetch)"
BEKLE = 2.0
DENEME = 3


def sha256_bayt(b):
    return hashlib.sha256(b).hexdigest()


def sha256_dosya(yol):
    return sha256_bayt(open(yol, "rb").read())


# ------------------------------------------------------------------ biçim uyarlaması (madde 5)
_ORIJ_NOTLARA_BOL = HK.notlara_bol
_ORIJ_TARIH = HK.tarih
_DAMGA = (r"((?:19|20)\d\d)(0[1-9]|1[0-2])(\d\d)\d{4}"          # YYYYAAGGssdd
          r"|((?:19|20)\d\d)j(\d{3})\d{4}"                       # YYYYjGGGssdd
          r"|(\d\d)j(\d{3})\d{6}")                               # YYjGGGssddss
DAMGA_RE = re.compile(r"(?<![a-z0-9])(?:" + _DAMGA + r")(?![0-9])", re.I)
TABLO_SATIRI = re.compile(r"^\s*(?:[A-Z]\s+){1,2}(?:" + _DAMGA + r")(?![0-9])")


def _damga_tarihi(m):
    try:
        if m.group(1):
            return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        if m.group(4):
            g = int(m.group(5))
            return dt.date(int(m.group(4)), 1, 1) + dt.timedelta(days=g - 1) if 1 <= g <= 366 else None
        g = int(m.group(7))
        y = HK._yy(m.group(6))
        return dt.date(y, 1, 1) + dt.timedelta(days=g - 1) if 1 <= g <= 366 else None
    except ValueError:
        return None


def tarih_uyarli(metin):
    """HK.tarih + zaman damgası biçimleri (ek). En solda başlayan tam tarih; eşit konumda HK.TAM sırası önce."""
    m_ = metin.lower()
    aday = []
    for sira, (p, f) in enumerate(HK.TAM):
        for m in re.finditer(p, m_):
            try:
                d = f(m)
            except (ValueError, KeyError):
                d = None
            if d is not None:
                aday.append((m.start(), sira, d))
    for m in DAMGA_RE.finditer(m_):
        d = _damga_tarihi(m)
        if d is not None:
            aday.append((m.start(), len(HK.TAM), d))
    if aday:
        return min(aday)[2], "tam"
    return _ORIJ_TARIH(metin)


def notlara_bol_uyarli(satirlar):
    """HK.notlara_bol + tablo satırı birimi (ek). Dönüş biçimi aynı: [(ilk_satir_no, [satırlar])], satır sırasıyla."""
    out = []
    for bas, p in _ORIJ_NOTLARA_BOL(satirlar):
        if not any(TABLO_SATIRI.match(s) for s in p):
            out.append((bas, p))
            continue
        cur, cbas, tablo = [], None, False
        for j, s in enumerate(p):
            if TABLO_SATIRI.match(s):
                if cur:
                    out.append((cbas, cur))
                cur, cbas, tablo = [s], bas + j, True
            elif tablo and s[:1].isspace():
                cur.append(s)                      # tablo satırının devam satırı
            else:
                if tablo:
                    out.append((cbas, cur))
                    cur, cbas, tablo = [], None, False
                if cbas is None:
                    cbas = bas + j
                cur.append(s)
        if cur:
            out.append((cbas, cur))
    return out


def uyarlamayi_kur():
    HK.notlara_bol = notlara_bol_uyarli
    HK.tarih = tarih_uyarli


# ------------------------------------------------------------------ (ii) README sınaması
def readme_sinama(readme, lj):
    bas = open(BASVURU, encoding="utf-8").read().split("\n", 2)[2]
    out0 = subprocess.run([sys.executable, "-I", "-B", os.path.join(YARDIMCI, "inc1_hdr_kural.py"), readme, lj],
                          capture_output=True, text=True, check=True).stdout
    # uyarlanmış kural: aynı main, notlara_bol ve tarih sarmalayıcılarıyla (süreç içinde)
    import contextlib
    uyarlamayi_kur()
    eski = sys.argv
    sys.argv = ["inc1_hdr_kural.py", readme, lj]
    tampon = io.StringIO()
    try:
        with contextlib.redirect_stdout(tampon):
            HK.main()
    finally:
        sys.argv = eski
    out1 = tampon.getvalue()
    a0, a1 = out0 == bas, out1 == bas
    print(f"README sınaması (README sha256 {sha256_dosya(readme)}; başvuru sha256 {sha256_dosya(BASVURU)}):")
    print(f"  uyarlanmamış kural: başvuru çıktısı {'BAYT BAYT AYNI' if a0 else 'FARKLI'}")
    print(f"  uyarlanmış kural (madde 5): başvuru çıktısı {'BAYT BAYT AYNI' if a1 else 'FARKLI'}")
    return a0 and a1


# ------------------------------------------------------------------ indirme listesi
def sayfa_hdr(tr10_ham):
    ls = sorted({u for s in KS.sayfa_istasyonlar(tr10_ham) for u in s["dosya"]["HDR"]})
    assert len(ls) == 29 and all(u.startswith(ARSIV + "HDR/") and u.endswith(".hdr1") for u in ls), ls
    assert ARSIV + "HDR/c461.hdr1" not in ls
    return ls


def hdr2025_listesi(dizin_html):
    t = open(dizin_html, encoding="utf-8", errors="replace").read()
    adlar = sorted({m for m in re.findall(r'href="\./([^"/]+\.hdr1)"', t) if not m.startswith("._")})
    assert len(adlar) == 30 and "c461.hdr1" in adlar, adlar
    return [ARSIV + "HDR2025/" + a for a in adlar], sha256_dosya(dizin_html)


def indir_bir(url, hedef_yol):
    son = None
    for d in range(DENEME):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                b = r.read()
                lm = r.headers.get("Last-Modified", "")
                st = r.status
            with open(hedef_yol, "xb") as f:
                f.write(b)
            return dict(url=url, durum="tamam", http=st, boy=len(b), last_modified=lm, sha256=sha256_bayt(b),
                        zaman=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), deneme=d + 1)
        except urllib.error.HTTPError as e:
            son = f"HTTP {e.code}"
            if e.code in (401, 403, 404):          # atlatılmaz, yeniden denenmez
                break
        except Exception as e:                     # noqa: BLE001
            son = f"{type(e).__name__}: {e}"
        time.sleep(BEKLE * 2 ** d)
    return dict(url=url, durum="hata", hata=son, zaman=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"))


def indir(hedef, tr10_ham, dizin_hdr2025, manifest_yol):
    depo = TL.DEPO
    if os.path.commonpath([os.path.abspath(hedef), depo]) == depo:
        sys.exit("DUR: hedef dizin depo içinde")
    if os.path.exists(manifest_yol):
        sys.exit("DUR: HDR manifesti zaten var (tek indirme)")
    l1 = sayfa_hdr(tr10_ham)
    l2, dizin_sha = hdr2025_listesi(dizin_hdr2025)
    l3 = [ARSIV + "HDR/caveat.txt"]
    os.makedirs(os.path.join(hedef, "HDR"), exist_ok=False)
    os.makedirs(os.path.join(hedef, "HDR2025"), exist_ok=False)
    kayit = []
    for u in l1 + l2 + l3:
        alt = "HDR2025" if "/HDR2025/" in u else "HDR"
        r = indir_bir(u, os.path.join(hedef, alt, u.rsplit("/", 1)[1]))
        r["yerel"] = f"{alt}/{u.rsplit('/', 1)[1]}"
        kayit.append(r)
        print(r["durum"], r.get("http", ""), r.get("boy", r.get("hata")), u, flush=True)
        time.sleep(BEKLE)
    man = dict(aciklama="TR-10b HDR adımı (§2.4 madde 1, §6.4): HDR/HDR2025 .hdr1 dosyaları ve caveat.txt; üstveri.",
               sira="1) sayfada bağlantılı 29 CREEP/HDR/*.hdr1 (alfabetik) 2) CREEP/HDR2025/*.hdr1, 30 dosya "
                    "(alfabetik) 3) CREEP/HDR/caveat.txt",
               hdr2025_dizin_listesi_sha256=dizin_sha, sayfa_sha256=KS.SAYFA_SHA, user_agent=UA,
               dosyalar=kayit, basarisiz=[r["url"] for r in kayit if r["durum"] != "tamam"])
    metin = json.dumps(man, ensure_ascii=False, indent=1) + "\n"
    with open(manifest_yol, "x", encoding="utf-8") as f:
        f.write(metin)
    print("manifest:", manifest_yol, "başarısız:", man["basarisiz"])


# ------------------------------------------------------------------ uygulama
def dosya_notlari(yol):
    """Bir .hdr1 dosyasının notları: [(1 tabanlı ilk satır no, birleştirilmiş metin)] (README vekiliyle aynı
    birleştirme: satırlar strip edilip tek boşlukla birleştirilir)."""
    L = open(yol, encoding="utf-8", errors="replace").read().splitlines()
    return [(sn + 1, " ".join(s.strip() for s in p)) for sn, p in HK.notlara_bol(L)]


def kod_gecer(kod, metin):
    """caveat.txt notunda istasyon kodu geçiyor mu (büyük-küçük harf duyarsız; önünde/ardında harf ya da rakam yok)."""
    return re.search(r"(?<![a-z0-9])" + kod.lower() + r"(?![a-z0-9])", metin.lower()) is not None


def uygula(hdr_dizin, manifest_yol, cikti_dizin, ilk_gozlem):
    uyarlamayi_kur()
    man = json.load(open(manifest_yol, encoding="utf-8"))
    sira = [r for r in man["dosyalar"]]
    for r in sira:
        if r["durum"] != "tamam":
            continue
        if sha256_dosya(os.path.join(hdr_dizin, r["yerel"])) != r["sha256"]:
            sys.exit(f"DUR: {r['yerel']} sha256 manifestle uyuşmuyor")
    olaylar, dosya_ozet, caveat_listesi = [], [], []
    for r in sira:
        if r["durum"] != "tamam":
            dosya_ozet.append(dict(dosya=r["yerel"], durum="indirilemedi", hata=r.get("hata")))
            continue
        yol = os.path.join(hdr_dizin, r["yerel"])
        notlar = dosya_notlari(yol)
        ad = os.path.basename(yol)
        if ad == "caveat.txt":
            kodlar = sorted(set(ilk_gozlem) | {os.path.basename(x["yerel"])[:-5].upper() for x in sira
                                               if x["yerel"].endswith(".hdr1")})
            for sn, m in notlar:
                gecen = [k for k in kodlar if kod_gecer(k, m)]
                t, es = HK.tur(m)
                d, cins = HK.tarih(m)
                caveat_listesi.append(dict(satir=sn, kodlar=gecen, tur=t, es=es,
                                           tarih=d.isoformat() if d else None, cins=cins))
            for k in sorted({k for c in caveat_listesi for k in c["kodlar"]}):
                # "aynı dosyadaki iki tarih": caveat.txt'nin bütün notları; olay yalnız kodu geçen nota ait
                ilk = ilk_gozlem.get(k, dt.date(1960, 1, 1))
                metin = dict(notlar)
                for o in HK.isle(notlar, ilk):
                    if kod_gecer(k, metin[o["satir"]]):
                        olaylar.append(dict(o, istasyon=k, dosya=r["yerel"]))
            dosya_ozet.append(dict(dosya=r["yerel"], not_sayisi=len(notlar), istasyon="(caveat)"))
            continue
        kod = ad[:-5].upper()
        ilk = ilk_gozlem.get(kod)
        ilk_not = ""
        if ilk is None:
            ilk, ilk_not = dt.date(1960, 1, 1), "sayfada yok; tarihsiz not başı 1960-01-01"
        ol = HK.isle(notlar, ilk)
        for o in ol:
            olaylar.append(dict(o, istasyon=kod, dosya=r["yerel"]))
        dosya_ozet.append(dict(dosya=r["yerel"], istasyon=kod, not_sayisi=len(notlar), olay=len(ol),
                               tarihli_not=sum(1 for _, m in notlar if HK.tarih(m)[0] is not None),
                               ilk_gozlem_notu=ilk_not,
                               bos_satirsiz=not any(HK.AYRAC.fullmatch(s) for s in
                                                    open(yol, encoding="utf-8", errors="replace").read().splitlines())))
    return olaylar, dosya_ozet, caveat_listesi


def etki(olaylar, L, ist):
    """Olayların aday listelerine etkisi. K: [w0 − 30 g, T + 15 g] aralığı olay tarihini (tarihsiz notta aralığı)
    içeren/kesen istasyon-pencere düşer. D: yalnız 'D dışarıda' bilgi satırında."""
    def dusen(tur):
        out = {}
        for o in olaylar:
            if o["tur"] != tur:
                continue
            for Y in HK.dusen_epoklar(o):
                out.setdefault((o["istasyon"], Y), []).append(o)
        return out
    Kd, Dd = dusen("K"), dusen("D")

    def ozet(sw):
        sp = {}
        for k, y in sorted(sw, key=lambda x: (ist[x[0]]["ilk"], x[0])):
            sp.setdefault((ist[k]["site"], y), k)
        kes = {}
        for (site, y), k in sp.items():
            kes[ist[k]["kesim"]] = kes.get(ist[k]["kesim"], 0) + 1
        return dict(istasyon_pencere=len(sw), istasyon=len({k for k, _ in sw}), yer_pencere=len(sp),
                    yer=len({s for s, _ in sp}), kesim=len(kes), kesim_basina_yer_pencere=dict(sorted(kes.items())))
    sonuc = {}
    for ad, v in L.items():
        v = set(v)
        kdus = sorted(x for x in v if x in Kd)
        ddus = sorted(x for x in v if x in Dd)
        kalan = v - set(kdus)
        sonuc[ad] = dict(
            once=ozet(v), K_sonrasi=ozet(kalan), K_dusen=[f"{k}|{y}" for k, y in kdus],
            K_dusen_creep_event=sum(1 for x in kdus if any(o["creep_event"] for o in Kd[x])),
            D_disarida_dusen=[f"{k}|{y}" for k, y in ddus],
            K_ve_D_sonrasi=ozet(kalan - set(ddus)))
    return sonuc


def csv_metni(olaylar):
    s = io.StringIO()
    w = csv.writer(s, lineterminator="\n")
    w.writerow(["istasyon", "dosya", "satir", "tur", "tarih", "tarihsiz", "aralik_bas", "aralik_son", "tarih_cinsi",
                "eslesen", "creep_event", "dusurdugu_epoklar"])
    for o in sorted(olaylar, key=lambda o: (o["istasyon"], o["dosya"], o["satir"])):
        w.writerow([o["istasyon"], o["dosya"], o["satir"], o["tur"], "" if o["tarihsiz"] else o["a"].isoformat(),
                    int(o["tarihsiz"]), o["a"].isoformat(), o["b"].isoformat(), o["cins"] or "",
                    ";".join(o["es"]), int(o["creep_event"]), ";".join(map(str, HK.dusen_epoklar(o)))])
    return s.getvalue()


def main():
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    if a[0] == "readme":
        sys.exit(0 if readme_sinama(a[1], a[2]) else 2)
    if a[0] == "indir":
        mi = a.index("--manifest") + 1 if "--manifest" in a else None
        tr10_ham = a[a.index("--tr10-ham") + 1]
        indir(a[1], tr10_ham, a[2], a[mi] if mi else MANIFEST)
        return
    if a[0] == "uygula":
        manifest_yol = a[a.index("--manifest") + 1] if "--manifest" in a else MANIFEST
        cd = a[a.index("--cikti-dizin") + 1] if "--cikti-dizin" in a else BURA
        csv_yol, js_yol = os.path.join(cd, "tr10b_hdr_olaylar.csv"), os.path.join(cd, "tr10b_hdr_etki.json")
        for y in (csv_yol, js_yol):
            if os.path.exists(y):
                sys.exit(f"DUR: {y} zaten var (tek koşu)")
        T = TL.listeleri_yukle()
        ist = T["istasyon"]
        j = json.load(open(TL.JSON_YOL, encoding="utf-8"))
        # tarihsiz not başı için "sayfadaki ilk gözlem": B istasyonları için dondurulmuş üstveriden; öteki
        # istasyonlar için sayfa anlık görüntüsünden (--tr10-ham verilirse)
        ilk = {k: dt.date.fromisoformat(v["ilk"]) for k, v in ist.items()}
        if "--tr10-ham" in a:
            for s in KS.sayfa_istasyonlar(a[a.index("--tr10-ham") + 1]):
                ilk.setdefault(s["kod"], s["ilk"])
        kural_sha = {os.path.basename(p): sha256_dosya(p) for p in
                     (os.path.join(YARDIMCI, "inc1_hdr_kural.py"), os.path.abspath(__file__))}
        olaylar, dozet, cav = uygula(a[1], manifest_yol, cd, ilk)
        e = etki(olaylar, T["listeler"], ist)
        out = dict(aciklama="TR-10b HDR adımı (§6.4) sonucu: olayların aday listelerine etkisi (veri öncesi; U kapsamı "
                            "üst sınırı). Notlardaki kayma/hız ifadeleri kayda alınmaz.",
                   girdi=dict(manifest_sha256=sha256_dosya(manifest_yol), listeler_json_sha256=T["json_sha256"],
                              kural_kodu_sha256=kural_sha, onkayit_sha256=TL.MD_SHA),
                   olay_sayisi=dict(K=sum(o["tur"] == "K" for o in olaylar), D=sum(o["tur"] == "D" for o in olaylar),
                                    tarihsiz_K=sum(o["tur"] == "K" and o["tarihsiz"] for o in olaylar),
                                    tarihsiz_D=sum(o["tur"] == "D" and o["tarihsiz"] for o in olaylar),
                                    yalin_yil=sum(o["cins"] == "yalin" for o in olaylar)),
                   dosyalar=dozet, caveat_notlari=cav, etki=e,
                   kapi_ust_sinir_B=dict(yer=e["B"]["K_sonrasi"]["yer"], yer_pencere=e["B"]["K_sonrasi"]["yer_pencere"],
                                         ulasilabilir=e["B"]["K_sonrasi"]["yer"] >= 20 and
                                         e["B"]["K_sonrasi"]["yer_pencere"] >= 40))
        c = csv_metni(olaylar)
        js = json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n"
        with open(csv_yol, "x", encoding="utf-8") as f:
            f.write(c)
        with open(js_yol, "x", encoding="utf-8") as f:
            f.write(js)
        print(json.dumps(dict(olay_sayisi=out["olay_sayisi"], kapi=out["kapi_ust_sinir_B"],
                              etki={ad: dict(K_dusen=v["K_dusen"], yp_once=v["once"]["yer_pencere"],
                                             yp_sonra=v["K_sonrasi"]["yer_pencere"], yer_sonra=v["K_sonrasi"]["yer"],
                                             D_disarida=v["D_disarida_dusen"],
                                             creep_event=v["K_dusen_creep_event"]) for ad, v in e.items()}),
                         ensure_ascii=False, indent=1))
        return
    sys.exit(__doc__)


if __name__ == "__main__":
    main()
