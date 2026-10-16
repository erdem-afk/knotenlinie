"""Poisson skoru, Rhoades T/W ve Zechar N/S/M testleri."""
from __future__ import annotations

import numpy as np
from scipy import stats
from scipy.special import gammaln, xlogy


class PuanHatasi(ValueError):
    """Skor girdisi veya gözlemli hücrenin olasılığı geçersiz."""


def oranlar(x):
    x = np.asarray(x, dtype=float)
    if not np.isfinite(x).all() or (x < 0).any() or not np.isfinite(x.sum()):
        raise PuanHatasi("Beklenen sayılar sonlu ve negatif olmayan olmalı")
    return x


def sayilar(x):
    x = np.asarray(x, dtype=float)
    if not np.isfinite(x).all() or (x < 0).any() or (x != np.floor(x)).any():
        raise PuanHatasi("Gözlemler negatif olmayan tamsayı olmalı")
    return x


def log_olabilirlik(beklenen, gozlem):
    """0 log 0=0; gözlemli sıfır oran -inf, tabanlama yapılmaz."""
    lam, n = oranlar(beklenen), sayilar(gozlem)
    if lam.shape != n.shape:
        raise PuanHatasi("Oran ve gözlem şekilleri farklı")
    return float(np.sum(xlogy(n, lam) - lam - gammaln(n + 1)))


def eslestirilmis(olay_model, olay_taban, toplam_model, toplam_taban, alfa=0.05):
    """Günlük hücre oranlarından tam integral terimli IG ve iki yönlü T/W."""
    a, b = oranlar(olay_model), oranlar(olay_taban)
    if a.ndim != 1 or a.shape != b.shape or not 0 < alfa < 1:
        raise PuanHatasi("Eşleştirilmiş olay dizileri veya alfa geçersiz")
    ta, tb = oranlar([toplam_model, toplam_taban])
    n = len(a)
    if n and ((a == 0).any() or (b == 0).any()):
        raise PuanHatasi("Gözlemli sıfır oran: IG/T/W tanımsız; model kazanamaz")
    if not n:
        return dict(N=0, IG=None, IG_olay=None, integral_terimi=None,
                    T=None, p_T=None, p_W=None, W=None, GA=None, sebep="N=0")
    x = np.log(a) - np.log(b)
    duzeltme = float((ta - tb) / n)
    y = x - duzeltme
    ig = float(y.mean())
    result = dict(N=n, IG=ig, IG_olay=float(x.mean()), integral_terimi=-duzeltme,
                  T=None, p_T=None, p_W=None, W=None, GA=None, sebep=None)
    if n < 2:
        result['sebep'] = 'N<2'
        return result
    se = float(np.std(x, ddof=1) / np.sqrt(n))
    if se == 0:
        t, p = (0.0, 1.0) if ig == 0 else (float(np.copysign(np.inf, ig)), 0.0)
        ga = [ig, ig]
    else:
        t = ig / se
        p = float(2 * stats.t.sf(abs(t), n - 1))
        h = float(stats.t.ppf(1 - alfa / 2, n - 1) * se)
        ga = [ig - h, ig + h]
    # Yuvarlama yok: eşit modeller tam sıfır; bağlar/zero yöntemi açık.
    if np.all(y == 0):
        w, pw = 0.0, 1.0
    else:
        wtest = stats.wilcoxon(y, zero_method='wilcox', correction=False,
                              alternative='two-sided', method='approx')
        w, pw = float(wtest.statistic), float(wtest.pvalue)
    result.update(T=t, p_T=p, W=w, p_W=pw, GA=ga, SE=se, varyans_sifir=se == 0)
    return result


def n_testi(toplam, n, alfa=0.05):
    """İki Poisson kuyruğu: P(X>=N), P(X<=N), her biri alfa/2."""
    lam = float(oranlar([toplam])[0])
    n = int(sayilar([n])[0])
    if not 0 < alfa < 1:
        raise PuanHatasi("alfa (0,1) içinde olmalı")
    ust, alt = float(stats.poisson.sf(n - 1, lam)), float(stats.poisson.cdf(n, lam))
    return dict(beklenen=lam, N=n, ust_kuyruk=ust, alt_kuyruk=alt,
                gecti=bool(min(ust, alt) >= alfa / 2))


