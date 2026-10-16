"""Hiyerarşik büzülme: ortak parametre uzayı, gözlenen bilgi (Hessian) ve çekirdek havuzu.

Karşılaştırılabilir parametre vektörü (log uzayında, 7 bileşen):
  log K_ref, log c, log alpha, log p, log D_ref, log q, log(gamma + GAMMA_OFS)
K_ref = K 10^{alpha (M_REF - Mc0)} ve D_ref = D 10^{gamma (M_REF - Mc0)}: bölgenin kendi
referans büyüklüğü Mc0'dan ortak M_REF'e taşınır. Zaman gün, uzay km. mu bölgeye özgüdür,
büzülmez. Çekirdek = bölge ayarlarının log uzayında ters varyans ağırlıklı ortalaması.
"""
from __future__ import annotations

import numpy as np
from scipy.special import expit

from knotenlinie.etas import model as M
from knotenlinie.etas_mc25.mle import coz
from knotenlinie.ortak_zemin.ayar import dallanma

M_REF = 3.5
GAMMA_OFS = 0.05
ADLAR = ('K_ref', 'c', 'alpha', 'p', 'D_ref', 'q', 'gamma')
DALLANMA_SINIR = 0.999


def tema(th, mc0, m_ref=M_REF):
    """Parametre sözlüğü -> 7 bileşenli log vektörü."""
    dm = float(m_ref) - float(mc0)
    return np.array([np.log(th['K']) + M.LN10 * th['alpha'] * dm,
                     np.log(th['c']), np.log(th['alpha']), np.log(th['p']),
                     np.log(th['D']) + M.LN10 * th['gamma'] * dm,
                     np.log(th['q']), np.log(th['gamma'] + GAMMA_OFS)])


def tema_v(v, b, mc0, m_ref=M_REF):
    return tema(coz(v, b, 'ortak'), mc0, m_ref)


def tema_jakobi(v, b, mc0, m_ref=M_REF, h=1e-6):
    """d tema / d v (7x8), merkezi fark."""
    v = np.asarray(v, float)
    J = np.zeros((7, len(v)))
    for k in range(len(v)):
        e = np.zeros(len(v)); e[k] = h
        J[:, k] = (tema_v(v + e, b, mc0, m_ref) - tema_v(v - e, b, mc0, m_ref)) / (2 * h)
    return J


def gozlenen_bilgi(L, x, h=1e-4):
    """-logL'nin v'ye göre Hessian'ı (toplam logL; analitik gradyanın merkezi farkı)."""
    x = np.asarray(x, float)
    n = len(L.t)
    H = np.zeros((len(x), len(x)))
    for k in range(len(x)):
        e = np.zeros(len(x)); e[k] = h * (1 + abs(x[k]))
        gp = L.objectif(x + e, 'ortak')[1] * n
        gm = L.objectif(x - e, 'ortak')[1] * n
        H[:, k] = (gp - gm) / (2 * e[k])
    return 0.5 * (H + H.T)


def tema_kovaryans(L, x, mc0, h=1e-4):
    """Delta yöntemiyle 7x7 log-tema kovaryansı; tekil yönler büyük varyans alır."""
    H = gozlenen_bilgi(L, x, h)
    w, V = np.linalg.eigh(H)
    zemin = 1e-8 * max(w.max(), 1e-12)
    w_s = np.maximum(w, zemin)
    cov_v = (V / w_s) @ V.T
    J = tema_jakobi(x, L.b, mc0)
    cov = J @ cov_v @ J.T
    return 0.5 * (cov + cov.T), dict(hessian_ozdeger_min=float(w.min()), hessian_ozdeger_max=float(w.max()),
                                     tekil_yon=int((w < zemin).sum()))


