#!/usr/bin/env python3
"""TR-4 koşu kodunun YALNIZ yapay veriyle sınanması: yapay miniSEED, yerel sahte FDSN sunucusu (yalnız 127.0.0.1),
yapay saatlik ÇİF deposu. Gerçek dalga formu ya da üstveri açılmaz ve istenmez; ağ çağrıları 127.0.0.1 dışına
gidemez (urlopen sarmalanır).

Sınamalar:
  S01 plan: kronolojik sıra (2014-01 … 2023-12, ayda istasyon kod sırası, sonra bilgi 13), kademe C günleri 1–20
  S02 2026 kapısı ve körlük: bağlantı kurulmadan red (sunucu bağlantı sayısı 0)
  S03 indirme uçtan uca: POST biçimi, genel User-Agent, ≥ 2 sn aralık, 503 → yeniden deneme, 403 aşılmaz, iki hata →
      bırakılır, > %5 → tek tur, ham dosya silinir, ÇİF dosyası sha256'lı, 429 Retry-After
  S04 sürdürme: sure_sn ile temiz çıkış, sonraki iş kaldığı yerden; süre kesmesi deneme sayılmaz; çift kayıt yok
  S05 kesik koşu: 21 etkin gün / 42 takvim günü; "kesildi" kalıcı; tamamlanan T sayımı yalnız kesin kodlarla
  S06 ε yasağı: indirme bitmeden olc durur
  S07 saatlik ön işlem: boşluk kuralı, ÇİF kuralı (doğrudan zaman alanı toplamıyla), bilinen gecikme, miniSEED → ÇİF
  S08 enerji reddi ve günlük ÇİF (≥ 2 saat, maske)
  S09 TR-5b başvurusuyla eşdeğerlik: dondurulmuş npz dizilerinden saatlik ÇİF kurulur, koşu yolundan Δ ve oran
      tr5b_yapay_ccf_ref.json (ve C maskesiyle tr4_yapay_ref.json) toleranslarında
  S10 önyükleme ve kestiriciler (bağımsız yeniden hesap), (c) eşikleri
  S11 hüküm kalıbının her dalı (9 hüküm adı) ve metinlerin ön kayıt kalıplarıyla birebirliği; bilgi satırı 0 iki biçim
  S12 tek koşu: hukum.json farklı hükümle yeniden yazılamaz
  S13 1b gün doluluğu kapısı
  S14 uçtan uca ölçü (yavaş): yapay depo, 10 yer × T 2017/2020, gerçek kod denetimi (i) → "taban ölçüldü"
  MUT mutasyonlar (≥ 8): kodun kopyası değiştirilir, hızlı sınamalar yeniden koşulur; her mutant yakalanmalı

Kullanım: python3 -I -B tr4_test_yapay.py <karalama_dizini> <npz> [--hizli] [--mutasyon] [--kod <dizin>]
"""
import contextlib, datetime as dt, hashlib, http.server, importlib.util, io, json, math, os, shutil, socket, subprocess
import sys, threading, time, urllib.parse, urllib.request

import numpy as np

KOD = os.path.dirname(os.path.abspath(__file__))
for i, a in enumerate(sys.argv):
    if a == '--kod': KOD = sys.argv[i + 1]
TD = dt.timedelta


def yukle(ad, yol):
    sp = importlib.util.spec_from_file_location(ad, yol); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return m


# ---------------------------------------------------------------- ağ korkuluğu: yalnız 127.0.0.1
_asil_urlopen = urllib.request.urlopen


def _korunan_urlopen(req, *a, **kw):
    url = req.full_url if hasattr(req, 'full_url') else req
    h = urllib.parse.urlparse(url).hostname
    if h != '127.0.0.1': raise RuntimeError(f'SINAMA AĞ KORKULUĞU: {h} yasak')
    return _asil_urlopen(req, *a, **kw)


urllib.request.urlopen = _korunan_urlopen
_asil_conn = socket.create_connection


def _korunan_conn(adr, *a, **kw):
    if adr[0] not in ('127.0.0.1', 'localhost'): raise RuntimeError(f'SINAMA AĞ KORKULUĞU: {adr}')
    return _asil_conn(adr, *a, **kw)


socket.create_connection = _korunan_conn

IN = yukle('tr4_indir', os.path.join(KOD, 'tr4_indir.py'))
K = yukle('tr4_kosu', os.path.join(KOD, 'tr4_kosu.py'))
K.IN = IN

SONUC = []


def sina(ad):
    def d(f):
        def g(*a, **kw):
            t0 = time.time()
            try:
                f(*a, **kw); SONUC.append((ad, True, '')); print(f'GEÇTİ {ad} ({time.time() - t0:.1f} sn)', flush=True)
            except BaseException as e:                                # SystemExit da yakalanır
                import traceback
                yer = [l.strip() for l in traceback.format_exc().splitlines() if l.strip().startswith('File')][-1:]
                SONUC.append((ad, False, f'{type(e).__name__}: {e} {yer}')); print(f'KALDI {ad}: {type(e).__name__}: {e} {yer}', flush=True)
        g.ad = ad; return g
    return d


# ---------------------------------------------------------------- sahte saat
class Saat:
    def __init__(self, t=1.8e9): self.t = t; self.uykular = []
    def simdi(self): return self.t
    def uyu(self, s): self.uykular.append(s); self.t += s


def saat_tak(t=1.8e9):
    S = Saat(t); IN.simdi = S.simdi; IN.uyu = S.uyu; return S


# ---------------------------------------------------------------- sahte FDSN sunucusu
class Sunucu:
    """POST/GET dataselect. davranis: istasyon-ay anahtarı ('KO.X01|2017-03') -> eylem kuyruğu
    (200 | 204 | 403 | 404 | 500 | 503 | 429 | 'sifirla'). veri: 'kisa' (pencere başına 10 sn) ya da 'tam'."""
    def __init__(self, veri='kisa', davranis=None, saat=None):
        self.veri = veri; self.davranis = davranis or {}; self.istekler = []; self.baglanti = 0; self.saat = saat
        S = self

        class H(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a): pass

            def _isle(self, govde):
                S.baglanti += 1
                satir = [l.split() for l in govde.strip().splitlines() if l.strip()]
                k = f'KO.{satir[0][1]}|{satir[0][4][:7]}' if satir else '?'
                if satir:   # gün d yerel tarihtir: UTC başlangıcı (d−1) 22:00 olabilir → ay, son satırın bitişinden
                    k = f'KO.{satir[0][1]}|{satir[-1][5][:7]}'
                S.istekler.append(dict(k=k, ua=self.headers.get('User-Agent'), yontem=self.command, satir=len(satir),
                                       t=S.saat.t if S.saat else time.time(), govde=govde))
                q = S.davranis.get(k, [])
                e = q.pop(0) if q else 200
                if e == 'sifirla':
                    self.send_response(200); self.send_header('Content-Length', '100000'); self.end_headers()
                    self.wfile.write(b'x' * 1000); self.wfile.flush()
                    self.connection.shutdown(socket.SHUT_RDWR); return
                if e in (429, 503):
                    self.send_response(e); self.send_header('Retry-After', '7'); self.end_headers(); return
                if e != 200:
                    self.send_response(e); self.end_headers(); return
                b = mseed_uret(satir, S.veri)
                self.send_response(200); self.send_header('Content-Length', str(len(b))); self.end_headers(); self.wfile.write(b)

            def do_POST(self):
                n = int(self.headers.get('Content-Length', 0)); self._isle(self.rfile.read(n).decode())

            def do_GET(self):
                q = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(self.path).query))
                self._isle(f"{q['net']} {q['sta']} {q['loc']} {q['cha']} {q['start']} {q['end']}\n")

        self.srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), H)
        self.url = f'http://127.0.0.1:{self.srv.server_address[1]}/fdsnws/dataselect/1/query'
        self.th = threading.Thread(target=self.srv.serve_forever, daemon=True); self.th.start()

    def kapat(self): self.srv.shutdown(); self.srv.server_close()


