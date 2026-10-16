"""Çerçeveler: yerel yatay düzlem, fay düzlemi çerçevesi ve Voigt tensör dönüşümleri.

clean-room implementation from the equations published in Okada 1992 (BSSA 82(2),
1018-1040, DOI 10.1785/bssa0820021018); no code copied from cutde (MIT) or any other
Okada implementation.

The frame is fixed: north-east-down, all three components of every vector.  Every name
that carries a physical quantity ends in its unit (``_m``, ``_Pa``, ``_deg``, ``_N``,
``_kg``).  Tension is positive; a consumer's own conventions are declared by the
consumer and converted once by the ledger writer.

The fault-plane frame here is built from the *same angles and the same arithmetic* as
``knotenlinie.defter.geometri.fay_vektorleri``: x is along strike, y is the down-dip
direction and z = x × y is the fault normal (pointing into the half-space; for dip 90 it
is horizontal).  That is the frame ``okada_yerel`` is written in; it is *not* a
half-space frame whose z is true vertical down.
"""
from __future__ import annotations

import numpy as np

from .sabitler import LAM, MU

__all__ = [
    "ned_metre", "aeqd_metre", "yakinsama_rad", "yerel_cerceve", "yerelden_nede", "nede_yerel",
    "dud_gerilme", "fay_gerilmesi", "voigt_matris", "matris_voigt",
]


def ned_metre(lat_deg, lon_deg, *, lat0_deg, lon0_deg, R=6371000.0):
    """Equirectangular projection about ``(lat0_deg, lon0_deg)``; returns (north, east) metres.

    The bound: relative error below 0.5 % of the horizontal distance for |Δ| <= 1°
    (about 0.5 km at 100 km).  The tangent-plane receiver projection assumes this
    projection.  Δlon is wrapped into [-180°, 180°) (elastik 2.0.0), so a field given in
    0–360 and in −180–180 longitudes projects identically; the frozen signature is unchanged.
    """
    lat0 = np.deg2rad(np.asarray(lat0_deg, dtype=np.float64))
    kuzey_m = R * np.deg2rad(np.asarray(lat_deg, dtype=np.float64) - np.asarray(lat0_deg, dtype=np.float64))
    dlon = (np.asarray(lon_deg, dtype=np.float64) - np.asarray(lon0_deg, dtype=np.float64) + 180.0) % 360.0 - 180.0
    dogu_m = R * np.deg2rad(dlon) * np.cos(lat0)
    return kuzey_m, dogu_m


def aeqd_metre(lat_deg, lon_deg, *, lat0_deg, lon0_deg, R=6371000.0):
    """Azimuthal-equidistant projection about ``(lat0_deg, lon0_deg)``; returns (north, east) metres.

    ``(north_m, east_m) = (d cos alpha, d sin alpha)`` where ``d`` is the great-circle
    distance on the sphere of radius ``R`` and ``alpha`` is the forward azimuth at the
    centre.  A receiver at the centre gives ``(0, 0)``.  The distance uses the haversine /
    ``arctan2`` form, so it is stable arbitrarily close to the centre (no ``arccos``), and
    the longitude difference is wrapped into [-180, 180) first (as ``ned_metre`` does), so a
    receiver either side of 180 E is the small separation, not the long way round.

    The bound: this keeps the source-receiver distance and the azimuth from the source
    exactly, for every distance; it does not make the flat half-space spherical (the
    receiver's local frame is only rotated, ``okada_ned``).  It replaces ``ned_metre``'s
    equirectangular grid in ``okada_ned`` because the PSCMP sphere check found the equirectangular
    projection off by up to 86 km at 1000 km.
    """
    lat0 = np.deg2rad(np.asarray(lat0_deg, dtype=np.float64))
    lat = np.deg2rad(np.asarray(lat_deg, dtype=np.float64))
    dlon = np.deg2rad((np.asarray(lon_deg, dtype=np.float64) - np.asarray(lon0_deg, dtype=np.float64)
                       + 180.0) % 360.0 - 180.0)
    a = np.sin(0.5 * (lat - lat0)) ** 2 + np.cos(lat0) * np.cos(lat) * np.sin(0.5 * dlon) ** 2
    d_m = 2.0 * R * np.arctan2(np.sqrt(a), np.sqrt(np.clip(1.0 - a, 0.0, None)))
    az = np.arctan2(np.sin(dlon) * np.cos(lat),
                    np.cos(lat0) * np.sin(lat) - np.sin(lat0) * np.cos(lat) * np.cos(dlon))
    return d_m * np.cos(az), d_m * np.sin(az)


