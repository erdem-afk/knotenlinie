#!/usr/bin/env python3
"""TR-7 indirme katmanı (ön kayıt sürüm 3 §3.5, §6.1, §10 madde 6): FDSN dataselect / station / event istemcisi.

BU MODÜL KOD İNCELEMESİNDEN ÖNCE GERÇEK SERVİSLERE KARŞI ÇALIŞTIRILMAZ. Koşu kodu (`tr7_kosu.py`) onu aşama aşama çağırır;
sınama (`tr7_test_yapay.py`) yalnız yerel yapay sunucuyla (127.0.0.1) çağırır.

- Servis (§6.1): KO/TL/IJ/6G → KOERI; YH/YL → EarthScope; öteki EIDA ağları → ORFEUS federatör; Parkfield → NCEDC
  (204/404 dönerse EarthScope).
- Nezaket (§6.1): servis başına en çok 2 eşzamanlı akış (semafor), aynı akışta istekler arası ≥ 0,5 sn, genel
  User-Agent (kişi ya da proje adı yok). 429/503: Retry-After (yoksa 30 sn × deneme), en çok 2 yeniden deneme.
  401/403: "kısıtlı" yazılır, atlatılmaz, yeniden denenmez. 204/404: "yok". Öteki 5xx ve zaman aşımı: "servis hatası"
  (aşama düzeyinde tek yeniden deneme turu koşu kodundadır, §10 madde 6).
- 2026 sınırı (§3.6): her istekten ÖNCE başlangıç ve bitiş denetlenir; bitiş ≥ 2026-01-01 (katalogda >
  2025-12-31T23:59:59) ise istek gönderilmeden `SinirIhlali` atılır.
- Ham miniSEED yalnız depo DIŞINDAKİ geçici dizine yazılır (".part" → yeniden adlandırma); sha256 ve bayt döner. Koşu
  kodu işledikten sonra siler (§6.1). Bu modül miniSEED'i ayrıştırmaz.
"""
import datetime as dt
import hashlib
import os
import socket
import ssl
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

UA = 'Mozilla/5.0 (compatible; fdsn-client)'
SERVIS = {
    'koeri': 'https://eida.koeri.boun.edu.tr/fdsnws',
    'eida_federator': 'https://federator.orfeus-eu.org/fdsnws',
    'earthscope': 'https://service.earthscope.org/fdsnws',
    'ncedc': 'https://service.ncedc.org/fdsnws',
}
KATALOG = {
    'comcat': 'https://earthquake.usgs.gov/fdsnws/event/1/query',
    'emsc': 'https://www.seismicportal.eu/fdsnws/event/1/query',
}
KOERI_AG = ('KO', 'TL', 'IJ', '6G')
EARTHSCOPE_AG = ('YH', 'YL')
AKIS = 2
ARALIK_S = 0.5
YENIDEN_429 = 2
BEKLE_429_S = 30.0
ZAMAN_ASIMI_S = 300
SON_AN = dt.datetime(2026, 1, 1)
KATALOG_SON = dt.datetime(2025, 12, 31, 23, 59, 59)


class SinirIhlali(Exception):
    """İstek 2026 sınırını aşıyor: hiçbir bağlantı kurulmadan atılır."""


def zaman(s):
    return s if isinstance(s, dt.datetime) else dt.datetime.fromisoformat(str(s).replace('Z', ''))


def iso(t):
    return zaman(t).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]


def sinir(t0, t1, katalog=False):
    t0, t1 = zaman(t0), zaman(t1)
    if katalog:
        if t1 > KATALOG_SON or t0 > KATALOG_SON:
            raise SinirIhlali(f'katalog sorgusu {t0}–{t1} 2025-12-31T23:59:59\'u aşıyor')
    elif t1 >= SON_AN or t0 >= SON_AN:
        raise SinirIhlali(f'istek {t0}–{t1} 2026-01-01\'i aşıyor')
    if t1 <= t0:
        raise SinirIhlali(f'boş ya da ters aralık {t0}–{t1}')


def servis_sec(ag, kaynak='', parkfield=False):
    """§6.1. kaynak: tr7_istasyon.csv 'kaynak' sütunu."""
    if parkfield:
        return 'ncedc'
    if ag in KOERI_AG:
        return 'koeri'
    if ag in EARTHSCOPE_AG:
        return 'earthscope'
    if 'eida_federator' in kaynak:
        return 'eida_federator'
    return 'earthscope'


