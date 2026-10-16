"""Stochastic declustering.

Zhuang, Ogata & Vere-Jones 2002, 10.1198/016214502760046925.  On top of the
fitted model, event j's background probability is

    phi_j = mu*u(x_j,y_j) / lambda(t_j,x_j,y_j)

and the probability that j was triggered by i is

    rho_ij = K*10^{alpha(M_i-M0)}/(t_j-t_i+c)^p * g(.) / lambda(t_j,x_j,y_j).

Then the iteration replaces the background rate by the expectation over phi,
refits mu (and u for space-time), recomputes phi and rho, and stops when
``|d ell| < 1e-4`` or at 50 iterations (both declared).  The outputs mirror the
reference implementation's names so they can be compared later: ``probs``
(per-event background probability), ``pmatr`` (parent-child probabilities),
``rates`` (background/total intensity on the grid).

For a space-time parameter file the declustering is the full space-time version (:func:`ayristir_uzay`): ``phi_j = mu u(x_j, y_j) / lambda(t_j, x_j, y_j)`` with the
kernel ``g`` at each event's exact location in the fit's km metric, the fit's exact ``G_i`` in the
compensator, and ``u`` refitted each round.  That refit is Zhuang,
Ogata & Vere-Jones (2002)'s variable-bandwidth Gaussian estimate (:func:`arka_plan_yogunlugu`), not
the coarse 0.1 degree histogram (still available as a named variant).  The event's own kernel is
left out at the events, and **each kernel is normalised by its own box mass**
(``u = sum_j phi_j K_j(x)/m_j / sum_j phi_j``, ``m_j`` the Gaussian's box mass from two ``ndtr``
terms) so ``int_box u dA = 1`` exactly and ``sum(arka_plan) = mu`` and the compensator
``mu (T - t0)`` are exact; ten ``ndtr``-checked cells sum to one.  The re-selection of ``n_p``
from ``{100, 200, 300, 400}`` on three declared non-box known answers (test, fitted-parameter regime and a NW-SE belt)
found **no candidate passing all three**, so nothing is adopted: ``NP_VARSAYILAN`` is ``None`` and the
production space-time declustering is **descriptive** (``u`` the fit's histogram, the background count from
``mu (T - t0)``).  The kernel runs only when a caller names an ``n_p``; its EM stops on
``max |d phi| <= PHI_DURMA`` and its logL is a leave-one-out pseudo-likelihood.  The starting ``u`` is
the fit's own (the unweighted histogram of the events), so the first round's log-likelihood is the fit's.
**The descriptive path is one phi pass at the fit's own ``theta[0]`` and unweighted
histogram, with no refit** (the reported count is exactly ``theta[0] (T - t0)``), and
``cekirdek = n_p is not None and not histogram``, so ``histogram=True`` with an explicit ``n_p`` is the
named exact-EM variant.
The **temporal marginal**,
``lambda(t) = mu + K sum_i A_i G_i (t - t_i + c)^-p`` (:func:`ayristir` with ``G``), stays as a named
variant; its ``phi`` is the background probability under that marginal, not the background/triggered separation's number.

mu and the triggering term are never merged; that separability is the whole
point of the background/triggered separation.  Clean-room implementation from the published equations; no code
copied from the pyetas package (AGPL), the CRAN ETAS package (GPL) or Zhuang's Fortran sd.

The space-time version normalises each kernel by its **own** box mass,
``u(x) = sum_j phi_j K_j(x)/m_j / sum_j phi_j``, so every background event's density is a
probability density on the box; the leave-one-out (own kernel out) stays.  ``n_p`` is
re-selected from ``{100, 200, 300, 400}`` by three declared non-box known answers (test, fitted-parameter
regime and a NW-SE belt recipe; :data:`NP_ADAYLARI`) and the kernel EM stops on ``max |d phi| <= PHI_DURMA`` (or
the declared iteration cap, reported); its log-likelihood is a leave-one-out pseudo-likelihood.  **No
candidate passes all three**, so :data:`NP_VARSAYILAN` is ``None``: the declustering is descriptive
(``u`` the fit's histogram, the background count from ``mu (T - t0)``) and the kernel runs only when a caller names an
``n_p``.
"""
from __future__ import annotations

