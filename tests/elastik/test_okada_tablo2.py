"""Okada 1985 Table 2 ("Checklist for numerical calculations") against ``okada_yerel``.

The printed values are the manual transcription in ``okada1985_tablo2.py`` (four
significant figures, λ = μ, receiver on the free surface).  The pass rule is that module's
``eslesir``, as written and never loosened: the computed value rounds to the printed one,
and a printed 0 is zero to 1e-12 of the case's largest printed magnitude.

Cases 2-4 are finite rectangles and are the gate: 3 slip types x 9 columns x 3 cases = 81
values.  Case 1 is a point source, which is not part of the interface; the small-rectangle
limit is a derived, non-gating check.

``okada1985_den_yerel`` is the one place Okada 1985's geometry (x, y, d, delta, L, W with
z up, the reference corner at depth d on the LOWER edge, Fig. 1 of the 1985 paper and
Figs. 3-4 of the 1992 paper) is mapped to ``okada_yerel``'s frame; it is tested separately
below with hand-computed numbers.
"""
import math

import numpy as np
import pytest

from knotenlinie.elastik.okada import okada_yerel
from tests.elastik import okada1985_tablo2 as T

_TURLER = ("strike", "dip", "tensile")
_S = np.array([1.0, -1.0, -1.0])   # okada_yerel's (x, y right, z down) -> Okada's (x, y left, z up)


def okada1985_den_yerel(x, y, d, delta_deg, L, W):
    """Map Okada 1985's source geometry and receiver ``(x, y)`` on ``z = 0`` to ``okada_yerel``.

    Returns ``(x, y, z, kw, isaret)``: the receiver in ``okada_yerel``'s frame, the keyword
    arguments ``L, W, ust_derinlik, egim_deg``, and ``isaret = (s1, s2, s3)``, the factors that
    turn Okada's unit ``U1, U2, U3`` into ``okada_yerel``'s.

    * ``delta > 0``: the reference corner is on the lower edge at depth ``d``, so the upper edge
      is at ``d - W sin(delta)``; the frame is rotated by 180 degrees about the strike axis and
      centred on mid-length: ``x = x_O - L/2``, ``y = W cos(delta) - y_O``; the slips map
      unchanged.
    * ``delta = -90``: the rectangle runs down from the reference at depth ``d`` (its "up-dip"
      axis points down), i.e. the vertical plane with its upper edge at ``d``.  The slip of
      Okada's convention (the jump ``u(+) - u(-)`` with ``+`` the side of
      ``nu = (0, -sin(delta), cos(delta))``) maps to ``okada_yerel`` as ``(-U1, +U2, +U3)``:
      the ``+`` side is ``y_O > 0`` instead of ``y_O < 0``, so the strike jump flips, while the
      dip jump ``(0, 0, -U2)`` along the downward axis and the opening ``U3 nu`` are the same
      physical motions.
    """
    if delta_deg == -90.0:
        return x - 0.5 * L, -y, 0.0, dict(L=L, W=W, ust_derinlik=d, egim_deg=90.0), (-1.0, 1.0, 1.0)
    if 0.0 < delta_deg <= 90.0:
        dr = math.radians(delta_deg)
        kw = dict(L=L, W=W, ust_derinlik=d - W * math.sin(dr), egim_deg=delta_deg)
        return x - 0.5 * L, W * math.cos(dr) - y, 0.0, kw, (1.0, 1.0, 1.0)
    raise ValueError(f"delta {delta_deg} is not mapped (0 < delta <= 90 or delta = -90)")


def _dokuz_deger(g, tur):
    """The nine printed-column values at the case's receiver, in Okada's frame, for unit slip."""
    x, y, z, kw, isaret = okada1985_den_yerel(g["x"], g["y"], g["d"], g["delta_deg"], g["L"], g["W"])
    k = _TURLER.index(tur)
    U = [0.0, 0.0, 0.0]
    U[k] = isaret[k]
    u, dud = okada_yerel(np.array([x]), np.array([y]), np.array([z]), U1=U[0], U2=U[1], U3=U[2], **kw)
    uo = u[0] * _S
    do = dud[0] * _S[:, None] * _S[None, :]
    return [uo[0], uo[1], uo[2], do[0, 0], do[0, 1], do[1, 0], do[1, 1], do[2, 0], do[2, 1]]


def _olcek(vaka):
    return max(abs(float(s)) for sl in T.TABLO[vaka].values() for s in sl)


# ---- the helper, tested by itself (hand-computed) ----

def test_yardimci_dogru_eksen_ve_derinlik():
    s70, c70 = math.sin(math.radians(70.0)), math.cos(math.radians(70.0))
    x, y, z, kw, isaret = okada1985_den_yerel(2.0, 3.0, 4.0, 70.0, 3.0, 2.0)
    assert x == pytest.approx(2.0 - 1.5, abs=1e-15)
    assert y == pytest.approx(2.0 * c70 - 3.0, abs=1e-15)
    assert z == 0.0
    assert kw["ust_derinlik"] == pytest.approx(4.0 - 2.0 * s70, abs=1e-15)
    assert (kw["L"], kw["W"], kw["egim_deg"]) == (3.0, 2.0, 70.0)
    assert isaret == (1.0, 1.0, 1.0)


