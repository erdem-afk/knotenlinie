#!/usr/bin/env python3
"""TR-7c koşu kodu: K5 sızıntı kuralıyla kör Parkfield kontrolü (K1c) ve yalnız K1c (b) ise Marmara.

Bağlayıcı metin: `kayit/onkayit/TR-7c_tetiklenmis-tremor_ONKAYIT.md` (KARAR METNİ DONDURULDU, commit bd3c93a).
Kodlayıcı okumaları ve seçimler: `kayit/onkayit/TR-7c_KODLAYICI-OKUMALARI.md` (burada "O-n" diye anılır).

GERÇEK KİP KAPISI (TR-13b §12.1 ve TR-13b KOD-İNCELEME §G örneği): ağ isteği yapan ya da gerçek (kör) dalga formu /
zarf açan HER yol `gercek_kapi()`'yı kendi içinde çağırır: `GercekOrtam.istemci/zyol/hyol`, `GercekKaynak.__init__` ve
okuma işlevleri, bütün `asama_*` işlevleri, `marmara_kos`, gerçek çıktı dizinine yazan `k1c_kos`. Kapı ancak ön kaydın
"Durum:" satırında "KOŞU DONDURULDU" yazıyorsa, bu dosyanın ve `KOD_DOSYALARI`'nın sha256'ları ön kayıt metninde
geçiyorsa, karar metninin §0–§6 gövdesi dondurulmuş hâliyle aynıysa ve D-2 dosyaları uyuşuyorsa açılır. İçe aktarılarak
çağrılınca da aynı kapı işler. Bugün (koşu dondurması yok) kapı KAPALIDIR; `tr7c_test_yapay.py` bunu sınar.

D-2: modül yüklenirken, K5'i içe aktarmadan ÖNCE, K5'in çağrı ağacındaki üç dosyanın sha256'sı denetlenir; biri
uyuşmazsa modül yüklenmez (hiçbir şey hesaplanmaz).

Aşamalar (§10 madde 6; aşama adlarında K1 → K1c): manifest → K1c-indirme → K1c-negatif → K1c-algılama (önce 29 N
birimi, sonra 10 P; modülasyon bütün olaylardan sonra, T0 sırasıyla; Z3/Z4 en sonda; hüküm dosyası bir kez, "x" kipi).
Marmara: `marmara` komutu ayrıdır ve yalnız K1c hüküm dosyası dal (b) ise ve kapı açıksa ilerler (bkz. O-30).

Yapay sınama `kos`un çekirdeğini (`k1c_kos`) bellekteki bir `Kaynak`la çağırır; gerçek dalga formu açan hiçbir sınama
yoktur.

Kullanım (depo kökünden, python3 -I -B):
  tr7c_kosu.py kapi                     kapının durumunu yazar (hiçbir şey açılmaz)
  tr7c_kosu.py baslat <aşama>           durum dosyasına "başladı" yazar (commit + push sonra)
  tr7c_kosu.py kos <aşama> [--surdur]   aşamayı koşar (kapı + git doğrulaması)
  tr7c_kosu.py marmara <aşama>          yalnız K1c (b) hüküm dosyası varsa
  tr7c_kosu.py durum
"""
import dataclasses
import datetime as dt
import hashlib
import json
import math
import os
import sys

import numpy as np

sys.dont_write_bytecode = True
BURA = os.path.dirname(os.path.abspath(__file__))
DEPO = os.path.abspath(os.path.join(BURA, '..', '..', '..'))
TR7 = os.path.join(DEPO, 'kayit', 'turetme', 'tr7')
TR7B = os.path.join(DEPO, 'kayit', 'turetme', 'tr7b')


