"""TR-7c İNCELEME-1: ön kayıt taslağı (sürüm 1, commit 4ba57ab) için bağımsız hesap. Yalnız yapay/kombinatorik hesap.

Gerçek dalga formu okunmaz, indirilmez; ağ isteği yoktur. Girdiler (yalnız okunur):
  kayit/turetme/tr7b/tr7b_sayim.json   (Chao 2012 S1 etiketleri, PGV_T, T0, Δ; üstveri)
  kayit/turetme/tr7c/tr7c_guc.py/.json (yeniden üretim için; tr7c_guc.py modül olarak yüklenir, ÇIKTISI depo DIŞINA,
                                         komut satırında verilen geçici dizine yazdırılır; depodaki json'a dokunulmaz)
  kayit/onkayit/TR-7c_INCELEME-0.md, TR-7c_tetiklenmis-tremor_ONKAYIT.md (Z1–Z8 birebir karşılaştırması)

Bölümler (çıktı anahtarları):
  1 z_aynen          : Z1–Z8 alıntılarının ön kayıtta birebir (boşluk normalleştirilerek) bulunup bulunmadığı.
  2 dal_izgarasi     : Z4 dallarının bütün tamsayı ızgarasında sayımı (çakışma / boşluk).
  3 yeniden_uretim   : tr7c_guc.py'nin yeniden koşusu, depodaki json ile sha256 karşılaştırması.
  4 bagimsiz         : kendi Clopper–Pearson (ikiye bölme), kendi hipergeometrik (lgamma) ve kendi D30M3 hesabı;
                       ayrıca Monte Carlo. Ön kayıttaki hücrelerle karşılaştırma.
  5 cift_N27_N28     : 2009-10-07 çiftinin pencere örtüşmesi; çifti tek sayma / ayrı sayma etkisi.
  6 kilitli_sizinti  : yüzey dalgasına kilitli, genliğe bağlı sızıntıda (m_f büyük) D30M3 yanlış kabulü; genliği eşlenmiş
                       4 N olayı kuralının etkisi ve bedeli.
  7 marmara          : K1c (b) olup "Parkfield modülasyonu geçti" etiketinin sağlanmama olasılığı.
  8 esik             : görülebilir en küçük etki, ×0,5 / ×2 (s₀'da), n_P = 8 / n_N = 20'de MDE; D1 için başvuru
                       istasyonlu P olayı sayısına göre güç.

Model (INCELEME-0 ile aynı varsayımlar; sonuç değil): olaylar bağımsız; P olayında gerçek algılama s, tremorsuz yanlış
alarm q; p_P = 1 − (1 − s)(1 − q); gerçek tremor algılaması m_t, sızıntı algılaması m_f olasılıkla modülasyonlu
(p ≤ 0,01); rastgele negatif pencere r, N_PK = 120.

Kullanım: python3 -I -B tr7c_inc1.py <geçici_dizin>
"""
import hashlib, importlib.util, json, math, os, re, sys

os.environ.setdefault('OMP_NUM_THREADS', '1')
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from scipy.stats import beta, fisher_exact  # noqa: E402

BU = os.path.dirname(os.path.abspath(__file__))
TR7C = os.path.dirname(BU)
TUR = os.path.dirname(TR7C)
KOK = os.path.dirname(os.path.dirname(TUR))
SAYIM = os.path.join(TUR, 'tr7b', 'tr7b_sayim.json')
GUC_PY = os.path.join(TR7C, 'tr7c_guc.py')
GUC_JSON = os.path.join(TR7C, 'tr7c_guc.json')
ONK = os.path.join(KOK, 'kayit', 'onkayit', 'TR-7c_tetiklenmis-tremor_ONKAYIT.md')
INC0 = os.path.join(KOK, 'kayit', 'onkayit', 'TR-7c_INCELEME-0.md')
CIKTI = os.path.join(BU, 'tr7c_inc1.json')
N_PK = 120


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


# ---------------------------------------------------------------- bağımsız yapı taşları
def lcomb(n, k):
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def hyper_ust(xp, n, xn, m):
    """Kendi uygulamam: P(X ≥ xp), X ~ Hipergeometrik(toplam n+m, başarı K = xp+xn, çekiliş n). lgamma ile."""
    K = xp + xn
    T = n + m
    lo, hi = max(0, K - m), min(K, n)
    tot = 0.0
    for x in range(max(xp, lo), hi + 1):
        tot += math.exp(lcomb(n, x) + lcomb(m, K - x) - lcomb(T, K))
    return min(1.0, tot)


def binom_sf(k, n, p):
    """P(Bin(n, p) ≥ k), doğrudan toplam."""
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    return sum(math.comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(k, n + 1))


