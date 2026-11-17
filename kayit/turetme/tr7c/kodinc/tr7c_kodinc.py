#!/usr/bin/env python3
"""TR-7c BAĞIMSIZ KOD İNCELEMESİ: incelemecinin kendi sınamaları ve mutasyonları (`tr7c_kosu.py` üzerinde).

YALNIZ YAPAY VERİ. Süreç başında bir denetim kancası (sys.addaudithook) kurulur: her soket çağrısı, `/mnt/project-files`
altındaki her açma girişimi, gerçek çıktı dizinine (`kayit/turetme/tr7c/kosu/`) her yazma ve dizin kurma, her alt süreç
REDDEDİLİR ve sayılır (TR-13b KOD-İNCELEME §G dersi: gerçek kip yolları çağrılmadan ÖNCE kapatılır). Hiçbir FDSN/HTTP
isteği yoktur; hiçbir gerçek dalga formu ya da zarf açılmaz. Kapının açık hâli yalnız `kosu_dondurulmus_mu(onkayit=geçici
kopya)` ile sınanır; açık kapıyla hiçbir gerçek yol çağrılmaz.

Yapay pencere üreteci bu dosyada bağımsız yazıldı (kodlayıcının `tr7c_test_yapay.py` üreteci kullanılmaz): 1 Hz zarflar,
log-normal gürültü, dar bantlı bir başvuru hızının fazına kilitli (ya da kilitsiz) 2–8 Hz tremor.

Kullanım (depo kökünden): python3 -I -B kayit/turetme/tr7c/kodinc/tr7c_kodinc.py <çıktı.json> [--mutasyonsuz]
"""
import functools
import importlib.util
import json
import math
import os
import re
import shutil
import sys
import tempfile
import time

sys.dont_write_bytecode = True
os.environ.setdefault('OMP_NUM_THREADS', '1')
BURA = os.path.dirname(os.path.abspath(__file__))
TR7C = os.path.abspath(os.path.join(BURA, '..'))
DEPO = os.path.abspath(os.path.join(TR7C, '..', '..', '..'))
KOSU_YOL = os.path.join(TR7C, 'tr7c_kosu.py')
ONKAYIT = os.path.join(DEPO, 'kayit', 'onkayit', 'TR-7c_tetiklenmis-tremor_ONKAYIT.md')
YASAK = '/mnt/project-files'
CIKTI_GERCEK = os.path.join(TR7C, 'kosu')
GECICI = '/tmp/claude-0/-home-user/635decb6-3930-5a4d-9c31-b6f30d64fb94/scratchpad/tr7c_kodinc'

# ================================================================ denetim kancası (her şeyden önce)
ENGEL = []
HAFIF = {'acik': False}   # mutasyon koşularında U6 ızgarası küçülür (ana koşuda tam)


def _p(a):
    try:
        return None if isinstance(a, int) else os.path.abspath(os.fsdecode(a))
    except Exception:   # noqa: BLE001
        return None


def _kanca(olay, args):
    if olay.startswith('socket.'):
        ENGEL.append((olay, repr(args)[:120]))
        raise PermissionError(f'KOD İNCELEMESİ: ağ yasak ({olay})')
    if olay in ('subprocess.Popen', 'os.system', 'os.posix_spawn', 'os.exec', 'os.fork'):
        ENGEL.append((olay, repr(args)[:120]))
        raise PermissionError(f'KOD İNCELEMESİ: alt süreç yasak ({olay})')
    if olay == 'open' and args:
        p = _p(args[0])
        if p and (p == YASAK or p.startswith(YASAK + os.sep)):
            ENGEL.append((olay, p))
            raise PermissionError(f'KOD İNCELEMESİ: gerçek veri yolu yasak: {p}')
        if p and (p == CIKTI_GERCEK or p.startswith(CIKTI_GERCEK + os.sep)):
            m = args[1] if len(args) > 1 else 'r'
            if not isinstance(m, str) or any(c in m for c in 'wax+'):
                ENGEL.append((olay, p))
                raise PermissionError(f'KOD İNCELEMESİ: gerçek çıktı dizinine yazma yasak: {p}')
    if olay in ('os.mkdir', 'os.makedirs', 'os.rename', 'os.replace', 'os.remove') and args:
        p = _p(args[0])
        if p and (p.startswith(CIKTI_GERCEK) or p.startswith(YASAK)):
            ENGEL.append((olay, p))
            raise PermissionError(f'KOD İNCELEMESİ: yasak dizin işlemi: {p}')


sys.addaudithook(_kanca)

import numpy as np  # noqa: E402
from scipy.signal import hilbert  # noqa: E402
from scipy.stats import beta as _beta, binom as _binom, fisher_exact, hypergeom, spearmanr  # noqa: E402

sys.path.insert(0, TR7C)
import tr7c_kosu as T0  # noqa: E402
K, Y2, Y = T0.K, T0.Y2, T0.Y


def modul_yukle(metin, ad):
    spec = importlib.util.spec_from_loader(ad, loader=None)
    m = importlib.util.module_from_spec(spec)
    m.__file__ = KOSU_YOL
    sys.modules[ad] = m
    try:
        exec(compile(metin, KOSU_YOL, 'exec'), m.__dict__)
    finally:
        sys.modules.pop(ad, None)
    return m


class Kayit:
    def __init__(self):
        self.s = []

    def sina(self, grup, ad, kosul, ayrinti=None):
        self.s.append(dict(grup=grup, ad=ad, gecti=bool(kosul), ayrinti=ayrinti))
        return bool(kosul)


def hata_mi(fn, tur):
    try:
        fn()
    except tur as e:
        return True, str(e)[:160]
    except BaseException as e:   # noqa: BLE001
        return False, f'beklenmeyen {type(e).__name__}: {str(e)[:160]}'
    return False, 'hata yükselmedi'


# ================================================================ karar metninden bağımsız okuma (tablolar, sabitler)
def metin_oku():
    with open(ONKAYIT, encoding='utf-8') as f:
        return f.read()


def metin_olaylari(m):
    s31 = m[m.index('### 3.1 P'):m.index('### 3.2 N')]
    P = [re.sub(r'\D', '', t) for t in re.findall(r'\| [^|]+ \| (\d{4}-\d\d-\d\d \d\d:\d\d) \|', s31)]
    s32 = m[m.index('### 3.2 N'):m.index('- **Bilgi satırları')]
    N = {}
    for no, t, ad, pgv in re.findall(r'\| (\d+) \| (\d{4}-\d\d-\d\d \d\d:\d\d) \| ([^|]+) \| ([\d,]+) ', s32):
        N[int(no)] = (re.sub(r'\D', '', t), ad.strip(), float(pgv.replace(',', '.')))
    d2 = dict(re.findall(r'`kayit/turetme/(tr7b?/tr7[\w]*\.py)`\s*\n?>?\s*\(([0-9a-f]{64})', m))
    return P, N, d2


# ================================================================ bağımsız başvurular (Z3, Z4, D-7; scipy ile)
@functools.lru_cache(maxsize=None)
def ref_fisher(xp, n, xn, m):
    k = xp + xn
    if n + m == 0:
        return 1.0
    return float(hypergeom.sf(xp - 1, n + m, n, k))


@functools.lru_cache(maxsize=None)
def ref_cp_ust(f, N):
    return 1.0 if f >= N else float(_beta.ppf(0.95, f + 1, N - f))


@functools.lru_cache(maxsize=None)
def ref_xmin(n, f, N):
    if N <= 0:
        return None
    pu = ref_cp_ust(f, N)
    for x in range(2, n + 1):
        if _binom.sf(x - 1, n, pu) <= 0.05 + 1e-12:
            return x
    return None


