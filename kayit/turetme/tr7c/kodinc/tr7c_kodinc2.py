#!/usr/bin/env python3
"""TR-7c KOD İNCELEMESİ-2: yalnız b0f70642… → c86d8b9b… farkı (kuru prova düğmesi, taban URL'leri, aşama protokolü,
durma kaydı) için incelemecinin sınamaları ve mutasyonları.

YALNIZ YAPAY VERİ; HİÇBİR SOKET AÇILMAZ. Süreç başında denetim kancası: her soket olayı, `/mnt/project-files` altında
her açma, gerçek çıktı dizinine (`tr7c/kosu/`) her yazma ve dizin kurma, her alt süreç reddedilir ve sayılır. Prova
düğmesinin kancası (`_prova_kancasi`) bu yüzden doğrudan çağrılarak sınanır; sahte sunucu kurulmaz (kodlayıcının
`tr7c_prova.py`'si bunu yapar). Aşama gövdesi (`_asama_govde`) sınamada saplanır: indirme, ağ ve hesap çağrılmaz.
Kapının açık hâli yalnız ön kaydın geçici bir kopyasıyla (`onkayit=`) ya da `kosu_dondurulmus_mu` saplanarak kurulur;
açık kapıyla hiçbir gerçek yol çağrılmaz.

Kullanım (depo kökünden):
  python3 -I -B kayit/turetme/tr7c/kodinc/tr7c_kodinc2.py <çıktı.json> [--mutasyonsuz] [--parca i/n]
  --parca i/n: yalnız (sıra % n == i) mutasyonları koşar; sonuç ara jsonl'e (<çıktı>.mut.jsonl) her mutasyondan sonra
  yazılır ve sürdürülür. Birleştirme: aynı komut --birlestir ile.
"""
import datetime as _dt
import importlib.util
import json
import os
import shutil
import sys
import time
import types

sys.dont_write_bytecode = True
os.environ.setdefault('OMP_NUM_THREADS', '1')
BURA = os.path.dirname(os.path.abspath(__file__))
TR7C = os.path.abspath(os.path.join(BURA, '..'))
DEPO = os.path.abspath(os.path.join(TR7C, '..', '..', '..'))
KOSU_YOL = os.path.join(TR7C, 'tr7c_kosu.py')
ONKAYIT = os.path.join(DEPO, 'kayit', 'onkayit', 'TR-7c_tetiklenmis-tremor_ONKAYIT.md')
YASAK = '/mnt/project-files'
CIKTI_GERCEK = os.path.join(TR7C, 'kosu')
GECICI = '/tmp/claude-0/-home-user/635decb6-3930-5a4d-9c31-b6f30d64fb94/scratchpad/tr7c_kodinc/k2'

ENGEL = []


def _p(a):
    try:
        return None if isinstance(a, int) else os.path.abspath(os.fsdecode(a))
    except Exception:   # noqa: BLE001
        return None


def _kanca(olay, args):
    if olay.startswith('socket.'):
        ENGEL.append((olay, repr(args)[:120]))
        raise PermissionError(f'KOD İNCELEMESİ-2: ağ yasak ({olay})')
    if olay in ('subprocess.Popen', 'os.system', 'os.posix_spawn', 'os.exec', 'os.fork'):
        ENGEL.append((olay, repr(args)[:120]))
        raise PermissionError(f'KOD İNCELEMESİ-2: alt süreç yasak ({olay})')
    if olay == 'open' and args:
        p = _p(args[0])
        if p and (p == YASAK or p.startswith(YASAK + os.sep)):
            ENGEL.append((olay, p))
            raise PermissionError(f'KOD İNCELEMESİ-2: gerçek veri yolu yasak: {p}')
        if p and (p == CIKTI_GERCEK or p.startswith(CIKTI_GERCEK + os.sep)):
            m = args[1] if len(args) > 1 else 'r'
            if not isinstance(m, str) or any(c in m for c in 'wax+'):
                ENGEL.append((olay, p))
                raise PermissionError(f'KOD İNCELEMESİ-2: gerçek çıktı dizinine yazma yasak: {p}')
    if olay in ('os.mkdir', 'os.makedirs', 'os.rename', 'os.replace', 'os.remove', 'os.symlink') and args:
        p = _p(args[1] if olay == 'os.symlink' else args[0])     # bağın kendisi (hedefe dokunulmaz)
        if p and (p.startswith(CIKTI_GERCEK) or p.startswith(YASAK)):
            ENGEL.append((olay, p))
            raise PermissionError(f'KOD İNCELEMESİ-2: yasak dizin işlemi: {p}')


