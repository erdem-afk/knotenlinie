#!/usr/bin/env python3
"""TR-7c KURU PROVA (kod incelemesi §B.3): gerçek I/O katmanının (`GercekOrtam`, `GercekKaynak`, `asama_manifest`,
`lp_adaylari_manifest`, `asama_indirme`, `lp_indir`, `negatif_turu`, `k1c_kos`; aşama protokolü `baslat` / `kos` /
`durdu`) yalnız 127.0.0.1'de çalışan SAHTE bir FDSN sunucusuna karşı uçtan uca koşusu. YALNIZ YAPAY VERİ.

Sahte sunucu: dataselect (yapay miniSEED, 20 Hz), station (yapay StationXML), ComCat/EMSC olay sorgusu (olay zamanı,
yeri ve büyüklüğü depodaki `tr7b_sayim.json`'dan; derinlik 33 km sabit). İstasyon adları gerçektir
(`tr7_parkfield_liste.csv`), dalga formları ve yanıtlar tümüyle yapaydır. Gerçek sunuculara HİÇBİR istek gitmez:
- taban URL'ler yalnız `tr7c_kosu.prova_ac` (sınama düğmesi) ile 127.0.0.1'e çevrilir; düğme kapı açıkken (koşu
  dondurulmuşken) açılmaz (aşağıda sınanır);
- süreçte iki denetim kancası vardır: koşu kodunun kendi kancası (prova açıkken izinli (127.0.0.1, port) dışındaki her
  bağlantıyı ve ad çözümünü reddeder) ve bu betiğin kancası (sahte sunucunun portu dışındaki her bağlantı,
  `/mnt/project-files` altında açma, gerçek çıktı dizinine `kosu/` yazma, `pip freeze` dışındaki alt süreç reddedilir);
- vekil sunucu ortam değişkenleri süreçten silinir (kapsayıcının vekil sunucusu da 127.0.0.1'dedir; port denetimi bu
  yüzden vardır).
Gerçek kip kapısı AÇILMAZ (ön kayıtta koşu dondurması yok); prova `gercek_kapi`'nın prova kolundan geçer.

Senaryolar: S1 gerçek tremor (yalnız P'de, başvuruya kilitli) → "ölçü sınandı"; S2 ayırt etmeyen (P ve N'de aynı
tremor) → "ölçü sınanamadı"; S3 eksik veri (bazı olaylar boş, 3 P'de başvuru yok → k_koşu 6) + işletim arızaları
(429, 500, zaman aşımı, boş 200, 404, boşluklu veri, bozuk miniSEED) + iki kesinti (K1c-indirme'de biçim hatası payı,
K1c-algılama'da bozuk zarf) ve sürdürme.

Kullanım: python3 -I -B tr7c_prova.py <çıktı.json> [S1,S2,S3,dugme]
"""
import contextlib
import hashlib
import http.server
import io
import json
import math
import os
import shutil
import socketserver
import sys
import threading
import time
import urllib.parse

sys.dont_write_bytecode = True
os.environ.setdefault('OMP_NUM_THREADS', '1')
for _k in list(os.environ):
    if _k.lower() in ('http_proxy', 'https_proxy', 'all_proxy', 'ftp_proxy'):
        del os.environ[_k]

BURA = os.path.dirname(os.path.abspath(__file__))
GECICI = '/tmp/claude-0/-home-user/635decb6-3930-5a4d-9c31-b6f30d64fb94/scratchpad/tr7c_kod'
YASAK_KOK = '/mnt/project-files'
CIKTI_GERCEK = os.path.join(BURA, 'kosu')

# ---------------------------------------------------------------- bu betiğin denetim kancası
ENGEL = []
OBSPY_GIT = []
SAHTE_UCLAR = set()


def _yol(a):
    try:
        if isinstance(a, int):
            return None
        return os.path.abspath(os.fsdecode(a))
    except Exception:   # noqa: BLE001
        return None


def _kanca(olay, args):
    if olay == 'open' and args:
        p = _yol(args[0])
        if p and (p == YASAK_KOK or p.startswith(YASAK_KOK + os.sep)):
            ENGEL.append((olay, p))
            raise PermissionError(f'PROVA: gerçek veri yolu yasak: {p}')
        if p and (p == CIKTI_GERCEK or p.startswith(CIKTI_GERCEK + os.sep)):
            mod = args[1] if len(args) > 1 else 'r'
            if isinstance(mod, str) and any(c in mod for c in 'wax+'):
                ENGEL.append((olay, p))
                raise PermissionError(f'PROVA: gerçek çıktı dizinine yazma yasak: {p}')
    elif olay in ('os.mkdir', 'os.makedirs') and args:
        p = _yol(args[0])
        if p and (p.startswith(CIKTI_GERCEK) or p.startswith(YASAK_KOK)):
            ENGEL.append((olay, p))
            raise PermissionError(f'PROVA: dizin yasak: {p}')
    elif olay == 'subprocess.Popen':
        argv = [str(x) for x in (args[1] or [])] if len(args) > 1 else []
        if argv[1:4] == ['-m', 'pip', 'freeze']:
            return
        if argv[:1] == ['git'] and 'rev-parse' in argv:
            OBSPY_GIT.append(argv)        # obspy'nin içe aktarılırken sürüm için denediği git (site-packages)
        else:
            ENGEL.append((olay, repr(argv)[:200]))
        raise PermissionError(f'PROVA: alt süreç yasak: {argv[:3]}')
    elif olay in ('os.system', 'os.exec', 'os.posix_spawn', 'os.fork'):
        ENGEL.append((olay, repr(args)[:160]))
        raise PermissionError(f'PROVA: {olay} yasak')
    elif olay == 'socket.connect':
        a = args[1] if len(args) > 1 else None
        if not (isinstance(a, tuple) and len(a) >= 2 and (a[0], a[1]) in SAHTE_UCLAR):
            ENGEL.append((olay, repr(a)[:160]))
            raise PermissionError(f'PROVA: izinsiz bağlantı {a!r}')
    elif olay == 'socket.getaddrinfo':
        h = args[0].decode() if isinstance(args[0], bytes) else args[0]
        try:
            p = int(args[1]) if args[1] is not None else None
        except (TypeError, ValueError):
            p = None
        if (h, p) not in SAHTE_UCLAR:
            ENGEL.append((olay, repr((h, p))))
            raise PermissionError(f'PROVA: izinsiz ad çözümü {h}:{p}')
    elif olay in ('socket.gethostbyname', 'socket.gethostbyaddr', 'socket.sendto', 'socket.sendmsg'):
        ENGEL.append((olay, repr(args)[:160]))
        raise PermissionError(f'PROVA: {olay} yasak')
    elif olay == 'socket.bind':
        a = args[1] if len(args) > 1 else None
        if not (isinstance(a, tuple) and a[0] == '127.0.0.1'):
            ENGEL.append((olay, repr(a)))
            raise PermissionError(f'PROVA: bağlama yalnız 127.0.0.1: {a!r}')


sys.addaudithook(_kanca)

sys.path.insert(0, BURA)
import numpy as np  # noqa: E402
import tr7c_kosu as KM  # noqa: E402

K = KM.K
sys.path.insert(0, KM.TR7)
import tr7_kosu as T  # noqa: E402  (değiştirilmeden; yalnız senaryo kurulumu için okuma)
import tr7_indir as I  # noqa: E402

