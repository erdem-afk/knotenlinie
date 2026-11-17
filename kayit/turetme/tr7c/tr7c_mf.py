#!/usr/bin/env python3
"""TR-7c D-4: m_f ölçümü (§10 adım 2), YALNIZ YAPAY VERİ.

D-4 (aynen): "m_f, §10 adım 2'de Y2 ve Y3 satırlarında ayıklamadan önce algılanan bütün kümelerde, K5'ten sağ çıkıp
çıkmadığına bakılmadan, TR-7 §6.4 ölçüsüyle ölçülür (en az 100 küme; daha azsa pencere sayısı artırılır); K5'ten sağ
kalanlardaki pay ayrıca yazılır. Ölçülen m_f > 0,10 ise taslak bağımsız incelemeye döner. Bu ölçüm yalnız yüzey dalgasına
kilitli olmayan sızıntıyı kapsar ..."

Uygulama (kodlayıcı okuması O-40):
- Satırlar TR-7b Tur 2'nin (`tr7b_yapay2.py`, değiştirilmeden içe aktarılır) Y2 (18 hücre: a_y 2/5/10 × κ 6/12,5/25 ×
  'egim'/'sabit') ve Y3 (3 hücre: koda ×20 + tele 'egim', κ 12,5, a_y 2/5/10) üreteçleriyle, aynı çağrılarla kurulur
  (3 istasyon, gauss gürültü). Pencere sayısı hücre başına N_PEN.
- "Ayıklamadan önce algılanan küme" = TR-7 §6.3 tutarlı küme (`K.kumeler`), I′ W'nin herhangi bir yerinde.
- Başvuru hızı: üç bileşen (Z, R, T), her biri bağımsız dar bantlı (15–30 sn) Gauss dizisi; sızıntı zarfından
  bağımsızdır (Y2/Y3'te yüzey dalgası periyodu yoktur; D-4'ün kapsamı). Ölçü: `tr7c_kosu.modulasyon_kume`
  (TR-7 §6.4: L_k = üyelerin L medyanı, M, 1000 dairesel kaydırma, p ≤ 0,01).
- Ayrıca her küme için TR-7c ayıklaması (`tr7c_kosu.ayikla_k5`: darbe, K5, taban) yazılır; "K5'ten sağ kalan" =
  ayıklamadan sağ çıkan (darbe, K5 ve taban kaymasının hiçbiri bayraklamadı).
- Üreteç: pencereler default_rng(TOHUM), başvuru hızları ve kaydırmalar default_rng(TOHUM + 1) (bu betiğin seçimi).
Ağ isteği yok, gerçek dalga formu yok. Sürdürülebilir (ara sonuç jsonl, depo dışında).

Kullanım: python3 -I -B tr7c_mf.py <çıktı.json> <ara.jsonl> [N_PEN]
"""
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

K, Y2, Y = T.K, T.Y2, T.Y
TOHUM = 20261119
MOD_N = 1000


def lp3(rng):
    out = []
    f = np.fft.rfftfreq(Y.T, 1.0)
    for _ in range(3):
        X = np.fft.rfft(rng.standard_normal(Y.T))
        X[(f < 1 / 30) | (f > 1 / 15)] = 0
        v = np.fft.irfft(X, Y.T)
        out.append(v / v.std())
    return out


def hucreler():
    def y2(ay, ka, bicim):
        def u(rng):
            ey, e = Y2.tele_zarf(rng, bicim)
            return Y2.istasyonlar(rng, tele=(ey, e, ay, ka))
        return u

    def y3(ay):
        def u(rng):
            ey, e = Y2.tele_zarf(rng, 'egim')
            env, norm = Y2.koda_zarf(Y.bas_w(rng))
            return Y2.istasyonlar(rng, tremor=env, A=20.0, sekil=Y.KODA, norm=norm, tele=(ey, e, ay, 12.5))
        return u
    out = [(f'Y2 a_y{ay} κ{ka} {b}', y2(ay, ka, b)) for ay in (2, 5, 10) for ka in (6, 12.5, 25)
           for b in ('egim', 'sabit')]
    out += [(f'Y3 koda x20 + tele a_y{ay}', y3(ay)) for ay in (2, 5, 10)]
    return out


