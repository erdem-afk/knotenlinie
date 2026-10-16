"""ETAS intensity, likelihood, MLE and space-time kernel.

Clean-room implementation from the equations published in Ogata 1988 (temporal
ETAS and transformed-time residuals; 10.1080/01621459.1988.10478560) and Ogata
1998 (space-time ETAS; 10.1023/A:1003403601725).  No code copied from the pyetas package
(AGPL), the CRAN ETAS package (GPL) or Zhuang's Fortran sd package.

Temporal intensity, printed so the normalisation cannot drift::

    lambda(t) = mu + sum_{t_i < t} K * 10^{alpha*(M_i - M0)} / (t - t_i + c)^p

with M0 = Mc fixed and recorded; that is what makes K and alpha well defined.
Domain: mu > 0, K > 0, c > 0, 0 <= alpha < beta, p > 1.

Space-time intensity (Ogata 1998)::

    lambda(t,x,y) = mu*u(x,y) + sum_i K*10^{alpha*(M_i-M0)}/(t-t_i+c)^p * g(x-x_i,y-y_i;M_i)
    g(r;D_i) = (q-1)/(pi*D_i^2) * (1 + r^2/D_i^2)^{-q}
             = (q-1)*D_i^{2(q-1)} / (pi*(r^2 + D_i^2)^q),   D_i = D*10^{gamma*(M_i-M0)}

The 2-D plane normalisation is ``int g dA = 1`` and the ``pi`` is explicit: this is
the classic silent ``2*pi`` / ``2(q-1)`` error.  ``u(x,y)`` is a coarse 0.1
degree histogram (updated by the stochastic declustering probabilities), normalised to
one over the box, never a free non-parametric surface.

One metric, in km.  Distances are taken in the declared
local equirectangular projection of the region box, :func:`yerel_metrik`:
``x = R cos(phi0) (lon - lam0)``, ``y = R (lat - phi0)`` with ``phi0, lam0`` the box
centre and ``R = R_DUNYA_KM``.  ``r`` and ``D`` are in km (``D^2`` in km^2), ``g`` and
``lambda`` are per km^2 per day.  An earlier version took ``r^2`` in degrees with no
``cos(lat)``, so the kernel was elliptical in km (E-W about 0.73 of N-S).  The
projection's own E-W scale error across the box is ``cos(lat)/cos(phi0) - 1``: about
+/-2.0 % over the Apennine box's 41.5-44.0 N (``YerelMetrik.anizotropi``); it is declared,
not corrected.  Every consumer (likelihood, normalisation, simulator, residuals,
declustering) reads the metric from :func:`yerel_metrik`.

Log-likelihood::

    ell = sum_i log lambda(t_i,x_i,y_i | H_{t_i}) - int_0^T int_A lambda dA dt

The temporal integral is analytic (closed form in ``_omori_ilke``).  The spatial
integral of each parent's kernel over the box, ``G_i = int_A g_i dA``, is exact
(:func:`mekan_kutu_integrali`): the radial CDF
``F(R) = 1 - (1 + R^2/D_i^2)^(1-q)`` over the four signed triangles the event forms
with the box edges.  The log-intensity keeps ``g`` at the event's exact location.
The earlier midpoint sum (:func:`mekan_izgara_integrali`) put ``G`` between 0.16 and
35 at an earlier fit's ``D`` and is kept only as a named reference.

MLE: the transformed parameters are ``(log mu, log K, log c, logit(alpha/beta),
log(p-1), log D, log(q-1), gamma)``; L-BFGS-B from a declared deterministic start
list; the gradient norm, the condition number of the numerically differentiated
Hessian, sigma_theta = sqrt(diag(H^-1)) and the correlation matrix are reported.
A parameter whose standard error exceeds its value is a finding, written
into the parameter file, never fixed to make a test pass.

Compute budget: parents are chained in chunks (default 1,000); only pairs inside a
declared temporal window and a declared spatial cutoff are kept; a run whose pair
count would exceed ``--maks-cift`` (default 5e7) refuses, and instead Mc is raised
in 0.5 steps until it fits, reported as *the fit's Mc*, never as a tuned choice.

The ETAS baseline parameters here are not the parameter budget of the physical
response terms: that budget limits the physical response terms (Asigma and s_r)
to at most two free parameters; the baseline has its own and nobody should read
them as part of that budget.
"""
from __future__ import annotations

from typing import NamedTuple

import numpy as np
from scipy import optimize

from . import katalog as K

LN10 = float(np.log(10.0))

#: Declared Earth radius of the local projection (km): the mean radius, rounded.
R_DUNYA_KM = 6371.0
#: km per degree of latitude on that sphere (111.19 km).
KM_DERECE = R_DUNYA_KM * np.pi / 180.0

#: Declared deterministic start list (Zhuang's example values and perturbations).
BASLANGICLAR = (
    {"mu": 0.05, "K": 0.02, "c": 0.010, "alpha": 1.0, "p": 1.10},
    {"mu": 0.10, "K": 0.05, "c": 0.020, "alpha": 0.8, "p": 1.20},
    {"mu": 0.02, "K": 0.01, "c": 0.005, "alpha": 1.2, "p": 1.05},
)
#: Declared space-time starts (Zhuang's etas8p names: mu, K, c, alpha, p, D, q, gamma).  ``D`` is
#: in km: the earlier degree starts 0.02 and 0.05 converted with ``KM_DERECE``.
BASLANGICLAR_UZAY = (
    {"mu": 0.05, "K": 0.02, "c": 0.010, "alpha": 1.0, "p": 1.10, "D": 0.02 * KM_DERECE, "q": 1.5,
     "gamma": 1.0},
    {"mu": 0.10, "K": 0.05, "c": 0.020, "alpha": 0.8, "p": 1.20, "D": 0.05 * KM_DERECE, "q": 1.8,
     "gamma": 1.2},
)
ZAMAN_ADLARI = ("mu", "K", "c", "alpha", "p")
UZAY_ADLARI = ("mu", "K", "c", "alpha", "p", "D", "q", "gamma")
ALFA_ARA = 1e-3  # alpha < beta - 1e-3 (finite branching)
#: Parameter bounds in transformed space: mu in [1e-5,1e3], K in [1e-8,10], c in [1e-3,30] d,
#: alpha/beta inside (0,1), p in [1.001, 5].  Declared, not tuned.
ZAMAN_SINIRLAR = (np.array([-11.5, -18.4, -6.9, -14.0, -6.9]),
                  np.array([6.9, 2.3, 3.4, 14.0, 1.386]))
