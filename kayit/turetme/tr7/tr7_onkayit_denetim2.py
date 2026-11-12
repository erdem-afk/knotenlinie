#!/usr/bin/env python3
"""TR-7 ön kayıt sürüm 2, §7.1: İNCELEME-1 düzeltmelerinin gerektirdiği yeni yapay denetimlerin (KD) referans değerleri.

YALNIZ YAPAY VERİ; numpy ve standart kitaplık. Gerçek dalga formu okunmaz, ağa çıkılmaz.
Zarf zinciri `tr7_onkayit_yapay.py` ile aynıdır (20 Hz, FFT ile 4 kutuplu ileri-geri Butterworth |H|^2, Hilbert, 1 sn
ortalama, 3 bileşen karesel ortalama, 5 sn kayan ortalama, log10; R 3600 sn, W 1900 sn; aşım m + 4σ). Bu betik ona
sürüm 2'nin kurallarını ekler: §6.2.7 köprüleme (maskeli saniye köprülenmez), §6.3 bağlantılı bileşen kümesi,
§6.5 madde 1/1a (maske), 2 (darbe; istasyon başına c_p'si en büyük parça), 3 (sızıntı, Δ = log10 artışı, istasyonun
aşım saniyelerinde; İNCELEME-1'in küme aralığı I üzerindeki değişkesi de karşılaştırma için hesaplanır),
3a (taban kayması); §7.5 kestirici (I′); A_300; §7.4 basamak kuralı; yanıtla çarpılmış enjeksiyon.

Her denetim için "doğru kod" (ön kayıt metni) ve "bilinen yanlış kod" aynı yapay pencerelerde değerlendirilir;
doğru kod ikinci, bağımsız bir tohumla da koşulur. Kabul bantları ön kayıt §7.1 tablosundadır.

Kullanım: python3 -I -B tr7_onkayit_denetim2.py <denetim> <tohum> <n_pencere>
  denetim ∈ D5b D6 D6b D7 D7b D7c D7d D10 D12 D12b D13 D14 O4 A300
  ek bağımsız değişken: D5b <A> [kaydirma|karistirma]; D6 [A]; D6b <S–P>[:A]; D7b <A>; D7c <A>:<gauss|kentsel>;
  D7d [gauss|kentsel]; D10 <yarim|sabit>; D12b <A>:<sönüm sn> (6,0 ≤ M < 7,0 P vekili, +60 ve +30 sn maske);
  D14 [jeofon4.5|bh20]
Çıktı: tek satır JSON (stdout). Toplama: tr7_onkayit_denetim2_kos.py.
"""
import json, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tr7_onkayit_yapay as Y            # noqa: E402  (aynı süzgeç, analitik sinyal, 1 Hz zarf)

FS, R_S, W_S, N = Y.FS, Y.R_S, Y.W_S, Y.N
T = R_S + W_S
F = Y.f
H28 = Y.bw2(F, 2, 8)
H051 = Y.bw2(F, 0.5, 1)
KSIG, BOSLUK, KMIN, NUST = 4.0, 20, 30, 15
t_ornek = np.arange(N) / FS


# ------------------------------------------------------------------ üretim
def analitik(S):
    return Y.analitik(S)


def gurultu(rng, tur='gauss'):
    """Bileşen başına (y: 2-8 Hz, d: 0,5-1 Hz) analitik gürültü, her bant RMS 1."""
    X = np.fft.rfft(rng.standard_normal(N))
    y = analitik(X * H28)
    y /= np.sqrt(np.mean(y.real ** 2))
    d = analitik(X * H051)
    d /= np.sqrt(np.mean(d.real ** 2))
    if tur == 'kentsel':      # 2-8 Hz'te yavaş (≈300 sn) rastgele genlik oynaması, ×exp(0,35 z)
        z = np.fft.irfft(np.fft.rfft(rng.standard_normal(N)) * Y.bw2(F, 1e-6, 1 / 300.0), N)
        y *= np.exp(0.35 * z / z.std())
    elif tur == 'rampa':      # Ö4 bilgi: R başından W sonuna doğrusal ×2 yükselen 2-8 Hz gürültü
        y *= 1 + t_ornek / T
    return y, d


