#!/usr/bin/env python3
"""TR-11 koşu kodunun yapay serilerle sınanması (hiçbir gerçek tenv3 okunmaz ya da indirilmez).

Yapay dosyalar NGL tenv3 başlığı ve sütun düzeniyle yazılır (README_tenv3.txt: 23 sütun; site YYMMMDD yyyy.yyyy
__MJD week d reflon _e0(m) __east(m) ____n0(m) _north(m) u0(m) ____up(m) _ant(m) sig_e(m) sig_n(m) sig_u(m)
__corr_en __corr_eu __corr_nu _latitude(deg) _longitude(deg) __height(m)). Gürültü N0 (beyaz + kırpışma), boşluklar,
kod 1 sıçramaları, aykırı günler, tekrar eden günler eklenir. Yalnız gerçek üstveri (DataHoldings koordinatları) ve
bağlayıcı küme listesi okunur (Marmara ve seçim denetimleri için).

Kullanım: python3 -I -B kayit/turetme/tr11/tr11_test_yapay.py [-v]
"""
import os, sys
BURADA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURADA)
import argparse, contextlib, csv, datetime as dt, hashlib, io, json, math, shutil, tempfile, time, unittest
import numpy as np
import tr11_kosu as K

USTVERI_GERCEK = '/mnt/project-files/turetme/tr11-ustveri'


def sha(p): return K.sha256_dosya(p)