def yapay_iz(t0, n, fs, rng, gecikme_sn=2.0):
    """Z = s, N = s + gürültü, E = s(t − gecikme) + gürültü (tutarlı ÇİF)."""
    s = rng.standard_normal(n + 400)
    k = int(gecikme_sn * fs)
    return dict(Z=s[200:200 + n] * 1000, N=(s[200:200 + n] + 0.5 * rng.standard_normal(n)) * 1000,
                E=(s[200 - k:200 - k + n] + 0.5 * rng.standard_normal(n)) * 1000)


def mseed_uret(satir, veri, fs=100.0):
    from obspy import Stream, Trace, UTCDateTime
    st = Stream()
    for p in satir:
        ag, ist, loc, cha, a, b = p
        t0 = UTCDateTime(a); dur = (UTCDateTime(b) - t0) if veri == 'tam' else 10.0
        n = int(round(dur * fs))
        rng = np.random.default_rng(int(t0.timestamp) % 2 ** 31)
        iz = yapay_iz(t0, n, fs, rng)
        for c in 'ZNE':
            tr = Trace(data=np.round(iz[c]).astype(np.int32))
            tr.stats.network, tr.stats.station, tr.stats.location = ag, ist, '' if loc == '--' else loc
            tr.stats.channel, tr.stats.sampling_rate, tr.stats.starttime = cha[:2] + c, fs, t0
            st.append(tr)
    b = io.BytesIO(); st.write(b, format='MSEED', encoding='STEIM2', reclen=4096); return b.getvalue()


# ---------------------------------------------------------------- yapay girdiler
def yapay_G(istler, Tler, kademe='C', b13=False, bicim='POST'):
    W = []
    for s in istler:
        for T in Tler:
            T = dt.date(T, 1, 1)
            W.append(dict(k=f'{s}|{T}', ist=s, yer=s, T=T, a=T - TD(days=1095), b=T - TD(days=8), loc='', bant='HH',
                          yatay=['N', 'E']))
    kon = {s: (40.9, 29.0 + 0.01 * i) for i, s in enumerate(istler + ['KO.SLVT'])}
    B = dict(k='KO.SLVT|2025-04-23', ist='KO.SLVT', yer='KO.SLVT', T=dt.date(2025, 4, 23), loc='', bant='HH', yatay=['N', 'E']) if b13 else None
    return dict(W=W, b13=B, kademe=kademe, bicim=bicim, hiz=dict(kademe=kademe, v_medyan_KiBs=119.0, ek_metin='aşama H hızları 20,0, 25,0, 22,0 KiB/s; medyan 22,0; V_D / v = 81,0 gün; bilgi satırı 0: hesaplanmadı (indirme yok)'),
                S0=dict(hukum='G0 geçti', dolu_yer_pencere=max(30, len(W)), yer_T={str(y): 0 for y in range(2017, 2025)}),
                konum=kon)


def yapay_csv(G, dizin):
    """tr4_pencereler.csv biçiminde yapay satırlar ve sayım json'u (maske olayı yok); sha sabitleri sınamaya özgü."""
    import csv
    alan = ['ist', 'T', 'a', 'b', 'maske_gun', 'maske_olay', 'sakin_ileri_2y', 'sakin_M7_500', 'sakin_M5_50_pencere',
            'sakin_M55_100_genis', 'DOLU_gevsek', 'DOLU_siki', 'yer']
    y = os.path.join(dizin, 'pencereler.csv')
    with open(y, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, alan); w.writeheader()
        for x in G['W']:
            w.writerow(dict(ist=x['ist'], T=x['T'].isoformat(), a=x['a'].isoformat(), b=x['b'].isoformat(), maske_gun=0,
                            maske_olay='', sakin_ileri_2y='True', sakin_M7_500='True', sakin_M5_50_pencere='True',
                            sakin_M55_100_genis='True', DOLU_gevsek='True', DOLU_siki='True', yer=x['yer']))
    sy = os.path.join(dizin, 'sayim.json')
    IN.yaz_json(sy, dict(olay_uzaklik={'us70005lkl': dict(t='2019-09-26')}))
    G['csv_yol'] = y; G['sayim_yol'] = sy
    K.SHA['tr4_pencereler.csv'] = IN.sha_dosya(y); K.SHA['tr4_onkayit_sayim.json'] = IN.sha_dosya(sy)
    return G


def temiz(d):
    shutil.rmtree(d, ignore_errors=True); os.makedirs(d); return d


# ================================================================ sınamalar
@sina('S01 plan: kronolojik sıra ve kademe C günleri')
def s01(KAR):
    G = yapay_G(['KO.B02', 'KO.A01'], [2017, 2020], b13=True)
    P = IN.plan(G)
    anah = [(x['ay'], x['ist']) for x in P if x['rol'] == 'ana']
    assert anah == sorted(anah), 'ay sonra istasyon sırası bozuk'
    assert P[0]['ay'] == '2014-01' and [x for x in P if x['rol'] == 'ana'][-1]['ay'] == '2019-12'
    assert all(dt.date.fromisoformat(g).day <= 20 for x in P if x['rol'] == 'ana' for g in x['gunler'])
    assert max(len(x['gunler']) for x in P if x['rol'] == 'ana') == 20
    i13 = [i for i, x in enumerate(P) if x['rol'] == 'bilgi13']
    assert i13 and min(i13) > max(i for i, x in enumerate(P) if x['rol'] == 'ana'), 'bilgi 13 ana aylardan sonra gelmeli'
    g13 = sorted(dt.date.fromisoformat(g) for x in P if x['rol'] == 'bilgi13' for g in x['gunler'])
    T = dt.date(2025, 4, 23)
    assert g13[0] == T - TD(days=400) + TD(days=(0 if (T - TD(days=400)).day <= 20 else 0)) or g13[0].day <= 20
    assert all(d in g13 for d in [T + TD(days=i) for i in range(-69, 31)]), '[T−69, T+30] her gün olmalı'
    assert all(d.day <= 20 for d in g13 if d < T - TD(days=69)) and g13[-1] == T + TD(days=30)
    GA = yapay_G(['KO.A01'], [2017], kademe='A'); PA = IN.plan(GA)
    assert sum(len(x['gunler']) for x in PA) == 1088
    # yer-penceresinin ay listesi
    assert len(IN.pencere_aylari(G['W'][0], 'C')) == 36
    # kademe seçilmemişse plan yok
    G2 = yapay_G(['KO.A01'], [2017]); G2['kademe'] = 'ertelendi (aktarım hızı)'
    try: IN.plan(G2); raise AssertionError('kademesiz plan kuruldu')
    except SystemExit: pass


@sina('S02 2026 kapısı ve körlük: bağlantıdan önce red')
def s02(KAR):
    D = IN.kor_denet
    for bit, gun, rol, ok in [(dt.datetime(2023, 12, 24, 2), dt.date(2023, 12, 24), 'ana', True),
                              (dt.datetime(2023, 12, 25, 2), dt.date(2023, 12, 25), 'ana', False),
                              (dt.datetime(2025, 5, 31, 2), dt.date(2025, 5, 31), 'bilgi13', True),
                              (dt.datetime(2025, 6, 1, 2), dt.date(2025, 6, 1), 'bilgi13', False),
                              (dt.datetime(2026, 1, 1, 0), dt.date(2025, 12, 31), 'bilgi13', False),
                              (dt.datetime(2026, 1, 1, 2), dt.date(2026, 1, 1), 'ana', False)]:
        try: D(bit, gun, rol); r = True
        except SystemExit: r = False
        assert r == ok, (bit, gun, rol)
    # uçtan uca: plan dışı bir 2026 isteği bağlantı kurulmadan reddedilir
    saat_tak(); srv = Sunucu()
    try:
        G = yapay_G(['KO.A01'], [2017])
        kotu = dict(k='KO.A01|2026-01', ist='KO.A01', ay='2026-01', rol='ana', loc='', bant='HH', yatay=['N', 'E'],
                    gunler=['2026-01-02'])
        IN_plan = IN.plan; IN.plan = lambda G: [kotu]
        depo = temiz(os.path.join(KAR, 's02'));
        try:
            IN.indir(None, depo, os.path.join(depo, 'yerel'), 600, taban=srv.url, G=G); raise AssertionError('2026 isteği reddedilmedi')
        except SystemExit as e:
            assert 'KÖRLÜK' in str(e)
        finally:
            IN.plan = IN_plan
        assert srv.baglanti == 0, 'bağlantı kuruldu'
        # plan düzeyinde: ana pencerenin bitişi 2023-12-24'ü aşamaz
        G3 = yapay_G(['KO.A01'], [2024], kademe='A'); G3['W'][0]['b'] = dt.date(2023, 12, 26)
        try: IN.plan(G3); raise AssertionError('plan 2023-12-24 sonrasını kabul etti')
        except AssertionError as e:
            if 'kabul' in str(e): raise
    finally:
        srv.kapat()