def ref_dal(nP, nN, XP, XN, f, N, Molc, Mmod, A90):
    """Z4 + D-7 metinden: sıra (a), (b), (c), (d), (e)."""
    if nP < 8 or nN < 20:
        return 'a', None
    xm = ref_xmin(nP, f, N)
    i = xm is not None and XP >= max(math.ceil(nP / 2), xm)
    ii = N >= 5 and f / N <= 0.30
    iii = ref_fisher(XP, nP, XN, nN) <= 0.05
    iv = Mmod >= 3
    if i and ii and iii and iv:
        return 'b', None
    if i and ii and Molc >= 3:
        return 'c', ('(iii) ve (iv)' if not iii and not iv else '(iii)' if not iii else '(iv)')
    a90ok = isinstance(A90, (int, float)) and not isinstance(A90, bool) and A90 <= 1e5
    if (not i or not ii) and a90ok:
        return 'd', None
    if i and ii and Molc < 3:
        return 'e', 'modülasyon ölçülemedi'
    return 'e', 'yöntem'


# ================================================================ bağımsız yapay pencere üreteci
NAX, R_, Q_, W_, K1B_ = 6000, (0, 3600), (3700, 3900), (3900, 5900), (4400, 5000)
TREM = (4500, 4820)


def ref_hiz(rng, n=NAX):
    """Dar bantlı (15–30 sn) Gauss hızı: faz zamanla rastgele ilerler, dairesel kaydırma boş dağılımı ayırır."""
    X = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1.0)
    X[(f < 1 / 30) | (f > 1 / 15)] = 0
    v = np.fft.irfft(X, n)
    return v / v.std()


def faz_cos_W(v):
    return np.cos(np.angle(hilbert(v[W_[0]:W_[1]])))


def pencere_kur(KM, pid, tohum, tremor=None, A=8.0, n_ist=4, trem_ara=TREM, k1b=K1B_):
    """tremor: None, 'kilitli' (başvuru hızının fazına), 'kilitsiz' (başka bir hıza), 'genlik' (fazsız sabit zarf)."""
    rng = np.random.default_rng(tohum)
    v = ref_hiz(rng)
    ist = []
    maske = np.zeros(NAX, bool)
    zarf = np.zeros(NAX)
    araliklar = trem_ara if isinstance(trem_ara, list) else [trem_ara]
    for a, b in (araliklar if tremor is not None else []):
        tt = np.arange(b - a)
        tap = np.minimum(1, np.minimum(tt, b - a - 1 - tt) / 30.0)
        if tremor == 'kilitli':
            mod = 0.4 + np.maximum(0, faz_cos_W(v))[a - W_[0]:b - W_[0]]
        elif tremor == 'kilitsiz':
            mod = 0.4 + np.maximum(0, faz_cos_W(ref_hiz(rng)))[a - W_[0]:b - W_[0]]
        else:
            mod = np.full(b - a, 0.9)
        zarf[a:b] += A * tap * mod
    for i in range(n_ist):
        g = np.exp(rng.normal(0, 0.12, NAX))
        gd = np.exp(rng.normal(0, 0.12, NAX))
        kay = int(rng.integers(-2, 3))
        C = g + np.roll(zarf, kay)
        x = K.istasyon(C, gd, R_, W_, maske, f'YP.S{i}')
        x['la'], x['lo'] = 35.90 + 0.02 * i, -120.45 - 0.01 * i
        ist.append(x)
    return dict(id=pid, durum='tarandi', n_gecen=n_ist, ist=ist, maske=maske, Wb=W_, Q=Q_,
                K1b=k1b, k0=1_000_000_000, _v=v)


class YapayKaynak:
    gercek = False

    def __init__(self, KM, senaryo, ref_yok=(), mda_esik=20.0, n_neg=12, neg_trem=()):
        self.KM, self.sen, self.ref_yok = KM, senaryo, set(ref_yok)
        self._b = KM.birimler_kur()
        self.mda_esik, self.n_neg, self.neg_trem = mda_esik, n_neg, set(neg_trem)
        self._pv = {}
        self.cagri = {'pencere': 0, 'mda': 0, 'lp': 0, 'sira_lp': []}

    def birimler(self):
        return self._b

    def negatifler(self):
        return [dict(id=f'neg{i:03d}', olay='x', sira=i) for i in range(self.n_neg)]

    def pencere(self, desc):
        self.cagri['pencere'] += 1
        i = desc['id']
        if i not in self._pv:
            h = int.from_bytes(i.encode()[-6:].rjust(6, b'0'), 'big') % 10 ** 6
            if i.startswith('neg'):
                pv = pencere_kur(self.KM, i, 7000 + h, 'kilitsiz' if i in self.neg_trem else None, k1b=None)
            else:
                tr, kw = self.sen(desc)
                pv = pencere_kur(self.KM, i, 9000 + h, tr, **kw)
            self._pv[i] = pv
        return self._pv[i]

    def lp_adaylari(self, desc, pv):
        self.cagri['lp'] += 1
        self.cagri['sira_lp'].append(desc['id'])
        if desc['id'] in self.ref_yok:
            return []
        return [dict(ad='YP.REF', la=35.91, lo=-120.46, kanallar=[
            dict(kod='HHZ', konum='', uygun_yanit=True, ortu_ok=True, v=dict(Z=pv['_v'], R=None, T=None))])]

    def mda(self, desc, pv, rng, n_bas):
        self.cagri['mda'] += 1
        out = []
        for _ in range(n_bas):
            e = self.mda_esik * float(rng.uniform(0.9, 1.1))
            out.append(dict(bas=0, alg=[A >= e for A in K.A_BASAMAK]))
        return out

    def b_prime_girdisi(self, desc, pv):
        return [], []


def sen_gercek(KM, P_trem=8, N_yanlis=('200107070938',), genlik_kilitli=()):
    """P'nin ilk P_trem olayında (T0 sırasıyla) kilitli tremor; N_yanlis'te kilitsiz tremor; genlik_kilitli'de kilitli."""
    Pler = [x for x in KM.P_OLAY][:P_trem]

    def f(b):
        if b['sinif'] == 'P' and b['id'] in Pler:
            return 'kilitli', {}
        if b['id'] in genlik_kilitli:
            return 'kilitli', {}
        if b['id'] in N_yanlis:
            return 'kilitsiz', {}
        return None, {}
    return f


def k1c(KM, kaynak, ad, mod_n=200):
    d = os.path.join(GECICI, 'e2e', ad)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    return KM.k1c_kos(kaynak, d, KM.Ayar(mod_n=mod_n), gunluk=lambda *a: None), d


# ================================================================ bağımsız modülasyon başvurusu (K.mod_p ile)
def ref_ayikla(ist, k, maske, Q):
    uy = k['uyeler']
    pk = {u: [(a, b) for kk, a, b in k['parcalar'] if kk == u] for u in uy}
    yar = len(uy) / 2
    d = sum(K.darbe_ist(ist[u]['Cy'], pk[u]) for u in uy) >= yar
    s = sum(bool(Y2.K5(ist[u], pk[u], maske, Q)) for u in uy) >= yar
    t = sum(K.taban_ist(ist[u], pk[u], maske) for u in uy) >= yar
    return not (d or s or t)


