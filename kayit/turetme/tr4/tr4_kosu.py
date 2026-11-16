#!/usr/bin/env python3
"""TR-4 KOŞU: 1b gün doluluğu, kod denetimleri (i) ve (ii-a), ε geçerliliği, taban (σ̂_Δ, q95, iki yönlü önyükleme),
kapalı hüküm listesi ve bilgi satırları 0–14.

Ön kayıt: `kayit/onkayit/TR-4_marmara-hiz-tabani_ONKAYIT.md` DONDURULDU sürüm 2 + Ek 1 (§3, §4, §5.3, §5.5, §8);
öncelik: ön kayıt > `TR-4_INCELEME-1.md` > TR-5b sürüm 3 §3. Okumalar: `kayit/onkayit/TR-4_KODLAYICI-OKUMALARI.md`.
Zincir TR-5b §3.1–3.6'dır; başvuru işlevleri (`zincir`, `germe_olc`, `ay_esle`, `ger`; bilgi satırı 13–14 için
`tr5b_yapay2.germe_pk`) `kayit/turetme/tr5/` altındaki dondurulmuş dosyalardan DEĞİŞTİRİLMEDEN içe aktarılır
(sha256 denetimli). Saatlik ön işlem ve ÇİF `tr4_indir.py`'dedir.

TEK KOŞU VE KÖRLÜK:
  - İndirme bitmeden ("bitti") ya da bütçeyle kesilmeden ("kesildi") hiçbir ε ya da Δ hesaplanmaz: `olc` kipi
    `indirme_durum.json`'u okur ve başka durumda durur (§5.5). Yalnız kod denetimi (i) (yapay npz) ondan önce koşabilir.
  - Her aşamanın sonucu `<depo>/kosu/kosu_durum.json`'a yazılır; hüküm `hukum.json`'a bir kez yazılır. Var olan hüküm
    farklı bir sonuçla yeniden yazılamaz (§5.6, §11: "taban ölçüldü" tek koşudur).
  - Ölçüm dosyasının sha256'sı `kosu_gunlugu.jsonl`'a geçer (§4.3 adım 5).

Kipler:
  denetim_i <ob> <depo> <npz>     kod denetimi (i) (§4.3 adım 2); ağsız, yalnız yapay npz.
  olc       <ob> <depo> <npz>     bütün sıra: adım 0 (bütçe) → 1b → (i) → (ii-a) → ε → taban → bilgi satırları.
  durum     <ob> <depo>           durum dosyasını yazdırır.
"""
import collections, datetime as dt, hashlib, importlib.util, json, math, os, sys, time

import numpy as np

BURASI = os.path.dirname(os.path.abspath(__file__))
TR5 = os.path.join(os.path.dirname(BURASI), 'tr5')
TD = dt.timedelta


def _yukle(ad, yol):
    sp = importlib.util.spec_from_file_location(ad, yol); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return m


IN = _yukle('tr4_indir', os.path.join(BURASI, 'tr4_indir.py'))

# ---------------------------------------------------------------- dondurulmuş sabitler
SHA = {   # girdi dosyaları (ön kayıt §4.3 adım 2; Ek; tr5b sürüm 3)
    'tr5b_yapay.py': '70e8fbaba4b01753798b03976d261101cef30e7d9ea44dcf874b443de7b6c024',
    'tr5b_yapay2.py': '785690b0fbe7d6cb758c62607c603b448afa65167c5b1a282053e1a374822fbf',
    'tr5b_yapay_ccf_ref.json': '36339a46ac3ac75423573852ec5e0677a425d1da951e732dee52123a02580e5c',
    'tr4_yapay_ref.json': '238b6e09289db01819bb9ea1719fc8f964476d4653a5ab9557970ea14e0717b5',
    'tr5b_yapay_ccf.npz': '44189a31d1642e273186bfebc5c6625c62be26bf9cf090a79334da6e46a1cb29',
    'tr4_pencereler.csv': '166e42ea5b2fbe97ed608daf0f533252c13ef0959d78950c9b3213998915a4ef',
    'tr4_onkayit_sayim.json': '39e91fcecb2b6c9554a7f9d79569b1b81fc20427a72ca207244a85b5151cb2ee',
    'tr4_guc_sonuc.json': 'ed81dfd06660a1c2e986988e7f8e57ba884179fb4b91a0a39e04db90f6e31ee2',
}
YOL = {'tr5b_yapay.py': os.path.join(TR5, 'tr5b_yapay.py'), 'tr5b_yapay2.py': os.path.join(TR5, 'tr5b_yapay2.py'),
       'tr5b_yapay_ccf_ref.json': os.path.join(TR5, 'tr5b_yapay_ccf_ref.json'),
       'tr4_yapay_ref.json': os.path.join(BURASI, 'tr4_yapay_ref.json'),
       'tr4_pencereler.csv': os.path.join(BURASI, 'tr4_pencereler.csv'),
       'tr4_onkayit_sayim.json': os.path.join(BURASI, 'tr4_onkayit_sayim.json'),
       'tr4_guc_sonuc.json': os.path.join(BURASI, 'tr4_guc_sonuc.json')}


def sha_denet(ad, yol=None):
    s = IN.sha_dosya(yol or YOL[ad])
    if s != SHA[ad]: raise SystemExit(f'girdi sha256 uyuşmuyor: {ad} {s}; durdu')
    return s


sha_denet('tr5b_yapay.py'); sha_denet('tr5b_yapay2.py')
YP2 = _yukle('tr5b_yapay2', YOL['tr5b_yapay2.py'])                 # tr5b_yapay'ı kendi dizininden yükler
YP = YP2.YP

