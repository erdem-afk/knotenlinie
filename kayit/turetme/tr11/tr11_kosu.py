#!/usr/bin/env python3
"""TR-11 tek koşu: GNSS 2 yıllık hız değişiminin depremsiz küme-pencerelerindeki taban dağılımı.

Bağlayıcı metinler (çelişkide bu sırayla): `kayit/onkayit/TR-11_INCELEME-1.md` "Düzeltme metni" blokları (E1, E2,
E3, Ö1–Ö5, K1, K2, K4, K6), `TR-11_gnss-taban-dagilimi_ONKAYIT.md`, `TR-11_SAYIM.md` §2, §4, §5. Küme-pencere listesi
`tr11_kume_listesi.json` (sha256 79f6cf0f…27cbbd) hepsinin üstündedir; bu betik kümeleri yeniden kurmaz.

Sıra (ön kayıt §3, INCELEME-1 E2 madde 7):
  0. girdi denetimi (liste sha256, üstveri sha256, Marmara kutusu, indirme manifesti, %5 indirme hatası kuralı)
  1. veri kapısı (doluluk, indirme hatası, rank; geçerli yer >= 100 ve blok >= 30)
  2. kod denetimi (i) ve (ii-b), yalnız yapay N0 serilerinde (gerçek gün maskeleriyle)
  3. kod denetimi (ii-a), gerçek veride istasyon düzeyinde (S hesaplanmaz)
  4. ancak bunlar geçerse gerçek S, ana ölçü, kırılımlar, bilgi satırları, Marmara çevirisi
Gerçek S değerleri 4. adımdan önce hesaplanmaz ve hiçbir yere yazılmaz. Sonuç önce bellekte üretilir, sonra
`tr11_sonuc.json` ve `tr11_sonuc.md` "x" kipinde (yalnız yoksa) yazılır. Çıktı varsa koşu başlamaz.

Kullanım (tek komut):
  python3 -I -B tr11_kosu.py --tenv3 <indirme_dizini> --manifest <indirme_dizini>/tr11_indirme_manifest.json \
      --ustveri /mnt/project-files/turetme/tr11-ustveri --tr2 <tr2/ham> [--cikti kayit/turetme/tr11]
  --yalniz-denetim: yalnız 0. adımı koşar (hiçbir tenv3 okunmaz), sayıları yazar.
"""
import os
for _v in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
import argparse, collections, csv, dataclasses, datetime as dt, hashlib, json, math, sys, time
import multiprocessing as mp
import numpy as np

# ===================================================================== önceden sabit değerler (bağlayıcı)
LISTE_SHA256 = '79f6cf0f9a1a11d932617b20c7b866bb5125a3acea62d35325af9364f027cbbd'
USTVERI_SHA16 = {'DataHoldings.txt': '4a98b65ad74c425b', 'steps.txt': '887501a438c41c34'}
TR2_SHA16 = {'m6_havuz.csv': '969c5c54851ee353', 'birincil_aday.csv': 'f905535cf0837dbb',
             'birincil_aday_fm.csv': '8c9cae2206b35c11', 'mekanizma.jsonl': 'eb30828a7a1fff17'}
Y = 365.25
def gun(y): return int(math.floor(y * Y))
N_PEN, N_YAK = gun(5), gun(2)              # 1826, 730
N_TAB = N_PEN - N_YAK                      # 1096
DT = 1.0 / Y
SW, BF0, BRW_N1 = 1.5, 3.0, 1.0            # N0: beyaz 1,5 mm, kırpışma 3 mm/yıl^0,25; N1: + RW 1 mm/yıl^0,5
TOHUM = 20261111
SINYAL = 3.0                               # mm/yıl, doğu
DOLULUK = 0.60
MAD_K = 5 * 1.4826
MARMARA = (39.5, 42.0, 26.0, 31.5)
O4_KM = 150.0
SON = dt.date(2026, 1, 1)
MJD_KOK = dt.date(1858, 11, 17).toordinal()
QS = (0.5, 0.9, 0.95, 0.99)
KAPI_YER, KAPI_BLOK = 100, 30
SINIF_YER_MIN = 30
Q99_KP_MIN = 300
CEVIRI_KP_MIN = 300
ORAN_ARALIK = (0.9, 1.1)
D_E_ARALIK = (2.95, 3.05)
D_N_UST = 0.05
IIB_ARALIK = (0.9, 1.1)
INDIRME_HATA_PAY = 0.05
G_D = (5.0, 10.0, 15.0)
G_X = (5.0, 10.0, 20.0, 30.0, 50.0)
G_MR = (('dengeli', 0.0), ('ayni_yan', math.pi / 2), ('karsi_yan', -math.pi / 2))
O3_ESIK, C_ESIK = 10.0, 5.0
BIRIM_YER_AGIRLIK = 60                     # yer ağırlığı 1/n_epok -> tam sayı 60/n_epok (n_epok 1..5)


@dataclasses.dataclass
class Ayar:
    """Koşu ayarı. Komut satırı her zaman varsayılanı (bağlayıcı değerler) kullanır; testler küçültebilir."""
    liste_sha256: str = LISTE_SHA256
    ustveri_sha16: dict = dataclasses.field(default_factory=lambda: dict(USTVERI_SHA16))
    tr2_sha16: dict = dataclasses.field(default_factory=lambda: dict(TR2_SHA16))
    M: int = 2000
    B: int = 2000
    surec: int = 4
    bf_izgara_n: int = 121

    def bagli_mi(self):
        return self == Ayar(surec=self.surec)


def mjd(d): return d.toordinal() - MJD_KOK
def mjd_tarih(m): return dt.date.fromordinal(int(m) + MJD_KOK)
def sar(lo): return (lo + 180) % 360 - 180


def pencere(T):
    """T (date) -> (MJD(w0), MJD(H), MJD(w1)); W = [T - 1826 g, T - 1 g], H = T - 730 g."""
    t = mjd(T)
    return t - N_PEN, t - N_YAK, t - 1