import numpy as np
from scipy.special import ndtr
from scipy.spatial import cKDTree

from . import model as M

VARSAYILAN_ESIK = 1e-6
VARSAYILAN_DURMA = 1e-4
VARSAYILAN_AZAMI = 50
#: Zhuang et al. (2002)'s variable-kernel background estimate: the Gaussian bandwidth of event j
#: is its distance to the ``NP``-th nearest event (the event itself at distance 0, so the sorted
#: index ``NP``), floored at ``EPS_KM``; the estimate is the ``phi``-weighted sum of every event's
#: kernel.  **Nothing is adopted.**  The candidates ``{100, 200, 300,
#: 400}`` were run on the three declared non-box known answers (test 101-110, fitted-parameter regime 201-210 and the
#: NW-SE belt 301-310); no candidate passes all three (the belt's z for 300 is -3.31 and for 400
#: -6.35, the fitted-parameter regime's for 200 is +3.63), so the space-time declustering stays **descriptive**: ``u``
#: stays the fit's histogram and the background count is the fit's own ``mu (T - t0)``.  ``None``
#: is the unadopted placeholder; the calibration command may still run the kernel with an explicit
#: ``n_p``.  The earlier ``n_p = 10``
#: placeholder is gone.
NP_VARSAYILAN = None
#: The minimum bandwidth (km).
EPS_KM = 1.0
EPS_KM_VARSAYILAN = EPS_KM
#: The kernel EM stops when the largest per-event change in the
#: background probability between rounds is at most this, or at the declared iteration cap (which is
#: reported).  The kernel log-likelihood is a leave-one-out pseudo-likelihood.
PHI_DURMA = 1e-6
#: The candidates for the re-selected ``n_p``.  The adopted value (if
#: any) is the one that passes all three declared non-box known answers with the smallest maximum
#: |z|; ties go to the larger ``n_p``.  **No candidate passed**, so :data:`NP_VARSAYILAN` is
#: ``None``; the candidate table and verdict come from the calibration command and are pinned in the
#: small local test tier.
NP_ADAYLARI = (100, 200, 300, 400)
#: The named variable-kernel variant's default ``n_p`` when a caller asks for the kernel without naming
#: one.  It is **not** an adoption (no candidate was adopted): ``ayristir_uzay`` defaults
#: to the descriptive histogram (``n_p=None``) and only an explicit ``n_p`` runs the kernel.
NP_CEKIRDEK_VARSAYILAN = 10
#: ``True`` when an ``n_p`` has been adopted; ``False`` leaves the space-time
#: declustering descriptive.  Callers that need an adopted ``n_p`` refuse while this is ``False``.
NP_KABUL = NP_VARSAYILAN is not None


def _arka_plan_cekirdekleri(x, y, metrik, n_p: int = NP_CEKIRDEK_VARSAYILAN,
                            eps_km: float = EPS_KM_VARSAYILAN, kutu=None):
    """The variable-kernel background's parts in the fit's km metric.

    Returns ``(xk, yk, h, m)``: the events' km coordinates, each event's bandwidth (the distance to
    its ``n_p``-th event, the event itself at distance 0, floored at ``eps_km``) and each Gaussian's
    mass inside the box, ``m_j = [ndtr((x1-xk_j)/h_j) - ndtr((x0-xk_j)/h_j)] *`` the same in ``y``,
    because the box is a rectangle in km under the declared projection.
    """
    xk, yk = metrik.km(np.asarray(x, float), np.asarray(y, float))
    pts = np.column_stack([xk, yk])
    k = int(min(int(n_p) + 1, max(pts.shape[0], 1)))
    d, _ = cKDTree(pts).query(pts, k=k)
    d = np.asarray(d)
    if d.ndim == 1:
        d = d[:, None]
    h = np.maximum(d[:, -1], float(eps_km))
    x0, x1, y0, y1 = metrik.kutu_km(kutu)
    m = (ndtr((x1 - xk) / h) - ndtr((x0 - xk) / h)) * (ndtr((y1 - yk) / h) - ndtr((y0 - yk) / h))
    return xk, yk, h, m