def dataselect_url(servis, ag, ist, konum, kanallar, t0, t1, taban=None):
    sinir(t0, t1)
    q = urllib.parse.urlencode(dict(net=ag, sta=ist, loc=konum if konum else '--', cha=','.join(kanallar),
                                    start=iso(t0), end=iso(t1)))
    return f'{(taban or SERVIS)[servis]}/dataselect/1/query?{q}'


def station_url(servis, ag, ist, konum, kanallar, t0, t1, taban=None):
    sinir(t0, t1)
    q = urllib.parse.urlencode(dict(net=ag, sta=ist, loc=konum if konum else '--', cha=','.join(kanallar),
                                    start=iso(t0), end=iso(t1), level='response'))
    return f'{(taban or SERVIS)[servis]}/station/1/query?{q}'


def event_url(katalog, t0, t1, la, lo, yaricap_derece, minmag, taban=None):
    sinir(t0, t1, katalog=True)
    if katalog == 'comcat':
        q = dict(format='csv', starttime=iso(t0), endtime=iso(t1), latitude=f'{la:.4f}', longitude=f'{lo:.4f}',
                 maxradius=f'{yaricap_derece:.4f}', minmagnitude=f'{minmag}', orderby='time-asc')
    elif katalog == 'emsc':
        q = dict(format='text', start=iso(t0), end=iso(t1), lat=f'{la:.4f}', lon=f'{lo:.4f}',
                 maxradius=f'{yaricap_derece:.4f}', minmag=f'{minmag}', orderby='time-asc')
    else:
        raise ValueError(katalog)
    return f'{(taban or KATALOG)[katalog]}?{urllib.parse.urlencode(q)}'


def ssl_baglam():
    ca = os.environ.get('SSL_CERT_FILE') or os.environ.get('REQUESTS_CA_BUNDLE')
    return ssl.create_default_context(cafile=ca) if ca and os.path.exists(ca) else ssl.create_default_context()


class Istemci:
    """Servis başına ≤ 2 akış; aynı akışta istekler arası ≥ 0,5 sn; 429/503 bekleme; 401/403 atlatılmaz."""

    def __init__(self, aralik=ARALIK_S, bekle_429=BEKLE_429_S, uyku=time.sleep, zaman_asimi=ZAMAN_ASIMI_S):
        self.aralik, self.bekle_429, self.uyku, self.zaman_asimi = aralik, bekle_429, uyku, zaman_asimi
        self._sem = {}
        self._son = {}
        self._kilit = threading.Lock()
        self.baglam = ssl_baglam()
        self.gunluk = []

    def _semafor(self, servis):
        with self._kilit:
            if servis not in self._sem:
                self._sem[servis] = threading.BoundedSemaphore(AKIS)
            return self._sem[servis]

    def _nazik(self, servis):
        key = (servis, threading.get_ident())
        son = self._son.get(key)
        if son is not None:
            kalan = self.aralik - (time.monotonic() - son)
            if kalan > 0:
                self.uyku(kalan)
        self._son[key] = time.monotonic()

    def iste(self, servis, url, hedef=None):
        """Dönüş dict(durum, http, bayt, sha256, deneme, hata). hedef verilirse gövde oraya (".part" üzerinden) yazılır;
        verilmezse 'govde' alanında döner (yalnız katalog ve StationXML; dalga formu her zaman dosyaya)."""
        with self._semafor(servis):
            deneme = 0
            while True:
                deneme += 1
                self._nazik(servis)
                r = self._tek(url, hedef)
                r['deneme'] = deneme
                if r['http'] in (429, 503) and deneme <= YENIDEN_429:
                    ra = r.get('retry_after')
                    self.uyku(float(ra) if ra is not None else self.bekle_429 * deneme)
                    continue
                self.gunluk.append(dict(url=url, http=r['http'], bayt=r.get('bayt', 0), durum=r['durum'],
                                        deneme=deneme))
                return r

    def _tek(self, url, hedef):
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        kw = dict(context=self.baglam) if url.startswith('https:') else {}
        try:
            with urllib.request.urlopen(req, timeout=self.zaman_asimi, **kw) as r:
                kod = r.status
                if kod == 204:
                    return dict(durum='yok', http=204, bayt=0)
                h = hashlib.sha256()
                n = 0
                if hedef is not None:
                    with open(hedef + '.part', 'wb') as f:
                        for b in iter(lambda: r.read(1 << 20), b''):
                            f.write(b)
                            h.update(b)
                            n += len(b)
                    os.replace(hedef + '.part', hedef)
                    govde = None
                else:
                    govde = r.read()
                    h.update(govde)
                    n = len(govde)
                if n == 0:
                    if hedef is not None and os.path.exists(hedef):
                        os.remove(hedef)
                    return dict(durum='yok', http=kod, bayt=0)
                return dict(durum='tamam', http=kod, bayt=n, sha256=h.hexdigest(), govde=govde,
                            yol=hedef)
        except urllib.error.HTTPError as e:
            ra = e.headers.get('Retry-After') if e.headers else None
            try:
                ra = float(ra) if ra is not None else None
            except ValueError:
                ra = None
            if e.code in (401, 403):
                d = 'kisitli'
            elif e.code in (204, 404):
                d = 'yok'
            elif e.code == 429 or e.code >= 500:
                d = 'servis_hatasi'
            else:
                d = 'istemci_hatasi'
            return dict(durum=d, http=e.code, bayt=0, retry_after=ra)
        except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError, OSError) as e:
            return dict(durum='servis_hatasi', http=None, bayt=0, hata=f'{type(e).__name__}: {e}')
        finally:
            if hedef is not None and os.path.exists(hedef + '.part'):
                os.remove(hedef + '.part')


