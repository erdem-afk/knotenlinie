"""Okada 1992 dikdörtgen dislokasyon çekirdeği (K9 aktarımı).

clean-room implementation from the equations published in Okada 1992 (BSSA 82(2),
1018-1040, DOI 10.1785/bssa0820021018); no code copied from cutde (MIT) or any other
Okada implementation.  Every expression
below was read from the page images of the 1992 paper (eqs. (14)-(17), Tables 6-9 and the
singularity rules on pp. 1030-1037); no third-party Okada implementation was opened.

**Frame of ``okada_yerel``.**
x along strike, y horizontal in the dip direction (to the right of the strike direction,
the side the fault dips towards), z down, metres, free surface ``z = 0``.  The fault is
centred on ``x = 0`` along strike, ``-L/2 <= x <= L/2`` (the antiplane check
evaluates at ``x = 0`` and expects the mid-length value; with ``0 <= x <= L`` that point is a
fault end and the field is exactly half), with its upper edge at depth ``ust_derinlik``
directly below ``y = 0``; it dips by ``egim_deg`` towards +y.  ``egim_deg`` is a **required**
keyword with ``0 < egim_deg <= 90`` (no hidden default: a forgotten dip would silently make the
fault vertical); a vertical fault is ``egim_deg=90``, whose plane is ``y = 0`` between the
depths ``ust_derinlik`` and ``ust_derinlik + W``.  The frame is *not* ``cerceve.yerel_cerceve`` (whose z is the
tilted fault normal): ``okada_ned`` rotates NED by the strike only, about the vertical, and
from the source grid into each receiver's local NED by the AEQD grid convergence (2.1.0).

**Mapping to Okada 1992 (Figs. 3 and 4; eqs. (12)-(13)).**  Okada's frame is ``(x, y, z up)``
with the fault's reference corner at ``(0, 0, -c)`` on its *lower* edge, the rectangle
running up-dip from there by ``W`` and along +x by ``L``, dipping towards -y.  The frame
here is Okada's rotated by 180 degrees about the strike axis and shifted to mid-length:
``x = x_O - L/2``, ``y = W cos(delta) - y_O``, ``z = -z_O``, with ``c = ust_derinlik + W sin(delta)``; vectors
and the gradient map with the signs ``(+1, -1, -1)``.

**Slip signs (Okada p. 1023, Fig. 3).**  ``U1 > 0`` is left-lateral strike slip, ``U2 > 0``
is reverse dip slip (the hanging wall, the block on the side the fault dips towards, moves
up relative to the foot wall; for a vertical fault the block at ``y > 0`` moves up) and
``U3 > 0`` is tensile opening.  Test (ii) asserts the U1 sign: ``d u_x / d y > 0`` across a
vertical fault, i.e. the block at ``y > 0`` moves in +x.

**Reading note.**  The derivative columns of Tables 7-9 are the derivatives of Table 6 only after the
Chinnery sum ``||`` of eq. (15): they omit terms that do not depend on ``eta`` (or on ``xi``) and
cancel between the corners (for example ``d Theta / d xi = -q Y11 + q / (q^2 + xi^2)``), so a single
corner must not be checked against a finite difference.  The tables are transcribed literally; where a
``(1 - alpha)`` factor covers only the first term of a column (Tables 8 and 9, column C) the code
does the same, and the finite-difference check of the full field confirms it.

**Singularities (Okada pp. 1031, 1034-1037).**  Rule (i) ``q = 0``: ``Theta = 0``; (ii)
``xi = 0``: ``I4 = 0``; (iii) ``R + xi = 0``: every ``R + xi`` denominator term is zero and
``ln(R + xi) -> -ln(R - xi)``; (iv) ``R + eta = 0`` likewise.  As the paper says (p. 1036-1037)
the rules apply when the quantity is *sufficiently small*, and the vertical-fault alternates
of ``I, J, K`` apply when ``cos(delta)`` is sufficiently small.  A point on a fault edge is
an essential singularity (the paper: set the output to a flag): the value there is not
finite or not meaningful and the caller must not evaluate on an edge.
"""
from __future__ import annotations

import numpy as np

from .sabitler import LAM, MU

__all__ = ["okada_yerel", "okada_ned", "kaynak_dogrula"]

_KAYNAK_ZORUNLU = (
    "dogrultu_deg", "egim_deg", "kayma_deg", "uzunluk_m", "genislik_m",
    "ust_derinlik_m", "kayma_m", "kaynak_lat", "kaynak_lon",
)
_KAYNAK_SECMELI = ("acilma_m",)

# "sufficiently small" thresholds of the paper's rules (pp. 1036-1037).  The length tolerance
# ``tol`` is absolute, ``_EPS_GORECELI`` times the largest coordinate magnitude of the problem
# (a receiver closer than that to a plane or line is on it to rounding); R + xi, R + eta and
# R + d~ are formed without cancellation, so no relative threshold on them is needed.
# NB: the tolerance scales with L, so for a fault 1e12 m long a receiver within about 1 m of a
# plane is treated as on it (harmless for realistic sizes: 1e-8 m at 10 km).
_EPS_GORECELI = 1.0e-12
# |cos(delta)| below this uses the vertical-fault alternates.  Balance point between the alternates'
# O(cos delta) error and the oblique branch's roundoff ~ eps / cos^2 (about (1e-16)^(1/3)); for
# 5e-6 < cos delta < 1e-4 (dip 89.994 to 89.9997 degrees) the field carries noise of order 3e-5 of
# its maximum, outside that window below 1e-5.  Physically irrelevant for DISS dips.
_EPS_KOS = 5.0e-6


