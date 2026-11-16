#!/usr/bin/env python3
"""TR-4 koşu kodu bağımsız incelemesi (TR-4_KOD-INCELEME.md): incelemecinin kendi sınamaları (I01–I15) ve kendi
mutasyonları (N01–N23). YALNIZ yapay veri ve 127.0.0.1; gerçek dalga formu, üstveri ya da KOERI/FDSN isteği yok.
Yazarın sınama düzeneği (`tr4_test_yapay.py`: ağ korkuluğu, sahte sunucu, yapay girdiler) içe aktarılır; sınamalar ve
mutantlar ondan bağımsızdır.

Kullanım (kök dizinden):
  python3 -I -B kayit/turetme/tr4/inc_kod/tr4_inc_kod_sinama.py <karalama> <npz> [--mutasyon [--yalniz=N01,N02]] [--kod <dizin>]
--mutasyon: her mutant için kodun kopyası değiştirilir; yazarın hızlı sınamaları (--hizli) VE bu dosyanın sınamaları
o kopyada koşulur; mutant, ikisinden biri kalırsa yakalanmış sayılır (hangisinin yakaladığı ayrı yazılır).
"""
import datetime as dt, hashlib, importlib.util, json, math, os, re, shutil, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

import numpy as np

BURASI = os.path.dirname(os.path.abspath(__file__))
KOD = os.path.dirname(BURASI)
for i, a in enumerate(sys.argv):
    if a == '--kod': KOD = sys.argv[i + 1]
TD = dt.timedelta

sp = importlib.util.spec_from_file_location('tt', os.path.join(KOD, 'tr4_test_yapay.py'))
tt = importlib.util.module_from_spec(sp); sp.loader.exec_module(tt)       # ağ korkuluğu + IN, K (aynı --kod)
IN, K = tt.IN, tt.K
SONUC = []


def sina(ad):
    def d(f):
        def g(*a):
            t0 = time.time()
            try:
                f(*a); SONUC.append((ad, True, '')); print(f'GEÇTİ {ad} ({time.time() - t0:.1f} sn)', flush=True)
            except BaseException as e:
                SONUC.append((ad, False, f'{type(e).__name__}: {e}')); print(f'KALDI {ad}: {type(e).__name__}: {str(e)[:300]}', flush=True)
        return g
    return d


def kos(KAR, ad, ist, Tler, dav, butce='bitti', kod_f=None, hukum_on=None):
    """olc'u sahte 1b/(i)/Δ/bilgi işlevleriyle koşar. kod_f(x) → istasyon-ay satırının kodu (None: satır yok)."""
    depo = tt.temiz(os.path.join(KAR, ad))
    G = tt.yapay_csv(tt.yapay_G(ist, list(Tler)), depo)
    IN.yaz_json(IN.durum_yollari(depo)['butce'], dict(durum=butce, ilk_istek=1.0, bitis=1.0 + 30 * 86400, etkin_sn=21 * 86400.0,
                                                      isler=[], tur=False))
    with open(IN.durum_yollari(depo)['gunluk'], 'w') as f:
        for x in IN.plan(G):
            k = kod_f(x) if kod_f else 200
            if k is not None: f.write(json.dumps(dict(k=x['k'], kod=k)) + '\n')
    if hukum_on:
        os.makedirs(os.path.join(depo, 'kosu'), exist_ok=True); IN.yaz_json(os.path.join(depo, 'kosu', 'hukum.json'), hukum_on)
    y = tt.kosu_stub(dav)
    try: return K.olc(None, depo, None, G=G), depo, G
    finally: K.b1_hesapla, K.denetim_i, K.hepsini_hesapla, K.bilgi_satirlari = y


IST12 = [f'KO.S{i:02d}' for i in range(12)]
Z = np.random.default_rng(20261116).standard_normal(400)