#: Space-time bounds: log D in km is the earlier degree range [1e-5, 10] deg converted with KM_DERECE
#: (a change of unit, not of range); log(q-1) in [-6.9, 2.3]; gamma in [-10, 10].
UZAY_SINIRLAR = (np.concatenate([ZAMAN_SINIRLAR[0], [np.log(1e-5 * KM_DERECE), -6.9, -10.0]]),
                 np.concatenate([ZAMAN_SINIRLAR[1], [np.log(10.0 * KM_DERECE), 2.3, 10.0]]))
VARSAYILAN_MAKS_CIFT = 5.0e7
VARSAYILAN_PENCERE_GUN = 3650.0  # declared temporal pair window (10 years)


def _dizi(d: dict, adlar) -> np.ndarray:
    return np.array([float(d[a]) for a in adlar], dtype=float)


def _sozluk(x: np.ndarray, adlar) -> dict:
    return {a: float(v) for a, v in zip(adlar, x)}


# --- transforms (p->1, alpha->beta, mu->0 closed by construction) -----------

def _x_den_theta(x: np.ndarray, beta: float, adlar=ZAMAN_ADLARI) -> np.ndarray:
    th = np.empty_like(x)
    th[0] = np.exp(x[0])
    th[1] = np.exp(x[1])
    th[2] = np.exp(x[2])
    s = 1.0 / (1.0 + np.exp(-x[3]))
    th[3] = (beta - ALFA_ARA) * s
    th[4] = 1.0 + np.exp(x[4])
    if len(x) > 5:
        th[5] = np.exp(x[5])
        th[6] = 1.0 + np.exp(x[6])
        th[7] = x[7]
    return th


def _theta_dan_x(theta: np.ndarray, beta: float) -> np.ndarray:
    x = np.empty_like(theta)
    x[0] = np.log(theta[0])
    x[1] = np.log(theta[1])
    x[2] = np.log(theta[2])
    r = min(max(theta[3] / (beta - ALFA_ARA), 1e-12), 1 - 1e-12)
    x[3] = np.log(r / (1 - r))
    x[4] = np.log(theta[4] - 1.0)
    if len(theta) > 5:
        x[5] = np.log(theta[5])
        x[6] = np.log(theta[6] - 1.0)
        x[7] = theta[7]
    return x


def _zincir_carpani(x: np.ndarray, beta: float) -> np.ndarray:
    """d theta / d x, so a natural-parameter gradient maps to the transformed one."""
    th = _x_den_theta(x, beta)
    c = np.empty_like(x)
    c[0], c[1], c[2] = th[0], th[1], th[2]
    s = 1.0 / (1.0 + np.exp(-x[3]))
    c[3] = (beta - ALFA_ARA) * s * (1 - s)
    c[4] = th[4] - 1.0
    if len(x) > 5:
        c[5] = th[5]
        c[6] = th[6] - 1.0
        c[7] = 1.0
    return c


# --- temporal likelihood -----------------------------------------------------

def _omori_ilke(tau: np.ndarray, c: float, p: float):
    """I = int_0^tau (u+c)^-p du and its c and p derivatives (closed form)."""
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        I = ((tau + c) ** (1.0 - p) - c ** (1.0 - p)) / (1.0 - p)
        dIdc = (tau + c) ** (-p) - c ** (-p)
        a = tau + c
        dIdp = (((-np.log(a) * a ** (1.0 - p) + np.log(c) * c ** (1.0 - p)) * (1.0 - p)
                 + (a ** (1.0 - p) - c ** (1.0 - p))) / (1.0 - p) ** 2)
    return I, dIdc, dIdp


def _zaman_cekirdek(theta: np.ndarray, t: np.ndarray, mags: np.ndarray, m0: float,
                    chunk: int = 1000, G=None):
    """Chunked triggering sums and their natural-parameter derivatives.

    ``G`` (default 1) multiplies each parent's productivity: with the space-time fit's
    exact ``G_i`` the sums are those of the fit's temporal marginal
    ``lambda(t) = mu + K sum_i A_i G_i (t - t_i + c)^-p``.
    """
    mu, Kk, c, alpha, p = (float(v) for v in theta[:5])
    A = 10.0 ** (alpha * (mags - m0))
    if G is not None:
        A = A * np.asarray(G, float)
    N = t.size
    S = np.empty(N)
    dS = np.empty((N, 3))  # d/dc, d/dalpha, d/dp
    for a in range(0, N, chunk):
        b = min(a + chunk, N)
        dt = t[a:b, None] - t[None, :]
        maske = dt > 0.0
        dc = dt + c
        with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
            P = np.where(maske, dc ** (-p), 0.0)
            M = P * A[None, :]
            gec = np.where(maske, 1.0 / dc, 0.0)
            logdc = np.where(maske, np.log(dc), 0.0)
        S[a:b] = M.sum(1)
        dS[a:b, 0] = -p * np.sum(M * gec, axis=1)
        dS[a:b, 1] = LN10 * np.sum(M * (mags[None, :] - m0), axis=1)
        dS[a:b, 2] = -np.sum(M * logdc, axis=1)
    return A, S, dS


