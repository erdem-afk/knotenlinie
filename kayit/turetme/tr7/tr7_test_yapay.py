#!/usr/bin/env python3
"""TR-7 koşu kodunun sınaması: YALNIZ YAPAY VERİ. Gerçek dalga formu ya da StationXML indirilmez ve açılmaz; ağa
yalnız 127.0.0.1'deki yapay FDSN sunucusu için çıkılır.

Kullanım (depo kökünden):
  python3 -I -B kayit/turetme/tr7/tr7_test_yapay.py            (hepsi; uçtan uca prova birkaç dakika)
  python3 -I -B kayit/turetme/tr7/tr7_test_yapay.py -k Cekirdek (yalnız bir sınıf)
KD'nin tam koşusu (§7.1; saatler) burada değil: `tr7_kosu.py kd`. Burada KD'nin her işi küçük ölçekte bir kez koşulur.
"""
import contextlib
import csv
import datetime as dt
import hashlib
import http.server
import io
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.parse
from unittest import mock

import numpy as np

BURA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURA)
import tr7_cekirdek as K  # noqa: E402
import tr7_indir as I  # noqa: E402
import tr7_kosu as T  # noqa: E402

SCRATCH = os.environ.get('TR7_SINAMA_DIZIN') or tempfile.gettempdir()


json_oku = T.json_oku


def sessiz(*a, **k):
    pass


# ====================================================================== çekirdek
class Cekirdek(unittest.TestCase):
    def test_hilbert_scipy_ile_ayni(self):
        from scipy.signal import hilbert
        rng = np.random.default_rng(1)
        for n in (1000, 1001, 4096, 777):
            x = rng.standard_normal(n)
            self.assertTrue(np.allclose(K.analitik(x), hilbert(x), atol=1e-12))

    def test_rotasyon_obspy_ile_ayni(self):
        from obspy.signal.rotate import rotate_ne_rt
        rng = np.random.default_rng(2)
        n, e = rng.standard_normal(500), rng.standard_normal(500)
        for baz in (0.0, 37.5, 181.0, 300.2):
            r1, t1 = rotate_ne_rt(n, e, baz)
            r2, t2 = K.rotasyon_ne_rt(n, e, baz)
            self.assertTrue(np.allclose(r1, r2) and np.allclose(t1, t2))

    def test_egilim_obspy_ile_ayni(self):
        from obspy import Trace
        rng = np.random.default_rng(3)
        x = rng.standard_normal(3001) + np.linspace(0, 50, 3001) + 7
        tr = Trace(x.copy())
        tr.detrend('demean')
        tr.detrend('linear')
        self.assertTrue(np.allclose(tr.data, K.ortalama_egilim(x), atol=1e-9))

    def test_kutula_kisa_yol_ayni_ve_kismi_kutu(self):
        rng = np.random.default_rng(4)
        for t0, fs, n in ((1000.37, 20.0, 4000), (1000.0, 100.0, 7000), (55.05, 40.0, 1999)):
            g = np.abs(rng.standard_normal(n))
            k0, e = K.kutula(t0, fs, g)
            k1, e1 = K.Kutulayici(t0, fs, n)(g)
            self.assertEqual(k0, k1)
            self.assertTrue(np.array_equal(np.isnan(e), np.isnan(e1)))
            self.assertTrue(np.allclose(e[np.isfinite(e)], e1[np.isfinite(e1)]))
        k0, e = K.kutula(1000.5, 20.0, np.ones(2000))     # ilk kutu [1010,1011) tam; 1000.5+10=1010.5 → ilk kısmi
        self.assertTrue(np.isnan(e[0]))

    def test_saniye_maskesi(self):
        m = K.saniye_maskesi([(10.5, 12.0), (20.0, 20.2)], 0, 30)
        self.assertEqual(list(np.flatnonzero(m)), [10, 11, 20])

    def test_referans_betikle_esdeger(self):
        """Aynı C girdisinde koşu çekirdeği ile `tr7_onkayit_denetim2.py`: kümeler, parçalar, I, darbe/sızıntı/taban."""
        D = T.referans_modul(T.Ortam(), 'tr7_onkayit_denetim2')
        rng = np.random.default_rng(20261112 + 4040)
        say = dict(pencere=0, kume=0)
        for i in range(12):
            bas = float(rng.uniform(100, 1500))
            env = D.zarf_yarim(bas) if i % 3 else D.zarf_deprem(bas, 8)
            st = D.istasyonlar(rng, 4, env, [0.6, 1.0, 3.0, 30.0][i % 4])
            ks, ist = D.pencere(st)
            R, W = (0, D.R_S), (D.R_S, D.T)
            m = np.zeros(D.T, bool)
            bizim = [K.istasyon(cy, cd, R, W, m) for cy, cd in st]
            r = K.pencere_algila(bizim, m, W)
            self.assertEqual(len(ks), len(r['kumeler']))
            for a, b in zip(sorted(ks, key=lambda k: min(p[1] for p in k['parcalar'])), r['kumeler']):
                self.assertEqual(a['uyeler'], b['uyeler'])
                self.assertEqual(sorted((k, x + D.R_S, y + D.R_S) for k, x, y in a['parcalar']), sorted(b['parcalar']))
                self.assertEqual((a['I'][0] + D.R_S, a['I'][1] + D.R_S), b['I'])
                bay = D.ayikla(ist, a, m)
                self.assertEqual(bay['darbe_dogru'], b['bayrak']['darbe'])
                self.assertEqual(bay['sizinti_dogru'], b['bayrak']['sizinti'])
                self.assertEqual(bay['taban'], b['bayrak']['taban'])
                say['kume'] += 1
            say['pencere'] += 1
        self.assertGreater(say['kume'], 3)

    def test_taban_wson_denetim3_ile_esdeger(self):
        D3 = T.referans_modul(T.Ortam(), 'tr7_onkayit_denetim3')
        D = D3.D
        rng = np.random.default_rng(20261112 + 4041)
        n_k = 0
        for mson in (0, 120, 200):
            for _ in range(3):
                st = []
                for i in range(3):
                    nl = [(lambda yd: (yd[0] * D3.PROFIL, yd[1]))(D.gurultu(rng, 'gauss')) for _ in range(3)]
                    st.append((D.C(nl, [None] * 3, 0, 0), D.C(nl, [None] * 3, 0, 1)))
                mk = np.zeros(D.T, bool)
                if mson:
                    mk[D.T - mson:] = True
                ks, ist = D.pencere(st, mk)
                bizim = [K.istasyon(cy, cd, (0, D.R_S), (D.R_S, D.T), mk) for cy, cd in st]
                r = K.pencere_algila(bizim, mk, (D.R_S, D.T))
                self.assertEqual(len(ks), len(r['kumeler']))
                for a, b in zip(sorted(ks, key=lambda k: min(p[1] for p in k['parcalar'])), r['kumeler']):
                    self.assertEqual(D3.taban_wson(a, mk), b['bayrak']['taban'])
                    n_k += 1
        self.assertGreater(n_k, 3)

    def test_xmin_ve_pmin_tablolari(self):
        with open(os.path.join(BURA, 'tr7_onkayit_sayilar.json'), encoding='utf-8') as f:
            s1 = json.load(f)['X_min_tablo']
        with open(os.path.join(BURA, 'tr7_onkayit_sayilar3.json'), encoding='utf-8') as f:
            s3 = json.load(f)
        for tablo, alfa in ((s1['0.05'], 0.05), (s1['0.05/3'], 0.05 / 3), (s3['X_min_tablo_005_7'], 0.05 / 7),
                            (s3['X_min_tablo_005_3_yeniden'], 0.05 / 3)):
            for n, satir in tablo.items():
                n = int(n)
                self.assertEqual([K.x_min(n, f, 10 * n, alfa) for f in range(6)], satir, (n, alfa))
        for n, v in s3['p_min_tablo'].items():
            self.assertAlmostEqual(round(K.p_min(int(n)), 3), v)
        self.assertIsNone(K.p_min(4))

    def test_mda_basamak(self):
        A = K.A_BASAMAK
        P = [0.0] * 40 + [0.6, 0.4] + [0.95] * 59
        self.assertEqual(K.basamak(A, P, 0.5), A[42])
        self.assertEqual(K.basamak(A, P, 0.9), A[42])
        self.assertEqual(K.mda_ozet(P, 19)['A90'], 'belirsiz')
        self.assertEqual(K.mda_ozet([0.0] * 101, 30)['A90'], '> 100 µm/s')


