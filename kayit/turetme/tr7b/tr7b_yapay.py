#!/usr/bin/env python3
"""TR-7b ön kayıt taslağı §2: sızıntı kuralının aday yeniden tasarımları, YALNIZ YAPAY VERİ.

TR-7'nin `tr7_cekirdek.py`'si DEĞİŞTİRİLMEDEN içe aktarılır ve algılayıcının kendisi (L, m, σ, aşım, köprüleme, küme,
tutarlılık, darbe, taban) oradan kullanılır. Bu betik yalnız (i) yapay 1 Hz zarfları üretir (20 Hz, FFT ile 4 kutuplu
ileri-geri Butterworth |H|², Hilbert, 1 sn ortalama, 3 bileşen karesel ortalama; TR-7 §7.1 referans zinciri) ve
(ii) sızıntı kuralının adaylarını tanımlar. Gerçek dalga formu okunmaz, ağa çıkılmaz.

Zaman ekseni (saniye): R = [0, 3600), Q = [3600, 4500) (tetikleyicinin kendi cisim dalgası aralığı: T0 + t_P ile
W başı arası; tele sinyal 3630'da başlar), W = [4500, 6400).

Aday kurallar (istasyon başına bayrak; küme, istasyonların ≥ yarısı bayraklıysa atılır; TR-7 §6.5.3 ile aynı toplama):
  K0  TR-7 §6.5.3 (taban çizgisi): Δ_d ≥ Δ_y.
  K1  Referans-göreli (tetikleyicinin kendi cisim dalgası aralığı Q referans): Q'da L_d − m_d > 4σ_d olan saniyeler
      ≥ 30 ise (L − m) = a + b (L_d − m_d) en küçük kareler doğrusu kurulur; istasyonun kümedeki aşım saniyelerinde
      kalıntı e = (L − m) − (a + b (L_d − m_d)) ve bayrak: medyan(e) < 2σ (2–8 Hz fazlasının, tetikleyicinin kendi
      telesismik sinyalinin öngördüğünün üstündeki kısmı algılama eşiğinin yarısından küçük). Q'da yeterli saniye
      yoksa K0'a düşer.
  K2  Eşzamanlılık: Δ_d ≥ Δ_y VE r(L, L_d) ≥ 0,5; r, istasyonun kümedeki aşım saniyelerindeki (K0 ile aynı saniyeler)
      Pearson ilişkisidir; < 10 saniye varsa r = 1 sayılır (tutucu). 0,5 eşiği §6.3'ün KORR'udur; veriyle seçilmedi.
  K3  Birleşik: Δ_d ≥ Δ_y VE (K1'in kalıntı şartı VEYA K2'nin r şartı). Q'da referans yoksa K2'ye eşittir.

Satırlar (iki bağımsız tohum; her satırda algılama oranı, algılananlarda TÜM ayıklama kurallarıyla (darbe + sızıntı
adayı + taban) ve yalnız sızıntı adayıyla atılma; Y1'de yalnız I′'su tremor aralığıyla kesişen kümeler sayılır):
  D7   yarım sinüs tremor A_etkin = 10                                   şart: tam atılma ≤ 0,03
  D7b  patlamalı tremor A_etkin = 3, 10, 30                              şart: tam atılma ≤ 0,03
  D7c  0,5–8 Hz düz, yarım sinüs tremor A_etkin = 3, 10 (Gauss)          şart: sızıntıyla atılma ≤ 0,05
  D7d  bölgesel koda ×20 (0,5–8 Hz, f⁻¹, 40 sn sönüm)                    şart: sızıntıyla atılma ≥ 0,95
  Y1   tremor (yarım sinüs, A_etkin 3 ve 10) + eş zamanlı telesismik     şart ('egim' = kalibre biçim): tam atılma
       sinyal (Tohoku–Parkfield düzeyi)                                  ≤ 0,05; 'sabit' biçim yalnız bilgi
  Y2   yalnız telesismik sinyal, tremor yok (4 düzey/biçim)              şart: algılananlarda tam atılma ≥ 0,95
  Y3   bölgesel koda ×20 + kalibre telesismik sinyal, tremor yok         şart: sızıntıyla atılma ≥ 0,95
Telesismik model: beyaz taşıyıcı, iki bantta ayrı genlik: 2–8 Hz a_y·e_y(t), 0,5–1 Hz κ·a_y·e(t); e(t) = P başında 1,
150 sn e-katlı sönen koda + 0,1 taban + artçı P darbeleri (Poisson, ortalama 120 sn arayla; genlik 0,1·LN(0, 0,5);
ani başlangıç, 60–180 sn sönüm). 'egim' biçiminde e_y = e·exp(−(t − t_P)/600 sn) (yüksek frekans daha hızlı
soğurulur), 'sabit' biçimde e_y = e. Kalibrasyon (geliştirme verisi: Tohoku–Parkfield, 12 istasyonun dakikalık
medyanı, yalnız tetikleyicinin P aralığı 05:57–06:05 UTC, W'den önce): P tepesinde Δ_y ≈ 1,0, Δ_d ≈ 2,1 →
a_y = 10, κ = 12,5; P'den 7 dk sonra Δ_y ≈ 0,1–0,2, Δ_d ≈ 1,2–1,35 → 150 sn koda sönümü, 0,1 taban ve 'egim'.
Ötekiler ('sabit'; a_y 20 / κ 6; a_y 5 / κ 25) zorlama varyantlarıdır.

SEÇİM ÖLÇÜTÜ (tam koşudan önce yazıldı): bir aday, iki tohumda da yukarıdaki bütün şartları sağlıyorsa "kabul
edilebilir"dir. Kabul edilebilirler arasında (1) tetikleyici ve negatif pencerelerde aynı hesabı yapan (simetrik)
kural, (2) eşitlikte şartlara en kötü pay farkı en büyük olan seçilir. Hiçbiri kabul edilebilir değilse kural seçilmez
ve TR-7b dondurulamaz.
Açıklık notu: K3, Y3 satırı ve Y1 'sabit'in bilgiye indirilmesi, 20 pencerelik bir ön denemeden (tohum 11) SONRA
eklendi: ön denemede K2 kalibre Y2'de (2 algılamanın 2'si) atmadı, K1 kalibre Y1 A3'te 0,05 verdi, 'sabit' biçimde
2–8 Hz telesismik sinyal W boyunca tek küme kurduğu için hiçbir kural tremoru ayıramadı (K0, K1, K2 hepsi 1,00).
Bu ön deneme bir ayar adımıdır; bağımsız inceleme bu sırayı bilmelidir.

Kullanım: python3 -I -B tr7b_yapay.py <tohum> <n_pencere> <çıktı.json>
"""
import json, os, sys
import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tr7'))
import tr7_cekirdek as c   # noqa: E402  (değiştirilmeden)

