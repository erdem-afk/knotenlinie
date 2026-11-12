"""İNCELEME-2: taban kayması (3a) için ayırt edici yapay denetim adayı (yalnız yapay).
Gürültü profili: R'nin son `rampa` sn'sinde 2-8 Hz genliği 1'den K'ye doğrusal yükselir, W boyunca K'de kalır
(sabah artışı vekili). Ayrıca 'maskeli son': W'nin son `mson` sn'si maskeli iken 3a'nın W sonu ve
"son maskesiz saniye" tanımlarıyla davranışı.
Kullanım: python3 -I -B o4b.py <tohum> <n> <K> <rampa_s> <mson_s>
"""
import json, sys
import numpy as np
sys.path.insert(0, '/home/user/knotenlinie/kayit/turetme/tr7')
import tr7_onkayit_denetim2 as D  # noqa

tohum, n, K, rampa, mson = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5])
rng = np.random.default_rng(tohum)
ts = D.t_ornek
BAS = float(sys.argv[6]) if len(sys.argv) > 6 else -rampa
prof = np.clip((ts - (D.R_S + BAS)) / rampa, 0, 1) * (K - 1) + 1


def gur():
    y, d = D.gurultu(rng, 'gauss')
    return y * prof, d


alg, at_w, at_acik, at_yok = [], [], [], []
for _ in range(n):
    st = []
    for i in range(3):
        nl = [gur() for _ in range(3)]
        st.append((D.C(nl, [None] * 3, 0, 0), D.C(nl, [None] * 3, 0, 1)))
    mk = np.zeros(D.T, bool)
    if mson:
        mk[D.T - mson:] = True
    ks, ist = D.pencere(st, mk)
    alg.append(bool(ks))
    if ks:
        # metin: parça sonu >= W sonu - 60
        at_w.append(not D.kalan(ks, ist, mk, {'taban'}))
        # öneri: parça sonu >= son maskesiz saniye - 60
        son = D.W_S - (mson if mson else 0)
        ok = False
        for k in ks:
            nt = sum(any(b >= son - 60 for kk, a, b in k['parcalar'] if kk == u) for u in k['uyeler'])
            if nt < len(k['uyeler']) / 2:
                ok = True
        at_acik.append(not ok)
print(json.dumps(dict(tohum=tohum, n=n, K=K, rampa=rampa, mson=mson, algilama=float(np.mean(alg)),
                      taban_metin_atilma=float(np.mean(at_w)) if at_w else None,
                      taban_son_maskesiz_atilma=float(np.mean(at_acik)) if at_acik else None)))