def arka_plan_yogunlugu(x, y, phi, metrik, hedef=None, n_p: int = NP_CEKIRDEK_VARSAYILAN,
                        eps_km: float = EPS_KM_VARSAYILAN, chunk: int = 2000, kutu=None,
                        kendini_haric: bool = True) -> np.ndarray:
    """Zhuang, Ogata & Vere-Jones (2002)'s variable-kernel background density.

    ``u(z) = (sum_j phi_j K(z - z_j; h_j)) / (sum_j phi_j m_j)`` with a 2-D Gaussian ``K`` of
    bandwidth ``h_j`` = the distance from event j to its ``n_p``-th nearest event (the event itself at
    distance 0, so the ``n_p``-th *other* event), floored at ``eps_km``, and ``m_j`` the Gaussian's
    mass inside the box (two ``ndtr`` terms).  The box normalisation makes
    ``int_box u dA = 1`` exactly, so ``mu u`` is the intensity whose compensator is ``mu (T - t0)``
    and the ``rates`` grid sums to ``mu``.  With ``kendini_haric`` (default) and targets at the events
    the event's own kernel is left out of numerator and denominator (the adopted
    estimator: a lone event keeps its neighbours' kernels, so leave-one-out does not collapse the
    EM as the histogram did).  A grid target (``hedef``) never leaves one out.  Returns per deg^2
    (multiplied by the metric's Jacobian).
    """
    met = metrik
    xk, yk, h, m = _arka_plan_cekirdekleri(x, y, met, n_p, eps_km, kutu)
    phi = np.asarray(phi, float)
    # each kernel is normalised by its own box mass (phi_j / m_j) and the whole density by
    # sum(phi), so int_box u = 1 exactly (an earlier box normalisation sum(phi m) is replaced by the
    # per-kernel one)
    agirlik = np.where(m > 0.0, phi / np.where(m > 0.0, m, 1.0), 0.0)
    iki_h2 = 2.0 * h ** 2
    normal = 1.0 / (2.0 * np.pi * h ** 2)
    payda = float(np.sum(phi))
    if hedef is None:
        xh, yh = xk, yk
    else:
        xh, yh = met.km(np.asarray(hedef[0], float), np.asarray(hedef[1], float))
    cikti = np.empty(xh.size)
    for a in range(0, xh.size, int(chunk)):
        b = min(a + int(chunk), xh.size)
        d2 = (xh[a:b, None] - xk[None, :]) ** 2 + (yh[a:b, None] - yk[None, :]) ** 2
        K = np.exp(-d2 / iki_h2[None, :]) * normal[None, :]
        pay = (K * agirlik[None, :]).sum(1)
        if hedef is None and kendini_haric:
            pay = pay - agirlik[a:b] * normal[a:b]
            p_alt = payda - phi[a:b]
        else:
            p_alt = payda
        with np.errstate(divide="ignore", invalid="ignore"):
            cikti[a:b] = np.where(p_alt > 0.0, pay / p_alt, 0.0)
    return cikti * met.jakobiyen


def arka_plan_hucreleri(x, y, phi, kutu, metrik=None, dx: float = 0.1,
                        n_p: int = NP_CEKIRDEK_VARSAYILAN, eps_km: float = EPS_KM_VARSAYILAN,
                        chunk: int = 500) -> np.ndarray:
    """Exact per-cell integrals of the self-included box-normalised kernel background.

    The cells of :func:`knotenlinie.etas.model.hucre_kenarlari` tile the box and each Gaussian's cell
    masses sum to its box mass ``m_j``, so the returned shares sum to 1 to rounding; multiplied by
    ``mu`` they are the ``arka_plan`` grid of :func:`uzay_oranlari` and their sum is exactly ``mu``.
    """
    met = metrik if metrik is not None else M.yerel_metrik(kutu)
    xk, yk, h, m = _arka_plan_cekirdekleri(x, y, met, n_p, eps_km, kutu)
    # kernel j contributes K_j/m_j, whose box integral is one; the phi weights
    # are the shares (sum_j phi_j = 1)
    agirlik = np.asarray(phi, float) / float(np.sum(np.asarray(phi, float))) / m
    lo_k, la_k = M.hucre_kenarlari(kutu, dx)
    X = met.kx * (lo_k - met.lam0)
    Y = met.ky * (la_k - met.phi0)
    cikti = np.zeros((Y.size - 1, X.size - 1))
    for a in range(0, h.size, int(chunk)):
        b = min(a + int(chunk), h.size)
        dX = np.diff(ndtr((X[None, :] - xk[a:b, None]) / h[a:b, None]), axis=1)
        dY = np.diff(ndtr((Y[None, :] - yk[a:b, None]) / h[a:b, None]), axis=1)
        cikti += np.einsum("j,ja,jb->ab", agirlik[a:b], dY, dX)
    return cikti