FS = 20.0
R_S, Q_S, W_S = 3600, 900, 1900
T = R_S + Q_S + W_S
N = int(T * FS)
F = np.fft.rfftfreq(N, 1 / FS)
R_IX, Q_IX, W_IX = (0, R_S), (R_S, R_S + Q_S), (R_S + Q_S, T)
TP = R_S + 30
t = np.arange(N) / FS


def bw2(lo, hi, n=4):
    with np.errstate(divide='ignore'):
        return 1 / (1 + (lo / np.maximum(F, 1e-9)) ** (2 * n)) / (1 + (F / hi) ** (2 * n))


H28, H051 = bw2(2, 8), bw2(0.5, 1)
DUZ = bw2(0.5, 8)
KODA = bw2(0.5, 8) / np.maximum(F, 0.5)


def analitik(X):
    X = X.copy()
    X[1:] *= 2
    full = np.zeros(N, complex)
    full[:len(X)] = X
    if N % 2 == 0:
        full[len(X) - 1] /= 2
    return np.fft.ifft(full)


def zarf1hz(a):
    return np.abs(a).reshape(-1, int(FS)).mean(1)


def iki_bant(rng, env=None, sekil=None, norm=None):
    """(y, d) analitik; env yoksa durağan beyaz taşıyıcı, her bant RMS 1. env varsa TR-7 §7.1 gibi y RMS (env>0 ya da
    norm maskesinde) 1."""
    x = rng.standard_normal(N)
    if env is None:
        X = np.fft.rfft(x)
        y, d = analitik(X * H28), analitik(X * H051)
        return y / np.sqrt(np.mean(y.real ** 2)), d / np.sqrt(np.mean(d.real ** 2))
    S = np.fft.rfft(x * env) * (H28 if sekil is None else sekil)
    y0 = analitik(S * H28)
    m = env > 0 if norm is None else norm
    k = 1 / np.sqrt(np.mean(y0.real[m] ** 2))
    return y0 * k, analitik(S * H051) * k


def zarf_yarim(bas, sure=300, per=20.0):
    tt = t - bas
    e = np.zeros(N)
    m = (tt >= 0) & (tt < sure)
    e[m] = np.maximum(0, np.sin(2 * np.pi * tt[m] / per)) * np.minimum(1, np.minimum(tt[m], sure - tt[m]) / 10)
    return e


def zarf_patlama(rng, bas, yuk=2.0, sure=300):
    tt = t - bas
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


def zarf_sabit(bas, sure=300):
    tt = t - bas
    e = np.zeros(N)
    m = (tt >= 0) & (tt < sure)
    e[m] = np.minimum(1, np.minimum(tt[m], sure - tt[m]) / 10)
    return e