# ================================================================ kesik koşu gövdesi
@sina('I01 kesik: yalnız T 2021 eksikse "veri yok (indirme bütçesi)"')
def i01(KAR):
    H, _, _ = kos(KAR, 'i01', IST12, (2017, 2020, 2021), dict(delta=lambda i, w: Z[i] * 5e-4), butce='kesildi',
                  kod_f=lambda x: 'URLError' if x['k'] == 'KO.S03|2020-11' else 200)
    assert H['hukum'] == 'veri yok (indirme bütçesi)', H['metin']
    assert H['metin'].startswith('veri yok (indirme bütçesi). tamamlanan T: 2017, 2020; T başına yer: 2017: 12, 2018: 0, 2019: 0, 2020: 12, 2021: 0,'), H['metin']


@sina('I02 kesik: T 2017–2021 tam ama tamamlanan T ile kapı tutmuyorsa "veri yok (indirme bütçesi)"')
def i02(KAR):
    H, _, _ = kos(KAR, 'i02', IST12, (2017, 2018), dict(delta=lambda i, w: Z[i] * 5e-4), butce='kesildi')
    assert H['hukum'] == 'veri yok (indirme bütçesi)', H['metin']
    # aynı veri tam (kesilmemiş) koşuda 1b kapısıyla düşer: iki dal ayrışır
    H2, _, _ = kos(KAR, 'i02b', IST12, (2017, 2018), dict(delta=lambda i, w: Z[i] * 5e-4), butce='bitti')
    assert H2['hukum'] == 'veri yok (gün doluluğu)', H2['metin']


@sina('I03 bilgi satırı 0 sınırları: n = 30 ve yer = 6 hesaplanır; n 29 ya da yer 5 hesaplanmaz')
def i03(KAR):
    i6 = [f'KO.S{i:02d}' for i in range(6)]
    H, _, _ = kos(KAR, 'i03a', i6, range(2017, 2022), dict(delta=lambda i, w: Z[i] * 5e-4))
    assert H['hukum'] == 'veri yok (gün doluluğu)' and '; bilgi satırı 0: σ̂_Δ ' in H['metin'] and H['metin'].endswith(
        'n 30, yer 6, T 2017, 2018, 2019, 2020, 2021'), H['metin']
    H, _, _ = kos(KAR, 'i03b', i6, range(2017, 2022), dict(delta=lambda i, w: float('nan') if i == 0 else Z[i] * 5e-4))
    assert H['metin'].endswith('bilgi satırı 0: hesaplanmadı (n = 29, yer = 6)'), H['metin']
    H, _, _ = kos(KAR, 'i03c', i6[:5], range(2017, 2023), dict(delta=lambda i, w: Z[i] * 5e-4))
    assert H['metin'].endswith('bilgi satırı 0: hesaplanmadı (n = 30, yer = 5)'), H['metin']


@sina('I04 (ii-a) aralığının iki ucu: 0,81 ve 1,19 geçer, 0,79 ve 1,25 "geçersiz (kod)"')
def i04(KAR):
    for o, ok in ((0.81, True), (1.19, True), (0.79, False), (1.25, False)):
        H, _, _ = kos(KAR, f'i04_{o}', IST12, (2017, 2020, 2021), dict(delta=lambda i, w: Z[i] * 5e-4, oran=o))
        assert (H['hukum'] != 'geçersiz (kod)') == ok, (o, H['metin'][:80])
        if not ok: assert H['metin'] == f"geçersiz (kod). medyan oran {K.yz(o)}", H['metin']


def bagimsiz_onyukleme(rows, metin, B=2000):
    """Bağımsız yazım: hücre ağırlığı = yer çokluğu × yıl çokluğu (§4.2), np.add.at ile ağırlıklı örnek."""
    tohum = int(hashlib.sha256(metin.encode()).hexdigest()[:8], 16)
    rng = np.random.default_rng(tohum)
    yerler = sorted({r[0] for r in rows}); yillar = sorted({r[1] for r in rows})
    ms = rng.multinomial(len(yerler), [1 / len(yerler)] * len(yerler), size=B)
    my = rng.multinomial(len(yillar), [1 / len(yillar)] * len(yillar), size=B)
    v = np.array([r[2] for r in rows]) * 100
    sg, qq = [], []
    for b in range(B):
        x = []
        for (s, y, _), d in zip(rows, v): x.extend([d] * int(ms[b][yerler.index(s)] * my[b][yillar.index(y)]))
        if len(x) < 5: continue
        x = np.sort(np.array(x)); med = np.median(x)
        sg.append(1.4826 * np.median(np.abs(x - med))); qq.append(np.quantile(np.abs(x), 0.95))
    return np.quantile(sg, [0.05, 0.95]), np.quantile(qq, [0.025, 0.975])


