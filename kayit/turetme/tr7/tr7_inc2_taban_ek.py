import json, sys
import numpy as np
sys.path.insert(0, '/home/user/knotenlinie/kayit/turetme/tr7')
import tr7_onkayit_denetim2 as D  # noqa
rng = np.random.default_rng(int(sys.argv[1])); n = int(sys.argv[2])
prof = np.clip((D.t_ornek - (D.R_S + 300)) / 900, 0, 1) * 1 + 1
sag_tabansiz, sag_tam = [], []
for _ in range(n):
    st = []
    for i in range(3):
        nl = [(lambda yd: (yd[0] * prof, yd[1]))(D.gurultu(rng, 'gauss')) for _ in range(3)]
        st.append((D.C(nl, [None] * 3, 0, 0), D.C(nl, [None] * 3, 0, 1)))
    z = np.zeros(D.T, bool)
    ks, ist = D.pencere(st, z)
    if ks:
        sag_tabansiz.append(D.kalan(ks, ist, z, {'darbe_dogru', 'sizinti_dogru'}))
        sag_tam.append(D.kalan(ks, ist, z, D.TAM))
print(json.dumps(dict(tohum=int(sys.argv[1]), n=n, n_alg=len(sag_tam), sag_3a_siz=float(np.mean(sag_tabansiz)), sag_tam=float(np.mean(sag_tam)))))
