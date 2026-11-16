#!/usr/bin/env python3
"""TR-7b Tur 3: kaynağın yerine dayanan sızıntı kuralı K6, YALNIZ YAPAY VERİ (ön kayıt taslağı §12).

`tr7b_yapay.py` (Tur 1), `tr7b_yapay2.py` (Tur 2) ve TR-7 `tr7_cekirdek.py` DEĞİŞTİRİLMEDEN içe aktarılır.

Üreteç farkı (Tur 1–2'ye göre): istasyonlar arası gecikmeler gerçek geometriyle kurulur.
  İstasyonlar: TR-7 Parkfield listesinin `ilk12` istasyonları ize göre (birinci temel bileşen) güneyden kuzeye
  sıralanır, 0, 2, 4, 6, 8, 10. sıradakiler alınır (6 istasyon: PTR, PSN, PGH, PHF, PL11B, PPT; ≈ 75 km açıklık).
  Tremor: kaynak iz üzerinde düzgün dağılımlı bir noktanın U[20, 25] km altında; gecikme r_i / 3,5 km/s.
  Bölgesel koda (D7d, Y3): dış merkez dizi ortasından U[20, 150] km, azimut U[0, 360), derinlik 10 km; r_i / 3,5 km/s.
  Telesismik sinyal (Y1–Y3, F2): düzlem dalga, dizi doğrultusunda görünür hız U[8, 25] km/s, yönü rastgele (±);
    zarf e(t) her istasyonda gecikmeli (taşıyıcılar bağımsız, Tur 1 ile aynı).
  Gecikmeler zarfa FS örneklemede doğrusal ara değerlemeyle uygulanır. Genlikler istasyonlar arası eşittir (1/r yok).
  Gecikme ölçüm gürültüsü ayrıca eklenmez: gecikmeler gürültülü yapay zarflardan ölçülür.

K6 (küme düzeyi; simetrik, her pencerede aynı hesap):
  1. Kümenin her istasyon çifti (i, j) için I üzerinde (maskesiz, tanımlı saniyeler) Pearson(L_i(t), L_j(t + k)),
     k = −10…+10 sn; en büyük değer ≥ 0,5 ise çift kullanılır; gecikme τ_ij = k* + parabolik ara değerleme
     (k* ± 1 komşularıyla; k* uçtaysa ara değerleme yok).
  2. Kullanılan çift ≥ 3 ve kapsanan istasyon ≥ 3 değilse konum "belirsiz" → telesismik sayılmaz.
  3. (a) Düzlem dalga, dizi doğrultusunda: τ_ij = s (u_j − u_i), en küçük kareler; RMS_a; v_a = 1/|s|.
     (b) Yerel kaynak: iz üzerinde −10 … +10 km uzatılmış, 1 km adımlı noktalar × derinlik {15, 20, 25} km,
         v = 3,5 km/s; τ_ij = (r_j − r_i)/v; RMS_b = ızgaradaki en küçük.
  4. Konum telesismik ⇔ RMS_a ≤ 1,0 sn (düzlem dalga gerçekten uyuyor; 1 Hz zarf çözünürlüğü) VE RMS_a < RMS_b
     VE v_a ≥ 6 km/s.
  5. Küme sızıntı nedeniyle atılır ⇔ konum telesismik VEYA istasyonların ≥ yarısında sönüm şartı
     (Δ_d ≥ Δ_y VE ρ(L, zaman) ≤ −0,7; Tur 2 ile aynı).
  Darbe ve taban kuralları TR-7 aynen.

Satırlar ve şartlar: Tur 2 (§11.2) ile aynı, aynı eşikler; ayrıca üreteç denetimi: D7, D7b ×3, D7c ×2, D7d satırları
aynı 6 istasyonla gecikmesiz de koşulur ("gecikmesiz" son ekli satırlar).

Kullanım: python3 -I -B tr7b_yapay3.py <tohum> <n_pencere> <çıktı.json> [bölüm: hepsi|1|2]
"""
import csv, json, math, os, sys
import numpy as np

sys.dont_write_bytecode = True
BURADA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURADA)
import tr7b_yapay as Y       # noqa: E402
import tr7b_yapay2 as Y2     # noqa: E402  (K4, K5 ve sönüm; Y.KURALLAR'a K4, K5'i ekler)
c = Y.c

V_S = 3.5
IZ = [(-120.80, 36.20), (-120.50, 35.97), (-120.35, 35.83), (-120.20, 35.65)]
LA0 = sum(p[1] for p in IZ) / 4
LO0 = sum(p[0] for p in IZ) / 4
KX = math.cos(math.radians(LA0)) * 111.195