def ref_modulasyon(kaynak, birimler, mod_n):
    """§4.1 + D-9: tek üreteç default_rng(20261112 + 3); P ve N T0 sırasıyla; kümeler I′ başı sırasıyla; yalnız
    sağ çıkan ve K1b (kapsayıcı) ile kesişen kümeler; K.mod_p (TR-7 çekirdeği)."""
    rng = np.random.default_rng(20261112 + 3)
    out = {}
    ref_modulasyon.M = {}
    for b in sorted([b for b in birimler if b['sinif'] in ('P', 'N')], key=lambda b: b['t0']):
        pv = kaynak._pv.get(b['id']) or kaynak.pencere(b)
        ks = K.kumeler(pv['ist'], pv['maske'], pv['Wb'])
        c, d = pv['K1b']
        alg = [k for k in ks if ref_ayikla(pv['ist'], k, pv['maske'], pv['Q']) and k['Ip'][0] <= d and k['Ip'][1] - 1 >= c]
        ps = []
        if b['id'] not in kaynak.ref_yok:
            W0, W1 = pv['Wb']
            cfs = [K.faz_cos(pv['_v'][W0:W1].astype(float))]
            for k in sorted(alg, key=lambda k: k['Ip']):
                Ls = np.array([pv['ist'][i]['L'][W0:W1] for i in k['uyeler']])
                m = pv['maske'][W0:W1]
                Lk = np.median(Ls, axis=0)
                gec = np.isfinite(Lk) & ~m
                a, bb = max(k['I'][0], W0) - W0, min(k['I'][1], W1) - W0
                M, p = K.mod_p(np.where(gec, Lk, 0.0), cfs, a, bb, gec, rng, n=mod_n)
                ps.append(p)
                ref_modulasyon.M.setdefault(b['id'], []).append(float(M))
        out[b['id']] = ps
    return out