def bolge_kaydi(ad, fit, L, mc0, kovaryans=True):
    """MLE sonucundan çekirdeğe girecek bölge kaydı."""
    th = fit['parametreler']
    g = tema(th, mc0)
    kayit = dict(ad=ad, mc0=float(mc0), b=float(L.b), parametreler={k: float(v) for k, v in th.items()},
                 tema=g.tolist(), dallanma=float(fit['dallanma']), basari=bool(fit['basari']),
                 logL=float(fit['logL']), n_olay=int(len(L.t)), x=list(map(float, fit['x'])))
    if kovaryans:
        cov, tani = tema_kovaryans(L, fit['x'], mc0)
        kayit.update(tema_var=np.diag(cov).tolist(), tema_std=np.sqrt(np.maximum(np.diag(cov), 0)).tolist(),
                     kovaryans_tani=tani)
    return kayit


def uygun(kayit):
    """Önceden yazılı kapı: yakınsamış ve dallanma < 0,999; varyanslar sonlu pozitif."""
    if not kayit.get('basari') or not kayit['dallanma'] < DALLANMA_SINIR:
        return False
    var = np.asarray(kayit.get('tema_var', []), float)
    return bool(var.size == 7 and np.isfinite(var).all() and (var > 0).all())


def havuz(kayitlar, gevsek=False):
    """Bölge ayarlarının log uzayında ters varyans ağırlıklı ortalaması (bileşen bileşen).

    Sıkı (varsayılan): `uygun` olmayan bölge tamamen dışlanır; hiçbiri kalmazsa None.
    Gevşek (KURAL.md Ek): dallanma kapısı yalnız K_ref bileşenine uygulanır (tavandaki n'de K
    yalnız tavan kısıtıyla belirlenir); öteki bileşenler yakınsayan her bölgeden gelir.
    `maske[j]` False ise j. bileşen için hiçbir bölge kalmamıştır (ceza o bileşene uygulanmaz).
    """
    def ok_bilesen(k, j):
        var = np.asarray(k.get('tema_var', []), float)
        if not k.get('basari') or var.size != 7 or not np.isfinite(var[j]) or var[j] <= 0:
            return False
        return (not gevsek) or j != 0 or k['dallanma'] < DALLANMA_SINIR
    if not gevsek:
        ok = [k for k in kayitlar if uygun(k)]
        if not ok:
            return None
        masks = [[True] * 7 for _ in ok]
    else:
        ok = [k for k in kayitlar if k.get('basari')]
        masks = [[ok_bilesen(k, j) for j in range(7)] for k in ok]
    cek = np.full(7, np.nan); var = np.full(7, np.nan); Q = np.full(7, np.nan)
    pay = {k['ad']: [0.0] * 7 for k in ok}
    for j in range(7):
        sel = [i for i, m in enumerate(masks) if m[j]]
        if not sel:
            continue
        g = np.array([ok[i]['tema'][j] for i in sel])
        w = 1.0 / np.array([ok[i]['tema_var'][j] for i in sel])
        cek[j] = (w * g).sum() / w.sum(); var[j] = 1.0 / w.sum(); Q[j] = (w * (g - cek[j]) ** 2).sum()
        for i, wi in zip(sel, w):
            pay[ok[i]['ad']][j] = float(wi / w.sum())
    maske = np.isfinite(cek)
    if not maske.any():
        return None
    return dict(tema=[None if not np.isfinite(x) else float(x) for x in cek], maske=maske.tolist(),
                var=[None if not np.isfinite(x) else float(x) for x in var],
                uyeler=[k['ad'] for k in ok],
                dislanan=[dict(ad=k['ad'], dallanma=k['dallanma'], basari=k['basari'])
                          for k in kayitlar if k not in ok],
                agirlik_payi=pay, heterojenlik_Q=[None if not np.isfinite(x) else float(x) for x in Q],
                serbestlik=len(ok) - 1, adlar=list(ADLAR), m_ref=M_REF, gevsek=bool(gevsek))


def tek_cekirdek(kayit):
    """Tek bölgeli (zaman havuzu) çekirdek; K_ref kapısı gevşek kurala göre."""
    maske = [True] * 7
    if kayit['dallanma'] >= DALLANMA_SINIR:
        maske[0] = False
    return dict(tema=list(kayit['tema']), maske=maske, uyeler=[kayit['ad']], gevsek=True,
                dislanan=[], serbestlik=0, adlar=list(ADLAR), m_ref=M_REF)