def cp_ust_bisection(f, N):
    """Tek yanlı %95 Clopper–Pearson üst sınırı, ikiye bölmeyle: P(Bin(N, p) ≤ f) = 0,05."""
    if N == 0 or f >= N:
        return 1.0
    lo, hi = 0.0, 1.0
    for _ in range(80):
        mid = (lo + hi) / 2
        cdf = 1.0 - binom_sf(f + 1, N, mid)
        if cdf > 0.05:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def cp_ust_scipy(f, N):
    if N == 0 or f >= N:
        return 1.0
    return float(beta.ppf(0.95, f + 1, N - f))


_XM = {}


def xmin(n, f, N=N_PK, esik=0.05, cp=cp_ust_scipy):
    key = (n, f, N, esik, cp.__name__)
    if key not in _XM:
        pu = cp(f, N)
        v = None
        for X in range(2, n + 1):
            if binom_sf(X, n, pu) <= esik:
                v = X
                break
        _XM[key] = v
    return _XM[key]


def pbinom_dist(ps):
    d = np.zeros(len(ps) + 1)
    d[0] = 1.0
    for p in ps:
        d[1:] = d[1:] * (1 - p) + d[:-1] * p
        d[0] *= (1 - p)
    return d


# ---------------------------------------------------------------- kendi D30M3 hesabım
_FISH = {}


def fisher_ok(xp, n, xn, m):
    k = (xp, n, xn, m)
    if k not in _FISH:
        _FISH[k] = hyper_ust(xp, n, xn, m) <= 0.05
    return _FISH[k]


def p_d30m3(p_mod, p_nomod, qN, r=0.05, mod_esik=3, NPK=N_PK, mod_kural='mutlak', cp=cp_ust_bisection,
            ciftli_N=None, ek_kural=None):
    """D30M3 'sınandı' olasılığı (kendi uygulamam).

    p_mod[i], p_nomod[i]: P olayı i için (algılama ve modülasyonlu) / (algılama, modülasyonsuz) olasılıkları.
    qN[j]: N olayı j için algılama olasılığı. ciftli_N: (indis_listesi) aynı sonucu paylaşan, iki kez sayılan N olayı
    (tam bağımlı çift). ek_kural: (xp, mm, xn) dışında bir koşul gerekiyorsa çağrılır (bkz. bölüm 6).
    mod_kural: 'mutlak' → mm ≥ mod_esik; 'yari' → mm ≥ ⌈xp/2⌉ ve ≥ 1.
    """
    n = len(p_mod)
    # P tarafı: (xp, mm) ortak dağılımı
    D = {(0, 0): 1.0}
    for a, b in zip(p_mod, p_nomod):
        c0 = 1 - a - b
        Y = {}
        for (x, mm), w in D.items():
            for (dx, dm), w2 in (((1, 1), a), ((1, 0), b), ((0, 0), c0)):
                if w2 <= 0:
                    continue
                kk = (x + dx, mm + dm)
                Y[kk] = Y.get(kk, 0.0) + w * w2
        D = Y
    # N tarafı
    if ciftli_N is None:
        DN = pbinom_dist(qN)
        m = len(qN)
        DNd = {k: DN[k] for k in range(m + 1)}
    else:
        i, j = ciftli_N  # j, i'nin kopyası (tam bağımlı); i'nin olasılığı kullanılır
        tek = [q for k, q in enumerate(qN) if k not in (i, j)]
        DN0 = pbinom_dist(tek)
        m = len(qN)
        DNd = {}
        for k in range(len(tek) + 1):
            DNd[k] = DNd.get(k, 0.0) + DN0[k] * (1 - qN[i])
            DNd[k + 2] = DNd.get(k + 2, 0.0) + DN0[k] * qN[i]
    # f_PK
    PF = pbinom_dist([r] * NPK)
    top = 0.0
    for f in range(NPK + 1):
        if PF[f] < 1e-13:
            continue
        if NPK < 5 or f / NPK > 0.30:
            continue
        xm = xmin(n, f, NPK, cp=cp)
        if xm is None:
            continue
        esik_x = max(math.ceil(n / 2), xm)
        for (xp, mm), w in D.items():
            if xp < esik_x:
                continue
            if mod_kural == 'mutlak' and mm < mod_esik:
                continue
            if mod_kural == 'yari' and mm < max(1, math.ceil(xp / 2)):
                continue
            for xn, wn in DNd.items():
                if wn < 1e-15:
                    continue
                if not fisher_ok(xp, n, xn, m):
                    continue
                if ek_kural is not None and not ek_kural(xp, mm, xn):
                    continue
                top += PF[f] * w * wn
    return top


def sabit_model(s, q, m_t, m_f=0.05, nP=10):
    pt = s
    pf = (1 - s) * q
    return [pt * m_t + pf * m_f] * nP, [pt * (1 - m_t) + pf * (1 - m_f)] * nP


