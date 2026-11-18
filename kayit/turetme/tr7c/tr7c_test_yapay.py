#!/usr/bin/env python3
"""TR-7c koşu kodunun (`tr7c_kosu.py`) YALNIZ YAPAY VERİDE sınaması (§10 adım 2): birim sınamaları, uçtan uca yapay
senaryolar ve kaynak düzeyinde mutasyon sınamaları.

Körlük: Bu süreç bir denetim kancası (sys.addaudithook) kurar: her soket çağrısı ve `/mnt/project-files` altındaki her
dosya açma girişimi REDDEDİLİR ve kayda geçer; kapı sınamalarında ayrıca alt süreç, `kosu/` çıktı dizinine yazma ve dizin
kurma reddedilir. Hiçbir gerçek dalga formu, zarf ya da ağ isteği yoktur. Pencereler `tr7b_yapay.py` / `tr7b_yapay2.py`
üreteçleriyle (değiştirilmeden) bellekte kurulur.

Yapay senaryoların sınırları (O-n'ye bakınız): MDA bir taslak işlevle (A_basamak eşiği rastgele) üretilir, çünkü TR-7
`mda_deneme` 100 Hz parça verisi ister; `k5_mda_baglami`nın K5'i MDA algılamasına bağladığı ayrıca birim sınamasıyla
gösterilir. Modülasyon için başvuru hızı dar bantlı rastgele bir dizidir (15–30 sn); tremor zarfı onun fazına kilitlidir.

Kullanım: python3 -I -B tr7c_test_yapay.py <çıktı.json> [--hizli]   (--hizli: mutasyonları atla)
"""
import contextlib
import copy
import fractions
import hashlib
import importlib.util
import json
import math
import os
import shutil
import subprocess
import sys
import time

sys.dont_write_bytecode = True
os.environ.setdefault('OMP_NUM_THREADS', '1')
BURA = os.path.dirname(os.path.abspath(__file__))
KOSU_YOL = os.path.join(BURA, 'tr7c_kosu.py')
GECICI = '/tmp/claude-0/-home-user/635decb6-3930-5a4d-9c31-b6f30d64fb94/scratchpad/tr7c_kod'
YASAK_KOK = '/mnt/project-files'
CIKTI_GERCEK = os.path.join(BURA, 'kosu')

# ---------------------------------------------------------------- denetim kancası (ağ ve gerçek veri yasak)
ENGELLENEN = []
KUM = {'havuz': False}


def _yol(a):
    try:
        if isinstance(a, int):
            return None
        return os.path.abspath(os.fsdecode(a))
    except Exception:
        return None


def _denetim(olay, args):
    if olay.startswith('socket.') and olay not in ('socket.__new__',):
        ENGELLENEN.append((olay, repr(args)[:160]))
        raise PermissionError(f'YAPAY SINAMA: ağ yasak ({olay})')
    if olay == 'socket.__new__':
        ENGELLENEN.append((olay, repr(args)[:160]))
        raise PermissionError('YAPAY SINAMA: soket yasak')
    if olay == 'open' and args:
        p = _yol(args[0])
        if p and (p == YASAK_KOK or p.startswith(YASAK_KOK + os.sep)):
            ENGELLENEN.append((olay, p))
            raise PermissionError(f'YAPAY SINAMA: gerçek veri yolu yasak: {p}')
        if p and (p == CIKTI_GERCEK or p.startswith(CIKTI_GERCEK + os.sep)):
            mod = args[1] if len(args) > 1 else 'r'
            if isinstance(mod, str) and any(c in mod for c in 'wax+'):
                ENGELLENEN.append((olay, p))
                raise PermissionError(f'YAPAY SINAMA: gerçek çıktı dizinine yazma yasak: {p}')
    if KUM['havuz']:
        if olay in ('subprocess.Popen', 'os.system', 'os.exec', 'os.posix_spawn', 'os.fork'):
            ENGELLENEN.append((olay, repr(args)[:160]))
            raise PermissionError(f'YAPAY SINAMA (kum havuzu): {olay} yasak')
        if olay in ('os.mkdir', 'os.makedirs') and args:
            p = _yol(args[0])
            if p and (p.startswith(CIKTI_GERCEK) or p.startswith(YASAK_KOK)):
                ENGELLENEN.append((olay, p))
                raise PermissionError(f'YAPAY SINAMA (kum havuzu): dizin yasak: {p}')


sys.addaudithook(_denetim)

import numpy as np  # noqa: E402
from scipy.signal import hilbert  # noqa: E402
from scipy.stats import beta as _beta, binom as _binom  # noqa: E402

sys.path.insert(0, BURA)
import tr7c_kosu as T0  # noqa: E402  (özgün)
K = T0.K
Y2 = T0.Y2
Y = T0.Y


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


# ---------------------------------------------------------------- sınama kaydı
class Kayit:
    def __init__(self):
        self.s = []

    def sina(self, grup, ad, kosul, ayrinti=None):
        self.s.append(dict(grup=grup, ad=ad, gecti=bool(kosul), ayrinti=ayrinti))
        return bool(kosul)

    def kalan(self):
        return [x for x in self.s if not x['gecti']]


def beklenen_hata(fn, tur, icerik=None):
    try:
        fn()
    except tur as e:
        return icerik is None or icerik in str(e), str(e)[:200]
    except BaseException as e:   # noqa: BLE001
        return False, f'beklenmeyen {type(e).__name__}: {str(e)[:200]}'
    return False, 'hata yükselmedi'


# ================================================================ BAĞIMSIZ BAŞVURU (Z3, Z4, D-7; metinden yeniden yazıldı)
_XM = {}


def ref_xmin(n, f, N):
    if N <= 0:
        return None
    if (n, f, N) not in _XM:
        pu = 1.0 if f >= N else float(_beta.ppf(0.95, f + 1, N - f))
        _XM[(n, f, N)] = next((x for x in range(2, n + 1) if _binom.sf(x - 1, n, pu) <= 0.05), None)
    return _XM[(n, f, N)]


_FI = {}


def ref_fisher(xp, n, xn, m):
    """Kesin kesir: P(X ≥ X_P | X_P + X_N, n_P, n_N)."""
    k = (xp, n, xn, m)
    if k not in _FI:
        top, tot = xp + xn, n + m
        if tot == 0:
            _FI[k] = fractions.Fraction(1)
        else:
            _FI[k] = fractions.Fraction(sum(math.comb(n, x) * math.comb(m, top - x) for x in range(xp, min(top, n) + 1)),
                                        math.comb(tot, top))
    return _FI[k]