def kaynak_dogrula(kaynak):
    """Validate the frozen source mapping's keys without a hidden default.

    ``okada_ned`` calls it first, so an unknown or missing key is named before any maths.
    """
    if not isinstance(kaynak, dict):
        raise ValueError(f"kaynak bir sözlük olmalı, alındı: {type(kaynak).__name__}")
    bilinmeyen = sorted(set(kaynak) - set(_KAYNAK_ZORUNLU) - set(_KAYNAK_SECMELI))
    if bilinmeyen:
        raise ValueError(f"kaynak sözlüğünde bilinmeyen anahtar: {bilinmeyen}")
    eksik = [a for a in _KAYNAK_ZORUNLU if a not in kaynak]
    if eksik:
        raise ValueError(f"kaynak sözlüğünde eksik anahtar: {eksik}")
    return dict(kaynak)


def _kararli_toplam(R, a, b2):
    """``R + a`` without cancellation: ``R + a = b2 / (R - a)`` for ``a < 0``, ``b2 = R**2 - a**2``."""
    pozitif = a >= 0.0
    return np.where(pozitif, R + a, b2 / np.where(pozitif, 1.0, R - a))


def _ters_ve_sifir(rpa, sifir):
    """1/(R + a), and 0 on the singular line where ``sifir`` marks R + a = 0 (rules iii and iv)."""
    return np.where(sifir, 0.0, 1.0 / np.where(sifir, 1.0, rpa))


class _Taban:
    """The shared variables of eq. (14) and of the footers of Tables 6-9 at one (xi, eta, q, z)."""

    def __init__(self, xi, eta, q, z, sd, cd, alfa, tol):
        self.xi, self.eta, self.q, self.z = xi, eta, q, z
        self.sd, self.cd, self.a = sd, cd, alfa
        self.ca = 1.0 - alfa
        R = np.sqrt(xi * xi + eta * eta + q * q)
        self.R = R
        Rg = np.where(R == 0.0, 1.0, R)           # R = 0 is an essential singularity (fault edge)
        self.yt = eta * cd + q * sd               # y~, Table 6 header
        self.dt = eta * sd - q * cd               # d~, Table 6 header
        self.ct = self.dt + z                     # c~, Table 6 header
        X = np.sqrt(xi * xi + q * q)              # X^2 = xi^2 + q^2, Table 6 footer
        # rule (iii): R + xi = 0 (xi < 0 and eta = q = 0), rule (iv): R + eta = 0 (p. 1034)
        rpx = _kararli_toplam(R, xi, eta * eta + q * q)
        rpe = _kararli_toplam(R, eta, xi * xi + q * q)
        rx0 = (xi < 0.0) & (np.hypot(eta, q) <= tol)
        re0 = (eta < 0.0) & (np.hypot(xi, q) <= tol)
        inv_rx = _ters_ve_sifir(rpx, rx0)
        inv_re = _ters_ve_sifir(rpe, re0)
        self.lnRxi = np.where(rx0, -np.log(np.where(rx0, R - xi, 1.0)), np.log(np.where(rx0, 1.0, rpx)))
        self.lnReta = np.where(re0, -np.log(np.where(re0, R - eta, 1.0)), np.log(np.where(re0, 1.0, rpe)))
        inv_R = 1.0 / Rg
        # eq. (14), p. 1026
        self.X11 = inv_R * inv_rx
        self.X32 = (2.0 * R + xi) * inv_R ** 3 * inv_rx ** 2
        self.X53 = (8.0 * R * R + 9.0 * R * xi + 3.0 * xi * xi) * inv_R ** 5 * inv_rx ** 3
        self.Y11 = inv_R * inv_re
        self.Y32 = (2.0 * R + eta) * inv_R ** 3 * inv_re ** 2
        self.Y53 = (8.0 * R * R + 9.0 * R * eta + 3.0 * eta * eta) * inv_R ** 5 * inv_re ** 3
        h = q * cd - z
        self.Z32 = sd * inv_R ** 3 - h * self.Y32
        self.Z53 = 3.0 * sd * inv_R ** 5 - h * self.Y53
        self.Y0 = self.Y11 - xi * xi * self.Y32
        self.Z0 = self.Z32 - xi * xi * self.Z53
        self.iR = inv_R
        self.iR3 = inv_R ** 3
        self.iR5 = inv_R ** 5
        # Theta = atan(xi eta / (q R)); rule (i): q = 0 -> Theta = 0 (Table 6 footer, p. 1034)
        q0 = np.abs(q) <= tol
        self.Theta = np.where(q0, 0.0, np.arctan(xi * eta / (np.where(q0, 1.0, q) * Rg)))
        # R + d~ denominators of I, J, K; zero on the singular line R + d~ = 0 (the factor
        # multiplying it vanishes there, as for rule iv)
        rpd = _kararli_toplam(R, self.dt, xi * xi + self.yt * self.yt)
        rd0 = (self.dt < 0.0) & (np.hypot(xi, self.yt) <= tol)
        inv_rd = _ters_ve_sifir(rpd, rd0)
        lnRd = np.where(rd0, 0.0, np.log(np.where(rd0, 1.0, rpd)))
        self.inv_rd = inv_rd
        vert = np.abs(cd) < _EPS_KOS              # pp. 1036-1037: alternates when cos(delta) ~ 0
        cds = np.where(vert, 1.0, cd)             # safe divisor for the oblique branch
        # I4, I3, I2, I1, Table 6 footer p. 1030; rule (ii): xi = 0 -> I4 = 0
        xi0 = np.abs(xi) <= tol
        arg_pay = eta * (X + q * cd) + X * (R + X) * sd
        arg_den = np.where(xi0, 1.0, xi * (R + X) * cds)
        arg_den = np.where(arg_den == 0.0, 1.0, arg_den)
        I4_obl = sd / cds * xi * inv_rd + 2.0 / cds ** 2 * np.arctan(arg_pay / arg_den)
        I4_obl = np.where(xi0, 0.0, I4_obl)
        I4_dik = 0.5 * xi * self.yt * inv_rd ** 2
        self.I4 = np.where(vert, I4_dik, I4_obl)
        I3_obl = (1.0 / cds) * self.yt * inv_rd - (1.0 / cds ** 2) * (self.lnReta - sd * lnRd)
        I3_dik = 0.5 * (eta * inv_rd + self.yt * q * inv_rd ** 2 - self.lnReta)
        self.I3 = np.where(vert, I3_dik, I3_obl)
        self.I2 = lnRd + self.I3 * sd
        self.I1 = -xi * inv_rd * cd - self.I4 * sd
        # D11, K1-K4, J1-J6, Table 7 footer p. 1031
        D11 = inv_R * inv_rd
        self.D11 = D11
        K1 = np.where(vert, xi * q * inv_rd * D11, xi / cds * (D11 - self.Y11 * sd))
        K3 = np.where(vert, sd * inv_rd * (xi * xi * D11 - 1.0), (1.0 / cds) * (q * self.Y11 - self.yt * D11))
        self.K1, self.K3 = K1, K3
        self.K2 = inv_R + K3 * sd
        self.K4 = xi * self.Y11 * cd - K1 * sd
        J2 = xi * self.yt * inv_rd * D11
        J5 = -(self.dt + self.yt ** 2 * inv_rd) * D11
        J3 = np.where(vert, -xi * inv_rd ** 2 * (q * q * D11 - 0.5), (1.0 / cds) * (K1 - J2 * sd))
        J6 = np.where(vert, -self.yt * inv_rd ** 2 * (xi * xi * D11 - 0.5), (1.0 / cds) * (K3 - J5 * sd))
        self.J1 = J5 * cd - J6 * sd
        self.J2, self.J3, self.J5, self.J6 = J2, J3, J5, J6
        self.J4 = -xi * self.Y11 - J2 * cd + J3 * sd