def kisa_depo(KAR, ad, davranis, sure=6000, G=None, saat=None, kademe='C'):
    S = saat or saat_tak()
    srv = Sunucu('kisa', davranis, S)
    G = G or yapay_G(['KO.A01', 'KO.B02'], [2017], kademe=kademe)
    depo = os.path.join(KAR, ad)
    return S, srv, G, depo


@sina('S03 indirme uçtan uca: biçim, nezaket, kesin kodlar, tek tur')
def s03(KAR):
    depo = temiz(os.path.join(KAR, 's03'))
    S = saat_tak()
    dav = {'KO.A01|2014-01': [503, 200], 'KO.B02|2014-01': [403], 'KO.A01|2014-02': ['sifirla', 'sifirla', 200],
           'KO.B02|2014-02': [500, 500, 500], 'KO.A01|2014-03': [429, 204]}
    srv = Sunucu('kisa', dav, S)
    try:
        G = yapay_G(['KO.A01', 'KO.B02'], [2017])
        for _ in range(4):
            B = IN.indir(None, depo, os.path.join(KAR, 's03_yerel'), 6000, taban=srv.url, G=G)
            if B['durum'] == 'bitti': break
        assert B['durum'] == 'bitti', B['durum']
        L = IN.satirlar(IN.durum_yollari(depo)['gunluk']); d, n = IN.son_durum(L)
        P = IN.plan(G)
        assert d['KO.A01|2014-01']['kod'] == 200 and n['KO.A01|2014-01'] == 2
        assert d['KO.B02|2014-01']['kod'] == 403 and n['KO.B02|2014-01'] == 1, '403 aşıldı ya da yeniden denendi'
        # 2 / 72 > %5 değil (2,8 %) → tur yok; sıfırlanan istek iki denemede bırakılır
        assert n['KO.A01|2014-02'] == 2 and d['KO.A01|2014-02']['kod'] not in IN.KESIN
        assert n['KO.B02|2014-02'] == 2
        assert d['KO.A01|2014-03']['kod'] == 204 and n['KO.A01|2014-03'] == 2
        assert all(r['ua'] == IN.UA and 'knotenlinie' not in r['ua'].lower() for r in srv.istekler)
        assert all(r['yontem'] == 'POST' for r in srv.istekler)
        t = [r['t'] for r in srv.istekler]
        assert all(b - a >= IN.ARA_SN - 1e-9 for a, b in zip(t, t[1:])), 'istekler arası < 2 sn'
        assert 7 in S.uykular or any(abs(u - 7) < 1e-6 for u in S.uykular), 'Retry-After beklenmedi'
        assert len(srv.istekler) == len(P) + 4, len(srv.istekler)
        g = srv.istekler[0]['govde'].splitlines()[0].split()
        assert g[0] == 'KO' and g[2] == '--' and g[3] == 'HH?' and g[4].endswith('T22:00:00'), g
        assert not [f for f in os.listdir(os.path.join(KAR, 's03_yerel')) if f.endswith('.mseed')], 'ham dosya silinmedi'
        ok = [x for x in d.values() if x['kod'] == 200]
        for x in ok:
            assert x['cif_sha256'] == IN.sha_dosya(os.path.join(depo, 'cif', x['cif']))
        # > %5 başarısızlıkta tek tur
        depo2 = temiz(os.path.join(KAR, 's03b')); S2 = saat_tak()
        dav2 = {f'KO.A01|2014-{m:02d}': [500, 500, 200] for m in range(1, 6)}
        srv2 = Sunucu('kisa', dav2, S2)
        try:
            for _ in range(5):
                B = IN.indir(None, depo2, os.path.join(KAR, 's03b_yerel'), 6000, taban=srv2.url, G=yapay_G(['KO.A01'], [2017]))
                if B['durum'] == 'bitti': break
            d2, n2 = IN.son_durum(IN.satirlar(IN.durum_yollari(depo2)['gunluk']))
            assert B['tur'] is True and all(n2[f'KO.A01|2014-{m:02d}'] == 3 and d2[f'KO.A01|2014-{m:02d}']['kod'] == 200 for m in range(1, 6))
        finally:
            srv2.kapat()
    finally:
        srv.kapat()


@sina('S04 sürdürme: süre sınırı, kaldığı yerden, çift kayıt yok')
def s04(KAR):
    depo = temiz(os.path.join(KAR, 's04')); S = saat_tak()
    srv = Sunucu('kisa', {}, S)
    try:
        G = yapay_G(['KO.A01'], [2017])
        G['hiz']['v_medyan_KiBs'] = 1.0e4                                 # küçük tahmin: her iş birkaç istek
        n_is = 0; onceki = 0
        while True:
            n_is += 1
            B = IN.indir(None, depo, os.path.join(KAR, 's04_yerel'), 90, taban=srv.url, G=G)
            k = len(IN.satirlar(IN.durum_yollari(depo)['gunluk']))
            assert k > onceki or B['durum'] == 'bitti', 'iş ilerlemedi'
            onceki = k
            if B['durum'] == 'bitti' or n_is > 60: break
        assert B['durum'] == 'bitti' and n_is > 2, n_is
        L = IN.satirlar(IN.durum_yollari(depo)['gunluk'])
        assert len(L) == len({x['k'] for x in L}) == 36, 'çift kayıt'
        assert len(B['isler']) == n_is - 0 and B['etkin_sn'] > 0
        # yarım satır: dosyayı yarım bir satırla bitir, sonraki iş bozulmasın
        with open(IN.durum_yollari(depo)['gunluk'], 'a') as f: f.write('{"k": "yarim')
        assert len(IN.satirlar(IN.durum_yollari(depo)['gunluk'])) == 36
        # süre kesmesi deneme sayılmaz
        d, n = IN.son_durum([dict(k='x', kod='URLError', sure_kesti=True), dict(k='x', kod='URLError', sure_kesti=True)])
        assert n['x'] == 0 and 'x' not in d
        # bitmiş indirme yeni istek atmaz
        nb = len(srv.istekler); IN.indir(None, depo, os.path.join(KAR, 's04_yerel'), 30, taban=srv.url, G=G)
        assert len(srv.istekler) == nb
    finally:
        srv.kapat()