def sha256_dosya(yol):
    h = hashlib.sha256()
    with open(yol, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def hav(la1, lo1, la2, lo2):
    """haversine, derece girdisi, R = 6371 km; dizi uyumlu."""
    la1, lo1, la2, lo2 = map(np.radians, (la1, lo1, la2, lo2))
    a = np.sin((la2 - la1) / 2) ** 2 + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def marmara_icinde(la, lo):
    return MARMARA[0] <= la <= MARMARA[1] and MARMARA[2] <= lo <= MARMARA[3]


_KUTU_SINIR = None
def marmara_uzaklik(la, lo):
    """Marmara kutusuna en kısa büyük daire uzaklığı (km; içerideyse 0). Kutu kenarı 0,005° adımla örneklenir."""
    global _KUTU_SINIR
    if _KUTU_SINIR is None:
        a, b, c, d = MARMARA
        la_k = np.arange(a, b + 1e-9, 0.005); lo_k = np.arange(c, d + 1e-9, 0.005)
        pla = np.concatenate([la_k, la_k, np.full_like(lo_k, a), np.full_like(lo_k, b)])
        plo = np.concatenate([np.full_like(la_k, c), np.full_like(la_k, d), lo_k, lo_k])
        _KUTU_SINIR = (pla, plo)
    if marmara_icinde(la, lo):
        return 0.0
    return float(hav(la, lo, _KUTU_SINIR[0], _KUTU_SINIR[1]).min())


# ===================================================================== üstveri okuyucular
def dataholdings_oku(yol):
    out = {}
    with open(yol) as f:
        next(f)
        for l in f:
            p = l.split()
            try:
                out[p[0]] = (float(p[1]), sar(float(p[2])))
            except Exception:
                continue
    return out


def steps_tarih(s):
    yy = int(s[:2]); yyyy = 2000 + yy if yy <= 79 else 1900 + yy
    return dt.datetime.strptime(f'{yyyy}{s[2:]}', '%Y%b%d').date()


def steps_kod1_oku(yol):
    """steps.txt kod 1 (ekipman) tarihleri; 2026 ve sonrası atılır (sayım betiğiyle aynı ayrıştırma)."""
    k1 = collections.defaultdict(set)
    with open(yol) as f:
        for l in f:
            p = l.split()
            if len(p) < 3:
                continue
            try:
                t = steps_tarih(p[1])
            except Exception:
                continue
            if t >= SON:
                continue
            if p[2] == '1':
                k1[p[0]].add(t)
    return k1


def pencere_adimlari(k1, sta, T):
    w0, _, w1 = pencere(T)
    return sorted({mjd(t) for t in k1.get(sta, ()) if w0 <= mjd(t) <= w1})


# ---- ortam sınıfı (sayim_ustveri.py ile aynı kod; o betik içe aktarılamıyor)
def _katalog(fn, sadece_deprem=True):
    out = []
    with open(fn) as f:
        for r in csv.DictReader(f):
            t = dt.date.fromisoformat(r['time'][:10])
            if t >= SON:
                continue
            if sadece_deprem and r.get('type', 'earthquake') != 'earthquake':
                continue
            out.append(dict(id=r['id'], T=t, la=float(r['latitude']), lo=sar(float(r['longitude'])),
                            M=float(r['mag']), z=float(r['depth'] or 0)))
    return out


def _rake_sec(rec):
    for k in ('mt', 'fm'):
        L = [x for x in rec.get(k, []) if 'nodal-plane-1-rake' in x or 'nodal-plane-1-slip' in x]
        if L:
            x = max(L, key=lambda q: q.get('_w', 0))
            return float(x.get('nodal-plane-1-rake', x.get('nodal-plane-1-slip')))
    return None


class Sinif:
    SINIF_R, SINIF_MIN_MEK = 150.0, 2

    def __init__(self, tr2):
        E6 = _katalog(os.path.join(tr2, 'm6_havuz.csv'))
        self.e6 = (np.array([e['la'] for e in E6]), np.array([e['lo'] for e in E6]))
        konum = {}
        for fn in ('birincil_aday.csv', 'birincil_aday_fm.csv'):
            for e in _katalog(os.path.join(tr2, fn)):
                konum[e['id']] = e
        MEK = []
        with open(os.path.join(tr2, 'mekanizma.jsonl')) as f:
            for s in f:
                if not s.strip():
                    continue
                r = json.loads(s)
                if r.get('hata') or r['id'] not in konum:
                    continue
                rk = _rake_sec(r)
                if rk is None:
                    continue
                rk = sar(rk)
                e = konum[r['id']]
                MEK.append((e['la'], e['lo'], abs(rk) <= 30 or abs(rk) >= 150))
        self.mla = np.array([m[0] for m in MEK]); self.mlo = np.array([m[1] for m in MEK])
        self.mss = np.array([m[2] for m in MEK], bool)

    def __call__(self, la, lo):
        n6 = int((hav(la, lo, self.e6[0], self.e6[1]) <= self.SINIF_R).sum()) if len(self.e6[0]) else 0
        if n6 == 0:
            return 'D'
        m = hav(la, lo, self.mla, self.mlo) <= self.SINIF_R if len(self.mla) else np.zeros(0, bool)
        nm, nss = int(m.sum()), int(self.mss[m].sum())
        if nm >= self.SINIF_MIN_MEK and nss / nm >= 0.5:
            return 'A'
        return 'B'


# ===================================================================== tenv3 biçimi
# NGL README_tenv3.txt (gps_timeseries/readmes/) sütunları; dosya başlığı bu adlarla.
TENV3_BASLIK = ('site YYMMMDD yyyy.yyyy __MJD week d reflon _e0(m) __east(m) ____n0(m) _north(m) u0(m) ____up(m) '
                '_ant(m) sig_e(m) sig_n(m) sig_u(m) __corr_en __corr_eu __corr_nu _latitude(deg) _longitude(deg) '
                '__height(m)')
SUTUN = {3: 'MJD', 7: 'e0(m)', 8: 'east(m)', 9: 'n0(m)', 10: 'north(m)'}
AYLAR = ('JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC')


class Tenv3Hata(Exception):
    pass


def tenv3_ayristir(satirlar, pencereler):
    """tenv3 satırlarını okur; yalnız pencerelerin (MJD [a, b], kapalı) içindeki satırlar tutulur.

    Dosyanın zaman sıralı olduğu varsayılır: MJD en son pencerenin sonundan büyük olan ilk satırda okuma DURUR
    (INCELEME-1 Ö4: w1 sonrası satırlar belleğe alınmaz). Pencere dışındaki satırlar okunduğu anda atılır.
    Aynı MJD birden çok kez varsa dosyadaki ilki alınır. Doğu = _e0 + __east, kuzey = ____n0 + _north, mm.
    Dönüş: ([ (mjd int64, E mm, N mm) her pencere için ], bilgi)."""
    son = max(b for a, b in pencereler)
    kayit = [dict() for _ in pencereler]
    bilgi = dict(bozuk=0, geri=0, tekrar=0, durdu=False, baslik=False)
    onceki = -10 ** 9
    ilk = True
    for line in satirlar:
        p = line.split()
        if not p:
            continue
        if ilk:
            ilk = False
            if p[0] == 'site':
                ad = [x.strip('_') for x in p]
                for j, beklenen in SUTUN.items():
                    if len(ad) <= j or ad[j] != beklenen:
                        raise Tenv3Hata(f'beklenmeyen tenv3 başlığı: sütun {j + 1} {p[j] if len(p) > j else None!r}')
                bilgi['baslik'] = True
                continue
        if len(p) < 11:
            bilgi['bozuk'] += 1
            continue
        try:
            m = int(p[3])
        except ValueError:
            bilgi['bozuk'] += 1
            continue
        if m > son:
            bilgi['durdu'] = True
            break
        if m < onceki:
            bilgi['geri'] += 1
        onceki = max(onceki, m)
        for j, (a, b) in enumerate(pencereler):
            if a <= m <= b:
                if m in kayit[j]:
                    bilgi['tekrar'] += 1
                else:
                    try:
                        kayit[j][m] = (float(p[7]) + float(p[8]), float(p[9]) + float(p[10]))
                    except ValueError:
                        bilgi['bozuk'] += 1
                break
    out = []
    for k in kayit:
        ms = np.array(sorted(k), dtype=np.int64)
        E = np.array([k[m][0] for m in ms], float) * 1000.0
        N = np.array([k[m][1] for m in ms], float) * 1000.0
        out.append((ms, E, N))
    return out, bilgi


_TARIH_ON = {}
def _tarih_alanlari(m):
    r = _TARIH_ON.get(m)
    if r is None:
        d = mjd_tarih(m)
        ny = 366 if (d.year % 4 == 0 and (d.year % 100 != 0 or d.year % 400 == 0)) else 365
        r = (f'{d.year % 100:02d}{AYLAR[d.month - 1]}{d.day:02d}', d.year + (d.timetuple().tm_yday - 0.5) / ny,
             (m - 44244) // 7, (m - 44244) % 7)
        _TARIH_ON[m] = r
    return r


def tenv3_satirlari(sta, mjd_dizi, e_mm, n_mm, u_mm=None, lat=0.0, lon=0.0, hgt=100.0, baslik=True,
                    e0=None, n0=None, reflon=None):
    """NGL tenv3 biçiminde satırlar (README_tenv3 örnek satırının alan genişlikleriyle)."""
    reflon = round(lon, 1) if reflon is None else reflon
    if e0 is None:
        e0 = int(round((lon - reflon) * 111320 * math.cos(math.radians(lat))))
    if n0 is None:
        n0 = int(round(lat * 110950))
    u0 = int(hgt)
    if u_mm is None:
        u_mm = np.zeros(len(mjd_dizi))
    out = [TENV3_BASLIK] if baslik else []
    for m, e, n, u in zip(mjd_dizi, e_mm, n_mm, u_mm):
        ymd, dy, w, dw = _tarih_alanlari(int(m))
        out.append(f'{sta} {ymd} {dy:.4f} {int(m):5d} {w:4d} {dw:1d} {reflon:6.1f} {e0:6d} {e / 1000.0:9.6f} '
                   f'{n0:9d} {n / 1000.0:9.6f} {u0:5d} {(hgt - u0) + u / 1000.0:9.6f} {0.0:6.4f} {0.000902:8.6f} '
                   f'{0.000992:8.6f} {0.004512:8.6f} {0.091352:9.6f} {-0.536983:9.6f} {0.041338:9.6f} '
                   f'{lat:14.10f} {lon:15.10f} {hgt:11.5f}')
    return out


# ===================================================================== menteşe modeli (INCELEME-1 Ö2)
def tasarim(ms, w0, H, adimlar):
    """sabit, eğim, yıllık ve altı aylık sin/cos, kod 1 sıçramaları 1{MJD >= MJD(t_k)}, menteşe (son sütun)."""
    t = (ms - w0) / Y
    tH = (H - w0) / Y
    cols = [np.ones(len(ms)), t, np.sin(2 * np.pi * t), np.cos(2 * np.pi * t), np.sin(4 * np.pi * t),
            np.cos(4 * np.pi * t)]
    for s in adimlar:
        cols.append((ms >= s).astype(float))
    cols.append(np.maximum(0.0, t - tH))
    return np.column_stack(cols)


def _rank_tam(X):
    return X.shape[0] >= X.shape[1] and np.linalg.matrix_rank(X) == X.shape[1]


def olc(ms, E, N, w0, H, adimlar, ek_dogu=0.0):
    """İstasyon ölçüsü: bileşen başına sıradan en küçük kareler, bir kez 5 x 1,4826 x MAD ayıklaması, yeniden uydurma.
    ek_dogu > 0 ise doğuya ek_dogu x max(0, t - t_H) eklenir (pozitif kontrol). Dönüş ((dvE, dvN), None) ya da
    (None, neden)."""
    X = tasarim(ms, w0, H, adimlar)
    if not _rank_tam(X):
        return None, 'rank'
    dv = []
    for k, y in enumerate((E, N)):
        y = np.asarray(y, float) - y[0]
        if k == 0 and ek_dogu:
            y = y + ek_dogu * X[:, -1]
        b1 = np.linalg.lstsq(X, y, rcond=None)[0]
        r = y - X @ b1
        med = np.median(r)
        sap = np.abs(r - med)
        mad = np.median(sap)
        if mad > 0:
            tut = sap <= MAD_K * mad
            Xk = X[tut]
            if not _rank_tam(Xk):
                return None, 'rank_mad'
            b2 = np.linalg.lstsq(Xk, y[tut], rcond=None)[0]
        else:
            b2 = b1
        dv.append(float(b2[-1]))
    return tuple(dv), None


# ===================================================================== gürültü: Williams (2003) kesirli fark
def h_katsayi(kappa, n=N_PEN):
    v = np.empty(n); v[0] = 1.0
    for i in range(1, n):
        v[i] = v[i - 1] * (i - 1 - kappa / 2) / i
    return v


HF, HR = h_katsayi(-1.0), h_katsayi(-2.0)
NFFT = 4096
_FHF, _FHR = np.fft.rfft(HF, NFFT), np.fft.rfft(HR, NFFT)


def _Ta(a, FH):
    """T' a (T alt üçgen Toeplitz, ilk sütun h): (T'a)_j = sum_{i>=j} a_i h_{i-j}."""
    c = np.fft.irfft(np.fft.rfft(a[::-1], NFFT) * FH, NFFT)[:len(a)]
    return c[::-1]


def _Tz(z, FH):
    """T z = süzülmüş seri: (Tz)_i = sum_{j<=i} h_{i-j} z_j."""
    return np.fft.irfft(np.fft.rfft(z, NFFT) * FH, NFFT)[:len(z)]


def sigma_bilesenleri(ms, w0, H, adimlar):
    """Maskeli tasarımın menteşe satırı a (eksik günlerde 0) -> (VW, VF, VR):
    sigma_h^2 = sw^2 VW + bf^2 VF + brw^2 VR; VW = a'a, VF = dT^(1/2) |T_F' a|^2, VR = dT |T_R' a|^2."""
    X = tasarim(ms, w0, H, adimlar)
    Q, R = np.linalg.qr(X)
    a = Q[:, -1] / R[-1, -1]                 # (X'X)^-1 X' 'nin son satırı
    af = np.zeros(N_PEN)
    af[ms - w0] = a
    return (float(af @ af), DT ** 0.5 * float(np.sum(_Ta(af, _FHF) ** 2)),
            DT * float(np.sum(_Ta(af, _FHR) ** 2)))


def sigma_h(v, sw=SW, bf=BF0, brw=0.0):
    VW, VF, VR = v
    return math.sqrt(sw ** 2 * VW + bf ** 2 * VF + brw ** 2 * VR)


def yapay_seri(sta, Ts, sw=SW, bf=BF0):
    """Kod denetimi (i) yapay serisi: 1826 günlük tam ızgara, beyaz + kesirli farkla süzülmüş kırpışma, iki bileşen.
    Tohum int(SHA-256(f"{STA}|{T}")[:16], 16) XOR 20261111. Çekiliş sırası: (4, 1826) standart normal;
    satırlar doğu beyaz, kuzey beyaz, doğu kırpışma, kuzey kırpışma."""
    tohum = int(hashlib.sha256(f'{sta}|{Ts}'.encode()).hexdigest()[:16], 16) ^ TOHUM
    z = np.random.default_rng(tohum).standard_normal((4, N_PEN))
    c = bf * DT ** 0.25
    return sw * z[0] + c * _Tz(z[2], _FHF), sw * z[1] + c * _Tz(z[3], _FHF)


# ===================================================================== küme ölçüsü S
def S_hesapla(y, r):
    """y: (..., n_y, 2) yakın Δv; r: (..., n_r, 2) referans Δv. Bileşen bazında referans medyanı çıkarılır;
    boyların medyanı (numpy.median; çiftte ortadaki ikisinin ortalaması)."""
    m = np.median(r, axis=-2, keepdims=True)
    return np.median(np.sqrt(((y - m) ** 2).sum(axis=-1)), axis=-1)


def S_refsiz(y):
    return np.median(np.sqrt((y ** 2).sum(axis=-1)), axis=-1)


# ===================================================================== nicelikler
def nicelik(x, q):
    return np.quantile(np.asarray(x, float), q, method='linear')


def agirlikli_nicelik(vals_sirali, sahip_sirali, w, qs):
    """np.quantile(np.repeat(...), method='linear') ile birebir aynı sonuç: sıralı değerler, her değerin sahibi
    (küme-pencere yerel indisi) ve sahip başına tam sayı ağırlık (tekrar sayısı)."""
    c = np.asarray(w, np.int64)[sahip_sirali]
    C = np.cumsum(c)
    n = int(C[-1])
    out = []
    for q in np.atleast_1d(qs):
        v = (n - 1) * q
        i0 = math.floor(v)
        g = v - i0
        i0 = min(max(i0, 0), n - 1); i1 = min(i0 + 1, n - 1)
        a = vals_sirali[np.searchsorted(C, i0, side='right')]
        b = vals_sirali[np.searchsorted(C, i1, side='right')]
        d = b - a
        out.append(b - d * (1 - g) if g >= 0.5 else a + d * g)
    return np.array(out)


def havuz(draws_list):
    """[(M,) dizi her küme-pencere için] -> (sıralı değerler, sahip)."""
    v = np.concatenate(draws_list)
    s = np.concatenate([np.full(len(d), k, np.int32) for k, d in enumerate(draws_list)])
    o = np.argsort(v, kind='stable')
    return v[o], s[o]


# ===================================================================== paralel yardımcı (fork; büyük veri kalıtılır)
_G = {}


def paralel(fn, isler, surec, chunksize=16):
    if surec <= 1 or len(isler) < 2:
        return [fn(x) for x in isler]
    with mp.get_context('fork').Pool(surec) as p:
        return p.map(fn, isler, chunksize=max(1, min(chunksize, len(isler) // (4 * surec) or 1)))


def _oku_is(sta):
    g = _G
    yol = os.path.join(g['tenv3'], f'{sta}.tenv3')
    Tler = sorted(g['ist_T'][sta])
    pen = [(pencere(T)[0], pencere(T)[2]) for T in Tler]
    sha_ok = None
    if sta not in g['o4']:
        sha_ok = sha256_dosya(yol) == g['manifest_sha'].get(sta)
    try:
        with open(yol, 'r', errors='replace') as f:
            seriler, bilgi = tenv3_ayristir(f, pen)
    except Tenv3Hata as e:
        return sta, None, dict(hata=str(e)), sha_ok
    out = {T: ist_hazirla(ms, E, N, T, pencere_adimlari(g['k1'], sta, T)) for T, (ms, E, N) in zip(Tler, seriler)}
    return sta, out, bilgi, sha_ok


def ist_hazirla(ms, E, N, T, adim):
    """(istasyon, T): doluluk (ayıklamadan önce, satır günleriyle; taban 1096, yakın dönem 730 takvim günü, her biri
    >= 0,60), rank denetimi ve sigma_h bileşenleri (gün maskesi MAD'den önce)."""
    w0, H, w1 = pencere(T)
    r = dict(ms=ms, E=E, N=N, adim=adim, n_tab=int((ms < H).sum()), n_yak=int((ms >= H).sum()))
    if len(ms) == 0:
        r['neden'] = 'satir_yok'
    elif r['n_tab'] / N_TAB < DOLULUK or r['n_yak'] / N_YAK < DOLULUK:
        r['neden'] = 'doluluk'
    elif not _rank_tam(tasarim(ms, w0, H, adim)):
        r['neden'] = 'rank'
    else:
        r['neden'] = None
        r['v'] = sigma_bilesenleri(ms, w0, H, adim)
    return r


def _yapay_is(anahtar):
    sta, T = anahtar
    g = _G
    r = g['kayit'][anahtar]
    w0, H, w1 = pencere(T)
    Ef, Nf = yapay_seri(sta, T.isoformat())
    i = r['ms'] - w0
    la, lo = g['koord'].get(sta, (0.0, 0.0))
    satir = tenv3_satirlari(sta, r['ms'], Ef[i], Nf[i], lat=la, lon=lo)
    (ser,), _ = tenv3_ayristir(satir, [(w0, w1)])
    ms, E, N = ser
    o, neden = olc(ms, E, N, w0, H, r['adim'])
    e = None
    if o is not None and anahtar in g['ekle']:
        e, neden2 = olc(ms, E, N, w0, H, r['adim'], ek_dogu=SINYAL)
        neden = neden or neden2
    return anahtar, o, e, neden


def _gercek_is(arg):
    anahtar, ekle = arg
    sta, T = anahtar
    r = _G['kayit'][anahtar]
    w0, H, w1 = pencere(T)
    o, neden = olc(r['ms'], r['E'], r['N'], w0, H, r['adim'])
    e = None
    if o is not None and ekle:
        e, neden2 = olc(r['ms'], r['E'], r['N'], w0, H, r['adim'], ek_dogu=SINYAL)
        neden = neden or neden2
    return anahtar, o, e, neden


# ===================================================================== Monte Carlo (E2 madde 3)
class MC:
    """Her geçerli küme-pencere için M çekiliş, liste sırasıyla; üreteç default_rng(20261111).
    Küme-pencere k için z_k ~ N(0, 1), biçim (M, n_y + n_r, 2), önce yakınlar sonra referanslar (liste sırası).
    Δv = sigma_h(istasyon, T) x z."""

    def __init__(self, kps, kayit, M):
        rng = np.random.default_rng(TOHUM)
        self.M = M
        self.z = []
        self.sut = []
        for kp in kps:
            self.z.append(rng.standard_normal((M, len(kp['y']) + len(kp['r']), 2)))
            self.sut.append({s: j for j, s in enumerate(list(kp['y']) + list(kp['r']))})
        self.kps = kps
        self.v = [(np.array([kayit[(s, kp['T'])]['v'] for s in kp['y']]),
                   np.array([kayit[(s, kp['T'])]['v'] for s in kp['r']])) for kp in kps]

    def cekilis(self, k, sw=SW, bf=BF0, brw=0.0, y=None, r=None, refsiz=False, ek=0.0):
        kp = self.kps[k]
        y = kp['y'] if y is None else y
        r = kp['r'] if r is None else r
        vy, vr = self.v[k]
        iy = [kp['y'].index(s) for s in y]; ir = [kp['r'].index(s) for s in r]
        sy = np.sqrt(sw ** 2 * vy[iy, 0] + bf ** 2 * vy[iy, 1] + brw ** 2 * vy[iy, 2])
        sr = np.sqrt(sw ** 2 * vr[ir, 0] + bf ** 2 * vr[ir, 1] + brw ** 2 * vr[ir, 2])
        z = self.z[k]
        Y_ = z[:, [self.sut[k][s] for s in y], :] * sy[None, :, None]
        if ek:
            Y_ = Y_.copy(); Y_[:, :, 0] += ek
        if refsiz:
            return S_refsiz(Y_)
        R_ = z[:, [self.sut[k][s] for s in r], :] * sr[None, :, None]
        return S_hesapla(Y_, R_)


def _mc_bf_is(arg):
    bf, idx = arg
    mc = _G['mc']
    return [mc.cekilis(k, bf=bf, y=_G['yy'][k], r=_G['rr'][k]) for k in idx]


def mc_havuz_bf(mc, kidx, yy, rr, bf, surec):
    _G.update(mc=mc, yy=yy, rr=rr)
    parca = [kidx[i::max(1, surec)] for i in range(max(1, surec))]
    res = paralel(_mc_bf_is, [(bf, p) for p in parca if len(p)], surec, chunksize=1)
    d = {}
    for p, rr_ in zip([p for p in parca if len(p)], res):
        for k, x in zip(p, rr_):
            d[k] = x
    return [d[k] for k in kidx]


# ===================================================================== bootstrap (E2 madde 5)
def _boot_is(satirlar):
    g = _G['boot']
    out = []
    for sec in satirlar:
        cnt = np.bincount(sec, minlength=g['nu'])
        w = cnt[g['birim']] * g['taban_w']
        r = dict(S=nicelik(np.repeat(g['S'], w), QS))
        for ad, (v, s) in g['havuz'].items():
            r[ad] = agirlikli_nicelik(v, s, w, (0.5, 0.95))
        if g.get('izgara') is not None:
            r['bf'] = _bf_izgara_coz(g['izgara'], r['S'][2], w)
        out.append(r)
    return out


def _bf_izgara_coz(izg, hedef, w):
    b, hv = izg['b'], izg['h']
    q = lambda i: agirlikli_nicelik(hv[i][0], hv[i][1], w, (0.95,))[0]
    lo, hi = 0, len(b) - 1
    qlo, qhi = q(lo), q(hi)
    if hedef <= qlo:
        return (float(b[lo]), 'alt_sinir')
    if hedef > qhi:
        return (float(b[hi]), 'ust_sinir')
    while hi - lo > 1:
        mid = (lo + hi) // 2
        qm = q(mid)
        if qm < hedef:
            lo, qlo = mid, qm
        else:
            hi, qhi = mid, qm
    return (float(b[lo] + (hedef - qlo) / (qhi - qlo) * (b[hi] - b[lo])) if qhi > qlo else float(b[hi]), None)


def bootstrap(S, birim, havuzlar, B, surec, taban_w=None, izgara=None):
    """S: yerel küme-pencere ölçümleri; birim: her küme-pencerenin birim indisi (0..nu-1, sıralı birim listesine göre).
    Üreteç default_rng(20261111 + 1); seçim dizisi (B, nu) rng.integers(0, nu) ile tek seferde."""
    S = np.asarray(S, float)
    birim = np.asarray(birim, np.int64)
    nu = int(birim.max()) + 1
    taban_w = np.ones(len(S), np.int64) if taban_w is None else np.asarray(taban_w, np.int64)
    sec = np.random.default_rng(TOHUM + 1).integers(0, nu, size=(B, nu))
    _G['boot'] = dict(S=S, birim=birim, nu=nu, taban_w=taban_w, havuz=havuzlar, izgara=izgara)
    parca = [sec[i::max(1, surec)] for i in range(max(1, surec))]
    res = paralel(_boot_is, [p for p in parca if len(p)], surec, chunksize=1)
    out = [None] * B
    for i, rr in enumerate(res):
        for j, x in enumerate(rr):
            out[i + j * max(1, surec)] = x
    return out


# ===================================================================== yardımcı: aralık ve biçim
def aralik(x):
    x = np.asarray(x, float)
    return [float(v) for v in nicelik(x, [0.05, 0.95])]


def f2(x, n=2):
    if x is None:
        return '–'
    if isinstance(x, (list, tuple)):
        return '[' + ', '.join(f2(v, n) for v in x) + ']'
    return f'{x:.{n}f}'.replace('.', ',')


# ===================================================================== koşu
class KosuDur(Exception):
    pass


def girdi_denetimi(a, ayar):
    """0. adım: hiçbir tenv3 okunmadan önce. Uyuşmazlıkta KosuDur."""
    d = {}
    for ad in ('tr11_sonuc.json', 'tr11_sonuc.md'):
        if os.path.exists(os.path.join(a.cikti, ad)):
            raise KosuDur(f'tek koşu koruması: {os.path.join(a.cikti, ad)} zaten var; koşu başlatılmadı')
    d['liste_sha256'] = sha256_dosya(a.liste)
    if d['liste_sha256'] != ayar.liste_sha256:
        raise KosuDur(f'küme listesi sha256 uyuşmuyor: {d["liste_sha256"]}')
    d['ustveri_sha256'] = {}
    for ad, b in ayar.ustveri_sha16.items():
        h = sha256_dosya(os.path.join(a.ustveri, ad)); d['ustveri_sha256'][ad] = h
        if h[:16] != b:
            raise KosuDur(f'{ad} sha256 uyuşmuyor: {h[:16]} != {b}')
    d['tr2_sha256'] = {}
    for ad, b in ayar.tr2_sha16.items():
        h = sha256_dosya(os.path.join(a.tr2, ad)); d['tr2_sha256'][ad] = h
        if h[:16] != b:
            raise KosuDur(f'TR-2 {ad} sha256 uyuşmuyor: {h[:16]} != {b}')
    with open(a.liste) as f:
        liste = json.load(f)
    koord = dataholdings_oku(os.path.join(a.ustveri, 'DataHoldings.txt'))
    istasyonlar = sorted({s for k in liste for s in k['y'] + k['r']})
    eksik = [s for s in istasyonlar if s not in koord]
    if eksik:
        raise KosuDur(f'DataHoldings\'te olmayan liste istasyonu: {eksik[:10]}')
    kutu = [s for s in istasyonlar if marmara_icinde(*koord[s])]
    if kutu:
        raise KosuDur(f'listede Marmara kutusu istasyonu var: {kutu}')
    if any(marmara_icinde(k['la'], k['lo']) for k in liste):
        raise KosuDur('listede Marmara kutusunda merkez var')
    o4 = sorted(s for s in istasyonlar if marmara_uzaklik(*koord[s]) < O4_KM)
    if not os.path.exists(a.manifest):
        raise KosuDur(f'indirme manifesti yok: {a.manifest}')
    with open(a.manifest) as f:
        man = json.load(f)
    d['manifest_sha256'] = sha256_dosya(a.manifest)
    mi = man.get('istasyonlar', {})
    tamam = {s: v['sha256'] for s, v in mi.items() if v.get('durum') == 'tamam' and v.get('sha256')}
    basarisiz = sorted(s for s in istasyonlar if s not in tamam)
    for s in tamam:
        if s in istasyonlar and not os.path.exists(os.path.join(a.tenv3, f'{s}.tenv3')):
            basarisiz.append(s)
    basarisiz = sorted(set(basarisiz))
    pay = len(basarisiz) / len(istasyonlar)
    if pay > INDIRME_HATA_PAY:
        raise KosuDur(f'indirme hatası payı %{100 * pay:.1f} > %5 ({len(basarisiz)} istasyon); koşu durdu, '
                      f'S hesaplanmadı. Tek bir yeniden deneme turu yapılmalı (K6).')
    d.update(liste=liste, koord=koord, istasyonlar=istasyonlar, o4=o4, basarisiz=basarisiz, indirme_pay=pay,
             manifest_sha=tamam)
    return d


def kos(a, ayar=None, kayit_fn=print):
    ayar = ayar or Ayar()
    t0 = time.time()
    log = lambda s: kayit_fn(f'[{time.time() - t0:7.1f} sn] {s}')
    d = girdi_denetimi(a, ayar)
    liste, koord, o4 = d['liste'], d['koord'], d['o4']
    log(f'girdi denetimi geçti: {len(liste)} küme-pencere, {len(d["istasyonlar"])} istasyon, indirme hatası '
        f'{len(d["basarisiz"])} (%{100 * d["indirme_pay"]:.2f}); Ö4 istasyonları {o4}')
    if getattr(a, 'yalniz_denetim', False):
        return None
    sinif = Sinif(a.tr2)
    k1 = steps_kod1_oku(os.path.join(a.ustveri, 'steps.txt'))

    # ------------------------------------------------------------ okuma (yalnız pencereler)
    ist_T = collections.defaultdict(set)
    for k in liste:
        T = dt.date.fromisoformat(k['T'])
        for s in k['y'] + k['r']:
            ist_T[s].add(T)
    basarisiz = set(d['basarisiz'])
    _G.clear()
    _G.update(tenv3=a.tenv3, ist_T=ist_T, o4=set(o4), manifest_sha=d['manifest_sha'], k1=k1)
    oku = [s for s in sorted(ist_T) if s not in basarisiz]
    res = paralel(_oku_is, oku, ayar.surec, chunksize=8)
    kayit, okuma_bilgi = {}, dict(bozuk=0, geri=0, tekrar=0, durdu=0, baslik_yok=0, tenv3_hata=[], sha_uyusmaz=[])
    for sta, out, bilgi, sha_ok in res:
        if sha_ok is False:
            okuma_bilgi['sha_uyusmaz'].append(sta)
        if out is None:
            okuma_bilgi['tenv3_hata'].append((sta, bilgi['hata']))
            basarisiz.add(sta)
            continue
        for kk in ('bozuk', 'geri', 'tekrar'):
            okuma_bilgi[kk] += bilgi[kk]
        okuma_bilgi['durdu'] += int(bilgi['durdu'])
        okuma_bilgi['baslik_yok'] += int(not bilgi['baslik'])
        for T, r in out.items():
            kayit[(sta, T)] = r
    if okuma_bilgi['sha_uyusmaz']:
        raise KosuDur(f'tenv3 dosyası manifestteki sha256 ile uyuşmuyor: {okuma_bilgi["sha_uyusmaz"][:10]}')
    for s in basarisiz:
        for T in ist_T.get(s, ()):
            kayit[(s, T)] = dict(neden='indirme')
    del res
    log(f'okuma bitti: {len(kayit)} (istasyon, T)')

    # ------------------------------------------------------------ geçerlilik ve veri kapısı (K2)
    ist_neden = collections.Counter(r['neden'] or 'gecerli' for r in kayit.values())
    gec = lambda s, T: kayit[(s, T)]['neden'] is None
    kps, kp_dus = [], collections.Counter()
    for i, k in enumerate(liste):
        T = dt.date.fromisoformat(k['T'])
        y = [s for s in k['y'] if gec(s, T)]
        r = [s for s in k['r'] if gec(s, T)]
        if len(y) < 3 or len(r) < 3:
            kp_dus['yakin<3' if len(y) < 3 else 'referans<3'] += 1
            continue
        kps.append(dict(i=i, T=T, Ts=k['T'], la=k['la'], lo=k['lo'], y=y, r=r, y0=k['y'], r0=k['r'],
                        yer=(k['la'], k['lo']), blok=(int(math.floor(k['la'] / 10)), int(math.floor(k['lo'] / 10)))))
    # pozitif kontrol seçimi (E1): bütün listede SHA-256 sırası, ilk floor(n/2); düşenler seçimden çıkar
    anahtar = [hashlib.sha256(f'{k["T"]}|{k["la"]:.4f}|{k["lo"]:.4f}'.encode()).hexdigest() for k in liste]
    secili_i = set(sorted(range(len(liste)), key=lambda i: anahtar[i])[:len(liste) // 2])
    for kp in kps:
        kp['secili'] = kp['i'] in secili_i
    yerler = sorted({kp['yer'] for kp in kps})
    bloklar = sorted({kp['blok'] for kp in kps})
    sonuc = dict(
        tr='TR-11', surum='tr11_kosu.py', ayar=dict(dataclasses.asdict(ayar), bagli_degerler=ayar.bagli_mi()),
        girdi=dict(liste_sha256=d['liste_sha256'], ustveri_sha256=d['ustveri_sha256'], tr2_sha256=d['tr2_sha256'],
                   indirme_manifesti_sha256=d['manifest_sha256'], tenv3_sha256=d['manifest_sha']),
        o4=dict(istasyonlar=o4, kural='w1 sonrası satırlar okunmadan okuma durduruldu; dosyalar koşudan sonra silinir'),
        dusme=dict(indirme_hatasi_istasyon=sorted(basarisiz), indirme_hatasi_pay=d['indirme_pay'],
                   istasyon_T_neden=dict(ist_neden), kume_pencere_neden=dict(kp_dus),
                   kume_pencere_liste=len(liste), kume_pencere_gecerli=len(kps),
                   okuma=dict((k, v) for k, v in okuma_bilgi.items() if k != 'sha_uyusmaz')),
        kapi=dict(yer=len(yerler), blok=len(bloklar), esik=dict(yer=KAPI_YER, blok=KAPI_BLOK)))
    log(f'veri kapısı: KP {len(kps)}, yer {len(yerler)}, blok {len(bloklar)}')
    if len(yerler) < KAPI_YER or len(bloklar) < KAPI_BLOK:
        sonuc['hukum'] = 'veri yok'
        return yaz(a, sonuc, o4, log)

    # ------------------------------------------------------------ Monte Carlo q95_N0 (E2 madde 3)
    mc = MC(kps, kayit, ayar.M)
    K = len(kps)
    _G.update(kayit=kayit, koord=koord)
    yy = [kp['y'] for kp in kps]; rr = [kp['r'] for kp in kps]
    SN0 = mc_havuz_bf(mc, list(range(K)), yy, rr, BF0, ayar.surec)
    log('Monte Carlo N0 bitti')

    # ------------------------------------------------------------ kod denetimi (i) ve (ii-b): yapay seriler
    gerekli = sorted({(s, kp['T']) for kp in kps for s in kp['y'] + kp['r']})
    ekle = {(s, kp['T']) for kp in kps if kp['secili'] for s in kp['y']}
    _G['ekle'] = ekle
    yres = paralel(_yapay_is, gerekli, ayar.surec, chunksize=32)
    yo = {k_: (o, e, n) for k_, o, e, n in yres}
    del yres
    yS, yfark, y_dus = [], [], 0
    yS_k = []
    for k, kp in enumerate(kps):
        y = [s for s in kp['y'] if yo[(s, kp['T'])][0] is not None]
        r = [s for s in kp['r'] if yo[(s, kp['T'])][0] is not None]
        if len(y) < 3 or len(r) < 3:
            y_dus += 1
            continue
        Yv = np.array([yo[(s, kp['T'])][0] for s in y]); Rv = np.array([yo[(s, kp['T'])][0] for s in r])
        S0 = float(S_hesapla(Yv, Rv))
        yS.append(S0); yS_k.append(k)
        if kp['secili']:
            if any(yo[(s, kp['T'])][1] is None for s in y):
                y_dus += 1
                continue
            Ye = np.array([yo[(s, kp['T'])][1] for s in y])
            yfark.append(float(S_hesapla(Ye, Rv)) - S0)
    q95_N0 = float(nicelik(np.concatenate(SN0), 0.95))
    oran_i = float(nicelik(yS, 0.95)) / q95_N0
    sec_k = [k for k, kp in enumerate(kps) if kp['secili']]
    mfark = np.concatenate([mc.cekilis(k, ek=SINYAL) - SN0[k] for k in sec_k]) if sec_k else np.array([np.nan])
    m_yildiz = float(np.median(mfark))
    olc_iib = float(np.median(yfark)) if yfark else float('nan')
    gecti_i = ORAN_ARALIK[0] <= oran_i <= ORAN_ARALIK[1]
    gecti_iib = IIB_ARALIK[0] * m_yildiz <= olc_iib <= IIB_ARALIK[1] * m_yildiz
    sonuc['kod_denetimi'] = dict(
        i=dict(q95_yapay=float(nicelik(yS, 0.95)), q95_N0=q95_N0, oran=oran_i, aralik=list(ORAN_ARALIK),
               gecti=gecti_i, kume_pencere=len(yS)),
        ii_b=dict(olculen_medyan_fark=olc_iib, m_yildiz=m_yildiz, aralik=[IIB_ARALIK[0] * m_yildiz,
                  IIB_ARALIK[1] * m_yildiz], gecti=gecti_iib, secili_kume_pencere=len(yfark)),
        yapay_dusen_kume_pencere=y_dus)
    log(f'kod denetimi (i) oran {oran_i:.3f} ({"geçti" if gecti_i else "KALDI"}); (ii-b) {olc_iib:.3f} / m* '
        f'{m_yildiz:.3f} ({"geçti" if gecti_iib else "KALDI"})')
    if not (gecti_i and gecti_iib):
        sonuc['hukum'] = 'geçersiz (kod)'
        return yaz(a, sonuc, o4, log)

    # ------------------------------------------------------------ kod denetimi (ii-a): gerçek veri, istasyon düzeyi
    isler = [(k_, k_ in ekle) for k_ in gerekli]
    gres = paralel(_gercek_is, isler, ayar.surec, chunksize=32)
    go = {k_: (o, e, n) for k_, o, e, n in gres}
    del gres
    dE, dN = [], []
    for kp in kps:
        if not kp['secili']:
            continue
        for s in kp['y']:
            o, e, _ = go[(s, kp['T'])]
            if o is None or e is None:
                continue
            dE.append(e[0] - o[0]); dN.append(e[1] - o[1])
    med_dE = float(np.median(dE)) if dE else float('nan')
    med_adN = float(np.median(np.abs(dN))) if dN else float('nan')
    gecti_iia = D_E_ARALIK[0] <= med_dE <= D_E_ARALIK[1] and med_adN < D_N_UST
    sonuc['kod_denetimi']['ii_a'] = dict(medyan_dE=med_dE, medyan_abs_dN=med_adN, aralik_dE=list(D_E_ARALIK),
                                         ust_abs_dN=D_N_UST, gecti=gecti_iia, istasyon_cifti=len(dE))
    log(f'kod denetimi (ii-a) medyan d_E {med_dE:.4f}, medyan |d_N| {med_adN:.4f} ({"geçti" if gecti_iia else "KALDI"})')
    if not gecti_iia:
        sonuc['hukum'] = 'geçersiz (kod)'
        return yaz(a, sonuc, o4, log)

    # ------------------------------------------------------------ gerçek S (yalnız buradan sonra)
    ana = ana_olcum(kps, kayit, go, mc, SN0, sinif, k1, ayar, sonuc, log)
    sonuc.update(ana)
    return yaz(a, sonuc, o4, log)


# ===================================================================== ana ölçüm (adım 4)
def ana_olcum(kps, kayit, go, mc, SN0, sinif, k1, ayar, sonuc, log):
    out = {}
    # gerçek uydurmada (ayıklama sonrası) rank düşen istasyonlar
    gS, gk, dus_gercek = [], [], 0
    yy, rr = {}, {}
    for k, kp in enumerate(kps):
        y = [s for s in kp['y'] if go[(s, kp['T'])][0] is not None]
        r = [s for s in kp['r'] if go[(s, kp['T'])][0] is not None]
        if len(y) < 3 or len(r) < 3:
            dus_gercek += 1
            continue
        yy[k], rr[k] = y, r
        gk.append(k)
    sonuc['dusme']['kume_pencere_gercek_uydurma_dusen'] = dus_gercek
    dv = lambda s, T: np.array(go[(s, T)][0])
    S = np.array([float(S_hesapla(np.array([dv(s, kps[k]['T']) for s in yy[k]]),
                                  np.array([dv(s, kps[k]['T']) for s in rr[k]]))) for k in gk])
    # MC çekilişleri, gerçek uydurmada istasyon düştüyse yalnız kalan sütunlarla
    N0 = [SN0[k] if (yy[k] == kps[k]['y'] and rr[k] == kps[k]['r'])
          else mc.cekilis(k, y=yy[k], r=rr[k]) for k in gk]
    N1 = [mc.cekilis(k, brw=BRW_N1, y=yy[k], r=rr[k]) for k in gk]
    log(f'gerçek S hesaplandı: {len(S)} küme-pencere')
    kp_g = [kps[k] for k in gk]
    for kp in kp_g:
        kp['sinif'] = sinif(kp['la'], kp['lo'])
    blok_l = sorted({kp['blok'] for kp in kp_g}); yer_l = sorted({kp['yer'] for kp in kp_g})
    bidx = np.array([blok_l.index(kp['blok']) for kp in kp_g])
    yidx = np.array([yer_l.index(kp['yer']) for kp in kp_g])

    def katman(ad, maske, birim='blok', taban_w=None, Sx=None, N0x=None, N1x=None, bf=False, q99=True):
        L = np.where(maske)[0]
        if len(L) == 0:
            return dict(ad=ad, kume_pencere=0)
        Sx = S if Sx is None else Sx
        N0x = N0 if N0x is None else N0x
        N1x = N1 if N1x is None else N1x
        Ss = Sx[L]
        lab = (bidx if birim == 'blok' else yidx)[L]
        u = sorted(set(lab.tolist())); lab = np.array([u.index(x) for x in lab])
        tw = None if taban_w is None else np.asarray(taban_w)[L]
        hv = {'N0': havuz([N0x[i] for i in L])}
        if N1x is not False:
            hv['N1'] = havuz([N1x[i] for i in L])
        w1 = np.ones(len(L), np.int64) if tw is None else tw
        nok = dict(S=nicelik(np.repeat(Ss, w1), QS), **{h: agirlikli_nicelik(v, s, w1, (0.5, 0.95))
                                                       for h, (v, s) in hv.items()})
        izg = None
        bf_nokta = None
        if bf:
            bf_nokta, izg = bf_hazirla(mc, [gk[i] for i in L], yy, rr, nok['S'][2], ayar, log)
        bs = bootstrap(Ss, lab, hv, ayar.B, ayar.surec, taban_w=tw, izgara=izg)
        bsS = np.array([b['S'] for b in bs])
        sat = dict(ad=ad, kume_pencere=int(len(L)), yer=int(len({kp_g[i]['yer'] for i in L})),
                   blok=int(len({kp_g[i]['blok'] for i in L})), birim=birim, B=ayar.B)
        for j, q in enumerate(QS):
            if q == 0.99 and (not q99 or len(L) < Q99_KP_MIN):
                sat['q99'] = None
                continue
            sat[f'q{int(round(q * 100))}'] = dict(nokta=float(nok['S'][j]), aralik=aralik(bsS[:, j]))
        n095 = np.array([b['N0'][1] for b in bs]); n050 = np.array([b['N0'][0] for b in bs])
        rho = bsS[:, 2] / n095; rho50 = bsS[:, 0] / n050
        sat['q95_N0'] = float(nok['N0'][1]); sat['medyan_N0'] = float(nok['N0'][0])
        sat['rho'] = dict(nokta=float(nok['S'][2] / nok['N0'][1]), aralik=aralik(rho))
        sat['rho50'] = dict(nokta=float(nok['S'][0] / nok['N0'][0]), aralik=aralik(rho50))
        sat['kuyruk'] = dict(nokta=sat['rho']['nokta'] / sat['rho50']['nokta'], aralik=aralik(rho / rho50))
        if 'N1' in hv:
            n195 = np.array([b['N1'][1] for b in bs])
            sat['q95_N1'] = float(nok['N1'][1])
            sat['rho_N1'] = dict(nokta=float(nok['S'][2] / nok['N1'][1]), aralik=aralik(bsS[:, 2] / n195))
        if bf:
            bfs = np.array([b['bf'][0] for b in bs])
            sat['bf_yildiz'] = dict(nokta=bf_nokta[0], nokta_bayrak=bf_nokta[1], aralik=aralik(bfs),
                                    izgara=[float(izg['b'][0]), float(izg['b'][-1]), len(izg['b'])],
                                    izgara_disi=int(sum(b['bf'][1] is not None for b in bs)))
        return sat

    tum = np.ones(len(kp_g), bool)
    out['ana'] = katman('havuz', tum, bf=True)
    log('ana katman bitti')
    a_ = out['ana']
    bfL, bfU = a_['bf_yildiz']['aralik']
    if bfL > 4:
        etiket = "taban N0-yüksek'ten büyük"
    elif bfU < 2:
        etiket = "taban N0-düşük'ten küçük"
    else:
        etiket = 'taban N0 bandında (b_f 2–4)'
    out['hukum'] = etiket
    out['kuyruk_hukum'] = "kuyruk Gauss N0'dan ağır" if a_['kuyruk']['aralik'][0] > 1.1 else None
    out['rho_N0_konumu'] = ('ρ_L > 1' if a_['rho']['aralik'][0] > 1 else 'ρ_U < 1' if a_['rho']['aralik'][1] < 1
                            else 'ρ aralığı 1\'i içeriyor')
    # kırılımlar
    ny = np.array([len(yy[k]) for k in gk])
    kir = dict(n_y={}, sinif={}, epok={})
    for ad, m in (('3–4', (ny >= 3) & (ny <= 4)), ('5–7', (ny >= 5) & (ny <= 7)), ('8', ny == 8)):
        kir['n_y'][ad] = katman(f'n_y {ad}', m)
    for c in ('A', 'B', 'D'):
        m = np.array([kp['sinif'] == c for kp in kp_g])
        nyer = len({kp_g[i]['yer'] for i in np.where(m)[0]})
        if nyer >= SINIF_YER_MIN:
            kir['sinif'][c] = katman(f'sınıf {c}', m)
        else:
            kir['sinif'][c] = dict(ad=f'sınıf {c}', hukum='güç yok', yer=nyer, kume_pencere=int(m.sum()))
    for T in sorted({kp['Ts'] for kp in kp_g}):
        kir['epok'][T] = katman(f'epok {T}', np.array([kp['Ts'] == T for kp in kp_g]))
    out['kirilim'] = kir
    log('kırılımlar bitti')
    # bilgi satırları
    bil = {}
    S_ref = np.array([float(S_refsiz(np.array([dv(s, kps[k]['T']) for s in yy[k]]))) for k in gk])
    N0_ref = [mc.cekilis(k, y=yy[k], r=rr[k], refsiz=True) for k in gk]
    bil['referans_farki_yok'] = katman('referans farkı alınmamış S', tum, Sx=S_ref, N0x=N0_ref, N1x=False)
    bil['yer_bootstrap'] = katman('yer bootstrap', tum, birim='yer')
    bc = collections.Counter(kp['blok'] for kp in kp_g)
    enb = max(sorted(bc), key=lambda b: bc[b])
    bil['en_buyuk_blok_disarida'] = katman(f'en büyük blok {enb} dışarıda', np.array([kp['blok'] != enb for kp in kp_g]))
    bil['en_buyuk_blok_disarida']['blok_adi'] = list(enb)
    # bileşen bazında: yakın istasyon Δv'leri (ham) ve referans medyanı çıkarılmış
    ham, fark = [], []
    for k in gk:
        T = kps[k]['T']
        Yv = np.array([dv(s, T) for s in yy[k]]); m = np.median(np.array([dv(s, T) for s in rr[k]]), axis=0)
        ham.append(Yv); fark.append(Yv - m)
    ham = np.concatenate(ham); fark = np.concatenate(fark)
    bil['bilesen'] = {nm: {c: dict(medyan=float(np.median(X[:, j])), q95=float(nicelik(X[:, j], 0.95)),
                                   medyan_mutlak=float(np.median(np.abs(X[:, j]))),
                                   q95_mutlak=float(nicelik(np.abs(X[:, j]), 0.95)))
                           for j, c in enumerate(('dogu', 'kuzey'))}
                      for nm, X in (('ham', ham), ('referans_farki', fark))}
    bil['bilesen']['yakin_istasyon_kume_cifti'] = int(len(ham))
    # kod 1'li istasyonlar dışarıda
    S_k1, N0_k1, N1_k1, m_k1 = [], [], [], []
    for k in gk:
        T = kps[k]['T']
        y = [s for s in yy[k] if not pencere_adimlari(k1, s, T)]
        r = [s for s in rr[k] if not pencere_adimlari(k1, s, T)]
        if len(y) < 3 or len(r) < 3:
            S_k1.append(np.nan); N0_k1.append(None); N1_k1.append(None); m_k1.append(False)
            continue
        S_k1.append(float(S_hesapla(np.array([dv(s, T) for s in y]), np.array([dv(s, T) for s in r]))))
        N0_k1.append(mc.cekilis(k, y=y, r=r)); N1_k1.append(False); m_k1.append(True)
    bil['kod1_disarida'] = katman("kod 1'li istasyonlar dışarıda", np.array(m_k1), Sx=np.array(S_k1), N0x=N0_k1,
                                  N1x=False)
    # yer ağırlıklı q95 (K1): her yerin küme-pencereleri 1/n_epok; tam sayı ağırlık 60/n_epok
    ne = collections.Counter(kp['yer'] for kp in kp_g)
    tw = np.array([BIRIM_YER_AGIRLIK // ne[kp['yer']] for kp in kp_g], np.int64)
    bil['yer_agirlikli'] = katman('yer ağırlıklı', tum, taban_w=tw, q99=False)
    out['bilgi'] = bil
    log('bilgi satırları bitti')
    # Marmara çevirisi (E3)
    out['marmara_cevirisi'] = ceviri(kir['n_y']['8'], out['ana'], S[ny == 8], S)
    # küme-pencere tablosu (S değerleri yalnız denetimler geçtikten sonra yazılır)
    out['kume_pencere_tablosu'] = [dict(T=kp['Ts'], la=kp['la'], lo=kp['lo'], n_y=len(yy[k]), n_r=len(rr[k]),
                                        S=float(s_), sinif=kp['sinif'], blok=list(kp['blok']))
                                   for kp, k, s_ in zip(kp_g, gk, S)]
    return out


def bf_hazirla(mc, kidx, yy, rr, hedef, ayar, log):
    """b_f* (Ö1): sw = 1,5 sabit; q95_N0(b_f) = q95_ölçülen. Nokta: tam yeniden hesapla ikiye bölme (1e-4).
    Bootstrap için b_f ızgarası: nokta x [1/3, 3] doğrusal, ayar.bf_izgara_n nokta; ızgara arası doğrusal ara değer."""
    yl = {k: yy[k] for k in kidx}; rl = {k: rr[k] for k in kidx}

    def q95(bf):
        d = mc_havuz_bf(mc, kidx, yl, rl, bf, ayar.surec)
        return float(nicelik(np.concatenate(d), 0.95)), d

    lo, hi = 0.0, 30.0
    qlo, _ = q95(lo)
    bayrak = None
    if hedef <= qlo:
        b = 0.0; bayrak = 'q95_olculen <= q95_N0(b_f=0)'
    else:
        qhi, _ = q95(hi)
        if hedef > qhi:
            b = hi; bayrak = 'q95_olculen > q95_N0(b_f=30)'
        else:
            while hi - lo > 1e-4:
                mid = 0.5 * (lo + hi)
                if q95(mid)[0] < hedef:
                    lo = mid
                else:
                    hi = mid
            b = 0.5 * (lo + hi)
    izg_b = np.linspace(b / 3, 3 * b, ayar.bf_izgara_n) if b > 0 else np.linspace(0, 3, ayar.bf_izgara_n)
    hv = []
    for bb in izg_b:
        dl = mc_havuz_bf(mc, kidx, yl, rl, float(bb), ayar.surec)
        v, s = havuz(dl)
        hv.append((v.astype(np.float32), s.astype(np.int32)))
    log(f'b_f* nokta {b:.4f}; ızgara {len(izg_b)} nokta hazır')
    return (b, bayrak), dict(b=izg_b, h=hv)


def G(D, x, m_r):
    return abs(math.atan(x / D) - m_r) / math.pi


def ceviri(k8, ana, S8, S):
    """INCELEME-1 E3. n_y = 8 katmanı (>= 300 KP değilse havuz)."""
    if k8.get('kume_pencere', 0) >= CEVIRI_KP_MIN:
        kat, ad, S50 = k8, 'n_y = 8', float(np.median(S8))
    else:
        kat, ad, S50 = ana, f'havuz (n_y = 8 katmanında {k8.get("kume_pencere", 0)} < 300 küme-pencere)', float(np.median(S))
    q95 = kat['q95']['nokta']; L8, U8 = kat['q95']['aralik']
    pay_alt = math.sqrt(max(L8 ** 2 - S50 ** 2, 0.0)); pay_nok = math.sqrt(max(q95 ** 2 - S50 ** 2, 0.0))
    tablo = []
    for geo, mr in G_MR:
        for D in G_D:
            for x in G_X:
                g = G(D, x, mr)
                tablo.append(dict(geometri=geo, m_r=mr, D=D, x=x, G=g, ds_alt=pay_alt / g, ds_nokta=pay_nok / g,
                                  ds_U=U8 / g))
    a = min(t['ds_alt'] for t in tablo)
    a_hucre = min(tablo, key=lambda t: t['ds_alt'])
    c = [t for t in tablo if t['geometri'] == 'dengeli' and t['D'] == 10.0 and t['x'] == 20.0][0]['ds_alt']
    cumle = ('Bu ölçüm ve bu model altında, yıl ölçekli GNSS hız değişimi alarmı Marmara benzeri geometride derin '
             f'kayma hızındaki {f2(a)} mm/yıl\'dan küçük değişimleri %5 yanlış alarm düzeyinde yarıdan fazla '
             f'olasılıkla göremez (alt sınır; temsilî geometride {f2(c)} mm/yıl). Karşılaştırma için Prens Adaları '
             'kesiminde yayımlanmış kayma açığı hızı 10–15 mm/yıl\'dır (Ergintav 2014, özetten).')
    if a >= O3_ESIK:
        o3 = ("GNSS yıl ölçekli alarm yolu bugünkü ağla Marmara'da kapalı (alt sınır en elverişli geometride bile "
              'kayma açığına ulaşıyor).')
    else:
        o3 = 'Bu ölçüm yolu kapatamadı. Bu hüküm yolun açık olduğu anlamına gelmez.'
    not_c = ("Marmara'ya özgü ön kayıt düşünülebilir (2017 sonrası veri hâlâ kör)." if c < C_ESIK else None)
    return dict(katman=ad, q95=q95, L8=L8, U8=U8, S50=S50, kok_L=pay_alt, kok_q95=pay_nok, tablo=tablo, a=a,
                a_hucre=dict((k, a_hucre[k]) for k in ('geometri', 'D', 'x')), c=c, yorum=cumle, o3=o3, c_notu=not_c,
                etiket='alt sınır: düşük sismisiteli bölge tabanı (sınıf A güç yok)')


# ===================================================================== yazma (tek koşu koruması)
def md_yap(s):
    L = ['# TR-11 sonuç', '']
    L.append(f'Hüküm: **{s["hukum"]}**')
    L.append('')
    if not s['ayar']['bagli_degerler']:
        L += ['**UYARI: bağlayıcı olmayan ayar (test koşusu).**', '']
    k = s['kapi']
    du = s['dusme']
    L += ['## Veri kapısı ve düşmeler', '',
          f'- Küme-pencere: listede {du["kume_pencere_liste"]}, geçerli {du["kume_pencere_gecerli"]}; yer {k["yer"]} '
          f'(eşik {k["esik"]["yer"]}), blok {k["blok"]} (eşik {k["esik"]["blok"]}).',
          f'- İndirme hatası: {len(du["indirme_hatasi_istasyon"])} istasyon (pay %{100 * du["indirme_hatasi_pay"]:.2f}).',
          f'- (istasyon, T) nedenleri: {du["istasyon_T_neden"]}',
          f'- Küme-pencere düşme nedenleri: {du["kume_pencere_neden"]}',
          f'- Okuma: {du["okuma"]}', '']
    if 'kod_denetimi' in s:
        kd = s['kod_denetimi']
        L += ['## Kod denetimi (gerçek S görülmeden)', '',
              f'- (i) yapay N0: q95 {f2(kd["i"]["q95_yapay"], 3)} / q95_N0 {f2(kd["i"]["q95_N0"], 3)} = '
              f'{f2(kd["i"]["oran"], 3)} (aralık [0,9, 1,1]; {"geçti" if kd["i"]["gecti"] else "KALDI"})',
              f'- (ii-b) yapay S düzeyi: ölçülen medyan(S_eklenen − S_özgün) {f2(kd["ii_b"]["olculen_medyan_fark"], 3)}, '
              f'm* {f2(kd["ii_b"]["m_yildiz"], 3)}, aralık {f2(kd["ii_b"]["aralik"], 3)} '
              f'({"geçti" if kd["ii_b"]["gecti"] else "KALDI"}; {kd["ii_b"]["secili_kume_pencere"]} seçili KP)']
        if 'ii_a' in kd:
            L.append(f'- (ii-a) gerçek, istasyon düzeyi: medyan(d_E) {f2(kd["ii_a"]["medyan_dE"], 4)} '
                     f'(aralık [2,95, 3,05]), medyan(|d_N|) {f2(kd["ii_a"]["medyan_abs_dN"], 4)} (< 0,05) '
                     f'({"geçti" if kd["ii_a"]["gecti"] else "KALDI"}; {kd["ii_a"]["istasyon_cifti"]} çift)')
        L.append('')
    if 'ana' in s:
        a = s['ana']
        L += ['## Ana ölçü (Ö1)', '',
              f'- q95 = {f2(a["q95"]["nokta"])} {f2(a["q95"]["aralik"])} mm/yıl (blok bootstrap, %90; KP '
              f'{a["kume_pencere"]}, yer {a["yer"]}, blok {a["blok"]})',
              f'- medyan {f2(a["q50"]["nokta"])} {f2(a["q50"]["aralik"])}; %90 {f2(a["q90"]["nokta"])} '
              f'{f2(a["q90"]["aralik"])}; %99 ' + (f'{f2(a["q99"]["nokta"])} {f2(a["q99"]["aralik"])}' if a.get('q99')
                                                   else 'yazılmaz (< 300 KP)'),
              f'- q95_N0 = {f2(a["q95_N0"], 3)}; ρ = {f2(a["rho"]["nokta"], 3)} {f2(a["rho"]["aralik"], 3)} '
              f'({s["rho_N0_konumu"]}; bilgi satırı)',
              f'- b_f* = {f2(a["bf_yildiz"]["nokta"], 3)} {f2(a["bf_yildiz"]["aralik"], 3)} mm/yıl^0,25 '
              f'(σ_w = 1,5 mm sabit)' + (f'; bayrak: {a["bf_yildiz"]["nokta_bayrak"]}' if a['bf_yildiz']['nokta_bayrak']
                                         else ''),
              f'- Kuyruk ρ₉₅/ρ₅₀ = {f2(a["kuyruk"]["nokta"], 3)} {f2(a["kuyruk"]["aralik"], 3)}'
              + (f' → {s["kuyruk_hukum"]}' if s.get('kuyruk_hukum') else ''),
              f'- N1 (bilgi): q95_N1 {f2(a["q95_N1"], 3)}; ρ_N1 {f2(a["rho_N1"]["nokta"], 3)} '
              f'{f2(a["rho_N1"]["aralik"], 3)}', '']
        L += ['## Kırılımlar', '', '| Katman | KP | Yer | Blok | q95 [L, U] | ρ [L, U] |', '|---|---|---|---|---|---|']
        for grup in ('n_y', 'sinif', 'epok'):
            for ad, t in s['kirilim'][grup].items():
                if t.get('hukum') == 'güç yok':
                    L.append(f'| {t["ad"]} | {t["kume_pencere"]} | {t["yer"]} | – | güç yok (< 30 yer) | – |')
                elif t.get('kume_pencere', 0) == 0:
                    L.append(f'| {t["ad"]} | 0 | – | – | – | – |')
                else:
                    L.append(f'| {t["ad"]} | {t["kume_pencere"]} | {t["yer"]} | {t["blok"]} | {f2(t["q95"]["nokta"])} '
                             f'{f2(t["q95"]["aralik"])} | {f2(t["rho"]["nokta"], 3)} {f2(t["rho"]["aralik"], 3)} |')
        L += ['', '## Bilgi satırları (hüküm vermez)', '']
        for ad in ('referans_farki_yok', 'yer_bootstrap', 'en_buyuk_blok_disarida', 'kod1_disarida', 'yer_agirlikli'):
            t = s['bilgi'][ad]
            if t.get('kume_pencere', 0) == 0:
                L.append(f'- {t["ad"]}: küme-pencere yok')
                continue
            L.append(f'- {t["ad"]}: KP {t["kume_pencere"]}; q95 {f2(t["q95"]["nokta"])} {f2(t["q95"]["aralik"])}; '
                     f'ρ {f2(t["rho"]["nokta"], 3)} {f2(t["rho"]["aralik"], 3)}')
        b = s['bilgi']['bilesen']
        for nm in ('ham', 'referans_farki'):
            L.append(f'- bileşen bazında ({nm}; {b["yakin_istasyon_kume_cifti"]} yakın istasyon): doğu medyan '
                     f'{f2(b[nm]["dogu"]["medyan"], 3)}, %95 {f2(b[nm]["dogu"]["q95"], 3)}, |.| %95 '
                     f'{f2(b[nm]["dogu"]["q95_mutlak"], 3)}; kuzey medyan {f2(b[nm]["kuzey"]["medyan"], 3)}, %95 '
                     f'{f2(b[nm]["kuzey"]["q95"], 3)}, |.| %95 {f2(b[nm]["kuzey"]["q95_mutlak"], 3)}')
        L.append(f'- N1: yukarıda (ana ölçü).')
        c = s['marmara_cevirisi']
        L += ['', '## Marmara çevirisi (E3; önceden sabit)', '',
              f'Katman: {c["katman"]}. q95 {f2(c["q95"])} [L₈ {f2(c["L8"])}, U₈ {f2(c["U8"])}], S50 {f2(c["S50"])}; '
              f'√(L₈² − S50²) = {f2(c["kok_L"], 3)}. Etiket: {c["etiket"]}.', '',
              '| Geometri | D (km) | x (km) | G | Δs_alt | nokta √(q95²−S50²)/G | U₈/G |', '|---|---|---|---|---|---|---|']
        for t in c['tablo']:
            L.append(f'| {t["geometri"]} | {t["D"]:.0f} | {t["x"]:.0f} | {f2(t["G"], 3)} | {f2(t["ds_alt"])} | '
                     f'{f2(t["ds_nokta"])} | {f2(t["ds_U"])} |')
        L += ['', f'a = {f2(c["a"])} mm/yıl ({c["a_hucre"]}); c (dengeli, D = 10, x = 20) = {f2(c["c"])} mm/yıl.', '',
              f'> {c["yorum"]}', '', f'İstanbul kuralı (Ö3): {c["o3"]}' + (f' {c["c_notu"]}' if c['c_notu'] else ''),
              '', 'TR-11 hiçbir durumda "yol açık" hükmü vermez. Sonuç bir olasılık terimi değildir.', '']
    L += ['## Girdiler (sha256)', '', f'- küme listesi: {s["girdi"]["liste_sha256"]}']
    for ad, h in {**s['girdi']['ustveri_sha256'], **s['girdi']['tr2_sha256']}.items():
        L.append(f'- {ad}: {h}')
    L += [f'- indirme manifesti: {s["girdi"]["indirme_manifesti_sha256"]} ({len(s["girdi"]["tenv3_sha256"])} tenv3 '
          'dosyası; tek tek sha256 değerleri JSON\'da)',
          f'- Ö4 istasyonları (Marmara kutusuna < 150 km): {", ".join(s["o4"]["istasyonlar"])}; {s["o4"]["kural"]}.']
    return '\n'.join(L) + '\n'


def yaz(a, sonuc, o4, log):
    js = json.dumps(sonuc, ensure_ascii=False, indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o))
    md = md_yap(sonuc)
    yj, ym = os.path.join(a.cikti, 'tr11_sonuc.json'), os.path.join(a.cikti, 'tr11_sonuc.md')
    with open(yj, 'x') as f:
        f.write(js)
    with open(ym, 'x') as f:
        f.write(md)
    log(f'yazıldı: {yj}, {ym}; hüküm: {sonuc["hukum"]}')
    if getattr(a, 'o4_sil', True) and sonuc['hukum'] != 'geçersiz (kod)':
        for s in o4:
            p = os.path.join(a.tenv3, f'{s}.tenv3')
            if os.path.exists(p):
                os.remove(p)
                log(f'Ö4: {p} silindi (sha256 manifestte ve sonuçta)')
    return sonuc


def arguman(argv=None):
    p = argparse.ArgumentParser(description='TR-11 tek koşu')
    p.add_argument('--tenv3', required=True, help='indirilen tenv3 dizini ({STA}.tenv3)')
    p.add_argument('--manifest', default=None, help='indirme manifesti (varsayılan <tenv3>/tr11_indirme_manifest.json)')
    p.add_argument('--ustveri', default='/mnt/project-files/turetme/tr11-ustveri')
    p.add_argument('--tr2', required=True, help='TR-2 ComCat ham dizini (m6_havuz.csv, birincil_aday*.csv, mekanizma.jsonl)')
    p.add_argument('--liste', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tr11_kume_listesi.json'))
    p.add_argument('--cikti', default=os.path.dirname(os.path.abspath(__file__)))
    p.add_argument('--surec', type=int, default=4)
    p.add_argument('--yalniz-denetim', action='store_true')
    a = p.parse_args(argv)
    if a.manifest is None:
        a.manifest = os.path.join(a.tenv3, 'tr11_indirme_manifest.json')
    a.o4_sil = True
    return a


def main(argv=None):
    a = arguman(argv)
    try:
        kos(a, Ayar(surec=a.surec))
    except KosuDur as e:
        print(f'KOŞU DURDU: {e}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