def depo_disi(yol, depo):
    """Ham veri ve zarf deposu depo DIŞINDA olmalı (§6.1)."""
    yol, depo = os.path.realpath(yol), os.path.realpath(depo)
    return os.path.commonpath([yol, depo]) != depo


def sha256_dosya(yol):
    h = hashlib.sha256()
    with open(yol, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


# ====================================================================== zarfla (§6.2) — indirilen miniSEED'in işlenmesi
import json  # noqa: E402
import math  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402

import numpy as np  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tr7_cekirdek as K  # noqa: E402


class BicimHata(Exception):
    """miniSEED ya da StationXML ayrıştırılamadı (§10 madde 6: payı %1'i aşarsa koşu durur)."""


def oku_mseed(yol):
    from obspy import read
    try:
        return read(yol, format='MSEED')
    except Exception as e:                           # noqa: BLE001
        raise BicimHata(f'miniSEED ayrıştırılamadı: {type(e).__name__}: {e}') from e


def oku_stationxml(yol):
    from obspy import read_inventory
    try:
        return read_inventory(yol, format='STATIONXML')
    except Exception as e:                           # noqa: BLE001
        raise BicimHata(f'StationXML ayrıştırılamadı: {type(e).__name__}: {e}') from e


_BIT = re.compile(r'(?<!\d)(16|18|20|22|24|26|27|28|30|32)\s*-?\s*bits?\b', re.I)


def bit_sayisi(kanal):
    """§3.5 c: sayısallaştırıcı bit sayısı yalnız StationXML'de açıkça yazılıysa (DataLogger tanımında "24-bit" gibi);
    yoksa None ("bilinmiyor"; §6.2.2'de b = 24). Okuma O-18."""
    dl = getattr(kanal, 'data_logger', None)
    if dl is None:
        return None
    for alan in ('description', 'model', 'type', 'manufacturer'):
        v = getattr(dl, alan, None)
        if v:
            m = _BIT.search(str(v))
            if m:
                return int(m.group(1))
    return None


def yanit_ozeti(inv, ag, ist, konum, kanal, t):
    """§3.5 c ve §6.6: S, fs, b, |H(0,02)|/|H(1)|, PGV uygunluğu, g(f) = |H(f)|/S (f = 2, 4, 6, 8 Hz)."""
    from obspy import UTCDateTime
    sid = f'{ag}.{ist}.{konum}.{kanal}'
    try:
        ch = inv.select(network=ag, station=ist, location=konum, channel=kanal, time=UTCDateTime(K.zaman(t)))
        kan = [c for n in ch for s in n for c in s]
        if not kan or kan[0].response is None or kan[0].response.instrument_sensitivity is None:
            return dict(sid=sid, yanit=False)
        c = kan[0]
        resp = c.response
        S = float(resp.instrument_sensitivity.value)
        h = np.abs(resp.get_evalresp_response_for_frequencies([0.02, 1.0, 2.0, 4.0, 6.0, 8.0], output='VEL'))
    except Exception as e:                           # noqa: BLE001
        return dict(sid=sid, yanit=False, hata=f'{type(e).__name__}: {e}')
    oran = float(h[0] / h[1]) if h[1] > 0 else None
    g = [float(x / S) for x in h[2:]]
    pgv = (kanal[0] in 'BH' and kanal[1] == 'H' and oran is not None and oran >= K.PGV_ORAN)
    return dict(sid=sid, yanit=True, S=S, fs=float(c.sample_rate), b=bit_sayisi(c), oran_002_1=oran,
                pgv_uygun=bool(pgv), g_2_4_6_8=g, g_disinda=any(not (K.G_ARALIK[0] <= x <= K.G_ARALIK[1]) for x in g),
                azimut=c.azimuth, egim=c.dip)


def _parcalar(st, kanal):
    """Kanalın kesintisiz parçaları (obspy merge(method=1) + split; okuma O-19)."""
    s = st.select(channel=kanal).copy()
    if len(s) == 0:
        return []
    s.merge(method=1, fill_value=None)
    s = s.split()
    fs = {round(tr.stats.sampling_rate, 6) for tr in s}
    if len(fs) > 1:
        raise ValueError('örnekleme hızı değişken')
    return sorted(s, key=lambda tr: tr.stats.starttime)


def _ortu(parcalar, a, b):
    return K.ortu([(tr.stats.starttime.timestamp, tr.stats.endtime.timestamp, tr.stats.sampling_rate)
                   for tr in parcalar], a, b)


def _hizala(p1, p2, az1, az2):
    """1/2 → N/E (yatay; StationXML azimutuyla). Yalnız aynı fs'li ve örnek zamanları hizalı ortak bölümler."""
    out = []
    for a in p1:
        for b in p2:
            fs = a.stats.sampling_rate
            if abs(b.stats.sampling_rate - fs) > 1e-6:
                continue
            t0 = max(a.stats.starttime.timestamp, b.stats.starttime.timestamp)
            t1 = min(a.stats.endtime.timestamp, b.stats.endtime.timestamp)
            if t1 <= t0:
                continue
            ia = (t0 - a.stats.starttime.timestamp) * fs
            ib = (t0 - b.stats.starttime.timestamp) * fs
            if abs(ia - round(ia)) > 0.01 or abs(ib - round(ib)) > 0.01:
                continue
            ia, ib = int(round(ia)), int(round(ib))
            n = int(math.floor((t1 - t0) * fs + 1e-6)) + 1
            x1 = a.data[ia:ia + n].astype(np.float64)
            x2 = b.data[ib:ib + n].astype(np.float64)
            r1, r2 = math.radians(az1), math.radians(az2)
            out.append((t0, fs, (x1 * math.cos(r1) + x2 * math.cos(r2), x1 * math.sin(r1) + x2 * math.sin(r2))))
    return out


def _lp_seri(tr, inv, k0, n):
    """§6.2.4: remove_response(VEL, pre_filt, water_level=60), 0,02–0,1 Hz Butterworth (4, sıfır faz), tam saniyelerde
    doğrusal ara değerle örnekleme (okuma O-20). Dönüş eksen üstünde 1 Hz dizi (m/s)."""
    t = tr.copy()
    t.data = K.ortalama_egilim(t.data.astype(np.float64))
    t.remove_response(inventory=inv, output='VEL', pre_filt=K.PRE_FILT, water_level=K.WATER_LEVEL)
    t.filter('bandpass', freqmin=K.BANT_LP[0], freqmax=K.BANT_LP[1], corners=4, zerophase=True)
    ts = t.stats.starttime.timestamp + np.arange(t.stats.npts) / t.stats.sampling_rate
    ks = np.arange(int(math.ceil(ts[0] - 1e-7)), int(math.floor(ts[-1] + 1e-7)) + 1)
    out = np.full(n, np.nan)
    if len(ks):
        K.eksene(k0, n, int(ks[0]), np.interp(ks, ts, t.data), out)
    return out


def isle_istasyon_penceresi(yol, inv, ist, pencere, lp=False, mda=False):
    """Bir istasyon-pencere miniSEED'ini işler (indir–zarfla–sil'in "zarfla" adımı; ham dosyayı silmez).

    ist: dict(ag, istasyon, konum, z_kanal (ör. 'BHZ'), yatay (['BHN','BHE'] ya da ['BH1','BH2']), ozet: {kanal:
         yanit_ozeti}, baz (istasyondan dış merkeze azimut, derece)).
    pencere: dict(R=(r0, r1) epoch, W=(w0, w1) epoch, eksen=(k0, n)) (eksen: [R başı − 600, W sonu + 600]).
    Dönüş dict: dusme (None ya da neden), ortu_R, ortu_W, bilesen, zarf (eZ, eN, eE, C051 eksende), lp (vZ, vR, vT),
    mda (istenirse: bileşen başına parçalar ve W bölgesinde analitik sinyaller, complex64).
    """
    st = oku_mseed(yol)
    k0, n = pencere['eksen']
    R, W = pencere['R'], pencere['W']
    zk = ist['z_kanal']
    oz = ist['ozet']
    try:
        pz = _parcalar(st, zk)
    except ValueError as e:
        return dict(dusme=f'kanal: {e}')
    ortu_R, ortu_W = _ortu(pz, *R), _ortu(pz, *W)
    out = dict(ortu_R=ortu_R, ortu_W=ortu_W, dusme=None)
    if ortu_R < K.ORTU_MIN or ortu_W < K.ORTU_MIN:
        out['dusme'] = 'ortu'
        return out
    if not oz.get(zk, {}).get('yanit'):
        out['dusme'] = 'yanit_yok'
        return out
    # yatay bileşenler: ikisi de var, yanıtlı ve R/W örtüsü ≥ %90 ise (okuma O-5)
    bil = {'Z': [(tr.stats.starttime.timestamp, tr.stats.sampling_rate, tr.data.astype(np.float64)
                  / oz[zk]['S']) for tr in pz]}
    ham = {'Z': pz}
    yat = ist.get('yatay') or []
    if len(yat) == 2 and all(oz.get(c, {}).get('yanit') for c in yat):
        try:
            p1, p2 = _parcalar(st, yat[0]), _parcalar(st, yat[1])
        except ValueError:
            p1, p2 = [], []
        if p1 and p2:
            if yat[0][-1] in '12':
                hz = _hizala([_olcekli(tr, oz[yat[0]]['S']) for tr in p1], [_olcekli(tr, oz[yat[1]]['S'])
                             for tr in p2], oz[yat[0]]['azimut'] or 0.0, oz[yat[1]]['azimut'] or 0.0)
                bN = [(t0, fs, xy[0]) for t0, fs, xy in hz]
                bE = [(t0, fs, xy[1]) for t0, fs, xy in hz]
            else:
                bN = [(tr.stats.starttime.timestamp, tr.stats.sampling_rate, tr.data.astype(np.float64)
                       / oz[yat[0]]['S']) for tr in p1]
                bE = [(tr.stats.starttime.timestamp, tr.stats.sampling_rate, tr.data.astype(np.float64)
                       / oz[yat[1]]['S']) for tr in p2]

            def o(b, a, z):
                return K.ortu([(t0, t0 + (len(x) - 1) / fs, fs) for t0, fs, x in b], a, z)
            if bN and all(o(b, *R) >= K.ORTU_MIN and o(b, *W) >= K.ORTU_MIN for b in (bN, bE)):
                bil['N'], bil['E'] = bN, bE
                ham['N'], ham['E'] = p1, p2
    # kırpılma: kullanılan her bileşende, W içinde ham sayım (okuma O-21)
    for c, trs in ham.items():
        kan = zk if c == 'Z' else (yat[0] if c == 'N' else yat[1])
        bb = oz.get(kan, {}).get('b')
        xw = [tr.slice(_utc(W[0]), _utc(W[1])).data for tr in trs]
        xw = np.concatenate([np.asarray(x, dtype=np.float64) for x in xw if len(x)]) if xw else np.zeros(0)
        if K.kirpilma(xw, bb):
            out['dusme'] = 'kirpilma'
            return out
    out['bilesen'] = ''.join(bil)
    zarf = {}
    mda_d = {}
    Wb_lo, Wb_hi = pencere.get('W_mda', W)
    for c, parcalar in bil.items():
        e28 = np.full(n, np.nan)
        e051 = np.full(n, np.nan)
        md = []
        for t0, fs, x in parcalar:
            x = K.ortalama_egilim(x)
            a28 = K.parca_analitik(x, fs, K.BANT_YUKSEK)
            a051 = K.parca_analitik(x, fs, K.BANT_ALCAK)
            kk, e = K.kutula(t0, fs, np.abs(a28))
            K.eksene(k0, n, kk, e, e28)
            kk, e = K.kutula(t0, fs, np.abs(a051))
            K.eksene(k0, n, kk, e, e051)
            if mda:
                i0 = max(0, int(math.floor((Wb_lo - 5 - t0) * fs)))
                i1 = min(len(x), int(math.ceil((Wb_hi + 5 - t0) * fs)) + 1)
                if i1 > i0:
                    md.append(dict(t0=t0, fs=fs, n=len(x), i0=i0, i1=i1,
                                   a28=a28[i0:i1].astype(np.complex64), a051=a051[i0:i1].astype(np.complex64)))
        zarf['e' + c] = e28.astype(np.float32)
        zarf['d' + c] = e051
        if mda:
            mda_d[c] = md
    dl = [zarf.pop('d' + c) for c in bil]
    zarf['C051'] = K.birlesik(dl).astype(np.float32)
    out['zarf'] = zarf
    if mda:
        out['mda'] = mda_d
    if lp:
        out['lp'] = _lp_yolu(st, inv, ist, zk, yat if 'N' in bil else [], k0, n)
    return out


def _olcekli(tr, S):
    t = tr.copy()
    t.data = t.data.astype(np.float64) / S
    return t


def _utc(e):
    from obspy import UTCDateTime
    return UTCDateTime(float(e))


def _lp_yolu(st, inv, ist, zk, yat, k0, n):
    def seri(kanal):
        out = np.full(n, np.nan)
        for tr in _parcalar(st, kanal):
            s = _lp_seri(tr, inv, k0, n)
            ok = np.isfinite(s)
            out[ok] = s[ok]
        return out
    vZ = seri(zk)
    if len(yat) == 2:
        v1, v2 = seri(yat[0]), seri(yat[1])
        oz = ist['ozet']
        if yat[0][-1] in '12':
            r1, r2 = math.radians(oz[yat[0]]['azimut'] or 0.0), math.radians(oz[yat[1]]['azimut'] or 0.0)
            vN = v1 * math.cos(r1) + v2 * math.cos(r2)
            vE = v1 * math.sin(r1) + v2 * math.sin(r2)
        else:
            vN, vE = v1, v2
        vR, vT = K.rotasyon_ne_rt(vN, vE, ist['baz'])
    else:
        vR = vT = np.full(n, np.nan)
    return dict(vZ=vZ.astype(np.float32), vR=np.asarray(vR, np.float32), vT=np.asarray(vT, np.float32))


def zarf_yaz(yol, k0, sonuc, meta):
    """Zarf deposuna (depo dışı) npz: float32 1 Hz seriler + meta (JSON). 'x' kipi: üzerine yazılmaz."""
    d = dict(k0=np.int64(k0), meta=np.array(json.dumps(meta, ensure_ascii=False, sort_keys=True)))
    for k, v in (sonuc.get('zarf') or {}).items():
        d[k] = np.asarray(v, np.float32)
    for k, v in (sonuc.get('lp') or {}).items():
        d[k] = np.asarray(v, np.float32)
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    with open(yol, 'xb') as f:
        np.savez(f, **d)
    return sha256_dosya(yol)


def zarf_oku(yol, sha=None):
    if sha is not None and sha256_dosya(yol) != sha:
        raise BicimHata(f'zarf deposu sha256 uyuşmuyor: {yol}')
    with np.load(yol, allow_pickle=False) as z:
        d = {k: z[k] for k in z.files}
    d['meta'] = json.loads(str(d['meta']))
    d['k0'] = int(d['k0'])
    return d