def bicim(ad):
    if ad == 'bant28':
        return H28
    if ad == 'duz':                      # 0,5-8 Hz düz
        return Y.bw2(F, 0.5, 8)
    if ad == 'koda':                     # genlik ∝ f^-1, 0,5-8 Hz
        return Y.bw2(F, 0.5, 8) / np.maximum(F, 0.5)
    raise ValueError(ad)


def yanit(ad):
    if ad is None:
        return 1.0
    if ad == 'jeofon4.5':                # 4,5 Hz jeofon, ζ = 0,7, yüksek frekansta 1'e normalize
        fn, z = 4.5, 0.7
        return -F ** 2 / (fn ** 2 - F ** 2 + 2j * z * fn * F)
    if ad == 'bh20':                     # 20 sps BH: yumuşatma süzgecine benzer dik alçak geçiren, 7 Hz
        return 1 / np.sqrt(1 + (F / 7.0) ** 20)
    raise ValueError(ad)


def sinyal(rng, env, sekil='bant28', norm=None, H=None):
    """Bileşen başına yapay sinyal (y, d), zarf env (FS örnekli). Ölçek: y bandının gerçel RMS'i `norm` maskesinde 1
    (yer biriminde, H uygulanmadan önce); H verilirse sonra kanal yanıtıyla çarpılır."""
    S = np.fft.rfft(rng.standard_normal(N) * env) * bicim(sekil)
    y0 = analitik(S * H28)
    m = env > 0 if norm is None else norm
    k = 1 / np.sqrt(np.mean(y0.real[m] ** 2))
    Hs = yanit(H)
    return analitik(S * H28 * Hs) * k, analitik(S * H051 * Hs) * k


def zarf_yarim(bas, sure=300, per=20.0):
    tt = t_ornek - (R_S + bas)
    e = np.zeros(N)
    m = (tt >= 0) & (tt < sure)
    e[m] = np.maximum(0, np.sin(2 * np.pi * tt[m] / per)) * np.minimum(1, np.minimum(tt[m], sure - tt[m]) / 10)
    return e


def zarf_sabit(bas, sure=300):
    tt = t_ornek - (R_S + bas)
    e = np.zeros(N)
    m = (tt >= 0) & (tt < sure)
    e[m] = np.minimum(1, np.minimum(tt[m], sure - tt[m]) / 10)
    return e


def zarf_patlama(rng, bas, yuk=2.0, sure=300):
    tt = t_ornek - (R_S + bas)
    e = np.zeros(N)
    k = 0.0
    while True:
        k += rng.exponential(15)
        d = rng.uniform(5, 15)
        if k + d > sure:
            break
        m = (tt >= k) & (tt < k + d)
        e[m] = np.minimum(1, np.minimum(tt[m] - k, k + d - tt[m]) / yuk)
        k += d
    return e


def zarf_deprem(bas, sp, p_oran=0.25, sonum=5.0):
    """Yerel deprem: P (tepenin p_oran'ı) bas'ta, S bas+sp'de; ani başlangıç, sonum sn e-katlı sönüm."""
    tt = t_ornek - (R_S + bas)
    return (np.where(tt >= 0, p_oran * np.exp(-np.maximum(tt, 0) / sonum), 0)
            + np.where(tt >= sp, np.exp(-np.maximum(tt - sp, 0) / sonum), 0))


def zarf_tele(bas, sonum=60.0):
    tt = t_ornek - (R_S + bas)
    return np.where(tt >= 0, np.exp(-np.maximum(tt, 0) / sonum), 0)


def ilk5(bas):
    tt = t_ornek - (R_S + bas)
    return (tt >= 0) & (tt < 5)


def C(nl, sl, A, band):
    """Birleşik 1 Hz zarf: nl, sl bileşen listeleri [(y, d)]; band 0 = 2-8 Hz, 1 = 0,5-1 Hz."""
    cs = [Y.zarf1hz(np.abs(n[band] + (A * s[band] if s is not None else 0)))[:T] for n, s in zip(nl, sl)]
    return np.sqrt(np.mean(np.array(cs) ** 2, 0))