# ================================================================ BİRİM SINAMALARI
def birim(KM, R):
    g = 'birim'
    m = metin_oku()
    Pm, Nm, d2m = metin_olaylari(m)
    # U1 olay listesi metinle
    R.sina(g, 'U1 P listesi §3.1 tablosuyla aynı (10 olay, T0 sırası)', list(KM.P_OLAY) == Pm, dict(kod=KM.P_OLAY, metin=Pm))
    bs = KM.birimler_kur()
    Nkod = sorted(e for b in bs if b['sinif'] == 'N' for e in b['evids'])
    R.sina(g, 'U1 N olayları §3.2 tablosuyla aynı (30 olay)', Nkod == sorted(v[0] for v in Nm.values()),
           dict(n_kod=len(Nkod), n_metin=len(Nm)))
    g4 = sorted(v[0] for v in Nm.values() if v[2] >= 0.02)
    R.sina(g, 'U1 GENLIK4 = §3.2\'de PGV_T ≥ 0,02 olan N olayları (D-9)', sorted(KM.GENLIK4) == g4, dict(metin=g4))
    R.sina(g, 'U1 Vanuatu = N 27 + N 28 (D-1)', tuple(KM.VANUATU) == (Nm[27][0], Nm[28][0]))
    sayi = {s: sum(1 for b in bs if b['sinif'] == s) for s in 'PNB'}
    R.sina(g, 'U1 birim sayıları 10 P / 29 N / 2 B', sayi == dict(P=10, N=29, B=2), sayi)
    # U2 D-2: sabitler metinle, modüller denetlenen dosyalardan
    d2kod = {os.path.relpath(k, os.path.join(DEPO, 'kayit', 'turetme')): v for k, v in KM.D2_DOSYALAR.items()}
    R.sina(g, 'U2 D-2 dosya/sha listesi karar metnindeki üç satırla aynı', d2kod == d2m, dict(kod=d2kod, metin=d2m))
    R.sina(g, 'U2 içe aktarılan modüller tam olarak D-2 dosyaları', {os.path.realpath(K.__file__), os.path.realpath(
        Y.__file__), os.path.realpath(Y2.__file__)} == {os.path.realpath(p) for p in KM.D2_DOSYALAR})
    # U3 K5 çağrı ağacı (sys.setprofile ile)
    pv = pencere_kur(KM, 'u3', 11, 'kilitli')
    dosyalar = set()

    def prof(frame, olay, arg):
        if olay == 'call':
            dosyalar.add(os.path.realpath(frame.f_code.co_filename))
    ks = K.kumeler(pv['ist'], pv['maske'], pv['Wb'])
    sys.setprofile(prof)
    try:
        for k in ks:
            for u in k['uyeler']:
                Y2.K5(pv['ist'][u], [(a, b) for kk, a, b in k['parcalar'] if kk == u], pv['maske'], pv['Q'])
    finally:
        sys.setprofile(None)
    proje = {d for d in dosyalar if d.startswith(DEPO)}
    R.sina(g, 'U3 K5 çağrı ağacında depo içinden yalnız D-2 dosyaları (tr7b_yapay2, tr7b_yapay; tr7_cekirdek yalnız '
           'sabit KSIG)', proje <= {os.path.realpath(p) for p in KM.D2_DOSYALAR} and bool(ks),
           dict(depo_ici=sorted(os.path.basename(x) for x in proje), kume=len(ks)))
    # U4 Fisher
    kotu = []
    for n in range(0, 11):
        for mm in range(0, 30, 3):
            for xp in range(n + 1):
                for xn in range(mm + 1):
                    a = KM.fisher_tek(xp, n, xn, mm)
                    b = ref_fisher(xp, n, xn, mm)
                    if abs(a - b) > 1e-9:
                        kotu.append((xp, n, xn, mm, a, b))
    fe = fisher_exact([[8, 2], [3, 26]], alternative='greater')[1]
    R.sina(g, 'U4 Fisher üst kuyruğu = scipy hypergeom.sf ve fisher_exact(greater)', not kotu and
           abs(KM.fisher_tek(8, 10, 3, 29) - fe) < 1e-12, dict(kotu=kotu[:5]))
    # U5 X_min (K2'siz, TR-7 §8) scipy beta/binom ile
    kotu = []
    for N in (0, 4, 5, 12, 40, 100, 120):
        for f in range(0, min(N, 40) + 1, 3):
            for n in (8, 9, 10):
                if KM.xmin(n, f, N) != ref_xmin(n, f, N):
                    kotu.append((n, f, N, KM.xmin(n, f, N), ref_xmin(n, f, N)))
    R.sina(g, 'U5 X_min = bağımsız Clopper–Pearson + binom (K2 kapısı yok, KMS-5)', not kotu, dict(kotu=kotu[:5]))
    # U6 dal: rastgele 200 000 nokta + sınır dilimleri
    rng = np.random.default_rng(42)
    A90s = [None, 'belirsiz', '> 100 µm/s', 50.0, 1e5, 1e5 + 1]
    kotu, sayac = [], {}
    pts = []
    for _ in range(12000 if HAFIF['acik'] else 120000):
        nP, nN = int(rng.integers(6, 11)), int(rng.integers(18, 30))
        XP, XN = int(rng.integers(0, nP + 1)), int(rng.integers(0, nN + 1))
        N = int(rng.choice([0, 3, 4, 5, 12, 60, 120]))
        f = int(rng.integers(0, N + 1)) if N else 0
        Mo = int(rng.integers(0, XP + 1))
        Mm = int(rng.integers(0, Mo + 1))
        pts.append((nP, nN, XP, XN, f, N, Mo, Mm, A90s[int(rng.integers(0, 6))]))
    for nP in (7, 8, 10):
        for nN in (19, 20, 29):
            for XP in range(nP + 1):
                for XN in (0, 2, 5, 29 if nN == 29 else nN):
                    for f, N in ((0, 12), (36, 120), (37, 120), (2, 4), (1, 5)):
                        for Mo, Mm in ((0, 0), (2, 2), (3, 2), (3, 3), (5, 4)):
                            if Mo <= XP:
                                pts.append((nP, nN, XP, XN, f, N, Mo, Mm, 1e5))
    for p in pts:
        a = KM.k1c_dal(*p)[:2]
        b = ref_dal(*p)
        sayac[b[0]] = sayac.get(b[0], 0) + 1
        if a != b:
            kotu.append((p, a, b))
    R.sina(g, f'U6 Z4 + D-7 dalı bağımsız başvuruyla ({len(pts)} nokta)', not kotu, dict(kotu=kotu[:5], dal=sayac))
    R.sina(g, 'U6 Marmara yalnız (b)', all(KM.marmara_acilir(d) == (d == 'b') for d in 'abcde'))
    # U7 K1b kapsayıcı uç (O-35): I′ = [a, b), K1b = [c, d]
    c, d = 100, 200
    R.sina(g, 'U7 kesişim sınırları: b = c yok; b = c + 1 var; a = d var; a = d + 1 yok',
           (KM.kesisir((50, 100), (c, d)), KM.kesisir((50, 101), (c, d)), KM.kesisir((200, 300), (c, d)),
            KM.kesisir((201, 300), (c, d))) == (False, True, True, False))
    # U8 toplama: istasyonların ≥ yarısı
    eski = KM.k5_ist
    sonuc = {}
    try:
        for n_ist, bay in ((4, 2), (4, 1), (3, 1), (3, 2)):
            seq = iter([True] * bay + [False] * (n_ist - bay))
            KM.k5_ist = lambda *a, **k: next(seq)
            pv = pencere_kur(KM, 'u8', 5, 'kilitli', n_ist=n_ist)
            kk = K.kumeler(pv['ist'], pv['maske'], pv['Wb'])[0]
            sonuc[(n_ist, bay)] = KM.ayikla_k5(pv['ist'], kk, pv['maske'], pv['Q'])['sizinti']
    finally:
        KM.k5_ist = eski
    R.sina(g, 'U8 K5 toplaması "istasyonların ≥ yarısı" (4/2 atılır, 4/1 atılmaz, 3/1 atılmaz, 3/2 atılır)',
           sonuc == {(4, 2): True, (4, 1): False, (3, 1): False, (3, 2): True}, {str(k): v for k, v in sonuc.items()})
    # U8b K5'e pencerenin Q'su (§4.2, "Q-doğrusu") olduğu gibi gider
    eskiY = KM.Y2.K5
    qler = []
    try:
        KM.Y2.K5 = lambda x, p, m, Q: (qler.append(tuple(Q)), eskiY(x, p, m, Q))[1]
        pv = pencere_kur(KM, 'u8b', 6, 'kilitli')
        kk = K.kumeler(pv['ist'], pv['maske'], pv['Wb'])[0]
        KM.ayikla_k5(pv['ist'], kk, pv['maske'], pv['Q'])
    finally:
        KM.Y2.K5 = eskiY
    R.sina(g, "U8b K5 her istasyonda pencerenin Q aralığıyla çağrılır", bool(qler) and
           all(q == tuple(pv['Q']) for q in qler), dict(Q=list(pv['Q']), gelen=qler[:4]))
    # U9 E-1
    v = dict(Z=np.zeros(10), R=np.zeros(10), T=np.zeros(10))

    def kan(kod, konum='', ok=True, ortu=True, vv=v):
        return dict(kod=kod, konum=konum, uygun_yanit=ok, ortu_ok=ortu, v=vv)
    yakin, uzak = (35.913, -120.463), (36.2, -120.8)
    c1 = KM.e1_secim([dict(ad='A.UZAK', la=uzak[0], lo=uzak[1], kanallar=[kan('HHZ')]),
                      dict(ad='B.YAKIN', la=yakin[0], lo=yakin[1], kanallar=[kan('BHZ', '00')])])
    c2 = KM.e1_secim([dict(ad='B.YAKIN', la=yakin[0], lo=yakin[1], kanallar=[kan('BHZ', '00'), kan('HHZ', '10')])])
    c3 = KM.e1_secim([dict(ad='B.YAKIN', la=yakin[0], lo=yakin[1], kanallar=[kan('HNZ'), kan('EHZ'), kan('BLZ')])])
    c4 = KM.e1_secim([dict(ad='B.YAKIN', la=yakin[0], lo=yakin[1], kanallar=[kan('HHZ', ortu=False), kan('BHZ')])])
    c5 = KM.e1_secim([dict(ad='B.YAKIN', la=yakin[0], lo=yakin[1],
                           kanallar=[kan('HHZ', vv=dict(Z=np.zeros(10), R=np.zeros(10), T=None))])])
    c6 = KM.e1_secim([dict(ad='Z.IKI', la=yakin[0], lo=yakin[1], kanallar=[kan('BHZ')]),
                      dict(ad='A.BIR', la=yakin[0], lo=yakin[1], kanallar=[kan('BHZ')])])
    R.sina(g, 'U9 E-1: en yakın istasyon (BH bile olsa) uzaktaki HH\'den önce', c1 and c1['ad'] == 'B.YAKIN')
    R.sina(g, 'U9 E-1: aynı istasyonda HH, konum sırasından bağımsız BH\'den önce', c2 and c2['kanal'] == 'HHZ')
    R.sina(g, 'U9 E-1: HN/EH/BL kanalları uygun değil', c3 is None)
    R.sina(g, 'U9 E-1: HH örtüsü kalırsa BH', c4 and c4['kanal'] == 'BHZ')
    R.sina(g, 'U9 E-1: yataylardan biri yoksa yalnız Z', c5 and c5['bilesen'] == 1)
    R.sina(g, 'U9 E-1: eşit uzaklıkta ad sırası (belirlenimci)', c6 and c6['ad'] == 'A.BIR')
    # U10 modulasyon_kume = K.mod_p (aynı üreteç, aynı çekiliş sırası)
    pv = pencere_kur(KM, 'u10', 21, 'kilitli')
    kk = K.kumeler(pv['ist'], pv['maske'], pv['Wb'])[0]
    ref = dict(v=[pv['_v']], W=pv['Wb'])
    r1 = KM.modulasyon_kume(pv, kk, ref, np.random.default_rng(5), 300)
    W0, W1 = pv['Wb']
    Lk = np.median(np.array([pv['ist'][i]['L'][W0:W1] for i in kk['uyeler']]), axis=0)
    gec = np.isfinite(Lk)
    M2, p2 = K.mod_p(np.where(gec, Lk, 0.0), [K.faz_cos(pv['_v'][W0:W1])], max(kk['I'][0], W0) - W0,
                     min(kk['I'][1], W1) - W0, gec, np.random.default_rng(5), n=300)
    R.sina(g, 'U10 modulasyon_kume (p, M) = TR-7 çekirdeği K.mod_p (aynı tohum)', r1 and r1['p'] == p2 and
           r1['M'] == round(M2, 4), dict(kod=r1, ref=(M2, p2)))
    # U11 _rho eşitlik okuması (Ö-i): sürekli L'de Spearman ile aynı; nicemlenmiş L'de fark ölçülür
    rng = np.random.default_rng(3)
    fark_s, fark_q = [], []
    for _ in range(300):
        L = rng.normal(0, 1, 200).cumsum() * 0.01 + 1
        sec = np.zeros(200, bool)
        sec[rng.integers(0, 50):rng.integers(100, 200)] = True
        x = dict(L=L)
        r = Y2._rho(x, sec)
        if r is not None:
            fark_s.append(abs(r - spearmanr(L[sec], np.flatnonzero(sec))[0]))
        Lq = np.round(L, 2)
        rq = Y2._rho(dict(L=Lq), sec)
        if rq is not None:
            fark_q.append(abs(rq - spearmanr(Lq[sec], np.flatnonzero(sec))[0]))
    R.sina(g, 'U11 _rho = Spearman (sürekli L); eşitlikte sıra okuması (bilgi: nicemlenmiş L\'de en büyük fark)',
           max(fark_s) < 1e-9, dict(surekli_max=float(max(fark_s)), nicem_0_01_max=float(max(fark_q)),
                                   nicem_0_01_medyan=float(np.median(fark_q))))
    # U12 Q ekseni: 41 birimde Q başı > 0 (K5'in q[Q0:Q1] dilimi sarmaz) ve Q boş değil (derinlik 0–700 km)
    from obspy.geodetics import locations2degrees
    D = KM.dunya_kur(bs)
    ol = KM.olaylar()
    kotu, qmin, qlen = [], 10 ** 9, 10 ** 9
    for b in bs:
        p = D['pen']['pk|' + b['id']]
        xs = list(p['ist'].values())
        k0 = int(math.floor(K.epoch(min(x['R'][0] for x in xs)) - K.DOLGU_S))
        Wb0 = min(int(round(K.epoch(x['W'][0]))) - k0 for x in xs)
        e = ol[b['evids'][0]]
        dg = locations2degrees(e['la'], e['lo'], *KM.IZ_ORTA)
        for dep in (0.0, 33.0, 300.0, 700.0):
            q0 = int(math.floor(K.epoch(e['t0']) + K.taup_varislar(dep, dg)[0])) - k0
            qmin, qlen = min(qmin, q0), min(qlen, Wb0 - q0)
            if q0 <= 0 or Wb0 - q0 < 30:
                kotu.append((b['id'], dep, q0, Wb0))
    R.sina(g, 'U12 Q = [⌊T0 + t_P⌋, Wb başı) gerçek geometride pozitif ve ≥ 30 sn (Ö-i ikinci not)', not kotu,
           dict(en_kucuk_Q0=qmin, en_kisa_Q=qlen, kotu=kotu[:5]))
    # U13 Vanuatu birimi (D-1) ve USTVERI kayıtları (K-1)
    ust = {u['ad']: u for u in json.load(open(os.path.join(TR7C, 'ustveri', 'tr7c_ustveri.json')))['birimler']}
    vb = next(b for b in bs if b['id'] == KM.VANUATU_BIRIM)
    e1 = [e for e in D['e1'] if e['tetikleyici'] == KM.VANUATU[0]]
    n28 = [(e['faz'], e['varis']) for e in e1 if float(e['M']) >= 7.0]
    R.sina(g, 'U13 Vanuatu: K1b ve açık pay USTVERI birleşik biriminden; N 28 P ve S (M 7,8) E1\'de',
           vb['K1b_acik_pay'] == ust['VANUATU2009']['K1b_acik_pay'] and vb['K1b'] == (
               K.epoch(ust['VANUATU2009']['K1b'][0]), K.epoch(ust['VANUATU2009']['K1b'][1]))
           and ('P', '2009-10-07T22:31:18') in n28 and ('S', '2009-10-07T22:40:04') in n28,
           dict(pay=vb['K1b_acik_pay'], e1=len(e1), n28=n28))
    R.sina(g, 'U13 Vanuatu biriminin T0\'ı ve tetikleyicisi N 27 (D-1: R ve Q N 27\'nin)',
           vb['t0'] == ol[KM.VANUATU[0]]['t0'] and D['pen']['pk|' + vb['id']]['tetikleyici'] == KM.VANUATU[0])
    eksik = [b['id'] for b in bs if b['sinif'] in 'PN' and (b['K1b_acik_pay'] is None or b['maskelenen'] is None)]
    R.sina(g, 'U13 39 P/N biriminin hepsinde dondurulmuş K1b payı ve E1 satırları kullanılıyor', not eksik, eksik)
    # U14 taranan sınırı
    R.sina(g, 'U14 K1b açık payı tam 0,50 taranır, 0,499 taranmaz (Z2 "≥ %50")',
           KM.taranan_mi(dict(K1b_acik_pay=0.5), dict(durum='tarandi')) and
           not KM.taranan_mi(dict(K1b_acik_pay=0.499), dict(durum='tarandi')))
    # U15 E-2 güç tablosu §7.3 ile
    tab = {3: (0.18, 0.04), 4: (0.41, 0.13), 5: (0.61, 0.24), 6: (0.75, 0.35), 7: (0.85, 0.47), 8: (0.90, 0.57),
           10: (0.95, 0.73)}
    kotu = [(k, KM.k_guc(k), v) for k, v in tab.items() if KM.k_guc(k) is None or
            any(abs(a - b) > 0.006 for a, b in zip(KM.k_guc(k), v))]
    R.sina(g, 'U15 k_koşu güç tablosu §7.3 k satırıyla aynı (±0,005)', not kotu, kotu)
    c9 = KM.k1c_cumle('b', '', 10, 29, 8, 1.0, dict(k_kosu=9, mod_gecti=True, b_prime=False))
    c10 = KM.k1c_cumle('b', '', 10, 29, 8, 1.0, dict(k_kosu=10, mod_gecti=True, b_prime=False))
    R.sina(g, 'U15b E-2: güç satırı yalnız k_koşu < 10 iken (9 var, 10 yok); "koşuda 10" yazılır',
           'k_koşu ile güç' in c9 and 'k_koşu ile güç' not in c10 and 'koşuda 10' in c10, dict(c9=c9[-160:], c10=c10[-120:]))
    # U16 D-8 MDE §7.3 tablosuyla
    tab = {(10, 20): (0.60, 0.78), (10, 24): (0.59, 0.77), (10, 29): (0.58, 0.77), (9, 20): (0.64, 0.84),
           (9, 29): (0.63, 0.84), (8, 20): (0.66, 0.93), (8, 29): (0.64, 0.93)}
    kotu = [(k, KM.mde_degeri(*k)) for k, v in tab.items() if KM.mde_degeri(*k) is None or
            any(abs(a - b) > 0.006 for a, b in zip(KM.mde_degeri(*k), v))]
    yok = [(a, b) for a in (8, 9, 10) for b in range(20, 30) if KM.mde_degeri(a, b) is None]
    R.sina(g, 'U16 D-8 MDE §7.3 tablosuyla aynı; n_P 8–10 × n_N 20–29 hepsi dondurulmuş', not kotu and not yok,
           dict(kotu=kotu, yok=yok))
    # U17 sabitler metinle (tohumlar, eşikler)
    R.sina(g, 'U17 tohumlar ve eşikler metindeki gibi', (KM.MOD_TOHUM_PK, KM.NEG_TOHUM, K.MDA_TOHUM, KM.N_P_MIN,
           KM.N_N_MIN, KM.FAR_TAVAN, KM.N_PK_MIN, KM.FISHER_ALFA, KM.MOD_P_MIN, K.MOD_ESIK, KM.A90_TAVAN,
           KM.K_USTVERI, KM.NEG_SAYI, KM.NEG_N_MAX, KM.MDA_BAS_PK, KM.V_K1B) == (
        20261115, 20261117, 20261114, 8, 20, 0.30, 5, 0.05, 3, 0.01, 1e5, 10, 10, 120, 3, (4.6, 3.0)))


