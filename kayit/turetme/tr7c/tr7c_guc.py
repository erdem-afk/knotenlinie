"""TR-7c bağımsız inceleme (İNCELEME-0): kör Parkfield kontrolünün gücü. Yalnız ikiterimli hesap.

Gerçek dalga formu okunmaz ya da indirilmez. Tek girdi `kayit/turetme/tr7b/tr7b_sayim.json` (Chao 2012 Tablo S1
etiketleri, PGV_T ve istasyon sayıları; üstveri). Çıktı: `kayit/turetme/tr7c/tr7c_guc.json`.

Model (varsayımlar, sonuç değil):
- Her pozitif (P) olay bağımsız olarak s olasılıkla gerçek tremor algılaması verir; tremor kaçarsa yine de q_N
  olasılıkla yanlış alarm (K1b aralığında sağ küme) verebilir: p_P = 1 − (1 − s)(1 − q_N).
- Her Chao negatif (N) olay q_N olasılıkla algılama verir (tetikleyicili ama tremorsuz pencere; sızıntı dahil).
- Rastgele negatif pencereler (TR-7 §7.3; N_PK = 120) r olasılıkla algılama verir: f_PK ~ Bin(120, r).
  r ile q_N ayrı tutulur, çünkü TR-7'nin başarısızlık biçimi (tetikleyicinin kendi sinyali) rastgele pencerede yoktur.
- Olaylar bağımsız (Kuril 2006/2007 bağımlılığı modelde yok).

Ölçütler:
- A  : TR-7b §6.4 (b) aynen, |N| = 2: X_P ≥ max(⌈n/2⌉, X_min(n, f_PK)), FAR_PK ≤ 0,30 ve
       değil(X_N/|N| ≥ X_P/n)  ["geçti, ayırt edici değil" etiketi yoksa "sınandı"].
- B  : X_P ≥ 5/10 ve X_N = 0/2.
- F2 : Fisher tek yanlı p ≤ 0,05 (P'ye karşı N, |N| = 2) + A'nın X_P şartı.
- A30: A ile aynı, |N| = 30.
- D30: A'nın X_P şartı + Fisher tek yanlı p ≤ 0,05 (P'ye karşı N, |N| = 30) + FAR_PK ≤ 0,30. (Önerilen.)
- E30: X_P ≥ 5/10 ve X_N ≤ 6/30.
- D11: D30 ile aynı, N = Q = 0 ve PGV_T ≥ 0,01 cm/s (11 olay).
- D30M / D30M3: D30 + modülasyon şartı (algılama veren P olaylarının ≥ ⌈X_P/2⌉'si / en az 3'ü modülasyonlu).
  Önerilen ölçüt D30M3'tür. Modülasyon geçme olasılıkları (m_t, m_f) varsayımdır.
- Genliğe bağlı sızıntı: q(v) = 1/(1 + (v0/v)²), v = PKD PGV_T (Chao 2012 S1), v0 ∈ {0,01; 0,03; 0,1} cm/s.
"""
import json, math, os, sys

os.environ.setdefault('OMP_NUM_THREADS', '1')
from scipy.stats import beta  # noqa: E402

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAYIM = os.path.join(KOK, 'tr7b', 'tr7b_sayim.json')
CIKTI = os.path.join(KOK, 'tr7c', 'tr7c_guc.json')

N_PK = 120


def binom_pmf(n, p):
    return [math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(n + 1)]


def p_ust(f, N):
    return 1.0 if f >= N else float(beta.ppf(0.95, f + 1, N - f))


def x_min(n, f, N=N_PK, esik=0.05):
    pu = p_ust(f, N)
    pmf = binom_pmf(n, pu)
    for X in range(2, n + 1):
        if sum(pmf[X:]) <= esik:
            return X
    return None


XMIN = {}


def xmin_c(n, f):
    if (n, f) not in XMIN:
        XMIN[(n, f)] = x_min(n, f)
    return XMIN[(n, f)]


def fisher_tek(xp, n, xn, m):
    """H1: P'de algılama oranı N'dekinden büyük. Hipergeometrik üst kuyruk."""
    K = xp + xn
    T = n + m
    den = math.comb(T, K)
    return sum(math.comb(n, x) * math.comb(m, K - x) for x in range(xp, min(K, n) + 1)) / den