def xy(lo, la):
    return np.array([(lo - LO0) * KX, (la - LA0) * 111.195])


def _istasyonlar_geo():
    rows = [r for r in csv.DictReader(open(os.path.join(BURADA, '..', 'tr7', 'tr7_parkfield_liste.csv')))
            if r['ilk12'].strip() == '1']
    P = np.array([xy(float(r['boylam']), float(r['enlem'])) for r in rows])
    m = P.mean(0)
    _, _, vt = np.linalg.svd(P - m)
    yon = vt[0] if vt[0][1] > 0 else -vt[0]              # kuzeye bakan birinci temel bileşen
    u = (P - m) @ yon
    sira = np.argsort(u)
    sec = sira[::2]
    return [rows[i]['ag'] + '.' + rows[i]['istasyon'] for i in sec], P[sec], u[sec], yon, m


ADLAR, PXY, U, YON, MERKEZ = _istasyonlar_geo()
IZXY = np.array([xy(lo, la) for lo, la in IZ])


def _iz_noktalari(adim=1.0, uzat=10.0):
    seg = np.diff(IZXY, axis=0)
    uz = np.hypot(seg[:, 0], seg[:, 1])
    L = uz.sum()
    out = []
    for s in np.arange(-uzat, L + uzat + 1e-9, adim):
        if s < 0:
            out.append(IZXY[0] + seg[0] / uz[0] * s)
            continue
        if s > L:
            out.append(IZXY[-1] + seg[-1] / uz[-1] * (s - L))
            continue
        k, acc = 0, 0.0
        while k < len(uz) - 1 and acc + uz[k] < s:
            acc += uz[k]
            k += 1
        out.append(IZXY[k] + seg[k] / uz[k] * (s - acc))
    return np.array(out), L


IZ_GRID, IZ_L = _iz_noktalari()
DERINLIK = (15.0, 20.0, 25.0)
RMS_UST = 1.0


def gecik_tremor(rng):
    nok, _ = _iz_noktalari(adim=0.1, uzat=0.0)
    p = nok[rng.integers(len(nok))]
    z = rng.uniform(20, 25)
    r = np.sqrt(((PXY - p) ** 2).sum(1) + z * z)
    return r / V_S


def gecik_koda(rng):
    d, az = rng.uniform(20, 150), rng.uniform(0, 2 * np.pi)
    p = MERKEZ + d * np.array([np.sin(az), np.cos(az)])
    r = np.sqrt(((PXY - p) ** 2).sum(1) + 100.0)
    return r / V_S


def gecik_tele(rng):
    v = rng.uniform(8, 25) * (1 if rng.random() < 0.5 else -1)
    return (U - U.min()) / v


def kaydir(e, d):
    return np.interp(Y.t - d, Y.t, e, left=0.0, right=e[-1])


def istasyonlar(rng, gtur='gauss', tremor=None, dtr=None, A=0.0, sekil=None, norm=None, tele=None, dtel=None):
    n_ist = len(PXY)
    st = []
    for i in range(n_ist):
        env = None if tremor is None else (tremor if dtr is None else kaydir(tremor, dtr[i]))
        nrm = None if norm is None else (norm if dtr is None else kaydir(norm.astype(float), dtr[i]) > 0.5)
        tl = None
        if tele is not None:
            ey, ed, ay, ka = tele
            tl = (ey, ed, ay, ka) if dtel is None else (kaydir(ey, dtel[i]), kaydir(ed, dtel[i]), ay, ka)
        st += Y2.istasyonlar(rng, gtur=gtur, tremor=env, A=A, sekil=sekil, norm=nrm, tele=tl, n_ist=1)
    return st


# ------------------------------------------------------------------ K6
def _gecikme(x, y, g):
    best, kb, cs = -2.0, None, {}
    n = len(x)
    for k in range(-c.LAG, c.LAG + 1):
        if k >= 0:
            a, b, gg = x[:n - k], y[k:], g[:n - k] & g[k:]
        else:
            a, b, gg = x[-k:], y[:n + k], g[-k:] & g[:n + k]
        a, b = a[gg], b[gg]
        if len(a) > 10 and a.std() > 0 and b.std() > 0:
            r = float(np.corrcoef(a, b)[0, 1])
            cs[k] = r
            if r > best:
                best, kb = r, k
    if kb is None or best < c.KORR:
        return None
    t = float(kb)
    if (kb - 1) in cs and (kb + 1) in cs:
        y0, y1, y2 = cs[kb - 1], cs[kb], cs[kb + 1]
        den = y0 - 2 * y1 + y2
        if den < 0:
            t += 0.5 * (y0 - y2) / den
    return t


