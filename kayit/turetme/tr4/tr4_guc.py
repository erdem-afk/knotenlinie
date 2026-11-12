#!/usr/bin/env python3
"""TR-4 ön kayıt taslağı (sürüm 1): örnekleme tasarımlarının yapay veriyle sınanması ve σ_Δ / q95 kesinliği.

Gerçek dalga formu YOK. Zincir TR-5b'nin dondurulmuş başvuru uygulamasıdır (`kayit/turetme/tr5/tr5b_yapay.py`:
`bant_gurultu`, `ger`, `zincir`, `ay_esle`, `gun_ay`; `tr5b_yapay2.py`: `pk_istasyon`, SNR düzeyleri). Bu betik o
dosyaları değiştirmez; yalnız günlük ÇİF'lerin hangi günlerde ve kaç saatle oluştuğunu (örnekleme) değiştirir.

Kipler (python3 -I -B tr4_guc.py <kip>):
  olcum      (A) Örnekleme tasarımı başına ölçüm gürültüsü σ_ölçüm (H0: yalnız %0,05 mevsimsel), geçerli Δ oranı ve
             −%0,1 ekleme oranı (TR-5b E2 ölçütü). 3 SNR × tasarımlar × N_TEKRAR. Çıktı: tr4_guc_sonuc.json → olcum
  kesinlik   (B) σ̂_Δ (1,4826·MAD) ve q95|Δ| kestiriminin kesinliği; iki yönlü (istasyon × C yılı) bootstrap aralığı;
             (c) etiketinin olasılıkları. Gerçek istasyon-pencere deseni tr4_pencereler.csv'den. → kesinlik
  pk         (C) Nisan 2025 M6,2 pozitif kontrolü (tek istasyon, KO.SLVT, 44 km): δ_ko'nun saptama olasılığı. → pk
  ref <npz>  (D) Dondurulmuş TR-5b yapay ÇİF'lerinin (tr5b_yapay_ccf.npz) TR-4 gün örneklemesiyle başvuru Δ'ları
             → tr4_yapay_ref.json (TR-4 koşu kodunun 1. adım denetimi için)
Tohumlar: olcum 20261201, kesinlik 20261202, pk 20261203 (her iş için sha256'dan türetilir).
"""
import hashlib, importlib.util, json, math, os, sys, time, datetime as dt
import numpy as np

BURASI = os.path.dirname(os.path.abspath(__file__))
TR5 = os.path.join(BURASI, '..', 'tr5')


def _yukle(ad):
    sp = importlib.util.spec_from_file_location(ad, os.path.join(TR5, ad + '.py'))
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


YP = _yukle('tr5b_yapay')
YP2 = _yukle('tr5b_yapay2')
SNR = YP2.SNR                                   # 4 saatlik günün SNR'si (CC10 ≈ 0,5 / 0,7 / 0,9)
GUNLER = np.arange(-YP.TABAN_GUN, 0)
SONUC = os.path.join(BURASI, 'tr4_guc_sonuc.json')

# örnekleme tasarımları: (ayda gün bloğu 1..d ya da None = her gün, saat/gün, gün için en az kabul edilen saat)
TASARIM = {
    'A_her_gun_4s': (None, 4, 2), 'H_her_gun_3s': (None, 3, 2), 'B_her_gun_2s': (None, 2, 2),
    'C_20g_4s': (20, 4, 2), 'G_20g_3s': (20, 3, 2), 'D_20g_2s': (20, 2, 2),
    'F_16g_4s': (16, 4, 2), 'E_16g_2s': (16, 2, 2),
    'Y_her_gun_1s_zincir_disi': (None, 1, 1),
}
SAAT_RED, GUN_KESINTI = 0.10, 0.10              # saat başına bağımsız ret (tamlık + enerji reddi); gün kesintisi
N_TEKRAR = 100


def tohum(*p): return int(hashlib.sha256('|'.join(map(str, p)).encode()).hexdigest()[:8], 16)


def json_yaz(anahtar, deger):
    d = json.load(open(SONUC)) if os.path.exists(SONUC) else {}
    d[anahtar] = deger
    json.dump(d, open(SONUC, 'w'), ensure_ascii=False, indent=1)