def main():
    cikti, ara = sys.argv[1], sys.argv[2]
    n_pen = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    t0 = time.time()
    rng = np.random.default_rng(TOHUM)
    rng_v = np.random.default_rng(TOHUM + 1)
    yazili = []
    if os.path.exists(ara):
        yazili = [json.loads(s) for s in open(ara, encoding='utf-8') if s.strip()]
    son = {(r['hucre'], r['pencere']): r for r in yazili}
    durum = next((r['rng'] for r in reversed(yazili) if r.get('rng')), None)
    if durum:
        rng.bit_generator.state = durum['p']
        rng_v.bit_generator.state = durum['v']
    maske = np.zeros(Y.T, bool)
    for ad, u in hucreler():
        for j in range(n_pen):
            if (ad, j) in son:
                continue
            st = u(rng)
            ist = [K.istasyon(Cy, Cd, Y.R_IX, Y.W_IX, maske) for Cy, Cd in st]
            v = lp3(rng_v)
            pv = dict(ist=ist, maske=maske, Wb=Y.W_IX, Q=Y.Q_IX)
            ref = dict(W=Y.W_IX, v=v)
            km = []
            for k in K.kumeler(ist, maske, Y.W_IX):
                b = T.ayikla_k5(ist, k, maske, Y.Q_IX)
                r = T.modulasyon_kume(pv, k, ref, rng_v, MOD_N)
                km.append(dict(Ip=list(map(int, k['Ip'])), n_ist=len(k['uyeler']), K5=bool(b['sizinti']),
                               darbe=bool(b['darbe']), taban=bool(b['taban']),
                               sag=not (b['darbe'] or b['sizinti'] or b['taban']),
                               M=None if r is None else r['M'], p=None if r is None else r['p']))
            sat = dict(hucre=ad, pencere=j, kumeler=km,
                       rng=dict(p=json.loads(json.dumps(rng.bit_generator.state)),
                                v=json.loads(json.dumps(rng_v.bit_generator.state))))
            with open(ara, 'a', encoding='utf-8') as f:
                f.write(json.dumps(sat, ensure_ascii=False) + '\n')
                f.flush()
                os.fsync(f.fileno())
            son[(ad, j)] = sat
            print(ad, j, len(km), round(time.time() - t0), flush=True)
    # özet
    satirlar = {}
    tum = {'Y2': [], 'Y3': []}
    for (ad, j), r in sorted(son.items()):
        if j >= n_pen:
            continue
        s = satirlar.setdefault(ad, dict(pencere=0, kume=0, olculen=0, mod=0, sag=0, sag_mod=0))
        s['pencere'] += 1
        for k in r['kumeler']:
            s['kume'] += 1
            tum[ad[:2]].append(k)
            if k['p'] is not None:
                s['olculen'] += 1
                s['mod'] += k['p'] <= K.MOD_ESIK
                s['sag'] += k['sag']
                s['sag_mod'] += k['sag'] and k['p'] <= K.MOD_ESIK

    def oz(ks):
        o = [k for k in ks if k['p'] is not None]
        sg = [k for k in o if k['sag']]
        m = sum(k['p'] <= K.MOD_ESIK for k in o)
        ms = sum(k['p'] <= K.MOD_ESIK for k in sg)
        return dict(kume=len(ks), olculen=len(o), mod_p_le_001=m, m_f=(m / len(o)) if o else None,
                    m_f_cp_ust=K.cp_ust(m, len(o)) if o else None,
                    K5_ayiklamadan_sag=len(sg), sag_mod=ms, m_f_sag=(ms / len(sg)) if sg else None,
                    p_dagilimi_ceyrek=[float(np.quantile([k['p'] for k in o], q)) for q in (0.1, 0.25, 0.5)]
                    if o else None)
    hep = oz(tum['Y2'] + tum['Y3'])
    out = dict(
        aciklama='TR-7c D-4 m_f ölçümü: TR-7b Y2 (18 hücre) ve Y3 (3 hücre), ayıklamadan önce algılanan bütün tutarlı '
                 'kümeler, TR-7 §6.4 ölçüsü (1000 kaydırma, p ≤ 0,01). Yalnız yapay veri.',
        kapsam='Yalnız yüzey dalgasına kilitli OLMAYAN sızıntı (Y2/Y3 telesismik ve koda zarfları; başvuru hızı '
               'sızıntıdan bağımsız dar bantlı 15–30 sn). Kilitli sızıntının m_f\'si bu ölçümle ölçülmez '
               '(D-4; doğrulanamadı); onun için tanım gereği m_f ≈ 1 (tr7c_inc1.json kilitli_sizinti).',
        kod_sha256={'tr7c_mf.py': T.sha256_dosya(os.path.abspath(__file__)),
                    'tr7c_kosu.py': T.sha256_dosya(os.path.join(BURA, 'tr7c_kosu.py'))},
        d2_sha256=T.D2_SONUC, tohum=dict(pencere=TOHUM, hiz_ve_kaydirma=TOHUM + 1), pencere_hucre_basina=n_pen,
        mod_n=MOD_N, toplam=hep, Y2=oz(tum['Y2']), Y3=oz(tum['Y3']), hucreler=satirlar,
        d4_esik=dict(esik=0.10, asildi=(hep['m_f'] is not None and hep['m_f'] > 0.10),
                     not_='m_f > 0,10 ise yalnız bildirilir (görev tanımı); taslak bağımsız incelemeye döner (D-4).'),
        en_az_100_kume=hep['olculen'] >= 100, sure_s=round(time.time() - t0, 1))
    with open(cikti, 'w', encoding='utf-8') as f:
        f.write(json.dumps(out, ensure_ascii=False, indent=1) + '\n')
    print(json.dumps(dict(toplam=hep, Y2=out['Y2'], Y3=out['Y3']), ensure_ascii=False))


if __name__ == '__main__':
    main()
