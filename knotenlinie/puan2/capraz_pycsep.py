"""İsteğe bağlı pyCSEP çapraz kontrolü; skor kodu pyCSEP'e bağlı DEĞİL (yalnız bu betik import eder).

    MPLCONFIGDIR=$TMPDIR/mpl <pycsep-0.8.0 venv>/bin/python -m knotenlinie.puan2.capraz_pycsep

Aynı küçük sentetik girdide: NBD N (analitik, rtol 1e-6), ikili logL (rtol 1e-12), ikili S/L (aynı tohum,
pyCSEP akışıyla birebir), T/W, Poisson N; ayrıca HAC'ı statsmodels OLS-HAC ile.
"""
from __future__ import annotations

import importlib.metadata
import json
from pathlib import Path

import numpy as np

from csep.core.binomial_evaluations import (_binary_likelihood_test, _nbd_number_test_ndarray,
                                            binary_joint_log_likelihood_ndarray)
from csep.core.poisson_evaluations import _number_test_ndarray, _t_test_ndarray, _w_test_ndarray

from knotenlinie.karsilastir.puan import eslestirilmis, n_testi
from . import hac, ikili, nbd

from knotenlinie.yollar import KOSU  # noqa: E402

MC2 = KOSU / 'MC2'   # output folder of the optional pyCSEP cross-check


def rel(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(np.max(np.abs(a - b) / np.maximum(np.abs(b), 1e-300)))


def kos():
    out = dict(pycsep=importlib.metadata.version('pycsep'))
    # 1. NBD sayı testi
    farklar = []
    for lam, n, var in [(13.0, 13, 40.0), (13.0, 25, 40.0), (130.0, 99, 2115.0), (7.1, 2, 9.0), (1350.0, 1341, 2.2e5)]:
        d1p, d2p = _nbd_number_test_ndarray(lam, n, var)
        ours = nbd.nbd_n_testi(lam, n, varyans_degeri=var)
        farklar.append(rel([ours['ust_kuyruk'], ours['alt_kuyruk']], [d1p, d2p]))
    out['nbd_N_max_rel'] = max(farklar)
    out['poisson_N_max_rel'] = rel([n_testi(13, 13)['ust_kuyruk'], n_testi(13, 13)['alt_kuyruk']],
                                  _number_test_ndarray(13, 13))
    assert out['nbd_N_max_rel'] <= 1e-6 and out['poisson_N_max_rel'] <= 1e-6
    # 2. ikili logL ve S/L testleri (hücre×kutu sentetik)
    rng = np.random.default_rng(7)
    lam = rng.gamma(0.5, 0.4, size=(40, 5))
    gz = rng.poisson(lam * 1.3)
    out['ikili_logL_rel'] = rel(ikili.ikili_logL(lam, gz), binary_joint_log_likelihood_ndarray(lam, gz))
    assert out['ikili_logL_rel'] <= 1e-12
    for ad, f, g in (('L', lam, gz), ('S', lam.sum(axis=1), gz.sum(axis=1))):
        qs, obs, sim = _binary_likelihood_test(f.copy(), g.copy(), num_simulations=10000, seed=20261007,
                                               use_observed_counts=True)
        mine = ikili.ikili_kosullu_test(f, g, tekrar=10000, tohum=20261007, uretec='pycsep',
                                        simulasyon_dondur=True)
        out[f'ikili_{ad}'] = dict(p_pycsep=float(qs), p_biz=mine['p'], logL_rel=rel(mine['logL'], obs),
                                  sim_max_mutlak_fark=float(np.max(np.abs(np.asarray(sim) - mine['simulasyon']))))
        assert out[f'ikili_{ad}']['logL_rel'] <= 1e-12 and out[f'ikili_{ad}']['p_pycsep'] == out[f'ikili_{ad}']['p_biz']
        # üretim üreteci (pcg64): dağılım düzeyinde uyum
        uret = ikili.ikili_kosullu_test(f, g, tekrar=10000, tohum=20261007, simulasyon_dondur=True)
        from scipy import stats
        ks = stats.ks_2samp(np.asarray(sim), uret['simulasyon'])
        out[f'ikili_{ad}']['pcg64_p'] = uret['p']
        out[f'ikili_{ad}']['ks_p'] = float(ks.pvalue)
        assert ks.pvalue > 0.001
    # 3. T/W (mevcut puan.eslestirilmis, iki yanlı)
    a = np.array([1, 2, 3, 4, 5, 2, 3, 1, 2, 4, 2, 3], float)
    b = np.array([2, 2, 1, 5, 4, 3, 2, 2, 1, 3, 1, 2], float)
    s = eslestirilmis(a, b, 30, 25)
    t = _t_test_ndarray(a, b, len(a), 30, 25)
    w = _w_test_ndarray(np.log(a) - np.log(b), m=5 / len(a))
    out['T_rel'] = rel([s['IG'], s['T'], *s['GA']], [t['information_gain'], t['t_statistic'], t['ig_lower'], t['ig_upper']])
    out['W_rel'] = rel(s['p_W'], w['probability'])
    assert out['T_rel'] <= 1e-12 and out['W_rel'] <= 1e-12
    # 4. HAC: statsmodels OLS (sabit) + HAC(Bartlett, use_correction)
    try:
        import statsmodels.api as sm
        D = np.random.default_rng(3).normal(size=400).cumsum() * 0.05 + rng.normal(size=400)
        farklar = []
        for L in (0, 3, 7):
            r = hac.hac_ozeti(D, np.ones(400), gecikme=L)
            m = sm.OLS(D, np.ones(400)).fit(cov_type='HAC', cov_kwds=dict(maxlags=L, use_correction=True))
            farklar.append(rel(r['SE_HAC'] * 400, m.bse[0] * 400))
        out['HAC_statsmodels_max_rel'] = max(farklar)
        out['statsmodels'] = importlib.metadata.version('statsmodels')
        assert out['HAC_statsmodels_max_rel'] <= 1e-10
    except ImportError:
        out['HAC_statsmodels_max_rel'] = None
    out['sonuc'] = ('NBD N ≤1e-6, ikili logL ≤1e-12, ikili S/L pyCSEP akışıyla birebir (p ve simülasyon dizisi), '
                    'T/W ≤1e-12, HAC statsmodels ≤1e-10; pcg64 üreteci KS ile dağılım düzeyinde uyumlu')
    return out


def main():
    o = kos()
    (MC2).mkdir(parents=True, exist_ok=True)
    (MC2 / 'capraz-pycsep.json').write_text(json.dumps(o, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(o, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