def arka_plan_olasiliklari(theta, t, mags, m0, esik: float = VARSAYILAN_ESIK, G=None):
    """Return (phi per event, sparse (i, j, rho) triplets).

    ``G`` (default 1) is the per-parent box integral of a space-time fit.
    """
    t = np.asarray(t, float)
    mags = np.asarray(mags, float)
    mu, Kk, c, alpha, p = (float(v) for v in theta[:5])
    A, S, _ = M._zaman_cekirdek(np.asarray(theta[:5], float), t, mags, m0, G=G)
    lam = mu + Kk * S
    phi = mu / lam
    i_idx, j_idx, rho = [], [], []
    for j in range(t.size):
        if j == 0:
            continue
        gecmis = t[:j] < t[j]
        if not np.any(gecmis):
            continue
        k = A[:j][gecmis] * (t[j] - t[:j][gecmis] + c) ** (-p)
        r = Kk * k / lam[j]
        sec = r > esik
        if np.any(sec):
            idx = np.nonzero(gecmis)[0][sec]
            i_idx.extend(idx.tolist())
            j_idx.extend([j] * int(sec.sum()))
            rho.extend(r[sec].tolist())
    return phi, (np.asarray(i_idx, int), np.asarray(j_idx, int), np.asarray(rho, float))


def ayristir(theta, t, mags, m0, beta, t0, T, esik: float = VARSAYILAN_ESIK,
             durma: float = VARSAYILAN_DURMA, azami: int = VARSAYILAN_AZAMI, G=None) -> dict:
    """The Zhuang, Ogata & Vere-Jones (2002) iteration, mu re-estimated each round.

    ``G`` (default 1) is the per-parent box integral of a space-time fit: the iteration then
    runs on that fit's temporal marginal and its log-likelihood.
    """
    t = np.asarray(t, float)
    mags = np.asarray(mags, float)
    theta = np.asarray(theta[:5], float).copy()
    Gv = None if G is None else np.asarray(G, float)
    gecmis_logL = []
    for it in range(azami):
        phi, (ii, jj, rr) = arka_plan_olasiliklari(theta, t, mags, m0, esik, G=Gv)
        ell = M.logL_temporal(theta, t, mags, m0, beta, t0, T, G=Gv)
        gecmis_logL.append(float(ell))
        if it > 0 and abs(gecmis_logL[-1] - gecmis_logL[-2]) < durma:
            break
        theta = theta.copy()
        theta[0] = float(phi.sum() / (T - t0))
    phi, (ii, jj, rr) = arka_plan_olasiliklari(theta, t, mags, m0, esik, G=Gv)
    grid = np.linspace(t0, T, 200)
    carpan = np.ones(t.size) if Gv is None else Gv
    lam_grid = np.array([theta[0] + theta[1] * np.sum(
        carpan[t < x] * 10.0 ** (theta[3] * (mags[t < x] - m0)) * (x - t[t < x] + theta[2]) ** (-theta[4]))
        for x in grid])
    return {"probs": phi.tolist(), "pmatr": [[int(a), int(b), float(v)] for a, b, v in zip(ii, jj, rr)],
            "rates": {"t": grid.tolist(), "arka_plan": [float(theta[0])] * grid.size,
                      "toplam": lam_grid.tolist()},
            "iterasyon": it + 1, "logL_gecmisi": gecmis_logL, "logL": gecmis_logL[-1],
            "mu": float(theta[0]), "parametreler": M._sozluk(theta, M.ZAMAN_ADLARI),
            "arka_plan_sayisi_beklenen": float(phi.sum()), "esik": esik,
            "G_kullanildi": Gv is not None}