# ------------------------------------------------------------------ algılayıcı (sürüm 2 metni)
def L_ve_ist(c, maske):
    L = np.log10(np.convolve(c, np.ones(5) / 5, 'same'))
    r = np.ones(T, bool)
    r[:5] = False
    r[R_S - 5:] = False
    r &= ~maske
    x = L[r]
    m = np.median(x)
    return L, m, 1.4826 * np.median(np.abs(x - m))


def asimlar(L, m, s, maske):
    e = (L[R_S:] > m + KSIG * s) & ~maske[R_S:]
    mw = maske[R_S:]
    w = np.flatnonzero(e)
    out = []
    if len(w) == 0:
        return out
    a = b = w[0]
    n = 1
    for x in w[1:]:
        if x - b - 1 <= BOSLUK and not mw[b + 1:x].any():
            b = x
            n += 1
        else:
            if b - a + 1 >= KMIN and n >= NUST:
                out.append((a, b + 1))
            a = b = x
            n = 1
    if b - a + 1 >= KMIN and n >= NUST:
        out.append((a, b + 1))
    return out


def pearson_max(x, y, gecerli):
    best = -1.0
    n = len(x)
    for lag in range(-10, 11):
        if lag >= 0:
            xx, yy, g = x[lag:], y[:n - lag], gecerli[lag:] & gecerli[:n - lag]
        else:
            xx, yy, g = x[:lag], y[-lag:], gecerli[:lag] & gecerli[-lag:]
        xx, yy = xx[g], yy[g]
        if len(xx) > 10 and xx.std() > 0 and yy.std() > 0:
            best = max(best, float(np.corrcoef(xx, yy)[0, 1]))
    return best


def kumeler(ist, maske):
    """ist: [dict(L, ax)] -> tutarlı kümeler [dict(uyeler, parcalar, I)] (§6.3, bağlantılı bileşen)."""
    parc = [(k, a, b) for k, x in enumerate(ist) for a, b in x['ax']]
    ust = list(range(len(parc)))

    def bul(i):
        while ust[i] != i:
            ust[i] = ust[ust[i]]
            i = ust[i]
        return i
    for i in range(len(parc)):
        for j in range(i + 1, len(parc)):
            if parc[i][1] - 20 <= parc[j][2] + 20 and parc[j][1] - 20 <= parc[i][2] + 20:
                ust[bul(i)] = bul(j)
    gr = {}
    for i, p in enumerate(parc):
        gr.setdefault(bul(i), []).append(p)
    out = []
    for ps in gr.values():
        uy = sorted({p[0] for p in ps})
        if len(uy) < 3:
            continue
        lo = max(0, min(p[1] for p in ps) - 60)
        hi = min(W_S, max(p[2] for p in ps) + 60)
        g = ~maske[R_S + lo:R_S + hi]
        n_ok = 0
        for i1 in range(len(uy)):
            for i2 in range(i1 + 1, len(uy)):
                x = ist[uy[i1]]['L'][R_S + lo:R_S + hi]
                y = ist[uy[i2]]['L'][R_S + lo:R_S + hi]
                if pearson_max(x, y, g) >= 0.5:
                    n_ok += 1
        if n_ok >= 3:
            out.append(dict(uyeler=uy, parcalar=ps, I=(lo, hi)))
    return out


def darbe(Cy, parcalar, kip='dogru'):
    """§6.5.2: istasyonun c_p'si en büyük parçası. kip: 'dogru', 'yanlis_on' (ön şart c_p/2), 'yanlis_yumusak'
    (5 sn yumuşatılmış C üzerinde)."""
    c = np.convolve(Cy, np.ones(5) / 5, 'same') if kip == 'yanlis_yumusak' else Cy
    en = None
    for a, b in parcalar:
        seg = c[R_S + a:R_S + b]
        k = int(np.argmax(seg))
        if en is None or seg[k] > en[0]:
            en = (seg[k], R_S + a + k)
    cp, tp = en
    on_esik = cp / 2 if kip == 'yanlis_on' else cp / 8
    return bool((c[tp - 2:tp] <= on_esik).any() and (c[tp + 1:tp + 21] <= cp / 2).any())