# ================================================================ KAPI (B)
def kapi(KM, R):
    g = 'kapı'
    n0 = len(ENGEL)

    class SahteGercek(KM.Kaynak):
        gercek = True

        def birimler(self):
            raise AssertionError('dokunuldu')
        pencere = negatifler = birimler
    girisler = [
        ('main kos manifest', lambda: KM.main(['kos', 'manifest'])),
        ('main kos K1c-algılama', lambda: KM.main(['kos', 'K1c-algılama'])),
        ('main baslat', lambda: KM.main(['baslat', 'manifest'])),
        ('main marmara', lambda: KM.main(['marmara', 'Marmara-indirme'])),
        ('asama_kos', lambda: KM.asama_kos('K1c-indirme')),
        ('asama_manifest', lambda: KM.asama_manifest(None, [])),
        ('asama_indirme', lambda: KM.asama_indirme(None, None, None)),
        ('lp_adaylari_manifest', lambda: KM.lp_adaylari_manifest(None, None)),
        ('lp_indir', lambda: KM.lp_indir(None, None, None)),
        ('marmara_kos', lambda: KM.marmara_kos('Marmara-indirme')),
        ('GercekOrtam()', lambda: KM.GercekOrtam()),
        ('GercekKaynak()', lambda: KM.GercekKaynak(None, None, None, None, None)),
        ('GercekOrtam.zyol (kurucu atlanarak)', lambda: object.__new__(KM.GercekOrtam).zyol('x')),
        ('GercekOrtam.hyol (kurucu atlanarak)', lambda: object.__new__(KM.GercekOrtam).hyol('x')),
        ('GercekOrtam.istemci (kurucu atlanarak)', lambda: object.__new__(KM.GercekOrtam).istemci()),
        ('GercekKaynak.pencere (kurucu atlanarak)', lambda: object.__new__(KM.GercekKaynak).pencere({'id': 'x'})),
        ('GercekKaynak.lp_adaylari (kurucu atlanarak)', lambda: object.__new__(KM.GercekKaynak).lp_adaylari({}, {})),
        ('GercekKaynak.mda (kurucu atlanarak)', lambda: object.__new__(KM.GercekKaynak).mda({}, {}, None, 3)),
        ('GercekKaynak.b_prime (kurucu atlanarak)', lambda: object.__new__(KM.GercekKaynak).b_prime_girdisi({}, {})),
        ('k1c_kos gerçek dizin', lambda: KM.k1c_kos(YapayKaynak(KM, sen_gercek(KM)), KM.CIKTI)),
        ('k1c_kos gercek=True', lambda: KM.k1c_kos(YapayKaynak(KM, sen_gercek(KM)), GECICI + '/k', gercek=True)),
        ('k1c_kos gerçek kaynak', lambda: KM.k1c_kos(SahteGercek(), GECICI + '/k')),
    ]
    sonuc = {}
    for ad, fn in girisler:
        ok, ne = hata_mi(fn, KM.GercekKipReddedildi)
        sonuc[ad] = ok
        R.sina(g, f'B kapalı kapı: {ad} → GERÇEK KİP REDDEDİLDİ', ok, ne)
    R.sina(g, 'B kapı sınamalarında hiçbir soket / /mnt / kosu/ / alt süreç girişimi olmadı', len(ENGEL) == n0,
           ENGEL[n0:])
    # kapi ve durum komutları hiçbir şey açmaz
    import io
    import contextlib
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        KM.main(['kapi'])
        KM.main(['durum'])
    R.sina(g, 'B `kapi` ve `durum` komutları kapalı der, hiçbir yasak girişim yok',
           '"acik": false' in buf.getvalue() and len(ENGEL) == n0)
    # açık kapı yalnız geçici kopyada (gerçek yol ÇAĞRILMAZ)
    m = metin_oku()
    tmp = tempfile.mkdtemp(dir=GECICI)
    y = os.path.join(tmp, 'onkayit.md')

    def yaz(metin):
        with open(y, 'w', encoding='utf-8') as f:
            f.write(metin)
        return y
    shas = ' '.join(KM.kod_sha().values())
    acik = m.replace('Durum: KARAR METNİ DONDURULDU', 'Durum: KOŞU DONDURULDU; KARAR METNİ DONDURULDU', 1) + \
        f'\n\n## Ek: koşu dondurması\n{shas}\n'
    R.sina(g, 'B geçici kopyada (belirteç + kod sha\'ları) kapı açılır', KM.kosu_dondurulmus_mu(yaz(acik))[0])
    kms1 = m + f'\n\n## Ek\n{shas}\n'
    R.sina(g, 'B KMS-1: yalnız "KARAR METNİ DONDURULDU" + sha\'lar kapıyı açmaz', not KM.kosu_dondurulmus_mu(yaz(kms1))[0])
    eski = dict(KM.TR7_MOTOR) if hasattr(KM, 'TR7_MOTOR') else None
    if eski is not None:
        try:
            k = next(iter(KM.TR7_MOTOR))
            KM.TR7_MOTOR[k] = '0' * 64
            R.sina(g, 'B K-2: TR-7 motoru (tr7_kosu.py / tr7_indir.py) değişmişse kapı kapanır',
                   not KM.kosu_dondurulmus_mu(yaz(acik))[0])
        finally:
            KM.TR7_MOTOR.clear()
            KM.TR7_MOTOR.update(eski)
    else:
        R.sina(g, 'B K-2: TR-7 motoru (tr7_kosu.py / tr7_indir.py) değişmişse kapı kapanır', False, 'TR7_MOTOR yok')
    # açık kapıda bile yapay düğmeler gerçek kipte reddedilir (kapı sahte açık; kaynak gerçek değil → hiçbir şey açılmaz)
    eski_f = KM.kosu_dondurulmus_mu
    try:
        KM.kosu_dondurulmus_mu = lambda onkayit=None: (True, 'sahte (sınama)')
        ok1, _ = hata_mi(lambda: KM.k1c_kos(YapayKaynak(KM, sen_gercek(KM)), GECICI + '/k', gercek=True),
                         KM.GercekKipReddedildi)
        ok2, _ = hata_mi(lambda: KM.k1c_kos(SahteGercek(), GECICI + '/k'), KM.GercekKipReddedildi)
        ok3, _ = hata_mi(lambda: KM.k1c_kos(SahteGercek(), KM.CIKTI, KM.Ayar(mod_n=100)), KM.GercekKipReddedildi)
    finally:
        KM.kosu_dondurulmus_mu = eski_f
    R.sina(g, 'B gerçek kipte yapay düğmeler kapalı: yapay kaynak, yapay dizin, mod_n ≠ 1000 reddedilir', ok1 and ok2 and ok3,
           dict(yapay_kaynak=ok1, yapay_dizin=ok2, mod_n=ok3))
    R.sina(g, 'B sahte açık kapı sınamasında da hiçbir yasak girişim yok', len(ENGEL) == n0, ENGEL[n0:])
    shutil.rmtree(tmp, ignore_errors=True)