def sha256_dosya(yol):
    h = hashlib.sha256()
    with open(yol, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


class Tr7cDur(Exception):
    """Girdi, biçim ya da önkoşul sorunu: koşu durur; 'veri yok' yazılmaz."""


class GercekKipReddedildi(SystemExit):
    """Gerçek kip kapısı kapalı: hiçbir ağ isteği yapılmadı, hiçbir gerçek dosya açılmadı."""


# ====================================================================== D-2 (K5 içe aktarılmadan ÖNCE)
D2_DOSYALAR = {
    os.path.join(TR7B, 'tr7b_yapay2.py'): 'ae995ba8802a934577cbf26051229360bcfb1a85d5d4d7dc16d358dfeaef437f',
    os.path.join(TR7B, 'tr7b_yapay.py'): 'e92715318e21a0200b66e3c130853f73cbc382b0398aef561619fcbe1bb74374',
    os.path.join(TR7, 'tr7_cekirdek.py'): '4a1b9131603d0f3d519cacb183fdbcccc106157b66392bf2d09350c9f49206f6',
}


def d2_denetle(dosyalar=None):
    """D-2 (aynen): 'Biri uyuşmazsa hiçbir şey hesaplanmadan durur.' Dönüş: {yol: sha} ya da Tr7cDur."""
    dosyalar = D2_DOSYALAR if dosyalar is None else dosyalar
    out = {}
    for yol, beklenen in dosyalar.items():
        if not os.path.exists(yol):
            raise Tr7cDur(f'D-2: dosya yok: {yol}')
        s = sha256_dosya(yol)
        if s != beklenen:
            raise Tr7cDur(f'D-2: sha256 uyuşmuyor: {os.path.basename(yol)} ({s} ≠ {beklenen}); hiçbir şey hesaplanmadı')
        out[os.path.relpath(yol, DEPO)] = s
    return out


D2_SONUC = d2_denetle()
sys.path.insert(0, TR7B)
sys.path.insert(0, TR7)
import tr7_cekirdek as K  # noqa: E402  (değiştirilmeden)
import tr7b_yapay2 as Y2  # noqa: E402  (değiştirilmeden; K5, _rho, _delta)
Y = Y2.Y                  # tr7b_yapay (secili, _k1_kalinti)
assert Y.c is K, 'K5 başka bir tr7_cekirdek örneğine bağlı'

# ====================================================================== sabitler
ONKAYIT = os.path.join(DEPO, 'kayit', 'onkayit', 'TR-7c_tetiklenmis-tremor_ONKAYIT.md')
KARAR_GOVDE_SHA = '8761573150be97dca99590283d7e3cecc3ddf0067804945966773f5276f69f18'   # §0–§6 (bd3c93a)
KOD_DOSYALARI = ('tr7c_kosu.py', 'tr7c_mde_ek.py')
GIRDI = {   # repo içi, yalnız okunur (O-3)
    os.path.join(TR7B, 'tr7b_sayim.json'): '55318360214f96237802346d84a501e6c6964116906332362e704e3b0e5e5114',
    os.path.join(BURA, 'ustveri', 'tr7c_ustveri.json'): 'ed8cf3c63cc89609ed4bc865df788bc94c4f6fab40168f7985dd99d2d66ead8c',
    os.path.join(TR7, 'tr7_parkfield_liste.csv'): '9dca3380815196a8db15a8a5929441d38dd9b07fd7ed982845543e179957b2b8',
    os.path.join(BURA, 'inc1', 'tr7c_inc1.json'): '4974dbe66163b49ba8c1b7dab699121c45cdce5aa1fba53c0cb1b0791d912974',
    os.path.join(BURA, 'tr7c_mde_ek.json'): 'e759176ec28f0b4a9f18fed47bddfe1ed7f43a52fa24ed994c5d2a1d062c3b3d',
}
TR7_MOTOR = {   # K-2: GercekOrtam/GercekKaynak'ın çağırdığı TR-7 motoru (tr7_sonuc.md'deki kod sha256'larıyla aynı)
    os.path.join(TR7, 'tr7_kosu.py'): 'ce439a4797fd1992ddd68de734ee842b146bd6f13155ba6151769bceb26a9005',
    os.path.join(TR7, 'tr7_indir.py'): '0763f46da14b2a12f5268937dc6e479dbfd1bc54c3c3ba93d700914dc4b91f2f',
}
CIKTI = os.path.join(BURA, 'kosu')                    # gerçek koşunun çıktı dizini (kapı ister)
DURUM_AD = 'TR7C_KOSU_DURUM.json'
HUKUM_AD = 'tr7c_k1c_hukum.json'
ZARF_KOK = '/mnt/project-files/turetme/tr7c-zarf'        # depo dışı; yalnız kapı açıkken
GERCEK_KOKLER = (ZARF_KOK, '/mnt/project-files/turetme/tr7c-marmara')

P_OLAY = ('200106232033', '200211032212', '200301220206', '200309251950', '200412260058', '200611151114',
          '200701130423', '200805120628', '200909291748', '201002270634')
VANUATU = ('200910072203', '200910072218')               # D-1: tek N birimi; tetikleyici N 27
VANUATU_BIRIM = 'VANUATU2009'
GENLIK4 = ('200412231459', '200503281609', '200704012039', '200708152340')   # D-9: Macquarie, Nias, Solomon, Peru 2007
BILGI_OLAY = ('200111140926', '200605031526')            # Kunlun 2001, Tonga 2006 (bilgi satırı)
KURIL2007 = '200701130423'
NEG_OLAY = P_OLAY + ('200412231459', '200708152340')     # rastgele negatif: 10 P + Macquarie 2004 + Peru 2007
IZ_ORTA = (35.9125, -120.4625)                           # iz köşe ortalaması (enlem, boylam)
V_K1B = (4.6, 3.0)                                       # K1b aralığı [T0 + Δ/4,6, T0 + Δ/3,0]

N_P_MIN, N_N_MIN = 8, 20                                 # Z4 (a)
FAR_TAVAN, N_PK_MIN = 0.30, 5                            # Z3 (ii), yazarın seçimi 2
FISHER_ALFA = 0.05                                       # Z3 (iii)
MOD_P_MIN = 3                                            # Z3 (iv)
A90_TAVAN = 1e5                                          # 100 µm/s (nm/s)
K_USTVERI = 10                                           # E-2
MOD_TOHUM_PK = 20261112 + 3                              # §4.1 yazarın seçimi (Parkfield kör koşusu, yeni örnek)
NEG_TOHUM = 20261116 + 1                                 # TR-7b §6.3
NEG_SAYI, NEG_N_MAX = 10, 120
MDA_BAS_PK = 3                                           # TR-7b §6.3
BIRLESIK_BIRIMLER = {VANUATU_BIRIM: VANUATU}             # D-1 (mutasyon sınaması bunu boşaltır)
BPRIME_MASKE_S, BPRIME_FAZ = 5, (-10, 120)               # TR-7 §7.2 (b′)


@dataclasses.dataclass(frozen=True)
class Ayar:
    mod_n: int = K.MOD_N           # §6.4: 1000 kaydırma (yapay sınama hız için küçültebilir; gerçek kipte yalnız 1000)
    mda_bas: int = MDA_BAS_PK


# ====================================================================== gerçek kip kapısı
def karar_govde_sha(metin):
    a = metin.index('\n## 0. ')
    b = metin.index('\n## 7. ')
    return hashlib.sha256(metin[a + 1:b + 1].encode('utf-8')).hexdigest()


def kod_sha():
    return {f: sha256_dosya(os.path.join(BURA, f)) for f in KOD_DOSYALARI}


def kosu_dondurulmus_mu(onkayit=None):
    """(açık mı, neden). Şartlar (hepsi): 'Durum:' satırında KOŞU DONDURULDU; KOD_DOSYALARI'nın sha256'ları metinde;
    §0–§6 gövdesi karar metni dondurmasındakiyle aynı; D-2 dosyaları uyuşuyor; repo girdileri uyuşuyor."""
    onkayit = ONKAYIT if onkayit is None else onkayit
    if not os.path.exists(onkayit):
        return False, 'ön kayıt yok'
    with open(onkayit, encoding='utf-8') as f:
        metin = f.read()
    durum = next((s for s in metin.splitlines() if s.startswith('Durum:')), '')
    if 'KOŞU DONDURULDU' not in durum:
        return False, "koşu dondurması yok ('Durum:' satırında 'KOŞU DONDURULDU' yok)"
    try:
        g = karar_govde_sha(metin)
    except ValueError:
        return False, 'karar metninin §0/§7 başlıkları bulunamadı'
    if g != KARAR_GOVDE_SHA:
        return False, f'karar metni §0–§6 gövdesi değişmiş ({g[:12]}…)'
    eksik = [k for k, v in kod_sha().items() if v not in metin]
    if eksik:
        return False, 'sha256\'sı ön kayıtta yazılı değil: ' + ', '.join(eksik)
    try:
        d2_denetle()
        girdi_denetimi()
        d2_denetle(TR7_MOTOR)     # K-2 (kod incelemesi): gerçek I/O katmanının çağırdığı TR-7 motoru da sabit
    except Tr7cDur as e:
        return False, str(e)
    return True, 'tamam'


def gercek_kapi(islem, onkayit=None):
    """Her gerçek yolun girişinde. Kapalıysa GercekKipReddedildi (SystemExit): hiçbir şey açılmadı, istenmedi."""
    ok, neden = kosu_dondurulmus_mu(onkayit)
    if not ok:
        raise GercekKipReddedildi(f'GERÇEK KİP REDDEDİLDİ ({islem}): {neden}')
    return True


def gercek_yol_mu(yol):
    r = os.path.realpath(yol)
    return any(r == os.path.realpath(k) or r.startswith(os.path.realpath(k) + os.sep) for k in GERCEK_KOKLER) \
        or r == os.path.realpath(CIKTI) or r.startswith(os.path.realpath(CIKTI) + os.sep)


def girdi_denetimi():
    out = {}
    for yol, beklenen in GIRDI.items():
        if not os.path.exists(yol):
            raise Tr7cDur(f'girdi yok: {yol}')
        s = sha256_dosya(yol)
        if s != beklenen:
            raise Tr7cDur(f'girdi sha256 uyuşmuyor: {os.path.basename(yol)}')
        out[os.path.relpath(yol, DEPO)] = s
    return out


# ====================================================================== olay listesi (Z2, D-1; yalnız repo dosyaları)
def _json(yol):
    with open(yol, encoding='utf-8') as f:
        return json.load(f)


def olaylar():
    """{evid: dict(evid, ad, t0 (datetime), la, lo, M, Q, pgv_t, delta_km)} — tr7b_sayim.json'dan (Tablo S1)."""
    d = _json(os.path.join(TR7B, 'tr7b_sayim.json'))
    out = {}
    for o in d['olaylar']:
        if o['evid'].startswith('2011'):
            continue                                      # Tohoku: geliştirme verisi, kör listeye girmez
        out[o['evid']] = dict(evid=o['evid'], ad=o['ad'], t0=K.zaman(o['t0']), la=o['lat'], lo=o['lon'], M=o['M'],
                              Q=o['Q_CC'], pgv_t=o['pgv_t_cms'], delta_km=o['delta_km'])
    return out


def birimler_kur(ol=None, ustveri=None):
    """Z2 + D-1: P (10 olay), N (30 olayın 29 birimi), B (bilgi: Kunlun 2001, Tonga 2006). T0 sırasıyla.
    Birim: dict(id, sinif, evids, t0 (ilk olayın), pgv_t (N'de olayların en büyüğü), K1b (epoch, kapsayıcı uç),
    K1b_acik_pay (USTVERI, dondurulmuş), maskelenen (USTVERI E1 varışları), genlik4 (D-9))."""
    ol = olaylar() if ol is None else ol
    ust = _json(os.path.join(BURA, 'ustveri', 'tr7c_ustveri.json')) if ustveri is None else ustveri
    ub = {b['ad']: b for b in ust['birimler']}
    birlesik = {e: b for b, es in BIRLESIK_BIRIMLER.items() for e in es}
    out, goruldu = [], set()
    for e in sorted(ol, key=lambda x: ol[x]['t0']):
        o = ol[e]
        if e in P_OLAY:
            sinif = 'P'
        elif o['Q'] == 0:
            sinif = 'N'
        elif e in BILGI_OLAY:
            sinif = 'B'
        else:
            continue
        if e in birlesik:
            bid = birlesik[e]
            if bid in goruldu:
                continue
            goruldu.add(bid)
            evids = BIRLESIK_BIRIMLER[bid]
            u = ub.get(bid)       # K-1 (kod incelemesi): USTVERI birleşik birimi birim adıyla yazar (D-1)
        else:
            bid, evids, u = e, (e,), ub.get(e)
        k1b = k1b_formul([ol[x] for x in evids])
        b = dict(id=bid, sinif=sinif, evids=list(evids), t0=ol[evids[0]]['t0'], ad=' + '.join(ol[x]['ad'] for x in evids),
                 pgv_t=max(ol[x]['pgv_t'] for x in evids), genlik4=bool(set(evids) & set(GENLIK4)),
                 K1b_formul=k1b)
        if u is not None:
            b.update(K1b=(K.epoch(u['K1b'][0]), K.epoch(u['K1b'][1])), K1b_acik_pay=u['K1b_acik_pay'],
                     maskelenen=u['maskelenen_varis'], tetikleyici_id=u['tetikleyici_id'])
        else:
            b.update(K1b=k1b, K1b_acik_pay=None, maskelenen=None, tetikleyici_id=None)
        out.append(b)
    return out


def k1b_formul(evs):
    """[T0 + Δ/4,6, T0 + Δ/3,0] iz ortasında, saniyeye yuvarlanmış; birimde [ilk başı, son sonu] (D-1)."""
    a = min(K.epoch(e['t0']) + e['delta_km'] / V_K1B[0] for e in evs)
    b = max(K.epoch(e['t0']) + e['delta_km'] / V_K1B[1] for e in evs)
    return float(round(a)), float(round(b))


# ====================================================================== saf istatistik ve dal (Z3, Z4, D-7)
def fisher_tek(xp, n, xn, m):
    """Yazarın seçimi 1: P(X ≥ X_P | X_P + X_N, n_P, n_N), hipergeometrik üst kuyruk (tr7c_guc.py fisher_tek)."""
    k = xp + xn
    T = n + m
    if T == 0:
        return 1.0
    den = math.comb(T, k)
    return sum(math.comb(n, x) * math.comb(m, k - x) for x in range(xp, min(k, n) + 1)) / den


def xmin(n, f, N):
    """TR-7 §8: P(Bin(n, p_üst) ≥ X) ≤ 0,05 olan en küçük X ∈ [2, n]; yoksa None (D-7: (i) sağlanmaz). p_üst:
    Clopper–Pearson tek yanlı %95 üst sınırı (K.cp_ust). K2 kapısı (TR-7 Marmara) burada YOKTUR (O-12). N = 0 → None."""
    if N <= 0:
        return None
    pu = K.cp_ust(f, N)
    return next((x for x in range(2, n + 1) if K.binom_ust(n, pu, x) <= 0.05), None)


def a90_sayi(A90):
    return A90 if isinstance(A90, (int, float)) and not isinstance(A90, bool) else None


def z3(n_P, n_N, X_P, X_N, f_PK, N_PK, M_mod):
    xm = xmin(n_P, f_PK, N_PK)
    i = xm is not None and X_P >= max(math.ceil(n_P / 2), xm)
    ii = N_PK >= N_PK_MIN and f_PK / N_PK <= FAR_TAVAN
    pf = fisher_tek(X_P, n_P, X_N, n_N)
    iii = pf <= FISHER_ALFA
    iv = M_mod >= MOD_P_MIN
    return dict(i=i, ii=ii, iii=iii, iv=iv, X_min=xm, fisher_p=pf,
                FAR_PK=(f_PK / N_PK if N_PK else None))


def _e_ikinci_cumle_uygulanir(a, i, ii):
    """D-7: (e)'nin ikinci cümlesi yalnız (a) sağlanmıyorsa ve (i) ile (ii) sağlanıyorsa."""
    return (not a) and i and ii


def k1c_dal(n_P, n_N, X_P, X_N, f_PK, N_PK, M_olc, M_mod, A90_PK):
    """Z4 + D-7, sıra bağlayıcı. Dönüş (dal, alt, z3 sözlüğü). alt: (c)'de kalan şart(lar) (Ö-d), (e)'de 'yöntem' ya da
    'modülasyon ölçülemedi'."""
    s = z3(n_P, n_N, X_P, X_N, f_PK, N_PK, M_mod)
    a = n_P < N_P_MIN or n_N < N_N_MIN
    a90 = a90_sayi(A90_PK)
    if a:
        return 'a', None, s
    if s['i'] and s['ii'] and s['iii'] and s['iv']:
        return 'b', None, s
    if s['i'] and s['ii'] and M_olc >= MOD_P_MIN and (not s['iii'] or not s['iv']):
        kalan = ' ve '.join(x for x, v in (('(iii)', s['iii']), ('(iv)', s['iv'])) if not v)
        return 'c', kalan, s
    if (not s['i'] or not s['ii']) and a90 is not None and a90 <= A90_TAVAN:
        return 'd', None, s
    if _e_ikinci_cumle_uygulanir(a, s['i'], s['ii']) and M_olc < MOD_P_MIN:
        return 'e', 'modülasyon ölçülemedi', s
    return 'e', 'yöntem', s


def marmara_acilir(dal):
    """Z4: '(b) dışında Marmara verisi indirilmez.'"""
    return dal == 'b'


def say(x, n=2):
    if x is None:
        return '—'
    if isinstance(x, str):
        return x
    return f'{x:.{n}f}'.replace('.', ',')


def anlamli(x, n=3):
    if x is None or isinstance(x, str):
        return '—' if x is None else x
    if x == 0:
        return '0'
    b = n - 1 - int(math.floor(math.log10(abs(x))))
    return f'{round(x, b):.{max(0, b)}f}'.replace('.', ',')


_MDE = {}


def mde_degeri(n_P, n_N):
    """D-8: q 0,1'de görülebilir en küçük s (m_t 0,8, m_t 0,5). inc1 tablosu, yoksa dondurulmuş ek tablo."""
    if not _MDE:
        _MDE['inc1'] = _json(os.path.join(BURA, 'inc1', 'tr7c_inc1.json'))['esik']['MDE_tablosu_q0.1']
        _MDE['ek'] = _json(os.path.join(BURA, 'tr7c_mde_ek.json'))
    k = f'nP{n_P}_nN{n_N}'
    v = _MDE['inc1'].get(k) or _MDE['ek']['MDE_q01'].get(k)
    if v is None:
        return None
    return v['mt08'], v['mt05']


def k_guc(k):
    """E-2: k_koşu ile güç (s 0,7, q 0,1; esik.D1_kref_guc_s0.7_q0.1 işlevi; dondurulmuş ek tablo, k 0…10)."""
    if not _MDE:
        mde_degeri(10, 29)
    v = _MDE['ek']['k_guc_s07_q01'].get(f'k{k}')
    return None if v is None else (v['mt08'], v['mt05'])


def d8_eki(n_P, n_N):
    v = mde_degeri(n_P, n_N)
    if v is None:
        return ' (ayırt edilemez: görülebilir en küçük s bu n_P, n_N için dondurulmamış)'
    return (f' (ayırt edilemez: gerçekleşen n_P, n_N ile, q 0,1\'de görülebilir en küçük s = {say(v[0])} (m_t 0,8) / '
            f'{say(v[1])} (m_t 0,5))')


def k1c_cumle(dal, alt, n_P, n_N, X_P, A90_PK, etiket):
    """K1c satırı. etiket: dict(b_prime, mod_gecti, genlik, genlik_olculemeyen, k_kosu)."""
    if dal == 'a':
        c = 'ölçü sınanamadı (Parkfield verisi yok)'
    elif dal == 'b':
        c = 'ölçü sınandı' if etiket['mod_gecti'] else \
            'ölçü sınandı (Parkfield modülasyonu geçmedi: Marmara\'da en çok "aday")'
        if etiket['b_prime']:
            c += '; geçti, belirsiz (cisim dalgası açıklaması dışlanamadı)'
    elif dal == 'c':
        c = ('ölçü sınanamadı (algılayıcı kör olaylarda tetiklenmiş tremoru tetikleyici genliğinden ayıramadı)'
             f' (kalan: {alt})' + d8_eki(n_P, n_N))
    elif dal == 'd':
        c = ('ölçü sınanamadı (kör Parkfield olaylarında tetiklenmiş tremor ölçütü karşılamadı: '
             f'X_P = {X_P} / n_P = {n_P}; A90_PK = {anlamli(a90_sayi(A90_PK))} nm/s)' + d8_eki(n_P, n_N))
    else:
        c = f'ölçü sınanamadı ({alt})' + d8_eki(n_P, n_N)
    if etiket.get('genlik'):
        c += '; genlik karıştırıcısı dışlanmadı'
    c += f'; genliği eşlenmiş 4 N olayında modülasyonu ölçülemeyen: {etiket.get("genlik_olculemeyen", "—")}'
    c += f'; k: üstveriden {K_USTVERI}, koşuda {etiket.get("k_kosu", "—")}'
    if isinstance(etiket.get('k_kosu'), int) and etiket['k_kosu'] < K_USTVERI:
        g = k_guc(etiket['k_kosu'])
        if g:
            c += f' (k_koşu ile güç, s 0,7, q 0,1: {say(g[0])} (m_t 0,8) / {say(g[1])} (m_t 0,5); bilgi)'
    return c


def var_verilebilir(dal, etiket):
    """§6.2: 'VAR' ancak K1c (b), (b′) 'belirsiz' değil, 'Parkfield modülasyonu geçti' ve D-9 etiketi yok ise
    (TR-7 §8 sıra 5'in öteki şartları Marmara aşamasında). Değilse en çok 'aday'."""
    return dal == 'b' and not etiket['b_prime'] and etiket['mod_gecti'] and not etiket['genlik']


def s_sapka(X_P, n_P, X_N, n_N):
    """§6.2 yazarın seçimi: ŝ = max(0, (X_P/n_P − X_N/n_N) / (1 − X_N/n_N))."""
    if n_P == 0 or n_N == 0:
        return None
    q = X_N / n_N
    if q >= 1:
        return 0.0
    return max(0.0, (X_P / n_P - q) / (1 - q))


def cp_alt(x, n, a=0.05):
    """Clopper–Pearson tek yanlı %95 alt sınırı (Ö-e): P(Bin(n, p) ≥ x) = a; ikiye bölme."""
    if x <= 0:
        return 0.0
    lo, hi = 0.0, x / n
    for _ in range(200):
        m = (lo + hi) / 2
        if K.binom_ust(n, m, x) < a:
            lo = m
        else:
            hi = m
    return (lo + hi) / 2


def z6_cumle(seg, n, A90, A_PK, s_hat, n_acik, b_prime=False):
    """Z6 'görülmedi' cümlesi + D-6 + Z6 ek kuralı (Marmara aşaması için saf işlev)."""
    a90 = a90_sayi(A90)
    oran_buyuk = a90 is None or a90 > A90_TAVAN or not A_PK or (a90 / A_PK > 1)
    c = (f'{seg}\'de kaba τ ≥ 2 kPa olan n = {n} tetikleyicide tetiklenmiş tremor görülmedi. Bu segmentte '
         f'algılanabilir en küçük genlik A90({seg}) = {anlamli(a90) if a90 is not None else A90} nm/s\'dir. Parkfield '
         f'kör olaylarında algılanan tremorun 25 km\'ye indirgenmiş medyan genliği A_PK = {anlamli(A_PK)} nm/s\'dir. ')
    if not oran_buyuk:
        c += ('Parkfield türü, ≈ 2 kPa\'da tetiklenen ve Parkfield\'dakine eşit genlikte tremor veren bir kaynak bu '
              'gürültüde görülürdü. ')
        if n_acik < 5:
            c += 'hiç görülmeme olasılığı hesaplanmadı (n_açık < 5). '
        else:
            c += (f'Tetikleyici başına algılama olasılığı Parkfield\'da ölçülen ŝ = {say(s_hat)} ise n tetikleyicide hiç '
                  f'görülmeme olasılığı (1 − ŝ)^n_açık = {say((1 - s_hat) ** n_acik, 3)} (n_açık = {n_acik}) olur. ')
    else:
        c += ('Bu tarama Parkfield türü bir kaynağı dışlamaz, yalnız A90(S_k)\'nın üstündeki tremoru dışlar. '
              'Parkfield türü kaynak bu gürültüde görülemezdi. ')
    c += 'Bu cümle deprem olasılığı hakkında hiçbir şey söylemez.'
    if b_prime:
        c += ' (K1c yalnız belirsiz geçti)'
    return c


# ====================================================================== algılama: TR-7 §6.0–§6.5, madde 3 = K5
def k5_ist(x, parcalar, maske, Q):
    """§4.2 Uygulama: tr7b_yapay2.K5 değiştirilmeden çağrılır (Q: eksen dizinleri [a, b))."""
    return bool(Y2.K5(x, parcalar, maske, Q))


def q_dogrusu_var(x, maske, Q):
    """Ö-h (bilgi): Q'da L_d − m_d > 4σ_d olan kayıtlı, maskesiz saniye ≥ 30 mu (`_k1_kalinti`'nin şartı)."""
    q = np.zeros(len(x['L']), bool)
    q[max(0, Q[0]):max(0, Q[1])] = True
    with np.errstate(invalid='ignore'):
        q &= ~maske & np.isfinite(x['L']) & np.isfinite(x['Ld']) & (x['Ld'] - x['md'] > K.KSIG * x['sd'])
    return int(q.sum()) >= 30


def ayikla_k5(ist, kume, maske, Q):
    """TR-7 §6.5 madde 2, 3 (K5), 3a; toplama: istasyonların ≥ yarısı bayraklıysa küme atılır."""
    uy = kume['uyeler']
    yarim = len(uy) / 2
    pk = {k: [(a, b) for kk, a, b in kume['parcalar'] if kk == k] for k in uy}
    d = [K.darbe_ist(ist[k]['Cy'], pk[k]) for k in uy]
    s = [k5_ist(ist[k], pk[k], maske, Q) for k in uy]
    t = [K.taban_ist(ist[k], pk[k], maske) for k in uy]
    k0 = [K.sizinti_ist(ist[k], pk[k], maske) for k in uy]
    return dict(darbe=sum(d) >= yarim, sizinti=sum(s) >= yarim, taban=sum(t) >= yarim,
                k5_bayrak=int(sum(s)), k0_bayrak_bilgi=int(sum(k0)), n_ist=len(uy))


def pencere_algila_k5(ist, maske, Wb, Q):
    ks = K.kumeler(ist, maske, Wb)
    for k in ks:
        k['bayrak'] = ayikla_k5(ist, k, maske, Q)
        k['sag'] = not (k['bayrak']['darbe'] or k['bayrak']['sizinti'] or k['bayrak']['taban'])
    return ks


def kesisir(Ip, ara):
    """I′ = [a, b) (eksen, b dışlayıcı) ile kapsayıcı uçlu [c, d] aralığı kesişir mi (TR-7 K1 okuması O-35)."""
    return Ip[0] < ara[1] + 1 and Ip[1] > ara[0]


def pencere_sonucu(pv):
    """PencereVerisi → algılama satırı (bellekte; kümeler ayrıntısıyla). pv: dict(id, durum, n_gecen, ist [K.istasyon],
    maske, Wb, Q, K1b (eksen, kapsayıcı) ya da None, k0)."""
    sat = dict(id=pv['id'], durum=pv['durum'], n_gecen=pv.get('n_gecen'))
    if pv['durum'] != 'tarandi':
        sat.update(algilama=None, kumeler=[])
        return sat, []
    ist, maske = pv['ist'], pv['maske']
    ks = pencere_algila_k5(ist, maske, pv['Wb'], pv['Q'])
    for k in ks:
        k['k1b'] = pv.get('K1b') is not None and kesisir(k['Ip'], pv['K1b'])
        k['algilama_kumesi'] = k['sag'] and k['k1b']
    sat.update(
        algilama=any(k['algilama_kumesi'] for k in ks) if pv.get('K1b') is not None else None,
        W_algilama=any(k['sag'] for k in ks),
        kume_sayisi=len(ks),
        ayiklanan=dict(darbe=sum(k['bayrak']['darbe'] for k in ks), sizinti_K5=sum(k['bayrak']['sizinti'] for k in ks),
                       taban=sum(k['bayrak']['taban'] for k in ks)),
        q_dogrusu=[q_dogrusu_var(x, maske, pv['Q']) for x in ist],
        kumeler=[dict(Ip=[pv['k0'] + k['Ip'][0], pv['k0'] + k['Ip'][1]], I=[pv['k0'] + k['I'][0], pv['k0'] + k['I'][1]],
                      uyeler=[ist[i].get('ad') for i in k['uyeler']], bayrak=k['bayrak'], sag=k['sag'], k1b=k['k1b'],
                      n_cift_tutarli=k['n_cift_tutarli']) for k in ks])
    return sat, ks


# ====================================================================== modülasyon: TR-7 §6.4 + E-1
def e1_secim(adaylar, iz_orta=IZ_ORTA):
    """E-1 (aynen uygulanır). adaylar: [dict(ad, la, lo, kanallar=[dict(kod ('BHZ'…), konum, uygun_yanit (B/H bant,
    H alet, |H(0,02)|/|H(1)| ≥ 0,5, olay epoku), ortu_ok (W ve R ≥ %90, indirilen veri), v=dict(Z, R, T) ya da None)])].
    Uygun kanalı olan istasyonlardan iz köşe ortalamasına en yakını; onun uygun kanallarından önce HH, yoksa BH.
    Dönüş dict(ad, kanal, v: [dizi]) ya da None."""
    uygun = []
    for a in adaylar:
        ks = [c for c in a['kanallar'] if c['kod'][2] == 'Z' and c['kod'][0] in 'BH' and c['kod'][1] == 'H'
              and c['uygun_yanit'] and c['ortu_ok'] and c.get('v') is not None]
        if ks:
            uygun.append((K.hav(iz_orta[0], iz_orta[1], a['la'], a['lo']), a['ad'], a, ks))
    if not uygun:
        return None
    uygun.sort(key=lambda x: (x[0], x[1]))
    _, ad, a, ks = uygun[0]
    sec = sorted(ks, key=lambda c: (0 if c['kod'][0] == 'H' else 1, c.get('konum') or ''))[0]
    v = sec['v']
    cfs = [v['Z']] + ([v['R'], v['T']] if v.get('R') is not None and v.get('T') is not None else [])
    return dict(ad=ad, kanal=sec['kod'], konum=sec.get('konum', ''), v=cfs, bilesen=len(cfs),
                uzaklik_km=round(uygun[0][0], 2))


def modulasyon_kume(pv, ks_k, ref, rng, n_kay=K.MOD_N):
    """tr7_kosu.modulasyon ile aynı hesap (Lk = küme üyelerinin L medyanı, başvuru W'si, maske dışı). ref['W']:
    başvuru istasyonunun W'si (eksen). Dönüş dict(M, p) ya da None (ölçülemedi)."""
    if ref is None:
        return None
    W0, W1 = ref['W']
    if W1 - W0 <= 2 * K.MOD_KAY + 1:
        return None
    cfs = [K.faz_cos(np.asarray(v[W0:W1], dtype=np.float64)) for v in ref['v']
           if v is not None and np.isfinite(v[W0:W1]).any()]
    if not cfs:
        return None
    m = pv['maske'][W0:W1]
    Ls = np.array([pv['ist'][i]['L'][W0:W1] for i in ks_k['uyeler']])
    Ls[:, m] = np.nan
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning)
        Lk = np.nanmedian(Ls, axis=0)
    gec = np.isfinite(Lk) & ~m
    a = max(ks_k['I'][0], W0) - W0
    b = min(ks_k['I'][1], W1) - W0
    if b - a < 3:
        return None
    o = K.mod_istatistik(np.where(gec, Lk, 0.0), cfs, a, b, gec)
    say_ = 0
    for _ in range(n_kay):
        kk = int(rng.integers(K.MOD_KAY, len(cfs[0]) - K.MOD_KAY))
        say_ += K.mod_istatistik(np.where(gec, Lk, 0.0), [np.roll(c, kk) for c in cfs], a, b, gec) >= o
    return dict(M=round(o, 4), p=(1 + say_) / (n_kay + 1), bilesen=len(cfs))