KAPI_YER, KAPI_ARA = 10, 3
ANA_YIL = list(range(2017, 2025))
D_YIL = (2017, 2021)                                                # §5.3: kesik koşunun en küçük kümesi
TABAN_GUN, KORUMA = 1095, 7
DOLU_GUN_SAAT = 2                                                   # TR-5b §5 1b: 4 saatin ≥ 2'si üç bileşende kabul
DOLU_DILIM_ORAN = 0.60
ENERJI_KAT = 3.0
SAAT_MIN = 2                                                        # §3.3: günlük ÇİF ≥ 2 saat
EKLEME = -1e-3                                                      # (ii-a): −%0,1
ORAN_ARALIK = (0.80, 1.20)
TOL_DELTA, TOL_ORAN = 0.0005, 0.005                                  # % ve oran
B_ONYUKLEME = 2000
TOHUM_HUKUM = 'tr4-hukum|20261202'
ESIK_KARSILANDI, ESIK_KARSILANMADI = 0.20, 0.245                    # % (§4.3 adım 5; İ1-Ö1)
BILGI0_N, BILGI0_YER = 30, 6
M5_GUN = 60
OLAY_2019 = ('us70005lkl', dt.date(2019, 9, 26), ('KO.SLVT', 'KO.CRLT', 'KO.CTKS'))
MPA_DUYARLILIK = 0.5                                                # Hillers 2014, MPa^-1 (yalnız mertebe)
HUKUM_ADLARI = ('veri yok (aşama 0)', 'veri yok (aktarım hızı)', 'veri yok (indirme bütçesi)',
                'veri yok (gün doluluğu)', 'geçersiz (kod)', 'veri yok (ε geçerliliği)',
                'taban ölçüldü; TR-5b (c) karşılandı', 'taban ölçüldü; TR-5b (c) karşılanmadı',
                'taban ölçüldü; TR-5b (c) belirsiz')


# ---------------------------------------------------------------- biçim
def yz(x, h=3):
    """Yüzde sayısını Türkçe ondalıkla yazar (eksi işareti U+2212)."""
    if x is None or (isinstance(x, float) and math.isnan(x)): return 'hesaplanamadı'
    s = f'{x:.{h}f}'.replace('.', ',')
    return s.replace('-', '−')


def kapi(sayi):
    iyi = sorted(y for y, n in sayi.items() if n >= KAPI_YER)
    return any(b - a >= KAPI_ARA for i, a in enumerate(iyi) for b in iyi[i + 1:])


def yer_T(W):
    return {y: len({w['yer'] for w in W if w['T'].year == y}) for y in ANA_YIL}


def t_metin(s):
    return ', '.join(f'{y}: {s[y]}' for y in ANA_YIL)


# ---------------------------------------------------------------- M5 maskesi (TR-5b §2.6; csv'den)
def maske_gunleri(G):
    """yer-penceresi anahtarı -> maskeli gün kümesi (yerel güneş tarihi d). Olay tarihleri sayım json'undan; gün
    sayısı csv'deki maske_gun ile denetlenir."""
    sha_denet('tr4_pencereler.csv', G.get('csv_yol')); sha_denet('tr4_onkayit_sayim.json', G.get('sayim_yol'))
    S = json.load(open(G.get('sayim_yol') or YOL['tr4_onkayit_sayim.json'], encoding='utf-8'))
    C = IN.csv_oku(G.get('csv_yol'))
    out = {}
    for w in G['W']:
        r = C[w['k']]; g = set()
        for e in [x for x in r['maske_olay'].split(';') if x]:
            t = dt.date.fromisoformat(S['olay_uzaklik'][e]['t'][:10])
            for i in range(M5_GUN):
                d = t + TD(days=i)
                if w['a'] <= d <= w['b']: g.add(d)
        if len(g) != int(r['maske_gun']): raise SystemExit(f"{w['k']}: maske günü {len(g)} != csv {r['maske_gun']}; durdu")
        out[w['k']] = g
    return out


# ---------------------------------------------------------------- saatlik ÇİF deposundan okuma
def istasyon_yukle(depo, ist, gunluk_satir, rol='ana', bant='ccf'):
    """İstasyonun bütün istasyon-ay ÇİF dosyaları: ordinal -> (ccf (4,3,2401) float32, rms (4,3), tamlik (4,3))."""
    out = {}
    for k, x in gunluk_satir.items():
        if not k.startswith(ist + '|') or x.get('rol', 'ana') != rol or not x.get('cif'): continue
        d = IN.cif_oku(os.path.join(depo, 'cif', x['cif']), x.get('cif_sha256'))
        for i, o in enumerate(d['gun']):
            out[int(o)] = (d[bant][i], d['rms'][i], d['tamlik'][i])
    return out


def gun_dolu(tam):
    """§3.2 madde 1 + TR-5b §5 1b: gün dolu ⇔ 4 saatin ≥ 2'sinde üç bileşenin tamlığı ≥ %99."""
    return int(np.sum(np.all(tam >= IN.KABUL_TAMLIK, axis=1))) >= DOLU_GUN_SAAT


def pencere_gunleri(T):
    return [T + TD(days=i) for i in range(-TABAN_GUN, 0)]


def gunluk_cif(veri, gunler, maske, ref_aralik):
    """TR-5b §3.2 madde 4 ve §3.3: enerji reddi (medyan: ref_aralik içindeki bütün saatlerin bileşen RMS'i), günlük
    ÇİF = kabul edilen saatlerin ortalaması (≥ 2 saat), maskeli gün geçersiz.
    Dönen: ccf (3 çift, n gün, 2401) float64, gec (3, n) bool, red oranı."""
    n = len(gunler); nl = 2 * IN.NLAG + 1
    a, b = ref_aralik
    R = [veri[d.toordinal()][1] for d in gunler if a <= d <= b and d.toordinal() in veri]
    med = np.nanmedian(np.concatenate([r[None] for r in R], 0).reshape(-1, 3), axis=0) if R else np.full(3, np.nan)
    ccf = np.zeros((3, n, nl)); gec = np.zeros((3, n), bool); toplam = red = 0
    for i, d in enumerate(gunler):
        v = veri.get(d.toordinal())
        if v is None: continue
        c, rms, _ = v
        tam_saat = ~np.isnan(c[:, 0, 0])                            # üç bileşen tamlığı geçen saatler
        enerji_ok = ~np.any(rms > ENERJI_KAT * med[None, :], axis=1)
        kab = tam_saat & enerji_ok
        toplam += int(tam_saat.sum()); red += int((tam_saat & ~enerji_ok).sum())
        if d in maske: continue
        for j in range(3):
            kj = kab & ~np.isnan(c[:, j, 0])
            if kj.sum() >= SAAT_MIN:
                ccf[j, i] = c[kj, j].astype(np.float64).mean(axis=0); gec[j, i] = True
    return ccf, gec, (red / toplam if toplam else float('nan'))