# Each table function returns ``[type][component]``: type 0 strike, 1 dip, 2 tensile; component
# 0, 1, 2 are the paper's f1, f2, f3 (up-dip and normal directions, eqs. (16)-(17)).

def _ab_u(t):
    """Table 6 (p. 1030), columns f^A and f^B."""
    a, ca, sd, cd = t.a, t.ca, t.sd, t.cd
    xi, eta, q = t.xi, t.eta, t.q
    k = ca / a
    fA = [
        [t.Theta / 2 + a / 2 * xi * q * t.Y11, a / 2 * q * t.iR, ca / 2 * t.lnReta - a / 2 * q * q * t.Y11],
        [a / 2 * q * t.iR, t.Theta / 2 + a / 2 * eta * q * t.X11, ca / 2 * t.lnRxi - a / 2 * q * q * t.X11],
        [-ca / 2 * t.lnReta - a / 2 * q * q * t.Y11, -ca / 2 * t.lnRxi - a / 2 * q * q * t.X11,
         t.Theta / 2 - a / 2 * q * (eta * t.X11 + xi * t.Y11)],
    ]
    fB = [
        [-xi * q * t.Y11 - t.Theta - k * t.I1 * sd, -q * t.iR + k * t.yt * t.inv_rd * sd,
         q * q * t.Y11 - k * t.I2 * sd],
        [-q * t.iR + k * t.I3 * sd * cd, -eta * q * t.X11 - t.Theta - k * xi * t.inv_rd * sd * cd,
         q * q * t.X11 + k * t.I4 * sd * cd],
        [q * q * t.Y11 - k * t.I3 * sd * sd, q * q * t.X11 + k * xi * t.inv_rd * sd * sd,
         q * (eta * t.X11 + xi * t.Y11) - t.Theta - k * t.I4 * sd * sd],
    ]
    return fA, fB


