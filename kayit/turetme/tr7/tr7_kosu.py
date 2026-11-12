#!/usr/bin/env python3
"""TR-7 tek koşu kodu (ön kayıt sürüm 3, DONDURULDU; sha256 df426ffc59793dcb75e5167aca643145d3bd55be3bb4bdcce11f58e1ea544c20).

BU KOD KOD İNCELEMESİNDEN ("koşulabilir" hükmü) ÖNCE GERÇEK VERİYE KARŞI ÇALIŞTIRILMAZ (§10 madde 2).

Sıra (§7, §10): KD (yapay; `kd`) → kod incelemesi → manifest → K1-indirme → K1-negatif → K1-algılama →
Marmara-indirme → Marmara-negatif → Marmara-algılama → hüküm.

Aşama mekanizması (§10 madde 6; kodlayıcı okuması O-30): kod kendisi commit/push YAPMAZ.
  1. `baslat <aşama>`: önkoşulları (önceki aşama tamam, KD geçti, girdi sha256'ları) denetler, kuru provayı koşar
     (yapay değerlerle; veriye bağlı olmayan her kurulum burada), `TR7_KOSU_DURUM.json`'a aşamayı "başladı" yazar ve
     depo dışı bekçi dosyasına (`TR7_GERCEK_KOSU_BASLADI`) ekler. Sonra durur ve commit + push ister.
  2. `kos <aşama>`: `git` ile durum dosyasının HEAD'deki hâlinin çalışma kopyasıyla aynı olduğunu, aşamayı "başladı"
     gösterdiğini ve HEAD'in uzak dala push edildiğini (`git ls-remote` + `merge-base --is-ancestor`) doğrular; değilse
     durur ve ne yapılacağını yazar. Doğrulanırsa aşamayı koşar, çıktıları yazar, durumu "tamamlandı" yapar (bu değişiklik
     sonraki `baslat`tan önce çıktılarla birlikte commit edilir).
  3. Duran aşama: `durdu <aşama> --neden "..."` durma nedenini kayda yazar (commit + push), sonra `kos <aşama>
     --surdur`. Algılama aşamaları (K1-negatif, K1-algılama, Marmara-negatif, Marmara-algılama) kaldığı pencereden
     sürdürülür; yazılmış algılama ve MDA satırları yeniden hesaplanmaz. Algılama aşamasına bir kez girildiyse
     baştan koşulmaz (§7.2 uygulama hatası yolu dışında: `--uygulama-hatasi-yolu`, yalnız K1-algılama, bir kez).

Çıktılar (depoda, `kayit/turetme/tr7/`): TR7_KOSU_DURUM.json, tr7_kd.json, tr7_manifest.json, tr7_indirme_<aşama>.jsonl
(istek, HTTP, bayt, miniSEED sha256, örtü), tr7_zarf_sha256.jsonl, tr7_k0_tam.json, tr7_algilama_<aşama>.jsonl,
tr7_mda.csv, tr7_k1.json, tr7_marmara_algilama.json, tr7_sonuc.json, tr7_sonuc.md. Depo dışında
(`/mnt/project-files/turetme/tr7-zarf/`): ham miniSEED (geçici, işlendikten sonra silinir), 1 Hz zarflar (npz), katalog ve
StationXML yanıtları, bekçi dosyası.

Kullanım (depo kökünden):
  python3 -I -B kayit/turetme/tr7/tr7_kosu.py kd [--paralel 4]
  python3 -I -B kayit/turetme/tr7/tr7_kosu.py baslat <aşama>
  python3 -I -B kayit/turetme/tr7/tr7_kosu.py kos <aşama> [--surdur]
  python3 -I -B kayit/turetme/tr7/tr7_kosu.py durdu <aşama> --neden "..."
  python3 -I -B kayit/turetme/tr7/tr7_kosu.py k0          (indirmesiz: dondurulmuş listeden önsayım yeniden üretimi)
Çıkış kodları: 0 tamam; 2 KosuDur (girdi, biçim, sınır, önkoşul); 3 KD kaldı; 5 commit/push doğrulanamadı.
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import os
import subprocess
import sys
import time

import numpy as np

BURA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURA)
import tr7_cekirdek as K  # noqa: E402
import tr7_indir as I  # noqa: E402

DEPO = os.path.abspath(os.path.join(BURA, '..', '..', '..'))
ONKAYIT = os.path.join(DEPO, 'kayit', 'onkayit', 'TR-7_tetiklenmis-tremor_ONKAYIT.md')
ONKAYIT_SHA = 'df426ffc59793dcb75e5167aca643145d3bd55be3bb4bdcce11f58e1ea544c20'
ZARF_VARSAYILAN = '/mnt/project-files/turetme/tr7-zarf'
BEKCI_AD = 'TR7_GERCEK_KOSU_BASLADI'
DURUM_AD = 'TR7_KOSU_DURUM.json'

# §3 ve §18–§19'da sha256'sı verilen dosyalar (bu metnin parçası; uyuşmazlık koşuyu durdurur, §10 madde 6)
DONDURULMUS = {
    'tr7_dondurulan_liste.csv': '0f3cbd36876a46354b46355016f949f113ddaadcce4d26b6bc9e7a0b1da4358b',
    'tr7_parkfield_liste.csv': '9dca3380815196a8db15a8a5929441d38dd9b07fd7ed982845543e179957b2b8',
    'tr7_parkfield_varlik.csv': '951d7797fcbb2d4427f43f35e3b0a2ceec46e8a684421f535be70371fd5305d0',
    'tr7_negatif_pencere.csv': 'ae4fa9c1d84ff3a461c9659ffc58c5a366f82671e1df74233cb3283253a6a59b',
    'tr7_negatif_pencere_ozet.json': '16ac030f9370bc528dd0bf9669328bada317acf50481d7db76680e1b5adbcbc8',
    'tr7_e1_maske.csv': 'aef412df1d805fbbee65c1d4f7a76df67ce9b43ec9ee2a8bb3f1345bffccf391',
    'tr7_e1_maske_ozet.json': '128720470ea39479108329960f605bc49f3795e19f50c410bfefd1d9b1a13e7c',
    'tr7_onkayit_sayilar.json': 'be439bf6dec47e309671c382325f5266b69ee60949cb4cdac2d920c630452728',
    'tr7_onkayit_sayilar3.json': '0ca41dcc21d47f92775613dc10889ee34d2398713b866d23689072d38784e4bd',
    'tr7_istasyon.csv': 'a7bb0892d3fb19d1ea0b882857bf1be6340ea3600f61586edcf0da56e4050db7',
    'tr7_tetikleyici.csv': 'dec0cdd0b0b441ae792a98564d55164edd2bb858a0b7eebf235e6355f95ceb8c',
    'tr7_varlik.csv': 'a795a7f98198e6c20b1b24bca282dabb35addc9c50023694379110d8c90d48e8',
    'tr7_varlik_ozet.json': '621791d083c071f0c53617a26dd65ae513a9f3a6f20d72140006af17510d174d',
    'tr7_parkfield_varlik_ozet.json': '71be3c1b52d78c6656bf43f64f9dec96b6a33de89b35464e3b3a898b085cce12',
}
# KD'nin referans betikleri (§7.1). denetim2/yapay'ın sha256'sı metinde yok: kodlayıcı depodaki hâlini sabitledi (O-31).
REFERANS = {
    'tr7_onkayit_yapay.py': 'c77ffc0ba48719444ef6d4040bac38483b7e3b76bf7ecd8adc35ce47d338abb0',
    'tr7_onkayit_denetim2.py': 'dcf4acc510d318c3bfe9240978750bf03890b0d4ec79c6ccd67a36d771578998',
    'tr7_onkayit_denetim3.py': '0b4d6f90e5f429da3d585eab83b6bdeafcd9b6b57b707c6448e46831f4192fae',
    'tr7_onkayit_d12c.py': '1ca3678d4e6ea879778d9335437231cd6895aea7f25900ac06aced31a9d75ad2',
    'tr7_inc2_taban.py': '43cab6187e3fabd3a6ea28776ae21de309fe3924d9fc2dbfeab8c53c4a3d085b',
    'tr7_inc2_taban_ek.py': '7e73fc5fed62eb1706b33ca321a739413e4f70bb7a787ee20f9e9ebdf254cdff',
}
KOD_DOSYALARI = ('tr7_cekirdek.py', 'tr7_indir.py', 'tr7_kosu.py')

ASAMALAR = ('manifest', 'K1-indirme', 'K1-negatif', 'K1-algılama', 'Marmara-indirme', 'Marmara-negatif',
            'Marmara-algılama', 'hüküm')
ALGILAMA_ASAMALARI = ('K1-negatif', 'K1-algılama', 'Marmara-negatif', 'Marmara-algılama')
INDIRME_ASAMALARI = ('K1-indirme', 'K1-negatif', 'Marmara-indirme', 'Marmara-negatif')

TOHOKU = 'official20110311054624120_30'
WHARTON = ('official20120411083836720_20', 'usp000jhjb')
KAHRAMANMARAS = ('us6000jllz', 'us6000jlqa')
K1_ARALIK = (dt.datetime(2011, 3, 11, 6, 16, 1), dt.datetime(2011, 3, 11, 6, 31, 48))   # §7.2 (b), kapsayıcı
PK_TAU_KABA = 27.12                                       # §3.2 (tr7_onkayit_sayilar.json parkfield.tau_kaba_kpa)
PKD = ('BK', 'PKD')
BAGIMSIZ_SEG = ('S5', 'S6')                               # §8: bağımsız satır yalnız 2009 sonrası birimler
BAGIMSIZ_BAS = dt.datetime(2009, 1, 1)
SERVIS_HATA_PAY, BICIM_HATA_PAY = 0.10, 0.01              # §10 madde 6
YENIDEN_DENEME_BEKLE_S = 600.0
FAR_PK_ESIK, N_PK_MIN = 0.30, 5                           # §7.2 (b)
A90_PK_TAVAN = 1e5                                        # 100 µm/s = 1e5 nm/s
BPRIME_MASKE_S, BPRIME_FAZ = 5, (-10, 120)                # §7.2 (b′)
PK_MDA_BAS = 3


class KosuDur(Exception):
    """Girdi, biçim, sınır ya da önkoşul sorunu: koşu durur; 'veri yok' yazılmaz."""


class GitDogrulanamadi(KosuDur):
    pass


# ====================================================================== yardımcılar
def sha256_dosya(yol):
    return I.sha256_dosya(yol)


def simdi():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')


def json_yaz_x(yol, nesne):
    with open(yol, 'x', encoding='utf-8') as f:
        f.write(json.dumps(nesne, ensure_ascii=False, indent=1, default=_jv) + '\n')


def json_yaz(yol, nesne):
    tmp = yol + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(json.dumps(nesne, ensure_ascii=False, indent=1, default=_jv) + '\n')
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, yol)


def satir_ekle(yol, nesne):
    """jsonl günlüğüne bir satır (fsync): çökme yazılmış satırları kaybettirmez."""
    with open(yol, 'a', encoding='utf-8') as f:
        f.write(json.dumps(nesne, ensure_ascii=False, sort_keys=True, default=_jv) + '\n')
        f.flush()
        os.fsync(f.fileno())


def jsonl_oku(yol):
    if not os.path.exists(yol):
        return []
    out = []
    with open(yol, encoding='utf-8') as f:
        for s in f:
            s = s.strip()
            if s:
                out.append(json.loads(s))
    return out


def _jv(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (dt.datetime, dt.date)):
        return o.isoformat()
    if isinstance(o, (set, tuple)):
        return list(o)
    raise TypeError(type(o))


def say(x, n=2):
    """Türkçe ondalık virgülle sabit basamak."""
    if x is None:
        return '—'
    if isinstance(x, str):
        return x
    return f'{x:.{n}f}'.replace('.', ',')


def anlamli(x, n=3):
    """3 anlamlı basamak, üssüz, ondalık virgül (A değerleri, nm/s)."""
    if isinstance(x, str) or x is None:
        return x if x is not None else '—'
    if x == 0:
        return '0'
    b = n - 1 - int(math.floor(math.log10(abs(x))))
    return f'{round(x, b):.{max(0, b)}f}'.replace('.', ',')


class Ortam:
    """Yollar ve (yalnız sınamada değiştirilebilen) dış uç noktalar. Gerçek koşu varsayılanlarla kurulur."""

    def __init__(self, tr7=BURA, depo=DEPO, zarf=ZARF_VARSAYILAN, servis=None, katalog=None, uyku=time.sleep,
                 aralik=I.ARALIK_S, bekle_429=I.BEKLE_429_S, yeniden_bekle=YENIDEN_DENEME_BEKLE_S,
                 dondurulmus=None, git_dogrula=True, log=print):
        self.tr7, self.depo, self.zarf = tr7, depo, zarf
        self.servis, self.katalog = servis, katalog
        self.uyku, self.aralik, self.bekle_429, self.yeniden_bekle = uyku, aralik, bekle_429, yeniden_bekle
        self.dondurulmus = DONDURULMUS if dondurulmus is None else dondurulmus
        self.git_dogrula = git_dogrula
        self.log = log

    def yol(self, ad):
        return os.path.join(self.tr7, ad)

    def zyol(self, *p):
        return os.path.join(self.zarf, *p)

    def istemci(self):
        return I.Istemci(aralik=self.aralik, bekle_429=self.bekle_429, uyku=self.uyku)


# ====================================================================== girdiler (yalnız okunur, yeniden kurulmaz)
def girdi_denetimi(o):
    """§3.5 (a) ve §10 madde 6: §3 dosyalarının sha256'ları; ön kayıt metni; uyuşmazlık KosuDur (biçim hatası)."""
    out = {}
    for ad, beklenen in o.dondurulmus.items():
        y = o.yol(ad)
        if not os.path.exists(y):
            raise KosuDur(f'girdi yok: {ad}')
        s = sha256_dosya(y)
        if s != beklenen:
            raise KosuDur(f'sha256 uyuşmuyor: {ad} ({s} ≠ {beklenen}); §10 madde 6: koşu durur')
        out[ad] = s
    if o.tr7 == BURA:
        s = sha256_dosya(ONKAYIT)
        if s != ONKAYIT_SHA:
            raise KosuDur(f'ön kayıt metninin sha256\'sı uyuşmuyor ({s})')
        out['TR-7_tetiklenmis-tremor_ONKAYIT.md'] = s
    return out


def kod_sha():
    return {f: sha256_dosya(os.path.join(BURA, f)) for f in KOD_DOSYALARI}


def json_oku(yol):
    with open(yol, encoding='utf-8') as f:
        return json.load(f)


def metin_oku(yol):
    with open(yol, encoding='utf-8') as f:
        return f.read()