@sina('I05 hüküm önyüklemesi olc yolunda: tohum sha256("tr4-hukum|20261202")[:8], B = 2000, aralıklar bağımsız hesapla aynı')
def i05(KAR):
    H, _, G = kos(KAR, 'i05', IST12, (2017, 2020, 2021), dict(delta=lambda i, w: Z[i] * 5e-4))
    R = {w['k']: Z[i] * 5e-4 for i, w in enumerate(G['W'])}         # sahte Δ hesabı W sırasıyla
    rows = [(w['yer'], w['T'].year, R[w['k']]) for w in G['W']]
    (sL, sU), (qL, qU) = bagimsiz_onyukleme(rows, 'tr4-hukum|20261202')
    t = H['taban']
    assert np.allclose([t['sigma_L'], t['sigma_U'], t['q95_L'], t['q95_U']], [sL, sU, qL, qU], rtol=0, atol=1e-12), (t, sL, sU, qL, qU)
    v = np.array([r[2] for r in rows]) * 100
    assert abs(t['sigma'] - 1.4826 * np.median(np.abs(v - np.median(v)))) < 1e-12
    assert H['hukum'] == ('taban ölçüldü; TR-5b (c) karşılandı' if sU < 0.20 else 'taban ölçüldü; TR-5b (c) belirsiz')


# ================================================================ enerji reddi, 1b, maske
@sina('I06 enerji reddi medyanı yalnız yer-penceresinin [a, b] saatlerinden')
def i06(KAR):
    nl = 2401; d0 = dt.date(2016, 3, 1); V = {}; rng = np.random.default_rng(6)
    gl = [d0 + TD(days=i) for i in range(-10, 4)]
    for d in gl:
        rms = np.ones((4, 3), np.float32) * (100.0 if d < d0 else 1.0)          # pencere dışı 10 gün çok gürültülü
        V[d.toordinal()] = (rng.standard_normal((4, 3, nl)).astype(np.float32), rms, np.ones((4, 3), np.float32))
    V[(d0 + TD(days=2)).toordinal()][1][1, 0] = 3.5
    ccf, gec, red = K.gunluk_cif(V, gl, set(), (d0, d0 + TD(days=3)))
    i = gl.index(d0 + TD(days=2)); a = V[(d0 + TD(days=2)).toordinal()][0].astype(float)
    assert np.allclose(ccf[0, i], a[[0, 2, 3], 0].mean(0)), 'pencere içi medyanla 3,5 × saat atılmalıydı'
    assert abs(red - 41 / 56) < 1e-12, red                                   # 40 pencere dışı saat + 1


@sina('I07 1b: maskeli günler ne payda ne payda sayılır (oranlar tam 1,0)')
def i07(KAR):
    depo = tt.temiz(os.path.join(KAR, 'i07'))
    G = tt.yapay_csv(tt.yapay_G(['KO.A01'], [2017]), depo)
    tt.yapay_depo(depo, G, eksik=0.0)
    satir, _ = IN.son_durum(IN.satirlar(IN.durum_yollari(depo)['gunluk']))
    M = {d for d in (dt.date(2016, 3, 1) + TD(days=i) for i in range(60))}
    b = K.b1_hesapla(G['W'], depo, satir, {G['W'][0]['k']: M}, 'C')[G['W'][0]['k']]
    assert b['oran'] == [1.0, 1.0, 1.0] and b['dolu'], b