def ayikla(ist, kume, maske):
    """Kümenin ayıklama bayrakları (ön kayıt §6.5; yanlış kod değişkeleri dahil)."""
    lo, hi = kume['I']
    g = ~maske[R_S + lo:R_S + hi]
    uy = kume['uyeler']
    yarim = len(uy) / 2
    bay = {}
    for kip in ('dogru', 'yanlis_on', 'yanlis_yumusak'):
        n = sum(darbe(ist[k]['Cy'], [(a, b) for kk, a, b in kume['parcalar'] if kk == k], kip) for k in uy)
        bay['darbe_' + kip] = n >= yarim
    nd = ni = nz = 0
    for k in uy:
        x = ist[k]
        # sürüm 2 (§6.5.3): istasyonun kümedeki aşım saniyeleri (parçaların içinde, L > m + 4σ, maskesiz)
        sec = np.zeros(T, bool)
        for kk, a, b in kume['parcalar']:
            if kk == k:
                sec[R_S + a:R_S + b] = True
        sec &= (x['L'] > x['m'] + KSIG * x['s']) & ~maske
        dy_a, dd_a = np.median(x['L'][sec]) - x['m'], np.median(x['Ld'][sec]) - x['md']
        nd += dd_a >= dy_a
        # İNCELEME-1 Ö6 metni: küme aralığı I üzerinde medyan (yapayda D7c'yi geçemedi; §17)
        Ly, Ld = x['L'][R_S + lo:R_S + hi][g], x['Ld'][R_S + lo:R_S + hi][g]
        dy, dd = np.median(Ly) - x['m'], np.median(Ld) - x['md']
        ni += dd >= dy
        nz += (dd / x['sd']) >= (dy / x['s'])          # sürüm 1 kuralı (z, I üzerinde): bilinen yanlış kod
    bay['sizinti_dogru'] = nd >= yarim
    bay['sizinti_inc1_I'] = ni >= yarim
    bay['sizinti_yanlis_z'] = nz >= yarim
    bay['sizinti_yanlis_ters'] = (len(uy) - nd) >= yarim   # eşitsizlik ters: Δ_y ≥ Δ_d (aşım saniyelerinde)
    nt = sum(any(b >= W_S - 60 for kk, a, b in kume['parcalar'] if kk == k) for k in uy)
    bay['taban'] = nt >= yarim
    return bay


def pencere(stations, maske=None):
    """stations: [(Cy, Cd)] -> (tutarlı kümeler, istasyon kayıtları)."""
    maske = np.zeros(T, bool) if maske is None else maske
    ist = []
    for Cy, Cd in stations:
        L, m, s = L_ve_ist(Cy, maske)
        Ld, md, sd = L_ve_ist(Cd, maske)
        ist.append(dict(Cy=Cy, L=L, m=m, s=s, Ld=Ld, md=md, sd=sd, ax=asimlar(L, m, s, maske) if s > 0 else []))
    return kumeler(ist, maske), ist


def kalan(ks, ist, maske, kural):
    """kural: atılma nedenleri kümesi (ör. {'darbe_dogru', 'sizinti_dogru', 'taban'}). Sağ kalan küme var mı."""
    for k in ks:
        b = ayikla(ist, k, maske)
        if not any(b[x] for x in kural):
            return True
    return False


TAM = {'darbe_dogru', 'sizinti_dogru', 'taban'}


def istasyonlar(rng, n_ist, env, A, sekil='bant28', gtur='gauss', norm=None, H=None, kayma=None):
    st = []
    for i in range(n_ist):
        e = env if kayma is None else np.roll(env, int(round(kayma[i] * FS)))
        nl = [gurultu(rng, gtur) for _ in range(3)]
        sl = [sinyal(rng, e, sekil, norm, H) for _ in range(3)] if A else [None] * 3
        st.append((C(nl, sl, A, 0), C(nl, sl, A, 1)))
    return st


# ------------------------------------------------------------------ denetimler
def oran(x):
    return round(float(np.mean(x)), 3) if len(x) else None