# ====================================================================== (b′), A_PK
def b_prime_kume(Ip0_epoch, e1_sonlar, cekirdek):
    i_ = any(0 <= Ip0_epoch - e <= BPRIME_MASKE_S for e in e1_sonlar)
    ii = any(BPRIME_FAZ[0] <= Ip0_epoch - v <= BPRIME_FAZ[1] for v in cekirdek)
    return i_ or ii


def a_kume(pv, k):
    v = []
    for i in k['uyeler']:
        x = pv['ist'][i]
        a = K.kestirici_ist(x, k['Ip'], pv['maske'])
        if a is not None:
            v.append(a * K.r_hiposantr(x['la'], x['lo'], 'PK') / K.MDA_DERIN * pv.get('birim_nm', 1e9))
    return float(np.median(v)) if v else None


# ====================================================================== MDA özeti (TR-7 §7.4)
def mda_ozeti(denemeler):
    if not denemeler:
        return K.mda_ozet([0.0] * len(K.A_BASAMAK), 0)
    P = [float(np.mean([d['alg'][j] for d in denemeler])) for j in range(len(K.A_BASAMAK))]
    out = K.mda_ozet(P, len(denemeler))
    out['P'] = [round(x, 4) for x in P]
    return out


class k5_mda_baglami:
    """MDA'nın algılaması da K5 ile (TR-7c'nin algılayıcısı): K.mda_deneme → K.pencere_algila → K.ayikla çağrısı
    bu bağlamda ayikla_k5'e (pencerenin Q'suyla) yönlendirilir; çıkışta eski hâline döner (O-17). Dosya değişmez."""

    def __init__(self, Q):
        self.Q = Q

    def __enter__(self):
        self.eski = K.ayikla
        Q = self.Q

        def _ayikla(ist, kume, maske, yanlis=False):
            return ayikla_k5(ist, kume, maske, Q)
        K.ayikla = _ayikla
        return self

    def __exit__(self, *a):
        K.ayikla = self.eski
        return False