def logL_temporal(theta: np.ndarray, t: np.ndarray, mags: np.ndarray, m0: float,
                  beta: float, t0: float, T: float, chunk: int = 1000,
                  gradyan: bool = False, G=None):
    """Temporal ETAS log-likelihood (optionally with its natural-parameter gradient).

    ``G`` (default 1) is a per-parent factor on the productivity; with the space-time
    fit's exact ``G_i`` this is the log-likelihood of that fit's temporal marginal,
    which the declustering of a space-time parameter file uses.
    """
    mu, Kk, c, alpha, p = (float(v) for v in theta[:5])
    A, S, dS = _zaman_cekirdek(theta, t, mags, m0, chunk, G=G)
    lam = mu + Kk * S
    with np.errstate(divide="ignore", invalid="ignore"):
        if np.any(lam <= 0) or not np.all(np.isfinite(lam)):
            return (-np.inf, np.zeros(5)) if gradyan else -np.inf
        ell = float(np.log(lam).sum())
    if not gradyan:
        tau = T - t
        I, _, _ = _omori_ilke(tau, c, p)
        sonuc = ell - mu * (T - t0) - Kk * float(np.sum(A * I))
        return sonuc if np.isfinite(sonuc) else -np.inf
    g = np.zeros(5)
    g[0] = float(np.sum(1.0 / lam))
    g[1] = float(np.sum(S / lam))
    g[2] = Kk * float(np.sum(dS[:, 0] / lam))
    g[3] = Kk * float(np.sum(dS[:, 1] / lam))
    g[4] = Kk * float(np.sum(dS[:, 2] / lam))
    tau = T - t
    I, dIdc, dIdp = _omori_ilke(tau, c, p)
    g[0] -= (T - t0)
    g[1] -= float(np.sum(A * I))
    g[2] -= Kk * float(np.sum(A * dIdc))
    g[3] -= Kk * LN10 * float(np.sum((mags - m0) * A * I))
    g[4] -= Kk * float(np.sum(A * dIdp))
    sonuc = ell - mu * (T - t0) - Kk * float(np.sum(A * I))
    if not (np.isfinite(sonuc) and np.all(np.isfinite(g))):
        return -np.inf, np.zeros(5)
    return sonuc, g


def _nll_temporal_x(x, t, mags, m0, beta, t0, T, chunk):
    try:
        th = _x_den_theta(x, beta)
        ell, g = logL_temporal(th, t, mags, m0, beta, t0, T, chunk, gradyan=True)
        gx = -g * _zincir_carpani(x, beta)
        if not (np.isfinite(ell) and np.all(np.isfinite(gx))):
            return 1e12, np.zeros_like(x)
        return -ell, gx
    except (OverflowError, FloatingPointError):
        return 1e12, np.zeros_like(x)


def hessian_nll(theta: np.ndarray, t, mags, m0, beta, t0, T, adim: float = 1e-5) -> np.ndarray:
    """Numerically differentiated Hessian of the negative log-likelihood, natural theta.

    Uses central differences of the *analytic* gradient, not of the likelihood
    itself: with a log-likelihood of order 1e4 the second difference of ell loses
    its significant digits, the first difference of its gradient does not.
    """
    n = len(theta)
    h = adim * np.maximum(np.abs(theta), 1e-2)
    H = np.zeros((n, n))
    for j in range(n):
        a = theta.copy(); a[j] += h[j]
        b = theta.copy(); b[j] -= h[j]
        _, ga = logL_temporal(a, t, mags, m0, beta, t0, T, gradyan=True)
        _, gb = logL_temporal(b, t, mags, m0, beta, t0, T, gradyan=True)
        if not (np.all(np.isfinite(ga)) and np.all(np.isfinite(gb))):
            return np.full((n, n), np.nan)
        H[:, j] = -(ga - gb) / (2.0 * h[j])
    return 0.5 * (H + H.T)


def _std_korelasyon(H: np.ndarray):
    try:
        C = np.linalg.inv(H)
    except np.linalg.LinAlgError:
        C = np.linalg.pinv(H)
    d = np.sqrt(np.clip(np.diag(C), 0.0, None))
    with np.errstate(divide="ignore", invalid="ignore"):
        R = C / np.outer(d, d)
    R = np.nan_to_num(R)
    return d, R, float(np.linalg.cond(H)), C


def mle_temporal(t, mags, m0: float, beta: float, t0: float, T: float,
                 baslangiclar=None, chunk: int = 1000, maksiter: int = 500,
                 gtol: float = 1e-8, ftol: float = 1e-12) -> dict:
    """Temporal ETAS MLE over the transformed parameters.  Deterministic."""
    t = np.asarray(t, float)
    mags = np.asarray(mags, float)
    bas = baslangiclar or BASLANGICLAR
    en_iyi = None
    for b0 in bas:
        th0 = _dizi(b0, ZAMAN_ADLARI)
        x0 = _theta_dan_x(th0, beta)
        res = optimize.minimize(
            _nll_temporal_x, x0, args=(t, mags, m0, beta, t0, T, chunk),
            jac=True, method="L-BFGS-B", bounds=optimize.Bounds(*ZAMAN_SINIRLAR),
            options={"maxiter": maksiter, "ftol": ftol, "gtol": gtol})
        if en_iyi is None or res.fun < en_iyi.fun:
            en_iyi = res
    th = _x_den_theta(en_iyi.x, beta)
    ell = float(-en_iyi.fun)
    H = hessian_nll(th, t, mags, m0, beta, t0, T)
    std, R, kosul, _ = _std_korelasyon(H)
    _, g = logL_temporal(th, t, mags, m0, beta, t0, T, gradyan=True)
    return {"parametreler": _sozluk(th, ZAMAN_ADLARI), "std": _sozluk(std, ZAMAN_ADLARI),
            "korelasyon": R.tolist(), "korelasyon_adlari": list(ZAMAN_ADLARI),
            "gradyan_normu": float(np.linalg.norm(g)), "hessian_kosul": kosul,
            "logL": ell, "nit": int(en_iyi.nit), "basari": bool(en_iyi.success),
            "m0": float(m0), "beta": float(beta), "t0": float(t0), "T": float(T),
            "n": int(t.size), "model": "zaman"}


