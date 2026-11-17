#!/usr/bin/env python3
"""TR-7c §9 Tohoku duman sınaması (Z7, D-3: karar metni dondurulduktan SONRA; kör değil, geliştirme verisi).

Z7 (aynen): "K5 dondurulmadan önce Tohoku geliştirme verisinde (`tr7b_gelistirme.py` girdileri) bir kez çalıştırılır.
Yalnız kodun gerçek zarflarla çalıştığını gösterir. Sonucu ne olursa olsun K5 ve Z3 değişmez."

Girdiler (yeni indirme YOK; yalnız TR-7'nin hâlihazırda işlenmiş zarfları ve depo dosyaları):
- `/mnt/project-files/turetme/tr7-zarf/zarf/pk_tohoku/<istasyon>.npz` — her biri `tr7_zarf_sha256.jsonl`'daki
  sha256 ile denetlenir; uyuşmazsa ya da dosya yoksa "yapılamadı" yazılır.
- `tr7_k1.json` (kullanılan 12 istasyon, Wb, TR-7'nin 4 kümesi), `tr7_e1_maske.csv` (birim PARKFIELD),
  `tr7_parkfield_liste.csv` (W'ler). Maske, R, Q ve saf P aralığı `tr7b_gelistirme.py` ile aynı kurulur.

Koşu kodunun kendi işlevleri çağrılır (`tr7c_kosu`): `pencere_sonucu` (TR-7 §6.3 kümeleri + K5 ayıklaması),
`e1_secim`, `modulasyon_kume` (TR-7 §6.4, 1000 kaydırma; üreteç default_rng(20261112 + 3), kümeler I′ sırasıyla).
Dal hesaplanmaz (§9). Başvuru: BK.PKD (TR-7 depoda uzun periyot hızı olan tek istasyon; TR-7 K1 lp_referans).
Kullanım: python3 -I -B tr7c_duman.py <çıktı.json>
"""
import csv
import datetime as dt
import hashlib
import json
import os
import sys
import time

sys.dont_write_bytecode = True
os.environ.setdefault('OMP_NUM_THREADS', '1')
BURA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURA)
import numpy as np  # noqa: E402
import tr7c_kosu as T  # noqa: E402

K = T.K
TR7 = T.TR7
ZARF_KOK = '/mnt/project-files/turetme/tr7-zarf/'
T0 = 1299822384            # tr7b_gelistirme.py ile aynı (2011-03-11T05:46:24, saniyeye kesik)
DERIN = 29.0
TOHOKU = (38.297, 142.373)


def ep(s):
    return int((dt.datetime.fromisoformat(s[:19]) - dt.datetime(1970, 1, 1)).total_seconds())