def D6(rng, n, sp=None, A=20.0):
    """sp None: D6 (ani başlangıç, C ×A, 5 sn e-katlı sönüm, P yok); sayı: D6b (P = tepenin 1/4'ü, S–P = sp)."""
    alg, atil, atil_y, maske_at = [], [], [], []
    for _ in range(n):
        bas = int(rng.integers(60, W_S - 360))
        env = zarf_deprem(bas, 0 if sp is None else sp, p_oran=0.0 if sp is None else 0.25)
        tS = bas + (0 if sp is None else sp)
        st = istasyonlar(rng, 3, env, A, norm=ilk5(tS))
        ks, ist = pencere(st)
        alg.append(bool(ks))
        z = np.zeros(T, bool)
        if ks:
            atil.append(not kalan(ks, ist, z, {'darbe_dogru'}))
            atil_y.append(not kalan(ks, ist, z, {'darbe_yanlis_yumusak'}))
            mk = np.zeros(T, bool)
            mk[R_S + bas:R_S + bas + 70] = True        # katalogdaki olay, d ≈ 30 km: [t0, t0 + d/3 + 60]
            ks2, ist2 = pencere(st, mk)
            maske_at.append(not kalan(ks2, ist2, mk, set()))
    alg_yok = 1 - np.mean(alg)
    return dict(algilama=oran(alg), darbe_atilma_algilananda=oran(atil),
                algilanmama_ya_da_darbe=round(float(alg_yok + np.mean(alg) * (np.mean(atil) if atil else 0)), 3),
                yanlis_yumusak_algilanmama_ya_da_darbe=round(float(alg_yok + np.mean(alg) * (np.mean(atil_y) if atil_y else 0)), 3),
                katalog_maskesi_atilma=oran(maske_at))


def D7(rng, n, tur, A, gtur='gauss', sekil='bant28'):
    alg, at, at_y_on, at_tam, at_siz, at_siz_z, at_siz_i = [], [], [], [], [], [], []
    for _ in range(n):
        bas = int(rng.integers(60, W_S - 360))
        env = (zarf_yarim(bas) if tur == 'yarim' else zarf_patlama(rng, bas) if tur == 'patlama'
               else zarf_sabit(bas))
        st = istasyonlar(rng, 3, env, A, sekil=sekil, gtur=gtur)
        ks, ist = pencere(st)
        alg.append(bool(ks))
        if ks:
            z = np.zeros(T, bool)
            at.append(not kalan(ks, ist, z, {'darbe_dogru', 'sizinti_dogru'}))
            at_y_on.append(not kalan(ks, ist, z, {'darbe_yanlis_on', 'sizinti_dogru'}))
            at_tam.append(not kalan(ks, ist, z, TAM))
            at_siz.append(not kalan(ks, ist, z, {'sizinti_dogru'}))
            at_siz_z.append(not kalan(ks, ist, z, {'sizinti_yanlis_z'}))
            at_siz_i.append(not kalan(ks, ist, z, {'sizinti_inc1_I'}))
    return dict(algilama=oran(alg), darbe_ya_da_sizinti_atilma=oran(at), tam_kural_atilma_3a_dahil=oran(at_tam),
                yanlis_on_esik_atilma=oran(at_y_on), sizinti_atilma=oran(at_siz), yanlis_z_sizinti_atilma=oran(at_siz_z),
                inc1_I_sizinti_atilma=oran(at_siz_i))


def D7d(rng, n, A=20.0, gtur='gauss'):
    alg, siz, siz_t, siz_z, siz_i = [], [], [], [], []
    for _ in range(n):
        bas = int(rng.integers(60, W_S - 360))
        env = np.where(t_ornek - (R_S + bas) >= 0, np.exp(-np.maximum(t_ornek - (R_S + bas), 0) / 40.0), 0) * \
            np.minimum(1, np.maximum(t_ornek - (R_S + bas), 0) / 1.0)
        st = istasyonlar(rng, 3, env, A, sekil='koda', gtur=gtur, norm=ilk5(bas))
        ks, ist = pencere(st)
        alg.append(bool(ks))
        if ks:
            z = np.zeros(T, bool)
            siz.append(not kalan(ks, ist, z, {'sizinti_dogru'}))
            siz_t.append(not kalan(ks, ist, z, {'sizinti_yanlis_ters'}))
            siz_z.append(not kalan(ks, ist, z, {'sizinti_yanlis_z'}))
            siz_i.append(not kalan(ks, ist, z, {'sizinti_inc1_I'}))
    return dict(algilama=oran(alg), sizinti_atilma=oran(siz), yanlis_ters_sizinti_atilma=oran(siz_t),
                yanlis_z_sizinti_atilma=oran(siz_z), inc1_I_sizinti_atilma=oran(siz_i))