@sina('I08 M5 maskesi: 2019 Silivri, T 2020 penceresinde tam 60 gün; csv ile uyuşmazlıkta durur')
def i08(KAR):
    import csv
    depo = tt.temiz(os.path.join(KAR, 'i08'))
    G = tt.yapay_csv(tt.yapay_G(['KO.A01'], [2020]), depo)
    R = list(csv.DictReader(open(G['csv_yol'], encoding='utf-8')))
    R[0]['maske_olay'] = 'us70005lkl'; R[0]['maske_gun'] = '60'
    with open(G['csv_yol'], 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, list(R[0])); w.writeheader(); w.writerows(R)
    K.SHA['tr4_pencereler.csv'] = IN.sha_dosya(G['csv_yol'])
    M = K.maske_gunleri(G)[G['W'][0]['k']]
    assert M == {dt.date(2019, 9, 26) + TD(days=i) for i in range(60)}, (min(M), max(M), len(M))


# ================================================================ indirme: tur, yeniden deneme, akış, iş sonu
@sina('I09 tek tur eşiği: başarısız oran tam %5 iken tur açılmaz')
def i09(KAR):
    depo = tt.temiz(os.path.join(KAR, 'i09')); S = tt.saat_tak()
    G = tt.yapay_G(['KO.A01', 'KO.B02'], [2017])
    P40 = IN.plan(G)[:40]; kotu = [P40[3]['k'], P40[17]['k']]
    srv = tt.Sunucu('kisa', {k: [500, 500, 200] for k in kotu}, S)
    eski = IN.plan; IN.plan = lambda G: [dict(x) for x in P40]
    try:
        for _ in range(6):
            B = IN.indir(None, depo, os.path.join(KAR, 'i09_yerel'), 6000, taban=srv.url, G=G)
            if B['durum'] == 'bitti': break
        d, n = IN.son_durum(IN.satirlar(IN.durum_yollari(depo)['gunluk']))
        assert B['durum'] == 'bitti' and B['tur'] is False and all(n[k] == 2 for k in kotu), (B['tur'], [n[k] for k in kotu])
    finally:
        IN.plan = eski; srv.kapat()


@sina('I10 körlük: tam boy plan (A, T 2017–2024, bilgi 13) istek bitişleri ≤ 2023-12-24 02:00 / 2025-05-31 02:00; GET yolunda 2026 bağlantısız red')
def i10(KAR):
    G = tt.yapay_G([f'KO.S{i:02d}' for i in range(3)], list(range(2017, 2025)), kademe='A', b13=True)
    P = IN.plan(G); son_ana = son_b13 = dt.datetime(1, 1, 1)
    for x in P:
        for l in IN.post_govde(x, G['konum']).splitlines():
            t1 = dt.datetime.fromisoformat(l.split()[5])
            if x['rol'] == 'ana': son_ana = max(son_ana, t1)
            else: son_b13 = max(son_b13, t1)
    assert son_ana == dt.datetime(2023, 12, 24, 2) and son_b13 == dt.datetime(2025, 5, 23, 2), (son_ana, son_b13)
    S = tt.saat_tak(); srv = tt.Sunucu('kisa', {}, S)
    eski = IN.plan
    try:
        G2 = tt.yapay_G(['KO.A01'], [2017], bicim='GET')
        IN.plan = lambda G: [dict(k='KO.A01|2025-12', ist='KO.A01', ay='2025-12', rol='bilgi13', loc='', bant='HH',
                                  yatay=['N', 'E'], gunler=['2025-12-30', '2026-01-01'])]
        try: IN.indir(None, tt.temiz(os.path.join(KAR, 'i10')), os.path.join(KAR, 'i10_yerel'), 600, taban=srv.url, G=G2); raise AssertionError('red yok')
        except SystemExit as e: assert 'KÖRLÜK' in str(e), e
        assert srv.baglanti == 0
    finally:
        IN.plan = eski; srv.kapat()


