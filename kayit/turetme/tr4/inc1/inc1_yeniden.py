#!/usr/bin/env python3
"""TR-4 İNCELEME-1: tr4_guc.py'nin iki sayısının küçük ölçekte yeniden üretimi (tek süreç; depo dosyalarına yazmaz).

  ref <npz>  Kademe C (ayın 1-20'si) başvuru Δ'ları, dondurulmuş TR-5b dizilerinde, tr5b_yapay fonksiyonlarıyla bu
             betikte yeniden kurulur ve tr4_yapay_ref.json'la dizi dizi karşılaştırılır.
  olcum      §6.1 tablosunun C | CC10 ≈ 0,5 satırı: tr4_guc._olcum_is aynı tohumlarla 100 tekrar (tek süreç) koşulur,
             özet sayılar tr4_guc_sonuc.json'la karşılaştırılır. (Pool(4) kullanılmaz.)
Çıktı: inc1_yeniden_<kip>.json (bu dizine).
"""
import datetime as dt, importlib.util, json, os, sys, time
import numpy as np

BURASI = os.path.dirname(os.path.abspath(__file__))
TR4 = os.path.dirname(BURASI); TR5 = os.path.join(TR4, '..', 'tr5')


def yukle(ad, yol):
    sp = importlib.util.spec_from_file_location(ad, yol); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return m


def ref(npz):
    YP = yukle('tr5b_yapay', os.path.join(TR5, 'tr5b_yapay.py'))
    r4 = json.load(open(os.path.join(TR4, 'tr4_yapay_ref.json')))['tasarim']['C_20g_4s']['seriler']
    z = np.load(npz); gun = z['gunler'].astype(int)
    fark_d, fark_o, uyusmaz = 0.0, 0.0, 0
    for i, s in enumerate(r4):
        ayg = np.array([dt.date.fromordinal(s['T_ord'] + int(g)).day for g in gun])
        gec = z['gecerli'][i] & (ayg <= 20); ay = z['ay'][i].astype(int)
        D0 = YP.ay_esle(YP.zincir(z['ccf'][i].astype(np.float64), gec, gun, 0), gun, ay)
        D2 = YP.ay_esle(YP.zincir(z['ccf_eklenmis'][i].astype(np.float64), gec, gun, 0), gun, ay)
        if np.isnan(D0) != (s['delta_yuzde'] is None): uyusmaz += 1; continue
        if np.isnan(D0): continue
        fark_d = max(fark_d, abs(D0 * 100 - s['delta_yuzde']))
        if not np.isnan(D2): fark_o = max(fark_o, abs((D2 - D0) / -1e-3 - s['oran']))
    return dict(dizi=len(r4), gecerlilik_uyusmaz=uyusmaz, en_buyuk_fark_delta_yuzde=fark_d, en_buyuk_fark_oran=fark_o)


def olcum():
    G = yukle('tr4_guc', os.path.join(TR4, 'tr4_guc.py'))
    R = [G._olcum_is(('C_20g_4s', 'CC10~0,5', k)) for k in range(G.N_TEKRAR)]
    D0 = np.array([x[2] for x in R]); D2 = np.array([x[3] for x in R])
    ok = ~np.isnan(D0); ok2 = ok & ~np.isnan(D2); o = (D2[ok2] - D0[ok2]) / -1e-3
    yeni = dict(gecerli_delta_orani=round(float(ok.mean()), 3), sigma_olcum_yuzde=round(float(np.std(D0[ok])) * 100, 4),
                oran_medyan=round(float(np.median(o)), 3), oran_q05=round(float(np.quantile(o, .05)), 3),
                oran_q95=round(float(np.quantile(o, .95)), 3))
    eski = json.load(open(os.path.join(TR4, 'tr4_guc_sonuc.json')))['olcum']['sonuc']['C_20g_4s|CC10~0,5']
    return dict(yeni=yeni, kayitli={k: eski[k] for k in yeni}, ayni=all(yeni[k] == eski[k] for k in yeni))


if __name__ == '__main__':
    t0 = time.time(); k = sys.argv[1]
    out = ref(sys.argv[2]) if k == 'ref' else olcum()
    out['sure_sn'] = round(time.time() - t0)
    json.dump(out, open(os.path.join(BURASI, f'inc1_yeniden_{k}.json'), 'w'), ensure_ascii=False, indent=1)
    print(out)