# ============================================================== (A) ölçüm gürültüsü, örnekleme başına
def seri_ornekli(rng, snr4, eps_gercek, gun_ayi, d, h, hmin):
    """Günlük ÇİF: G(τ(1+ε)) + gürültü/(snr4·√(n_saat/4)); geçerli gün: kesinti yok, örneklenmiş, n_saat >= hmin."""
    zarf = np.exp(-np.abs(YP.tau) / 20.0)
    G = YP.bant_gurultu(rng, 1)[0] * zarf; G /= np.sqrt(np.mean(G[YP.koda] ** 2))
    n = len(eps_gercek)
    acik = rng.random(n) > GUN_KESINTI
    b = rng.integers(0, n - 30); acik[b:b + 30] = False
    ns = rng.binomial(h, 1 - SAAT_RED, n)
    orn = np.ones(n, bool) if d is None else (gun_ayi <= d)
    gec = acik & orn & (ns >= hmin)
    ccf = np.zeros((n, len(YP.tau)))
    ix = np.nonzero(gec)[0]
    gur = YP.bant_gurultu(rng, len(ix))
    for j, i in enumerate(ix):
        ccf[i] = YP.ger(G, eps_gercek[i]) + gur[j] / (snr4 * math.sqrt(ns[i] / 4.0))
    return ccf, gec


def _olcum_is(arg):
    ad, sn, k = arg
    d, h, hmin = TASARIM[ad]
    rng = np.random.default_rng(tohum('tr4-olcum', 20261201, ad, sn, k))
    T_ord = 737000 + int(rng.integers(0, 365))
    ay = YP.gun_ay(T_ord, GUNLER)
    gun_ayi = np.array([dt.date.fromordinal(T_ord + int(g)).day for g in GUNLER])
    faz = rng.uniform(0, 2 * np.pi)
    e = 5e-4 * np.sin(2 * np.pi * GUNLER / 365.25 + faz)
    ccf, gec = seri_ornekli(rng, SNR[sn], e, gun_ayi, d, h, hmin)
    D0 = YP.ay_esle(YP.zincir(ccf, gec, GUNLER, 0), GUNLER, ay)
    ccf2 = ccf.copy()
    for i in np.nonzero((GUNLER >= -365) & gec)[0]: ccf2[i] = YP.ger(ccf[i], -1e-3)
    D2 = YP.ay_esle(YP.zincir(ccf2, gec, GUNLER, 0), GUNLER, ay)
    return ad, sn, D0, D2, float(gec.mean())


def olcum():
    t0 = time.time()
    isler = [(ad, sn, k) for ad in TASARIM for sn in SNR for k in range(N_TEKRAR)]
    import multiprocessing as mp
    with mp.get_context('fork').Pool(4) as p:
        R = p.map(_olcum_is, isler, chunksize=4)
    out = {}
    for ad in TASARIM:
        for sn in SNR:
            x = [(a, b, g) for a_, s_, a, b, g in R if a_ == ad and s_ == sn]
            D0 = np.array([v[0] for v in x]); D2 = np.array([v[1] for v in x]); g = np.array([v[2] for v in x])
            ok = ~np.isnan(D0); ok2 = ok & ~np.isnan(D2)
            oran = (D2[ok2] - D0[ok2]) / -1e-3
            out[f'{ad}|{sn}'] = dict(
                n=len(x), gecerli_delta_orani=round(float(ok.mean()), 3), gecerli_gun_orani=round(float(g.mean()), 3),
                sigma_olcum_yuzde=round(float(np.std(D0[ok])) * 100, 4) if ok.sum() > 2 else None,
                ort_delta_yuzde=round(float(np.mean(D0[ok])) * 100, 4) if ok.any() else None,
                oran_medyan=round(float(np.median(oran)), 3) if len(oran) else None,
                oran_q05=round(float(np.quantile(oran, 0.05)), 3) if len(oran) else None,
                oran_q95=round(float(np.quantile(oran, 0.95)), 3) if len(oran) else None)
            print(ad, sn, out[f'{ad}|{sn}'], flush=True)
    json_yaz('olcum', dict(tasarim={k: dict(ayda_gun=v[0], saat=v[1], gun_icin_en_az_saat=v[2]) for k, v in TASARIM.items()},
                           saat_red=SAAT_RED, gun_kesinti=GUN_KESINTI, n_tekrar=N_TEKRAR, mevsim_yuzde=0.05,
                           sonuc=out, sure_sn=round(time.time() - t0)))


