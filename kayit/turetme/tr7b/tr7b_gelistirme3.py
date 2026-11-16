#!/usr/bin/env python3
"""TR-7b Tur 3, GELİŞTİRME VERİSİ (Tohoku 2011 – Parkfield): K6'nın konum adımı gerçek kümelerde ne der? BİLGİ;
seçim ölçütüne girmez, K6'nın tanımı bu çıktıdan sonra değiştirilmez.

`tr7b_gelistirme.py` ile aynı girdi ve kümeler (TR-7 K1'in W kümeleri ve saf P aralığı sahte W'si). Konum, 12 gerçek
istasyonun ize göre koordinatlarıyla `tr7b_yapay3.konum` ile hesaplanır (modül değişkenleri U, PXY bu istasyonlara
geçici olarak atanır; kod değişmez).
Kullanım: python3 -I -B tr7b_gelistirme3.py <çıktı.json>
"""
import csv, datetime as dt, json, os, sys
import numpy as np

sys.dont_write_bytecode = True
BURADA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURADA)
import tr7b_gelistirme as G   # noqa: E402
import tr7b_yapay3 as Z       # noqa: E402
c = G.c


def main():
    TR7 = G.TR7
    k1 = json.load(open(os.path.join(TR7, 'tr7_k1.json')))['algilama_satiri']
    ad = k1['kullanilan']
    liste = {r['ag'] + '.' + r['istasyon']: r for r in csv.DictReader(open(os.path.join(TR7, 'tr7_parkfield_liste.csv')))}
    P = np.array([Z.xy(float(liste[s]['boylam']), float(liste[s]['enlem'])) for s in ad])
    Z.PXY, Z.U = P, (P - Z.MERKEZ) @ Z.YON
    d0 = np.load(G.ZARF + ad[0] + '.npz')
    k0, n = int(d0['k0']), len(d0['eZ'])
    maske = np.zeros(n, bool)
    for r in csv.DictReader(open(os.path.join(TR7, 'tr7_e1_maske.csv'))):
        if r['birim'] != 'PARKFIELD':
            continue
        M, t = float(r['M']), G.ep(r['varis'])
        if M >= 7.0:
            a, b = t - 10, t + 240
        elif r['faz'] == 'P':
            a, b = t - 10, t + 60
        else:
            continue
        maske[max(0, a - k0):max(0, b - k0)] = True
    R = (G.T0 - 3600 - k0, G.T0 - k0)
    seri = []
    for s in ad:
        d = np.load(G.ZARF + s + '.npz')
        es = [d[x] for x in ('eZ', 'eN', 'eE') if x in d.files]
        seri.append((c.birlesik(es), np.asarray(d['C051'], float),
                     (G.ep(liste[s]['W_bas']) - k0, G.ep(liste[s]['W_son']) - k0 + 1)))
    delta = c.hav(38.297, 142.373, *G.IZ_ORTA) / 6371.0 * 180 / np.pi
    tP, tS = c.taup_varislar(G.DERIN, delta)
    out = dict(not_='GELİŞTİRME VERİSİ; bilgi, seçim ölçütüne girmez', istasyon_u_km=dict(zip(ad, np.round(Z.U, 1).tolist())))

    def kur(W_of, Wb):
        ist = [c.istasyon(C, Cd, R, W_of(Wst), maske, ad=a) for (C, Cd, Wst), a in zip(seri, ad)]
        sat = []
        for k in c.kumeler(ist, maske, Wb):
            tele, ra, rb, va, nc = Z.konum(ist, k['uyeler'], k['I'], maske, list(range(len(ist))))
            sat.append(dict(Ip=[str(dt.datetime(1970, 1, 1) + dt.timedelta(seconds=k0 + k['Ip'][j])) for j in (0, 1)],
                            n_ist=len(k['uyeler']), cift=nc, konum_tele=tele,
                            rms_a=None if ra is None else round(ra, 2), rms_b=None if rb is None else round(rb, 2),
                            v_a=None if va is None else round(min(va, 9999), 1)))
        return sat

    Wb = (k1['Wb'][0] - k0, k1['Wb'][1] + 1 - k0)
    out['W_kumeleri'] = kur(lambda w: w, Wb)
    Wp = (int(G.T0 + tP) - 10 - k0, int(G.T0 + tS) - 10 - k0)
    out['P_araligi_kumeleri'] = kur(lambda w: Wp, Wp)
    json.dump(out, open(sys.argv[1], 'w'), ensure_ascii=False, indent=1)
    for k in out['W_kumeleri'] + out['P_araligi_kumeleri']:
        print(k)


if __name__ == '__main__':
    main()