def test_yardimci_dikey_ve_eksi_doksan():
    x, y, z, kw, isaret = okada1985_den_yerel(0.0, 0.0, 4.0, 90.0, 3.0, 2.0)
    assert (x, y, z) == (-1.5, 0.0 * 0.0 + 2.0 * math.cos(math.radians(90.0)), 0.0)
    assert kw["ust_derinlik"] == pytest.approx(2.0, abs=1e-15)      # 4 - 2 sin 90
    assert isaret == (1.0, 1.0, 1.0)
    x, y, z, kw, isaret = okada1985_den_yerel(0.0, 1.0, 4.0, -90.0, 3.0, 2.0)
    assert (x, y, z) == (-1.5, -1.0, 0.0)
    assert kw["ust_derinlik"] == 4.0                                # the reference is the UPPER edge
    assert kw["egim_deg"] == 90.0
    assert isaret == (-1.0, 1.0, 1.0)


def test_yardimci_taninmayan_egim():
    with pytest.raises(ValueError):
        okada1985_den_yerel(0.0, 0.0, 4.0, -45.0, 3.0, 2.0)


def test_yardimci_eksi_doksan_ayni_duzlem():
    """delta = -90 with slip (-U1, U2, U3) is the delta = 90 plane moved down by W: same physics.

    A vertical fault with its upper edge at 4 m (delta = -90, reference at 4 m) and one with
    delta = 90 whose reference is at 4 + W = 6 m (upper edge 4 m) are the same rectangle; their
    printed-convention fields agree with the sign map of the helper (U1 flips)."""
    g = dict(x=0.7, y=1.3, d=4.0, delta_deg=-90.0, L=3.0, W=2.0)
    for tur in _TURLER:
        a = _dokuz_deger(g, tur)
        h = dict(g, d=6.0, delta_deg=90.0)
        b = _dokuz_deger(h, tur)
        isr = 1.0 if tur != "strike" else -1.0
        assert a == pytest.approx([isr * v for v in b], rel=1e-9, abs=1e-12)


# ---- the gate: 81 finite-source values ----

@pytest.mark.parametrize("vaka", [2, 3, 4])
@pytest.mark.parametrize("tur", _TURLER)
def test_tablo2_sonlu_kaynak(vaka, tur):
    degerler = _dokuz_deger(T.GEOMETRI[vaka], tur)
    olcek = _olcek(vaka)
    basili = T.TABLO[vaka][tur]
    kotu = [(T.SUTUNLAR[i], degerler[i], basili[i]) for i in range(9) if not T.eslesir(degerler[i], basili[i], olcek)]
    assert not kotu, f"case {vaka} {tur}: computed vs printed {kotu}"


def test_tablo2_toplam_81():
    gecen = 0
    for vaka in (2, 3, 4):
        olcek = _olcek(vaka)
        for tur in _TURLER:
            d = _dokuz_deger(T.GEOMETRI[vaka], tur)
            gecen += sum(T.eslesir(d[i], T.TABLO[vaka][tur][i], olcek) for i in range(9))
    assert gecen == 81


# ---- case 1: the point source, a derived and non-gating check ----

def test_tablo2_nokta_kaynak_sinir_turetilmis():
    """Derived, non-gating (the point source is not part of the interface).

    A 1e-3 x 1e-3 rectangle divided by its area approaches Okada's point source (case 1, units
    of U dSigma); the strict pass rule does not apply, the stated agreement is rel 1e-3 on every
    printed value (the table's own rounding is 5e-4 at its smallest entry, hence the
    comparison against the printed numbers uses ``max(1e-3 relative, half a printed unit)``).
    """
    g = T.GEOMETRI[1]
    L = W = 1.0e-3
    dr = math.radians(g["delta_deg"])
    # the point sits at depth d = 4 below (0, 0): the rectangle is centred there
    for tur in _TURLER:
        k = _TURLER.index(tur)
        U = [0.0, 0.0, 0.0]
        U[k] = 1.0
        kw = dict(L=L, W=W, ust_derinlik=g["d"] - 0.5 * W * math.sin(dr), egim_deg=g["delta_deg"])
        y = 0.5 * W * math.cos(dr) - g["y"]
        u, dud = okada_yerel(np.array([g["x"]]), np.array([y]), np.array([0.0]), U1=U[0], U2=U[1], U3=U[2], **kw)
        uo = u[0] * _S / (L * W)
        do = dud[0] * _S[:, None] * _S[None, :] / (L * W)
        v = [uo[0], uo[1], uo[2], do[0, 0], do[0, 1], do[1, 0], do[1, 1], do[2, 0], do[2, 1]]
        for i in range(9):
            beklenen = float(T.TABLO[1][tur][i])
            assert abs(v[i] - beklenen) <= max(1e-3 * abs(beklenen), T.yarim_birim(T.TABLO[1][tur][i])), (
                tur, T.SUTUNLAR[i], v[i], beklenen)
