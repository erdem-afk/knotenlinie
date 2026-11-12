#!/usr/bin/env python3
"""TR-7 ön kayıt sürüm 3, §7.1 D15 (İNCELEME-2 İ2-E1, İ2-E2): taban kayması kuralı (§6.5 madde 3a) W′_son tanımıyla.

YALNIZ YAPAY VERİ; numpy ve standart kitaplık. Zarf zinciri, algılayıcı ve öteki ayıklamalar
`tr7_onkayit_denetim2.py`'den (sürüm 2 referans betiği) aynen alınır; bu betik yalnız 3a'nın sürüm 3 tanımını ekler:
  3a. Kümedeki istasyonların ≥ yarısında, istasyonun kümedeki aşım parçalarından biri W′_son − 60 sn'ye ya da daha
      sonrasına kadar sürüyorsa küme atılır. W′_son, istasyonun kendi W'si içinde maskelenmemiş ve kayıtlı son saniyedir.
Gösterim: parça (a, b) W içinde [a, b) saniyeleridir (b dışlayıcı); W′_son = k ise "W′_son − 60'a kadar sürer" şartı
b ≥ (k + 1) − 60'tır (maskesiz ve kayıtsız saniye yoksa k + 1 = W sonu; sürüm 2 ile aynı).

D15 (§7.1): tremor yok; 3 istasyon; 2–8 Hz gürültü W başından 300 sn sonra 900 sn içinde doğrusal ×2'ye yükselir, W
sonuna kadar ×2 kalır (İNCELEME-2 `tr7_inc2_taban.py` profili: K = 2, BAS = 300, rampa = 900); (a) maskesiz, (b) W'nin
son 120 sn'si maskeli. Doğru kod: 3a (W′_son) ile atılma. Bilinen yanlış kodlar: 3a yok (yalnız darbe ve sızıntı);
sürüm 2'nin "W sonu − 60" tanımı.
Kullanım: python3 -I -B tr7_onkayit_denetim3.py D15 <tohum> <n_pencere> <maskeli_son_sn>
Çıktı: tek satır JSON (stdout). Toplayıcı: tr7_onkayit_denetim3_kos.py.
"""
import json, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tr7_onkayit_denetim2 as D        # noqa: E402

PROFIL = np.clip((D.t_ornek - (D.R_S + 300.0)) / 900.0, 0, 1) * (2.0 - 1) + 1


def w_son_acik(maske, kayitsiz=None):
    """İstasyonun W′_son'u (W koordinatında, kapsayıcı indis); W'de açık saniye yoksa None."""
    acik = ~maske[D.R_S:]
    if kayitsiz is not None:
        acik &= ~kayitsiz[D.R_S:]
    k = np.flatnonzero(acik)
    return int(k[-1]) if len(k) else None


def taban_wson(kume, maske, kayitsiz_ist=None):
    """Sürüm 3 3a: True = küme atılır. kayitsiz_ist: istasyon indisi → kayıtsız saniye maskesi (yoksa hepsi kayıtlı)."""
    uy = kume['uyeler']
    nt = 0
    for u in uy:
        k = w_son_acik(maske, None if kayitsiz_ist is None else kayitsiz_ist.get(u))
        if k is None:
            continue
        sinir = (k + 1) - 60
        nt += any(b >= sinir for kk, a, b in kume['parcalar'] if kk == u)
    return nt >= len(uy) / 2


def sag_kalan_var(ks, ist, maske, kural, wson=False):
    for k in ks:
        b = D.ayikla(ist, k, maske)
        at = any(b[x] for x in kural)
        if wson:
            at = at or taban_wson(k, maske)
        if not at:
            return True
    return False


def D15(rng, n, mson):
    alg, at_dogru, at_tam, at_3a_yok, at_v2 = [], [], [], [], []
    for _ in range(n):
        st = []
        for i in range(3):
            nl = [(lambda yd: (yd[0] * PROFIL, yd[1]))(D.gurultu(rng, 'gauss')) for _ in range(3)]
            st.append((D.C(nl, [None] * 3, 0, 0), D.C(nl, [None] * 3, 0, 1)))
        mk = np.zeros(D.T, bool)
        if mson:
            mk[D.T - mson:] = True
        ks, ist = D.pencere(st, mk)
        alg.append(bool(ks))
        if ks:
            at_dogru.append(not sag_kalan_var(ks, ist, mk, set(), wson=True))
            at_tam.append(not sag_kalan_var(ks, ist, mk, {'darbe_dogru', 'sizinti_dogru'}, wson=True))
            at_3a_yok.append(not sag_kalan_var(ks, ist, mk, {'darbe_dogru', 'sizinti_dogru'}))
            at_v2.append(not sag_kalan_var(ks, ist, mk, {'taban'}))      # sürüm 2: parça sonu ≥ W sonu − 60
    o = D.oran
    return dict(maskeli_son_s=mson, algilama_ayiklamasiz=o(alg), taban_3a_Wson_atilma=o(at_dogru),
                tam_kural_atilma=o(at_tam), yanlis_3a_yok_atilma=o(at_3a_yok),
                yanlis_surum2_W_sonu_atilma=o(at_v2))


def main():
    ad, tohum, n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    rng = np.random.default_rng(tohum)
    if ad != 'D15':
        sys.exit('bilinmeyen denetim')
    mson = int(sys.argv[4])
    r = D15(rng, n, mson)
    print(json.dumps(dict(denetim=ad, ek=str(mson), tohum=tohum, n=n, sonuc=r), ensure_ascii=False))


if __name__ == '__main__':
    main()