# ============================================================== (B) σ̂_Δ ve q95 kesinliği
def desen(tset=None, ist_kes=None):
    import csv
    hucre = []
    for r in csv.DictReader(open(os.path.join(BURASI, 'tr4_pencereler.csv'))):
        if r['ana_T'] != 'True' or r['DOLU_ana'] != 'True' or r['sakin_ana'] != 'True': continue
        y = int(r['T'][:4])
        if tset and y not in tset: continue
        hucre.append((r['ist'], y))
    ist = sorted({s for s, _ in hucre})
    if ist_kes: ist = ist[::2][:ist_kes] if ist_kes < len(ist) else ist
    hucre = [(s, y) for s, y in hucre if s in ist]
    return hucre


def kestir(v):
    v = np.asarray(v)
    return 1.4826 * np.median(np.abs(v - np.median(v))), np.quantile(np.abs(v), 0.95)


def bootstrap(hucre_s, hucre_y, v, rng, B):
    S = np.unique(hucre_s); Y = np.unique(hucre_y)
    si = np.searchsorted(S, hucre_s); yi = np.searchsorted(Y, hucre_y)
    ms = rng.multinomial(len(S), np.ones(len(S)) / len(S), size=B)      # (B, S) çokluk
    my = rng.multinomial(len(Y), np.ones(len(Y)) / len(Y), size=B)
    w = ms[:, si] * my[:, yi]                                            # (B, hücre)
    sig = np.empty(B); q = np.empty(B)
    for b in range(B):
        x = np.repeat(v, w[b])
        if len(x) < 5: sig[b] = q[b] = np.nan; continue
        sig[b], q[b] = kestir(x)
    return np.nanquantile(sig, [0.05, 0.95]), np.nanquantile(q, [0.05, 0.95])


def benzet(hucre, sigma, rho, phi, kuyruk, s_olc, p_gec, rng, B):
    ist = sorted({s for s, _ in hucre}); yillar = list(range(2012, 2025))
    ny = len(yillar)

    def ar1(n_seri):
        x = np.empty((n_seri, ny)); x[:, 0] = rng.standard_normal(n_seri)
        for j in range(1, ny): x[:, j] = phi * x[:, j - 1] + math.sqrt(1 - phi ** 2) * rng.standard_normal(n_seri)
        return x
    C = ar1(1)[0]
    if kuyruk == 't4':
        U = rng.standard_t(4, (len(ist), ny)) / math.sqrt(2.0)        # t4, birim varyans, yıllar bağımsız (φ = 0)
    else:
        U = ar1(len(ist))
    L = math.sqrt(rho) * C[None, :] + math.sqrt(1 - rho) * U
    olcek = sigma / math.sqrt(1.5 - phi / 2 - phi ** 2)          # Var[L(T-1) - (L(T-2)+L(T-3))/2], AR(1)
    v, hs, hy = [], [], []
    for s, y in hucre:
        if rng.random() > p_gec: continue
        i = ist.index(s); j = yillar.index(y - 1)
        env = (L[i, j] - 0.5 * (L[i, j - 1] + L[i, j - 2])) * olcek
        v.append(env + s_olc * rng.standard_normal()); hs.append(i); hy.append(y)
    v = np.array(v); hs = np.array(hs); hy = np.array(hy)
    if len(v) < 10: return None
    sh, qh = kestir(v)
    (sl, su), (ql, qu) = bootstrap(hs, hy, v, rng, B)
    return len(v), len(set(hs)), len(set(hy)), sh, qh, sl, su, ql, qu


def gercek_deger(sigma, rho, phi, kuyruk, s_olc, rng, n=400000):
    """Popülasyon σ (1,4826·MAD) ve q95|Δ|: aynı modelden büyük örnek."""
    if kuyruk == 't4':
        U = rng.standard_t(4, (n, 3)) / math.sqrt(2.0)
        C = rng.standard_normal((n, 3))
        L = math.sqrt(rho) * C + math.sqrt(1 - rho) * U
        olcek = sigma / math.sqrt(1.5)
    else:
        # AR(1) yıllık düzey: 3 ardışık yıl
        x0 = rng.standard_normal(n); x1 = phi * x0 + math.sqrt(1 - phi ** 2) * rng.standard_normal(n)
        x2 = phi * x1 + math.sqrt(1 - phi ** 2) * rng.standard_normal(n)
        L = np.stack([x0, x1, x2], 1); olcek = sigma / math.sqrt(1.5 - phi / 2 - phi ** 2)
    env = (L[:, 2] - 0.5 * (L[:, 1] + L[:, 0])) * olcek
    v = env + s_olc * rng.standard_normal(n)
    return kestir(v)