def _c_u(t):
    """Table 6 (p. 1030), column f^C."""
    a, ca, sd, cd, z = t.a, t.ca, t.sd, t.cd, t.z
    xi, eta, q = t.xi, t.eta, t.q
    return [
        [ca * xi * t.Y11 * cd - a * xi * q * t.Z32,
         ca * (cd * t.iR + 2 * q * t.Y11 * sd) - a * t.ct * q * t.iR3,
         ca * q * t.Y11 * cd - a * (t.ct * eta * t.iR3 - z * t.Y11 + xi * xi * t.Z32)],
        [ca * cd * t.iR - q * t.Y11 * sd - a * t.ct * q * t.iR3,
         ca * t.yt * t.X11 - a * t.ct * eta * q * t.X32,
         -t.dt * t.X11 - xi * t.Y11 * sd - a * t.ct * (t.X11 - q * q * t.X32)],
        [-ca * (sd * t.iR + q * t.Y11 * cd) - a * (z * t.Y11 - q * q * t.Z32),
         ca * 2 * xi * t.Y11 * sd + t.dt * t.X11 - a * t.ct * (t.X11 - q * q * t.X32),
         ca * (t.yt * t.X11 + xi * t.Y11 * cd) + a * q * (t.ct * eta * t.X32 + xi * t.Z32)],
    ]


def _ab_dx(t):
    """Table 7 (p. 1031), columns df^A/dx and df^B/dx."""
    a, ca, sd, cd = t.a, t.ca, t.sd, t.cd
    xi, eta, q = t.xi, t.eta, t.q
    k = ca / a
    dA = [
        [-ca / 2 * q * t.Y11 - a / 2 * xi * xi * q * t.Y32, -a / 2 * xi * q * t.iR3,
         ca / 2 * xi * t.Y11 + a / 2 * xi * q * q * t.Y32],
        [-a / 2 * xi * q * t.iR3, -q / 2 * t.Y11 - a / 2 * eta * q * t.iR3,
         ca / 2 * t.iR + a / 2 * q * q * t.iR3],
        [-ca / 2 * xi * t.Y11 + a / 2 * xi * q * q * t.Y32, -ca / 2 * t.iR + a / 2 * q * q * t.iR3,
         -ca / 2 * q * t.Y11 - a / 2 * q ** 3 * t.Y32],
    ]
    dB = [
        [xi * xi * q * t.Y32 - k * t.J1 * sd, xi * q * t.iR3 - k * t.J2 * sd,
         -xi * q * q * t.Y32 - k * t.J3 * sd],
        [xi * q * t.iR3 + k * t.J4 * sd * cd, eta * q * t.iR3 + q * t.Y11 + k * t.J5 * sd * cd,
         -q * q * t.iR3 + k * t.J6 * sd * cd],
        [-xi * q * q * t.Y32 - k * t.J4 * sd * sd, -q * q * t.iR3 - k * t.J5 * sd * sd,
         q ** 3 * t.Y32 - k * t.J6 * sd * sd],
    ]
    return dA, dB


def _c_dx(t):
    """Table 7 (p. 1031), column df^C/dx."""
    a, ca, sd, cd, z = t.a, t.ca, t.sd, t.cd, t.z
    xi, eta, q = t.xi, t.eta, t.q
    return [
        [ca * t.Y0 * cd - a * q * t.Z0,
         -ca * xi * (cd * t.iR3 + 2 * q * t.Y32 * sd) + a * 3 * t.ct * xi * q * t.iR5,
         -ca * xi * q * t.Y32 * cd + a * xi * (3 * t.ct * eta * t.iR5 - z * t.Y32 - t.Z32 - t.Z0)],
        [-ca * xi * t.iR3 * cd + xi * q * t.Y32 * sd + a * 3 * t.ct * xi * q * t.iR5,
         -ca * t.yt * t.iR3 + a * 3 * t.ct * eta * q * t.iR5,
         t.dt * t.iR3 - t.Y0 * sd + a * t.ct * t.iR3 * (1 - 3 * q * q * t.iR ** 2)],
        [ca * xi * t.iR3 * sd + xi * q * t.Y32 * cd + a * xi * (3 * t.ct * eta * t.iR5 - 2 * t.Z32 - t.Z0),
         ca * 2 * t.Y0 * sd - t.dt * t.iR3 + a * t.ct * t.iR3 * (1 - 3 * q * q * t.iR ** 2),
         -ca * (t.yt * t.iR3 - t.Y0 * cd) - a * (3 * t.ct * eta * q * t.iR5 - q * t.Z0)],
    ]


def _efgh(t):
    """Table 8 footer (p. 1032): E, F, G, H, P, Q."""
    sd, cd = t.sd, t.cd
    q, xi = t.q, t.xi
    E = sd * t.iR - t.yt * q * t.iR3
    F = t.dt * t.iR3 + xi * xi * t.Y32 * sd
    G = 2 * t.X11 * sd - t.yt * q * t.X32
    H = t.dt * q * t.X32 + xi * q * t.Y32 * sd
    P = cd * t.iR3 + q * t.Y32 * sd
    Q = 3 * t.ct * t.dt * t.iR5 - (t.z * t.Y32 + t.Z32 + t.Z0) * sd
    return E, F, G, H, P, Q