def yakinsama_rad(lat_deg, lon_deg, *, lat0_deg, lon0_deg):
    """Grid convergence ``gamma`` of the AEQD projection about ``(lat0_deg, lon0_deg)``, radians.

    ``gamma = (beta + pi) - alpha`` wrapped to ``(-pi, pi]``, with ``alpha`` the forward
    azimuth at the centre and ``beta`` the azimuth from the receiver back to the centre.
    It is the angle between the projection's grid north and the receiver's local north; it
    is ``0`` at the centre and on the centre's meridian, changes sign for receivers
    mirrored east and west, and is ``|gamma| = |Delta lon| sin(lat)`` to first order for a
    close pair on the same parallel.  A direction at grid azimuth ``theta`` therefore has
    local azimuth ``theta + gamma``, and the receiver's local north lies at grid azimuth
    ``-gamma``; ``okada_ned`` rotates the grid tensor by ``+gamma`` with it into the
    receiver's local NED (see the PSCMP sphere check in the tests).
    """
    lat0 = np.deg2rad(np.asarray(lat0_deg, dtype=np.float64))
    lat = np.deg2rad(np.asarray(lat_deg, dtype=np.float64))
    dlon = np.deg2rad((np.asarray(lon_deg, dtype=np.float64) - np.asarray(lon0_deg, dtype=np.float64)
                       + 180.0) % 360.0 - 180.0)
    alfa = np.arctan2(np.sin(dlon) * np.cos(lat),
                      np.cos(lat0) * np.sin(lat) - np.sin(lat0) * np.cos(lat) * np.cos(dlon))
    beta = np.arctan2(-np.sin(dlon) * np.cos(lat0),
                      np.cos(lat) * np.sin(lat0) - np.sin(lat) * np.cos(lat0) * np.cos(dlon))
    gamma = (beta + np.pi - alfa + np.pi) % (2.0 * np.pi) - np.pi
    # at the centre alpha and beta are undefined (0/0); the limit is gamma = 0, not the -pi the
    # half-open wrap would give (which would flip the horizontal signs).
    a = np.sin(0.5 * (lat - lat0)) ** 2 + np.cos(lat0) * np.cos(lat) * np.sin(0.5 * dlon) ** 2
    return np.where(a == 0.0, 0.0, gamma)


def _eksenler(dogrultu_deg, egim_deg):
    """The three fault-plane axes in NED, from the same angles as ``fay_vektorleri``."""
    S = np.deg2rad(np.asarray(dogrultu_deg, dtype=np.float64))
    d = np.deg2rad(np.asarray(egim_deg, dtype=np.float64))
    x = np.stack([np.cos(S), np.sin(S), np.zeros_like(S)], axis=-1)
    y = np.stack([-np.sin(S) * np.cos(d), np.cos(S) * np.cos(d), np.sin(d)], axis=-1)
    z = np.stack([np.sin(S) * np.sin(d), -np.cos(S) * np.sin(d), np.cos(d)], axis=-1)
    return x, y, z


def yerel_cerceve(dogrultu_deg, egim_deg):
    """Rotation ``R`` with ``v_yerel = R @ v_ned``; rows are the fault-plane axes in NED.

    x along strike, y down-dip, z = x × y the fault normal.  For strike 0 / dip 90 the
    north direction maps to the strike axis and the downward direction to the dip axis.
    """
    x, y, z = _eksenler(dogrultu_deg, egim_deg)
    return np.stack([x, y, z], axis=-2)