# ---------------------------------------------------------------- zincir sarmalayıcıları (TR-5b başvuru işlevleri)
def eps_seri(ccf, gec, gun):
    """Bir çiftin günlük ÇİF'lerinden yığın-sonu ε dizisi (tr5b_yapay.zincir; başvuru [T−1095, T−8])."""
    pen = (gun >= -TABAN_GUN) & (gun <= -(KORUMA + 1))
    if not (pen & gec).any(): return np.full(len(gun), np.nan)
    return YP.zincir(ccf, gec, gun, 0)


def delta_cift(ccf, gec, gun, ay):
    return YP.ay_esle(eps_seri(ccf, gec, gun), gun, ay)


def ekle(ccf, gun, eps=EKLEME):
    """(ii-a): C dilimi [T − 365, T − 8] günlük ÇİF'lerine germe: R(τ) → R(τ(1 + eps)) (eps = −0,001)."""
    out = ccf.copy()
    for i in np.flatnonzero((gun >= -365) & (gun <= -(KORUMA + 1))): out[i] = YP.ger(ccf[i], eps)
    return out


def kademe_maskesi(tarihler, kademe):
    return np.array([kademe == 'A' or d.day <= IN.C_GUN for d in tarihler])


def istasyon_delta(dl):
    """TR-5b §3.6: istasyon Δ = geçerli çiftlerin medyanı (≥ 2 çift)."""
    v = [x for x in dl if not np.isnan(x)]
    return float(np.median(v)) if len(v) >= 2 else float('nan')


# ---------------------------------------------------------------- kod denetimi (i)
def denetim_i(npz, kademe, durum_yaz=None):
    """§4.3 adım 2: (a) TR-5b başvurusu; (b) kademe C ise tr4_yapay_ref.json (ayın 1–20. günleri maskesi)."""
    t0 = time.time()
    sha_denet('tr5b_yapay_ccf.npz', npz); sha_denet('tr5b_yapay_ccf_ref.json'); sha_denet('tr4_yapay_ref.json')
    r5 = json.load(open(YOL['tr5b_yapay_ccf_ref.json'], encoding='utf-8'))
    r4 = json.load(open(YOL['tr4_yapay_ref.json'], encoding='utf-8'))['tasarim']['C_20g_4s']['seriler']
    z = np.load(npz); gun = z['gunler'].astype(int)
    z = dict(ccf=z['ccf'], ccf_eklenmis=z['ccf_eklenmis'], gecerli=z['gecerli'], ay=z['ay'])   # bir kez oku
    sap = []; enb = dict(delta=0.0, oran=0.0)

    def kars(ad, i, D0, D2, ref):
        o = (D2 - D0) / EKLEME if not (np.isnan(D0) or np.isnan(D2)) else float('nan')
        rv = [ref['delta_yuzde'], ref['oran']]
        if rv[0] is None or np.isnan(D0) or rv[1] is None or np.isnan(o):
            if (rv[0] is None) != bool(np.isnan(D0)) or (rv[1] is None) != bool(np.isnan(o)): sap.append(f'{ad}:{i}:geçerlilik')
            return
        dd = abs(D0 * 100 - rv[0]); do = abs(o - rv[1])
        enb['delta'] = max(enb['delta'], dd); enb['oran'] = max(enb['oran'], do)
        if dd > TOL_DELTA or do > TOL_ORAN: sap.append(f'{ad}:{i}')

    for i, s in enumerate(r5['seriler']):
        ay = z['ay'][i].astype(int); gec = z['gecerli'][i]
        a16, b16 = z['ccf'][i].astype(np.float64), z['ccf_eklenmis'][i].astype(np.float64)
        kars('a', i, delta_cift(a16, gec, gun, ay), delta_cift(b16, gec, gun, ay), s)
        if kademe == 'C':
            tar = [dt.date.fromordinal(s['T_ord'] + int(g)) for g in gun]
            gc = gec & kademe_maskesi(tar, 'C')
            kars('b', i, delta_cift(a16, gc, gun, ay), delta_cift(b16, gc, gun, ay), r4[i])
    return dict(sapan=len(sap), sapan_liste=sap, en_buyuk_fark_delta_yuzde=enb['delta'], en_buyuk_fark_oran=enb['oran'],
                b_koşuldu=kademe == 'C', sure_sn=round(time.time() - t0, 1))


# ---------------------------------------------------------------- önyükleme ve kestiriciler
def kestir(v):
    v = np.asarray(v, float)
    return 1.4826 * float(np.median(np.abs(v - np.median(v)))), float(np.quantile(np.abs(v), 0.95))


def tohum(metin):
    return int(hashlib.sha256(metin.encode()).hexdigest()[:8], 16)