def D12(rng, n, A=5.0, sonum=60.0, kuyruklar=(240, 60)):
    alg, alg_tam = [], []
    at = {k: [] for k in kuyruklar}
    for _ in range(n):
        bas = int(rng.integers(60, W_S - 600))
        env = zarf_tele(bas, sonum)
        st = istasyonlar(rng, 3, env, A, norm=ilk5(bas), kayma=rng.uniform(-2, 2, 3))
        ks, ist = pencere(st)
        alg.append(bool(ks))
        z = np.zeros(T, bool)
        if ks:
            alg_tam.append(kalan(ks, ist, z, TAM))
            for son in kuyruklar:
                mk = np.zeros(T, bool)
                mk[R_S + bas - 10:R_S + bas + son] = True
                ks2, ist2 = pencere(st, mk)
                at[son].append(not kalan(ks2, ist2, mk, TAM))
    r = dict(algilama_maskesiz=oran(alg), ayiklamadan_sag_maskesiz=oran(alg_tam))
    r.update({f'maske_atilma_kuyruk{k}': oran(v) for k, v in at.items()})
    return r


def D10(rng, n, tur, A_etkin=3.0):
    r_dogru, r_eski, r_etkin = [], [], []
    for _ in range(n):
        bas = int(rng.integers(60, W_S - 360))
        env = zarf_yarim(bas) if tur == 'yarim' else zarf_sabit(bas)
        nl_all, sl_all, st = [], [], []
        a300 = []
        for i in range(3):
            nl = [gurultu(rng) for _ in range(3)]
            sl = [sinyal(rng, env) for _ in range(3)]          # A_etkin = 1 birimi
            on300 = (t_ornek >= R_S + bas) & (t_ornek < R_S + bas + 300)
            a300 += [np.sqrt(np.mean((A_etkin * s[0].real[on300]) ** 2)) for s in sl]
            st.append((C(nl, sl, A_etkin, 0), C(nl, sl, A_etkin, 1)))
        ks, ist = pencere(st)
        if not ks:
            continue
        k = ks[0]
        A300 = float(np.mean(a300))
        for liste, ek, bol in ((r_dogru, 0, A300), (r_eski, 60, A300), (r_etkin, 0, A_etkin)):
            lo = max(0, min(p[1] for p in k['parcalar']) - ek)
            hi = min(W_S, max(p[2] for p in k['parcalar']) + ek)
            a = [np.sqrt(max(0.0, np.mean(ist[u]['Cy'][R_S + lo:R_S + hi] ** 2) - np.mean(ist[u]['Cy'][:R_S] ** 2))
                         * 2 / np.pi) for u in k['uyeler']]
            liste.append(float(np.median(a)) / bol)
    med = lambda x: round(float(np.median(x)), 3) if x else None
    return dict(n_algilanan=len(r_dogru), kestirilen_bolu_A300_dogru=med(r_dogru),
                q05_q95=[round(float(q), 3) for q in np.quantile(r_dogru, [0.05, 0.95])] if r_dogru else None,
                yanlis_I_artieksi60=med(r_eski), yanlis_A_etkin_paydasi=med(r_etkin))


def P_egrisi(rng, n, Aler, H_ger=None, H_enj='ayni', n_ist=3):
    """A_300 ızgarasında algılama oranı (tam ayıklama). H_ger: verideki kanal yanıtı; H_enj: enjeksiyonda kullanılan
    ('ayni' = doğru kod, None = yanıtsız düz enjeksiyon: bilinen yanlış kod)."""
    say = np.zeros(len(Aler))
    for _ in range(n):
        bas = int(rng.integers(60, W_S - 360))
        env = zarf_yarim(bas)
        on300 = (t_ornek >= R_S + bas) & (t_ornek < R_S + bas + 300)
        H = H_ger if H_enj == 'ayni' else H_enj
        stl = []
        for i in range(n_ist):
            nl = [gurultu(rng) for _ in range(3)]
            sl = [sinyal(rng, env, norm=on300, H=H) for _ in range(3)]   # A_300 = 1 birimi (yer biriminde)
            stl.append((nl, sl))
        for j, A in enumerate(Aler):
            st = [(C(nl, sl, A, 0), C(nl, sl, A, 1)) for nl, sl in stl]
            ks, ist = pencere(st)
            say[j] += bool(ks) and kalan(ks, ist, np.zeros(T, bool), TAM)
    return say / n