def auc(skorlar, etiketler) -> float:
    """Rank-based AUC; ``etiketler`` True = background (the positive class)."""
    s = np.asarray(skorlar, float)
    y = np.asarray(etiketler, bool)
    if y.all() or (~y).all():
        return float("nan")
    from scipy import stats
    poz = s[y]
    neg = s[~y]
    # P(score_pos > score_neg) via the Mann-Whitney U statistic
    U = stats.mannwhitneyu(poz, neg, alternative="greater").statistic
    return float(U / (poz.size * neg.size))


def ebeveyn_geri_kazanim(ii, jj, rr, ebeveyn) -> dict:
    """Fraction of triggered events whose highest-rho parent is the true parent."""
    en_iyi = {}
    for a, b, v in zip(ii, jj, rr):
        if b not in en_iyi or v > en_iyi[b][1]:
            en_iyi[b] = (int(a), float(v))
    dogru = 0
    toplam = 0
    for b, (a, _) in en_iyi.items():
        if ebeveyn[b] is None or ebeveyn[b] < 0:
            continue
        toplam += 1
        dogru += int(a == ebeveyn[b])
    return {"dogru": dogru, "toplam": toplam,
            "oran": (dogru / toplam) if toplam else float("nan")}


# --- the space-time declustering ------------------------------------

def uzay_arka_plan_olasiliklari(theta, t, mags, x, y, m0, kutu, u_olay=None, metrik=None,
                                esik: float = VARSAYILAN_ESIK, chunk: int = 500):
    """Space-time ``phi_j = mu u(x_j, y_j) / lambda(t_j, x_j, y_j)`` and the triplets ``(i, j, rho_ij)``.

    ``theta`` is the space-time vector ``(mu, K, c, alpha, p, D, q, gamma)`` with ``D`` in km of
    ``metrik`` (default :func:`knotenlinie.etas.model.yerel_metrik` of ``kutu``); ``x, y`` are longitudes and
    latitudes in degrees; ``u_olay`` is the background density at the events per deg^2 with unit
    integral over the box (``None``: uniform), turned into per km^2 as :func:`knotenlinie.etas.model.logL_uzay_zaman`
    does, so ``lambda`` is that function's intensity term by term.  ``rho_ij = K A_i (t_j - t_i + c)^-p
    g(r_ij; D_i) / lambda_j`` for ``t_i < t_j``, kept above ``esik``.  The events are taken in time order
    internally (a stable sort), so the input need not be sorted; indices refer to the input order.
    Returns ``(phi, (i, j, rho), log_lambda)``.
    """
    th = np.asarray(theta, float)
    mu, Kk, c, alpha, p, D, q, gamma = (float(v) for v in th[:8])
    t = np.asarray(t, float); mags = np.asarray(mags, float)
    met = metrik if metrik is not None else M.yerel_metrik(kutu)
    xk, yk = met.km(np.asarray(x, float), np.asarray(y, float))
    N = t.size
    la0, la1, lo0, lo1 = kutu
    u_derece = (np.full(N, 1.0 / ((la1 - la0) * (lo1 - lo0))) if u_olay is None
                else np.asarray(u_olay, float))
    u = u_derece / met.jakobiyen
    A = 10.0 ** (alpha * (mags - m0))
    o = np.argsort(t, kind="stable")
    ts, xs, ys, As, ms, us = t[o], xk[o], yk[o], A[o], mags[o], u[o]
    phi_s = np.empty(N)
    lam_s = np.empty(N)
    ii, jj, rr = [], [], []
    for a0 in range(0, N, chunk):
        b0 = min(a0 + chunk, N)
        dt = ts[a0:b0, None] - ts[None, :b0]
        maske = dt > 0.0
        with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
            P = np.where(maske, (dt + c) ** (-p), 0.0)
        r2 = (xs[a0:b0, None] - xs[None, :b0]) ** 2 + (ys[a0:b0, None] - ys[None, :b0]) ** 2
        tetik = Kk * P * As[None, :b0] * M.mekan_cekirdegi(r2, D, q, gamma, ms[:b0], m0)
        lam = mu * us[a0:b0] + tetik.sum(1)
        lam_s[a0:b0] = lam
        phi_s[a0:b0] = mu * us[a0:b0] / lam
        rho = tetik / lam[:, None]
        hj, hi = np.nonzero(rho > esik)
        ii.append(o[hi]); jj.append(o[a0 + hj]); rr.append(rho[hj, hi])
    phi = np.empty(N); phi[o] = phi_s
    log_lam = np.empty(N); log_lam[o] = np.log(lam_s)
    birles = (lambda v, tip: np.concatenate(v).astype(tip) if v else np.zeros(0, tip))
    return phi, (birles(ii, int), birles(jj, int), birles(rr, float)), log_lam