def gecer(kriter, xp, n, xn, m, f):
    far = f / N_PK
    xm = xmin_c(n, f)
    temel = xm is not None and xp >= max(math.ceil(n / 2), xm)
    if kriter in ('A', 'A30'):
        return temel and far <= 0.30 and not (m >= 1 and xn / m >= xp / n)
    if kriter == 'B':
        return xp >= 5 and xn == 0
    if kriter in ('F2', 'D30'):
        return temel and far <= 0.30 and fisher_tek(xp, n, xn, m) <= 0.05
    if kriter == 'E30':
        return xp >= 5 and xn <= 6
    raise ValueError(kriter)


M_KRITER = {'A': 2, 'B': 2, 'F2': 2, 'A30': 30, 'D30': 30, 'E30': 30}


def p_gec(kriter, s, qN, r, n=10, m=None, qP=None):
    m = M_KRITER[kriter] if m is None else m
    qP = qN if qP is None else qP
    pP = 1 - (1 - s) * (1 - qP)
    PP = binom_pmf(n, pP)
    PN = binom_pmf(m, qN)
    if kriter in ('B', 'E30'):
        PF = [1.0]
        fs = [0]
    else:
        PF = binom_pmf(N_PK, r)
        fs = range(N_PK + 1)
    top = 0.0
    for f in fs:
        wf = PF[f]
        if wf < 1e-12:
            continue
        for xp in range(n + 1):
            if PP[xp] < 1e-15:
                continue
            for xn in range(m + 1):
                if PN[xn] < 1e-15:
                    continue
                if gecer(kriter, xp, n, xn, m, f):
                    top += wf * PP[xp] * PN[xn]
    return top