sys.addaudithook(_kanca)
sys.path.insert(0, TR7C)
import tr7c_kosu as T0  # noqa: E402
import tr7_indir as I  # noqa: E402


def modul_yukle(metin, ad):
    spec = importlib.util.spec_from_loader(ad, loader=None)
    m = importlib.util.module_from_spec(spec)
    m.__file__ = KOSU_YOL           # sha256_dosya(__file__) diskteki (değişmemiş) dosyanın değeridir
    sys.modules[ad] = m
    try:
        exec(compile(metin, KOSU_YOL, 'exec'), m.__dict__)
    finally:
        sys.modules.pop(ad, None)
    return m


class Kayit:
    def __init__(self):
        self.s = []

    def sina(self, grup, ad, kosul, ayrinti=None):
        self.s.append(dict(grup=grup, ad=ad, gecti=bool(kosul), ayrinti=None if kosul else ayrinti))


def reddedilir(fn, tur):
    try:
        fn()
    except tur:
        return True
    except BaseException:   # noqa: BLE001
        return False
    return False


def dizin(*p):
    y = os.path.join(GECICI, *p)
    if os.path.lexists(y):
        if os.path.islink(y) or os.path.isfile(y):
            os.unlink(y)
        else:
            shutil.rmtree(y)
    os.makedirs(y)
    return y


def prova(KM, ad, port=9, **ek):
    d = dizin(ad)
    os.makedirs(os.path.join(d, 'zarf'))
    a = dict(dizin=os.path.join(d, 'cikti'), zarf=os.path.join(d, 'zarf'),
             servis={k: f'http://127.0.0.1:{port}/{k}' for k in I.SERVIS},
             katalog={k: f'http://127.0.0.1:{port}/{k}' for k in I.KATALOG})
    a.update(ek)
    return KM.Prova(**a)


def dondurulmus_kopya():
    """Ön kaydın geçici kopyası: 'Durum:' satırına KOŞU DONDURULDU + iki kod sha256'sı (dondurma eki §8 biçimi)."""
    m = open(ONKAYIT, encoding='utf-8').read()
    L = m.split('\n')
    i = next(j for j, s in enumerate(L) if s.startswith('Durum:'))
    ks = T0.kod_sha()
    L[i] = (f"Durum: KOŞU DONDURULDU (sınama; tr7c_kosu.py {ks['tr7c_kosu.py']}; tr7c_mde_ek.py {ks['tr7c_mde_ek.py']}; "
            f"ek: TR-7c_KOSU-DONDURMA-EKI.md) — " + L[i][len('Durum: '):])
    y = os.path.join(dizin('onkayit'), 'on.md')
    with open(y, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L))
    return y


class Saat:
    """Sınamada denetlenen saat: her `now` çağrısı 1 sn ilerler (eşit saniye belirsizliği sınamayı bozmasın)."""

    def __init__(self):
        self.t = _dt.datetime(2026, 12, 1, tzinfo=_dt.timezone.utc)

    def kur(self, KM):
        s = self

        class D(_dt.datetime):
            @classmethod
            def now(cls, tz=None):
                s.t += _dt.timedelta(seconds=1)
                return s.t
        KM.dt = types.SimpleNamespace(datetime=D, timezone=_dt.timezone, timedelta=_dt.timedelta, date=_dt.date)


