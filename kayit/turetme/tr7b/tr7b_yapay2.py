#!/usr/bin/env python3
"""TR-7b Tur 2: sızıntı kuralı adayları K4 ve K5, YALNIZ YAPAY VERİ (ön kayıt taslağı §11).

`tr7b_yapay.py` (Tur 1; K0–K3, üreteç, algılayıcı sarmalayıcısı) ve TR-7 `tr7_cekirdek.py` DEĞİŞTİRİLMEDEN içe aktarılır.
K0–K3 karşılaştırma için aynı pencerelerde yeniden hesaplanır.

Yeni tanımlar (istasyonun kümedeki aşım saniyeleri üzerinde; Δ_y, Δ_d, Q, K1 kalıntısı Tur 1 ile aynı):
  ρ      = Spearman sıra ilişkisi (L, zaman); aşım saniyesi < 10 ise tanımsız (sönüm şartı sağlanmaz).
  sönüm  = Δ_d ≥ Δ_y VE ρ ≤ −0,7 (tekdüze sönen bölgesel koda; −0,7 önceden sabit, veriyle seçilmedi).
  K4     = K1 VEYA sönüm. (K1: Q referansı varsa kalıntı < 2σ, yoksa K0.)  ASİMETRİK: tetikleyicisiz pencerede K0'a eşit.
  K5     = Δ_d ≥ Δ_y VE (kalıntı < 2σ VEYA ρ ≤ −0,7), kalıntı Q doğrusundan; Q'da L_d − m_d > 4σ_d olan saniye < 30 ise
           doğru a = b = 0 alınır (kalıntı = L − m ≥ 4σ, şart sağlanmaz). SİMETRİK: her pencerede aynı formül.

Satırlar ve şartlar (iki tohum; "sağ" = sağ kalan küme veren pencere / bütün pencereler):
  D7 yarım A10; D7b patlama A3/10/30          tam atılma ≤ 0,03 (algılananlarda)
  D7c düz A3/A10                              sızıntıyla atılma ≤ 0,05
  D7d koda ×20                                sızıntıyla atılma ≥ 0,95
  Y1 tremor A3/A10 + tele 'egim', a_y 2/5/10, κ 12,5                  tam atılma ≤ 0,05 (I′ tremorla kesişen kümeler)
  Y1 'sabit' a_y 10                                                    bilgi
  Y2 tele, a_y 2/5/10 × κ 6/12,5/25 × 'egim'/'sabit' (18 hücre)        sağ ≤ 0,05
  Y3 koda ×20 + tele 'egim' κ 12,5, a_y 2/5/10                          sızıntıyla atılma ≥ 0,95
  F1 tetikleyicisiz pencere, kentsel gürültü, tremor yok               sağ ≤ 0,05
  F2 tetikleyicili pencere (tele 'egim' a_y 10 κ 12,5), kentsel gürültü, tremor yok   sağ ≤ 0,05 ve sağ(F2) − sağ(F1) ≤ 0,02
Kentsel gürültü: TR-7 §7.1 D7c/D7d ile aynı (2–8 Hz'te ≈300 sn'lik rastgele ×exp(0,35 z)).
Seçim ölçütü: ön kayıt taslağı §11.3 (iki tohumda bütün şartlar; önce simetrik, sonra en büyük en kötü pay).

Kullanım: python3 -I -B tr7b_yapay2.py <tohum> <n_pencere> <çıktı.json>
"""
import json, os, sys
import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tr7b_yapay as Y   # noqa: E402  (değiştirilmeden)
c = Y.c


def _rho(x, sec):
    if sec.sum() < 10:
        return None
    L = x['L'][sec]
    tt = np.flatnonzero(sec).astype(float)
    rl = np.argsort(np.argsort(L)).astype(float)
    rt = np.argsort(np.argsort(tt)).astype(float)
    if rl.std() == 0:
        return None
    return float(np.corrcoef(rl, rt)[0, 1])


def _delta(x, sec):
    return np.median(x['L'][sec]) - x['m'], np.median(x['Ld'][sec]) - x['md']


def sonum(x, sec):
    dy, dd = _delta(x, sec)
    r = _rho(x, sec)
    return bool(dd >= dy and r is not None and r <= -0.7)


def K4(x, parcalar, maske, Q):
    sec = Y.secili(x, parcalar, maske)
    if not sec.any():
        return False
    return bool(Y.K1(x, parcalar, maske, Q) or sonum(x, sec))


def K5(x, parcalar, maske, Q):
    sec = Y.secili(x, parcalar, maske)
    if not sec.any():
        return False
    dy, dd = _delta(x, sec)
    if dd < dy:
        return False
    kal = Y._k1_kalinti(x, sec, maske, Q, yedek=False)   # Q'da doğru yoksa False (a = b = 0 ile eşdeğer)
    r = _rho(x, sec)
    return bool(kal or (r is not None and r <= -0.7))


Y.KURALLAR['K4'] = K4
Y.KURALLAR['K5'] = K5


def gurultu_kentsel(rng):
    y, d = Y.iki_bant(rng)
    z = np.fft.irfft(np.fft.rfft(rng.standard_normal(Y.N)) * Y.bw2(1e-6, 1 / 300.0), Y.N)
    return y * np.exp(0.35 * z / z.std()), d