@sina('I11 yeniden deneme sonraki işte; sunucu kesintisinde iş 5 ardışık hatadan sonra biter (Ö1)')
def i11(KAR):
    depo = tt.temiz(os.path.join(KAR, 'i11')); S = tt.saat_tak()
    dav = {f'KO.A01|2014-{m:02d}': [500] for m in range(1, 9)}
    srv = tt.Sunucu('kisa', dav, S)
    try:
        G = tt.yapay_G(['KO.A01'], [2017])
        B = IN.indir(None, depo, os.path.join(KAR, 'i11_yerel'), 6000, taban=srv.url, G=G)
        k1 = [r['k'] for r in srv.istekler]
        assert len(k1) == 5 and len(set(k1)) == 5, k1                        # 5 ardışık hata → iş biter, tekrar yok
        for _ in range(4):
            n0 = len(srv.istekler)
            B = IN.indir(None, depo, os.path.join(KAR, 'i11_yerel'), 6000, taban=srv.url, G=G)
            kk = [r['k'] for r in srv.istekler[n0:]]
            assert len(kk) == len(set(kk)), 'aynı işte yeniden deneme'
            if B['durum'] == 'bitti': break
        d, n = IN.son_durum(IN.satirlar(IN.durum_yollari(depo)['gunluk']))
        assert B['durum'] == 'bitti' and all(d[k]['kod'] == 200 and n[k] == 2 for k in dav), [(k, n[k]) for k in dav]
    finally:
        srv.kapat()


@sina('I12 akış işler arasında sürer: ≥ 2 sn ve Retry-After yeni işte de beklenir (Ö1)')
def i12(KAR):
    depo = tt.temiz(os.path.join(KAR, 'i12')); S = tt.saat_tak()
    dav = {f'KO.A01|2014-{m:02d}': [500] for m in range(1, 5)}; dav['KO.A01|2014-05'] = [503]
    srv = tt.Sunucu('kisa', dav, S)
    try:
        G = tt.yapay_G(['KO.A01'], [2017])
        IN.indir(None, depo, os.path.join(KAR, 'i12_yerel'), 6000, taban=srv.url, G=G)
        n1 = len(srv.istekler); assert n1 == 5
        IN.indir(None, depo, os.path.join(KAR, 'i12_yerel'), 6000, taban=srv.url, G=G)
        t = [r['t'] for r in srv.istekler]
        assert t[n1] - t[n1 - 1] >= 7.0 - 1e-6, t[n1] - t[n1 - 1]
        assert all(b - a >= 2.0 - 1e-9 for a, b in zip(t, t[1:]))
    finally:
        srv.kapat()


@sina('I13 iş sonu tahmini gözlenen bayt/gün ile (Ö2): sığmayacak istek başlatılmaz, sığan başlatılır')
def i13(KAR):
    for sure, beklenen in ((1450, 0), (1600, 1)):   # ilk iş 19 gün: tahmin 19 × 7,5 MB / 125 kB/s + 60 = 1200 sn; × 1,25 = 1500
        depo = tt.temiz(os.path.join(KAR, f'i13_{sure}')); S = tt.saat_tak()
        with open(IN.durum_yollari(depo)['gunluk'], 'w') as f:       # önceki işlerin 20 başarılı isteği (plan dışı anahtarlar)
            for i in range(20):
                f.write(json.dumps(dict(k=f'KO.ZZ|2000-{i:02d}', kod=200, bayt=150_000_000, gun=20, sn=1200.0, sure_kesti=False)) + '\n')
        srv = tt.Sunucu('kisa', {}, S)
        try:
            G = tt.yapay_G(['KO.A01'], [2017])
            IN.indir(None, depo, os.path.join(KAR, 'i13_yerel'), sure, taban=srv.url, G=G)
            assert min(len(srv.istekler), 1) == beklenen, (sure, len(srv.istekler))
        finally:
            srv.kapat()