def _ab_dy(t):
    """Table 8 (p. 1032), columns df^A/dy and df^B/dy."""
    a, ca, sd, cd = t.a, t.ca, t.sd, t.cd
    xi, eta, q = t.xi, t.eta, t.q
    k = ca / a
    E, F, G, H, _, _ = _efgh(t)
    dA = [
        [ca / 2 * xi * t.Y11 * sd + t.dt / 2 * t.X11 + a / 2 * xi * F, a / 2 * E,
         ca / 2 * (cd * t.iR + q * t.Y11 * sd) - a / 2 * q * F],
        [a / 2 * E, ca / 2 * t.dt * t.X11 + xi / 2 * t.Y11 * sd + a / 2 * eta * G,
         ca / 2 * t.yt * t.X11 - a / 2 * q * G],
        [-ca / 2 * (cd * t.iR + q * t.Y11 * sd) - a / 2 * q * F, -ca / 2 * t.yt * t.X11 - a / 2 * q * G,
         ca / 2 * (t.dt * t.X11 + xi * t.Y11 * sd) + a / 2 * q * H],
    ]
    dB = [
        [-xi * F - t.dt * t.X11 + k * (xi * t.Y11 + t.J4) * sd, -E + k * (t.iR + t.J5) * sd,
         q * F - k * (q * t.Y11 - t.J6) * sd],
        [-E + k * t.J1 * sd * cd, -eta * G - xi * t.Y11 * sd + k * t.J2 * sd * cd, q * G + k * t.J3 * sd * cd],
        [q * F - k * t.J1 * sd * sd, q * G - k * t.J2 * sd * sd, -q * H - k * t.J3 * sd * sd],
    ]
    return dA, dB


def _c_dy(t):
    """Table 8 (p. 1032), column df^C/dy."""
    a, ca, sd, cd, z = t.a, t.ca, t.sd, t.cd, t.z
    xi, eta, q = t.xi, t.eta, t.q
    _, _, _, _, P, Q = _efgh(t)
    return [
        [-ca * xi * P * cd - a * xi * Q,
         2 * ca * (t.dt * t.iR3 - t.Y0 * sd) * sd - t.yt * t.iR3 * cd
         - a * ((t.ct + t.dt) * t.iR3 * sd - eta * t.iR3 - 3 * t.ct * t.yt * q * t.iR5),
         -ca * q * t.iR3 + (t.yt * t.iR3 - t.Y0 * cd) * sd
         + a * ((t.ct + t.dt) * t.iR3 * cd + 3 * t.ct * t.dt * q * t.iR5 - (t.Y0 * cd + q * t.Z0) * sd)],
        [-ca * eta * t.iR3 + t.Y0 * sd * sd - a * ((t.ct + t.dt) * t.iR3 * sd - 3 * t.ct * t.yt * q * t.iR5),
         ca * (t.X11 - t.yt ** 2 * t.X32) - a * t.ct * ((t.dt + 2 * q * cd) * t.X32 - t.yt * eta * q * t.X53),
         xi * P * sd + t.yt * t.dt * t.X32 + a * t.ct * ((t.yt + 2 * q * sd) * t.X32 - t.yt * q * q * t.X53)],
        [ca * (q * t.iR3 + t.Y0 * sd * cd) + a * (z * t.iR3 * cd + 3 * t.ct * t.dt * q * t.iR5 - q * t.Z0 * sd),
         -ca * 2 * xi * P * sd - t.yt * t.dt * t.X32 + a * t.ct * ((t.yt + 2 * q * sd) * t.X32 - t.yt * q * q * t.X53),
         -ca * (xi * P * cd - t.X11 + t.yt ** 2 * t.X32)
         + a * t.ct * ((t.dt + 2 * q * cd) * t.X32 - t.yt * eta * q * t.X53) + a * xi * Q],
    ]


def _efgh_z(t):
    """Table 9 footer (p. 1033): E', F', G', H', P', Q'."""
    cd = t.cd
    q, xi = t.q, t.xi
    E = cd * t.iR + t.dt * q * t.iR3
    F = t.yt * t.iR3 + xi * xi * t.Y32 * cd
    G = 2 * t.X11 * cd + t.dt * q * t.X32
    H = t.yt * q * t.X32 + xi * q * t.Y32 * cd
    P = t.sd * t.iR3 - q * t.Y32 * cd
    Q = 3 * t.ct * t.yt * t.iR5 + q * t.Y32 - (t.z * t.Y32 + t.Z32 + t.Z0) * cd
    return E, F, G, H, P, Q


def _ab_dz(t):
    """Table 9 (p. 1033), columns df^A/dz and df^B/dz."""
    a, ca, sd, cd = t.a, t.ca, t.sd, t.cd
    xi, eta, q = t.xi, t.eta, t.q
    k = ca / a
    E, F, G, H, _, _ = _efgh_z(t)
    dA = [
        [ca / 2 * xi * t.Y11 * cd + t.yt / 2 * t.X11 + a / 2 * xi * F, a / 2 * E,
         -ca / 2 * (sd * t.iR - q * t.Y11 * cd) - a / 2 * q * F],
        [a / 2 * E, ca / 2 * t.yt * t.X11 + xi / 2 * t.Y11 * cd + a / 2 * eta * G,
         -ca / 2 * t.dt * t.X11 - a / 2 * q * G],
        [ca / 2 * (sd * t.iR - q * t.Y11 * cd) - a / 2 * q * F, ca / 2 * t.dt * t.X11 - a / 2 * q * G,
         ca / 2 * (t.yt * t.X11 + xi * t.Y11 * cd) + a / 2 * q * H],
    ]
    dB = [
        [-xi * F - t.yt * t.X11 + k * t.K1 * sd, -E + k * t.yt * t.D11 * sd, q * F + k * t.K2 * sd],
        [-E - k * t.K3 * sd * cd, -eta * G - xi * t.Y11 * cd - k * xi * t.D11 * sd * cd, q * G - k * t.K4 * sd * cd],
        [q * F + k * t.K3 * sd * sd, q * G + k * xi * t.D11 * sd * sd, -q * H + k * t.K4 * sd * sd],
    ]
    return dA, dB