def istasyonlar(rng, gtur='gauss', tremor=None, A=0.0, sekil=None, norm=None, tele=None, n_ist=3):
    st = []
    for _ in range(n_ist):
        cy, cd = [], []
        for _b in range(3):
            ny, nd = Y.iki_bant(rng) if gtur == 'gauss' else gurultu_kentsel(rng)
            y, d = ny.copy(), nd.copy()
            if tremor is not None and A:
                sy, sd = Y.iki_bant(rng, tremor, sekil, norm)
                y += A * sy
                d += A * sd
            if tele is not None:
                ey, ed, ay, ka = tele
                ty, td = Y.iki_bant(rng)
                y += ay * ey * ty
                d += ka * ay * ed * td
            cy.append(Y.zarf1hz(y))
            cd.append(Y.zarf1hz(d))
        st.append((c.birlesik(cy), c.birlesik(cd)))
    return st


def satir(rng, n, uret):
    alg, at = 0, {k: [0, 0] for k in Y.KURALLAR}
    for _ in range(n):
        st, ilgi = uret(rng)
        r = Y.degerlendir(st, ilgi=ilgi)
        if r is None:
            continue
        alg += 1
        for k, (a1, a2) in r.items():
            at[k][0] += a1
            at[k][1] += a2
    out = dict(n=n, n_alg=alg, algilama=round(alg / n, 3))
    for k, v in at.items():
        out[f'{k}_atilma_tam'] = round(v[0] / alg, 3) if alg else None
        out[f'{k}_atilma_sizinti'] = round(v[1] / alg, 3) if alg else None
        out[f'{k}_sag'] = round((alg - v[0]) / n, 3)
    return out


def tele_zarf(rng, bicim):
    e = Y.zarf_tele(rng)
    ey = e * np.where(Y.t >= Y.TP, np.exp(-(Y.t - Y.TP) / 600.0), 0) if bicim == 'egim' else e
    return ey, e


def koda_zarf(b):
    tt = Y.t - b
    env = np.where(tt >= 0, np.exp(-np.maximum(tt, 0) / 40.0), 0) * np.minimum(1, np.maximum(tt, 0) / 1.0)
    return env, (tt >= 0) & (tt < 5)


def main():
    tohum, n, cikti = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    rng = np.random.default_rng(tohum)

    def tr(tur, A, sekil=None):
        def u(rng):
            b = Y.bas_w(rng)
            env = Y.zarf_yarim(b) if tur == 'yarim' else Y.zarf_patlama(rng, b)
            return istasyonlar(rng, tremor=env, A=A, sekil=sekil), None
        return u

    def koda(rng):
        env, norm = koda_zarf(Y.bas_w(rng))
        return istasyonlar(rng, tremor=env, A=20.0, sekil=Y.KODA, norm=norm), None

    def y1(A, ay, ka, bicim):
        def u(rng):
            ey, e = tele_zarf(rng, bicim)
            b = Y.bas_w(rng)
            return istasyonlar(rng, tremor=Y.zarf_yarim(b), A=A, tele=(ey, e, ay, ka)), (b, b + 300)
        return u

    def y2(ay, ka, bicim):
        def u(rng):
            ey, e = tele_zarf(rng, bicim)
            return istasyonlar(rng, tele=(ey, e, ay, ka)), None
        return u

    def y3(ay):
        def u(rng):
            ey, e = tele_zarf(rng, 'egim')
            env, norm = koda_zarf(Y.bas_w(rng))
            return istasyonlar(rng, tremor=env, A=20.0, sekil=Y.KODA, norm=norm, tele=(ey, e, ay, 12.5)), None
        return u

    def f(tele):
        def u(rng):
            if tele:
                ey, e = tele_zarf(rng, 'egim')
                return istasyonlar(rng, gtur='kentsel', tele=(ey, e, 10, 12.5)), None
            return istasyonlar(rng, gtur='kentsel'), None
        return u

    isler = [('D7 yarım A10', tr('yarim', 10.0))]
    isler += [(f'D7b patlama A{A}', tr('patlama', float(A))) for A in (3, 10, 30)]
    isler += [(f'D7c düz A{A}', tr('yarim', float(A), Y.DUZ)) for A in (3, 10)]
    isler += [('D7d koda x20', koda)]
    isler += [(f'Y1 A{A} a_y{ay} κ12.5 egim', y1(float(A), ay, 12.5, 'egim')) for A in (3, 10) for ay in (2, 5, 10)]
    isler += [(f'Y1 A{A} a_y10 κ12.5 sabit', y1(float(A), 10, 12.5, 'sabit')) for A in (3, 10)]
    isler += [(f'Y2 a_y{ay} κ{ka} {b}', y2(ay, ka, b)) for ay in (2, 5, 10) for ka in (6, 12.5, 25)
              for b in ('egim', 'sabit')]
    isler += [(f'Y3 koda x20 + tele a_y{ay}', y3(ay)) for ay in (2, 5, 10)]
    isler += [('F1 tetikleyicisiz kentsel', f(False)), ('F2 tetikleyicili kentsel', f(True))]
    sonuc = {}
    for ad, u in isler:
        sonuc[ad] = satir(rng, n, u)
        print(ad, json.dumps(sonuc[ad], ensure_ascii=False), flush=True)
    json.dump(dict(tohum=tohum, n=n, satirlar=sonuc), open(cikti, 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
