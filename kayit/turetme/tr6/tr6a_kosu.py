#!/usr/bin/env python3
"""TR-6a koşu kodu (ön kayıt sürüm 3, DONDURULDU, sha256 41ca1e95…a94e). Aşamalar ön kayıttaki sırayla (§5, §9):

  1. sinama      : §3.3 Okada doğrulaması, §9 adım 2 yapay katalog sınaması (tohum 20261114) ve tamlık sınaması
                   (tohum 20261115, yedek merdiveni). Çıktı tr6a_sinama_sonuc.json ("x"; bağlayıcı tohumlar yalnız
                   --baglayici ile ve yalnız bir kez). Geliştirmede --gelistirme ile başka tohum ve küçük deneme sayısı.
  2. manifest    : yalnız olay öncesi veri: sonlu fay ürünleri, alıcı tensörleri, ön katalog indirmeleri; loblar,
                   katalog seçimi, kapılar, kümeleme, çıkarmalar, sahte kalibrasyon (p₀), testere dişi, S2 negatif
                   kontrol, K⁺, K_nt, satır kapıları, olay sonrası indirme planı. Çıktı tr6a_manifest.json +
                   tr6a_on_ham_sha256.txt ("x"). Önkoşul: sinama çıktısı commit + push edilmiş ve geçmiş.
  3. son-indir   : manifest commit + push edilmiş, K_kapı ≥ 23, p₀ ≤ 0,60 ve kod incelemesi dosyası commit edilmişse
                   manifestteki plana göre olay sonrası katalog bir kez indirilir (hiçbir istek 2025-12-31'i aşamaz).
                   Çıktı tr6a_son_ham_sha256.txt + tr6a_son_kayit.json ("x").
  4. kos         : manifest ve ham listeler doğrulanır, manifest çekirdeği arşivden yeniden hesaplanıp karşılaştırılır,
                   ölçü/hüküm/çıktı kodu yapay olay sonrası verisiyle kuru koşulur, anlık görüntü + iki işaret "x"
                   kipinde yazılır, sonra oylar sayılır ve tr6a_sonuc.json / tr6a_sonuc.md bir kez yazılır.
                   Manifest "güç yok" / "güç yok (ölçü yanlı)" ya da sinama "koşulmadı" diyorsa olay sonrası veri
                   olmadan yalnız hüküm yazılır. İşaret sonrası istisnada yalnız doğrudan neden düzeltilip --devam.

Kod commit ya da push yapmaz; aşama geçişlerinde `git` ile gereken dosyaların commit edilip HEAD'in upstream'e push
edildiğini denetler, değilse KosuDur ile durur.

Çıkış kodları: 0 tamam; 2 KosuDur (önkoşul, biçim, körlük, kuru prova; işaret yazılmadı); 4 işaret sonrası istisna.
Kullanım: python3 -I -B kayit/turetme/tr6/tr6a_kosu.py <aşama> [seçenekler]   (--help)
"""
import argparse
import datetime as dt
import hashlib
import json
import math
import os
import pickle
import subprocess
import sys

import numpy as np

BURAYA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURAYA)
import tr6_a_kapi as KAPI                 # noqa: E402  (kumele, gereken_n0, binom_ust, uzaklik_km; ağ kodu yok)
import tr6a_onkayit_sayilar as S          # noqa: E402  (kritik, esik_H0, guc, sabitler)
import tr6a_okada as OK                   # noqa: E402
import tr6a_ffm as FFM                    # noqa: E402
import tr6a_katalog as KAT                # noqa: E402

DEPO = os.path.abspath(os.path.join(BURAYA, "..", "..", ".."))
ONKAYIT = os.path.join(DEPO, "kayit", "onkayit", "TR-6a_gerilme-olcer-kor-dogrulama_ONKAYIT.md")
ONKAYIT_SHA = "41ca1e951d330ab72d106be79bb5f700b415d9574dbddff3da0a12ad73fea94e"
# Ek 1 (12 Kasım 2026) dosyanın SONUNA eklendi: dondurulmuş gövde ilk ONKAYIT_GOVDE_BAYT bayttır; sha256 bu baytlar
# üzerinden denetlenir (eklerin kendisi commit'le sabitlenir; git_denetle ön kaydın commit+push edildiğini sınar).
ONKAYIT_GOVDE_BAYT = 126740
LISTE = os.path.join(BURAYA, "tr6a_olay_listesi.json")
LISTE_SHA = "0cde4fa1433eaa11f513460b1c728e4f3f142d3dc091c120f4f55b677728048f"
SAYILAR_JSON = os.path.join(BURAYA, "tr6a_onkayit_sayilar.json")
SAYILAR_JSON_SHA = "e39b3252a9f5db6b1c201936c245edb93b94b0a7c4ad94b5ed41d5c48db78c4f"
KOD_INCELEME = os.path.join(DEPO, "kayit", "onkayit", "TR-6a_KOD-INCELEME.md")
HAM_KOK = "/mnt/project-files/turetme/tr6a-ham"
SINAMA_CIKTI = os.path.join(BURAYA, "tr6a_sinama_sonuc.json")
MANIFEST = os.path.join(BURAYA, "tr6a_manifest.json")
ON_HAM_SHA = os.path.join(BURAYA, "tr6a_on_ham_sha256.txt")
SON_HAM_SHA = os.path.join(BURAYA, "tr6a_son_ham_sha256.txt")
SON_KAYIT = os.path.join(BURAYA, "tr6a_son_kayit.json")
SONUC_JSON = os.path.join(BURAYA, "tr6a_sonuc.json")
SONUC_MD = os.path.join(BURAYA, "tr6a_sonuc.md")
ISARET_AD = "TR6A_OLAY_SONRASI_OYLAR_SAYILDI"
ANLIK_AD = "TR6A_KOSU_ANLIK.pickle"
KOD_DOSYALARI = ("tr6a_kosu.py", "tr6a_okada.py", "tr6a_ffm.py", "tr6a_katalog.py", "tr6a_yapay.py",
                 "tr6a_onkayit_sayilar.py", "tr6_a_kapi.py", "tr6a_onbellek_kor.py", "tr6_sayim.py")

# Ek 1 kararları (kök oturum). None iken ilgili aşama durur; kod karar vermez (TR-6a_KODLAYICI-OKUMALARI.md).
# okuma 3 / Ek 1 E1.1: §3.3 sınama 3, 5 (uzak alan) ve 6'nın harfi harfine ölçütleri doğru kodda sağlanamıyor; Ek 1
# bağlayıcı ölçütü tanı biçimine çevirir (Richardson ≤ 1e−6; uzak alan farkı (L/r)² ile azalır) ve yayımlanmış denetim
# değerlerini (Okada 1985 Tablo 2, DC3D kılavuzu Ek-2) ekler. Değerlendirme tr6a_okada.dogrulama()["ek1"]'dedir.
OKADA_EK1_KARAR = dict(hukum="ek1_olcutu", olcut="Ek 1 E1.1 (tr6a_okada.dogrulama()['ek1'])")
TAMLIK_KURALLARI = ("A2", "yedek_a", "yedek_b", "yedek_c", "yedek_d")    # (d): Ek 1 E1.3 ((e) tanımlanmadı)

# ------------------------------------------------------------------ TR-6c (tasarım c; fark belgesi)
# `--tasarim c` bu modülün dosya yollarını ve kurallarını TR-6c'ye çevirir (tasarim_sec). Varsayılan "a" TR-6a'dır ve
# hiçbir davranışı değişmez. TR-6c ön kaydı TASLAK iken TR6C_ONKAYIT_SHA None'dur: bağlayıcı aşamalar koşmaz.
TASARIM = "a"
TR6A_ONKAYIT, TR6A_ONKAYIT_SHA, TR6A_GOVDE_BAYT = ONKAYIT, ONKAYIT_SHA, ONKAYIT_GOVDE_BAYT
TR6C_ONKAYIT = os.path.join(DEPO, "kayit", "onkayit", "TR-6c_gerilme-olcer-kor-dogrulama_ONKAYIT.md")
TR6C_ONKAYIT_SHA = None             # dondurulunca: TR-6c gövdesinin sha256'sı
TR6C_GOVDE_BAYT = None              # dondurulunca: TR-6c gövdesinin bayt uzunluğu
TR6C_N0_UST = None                  # §C4 kenar etkisi kuralının kapı N0 sınırı (olay/yıl; aşağıda N0_UST_C)


def tasarim_sec(t):
    """'a' (varsayılan, TR-6a) ya da 'c' (TR-6c): dosya yolları, ön kayıt denetimi ve tamlık kuralı."""
    g = globals()
    if t == "a":
        return
    if t != "c":
        raise ValueError(t)
    g.update(TASARIM="c", ONKAYIT=TR6C_ONKAYIT, ONKAYIT_SHA=TR6C_ONKAYIT_SHA, ONKAYIT_GOVDE_BAYT=TR6C_GOVDE_BAYT,
             SINAMA_CIKTI=os.path.join(BURAYA, "tr6c_sinama_sonuc.json"),
             MANIFEST=os.path.join(BURAYA, "tr6c_manifest.json"),
             ON_HAM_SHA=os.path.join(BURAYA, "tr6c_on_ham_sha256.txt"),
             SON_HAM_SHA=os.path.join(BURAYA, "tr6c_son_ham_sha256.txt"),
             SON_KAYIT=os.path.join(BURAYA, "tr6c_son_kayit.json"),
             SONUC_JSON=os.path.join(BURAYA, "tr6c_sonuc.json"), SONUC_MD=os.path.join(BURAYA, "tr6c_sonuc.md"),
             ISARET_AD="TR6C_OLAY_SONRASI_OYLAR_SAYILDI", ANLIK_AD="TR6C_KOSU_ANLIK.pickle",
             KOD_INCELEME=os.path.join(DEPO, "kayit", "onkayit", "TR-6c_KOD-INCELEME.md"),
             TAMLIK_KURALLARI=("yedek_d",))


def onkayit_uyusmuyor():
    """TR-6a: gövde sha256 dondurulan değerle uyuşmuyor mu. TR-6c: ayrıca TR-6a gövdesi (devralınan kurallar) denetlenir;
    TR-6c TASLAK iken (sha yok) KosuDur."""
    if TASARIM == "a":
        return onkayit_govde_sha() != ONKAYIT_SHA
    if ONKAYIT_SHA is None or ONKAYIT_GOVDE_BAYT is None:
        raise KosuDur("TR-6c ön kaydı TASLAK (dondurulmadı): bağlayıcı aşamalar koşmaz")
    with open(TR6A_ONKAYIT, "rb") as f:
        b = f.read(TR6A_GOVDE_BAYT)
    if hashlib.sha256(b).hexdigest() != TR6A_ONKAYIT_SHA:
        return True
    return onkayit_govde_sha() != ONKAYIT_SHA


ESIK = {a: KAPI.gereken_n0(math.exp(-S.DTAU_ESIK / a)) for a in (13.0, 19.0, 39.0)}
N0_YIL = S.T_ON_G / 365.25                      # 1796 g, yıl
T_ON = float(S.T_ON_G)
ON_A, ON_B = S.ON_G0, S.ON_G1                   # 1826, 30
SAHTE_ON_INDIRME_G = S.SAHTE_ILK_G + S.SAHTE_ADIM_G * (S.SAHTE_J - 1) + S.ON_G0 + S.TAMPON_G   # 3621
ANA_SOK_S, ANA_SOK_KM, ANA_SOK_M = 16.0, 100.0, 5.5
KEY_OFS, KEY_M = 1 << 19, 1 << 20
ASIGMALAR = (13.0, 19.0, 39.0)
MEGATHRUST = "ters, düşük eğimli (megathrust dahil)"
DOGRULTU_ATIMLI = "doğrultu atımlı"


class KosuDur(Exception):
    """Önkoşul, biçim, körlük ya da kuru prova hatası: işaret yazılmadı; çıkış kodu 2."""


class IsaretSonrasiHata(Exception):
    """İşaretten sonra istisna: tek koşu kullanıldı; yalnız doğrudan neden düzeltilip --devam (çıkış kodu 4)."""


# ================================================================== yardımcılar
def onkayit_govde_sha(yol=None):
    """Ön kaydın dondurulmuş gövdesinin (ilk ONKAYIT_GOVDE_BAYT bayt) sha256'sı; dosya daha kısaysa None."""
    with open(yol or ONKAYIT, "rb") as f:
        b = f.read(ONKAYIT_GOVDE_BAYT)
    return hashlib.sha256(b).hexdigest() if len(b) == ONKAYIT_GOVDE_BAYT else None


def sha256_dosya(yol):
    h = hashlib.sha256()
    with open(yol, "rb") as f:
        for p in iter(lambda: f.read(1 << 20), b""):
            h.update(p)
    return h.hexdigest()


def v(x, n=3):
    """Türkçe ondalık virgül."""
    if x is None:
        return "—"
    if isinstance(x, float) and math.isinf(x):
        return "−∞" if x < 0 else "∞"
    return f"{x:.{n}f}".replace(".", ",").replace("-", "−")


def json_v(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        f = float(o)
        return f if math.isfinite(f) else ("-inf" if f < 0 else "inf")
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (set, tuple)):
        return list(o)
    raise TypeError(type(o).__name__)


def _temiz(o):
    """JSON için: sonsuz float'ları dizgeye çevirir."""
    if isinstance(o, float) and not math.isfinite(o):
        return "-inf" if o < 0 else ("inf" if o > 0 else "nan")
    if isinstance(o, dict):
        return {str(k): _temiz(x) for k, x in o.items()}
    if isinstance(o, (list, tuple)):
        return [_temiz(x) for x in o]
    return o


def json_metni(o):
    return json.dumps(_temiz(o), ensure_ascii=False, indent=1, default=json_v) + "\n"


def x_yaz(yol, metin):
    """Var olan dosyanın üzerine yazmaz ("x" kipi)."""
    with open(yol, "x", encoding="utf-8") as f:
        f.write(metin)


def git(*args):
    return subprocess.run(["git", "-C", DEPO] + list(args), capture_output=True, text=True)