# ====================================================================== kaynak arayüzü
class Kaynak:
    """Pencere verisi sağlayıcısı. Yapay sınama bellekte bir alt sınıf kurar; gerçek veri yalnız GercekKaynak'tadır."""
    gercek = False

    def birimler(self):
        raise NotImplementedError

    def negatifler(self):
        raise NotImplementedError

    def pencere(self, desc):
        raise NotImplementedError

    def lp_adaylari(self, desc, pv):
        raise NotImplementedError

    def mda(self, desc, pv, rng, n_bas):
        raise NotImplementedError

    def b_prime_girdisi(self, desc, pv):
        return [], []


# ====================================================================== durum, kilit, yazım
def json_yaz(yol, nesne, kip='w'):
    metin = json.dumps(nesne, ensure_ascii=False, indent=1, default=_jv) + '\n'
    if kip == 'x':
        with open(yol, 'x', encoding='utf-8') as f:
            f.write(metin)
        return
    tmp = yol + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(metin)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, yol)


def _jv(o):
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (dt.datetime, dt.date)):
        return o.isoformat()
    if isinstance(o, (set, tuple)):
        return list(o)
    raise TypeError(type(o))


def satir_ekle(yol, nesne):
    with open(yol, 'a', encoding='utf-8') as f:
        f.write(json.dumps(nesne, ensure_ascii=False, sort_keys=True, default=_jv) + '\n')
        f.flush()
        os.fsync(f.fileno())


def jsonl_oku(yol):
    if not os.path.exists(yol):
        return []
    with open(yol, encoding='utf-8') as f:
        return [json.loads(s) for s in f if s.strip()]


def durum_isle(dizin, asama, durum, dosyalar=()):
    """Ö-b: durum dosyası yalnız 'başladı / tamamlandı / hata' ve dosya sha256'larını taşır; sayı yazılmaz."""
    y = os.path.join(dizin, DURUM_AD)
    d = _json(y) if os.path.exists(y) else dict(asamalar={})
    d['asamalar'][asama] = dict(durum=durum, zaman=dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'),
                                sha256={os.path.basename(f): sha256_dosya(f) for f in dosyalar if os.path.exists(f)})
    json_yaz(y, d)
    return d