# ====================================================================== KD'nin deterministik satırları
class KDDeterministik(unittest.TestCase):
    def test_D8(self):
        d8 = T.kd_D8()
        self.assertLessEqual(abs(d8['rms_oran'] - 1), 0.05)
        self.assertLessEqual(abs(d8['pgv_oran'] - 1), 0.05)

    def test_D9(self):
        d9 = T.kd_D9(T.Ortam())
        self.assertLessEqual(d9['en_buyuk_fark_s'], 1.0)
        self.assertTrue(all(d9['sinir_durdurdu']))

    def test_D11(self):
        r = T.kd_D11()
        self.assertTrue(r['hepsi'], [x for x in r['senaryolar'] if not x['dogru']])

    def test_D12c(self):
        d = T.kd_D12c(T.Ortam())
        self.assertTrue(d['elle_birebir']['dogru'])
        self.assertTrue(all(not v for k, v in d['elle_birebir'].items() if k != 'dogru'), d['elle_birebir'])
        self.assertEqual(d['rastgele_birebir'], [20, 20])
        self.assertTrue(d['gercek_tolerans'], d['gercek'])

    def test_K0_onsayim_yeniden_uretimi(self):
        D = T.dunya_yukle(T.Ortam())
        k = T.k0_tam(D, {}, onsayim=True)
        ref = json_oku(os.path.join(BURA, 'tr7_onkayit_sayilar.json'))['K0_on']
        for c in ('x1', 'x1/3'):
            for s in T.MARMARA_SEG:
                a, b = k[c][s], ref[c][s]
                self.assertEqual((a['n'], a['tau_n'], a['tau8'], a['tau5'], sorted(a['birimler'])),
                                 (b['n'], b['tau_n'], b['tau8'], b['tau5'], sorted(b['birimler'])), (c, s))
                self.assertEqual(a['bant'].replace('ı', 'i'), b['bant'])
        self.assertEqual((k['x1']['S5']['bagimsiz']['n'], k['x1']['S6']['bagimsiz']['n']), (2, 1))
        for s in T.MARMARA_SEG:                                        # ×3 alt sınır: önsayımın altında ya da eşit
            self.assertLessEqual(k['x3'][s]['n'], ref['x3'][s]['n'])

    def test_girdi_sha_gercek(self):
        g = T.girdi_denetimi(T.Ortam())
        self.assertEqual(g['TR-7_tetiklenmis-tremor_ONKAYIT.md'], T.ONKAYIT_SHA)
        for ad, s in T.REFERANS.items():
            self.assertEqual(T.sha256_dosya(os.path.join(BURA, ad)), s, ad)


# ====================================================================== 2026 sınırı ve istemci
class Sinir(unittest.TestCase):
    def test_2026_istegi_imkansiz(self):
        with mock.patch('urllib.request.urlopen', side_effect=AssertionError('ağa çıkıldı')):
            for f in (lambda: I.dataselect_url('koeri', 'KO', 'X', '', ['HHZ'], '2025-12-31T23:00:00', '2026-01-01T00:00:00'),
                      lambda: I.station_url('koeri', 'KO', 'X', '', ['HH?'], '2025-01-01', '2026-01-02'),
                      lambda: I.event_url('comcat', '2025-12-31', '2026-01-01T00:00:00', 0, 0, 180, 6),
                      lambda: I.dataselect_url('koeri', 'KO', 'X', '', ['HHZ'], '2026-01-01', '2026-01-02')):
                with self.assertRaises(I.SinirIhlali):
                    f()
            I.event_url('comcat', '2025-12-31', '2025-12-31T23:59:59', 0, 0, 180, 6)
        with self.assertRaises(K.CekirdekHata):
            K.pencere_hesapla('2025-12-31T23:00:00', 10000.0)
        K.pencere_hesapla('2025-12-31T21:00:00', 6000.0)

    def test_depo_disi(self):
        self.assertTrue(I.depo_disi('/mnt/project-files/turetme/tr7-zarf', T.DEPO))
        self.assertFalse(I.depo_disi(os.path.join(T.DEPO, 'x'), T.DEPO))


class _Sunucu(http.server.ThreadingHTTPServer):
    daemon_threads = True


@contextlib.contextmanager
def sunucu(isleyici):
    s = _Sunucu(('127.0.0.1', 0), isleyici)
    t = threading.Thread(target=s.serve_forever, daemon=True)
    t.start()
    try:
        yield s
    finally:
        s.shutdown()
        s.server_close()