# --- the km metric ---------------------------------

class YerelMetrik(NamedTuple):
    """The declared local equirectangular projection of one region box, in km.

    ``x = kx (lon - lam0)``, ``y = ky (lat - phi0)`` with ``kx = R cos(phi0) pi/180``,
    ``ky = R pi/180`` and ``(phi0, lam0)`` the box centre.  The map is linear, so a
    latitude-longitude rectangle (the box, a 0.1 degree cell) is a rectangle in km and a
    density per deg^2 becomes one per km^2 by dividing by :attr:`jakobiyen`.  Build it
    only with :func:`yerel_metrik`.
    """

    phi0: float
    lam0: float
    kx: float
    ky: float
    kutu: tuple

    def km(self, lon, lat):
        """(x, y) in km of longitudes and latitudes in degrees."""
        return (self.kx * (np.asarray(lon, float) - self.lam0),
                self.ky * (np.asarray(lat, float) - self.phi0))

    def derece(self, x, y):
        """(lon, lat) in degrees of km coordinates (the inverse of :meth:`km`)."""
        return (self.lam0 + np.asarray(x, float) / self.kx,
                self.phi0 + np.asarray(y, float) / self.ky)

    def kutu_km(self, kutu=None):
        """A ``(lat_min, lat_max, lon_min, lon_max)`` rectangle as ``(x0, x1, y0, y1)`` in km."""
        la0, la1, lo0, lo1 = (float(v) for v in (self.kutu if kutu is None else kutu))
        x0, y0 = self.km(lo0, la0)
        x1, y1 = self.km(lo1, la1)
        return float(x0), float(x1), float(y0), float(y1)

    @property
    def jakobiyen(self) -> float:
        """km^2 per deg^2 of the projection."""
        return float(self.kx * self.ky)

    @property
    def anizotropi(self) -> float:
        """The declared E-W scale error at the box's latitude edges: max |cos(lat)/cos(phi0) - 1|."""
        c0 = np.cos(np.radians(self.phi0))
        return float(max(abs(np.cos(np.radians(v)) / c0 - 1.0) for v in self.kutu[:2]))

    def kayit(self) -> dict:
        """The metric as the parameter file records it."""
        return {"tur": "yerel-esdikdortgen", "R_km": R_DUNYA_KM, "phi0": float(self.phi0),
                "lam0": float(self.lam0), "kx_km_derece": float(self.kx),
                "ky_km_derece": float(self.ky), "kutu": [float(v) for v in self.kutu],
                "anizotropi": self.anizotropi, "D_birim": "km"}


def yerel_metrik(kutu) -> YerelMetrik:
    """The one metric every space-time consumer reads.

    ``kutu`` is the region box ``(lat_min, lat_max, lon_min, lon_max)``; the projection's
    ``phi0, lam0`` are its centre.  Cells and sub-boxes of the region use the region's
    metric (pass it on as ``metrik=``), never one of their own.
    """
    la0, la1, lo0, lo1 = (float(v) for v in kutu)
    if not (la1 > la0 and lo1 > lo0):
        raise ValueError(f"the box {tuple(kutu)} is not (lat_min, lat_max, lon_min, lon_max)")
    phi0 = 0.5 * (la0 + la1)
    return YerelMetrik(phi0=phi0, lam0=0.5 * (lo0 + lo1), kx=float(KM_DERECE * np.cos(np.radians(phi0))),
                       ky=float(KM_DERECE), kutu=(la0, la1, lo0, lo1))


# --- space-time --------------------------------------------------------------

def mekan_olcegi(D: float, gamma: float, mags, m0: float) -> np.ndarray:
    """``D_i = D * 10^(gamma (M_i - M0))``, in the unit of ``D`` (km in the fit)."""
    return float(D) * 10.0 ** (float(gamma) * (np.asarray(mags, float) - float(m0)))


def mekan_cekirdegi(r2: np.ndarray, D: float, q: float, gamma: float, mags: np.ndarray, m0: float):
    """Ogata 1998 power-law kernel on the plane; ``int g dA = 1`` exactly.

    Unit-agnostic: ``r2`` and ``D`` in one length unit (km^2 and km for the fit),
    ``g`` per that unit squared.
    """
    Di = D * 10.0 ** (gamma * (mags - m0))
    return (q - 1.0) * Di ** (2.0 * (q - 1.0)) / (np.pi * (r2 + Di ** 2) ** q)


def radyal_cdf(R2, D_i, q) -> np.ndarray:
    """``F(R) = int_{|r|<R} g dA = 1 - (1 + R^2/D_i^2)^(1-q)`` in a form exact for small ``R``."""
    return -np.expm1((1.0 - float(q)) * np.log1p(np.asarray(R2, float) / np.asarray(D_i, float) ** 2))


#: Gauss-Legendre nodes per panel of the exact normalisation, declared.
GL_DUGUM = 16
#: Longest panel in ``v = asinh(s/|d|)``, declared; panels are set by geometry only.
PANEL_V = 1.0
_GL_X, _GL_W = np.polynomial.legendre.leggauss(GL_DUGUM)


