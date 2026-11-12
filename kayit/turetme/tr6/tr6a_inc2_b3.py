"""İNCELEME-2 b3 (bağımsız denetim), numpy + standart kitaplıkla yeniden yazım (özgün betik scipy kullanıyordu).

Yapay: sabit yıllık varyasyon katsayısı modeli (φ = 1 + CV² N0). K = 23'ün 5–8 kümesi yüksek N0'lı ve sahte zamansız,
kalanı N0 50 ve üç geçerli sahte zamanla. p0 0,50'ye karşı ve §4.6 kalibrasyonuyla α. Gerçek veri okumaz.
tr6a_inc2_b2.py'nin işlevlerini kullanır; tohum 8.
Kullanım: python3 -I -B tr6a_inc2_b3.py
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tr6a_inc2_b2 as B2  # noqa: E402

B2.rng = np.random.default_rng(8)


def main(R=20000):
    print("Sabit yıllık CV modeli: φ = 1 + CV² N0")
    for cv in (0.1, 0.2, 0.3):
        for N0 in (31.36, 100, 500, 1000):
            phi = 1 + cv * cv * N0
            D, _ = B2.kume(R, N0, phi)
            print(f"CV {cv} N0 {N0} φ {phi:.1f} P(D) {D.mean():.4f}")
    for cv in (0.1, 0.2, 0.3):
        for Nh, nh in ((1000, 5), (500, 5), (1000, 8)):
            K = 23
            nm = K - nh
            Dh, _ = B2.kume(R * nh, Nh, 1 + cv * cv * Nh)
            Dm, Dsm = B2.kume(R * nm, 50, 1 + cv * cv * 50)
            D = np.concatenate([Dh.reshape(R, nh), Dm.reshape(R, nm)], 1)
            Ds = Dsm.reshape(R, nm * 3)
            a = B2.yordam(D, Ds, np.ones_like(Ds), K)
            a5 = (D.sum(1) >= B2.ckp(K, 0.5)).mean()
            print(f"CV {cv} yüksek N0 {Nh} x{nh}, orta N0 50 x{nm} (J={3 * nm}): α p0 0,50 {a5:.4f}  kalibre {a:.4f}")


if __name__ == "__main__":
    main()