def _c_dz(t):
    """Table 9 (p. 1033), column df^C/dz."""
    a, ca, sd, cd, z = t.a, t.ca, t.sd, t.cd, t.z
    xi, eta, q = t.xi, t.eta, t.q
    _, _, _, _, P, Q = _efgh_z(t)
    return [
        [ca * xi * P * cd - a * xi * Q,
         2 * ca * (t.yt * t.iR3 - t.Y0 * cd) * sd + t.dt * t.iR3 * cd
         - a * ((t.ct + t.dt) * t.iR3 * cd + 3 * t.ct * t.dt * q * t.iR5),
         (t.yt * t.iR3 - t.Y0 * cd) * cd
         - a * ((t.ct + t.dt) * t.iR3 * sd - 3 * t.ct * t.yt * q * t.iR5 - t.Y0 * sd * sd + q * t.Z0 * cd)],
        [-q * t.iR3 + t.Y0 * sd * cd - a * ((t.ct + t.dt) * t.iR3 * cd + 3 * t.ct * t.dt * q * t.iR5),
         ca * t.yt * t.dt * t.X32 - a * t.ct * ((t.yt - 2 * q * sd) * t.X32 + t.dt * eta * q * t.X53),
         -xi * P * sd + t.X11 - t.dt ** 2 * t.X32 - a * t.ct * ((t.dt - 2 * q * cd) * t.X32 - t.dt * q * q * t.X53)],
        [-eta * t.iR3 + t.Y0 * cd * cd
         - a * (z * t.iR3 * sd - 3 * t.ct * t.yt * q * t.iR5 - t.Y0 * sd * sd + q * t.Z0 * cd),
         ca * 2 * xi * P * sd - t.X11 + t.dt ** 2 * t.X32 - a * t.ct * ((t.dt - 2 * q * cd) * t.X32 - t.dt * q * q * t.X53),
         ca * (xi * P * cd + t.yt * t.dt * t.X32) + a * t.ct * ((t.yt - 2 * q * sd) * t.X32 + t.dt * eta * q * t.X53)
         + a * xi * Q],
    ]


def _zincir(parcalar, isaretler):
    """Chinnery's notation, eq. (15) (p. 1026): sum the four corner values with their signs."""
    toplam = None
    for p, s in zip(parcalar, isaretler):
        v = [[np.asarray(p[k][i]) * s for i in range(3)] for k in range(3)]
        toplam = v if toplam is None else [[toplam[k][i] + v[k][i] for i in range(3)] for k in range(3)]
    return toplam


def _okada_orijinal(x, y, z, L, W, c, delta, U, alfa):
    """Okada 1992 half-space field in the paper's own frame (z up, source corner at (0, 0, -c)).

    Returns ``u`` ``(..., 3)`` and ``dud`` ``(..., 3, 3)`` with ``dud[..., i, j] = du_i/dx_j``.
    """
    sd, cd = np.sin(delta), np.cos(delta)
    x, y, z = np.broadcast_arrays(np.asarray(x, dtype=np.float64), np.asarray(y, dtype=np.float64),
                                  np.asarray(z, dtype=np.float64))
    d = c - z                                    # Table 6 header
    p = y * cd + d * sd
    q = y * sd - d * cd
    dh = c + z                                   # the image fault, f(xi, eta, -z): z -> -z
    ph = y * cd + dh * sd
    qh = y * sd - dh * cd
    # eq. (15): f(x, p) - f(x, p - W) - f(x - L, p) + f(x - L, p - W)
    esler = [(x, p, ph, 1.0), (x, p - W, ph - W, -1.0), (x - L, p, ph, -1.0), (x - L, p - W, ph - W, 1.0)]
    tol = _EPS_GORECELI * (np.abs(x) + np.abs(y) + np.abs(z) + L + W + abs(c))
    reel = [(_Taban(xi, eta, q, z, sd, cd, alfa, tol), s) for xi, eta, _, s in esler]
    yans = [(_Taban(xi, etah, qh, -z, sd, cd, alfa, tol), s) for (xi, _, etah, s) in esler]
    isr = [s for _, s in reel]
    ta = [t for t, _ in reel]
    th = [t for t, _ in yans]

    def blok(ab_f, c_f, aynala):
        gercek = [ab_f(t) for t in ta]
        A = _zincir([g[0] for g in gercek], isr)
        B = _zincir([g[1] for g in gercek], isr)
        Ah = _zincir([ab_f(t)[0] for t in th], isr)
        C = _zincir([c_f(t) for t in ta], isr) if c_f is not None else None
        return A, Ah, B, C

    def birlestir(A, Ah, B, C, uC, zz, yon):
        """Eqs. (16)-(17) and the first lines of Tables 6-9: the three Cartesian components."""
        # yon = "fark": u^A - u^A_hat (Tables 6-8); "toplam": l^A + l^A_hat (Table 9)
        sonuc = np.zeros(zz.shape + (3,))
        for k in range(3):
            if U[k] == 0.0:
                continue
            Aef = [A[k][i] - Ah[k][i] if yon == "fark" else A[k][i] + Ah[k][i] for i in range(3)]
            if yon == "fark":
                f = [Aef[i] + B[k][i] + zz * C[k][i] for i in range(3)]
                g = [Aef[i] + B[k][i] - zz * C[k][i] for i in range(3)]
            else:                                # Table 9: + u^C_i + z l^C_i  (and - for the z comp.)
                f = [Aef[i] + B[k][i] + uC[k][i] + zz * C[k][i] for i in range(3)]
                g = [Aef[i] + B[k][i] - uC[k][i] - zz * C[k][i] for i in range(3)]
            fak = U[k] / (2.0 * np.pi)
            sonuc[..., 0] += fak * f[0]
            sonuc[..., 1] += fak * (f[1] * cd - f[2] * sd)
            sonuc[..., 2] += fak * (g[1] * sd + g[2] * cd)
        return sonuc

    uA, uAh, uB, uC = blok(_ab_u, _c_u, None)
    u = birlestir(uA, uAh, uB, uC, None, z, "fark")
    dud = np.zeros(z.shape + (3, 3))
    for j, (ab_f, c_f) in enumerate(((_ab_dx, _c_dx), (_ab_dy, _c_dy))):
        A, Ah, B, C = blok(ab_f, c_f, None)
        dud[..., :, j] = birlestir(A, Ah, B, C, None, z, "fark")
    A, Ah, B, C = blok(_ab_dz, _c_dz, None)
    dud[..., :, 2] = birlestir(A, Ah, B, C, uC, z, "toplam")
    return u, dud