# ====================================================================== K1c koşusu (gerçek ve yapay ortak çekirdek)
def negatif_turu(kaynak, dizin, ayar):
    """Rastgele negatif pencereler: algılama (W'nin herhangi bir yerinde), f_PK, N_PK, MDA (pencere başına 3
    başlangıç, üreteç default_rng(20261112 + 2), pencereler verilen sırayla). Sürdürülebilir (jsonl)."""
    yol = os.path.join(dizin, 'tr7c_negatif.jsonl')
    yazili = {r['id']: r for r in jsonl_oku(yol)}
    durum = None
    for r in yazili.values():
        if r.get('rng_sonra') is not None:
            durum = r['rng_sonra']
    rng = np.random.default_rng(K.MDA_TOHUM)
    if durum is not None:
        rng.bit_generator.state = durum
    for desc in kaynak.negatifler():
        if desc['id'] in yazili:
            continue
        pv = kaynak.pencere(desc)
        sat, _ = pencere_sonucu(pv)
        sat.update(tur='neg', olay=desc.get('olay'), sira=desc.get('sira'))
        if sat['durum'] == 'tarandi' and not sat['W_algilama']:
            with k5_mda_baglami(pv['Q']):
                sat['mda'] = kaynak.mda(desc, pv, rng, ayar.mda_bas)
            sat['rng_sonra'] = json.loads(json.dumps(rng.bit_generator.state))
        satir_ekle(yol, sat)
        yazili[desc['id']] = sat
    return list(yazili.values())


def algilama_turu(kaynak, dizin):
    """Önce N birimleri, sonra P, sonra bilgi satırları (§10 madde 6). Sürdürülebilir (jsonl)."""
    yol = os.path.join(dizin, 'tr7c_algilama.jsonl')
    yazili = {r['id']: r for r in jsonl_oku(yol)}
    sira = {'N': 0, 'P': 1, 'B': 2, 'Nayri': 3}
    bs = sorted(kaynak.birimler(), key=lambda b: (sira[b['sinif']], b['t0']))
    for b in bs:
        if b['id'] in yazili:
            continue
        pv = kaynak.pencere(b)
        sat, _ = pencere_sonucu(pv)
        sat.update(sinif=b['sinif'], t0=b['t0'], genlik4=b.get('genlik4', False))
        satir_ekle(yol, sat)
        yazili[b['id']] = sat
    return yazili


def taranan_mi(b, sat):
    """Z2: ≥ 3 liste istasyonu (TR-7 §4.2 örtüsü, n_gecen) ve K1b'nin E1'den sonra ≥ %50'si açık (USTVERI'de
    dondurulmuş pay; yoksa pencerenin kendi E1 payı)."""
    if sat['durum'] != 'tarandi':
        return False
    pay = b.get('K1b_acik_pay')
    if pay is None:
        pay = sat.get('K1b_acik_pay_pencere', 1.0)
    return pay >= 0.5


def modulasyon_turu(kaynak, birimler, ayar):
    """§4.1 yazarın seçimi + D-9: üreteç default_rng(20261112 + 3) yeni örnek; kümeler birimler T0 sırasıyla (P ve N
    birlikte), birim içinde I′ başı sırasıyla. Ölçülen: algılama kümeleri (sağ çıkan ve K1b ile kesişen). Dönüş
    {birim: dict(ref, kumeler=[dict(Ip, M, p)])}."""
    rng = np.random.default_rng(MOD_TOHUM_PK)
    out = {}
    for b in sorted([b for b in birimler if b['sinif'] in ('P', 'N')], key=lambda b: b['t0']):
        pv = kaynak.pencere(b)
        if pv['durum'] != 'tarandi':
            out[b['id']] = dict(ref=None, kumeler=[], durum='taranmadı')
            continue
        _, ks = pencere_sonucu(pv)
        alg = sorted([k for k in ks if k['algilama_kumesi']], key=lambda k: (k['Ip'][0], k['Ip'][1]))
        ref = e1_secim(kaynak.lp_adaylari(b, pv))
        if ref is not None:
            ref = dict(ref, W=pv['ref_W'](ref['ad']) if callable(pv.get('ref_W')) else pv['Wb'])
        km = []
        for k in alg:
            r = modulasyon_kume(pv, k, ref, rng, ayar.mod_n) if ref is not None else None
            km.append(dict(Ip=[pv['k0'] + k['Ip'][0], pv['k0'] + k['Ip'][1]], M=None if r is None else r['M'],
                           p=None if r is None else r['p']))
        out[b['id']] = dict(ref=None if ref is None else dict(ad=ref['ad'], kanal=ref['kanal'], bilesen=ref['bilesen'],
                                                              uzaklik_km=ref['uzaklik_km']), kumeler=km)
    return out


def k1c_hesap(kaynak, birimler, neg, alg, mod):
    """Z2–Z4, D-1, D-7–D-10, E-2, (b′), A_PK, ŝ ve bilgi satırları. Saf hesap (veri yalnız argümanlarda + (b′) ve A_PK
    için pencereler)."""
    ana = [b for b in birimler if b['sinif'] in ('P', 'N')]
    tar = {b['id']: taranan_mi(b, alg[b['id']]) for b in ana}
    P = [b for b in ana if b['sinif'] == 'P']
    N = [b for b in ana if b['sinif'] == 'N']
    n_P = sum(tar[b['id']] for b in P)
    n_N = sum(tar[b['id']] for b in N)
    alg_P = [b for b in P if tar[b['id']] and alg[b['id']]['algilama']]
    X_P = len(alg_P)
    X_N = sum(1 for b in N if tar[b['id']] and alg[b['id']]['algilama'])
    negs = [r for r in neg if r['durum'] == 'tarandi'][:NEG_N_MAX]
    N_PK = len(negs)
    f_PK = sum(1 for r in negs if r['W_algilama'])
    den = [d for r in negs if not r['W_algilama'] for d in (r.get('mda') or [])]
    mda = mda_ozeti(den)
    A90 = mda['A90']

    def olc(bid):
        ks = mod.get(bid, {}).get('kumeler', [])
        return any(k['M'] is not None for k in ks), any(k['p'] is not None and k['p'] <= K.MOD_ESIK for k in ks)
    M_olc = sum(olc(b['id'])[0] for b in alg_P)
    M_mod = sum(olc(b['id'])[1] for b in alg_P)
    k_kosu = sum(1 for b in P if mod.get(b['id'], {}).get('ref') is not None)
    dal, alt, s = k1c_dal(n_P, n_N, X_P, X_N, f_PK, N_PK, M_olc, M_mod, A90)
    mod_gecti = X_P > 0 and M_mod >= math.ceil(X_P / 2)
    g4 = [b for b in N if b['genlik4']]
    g4_olc = [b for b in g4 if tar[b['id']] and olc(b['id'])[0]]
    genlik = any(olc(b['id'])[1] for b in g4 if tar[b['id']])
    g4_olculemeyen = len(g4) - len(g4_olc)
    # (b′): algılama veren P olaylarının hepsinde bütün algılama kümeleri (i) ya da (ii) durumunda mı
    bp_olay = []
    a_olay, a_mod_olay, a_med_olay = [], [], []
    for b in alg_P:
        pv = kaynak.pencere(b)
        _, ks = pencere_sonucu(pv)
        e1s, cek = kaynak.b_prime_girdisi(b, pv)
        ak = [k for k in ks if k['algilama_kumesi']]
        bp_olay.append(all(b_prime_kume(pv['k0'] + k['Ip'][0], e1s, cek) for k in ak))
        av = [a_kume(pv, k) for k in ak]
        av2 = [a for a in av if a is not None]
        if av2:
            a_olay.append(max(av2))
            a_med_olay.append(float(np.median(av2)))
        mk = mod.get(b['id'], {}).get('kumeler', [])
        am = [a for a, k, m in zip(av, ak, sorted(mk, key=lambda x: x['Ip'][0])) if a is not None
              and m['p'] is not None and m['p'] <= K.MOD_ESIK]
        if am:
            a_mod_olay.append(max(am))
    b_prime = bool(alg_P) and all(bp_olay)
    etiket = dict(b_prime=b_prime, mod_gecti=mod_gecti, genlik=genlik, genlik_olculemeyen=g4_olculemeyen,
                  k_kosu=k_kosu)
    cumle = k1c_cumle(dal, alt, n_P, n_N, X_P, A90, etiket)
    # bilgi satırları
    bilgi = {}
    Pk = [b for b in P if b['id'] != KURIL2007]
    n_Pk = sum(tar[b['id']] for b in Pk)
    X_Pk = sum(1 for b in Pk if tar[b['id']] and alg[b['id']]['algilama'])
    M_modk = sum(olc(b['id'])[1] for b in alg_P if b['id'] != KURIL2007)
    bilgi['Kuril2007_cikarilmis_Z3'] = z3(n_Pk, n_N, X_Pk, X_N, f_PK, N_PK, M_modk)
    bilgi['genlik4_algilama'] = {b['id']: alg[b['id']]['algilama'] for b in g4}
    # O-37: "modülasyonu ölçülemeyen" = §5 madde 4'ün ölçülebilir olay tanımını sağlamayan (algılama kümesi yok da dahil)
    bilgi['genlik4_olculemeyen_neden'] = {
        b['id']: ('taranmadı' if not tar[b['id']] else 'ölçüldü' if olc(b['id'])[0] else
                  'algılama kümesi yok' if not alg[b['id']]['algilama'] else
                  'başvuru kanalı yok' if mod.get(b['id'], {}).get('ref') is None else 'M hesaplanamadı')
        for b in g4}
    bilgi['X_N_bolu_n_N'] = X_N / n_N if n_N else None
    bilgi['X_P_bolu_n_P'] = X_P / n_P if n_P else None
    ayri = [r for r in alg.values() if r.get('sinif') == 'Nayri']
    if ayri:
        vb = next((b for b in N if b['id'] == VANUATU_BIRIM), None)
        if vb is not None and tar.get(vb['id']):
            n2 = n_N + 1
            x2 = X_N - int(bool(alg[vb['id']]['algilama'])) + sum(int(bool(r['algilama'])) for r in ayri)
            bilgi['N27_N28_ayri_Z3_iii'] = dict(n_N=n2, X_N=x2, fisher_p=fisher_tek(X_P, n_P, x2, n2),
                                                 iii=fisher_tek(X_P, n_P, x2, n2) <= FISHER_ALFA)
    bilgi['Q_dogrusu_kuruldu_mu'] = {k: (sum(v.get('q_dogrusu') or []), len(v.get('q_dogrusu') or []))
                                     for k, v in alg.items()}
    bilgi['N_modulasyon_p'] = {b['id']: [k['p'] for k in mod.get(b['id'], {}).get('kumeler', [])] for b in N}
    bilgi['k_nP_icinde'] = sum(1 for b in P if tar[b['id']] and mod.get(b['id'], {}).get('ref') is not None)
    A_PK = float(np.median(a_olay)) if a_olay else None
    bilgi['A_PK_yalniz_modulasyonlu'] = float(np.median(a_mod_olay)) if a_mod_olay else None
    bilgi['A_PK_olay_medyan_kume'] = float(np.median(a_med_olay)) if a_med_olay else None
    sh = s_sapka(X_P, n_P, X_N, n_N)
    sh_alt = None
    if n_P and n_N:
        q = X_N / n_N
        sh_alt = max(0.0, (cp_alt(X_P, n_P) - q) / (1 - q)) if q < 1 else 0.0
    return dict(dal=dal, alt=alt, cumle=cumle, marmara_acilir=marmara_acilir(dal),
                var_verilebilir=var_verilebilir(dal, etiket), etiket=etiket,
                n_P=n_P, n_N=n_N, X_P=X_P, X_N=X_N, f_PK=f_PK, N_PK=N_PK, M_olc=M_olc, M_mod=M_mod,
                z3=s, A90_PK=A90, A50_PK=mda['A50'], mda_deneme=mda['n_deneme'], A_PK=A_PK, s_sapka=sh,
                s_sapka_alt=sh_alt, bilgi=bilgi, modulasyon=mod)