def onyukleme(yer, yil, v, metin=TOHUM_HUKUM, B=B_ONYUKLEME):
    """§4.2: iki yönlü (yer × T); hücre ağırlığı iki çokluğun çarpımı; σ̂ için %5–95, q95 için %2,5–97,5."""
    rng = np.random.default_rng(tohum(metin))
    S = sorted(set(yer)); Y = sorted(set(yil))
    si = np.array([S.index(s) for s in yer]); yi = np.array([Y.index(y) for y in yil])
    ms = rng.multinomial(len(S), np.ones(len(S)) / len(S), size=B)
    my = rng.multinomial(len(Y), np.ones(len(Y)) / len(Y), size=B)
    w = ms[:, si] * my[:, yi]
    sig = np.full(B, np.nan); q = np.full(B, np.nan); v = np.asarray(v, float)
    for b in range(B):
        x = np.repeat(v, w[b])
        if len(x) >= 5: sig[b], q[b] = kestir(x)
    return [float(x) for x in np.nanquantile(sig, [0.05, 0.95])], [float(x) for x in np.nanquantile(q, [0.025, 0.975])]


def taban(rows, metin=TOHUM_HUKUM):
    """rows: [(yer, T yılı, Δ (oran, yüzde değil))]. Yüzde birimiyle döner."""
    v = np.array([r[2] for r in rows]) * 100
    s, q = kestir(v)
    si, qi = onyukleme([r[0] for r in rows], [r[1] for r in rows], v, metin)
    return dict(n=len(rows), yer=len({r[0] for r in rows}), T=sorted({r[1] for r in rows}), sigma=s, sigma_L=si[0],
                sigma_U=si[1], q95=q, q95_L=qi[0], q95_U=qi[1])


def c_hukmu(t):
    if t['sigma_U'] < ESIK_KARSILANDI: return 'taban ölçüldü; TR-5b (c) karşılandı'
    if t['sigma_L'] > ESIK_KARSILANMADI: return 'taban ölçüldü; TR-5b (c) karşılanmadı'
    return 'taban ölçüldü; TR-5b (c) belirsiz'


def bilgi0_metin(rows, hukum):
    yer = len({r[0] for r in rows})
    if len(rows) < BILGI0_N or yer < BILGI0_YER:
        return f'bilgi satırı 0: hesaplanmadı (n = {len(rows)}, yer = {yer})', None
    t = taban(rows)
    m = (f"bilgi satırı 0: σ̂_Δ {yz(t['sigma'])} % ({yz(t['sigma_L'])}–{yz(t['sigma_U'])}), q95 {yz(t['q95'])} % "
         f"({yz(t['q95_L'])}–{yz(t['q95_U'])}), n {t['n']}, yer {t['yer']}, T {', '.join(map(str, t['T']))}")
    t['ek'] = f'Kapı altı; TR-5b (c) için dayanak değildir; hüküm {hukum}.'
    return m, t


def kalip_T(t, kademe_metni, b11, b14):
    k95 = t['q95'] + 0.84 * t['sigma']
    return (f"Marmara KO ağında {kademe_metni}, {t['n']} yer-penceresinde ({t['yer']} yer, T {t['T'][0]}–{t['T'][-1]}), "
            f"olaysız pencerelerde tek istasyonun bir yıllık dv/v düzey değişiminin (0,5–2 Hz, TR-5b ölçüsü) örneklem %95 "
            f"niceliği q95 = {yz(t['q95'])} %'dir (%95 iki yönlü önyükleme aralığı {yz(t['q95_L'])}–{yz(t['q95_U'])}; "
            f"benzetimde bu aralık gerçek değeri 0,79–0,97 olasılıkla kapsar). σ̂_Δ = {yz(t['sigma'])} % (%90 iki yönlü "
            f"önyükleme aralığı {yz(t['sigma_L'])}–{yz(t['sigma_U'])}). q95, tek istasyonda %5 yanlış alarm oranındaki "
            f"saptama eşiğidir. Bu büyüklükte bir düzey değişimi yaklaşık yarı yarıya saptanır. %80 olasılıkla saptanacak "
            f"değişim, normal yaklaşımla, ≈ q95 + 0,84 · σ̂_Δ = {yz(k95)} %'dir. Bu bir olasılık ya da alarm eşiği değildir. "
            f"Ölçü istasyon çevresindeki sığ ortamı örnekler. Zincir bu ön kayıtta Marmara'da gerçek bir hız değişimiyle "
            f"sınanmadı; mevsimsel genliğin yer medyanı (bilgi satırı 11) {yz(b11)} %, 2019 Silivri δ_ko'su (bilgi satırı "
            f"14) {b14}.")


# ---------------------------------------------------------------- durum dosyası
class Durum:
    def __init__(self, depo):
        self.dir = os.path.join(depo, 'kosu'); os.makedirs(self.dir, exist_ok=True)
        self.yol = os.path.join(self.dir, 'kosu_durum.json')
        self.d = json.load(open(self.yol, encoding='utf-8')) if os.path.exists(self.yol) else dict(asamalar={})

    def yaz(self, asama, **kw):
        self.d['asamalar'][asama] = dict(kw, t=round(time.time(), 1))
        IN.yaz_json(self.yol, self.d)
        with IN.ekle_ac(os.path.join(self.dir, 'kosu_gunlugu.jsonl')) as g:
            g.write(json.dumps(dict(asama=asama, t=round(time.time(), 1), ozet={k: v for k, v in kw.items()
                                                                                 if not isinstance(v, (list, dict))}),
                               ensure_ascii=False, sort_keys=True, default=str) + '\n')