# ================================================================ UÇTAN UCA (yapay)
def uctan_uca(KM, R, ozet):
    g = 'uçtan uca'
    # E1 gerçek tremor: 8/10 P kilitli; N'de 1 yanlış alarm (kilitsiz); negatif yok
    kay = YapayKaynak(KM, sen_gercek(KM))
    t = time.time()
    h, d = k1c(KM, kay, 'e1')
    ozet['e1_sure_s'] = round(time.time() - t, 1)
    ozet['e1'] = {k: h[k] for k in ('dal', 'n_P', 'n_N', 'X_P', 'X_N', 'f_PK', 'N_PK', 'M_olc', 'M_mod', 'A90_PK')}
    ozet['e1']['cumle'] = h['cumle']
    R.sina(g, 'E1 gerçek tremor → (b), X_P 8/10, X_N 1/29, f_PK 0/12, M_mod 8, VAR verilebilir',
           (h['dal'], h['n_P'], h['n_N'], h['X_P'], h['X_N'], h['f_PK'], h['N_PK'], h['M_mod'], h['var_verilebilir'],
            h['marmara_acilir']) == ('b', 10, 29, 8, 1, 0, 12, 8, True, True), ozet['e1'])
    ref = ref_modulasyon(kay, kay.birimler(), 200)
    kod = {b: [k['p'] for k in v['kumeler']] for b, v in h['modulasyon'].items()}
    R.sina(g, 'E1 modülasyon p\'leri bağımsız başvuruyla birebir (tek üreteç, P+N T0 sırası, I′ sırası)', kod == ref,
           dict(fark=[(b, kod.get(b), ref.get(b)) for b in ref if kod.get(b) != ref.get(b)][:4]))
    R.sina(g, 'E1 E-1 başvurusu birimler T0 sırasıyla istendi (P ve N iç içe)',
           kay.cagri['sira_lp'] == [b['id'] for b in sorted([b for b in kay.birimler() if b['sinif'] in 'PN'],
                                                              key=lambda b: b['t0'])])
    R.sina(g, 'E1 MDA yalnız W\'de algılama vermeyen negatiflerde, pencere başına 3 başlangıç',
           kay.cagri['mda'] == 12 and h['mda_deneme'] == 36, dict(mda=kay.cagri['mda'], deneme=h['mda_deneme']))
    alg = [json.loads(s) for s in open(os.path.join(d, 'tr7c_algilama.jsonl'))]
    R.sina(g, 'E1 algılama jsonl sırası: önce 29 N, sonra 10 P, sonra 2 B',
           [r['sinif'] for r in alg] == ['N'] * 29 + ['P'] * 10 + ['B'] * 2)
    du = json.load(open(os.path.join(d, KM.DURUM_AD)))
    R.sina(g, 'E1 durum dosyasında sayı yok (Ö-b)', not re.search(r'"(X_|f_PK|N_PK|n_)', json.dumps(du)))
    # kilit: ikinci çağrı hiçbir pencere açmaz
    n_once = kay.cagri['pencere']
    h2 = KM.k1c_kos(kay, d, KM.Ayar(mod_n=200), gunluk=lambda *a: None)
    R.sina(g, 'E1 kilit: ikinci çağrı hiçbir pencereye dokunmaz ve aynı hükmü döndürür',
           kay.cagri['pencere'] == n_once and h2['dal'] == h['dal'] and h2['cumle'] == h['cumle'])
    # E2 D-9: Nias'ta kilitli tremor; D-1: Vanuatu'da N 28 kısmında tremor
    van = KM.VANUATU_BIRIM

    def sen2(b):
        if b['id'] == '200503281609':
            return 'kilitli', {}
        if b['id'] == van:
            return 'kilitsiz', dict(trem_ara=(4500, 4820))
        return sen_gercek(KM)(b)
    kay2 = YapayKaynak(KM, sen2, neg_trem=('neg000',))
    h, d = k1c(KM, kay2, 'e2')
    ozet['e2'] = {k: h[k] for k in ('dal', 'n_N', 'X_N', 'f_PK', 'N_PK')}
    ozet['e2']['etiket'] = h['etiket']
    R.sina(g, 'E2 D-9: genliği eşlenmiş N\'de modülasyonlu algılama → (b) + "genlik karıştırıcısı dışlanmadı"; VAR yok',
           h['dal'] == 'b' and h['etiket']['genlik'] and 'genlik karıştırıcısı dışlanmadı' in h['cumle']
           and not h['var_verilebilir'], ozet['e2'])
    R.sina(g, 'E2 D-1: Vanuatu birimi bir kez sayılır (n_N 29; X_N = 1 + Nias + Vanuatu = 3)',
           h['n_N'] == 29 and h['X_N'] == 3, ozet['e2'])
    R.sina(g, 'E2 f_PK = W\'de algılama veren negatif sayısı (1/12); MDA yalnız 11 negatifte',
           h['f_PK'] == 1 and h['N_PK'] == 12 and kay2.cagri['mda'] == 11, dict(f=h['f_PK'], mda=kay2.cagri['mda']))
    # E3 E-2: 5 P'de başvuru yok → k_koşu 5; (e) modülasyon ölçülemedi değil: M_olc 3 → (b)/(c)? burada M_mod 3 → (b)
    yok = list(KM.P_OLAY[:5])
    kay3 = YapayKaynak(KM, sen_gercek(KM), ref_yok=yok)
    h, d = k1c(KM, kay3, 'e3')
    ozet['e3'] = {k: h[k] for k in ('dal', 'alt', 'X_P', 'M_olc', 'M_mod')}
    ozet['e3']['cumle'] = h['cumle']
    R.sina(g, 'E3 E-2: 5 P\'de başvuru yok → k_koşu 5, X_P ve n_P değişmez, M_olc = M_mod = 3 → (b), D-10 "geçmedi"',
           h['etiket']['k_kosu'] == 5 and h['X_P'] == 8 and h['n_P'] == 10 and h['M_olc'] == 3 and h['dal'] == 'b'
           and not h['etiket']['mod_gecti'] and 'Parkfield modülasyonu geçmedi' in h['cumle']
           and 'koşuda 5 (k_koşu ile güç' in h['cumle'], ozet['e3'])
    # E5 bir P olayında iki ayrı tremor kümesi: üreteç kümeleri I′ başı sırasıyla tüketir
    iki = KM.P_OLAY[0]

    def sen5(b):
        if b['id'] == iki:
            return 'kilitli', dict(trem_ara=[(4420, 4620), (4760, 4980)])
        return sen_gercek(KM)(b)
    kay5 = YapayKaynak(KM, sen5)
    h, d = k1c(KM, kay5, 'e5')
    ref = ref_modulasyon(kay5, kay5.birimler(), 200)
    kod = {b: [k['p'] for k in v['kumeler']] for b, v in h['modulasyon'].items()}
    kodM = [float(k['M']) for k in h['modulasyon'][iki]['kumeler']]
    refM = ref_modulasyon.M.get(iki, [])
    # iki kilitli küme p'de eşit (1/(n+1)) çıkabilir: sırayı M ile de denetle (kod M'yi 4 basamağa yuvarlar)
    R.sina(g, 'E5 iki algılama kümeli P olayında (M, p) başvuruyla birebir ve aynı sırada (küme sırası I′ başı)',
           len(ref[iki]) == 2 and kod == ref and len(kodM) == 2 and np.allclose(kodM, refM, rtol=0, atol=6e-5),
           dict(iki=(kod.get(iki), ref.get(iki)), M=(kodM, refM)))
    # E4 başvuru 8 P'de yok → M_olc 0 → (e) modülasyon ölçülemedi (D-7: i, ii var)
    kay4 = YapayKaynak(KM, sen_gercek(KM), ref_yok=list(KM.P_OLAY[:8]))
    h, d = k1c(KM, kay4, 'e4')
    R.sina(g, 'E4 başvurusuz 8 P → (e) "modülasyon ölçülemedi" + D-8 eki', h['dal'] == 'e' and
           h['alt'] == 'modülasyon ölçülemedi' and 'ayırt edilemez' in h['cumle'], dict(dal=h['dal'], alt=h['alt']))