def k1c_kos(kaynak, dizin=CIKTI, ayar=Ayar(), gercek=False, gunluk=print):
    """K1c'nin çekirdeği: negatifler → algılama (N, P) → modülasyon → Z3/Z4 → hüküm dosyası bir kez ('x').
    Kapı içeride: gerçek kip, gerçek kaynak ya da gerçek çıktı dizini → kapı (dondurulmamışsa SystemExit)."""
    if gercek or kaynak.gercek or gercek_yol_mu(dizin):
        gercek_kapi('k1c_kos')
        if ayar != Ayar() or not kaynak.gercek or not gercek_yol_mu(dizin):
            raise GercekKipReddedildi('GERÇEK KİP REDDEDİLDİ: gerçek kipte ayar ön kayıttaki gibi, kaynak ve dizin '
                                      'gerçek olmalı')
    d2 = d2_denetle()
    girdi = girdi_denetimi()
    os.makedirs(dizin, exist_ok=True)
    hy = os.path.join(dizin, HUKUM_AD)
    if os.path.exists(hy):
        gunluk('KİLİT: K1c hüküm dosyası var; koşu bir kez yapılır. Hiçbir şey hesaplanmadı.')
        return _json(hy)
    durum_isle(dizin, 'K1c-negatif', 'başladı')
    neg = negatif_turu(kaynak, dizin, ayar)
    durum_isle(dizin, 'K1c-negatif', 'tamamlandı', [os.path.join(dizin, 'tr7c_negatif.jsonl')])
    durum_isle(dizin, 'K1c-algılama', 'başladı')
    alg = algilama_turu(kaynak, dizin)
    birimler = kaynak.birimler()
    mod = modulasyon_turu(kaynak, birimler, ayar)
    h = k1c_hesap(kaynak, birimler, neg, alg, mod)
    h.update(d2_sha256=d2, girdi_sha256=girdi, kod_sha256=kod_sha(), gercek_kip=bool(kaynak.gercek),
             ayar=dataclasses.asdict(ayar),
             tohum=dict(modulasyon=MOD_TOHUM_PK, mda=K.MDA_TOHUM, negatif_secim=NEG_TOHUM))
    json_yaz(hy, h, kip='x')
    durum_isle(dizin, 'K1c-algılama', 'tamamlandı', [os.path.join(dizin, 'tr7c_algilama.jsonl'), hy])
    return h


# ====================================================================== rastgele negatif pencere seçimi (TR-7 §7.3)
def negatif_sec(rng, T0, R0, W1, kat_m65, tz='America/Los_Angeles', n=NEG_SAYI):
    """TR-7 §7.3 (tr7_negatif_pencere.py `sec` ile aynı kural): p1 = perm(±1–30), p2 = perm(±31–60) her zaman çekilir;
    (i) [R0 − 3 sa, W1] kaydırılmışta M ≥ 6,5 yok, (ii) W1 < 2026, (iii) yerel gün türü, (iv) UTC farkı R0 ve W1'de."""
    from zoneinfo import ZoneInfo
    z = ZoneInfo(tz)
    utc = dt.timezone.utc

    def yerel(t):
        x = t.replace(tzinfo=utc).astimezone(z)
        return ('hafta_sonu' if x.weekday() >= 5 else 'hafta_ici'), x.utcoffset()
    gt, _ = yerel(T0)
    _, fr = yerel(R0)
    _, fw = yerel(W1)
    p1 = rng.permutation([d for d in range(-30, 31) if d != 0])
    p2 = rng.permutation([d for d in range(-60, 61) if abs(d) > 30])
    out = []
    for d in list(p1) + list(p2):
        k = dt.timedelta(days=int(d))
        r0, w1, t0 = R0 + k, W1 + k, T0 + k
        if any(r0 - dt.timedelta(hours=3) <= e <= w1 for e in kat_m65):
            continue
        if w1 >= K.SON_AN:
            continue
        if yerel(t0)[0] != gt or yerel(r0)[1] != fr or yerel(w1)[1] != fw:
            continue
        out.append(int(d))
        if len(out) == n:
            break
    return out


# ====================================================================== GERÇEK VERİ KATMANI (yalnız kapı açıkken)
class GercekOrtam:
    """tr7_kosu.Ortam ile aynı arayüz; her ağ ve depo dışı dosya erişimi kapıdan geçer. Çıktı dosya adları tr7c_."""

    def __new__(cls, *a, **kw):
        gercek_kapi('GercekOrtam')
        return super().__new__(cls)

    def __init__(self, zarf=ZARF_KOK, log=print):
        import tr7_kosu as T
        self.T = T
        self.o = T.Ortam(tr7=CIKTI, depo=DEPO, zarf=zarf, dondurulmus={}, log=log)
        self.tr7, self.depo, self.zarf, self.log = CIKTI, DEPO, zarf, log
        self.servis = self.katalog = None
        self.uyku, self.aralik, self.bekle_429, self.yeniden_bekle = self.o.uyku, self.o.aralik, self.o.bekle_429, \
            self.o.yeniden_bekle
        self.dondurulmus = {}
        self.git_dogrula = True

    def yol(self, ad):
        if ad == 'TR7_KOSU_DURUM.json':
            ad = DURUM_AD
        elif ad.startswith('tr7_'):
            ad = 'tr7c_' + ad[4:]
        return os.path.join(CIKTI, ad)

    def zyol(self, *p):
        gercek_kapi('zarf deposu')
        return os.path.join(self.zarf, *p)

    def hyol(self, *p):
        gercek_kapi('ham veri')
        return os.path.join(os.environ.get('TR7_HAM_DIZIN') or os.path.join(self.zarf, 'ham'), *p)

    def istemci(self):
        gercek_kapi('ağ istemcisi')
        return self.T.I.Istemci(aralik=self.aralik, bekle_429=self.bekle_429, uyku=self.uyku)


def _sayim_istasyonlari(evid, sinif='liste'):
    """tr7b_sayim.json: olayın sınıf istasyonları ve TR-7 §3.2 önceliğiyle (HHZ > BHZ > EHZ > SHZ; kuyuda listedeki
    sıra) W ve R örtüsü ≥ 0,90 olan ilk düşey kanal (O-8). Dönüş {(ag, ist): (konum, kanal)}."""
    d = _json(os.path.join(TR7B, 'tr7b_sayim.json'))
    o = next(x for x in d['olaylar'] if x['evid'] == evid)
    onc = {'HHZ': 0, 'BHZ': 1, 'EHZ': 2, 'SHZ': 3}
    out = {}
    for k, v in o['istasyonlar'].items():
        if v['sinif'] != sinif:
            continue
        ks = [c for c in v['kanallar'] if c['ortu_W'] >= 0.9 and c['ortu_R'] >= 0.9]
        if not ks:
            continue
        c = sorted(ks, key=lambda c: (onc.get(c['cha'], 9), c['loc']))[0]
        ag, ist = k.split('.', 1)
        out[(ag, ist)] = (c['loc'], c['cha'])
    return out