def monte_carlo(s, q, m_t, m_f=0.05, nP=10, nN=30, r=0.05, reps=200000, tohum=20261117):
    """Bağımsız Monte Carlo (kendi kuralımla): D30M3."""
    rng = np.random.default_rng(tohum)
    gt = rng.random((reps, nP)) < s
    yf = rng.random((reps, nP)) < q
    alg = gt | yf
    mod = np.where(gt, rng.random((reps, nP)) < m_t, rng.random((reps, nP)) < m_f) & alg
    xp = alg.sum(1)
    mm = mod.sum(1)
    xn = (rng.random((reps, nN)) < q).sum(1)
    f = rng.binomial(N_PK, r, reps)
    ok = np.zeros(reps, bool)
    for k in range(reps):
        if f[k] / N_PK > 0.30:
            continue
        xm = xmin(nP, int(f[k]), N_PK, cp=cp_ust_scipy)
        if xm is None or xp[k] < max(math.ceil(nP / 2), xm) or mm[k] < 3:
            continue
        ok[k] = fisher_ok(int(xp[k]), nP, int(xn[k]), nN)
    p = ok.mean()
    return float(p), float(math.sqrt(p * (1 - p) / reps))


# ---------------------------------------------------------------- 1. Z1–Z8 birebir
def norm(t):
    t = re.sub(r'^\s*>\s?', '', t, flags=re.M)
    return re.sub(r'\s+', ' ', t).strip()


def z_aynen():
    inc = open(INC0, encoding='utf-8').read()
    onk = open(ONK, encoding='utf-8').read()
    bol6 = inc.split('## 6. Düzeltmeler')[1].split('## 7.')[0]
    parcalar = re.split(r'\n\*\*(Z\d)\b[^\n]*\n', '\n' + bol6)
    sonuc = {}
    onk_n = norm(onk)
    for i in range(1, len(parcalar), 2):
        ad, govde = parcalar[i], parcalar[i + 1]
        alint = [norm(b) for b in re.findall(r'((?:^>.*\n?)+)', govde, flags=re.M)]
        if not alint:  # Z8 düz yazı
            alint = [norm(govde.split('**Z8 – Bağımsız kod incelemesi.**')[-1])]
        tirnaksiz = lambda s: re.sub(r'["“”]', '', s).strip()  # noqa: E731
        sonuc[ad] = [dict(uzunluk=len(a), birebir=(a in onk_n), tirnaksiz_birebir=(tirnaksiz(a) in tirnaksiz(onk_n)))
                     for a in alint]
    # Z8 düz cümlesi ayrıca
    z8 = ('TR-7b koşu kodu (K5 ile K1b) dondurulmadan önce bağımsız kod incelemesi gerekir. Gerekçe: K5 bu kodda ilk kez '
          'yapay ortam dışında çalışacak; Q referansı ve ρ gerçek maske parçalarıyla hesaplanacak.')
    sonuc['Z8_duz'] = [dict(uzunluk=len(z8), birebir=z8 in onk_n)]
    return sonuc


# ---------------------------------------------------------------- 2. dal ızgarası
def dal_izgarasi():
    """Bütün tamsayı ızgarası: n_P 0..10, X_P ≤ n_P, n_N 0..30, X_N ≤ n_N, N_PK 0..120, f ≤ N_PK,
    M_olc (modülasyonu ölçülebilen algılama veren P olayı) ≤ X_P, M_mod ≤ M_olc, MDA tanımlı ∈ {0,1},
    A90_PK ≤ 100 µm/s ∈ {0,1}. Çokluklar kombinatorik olarak sayılır (her tamsayı noktası bir kez)."""
    # (n_P, X_P) için (i, ii) bileşimlerinin (N_PK, f) çokluğu
    ii_say = {}
    for nP in range(0, 11):
        for NPK in range(0, 121):
            for f in range(0, NPK + 1):
                ii = NPK >= 5 and f / NPK <= 0.30
                xm = xmin(nP, f, NPK, cp=cp_ust_scipy) if nP >= 2 else None
                for XP in range(0, nP + 1):
                    i = xm is not None and XP >= max(math.ceil(nP / 2), xm)
                    k = (nP, XP, i, ii)
                    ii_say[k] = ii_say.get(k, 0) + 1

    def m_say(XP):
        ff = sum(Mo + 1 for Mo in range(0, min(2, XP) + 1))
        tf = sum(3 for Mo in range(3, XP + 1))
        tt = sum(Mo - 2 for Mo in range(3, XP + 1))
        return {(False, False): ff, (True, False): tf, (True, True): tt}

    sira = {k: 0 for k in 'abcde'}
    cakisma = {}
    bos = 0
    toplam = 0
    e2_d = 0
    e2_a = 0
    ornek_e2_d = None
    sh_ihlal = 0
    for nP in range(0, 11):
        for XP in range(0, nP + 1):
            MS = m_say(XP)
            for nN in range(0, 31):
                for XN in range(0, nN + 1):
                    iii = (nP > 0 and nN >= 0) and fisher_ok(XP, nP, XN, nN)
                    if iii and nP > 0 and nN > 0 and not (XP / nP > XN / nN):
                        sh_ihlal += 1
                    a = nP < 8 or nN < 20
                    for i in (False, True):
                        for ii in (False, True):
                            c_if = ii_say.get((nP, XP, i, ii), 0)
                            if not c_if:
                                continue
                            for (molc3, iv), c_m in MS.items():
                                if not c_m:
                                    continue
                                for mda in (False, True):
                                    for a90 in (False, True):
                                        w = c_if * c_m
                                        toplam += w
                                        b = i and ii and iii and iv
                                        c = i and ii and molc3 and ((not iii) or (not iv))
                                        d = ((not i) or (not ii)) and mda and a90
                                        e1 = not (a or b or c or d)
                                        e2 = not molc3  # (e)'nin ikinci cümlesi, harfiyen
                                        hangi = [x for x, v in zip('abcde', (a, b, c, d, e1)) if v]
                                        if not hangi:
                                            bos += w
                                        sira[hangi[0]] += w
                                        anahtar = '+'.join(x for x in 'abcd' if x in hangi)
                                        if len([x for x in hangi if x != 'e']) > 1:
                                            cakisma[anahtar] = cakisma.get(anahtar, 0) + w
                                        # (e) ikinci cümlesi ile sıralı dalın çelişmesi
                                        if e2 and hangi[0] == 'd':
                                            e2_d += w
                                            if ornek_e2_d is None and nP >= 8 and nN >= 20:
                                                ornek_e2_d = dict(n_P=nP, X_P=XP, n_N=nN, X_N=XN, i=i, ii=ii,
                                                                  M_olc_ge3=molc3, MDA=mda, A90_ok=a90)
                                        if e2 and hangi[0] == 'a':
                                            e2_a += w
    # (b) iken n_P ≥ 8 gerekmiyor mu? (b) sırayla ancak (a) değilse işler — kontrol: (b) harfiyen ama (a) da doğru
    return dict(toplam_nokta=toplam, sirali_dal_sayisi=sira, hicbir_dala_dusmeyen=bos,
                sirasiz_coklu_dal_abcd=cakisma,
                e_ikinci_cumle_ile_d_celiskisi=e2_d, e_ikinci_cumle_ile_a_celiskisi=e2_a,
                ornek_e2_d=ornek_e2_d,
                fisher_gecip_oran_esitsizligi_saglamayan=sh_ihlal)