def basamak(Aler, P, q):
    """§7.4: P ≥ q olan ve üstündeki bütün basamaklarda da sağlayan en küçük basamak."""
    for j in range(len(Aler)):
        if all(p >= q for p in P[j:]):
            return float(Aler[j])
    return None


def ara_deger(Aler, P, q):
    """D2: log10 A'ya göre doğrusal ara değerleme."""
    la = np.log10(Aler)
    for j in range(1, len(Aler)):
        if P[j - 1] < q <= P[j]:
            return float(10 ** (la[j - 1] + (q - P[j - 1]) / (P[j] - P[j - 1]) * (la[j] - la[j - 1])))
    return None


def D13(rng, n):
    A20 = np.array([10 ** (j / 20) for j in range(-12, -1)])          # 0,251 … 0,794 (A_300)
    A8 = np.array([10 ** (j / 8) for j in range(-5, 0)])               # sürüm 1 ızgarası: bilinen yanlış kod
    Aler = np.unique(np.round(np.concatenate([A20, A8]), 6))
    P = P_egrisi(rng, n, Aler)
    i20 = [int(np.flatnonzero(np.isclose(Aler, a))[0]) for a in A20]
    i8 = [int(np.flatnonzero(np.isclose(Aler, a))[0]) for a in A8]
    return dict(A_300=[round(float(a), 3) for a in Aler], P=[round(float(p), 3) for p in P],
                A50_basamak_j20=basamak(A20, P[i20], 0.5), A90_basamak_j20=basamak(A20, P[i20], 0.9),
                A50_basamak_j8_yanlis=basamak(A8, P[i8], 0.5), A90_basamak_j8_yanlis=basamak(A8, P[i8], 0.9),
                A50_ara_deger=ara_deger(A20, P[i20], 0.5), A90_ara_deger=ara_deger(A20, P[i20], 0.9))


def D14(rng, n, H='jeofon4.5'):
    Aler = np.array([10 ** (j / 40) for j in range(-24, 17)])          # 0,251 … 2,51 (A_300, yer biriminde)
    P_ger = P_egrisi(rng, n, Aler, H_ger=H, H_enj='ayni')
    P_yan = P_egrisi(rng, n, Aler, H_ger=H, H_enj=None)
    a50g, a50y = ara_deger(Aler, P_ger, 0.5), ara_deger(Aler, P_yan, 0.5)
    a90g, a90y = ara_deger(Aler, P_ger, 0.9), ara_deger(Aler, P_yan, 0.9)
    g = np.abs(yanit(H))
    return dict(yanit=H, g_2_4_6_8Hz=[round(float(np.interp(x, F, g)), 3) for x in (2, 4, 6, 8)],
                A50_yanitli=a50g, A90_yanitli=a90g, A50_duz_yanlis=a50y, A90_duz_yanlis=a90y)


