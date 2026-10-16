"""İsteğe bağlı pyCSEP çapraz kontrolü; üretim kodu pyCSEP'e bağlı değil."""
import importlib.metadata
import json
from pathlib import Path

import numpy as np
from csep.core.poisson_evaluations import (
    _t_test_ndarray, _w_test_ndarray, _number_test_ndarray, _poisson_likelihood_test,
)
from csep.utils.stats import poisson_joint_log_likelihood_ndarray

from .puan import eslestirilmis, log_olabilirlik, n_testi, kosullu_test


def main():
    # Oran integral farkı sıfır değil; sadece olay log oranını test etmek yetmez.
    a = np.array([1, 2, 3, 4, 5, 2, 3, 1, 2, 4, 2, 3], float)
    b = np.array([2, 2, 1, 5, 4, 3, 2, 2, 1, 3, 1, 2], float)
    s = eslestirilmis(a, b, 30, 25)
    t = _t_test_ndarray(a, b, len(a), 30, 25)
    w = _w_test_ndarray(np.log(a) - np.log(b), m=5/len(a))
    np.testing.assert_allclose([s['IG'], s['T'], *s['GA']],
                               [t['information_gain'], t['t_statistic'], t['ig_lower'], t['ig_upper']], rtol=1e-12)
    np.testing.assert_allclose(s['p_W'], w['probability'], rtol=1e-12)
    nt = n_testi(13, 13)
    np.testing.assert_allclose([nt['ust_kuyruk'], nt['alt_kuyruk']], _number_test_ndarray(13, 13), rtol=1e-12)
    lam, n = np.array([8., 3., 2.]), np.array([5, 6, 2])
    raw = poisson_joint_log_likelihood_ndarray(n * np.log(lam), n, lam.sum())
    np.testing.assert_allclose(raw, log_olabilirlik(lam, n), rtol=1e-12)
    own = kosullu_test(lam, n, tekrar=10000, tohum=20261005)
    pc, ll, _ = _poisson_likelihood_test(lam, n, num_simulations=10000, seed=20261005,
                                        use_observed_counts=True, normalize_likelihood=True)
    np.testing.assert_allclose(ll, own['logL'], rtol=1e-12)
    # İki farklı üreteç/örnekleme + bizde (k+1)/(R+1), pyCSEP'te k/R.
    tolerance = 5 * np.sqrt((own['p']*(1-own['p']) + pc*(1-pc))/10000) + 1/10000
    assert abs(pc - own['p']) < tolerance
    result = dict(pycsep=importlib.metadata.version('pycsep'), IG=s['IG'], T=s['T'], W_p=s['p_W'],
                  logL=raw, kosullu_p_biz=own['p'], kosullu_p_pycsep=float(pc), tolerans=float(tolerance),
                  sonuc='LL, IG, T/GA, W ve N 1e-12; koşullu S/M çekirdeği Monte Carlo toleransında')
    from knotenlinie.yollar import KOSU
    p = KOSU / 'capraz-pycsep.json'
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(result, indent=2) + '\n')
    print(result)


if __name__ == '__main__':
    main()
