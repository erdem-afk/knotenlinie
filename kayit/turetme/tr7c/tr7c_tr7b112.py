#!/usr/bin/env python3
"""TR-7c §10 adım 2: TR-7b §11.2 satırlarının (Tur 2, `tr7b_yapay2.py`) TR-7c KOŞU KODUNUN algılama yolundan
(`tr7c_kosu.pencere_algila_k5` → `ayikla_k5` → `k5_ist` → `tr7b_yapay2.K5`) yeniden koşulması. YALNIZ YAPAY VERİ, bilgi.

Pencereler `tr7b_yapay2.main` ile aynı üreteç çağrılarıyla ve aynı sırayla kurulur (aşağıdaki satır listesi oradan
kopyadır; üreteç işlevleri değiştirilmeden içe aktarılır). Algılayıcı çağrısı rastgele sayı çekmediği için aynı tohumda
pencereler Tur 2'dekilerle bayt bayt aynıdır; bu yüzden K5 sütunlarının (`K5_atilma_tam`, `K5_atilma_sizinti`, `K5_sag`,
`n_alg`) Tur 2 json'larıyla BİREBİR tutması beklenir (Monte Carlo farkı yok). Tutmazsa koşu kodu K5'i yanlış çağırıyor
demektir.

Kullanım: python3 -I -B tr7c_tr7b112.py <tohum> <n_pencere> <çıktı.json>
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


def degerlendir_tr7c(st, ilgi=None):
    """Y.degerlendir'in K5 sütunu, ama TR-7c koşu kodunun yoluyla (pencere_algila_k5)."""
    maske = np.zeros(Y.T, bool)
    ist = [K.istasyon(Cy, Cd, Y.R_IX, Y.W_IX, maske) for Cy, Cd in st]
    ks = T.pencere_algila_k5(ist, maske, Y.W_IX, Y.Q_IX)
    if ilgi is not None:
        ks = [k for k in ks if k['Ip'][0] < ilgi[1] and k['Ip'][1] > ilgi[0]]
    if not ks:
        return None
    tam_sag = any(k['sag'] for k in ks)
    siz_sag = any(not k['bayrak']['sizinti'] for k in ks)
    return (not tam_sag, not siz_sag)


def satir(rng, n, uret):
    alg, a1, a2 = 0, 0, 0
    for _ in range(n):
        st, ilgi = uret(rng)
        r = degerlendir_tr7c(st, ilgi)
        if r is None:
            continue
        alg += 1
        a1 += r[0]
        a2 += r[1]
    return dict(n=n, n_alg=alg, K5_atilma_tam=round(a1 / alg, 3) if alg else None,
                K5_atilma_sizinti=round(a2 / alg, 3) if alg else None, K5_sag=round((alg - a1) / n, 3))


def isler():
    # ---- tr7b_yapay2.main'den kopya (aynı çağrılar, aynı sıra)
    def tr(tur, A, sekil=None):
        def u(rng):
            b = Y.bas_w(rng)
            env = Y.zarf_yarim(b) if tur == 'yarim' else Y.zarf_patlama(rng, b)
            return Y2.istasyonlar(rng, tremor=env, A=A, sekil=sekil), None
        return u

    def koda(rng):
        env, norm = Y2.koda_zarf(Y.bas_w(rng))
        return Y2.istasyonlar(rng, tremor=env, A=20.0, sekil=Y.KODA, norm=norm), None

    def y1(A, ay, ka, bicim):
        def u(rng):
            ey, e = Y2.tele_zarf(rng, bicim)
            b = Y.bas_w(rng)
            return Y2.istasyonlar(rng, tremor=Y.zarf_yarim(b), A=A, tele=(ey, e, ay, ka)), (b, b + 300)
        return u

    def y2(ay, ka, bicim):
        def u(rng):
            ey, e = Y2.tele_zarf(rng, bicim)
            return Y2.istasyonlar(rng, tele=(ey, e, ay, ka)), None
        return u

    def y3(ay):
        def u(rng):
            ey, e = Y2.tele_zarf(rng, 'egim')
            env, norm = Y2.koda_zarf(Y.bas_w(rng))
            return Y2.istasyonlar(rng, tremor=env, A=20.0, sekil=Y.KODA, norm=norm, tele=(ey, e, ay, 12.5)), None
        return u

    def f(tele):
        def u(rng):
            if tele:
                ey, e = Y2.tele_zarf(rng, 'egim')
                return Y2.istasyonlar(rng, gtur='kentsel', tele=(ey, e, 10, 12.5)), None
            return Y2.istasyonlar(rng, gtur='kentsel'), None
        return u

    out = [('D7 yarım A10', tr('yarim', 10.0))]
    out += [(f'D7b patlama A{A}', tr('patlama', float(A))) for A in (3, 10, 30)]
    out += [(f'D7c düz A{A}', tr('yarim', float(A), Y.DUZ)) for A in (3, 10)]
    out += [('D7d koda x20', koda)]
    out += [(f'Y1 A{A} a_y{ay} κ12.5 egim', y1(float(A), ay, 12.5, 'egim')) for A in (3, 10) for ay in (2, 5, 10)]
    out += [(f'Y1 A{A} a_y10 κ12.5 sabit', y1(float(A), 10, 12.5, 'sabit')) for A in (3, 10)]
    out += [(f'Y2 a_y{ay} κ{ka} {b}', y2(ay, ka, b)) for ay in (2, 5, 10) for ka in (6, 12.5, 25)
            for b in ('egim', 'sabit')]
    out += [(f'Y3 koda x20 + tele a_y{ay}', y3(ay)) for ay in (2, 5, 10)]
    out += [('F1 tetikleyicisiz kentsel', f(False)), ('F2 tetikleyicili kentsel', f(True))]
    return out


def main():
    tohum, n, cikti = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    tur2 = {20261117: 'tr7b_yapay2_t1.json', 9393: 'tr7b_yapay2_t2.json'}.get(tohum)
    ref = json.load(open(os.path.join(T.TR7B, tur2)))['satirlar'] if tur2 else {}
    t0 = time.time()
    rng = np.random.default_rng(tohum)
    sonuc, fark = {}, []
    for ad, u in isler():
        s = satir(rng, n, u)
        r = ref.get(ad)
        s['tur2'] = None if r is None else {k: r[k] for k in ('n_alg', 'K5_atilma_tam', 'K5_atilma_sizinti', 'K5_sag')}
        s['birebir'] = None if r is None else all(s[k] == r[k] for k in s['tur2'])
        if s['birebir'] is False:
            fark.append(ad)
        sonuc[ad] = s
        print(ad, json.dumps(s, ensure_ascii=False), flush=True)
    out = dict(aciklama='TR-7b §11.2 (Tur 2) satırları TR-7c koşu kodunun algılama yolundan; bilgi (K5 seçimini '
                        'etkilemez). Aynı tohumda Tur 2 ile birebir beklenir.',
               kod_sha256={f: T.sha256_dosya(os.path.join(BURA, f)) for f in ('tr7c_tr7b112.py', 'tr7c_kosu.py')},
               d2_sha256=T.D2_SONUC, tohum=tohum, n=n, tur2_json=tur2, birebir_tutmayan=fark,
               hepsi_birebir=(not fark) if tur2 and n == 100 else None, satirlar=sonuc,
               sure_s=round(time.time() - t0, 1))
    with open(cikti, 'w', encoding='utf-8') as f:
        f.write(json.dumps(out, ensure_ascii=False, indent=1) + '\n')
    print('birebir tutmayan:', fark)


if __name__ == '__main__':
    main()