# ================================================================ DÜĞME (kuru prova)
def dugme(KM, R):
    g = 'düğme'
    Red = KM.GercekKipReddedildi
    # D1 kapı açıkken (gerçekten dondurulmuş geçici kopya) prova açılmaz
    on = dondurulmus_kopya()
    acik = KM.kosu_dondurulmus_mu(on)
    pr = prova(KM, 'd1')

    def ac_kopya():
        with KM.prova_ac(pr, onkayit=on):
            pass

    def ac_gercek():
        with KM.prova_ac(pr):
            pass
    R.sina(g, 'D1 dondurulmuş metinle (kapı açık) prova_ac reddedilir; kapalı metinle açılır',
           acik[0] and reddedilir(ac_kopya, Red) and KM._PROVA is None and not reddedilir(ac_gercek, Red),
           dict(kapi=acik))
    KM._PROVA = None
    # D2 prova açıkken koşu dondurulursa: gercek_kapi her çağrıda yeniden denetler ve reddeder
    eski = KM.kosu_dondurulmus_mu
    r2 = None
    try:
        with KM.prova_ac(pr):
            KM.kosu_dondurulmus_mu = lambda onkayit=None: (True, 'tamam')
            r2 = reddedilir(lambda: KM.gercek_kapi('sınama'), Red)
    finally:
        KM.kosu_dondurulmus_mu = eski
        KM._PROVA = None
    R.sina(g, 'D2 prova açıkken kapı açılırsa (dondurma) gercek_kapi reddeder: düğme dondurmadan sonra işlemez', r2)
    # D2b düğme elle (prova_ac'sız) kurulup kapı açıksa da reddedilir
    try:
        KM._PROVA = (pr, frozenset({('127.0.0.1', 9)}))
        KM.kosu_dondurulmus_mu = lambda onkayit=None: (True, 'tamam')
        r2b = reddedilir(lambda: KM.gercek_kapi('sınama'), Red)
    finally:
        KM.kosu_dondurulmus_mu = eski
        KM._PROVA = None
    R.sina(g, 'D2b _PROVA elle kurulsa da (prova_ac atlanarak) dondurulmuş kipte gercek_kapi reddeder', r2b)
    # D3 taban URL denetimi
    kotu_url = ['https://127.0.0.1:8080/x', 'http://localhost:8080/x', 'http://127.0.0.1/x', 'http://127.0.0.2:8080/x',
                'http://[::1]:8080/x', 'http://127.0.0.1:8080@service.ncedc.org:80/x',
                'http://service.ncedc.org:80#@127.0.0.1:8080', 'http://2130706433:8080/x', 'http://0.0.0.0:8080/x',
                'http://service.iris.edu:8080/fdsnws', 'ftp://127.0.0.1:21/x']
    kacan = []
    for u in kotu_url:
        for alan in ('servis', 'katalog'):
            k = next(iter(getattr(pr, alan)))
            d = dict(getattr(pr, alan))
            d[k] = u
            p2 = KM.Prova(**{**pr.__dict__, alan: d})
            if not reddedilir(lambda: KM.prova_denetle(p2), Red):
                kacan.append((alan, u))
    eksik = KM.Prova(**{**pr.__dict__, 'servis': {k: v for k, v in list(pr.servis.items())[1:]}})
    fazla = KM.Prova(**{**pr.__dict__, 'katalog': {**pr.katalog, 'gercek': 'http://127.0.0.1:9/x'}})
    R.sina(g, f'D3 taban URL: {len(kotu_url)} kötü biçim × 2 alan reddedilir; eksik/fazla anahtar reddedilir; '
              'http://127.0.0.1:<port> kabul', not kacan and reddedilir(lambda: KM.prova_denetle(eksik), Red) and
           reddedilir(lambda: KM.prova_denetle(fazla), Red) and KM.prova_denetle(pr) == frozenset({('127.0.0.1', 9)}),
           dict(kacan=kacan))
    # D4 prova dizinleri
    bag = os.path.join(dizin('d4'), 'bag')
    os.symlink(YASAK, bag)
    durumlar = dict(depo=dict(dizin=os.path.join(TR7C, 'prova_cikti')), kosu=dict(dizin=CIKTI_GERCEK),
                    zarf_kok=dict(zarf=KM.ZARF_KOK), marmara=dict(zarf=KM.GERCEK_KOKLER[1]),
                    mnt_baska=dict(zarf='/mnt/project-files/turetme/baska'), mnt=dict(dizin='/mnt'),
                    bag_mnt=dict(zarf=bag), bag_alt=dict(zarf=os.path.join(bag, 'turetme', 'tr7c-zarf')))
    kacan = [k for k, v in durumlar.items() if not reddedilir(lambda v=v: KM.prova_denetle(
        KM.Prova(**{**pr.__dict__, **v})), Red)]
    R.sina(g, 'D4 prova dizini depo içi, kosu/, gerçek kökler, /mnt altı ya da /mnt\'ye giden bağ olamaz', not kacan,
           dict(kacan=kacan))
    # D5 prova kancası (doğrudan çağrı; soket açılmaz)
    def k(olay, args):
        try:
            KM._prova_kancasi(olay, args)
            return 'izin'
        except PermissionError:
            return 'ret'
    with KM.prova_ac(pr):
        kurulu = bool(KM._PROVA_KANCA)
        acikken = [k('socket.connect', (None, ('127.0.0.1', 9))), k('socket.connect', (None, ('127.0.0.1', 3128))),
                   k('socket.connect', (None, ('10.0.0.1', 9))), k('socket.connect', (None, '/tmp/s')),
                   k('socket.getaddrinfo', ('127.0.0.1', 9, 0, 0, 0, 0)),
                   k('socket.getaddrinfo', ('service.ncedc.org', 443, 0, 0, 0, 0)),
                   k('socket.getaddrinfo', (b'127.0.0.1', '9', 0, 0, 0, 0)),
                   k('socket.getaddrinfo', ('127.0.0.1', 443, 0, 0, 0, 0)),
                   k('socket.gethostbyname', ('earthquake.usgs.gov',)), k('socket.sendto', (None, b'', ('1.1.1.1', 53)))]
    kapali = [k('socket.connect', (None, ('10.0.0.1', 9))), k('socket.getaddrinfo', ('x.org', 443, 0, 0, 0, 0))]
    R.sina(g, 'D5 prova kancası: yalnız izinli (127.0.0.1, port) bağlantı/ad çözümü; vekil portu, dış ad, '
              'gethostbyname, sendto reddedilir; prova kapalıyken kanca etkisiz',
           kurulu and acikken == ['izin', 'ret', 'ret', 'ret', 'izin', 'ret', 'izin', 'ret', 'ret', 'ret'] and
           kapali == ['izin', 'izin'], dict(acikken=acikken, kapali=kapali))
    # D6 GercekOrtam provada gerçek köklere bakmaz (TR7_HAM_DIZIN de dinlenmez); prova dışında git doğrulaması açık
    eski_ham = os.environ.get('TR7_HAM_DIZIN')
    os.environ['TR7_HAM_DIZIN'] = '/mnt/project-files/turetme/tr7c-zarf/ham'
    try:
        with KM.prova_ac(pr):
            go = KM.GercekOrtam()
            pv = dict(zarf=go.zarf, yol=go.yol('tr7c_manifest.json'), durum=go.yol('TR7_KOSU_DURUM.json'),
                      zyol=go.zyol('katalog'), hyol=go.hyol('lp', 'x.mseed'), git=go.git_dogrula,
                      servis=go.servis == pr.servis, katalog=go.katalog == pr.katalog, cikti=KM._cikti())
        kapali_red = reddedilir(KM.GercekOrtam, Red)        # prova dışında, kapı kapalı: kurucu reddeder
        eski_k = KM.kosu_dondurulmus_mu
        KM.kosu_dondurulmus_mu = lambda onkayit=None: (True, 'tamam')     # dondurulmuş kip benzetimi (kurucu saf)
        try:
            go2 = KM.GercekOrtam()
        finally:
            KM.kosu_dondurulmus_mu = eski_k
        dis = dict(zarf=go2.zarf, git=go2.git_dogrula, servis=go2.servis, katalog=go2.katalog, cikti=KM._cikti(),
                   kapali_red=kapali_red)
    finally:
        if eski_ham is None:
            os.environ.pop('TR7_HAM_DIZIN', None)
        else:
            os.environ['TR7_HAM_DIZIN'] = eski_ham
        KM._PROVA = None
    pz = os.path.realpath(pr.zarf)
    ok6 = (pv['zarf'] == pr.zarf and pv['yol'].startswith(pr.dizin + os.sep) and pv['durum'].startswith(pr.dizin + os.sep)
           and os.path.realpath(pv['zyol']).startswith(pz) and os.path.realpath(pv['hyol']).startswith(pz)
           and pv['git'] is False and pv['servis'] and pv['katalog'] and pv['cikti'] == pr.dizin)
    ok6b = dis == dict(zarf=KM.ZARF_KOK, git=True, servis=None, katalog=None, cikti=KM.CIKTI, kapali_red=True)
    R.sina(g, 'D6 provada GercekOrtam: zarf/ham/çıktı prova dizinlerinde (TR7_HAM_DIZIN=/mnt/... olsa da), servis ve '
              'katalog prova tabanı, git doğrulaması kapalı', ok6, pv)
    R.sina(g, 'D6b prova dışında GercekOrtam: kapı kapalıyken kurulamaz; dondurulmuş kipte ZARF_KOK, CIKTI, git doğrulaması AÇIK, taban None', ok6b, dis)
    # D7 provada k1c_kos gerçek çıktı dizinine yazamaz (dizin prova dizini olmalı)
    class Sahte(KM.Kaynak):
        gercek = True

        def birimler(self):
            raise AssertionError('dokunuldu')
    with KM.prova_ac(pr):
        r7 = [reddedilir(lambda d=d: KM.k1c_kos(Sahte(), d, KM.Ayar(), gercek=True), Red)
              for d in (KM.CIKTI, os.path.join(KM.CIKTI, 'alt'), KM.ZARF_KOK, os.path.join(GECICI, 'baska'))]
    KM._PROVA = None
    R.sina(g, 'D7 provada k1c_kos(gercek=True) kosu/, kosu/ altı, ZARF_KOK ve prova dışı dizinle reddedilir', all(r7), r7)
    # D8 manifest isteği provada prova tabanına gider (taban geçişi)
    class Dur(Exception):
        pass
    urller = []

    def kat_iste(cl, dz, kt, url, anahtar):
        urller.append(url)
        raise Dur()
    d8 = dizin('d8')
    go = types.SimpleNamespace(T=types.SimpleNamespace(I=I, _katalog_iste=kat_iste), istemci=lambda: None,
                               zyol=lambda *p: os.path.join(d8, *p), katalog=dict(pr.katalog), servis=dict(pr.servis))
    with KM.prova_ac(pr):
        try:
            KM.asama_manifest(go, KM.birimler_kur())
        except Dur:
            pass
    KM._PROVA = None
    R.sina(g, 'D8 provada manifest ComCat isteği prova tabanına (http://127.0.0.1:9/comcat) gider; katalog/ dizini kurulur',
           len(urller) == 1 and urller[0].startswith('http://127.0.0.1:9/comcat?') and os.path.isdir(os.path.join(d8, 'katalog')),
           dict(url=urller[:1]))