@sina('S05 kesik koşu: bütçe (21 etkin / 42 takvim günü) ve tamamlanan T')
def s05(KAR):
    for tur in ('etkin', 'takvim'):
        depo = temiz(os.path.join(KAR, f's05_{tur}')); S = saat_tak()
        srv = Sunucu('kisa', {}, S)
        try:
            G = yapay_G(['KO.A01'], [2017, 2020])
            B0 = IN.butce_oku(depo)
            if tur == 'etkin': B0.update(ilk_istek=S.t - 10 * 86400, etkin_sn=21 * 86400 - 50)
            else: B0.update(ilk_istek=S.t - 42 * 86400 + 30, etkin_sn=86400)
            os.makedirs(depo, exist_ok=True); IN.yaz_json(IN.durum_yollari(depo)['butce'], B0)
            B = IN.indir(None, depo, os.path.join(KAR, 's05_yerel'), 6000, taban=srv.url, G=G)
            assert B['durum'] == 'kesildi', B
            n1 = len(srv.istekler); assert 0 < n1 < 72, n1
            B = IN.indir(None, depo, os.path.join(KAR, 's05_yerel'), 6000, taban=srv.url, G=G)
            assert B['durum'] == 'kesildi' and len(srv.istekler) == n1, '"kesildi" kalıcı değil'
        finally:
            srv.kapat()
    # sınırın hemen altında kesilmez
    S = saat_tak(); B0 = dict(durum='suruyor', ilk_istek=S.t - 42 * 86400 + 5000, etkin_sn=21 * 86400 - 5000, isler=[], tur=False)
    assert IN.butce_asildi(B0, S.t) is None
    # kosu: kesik koşuda "veri yok (indirme bütçesi)" ve kesin kod kuralı
    depo = temiz(os.path.join(KAR, 's05_kosu')); S = saat_tak()
    G = yapay_csv(yapay_G([f'KO.S{i:02d}' for i in range(11)], [2017, 2020]), depo)
    satir = []
    for x in IN.plan(G):
        if x['ay'] <= '2016-12': satir.append(dict(k=x['k'], kod=200 if x['ay'] != '2015-06' or x['ist'] != 'KO.S03' else 'URLError'))
    satir.append(dict(k='KO.S03|2015-06', kod='URLError'))
    with open(IN.durum_yollari(depo)['gunluk'], 'w') as f:
        for r in satir: f.write(json.dumps(r) + '\n')
    IN.yaz_json(IN.durum_yollari(depo)['butce'], dict(durum='kesildi', ilk_istek=S.t - 42 * 86400, etkin_sn=5 * 86400, bitis=S.t, isler=[], tur=False))
    yedek = (K.b1_hesapla, K.denetim_i, K.hepsini_hesapla, K.bilgi_satirlari)
    K.b1_hesapla = lambda W, *a: {w['k']: dict(dolu=True) for w in W}
    K.denetim_i = lambda *a: dict(sapan=0)
    K.hepsini_hesapla = lambda W, *a: {w['k']: dict(delta=0.001 * (i % 5 - 2), delta_ekli=0.001 * (i % 5 - 2) - 0.00095) for i, w in enumerate(W)}
    K.bilgi_satirlari = lambda *a: {'11': dict(yer_medyani=None), '14': dict(ortalama=None)}
    try:
        H = K.olc(None, depo, None, G=G)
        assert H['hukum'] == 'veri yok (indirme bütçesi)', H['hukum']
        assert 'tamamlanan T: yok' in H['metin'], H['metin']                 # S03'ün 2015-06 isteği kesin değil → T 2017 eksik
        assert 'etkin süre 5,00 gün, takvim 42,00 gün' in H['metin'], H['metin']
        assert 'bilgi satırı 0: hesaplanmadı (n = 0, yer = 0)' in H['metin']
    finally:
        K.b1_hesapla, K.denetim_i, K.hepsini_hesapla, K.bilgi_satirlari = yedek


@sina('S06 ε yasağı: indirme bitmeden ölçü yok')
def s06(KAR):
    depo = temiz(os.path.join(KAR, 's06'))
    G = yapay_G(['KO.A01'], [2017])
    for dur in ('baslamadi', 'suruyor'):
        if dur == 'suruyor': IN.yaz_json(IN.durum_yollari(depo)['butce'], dict(durum='suruyor', ilk_istek=1.0, etkin_sn=1.0, isler=[], tur=False))
        try: K.olc(None, depo, None, G=G); raise AssertionError('ölçü koştu')
        except SystemExit as e: assert 'hiçbir ε ya da Δ' in str(e), e
    assert not os.path.exists(os.path.join(depo, 'kosu', 'olcum_delta.json'))
    src = open(os.path.join(KOD, 'tr4_indir.py'), encoding='utf-8').read()
    assert 'germe_olc' not in src and 'ay_esle' not in src and 'tr5b_yapay' not in src, 'indirme modülü zincir içeriyor'