def _ucgen_dugumleri(px, py, ax, ay, bx, by):
    """Quadrature nodes of the signed triangle integrals ``int_{(P,A,B)} g dA``, flattened.

    For the segment ``A -> B``, ``d`` is the signed distance of ``P`` from its line
    (positive when ``P`` lies to the left, i.e. inside a counter-clockwise polygon) and
    ``s`` the position along the line from ``P``'s foot.  In polar coordinates about ``P``
    the triangle is ``int dphi int_0^{|d| sec phi} g r dr = int F(|d| sec phi) dphi / (2 pi)``.
    With ``s = |d| tan phi = |d| sinh v``, ``dphi = dv / cosh v`` and ``|d| sec phi = |d| cosh v``:

        int_{(P,A,B)} g dA = sign(d)/(2 pi) * int_{v_a}^{v_b} F(|d| cosh v) / cosh v dv,
        v_a = asinh(s_a/|d|), v_b = asinh(s_b/|d|).

    The integrand's complex singularities lie on ``Im v = +/- pi/2`` for every ``D_i``,
    ``q`` and ``d`` (``cosh v = 0`` and ``1 + (d/D_i)^2 cosh^2 v = 0``), so fixed
    Gauss-Legendre on panels no longer than ``PANEL_V`` converges geometrically at a rate
    that does not depend on ``D``.  The panel count comes from ``v_a, v_b`` only — the
    event-edge geometry — never from ``D`` or ``q``: at fixed events the result is an
    analytic function of ``(D_i, q)``, so finite-difference gradients and the second
    differences of :func:`hessian_nll_uzay` see no switching.  A segment on ``P``'s line
    (``d = 0``) spans no area and has no node.

    Returns ``(R2, agirlik, cift, n_cift)``: ``R^2`` at each node, the node weight
    (Gauss weight, panel half-length, ``1/cosh v``, ``sign(d)/(2 pi)``), the flat index of
    its ``(P, segment)`` pair in the broadcast shape, and the pair count.
    """
    arr = np.broadcast_arrays(*(np.asarray(v, float) for v in (px, py, ax, ay, bx, by)))
    px, py, ax, ay, bx, by = (a.ravel() for a in arr)
    L = np.hypot(bx - ax, by - ay)
    if np.any(L <= 0.0):
        raise ValueError("a polygon edge has zero length")
    ux, uy = (bx - ax) / L, (by - ay) / L
    d = (py - ay) * ux - (px - ax) * uy
    sa = (ax - px) * ux + (ay - py) * uy
    sb = (bx - px) * ux + (by - py) * uy
    idx = np.flatnonzero(d != 0.0)
    ad = np.abs(d[idx])
    va = np.arcsinh(sa[idx] / ad)
    vb = np.arcsinh(sb[idx] / ad)
    m = np.maximum(1, np.ceil((vb - va) / PANEL_V).astype(np.int64))
    rep = np.repeat(np.arange(idx.size), m)
    k = np.arange(rep.size) - np.repeat(np.cumsum(m) - m, m)
    h = (vb - va)[rep] / m[rep]
    v = (va[rep] + k * h)[:, None] + 0.5 * h[:, None] * (_GL_X[None, :] + 1.0)
    R2 = (ad[rep] ** 2)[:, None] * (1.0 + np.sinh(v) ** 2)
    w = (0.5 * h)[:, None] * _GL_W[None, :] / np.cosh(v) * (np.sign(d[idx])[rep] / (2.0 * np.pi))[:, None]
    return R2.ravel(), w.ravel(), np.repeat(idx[rep], GL_DUGUM), int(px.size)


def _dikdortgen_km(xk, yk, Di, q, x0, x1, y0, y1) -> np.ndarray:
    """``int_rect g_i dA`` for events at ``(xk, yk)`` km and one km rectangle (four CCW edges)."""
    xk = np.atleast_1d(np.asarray(xk, float))
    yk = np.atleast_1d(np.asarray(yk, float))
    n = xk.size
    Di = np.broadcast_to(np.asarray(Di, float), (n,)) if np.ndim(Di) else np.full(n, float(Di))
    ax = np.array([x0, x1, x1, x0]); ay = np.array([y0, y0, y1, y1])
    bx = np.array([x1, x1, x0, x0]); by = np.array([y0, y1, y1, y0])
    R2, w, cift, n_cift = _ucgen_dugumleri(xk[:, None], yk[:, None], ax[None, :], ay[None, :],
                                           bx[None, :], by[None, :])
    olay = cift // 4
    deger = np.bincount(cift, w * radyal_cdf(R2, Di[olay], q), minlength=n_cift)
    return deger.reshape(n, 4).sum(1)


def mekan_kutu_integrali(x_i, y_i, D_i, q, kutu, metrik=None) -> np.ndarray:
    """``G_i = int_box g_i dA``, exact.

    ``x_i, y_i`` are the events' longitudes and latitudes in degrees, ``D_i`` their kernel
    scales in km (a scalar or one per event, :func:`mekan_olcegi`), ``kutu`` the rectangle
    ``(lat_min, lat_max, lon_min, lon_max)`` integrated over and ``metrik`` the region's
    :func:`yerel_metrik` (default: the metric of ``kutu`` itself, right when ``kutu`` is the
    region).  The radial CDF over the four signed triangles the event forms with the edges
    (:func:`_ucgen_dugumleri`); an event inside gives the full angle, one outside
    cancels, one on an edge or a corner gets its half or quarter.
    """
    met = metrik if metrik is not None else yerel_metrik(kutu)
    xk, yk = met.km(x_i, y_i)
    x0, x1, y0, y1 = met.kutu_km(kutu)
    return _dikdortgen_km(xk, yk, D_i, q, x0, x1, y0, y1)