def ref_dal(nP, nN, XP, XN, f, N, Molc, Mmod, A90):
    if nP < 8 or nN < 20:
        return 'a', None
    xm = ref_xmin(nP, f, N)
    i = xm is not None and XP >= max(-(-nP // 2), xm)
    ii = N >= 5 and f / N <= 0.30
    iii = ref_fisher(XP, nP, XN, nN) <= fractions.Fraction(1, 20)
    iv = Mmod >= 3
    if i and ii and iii and iv:
        return 'b', None
    if i and ii and Molc >= 3:
        return 'c', ' ve '.join(x for x, v in (('(iii)', iii), ('(iv)', iv)) if not v)
    a90ok = isinstance(A90, (int, float)) and not isinstance(A90, bool) and A90 <= 1e5
    if (not i or not ii) and a90ok:
        return 'd', None
    if i and ii and Molc < 3:
        return 'e', 'modülasyon ölçülemedi'
    return 'e', 'yöntem'


FAR_KOMB = [(0, 120, 50.0), (40, 120, 50.0), (3, 4, 50.0), (0, 120, 'belirsiz'), (10, 120, '> 100 µm/s'),
            (0, 120, 2e5), (12, 30, 9.0), (30, 120, 50.0), (0, 4, 50.0)]


def izgara(KM, tam=True):
    """Z4 + D-7 ızgarası: kod ile bağımsız başvuru birebir mi; her noktada tek dal; Marmara yalnız (b)."""
    nPs = range(0, 11) if tam else (7, 8, 10)
    nNs = range(0, 30) if tam else (19, 20, 29)
    xmc = {}
    orj = KM.xmin

    def xm_bellek(n, f, N):                       # yalnız bellekleme; işlev aynı
        if (n, f, N) not in xmc:
            xmc[(n, f, N)] = orj(n, f, N)
        return xmc[(n, f, N)]
    KM.xmin = xm_bellek
    say, uyusmaz, marmara_yanlis, dal_say = 0, [], 0, {}
    try:
        for nP in nPs:
            for nN in nNs:
                for XP in range(nP + 1):
                    for XN in range(nN + 1):
                        if not tam and XN not in (0, 1, 2, 3, nN // 2, nN):
                            continue
                        for Molc in range(XP + 1):
                            for Mmod in sorted({0, 2, 3, Molc} & set(range(Molc + 1))):
                                for f, N, A90 in FAR_KOMB:
                                    say += 1
                                    d, alt, _ = KM.k1c_dal(nP, nN, XP, XN, f, N, Molc, Mmod, A90)
                                    r = ref_dal(nP, nN, XP, XN, f, N, Molc, Mmod, A90)
                                    dal_say[d] = dal_say.get(d, 0) + 1
                                    if (d, alt) != r and len(uyusmaz) < 20:
                                        uyusmaz.append(dict(nokta=[nP, nN, XP, XN, f, N, Molc, Mmod, A90], kod=[d, alt],
                                                            ref=list(r)))
                                    elif (d, alt) != r:
                                        uyusmaz.append(None)
                                    if KM.marmara_acilir(d) != (d == 'b'):
                                        marmara_yanlis += 1
    finally:
        KM.xmin = orj
    return dict(nokta=say, uyusmaz=len(uyusmaz), ilk_uyusmazlar=[u for u in uyusmaz if u][:10],
                marmara_yanlis=marmara_yanlis, dal_sayilari=dal_say)


# ================================================================ YAPAY PENCERELER
W0, W1 = Y.W_IX
TT = Y.T
K1B_EKSEN = (W0 + 200, W0 + 1400)
ISTASYON_KOORD = [(35.90, -120.43), (35.95, -120.50), (35.85, -120.40), (36.00, -120.55)]
PKD = (35.9452, -120.5416)
_ONBELLEK = {}


def lp_v(rng):
    X = np.fft.rfft(rng.standard_normal(TT))
    f = np.fft.rfftfreq(TT, 1.0)
    X[(f < 1 / 30) | (f > 1 / 15)] = 0
    v = np.fft.irfft(X, TT)
    return v / v.std()


def pencere_uret(tohum, cfg):
    """cfg: dict(veri, A (yalnız 2–8 Hz tremor genliği; 0 yok), kilitli (zarf v fazına kilitli; değilse düz 300 sn),
    koda (TR-7b Y3 bölgesel koda ×20), leak ([a_y, κ, 'egim'|'sabit'] TR-7b Y2 telesismik sızıntı ya da None), n_ist)."""
    anahtar = (tohum, json.dumps(cfg, sort_keys=True))
    if anahtar in _ONBELLEK:
        return _ONBELLEK[anahtar]
    rng = np.random.default_rng(tohum)
    v = lp_v(rng)
    if not cfg.get('veri', True):
        pv = dict(durum='veri_yok', n_gecen=0, v=v)
        _ONBELLEK[anahtar] = pv
        return pv
    tremor = None
    A = float(cfg.get('A', 0.0))
    bas = None
    if A:
        bas = int(rng.integers(K1B_EKSEN[0] + 50, K1B_EKSEN[1] - 350))
        faz = np.angle(hilbert(v))
        e1 = np.zeros(TT)
        tt = np.arange(TT) - bas
        m = (tt >= 0) & (tt < 300)
        sek = np.maximum(0.0, np.cos(faz)) if cfg.get('kilitli', True) else np.ones(TT)
        e1[m] = sek[m] * np.minimum(1, np.minimum(tt[m], 300 - tt[m]) / 10)
        tremor = np.repeat(e1, int(Y.FS))
    sekil = norm = None
    if cfg.get('koda'):                                   # TR-7b Y3: bölgesel koda ×20 (W içinde)
        bas = int(rng.integers(K1B_EKSEN[0] + 50, K1B_EKSEN[1] - 350))
        tremor, norm = Y2.koda_zarf(bas)
        A, sekil = 20.0, Y.KODA
    tele = None
    if cfg.get('leak'):
        ay, ka, bicim = cfg['leak']
        ey, e = Y2.tele_zarf(rng, bicim)
        tele = (ey, e, ay, ka)
    n_ist = cfg.get('n_ist', 4)
    st = Y2.istasyonlar(rng, tremor=tremor, A=A, sekil=sekil, norm=norm, tele=tele, n_ist=n_ist)
    maske = np.zeros(TT, bool)
    ist = []
    for i, (Cy, Cd) in enumerate(st):
        x = K.istasyon(Cy, Cd, Y.R_IX, Y.W_IX, maske, ad=f'YY.S{i}')
        x['la'], x['lo'] = ISTASYON_KOORD[i % len(ISTASYON_KOORD)]
        ist.append(x)
    pv = dict(durum='tarandi', n_gecen=n_ist, ist=ist, maske=maske, Wb=Y.W_IX, Q=Y.Q_IX, k0=0, v=v, bas=bas)
    _ONBELLEK[anahtar] = pv
    return pv


def tohum_of(s, tohum0):
    return int(hashlib.sha256(f'{tohum0}|{s}'.encode()).hexdigest()[:12], 16)


class YapayKaynak:
    """Kaynak arayüzü (bellekte). senaryo: birim → cfg; ref_yok: başvuru kanalı olmayan birimler."""
    gercek = False

    def __init__(self, KM, senaryo, tohum0=20261117, n_neg=12, ref_yok=(), bprime=False, sayac=None):
        self.KM, self.sen, self.t0, self.n_neg, self.ref_yok, self.bprime = KM, senaryo, tohum0, n_neg, set(ref_yok), \
            bprime
        self.sayac = {'pencere': 0} if sayac is None else sayac
        self._b = None

    def birimler(self):
        if self._b is None:
            bs = self.KM.birimler_kur()
            for b in bs:
                b['K1b_epoch'] = b['K1b']
            self._b = bs
        return self._b

    def negatifler(self):
        return [dict(id=f'neg{i:03d}', olay='yapay', sira=i, tur='neg') for i in range(self.n_neg)]

    def _cfg(self, desc):
        if desc.get('tur') == 'neg':
            return self.sen('neg', desc)
        return self.sen(desc['sinif'], desc)

    def pencere(self, desc):
        self.sayac['pencere'] += 1
        cfg = self._cfg(desc)
        pv = dict(pencere_uret(tohum_of(desc['id'], self.t0), cfg))
        pv['id'] = desc['id']
        pv['K1b'] = None if desc.get('tur') == 'neg' else K1B_EKSEN
        return pv

    def lp_adaylari(self, desc, pv):
        ok = desc['id'] not in self.ref_yok
        v = dict(Z=pv['v'], R=None, T=None)
        return [dict(ad='NC.PHA', la=35.80, lo=-120.30,
                     kanallar=[dict(kod='EHZ', konum='', uygun_yanit=True, ortu_ok=True, v=v)]),
                dict(ad='BK.PKD', la=PKD[0], lo=PKD[1],
                     kanallar=[dict(kod='BHZ', konum='00', uygun_yanit=True, ortu_ok=ok, v=v if ok else None),
                               dict(kod='HHZ', konum='00', uygun_yanit=True, ortu_ok=ok, v=v if ok else None)])]

    def mda(self, desc, pv, rng, n_bas):
        out = []
        for _ in range(n_bas):
            a = 10 ** rng.uniform(0.9, 1.2)
            out.append(dict(bas=int(rng.integers(60, 1540)), alg=[bool(x >= a) for x in K.A_BASAMAK]))
        return out

    def b_prime_girdisi(self, desc, pv):
        if (self.bprime is True or (self.bprime and desc['id'] in self.bprime)) and pv.get('bas') is not None:
            return [], [float(pv['bas'] - 30)]          # bir çekirdek fazı I′ başından 30 sn önce → (b′) (ii)
        return [], []


# senaryolar: (sınıf, birim) → cfg
LEAK_ZAYIF = (5, 12.5, 'egim')     # TR-7b Y1: K0 bunu tremorla birlikte atar (0,97–1,00), K5 atmaz


def sen_gercek(P_tremor=8, genlik_N=()):
    def s(sinif, b):
        if sinif == 'neg':
            return dict(A=0)
        if sinif == 'P':
            i = T0.P_OLAY.index(b['evids'][0])
            return dict(A=10.0 if i < P_tremor else 0.0, leak=list(LEAK_ZAYIF))
        if sinif == 'N' and b['id'] in genlik_N:
            return dict(A=10.0, leak=list(LEAK_ZAYIF))
        return dict(A=0, leak=list(LEAK_ZAYIF))
    return s


def sen_ayirt_etmeyen(sinif, b):
    if sinif == 'neg':
        return dict(A=0)
    return dict(A=10.0, leak=list(LEAK_ZAYIF))


def sen_genlik_sizinti(sinif, b):
    """Tremor dışı, yüzey dalgasına kilitli OLMAYAN, yalnız 2–8 Hz bir sinyal; genliği tetikleyici PGV_T'yi izler
    (A = 10·PGV_T/0,03, en çok 20). K5 bunu atmaz (Δ_d < Δ_y); D30M3'te yalnız (iv) onu kırabilir."""
    if sinif == 'neg':
        return dict(A=0)
    a = min(20.0, 10.0 * b['pgv_t'] / 0.03)
    return dict(A=round(a, 3), kilitli=False, leak=list(LEAK_ZAYIF)) if a >= 0.5 else dict(A=0, leak=list(LEAK_ZAYIF))


def sen_tele_sizinti(sinif, b):
    """TR-7b Y2 'sabit' (W boyunca telesismik koda sızıntısı), a_y PGV_T ile 2…10, κ 12,5: K5'in hedefi."""
    if sinif == 'neg':
        return dict(A=0)
    a = min(10.0, max(2.0, 2.0 + 8.0 * math.sqrt(b['pgv_t'] / 0.08)))
    return dict(A=0, leak=[round(a, 2), 12.5, 'sabit'])


def sen_veri_yok(sinif, b):
    return dict(veri=False)


def kos(KM, kaynak, ad, ayar=None):
    d = os.path.join(GECICI, 'e2e', f'{ad}_{os.getpid()}_{time.time_ns()}')
    os.makedirs(d)
    ayar = KM.Ayar(mod_n=100) if ayar is None else ayar
    h = KM.k1c_kos(kaynak, dizin=d, ayar=ayar, gunluk=lambda *a: None)
    return h, d


# ================================================================ BİRİM SINAMALARI
def birim(KM, R, tam_izgara):
    g = 'birim'
    # --- dal ızgarası
    iz = izgara(KM, tam=tam_izgara)
    R.sina(g, f'Z4+D-7 ızgarası ({"tam" if tam_izgara else "küçük"}; {iz["nokta"]} nokta) bağımsız başvuruyla birebir',
           iz['uyusmaz'] == 0, iz)
    R.sina(g, 'Marmara yalnız (b)', iz['marmara_yanlis'] == 0, iz['marmara_yanlis'])
    d, alt, _ = KM.k1c_dal(8, 20, 0, 0, 0, 120, 0, 0, 11.2)
    R.sina(g, 'D-7 örneği (n_P 8, X_P 0, n_N 20, X_N 0, A90 uygun) → (d)', (d, alt) == ('d', None), [d, alt])
    d, alt, _ = KM.k1c_dal(10, 29, 8, 0, 0, 120, 2, 2, 11.2)
    R.sina(g, '(i),(ii),(iii) var, M_ölç 2 → (e) modülasyon ölçülemedi', (d, alt) == ('e', 'modülasyon ölçülemedi'),
           [d, alt])
    d, alt, _ = KM.k1c_dal(10, 29, 8, 0, 0, 120, 3, 3, 'belirsiz')
    R.sina(g, 'Z3 tam → (b) (A90 belirsiz olsa da)', d == 'b', [d, alt])
    d, alt, _ = KM.k1c_dal(10, 29, 8, 20, 0, 120, 5, 2, 11.2)
    R.sina(g, '(c) kalan "(iii) ve (iv)"', (d, alt) == ('c', '(iii) ve (iv)'), [d, alt])
    d, alt, _ = KM.k1c_dal(10, 29, 8, 0, 0, 4, 5, 5, 11.2)
    R.sina(g, 'N_PK < 5 → (ii) yok → (d)', d == 'd', [d, alt])
    d, alt, _ = KM.k1c_dal(7, 29, 7, 0, 0, 120, 5, 5, 11.2)
    R.sina(g, 'n_P 7 → (a)', d == 'a', d)
    d, alt, _ = KM.k1c_dal(10, 19, 8, 0, 0, 120, 5, 5, 11.2)
    R.sina(g, 'n_N 19 → (a)', d == 'a', d)
    # --- X_min, Fisher
    R.sina(g, 'X_min yoksa None (N = 0)', KM.xmin(10, 0, 0) is None)
    xs = [(n, f, N) for n in (8, 10) for f in (0, 3, 12, 30) for N in (20, 120)]
    R.sina(g, 'X_min: TR-7 §8 (K2 kapısız) = scipy başvurusu', all(KM.xmin(*a) == ref_xmin(*a) for a in xs),
           {str(a): [KM.xmin(*a), ref_xmin(*a)] for a in xs})
    R.sina(g, 'X_min K2 kapısı yok (O-12): f/N > 0,05 iken de sayı', KM.xmin(10, 12, 120) is not None
           and K.x_min(10, 12, 120) == 'K2', [KM.xmin(10, 12, 120), K.x_min(10, 12, 120)])
    fs = [(xp, 10, xn, 29) for xp in range(11) for xn in range(30)] + [(0, 0, 0, 0)]
    R.sina(g, 'Fisher tek yanlı = kesin hipergeometrik üst kuyruk (311 hücre)',
           all(abs(KM.fisher_tek(*a) - float(ref_fisher(*a))) < 1e-12 for a in fs))
    R.sina(g, 'Fisher yönü: P fazlası küçük p, N fazlası büyük p',
           KM.fisher_tek(8, 10, 1, 29) < 1e-4 and KM.fisher_tek(1, 10, 8, 29) > 0.9,
           [KM.fisher_tek(8, 10, 1, 29), KM.fisher_tek(1, 10, 8, 29)])
    spec = importlib.util.spec_from_file_location('tr7c_guc_', os.path.join(BURA, 'tr7c_guc.py'))
    G = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(G)
    R.sina(g, 'Fisher = tr7c_guc.py fisher_tek (yazarın seçimi 1)',
           all(abs(KM.fisher_tek(*a) - G.fisher_tek(*a)) < 1e-15 for a in fs if a[1] + a[3] > 0))
    # --- D-1
    bs = KM.birimler_kur()
    P = [b for b in bs if b['sinif'] == 'P']
    N = [b for b in bs if b['sinif'] == 'N']
    B = [b for b in bs if b['sinif'] == 'B']
    v = [b for b in N if b['id'] == KM.VANUATU_BIRIM]
    R.sina(g, 'D-1: 10 P, 29 N birimi (30 olay), 2 bilgi', (len(P), len(N), len(B)) == (10, 29, 2)
           and sum(len(b['evids']) for b in N) == 30, [len(P), len(N), len(B)])
    R.sina(g, 'D-1: N27 + N28 tek birim, K1b USTVERI\'den (ilk başı, son sonu)', len(v) == 1 and
           v[0]['evids'] == list(KM.VANUATU) and v[0]['K1b'][0] <= v[0]['K1b_formul'][0] + 1 and
           v[0]['K1b'][1] >= v[0]['K1b_formul'][1] - 1, v[0]['K1b'] if v else None)
    R.sina(g, 'D-9: genlik4 bayrağı tam 4 N biriminde', sum(b['genlik4'] for b in N) == 4 and
           not any(b['genlik4'] for b in P))
    R.sina(g, 'birimler T0 sırasında', [b['t0'] for b in bs] == sorted(b['t0'] for b in bs))
    # --- K1b kesişimi (kapsayıcı uç)
    R.sina(g, 'K1b kapsayıcı uç: I′ [200, 250) ile [100, 200] kesişir; [201, 250) ile kesişmez',
           KM.kesisir((200, 250), (100, 200)) and not KM.kesisir((201, 250), (100, 200))
           and KM.kesisir((50, 101), (100, 200)) and not KM.kesisir((50, 100), (100, 200)))
    # --- E-1
    vv = np.zeros(10)

    def kan(kod, ok=True, yan=True, konum='00', R_=True):
        return dict(kod=kod, konum=konum, uygun_yanit=yan, ortu_ok=ok,
                    v=dict(Z=vv, R=vv if R_ else None, T=vv if R_ else None))   # v örtü kalsa da verilir
    yakin = dict(ad='BK.YAK', la=35.92, lo=-120.46, kanallar=[kan('BHZ'), kan('HHZ')])
    uzak = dict(ad='NC.UZK', la=36.30, lo=-120.90, kanallar=[kan('HHZ')])
    s = KM.e1_secim([uzak, yakin])
    R.sina(g, 'E-1: en yakın uygun istasyon, onda önce HH', s is not None and (s['ad'], s['kanal']) == ('BK.YAK', 'HHZ'),
           s and [s['ad'], s['kanal']])
    s = KM.e1_secim([uzak, dict(yakin, kanallar=[kan('BHZ'), kan('HHZ', ok=False)])])
    R.sina(g, 'E-1: HH örtüsü < %90 → aynı istasyonda BH', s and (s['ad'], s['kanal']) == ('BK.YAK', 'BHZ'))
    s = KM.e1_secim([uzak, dict(yakin, kanallar=[kan('HHZ', yan=False), kan('EHZ'), kan('LHZ'), kan('HNZ'),
                                                  kan('BHN')])])
    R.sina(g, 'E-1: uygunsuz yanıt, E/L bant, N alet, yatay kanal dışlanır → uzak istasyon', s and s['ad'] == 'NC.UZK')
    s = KM.e1_secim([dict(yakin, kanallar=[kan('HHZ', R_=False)])])
    R.sina(g, 'E-1: iki yatay yoksa yalnız Z', s and s['bilesen'] == 1)
    s = KM.e1_secim([dict(yakin, kanallar=[kan('HHZ')])])
    R.sina(g, 'E-1: iki yatay varsa üç bileşen', s and s['bilesen'] == 3)
    R.sina(g, 'E-1: uygun kanal yoksa None', KM.e1_secim([dict(yakin, kanallar=[kan('HHZ', ok=False)])]) is None)
    # --- E-2, D-8, D-10, (b′), D-9 cümleleri
    et = dict(b_prime=False, mod_gecti=True, genlik=False, genlik_olculemeyen=0, k_kosu=10)
    c = KM.k1c_cumle('b', None, 10, 29, 8, 11.2, et)
    R.sina(g, 'E-2: k_koşu 10 → güç satırı yok', 'k: üstveriden 10, koşuda 10' in c and 'k_koşu ile güç' not in c, c)
    c = KM.k1c_cumle('b', None, 10, 29, 8, 11.2, dict(et, k_kosu=6))
    mde = json.load(open(os.path.join(BURA, 'tr7c_mde_ek.json')))['k_guc_s07_q01']['k6']
    inc1 = json.load(open(os.path.join(BURA, 'inc1', 'tr7c_inc1.json')))['esik']['D1_kref_guc_s0.7_q0.1']
    R.sina(g, 'E-2: k_koşu 6 → güç (dondurulmuş tablo) bilgi olarak', 'koşuda 6' in c and
           f'{KM.say(mde["mt08"])} (m_t 0,8) / {KM.say(mde["mt05"])} (m_t 0,5)' in c, c)
    R.sina(g, 'E-2 tablosu inc1 D1_kref ile aynı (ortak hücreler)',
           all(json.load(open(os.path.join(BURA, 'tr7c_mde_ek.json')))['k_guc_s07_q01'][k] == v_ for k, v_ in
               inc1.items()))
    c = KM.k1c_cumle('c', '(iii)', 9, 27, 7, 11.2, et)
    m = KM.mde_degeri(9, 27)
    R.sina(g, 'Ö-d + D-8 eki (c): kalan ve MDE değerleri', '(kalan: (iii))' in c and
           f's = {KM.say(m[0])} (m_t 0,8) / {KM.say(m[1])} (m_t 0,5)' in c and c.index('kalan') < c.index('ayırt'), c)
    c = KM.k1c_cumle('d', None, 10, 29, 2, 11.2, et)
    R.sina(g, 'D-8 eki (d) ve X_P / n_P, A90', 'X_P = 2 / n_P = 10' in c and 'A90_PK = 11,2 nm/s' in c and
           'görülebilir en küçük s' in c, c)
    c = KM.k1c_cumle('e', 'yöntem', 10, 29, 2, 'belirsiz', et)
    R.sina(g, 'D-8 eki (e)', c.startswith('ölçü sınanamadı (yöntem)') and 'görülebilir en küçük s' in c, c)
    c = KM.k1c_cumle('b', None, 10, 29, 8, 11.2, dict(et, mod_gecti=False))
    R.sina(g, 'D-10 cümlesi', c.startswith('ölçü sınandı (Parkfield modülasyonu geçmedi: Marmara\'da en çok "aday")'), c)
    c = KM.k1c_cumle('b', None, 10, 29, 8, 11.2, dict(et, b_prime=True))
    R.sina(g, '(b′) "geçti, belirsiz"', 'geçti, belirsiz' in c, c)
    c = KM.k1c_cumle('b', None, 10, 29, 8, 11.2, dict(et, genlik=True, genlik_olculemeyen=1))
    R.sina(g, 'D-9 etiketi ve ölçülemeyen sayısı', 'genlik karıştırıcısı dışlanmadı' in c and
           'modülasyonu ölçülemeyen: 1' in c, c)
    R.sina(g, '"VAR" şartları (§6.2): yalnız (b), (b′) yok, mod geçti, D-9 yok',
           KM.var_verilebilir('b', et) and not KM.var_verilebilir('b', dict(et, genlik=True)) and
           not KM.var_verilebilir('b', dict(et, b_prime=True)) and not KM.var_verilebilir('b', dict(et, mod_gecti=False))
           and not KM.var_verilebilir('c', et))
    # --- ŝ, ŝ_alt, Z6
    R.sina(g, 'ŝ arındırılmış (8/10, 3/29)', abs(KM.s_sapka(8, 10, 3, 29) - (0.8 - 3 / 29) / (1 - 3 / 29)) < 1e-12,
           KM.s_sapka(8, 10, 3, 29))
    R.sina(g, 'ŝ ≥ 0 (X_N oranı büyükse 0)', KM.s_sapka(1, 10, 10, 29) == 0.0)
    ca = KM.cp_alt(8, 10)
    R.sina(g, 'CP alt sınırı: P(Bin(10, p_alt) ≥ 8) = 0,05', abs(K.binom_ust(10, ca, 8) - 0.05) < 1e-9, ca)
    z = KM.z6_cumle('S2', 9, 20.0, 15.0, 0.5, 8)
    R.sina(g, 'Z6/D-6: A90/A_PK > 1 → ek bağlayıcı', 'görülemezdi' in z and '(1 − ŝ)' not in z)
    z = KM.z6_cumle('S2', 9, 10.0, 15.0, 0.5, 8)
    R.sina(g, 'Z6/D-6: n_açık üssü', '(1 − ŝ)^n_açık = 0,004 (n_açık = 8)' in z, z)
    z = KM.z6_cumle('S2', 9, 10.0, 15.0, 0.5, 4)
    R.sina(g, 'D-6: n_açık < 5 → hesaplanmadı', 'hesaplanmadı (n_açık < 5)' in z)
    z = KM.z6_cumle('S2', 9, 'belirsiz', 15.0, 0.5, 8)
    R.sina(g, 'D-6: A90 belirsiz → oran > 1', 'görülemezdi' in z)
    # --- (b′)
    R.sina(g, '(b′) kümesi: E1 sonundan ≤ 5 sn ya da çekirdek fazından −10…+120 sn',
           KM.b_prime_kume(1000, [996], []) and KM.b_prime_kume(1000, [], [890]) and
           not KM.b_prime_kume(1000, [994], [879]) and KM.b_prime_kume(1000, [], [1010]))
    # --- k1c_hesap sayımı (modülasyon eşiği, ölçülebilir olay, k_koşu, D-9)
    R.sina(g, 'modülasyon sayımı: p ≤ 0,01 (eşik TR-7 §6.4)', _k1c_hesap_sayim(KM))
    R.sina(g, 'tohumlar ön kayıttaki gibi (20261112 + 3, + 2, 20261116 + 1)',
           (KM.MOD_TOHUM_PK, K.MDA_TOHUM, KM.NEG_TOHUM) == (20261115, 20261114, 20261117))
    R.sina(g, 'K5 = TR-7b tr7b_yapay2.K5 (istasyon ve küme toplaması; K0 ile ayırt edici örnekte)', _k5_ayni(KM))
    R.sina(g, 'k5_mda_baglami: MDA algılaması K5 ile, çıkışta K.ayikla eski hâline', _mda_baglam(KM))
    R.sina(g, 'negatif seçim kuralı TR-7 §7.3 tr7_negatif_pencere.sec ile aynı', _negatif_sec_ayni(KM))


def _k1c_hesap_sayim(KM):
    bs = KM.birimler_kur()
    P = [b for b in bs if b['sinif'] == 'P']
    N = [b for b in bs if b['sinif'] == 'N']
    alg = {b['id']: dict(durum='tarandi', algilama=True) for b in P}
    alg.update({b['id']: dict(durum='tarandi', algilama=False) for b in N + [b for b in bs if b['sinif'] == 'B']})
    ps = [0.0099, 0.0099, 0.0099, 0.0099, 0.0099, 0.03, 0.03, None, 'refvar', 0.011]
    mod = {}
    for b, p in zip(P, ps):
        ref = None if p is None else dict(ad='BK.PKD')       # 'refvar': başvuru var ama M hesaplanamadı
        p = None if p == 'refvar' else p
        mod[b['id']] = dict(ref=ref, kumeler=[dict(Ip=[0, 1], M=None if p is None else 0.5, p=p)])
    g4 = [b for b in N if b['genlik4']]
    mod[g4[0]['id']] = dict(ref=dict(ad='BK.PKD'), kumeler=[dict(Ip=[0, 1], M=0.5, p=0.0099)])
    alg[g4[0]['id']]['algilama'] = True

    class Bos:
        def pencere(self, b):
            return dict(id=b['id'], durum='veri_yok', k0=0)

        def b_prime_girdisi(self, b, pv):
            return [], []
    neg = [dict(id=f'n{i}', durum='tarandi', W_algilama=False, mda=[]) for i in range(20)]
    h = KM.k1c_hesap(Bos(), bs, neg, alg, mod)
    return (h['M_olc'], h['M_mod'], h['etiket']['k_kosu'], h['etiket']['genlik'], h['X_N'],
            h['etiket']['genlik_olculemeyen'], h['etiket']['mod_gecti']) == (8, 5, 9, True, 1, 3, True)


def _k5_ayni(KM):
    """k5_ist ve ayikla_k5, TR-7b K5'i istasyon ve küme düzeyinde birebir verir; sınama ayırt edicidir: K0'ın K5'ten
    ayrıldığı (Y1: tremor + telesismik sızıntı) ve K5'in bayrakladığı (Y3 koda) istasyonlar vardır."""
    fark = ayri_k0 = k5_dogru = kume_fark = 0
    for tohum, cfg in [(4300 + i, dict(A=10.0, kilitli=False, leak=[5, 12.5, 'egim'])) for i in range(3)] + \
            [(4400 + i, dict(koda=True, leak=[5, 12.5, 'egim'])) for i in range(3)]:
        pv = pencere_uret(tohum, cfg)
        for k in K.kumeler(pv['ist'], pv['maske'], pv['Wb']):
            bay = []
            for i in k['uyeler']:
                pk = [(a, b) for kk, a, b in k['parcalar'] if kk == i]
                k5 = KM.k5_ist(pv['ist'][i], pk, pv['maske'], pv['Q'])
                ref = bool(Y2.K5(pv['ist'][i], pk, pv['maske'], pv['Q']))
                fark += k5 != ref
                ayri_k0 += ref != bool(Y.K0(pv['ist'][i], pk, pv['maske'], pv['Q']))
                k5_dogru += ref
                bay.append(ref)
            kume_fark += KM.ayikla_k5(pv['ist'], k, pv['maske'], pv['Q'])['sizinti'] != (sum(bay) >= len(bay) / 2)
    return fark == 0 and kume_fark == 0 and ayri_k0 > 0 and k5_dogru > 0


def _mda_baglam(KM):
    eski = K.ayikla
    cagri = []
    orj = KM.ayikla_k5

    def izle(ist, kume, maske, Q):
        cagri.append(Q)
        return orj(ist, kume, maske, Q)
    KM.ayikla_k5 = izle
    try:
        pv = pencere_uret(4243, dict(A=10.0, leak=[2, 12.5, 'egim']))
        with KM.k5_mda_baglami((11, 22)):
            r = K.pencere_algila(pv['ist'], pv['maske'], pv['Wb'])
    finally:
        KM.ayikla_k5 = orj
    return K.ayikla is eski and len(cagri) > 0 and all(q == (11, 22) for q in cagri) and len(r['kumeler']) > 0


def _negatif_sec_ayni(KM):
    import datetime as dt
    tr7 = os.path.join(os.path.dirname(BURA), 'tr7')
    spec = importlib.util.spec_from_file_location('tr7_negatif_pencere_', os.path.join(tr7, 'tr7_negatif_pencere.py'))
    NP = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(NP)
    except Exception:   # noqa: BLE001
        return None
    tz = 'America/Los_Angeles'
    for T0_, kat in ((dt.datetime(2004, 12, 26, 0, 58, 53), []),
                     (dt.datetime(2004, 12, 26, 0, 58, 53), [dt.datetime(2004, 12, 29, 1, 0),
                                                              dt.datetime(2005, 1, 2, 3, 0)]),
                     (dt.datetime(2007, 1, 13, 4, 23, 21), [dt.datetime(2007, 1, 20, 2, 0)]),
                     (dt.datetime(2009, 9, 29, 17, 48, 10), []), (dt.datetime(2010, 2, 27, 6, 34, 14), [])):
        R0, W1 = T0_ + dt.timedelta(seconds=-1800), T0_ + dt.timedelta(seconds=5000)
        a = KM.negatif_sec(np.random.default_rng(5), T0_, R0, W1, kat, tz=tz)
        from zoneinfo import ZoneInfo
        b = [x['d_gun'] for x in NP.sec(np.random.default_rng(5), dict(T0=T0_, R0=R0, W1=W1), ZoneInfo(tz), kat)]
        if a != b or len(a) != 10:
            return False
    return True


# ================================================================ KAPI, KİLİT, SHA
def kapi(KM, R):
    g = 'kapı'
    ok, neden = KM.kosu_dondurulmus_mu()
    R.sina(g, 'kapı bugün KAPALI (Durum: KOŞU DONDURULDU yok)', not ok and 'KOŞU DONDURULDU' in neden, neden)
    once = len(ENGELLENEN)
    KUM['havuz'] = True
    ciktivar = os.path.exists(CIKTI_GERCEK)
    try:
        dene = [
            ('gercek_kapi', lambda: KM.gercek_kapi('sınama'), '(sınama)'),
            ('GercekOrtam()', lambda: KM.GercekOrtam(), '(GercekOrtam)'),
            ('GercekKaynak()', lambda: KM.GercekKaynak(None, None, None, None, None), '(GercekKaynak)'),
            ('asama_kos manifest', lambda: KM.asama_kos('manifest'), '(aşama manifest)'),
            ('asama_kos K1c-indirme', lambda: KM.asama_kos('K1c-indirme'), '(aşama K1c-indirme)'),
            ('asama_kos K1c-algılama', lambda: KM.asama_kos('K1c-algılama'), '(aşama K1c-algılama)'),
            ('asama_manifest', lambda: KM.asama_manifest(None, []), '(manifest)'),
            ('lp_adaylari_manifest', lambda: KM.lp_adaylari_manifest(None, None), '(lp adayları)'),
            ('asama_indirme', lambda: KM.asama_indirme(None, None, None), '(indirme)'),
            ('lp_indir', lambda: KM.lp_indir(None, None, None), '(lp indirme)'),
            ('marmara_kos', lambda: KM.marmara_kos('Marmara-indirme'), '(Marmara Marmara-indirme)'),
            ('main kos', lambda: KM.main(['kos', 'manifest']), '(aşama manifest)'),
            ('main baslat', lambda: KM.main(['baslat', 'manifest']), '(baslat manifest)'),
            ('main marmara', lambda: KM.main(['marmara', 'Marmara-indirme']), '(Marmara Marmara-indirme)'),
            ('baslat', lambda: KM.baslat('K1c-indirme'), '(baslat K1c-indirme)'),
            ('durdu', lambda: KM.durdu('K1c-algılama', 'x'), '(durdu K1c-algılama)'),
            ('main durdu', lambda: KM.main(['durdu', 'K1c-algılama', '--neden', 'x']), '(durdu K1c-algılama)'),
            ('main baslat --surdur', lambda: KM.main(['baslat', 'K1c-algılama', '--surdur']), '(baslat K1c-algılama)'),
            ('k1c_kos gerçek dizin', lambda: KM.k1c_kos(YapayKaynak(KM, sen_veri_yok), dizin=KM.CIKTI), '(k1c_kos)'),
            ('k1c_kos gercek=True', lambda: KM.k1c_kos(YapayKaynak(KM, sen_veri_yok),
                                                     dizin=os.path.join(GECICI, 'kapi_t'), gercek=True), '(k1c_kos)'),
        ]

        class GK(YapayKaynak):
            gercek = True
        dene.append(('k1c_kos gerçek kaynak', lambda: KM.k1c_kos(GK(KM, sen_veri_yok),
                                                                 dizin=os.path.join(GECICI, 'kapi_t2')), '(k1c_kos)'))
        for ad, fn, ic in dene:
            r, msg = beklenen_hata(fn, KM.GercekKipReddedildi, ic)
            R.sina(g, f'kapı içeride reddeder: {ad}', r, msg)
    finally:
        KUM['havuz'] = False
    R.sina(g, 'kapı sınamalarında ağ / gerçek veri / alt süreç girişimi yok', len(ENGELLENEN) == once,
           ENGELLENEN[once:])
    R.sina(g, 'gerçek çıktı dizini kurulmadı', os.path.exists(CIKTI_GERCEK) == ciktivar)
    R.sina(g, 'gercek_yol_mu: zarf deposu ve kosu/ gerçek, geçici dizin değil',
           KM.gercek_yol_mu(KM.ZARF_KOK + '/x') and KM.gercek_yol_mu(KM.CIKTI) and not KM.gercek_yol_mu(GECICI))
    # kapı geçici bir ön kayıt kopyasında açılır; gövde değişince ya da sha eksikse kapanır
    metin = open(KM.ONKAYIT, encoding='utf-8').read()
    ks = KM.kod_sha()
    ac = metin.replace('Durum: KARAR METNİ DONDURULDU', 'Durum: KOŞU DONDURULDU; KARAR METNİ DONDURULDU', 1) + \
        '\n' + '\n'.join(f'{k} {v}' for k, v in ks.items()) + '\n'
    d = os.path.join(GECICI, 'kapi')
    os.makedirs(d, exist_ok=True)
    yol = os.path.join(d, 'onkayit_kopya.md')
    open(yol, 'w', encoding='utf-8').write(ac)
    ok, neden = KM.kosu_dondurulmus_mu(yol)
    R.sina(g, 'kapı açılır: KOŞU DONDURULDU + kod sha256\'ları + gövde aynı (geçici kopya)', ok, neden)
    R.sina(g, 'gercek_kapi(geçici kopya) geçer', beklenen_hata(lambda: KM.gercek_kapi('x', yol), Exception)[1] ==
           'hata yükselmedi')
    open(yol, 'w', encoding='utf-8').write(ac.replace('Z4 (aynen; sıra bağlayıcı)', 'Z4 (aynen;  sıra bağlayıcı)'))
    ok, neden = KM.kosu_dondurulmus_mu(yol)
    R.sina(g, 'kapı kapanır: karar metni gövdesi değişmiş', not ok and 'gövdesi' in neden, neden)
    open(yol, 'w', encoding='utf-8').write(ac.replace(ks['tr7c_kosu.py'], 'x' * 64))
    ok, neden = KM.kosu_dondurulmus_mu(yol)
    R.sina(g, 'kapı kapanır: tr7c_kosu.py sha256 yazılı değil', not ok and 'tr7c_kosu.py' in neden, neden)
    open(yol, 'w', encoding='utf-8').write(ac.replace('Durum: KOŞU DONDURULDU; ', 'Durum: '))
    ok, neden = KM.kosu_dondurulmus_mu(yol)
    R.sina(g, 'kapı kapanır: Durum satırında KOŞU DONDURULDU yok (metnin başka yerinde geçse de)', not ok)
    # Marmara önkoşulu (kapı geçici olarak sınama içinde açılır; marmara_kos hiçbir şey indirmez)
    orj = KM.gercek_kapi
    KM.gercek_kapi = lambda *a, **k: True
    try:
        d2 = os.path.join(GECICI, 'marmara')
        os.makedirs(d2, exist_ok=True)
        hy = os.path.join(d2, KM.HUKUM_AD)
        sonuc = {}
        for dal in ('a', 'c', 'd', 'e', 'b'):
            if os.path.exists(hy):
                os.remove(hy)
            json.dump(dict(dal=dal), open(hy, 'w'))
            r, msg = beklenen_hata(lambda: KM.marmara_kos('Marmara-indirme', d2), KM.Tr7cDur)
            sonuc[dal] = msg
        os.remove(hy)
        r0, m0 = beklenen_hata(lambda: KM.marmara_kos('Marmara-indirme', d2), KM.Tr7cDur, 'hüküm dosyası yok')
    finally:
        KM.gercek_kapi = orj
    R.sina(g, 'Marmara yalnız K1c (b): (a)/(c)/(d)/(e) → "(b) dışında Marmara verisi indirilmez"',
           all('(b) dışında' in sonuc[x] for x in 'acde') and 'yazılmadı' in sonuc['b'] and r0, dict(sonuc, yok=m0))


def protokol(KM, R):
    """§B.4 aşama protokolü (önkoşul, durma kaydı, sürdürme) ve kuru prova düğmesi (§B.3). Ağ yok: provanın taban
    URL'leri 127.0.0.1:9'dur ama hiçbir istek atılmaz (aşama, manifest olmadığı için ağdan önce durur)."""
    g = 'protokol'
    import tr7_indir as I
    z = '2026-11-18T00:00:00+00:00'

    def D(*ciftler, durmalar=()):
        return dict(asamalar={a: dict(durum=d, zaman=z, sha256={}) for a, d in ciftler}, durmalar=list(durmalar))

    def on(asama, d, surdur=False):
        try:
            return KM.onkosul(asama, d, surdur)
        except KM.Tr7cDur as e:
            return 'DUR: ' + str(e)
    T_, H_ = 'tamamlandı', 'hata'
    R.sina(g, 'önkoşul: ilk aşama "yeni"', on('manifest', D()) == 'yeni')
    R.sina(g, 'önkoşul: sıra dışı aşama reddedilir (manifest yokken K1c-indirme; K1c-negatif "hata" iken K1c-algılama)',
           'önceki aşama' in on('K1c-indirme', D()) and 'önceki aşama' in on('K1c-algılama', D(
               ('manifest', T_), ('K1c-indirme', T_), ('K1c-negatif', H_))))
    R.sina(g, 'önkoşul: tamamlanmış aşama ikinci kez başlatılmaz (--surdur ile de)',
           'zaten tamamlandı' in on('manifest', D(('manifest', T_))) and
           'zaten tamamlandı' in on('manifest', D(('manifest', T_)), True))
    d_alg = D(('manifest', T_), ('K1c-indirme', T_), ('K1c-negatif', T_), ('K1c-algılama', H_))
    R.sina(g, 'önkoşul: algılama aşamasına --surdur olmadan ikinci kez girilmez',
           'algılama aşamasına daha önce girildi' in on('K1c-algılama', d_alg))
    R.sina(g, 'önkoşul: yalnız koşu kodunun (kod) durma kaydı sürdürmeye yetmez; elle kayıt gerekir',
           'elle' in on('K1c-algılama', dict(d_alg, durmalar=[dict(asama='K1c-algılama', tur='kod', neden='x',
                                                                   zaman=z)]), True))
    R.sina(g, 'önkoşul: aşamanın son durumundan ÖNCEKİ elle kayıt yetmez',
           'elle' in on('K1c-algılama', dict(d_alg, durmalar=[dict(asama='K1c-algılama', tur='elle', neden='x',
                                                                   zaman='2026-11-17T00:00:00+00:00')]), True))
    R.sina(g, 'önkoşul: elle durma kaydıyla --surdur geçer',
           on('K1c-algılama', dict(d_alg, durmalar=[dict(asama='K1c-algılama', tur='elle', neden='x', zaman=z)]),
              True) == 'surdur')
    R.sina(g, 'önkoşul: indirme aşaması (algılama değil) hata sonrası yeniden başlatılabilir (TR-7 gibi)',
           on('K1c-indirme', D(('manifest', T_), ('K1c-indirme', H_))) == 'surdur')
    R.sina(g, 'önkoşul: hiç başlamamış aşama sürdürülemez; bilinmeyen aşama reddedilir',
           'hiç başlamadı' in on('manifest', D(), True) and 'bilinmeyen' in on('hüküm', D()))
    # kuru prova kipinde (ağsız) aşama protokolü: başlat, hata ile durma kaydı, elle durdu, sürdür, kod değişikliği
    kok = os.path.join(GECICI, 'protokol', str(time.time_ns()))
    pr = KM.Prova(dizin=os.path.join(kok, 'c'), zarf=os.path.join(kok, 'z'),
                  servis={k: f'http://127.0.0.1:9/{k}/fdsnws' for k in I.SERVIS},
                  katalog={k: f'http://127.0.0.1:9/{k}/query' for k in I.KATALOG})
    once = len(ENGELLENEN)
    sonuc = {}
    with KM.prova_ac(pr):
        dz = pr.dizin
        os.makedirs(dz)
        KM.durum_isle(dz, 'manifest', 'tamamlandı')
        KM.durum_isle(dz, 'K1c-indirme', 'tamamlandı')
        sonuc['baslat'] = KM.baslat('K1c-negatif')
        sonuc['baslat2'] = beklenen_hata(lambda: KM.baslat('K1c-negatif'), KM.Tr7cDur, 'zaten başlatıldı')
        sonuc['kos_hata'] = beklenen_hata(lambda: KM.asama_kos('K1c-negatif'), KM.Tr7cDur, 'durdu')
        d1 = KM.durum_oku(dz)
        sonuc['kos_tekrar'] = beklenen_hata(lambda: KM.asama_kos('K1c-negatif'), KM.Tr7cDur, 'başlatılmamış')
        sonuc['baslat_surdursuz'] = beklenen_hata(lambda: KM.baslat('K1c-negatif'), KM.Tr7cDur, 'daha önce girildi')
        sonuc['baslat_elle_yok'] = beklenen_hata(lambda: KM.baslat('K1c-negatif', surdur=True), KM.Tr7cDur, 'elle')
        sonuc['main_durdu'] = KM.main(['durdu', 'K1c-negatif', '--neden', 'sınama: manifest yok'])
        sonuc['surdur'] = KM.baslat('K1c-negatif', surdur=True)
        d2 = KM.durum_oku(dz)
        d2['asamalar']['K1c-negatif']['sha256']['tr7c_kosu.py'] = 'x' * 64
        KM.json_yaz(os.path.join(dz, KM.DURUM_AD), d2)
        sonuc['kod_degisti'] = beklenen_hata(lambda: KM.asama_kos('K1c-negatif'), KM.Tr7cDur, 'değişti')
        go = KM.GercekOrtam(log=lambda *a: None)
        sonuc['ortam'] = (go.servis == pr.servis and go.tr7 == dz and go.zarf == pr.zarf and not go.git_dogrula and
                          go.zaman_asimi == pr.zaman_asimi)
        sonuc['kanca'] = []
        for hedef in (('127.0.0.1', 44457), ('203.0.113.7', 443), ('127.0.0.1', 9)):
            try:
                KM._prova_kancasi('socket.connect', (None, hedef))
                sonuc['kanca'].append('izin')
            except PermissionError:
                sonuc['kanca'].append('ret')
        try:
            KM._prova_kancasi('socket.getaddrinfo', ('earthquake.usgs.gov', 443, 0, 0, 0))
            sonuc['kanca'].append('izin')
        except PermissionError:
            sonuc['kanca'].append('ret')
    kod = [x for x in d1['durmalar'] if x['tur'] == 'kod']
    R.sina(g, 'prova kipinde: baslat "yeni"; ikinci baslat reddedilir', sonuc['baslat'] == 'yeni' and
           sonuc['baslat2'][0], sonuc)
    R.sina(g, 'hata ile durma: durum "hata" + durma kaydı (tur kod, ileti, saat); sayı yazılmaz',
           sonuc['kos_hata'][0] and d1['asamalar']['K1c-negatif']['durum'] == 'hata' and len(kod) == 1 and
           'FileNotFoundError' in kod[0]['neden'] and kod[0]['zaman'] and
           all(set(v) == {'durum', 'zaman', 'sha256'} for v in d1['asamalar'].values()), d1)
    R.sina(g, 'durmadan sonra: kos reddedilir; baslat --surdur olmadan ve elle kayıtsız reddedilir',
           sonuc['kos_tekrar'][0] and sonuc['baslat_surdursuz'][0] and sonuc['baslat_elle_yok'][0], sonuc)
    R.sina(g, 'durdu (CLI) + baslat --surdur → "surdur"; kod baslattan sonra değişince kos reddedilir',
           sonuc['main_durdu'] == 0 and sonuc['surdur'] == 'surdur' and sonuc['kod_degisti'][0], sonuc)
    R.sina(g, 'prova: GercekOrtam 127.0.0.1 tabanı, prova dizinleri, git doğrulaması yok', sonuc['ortam'])
    R.sina(g, 'prova kancası: vekil portu, dış adres, dış ad çözümü ret; yalnız provanın (127.0.0.1, port) çifti izinli',
           sonuc['kanca'] == ['ret', 'ret', 'izin', 'ret'], sonuc['kanca'])
    R.sina(g, 'prova kapanınca kapı yeniden kapalı', KM._PROVA is None and
           beklenen_hata(lambda: KM.gercek_kapi('x'), KM.GercekKipReddedildi)[0])
    # düğme gerçek kipte kapalı: koşu dondurulmuş (geçici kopya) ön kayıtla prova açılmaz; geçersiz ayar reddedilir
    metin = open(KM.ONKAYIT, encoding='utf-8').read()
    ac = metin.replace('Durum: KARAR METNİ DONDURULDU', 'Durum: KOŞU DONDURULDU; KARAR METNİ DONDURULDU', 1) + \
        '\n' + '\n'.join(KM.kod_sha().values()) + '\n'
    yk = os.path.join(kok, 'onkayit_kopya.md')
    open(yk, 'w', encoding='utf-8').write(ac)

    def ac_dene(pr_, onk=None):
        def f():
            with KM.prova_ac(pr_, onkayit=onk):
                pass
        return beklenen_hata(f, KM.GercekKipReddedildi)[0]
    R.sina(g, 'düğme gerçek kipte kapalı: kapı açıkken (geçici kopya) prova açılmaz', KM.kosu_dondurulmus_mu(yk)[0] and
           ac_dene(pr, yk) and KM._PROVA is None)
    R.sina(g, 'prova reddedilir: 127.0.0.1 dışı taban, https, çıktı kosu/, zarf gerçek kök, depo içi dizin',
           ac_dene(KM.Prova(pr.dizin, pr.zarf, dict(pr.servis, ncedc='http://service.ncedc.org/fdsnws'), pr.katalog))
           and ac_dene(KM.Prova(pr.dizin, pr.zarf, dict(pr.servis, ncedc='http://service.ncedc.org:80/fdsnws'),
                                pr.katalog))   # portlu dış ad da reddedilir (mutasyon "taban URL 127.0.0.1 denetimi yok")
           and ac_dene(KM.Prova(pr.dizin, pr.zarf, pr.servis, dict(pr.katalog, comcat='http://10.0.0.1:8080/q')))
           and ac_dene(KM.Prova(pr.dizin, pr.zarf, pr.servis, dict(pr.katalog, comcat='https://127.0.0.1:9/q')))
           and ac_dene(KM.Prova(KM.CIKTI, pr.zarf, pr.servis, pr.katalog))
           and ac_dene(KM.Prova(pr.dizin, KM.ZARF_KOK, pr.servis, pr.katalog))
           and ac_dene(KM.Prova(os.path.join(KM.DEPO, 'x'), pr.zarf, pr.servis, pr.katalog)))
    # Gerçek kökler bugün /mnt altında, /mnt denetimi onları zaten yakalar; gerçek kök denetimini ayrıca sınamak için
    # depo ve /mnt dışında geçici bir "gerçek kök" tanımlanır (mutasyon "prova dizini gerçek kök olabilir").
    sahte_kok = os.path.join(kok, 'gercek_kok')
    eski_kokler = KM.GERCEK_KOKLER
    try:
        KM.GERCEK_KOKLER = tuple(eski_kokler) + (sahte_kok,)
        kok_ret = (ac_dene(KM.Prova(os.path.join(sahte_kok, 'c'), pr.zarf, pr.servis, pr.katalog))
                   and ac_dene(KM.Prova(pr.dizin, sahte_kok, pr.servis, pr.katalog)))
    finally:
        KM.GERCEK_KOKLER = eski_kokler
    R.sina(g, 'prova reddedilir: /mnt dışında olsa da gerçek kök (ya da altı) prova dizini olamaz', kok_ret)
    R.sina(g, 'protokol ve prova sınamalarında ağ / gerçek veri girişimi yok', len(ENGELLENEN) == once,
           ENGELLENEN[once:])
    shutil.rmtree(kok, ignore_errors=True)


def sha_kilit(KM, R):
    g = 'sha/kilit'
    d = os.path.join(GECICI, 'sha')
    os.makedirs(d, exist_ok=True)
    kop = os.path.join(d, 'tr7b_yapay2.py')
    shutil.copy(os.path.join(KM.TR7B, 'tr7b_yapay2.py'), kop)
    with open(kop, 'a') as f:
        f.write('\n# değişti\n')
    dos = dict(KM.D2_DOSYALAR)
    dos[kop] = dos.pop(os.path.join(KM.TR7B, 'tr7b_yapay2.py'))
    r, msg = beklenen_hata(lambda: KM.d2_denetle(dos), KM.Tr7cDur, 'sha256 uyuşmuyor')
    R.sina(g, 'D-2: değişmiş tr7b_yapay2.py → durur', r, msg)
    R.sina(g, 'D-2: özgün dosyalar geçer', KM.d2_denetle() == KM.D2_SONUC)
    orj = dict(KM.GIRDI)
    try:
        g2 = dict(orj)
        g2[kop] = g2.pop(os.path.join(KM.BURA, 'tr7c_mde_ek.json'))
        KM.GIRDI.clear()
        KM.GIRDI.update(g2)
        r, msg = beklenen_hata(KM.girdi_denetimi, KM.Tr7cDur, 'uyuşmuyor')
    finally:
        KM.GIRDI.clear()
        KM.GIRDI.update(orj)
    R.sina(g, 'girdi sha256 uyuşmazlığı → durur', r, msg)
    R.sina(g, 'gerçek girdiler geçer', len(KM.girdi_denetimi()) == len(KM.GIRDI))
    # kilit
    kay = YapayKaynak(KM, sen_veri_yok)
    h1, dz = kos(KM, kay, 'kilit')
    n1 = kay.sayac['pencere']
    kay.sayac['pencere'] = 0
    msj = []
    h2 = KM.k1c_kos(kay, dizin=dz, ayar=KM.Ayar(mod_n=100), gunluk=msj.append)
    R.sina(g, 'kilit: hüküm dosyası varken ikinci koşu hiçbir şey hesaplamaz', kay.sayac['pencere'] == 0 and n1 > 0 and
           h2['dal'] == h1['dal'] and any('KİLİT' in m for m in msj), dict(n1=n1, msj=msj))
    r, msg = beklenen_hata(lambda: KM.json_yaz(os.path.join(dz, KM.HUKUM_AD), {}, kip='x'), FileExistsError)
    R.sina(g, 'hüküm dosyası "x" kipinde: üzerine yazılamaz', r, msg)
    du = json.load(open(os.path.join(dz, KM.DURUM_AD)))
    R.sina(g, 'Ö-b: durum dosyası yalnız durum, zaman, sha256', all(set(v) == {'durum', 'zaman', 'sha256'}
                                                                    for v in du['asamalar'].values()), du)


def d2_altsurec(R):
    """D-2'nin modül yüklenirken (hesaptan önce) işlediği: geçici bir ağaçta değişmiş tr7b_yapay2.py ile içe aktarma."""
    g = 'sha/kilit'
    kok = os.path.join(GECICI, 'agac')
    if os.path.exists(kok):
        shutil.rmtree(kok)
    for alt in ('tr7', 'tr7b', 'tr7c'):
        os.makedirs(os.path.join(kok, 'kayit', 'turetme', alt))
    dep = os.path.dirname(BURA)
    for alt, ad in (('tr7', 'tr7_cekirdek.py'), ('tr7b', 'tr7b_yapay.py'), ('tr7b', 'tr7b_yapay2.py'),
                    ('tr7c', 'tr7c_kosu.py')):
        shutil.copy(os.path.join(dep, alt, ad), os.path.join(kok, 'kayit', 'turetme', alt, ad))
    with open(os.path.join(kok, 'kayit', 'turetme', 'tr7b', 'tr7b_yapay2.py'), 'a') as f:
        f.write('\n')
    p = subprocess.run([sys.executable, '-I', '-B', '-c',
                        'import sys; sys.path.insert(0, sys.argv[1]); import tr7c_kosu',
                        os.path.join(kok, 'kayit', 'turetme', 'tr7c')], capture_output=True, text=True, timeout=120)
    R.sina(g, 'D-2: değişmiş dosyayla modül yüklenmez (alt süreç)', p.returncode != 0 and 'D-2: sha256 uyuşmuyor' in
           p.stderr, p.stderr[-300:])
    p = subprocess.run([sys.executable, '-I', '-B', KOSU_YOL, 'kos', 'manifest'], capture_output=True, text=True,
                       timeout=120, cwd=os.path.dirname(os.path.dirname(os.path.dirname(BURA))))
    R.sina(g, 'komut satırı: kos manifest → GERÇEK KİP REDDEDİLDİ (alt süreç)',
           p.returncode != 0 and 'GERÇEK KİP REDDEDİLDİ' in (p.stderr + p.stdout), (p.stderr + p.stdout)[-300:])
    shutil.rmtree(kok)


# ================================================================ UÇTAN UCA
def uctan_uca(KM, R, ozet):
    g = 'uçtan uca'
    S = {}

    def kosu(ad, kaynak):
        t = time.time()
        h, d = kos(KM, kaynak, ad)
        S[ad] = dict(dal=h['dal'], alt=h['alt'], n_P=h['n_P'], n_N=h['n_N'], X_P=h['X_P'], X_N=h['X_N'], f_PK=h['f_PK'],
                     N_PK=h['N_PK'], M_olc=h['M_olc'], M_mod=h['M_mod'], A90_PK=h['A90_PK'], etiket=h['etiket'],
                     cumle=h['cumle'], marmara=h['marmara_acilir'], VAR=h['var_verilebilir'],
                     sure_s=round(time.time() - t, 1))
        return h, d
    h, d = kosu('gercek_tremor', YapayKaynak(KM, sen_gercek()))
    R.sina(g, 'gerçek tremor (8/10 P, kilitli) → (b) "ölçü sınandı", Marmara açılır, VAR verilebilir',
           h['dal'] == 'b' and h['cumle'].startswith('ölçü sınandı;') and h['marmara_acilir'] and h['var_verilebilir'],
           S['gercek_tremor'])
    sira = [r['sinif'] for r in KM.jsonl_oku(os.path.join(d, 'tr7c_algilama.jsonl'))]
    R.sina(g, 'algılama sırası: önce bütün N, sonra P, sonra bilgi', sira == sorted(sira, key='NPB'.index) and
           sira.count('N') == 29 and sira.count('P') == 10, ''.join(sira))
    R.sina(g, 'hüküm dosyası tek ve tohumlar yazılı', os.path.exists(os.path.join(d, KM.HUKUM_AD)) and
           h['tohum'] == dict(modulasyon=20261115, mda=20261114, negatif_secim=20261117))
    # aynı kaynakla ikinci koşu: belirlenimci
    h2, _ = kos(KM, YapayKaynak(KM, sen_gercek()), 'gercek_tremor_2')
    R.sina(g, 'belirlenimci: aynı veriyle ikinci koşu aynı M, p, dal',
           json.dumps(h2['modulasyon'], sort_keys=True) == json.dumps(h['modulasyon'], sort_keys=True) and
           h2['dal'] == h['dal'])
    h, _ = kosu('ayirt_etmeyen', YapayKaynak(KM, sen_ayirt_etmeyen))
    R.sina(g, 'ayırt etmeyen algılayıcı (P ve N\'de aynı tremor) → (c) "sınanamadı", kalan (iii), Marmara kapalı',
           h['dal'] == 'c' and '(iii)' in (h['alt'] or '') and 'ayıramadı' in h['cumle'] and not h['marmara_acilir'],
           S['ayirt_etmeyen'])
    h, d3 = kosu('genlik_sizinti', YapayKaynak(KM, sen_genlik_sizinti))
    R.sina(g, 'genliğe bağlı, kilitsiz 2–8 Hz sızıntı (K5\'ten geçer) → (iv) sağlanmaz, (b) değil, Marmara kapalı',
           h['dal'] != 'b' and not h['z3']['iv'] and not h['marmara_acilir'], S['genlik_sizinti'])
    for ad_, dz in (('genlik_sizinti', d3),):
        al = KM.jsonl_oku(os.path.join(dz, 'tr7c_algilama.jsonl'))
        ozet[ad_] = dict(kume=sum(r.get('kume_sayisi') or 0 for r in al),
                         K5_atilan=sum((r.get('ayiklanan') or {}).get('sizinti_K5', 0) for r in al),
                         algilama=sum(bool(r.get('algilama')) for r in al))
    h, d4 = kosu('tele_sizinti_K5', YapayKaynak(KM, sen_tele_sizinti))
    al = KM.jsonl_oku(os.path.join(d4, 'tr7c_algilama.jsonl'))
    ozet['tele_sizinti_K5'] = dict(kume=sum(r.get('kume_sayisi') or 0 for r in al),
                                   K5_atilan=sum((r.get('ayiklanan') or {}).get('sizinti_K5', 0) for r in al),
                                   algilama=sum(bool(r.get('algilama')) for r in al))
    R.sina(g, 'telesismik koda sızıntısı (TR-7b Y2 sabit, a_y ∝ PGV_T) → K5 atar, (b) değil, Marmara kapalı',
           h['dal'] != 'b' and not h['marmara_acilir'] and ozet['tele_sizinti_K5']['K5_atilan'] >= 30,
           dict(S['tele_sizinti_K5'], kume=ozet['tele_sizinti_K5']))
    h, _ = kosu('veri_yok', YapayKaynak(KM, sen_veri_yok))
    R.sina(g, 'veri yok → (a) "ölçü sınanamadı (Parkfield verisi yok)"', h['dal'] == 'a' and h['n_P'] == 0 and
           h['cumle'].startswith('ölçü sınanamadı (Parkfield verisi yok)') and not h['marmara_acilir'], S['veri_yok'])
    g4 = '200708152340'
    h, _ = kosu('D9_etiket', YapayKaynak(KM, sen_gercek(genlik_N=(g4,))))
    R.sina(g, 'D-9: Peru 2007 (N) modülasyonlu → (b) + "genlik karıştırıcısı dışlanmadı", VAR verilemez',
           h['dal'] == 'b' and h['etiket']['genlik'] and 'genlik karıştırıcısı dışlanmadı' in h['cumle'] and
           h['marmara_acilir'] and not h['var_verilebilir'], S['D9_etiket'])
    # E-2: başvuru kanalı 6 P'de yok → k_koşu 4; 9 P'de yok → k 1 → (e) modülasyon ölçülemedi
    P = list(T0.P_OLAY)
    h, _ = kosu('E2_k4', YapayKaynak(KM, sen_gercek(), ref_yok=P[:6]))
    dd = KM.k1c_dal(h['n_P'], h['n_N'], h['X_P'], h['X_N'], h['f_PK'], h['N_PK'], h['M_olc'], h['M_mod'], h['A90_PK'])
    R.sina(g, 'E-2: k_koşu 4 → koşu sürer, n_P aynı, dal Z4 ile, güç bilgisi yazılır',
           h['etiket']['k_kosu'] == 4 and h['n_P'] == 10 and (h['dal'], h['alt']) == dd[:2] and 'koşuda 4' in h['cumle']
           and 'k_koşu ile güç' in h['cumle'], S['E2_k4'])
    h, _ = kosu('E2_k1', YapayKaynak(KM, sen_gercek(), ref_yok=P[:9]))
    R.sina(g, 'E-2: k_koşu 1 → (e) "modülasyon ölçülemedi" (D-7: (i), (ii) var)',
           h['dal'] == 'e' and h['alt'] == 'modülasyon ölçülemedi' and h['etiket']['k_kosu'] == 1, S['E2_k1'])
    h, _ = kosu('b_prime', YapayKaynak(KM, sen_gercek(), bprime=True))
    R.sina(g, '(b′): bütün algılama kümeleri çekirdek fazında → "geçti, belirsiz", VAR verilemez',
           h['dal'] == 'b' and h['etiket']['b_prime'] and 'geçti, belirsiz' in h['cumle'] and not h['var_verilebilir'],
           S['b_prime'])
    h, _ = kosu('b_prime_kismi', YapayKaynak(KM, sen_gercek(), bprime=set(P[:3])))
    R.sina(g, '(b′) yalnız 3 P olayında → etiket yok (hepsi şartı), VAR verilebilir',
           h['dal'] == 'b' and not h['etiket']['b_prime'] and h['var_verilebilir'], S['b_prime_kismi'])
    h, _ = kosu('modulasyonsuz', YapayKaynak(KM, lambda s, b: dict(sen_gercek()(s, b), kilitli=False)
                                             if s == 'P' else sen_gercek()(s, b)))
    R.sina(g, 'kilitsiz tremor (P\'de) → (c) kalan (iv) ya da (b)+D-10 değil: (iv) sağlanmaz',
           h['dal'] == 'c' and h['alt'] == '(iv)', S['modulasyonsuz'])
    # negatif turunun sürdürülmesi: yarıda kesilen jsonl'dan aynı sonuç
    kay = YapayKaynak(KM, sen_gercek())
    d1 = os.path.join(GECICI, 'e2e', f'surdur_a_{time.time_ns()}')
    d2 = os.path.join(GECICI, 'e2e', f'surdur_b_{time.time_ns()}')
    os.makedirs(d1)
    os.makedirs(d2)
    a = KM.negatif_turu(kay, d1, KM.Ayar(mod_n=100))
    sat = open(os.path.join(d1, 'tr7c_negatif.jsonl')).read().splitlines(True)
    open(os.path.join(d2, 'tr7c_negatif.jsonl'), 'w').writelines(sat[:5])
    b = KM.negatif_turu(kay, d2, KM.Ayar(mod_n=100))
    R.sina(g, 'negatif turu sürdürülebilir: 5 satırdan sonra devam aynı MDA çekilişlerini verir',
           json.dumps(a, sort_keys=True, default=str) == json.dumps(b, sort_keys=True, default=str))
    return S


# ================================================================ MUTASYONLAR
MUTASYONLAR = [
    # §B.4 aşama protokolü ve §B.3 kuru prova düğmesi (kod incelemesinden sonra eklendi)
    ('önkoşul: önceki aşama denetimi yok',
     "    if i > 0 and a.get(ASAMALAR[i - 1], {}).get('durum') != 'tamamlandı':\n        raise Tr7cDur(f'önceki aşama",
     "    if False:\n        raise Tr7cDur(f'önceki aşama"),
    ('önkoşul: tamamlanmış aşama yeniden başlatılabilir', "    if mevcut.get('durum') == 'tamamlandı':\n        raise",
     "    if False:\n        raise"),
    ('önkoşul: algılama aşamasına --surdur olmadan yeniden girilir',
     "    if asama in ALGILAMA_ASAMALARI and not surdur:\n        raise", "    if False:\n        raise"),
    ('sürdürme: koşu kodunun durma kaydı yeter (elle şartı yok)', "x.get('tur') == 'elle' and ", ""),
    ('hata ile durmada durma kaydı yazılmaz', "        durma_yaz(dz, asama, neden, 'kod')\n", ""),
    ('kod baslattan sonra değişse de koşar',
     "    if (a.get('sha256') or {}).get('tr7c_kosu.py') != sha256_dosya(os.path.abspath(__file__)):",
     "    if False:"),
    ('prova düğmesi kapı açıkken de açılır',
     "    if ok:\n        raise GercekKipReddedildi('PROVA REDDEDİLDİ: koşu dondurulmuş",
     "    if False:\n        raise GercekKipReddedildi('PROVA REDDEDİLDİ: koşu dondurulmuş"),
    ('prova kancası portu denetlemez (vekil 127.0.0.1\'de)', "(a[0], a[1]) in izin)", "a[0] == '127.0.0.1')"),
    ('prova taban URL 127.0.0.1 denetimi yok', "x.hostname != '127.0.0.1' or ", ""),
    ('prova dizini gerçek kök olabilir', "if gercek_yol_mu(y) or not I.depo_disi", "if not I.depo_disi"),
    ('prova bağlamı kapanınca düğme açık kalır', "    finally:\n        _PROVA = None", "    finally:\n        pass"),
    ('Fisher yönü ters (alt kuyruk)', 'for x in range(xp, min(k, n) + 1)) / den', 'for x in range(0, xp + 1)) / den'),
    ('(iv) "≥ 3" yerine "≥ 1"', 'MOD_P_MIN = 3 ', 'MOD_P_MIN = 1 '),
    ('dal (a) eşiği n_N < 2', 'N_P_MIN, N_N_MIN = 8, 20', 'N_P_MIN, N_N_MIN = 8, 2'),
    ('(b) dışında Marmara (c de açar)', "    return dal == 'b'\n", "    return dal in ('b', 'c')\n"),
    ('Vanuatu iki kez sayılır (D-1 kalkar)', 'BIRLESIK_BIRIMLER = {VANUATU_BIRIM: VANUATU}', 'BIRLESIK_BIRIMLER = {}'),
    ('D-7 okuma kuralı kaldırılır', '    return (not a) and i and ii', '    return not a'),
    ('D-9 etiketi VAR\'ı engellemez', "and etiket['mod_gecti'] and not etiket['genlik']", "and etiket['mod_gecti']"),
    ('K5 yerine TR-7 K0', 'return bool(Y2.K5(x, parcalar, maske, Q))', 'return bool(K.sizinti_ist(x, parcalar, maske))'),
    ('K5 hiç bayraklamaz', 'return bool(Y2.K5(x, parcalar, maske, Q))', 'return False'),
    ('K1b bir saniye kayık (kapsayıcı uç dışlayıcı)', 'return Ip[0] < ara[1] + 1 and Ip[1] > ara[0]',
     'return Ip[0] < ara[1] and Ip[1] > ara[0]'),
    ('E-1 önce BH', "(0 if c['kod'][0] == 'H' else 1,", "(0 if c['kod'][0] == 'B' else 1,"),
    ('E-1 en uzak istasyon', 'uygun.sort(key=lambda x: (x[0], x[1]))', 'uygun.sort(key=lambda x: (-x[0], x[1]))'),
    ('E-1 örtü şartı yok', "and c['uygun_yanit'] and c['ortu_ok'] and", "and c['uygun_yanit'] and"),
    ('kod sha256 denetimi atlanır', "eksik = [k for k, v in kod_sha().items() if v not in metin]", 'eksik = []'),
    ('karar metni gövde denetimi atlanır', 'if g != KARAR_GOVDE_SHA:', 'if False:'),
    ('kilit atlanır', "    if os.path.exists(hy):\n        gunluk('KİLİT", "    if False:\n        gunluk('KİLİT"),
    ('kapı tümden açık', "    if not ok:\n        raise GercekKipReddedildi(f'GERÇEK KİP REDDEDİLDİ ({islem})",
     "    if False:\n        raise GercekKipReddedildi(f'GERÇEK KİP REDDEDİLDİ ({islem})"),
    ('GercekOrtam kapısı yok', "        gercek_kapi('GercekOrtam')\n", '        pass\n'),
    ('k1c_kos kapısı yok', "        gercek_kapi('k1c_kos')\n", '        pass\n'),
    ('asama_kos kapısı yok', "    gercek_kapi(f'aşama {asama}')\n", '    pass\n'),
    ('D-2 karşılaştırması yok', '        if s != beklenen:\n            raise Tr7cDur(f\'D-2',
     '        if False:\n            raise Tr7cDur(f\'D-2'),
    ('modülasyon eşiği 0,05', "any(k['p'] is not None and k['p'] <= K.MOD_ESIK for k in ks)",
     "any(k['p'] is not None and k['p'] <= 0.05 for k in ks)"),
    ('X_min yok sayılır', 'i = xm is not None and X_P >= max(math.ceil(n_P / 2), xm)',
     'i = X_P >= math.ceil(n_P / 2)'),
    ('N_PK < 5 kuralı yok', 'ii = N_PK >= N_PK_MIN and f_PK / N_PK <= FAR_TAVAN',
     'ii = N_PK > 0 and f_PK / N_PK <= FAR_TAVAN'),
    ('ŝ ham X_P/n_P', '    return max(0.0, (X_P / n_P - q) / (1 - q))', '    return X_P / n_P'),
    ('D-10 yazılmaz', "c = 'ölçü sınandı' if etiket['mod_gecti'] else", "c = 'ölçü sınandı' if True else"),
    ('(b′) yazılmaz', "        if etiket['b_prime']:\n            c += '; geçti, belirsiz",
     "        if False:\n            c += '; geçti, belirsiz"),
    ('D-8 eki yok', "f' (kalan: {alt})' + d8_eki(n_P, n_N))", "f' (kalan: {alt})')"),
    ('E-2 güç satırı yok', "and etiket['k_kosu'] < K_USTVERI:", "and etiket['k_kosu'] < 0:"),
    ('modülasyon tohumu farklı', 'MOD_TOHUM_PK = 20261112 + 3', 'MOD_TOHUM_PK = 20261112 + 4'),
    ('algılama sırası önce P', "sira = {'N': 0, 'P': 1, 'B': 2, 'Nayri': 3}", "sira = {'N': 1, 'P': 0, 'B': 2, 'Nayri': 3}"),
    ('ölçülebilir olay: ref yeterli (M aranmaz)', "return any(k['M'] is not None for k in ks),",
     "return mod.get(bid, {}).get('ref') is not None,"),
    ('D-9 ölçülemeyen olay etiketi tetikler', "genlik = any(olc(b['id'])[1] for b in g4 if tar[b['id']])",
     "genlik = any(olc(b['id'])[1] or not olc(b['id'])[0] for b in g4 if tar[b['id']])"),
    ('(b′) tek olay yeter (hepsi yerine)', "b_prime = bool(alg_P) and all(bp_olay)", "b_prime = any(bp_olay)"),
]


def suite(KM, tam_izgara, uc=True, ozet=None):
    R = Kayit()
    for adim in (lambda: birim(KM, R, tam_izgara), lambda: kapi(KM, R), lambda: protokol(KM, R),
                 lambda: sha_kilit(KM, R)):
        try:
            adim()
        except BaseException as e:   # noqa: BLE001
            R.sina('çöküş', f'{type(e).__name__}: {str(e)[:200]}', False)
    S = None
    if uc:
        try:
            S = uctan_uca(KM, R, {} if ozet is None else ozet)
        except BaseException as e:   # noqa: BLE001
            R.sina('çöküş', f'uçtan uca {type(e).__name__}: {str(e)[:200]}', False)
    return R, S


def main():
    cikti = sys.argv[1]
    hizli = '--hizli' in sys.argv
    os.makedirs(GECICI, exist_ok=True)
    t0 = time.time()
    ozet = {}
    R, S = suite(T0, tam_izgara=True, ozet=ozet)
    d2_altsurec(R)
    sure_ana = round(time.time() - t0, 1)
    for x in R.s:
        print(('GEÇTİ ' if x['gecti'] else 'KALDI ') + f"[{x['grup']}] {x['ad']}", flush=True)
        if not x['gecti']:
            print('   ', json.dumps(x['ayrinti'], ensure_ascii=False, default=str)[:1500], flush=True)
    mut = []
    if not hizli:
        kaynak = open(KOSU_YOL, encoding='utf-8').read()
        for i, (ad, eski, yeni) in enumerate(MUTASYONLAR):
            if kaynak.count(eski) != 1:
                mut.append(dict(ad=ad, durum=f'uygulanamadı (bulunma sayısı {kaynak.count(eski)})', yakalandi=False))
                print('MUTASYON UYGULANAMADI', ad, flush=True)
                continue
            t = time.time()
            try:
                KM = modul_yukle(kaynak.replace(eski, yeni), f'tr7c_kosu_mut{i}')
                Rm, _ = suite(KM, tam_izgara=False)
                kalan = [f"[{x['grup']}] {x['ad']}" for x in Rm.kalan()]
            except BaseException as e:   # noqa: BLE001
                kalan = [f'yükleme/çöküş: {type(e).__name__}: {str(e)[:150]}']
            mut.append(dict(ad=ad, yakalandi=bool(kalan), yakalayan=kalan[:6], n_yakalayan=len(kalan),
                            sure_s=round(time.time() - t, 1)))
            print(('YAKALANDI ' if kalan else 'YAKALANMADI ') + ad, kalan[:3], flush=True)
    grup = {}
    for x in R.s:
        grup.setdefault(x['grup'], [0, 0])
        grup[x['grup']][0] += 1
        grup[x['grup']][1] += x['gecti']
    out = dict(
        aciklama='TR-7c koşu kodunun yalnız yapay veride sınaması (§10 adım 2). Gerçek dalga formu, zarf ya da ağ yok; '
                 'denetim kancası bütün soket ve /mnt/project-files açma girişimlerini reddeder.',
        kod_sha256={'tr7c_kosu.py': T0.sha256_dosya(KOSU_YOL),
                    'tr7c_test_yapay.py': T0.sha256_dosya(os.path.abspath(__file__))},
        sinama=dict(toplam=len(R.s), gecen=sum(x['gecti'] for x in R.s), gruplar=grup,
                    kalanlar=[dict(grup=x['grup'], ad=x['ad'], ayrinti=x['ayrinti']) for x in R.kalan()]),
        sinamalar=[dict(grup=x['grup'], ad=x['ad'], gecti=x['gecti']) for x in R.s],
        izgara=next((x['ayrinti'] for x in R.s if x['ad'].startswith('Z4+D-7 ızgarası')), None),
        uctan_uca=S, sizinti_kumeleri=ozet,
        mutasyon=dict(toplam=len(mut), yakalanan=sum(m['yakalandi'] for m in mut), liste=mut),
        engellenen_giris=ENGELLENEN, sure_s=dict(ana=sure_ana, toplam=round(time.time() - t0, 1)))
    with open(cikti, 'w', encoding='utf-8') as f:
        f.write(json.dumps(out, ensure_ascii=False, indent=1, default=str) + '\n')
    print(json.dumps(dict(sinama=out['sinama']['gruplar'], mutasyon=[out['mutasyon']['toplam'],
                                                                     out['mutasyon']['yakalanan']],
                          sure=out['sure_s']), ensure_ascii=False))


if __name__ == '__main__':
    main()