def kesinlik():
    t0 = time.time()
    ol = json.load(open(SONUC)).get('olcum', {}).get('sonuc', {})
    def so(ad): return ol[f'{ad}|CC10~0,5']['sigma_olcum_yuzde'] / 100, ol[f'{ad}|CC10~0,5']['gecerli_delta_orani']
    DES = {'tam (T 2017-2024, bütün dolu)': desen(),
           'örtüşmeyen T 2018/2021/2024': desen({2018, 2021, 2024}),
           'yalnız T 2021-2024': desen({2021, 2022, 2023, 2024}),
           'istasyonların yarısı': desen(ist_kes=11)}
    SIG = [0.0005, 0.001, 0.0015, 0.002, 0.003]
    SEN = [(0.0, 0.0, 'normal'), (0.3, 0.0, 'normal'), (0.6, 0.0, 'normal'), (0.3, 0.5, 'normal'), (0.3, 0.0, 't4')]
    TAS = ['A_her_gun_4s', 'C_20g_4s']
    R, B = 200, 300
    out = {}
    for dad, h in DES.items():
        for tas in TAS:
            if dad != 'tam (T 2017-2024, bütün dolu)' and tas != 'C_20g_4s': continue
            s_olc, p_gec = so(tas)
            p_gec = p_gec * 0.9      # gün doluluğu ve aygıt (yatay) kaybı için ek %10 (varsayım)
            for rho, phi, kuy in SEN:
                if dad != 'tam (T 2017-2024, bütün dolu)' and (rho, phi, kuy) != (0.3, 0.0, 'normal'): continue
                for sg in SIG:
                    rng = np.random.default_rng(tohum('tr4-kesinlik', 20261202, dad, tas, rho, phi, kuy, sg))
                    sg_g, q_g = gercek_deger(sg, rho, phi, kuy, s_olc, rng)
                    res = [benzet(h, sg, rho, phi, kuy, s_olc, p_gec, rng, B) for _ in range(R)]
                    res = np.array([r for r in res if r is not None])
                    N, nS, nY, sh, qh, sl, su, ql, qu = res.T
                    k = f'{dad}|{tas}|rho={rho}|phi={phi}|{kuy}|sigma={sg * 100:.2f}%'
                    out[k] = dict(
                        hucre_ort=round(float(N.mean()), 1), istasyon_ort=round(float(nS.mean()), 1), yil_ort=round(float(nY.mean()), 1),
                        sigma_gercek_yuzde=round(sg_g * 100, 4), q95_gercek_yuzde=round(q_g * 100, 4),
                        sigma_hat_oran_q05_q50_q95=[round(float(x), 3) for x in np.quantile(sh / sg_g, [0.05, 0.5, 0.95])],
                        q95_hat_oran_q05_q50_q95=[round(float(x), 3) for x in np.quantile(qh / q_g, [0.05, 0.5, 0.95])],
                        sigma_aralik_genislik_oran=round(float(np.median((su - sl) / sg_g)), 3),
                        q95_aralik_genislik_oran=round(float(np.median((qu - ql) / q_g)), 3),
                        sigma_kapsama=round(float(np.mean((sl <= sg_g) & (su >= sg_g))), 3),
                        q95_kapsama=round(float(np.mean((ql <= q_g) & (qu >= q_g))), 3),
                        c_karsilandi=round(float(np.mean(su < 0.002)), 3), c_karsilanmadi=round(float(np.mean(sl > 0.002)), 3),
                        c_belirsiz=round(float(np.mean((su >= 0.002) & (sl <= 0.002))), 3))
                    print(k, out[k], flush=True)
    json_yaz('kesinlik', dict(R=R, B=B, gun_doluluk_ek_kayip=0.10, sonuc=out, sure_sn=round(time.time() - t0),
                              model='Δ = [L(T-1) - (L(T-2)+L(T-3))/2]·ölçek + ölçüm; L = √ρ·C(yıl) + √(1-ρ)·U(istasyon, yıl); '
                                    'C, U AR(1) φ; t4 değişkesinde U Student-t(4), AR yok'))


# ============================================================== (C) Nisan 2025 M6,2 pozitif kontrolü (bilgi)
def _pk_is(arg):
    sn, h, A, k = arg
    rng = np.random.default_rng(tohum('tr4-pk', 20261203, sn, h, A, k))
    snr = SNR[sn] * math.sqrt(h / 4.0)
    return sn, h, A, YP2.pk_istasyon(rng, snr, A, 5e-4)