# ================================================================ PROTOKOL (aşama önkoşulu, durma kaydı)
def protokol(KM, R):
    g = 'protokol'
    D = KM.Tr7cDur
    Saat().kur(KM)
    pr = prova(KM, 'p')
    gov = {'hata': None}

    def govde(go, asama, dz):
        if gov['hata']:
            raise gov['hata']
        y = os.path.join(dz, f'{asama}.cikti')
        with open(y, 'w') as f:
            f.write(asama)
        return dict(asama=asama), [y]
    KM._asama_govde = govde
    dur = lambda: KM.durum_oku(pr.dizin)   # noqa: E731
    ok = {}
    with KM.prova_ac(pr):
        ok['P1 sıra dışı baslat (K1c-indirme manifest\'ten önce) reddedilir'] = reddedilir(
            lambda: KM.baslat('K1c-indirme'), D)
        ok['P1b bilinmeyen aşama reddedilir'] = reddedilir(lambda: KM.baslat('Marmara-indirme'), D)
        ok['P4 başlatılmamış aşama kos edilemez'] = reddedilir(lambda: KM.asama_kos('manifest'), D)
        ok['P2 baslat manifest → yeni'] = KM.baslat('manifest') == 'yeni'
        ok['P2b ikinci baslat (başladı iken) reddedilir'] = reddedilir(lambda: KM.baslat('manifest'), D)
        s0 = dur()['asamalar']['manifest']
        ok['P2c başladı kaydı tr7c_kosu.py sha256\'sını taşır'] = s0['sha256'].get('tr7c_kosu.py') == \
            KM.sha256_dosya(KOSU_YOL)
        # P5 kod değişikliği
        d = dur()
        d['asamalar']['manifest']['sha256']['tr7c_kosu.py'] = '0' * 64
        KM.json_yaz(os.path.join(pr.dizin, KM.DURUM_AD), d)
        ok['P5 baslat\'tan sonra kod değişmişse kos reddedilir'] = reddedilir(lambda: KM.asama_kos('manifest'), D)
        d['asamalar']['manifest']['sha256']['tr7c_kosu.py'] = KM.sha256_dosya(KOSU_YOL)
        KM.json_yaz(os.path.join(pr.dizin, KM.DURUM_AD), d)
        KM.asama_kos('manifest')
        ok['P3 kos → tamamlandı'] = dur()['asamalar']['manifest']['durum'] == 'tamamlandı'
        ok['P3b tamamlanmış aşama yeniden başlatılamaz (--surdur ile de)'] = reddedilir(
            lambda: KM.baslat('manifest'), D) and reddedilir(lambda: KM.baslat('manifest', surdur=True), D)
        # P6 kod hatası → hata + kod durma kaydı
        KM.baslat('K1c-indirme')
        gov['hata'] = ValueError('bozuk miniSEED')
        r6 = reddedilir(lambda: KM.asama_kos('K1c-indirme'), D)
        gov['hata'] = None
        d = dur()
        ok['P6 gövde hatası → durum hata, durmalar\'da tür kod (ileti ve saat)'] = r6 and \
            d['asamalar']['K1c-indirme']['durum'] == 'hata' and any(
                x['asama'] == 'K1c-indirme' and x['tur'] == 'kod' and 'bozuk miniSEED' in x['neden'] and x.get('zaman')
                for x in d['durmalar'])
        ok['P6b hata durumundaki aşama baslat\'sız kos edilemez'] = reddedilir(lambda: KM.asama_kos('K1c-indirme'), D)
        KM.baslat('K1c-indirme')
        KM.asama_kos('K1c-indirme')
        # P10 kos önceki aşama tamamlanmadıysa reddeder (durum dosyası elle bozulmuş)
        KM.baslat('K1c-negatif')
        d = dur()
        d['asamalar']['K1c-indirme']['durum'] = 'hata'
        KM.json_yaz(os.path.join(pr.dizin, KM.DURUM_AD), d)
        ok['P10 kos: önceki aşama tamamlanmamışsa reddedilir'] = reddedilir(lambda: KM.asama_kos('K1c-negatif'), D)
        d['asamalar']['K1c-indirme']['durum'] = 'tamamlandı'
        KM.json_yaz(os.path.join(pr.dizin, KM.DURUM_AD), d)
        # P7 algılama aşaması: kesinti, yeniden giriş kuralları
        gov['hata'] = RuntimeError('teknik çöküş')
        reddedilir(lambda: KM.asama_kos('K1c-negatif'), D)
        gov['hata'] = None
        ok['P7 algılama aşamasına --surdur\'suz yeniden giriş reddedilir'] = reddedilir(
            lambda: KM.baslat('K1c-negatif'), D)
        ok['P7b yalnız kod durma kaydıyla --surdur reddedilir (elle kayıt gerekir)'] = reddedilir(
            lambda: KM.baslat('K1c-negatif', surdur=True), D)
        ok['P7c boş durma nedeni reddedilir'] = reddedilir(lambda: KM.durdu('K1c-negatif', '  '), D)
        KM.durdu('K1c-negatif', 'teknik çöküş: ileti, saat')
        ok['P7d durdu → hata + elle kayıt; kos baslat\'sız reddedilir'] = dur()['asamalar']['K1c-negatif']['durum'] == \
            'hata' and any(x['tur'] == 'elle' for x in dur()['durmalar']) and reddedilir(
                lambda: KM.asama_kos('K1c-negatif'), D)
        ok['P7e elle kayıttan sonra baslat --surdur → surdur'] = KM.baslat('K1c-negatif', surdur=True) == 'surdur'
        # P8 eski elle kayıt yeni bir kesintiyi örtmez
        gov['hata'] = RuntimeError('ikinci çöküş')
        reddedilir(lambda: KM.asama_kos('K1c-negatif'), D)
        gov['hata'] = None
        ok['P8 yeni kesintiden sonra eski elle kayıt yetmez (--surdur reddedilir)'] = reddedilir(
            lambda: KM.baslat('K1c-negatif', surdur=True), D)
        KM.durdu('K1c-negatif', 'ikinci çöküş')
        KM.baslat('K1c-negatif', surdur=True)
        KM.asama_kos('K1c-negatif')
        # P9 bilinen sınır (bilgi): SIGKILL benzeri ölümden sonra ('başladı'da kalır) kos elle kayıt istemeden sürer
        KM.baslat('K1c-algılama')
        sinir = not reddedilir(lambda: KM.asama_kos('K1c-algılama'), D)
        ok['P11 durma kayıtlarında yalnız aşama/tür/neden/zaman'] = all(
            set(x) == {'asama', 'tur', 'neden', 'zaman'} for x in dur()['durmalar'])
        ok['P12 durum dosyası aşama kayıtları yalnız durum/zaman/sha256'] = all(
            set(v) == {'durum', 'zaman', 'sha256'} for v in dur()['asamalar'].values())
    KM._PROVA = None
    for ad, v in ok.items():
        R.sina(g, ad, v)
    R.sina('bilgi', 'P9 (bilgi, kodun bugünkü davranışı) "başladı"da kalan aşama elle durma kaydı istenmeden kos edilir '
           '(TR-7 ile aynı; dondurma eki §7)', sinir)


