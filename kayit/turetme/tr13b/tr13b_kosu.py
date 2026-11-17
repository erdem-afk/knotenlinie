#!/usr/bin/env python3
"""TR-13b sınırlı koşu betiği (ön kayıt sürüm 3; INCELEME-2 D-1…D-5). TEK KOŞU İÇİNDİR.

Gerçek kip yalnız ön kaydın "Durum:" satırı DONDURULDU içerdiğinde ve bu betiğin, tr13_guc.py'nin ve tr13_sayim.py'nin
sha256'ları ön kayıtta yazılı olduğunda çalışır. Yapay sınama `tr13b_test_yapay.py` bu modülü içe aktarıp sahte
arşivle (`kos(ayar, yollar, gercek=False)`) çağırır; gerçek arşivde ölçü hesaplayan hiçbir sınama yoktur.

Aşamalar (sıra sabit; her aşamanın sonucu durum dosyasına yazılır, koşu kesilirse kaldığı yerden sürer):
  1 girdi   : iki ham arşivin sha256'sı `tr13_ham_sha256.txt` ile; arşivler bilinen adlarıyla doğrudan açılır
              (dizin taranmaz), gereken üyeler belleğe okunur (diske açılmaz). Uyuşmazlık -> dal 1 (veri yok).
  2 hazırlık: olay başına yalnız SAYI: ortak Mc_b = max(Mc_önce, Mc_ref) (tr13_tamsayim.json'dan, TR-13 Ek 1),
              m >= Mc_b ile GK74 (indirilen bütün daire), önce-pencere [t-3y, t) arka plan sayısı N; N > 100 iken
              Mc_b += 0,1 ve GK74 yeniden; N < 50 -> olay düşer; referans [t-10y, t-3y) arka planı < N + 5 -> düşer;
              arşivde parça eksik -> olay düşer (veri yok). Küme kalan üyeyle sürer, boşalırsa düşer.
              Keşif dışı küme sayısı < 8 -> dal 1 (veri yok).
  3 sıfır   : olay x dallanma (0,4 / 0,6 / 0,8) başına μ kalibrasyonu kendi R'de (40 + 40 deneme, iki adım), sonra
              TAM 2000 yapay ETAS bölgesi (tohum 20261201 + 1000 x olay sırası + dallanma sırası; 4 parça, parça p'nin
              tohumu SeedSequence(tohum, spawn_key=(p,))). Havuzun ortalama N'si N'nin ±%5'i dışında -> kalibrasyon
              bir kez yinelenir (μ x N / ort, havuz yeni tohumla yeniden), yine dışında -> dal 2 (geçersiz).
  4 D-3     : yapay veri (her olayın R ve N'si, dallanma 0,6, ayrı kalibrasyon): sinyalsiz ve f = 0,2…0,6 havuzları;
              R0'ın yanlış alarmı > 0,05 ya da f = 0,4'te gücü < 0,65 -> dal 2 (geçersiz). Aynı havuzlardan MDE
              (güç 0,8) yeniden hesaplanır; yalnız cümledeki sayıyı belirler. GERÇEK z BU AŞAMADAN ÖNCE HESAPLANMAZ.
  5 ölçü    : gerçek z ve z_p (5 km hücre, V(0,5), referanstan 200 alt örnek; tohum 20261201 + 1000 i + 50).
              Sonuç `gercek_z.json` dosyasına bir kez yazılır.
  6 hüküm   : T1 (küme ortalaması, 200 000 çekiliş, tohum 20260900 + dallanma sırası), R0, bilgi satırları;
              `tr13b_hukum.json` bir kez yazılır ("x" kipi). Dosya varsa betik hiçbir şey hesaplamadan durur.

Kullanım (python3 -I -B):
  tr13b_kosu.py bicim     arşivlerin sha256'sı ve üye/biçim denetimi (ölçü yok, sayı yok)
  tr13b_kosu.py kos       gerçek koşu (yalnız dondurulmuş ön kayıtla)
  tr13b_kosu.py durum     durum dosyasını yazdırır
"""
import dataclasses
import hashlib
import io
import itertools
import json
import math
import multiprocessing as mp
import os
import re
import sys
import tarfile
import time

import numpy as np

sys.dont_write_bytecode = True
BURA = os.path.dirname(os.path.abspath(__file__))
DEPO = os.path.abspath(os.path.join(BURA, "..", "..", ".."))
sys.path.insert(0, os.path.join(BURA, "..", "tr13"))
import tr13_guc as G  # noqa: E402
import tr13_sayim as T  # noqa: E402

# ------------------------------------------------------------------ sabitler (ön kayıt sürüm 3)
YIL = G.YIL                     # gün
YIL_MS, GUN_MS = T.YIL_MS, T.GUN_MS
KESIF = (397, 979, 395)
DALLANMA = (0.4, 0.6, 0.8)
HAVUZ = 2000
PARCA = 4
KAL_DENEME = 40
TOL_KAL = 0.05
B_REF = 200
Q_V = 0.5
NS_T1 = 200000
ALFA = 0.05
SINIRDA = 0.03
N_ALT, N_UST = 50, 100
KD_MIN = 8
D3_FA_UST, D3_GUC_ALT, D3_F = 0.05, 0.65, 0.4
D3_N0, D3_NF, D3_NB = 200, 150, 20000
D3_FLIST = (0.2, 0.3, 0.4, 0.5, 0.6)
TOHUM0 = 20261201
TOHUM_T1 = 20260900
TOHUM_D3 = 20260999
MDE_ONKAYIT = "f ≈ 0,40 (bileşim, kendi R'de kalibrasyon; INCELEME-2)"