def konum(ist, uy, I, maske, idx):
    """Dönüş: (telesismik mi, RMS_a, RMS_b, v_a, çift sayısı). idx: küme üyesinin istasyon geometri dizini."""
    lo, hi = I
    g0 = ~maske[lo:hi]
    ciftler = []
    for a in range(len(uy)):
        for b in range(a + 1, len(uy)):
            xa, xb = ist[uy[a]]['L'][lo:hi], ist[uy[b]]['L'][lo:hi]
            g = g0 & np.isfinite(xa) & np.isfinite(xb)
            t = _gecikme(np.where(g, xa, 0), np.where(g, xb, 0), g)
            if t is not None:
                ciftler.append((idx[uy[a]], idx[uy[b]], t))
    kaps = {i for p in ciftler for i in p[:2]}
    if len(ciftler) < 3 or len(kaps) < 3:
        return False, None, None, None, len(ciftler)
    i_, j_, t_ = (np.array([p[0] for p in ciftler]), np.array([p[1] for p in ciftler]),
                  np.array([p[2] for p in ciftler]))
    du = U[j_] - U[i_]
    s = float((t_ * du).sum() / (du * du).sum()) if (du * du).sum() > 0 else 0.0
    rms_a = float(np.sqrt(np.mean((t_ - s * du) ** 2)))
    v_a = float('inf') if s == 0 else 1 / abs(s)
    rms_b = 1e9
    for z in DERINLIK:
        r = np.sqrt(((PXY[None, :, :] - IZ_GRID[:, None, :]) ** 2).sum(2) + z * z) / V_S   # nokta × istasyon
        pred = r[:, j_] - r[:, i_]
        rms_b = min(rms_b, float(np.sqrt(np.mean((t_[None, :] - pred) ** 2, axis=1)).min()))
    return bool(rms_a <= RMS_UST and rms_a < rms_b and v_a >= 6.0), rms_a, rms_b, v_a, len(ciftler)


def degerlendir(st, maske=None, ilgi=None):
    maske = np.zeros(Y.T, bool) if maske is None else maske
    ist = [c.istasyon(Cy, Cd, Y.R_IX, Y.W_IX, maske) for Cy, Cd in st]
    ks = c.kumeler(ist, maske, Y.W_IX)
    if ilgi is not None:
        ks = [k for k in ks if k['Ip'][0] < ilgi[1] and k['Ip'][1] > ilgi[0]]
    if not ks:
        return None, 0, 0
    idx = list(range(len(ist)))
    out = {}
    tam = {k: False for k in list(Y.KURALLAR) + ['K6']}
    siz = {k: False for k in tam}
    n_tele = 0
    for k in ks:
        uy = k['uyeler']
        pk = {i: [(a, b) for ii, a, b in k['parcalar'] if ii == i] for i in uy}
        yarim = len(uy) / 2
        d = sum(c.darbe_ist(ist[i]['Cy'], pk[i]) for i in uy) >= yarim
        tb = sum(c.taban_ist(ist[i], pk[i], maske) for i in uy) >= yarim
        for ad, kural in Y.KURALLAR.items():
            s = sum(kural(ist[i], pk[i], maske, Y.Q_IX) for i in uy) >= yarim
            tam[ad] |= not (d or s or tb)
            siz[ad] |= not s
        tele = konum(ist, uy, k['I'], maske, idx)[0]
        n_tele += tele
        son = sum(Y2.sonum(ist[i], Y.secili(ist[i], pk[i], maske)) if Y.secili(ist[i], pk[i], maske).any() else False
                  for i in uy) >= yarim
        s6 = tele or son
        tam['K6'] |= not (d or s6 or tb)
        siz['K6'] |= not s6
    for ad in tam:
        out[ad] = (not tam[ad], not siz[ad])
    return out, len(ks), n_tele


def satir(rng, n, uret):
    kur = list(Y.KURALLAR) + ['K6']
    alg, at = 0, {k: [0, 0] for k in kur}
    nk = nt = 0
    for _ in range(n):
        st, ilgi = uret(rng)
        r, a, b = degerlendir(st, ilgi=ilgi)
        if r is None:
            continue
        alg += 1
        nk += a
        nt += b
        for k, (a1, a2) in r.items():
            at[k][0] += a1
            at[k][1] += a2
    out = dict(n=n, n_alg=alg, algilama=round(alg / n, 3), kume=nk, kume_konum_tele=nt)
    for k, v in at.items():
        out[f'{k}_atilma_tam'] = round(v[0] / alg, 3) if alg else None
        out[f'{k}_atilma_sizinti'] = round(v[1] / alg, 3) if alg else None
        out[f'{k}_sag'] = round((alg - v[0]) / n, 3)
    return out