# ================================================================ tek koşu ve kalıp
@sina('I14 var olan hüküm olc ile yeniden hesaplanmaz; Δ dosyası yazılmaz')
def i14(KAR):
    on = dict(hukum='veri yok (gün doluluğu)', metin='veri yok (gün doluluğu). önceki')
    H, depo, _ = kos(KAR, 'i14', IST12, (2017, 2020, 2021), dict(delta=lambda i, w: Z[i] * 5e-4), hukum_on=on)
    assert H == on, H
    assert not os.path.exists(os.path.join(depo, 'kosu', 'olcum_delta.json'))
    assert '1b' not in json.load(open(os.path.join(depo, 'kosu', 'kosu_durum.json'))).get('asamalar', {}) if os.path.exists(
        os.path.join(depo, 'kosu', 'kosu_durum.json')) else True


@sina('I15 Kalıp T sayıları: %80 değişimi = q95 + 0,84 · σ̂_Δ; kesik olmayan koşuda "kesik" yazılmaz')
def i15(KAR):
    H, _, _ = kos(KAR, 'i15', IST12, (2017, 2020, 2021), dict(delta=lambda i, w: Z[i] * 5e-4))
    t = H['taban']
    m = re.search(r'≈ q95 \+ 0,84 · σ̂_Δ = (\S+) %', H['metin'])
    assert m and m.group(1) == K.yz(t['q95'] + 0.84 * t['sigma']), (m and m.group(1))
    assert f"q95 = {K.yz(t['q95'])} %'dir" in H['metin'] and f"σ̂_Δ = {K.yz(t['sigma'])} %" in H['metin']
    assert 'Marmara KO ağında kademe C, 36 yer-penceresinde' in H['metin'] and 'kesik' not in H['metin']


@sina('I16 "kesildi" kalıcı: sonraki çağrı istek atmaz ve kesme anını (takvim süresi) değiştirmez')
def i16(KAR):
    depo = tt.temiz(os.path.join(KAR, 'i16')); S = tt.saat_tak(); srv = tt.Sunucu('kisa', {}, S)
    try:
        G = tt.yapay_G(['KO.A01'], [2017])
        IN.yaz_json(IN.durum_yollari(depo)['butce'], dict(durum='baslamadi', ilk_istek=S.t - 42 * 86400 + 30, etkin_sn=0.0, isler=[], tur=False))
        B1 = IN.indir(None, depo, os.path.join(KAR, 'i16_yerel'), 6000, taban=srv.url, G=G)
        assert B1['durum'] == 'kesildi'; b1 = json.load(open(IN.durum_yollari(depo)['butce'])); n1 = len(srv.istekler)
        S.t += 86400
        IN.indir(None, depo, os.path.join(KAR, 'i16_yerel'), 6000, taban=srv.url, G=G)
        b2 = json.load(open(IN.durum_yollari(depo)['butce']))
        assert len(srv.istekler) == n1 and b2 == b1, (b1.get('bitis'), b2.get('bitis'), len(b1['isler']), len(b2['isler']))
    finally:
        srv.kapat()


HEPSI = [i01, i02, i03, i04, i05, i06, i07, i08, i09, i10, i11, i12, i13, i14, i15, i16]