def zarf_tele(rng):
    """Tetikleyicinin telesismik cisim dalgası + artçı P'leri (1 Hz'te üretilip FS'ye taşınır); bütün istasyonlarda
    ortak (telesismik dalga cephesi Parkfield ölçeğinde düzlemsel)."""
    s = np.arange(T, dtype=float)
    e = np.where(s >= TP, np.exp(-(s - TP) / 150.0) + 0.1, 0.0)
    k = TP + rng.exponential(120)
    while k < T:
        a = 0.1 * rng.lognormal(0, 0.5)
        d = rng.uniform(60, 180)
        e += np.where(s >= k, a * np.exp(-(s - k) / d), 0.0)
        k += rng.exponential(120)
    return np.repeat(e, int(FS))


def istasyonlar(rng, n_ist=3, tremor=None, A=0.0, sekil=None, norm=None, tele=None):
    """tremor: FS örnekli zarf (ortak); tele: (e_y, e_d, a_y, kappa) ya da None."""
    st = []
    for _ in range(n_ist):
        cy, cd = [], []
        for _b in range(3):
            ny, nd = iki_bant(rng)
            y, d = ny.copy(), nd.copy()
            if tremor is not None and A:
                sy, sd = iki_bant(rng, tremor, sekil, norm)
                y += A * sy
                d += A * sd
            if tele is not None:
                ey, ed, ay, ka = tele
                ty, td = iki_bant(rng)
                y += ay * ey * ty
                d += ka * ay * ed * td
            cy.append(zarf1hz(y))
            cd.append(zarf1hz(d))
        st.append((c.birlesik(cy), c.birlesik(cd)))
    return st


# ------------------------------------------------------------------ aday sızıntı kuralları
def secili(x, parcalar, maske):
    sec = np.zeros(len(x['L']), bool)
    for a, b in parcalar:
        sec[a:b] = True
    with np.errstate(invalid='ignore'):
        sec &= (x['L'] > x['m'] + c.KSIG * x['s']) & ~maske & np.isfinite(x['Ld'])
    return sec


def K0(x, parcalar, maske, Q):
    return c.sizinti_ist(x, parcalar, maske)


def K2(x, parcalar, maske, Q, r0=0.5):
    sec = secili(x, parcalar, maske)
    if not sec.any():
        return False
    dy = np.median(x['L'][sec]) - x['m']
    dd = np.median(x['Ld'][sec]) - x['md']
    if dd < dy:
        return False
    if sec.sum() < 10:
        return True
    a, b = x['L'][sec], x['Ld'][sec]
    if a.std() == 0 or b.std() == 0:
        return True
    return bool(np.corrcoef(a, b)[0, 1] >= r0)


def K1(x, parcalar, maske, Q):
    sec = secili(x, parcalar, maske)
    if not sec.any():
        return False
    r = _k1_kalinti(x, sec, maske, Q)
    return K0(x, parcalar, maske, Q) if r is None else r


def _k1_kalinti(x, sec, maske, Q, yedek=True):
    """K1'in kalıntı şartı; Q'da referans yoksa None (yedek) ya da False (K3 içinde)."""
    q = np.zeros(len(x['L']), bool)
    q[Q[0]:Q[1]] = True
    with np.errstate(invalid='ignore'):
        q &= ~maske & np.isfinite(x['L']) & np.isfinite(x['Ld']) & (x['Ld'] - x['md'] > c.KSIG * x['sd'])
    if q.sum() < 30:
        return None if yedek else False
    u, v = x['Ld'][q] - x['md'], x['L'][q] - x['m']
    b, a = np.polyfit(u, v, 1)
    e = (x['L'][sec] - x['m']) - (a + b * (x['Ld'][sec] - x['md']))
    return bool(np.median(e) < 2 * x['s'])


def K3(x, parcalar, maske, Q):
    sec = secili(x, parcalar, maske)
    if not sec.any():
        return False
    if np.median(x['Ld'][sec]) - x['md'] < np.median(x['L'][sec]) - x['m']:
        return False
    return K2(x, parcalar, maske, Q) or _k1_kalinti(x, sec, maske, Q, yedek=False)


KURALLAR = {'K0': K0, 'K1': K1, 'K2': K2, 'K3': K3}