def ayristir_uzay(theta, t, mags, x, y, m0, beta, t0, T, kutu, u_olay=None, metrik=None,
                  dx: float = 0.1, esik: float = VARSAYILAN_ESIK, durma: float = VARSAYILAN_DURMA,
                  azami: int = VARSAYILAN_AZAMI, chunk: int = 500, histogram: bool = False,
                  n_p: int = NP_VARSAYILAN, eps_km: float = EPS_KM_VARSAYILAN,
                  mu_std: float | None = None) -> dict:
    """The space-time iteration (Zhuang, Ogata & Vere-Jones 2002).

    Each round: ``phi_j`` from :func:`uzay_arka_plan_olasiliklari`, the log-likelihood
    :func:`knotenlinie.etas.model.logL_uzay_zaman` with the fit's exact ``G_i`` (fixed: the triggering
    parameters are the fit's), then ``mu = sum(phi) / (T - t0)`` and ``u`` from the round's ``phi``.
    With an explicit ``n_p`` the ``u`` is Zhuang et al. (2002)'s variable-kernel estimate, each
    kernel normalised by its own box mass and leave-one-out (:func:`arka_plan_yogunlugu`), and the
    **kernel** iteration stops on ``max |d phi| <= PHI_DURMA`` or at ``azami`` rounds (the cap is
    reported).  **No ``n_p`` is adopted**, so ``n_p`` defaults to ``None``.

    The descriptive fallback is fixed: with ``n_p`` None (and
    ``histogram`` False) there is **one** ``phi`` pass at the fit's own unweighted histogram
    ``u`` and its own ``theta[0]``, **no refit**; the reported count is exactly
    ``theta[0] (T - t0)`` with ``sum(phi)`` beside it, and ``mu`` stays the fit's.  ``u_tur`` is
    ``"histogram"``, ``u_guncellendi`` is ``False`` and ``iterasyon`` is 1.
    ``cekirdek = n_p is not None and not histogram``: ``histogram=True`` is the named earlier
    exact-EM variant and wins over an explicit ``n_p`` (so it is never mislabelled ``cekirdek``).
    When the fit's ``mu`` standard error is given as ``mu_std``, the
    count's uncertainty ``std(mu) (T - t0)`` is reported as ``arka_plan_sayisi_sd_mu``, **beside**
    ``arka_plan_sayisi_sd`` (the spread of ``sum phi``, not of the count); they are different
    quantities and FORMATS says which is which.  **The uncertainty is
    reported only on the descriptive path**, where the count is exactly the fit's ``mu (T - t0)``;
    on the histogram/kernel variants ``mu`` is refitted, so the count is not ``mu_fit (T - t0)``
    and ``arka_plan_sayisi_sd_mu`` is ``null``.  The count itself is not changed.
    ``n_p``, ``eps_km`` and the flags are reported; ``u_olay`` is the starting ``u`` per deg^2
    (``None``: the fit's own unweighted histogram, so the first round's log-likelihood is the
    fit's).  The kernel log-likelihood is labelled a leave-one-out pseudo-likelihood and is never
    compared with the fit's ``logL`` in a ratio.  ``mu`` and the triggering
    term stay separate.
    """
    th = np.asarray(theta, float)[:8].copy()
    t = np.asarray(t, float); mags = np.asarray(mags, float)
    x = np.asarray(x, float); y = np.asarray(y, float)
    met = metrik if metrik is not None else M.yerel_metrik(kutu)
    if u_olay is None:
        u_olay = M.arka_plan_degeri(x, y, M.arka_plan_histogram(x, y, kutu, dx=dx))
    u = np.asarray(u_olay, float)
    # ``histogram=True`` is the named exact-EM variant and wins over an
    # explicit ``n_p`` (an ``n_p`` with ``histogram=True`` is not mislabelled ``cekirdek``).
    cekirdek = n_p is not None and not histogram
    # The default (``n_p`` None, ``histogram`` False) is descriptive:
    # one ``phi`` pass at the fit's own unweighted histogram and its own ``theta[0]``, no refit.
    betimsel = (n_p is None) and (not histogram)
    hist = None
    G = M.uzay_normalizasyonu(th, x, y, mags, m0, kutu, metrik=met)
    gecmis_logL = []
    onceki_phi = None
    phi_yakinsama = float("nan")
    phi_durdu = False
    durdu = False
    for it in range(azami):
        phi, _, _ = uzay_arka_plan_olasiliklari(th, t, mags, x, y, m0, kutu, u, met, esik, chunk)
        ell = M.logL_uzay_zaman(th, t, mags, x, y, m0, beta, t0, T, kutu, u, G=G, metrik=met)
        gecmis_logL.append(float(ell))
        if betimsel:
            # exactly one phi pass; the fit's mu and unweighted histogram are not refitted
            durdu = True
            break
        if histogram:
            if it > 0 and abs(gecmis_logL[-1] - gecmis_logL[-2]) < durma:
                durdu = True
                break
        else:
            if onceki_phi is not None:
                phi_yakinsama = float(np.max(np.abs(phi - onceki_phi)))
                if phi_yakinsama <= PHI_DURMA:
                    phi_durdu = True
                    durdu = True
                    break
            onceki_phi = phi
        th = th.copy()
        th[0] = float(phi.sum() / (T - t0))
        if histogram:
            hist = M.arka_plan_histogram(x, y, kutu, dx=dx, agirlik=phi)
            u = M.arka_plan_degeri(x, y, hist)
        else:
            hist = None
            u = arka_plan_yogunlugu(x, y, phi, met, n_p=n_p, eps_km=eps_km, kutu=kutu)
    phi, (ii, jj, rr), log_lam = uzay_arka_plan_olasiliklari(th, t, mags, x, y, m0, kutu, u, met, esik, chunk)
    if betimsel:
        hist = M.arka_plan_histogram(x, y, kutu, dx=dx)
    if cekirdek:
        _, _, h_final, _ = _arka_plan_cekirdekleri(x, y, met, n_p, eps_km, kutu)
        taban = int(np.sum(h_final <= float(eps_km) + 1e-12))
    else:
        taban = None
    # a NaN phi_yakinsama (the descriptive/histogram paths) is written as
    # ``null``, not the invalid bare ``NaN``.
    phi_yakinsama_cikti = float(phi_yakinsama) if np.isfinite(phi_yakinsama) else None
    return {"probs": phi.tolist(), "pmatr": [[int(a), int(b), float(v)] for a, b, v in zip(ii, jj, rr)],
            "rates": uzay_oranlari(th, t, mags, x, y, m0, t0, T, kutu,
                                   phi=None if not cekirdek else phi, histogram=hist, metrik=met, dx=dx,
                                   n_p=n_p, eps_km=eps_km),
            "iterasyon": it + 1, "logL_gecmisi": gecmis_logL, "logL": gecmis_logL[-1],
            "mu": float(th[0]), "parametreler": M._sozluk(th, M.UZAY_ADLARI),
            "arka_plan_sayisi_beklenen": (float(phi.sum()) if cekirdek else float(th[0] * (T - t0))),
            "arka_plan_sum_phi": float(phi.sum()),
            "arka_plan_sayisi_sd": float(np.sqrt(np.sum(phi * (1.0 - phi)))),
            # The count's uncertainty, std(mu) (T - t0), reported beside
            # the spread of sum(phi) (``arka_plan_sayisi_sd``), which is a different quantity.
            # Only on the descriptive path, where the count is exactly
            # the fit's mu (T - t0); the refitting variants report null.
            "arka_plan_sayisi_sd_mu": (float(mu_std) * (float(T) - float(t0))
                                       if (betimsel and mu_std is not None) else None),
            "esik": esik,
            "G_kullanildi": True, "u_guncellendi": bool(cekirdek or histogram), "model": "uzay-zaman",
            "u_tur": "cekirdek" if cekirdek else "histogram", "u_np": None if not cekirdek else int(n_p),
            "eps_km": float(eps_km) if cekirdek else None, "taban_sayisi": taban, "n": int(t.size),
            "phi_durma": (float(PHI_DURMA) if cekirdek else None), "phi_yakinsama": phi_yakinsama_cikti,
            "phi_durdu": phi_durdu, "azami": int(azami), "azami_doldu": (not durdu),
            "np_kabul": bool(NP_KABUL),
            "logL_etiket": ("leave-one-out pseudo-likelihood" if cekirdek
                            else "exact-EM log-likelihood"),
            "metrik": met.kayit(), "normalizasyon": M.NORMALIZASYON}


