#!/usr/bin/env python3
"""TR-7b, GELİŞTİRME VERİSİ: Tohoku 2011 – Parkfield (TR-7 K1 penceresi). Kör DEĞİL; seçim ölçütüne girmez.

Girdi: TR-7'nin depo dışı 1 Hz zarf serileri (`/mnt/project-files/turetme/tr7-zarf/zarf/pk_tohoku/*.npz`) ve depodaki
`tr7_k1.json`, `tr7_e1_maske.csv`, `tr7_parkfield_liste.csv`. Hiçbir dalga formu indirilmez. Algılayıcı
`tr7_cekirdek.py`'den (değiştirilmeden), aday sızıntı kuralları `tr7b_yapay.py`'den alınır.

Yapılanlar:
 (a) TR-7 K1'in 4 kümesini aynı istasyonlar (12 sınırı), E1 maskesi ve W'lerle yeniden kurar (I′ eşleşmesi denetlenir)
     ve K0–K3 bayraklarını yazar (istasyon başına Δ_y, Δ_d, r, K1 kalıntısı).
 (b) Saf telesismik sınama: tetikleyicinin P varışından S varışına kadarki aralık (iz ortasına iasp91; S'den önce,
     Hill 2013'e göre tremor S ile başlar) sahte W olarak alınır; burada kurulan kümelerin aday kurallarla atılıp
     atılmadığı yazılır (K1 bu aralıkta referanssız olduğundan K0'a, K3 K2'ye düşer).
 (c) Dakikalık 12 istasyon medyanı Δ_y, Δ_d (tr7b_yapay.py'deki telesismik modelin kalibrasyonu).
Kullanım: python3 -I -B tr7b_gelistirme.py <çıktı.json>
"""
import csv, datetime as dt, json, os, sys
import numpy as np

sys.dont_write_bytecode = True
BURADA = os.path.dirname(os.path.abspath(__file__))
TR7 = os.path.join(BURADA, '..', 'tr7')
sys.path.insert(0, TR7)
sys.path.insert(0, BURADA)
import tr7_cekirdek as c   # noqa: E402
import tr7b_yapay as Y     # noqa: E402

ZARF = '/mnt/project-files/turetme/tr7-zarf/zarf/pk_tohoku/'
T0 = 1299822384            # 2011-03-11T05:46:24 (TR-7 tetikleyici, saniyeye kesik)
DERIN = 29.0
IZ_ORTA = (35.9125, -120.4625)


def ep(s):
    return int((dt.datetime.fromisoformat(s[:19]) - dt.datetime(1970, 1, 1)).total_seconds())


