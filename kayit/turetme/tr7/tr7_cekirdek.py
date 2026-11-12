#!/usr/bin/env python3
"""TR-7 koşu kodunun çekirdeği (ön kayıt sürüm 3, DONDURULDU; sha256 df426ffc…4c20).

Bu modül YALNIZ hesap yapar: ağa çıkmaz, dosya indirmez, dalga formu dosyası açmaz. Girdiler bellekteki dizilerdir.
obspy yalnız (i) §6.2.3'ün adını verdiği Butterworth süzgeci (`obspy.signal.filter.bandpass`, corners=4,
zerophase=True), (ii) yanıt (StationXML nesnesinden) ve (iii) seyahat süresi (`obspy.taup`, iasp91) için ve yalnız
gerektiğinde içe aktarılır. Hilbert dönüşümü numpy ile `scipy.signal.hilbert`'in birebir aynısıdır (sınamada
denetlenir; kodlayıcı okuması O-2).

Bölümler (ön kayıt bölüm numaralarıyla):
  §5      pencereler (W, R, dolgu), 2026 sınırı
  §6.0    12 istasyon sınırı, `nokta_cizgi`
  §6.2    zarf zinciri (1–5), L, m, σ (6), aşım ve köprüleme (7), kırpılma (2), örtü (§4.2)
  §6.3    tutarlılık kümesi (bağlantılı bileşen), gecikmeli Pearson
  §6.4    modülasyon ölçüsü ve dairesel kaydırma boş dağılımı
  §6.5    maskeler (1 yerel katalog, 1a E1), darbe (2), sızıntı (3), taban kayması (3a, W′_son)
  §6.6    ölçülen dinamik gerilme
  §7.4    MDA: yapay tremor, yanıtla çarpma, basamak kuralı
  §7.5    tremor genliği kestiricisi
  §8      binom şartı, X_min, p_üst, n_açık, p_min, bant
Zaman ekseni: tam UTC saniyeleri (epoch, int). "Eksen" bir (pencere, segment) için ortak 1 Hz dizinidir; e[i] eksen
başı + i saniyesindeki [k, k+1) kutusudur. NaN = kayıtsız.
"""
import datetime as dt
import math

import numpy as np

# ------------------------------------------------------------------ bağlayıcı sabitler
V_ON, V_ARKA, KUYRUK, BASVURU_S, DOLGU_S = 5.0, 2.8, 600.0, 3600.0, 600.0   # §5
SON_AN = dt.datetime(2026, 1, 1)                                            # §3.6: hiçbir pencere geçemez
KATALOG_SON = dt.datetime(2025, 12, 31, 23, 59, 59)                          # §3.6
N_SINIR, N_IST_MIN = 12, 3                                                  # §6.0, §4.2
ORTU_MIN = 0.90                                                             # §4.2
BANT_YUKSEK, BANT_ALCAK, BANT_LP = (2.0, 8.0), (0.5, 1.0), (0.02, 0.1)      # §6.2
HILBERT_KENAR = 10.0                                                        # §6.2.3
PRE_FILT, WATER_LEVEL = (0.005, 0.01, 0.15, 0.2), 60                        # §6.2.4
KIRP_ARDISIK, KIRP_TAVAN, KIRP_PAY, KIRP_B_VARSAYILAN = 5, 1e6, 0.95, 24    # §6.2.2
YUMUSAT, R_KENAR = 5, 5                                                     # §6.2.6
KSIG, BOSLUK, KMIN, NUST = 4.0, 20, 30, 15                                  # §6.2.7
KUME_PAY, I_PAY, LAG, KORR, KORR_CIFT = 20, 60, 10, 0.5, 3                  # §6.3
MOD_N, MOD_KAY, MOD_LAG, MOD_ESIK, MOD_TOHUM = 1000, 120, 10, 0.01, 20261112 + 3   # §6.4
YEREL_YAKIN = (150.0, 2.0, 60.0)        # §6.5.1: ≤150 km, M ≥ 2,0, [t0, t0 + d/3 + 60]
YEREL_UZAK = (1000.0, 4.0, 180.0)       # §6.5.1: ≤1000 km, M ≥ 4,0, [t0, t0 + d/3 + 180]
YEREL_HIZ = 3.0
E1_ONCE, E1_BUYUK, E1_KUCUK, E1_M7, E1_M6, E1_IKIZ_S = 10.0, 240.0, 60.0, 7.0, 6.0, 5.0   # §6.5.1a
DARBE_ON, DARBE_ON_ORAN, DARBE_SON, DARBE_SON_ORAN = 2, 8.0, 20, 2.0          # §6.5.2
TABAN_S = 60                                                                # §6.5.3a
G_MODUL, C_HIZ = 30e9, 3500.0                                               # §6.6
PGV_ORAN = 0.5                                                              # §6.6 |H(0,02)|/|H(1)|
G_ARALIK = (0.5, 2.0)                                                       # §3.5 c
MDA_DERIN, MDA_HIZ, MDA_SURE, MDA_PER, MDA_KENAR = 25.0, 3.5, 300.0, 20.0, 10.0   # §7.4
MDA_BAS = (60, 360)                                                         # U[60, |W| − 360]
MDA_J = range(0, 101)                                                       # A = 10^(j/20) nm/s
MDA_MIN_DENEME = 20
MDA_TOHUM = 20261112 + 2
A_BASAMAK = [10 ** (j / 20) for j in MDA_J]                                 # nm/s
TAU_ESIK = 2.0                                                              # kPa
FAR_K2 = 0.05

SEGMENT = {                                     # tr7_onkayit_sayilar.py ile aynı izler (boylam, enlem)
    'S1': [(26.20, 40.55), (26.90, 40.62), (27.50, 40.80)],
    'S2': [(27.50, 40.80), (28.00, 40.82), (28.60, 40.85), (29.00, 40.83)],
    'S3': [(29.00, 40.83), (29.30, 40.72), (29.90, 40.72)],
    'S4': [(29.90, 40.72), (30.30, 40.70), (30.80, 40.75), (31.20, 40.80)],
    'S5': [(31.20, 40.80), (31.60, 40.73), (32.20, 40.80), (32.60, 40.87)],
    'S6': [(32.60, 40.87), (33.30, 40.90), (34.00, 41.02)],
    'S7': [(30.30, 40.50), (29.50, 40.43), (29.10, 40.42), (28.30, 40.33), (27.50, 40.25), (27.00, 40.10),
           (26.60, 39.70)],
    'PK': [(-120.80, 36.20), (-120.50, 35.97), (-120.35, 35.83), (-120.20, 35.65)],
}
SEGMENTLER = ('S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7')