def kosullu_test(beklenen, gozlem, *, tekrar=10000, tohum=20261005, alfa=0.05):
    """S/M: N'ye normalize marjinal, sabit N multinomial alt kuyruk."""
    lam, n = oranlar(beklenen).ravel(), sayilar(gozlem).ravel()
    if lam.shape != n.shape or tekrar < 1 or int(tekrar) != tekrar or not 0 < alfa < 1:
        raise PuanHatasi("Koşullu test şekli/tekrar/alfa geçersiz")
    N = int(n.sum())
    if N == 0:
        return dict(p=None, gecti=False, sebep='N=0; şekil sınanamaz', tekrar=tekrar)
    if lam.sum() == 0:
        return dict(p=0.0, gecti=False, sebep='Toplam oran sıfır', tekrar=tekrar)
    probs = lam / lam.sum()
    normal = probs * N
    obs = log_olabilirlik(normal, n)
    if not np.isfinite(obs):
        return dict(p=0.0, gecti=False, logL=obs, sebep='Gözlemli sıfır oran', tekrar=tekrar)
    # Sıfır olasılıklı hücreler simülasyonda zaten hiç olay alamaz.
    sec = probs > 0
    probs, normal = probs[sec], normal[sec]
    rng = np.random.default_rng(tohum)
    alt = 0
    for _ in range(int(tekrar)):
        sim = rng.multinomial(N, probs)
        ll = float(np.sum(xlogy(sim, normal) - normal - gammaln(sim + 1)))
        alt += ll <= obs
    p = float((alt + 1) / (tekrar + 1))
    return dict(p=p, gecti=bool(p >= alfa), logL=obs, tekrar=int(tekrar),
                tohum=int(tohum), sebep=None)


def tutarlilik(beklenen, gozlem, *, tekrar=10000, tohum=20261005, alfa=0.05):
    """Zaman toplamı (hücre,büyüklük); N iki, S/M tek alt kuyruk."""
    lam, n = oranlar(beklenen), sayilar(gozlem)
    if lam.ndim != 2 or lam.shape != n.shape:
        raise PuanHatasi("Tutarlılık (hücre,büyüklük) ister")
    nt = n_testi(lam.sum(), n.sum(), alfa)
    st = kosullu_test(lam.sum(axis=1), n.sum(axis=1), tekrar=tekrar, tohum=tohum, alfa=alfa)
    mt = kosullu_test(lam.sum(axis=0), n.sum(axis=0), tekrar=tekrar, tohum=tohum + 1, alfa=alfa)
    return dict(N=nt, S=st, M=mt, gecti=nt['gecti'] and st['gecti'] and mt['gecti'])


def holm(p_degerleri):
    """Önceden sabitlenmiş aile; ölçülemeyen p=1, sıra geri korunur."""
    p = np.asarray([1.0 if x is None else x for x in p_degerleri], float)
    if not np.isfinite(p).all() or ((p < 0) | (p > 1)).any():
        raise PuanHatasi("p-değerleri [0,1] içinde olmalı")
    sira = np.argsort(p, kind='stable')
    duzeltilmis = np.minimum(1, np.maximum.accumulate((len(p) - np.arange(len(p))) * p[sira]))
    out = np.empty_like(p)
    out[sira] = duzeltilmis
    return out.tolist()


def gectik(ciftler, model_testleri, *, alfa=0.05):
    """Üç İtalya karşılaştırması: tek üçlü Holm ailesi.

    İki statik taban (HAZFX, TripleS) ve düz ETAS; Holm düzeltmesi bu üç p değeri üzerinedir.
    Kör pencere açma kodu ön kayıt dondurulana kadar bu sürümde yoktur.
    """
    anahtar = ['italya_hazfx', 'italya_triples', 'italya_etas']
    if set(ciftler) != set(anahtar) or set(model_testleri) != {'italya'}:
        raise PuanHatasi("Hüküm tam üç İtalya karşılaştırması (düz ETAS dahil) ve tek bölge ister")
    p = holm([ciftler[k]['p_T'] for k in anahtar])
    kapilar = {k: bool(ciftler[k]['IG'] is not None and ciftler[k]['IG'] > 0 and v < alfa)
               for k, v in zip(anahtar, p)}
    return dict(gectik=all(kapilar.values()) and all(t['gecti'] for t in model_testleri.values()),
                p_T_holm=dict(zip(anahtar, p)), kapilar=kapilar)