# ================================================================ mutantlar (yazarın M01–M18'inden bağımsız)
MUT = [
    ('N01 kesik: T 2021 D kümesinden düşer', 'tr4_kosu.py', 'any(D_YIL[0] <= y <= D_YIL[1] for y in eksik_T)', 'any(D_YIL[0] <= y < D_YIL[1] for y in eksik_T)'),
    ('N02 kesik: tamamlanan T ile kapı sınanmaz', 'tr4_kosu.py', ' or not kapi(yT):', ':'),
    ('N03 bilgi 0: n ≥ 31', 'tr4_kosu.py', 'BILGI0_N, BILGI0_YER = 30, 6', 'BILGI0_N, BILGI0_YER = 31, 6'),
    ('N04 bilgi 0: yer ≥ 7', 'tr4_kosu.py', 'BILGI0_N, BILGI0_YER = 30, 6', 'BILGI0_N, BILGI0_YER = 30, 7'),
    ('N05 (ii-a) üst sınır 1,30', 'tr4_kosu.py', 'ORAN_ARALIK = (0.80, 1.20)', 'ORAN_ARALIK = (0.80, 1.30)'),
    ('N06 hüküm önyüklemesi başka tohumla', 'tr4_kosu.py', '        t = taban(rows)\n        hukum = c_hukmu(t)', "        t = taban(rows, 'tr4-hukum|20261203')\n        hukum = c_hukmu(t)"),
    ('N07 enerji medyanı pencere dışı saatlerle', 'tr4_kosu.py', 'for d in gunler if a <= d <= b and d.toordinal() in veri]', 'for d in gunler if d.toordinal() in veri]'),
    ('N08 1b: maskeli gün dolu sayılır', 'tr4_kosu.py', 'gun_dolu(V[d.toordinal()][2]) and d not in M for d in gl]', 'gun_dolu(V[d.toordinal()][2]) for d in gl]'),
    ('N09 M5 maskesi 59 gün', 'tr4_kosu.py', 'M5_GUN = 60', 'M5_GUN = 59'),
    ('N10 tur eşiği ≥ %5', 'tr4_indir.py', 'len(bas) / len(isler) > TUR_ESIK', 'len(bas) / len(isler) >= TUR_ESIK'),
    ('N11 aynı işte yeniden deneme', 'tr4_indir.py', "Q = [x for x in Qt if x['k'] not in bu_is_hata]", 'Q = list(Qt)'),
    ('N12 akış durumu işler arasında taşınmaz', 'tr4_indir.py', "akis = Akis(B.get('akis'))", 'akis = Akis()'),
    ('N13 ardışık hata durdurması yok', 'tr4_indir.py', 'if not Q or ardisik >= ARDISIK_HATA_MAX:', 'if not Q:'),
    ('N14 iş sonu tahmini 1,3 bayt/örnek formülüyle', 'tr4_indir.py', "bayt_gun = sum(r['bayt'] for r in ok) / sum(r['gun'] for r in ok) if ok else", 'bayt_gun ='),
    ('N15 olc var olan hükmü yeniden hesaplar', 'tr4_kosu.py', "    if os.path.exists(os.path.join(depo, 'kosu', 'hukum.json')):\n        H = json", "    if False:\n        H = json"),
    ('N16 Kalıp T: %80 için q95 + 1,0 σ̂', 'tr4_kosu.py', "k95 = t['q95'] + 0.84 * t['sigma']", "k95 = t['q95'] + 1.0 * t['sigma']"),
    ('N17 karşılanmadı U ile', 'tr4_kosu.py', "if t['sigma_L'] > ESIK_KARSILANMADI", "if t['sigma_U'] > ESIK_KARSILANMADI"),
    ('N18 bilgi 13 körlük sınırı 2025-06-30', 'tr4_indir.py', 'SON_B13 = dt.date(2025, 5, 31)', 'SON_B13 = dt.date(2025, 6, 30)'),
    ('N19 körlük sınırı role bakmaz', 'tr4_indir.py', "sinir = SON_HUKUM if rol == 'ana' else SON_B13", 'sinir = SON_B13'),
    ('N20 bütçe: süren iş sayılmaz', 'tr4_indir.py', "etkin = B['etkin_sn'] + (simdi() - is_bas)", "etkin = B['etkin_sn']"),
    ('N21 "kesildi" kalıcı değil', 'tr4_indir.py', "if B['durum'] in ('bitti', 'kesildi'):\n        print", "if B['durum'] == 'bitti':\n        print"),
    ('N22 kesik gövde kesin sayılır', 'tr4_indir.py', 'n < int(cl): kod', 'n < 0: kod'),
    ('N23 sürdürme: zorla kesilen işin süresi kaybolur', 'tr4_indir.py', "B['etkin_sn'] += max(0.0, j['son'] - j['bas'])", "B['etkin_sn'] += 0.0"),
]