# ================================================================ MUTASYONLAR (kodlayıcının 34'ünden farklı)
MUTASYONLAR = [
    ('modülasyon sırası: önce bütün P, sonra N', "if b['sinif'] in ('P', 'N')], key=lambda b: b['t0']):",
     "if b['sinif'] in ('P', 'N')], key=lambda b: (b['sinif'] != 'P', b['t0'])):"),
    ('modülasyon akışına yalnız P girer', "if b['sinif'] in ('P', 'N')], key=lambda b: b['t0']):",
     "if b['sinif'] in ('P',)], key=lambda b: b['t0']):"),
    ('modülasyon akışına B (bilgi) birimleri de girer', "if b['sinif'] in ('P', 'N')], key=lambda b: b['t0']):",
     "if b['sinif'] in ('P', 'N', 'B')], key=lambda b: b['t0']):"),
    ('küme sırası I′ sonu tersten', "key=lambda k: (k['Ip'][0], k['Ip'][1]))\n        ref = e1_secim",
     "key=lambda k: (-k['Ip'][1], k['Ip'][0]))\n        ref = e1_secim"),
    ('modülasyon kaydırma aralığı [0, W)', 'kk = int(rng.integers(K.MOD_KAY, len(cfs[0]) - K.MOD_KAY))',
     'kk = int(rng.integers(0, len(cfs[0])))'),
    ('modülasyon p = say/n (+1 yok)', 'p=(1 + say_) / (n_kay + 1)', 'p=max(say_, 1e-9) / n_kay'),
    ('Fisher katı kuyruk (X > X_P)', 'for x in range(xp, min(k, n) + 1)) / den', 'for x in range(xp + 1, min(k, n) + 1)) / den'),
    ('Fisher n_P ile n_N yer değiştirir', 'math.comb(n, x) * math.comb(m, k - x)', 'math.comb(m, x) * math.comb(n, k - x)'),
    ('D-1: USTVERI birleşik birim kaydı okunmaz (K-1 öncesi hâl)', 'u = ub.get(bid)', 'u = ub.get(evids[0])'),
    ('D-1: birim T0\'ı N 28\'den', "t0=ol[evids[0]]['t0'], ad=", "t0=ol[evids[-1]]['t0'], ad="),
    ('E-1: konum bant tercihinden önce', "key=lambda c: (0 if c['kod'][0] == 'H' else 1, c.get('konum') or ''))",
     "key=lambda c: (c.get('konum') or '', 0 if c['kod'][0] == 'H' else 1))"),
    ('E-1: alet kodu H şartı yok', "and c['kod'][1] == 'H'\n", "\n"),
    ('E-1: tek yatayla da üç bileşen', "if v.get('R') is not None and v.get('T') is not None else",
     "if v.get('R') is not None or v.get('T') is not None else"),
    ('k_koşu yalnız taranan P\'de sayılır', "k_kosu = sum(1 for b in P if mod.get(b['id'], {}).get('ref') is not None)",
     "k_kosu = sum(1 for b in alg_P if mod.get(b['id'], {}).get('ref') is not None)"),
    ('E-2 güç satırı k = 10\'da da', "and etiket['k_kosu'] < K_USTVERI:", "and etiket['k_kosu'] <= K_USTVERI:"),
    ('kilit iki katmanıyla kalkar', "    if os.path.exists(hy):\n        gunluk('KİLİT", "    if False:\n        gunluk('KİLİT"),
    ('kapı: Durum satırında "DONDURULDU" yeter (KMS-1)', "if 'KOŞU DONDURULDU' not in durum:",
     "if 'DONDURULDU' not in durum:"),
    ('kapı: K-2 motor denetimi yok', '        d2_denetle(TR7_MOTOR)', '        pass'),
    ('kapı: GercekOrtam.zyol kapısız', "        gercek_kapi('zarf deposu')\n", '        pass\n'),
    ('kapı: GercekKaynak.pencere kapısız', "        gercek_kapi('pencere')\n", '        pass\n'),
    ('K5 toplaması "> yarı"', 'sizinti=sum(s) >= yarim', 'sizinti=sum(s) > yarim'),
    ('K5\'e Q yerine boş aralık', 's = [k5_ist(ist[k], pk[k], maske, Q) for k in uy]',
     's = [k5_ist(ist[k], pk[k], maske, (0, 0)) for k in uy]'),
    ('taranan sınırı "> 0,5"', '    return pay >= 0.5', '    return pay > 0.5'),
    ('f_PK K1b algılamasıyla sayılır', "f_PK = sum(1 for r in negs if r['W_algilama'])",
     "f_PK = sum(1 for r in negs if r.get('algilama'))"),
    ('MDA algılama veren negatifte de', "if sat['durum'] == 'tarandi' and not sat['W_algilama']:",
     "if sat['durum'] == 'tarandi':"),
    ('dal (d) A90 sınırı dışlayıcı', 'a90 is not None and a90 <= A90_TAVAN:', 'a90 is not None and a90 < A90_TAVAN:'),
    ('K1b üst ucu dışlayıcı (I′ başı = K1b sonu kesişmez)', 'return Ip[0] < ara[1] + 1 and Ip[1] > ara[0]',
     'return Ip[0] < ara[1] and Ip[1] > ara[0]'),
    ('E-2 güç tablosu bir kaymış', "v = _MDE['ek']['k_guc_s07_q01'].get(f'k{k}')",
     "v = _MDE['ek']['k_guc_s07_q01'].get(f'k{k + 1}')"),
    ('algılama sırası B önce', "sira = {'N': 0, 'P': 1, 'B': 2, 'Nayri': 3}", "sira = {'N': 1, 'P': 2, 'B': 0, 'Nayri': 3}"),
    ('GENLIK4 bir olay eksik (Peru 2007 yok)', "GENLIK4 = ('200412231459', '200503281609', '200704012039', '200708152340')",
     "GENLIK4 = ('200412231459', '200503281609', '200704012039')"),
    ('D-9 etiketi yalnız taranmayanda değil, sınıf P\'de de aranır', "g4 = [b for b in N if b['genlik4']]",
     "g4 = [b for b in P + N if b['genlik4'] or b['sinif'] == 'P']"),
]