def dunya_kur(birimler, negatif_kaydirma=None):
    """tr7_kosu biçiminde D: pencereler ('tet' = kör birimler, 'neg' = kaydırılmış), istasyonlar iz_sira sırasıyla,
    E1 satırları (USTVERI). Yalnız repo dosyaları; ağ yok, veri yok."""
    import csv
    ol = olaylar()
    with open(os.path.join(TR7, 'tr7_parkfield_liste.csv'), encoding='utf-8', newline='') as f:
        pk = {(r['ag'], r['istasyon']): r for r in csv.DictReader(f)}
    pen, e1 = {}, []
    for b in birimler:
        evs = [ol[e] for e in b['evids']]
        sec = _sayim_istasyonlari(b['evids'][0])
        for e in b['evids'][1:]:
            s2 = _sayim_istasyonlari(e)
            sec = {k: v for k, v in sec.items() if k in s2}
        p = dict(id=f"pk|{b['id']}", tur='tet', bolge='Parkfield', birim=b['id'], tetikleyici=b['evids'][0],
                 t0=evs[0]['t0'], kayma=0, seg={'PK': []}, ist={}, tani=[], ev=(evs[0]['la'], evs[0]['lo']))
        for key in sorted(sec, key=lambda k: int(pk[k]['iz_sira']) if k in pk and pk[k]['iz_sira'] else 10 ** 6):
            if key not in pk:
                continue
            r = pk[key]
            la, lo = float(r['enlem']), float(r['boylam'])
            w = [K.pencere_hesapla(e['t0'], K.hav(e['la'], e['lo'], la, lo)) for e in evs]
            p['ist'][key] = dict(ag=key[0], istasyon=key[1], konum=sec[key][0], z_kanal=sec[key][1], la=la, lo=lo,
                                 d_km=K.hav(evs[0]['la'], evs[0]['lo'], la, lo), R=w[0]['R'],
                                 W=(w[0]['W'][0], w[-1]['W'][1]), kaynak='', parkfield=True)
            p['seg']['PK'].append(key)
        pen[p['id']] = p
        for m in b.get('maskelenen') or []:
            e1.append(dict(tetikleyici=b['evids'][0], segment='PK', olay=m['olay'], M=str(m['M']), faz=m['faz'],
                           varis=m['varis']))
    for e, ds in (negatif_kaydirma or {}).items():
        b = next(x for x in birimler if e in x['evids'])
        for i, d in enumerate(ds, 1):
            base = pen[f"pk|{b['id']}"]
            pid = f'pkneg|{e}|{i}'
            pen[pid] = dict(base, id=pid, tur='neg', t0=base['t0'] + dt.timedelta(days=d), kayma=d, sira=i, tani=[],
                            seg=dict(base['seg']), ist={k: dict(x, R=(x['R'][0] + dt.timedelta(days=d),
                                                                      x['R'][1] + dt.timedelta(days=d)),
                                                                 W=(x['W'][0] + dt.timedelta(days=d),
                                                                    x['W'][1] + dt.timedelta(days=d)))
                                                         for k, x in base['ist'].items()})
    for p in pen.values():
        for x in p['ist'].values():
            K.sinir_denetle(x['W'][1] + dt.timedelta(seconds=K.DOLGU_S))
    return dict(girdi={}, olay={}, pen=pen, e1=e1, neg=[], ist_csv={})


class GercekKaynak(Kaynak):
    """Gerçek zarf deposundan pencere verisi. Kurucu ve her okuma kapıdan geçer."""
    gercek = True

    def __init__(self, go, D, man, birimler, derinlik):
        gercek_kapi('GercekKaynak')
        self.go, self.D, self.man, self._b, self.derinlik = go, D, man, birimler, derinlik
        self._onbellek = {}

    def birimler(self):
        return self._b

    def negatifler(self):
        ps = sorted([p for p in self.D['pen'].values() if p['tur'] == 'neg'],
                    key=lambda p: (self.D['pen'][f"pk|{self._birim_of(p)}"]['t0'], p['sira']))
        return [dict(id=p['id'], olay=p['tetikleyici'], sira=p['sira'], pid=p['id']) for p in ps]

    def _birim_of(self, p):
        return p['birim']

    def pencere(self, desc):
        gercek_kapi('pencere')
        pid = desc.get('pid') or f"pk|{desc['id']}"
        if pid in self._onbellek:
            return self._onbellek[pid]
        T = self.go.T
        p = self.D['pen'][pid]
        kay = T.zarf_kayitlari(self.go).get(pid, {})
        ws = T.ws_kur(self.go, self.D, self.man, p, 'PK', kay)
        pv = dict(id=desc['id'], durum=ws['durum'], n_gecen=ws['n_gecen'], k0=ws['k0'], n=ws['n'], ws=ws, p=p)
        if ws['durum'] == 'tarandi':
            t0 = K.epoch(p['t0'])
            from obspy.geodetics import locations2degrees
            dg = locations2degrees(p['ev'][0], p['ev'][1], *IZ_ORTA)
            tp, _ = K.taup_varislar(self.derinlik[p['tetikleyici']], dg)
            Q = (int(math.floor(t0 + tp)) - ws['k0'], ws['Wb'][0])
            k1b = None
            if p['tur'] == 'tet':
                b = next(x for x in self._b if x['id'] == p['birim'])
                k1b = (int(b['K1b'][0]) - ws['k0'], int(b['K1b'][1]) - ws['k0'])
            for x, k in zip(ws['ist'], ws['kul']):
                x['la'], x['lo'] = p['ist'][k]['la'], p['ist'][k]['lo']
            pv.update(ist=ws['ist'], maske=ws['maske'], Wb=ws['Wb'], Q=Q, K1b=k1b,
                      # TR-7 §6.4 aynen (tr7_kosu.modulasyon): başvuru istasyonunun KENDİ W'si (eksen_dilim)
                      ref_W=lambda ad, p=p, k0=ws['k0']: T.eksen_dilim(p['ist'][tuple(ad.split('.', 1))], k0)[1])
        self._onbellek[pid] = pv
        return pv

    def lp_adaylari(self, desc, pv):
        """E-1: manifestteki lp adayları (uzaklık sırası) ve indirilen lp zarfları (tr7c_lp_sha256.jsonl)."""
        gercek_kapi('lp')
        T = self.go.T
        out = []
        kayit = {(r['pencere'], r['ad'], r['kanal']): r for r in jsonl_oku(self.go.yol('tr7c_lp_sha256.jsonl'))}
        for a in self.man.get('lp_aday', {}).get(f"pk|{desc['id']}", []):
            ks = []
            for c in a['kanallar']:
                r = kayit.get((f"pk|{desc['id']}", a['ad'], c['kod']))
                v = None
                ok = bool(r and r.get('dusme') is None and r.get('sha256'))
                if ok:
                    z = T.I.zarf_oku(self.go.zyol(r['dosya']), r['sha256'])
                    v = dict(Z=z['vZ'].astype(float), R=z['vR'].astype(float) if np.isfinite(z['vR']).any() else None,
                             T=z['vT'].astype(float) if np.isfinite(z['vT']).any() else None)
                ks.append(dict(kod=c['kod'], konum=c['konum'], uygun_yanit=c['uygun_yanit'], ortu_ok=ok, v=v))
            out.append(dict(ad=a['ad'], la=a['la'], lo=a['lo'], kanallar=ks))
        return out

    def mda(self, desc, pv, rng, n_bas):
        gercek_kapi('MDA')
        T = self.go.T
        veri, hn, rk = T.mda_girdisi(self.go, self.man, pv['p'], pv['ws'], 'K1c-negatif')
        return K.mda_deneme(pv['ist'], veri, hn, rk, pv['maske'], pv['Wb'], pv['k0'], rng, n_bas=n_bas)

    def b_prime_girdisi(self, desc, pv):
        gercek_kapi('b_prime')
        from obspy.geodetics import locations2degrees
        p = pv['p']
        ol = self.go.T.e1_olay_listesi(self.D, self.man, p, 'PK')
        sonlar = self.go.T.e1_bireysel_sonlar(ol)
        dg = locations2degrees(p['ev'][0], p['ev'][1], *IZ_ORTA)
        cf = K.cekirdek_fazlari(self.derinlik[p['tetikleyici']], dg)
        return sonlar, sorted(K.epoch(p['t0']) + t for v in cf.values() for t in v)


def asama_kos(asama, surdur=False):
    """Gerçek aşamalar. Kapı ilk satırda. Bu sürümde (koşu dondurması yok) her çağrı burada reddedilir."""
    gercek_kapi(f'aşama {asama}')
    go = GercekOrtam()
    go.T.git_dogrula(go, asama)                     # durum dosyası 'başladı' ile commit + push edilmiş olmalı
    birim = birimler_kur()
    if asama == 'manifest':
        return asama_manifest(go, birim)
    man = _json(go.yol('tr7c_manifest.json'))
    D = dunya_kur(birim, man['negatif_kaydirma'])
    if asama == 'K1c-indirme':
        return asama_indirme(go, D, man)
    kay = GercekKaynak(go, D, man, birim, man['derinlik'])
    if asama == 'K1c-negatif':
        return negatif_turu(kay, CIKTI, Ayar())
    if asama == 'K1c-algılama':
        return k1c_kos(kay, CIKTI, Ayar(), gercek=True)
    raise Tr7cDur(f'bilinmeyen aşama: {asama}')


def asama_manifest(go, birim):
    """manifest: ComCat (tetikleyici kaydı ±60 sn M ≥ 7,0 en yakın — Ö-k; derinlik; M ≥ 6,5 negatif seçimi için),
    negatif kaydırmaları (TR-7 §7.3, default_rng(20261116 + 1), olaylar T0 sırasıyla), sonra tr7_kosu.asama_manifest
    (StationXML, yerel katalog, negatiflerin E1'i, indirme planı) ve E-1 lp adayları. Dalga formu YOK."""
    gercek_kapi('manifest')
    T = go.T
    cl = go.istemci()
    ol = olaylar()
    derinlik, kayit = {}, {}
    for e in sorted(set(x for b in birim for x in b['evids']) | set(NEG_OLAY), key=lambda x: ol[x]['t0']):
        t0 = ol[e]['t0']
        url = T.I.event_url('comcat', t0 - dt.timedelta(seconds=60), t0 + dt.timedelta(seconds=60), 0.0, 0.0, 180.0,
                            K.E1_M7)
        r = T._katalog_iste(cl, go.zyol('katalog'), 'comcat', url, f'tet|{e}')
        kat = T.katalog_ayristir('comcat', T._govde(go.zyol('katalog'), r))
        aday = sorted([k for k in kat if k['M'] is not None and k['M'] >= K.E1_M7
                       and abs(k['t0'] - K.epoch(t0)) <= 60], key=lambda k: abs(k['t0'] - K.epoch(t0)))
        if not aday:
            raise Tr7cDur(f'tetikleyicinin ComCat kaydı yok: {e}')
        derinlik[e] = aday[0]['derinlik']
        kayit[e] = dict(id=aday[0]['id'], sapma_s=round(aday[0]['t0'] - K.epoch(t0), 2))
    D0 = dunya_kur(birim)
    rng = np.random.default_rng(NEG_TOHUM)
    kayd = {}
    for e in sorted(NEG_OLAY, key=lambda x: ol[x]['t0']):
        b = next(x for x in birim if e in x['evids'])
        p = D0['pen'][f"pk|{b['id']}"]
        R0 = min(x['R'][0] for x in p['ist'].values())
        W1 = max(x['W'][1] for x in p['ist'].values())
        url = T.I.event_url('comcat', R0 - dt.timedelta(days=61, hours=3), W1 + dt.timedelta(days=61), 0.0, 0.0, 180.0,
                            6.5)
        r = T._katalog_iste(cl, go.zyol('katalog'), 'comcat', url, f'neg65|{e}')
        kat = [K.epoch_zaman(k['t0']) for k in T.katalog_ayristir('comcat', T._govde(go.zyol('katalog'), r))]
        kayd[e] = negatif_sec(rng, p['t0'], R0, W1, kat)
    D = dunya_kur(birim, kayd)
    man = T.asama_manifest(go, D)
    man.update(derinlik=derinlik, tetikleyici_kaydi=kayit, negatif_kaydirma=kayd, lp_aday=lp_adaylari_manifest(go, D))
    json_yaz(go.yol('tr7c_manifest.json'), man, kip='x')
    return dict(durum='tamamlandı')