def git_denetle(yollar, log=print):
    """Her dosya izleniyor ve HEAD ile aynı; HEAD upstream'de (push edilmiş). Değilse KosuDur. Kod commit/push
    yapmaz; yalnız okur. (Upstream başvurusu yerel izleme dalıdır; push onu günceller.)"""
    for y in yollar:
        rel = os.path.relpath(y, DEPO)
        if git("ls-files", "--error-unmatch", "--", rel).returncode != 0:
            raise KosuDur(f"git: {rel} commit edilmemiş")
        if git("diff", "--quiet", "HEAD", "--", rel).returncode != 0:
            raise KosuDur(f"git: {rel} HEAD'deki hâlinden farklı (commit edilmemiş değişiklik)")
    up = git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
    if up.returncode != 0:
        raise KosuDur("git: dalın upstream'i yok (push edilmemiş)")
    if git("merge-base", "--is-ancestor", "HEAD", "@{u}").returncode != 0:
        raise KosuDur(f"git: HEAD {up.stdout.strip()} içinde değil (push edilmemiş)")
    log(f"git denetimi: {len(yollar)} dosya commit edilmiş, HEAD {up.stdout.strip()} içinde")


def kod_sha():
    return {k: sha256_dosya(os.path.join(BURAYA, k)) for k in KOD_DOSYALARI if os.path.exists(os.path.join(BURAYA, k))}


def liste_oku(yol=LISTE, sha=LISTE_SHA):
    if sha is not None and sha256_dosya(yol) != sha:
        raise KosuDur("tr6a_olay_listesi.json sha256 dondurulan değerle uyuşmuyor")
    return json.load(open(yol, encoding="utf-8"))


_P0_IZGARA = None


def p0_izgarasi():
    global _P0_IZGARA
    if _P0_IZGARA is None:
        if sha256_dosya(SAYILAR_JSON) != SAYILAR_JSON_SHA:
            raise KosuDur("tr6a_onkayit_sayilar.json sha256 dondurulan değerle uyuşmuyor")
        with open(SAYILAR_JSON, encoding="utf-8") as f:
            _P0_IZGARA = json.load(f)["p0_izgarasi"]
    return _P0_IZGARA


def kritik(K, p0):
    return S.kritik(K, p0) if K >= 1 else None


def ust_kuyruk(x, K, p):
    return KAPI.binom_ust(x, K, p) if K >= 1 else None