def suite(KM):
    R = Kayit()
    for ad, fn in (('düğme', lambda: dugme(KM, R)), ('protokol', lambda: protokol(KM, R))):
        try:
            fn()
        except BaseException as e:   # noqa: BLE001
            R.sina('çöküş', f'{ad}: {type(e).__name__}: {str(e)[:200]}', False)
        finally:
            KM._PROVA = None
    return R


MUTASYONLAR = [
    ('düğme: gercek_kapi prova kolunda yeniden denetlemez', "    if _PROVA is not None:\n        prova_denetle(_PROVA[0])\n",
     "    if _PROVA is not None:\n"),
    ('düğme: prova dondurmaya bakmaz', "    if ok:\n        raise GercekKipReddedildi('PROVA REDDEDİLDİ: koşu dondurulmuş",
     "    if False:\n        raise GercekKipReddedildi('PROVA REDDEDİLDİ: koşu dondurulmuş"),
    ('taban: host denetimi yok', "x.hostname != '127.0.0.1' or ", ''),
    ('taban: port denetimi yok', ' or not x.port:', ':'),
    ('taban: https de kabul', "x.scheme != 'http'", "x.scheme not in ('http', 'https')"),
    ('taban: localhost da kabul', "x.hostname != '127.0.0.1'", "x.hostname not in ('127.0.0.1', 'localhost')"),
    ('kanca: 127.0.0.1\'in her portu', '(a[0], a[1]) in izin', "a[0] == '127.0.0.1'"),
    ('kanca: ad çözümü serbest', 'if (h, p) not in izin:', 'if False:'),
    ('düğme: /mnt denetimi yok', " or r == '/mnt' or r.startswith('/mnt' + os.sep)", ''),
    ('düğme: GercekOrtam provada gerçek zarf kökü', '            zarf = pr.zarf\n', '            pass\n'),
    ('düğme: hyol provada TR7_HAM_DIZIN\'i dinler', "        if _PROVA is not None:\n            return os.path.join(self.zarf, 'ham', *p)\n",
     ''),
    ('düğme: _cikti provada CIKTI', 'return _PROVA[0].dizin if _PROVA is not None else CIKTI', 'return CIKTI'),
    ('düğme: k1c_kos dizin denetimi gevşek (gerçek yol da olur)', 'not _cikti_mi(dizin)',
     'not (gercek_yol_mu(dizin) or _cikti_mi(dizin))'),
    ('taban: manifest tetikleyici isteği taban almaz', 'K.E1_M7, taban=go.katalog)', 'K.E1_M7)'),
    ('düğme: GercekOrtam prova dışında git doğrulamasız', '        self.git_dogrula = pr is None', '        self.git_dogrula = False'),
    ('aşama sırası: baslat önceki aşamaya bakmaz', 'if i > 0 and a.get(ASAMALAR[i - 1]', 'if False and a.get(ASAMALAR[i - 1]'),
    ('aşama sırası: kos önceki aşamaya bakmaz', "if i > 0 and d['asamalar'].get(ASAMALAR[i - 1]",
     "if False and d['asamalar'].get(ASAMALAR[i - 1]"),
    ('tek koşu: tamamlanmış aşama yeniden', "    if mevcut.get('durum') == 'tamamlandı':\n        raise Tr7cDur(f'\"{asama}\" zaten tamamlandı",
     "    if False:\n        raise Tr7cDur(f'\"{asama}\" zaten tamamlandı"),
    ('durma: algılamaya --surdur\'suz yeniden giriş', 'if asama in ALGILAMA_ASAMALARI and not surdur:', 'if False:'),
    ('durma: kod durması da sürdürmeye yeter', "x.get('tur') == 'elle' and ", ''),
    ('durma: eski elle kayıt yeter', " and x['zaman'] >= mevcut.get('zaman', '')", ''),
    ('kos: kod değişikliğini reddetmez', "if (a.get('sha256') or {}).get('tr7c_kosu.py') != sha256_dosya(os.path.abspath(__file__)):",
     'if False:'),
    ('durma: hata yolunda kod durma kaydı yok', "        durma_yaz(dz, asama, neden, 'kod')\n", ''),
    ('aşama: baslat başladı\'yı yeniden yazar', "    if m and m.get('durum') == 'başladı':", '    if False:'),
    ('durma: boş neden kabul', '    if not str(neden).strip():', '    if False:'),
    ('kos: hata durumundaki aşamayı baslat\'sız koşar', "if not a or a.get('durum') != 'başladı':",
     "if not a or a.get('durum') not in ('başladı', 'hata'):"),
]