ARSIV_DIZIN = "/mnt/project-files/turetme/tr13-ham/"
SHA_LISTE = os.path.join(DEPO, "kayit", "turetme", "tr13", "tr13_ham_sha256.txt")
TAMSAYIM = os.path.join(DEPO, "kayit", "turetme", "tr13", "tr13_tamsayim.json")
CIKTI = os.path.join(DEPO, "kayit", "turetme", "tr13b", "kosu")
ONKAYIT = os.path.join(DEPO, "kayit", "onkayit", "TR-13b_sinirli-kosu_ONKAYIT.md")


def tohum_havuz(i, di, deneme=0):
    return TOHUM0 + 1000 * i + di + 20 * deneme          # deneme 1 = ±%5 yinelemesi


def tohum_kal(i, di):
    return TOHUM0 + 1000 * i + 10 + di


def tohum_veri_kal(i):
    return TOHUM0 + 1000 * i + 40


def tohum_olcu(i):
    return TOHUM0 + 1000 * i + 50


def tohum_veri(i, k):
    return TOHUM0 + 1000 * i + 60 + k                    # k = 0 sinyalsiz, 1.. D3_FLIST sırası


@dataclasses.dataclass(frozen=True)
class Ayar:
    havuz: int = HAVUZ
    parca: int = PARCA
    kal_deneme: int = KAL_DENEME
    b_ref: int = B_REF
    ns_t1: int = NS_T1
    d3_n0: int = D3_N0
    d3_nf: int = D3_NF
    d3_nb: int = D3_NB
    cekirdek: int = 4
    test_nh_carpan: float = 1.0       # yalnız yapay sınama: kalibre μ'yü bozar (dal 2 sınaması)
    test_d3_sinyal0: float = 0.0      # yalnız yapay sınama: D-3'ün "sinyalsiz" havuzuna sinyal koyar


@dataclasses.dataclass(frozen=True)
class Yollar:
    arsiv_dizin: str = ARSIV_DIZIN
    sha_liste: str = SHA_LISTE
    tamsayim: str = TAMSAYIM
    cikti: str = CIKTI