def degerlendir(st, maske=None, ilgi=None):
    """Algılayıcı (tr7_cekirdek) + her aday için: (algılandı mı, tam kuralla atıldı mı, yalnız sızıntıyla atıldı mı).
    ilgi: (a, b) verilirse yalnız I′'su bu aralıkla kesişen kümeler sayılır."""
    maske = np.zeros(T, bool) if maske is None else maske
    ist = [c.istasyon(Cy, Cd, R_IX, W_IX, maske) for Cy, Cd in st]
    ks = c.kumeler(ist, maske, W_IX)
    if ilgi is not None:
        ks = [k for k in ks if k['Ip'][0] < ilgi[1] and k['Ip'][1] > ilgi[0]]
    if not ks:
        return None
    out = {}
    for ad, kural in KURALLAR.items():
        tam_sag, siz_sag = False, False
        for k in ks:
            uy = k['uyeler']
            pk = {i: [(a, b) for ii, a, b in k['parcalar'] if ii == i] for i in uy}
            yarim = len(uy) / 2
            d = sum(c.darbe_ist(ist[i]['Cy'], pk[i]) for i in uy) >= yarim
            s = sum(kural(ist[i], pk[i], maske, Q_IX) for i in uy) >= yarim
            tb = sum(c.taban_ist(ist[i], pk[i], maske) for i in uy) >= yarim
            tam_sag |= not (d or s or tb)
            siz_sag |= not s
        out[ad] = (not tam_sag, not siz_sag)
    return out


def satir(rng, n, uret, ilgi_f=None):
    alg, at = 0, {k: [0, 0] for k in KURALLAR}
    for _ in range(n):
        st, ilgi = uret(rng)
        r = degerlendir(st, ilgi=ilgi)
        if r is None:
            continue
        alg += 1
        for k, (a1, a2) in r.items():
            at[k][0] += a1
            at[k][1] += a2
    return dict(n=n, algilama=round(alg / n, 3),
                **{f'{k}_atilma_tam': (round(v[0] / alg, 3) if alg else None) for k, v in at.items()},
                **{f'{k}_atilma_sizinti': (round(v[1] / alg, 3) if alg else None) for k, v in at.items()})


def bas_w(rng):
    return W_IX[0] + int(rng.integers(60, W_S - 360))


def main():
    tohum, n, cikti = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    rng = np.random.default_rng(tohum)
    sonuc = {}

    def tr(tur, A, sekil=None):
        def u(rng):
            b = bas_w(rng)
            env = zarf_yarim(b) if tur == 'yarim' else zarf_patlama(rng, b) if tur == 'patlama' else zarf_sabit(b)
            return istasyonlar(rng, tremor=env, A=A, sekil=sekil), None
        return u

    def koda(rng):
        b = bas_w(rng)
        tt = t - b
        env = np.where(tt >= 0, np.exp(-np.maximum(tt, 0) / 40.0), 0) * np.minimum(1, np.maximum(tt, 0) / 1.0)
        norm = (tt >= 0) & (tt < 5)
        return istasyonlar(rng, tremor=env, A=20.0, sekil=KODA, norm=norm), None

    def tele_u(ay, ka, bicim, A=0.0, tur='yarim'):
        def u(rng):
            e = zarf_tele(rng)
            ey = e * np.where(t >= TP, np.exp(-(t - TP) / 600.0), 0) if bicim == 'egim' else e
            tele = (ey, e, ay, ka)
            if A:
                b = bas_w(rng)
                return istasyonlar(rng, tremor=zarf_yarim(b), A=A, tele=tele), (b, b + 300)
            return istasyonlar(rng, tele=tele), None
        return u

    isler = [('D7 yarım A10', tr('yarim', 10.0))]
    isler += [(f'D7b patlama A{A}', tr('patlama', float(A))) for A in (3, 10, 30)]
    isler += [(f'D7c düz A{A}', tr('yarim', float(A), DUZ)) for A in (3, 10)]
    isler += [('D7d koda x20', koda)]
    isler += [(f'Y1 tremor A{A} + tele a_y{ay} κ{ka} {b}', tele_u(ay, ka, b, A=float(A)))
              for A in (3, 10) for ay, ka, b in ((10, 12.5, 'egim'), (10, 12.5, 'sabit'))]
    isler += [(f'Y2 tele a_y{ay} κ{ka} {b}', tele_u(ay, ka, b))
              for ay, ka, b in ((10, 12.5, 'egim'), (10, 12.5, 'sabit'), (20, 6, 'sabit'), (5, 25, 'sabit'))]
    def y3(rng):
        e = zarf_tele(rng)
        ey = e * np.where(t >= TP, np.exp(-(t - TP) / 600.0), 0)
        b = bas_w(rng)
        tt = t - b
        env = np.where(tt >= 0, np.exp(-np.maximum(tt, 0) / 40.0), 0) * np.minimum(1, np.maximum(tt, 0) / 1.0)
        norm = (tt >= 0) & (tt < 5)
        return istasyonlar(rng, tremor=env, A=20.0, sekil=KODA, norm=norm, tele=(ey, e, 10, 12.5)), (b, b + 300)
    isler += [('Y3 koda x20 + tele kalibre', y3)]
    for ad, u in isler:
        sonuc[ad] = satir(rng, n, u)
        print(ad, json.dumps(sonuc[ad], ensure_ascii=False), flush=True)
    json.dump(dict(tohum=tohum, n=n, satirlar=sonuc), open(cikti, 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