def hucre_kenarlari(kutu, dx: float = 0.1):
    """Cell edges ``(lon_edges, lat_edges)`` in degrees of the :func:`_izgara_merkezleri` grid.

    Edge ``k`` is ``min + k dx``; the last edge of each axis is the box edge itself, so the
    cells tile the box exactly (for the Apennine box at 0.1 degree every cell is whole).
    """
    la0, la1, lo0, lo1 = (float(v) for v in kutu)
    n_la = np.arange(la0 + dx / 2, la1, dx).size
    n_lo = np.arange(lo0 + dx / 2, lo1, dx).size
    la = la0 + dx * np.arange(n_la + 1)
    lo = lo0 + dx * np.arange(n_lo + 1)
    la[-1] = la1
    lo[-1] = lo1
    return lo, la


def mekan_hucre_integralleri(x_i, y_i, D_i, q, kutu, dx: float = 0.1, metrik=None,
                             blok: int = 64) -> np.ndarray:
    """``int_cell g_i dA`` for every cell of the ``dx`` grid of ``kutu``, exact.

    Returns an array ``(N, n_lat, n_lon)`` in the layout of :func:`_izgara_merkezleri`
    (rows latitude, columns longitude), with the cells of :func:`hucre_kenarlari`.  Each
    grid segment's signed triangle integral is computed once (horizontal segments
    oriented +x, vertical +y) and each cell is its four segments counter-clockwise,
    ``H[k, j] + V[k, j+1] - H[k+1, j] - V[k, j]``, the same decomposition as
    :func:`mekan_kutu_integrali`; the cells of an event sum to its ``G_i`` to rounding.
    ``metrik`` defaults to the metric of ``kutu`` (the region); ``blok`` events are done
    at a time.

    Each cell is clipped at 0 after the signed-triangle sum: far from the event
    the four signed terms cancel to rounding and can land at about -7e-17 (a steep tail, ``q = 5``),
    a negative share no cell can hold.  The clipped amount is below 1e-16 per cell, so the cells
    still sum to ``G_i`` to 1e-12.
    """
    met = metrik if metrik is not None else yerel_metrik(kutu)
    lo_k, la_k = hucre_kenarlari(kutu, dx)
    X = met.kx * (lo_k - met.lam0)
    Y = met.ky * (la_k - met.phi0)
    xk, yk = met.km(x_i, y_i)
    xk = np.atleast_1d(xk); yk = np.atleast_1d(yk)
    n = xk.size
    Di = np.broadcast_to(np.asarray(D_i, float), (n,)) if np.ndim(D_i) else np.full(n, float(D_i))
    nla, nlo = Y.size - 1, X.size - 1
    # horizontal segments (k over lat edges, j over lon cells), then vertical ones
    hax, hay = np.meshgrid(X[:-1], Y, indexing="xy")
    hbx, hby = np.meshgrid(X[1:], Y, indexing="xy")
    vax, vay = np.meshgrid(X, Y[:-1], indexing="xy")
    vbx, vby = np.meshgrid(X, Y[1:], indexing="xy")
    ax = np.concatenate([hax.ravel(), vax.ravel()]); ay = np.concatenate([hay.ravel(), vay.ravel()])
    bx = np.concatenate([hbx.ravel(), vbx.ravel()]); by = np.concatenate([hby.ravel(), vby.ravel()])
    ns = ax.size
    nh = (nla + 1) * nlo
    cikti = np.empty((n, nla, nlo))
    for a in range(0, n, blok):
        b = min(a + blok, n)
        R2, w, cift, n_cift = _ucgen_dugumleri(xk[a:b, None], yk[a:b, None], ax[None, :], ay[None, :],
                                               bx[None, :], by[None, :])
        olay = cift // ns
        S = np.bincount(cift, w * radyal_cdf(R2, Di[a:b][olay], q), minlength=n_cift).reshape(b - a, ns)
        H = S[:, :nh].reshape(b - a, nla + 1, nlo)
        V = S[:, nh:].reshape(b - a, nla, nlo + 1)
        cikti[a:b] = np.maximum(H[:, :-1, :] + V[:, :, 1:] - H[:, 1:, :] - V[:, :, :-1], 0.0)
    return cikti


def _izgara_merkezleri(kutu, dx):
    la0, la1, lo0, lo1 = kutu
    la = np.arange(la0 + dx / 2, la1, dx)
    lo = np.arange(lo0 + dx / 2, lo1, dx)
    return np.meshgrid(lo, la)  # (lon, lat) grids


def mekan_izgara_integrali(kutu, x_i, y_i, mags, m0, D, q, gamma, dx: float = 0.1) -> np.ndarray:
    """Named reference only: the earlier midpoint ``G_i`` on the 0.1 degree grid, degree metric.

    ``r^2`` in degrees with no ``cos(lat)`` and ``D`` in degrees, the kernel at each cell
    centre times the cell's deg^2 area.  At an earlier full fit's ``D = 0.00694`` degree the kernel is far
    narrower than a cell and this sum lies between 0.16 and 35 depending on where the event
    sits in its cell.  The fit, the residuals and the declustering use the exact
    :func:`mekan_kutu_integrali`; this stays for the tests' negative controls and for the
    compatibility shim until its last caller moves to :func:`mekan_hucre_integralleri`.
    """
    la0, la1, lo0, lo1 = kutu
    lo_g, la_g = _izgara_merkezleri(kutu, dx)
    alan = dx ** 2
    G = np.empty(mags.size)
    for i in range(mags.size):
        r2 = (lo_g - x_i[i]) ** 2 + (la_g - y_i[i]) ** 2
        G[i] = float(np.sum(mekan_cekirdegi(r2, D, q, gamma, np.array([mags[i]]), m0)) * alan)
    return G