def bir_mutant(KAR, npz, m):
    ad, dosya, eski, yeni = m
    md = tt.temiz(os.path.join(KAR, 'nmut', ad.split()[0]))
    tr4 = os.path.join(md, 'tr4'); tr5 = os.path.join(md, 'tr5'); os.makedirs(tr4); os.makedirs(tr5); os.makedirs(os.path.join(tr4, 'inc_kod'))
    for f in ('tr4_indir.py', 'tr4_kosu.py', 'tr4_test_yapay.py', 'tr4_yapay_ref.json', 'tr4_pencereler.csv',
              'tr4_onkayit_sayim.json', 'tr4_guc_sonuc.json'):
        shutil.copy(os.path.join(KOD, f), tr4)
    shutil.copy(os.path.abspath(__file__), os.path.join(tr4, 'inc_kod'))
    for f in ('tr5b_yapay.py', 'tr5b_yapay2.py', 'tr5b_yapay_ccf_ref.json'):
        shutil.copy(os.path.join(os.path.dirname(KOD), 'tr5', f), tr5)
    y = os.path.join(tr4, dosya); s = open(y, encoding='utf-8').read()
    assert s.count(eski) == 1, (ad, s.count(eski)); open(y, 'w', encoding='utf-8').write(s.replace(eski, yeni))
    env = dict(os.environ, OMP_NUM_THREADS='1')
    out = {}
    for suite, yol in (('yazar', os.path.join(tr4, 'tr4_test_yapay.py')), ('inceleme', os.path.join(tr4, 'inc_kod', os.path.basename(__file__)))):
        args = [sys.executable, '-I', '-B', yol, os.path.join(md, 'k_' + suite), npz, '--kod', tr4] + (['--hizli'] if suite == 'yazar' else [])
        try:
            p = subprocess.run(args, capture_output=True, text=True, timeout=1500, env=env)
            kal = [l for l in p.stdout.splitlines() if l.startswith('KALDI')]
            out[suite] = dict(yakaladi=p.returncode != 0, kalan=[l[:160] for l in kal[:3]])
        except subprocess.TimeoutExpired:
            out[suite] = dict(yakaladi=True, kalan=['zaman aşımı (1500 sn)'])
    shutil.rmtree(md, ignore_errors=True)
    yak = out['yazar']['yakaladi'] or out['inceleme']['yakaladi']
    print(f"{'YAKALANDI' if yak else 'KAÇTI    '} {ad}: yazar {'+' if out['yazar']['yakaladi'] else '-'} / inceleme "
          f"{'+' if out['inceleme']['yakaladi'] else '-'} {out['inceleme']['kalan'][:1] or out['yazar']['kalan'][:1]}", flush=True)
    return dict(ad=ad, yakalandi=yak, **out)


if __name__ == '__main__':
    a = [x for i, x in enumerate(sys.argv[1:], 1) if not x.startswith('--') and sys.argv[i - 1] != '--kod']
    KAR, npz = a[0], a[1]
    os.makedirs(KAR, exist_ok=True); t0 = time.time()
    for f in HEPSI: f(KAR)
    n_ok = sum(1 for x in SONUC if x[1])
    print(f'İNCELEME SINAMASI: {n_ok} / {len(SONUC)} geçti ({time.time() - t0:.0f} sn)', flush=True)
    rapor = dict(sinama=[dict(ad=x[0], gecti=x[1], hata=x[2]) for x in SONUC])
    if '--mutasyon' in sys.argv:
        sec = [x.split('=', 1)[1].split(',') for x in sys.argv if x.startswith('--yalniz=')]
        M = [m for m in MUT if not sec or m[0].split()[0] in sec[0]]
        with ThreadPoolExecutor(3) as ex: R = list(ex.map(lambda m: bir_mutant(KAR, npz, m), M))
        rapor['mutasyon'] = R
        print(f"MUTASYON: {sum(1 for r in R if r['yakalandi'])} / {len(R)} yakalandı; yazarın sınamaları "
              f"{sum(1 for r in R if r['yazar']['yakaladi'])}, inceleme sınamaları {sum(1 for r in R if r['inceleme']['yakaladi'])}", flush=True)
    if '--kod' not in sys.argv: IN.yaz_json(os.path.join(KAR, 'tr4_inc_kod_sinama_sonuc.json'), rapor)
    sys.exit(0 if n_ok == len(SONUC) else 1)