# ===================================================================== yapay dünya
B36 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
ONEK = 'P'   # yapay istasyon adı öneki (yapay seri tohumu ada bağlıdır)
def ad(i): return ONEK + B36[i // 1296 % 36] + B36[i // 36 % 36] + B36[i % 36]


def seri_uret(rng, ms, w0, H, bf=3.0, sw=1.5, hinge=(0.0, 0.0), adim=(), sicrama=8.0, aykiri=0.005):
    """Pencere içi tam ızgarada N0 gürültüsü + eğim + mevsimsel + kod 1 sıçramaları + aykırı günler; ms günlerinde."""
    n = K.N_PEN
    t = np.arange(n) / K.Y
    tH = (H - w0) / K.Y
    out = []
    for k in range(2):
        z1, z2 = rng.standard_normal(n), rng.standard_normal(n)
        y = sw * z1 + bf * K.DT ** 0.25 * K._Tz(z2, K._FHF)
        y += rng.uniform(-20, 20) * t + 2.0 * np.sin(2 * np.pi * t + rng.uniform(0, 6)) + 0.7 * np.cos(4 * np.pi * t)
        y += hinge[k] * np.maximum(0, t - tH)
        for s in adim:
            y += sicrama * (np.arange(n) + w0 >= s)
        a = rng.random(n) < aykiri
        y[a] += rng.choice([-1, 1], a.sum()) * rng.uniform(40, 80, a.sum())
        out.append(y[ms - w0])
    return out


class Dunya:
    """Küçük yapay ağ: yer, epok, istasyon, tenv3 dosyaları, üstveri, TR-2 sınıf dosyaları, manifest."""

    def __init__(self, kok, n_yer=100, iki_epok=40, bf=3.0, tohum=7, o4=True, hinge=(0.0, 0.0)):
        self.kok = kok
        rng = np.random.default_rng(tohum)
        for d in ('ustveri', 'tenv3', 'tr2', 'cikti'):
            os.makedirs(os.path.join(kok, d), exist_ok=True)
        T13, T18 = dt.date(2013, 1, 1), dt.date(2018, 1, 1)
        yerler = [(-50 + 10 * (i % 10) + 2.0, -170 + 20 * (i // 10) + 3.0) for i in range(n_yer)]
        if o4:
            yerler[-1] = (41.0, 33.33)       # Marmara kutusuna yakın yer (Ö4)
        self.koord, self.k1, ist_T = {}, {}, {}
        sayac = [0]
        def yeni(la, lo):
            s = ad(sayac[0]); sayac[0] += 1
            self.koord[s] = (la + rng.uniform(-0.5, 0.5), lo + rng.uniform(-0.5, 0.5)); return s
        yakin, ref = [], []
        for p, (la, lo) in enumerate(yerler):
            ny = int(rng.integers(5 if p < 4 else 3, 9))
            yakin.append([yeni(la, lo) for _ in range(ny)])
            ref.append([yeni(la + 3, lo) for _ in range(8)])
        if o4:
            self.koord[yakin[-1][0]] = (40.3, 33.0)    # kutuya ~127 km
        for p in range(n_yer - 1):                      # paylaşılan istasyon: p'nin referansı p+1'in yakını
            ref[p][0] = yakin[p + 1][0]
        self.liste = []
        for p, (la, lo) in enumerate(yerler):
            for T in ([T13, T18] if p < iki_epok else [T18]):
                self.liste.append(dict(T=T.isoformat(), la=la, lo=lo, y=list(yakin[p]), r=list(ref[p])))
                for s in yakin[p] + ref[p]:
                    ist_T.setdefault(s, set()).add(T)
        self.ozel = dict(doluluk=yakin[0][1], rank=yakin[1][1], indirme=yakin[2][1], o4=yakin[-1][0] if o4 else None,
                         sicrama=[])
        # kod 1 sıçramaları (pencere içinde, kenarlardan ve H'den uzak) ve rank düşüren geç sıçrama
        steps = []
        for s, Ts in sorted(ist_T.items()):
            for T in Ts:
                w0, H, w1 = K.pencere(T)
                if s == self.ozel['rank']:
                    self.k1.setdefault(s, []).append(w1 - 100)
                elif rng.random() < 0.06:
                    self.k1.setdefault(s, []).append(w0 + int(rng.integers(100, 900)))
                    self.ozel['sicrama'].append(s)
        for s, L in self.k1.items():
            for m in L:
                d = K.mjd_tarih(m)
                steps.append(f'{s}  {d.year % 100:02d}{K.AYLAR[d.month - 1]}{d.day:02d}  1  Antenna_Type_Changed')
        steps.append(f'{ad(0)}  94JAN17  2   363.078   201.965  6.7 ci3144585')
        U = os.path.join(kok, 'ustveri')
        open(os.path.join(U, 'steps.txt'), 'w').write('\n'.join(steps) + '\n')
        with open(os.path.join(U, 'DataHoldings.txt'), 'w') as f:
            f.write('Sta  Lat(deg)   Long(deg) Hgt(m)  X(m)           Y(m)         Z(m)          Dtbeg      Dtend      '
                    'Dtmod      NumSol StaOrigName\n')
            for s, (la, lo) in sorted(self.koord.items()):
                f.write(f'{s} {la:8.4f} {lo:9.4f} 100.000 0.0 0.0 0.0 2005-01-01 2025-06-01 2025-09-25 5000\n')
        # TR-2 sınıf dosyaları: yer 5 B (mekanizmasız M6), yer 6 A (iki doğrultu atımlı)
        R2 = os.path.join(kok, 'tr2')
        bas = 'time,latitude,longitude,depth,mag,id,type\n'
        ev = [('2001-05-05T00:00:00Z', yerler[5][0], yerler[5][1], 10, 6.2, 'b1'),
              ('2002-05-05T00:00:00Z', yerler[6][0], yerler[6][1], 10, 6.3, 'a1'),
              ('2003-05-05T00:00:00Z', yerler[6][0] + .2, yerler[6][1], 12, 6.1, 'a2')]
        open(os.path.join(R2, 'm6_havuz.csv'), 'w').write(bas + ''.join(f'{t},{a},{b},{z},{m},{i},earthquake\n'
                                                                     for t, a, b, z, m, i in ev))
        open(os.path.join(R2, 'birincil_aday.csv'), 'w').write(bas + ''.join(f'{t},{a},{b},{z},{m},{i},earthquake\n'
                                                                        for t, a, b, z, m, i in ev[1:]))
        open(os.path.join(R2, 'birincil_aday_fm.csv'), 'w').write(bas)
        open(os.path.join(R2, 'mekanizma.jsonl'), 'w').write(
            json.dumps(dict(id='a1', mt=[{'nodal-plane-1-rake': '5', '_w': 1}])) + '\n'
            + json.dumps(dict(id='a2', mt=[{'nodal-plane-1-rake': '175', '_w': 1}])) + '\n')
        self.yerler = yerler
        # tenv3 dosyaları
        man = {}
        for s, Ts in sorted(ist_T.items()):
            if s == self.ozel['indirme']:
                man[s] = dict(durum='hata', hata='HTTP 404')
                continue
            satir = [K.TENV3_BASLIK]
            for T in sorted(Ts):
                w0, H, w1 = K.pencere(T)
                tum = np.arange(w0, w1 + 1)
                tut = rng.random(len(tum)) > 0.10
                g0 = w0 + int(rng.integers(50, 900)); tut[(tum >= g0) & (tum < g0 + 60)] = False
                if s == self.ozel['doluluk']:
                    tut &= ~((tum >= H) & (rng.random(len(tum)) < 0.5))
                adim = [m for m in self.k1.get(s, []) if w0 <= m <= w1]
                if s == self.ozel['rank']:
                    tut &= tum < adim[0]
                ms = tum[tut]
                E, N = seri_uret(rng, ms, w0, H, bf=bf, adim=adim, hinge=hinge)
                la, lo = self.koord[s]
                L = K.tenv3_satirlari(s, ms, E + 1234.5, N - 987.6, lat=la, lon=lo, baslik=False)
                # tekrar eden gün: ikinci kopya bozuk değerli (ilk alınmalı)
                for j in (10, 500):
                    p_ = L[j].split(); p_[8] = f'{float(p_[8]) + 1.0:9.6f}'
                    L.insert(j + 1, ' '.join(p_))
                satir += L
            # pencere sonrası satırlar (2018-2025): Ö4 için; okunmamalı
            son = K.mjd(dt.date(2025, 6, 1))
            ms2 = np.arange(max(K.pencere(T)[2] for T in Ts) + 1, son)
            la, lo = self.koord[s]
            satir += K.tenv3_satirlari(s, ms2, np.zeros(len(ms2)), np.zeros(len(ms2)), lat=la, lon=lo, baslik=False)
            yol = os.path.join(kok, 'tenv3', f'{s}.tenv3')
            open(yol, 'w').write('\n'.join(satir) + '\n')
            man[s] = dict(durum='tamam', sha256=sha(yol), bayt=os.path.getsize(yol))
        self.manifest = os.path.join(kok, 'tenv3', 'tr11_indirme_manifest.json')
        json.dump(dict(istasyonlar=man), open(self.manifest, 'w'))
        self.liste_yol = os.path.join(kok, 'liste.json')
        json.dump(self.liste, open(self.liste_yol, 'w'))
        self.ayar = K.Ayar(liste_sha256=sha(self.liste_yol),
                           ustveri_sha16={a: sha(os.path.join(U, a))[:16] for a in ('DataHoldings.txt', 'steps.txt')},
                           tr2_sha16={a: sha(os.path.join(R2, a))[:16] for a in K.TR2_SHA16},
                           M=400, B=200, surec=4, bf_izgara_n=31)

    def arg(self, cikti=None, o4_sil=False):
        c = cikti or os.path.join(self.kok, 'cikti')
        os.makedirs(c, exist_ok=True)
        return argparse.Namespace(tenv3=os.path.join(self.kok, 'tenv3'), manifest=self.manifest,
                                  ustveri=os.path.join(self.kok, 'ustveri'), tr2=os.path.join(self.kok, 'tr2'),
                                  liste=self.liste_yol, cikti=c, surec=4, yalniz_denetim=False, o4_sil=o4_sil)


@contextlib.contextmanager
def yamala(**kw):
    eski = {k: getattr(K, k) for k in kw}
    for k, v in kw.items():
        setattr(K, k, v)
    try:
        yield
    finally:
        for k, v in eski.items():
            setattr(K, k, v)


SESSIZ = lambda s: None


# ===================================================================== birim testleri
class Tenv3Bicim(unittest.TestCase):
    def test_yaz_oku_gidis_donus(self):
        ms = np.arange(58000, 58010)
        E = np.linspace(-3, 3, 10); N = np.linspace(5, -5, 10)
        L = K.tenv3_satirlari('ABCD', ms, E, N, lat=38.6, lon=-112.84)
        self.assertEqual(L[0].split()[3], '__MJD')
        self.assertEqual(len(L[1].split()), 23)
        (s,), b = K.tenv3_ayristir(L, [(58000, 58009)])
        self.assertTrue(b['baslik'])
        np.testing.assert_allclose(s[1] - s[1][0], E - E[0], atol=2e-3)   # 1 µm yuvarlama
        np.testing.assert_allclose(s[2] - s[2][0], N - N[0], atol=2e-3)

    def test_baslik_uyusmazligi_durdurur(self):
        L = K.tenv3_satirlari('ABCD', np.arange(5), np.zeros(5), np.zeros(5))
        L[0] = L[0].replace('_e0(m) __east(m)', '__east(m) _e0(m)')
        with self.assertRaises(K.Tenv3Hata):
            K.tenv3_ayristir(L, [(0, 4)])

    def test_basliksiz_konumsal(self):
        L = K.tenv3_satirlari('ABCD', np.arange(100, 105), np.arange(5.0), np.zeros(5), baslik=False)
        (s,), b = K.tenv3_ayristir(L, [(100, 104)])
        self.assertFalse(b['baslik']); self.assertEqual(len(s[0]), 5)

    def test_tekrar_ilk_alinir_pencere_disi_atilir(self):
        L = K.tenv3_satirlari('ABCD', np.array([9, 10, 10, 11, 12]), np.array([0., 1., 99., 2., 3.]), np.zeros(5))
        (s,), b = K.tenv3_ayristir(L, [(10, 11)])
        self.assertEqual(list(s[0]), [10, 11]); self.assertEqual(b['tekrar'], 1)
        self.assertAlmostEqual(s[1][1] - s[1][0], 1.0, places=2)

    def test_w1_sonrasi_okunmaz(self):
        """Ö4: son pencerenin sonundan büyük MJD'li ilk satırda okuma durur; sonraki satırlar hiç istenmez."""
        L = K.tenv3_satirlari('ABCD', np.arange(100, 110), np.zeros(10), np.zeros(10))
        istenen = []
        def uret():
            for i, l in enumerate(L):
                istenen.append(i)
                yield l
            raise AssertionError('dosya sonuna kadar okundu')
        (s,), b = K.tenv3_ayristir(uret(), [(100, 104)])
        self.assertTrue(b['durdu']); self.assertEqual(max(istenen), 6)   # başlık + 5 satır + ilk taşan satır
        self.assertEqual(len(s[0]), 5)


class MentesemModeli(unittest.TestCase):
    T = dt.date(2018, 1, 1)

    def test_katsayi_kurtarimi_gurultusuz(self):
        w0, H, w1 = K.pencere(self.T)
        ms = np.arange(w0, w1 + 1)[::2]
        t = (ms - w0) / K.Y; tH = (H - w0) / K.Y
        adim = [w0 + 400]
        E = 3 + 7 * t + 2 * np.sin(2 * np.pi * t) + 2.5 * np.maximum(0, t - tH) + 6.0 * (ms >= adim[0])
        N = -1 - 4 * t + 1 * np.cos(4 * np.pi * t) - 1.5 * np.maximum(0, t - tH)
        dv, neden = K.olc(ms, E, N, w0, H, adim)
        self.assertIsNone(neden)
        self.assertAlmostEqual(dv[0], 2.5, places=6); self.assertAlmostEqual(dv[1], -1.5, places=6)
        dv2, _ = K.olc(ms, E, N, w0, H, adim, ek_dogu=3.0)
        self.assertAlmostEqual(dv2[0] - dv[0], 3.0, places=6); self.assertAlmostEqual(dv2[1] - dv[1], 0.0, places=9)

    def test_katsayi_kurtarimi_gurultulu_yansiz(self):
        rng = np.random.default_rng(3)
        w0, H, w1 = K.pencere(self.T)
        ms = np.arange(w0, w1 + 1)
        ms = ms[rng.random(len(ms)) > 0.2]
        v = K.sigma_bilesenleri(ms, w0, H, [])
        sd = K.sigma_h(v)
        d = []
        for _ in range(150):
            E, N = seri_uret(rng, ms, w0, H, hinge=(2.0, -1.0), aykiri=0.0)
            d.append(K.olc(ms, E, N, w0, H, [])[0])
        d = np.array(d)
        self.assertLess(abs(d[:, 0].mean() - 2.0), 4 * sd / math.sqrt(150))
        self.assertLess(abs(d[:, 1].mean() + 1.0), 4 * sd / math.sqrt(150))

    def test_sicrama_terimi(self):
        w0, H, w1 = K.pencere(self.T)
        ms = np.arange(w0, w1 + 1)
        t = (ms - w0) / K.Y
        s = w0 + 1300                                 # yakın dönemde (H'den > 30 g sonra)
        E = 10.0 * (ms >= s); N = np.zeros(len(ms))
        with_ = K.olc(ms, E, N, w0, H, [s])[0]
        without = K.olc(ms, E, N, w0, H, [])[0]
        self.assertAlmostEqual(with_[0], 0.0, places=6)
        self.assertGreater(abs(without[0]), 1.0)       # sıçrama terimi olmadan menteşe sapar

    def test_mad_ayiklamasi(self):
        rng = np.random.default_rng(5)
        w0, H, w1 = K.pencere(self.T)
        ms = np.arange(w0, w1 + 1)
        t = (ms - w0) / K.Y; tH = (H - w0) / K.Y
        temiz = 1.5 * rng.standard_normal(len(ms)) + 2.0 * np.maximum(0, t - tH)
        kirli = temiz.copy(); a = rng.choice(len(ms), 30, replace=False); kirli[a] += 200.0
        dv, _ = K.olc(ms, kirli, temiz, w0, H, [])
        X = K.tasarim(ms, w0, H, [])
        b1 = np.linalg.lstsq(X, kirli - kirli[0], rcond=None)[0]
        r = kirli - kirli[0] - X @ b1
        tut = np.abs(r - np.median(r)) <= 5 * 1.4826 * np.median(np.abs(r - np.median(r)))
        self.assertTrue(set(a) <= set(np.where(~tut)[0]))
        b2 = np.linalg.lstsq(X[tut], (kirli - kirli[0])[tut], rcond=None)[0]
        self.assertAlmostEqual(dv[0], b2[-1], places=9)
        ham = np.linalg.lstsq(X, kirli, rcond=None)[0][-1]
        self.assertGreater(abs(ham - dv[0]), 0.05)

    def test_mad_sifir_ayiklama_yok(self):
        """Artıklar tam sıfırsa MAD = 0: ayıklama yapılmaz, ilk uydurma kullanılır (hata vermez)."""
        w0, H, w1 = K.pencere(self.T)
        ms = np.arange(w0, w1 + 1)
        z = np.full(len(ms), 7.0)
        dv, neden = K.olc(ms, z, z, w0, H, [])
        self.assertIsNone(neden); self.assertEqual(dv, (0.0, 0.0))

    def test_doluluk_ve_rank(self):
        w0, H, w1 = K.pencere(self.T)
        tum = np.arange(w0, w1 + 1)
        z = np.zeros(len(tum))
        r = K.ist_hazirla(tum, z, z, self.T, [])
        self.assertIsNone(r['neden'])
        # yakın dönem 0,59 -> düşer; 0,60 -> kalır
        for oran, beklenen in ((0.59, 'doluluk'), (0.60, None)):
            nyak = int(math.ceil(oran * 730)) if oran == 0.60 else int(oran * 730)
            ms = np.concatenate([tum[tum < H], tum[tum >= H][:nyak]])
            self.assertEqual(K.ist_hazirla(ms, ms * 0.0, ms * 0.0, self.T, [])['neden'], beklenen)
        ms = np.concatenate([tum[tum < H][:int(0.59 * 1096)], tum[tum >= H]])
        self.assertEqual(K.ist_hazirla(ms, ms * 0.0, ms * 0.0, self.T, [])['neden'], 'doluluk')
        # sıçramadan sonra veri yok -> rank
        s = w1 - 100
        ms = tum[tum < s]
        self.assertEqual(K.ist_hazirla(ms, ms * 0.0, ms * 0.0, self.T, [s])['neden'], 'rank')
        self.assertEqual(K.olc(ms, ms * 0.0, ms * 0.0, w0, H, [s])[1], 'rank')


class SOlcusu(unittest.TestCase):
    def test_elle_ornek(self):
        y = np.array([[1, 0], [0, 2], [3, 4]], float)
        r = np.array([[0, 0], [1, 1], [2, 0]], float)      # bileşen medyanı (1, 0)
        self.assertAlmostEqual(float(K.S_hesapla(y, r)), math.sqrt(5), places=12)
        y4 = np.array([[1, 0], [0, 2], [3, 4], [1, 3]], float)   # boylar 0, √5, √20, 3 -> (√5 + 3)/2
        self.assertAlmostEqual(float(K.S_hesapla(y4, r)), (math.sqrt(5) + 3) / 2, places=12)
        r4 = np.array([[0, 0], [1, 1], [2, 0], [5, 1]], float)   # çift referans: medyan (1,5; 0,5)
        self.assertAlmostEqual(float(K.S_hesapla(y[:1], r4)), math.hypot(0.5, 0.5), places=12)
        # toplu biçim tek tek ile aynı
        Y = np.stack([y, y + 1]); R = np.stack([r, r * 2])
        np.testing.assert_allclose(K.S_hesapla(Y, R), [K.S_hesapla(y, r), K.S_hesapla(y + 1, r * 2)])
        self.assertAlmostEqual(float(K.S_refsiz(y)), 2.0)     # boylar 1, 2, 5


class Gurultu(unittest.TestCase):
    def test_bosluksuz_sigma_beklenti_ile_ayni(self):
        import beklenti_gurultu as BG
        T = dt.date(2018, 1, 1); w0, H, w1 = K.pencere(T)
        v = K.sigma_bilesenleri(np.arange(w0, w1 + 1), w0, H, [])
        self.assertAlmostEqual(v[0], BG.VW, places=10)
        self.assertAlmostEqual(v[1], BG.VF * 1.0, delta=1e-9 * BG.VF)
        self.assertAlmostEqual(v[2], BG.VR, delta=1e-8 * BG.VR)
        self.assertAlmostEqual(K.sigma_h(v), 0.748, places=3)

    def test_sigma_analitik_monte_carlo(self):
        rng = np.random.default_rng(11)
        T = dt.date(2013, 1, 1); w0, H, w1 = K.pencere(T)
        tum = np.arange(w0, w1 + 1)
        tut = rng.random(len(tum)) > 0.25
        tut[(tum > w0 + 300) & (tum < w0 + 420)] = False
        ms = tum[tut]; adim = [w0 + 600]
        v = K.sigma_bilesenleri(ms, w0, H, adim)
        an = K.sigma_h(v)
        X = K.tasarim(ms, w0, H, adim)
        n = 1500
        Z = rng.standard_normal((2, n, K.N_PEN))
        seri = 1.5 * Z[0] + 3.0 * K.DT ** 0.25 * np.fft.irfft(np.fft.rfft(Z[1], K.NFFT) * K._FHF, K.NFFT)[:, :K.N_PEN]
        b = np.linalg.lstsq(X, seri[:, ms - w0].T, rcond=None)[0][-1]
        self.assertLess(abs(b.std(ddof=1) / an - 1), 0.06, (b.std(), an))
        # tam boru hattı (MAD ayıklamalı) ile de uyumlu
        d = [K.olc(ms, s1[ms - w0], s2[ms - w0], w0, H, adim)[0][0] for s1, s2 in zip(seri[:300], seri[300:600])]
        self.assertLess(abs(np.std(d, ddof=1) / an - 1), 0.12)

    def test_yapay_seri_tohum(self):
        a = K.yapay_seri('ABCD', '2018-01-01'); b = K.yapay_seri('ABCD', '2018-01-01')
        c = K.yapay_seri('ABCD', '2013-01-01')
        np.testing.assert_array_equal(a[0], b[0]); self.assertFalse(np.allclose(a[0], c[0]))
        tohum = int(hashlib.sha256(b'ABCD|2018-01-01').hexdigest()[:16], 16) ^ 20261111
        z = np.random.default_rng(tohum).standard_normal((4, 1826))
        np.testing.assert_allclose(a[0][:3], 1.5 * z[0][:3] + 3.0 * K.DT ** 0.25 * (np.convolve(z[2], K.HF)[:3]))


class Nicelik(unittest.TestCase):
    def test_agirlikli_nicelik_np_quantile_ile_ayni(self):
        rng = np.random.default_rng(1)
        for _ in range(20):
            dl = [rng.standard_normal(int(rng.integers(5, 40))) for _ in range(12)]
            w = rng.integers(0, 4, 12); w[0] = max(w[0], 1)
            v, s = K.havuz(dl)
            rep = np.concatenate([np.repeat(d, c) for d, c in zip(dl, w)])
            for q in (0.05, 0.5, 0.9, 0.95, 0.99):
                self.assertEqual(K.agirlikli_nicelik(v, s, w, (q,))[0], np.quantile(rep, q, method='linear'))

    def test_bootstrap_tekrarlanabilir(self):
        rng = np.random.default_rng(2)
        S = rng.random(60); birim = np.repeat(np.arange(15), 4)
        hv = {'N0': K.havuz([rng.random(50) for _ in range(60)])}
        a = K.bootstrap(S, birim, hv, 100, 2); b = K.bootstrap(S, birim, hv, 100, 1)
        for x, y in zip(a, b):
            np.testing.assert_array_equal(x['S'], y['S']); np.testing.assert_array_equal(x['N0'], y['N0'])
        sec = np.random.default_rng(20261112).integers(0, 15, size=(100, 15))
        w = np.bincount(sec[7], minlength=15)[birim]
        np.testing.assert_array_equal(a[7]['S'], np.quantile(np.repeat(S, w), K.QS))


class BfCozumu(unittest.TestCase):
    def test_bilinen_bf_geri_bulunur(self):
        """Bilinen b_f ile üretilmiş Δv'lerden (maskeli σ_h ile) b_f* geri bulunur."""
        rng = np.random.default_rng(4)
        T = dt.date(2018, 1, 1); w0, H, w1 = K.pencere(T)
        tum = np.arange(w0, w1 + 1)
        kayit, kps = {}, []
        for k in range(300):
            ny = int(rng.integers(3, 9))
            y = [f'Y{k}_{i}' for i in range(ny)]; r = [f'R{k}_{i}' for i in range(8)]
            for s in y + r:
                ms = tum[rng.random(len(tum)) > rng.uniform(0, 0.35)]
                kayit[(s, T)] = dict(v=K.sigma_bilesenleri(ms, w0, H, []))
            kps.append(dict(T=T, y=y, r=r))
        for bf_gercek in (2.2, 4.5):
            S = []
            for kp in kps:
                sy = np.array([K.sigma_h(kayit[(s, T)]['v'], bf=bf_gercek) for s in kp['y']])
                sr = np.array([K.sigma_h(kayit[(s, T)]['v'], bf=bf_gercek) for s in kp['r']])
                S.append(float(K.S_hesapla(rng.standard_normal((len(sy), 2)) * sy[:, None],
                                           rng.standard_normal((len(sr), 2)) * sr[:, None])))
            mc = K.MC(kps, kayit, 400)
            yy = {k: kp['y'] for k, kp in enumerate(kps)}; rr = {k: kp['r'] for k, kp in enumerate(kps)}
            (b, bayrak), izg = K.bf_hazirla(mc, list(range(300)), yy, rr, float(K.nicelik(S, 0.95)),
                                            K.Ayar(M=400, surec=4, bf_izgara_n=21), SESSIZ)
            self.assertIsNone(bayrak)
            self.assertLess(abs(b / bf_gercek - 1), 0.12, (b, bf_gercek))
            # ızgara çözümü (ağırlık 1) nokta çözümüne yakın; q95_N0(b) tekdüze
            qg = [K.agirlikli_nicelik(v, s, np.ones(300, np.int64), (0.95,))[0] for v, s in izg['h']]
            self.assertTrue(np.all(np.diff(qg) > 0))
            bi, _ = K._bf_izgara_coz(izg, float(K.nicelik(S, 0.95)), np.ones(300, np.int64))
            self.assertLess(abs(bi - b), 0.01 * b)


class Ceviri(unittest.TestCase):
    def test_G_hucreleri_elle(self):
        self.assertAlmostEqual(K.G(10, 20, 0.0), math.atan(2) / math.pi, places=12)
        self.assertAlmostEqual(round(K.G(10, 20, 0.0), 3), 0.352)
        self.assertAlmostEqual(round(K.G(5, 5, math.pi / 2), 3), 0.250)       # aynı yan: arctan(D/x)/π
        self.assertAlmostEqual(round(K.G(10, 5, -math.pi / 2), 3), 0.648)     # karşı yan: ½ + arctan(x/D)/π
        self.assertAlmostEqual(round(K.G(15, 50, -math.pi / 2), 3), 0.907)
        self.assertAlmostEqual(round(K.G(15, 5, 0.0), 3), 0.102)

    def test_tablo_a_c_ve_kurallar(self):
        k8 = dict(kume_pencere=371, q95=dict(nokta=1.6, aralik=[1.5, 1.8]))
        S8 = np.array([0.9, 1.0, 1.1])
        c = K.ceviri(k8, None, S8, None)
        self.assertEqual(len(c['tablo']), 45)
        kok = math.sqrt(1.5 ** 2 - 1.0 ** 2)
        self.assertAlmostEqual(c['kok_L'], kok)
        hucre = [t for t in c['tablo'] if t['geometri'] == 'karsi_yan' and t['D'] == 5 and t['x'] == 50][0]
        self.assertAlmostEqual(hucre['ds_alt'], kok / (0.5 + math.atan(10) / math.pi))
        self.assertAlmostEqual(c['a'], hucre['ds_alt'])                       # en küçük hücre
        self.assertAlmostEqual(c['c'], kok / (math.atan(2) / math.pi))
        self.assertIn('kapatamadı', c['o3']); self.assertIsNotNone(c['c_notu'])
        self.assertIn(K.f2(c['a']), c['yorum'])
        # a >= 10 -> kapalı; c >= 5 -> not yok
        c2 = K.ceviri(dict(kume_pencere=400, q95=dict(nokta=12, aralik=[11.0, 13.0])), None, np.array([1.0]), None)
        self.assertGreaterEqual(c2['a'], 10); self.assertIn('kapalı', c2['o3']); self.assertIsNone(c2['c_notu'])
        # < 300 KP -> havuz
        c3 = K.ceviri(dict(kume_pencere=100), dict(q95=dict(nokta=1.6, aralik=[1.5, 1.8])), None, S8)
        self.assertTrue(c3['katman'].startswith('havuz'))


class UstveriDenetimleri(unittest.TestCase):
    """Yalnız üstveri (DataHoldings koordinatları) ve bağlayıcı liste; seri okunmaz."""

    def test_liste_secim_ve_marmara(self):
        yol = os.path.join(BURADA, 'tr11_kume_listesi.json')
        self.assertEqual(sha(yol), K.LISTE_SHA256)
        L = json.load(open(yol))
        an = [hashlib.sha256(f'{k["T"]}|{k["la"]:.4f}|{k["lo"]:.4f}'.encode()).hexdigest() for k in L]
        self.assertEqual(len(L) // 2, 401); self.assertEqual(len(set(an)), len(L))
        if not os.path.exists(os.path.join(USTVERI_GERCEK, 'DataHoldings.txt')):
            self.skipTest('üstveri yok')
        ko = K.dataholdings_oku(os.path.join(USTVERI_GERCEK, 'DataHoldings.txt'))
        ist = sorted({s for k in L for s in k['y'] + k['r']})
        self.assertEqual(len(ist), 4730)
        self.assertFalse(any(K.marmara_icinde(*ko[s]) for s in ist))
        uz = {s: K.marmara_uzaklik(*ko[s]) for s in ist}
        o4 = sorted(s for s in ist if uz[s] < 150)
        self.assertEqual(o4, sorted(['CMLD', 'AFYN', 'KRBK', 'AKHR', 'KLUU']))
        for s, km in (('CMLD', 82), ('AFYN', 85), ('KRBK', 98), ('AKHR', 126), ('KLUU', 143)):
            self.assertAlmostEqual(uz[s], km, delta=1.5)


# ===================================================================== uçtan uca (yapay ağ)
class UctanUca(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix='tr11_test_')
        t0 = time.time()
        cls.d = Dunya(os.path.join(cls.tmp, 'ana'), n_yer=100, iki_epok=40)
        cls.kurulum = time.time() - t0

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def _kos(self, cikti, o4_sil=False, ayar=None):
        return K.kos(self.d.arg(cikti, o4_sil), ayar or self.d.ayar, kayit_fn=SESSIZ)

    def test_2_tam_kosu_tek_koru_tekrarlanabilir(self):
        t0 = time.time()
        c1 = os.path.join(self.tmp, 'c1')
        s = self._kos(c1)
        sure = time.time() - t0
        print(f'\n  [uçtan uca: kurulum {self.kurulum:.0f} sn, koşu {sure:.0f} sn; KP {s["dusme"]["kume_pencere_gecerli"]}; '
              f'(i) {s["kod_denetimi"]["i"]["oran"]:.3f}; (ii-b) {s["kod_denetimi"]["ii_b"]["olculen_medyan_fark"]:.3f}'
              f' / m* {s["kod_denetimi"]["ii_b"]["m_yildiz"]:.3f}; (ii-a) d_E {s["kod_denetimi"]["ii_a"]["medyan_dE"]:.4f}'
              f' |d_N| {s["kod_denetimi"]["ii_a"]["medyan_abs_dN"]:.4f}; b_f* {s["ana"]["bf_yildiz"]["nokta"]:.2f} '
              f'{s["ana"]["bf_yildiz"]["aralik"]}; ρ {s["ana"]["rho"]["nokta"]:.3f}; hüküm {s["hukum"]}]')
        self.assertIn(s['hukum'], ("taban N0-yüksek'ten büyük", "taban N0-düşük'ten küçük", 'taban N0 bandında (b_f 2–4)'))
        self.assertTrue(s['kod_denetimi']['i']['gecti']); self.assertTrue(s['kod_denetimi']['ii_b']['gecti'])
        self.assertTrue(s['kod_denetimi']['ii_a']['gecti'])
        self.assertAlmostEqual(s['kod_denetimi']['ii_a']['medyan_dE'], 3.0, delta=0.02)
        # düşmeler: doluluk, rank, indirme
        n = s['dusme']['istasyon_T_neden']
        self.assertGreaterEqual(n.get('doluluk', 0), 1); self.assertGreaterEqual(n.get('rank', 0), 1)
        self.assertGreaterEqual(n.get('indirme', 0), 1)
        self.assertEqual(s['dusme']['indirme_hatasi_istasyon'], [self.d.ozel['indirme']])
        self.assertIn(self.d.ozel['o4'], s['o4']['istasyonlar'])
        self.assertTrue(all(K.marmara_uzaklik(*self.d.koord[x]) < 150 for x in s['o4']['istasyonlar']))
        self.assertGreater(s['dusme']['okuma']['tekrar'], 0)
        # b_f N0 (3,0) ile üretildi: aralık 3'ü kabaca kapsamalı (MAD ve boşluk etkisi küçük)
        self.assertLess(abs(s['ana']['bf_yildiz']['nokta'] - 3.0), 0.8)
        self.assertEqual(len(s['marmara_cevirisi']['tablo']), 45)
        self.assertEqual(s['kirilim']['sinif']['A']['hukum'], 'güç yok')
        self.assertIn('q95', s['kirilim']['sinif']['D'])
        self.assertIsNone(s['ana']['q99'])          # < 300 KP
        for ad in ('referans_farki_yok', 'yer_bootstrap', 'en_buyuk_blok_disarida', 'kod1_disarida', 'yer_agirlikli'):
            self.assertIn('q95', s['bilgi'][ad], ad)
        md = open(os.path.join(c1, 'tr11_sonuc.md')).read()
        self.assertIn('Bu ölçüm ve bu model altında', md)
        for yasak in ('olasılığı %', 'İstanbul depremi olasılığı', 'yol açık hükmü verir'):
            self.assertNotIn(yasak, md)
        # tek koşu koruması
        with self.assertRaises(K.KosuDur):
            self._kos(c1)
        # tekrarlanabilirlik (bootstrap ve MC tohumları sabit)
        s2 = self._kos(os.path.join(self.tmp, 'c2'), o4_sil=True)
        self.assertEqual(json.dumps(s['ana'], sort_keys=True), json.dumps(s2['ana'], sort_keys=True))
        self.assertEqual(json.dumps(s['kirilim'], sort_keys=True), json.dumps(s2['kirilim'], sort_keys=True))
        # Ö4 dosyası koşudan sonra silindi
        self.assertFalse(os.path.exists(os.path.join(self.d.kok, 'tenv3', f'{self.d.ozel["o4"]}.tenv3')))

    def test_1_kod_gecersiz_yollari_gercek_S_hesaplanmaz(self):
        o4 = os.path.join(self.d.kok, 'tenv3', f'{self.d.ozel["o4"]}.tenv3')
        if not os.path.exists(o4):
            self.skipTest('Ö4 dosyası test 2 tarafından silindi (sıra)')
        def yasak(*a, **k):
            raise AssertionError('gerçek S hesaplandı')
        for i, yama in enumerate((dict(ORAN_ARALIK=(5.0, 6.0)), dict(IIB_ARALIK=(1.5, 1.6)),
                                  dict(D_E_ARALIK=(3.5, 3.6)))):
            c = os.path.join(self.tmp, f'g{i}')
            with yamala(ana_olcum=yasak, **yama):
                s = self._kos(c)
            self.assertEqual(s['hukum'], 'geçersiz (kod)')
            j = json.load(open(os.path.join(c, 'tr11_sonuc.json')))
            self.assertNotIn('ana', j); self.assertNotIn('kume_pencere_tablosu', j)
            if i < 2:
                self.assertNotIn('ii_a', j['kod_denetimi'])

    def test_3_iib_beklenti_yansiz(self):
        """(ii-b): yapay serilerden ölçülen medyan(S_eklenen − S_özgün), farklı gerçekleşmelerde ortalama olarak
        Monte Carlo m*'a eşit (tek gerçekleşme küçük ağda ±%10 dışına düşebilir; gerçek koşuda 401 KP ile sd ≈ 0,035)."""
        d = self.d; a = d.arg(os.path.join(self.tmp, 'iib'))
        dd = K.girdi_denetimi(a, d.ayar)
        k1 = K.steps_kod1_oku(os.path.join(a.ustveri, 'steps.txt'))
        ist_T = {}
        for k in dd['liste']:
            for s_ in k['y'] + k['r']:
                ist_T.setdefault(s_, set()).add(dt.date.fromisoformat(k['T']))
        K._G.update(tenv3=a.tenv3, ist_T=ist_T, o4=set(dd['o4']), manifest_sha=dd['manifest_sha'], k1=k1)
        kayit = {}
        for s_ in ist_T:
            if s_ in dd['basarisiz'] or not os.path.exists(os.path.join(a.tenv3, f'{s_}.tenv3')):
                continue
            for T_, r in K._oku_is(s_)[1].items():
                kayit[(s_, T_)] = r
        an = [hashlib.sha256(f'{k["T"]}|{k["la"]:.4f}|{k["lo"]:.4f}'.encode()).hexdigest() for k in dd['liste']]
        sec = set(sorted(range(len(an)), key=lambda i: an[i])[:len(an) // 2])
        kps = []
        for i, k in enumerate(dd['liste']):
            T_ = dt.date.fromisoformat(k['T'])
            ok = lambda x: kayit.get((x, T_), {}).get('neden', 'yok') is None
            y = [x for x in k['y'] if ok(x)]; r = [x for x in k['r'] if ok(x)]
            if i in sec and len(y) >= 3 and len(r) >= 3:
                kps.append(dict(T=T_, y=y, r=r))
        mc = K.MC(kps, kayit, 1000)
        m_yildiz = float(np.median(np.concatenate([mc.cekilis(k, ek=3.0) - mc.cekilis(k) for k in range(len(kps))])))
        K._G.update(kayit=kayit, koord=d.koord, ekle=set(kayit))
        asil = K.yapay_seri
        olc = []
        try:
            for e in range(5):
                K.yapay_seri = lambda sta, Ts, sw=K.SW, bf=K.BF0, e=e: asil(f'{sta}#{e}', Ts, sw, bf)
                yo = {}
                fark = []
                for kp in kps:
                    for x in kp['y'] + kp['r']:
                        if (x, kp['T']) not in yo:
                            yo[(x, kp['T'])] = K._yapay_is((x, kp['T']))[1:3]
                    R = np.array([yo[(x, kp['T'])][0] for x in kp['r']])
                    Y0 = np.array([yo[(x, kp['T'])][0] for x in kp['y']])
                    Ye = np.array([yo[(x, kp['T'])][1] for x in kp['y']])
                    fark.append(float(K.S_hesapla(Ye, R) - K.S_hesapla(Y0, R)))
                olc.append(np.median(fark))
        finally:
            K.yapay_seri = asil
        print(f'\n  [(ii-b) 5 gerçekleşme: {np.round(olc, 3)}; ortalama {np.mean(olc):.3f}; m* {m_yildiz:.3f}]')
        self.assertLess(abs(np.mean(olc) - m_yildiz), 0.09)

    def test_0_girdi_denetimleri(self):
        d = self.d
        # liste sha256 uyuşmazlığı
        import dataclasses
        with self.assertRaises(K.KosuDur):
            K.kos(d.arg(os.path.join(self.tmp, 'x1')), dataclasses.replace(d.ayar, liste_sha256='0' * 64), SESSIZ)
        # üstveri sha uyuşmazlığı
        with self.assertRaises(K.KosuDur):
            K.kos(d.arg(os.path.join(self.tmp, 'x2')),
                  dataclasses.replace(d.ayar, ustveri_sha16={'steps.txt': '887501a438c41c34'}), SESSIZ)
        # indirme hatası payı > %5
        a = d.arg(os.path.join(self.tmp, 'x3'))
        man = json.load(open(d.manifest))
        for s in list(man['istasyonlar'])[:100]:
            man['istasyonlar'][s] = dict(durum='hata')
        a.manifest = os.path.join(self.tmp, 'man_bozuk.json'); json.dump(man, open(a.manifest, 'w'))
        with self.assertRaises(K.KosuDur) as e:
            K.kos(a, d.ayar, SESSIZ)
        self.assertIn('%5', str(e.exception))
        # yalnız denetim kipi: tenv3 okunmaz, çıktı yazılmaz
        a = d.arg(os.path.join(self.tmp, 'x4')); a.yalniz_denetim = True
        self.assertIsNone(K.kos(a, d.ayar, SESSIZ))
        self.assertEqual(os.listdir(a.cikti), [])


class KapiVeMarmara(unittest.TestCase):
    def test_veri_yok_ve_kutu_istasyonu(self):
        tmp = tempfile.mkdtemp(prefix='tr11_test_k_')
        try:
            d = Dunya(os.path.join(tmp, 'k'), n_yer=12, iki_epok=4, o4=False)
            s = K.kos(d.arg(), d.ayar, kayit_fn=SESSIZ)
            self.assertEqual(s['hukum'], 'veri yok')
            self.assertNotIn('kod_denetimi', s); self.assertNotIn('ana', s)
            # listede Marmara kutusu istasyonu -> durur
            L = json.load(open(d.liste_yol))
            dh = os.path.join(d.kok, 'ustveri', 'DataHoldings.txt')
            txt = open(dh).read().replace(f'{L[0]["y"][0]} ', f'{L[0]["y"][0]} 41.0000 29.0000 #', 1)
            open(dh, 'w').write(txt)
            import dataclasses
            ay = dataclasses.replace(d.ayar, ustveri_sha16={'DataHoldings.txt': sha(dh)[:16]})
            with self.assertRaises(K.KosuDur) as e:
                K.kos(d.arg(os.path.join(tmp, 'c2')), ay, SESSIZ)
            self.assertIn('Marmara', str(e.exception))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    unittest.main(verbosity=2 if '-v' in sys.argv else 1, argv=[sys.argv[0]])