def bagimsiz_cif(xs, fs):
    """Bağımsız yazım: ön işlem (ortalama + eğilim, %5 Hann her uçta, FFT indirgeme 20 sn^-1, beyazlatma 0,5–2 Hz),
    sonra doğrudan zaman alanı toplamıyla birkaç gecikmede ÇİF."""
    out = []
    for x in xs:
        n0 = len(x); t = np.arange(n0)
        A = np.vstack([t, np.ones(n0)]).T; c = np.linalg.lstsq(A, x, rcond=None)[0]; y = x - A @ c
        k = int(round(0.05 * n0)); w = np.hanning(2 * k + 1)[:k] if False else 0.5 * (1 - np.cos(np.pi * np.arange(k) / k))
        y[:k] *= w; y[n0 - k:] *= w[::-1]
        X = np.fft.rfft(y); f = np.fft.rfftfreq(n0, 1 / fs); n = int(3600 * 20)
        H = np.where(f <= 7.5, 1.0, np.where(f >= 8.0, 0.0, 0.5 * (1 + np.cos(np.pi * (f - 7.5) / 0.5))))
        Y = (X * H)[:n // 2 + 1] * (n / n0)
        g = np.fft.rfftfreq(n, 1 / 20.0)
        W = np.where((g >= 0.5) & (g <= 2.0), 1.0, 0.0)
        m = (g >= 0.4) & (g < 0.5); W[m] = 0.5 * (1 - np.cos(np.pi * (g[m] - 0.4) / 0.1))
        m = (g > 2.0) & (g <= 2.1); W[m] = 0.5 * (1 + np.cos(np.pi * (g[m] - 2.0) / 0.1))
        out.append(np.fft.irfft(np.exp(1j * np.angle(Y)) * W, n))
    return out


def dogrudan(a, b, lag):
    n = len(a)
    s = np.dot(a[:n - lag], b[lag:]) if lag >= 0 else np.dot(a[-lag:], b[:n + lag])
    return s / math.sqrt(np.dot(a, a) * np.dot(b, b))


@sina('S07 saatlik ön işlem ve ÇİF: boşluk, kural, gecikme, miniSEED yolu')
def s07(KAR):
    fs = 100.0; n0 = int(3600 * fs); rng = np.random.default_rng(7)
    iz = yapay_iz(0, n0, fs, rng, gecikme_sn=2.0)
    xs = [iz[c].astype(float) for c in 'ZNE']
    Ys = [IN.saat_onisle(x, fs)[0] for x in xs]
    C = IN.cif3([IN.beyazlat(Y, 'b052') for Y in Ys])
    B = bagimsiz_cif(xs, fs)
    for j, (a, b) in enumerate(IN.CIFTLER):
        for lag in (-37, 0, 5, 40, 1200):
            assert abs(C[j, IN.NLAG + lag] - dogrudan(B[a], B[b], lag)) < 1e-6, (IN.CIFT_AD[j], lag)
    assert IN.CIFT_AD == ('ZE', 'ZN', 'EN')
    # bilinen gecikme: E(t) = Z(t − 2 sn) → ZE ÇİF'inin tepesi τ = +2 sn
    assert int(np.argmax(C[0])) - IN.NLAG == 40, int(np.argmax(C[0])) - IN.NLAG
    # boşluk kuralı: ≤ 1 sn aradeğer, > 1 sn sıfır
    x = xs[0].copy(); x[1000:1080] = np.nan
    y = xs[0].copy(); y[1000:1080] = np.interp(np.arange(1000, 1080), [999, 1080], [y[999], y[1080]])
    assert np.allclose(IN.saat_onisle(x, fs)[0], IN.saat_onisle(y, fs)[0], atol=1e-6)
    x = xs[0].copy(); x[5000:5200] = np.nan
    i = np.arange(n0); ok = ~np.isnan(x); p = np.polyfit(i[ok], x[ok], 1)
    z = np.where(ok, x - np.polyval(p, i), 0.0)
    Yz = IN.saat_onisle(np.where(ok, x, np.polyval(p, i)), fs)[0]
    assert np.allclose(IN.saat_onisle(x, fs)[0], Yz, atol=1e-6), '> 1 sn boşluk sıfır sayılmadı'
    # RMS: 0,5–2 Hz bant RMS'i (Parseval) — bağımsız: bant geçiren zaman dizisinin RMS'i
    Y0, r = IN.saat_onisle(xs[0], fs)
    M = IN.RMS_MASKE; yb = np.fft.irfft(np.where(M, Y0, 0), IN.N20)
    assert abs(r - math.sqrt(np.mean(yb ** 2))) / r < 1e-3, (r, math.sqrt(np.mean(yb ** 2)))
    # miniSEED yolu: sahte sunucunun tam verisi → isle_istasyon_ay, aynı saatin doğrudan hesabıyla
    satir = [['KO', 'A01', '--', 'HH?', '2014-01-01T22:00:00', '2014-01-02T02:00:00']]
    ham = os.path.join(KAR, 's07.mseed'); open(ham, 'wb').write(mseed_uret(satir, 'tam'))
    x = dict(ist='KO.A01', ay='2014-01', rol='ana', loc='', bant='HH', yatay=['N', 'E'], gunler=['2014-01-02'])
    r = IN.isle_istasyon_ay(ham, x, {'KO.A01': (40.9, 29.0)})
    assert r['ccf'].shape == (1, 4, 3, 2401) and np.all(r['tamlik'] == 1.0)
    from obspy import UTCDateTime
    rng = np.random.default_rng(int(UTCDateTime('2014-01-01T22:00:00').timestamp) % 2 ** 31)
    iz = yapay_iz(0, int(4 * 3600 * fs), fs, rng)
    xh = [np.round(iz[c][3600 * 100:7200 * 100]).astype(float) for c in 'ZNE']    # 2. saat
    C2 = IN.cif3([IN.beyazlat(IN.saat_onisle(v, fs)[0], 'b052') for v in xh])
    assert np.allclose(r['ccf'][0, 1], C2, atol=1e-6)
    os.remove(ham)


@sina('S08 enerji reddi ve günlük ÇİF (≥ 2 saat, maske)')
def s08(KAR):
    nl = 2401; d0 = dt.date(2015, 3, 1); V = {}
    rng = np.random.default_rng(8)
    for i in range(10):
        c = rng.standard_normal((4, 3, nl)).astype(np.float32); rms = np.ones((4, 3), np.float32)
        V[(d0 + TD(days=i)).toordinal()] = (c, rms, np.ones((4, 3), np.float32))
    o = (d0 + TD(days=2)).toordinal(); V[o][1][1, 0] = 3.5           # 1 saat > 3 × medyan → atılır
    o3 = (d0 + TD(days=3)).toordinal(); V[o3][1][:3, 2] = 3.5          # 3 saat atılır → 1 saat kalır → gün geçersiz
    o4 = (d0 + TD(days=4)).toordinal(); V[o4][1][0, 1] = 2.9          # eşiğin altı
    o5 = (d0 + TD(days=5)).toordinal(); V[o5][0][2:, 0] = np.nan       # 2 saat tamlıkta düşer (2 kalır: geçerli)
    gl = [d0 + TD(days=i) for i in range(10)]
    ccf, gec, red = K.gunluk_cif(V, gl, {d0 + TD(days=7)}, (d0, d0 + TD(days=9)))
    a = V[o][0].astype(float)
    assert np.allclose(ccf[0, 2], a[[0, 2, 3], 0].mean(0)) and gec[0, 2]
    assert not gec[:, 3].any(), '1 saatlik gün geçerli sayıldı'
    assert np.allclose(ccf[1, 4], V[o4][0][:, 1].astype(float).mean(0))
    assert gec[:, 5].all() and np.allclose(ccf[2, 5], V[o5][0][:2, 2].astype(float).mean(0))
    assert not gec[:, 7].any(), 'maskeli gün geçerli'
    assert abs(red - 4 / 38) < 1e-9, red


@sina('S09 TR-5b başvurusuyla eşdeğerlik (dondurulmuş npz → saatlik → koşu yolu)')
def s09(KAR, npz):
    r5 = json.load(open(K.YOL['tr5b_yapay_ccf_ref.json'], encoding='utf-8'))
    r4 = json.load(open(K.YOL['tr4_yapay_ref.json'], encoding='utf-8'))['tasarim']['C_20g_4s']['seriler']
    z = np.load(npz); gun = z['gunler'].astype(int); rng = np.random.default_rng(9)
    for i in (0, 23, 47):
        s = r5['seriler'][i]; T = dt.date.fromordinal(s['T_ord'])
        for kademe, ref in (('A', s), ('C', r4[i])):
            V = {}; Ve = {}
            for j, g in enumerate(gun):
                d = T + TD(days=int(g))
                if not z['gecerli'][i][j] or (kademe == 'C' and d.day > 20): continue
                for VV, kaynak in ((V, z['ccf']), (Ve, z['ccf_eklenmis'])):
                    a = kaynak[i][j].astype(np.float64)
                    e = rng.standard_normal((4, 2401)) * 1e-3; e -= e.mean(0)          # saatlerin ortalaması = günlük ÇİF
                    h = (a[None] + e)
                    VV[d.toordinal()] = (np.repeat(h[:, None, :], 3, axis=1).astype(np.float64), np.ones((4, 3)), np.ones((4, 3)))
            w = dict(k='x', T=T, a=T - TD(days=1095), b=T - TD(days=8))
            r = K.pencere_hesapla(w, V, set(), kademe, ekli=False)
            re_ = K.pencere_hesapla(w, Ve, set(), kademe, ekli=False)
            D0, D2 = r['delta'], re_['delta']
            if ref['delta_yuzde'] is None: assert np.isnan(D0); continue
            assert abs(D0 * 100 - ref['delta_yuzde']) <= K.TOL_DELTA, (i, kademe, D0 * 100, ref['delta_yuzde'])
            assert abs((D2 - D0) / -1e-3 - ref['oran']) <= K.TOL_ORAN, (i, kademe)
    # (ii-a) ekleme yolu: koşu kodunun germe eklemesi tr5b_yapay.ger ile aynı
    a = z['ccf'][0].astype(np.float64); gg = gun
    E = K.ekle(a, gg)
    assert np.allclose(E[gg >= -365], np.stack([K.YP.ger(x, -1e-3) for x in a[gg >= -365]])) and np.array_equal(E[gg < -365], a[gg < -365])


@sina('S10 önyükleme, kestiriciler ve (c) eşikleri')
def s10(KAR):
    rng = np.random.default_rng(10)
    rows = [(f'Y{i}', y, rng.standard_normal() * 0.0012) for i in range(14) for y in (2017, 2018, 2020, 2021)]
    t = K.taban(rows)
    v = np.array([r[2] for r in rows]) * 100
    assert abs(t['sigma'] - 1.4826 * np.median(np.abs(v - np.median(v)))) < 1e-12
    assert abs(t['q95'] - np.quantile(np.abs(v), 0.95)) < 1e-12
    # bağımsız iki yönlü önyükleme
    r2 = np.random.default_rng(int(hashlib.sha256(b'tr4-hukum|20261202').hexdigest()[:8], 16))
    S = sorted({r[0] for r in rows}); Y = sorted({r[1] for r in rows})
    ms = r2.multinomial(len(S), [1 / len(S)] * len(S), size=2000); my = r2.multinomial(len(Y), [1 / len(Y)] * len(Y), size=2000)
    sg, qq = [], []
    for b in range(2000):
        x = []
        for (s, y, d) in rows: x += [d * 100] * int(ms[b, S.index(s)] * my[b, Y.index(y)])
        if len(x) >= 5:
            x = np.array(x); sg.append(1.4826 * np.median(np.abs(x - np.median(x)))); qq.append(np.quantile(np.abs(x), 0.95))
    assert np.allclose([t['sigma_L'], t['sigma_U']], np.quantile(sg, [0.05, 0.95]))
    assert np.allclose([t['q95_L'], t['q95_U']], np.quantile(qq, [0.025, 0.975]))
    assert K.tohum('tr4-hukum|20261202') == int(hashlib.sha256(b'tr4-hukum|20261202').hexdigest()[:8], 16)
    f = lambda L, U: K.c_hukmu(dict(sigma_L=L, sigma_U=U))
    assert f(0.05, 0.1999) == 'taban ölçüldü; TR-5b (c) karşılandı'
    assert f(0.05, 0.20) == 'taban ölçüldü; TR-5b (c) belirsiz'
    assert f(0.2451, 0.4) == 'taban ölçüldü; TR-5b (c) karşılanmadı'
    assert f(0.245, 0.4) == 'taban ölçüldü; TR-5b (c) belirsiz'
    assert f(0.21, 0.30) == 'taban ölçüldü; TR-5b (c) belirsiz'
    assert K.kapi({2017: 10, 2020: 10}) and not K.kapi({2017: 10, 2019: 10}) and not K.kapi({2017: 9, 2020: 30})


KALIP_T = ("Marmara KO ağında [kademe], [n] yer-penceresinde ([yer] yer, T [ilk]–[son]), olaysız pencerelerde tek "
           "istasyonun bir yıllık dv/v düzey değişiminin (0,5–2 Hz, TR-5b ölçüsü) örneklem %95 niceliği q95 = [..] %'dir (%95 iki "
           "yönlü önyükleme aralığı [L–U]; benzetimde bu aralık gerçek değeri 0,79–0,97 olasılıkla kapsar). σ̂_Δ = [..] % (%90 iki "
           "yönlü önyükleme aralığı [L–U]). q95, tek istasyonda %5 yanlış alarm oranındaki saptama eşiğidir. Bu büyüklükte bir "
           "düzey değişimi yaklaşık yarı yarıya saptanır. %80 olasılıkla saptanacak değişim, normal yaklaşımla, ≈ q95 + 0,84 · "
           "σ̂_Δ = [..] %'dir. Bu bir olasılık ya da alarm eşiği değildir. Ölçü istasyon çevresindeki sığ ortamı örnekler. Zincir "
           "bu ön kayıtta Marmara'da gerçek bir hız değişimiyle sınanmadı; mevsimsel genliğin yer medyanı (bilgi satırı 11) "
           "[..] %, 2019 Silivri δ_ko'su (bilgi satırı 14) [..].")


def kalip_esle(metin, kalip):
    import re
    p = re.escape(kalip)
    for ph in (r'\[kademe\]', r'\[n\]', r'\[yer\]', r'\[ilk\]', r'\[son\]', r'\[\.\.\]', r'\[L–U\]'):
        p = p.replace(re.escape(ph.replace('\\', '')), '(.+?)')
    return re.fullmatch(p, metin) is not None


def kosu_stub(dav):
    """Hızlı hüküm dalları: 1b, denetim (i), Δ hesabı ve bilgi satırları sahte işlevlerle."""
    yedek = (K.b1_hesapla, K.denetim_i, K.hepsini_hesapla, K.bilgi_satirlari)
    K.b1_hesapla = lambda W, *a: {w['k']: dict(dolu=dav.get('dolu', lambda w: True)(w)) for w in W}
    K.denetim_i = lambda *a: dict(sapan=dav.get('sapan', 0))
    def hh(W, *a):
        out = {}
        for i, w in enumerate(W):
            d = dav['delta'](i, w); e = d + dav.get('oran', 0.95) * -1e-3 if not np.isnan(d) else float('nan')
            out[w['k']] = dict(delta=d, delta_ekli=e)
        return out
    K.hepsini_hesapla = hh
    K.bilgi_satirlari = lambda *a: {'11': dict(yer_medyani=0.12), '14': dict(ortalama=-0.03)}
    return yedek


@sina('S11 hüküm kalıbının her dalı ve kalıp metinleri')
def s11(KAR):
    ist = [f'KO.S{i:02d}' for i in range(12)]
    def kos(ad, dav, Tler=(2017, 2020, 2021), butce='bitti'):
        depo = temiz(os.path.join(KAR, 's11_' + ad))
        G = yapay_csv(yapay_G(ist, list(Tler)), depo)
        IN.yaz_json(IN.durum_yollari(depo)['butce'], dict(durum=butce, ilk_istek=1.0, etkin_sn=1.0, isler=[], tur=False))
        with open(IN.durum_yollari(depo)['gunluk'], 'w') as f:
            for x in IN.plan(G): f.write(json.dumps(dict(k=x['k'], kod=200)) + '\n')
        y = kosu_stub(dav)
        try: return K.olc(None, depo, None, G=G)
        finally: K.b1_hesapla, K.denetim_i, K.hepsini_hesapla, K.bilgi_satirlari = y
    r = np.random.default_rng(11); Z = r.standard_normal(200)
    gor = set()
    H = kos('karsilandi', dict(delta=lambda i, w: Z[i] * 0.0005))
    assert H['hukum'] == 'taban ölçüldü; TR-5b (c) karşılandı', H['hukum']; gor.add(H['hukum'])
    m = H['metin'].split('. ', 1)[1]
    assert kalip_esle(m, KALIP_T), m
    assert 'kademe C, 36 yer-penceresinde (12 yer, T 2017–2021)' in m and "0,120 %, 2019 Silivri δ_ko'su (bilgi satırı 14) −0,030 % (istasyon ortalaması)." in m
    H = kos('karsilanmadi', dict(delta=lambda i, w: Z[i] * 0.012)); gor.add(H['hukum'])
    assert H['hukum'] == 'taban ölçüldü; TR-5b (c) karşılanmadı', H['hukum']
    H = kos('belirsiz', dict(delta=lambda i, w: Z[i] * 0.0020)); gor.add(H['hukum'])
    assert H['hukum'] == 'taban ölçüldü; TR-5b (c) belirsiz', H['hukum']
    H = kos('kod_i', dict(delta=lambda i, w: 0.0, sapan=2)); gor.add(H['hukum'])
    assert H['metin'] == 'geçersiz (kod). sapan dizi sayısı 2', H['metin']
    H = kos('kod_iia', dict(delta=lambda i, w: Z[i] * 0.0005, oran=0.75)); gor.add(H['hukum'])
    assert H['metin'] == 'geçersiz (kod). medyan oran 0,750', H['metin']
    assert 'taban' not in H and 'bilgi' not in H, 'geçersizde Δ sayısı yazıldı'
    H = kos('gun', dict(delta=lambda i, w: Z[i] * 0.0005, dolu=lambda w: w['ist'] != 'KO.S11'), Tler=(2017, 2018, 2019)); gor.add(H['hukum'])
    assert H['hukum'] == 'veri yok (gün doluluğu)'
    assert H['metin'].startswith('veri yok (gün doluluğu). T başına dolu yer: 2017: 11, 2018: 11, 2019: 11, 2020: 0, 2021: 0, 2022: 0, 2023: 0, 2024: 0; bilgi satırı 0: σ̂_Δ '), H['metin']
    assert H['metin'].endswith(', n 33, yer 11, T 2017, 2018, 2019'), H['metin']
    assert H['bilgi_0']['ek'] == 'Kapı altı; TR-5b (c) için dayanak değildir; hüküm veri yok (gün doluluğu).'
    H = kos('eps', dict(delta=lambda i, w: Z[i] * 0.0005 if w['T'].year != 2017 else float('nan'))); gor.add(H['hukum'])
    assert H['metin'].startswith('veri yok (ε geçerliliği). T başına geçerli yer: 2017: 0, 2018: 0, 2019: 0, 2020: 12, 2021: 12'), H['metin']
    # bilgi satırı 0 "hesaplanmadı" biçimi (n < 30)
    H = kos('eps2', dict(delta=lambda i, w: Z[i] * 0.0005 if (w['T'].year == 2020 and w['ist'] < 'KO.S05') else float('nan')))
    assert H['metin'].endswith('bilgi satırı 0: hesaplanmadı (n = 5, yer = 5)'), H['metin']
    G = yapay_G(ist, [2017]); G['kademe'] = 'veri yok (aktarım hızı)'
    depo = temiz(os.path.join(KAR, 's11_hiz')); H = K.olc(None, depo, None, G=G); gor.add(H['hukum'])
    assert H['metin'] == ('veri yok (aktarım hızı). aşama H hızları 20,0, 25,0, 22,0 KiB/s; medyan 22,0; V_D / v = 81,0 gün; '
                          'bilgi satırı 0: hesaplanmadı (indirme yok)'), H['metin']
    G = yapay_G(ist, [2017]); G['S0']['hukum'] = 'veri yok (aşama 0)'
    G['S0']['yer_T'] = {str(y): 3 for y in range(2017, 2025)}
    depo = temiz(os.path.join(KAR, 's11_a0')); H = K.olc(None, depo, None, G=G); gor.add(H['hukum'])
    assert H['metin'].startswith('veri yok (aşama 0). T başına dolu yer: 2017: 3,')
    # kesik ve ölçüldü: kademe metni
    depo = temiz(os.path.join(KAR, 's11_kesik'))
    G = yapay_csv(yapay_G(ist, [2017, 2020, 2021, 2022]), depo)
    IN.yaz_json(IN.durum_yollari(depo)['butce'], dict(durum='kesildi', ilk_istek=1.0, bitis=86400 * 42 + 1, etkin_sn=86400 * 21, isler=[], tur=False))
    with open(IN.durum_yollari(depo)['gunluk'], 'w') as f:
        for x in IN.plan(G):
            if x['ay'] <= '2020-12': f.write(json.dumps(dict(k=x['k'], kod=200 if x['ay'] != '2019-03' else 404)) + '\n')
    y = kosu_stub(dict(delta=lambda i, w: Z[i] * 0.0005))
    try: H = K.olc(None, depo, None, G=G)
    finally: K.b1_hesapla, K.denetim_i, K.hepsini_hesapla, K.bilgi_satirlari = y
    assert 'Marmara KO ağında kademe C, kesik, T 2017–2021, 36 yer-penceresinde' in H['metin'], H['metin']
    gor.add('veri yok (indirme bütçesi)')                             # S05'te uçtan uca
    assert gor == set(K.HUKUM_ADLARI), set(K.HUKUM_ADLARI) - gor
    for metin in ('İstanbul', 'olasılığı %'):
        assert metin not in open(os.path.join(KOD, 'tr4_kosu.py'), encoding='utf-8').read() or metin == 'olasılığı %'


@sina('S12 tek koşu: hukum.json değiştirilemez')
def s12(KAR):
    depo = temiz(os.path.join(KAR, 's12')); os.makedirs(os.path.join(depo, 'kosu'))
    K.hukum_yaz(depo, dict(hukum='veri yok (gün doluluğu)', metin='a'))
    K.hukum_yaz(depo, dict(hukum='veri yok (gün doluluğu)', metin='a'))
    try: K.hukum_yaz(depo, dict(hukum='taban ölçüldü; TR-5b (c) karşılandı', metin='b')); raise AssertionError('üzerine yazıldı')
    except SystemExit: pass
    try: K.hukum_yaz(depo, dict(hukum='başka bir hüküm', metin='b')); raise AssertionError('kapalı liste dışı')
    except AssertionError as e:
        if 'yazıldı' in str(e) or 'kapalı' in str(e): raise


def yapay_depo(depo, G, kademe='C', seed=1, eksik=0.15, delik=None):
    """Yapay saatlik ÇİF deposu: istasyon başına bir G(τ) (tr5b_yapay.seri gibi), günlük ε = %0,05 mevsim, saatlik
    gürültü. Gün indirme günlüğü satırlarıyla birlikte."""
    YP = K.YP; rng = np.random.default_rng(seed)
    P = IN.plan(G); os.makedirs(os.path.join(depo, 'cif'), exist_ok=True)
    Gs = {}
    with open(IN.durum_yollari(depo)['gunluk'], 'w') as g:
        for x in P:
            s = x['ist']
            if s not in Gs:
                z = np.exp(-np.abs(YP.tau) / 20.0); G0 = YP.bant_gurultu(rng, 1)[0] * z; Gs[s] = (G0 / np.sqrt(np.mean(G0[YP.koda] ** 2)), rng.uniform(0, 6.28))
            G0, faz = Gs[s]; gl = [dt.date.fromisoformat(d) for d in x['gunler']]; nd = len(gl)
            ccf = np.full((nd, 4, 3, 2401), np.nan, np.float32); tam = np.ones((nd, 4, 3), np.float32); rms = np.ones((nd, 4, 3), np.float32)
            for i, d in enumerate(gl):
                if rng.random() < eksik or (delik and delik(s, d)): tam[i] = 0.5; continue
                e = 5e-4 * math.sin(2 * math.pi * d.toordinal() / 365.25 + faz)
                base = YP.ger(G0, e)
                ccf[i] = (base[None, None, :] + YP.bant_gurultu(rng, 12).reshape(4, 3, -1) * (0.98 / math.sqrt(10)) ** -1 * 0.5).astype(np.float32)
            d = dict(gun=np.array([q.toordinal() for q in gl], np.int32), ccf=ccf, ccf24=ccf, rms=rms, tamlik=tam,
                     meta=dict(ist=s, ay=x['ay'], rol=x['rol']))
            yol, sh = IN.cif_yaz(depo, x, d)
            g.write(json.dumps(dict(k=x['k'], kod=200, cif=os.path.basename(yol), cif_sha256=sh, rol=x['rol'])) + '\n')


@sina('S13 1b gün doluluğu')
def s13(KAR):
    depo = temiz(os.path.join(KAR, 's13'))
    G = yapay_csv(yapay_G(['KO.A01', 'KO.B02'], [2017]), depo)
    yapay_depo(depo, G, eksik=0.0, delik=lambda s, d: s == 'KO.B02' and d.year == 2016 and d.day <= 9)
    satir, _ = IN.son_durum(IN.satirlar(IN.durum_yollari(depo)['gunluk']))
    b = K.b1_hesapla(G['W'], depo, satir, {w['k']: set() for w in G['W']}, 'C')
    a, bb = b['KO.A01|2017-01-01'], b['KO.B02|2017-01-01']
    assert a['dolu'] and a['oran'] == [1.0, 1.0, 1.0] and a['yigin_ay'] == 12, a
    assert not bb['dolu'] and 0.5 < bb['oran'][2] < 0.6 and bb['yigin_ay'] >= 9, bb
    assert K.gun_dolu(np.array([[1, 1, 1], [1, 1, .99], [0.98, 1, 1], [0, 0, 0]])) and not K.gun_dolu(np.array([[1, 1, 1], [1, 1, .98], [1, 1, 1.0], [0, 0, 0]]) * np.array([1, 1, 0, 0])[:, None])


@sina('S14 uçtan uca ölçü: yapay depo → taban ölçüldü')
def s14(KAR, npz):
    depo = temiz(os.path.join(KAR, 's14'))
    ist = [f'KO.E{i:02d}' for i in range(10)]
    G = yapay_csv(yapay_G(ist, [2017, 2020]), depo)
    t0 = time.time(); yapay_depo(depo, G, eksik=0.10); print(f'  yapay depo {time.time() - t0:.0f} sn', flush=True)
    IN.yaz_json(IN.durum_yollari(depo)['butce'], dict(durum='bitti', ilk_istek=1.0, etkin_sn=1.0, isler=[], tur=False))
    H = K.olc(None, depo, npz, G=G)
    assert H['hukum'] == 'taban ölçüldü; TR-5b (c) karşılandı', H['metin']
    st = json.load(open(os.path.join(depo, 'kosu', 'kosu_durum.json'), encoding='utf-8'))['asamalar']
    assert st['2_denetim_i']['sapan'] == 0 and 0.8 <= st['3_denetim_iia']['medyan_oran'] <= 1.2, st['3_denetim_iia']
    assert st['olcum_dosyasi']['sha256'] == IN.sha_dosya(os.path.join(depo, 'kosu', 'olcum_delta.json'))
    assert H['taban']['n'] == 20 and H['taban']['sigma'] < 0.05, H['taban']
    assert set(H['bilgi']) >= {str(i) for i in range(1, 15)}, sorted(H['bilgi'])
    print('  ', H['metin'][:300], flush=True)
    shutil.rmtree(os.path.join(depo, 'cif'), ignore_errors=True)


HIZLI = [s01, s02, s03, s04, s05, s06, s07, s08, s10, s11, s12, s13]

# ---------------------------------------------------------------- mutasyonlar
MUT = [
    ('M01 KESIN kümesine 500', 'tr4_indir.py', 'KESIN = (200, 204, 404, 401, 403)', 'KESIN = (200, 204, 404, 401, 403, 500)'),
    ('M02 körlük denetimi çağrılmaz', 'tr4_indir.py', "kor_denet(son_utc, son_gun, x['rol'])  ", "(son_utc, son_gun, x['rol'])  "),
    ('M03 kademe C 1–21. günler', 'tr4_indir.py', 'C_GUN = 20 ', 'C_GUN = 21 '),
    ('M04 karşılanmadı eşiği 0,20', 'tr4_kosu.py', 'ESIK_KARSILANDI, ESIK_KARSILANMADI = 0.20, 0.245', 'ESIK_KARSILANDI, ESIK_KARSILANMADI = 0.20, 0.20'),
    ('M05 σ aralığı %10–90', 'tr4_kosu.py', 'np.nanquantile(sig, [0.05, 0.95])', 'np.nanquantile(sig, [0.10, 0.90])'),
    ('M06 enerji eşiği 3 → 4', 'tr4_kosu.py', 'ENERJI_KAT = 3.0', 'ENERJI_KAT = 4.0'),
    ('M07 takvim bütçesi 43 gün', 'tr4_indir.py', 'BUTCE_TAKVIM_SN = 42 * 86400.0', 'BUTCE_TAKVIM_SN = 43 * 86400.0'),
    ('M08 ε yasağı yok', 'tr4_kosu.py', "if B['durum'] not in ('bitti', 'kesildi'):", "if False:"),
    ('M09 günlük ÇİF ≥ 1 saat', 'tr4_kosu.py', 'SAAT_MIN = 2 ', 'SAAT_MIN = 1 '),
    ('M10 ÇİF yönü ters', 'tr4_indir.py', 'c = np.fft.irfft(np.conj(F[a]) * F[b], 2 * N20)', 'c = np.fft.irfft(F[a] * np.conj(F[b]), 2 * N20)'),
    ('M11 deneme sınırı 3', 'tr4_indir.py', 'DENEME_MAX = 2 ', 'DENEME_MAX = 3 '),
    ('M12 kapı arası 2 yıl', 'tr4_kosu.py', 'KAPI_YER, KAPI_ARA = 10, 3', 'KAPI_YER, KAPI_ARA = 10, 2'),
    ('M13 süre kesmesi deneme sayılır', 'tr4_indir.py', "        if x.get('sure_kesti'): continue\n", ''),
    ('M14 istekler arası 1 sn', 'tr4_indir.py', 'ARA_SN = 2.0 ', 'ARA_SN = 1.0 '),
    ('M15 boşluk aradeğeri 2 sn', 'tr4_indir.py', 'BOSLUK_ARADEGER_SN = 1.0', 'BOSLUK_ARADEGER_SN = 2.0'),
    ('M16 kesik koşuda kesin kod şartı yok', 'tr4_kosu.py', "all(k in satir and satir[k]['kod'] in IN.KESIN for k in", "all(k in satir for k in"),
    ('M17 1b dilim oranı 0,50', 'tr4_kosu.py', 'DOLU_DILIM_ORAN = 0.60', 'DOLU_DILIM_ORAN = 0.50'),
    ('M18 tek koşu koruması yok', 'tr4_kosu.py', "        if eski['hukum'] != H['hukum'] or eski['metin'] != H['metin']:\n            raise SystemExit", "        if False:\n            raise SystemExit"),
]


def mutasyon(KAR, npz):
    sonuc = []
    for ad, dosya, eski, yeni in MUT:
        md = temiz(os.path.join(KAR, 'mut', ad.split()[0]))
        tr4 = os.path.join(md, 'tr4'); tr5 = os.path.join(md, 'tr5'); os.makedirs(tr4); os.makedirs(tr5)
        for f in ('tr4_indir.py', 'tr4_kosu.py', 'tr4_test_yapay.py', 'tr4_yapay_ref.json', 'tr4_pencereler.csv',
                  'tr4_onkayit_sayim.json', 'tr4_guc_sonuc.json'):
            shutil.copy(os.path.join(KOD, f), tr4)
        for f in ('tr5b_yapay.py', 'tr5b_yapay2.py', 'tr5b_yapay_ccf_ref.json'):
            shutil.copy(os.path.join(os.path.dirname(KOD), 'tr5', f), tr5)
        y = os.path.join(tr4, dosya); s = open(y, encoding='utf-8').read()
        assert s.count(eski) == 1, (ad, s.count(eski)); open(y, 'w', encoding='utf-8').write(s.replace(eski, yeni))
        p = subprocess.run([sys.executable, '-I', '-B', os.path.join(tr4, 'tr4_test_yapay.py'), os.path.join(md, 'k'), npz,
                            '--hizli', '--kod', tr4], capture_output=True, text=True, timeout=1800,
                           env=dict(os.environ, OMP_NUM_THREADS='1'))
        kal = [l for l in p.stdout.splitlines() if l.startswith('KALDI')]
        yak = p.returncode != 0 and bool(kal)
        sonuc.append((ad, yak, kal[:2]))
        print(f"{'YAKALANDI' if yak else 'KAÇTI    '} {ad}: {len(kal)} sınama kaldı {kal[:1]}", flush=True)
        shutil.rmtree(md, ignore_errors=True)
    return sonuc


if __name__ == '__main__':
    a = [x for i, x in enumerate(sys.argv[1:], 1) if not x.startswith('--') and sys.argv[i - 1] != '--kod']
    KAR, npz = a[0], a[1]
    os.makedirs(KAR, exist_ok=True)
    t0 = time.time()
    for f in HIZLI: f(KAR)
    if '--hizli' not in sys.argv:
        s09(KAR, npz); s14(KAR, npz)
    n_ok = sum(1 for x in SONUC if x[1])
    print(f'SINAMA: {n_ok} / {len(SONUC)} geçti ({time.time() - t0:.0f} sn)', flush=True)
    rapor = dict(sinama=[dict(ad=x[0], gecti=x[1], hata=x[2]) for x in SONUC])
    if '--mutasyon' in sys.argv:
        M = mutasyon(KAR, npz)
        rapor['mutasyon'] = [dict(ad=m[0], yakalandi=m[1], kalan=m[2]) for m in M]
        print(f'MUTASYON: {sum(1 for m in M if m[1])} / {len(M)} yakalandı', flush=True)
    if '--kod' not in sys.argv: IN.yaz_json(os.path.join(KAR, 'tr4_test_yapay_sonuc.json'), rapor)
    sys.exit(0 if n_ok == len(SONUC) else 1)