# ---------------------------------------------------------------- 1b
def b1_hesapla(W, depo, satir, maske, kademe):
    """TR-5b §5 1b tanımı: A, B, C dilimlerinin her birinde dolu gün oranı ≥ 0,60 (payda: dilimin maskesiz ve
    örneklemdeki günleri), ≥ 9 takvim ayında hem C'de hem A∪B'de ≥ 10 gün için yığın şartı (son 10 günde ≥ 5 dolu ve
    maskesiz gün). Yalnız tamlık okunur; ε hesaplanmaz."""
    out = {}
    for ist in sorted({w['ist'] for w in W}):
        V = istasyon_yukle(depo, ist, satir)
        for w in [x for x in W if x['ist'] == ist]:
            T = w['T']; gl = pencere_gunleri(T); M = maske[w['k']]
            dolu = np.array([d.toordinal() in V and gun_dolu(V[d.toordinal()][2]) and d not in M for d in gl])
            ornek = np.array([w['a'] <= d <= w['b'] and d not in M and (kademe == 'A' or d.day <= IN.C_GUN) for d in gl])
            gg = np.array([(d - T).days for d in gl])
            dil = [(-1095, -731), (-730, -366), (-365, -8)]
            oran = [float(dolu[(gg >= a) & (gg <= b)].sum() / max(1, ornek[(gg >= a) & (gg <= b)].sum())) for a, b in dil]
            cs = np.concatenate([[0], np.cumsum(dolu)])
            yig = np.array([cs[i + 1] - cs[max(0, i - 9)] >= YP.YIGIN_MIN for i in range(len(gl))])
            ay = np.array([d.month for d in gl]); Cm = (gg >= -365) & (gg <= -8); ABm = (gg >= -1095) & (gg <= -366)
            n_ay = sum(1 for m in range(1, 13) if (yig & Cm & (ay == m)).sum() >= YP.AY_MIN_GUN and (yig & ABm & (ay == m)).sum() >= YP.AY_MIN_GUN)
            out[w['k']] = dict(dolu=all(o >= DOLU_DILIM_ORAN for o in oran) and n_ay >= YP.AY_MIN,
                               oran=[round(o, 3) for o in oran], yigin_ay=n_ay)
        del V
    return out


# ---------------------------------------------------------------- Δ hesabı (ii-a dahil)
def pencere_hesapla(w, V, M, kademe, ekli=True, bant_ccf=None, alt_c=False):
    """Bir yer-penceresinin çift Δ'ları; ekli=True ise (ii-a) için −%0,1 eklenmiş Δ'lar da. alt_c: kademe A'da C alt
    kümesi (bilgi satırı 9)."""
    T = w['T']; gl = pencere_gunleri(T)
    gun = np.array([(d - T).days for d in gl]); ay = np.array([d.month for d in gl])
    ccf, gec, red = gunluk_cif(bant_ccf if bant_ccf is not None else V, gl, M, (w['a'], w['b']))
    if alt_c: gec = gec & kademe_maskesi(gl, 'C')[None, :]
    D, De, eps_ay, Dtr = [], [], [], []
    for j in range(3):
        e = eps_seri(ccf[j], gec[j], gun)
        D.append(YP.ay_esle(e, gun, ay))
        eps_ay.append([float(np.nanmean(e[(ay == m) & ~np.isnan(e)])) if np.any((ay == m) & ~np.isnan(e)) else float('nan')
                       for m in range(1, 13)])
        De.append(delta_cift(ekle(ccf[j], gun), gec[j], gun, ay) if ekli else float('nan'))
        # eğilimden arındırılmış Δ (bilgi satırı 10): A∪B'ye doğrusal eğilim, bütün ε'dan çıkarılır
        ab = (gun <= -366) & ~np.isnan(e)
        if ekli and ab.sum() >= 2:
            p = np.polyfit(gun[ab], e[ab], 1); Dtr.append(YP.ay_esle(e - np.polyval(p, gun), gun, ay))
        else: Dtr.append(float('nan'))
    return dict(cift=D, cift_ekli=De, delta=istasyon_delta(D), delta_ekli=istasyon_delta(De),
                delta_egilimsiz=istasyon_delta(Dtr), gecerli_cift=int(sum(1 for x in D if not np.isnan(x))),
                saat_red=red, eps_ay=eps_ay)


def hepsini_hesapla(W, depo, satir, maske, kademe):
    out = {}
    for ist in sorted({w['ist'] for w in W}):
        V = istasyon_yukle(depo, ist, satir); V24 = istasyon_yukle(depo, ist, satir, bant='ccf24')
        for w in [x for x in W if x['ist'] == ist]:
            r = pencere_hesapla(w, V, maske[w['k']], kademe)
            r['delta_24'] = pencere_hesapla(w, V, maske[w['k']], kademe, ekli=False, bant_ccf=V24)['delta']
            if kademe == 'A': r['delta_altC'] = pencere_hesapla(w, V, maske[w['k']], kademe, ekli=False, alt_c=True)['delta']
            out[w['k']] = r
        del V, V24
    return out


# ---------------------------------------------------------------- δ_ko (bilgi satırları 13 ve 14)
def dko(V, t_olay, ref_ilk, maske_on=frozenset()):
    """TR-5b §4.2 adım 8 tanımı: δ_ko = ort ε(yığın sonu [T+10, T+30]) − ort ε(yığın sonu [T−60, T−8]); ±%2 ızgara
    (tr5b_yapay2.germe_pk); başvuru [ref_ilk, T−8]; enerji medyanı önce [ref_ilk, T−8], sonra [T+1, T+30] kendi
    medyanı; [T, T+30] için maske yok. Çift δ_ko'larının medyanı (≥ 2 çift)."""
    gl = [t_olay + TD(days=i) for i in range((ref_ilk - t_olay).days, 31)]
    on = [d for d in gl if d <= t_olay - TD(days=8)]; son = [d for d in gl if d > t_olay]
    c1, g1, _ = gunluk_cif(V, on, maske_on, (ref_ilk, t_olay - TD(days=8)))
    c2, g2, _ = gunluk_cif(V, son, frozenset(), (t_olay + TD(days=1), t_olay + TD(days=30)))
    tum = on + [t_olay - TD(days=i) for i in range(7, -1, -1)] + son
    tum = sorted(set(tum)); idx = {d: i for i, d in enumerate(tum)}
    sonuc = []
    for j in range(3):
        C = np.zeros((len(tum), c1.shape[2])); G = np.zeros(len(tum), bool)
        for d, i in idx.items():
            if d in on: k = on.index(d); C[i] = c1[j, k]; G[i] = g1[j, k]
            elif d in son: k = son.index(d); C[i] = c2[j, k]; G[i] = g2[j, k]
        if not G[[idx[d] for d in on]].any(): sonuc.append(float('nan')); continue
        ref = C[[idx[d] for d in on if G[idx[d]]]].mean(axis=0)
        Y, et = [], []
        for d in [t_olay + TD(days=k) for k in list(range(-60, -7)) + list(range(10, 31))]:
            rows = [C[idx[x]] for x in (d - TD(days=q) for q in range(10)) if x in idx and G[idx[x]]]
            if len(rows) >= YP.YIGIN_MIN: Y.append(np.mean(rows, axis=0)); et.append((d - t_olay).days)
        if not Y: sonuc.append(float('nan')); continue
        e = YP2.germe_pk(np.array(Y), ref); et = np.array(et)
        pre, post = e[et <= -8], e[et >= 10]
        sonuc.append(float(np.nanmean(post) - np.nanmean(pre)) if np.sum(~np.isnan(pre)) >= 10 and np.sum(~np.isnan(post)) >= 5 else float('nan'))
    return istasyon_delta(sonuc), sonuc