FS = 20.0
S_DUY = 6.0e8               # sayım / (m/s)
GUR = 1.0e-7                # m/s, beyaz
TREMOR_RMS = 6.0e-7         # m/s, 2–8 Hz
TREMOR_S = 300.0
LP_RMS = 2.0e-5             # m/s, 15–30 sn dar bant
DERINLIK = 33.0
VERI_IST = (('NC', 'PMM'), ('NC', 'PHF'), ('NC', 'PGH'), ('NC', 'PHA'))   # 41 birimin hepsinde liste istasyonu
REF = ('BK', 'PKD')
KOTU = ('NC', 'PST')       # iz ortasına en yakın; geniş bant kodlu ama 1 Hz yanıtlı (E-1 'uygun_yanit' değil)


# ================================================================ sahte FDSN sunucusu
def _yanit(tur):
    from obspy.core.inventory import Response
    if tur == 'gb':
        w, fn = 2 * np.pi / 120.0, 1.0
    else:                       # 'sp': 1 Hz jeofon
        w, fn = 2 * np.pi * 1.0, 5.0
    r = Response.from_paz(zeros=[0j, 0j], poles=[complex(-w * 0.707, w * 0.707), complex(-w * 0.707, -w * 0.707)],
                          stage_gain=S_DUY, stage_gain_frequency=fn, input_units='M/S', output_units='COUNTS',
                          normalization_frequency=fn)
    r.recalculate_overall_sensitivity(fn)
    return r


def _envanter(ag, ist, la, lo, kanallar):
    """kanallar: [(konum, kod, tür)]"""
    from obspy import UTCDateTime
    from obspy.core.inventory import Inventory, Network, Station, Channel
    ch = []
    for loc, c, tur in kanallar:
        az, dip = {'Z': (0.0, -90.0), 'N': (0.0, 0.0), 'E': (90.0, 0.0)}[c[-1]]
        ch.append(Channel(c, loc, la, lo, 0.0, 0.0, azimuth=az, dip=dip, sample_rate=FS, response=_yanit(tur),
                          start_date=UTCDateTime(1990, 1, 1)))
    inv = Inventory(networks=[Network(ag, stations=[Station(ist, la, lo, 0.0, channels=ch,
                                                            start_date=UTCDateTime(1990, 1, 1))])], source='yapay')
    b = io.BytesIO()
    inv.write(b, format='STATIONXML')
    return b.getvalue()


class _Sunucu(http.server.ThreadingHTTPServer):
    daemon_threads = True

    def server_bind(self):          # getfqdn (ters ad çözümü) yok
        socketserver.TCPServer.server_bind(self)
        self.server_name, self.server_port = '127.0.0.1', self.server_address[1]


