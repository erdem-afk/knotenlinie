"""Synthetic ETAS simulator with known truth.

The simulator is the reference the estimator is checked against.  Parameters in
the tests come from pre-2015 literature (Falcone, Console & Murru 2010,
10.4401/ag-4760, for Italy; or Zhuang's example values), written into the test
file as literals and never tuned to make a test pass.

Standard branching: background (immigration) events from a Poisson process of
rate ``mu``, each event spawning a Poisson number of direct aftershocks,

    n_i = K * 10^{alpha*(M_i-M0)} * c^{1-p} / (p-1)          (temporal)

because ``int_0^inf (t+c)^-p dt = c^{1-p}/(p-1)``; each offspring time is drawn
from the normalised Omori law, ``dt = c*(U^{-1/(p-1)} - 1)``, and in the
space-time case its offset from the parent from the normalised 2-D kernel
``F(r) = 1 - (1 + r^2/D_i^2)^{-(q-1)}``.  Background/triggered labels and the
true parent index are kept for the declustering test.

The offset is drawn in km, isotropic, and mapped to degrees with the region's
:func:`knotenlinie.etas.model.yerel_metrik`, the same metric the
likelihood reads, so ``D`` is in km — pass ``metrik="km"``.  A space-time call must name its
metric: a ``bbox`` without ``metrik`` is refused by name
(:class:`MetrikHatasi`).  ``"derece"`` keeps the earlier degree draw (the offset added to longitude and
latitude as if both were the same length unit) only when asked for by name.

:func:`uretim` is a detection-free ETAS model; thinning its catalogue afterwards (:func:`incelt`)
lets undetected events trigger, which the ETAS-D likelihood (a sum over detected events) does not
represent.  :func:`uretim_tespitli` is the exact realisation of ETAS-D:
detection is decided at birth with the model's ``q(t, m)`` and an undetected event never triggers.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import model as M

EPOCH = pd.Timestamp("1985-01-01T00:00:00Z")


class MetrikHatasi(ValueError):
    """A space-time simulation (``bbox`` given) without a declared ``metrik``."""


def _gr_mag(rng, beta: float, mc: float, m_max: float, n: int) -> np.ndarray:
    u = rng.random(n)
    p = 1.0 - np.exp(-beta * (m_max - mc))
    return mc - np.log(1.0 - u * p) / beta


def _mekan_ofset(rng, D: float, q: float, gamma: float, ebeveyn_mag: float, mc: float, k: int):
    Di = D * 10.0 ** (gamma * (ebeveyn_mag - mc))
    u = rng.random(k)
    r = Di * np.sqrt((1.0 - u) ** (-1.0 / (q - 1.0)) - 1.0)
    a = rng.random(k) * 2.0 * np.pi
    return r * np.cos(a), r * np.sin(a)


def _arka_plan_konum(rng, lo0, lo1, la0, la1, n, f):
    """Draw ``n`` background positions inside the box with density proportional to ``f``.

    Rejection sampling; ``f`` is a callable ``f(lon, lat)`` in degrees returning an unnormalised
    density.  Its maximum is estimated on a 201 x 201 grid, so a hook whose peak is sharper than
    that grid over-samples slightly but stays unbiased in the limit (a dense grid keeps the
    rejection constant close to one).
    """
    if n <= 0:
        return [], []
    gl = np.linspace(lo0, lo1, 201)
    ga = np.linspace(la0, la1, 201)
    GL, GA = np.meshgrid(gl, ga)
    fmax = float(np.max(np.asarray(f(GL.ravel(), GA.ravel()), float)))
    if not fmax > 0.0:
        raise ValueError("the declared background density is zero everywhere on the box")
    xs, ys = [], []
    while len(xs) < n:
        k = max(4 * (n - len(xs)), 64)
        cl = rng.uniform(lo0, lo1, k)
        ca = rng.uniform(la0, la1, k)
        ok = rng.random(k) < np.asarray(f(cl, ca), float) / fmax
        xs += list(cl[ok])
        ys += list(ca[ok])
    return xs[:n], ys[:n]


def kusak_yogunlugu(kutu, aci_deg: float = -40.0, sigma_km: float = 15.0, taban: float = 0.10):
    """A NW-SE Gaussian belt background (unnormalised density on the box).

    A Gaussian ridge of width ``sigma_km`` along an axis at ``aci_deg`` from east, plus a uniform
    ``taban`` floor; the returned callable takes ``(lon, lat)`` in degrees and reads the box's km
    metric.  The fitted-parameter regime plus this belt (sigma 15 km, 10 % floor) is the third declared
    non-box known answer of the ``n_p`` re-selection.
    """
    met = M.yerel_metrik(kutu)
    aci = np.radians(float(aci_deg))

    def f(lon, lat):
        xk, yk = met.km(np.asarray(lon, float), np.asarray(lat, float))
        d = -np.sin(aci) * xk + np.cos(aci) * yk
        return np.exp(-d ** 2 / (2.0 * float(sigma_km) ** 2)) + float(taban)

    return f


def uretim(theta, t0: float, t1: float, mc: float, b: float, m_max: float = 6.5,
           seed: int = 20260929, bbox=None, en_cok: int = 200000, m_min: float = None,
           metrik: str = None, arka_plan=None) -> pd.DataFrame:
    """Simulate an ETAS catalog on ``[t0, t1]`` in days; returns a labelled table.

    Temporal when ``bbox`` is None, space-time (uniform background in ``bbox``)
    otherwise.  ``theta`` uses the model names (``mu, K, c, alpha, p[, D, q,
    gamma]``).  ``m_min`` (default ``mc``) is the lowest simulated magnitude; it
    must match the model's ``Mmin`` so the detection model's magnitude integral and the
    synthetic catalog cover the same range.  ``mu`` is always the model's rate of
    ``M >= M0 = mc`` events, so the background rate is scaled by
    ``exp(-beta*(m_min-mc))`` when ``m_min < mc``.  ``metrik`` is required with ``bbox``
    (a missing one raises :class:`MetrikHatasi`): ``"km"`` (``D`` in km of the
    box's :func:`knotenlinie.etas.model.yerel_metrik`) or ``"derece"`` (the earlier degree
    offsets, by name only).  Without ``bbox`` it is not used.

    ``arka_plan`` is an optional background-density hook: a callable
    ``f(lon, lat)`` in degrees returning an unnormalised density on the box.  Background positions
    are then drawn by rejection sampling (:func:`_arka_plan_konum`) instead of uniformly; the total
    background rate ``mu`` is unchanged, so ``nb`` keeps its Poisson draw.  The NW-SE belt recipe
    builds this callable with :func:`kusak_yogunlugu`.
    """
    rng = np.random.default_rng(seed)
    beta = b * np.log(10.0)
    m_min = float(mc) if m_min is None else float(m_min)
    onem = float(np.exp(-beta * (m_min - mc)))
    mu, Kk, c, alfa, p = (float(theta[k]) for k in ("mu", "K", "c", "alpha", "p"))
    uzay = bbox is not None
    if uzay:
        D, q, gama = (float(theta[k]) for k in ("D", "q", "gamma"))
        la0, la1, lo0, lo1 = bbox
        if metrik is None:
            raise MetrikHatasi("benzetim.uretim: a space-time simulation (bbox given) must name its metric, "
                               "metrik='km' or 'derece'; none was given")
        if metrik == "km":
            met = M.yerel_metrik(bbox)
            olcek_x, olcek_y = 1.0 / met.kx, 1.0 / met.ky      # km -> degrees of lon, lat
        elif metrik == "derece":
            olcek_x = olcek_y = 1.0
        else:
            raise ValueError(f"metrik must be 'km' or 'derece', got {metrik!r}")
    sure = t1 - t0
    nb = rng.poisson(mu * onem * sure)
    t = list(rng.random(nb) * sure + t0)
    mags = list(_gr_mag(rng, beta, m_min, m_max, nb))
    if not uzay:
        xs = list(np.zeros(nb))
        ys = list(np.zeros(nb))
    elif arka_plan is None:
        xs = list(rng.uniform(lo0, lo1, nb))
        ys = list(rng.uniform(la0, la1, nb))
    else:
        xs, ys = _arka_plan_konum(rng, lo0, lo1, la0, la1, nb, arka_plan)
    arka = [True] * nb
    ebeveyn = [-1] * nb
    i = 0
    while i < len(t):
        n_i = Kk * 10.0 ** (alfa * (mags[i] - mc)) * c ** (1.0 - p) / (p - 1.0) * onem
        k = rng.poisson(n_i)
        if k > 0 and len(t) < en_cok:
            u = rng.random(k)
            dt = c * (u ** (-1.0 / (p - 1.0)) - 1.0)
            tt = t[i] + dt
            mm = _gr_mag(rng, beta, m_min, m_max, k)
            if uzay:
                dx, dy = _mekan_ofset(rng, D, q, gama, mags[i], mc, k)
                xx = xs[i] + dx * olcek_x
                yy = ys[i] + dy * olcek_y
            else:
                xx = np.zeros(k)
                yy = np.zeros(k)
            for j in range(k):
                if tt[j] <= t1:
                    t.append(tt[j]); mags.append(mm[j]); xs.append(xx[j]); ys.append(yy[j])
                    arka.append(False); ebeveyn.append(i)
        i += 1
    t = np.asarray(t); mags = np.asarray(mags); xs = np.asarray(xs); ys = np.asarray(ys)
    arka = np.asarray(arka)
    ebe = np.asarray(ebeveyn)
    s = np.argsort(t, kind="stable")
    # remap the true parent index from the pre-sort order to the sorted order
    yeni = np.empty(t.size, dtype=int)
    yeni[s] = np.arange(t.size)
    ebe_sirali = np.where(ebe >= 0, yeni[np.clip(ebe, 0, t.size - 1)], -1)
    df = pd.DataFrame({
        "time_utc": EPOCH + pd.to_timedelta(t[s], unit="D"),
        "gun": t[s], "lat": ys[s], "lon": xs[s], "mag": mags[s],
        "arka_plan": arka[s], "ebeveyn": ebe_sirali[s]})
    df["ebeveyn"] = df["ebeveyn"].astype(int)
    df.attrs["theta"] = {k: float(theta[k]) for k in theta}
    df.attrs["mc"] = float(mc)
    df.attrs["b"] = float(b)
    return df.reset_index(drop=True)


def uretim_tespitli(theta, t0: float, t1: float, mc: float, b: float, q, m_max: float = 6.5,
                    seed: int = 20260929, m_min: float = None, en_cok: int = 400000) -> pd.DataFrame:
    """An exact temporal realisation of ETAS-D.

    Every event, background or offspring, is born with a magnitude from ``m_min`` (default ``mc``)
    and is **detected at birth** with probability ``q(t, m)`` (vectorised, clipped to [0, 1]); an
    undetected event is discarded and never triggers.  So the detected catalogue has the ETAS-D
    intensity ``q(t, m) f_GR(m) [mu + sum_{detected i} K 10^(alpha (M_i - M0)) (t - t_i + c)^-p]``
    with ``M0 = mc`` — a sum over detected events only, as the ETAS-D likelihood writes it.
    Rates, magnitudes and the Omori draw are those of :func:`uretim` (temporal).  Returns the
    detected events with ``time_utc, gun, lat, lon (0), mag, arka_plan, ebeveyn`` (the parent's
    index in the returned table, -1 for background); ``attrs['n_dogan']`` counts every event born
    inside ``[t0, t1]``.  A catalogue that reaches ``en_cok`` is **refused** by name, not silently
    truncated (as the earlier generator did).
    """
    rng = np.random.default_rng(seed)
    beta = b * np.log(10.0)
    m_min = float(mc) if m_min is None else float(m_min)
    onem = float(np.exp(-beta * (m_min - mc)))
    mu, Kk, c, alfa, p = (float(theta[k]) for k in ("mu", "K", "c", "alpha", "p"))

    def tespit(tt, mm):
        return rng.random(tt.size) < np.clip(np.asarray(q(tt, mm), float), 0.0, 1.0)

    nb = rng.poisson(mu * onem * (t1 - t0))
    tb = rng.random(nb) * (t1 - t0) + t0
    mb = _gr_mag(rng, beta, m_min, m_max, nb)
    sec = tespit(tb, mb)
    t, mags, ebeveyn, dogan = list(tb[sec]), list(mb[sec]), [-1] * int(sec.sum()), nb
    i = 0
    while i < len(t):
        k = rng.poisson(Kk * 10.0 ** (alfa * (mags[i] - mc)) * c ** (1.0 - p) / (p - 1.0) * onem)
        if k > 0 and len(t) < en_cok:
            tt = t[i] + c * (rng.random(k) ** (-1.0 / (p - 1.0)) - 1.0)
            mm = _gr_mag(rng, beta, m_min, m_max, k)
            sec = tespit(tt, mm) & (tt <= t1)
            dogan += int((tt <= t1).sum())
            t += list(tt[sec]); mags += list(mm[sec]); ebeveyn += [i] * int(sec.sum())
        i += 1
    t, mags, ebe = np.asarray(t, float), np.asarray(mags, float), np.asarray(ebeveyn, int)
    if t.size >= en_cok:
        raise ValueError(
            f"uretim_tespitli: the detected catalogue reached the declared bound en_cok={en_cok}; "
            "refused, not truncated")
    s = np.argsort(t, kind="stable")
    yeni = np.empty(t.size, dtype=int)
    yeni[s] = np.arange(t.size)
    ebe_sirali = np.where(ebe >= 0, yeni[np.clip(ebe, 0, max(t.size - 1, 0))], -1)[s]
    df = pd.DataFrame({"time_utc": EPOCH + pd.to_timedelta(t[s], unit="D"), "gun": t[s],
                       "lat": np.zeros(t.size), "lon": np.zeros(t.size), "mag": mags[s],
                       "arka_plan": ebe[s] < 0, "ebeveyn": ebe_sirali.astype(int)})
    df.attrs.update({"theta": {k: float(theta[k]) for k in theta}, "mc": float(mc), "b": float(b),
                     "n_dogan": int(dogan), "uretec": "tespitli"})
    return df.reset_index(drop=True)


def incelt(df: pd.DataFrame, q, seed: int = 20260929) -> pd.DataFrame:
    """Thin a complete catalog with a detection probability ``q(t, mag)`` (detection-model tests)."""
    rng = np.random.default_rng(seed)
    keep = rng.random(len(df)) < np.clip(np.asarray(q(df["gun"].to_numpy(), df["mag"].to_numpy())), 0, 1)
    return df.loc[keep].reset_index(drop=True)


def diziler(df: pd.DataFrame):
    """(t days, magnitudes, x=lon, y=lat) arrays for the model functions."""
    return (df["gun"].to_numpy(float), df["mag"].to_numpy(float),
            df["lon"].to_numpy(float), df["lat"].to_numpy(float))