# ---------------------------------------------------------------- bilgi satırları
def bilgi_satirlari(W, R, kademe, depo, satir, G, rows_gec):
    sha_denet('tr4_pencereler.csv', G.get('csv_yol'))
    C = IN.csv_oku(G.get('csv_yol')); B = {}
    def alt(f, ad):
        rr = [(w['yer'], w['T'].year, R[w['k']]['delta']) for w in W if w['k'] in R and not np.isnan(R[w['k']]['delta']) and f(w)]
        if len(rr) < 5: return dict(ad=ad, n=len(rr), not_='hesaplanmadı (n < 5)')
        t = taban(rr, f'tr4-bilgi|{ad}|20261202'); t['ad'] = ad; t['kapi'] = kapi(yer_T([w for w in W if w['k'] in R and not np.isnan(R[w['k']]['delta']) and f(w)]))
        return t
    B['1'] = [alt(lambda w: C[w['k']]['sakin_ileri_2y'] == 'True', 'ileri 2 yıl'),
              alt(lambda w: C[w['k']]['sakin_M7_500'] == 'True', 'M ≥ 7 için 500 km'),
              alt(lambda w: C[w['k']]['sakin_M5_50_pencere'] == 'True', 'pencere içinde M ≥ 5 ≤ 50 km dışarıda'),
              alt(lambda w: C[w['k']]['sakin_M55_100_genis'] == 'True', 'M ≥ 5,5 ≤ 100 km ±1 yıl'),
              alt(lambda w: w['T'].year <= 2020, 'pencere içinde M ≥ 7 ≤ 1000 km dışarıda (T 2017–2020)')]
    B['2'] = [alt(lambda w: C[w['k']]['DOLU_gevsek'] == 'True', 'gevşek doluluk (indirilenlerle kesişim)'),
              alt(lambda w: C[w['k']]['DOLU_siki'] == 'True', 'sıkı doluluk')]
    B['3'] = [alt(lambda w: w['T'].year in (2017, 2020, 2023), 'T 2017/2020/2023'),
              alt(lambda w: w['T'].year in (2018, 2021, 2024), 'T 2018/2021/2024')]
    v = np.array([r[2] for r in rows_gec]) * 100
    B['4'] = dict(medyan=float(np.median(v)), q025=float(np.quantile(v, 0.025)), q975=float(np.quantile(v, 0.975))) if len(v) else None
    pt = {}
    for y in ANA_YIL:
        x = [r[2] * 100 for r in rows_gec if r[1] == y]
        if x: pt[y] = float(np.mean(x))
    B['5'] = dict(T_ortalama=pt, sd_T_arasi=float(np.std(list(pt.values()), ddof=1)) if len(pt) > 1 else None, n_T=len(pt))
    rng = np.random.default_rng(tohum('tr4-bilgi6|20261202')); ik = []
    Ty = [y for y in ANA_YIL if sum(1 for r in rows_gec if r[1] == y) >= 2]
    for _ in range(2000 if Ty else 0):
        y = Ty[rng.integers(len(Ty))]; x = [r[2] for r in rows_gec if r[1] == y]
        i, j = rng.choice(len(x), 2, replace=False); ik.append((x[i] + x[j]) / 2 * 100)
    B['6'] = dict(sigma_kontrol_esleni=kestir(ik)[0] if ik else None, cekilis=len(ik))
    yer = collections.defaultdict(list)
    for w in W:
        if w['k'] in R: yer[w['yer']].append(R[w['k']])
    B['7'] = {s: dict(n=sum(1 for r in L if not np.isnan(r['delta'])),
                      medyan=float(np.nanmedian([r['delta'] * 100 for r in L])) if any(not np.isnan(r['delta']) for r in L) else None,
                      mad=float(np.nanmedian(np.abs(np.array([r['delta'] for r in L]) * 100 - np.nanmedian([r['delta'] * 100 for r in L])))) if any(not np.isnan(r['delta']) for r in L) else None,
                      gecerli_cift=sum(r['gecerli_cift'] for r in L), saat_red_orani=float(np.nanmean([r['saat_red'] for r in L])))
              for s, L in sorted(yer.items())}
    B['8'] = alt(lambda w: w['T'].year != 2021, 'T 2021 dışarıda')
    if kademe == 'A':
        rr = [(w['yer'], w['T'].year, R[w['k']]['delta_altC']) for w in W if w['k'] in R and not np.isnan(R[w['k']].get('delta_altC', np.nan))]
        B['9'] = taban(rr, 'tr4-bilgi|9|20261202') if len(rr) >= 5 else dict(n=len(rr), not_='hesaplanmadı')
    else: B['9'] = 'kademe C seçildi; uygulanmaz'
    for ad, an in (('2–4 Hz', 'delta_24'), ('eğilimden arındırılmış', 'delta_egilimsiz')):
        rr = [(w['yer'], w['T'].year, R[w['k']][an]) for w in W if w['k'] in R and not np.isnan(R[w['k']][an])]
        B.setdefault('10', []).append(dict(ad=ad, **(taban(rr, f'tr4-bilgi|10|{ad}|20261202') if len(rr) >= 5 else dict(n=len(rr), not_='hesaplanmadı'))))
    gy = {}
    for s, L in yer.items():
        pp = []
        for r in L:
            for e in r['eps_ay']:
                e = np.array(e) * 100
                if np.sum(~np.isnan(e)) >= 9: pp.append(float(np.nanmax(e) - np.nanmin(e)))
        if pp: gy[s] = float(np.median(pp))
    B['11'] = dict(yer=gy, yer_medyani=float(np.median(list(gy.values()))) if gy else None)
    B['12'] = None
    # 13: Nisan 2025 M6,2, SLVT
    b13 = G.get('b13'); B['13'] = 'veri yok (aşama 0 doluluğu ya da indirme)'
    if b13:
        V = istasyon_yukle(depo, b13['ist'], satir, rol='bilgi13')
        if V:
            d, c = dko(V, b13['T'], b13['T'] - TD(days=400))
            sha_denet('tr4_guc_sonuc.json')
            pk = json.load(open(YOL['tr4_guc_sonuc.json'], encoding='utf-8'))['pk']['sonuc']
            esik = {k.split('|')[0]: pk[k]['esik_q05_A0_yuzde'] for k in pk if k.endswith('|4s|A=0.00%')}
            B['13'] = dict(dko_yuzde=None if np.isnan(d) else d * 100, cift=[None if np.isnan(x) else x * 100 for x in c],
                           A0_q05_esigi_yuzde=esik, altinda={k: (None if np.isnan(d) else bool(d * 100 < v)) for k, v in esik.items()})
    # 14: 2019 Silivri
    ev, t14, ists = OLAY_2019; r14 = {}
    for s in ists:
        if not any(w['ist'] == s and w['T'].year == 2020 for w in W): r14[s] = None; continue
        V = istasyon_yukle(depo, s, satir)
        d, _ = dko(V, t14, t14 - TD(days=TABAN_GUN)); r14[s] = None if np.isnan(d) else d * 100
    vv = [x for x in r14.values() if x is not None]
    B['14'] = dict(olay=ev, istasyon=r14, ortalama=float(np.mean(vv)) if vv else None)
    return B