def voigt_matris(v):
    """Voigt-6 ``(xx, yy, zz, xy, xz, yz)`` -> symmetric ``(..., 3, 3)`` tensor."""
    v = np.asarray(v, dtype=np.float64)
    m = np.zeros(v.shape[:-1] + (3, 3), dtype=np.float64)
    m[..., 0, 0] = v[..., 0]
    m[..., 1, 1] = v[..., 1]
    m[..., 2, 2] = v[..., 2]
    m[..., 0, 1] = m[..., 1, 0] = v[..., 3]
    m[..., 0, 2] = m[..., 2, 0] = v[..., 4]
    m[..., 1, 2] = m[..., 2, 1] = v[..., 5]
    return m


def matris_voigt(m):
    """Symmetric ``(..., 3, 3)`` tensor -> Voigt-6 ``(xx, yy, zz, xy, xz, yz)``."""
    m = np.asarray(m, dtype=np.float64)
    return np.stack([
        m[..., 0, 0], m[..., 1, 1], m[..., 2, 2],
        m[..., 0, 1], m[..., 0, 2], m[..., 1, 2],
    ], axis=-1)


def yerelden_nede(tensor_yerel, dogrultu_deg, egim_deg):
    """Fault-plane Voigt tensor -> NED Voigt tensor: ``σ_ned = Rᵀ σ_yerel R``."""
    R = yerel_cerceve(dogrultu_deg, egim_deg)
    m = voigt_matris(tensor_yerel)
    Rt = np.swapaxes(R, -1, -2)
    nede = np.einsum("...ik,...kl,...lj->...ij", Rt, m, R)
    return matris_voigt(nede)


def nede_yerel(tensor_ned, dogrultu_deg, egim_deg):
    """NED Voigt tensor -> fault-plane Voigt tensor: ``σ_yerel = R σ_ned Rᵀ``."""
    R = yerel_cerceve(dogrultu_deg, egim_deg)
    m = voigt_matris(tensor_ned)
    Rt = np.swapaxes(R, -1, -2)
    yerel = np.einsum("...ik,...kl,...lj->...ij", R, m, Rt)
    return matris_voigt(yerel)


def dud_gerilme(dud, lam=LAM, mu=MU):
    """Displacement gradient -> stress, tension positive, Voigt-NED.

    ``dud[..., i, j] = ∂u_i/∂x_j`` (i along the frame's axes, NED here).  The symmetric
    part is the strain, ``ε = sym(∇u)``, and Hooke's law with the constants of ``sabitler`` gives
    ``σ = λ δ_ij tr(ε) + 2μ ε_ij``.  This is the one place the sign convention is
    applied: tension positive, Voigt order ``(xx, yy, zz, xy, xz, yz)``, exactly
    the ledger writer's ``s_xx_Pa … s_yz_Pa``.
    """
    d = np.asarray(dud, dtype=np.float64)
    eps = 0.5 * (d + np.swapaxes(d, -1, -2))
    tr = np.trace(eps, axis1=-2, axis2=-1)
    lam = float(lam)
    mu = float(mu)
    sigma = np.zeros_like(eps)
    for i in range(3):
        for j in range(3):
            sigma[..., i, j] = 2.0 * mu * eps[..., i, j]
    for i in range(3):
        sigma[..., i, i] += lam * tr
    return matris_voigt(sigma)


def fay_gerilmesi(tensor_ned, normal, slip):
    """Resolve a NED tensor onto a fault: delegates to ``knotenlinie.defter.geometri.gerilmeyi_coz``.

    Convenience only; the project's single implementation of the resolution lives in
    ``knotenlinie.defter``, and this function is bit-for-bit that function once a
    Voigt-6 input (the writer's ``s_xx_Pa … s_yz_Pa``) has been reshaped to a 3x3 tensor.
    """
    from knotenlinie.defter.geometri import gerilmeyi_coz

    t = np.asarray(tensor_ned, dtype=np.float64)
    if t.shape[-1] == 6:
        t = voigt_matris(t)
    return gerilmeyi_coz(t, normal, slip)