# ================================================================== §4.6 p₀ ve §5 testere dişi
def p0_kestir(Ssay, J):
    """p₀ = max(0,50; ⌈100 S/J⌉/100) (J ≥ 30); J < 30: max(0,52; ⌈100 S/J⌉/100); J = 0: 0,52. Tamsayı aritmetiği."""
    if J == 0:
        return 0.52, True
    yuz = -(-100 * Ssay // J)
    if J >= S.J_ALT:
        return max(50, yuz) / 100, False
    return max(52, yuz) / 100, True


def testere(K_kapi, p0):
    """§5: K_kapı = 23–80 için tr6a_onkayit_sayilar.json p0_izgarasi.<p₀>.testere (bağlayıcı); > 80 aynı kural."""
    anah = f"{p0:.2f}"
    if 23 <= K_kapi <= 80:
        r = p0_izgarasi()[anah]["testere"][str(K_kapi)]
        return dict(K_hukum=r["K_hukum"], atilan=r["atilan"], guc=r["guc"], c=r["c"],
                    tasarim_alti=bool(r.get("tasarim_alti", False)), kaynak="json")
    uygun = [k for k in range(S.K_ALT, K_kapi + 1) if S.guc(k, p0) >= S.GUC]
    if uygun:
        kh = max(uygun)
        return dict(K_hukum=kh, atilan=K_kapi - kh, guc=round(S.guc(kh, p0), 4), c=S.kritik(kh, p0),
                    tasarim_alti=False, kaynak="fonksiyon")
    return dict(K_hukum=K_kapi, atilan=0, guc=round(S.guc(K_kapi, p0), 4), c=S.kritik(K_kapi, p0),
                tasarim_alti=True, kaynak="fonksiyon")


def en_zayif_sirasi(kumeler, N0):
    """§5: kapı N0'ı en küçük önce; eşitlikte kimliği sözlük sırasında sonra gelen önce atılır."""
    s = sorted(kumeler, key=lambda c: c["temsilci"], reverse=True)
    return sorted(s, key=lambda c: N0[c["temsilci"]])


# ================================================================== §6.1, §6.4 hüküm adı (kapalı liste)
YONTEMLER = ("Okada sınaması", "yapay katalog sınaması", "tamlık sınaması")
DUSURUCULER = ("pozitif kontrol tutmadı", "olay öncesi düşüş eğilimi",
               "nötr bölgede de düşüş: tamlık ya da ağ yapay olgusu")


def taban_hukum(K, X, p0):
    c, h = S.kritik(K, p0), S.esik_H0(K)
    if X >= c:
        return "H1", c, h
    if X <= h:
        return "H0", c, h
    return "ayırt edilemez", c, h


def hukum_adi(f):
    """§6.4. f: dict(taban ∈ {yontem, guc_yok, olcu_yanli, H1, H0, ayırt edilemez}, yontem, S1 ∈ {tuttu, tutmadı,
    koşulamadı}, S2_dusus, S2_artis, S2_kosulamadi, S7 ∈ {koşulamadı, düşüş, ayrışmadı, ayrıştı}, S4_dayanir,
    tasarim_alti_guc, kalib_zayif (J, p0), ters_yon (None | ("not", Y, c⁺) | ("sınanamadı", p̂₀⁺)),
    etkin_N0 (None | (sayı, K))). Dönüş dict(ad, taban, parantez, ekler, tasinir)."""
    t = f["taban"]
    if t == "yontem":
        assert f["yontem"] in YONTEMLER
        return dict(ad=f"koşulmadı (yöntem: {f['yontem']})", taban="koşulmadı", parantez=[], ekler=[], tasinir=False)
    if t == "guc_yok":
        return dict(ad="güç yok", taban="güç yok", parantez=[], ekler=[], tasinir=False)
    if t == "guc_yok_tamlik":
        # Ek 1 E1.3 (d): K_kapı, tamlığı kestirilemeyen kümeler düşüldükten sonra < 23. Ad §6.4 (b)'nin "güç yok"udur
        # (kapalı liste genişletilmez); neden yalnız cümlede yazılır.
        return dict(ad="güç yok", taban="güç yok", neden="tamlık", parantez=[], ekler=[], tasinir=False)
    if t == "olcu_yanli":
        return dict(ad="güç yok (ölçü yanlı)", taban="güç yok (ölçü yanlı)", parantez=[], ekler=[], tasinir=False)
    assert t in ("H1", "H0", "ayırt edilemez")
    tas = f"tasarım gücünün altında: güç {v(f['tasarim_alti_guc'], 3)}" if f.get("tasarim_alti_guc") is not None \
        else None
    kz = (f"kalibrasyon zayıf: J = {f['kalib_zayif'][0]}, p₀ = {v(f['kalib_zayif'][1], 2)}"
          if f.get("kalib_zayif") else None)
    if t == "H1":
        dus = []
        if f["S1"] == "tutmadı":
            dus.append(DUSURUCULER[0])
        if f.get("S2_dusus") and not f.get("S2_kosulamadi"):
            dus.append(DUSURUCULER[1])
        if f["S7"] == "düşüş":
            dus.append(DUSURUCULER[2])
        if dus:
            return dict(ad=f"ayırt edilemez ({'; '.join(dus)})", taban="ayırt edilemez", parantez=dus, ekler=[],
                        tasinir=False, dusuruldu=True)
        nit = []
        if f["S1"] == "koşulamadı":
            nit.append("pozitif kontrol koşulamadı")
        if f.get("S2_kosulamadi"):
            nit.append("negatif kontrol koşulamadı")
        if f["S7"] == "koşulamadı":
            nit.append("nötr kontrol koşulamadı")
        elif f["S7"] == "ayrışmadı":
            nit.append("nötr kontrolden ayrışmadı")
        if f.get("S4_dayanir"):
            nit.append("megathrust kümelerine dayanıyor")
        if tas:
            nit.append(tas)
        if kz:
            nit.append(kz)
        ad = "H1" + (f" ({'; '.join(nit)})" if nit else "")
        return dict(ad=ad, taban="H1", parantez=nit, ekler=[], tasinir=(not nit or nit == [tas]))
    ekler = []
    ty = f.get("ters_yon")
    if ty and ty[0] == "not":
        ekler.append(f"ters yön notu: gölgede anlamlı artış (Y = {ty[1]} ≥ c⁺ = {ty[2]})")
    elif ty and ty[0] == "sınanamadı":
        ekler.append(f"ters yön sınanamadı (p̂₀⁺ = {v(ty[1], 3)})")
    if f["S1"] == "tutmadı":
        ekler.append("pozitif kontrol de tutmadı: hat ya da model başarısız; ayrılamaz")
    if f.get("S2_artis") and not f.get("S2_kosulamadi") and (t == "H0" or (ty and ty[0] == "not")):
        ekler.append("olay öncesi artış eğilimiyle ayırt edilemez")
    if f.get("etkin_N0"):
        a, K = f["etkin_N0"]
        ekler.append(f"oy Mc'si kapı Mc'sinin belirgin üstünde: K kümenin {a}'inde etkin N0_kul < 31,36")
    if tas:
        ekler.append(f"({tas})")
    if kz:
        ekler.append(f"({kz})")
    ad = t + ("" if not ekler else " — " + "; ".join(ekler))
    return dict(ad=ad, taban=t, parantez=[], ekler=ekler, tasinir=False)


def hukum_cumlesi(H, d):
    """§6.3 kalıpları. d: K, X, c, h, p0, p, J, p0_sapka, K_kapi, yontem_olcut."""
    t = H["taban"]
    if t == "koşulmadı":
        return (f"TR-6a koşulmadı: {d.get('yontem', '?')} önceden yazılan ölçütü tutmadı ({d.get('yontem_olcut', '?')})."
                " Olay sonrası veri indirilmedi. Aday elenmedi; yeniden açma ayrı ön kayıtla.")
    if t == "güç yok" and H.get("neden") == "tamlık":
        return (f"Olay sonrası bölge kataloğunda tamlık kestirilemediği için {d.get('dus')} küme 'veri yok (tamlık "
                f"kestirilemedi)' oldu (Ek 1 E1.3 (d)); kalan K_kapı = {d['K_kapi']} < 23 (önce {d.get('K_once')}). "
                "Hüküm satırı koşulmadı; hiçbir lob sayısı hesaplanmadı. Aday elenmedi; yeniden açma şartı §14.")
    if t == "güç yok":
        return (f"Lob Mc'siyle olay öncesi sayılan bağımsız küme K_kapı = {d['K_kapi']} < 23. Hüküm satırı koşulmadı, "
                "olay sonrası veri indirilmedi. Aday elenmedi; yeniden açma şartı §14.")
    if t == "güç yok (ölçü yanlı)":
        return (f"Olay öncesi sahte zamanlarda düşüş oyu payı p̂₀ = {v(d['p0_sapka'], 3)} (J = {d['J']}) > 0,60. "
                "Ölçü H0 altında yanlı; hüküm satırı koşulmadı, olay sonrası veri indirilmedi.")
    iki = (" Bu sonuç iki açıklamayı ayıramaz: (i) hız-durum gerilme ölçeri (Aσ 19 kPa) gölgeyi 1 yılda göremiyor, (ii) "
           "Coulomb modelinin gölgesi (tek sonlu fay modeli, tek alıcı düzlem, μ' 0,4, 7,5 km) yanlış yerde ya da gerçek "
           "değil.")
    if t == "H1" and not H.get("dusuruldu"):
        return (f"Kosismik Coulomb gölge loblarında (ΔCFF ≤ −10 kPa, kırıktan 20 km–2L) olay sonrası [30 g, 365 g) oran "
                f"düşüşü K = {d['K']} bağımsız kümenin X = {d['X']}'inde görüldü (kritik c = {d['c']}; p₀ = "
                f"{v(d['p0'], 2)}, tek yanlı kesin binom p = {v(d['p'], 4)}). Hız-durum gerilme ölçeri bu örneklemde "
                "gölgelerin işaretini olay öncesi sahte zamanlarla kalibre edilmiş rastlantı düzeyinin üstünde buluyor. "
                "Bu, yöntemin işaret düzeyinde geçerliliğidir; Marmara'da kullanılabilirliği göstermez ((b) ayağı "
                "çözünürlük kapısını geçmedi).")
    if t == "H0":
        s = (f"Gölge loblarında düşüş oyu K = {d['K']} kümenin X = {d['X']}'inde (X ≤ h = {d['h']}). Küme başına 0,75 ve "
             "üstü oy olasılığı bu örneklemle dışlandı." + iki)
    else:
        s = (f"X = {d['X']}, h = {d['h']} < X < c = {d['c']} (K = {d['K']}, p₀ = {v(d['p0'], 2)}). Bu örneklem "
             "p ≈ p₀ ile p ≈ 0,75'i ayıramıyor." + iki)
    if any(e.startswith("ters yön notu") for e in H["ekler"]):
        s += (" Gölgede anlamlı artış (Y ≥ c⁺): Hardebeck & Harris (2025) bulgusunun küresel karşılığı; aynı iki "
              "açıklama burada da ayrılmaz.")
    if any(e.startswith("oy Mc'si") for e in H["ekler"]):
        s += (" Olumsuz sonuç (iii) ana şok sonrası tamlık sınırıyla da açıklanabilir; (i), (ii) ve (iii) "
              "ayrılamaz.")
    return s


def marmara_satiri(H):
    """§6.4 madde 5, §13. Mutlak olasılık, çarpan ya da tarih hiçbir durumda yazılmaz."""
    if H["taban"] == "H1" and not H.get("dusuruldu"):
        if H["tasinir"]:
            return ("Marmara'ya taşınan tek cümle: \"sismisite oranından gerilme işareti çıkaran hız-durum ölçeri, "
                    "küresel kosismik gölgelerde işaret düzeyinde geçerli.\" Bu, Marmara'da kullanılabilirlik değildir.")
        return "Marmara'ya taşınmadı: " + "; ".join(x for x in H["parantez"] if not x.startswith("tasarım gücünün"))
    return "Marmara'ya hiçbir şey taşınmaz (§13)."


# ================================================================== birim hazırlığı (§3.2–§3.4)
def _anahtar(i, j):
    return (np.asarray(i, np.int64) + KEY_OFS) * KEY_M + (np.asarray(j, np.int64) + KEY_OFS)


def hucre_maskeleri(H, L):
    """§3.4 ve §7 lob tanımları. H: dA (ana alıcı), dB (ikinci düzlem), r_k, tekil."""
    rk, tek, dA, dB = H["r_k"], H["tekil"], H["dA"], H["dB"]
    b20 = (rk >= 20.0) & (rk <= 2 * L)
    temiz = ~tek
    g = b20 & temiz & (dA <= -S.DTAU_ESIK)
    p = b20 & temiz & (dA >= S.DTAU_ESIK)
    rmax = rk[g].max() if g.any() else -np.inf
    n = b20 & temiz & (np.abs(dA) <= 2.0) & (rk <= rmax)
    return dict(
        bolge=b20, golge=g, pozitif=p, notr=n,
        D3a=(rk >= 5.0) & (rk <= 2 * L) & temiz & (dA <= -S.DTAU_ESIK),
        D3b=(rk >= 40.0) & (rk <= 2 * L) & temiz & (dA <= -S.DTAU_ESIK),
        D5=b20 & temiz & (dA <= -S.DTAU_ESIK) & (dB <= -S.DTAU_ESIK),
        D8=b20 & temiz & (dA <= -30.0),
        ic_sinir_golge=(rk < 20.0) & temiz & (dA <= -S.DTAU_ESIK),
    )


def ev_maske(E, hm):
    h = E["h"]
    return (h >= 0) & hm[np.maximum(h, 0)]


def bos_E():
    return dict(t=np.zeros(0), la=np.zeros(0), lo=np.zeros(0), m=np.zeros(0), h=np.zeros(0, np.int64),
                ana_sok=np.zeros(0, bool))


def E_birlestir(a, b):
    o = {k: np.concatenate([a[k], b[k]]) for k in ("t", "la", "lo", "m", "h", "ana_sok")}
    s = np.argsort(o["t"], kind="stable")
    return {k: x[s] for k, x in o.items()}


class Analiz:
    """Bir birim listesi + bir veri kaynağı üzerinde §3–§7 hesabı. Kaynak arayüzü (tr6a_yapay.YapayKaynak,
    GercekKaynak, ArsivKaynak): ffm(uye_id) -> tr6a_ffm.coz biçimi; tensorler(birim) -> [(mrr, mtt, mpp, mrt, mrp,
    mtp)]; katalog(birim, katalog, t_bas, t_bit (datetime), taban, R_km, merkez, asama) -> FDSN sözlüğü (ham)."""

    def __init__(self, liste, kaynak, kural="A2", log=print, adaylar=None):
        assert kural in TAMLIK_KURALLARI
        self.liste, self.kaynak, self.kural, self.log = liste, kaynak, kural, log
        self.S0 = KAT.SON_BASLANGIC_G[kural]
        self.olay = {o["id"]: o for o in liste["olaylar"]}
        self.birim = {b["id"]: b for b in liste["birimler"]}
        ids = adaylar if adaylar is not None else [b["id"] for b in liste["birimler"] if b["kosu_adayi"]]
        self.adaylar = sorted(ids, key=lambda u: self.birim[u]["zaman"])
        self.B = {}
        self.R_A = {}
        self.son_eklendi = False

    # ---------------------------------------------------------------- sonlu fay, alıcı, ızgara, kesme
    def hazirla(self, havuz_R_A=True):
        for u in self.adaylar:
            self.B[u] = self._birim_hazirla(self.birim[u])
        if havuz_R_A:
            for o in self.liste["olaylar"]:
                self.R_A[o["id"]] = self._R_A(o)
        for u, B in self.B.items():
            if B["durum"] == "hazır":
                self._kesme(B)

    def _birim_hazirla(self, b):
        t0, ts = KAT.gun(b["zaman"]), KAT.gun(b["t_s"])
        B = dict(id=b["id"], t0=t0, ts=ts, L=float(b["L_km"]), la=b["enlem"], lo=b["boylam"], durum="hazır",
                 kat={}, ffm={})
        af = []
        for uy in b["uyeler"]:
            try:
                r = self.kaynak.ffm(uy)
            except FFM.VeriYok as e:
                B.update(durum="veri yok", neden=f"{uy}: {e}")
                return B
            B["ffm"][uy] = {k: r[k] for k in r if k != "altfaylar"}
            af += [dict(a, uye=uy) for a in r["altfaylar"]]
        izd = OK.altfaylari_izdus(af, B["la"], B["lo"])
        al = OK.alici_sec(self.kaynak.tensorler(b), af)
        B["alici"] = {k: (list(x) if isinstance(x, tuple) else x) for k, x in al.items()}
        G = OK.izgara_hesapla(izd, B["L"], {"ana": al["alici"], "ikinci": al["ikinci"]}, r_ic=0.0)
        H = dict(i=G["i"], j=G["j"], x=G["x"], y=G["y"], r_k=G["r_k"], tekil=G["tekil"], dA=G["dcff"]["ana"],
                 dB=G["dcff"]["ikinci"])
        k = _anahtar(H["i"], H["j"])
        o = np.argsort(k)
        H["anahtar"], H["sira"] = k[o], o
        B["H"], B["iz"] = H, G["iz"]
        B["R_sorgu"] = 2 * B["L"] + float(np.hypot(G["iz"][:, 0], G["iz"][:, 1]).max())
        M = hucre_maskeleri(H, B["L"])
        B["M"] = M
        B["hucre"] = dict(golge=int(M["golge"].sum()), pozitif=int(M["pozitif"].sum()), notr=int(M["notr"].sum()),
                          D8=int(M["D8"].sum()), D3a=int(M["D3a"].sum()), D3b=int(M["D3b"].sum()),
                          D5=int(M["D5"].sum()), bolge=int(M["bolge"].sum()),
                          tekil_yakin_alan_bolgede=int((H["tekil"] & M["bolge"]).sum()),
                          tekil_yakin_alan_toplam=int(H["tekil"].sum()),
                          ic_sinir_atilan_golge=int(M["ic_sinir_golge"].sum()),
                          ic_sinir_atilan_pay=round(float(M["ic_sinir_golge"].sum())
                                                    / max(1, int(M["ic_sinir_golge"].sum() + M["golge"].sum())), 4))
        B["lob_ortalama_dcff"] = dict(golge=float(H["dA"][M["golge"]].mean()) if M["golge"].any() else None,
                                      pozitif=float(H["dA"][M["pozitif"]].mean()) if M["pozitif"].any() else None)
        return B

    def _R_A(self, o):
        """§9 adım 3: R_A = 2 L_A + (kırık izinin dış merkeze en uzak noktası). Sonlu fay okunamazsa None."""
        try:
            r = self.kaynak.ffm(o["id"])
        except (FFM.VeriYok, FFM.BicimHata, OK.OkadaHata):
            return None
        af = [dict(a, uye=o["id"]) for a in r["altfaylar"]]
        iz = OK.kirik_izi(OK.altfaylari_izdus(af, o["enlem"], o["boylam"]))
        return round(2 * o["L_km"] + float(np.hypot(iz[:, 0], iz[:, 1]).max()), 1) if len(iz) else None

    def _izd(self, B, la, lo):
        x, y = OK.aeqd_ileri(B["la"], B["lo"], np.atleast_1d(la), np.atleast_1d(lo))
        return OK.en_yakin_uzaklik(x, y, B["iz"])

    def _kesme(self, B):
        """§3.7: [t_s + 30 g, t0 + 365 g) aralığında, kırık izine yatay uzaklığı ≤ 2L havuz olayı (grup dışı) varsa son
        pencere o olaydan bir gün önce biter. Bayraklar: [t_s + 30 g, t0 + 365 g) ve 2L (B3); öncül komşu (B3)."""
        b = self.birim[B["id"]]
        bas, bit = B["ts"] + S.SON_G0, B["t0"] + S.SON_G1
        aday, bayrak, oncul = [], [], []
        for o in self.liste["olaylar"]:
            if o["grup"] == B["id"]:
                continue
            to = KAT.gun(o["zaman"])
            if B["t0"] - 365 <= to < B["t0"]:
                d = float(KAPI.uzaklik_km(b["enlem"], b["boylam"], np.array([o["enlem"]]), np.array([o["boylam"]]))[0])
                if d < 3 * o["L_km"] + 3 * B["L"]:
                    oncul.append(o["id"])
            if not (B["t0"] <= to < bit):
                continue
            rk = float(self._izd(B, o["enlem"], o["boylam"])[0])
            if rk <= 2 * B["L"] and to >= bas:
                # B3 bayrağı "temsilcinin son penceresinde" (§7 B3): [t_s + 30 g, t0 + 365 g) (kod incelemesi K1;
                # önceden [t0, t_s + 30 g) olayları da bayraklanıyordu)
                bayrak.append(o["id"])
                aday.append((to, o["id"], round(rk, 1)))
        if aday:
            to, oid, rk = min(aday)
            B["son_bit"], B["kesme"] = to - 1.0, dict(olay=oid, r_k_km=rk)
        else:
            B["son_bit"], B["kesme"] = bit, None
        B["T_son"] = B["son_bit"] - (B["ts"] + self.S0)
        B["pi"] = B["T_son"] / (T_ON + B["T_son"]) if B["T_son"] > 0 else None
        B["bayrak_2L_365"], B["oncul_komsu"] = bayrak, oncul

    # ---------------------------------------------------------------- katalog (§3.5)
    def kataloglar_gereken(self, B):
        b = self.birim[B["id"]]
        k = list(b["secilebilir_kataloglar"])
        if b.get("isc_kurali_ile_dusen") and "ISC" in b["kataloglar"] and \
                not b["kataloglar"]["ISC"]["gecersiz_sifir_buyukluk"] and "ISC" not in k:
            k.append("ISC")          # yalnız D6 satırı için
        return k

    def _olaylari_yerlestir(self, B, d, taban, ana_sok=False):
        tut, sayim = KAT.buyukluk_kurallari(d, taban)
        x = KAT.secim(d, tut)
        derin = x["de"] <= KAT.DERIN_KM + 1e-9
        sayim["derinlik_disi"] = int((~derin).sum())
        x = KAT.secim(x, derin)
        if len(x["m"]) == 0:
            return bos_E(), sayim
        xx, yy = OK.aeqd_ileri(B["la"], B["lo"], x["la"], x["lo"])
        i, j = OK.hucre_indeksi(xx, yy)
        k = _anahtar(i, j)
        H = B["H"]
        pos = np.minimum(np.searchsorted(H["anahtar"], k), len(H["anahtar"]) - 1)
        var = H["anahtar"][pos] == k
        h = np.where(var, H["sira"][pos], -1)
        sayim["bolge_disi"] = int((h < 0).sum())
        E = dict(t=x["t"][var], la=x["la"][var], lo=x["lo"][var], m=x["m"][var], h=h[var].astype(np.int64),
                 ana_sok=np.zeros(int(var.sum()), bool))
        if ana_sok:
            for uy in self.birim[B["id"]]["uyeler"]:
                o = self.olay[uy]
                to = KAT.gun(o["zaman"])
                yak = np.abs(E["t"] - to) <= ANA_SOK_S / 86400.0
                if yak.any():
                    r = KAPI.uzaklik_km(o["enlem"], o["boylam"], E["la"], E["lo"])
                    E["ana_sok"] |= yak & (r <= ANA_SOK_KM) & (E["m"] >= ANA_SOK_M)
            sayim["ana_sok_satiri"] = int(E["ana_sok"].sum())
        s = np.argsort(E["t"], kind="stable")
        return {k_: a[s] for k_, a in E.items()}, sayim

    def on_katalog(self):
        """Ön indirme [t0 − 3621 g, t0 − 30 g), taban Mc_halka − 0,05, daire R (§3.5, §4.6). Aşama sınırı t0 − 30 g."""
        for u in self.adaylar:
            B = self.B[u]
            if B["durum"] != "hazır":
                continue
            b = self.birim[u]
            for k in self.kataloglar_gereken(B):
                mc_h = float(b["kataloglar"][k]["mc"])
                taban = round(mc_h - 0.05, 2)
                t_bas = KAT.zaman(B["t0"] - SAHTE_ON_INDIRME_G)
                t_bit = KAT.zaman(B["t0"] - ON_B)
                try:
                    d = self.kaynak.katalog(b, k, t_bas, t_bit, taban, B["R_sorgu"], (B["la"], B["lo"]), "on")
                except KAT.VeriYok as e:
                    B["durum"], B["neden"] = "veri yok", f"{k} ön indirme: {e}"
                    break
                E, sayim = self._olaylari_yerlestir(B, d, taban)
                B["kat"][k] = dict(E=E, mc_halka=mc_h, taban=taban, sayim_on=sayim)

    # ---------------------------------------------------------------- lob sayıları
    def mc_lob(self, E, ev, on, mc_halka):
        a, b = on
        return KAT.mc_lob(E["m"][ev & (E["t"] >= a) & (E["t"] < b)], mc_halka)

    @staticmethod
    def say(E, ev, on, son, son_katalog, mc, kumesiz=True):
        return KAT.pencere_sayisi(E, ev, dict(on=on, son=son, son_katalog=son_katalog), mc, kumesiz)

    def kapi_degerleri(self, B, k):
        """§4.2 kapı N0'ları (Mc_lob, yalnız ön katalog kümesizleştirmesi) ve satır kapıları (D1, D3a, D3b, D4, D5, D8,
        pozitif, nötr)."""
        KK = B["kat"][k]
        E, on = KK["E"], (B["t0"] - ON_A, B["t0"] - ON_B)
        out = {}
        # yalniz_golge: yalnız yapay tek birim sınamasında (TR-6c provası) hız için; gölge sayıları aynıdır
        loblar = ("golge",) if getattr(self, "yalniz_golge", False) else ("golge", "pozitif", "notr", "D3a", "D3b",
                                                                          "D5", "D8")
        for lob in loblar:
            ev = ev_maske(E, B["M"][lob])
            mcl, bilgi = self.mc_lob(E, ev, on, KK["mc_halka"])
            n_on = self.say(E, ev, on, None, None, mcl)[0]
            out[lob] = dict(mc_lob=mcl, mc_bilgi=bilgi, n_on=n_on, N0=round(n_on / N0_YIL, 4))
        if getattr(self, "yalniz_golge", False):
            return out
        ev = ev_maske(E, B["M"]["golge"])
        g = out["golge"]
        n1 = self.say(E, ev, on, None, None, g["mc_lob"] + 0.5)[0]
        n4 = self.say(E, ev, on, None, None, g["mc_lob"], kumesiz=False)[0]
        out["D1"] = dict(mc_lob=r2(g["mc_lob"] + 0.5), n_on=n1, N0=round(n1 / N0_YIL, 4))
        out["D4"] = dict(mc_lob=g["mc_lob"], n_on=n4, N0=round(n4 / N0_YIL, 4))
        return out

    def katalog_secimi(self):
        """§3.5: seçilebilir kataloglar arasında gölge kapı N0'ı en büyük; eşitlikte ISC, ComCat, GeoNet, EMSC, KOERI."""
        for u in self.adaylar:
            B = self.B[u]
            if B["durum"] != "hazır":
                continue
            B["kapi"] = {k: self.kapi_degerleri(B, k) for k in B["kat"]}
            sec = [k for k in self.birim[u]["secilebilir_kataloglar"] if k in B["kapi"]]
            B["secim"] = (max(sec, key=lambda k: (B["kapi"][k]["golge"]["N0"], -KAT.SECIM_SIRASI.index(k)))
                          if sec else None)

    # ---------------------------------------------------------------- kümeleme ve çıkarmalar (§3.7, §5)
    def kume_seti(self, gecen):
        bl = [self.birim[u] for u in sorted(gecen, key=lambda u: self.birim[u]["zaman"])]
        kl = KAPI.kumele(bl)
        kal, cik = [], []
        for c in kl:
            tem = c[0]["id"]
            uy = {x for b in c for x in b["uyeler"]}
            ad = dict(temsilci=tem, birimler=[b["id"] for b in c])
            if uy & set(S.BILINEN_CIKAN):
                cik.append(dict(ad, neden="bilinen sonuçlu (§3.4)"))
            elif self.B[tem]["T_son"] < S.KISA_SON_G:
                cik.append(dict(ad, neden="kısa son pencere (§3.7)", T_son_g=round(self.B[tem]["T_son"], 3),
                                kesme=self.B[tem]["kesme"]))
            else:
                kal.append(ad)
        return kal, cik, kl

    def tek_baglanti_ciftleri(self, kl):
        n = 0
        for a in range(len(kl)):
            for b in range(a + 1, len(kl)):
                if any(float(KAPI.uzaklik_km(x["enlem"], x["boylam"], np.array([y["enlem"]]), np.array([y["boylam"]]))[0])
                       < 300.0 and abs((dt.datetime.fromisoformat(x["zaman"])
                                        - dt.datetime.fromisoformat(y["zaman"])).days) < 1826
                       for x in kl[a] for y in kl[b]):
                    n += 1
        return n

    # ---------------------------------------------------------------- pencereler ve oylar
    def pencere(self, B, tur, j=None):
        t0, ts, k = B["t0"], B["ts"], B["ts"] - B["t0"]
        if tur == "gercek":
            s, e = ts + self.S0, B["son_bit"]
            return dict(on=(t0 - ON_A, t0 - ON_B), son=(s, e), son_katalog=t0, koken=ts, pi=B["pi"], T_son=e - s)
        if tur == "D2":
            s, e = ts + 90.0, B["son_bit"]
            return dict(on=(t0 - ON_A, t0 - ON_B), son=(s, e), son_katalog=t0, koken=ts, pi=(e - s) / (T_ON + e - s),
                        T_son=e - s)
        if tur == "sahte":
            tp = t0 - S.SAHTE_ILK_G - S.SAHTE_ADIM_G * (j - 1)
            s, e = tp + k + self.S0, tp + (B["son_bit"] - t0)
            return dict(on=(tp - ON_A, tp - ON_B), son=(s, e), son_katalog=tp, koken=tp + k, pi=B["pi"], T_son=e - s)
        if tur == "nk":
            o = t0 - S.SAHTE_ILK_G + k
            s, e = o + self.S0, t0 - ON_B
            return dict(on=(t0 - ON_A, t0 - S.NK_G0), son=(s, e), son_katalog=t0 - S.SAHTE_ILK_G, koken=o,
                        pi=(e - s) / (S.T_NK_ON_G + e - s), T_son=e - s)
        raise ValueError(tur)

    def mc_son(self, B, k, P, mc_lob_golge):
        E = B["kat"][k]["E"]
        ev = ev_maske(E, B["M"]["bolge"])
        return KAT.mc_son(E["t"][ev], E["m"][ev], P["koken"], P["son"][1], mc_lob_golge, self.kural)

    def lob_oyu(self, B, k, lob, P, mc_kul, kumesiz=True, T_on=T_ON):
        E = B["kat"][k]["E"]
        ev = ev_maske(E, B["M"][lob])
        n_on, n_son = self.say(E, ev, P["on"], P["son"], P["son_katalog"], mc_kul, kumesiz)
        D, A = KAT.oy(n_on, n_son, P["pi"])
        if n_on == 0:
            dl = None
        elif n_son == 0:
            dl = -math.inf
        else:
            dl = math.log((n_son / P["T_son"]) / (n_on / T_on))
        return dict(n_on=n_on, n_son=n_son, D=D, A=A, pi=round(P["pi"], 6), mc_kul=mc_kul,
                    N0_kul=round(n_on / N0_YIL, 4), ln_oran=dl)

    def sahte_oylari(self, B, k):
        """§4.6: üç sahte zaman; geçerlilik listeden (havuz) ve sahte kapıdan (n_on' ≥ 155, sahte Mc_lob)."""
        b = self.birim[B["id"]]
        E, mc_h = B["kat"][k]["E"], B["kat"][k]["mc_halka"]
        ev = ev_maske(E, B["M"]["golge"])
        out = []
        for s in b["sahte"]:
            j = s["j"]
            r = dict(j=j, gecerli=False)
            if not s["gecerli"]:
                r["neden"] = "havuz: " + ",".join(s["ortusen"])
                out.append(r)
                continue
            P = self.pencere(B, "sahte", j)
            mcl, _ = self.mc_lob(E, ev, P["on"], mc_h)
            n_kapi = self.say(E, ev, P["on"], None, None, mcl)[0]
            r.update(mc_lob=mcl, n_on_kapi=n_kapi)
            if n_kapi / N0_YIL < ESIK[19.0]:
                r["neden"] = "sahte kapı"
                out.append(r)
                continue
            ms, msb = self.mc_son(B, k, P, mcl)
            if ms is None:                                   # Ek 1 E1.3 (d)
                r.update(neden="tamlık kestirilemedi", mc_son_bilgi=msb)
                out.append(r)
                continue
            mk = r2(max(mcl, ms))
            o = self.lob_oyu(B, k, "golge", P, mk)
            r.update(gecerli=True, mc_son=ms, mc_son_bilgi=msb, **o)
            out.append(r)
        return out

    def nk_oyu(self, B, k):
        """§7 S2: ön [t0 − 1826, t0 − 365), son [t0 − 365 g + (t_s − t0), t0 − 30) (yedek (c): t0 − 305 g + …);
        Mc kendi pencerelerinden (§3.5)."""
        KK = B["kat"][k]
        E = KK["E"]
        ev = ev_maske(E, B["M"]["golge"])
        P = self.pencere(B, "nk")
        mcl, _ = self.mc_lob(E, ev, P["on"], KK["mc_halka"])
        ms, msb = self.mc_son(B, k, P, mcl)
        if ms is None:                                       # Ek 1 E1.3 (d): S2'ye girmez
            return None
        mk = r2(max(mcl, ms))
        o = self.lob_oyu(B, k, "golge", P, mk, T_on=float(S.T_NK_ON_G))
        return dict(o, mc_lob=mcl, mc_son=ms, T_son=round(P["T_son"], 3))

    # ---------------------------------------------------------------- manifest (§5 işlem sırası)
    def manifest(self):
        L = self.log
        aday = [u for u in self.adaylar]
        veri_yok = {u: self.B[u].get("neden") for u in aday if self.B[u]["durum"] != "hazır"}
        hazir = [u for u in aday if self.B[u]["durum"] == "hazır"]
        N0 = {u: self.B[u]["kapi"][self.B[u]["secim"]]["golge"]["N0"] for u in hazir if self.B[u]["secim"]}
        gecen = [u for u in hazir if self.B[u]["secim"] and N0[u] >= ESIK[19.0]]
        kal, cik, kl = self.kume_seti(gecen)
        K_kapi = len(kal)
        L(f"manifest: aday {len(aday)}, veri yok {len(veri_yok)}, kapı {len(gecen)} birim, {len(kl)} küme, "
          f"çıkan {len(cik)}, K_kapı {K_kapi}")
        m = dict(kural=self.kural, aday=len(aday), veri_yok=veri_yok, kapi_birim=gecen, kume_sayisi=len(kl),
                 kumeler=kal, cikan=cik, K_kapi=K_kapi, tek_baglanti_cift=self.tek_baglanti_ciftleri(kl),
                 esik=dict((f"{a:g}", round(e, 4)) for a, e in ESIK.items()))
        mek = {}
        for c in kal:
            s_ = self.birim[c["temsilci"]]["mekanizma_sinif"]
            mek[s_] = mek.get(s_, 0) + 1
        m["mekanizmaya_gore_K"] = mek
        # sahte kalibrasyon (§4.6) — K_kapı kümelerinde; K_kapı < 23 iken bilgi
        sahte = {}
        for c in kal:
            B = self.B[c["temsilci"]]
            sahte[c["temsilci"]] = self.sahte_oylari(B, B["secim"])
        gec = [r for x in sahte.values() for r in x if r["gecerli"]]
        J, Ss, Sp = len(gec), sum(r["D"] for r in gec), sum(r["A"] for r in gec)
        p0, zayif = p0_kestir(Ss, J)
        p0p, _ = p0_kestir(Sp, J)
        m["sahte"] = dict(oylar=sahte, J=J, S=Ss, S_arti=Sp, p0_sapka=(Ss / J if J else None),
                          p0_arti_sapka=(Sp / J if J else None), J30_kurali=zayif, p0=p0, p0_arti=p0p)
        med = float(np.median([N0[c["temsilci"]] for c in kal])) if kal else None
        for ad_, kos in (("altinda", lambda x: x <= med), ("ustunde", lambda x: x > med)):
            g_ = [r for c in kal if kos(N0[c["temsilci"]]) for r in sahte[c["temsilci"]] if r["gecerli"]]
            m["sahte"][f"p0_sapka_N0_medyan_{ad_}"] = (sum(r["D"] for r in g_) / len(g_)) if g_ else None
        m["sahte"]["K_0"] = [dict(id=c["temsilci"], N0=N0[c["temsilci"]]) for c in kal
                             if not any(r["gecerli"] for r in sahte[c["temsilci"]])]
        m["durum"] = "devam"
        if K_kapi < S.K_ALT:
            m["durum"] = "güç yok"
        elif p0 > S.P0_UST:
            m["durum"] = "güç yok (ölçü yanlı)"
        m["kapi_N0"] = {u: N0[u] for u in N0}
        # testere dişi
        if m["durum"] == "devam":
            tz = testere(K_kapi, p0)
            sira = en_zayif_sirasi(kal, N0)
            atilan = [c["temsilci"] for c in sira[:tz["atilan"]]]
            ana = [c for c in kal if c["temsilci"] not in atilan]
            m["testere"] = dict(tz, atilan_kumeler=atilan, c_K=S.kritik(tz["K_hukum"], p0),
                                c_arti_K=(S.kritik(tz["K_hukum"], p0p) if p0p <= S.P0_UST else None))
        else:
            ana = list(kal)
            m["testere"] = None
        m["ana_kumeler"] = [c["temsilci"] for c in ana]
        # S1 K⁺, S7 K_nt, S2 negatif kontrol (olay öncesi)
        m["K_arti"] = [c["temsilci"] for c in ana
                       if self.B[c["temsilci"]]["kapi"][self.B[c["temsilci"]]["secim"]]["pozitif"]["N0"] >= S.N0_POZ_KAPI]
        m["K_nt"] = [c["temsilci"] for c in ana
                     if self.B[c["temsilci"]]["kapi"][self.B[c["temsilci"]]["secim"]]["notr"]["N0"] >= ESIK[19.0]]
        m["S2"] = self.S2_satiri(self._nk_kumeleri(ana, sahte))
        # satır kapıları (kendi K'leri) — yalnız ana durum "devam" iken koşulur; değilse K'ler bilgi
        m["satir_kapilari"] = self.satir_kapilari(hazir, N0)
        m["birimler"] = {u: self.birim_ozeti(u) for u in aday}
        m["uyeler"] = {u: self.birim[u]["uyeler"] for u in self.birim}
        m["olay_grubu"] = {o["id"]: o["grup"] for o in self.liste["olaylar"]}
        m["R_A"] = self.R_A
        m["son_indirme_plani"] = self.son_plani(m) if m["durum"] == "devam" else []
        return m

    def _nk_kumeleri(self, ana, sahte):
        nk = {}
        for c in ana:
            ilk = next(r for r in sahte[c["temsilci"]] if r["j"] == 1)
            if ilk["gecerli"]:
                B = self.B[c["temsilci"]]
                o = self.nk_oyu(B, B["secim"])
                if o is not None:
                    nk[c["temsilci"]] = o
        return nk

    def S2_satiri(self, nk):
        K = len(nk)
        X, Y = sum(r["D"] for r in nk.values()), sum(r["A"] for r in nk.values())
        r = dict(K_nk=K, X_nk=X, Y_nk=Y, kumeler=nk)
        if K < S.K_NT_ALT:
            r["durum"] = "koşulamadı"
            return r
        c = S.kritik(K, 0.5)
        r.update(c=c, dusus=X >= c, artis=Y >= c, p_X=KAPI.binom_ust(X, K, 0.5), p_Y=KAPI.binom_ust(Y, K, 0.5))
        r["durum"] = ("düşüş ve artış" if r["dusus"] and r["artis"] else "düşüş" if r["dusus"] else
                      "artış" if r["artis"] else "eğilim yok")
        return r

    def satir_kapilari(self, hazir, N0):
        out = {}
        tan = dict(S5a=("golge", ESIK[13.0]), S5b=("golge", ESIK[39.0]), D1=("D1", ESIK[19.0]),
                   D3a=("D3a", ESIK[19.0]), D3b=("D3b", ESIK[19.0]), D4=("D4", ESIK[19.0]),
                   D5=("D5", ESIK[19.0]), D8=("D8", ESIK[19.0]))
        for ad, (lob, e) in tan.items():
            g = [u for u in hazir if self.B[u]["secim"] and self.B[u]["kapi"][self.B[u]["secim"]][lob]["N0"] >= e]
            kal, cik, _ = self.kume_seti(g)
            out[ad] = dict(kumeler=[dict(c, katalog=self.B[c["temsilci"]]["secim"]) for c in kal],
                           cikan=cik, K=len(kal))
        # D6: ISC kuralıyla ana hükümden çıkanlar ISC ile eklenir
        ana = [u for u in hazir if self.B[u]["secim"] and N0[u] >= ESIK[19.0]]
        ek = [u for u in hazir if u not in ana and self.birim[u].get("isc_kurali_ile_dusen") and "ISC" in self.B[u]["kapi"]
              and self.B[u]["kapi"]["ISC"]["golge"]["N0"] >= ESIK[19.0]]
        kal, cik, _ = self.kume_seti(ana + ek)
        out["D6"] = dict(kumeler=[dict(c, katalog=("ISC" if c["temsilci"] in ek else self.B[c["temsilci"]]["secim"]))
                                  for c in kal], cikan=cik, K=len(kal), isc_ile_eklenen=ek)
        return out

    def birim_ozeti(self, u):
        B = self.B[u]
        o = dict(durum=B["durum"], neden=B.get("neden"), mekanizma=self.birim[u]["mekanizma_sinif"])
        if B["durum"] != "hazır" and "H" not in B:
            return o
        o.update(ffm=B.get("ffm"), alici=B.get("alici"), hucre=B.get("hucre"), R_sorgu_km=round(B.get("R_sorgu", 0), 1),
                 son_bit=KAT.zaman(B["son_bit"]).isoformat(timespec="seconds") if "son_bit" in B else None,
                 T_son_g=round(B["T_son"], 3) if "T_son" in B else None, pi=B.get("pi"), kesme=B.get("kesme"),
                 bayrak_2L_365=B.get("bayrak_2L_365"), oncul_komsu=B.get("oncul_komsu"), secim=B.get("secim"),
                 kapi=B.get("kapi"),
                 kataloglar={k: dict(mc_halka=x["mc_halka"], taban=x["taban"], sayim_on=x["sayim_on"],
                                     indirme=x.get("indirme")) for k, x in B["kat"].items()})
        return o

    def son_plani(self, m):
        """§9 adım 5: manifestteki bütün kapı kümelerinin (bütün satırların birleşimi) temsilcileri; [t0, son pencere
        sonu). B4 için bilinen sonuçlu (çıkarılan) kümelerin temsilcileri de."""
        gerek = {}
        for c in m["kumeler"]:
            gerek[(c["temsilci"], self.B[c["temsilci"]]["secim"])] = 1
        for c in m["cikan"]:
            if c["neden"].startswith("bilinen"):
                gerek[(c["temsilci"], self.B[c["temsilci"]]["secim"])] = 1
        for ad, r in m["satir_kapilari"].items():
            for c in r["kumeler"]:
                gerek[(c["temsilci"], c["katalog"])] = 1
        plan = []
        for (u, k) in sorted(gerek):
            B = self.B[u]
            plan.append(dict(birim=u, katalog=k, t_bas=KAT.zaman(B["t0"]).isoformat(timespec="milliseconds"),
                             t_bit=KAT.zaman(B["son_bit"]).isoformat(timespec="milliseconds"),
                             taban=B["kat"][k]["taban"], R_km=round(B["R_sorgu"], 3), merkez=[B["la"], B["lo"]]))
        return plan

    # ---------------------------------------------------------------- olay sonrası (yalnız kos aşamasında)
    def son_ekle(self, plan, son_kaynak):
        for p in plan:
            B = self.B[p["birim"]]
            b = self.birim[p["birim"]]
            d = son_kaynak.katalog(b, p["katalog"], dt.datetime.fromisoformat(p["t_bas"]),
                                   dt.datetime.fromisoformat(p["t_bit"]), p["taban"], p["R_km"], tuple(p["merkez"]),
                                   "son")
            E, sayim = self._olaylari_yerlestir(B, d, p["taban"], ana_sok=True)
            if len(E["t"]) and (E["t"].min() < B["t0"] - 1e-9 or E["t"].max() >= B["son_bit"] + 1e-9):
                raise KosuDur(f"{p['birim']}: olay sonrası veri pencere dışı satır taşıyor")
            KK = B["kat"][p["katalog"]]
            KK["E"] = E_birlestir(KK["E"], E)
            KK["sayim_son"] = sayim
        self.son_eklendi = True

    def oylar(self, m):
        """§4.3, §6, §7: bütün satırlar. Yalnız son_ekle'den sonra (kos aşaması)."""
        if not self.son_eklendi:
            raise KosuDur("olay sonrası veri eklenmeden oy sayılamaz")
        p0, p0p = m["sahte"]["p0"], m["sahte"]["p0_arti"]
        mcson = self.mc_son_gercek
        m = self.tamlik_eleme(m)
        if m["durum"] != "devam":
            return dict(m_etkin=m)

        def oy(u, k, lob="golge", tur="gercek", mc_ek=0.0, kumesiz=True, mc_lob_anahtar=None):
            B = self.B[u]
            ms, msb = mcson(u, k)
            if ms is None:                                   # Ek 1 E1.3 (d): satırdan düşer (veri yok)
                return None
            ml = B["kapi"][k][mc_lob_anahtar or lob]["mc_lob"]
            mk = mc_kul(ml, ms, mc_ek)
            r = self.lob_oyu(B, k, lob, self.pencere(B, tur), mk, kumesiz)
            r.update(temsilci=u, katalog=k, mc_lob=ml, mc_son=ms, mc_son_bilgi=msb)
            return r

        ana_c = m["ana_kumeler"]
        sec = {u: self.B[u]["secim"] for u in self.B if self.B[u]["durum"] == "hazır"}
        R = {}
        R["ana"] = [oy(u, sec[u]) for u in ana_c]
        R["B1"] = [oy(c["temsilci"], sec[c["temsilci"]]) for c in m["kumeler"]] if m["testere"]["atilan"] else None
        R["S1"] = [oy(u, sec[u], "pozitif") for u in m["K_arti"]]
        R["S1_bilgi_kapi_disi"] = [oy(u, sec[u], "pozitif") for u in ana_c if u not in m["K_arti"]]
        R["S7"] = [oy(u, sec[u], "notr") for u in m["K_nt"]]
        R["S7_bilgi_kapi_disi"] = [oy(u, sec[u], "notr") for u in ana_c if u not in m["K_nt"]]
        R["S3"] = [r for r in R["ana"] if self.birim[r["temsilci"]]["mekanizma_sinif"] == DOGRULTU_ATIMLI]
        R["S4"] = [r for r in R["ana"] if self.birim[r["temsilci"]]["mekanizma_sinif"] != MEGATHRUST]
        sk = m["satir_kapilari"]
        R["S5a"] = [oy(c["temsilci"], c["katalog"]) for c in sk["S5a"]["kumeler"]]
        R["S5b"] = [oy(c["temsilci"], c["katalog"]) for c in sk["S5b"]["kumeler"]]
        R["D1"] = [oy(c["temsilci"], c["katalog"], mc_ek=0.5) for c in sk["D1"]["kumeler"]]
        R["D2"] = None if self.kural in KAT.GEC_BASLANGIC else [oy(u, sec[u], tur="D2") for u in ana_c]
        for ad in ("D3a", "D3b", "D5", "D8"):
            R[ad] = [oy(c["temsilci"], c["katalog"], lob=ad) for c in sk[ad]["kumeler"]]
        R["D4"] = [oy(c["temsilci"], c["katalog"], kumesiz=False) for c in sk["D4"]["kumeler"]]
        R["D6"] = [oy(c["temsilci"], c["katalog"]) for c in sk["D6"]["kumeler"]]
        R["D7"] = [r for r in R["ana"] if not self._buyuk_on(r["temsilci"], r["katalog"])]
        bilinen = [c for c in m["cikan"] if c["neden"].startswith("bilinen")]
        R["B4_cikan"] = [oy(c["temsilci"], sec[c["temsilci"]]) for c in bilinen]
        for ad, x in list(R.items()):
            if isinstance(x, list):
                R[ad] = [r for r in x if r is not None]
        R["m_etkin"] = m
        return R

    def mc_son_gercek(self, u, k):
        """Gerçek son pencerenin Mc_son'u (yalnız bölge olaylarından; lob sayısı kullanılmaz). Önbellekli."""
        if not hasattr(self, "_mcs"):
            self._mcs = {}
        if (u, k) not in self._mcs:
            B = self.B[u]
            ml = B["kapi"][k]["golge"]["mc_lob"]
            self._mcs[(u, k)] = self.mc_son(B, k, self.pencere(B, "gercek"), ml)
        return self._mcs[(u, k)]

    def tamlik_eleme(self, m):
        """Ek 1 E1.3 (d): olay sonrası veri eklendikten sonra, hiçbir lob sayısı hesaplanmadan, K_kapı kümelerinin
        gerçek son pencere Mc_son'u (bölge olayları) kestirilemiyorsa küme "veri yok (tamlık kestirilemedi)" olur.
        K_kapı bu kümeler düşüldükten sonra yeniden sayılır; < 23 ise "güç yok (tamlık)"; değilse testere dişi aynı p₀
        ile yeniden çözülür, K⁺, K_nt ve S2 yeni ana kümeler üzerinde yeniden kurulur (hepsi olay öncesi sayılar)."""
        import copy
        m2 = copy.deepcopy(m)
        m2["tamlik_eleme"] = []
        if self.kural not in KAT.TAMLIK_VERI_YOK:
            return m2
        dus = [c["temsilci"] for c in m["kumeler"]
               if self.mc_son_gercek(c["temsilci"], self.B[c["temsilci"]]["secim"])[0] is None]
        if not dus:
            return m2
        kal = [c for c in m["kumeler"] if c["temsilci"] not in dus]
        p0, p0p = m["sahte"]["p0"], m["sahte"]["p0_arti"]
        m2.update(tamlik_eleme=dus, kumeler=kal, K_kapi_once=m["K_kapi"], K_kapi=len(kal))
        if len(kal) < S.K_ALT:
            m2["durum"] = "güç yok (tamlık)"
            return m2
        tz = testere(len(kal), p0)
        sira = en_zayif_sirasi(kal, m["kapi_N0"])
        atilan = [c["temsilci"] for c in sira[:tz["atilan"]]]
        ana = [c for c in kal if c["temsilci"] not in atilan]
        m2["testere"] = dict(tz, atilan_kumeler=atilan, c_K=S.kritik(tz["K_hukum"], p0),
                             c_arti_K=(S.kritik(tz["K_hukum"], p0p) if p0p <= S.P0_UST else None))
        m2["ana_kumeler"] = [c["temsilci"] for c in ana]
        kp = lambda u: self.B[u]["kapi"][self.B[u]["secim"]]                      # noqa: E731
        m2["K_arti"] = [c["temsilci"] for c in ana if kp(c["temsilci"])["pozitif"]["N0"] >= S.N0_POZ_KAPI]
        m2["K_nt"] = [c["temsilci"] for c in ana if kp(c["temsilci"])["notr"]["N0"] >= ESIK[19.0]]
        m2["S2"] = json.loads(json_metni(self.S2_satiri(self._nk_kumeleri(ana, m["sahte"]["oylar"]))))
        return m2

    def _buyuk_on(self, u, k):
        """D7: bölgede ön pencerede M ≥ 6,0 (Mc_kul süzgeçsiz, aynı katalog)."""
        B = self.B[u]
        E = B["kat"][k]["E"]
        ev = ev_maske(E, B["M"]["bolge"])
        return bool((ev & (E["t"] >= B["t0"] - ON_A) & (E["t"] < B["t0"] - ON_B) & (E["m"] >= 6.0 - 1e-9)).any())


def r2(x):
    return KAT.r2(x)


def mc_kul(mc_lob, mc_son, ek=0.0):
    """§4.3: Mc_kul = max(Mc_lob, Mc_son) (+ D-satırı eki), iki basamağa yuvarlanmış."""
    return r2(max(mc_lob, mc_son) + ek)


# ================================================================== satır istatistikleri ve hüküm (§6, §7, §8)
def satir_istatistigi(oylar, p0, p0p, A_oyu=False):
    """K, X, Y, X/K, c(K; p₀), c(K; 0,5), üst kuyruk p'leri, koşullu Poisson-binom p (bilgi)."""
    if oylar is None:
        return dict(K=0, kosulamadi=True, neden="satır yok")
    K = len(oylar)
    X = sum(r["A"] if A_oyu else r["D"] for r in oylar)
    Y = sum(r["A"] for r in oylar)
    r = dict(K=K, X=X, Y=Y, X_K=(X / K if K else None), c_p0=kritik(K, p0), c_05=kritik(K, 0.5),
             p_X_p0=ust_kuyruk(X, K, p0), p_X_05=ust_kuyruk(X, K, 0.5),
             p_Y_p0arti=(ust_kuyruk(Y, K, p0p) if p0p <= S.P0_UST else None), p_Y_05=ust_kuyruk(Y, K, 0.5))
    if K:
        ps = [KAT.p_dusus_kosullu(o["n_on"] + o["n_son"], o["pi"]) for o in oylar]
        r["kosullu_p"] = KAT.poisson_binom_ust(X, ps) if not A_oyu else None
    r["kosulamadi"] = K == 0
    return r


def medyan_inf(x):
    x = sorted(x)
    if not x:
        return None
    n = len(x)
    a, b = x[(n - 1) // 2], x[n // 2]
    if math.isinf(a) or math.isinf(b):
        return a if math.isinf(a) else b
    return (a + b) / 2


def spearman(a, b):
    """−∞ en küçük sıra; eşitlikte ortalama sıra."""
    def sira(x):
        x = np.array([(-1e300 if math.isinf(v_) and v_ < 0 else v_) for v_ in x], float)
        o = np.argsort(x, kind="stable")
        r = np.empty(len(x))
        r[o] = np.arange(len(x), dtype=float)
        for u in np.unique(x):
            k = x == u
            r[k] = r[k].mean()
        return r
    if len(a) < 3:
        return None
    ra, rb = sira(a), sira(b)
    if ra.std() == 0 or rb.std() == 0:
        return None
    return float(np.corrcoef(ra, rb)[0, 1])


def mcnemar(golge, notr):
    Dg = {r["temsilci"]: r["D"] for r in golge}
    a = sum(1 for r in notr if Dg[r["temsilci"]] == 1 and r["D"] == 0)
    b = sum(1 for r in notr if Dg[r["temsilci"]] == 0 and r["D"] == 1)
    return dict(a=a, b=b, p=(KAPI.binom_ust(a, a + b, 0.5) if a + b > 0 else 1.0))


def hukum_kur(m, R, analiz=None):
    """§6.1–§6.4 ve §7: satır tablosu, hüküm adı ve cümlesi. R: Analiz.oylar çıktısı."""
    m = R.get("m_etkin", m)
    p0, p0p, J = m["sahte"]["p0"], m["sahte"]["p0_arti"], m["sahte"]["J"]
    T = {}
    for ad in ("ana", "B1", "S3", "S4", "S5a", "S5b", "D1", "D2", "D3a", "D3b", "D4", "D5", "D6", "D7", "D8"):
        T[ad] = satir_istatistigi(R.get(ad), p0, p0p)
    T["S1"] = satir_istatistigi(R["S1"], 0.5, p0p, A_oyu=True)
    T["S7"] = satir_istatistigi(R["S7"], p0, p0p)
    T["S7"]["mcnemar"] = mcnemar(R["ana"], R["S7"]) if R["S7"] else None
    T["S6"] = dict(K=0, kosulamadi=True, neden="SRCMOD erişimi/kapsamı doğrulanmadı (okuma 22): koşulamadı")
    tz = m["testere"]
    K, X, Y = T["ana"]["K"], T["ana"]["X"], T["ana"]["Y"]
    taban, c, h = taban_hukum(K, X, p0)
    # S1
    Kp = T["S1"]["K"]
    S1 = "koşulamadı" if Kp < S.K_POZ_ALT else ("tuttu" if T["S1"]["X"] >= S.kritik(Kp, 0.5) else "tutmadı")
    # S2
    s2 = m["S2"]
    # S7
    Knt = T["S7"]["K"]
    if Knt < S.K_NT_ALT:
        S7 = "koşulamadı"
    elif T["S7"]["X"] >= S.kritik(Knt, p0):
        S7 = "düşüş"
    elif T["S7"]["mcnemar"]["p"] > 0.10:
        S7 = "ayrışmadı"
    else:
        S7 = "ayrıştı"
    # S4 megathrust ağırlığı
    K4, X4 = T["S4"]["K"], T["S4"]["X"]
    S4_dayanir = K4 < 5 or (X4 / K4 <= 0.5)
    # ters yön
    if p0p > S.P0_UST:
        ty = ("sınanamadı", m["sahte"]["p0_arti_sapka"])
    else:
        cp = S.kritik(K, p0p)
        ty = ("not", Y, cp) if Y >= cp else None
    # etkin N0 (§6.2 kural 6)
    az = sum(1 for r in R["ana"] if r["N0_kul"] < ESIK[19.0])
    etkin = (az, K) if az > K / 2 else None
    f = dict(taban=taban, S1=S1, S2_dusus=bool(s2.get("dusus")), S2_artis=bool(s2.get("artis")),
             S2_kosulamadi=s2["durum"] == "koşulamadı", S7=S7, S4_dayanir=S4_dayanir,
             tasarim_alti_guc=(tz["guc"] if tz["tasarim_alti"] else None),
             kalib_zayif=((J, p0) if m["sahte"]["J30_kurali"] else None), ters_yon=ty, etkin_N0=etkin)
    H = hukum_adi(f)
    d = dict(K=K, X=X, c=c, h=h, p0=p0, p=KAPI.binom_ust(X, K, p0))
    # sağlamlık cümlesi (§6.2 kural 4)
    zayif = [ad for ad in ("D1", "D2", "D3a", "D3b", "D4", "D5", "D6", "D7", "D8")
             if T[ad]["K"] and T[ad]["X"] / T[ad]["K"] <= 0.5]
    kos_yok = [ad for ad in ("D1", "D2", "D3a", "D3b", "D4", "D5", "D6", "D7", "D8") if not T[ad]["K"]]
    # B2 büyüklük ölçeri
    B2 = {}
    for lob, ad in (("golge", "ana"), ("pozitif", "S1")):
        rr = R["ana"] if lob == "golge" else (R["S1"] + R["S1_bilgi_kapi_disi"])
        ln = [r["ln_oran"] for r in rr if r["ln_oran"] is not None]
        B2[lob] = {f"Asigma_{a:g}": (None if not ln else (a * medyan_inf(ln))) for a in ASIGMALAR}
        B2[lob]["tanimsiz"] = sum(1 for r in rr if r["ln_oran"] is None)
    if analiz is not None:
        rr = [r for r in (R["S1"] + R["S1_bilgi_kapi_disi"]) if r["ln_oran"] is not None]
        B2["pozitif_spearman"] = spearman([analiz.B[r["temsilci"]]["lob_ortalama_dcff"]["pozitif"] for r in rr],
                                          [S.ASIGMA * r["ln_oran"] for r in rr])
    # B3
    bayrakli = [r for r in R["ana"] if m["birimler"][r["temsilci"]].get("bayrak_2L_365")]
    oncul = [r for r in R["ana"] if m["birimler"][r["temsilci"]].get("oncul_komsu")]
    oncul_yok = [r for r in R["ana"] if r not in oncul]
    temsilciler = {c_["temsilci"] for c_ in m["kumeler"] + m["cikan"]}
    ortusen = []
    for c_ in m["kumeler"] + m["cikan"]:
        ks = m["birimler"][c_["temsilci"]].get("kesme")
        if ks and m["olay_grubu"].get(ks["olay"]) in temsilciler:
            ortusen.append(dict(temsilci=c_["temsilci"], kesme_olayi=ks["olay"],
                                obur_kume=m["olay_grubu"][ks["olay"]]))
    B3 = dict(bayrakli=satir_istatistigi(bayrakli, p0, p0p),
              kesme_ile_cikan=[c_ for c_ in m["cikan"] if c_["neden"].startswith("kısa")],
              ortusen_ciftler=ortusen,
              tek_baglanti_cift=m["tek_baglanti_cift"],
              oncul_komsu=[r["temsilci"] for r in oncul], oncul_cikarilmis=satir_istatistigi(oncul_yok, p0, p0p))
    # B4
    toh = [r for r in R["ana"] if r["temsilci"] in _tohoku_kumeleri(m)]
    B4_set = [r for r in R["ana"] if r not in toh] + R["B4_cikan"]
    B4 = dict(cikan=R["B4_cikan"], tohoku=toh, eklenmis_tohoku_cikarilmis=satir_istatistigi(B4_set, p0, p0p))
    return dict(hukum=H, cumle=hukum_cumlesi(H, d), marmara=marmara_satiri(H), satirlar=T, S2=s2,
                saglamlik_X_K_le_05=zayif, saglamlik_kosulamadi=kos_yok, B2=B2, B3=B3, B4=B4, taban_d=d,
                olgular=f)


def _tohoku_kumeleri(m):
    return {c["temsilci"] for c in m["kumeler"]
            if any(x in S.BILINEN_KALAN for b in c["birimler"] for x in m["uyeler"][b])}


def erken_hukum(tur, m=None, sinama=None):
    """Olay sonrası veri olmadan: koşulmadı (yöntem) / güç yok / güç yok (ölçü yanlı)."""
    if tur == "yontem":
        H = hukum_adi(dict(taban="yontem", yontem=sinama["yontem"]))
        return dict(hukum=H, cumle=hukum_cumlesi(H, dict(yontem=sinama["yontem"], yontem_olcut=sinama["olcut"])),
                    marmara=marmara_satiri(H))
    if tur == "guc_yok":
        H = hukum_adi(dict(taban="guc_yok"))
        return dict(hukum=H, cumle=hukum_cumlesi(H, dict(K_kapi=m["K_kapi"])), marmara=marmara_satiri(H))
    if tur == "guc_yok_tamlik":
        H = hukum_adi(dict(taban="guc_yok_tamlik"))
        return dict(hukum=H, cumle=hukum_cumlesi(H, dict(K_kapi=m["K_kapi"], K_once=m.get("K_kapi_once"),
                                                       dus=len(m.get("tamlik_eleme", [])))),
                    marmara=marmara_satiri(H))
    H = hukum_adi(dict(taban="olcu_yanli"))
    return dict(hukum=H, cumle=hukum_cumlesi(H, dict(p0_sapka=m["sahte"]["p0_sapka"], J=m["sahte"]["J"])),
                marmara=marmara_satiri(H))


# ================================================================== çıktı (§8)
SATIR_SIRASI = ("ana", "S1", "S2", "S7", "S3", "S4", "S5a", "S5b", "S6", "D1", "D2", "D3a", "D3b", "D4", "D5", "D6",
                "D7", "D8", "B1")


def sonuc_md(m, Hk, R, girdi):
    L = ["# TR-6a sonuç", "", f"**Hüküm:** {Hk['hukum']['ad']}", "", Hk["cumle"], "", Hk["marmara"], ""]
    if R is None:
        L += ["Olay sonrası veri indirilmedi; satır tablosu yok.", ""]
    else:
        s = m["sahte"]
        L += [f"Üst bilgi: p̂₀ = {v(s['p0_sapka'])}, p̂₀⁺ = {v(s['p0_arti_sapka'])}, J = {s['J']}, J < 30 kuralı "
              f"{'uygulandı' if s['J30_kurali'] else 'uygulanmadı'}, p₀ = {v(s['p0'], 2)}, p₀⁺ = {v(s['p0_arti'], 2)}, "
              f"testere: K_kapı {m['K_kapi']} → K {m['testere']['K_hukum']} (atılan {m['testere']['atilan']})", "",
              "| Satır | K | X (düşüş) | Y (artış) | X/K | c(K; p₀) | c(K; 0,5) | p (X, p₀) | p (X, 0,5) | p (Y) | "
              "koşullu p (bilgi) | Hüküm / etiket |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        T = Hk["satirlar"]
        for ad in SATIR_SIRASI:
            if ad == "S2":
                s2 = Hk["S2"]
                L.append(f"| S2 negatif kontrol | {s2['K_nk']} | {s2['X_nk']} | {s2['Y_nk']} | | | {s2.get('c', '—')} | | "
                         f"{v(s2.get('p_X'), 4)} | {v(s2.get('p_Y'), 4)} | | {s2['durum']} |")
                continue
            t = T[ad]
            if t.get("kosulamadi"):
                L.append(f"| {ad} | {t['K']} | | | | | | | | | | koşulamadı{(': ' + t['neden']) if t.get('neden') else ''} |")
                continue
            et = Hk["hukum"]["ad"] if ad == "ana" else ""
            if ad == "S1":
                et = Hk["olgular"]["S1"]
            if ad == "S7" and t.get("mcnemar"):
                et = f"McNemar p = {v(t['mcnemar']['p'], 4)}"
            L.append(f"| {ad} | {t['K']} | {t['X']} | {t['Y']} | {v(t['X_K'])} | {t['c_p0']} | {t['c_05']} | "
                     f"{v(t['p_X_p0'], 4)} | {v(t['p_X_05'], 4)} | {v(t['p_Y_p0arti'], 4)} | {v(t.get('kosullu_p'), 4)}"
                     f" | {et} |")
        L += ["", "Sağlamlık (X/K ≤ 0,5): " + (", ".join(Hk["saglamlik_X_K_le_05"]) or "yok") +
              "; koşulamadı: " + (", ".join(Hk["saglamlik_kosulamadi"]) or "yok"), ""]
        L += ["## Küme başına", "", "| Küme | Katalog | Mc_lob | Mc_son | Mc_kul | T_son | π | n_on | n_son | N0_kul | D | A |"
              " Δτ_est (Aσ 19) | Mekanizma |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in R["ana"]:
            u = r["temsilci"]
            dl = None if r["ln_oran"] is None else S.ASIGMA * r["ln_oran"]
            L.append(f"| {u} | {r['katalog']} | {v(r['mc_lob'], 2)} | {v(r['mc_son'], 2)} | {v(r['mc_kul'], 2)} | "
                     f"{m['birimler'][u]['T_son_g']} | {v(r['pi'], 5)} | {r['n_on']} | {r['n_son']} | {v(r['N0_kul'], 2)} "
                     f"| {r['D']} | {r['A']} | {v(dl, 2) if dl is not None else 'tanımsız'} | "
                     f"{m['birimler'][u].get('mekanizma', '')} |")
    L += ["", "## Girdiler (sha256)", ""] + [f"- {k}: {x}" for k, x in sorted(girdi.items())]
    L += ["", "İstanbul ya da Marmara için mutlak olasılık, olasılık çarpanı ya da tarih bu sınavdan yazılmaz (§13).", ""]
    return "\n".join(L)


# ================================================================== gerçek veri kaynakları
class GercekKaynak:
    """Manifest ve son-indir aşamaları için ağ kaynağı. Her istek tarih/aşama denetiminden geçer; yanıtlar ham dizine
    sha256 adıyla yazılır; okuma yalnız KAT.kendi_indirmesini_oku (sha256 doğrulamalı) ile."""

    def __init__(self, ham_dizin, asama, log=print, bekleme=1.0):
        self.ham, self.asama, self.log = ham_dizin, asama, log
        os.makedirs(ham_dizin, exist_ok=True)
        # aynı ham dizinle yeniden çağrılınca (aşamayı bölmek / yarıda kalanı sürdürmek) istekler günlükten okunur
        self.getir = KAT.Getirici(os.path.join(ham_dizin, "yanit"), bekleme=bekleme,
                                  gunluk=os.path.join(ham_dizin, "yanit_gunluk.jsonl"))
        self._kayit_yol = os.path.join(ham_dizin, "kaynak_kayit.json")
        self.kayit = dict(ffm={}, tensor={}, katalog=[])
        if os.path.exists(self._kayit_yol):
            with open(self._kayit_yol, encoding="utf-8") as f:
                self.kayit = json.load(f)

    def _kaydet(self):
        gecici = self._kayit_yol + ".gecici"
        with open(gecici, "w", encoding="utf-8") as f:
            f.write(json_metni(self.kayit))
        os.replace(gecici, self._kayit_yol)

    def _getir_bayt(self, url):
        return self.getir(url)

    def ffm(self, uye):
        if self.asama != "on":
            raise KosuDur("sonlu fay ürünü yalnız manifest aşamasında indirilir")
        if uye not in self.kayit["ffm"]:
            self.kayit["ffm"][uye] = FFM.indir(uye, self.ham, self._getir_bayt)
            self._kaydet()
        return FFM.arsivden_oku(self.kayit["ffm"][uye], self.ham)

    def tensorler(self, b):
        if b["id"] in self.kayit["tensor"]:
            return [tuple(x["tensor"]) for x in self.kayit["tensor"][b["id"]]["tensorler"]]
        t0 = dt.datetime.fromisoformat(b["zaman"])
        KAT.tarih_denetle(dt.datetime(1976, 1, 1), t0 - dt.timedelta(milliseconds=1), t0)
        r1, r2_ = b["L_km"] / 2 + 10.0, 2 * b["L_km"]
        u = KAT.mt_url(b["enlem"], b["boylam"], r1, r2_, t0)
        n0 = len(self.getir.kayitlar)
        js = json.loads(self.getir(u).decode("utf-8"))
        out = []
        ozellik = js.get("features", [])
        if len(ozellik) < 5:
            # §3.3 karar 6 kural 3: 5'ten az tensör -> ana şok düzlemi. Arama yanıtındaki her olayın moment-tensor
            # ürünü var; 5'ten az olayda ayrıntı istemek kararı değiştiremez (Ek 1 E1.4: istek yükü azaltma). Ayrıntılar
            # birimler arasında günlükle (URL) paylaşılır; aynı olay bir kez istenir.
            self.kayit["tensor"][b["id"]] = dict(sorgu=u, tensorler=[], arama_olay_sayisi=len(ozellik),
                                                 istekler=self.getir.kayitlar[n0:])
            self._kaydet()
            return []
        for f in ozellik:
            eid = f.get("id")
            d = json.loads(self.getir(FFM.detay_url(eid)).decode("utf-8"))
            mt = ((d.get("properties") or {}).get("products") or {}).get("moment-tensor") or []
            if not mt:
                continue
            q = mt[0].get("properties") or {}
            try:
                t = tuple(float(q[f"tensor-{c}"]) for c in ("mrr", "mtt", "mpp", "mrt", "mrp", "mtp"))
            except (KeyError, ValueError):
                continue
            out.append(dict(olay=eid, urun=mt[0].get("id"), tensor=t))
        self.kayit["tensor"][b["id"]] = dict(sorgu=u, tensorler=out, istekler=self.getir.kayitlar[n0:])
        self._kaydet()
        return [x["tensor"] for x in out]

    def katalog(self, b, k, t_bas, t_bit, taban, R_km, merkez, asama):
        if asama != self.asama:
            raise KosuDur(f"aşama uyuşmazlığı: {asama} ≠ {self.asama}")
        t0 = dt.datetime.fromisoformat(b["zaman"])
        sinir = t0 - dt.timedelta(days=ON_B) if asama == "on" else t_bit
        if asama == "on" and t_bit > sinir:
            raise KAT.KorIhlal("manifest aşamasında t0 − 30 g sonrası istenemez")
        n0 = len(self.getir.kayitlar)
        r = KAT.parcali_indir(KAT.SERVIS[k], merkez[0], merkez[1], R_km, t_bas, t_bit, taban, self.getir, sinir)
        kay = self.getir.kayitlar[n0:]
        metin = KAT.kendi_indirmesini_oku(os.path.join(self.ham, "yanit"), kay)
        self.kayit["katalog"] = [x for x in self.kayit["katalog"]
                                 if not (x["birim"] == b["id"] and x["katalog"] == k and x["asama"] == asama)]
        self.kayit["katalog"].append(dict(birim=b["id"], katalog=k, asama=asama, t_bas=t_bas.isoformat(),
                                          t_bit=t_bit.isoformat(), taban=taban, R_km=R_km, istek=r["istek"],
                                          bolunen=r["bolunen"], kullanilan=[u_ for u_, _ in r["metinler"]],
                                          kayitlar=[{k_: v_ for k_, v_ in x.items() if k_ != "gunlukten"}
                                                    for x in kay]))
        self._kaydet()
        kull = set(u_ for u_, _ in r["metinler"])
        return KAT.ayristir(k, [(u_, m_) for u_, m_ in metin if u_ in kull])


class ArsivKaynak:
    """kos aşaması: yalnız arşivden (sha256 doğrulamalı) okur; ağ yok."""

    def __init__(self, on_ham, on_kayit, son_ham=None, son_kayit=None):
        self.on_ham, self.on_kayit, self.son_ham, self.son_kayit = on_ham, on_kayit, son_ham, son_kayit

    def ffm(self, uye):
        k = self.on_kayit["ffm"].get(uye)
        if k is None:
            raise FFM.VeriYok("manifestte kayıt yok")
        return FFM.arsivden_oku(k, self.on_ham)

    def tensorler(self, b):
        k = self.on_kayit["tensor"][b["id"]]
        KAT.kendi_indirmesini_oku(os.path.join(self.on_ham, "yanit"), k["istekler"])   # sha256 doğrulaması
        return [tuple(x["tensor"]) for x in k["tensorler"]]

    def katalog(self, b, k, t_bas, t_bit, taban, R_km, merkez, asama):
        ham, kayit = (self.on_ham, self.on_kayit) if asama == "on" else (self.son_ham, self.son_kayit)
        for x in kayit["katalog"]:
            if x["birim"] == b["id"] and x["katalog"] == k and x["asama"] == asama:
                metin = KAT.kendi_indirmesini_oku(os.path.join(ham, "yanit"), x["kayitlar"])
                kull = set(x["kullanilan"])
                return KAT.ayristir(k, [(u_, m_) for u_, m_ in metin if u_ in kull])
        raise KosuDur(f"arşivde katalog kaydı yok: {b['id']} {k} {asama}")


# ================================================================== aşamalar
def asama_sinama_c(a, log=print):
    """TR-6c §C3: Okada (Ek 1 E1.1), yapay katalog sınaması (HUCRELER_C, tohum 20261116, parçalı) ve tamlık sınaması
    (yalnız (d), tohum 20261117). --prova: dondurma öncesi tam ölçekli prova (bağlayıcı olmayan tohum)."""
    import tr6a_yapay as Y
    if sum(map(bool, (a.baglayici, a.gelistirme, a.prova))) != 1:
        raise KosuDur("sinama --tasarim c: --baglayici, --gelistirme ya da --prova'dan tam olarak biri")
    if a.baglayici:
        if os.path.exists(SINAMA_CIKTI):
            raise KosuDur("bağlayıcı sınama çıktısı zaten var; bir kez koşulur (TR-6c §C3)")
        if not a.parca_dizini:
            raise KosuDur("--parca-dizini gerekli (parçalar kesintiden sonra kaldığı yerden sürer)")
        git_denetle([TR6A_ONKAYIT, ONKAYIT] + [os.path.join(BURAYA, k) for k in KOD_DOSYALARI], log)
        if onkayit_uyusmuyor():
            raise KosuDur("ön kayıt gövdelerinin sha256'sı dondurulan değerlerle uyuşmuyor")
        sonuc = Y.baglayici_sinamalar_c(a.parca_dizini, log=log)
        sonuc["kod_sha256"] = kod_sha()
        sonuc["onkayit_sha256"] = dict(tr6a_govde=TR6A_ONKAYIT_SHA, govde=ONKAYIT_SHA, tam=sha256_dosya(ONKAYIT))
        x_yaz(SINAMA_CIKTI, json_metni(sonuc))
        log(f"yazıldı: {SINAMA_CIKTI} (commit + push edilmeden manifest aşaması açılmaz)")
        return 0
    if not a.parca_dizini:
        raise KosuDur("--parca-dizini gerekli")
    hucreler = a.hucreler.split(",") if a.hucreler else list(Y.HUCRELER_C)
    try:
        if a.prova:
            Y.prova_c(a.tohum, a.deneme, hucreler, a.parca_dizini, cikti_dizini=(BURAYA if a.yaz else None), log=log)
        else:
            sonuc = {h: Y.hucre_kos_c(h, a.tohum, a.deneme, a.parca_dizini, log=log) for h in hucreler}
            if a.cikti:
                x_yaz(a.cikti, json_metni(sonuc))
    except ValueError as e:
        raise KosuDur(str(e)) from e
    return 0


def asama_sinama(a, log=print):
    import tr6a_yapay as Y
    if TASARIM == "c":
        return asama_sinama_c(a, log)
    if a.baglayici and a.gelistirme:
        raise KosuDur("--baglayici ve --gelistirme birlikte verilemez")
    if a.baglayici:
        if os.path.exists(SINAMA_CIKTI):
            raise KosuDur("bağlayıcı sınama çıktısı zaten var; her basamak bir kez koşulur (§9 adım 2)")
        # Ek 1 (E1.1–E1.3) sınama ölçütlerini değiştirir: ön kayıt (gövde + Ek 1) commit + push edilmiş olmalı
        git_denetle([ONKAYIT] + [os.path.join(BURAYA, k) for k in KOD_DOSYALARI], log)
        if onkayit_uyusmuyor():
            raise KosuDur("ön kayıt gövdesinin sha256'sı dondurulan değerle uyuşmuyor")
        sonuc = Y.baglayici_sinamalar(log=log)
        sonuc["kod_sha256"] = kod_sha()
        sonuc["onkayit_sha256"] = dict(govde=ONKAYIT_SHA, tam=sha256_dosya(ONKAYIT))
        x_yaz(SINAMA_CIKTI, json_metni(sonuc))
        log(f"yazıldı: {SINAMA_CIKTI} (commit + push edilmeden manifest aşaması açılmaz)")
        return 0
    if not a.gelistirme:
        raise KosuDur("sinama: --baglayici ya da --gelistirme gerekli")
    sonuc = Y.gelistirme_sinamalari(tohum=a.tohum, n=a.deneme, log=log)
    if a.cikti:
        x_yaz(a.cikti, json_metni(sonuc))
    return 0


def sinama_degerlendir(sin):
    """§6.4 madde 1(a): koşulmadı (yöntem) mi? Dönüş (None | dict(yontem, olcut)), tamlık kuralı.
    Okada: Ek 1 E1.1 ölçütü (sin["okada"]["ek1"]["gecti"]) bağlayıcıdır; harfiyen sonuç bilgi olarak kalır."""
    ok = sin["okada"]
    if not ok["gecti"]:
        if OKADA_EK1_KARAR is None:
            raise KosuDur("Okada doğrulaması harfi harfine ölçütlerde tutmadı (sınama 3, 5 uzak alan, 6); kök oturumun "
                          "Ek 1 kararı (OKADA_EK1_KARAR) olmadan manifest aşaması açılmaz (kodlayıcı okuması 3)")
        if OKADA_EK1_KARAR.get("hukum") == "koşulmadı":
            return dict(yontem="Okada sınaması", olcut=OKADA_EK1_KARAR.get("olcut", "")), None
        ek1 = ok.get("ek1")
        if ek1 is None:
            raise KosuDur("sınama çıktısında Ek 1 E1.1 Okada değerlendirmesi yok")
        if not ek1["gecti"]:
            return dict(yontem="Okada sınaması", olcut="Ek 1 E1.1: " + ek1.get("ozet", "")), None
    if not sin["yapay_katalog"]["gecti"]:
        return dict(yontem="yapay katalog sınaması", olcut=sin["yapay_katalog"].get("ozet", "")), None
    kural = sin["tamlik"].get("secilen")
    if kural is None:
        return dict(yontem="tamlık sınaması", olcut=sin["tamlik"].get("ozet", "")), None
    return None, kural


def asama_manifest(a, log=print):
    for y in (MANIFEST, ON_HAM_SHA):
        if os.path.exists(y):
            raise KosuDur(f"{os.path.basename(y)} zaten var (\"x\" kipi)")
    git_denetle([SINAMA_CIKTI, ONKAYIT, LISTE, SAYILAR_JSON] + [os.path.join(BURAYA, k) for k in KOD_DOSYALARI], log)
    if onkayit_uyusmuyor():
        raise KosuDur("ön kayıt gövdesinin (ilk ONKAYIT_GOVDE_BAYT bayt) sha256'sı dondurulan değerle uyuşmuyor")
    sin = json.load(open(SINAMA_CIKTI, encoding="utf-8"))
    kosulmadi, kural = sinama_degerlendir(sin)
    if kosulmadi:
        raise KosuDur(f"§6.4(a): {kosulmadi['yontem']} tutmadı; manifest koşulmaz, `kos` yalnız hüküm yazar")
    liste = liste_oku()
    ham = a.ham_dizin or os.path.join(a.ham_kok, "on_" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    log(f"ham dizin: {ham}")
    kay = GercekKaynak(ham, "on", log=log, bekleme=a.bekleme)
    adaylar = None
    if a.birimler:
        adaylar = [u for u in a.birimler.split(",") if u]
        if not a.yalniz_indir:
            raise KosuDur("--birimler yalnız --yalniz-indir ile (manifest bütün adaylarla kurulur)")
    an = Analiz(liste, kay, kural=kural, log=log, adaylar=adaylar)
    an.hazirla(havuz_R_A=not a.yalniz_indir or adaylar is None)
    an.on_katalog()
    if a.yalniz_indir:
        log(f"yalnız indirme tamam ({len(an.adaylar)} birim); manifest için aynı --ham-dizin ile yeniden çağırın")
        return 0
    an.katalog_secimi()
    m = an.manifest()
    m["ham_dizin"] = ham
    m["on_kayit"] = kay.kayit
    m["girdi"] = dict(onkayit=ONKAYIT_SHA, onkayit_tam=sha256_dosya(ONKAYIT), liste=LISTE_SHA,
                      sayilar_json=SAYILAR_JSON_SHA,
                      sinama=sha256_dosya(SINAMA_CIKTI), kod=kod_sha())
    m["uretim_zamani"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    x_yaz(MANIFEST, json_metni(m))
    satir = sorted({(k["sha256"], k["url"]) for k in kay.getir.kayitlar})
    x_yaz(ON_HAM_SHA, "".join(f"{h}  {u}\n" for h, u in satir))
    log(f"manifest yazıldı: durum {m['durum']}, K_kapı {m['K_kapi']}, p₀ {m['sahte']['p0']}")
    return 0


def asama_son_indir(a, log=print):
    for y in (SON_HAM_SHA, SON_KAYIT):
        if os.path.exists(y):
            raise KosuDur(f"{os.path.basename(y)} zaten var; olay sonrası katalog bir kez indirilir")
    git_denetle([MANIFEST, ON_HAM_SHA, KOD_INCELEME] + [os.path.join(BURAYA, k) for k in KOD_DOSYALARI], log)
    m = json.load(open(MANIFEST, encoding="utf-8"))
    if m["durum"] != "devam":
        raise KosuDur(f"manifest durumu '{m['durum']}': olay sonrası veri indirilmez (§5)")
    liste = liste_oku()
    ham = os.path.join(a.ham_kok, "son_" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    kay = GercekKaynak(ham, "son", log=log, bekleme=a.bekleme)
    birim = {b["id"]: b for b in liste["birimler"]}
    for p in m["son_indirme_plani"]:
        t_bas, t_bit = dt.datetime.fromisoformat(p["t_bas"]), dt.datetime.fromisoformat(p["t_bit"])
        KAT.tarih_denetle(t_bas, t_bit - dt.timedelta(milliseconds=1))
        try:
            kay.katalog(birim[p["birim"]], p["katalog"], t_bas, t_bit, p["taban"], p["R_km"], tuple(p["merkez"]),
                        "son")
        except KAT.VeriYok as e:
            kay.kayit["katalog"].append(dict(birim=p["birim"], katalog=p["katalog"], asama="son", veri_yok=str(e)))
    x_yaz(SON_KAYIT, json_metni(dict(ham_dizin=ham, kayit=kay.kayit, manifest_sha256=sha256_dosya(MANIFEST))))
    satir = sorted({(k["sha256"], k["url"]) for k in kay.getir.kayitlar})
    x_yaz(SON_HAM_SHA, "".join(f"{h}  {u}\n" for h, u in satir))
    log("olay sonrası indirme tamam; tr6a_son_ham_sha256.txt ve tr6a_son_kayit.json commit + push edilmeli")
    return 0


MANIFEST_CEKIRDEK = ("durum", "K_kapi", "kapi_birim", "kumeler", "cikan", "ana_kumeler", "K_arti", "K_nt", "testere",
                     "son_indirme_plani")


def cekirdek(m):
    c = {k: m.get(k) for k in MANIFEST_CEKIRDEK}
    c["sahte"] = {k: m["sahte"][k] for k in ("J", "S", "S_arti", "p0", "p0_arti", "J30_kurali")}
    c["secim"] = {u: x.get("secim") for u, x in m["birimler"].items()}
    c["satir_K"] = {k: x["K"] for k, x in m["satir_kapilari"].items()}
    return json.loads(json_metni(c))


def yapay_son_veri(an, plan, tohum=1):
    """Kuru prova için yapay olay sonrası verisi: birimin ön penceresindeki olayların yer ve büyüklükleri, zamanları
    [t0, son_bit) içinde rastgele. Gerçek olay sonrası verisine dokunmaz."""
    rng = np.random.default_rng(tohum)

    class _K:
        def katalog(self, b, k, t_bas, t_bit, taban, R_km, merkez, asama):
            B = an.B[b["id"]]
            E = B["kat"][k]["E"]
            on = (E["t"] >= B["t0"] - 365) & (E["t"] < B["t0"] - ON_B)
            n = int(on.sum())
            i = rng.integers(0, max(n, 1), n)
            t = np.sort(rng.uniform(B["t0"], B["son_bit"], n))
            return dict(id=[f"y{x}" for x in range(n)], t=t, la=E["la"][on][i] if n else np.zeros(0),
                        lo=E["lo"][on][i] if n else np.zeros(0), de=np.full(n, 10.0),
                        m=E["m"][on][i] if n else np.zeros(0), mtip=np.array(["ml"] * n, dtype=object))
    return _K()


def asama_kos(a, log=print):
    for y in (SONUC_JSON, SONUC_MD):
        if os.path.exists(y):
            raise KosuDur(f"{os.path.basename(y)} zaten var; var olan çıktının üzerine yazılmaz")
    if a.devam:
        return devam(a, log)
    girdi = dict(onkayit=onkayit_govde_sha(), onkayit_tam=sha256_dosya(ONKAYIT), liste=sha256_dosya(LISTE),
                 sayilar_json=sha256_dosya(SAYILAR_JSON),
                 kosu_kodu=sha256_dosya(os.path.abspath(__file__)))
    if onkayit_uyusmuyor():
        raise KosuDur("ön kayıt sha256 uyuşmuyor")
    sin_yol = SINAMA_CIKTI
    git_denetle([sin_yol], log)
    sin = json.load(open(sin_yol, encoding="utf-8"))
    girdi["sinama"] = sha256_dosya(sin_yol)
    kosulmadi, kural = sinama_degerlendir(sin)
    if kosulmadi:
        Hk = erken_hukum("yontem", sinama=kosulmadi)
        return yaz(dict(hukum=Hk, girdi=girdi), sonuc_md(None, Hk, None, girdi), log)
    git_denetle([MANIFEST, ON_HAM_SHA] + [os.path.join(BURAYA, k) for k in KOD_DOSYALARI], log)
    m = json.load(open(MANIFEST, encoding="utf-8"))
    girdi.update(manifest=sha256_dosya(MANIFEST), on_ham_sha=sha256_dosya(ON_HAM_SHA))
    if m["durum"] in ("güç yok", "güç yok (ölçü yanlı)"):
        Hk = erken_hukum("guc_yok" if m["durum"] == "güç yok" else "olcu_yanli", m=m)
        return yaz(dict(hukum=Hk, girdi=girdi, manifest_ozet=cekirdek(m)), sonuc_md(m, Hk, None, girdi), log)
    git_denetle([SON_HAM_SHA, SON_KAYIT, KOD_INCELEME], log)
    sk = json.load(open(SON_KAYIT, encoding="utf-8"))
    girdi.update(son_ham_sha=sha256_dosya(SON_HAM_SHA), son_kayit=sha256_dosya(SON_KAYIT))
    if sk["manifest_sha256"] != girdi["manifest"]:
        raise KosuDur("son kayıt başka bir manifeste ait")
    _ham_listesi_denetle(m["ham_dizin"], ON_HAM_SHA)
    _ham_listesi_denetle(sk["ham_dizin"], SON_HAM_SHA)
    liste = liste_oku()
    kay = ArsivKaynak(m["ham_dizin"], m["on_kayit"], sk["ham_dizin"], sk["kayit"])
    an = Analiz(liste, kay, kural=m["kural"], log=log)
    an.hazirla()
    an.on_katalog()
    an.katalog_secimi()
    m2 = an.manifest()
    if cekirdek(m2) != cekirdek(m):
        raise KosuDur("manifest çekirdeği arşivden yeniden hesaplanınca uyuşmuyor")
    # kuru prova: aynı oy/hüküm/çıktı kodu, yapay olay sonrası verisiyle; dosya yazılmaz
    try:
        import copy
        an_k = copy.deepcopy(an)
        an_k.kaynak = None
        an_k.son_ekle(m["son_indirme_plani"], yapay_son_veri(an_k, m["son_indirme_plani"]))
        Rk = an_k.oylar(m)
        if Rk["m_etkin"]["durum"] == "devam":
            sonuc_md(m, hukum_kur(m, Rk, an_k), Rk, girdi)
        else:
            erken_hukum("guc_yok_tamlik", m=Rk["m_etkin"])
        json_metni(dict(R=Rk))
        del an_k
    except Exception as e:                                         # noqa: BLE001
        raise KosuDur(f"işaret öncesi kuru prova başarısız: {type(e).__name__}: {e}; işaret yazılmadı") from e
    # olay sonrası veri arşivden yüklenir (oy sayılmaz), anlık görüntü + iki işaret
    an.kaynak = None
    eksik = [x for x in sk["kayit"]["katalog"] if x.get("veri_yok")]
    an.son_ekle([p for p in m["son_indirme_plani"]
                 if not any(x["birim"] == p["birim"] and x["katalog"] == p["katalog"] for x in eksik)], kay)
    if eksik:
        raise KosuDur(f"olay sonrası 'veri yok' satırları var ({len(eksik)}); §5 madde 1 kök oturumda karara bağlanmalı")
    an.kaynak = None
    D = dict(an=an, m=m, girdi=girdi)
    anlik = pickle.dumps(D, protocol=4)
    a_sha = hashlib.sha256(anlik).hexdigest()
    with open(os.path.join(a.veri, ANLIK_AD), "xb") as f:
        f.write(anlik)
    isaret = (f"TR-6a olay sonrası oylar sayıldı\nmanifest_sha256 {girdi['manifest']}\nanlik_sha256 {a_sha}\n"
              f"kosu_kodu_sha256 {girdi['kosu_kodu']}\nzaman {dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')}\n")
    for y in (os.path.join(a.veri, ISARET_AD), os.path.join(BURAYA, ISARET_AD)):
        x_yaz(y, isaret)
    log("işaret dosyaları ve anlık görüntü yazıldı; oylar sayılıyor")
    try:
        return _kos_son(D, isaret, log)
    except KosuDur:
        raise
    except Exception as e:                                         # noqa: BLE001
        raise IsaretSonrasiHata(f"{type(e).__name__}: {e}") from e


def _kos_son(D, isaret, log, devam_bilgi=None):
    an, m, girdi = D["an"], D["m"], D["girdi"]
    R = an.oylar(m)
    if R["m_etkin"]["durum"] != "devam":
        Hk = erken_hukum("guc_yok_tamlik", m=R["m_etkin"])
        return yaz(dict(hukum=Hk, girdi=girdi, isaret=isaret, devam=devam_bilgi,
                        tamlik_eleme=R["m_etkin"]["tamlik_eleme"]), sonuc_md(m, Hk, None, girdi), log)
    Hk = hukum_kur(m, R, an)
    sonuc = dict(hukum=Hk, oylar=R, sahte=m["sahte"], testere=m["testere"], girdi=girdi, isaret=isaret,
                 devam=devam_bilgi)
    return yaz(sonuc, sonuc_md(m, Hk, R, girdi), log)


def _ham_listesi_denetle(ham, liste_yol):
    for s in open(liste_yol, encoding="utf-8"):
        h = s.split()[0]
        y = os.path.join(ham, "yanit", h[:2], h + ".txt")
        if sha256_dosya(y) != h:
            raise KosuDur(f"ham dosya sha256 tutmuyor: {h[:12]}")


def devam(a, log):
    yv, yd = os.path.join(a.veri, ISARET_AD), os.path.join(BURAYA, ISARET_AD)
    if not (os.path.exists(yv) and os.path.exists(yd)):
        raise KosuDur("--devam: iki işaret dosyası da var olmalı")
    metin = open(yd, encoding="utf-8").read()
    if open(yv, encoding="utf-8").read() != metin:
        raise KosuDur("--devam: iki işaret dosyası farklı")
    alan = dict(s.split(" ", 1) for s in metin.splitlines()[1:] if " " in s)
    b = open(os.path.join(a.veri, ANLIK_AD), "rb").read()
    if hashlib.sha256(b).hexdigest() != alan.get("anlik_sha256"):
        raise KosuDur("--devam: anlık görüntü sha256 uyuşmuyor")
    if sha256_dosya(MANIFEST) != alan.get("manifest_sha256"):
        raise KosuDur("--devam: manifest sha256 uyuşmuyor")
    D = pickle.loads(b)
    bilgi = dict(neden="işaret sonrası istisna; yalnız doğrudan nedeni düzeltildi (§9 adım 6)",
                 kod_isaret=alan.get("kosu_kodu_sha256"), kod_devam=sha256_dosya(os.path.abspath(__file__)))
    try:
        return _kos_son(D, metin, log, bilgi)
    except KosuDur:
        raise
    except Exception as e:                                         # noqa: BLE001
        raise IsaretSonrasiHata(f"{type(e).__name__}: {e}") from e


def yaz(sonuc, md, log):
    j = json_metni(sonuc)
    x_yaz(SONUC_JSON, j)
    x_yaz(SONUC_MD, md)
    log(f"yazıldı: {SONUC_JSON}, {SONUC_MD}; hüküm: {sonuc['hukum']['hukum']['ad']}")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--tasarim", choices=("a", "c"), default="a",
                   help="a: TR-6a (varsayılan, değişmez); c: TR-6c fark belgesi (yollar tr6c_*, tamlık kuralı (d))")
    alt = p.add_subparsers(dest="asama", required=True)
    s1 = alt.add_parser("sinama")
    s1.add_argument("--baglayici", action="store_true")
    s1.add_argument("--gelistirme", action="store_true")
    s1.add_argument("--tohum", type=int, default=7)
    s1.add_argument("--deneme", type=int, default=400)
    s1.add_argument("--cikti")
    s1.add_argument("--prova", action="store_true", help="--tasarim c: dondurma öncesi tam ölçekli prova")
    s1.add_argument("--hucreler", help="--tasarim c: virgülle hücreler (ör. i:500,ii:4500,adim:31.36)")
    s1.add_argument("--parca-dizini", help="--tasarim c: parça dosyalarının dizini")
    s1.add_argument("--yaz", action="store_true", help="--prova: tr6c_prova_<hücre>.json'u kod dizinine yaz")
    s2 = alt.add_parser("manifest")
    s2.add_argument("--ham-kok", default=HAM_KOK)
    s2.add_argument("--ham-dizin", help="var olan ön ham dizini (yarıda kalanı sürdürmek / bölünmüş indirme)")
    s2.add_argument("--yalniz-indir", action="store_true", help="indir, manifest yazma (aşamayı bölmek için)")
    s2.add_argument("--birimler", help="--yalniz-indir ile: virgülle ayrılmış birim kimlikleri")
    s2.add_argument("--bekleme", type=float, default=1.0)
    s3 = alt.add_parser("son-indir")
    s3.add_argument("--ham-kok", default=HAM_KOK)
    s3.add_argument("--bekleme", type=float, default=1.0)
    s4 = alt.add_parser("kos")
    s4.add_argument("--veri", default=HAM_KOK)
    s4.add_argument("--devam", action="store_true")
    a = p.parse_args(argv)
    tasarim_sec(a.tasarim)
    try:
        return dict(sinama=asama_sinama, manifest=asama_manifest, kos=asama_kos)[a.asama](a) \
            if a.asama != "son-indir" else asama_son_indir(a)
    except KosuDur as e:
        print(f"DURDU (KosuDur): {e}", file=sys.stderr)
        return 2
    except IsaretSonrasiHata as e:
        print(f"İŞARET SONRASI İSTİSNA: {e}; yalnız doğrudan nedeni düzeltip --devam", file=sys.stderr)
        return 4


if __name__ == "__main__":
    sys.exit(main())
