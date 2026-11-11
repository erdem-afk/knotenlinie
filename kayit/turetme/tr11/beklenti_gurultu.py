#!/usr/bin/env python3
"""TR-11: gürültü modelinden beklenen S dağılımı (yalnız yapay; hiçbir gerçek seri okunmaz).

Menteşe modeli TR-1 sürüm 2 ile aynı: sabit + eğim + yıllık/altı aylık sin-cos + max(0, t - H).
Pencere 1826 gün (floor(5 x 365,25)), menteşe sondan 730 gün önce (floor(2 x 365,25)); boşluksuz günlük örnekleme.
Gürültü (her yatay bileşen, bağımsız): beyaz sigma_w (mm) + kırpışma b_f (mm/yıl^0,25) + rastgele yürüyüş b_rw (mm/yıl^0,5).
Güç yasası kovaryansı Williams (2003) kesirli fark dönüşümüyle: C = b^2 dT^(-kappa/2) T T', dT yıl.
1) menteşe katsayısının standart sapması sigma_h (mm/yıl), en küçük kareler + gerçek kovaryans (sandviç);
2) S'nin dağılımı: her yakın ve referans istasyonda Dv ~ N(0, sigma_h^2 I2) bağımsız; S = medyan_i |Dv_i - medyan_ref|.
   S = sigma_h x f(n_y, n_r); f'nin nicelikleri Monte Carlo ile (tohum sabit).
Kullanım: python3 -I -B beklenti_gurultu.py
"""
import numpy as np

N, NH = 1826, 730
Y = 365.25
t = np.arange(N) / Y
H = (N - NH) / Y
X = np.column_stack([np.ones(N), t, np.sin(2*np.pi*t), np.cos(2*np.pi*t), np.sin(4*np.pi*t), np.cos(4*np.pi*t),
                     np.maximum(0, t - H)])
A = np.linalg.solve(X.T @ X, X.T)          # 7 x N
a = A[-1]                                   # menteşe satırı
dT = 1 / Y

def h(kappa):
    v = np.empty(N); v[0] = 1.0
    for i in range(1, N): v[i] = v[i-1] * (i - 1 - kappa/2) / i
    return v

HF, HR = h(-1.0), h(-2.0)
def var_pl(hv, kappa):
    # a' T T' a ; T alt üçgen Toeplitz (h). T' a = ters kayan toplam -> evrişim
    u = np.convolve(a[::-1], hv)[:N][::-1]     # (T' a)_j = sum_{i>=j} a_i h_{i-j}
    return dT ** (-kappa/2) * float(u @ u)

VF, VR, VW = var_pl(HF, -1.0), var_pl(HR, -2.0), float(a @ a)
def sigma_h(sw, bf, brw=0.0):
    return float(np.sqrt(sw**2 * VW + bf**2 * VF + brw**2 * VR))

# yıllık ortalama artık sd (AV-1 ile kaba karşılaştırma için): modeli menteşesiz uydur, artıkların 365 günlük
# blok ortalamalarının sd'si; beklenen değer Monte Carlo ile
def yillik_sd(sw, bf, brw=0.0, n=400, rng=np.random.default_rng(1)):
    X0 = X[:, :-1]; P = np.eye(N) - X0 @ np.linalg.solve(X0.T @ X0, X0.T)
    out = []
    for _ in range(n):
        e = sw * rng.standard_normal(N)
        if bf: e += bf * dT**0.25 * np.convolve(rng.standard_normal(N), HF)[:N]
        if brw: e += brw * dT**0.5 * np.cumsum(rng.standard_normal(N))
        r = P @ e
        out.append(np.std([r[k*365:(k+1)*365].mean() for k in range(5)], ddof=1))
    return float(np.mean(out))

def f_dagilim(ny, nr, n=200000, rng=None):
    rng = rng or np.random.default_rng(20261111 + 10*ny + nr)
    y = rng.standard_normal((n, ny, 2)); r = rng.standard_normal((n, nr, 2))
    m = np.median(r, axis=1)[:, None, :]
    return np.median(np.linalg.norm(y - m, axis=2), axis=1)

if __name__ == '__main__':
    print('menteşe katsayısı sigma_h (mm/yıl), bileşen başına, boşluksuz 1826 gün:')
    print('  birim katkılar: beyaz 1 mm -> %.4f ; kırpışma 1 mm/yıl^0,25 -> %.4f ; RW 1 mm/yıl^0,5 -> %.4f'
          % (np.sqrt(VW), np.sqrt(VF), np.sqrt(VR)))
    for sw in (1.0, 1.5, 2.0):
        for bf in (1.0, 2.0, 3.0, 4.0):
            print(f'  sw={sw} bf={bf}: sigma_h={sigma_h(sw, bf):.3f}   +RW1: {sigma_h(sw, bf, 1.0):.3f}')
    print('yıllık ortalama artık sd (mm), menteşesiz model, MC:')
    for sw, bf in ((1.5, 1.0), (1.5, 2.0), (1.5, 3.0), (1.5, 4.0)):
        print(f'  sw={sw} bf={bf}: {yillik_sd(sw, bf):.2f}')
    print('  sw=1.5 bf=2 rw=1:', round(yillik_sd(1.5, 2.0, 1.0), 2))
    print('f = S / sigma_h nicelikleri (medyan, %90, %95, %99):')
    for ny in (3, 4, 5, 6, 8):
        for nr in (3, 8):
            q = np.quantile(f_dagilim(ny, nr), [0.5, 0.9, 0.95, 0.99])
            print(f'  n_y={ny} n_r={nr}: ' + ' '.join(f'{x:.3f}' for x in q))

def karisim_nicelik(ny_say, nr=8, q=(0.5, 0.9, 0.95, 0.99), n=100000):
    """n_y dağılımı {n_y: küme-pencere sayısı} ağırlıklı f nicelikleri (n_r sabit)."""
    tum = np.concatenate([f_dagilim(ny, nr, n=max(1, int(n * c / sum(ny_say.values())))) for ny, c in ny_say.items()])
    return np.quantile(tum, q)

def G(x, D, m_r=0.0):
    """Vida dislokasyonu geometri çarpanı: S_sinyal = Δs * G; G = |arctan(x/D) - m_r| / pi (x işaretli, km)."""
    return abs(np.arctan(x / D) - m_r) / np.pi

if __name__ == '__main__':
    NY = {3: 160, 4: 104, 5: 59, 6: 54, 7: 55, 8: 371}     # sayim_ustveri.py ANA, n_r ≈ 8
    fq = karisim_nicelik(NY)
    print('havuz f nicelikleri (ANA n_y karışımı, n_r=8):', np.round(fq, 3))
    for ad, (sw, bf, rw) in {'N0 (1,5 mm; 3 mm/yıl^0,25)': (1.5, 3.0, 0.0), 'N0-düşük (bf 2)': (1.5, 2.0, 0.0),
                             'N0-yüksek (bf 4)': (1.5, 4.0, 0.0), 'N1 (N0 + RW 1 mm/yıl^0,5)': (1.5, 3.0, 1.0)}.items():
        s = sigma_h(sw, bf, rw)
        print(f'  {ad}: sigma_h={s:.3f}; S medyan/%90/%95/%99 = ' + ' / '.join(f'{s*x:.2f}' for x in fq))
    print('G(x, D), dengeli referans (m_r = 0):')
    for D in (5.0, 10.0, 15.0):
        print(f'  D={D:>4}: ' + '  '.join(f'x={x:>2}: {G(x, D):.3f} (1/G={1/G(x, D):.1f})' for x in (5, 10, 20, 30, 50)))