# ---------------------------------------------------------------- 3. yeniden üretim
def yeniden_uretim(gecici):
    spec = importlib.util.spec_from_file_location('tr7c_guc_kopya', GUC_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    hedef = os.path.join(gecici, 'tr7c_guc_yeniden.json')
    mod.CIKTI = hedef
    import contextlib, io
    with contextlib.redirect_stdout(io.StringIO()):
        mod.main()
    a, b = sha(hedef), sha(GUC_JSON)
    return dict(py_sha256=sha(GUC_PY), depo_json_sha256=b, yeniden_json_sha256=a, ayni=(a == b))


# ---------------------------------------------------------------- 4. bağımsız doğrulama
def bagimsiz(d_guc):
    out = {}
    # 4a. Clopper–Pearson ve X_min: ikiye bölme ile scipy beta.ppf karşılaştırması ve INCELEME-0 tablosu
    cp_fark = max(abs(cp_ust_bisection(f, N) - cp_ust_scipy(f, N)) for N in (5, 10, 60, 120) for f in range(0, N + 1))
    out['cp_ust_en_buyuk_fark'] = cp_fark
    out['xmin_tablo_kendi'] = {str(f): xmin(10, f, N_PK, cp=cp_ust_bisection) for f in (0, 6, 12, 18, 24, 30, 36, 40)}
    out['xmin_tablo_guc_json'] = d_guc['xmin_tablo']
    # 4b. Fisher: kendi lgamma hipergeometrik vs scipy fisher_exact (alternative='greater')
    fmax = 0.0
    for n in range(1, 11):
        for m in (2, 20, 29, 30):
            for xp in range(n + 1):
                for xn in range(m + 1):
                    p1 = hyper_ust(xp, n, xn, m)
                    p2 = fisher_exact([[xp, n - xp], [xn, m - xn]], alternative='greater')[1]
                    fmax = max(fmax, abs(p1 - p2))
    out['fisher_en_buyuk_fark_scipy'] = fmax
    out['fisher_ornek_kendi'] = {'9/10 vs 0/2': hyper_ust(9, 10, 0, 2), '7/10 vs 9/30': hyper_ust(7, 10, 9, 30),
                                 '6/10 vs 6/30': hyper_ust(6, 10, 6, 30)}
    # 4c. D30M3 hücreleri (kendi uygulamam) ve ön kayıttaki değerler
    hucre = {}
    onk = {('mt0.8', 0.7, 0.1): 0.95, ('mt0.5', 0.7, 0.1): 0.73, ('mt0.8', 0.5, 0.2): 0.51, ('mt0.5', 0.9, 0.3): 0.49,
           ('mt0.8', 0.3, 0.05): 0.19, ('mt0.5', 0.5, 0.05): 0.42}
    for (mt, s, q), yazili in onk.items():
        m_t = float(mt[2:])
        pm, pn = sabit_model(s, q, m_t)
        v = p_d30m3(pm, pn, [q] * 30, r=q)
        hucre[f'{mt}_s{s}_q{q}'] = dict(kendi=round(v, 4), guc_json=d_guc[f'D30M3_izgara_{mt}'][f's{s}_q{q}'],
                                        onkayit=yazili)
    out['D30M3_hucreler'] = hucre
    # Monte Carlo (tamamen ayrı yol)
    mc, se = monte_carlo(0.7, 0.1, 0.8, reps=100000)
    out['MC_s0.7_q0.1_mt0.8'] = dict(p=round(mc, 4), se=round(se, 4), onkayit=0.95)
    # 4d. Genliğe bağlı sızıntı, m_f 0,05 / 0,10 (ön kayıt §7.2)
    d = json.load(open(SAYIM))
    olay = d['olaylar']
    P10 = ['Peru 2001', 'Denali 2002', 'Colima 2003', 'Tokachi-oki 2003', 'Sumatra 2004', 'Kuril 2006', 'Kuril 2007',
           'Wenchuan 2008', 'Samoa 2009', 'Maule 2010']
    vP = [o['pgv_t_cms'] for o in olay if o['ad'] in P10]
    vN = [o['pgv_t_cms'] for o in olay if o['Q_CC'] == 0]
    siz = {}
    for v0 in (0.01, 0.03, 0.1):
        qf = lambda v: 1 / (1 + (v0 / v) ** 2)  # noqa: E731
        for mf in (0.05, 0.10):
            pm = [qf(v) * mf for v in vP]
            pn = [qf(v) * (1 - mf) for v in vP]
            siz[f'v0_{v0}_mf{mf}'] = round(p_d30m3(pm, pn, [qf(v) for v in vN], r=0.05), 4)
    out['sizinti_kendi'] = siz
    out['sizinti_onkayit'] = {'mf0.05': [0.010, 0.006, 0.001], 'mf0.10': [0.062, 0.040, 0.004]}
    # 4e. Ayırt etmeyen algılayıcı, D30M3 (mutlak 3), t 0,3–0,9, m_f 0,05; ön kayıt "≤ 0,0002"
    ayirt = {}
    for t in (0.3, 0.5, 0.7, 0.9):
        pm, pn = sabit_model(0.0, t, 0.8, 0.05)
        ayirt[f't{t}'] = p_d30m3(pm, pn, [t] * 30, r=0.05)
    out['ayirt_etmeyen_D30M3_kendi'] = ayirt
    out['not_ayirt'] = ('tr7c_guc.json bu değeri D30M3 (mutlak 3) için yalnız t = 0,7 ile verir (D30M3_olay_sayisi); '
                        't 0,3/0,5/0,9 D30M (⌈X_P/2⌉) içindir. Kendi hesabım D30M3 için dört t değerini verir.')
    return out, vP, vN, olay


# ---------------------------------------------------------------- 5. N 27 / N 28
def cift(olay, vN):
    from datetime import datetime, timezone
    def t(o):
        return datetime.strptime(o['t0'][:19], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc).timestamp()
    ev = sorted(olay, key=t)
    pen = []
    for o in ev:
        T0, D = t(o), o['delta_km']
        pen.append(dict(ad=o['ad'], Q=o['Q_CC'], T0=T0, R=(T0 - 3600, T0), W=(T0 + D / 5.0, T0 + D / 2.8 + 600),
                        K1b=(T0 + D / 4.6, T0 + D / 3.0), D=D))
    ortusme = []
    for a in range(len(pen)):
        for b in range(a + 1, len(pen)):
            A, B = pen[a], pen[b]
            sA = (A['R'][0] - 3 * 3600, A['W'][1])
            if B['T0'] <= sA[1] and B['T0'] >= sA[0] - 3600:
                ortusme.append(dict(ilk=A['ad'], ikinci=B['ad'], ara_dk=round((B['T0'] - A['T0']) / 60, 1)))
            if A['W'][1] > B['R'][0]:
                ortusme.append(dict(ilk=A['ad'], ikinci=B['ad'], not_='A W sonu > B R başı',
                                    W_W_ortusme_sn=max(0, min(A['W'][1], B['W'][1]) - max(A['W'][0], B['W'][0]))))
    # Çift ayrıntısı
    c27 = next(p for p in pen if p['ad'].startswith('2009 M7.70 (-13.0'))
    c28 = next(p for p in pen if p['ad'].startswith('2009 M7.80 (-12.5'))
    # Kaba P/S yürüme süreleri (iasp91 ezberden, yüzey kaynağı; doğrulanamadı): 80° → P 726 s, S 1326 s;
    # 90° → P 776 s, S 1430 s; doğrusal ara değerleme.
    def ps(D):
        g = D / 111.195
        w = (g - 80) / 10
        return 726 + w * 50, 1326 + w * 104
    p28, s28 = ps(c28['D'])
    p27, s27 = ps(c27['D'])
    def hm(x):
        return datetime.fromtimestamp(x, timezone.utc).strftime('%H:%M:%S')
    ayr = dict(
        N27=dict(T0=hm(c27['T0']), W=[hm(c27['W'][0]), hm(c27['W'][1])], K1b=[hm(c27['K1b'][0]), hm(c27['K1b'][1])],
                 P_kaba=hm(c27['T0'] + p27), S_kaba=hm(c27['T0'] + s27)),
        N28=dict(T0=hm(c28['T0']), W=[hm(c28['W'][0]), hm(c28['W'][1])], K1b=[hm(c28['K1b'][0]), hm(c28['K1b'][1])],
                 P_kaba=hm(c28['T0'] + p28), S_kaba=hm(c28['T0'] + s28),
                 Q_kaba=[hm(c28['T0'] + p28), hm(c28['W'][0])]),
        W_ortusme_sn=round(min(c27['W'][1], c28['W'][1]) - max(c27['W'][0], c28['W'][0])),
        K1b_ortusme_sn=round(max(0, min(c27['K1b'][1], c28['K1b'][1]) - max(c27['K1b'][0], c28['K1b'][0]))),
        N27_W_icinde_N28_Q_sn=round(max(0, min(c27['W'][1], c28['W'][0]) - max(c27['W'][0], c28['T0'] + p28))),
        N27_T0_N28_R_icinde=bool(c28['R'][0] <= c27['T0'] < c28['R'][1]),
        pgv_esit=True,
        not_='P/S kaba (ezber iasp91 tablosundan ara değerleme); doğrulanamadı.')
    # Fisher eşikleri: her X_P için izin verilen en büyük X_N, n_N 30 / 29
    esik = {}
    for xp in range(5, 11):
        e30 = max([xn for xn in range(31) if fisher_ok(xp, 10, xn, 30)], default=None)
        e29 = max([xn for xn in range(30) if fisher_ok(xp, 10, xn, 29)], default=None)
        esik[str(xp)] = dict(nN30_en_cok_XN=e30, nN29_en_cok_XN=e29)
    # Güç / yanlış kabul: (A) 30 bağımsız (model), (B) çift tam bağımlı ama iki kez sayılır, (C) çift tek olay (29)
    i27 = next(k for k, o in enumerate([o for o in olay if o['Q_CC'] == 0]) if o['ad'].startswith('2009 M7.70 (-13.0'))
    i28 = next(k for k, o in enumerate([o for o in olay if o['Q_CC'] == 0]) if o['ad'].startswith('2009 M7.80 (-12.5'))
    etk = {}
    for etiket, (s, q, mt, mf) in {'guc_s0.7_q0.1_mt0.8': (0.7, 0.1, 0.8, 0.05),
                                   'guc_s0.7_q0.1_mt0.5': (0.7, 0.1, 0.5, 0.05),
                                   'guc_s0.5_q0.2_mt0.8': (0.5, 0.2, 0.8, 0.05)}.items():
        pm, pn = sabit_model(s, q, mt, mf)
        qN = [q] * 30
        etk[etiket] = dict(A_bagimsiz30=round(p_d30m3(pm, pn, qN, r=q), 4),
                           B_cift_iki_kez=round(p_d30m3(pm, pn, qN, r=q, ciftli_N=(i27, i28)), 4),
                           C_tek_olay29=round(p_d30m3(pm, pn, [q] * 29, r=q), 4))
    for v0 in (0.01, 0.03):
        qf = lambda v: 1 / (1 + (v0 / v) ** 2)  # noqa: E731
        P10v = VP
        for mf in (0.10, 0.5):
            pm = [qf(v) * mf for v in P10v]
            pn = [qf(v) * (1 - mf) for v in P10v]
            qN = [qf(v) for v in vN]
            qN29 = [q_ for k, q_ in enumerate(qN) if k != i28]
            etk[f'yanlis_kabul_v0_{v0}_mf{mf}'] = dict(
                A_bagimsiz30=round(p_d30m3(pm, pn, qN, r=0.05), 4),
                B_cift_iki_kez=round(p_d30m3(pm, pn, qN, r=0.05, ciftli_N=(i27, i28)), 4),
                C_tek_olay29=round(p_d30m3(pm, pn, qN29, r=0.05), 4))
    return dict(ortusen_ciftler=ortusme, ayrinti=ayr, fisher_esik=esik, etki=etk)


# ---------------------------------------------------------------- 6. kilitli sızıntı
def kilitli(vP, vN, olay):
    negs = [o for o in olay if o['Q_CC'] == 0]
    yuksek = [k for k, o in enumerate(negs) if o['pgv_t_cms'] >= 0.02]
    out = dict(yuksek_N=[negs[k]['ad'] for k in yuksek])
    # Kural G2: 4 yüksek genlikli N olayından ≥ 2'sinde modülasyonlu (p ≤ 0,01) algılama → etiket.
    # Bunun için N tarafında modülasyon da izlenmeli: N olayı j: modülasyonlu algılama q_j·m_f(j).
    def p_gec_ve_G(pm, pn, qN, mN, G_esik, r=0.05):
        """'sınandı' ∧ (yüksek N'de modülasyonlu algılama sayısı < G_esik) olasılığı ve 'sınandı' olasılığı."""
        # N: diğer 26 için yalnız algılama; 4 yüksek için (alg, mod) — bağımsız
        diger = [q for k, q in enumerate(qN) if k not in yuksek]
        Dd = pbinom_dist(diger)
        Dy = {(0, 0): 1.0}
        for k in yuksek:
            a = qN[k] * mN[k]
            b = qN[k] * (1 - mN[k])
            Y = {}
            for (x, mm), w in Dy.items():
                for (dx, dm), w2 in (((1, 1), a), ((1, 0), b), ((0, 0), 1 - a - b)):
                    kk = (x + dx, mm + dm)
                    Y[kk] = Y.get(kk, 0.0) + w * w2
            Dy = Y
        # xn dağılımı ve (xn, gmod) ortak dağılımı
        ort = {}
        for xd in range(len(Dd)):
            for (xy, gm), w in Dy.items():
                kk = (xd + xy, gm)
                ort[kk] = ort.get(kk, 0.0) + Dd[xd] * w
        # P tarafı
        D = {(0, 0): 1.0}
        for a, b in zip(pm, pn):
            Y = {}
            for (x, mm), w in D.items():
                for (dx, dm), w2 in (((1, 1), a), ((1, 0), b), ((0, 0), 1 - a - b)):
                    kk = (x + dx, mm + dm)
                    Y[kk] = Y.get(kk, 0.0) + w * w2
            D = Y
        PF = pbinom_dist([r] * N_PK)
        top = 0.0
        topG = 0.0
        for f in range(N_PK + 1):
            if PF[f] < 1e-13 or f / N_PK > 0.30:
                continue
            xm = xmin(10, f, N_PK, cp=cp_ust_scipy)
            if xm is None:
                continue
            for (xp, mm), w in D.items():
                if xp < max(5, xm) or mm < 3:
                    continue
                for (xn, gm), wn in ort.items():
                    if fisher_ok(xp, 10, xn, 30):
                        top += PF[f] * w * wn
                        if gm < G_esik:
                            topG += PF[f] * w * wn
        return top, topG

    tab = {}
    for v0 in (0.01, 0.03, 0.1):
        qf = lambda v: 1 / (1 + (v0 / v) ** 2)  # noqa: E731
        for mf in (0.05, 0.10, 0.3, 0.5, 0.8, 1.0):
            pm = [qf(v) * mf for v in vP]
            pn = [qf(v) * (1 - mf) for v in vP]
            qN = [qf(v) for v in vN]
            mN = [mf] * 30
            p, pG2 = p_gec_ve_G(pm, pn, qN, mN, 2)
            _, pG1 = p_gec_ve_G(pm, pn, qN, mN, 1)
            tab[f'v0_{v0}_mf{mf}'] = dict(D30M3=round(p, 4), D30M3_ve_G2_yok=round(pG2, 4),
                                          D30M3_ve_G1_yok=round(pG1, 4))
    out['yanlis_kabul_s0'] = tab
    # Bedel: gerçek tremor modeli (s, q sabit, m_t, m_f 0,05) ve kirli negatif (yüksek 4 N'de π payında gerçek tremor)
    bedel = {}
    for (s, q, mt) in ((0.7, 0.1, 0.8), (0.7, 0.1, 0.5), (0.5, 0.1, 0.8)):
        pm, pn = sabit_model(s, q, mt, 0.05)
        for pi in (0.0, 0.4):
            qN = [q] * 30
            mN = [0.05] * 30
            for k in yuksek:  # kirli: π olasılıkla gerçek tremor (s ile algılanır, m_t ile modülasyonlu)
                det_t = pi * s
                det = det_t + (1 - det_t) * q
                qN[k] = det
                mN[k] = (det_t * mt + (1 - det_t) * q * 0.05) / det
            p, pG2 = p_gec_ve_G(pm, pn, qN, mN, 2, r=q)
            _, pG1 = p_gec_ve_G(pm, pn, qN, mN, 1, r=q)
            bedel[f's{s}_q{q}_mt{mt}_pi{pi}'] = dict(D30M3=round(p, 4), G2_etiketi_olasiligi=round(p - pG2, 4),
                                                     G1_etiketi_olasiligi=round(p - pG1, 4))
    out['gercek_tremorda_etiket_bedeli'] = bedel
    return out


# ---------------------------------------------------------------- 7. Marmara: (b) ama etiket yok
def marmara():
    out = {}
    for (s, q, mt) in ((0.7, 0.1, 0.8), (0.7, 0.1, 0.5), (0.9, 0.1, 0.5), (0.5, 0.1, 0.8)):
        pm, pn = sabit_model(s, q, mt, 0.05)
        b = p_d30m3(pm, pn, [q] * 30, r=q, cp=cp_ust_scipy)
        b_ve_etiket = p_d30m3(pm, pn, [q] * 30, r=q, cp=cp_ust_scipy,
                              ek_kural=lambda xp, mm, xn: mm >= math.ceil(xp / 2))
        out[f's{s}_q{q}_mt{mt}'] = dict(P_b=round(b, 4), P_b_ve_etiket=round(b_ve_etiket, 4),
                                        P_b_etiketsiz=round(b - b_ve_etiket, 4),
                                        kosullu_etiketsiz=round((b - b_ve_etiket) / b, 3) if b > 0 else None)
    return out


# ---------------------------------------------------------------- 8. eşik / ESIK-DAYANAGI
def esik():
    out = {}
    def guc(s, q, mt, nP=10, nN=30, kref=None):
        pm, pn = sabit_model(s, q, mt, 0.05, nP)
        if kref is not None:  # yalnız kref P olayında modülasyon ölçülebilir; ötekilerde algılama modülasyonsuz sayılır
            pm2, pn2 = [], []
            for k in range(nP):
                if k < kref:
                    pm2.append(pm[k]); pn2.append(pn[k])
                else:
                    pm2.append(0.0); pn2.append(pm[k] + pn[k])
            pm, pn = pm2, pn2
        return p_d30m3(pm, pn, [q] * nN, r=q, cp=cp_ust_scipy)
    def mde(q, mt, nP=10, nN=30):
        for i in range(1, 101):
            if guc(i / 100, q, mt, nP, nN) >= 0.80:
                return i / 100
        return None
    for mt in (0.8, 0.5):
        s0 = mde(0.1, mt)
        out[f'mt{mt}'] = dict(
            s0=s0, guc_s0=round(guc(s0, 0.1, mt), 4),
            guc_s_x05=round(guc(s0 / 2, 0.1, mt), 4), guc_s_x2_kirpik_1=round(guc(min(1.0, 2 * s0), 0.1, mt), 4),
            guc_q_x05_s0=round(guc(s0, 0.05, mt), 4), guc_q_x2_s0=round(guc(s0, 0.2, mt), 4),
            mt_x05_s0=round(guc(s0, 0.1, mt / 2), 4),
            mde_nP8_nN20=mde(0.1, mt, 8, 20), mde_nP8_nN30=mde(0.1, mt, 8, 30))
    # D1: başvuru istasyonlu P olayı sayısı k'ya göre güç (s 0,7, q 0,1)
    # Gerçekleşen n_P, n_N'ye göre görülebilir en küçük s tablosu (q 0,1; 0,01 ızgarada ikiye bölme; güç monoton)
    def mde_ikiye(q, mt, nP, nN):
        lo, hi = 0, 100  # yüzde
        if guc(1.0, q, mt, nP, nN) < 0.80:
            return None
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if guc(mid / 100, q, mt, nP, nN) >= 0.80:
                hi = mid
            else:
                lo = mid
        return hi / 100
    out['MDE_tablosu_q0.1'] = {f'nP{nP}_nN{nN}': dict(mt08=mde_ikiye(0.1, 0.8, nP, nN), mt05=mde_ikiye(0.1, 0.5, nP, nN))
                               for nP in (8, 9, 10) for nN in (20, 22, 24, 26, 28, 29, 30)}
    out['D1_kref_guc_s0.7_q0.1'] ={f'k{k}': dict(mt08=round(guc(0.7, 0.1, 0.8, kref=k), 4),
                                                  mt05=round(guc(0.7, 0.1, 0.5, kref=k), 4))
                                    for k in (3, 4, 5, 6, 7, 8, 10)}
    return out


VP = None


def main():
    global VP
    gecici = sys.argv[1]
    os.makedirs(gecici, exist_ok=True)
    d_guc = json.load(open(GUC_JSON))
    sonuc = dict(not_='TR-7c İNCELEME-1; yalnız yapay/kombinatorik hesap; gerçek dalga formu yok; ağ isteği yok.',
                 girdi_sha256={os.path.relpath(p, KOK): sha(p) for p in (SAYIM, GUC_PY, GUC_JSON, ONK, INC0)})
    sonuc['z_aynen'] = z_aynen()
    sonuc['yeniden_uretim'] = yeniden_uretim(gecici)
    b, vP, vN, olay = bagimsiz(d_guc)
    VP = vP
    sonuc['bagimsiz'] = b
    sonuc['dal_izgarasi'] = dal_izgarasi()
    sonuc['cift_N27_N28'] = cift(olay, vN)
    sonuc['kilitli_sizinti'] = kilitli(vP, vN, olay)
    sonuc['marmara_etiket'] = marmara()
    sonuc['esik'] = esik()
    json.dump(sonuc, open(CIKTI, 'w'), ensure_ascii=False, indent=1, sort_keys=True)
    print(json.dumps(sonuc, ensure_ascii=False, indent=1, sort_keys=True))


if __name__ == '__main__':
    sys.exit(main())