class CekirdekHata(Exception):
    """Çekirdeğin girdisi metne aykırı (ör. 2026 sınırı): koşu durur."""


# ------------------------------------------------------------------ zaman ve geometri
def zaman(s):
    """ISO dizgesi -> saf (tz'siz) UTC datetime."""
    if isinstance(s, dt.datetime):
        return s
    return dt.datetime.fromisoformat(str(s).replace('Z', ''))


_EPOK = dt.datetime(1970, 1, 1)


def epoch(t):
    return (zaman(t) - _EPOK).total_seconds()


def epoch_zaman(e):
    return _EPOK + dt.timedelta(seconds=float(e))


def hav(la1, lo1, la2, lo2):
    p1, p2 = math.radians(la1), math.radians(la2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lo2 - lo1) / 2) ** 2
    return 2 * 6371.0 * math.asin(min(1, math.sqrt(a)))


def nokta_cizgi(la, lo, iz):
    """tr7_onkayit_sayilar.py `nokta_cizgi` ile aynı (km)."""
    k = math.cos(math.radians(la)) * 111.195
    px, py = lo * k, la * 111.195
    en = 1e9
    for (x1, y1), (x2, y2) in zip(iz[:-1], iz[1:]):
        ax, ay, bx, by = x1 * k, y1 * 111.195, x2 * k, y2 * 111.195
        dx, dy = bx - ax, by - ay
        t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
        en = min(en, math.hypot(px - (ax + t * dx), py - (ay + t * dy)))
    return en


def orta(seg):
    """Segment orta noktası: köşe noktalarının ortalaması (enlem, boylam)."""
    iz = SEGMENT[seg]
    return sum(p[1] for p in iz) / len(iz), sum(p[0] for p in iz) / len(iz)


def r_hiposantr(la, lo, seg):
    """§7.4: kaynak segment orta noktasının 25 km altında; r_i hiposantr uzaklığı (km)."""
    la0, lo0 = orta(seg)
    return math.hypot(hav(la, lo, la0, lo0), MDA_DERIN)


def pencere_hesapla(t0, d_km):
    """§5: W = [T0 + Δ/5, T0 + Δ/2,8 + 600], R = [T0 − 3600, T0); listede W saniyeye yuvarlanmış yazılıdır."""
    t0 = zaman(t0)
    w0 = t0 + dt.timedelta(seconds=d_km / V_ON)
    w1 = t0 + dt.timedelta(seconds=d_km / V_ARKA + KUYRUK)
    r0 = t0 - dt.timedelta(seconds=BASVURU_S)
    if w1 + dt.timedelta(seconds=DOLGU_S) >= SON_AN:
        raise CekirdekHata(f'2026 sınırı: pencere {w1} (+dolgu) 2026-01-01\'i geçiyor (§3.6)')
    return dict(R=(r0, t0), W=(w0, w1))


def sinir_denetle(t1):
    """Her istek ve pencere için: bitiş < 2026-01-01 (§3.6). İhlal kodu durdurur."""
    if zaman(t1) >= SON_AN:
        raise CekirdekHata(f'2026 sınırı ihlali: {t1}')


# ------------------------------------------------------------------ §6.2 zarf zinciri
def bant_gecir(x, fs, lo, hi):
    """§6.2.3: 4 kutuplu Butterworth bant geçiren, ileri-geri (obspy bandpass, corners=4, zerophase=True)."""
    from obspy.signal.filter import bandpass
    return bandpass(np.asarray(x, dtype=np.float64), lo, hi, fs, corners=4, zerophase=True)


