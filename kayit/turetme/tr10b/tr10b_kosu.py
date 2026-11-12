#!/usr/bin/env python3
"""TR-10b tek koşu kodu (ön kayıt sürüm 2; DONDURULDU, sha256 6993ae4a…4da4).

Hüküm sırası (§10): veri kapısı → kod denetimi yapay veriyle → pozitif kontrol gerçek veride → ölçü. Gerçek Δv
havuzu yalnız ilk üç adım geçtikten sonra (ya da kapı geçmediyse, 2. ve 3. adım geçtikten sonra "kapı altı" bilgi
satırı için) hesaplanır. Ondan hemen önce iki işaret dosyası "x" kipinde oluşturulur (§14 madde 6).

Girdiler (hepsi denetlenir; uyuşmazlıkta KosuDur):
  - ön kayıt metni (dondurulmuş ilk 77114 bayt sha256), §4 tablosundan B ve A listeleri (kanonik sha256);
  - tr10b_listeler.json (B_R2, A_R2, B1 geçmiş 5 y alt kümeleri ve istasyon üstverisi; sha256 sabit);
  - tr10b_hdr_olaylar.csv (HDR adımının çıktısı; sha256 sabit);
  - veri manifesti tr10b_manifest_veri.json (dosya başına sha256; veri dosyaları manifestle karşılaştırılır).
Listeler yeniden hesaplanmaz (sakinlik, kapsam yok); yalnız gerçek veri ve §8 şartları daraltır.

Okuma (§2.3, §5): yalnız ilk iki sütun (yıl, gün) her satırda ayrıştırılır. Tarih bir okuma aralığına düşmüyorsa
satırın değer sütunu ayrıştırılmaz, saklanmaz; yalnız sayılır. Okuma dosya sonuna dek sürer (erken durma yok).
Biçim hatası koşuyu durdurur (KosuDur), "veri yok" üretmez; durma iletisi yalnız biçim keşfi bilgisini taşır
(sütun 3 ve sonrası `***`).

Kullanım (depo kökünden):
  python3 -I -B kayit/turetme/tr10b/tr10b_kosu.py --veri <veri_dizini> [--manifest ...] [--cikti-dizin ...]
          [--isaret-depo ...] [--duzeltme-turu 0|1|2] [--bicim-belirsiz URL,...] [--devam]
Çıktılar (bellekte kurulur, "x" kipinde bir kez yazılır): tr10b_sonuc.json, tr10b_sonuc.md; kod denetimi
başarısızsa ve düzeltme turu < 2 ise yalnız tr10b_denetim_tur<N>.json (gerçek Δv hesaplanmaz).
Çıkış kodları: 0 sonuç yazıldı; 2 KosuDur (girdi/biçim/kuru prova; işaret yazılmadı); 3 kod denetimi başarısız
(düzeltme turu açık); 4 işaret sonrası istisna (yalnız doğrudan neden düzeltilip --devam).

Kod incelemesi (TR-10b_KOD-INCELEME.md) sonrası yapı: Ek 1 E1.4 (MIC okuma aralığı [w0 − 90 g, T + 90 g] ve "MIC
dar aralık" bilgi satırı), E1.3 ("başlık katılmış" bilgi satırı) uygulandı. Gerçek Δv'ye bağlı olmayan her adım
işaretten önce koşar; işaretten önce ölçü/hüküm/çıktı kodu yapay değerlerle kuru koşulur; okuma sonucu işaretle
birlikte veri dizinine (depo dışı) yazılır, işaret onun sha256'sını taşır (--devam bu görüntüden sürdürür).
"""
import argparse
import copy
import csv
import datetime as dt
import gzip
import hashlib
import io
import json
import math
import os
import re
import sys
import pickle
import time
import zlib

import numpy as np

BURA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURA)
import tr10b_listeler as TL  # noqa: E402
import tr10b_sayim as KS  # noqa: E402

T2 = KS.T2

# ---------------------------------------------------------------- bağlayıcı sabitler (ön kayıt sürüm 2)
LISTELER_JSON_SHA = "d0c2246007c25f11027cc3325ff3cfa53b3984296d0cf6c82f30e8dacffdcba5"
HDR_CSV_SHA = "5171bd52941b47bb260cd6444eb4c5933c19b9ce10fb15b50fd667ead110531a"
HDR_CSV = os.path.join(BURA, "tr10b_hdr_olaylar.csv")
# Ek 1 E1.3: "başlık katılmış" bilgi satırının HDR olay tablosu (tr10b_hdr_baslik.py; yalnız üstveri)
HDR_BASLIK_CSV_SHA = "c3f8cabb95ed2415cf540399d6dfb3a9195cb7a52377315b7015840885796dea"
HDR_BASLIK_CSV = os.path.join(BURA, "tr10b_hdr_olaylar_baslik_katilmis.csv")
# §6.4 madde 4 "creep/event" sayacı HDR adımının çıktısından okunur
HDR_ETKI_SHA = "89632d2f57ac11f2081df3bf85b63b42ede495ef059f94098aa7e5635185ea03"
HDR_ETKI = os.path.join(BURA, "tr10b_hdr_etki.json")
MANIFEST_VERI = os.path.join(BURA, "tr10b_manifest_veri.json")
ISARET_AD = "TR10B_GERCEK_DV_HESAPLANDI"
ANLIK_AD = "TR10B_HAM_OKUMA_ANLIK.pickle"   # işaretle birlikte veri dizinine yazılan okuma sonucu (depo dışı)
SON_GUN = dt.date(2023, 10, 16)          # §2.3: kullanılabilecek son gün
KAYNAK_SIRA = ("DAY", "10MIN", "MIC")    # §8.3
UC = 15                                  # §8.1: u(P) = [P − 15 g, P + 15 g]
MIC_GENIS = 90                           # Ek 1 E1.4: yalnız MIC okuma aralığı [w0 − 90 g, T + 90 g] (≤ SON_GUN)
UC_MIN = 10
DOLULUK = 0.60
BOSLUK = 60
MAN_YAKIN = 90
MAN_N_TABAN, MAN_N_YAKIN = 12, 8
MAN_ARALIK = 180
SUNEN_V5 = 2.0
K_TAMPON = 30                            # §6.1: [w0 − 30 g, T + 15 g]
KAPI_YER, KAPI_YP = 20, 40
K_MIN = 4
N_GUC = 20
N_Q99 = 300
B_BOOT = 2000
TOHUM = 20261112
C1 = 1.78
ETIKET_UST, ETIKET_ALT = 4.6, 2.2
KAPPA_GAUSS = 2.91
CH_R, CH_V = 0.43, 8.0
BOZUK_PAY = 0.01
DEGER_UST = 1e4
DOLGU_KOSU, DOLGU_K = 15, 0.6
# (a)–(c) eşikleri (§10.2, §10.3)
A_TAM, A_MASKE, A_ELLE, A_3, A_4 = 0.005, 0.50, 1e-6, 1e-6, 1e-6
B_ORAN = (0.88, 1.12)
B_GEN = 3.0                              # rastgele yürüyüş b, mm/yıl^0,5
B_BEYAZ = 0.1
B_N_PAY = 820
B_M = 2000
B_TAM_N = 20000
F144_ESIK = 0.005
PK_TELE = (4.72, 5.11)
PK_MEDYAN = (4.85, 5.03)
PK_ELLE = 1e-6
PK_HIZ = 5.0
N0_M = 2000
DT_YIL = 1.0 / 365.25

# README "Noise model for Creepmeters" tablosu: tr10b_sayim.beklenti içindeki TAB (kaynak metinden okunur)
_src = open(os.path.join(BURA, "tr10b_sayim.py"), encoding="utf-8").read()
README_TAB = {k: (float(n), float(a)) for k, n, a in
              re.findall(r'\("([A-Z0-9]{4})", (\d\.\d\d), (\d+\.\d\d), -?\d+\.\d\)', _src)}
assert len(README_TAB) == 18


class KosuDur(Exception):
    """Girdi ya da biçim sorunu: koşu durur; hiçbir Δv hesaplanmamıştır."""


class IsaretSonrasiHata(Exception):
    """İşaretten sonra bir istisna: tek koşu kullanıldı; doğrudan nedeni düzeltilip --devam ile sürdürülür."""


class BicimHata(KosuDur):
    def __init__(self, ileti, kesif):
        super().__init__(ileti)
        self.kesif = kesif