# ---------------------------------------------------------------- ana sıra
def kademe_metni(kademe, kesik, Tler):
    return f'kademe {kademe}, kesik, T {min(Tler)}–{max(Tler)}' if kesik else f'kademe {kademe}'


def hukum_yaz(depo, H):
    yol = os.path.join(depo, 'kosu', 'hukum.json')
    assert H['hukum'] in HUKUM_ADLARI, H['hukum']
    if os.path.exists(yol):
        eski = json.load(open(yol, encoding='utf-8'))
        if eski['hukum'] != H['hukum'] or eski['metin'] != H['metin']:
            raise SystemExit('hukum.json farklı bir hükümle var; tek koşu (§5.6, §11); durdu')
        return yol
    IN.yaz_json(yol, H)
    return yol


def olc(ob, depo, npz, G=None):
    G = G or IN.girdiler(ob)
    D = Durum(depo)
    if os.path.exists(os.path.join(depo, 'kosu', 'hukum.json')):
        H = json.load(open(os.path.join(depo, 'kosu', 'hukum.json'), encoding='utf-8'))
        print('hüküm zaten yazıldı (tek koşu):', H['hukum']); return H
    kademe = G['kademe']
    # adım 0: aşama 0 ve aşama H
    if G['S0'].get('hukum') == 'veri yok (aşama 0)':
        H = dict(hukum='veri yok (aşama 0)', metin=f"veri yok (aşama 0). T başına dolu yer: {t_metin({int(k): v for k, v in G['S0']['yer_T'].items()})}; bilgi satırı 0: hesaplanmadı (indirme yok)")
        hukum_yaz(depo, H); return H
    if kademe == 'veri yok (aktarım hızı)':
        H = dict(hukum=kademe, metin=f"veri yok (aktarım hızı). {G['hiz'].get('ek_metin', '')}")
        D.yaz('0', hukum=kademe); hukum_yaz(depo, H); return H
    if kademe not in ('A', 'C'): raise SystemExit(f'kademe seçilmedi ({kademe}); ölçü koşmaz')
    B = IN.butce_oku(depo)
    if B['durum'] not in ('bitti', 'kesildi'):
        raise SystemExit(f"indirme durumu '{B['durum']}': indirme bitmeden ya da kesilmeden hiçbir ε ya da Δ hesaplanmaz (§5.5); durdu")
    isler = IN.plan(G)
    satir, deneme = IN.son_durum(IN.satirlar(IN.durum_yollari(depo)['gunluk']))
    hukum = None; ek0 = ''
    W = G['W']
    kesik = B['durum'] == 'kesildi'
    if kesik:
        # K7: "indirildi" = bütün istasyon-ay istekleri KESIN kodla tamamlandı; T tamam = bütün yer-pencereleri indirildi
        eksik_T = sorted({w['T'].year for w in W
                          if not all(k in satir and satir[k]['kod'] in IN.KESIN for k in IN.pencere_aylari(w, kademe))})
        tamam_T = sorted({w['T'].year for w in W} - set(eksik_T))
        W = [w for w in W if w['T'].year in tamam_T]
        yT = yer_T(W)
        etkin = B['etkin_sn'] / 86400; takvim = ((B.get('bitis') or time.time()) - B['ilk_istek']) / 86400
        D.yaz('0_kesik', tamamlanan_T=tamam_T, eksik_T=eksik_T, yer_T=yT, etkin_gun=etkin, takvim_gun=takvim)
        if any(D_YIL[0] <= y <= D_YIL[1] for y in eksik_T) or not kapi(yT):
            hukum = 'veri yok (indirme bütçesi)'
            ek0 = (f"tamamlanan T: {', '.join(map(str, tamam_T)) or 'yok'}; T başına yer: {t_metin(yT)}; "
                   f"etkin süre {yz(etkin, 2)} gün, takvim {yz(takvim, 2)} gün")
    maske = maske_gunleri(G)
    # adım 1: 1b
    b1 = b1_hesapla(W, depo, satir, maske, kademe)
    W1 = [w for w in W if b1[w['k']]['dolu']]
    y1 = yer_T(W1)
    D.yaz('1b', yer_T=y1, dolu=len(W1), pencere=b1)
    if hukum is None and not kapi(y1):
        hukum = 'veri yok (gün doluluğu)'; ek0 = f'T başına dolu yer: {t_metin(y1)}'
    # adım 2: kod denetimi (i)
    d1 = denetim_i(npz, kademe)
    D.yaz('2_denetim_i', **d1)
    if d1['sapan'] > 0:
        if hukum is None:
            H = dict(hukum='geçersiz (kod)', metin=f"geçersiz (kod). sapan dizi sayısı {d1['sapan']}", denetim_i=d1)
            hukum_yaz(depo, H); return H
        H = dict(hukum=hukum, metin=f"{hukum}. {ek0}; bilgi satırı 0: hesaplanmadı (n = 0, yer = 0)", denetim_i=d1)
        hukum_yaz(depo, H); return H
    # adım 3: (ii-a) ve Δ (bütün dolu pencereler)
    R = hepsini_hesapla(W1, depo, satir, maske, kademe)
    oran = [(R[k]['delta_ekli'] - R[k]['delta']) / EKLEME for k in R if not np.isnan(R[k]['delta']) and not np.isnan(R[k]['delta_ekli'])]
    mo = float(np.median(oran)) if oran else float('nan')
    D.yaz('3_denetim_iia', medyan_oran=mo, n=len(oran))
    if oran and not (ORAN_ARALIK[0] <= mo <= ORAN_ARALIK[1]):
        if hukum is None:
            H = dict(hukum='geçersiz (kod)', metin=f'geçersiz (kod). medyan oran {yz(mo, 3)}', medyan_oran=mo)
            hukum_yaz(depo, H); return H
        H = dict(hukum=hukum, metin=f"{hukum}. {ek0}; bilgi satırı 0: hesaplanmadı (n = 0, yer = 0)", medyan_oran=mo)
        hukum_yaz(depo, H); return H
    # adım 4: ε geçerliliği
    Wg = [w for w in W1 if not np.isnan(R[w['k']]['delta'])]
    yg = yer_T(Wg)
    rows = [(w['yer'], w['T'].year, R[w['k']]['delta']) for w in Wg]
    D.yaz('4_eps', yer_T=yg, gecerli=len(Wg))
    if hukum is None and not kapi(yg):
        hukum = 'veri yok (ε geçerliliği)'; ek0 = f'T başına geçerli yer: {t_metin(yg)}'
    # ölçüm dosyası (Δ tablosu) ve sha256
    olcum = dict(kademe=kademe, kesik=kesik, delta={k: {a: b for a, b in v.items() if a != 'eps_ay'} for k, v in R.items()},
                 oran_ii_a=oran, medyan_oran=mo)
    oy = os.path.join(D.dir, 'olcum_delta.json'); IN.yaz_json(oy, olcum)
    D.yaz('olcum_dosyasi', sha256=IN.sha_dosya(oy))
    Bl = bilgi_satirlari(W1, R, kademe, depo, satir, G, rows)
    if hukum is not None:
        m0, t0 = bilgi0_metin(rows, hukum)
        H = dict(hukum=hukum, metin=f'{hukum}. {ek0}; {m0}', bilgi_0=t0, bilgi=Bl)
    else:
        t = taban(rows)
        hukum = c_hukmu(t)
        Bl['12'] = dict(q95_kPa=t['q95'] / 100 / MPA_DUYARLILIK * 1000, not_='bant farklı; yalnız mertebe')
        b14 = Bl['14']['ortalama']
        b14m = f"{yz(b14)} % (istasyon ortalaması)" if b14 is not None else 'hesaplanamadı'
        H = dict(hukum=hukum, metin=f"{hukum}. {kalip_T(t, kademe_metni(kademe, kesik, t['T']), Bl['11']['yer_medyani'], b14m)}",
                 taban=t, bilgi=Bl)
    if Bl.get('12') is None and H.get('bilgi_0'): Bl['12'] = dict(q95_kPa=H['bilgi_0']['q95'] / 100 / MPA_DUYARLILIK * 1000)
    yol = hukum_yaz(depo, H)
    D.yaz('5_hukum', hukum=H['hukum'], sha256=IN.sha_dosya(yol))
    print(H['metin'])
    return H


if __name__ == '__main__':
    k = sys.argv[1] if len(sys.argv) > 1 else ''
    a = [x for x in sys.argv[2:] if not x.startswith('--')]
    if k == 'denetim_i':
        G = IN.girdiler(a[0]); d = denetim_i(a[2], G['kademe']); Durum(a[1]).yaz('2_denetim_i_on', **d)
        print(json.dumps({x: y for x, y in d.items() if x != 'sapan_liste'}, ensure_ascii=False))
    elif k == 'olc': olc(a[0], a[1], a[2])
    elif k == 'durum': print(json.dumps(Durum(a[1]).d, ensure_ascii=False, indent=1)[:20000])
    else: print(__doc__)