def analitik(x):
    """Analitik sinyal; `scipy.signal.hilbert(x)` ile birebir aynı algoritma (FFT, h = [1, 2, …, 2, (1), 0, …])."""
    x = np.asarray(x, dtype=np.float64)
    n = len(x)
    X = np.fft.fft(x)
    h = np.zeros(n)
    if n % 2 == 0:
        h[0] = h[n // 2] = 1
        h[1:n // 2] = 2
    else:
        h[0] = 1
        h[1:(n + 1) // 2] = 2
    return np.fft.ifft(X * h)


def ortalama_egilim(x):
    """§6.2.1: ortalama ve doğrusal eğilim çıkarılır (en küçük kareler doğrusu; obspy detrend('linear') ile aynı)."""
    x = np.asarray(x, dtype=np.float64)
    n = len(x)
    if n < 2:
        return x - x.mean() if n else x
    t = np.arange(n, dtype=np.float64)
    tm = t.mean()
    b = np.dot(t - tm, x - x.mean()) / np.dot(t - tm, t - tm)
    return x - (x.mean() + b * (t - tm))


def parca_analitik(x, fs, bant):
    """Bir kesintisiz parçanın (yer birimi: sayım / S) bant analitik sinyali."""
    return analitik(bant_gecir(x, fs, *bant))


def kutula(t0, fs, genlik, kenar=HILBERT_KENAR):
    """§6.2.3: parçanın ilk ve son `kenar` sn'si atılır; 1 sn'lik kutularda ortalama.
    Dönüş (k0, e): e[i], [k0 + i, k0 + i + 1) kutusunun ortalaması; yalnız tümü örtülen kutular (öteki NaN).
    Kodlayıcı okuması O-4: kısmen örtülen kutu kayıtsızdır."""
    n = len(genlik)
    if n == 0:
        return 0, np.zeros(0)
    t = t0 + np.arange(n) / fs
    tut = (t >= t0 + kenar - 1e-9) & (t <= t0 + (n - 1) / fs - kenar + 1e-9)
    if not tut.any():
        return 0, np.zeros(0)
    t, g = t[tut], np.asarray(genlik, dtype=np.float64)[tut]
    kk = np.floor(t + 1e-7).astype(np.int64)
    k0 = int(kk[0])
    idx = kk - k0
    m = int(idx[-1]) + 1
    top = np.bincount(idx, weights=g, minlength=m)
    say = np.bincount(idx, minlength=m)
    e = np.full(m, np.nan)
    ok = say > 0
    e[ok] = top[ok] / say[ok]
    # ilk ve son kutu: öncesinde/sonrasında ızgara noktası eksikse kısmi
    if t[0] - 1.0 / fs >= k0 - 1e-7:
        e[0] = np.nan
    if t[-1] + 1.0 / fs < k0 + m - 1e-7:
        e[-1] = np.nan
    return k0, e


def eksene(eksen_k0, n, k0, e, hedef=None):
    """1 Hz diziyi ortak eksene yerleştirir (NaN kayıtsız)."""
    out = np.full(n, np.nan) if hedef is None else hedef
    a, b = k0 - eksen_k0, k0 - eksen_k0 + len(e)
    i0, i1 = max(a, 0), min(b, n)
    if i1 > i0:
        seg = e[i0 - a:i1 - a]
        h = out[i0:i1]
        sec = np.isfinite(seg)
        h[sec] = seg[sec]
        out[i0:i1] = h
    return out


def birlesik(es):
    """§6.2.5: C(t) = √(ortalama_bileşen e(t)²); bir bileşen kayıtsızsa o saniye kayıtsız (okuma O-5)."""
    es = np.array(es, dtype=np.float64)
    return np.sqrt(np.mean(es ** 2, axis=0))


def f32(x):
    """Zarf deposu float32'dir; algılama hep float32'ye yuvarlanmış zarfla yapılır (okuma O-6)."""
    return np.asarray(np.asarray(x, dtype=np.float32), dtype=np.float64)


# ------------------------------------------------------------------ §4.2 örtü, §6.2.2 kırpılma
def ortu(parcalar, a, b):
    """parcalar: [(t_ilk, t_son_dahil, fs)] (epoch). Örtü: [a, b) içindeki tam saniyelerden kesintisiz örnek bulunanların
    payı. Saniye k sayılır: bir parçanın örnekleri [k, k+1)'i tümüyle örter (t_ilk ≤ k ve t_son + 1/fs ≥ k + 1)."""
    a, b = int(math.floor(a)), int(math.ceil(b))
    if b <= a:
        return 0.0
    var = np.zeros(b - a, bool)
    for t1, t2, fs in parcalar:
        lo = max(a, int(math.ceil(t1 - 1e-7)))
        hi = min(b, int(math.floor(t2 + 1.0 / fs + 1e-7)))
        if hi > lo:
            var[lo - a:hi - a] = True
    return float(var.mean())


def kirpilma_esigi(b_bit):
    b = KIRP_B_VARSAYILAN if b_bit is None else int(b_bit)
    return min(KIRP_TAVAN, KIRP_PAY * (2 ** (b - 1) - 1))


def kirpilma(x_sayim, b_bit):
    """§6.2.2: W içinde, ham sayımın mutlak en büyük değerine eşit ≥5 ardışık örnek ve değer ≥ eşik."""
    x = np.abs(np.asarray(x_sayim, dtype=np.float64))
    if len(x) == 0:
        return False
    mx = x.max()
    if mx < kirpilma_esigi(b_bit):
        return False
    e = (x == mx).astype(np.int8)
    if e.sum() < KIRP_ARDISIK:
        return False
    d = np.diff(np.concatenate([[0], e, [0]]))
    bas, son = np.flatnonzero(d == 1), np.flatnonzero(d == -1)
    return bool(((son - bas) >= KIRP_ARDISIK).any())


# ------------------------------------------------------------------ §6.2.6 L, m, σ
def L_seri(c):
    """L = log10(5 sn merkezli kayan ortalama C). Dizinin iki ucunda np.convolve 'same' (sıfır dolgu) davranışı
    (referans betiklerle aynı); içerideki NaN'ı içeren her pencere NaN (kayıtsız)."""
    c = np.asarray(c, dtype=np.float64)
    nan = ~np.isfinite(c)
    k = np.ones(YUMUSAT) / YUMUSAT
    s = np.convolve(np.where(nan, 0.0, c), k, 'same')
    with np.errstate(divide='ignore', invalid='ignore'):
        L = np.log10(s)
    if nan.any():
        L[np.convolve(nan.astype(float), np.ones(YUMUSAT), 'same') > 0.5] = np.nan
    return L


def m_sigma(L, R, maske):
    """§6.2.6: m = medyan(L, R), σ = 1,4826·MAD; R'nin kenardaki 5'er sn'si, maskeli ve kayıtsız saniyeler hariç."""
    r = np.zeros(len(L), bool)
    r[R[0] + R_KENAR:R[1] - R_KENAR] = True
    r &= ~maske & np.isfinite(L)
    x = L[r]
    if len(x) == 0:
        return float('nan'), 0.0
    m = float(np.median(x))
    return m, float(1.4826 * np.median(np.abs(x - m)))


# ------------------------------------------------------------------ §6.2.7 aşım ve köprüleme
def asimlar(L, m, s, W, maske):
    """İstasyon W'si (eksen dizinleri [W0, W1)) içinde aşım parçaları [(a, b)] (eksen dizini, b dışlayıcı).
    Maskeli ya da kayıtsız saniye aşım değildir ve içinde böyle bir saniye bulunan boşluk köprülenmez."""
    W0, W1 = W
    Lw = L[W0:W1]
    acik = ~maske[W0:W1] & np.isfinite(Lw)
    with np.errstate(invalid='ignore'):
        e = (Lw > m + KSIG * s) & acik
    kapali = ~acik
    w = np.flatnonzero(e)
    out = []
    if len(w) == 0:
        return out
    a = b = int(w[0])
    n = 1
    for x in w[1:]:
        x = int(x)
        if x - b - 1 <= BOSLUK and not kapali[b + 1:x].any():
            b = x
            n += 1
        else:
            if b - a + 1 >= KMIN and n >= NUST:
                out.append((W0 + a, W0 + b + 1))
            a = b = x
            n = 1
    if b - a + 1 >= KMIN and n >= NUST:
        out.append((W0 + a, W0 + b + 1))
    return out


def istasyon(C, Cd, R, W, maske, ad=None):
    """Bir istasyonun 1 Hz kaydı: C (2–8 Hz birleşik), Cd (0,5–1 Hz birleşik), R ve W (eksen dizinleri)."""
    C = np.asarray(C, dtype=np.float64)
    Cd = np.asarray(Cd, dtype=np.float64)
    L = L_seri(C)
    Ld = L_seri(Cd)
    m, s = m_sigma(L, R, maske)
    md, sd = m_sigma(Ld, R, maske)
    ax = asimlar(L, m, s, W, maske) if s > 0 else []      # σ = 0: istasyon o pencereden düşer (okuma O-8)
    return dict(ad=ad, Cy=C, Cd=Cd, L=L, m=m, s=s, Ld=Ld, md=md, sd=sd, R=tuple(R), W=tuple(W), ax=ax,
                sigma_sifir=not s > 0)


# ------------------------------------------------------------------ §6.3 tutarlılık
def pearson_max(x, y, gx, gy):
    """Gecikme −10…+10 sn üzerinde en büyük Pearson (geçerli saniyeler; ≥ 11 ortak örnek; std > 0)."""
    best = -1.0
    n = len(x)
    for lag in range(-LAG, LAG + 1):
        if lag >= 0:
            xx, yy, g = x[lag:], y[:n - lag], gx[lag:] & gy[:n - lag]
        else:
            xx, yy, g = x[:lag], y[-lag:], gx[:lag] & gy[-lag:]
        xx, yy = xx[g], yy[g]
        if len(xx) > 10 and xx.std() > 0 and yy.std() > 0:
            best = max(best, float(np.corrcoef(xx, yy)[0, 1]))
    return best


def kumeler(ist, maske, Wb, tutarlilik=True):
    """§6.3: istasyon aşımları ±20 sn genişletilince örtüşenler bağlantılı bileşen; ≥3 farklı istasyon. Küme aralığı
    I = [en erken başlangıç − 60, en geç bitiş + 60] ∩ Wb (Wb: (pencere, segment) istasyon W'lerinin birleşim zarfı;
    okuma O-9). Tutarlı: ≥3 çiftte gecikmeli Pearson ≥ 0,5 (maskeli ve kayıtsız saniyeler çıkarılır)."""
    parc = [(k, a, b) for k, x in enumerate(ist) for a, b in x['ax']]
    ust = list(range(len(parc)))

    def bul(i):
        while ust[i] != i:
            ust[i] = ust[ust[i]]
            i = ust[i]
        return i
    for i in range(len(parc)):
        for j in range(i + 1, len(parc)):
            if parc[i][1] - KUME_PAY <= parc[j][2] + KUME_PAY and parc[j][1] - KUME_PAY <= parc[i][2] + KUME_PAY:
                ust[bul(i)] = bul(j)
    gr = {}
    for i, p in enumerate(parc):
        gr.setdefault(bul(i), []).append(p)
    out = []
    for ps in gr.values():
        uy = sorted({p[0] for p in ps})
        if len(uy) < N_IST_MIN:
            continue
        lo = max(Wb[0], min(p[1] for p in ps) - I_PAY)
        hi = min(Wb[1], max(p[2] for p in ps) + I_PAY)
        n_ok = 0
        ciftler = []
        if tutarlilik:
            g0 = ~maske[lo:hi]
            for i1 in range(len(uy)):
                for i2 in range(i1 + 1, len(uy)):
                    x = ist[uy[i1]]['L'][lo:hi]
                    y = ist[uy[i2]]['L'][lo:hi]
                    r = pearson_max(x, y, g0 & np.isfinite(x), g0 & np.isfinite(y))
                    ciftler.append(round(r, 4))
                    n_ok += r >= KORR
        k = dict(uyeler=uy, parcalar=sorted(ps, key=lambda p: (p[1], p[0])), I=(lo, hi),
                 Ip=(min(p[1] for p in ps), max(p[2] for p in ps)), n_cift_tutarli=n_ok, korelasyon=ciftler)
        if not tutarlilik or n_ok >= KORR_CIFT:
            out.append(k)
    return sorted(out, key=lambda k: (k['Ip'][0], k['Ip'][1]))


# ------------------------------------------------------------------ §6.5 ayıklama kuralları
def darbe_ist(Cy, parcalar, kip='dogru'):
    """§6.5.2: istasyonun kümedeki parçalarından C'nin (yumuşatılmamış) en büyük değeri c_p en büyük olan parça;
    [t_p − 2, t_p) içinde C ≤ c_p/8 bir saniye VE (t_p, t_p + 20] içinde C ≤ c_p/2 bir saniye → darbe.
    kip 'yanlis_on' (ön şart c_p/2) ve 'yanlis_yumusak' (5 sn yumuşatılmış C) yalnız KD'nin bilinen yanlış kodudur.
    Kayıtsız (NaN) saniye şartı sağlamaz (okuma O-10)."""
    c = np.convolve(Cy, np.ones(5) / 5, 'same') if kip == 'yanlis_yumusak' else Cy
    en = None
    for a, b in parcalar:
        seg = c[a:b]
        if not np.isfinite(seg).any():
            continue
        k = int(np.nanargmax(seg))
        if en is None or seg[k] > en[0]:
            en = (float(seg[k]), a + k)
    if en is None:
        return False
    cp, tp = en
    on_esik = cp / 2 if kip == 'yanlis_on' else cp / DARBE_ON_ORAN
    with np.errstate(invalid='ignore'):
        on = (c[max(0, tp - DARBE_ON):tp] <= on_esik).any()
        son = (c[tp + 1:tp + DARBE_SON + 1] <= cp / DARBE_SON_ORAN).any()
    return bool(on and son)


def sizinti_ist(x, parcalar, maske, kip='dogru', I=None):
    """§6.5.3: istasyonun kümedeki parçalarının içindeki aşım saniyelerinde (L > m + 4σ, maskesiz)
    Δ_y = medyan(L − m), Δ_d = medyan(L_d − m_d); Δ_d ≥ Δ_y → sızıntı. Yanlış kod kipleri yalnız KD için:
    'ters' (Δ_y ≥ Δ_d), 'inc1_I' (İNCELEME-1: küme aralığı I'da medyan), 'z' (sürüm 1: σ ile bölünmüş, I'da)."""
    if kip in ('inc1_I', 'z'):
        lo, hi = I
        g = ~maske[lo:hi] & np.isfinite(x['L'][lo:hi]) & np.isfinite(x['Ld'][lo:hi])
        if not g.any():
            return False
        dy = np.median(x['L'][lo:hi][g]) - x['m']
        dd = np.median(x['Ld'][lo:hi][g]) - x['md']
        if kip == 'z':
            return bool(x['sd'] > 0 and (dd / x['sd']) >= (dy / x['s']))
        return bool(dd >= dy)
    sec = np.zeros(len(x['L']), bool)
    for a, b in parcalar:
        sec[a:b] = True
    with np.errstate(invalid='ignore'):
        sec &= (x['L'] > x['m'] + KSIG * x['s']) & ~maske & np.isfinite(x['Ld'])
    if not sec.any():
        return False
    dy = np.median(x['L'][sec]) - x['m']
    dd = np.median(x['Ld'][sec]) - x['md']
    return bool(dy >= dd) if kip == 'ters' else bool(dd >= dy)


def w_son_acik(x, maske):
    """§6.5.3a: W′_son = istasyonun kendi W'si içinde maskelenmemiş ve kayıtlı son saniye (eksen dizini); yoksa None.
    'Kayıtlı' = L tanımlı (okuma O-11)."""
    W0, W1 = x['W']
    acik = ~maske[W0:W1] & np.isfinite(x['L'][W0:W1])
    k = np.flatnonzero(acik)
    return int(W0 + k[-1]) if len(k) else None


def taban_ist(x, parcalar, maske, kip='dogru'):
    """3a: istasyonun kümedeki parçalarından biri W′_son − 60'a ya da sonrasına kadar sürüyor mu (b dışlayıcı:
    b ≥ (W′_son + 1) − 60). kip 'v2' (sürüm 2: W sonu − 60) ve 'yok' yalnız KD'nin bilinen yanlış kodudur."""
    if kip == 'yok':
        return False
    if kip == 'v2':
        sinir = x['W'][1] - TABAN_S
    else:
        k = w_son_acik(x, maske)
        if k is None:
            return False
        sinir = (k + 1) - TABAN_S
    return any(b >= sinir for a, b in parcalar)


def ayikla(ist, kume, maske, yanlis=False):
    """§6.5 madde 2, 3, 3a. Dönüş: bayraklar (her biri 'küme atılır' anlamında) ve istasyon başına ayrıntı."""
    uy = kume['uyeler']
    yarim = len(uy) / 2
    pk = {k: [(a, b) for kk, a, b in kume['parcalar'] if kk == k] for k in uy}
    d = [darbe_ist(ist[k]['Cy'], pk[k]) for k in uy]
    s = [sizinti_ist(ist[k], pk[k], maske) for k in uy]
    t = [taban_ist(ist[k], pk[k], maske) for k in uy]
    bay = dict(darbe=sum(d) >= yarim, sizinti=sum(s) >= yarim, taban=sum(t) >= yarim,
               darbe_pay=round(sum(d) / len(uy), 3), sizinti_pay=round(sum(s) / len(uy), 3),
               taban_pay=round(sum(t) / len(uy), 3))
    if yanlis:
        for kip in ('yanlis_on', 'yanlis_yumusak'):
            bay['darbe_' + kip] = sum(darbe_ist(ist[k]['Cy'], pk[k], kip) for k in uy) >= yarim
        for kip in ('ters', 'inc1_I', 'z'):
            bay['sizinti_' + kip] = sum(sizinti_ist(ist[k], pk[k], maske, kip, kume['I']) for k in uy) >= yarim
        bay['taban_v2'] = sum(taban_ist(ist[k], pk[k], maske, 'v2') for k in uy) >= yarim
    return bay


TAM = ('darbe', 'sizinti', 'taban')


def pencere_algila(ist, maske, Wb, yanlis=False, kural=TAM):
    """§6.3 + §6.5: tutarlı kümeler, ayıklama bayrakları; algılama = en az bir tutarlı küme `kural`dan sağ çıkar."""
    ks = kumeler(ist, maske, Wb)
    for k in ks:
        k['bayrak'] = ayikla(ist, k, maske, yanlis)
        k['sag'] = not any(k['bayrak'][x] for x in kural)
    return dict(kumeler=ks, algilama=any(k['sag'] for k in ks),
                ayiklanan=dict(darbe=sum(k['bayrak']['darbe'] for k in ks),
                               sizinti=sum(k['bayrak']['sizinti'] for k in ks),
                               taban=sum(k['bayrak']['taban'] for k in ks)))


def sag_kalan(ks, kural):
    return any(not any(k['bayrak'][x] for x in kural) for k in ks)


# ------------------------------------------------------------------ §6.5.1, 1a maskeler
def saniye_maskesi(araliklar, eksen_k0, n):
    """[a, b) epoch aralıklarını eksen saniyelerine çevirir: k maskelidir ⇔ [k, k+1) aralıkla kesişir
    (floor(a) ≤ k < ceil(b)); tamsayı uçlarda D12c'nin `saniyeler`iyle aynı (okuma O-12)."""
    m = np.zeros(n, bool)
    for a, b in araliklar:
        lo, hi = int(math.floor(a)) - eksen_k0, int(math.ceil(b)) - eksen_k0
        lo, hi = max(lo, 0), min(hi, n)
        if hi > lo:
            m[lo:hi] = True
    return m


def birlesim(ar):
    ar = sorted(ar)
    out = []
    for a, b in ar:
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return [tuple(x) for x in out]


def e1_dislanir(o, tet_id, tet_t0, kip='dogru'):
    """§6.5.1a: tetikleyici olayın kendisi ve T0'a ±5 sn içinde M ≥ 7,0 başka kimlikli kaydı dışarıda (Wharton
    biriminin öteki olayı dahildir: `tet_id` yalnız pencerenin kendi olayıdır)."""
    if o['id'] == tet_id:
        return True
    if kip != 'ikiz_yok' and tet_t0 is not None and o.get('t0') is not None \
            and abs(o['t0'] - tet_t0) <= E1_IKIZ_S and o['M'] >= E1_M7:
        return True
    return False


def e1_kurallar(M, kip='dogru'):
    buyuk = M > E1_M7 if kip == 'buyuktur7' else M >= E1_M7
    if buyuk:
        return [('P', E1_BUYUK), ('S', E1_BUYUK)]
    if M >= E1_M6:
        k = 30.0 if kip == 'kuyruk30' else E1_KUCUK
        return [('P', k), ('S', k)] if kip == 'S6x' else [('P', k)]
    return []


def e1_araliklar(olaylar, tet_id, tet_t0, kip='dogru'):
    """olaylar: [dict(id, t0, M, P, S)] (zamanlar epoch sn; P/S varış anı ya da None). Dönüş: birleşmiş [a, b)."""
    ar = []
    for o in olaylar:
        if e1_dislanir(o, tet_id, tet_t0, kip):
            continue
        for faz, k in e1_kurallar(o['M'], kip):
            t = o.get(faz)
            if t is not None:
                ar.append((t - E1_ONCE, t + k))
    return birlesim(ar)


def taup_varislar(derinlik_km, delta_derece, model=None):
    """§6.5.1a: iasp91, olay derinliğinde: t_P = adı P ile başlayan fazların en erkeni, t_S = S ile başlayanların."""
    if model is None:
        model = taup_model()
    tt = model.get_travel_times(source_depth_in_km=max(0.0, derinlik_km), distance_in_degree=delta_derece,
                                phase_list=['ttall'])
    tp = min((a.time for a in tt if a.name.startswith('P')), default=None)
    ts = min((a.time for a in tt if a.name.startswith('S')), default=None)
    return tp, ts


_MODEL = {}


def taup_model():
    if 'iasp91' not in _MODEL:
        from obspy.taup import TauPyModel
        _MODEL['iasp91'] = TauPyModel('iasp91')
    return _MODEL['iasp91']


def cekirdek_fazlari(derinlik_km, delta_derece, model=None):
    """§7.2 (b′ ii): tetikleyicinin kendi PKKP, SKKP, PKKS, PKIKPPKIKP, PKPPKP varışları (iasp91; sn)."""
    if model is None:
        model = taup_model()
    fz = ('PKKP', 'SKKP', 'PKKS', 'PKIKPPKIKP', 'PKPPKP')
    out = {}
    for f in fz:
        try:
            tt = model.get_travel_times(source_depth_in_km=max(0.0, derinlik_km), distance_in_degree=delta_derece,
                                        phase_list=[f])
        except Exception:                      # noqa: BLE001  (faz bu modelde tanımsız)
            tt = []
        out[f] = [a.time for a in tt]
    return out


def yerel_araliklar(olaylar, iz):
    """§6.5.1: olaylar [dict(t0 epoch, la, lo, M)] (iki katalogun birleşimi, eşleştirme yok). Dönüş [a, b) aralıkları.
    Büyüklüğü olmayan kayıt hiçbir şartı sağlamaz (okuma O-13)."""
    ar = []
    for o in olaylar:
        if o.get('M') is None or not math.isfinite(o['M']):
            continue
        d = nokta_cizgi(o['la'], o['lo'], iz)
        if d <= YEREL_YAKIN[0] and o['M'] >= YEREL_YAKIN[1]:
            ar.append((o['t0'], o['t0'] + d / YEREL_HIZ + YEREL_YAKIN[2]))
        if d <= YEREL_UZAK[0] and o['M'] >= YEREL_UZAK[1]:
            ar.append((o['t0'], o['t0'] + d / YEREL_HIZ + YEREL_UZAK[2]))
    return birlesim(ar)


def maskeli_pay(maske_s, W):
    """Bir aralığın (eksen dizinleri) maskeli saniye payı."""
    a, b = W
    return float(maske_s[a:b].mean()) if b > a else float('nan')


# ------------------------------------------------------------------ §6.4 modülasyon
def faz_cos(v):
    """φ_c = v_c'nin W üzerindeki analitik sinyalinin fazı; dönüş cos φ (kayıtsız saniye 0 ile doldurulur, O-14)."""
    v = np.where(np.isfinite(v), v, 0.0)
    return np.cos(np.angle(analitik(v)))


def mod_istatistik(Lk, cfs, a, b, gecerli):
    """M = en büyük_{c, s∈{+1,−1}, gecikme 0…10} Pearson(L_k, max(0, s·cos φ_c(t − gecikme))) I = [a, b) üzerinde
    (W-başvuru koordinatı; gecikme np.roll ile, referans betiklerle aynı)."""
    best = -1.0
    g = gecerli[a:b]
    y = Lk[a:b][g]
    if len(y) < 3 or y.std() == 0:
        return best
    for cf in cfs:
        for s in (1, -1):
            for lag in range(0, MOD_LAG + 1):
                x = np.maximum(0, s * np.roll(cf, lag))[a:b][g]
                if x.std() > 0:
                    best = max(best, float(np.corrcoef(x, y)[0, 1]))
    return best


def mod_p(Lk, cfs, a, b, gecerli, rng, n=MOD_N):
    """Boş dağılım: üç bileşen birlikte, W uzunluğunda dairesel kaydırma, kaydırma tamsayı rng.integers(120, |W| − 120)
    (referans betikle aynı; okuma O-15). p = (1 + #{M₀ ≥ M}) / (n + 1)."""
    W = len(cfs[0])
    o = mod_istatistik(Lk, cfs, a, b, gecerli)
    say = 0
    for _ in range(n):
        k = int(rng.integers(MOD_KAY, W - MOD_KAY))
        say += mod_istatistik(Lk, [np.roll(c, k) for c in cfs], a, b, gecerli) >= o
    return o, (1 + say) / (n + 1)


# ------------------------------------------------------------------ §6.6 ölçülen gerilme
def tau_kpa(pgv_ms):
    """τ = G · PGV / c (G 30 GPa, c 3,5 km/s); kPa."""
    return G_MODUL * pgv_ms / C_HIZ / 1e3


def pgv_ist(vZ, vR, vT, W):
    a, b = W
    x = np.nanmax(np.abs(np.array([vZ[a:b], vR[a:b], vT[a:b]])))
    return float(x) if np.isfinite(x) else None


def rotasyon_ne_rt(n, e, baz_derece):
    """N/E → R/T (obspy.signal.rotate.rotate_ne_rt ile aynı formül; baz: istasyondan dış merkeze azimut)."""
    ba = math.radians(baz_derece)
    r = -e * math.sin(ba) - n * math.cos(ba)
    t = -e * math.cos(ba) + n * math.sin(ba)
    return r, t


# ------------------------------------------------------------------ §7.4 MDA
def tremor_zarfi(tt):
    """300 sn, 20 sn periyotlu yarım sinüs, 10 sn kenar yumuşatma (yapay sınamayla aynı)."""
    tt = np.asarray(tt, dtype=np.float64)
    e = np.zeros(len(tt))
    m = (tt >= 0) & (tt < MDA_SURE)
    e[m] = np.maximum(0, np.sin(2 * np.pi * tt[m] / MDA_PER)) * np.minimum(1, np.minimum(tt[m], MDA_SURE - tt[m])
                                                                           / MDA_KENAR)
    return e


def yapay_tremor_yer(gauss, fs, n, t_ilk, t_varis, H_norm=None):
    """Bir istasyon bileşeninin yapay tremoru, A_300 = 1 (m/s; yer biriminde 2–8 Hz RMS 300 sn boyunca), istasyonun
    kesintisiz örnek ızgarasında (t_ilk + i/fs, i < n). gauss: o bileşen için çekilmiş Gauss gerçekleşmesi
    (round(300·fs) örnek). H_norm verilirse (rfft frekanslarında H(f)/S) frekans ortamında çarpılır (§7.4, D14)."""
    t = t_ilk + np.arange(n) / fs
    tt = t - t_varis
    on = (tt >= 0) & (tt < MDA_SURE)
    idx = np.flatnonzero(on)
    s = np.zeros(n)
    k = min(len(idx), len(gauss))
    s[idx[:k]] = gauss[:k] * tremor_zarfi(tt[idx[:k]])
    sb = bant_gecir(s, fs, *BANT_YUKSEK)                      # "2–8 Hz süzülmüş"
    y0 = bant_gecir(sb, fs, *BANT_YUKSEK)                     # zincirin 2–8 Hz süzgecinden geçmiş hali
    rms = np.sqrt(np.mean(y0[on] ** 2)) if on.any() else 0.0
    if rms > 0:
        sb = sb / rms
    if H_norm is not None:
        sb = np.fft.irfft(np.fft.rfft(sb) * H_norm, n)
    return sb


def basamak(Aler, P, q):
    """§7.4: P ≥ q olan ve üstündeki bütün basamaklarda da bu şartı sağlayan en küçük basamak; yoksa None."""
    for j in range(len(Aler)):
        if all(p >= q for p in P[j:]):
            return float(Aler[j])
    return None


def ara_deger(Aler, P, q):
    """D2/D3: P'nin log10 A'ya göre doğrusal ara değerlemesi (referansla aynı)."""
    la = np.log10(Aler)
    for j in range(1, len(Aler)):
        if P[j - 1] < q <= P[j]:
            return float(10 ** (la[j - 1] + (q - P[j - 1]) / (P[j] - P[j - 1]) * (la[j] - la[j - 1])))
    return None


def mda_ozet(P, n_deneme, Aler=A_BASAMAK):
    """A50/A90 (nm/s) ya da 'belirsiz' (< 20 deneme, okuma O-16) ya da '> 100 µm/s'."""
    if n_deneme < MDA_MIN_DENEME:
        return dict(A50='belirsiz', A90='belirsiz', n_deneme=n_deneme)
    a50, a90 = basamak(Aler, P, 0.5), basamak(Aler, P, 0.9)
    return dict(A50=a50 if a50 is not None else '> 100 µm/s', A90=a90 if a90 is not None else '> 100 µm/s',
                n_deneme=n_deneme)


# ------------------------------------------------------------------ §7.5 kestirici
def kestirici_ist(x, Ip, maske):
    """a_i = √(max(0, ⟨C²⟩_I′ − ⟨C²⟩_R) · 2/π); maskeli ve kayıtsız saniyeler çıkarılır (okuma O-17)."""
    lo, hi = Ip
    R0, R1 = x['R']
    gi = ~maske[lo:hi] & np.isfinite(x['Cy'][lo:hi])
    gr = ~maske[R0:R1] & np.isfinite(x['Cy'][R0:R1])
    if not gi.any() or not gr.any():
        return None
    return float(np.sqrt(max(0.0, np.mean(x['Cy'][lo:hi][gi] ** 2) - np.mean(x['Cy'][R0:R1][gr] ** 2)) * 2 / np.pi))


# ------------------------------------------------------------------ §8 binom, X_min, p_min, bant
def bant(n):
    return 'tam' if n >= 8 else ('zayıf' if n >= 5 else 'veri yok')


def binom_ust(n, p, x):
    """P(Bin(n, p) ≥ x) (tr7_onkayit_sayilar.py ile aynı)."""
    return sum(math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(x, n + 1))


def cp_ust(f, N, a=0.05):
    """Clopper–Pearson tek yanlı %95 üst sınırı (tr7_onkayit_sayilar.py ile aynı ikiye bölme)."""
    if f >= N:
        return 1.0
    lo, hi = f / N, 1.0
    for _ in range(200):
        m = (lo + hi) / 2
        cdf = sum(math.comb(N, k) * m ** k * (1 - m) ** (N - k) for k in range(0, f + 1))
        lo, hi = (m, hi) if cdf > a else (lo, m)
    return (lo + hi) / 2


def k2_gecer(f, N):
    return f <= math.floor(FAR_K2 * N)


def x_min(n, f, N, alfa=0.05):
    """§8: X_min(n, f) = P(Bin(n, p_üst) ≥ X) ≤ α olan en küçük X ∈ [2, n]; yoksa None; K2 kalırsa 'K2'."""
    if not k2_gecer(f, N):
        return 'K2'
    pu = cp_ust(f, N)
    return next((x for x in range(2, n + 1) if binom_ust(n, pu, x) <= alfa), None)


def p_min(n_acik):
    return (1 - 0.05 ** (1 / n_acik)) / 0.9 if n_acik >= 5 else None


# ------------------------------------------------------------------ hızlı kutulama (aynı ızgarada çok kez)
class Kutulayici:
    """`kutula` ile aynı sonuç; aynı (t0, fs, n, geçerli aralık) için kutu dizinlerini bir kez hesaplar.
    gecerli: (lo, hi) epoch — yalnız bu aralıktaki örnekler (parçanın Hilbert kenarları dışı); None ise kutula'nın
    kuralı (t0 + 10, son − 10)."""

    def __init__(self, t0, fs, n, gecerli=None):
        t = t0 + np.arange(n) / fs
        if gecerli is None:
            gecerli = (t0 + HILBERT_KENAR, t0 + (n - 1) / fs - HILBERT_KENAR)
        lo, hi = gecerli
        tut = (t >= lo - 1e-9) & (t <= hi + 1e-9)
        self.tut = tut
        self.bos = not tut.any()
        if self.bos:
            self.k0, self.m = 0, 0
            return
        tk = t[tut]
        kk = np.floor(tk + 1e-7).astype(np.int64)
        self.k0 = int(kk[0])
        self.idx = kk - self.k0
        self.m = int(self.idx[-1]) + 1
        say = np.bincount(self.idx, minlength=self.m)
        self.ok = say > 0
        self.say = np.where(self.ok, say, 1)
        # kısmi ilk/son kutu: ızgarada önceki/sonraki örnek de aynı kutuya düşerdi ama tutulmadı
        if tk[0] - 1.0 / fs >= self.k0 - 1e-7:
            self.ok[0] = False
        if tk[-1] + 1.0 / fs < self.k0 + self.m - 1e-7:
            self.ok[-1] = False

    def __call__(self, genlik):
        if self.bos:
            return 0, np.zeros(0)
        top = np.bincount(self.idx, weights=np.asarray(genlik)[self.tut], minlength=self.m)
        e = np.full(self.m, np.nan)
        e[self.ok] = top[self.ok] / self.say[self.ok]
        return self.k0, e


# ------------------------------------------------------------------ §7.4 MDA denemesi
def mda_deneme(ist, mda_veri, hnorm, r_km, maske, Wb, eksen_k0, rng, n_bas=1, Aler=A_BASAMAK, birim=1e-9,
               kural=TAM, Wb_bas=None):
    """Algılama vermemiş bir negatif pencerede (ya da yapay sınamada) yapay tremor enjeksiyonu.

    ist: istasyon() kayıtları (veri; 12 sınırından sonra, `iz_sira` sırasıyla). mda_veri[i]: {bileşen: [parça]}; parça:
    dict(t0, fs, n, i0, i1, a28, a051) — a28/a051 verinin [i0, i1) örneklerindeki analitik sinyalleri.
    hnorm[i][bileşen]: f(n, fs) -> H(f)/S (rfft frekanslarında) ya da None (yanıtsız). r_km[i]: hiposantr uzaklığı.
    Çekiliş sırası (§7.4, K-c): her denemede önce başlangıç (rng.integers(60, |W| − 360)), sonra istasyon ve bileşen
    sırasıyla (Z, N, E) round(300·fs) Gauss örneği. Wb: (pencere, segment) W birleşimi (eksen dizini); başlangıç
    Wb başına göredir. Varış = Wb başı + başlangıç + r_i / 3,5 km/s. A (Aler, nm/s) × birim × 25/r_i.
    R'ye ekleme yapılmaz: m ve σ verinin R'sinden (ist kayıtlarındaki) kalır. Dönüş: [dict(bas, alg=[bool…])]."""
    Wlen = Wb[1] - Wb[0]
    w_epoch0 = eksen_k0 + Wb[0] if Wb_bas is None else Wb_bas
    out = []
    for _ in range(n_bas):
        bas = int(rng.integers(MDA_BAS[0], Wlen - MDA_BAS[1]))
        cek = []
        for i in range(len(ist)):
            d = {}
            for c in 'ZNE':
                if c in mda_veri[i]:
                    fs = mda_veri[i][c][0]['fs'] if mda_veri[i][c] else 100.0
                    d[c] = rng.standard_normal(int(round(MDA_SURE * fs)))
            cek.append(d)
        # yapay bileşenler: kesintisiz ızgarada üret, yanıtla çarp, parçalara böl, zincirden geçir
        syn = []
        for i, x in enumerate(ist):
            ta = w_epoch0 + bas + r_km[i] / MDA_HIZ
            ol = 25.0 / r_km[i] * birim
            d = {}
            for c, parcalar in mda_veri[i].items():
                if not parcalar:
                    continue
                fs = parcalar[0]['fs']
                g0 = parcalar[0]['t0']
                son = max(p['t0'] + (p['n'] - 1) / fs for p in parcalar)
                n_iz = int(round((son - g0) * fs)) + 1
                H = hnorm[i].get(c) if hnorm and hnorm[i] else None
                s = yapay_tremor_yer(cek[i][c], fs, n_iz, g0, ta, H(n_iz, fs) if H else None) * ol
                ps = []
                for p in parcalar:
                    j0 = int(round((p['t0'] - g0) * fs))
                    xs = ortalama_egilim(s[j0:j0 + p['n']])
                    a28 = parca_analitik(xs, fs, BANT_YUKSEK)[p['i0']:p['i1']]
                    a051 = parca_analitik(xs, fs, BANT_ALCAK)[p['i0']:p['i1']]
                    kt = Kutulayici(p['t0'] + p['i0'] / fs, fs, p['i1'] - p['i0'],
                                    (p['t0'] + HILBERT_KENAR, p['t0'] + (p['n'] - 1) / fs - HILBERT_KENAR))
                    ps.append((p, a28, a051, kt))
                d[c] = ps
            syn.append(d)
        alg = []
        n_eks = len(maske)
        for A in Aler:
            ist_A = []
            for i, x in enumerate(ist):
                ey, ed = [], []
                for c in 'ZNE':
                    if c not in syn[i]:
                        continue
                    ey_c = np.full(n_eks, np.nan)
                    ed_c = np.full(n_eks, np.nan)
                    for p, a28, a051, kt in syn[i][c]:
                        k0, e = kt(np.abs(p['a28'] + A * a28))
                        eksene(eksen_k0, n_eks, k0, e, ey_c)
                        k0, e = kt(np.abs(p['a051'] + A * a051))
                        eksene(eksen_k0, n_eks, k0, e, ed_c)
                    ey.append(ey_c)
                    ed.append(ed_c)
                Cy = x['Cy'].copy()
                Cd = x['Cd'].copy()
                if ey:
                    cy, cd = f32(birlesik(ey)), f32(birlesik(ed))
                    ok = np.isfinite(cy)
                    ok[:x['R'][1]] = False                    # R'ye ekleme yapılmaz
                    Cy[ok] = cy[ok]
                    ok = np.isfinite(cd)
                    ok[:x['R'][1]] = False
                    Cd[ok] = cd[ok]
                L = L_seri(Cy)
                Ld = L_seri(Cd)
                y = dict(x, Cy=Cy, Cd=Cd, L=L, Ld=Ld)
                y['ax'] = asimlar(L, x['m'], x['s'], x['W'], maske) if x['s'] > 0 else []
                ist_A.append(y)
            alg.append(pencere_algila(ist_A, maske, Wb, kural=kural)['algilama'])
        out.append(dict(bas=bas, alg=alg))
    return out
