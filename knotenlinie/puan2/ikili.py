"""İkili (Bernoulli) olabilirlik: p = 1 − exp(−λ); Bayona 2022; pyCSEP binomial_evaluations ile aynı tanım."""
from __future__ import annotations

import numpy as np

from knotenlinie.karsilastir.puan import PuanHatasi, oranlar, sayilar


def _ln_p(lam):
    """ln(1 − e^{−λ}) küçük λ'da kesin (−expm1)."""
    with np.errstate(divide='ignore'):
        return np.log(-np.expm1(-lam))


def ikili_logL(beklenen, gozlem):
    """Σ_y=1 ln(1−e^{−λ}) − Σ_y=0 λ. Gözlemli ve λ=0 → −inf (tabanlama yok)."""
    lam, n = oranlar(beklenen).ravel(), sayilar(gozlem).ravel()
    if lam.shape != n.shape:
        raise PuanHatasi('Oran ve gözlem şekilleri farklı')
    y = n > 0
    if (lam[y] == 0).any():
        return float('-inf')
    return float(_ln_p(lam[y]).sum() - lam[~y].sum())


def ikili_logL_defter(lam_benzersiz_olay, Lam_toplam):
    """Defterden tam ikili logL: yalnız olay hücre-gün-kutularının λ'sı + toplam Λ.

    Olaysız hücre-gün-kutular ln(1−p) = −λ verir; toplamları Λ_toplam − Σ λ_olay.
    lnL = Σ_olay [ln(1−e^{−λ}) + λ] − Λ_toplam.  λ→0'da Poisson'un olay terimine yakınsar.
    """
    lam = oranlar(lam_benzersiz_olay)
    if (lam == 0).any():
        return float('-inf')
    return float((_ln_p(lam) + lam).sum() - float(Lam_toplam))


def benzersiz_olay_lam(gun, hucre, kutu, lam):
    """Aynı (gün, hücre, kutu) için tek λ (ikili gözlem tek 1'dir)."""
    import pandas as pd
    d = pd.DataFrame(dict(g=np.asarray(gun).astype(str), h=np.asarray(hucre), k=np.asarray(kutu),
                          lam=np.asarray(lam, float)))
    return d.drop_duplicates(['g', 'h', 'k'])['lam'].to_numpy(float)


def _k_farkli(cdf, k, rng):
    """Ağırlığı cdf'den gelen kutulardan k farklı kutu (ardışık örnekleme, reddederek)."""
    secili, goruldu = [], set()
    while len(secili) < k:
        u = rng.random(max(16, int((k - len(secili)) * 1.3) + 8))
        for j in np.searchsorted(cdf, u, side='right'):
            if j not in goruldu:
                goruldu.add(j)
                secili.append(j)
                if len(secili) == k:
                    break
    return np.fromiter(secili, int, count=k)


def _k_farkli_tek(cdf, k, rs):
    """pyCSEP `_simulate_catalog` ile aynı akış: RandomState, tek tek uniform(0,1) çekimi."""
    secili, goruldu = [], set()
    while len(secili) < k:
        j = int(np.searchsorted(cdf, rs.uniform(0, 1), side='right'))
        if j not in goruldu:
            goruldu.add(j)
            secili.append(j)
    return np.fromiter(secili, int, count=k)


def ikili_kosullu_test(beklenen, gozlem, *, tekrar=10000, tohum=20261007, alfa=0.05,
                       uretec='pcg64', simulasyon_dondur=False):
    """pyCSEP `_binary_likelihood_test` protokolü: gözlenen dolu kutu sayısı kadar farklı kutu,
    ağırlık ∝ λ, alt kuyruk p = #(sim ≤ gözlenen)/R. Ek olarak (1+k)/(1+R) saklanır.

    ``uretec='pcg64'`` üretim (default_rng). ``'pycsep'`` yalnız çapraz kontrol içindir
    (RandomState + tek tek çekim: pyCSEP ile birebir aynı simülasyon dizisi)."""
    lam, n = oranlar(beklenen).ravel(), sayilar(gozlem).ravel()
    if lam.shape != n.shape or tekrar < 1 or int(tekrar) != tekrar or not 0 < alfa < 1:
        raise PuanHatasi('İkili test şekli/tekrar/alfa geçersiz')
    k = int((n > 0).sum())
    if k == 0:
        return dict(p=None, gecti=False, sebep='dolu kutu yok', tekrar=int(tekrar))
    toplam = float(lam.sum())
    if (lam > 0).sum() < k:
        return dict(p=0.0, gecti=False, sebep='pozitif kutu sayısı < dolu kutu', tekrar=int(tekrar))
    obs = ikili_logL(lam, n)
    if not np.isfinite(obs):
        return dict(p=0.0, p_laplace=1.0 / (tekrar + 1), gecti=False, logL=obs,
                    sebep='gözlemli sıfır oran', tekrar=int(tekrar))
    cdf = np.cumsum(lam) / toplam
    c = np.zeros_like(lam)
    pos = lam > 0
    c[pos] = _ln_p(lam[pos]) + lam[pos]
    if uretec == 'pycsep':
        rs = np.random.RandomState(tohum)
        cek = lambda: _k_farkli_tek(cdf, k, rs)
    elif uretec == 'pcg64':
        rng = np.random.default_rng(tohum)
        cek = lambda: _k_farkli(cdf, k, rng)
    else:
        raise PuanHatasi('uretec pcg64 ya da pycsep olmalı')
    sim = np.empty(int(tekrar))
    for i in range(int(tekrar)):
        sim[i] = c[cek()].sum() - toplam
    alt = int((sim <= obs).sum())
    p = alt / tekrar
    out = dict(p=float(p), p_laplace=float((alt + 1) / (tekrar + 1)), gecti=bool(p >= alfa), logL=obs,
               tekrar=int(tekrar), tohum=int(tohum), dolu_kutu=k, sebep=None)
    if simulasyon_dondur:
        out['simulasyon'] = sim
    return out