def main():
    k1 = json.load(open(os.path.join(TR7, 'tr7_k1.json')))['algilama_satiri']
    ist_ad = k1['kullanilan']
    liste = {r['ag'] + '.' + r['istasyon']: r for r in csv.DictReader(open(os.path.join(TR7, 'tr7_parkfield_liste.csv')))}
    d0 = np.load(ZARF + ist_ad[0] + '.npz')
    k0, n = int(d0['k0']), len(d0['eZ'])
    maske = np.zeros(n, bool)
    for r in csv.DictReader(open(os.path.join(TR7, 'tr7_e1_maske.csv'))):
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
        d = np.load(ZARF + s + '.npz')
        assert int(d['k0']) == k0
        es = [d[x] for x in ('eZ', 'eN', 'eE') if x in d.files]
        seri.append((c.birlesik(es), np.asarray(d['C051'], float), (ep(liste[s]['W_bas']) - k0, ep(liste[s]['W_son']) - k0 + 1)))
    delta = c.hav(38.297, 142.373, *IZ_ORTA) / 6371.0 * 180 / np.pi
    tP, tS = c.taup_varislar(DERIN, delta)
    out = dict(not_='GELİŞTİRME VERİSİ (Tohoku–Parkfield); kör değil, seçim ölçütüne girmez',
               delta_derece=round(delta, 2), tP_s=round(tP, 1), tS_s=round(tS, 1))

    def kur(W_of, Wb, Q):
        ist = [c.istasyon(C, Cd, R, W_of(Wst), maske, ad=a) for (C, Cd, Wst), a in zip(seri, ist_ad)]
        ks = c.kumeler(ist, maske, Wb)
        sat = []
        for k in ks:
            uy = k['uyeler']
            pk = {i: [(a, b) for ii, a, b in k['parcalar'] if ii == i] for i in uy}
            ayr = []
            for i in uy:
                x = ist[i]
                sec = Y.secili(x, pk[i], maske)
                dy = float(np.median(x['L'][sec]) - x['m'])
                dd = float(np.median(x['Ld'][sec]) - x['md'])
                r = float(np.corrcoef(x['L'][sec], x['Ld'][sec])[0, 1]) if sec.sum() >= 10 else None
                kal = None
                if Q is not None:
                    q = np.zeros(n, bool)
                    q[Q[0]:Q[1]] = True
                    with np.errstate(invalid='ignore'):
                        q &= ~maske & np.isfinite(x['L']) & np.isfinite(x['Ld']) & (x['Ld'] - x['md'] > c.KSIG * x['sd'])
                    if q.sum() >= 30:
                        bb, aa = np.polyfit(x['Ld'][q] - x['md'], x['L'][q] - x['m'], 1)
                        kal = float(np.median((x['L'][sec] - x['m']) - (aa + bb * (x['Ld'][sec] - x['md']))))
                ayr.append(dict(ist=x['ad'], dy=round(dy, 3), dd=round(dd, 3), r=None if r is None else round(r, 3),
                                k1_kalinti=None if kal is None else round(kal, 3), iki_sigma=round(2 * x['s'], 3),
                                **{kn: bool(kf(x, pk[i], maske, Q if Q is not None else (0, 0)))
                                   for kn, kf in Y.KURALLAR.items()}))
            yarim = len(uy) / 2
            sat.append(dict(Ip=[str(dt.datetime(1970, 1, 1) + dt.timedelta(seconds=k0 + k['Ip'][j])) for j in (0, 1)],
                            n_ist=len(uy), n_cift_tutarli=k['n_cift_tutarli'],
                            darbe=sum(c.darbe_ist(ist[i]['Cy'], pk[i]) for i in uy) >= yarim,
                            taban=sum(c.taban_ist(ist[i], pk[i], maske) for i in uy) >= yarim,
                            **{f'{kn}_atilir': sum(a[kn] for a in ayr) >= yarim for kn in Y.KURALLAR},
                            istasyonlar=ayr))
        return sat

    Wb = (k1['Wb'][0] - k0, k1['Wb'][1] + 1 - k0)
    Q = (int(T0 + tP) - k0, Wb[0])
    out['a_W_kumeleri'] = kur(lambda w: w, Wb, Q)
    out['a_Ip_TR7'] = [[str(dt.datetime(1970, 1, 1) + dt.timedelta(seconds=x)) for x in kk['Ip']] for kk in k1['kumeler']]
    Wp = (int(T0 + tP) - 10 - k0, int(T0 + tS) - 10 - k0)
    out['b_sahte_W_P_araligi'] = [str(dt.datetime(1970, 1, 1) + dt.timedelta(seconds=k0 + x)) for x in Wp]
    out['b_P_araligi_kumeleri'] = kur(lambda w: Wp, Wp, None)
    out['b_P_araligi_maskeli_pay'] = round(float(maske[Wp[0]:Wp[1]].mean()), 3)
    # (c) dakikalık medyanlar
    ist = [c.istasyon(C, Cd, R, Wst, maske) for C, Cd, Wst in seri]
    dak = []
    for t in range(T0 - k0 - 300, Wb[1], 60):
        dak.append(dict(utc=(dt.datetime(1970, 1, 1) + dt.timedelta(seconds=k0 + t)).strftime('%H:%M'),
                        dy=round(float(np.nanmedian([np.nanmedian(x['L'][t:t + 60]) - x['m'] for x in ist])), 2),
                        dd=round(float(np.nanmedian([np.nanmedian(x['Ld'][t:t + 60]) - x['md'] for x in ist])), 2),
                        maskeli=round(float(maske[t:t + 60].mean()), 2)))
    out['c_dakikalik'] = dak
    json.dump(out, open(sys.argv[1], 'w'), ensure_ascii=False, indent=1)
    for k in out['a_W_kumeleri'] + out['b_P_araligi_kumeleri']:
        print(k['Ip'], k['n_ist'], k['n_cift_tutarli'], 'darbe', k['darbe'], 'taban', k['taban'],
              {kn: k[f'{kn}_atilir'] for kn in Y.KURALLAR})
    print('TR-7 Ip:', out['a_Ip_TR7'])
    print('P aralığı:', out['b_sahte_W_P_araligi'], 'maskeli', out['b_P_araligi_maskeli_pay'])


if __name__ == '__main__':
    main()