def main():
    a = sys.argv[1:]
    cikti = a[0]
    os.makedirs(GECICI, exist_ok=True)
    ara = cikti + '.mut.jsonl'
    if '--birlestir' not in a:
        t0 = time.time()
        R = suite(T0)
        for x in R.s:
            print(('GEÇTİ ' if x['gecti'] else 'KALDI ') + f"[{x['grup']}] {x['ad']}", flush=True)
            if not x['gecti']:
                print('    ', json.dumps(x['ayrinti'], ensure_ascii=False, default=str)[:600], flush=True)
        ana = dict(sinamalar=R.s, sure=round(time.time() - t0, 1))
        with open(cikti + '.ana.json', 'w', encoding='utf-8') as f:
            json.dump(ana, f, ensure_ascii=False, default=str)
        if '--mutasyonsuz' not in a:
            parca = tuple(int(x) for x in a[a.index('--parca') + 1].split('/')) if '--parca' in a else (0, 1)
            yapilan = set()
            if os.path.exists(ara):
                yapilan = {json.loads(s)['ad'] for s in open(ara, encoding='utf-8') if s.strip()}
            kaynak = open(KOSU_YOL, encoding='utf-8').read()
            for i, (ad, eski, yeni) in enumerate(MUTASYONLAR):
                if i % parca[1] != parca[0] or ad in yapilan:
                    continue
                n0 = len(ENGEL)
                if kaynak.count(eski) != 1:
                    r = dict(ad=ad, durum=f'uygulanamadı ({kaynak.count(eski)})', yakalandi=False)
                else:
                    try:
                        Rm = suite(modul_yukle(kaynak.replace(eski, yeni), f'tr7c_kosu_k2mut{i}'))
                        kalan = [f"[{x['grup']}] {x['ad']}" for x in Rm.s if not x['gecti'] and x['grup'] != 'bilgi']
                    except BaseException as e:   # noqa: BLE001
                        kalan = [f'yükleme: {type(e).__name__}: {str(e)[:150]}']
                    r = dict(ad=ad, yakalandi=bool(kalan), yakalayan=kalan[:4], yasak_girisim=len(ENGEL) - n0)
                with open(ara, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(r, ensure_ascii=False) + '\n')
                print(('YAKALANDI ' if r['yakalandi'] else 'YAKALANMADI ') + ad, r.get('yakalayan', [])[:2], flush=True)
    ana = json.load(open(cikti + '.ana.json', encoding='utf-8'))
    mut = [json.loads(s) for s in open(ara, encoding='utf-8') if s.strip()] if os.path.exists(ara) else []
    grup = {}
    for x in ana['sinamalar']:
        grup.setdefault(x['grup'], [0, 0])
        grup[x['grup']][0] += 1
        grup[x['grup']][1] += x['gecti']
    out = dict(aciklama='TR-7c kod incelemesi-2: b0f70642… → c86d8b9b… farkı (kuru prova düğmesi, taban, aşama protokolü, '
                        'durma kaydı); yalnız yapay; hiçbir soket açılmaz; aşama gövdesi saplanır.',
               kod_sha256={'tr7c_kosu.py': T0.sha256_dosya(KOSU_YOL), 'tr7c_kodinc2.py': T0.sha256_dosya(__file__)},
               sinama=dict(gruplar=grup), sinamalar=ana['sinamalar'],
               mutasyon=dict(toplam=len(MUTASYONLAR), koşulan=len(mut), yakalanan=sum(m['yakalandi'] for m in mut),
                             liste=mut), engellenen_giris=ENGEL)
    with open(cikti, 'w', encoding='utf-8') as f:
        f.write(json.dumps(out, ensure_ascii=False, indent=1, default=str) + '\n')
    print(json.dumps(dict(sinama=grup, mutasyon=[len(MUTASYONLAR), len(mut), out['mutasyon']['yakalanan']],
                          engellenen=len(ENGEL)), ensure_ascii=False))


if __name__ == '__main__':
    main()