def main():
    tohum, n, cikti = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    bolum = sys.argv[4] if len(sys.argv) > 4 else 'hepsi'
    rng = np.random.default_rng(tohum if bolum in ('hepsi', '1') else tohum + 1000003)

    def tr(tur, A, sekil=None, gec=True):
        def u(rng):
            b = Y.bas_w(rng)
            env = Y.zarf_yarim(b) if tur == 'yarim' else Y.zarf_patlama(rng, b)
            return istasyonlar(rng, tremor=env, dtr=gecik_tremor(rng) if gec else None, A=A, sekil=sekil), None
        return u

    def koda(gec=True):
        def u(rng):
            env, norm = Y2.koda_zarf(Y.bas_w(rng))
            return istasyonlar(rng, tremor=env, dtr=gecik_koda(rng) if gec else None, A=20.0, sekil=Y.KODA,
                               norm=norm), None
        return u

    def y1(A, ay, ka, bicim):
        def u(rng):
            ey, e = Y2.tele_zarf(rng, bicim)
            b = Y.bas_w(rng)
            return istasyonlar(rng, tremor=Y.zarf_yarim(b), dtr=gecik_tremor(rng), A=A, tele=(ey, e, ay, ka),
                               dtel=gecik_tele(rng)), (b, b + 300)
        return u

    def y2(ay, ka, bicim):
        def u(rng):
            ey, e = Y2.tele_zarf(rng, bicim)
            return istasyonlar(rng, tele=(ey, e, ay, ka), dtel=gecik_tele(rng)), None
        return u

    def y3(ay):
        def u(rng):
            ey, e = Y2.tele_zarf(rng, 'egim')
            env, norm = Y2.koda_zarf(Y.bas_w(rng))
            return istasyonlar(rng, tremor=env, dtr=gecik_koda(rng), A=20.0, sekil=Y.KODA, norm=norm,
                               tele=(ey, e, ay, 12.5), dtel=gecik_tele(rng)), None
        return u

    def f(tele):
        def u(rng):
            if tele:
                ey, e = Y2.tele_zarf(rng, 'egim')
                return istasyonlar(rng, gtur='kentsel', tele=(ey, e, 10, 12.5), dtel=gecik_tele(rng)), None
            return istasyonlar(rng, gtur='kentsel'), None
        return u

    b1 = [('D7 yarım A10', tr('yarim', 10.0))]
    b1 += [(f'D7b patlama A{A}', tr('patlama', float(A))) for A in (3, 10, 30)]
    b1 += [(f'D7c düz A{A}', tr('yarim', float(A), Y.DUZ)) for A in (3, 10)]
    b1 += [('D7d koda x20', koda())]
    b1 += [('D7 yarım A10 gecikmesiz', tr('yarim', 10.0, gec=False))]
    b1 += [(f'D7b patlama A{A} gecikmesiz', tr('patlama', float(A), gec=False)) for A in (3, 10, 30)]
    b1 += [(f'D7c düz A{A} gecikmesiz', tr('yarim', float(A), Y.DUZ, gec=False)) for A in (3, 10)]
    b1 += [('D7d koda x20 gecikmesiz', koda(gec=False))]
    b1 += [(f'Y1 A{A} a_y{ay} κ12.5 egim', y1(float(A), ay, 12.5, 'egim')) for A in (3, 10) for ay in (2, 5, 10)]
    b1 += [(f'Y1 A{A} a_y10 κ12.5 sabit', y1(float(A), 10, 12.5, 'sabit')) for A in (3, 10)]
    b2 = [(f'Y2 a_y{ay} κ{ka} {b}', y2(ay, ka, b)) for ay in (2, 5, 10) for ka in (6, 12.5, 25)
          for b in ('egim', 'sabit')]
    b2 += [(f'Y3 koda x20 + tele a_y{ay}', y3(ay)) for ay in (2, 5, 10)]
    b2 += [('F1 tetikleyicisiz kentsel', f(False)), ('F2 tetikleyicili kentsel', f(True))]
    isler = b1 + b2 if bolum == 'hepsi' else b1 if bolum == '1' else b2
    sonuc = {}
    for ad, u in isler:
        sonuc[ad] = satir(rng, n, u)
        print(ad, json.dumps(sonuc[ad], ensure_ascii=False), flush=True)
    json.dump(dict(tohum=tohum, bolum=bolum, n=n, istasyonlar=ADLAR, satirlar=sonuc), open(cikti, 'w'),
              ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