def arka_plan_histogram(x: np.ndarray, y: np.ndarray, kutu, dx: float = 0.1,
                        agirlik: np.ndarray = None):
    """Coarse background density u(x,y) per deg^2 from declustering weights, sums to 1.

    The density is per deg^2 of the 0.1 degree cells; :func:`logL_uzay_zaman` turns it into
    one per km^2 with the metric's Jacobian.
    """
    la0, la1, lo0, lo1 = kutu
    xe = np.arange(lo0, lo1 + dx, dx)
    ye = np.arange(la0, la1 + dx, dx)
    w = np.ones(x.size) if agirlik is None else np.asarray(agirlik, float)
    H, _, _ = np.histogram2d(x, y, bins=[xe, ye], weights=w)
    toplam = H.sum()
    yog = H / (toplam * dx * dx) if toplam > 0 else H
    return {"x_kenar": xe, "y_kenar": ye, "yogunluk": yog, "dx": dx, "kutu": tuple(kutu)}


def arka_plan_degeri(x, y, hist) -> np.ndarray:
    ix = np.clip(np.searchsorted(hist["x_kenar"], x, side="right") - 1, 0, hist["yogunluk"].shape[0] - 1)
    iy = np.clip(np.searchsorted(hist["y_kenar"], y, side="right") - 1, 0, hist["yogunluk"].shape[1] - 1)
    return hist["yogunluk"][ix, iy]


def uzay_normalizasyonu(theta, x, y, mags, m0, kutu, metrik=None) -> np.ndarray:
    """The fit's own ``G_i`` for a space-time parameter vector: :func:`mekan_kutu_integrali`
    with ``D_i = D 10^(gamma (M_i - M0))`` (the residuals and the declustering use it)."""
    D, q, gamma = (float(v) for v in np.asarray(theta, float)[5:8])
    return mekan_kutu_integrali(x, y, mekan_olcegi(D, gamma, mags, m0), q, kutu, metrik=metrik)


def logL_uzay_zaman(theta: np.ndarray, t, mags, x, y, m0, beta, t0, T, kutu,
                    u_olay=None, dx: float = 0.1, chunk: int = 500, *, G=None, metrik=None) -> float:
    """Space-time ETAS log-likelihood in the km metric with the exact ``G_i``.

    ``x, y`` are longitudes and latitudes in degrees; distances are taken in
    ``metrik`` (default :func:`yerel_metrik` of ``kutu``).  ``u_olay`` is the background
    density at the events **per deg^2** (as :func:`arka_plan_degeri` gives it, unit
    integral over the box), turned into per km^2 here; ``None`` is the uniform density.
    ``lambda`` is then per km^2 per day.  The compensator is
    ``mu (T - t0) + K sum_i A_i I_i G_i`` with ``G_i`` from :func:`mekan_kutu_integrali`,
    or the given ``G`` (the tests assemble it from cell integrals on shifted grids).
    ``dx`` is unused (``G`` has no grid) and kept for the callers' signature.
    """
    mu, Kk, c, alpha, p, D, q, gamma = (float(v) for v in theta[:8])
    t = np.asarray(t, float); mags = np.asarray(mags, float)
    x = np.asarray(x, float); y = np.asarray(y, float)
    met = metrik if metrik is not None else yerel_metrik(kutu)
    xk, yk = met.km(x, y)
    A = 10.0 ** (alpha * (mags - m0))
    N = t.size
    la0, la1, lo0, lo1 = kutu
    u_derece = (np.full(N, 1.0 / ((la1 - la0) * (lo1 - lo0))) if u_olay is None
                else np.asarray(u_olay, float))
    u = u_derece / met.jakobiyen
    # pairs in time order: a target's parents all sit before it, so each chunk of targets needs
    # only the columns up to its own end (equal times are excluded by dt > 0)
    o = np.argsort(t, kind="stable")
    ts, xs, ys, As, ms = t[o], xk[o], yk[o], A[o], mags[o]
    Ss = np.zeros(N)
    for a0 in range(0, N, chunk):
        b0 = min(a0 + chunk, N)
        dt = ts[a0:b0, None] - ts[None, :b0]
        maske = dt > 0.0
        dc = dt + c
        with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
            P = np.where(maske, dc ** (-p), 0.0)
        r2 = (xs[a0:b0, None] - xs[None, :b0]) ** 2 + (ys[a0:b0, None] - ys[None, :b0]) ** 2
        g = mekan_cekirdegi(r2, D, q, gamma, ms[:b0], m0)
        Ss[a0:b0] = np.sum(P * As[None, :b0] * g, axis=1)
    Ssp = np.empty(N)
    Ssp[o] = Ss
    lam = mu * u + Kk * Ssp
    if np.any(lam <= 0) or not np.all(np.isfinite(lam)):
        return -np.inf
    ell = float(np.log(lam).sum())
    tau = T - t
    I, _, _ = _omori_ilke(tau, c, p)
    if G is None:
        G = mekan_kutu_integrali(x, y, mekan_olcegi(D, gamma, mags, m0), q, kutu, metrik=met)
    return ell - mu * (T - t0) - Kk * float(np.sum(A * I * np.asarray(G, float)))


#: The space-time parameter file's normalisation tag; a file without it has ``D`` in degrees and
#: the midpoint ``G`` (the earlier degree metric), and the residual and declustering commands refuse it.
NORMALIZASYON = "kesin-kutu-integrali"


class UzayParametreHatasi(ValueError):
    """A space-time parameter file in the earlier degree metric, or fitted on another box's metric."""


def _nll_uzay_x(x, t, mags, xs, ys, m0, beta, t0, T, kutu, u_olay, dx, chunk):
    try:
        th = _x_den_theta(x, beta, UZAY_ADLARI)
        v = -logL_uzay_zaman(th, t, mags, xs, ys, m0, beta, t0, T, kutu, u_olay, dx, chunk)
        return v if np.isfinite(v) else 1e12
    except (OverflowError, FloatingPointError):
        return 1e12