def pk():
    t0 = time.time()
    A_L = (0.0, 1e-4, 2e-4, 5e-4, 8e-4); N = 300
    isler = [(sn, h, A, k) for sn in ('CC10~0,5', 'CC10~0,7') for h in (4, 2) for A in A_L for k in range(N)]
    import multiprocessing as mp
    with mp.get_context('fork').Pool(4) as p:
        R = p.map(_pk_is, isler, chunksize=8)
    out = {}
    for sn in ('CC10~0,5', 'CC10~0,7'):
        for h in (4, 2):
            d0 = np.array([x[3] for x in R if x[0] == sn and x[1] == h and x[2] == 0.0]); d0 = d0[~np.isnan(d0)]
            esik = float(np.quantile(d0, 0.05))
            for A in A_L:
                d = np.array([x[3] for x in R if x[0] == sn and x[1] == h and x[2] == A]); g = d[~np.isnan(d)]
                out[f'{sn}|{h}s|A={A * 100:.2f}%'] = dict(
                    gecerli=round(len(g) / len(d), 3), dko_medyan_yuzde=round(float(np.median(g)) * 100, 4),
                    dko_sd_yuzde=round(float(np.std(g)) * 100, 4), esik_q05_A0_yuzde=round(esik * 100, 4),
                    P_saptama_tek_istasyon=round(float(np.mean(g < esik)), 3))
                print(sn, h, A, out[f'{sn}|{h}s|A={A * 100:.2f}%'], flush=True)
    json_yaz('pk', dict(istasyon='KO.SLVT (44 km; 2L(M6,2) ≈ 33 km)', N=N, mevsim_yuzde=0.05,
                        tanim='tr5b_yapay2.pk_istasyon (±%2 ızgara, δ_ko = ort ε[T+10,T+30] − ort ε[T−60,T−8]); '
                              'saptama: δ_ko < A = 0 dağılımının %5 niceliği (tek istasyon, tek yanlı)',
                        sonuc=out, sure_sn=round(time.time() - t0)))


# ============================================================== (D) dondurulmuş yapay ÇİF'lerde TR-4 gün örneklemesi
def ref(npz):
    t0 = time.time()
    z = np.load(npz)
    r5 = json.load(open(os.path.join(TR5, 'tr5b_yapay_ccf_ref.json')))
    gun = z['gunler'].astype(int); assert len(gun) == 1095
    out = dict(npz=os.path.basename(npz), npz_sha256=r5['sha256'], tolerans=dict(delta_yuzde=0.0005, oran=0.005), tasarim={})
    for ad in ('C_20g_4s', 'F_16g_4s'):
        d = TASARIM[ad][0]; L = []
        for i, s in enumerate(r5['seriler']):
            T_ord = s['T_ord']
            gun_ayi = np.array([dt.date.fromordinal(T_ord + int(g)).day for g in gun])
            ay = z['ay'][i].astype(int)
            gec = z['gecerli'][i] & (gun_ayi <= d)
            D0 = YP.ay_esle(YP.zincir(z['ccf'][i].astype(np.float64), gec, gun, 0), gun, ay)
            D2 = YP.ay_esle(YP.zincir(z['ccf_eklenmis'][i].astype(np.float64), gec, gun, 0), gun, ay)
            L.append(dict(snr=s['snr'], tekrar=s['tekrar'], T_ord=T_ord, delta_yuzde=None if np.isnan(D0) else round(D0 * 100, 6),
                          delta_eklenmis_yuzde=None if np.isnan(D2) else round(D2 * 100, 6),
                          oran=None if (np.isnan(D0) or np.isnan(D2)) else round((D2 - D0) / -1e-3, 5)))
        o = [x['oran'] for x in L if x['oran'] is not None]
        out['tasarim'][ad] = dict(ayda_gun=d, gecerli=len(o), oran_medyan=round(float(np.median(o)), 4),
                                  oran_min=round(min(o), 4), oran_max=round(max(o), 4), seriler=L)
        print(ad, len(o), out['tasarim'][ad]['oran_medyan'], out['tasarim'][ad]['oran_min'], out['tasarim'][ad]['oran_max'], flush=True)
    out['sure_sn'] = round(time.time() - t0)
    json.dump(out, open(os.path.join(BURASI, 'tr4_yapay_ref.json'), 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    k = sys.argv[1]
    if k == 'olcum': olcum()
    elif k == 'kesinlik': kesinlik()
    elif k == 'pk': pk()
    elif k == 'ref': ref(sys.argv[2])