def sha256(yol):
    h = hashlib.sha256()
    with open(yol, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def yaz_json(yol, d, kip="w"):
    if kip == "x":
        with open(yol, "x") as f:
            json.dump(d, f, indent=1, ensure_ascii=False, default=float)
        return
    tmp = yol + ".tmp"
    with open(tmp, "w") as f:
        json.dump(d, f, indent=1, ensure_ascii=False, default=float)
    os.replace(tmp, yol)


# ------------------------------------------------------------------ aşama 1: girdi
def sha_listesi(yol):
    """tr13_ham_sha256.txt: 'Arşiv: <yol> (...)' satırını izleyen 'sha256 <hex>'. Dönüş: [(dosya adı, hex)]."""
    metin = open(yol, encoding="utf-8").read()
    return [(os.path.basename(a), h) for a, h in
            re.findall(r"Arşiv: (\S+\.tar\.gz) \([^)]*\)\s*\n\s*sha256 ([0-9a-f]{64})", metin)]


def sha_denetimi(yollar):
    L = sha_listesi(yollar.sha_liste)
    sonuc, tamam = [], len(L) == 2
    for ad, h in L:
        yol = yollar.arsiv_dizin + ad                     # yol sonuna eğik çizgi; dizin taranmaz
        g = sha256(yol) if os.path.isfile(yol) else None
        sonuc.append(dict(arsiv=ad, beklenen=h, bulunan=g, uyusuyor=(g == h)))
        tamam = tamam and g == h
    return tamam, sonuc


def ana_liste(tamsayim):
    """Ön kayıt §2: M >= 6,5 ve ref_gecer[0,3]; tamsayim.json sırasıyla (olay sırası i bu sıradır)."""
    S = json.load(open(tamsayim))["satir"]
    return [s for s in S if s["M"] >= 6.5 and s["ref_gecer"]["0.3"]]


def uye_adlari(s):
    if s["katalog"] == "ComCat":
        return [f"ham/kat_ComCat_{s['id']}.npz"], []
    srv = s["katalog"]
    return [f"ham/tam3_{srv}_{s['id']}.npz"], [f"ham_tam/parca_{srv}_{s['id']}_{j:02d}.npz" for j in range(3, 10)]


def arsiv_oku(yol, adlar):
    """Gereken üyeleri belleğe okur (npz: allow_pickle=False; json). Dönüş: ad -> içerik."""
    adlar, out = set(adlar), {}
    with tarfile.open(yol, "r:gz") as tf:
        for m in tf:
            if m.name in adlar and m.isfile():
                b = tf.extractfile(m).read()
                if m.name.endswith(".json"):
                    out[m.name] = json.loads(b.decode("utf-8"))
                else:
                    with np.load(io.BytesIO(b), allow_pickle=False) as z:
                        out[m.name] = {k: np.asarray(z[k]) for k in z.files}
    return out


def girdi(yollar):
    L = ana_liste(yollar.tamsayim)
    adlar = [a for a, _ in sha_listesi(yollar.sha_liste)]
    gerek1 = {"ham/sayim_tam_satirlar.json"}
    gerek2 = set()
    for s in L:
        a, b = uye_adlari(s)
        gerek1.update(a)
        gerek2.update(b)
    A = {}
    A.update(arsiv_oku(yollar.arsiv_dizin + adlar[0], gerek1))
    A.update(arsiv_oku(yollar.arsiv_dizin + adlar[1], gerek2))
    s4 = {z["id"]: z for z in A["ham/sayim_tam_satirlar.json"]["satir"]}
    return L, s4, A


def katalog(s, A):
    """Olayın [t-10y, t) kataloğu (indirilen bütün daire). Eksik parça -> None."""
    a, b = uye_adlari(s)
    if any(x not in A for x in a + b):
        return None
    d = T.birlestir([A[x] for x in a + b])
    return {k: np.asarray(d[k], float) for k in ("t", "la", "lo", "de", "m")}


# ------------------------------------------------------------------ yerel düzlem
def izdusum(la0, lo0, la, lo):
    """Dış merkezli eşuzaklık izdüşümü (km): x doğu, y kuzey; uzaklık T.uzak ile aynı."""
    r = T.uzak(la0, lo0, la, lo)
    p1, p2 = math.radians(la0), np.radians(la)
    dl = np.radians(lo - lo0)
    az = np.arctan2(np.sin(dl) * np.cos(p2), math.cos(p1) * np.sin(p2) - math.sin(p1) * np.cos(p2) * np.cos(dl))
    return r * np.sin(az), r * np.cos(az)


# ------------------------------------------------------------------ aşama 2: hazırlık (yalnız sayı)
def hazirla(s, o, d):
    """Dönüş: (özet dict, bg olayları (x, y, t_gün) ya da None). Ölçü (V, z) hesaplamaz."""
    oz = dict(id=s["id"], yer=s["yer"], kume=s["kume"], R=s["R_km"], katalog=s["katalog"])
    if d is None:
        oz["durum"] = "düşer: arşivde parça eksik (veri yok)"
        return oz, None
    t_ana = float(o["t"])
    t0 = t_ana - 10 * YIL_MS
    sec = (d["t"] >= t0) & (d["t"] < t_ana) & (d["t"] < T.KOR_MS) & (d["de"] <= T.DERIN_MAX + 10)
    t, la, lo, m = d["t"][sec], d["la"][sec], d["lo"][sec], d["m"][sec]
    r = T.uzak(o["enlem"], o["boylam"], la, lo)
    mc0, mcr = float(s["mc_once"]), float(s["ref_tam"]["mc"])
    mc = max(mc0, mcr)
    oz.update(mc_once=mc0, mc_ref=mcr, mc_ortak=mc)
    while True:
        ust = m >= mc - 1e-6
        bg = T.gk74(t[ust], la[ust], lo[ust], m[ust])
        tt, ic = t[ust], r[ust] <= s["R_km"]
        N = int((ic & bg & (tt >= t_ana - 3 * YIL_MS)).sum())
        if N > N_UST:
            mc = round(mc + 0.1, 2)
            continue
        break
    oz.update(mc_son=mc, mc_artis=round(mc - mc0, 2), N3bg=N)
    b = ic & bg
    Nref = int((b & (tt < t_ana - 3 * YIL_MS)).sum())
    Np = int((b & (tt >= t_ana - 6 * YIL_MS) & (tt < t_ana - 3 * YIL_MS)).sum())
    Npref = int((b & (tt < t_ana - 6 * YIL_MS)).sum())
    oz.update(N_ref=Nref, N_plasebo=Np, N_plasebo_ref=Npref)
    # Ö-a: referans penceresindeki en büyük olay (indirilen daire, derinlik süzgeçli)
    w = t < t_ana - 3 * YIL_MS
    if w.any():
        k = int(np.argmax(np.where(w, m, -9)))
        oz["ref_en_buyuk"] = dict(M=round(float(m[k]), 2), uzaklik_km=round(float(r[k]), 1),
                                  zaman=T.iso(int(t[k]))[:10])
    if N < N_ALT:
        oz["durum"] = f"düşer: N3bg {N} < {N_ALT}"
        return oz, None
    if Nref < N + 5:
        oz["durum"] = f"düşer: referans arka planı {Nref} < N + 5"
        return oz, None
    oz["durum"] = "tamam"
    x, y = izdusum(o["enlem"], o["boylam"], la[ust][b], lo[ust][b])
    tg = (tt[b] - (t_ana - 10 * YIL_MS)) / GUN_MS
    return oz, (x, y, tg)


def kume_yapisi(uyeler):
    """uyeler: [(i, kume)]. Dönüş: (kümeler [[i,...]], küme kimlikleri, keşif dışı sütunlar)."""
    kids = sorted({k for _, k in uyeler})
    kum = [[i for i, k in uyeler if k == kk] for kk in kids]
    kd = [j for j, kk in enumerate(kids) if kk not in KESIF]
    return kum, kids, kd


# ------------------------------------------------------------------ yapay ETAS bölgesi
def dallanma(n):
    G.DAL = n
    G.K_VERIM = G.verim_sabiti()


def z_guvenli(rng, x, y, t, R, a0, a1, r0, g, ic, b_ref):
    """G.z_olcu; tr13_guc.V_q'nun çok küçük n'de (büyük ETAS olayının GK74 penceresi önce-pencereyi boşaltınca)
    verdiği IndexError -> z = NaN (bölge havuzdan, üye listeden düşer). tr13_guc.py değiştirilmez."""
    try:
        return G.z_olcu(rng, x, y, t, R, a0, a1, r0, Q_V, g, ic, b_ref)
    except IndexError:
        return np.nan, -1


def yapay_bolge(rng, Nh, R, f=0.0, b_ref=B_REF, olc=True):
    """(z, z_p, N): önce [7, 10) y, referans [0, 7) y; plasebo önce [4, 7) y, referans [0, 4) y."""
    F = G.faylar(rng, R)
    R_sim = R + 30
    mu = Nh / (3 * YIL) * (R_sim / R) ** 2
    t, x, y, m, _ = G.etas(rng, R_sim, mu, -5 * YIL, 10 * YIL, F, f_lok=f, lok_t0=7 * YIL)
    bg = G.gk74_xy(t, x, y, m)
    tt, xx, yy = t[bg], x[bg], y[bg]
    n = int(((tt >= 7 * YIL) & (tt < 10 * YIL) & (np.hypot(xx, yy) <= R)).sum())
    if not olc:
        return np.nan, np.nan, n
    g, ic = G.izgara(R)
    ze, _ = z_guvenli(rng, xx, yy, tt, R, 7 * YIL, 10 * YIL, 0.0, g, ic, b_ref)
    zp, _ = z_guvenli(rng, xx, yy, tt, R, 4 * YIL, 7 * YIL, 0.0, g, ic, b_ref)
    return ze, zp, n


def ortalama_n(rng, Nh, R, deneme):
    return float(np.mean([yapay_bolge(rng, Nh, R, 0.0, olc=False)[2] for _ in range(deneme)]))


def kalibre(rng, N, R, deneme):
    """İki adım: μ(N) -> ort. n1 -> Nh1 = N²/n1 -> ort. n2 -> Nh2 = Nh1 N / n2. Kendi R'de."""
    n1 = ortalama_n(rng, N, R, deneme)
    Nh1 = N * N / max(n1, 1.0)
    n2 = ortalama_n(rng, Nh1, R, deneme)
    return dict(Nh=Nh1 * N / max(n2, 1.0), n1=n1, n2=n2)


def kal_tamam(ort_n, N):
    return abs(ort_n / N - 1.0) <= TOL_KAL


def _is_kal(a):
    tohum, R, N, dal, deneme = a
    dallanma(dal)
    return kalibre(np.random.default_rng(tohum), N, R, deneme)


def _is_havuz(a):
    anahtar, tohum, p, R, Nh, dal, f, n, b_ref = a
    dallanma(dal)
    rng = np.random.default_rng(np.random.SeedSequence(tohum, spawn_key=(p,)))
    return anahtar, p, np.array([yapay_bolge(rng, Nh, R, f, b_ref) for _ in range(n)], float).reshape(-1, 3)


def parca_boylari(n, parca):
    return [n // parca + (1 if p < n % parca else 0) for p in range(parca)]


# ------------------------------------------------------------------ sınama
def kume_ort(z_uye, kumeler):
    """Küme z = üyelerin ortalaması; z̄ = küme z'lerinin ortalaması."""
    return float(np.mean([np.mean([z_uye[u] for u in k]) for k in kumeler]))


def sifir_cekilis(rng, havuzlar, kumeler, nb):
    """Küme yapılı sıfır çekilişi: (nb, küme sayısı, 2) -> [..., 0] z, [..., 1] z_p (aynı bölge)."""
    out = np.zeros((nb, len(kumeler), 2))
    for j, k in enumerate(kumeler):
        for u in k:
            h = havuzlar[u]
            out[:, j, :] += h[rng.integers(0, len(h), nb)][:, :2]
        out[:, j, :] /= len(k)
    return out


def sonlu(h):
    """Plasebo satırı için: z ve z_p'si tanımlı, önce-pencere N >= 50 bölgeler."""
    h = np.asarray(h, float)
    return h[np.isfinite(h[:, 0]) & np.isfinite(h[:, 1]) & (h[:, 2] >= N_ALT)]


def sonlu_z(h):
    """T1/R0 sıfırı ve D-3 verisi için, gerçek üyenin seçimiyle aynı şart: z tanımlı ve önce-pencere N >= 50
    (kod incelemesi, 17 Kasım 2026). Gerçek üyede z_p şartı olmadığından sıfırda da yoktur: z_p şartı sıfırın sol
    kuyruğunu kesip "VAR" yönüne yanlılık üretiyordu; N >= 50 şartı gerçek üye N3bg >= 50 ile girdiği için konur."""
    h = np.asarray(h, float)
    return h[np.isfinite(h[:, 0]) & (h[:, 2] >= N_ALT)]


def p_deger(sifir, gozlenen):
    """Tek yanlı (yerelleşme = z küçük): P(z̄_sıfır <= z̄_gözlenen)."""
    return float(np.mean(sifir <= gozlenen))


def p_vektor(sifir_sirali, z):
    return np.searchsorted(sifir_sirali, z, side="right") / len(sifir_sirali)


def karar(p_a, p_k):
    """R0: üç dallanmanın üçünde de bütün listede p <= 0,05 VE üçünde de keşif dışı listede p <= 0,05."""
    return all(p_a[d] <= ALFA for d in DALLANMA) and all(p_k[d] <= ALFA for d in DALLANMA)


def hukum_kur(p_a, p_k, p_pl, K_kd, mde_m):
    """Dal 3 / dal 5. p_plasebo hükmü değiştirmez; yalnız VAR cümlesine uyarı ekler (§3.8, §7.3)."""
    if karar(p_a, p_k):
        return 3, "VAR", cumle_var(K_kd, p_pl)
    return 5, "ayırt edilemez", cumle_ayirt(K_kd, mde_m)


def d3_gecer(fa, guc_f04):
    """D-3: sinyalsiz yapayda R0 yanlış alarmı <= 0,05 ve f = 0,4'te güç >= 0,65."""
    return bool(fa <= D3_FA_UST and guc_f04 >= D3_GUC_ALT)


def r0_oran(Sa, Sk, Va, Vk):
    """Sa/Sk: dallanma -> sıralı sıfır z̄ (bütün / keşif dışı); Va/Vk: veri çekilişlerinin z̄'leri. R0 red oranı."""
    red = np.ones(len(Va), bool)
    for d in DALLANMA:
        red &= (p_vektor(Sa[d], Va) <= ALFA) & (p_vektor(Sk[d], Vk) <= ALFA)
    return float(red.mean())


def mde(fs, gs, hedef=0.8):
    for i in range(1, len(fs)):
        if gs[i] >= hedef:
            return round(fs[i - 1] + (hedef - gs[i - 1]) * (fs[i] - fs[i - 1]) / max(gs[i] - gs[i - 1], 1e-9), 3)
    return None


def isaret_p(d):
    d = np.asarray(d, float)
    if len(d) == 0:
        return None
    if len(d) <= 20:
        s = np.array(list(itertools.product((1, -1), repeat=len(d))), float)
    else:
        s = np.random.default_rng(TOHUM_T1 + 7).choice((1.0, -1.0), (200000, len(d)))
    return float(((s * np.abs(d)).sum(1) <= d.sum() + 1e-12).mean())


def binom_p(k, n, p0=0.05):
    return float(sum(math.comb(n, i) * p0 ** i * (1 - p0) ** (n - i) for i in range(k, n + 1)))


def mde_metni(v):
    if v is None:
        return "f > 0,6 (benzetim aralığında güç 0,8'e ulaşılmadı)"
    return "f ≈ " + f"{v:.2f}".replace(".", ",")


def cumle_var(K_kd, p_pl):
    c = (f"BZ20'nin keşif olayları dışındaki K = {K_kd} bölgede, ana şoktan önceki 3 yılda kümesizleştirilmiş arka "
         "plan, ETAS'ın ürettiğinden belirgin biçimde yerelleşmiş. Tahmin ya da alarm iddiası değildir; ileriye "
         "dönük sınav ayrı ön kayıt ister.")
    if p_pl is not None and p_pl <= ALFA:
        c += (f" Aynı bölgelerin 3 yıl önceki penceresi de ETAS'a göre yerelleşmiş görünüyor (p = {p_pl:.3f}); "
              "sonuç ETAS dışı durağan bir bozulmadan ayrılamıyor.")
    return c


def cumle_ayirt(K_kd, mde_m):
    return (f"Keşif dışı K = {K_kd}; bu bileşimle görülebilir en küçük etki {mde_m} (koşudan önce, listenin gerçek "
            "R ve N3bg'siyle yapayda yeniden hesaplanan değer). Daha küçük yerelleşme hakkında bilgi yok.")


# ------------------------------------------------------------------ çalıştırma yardımcıları
def _yaz_hukum(dizin, h):
    yaz_json(os.path.join(dizin, "tr13b_hukum.json"), h, kip="x")
    return h


def havuz_nitelik(P):
    """Bilgi: sıfır havuzunda tanımsız z payı ve N < 50 bölge payı (gerçek üyede N >= 50 şartı var)."""
    return {f"{i}_{DALLANMA[di]}": dict(n=int(len(h)), z_tanimsiz=float(np.mean(~np.isfinite(h[:, 0]))),
                                         zp_tanimsiz=float(np.mean(~np.isfinite(h[:, 1]))),
                                         N_50_alti=float(np.mean(h[:, 2] < N_ALT)), N_ort=float(np.mean(h[:, 2])))
            for (i, di), h in P.items()}


def kod_sha():
    return dict(tr13b_kosu=sha256(os.path.abspath(__file__)), tr13_guc=sha256(G.__file__),
                tr13_sayim=sha256(T.__file__))


def havuz_yolu(dizin, ad, p):
    return os.path.join(dizin, "havuz", f"{ad}_p{p}.npy")


def havuzlari_kos(ayar, dizin, isler, havuz_ici):
    """isler: [(ad, tohum, R, Nh, dal, f, n)]. Parçalar ayrı dosyalara yazılır; var olan parça yeniden koşulmaz."""
    gen = []
    for ad, tohum, R, Nh, dal, f, n, parca in isler:
        for p, k in enumerate(parca_boylari(n, parca)):
            if not os.path.exists(havuz_yolu(dizin, ad, p)):
                gen.append((ad, tohum, p, R, Nh, dal, f, k, ayar.b_ref))
    gen.sort(key=lambda a: -a[3])                         # büyük R önce (yük dengesi)
    for ad, p, arr in havuz_ici.imap_unordered(_is_havuz, gen, chunksize=1):
        tmp = havuz_yolu(dizin, ad, p) + ".tmp.npy"
        np.save(tmp, arr)
        os.replace(tmp, havuz_yolu(dizin, ad, p))
    out = {}
    for ad, tohum, R, Nh, dal, f, n, parca in isler:
        out[ad] = np.concatenate([np.load(havuz_yolu(dizin, ad, p)) for p in range(parca)])
    return out


# ------------------------------------------------------------------ koşu
def gercek_girdi_mi(yollar):
    """Yollar gerçek arşiv dizinini ya da gerçek sha256 listesini gösteriyor mu (kod incelemesi, 17 Kasım 2026)."""
    return (os.path.realpath(yollar.arsiv_dizin) == os.path.realpath(ARSIV_DIZIN)
            or os.path.realpath(yollar.sha_liste) == os.path.realpath(SHA_LISTE))


def kos(ayar=Ayar(), yollar=Yollar(), gercek=False, gunluk=print):
    # Gerçek kip kapısı kos()'un içinde de: içe aktarılarak çağrılınca da dondurulmamış ön kayıtla gerçek arşiv
    # açılmaz, hiçbir şey yazılmaz; gerçek girdiyle yalnız varsayılan (ön kayıt) ayarı kabul edilir.
    if gercek or gercek_girdi_mi(yollar):
        ok, neden = dondurulmus_mu()
        if not ok:
            raise SystemExit("GERÇEK KOŞU REDDEDİLDİ: " + neden)
        if dataclasses.replace(ayar, cekirdek=Ayar().cekirdek) != Ayar() or not gercek_girdi_mi(yollar):
            raise SystemExit("GERÇEK KOŞU REDDEDİLDİ: gerçek kipte ayar ön kayıttaki gibi ve girdi gerçek olmalı")
    dizin = yollar.cikti
    hyol = os.path.join(dizin, "tr13b_hukum.json")
    if os.path.exists(hyol):
        gunluk("KİLİT: hüküm dosyası var; koşu bir kez yapılır. Hiçbir şey hesaplanmadı.")
        return json.load(open(hyol))
    os.makedirs(os.path.join(dizin, "havuz"), exist_ok=True)
    dyol = os.path.join(dizin, "durum.json")
    durum = json.load(open(dyol)) if os.path.exists(dyol) else dict(asama=[], baslangic=time.time())
    t_bas = time.time()

    def kaydet(asama=None):
        if asama and asama not in durum["asama"]:
            durum["asama"].append(asama)
            durum.setdefault("asama_zaman", {})[asama] = round(time.time() - t_bas, 1)
        yaz_json(dyol, durum)

    taban = dict(kod_sha256=kod_sha(), gercek_kip=gercek, ayar=dataclasses.asdict(ayar),
                 tohum=dict(havuz="20261201 + 1000 i + dallanma sırası (+20 yineleme)", T1=TOHUM_T1, D3=TOHUM_D3))

    # ---- 1 girdi
    tamam, sha = sha_denetimi(yollar)
    durum["sha256"] = sha
    kaydet("1_girdi_sha")
    if not tamam:
        return _yaz_hukum(dizin, dict(taban, dal=1, hukum="veri yok", neden="ham arşiv sha256 uyuşmuyor", sha=sha,
                                      cumle=f"Veri yok. MDE (ön kayıt): {MDE_ONKAYIT}."))
    L, s4, A = girdi(yollar)

    # ---- 2 hazırlık (yalnız sayı)
    ozet, BG = [], {}
    for i, s in enumerate(L):
        o = s4[s["id"]]
        assert abs(float(o["R"]) - float(s["R_km"])) < 0.05, "R uyuşmuyor"
        oz, bg = hazirla(s, o, katalog(s, A))
        oz["sira"] = i
        ozet.append(oz)
        if bg is not None:
            BG[i] = bg
    uy = [(i, L[i]["kume"]) for i in sorted(BG)]
    kum, kids, kd = kume_yapisi(uy)
    durum["hazirlik"] = dict(olay=ozet, K_ana=len(kum), K_kesif_disi=len(kd), kumeler=kids)
    kaydet("2_hazirlik")
    gunluk("hazırlık:", len(BG), "üye,", len(kum), "küme; keşif dışı", len(kd))
    if len(kd) < KD_MIN:
        return _yaz_hukum(dizin, dict(taban, dal=1, hukum="veri yok", neden=f"keşif dışı K = {len(kd)} < {KD_MIN}",
                                      hazirlik=durum["hazirlik"],
                                      cumle=f"Veri yok (keşif dışı K = {len(kd)}). MDE (ön kayıt): {MDE_ONKAYIT}."))
    N = {i: next(o["N3bg"] for o in ozet if o["sira"] == i) for i in BG}
    R = {i: float(L[i]["R_km"]) for i in BG}

    with mp.get_context("fork").Pool(ayar.cekirdek) as havuz_ici:
        # ---- 3 kalibrasyon + sıfır havuzları
        kal = durum.setdefault("kal", {})
        isler, adlar = [], []
        for i in BG:
            for di, d in enumerate(DALLANMA):
                if f"{i}_{di}" not in kal:
                    isler.append((tohum_kal(i, di), R[i], N[i], d, ayar.kal_deneme)); adlar.append(f"{i}_{di}")
            if f"{i}_veri" not in kal:
                isler.append((tohum_veri_kal(i), R[i], N[i], 0.6, ayar.kal_deneme)); adlar.append(f"{i}_veri")
        for ad, r in zip(adlar, havuz_ici.map(_is_kal, isler, chunksize=1)):
            kal[ad] = r
        kaydet("3a_kalibrasyon")
        P, gecersiz = {}, []
        for deneme in (0, 1):
            isler = []
            for i in BG:
                for di, d in enumerate(DALLANMA):
                    k = f"{i}_{di}"
                    if deneme == 1 and kal[k].get("tamam0", True):
                        continue
                    Nh = kal[k]["Nh"] if deneme == 0 else kal[k]["Nh_yineleme"]
                    isler.append((f"s{i:02d}_{di}_{deneme}", tohum_havuz(i, di, deneme), R[i],
                                  Nh * ayar.test_nh_carpan, d, 0.0, ayar.havuz, ayar.parca))
            H = havuzlari_kos(ayar, dizin, isler, havuz_ici)
            for ad, h in H.items():
                i, di = int(ad[1:3]), int(ad[4])
                k = f"{i}_{di}"
                ort = float(np.mean(h[:, 2]))
                ok = kal_tamam(ort, N[i])
                kal[k][f"ort_n{deneme}"] = ort
                kal[k][f"tamam{deneme}"] = ok
                if deneme == 0 and not ok:
                    kal[k]["Nh_yineleme"] = kal[k]["Nh"] * N[i] / max(ort, 1.0)
                if ok:
                    P[(i, di)] = h
                elif deneme == 1:
                    gecersiz.append(dict(olay=i, dallanma=DALLANMA[di], N=N[i], ort_n=ort))
            kaydet(f"3b_havuz_deneme{deneme}")
        durum["kalibrasyon_gecersiz"] = gecersiz
        kaydet("3_sifir")
        if gecersiz:
            return _yaz_hukum(dizin, dict(taban, dal=2, hukum="geçersiz", neden="kalibrasyon ±%5 dışında (iki kez)",
                                          ayrinti=gecersiz, kal=kal, hazirlik=durum["hazirlik"],
                                          cumle="Geçersiz: sıfır havuzunun arka plan sayısı kalibre edilemedi."))
        # ---- 4 D-3 (gerçek z görülmeden)
        isler = []
        for i in BG:
            Nh = kal[f"{i}_veri"]["Nh"]
            isler.append((f"v{i:02d}_0", tohum_veri(i, 0), R[i], Nh, 0.6, ayar.test_d3_sinyal0, ayar.d3_n0, 1))
            for k, f in enumerate(D3_FLIST, 1):
                isler.append((f"v{i:02d}_{k}", tohum_veri(i, k), R[i], Nh, 0.6, f, ayar.d3_nf, 1))
        V = havuzlari_kos(ayar, dizin, isler, havuz_ici)
    havuzlar = {d: {i: sonlu_z(P[(i, di)]) for i in BG} for di, d in enumerate(DALLANMA)}
    bos = [f"{i}_{d}" for d in DALLANMA for i in BG if len(havuzlar[d][i]) == 0]
    bos += [f"veri_{i}_{k}" for i in BG for k in range(len(D3_FLIST) + 1) if len(sonlu_z(V[f"v{i:02d}_{k}"])) == 0]
    if bos:   # yalnız çok küçük sınama havuzlarında olur; gerçek ayarda 2000 bölgenin ortalama N'si N3bg >= 50
        return _yaz_hukum(dizin, dict(taban, dal=2, hukum="geçersiz", neden="süzgeçten sonra boş havuz: " + ", ".join(bos),
                                      hazirlik=durum["hazirlik"], cumle="Geçersiz: sıfır havuzu boş kaldı."))
    S = {d: sifir_cekilis(np.random.default_rng(TOHUM_T1 + di), havuzlar[d], kum, ayar.ns_t1)
         for di, d in enumerate(DALLANMA)}
    Sa = {d: np.sort(S[d][:, :, 0].mean(1)) for d in DALLANMA}
    Sk = {d: np.sort(S[d][:, kd, 0].mean(1)) for d in DALLANMA}
    rr = np.random.default_rng(TOHUM_D3)
    oran = {}
    for k, f in [(0, 0.0)] + list(enumerate(D3_FLIST, 1)):
        c = sifir_cekilis(rr, {i: sonlu_z(V[f"v{i:02d}_{k}"]) for i in BG}, kum, ayar.d3_nb)
        oran[f] = r0_oran(Sa, Sk, c[:, :, 0].mean(1), c[:, kd, 0].mean(1))
    fs = [0.0] + list(D3_FLIST)
    m_yeni = mde(fs, [oran[f] for f in fs])
    d3 = dict(yanlis_alarm=oran[0.0], guc={str(f): oran[f] for f in D3_FLIST}, MDE=m_yeni,
              gecer=d3_gecer(oran[0.0], oran[D3_F]),
              veri_ort_n={str(i): float(np.mean(V[f"v{i:02d}_0"][:, 2])) for i in BG})
    durum["D3"] = d3
    kaydet("4_D3")
    gunluk("D-3:", json.dumps(d3))
    if not d3["gecer"]:
        return _yaz_hukum(dizin, dict(taban, dal=2, hukum="geçersiz", neden="D-3 yapay denetimi geçilmedi", D3=d3,
                                      hazirlik=durum["hazirlik"],
                                      cumle="Geçersiz: koşu betiği yapay girdide R0'ın yanlış alarmını ya da gücünü "
                                            "tutturamadı; gerçek z hesaplanmadı."))

    # ---- 5 gerçek ölçü (bir kez)
    zyol = os.path.join(dizin, "gercek_z.json")
    if os.path.exists(zyol):
        Z = {int(k): v for k, v in json.load(open(zyol)).items()}
    else:
        Z = {}
        for i in BG:
            x, y, tg = BG[i]
            g, ic = G.izgara(R[i])
            rng = np.random.default_rng(tohum_olcu(i))
            ze, n = z_guvenli(rng, x, y, tg, R[i], 7 * YIL, 10 * YIL, 0.0, g, ic, ayar.b_ref)
            zp, n_p = z_guvenli(rng, x, y, tg, R[i], 4 * YIL, 7 * YIL, 0.0, g, ic, ayar.b_ref)
            Z[i] = dict(z=float(ze), z_p=float(zp), n=int(n), n_p=int(n_p))
        yaz_json(zyol, {str(k): v for k, v in Z.items()}, kip="x")
    kaydet("5_olcu")

    # ---- 6 hüküm
    uy2 = [(i, L[i]["kume"]) for i in sorted(BG) if np.isfinite(Z[i]["z"])]
    kum2, kids2, kd2 = kume_yapisi(uy2)
    if len(kd2) < KD_MIN:
        return _yaz_hukum(dizin, dict(taban, dal=1, hukum="veri yok", neden=f"z tanımsız; keşif dışı K = {len(kd2)}",
                                      cumle=f"Veri yok. MDE (ön kayıt): {MDE_ONKAYIT}."))
    if kum2 != kum:
        S = {d: sifir_cekilis(np.random.default_rng(TOHUM_T1 + di), havuzlar[d], kum2, ayar.ns_t1)
             for di, d in enumerate(DALLANMA)}
    zu = {i: Z[i]["z"] for i, _ in uy2}
    za, zk = kume_ort(zu, kum2), kume_ort(zu, [kum2[j] for j in kd2])
    p_a = {d: p_deger(S[d][:, :, 0].mean(1), za) for d in DALLANMA}
    p_k = {d: p_deger(S[d][:, kd2, 0].mean(1), zk) for d in DALLANMA}
    # plasebo (bilgi): z_p tanımlı üyelerle, dallanma 0,6 sıfırı
    uyp = [(i, L[i]["kume"]) for i, _ in uy2 if np.isfinite(Z[i]["z_p"])]
    kp, _, _ = kume_yapisi(uyp)
    p_pl = None
    if kp:
        sp = sifir_cekilis(np.random.default_rng(TOHUM_T1 + 9), {i: sonlu(P[(i, 1)]) for i in BG}, kp,
                           ayar.ns_t1)
        p_pl = p_deger(sp[:, :, 1].mean(1), kume_ort({i: Z[i]["z_p"] for i, _ in uyp}, kp))
    K_kd = len(kd2)
    mm = mde_metni(m_yeni)
    dal, hukum, cumle = hukum_kur(p_a, p_k, p_pl, K_kd, mm)
    # bilgi satırları
    se = {f"{a}_{d}": math.sqrt(p * (1 - p) / ayar.ns_t1) for a, pp in (("a", p_a), ("k", p_k)) for d, p in pp.items()}
    sinirda = [f"{a}_{d}" for a, pp in (("a", p_a), ("k", p_k)) for d, p in pp.items() if abs(p - ALFA) < SINIRDA]
    dk = [np.mean([Z[i]["z"] - Z[i]["z_p"] for i in k]) for k in kum2 if all(np.isfinite(Z[i]["z_p"]) for i in k)]
    q05 = {i: float(np.quantile(havuzlar[0.6][i][:, 0], 0.05)) for i, _ in uy2}
    t3k = sum(Z[i]["z"] <= q05[i] for i, _ in uy2)
    h = dict(taban, dal=dal, hukum=hukum, cumle=cumle, K_ana=len(kum2), K_kesif_disi=K_kd,
             kumeler=kids2, z_bar=dict(butun=za, kesif_disi=zk), p_butun={str(d): v for d, v in p_a.items()},
             p_kesif_disi={str(d): v for d, v in p_k.items()}, mc_standart_hata=se, sinirda=sinirda,
             MDE_kosu_oncesi=m_yeni, MDE_metni=mm, D3=d3,
             bilgi=dict(p_plasebo=p_pl, plasebo_arka_plan_sayisi={str(i): Z[i]["n_p"] for i in BG},
                        T2_isaret_cevirme_p=isaret_p(dk), T2_K=len(dk),
                        T3_binom=dict(asim=int(t3k), n=len(uy2), p=binom_p(int(t3k), len(uy2))),
                        uye_z={str(i): Z[i] for i in BG},
                        ref_en_buyuk={o["id"]: o.get("ref_en_buyuk") for o in ozet},
                        kalibrasyon=kal, havuz_nitelik=havuz_nitelik(P)),
             hazirlik=durum["hazirlik"], sure_s=round(time.time() - t_bas))
    kaydet("6_hukum")
    return _yaz_hukum(dizin, h)


# ------------------------------------------------------------------ gerçek kip kapısı ve komutlar
def dondurulmus_mu():
    if not os.path.exists(ONKAYIT):
        return False, "ön kayıt yok"
    metin = open(ONKAYIT, encoding="utf-8").read()
    durum = next((s for s in metin.splitlines() if s.startswith("Durum:")), "")
    if "DONDURULDU" not in durum:
        return False, "ön kayıt dondurulmamış ('Durum:' satırında DONDURULDU yok)"
    eksik = [k for k, v in kod_sha().items() if v not in metin]
    if eksik:
        return False, "sha256'sı ön kayıtta yazılı değil: " + ", ".join(eksik)
    return True, "tamam"


def bicim(yollar=Yollar()):
    """sha256 ve üye/biçim denetimi: ölçü yok, sayı yok, Mc yok."""
    tamam, sha = sha_denetimi(yollar)
    L = ana_liste(yollar.tamsayim)
    adlar = [a for a, _ in sha_listesi(yollar.sha_liste)]
    uye = [set(), set()]
    for k in (0, 1):
        with tarfile.open(yollar.arsiv_dizin + adlar[k], "r:gz") as tf:
            uye[k] = {m.name for m in tf}
    eksik, anahtar_hata = [], []
    for s in L:
        a, b = uye_adlari(s)
        eksik += [x for x in a if x not in uye[0]] + [x for x in b if x not in uye[1]]
    ornek = arsiv_oku(yollar.arsiv_dizin + adlar[0], {uye_adlari(L[0])[0][0], "ham/sayim_tam_satirlar.json"})
    for ad, v in ornek.items():
        if ad.endswith(".npz") and set(v) != {"t", "la", "lo", "de", "m"}:
            anahtar_hata.append(ad)
    s4 = {z["id"] for z in ornek["ham/sayim_tam_satirlar.json"]["satir"]}
    return dict(sha_tamam=tamam, sha=sha, olay=len(L), eksik_uye=eksik, npz_anahtar_hatasi=anahtar_hata,
                sayim4_eksik_olay=[s["id"] for s in L if s["id"] not in s4])


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["bicim"]:
        print(json.dumps(bicim(), indent=1, ensure_ascii=False))
    elif a == ["kos"]:
        ok, neden = dondurulmus_mu()
        if not ok:
            sys.exit("GERÇEK KOŞU REDDEDİLDİ: " + neden)
        print(json.dumps({k: v for k, v in kos(gercek=True).items() if k in ("dal", "hukum", "cumle")},
                         indent=1, ensure_ascii=False))
    elif a == ["durum"]:
        p = os.path.join(CIKTI, "durum.json")
        print(open(p).read() if os.path.exists(p) else "durum dosyası yok")
    else:
        print(__doc__)