def utc(e):
    return str(dt.datetime(1970, 1, 1) + dt.timedelta(seconds=int(e)))


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def main():
    t_bas = time.time()
    out = dict(not_='TR-7c §9 Tohoku duman sınaması. GELİŞTİRME VERİSİ (kör değil). Yalnız kodun gerçek zarflarla '
                    'çalıştığını gösterir; sonuç ne olursa olsun hiçbir dal, K5 ya da Z3 değişmez (Z7, D-3).',
               kod_sha256={f: T.sha256_dosya(os.path.join(BURA, f)) for f in ('tr7c_duman.py', 'tr7c_kosu.py')},
               d2_sha256=T.D2_SONUC,
               depo_girdi_sha256={f: T.sha256_dosya(os.path.join(TR7, f)) for f in
                                  ('tr7_k1.json', 'tr7_e1_maske.csv', 'tr7_parkfield_liste.csv', 'tr7_zarf_sha256.jsonl')})
    k1 = json.load(open(os.path.join(TR7, 'tr7_k1.json')))['algilama_satiri']
    ist_ad = k1['kullanilan']
    kayit = {}
    for s in open(os.path.join(TR7, 'tr7_zarf_sha256.jsonl'), encoding='utf-8'):
        r = json.loads(s)
        if r['pencere'] == 'pk|tohoku':
            kayit[f"{r['ag']}.{r['istasyon']}"] = r
    gerek = list(ist_ad) + ['BK.PKD']
    eksik = [a for a in gerek if a not in kayit or not os.path.exists(os.path.join(ZARF_KOK, kayit[a]['dosya']))]
    if eksik:
        out.update(sonuc='yapılamadı', neden=f'zarf yok: {eksik}')
        json.dump(out, open(sys.argv[1], 'w'), ensure_ascii=False, indent=1)
        print(out['sonuc'], out['neden'])
        return
    shalar = {a: sha(os.path.join(ZARF_KOK, kayit[a]['dosya'])) for a in gerek}
    uyusmaz = [a for a in gerek if shalar[a] != kayit[a]['sha256']]
    out['zarf_sha256_denetimi'] = dict(dosya=len(gerek), uyusmayan=uyusmaz)
    if uyusmaz:
        out.update(sonuc='yapılamadı', neden=f'zarf sha256 uyuşmuyor: {uyusmaz}')
        json.dump(out, open(sys.argv[1], 'w'), ensure_ascii=False, indent=1)
        return
    liste = {r['ag'] + '.' + r['istasyon']: r for r in
             csv.DictReader(open(os.path.join(TR7, 'tr7_parkfield_liste.csv'), encoding='utf-8'))}
    d0 = np.load(os.path.join(ZARF_KOK, kayit[ist_ad[0]]['dosya']))
    k0, n = int(d0['k0']), len(d0['eZ'])
    maske = np.zeros(n, bool)
    for r in csv.DictReader(open(os.path.join(TR7, 'tr7_e1_maske.csv'), encoding='utf-8')):
        if r['birim'] != 'PARKFIELD':
            continue
        M, t = float(r['M']), ep(r['varis'])
        if M >= 7.0:
            a, b = t - 10, t + 240
        elif r['faz'] == 'P':
            a, b = t - 10, t + 60
        else:
            continue
        maske[max(0, a - k0):max(0, b - k0)] = True
    R = (T0 - 3600 - k0, T0 - k0)
    seri = []
    for s in ist_ad:
        d = np.load(os.path.join(ZARF_KOK, kayit[s]['dosya']))
        assert int(d['k0']) == k0
        es = [d[x] for x in ('eZ', 'eN', 'eE') if x in d.files]
        seri.append((K.birlesik(es), np.asarray(d['C051'], float),
                     (ep(liste[s]['W_bas']) - k0, ep(liste[s]['W_son']) - k0 + 1)))
    delta = K.hav(*TOHOKU, *T.IZ_ORTA) / 6371.0 * 180 / np.pi
    tP, tS = K.taup_varislar(DERIN, delta)
    Wb = (k1['Wb'][0] - k0, k1['Wb'][1] + 1 - k0)
    Q = (int(T0 + tP) - k0, Wb[0])
    Wp = (int(T0 + tP) - 10 - k0, int(T0 + tS) - 10 - k0)
    k1b = (int(round(T0 + K.hav(*TOHOKU, *T.IZ_ORTA) / T.V_K1B[0])) - k0,
           int(round(T0 + K.hav(*TOHOKU, *T.IZ_ORTA) / T.V_K1B[1])) - k0)
    out.update(delta_derece=round(delta, 2), tP_s=round(tP, 1), tS_s=round(tS, 1), Wb=[utc(k0 + x) for x in Wb],
               Q=[utc(k0 + x) for x in Q], K1b_bilgi=[utc(k0 + x) for x in k1b],
               saf_P_araligi=[utc(k0 + x) for x in Wp], P_araligi_maskeli_pay=round(float(maske[Wp[0]:Wp[1]].mean()), 3))

    def kur(W_of, Wb_, Q_, K1b_, ad):
        ist = []
        for (C, Cd, Wst), a in zip(seri, ist_ad):
            x = K.istasyon(C, Cd, R, W_of(Wst), maske, ad=a)
            x['la'], x['lo'] = float(liste[a]['enlem']), float(liste[a]['boylam'])
            ist.append(x)
        pv = dict(id=ad, durum='tarandi', n_gecen=len(ist), ist=ist, maske=maske, Wb=Wb_, Q=Q_, K1b=K1b_, k0=k0)
        sat, ks = T.pencere_sonucu(pv)
        return pv, sat, ks
    calisti, hata = True, None
    try:
        pvW, satW, ksW = kur(lambda w: w, Wb, Q, k1b, 'pk|tohoku W')
        pvP, satP, ksP = kur(lambda w: Wp, Wp, (int(T0 + tP) - k0, Wp[0]), None, 'pk|tohoku saf P')
        tr7_ip = [[x for x in kk['Ip']] for kk in k1['kumeler']]

        def kume_sat(k, pv):
            return dict(Ip=[utc(k0 + k['Ip'][0]), utc(k0 + k['Ip'][1])], n_ist=len(k['uyeler']),
                        n_cift_tutarli=k['n_cift_tutarli'], K5_bayrakli_ist=k['bayrak']['k5_bayrak'],
                        K0_bayrakli_ist_bilgi=k['bayrak']['k0_bayrak_bilgi'], darbe=bool(k['bayrak']['darbe']),
                        sizinti_K5=bool(k['bayrak']['sizinti']), taban=bool(k['bayrak']['taban']), sag=bool(k['sag']),
                        K1b_kesisir_bilgi=bool(k.get('k1b')))
        out['W_kumeleri'] = [kume_sat(k, pvW) for k in ksW]
        out['W_kumeleri_TR7_Ip_eslesmesi'] = dict(
            TR7=[[utc(x) for x in ip] for ip in tr7_ip],
            bu_kod=[[utc(k0 + k['Ip'][0]), utc(k0 + k['Ip'][1])] for k in ksW],
            ayni=[[k0 + k['Ip'][0], k0 + k['Ip'][1]] for k in ksW] == [list(ip) for ip in tr7_ip])
        out['saf_P_kumeleri'] = [kume_sat(k, pvP) for k in ksP]
        out['Q_dogrusu_kuruldu_mu'] = dict(W=satW['q_dogrusu'], saf_P=satP['q_dogrusu'])
        out['sag_kalan_kume'] = dict(W=sum(k['sag'] for k in ksW), saf_P=sum(k['sag'] for k in ksP))
        # modülasyon (Ö-c): BK.PKD, E-1 seçimi üzerinden
        z = np.load(os.path.join(ZARF_KOK, kayit['BK.PKD']['dosya']))
        assert int(z['k0']) == k0
        v = {c: (z[c].astype(float) if c in z.files and np.isfinite(z[c]).any() else None) for c in ('vZ', 'vR', 'vT')}
        pkd = liste['BK.PKD']
        aday = [dict(ad='BK.PKD', la=float(pkd['enlem']), lo=float(pkd['boylam']),
                     kanallar=[dict(kod='HHZ', konum='00', uygun_yanit=True,
                                    ortu_ok=bool(kayit['BK.PKD']['ortu_W'] >= 0.9 and kayit['BK.PKD']['ortu_R'] >= 0.9),
                                    v=dict(Z=v['vZ'], R=v['vR'], T=v['vT']))])]
        ref = T.e1_secim(aday)
        out['modulasyon_basvuru'] = None if ref is None else dict(
            ad=ref['ad'], kanal_varsayilan=ref['kanal'], bilesen=ref['bilesen'], uzaklik_km=ref['uzaklik_km'],
            not_='kanal kodu TR-7 zarf kaydında yok; E-1 için HHZ varsayıldı (yanıt ve örtü TR-7 lp=true kaydından)')
        if ref is None:
            out['modulasyon'] = 'duman sınaması modülasyonu kapsamadı (başvuru yok)'
        else:
            rng = np.random.default_rng(T.MOD_TOHUM_PK)
            Wref = (ep(pkd['W_bas']) - k0, ep(pkd['W_son']) - k0 + 1)
            mods = []
            for k in sorted(ksW, key=lambda k: (k['Ip'][0], k['Ip'][1])):
                r = T.modulasyon_kume(pvW, k, dict(ref, W=Wref), rng, K.MOD_N)
                mods.append(dict(kume='W', Ip=[utc(k0 + k['Ip'][0]), utc(k0 + k['Ip'][1])], sag=bool(k['sag']),
                                 M=None if r is None else r['M'], p=None if r is None else r['p']))
            for k in sorted(ksP, key=lambda k: (k['Ip'][0], k['Ip'][1])):
                r = T.modulasyon_kume(pvP, k, dict(ref, W=Wp), rng, K.MOD_N)
                mods.append(dict(kume='saf P (başvuru W = saf P aralığı)', Ip=[utc(k0 + k['Ip'][0]),
                                                                              utc(k0 + k['Ip'][1])],
                                 sag=bool(k['sag']), M=None if r is None else r['M'], p=None if r is None else r['p']))
            out['modulasyon'] = mods
            out['modulasyon_okunusu'] = (
                'Ö-c önceden yazılı okunuş: saf P kümesinde p ≤ 0,01 ise kilitsiz sızıntıda da m_f\'nin küçük olmadığına '
                'dair tek gözlemlik işaret; dal değişmez, metin değişmez, yalnız §12\'ye yazılır.')
    except Exception as e:   # noqa: BLE001
        calisti, hata = False, f'{type(e).__name__}: {e}'
    out.update(sonuc='kod çalıştı' if calisti else 'kod çöktü', hata=hata, sure_s=round(time.time() - t_bas, 1))
    with open(sys.argv[1], 'w', encoding='utf-8') as f:
        f.write(json.dumps(out, ensure_ascii=False, indent=1) + '\n')
    print(json.dumps({k: out.get(k) for k in ('sonuc', 'hata', 'W_kumeleri', 'W_kumeleri_TR7_Ip_eslesmesi',
                                              'saf_P_kumeleri', 'sag_kalan_kume', 'Q_dogrusu_kuruldu_mu', 'modulasyon',
                                              'saf_P_araligi', 'P_araligi_maskeli_pay')},
                     ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