def okada_yerel(x, y, z, *, L, W, ust_derinlik, U1, U2, U3, egim_deg, lam=LAM, mu=MU):
    """Fault-local displacement and gradient of a rectangular Okada 1992 source.

    Returns ``(u, dud)`` with ``u`` shaped ``(..., 3)`` in metres and
    ``dud[..., i, j] = ∂u_i/∂x_j``, dimensionless, broadcast over a leading receiver
    axis.  Frame (module docstring): x along strike, y horizontal to the right of the
    strike direction (the side the fault dips towards), z down, free surface ``z = 0``,
    metres.  The fault is ``-L/2 <= x <= L/2``; its upper edge is at depth ``ust_derinlik``
    directly below ``y = 0``; its down-dip width is ``W`` and it dips by ``egim_deg``
    (required, ``0 < egim_deg <= 90``, 90 is vertical) towards +y.  ``U1``, ``U2``, ``U3`` (m) are the strike-slip
    (positive left-lateral), dip-slip (positive reverse: the block on the dipping side
    moves up) and tensile (positive opening) components of the dislocation.  ``lam`` and
    ``mu`` enter only through ``alpha = (lam + mu) / (lam + 2 mu)``.

    A receiver on a fault edge is an essential singularity (Okada p. 1031); the result
    there is not meaningful.  A receiver above the free surface (``z < 0``) is refused.
    """
    if not (0.0 < float(egim_deg) <= 90.0):
        raise ValueError(f"egim_deg must satisfy 0 < egim_deg <= 90, got {egim_deg!r}")
    if np.any(np.asarray(z, dtype=np.float64) < 0.0):
        raise ValueError("z < 0: the receiver is above the free surface (z is depth, z >= 0)")
    delta = np.deg2rad(float(egim_deg))
    alfa = (lam + mu) / (lam + 2.0 * mu)
    c = float(ust_derinlik) + float(W) * np.sin(delta)
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    z = np.asarray(z, dtype=np.float64)
    x, y, z = np.broadcast_arrays(x, y, z)
    xo = x + 0.5 * float(L)                      # Okada's x: the fault spans 0 <= x_O <= L
    yo = float(W) * np.cos(delta) - y            # Okada's y
    zo = -z                                      # Okada's z (up)
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):   # guarded branches of np.where
        u_o, dud_o = _okada_orijinal(xo, yo, zo, float(L), float(W), c, delta,
                                     (float(U1), float(U2), float(U3)), alfa)
    s = np.array([1.0, -1.0, -1.0])
    return u_o * s, dud_o * s[:, None] * s[None, :]


def kayma_bilesenleri(kaynak):
    """``(U1, U2, U3)`` in metres from a source mapping: ``kayma_m cos(rake)``, ``kayma_m sin(rake)``, ``acilma_m``.

    The rake convention of ``knotenlinie.defter.geometri.fay_vektorleri``: rake 0 is
    left-lateral strike slip (``U1``), rake 90 reverse dip slip (``U2``), and ``U3`` is the
    optional opening ``acilma_m`` (default 0).
    """
    kayma = float(kaynak["kayma_m"])
    rake = np.deg2rad(float(kaynak["kayma_deg"]))
    return kayma * np.cos(rake), kayma * np.sin(rake), float(kaynak.get("acilma_m", 0.0))