class Istemci(unittest.TestCase):
    def test_davranis(self):
        kayit = dict(ua=set(), say={}, eszaman=0, en_cok=0)
        kilit = threading.Lock()

        class H(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_GET(self):
                with kilit:
                    kayit['ua'].add(self.headers.get('User-Agent'))
                    kayit['say'][self.path] = kayit['say'].get(self.path, 0) + 1
                    n = kayit['say'][self.path]
                    kayit['eszaman'] += 1
                    kayit['en_cok'] = max(kayit['en_cok'], kayit['eszaman'])
                try:
                    if self.path.startswith('/yavas'):
                        time.sleep(0.2)
                    if self.path == '/429' and n == 1:
                        self.send_response(429)
                        self.send_header('Retry-After', '0')
                        self.end_headers()
                        return
                    kod = {'/403': 403, '/204': 204, '/500': 500, '/404': 404}.get(self.path, 200)
                    self.send_response(kod)
                    self.end_headers()
                    if kod == 200:
                        self.wfile.write(b'veri' * 100)
                finally:
                    with kilit:
                        kayit['eszaman'] -= 1
        uykular = []
        with sunucu(H) as s:
            taban = f'http://127.0.0.1:{s.server_address[1]}'
            cl = I.Istemci(aralik=0.01, bekle_429=0.0, uyku=lambda x: uykular.append(x))
            d = tempfile.mkdtemp(dir=SCRATCH)
            r = cl.iste('a', taban + '/429', hedef=os.path.join(d, 'x'))
            self.assertEqual((r['durum'], r['deneme'], r['bayt']), ('tamam', 2, 400))
            self.assertEqual(r['sha256'], hashlib.sha256(b'veri' * 100).hexdigest())
            self.assertEqual(cl.iste('a', taban + '/403')['durum'], 'kisitli')
            self.assertEqual(kayit['say']['/403'], 1)                    # 401/403 yeniden denenmez
            self.assertEqual(cl.iste('a', taban + '/204')['durum'], 'yok')
            self.assertEqual(cl.iste('a', taban + '/404')['durum'], 'yok')
            self.assertEqual(cl.iste('a', taban + '/500')['durum'], 'servis_hatasi')
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(6) as ex:
                list(ex.map(lambda i: cl.iste('ayni', taban + f'/yavas{i}'), range(8)))
            self.assertLessEqual(kayit['en_cok'], I.AKIS)                  # servis başına ≤ 2 akış
            shutil.rmtree(d)
        self.assertEqual(kayit['ua'], {I.UA})
        self.assertNotIn('knoten', I.UA.lower())
        self.assertIn(0.0, uykular)                                        # Retry-After: 0


# ====================================================================== mekanizma: git, önkoşul, hata payları
class Mekanizma(unittest.TestCase):
    def test_git_dogrulama(self):
        kok = tempfile.mkdtemp(dir=SCRATCH)
        try:
            uzak = os.path.join(kok, 'uzak.git')
            depo = os.path.join(kok, 'depo')
            env = dict(os.environ, GIT_AUTHOR_NAME='s', GIT_AUTHOR_EMAIL='s@x', GIT_COMMITTER_NAME='s',
                       GIT_COMMITTER_EMAIL='s@x')

            def g(*a, cwd=None):
                subprocess.run(['git'] + list(a), cwd=cwd or depo, check=True, capture_output=True, env=env)
            subprocess.run(['git', 'init', '-q', '--bare', uzak], check=True, capture_output=True)
            subprocess.run(['git', 'init', '-q', '-b', 'ana', depo], check=True, capture_output=True)
            tr7 = os.path.join(depo, 'tr7')
            os.makedirs(tr7)
            o = T.Ortam(tr7=tr7, depo=depo, zarf=os.path.join(kok, 'zarf'), log=sessiz)
            d = T.durum_oku(o)
            d['asamalar']['manifest'] = dict(durum='başladı')
            T.json_yaz(o.yol(T.DURUM_AD), d)
            with self.assertRaises(T.GitDogrulanamadi):                     # izlenmiyor
                T.git_dogrula(o, 'manifest')
            g('add', '.')
            g('commit', '-q', '-m', 'x')
            with self.assertRaises(T.GitDogrulanamadi):                     # uzak izleme dalı yok
                T.git_dogrula(o, 'manifest')
            g('remote', 'add', 'origin', uzak)
            g('push', '-q', '-u', 'origin', 'ana')
            T.git_dogrula(o, 'manifest')                                    # geçer
            with open(o.yol('baska'), 'w') as f:
                f.write('1')
            g('add', '.')
            g('commit', '-q', '-m', 'y')
            with self.assertRaises(T.GitDogrulanamadi):                     # HEAD push edilmedi
                T.git_dogrula(o, 'manifest')
            g('push', '-q')
            T.git_dogrula(o, 'manifest')
            d['asamalar']['manifest']['durum'] = 'tamamlandı'
            T.json_yaz(o.yol(T.DURUM_AD), d)
            with self.assertRaises(T.GitDogrulanamadi):                     # çalışma kopyası HEAD'den farklı
                T.git_dogrula(o, 'manifest')
            g('add', '.')
            g('commit', '-q', '-m', 'z')
            g('push', '-q')
            with self.assertRaises(T.GitDogrulanamadi):                     # HEAD aşamayı başlamış göstermiyor
                T.git_dogrula(o, 'manifest')
        finally:
            shutil.rmtree(kok)

    def test_onkosul(self):
        o = T.Ortam(log=sessiz)
        d = dict(asamalar={}, durmalar=[])
        self.assertEqual(T.onkosul(o, 'manifest', d), 'yeni')
        with self.assertRaises(T.KosuDur):
            T.onkosul(o, 'K1-indirme', d)                                   # manifest tamamlanmadı
        d['asamalar'] = {'manifest': dict(durum='tamamlandı'), 'K1-indirme': dict(durum='tamamlandı'),
                         'K1-negatif': dict(durum='durdu')}
        with self.assertRaises(T.KosuDur):
            T.onkosul(o, 'K1-negatif', d)                                   # algılama aşamasına girildi
        with self.assertRaises(T.KosuDur):
            T.onkosul(o, 'K1-negatif', d, surdur=True)                      # durma nedeni yok
        d['durmalar'].append(dict(asama='K1-negatif', neden='x'))
        self.assertEqual(T.onkosul(o, 'K1-negatif', d, surdur=True), 'surdur')
        with self.assertRaises(T.KosuDur):
            T.onkosul(o, 'manifest', d)                                     # tek koşu
        d['asamalar'].update({'K1-negatif': dict(durum='tamamlandı'),
                              'K1-algılama': dict(durum='tamamlandı', k1_dal='d')})
        with self.assertRaises(T.KosuDur):
            T.onkosul(o, 'Marmara-indirme', d)                              # K1 (d): Marmara indirilmez
        self.assertEqual(T.onkosul(o, 'hüküm', d), 'yeni')                  # K1 kaldı: doğrudan hüküm
        d['uygulama_hatasi_yolu'] = None
        self.assertEqual(T.onkosul(o, 'K1-algılama', d, uygulama_hatasi=True), 'uygulama_hatasi')
        d['uygulama_hatasi_yolu'] = dict(zaman='x')
        with self.assertRaises(T.KosuDur):
            T.onkosul(o, 'K1-algılama', d, uygulama_hatasi=True)            # yalnız bir kez

    def test_hata_paylari(self):
        kok = tempfile.mkdtemp(dir=SCRATCH)
        try:
            o = T.Ortam(tr7=kok, log=sessiz, uyku=lambda x: None)
            s = T.AsamaSayac(os.path.join(kok, 'g.jsonl'), 200)
            for i in range(200):
                s.ekle(dict(anahtar=f'p|{i}', pencere='p', durum='tamam', http=200))
            T.hata_denetimi(o, s, 'x')
            s.ekle(dict(anahtar='p|0', pencere='p', durum='bicim_hatasi', http=200))
            s.ekle(dict(anahtar='p|1', pencere='p', durum='bicim_hatasi', http=200))
            T.hata_denetimi(o, s, 'x')                                       # 2/200 = %1: geçer (aşmıyor)
            s.ekle(dict(anahtar='p|2', pencere='p', durum='bicim_hatasi', http=200))
            with self.assertRaises(T.KosuDur):
                T.hata_denetimi(o, s, 'x')
            s2 = T.AsamaSayac(os.path.join(kok, 'g2.jsonl'), 100)
            for i in range(100):
                s2.ekle(dict(anahtar=f'q|{i}', pencere='q', durum='servis_hatasi' if i < 11 else 'tamam',
                             http=503 if i < 11 else 200))
            cagri = []

            def yeniden():
                cagri.append(1)
                for i in range(11):
                    s2.ekle(dict(anahtar=f'q|{i}', pencere='q', durum='tamam', http=200))
            sp = T.hata_denetimi(o, s2, 'y', yeniden=yeniden)
            self.assertEqual((len(cagri), sp), (1, 0.0))
            T.hata_denetimi(o, s2, 'y', yeniden=yeniden)
            self.assertEqual(len(cagri), 1)                                  # tek tur
            s3 = T.AsamaSayac(os.path.join(kok, 'g2.jsonl'), 100)            # günlükten yeniden kurulur
            self.assertTrue(s3.yeniden_tur)
        finally:
            shutil.rmtree(kok)


# ====================================================================== uçtan uca: yapay dünya ve yapay FDSN sunucusu
FS = 20.0
S_DUY = 6.0e8                       # sayım / (m/s)
GUR = 1.0e-7                        # m/s, beyaz
TREMOR_RMS = 6.0e-7                 # m/s, 2–8 Hz
TOHOKU_T0 = '2011-03-11T05:46:24.120000'
IKINCI = 'usb000g7x7'


def _w(t0, d):
    w = K.pencere_hesapla(t0, d)
    return w


def mini_dunya(kok):
    """Küçük ama biçimce gerçek dondurulmuş girdiler (yapay istasyonlar; gerçek iki olayın zamanı ve yeri)."""
    tr7 = os.path.join(kok, 'tr7')
    os.makedirs(tr7)
    olaylar = [dict(id=T.TOHOKU, t0=TOHOKU_T0, M=9.1, la=38.297, lo=142.373, dz=29.0, tau=23.25),
               dict(id=IKINCI, t0='2013-04-16T10:44:20.000000', M=7.7, la=28.033, lo=61.996, dz=80.0, tau=4.68)]
    mist = [('KO', f'M0{i}', 40.80 + 0.05 * i, 28.2 + 0.25 * i) for i in range(1, 5)]
    sat = []
    for e in olaylar:
        rs = []
        for ag, ist, la, lo in mist:
            d = K.hav(e['la'], e['lo'], la, lo)
            w = _w(e['t0'], d)
            rs.append(dict(birim=e['id'], tetikleyici=e['id'], t0=e['t0'], M=e['M'], ev_enlem=e['la'],
                           ev_boylam=e['lo'], segment='S2', tau_kaba_kpa=e['tau'], kahramanmaras=0, ag=ag, istasyon=ist,
                           ist_enlem=la, ist_boylam=lo, yoklama_kanal='BHZ', uzaklik_km=round(d, 1),
                           R_bas=w['R'][0].isoformat(), R_son=w['R'][1].isoformat(),
                           W_bas=w['W'][0].isoformat(timespec='seconds'), W_son=w['W'][1].isoformat(timespec='seconds'),
                           iz_km=round(K.nokta_cizgi(la, lo, K.SEGMENT['S2']), 2)))
        for i, r in enumerate(sorted(rs, key=lambda r: (r['iz_km'], r['ag'], r['istasyon'])), 1):
            r['iz_sira'], r['ilk12'] = i, int(i <= 12)
        sat += rs
    _csv(os.path.join(tr7, 'tr7_dondurulan_liste.csv'), sat)
    pist = [('NC', f'P0{i}', 35.95 - 0.04 * i, -120.45 + 0.04 * i) for i in range(1, 5)] + [('BK', 'PKD', 35.945, -120.541)]
    th = olaylar[0]
    ps, pv = [], []
    for j, (ag, ist, la, lo) in enumerate(pist, 1):
        d = K.hav(th['la'], th['lo'], la, lo)
        w = _w(th['t0'], d)
        ps.append(dict(ag=ag, istasyon=ist, enlem=la, boylam=lo, kanallar='BHZ', fay_km=1.0, uzaklik_km=round(d, 1),
                       W_bas=w['W'][0].isoformat(timespec='seconds'), W_son=w['W'][1].isoformat(timespec='seconds'),
                       var_R=1, var_W=0 if ist == 'PKD' else 1, iz_sira=j, ilk12=int(j <= 12)))
        pv.append(dict(ag=ag, istasyon=ist, konum='', kanal='BHZ', ornek='R', bas='', son='', ncedc_http=200,
                       servis='ncedc', http=200, bayt=1, sure_s=0.1, durum='var'))
    _csv(os.path.join(tr7, 'tr7_parkfield_liste.csv'), ps)
    _csv(os.path.join(tr7, 'tr7_parkfield_varlik.csv'), pv)
    neg = []
    for e in olaylar:
        for sira, d in ((1, -7), (2, 7)):
            neg.append(dict(birim=e['id'], bolge='Marmara', sira=sira, d_gun=d, T0_kaydirilmis='', gun_turu='hafta_ici',
                            utc_farki_saat=2.0, aday_kumesi='±30'))
    for sira, d in enumerate((-7, -14, 7, 14, 21), 1):
        neg.append(dict(birim='PARKFIELD_TOHOKU', bolge='Parkfield', sira=sira, d_gun=d, T0_kaydirilmis='',
                        gun_turu='hafta_ici', utc_farki_saat=-8.0, aday_kumesi='±30'))
    _csv(os.path.join(tr7, 'tr7_negatif_pencere.csv'), neg)
    t0 = K.epoch(TOHOKU_T0)
    e1 = []
    for faz, tt in (('P', 3000.0), ('S', 3300.0)):
        e1.append(dict(birim=T.TOHOKU, tetikleyici=T.TOHOKU, segment='S2', olay='yapay_m62', olay_t='', M=6.2,
                       derinlik_km=10.0, delta_derece=80.0, faz=faz, seyahat_s=0,
                       varis=K.epoch_zaman(t0 + tt).isoformat(), W_icinde=1))
    _csv(os.path.join(tr7, 'tr7_e1_maske.csv'), e1)
    _csv(os.path.join(tr7, 'tr7_istasyon.csv'), [dict(ag=ag, istasyon=ist, enlem=la, boylam=lo, kanallar='BHZ',
                                                      ilk_epok='', son_epok='', kaynak='koeri', yakin_segmentler='S2',
                                                      en_yakin_fay_km=1) for ag, ist, la, lo in mist])
    _csv(os.path.join(tr7, 'tr7_tetikleyici.csv'), [dict(id=e['id'], zaman=e['t0'], M=e['M'], derinlik_km=e['dz'])
                                                    for e in olaylar])
    dond = {f: T.sha256_dosya(os.path.join(tr7, f)) for f in (
        'tr7_dondurulan_liste.csv', 'tr7_parkfield_liste.csv', 'tr7_parkfield_varlik.csv', 'tr7_negatif_pencere.csv',
        'tr7_e1_maske.csv', 'tr7_istasyon.csv', 'tr7_tetikleyici.csv')}
    with open(os.path.join(tr7, 'tr7_kd.json'), 'w', encoding='utf-8') as f:     # KD burada sahte (mekanizma provası)
        json.dump(dict(gecti=True, olcek=1.0, kod_sha256=T.kod_sha(), satirlar=[]), f)
    return tr7, dond, mist, pist


def _csv(yol, rows):
    with open(yol, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def _envanter(ag, ist, la, lo, kanallar):
    from obspy import UTCDateTime
    from obspy.core.inventory import Inventory, Network, Station, Channel, Response
    p = 2 * np.pi / 120.0
    ch = []
    for c in kanallar:
        resp = Response.from_paz(zeros=[0j, 0j], poles=[complex(-p * 0.707, p * 0.707), complex(-p * 0.707, -p * 0.707)],
                                 stage_gain=S_DUY, stage_gain_frequency=1.0, input_units='M/S', output_units='COUNTS',
                                 normalization_frequency=1.0)
        resp.recalculate_overall_sensitivity(1.0)
        az, dip = {'Z': (0.0, -90.0), 'N': (0.0, 0.0), 'E': (90.0, 0.0)}[c[-1]]
        ch.append(Channel(c, '', la, lo, 0.0, 0.0, azimuth=az, dip=dip, sample_rate=FS, response=resp,
                          start_date=UTCDateTime(2000, 1, 1)))
    inv = Inventory(networks=[Network(ag, stations=[Station(ist, la, lo, 0.0, channels=ch,
                                                            start_date=UTCDateTime(2000, 1, 1))])], source='yapay')
    b = io.BytesIO()
    inv.write(b, format='STATIONXML')
    return b.getvalue()


def _tremor(rng, n, i_bas):
    from scipy.signal import butter, sosfiltfilt
    s = np.zeros(n)
    m = int(300 * FS)
    if i_bas < 0 or i_bas + m > n:
        return s
    tt = np.arange(m) / FS
    env = np.maximum(0, np.sin(2 * np.pi * tt / 20.0)) * np.minimum(1, np.minimum(tt, 300 - tt) / 10)
    g = rng.standard_normal(m) * env
    sos = butter(4, [2.0, 8.0], btype='band', fs=FS, output='sos')
    g = sosfiltfilt(sos, g)
    g *= TREMOR_RMS / np.sqrt(np.mean(g ** 2))
    s[i_bas:i_bas + m] = g
    return s


class YapayFDSN(http.server.BaseHTTPRequestHandler):
    """dataselect / station / event. Sunucu özellikleri: istasyonlar {(ag, ist): (la, lo, kanallar)}, tremor
    [(ag, ist, epoch başlangıç)], kisitli {(ag, ist)}, bozuk {(ag, ist)}, bosluk {(ag, ist, gün)}, yerel_olay."""

    def log_message(self, *a):
        pass

    def do_GET(self):
        sv = self.server
        u = urllib.parse.urlparse(self.path)
        q = dict(urllib.parse.parse_qsl(u.query))
        with sv.kilit:
            sv.istekler.append((u.path, q, self.headers.get('User-Agent')))
        try:
            if '/dataselect/' in u.path:
                return self._veri(q)
            if '/station/' in u.path:
                key = (q['net'], q['sta'])
                if key not in sv.istasyonlar:
                    return self._kod(204)
                la, lo, kan = sv.istasyonlar[key]
                return self._govde(_envanter(key[0], key[1], la, lo, kan), 'application/xml')
            if u.path.startswith('/comcat'):
                return self._katalog(q, 'comcat')
            if u.path.startswith('/emsc'):
                return self._katalog(q, 'emsc')
            return self._kod(404)
        except Exception as e:                                    # noqa: BLE001
            sv.hatalar.append(repr(e))
            return self._kod(500)

    def _kod(self, k):
        self.send_response(k)
        self.end_headers()

    def _govde(self, b, ct):
        self.send_response(200)
        self.send_header('Content-Type', ct)
        self.send_header('Content-Length', str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def _katalog(self, q, kt):
        sv = self.server
        bas = K.epoch(q.get('starttime') or q.get('start'))
        bit = K.epoch(q.get('endtime') or q.get('end'))
        if bit >= K.epoch('2026-01-01T00:00:00'):
            sv.hatalar.append('2026 katalog isteği')
        mm = float(q.get('minmagnitude') or q.get('minmag'))
        ol = []
        if mm < 6.0:
            for la, lo, M, dt_ in sv.yerel_olay:
                t = bas + dt_
                if t < bit:
                    ol.append((t, la, lo, M))
        if kt == 'comcat':
            s = 'time,latitude,longitude,depth,mag,id\n' + ''.join(
                f'{K.epoch_zaman(t).isoformat()}Z,{la},{lo},10.0,{M},y{i}\n' for i, (t, la, lo, M) in enumerate(ol))
        else:
            s = '#EventID|Time|Latitude|Longitude|Depth/Km|Author|Catalog|Contributor|ContributorID|MagType|Magnitude|' \
                'MagAuthor|EventLocationName\n' + ''.join(
                    f'e{i}|{K.epoch_zaman(t).isoformat()}|{la}|{lo}|10.0|A|C|C|1|ml|{M}|A|yer\n'
                    for i, (t, la, lo, M) in enumerate(ol))
        if not ol and kt == 'emsc':
            return self._kod(204)
        return self._govde(s.encode(), 'text/plain')

    def _veri(self, q):
        from obspy import Stream, Trace, UTCDateTime
        sv = self.server
        key = (q['net'], q['sta'])
        if key in sv.kisitli:
            return self._kod(403)
        bas, bit = K.epoch(q['start']), K.epoch(q['end'])
        if bit >= K.epoch('2026-01-01T00:00:00'):
            sv.hatalar.append('2026 veri isteği')
        if key in sv.bozuk:
            return self._govde(b'bu miniSEED degil' * 300, 'application/vnd.fdsn.mseed')
        n = int(round((bit - bas) * FS)) + 1
        st = Stream()
        tohum = int(hashlib.sha256(f'{key}{int(bas)}'.encode()).hexdigest()[:12], 16)
        for c in q['cha'].split(','):
            if c not in sv.istasyonlar.get(key, (0, 0, ()))[2]:
                continue
            rng = np.random.default_rng(tohum + 'ZNE'.index(c[-1]))
            v = rng.standard_normal(n) * GUR
            for ag, ist, t_tr in sv.tremor:
                if (ag, ist) == key:
                    v += _tremor(np.random.default_rng(tohum + 7 + 'ZNE'.index(c[-1])), n, int(round((t_tr - bas) * FS)))
            x = np.round(v * S_DUY).astype(np.int32)
            tr = Trace(x, header=dict(network=key[0], station=key[1], location='', channel=c, sampling_rate=FS,
                                      starttime=UTCDateTime(bas)))
            gun = int(bas // 86400)
            if (key[0], key[1], gun) in sv.bosluk:
                a = tr.slice(UTCDateTime(bas), UTCDateTime(bas + (bit - bas) * 0.4))
                b = tr.slice(UTCDateTime(bas + (bit - bas) * 0.7), UTCDateTime(bit))
                st += a.copy()
                st += b.copy()
            else:
                st += tr
        if not len(st):
            return self._kod(204)
        b = io.BytesIO()
        st.write(b, format='MSEED', encoding='STEIM2', reclen=4096)
        return self._govde(b.getvalue(), 'application/vnd.fdsn.mseed')


@contextlib.contextmanager
def fdsn(mist, pist, kisitli=(), bozuk=(), bosluk=()):
    s = _Sunucu(('127.0.0.1', 0), YapayFDSN)
    s.kilit = threading.Lock()
    s.istekler, s.hatalar = [], []
    s.istasyonlar = {}
    for ag, ist, la, lo in mist:
        s.istasyonlar[(ag, ist)] = (la, lo, ('BHZ',) if ist == 'M03' else ('BHZ', 'BHN', 'BHE'))
    for ag, ist, la, lo in pist:
        s.istasyonlar[(ag, ist)] = (la, lo, ('BHZ', 'BHN', 'BHE'))
    t0 = K.epoch(TOHOKU_T0)
    k1a = K.epoch('2011-03-11T06:21:00')
    s.tremor = [(ag, ist, k1a) for ag, ist, _, _ in pist] + [(ag, ist, t0 + 2400.0) for ag, ist, _, _ in mist]
    s.kisitli, s.bozuk, s.bosluk = set(kisitli), set(bozuk), set(bosluk)
    s.yerel_olay = [(40.85, 28.6, 2.6, 5400.0)]
    t = threading.Thread(target=s.serve_forever, daemon=True)
    t.start()
    p = s.server_address[1]
    try:
        yield s, {k: f'http://127.0.0.1:{p}/{k}/fdsnws' for k in I.SERVIS}, \
            {'comcat': f'http://127.0.0.1:{p}/comcat/query', 'emsc': f'http://127.0.0.1:{p}/emsc/query'}
    finally:
        s.shutdown()
        s.server_close()


def ortam_kur(kok, servis, katalog, dond, tr7):
    return T.Ortam(tr7=tr7, depo=os.path.join(kok, 'depo_yok'), zarf=os.path.join(kok, 'zarf'), servis=servis,
                   katalog=katalog, uyku=lambda x: None, aralik=0.0, bekle_429=0.0, yeniden_bekle=0.0,
                   dondurulmus=dond, git_dogrula=False, log=sessiz)


def asama(o, ad, **kw):
    T.baslat(o, ad, **kw)
    return T.kos(o, ad)


class UctanUca(unittest.TestCase):
    """Bütün aşamalar yapay dünyada: indir–zarfla–sil, manifest, K1, K0-tam, K2, MDA, algılama, hüküm."""

    @classmethod
    def setUpClass(cls):
        cls.kok = tempfile.mkdtemp(prefix='tr7_uu_', dir=SCRATCH)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.kok, ignore_errors=True)

    def test_1_tam_koşu(self):
        kok = os.path.join(self.kok, 'A')
        os.makedirs(kok)
        tr7, dond, mist, pist = mini_dunya(kok)
        g_bas = int(K.epoch('2013-04-16T00:00:00') // 86400)
        with fdsn(mist, pist, kisitli={('NC', 'P04')}, bosluk={('KO', 'M04', g_bas)}) as (sv, servis, katalog):
            o = ortam_kur(kok, servis, katalog, dond, tr7)
            with self.assertRaises(T.KosuDur):
                T.kos(o, 'manifest')                                       # başlatılmadan koşulmaz
            sonuc = {}
            for ad in T.ASAMALAR:
                sonuc[ad] = asama(o, ad)
            self.assertEqual(sv.hatalar, [])
            self.assertTrue(all(ua == I.UA for _, _, ua in sv.istekler))
        d = T.durum_oku(o)
        self.assertTrue(all(d['asamalar'][a]['durum'] == 'tamamlandı' for a in T.ASAMALAR))
        k1 = json_oku(o.yol('tr7_k1.json'))
        self.assertIn(k1['dal'], ('b', "b'"), k1.get('algilama_satiri'))
        self.assertEqual(k1['N_PK'], 5)
        self.assertEqual(k1['mda_deneme'], 3 * (5 - k1['f_PK']))
        self.assertIsNotNone(k1['A_PK'])
        k0 = json_oku(o.yol('tr7_k0_tam.json'))
        self.assertEqual(k0['x1']['S2']['n'], 2)
        self.assertEqual(k0['x1']['S2']['bant'], 'veri yok')
        alg = T._algilama_satirlari(o, 'Marmara-algılama')
        self.assertTrue(alg[(f'tet|{T.TOHOKU}', 'S2')]['algilama'])
        self.assertGreater(alg[(f'tet|{T.TOHOKU}', 'S2')]['paylar']['W_e1'], 0)  # E1 maskesi uygulandı
        self.assertGreater(alg[(f'tet|{T.TOHOKU}', 'S2')]['paylar']['R_yerel'], 0)  # yerel katalog maskesi
        self.assertFalse(alg[(f'tet|{IKINCI}', 'S2')]['algilama'])
        self.assertEqual(alg[(f'tet|{IKINCI}', 'S2')]['n_gecen'], 3)          # M04 örtüden düştü
        zk = T.zarf_kayitlari(o)
        self.assertEqual(zk[f'tet|{IKINCI}'][('KO', 'M04')]['dusme'], 'ortu')
        self.assertEqual(zk['pk|tohoku'][('NC', 'P04')]['dusme'], 'kisitli')
        self.assertEqual(zk[f'tet|{T.TOHOKU}'][('KO', 'M03')]['bilesen'], 'Z')
        self.assertEqual(zk[f'tet|{T.TOHOKU}'][('KO', 'M01')]['bilesen'], 'ZNE')
        for r in jsonl_hepsi(o.yol('tr7_zarf_sha256.jsonl')):                  # zarf sha256 listesi doğrulanır
            if r.get('sha256'):
                self.assertEqual(T.sha256_dosya(os.path.join(o.zarf, r['dosya'])), r['sha256'])
        self.assertFalse(os.path.exists(o.zyol('ham', 'K1-negatif')))         # ham silindi
        self.assertFalse(os.path.exists(o.zyol('ham', 'Marmara-negatif')))
        hamlar = [f for _, _, fs in os.walk(o.zarf) for f in fs if f.endswith('.mseed')]
        self.assertEqual(hamlar, [])
        mda = T.csv_oku(o.yol('tr7_mda.csv'))
        self.assertEqual(len(mda) % 101, 0)
        with self.assertRaises(I.BicimHata):                                   # bozulmuş zarf sha256 ile yakalanır
            r = next(r for r in jsonl_hepsi(o.yol('tr7_zarf_sha256.jsonl')) if r.get('sha256'))
            I.zarf_oku(os.path.join(o.zarf, r['dosya']), '0' * 64)
        so = json_oku(o.yol('tr7_sonuc.json'))
        self.assertEqual(so['segment']['S2']['hukum']['cumle'], 'S2: veri yok.')
        md = T.metin_oku(o.yol('tr7_sonuc.md'))
        self.assertIn('Kaba τ ×1/3 alınırsa', md)
        with self.assertRaises(FileExistsError):                               # tek koşu: 'x' kipi
            T.json_yaz_x(o.yol('tr7_sonuc.json'), {})
        with self.assertRaises(T.KosuDur):
            T.baslat(o, 'hüküm')                                               # tamamlanmış aşama yeniden koşulmaz
        type(self).A = o

    def test_2_sha_uyusmazligi_durdurur(self):
        kok = os.path.join(self.kok, 'B')
        os.makedirs(kok)
        tr7, dond, mist, pist = mini_dunya(kok)
        with open(os.path.join(tr7, 'tr7_negatif_pencere.csv'), 'a') as f:
            f.write('\n')
        o = ortam_kur(kok, None, None, dond, tr7)
        with self.assertRaises(T.KosuDur):
            T.baslat(o, 'manifest')
        self.assertFalse(os.path.exists(o.yol(T.DURUM_AD)))

    def test_3_bicim_hatasi_durdurur(self):
        kok = os.path.join(self.kok, 'C')
        os.makedirs(kok)
        tr7, dond, mist, pist = mini_dunya(kok)
        with fdsn(mist, pist, bozuk={('NC', 'P01')}) as (sv, servis, katalog):
            o = ortam_kur(kok, servis, katalog, dond, tr7)
            asama(o, 'manifest')
            T.baslat(o, 'K1-indirme')
            with self.assertRaises(T.KosuDur) as cm:
                T.kos(o, 'K1-indirme')
            self.assertIn('biçim', str(cm.exception))
        d = T.durum_oku(o)
        self.assertEqual(d['asamalar']['K1-indirme']['durum'], 'durdu')
        self.assertFalse(os.path.exists(o.yol('tr7_algilama_K1-negatif.jsonl')))

    def test_4_yeniden_baslatma_ayni_sonuc(self):
        """K1-negatif MDA'nın ikinci penceresinde durdurulup sürdürülen koşu, kesintisizle aynı satırları yazar."""
        A = getattr(type(self), 'A', None)
        if A is None:
            self.skipTest('uçtan uca koşu yok')
        kok = os.path.join(self.kok, 'D')
        os.makedirs(kok)
        tr7, dond, mist, pist = mini_dunya(kok)
        g_bas = int(K.epoch('2013-04-16T00:00:00') // 86400)
        with fdsn(mist, pist, kisitli={('NC', 'P04')}, bosluk={('KO', 'M04', g_bas)}) as (sv, servis, katalog):
            o = ortam_kur(kok, servis, katalog, dond, tr7)
            for ad in ('manifest', 'K1-indirme'):
                asama(o, ad)
            T.baslat(o, 'K1-negatif')
            asil = K.mda_deneme
            sayac = [0]

            def kesik(*a, **k):
                sayac[0] += 1
                if sayac[0] == 2:
                    raise T.KosuDur('yapay kesinti')
                return asil(*a, **k)
            with mock.patch.object(K, 'mda_deneme', kesik):
                with self.assertRaises(T.KosuDur):
                    T.kos(o, 'K1-negatif')
            with self.assertRaises(T.KosuDur):
                T.baslat(o, 'K1-negatif', surdur=True)                       # durma nedeni kayda geçmeden olmaz
            T.durdu(o, 'K1-negatif', 'yapay kesinti (sınama)')
            T.baslat(o, 'K1-negatif', surdur=True)
            T.kos(o, 'K1-negatif')
        a = [r for r in jsonl_hepsi(A.yol('tr7_mda.jsonl')) if r['asama'] == 'K1-negatif']
        b = [r for r in jsonl_hepsi(o.yol('tr7_mda.jsonl')) if r['asama'] == 'K1-negatif']
        self.assertEqual([(r['pencere'], r['denemeler'], r['rng_sonra']) for r in a],
                         [(r['pencere'], r['denemeler'], r['rng_sonra']) for r in b])
        aa = T._algilama_satirlari(A, 'K1-negatif')
        bb = T._algilama_satirlari(o, 'K1-negatif')
        self.assertEqual({k: v['algilama'] for k, v in aa.items()}, {k: v['algilama'] for k, v in bb.items()})
        self.assertEqual(len(jsonl_hepsi(o.yol('tr7_algilama_K1-negatif.jsonl'))), 5)   # yeniden hesaplanmadı


def jsonl_hepsi(y):
    return T.jsonl_oku(y)


# ====================================================================== KD işleri, küçük ölçekte (her iş bir kez)
@unittest.skipUnless(os.environ.get('TR7_KD_KUCUK'), 'uzun (≈ 30 dk): TR7_KD_KUCUK=1 ile koşulur')
class KDKucuk(unittest.TestCase):
    def test_her_is_kosar(self):
        """Her KD işi 1 pencereyle koşar ve beklenen alanları döndürür (bantlar tam KD'de denetlenir)."""
        goruldu = set()
        for i, (ad, ek, nt, n) in enumerate(T.KD_ISLER):
            if (ad, json.dumps(ek)) in goruldu or ad in ('D4', 'D5', 'D5b'):
                continue
            goruldu.add((ad, json.dumps(ek)))
            r = T.kd_is(ad, ek, T.kd_tohum(i, 0), 1)
            self.assertIn('sonuc', r)
        r = T.kd_is('D5', ('sabit', 1.0, 20), 1, 2)
        self.assertIn('p_le_001_orani', r['sonuc'])



# ====================================================================== kod incelemesi (bağımsız): mutasyonlar
@contextlib.contextmanager
def mutant(mod, ad, eski, yeni):
    """Fonksiyonun kaynağında tek bir yeri değiştirip modülde geçici olarak yeniden tanımlar (mutasyon sınaması)."""
    import inspect
    import textwrap
    kay = textwrap.dedent(inspect.getsource(getattr(mod, ad)))
    assert kay.count(eski) == 1, (ad, eski)
    eski_f = mod.__dict__[ad]
    exec(compile(kay.replace(eski, yeni), f'<mutant {ad}>', 'exec'), mod.__dict__)
    try:
        yield
    finally:
        mod.__dict__[ad] = eski_f


def _o_esik():
    rng = np.random.default_rng(5)
    L = np.zeros(400)
    L[:200] = rng.normal(0, 0.1, 200)
    mk = np.zeros(400, bool)
    m, s = K.m_sigma(L, (0, 200), mk)
    r = L[5:195]
    mm = float(np.median(r))
    ok = abs(m - mm) < 1e-15 and abs(s - 1.4826 * float(np.median(np.abs(r - mm)))) < 1e-15
    L[200:] = m
    L[250:290] = m + 4.5 * s
    L[320:360] = m + 3.6 * s
    return ok and K.asimlar(L, m, s, (200, 400), mk) == [(250, 290)]


def _o_kopru():
    def ax(parcalar, maskeli=()):
        L = np.zeros(300)
        for a, b in parcalar:
            L[a:b] = 5.0
        mk = np.zeros(300, bool)
        mk[list(maskeli)] = True
        return K.asimlar(L, 0.0, 1.0, (0, 300), mk)
    return (ax([(100, 115), (135, 150)]) == [(100, 150)] and ax([(100, 115), (136, 151)]) == []
            and ax([(100, 115), (135, 150)], [125]) == [] and ax([(100, 130)]) == [(100, 130)]
            and ax([(100, 110), (115, 125)]) == []
            and ax([(100, 104), (120, 125), (131, 136)]) == [] and ax([(100, 105), (120, 125), (131, 136)]) == [(100, 136)])


def _o_kume():
    def ist(axs, Ls=None):
        return [dict(ax=a, L=(Ls[i] if Ls else np.zeros(600))) for i, a in enumerate(axs)]
    mk = np.zeros(600, bool)
    k = K.kumeler(ist([[(100, 140)], [(180, 220)], [(260, 300)]]), mk, (0, 600), tutarlilik=False)
    ok = len(k) == 1 and k[0]['uyeler'] == [0, 1, 2] and k[0]['I'] == (40, 360) and k[0]['Ip'] == (100, 300)
    ok &= K.kumeler(ist([[(100, 140)], [(181, 220)], [(260, 300)]]), mk, (0, 600), tutarlilik=False) == []
    ok &= K.kumeler(ist([[(100, 140), (150, 190)], [(120, 160)]]), mk, (0, 600), tutarlilik=False) == []
    rng = np.random.default_rng(6)
    a, b = rng.standard_normal(600), rng.standard_normal(600)
    axs = [[(200, 260)], [(200, 260)], [(200, 260)]]
    ok &= len(K.kumeler(ist(axs, [a, a, a]), mk, (0, 600))) == 1
    ok &= K.kumeler(ist(axs, [a, a, b]), mk, (0, 600)) == []          # 1 çift ≥ 0,5: tutarsız
    return bool(ok)


def _o_e1():
    ol = [dict(id='A', t0=0.0, M=7.0, P=1000.0, S=2000.0), dict(id='B', t0=0.0, M=6.99, P=3000.0, S=3500.0),
          dict(id='C', t0=0.0, M=6.0, P=4000.0, S=4500.0), dict(id='D', t0=0.0, M=5.99, P=5000.0, S=5500.0),
          dict(id='IKIZ', t0=105.0, M=7.2, P=6000.0, S=6500.0), dict(id='IKIZ2', t0=106.0, M=7.2, P=7000.0, S=7500.0),
          dict(id='IKIZ3', t0=100.0, M=6.9, P=8000.0, S=8500.0), dict(id='TET', t0=100.0, M=9.0, P=9000.0, S=9500.0)]
    bek = [(990.0, 1240.0), (1990.0, 2240.0), (2990.0, 3060.0), (3990.0, 4060.0), (6990.0, 7240.0), (7490.0, 7740.0),
           (7990.0, 8060.0)]
    return K.e1_araliklar(ol, 'TET', 100.0) == bek


def _o_taban():
    x = dict(W=(0, 100), L=np.zeros(100))
    mk = np.zeros(100, bool)
    mk[80:] = True
    return (K.w_son_acik(x, mk) == 79 and K.taban_ist(x, [(10, 20)], mk) and not K.taban_ist(x, [(10, 19)], mk)
            and K.taban_ist(dict(W=(0, 100), L=np.zeros(100)), [(10, 40)], np.zeros(100, bool))
            and not K.taban_ist(dict(W=(0, 100), L=np.zeros(100)), [(10, 39)], np.zeros(100, bool)))


def _o_mod():
    W = 600
    t = np.arange(W)
    cf = K.faz_cos(np.cos(2 * np.pi * t / 37.0 + 0.3))
    Lk = np.maximum(0, -np.roll(cf, 10))
    g = np.ones(W, bool)
    M = K.mod_istatistik(Lk, [cf], 100, 500, g)
    rng = np.random.default_rng(7)
    rng2 = np.random.default_rng(7)
    Lr = np.random.default_rng(8).standard_normal(W)
    o, p = K.mod_p(Lr, [cf], 100, 500, g, rng, n=20)
    say = sum(K.mod_istatistik(Lr, [np.roll(cf, int(rng2.integers(120, W - 120)))], 100, 500, g) >= o
              for _ in range(20))
    return M > 0.9999 and abs(p - (1 + say) / 21) < 1e-15


def _o_binom():
    def cdf(f, N, p):
        return sum(math.comb(N, k) * p ** k * (1 - p) ** (N - k) for k in range(f + 1))
    ok = True
    for n, p, x in ((8, 0.0766, 1), (8, 0.2, 3), (10, 0.05, 2), (5, 0.5, 5)):
        ok &= abs(K.binom_ust(n, p, x) - (1 - cdf(x - 1, n, p))) < 1e-12
    for f, N in ((0, 80), (2, 80), (4, 80), (3, 60)):
        pu = K.cp_ust(f, N)
        ok &= abs(cdf(f, N, pu) - 0.05) < 1e-9
    ok &= K.x_min(8, 2, 80) == 3 and K.x_min(8, 5, 80) == 'K2' and K.x_min(8, 4, 80) == 3
    return bool(ok)


def _o_pmin():
    return (all(abs(K.p_min(n) - (1 - 0.05 ** (1 / n)) / 0.9) < 1e-15 for n in range(5, 12))
            and K.p_min(4) is None and round(K.p_min(7), 2) == 0.39)


def _o_basamak():
    A = [1.0, 2.0, 3.0, 4.0, 5.0]
    return K.basamak(A, [0.0, 0.6, 0.4, 0.95, 1.0], 0.5) == 4.0 and K.basamak(A, [0.0] * 5, 0.5) is None


def _o_k1():
    f = T.k1_dal
    return (f(False, [], False, 10.0, 10, 0) == ('a', False) and f(True, [True, True], True, None, 10, 0) == ("b'", False)
            and f(True, [True, False], True, None, 10, 0) == ('b', False)
            and f(True, [], False, 1e5, 10, 0) == ('c', False) and f(True, [], False, 1e5 * 1.0001, 10, 0)[0] == 'd'
            and f(True, [], False, 'belirsiz', 10, 0)[0] == 'd' and f(True, [], True, 50.0, 10, 0)[0] == 'd'
            and f(True, [False], True, None, 10, 3) == ('b', False) and f(True, [False], True, None, 10, 4) == ('b', True)
            and f(True, [False], True, None, 4, 0) == ('b', True))


def _o_2026():
    ok = True
    try:
        K.pencere_hesapla('2025-12-31T23:23:20', 2800.0)            # W sonu + 600 = 2026-01-01T00:00:00
        ok = False
    except K.CekirdekHata:
        pass
    K.pencere_hesapla('2025-12-31T23:23:19', 2800.0)
    try:
        I.dataselect_url('koeri', 'KO', 'X', '', ['HHZ'], '2025-12-31T23:00:00', '2026-01-01T00:00:00')
        ok = False
    except I.SinirIhlali:
        pass
    I.dataselect_url('koeri', 'KO', 'X', '', ['HHZ'], '2025-12-31T23:00:00', '2025-12-31T23:59:59.999')
    return ok


def _nacik_dunya():
    D = dict(pen={}, olay={})
    pay = {'B1': [0.4], 'WH': [0.3, 0.7], 'B3': [0.5], 'B4': [0.51]}
    alg = dict(pencere_segment={})
    for b, ps in pay.items():
        for i, w in enumerate(ps):
            pid = f'tet|{b}{i}'
            D['pen'][pid] = dict(id=pid, tur='tet', bolge='Marmara', birim=b, seg={'S2': []})
            alg['pencere_segment'][f'{pid}|S2'] = dict(algilama=False, W_payi=w, tau_olc=None, mod=[], lp_referans=None)
    x1 = dict(birimler=list(pay), n=4, bant='veri yok', tau={b: 3.0 for b in pay}, tau_n=3.0)
    k0 = {'x1': {'S2': x1}, 'x1/3': {'S2': dict(n=0, bant='veri yok')}, 'x3': {'S2': dict(n=4, bant='veri yok')}}
    neg = dict(segment={'S2': dict(N=40, f=0, mda=dict(A50=1.0, A90=2.0, n_deneme=40))})
    return D, k0, neg, alg


def _o_nacik():
    D, k0, neg, alg = _nacik_dunya()
    g, _ = T.seg_veri(D, k0, neg, alg, 'S2', dict(tau_olc_bolu_kaba=None))
    return g['n_acik'] == 2


MUTASYONLAR = [
    ('eşik 4σ → 3,5σ', _o_esik, lambda: mock.patch.object(K, 'KSIG', 3.5)),
    ('σ: R kenarı atılmıyor', _o_esik, lambda: mock.patch.object(K, 'R_KENAR', 0)),
    ('köprü: maskeli boşluk köprülenir', _o_kopru,
     lambda: mutant(K, 'asimlar', ' and not kapali[b + 1:x].any()', '')),
    ('köprü: boşluk < 20', _o_kopru, lambda: mutant(K, 'asimlar', 'x - b - 1 <= BOSLUK', 'x - b - 1 < BOSLUK')),
    ('aşım: ≥15 saniye şartı yok', _o_kopru, lambda: mock.patch.object(K, 'NUST', 1)),
    ('küme: ±20 yerine ±19', _o_kume, lambda: mock.patch.object(K, 'KUME_PAY', 19)),
    ('küme: istasyon yerine parça sayısı', _o_kume,
     lambda: mutant(K, 'kumeler', 'if len(uy) < N_IST_MIN', 'if len(ps) < N_IST_MIN')),
    ('küme: ≥3 yerine ≥1 tutarlı çift', _o_kume, lambda: mock.patch.object(K, 'KORR_CIFT', 1)),
    ('E1: M ≥ 7,0 yerine > 7,0', _o_e1, lambda: mutant(K, 'e1_kurallar', 'M >= E1_M7', 'M > E1_M7')),
    ('E1: M 6,x için S de', _o_e1, lambda: mutant(K, 'e1_kurallar', "else [('P', k)]", "else [('P', k), ('S', k)]")),
    ('E1: ikiz kuralı < 5 sn', _o_e1, lambda: mutant(K, 'e1_dislanir', '<= E1_IKIZ_S', '< E1_IKIZ_S')),
    ('E1: ikiz kuralı büyüklüksüz', _o_e1, lambda: mutant(K, 'e1_dislanir', " and o['M'] >= E1_M7", '')),
    ('3a: W′_son maskeyi yok sayar', _o_taban,
     lambda: mutant(K, 'w_son_acik', 'acik = ~maske[W0:W1] & ', 'acik = ')),
    ('3a: W sonu − 59', _o_taban, lambda: mock.patch.object(K, 'TABAN_S', 59)),
    ('modülasyon: yalnız s = +1', _o_mod, lambda: mutant(K, 'mod_istatistik', 'for s in (1, -1)', 'for s in (1,)')),
    ('modülasyon: gecikme 0…9', _o_mod,
     lambda: mutant(K, 'mod_istatistik', 'range(0, MOD_LAG + 1)', 'range(0, MOD_LAG)')),
    ('modülasyon: p = say/n', _o_mod, lambda: mutant(K, 'mod_p', 'return o, (1 + say) / (n + 1)', 'return o, say / n')),
    ('binom: ≥ X yerine > X', _o_binom, lambda: mutant(K, 'binom_ust', 'range(x, n + 1)', 'range(x + 1, n + 1)')),
    ('Clopper–Pearson iki yanlı', _o_binom, lambda: mutant(K, 'cp_ust', 'cdf > a', 'cdf > a / 2')),
    ('p_min: /0,9 yok', _o_pmin, lambda: mutant(K, 'p_min', '/ 0.9 ', ' ')),
    ('p_min: n_açık ≥ 5 yerine > 5', _o_pmin, lambda: mutant(K, 'p_min', 'n_acik >= 5', 'n_acik > 5')),
    ('n_açık: Wharton bir pencereyle açık', _o_nacik,
     lambda: mutant(T, 'seg_veri', "all(e['W_payi'] is not None and e['W_payi'] <= 0.5 for e in es)",
                    "any(e['W_payi'] is not None and e['W_payi'] <= 0.5 for e in es)")),
    ('n_açık: ≤ 0,50 yerine < 0,50', _o_nacik,
     lambda: mutant(T, 'seg_veri', "e['W_payi'] <= 0.5 for", "e['W_payi'] < 0.5 for")),
    ('MDA: üstündeki basamak şartı yok', _o_basamak,
     lambda: mutant(K, 'basamak', 'all(p >= q for p in P[j:])', 'P[j] >= q')),
    ('K1: b′ için "her küme" yerine "bir küme"', _o_k1, lambda: mutant(T, 'k1_dal', 'all(belirsiz)', 'any(belirsiz)')),
    ('K1: A90_PK < 100 µm/s', _o_k1, lambda: mutant(T, 'k1_dal', 'A90_PK <= A90_PK_TAVAN', 'A90_PK < A90_PK_TAVAN')),
    ('K1: FAR_PK ≥ 0,30', _o_k1, lambda: mutant(T, 'k1_dal', 'f_PK / N_PK > FAR_PK_ESIK', 'f_PK / N_PK >= FAR_PK_ESIK')),
    ('K1: algılama K1 aralığı dışında → c', _o_k1,
     lambda: mutant(T, 'k1_dal', 'elif not algilama and', 'elif')),
    ('2026: pencere > yerine ≥', _o_2026, lambda: mutant(K, 'pencere_hesapla', '>= SON_AN', '> SON_AN')),
    ('2026: istek sınırı', _o_2026, lambda: mutant(I, 'sinir', 't1 >= SON_AN', 't1 > SON_AN')),
]


class KodIncelemeMutasyon(unittest.TestCase):
    """Bağımsız kod incelemesi: her kahin doğru kodda geçer, her mutasyonda kalır."""

    def test_kahinler_dogru_kodda_gecer(self):
        for ad, f in (('eşik', _o_esik), ('köprü', _o_kopru), ('küme', _o_kume), ('E1', _o_e1), ('3a', _o_taban),
                      ('modülasyon', _o_mod), ('binom', _o_binom), ('p_min', _o_pmin), ('basamak', _o_basamak),
                      ('K1', _o_k1), ('2026', _o_2026), ('n_açık', _o_nacik)):
            self.assertTrue(f(), ad)

    def test_mutasyonlar_yakalanir(self):
        kacan = []
        for ad, kahin, yama in MUTASYONLAR:
            with yama():
                try:
                    sonuc = kahin()
                except (K.CekirdekHata, I.SinirIhlali, AssertionError, TypeError, ValueError):
                    sonuc = False
            if sonuc:
                kacan.append(ad)
        self.assertEqual(kacan, [], kacan)
        self.assertGreaterEqual(len(MUTASYONLAR), 10)


# ====================================================================== hüküm kalıpları: metinden bağımsız yeniden türetme
def _sayi(x, n=2):
    return ('%.' + str(n) + 'f') % x


def _tr(x, n=2):
    return _sayi(x, n).replace('.', ',')


def _cp(f, N):
    lo, hi = 0.0, 1.0
    for _ in range(200):
        m = (lo + hi) / 2
        c = sum(math.comb(N, k) * m ** k * (1 - m) ** (N - k) for k in range(f + 1))
        if c > 0.05:
            lo = m
        else:
            hi = m
    return (lo + hi) / 2


def _bin(n, p, x):
    return 1 - sum(math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(x))


def _xmin(n, f, N, a):
    if f > math.floor(0.05 * N):
        return 'K2'
    pu = _cp(f, N)
    for X in range(2, n + 1):
        if _bin(n, pu, X) <= a:
            return X
    return None


def _A(x):
    if not isinstance(x, float):
        return str(x)
    b = 2 - int(math.floor(math.log10(abs(x))))
    return f'{round(x, b):.{max(0, b)}f}'.replace('.', ',')


def bagimsiz_cumle(g, k1):
    """§7.2 ve §8 metninden (kodun kendisine bakmadan) yazılmış kalıp üretici; biçim: τ 2, olasılık 3 ondalık, A 3
    anlamlı basamak, ondalık virgül; 'n' yerine sayı (metindeki ekler korunur)."""
    s, n, N, f = g['seg'], g['n'], g['N'], g['f']
    dal = k1['dal']
    if dal in ('a', 'c', 'd'):
        neden = {'a': 'ölçü sınanamadı (Parkfield verisi yok)', 'd': 'ölçü sınanamadı (yöntem)',
                 'c': 'ölçü sınanamadı (Tohoku tremoru Parkfield yüzey ağının gürültüsünde görülmedi; A90_PK = '
                      + _A(k1.get('A90_PK')) + ' nm/s)'}[dal]
        return f'{s}: {neden}.'
    if n < 5:
        return f'{s}: veri yok.'
    if N < 5 * n:
        return f'{s}: ölçü güvenilmez (negatif kontrol yetersiz).'
    if f > math.floor(0.05 * N):
        return f'{s}: ölçü güvenilmez.'
    xm = _xmin(n, f, N, 0.05)
    xm7 = _xmin(n, f, N, 0.05 / 7)
    var = (xm is not None and g['X_mod'] >= xm and k1['mod_gecti'] and not k1['ayirt_degil'] and dal != "b'"
           and g['lp_ref'])
    if var:
        olc = (f"ölçülen τ ≥ {_tr(g['tau_olc_alg_min'])} kPa" if g['tau_olc_alg_min'] is not None
               else 'ölçülen τ ölçülemedi')
        return (f"{s}: tetiklenmiş tremor VAR. {n} bağımsız tetikleyicinin {g['X_mod']}'unda, yerel deprem ve "
                'teleseismik cisim dalgası maskesi ile darbe/sızıntı/taban ayıklamasından sonra ≥3 istasyonda tutarlı '
                've yüzey dalgasıyla eş periyotlu modülasyonlu (p ≤ 0,01; ölçü faz kilidini 20 sn periyodik, kilitsiz '
                'modülasyondan ayıramaz, yapayda yanlış pozitif 0,33–0,56) 2–8 Hz tremor (tetiklenmiş yerel '
                'mikrodeprem kümesi darbe kuralının ayırabildiği kadar dışlandı); negatif kontrolde FAR = '
                f"{f}/{N}; kaba τ ≥ {_tr(g['tau_alg_min'])} kPa ({olc}) (segment düzeyi α = 0,05; yedi segment için "
                f"düzeltilmedi; X_min^(0,05/7) = {'yok' if xm7 is None else xm7}, "
                f"{'sağlandı' if isinstance(xm7, int) and g['X_mod'] >= xm7 else 'sağlanmadı'}).")
    if g['X_alg'] >= 1:
        sag = []
        if xm is None:
            sag.append('X_min yok')
        elif g['X_mod'] < xm:
            sag.append(f"X_mod ≥ X_min(n, f) (X_mod = {g['X_mod']}, X_min = {xm})")
        if not k1['mod_gecti']:
            sag.append('Parkfield modülasyonu geçmedi (modülasyon ölçüsü pozitif kontrolde doğrulanmadı)')
        if k1['ayirt_degil']:
            sag.append('K1 ayırt edici değil')
        if dal == "b'":
            sag.append('K1 yalnız belirsiz geçti')
        if not g['lp_ref']:
            sag.append('uzun periyot başvuru istasyonu yok')
        return (f"{s}: aday, doğrulanmadı. {g['X_alg']} tetikleyicide algılama; negatif kontrole göre {n} tetikleyicide "
                f"beklenen yanlış algılama n·f/N = {_tr(n * f / N)}, P(Bin(n, p_üst) ≥ X_alg) = "
                f"{_tr(_bin(n, _cp(f, N), g['X_alg']), 3)}; VAR şartlarından sağlanmayan: {'; '.join(sag)}.")
    bas = s + (' (yalnız kaba τ ölçeğinde):' if g['bant13'] == 'veri yok' or g['bant_olc'] == 'veri yok' else ':')
    if g['n_acik'] >= 5:
        dis = (f"; tetikleyici başına ≥ {_tr((1 - 0.05 ** (1 / g['n_acik'])) / 0.9)} olasılıkla bu genliği aşan "
               'tremor üreten bir kaynak %95 düzeyinde dışlanır.')
    else:
        dis = "; dışlama hesaplanmadı (W'si yarıdan az maskeli birim < 5)."
    a90 = _A(g['A90']) + (' nm/s' if isinstance(g['A90'], float) else '')
    c = (f"{bas} kaba τ ≥ {_tr(g['X'])} kPa üstündeki {n} bağımsız tetikleyicide ({g['n_acik']}'ının W'si en az yarı "
         f"yarıya maskesiz) tetiklenmiş tremor görülmedi; algılanabilir en küçük genlik A90 = {a90} (25 km'de, 300 sn "
         f"boyunca 2–8 Hz RMS; A50 = {_A(g['A50'])}){dis}{' Zayıf bant.' if 5 <= n < 8 else ''} Ölçek uyarısı: kaba "
         f"τ ×1/3 alınırsa {g['n13']} birim ≥ 2 kPa ({g['bant13']}); ölçülen τ ile {g['n_olc']} birim ≥ 2 kPa "
         f"({g['bant_olc']}); Parkfield–Tohoku'da τ_ölç / kaba τ = "
         f"{_tr(g['oran_pk']) if g['oran_pk'] is not None else 'ölçülemedi'}.")
    if dal == "b'":
        c = c[:-1] + ' (K1 yalnız belirsiz geçti).'
    return c


class HukumKalibiBagimsiz(unittest.TestCase):
    def test_D11_beklenen_cumleler_bagimsiz_turetimle_ayni(self):
        for ad, g, k1, bek in T.D11_SENARYO:
            k = dict(dict(ayirt_degil=False, mod_gecti=False), **k1)
            self.assertEqual(bagimsiz_cumle(g, k), bek, ad)

    def test_rastgele_senaryolar(self):
        rng = np.random.default_rng(20261112 + 7070)
        bantlar = ('tam', 'zayıf', 'veri yok')
        say = {}
        for _ in range(3000):
            n = int(rng.integers(3, 11))
            N = int(rng.choice([10 * n, 5 * n, 5 * n - 1, 9 * n]))
            Xa = int(rng.integers(0, n + 1)) if rng.random() < 0.6 else 0
            g = T._g(seg=str(rng.choice(['S1', 'S2', 'S3', 'S5'])), n=n, bant=K.bant(n), N=N,
                     f=int(rng.integers(0, 7)), X_alg=Xa, X_mod=int(rng.integers(0, Xa + 1)), lp_ref=bool(rng.random() < 0.8),
                     n_acik=int(rng.integers(0, n + 1)), A50=float(rng.choice([355.0, 1259.0, 0.5])),
                     A90=rng.choice([446.0, 12589.25, 'belirsiz', '> 100 µm/s']),
                     X=float(rng.uniform(2, 10)), tau_alg_min=float(rng.uniform(2, 20)),
                     tau_olc_alg_min=(None if rng.random() < 0.3 else float(rng.uniform(0.1, 9))),
                     n13=int(rng.integers(0, n + 1)), bant13=str(rng.choice(bantlar)), n_olc=int(rng.integers(0, n + 1)),
                     bant_olc=str(rng.choice(bantlar)), oran_pk=(None if rng.random() < 0.3 else float(rng.uniform(0, 1))))
            if isinstance(g['A90'], np.str_):
                g['A90'] = str(g['A90'])
            k1 = dict(dal=str(rng.choice(['b', 'b', "b'", 'a', 'c', 'd'])), ayirt_degil=bool(rng.random() < 0.2),
                      mod_gecti=bool(rng.random() < 0.7), A90_PK=float(rng.uniform(10, 9e4)))
            h = T.segment_hukmu(g, k1)
            self.assertEqual(h['cumle'], bagimsiz_cumle(g, k1), (g, k1))
            say[h['tur']] = say.get(h['tur'], 0) + 1
        for t in ('VAR', 'aday', 'görülmedi', 'veri yok', 'ölçü güvenilmez', 'ölçü sınanamadı'):
            self.assertGreater(say.get(t, 0), 20, say)


# ====================================================================== hızlandırma: süzgeç bit düzeyinde aynı
class Hiz(unittest.TestCase):
    def test_bant_gecir_obspy_ile_bit_ayni(self):
        rng = np.random.default_rng(20261112 + 8080)
        for n, fs in ((200001, 100.0), (60000, 20.0), (150000, 40.0)):
            x = rng.standard_normal(n)
            y = np.zeros(n)
            i = n // 3
            y[i:i + 3000] = rng.standard_normal(3000) * np.hanning(3000)
            zz = np.zeros(n)
            zz[50:4000] = rng.standard_normal(3950)
            for v in (x, y, zz, np.zeros(n)):
                for lo, hi in ((2.0, 8.0), (0.5, 1.0), (0.5, 8.0)):
                    a = K.bant_gecir_obspy(v, fs, lo, hi)
                    b = K.bant_gecir(v, fs, lo, hi)
                    self.assertTrue(np.array_equal(a.view(np.int64), b.view(np.int64)), (n, fs, lo, hi))

    def test_kd_isi_eski_yeni_ayni(self):
        yeni = K.bant_gecir
        try:
            K.bant_gecir = K.bant_gecir_obspy
            T._KD.clear()
            a = T.kd_is('D6', (0, 100.0, 0.0), 4242, 1)
        finally:
            K.bant_gecir = yeni
        T._KD.clear()
        b = T.kd_is('D6', (0, 100.0, 0.0), 4242, 1)
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))

if __name__ == '__main__':
    unittest.main(verbosity=2)