def csv_oku(yol):
    with open(yol, encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def birim_ad(o):
    return 'WHARTON2012' if o in WHARTON else o


def dunya_yukle(o):
    """Dondurulmuş listelerden pencereler (yeniden kurulmaz; §0 son cümle)."""
    girdi = girdi_denetimi(o)
    mar = csv_oku(o.yol('tr7_dondurulan_liste.csv'))
    pk = csv_oku(o.yol('tr7_parkfield_liste.csv'))
    pkv = csv_oku(o.yol('tr7_parkfield_varlik.csv'))
    neg = csv_oku(o.yol('tr7_negatif_pencere.csv'))
    e1 = csv_oku(o.yol('tr7_e1_maske.csv'))
    ist_csv = {(r['ag'], r['istasyon']): r for r in csv_oku(o.yol('tr7_istasyon.csv'))}
    olay = {}
    for r in mar:
        olay.setdefault(r['tetikleyici'], dict(id=r['tetikleyici'], birim=r['birim'], t0=K.zaman(r['t0']),
                                               M=float(r['M']), la=float(r['ev_enlem']), lo=float(r['ev_boylam']),
                                               kahramanmaras=r['kahramanmaras'] == '1', tau={}))
        olay[r['tetikleyici']]['tau'][r['segment']] = float(r['tau_kaba_kpa'])
    # tetikleyici pencereleri: tetikleyici başına bir pencere, segment başına istasyon listesi (iz_sira sırasıyla)
    pen = {}
    for r in mar:
        p = pen.setdefault(f"tet|{r['tetikleyici']}", dict(
            id=f"tet|{r['tetikleyici']}", tur='tet', bolge='Marmara', birim=r['birim'], tetikleyici=r['tetikleyici'],
            t0=olay[r['tetikleyici']]['t0'], kayma=0, seg={}, ist={}, tani=[],
            ev=(olay[r['tetikleyici']]['la'], olay[r['tetikleyici']]['lo'])))
        loc, cha = (r['yoklama_kanal'].split('.') if '.' in r['yoklama_kanal'] else ('', r['yoklama_kanal']))
        key = (r['ag'], r['istasyon'])
        p['ist'].setdefault(key, dict(ag=r['ag'], istasyon=r['istasyon'], konum=loc, z_kanal=cha,
                                      la=float(r['ist_enlem']), lo=float(r['ist_boylam']),
                                      d_km=float(r['uzaklik_km']), R=(K.zaman(r['R_bas']), K.zaman(r['R_son'])),
                                      W=(K.zaman(r['W_bas']), K.zaman(r['W_son'])),
                                      kaynak=ist_csv.get(key, {}).get('kaynak', '')))
        p['seg'].setdefault(r['segment'], []).append((int(r['iz_sira']), key))
    for p in pen.values():
        for s in p['seg']:
            p['seg'][s] = [k for _, k in sorted(p['seg'][s])]
    # Parkfield–Tohoku penceresi: var_R = var_W = 1 olan istasyonlar iz_sira ile (§3.2); BK.PKD tanı için ayrıca
    th = olay[TOHOKU]
    pkk = {(r['ag'], r['istasyon']): (r['konum'], r['kanal']) for r in pkv}
    pp = dict(id='pk|tohoku', tur='tet', bolge='Parkfield', birim='PARKFIELD_TOHOKU', tetikleyici=TOHOKU, t0=th['t0'],
              kayma=0, seg={'PK': []}, ist={}, tani=[], ev=(th['la'], th['lo']))
    for r in sorted(pk, key=lambda r: (int(r['iz_sira']) if r['iz_sira'] else 10 ** 6)):
        key = (r['ag'], r['istasyon'])
        loc, cha = pkk.get(key, ('', r['kanallar'].split()[0].split('.')[-1]))
        d = dict(ag=r['ag'], istasyon=r['istasyon'], konum=loc, z_kanal=cha, la=float(r['enlem']),
                 lo=float(r['boylam']), d_km=float(r['uzaklik_km']), R=(th['t0'] - dt.timedelta(seconds=3600),
                                                                       th['t0']),
                 W=(K.zaman(r['W_bas']), K.zaman(r['W_son'])), kaynak='', parkfield=True)
        if r['var_R'] == '1' and r['var_W'] == '1':
            pp['ist'][key] = d
            pp['seg']['PK'].append(key)
        if key == PKD:
            pp['ist'][key] = d
            pp['tani'].append(key)
    pen['pk|tohoku'] = pp
    # negatif pencereler: tam gün kaydırma (R ve W birlikte; Wharton'ın iki penceresi aynı d ile)
    for r in neg:
        d = int(r['d_gun'])
        kay = dt.timedelta(days=d)
        if r['bolge'] == 'Parkfield':
            b = pen['pk|tohoku']
            pid = f"pkneg|{r['sira']}"
            pen[pid] = _kaydir(b, pid, kay, d, r)
        else:
            for tp in [x for x in list(pen.values()) if x['tur'] == 'tet' and x['bolge'] == 'Marmara'
                       and x['birim'] == r['birim']]:
                pid = f"neg|{r['birim']}|{r['sira']}|{tp['tetikleyici']}"
                pen[pid] = _kaydir(tp, pid, kay, d, r)
    for p in pen.values():
        for x in p['ist'].values():
            K.sinir_denetle(x['W'][1] + dt.timedelta(seconds=K.DOLGU_S))
    derinlik = {r['id']: float(r['derinlik_km']) for r in csv_oku(o.yol('tr7_tetikleyici.csv'))}
    for x in olay.values():
        x['derinlik'] = derinlik.get(x['id'], 0.0)
    return dict(girdi=girdi, olay=olay, pen=pen, e1=e1, neg=neg, ist_csv=ist_csv)


def _kaydir(b, pid, kay, d, r):
    p = dict(b, id=pid, tur='neg', t0=b['t0'] + kay, kayma=d, sira=int(r['sira']), seg=dict(b['seg']), tani=[],
             ist={k: dict(x, R=(x['R'][0] + kay, x['R'][1] + kay), W=(x['W'][0] + kay, x['W'][1] + kay))
                  for k, x in b['ist'].items() if k in {kk for v in b['seg'].values() for kk in v}})
    return p


def pencere_ekseni(p, keys=None):
    """(pencere) ekseni: [floor(R başı − 600), ceil(max W sonu + 600)) epoch saniye."""
    xs = [p['ist'][k] for k in (keys or p['ist'])]
    k0 = int(math.floor(K.epoch(min(x['R'][0] for x in xs)) - K.DOLGU_S))
    k1 = int(math.ceil(K.epoch(max(x['W'][1] for x in xs)) + K.DOLGU_S))
    return k0, k1 - k0


def ist_pencere(x, k0, n):
    """İstasyon için R ve W (epoch) ve eksen; R saniyeleri [ceil(R0), floor(R1)), W [W0, W1) (okuma O-22)."""
    return dict(R=(K.epoch(x['R'][0]), K.epoch(x['R'][1])), W=(K.epoch(x['W'][0]), K.epoch(x['W'][1])),
                eksen=(k0, n))


def eksen_dilim(x, k0):
    R = (int(math.ceil(K.epoch(x['R'][0]) - 1e-9)) - k0, int(math.floor(K.epoch(x['R'][1]) + 1e-9)) - k0)
    W = (int(round(K.epoch(x['W'][0]))) - k0, int(round(K.epoch(x['W'][1]))) - k0)
    return R, W


# ====================================================================== durum dosyası ve git doğrulaması
def durum_oku(o):
    y = o.yol(DURUM_AD)
    if not os.path.exists(y):
        return dict(onkayit_sha256=ONKAYIT_SHA, asamalar={}, durmalar=[], uygulama_hatasi_yolu=None)
    with open(y, encoding='utf-8') as f:
        return json.load(f)


def _git(o, *args, check=True):
    r = subprocess.run(['git', '-C', o.depo] + list(args), capture_output=True, text=True)
    if check and r.returncode != 0:
        raise GitDogrulanamadi(f'git {" ".join(args)} başarısız: {r.stderr.strip()}')
    return r


def git_dogrula(o, asama):
    """§10 madde 6: aşama başlamadan önce durum dosyası commit + push edilmiş olmalı. Kod commit/push yapmaz."""
    rel = os.path.relpath(o.yol(DURUM_AD), o.depo)
    ne = (f'Yapılacak: git -C {o.depo} add {rel} && git -C {o.depo} commit -m "TR-7 aşama başlıyor: {asama}" && '
          f'git -C {o.depo} push; sonra aynı `kos {asama}` komutunu yineleyin.')
    if _git(o, 'ls-files', '--error-unmatch', rel, check=False).returncode != 0:
        raise GitDogrulanamadi(f'{rel} depoda izlenmiyor (commit edilmemiş). {ne}')
    if _git(o, 'diff', '--quiet', 'HEAD', '--', rel, check=False).returncode != 0:
        raise GitDogrulanamadi(f'{rel} çalışma kopyası HEAD ile aynı değil (commit edilmemiş değişiklik). {ne}')
    icerik = _git(o, 'show', f'HEAD:{rel}').stdout
    d = json.loads(icerik)
    a = d.get('asamalar', {}).get(asama)
    if not a or a.get('durum') not in ('başladı', 'sürdürülüyor'):
        raise GitDogrulanamadi(f'HEAD\'deki durum dosyası "{asama}" aşamasını başlamış göstermiyor. Önce `baslat {asama}`.')
    ust = _git(o, 'rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{u}', check=False)
    if ust.returncode != 0:
        raise GitDogrulanamadi(f'dalın uzak izleme dalı yok (push edilmemiş). {ne}')
    uzak, dal = ust.stdout.strip().split('/', 1)
    ls = _git(o, 'ls-remote', uzak, f'refs/heads/{dal}', check=False)
    if ls.returncode != 0 or not ls.stdout.strip():
        raise GitDogrulanamadi(f'uzak dal okunamadı ({uzak} {dal}); push doğrulanamadı. {ne}')
    uzak_sha = ls.stdout.split()[0]
    bas = _git(o, 'rev-parse', 'HEAD').stdout.strip()
    if uzak_sha != bas and _git(o, 'merge-base', '--is-ancestor', bas, uzak_sha, check=False).returncode != 0:
        raise GitDogrulanamadi(f'HEAD ({bas[:12]}) uzak dalda ({uzak_sha[:12]}) yok: push edilmemiş. {ne}')
    return dict(head=bas, uzak=uzak_sha, dosya=rel)


def bekci_yaz(o, satir):
    os.makedirs(o.zarf, exist_ok=True)
    with open(o.zyol(BEKCI_AD), 'a', encoding='utf-8') as f:
        f.write(json.dumps(satir, ensure_ascii=False) + '\n')
        f.flush()
        os.fsync(f.fileno())


def onkosul(o, asama, d, surdur=False, uygulama_hatasi=False):
    i = ASAMALAR.index(asama)
    a = d['asamalar']
    if asama.startswith('Marmara'):
        k1 = a.get('K1-algılama', {}).get('k1_dal')
        if k1 not in ('b', "b'"):
            raise KosuDur(f'K1 dalı {k1}: §7.2 — (b) ve (b′) dışında Marmara verisi indirilmez')
    if asama == 'hüküm' and a.get('K1-algılama', {}).get('durum') == 'tamamlandı' \
            and a['K1-algılama'].get('k1_dal') not in ('b', "b'"):
        pass                                       # K1 kaldı: Marmara aşamaları koşulmaz (§7.2), hüküm doğrudan
    elif i > 0 and a.get(ASAMALAR[i - 1], {}).get('durum') != 'tamamlandı':
        raise KosuDur(f'önceki aşama "{ASAMALAR[i - 1]}" tamamlanmamış')
    mevcut = a.get(asama)
    if mevcut:
        if mevcut.get('durum') == 'tamamlandı':
            if uygulama_hatasi and asama == 'K1-algılama' and d.get('uygulama_hatasi_yolu') is None \
                    and mevcut.get('k1_dal') in ('c', 'd'):
                return 'uygulama_hatasi'
            raise KosuDur(f'"{asama}" zaten tamamlandı (tek koşu)')
        if asama in ALGILAMA_ASAMALARI and not surdur:
            raise KosuDur(f'"{asama}" algılama aşamasına daha önce girildi: yalnız durma nedeni kayda geçtikten sonra '
                          f'`durdu` + `kos --surdur` ile kaldığı pencereden sürdürülür (§10 madde 6)')
        if surdur and not any(x['asama'] == asama for x in d['durmalar']):
            raise KosuDur('sürdürme için önce `durdu <aşama> --neden ...` ile durma nedeni kayda geçmeli')
        return 'surdur'
    return 'yeni'


# ====================================================================== KD (§7.1): yalnız yapay veri, koşu kodunun kendi fonksiyonları
# 100 Hz, Butterworth (obspy), numpy Hilbert, 1 sn kutu, float32 zarf; R 3600 sn, W 1900 sn; iki yanda indirme dolgusu
# gibi 600/620 sn (zincirin parça kenarı kırpması dolguya düşer; okuma O-23). Tohumlar: 20261112 + 900 + i ve 9090 + i.
KD_FS = 100.0
KD_ON, KD_R, KD_W, KD_SON = 600, 3600, 1900, 620
KD_T = KD_ON + KD_R + KD_W + KD_SON
KD_N = int(KD_T * KD_FS)
KD_RI = (KD_ON, KD_ON + KD_R)
KD_WI = (KD_ON + KD_R, KD_ON + KD_R + KD_W)


def kd_tohum(i, k):
    return 20261112 + 900 + i if k == 0 else 9090 + i


_KD = {}


def _kd():
    if not _KD:
        _KD['t'] = np.arange(KD_N) / KD_FS
        _KD['F'] = np.fft.rfftfreq(KD_N, 1 / KD_FS)
        _KD['kt'] = K.Kutulayici(0.0, KD_FS, KD_N)
    return _KD


def _bw2(F, lo, hi, n=4):
    with np.errstate(divide='ignore'):
        return 1 / (1 + (lo / np.maximum(F, 1e-9)) ** (2 * n)) / (1 + (F / hi) ** (2 * n))


def _rms(x, m=None):
    x = x if m is None else x[m]
    return float(np.sqrt(np.mean(x ** 2)))


def kd_yanit(ad, F):
    if ad is None:
        return None
    if ad == 'jeofon4.5':
        fn, z = 4.5, 0.7
        return -F ** 2 / (fn ** 2 - F ** 2 + 2j * z * fn * F)
    if ad == 'bh20':
        return 1 / np.sqrt(1 + (F / 7.0) ** 20) + 0j
    raise ValueError(ad)


def kd_gurultu(rng, tur='gauss', profil=None):
    """Bileşen başına (2–8 Hz, 0,5–1 Hz) analitik gürültü; her bant RMS 1 (referansla aynı model)."""
    D = _kd()
    x = K.ortalama_egilim(rng.standard_normal(KD_N))
    y = K.parca_analitik(x, KD_FS, K.BANT_YUKSEK)
    y /= _rms(y.real)
    d = K.parca_analitik(x, KD_FS, K.BANT_ALCAK)
    d /= _rms(d.real)
    if tur == 'kentsel':
        z = np.fft.irfft(np.fft.rfft(rng.standard_normal(KD_N)) * _bw2(D['F'], 1e-6, 1 / 300.0), KD_N)
        y *= np.exp(0.35 * z / z.std())
    if profil is not None:
        y *= profil
    return y.astype(np.complex64), d.astype(np.complex64)


def kd_sinyal(rng, env, sekil='bant28', norm=None, H=None):
    D = _kd()
    w = rng.standard_normal(KD_N) * env
    if sekil == 'bant28':
        S = K.bant_gecir(w, KD_FS, 2, 8)
    elif sekil == 'duz':
        S = K.bant_gecir(w, KD_FS, 0.5, 8)
    elif sekil == 'koda':
        S = np.fft.irfft(np.fft.rfft(K.bant_gecir(w, KD_FS, 0.5, 8)) / np.maximum(D['F'], 0.5), KD_N)
    else:
        raise ValueError(sekil)
    y0 = K.parca_analitik(S, KD_FS, K.BANT_YUKSEK)
    m = env > 0 if norm is None else norm
    k = 1 / _rms(y0.real, m)
    if H is not None:
        S = np.fft.irfft(np.fft.rfft(S) * kd_yanit(H, D['F']), KD_N)
    return ((K.parca_analitik(S, KD_FS, K.BANT_YUKSEK) * k).astype(np.complex64),
            (K.parca_analitik(S, KD_FS, K.BANT_ALCAK) * k).astype(np.complex64))


def kd_C(nl, sl, A, bant):
    D = _kd()
    es = []
    for n, s in zip(nl, sl):
        g = np.abs(n[bant] + (A * s[bant] if s is not None else 0))
        k0, e = D['kt'](g)
        es.append(K.eksene(0, KD_T, k0, e))
    return K.f32(K.birlesik(es))


def kd_istasyonlar(rng, n_ist, env, A, sekil='bant28', gtur='gauss', norm=None, H=None, kayma=None, profil=None):
    st = []
    for i in range(n_ist):
        e = env if kayma is None else np.roll(env, int(round(kayma[i] * KD_FS)))
        nl = [kd_gurultu(rng, gtur, profil) for _ in range(3)]
        sl = [kd_sinyal(rng, e, sekil, norm, H) for _ in range(3)] if A else [None] * 3
        st.append((nl, sl))
    return st


def kd_pencere(st, A, maske=None, yanlis=True):
    maske = np.zeros(KD_T, bool) if maske is None else maske
    ist = [K.istasyon(kd_C(nl, sl, A, 0), kd_C(nl, sl, A, 1), KD_RI, KD_WI, maske) for nl, sl in st]
    return K.pencere_algila(ist, maske, KD_WI, yanlis=yanlis), ist


def _tt(bas):
    return _kd()['t'] - (KD_ON + KD_R + bas)


def kd_zarf(tur, bas, rng=None):
    tt = _tt(bas)
    if tur == 'yarim':
        return K.tremor_zarfi(tt)
    e = np.zeros(KD_N)
    m = (tt >= 0) & (tt < 300)
    if tur == 'sabit':
        e[m] = np.minimum(1, np.minimum(tt[m], 300 - tt[m]) / 10)
        return e
    if tur == 'patlama':
        k = 0.0
        while True:
            k += rng.exponential(15)
            d = rng.uniform(5, 15)
            if k + d > 300:
                break
            mm = (tt >= k) & (tt < k + d)
            e[mm] = np.minimum(1, np.minimum(tt[mm] - k, k + d - tt[mm]) / 2.0)
            k += d
        return e
    raise ValueError(tur)


def kd_deprem(bas, sp, p_oran, sonum=5.0):
    tt = _tt(bas)
    return (np.where(tt >= 0, p_oran * np.exp(-np.maximum(tt, 0) / sonum), 0)
            + np.where(tt >= sp, np.exp(-np.maximum(tt - sp, 0) / sonum), 0))


def kd_ilk5(bas):
    tt = _tt(bas)
    return (tt >= 0) & (tt < 5)


def _oran(x):
    return round(float(np.mean(x)), 3) if len(x) else None


def _sag(r, kural):
    return K.sag_kalan(r['kumeler'], kural)


TAMK = K.TAM


def kd_D2(rng, n, n_ist, Aler):
    """D1/D2/D3: A_etkin basamakları; tam algılama (tutarlılık + ayıklama)."""
    P = np.zeros(len(Aler))
    Ptut = np.zeros(len(Aler))
    for _ in range(n):
        bas = int(rng.integers(60, KD_W - 360))
        env = kd_zarf('yarim', bas)
        st = kd_istasyonlar(rng, n_ist, env, 1.0)
        for j, A in enumerate(Aler):
            r, _ = kd_pencere(st, A, yanlis=False)
            P[j] += r['algilama']
            Ptut[j] += bool(r['kumeler'])
    return dict(A=[round(a, 4) for a in Aler], P=(P / n).round(3).tolist(), P_tutarli=(Ptut / n).round(3).tolist())


def kd_D4(rng, n, tur, A, n_kay):
    """D4/D5/D5b: modülasyon ölçüsü (koşu kodunun mod_p'si) 1 Hz modelde (tr7_onkayit_modulasyon.py modeli)."""
    W = 1900
    t = np.arange(W)
    ok = 0
    for _ in range(n):
        t0 = 600
        f = np.interp(t, [t0 - 450, t0 + 450], [1 / 40, 1 / 15])
        ph = 2 * np.pi * np.cumsum(f) + rng.uniform(0, 2 * np.pi)
        v = np.exp(-0.5 * ((t - t0) / 250) ** 2) * np.cos(ph)
        bas = int(rng.integers(450, 750))
        a, b = max(0, bas - 60), min(W, bas + 360)
        m = np.zeros(W)
        e = t - bas
        on = (e >= 0) & (e < 300)
        tap = np.minimum(1, np.minimum(e, 300 - e) / 10)
        if tur == 'kilitli':
            m[on] = (np.maximum(0, np.roll(v, 3)) / np.abs(v).max())[on] * tap[on]
            m /= np.sqrt(np.mean(m[on] ** 2))
        elif tur == 'bagimsiz':
            m[on] = np.maximum(0, np.sin(2 * np.pi * e[on] / 20 + rng.uniform(0, 6.3))) * tap[on]
            m /= np.sqrt(np.mean(m[on] ** 2))
        elif tur == 'rastgele':
            for b0 in np.flatnonzero(rng.random(300) < 1 / 15):
                m[bas + b0:bas + b0 + int(rng.integers(5, 15))] = 1
            m[~on] = 0
            m[on] *= tap[on]
        else:
            m[on] = tap[on]
        c = np.sqrt(1 + (A * m) ** 2) * (1 + 0.1 * rng.standard_normal(W))
        L = K.L_seri(c)
        _, p = K.mod_p(L, [K.faz_cos(v)], a, b, np.ones(W, bool), rng, n=n_kay)
        ok += p <= K.MOD_ESIK
    return dict(p_le_001_orani=round(ok / n, 3), kaydirma=n_kay)


def kd_D6(rng, n, sp, A, p_oran):
    alg, atil, atil_y, maske_at = [], [], [], []
    for _ in range(n):
        bas = int(rng.integers(60, KD_W - 360))
        env = kd_deprem(bas, sp, p_oran)
        st = kd_istasyonlar(rng, 3, env, A, norm=kd_ilk5(bas + sp))
        r, _ = kd_pencere(st, A)
        ks = r['kumeler']
        alg.append(bool(ks))
        if ks:
            atil.append(not _sag(r, ('darbe',)))
            atil_y.append(not _sag(r, ('darbe_yanlis_yumusak',)))
            mk = np.zeros(KD_T, bool)
            mk[KD_WI[0] + bas:KD_WI[0] + bas + 70] = True       # katalogdaki olay, d ≈ 30 km: [t0, t0 + d/3 + 60]
            r2, _ = kd_pencere(st, A, mk)
            maske_at.append(not r2['kumeler'] or not any(True for _ in r2['kumeler']))
    a = float(np.mean(alg))
    return dict(algilama=_oran(alg), darbe_atilma_algilananda=_oran(atil),
                algilanmama_ya_da_darbe=round(1 - a + a * (np.mean(atil) if atil else 0), 3),
                yanlis_yumusak=round(1 - a + a * (np.mean(atil_y) if atil_y else 0), 3),
                katalog_maskesi_atilma=_oran(maske_at))


def kd_D7(rng, n, tur, A, gtur='gauss', sekil='bant28'):
    alg, at, at_tam, at_on, at_siz, at_inc1 = [], [], [], [], [], []
    for _ in range(n):
        bas = int(rng.integers(60, KD_W - 360))
        env = kd_zarf(tur, bas, rng)
        st = kd_istasyonlar(rng, 3, env, A, sekil=sekil, gtur=gtur)
        r, _ = kd_pencere(st, A)
        alg.append(bool(r['kumeler']))
        if r['kumeler']:
            at.append(not _sag(r, ('darbe', 'sizinti')))
            at_tam.append(not _sag(r, TAMK))
            at_on.append(not _sag(r, ('darbe_yanlis_on', 'sizinti')))
            at_siz.append(not _sag(r, ('sizinti',)))
            at_inc1.append(not _sag(r, ('sizinti_inc1_I',)))
    return dict(algilama=_oran(alg), darbe_ya_da_sizinti_atilma=_oran(at), tam_kural_atilma=_oran(at_tam),
                yanlis_on_esik_atilma=_oran(at_on), sizinti_atilma=_oran(at_siz), inc1_I_sizinti_atilma=_oran(at_inc1))


def kd_D7d(rng, n, gtur):
    alg, siz, siz_t = [], [], []
    for _ in range(n):
        bas = int(rng.integers(60, KD_W - 360))
        tt = _tt(bas)
        env = np.where(tt >= 0, np.exp(-np.maximum(tt, 0) / 40.0), 0) * np.minimum(1, np.maximum(tt, 0) / 1.0)
        st = kd_istasyonlar(rng, 3, env, 20.0, sekil='koda', gtur=gtur, norm=kd_ilk5(bas))
        r, _ = kd_pencere(st, 20.0)
        alg.append(bool(r['kumeler']))
        if r['kumeler']:
            siz.append(not _sag(r, ('sizinti',)))
            siz_t.append(not _sag(r, ('sizinti_ters',)))
    return dict(algilama=_oran(alg), sizinti_atilma=_oran(siz), yanlis_ters_sizinti_atilma=_oran(siz_t))


def kd_D10(rng, n, tur, A_etkin=3.0):
    r_d, r_60, r_et = [], [], []
    for _ in range(n):
        bas = int(rng.integers(60, KD_W - 360))
        env = kd_zarf(tur, bas)
        st = kd_istasyonlar(rng, 3, env, 1.0)
        tt = _tt(bas)
        on300 = (tt >= 0) & (tt < 300)
        a300 = float(np.mean([_rms(A_etkin * s[0].real, on300) for nl, sl in st for s in sl]))
        r, ist = kd_pencere(st, A_etkin, yanlis=False)
        if not r['kumeler']:
            continue
        k = r['kumeler'][0]
        z = np.zeros(KD_T, bool)
        for liste, ek, bol in ((r_d, 0, a300), (r_60, 60, a300), (r_et, 0, A_etkin)):
            Ip = (max(KD_WI[0], k['Ip'][0] - ek), min(KD_WI[1], k['Ip'][1] + ek))
            a = [K.kestirici_ist(ist[u], Ip, z) for u in k['uyeler']]
            liste.append(float(np.median(a)) / bol)
    med = (lambda x: round(float(np.median(x)), 3) if x else None)
    return dict(n_algilanan=len(r_d), kestirilen_bolu_A300=med(r_d), yanlis_I_60=med(r_60), yanlis_A_etkin=med(r_et))


def kd_D12(rng, n, A, sonum, kuyruklar):
    alg, sag = [], []
    at = {k: [] for k in kuyruklar}
    for _ in range(n):
        bas = int(rng.integers(60, KD_W - 600))
        tt = _tt(bas)
        env = np.where(tt >= 0, np.exp(-np.maximum(tt, 0) / sonum), 0)
        st = kd_istasyonlar(rng, 3, env, A, norm=kd_ilk5(bas), kayma=rng.uniform(-2, 2, 3))
        r, _ = kd_pencere(st, A, yanlis=False)
        alg.append(bool(r['kumeler']))
        if r['kumeler']:
            sag.append(r['algilama'])
            for son in kuyruklar:
                mk = np.zeros(KD_T, bool)
                mk[KD_WI[0] + bas - 10:KD_WI[0] + bas + son] = True
                r2, _ = kd_pencere(st, A, mk, yanlis=False)
                at[son].append(not r2['algilama'])
    out = dict(algilama_maskesiz=_oran(alg), ayiklamadan_sag_maskesiz=_oran(sag))
    out.update({f'maske_atilma_kuyruk{k}': _oran(v) for k, v in at.items()})
    return out


def kd_mda_istasyonlar(rng, n_ist=3):
    """D13/D14: ham (sayım/S = m/s) gürültü, 2–8 Hz RMS 1; koşu zincirinden geçmiş veri ve MDA ara ürünü."""
    D = _kd()
    ist, mv = [], []
    z = np.zeros(KD_T, bool)
    i0, i1 = int((KD_WI[0] - 5) * KD_FS), int((KD_WI[1] + 5) * KD_FS)
    for _ in range(n_ist):
        ey, ed, md = [], [], {}
        for c in 'ZNE':
            x = rng.standard_normal(KD_N)
            x /= _rms(K.bant_gecir(x, KD_FS, 2, 8))
            x = K.ortalama_egilim(x)
            a28 = K.parca_analitik(x, KD_FS, K.BANT_YUKSEK)
            a051 = K.parca_analitik(x, KD_FS, K.BANT_ALCAK)
            for a, l in ((a28, ey), (a051, ed)):
                k0, e = D['kt'](np.abs(a))
                l.append(K.eksene(0, KD_T, k0, e))
            md[c] = [dict(t0=0.0, fs=KD_FS, n=KD_N, i0=i0, i1=i1, a28=a28[i0:i1].astype(np.complex64),
                          a051=a051[i0:i1].astype(np.complex64))]
        ist.append(K.istasyon(K.f32(K.birlesik(ey)), K.f32(K.birlesik(ed)), KD_RI, KD_WI, z))
        mv.append(md)
    return ist, mv, z


def kd_D13(rng, n):
    A20 = [10 ** (j / 20) for j in range(-14, 1)]
    A8 = [10 ** (j / 8) for j in range(-5, 1)]
    Aler = sorted(set(round(a, 9) for a in A20 + A8))
    P = np.zeros(len(Aler))
    for _ in range(n):
        ist, mv, z = kd_mda_istasyonlar(rng)
        if K.pencere_algila(ist, z, KD_WI)['algilama']:
            continue                                   # algılama veren pencereye enjeksiyon yapılmaz (§7.4)
        r = K.mda_deneme(ist, mv, None, [25.0] * 3, z, KD_WI, 0, rng, 1, Aler=Aler, birim=1.0)
        P += np.array(r[0]['alg'], float)
    P /= n
    i20 = [Aler.index(round(a, 9)) for a in A20]
    i8 = [Aler.index(round(a, 9)) for a in A8]
    return dict(A=[round(a, 3) for a in Aler], P=P.round(3).tolist(),
                A50_basamak=K.basamak([Aler[i] for i in i20], P[i20], 0.5),
                A90_basamak=K.basamak([Aler[i] for i in i20], P[i20], 0.9),
                yanlis_j8_A50=K.basamak([Aler[i] for i in i8], P[i8], 0.5),
                yanlis_j8_A90=K.basamak([Aler[i] for i in i8], P[i8], 0.9),
                A50_ara=K.ara_deger([Aler[i] for i in i20], P[i20], 0.5),
                A90_ara=K.ara_deger([Aler[i] for i in i20], P[i20], 0.9))


def kd_D14(rng, n, yanit='jeofon4.5'):
    Aler = [10 ** (j / 40) for j in range(-24, 17)]
    Pg, Py = np.zeros(len(Aler)), np.zeros(len(Aler))
    H = (lambda nn, fs: kd_yanit(yanit, np.fft.rfftfreq(nn, 1 / fs)))
    for _ in range(n):
        ist, mv, z = kd_mda_istasyonlar(rng)
        r = K.mda_deneme(ist, mv, [{c: H for c in 'ZNE'}] * 3, [25.0] * 3, z, KD_WI, 0, rng, 1, Aler=Aler,
                         birim=1.0)
        Pg += np.array(r[0]['alg'], float)
        r = K.mda_deneme(ist, mv, None, [25.0] * 3, z, KD_WI, 0, rng, 1, Aler=Aler, birim=1.0)
        Py += np.array(r[0]['alg'], float)
    Pg /= n
    Py /= n
    g = np.abs(kd_yanit(yanit, np.array([2.0, 4.0, 6.0, 8.0])))
    return dict(yanit=yanit, g_2_4_6_8=[round(float(x), 3) for x in g], P_yanitli=Pg.round(3).tolist(),
                A50_yanitli=K.ara_deger(Aler, Pg, 0.5), A90_yanitli=K.ara_deger(Aler, Pg, 0.9),
                A50_duz_yanlis=K.ara_deger(Aler, Py, 0.5), A90_duz_yanlis=K.ara_deger(Aler, Py, 0.9))


def kd_D15(rng, n, mson):
    t = _kd()['t']
    prof = np.clip((t - (KD_ON + KD_R + 300.0)) / 900.0, 0, 1) + 1
    alg, at, at_yok, at_v2 = [], [], [], []
    for _ in range(n):
        st = [([kd_gurultu(rng, 'gauss', prof) for _ in range(3)], [None] * 3) for _ in range(3)]
        mk = np.zeros(KD_T, bool)
        if mson:
            mk[KD_WI[1] - mson:KD_WI[1]] = True
        r, _ = kd_pencere(st, 0.0, mk)
        alg.append(bool(r['kumeler']))
        if r['kumeler']:
            at.append(not _sag(r, ('taban',)))
            at_yok.append(not _sag(r, ('darbe', 'sizinti')))
            at_v2.append(not _sag(r, ('taban_v2',)))
    return dict(maskeli_son_s=mson, algilama_ayiklamasiz=_oran(alg), taban_3a_atilma=_oran(at),
                yanlis_3a_yok_atilma=_oran(at_yok), yanlis_surum2_W_sonu=_oran(at_v2))


def kd_D8():
    """Birim: (a) sıfır gürültüye 100 nm/s RMS 5 Hz bileşen (2–8 Hz), bilinen duyarlılık; ölçülen RMS = medyan(C)/√2.
    (b) §6.6 PGV'si: bilinen PAZ yanıtlı (120 sn, 2 sıfır) 20 sn sinüs, 1 mm/s; koşu kodunun uzun periyot yolu (okuma O-24)."""
    from obspy import Trace, UTCDateTime
    from obspy.core.inventory import Inventory, Network, Station, Channel, Response
    fs = 100.0
    n = int(1200 * fs)
    t = np.arange(n) / fs
    S = 6.0e8
    sayim = 100e-9 * math.sqrt(2) * np.sin(2 * np.pi * 5.0 * t) * S
    x = K.ortalama_egilim(sayim / S)
    k0, e = K.kutula(0.0, fs, np.abs(K.parca_analitik(x, fs, K.BANT_YUKSEK)))
    rms = float(np.nanmedian(e[100:-100]) / math.sqrt(2))
    fs2 = 20.0
    n2 = int(4000 * fs2)
    t2 = np.arange(n2) / fs2
    p = 2 * np.pi / 120.0
    resp = Response.from_paz(zeros=[0j, 0j], poles=[complex(-p * 0.707, p * 0.707), complex(-p * 0.707, -p * 0.707)],
                             stage_gain=S, stage_gain_frequency=1.0, input_units='M/S', output_units='COUNTS',
                             normalization_frequency=1.0)
    resp.recalculate_overall_sensitivity(1.0)
    ch = Channel('BHZ', '', 40.0, 29.0, 0.0, 0.0, azimuth=0.0, dip=-90.0, sample_rate=fs2, response=resp,
                 start_date=UTCDateTime(2010, 1, 1))
    inv = Inventory(networks=[Network('XX', stations=[Station('KD8', 40.0, 29.0, 0.0, channels=[ch],
                                                             start_date=UTCDateTime(2010, 1, 1))])], source='KD')
    v = 1e-3 * np.sin(2 * np.pi * t2 / 20.0)
    H, f = resp.get_evalresp_response(1 / fs2, n2, output='VEL')
    sy = np.fft.irfft(np.fft.rfft(v) * H, n2)
    tr = Trace(sy.astype(np.float64), header=dict(network='XX', station='KD8', location='', channel='BHZ',
                                                  sampling_rate=fs2, starttime=UTCDateTime(2011, 1, 1)))
    k0b = int(UTCDateTime(2011, 1, 1).timestamp)
    lp = I._lp_seri(tr, inv, k0b, 4000)
    pgv = float(np.nanmax(np.abs(lp[800:3200])))
    return dict(rms_nm_s=round(rms * 1e9, 2), rms_oran=round(rms / 100e-9, 4), pgv_oran=round(pgv / 1e-3, 4))


def kd_D9(o):
    """Pencere: listedeki W ve R, (T0, Δ) ile ±1 sn; 2026 ihlali kodu durdurur. Δ koordinatlardan (`hav`) yeniden
    hesaplanır: listedeki `uzaklik_km` 0,1 km'ye yuvarlıdır (okuma O-39)."""
    mar = csv_oku(o.yol('tr7_dondurulan_liste.csv'))
    pk = csv_oku(o.yol('tr7_parkfield_liste.csv'))
    en = 0.0
    for r in mar:
        d = K.hav(float(r['ev_enlem']), float(r['ev_boylam']), float(r['ist_enlem']), float(r['ist_boylam']))
        w = K.pencere_hesapla(r['t0'], d)
        for a, b in ((w['W'][0], r['W_bas']), (w['W'][1], r['W_son']), (w['R'][0], r['R_bas']),
                     (w['R'][1], r['R_son'])):
            en = max(en, abs((a - K.zaman(b)).total_seconds()))
    th = next(r for r in mar if r['tetikleyici'] == TOHOKU)
    t0 = K.zaman(th['t0'])
    for r in pk:
        d = K.hav(float(th['ev_enlem']), float(th['ev_boylam']), float(r['enlem']), float(r['boylam']))
        w = K.pencere_hesapla(t0, d)
        en = max(en, abs((w['W'][0] - K.zaman(r['W_bas'])).total_seconds()),
                 abs((w['W'][1] - K.zaman(r['W_son'])).total_seconds()))
    durdu = []
    for t, d in (('2025-12-31T22:00:00', 20000.0), ('2025-12-31T23:40:00', 1000.0)):
        try:
            K.pencere_hesapla(t, d)
            durdu.append(False)
        except K.CekirdekHata:
            durdu.append(True)
    try:
        I.dataselect_url('koeri', 'KO', 'X', '', ['HHZ'], '2025-12-31T23:00:00', '2026-01-01T00:00:01')
        durdu.append(False)
    except I.SinirIhlali:
        durdu.append(True)
    return dict(en_buyuk_fark_s=round(en, 3), satir=len(mar) + len(pk), sinir_durdurdu=durdu)


def kd_D12c(o):
    """E1 birim sınaması (deterministik): elle katalog birebir, rastgele kataloglar kaba kuvvetle birebir (referansın
    `maske_kaba`sı), gerçek varışlarda paylar ±0,001 (koşu kodunun `e1_olaylari_csv` + `e1_araliklar` yolu)."""
    import random
    D = referans_modul(o, 'tr7_onkayit_d12c')

    def kume(ar, alan):
        s = set()
        for lo, hi in alan:
            m = K.saniye_maskesi(ar, lo, hi - lo)
            s.update(lo + int(i) for i in np.flatnonzero(m))
        return s
    bek = set()
    for a, b in D.EL_BEKLENEN:
        bek.update(range(a, b))
    out = {}
    for kip in ('dogru', 'kuyruk30', 'S6x', 'buyuktur7', 'ikiz_yok', 'wharton_dislar'):
        ol = [dict(o_) for o_ in D.EL_KATALOG]
        tid = 'TET'
        if kip == 'wharton_dislar':
            ol = [x for x in ol if x['id'] != 'DIGER']
        s = kume(K.e1_araliklar(ol, tid, 0.0, 'dogru' if kip == 'wharton_dislar' else kip), D.EL_ALAN)
        out[kip] = s == bek
    rast = []
    for tohum in (20261616, 6266):
        rng = random.Random(tohum)
        ok = 0
        for _ in range(20):
            tet = dict(id='T', t0=0.0, digerleri=('W2',))
            ol = [dict(id='T', t0=0.0, M=9.0, P=rng.randint(500, 900), S=rng.randint(900, 1200))]
            for i, M in enumerate([7.00, 6.00, 5.99, 6.95]):
                P = rng.randint(-3500, 2800)
                ol.append(dict(id=f'B{i}', t0=float(P - 700), M=M, P=P, S=P + rng.randint(150, 500)))
            ol.append(dict(id='IKIZ', t0=float(rng.randint(-5, 5)), M=round(rng.uniform(7.0, 9.0), 2),
                           P=rng.randint(600, 900), S=rng.randint(1000, 2800)))
            ol.append(dict(id='W2', t0=float(rng.randint(60, 7200)), M=8.2, P=rng.randint(600, 2800),
                           S=rng.randint(1000, 3200)))
            for j in range(40):
                P = rng.randint(-4000, 3500)
                ol.append(dict(id=f'O{j}', t0=float(P - rng.randint(300, 900)), M=round(rng.uniform(5.5, 8.5), 2),
                               P=P, S=P + rng.randint(100, 600)))
            alan = [(-3600, 0), (rng.randint(800, 1200), rng.randint(2600, 3100))]
            ok += kume(K.e1_araliklar(ol, 'T', 0.0), alan) == D.maske_kaba(ol, tet, alan)
        rast.append(ok)
    gercek = e1_paylar_gercek(o)
    bek_g = {'S1': 0.664, 'S2': 0.654, 'S3': 0.645, 'PK': 0.578, 'K1': 0.647}
    return dict(elle_birebir=out, rastgele_birebir=rast, gercek=gercek,
                gercek_tolerans=all(abs(gercek[k] - v) <= 0.001 + 1e-9 for k, v in bek_g.items()))


def e1_olaylari_csv(e1, tetikleyici, segment):
    """§3.4 / §6.5.1a: tetikleyici ve Parkfield pencerelerinin E1 olayları `tr7_e1_maske.csv`'deki varışlardan
    (segment orta noktasıyla önhesaplanmış). csv'de tetikleyicinin kendisi ve ikizi zaten yoktur; Wharton'ın öteki
    olayı vardır. Dönüş: [dict(id, M, t0=None, P, S)] (epoch)."""
    ol = {}
    for r in e1:
        if r['tetikleyici'] != tetikleyici or r['segment'] != segment:
            continue
        x = ol.setdefault(r['olay'], dict(id=r['olay'], M=float(r['M']), t0=None))
        x[r['faz']] = K.epoch(r['varis'])
    return list(ol.values())


def e1_paylar_gercek(o):
    mar = csv_oku(o.yol('tr7_dondurulan_liste.csv'))
    pk = csv_oku(o.yol('tr7_parkfield_liste.csv'))
    e1 = csv_oku(o.yol('tr7_e1_maske.csv'))
    out = {}
    for seg in ('S1', 'S2', 'S3'):
        rs = [r for r in mar if r['tetikleyici'] == TOHOKU and r['segment'] == seg]
        w0 = min(K.epoch(r['W_bas']) for r in rs)
        w1 = max(K.epoch(r['W_son']) for r in rs)
        ar = K.e1_araliklar(e1_olaylari_csv(e1, TOHOKU, seg), TOHOKU, None)
        out[seg] = round(float(K.saniye_maskesi(ar, int(w0), int(w1 - w0)).mean()), 3)
    w0 = min(K.epoch(r['W_bas']) for r in pk)
    w1 = max(K.epoch(r['W_son']) for r in pk)
    ar = K.e1_araliklar(e1_olaylari_csv(e1, TOHOKU, 'PK'), TOHOKU, None)
    out['PK'] = round(float(K.saniye_maskesi(ar, int(w0), int(w1 - w0)).mean()), 3)
    ka, kz = K.epoch(K1_ARALIK[0]), K.epoch(K1_ARALIK[1])
    m = K.saniye_maskesi(ar, int(ka), int(kz - ka))
    out['K1'] = round(float(m.mean()), 3)
    out['K1_maskeli_s'] = int(m.sum())
    out['K1_uzunluk_s'] = int(kz - ka)
    return out


def referans_modul(o, ad):
    """Referans betiği sha256'sı denetlenerek içe aktarılır (yalnız KD ve sınama)."""
    import importlib
    y = o.yol(ad + '.py')
    if sha256_dosya(y) != REFERANS[ad + '.py']:
        raise KosuDur(f'referans betik sha256 uyuşmuyor: {ad}.py')
    if o.tr7 not in sys.path:
        sys.path.insert(0, o.tr7)
    return importlib.import_module(ad)


# KD iş listesi: (ad, ek, tohum sayısı, pencere). Bantlar §7.1 tablosundan (okuma O-25: D12 "maskesiz algılanır" ≥ 0,95).
KD_ISLER = [
    ('D2', 3, 2, 200), ('D3', 8, 2, 100),
    ('D4', ('kilitli', 0.7, 1000), 1, 100),
    ('D5', ('sabit', 1.0, 1000), 1, 100), ('D5', ('sabit', 3.0, 1000), 1, 100),
    ('D5', ('rastgele', 1.0, 1000), 1, 100), ('D5', ('rastgele', 3.0, 1000), 1, 100),
    ('D5b', ('bagimsiz', 1.0, 200), 2, 100), ('D5b', ('bagimsiz', 3.0, 200), 2, 100),
    ('D6', (0, 100.0, 0.0), 2, 100), ('D6', (0, 20.0, 0.0), 1, 100),
    ('D6b', (8, 100.0, 0.25), 2, 100), ('D6b', (3, 100.0, 0.25), 1, 100), ('D6b', (5, 100.0, 0.25), 1, 100),
    ('D6b', (3, 20.0, 0.25), 1, 100), ('D6b', (5, 20.0, 0.25), 1, 100), ('D6b', (8, 20.0, 0.25), 1, 100),
    ('D7', ('yarim', 10.0, 'gauss', 'bant28'), 2, 100),
    ('D7b', ('patlama', 3.0, 'gauss', 'bant28'), 2, 100), ('D7b', ('patlama', 10.0, 'gauss', 'bant28'), 2, 100),
    ('D7b', ('patlama', 30.0, 'gauss', 'bant28'), 2, 100),
    ('D7c', ('yarim', 3.0, 'gauss', 'duz'), 2, 100), ('D7c', ('yarim', 10.0, 'gauss', 'duz'), 2, 100),
    ('D7c', ('yarim', 3.0, 'kentsel', 'duz'), 2, 100), ('D7c', ('yarim', 10.0, 'kentsel', 'duz'), 2, 100),
    ('D7d', 'gauss', 2, 100), ('D7d', 'kentsel', 2, 100),
    ('D10', 'yarim', 2, 100), ('D10', 'sabit', 2, 100),
    ('D12', (5.0, 60.0, (240, 60)), 2, 100),
    ('D12b', (2.0, 30.0, (60, 30)), 2, 100), ('D12b', (3.0, 30.0, (60, 30)), 2, 100),
    ('D12b', (5.0, 30.0, (60, 30)), 2, 100), ('D12b', (5.0, 60.0, (60, 30)), 1, 100),
    ('D13', None, 2, 100), ('D14', 'jeofon4.5', 2, 100), ('D14', 'bh20', 1, 100),
    ('D15', 0, 2, 100), ('D15', 120, 2, 100),
]


def kd_is(ad, ek, tohum, n):
    rng = np.random.default_rng(tohum)
    if ad in ('D2', 'D3'):
        Aler = [0.0] + [10 ** (j / 40) for j in range(-16, 1)]
        r = kd_D2(rng, n, ek, Aler)
    elif ad in ('D4', 'D5', 'D5b'):
        r = kd_D4(rng, n, ek[0], ek[1], ek[2])
    elif ad in ('D6', 'D6b'):
        r = kd_D6(rng, n, ek[0], ek[1], ek[2])
    elif ad in ('D7', 'D7b', 'D7c'):
        r = kd_D7(rng, n, ek[0], ek[1], ek[2], ek[3])
    elif ad == 'D7d':
        r = kd_D7d(rng, n, ek)
    elif ad == 'D10':
        r = kd_D10(rng, n, ek)
    elif ad in ('D12', 'D12b'):
        r = kd_D12(rng, n, ek[0], ek[1], ek[2])
    elif ad == 'D13':
        r = kd_D13(rng, n)
    elif ad == 'D14':
        r = kd_D14(rng, n, ek)
    elif ad == 'D15':
        r = kd_D15(rng, n, ek)
    else:
        raise ValueError(ad)
    return dict(denetim=ad, ek=ek, tohum=tohum, n=n, sonuc=r)


def _kd_is_tup(x):
    return kd_is(*x)


def kd_plan(olcek=1.0):
    plan = []
    for i, (ad, ek, nt, n) in enumerate(KD_ISLER):
        for k in range(nt):
            plan.append((ad, ek, kd_tohum(i, k), max(1, int(round(n * olcek)))))
    return plan


def kd_bantlar(sonuclar, d8, d9, d11, d12c):
    """§7.1 kabul bantları; her satır: dogru (bant içinde mi), değerler. 'bilgi' satırları şart değildir."""
    S = {}
    for r in sonuclar:
        S.setdefault((r['denetim'], json.dumps(r['ek'])), []).append(r['sonuc'])
    sat = []

    def ekle(ad, sart, gecti, deger, bilgi=False):
        sat.append(dict(denetim=ad, sart=sart, gecti=bool(gecti), deger=deger, bilgi=bilgi))
    for (ad, ek), rs in sorted(S.items()):
        if ad == 'D2':
            i0 = 0
            d1 = [x['P'][i0] for x in rs]
            ekle('D1', 'yanlış algılama ≤ 0,01', all(v <= 0.01 for v in d1), d1)
            a50 = [K.ara_deger(x['A'][1:], x['P'][1:], 0.5) for x in rs]
            a90 = [K.ara_deger(x['A'][1:], x['P'][1:], 0.9) for x in rs]
            ekle('D2', 'A50 ∈ [0,56, 0,67], A90 ∈ [0,59, 0,72]',
                 all(v is not None and 0.56 <= v <= 0.67 for v in a50) and all(v is not None and 0.59 <= v <= 0.72
                                                                                for v in a90),
                 dict(A50=a50, A90=a90))
        elif ad == 'D3':
            a50 = [K.ara_deger(x['A'][1:], x['P'][1:], 0.5) for x in rs]
            ekle('D3', 'A50 ∈ [0,52, 0,62]', all(v is not None and 0.52 <= v <= 0.62 for v in a50), dict(A50=a50))
        elif ad == 'D4':
            v = [x['p_le_001_orani'] for x in rs]
            ekle('D4', 'p ≤ 0,01 oranı ≥ 0,90', all(x >= 0.90 for x in v), v)
        elif ad == 'D5':
            v = [x['p_le_001_orani'] for x in rs]
            ekle(f'D5 {ek}', 'p ≤ 0,01 oranı ≤ 0,05', all(x <= 0.05 for x in v), v)
        elif ad == 'D5b':
            v = [x['p_le_001_orani'] for x in rs]
            ekle(f'D5b {ek}', 'bilgi bandı [0,25, 0,65] (şart değil; dışında: kod incelenir)',
                 all(0.25 <= x <= 0.65 for x in v), v, bilgi=True)
        elif ad in ('D6', 'D6b'):
            e = json.loads(ek)
            v = [x['algilanmama_ya_da_darbe'] for x in rs]
            km = [x['katalog_maskesi_atilma'] for x in rs]
            if ad == 'D6' and e[1] == 100.0:
                ekle('D6 ×100', 'algılanmama ya da darbeyle atılma ≥ 0,95; katalogda maskeyle atılma 1,00',
                     all(x >= 0.95 for x in v) and all(k in (None, 1.0) for k in km),
                     dict(deger=v, katalog=km, yanlis_yumusak=[x['yanlis_yumusak'] for x in rs],
                          algilama=[x['algilama'] for x in rs]))
            elif ad == 'D6b' and e[0] == 8 and e[1] == 100.0:
                ekle('D6b ×100 S–P 8', 'algılanmama ya da darbeyle atılma ≥ 0,90', all(x >= 0.90 for x in v),
                     dict(deger=v, yanlis_yumusak=[x['yanlis_yumusak'] for x in rs]))
            else:
                ekle(f'{ad} {ek}', 'bilgi', True, dict(deger=v, algilama=[x['algilama'] for x in rs]), bilgi=True)
        elif ad == 'D7':
            v = [x['tam_kural_atilma'] for x in rs]
            ekle('D7', 'darbe, sızıntı ya da taban kaymasıyla atılma ≤ 0,03', all(x is not None and x <= 0.03 for x in v),
                 dict(deger=v, algilama=[x['algilama'] for x in rs],
                      yanlis_on=[x['yanlis_on_esik_atilma'] for x in rs]))
        elif ad == 'D7b':
            v = [x['darbe_ya_da_sizinti_atilma'] for x in rs]
            ekle(f'D7b {ek}', 'darbe ya da sızıntıyla atılma ≤ 0,03', all(x is not None and x <= 0.03 for x in v),
                 dict(deger=v, yanlis_on=[x['yanlis_on_esik_atilma'] for x in rs]))
        elif ad == 'D7c':
            v = [x['sizinti_atilma'] for x in rs]
            ekle(f'D7c {ek}', 'sızıntıyla atılma ≤ 0,05', all(x is not None and x <= 0.05 for x in v),
                 dict(deger=v, yanlis_inc1_I=[x['inc1_I_sizinti_atilma'] for x in rs]))
        elif ad == 'D7d':
            v = [x['sizinti_atilma'] for x in rs]
            ekle(f'D7d {ek}', 'sızıntıyla atılma ≥ 0,95', all(x is not None and x >= 0.95 for x in v),
                 dict(deger=v, yanlis_ters=[x['yanlis_ters_sizinti_atilma'] for x in rs]))
        elif ad == 'D10':
            v = [x['kestirilen_bolu_A300'] for x in rs]
            ekle(f'D10 {ek}', 'kestirilen / A_300 ∈ [0,90, 1,15]', all(x is not None and 0.90 <= x <= 1.15 for x in v),
                 dict(deger=v, yanlis_I60=[x['yanlis_I_60'] for x in rs], yanlis_A_etkin=[x['yanlis_A_etkin'] for x in rs]))
        elif ad == 'D12':
            alg = [x['algilama_maskesiz'] for x in rs]
            at = [x['maske_atilma_kuyruk240'] for x in rs]
            ekle('D12', 'maskesiz algılanır (≥ 0,95); +240 sn maske ile atılma 1,00',
                 all(a >= 0.95 for a in alg) and all(x == 1.0 for x in at),
                 dict(algilama=alg, atilma240=at, yanlis_kuyruk60=[x['maske_atilma_kuyruk60'] for x in rs]))
        elif ad == 'D12b':
            e = json.loads(ek)
            v = [x['maske_atilma_kuyruk60'] for x in rs]
            if e[1] == 30.0:
                ekle(f'D12b ×{e[0]:g} 30 sn', '+60 sn maske ile atılma ≥ 0,95', all(x is not None and x >= 0.95 for x in v),
                     dict(deger=v, yanlis_kuyruk30=[x['maske_atilma_kuyruk30'] for x in rs]))
            else:
                ekle(f'D12b ×{e[0]:g} 60 sn', 'bilgi', True, dict(deger=v), bilgi=True)
        elif ad == 'D13':
            a50 = [x['A50_basamak'] for x in rs]
            a90 = [x['A90_basamak'] for x in rs]
            ekle('D13', 'A50_basamak ∈ [0,42, 0,48], A90_basamak ∈ [0,44, 0,53]',
                 all(v is not None and 0.42 <= v <= 0.48 for v in a50)
                 and all(v is not None and 0.44 <= v <= 0.53 for v in a90),
                 dict(A50=a50, A90=a90, yanlis_j8=[(x['yanlis_j8_A50'], x['yanlis_j8_A90']) for x in rs]))
        elif ad == 'D14':
            a50 = [x['A50_yanitli'] for x in rs]
            if json.loads(ek) == 'jeofon4.5':
                oran = a50[1] / a50[0] if len(a50) == 2 and all(a50) else None
                ekle('D14', 'A50(tohum 2)/A50(tohum 1) ∈ [0,93, 1,07] ve A50 ∈ [0,55, 0,67]',
                     oran is not None and 0.93 <= oran <= 1.07 and all(0.55 <= v <= 0.67 for v in a50),
                     dict(A50=a50, oran=oran, A90=[x['A90_yanitli'] for x in rs],
                          yanlis_duz=[x['A50_duz_yanlis'] for x in rs]))
            else:
                ekle('D14 bh20', 'bilgi', True, dict(A50=a50, duz=[x['A50_duz_yanlis'] for x in rs]), bilgi=True)
        elif ad == 'D15':
            alg = [x['algilama_ayiklamasiz'] for x in rs]
            at = [x['taban_3a_atilma'] for x in rs]
            ekle(f'D15 ({"b" if json.loads(ek) else "a"})', 'ayıklamasız algılama ≥ 0,90 ve 3a ile atılma ≥ 0,95',
                 all(a >= 0.90 for a in alg) and all(x is not None and x >= 0.95 for x in at),
                 dict(algilama=alg, atilma=at, yanlis_3a_yok=[x['yanlis_3a_yok_atilma'] for x in rs],
                      yanlis_v2=[x['yanlis_surum2_W_sonu'] for x in rs]))
    ekle('D8', 'ölçülen RMS ±%5; PGV ±%5', abs(d8['rms_oran'] - 1) <= 0.05 and abs(d8['pgv_oran'] - 1) <= 0.05, d8)
    ekle('D9', 'W ve R listedekine ±1 sn; 2026 ihlali durdurur', d9['en_buyuk_fark_s'] <= 1.0 and all(d9['sinir_durdurdu']),
         d9)
    ekle('D11', 'metin birebir', d11['hepsi'], d11)
    ekle('D12c', 'elle katalog birebir; rastgele 20/20; gerçek varışlar ±0,001',
         d12c['elle_birebir']['dogru'] and d12c['rastgele_birebir'] == [20, 20] and d12c['gercek_tolerans'],
         d12c)
    yanlis_ayrildi = {k: not v for k, v in d12c['elle_birebir'].items() if k != 'dogru'}
    sat[-1]['deger']['yanlis_kod_ayrildi'] = yanlis_ayrildi
    return sat


def kd_kos(o, paralel=4, olcek=1.0, yaz=True, log=print):
    """Bütün KD'yi koşar; sonuç tr7_kd.json (yeniden koşu: tr7_kd_<n>.json; 'koşu öncesi düzeltme')."""
    from concurrent.futures import ProcessPoolExecutor
    t0 = time.time()
    plan = kd_plan(olcek)
    if paralel > 1:
        with ProcessPoolExecutor(paralel) as ex:
            sonuclar = list(ex.map(_kd_is_tup, plan))
    else:
        sonuclar = [kd_is(*x) for x in plan]
    d8, d9, d11, d12c = kd_D8(), kd_D9(o), kd_D11(), kd_D12c(o)
    sat = kd_bantlar(sonuclar, d8, d9, d11, d12c)
    gecti = all(s['gecti'] for s in sat if not s['bilgi'])
    out = dict(aciklama='TR-7 §7.1 KD: yalnız yapay veri; koşu kodunun kendi fonksiyonları (100 Hz, Butterworth).',
               kod_sha256=kod_sha(), olcek=olcek, sure_s=round(time.time() - t0, 1), gecti=gecti, satirlar=sat,
               ham=sonuclar)
    if yaz:
        y = o.yol('tr7_kd.json')
        i = 1
        while os.path.exists(y):
            i += 1
            y = o.yol(f'tr7_kd_{i}.json')
        json_yaz_x(y, out)
        log(f'KD yazıldı: {y}; geçti={gecti}')
    return out


def kd_son(o):
    ys = sorted([f for f in os.listdir(o.tr7) if f.startswith('tr7_kd') and f.endswith('.json')],
                key=lambda f: (len(f), f))
    if not ys:
        return None
    with open(o.yol(ys[-1]), encoding='utf-8') as f:
        return json.load(f)


# ====================================================================== manifest (§3.5): üstveri ve katalog; dalga formu YOK
MARMARA_SEG = tuple(s for s in K.SEGMENTLER)


def bolge_merkez(bolge):
    """Katalog sorgusunun merkezi ve yarıçapı (derece): bölgedeki izlerin bütün köşelerini + 1000 km örter (§6.5.1)."""
    segs = ['PK'] if bolge == 'Parkfield' else list(MARMARA_SEG)
    pts = [(la, lo) for s in segs for lo, la in K.SEGMENT[s]]
    la0 = sum(p[0] for p in pts) / len(pts)
    lo0 = sum(p[1] for p in pts) / len(pts)
    r = max(K.hav(la0, lo0, la, lo) for la, lo in pts) + K.YEREL_UZAK[0] + 50.0
    return la0, lo0, r / 111.195


def katalog_ayristir(katalog, govde):
    """ComCat csv ya da EMSC text → [dict(id, t0 epoch, la, lo, M, derinlik)]. Ayrıştırılamazsa BicimHata."""
    if not govde:
        return []
    try:
        metin = govde.decode('utf-8')
        out = []
        if katalog == 'comcat':
            for r in csv.DictReader(metin.splitlines()):
                M = float(r['mag']) if r.get('mag') not in (None, '') else None
                out.append(dict(id=r['id'], t0=K.epoch(r['time']), la=float(r['latitude']), lo=float(r['longitude']),
                                M=M, derinlik=float(r['depth']) if r.get('depth') not in (None, '') else 0.0))
        else:
            for s in metin.splitlines():
                if not s.strip() or s.startswith('#'):
                    continue
                f = s.split('|')
                M = float(f[10]) if len(f) > 10 and f[10].strip() not in ('', '--') else None
                out.append(dict(id=f[0], t0=K.epoch(f[1]), la=float(f[2]), lo=float(f[3]), M=M,
                                derinlik=float(f[4]) if f[4].strip() else 0.0))
        return out
    except Exception as e:                              # noqa: BLE001
        raise I.BicimHata(f'{katalog} yanıtı ayrıştırılamadı: {type(e).__name__}: {e}') from e


def pencere_zamanlari(p):
    xs = list(p['ist'].values())
    return min(x['R'][0] for x in xs), max(x['W'][1] for x in xs)


def _ist_aralik(D):
    """İstasyon başına StationXML sorgu aralığı (bütün pencereleri, dolguyla)."""
    out = {}
    for p in D['pen'].values():
        for k, x in p['ist'].items():
            a = x['R'][0] - dt.timedelta(seconds=K.DOLGU_S + 86400)
            b = min(x['W'][1] + dt.timedelta(seconds=K.DOLGU_S + 86400), I.KATALOG_SON)
            key = (x['ag'], x['istasyon'], x['konum'], x['z_kanal'][:2], x.get('parkfield', False))
            if key in out:
                out[key] = (min(out[key][0], a), max(out[key][1], b), out[key][2] | {x['kaynak']})
            else:
                out[key] = (a, b, {x['kaynak']})
    return out


def yatay_sec(inv, ag, ist, konum, bi, t):
    from obspy import UTCDateTime
    ch = inv.select(network=ag, station=ist, location=konum, channel=bi + '?', time=UTCDateTime(t))
    kods = {c.code for n in ch for s in n for c in s}
    for a, b in ((bi + 'N', bi + 'E'), (bi + '1', bi + '2')):
        if a in kods and b in kods:
            return [a, b]
    return []


def asama_manifest(o, D):
    I.sinir('2005-01-01', I.KATALOG_SON, katalog=True)
    cl = o.istemci()
    sx_dir = o.zyol('stationxml')
    kat_dir = o.zyol('katalog')
    os.makedirs(sx_dir, exist_ok=True)
    os.makedirs(kat_dir, exist_ok=True)
    man = dict(aciklama='TR-7 koşu manifesti (§3.5): üstveri ve katalog; dalga formu yok.', zaman=simdi(),
               girdi_sha256=D['girdi'], kod_sha256=kod_sha(), pip_freeze=pip_freeze(), user_agent=I.UA,
               stationxml={}, katalog={}, kanal={}, e1_negatif=[], plan={})
    kd = kd_son(o)
    man['kd'] = dict(gecti=kd['gecti'], kod_sha256=kd['kod_sha256']) if kd else None
    # (c) StationXML
    invs = {}
    bicim_hata = 0
    for (ag, ist, konum, bi, pk), (a, b, kay) in sorted(_ist_aralik(D).items()):
        servis = I.servis_sec(ag, ' '.join(kay), parkfield=pk)
        url = I.station_url(servis, ag, ist, konum, [bi + '?'], a, b, taban=o.servis)
        yol = os.path.join(sx_dir, f'{ag}.{ist}.{konum or "--"}.{bi}.xml')
        r = cl.iste(servis, url, hedef=yol)
        if pk and r['durum'] == 'yok':
            servis = 'earthscope'
            url = I.station_url(servis, ag, ist, konum, [bi + '?'], a, b, taban=o.servis)
            r = cl.iste(servis, url, hedef=yol)
        man['stationxml'][f'{ag}.{ist}.{konum}.{bi}'] = {k: r.get(k) for k in ('durum', 'http', 'bayt', 'sha256')}
        man['stationxml'][f'{ag}.{ist}.{konum}.{bi}']['url'] = url
        if r['durum'] == 'tamam':
            try:
                invs[(ag, ist, konum, bi)] = I.oku_stationxml(yol)
            except I.BicimHata as e:
                bicim_hata += 1
                man['stationxml'][f'{ag}.{ist}.{konum}.{bi}']['bicim_hatasi'] = str(e)
    if invs and bicim_hata / max(1, len(invs) + bicim_hata) > BICIM_HATA_PAY:
        raise KosuDur(f'StationXML biçim hatası payı > %1 ({bicim_hata}); §10 madde 6')
    # kanal özetleri: her pencere × istasyon için (pencere zamanında)
    for p in D['pen'].values():
        for k, x in p['ist'].items():
            inv = invs.get((x['ag'], x['istasyon'], x['konum'], x['z_kanal'][:2]))
            anahtar = f"{p['id']}|{x['ag']}.{x['istasyon']}"
            if inv is None:
                man['kanal'][anahtar] = dict(z=dict(yanit=False), yatay=[], ozet={})
                continue
            t = x['W'][0]
            yat = yatay_sec(inv, x['ag'], x['istasyon'], x['konum'], x['z_kanal'][:2], t)
            oz = {c: I.yanit_ozeti(inv, x['ag'], x['istasyon'], x['konum'], c, t) for c in [x['z_kanal']] + yat}
            man['kanal'][anahtar] = dict(yatay=yat, ozet=oz)
    # g ∉ [0,5, 2] kanal sayısı segment başına (bilgi; tetikleyici pencereleri)
    gsay = {}
    for p in D['pen'].values():
        if p['tur'] != 'tet':
            continue
        for s, keys in p['seg'].items():
            for k in keys:
                oz = man['kanal'][f"{p['id']}|{k[0]}.{k[1]}"]['ozet']
                gsay.setdefault(s, set()).update(c for c, v in oz.items() if v.get('yanit') and v.get('g_disinda'))
    man['g_disinda_kanal_sayisi'] = {s: len(v) for s, v in gsay.items()}
    # (b) kataloglar: yerel maske (EMSC + ComCat; Parkfield yalnız ComCat), negatiflerin E1'i (ComCat M ≥ 6,0)
    for p in sorted(D['pen'].values(), key=lambda p: p['id']):
        r0, w1 = pencere_zamanlari(p)
        la, lo, rd = bolge_merkez(p['bolge'])
        katlar = ('comcat',) if p['bolge'] == 'Parkfield' else ('emsc', 'comcat')
        for kt in katlar:
            a = r0 - dt.timedelta(hours=1)
            url = I.event_url(kt, a, min(w1, I.KATALOG_SON), la, lo, rd, K.YEREL_YAKIN[1], taban=o.katalog)
            man['katalog'][f"{p['id']}|yerel|{kt}"] = _katalog_iste(cl, kat_dir, kt, url, f"{p['id']}|yerel|{kt}")
        if p['tur'] == 'neg':
            a = r0 - dt.timedelta(hours=3)
            url = I.event_url('comcat', a, min(w1, I.KATALOG_SON), 0.0, 0.0, 180.0, K.E1_M6, taban=o.katalog)
            r = _katalog_iste(cl, kat_dir, 'comcat', url, f"{p['id']}|e1|comcat")
            man['katalog'][f"{p['id']}|e1|comcat"] = r
            man['e1_negatif'] += e1_negatif_varislar(p, katalog_ayristir('comcat', _govde(kat_dir, r)))
    # (d) indirme planı
    man['plan'] = indirme_plani(D, man)
    return man


def _govde(kat_dir, r):
    if r['durum'] != 'tamam':
        return b''
    with open(os.path.join(kat_dir, r['dosya']), 'rb') as f:
        return f.read()


def _katalog_iste(cl, kat_dir, kt, url, ad):
    dosya = hashlib.sha256(ad.encode()).hexdigest()[:24] + ('.csv' if kt == 'comcat' else '.txt')
    r = cl.iste('katalog_' + kt, url, hedef=os.path.join(kat_dir, dosya))
    out = {k: r.get(k) for k in ('durum', 'http', 'bayt', 'sha256')}
    out.update(url=url, dosya=dosya)
    if r['durum'] not in ('tamam', 'yok'):
        raise KosuDur(f'katalog sorgusu başarısız ({r["durum"]}, HTTP {r["http"]}): {url}; sorgular bir kez ve eksiksiz '
                      f'yapılmalı (§6.5.1)')
    if r['durum'] == 'tamam':
        katalog_ayristir(kt, _govde(kat_dir, out))        # biçim denetimi (BicimHata)
    return out


def e1_negatif_varislar(p, olaylar):
    """§3.4/§3.5 b: negatif pencerelerin E1 varışları (segment orta noktasına, iasp91). Kaydırılmış T0'ın ±5 sn'sindeki
    M ≥ 7 kayıt 'tetikleyici ikizi' kuralıyla dışarıda kalır (seçimde M ≥ 6,5 dışlandığından uygulamada boş)."""
    from obspy.geodetics import locations2degrees
    out = []
    r0, w1 = pencere_zamanlari(p)
    a, b = K.epoch(r0) - 3 * 3600, K.epoch(w1)
    tet_t0 = K.epoch(p['t0'])
    for s in p['seg']:
        la, lo = K.orta(s)
        for e in olaylar:
            if not (a <= e['t0'] <= b) or e['M'] is None or e['M'] < K.E1_M6:
                continue
            if K.e1_dislanir(dict(id=e['id'], t0=e['t0'], M=e['M']), None, tet_t0):
                continue
            deg = locations2degrees(e['la'], e['lo'], la, lo)
            tp, ts = K.taup_varislar(e['derinlik'], deg)
            for faz, tt in (('P', tp), ('S', ts)):
                if tt is not None:
                    out.append(dict(pencere=p['id'], segment=s, olay=e['id'], M=e['M'], t0=e['t0'], faz=faz,
                                    varis=e['t0'] + tt))
    return out


def pip_freeze():
    r = subprocess.run([sys.executable, '-m', 'pip', 'freeze'], capture_output=True, text=True)
    return r.stdout.splitlines() if r.returncode == 0 else [f'pip freeze başarısız: {r.stderr.strip()}']


def kanal_ozet(man, p, k):
    return man['kanal'].get(f"{p['id']}|{k[0]}.{k[1]}", dict(yatay=[], ozet={}))


def pgv_uygun(man, p, k):
    x = p['ist'][k]
    oz = kanal_ozet(man, p, k)['ozet'].get(x['z_kanal'], {})
    return bool(oz.get('pgv_uygun'))


def indirme_plani(D, man):
    """§3.5 d: her pencere için ilk istek kümesi: her segmentte `iz_sira` sırasıyla ilk 12 istasyon; tetikleyici
    pencerelerinde ayrıca PGV'ye uygun bütün istasyonlar (§6.4 başvuru ve §6.6, 12 sınırının dışı); Parkfield'da BK.PKD.
    Örtüden düşen istasyonun yerine sonraki aday sonradan istenir (planlı sayıya girmez; okuma O-26)."""
    plan = {}
    for p in sorted(D['pen'].values(), key=lambda p: p['id']):
        keys = []
        for s, ks in p['seg'].items():
            for k in ks[:K.N_SINIR]:
                if k not in keys:
                    keys.append(k)
        if p['tur'] == 'tet':
            for k in p['ist']:
                if k not in keys and pgv_uygun(man, p, k):
                    keys.append(k)
            for k in p.get('tani', []):
                if k not in keys:
                    keys.append(k)
        plan[p['id']] = [istek_tanimi(p, k, man) for k in keys]
    return plan


def istek_tanimi(p, k, man):
    x = p['ist'][k]
    oz = kanal_ozet(man, p, k)
    a = x['R'][0] - dt.timedelta(seconds=K.DOLGU_S)
    b = x['W'][1] + dt.timedelta(seconds=K.DOLGU_S)
    servis = I.servis_sec(x['ag'], x['kaynak'], parkfield=x.get('parkfield', False))
    return dict(ag=x['ag'], istasyon=x['istasyon'], konum=x['konum'], kanallar=[x['z_kanal']] + oz['yatay'],
                bas=a.isoformat(), son=b.isoformat(), servis=servis, istek=1)


def manifest_oku(o):
    y = o.yol('tr7_manifest.json')
    if not os.path.exists(y):
        raise KosuDur('manifest yok (önce manifest aşaması)')
    with open(y, encoding='utf-8') as f:
        return json.load(f)


# ====================================================================== indir–zarfla–sil motoru (§6.1)
def ham_yolu(o, asama, p, k):
    return o.zyol('ham', asama, p['id'].replace('|', '_'), f'{k[0]}.{k[1]}.mseed')


def zarf_yolu(o, p, k):
    return o.zyol('zarf', p['id'].replace('|', '_'), f'{k[0]}.{k[1]}.npz')


class AsamaSayac:
    """§10 madde 6: servis ve biçim hatası payları (aşama başına; günlükten yeniden kurulur)."""

    def __init__(self, gunluk_yol, planli):
        self.yol = gunluk_yol
        self.planli = max(1, planli)
        self.son = {}
        for r in jsonl_oku(gunluk_yol):
            if r.get('tur') == 'istek':
                self.son[r['anahtar']] = r
        self.yeniden_tur = any(r.get('tur') == 'yeniden_tur' for r in jsonl_oku(gunluk_yol))

    def ekle(self, r):
        r = dict(r, tur='istek', zaman=simdi())
        satir_ekle(self.yol, r)
        self.son[r['anahtar']] = r

    def servis_payi(self):
        return sum(1 for r in self.son.values() if r['durum'] == 'servis_hatasi') / self.planli

    def bicim_payi(self):
        n200 = sum(1 for r in self.son.values() if r.get('http') == 200 and r['durum'] in ('tamam', 'bicim_hatasi'))
        nb = sum(1 for r in self.son.values() if r['durum'] == 'bicim_hatasi')
        return nb / n200 if n200 else 0.0, nb, n200


def istasyon_isle(o, p, k, man, yol, lp, mda):
    """İndirilen dosyayı işler; zarf deposuna yazar. Dönüş (kayıt, mda ara ürünü)."""
    x = p['ist'][k]
    oz = kanal_ozet(man, p, k)
    from obspy.geodetics import gps2dist_azimuth
    olay = p.get('ev')
    baz = gps2dist_azimuth(olay[0], olay[1], x['la'], x['lo'])[2] if olay else 0.0
    k0, n = pencere_ekseni(p)
    pen = ist_pencere(x, k0, n)
    Wb = [K.epoch(min(y['W'][0] for y in p['ist'].values())), K.epoch(max(y['W'][1] for y in p['ist'].values()))]
    pen['W_mda'] = Wb
    inv = None
    if lp or mda:
        inv = stationxml_oku(o, x)
    ist = dict(ag=x['ag'], istasyon=x['istasyon'], konum=x['konum'], z_kanal=x['z_kanal'], yatay=oz['yatay'],
               ozet=oz['ozet'], baz=baz)
    r = I.isle_istasyon_penceresi(yol, inv, ist, pen, lp=lp and pgv_uygun(man, p, k), mda=mda)
    meta = dict(pencere=p['id'], ag=x['ag'], istasyon=x['istasyon'], dusme=r['dusme'], ortu_R=r.get('ortu_R'),
                ortu_W=r.get('ortu_W'), bilesen=r.get('bilesen'))
    return r, meta


def stationxml_oku(o, x):
    y = o.zyol('stationxml', f"{x['ag']}.{x['istasyon']}.{x['konum'] or '--'}.{x['z_kanal'][:2]}.xml")
    return I.oku_stationxml(y)


def pencere_indir(o, D, man, p, asama, sayac, lp=False, ham_tut=False, kayit=None, segler=None):
    """Bir pencerenin istasyonlarını indirir ve zarflar. Her segmentte örtüden geçen 12 istasyon bulununca o
    segmentin kalan adayları (başka segment için gerekmiyorsa) indirilmez (§6.1). Dönüş: {anahtar: kayıt}."""
    kayit = {} if kayit is None else kayit
    for r in jsonl_oku(o.yol('tr7_zarf_sha256.jsonl')):
        if r['pencere'] == p['id']:
            kayit[(r['ag'], r['istasyon'])] = r
    gerek = None if segler is None else {k for s in segler for k in p['seg'].get(s, [])} | set(p.get('tani', []))
    planli = [(q['ag'], q['istasyon']) for q in man['plan'].get(p['id'], [])]
    bekleyen = [k for k in planli if k not in kayit and (gerek is None or k in gerek)]
    denendi = set()                                     # bu çağrıda istenenler (servis hatası döngüye girmez)
    while True:
        if bekleyen:
            _indir_kume(o, man, p, asama, sayac, bekleyen, kayit, lp, ham_tut)
            denendi.update(bekleyen)
        bekleyen = []
        for s, ks in p['seg'].items():
            if segler is not None and s not in segler:
                continue
            gecen = [k for k in ks if k in kayit and kayit[k].get('dusme') is None]
            if len(gecen) >= K.N_SINIR:
                continue
            aday = [k for k in ks if k not in kayit and k not in bekleyen and k not in denendi]
            bekleyen += aday[:K.N_SINIR - len(gecen)]
        if not bekleyen:
            return kayit


def _indir_kume(o, man, p, asama, sayac, keys, kayit, lp, ham_tut):
    from concurrent.futures import ThreadPoolExecutor
    cl = o.istemci()
    isler = []
    for k in keys:
        q = istek_tanimi(p, k, man)
        hedef = ham_yolu(o, asama, p, k)
        os.makedirs(os.path.dirname(hedef), exist_ok=True)
        if os.path.exists(hedef):
            os.remove(hedef)
        isler.append((k, q, hedef))

    def bir(arg):
        k, q, hedef = arg
        url = I.dataselect_url(q['servis'], q['ag'], q['istasyon'], q['konum'], q['kanallar'], q['bas'], q['son'],
                               taban=o.servis)
        r = cl.iste(q['servis'], url, hedef=hedef)
        if r['durum'] == 'yok' and p['bolge'] == 'Parkfield' and q['servis'] == 'ncedc':
            url = I.dataselect_url('earthscope', q['ag'], q['istasyon'], q['konum'], q['kanallar'], q['bas'],
                                   q['son'], taban=o.servis)
            r = cl.iste('earthscope', url, hedef=hedef)
        return k, url, r, hedef
    servisler = {}
    for x in isler:
        servisler.setdefault(x[1]['servis'], []).append(x)
    with ThreadPoolExecutor(max(1, I.AKIS * len(servisler))) as ex:
        sonuclar = list(ex.map(bir, isler))
    for k, url, r, hedef in sonuclar:
        satir = dict(anahtar=f"{p['id']}|{k[0]}.{k[1]}", pencere=p['id'], ag=k[0], istasyon=k[1], url=url,
                     http=r['http'], bayt=r.get('bayt', 0), sha256=r.get('sha256'), durum=r['durum'])
        if r['durum'] == 'tamam':
            try:
                rr, meta = istasyon_isle(o, p, k, man, hedef, lp=lp, mda=False)
            except I.BicimHata as e:
                satir.update(durum='bicim_hatasi', hata=str(e))
                sayac.ekle(satir)
                continue
            meta['lp'] = 'lp' in rr
            satir.update(ortu_R=meta['ortu_R'], ortu_W=meta['ortu_W'], dusme=meta['dusme'])
            zy = zarf_yolu(o, p, k)
            if os.path.exists(zy):
                os.remove(zy)                     # yarım kalmış önceki deneme (günlükte yok)
            k0, _ = pencere_ekseni(p)
            sha = I.zarf_yaz(zy, k0, rr, meta)
            z = dict(meta, sha256=sha, dosya=os.path.relpath(zy, o.zarf))
            satir_ekle(o.yol('tr7_zarf_sha256.jsonl'), z)
            kayit[k] = z
            if not ham_tut:
                os.remove(hedef)
        else:
            if r['durum'] in ('yok', 'kisitli', 'istemci_hatasi'):
                z = dict(pencere=p['id'], ag=k[0], istasyon=k[1], dusme=r['durum'], sha256=None)
                satir_ekle(o.yol('tr7_zarf_sha256.jsonl'), z)
                kayit[k] = z
        sayac.ekle(satir)


def hata_denetimi(o, sayac, asama, yeniden=None):
    """§10 madde 6: biçim payı > %1 → KosuDur; servis payı > %10 → tek yeniden deneme turu (yeniden(), bir kez);
    sonra hâlâ > %10 ise eksikler örtü kuralıyla düşer. Dönüş: servis payı."""
    bp, nb, n200 = sayac.bicim_payi()
    if bp > BICIM_HATA_PAY:
        raise KosuDur(f'{asama}: biçim hatası payı {bp:.3f} > %1 ({nb}/{n200}); kalan pencereler işlenmeden durur, '
                      f'"veri yok" yazılmaz (§10 madde 6)')
    sp = sayac.servis_payi()
    if sp > SERVIS_HATA_PAY and not sayac.yeniden_tur and yeniden is not None:
        satir_ekle(sayac.yol, dict(tur='yeniden_tur', zaman=simdi(), servis_payi=sp))
        sayac.yeniden_tur = True
        o.log(f'{asama}: servis hatası payı {sp:.3f} > %10: algılama hesaplanmadan durdu; tek yeniden deneme turu')
        o.uyku(o.yeniden_bekle)
        yeniden()
        sp = sayac.servis_payi()
        bp, nb, n200 = sayac.bicim_payi()
        if bp > BICIM_HATA_PAY:
            raise KosuDur(f'{asama}: biçim hatası payı {bp:.3f} > %1')
    return sp


def yeniden_dene(o, D, man, asama, sayac, pencereler, kayitlar, lp, ham_tut):
    def f():
        for p in pencereler:
            keys = [(r['ag'], r['istasyon']) for a, r in sayac.son.items()
                    if r['pencere'] == p['id'] and r['durum'] == 'servis_hatasi']
            if keys:
                _indir_kume(o, man, p, asama, sayac, keys, kayitlar.setdefault(p['id'], {}), lp, ham_tut)
                pencere_indir(o, D, man, p, asama, sayac, lp=lp, ham_tut=ham_tut, kayit=kayitlar[p['id']],
                              segler=p.get('_segler'))
    return f


# ====================================================================== pencere-segment kurulumu (§6.0, §6.2.5–§6.5)
def zarf_kayitlari(o):
    """tr7_zarf_sha256.jsonl → {pencere: {(ağ, istasyon): kayıt}} (son satır geçerli)."""
    out = {}
    for r in jsonl_oku(o.yol('tr7_zarf_sha256.jsonl')):
        out.setdefault(r['pencere'], {})[(r['ag'], r['istasyon'])] = r
    return out


def gecenler(p, s, kayit):
    """Örtüden geçen istasyonlar (`iz_sira` sırasıyla) ve 12 sınırıyla kullanılanlar (§6.0)."""
    g = [k for k in p['seg'].get(s, []) if k in kayit and kayit[k].get('dusme') is None and kayit[k].get('sha256')]
    return g, g[:K.N_SINIR]


def yerel_olaylar(o, man, p):
    out = []
    for kt in (('comcat',) if p['bolge'] == 'Parkfield' else ('emsc', 'comcat')):
        r = man['katalog'].get(f"{p['id']}|yerel|{kt}")
        if r is None:
            raise KosuDur(f'manifestte yerel katalog yanıtı yok: {p["id"]} {kt}')
        out += katalog_ayristir(kt, _govde(o.zyol('katalog'), r))
    return out


def e1_olay_listesi(D, man, p, s):
    """E1 olayları [dict(id, M, t0, P, S)]: tetikleyici ve Parkfield pencerelerinde `tr7_e1_maske.csv` (§3.4),
    negatiflerde manifestteki ComCat yanıtından (§3.5 b). Dışlananlar (tetikleyici, ikiz) zaten yoktur."""
    if p['tur'] == 'tet':
        return e1_olaylari_csv(D['e1'], p['tetikleyici'], s)
    ol = {}
    for r in man['e1_negatif']:
        if r['pencere'] == p['id'] and r['segment'] == s:
            x = ol.setdefault(r['olay'], dict(id=r['olay'], M=r['M'], t0=r['t0']))
            x[r['faz']] = r['varis']
    return list(ol.values())


def ws_kur(o, D, man, p, s, kayit):
    """(pencere, segment): zarf deposundan istasyon kayıtları, maske (E1 ∪ yerel), Wb, maskeli paylar (§9.1)."""
    gecen, kul = gecenler(p, s, kayit)
    k0, n = pencere_ekseni(p)
    out = dict(pencere=p['id'], segment=s, birim=p['birim'], n_gecen=len(gecen), kul=kul, k0=k0, n=n)
    if len(gecen) < K.N_IST_MIN:
        out['durum'] = 'dustu'
        return out
    m_e1 = K.saniye_maskesi(K.e1_araliklar(e1_olay_listesi(D, man, p, s), None, None), k0, n)
    m_yer = K.saniye_maskesi(K.yerel_araliklar(yerel_olaylar(o, man, p), K.SEGMENT[s]), k0, n)
    maske = m_e1 | m_yer
    ist = []
    Wu = np.zeros(n, bool)
    Ru = np.zeros(n, bool)
    for k in kul:
        x = p['ist'][k]
        rec = kayit[k]
        z = I.zarf_oku(o.zyol(rec['dosya']), rec['sha256'])
        if z['k0'] != k0:
            raise KosuDur(f'zarf ekseni uyuşmuyor: {rec["dosya"]}')
        C = K.f32(K.birlesik([z['e' + c].astype(np.float64) for c in rec['bilesen']]))
        R, W = eksen_dilim(x, k0)
        ist.append(K.istasyon(C, z['C051'].astype(np.float64), R, W, maske, f'{k[0]}.{k[1]}'))
        Wu[W[0]:W[1]] = True
        Ru[R[0]:R[1]] = True

    def pay(m, u):
        return round(float(m[u].mean()), 4) if u.any() else None
    out.update(durum='tarandi', ist=ist, maske=maske, Wb=(min(x['W'][0] for x in ist), max(x['W'][1] for x in ist)),
               paylar=dict(W=pay(maske, Wu), W_e1=pay(m_e1, Wu), W_yerel=pay(m_yer, Wu), R=pay(maske, Ru),
                           R_e1=pay(m_e1, Ru), R_yerel=pay(m_yer, Ru)))
    return out


def maske_ayiklanan(ws, kumeler):
    """§6.5.4 'maske' nedeni (bilgi): maskesiz kurulumda tutarlı olup maskeli saniyelerle kesişen ve maskeli kurulumda
    karşılığı (I′ örtüşmesi) olmayan küme sayısı (okuma O-33)."""
    if not ws['maske'].any():
        return 0
    sifir = np.zeros_like(ws['maske'])
    ist0 = [K.istasyon(x['Cy'], x['Cd'], x['R'], x['W'], sifir, x['ad']) for x in ws['ist']]
    say = 0
    for k in K.kumeler(ist0, sifir, ws['Wb']):
        a, b = k['Ip']
        if ws['maske'][a:b].any() and not any(kk['Ip'][0] < b and a < kk['Ip'][1] for kk in kumeler):
            say += 1
    return say


def kume_ozet(ws, k):
    k0, m = ws['k0'], ws['maske']
    oran = []
    for i in k['uyeler']:
        x = ws['ist'][i]
        ps = [(a, b) for kk, a, b in k['parcalar'] if kk == i]
        cps = [float(np.nanmax(x['Cy'][a:b])) for a, b in ps if np.isfinite(x['Cy'][a:b]).any()]
        lo, hi = k['Ip']
        seg = x['Cy'][lo:hi][~m[lo:hi]]
        seg = seg[np.isfinite(seg)]
        if cps and len(seg) and np.median(seg) > 0:
            oran.append(max(cps) / float(np.median(seg)))
    return dict(I=[k0 + k['I'][0], k0 + k['I'][1]], Ip=[k0 + k['Ip'][0], k0 + k['Ip'][1]],
                uyeler=[ws['ist'][i]['ad'] for i in k['uyeler']], n_cift_tutarli=k['n_cift_tutarli'],
                korelasyon=k['korelasyon'], bayrak=k['bayrak'], sag=k['sag'], darbe_pay=k['bayrak']['darbe_pay'],
                cp_medyan_medyan=round(float(np.median(oran)), 3) if oran else None, sure_s=k['Ip'][1] - k['Ip'][0])


def algila(o, D, man, p, s, kayit, asama):
    """Bir (pencere, segment) için algılama satırı (§6.3, §6.5). Dönüş (satır, ws, sonuç)."""
    ws = ws_kur(o, D, man, p, s, kayit)
    sat = dict(asama=asama, pencere=p['id'], segment=s, birim=p['birim'], tur=p['tur'], sira=p.get('sira'),
               tetikleyici=p['tetikleyici'], n_gecen=ws['n_gecen'], kullanilan=[f'{k[0]}.{k[1]}' for k in ws['kul']],
               durum=ws['durum'], zaman=simdi())
    if ws['durum'] != 'tarandi':
        sat['algilama'] = None
        return sat, ws, None
    r = K.pencere_algila(ws['ist'], ws['maske'], ws['Wb'])
    k0 = ws['k0']
    sat.update(algilama=bool(r['algilama']), kume_sayisi=len(r['kumeler']),
               ayiklanan=dict(r['ayiklanan'], maske=maske_ayiklanan(ws, r['kumeler'])),
               kumeler=[kume_ozet(ws, k) for k in r['kumeler']], paylar=ws['paylar'],
               en_uzun_kume_s=max((k['Ip'][1] - k['Ip'][0] for k in r['kumeler'] if k['sag']), default=0),
               Wb=[k0 + ws['Wb'][0], k0 + ws['Wb'][1]],
               asimlar={x['ad']: [[k0 + a, k0 + b] for a, b in x['ax']] for x in ws['ist']},
               sigma_sifir=[x['ad'] for x in ws['ist'] if x['sigma_sifir']])
    return sat, ws, r


# ---------------------------------------------------------------------- §6.4 modülasyon, §6.6 τ_ölç, §7.5 kestirici
def lp_referans(man, p, s, kayit):
    """§6.4: PGV'ye uygun, W ve R örtüsü ≥ %90, segment orta noktasına en yakın istasyon (penceredeki bütün
    istasyonlardan; 12 sınırının dışı). Eşitlikte ağ ve istasyon adı alfabetik. Yoksa None."""
    la, lo = K.orta(s)
    aday = sorted((K.hav(la, lo, x['la'], x['lo']), k[0], k[1]) for k, x in p['ist'].items()
                  if k in kayit and kayit[k].get('dusme') is None and kayit[k].get('sha256') and kayit[k].get('lp')
                  and pgv_uygun(man, p, k))
    return (aday[0][1], aday[0][2]) if aday else None


def modulasyon(o, p, ws, kume, ref, kayit, rng):
    """Bir kümenin modülasyon p'si (§6.4). Dönüş dict(M, p) ya da None (ölçülemedi)."""
    if ref is None:
        return None
    rec = kayit[ref]
    z = I.zarf_oku(o.zyol(rec['dosya']), rec['sha256'])
    R, W = eksen_dilim(p['ist'][ref], ws['k0'])
    W0, W1 = W
    if W1 - W0 <= 2 * K.MOD_KAY + 1:
        return None
    cfs = []
    for c in ('vZ', 'vR', 'vT'):
        v = z.get(c)
        if v is not None and np.isfinite(v[W0:W1]).any():
            cfs.append(K.faz_cos(v[W0:W1].astype(np.float64)))
    if not cfs:
        return None
    m = ws['maske'][W0:W1]
    Ls = np.array([ws['ist'][i]['L'][W0:W1] for i in kume['uyeler']])
    Ls[:, m] = np.nan
    with np.errstate(all='ignore'):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', RuntimeWarning)
            Lk = np.nanmedian(Ls, axis=0)
    gec = np.isfinite(Lk) & ~m
    a = max(kume['I'][0], W0) - W0
    b = min(kume['I'][1], W1) - W0
    if b - a < 3:
        return None
    M, pp = K.mod_p(np.where(gec, Lk, 0.0), cfs, a, b, gec, rng)
    return dict(M=round(M, 4), p=pp, referans=f'{ref[0]}.{ref[1]}', bilesen=len(cfs))


def tau_olc(o, man, p, s, kayit):
    """§6.6: PGV_ölç = uygun istasyonlarda en büyük_{t∈W} max(|v_Z|, |v_R|, |v_T|) değerlerinin medyanı (segmentin
    bütün istasyonları; 12 sınırı dışı). Dönüş dict(tau, tau_z, n) ya da None ('ölçülemedi')."""
    pg, pz = [], []
    k0, n = pencere_ekseni(p)
    for k in p['seg'].get(s, []):
        rec = kayit.get(k)
        if not rec or rec.get('dusme') is not None or not rec.get('lp') or not pgv_uygun(man, p, k):
            continue
        z = I.zarf_oku(o.zyol(rec['dosya']), rec['sha256'])
        R, W = eksen_dilim(p['ist'][k], k0)
        v = K.pgv_ist(z['vZ'].astype(float), z['vR'].astype(float), z['vT'].astype(float), W)
        vz = K.pgv_ist(z['vZ'].astype(float), z['vZ'].astype(float), z['vZ'].astype(float), W)
        if v is not None:
            pg.append(v)
        if vz is not None:
            pz.append(vz)
    if not pg:
        return None
    return dict(tau=round(K.tau_kpa(float(np.median(pg))), 3),
                tau_z=round(K.tau_kpa(float(np.median(pz))), 3) if pz else None, n=len(pg))


def kestirici(p, ws, kume, s):
    """§7.5: a_i · r_i / 25 (nm/s), küme medyanı."""
    v = []
    for i in kume['uyeler']:
        a = K.kestirici_ist(ws['ist'][i], kume['Ip'], ws['maske'])
        if a is not None:
            x = p['ist'][ws['kul'][i]]
            v.append(a * K.r_hiposantr(x['la'], x['lo'], s) / K.MDA_DERIN * 1e9)
    return round(float(np.median(v)), 4) if v else None


# ---------------------------------------------------------------------- §7.4 MDA girdisi
def _yanit_fn(inv, x, kanal, t):
    from obspy import UTCDateTime
    ch = inv.select(network=x['ag'], station=x['istasyon'], location=x['konum'], channel=kanal, time=UTCDateTime(t))
    kan = [c for n in ch for s_ in n for c in s_]
    if not kan or kan[0].response is None:
        return None
    resp = kan[0].response
    S = float(resp.instrument_sensitivity.value)
    on = {}

    def f(n, fs):
        if (n, fs) not in on:
            H, _ = resp.get_evalresp_response(1.0 / fs, n, output='VEL')
            on[(n, fs)] = H[:n // 2 + 1] / S
        return on[(n, fs)]
    return f


def mda_girdisi(o, man, p, ws, asama):
    """Algılama vermemiş (pencere, segment) için ham veriden parça analitik sinyalleri ve yanıt çarpanları."""
    k0, n = ws['k0'], ws['n']
    veri, hn, rk = [], [], []
    s = ws['segment']
    for k in ws['kul']:
        x = p['ist'][k]
        yol = ham_yolu(o, asama, p, k)
        if not os.path.exists(yol):
            raise KosuDur(f'MDA için ham veri yok: {yol} (indir–zarfla–sil sırası bozuldu)')
        oz = kanal_ozet(man, p, k)
        inv = stationxml_oku(o, x)
        pen = ist_pencere(x, k0, n)
        pen['W_mda'] = [k0 + ws['Wb'][0], k0 + ws['Wb'][1]]
        ist = dict(ag=x['ag'], istasyon=x['istasyon'], konum=x['konum'], z_kanal=x['z_kanal'], yatay=oz['yatay'],
                   ozet=oz['ozet'], baz=0.0)
        r = I.isle_istasyon_penceresi(yol, inv, ist, pen, mda=True)
        if r['dusme'] is not None:
            raise KosuDur(f'MDA yeniden işlemede istasyon düştü ({r["dusme"]}): {k}')
        veri.append({c: v for c, v in r['mda'].items()})
        kan = {'Z': x['z_kanal']}
        if len(oz['yatay']) == 2:
            kan.update(N=oz['yatay'][0], E=oz['yatay'][1])
        hn.append({c: _yanit_fn(inv, x, kan[c], x['W'][0]) for c in r['mda']})
        rk.append(K.r_hiposantr(x['la'], x['lo'], s))
    return veri, hn, rk


def rng_durum(rng):
    return json.loads(json.dumps(rng.bit_generator.state))


def rng_kur(durum):
    rng = np.random.default_rng(K.MDA_TOHUM)
    if durum is not None:
        rng.bit_generator.state = durum
    return rng


def mda_csv_yaz(o):
    """tr7_mda.csv: her (segment, negatif pencere, deneme, A basamağı) için algılama E/H ve başlangıç (§6.1 K6).
    Kaynak, atomik satırlı tr7_mda.jsonl'dir; csv her pencereden sonra yeniden üretilir."""
    rows = jsonl_oku(o.yol('tr7_mda.jsonl'))
    tmp = o.yol('tr7_mda.csv.tmp')
    with open(tmp, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['asama', 'segment', 'pencere', 'birim', 'sira', 'deneme', 'baslangic_s', 'A_nm_s', 'algilama'])
        for r in rows:
            for j, d in enumerate(r['denemeler']):
                for A, al in zip(K.A_BASAMAK, d['alg']):
                    w.writerow([r['asama'], r['segment'], r['pencere'], r['birim'], r['sira'], j + 1, d['bas'],
                                f'{A:.6g}', 'E' if al else 'H'])
    os.replace(tmp, o.yol('tr7_mda.csv'))


def mda_ozeti(satirlar):
    den = [d for r in satirlar for d in r['denemeler']]
    if not den:
        return K.mda_ozet([0.0] * len(K.A_BASAMAK), 0)
    P = [float(np.mean([d['alg'][j] for d in den])) for j in range(len(K.A_BASAMAK))]
    out = K.mda_ozet(P, len(den))
    out['P'] = [round(x, 4) for x in P]
    return out


# ====================================================================== K0-tam (§4.2)
def birim_t0(D, birim):
    ids = WHARTON if birim == 'WHARTON2012' else (birim,)
    return min(D['olay'][i]['t0'] for i in ids if i in D['olay'])


def tarananlar(D, kayitlar, onsayim=False):
    """{segment: {birim: [tetikleyici, ...]}}: ≥3 istasyonu örtüden geçen tetikleyici pencereleri (Marmara)."""
    out = {s: {} for s in MARMARA_SEG}
    for p in D['pen'].values():
        if p['tur'] != 'tet' or p['bolge'] != 'Marmara':
            continue
        for s, keys in p['seg'].items():
            ng = len(keys) if onsayim else len(gecenler(p, s, kayitlar.get(p['id'], {}))[0])
            if ng >= K.N_IST_MIN:
                out[s].setdefault(p['birim'], []).append(p['tetikleyici'])
    return out


def k0_tam(D, kayitlar, onsayim=False):
    """§4.2: segment başına ≥3 istasyonla taranabilen ana birim sayısı n (×1, ×1/3, ×3), bant; S5/S6 için ayrıca
    2009 sonrası birimlerin bağımsız satırı. Birimin kaba τ'su sağ kalan pencerelerindeki olayların en büyüğü (Ö1).
    onsayim=True: listedeki her istasyon geçer (önsayımın yeniden üretimi; `k0` komutu)."""
    tar = tarananlar(D, kayitlar, onsayim)
    out = dict(taranan={s: {b: v for b, v in tar[s].items()} for s in tar})
    for ad, c in (('x1', 1.0), ('x1/3', 1 / 3), ('x3', 3.0)):
        sat = {}
        for s in MARMARA_SEG:
            def say_(filtre):
                b = {}
                km = []
                for birim, tets in tar[s].items():
                    tau = max(D['olay'][t]['tau'][s] for t in tets) * c
                    if tau < K.TAU_ESIK - 1e-12:
                        continue
                    if D['olay'][tets[0]]['kahramanmaras']:
                        km.append(birim)
                        continue
                    if filtre(birim):
                        b[birim] = tau
                ts = sorted(b.values(), reverse=True)
                return dict(n=len(ts), bant=K.bant(len(ts)), tau_n=round(ts[-1], 2) if ts else None,
                            tau8=round(ts[7], 2) if len(ts) >= 8 else None,
                            tau5=round(ts[4], 2) if len(ts) >= 5 else None,
                            birimler=sorted(b, key=lambda x: (-b[x], x)), tau={k: round(v, 3) for k, v in b.items()},
                            kahramanmaras_bilgi=sorted(km))
            sat[s] = say_(lambda b: True)
            if s in BAGIMSIZ_SEG:
                sat[s]['bagimsiz'] = say_(lambda b: birim_t0(D, b) >= BAGIMSIZ_BAS)
        out[ad] = sat
    out['not'] = ('x3 alt sınırdır (yalnız x1 adayları listede; listede kaba τ ≥ 2 kPa olmayan çift yok, okuma O-34); '
                  'x1/3 ve x3 bilgi satırıdır. Bant, tetikleyici pencerelerinde hiçbir algılama hesaplanmadan yazıldı.')
    return out


# ====================================================================== aşamalar
def _pencereler(D, filtre):
    return sorted([p for p in D['pen'].values() if filtre(p)], key=lambda p: (p['t0'], p['id']))


def _planli(man, ps):
    return sum(len(man['plan'].get(p['id'], [])) for p in ps)


def indir_kume(o, D, man, asama, ps, lp, ham_tut):
    """Aşamanın bütün pencerelerini indirir ve zarflar (algılama yok); biçim ve servis hata payları (§10 madde 6)."""
    sayac = AsamaSayac(o.yol(f'tr7_indirme_{asama}.jsonl'), _planli(man, ps))
    kayitlar = {}
    for p in ps:
        kayitlar[p['id']] = pencere_indir(o, D, man, p, asama, sayac, lp=lp, ham_tut=ham_tut,
                                          segler=p.get('_segler'))
    sp = hata_denetimi(o, sayac, asama, yeniden=yeniden_dene(o, D, man, asama, sayac, ps, kayitlar, lp, ham_tut))
    return dict(servis_payi=round(sp, 4), bicim_payi=round(sayac.bicim_payi()[0], 4), planli=sayac.planli,
                istek=len(sayac.son), yeniden_tur=sayac.yeniden_tur)


def asama_K1_indirme(o, D, d, kip):
    man = manifest_oku(o)
    ps = [D['pen']['pk|tohoku']]
    oz = indir_kume(o, D, man, 'K1-indirme', ps, lp=True, ham_tut=False)
    kay = zarf_kayitlari(o).get('pk|tohoku', {})
    oz['gecen'] = len(gecenler(ps[0], 'PK', kay)[0])
    return oz


def _algilama_satirlari(o, asama):
    return {(r['pencere'], r['segment']): r for r in jsonl_oku(o.yol(f'tr7_algilama_{asama}.jsonl'))}


def algilama_turu(o, D, man, asama, ps_seg):
    """ps_seg: [(pencere, segment)]: yazılmamış olanların algılamasını yazar (sürdürmede yazılmışlar yeniden
    hesaplanmaz)."""
    yazili = _algilama_satirlari(o, asama)
    kay = zarf_kayitlari(o)
    for p, s in ps_seg:
        if (p['id'], s) in yazili:
            continue
        sat, _, _ = algila(o, D, man, p, s, kay.get(p['id'], {}), asama)
        satir_ekle(o.yol(f'tr7_algilama_{asama}.jsonl'), sat)
        yazili[(p['id'], s)] = sat
    return yazili


def mda_turu(o, D, man, asama, isler, rng_bas):
    """isler: [(pencere, segment, n_bas)] çekiliş sırasıyla. Yazılmış satırlar atlanır; üreteç son satırın durumundan
    sürer (§7.4, §10 madde 6). Dönüş: (satırlar, son üreteç durumu)."""
    yazili = [r for r in jsonl_oku(o.yol('tr7_mda.jsonl')) if r['asama'] == asama]
    bitti = {(r['pencere'], r['segment']) for r in yazili}
    durum = yazili[-1]['rng_sonra'] if yazili else rng_bas
    kay = zarf_kayitlari(o)
    for p, s, nb in isler:
        if (p['id'], s) in bitti:
            continue
        rng = rng_kur(durum)
        ws = ws_kur(o, D, man, p, s, kay.get(p['id'], {}))
        veri, hn, rk = mda_girdisi(o, man, p, ws, asama)
        den = K.mda_deneme(ws['ist'], veri, hn, rk, ws['maske'], ws['Wb'], ws['k0'], rng, n_bas=nb)
        durum = rng_durum(rng)
        satir_ekle(o.yol('tr7_mda.jsonl'), dict(asama=asama, pencere=p['id'], segment=s, birim=p['birim'],
                                                sira=p.get('sira'), denemeler=den, rng_sonra=durum, zaman=simdi()))
        mda_csv_yaz(o)
    return [r for r in jsonl_oku(o.yol('tr7_mda.jsonl')) if r['asama'] == asama], durum


def ham_sil(o, asama, p=None):
    import shutil
    y = o.zyol('ham', asama) if p is None else o.zyol('ham', asama, p['id'].replace('|', '_'))
    if os.path.isdir(y):
        shutil.rmtree(y)


def asama_K1_negatif(o, D, d, kip):
    """Parkfield negatif pencereleri: indir (ham tutulur), algıla, MDA (pencere başına üç başlangıç), ham sil."""
    man = manifest_oku(o)
    ps = sorted([p for p in D['pen'].values() if p['id'].startswith('pkneg|')], key=lambda p: p['sira'])
    oz = indir_kume(o, D, man, 'K1-negatif', ps, lp=False, ham_tut=True)
    sat = algilama_turu(o, D, man, 'K1-negatif', [(p, 'PK') for p in ps])
    for p in ps:
        if sat[(p['id'], 'PK')]['algilama'] is not False:
            ham_sil(o, 'K1-negatif', p)
    isler = [(p, 'PK', PK_MDA_BAS) for p in ps if sat[(p['id'], 'PK')]['algilama'] is False]
    mda, durum = mda_turu(o, D, man, 'K1-negatif', isler, None)
    ham_sil(o, 'K1-negatif')
    N = sum(1 for p in ps if sat[(p['id'], 'PK')]['durum'] == 'tarandi')
    f = sum(1 for p in ps if sat[(p['id'], 'PK')]['algilama'])
    m = mda_ozeti(mda)
    sonuc = dict(N_PK=N, f_PK=f, FAR_PK=round(f / N, 4) if N else None, mda=m, indirme=oz, mda_rng_son=durum)
    json_yaz(o.yol('tr7_k1_negatif.json'), sonuc)
    return dict(N_PK=N, f_PK=f, A90_PK=m['A90'], mda_rng_son=durum)


def e1_bireysel_sonlar(olaylar):
    """(b′ i): birleştirilmemiş E1 aralıklarının bitişleri (epoch)."""
    out = []
    for e in olaylar:
        for faz, k in K.e1_kurallar(e['M']):
            if e.get(faz) is not None:
                out.append(e[faz] + k)
    return sorted(out)


def asama_K1_algilama(o, D, d, kip):
    from obspy.geodetics import locations2degrees
    man = manifest_oku(o)
    p = D['pen']['pk|tohoku']
    kay = zarf_kayitlari(o).get(p['id'], {})
    ad = 'K1-algılama' if kip != 'uygulama_hatasi' else 'K1-algılama-2'
    sat, ws, r = algila(o, D, man, p, 'PK', kay, ad)
    satir_ekle(o.yol(f'tr7_algilama_{ad}.jsonl'), sat)
    neg = json_oku(o.yol('tr7_k1_negatif.json'))
    th = D['olay'][TOHOKU]
    out = dict(algilama_satiri=sat, N_PK=neg['N_PK'], f_PK=neg['f_PK'], FAR_PK=neg['FAR_PK'],
               A50_PK=neg['mda']['A50'], A90_PK=neg['mda']['A90'], mda_deneme=neg['mda']['n_deneme'])
    if ws['durum'] != 'tarandi':
        out['dal'] = 'a'
    else:
        k0 = ws['k0']
        ka, kz = K.epoch(K1_ARALIK[0]), K.epoch(K1_ARALIK[1]) + 1           # kapsayıcı uç (okuma O-35)
        sag = [k for k in r['kumeler'] if k['sag']]
        k1k = [k for k in sag if k0 + k['Ip'][0] < kz and k0 + k['Ip'][1] > ka]
        ol = e1_olay_listesi(D, man, p, 'PK')
        sonlar = e1_bireysel_sonlar(ol)
        la, lo = K.orta('PK')
        deg = locations2degrees(th['la'], th['lo'], la, lo)
        cf = K.cekirdek_fazlari(th['derinlik'], deg)
        varis = sorted(K.epoch(th['t0']) + t for v in cf.values() for t in v)
        tani = []
        belirsiz = []
        for k in k1k:
            b = k0 + k['Ip'][0]
            onceki = [e for e in sonlar if e <= b]
            i_ = any(0 <= b - e <= BPRIME_MASKE_S for e in sonlar)
            ii = any(BPRIME_FAZ[0] <= b - v <= BPRIME_FAZ[1] for v in varis)
            belirsiz.append(i_ or ii)
            Ip = (k0 + k['Ip'][0], k0 + k['Ip'][1])
            tani.append(dict(Ip=list(Ip), onceki_maske_sonuna_s=round(b - max(onceki), 1) if onceki else None,
                             cekirdek_faza_en_yakin_s=round(min(abs(b - v) for v in varis), 1) if varis else None,
                             b_prime_i=i_, b_prime_ii=ii,
                             P_M6x_icinde=[e['id'] for e in ol if 6.0 <= e['M'] < 7.0 and e.get('P') is not None
                                           and Ip[0] <= e['P'] < Ip[1]],
                             S_M6x_maskesiz_icinde=[e['id'] for e in ol if 6.0 <= e['M'] < 7.0 and e.get('S') is not None
                                                    and Ip[0] <= e['S'] < Ip[1]
                                                    and not ws['maske'][int(math.floor(e['S'])) - k0]
                                                    if 0 <= int(math.floor(e['S'])) - k0 < ws['n']]))
        out.update(kume_ayiklama_oncesi=len(r['kumeler']), k1_kumeleri=tani,
                   cekirdek_fazlari={f: [round(t, 1) for t in v] for f, v in cf.items()})
        if k1k:
            out['dal'] = "b'" if all(belirsiz) else 'b'
        elif not r['algilama'] and isinstance(neg['mda']['A90'], float) and neg['mda']['A90'] <= A90_PK_TAVAN:
            out['dal'] = 'c'
        else:
            out['dal'] = 'd'
        out['ayirt_degil'] = out['dal'] in ('b', "b'") and (neg['N_PK'] < N_PK_MIN or (
            neg['N_PK'] > 0 and neg['f_PK'] / neg['N_PK'] > FAR_PK_ESIK))
        # bilgi: modülasyon (K7), A_PK, τ_ölç / kaba τ, BK.PKD aşımları
        rng = np.random.default_rng(K.MOD_TOHUM)
        ref = lp_referans(man, p, 'PK', kay)
        mods = [modulasyon(o, p, ws, k, ref, kay, rng) for k in k1k]
        out['modulasyon'] = mods
        out['lp_referans'] = f'{ref[0]}.{ref[1]}' if ref else None
        out['mod_gecti'] = any(m is not None and m['p'] <= K.MOD_ESIK for m in mods)
        aps = [kestirici(p, ws, k, 'PK') for k in k1k]
        aps = [a for a in aps if a is not None]
        out['A_PK'] = max(aps) if aps else None
        t = tau_olc(o, man, p, 'PK', kay)
        out['tau_olc'] = t
        out['tau_olc_bolu_kaba'] = round(t['tau'] / PK_TAU_KABA, 4) if t else None
        pk = kay.get(PKD)
        if pk and pk.get('dusme') is None and pk.get('sha256'):
            z = I.zarf_oku(o.zyol(pk['dosya']), pk['sha256'])
            C = K.f32(K.birlesik([z['e' + c].astype(np.float64) for c in pk['bilesen']]))
            R, W = eksen_dilim(p['ist'][PKD], k0)
            x = K.istasyon(C, z['C051'].astype(np.float64), R, W, ws['maske'], 'BK.PKD')
            out['PKD_asimlari'] = [[k0 + a, k0 + b] for a, b in x['ax']]
        else:
            out['PKD_asimlari'] = None if not pk else f'düştü ({pk.get("dusme")})'
    out.setdefault('ayirt_degil', False)
    out.setdefault('mod_gecti', False)
    out.setdefault('A_PK', None)
    out.setdefault('tau_olc_bolu_kaba', None)
    json_yaz_x(o.yol('tr7_k1.json' if ad == 'K1-algılama' else 'tr7_k1_2.json'), out)
    return dict(k1_dal=out['dal'], ayirt_degil=out['ayirt_degil'], mod_gecti=out['mod_gecti'])


def asama_Marmara_indirme(o, D, d, kip):
    man = manifest_oku(o)
    ps = _pencereler(D, lambda p: p['tur'] == 'tet' and p['bolge'] == 'Marmara')
    oz = indir_kume(o, D, man, 'Marmara-indirme', ps, lp=True, ham_tut=False)
    k0 = k0_tam(D, zarf_kayitlari(o))
    k0['indirme'] = oz
    json_yaz_x(o.yol('tr7_k0_tam.json'), k0)
    return dict(n={s: k0['x1'][s]['n'] for s in MARMARA_SEG}, bant={s: k0['x1'][s]['bant'] for s in MARMARA_SEG})


def k0_oku(o):
    with open(o.yol('tr7_k0_tam.json'), encoding='utf-8') as f:
        return json.load(f)


def negatif_isleri(D, k0):
    """Marmara negatif pencereleri: her segmentte K0-tam'da taranan birimlerin (Kahramanmaraş dahil, bilgi) negatifleri.
    Wharton'ın alt penceresi o segmentte taranmışsa (tetikleyici penceresi ≥3 istasyon) işlenir (okuma O-36)."""
    ps = {}
    for s in MARMARA_SEG:
        for birim, tets in k0['taranan'][s].items():
            for p in D['pen'].values():
                if p['tur'] == 'neg' and p['birim'] == birim and p['tetikleyici'] in tets:
                    q = ps.setdefault(p['id'], p)
                    q.setdefault('_segler', [])
                    if s not in q['_segler']:
                        q['_segler'].append(s)
    return sorted(ps.values(), key=lambda p: (birim_t0(D, p['birim']), p['sira'], p['t0']))


def asama_Marmara_negatif(o, D, d, kip):
    man = manifest_oku(o)
    k0 = k0_oku(o)
    ps = negatif_isleri(D, k0)
    oz = indir_kume(o, D, man, 'Marmara-negatif', ps, lp=False, ham_tut=True)
    sat = algilama_turu(o, D, man, 'Marmara-negatif', [(p, s) for s in MARMARA_SEG for p in ps
                                                         if s in p['_segler']])
    km = {b for s in MARMARA_SEG for b in k0['x1'][s]['kahramanmaras_bilgi']} | set(KAHRAMANMARAS)
    # birim-pencere (Wharton: iki alt pencere tek negatif pencere, §7.3)
    isler = []
    gerek = set()
    for s in MARMARA_SEG:
        ana = sorted([b for b in k0['taranan'][s] if b not in km and D['olay'][k0['taranan'][s][b][0]]['kahramanmaras']
                      is False], key=lambda b: birim_t0(D, b))
        for b in ana:
            for sira in range(1, 11):
                alt = sorted([p for p in ps if p['birim'] == b and p['sira'] == sira and s in p['_segler']],
                             key=lambda p: p['t0'])
                ss = [sat[(p['id'], s)] for p in alt]
                kul = [p for p, x in zip(alt, ss) if x['durum'] == 'tarandi']
                if kul and not any(x['algilama'] for x in ss):
                    isler.append((kul[0], s, 1))                    # Wharton: ana şok alt penceresi (okuma O-37)
                    gerek.add(kul[0]['id'])
    for p in ps:
        if p['id'] not in gerek:
            ham_sil(o, 'Marmara-negatif', p)
    k1n = json_oku(o.yol('tr7_k1_negatif.json'))
    mda, durum = mda_turu(o, D, man, 'Marmara-negatif', isler, k1n['mda_rng_son'])
    ham_sil(o, 'Marmara-negatif')
    out = dict(indirme=oz, segment={})
    for s in MARMARA_SEG:
        out['segment'][s] = k2_segment(D, k0, s, sat, ps, mda, km, None)
        if s in BAGIMSIZ_SEG:
            out['segment'][s]['bagimsiz'] = k2_segment(D, k0, s, sat, ps, mda, km, BAGIMSIZ_BAS)
        out['segment'][s]['kahramanmaras'] = {
            b: dict(N=sum(1 for p in ps if p['birim'] == b and s in p['_segler']
                          and sat[(p['id'], s)]['durum'] == 'tarandi'),
                    f=sum(1 for p in ps if p['birim'] == b and s in p['_segler'] and sat[(p['id'], s)]['algilama']))
            for b in k0['x1'][s]['kahramanmaras_bilgi']}
    out['mda_rng_son'] = durum
    json_yaz_x(o.yol('tr7_marmara_negatif.json'), out)
    return {s: dict(N=v['N'], f=v['f'], K2=v['K2']) for s, v in out['segment'].items()}


def k2_segment(D, k0, s, sat, ps, mda, km, bas):
    ana = [b for b in k0['taranan'][s] if b not in km and (bas is None or birim_t0(D, b) >= bas)]
    N = f = 0
    for b in ana:
        for sira in range(1, 11):
            ss = [sat[(p['id'], s)] for p in ps if p['birim'] == b and p['sira'] == sira and s in p['_segler']]
            if any(x['durum'] == 'tarandi' for x in ss):
                N += 1
                f += any(x['algilama'] for x in ss)
    m = mda_ozeti([r for r in mda if r['segment'] == s and r['birim'] in ana])
    return dict(N=N, f=f, FAR=round(f / N, 4) if N else None, K2=K.k2_gecer(f, N) if N else None,
                p_ust=round(K.cp_ust(f, N), 4) if N else None, mda=m, birimler=sorted(ana))


def asama_Marmara_algilama(o, D, d, kip):
    man = manifest_oku(o)
    k0 = k0_oku(o)
    ps = _pencereler(D, lambda p: p['tur'] == 'tet' and p['bolge'] == 'Marmara')
    isler = [(p, s) for p in ps for s in MARMARA_SEG if p['tetikleyici'] in k0['taranan'][s].get(p['birim'], [])]
    sat = algilama_turu(o, D, man, 'Marmara-algılama', isler)
    # modülasyon: kümeler birim (ana şok T0), segment, zaman sırasıyla; tek üreteç (§6.4; okuma O-38)
    rng = np.random.default_rng(K.MOD_TOHUM)
    kay = zarf_kayitlari(o)
    pen = {}
    for birim in sorted({p['birim'] for p in ps}, key=lambda b: birim_t0(D, b)):
        for s in MARMARA_SEG:
            for p in sorted([p for p in ps if p['birim'] == birim], key=lambda p: p['t0']):
                x = sat.get((p['id'], s))
                if x is None:
                    continue
                e = dict(birim=birim, tetikleyici=p['tetikleyici'], segment=s, algilama=x['algilama'],
                         W_payi=x.get('paylar', {}).get('W'), paylar=x.get('paylar'), mod=[], a=[])
                kk = kay.get(p['id'], {})
                if x['durum'] == 'tarandi':
                    e['tau_olc'] = tau_olc(o, man, p, s, kk)
                    if x['algilama']:
                        ws = ws_kur(o, D, man, p, s, kk)
                        r = K.pencere_algila(ws['ist'], ws['maske'], ws['Wb'])
                        ref = lp_referans(man, p, s, kk)
                        e['lp_referans'] = f'{ref[0]}.{ref[1]}' if ref else None
                        for k in sorted([k for k in r['kumeler'] if k['sag']], key=lambda k: k['Ip']):
                            e['mod'].append(modulasyon(o, p, ws, k, ref, kk, rng))
                            e['a'].append(kestirici(p, ws, k, s))
                pen[f"{p['id']}|{s}"] = e
    out = dict(pencere_segment=pen)
    json_yaz_x(o.yol('tr7_marmara_algilama.json'), out)
    return dict(algilama={k: v['algilama'] for k, v in pen.items()})


# ====================================================================== §8 hüküm (kalıplar yalnız bu biçimlerde)
def _xmin_yaz(x):
    return 'yok' if x is None else str(x)


def xmin_uc(n, f, N):
    """X_min (0,05), X_min^(0,05/3), X_min^(0,05/7)."""
    return tuple(K.x_min(n, f, N, a) if n >= 2 and N else None for a in (0.05, 0.05 / 3, 0.05 / 7))


def k1_neden(k1):
    """§7.2 K1 kalıpları. dal: 'a', 'b', "b'", 'c', 'd'."""
    if k1['dal'] == 'a':
        return 'ölçü sınanamadı (Parkfield verisi yok)'
    if k1['dal'] == 'c':
        return ('ölçü sınanamadı (Tohoku tremoru Parkfield yüzey ağının gürültüsünde görülmedi; '
                f'A90_PK = {anlamli(k1["A90_PK"])} nm/s)')
    if k1['dal'] == 'd':
        return 'ölçü sınanamadı (yöntem)'
    et = []
    if k1.get('ayirt_degil'):
        et.append('geçti, ayırt edici değil')
    if k1['dal'] == "b'":
        et.append('geçti, belirsiz (cisim dalgası açıklaması dışlanamadı)')
    return 'K1 ' + ('; '.join(et) if et else 'GEÇTİ')


def _sonuna(c, ek):
    """Cümlenin son noktasından önce ek (ör. '(K1 yalnız belirsiz geçti)')."""
    return c[:-1] + ' ' + ek + '.' if c.endswith('.') else c + ' ' + ek


def segment_hukmu(g, k1):
    """§8 sırası. g: seg, n, bant, N, f, X_alg, X_mod, lp_ref, n_acik, A50, A90, X (kaba τ₍ₙ₎), tau_alg_min,
    tau_olc_alg_min, n13, bant13, n3, bant3, n_olc, bant_olc, oran_pk. k1: dal, ayirt_degil, mod_gecti.
    Dönüş dict(tur, cumle, olcek=[×1/3 satırı, ×3 satırı], X_min…)."""
    s = g['seg']
    n, N, f = g['n'], g['N'], g['f']
    xm, xm3, xm7 = xmin_uc(n, f, N) if N else (None, None, None)
    p_ust = K.cp_ust(f, N) if N else None
    olcek = [f"Kaba τ ×1/3 alınırsa {g['n13']} birim ≥ 2 kPa (bant: {g['bant13']}).",
             f"Kaba τ ×3 alınırsa {g['n3']} birim ≥ 2 kPa (bant: {g['bant3']}; alt sınır: yalnız ×1 adayları yoklandı)."]
    out = dict(seg=s, X_min=xm, X_min_3=xm3, X_min_7=xm7, p_ust=p_ust, olcek=olcek)
    belirsiz = k1['dal'] == "b'"
    if k1['dal'] not in ('b', "b'"):
        return dict(out, tur='ölçü sınanamadı', cumle=f'{s}: {k1_neden(k1)}.')
    if g['bant'] == 'veri yok':
        return dict(out, tur='veri yok', cumle=f'{s}: veri yok.')
    if N < 5 * n:
        return dict(out, tur='ölçü güvenilmez', cumle=f'{s}: ölçü güvenilmez (negatif kontrol yetersiz).')
    if not K.k2_gecer(f, N):
        return dict(out, tur='ölçü güvenilmez', cumle=f'{s}: ölçü güvenilmez.')
    eksik = []
    if xm is None:
        eksik.append('X_min yok')
    elif g['X_mod'] < xm:
        eksik.append(f"X_mod ≥ X_min(n, f) (X_mod = {g['X_mod']}, X_min = {xm})")
    if not k1.get('mod_gecti'):
        eksik.append('Parkfield modülasyonu geçmedi (modülasyon ölçüsü pozitif kontrolde doğrulanmadı)')
    if k1.get('ayirt_degil'):
        eksik.append('K1 ayırt edici değil')
    if belirsiz:
        eksik.append('K1 yalnız belirsiz geçti')
    if not g['lp_ref']:
        eksik.append('uzun periyot başvuru istasyonu yok')
    if not eksik and g['X_alg'] >= 2:
        to = (f"ölçülen τ ≥ {say(g['tau_olc_alg_min'])} kPa" if g.get('tau_olc_alg_min') is not None
              else 'ölçülen τ ölçülemedi')
        c = (f"{s}: tetiklenmiş tremor VAR. {n} bağımsız tetikleyicinin {g['X_mod']}'unda, yerel deprem ve "
             'teleseismik cisim dalgası maskesi ile darbe/sızıntı/taban ayıklamasından sonra ≥3 istasyonda tutarlı ve '
             'yüzey dalgasıyla eş periyotlu modülasyonlu (p ≤ 0,01; ölçü faz kilidini 20 sn periyodik, kilitsiz '
             'modülasyondan ayıramaz, yapayda yanlış pozitif 0,33–0,56) 2–8 Hz tremor (tetiklenmiş yerel mikrodeprem '
             'kümesi darbe kuralının ayırabildiği kadar dışlandı); negatif kontrolde FAR = '
             f"{f}/{N}; kaba τ ≥ {say(g['tau_alg_min'])} kPa ({to}).")
        c = _sonuna(c, '(segment düzeyi α = 0,05; yedi segment için düzeltilmedi; X_min^(0,05/7) = '
                    f"{_xmin_yaz(xm7)}, {'sağlandı' if isinstance(xm7, int) and g['X_mod'] >= xm7 else 'sağlanmadı'})")
        return dict(out, tur='VAR', cumle=c, ozet_gozlendi=isinstance(xm3, int) and g['X_mod'] >= xm3)
    if g['X_alg'] >= 1:
        if not eksik:
            eksik.append('X_alg = 1')
        c = (f"{s}: aday, doğrulanmadı. {g['X_alg']} tetikleyicide algılama; negatif kontrole göre {n} tetikleyicide "
             f"beklenen yanlış algılama n·f/N = {say(n * f / N)}, P(Bin(n, p_üst) ≥ X_alg) = "
             f"{say(K.binom_ust(n, p_ust, g['X_alg']), 3)}; VAR şartlarından sağlanmayan: {'; '.join(eksik)}.")
        return dict(out, tur='aday', cumle=c)
    on = (f'{s} (yalnız kaba τ ölçeğinde):' if 'veri yok' in (g['bant13'], g['bant_olc']) else f'{s}:')
    a90 = g['A90']
    a90y = f'{anlamli(a90)} nm/s' if isinstance(a90, float) else str(a90)
    dis = (f"; tetikleyici başına ≥ {say(K.p_min(g['n_acik']))} olasılıkla bu genliği aşan tremor üreten bir kaynak "
           '%95 düzeyinde dışlanır.' if g['n_acik'] >= 5 else
           '; dışlama hesaplanmadı (W\'si yarıdan az maskeli birim < 5).')
    oran = say(g['oran_pk']) if g.get('oran_pk') is not None else 'ölçülemedi'
    c = (f"{on} kaba τ ≥ {say(g['X'])} kPa üstündeki {n} bağımsız tetikleyicide ({g['n_acik']}'ının W'si en az yarı "
         f"yarıya maskesiz) tetiklenmiş tremor görülmedi; algılanabilir en küçük genlik A90 = {a90y} (25 km'de, 300 sn "
         f"boyunca 2–8 Hz RMS; A50 = {anlamli(g['A50'])}){dis}"
         + (' Zayıf bant.' if g['bant'] == 'zayıf' else '')
         + f" Ölçek uyarısı: kaba τ ×1/3 alınırsa {g['n13']} birim ≥ 2 kPa ({g['bant13']}); ölçülen τ ile {g['n_olc']} "
           f"birim ≥ 2 kPa ({g['bant_olc']}); Parkfield–Tohoku'da τ_ölç / kaba τ = {oran}.")
    if belirsiz:
        c = _sonuna(c, '(K1 yalnız belirsiz geçti)')
    return dict(out, tur='görülmedi', cumle=c, onek=on.endswith('ölçeğinde):'))


def marmara_ozeti(hs):
    """S1–S3 özeti (§8). hs: {seg: segment_hukmu}. Dönüş cümle ya da None (segment satırları özetsiz)."""
    u = [hs[s] for s in ('S1', 'S2', 'S3')]
    if any(h['tur'] == 'VAR' and h.get('ozet_gozlendi') for h in u):
        return "Marmara özeti (S1–S3): Marmara'da dinamik gerilmeye duyarlı derin kayma bölgesi gözlendi."
    if all(h['tur'] == 'görülmedi' for h in u):
        if any(h.get('onek') for h in u):
            return ('Marmara özeti (S1–S3): bu duyarlılıkla (A90 ve kaba τ değerleriyle; kaba τ ölçeği ×1/3\'te ya da '
                    'ölçülen τ ile veri yok bandında) gözlenmedi.')
        return 'Marmara özeti (S1–S3): bu duyarlılıkla (A90 ve kaba τ değerleriyle) gözlenmedi.'
    return None


# ---------------------------------------------------------------------- D11: elle kurulmuş senaryolar, metin birebir
def _g(**kw):
    g = dict(seg='S2', n=8, bant='tam', N=80, f=0, X_alg=0, X_mod=0, lp_ref=True, n_acik=7, A50=355.0, A90=446.0,
             X=2.75, tau_alg_min=None, tau_olc_alg_min=None, n13=4, bant13='veri yok', n3=8, bant3='tam', n_olc=5,
             bant_olc='zayıf', oran_pk=0.31)
    g.update(kw)
    return g


K1_GECTI = dict(dal='b', ayirt_degil=False, mod_gecti=True)
D11_SENARYO = [
    ('K1 (a)', _g(), dict(dal='a'), 'S2: ölçü sınanamadı (Parkfield verisi yok).'),
    ('K1 (c)', _g(), dict(dal='c', A90_PK=1259.0),
     'S2: ölçü sınanamadı (Tohoku tremoru Parkfield yüzey ağının gürültüsünde görülmedi; A90_PK = 1260 nm/s).'),
    ('K1 (d)', _g(), dict(dal='d'), 'S2: ölçü sınanamadı (yöntem).'),
    ('veri yok', _g(n=4, bant='veri yok', N=40), K1_GECTI, 'S2: veri yok.'),
    ('N < 5n', _g(N=39), K1_GECTI, 'S2: ölçü güvenilmez (negatif kontrol yetersiz).'),
    ('K2 kaldı', _g(f=5), K1_GECTI, 'S2: ölçü güvenilmez.'),
    ('VAR', _g(f=1, X_alg=3, X_mod=3, tau_alg_min=3.97, tau_olc_alg_min=1.2), K1_GECTI,
     "S2: tetiklenmiş tremor VAR. 8 bağımsız tetikleyicinin 3'unda, yerel deprem ve teleseismik cisim dalgası maskesi ile "
     'darbe/sızıntı/taban ayıklamasından sonra ≥3 istasyonda tutarlı ve yüzey dalgasıyla eş periyotlu modülasyonlu '
     '(p ≤ 0,01; ölçü faz kilidini 20 sn periyodik, kilitsiz modülasyondan ayıramaz, yapayda yanlış pozitif 0,33–0,56) '
     '2–8 Hz tremor (tetiklenmiş yerel mikrodeprem kümesi darbe kuralının ayırabildiği kadar dışlandı); negatif '
     'kontrolde FAR = 1/80; kaba τ ≥ 3,97 kPa (ölçülen τ ≥ 1,20 kPa) (segment düzeyi α = 0,05; yedi segment için '
     'düzeltilmedi; X_min^(0,05/7) = 4, sağlanmadı).'),
    ('VAR, τ_ölç yok', _g(f=0, X_alg=2, X_mod=2, tau_alg_min=9.39), K1_GECTI,
     "S2: tetiklenmiş tremor VAR. 8 bağımsız tetikleyicinin 2'unda, yerel deprem ve teleseismik cisim dalgası maskesi ile "
     'darbe/sızıntı/taban ayıklamasından sonra ≥3 istasyonda tutarlı ve yüzey dalgasıyla eş periyotlu modülasyonlu '
     '(p ≤ 0,01; ölçü faz kilidini 20 sn periyodik, kilitsiz modülasyondan ayıramaz, yapayda yanlış pozitif 0,33–0,56) '
     '2–8 Hz tremor (tetiklenmiş yerel mikrodeprem kümesi darbe kuralının ayırabildiği kadar dışlandı); negatif '
     'kontrolde FAR = 0/80; kaba τ ≥ 9,39 kPa (ölçülen τ ölçülemedi) (segment düzeyi α = 0,05; yedi segment için '
     'düzeltilmedi; X_min^(0,05/7) = 3, sağlanmadı).'),
    ('aday, X_alg = 1', _g(f=2, X_alg=1, X_mod=1), K1_GECTI,
     'S2: aday, doğrulanmadı. 1 tetikleyicide algılama; negatif kontrole göre 8 tetikleyicide beklenen yanlış algılama '
     'n·f/N = 0,20, P(Bin(n, p_üst) ≥ X_alg) = 0,471; VAR şartlarından sağlanmayan: X_mod ≥ X_min(n, f) '
     '(X_mod = 1, X_min = 3).'),
    ('aday, modülasyon ve K1', _g(f=0, X_alg=2, X_mod=2), dict(dal="b'", ayirt_degil=True, mod_gecti=False),
     'S2: aday, doğrulanmadı. 2 tetikleyicide algılama; negatif kontrole göre 8 tetikleyicide beklenen yanlış algılama '
     'n·f/N = 0,00, P(Bin(n, p_üst) ≥ X_alg) = 0,033; VAR şartlarından sağlanmayan: Parkfield modülasyonu geçmedi '
     '(modülasyon ölçüsü pozitif kontrolde doğrulanmadı); K1 ayırt edici değil; K1 yalnız belirsiz geçti.'),
    ('aday, LP yok', _g(f=0, X_alg=2, X_mod=0, lp_ref=False), K1_GECTI,
     'S2: aday, doğrulanmadı. 2 tetikleyicide algılama; negatif kontrole göre 8 tetikleyicide beklenen yanlış algılama '
     'n·f/N = 0,00, P(Bin(n, p_üst) ≥ X_alg) = 0,033; VAR şartlarından sağlanmayan: X_mod ≥ X_min(n, f) '
     '(X_mod = 0, X_min = 2); uzun periyot başvuru istasyonu yok.'),
    ('görülmedi, ön ek', _g(), K1_GECTI,
     "S2 (yalnız kaba τ ölçeğinde): kaba τ ≥ 2,75 kPa üstündeki 8 bağımsız tetikleyicide (7'ının W'si en az yarı yarıya "
     "maskesiz) tetiklenmiş tremor görülmedi; algılanabilir en küçük genlik A90 = 446 nm/s (25 km'de, 300 sn boyunca "
     '2–8 Hz RMS; A50 = 355); tetikleyici başına ≥ 0,39 olasılıkla bu genliği aşan tremor üreten bir kaynak %95 '
     'düzeyinde dışlanır. Ölçek uyarısı: kaba τ ×1/3 alınırsa 4 birim ≥ 2 kPa (veri yok); ölçülen τ ile 5 birim ≥ 2 kPa '
     "(zayıf); Parkfield–Tohoku'da τ_ölç / kaba τ = 0,31."),
    ('görülmedi, zayıf, belirsiz, n_açık < 5', _g(n=6, bant='zayıf', N=60, n_acik=4, A90='belirsiz', A50='belirsiz',
                                                n13=6, bant13='zayıf', n_olc=6, bant_olc='zayıf', oran_pk=None),
     dict(dal="b'", ayirt_degil=False, mod_gecti=True),
     "S2: kaba τ ≥ 2,75 kPa üstündeki 6 bağımsız tetikleyicide (4'ının W'si en az yarı yarıya maskesiz) tetiklenmiş "
     "tremor görülmedi; algılanabilir en küçük genlik A90 = belirsiz (25 km'de, 300 sn boyunca 2–8 Hz RMS; A50 = "
     "belirsiz); dışlama hesaplanmadı (W'si yarıdan az maskeli birim < 5). Zayıf bant. Ölçek uyarısı: kaba τ ×1/3 "
     "alınırsa 6 birim ≥ 2 kPa (zayıf); ölçülen τ ile 6 birim ≥ 2 kPa (zayıf); Parkfield–Tohoku'da τ_ölç / kaba τ = "
     'ölçülemedi (K1 yalnız belirsiz geçti).'),
]
D11_OLCEK = ('Kaba τ ×1/3 alınırsa 4 birim ≥ 2 kPa (bant: veri yok).',
             'Kaba τ ×3 alınırsa 8 birim ≥ 2 kPa (bant: tam; alt sınır: yalnız ×1 adayları yoklandı).')
D11_K1 = [(dict(dal='b'), 'K1 GEÇTİ'), (dict(dal="b'"), 'K1 geçti, belirsiz (cisim dalgası açıklaması dışlanamadı)'),
          (dict(dal='b', ayirt_degil=True), 'K1 geçti, ayırt edici değil'),
          (dict(dal="b'", ayirt_degil=True),
           'K1 geçti, ayırt edici değil; geçti, belirsiz (cisim dalgası açıklaması dışlanamadı)')]


def kd_D11():
    """§7.1 D11: bant ve hüküm cümlesi üretici, elle kurulmuş senaryolar (§8'in her dalı, K1 (a)–(d), ön ek), birebir."""
    sonuc = []
    for ad, g, k1, bek in D11_SENARYO:
        h = segment_hukmu(g, k1)
        sonuc.append(dict(senaryo=ad, dogru=h['cumle'] == bek, uretilen=h['cumle']))
    h = segment_hukmu(_g(), K1_GECTI)
    sonuc.append(dict(senaryo='×1/3 ve ×3 satırları', dogru=tuple(h['olcek']) == D11_OLCEK, uretilen=h['olcek']))
    for k1, bek in D11_K1:
        e = k1_neden(k1)
        sonuc.append(dict(senaryo=f'K1 etiketi {k1}', dogru=e == bek, uretilen=e))
    gor = segment_hukmu(_g(bant13='tam', bant_olc='tam'), K1_GECTI)
    hs = {'S1': gor, 'S2': gor, 'S3': gor}
    oz = [(hs, 'Marmara özeti (S1–S3): bu duyarlılıkla (A90 ve kaba τ değerleriyle) gözlenmedi.'),
          ({'S1': gor, 'S2': segment_hukmu(_g(), K1_GECTI), 'S3': gor},
           "Marmara özeti (S1–S3): bu duyarlılıkla (A90 ve kaba τ değerleriyle; kaba τ ölçeği ×1/3'te ya da ölçülen τ "
           'ile veri yok bandında) gözlenmedi.'),
          ({'S1': gor, 'S2': segment_hukmu(_g(f=0, X_alg=3, X_mod=3, tau_alg_min=4.0), K1_GECTI), 'S3': gor},
           "Marmara özeti (S1–S3): Marmara'da dinamik gerilmeye duyarlı derin kayma bölgesi gözlendi."),
          ({'S1': gor, 'S2': segment_hukmu(_g(f=0, X_alg=2, X_mod=2, tau_alg_min=4.0), K1_GECTI), 'S3': gor}, None)]
    for i, (h_, bek) in enumerate(oz):
        e = marmara_ozeti(h_)
        sonuc.append(dict(senaryo=f'özet {i + 1}', dogru=e == bek, uretilen=e))
    for n, bek in ((4, 'veri yok'), (5, 'zayıf'), (7, 'zayıf'), (8, 'tam')):
        sonuc.append(dict(senaryo=f'bant n={n}', dogru=K.bant(n) == bek, uretilen=K.bant(n)))
    return dict(hepsi=all(x['dogru'] for x in sonuc), senaryolar=sonuc)


# ====================================================================== hüküm aşaması ve çıktı tabloları (§8, §9)
def _birim_pencereleri(D, birim, s):
    return [p for p in D['pen'].values() if p['tur'] == 'tet' and p['bolge'] == 'Marmara' and p['birim'] == birim
            and s in p['seg']]


def seg_veri(D, k0, neg, alg, s, k1, bas=None):
    """Segment tanımları (§8): n, bant, N, f, X_alg, X_mod, n_açık, n_ölç, … (bas: S5/S6 bağımsız satırı)."""
    x1, x13, x3 = (k0[c][s] if bas is None else k0[c][s]['bagimsiz'] for c in ('x1', 'x1/3', 'x3'))
    ng = neg['segment'][s] if bas is None else neg['segment'][s]['bagimsiz']
    ana = x1['birimler']
    pe = alg['pencere_segment']
    X_alg = X_mod = n_acik = n_olc = 0
    lp = False
    tau_alg, tauo_alg, birim_sat = [], [], {}
    for b in ana:
        es = [pe[f"{p['id']}|{s}"] for p in _birim_pencereleri(D, b, s) if f"{p['id']}|{s}" in pe]
        tum = len(_birim_pencereleri(D, b, s))
        det = any(e['algilama'] for e in es)
        mod = det and any(m is not None and m['p'] <= K.MOD_ESIK for e in es if e['algilama'] for m in e['mod'])
        acik = len(es) == tum and all(e['W_payi'] is not None and e['W_payi'] <= 0.5 for e in es)
        to = [e['tau_olc']['tau'] for e in es if e.get('tau_olc')]
        tob = max(to) if to else None
        X_alg += det
        X_mod += mod
        n_acik += acik
        n_olc += tob is not None and tob >= K.TAU_ESIK
        if det:
            lp = lp or any(e.get('lp_referans') for e in es if e['algilama'])
            tau_alg.append(x1['tau'][b])
            if tob is not None:
                tauo_alg.append(tob)
        birim_sat[b] = dict(algilama=det, modulasyon=mod, acik=acik, tau_olc=tob)
    g = dict(seg=s, n=x1['n'], bant=x1['bant'], N=ng['N'], f=ng['f'], X_alg=X_alg, X_mod=X_mod, lp_ref=lp,
             n_acik=n_acik, A50=ng['mda']['A50'], A90=ng['mda']['A90'], n_deneme=ng['mda']['n_deneme'],
             X=x1['tau_n'], tau_alg_min=min(tau_alg) if tau_alg else None,
             tau_olc_alg_min=min(tauo_alg) if tauo_alg else None, n13=x13['n'], bant13=x13['bant'], n3=x3['n'],
             bant3=x3['bant'], n_olc=n_olc, bant_olc=K.bant(n_olc), oran_pk=k1.get('tau_olc_bolu_kaba'))
    return g, birim_sat


def asama_hukum(o, D, d, kip):
    yol = o.yol('tr7_k1_2.json') if os.path.exists(o.yol('tr7_k1_2.json')) else o.yol('tr7_k1.json')
    with open(yol, encoding='utf-8') as f:
        k1 = json.load(f)
    kd = kd_son(o)
    k1d = dict(dal=k1['dal'], ayirt_degil=k1.get('ayirt_degil'), mod_gecti=k1.get('mod_gecti'),
               A90_PK=k1.get('A90_PK'), tau_olc_bolu_kaba=k1.get('tau_olc_bolu_kaba'))
    out = dict(aciklama='TR-7 tek koşu sonucu (ön kayıt sürüm 3, §8–§9).', zaman=simdi(), kod_sha256=kod_sha(),
               kd=dict(gecti=kd['gecti'] if kd else None,
                       satirlar=[{k: v for k, v in x.items() if k != 'deger'} for x in kd['satirlar']] if kd else None),
               k1=dict(etiket=k1_neden(k1d), **{k: k1.get(k) for k in (
                   'dal', 'ayirt_degil', 'N_PK', 'f_PK', 'FAR_PK', 'A50_PK', 'A90_PK', 'mda_deneme', 'A_PK',
                   'mod_gecti', 'modulasyon', 'lp_referans', 'tau_olc', 'tau_olc_bolu_kaba', 'k1_kumeleri',
                   'kume_ayiklama_oncesi', 'PKD_asimlari', 'cekirdek_fazlari')},
                       modulasyon_satiri='Parkfield modülasyonu geçti' if k1.get('mod_gecti') else
                       'Parkfield modülasyonu geçmedi'),
               segment={}, ozet=None, bilgi=[], birim_segment=[])
    if not kd or not kd['gecti']:
        out['hukum'] = 'geçersiz (kod): KD geçmedi'
    if k1['dal'] not in ('b', "b'"):
        k0 = k0_tam(D, {}, onsayim=True)
        for s in MARMARA_SEG:
            g = dict(seg=s, n13=k0['x1/3'][s]['n'], bant13=k0['x1/3'][s]['bant'], n3=k0['x3'][s]['n'],
                     bant3=k0['x3'][s]['bant'])
            h = segment_hukmu(dict(g, n=0, N=0, f=0, bant='veri yok'), k1d)
            h['olcek'] = [x[:-1] + ' (önsayım; Marmara verisi indirilmedi).' for x in h['olcek']]
            out['segment'][s] = dict(hukum=h, veri=g)
    else:
        k0 = k0_oku(o)
        neg = json_oku(o.yol('tr7_marmara_negatif.json'))
        alg = json_oku(o.yol('tr7_marmara_algilama.json'))
        hs = {}
        for s in MARMARA_SEG:
            if s in BAGIMSIZ_SEG:
                g, bs = seg_veri(D, k0, neg, alg, s, k1d, BAGIMSIZ_BAS)
                gt, bst = seg_veri(D, k0, neg, alg, s, k1d)
                h = segment_hukmu(g, k1d)
                ht = segment_hukmu(gt, k1d)
                ht['cumle'] = 'Yöntem karşılaştırması, bağımsız değil (2005–2008 birimleri dahil): ' + ht['cumle']
                out['segment'][s] = dict(hukum=h, veri=g, birim=bs, yontem_karsilastirmasi=dict(hukum=ht, veri=gt))
            else:
                g, bs = seg_veri(D, k0, neg, alg, s, k1d)
                h = segment_hukmu(g, k1d)
                out['segment'][s] = dict(hukum=h, veri=g, birim=bs)
            hs[s] = h
            ng = neg['segment'][s]
            a90 = g['A90']
            out['bilgi'].append(f"{s}: A90 / A_PK = " + (say(a90 / k1['A_PK']) if isinstance(a90, float)
                                                         and k1.get('A_PK') else 'tanımsız') + '.')
            for b, v in ng.get('kahramanmaras', {}).items():
                es = [alg['pencere_segment'].get(f'tet|{b}|{s}')]
                e = es[0] or {}
                ps = [m['p'] for m in e.get('mod', []) if m]
                out['bilgi'].append(f"{s} Kahramanmaraş {b} (bilgi; hükmü değiştirmez): algılama "
                                    f"{'E' if e.get('algilama') else 'H'}; modülasyon p = "
                                    f"{say(min(ps), 3) if ps else '—'}; negatif f/N = {v['f']}/{v['N']}; kaba τ = "
                                    f"{say(D['olay'][b]['tau'].get(s))} kPa.")
        out['ozet'] = marmara_ozeti(hs)
        out['bilgi'].append('S4–S7 ikinci satırlardır, Marmara özetine girmez.')
        out['birim_segment'] = birim_segment_tablosu(o, D, k0, alg)
        out['k0_tam'] = {c: {s: {k: v for k, v in k0[c][s].items() if k != 'tau'} for s in MARMARA_SEG}
                         for c in ('x1', 'x1/3', 'x3')}
        out['k2_mda'] = neg['segment']
    out['manifest_ozeti'] = manifest_ozeti(o)
    out['negatif_gun_turu'] = _say_dagilim([(r['bolge'], r['gun_turu'], r['utc_farki_saat']) for r in D['neg']])
    json_yaz_x(o.yol('tr7_sonuc.json'), out)
    with open(o.yol('tr7_sonuc.md'), 'x', encoding='utf-8') as f:
        f.write(sonuc_md(out))
    return dict(hukum={s: v['hukum']['tur'] for s, v in out['segment'].items()}, ozet=out['ozet'])


def _say_dagilim(xs):
    d = {}
    for x in xs:
        k = ' | '.join(str(v) for v in x)
        d[k] = d.get(k, 0) + 1
    return d


def birim_segment_tablosu(o, D, k0, alg):
    """§9.1 birim × segment satırları."""
    sat = _algilama_satirlari(o, 'Marmara-algılama')
    negs = list(_algilama_satirlari(o, 'Marmara-negatif').values())
    out = []
    for (pid, s), r in sorted(sat.items(), key=lambda kv: (D['pen'][kv[0][0]]['t0'], kv[0][1])):
        p = D['pen'][pid]
        e = alg['pencere_segment'].get(f'{pid}|{s}', {})
        ol = D['olay'][p['tetikleyici']]
        tau = ol['tau'].get(s)
        nf = [x for x in negs if x['birim'] == p['birim'] and x['segment'] == s and x['tetikleyici'] == p['tetikleyici']]
        out.append(dict(birim=p['birim'], olay=p['tetikleyici'], T0=ol['t0'], M=ol['M'], segment=s, kaba_tau=tau,
                        kaba_tau_x13=round(tau / 3, 2) if tau is not None else None, tau_olc=e.get('tau_olc'),
                        gecen=r['n_gecen'], kullanilan=len(r['kullanilan']), paylar=r.get('paylar'),
                        kume_sayisi=r.get('kume_sayisi'), ayiklanan=r.get('ayiklanan'), algilama=r['algilama'],
                        modulasyon_p=[m['p'] if m else None for m in e.get('mod', [])],
                        en_uzun_kume_s=r.get('en_uzun_kume_s'), a_nm_s=e.get('a'),
                        negatif_f=f"{sum(1 for x in nf if x['algilama'])}/{sum(1 for x in nf if x['durum'] == 'tarandi')}",
                        kumeler=[dict(Ip=k['Ip'], darbe_pay=k['darbe_pay'], cp_medyan=k['cp_medyan_medyan'], sag=k['sag'])
                                 for k in r.get('kumeler', [])]))
    return out


def manifest_ozeti(o):
    out = {}
    for a in INDIRME_ASAMALARI:
        rs = [r for r in jsonl_oku(o.yol(f'tr7_indirme_{a}.jsonl')) if r.get('tur') == 'istek']
        out[a] = dict(istek=len(rs), http=_say_dagilim([(r.get('http'),) for r in rs]),
                      bayt=sum(r.get('bayt') or 0 for r in rs), durum=_say_dagilim([(r['durum'],) for r in rs]))
    out['dusen'] = _say_dagilim([(r.get('dusme'),) for r in jsonl_oku(o.yol('tr7_zarf_sha256.jsonl'))
                                 if r.get('dusme')])
    return out


def sonuc_md(out):
    L = ['# TR-7 sonuç (tek koşu)', '', f"Kod sha256: {json.dumps(out['kod_sha256'], ensure_ascii=False)}", '',
         '## K1 (Parkfield–Tohoku)', '', f"- {out['k1']['etiket']}", f"- {out['k1']['modulasyon_satiri']}",
         f"- N_PK = {out['k1']['N_PK']}, f_PK = {out['k1']['f_PK']}, FAR_PK = {say(out['k1']['FAR_PK'])}; "
         f"A50_PK = {anlamli(out['k1']['A50_PK'])}, A90_PK = {anlamli(out['k1']['A90_PK'])} nm/s "
         f"({out['k1']['mda_deneme']} deneme); A_PK = {anlamli(out['k1']['A_PK'])} nm/s; τ_ölç / kaba τ = "
         f"{say(out['k1']['tau_olc_bolu_kaba'])}", '', '## Segment hükümleri', '']
    for s, v in out['segment'].items():
        L.append(f"- {v['hukum']['cumle']}")
        for x in v['hukum']['olcek']:
            L.append(f'  - {x}')
        if 'yontem_karsilastirmasi' in v:
            L.append(f"  - {v['yontem_karsilastirmasi']['hukum']['cumle']}")
    if out.get('ozet'):
        L += ['', out['ozet']]
    L += ['', '## Segment tablosu (§9.2)', '',
          '| Segment | n | n_açık | p_min | bant | n_ölç | bant_ölç | N | f | X_alg | X_mod | X_min | X_min^(0,05/3) | '
          'X_min^(0,05/7) | A50 | A90 (deneme) | kaba τ₍ₙ₎ |', '|' + '---|' * 17]
    for s, v in out['segment'].items():
        g, h = v['veri'], v['hukum']
        if 'N' not in g:
            continue
        L.append(f"| {s} | {g['n']} | {g['n_acik']} | {say(K.p_min(g['n_acik']))} | {g['bant']} | {g['n_olc']} | "
                 f"{g['bant_olc']} | {g['N']} | {g['f']} | {g['X_alg']} | {g['X_mod']} | {_xmin_yaz(h['X_min'])} | "
                 f"{_xmin_yaz(h['X_min_3'])} | {_xmin_yaz(h['X_min_7'])} | {anlamli(g['A50'])} | {anlamli(g['A90'])} "
                 f"({g['n_deneme']}) | {say(g['X'])} |")
    L += ['', '## Bilgi satırları', ''] + [f'- {x}' for x in out['bilgi']]
    L += ['', '## KD', '', f"- geçti: {out['kd']['gecti']}", '', '## Manifest özeti', '',
          '```', json.dumps(out['manifest_ozeti'], ensure_ascii=False, indent=1), '```', '']
    return '\n'.join(L)


# ====================================================================== aşama mekanizması ve komut satırı
ASAMA_FN = {'manifest': None, 'K1-indirme': asama_K1_indirme, 'K1-negatif': asama_K1_negatif,
            'K1-algılama': asama_K1_algilama, 'Marmara-indirme': asama_Marmara_indirme,
            'Marmara-negatif': asama_Marmara_negatif, 'Marmara-algılama': asama_Marmara_algilama,
            'hüküm': asama_hukum}


def asama_manifest_yaz(o, D, d, kip):
    man = asama_manifest(o, D)
    json_yaz_x(o.yol('tr7_manifest.json'), man)
    return dict(stationxml=len(man['stationxml']), katalog=len(man['katalog']),
                planli=sum(len(v) for v in man['plan'].values()))


ASAMA_FN['manifest'] = asama_manifest_yaz


def kd_denetle(o, tam=True):
    kd = kd_son(o)
    if not kd:
        raise KosuDur('KD sonucu yok (önce `kd`)')
    if not kd['gecti']:
        raise KosuDur('KD kaldı: kod gerçek veri görülmeden düzeltilir (§7.1)')
    if tam and kd.get('olcek') != 1.0:
        raise KosuDur('KD tam ölçekte koşulmamış')
    if kd['kod_sha256'] != kod_sha():
        raise KosuDur('KD bu kodla koşulmadı (kod değişti): KD yeniden koşulur')
    return kd


def kuru_prova(o):
    """Veriye bağlı olmayan kurulum: yapay 1 Hz zarflarla algılama zinciri, zarf deposu yazılabilirliği (depo dışı),
    obspy/taup. Gerçek veri yok."""
    t0 = time.time()
    if not I.depo_disi(o.zarf, o.depo):
        raise KosuDur(f'zarf deposu depo içinde: {o.zarf} (§6.1)')
    os.makedirs(o.zarf, exist_ok=True)
    y = o.zyol('.kuru_prova')
    with open(y, 'w') as f:
        f.write('x')
    os.remove(y)
    rng = np.random.default_rng(20261112 + 77)
    n, R, W = 6800, (600, 4200), (4200, 6100)
    m = np.zeros(n, bool)

    def ist(ek):
        return [K.istasyon(np.exp(rng.normal(0, 0.15, n)) + ek, np.exp(rng.normal(0, 0.15, n)), R, W, m, f'Y{i}')
                for i in range(3)]
    g = K.pencere_algila(ist(0.0), m, W)['algilama']
    ek = np.zeros(n)
    ek[5000:5300] = 3.0 * np.maximum(0, np.sin(2 * np.pi * np.arange(300) / 20.0))
    t = K.pencere_algila(ist(ek), m, W)['algilama']
    K.taup_model()
    if g or not t:
        raise KosuDur(f'kuru prova beklenmedik sonuç (gürültü {g}, tremor {t})')
    return dict(sure_s=round(time.time() - t0, 2), gurultu_algilama=g, tremor_algilama=t)


def baslat(o, asama, surdur=False, uygulama_hatasi=False):
    d = durum_oku(o)
    kd_denetle(o)
    dunya_yukle(o)
    mevcut = d['asamalar'].get(asama)
    if mevcut and mevcut.get('durum') in ('başladı', 'sürdürülüyor'):
        raise KosuDur(f'"{asama}" zaten başlatıldı: durum dosyasını commit + push edin, sonra `kos {asama}`')
    if uygulama_hatasi and d['asamalar'].get('hüküm'):
        raise KosuDur('hüküm yazıldıktan sonra uygulama hatası yolu kullanılamaz')
    kip = onkosul(o, asama, d, surdur=surdur, uygulama_hatasi=uygulama_hatasi)
    prova = kuru_prova(o)
    yeni = dict(durum='sürdürülüyor' if kip == 'surdur' else 'başladı', kip=kip, baslatma=simdi(),
                kod_sha256=kod_sha(), kuru_prova=prova)
    if mevcut:
        yeni['onceki'] = {k: v for k, v in mevcut.items() if k != 'onceki'}
    if kip == 'uygulama_hatasi':
        d['uygulama_hatasi_yolu'] = dict(zaman=simdi(), baslik='K1 sonrası düzeltme')
    d['asamalar'][asama] = yeni
    json_yaz(o.yol(DURUM_AD), d)
    bekci_yaz(o, dict(asama=asama, durum=yeni['durum'], zaman=simdi(), kod_sha256=yeni['kod_sha256']))
    rel = os.path.relpath(o.yol(DURUM_AD), o.depo)
    o.log(f'"{asama}" başlatıldı ({kip}). Şimdi: git -C {o.depo} add {rel} && git -C {o.depo} commit -m '
          f'"TR-7 aşama başlıyor: {asama}" && git -C {o.depo} push; sonra `kos {asama}`.')
    return yeni


def kos(o, asama):
    d = durum_oku(o)
    a = d['asamalar'].get(asama)
    if not a or a.get('durum') not in ('başladı', 'sürdürülüyor'):
        raise KosuDur(f'"{asama}" başlatılmamış (önce `baslat {asama}`, commit + push)')
    if o.git_dogrula:
        a['git'] = git_dogrula(o, asama)
    kd_denetle(o)
    D = dunya_yukle(o)
    if a.get('kod_sha256') != kod_sha():
        raise KosuDur('kod `baslat`tan sonra değişti: yeniden `baslat` (koşu öncesi düzeltme kaydıyla)')
    try:
        sonuc = ASAMA_FN[asama](o, D, d, a.get('kip'))
    except (KosuDur, I.BicimHata, I.SinirIhlali, K.CekirdekHata) as e:
        a.update(durum='durdu', son_hata=f'{type(e).__name__}: {e}', durma_zamani=simdi())
        json_yaz(o.yol(DURUM_AD), d)
        raise KosuDur(f'{asama} durdu: {e}. Durma nedenini `durdu {asama} --neden "..."` ile kayda geçirin, '
                      f'commit + push, sonra `baslat {asama} --surdur`.') from e
    a.update(durum='tamamlandı', bitis=simdi(), sonuc=sonuc)
    if isinstance(sonuc, dict):
        for k in ('k1_dal', 'ayirt_degil', 'mod_gecti'):
            if k in sonuc:
                a[k] = sonuc[k]
    json_yaz(o.yol(DURUM_AD), d)
    bekci_yaz(o, dict(asama=asama, durum='tamamlandı', zaman=simdi()))
    o.log(f'"{asama}" tamamlandı. Çıktıları ve {DURUM_AD}\'yi commit + push edin.')
    return sonuc


def durdu(o, asama, neden):
    d = durum_oku(o)
    a = d['asamalar'].get(asama)
    if not a:
        raise KosuDur(f'"{asama}" hiç başlamadı')
    if a.get('durum') == 'tamamlandı':
        raise KosuDur(f'"{asama}" tamamlanmış')
    a['durum'] = 'durdu'
    d['durmalar'].append(dict(asama=asama, neden=neden, zaman=simdi()))
    json_yaz(o.yol(DURUM_AD), d)
    o.log(f'durma nedeni kayda geçti. Commit + push, sonra `baslat {asama} --surdur`.')


def main(argv=None):
    ap = argparse.ArgumentParser(description='TR-7 tek koşu kodu (ön kayıt sürüm 3).')
    sp = ap.add_subparsers(dest='komut', required=True)
    k = sp.add_parser('kd')
    k.add_argument('--paralel', type=int, default=4)
    k.add_argument('--olcek', type=float, default=1.0)
    b = sp.add_parser('baslat')
    b.add_argument('asama', choices=ASAMALAR)
    b.add_argument('--surdur', action='store_true')
    b.add_argument('--uygulama-hatasi-yolu', action='store_true')
    c = sp.add_parser('kos')
    c.add_argument('asama', choices=ASAMALAR)
    e = sp.add_parser('durdu')
    e.add_argument('asama', choices=ASAMALAR)
    e.add_argument('--neden', required=True)
    sp.add_parser('k0')
    a = ap.parse_args(argv)
    o = Ortam()
    try:
        if a.komut == 'kd':
            r = kd_kos(o, paralel=a.paralel, olcek=a.olcek)
            return 0 if r['gecti'] else 3
        if a.komut == 'k0':
            D = dunya_yukle(o)
            print(json.dumps({c_: {s: (v['n'], v['bant']) for s, v in k0_tam(D, {}, onsayim=True)[c_].items()}
                              for c_ in ('x1', 'x1/3', 'x3')}, ensure_ascii=False, indent=1))
            return 0
        if a.komut == 'baslat':
            baslat(o, a.asama, surdur=a.surdur, uygulama_hatasi=a.uygulama_hatasi_yolu)
        elif a.komut == 'kos':
            kos(o, a.asama)
        elif a.komut == 'durdu':
            durdu(o, a.asama, a.neden)
        return 0
    except GitDogrulanamadi as e:
        print(f'DUR (git): {e}', file=sys.stderr)
        return 5
    except KosuDur as e:
        print(f'DUR: {e}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