def lp_adaylari_manifest(go, D):
    """E-1 adayları: her kör birimde liste istasyonlarının HH?/BH? kanalları (StationXML, olay epoku); düşey kanal B/H
    bant, H alet, |H(0,02)|/|H(1)| ≥ 0,5; aynı konum ve bantta iki yatay. Uzaklık sırasıyla."""
    gercek_kapi('lp adayları')
    T = go.T
    cl = go.istemci()
    out = {}
    for pid, p in D['pen'].items():
        if p['tur'] != 'tet':
            continue
        ad = []
        for key, x in p['ist'].items():
            url = T.I.station_url('ncedc', key[0], key[1], '*', ['HH?', 'BH?'], x['R'][0] - dt.timedelta(days=1),
                                  min(x['W'][1] + dt.timedelta(days=1), T.I.KATALOG_SON))
            yol = go.zyol('stationxml', f'lp.{key[0]}.{key[1]}.xml')
            os.makedirs(os.path.dirname(yol), exist_ok=True)
            r = cl.iste('ncedc', url.replace('loc=%2A', 'loc=*'), hedef=yol)
            if r['durum'] != 'tamam':
                continue
            inv = T.I.oku_stationxml(yol)
            ks = []
            for net in inv.select(time=__import__('obspy').UTCDateTime(K.epoch(p['t0']))):
                for st in net:
                    for c in st:
                        if c.code[2] != 'Z' or c.code[0] not in 'BH' or c.code[1] != 'H':
                            continue
                        oz = T.I.yanit_ozeti(inv, key[0], key[1], c.location_code, c.code, p['t0'])
                        ks.append(dict(kod=c.code, konum=c.location_code, uygun_yanit=bool(oz.get('pgv_uygun')),
                                       yatay=T.yatay_sec(inv, key[0], key[1], c.location_code, c.code[:2], p['t0'])))
            if ks:
                ad.append(dict(ad=f'{key[0]}.{key[1]}', la=x['la'], lo=x['lo'], kanallar=ks,
                               km=K.hav(IZ_ORTA[0], IZ_ORTA[1], x['la'], x['lo'])))
        out[pid] = sorted(ad, key=lambda a: (a['km'], a['ad']))
    return out


def asama_indirme(go, D, man):
    """K1c-indirme: tr7_kosu indir–zarfla–sil motoru (P, N, bilgi birimleri lp ile; negatifler ham tutulur), sonra
    E-1 lp adayları uzaklık sırasıyla ilk uygun istasyon bulunana dek (HH ve BH ayrı istek)."""
    gercek_kapi('indirme')
    T = go.T
    tet = sorted([p for p in D['pen'].values() if p['tur'] == 'tet'], key=lambda p: p['t0'])
    neg = sorted([p for p in D['pen'].values() if p['tur'] == 'neg'], key=lambda p: (p['t0'], p['id']))
    oz1 = T.indir_kume(go, D, man, 'K1c-indirme', tet, lp=False, ham_tut=False)
    oz2 = T.indir_kume(go, D, man, 'K1c-negatif', neg, lp=False, ham_tut=True)
    lp_indir(go, D, man)
    return dict(tet=oz1, neg=oz2)


def lp_indir(go, D, man):
    gercek_kapi('lp indirme')
    T = go.T
    yol_j = go.yol('tr7c_lp_sha256.jsonl')
    yazili = {(r['pencere'], r['ad'], r['kanal']) for r in jsonl_oku(yol_j)}
    for pid, adaylar in man['lp_aday'].items():
        p = D['pen'][pid]
        for a in adaylar:
            gecti = False
            for c in sorted([c for c in a['kanallar'] if c['uygun_yanit']], key=lambda c: (c['kod'][0] != 'H',)):
                if (pid, a['ad'], c['kod']) in yazili:
                    continue
                ag, ist = a['ad'].split('.', 1)
                lp_p = dict(p, id=f"{pid}|lp|{c['konum']}.{c['kod']}",
                            ist={(ag, ist): dict(p['ist'][(ag, ist)], konum=c['konum'], z_kanal=c['kod'])})
                kk = (ag, ist)
                x = lp_p['ist'][kk]
                q = dict(ag=ag, istasyon=ist, konum=c['konum'], kanallar=[c['kod']] + c['yatay'],
                         bas=(x['R'][0] - dt.timedelta(seconds=K.DOLGU_S)).isoformat(),
                         son=(x['W'][1] + dt.timedelta(seconds=K.DOLGU_S)).isoformat(), servis='ncedc')
                hedef = go.hyol('lp', lp_p['id'].replace('|', '_') + '.mseed')
                os.makedirs(os.path.dirname(hedef), exist_ok=True)
                url = T.I.dataselect_url('ncedc', ag, ist, c['konum'], q['kanallar'], q['bas'], q['son'])
                r = go.istemci().iste('ncedc', url, hedef=hedef)
                satir = dict(pencere=pid, ad=a['ad'], kanal=c['kod'], http=r['http'], bayt=r.get('bayt', 0),
                             dusme=None if r['durum'] == 'tamam' else r['durum'], sha256=None)
                if r['durum'] == 'tamam':
                    k0, n = T.pencere_ekseni(p)
                    pen = T.ist_pencere(x, k0, n)
                    inv = T.I.oku_stationxml(go.zyol('stationxml', f'lp.{ag}.{ist}.xml'))
                    oz = {k: T.I.yanit_ozeti(inv, ag, ist, c['konum'], k, x['W'][0]) for k in q['kanallar']}
                    from obspy.geodetics import gps2dist_azimuth
                    baz = gps2dist_azimuth(p['ev'][0], p['ev'][1], x['la'], x['lo'])[2]
                    rr = T.I.isle_istasyon_penceresi(hedef, inv, dict(ag=ag, istasyon=ist, konum=c['konum'],
                                                                      z_kanal=c['kod'], yatay=c['yatay'], ozet=oz,
                                                                      baz=baz), pen, lp=True)
                    satir['dusme'] = rr['dusme']
                    if rr['dusme'] is None:
                        zy = go.zyol('lp', lp_p['id'].replace('|', '_') + '.npz')
                        satir['sha256'] = T.I.zarf_yaz(zy, k0, dict(lp=rr['lp']), dict(pencere=pid, kanal=c['kod']))
                        satir['dosya'] = os.path.relpath(zy, go.zarf)
                        gecti = True
                    os.remove(hedef)
                satir_ekle(yol_j, satir)
            if gecti:
                break                                       # E-1: en yakın uygun istasyon bulundu


# ====================================================================== Marmara (yalnız K1c (b))
def marmara_kos(asama, dizin=CIKTI):
    """Ayrı komut. Sıra: kapı → K1c hüküm dosyası var ve dal (b) → (bu sürümde) TR-7 Marmara aşamalarının TR-7c
    bağlantısı YAZILMADI (O-30): K1c (b) çıkarsa ayrı kod ve kod incelemesi gerekir. Kapı ya da önkoşul kalırsa hiçbir
    şey açılmaz ve indirilmez."""
    gercek_kapi(f'Marmara {asama}')
    hy = os.path.join(dizin, HUKUM_AD)
    if not os.path.exists(hy):
        raise Tr7cDur('K1c hüküm dosyası yok: Marmara açılmaz')
    h = _json(hy)
    if not marmara_acilir(h.get('dal')):
        raise Tr7cDur(f"K1c dalı {h.get('dal')}: (b) dışında Marmara verisi indirilmez (Z4)")
    raise Tr7cDur('Marmara bağlantısı bu sürümde yazılmadı (O-30); K1c (b) sonrası ayrı kod ve inceleme')


# ====================================================================== komut satırı
def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    if a == ['kapi']:
        ok, neden = kosu_dondurulmus_mu()
        print(json.dumps(dict(acik=ok, neden=neden, kod_sha256=kod_sha(), d2=D2_SONUC), ensure_ascii=False, indent=1))
        return 0
    if a == ['durum']:
        y = os.path.join(CIKTI, DURUM_AD)
        print(open(y, encoding='utf-8').read() if os.path.exists(y) else 'durum dosyası yok')
        return 0
    if len(a) == 2 and a[0] == 'baslat':
        gercek_kapi(f'baslat {a[1]}')
        os.makedirs(CIKTI, exist_ok=True)
        durum_isle(CIKTI, a[1], 'başladı')
        print('durum dosyası yazıldı; commit + push edin, sonra `kos`.')
        return 0
    if len(a) >= 2 and a[0] == 'kos':
        asama_kos(a[1], surdur='--surdur' in a)
        return 0
    if len(a) == 2 and a[0] == 'marmara':
        marmara_kos(a[1])
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main())