class SahteFDSN(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        sv = self.server
        u = urllib.parse.urlparse(self.path)
        q = dict(urllib.parse.parse_qsl(u.query))
        with sv.kilit:
            sv.istekler.append(dict(yol=u.path, q=q, ua=self.headers.get('User-Agent'), host=self.headers.get('Host')))
        try:
            if '/dataselect/' in u.path:
                return self._veri(q)
            if '/station/' in u.path:
                return self._istasyon(q)
            if u.path.startswith('/comcat'):
                return self._katalog(q, 'comcat')
            if u.path.startswith('/emsc'):
                return self._katalog(q, 'emsc')
            return self._kod(404)
        except Exception as e:      # noqa: BLE001
            sv.hatalar.append(f'{type(e).__name__}: {e}')
            return self._kod(500)

    def _kod(self, k, ek=None):
        self.send_response(k)
        for a, b in (ek or {}).items():
            self.send_header(a, b)
        self.send_header('Content-Length', '0')
        self.end_headers()

    def _govde(self, b, ct):
        self.send_response(200)
        self.send_header('Content-Type', ct)
        self.send_header('Content-Length', str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def _istasyon(self, q):
        sv = self.server
        key = (q['net'], q['sta'])
        if key not in sv.koord:
            return self._kod(204)
        la, lo = sv.koord[key]
        loc = '' if q['loc'] == '--' else q['loc']
        desen = [c[:2] for c in q['cha'].split(',')]
        if loc == '*':                                     # E-1 uzun periyot aday sorgusu (HH?, BH?)
            if key == REF:
                kan = [(l_, b + c, 'gb') for l_, b in (('00', 'HH'), ('10', 'HH'), ('00', 'BH')) for c in 'ZNE']
            elif key == KOTU:
                kan = [('', 'HH' + c, 'sp') for c in 'ZNE']
            else:
                return self._kod(204)
        elif key == REF:
            kan = [(loc, b + c, 'gb') for b in desen for c in 'ZNE']
        elif key in VERI_IST or key == KOTU:
            kan = [(loc, b + 'Z', 'sp') for b in desen]
        else:
            return self._kod(204)
        return self._govde(_envanter(key[0], key[1], la, lo, kan), 'application/xml')

    def _katalog(self, q, kt):
        sv = self.server
        bas = K.epoch(q.get('starttime') or q.get('start'))
        bit = K.epoch(q.get('endtime') or q.get('end'))
        if bit >= K.epoch('2026-01-01T00:00:00'):
            sv.hatalar.append('2026 katalog isteği')
        mm = float(q.get('minmagnitude') or q.get('minmag'))
        la0, lo0 = float(q.get('latitude') or q.get('lat')), float(q.get('longitude') or q.get('lon'))
        rd = float(q.get('maxradius'))
        ol = [o for o in sv.olaylar if bas <= o[0] <= bit and o[3] >= mm and K.hav(la0, lo0, o[1], o[2]) / 111.195 <= rd]
        if kt == 'comcat':
            s = 'time,latitude,longitude,depth,mag,id\n' + ''.join(
                f'{K.epoch_zaman(t).isoformat()}Z,{la},{lo},{DERINLIK},{M},{i}\n' for t, la, lo, M, i in ol)
        else:
            if not ol:
                return self._kod(204)
            s = '#EventID|Time|Latitude|Longitude|Depth/Km|Author|Catalog|Contributor|ContributorID|MagType|' \
                'Magnitude|MagAuthor|EventLocationName\n' + ''.join(
                    f'{i}|{K.epoch_zaman(t).isoformat()}|{la}|{lo}|{DERINLIK}|A|C|C|1|mw|{M}|A|yer\n'
                    for t, la, lo, M, i in ol)
        return self._govde(s.encode(), 'text/plain')

    def _veri(self, q):
        from obspy import Stream, Trace, UTCDateTime
        sv = self.server
        key = (q['net'], q['sta'])
        loc = '' if q['loc'] == '--' else q['loc']
        bas, bit = K.epoch(q['start']), K.epoch(q['end'])
        if bit >= K.epoch('2026-01-01T00:00:00'):
            sv.hatalar.append('2026 veri isteği')
        ar = next((a for a in sv.araliklar if a['a'] - 1 <= bas and bit <= a['b'] + 1), None)
        if ar is None or ar['birim'] in sv.bos:
            return self._kod(204)
        bid = ar['birim']
        if key == REF:
            if ar['tur'] != 'tet' or loc not in ('00', '10') or bid in sv.lp_yok:
                return self._kod(204)
        elif key not in VERI_IST:
            return self._kod(204)
        # arızalar (S3) ve kesinti
        if sv.kesinti and bid in sv.kesinti_birim:
            with sv.kilit:
                sv.sayac['kesinti'] = sv.sayac.get('kesinti', 0) + 1
            return self._govde(b'bu miniSEED degil' * 300, 'application/vnd.fdsn.mseed')
        ariza = sv.ariza.get((key[1], bid))
        if ariza:
            with sv.kilit:
                sv.sayac[ariza] = sv.sayac.get(ariza, 0) + 1
                n_ar = sv.sayac[ariza]
            if ariza == '429' and n_ar == 1:
                return self._kod(429, {'Retry-After': '0'})
            if ariza == '500':
                return self._kod(500)
            if ariza == 'zaman':
                time.sleep(sv.uyku_s)
            if ariza == 'bos200':
                return self._govde(b'', 'application/vnd.fdsn.mseed')
            if ariza == '404':
                return self._kod(404)
            if ariza == 'bozuk':
                return self._govde(b'bu miniSEED degil' * 300, 'application/vnd.fdsn.mseed')
        n = int(round((bit - bas) * FS)) + 1
        t = bas + np.arange(n) / FS
        st = Stream()
        tohum = int(hashlib.sha256(f'{key}{loc}{int(bas)}'.encode()).hexdigest()[:12], 16)
        for c in q['cha'].split(','):
            rng = np.random.default_rng(tohum + 'ZNE'.index(c[-1]))
            v = rng.standard_normal(n) * GUR
            if key in VERI_IST and c[-1] == 'Z':
                for tr in sv.tremorler:
                    if tr['birim'] == bid and key in tr['ist']:
                        v += tremor_sinyal(sv, tr, t, np.random.default_rng(tohum + 7))
            if key == REF and loc == '00':
                v += {'Z': 1.0, 'N': 0.8, 'E': 0.6}[c[-1]] * lp_degeri(sv, bid, t)
            x = np.round(v * S_DUY).astype(np.int32)
            tr_ = Trace(x, header=dict(network=key[0], station=key[1], location=loc, channel=c, sampling_rate=FS,
                                       starttime=UTCDateTime(bas)))
            if ariza == 'bosluk':
                st += tr_.slice(UTCDateTime(bas), UTCDateTime(bas + (bit - bas) * 0.4)).copy()
                st += tr_.slice(UTCDateTime(bas + (bit - bas) * 0.7), UTCDateTime(bit)).copy()
            else:
                st += tr_
        b = io.BytesIO()
        st.write(b, format='MSEED', encoding='STEIM2', reclen=4096)
        return self._govde(b.getvalue(), 'application/vnd.fdsn.mseed')


def lp_serisi(sv, bid):
    """Birimin 1 Hz başvuru hızı (15–30 sn dar bantlı Gauss, LP_RMS) ve fazı; birim başına sabit tohum."""
    with sv.kilit:
        if bid in sv.lp:
            return sv.lp[bid]
    from scipy.signal import butter, sosfiltfilt, hilbert
    a = next(x for x in sv.araliklar if x['birim'] == bid and x['tur'] == 'tet')
    t0 = math.floor(a['a']) - 100
    n = int(math.ceil(a['b'] - t0)) + 200
    rng = np.random.default_rng(int(hashlib.sha256(f'lp{bid}'.encode()).hexdigest()[:12], 16))
    sos = butter(4, [1 / 30.0, 1 / 15.0], btype='band', fs=1.0, output='sos')
    x = sosfiltfilt(sos, rng.standard_normal(n))
    x *= LP_RMS / np.sqrt(np.mean(x ** 2))
    cf = np.cos(np.angle(hilbert(x)))
    out = (t0, x, cf)
    with sv.kilit:
        sv.lp[bid] = out
    return out


def lp_degeri(sv, bid, t):
    t0, x, _ = lp_serisi(sv, bid)
    return np.interp(t, t0 + np.arange(len(x)), x)


def tremor_sinyal(sv, tr, t, rng):
    from scipy.signal import butter, sosfiltfilt
    i = (t >= tr['ta']) & (t < tr['ta'] + TREMOR_S)
    s = np.zeros(len(t))
    if i.sum() < 100:
        return s
    tt = t[i] - tr['ta']
    taper = np.minimum(1, np.minimum(tt, TREMOR_S - tt) / 10.0)
    if tr['kilitli']:
        t0, _, cf = lp_serisi(sv, tr['birim'])
        mod = 0.1 + np.maximum(0, np.interp(t[i], t0 + np.arange(len(cf)), cf))
    else:
        mod = 0.1 + np.maximum(0, np.sin(2 * np.pi * tt / 23.0 + 1.3))
    g = sosfiltfilt(butter(4, [2.0, 8.0], btype='band', fs=FS, output='sos'), rng.standard_normal(int(i.sum())))
    g = g / np.sqrt(np.mean(g ** 2)) * taper * mod
    s[i] = g * TREMOR_RMS / np.sqrt(np.mean(g ** 2))
    return s


@contextlib.contextmanager
def sahte_sunucu():
    s = _Sunucu(('127.0.0.1', 0), SahteFDSN)
    s.kilit = threading.Lock()
    s.istekler, s.hatalar = [], []
    s.koord = {}
    import csv
    with open(os.path.join(KM.TR7, 'tr7_parkfield_liste.csv'), encoding='utf-8', newline='') as f:
        for r in csv.DictReader(f):
            s.koord[(r['ag'], r['istasyon'])] = (float(r['enlem']), float(r['boylam']))
    s.olaylar = [(K.epoch(o['t0']), o['la'], o['lo'], o['M'], f"yapay{o['evid']}") for o in KM.olaylar().values()]
    s.araliklar, s.tremorler, s.lp = [], [], {}
    s.bos, s.lp_yok, s.ariza, s.sayac = set(), set(), {}, {}
    s.kesinti, s.kesinti_birim, s.uyku_s = False, set(), 3.0
    th = threading.Thread(target=s.serve_forever, daemon=True)
    th.start()
    p = s.server_address[1]
    SAHTE_UCLAR.add(('127.0.0.1', p))
    try:
        yield s, {k: f'http://127.0.0.1:{p}/{k}/fdsnws' for k in I.SERVIS}, \
            {'comcat': f'http://127.0.0.1:{p}/comcat/query', 'emsc': f'http://127.0.0.1:{p}/emsc/query'}
    finally:
        s.shutdown()
        s.server_close()
        SAHTE_UCLAR.discard(('127.0.0.1', p))


# ================================================================ senaryo kurulumu (yalnız depo dosyaları)
def tremor_basi(b, p, D, man_derinlik):
    """K1b ile kesişen, bütün veri istasyonlarının W'sinde, E1 maskesinden ve (b′) çekirdek faz pencerelerinden uzak
    300 sn'lik tremorun başı (epoch)."""
    from obspy.geodetics import locations2degrees
    ws = [p['ist'][k]['W'] for k in VERI_IST if k in p['ist']]
    w0 = max(K.epoch(w[0]) for w in ws) + 40
    w1 = min(K.epoch(w[1]) for w in ws) - TREMOR_S - 40
    k1, k2 = b['K1b']
    e1 = K.e1_araliklar(T.e1_olaylari_csv(D['e1'], p['tetikleyici'], 'PK'), None, None)
    dg = locations2degrees(p['ev'][0], p['ev'][1], *KM.IZ_ORTA)
    cek = [K.epoch(p['t0']) + x for v in K.cekirdek_fazlari(man_derinlik, dg).values() for x in v]
    for pay, cekirdek in ((60, True), (0, True), (0, False)):     # gevşetme sırası (yalnız yer bulunamazsa)
        for ta in np.arange(max(w0, k1 - 120), min(w1, k2 - 30), 5.0):
            if any(a < ta + TREMOR_S + pay and z > ta - pay for a, z in e1):
                continue
            if cekirdek and any(ta - 150 <= v <= ta + 40 for v in cek):
                continue
            return float(ta)
    return None


def kur(sv, sen, birimler, D):
    """Sunucunun veri aralıklarını (tetikleyici pencereleri) ve tremorlerini kurar (manifestten önce)."""
    for b in birimler:
        p = D['pen'][f"pk|{b['id']}"]
        xs = list(p['ist'].values())
        sv.araliklar.append(dict(birim=b['id'], tur='tet', a=K.epoch(min(x['R'][0] for x in xs)) - K.DOLGU_S,
                                 b=K.epoch(max(x['W'][1] for x in xs)) + K.DOLGU_S))
    yerler = {}
    for b in birimler:
        if b['sinif'] not in sen['tremor_sinif'] or b['id'] in sen.get('bos', ()):
            continue
        ta = tremor_basi(b, D['pen'][f"pk|{b['id']}"], D, DERINLIK)
        yerler[b['id']] = ta
        if ta is not None:
            sv.tremorler.append(dict(birim=b['id'], ta=ta, ist=set(VERI_IST), kilitli=True))
    sv.bos = set(sen.get('bos', ()))
    sv.lp_yok = set(sen.get('lp_yok', ()))
    return yerler


def negatif_kur(sv, sen, man, birimler, D):
    e = sen['neg_olay']
    b = next(x for x in birimler if e in x['evids'])
    p = D['pen'][f"pk|{b['id']}"]
    xs = list(p['ist'].values())
    a0 = K.epoch(min(x['R'][0] for x in xs)) - K.DOLGU_S
    b0 = K.epoch(max(x['W'][1] for x in xs)) + K.DOLGU_S
    ds = man['negatif_kaydirma'][e]
    for i, d in enumerate(ds, 1):
        bid = f'pkneg|{e}|{i}'
        sv.araliklar.append(dict(birim=bid, tur='neg', a=a0 + d * 86400, b=b0 + d * 86400))
    if sen.get('neg_yanlis'):
        d = ds[0]
        w = [K.epoch(p['ist'][k]['W'][0]) for k in VERI_IST]
        sv.tremorler.append(dict(birim=f'pkneg|{e}|1', ta=max(w) + d * 86400 + 200, ist=set(VERI_IST), kilitli=False))
    return ds


# ================================================================ sınama kaydı
class Kayit:
    def __init__(self):
        self.s = []

    def sina(self, grup, ad, kosul, ayrinti=None):
        self.s.append(dict(grup=grup, ad=ad, gecti=bool(kosul), ayrinti=ayrinti))
        print(('GEÇTİ ' if kosul else 'KALDI ') + f'[{grup}] {ad}', flush=True)
        if not kosul and ayrinti is not None:
            print('    ', json.dumps(ayrinti, ensure_ascii=False, default=str)[:600], flush=True)


def komut(*argv):
    """CLI (tr7c_kosu.main) ile; dönüş (kod, stderr)."""
    e = io.StringIO()
    o = io.StringIO()
    with contextlib.redirect_stderr(e), contextlib.redirect_stdout(o):
        r = KM.main(list(argv))
    return r, e.getvalue()


def asama(R, g, ad):
    r1, e1 = komut('baslat', ad)
    t = time.time()
    r2, e2 = komut('kos', ad)
    R.sina(g, f'{ad}: baslat + kos (CLI) başarıyla', r1 == 0 and r2 == 0, dict(baslat=e1, kos=e2[-1500:]))
    return round(time.time() - t, 1)


SENARYOLAR = {
    'S1': dict(aciklama='gerçek tremor: 10 P olayında başvuru hızına kilitli tremor; N\'de yok; 1 negatif pencerede '
                         'kilitsiz tremor (yanlış alarm)',
               tremor_sinif=('P',), neg_olay='200106232033', neg_yanlis=True,
               beklenen=dict(dal='b', n_P=10, n_N=29, X_P=10, X_N=0, f_PK=1, N_PK=10, k_kosu=10,
                             cumle_bas='ölçü sınandı; genliği eşlenmiş 4 N olayında modülasyonu ölçülemeyen: 4; '
                                       'k: üstveriden 10, koşuda 10', var=True)),
    'S2': dict(aciklama='ayırt etmeyen algılayıcı: P ve N olaylarının hepsinde aynı kilitli tremor',
               tremor_sinif=('P', 'N'), neg_olay='200106232033', neg_yanlis=True,
               beklenen=dict(dal='c', alt='(iii)', n_P=10, n_N=29, X_P=10, X_N=29, f_PK=1, N_PK=10, k_kosu=10,
                             cumle_bas='ölçü sınanamadı (algılayıcı kör olaylarda tetiklenmiş tremoru tetikleyici '
                                       'genliğinden ayıramadı) (kalan: (iii))', genlik=True, var=False)),
    'S3': dict(aciklama='eksik veri: 1 P ve 2 N olayında hiç veri yok, 3 P olayında E-1 başvurusu yok (k_koşu 6); '
                         'işletim arızaları ve iki kesinti + sürdürme',
               tremor_sinif=('P',), neg_olay='200106232033', neg_yanlis=False,
               bos=('200211032212', '200110190328', '200209081844'),
               lp_yok=('200301220206', '200309251950', '200412260058'),
               ariza={('PHA', '200611151114'): '429', ('PHA', '200701130423'): '500',
                      ('PGH', '200805120628'): 'zaman', ('PHF', '200909291748'): 'bos200',
                      ('PMM', '201002270634'): '404', ('PMM', '200107070938'): 'bosluk',
                      ('PHF', '200308040437'): 'bozuk'},
               kesinti_birim=('201004062215', '201006121926'),
               beklenen=dict(dal='b', n_P=9, n_N=27, X_P=9, X_N=0, f_PK=0, N_PK=10, k_kosu=6)),
}


def senaryo(R, ad):
    sen = SENARYOLAR[ad]
    g = ad
    kok = os.path.join(GECICI, 'prova', f'{ad}_{time.time_ns()}')
    os.makedirs(kok)
    dizin, zarf = os.path.join(kok, 'cikti'), os.path.join(kok, 'zarf')
    ozet = dict(aciklama=sen['aciklama'], sure_s={})
    birimler = KM.birimler_kur()
    D0 = KM.dunya_kur(birimler)
    with sahte_sunucu() as (sv, servis, katalog):
        yerler = kur(sv, sen, birimler, D0)
        ozet['tremor_basi'] = yerler
        R.sina(g, 'senaryo kurulumu: tremor başı her tremorlu birimde bulundu',
               all(v is not None for v in yerler.values()), yerler)
        sv.ariza = dict(sen.get('ariza', {}))
        pr = KM.Prova(dizin=dizin, zarf=zarf, servis=servis, katalog=katalog)
        engel0, kengel0 = len(ENGEL), len(KM.PROVA_ENGEL)
        with KM.prova_ac(pr):
            go = KM.GercekOrtam(log=lambda *a: None)
            R.sina(g, 'prova: GercekOrtam taban URL\'leri yalnız 127.0.0.1, dizinler prova dizini, git doğrulaması yok',
                   all(urllib.parse.urlsplit(u).hostname == '127.0.0.1' for u in list(go.servis.values()) +
                       list(go.katalog.values())) and go.tr7 == dizin and go.zarf == zarf and not go.git_dogrula
                   and go.hyol('x').startswith(zarf))
            # önkoşul: sıra dışı aşama, başlatılmadan koşma
            r, e = komut('baslat', 'K1c-indirme')
            R.sina(g, 'önkoşul: manifest tamamlanmadan K1c-indirme başlatılamaz', r == 2 and 'önceki aşama' in e, e)
            r, e = komut('kos', 'manifest')
            R.sina(g, 'önkoşul: başlatılmamış aşama koşulamaz', r == 2 and 'başlatılmamış' in e, e)
            ozet['sure_s']['manifest'] = asama(R, g, 'manifest')
            r, e = komut('baslat', 'manifest')
            R.sina(g, 'tek koşu: tamamlanmış manifest ikinci kez başlatılamaz', r == 2 and 'zaten tamamlandı' in e, e)
            man = KM._json(go.yol('tr7c_manifest.json'))
            negatif_kur(sv, sen, man, birimler, D0)
            # K1c-indirme (S3: biçim hatası payıyla kesinti → durdu → sürdür)
            if sen.get('kesinti_birim'):
                sv.kesinti, sv.kesinti_birim = True, set(sen['kesinti_birim'])
                komut('baslat', 'K1c-indirme')
                r, e = komut('kos', 'K1c-indirme')
                d = KM.durum_oku(dizin)
                R.sina(g, 'kesinti 1 (K1c-indirme, biçim hatası payı > %1): aşama durur, durum "hata", durma kaydı '
                          '(kod) yazıldı', r == 2 and 'biçim hatası payı' in e and
                       d['asamalar']['K1c-indirme']['durum'] == 'hata' and
                       any(x['asama'] == 'K1c-indirme' and x['tur'] == 'kod' for x in d['durmalar']), e[-800:])
                r, e = komut('kos', 'K1c-indirme')
                R.sina(g, 'kesinti 1: "hata" durumundaki aşama yeniden başlatılmadan koşulamaz', r == 2, e)
                r, e = komut('baslat', 'K1c-indirme', '--surdur')
                R.sina(g, 'kesinti 1: elle durma kaydı olmadan --surdur reddedilir', r == 2 and 'elle' in e, e)
                r, _ = komut('durdu', 'K1c-indirme', '--neden', 'prova: sahte sunucu bozuk miniSEED verdi (kesinti 1)')
                sv.kesinti = False
                ozet['sure_s']['K1c-indirme_surdur'] = 0
                r1, e1 = komut('baslat', 'K1c-indirme', '--surdur')
                t = time.time()
                r2, e2 = komut('kos', 'K1c-indirme')
                ozet['sure_s']['K1c-indirme_surdur'] = round(time.time() - t, 1)
                R.sina(g, 'kesinti 1: durdu + baslat --surdur + kos ile sürdü ve tamamlandı', r == 0 and r1 == 0 and
                       r2 == 0, dict(e1=e1, e2=e2[-800:]))
            else:
                ozet['sure_s']['K1c-indirme'] = asama(R, g, 'K1c-indirme')
            ozet['sure_s']['K1c-negatif'] = asama(R, g, 'K1c-negatif')
            r, e = komut('baslat', 'K1c-negatif')
            R.sina(g, 'tek koşu: K1c-negatif ikinci kez başlatılamaz', r == 2 and 'zaten tamamlandı' in e, e)
            # K1c-algılama (S3: bozuk zarfla kesinti → durdu → sürdür)
            if ad == 'S3':
                kay = T.zarf_kayitlari(go).get('pk|200611151114', {})
                rec = next(v for v in kay.values() if v.get('sha256'))
                zy = os.path.join(zarf, rec['dosya'])
                yedek = zy + '.yedek'
                shutil.copy2(zy, yedek)
                with open(zy, 'ab') as f:
                    f.write(b'bozuk')
                komut('baslat', 'K1c-algılama')
                r, e = komut('kos', 'K1c-algılama')
                d = KM.durum_oku(dizin)
                alg1 = KM.jsonl_oku(os.path.join(dizin, 'tr7c_algilama.jsonl'))
                R.sina(g, 'kesinti 2 (K1c-algılama, bozuk zarf): aşama durur, "hata" + durma kaydı (kod, ileti, saat), '
                          'hüküm yazılmadı', r == 2 and 'sha256' in e and d['asamalar']['K1c-algılama']['durum'] ==
                       'hata' and any(x['asama'] == 'K1c-algılama' and x['tur'] == 'kod' and x['zaman']
                                      for x in d['durmalar']) and not os.path.exists(os.path.join(dizin, KM.HUKUM_AD)),
                       e[-600:])
                r, e = komut('baslat', 'K1c-algılama')
                R.sina(g, 'kesinti 2: algılama aşamasına --surdur olmadan ikinci kez girilemez',
                       r == 2 and 'algılama aşamasına daha önce girildi' in e, e)
                r, e = komut('baslat', 'K1c-algılama', '--surdur')
                R.sina(g, 'kesinti 2: elle durma kaydı olmadan --surdur reddedilir', r == 2 and 'elle' in e, e)
                komut('durdu', 'K1c-algılama', '--neden', 'prova: zarf dosyası bozuldu (kesinti 2); yedekten geri kondu')
                os.replace(yedek, zy)
                r1, e1 = komut('baslat', 'K1c-algılama', '--surdur')
                t = time.time()
                r2, e2 = komut('kos', 'K1c-algılama')
                ozet['sure_s']['K1c-algılama'] = round(time.time() - t, 1)
                alg2 = KM.jsonl_oku(os.path.join(dizin, 'tr7c_algilama.jsonl'))
                R.sina(g, 'kesinti 2: sürdürme kaldığı birimden devam etti (önceki satırlar yeniden yazılmadı, her birim '
                          'bir kez)', r1 == 0 and r2 == 0 and len(alg1) > 0 and alg2[:len(alg1)] == alg1 and
                       len({x['id'] for x in alg2}) == len(alg2) == 41,
                       dict(once=len(alg1), sonra=len(alg2), e1=e1, e2=e2[-600:]))
                ozet['kesinti2_once_satir'] = len(alg1)
            else:
                ozet['sure_s']['K1c-algılama'] = asama(R, g, 'K1c-algılama')
            r, e = komut('baslat', 'K1c-algılama', '--surdur')
            R.sina(g, 'tek koşu: tamamlanmış K1c-algılama --surdur ile de başlatılamaz', r == 2 and 'zaten tamamlandı'
                   in e, e)
            # kilit: hüküm dosyası varken k1c_kos hiçbir şey hesaplamaz
            msj = []
            man = KM._json(go.yol('tr7c_manifest.json'))
            Dm = KM.dunya_kur(birimler, man['negatif_kaydirma'])
            kay = KM.GercekKaynak(go, Dm, man, birimler, man['derinlik'])
            n_once = len(sv.istekler)
            h2 = KM.k1c_kos(kay, dizin, KM.Ayar(), gercek=True, gunluk=msj.append, durum_yaz=False)
            R.sina(g, 'kilit: hüküm dosyası varken ikinci k1c_kos hiçbir şey hesaplamadı ve istek atmadı',
                   any('KİLİT' in m for m in msj) and not kay._onbellek and len(sv.istekler) == n_once, msj)
            r, e = komut('durum')
        # ---------------------------------------------------------------- denetimler
        h = KM._json(os.path.join(dizin, KM.HUKUM_AD))
        bek = sen['beklenen']
        anahtar = ('dal', 'n_P', 'n_N', 'X_P', 'X_N', 'f_PK', 'N_PK')
        gercek_ = {k: h[k] for k in anahtar}
        gercek_['k_kosu'] = h['etiket']['k_kosu']
        R.sina(g, 'hüküm: dal ve sayımlar beklenenle aynı', all(gercek_[k] == bek[k] for k in gercek_),
               dict(gercek=gercek_, beklenen={k: bek[k] for k in gercek_}))
        if 'alt' in bek:
            R.sina(g, f"hüküm: (c) kalan şart {bek['alt']}", h['alt'] == bek['alt'], h['alt'])
        if 'cumle_bas' in bek:
            R.sina(g, 'hüküm cümlesi beklenen biçimde', h['cumle'].startswith(bek['cumle_bas']), h['cumle'])
        if 'var' in bek:
            R.sina(g, 'VAR verilebilirliği beklenen', h['var_verilebilir'] == bek['var'], h['var_verilebilir'])
        if 'genlik' in bek:
            R.sina(g, 'D-9 genlik etiketi beklenen', h['etiket']['genlik'] == bek['genlik'], h['etiket'])
        R.sina(g, 'hüküm: gerçek kip bayrağı, ayar ön kayıttaki gibi (mod_n 1000, MDA 3), tohumlar',
               h['gercek_kip'] is True and h['ayar'] == dict(mod_n=1000, mda_bas=3) and
               h['tohum'] == dict(modulasyon=20261115, mda=20261114, negatif_secim=20261117), h['ayar'])
        alg = KM.jsonl_oku(os.path.join(dizin, 'tr7c_algilama.jsonl'))
        R.sina(g, 'algılama sırası: önce 29 N, sonra 10 P, sonra 2 B (jsonl)',
               [r_['sinif'] for r_ in alg] == ['N'] * 29 + ['P'] * 10 + ['B'] * 2, [r_['sinif'] for r_ in alg])
        # E-1
        refs = {bid: v['ref'] for bid, v in h['modulasyon'].items()}
        p_ref = {b['id']: refs.get(b['id']) for b in birimler if b['sinif'] == 'P'}
        bek_ref = {bid: (None if bid in sen.get('lp_yok', ()) or bid in sen.get('bos', ()) else
                         ('BK.PKD', 'HHZ', '00', 3)) for bid in p_ref}
        gr = {bid: (None if v is None else (v['ad'], v['kanal'], v['konum'], v['bilesen'])) for bid, v in p_ref.items()}
        R.sina(g, 'E-1: başvuru en yakın UYGUN istasyon (PST 1 Hz yanıtlı atlandı), HH önce BH, iki konumda "00", '
                  'üç bileşen; başvurusuz olaylar None', gr == bek_ref, dict(gercek=gr, beklenen=bek_ref))
        lps = KM.jsonl_oku(os.path.join(dizin, 'tr7c_lp_sha256.jsonl'))
        kon = {(x['pencere'], x['kanal'], x['konum']) for x in lps if x['sha256']}
        iki = [bid for bid in p_ref if bek_ref[bid] and (f'pk|{bid}', 'HHZ', '00') in kon and
               (f'pk|{bid}', 'HHZ', '10') in kon]
        R.sina(g, 'K-3: aynı kanal kodu iki konumda (00.HHZ, 10.HHZ) ayrı kayıt; seçilen 00 (10\'da başvuru sinyali yok, '
                  'yanlış konum modülasyonu bozardı)', len(iki) == sum(1 for v in bek_ref.values() if v),
               dict(iki_konumlu=len(iki)))
        R.sina(g, 'E-1: PST (yanıt oranı < 0,5) için hiç lp isteği gitmedi',
               not any(r_['q'].get('sta') == 'PST' and '/dataselect/' in r_['yol'] and r_['q'].get('cha', '')[:2] in
                       ('HH', 'BH') for r_ in sv.istekler))
        if bek['dal'] == 'b' and ad == 'S1':
            mp = [k['p'] for b in birimler if b['sinif'] == 'P' for k in h['modulasyon'][b['id']]['kumeler']]
            R.sina(g, 'modülasyon: kilitli P kümelerinin p ≤ 0,01 (M_mod = X_P)', h['M_mod'] == h['X_P'], mp)
        # durum dosyası biçimi (Ö-b) ve durma kayıtları
        du = KM.durum_oku(dizin)
        R.sina(g, 'durum dosyası: dört aşama "tamamlandı"; kayıtlar yalnız durum, zaman, sha256',
               all(du['asamalar'][a]['durum'] == 'tamamlandı' for a in KM.ASAMALAR) and
               all(set(v) == {'durum', 'zaman', 'sha256'} for v in du['asamalar'].values()), du['asamalar'])
        if ad == 'S3':
            R.sina(g, 'durma kayıtları: iki kesintinin her biri kod + elle', sorted((x['asama'], x['tur'])
                   for x in du['durmalar']) == [('K1c-algılama', 'elle'), ('K1c-algılama', 'kod'),
                                                ('K1c-indirme', 'elle'), ('K1c-indirme', 'kod')], du['durmalar'])
            ind = KM.jsonl_oku(os.path.join(dizin, 'tr7c_indirme_K1c-indirme.jsonl'))
            son = {}
            for x in ind:
                if x.get('tur') == 'istek':
                    son[x['anahtar']] = x
            dur = {}
            for (ist, bid), tur in sen['ariza'].items():
                x = son.get(f'pk|{bid}|NC.{ist}')
                dur[tur] = None if x is None else (x['durum'], x['http'])
            bek_d = {'429': ('tamam', 200), '500': ('servis_hatasi', 500), 'zaman': ('servis_hatasi', None),
                     'bos200': ('yok', 200), '404': ('yok', 404), 'bosluk': ('tamam', 200), 'bozuk': ('bicim_hatasi', 200)}
            R.sina(g, 'arızalar: 429 → yeniden deneme tamam; 500 ve zaman aşımı → servis hatası; boş 200 ve 404 → yok; '
                      'bozuk → biçim hatası', dur == bek_d, dict(gercek=dur, beklenen=bek_d))
            zk = {}
            for x in KM.jsonl_oku(os.path.join(dizin, 'tr7c_zarf_sha256.jsonl')):
                zk.setdefault(x['pencere'], {})[(x['ag'], x['istasyon'])] = x
            bos_ = zk.get('pk|200107070938', {}).get(('NC', 'PMM'), {})
            R.sina(g, 'arıza: boşluklu veri örtüden düştü (dusme "ortu")', bos_.get('dusme') == 'ortu', bos_)
            tar = {b['id']: next(r_ for r_ in alg if r_['id'] == b['id'])['durum'] for b in birimler}
            R.sina(g, 'boş olaylar "dustu", arızalı birimler 3 istasyonla taranmış',
                   all(tar[x] == 'dustu' for x in sen['bos']) and
                   all(tar[bid] == 'tarandi' for (_, bid) in sen['ariza']), tar)
            R.sina(g, 'S3 hüküm cümlesi: "k: üstveriden 10, koşuda 6" ve güç bilgisi', 'k: üstveriden 10, koşuda 6 (k_koşu '
                   'ile güç' in h['cumle'], h['cumle'])
        # körlük ve ağ
        R.sina(g, 'ağ: bütün istekler sahte sunucuya, genel User-Agent; 2026+ istek yok; sunucu hatası yok',
               all(r_['ua'] == I.UA for r_ in sv.istekler) and not sv.hatalar and
               all(r_['host'].startswith('127.0.0.1:') for r_ in sv.istekler), sv.hatalar[:5])
        R.sina(g, 'ağ: prova kancası ve betik kancası hiçbir girişimi reddetmedi (gerçek sunucuya istek denenmedi)',
               len(KM.PROVA_ENGEL) == kengel0 and len(ENGEL) == engel0,
               dict(kosu=KM.PROVA_ENGEL[kengel0:], betik=ENGEL[engel0:]))
        R.sina(g, 'gerçek çıktı dizini kosu/ kurulmadı', not os.path.exists(CIKTI_GERCEK))
        ozet.update(hukum={k: h[k] for k in ('dal', 'alt', 'cumle', 'var_verilebilir', 'n_P', 'n_N', 'X_P', 'X_N',
                                             'f_PK', 'N_PK', 'M_olc', 'M_mod', 'A90_PK', 'mda_deneme')},
                    etiket=h['etiket'], z3=h['z3'], istek_sayisi=len(sv.istekler),
                    istek_tur={t_: sum(1 for r_ in sv.istekler if t_ in r_['yol']) for t_ in
                               ('dataselect', 'station', 'comcat', 'emsc')},
                    ariza_sayac=dict(sv.sayac), durmalar=du['durmalar'],
                    hukum_sha256=KM.sha256_dosya(os.path.join(dizin, KM.HUKUM_AD)))
    shutil.rmtree(kok, ignore_errors=True)
    return ozet


# ================================================================ sınama düğmesi
def dugme(R):
    g = 'düğme'
    import urllib.request
    with sahte_sunucu() as (sv, servis, katalog):
        kok = os.path.join(GECICI, 'prova', f'dugme_{time.time_ns()}')
        pr = KM.Prova(dizin=os.path.join(kok, 'c'), zarf=os.path.join(kok, 'z'), servis=servis, katalog=katalog)
        # 1) kapı açıkken (geçici ön kayıt kopyasında koşu dondurması) prova açılmaz
        metin = open(KM.ONKAYIT, encoding='utf-8').read()
        satir = next(s for s in metin.splitlines() if s.startswith('Durum:'))
        kopya = metin.replace(satir, satir + ' KOŞU DONDURULDU') + '\n' + '\n'.join(KM.kod_sha().values()) + '\n'
        os.makedirs(kok, exist_ok=True)
        yk = os.path.join(kok, 'onkayit_kopya.md')
        with open(yk, 'w', encoding='utf-8') as f:
            f.write(kopya)
        acik = KM.kosu_dondurulmus_mu(yk)
        try:
            with KM.prova_ac(pr, onkayit=yk):
                r = False
        except KM.GercekKipReddedildi as e:
            r = 'gerçek kipte kapalı' in str(e)
        R.sina(g, 'düğme gerçek kipte kapalı: koşu dondurulmuş ön kayıtla (geçici kopya, kapı açık) prova açılmaz',
               acik[0] and r and KM._PROVA is None, acik)
        # 2) gerçek kip benzetimi: kapı açık sayılınca GercekOrtam gerçek tabanla (None), gerçek dizinle, git ile kurulur
        eski = KM.kosu_dondurulmus_mu
        try:
            KM.kosu_dondurulmus_mu = lambda onkayit=None: (True, 'tamam (benzetim)')
            go = KM.GercekOrtam(log=lambda *a: None)
            try:
                with KM.prova_ac(pr):
                    r2 = False
            except KM.GercekKipReddedildi:
                r2 = True
        finally:
            KM.kosu_dondurulmus_mu = eski
        R.sina(g, 'gerçek kip benzetimi: taban None (gerçek sunucular), çıktı kosu/, zarf gerçek kök, git doğrulaması '
                  'açık, prova açılamaz', go.servis is None and go.katalog is None and go.tr7 == KM.CIKTI and
               go.zarf == KM.ZARF_KOK and go.git_dogrula and r2 and go.zaman_asimi == I.ZAMAN_ASIMI_S,
               dict(servis=go.servis, tr7=go.tr7))
        # 3) prova ayarı denetimi
        for ad_, pr_ in (('127.0.0.1 dışı taban', KM.Prova(pr.dizin, pr.zarf, dict(servis, ncedc='http://service.ncedc.'
                                                                                         'org/fdsnws'), katalog)),
                         ('https taban', KM.Prova(pr.dizin, pr.zarf, servis, dict(katalog, comcat=katalog['comcat']
                                                                                  .replace('http:', 'https:')))),
                         ('eksik servis anahtarı', KM.Prova(pr.dizin, pr.zarf, {k: v for k, v in servis.items()
                                                                                 if k != 'koeri'}, katalog)),
                         ('çıktı dizini kosu/', KM.Prova(KM.CIKTI, pr.zarf, servis, katalog)),
                         ('zarf gerçek kök', KM.Prova(pr.dizin, KM.ZARF_KOK, servis, katalog)),
                         ('çıktı depo içinde', KM.Prova(os.path.join(KM.DEPO, 'x'), pr.zarf, servis, katalog))):
            try:
                with KM.prova_ac(pr_):
                    r3 = False
            except KM.GercekKipReddedildi:
                r3 = True
            R.sina(g, f'prova reddedilir: {ad_}', r3 and KM._PROVA is None)
        # 4) prova açıkken: başka port (kapsayıcının vekili de 127.0.0.1'de) ve dış ad çözümü reddedilir
        import socket
        n0, e0 = len(KM.PROVA_ENGEL), len(ENGEL)
        port = urllib.parse.urlsplit(servis['ncedc']).port
        with KM.prova_ac(pr):
            # koşu kodunun kancası (doğrudan çağrı: betiğin kancası önce çalıştığı için gerçek girişimde ona sıra gelmez)
            sonuc = []
            for olay, args in (('socket.connect', (None, ('127.0.0.1', 44457))),
                               ('socket.connect', (None, ('203.0.113.7', 443))),
                               ('socket.getaddrinfo', ('earthquake.usgs.gov', 443, 0, 0, 0)),
                               ('socket.getaddrinfo', ('127.0.0.1', 44457, 0, 0, 0)),
                               ('socket.gethostbyname', ('service.ncedc.org',)),
                               ('socket.connect', (None, ('127.0.0.1', port))),
                               ('socket.getaddrinfo', ('127.0.0.1', port, 0, 0, 0))):
                try:
                    KM._prova_kancasi(olay, args)
                    sonuc.append('izin')
                except PermissionError:
                    sonuc.append('ret')
            # gerçek girişimler (betiğin kancası önce reddeder; hiçbir paket çıkmaz)
            gercek = []
            for hedef in (('127.0.0.1', 44457), ('earthquake.usgs.gov', 443)):
                try:
                    socket.create_connection(hedef, timeout=1).close()
                    gercek.append('bağlandı')
                except PermissionError:
                    gercek.append('ret')
                except OSError as e:
                    gercek.append(f'oserror {e}')
            ok_sahte = urllib.request.urlopen(servis['ncedc'] + '/station/1/query?net=XX&sta=YY&loc=--&cha=HH?'
                                              '&start=2001-01-01T00:00:00&end=2001-01-02T00:00:00', timeout=5).status
        R.sina(g, 'koşu kodunun prova kancası: 127.0.0.1\'in başka portu (kapsayıcının vekili), dış adres, dış ad '
                  'çözümü reddedilir; yalnız sahte sunucunun (127.0.0.1, port) çifti geçer',
               sonuc == ['ret'] * 5 + ['izin'] * 2 and len(KM.PROVA_ENGEL) - n0 == 5,
               dict(sonuc=sonuc, engel=KM.PROVA_ENGEL[n0:]))
        R.sina(g, 'gerçek bağlantı girişimleri reddedildi (vekil portu, dış ad); sahte sunucu yanıt verdi (204)',
               gercek == ['ret', 'ret'] and ok_sahte == 204, dict(gercek=gercek, engel=ENGEL[e0:]))
        del ENGEL[e0:]
        del KM.PROVA_ENGEL[n0:]
        R.sina(g, 'prova kapanınca _PROVA None; gercek_kapi yeniden kapalı kapı', KM._PROVA is None and
               _reddeder(lambda: KM.gercek_kapi('sınama')))
        # 5) taban düzeltmesi geri alınırsa (prova öncesi kod), prova gerçek sunucuya gidecek isteği yakalar
        kaynak = open(KM.__file__, encoding='utf-8').read()
        eski_s = "K.E1_M7, taban=go.katalog)"
        R.sina(g, 'mutasyon dizesi kodda var', kaynak.count(eski_s) == 1)
        mut = kaynak.replace(eski_s, 'K.E1_M7)')
        import types
        M2 = types.ModuleType('tr7c_kosu_mut')
        M2.__file__ = KM.__file__
        exec(compile(mut, KM.__file__, 'exec'), M2.__dict__)
        engel0 = len(ENGEL)
        n_ist = len(sv.istekler)
        with M2.prova_ac(pr):
            go2 = M2.GercekOrtam(log=lambda *a: None)
            os.makedirs(pr.dizin, exist_ok=True)
            try:
                M2.asama_manifest(go2, M2.birimler_kur())
                r5 = 'tamamlandı'
            except Exception as e:      # noqa: BLE001
                r5 = f'{type(e).__name__}: {str(e)[:200]}'
        R.sina(g, 'taban düzeltmesi geri alınınca: ilk ComCat isteği (earthquake.usgs.gov) ad çözümünde reddedildi, '
                  'manifest durdu, sahte sunucuya da istek gitmedi', 'earthquake.usgs.gov' in str(ENGEL[engel0:]) and
               r5 != 'tamamlandı' and len(sv.istekler) == n_ist,
               dict(r=r5, kosu=M2.PROVA_ENGEL[:3], betik=ENGEL[engel0:engel0 + 3]))
        # gerçek kanca kaydından bu beklenen girişimleri ayır
        beklenen_engel = ENGEL[engel0:]
        del ENGEL[engel0:]
        # 6) P-1 (kuru provada bulundu) geri alınırsa: boş zarf deposunda ilk ComCat yanıtı yazılamaz, manifest durur
        eski_s = "    os.makedirs(go.zyol('katalog'), exist_ok=True)   # P-1"
        R.sina(g, 'P-1 dizesi kodda var', kaynak.count(eski_s) == 1)
        M3 = types.ModuleType('tr7c_kosu_mut3')
        M3.__file__ = KM.__file__
        exec(compile(kaynak.replace(eski_s, '    pass   # P-1'), KM.__file__, 'exec'), M3.__dict__)
        pr3 = KM.Prova(dizin=os.path.join(kok, 'c3'), zarf=os.path.join(kok, 'z3'), servis=servis, katalog=katalog)
        n_ist = len(sv.istekler)
        with M3.prova_ac(pr3):
            go3 = M3.GercekOrtam(log=lambda *a: None)
            try:
                M3.asama_manifest(go3, M3.birimler_kur())
                r6 = 'tamamlandı'
            except Exception as e:      # noqa: BLE001
                r6 = f'{type(e).__name__}: {str(e)[:200]}'
        R.sina(g, 'P-1 geri alınınca: boş zarf deposunda ilk ComCat yanıtı yazılamadı, manifest "katalog sorgusu başarısız" '
                  'ile durdu (sahte sunucu isteği aldı; ağ dışına çıkılmadı)', 'katalog sorgusu başarısız' in r6 and
               len(sv.istekler) == n_ist + 1 and len(ENGEL) == engel0, r6)
        shutil.rmtree(kok, ignore_errors=True)
    return dict(taban_mutasyonu_engel=beklenen_engel)


def _reddeder(fn):
    try:
        fn()
    except KM.GercekKipReddedildi:
        return True
    return False


def main():
    cikti = sys.argv[1]
    secim = sys.argv[2].split(',') if len(sys.argv) > 2 else ['dugme', 'S1', 'S2', 'S3']
    os.makedirs(os.path.join(GECICI, 'prova'), exist_ok=True)
    R = Kayit()
    t0 = time.time()
    out = dict(aciklama='TR-7c kuru prova (§B.3): gerçek I/O katmanı 127.0.0.1\'deki sahte FDSN sunucusuna karşı; '
                        'yalnız yapay veri; gerçek kip kapısı açılmadı.',
               kod_sha256={f: KM.sha256_dosya(os.path.join(BURA, f)) for f in ('tr7c_prova.py', 'tr7c_kosu.py')},
               tr7_motor_sha256={os.path.basename(k): KM.sha256_dosya(k) for k in KM.TR7_MOTOR},
               kapi=KM.kosu_dondurulmus_mu(), secim=secim, senaryolar={})
    for s in secim:
        t = time.time()
        try:
            out['senaryolar'][s] = dugme(R) if s == 'dugme' else senaryo(R, s)
        except BaseException as e:     # noqa: BLE001
            import traceback
            R.sina(s, f'çöküş: {type(e).__name__}: {str(e)[:300]}', False, traceback.format_exc()[-3000:])
            out['senaryolar'][s] = dict(cokus=traceback.format_exc()[-3000:])
        out['senaryolar'][s]['sure_toplam_s'] = round(time.time() - t, 1)
    out.update(sinamalar=R.s, gecen=sum(x['gecti'] for x in R.s), toplam=len(R.s),
               hepsi_gecti=all(x['gecti'] for x in R.s), engellenen_betik=ENGEL, engellenen_kosu_kodu=KM.PROVA_ENGEL,
               obspy_git_alt_sureci=len(OBSPY_GIT), sure_s=round(time.time() - t0, 1))
    with open(cikti, 'w', encoding='utf-8') as f:
        f.write(json.dumps(out, ensure_ascii=False, indent=1, default=str) + '\n')
    print(f"{out['gecen']}/{out['toplam']} geçti; {out['sure_s']} sn")


if __name__ == '__main__':
    main()