def uzay_oranlari(theta, t, mags, x, y, m0, t0, T, kutu, phi=None, histogram=None, metrik=None,
                  dx: float = 0.1, n_p: int = NP_CEKIRDEK_VARSAYILAN,
                  eps_km: float = EPS_KM_VARSAYILAN) -> dict:
    """``rates`` of the space-time declustering: per cell of the ``dx`` grid, events per day over
    ``[t0, T]`` — the background ``mu int_cell u`` and the total, background plus
    ``sum_i K A_i I_i(T) int_cell g_i / (T - t0)`` with the exact cell integrals.  ``phi`` are the
    final background weights: the kernel background's cells are :func:`arka_plan_hucreleri` (exact,
    each kernel normalised by its own box mass, so they sum to ``mu`` exactly), and ``u_derece2`` is
    its self-included density at the cell centres.  ``histogram`` is the named earlier variant
    (uniform background when both are ``None``)."""
    th = np.asarray(theta, float)
    mu, Kk, c, alpha, p, D, q, gamma = (float(v) for v in th[:8])
    met = metrik if metrik is not None else M.yerel_metrik(kutu)
    lo_k, la_k = M.hucre_kenarlari(kutu, dx)
    lo_m, la_m = 0.5 * (lo_k[:-1] + lo_k[1:]), 0.5 * (la_k[:-1] + la_k[1:])
    LO, LA = np.meshgrid(lo_m, la_m)
    alan = np.outer(np.diff(la_k), np.diff(lo_k))                    # deg^2, rows latitude
    la0, la1, lo0, lo1 = kutu
    if histogram is not None:
        u = np.asarray(M.arka_plan_degeri(LO.ravel(), LA.ravel(), histogram), float).reshape(LO.shape)
        arka = mu * u * alan
    elif phi is not None:
        u = arka_plan_yogunlugu(x, y, phi, met, hedef=(LO.ravel(), LA.ravel()), n_p=n_p,
                                eps_km=eps_km, kutu=kutu).reshape(LO.shape)
        arka = mu * arka_plan_hucreleri(x, y, phi, kutu, met, dx=dx, n_p=n_p, eps_km=eps_km)
    else:
        u = np.full(LO.shape, 1.0 / ((la1 - la0) * (lo1 - lo0)))
        arka = mu * u * alan
    I, _, _ = M._omori_ilke(float(T) - np.asarray(t, float), c, p)
    agirlik = Kk * 10.0 ** (alpha * (np.asarray(mags, float) - m0)) * I
    H = M.mekan_hucre_integralleri(x, y, M.mekan_olcegi(D, gamma, mags, m0), q, kutu, dx=dx, metrik=met)
    tetik = np.tensordot(agirlik, H, axes=(0, 0)) / (float(T) - float(t0))
    return {"lon": lo_m.tolist(), "lat": la_m.tolist(), "arka_plan": arka.tolist(),
            "toplam": (arka + tetik).tolist(), "u_derece2": u.tolist(), "birim": "olay/gun/hucre",
            "dx": dx}