def main():
    d = json.load(open(SAYIM))
    olay = d['olaylar']
    neg = [o for o in olay if o['Q_CC'] == 0]
    poz = [o for o in olay if o['Q_CC'] == 1 and not o['evid'].startswith('20110311')]
    liste3_neg = [o for o in neg if o['sayi_var']['liste'] >= 3]
    pgv = sorted(o['pgv_t_cms'] for o in neg)
    neg_01 = [o['ad'] for o in neg if o['pgv_t_cms'] >= 0.01]
    neg_02 = [o['ad'] for o in neg if o['pgv_t_cms'] >= 0.02]
    sonuc = dict(
        not_='TR-7c İNCELEME-0; yapay ikiterimli hesap; gerçek dalga formu yok. Varsayımlar betik başlığında.',
        girdi=dict(sayim_json=os.path.relpath(SAYIM, KOK), n_poz_tohoku_haric=len(poz), n_neg=len(neg),
                   n_neg_liste3=len(liste3_neg), neg_pgv_t_medyan=pgv[len(pgv) // 2],
                   neg_pgv_t_ge_0_01=neg_01, neg_pgv_t_ge_0_02=neg_02),
        xmin_tablo={str(f): xmin_c(10, f) for f in (0, 6, 12, 18, 24, 30, 36, 40)},
        fisher_ornek={
            '10/10 vs 0/2': fisher_tek(10, 10, 0, 2), '9/10 vs 0/2': fisher_tek(9, 10, 0, 2),
            '8/10 vs 0/2': fisher_tek(8, 10, 0, 2), '5/10 vs 0/30': fisher_tek(5, 10, 0, 30),
            '5/10 vs 3/30': fisher_tek(5, 10, 3, 30), '6/10 vs 6/30': fisher_tek(6, 10, 6, 30),
            '7/10 vs 9/30': fisher_tek(7, 10, 9, 30)},
    )
    S = [0.3, 0.5, 0.7, 0.9]
    Q = [0.05, 0.1, 0.2, 0.3]
    kriterler = ['A', 'B', 'F2', 'A30', 'D30', 'E30']
    # 1) Ana tablo: r = q_N (rastgele pencere FAR'ı = tetikleyicili yanlış alarm)
    ana = {}
    for k in kriterler:
        ana[k] = {f's{s}_q{q}': round(p_gec(k, s, q, q), 4) for s in S for q in Q}
    sonuc['ana_r_esit_qN'] = ana
    # 2) Ayırt etmeyen (sızıntı güdümlü) algılayıcı: tremor yok (s = 0) ama her büyük tetikleyicide t olasılıkla
    #    ateşliyor; rastgele pencerede r = 0,05.
    ayirt = {}
    for k in kriterler:
        ayirt[k] = {f't{t}': round(p_gec(k, 0.0, t, 0.05), 4) for t in (0.3, 0.5, 0.7, 0.9)}
    sonuc['ayirt_etmeyen_s0_qN_t_r005'] = ayirt
    # 3) Kirli negatif: Chao Q = 0 olaylarının π'sinde görsel eşiğin altında gerçek tremor var; algılayıcımız onları
    #    s ile görür → q_N,etkin = q + π·s·(1 − q). P için p_P değişmez (q ile).
    kirli = {}
    for k in ('A', 'D30', 'E30'):
        for pi in (0.2, 0.4):
            for s in (0.5, 0.7, 0.9):
                q = 0.1
                qe = q + pi * s * (1 - q)
                kirli[f'{k}_pi{pi}_s{s}_q0.1'] = round(p_gec(k, s, qe, q, qP=q), 4)
    sonuc['kirli_negatif'] = kirli
    # 4) MDE: D30 ve A için, q = 0,1 ve 0,2'de güç ≥ 0,80 veren en küçük s (0,01 adım)
    mde = {}
    for k in ('A', 'D30'):
        for q in (0.05, 0.1, 0.2):
            sm = None
            for i in range(1, 101):
                s = i / 100
                if p_gec(k, s, q, q) >= 0.80:
                    sm = s
                    break
            mde[f'{k}_q{q}'] = sm
            if sm is not None:
                mde[f'{k}_q{q}_guc_s_x0.5'] = round(p_gec(k, sm * 0.5, q, q), 4)
                mde[f'{k}_q{q}_guc_s_x2'] = round(p_gec(k, min(1.0, sm * 2), q, q), 4)
    sonuc['mde_guc080'] = mde
    # 5) Marmara boş tarama: Parkfield türü kaynak varsa ve tetikleyici başına algılama olasılığı s_M ise
    #    n tetikleyicide hiç algılama olmama olasılığı (1 − s_M)^n.
    sonuc['marmara_bos_olasiligi'] = {f'n{n}_s{s}': round((1 - s) ** n, 4)
                                      for n in (4, 8, 9, 12) for s in (0.1, 0.2, 0.3, 0.5, 0.7)}
    # 6) PGV_T 0,027 cm/s ≈ kaç kPa (τ ≈ G·PGV/β; G = 30 GPa, β = 3,5 km/s; kaba)
    sonuc['pgv_kpa_kaba'] = {str(v): round(30e9 * v / 100 / 3500 / 1e3, 2) for v in (0.0013, 0.01, 0.0254, 0.027, 0.0615, 0.496)}
    # 7) Genliğe bağlı sızıntı (karıştırıcı): tremor yok (s = 0), yanlış alarm olasılığı tetikleyicinin PKD PGV_T'sine
    #    bağlı: q(v) = 1 / (1 + (v0 / v)^k), k = 2 (PGV 10 katında ~0,01 → ~0,99 değil; yumuşak), v0 = orta nokta.
    #    P = önerilen 10 pozitif, N30 = bütün Q = 0, N11 = Q = 0 ve PGV_T ≥ 0,01 cm/s.
    P10 = ['Peru 2001', 'Denali 2002', 'Colima 2003', 'Tokachi-oki 2003', 'Sumatra 2004', 'Kuril 2006',
           'Kuril 2007', 'Wenchuan 2008', 'Samoa 2009', 'Maule 2010']
    vP = [o['pgv_t_cms'] for o in poz if o['ad'] in P10]
    assert len(vP) == 10, vP
    vN30 = [o['pgv_t_cms'] for o in neg]
    vN11 = [v for v in vN30 if v >= 0.01]
    sonuc['P10_pgv_t'] = sorted(vP)

    def pois_binom(ps):
        dist = [1.0]
        for p_ in ps:
            yeni = [0.0] * (len(dist) + 1)
            for i, w in enumerate(dist):
                yeni[i] += w * (1 - p_)
                yeni[i + 1] += w * p_
            dist = yeni
        return dist

    def p_gec_gen(qP_list, qN_list, r, s=0.0, fisher=True):
        n, m = len(qP_list), len(qN_list)
        DP = pois_binom([1 - (1 - s) * (1 - q_) for q_ in qP_list])
        DN = pois_binom(qN_list)
        PF = binom_pmf(N_PK, r)
        top = 0.0
        for f in range(N_PK + 1):
            if PF[f] < 1e-12:
                continue
            xm = xmin_c(n, f)
            if xm is None or f / N_PK > 0.30:
                continue
            for xp in range(max(math.ceil(n / 2), xm), n + 1):
                for xn in range(m + 1):
                    if fisher_tek(xp, n, xn, m) <= 0.05:
                        top += PF[f] * DP[xp] * DN[xn]
        return top

    gen = {}
    for v0 in (0.01, 0.03, 0.1):
        q = lambda v: 1 / (1 + (v0 / v) ** 2)
        gen[f'v0_{v0}'] = dict(
            qP_ort=round(sum(map(q, vP)) / 10, 3), qN30_ort=round(sum(map(q, vN30)) / 30, 3),
            qN11_ort=round(sum(map(q, vN11)) / len(vN11), 3),
            D30_s0=round(p_gec_gen([q(v) for v in vP], [q(v) for v in vN30], 0.05), 4),
            D11_s0=round(p_gec_gen([q(v) for v in vP], [q(v) for v in vN11], 0.05), 4),
            D30_s07=round(p_gec_gen([q(v) for v in vP], [q(v) for v in vN30], 0.05, s=0.7), 4),
            D11_s07=round(p_gec_gen([q(v) for v in vP], [q(v) for v in vN11], 0.05, s=0.7), 4))
    sonuc['genlige_bagli_sizinti'] = gen
    # D11 sabit q ile güç (karşılaştırma)
    sonuc['D11_sabit_q'] = {f's{s_}_q{q_}': round(p_gec_gen([q_] * 10, [q_] * len(vN11), q_, s=s_), 4)
                            for s_ in (0.3, 0.5, 0.7, 0.9) for q_ in (0.05, 0.1, 0.2, 0.3)}
    sonuc['D11_ayirt_etmeyen'] = {f't{t}': round(p_gec_gen([t] * 10, [t] * len(vN11), 0.05), 4)
                                  for t in (0.3, 0.5, 0.7, 0.9)}
    # 8) Modülasyon şartı "sınandı"ya eklenirse (TR-7b §6.4'teki 'Parkfield modülasyonu geçti' tanımı: algılama veren P
    #    olaylarının ≥ ⌈X_P/2⌉'sinde p ≤ 0,01'lik küme). Gerçek tremor algılamasında modülasyon geçme olasılığı m_t
    #    (bilinmiyor; 0,5 / 0,8), yanlış (sızıntı) algılamada m_f = 0,05 (varsayım; doğrulanamadı).
    def p_gec_mod(qP_list, qN_list, r, s, m_t, m_f=0.05, mutlak=None):
        n, m = len(qP_list), len(qN_list)
        # P olayı başına durum olasılıkları: (algılama, modüle) çiftleri
        durum = []
        for q_ in qP_list:
            pt = s
            pf = (1 - s) * q_
            durum.append({(1, 1): pt * m_t + pf * m_f, (1, 0): pt * (1 - m_t) + pf * (1 - m_f),
                          (0, 0): 1 - pt - pf})
        dist = {(0, 0): 1.0}
        for dd in durum:
            yeni = {}
            for (x, mm), w in dist.items():
                for (a, b), w2 in dd.items():
                    k_ = (x + a, mm + b)
                    yeni[k_] = yeni.get(k_, 0.0) + w * w2
            dist = yeni
        DN = pois_binom(qN_list)
        PF = binom_pmf(N_PK, r)
        top = 0.0
        for f in range(N_PK + 1):
            if PF[f] < 1e-12:
                continue
            xm = xmin_c(n, f)
            if xm is None or f / N_PK > 0.30:
                continue
            for (xp, mm), w in dist.items():
                if xp < max(math.ceil(n / 2), xm) or mm < (math.ceil(xp / 2) if mutlak is None else mutlak):
                    continue
                for xn in range(m + 1):
                    if fisher_tek(xp, n, xn, m) <= 0.05:
                        top += PF[f] * w * DN[xn]
        return top

    modl = {}
    for m_t in (0.5, 0.8):
        for s_ in (0.5, 0.7, 0.9):
            for q_ in (0.05, 0.1, 0.2):
                modl[f'D30M_mt{m_t}_s{s_}_q{q_}'] = round(p_gec_mod([q_] * 10, [q_] * 30, q_, s_, m_t), 4)
    for v0 in (0.01, 0.03, 0.1):
        q = lambda v: 1 / (1 + (v0 / v) ** 2)
        modl[f'D30M_sizinti_v0_{v0}_s0'] = round(p_gec_mod([q(v) for v in vP], [q(v) for v in vN30], 0.05, 0.0, 0.8), 4)
        for m_t in (0.5, 0.8):
            modl[f'D30M_sizinti_v0_{v0}_s0.7_mt{m_t}'] = round(
                p_gec_mod([q(v) for v in vP], [q(v) for v in vN30], 0.05, 0.7, m_t), 4)
    for t in (0.3, 0.5, 0.7, 0.9):
        modl[f'D30M_ayirt_etmeyen_t{t}'] = round(p_gec_mod([t] * 10, [t] * 30, 0.05, 0.0, 0.8), 4)
    # Değişke D30M3: modülasyonlu P olayı ≥ 3 (mutlak), öteki şartlar aynı.
    for m_t in (0.3, 0.5, 0.8):
        for s_ in (0.5, 0.7, 0.9):
            modl[f'D30M3_mt{m_t}_s{s_}_q0.1'] = round(p_gec_mod([0.1] * 10, [0.1] * 30, 0.1, s_, m_t, mutlak=3), 4)
    for v0 in (0.01, 0.03, 0.1):
        q = lambda v: 1 / (1 + (v0 / v) ** 2)
        modl[f'D30M3_sizinti_v0_{v0}_s0'] = round(p_gec_mod([q(v) for v in vP], [q(v) for v in vN30], 0.05, 0.0, 0.8,
                                                            mutlak=3), 4)
        modl[f'D30M3_sizinti_v0_{v0}_s0_mf0.1'] = round(p_gec_mod([q(v) for v in vP], [q(v) for v in vN30], 0.05, 0.0,
                                                                  0.8, m_f=0.1, mutlak=3), 4)
    modl['D30M3_mde_mt0.5_q0.1'] = next((i / 100 for i in range(1, 101)
                                         if p_gec_mod([0.1] * 10, [0.1] * 30, 0.1, i / 100, 0.5, mutlak=3) >= 0.8), None)
    modl['D30M3_mde_mt0.8_q0.1'] = next((i / 100 for i in range(1, 101)
                                         if p_gec_mod([0.1] * 10, [0.1] * 30, 0.1, i / 100, 0.8, mutlak=3) >= 0.8), None)
    for m_t in (0.5, 0.8):
        sonuc[f'D30M3_izgara_mt{m_t}'] = {f's{s_}_q{q_}': round(p_gec_mod([q_] * 10, [q_] * 30, q_, s_, m_t, mutlak=3), 4)
                                          for s_ in (0.3, 0.5, 0.7, 0.9) for q_ in (0.05, 0.1, 0.2, 0.3)}
    # Olay sayısı düşerse (E1 maskesi, örtü): D30M3 gücü ve sızıntılı yanlış kabul (s = 0,7; q = 0,1; m_t = 0,8 / 0,5)
    sonuc['D30M3_olay_sayisi'] = {
        f'nP{nP}_nN{nN}': dict(
            guc_mt08=round(p_gec_mod([0.1] * nP, [0.1] * nN, 0.1, 0.7, 0.8, mutlak=3), 4),
            guc_mt05=round(p_gec_mod([0.1] * nP, [0.1] * nN, 0.1, 0.7, 0.5, mutlak=3), 4),
            ayirt_etmeyen_t07=round(p_gec_mod([0.7] * nP, [0.7] * nN, 0.05, 0.0, 0.8, mutlak=3), 4))
        for nP in (5, 6, 8, 10) for nN in (10, 20, 30)}
    sonuc['modulasyon_sartli_D30M'] = modl
    json.dump(sonuc, open(CIKTI, 'w'), ensure_ascii=False, indent=1, sort_keys=True)
    print(json.dumps(sonuc, ensure_ascii=False, indent=1, sort_keys=True))


if __name__ == '__main__':
    sys.exit(main())