# ---------------------------------------------------------------- yardımcılar
def sha256_dosya(yol):
    h = hashlib.sha256()
    with open(yol, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def sayi(x, n=2):
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "–"
    return f"{x:.{n}f}".replace(".", ",")


def aralik(L, U, n=2):
    return f"[{sayi(L, n)}, {sayi(U, n)}]"


def pencere(Y, genis=UC):
    """Epok penceresi ve okuma ızgarası [w0 − genis, min(T + genis, SON_GUN)]. genis = 15 (§2.3, §3) bütün telemetri
    kaynaklarında; MIC'de genis = 90 (Ek 1 E1.4)."""
    P = KS.pencere(Y)
    ilk = P["w0"] - dt.timedelta(days=genis)
    son = min(P["T"] + dt.timedelta(days=genis), SON_GUN)
    n = (son - ilk).days + 1
    i0, iH, iT = ((P[k] - ilk).days for k in ("w0", "H", "T"))
    return dict(Y=Y, w0=P["w0"], H=P["H"], T=P["T"], ilk=ilk, son=son, n=n, i0=i0, iH=iH, iT=iT, genis=genis,
                tau2=(iT - iH) / 365.25, tau3=(iH - i0) / 365.25)


def kaynak_penceresi(Y, kaynak, mic_dar=False):
    """Ek 1 E1.4: yalnız MIC kaynaklarında okuma aralığı [w0 − 90 g, T + 90 g]; mic_dar=True "MIC dar aralık"
    bilgi satırının [w0 − 15 g, T + 15 g] okumasıdır. Telemetri ve 10MIN'de aralık değişmez."""
    return pencere(Y, MIC_GENIS if (kaynak == "MIC" and not mic_dar) else UC)


def seri_tohumu(kod, Y, j):
    return int(hashlib.sha256(f"{kod}|{Y}|{j}".encode("utf-8")).hexdigest()[:16], 16) ^ TOHUM


def kanonik_sira(yps):
    return sorted(yps, key=lambda r: f"{r['kod']}|{r['Y']}\n")


# ---------------------------------------------------------------- okuma (§2.3, §5)
_JAN1 = {}


def _jan1(y):
    o = _JAN1.get(y)
    if o is None:
        o = _JAN1[y] = dt.date(y, 1, 1).toordinal()
    return o


def _desen(tok):
    if re.fullmatch(r"[+-]?\d+", tok):
        return "tam sayı"
    try:
        float(tok)
        return "ondalık"
    except ValueError:
        return "metin"


def kesif_satiri(no, alanlar, deger_deseni=True):
    """Biçim keşfi (§5): sütun 3 ve sonrası maskelenir. deger_deseni=False ise (okuma aralığı dışındaki ya da
    2024 ve sonrası satır, §2.3 ve §5) sütun 3 ve sonrasının tür deseni de hesaplanmaz (ayrıştırma yok)."""
    desen = [_desen(t) if (j < 2 or deger_deseni) else "denetlenmedi" for j, t in enumerate(alanlar)]
    return dict(satir=no, alan_sayisi=len(alanlar), desen=desen,
                sutun1=alanlar[0] if alanlar else None, sutun2=alanlar[1] if len(alanlar) > 1 else None,
                sonrasi=["***"] * max(0, len(alanlar) - 2))


def _deger(tok):
    """Değer sütununun ayrıştırılması; YALNIZ okuma aralığındaki satırlarda çağrılır (sınama bunu izler)."""
    return float(tok)


def oku_dosya(yol, araliklar, ad=None):
    """Bir veri dosyasını okur. araliklar: [(ilk_ordinal, son_ordinal)] kapalı. Dönüş: dict(gun -> değer listesi),
    sayaçlar, δ. Biçim hatasında BicimHata (KosuDur)."""
    ad = ad or os.path.basename(yol)
    say = dict(satir=0, baslik=0, bos=0, aralik_ici=0, aralik_disi=0, aralik_disi_bozuk=0, bozuk=0)
    gun = {}
    ondalik = -1
    ilk_sayisal = None
    ornek = []

    def dur(ileti, no, alanlar, deger_deseni=True):
        k = dict(dosya=ad, ileti=ileti, **kesif_satiri(no, alanlar, deger_deseni))
        k["ilk_5_sayisal"] = ornek[:5]
        raise BicimHata(f"{ad}: {ileti} (satır {no})", k)
    try:
        f = gzip.open(yol, "rt", encoding="latin-1", newline=None)
        f.read(0)
        satirlar = f
        for no, s in enumerate(satirlar, 1):
            say["satir"] += 1
            alanlar = s.split()
            if not alanlar:
                say["bos"] += 1
                continue
            try:
                y = float(alanlar[0]) if len(alanlar) >= 1 else None
                gg = float(alanlar[1]) if len(alanlar) >= 2 else None
            except ValueError:
                y = gg = None
            if y is None or gg is None or not (math.isfinite(y) and math.isfinite(gg)):
                if ilk_sayisal is None:
                    say["baslik"] += 1
                    continue
                dur("ilk sayısal satırdan sonra sayısal olmayan satır", no, alanlar)
            if ilk_sayisal is None:
                ilk_sayisal = no
            # 2024 ve sonrası (ve yılı geçersiz) satırların sütun 3+ deseni bile hesaplanmaz (§2.3)
            erken = y < 2024
            gtam = math.floor(gg)
            if gtam == 0:
                dur("⌊gün⌋ = 0", no, alanlar, erken)
            if not y.is_integer() or not (1960 <= y <= 2026):
                dur("geçersiz yıl", no, alanlar, erken and y >= 1960)
            yi = int(y)
            yg = 366 if (yi % 4 == 0 and (yi % 100 != 0 or yi % 400 == 0)) else 365
            if not (1 <= gtam <= yg):
                dur("geçersiz yılın günü", no, alanlar, erken)
            o = _jan1(yi) + gtam - 1
            ic = False
            for a, b in araliklar:
                if a <= o <= b:
                    ic = True
                    break
            if len(ornek) < 5:
                ornek.append(kesif_satiri(no, alanlar, ic and o <= SON_GUN.toordinal()))
            if not ic:
                say["aralik_disi"] += 1
                if len(alanlar) < 3:
                    say["aralik_disi_bozuk"] += 1
                continue
            say["aralik_ici"] += 1
            if len(alanlar) < 3:
                say["bozuk"] += 1
                continue
            try:
                v = _deger(alanlar[2])
            except ValueError:
                say["bozuk"] += 1
                continue
            if not math.isfinite(v) or abs(v) >= DEGER_UST:
                say["bozuk"] += 1
                continue
            t3 = alanlar[2]
            if "e" not in t3.lower():
                ondalik = max(ondalik, len(t3.split(".", 1)[1]) if "." in t3 else 0)
            gun.setdefault(o, []).append(v)
        f.close()
    except (OSError, EOFError, gzip.BadGzipFile, zlib.error) as e:
        raise BicimHata(f"{ad}: gzip okunamadı ({type(e).__name__})", dict(dosya=ad, ileti="gzip"))
    if say["aralik_ici"] and say["bozuk"] > BOZUK_PAY * say["aralik_ici"]:
        raise BicimHata(f"{ad}: okuma aralığında bozuk satır payı %1'i aşıyor ({say['bozuk']}/{say['aralik_ici']})",
                        dict(dosya=ad, ileti="bozuk pay", ilk_5_sayisal=ornek[:5]))
    delta = 10.0 ** (-ondalik) if ondalik >= 0 else None
    gunluk = {o: float(np.median(v)) for o, v in gun.items()}
    return dict(gunluk=gunluk, sayac=say, delta=delta)


def pencere_dizisi(gunluk, W):
    """Günlük değer sözlüğünden pencerenin okuma ızgarasına (n gün) x ve maske."""
    x = np.full(W["n"], np.nan)
    o0 = W["ilk"].toordinal()
    for o, v in gunluk.items():
        i = o - o0
        if 0 <= i < W["n"]:
            x[i] = v
    return x, ~np.isnan(x)


# ---------------------------------------------------------------- şartlar ve ölçü (§8)
def _uc_idx(maske, i):
    a, b = max(0, i - UC), min(len(maske), i + UC + 1)
    return np.nonzero(maske[a:b])[0] + a


def tele_sart(maske, W):
    """§8.1 şartları. Dönüş: (geçerli, neden)."""
    if not maske.any():
        return False, "kapsam yok"
    if (maske[W["i0"]:W["iH"]].sum() / (W["iH"] - W["i0"]) < DOLULUK or
            maske[W["iH"]:W["iT"]].sum() / (W["iT"] - W["iH"]) < DOLULUK):
        return False, "doluluk"
    eks = np.concatenate(([0], (~maske).astype(np.int8), [0]))
    d = np.diff(eks)
    kos = np.nonzero(d == -1)[0] - np.nonzero(d == 1)[0]
    if len(kos) and kos.max() > BOSLUK:
        return False, "boşluk"
    if any(len(_uc_idx(maske, i)) < UC_MIN for i in (W["i0"], W["iH"], W["iT"])):
        return False, "uç değeri"
    return True, None


def _man_braket(g, i):
    a = g[g <= i]
    b = g[g >= i]
    if not len(a) or not len(b):
        return None
    a, b = int(a[-1]), int(b[0])
    if i - a > MAN_YAKIN or b - i > MAN_YAKIN:
        return None
    return a, b


def man_sart(maske, W):
    """§8.2 şartları (ölçüm günleri = maske). Maske MIC okuma ızgarasıdır: Ek 1 E1.4'e göre [w0 − 90 g, T + 90 g]
    (≤ 2023-10-16); "MIC dar aralık" bilgi satırında [w0 − 15 g, T + 15 g]. Izgara dışındaki ölçümler okunmaz."""
    g = np.nonzero(maske)[0]
    if not len(g):
        return False, "kapsam yok"
    if ((g >= W["i0"]) & (g < W["iH"])).sum() < MAN_N_TABAN or ((g >= W["iH"]) & (g < W["iT"])).sum() < MAN_N_YAKIN:
        return False, "doluluk"
    a = g[g <= W["i0"]]
    b = g[g >= W["iT"]]
    if not len(a) or not len(b):
        return False, "uç değeri"
    gg = g[(g >= a[-1]) & (g <= b[0])]
    if len(gg) > 1 and np.diff(gg).max() > MAN_ARALIK:
        return False, "boşluk"
    if any(_man_braket(g, i) is None for i in (W["i0"], W["iH"], W["iT"])):
        return False, "uç değeri"
    return True, None


def olc(X, maske, W, katman):
    """Ana ölçü (§8.1–8.2). X: (n,) ya da (M, n). Dönüş: (dv, v5) dizileri/sayıları; uç tanımsızsa None."""
    X = np.asarray(X, float)
    if katman == "tele":
        u = []
        for i in (W["i0"], W["iH"], W["iT"]):
            idx = _uc_idx(maske, i)
            if len(idx) < UC_MIN:
                return None
            u.append(np.median(X[..., idx], axis=-1))
    else:
        g = np.nonzero(maske)[0]
        u = []
        for i in (W["i0"], W["iH"], W["iT"]):
            br = _man_braket(g, i)
            if br is None:
                return None
            a, b = br
            if a == b:
                u.append(X[..., a])
            else:
                w = (i - a) / (b - a)
                u.append((1 - w) * X[..., a] + w * X[..., b])
    u0, uH, uT = u
    dv = (uT - uH) / W["tau2"] - (uH - u0) / W["tau3"]
    v5 = (uT - u0) / (W["tau2"] + W["tau3"])
    return dv, v5


def rho_seri(W):
    """ρ(t) = 5 mm/yıl · max(0, t − t_H), t = (gün − w0)/365,25, gün tarihinde (§10.3)."""
    t = (np.arange(W["n"]) - W["i0"]) / 365.25
    return PK_HIZ * np.maximum(0.0, t - (W["iH"] - W["i0"]) / 365.25)


def d_analitik(maske, W):
    g = np.nonzero(maske)[0]
    a, b = _man_braket(g, W["iH"])
    rh = 0.0 if a == b else PK_HIZ * (b - W["iH"]) * (W["iH"] - a) / ((b - a) * 365.25)
    return PK_HIZ - rh * (1 / W["tau2"] + 1 / W["tau3"])


# ---------------------------------------------------------------- doğrusal dolgu tanısı (§8.1; bilgi)
def dolgu(x, maske, W, delta):
    """Dönüş: (dolgulu, eğim_sıfır). Bir uç penceresinin bütün geçerli günleri, ≥ 15 ardışık geçerli günlük ve kendi
    EKK doğrusuna göre en büyük mutlak artığı ≤ 0,6·δ olan bir koşunun içindeyse dolgulu. Aday koşular: uç
    penceresinin geçerli günlerini içeren, uzunluğu max(15, geçerli gün sayısı) olan ardışık pencereler (kodlayıcı
    okuması)."""
    if delta is None:
        return False, False
    esik = DOLGU_K * delta + 1e-12
    n = len(maske)
    for i in (W["i0"], W["iH"], W["iT"]):
        V = _uc_idx(maske, i)
        if len(V) < UC_MIN or V[-1] - V[0] + 1 != len(V):
            continue
        s0 = V[0]
        while s0 > 0 and maske[s0 - 1]:
            s0 -= 1
        s1 = V[-1]
        while s1 < n - 1 and maske[s1 + 1]:
            s1 += 1
        L = max(DOLGU_KOSU, len(V))
        if s1 - s0 + 1 < L:
            continue
        for s in range(max(s0, V[-1] - L + 1), min(V[0], s1 - L + 1) + 1):
            t = np.arange(L, dtype=float)
            y = x[s:s + L]
            A = np.vstack([np.ones(L), t]).T
            c, *_ = np.linalg.lstsq(A, y, rcond=None)
            if np.abs(y - A @ c).max() <= esik:
                return True, abs(c[1]) < 1e-12
    return False, False


# ---------------------------------------------------------------- menteşe modeli (§8.4; bilgi)
def mentese(x, maske, W, d_tarihleri):
    g = np.nonzero(maske[W["i0"]:W["iT"]])[0] + W["i0"]
    t = (g - W["i0"]) / 365.25
    tH = (W["iH"] - W["i0"]) / 365.25
    sut = [np.ones_like(t), t, np.maximum(0, t - tH), np.sin(2 * np.pi * t), np.cos(2 * np.pi * t),
           np.sin(4 * np.pi * t), np.cos(4 * np.pi * t)]
    o0 = W["ilk"].toordinal()
    for d in d_tarihleri:
        i = d.toordinal() - o0
        if W["i0"] < i < W["iT"]:
            sut.append((g >= i).astype(float))
    X = np.vstack(sut).T
    y = x[g]

    def uydur(X, y):
        if len(y) < X.shape[1] or np.linalg.matrix_rank(X) < X.shape[1]:
            return None
        c, *_ = np.linalg.lstsq(X, y, rcond=None)
        return c
    c = uydur(X, y)
    if c is None:
        return None
    e = y - X @ c
    mad = np.median(np.abs(e - np.median(e)))
    if mad > 0:
        tut = np.abs(e - np.median(e)) <= 5 * 1.4826 * mad
        c = uydur(X[tut], y[tut])
        if c is None:
            return None
    return float(c[2])


# ---------------------------------------------------------------- olaylar
def hdr_olaylari(yol):
    out = []
    for r in csv.DictReader(open(yol, encoding="utf-8")):
        out.append(dict(kod=r["istasyon"], tur=r["tur"], a=dt.date.fromisoformat(r["aralik_bas"]),
                        b=dt.date.fromisoformat(r["aralik_son"]), tarihsiz=r["tarihsiz"] == "1",
                        dosya=r["dosya"], satir=int(r["satir"])))
    return out


def olay_dusurur(a, b, W):
    lo, hi = W["w0"] - dt.timedelta(days=K_TAMPON), W["T"] + dt.timedelta(days=UC)
    return a <= hi and b >= lo


def k_nedeni(kod, W, hdr):
    """§6: K_OLAY ([w0 − 30 g, T + 15 g]), K_SON (tarihten sonraki bütün pencereler), HDR K olayları."""
    for k, t, _ in KS.K_OLAY:
        if k == kod:
            d = dt.date.fromisoformat(t)
            if olay_dusurur(d, d, W) or ((k, t) in KS.K_SON and d <= W["T"]):
                return "K"
    for o in hdr:
        if o["kod"] == kod and o["tur"] == "K" and olay_dusurur(o["a"], o["b"], W):
            return "HDR"
    return None


def d_var(kod, W, hdr):
    for k, t in KS.D_OLAY:
        d = dt.date.fromisoformat(t)
        if k == kod and olay_dusurur(d, d, W):
            return True
    return any(o["kod"] == kod and o["tur"] == "D" and olay_dusurur(o["a"], o["b"], W) for o in hdr)


def d_tarihleri(kod, hdr):
    out = [dt.date.fromisoformat(t) for k, t in KS.D_OLAY if k == kod]
    out += [o["a"] for o in hdr if o["kod"] == kod and o["tur"] == "D" and not o["tarihsiz"]]
    return sorted(set(out))


# ---------------------------------------------------------------- girdi denetimi
def girdi_denetimi(a):
    T = TL.listeleri_yukle(json_yol=a.listeler)
    if T["json_sha256"] != LISTELER_JSON_SHA:
        raise KosuDur("tr10b_listeler.json sha256 uyuşmuyor")
    if sha256_dosya(a.hdr_csv) != HDR_CSV_SHA:
        raise KosuDur("tr10b_hdr_olaylar.csv sha256 uyuşmuyor")
    if sha256_dosya(a.hdr_baslik_csv) != HDR_BASLIK_CSV_SHA:
        raise KosuDur("tr10b_hdr_olaylar_baslik_katilmis.csv sha256 uyuşmuyor")
    if sha256_dosya(a.hdr_etki) != HDR_ETKI_SHA:
        raise KosuDur("tr10b_hdr_etki.json sha256 uyuşmuyor")
    veri = os.path.abspath(a.veri)
    if os.path.commonpath([veri, TL.DEPO]) == TL.DEPO:
        raise KosuDur("veri dizini depo içinde (ham veri depoya konmaz, §14 madde 7)")
    for y in (os.path.join(a.veri, ISARET_AD), os.path.join(a.isaret_depo, ISARET_AD), os.path.join(a.veri, ANLIK_AD)):
        if os.path.exists(y):
            raise KosuDur(f"işaret ya da anlık görüntü dosyası var ({y}): gerçek Δv daha önce hesaplandı ya da "
                          f"hesaplanmak üzereydi; tek koşu (işaret sonrası istisnada yalnız --devam)")
    for ad in ("tr10b_sonuc.json", "tr10b_sonuc.md"):
        if os.path.exists(os.path.join(a.cikti_dizin, ad)):
            raise KosuDur(f"çıktı zaten var: {ad}")
    tur_yol = os.path.join(a.cikti_dizin, f"tr10b_denetim_tur{a.duzeltme_turu}.json")
    if os.path.exists(tur_yol):
        raise KosuDur(f"düzeltme turu {a.duzeltme_turu} zaten koşuldu ({tur_yol}); sonraki tur verilmeli")
    man_b = open(a.manifest, "rb").read()
    man = json.loads(man_b.decode("utf-8"))
    izinli = {u for k, v in T["istasyon"].items() for t in KAYNAK_SIRA for u in v["dosya"][t]}
    kayit = {r["url"]: r for r in man["dosyalar"]}
    if set(kayit) != izinli:
        raise KosuDur("manifest URL kümesi aday listesinin 66 dosyasıyla aynı değil")
    basarisiz = [u for u, r in kayit.items() if r["durum"] != "tamam"]
    pay = len(basarisiz) / len(kayit)
    if pay > 0.05:
        raise KosuDur(f"başarısız indirme payı %5'i aşıyor ({len(basarisiz)}/{len(kayit)}); Δv hesaplanmadı")
    sha_ok = {}
    for u, r in kayit.items():
        if r["durum"] != "tamam":
            continue
        yol = os.path.join(a.veri, r["yerel"])
        if not os.path.exists(yol) or sha256_dosya(yol) != r["sha256"]:
            raise KosuDur(f"veri dosyası sha256 manifestle uyuşmuyor: {r['yerel']}")
        sha_ok[u] = r["sha256"]
    return T, man, hashlib.sha256(man_b).hexdigest(), kayit, basarisiz, pay


# ---------------------------------------------------------------- okuma ve değerlendirme
def oku_hepsi(T, kayit, veri, belirsiz):
    """B listesindeki her istasyonun her kaynağını, istasyonun o kaynak türündeki okuma aralıklarının birleşimiyle
    okur (telemetri ve 10MIN: [w0 − 15 g, T + 15 g]; MIC: [w0 − 90 g, T + 90 g], Ek 1 E1.4; hepsi ≤ 2023-10-16)."""
    ist = T["istasyon"]
    pencereler = {}
    for k, y in T["listeler"]["B"]:
        pencereler.setdefault(k, []).append(y)
    veri_ist, sayac, dosya_durum = {}, {}, {}
    for k in sorted(pencereler):
        for t in KAYNAK_SIRA:
            ar = [(kaynak_penceresi(y, t)["ilk"].toordinal(), kaynak_penceresi(y, t)["son"].toordinal())
                  for y in sorted(pencereler[k])]
            if max(b for _, b in ar) > SON_GUN.toordinal():
                raise KosuDur("okuma aralığı 2023-10-16'yı aşıyor")
            for u in ist[k]["dosya"][t]:
                r = kayit[u]
                if r["durum"] != "tamam":
                    dosya_durum[u] = "indirilemedi"
                    continue
                if u in belirsiz:
                    dosya_durum[u] = "biçim belirsiz"
                    continue
                o = oku_dosya(os.path.join(veri, r["yerel"]), ar, ad=r["yerel"])
                veri_ist.setdefault(k, {})[t] = o
                sayac[r["yerel"]] = o["sayac"]
                dosya_durum[u] = "okundu"
    return veri_ist, sayac, dosya_durum, pencereler


def istasyon_penceresi(k, Y, T, veri_ist, dosya_durum, hdr, hdr_uygula=True, mic_dar=False):
    """Bir istasyon-pencerenin kaynağı ve geçerliliği. Değer kullanılmaz, yalnız gün varlığı (§8.3).
    mic_dar=True: "MIC dar aralık" bilgi satırı (Ek 1 E1.4)."""
    W0 = pencere(Y)
    ist = T["istasyon"][k]
    kn = k_nedeni(k, W0, hdr if hdr_uygula else [])
    if kn == "K" or (kn == "HDR" and hdr_uygula):
        return dict(kod=k, Y=Y, gecerli=False, neden=kn)
    neden = None
    for t in KAYNAK_SIRA:
        if not ist["dosya"][t]:
            continue
        o = veri_ist.get(k, {}).get(t)
        if o is None:
            continue
        W = kaynak_penceresi(Y, t, mic_dar)
        x, m = pencere_dizisi(o["gunluk"], W)
        katman = "man" if t == "MIC" else "tele"
        ok, ne = (man_sart if katman == "man" else tele_sart)(m, W)
        if ok:
            return dict(kod=k, Y=Y, gecerli=True, kaynak=t, katman=katman, x=x, maske=m, W=W, delta=o["delta"],
                        site=ist["site"], kesim=ist["kesim"], ilk=ist["ilk"])
        if neden is None and ne != "kapsam yok":
            neden = ne
    if neden is None:
        durumlar = {dosya_durum.get(u) for t in KAYNAK_SIRA for u in ist["dosya"][t]}
        if durumlar and durumlar <= {"indirilemedi"}:
            neden = "indirilemedi"
        elif durumlar and durumlar <= {"indirilemedi", "biçim belirsiz"}:
            neden = "biçim belirsiz"
        else:
            neden = "kapsam yok"
    return dict(kod=k, Y=Y, gecerli=False, neden=neden)


def temsilci(sws):
    """§9.1: aynı yer ve epokta tek temsilci: önce telemetri, sonra en erken ilk gözlem, sonra kod."""
    sp = {}
    for s in sorted(sws, key=lambda s: (s["katman"] != "tele", s["ilk"], s["kod"])):
        sp.setdefault((s["site"], s["Y"]), s)
    return kanonik_sira(sp.values())


def yer_kumeleri(siteler):
    S = sorted(siteler)
    xy = {s: tuple(map(float, s.split(","))) for s in S}
    ata = {s: s for s in S}

    def kok(x):
        while ata[x] != x:
            x = ata[x]
        return x
    for i, a in enumerate(S):
        for b in S[i + 1:]:
            if T2.mesafe_az(*xy[a], *xy[b])[0] <= 3.0:
                ata[kok(a)] = kok(b)
    return len({kok(s) for s in S})


# ---------------------------------------------------------------- yapay seriler ve dosya yolu
def yapay_rw(n, rng, M=None):
    sh = (n,) if M is None else (M, n)
    return (B_GEN * math.sqrt(DT_YIL) * np.cumsum(rng.standard_normal(sh), axis=-1)
            + B_BEYAZ * rng.standard_normal(sh))


def dosya_yaz(yol, W, x, maske, kaynak, satir144=False, rng=None):
    """Yapay seriyi kaynak türünün dosya biçiminde gzip'li metin olarak yazar (DAY/MIC: günde bir satır; 10MIN: günde
    bir satır, öğlen; satir144: günde 144 satır, değere ±0,01 mm beyaz gürültü)."""
    s = io.StringIO()
    o0 = W["ilk"].toordinal()
    for i in np.nonzero(maske)[0]:
        d = dt.date.fromordinal(o0 + int(i))
        j = d.timetuple().tm_yday
        if kaynak == "10MIN" and satir144:
            ek = 0.01 * rng.standard_normal(144)
            for q in range(144):
                s.write(f"{d.year} {j + q / 144:.6f} {x[i] + ek[q]:.6f}\n")
        elif kaynak == "10MIN":
            s.write(f"{d.year} {j + 0.5:.4f} {x[i]:.6f}\n")
        else:
            s.write(f"{d.year} {j} {x[i]:.6f}\n")
    with gzip.open(yol, "wt", encoding="ascii") as f:
        f.write(s.getvalue())


def dosya_yolundan(yol, W, kaynak, rho=False):
    """Dosyayı koşu kodunun okuma yolundan geçirir; günlük değere (10MIN'de günlük medyandan sonra) isteğe bağlı ρ
    ekler; şartları denetler ve Δv'yi verir."""
    o = oku_dosya(yol, [(W["ilk"].toordinal(), W["son"].toordinal())])
    x, m = pencere_dizisi(o["gunluk"], W)
    if rho:
        x = x + rho_seri(W)
    katman = "man" if kaynak == "MIC" else "tele"
    ok, ne = (man_sart if katman == "man" else tele_sart)(m, W)
    r = olc(x, m, W, katman) if ok else None
    return (None if r is None else float(r[0])), m


# ---------------------------------------------------------------- kod denetimleri (§10.2)
def denetim_a(yps, gecici):
    out = dict(tam=[], maske_en_buyuk=0.0, elle_en_buyuk=0.0, a3=[], a4=[])
    # x(t)'nin zaman başlangıcı okuma aralığının başıdır (SAYIM denetim_on; §10.2.1'deki 0,00045 değeri bu
    # başlangıçla doğrulandı). Başlangıç w0 alınırsa mevsim terimlerinin evresi değişir ve doğru kod tam maskede
    # 0,0029–0,0096 hata verir (kodlayıcı okuması).
    for Y in sorted({r["Y"] for r in yps} | {1973, 1978, 1998, 2003, 2008, 2013, 2018}):
        W = pencere(Y)
        t = np.arange(W["n"]) / 365.25
        tH = W["iH"] / 365.25
        g = np.arange(W["n"])
        dv0 = 4.0 - 3.0 / W["tau3"]
        m1 = np.ones(W["n"], bool)
        for mevsim in (True, False):
            x = (3 + 7 * t + 4 * np.maximum(0, t - tH) + 3.0 * (g >= W["iH"] - 200)
                 + ((2 * np.sin(2 * np.pi * t + 1) + 0.7 * np.cos(4 * np.pi * t)) if mevsim else 0))
            out["tam"].append(dict(Y=Y, mevsim=mevsim, hata=abs(float(olc(x, m1, W, "tele")[0]) - dv0)))
        # (a3) medyan denetimi, dosya yolundan
        x = np.full(W["n"], 3.0)
        x[W["iT"]] = 503.0
        yol = os.path.join(gecici, f"a3_{Y}.day.gz")
        dosya_yaz(yol, W, x, m1, "DAY")
        out["a3"].append(dict(Y=Y, hata=abs(dosya_yolundan(yol, W, "DAY")[0])))
        # (a4) gün kayması denetimi
        for kay, beklenen in ((0, -10 / W["tau3"]), (1, 10 / W["tau2"])):
            x = 10.0 * (g >= W["iH"] + kay)
            yol = os.path.join(gecici, f"a4_{Y}_{kay}.day.gz")
            dosya_yaz(yol, W, x, m1, "DAY")
            out["a4"].append(dict(Y=Y, kayma=kay, hata=abs(dosya_yolundan(yol, W, "DAY")[0] - beklenen)))
    for r in yps:
        W = r["W"]
        t = np.arange(W["n"]) / 365.25
        tH = W["iH"] / 365.25
        g = np.arange(W["n"])
        if r["katman"] == "tele":
            x = (3 + 7 * t + 4 * np.maximum(0, t - tH) + 2 * np.sin(2 * np.pi * t + 1) + 0.7 * np.cos(4 * np.pi * t)
                 + 3.0 * (g >= W["iH"] - 200))
            h = abs(float(olc(x, r["maske"], W, "tele")[0]) - (4.0 - 3.0 / W["tau3"]))
            out["maske_en_buyuk"] = max(out["maske_en_buyuk"], h)
        else:
            h = abs(float(olc(3 + 7 * t, r["maske"], W, "man")[0]))
            out["elle_en_buyuk"] = max(out["elle_en_buyuk"], h)
    out["tam_en_buyuk"] = max(x["hata"] for x in out["tam"])
    out["a3_en_buyuk"] = max(x["hata"] for x in out["a3"])
    out["a4_en_buyuk"] = max(x["hata"] for x in out["a4"])
    out["gecti"] = dict(tam=out["tam_en_buyuk"] <= A_TAM, maske=out["maske_en_buyuk"] <= A_MASKE,
                        elle=out["elle_en_buyuk"] <= A_ELLE, a3=out["a3_en_buyuk"] <= A_3,
                        a4=out["a4_en_buyuk"] <= A_4)
    return out


def denetim_b_c(yps, gecici):
    """(b) uçtan uca ölçek, 144 satırlık 10MIN denetimi ve (c-yapay) pozitif kontrol."""
    n = len(yps)
    R = math.ceil(B_N_PAY / n)
    pay, f144, cy = [], [], []
    for r in kanonik_sira(yps):
        W = r["W"]
        for j in range(R):
            rng = np.random.default_rng(seri_tohumu(r["kod"], r["Y"], j))
            x = yapay_rw(W["n"], rng)
            yol = os.path.join(gecici, f"b_{r['kod']}_{r['Y']}_{j}.gz")
            dosya_yaz(yol, W, x, r["maske"], r["kaynak"])
            dv, m = dosya_yolundan(yol, W, r["kaynak"])
            if dv is None or not np.array_equal(m, r["maske"]):
                raise KosuDur(f"(b) yapay seri maskeyi korumadı: {r['kod']}|{r['Y']}|{j}")
            pay.append(abs(dv))
            if j == 0:
                dv1, _ = dosya_yolundan(yol, W, r["kaynak"], rho=True)
                rec = dict(kod=r["kod"], Y=r["Y"], katman=r["katman"], d=dv1 - dv)
                if r["katman"] == "man":
                    rec["d_analitik"] = d_analitik(r["maske"], W)
                cy.append(rec)
                if r["kaynak"] == "10MIN":
                    yol2 = os.path.join(gecici, f"b144_{r['kod']}_{r['Y']}.gz")
                    dosya_yaz(yol2, W, x, r["maske"], "10MIN", satir144=True,
                              rng=np.random.default_rng(seri_tohumu(r["kod"], r["Y"], "144")))
                    dv144, _ = dosya_yolundan(yol2, W, "10MIN")
                    f144.append(dict(kod=r["kod"], Y=r["Y"], fark=abs(dv144 - dv)))
            os.remove(yol)
    if not f144:
        # gerçek kümede 10MIN yer-penceresi yoksa: 2013 tam maskeli yapay pencere (kodlayıcı okuması)
        W = pencere(2013)
        m = np.ones(W["n"], bool)
        x = yapay_rw(W["n"], np.random.default_rng(seri_tohumu("YAPAY", 2013, "144")))
        y1, y2 = os.path.join(gecici, "f1.gz"), os.path.join(gecici, "f2.gz")
        dosya_yaz(y1, W, x, m, "10MIN")
        dosya_yaz(y2, W, x, m, "10MIN", satir144=True, rng=np.random.default_rng(1))
        f144.append(dict(kod="YAPAY", Y=2013, fark=abs(dosya_yolundan(y2, W, "10MIN")[0] -
                                                        dosya_yolundan(y1, W, "10MIN")[0])))
    q_pay = float(np.quantile(pay, 0.95, method="linear"))
    rng = np.random.default_rng(TOHUM + 1)
    payda = []
    for r in kanonik_sira(yps):
        X = yapay_rw(r["W"]["n"], rng, B_M)
        payda.append(np.abs(olc(X, r["maske"], r["W"], r["katman"])[0]))
    q_payda = float(np.quantile(np.concatenate(payda), 0.95, method="linear"))
    # bilgi: tam maskeli payda (SAYIM tanımı); yer-pencere başına ⌈20000/n⌉ çekiliş, kendi epoğunun ızgarası
    rng = np.random.default_rng(TOHUM + 2)
    tam = []
    for r in kanonik_sira(yps):
        W = r["W"]
        X = yapay_rw(W["n"], rng, math.ceil(B_TAM_N / n))
        tam.append(np.abs(olc(X, np.ones(W["n"], bool), W, "tele")[0]))
    q_tam = float(np.quantile(np.concatenate(tam), 0.95, method="linear"))
    oran = q_pay / q_payda
    tele_d = [c["d"] for c in cy if c["katman"] == "tele"]
    man_s = [abs(c["d"] - c["d_analitik"]) for c in cy if c["katman"] == "man"]
    c_out = pk_ozet(tele_d, man_s)
    b_out = dict(n=n, R=R, pay_N=len(pay), q95_pay=q_pay, q95_payda=q_payda, oran=oran, gecti=B_ORAN[0] <= oran <= B_ORAN[1],
                 bilgi_tam_maske_payda=q_tam, bilgi_oran_tam=q_pay / q_tam)
    f_out = dict(yer_pencere=len(f144), en_buyuk_fark=max(x["fark"] for x in f144),
                 gecti=max(x["fark"] for x in f144) <= F144_ESIK, ayrinti=f144)
    return b_out, f_out, c_out


def pk_ozet(tele_d, man_s):
    """§10.3 geçme şartları; yalnız d istatistikleri (Δv_özgün yazılmaz)."""
    o = dict(tele_N=len(tele_d), man_N=len(man_s))
    if tele_d:
        o.update(tele_medyan=float(np.median(tele_d)), tele_en_kucuk=float(min(tele_d)),
                 tele_en_buyuk=float(max(tele_d)))
        s1 = all(PK_TELE[0] <= d <= PK_TELE[1] for d in tele_d)
        s2 = PK_MEDYAN[0] <= o["tele_medyan"] <= PK_MEDYAN[1]
    else:
        s1 = s2 = True
    if man_s:
        o["man_en_buyuk_sapma"] = float(max(man_s))
        s3 = o["man_en_buyuk_sapma"] <= PK_ELLE
    else:
        s3 = True
    o.update(sart1=s1, sart2=s2, sart3=s3, gecti=s1 and s2 and s3)
    return o


def pk_gercek(yps):
    """§10.3: ilk ⌊n/2⌋ yer-pencere (sha256(KOD|Y) artan); yalnız d yazılır."""
    sec = sorted(yps, key=lambda r: hashlib.sha256(f"{r['kod']}|{r['Y']}".encode("utf-8")).hexdigest())[:len(yps) // 2]
    tele_d, man_s = [], []
    for r in sec:
        W = r["W"]
        d0 = olc(r["x"], r["maske"], W, r["katman"])
        d1 = olc(r["x"] + rho_seri(W), r["maske"], W, r["katman"])
        d = float(d1[0] - d0[0])
        if r["katman"] == "tele":
            tele_d.append(d)
        else:
            man_s.append(abs(d - d_analitik(r["maske"], W)))
        del d0, d1
    o = pk_ozet(tele_d, man_s)
    o["secili"] = len(sec)
    return o


# ---------------------------------------------------------------- istatistik ve bootstrap (§9.3, §10.4, §11)
def q(v, p):
    return float(np.quantile(v, p, method="linear"))


def istatistik(dv, v5, r_mask=None):
    """Bir havuzun nicelikleri. Tanımsız olanlar NaN."""
    a = np.abs(dv)
    o = {}
    if len(a) == 0:
        return {}
    o["q50"], o["q95"], o["q99"] = q(a, .5), q(a, .95), q(a, .99)
    o["isaretli_medyan"] = float(np.median(dv))
    o["hizlanan_pay"] = float(np.mean(dv > 0))
    o["yavaslayan_pay"] = float(np.mean(dv < 0))
    o["kappa"] = o["q95"] / o["q50"] if o["q50"] > 0 else np.nan
    o["q99_q95"] = o["q99"] / o["q95"] if o["q95"] > 0 else np.nan
    o["b_yildiz"] = o["q95"] / C1
    s = v5 >= SUNEN_V5
    if s.any():
        r = np.abs(dv[s] / v5[s]) * 100
        o["r50"], o["r95"], o["r99"] = q(r, .5), q(r, .95), q(r, .99)
        o["P_r"] = float(np.mean(np.abs(dv[s] / v5[s]) >= CH_R))
    else:
        o["r50"] = o["r95"] = o["r99"] = o["P_r"] = np.nan
    o["sunen_N"] = int(s.sum())
    o["P_v"] = float(np.mean(a >= CH_V))
    return o


ANAHTAR = ("q50", "q95", "q99", "isaretli_medyan", "hizlanan_pay", "yavaslayan_pay", "kappa", "q99_q95", "b_yildiz",
           "r50", "r95", "r99", "P_r", "P_v")


def bootstrap(yps, birim, rho_N0=None):
    """birim: 'kesim' (blok) ya da 'site'. Yeni default_rng(20261112). Çekiliş dizisi (B, K); birimler ad sırasında.
    rho_N0: {yp anahtarı: N0 |Δv| dizisi} verilirse ρ_R aynı yinelemelerle hesaplanır."""
    birimler = sorted({r[birim] for r in yps})
    K = len(birimler)
    rng = np.random.default_rng(TOHUM)
    cek = rng.integers(0, K, size=(B_BOOT, K))
    uye = {b: [i for i, r in enumerate(yps) if r[birim] == b] for b in birimler}
    dv = np.array([r["dv"] for r in yps])
    v5 = np.array([r["v5"] for r in yps])
    sonuc = {k: np.full(B_BOOT, np.nan) for k in ANAHTAR}
    sonuc["rho_R"] = np.full(B_BOOT, np.nan)
    Ridx = [i for i, r in enumerate(yps) if rho_N0 is not None and (r["kod"], r["Y"]) in rho_N0]
    for it in range(B_BOOT):
        say = np.zeros(len(yps), int)
        for bi in cek[it]:
            say[uye[birimler[bi]]] += 1
        sec = np.repeat(np.arange(len(yps)), say)
        st = istatistik(dv[sec], v5[sec])
        for k in ANAHTAR:
            sonuc[k][it] = st.get(k, np.nan)
        if Ridx:
            c = say[Ridx]
            if c.sum() > 0:
                pay = q(np.repeat(np.abs(dv[Ridx]), c), .95)
                payda = q(np.concatenate([np.repeat(rho_N0[(yps[i]["kod"], yps[i]["Y"])][None, :], cc, axis=0).ravel()
                                          for i, cc in zip(Ridx, c) if cc > 0]), .95)
                sonuc["rho_R"][it] = pay / payda
    out = {}
    for k, v in sonuc.items():
        tanimsiz = int(np.isnan(v).sum())
        if tanimsiz > 0.10 * B_BOOT:
            out[k] = dict(L=None, U=None, tanimsiz=tanimsiz, guc_yok=True)
        else:
            w = v[~np.isnan(v)]
            out[k] = dict(L=q(w, .05) if len(w) else None, U=q(w, .95) if len(w) else None, tanimsiz=tanimsiz,
                          guc_yok=False)
    return K, out


def n0_cekilisleri(R_yps):
    """README N0 beklentisi (§11 madde 9): (n, A) güç yasası gürültüsü, gerçek maske, yer-pencere başına 2000
    çekiliş, default_rng(20261112 + 3), kanonik sıra. pl_seri ile aynı süzgeç, FFT ile toplu evrişim."""
    rng = np.random.default_rng(TOHUM + 3)
    out = {}
    for r in kanonik_sira(R_yps):
        ust, A = README_TAB[r["kod"]]
        n = r["W"]["n"]
        h = np.ones(n)
        for k in range(1, n):
            h[k] = h[k - 1] * (k - 1 + ust / 2.0) / k
        w = rng.standard_normal((N0_M, n))
        L = 1 << (2 * n - 1).bit_length()
        y = np.fft.irfft(np.fft.rfft(w, L, axis=1) * np.fft.rfft(h, L), L, axis=1)[:, :n]
        y = A * DT_YIL ** (ust / 4.0) * y
        out[(r["kod"], r["Y"])] = np.abs(olc(y, r["maske"], r["W"], r["katman"])[0])
    return out


def satir(yps, ad, birim="kesim", rho_N0=None, zorla=False):
    """Bir çıktı satırı: nokta değerler ve aralıklar. Katman/döküm/bilgi satırlarında N < 20 → güç yok (aralık yok);
    ana satır ve A satırı (zorla=True) N ≥ 2'de her zaman aralık alır (kodlayıcı okuması)."""
    N = len(yps)
    S = len({r["site"] for r in yps})
    Kk = len({r["kesim"] for r in yps})
    o = dict(ad=ad, N=N, S=S, K=Kk)
    if N == 0:
        o["bos"] = True
        return o
    dv = np.array([r["dv"] for r in yps])
    v5 = np.array([r["v5"] for r in yps])
    o["nokta"] = istatistik(dv, v5)
    if N < N_GUC and not (zorla and N >= 2):
        o["guc_yok"] = True
        return o
    if birim == "kesim" and Kk < K_MIN:
        # §9.3: bloklu aralık yalnız K ≥ 4 blokta; K ≤ 3'te yer bootstrap'ının aralığı bilgi olarak verilir
        birim = "site"
        o["blok_yetersiz"] = True
    Kb, ar = bootstrap(yps, birim, rho_N0)
    o["aralik"] = ar
    o["aralik_birim"] = birim
    o["aralik_K"] = Kb
    return o


# ---------------------------------------------------------------- hüküm kalıpları (§12)
def b_etiketi(L, U):
    if L / C1 > ETIKET_UST:
        return "taban, README'nin n = 2 istasyonlarının genlik aralığından büyük"
    if U / C1 < ETIKET_ALT:
        return "taban, README'nin n = 2 istasyonlarının genlik aralığından küçük"
    return "taban, README'nin n = 2 istasyonlarının genlik aralığında"


def rho_okuma(L, U):
    if U < 1:
        return "küçük"
    if L > 1:
        return "büyük"
    return "uyumlu"


def ch_okuma(L, U):
    if U < 0.05:
        return "tabanın üstünde"
    if L > 0.05:
        return "tabanın içinde"
    return "sınırda"


# ---------------------------------------------------------------- ana koşu
# Yapı (kod incelemesi, risk 4): gerçek Δv'ye bağlı olmayan HER ŞEY işaretten önce koşar (hazirla). İşaretten önce
# aynı ölçü/hüküm/çıktı kodu, gerçek gün maskeleri ve yapay değerlerle bir kez kuru koşulur (kuru prova); bir istisna
# orada çıkarsa işaret yazılmaz. İşaretle aynı anda okuma sonucu (durum D) veri dizinine (depo dışı) "x" kipinde
# yazılır ve sha256'sı işarete girer; işaretten sonra bir istisna olursa doğrudan nedeni düzeltilir ve
# `--devam` ile ham veriye ikinci kez bakılmadan bu anlık görüntüden sürdürülür (§14 madde 6).
def sw_kur(T, veri_ist, dosya_durum, hdr, **kw):
    return {(k, Y): istasyon_penceresi(k, Y, T, veri_ist, dosya_durum, hdr, **kw) for k, Y in T["listeler"]["B"]}


def yp_kur(liste, kaynak, suz=lambda s: True):
    return temsilci([kaynak[x] for x in liste if kaynak[x]["gecerli"] and suz(kaynak[x])])


def sayim(yps):
    return dict(yer=len({r["site"] for r in yps}), yer_pencere=len(yps), kesim=len({r["kesim"] for r in yps}),
                kaynak={t: sum(r["kaynak"] == t for r in yps) for t in KAYNAK_SIRA})


def hazirla(a, log):
    """İşaret öncesi: girdi denetimi, okuma, §6/§8 şartları, temsilci, kapı, dolgu tanısı, kod denetimleri (yapay),
    pozitif kontrol (gerçek veride; yalnız d), README N0 çekilişleri (yalnız maske). Gerçek Δv HESAPLANMAZ."""
    t0 = time.time()
    T, man, man_sha, kayit, basarisiz, pay = girdi_denetimi(a)
    hdr = hdr_olaylari(a.hdr_csv)
    hdr_b = hdr_olaylari(a.hdr_baslik_csv)
    belirsiz = set(x for x in (a.bicim_belirsiz or "").split(",") if x)
    if not belirsiz <= set(kayit):
        raise KosuDur(f"--bicim-belirsiz manifestte olmayan URL içeriyor: {sorted(belirsiz - set(kayit))}")
    etki_B = json.load(open(a.hdr_etki, encoding="utf-8"))["etki"]["B"]
    md_tam = open(TL.MD_YOL, "rb").read()
    girdi = dict(onkayit_sha256=TL.MD_SHA, onkayit_donmus_boy=TL.MD_DONMUS_BOY,
                 onkayit_tam_dosya_sha256=hashlib.sha256(md_tam).hexdigest(), onkayit_tam_boy=len(md_tam),
                 listeler_json_sha256=T["json_sha256"], hdr_csv_sha256=HDR_CSV_SHA,
                 hdr_baslik_csv_sha256=HDR_BASLIK_CSV_SHA, hdr_etki_sha256=HDR_ETKI_SHA,
                 manifest_veri_sha256=man_sha, kosu_kodu_sha256=sha256_dosya(os.path.abspath(__file__)),
                 yardimci_kod_sha256={os.path.basename(m.__file__): sha256_dosya(m.__file__) for m in (TL, KS, T2)},
                 liste_sha256=TL.LISTE_SHA,
                 veri_dosyalari_sha256={r["yerel"]: r.get("sha256") for r in kayit.values()})
    log(f"girdi denetimi tamam; indirme başarısız {len(basarisiz)} (pay {pay:.3f})")

    # 1) okuma
    veri_ist, sayac, dosya_durum, pencereler = oku_hepsi(T, kayit, a.veri, belirsiz)
    oku_top = {k: sum(s[k] for s in sayac.values()) for k in
               ("satir", "baslik", "bos", "aralik_ici", "aralik_disi", "aralik_disi_bozuk", "bozuk")}
    log(f"okuma bitti: {len(sayac)} dosya; {oku_top}")

    # 2) istasyon-pencereler: bağlayıcı küme ve bilgi satırlarının değişkeleri (yalnız gün varlığı)
    sw = sw_kur(T, veri_ist, dosya_durum, hdr)
    sw_hdrsiz = {x: (s if s.get("neden") != "HDR" else
                     istasyon_penceresi(x[0], x[1], T, veri_ist, dosya_durum, hdr, hdr_uygula=False))
                 for x, s in sw.items()}
    sw_baslik = sw_kur(T, veri_ist, dosya_durum, hdr_b)            # Ek 1 E1.3
    sw_micdar = sw_kur(T, veri_ist, dosya_durum, hdr, mic_dar=True)  # Ek 1 E1.4
    neden_say = {}
    for s in sw.values():
        nd = "geçerli" if s["gecerli"] else s["neden"]
        neden_say[nd] = neden_say.get(nd, 0) + 1
    L = T["listeler"]
    B_yp = yp_kur(L["B"], sw)
    A_yp = yp_kur(L["A"], sw)
    S_B, N_B = len({r["site"] for r in B_yp}), len(B_yp)
    K_B = len({r["kesim"] for r in B_yp})
    kapi = S_B >= KAPI_YER and N_B >= KAPI_YP
    S_A, N_A = len({r["site"] for r in A_yp}), len(A_yp)
    kapi_A = S_A >= KAPI_YER and N_A >= KAPI_YP
    kume = yer_kumeleri({r["site"] for r in B_yp})
    # dolgu tanısı (yalnız işaret; değer yazılmaz)
    for r in B_yp + A_yp:
        if "dolgulu" not in r:
            r["dolgulu"], r["dolgu_egim0"] = (dolgu(r["x"], r["maske"], r["W"], r["delta"])
                                             if r["katman"] == "tele" else (False, False))
    dolgu_tab = {}
    for r in B_yp:
        if r["dolgulu"]:
            kk = f"{r['kaynak']}|{r['Y']}"
            dolgu_tab[kk] = dolgu_tab.get(kk, 0) + 1
    gecerli_sw = [s for s in sw.values() if s["gecerli"]]
    kapi_out = dict(yer=S_B, yer_pencere=N_B, kesim_K=K_B, gecti=kapi, yer_kumesi=kume,
                    istasyon_bilgi=len({s["kod"] for s in gecerli_sw}), istasyon_pencere_bilgi=len(gecerli_sw),
                    dusme_nedenleri=neden_say, dolgulu=sum(r["dolgulu"] for r in B_yp),
                    dolgulu_egim_sifir=sum(r["dolgulu"] and r["dolgu_egim0"] for r in B_yp),
                    dolgulu_kaynak_epok=dolgu_tab,
                    kaynak_dokumu={t: sum(r["kaynak"] == t for r in B_yp) for t in KAYNAK_SIRA},
                    A=dict(yer=S_A, yer_pencere=N_A, gecti=kapi_A),
                    bilgi_sayimlari={"başlık katılmış (Ek 1 E1.3)": sayim(yp_kur(L["B"], sw_baslik)),
                                     "MIC dar aralık (Ek 1 E1.4)": sayim(yp_kur(L["B"], sw_micdar)),
                                     "HDR olayları uygulanmadan": sayim(yp_kur(L["B"], sw_hdrsiz))})
    log(f"veri kapısı: yer {S_B}, yer-pencere {N_B}, K {K_B}; {'geçti' if kapi else 'GEÇMEDİ'}; nedenler {neden_say}")

    sonuc = dict(girdi=girdi, okuma=dict(toplam=oku_top, dosya=sayac, dosya_durum=dosya_durum,
                                         bicim_belirsiz=sorted(belirsiz)),
                 manifest=dict(basarisiz=basarisiz, pay=pay), kapi=kapi_out, duzeltme_turu=a.duzeltme_turu,
                 hdr_sayac=dict(K_dusen_B=len(etki_B["K_dusen"]), K_dusen_creep_event_B=etki_B["K_dusen_creep_event"],
                                not_="§6.4 madde 4: HDR adımında (veri öncesi, U kapsamı) K olayıyla düşen B "
                                     "istasyon-pencerelerinden notunda 'creep'/'event' geçenler; bilgi"))

    # 3) kod denetimi (yapay) ve pozitif kontrol (gerçek, yalnız d)
    import tempfile
    kod_hata = None
    if N_B >= 2:
        with tempfile.TemporaryDirectory() as gecici:
            da = denetim_a(B_yp, gecici)
            db, df, dc = denetim_b_c(B_yp, gecici)
        sonuc["denetim"] = dict(a=da, b=db, f144=df, c_yapay=dc)
        log(f"(a) {da['gecti']}; (b) oran {db['oran']:.3f}; 144 satır {df['en_buyuk_fark']:.5f}; (c-yapay) {dc['gecti']}")
        for ad, ok, deger, esik in (
                ("(a) tam maske", da["gecti"]["tam"], da["tam_en_buyuk"], A_TAM),
                ("(a) gerçek maske", da["gecti"]["maske"], da["maske_en_buyuk"], A_MASKE),
                ("(a) elle katman", da["gecti"]["elle"], da["elle_en_buyuk"], A_ELLE),
                ("(a3)", da["gecti"]["a3"], da["a3_en_buyuk"], A_3),
                ("(a4)", da["gecti"]["a4"], da["a4_en_buyuk"], A_4),
                ("(b)", db["gecti"], db["oran"], "[0,88, 1,12]"),
                ("144 satırlık 10MIN", df["gecti"], df["en_buyuk_fark"], F144_ESIK),
                ("(c-yapay)", dc["gecti"], dc.get("tele_medyan", dc.get("man_en_buyuk_sapma")), "§10.3")):
            if not ok and kod_hata is None:
                kod_hata = (ad, deger, esik)
        if kod_hata is None:
            pk = pk_gercek(B_yp)
            sonuc["denetim"]["c_gercek"] = pk
            log(f"(c-gerçek) seçili {pk['secili']}; geçti {pk['gecti']}")
            if not pk["gecti"]:
                kod_hata = ("(c-gerçek)", pk.get("tele_medyan", pk.get("man_en_buyuk_sapma")), "§10.3")
    else:
        sonuc["denetim"] = dict(yapilamadi=f"n = {N_B} < 2")
    R_yp = [r for r in B_yp if r["kod"] in README_TAB]
    N0 = n0_cekilisleri(R_yp) if (R_yp and kod_hata is None and N_B >= 2) else {}
    sonuc["sure_hazirlik_sn"] = time.time() - t0
    return dict(sonuc=sonuc, T=T, L=L, hdr=hdr, sw=dict(B=sw, hdrsiz=sw_hdrsiz, baslik=sw_baslik, micdar=sw_micdar),
                kapi=kapi, kapi_A=kapi_A, S_B=S_B, N_B=N_B, K_B=K_B, S_A=S_A, N_A=N_A, kume=kume, kod_hata=kod_hata,
                N0=N0, R_anahtar=sorted((r["kod"], r["Y"]) for r in R_yp))


def fmt_e(e):
    return sayi(e, 6) if isinstance(e, float) else str(e)


def kuyruklar(dolgu_pay, kume):
    """§12 ek kuyrukları (şart sağlanırsa, bu sırayla). §8.1 ve §10.1 bunları kapıdan bağımsız koyar."""
    k = ""
    if dolgu_pay is not None and dolgu_pay > 20:
        k += f" (yer-pencerelerin %{sayi(dolgu_pay, 0)}'inde uç değeri doğrusal dolgudan; Δv sıfıra yanlı olabilir)"
    if kume < 20:
        k += f" (≤ 3 km'de kümelenince {kume} yer kümesi)"
    return k


def olcu_kur(D, log):
    """İşaretten SONRA koşan kısım: gerçek Δv, satırlar, hüküm. Yalnız bellekte kurar (D["sonuc"]); dosya yazmaz.
    Kuru provada aynı işlev yapay değerli bir kopyayla çağrılır."""
    sonuc, L, hdr, V = D["sonuc"], D["L"], D["hdr"], D["sw"]
    S_B, N_B, K_B, S_A, N_A = D["S_B"], D["N_B"], D["K_B"], D["S_A"], D["N_A"]
    kapi, kapi_A, kume, N0 = D["kapi"], D["kapi_A"], D["kume"], D["N0"]
    sw = V["B"]
    for S in V.values():
        for s in S.values():
            if s["gecerli"] and "dv" not in s:
                d = olc(s["x"], s["maske"], s["W"], s["katman"])
                s["dv"], s["v5"] = float(d[0]), float(d[1])
    B_yp = yp_kur(L["B"], sw)
    A_yp = yp_kur(L["A"], sw)
    if (len(B_yp), len({r["site"] for r in B_yp})) != (N_B, S_B):
        raise KosuDur("iç tutarlılık: işaret sonrası B kümesi işaret öncesindekinden farklı")
    R_yp = [r for r in B_yp if r["kod"] in README_TAB]
    if sorted((r["kod"], r["Y"]) for r in R_yp) != D["R_anahtar"] or set(N0) != set(D["R_anahtar"]):
        raise KosuDur("iç tutarlılık: README alt kümesi R işaret öncesindekinden farklı")
    R_ok = len(R_yp) >= N_GUC
    blok_yeter = K_B >= K_MIN
    ana = satir(B_yp, "Ana (B)", "kesim" if blok_yeter else "site", rho_N0=N0, zorla=True)
    ana_yer = satir(B_yp, "Ana (B), yer bootstrap'ı", "site", rho_N0=N0, zorla=True)
    q95_N0_R = q(np.concatenate(list(N0.values())), .95) if N0 else None
    q95_R = q(np.abs([r["dv"] for r in R_yp]), .95) if R_yp else None
    rhoR = q95_R / q95_N0_R if R_yp else None
    R08 = [r for r in R_yp if r["Y"] >= 2008]
    N0_08 = {k: v for k, v in N0.items() if k[1] >= 2008}
    rho08 = (q(np.abs([r["dv"] for r in R08]), .95) / q(np.concatenate(list(N0_08.values())), .95)
             if R08 else None)
    rho08_satir = satir(R08, "README N0, T ≥ 2008", "kesim", rho_N0=N0_08) if R08 else dict(N=0)
    A_satir = satir(A_yp, "A satırı", "kesim" if len({r['kesim'] for r in A_yp}) >= K_MIN else "site", zorla=True)
    kesim_d = {kk: satir([r for r in B_yp if r["kesim"] == kk], f"kesim {kk}", "site")
               for kk in sorted({r["kesim"] for r in B_yp})}
    epok_d = {Y: satir([r for r in B_yp if r["Y"] == Y], f"epok {Y}", "kesim") for Y in sorted({r["Y"] for r in B_yp})}
    katman_d = {k: satir([r for r in B_yp if r["katman"] == k], f"katman {k}", "kesim") for k in ("tele", "man")}
    kaynak_d = {k: satir([r for r in B_yp if r["kaynak"] == k], f"kaynak {k}", "kesim") for k in KAYNAK_SIRA}
    Dsiz = [x for x in L["B"] if not d_var(x[0], pencere(x[1]), hdr)]
    bilgi = {
        "Parkfield dışı": satir([r for r in B_yp if r["kesim"] != "SAF_Parkfield"], "Parkfield dışı"),
        "yalnız T ≥ 2008": satir([r for r in B_yp if r["Y"] >= 2008], "T ≥ 2008"),
        "D olayları dışarıda": satir(yp_kur(Dsiz, sw), "D dışarıda"),
        "yalnız telemetri": satir(yp_kur(L["B"], sw, suz=lambda s: s["katman"] == "tele"), "yalnız telemetri"),
        "SAYIM R2 alt kümesi": satir(yp_kur(L["B_R2"], sw), "B_R2"),
        "HDR olayları uygulanmadan": satir(yp_kur(L["B"], V["hdrsiz"]), "HDR uygulanmadan"),
        "B1 geçmiş 5 y": satir(yp_kur(L["B1_gecmis5"], sw), "B1 geçmiş 5 y"),
        "dolgulu yer-pencereler dışarıda": satir([r for r in B_yp if not r["dolgulu"]], "dolgusuz"),
        "XDL2 dışarıda": satir(yp_kur(L["B"], sw, suz=lambda s: s["kod"] != "XDL2"), "XDL2 dışarıda"),
        "başlık katılmış (Ek 1 E1.3)": satir(yp_kur(L["B"], V["baslik"]), "başlık katılmış"),
        "MIC dar aralık (Ek 1 E1.4)": satir(yp_kur(L["B"], V["micdar"]), "MIC dar aralık"),
    }
    m_dv = []
    for r in B_yp:
        if r["katman"] == "tele":
            m = mentese(r["x"], r["maske"], r["W"], d_tarihleri(r["kod"], hdr))
            if m is not None:
                m_dv.append(abs(m))
    mentese_out = dict(N=len(m_dv), q50=q(m_dv, .5) if m_dv else None, q95=q(m_dv, .95) if m_dv else None,
                       rank_dusen=sum(1 for r in B_yp if r["katman"] == "tele") - len(m_dv))
    p_pkf = sum(r["kesim"] == "SAF_Parkfield" for r in B_yp) / N_B * 100
    p_0818 = sum(2008 <= r["Y"] <= 2018 for r in B_yp) / N_B * 100
    dolgu_pay = sonuc["kapi"]["dolgulu"] / N_B * 100
    rho_ar = ana.get("aralik", {}).get("rho_R")
    sonuc["olcu"] = dict(ana=ana, ana_yer_bootstrap=ana_yer, A=A_satir,
                         readme=dict(N_R=len(R_yp), q95_R=q95_R, q95_N0_R=q95_N0_R, rho_R=rhoR, rho_R_aralik=rho_ar,
                                     guc_yok=not R_ok, T2008=dict(N=len(R08), rho=rho08, satir=rho08_satir)),
                         kesim=kesim_d, epok=epok_d, katman=katman_d, kaynak=kaynak_d, bilgi=bilgi,
                         mentese=mentese_out, p_parkfield=p_pkf, p_2008_2018=p_0818, dolgulu_pay=dolgu_pay,
                         q99_notu="N < 300: bilgi" if N_B < N_Q99 else "")
    # hüküm
    nk = ana["nokta"]
    ar = ana.get("aralik", {})
    kapi_A_m = "geçer" if kapi_A else "altı"
    Aar = A_satir.get("aralik", {}).get("q95", {}) if A_satir.get("N") else {}
    A_q95 = A_satir.get("nokta", {}).get("q95")
    kuyruk = kuyruklar(dolgu_pay, kume)
    if not kapi:
        ar_q95 = ar.get("q95", {})
        ar_r = ar.get("r95", {})
        hukum = (f"TR-10b: veri yok (kural seti B: yer {S_B} / yer-pencere {N_B}; kapı ≥ 20 / ≥ 40). Bilgi satırı, "
                 f"kapı altı: |Δv| q50 {sayi(nk['q50'])}, q95 {sayi(nk['q95'])} {aralik(ar_q95.get('L'), ar_q95.get('U'))} "
                 f"mm/yıl (sünen katmanda hızın %{sayi(nk['r95'], 0)}'si {aralik(ar_r.get('L'), ar_r.get('U'), 0)}); "
                 f"bu satır bir hüküm değildir.{kuyruk}")
    elif not blok_yeter:
        ay = ana_yer.get("aralik", {}).get("q95", {})
        hukum = (f"TR-10b: blok yetersiz (K = {K_B}); etiket yok. Kural seti B: |Δv| q50 {sayi(nk['q50'])}, "
                 f"q95 {sayi(nk['q95'])} mm/yıl (yer bootstrap'ı aralığı {aralik(ay.get('L'), ay.get('U'))}, bilgi; "
                 f"sünen katmanda hızın %{sayi(nk['r95'], 0)}'si); README modeline göre ρ_R = {sayi(rhoR)} "
                 f"(nokta değer); yer {S_B}, yer-pencere {N_B}. Kural seti A: q95 {sayi(A_q95)} mm/yıl (yer {S_A}, "
                 f"yer-pencere {N_A}; kapı {kapi_A_m}).{kuyruk}")
        # §9.3: Chihshang satırı da blok sayısı şartına uyar: nokta değerler ve yer bootstrap'ı aralığı (bilgi)
        ay_ar = ana_yer.get("aralik", {})
        sonuc["olcu"]["chihshang"] = dict(P_r=nk["P_r"], P_v=nk["P_v"], P_r_aralik_yer=ay_ar.get("P_r"),
                                          P_v_aralik_yer=ay_ar.get("P_v"), not_="blok yetersiz: okuma yok, bilgi")
    else:
        qa = ar["q95"]
        # q95 her yinelemede tanımlıdır (her blokta ≥ 1 yer-pencere); savunma: tanımsızsa etiket konmaz
        et = b_etiketi(qa["L"], qa["U"]) if not qa["guc_yok"] else "etiket yok (q95 aralığı tanımsız)"
        if R_ok and rho_ar is not None and not rho_ar["guc_yok"]:
            rmet = (f"README modeline göre {rho_okuma(rho_ar['L'], rho_ar['U'])} (ρ_R = {sayi(rhoR)} "
                    f"{aralik(rho_ar['L'], rho_ar['U'])}, yer-pencere {len(R_yp)})")
        else:
            # N_R < 20 (§10.4) ya da ρ_R aralığı yinelemelerin > %10'unda tanımsız (§9.3): okuma yok, "güç yok"
            rmet = f"README modeline göre (ρ_R = {sayi(rhoR)}, yer-pencere {len(R_yp)}; güç yok)"
        ra95 = ar["r95"]
        hukum = (f"TR-10b: {et}; {rmet}. Kural seti B: Orta Kaliforniya sünme ölçerlerinde sakin 5 yıllık "
                 f"pencerelerde 2 yıllık sünme hızı değişimi |Δv|, yer-pencerelerin yarısında {sayi(nk['q50'])} "
                 f"mm/yıl'ı, %5'inde {sayi(nk['q95'])} {aralik(qa['L'], qa['U'])} mm/yıl'ı aşar (sünen katmanda "
                 f"hızın %{sayi(nk['r50'], 0)}'sini ve %{sayi(nk['r95'], 0)} {aralik(ra95['L'], ra95['U'], 0)}'sunu); "
                 f"yer {S_B}, yer-pencere {N_B}, kesim {K_B}; aralık fay kesimi bloklu bootstrap, yüzdelik, "
                 f"nominal %90 (5–6 blokla gerçek kapsama daha düşük). Kural seti A: q95 {sayi(A_q95)} "
                 f"{aralik(Aar.get('L'), Aar.get('U'))} mm/yıl (yer {S_A}, yer-pencere {N_A}; kapı {kapi_A_m})."
                 f"{kuyruk}")
        yanlis = (f"Orta Kaliforniya sünme ölçerlerinde, önceden tanımlı sakinlik kuralı B'yi geçen 5 yıllık "
                  f"pencerelerde 2 yıllık sünme hızı değişimi %5 sıklıkla {sayi(nk['q95'])} mm/yıl'ı (sünen "
                  f"ölçerlerde hızın %{sayi(nk['r95'], 0)}'ini) aşar. Bloklu üst sınır {sayi(qa['U'])} mm/yıl'dır "
                  f"(nominal %90). Yer-pencerelerin %{sayi(p_pkf, 0)}'i Parkfield'da, %{sayi(p_0818, 0)}'i "
                  f"2008–2018 epoklarındadır. Sakin pencere seçimi ve küçük örneklem bu değeri aşağı çeker. Bu "
                  f"yüzden {sayi(nk['q95'])}, koşulsuz yanlış alarm eşiğinin alt kestirimidir. {sayi(qa['U'])} "
                  f"mm/yıl'dan küçük bir değişim bu tür bir ölçerde tek başına olağandışı sayılmaz. Daha büyük bir "
                  f"değişimin olağandışı olduğu ise bu ölçümden çıkmaz.")
        pr = ar["P_r"]
        # P_r aralığı tanımsızsa (§9.3 "güç yok") okuma yapılmaz; kalıbın üç sözcüğünden biri uydurulmaz
        ch_ok = ch_okuma(pr["L"], pr["U"]) if not pr["guc_yok"] else "okunamaz (P_r aralığı: güç yok)"
        ch = (f"Bilgi: Chihshang 2003 iddiası (−8 mm/yıl, r = −0,43; bindirme fayı, farklı alet dönemleri) bu sakin "
              f"tabanda |r| ölçüsüyle {ch_ok} "
              f"(P_r = {sayi(nk['P_r'])} {aralik(pr['L'], pr['U'])}). Taban sakin pencerelerden ve küçük örneklemle "
              f"kestirildiği için 'üstünde' okuması koşulsuz tabana genellenemez. Pencere uzunluğu farkı ters "
              f"yönde, 'içinde' yönüne iter.")
        sonuc["olcu"]["yanlis_alarm_cumlesi"] = yanlis
        sonuc["olcu"]["chihshang_cumlesi"] = ch
        sonuc["olcu"]["chihshang"] = dict(P_r=nk["P_r"], P_r_aralik=pr, P_v=nk["P_v"], P_v_aralik=ar["P_v"])
        sonuc["olcu"]["etiket"] = et
        if R_ok and rho_ar is not None and not rho_ar["guc_yok"]:
            sonuc["olcu"]["readme"]["okuma"] = rho_okuma(rho_ar["L"], rho_ar["U"])
        kp = ar["kappa"]
        sonuc["olcu"]["kappa_okuma"] = ("kuyruk tek ölçekli Gauss'tan ağır (ölçek karışımı ya da basamaklı sünme)"
                                        if kp["L"] is not None and kp["L"] > KAPPA_GAUSS else "")
    sonuc["hukum"] = hukum
    log("ölçü kuruldu")
    return sonuc


def metinler(sonuc):
    return json.dumps(sonuc, ensure_ascii=False, indent=1, default=json_varsayilan) + "\n", md_yap(sonuc)


def yaz(a, sonuc, log):
    js, mdm = metinler(sonuc)
    for ad, metin in (("tr10b_sonuc.json", js), ("tr10b_sonuc.md", mdm)):
        with open(os.path.join(a.cikti_dizin, ad), "x", encoding="utf-8") as f:
            f.write(metin)
    log("hüküm: " + sonuc["hukum"])
    return 0, sonuc


def sentetik_kopya(D):
    """Kuru prova için D'nin kopyası: her geçerli istasyon-pencerenin gerçek değerleri yapay seriyle değiştirilir
    (gerçek gün maskesi korunur). Yarısı sünen (10 mm/yıl), yarısı sünmeyen (0,5 mm/yıl) olur ki r dalları da koşsun."""
    P = copy.deepcopy(D)
    gorulen = set()
    for S in P["sw"].values():
        for s in S.values():
            if not s["gecerli"] or id(s) in gorulen:
                continue
            gorulen.add(id(s))
            W = s["W"]
            rng = np.random.default_rng(seri_tohumu(s["kod"], s["Y"], "prova"))
            hiz = 10.0 if int(hashlib.sha256(s["kod"].encode()).hexdigest()[:2], 16) % 2 else 0.5
            x = yapay_rw(W["n"], rng) + hiz * np.arange(W["n"]) / 365.25
            x[~s["maske"]] = np.nan
            s["x"] = x
            s.pop("dv", None)
            s.pop("v5", None)
    return P


def kos(a, log=print):
    if a.devam:
        return devam(a, log)
    D = hazirla(a, log)
    sonuc, kod_hata = D["sonuc"], D["kod_hata"]
    if kod_hata is not None and a.duzeltme_turu < 2:
        sonuc["kod_hata"] = dict(denetim=kod_hata[0], deger=kod_hata[1], esik=str(kod_hata[2]))
        yol = os.path.join(a.cikti_dizin, f"tr10b_denetim_tur{a.duzeltme_turu}.json")
        with open(yol, "x", encoding="utf-8") as f:
            f.write(json.dumps(sonuc, ensure_ascii=False, indent=1, default=json_varsayilan) + "\n")
        log(f"KOD DENETİMİ BAŞARISIZ: {kod_hata}; gerçek Δv hesaplanmadı; düzeltme turu {a.duzeltme_turu}; {yol}")
        return 3, sonuc
    if kod_hata is not None:
        # §10.2 ("üçüncü başarısızlıkta hüküm kesin olarak 'geçersiz (kod)'") ve §10.3: kapıdan bağımsızdır. Kapı
        # sayıları da aynı kodun ürünüdür; kod hatası "veri yok" ardına saklanmaz (kod incelemesi, okuma 19).
        sonuc["hukum"] = (f"TR-10b: geçersiz (kod) ({kod_hata[0]}, {fmt_e(kod_hata[1])} / {fmt_e(kod_hata[2])}); "
                          f"gerçek Δv hesaplanmadı.")
        sonuc["kod_hata"] = dict(denetim=kod_hata[0], deger=kod_hata[1], esik=str(kod_hata[2]), kesin=True,
                                 kapi_bilgi=dict(gecti=D["kapi"], yer=D["S_B"], yer_pencere=D["N_B"]))
        return yaz(a, sonuc, log)
    if D["N_B"] < 2:
        sonuc["hukum"] = (f"TR-10b: veri yok (kural seti B: yer {D['S_B']} / yer-pencere {D['N_B']}; kapı ≥ 20 / "
                          f"≥ 40).{kuyruklar(None, D['kume'])}")
        return yaz(a, sonuc, log)
    # kuru prova: aynı ölçü, hüküm ve çıktı kodu, gerçek maskeler, yapay değerler; dosya yazılmaz
    try:
        P = sentetik_kopya(D)
        metinler(olcu_kur(P, log=lambda *_: None))
    except Exception as e:                                         # noqa: BLE001
        raise KosuDur(f"işaret öncesi kuru prova (yapay değerler) başarısız: {type(e).__name__}: {e}; işaret "
                      f"yazılmadı, gerçek Δv hesaplanmadı") from e
    del P
    # okuma anlık görüntüsü ve iki işaret, aynı adımda; işaret anlık görüntünün sha256'sını taşır
    anlik = pickle.dumps(D, protocol=4)
    anlik_sha = hashlib.sha256(anlik).hexdigest()
    with open(os.path.join(a.veri, ANLIK_AD), "xb") as f:
        f.write(anlik)
    isaret_metni = (f"TR-10b gerçek Δv hesaplandı\nmanifest_veri_sha256 {D['sonuc']['girdi']['manifest_veri_sha256']}\n"
                    f"anlik_sha256 {anlik_sha}\nkosu_kodu_sha256 {D['sonuc']['girdi']['kosu_kodu_sha256']}\n"
                    f"zaman {dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')}\n")
    for y in (os.path.join(a.veri, ISARET_AD), os.path.join(a.isaret_depo, ISARET_AD)):
        with open(y, "x", encoding="utf-8") as f:
            f.write(isaret_metni)
    log("işaret dosyaları ve okuma anlık görüntüsü yazıldı; gerçek Δv hesaplanıyor")
    try:
        sonuc["isaret"] = isaret_metni
        olcu_kur(D, log)
        return yaz(a, sonuc, log)
    except Exception as e:                                         # noqa: BLE001
        raise IsaretSonrasiHata(f"{type(e).__name__}: {e}") from e


def devam(a, log):
    """§14 madde 6: işaretten sonra bir istisna olduysa, yalnız doğrudan nedeni düzeltilmiş kodla, ham veri ikinci kez
    okunmadan, işaretle yazılmış anlık görüntüden sürdürür. İki işaret de olmalı, çıktılar olmamalı, anlık görüntü ve
    manifest işaretteki sha256'larla uyuşmalı."""
    yv, yd = os.path.join(a.veri, ISARET_AD), os.path.join(a.isaret_depo, ISARET_AD)
    if not (os.path.exists(yv) and os.path.exists(yd)):
        raise KosuDur("--devam: iki işaret dosyası da var olmalı (işaret yoksa olağan koşu)")
    for ad in ("tr10b_sonuc.json", "tr10b_sonuc.md"):
        if os.path.exists(os.path.join(a.cikti_dizin, ad)):
            raise KosuDur(f"--devam: çıktı zaten var ({ad}); devam yok")
    metin = open(yd, encoding="utf-8").read()
    if open(yv, encoding="utf-8").read() != metin:
        raise KosuDur("--devam: iki işaret dosyası farklı")
    alan = dict(s.split(" ", 1) for s in metin.splitlines()[1:] if " " in s)
    b = open(os.path.join(a.veri, ANLIK_AD), "rb").read()
    if hashlib.sha256(b).hexdigest() != alan.get("anlik_sha256"):
        raise KosuDur("--devam: anlık görüntünün sha256'sı işarettekiyle uyuşmuyor")
    if sha256_dosya(a.manifest) != alan.get("manifest_veri_sha256"):
        raise KosuDur("--devam: manifest sha256'sı işarettekiyle uyuşmuyor")
    D = pickle.loads(b)
    simdi = sha256_dosya(os.path.abspath(__file__))
    D["sonuc"]["isaret"] = metin
    D["sonuc"]["devam"] = dict(
        neden="işaret sonrası istisna; yalnız doğrudan nedeni düzeltildi (§14 madde 6); ham veri yeniden okunmadı",
        kosu_kodu_sha256_isaret=alan.get("kosu_kodu_sha256"), kosu_kodu_sha256_devam=simdi,
        zaman=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"))
    log(f"devam: anlık görüntüden sürdürülüyor (kod {alan.get('kosu_kodu_sha256', '?')[:12]} → {simdi[:12]})")
    try:
        olcu_kur(D, log)
        return yaz(a, D["sonuc"], log)
    except Exception as e:                                         # noqa: BLE001
        raise IsaretSonrasiHata(f"{type(e).__name__}: {e}") from e


def json_varsayilan(o):
    if isinstance(o, np.generic):
        return o.item()
    if isinstance(o, np.ndarray):
        return o.tolist()
    if hasattr(o, "isoformat"):
        return o.isoformat()
    return str(o)


def md_yap(s):
    L = ["# TR-10b sonuç", "", "Hüküm: " + s["hukum"], ""]
    o = s.get("olcu")
    if o and o.get("yanlis_alarm_cumlesi"):
        L += [o["yanlis_alarm_cumlesi"], "", o["chihshang_cumlesi"], ""]
    if s.get("devam"):
        L += [f"Not (§14 madde 6): {s['devam']}", ""]
    k = s["kapi"]
    kh = s.get("kod_hata")
    L += ["## Veri kapısı", "",
          f"- Kural seti B: yer {k['yer']}, yer-pencere {k['yer_pencere']}, kesim K = {k['kesim_K']}; kapı "
          f"{'geçti' if k['gecti'] else 'geçmedi'} (≥ 20 / ≥ 40). Yer kümesi (≤ 3 km): {k['yer_kumesi']}.",
          f"- Kural seti A: yer {k['A']['yer']}, yer-pencere {k['A']['yer_pencere']}; kapı "
          f"{'geçer' if k['A']['gecti'] else 'altı'}.",
          f"- İstasyon düzeyi (bilgi): istasyon {k['istasyon_bilgi']}, istasyon-pencere {k['istasyon_pencere_bilgi']}.",
          f"- Düşme nedenleri (istasyon-pencere): {k['dusme_nedenleri']}.",
          f"- Kaynak dökümü (yer-pencere): {k['kaynak_dokumu']}.",
          f"- Bilgi değişkelerinin sayımları (hükmü değiştirmez): {k['bilgi_sayimlari']}.",
          f"- Dolgulu yer-pencere: {k['dolgulu']} (eğimi sıfır {k['dolgulu_egim_sifir']}); kaynak|epok: "
          f"{k['dolgulu_kaynak_epok']}.",
          f"- Manifest: başarısız {len(s['manifest']['basarisiz'])} (pay {sayi(s['manifest']['pay'], 3)}); sha256 "
          f"denetimi geçti.", f"- Okuma sayaçları: {s['okuma']['toplam']}; biçim belirsiz: {s['okuma']['bicim_belirsiz']}.",
          f"- HDR adımı sayacı (§6.4 madde 4): {s['hdr_sayac']}.",
          f"- Düzeltme turu: {s['duzeltme_turu']}.", ""]
    if kh:
        L += [f"- Kod denetimi başarısız: {kh}.", ""]
    d = s.get("denetim", {})
    if "a" in d:
        a, b, f, c = d["a"], d["b"], d["f144"], d["c_yapay"]
        L += ["## Kod denetimleri (gerçek Δv görülmeden)", "",
              f"- (a) tam maske en büyük hata {sayi(a['tam_en_buyuk'], 6)} (≤ 0,005); gerçek maske en büyük "
              f"{sayi(a['maske_en_buyuk'], 4)} (≤ 0,50); elle katman {sayi(a['elle_en_buyuk'], 9)} (≤ 1e-6).",
              f"- (a3) {sayi(a['a3_en_buyuk'], 9)}; (a4) {sayi(a['a4_en_buyuk'], 9)} (≤ 1e-6).",
              f"- (b) n {b['n']}, R {b['R']}: q95 pay {sayi(b['q95_pay'], 3)} / payda {sayi(b['q95_payda'], 3)} = "
              f"{sayi(b['oran'], 3)} ([0,88, 1,12]; {'geçti' if b['gecti'] else 'GEÇMEDİ'}). Bilgi, tam maskeli payda: "
              f"{sayi(b['bilgi_tam_maske_payda'], 3)}, oran {sayi(b['bilgi_oran_tam'], 3)}.",
              f"- 144 satırlık 10MIN: {f['yer_pencere']} yer-pencere, en büyük fark {sayi(f['en_buyuk_fark'], 5)} "
              f"(≤ 0,005).",
              f"- (c-yapay): {c}.", f"- (c-gerçek): {d.get('c_gercek', 'koşulmadı')}.", ""]
    elif d:
        L += ["## Kod denetimleri", "", f"- {d}", ""]
    if o:
        L += ["## Ölçü satırları (§11)", ""]

        def sat(x, ad=None, gecti=s["kapi"]["gecti"]):
            ad = ad or x.get("ad")
            if not x.get("N"):
                return f"- {ad}: N 0"
            n = x["nokta"]
            ar = x.get("aralik", {})

            def f(k, dd=2):
                v = n.get(k)
                if x.get("guc_yok") or k not in ar:
                    return sayi(v, dd)
                if ar[k]["guc_yok"]:
                    return f"{sayi(v, dd)} (güç yok)"
                return f"{sayi(v, dd)} {aralik(ar[k]['L'], ar[k]['U'], dd)}"
            if x.get("guc_yok"):
                ek = " (güç yok; aralık yok)"
            else:
                ek = f" (aralık: {x.get('aralik_birim')} bootstrap'ı, K = {x.get('aralik_K')}"
                ek += "; blok yetersiz, bilgi)" if x.get("blok_yetersiz") else ")"
            kapi_alti = "" if gecti else " [kapı altı]"
            return (f"- {ad}{kapi_alti}: N {x['N']}, yer {x['S']}, kesim {x['K']}{ek}; |Δv| q50 {f('q50')}, q95 "
                    f"{f('q95')}, q99 {f('q99')} mm/yıl; |r| % q50 {f('r50', 0)}, q95 {f('r95', 0)}, q99 {f('r99', 0)} "
                    f"(sünen N {n.get('sunen_N')}); işaretli medyan {f('isaretli_medyan')}, hızlanan pay "
                    f"{f('hizlanan_pay')}, yavaşlayan pay {f('yavaslayan_pay')}; κ {f('kappa')}; q99/q95 "
                    f"{f('q99_q95')}; b* {f('b_yildiz')}")
        L.append(sat(o["ana"], "1. Ana (B)"))
        r = o["readme"]
        ra = r["rho_R_aralik"]
        L.append(f"   - README modeli: N_R {r['N_R']}, q95_N0,R {sayi(r['q95_N0_R'])}, ρ_R {sayi(r['rho_R'])} "
                 f"{aralik(ra.get('L'), ra.get('U')) if ra else ''}"
                 f"{' (güç yok)' if (r['guc_yok'] or (ra and ra['guc_yok'])) else ''}"
                 f"{'; okuma: README modeline göre ' + r['okuma'] if r.get('okuma') else ''}; T ≥ 2008: N "
                 f"{r['T2008']['N']}, ρ {sayi(r['T2008']['rho'])}."
                 f" Güç yasası serisi okuma aralığının başında sıfırdan başlar; n > 2'de sonuç bu seçime bağlıdır.")
        if o.get("etiket"):
            L.append(f"   - b* etiketi: {o['etiket']}. κ okuması: {o.get('kappa_okuma') or '(yok)'}.")
        if o.get("q99_notu"):
            L.append(f"   - q99: {o['q99_notu']}.")
        if o.get("chihshang"):
            L.append(f"   - Chihshang (§10.5): {o['chihshang']}.")
        L.append(sat(o["A"], "5. A satırı", gecti=s["kapi"]["A"]["gecti"]))
        L += ["", "### Kesim dökümü (yer bootstrap'ı)"] + [sat(v) for v in o["kesim"].values()]
        L += ["", "### Epok dökümü (bloklu)"] + [sat(v) for v in o["epok"].values()]
        L += ["", "### Katman ve kaynak dökümü"] + [sat(v) for v in o["katman"].values()] + \
             [sat(v) for v in o["kaynak"].values()]
        L += ["", "### Bilgi satırları"] + [sat(v, kk) for kk, v in o["bilgi"].items()]
        L.append(sat(o["ana_yer_bootstrap"], "yer bootstrap'ı aralıkları"))
        L.append(sat(o["readme"]["T2008"]["satir"], "README N0, T ≥ 2008"))
        m = o["mentese"]
        L.append(f"- Menteşe modeli Δv_m: N {m['N']}, |Δv_m| q50 {sayi(m['q50'])}, q95 {sayi(m['q95'])} "
                 f"(rank düşen {m['rank_dusen']}).")
        L.append("")
    L += ["## Girdiler", "", "```", json.dumps({k: v for k, v in s["girdi"].items() if k != "veri_dosyalari_sha256"},
                                                ensure_ascii=False, indent=1), "```", ""]
    return "\n".join(L) + "\n"


def argumanlar(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--veri", required=True)
    p.add_argument("--manifest", default=MANIFEST_VERI)
    p.add_argument("--listeler", default=TL.JSON_YOL)
    p.add_argument("--hdr-csv", default=HDR_CSV)
    p.add_argument("--hdr-baslik-csv", default=HDR_BASLIK_CSV)
    p.add_argument("--hdr-etki", default=HDR_ETKI)
    p.add_argument("--cikti-dizin", default=BURA)
    p.add_argument("--isaret-depo", default=BURA)
    p.add_argument("--duzeltme-turu", type=int, default=0, choices=(0, 1, 2))
    p.add_argument("--bicim-belirsiz", default="")
    p.add_argument("--devam", action="store_true",
                   help="yalnız işaret sonrası istisnada: anlık görüntüden sürdür (ham veri okunmaz)")
    return p.parse_args(argv)


def main(argv=None):
    a = argumanlar(argv)
    try:
        kodu, _ = kos(a)
    except BicimHata as e:
        print("KOŞU DURDU (biçim; hiçbir Δv hesaplanmadı):", e)
        print(json.dumps(e.kesif, ensure_ascii=False, indent=1))
        return 2
    except KosuDur as e:
        print("KOŞU DURDU (girdi; hiçbir Δv hesaplanmadı):", e)
        return 2
    except IsaretSonrasiHata as e:
        # gerçek değer içermez: yalnız istisna türü ve iletisi (ölçü kodu Δv'yi istisna iletisine koymaz)
        print("İŞARET SONRASI İSTİSNA (tek koşu kullanıldı; hiçbir çıktı yazılmadı). Yalnız doğrudan nedeni düzelt, "
              "farkı kayda geçir ve aynı komutu --devam ile koş (ham veri yeniden okunmaz):", e)
        return 4
    return kodu


if __name__ == "__main__":
    sys.exit(main())