def suite(KM, R=None, ozet=None):
    R = R or Kayit()
    for ad, fn in (('birim', lambda: birim(KM, R)), ('kapı', lambda: kapi(KM, R)),
                   ('uçtan uca', lambda: uctan_uca(KM, R, {} if ozet is None else ozet))):
        try:
            fn()
        except BaseException as e:   # noqa: BLE001
            R.sina('çöküş', f'{ad}: {type(e).__name__}: {str(e)[:200]}', False)
    return R


def main():
    cikti = sys.argv[1]
    os.makedirs(GECICI, exist_ok=True)
    t0 = time.time()
    ozet = {}
    R = suite(T0, ozet=ozet)
    sure_ana = round(time.time() - t0, 1)
    for x in R.s:
        print(('GEÇTİ ' if x['gecti'] else 'KALDI ') + f"[{x['grup']}] {x['ad']}", flush=True)
        if not x['gecti']:
            print('    ', json.dumps(x['ayrinti'], ensure_ascii=False, default=str)[:800], flush=True)
    mut = []
    if '--mutasyonsuz' not in sys.argv:
        kaynak = open(KOSU_YOL, encoding='utf-8').read()
        HAFIF['acik'] = True
        sec = sys.argv[sys.argv.index('--mut') + 1] if '--mut' in sys.argv else None   # yalnız adında bu geçenler
        for i, (ad, eski, yeni) in enumerate(MUTASYONLAR):
            if sec and sec not in ad:
                continue
            if kaynak.count(eski) != 1:
                mut.append(dict(ad=ad, durum=f'uygulanamadı ({kaynak.count(eski)})', yakalandi=False))
                print('UYGULANAMADI', ad, flush=True)
                continue
            t = time.time()
            n0 = len(ENGEL)
            try:
                KM = modul_yukle(kaynak.replace(eski, yeni), f'tr7c_kosu_kimut{i}')
                Rm = suite(KM)
                kalan = [f"[{x['grup']}] {x['ad']}" for x in Rm.s if not x['gecti']]
            except BaseException as e:   # noqa: BLE001
                kalan = [f'yükleme: {type(e).__name__}: {str(e)[:150]}']
            mut.append(dict(ad=ad, yakalandi=bool(kalan), yakalayan=kalan[:5], n_yakalayan=len(kalan),
                            yasak_girisim=len(ENGEL) - n0, sure_s=round(time.time() - t, 1)))
            print(('YAKALANDI ' if kalan else 'YAKALANMADI ') + ad, kalan[:2], flush=True)
    grup = {}
    for x in R.s:
        grup.setdefault(x['grup'], [0, 0])
        grup[x['grup']][0] += 1
        grup[x['grup']][1] += x['gecti']
    out = dict(aciklama='TR-7c bağımsız kod incelemesi: incelemecinin sınamaları ve mutasyonları; yalnız yapay veri; '
                        'denetim kancası soket, /mnt/project-files, kosu/ yazma ve alt süreçleri reddeder.',
               kod_sha256={'tr7c_kosu.py': T0.sha256_dosya(KOSU_YOL), 'tr7c_kodinc.py': T0.sha256_dosya(__file__)},
               sinama=dict(toplam=len(R.s), gecen=sum(x['gecti'] for x in R.s), gruplar=grup),
               sinamalar=R.s, ozet=ozet,
               mutasyon=dict(toplam=len(mut), yakalanan=sum(m['yakalandi'] for m in mut), liste=mut),
               engellenen_giris=ENGEL, sure_s=dict(ana=sure_ana, toplam=round(time.time() - t0, 1)))
    with open(cikti, 'w', encoding='utf-8') as f:
        f.write(json.dumps(out, ensure_ascii=False, indent=1, default=str) + '\n')
    print(json.dumps(dict(sinama=grup, mutasyon=[out['mutasyon']['toplam'], out['mutasyon']['yakalanan']],
                          engellenen=len(ENGEL), sure=out['sure_s']), ensure_ascii=False))


if __name__ == '__main__':
    main()