def mle_uzay_zaman(t, mags, x, y, m0, beta, t0, T, kutu, u_olay=None, dx: float = 0.1,
                   baslangiclar=None, chunk: int = 500, maksiter: int = 400) -> dict:
    """Space-time ETAS MLE over the transformed parameters (declared start list).

    ``D`` is in km of :func:`yerel_metrik`; the result records the metric
    (``metrik``) and the normalisation (``normalizasyon``) so a consumer can refuse a
    parameter file in the earlier degree metric, whose ``D`` is in degrees.
    """
    bas = baslangiclar or BASLANGICLAR_UZAY
    en_iyi = None
    for b0 in bas:
        th0 = _dizi(b0, UZAY_ADLARI)
        x0 = _theta_dan_x(th0, beta)
        res = optimize.minimize(
            _nll_uzay_x, x0, args=(t, mags, x, y, m0, beta, t0, T, kutu, u_olay, dx, chunk),
            method="L-BFGS-B", bounds=optimize.Bounds(*UZAY_SINIRLAR),
            options={"maxiter": maksiter})
        if en_iyi is None or res.fun < en_iyi.fun:
            en_iyi = res
    th = _x_den_theta(en_iyi.x, beta, UZAY_ADLARI)
    H = hessian_nll_uzay(th, t, mags, x, y, m0, beta, t0, T, kutu, u_olay, dx, chunk)
    std, R, kosul, _ = _std_korelasyon(H)
    return {"parametreler": _sozluk(th, UZAY_ADLARI), "std": _sozluk(std, UZAY_ADLARI),
            "korelasyon": R.tolist(), "korelasyon_adlari": list(UZAY_ADLARI),
            "hessian_kosul": kosul, "logL": float(-en_iyi.fun), "nit": int(en_iyi.nit),
            "basari": bool(en_iyi.success), "m0": float(m0), "beta": float(beta),
            "t0": float(t0), "T": float(T), "n": int(np.size(t)), "model": "uzay-zaman",
            "metrik": yerel_metrik(kutu).kayit(), "normalizasyon": NORMALIZASYON}


def uzay_parametre_kontrol(p: dict, kutu) -> YerelMetrik:
    """Refuse, by name, a space-time parameter file this package cannot read in the km metric.

    A file in the earlier degree metric has no ``normalizasyon`` (its ``D`` is in degrees and its
    ``G`` the midpoint sum); a file whose recorded metric is not the one of ``kutu`` was
    fitted on another box.  Returns the metric to use.
    """
    if p.get("normalizasyon") != NORMALIZASYON:
        raise UzayParametreHatasi(
            "the space-time parameter file has no normalizasyon='kesin-kutu-integrali': it was fitted "
            "in the earlier degree metric (D in degrees, midpoint G) and must be refitted")
    met = yerel_metrik(kutu)
    kayit = p.get("metrik") or {}
    for alan in ("phi0", "lam0", "kx_km_derece", "ky_km_derece"):
        if alan not in kayit or abs(float(kayit[alan]) - float(met.kayit()[alan])) > 1e-9:
            raise UzayParametreHatasi(
                f"the space-time parameter file's metric ({alan}={kayit.get(alan)!r}) is not the metric of "
                f"the box {tuple(kutu)}")
    return met


def hessian_nll_uzay(theta, t, mags, x, y, m0, beta, t0, T, kutu, u_olay, dx, chunk,
                     adim: float = 1e-4) -> np.ndarray:
    n = len(theta)
    h = adim * np.maximum(np.abs(theta), 1e-3)
    f0 = -logL_uzay_zaman(theta, t, mags, x, y, m0, beta, t0, T, kutu, u_olay, dx, chunk)

    def f(v):
        return -logL_uzay_zaman(v, t, mags, x, y, m0, beta, t0, T, kutu, u_olay, dx, chunk)

    H = np.zeros((n, n))
    for i in range(n):
        for j in range(i, n):
            if i == j:
                a = theta.copy(); a[i] += h[i]
                b = theta.copy(); b[i] -= h[i]
                H[i, i] = (f(a) - 2.0 * f0 + f(b)) / h[i] ** 2
            else:
                a = theta.copy(); a[i] += h[i]; a[j] += h[j]
                b = theta.copy(); b[i] += h[i]; b[j] -= h[j]
                cc = theta.copy(); cc[i] -= h[i]; cc[j] += h[j]
                d = theta.copy(); d[i] -= h[i]; d[j] -= h[j]
                H[i, j] = H[j, i] = (f(a) - f(b) - f(cc) + f(d)) / (4.0 * h[i] * h[j])
    return H


# --- compute budget ----------------------------------------------------------

def yaklasik_cift_sayisi(t, pencere: float = VARSAYILAN_PENCERE_GUN) -> int:
    """Pairs (i, j) with 0 < t_j - t_i <= pencere, without building the matrix."""
    s = np.sort(np.asarray(t, float))
    sol = np.searchsorted(s, s - pencere, side="right")
    return int(np.sum(np.arange(s.size) - sol))


def mc_yukselt_ile_sinir(t, mags, mc0, maks_cift: float = VARSAYILAN_MAKS_CIFT, adim: float = 0.5,
                         pencere: float = VARSAYILAN_PENCERE_GUN):
    """Raise Mc in 0.5 steps until the pair count fits the declared budget."""
    mc = float(mc0)
    while True:
        sec = np.asarray(mags, float) >= mc
        n = int(sec.sum())
        cift = yaklasik_cift_sayisi(np.asarray(t, float)[sec], pencere)
        if cift <= maks_cift:
            return mc, {"mc": mc, "n": n, "cift": cift, "yukseltildi": mc > mc0 + 1e-12}
        mc = round(mc + adim, 10)
        if mc > float(np.max(mags)) + adim:
            raise RuntimeError("Mc raising did not bring the pair count under the budget")