def okada_ned(*, kaynak, alici_lat, alici_lon, alici_derinlik_m, R=6371000.0):
    """Channel-facing Okada call: a source mapping -> NED Voigt stress ``(N, 6)`` Pa.

    ``kaynak`` carries exactly ``dogrultu_deg, egim_deg, kayma_deg, uzunluk_m,
    genislik_m, ust_derinlik_m, kayma_m, kaynak_lat, kaynak_lon`` (plus optional
    ``acilma_m``, default 0).  ``(kaynak_lat, kaynak_lon)`` is the horizontal position of
    the rectangle's centre (mid-length, mid-width).  The slip components are
    ``U1 = kayma_m cos(rake)``, ``U2 = kayma_m sin(rake)`` and ``U3 = acilma_m``, the
    convention of ``knotenlinie.defter.geometri.fay_vektorleri`` (rake 0 left-lateral, rake 90
    reverse).

    **Receiver mapping (2.1.0).**  Receivers are projected with ``cerceve.aeqd_metre``:
    azimuthal equidistant about the source centre, which keeps the great-circle distance
    and the azimuth from the source exactly at every range (the equirectangular
    ``ned_metre`` used before was off by up to 86 km at 1000 km).  The projected point is
    rotated by the strike about the vertical (``yerel_cerceve(strike, 0)``) into the frame
    of ``okada_yerel``, the stress is ``cerceve.dud_gerilme`` of the gradient, and it is
    rotated back to the source grid by ``yerelden_nede``.  The result is then rotated about
    the vertical by ``+gamma`` (``cerceve.yakinsama_rad``) into the receiver's own local NED,
    which is what the ledger's NED columns mean.  With ``gamma = (beta + pi) - alpha`` a
    direction at grid azimuth ``theta`` has local azimuth ``theta + gamma``, so the receiver's
    local north lies at grid azimuth ``-gamma``; writing the local basis in grid components
    (``lN = (cos gamma, -sin gamma)``, ``lE = (sin gamma, cos gamma)``) gives the component map
    ``v_local = R(+gamma) v_grid`` and ``sigma_local = R(+gamma) sigma_grid R(+gamma)^T`` with
    ``R(g) = [[cos g, -sin g, 0], [sin g, cos g, 0], [0, 0, 1]]``.  A receiver on the source
    meridian has ``gamma = 0`` and is unchanged.  The sign is derived from the frames, not from
    PSCMP: the PSCMP sphere-check fixture confirms it only through frame-independent quantities (the four
    rotation invariants about the vertical match PSCMP to 0.30 Pa, and PSCMP's own horizontal
    axes sit ``2 gamma`` away from local NED, ``PSCMP = R(-2 gamma)`` local to 0.44 Pa); the
    six-component comparison in the receiver's local NED is not what PSCMP reports.  The
    mapping keeps distances and azimuths from the source exactly; it does not make the flat
    half-space spherical.

    The return is the writer's ``s_xx_Pa … s_yz_Pa`` order, Pa, tension positive; ``(N, 6)``
    for array receivers and ``(6,)`` for scalar receivers.
    """
    from .cerceve import (aeqd_metre, dud_gerilme, matris_voigt, voigt_matris,
                          yakinsama_rad, yerel_cerceve, yerelden_nede)

    k = kaynak_dogrula(kaynak)
    if np.any(np.asarray(alici_derinlik_m, dtype=np.float64) < 0.0):
        raise ValueError("alici_derinlik_m < 0: the receiver is above the free surface")
    tek = np.ndim(alici_lat) == 0 and np.ndim(alici_lon) == 0 and np.ndim(alici_derinlik_m) == 0
    lat, lon, derinlik = np.broadcast_arrays(
        np.atleast_1d(np.asarray(alici_lat, dtype=np.float64)),
        np.atleast_1d(np.asarray(alici_lon, dtype=np.float64)),
        np.atleast_1d(np.asarray(alici_derinlik_m, dtype=np.float64)))
    kuzey_m, dogu_m = aeqd_metre(lat, lon, lat0_deg=k["kaynak_lat"], lon0_deg=k["kaynak_lon"], R=R)
    dogrultu, egim = float(k["dogrultu_deg"]), float(k["egim_deg"])
    Rh = yerel_cerceve(dogrultu, 0.0)            # strike-only rotation: x strike, y right, z down
    ned = np.stack([kuzey_m, dogu_m, np.zeros_like(kuzey_m)], axis=-1)
    yerel = ned @ Rh.T
    L, W = float(k["uzunluk_m"]), float(k["genislik_m"])
    x = yerel[..., 0]
    y = yerel[..., 1] + 0.5 * W * np.cos(np.deg2rad(egim))
    U1, U2, U3 = kayma_bilesenleri(k)
    _, dud = okada_yerel(x, y, derinlik, L=L, W=W, ust_derinlik=float(k["ust_derinlik_m"]),
                         U1=U1, U2=U2, U3=U3, egim_deg=egim)
    sigma = yerelden_nede(dud_gerilme(dud), dogrultu, 0.0)
    # 2.1.0: from the source grid into the receiver's local NED (R(+gamma)).
    gamma = yakinsama_rad(lat, lon, lat0_deg=k["kaynak_lat"], lon0_deg=k["kaynak_lon"])
    cg, sg = np.cos(gamma), np.sin(gamma)
    Rz = np.zeros(sigma.shape[:-1] + (3, 3), dtype=np.float64)
    Rz[..., 0, 0] = cg
    Rz[..., 0, 1] = -sg
    Rz[..., 1, 0] = sg
    Rz[..., 1, 1] = cg
    Rz[..., 2, 2] = 1.0
    sigma = matris_voigt(Rz @ voigt_matris(sigma) @ np.swapaxes(Rz, -1, -2))
    return sigma[0] if tek else sigma