def D5b(rng, n, A, null='kaydirma', n_kay=200):
    """tr7_onkayit_modulasyon.py modeli; 'bagimsiz' 20 sn kilitsiz yarım sinüs. null: 'kaydirma' (doğru),
    'karistirma' (bilinen yanlış kod: faz serisinin rastgele permütasyonu)."""
    W = 1900
    t = np.arange(W)

    def paket():
        t0 = 600
        f = np.interp(t, [t0 - 450, t0 + 450], [1 / 40, 1 / 15])
        ph = 2 * np.pi * np.cumsum(f) + rng.uniform(0, 2 * np.pi)
        return np.exp(-0.5 * ((t - t0) / 250) ** 2) * np.cos(ph)

    def faz(v):
        V = np.fft.fft(v)
        h = np.zeros(W)
        h[0] = 1
        h[1:(W + 1) // 2] = 2
        if W % 2 == 0:
            h[W // 2] = 1
        return np.cos(np.angle(np.fft.ifft(V * h)))

    def stat(L, cf, a, b):
        best = -1
        for s in (1, -1):
            for lag in range(0, 11):
                x = np.maximum(0, s * np.roll(cf, lag))[a:b]
                if x.std() > 0:
                    best = max(best, np.corrcoef(x, L[a:b])[0, 1])
        return best
    ok = 0
    for _ in range(n):
        v = paket()
        bas = int(rng.integers(450, 750))
        a, b = max(0, bas - 60), min(W, bas + 360)
        m = np.zeros(W)
        e = t - bas
        on = (e >= 0) & (e < 300)
        tap = np.minimum(1, np.minimum(e, 300 - e) / 10)
        m[on] = np.maximum(0, np.sin(2 * np.pi * e[on] / 20 + rng.uniform(0, 6.3))) * tap[on]
        m /= np.sqrt(np.mean(m[on] ** 2))
        c = np.sqrt(1 + (A * m) ** 2) * (1 + 0.1 * rng.standard_normal(W))
        L = np.log10(np.convolve(c, np.ones(5) / 5, 'same'))
        cf = faz(v)
        o = stat(L, cf, a, b)
        if null == 'kaydirma':
            nul = [stat(L, np.roll(cf, int(rng.integers(120, W - 120))), a, b) for _ in range(n_kay)]
        else:
            nul = [stat(L, rng.permutation(cf), a, b) for _ in range(n_kay)]
        ok += (1 + sum(x >= o for x in nul)) / (n_kay + 1) <= 0.01
    return dict(p_le_001_orani=round(ok / n, 3), bos_dagilim=null, kaydirma=n_kay)


def O4(rng, n):
    alg, at3a = [], []
    for _ in range(n):
        st = istasyonlar(rng, 3, np.zeros(N), 0.0, gtur='rampa')
        ks, ist = pencere(st)
        alg.append(bool(ks))
        if ks:
            at3a.append(not kalan(ks, ist, np.zeros(T, bool), {'taban'}))
    return dict(algilama_ayiklamasiz=oran(alg), taban_3a_atilma_algilananda=oran(at3a))


def A300():
    e = zarf_yarim(100)
    on300 = (t_ornek >= R_S + 100) & (t_ornek < R_S + 400)
    return dict(A300_bolu_A_etkin_yarim_sinus=round(float(np.sqrt(np.mean(e[on300] ** 2) / np.mean(e[e > 0] ** 2))), 4),
                not_='zarfın kendisinden (gürültüsüz); sinyal RMS oranı aynı zarfla ölçeklenir')


def main():
    ad, tohum, n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    rng = np.random.default_rng(tohum)
    ek = sys.argv[4] if len(sys.argv) > 4 else None
    if ad == 'D5b':
        r = D5b(rng, n, float(ek), null=(sys.argv[5] if len(sys.argv) > 5 else 'kaydirma'))
    elif ad == 'D6':
        r = D6(rng, n, A=float(ek) if ek else 20.0)
    elif ad == 'D6b':
        sp, A = (ek.split(':') + ['20'])[:2]
        r = D6(rng, n, sp=float(sp), A=float(A))
    elif ad == 'D7':
        r = D7(rng, n, 'yarim', 10.0)
    elif ad == 'D7b':
        r = D7(rng, n, 'patlama', float(ek))
    elif ad == 'D7c':
        A, g = ek.split(':')
        r = D7(rng, n, 'yarim', float(A), gtur=g, sekil='duz')
    elif ad == 'D7d':
        r = D7d(rng, n, gtur=ek or 'gauss')
    elif ad == 'D10':
        r = D10(rng, n, ek)
    elif ad == 'D12':
        r = D12(rng, n)
    elif ad == 'D12b':
        A, s = ek.split(':')
        r = D12(rng, n, A=float(A), sonum=float(s), kuyruklar=(60, 30))
    elif ad == 'D13':
        r = D13(rng, n)
    elif ad == 'D14':
        r = D14(rng, n, ek or 'jeofon4.5')
    elif ad == 'O4':
        r = O4(rng, n)
    elif ad == 'A300':
        r = A300()
    else:
        sys.exit('bilinmeyen denetim')
    print(json.dumps(dict(denetim=ad, ek=ek, tohum=tohum, n=n, sonuc=r), ensure_ascii=False))


if __name__ == '__main__':
    main()
