"""okada_ned on the sphere (2.1.0): azimuthal-equidistant mapping and receiver-NED tensor.

The fixture ``pscmp_ka2_anlik.json`` is PSCMP's own output for the sphere check (44 receivers 27-1034 km,
frozen revision of the check).  The receiver mapping is azimuthal equidistant (``cerceve.aeqd_metre``)
and the tensor is rotated into the receiver's true local NED by the grid convergence
(``cerceve.yakinsama_rad``, ``gamma = (beta + pi) - alpha``), ``sigma_local = R(+gamma)
sigma_grid R(+gamma)^T``: a direction at grid azimuth ``theta`` has local azimuth ``theta +
gamma``, so the receiver's local north lies at grid azimuth ``-gamma``.  The equirectangular
grid used before 2.1.0 missed PSCMP by 606 Pa.  PSCMP's own horizontal axes are ``2 gamma`` from
local NED, so its six components are matched only after ``R(-2 gamma)``; the four rotation
invariants about the vertical are frame-free and match to 0.30 Pa.
"""
import json
from pathlib import Path

import numpy as np
import pytest

from knotenlinie.elastik.cerceve import (
    aeqd_metre, dud_gerilme, matris_voigt, ned_metre, voigt_matris, yakinsama_rad,
    yerel_cerceve, yerelden_nede,
)
from knotenlinie.elastik.okada import kayma_bilesenleri, okada_ned, okada_yerel

_R = 6371000.0
_FIKSTUR = Path(__file__).with_name("pscmp_ka2_anlik.json")
#: A surface fault in the fixture's range, used by the frame tests.
_DOGRU = {
    "dogrultu_deg": 155.0, "egim_deg": 45.0, "kayma_deg": -90.0,
    "uzunluk_m": 15000.0, "genislik_m": 12000.0, "ust_derinlik_m": 2000.0,
    "kayma_m": 1.0, "kaynak_lat": 42.5, "kaynak_lon": 13.2,
}
#: A representative vertical tensile crack (opening only), a case for the tensile branch of the kernel.
_CATLAK = {
    "dogrultu_deg": 315.0, "egim_deg": 90.0, "kayma_deg": 0.0, "uzunluk_m": 10000.0,
    "genislik_m": 3500.0, "ust_derinlik_m": 0.0, "kayma_m": 0.0, "kaynak_lat": 40.8,
    "kaynak_lon": 15.3, "acilma_m": 1.0,
}


# --- helpers --------------------------------------------------------------------------------

def _fixture():
    d = json.loads(_FIKSTUR.read_text(encoding="utf-8"))
    lat = np.asarray(d["alici_lat"], dtype=np.float64)
    lon = np.asarray(d["alici_lon"], dtype=np.float64)
    z = np.full(lat.size, float(d["derinlik_m"]))
    return d, lat, lon, z


def _fixture_sirasi(sigma):
    """okada_ned's Voigt (nn, ee, dd, ne, nd, ed) -> PSCMP's (nn, ee, dd, ne, ed, dn)."""
    return sigma[:, [0, 1, 2, 3, 5, 4]]


def _invaryantlar(v):
    """PSCMP order (nn, ee, dd, ne, ed, dn) -> the four vertical-rotation invariants (N, 4).

    ``(dd, hypot(ed, dn), (nn+ee)/2, hypot((nn-ee)/2, ne))``: none moves under a rotation of the
    horizontal axes about the vertical.
    """
    nn, ee, dd, ne, ed, dn = (v[..., i] for i in range(6))
    return np.stack([dd, np.hypot(ed, dn), 0.5 * (nn + ee), np.hypot(0.5 * (nn - ee), ne)], axis=-1)


def _dondur_pscmp(v, g):
    """Rotate a Voigt NED stress by ``g`` about the vertical and return PSCMP's component order."""
    m = voigt_matris(v)
    c, s = np.cos(g), np.sin(g)
    R = np.zeros(v.shape[:-1] + (3, 3), dtype=np.float64)
    R[..., 0, 0] = c
    R[..., 0, 1] = -s
    R[..., 1, 0] = s
    R[..., 1, 1] = c
    R[..., 2, 2] = 1.0
    return matris_voigt(R @ m @ np.swapaxes(R, -1, -2))[:, [0, 1, 2, 3, 5, 4]]


def _grid_aeqd(k, lat, lon, z):
    """Source-grid NED tensor: ``aeqd_metre`` + strike + ``okada_yerel`` + ``yerelden_nede``."""
    n, e = aeqd_metre(lat, lon, lat0_deg=k["kaynak_lat"], lon0_deg=k["kaynak_lon"])
    Rh = yerel_cerceve(k["dogrultu_deg"], 0.0)
    yerl = np.stack([n, e, np.zeros_like(n)], axis=-1) @ Rh.T
    x = yerl[..., 0]
    y = yerl[..., 1] + 0.5 * k["genislik_m"] * np.cos(np.deg2rad(k["egim_deg"]))
    U1, U2, U3 = kayma_bilesenleri(k)
    _, dud = okada_yerel(x, y, z, L=k["uzunluk_m"], W=k["genislik_m"], ust_derinlik=k["ust_derinlik_m"],
                         U1=U1, U2=U2, U3=U3, egim_deg=k["egim_deg"])
    return yerelden_nede(dud_gerilme(dud), k["dogrultu_deg"], 0.0)


def _eski(k, lat, lon, z):
    """The 2.0.0 mapping: ``ned_metre`` (equirectangular), no receiver-NED rotation."""
    n, e = ned_metre(lat, lon, lat0_deg=k["kaynak_lat"], lon0_deg=k["kaynak_lon"])
    Rh = yerel_cerceve(k["dogrultu_deg"], 0.0)
    yerl = np.stack([n, e, np.zeros_like(n)], axis=-1) @ Rh.T
    x = yerl[..., 0]
    y = yerl[..., 1] + 0.5 * k["genislik_m"] * np.cos(np.deg2rad(k["egim_deg"]))
    U1, U2, U3 = kayma_bilesenleri(k)
    _, dud = okada_yerel(x, y, z, L=k["uzunluk_m"], W=k["genislik_m"], ust_derinlik=k["ust_derinlik_m"],
                         U1=U1, U2=U2, U3=U3, egim_deg=k["egim_deg"])
    return yerelden_nede(dud_gerilme(dud), k["dogrultu_deg"], 0.0)


def _jacobian(lat, lon, *, lat0_deg, lon0_deg, adim=1e-6):
    """AEQD Jacobian at the receivers: grid metres per radian of latitude / longitude.

    ``c_lat`` is the grid image of the receiver's local north, ``c_lon`` of its local east; the
    projection is not conformal, so the two are not orthogonal.  Computed from ``aeqd_metre``
    alone, so the physical tests below do not use ``yakinsama_rad``.
    """
    lat = np.asarray(lat, dtype=np.float64)
    lon = np.asarray(lon, dtype=np.float64)
    e = np.rad2deg(adim)

    def q(la, lo):
        n, ea = aeqd_metre(la, lo, lat0_deg=lat0_deg, lon0_deg=lon0_deg)
        return np.stack([n, ea], axis=-1)

    return ((q(lat + e, lon) - q(lat - e, lon)) / (2.0 * adim),
            (q(lat, lon + e) - q(lat, lon - e)) / (2.0 * adim))


def _yerel_eksenler(lat, lon, *, lat0_deg, lon0_deg):
    """Receiver local north/east unit vectors in grid components, from ``aeqd_metre``."""
    c_lat, c_lon = _jacobian(lat, lon, lat0_deg=lat0_deg, lon0_deg=lon0_deg)
    return (c_lat / np.linalg.norm(c_lat, axis=-1, keepdims=True),
            c_lon / np.linalg.norm(c_lon, axis=-1, keepdims=True))


def _kapat(a):
    return (a + np.pi) % (2.0 * np.pi) - np.pi


# --- the PSCMP fixture ----------------------------------------------------------------------

def test_ka2b_invaryantlar_pscmp_ile_uyusur():
    """The four rotation invariants about the vertical match PSCMP (ies1, ies0) within 2.0 Pa.

    Observed 0.30 Pa.  These are frame-free: they do not use PSCMP's horizontal convention.
    """
    d, lat, lon, z = _fixture()
    bizim = _invaryantlar(_fixture_sirasi(okada_ned(kaynak=d["duzlem"], alici_lat=lat,
                                                     alici_lon=lon, alici_derinlik_m=z)))
    assert np.all(np.isfinite(bizim))
    assert np.abs(bizim).max() > 1e4                                  # a real field, not zeros
    for anahtar in ("ies1_Pa", "ies0_Pa"):
        fark = np.abs(_invaryantlar(np.asarray(d[anahtar], dtype=np.float64)) - bizim)
        assert fark.max() < 2.0, f"{anahtar}: {fark.max()} Pa"


def test_ka2b_cerceve_pscmp_cercevesi():
    """Characterization, not a gate: PSCMP's horizontal axes are ``2 gamma`` from local NED.

    ``PSCMP ~ R(-2 gamma) . our local NED`` within 2.0 Pa (observed 0.44 Pa).  This documents the
    convention gap; the gate is the frame-free invariants above.
    """
    d, lat, lon, z = _fixture()
    k = d["duzlem"]
    yerel = okada_ned(kaynak=k, alici_lat=lat, alici_lon=lon, alici_derinlik_m=z)
    gama = yakinsama_rad(lat, lon, lat0_deg=k["kaynak_lat"], lon0_deg=k["kaynak_lon"])
    ps = _dondur_pscmp(yerel, -2.0 * gama)
    for anahtar in ("ies1_Pa", "ies0_Pa"):
        fark = np.abs(np.asarray(d[anahtar], dtype=np.float64) - ps)
        assert fark.max() < 2.0, f"{anahtar}: {fark.max()} Pa"


# --- aeqd_metre known answers ---------------------------------------------------------------

def test_aeqd_meridyen_ve_ekvator():
    n, e = aeqd_metre(43.0, 13.0, lat0_deg=42.0, lon0_deg=13.0)
    assert e == pytest.approx(0.0, abs=1e-9)
    assert n == pytest.approx(_R * np.deg2rad(1.0), rel=1e-14)
    n, e = aeqd_metre(0.0, 90.0, lat0_deg=0.0, lon0_deg=0.0)
    assert n == pytest.approx(0.0, abs=1e-6)
    assert e == pytest.approx(np.pi * _R / 2.0, rel=1e-15)           # azimuth 90 degrees


def test_aeqd_kutup_ve_merkez():
    n, e = aeqd_metre(90.0, 0.0, lat0_deg=0.0, lon0_deg=0.0)
    assert n == pytest.approx(np.pi * _R / 2.0, rel=1e-14)
    assert e == pytest.approx(0.0, abs=1e-6)
    assert aeqd_metre(42.0, 13.0, lat0_deg=42.0, lon0_deg=13.0) == (0.0, 0.0)


def test_aeqd_ned_metre_meridyende_ozdes():
    """Within 10 km along the centre meridian, aeqd_metre and ned_metre agree to 1e-5 of d.

    The meridian is where the two projections coincide; off it the equirectangular grid is
    off by ``O(tan(lat) dlat)`` (~8e-4 of d at 10 km, 42 N), which is why ``okada_ned`` moved.
    """
    lat0, lon0 = 42.0, 13.0
    lat = lat0 + np.linspace(-0.08, 0.08, 21)
    lon = np.full_like(lat, lon0)
    an, ae = aeqd_metre(lat, lon, lat0_deg=lat0, lon0_deg=lon0)
    en, ee = ned_metre(lat, lon, lat0_deg=lat0, lon0_deg=lon0)
    d = np.hypot(an, ae)
    assert d.max() <= 10_000.0
    assert np.hypot(an - en, ae - ee).max() <= 1e-5 * d.max()


def test_aeqd_antimeridyen():
    """A receiver across 180 E is the small separation: it equals the same point written > 180."""
    a = aeqd_metre(42.0, -179.9, lat0_deg=42.0, lon0_deg=179.9)     # 0.2 deg east, across the seam
    b = aeqd_metre(42.0, 180.1, lat0_deg=42.0, lon0_deg=179.9)      # the same point, lon > 180
    assert a == b
    assert np.hypot(*a) == pytest.approx(_R * np.deg2rad(0.2) * np.cos(np.deg2rad(42.0)), rel=1e-3)


def test_aeqd_guney_yarimkure():
    """The projection is hemisphere-symmetric: a mirror in latitude mirrors north and gamma."""
    kuzey = aeqd_metre(42.5, 14.0, lat0_deg=42.0, lon0_deg=13.0)
    guney = aeqd_metre(-42.5, 14.0, lat0_deg=-42.0, lon0_deg=13.0)
    assert kuzey[0] == pytest.approx(-guney[0], rel=1e-12)          # north is mirrored
    assert kuzey[1] == pytest.approx(guney[1], rel=1e-12)           # east is not
    assert yakinsama_rad(42.0, 14.0, lat0_deg=42.0, lon0_deg=13.0) == \
        pytest.approx(-yakinsama_rad(-42.0, 14.0, lat0_deg=-42.0, lon0_deg=13.0), rel=1e-12)
    assert yakinsama_rad(42.0, 0.5, lat0_deg=42.0, lon0_deg=0.0) > 0.0
    assert yakinsama_rad(-42.0, 0.5, lat0_deg=-42.0, lon0_deg=0.0) < 0.0


def test_aeqd_kutup_alici_ve_merkez():
    """A pole receiver or a pole centre is a regular point: finite, with the right distance."""
    n, e = aeqd_metre(89.999, 37.0, lat0_deg=89.0, lon0_deg=0.0)
    assert np.isfinite(n) and np.isfinite(e) and np.hypot(n, e) > 0.0
    n, e = aeqd_metre(80.0, 130.0, lat0_deg=90.0, lon0_deg=0.0)     # 10 deg from the pole
    assert np.hypot(n, e) == pytest.approx(_R * np.deg2rad(10.0), rel=1e-12)


def test_aeqd_antipot_azimut_tanimsiz():
    """At the exact antipode the azimuth is undefined; ``aeqd_metre`` still returns finite values.

    We document the undefined azimuth and do not invent a refusal: the distance is ``pi R`` and
    the returned azimuth (from ``atan2(0, 0)``) carries no information.  ``okada_ned`` does not
    raise there either; the far-field tensor is finite.
    """
    n, e = aeqd_metre(0.0, 180.0, lat0_deg=0.0, lon0_deg=0.0)
    assert np.isfinite(n) and np.isfinite(e)
    assert np.hypot(n, e) == pytest.approx(np.pi * _R, rel=1e-12)
    k = {"dogrultu_deg": 0.0, "egim_deg": 90.0, "kayma_deg": 0.0, "uzunluk_m": 1000.0,
         "genislik_m": 1000.0, "ust_derinlik_m": 1000.0, "kayma_m": 0.0, "kaynak_lat": 0.0,
         "kaynak_lon": 0.0, "acilma_m": 1.0}
    s = okada_ned(kaynak=k, alici_lat=0.0, alici_lon=180.0, alici_derinlik_m=0.0)
    assert s.shape == (6,) and np.all(np.isfinite(s))


# --- yakinsama_rad known answers ------------------------------------------------------------

def test_yakinsama_sifir_ekvator_ve_meridyen():
    assert yakinsama_rad(0.0, 5.0, lat0_deg=0.0, lon0_deg=0.0) == pytest.approx(0.0, abs=1e-15)
    assert yakinsama_rad(42.5, 13.0, lat0_deg=42.0, lon0_deg=13.0) == pytest.approx(0.0, abs=1e-15)
    assert yakinsama_rad(41.5, 13.0, lat0_deg=42.0, lon0_deg=13.0) == pytest.approx(0.0, abs=1e-15)


def test_yakinsama_merkez_sifir():
    assert yakinsama_rad(42.0, 13.0, lat0_deg=42.0, lon0_deg=13.0) == 0.0


def test_yakinsama_antisimetrik():
    a = yakinsama_rad(43.0, 14.0, lat0_deg=42.0, lon0_deg=13.0)
    b = yakinsama_rad(43.0, 12.0, lat0_deg=42.0, lon0_deg=13.0)
    assert a == pytest.approx(-b, rel=1e-12)


def test_yakinsama_kucuk_delta_lambda():
    phi, dlam = 60.0, 1e-3
    g = yakinsama_rad(phi, dlam, lat0_deg=phi, lon0_deg=0.0)
    beklenen = np.deg2rad(dlam) * np.sin(np.deg2rad(phi))
    assert np.sign(g) == np.sign(beklenen)
    assert abs(g) == pytest.approx(abs(beklenen), rel=1e-3)


# --- the receiver-NED rotation (independent physical tests) ---------------------------------

def test_yerel_cerceve_izdusumu_okada_ned_ile_uyusur():
    """``okada_ned``'s nn, ee, ne are the grid tensor projected on the receiver's own north/east.

    The local basis is finite differences of ``aeqd_metre`` alone (no PSCMP, no
    ``yakinsama_rad``).  For receivers 0.001 deg (~110 m) due east, due west and north-east the
    AEQD chart's non-conformality is below 1e-9, so this pins the rotation sign and frame.
    """
    k = dict(_DOGRU)
    adim = 0.001
    coslat = np.cos(np.deg2rad(k["kaynak_lat"]))
    lat = np.array([k["kaynak_lat"], k["kaynak_lat"], k["kaynak_lat"] + adim])
    lon = np.array([k["kaynak_lon"] + adim / coslat, k["kaynak_lon"] - adim / coslat,
                    k["kaynak_lon"] + adim / coslat])
    z = np.array([3000.0, 3000.0, 3000.0])
    n_hat, e_hat = _yerel_eksenler(lat, lon, lat0_deg=k["kaynak_lat"], lon0_deg=k["kaynak_lon"])
    m = voigt_matris(_grid_aeqd(k, lat, lon, z))
    n3 = np.concatenate([n_hat, np.zeros((lat.size, 1))], axis=1)
    e3 = np.concatenate([e_hat, np.zeros((lat.size, 1))], axis=1)
    nn = np.einsum("ni,nij,nj->n", n3, m, n3)
    ee = np.einsum("ni,nij,nj->n", e3, m, e3)
    ne = np.einsum("ni,nij,nj->n", n3, m, e3)
    yeni = okada_ned(kaynak=k, alici_lat=lat, alici_lon=lon, alici_derinlik_m=z)
    olcek = np.abs(yeni).max()
    assert np.abs(yeni[:, 0] - nn).max() <= 1e-9 * olcek
    assert np.abs(yeni[:, 1] - ee).max() <= 1e-9 * olcek
    assert np.abs(yeni[:, 3] - ne).max() <= 1e-9 * olcek


def test_radyal_dogrultu_yerel_azimuta_kayar():
    """A direction at grid azimuth alpha maps to local azimuth ``alpha + gamma``.

    The local azimuth comes from the AEQD Jacobian of ``aeqd_metre`` (finite differences), so this
    is independent of the rotation under test; the source-to-receiver geodesic is the grid-radial
    direction.
    """
    k = dict(_DOGRU)
    lat0, lon0 = k["kaynak_lat"], k["kaynak_lon"]
    adim = 0.001
    coslat = np.cos(np.deg2rad(lat0))
    lat = np.array([lat0 + adim, lat0, lat0 - adim])
    lon = np.array([lon0, lon0 + adim / coslat, lon0 - adim / coslat])
    n, e = aeqd_metre(lat, lon, lat0_deg=lat0, lon0_deg=lon0)
    alpha = np.arctan2(e, n)
    gama = yakinsama_rad(lat, lon, lat0_deg=lat0, lon0_deg=lon0)
    c_lat, c_lon = _jacobian(lat, lon, lat0_deg=lat0, lon0_deg=lon0)
    v_n = c_lat / _R
    v_e = c_lon / (_R * np.cos(np.deg2rad(lat))[:, None])
    u = np.stack([np.cos(alpha), np.sin(alpha)], axis=-1)
    det = v_n[:, 0] * v_e[:, 1] - v_n[:, 1] * v_e[:, 0]
    p_n = (u[:, 0] * v_e[:, 1] - u[:, 1] * v_e[:, 0]) / det
    p_e = (v_n[:, 0] * u[:, 1] - v_n[:, 1] * u[:, 0]) / det
    yerel_az = np.arctan2(p_e, p_n)
    assert np.abs(_kapat(yerel_az - (alpha + gama))).max() < 1e-9


def test_donus_izi_ve_ikinci_invariant_korur():
    """The rotation is a rigid rotation: trace and second invariant survive, dd does not move."""
    d, lat, lon, z = _fixture()
    grid = _grid_aeqd(d["duzlem"], lat, lon, z)
    yeni = okada_ned(kaynak=d["duzlem"], alici_lat=lat, alici_lon=lon, alici_derinlik_m=z)
    iz = np.abs((grid[:, 0] + grid[:, 1] + grid[:, 2]) - (yeni[:, 0] + yeni[:, 1] + yeni[:, 2]))
    assert (iz / np.abs(grid[:, [0, 1, 2]]).max(axis=1)).max() < 1e-12
    assert np.allclose(grid[:, 2], yeni[:, 2], rtol=1e-12, atol=0.0)

    def _I2(v):
        return (v[:, 0] * v[:, 1] + v[:, 1] * v[:, 2] + v[:, 2] * v[:, 0]
                - v[:, 3] ** 2 - v[:, 4] ** 2 - v[:, 5] ** 2)

    assert (np.abs(_I2(grid) - _I2(yeni)) / np.abs(_I2(grid))).max() < 1e-12


def test_donus_gamma_sifirken_ozdeslik():
    """On the source meridian gamma = 0: the 2.1.0 mapping is the unrotated grid tensor."""
    k = dict(_DOGRU)
    lat = np.array([k["kaynak_lat"] + 0.02, k["kaynak_lat"] - 0.02])
    lon = np.array([k["kaynak_lon"], k["kaynak_lon"]])
    z = np.array([3000.0, 6000.0])
    assert np.array_equal(yakinsama_rad(lat, lon, lat0_deg=k["kaynak_lat"], lon0_deg=k["kaynak_lon"]),
                          np.zeros(2))
    grid = _grid_aeqd(k, lat, lon, z)
    yeni = okada_ned(kaynak=k, alici_lat=lat, alici_lon=lon, alici_derinlik_m=z)
    assert np.allclose(grid, yeni, rtol=1e-13, atol=0.0)


# --- short-range continuity and the off-meridian bound --------------------------------------

def test_ikikm_disi_degisim_siniri():
    """Within 2 km off the meridian the 2.1.0 - 2.0.0 change is rotation + position bounded.

    ``new - old = [R(+g) - I] sigma_grid(p_aeqd) + [sigma_grid(p_aeqd) - sigma_grid(p_ned)]``, so
    ``|new - old| <= 2|g| max|sigma| + |sigma_grid(p_aeqd) - sigma_grid(p_ned)|``.  The first term
    is the rotation term, the second the position term (the AEQD-equirectangular offset is
    ``O(tan(lat) d^2 / R)``, <= ~0.6 m at 2 km).
    """
    k = dict(_DOGRU)
    lat0, lon0 = k["kaynak_lat"], k["kaynak_lon"]
    off = np.linspace(-0.018, 0.018, 7)              # ~2 km
    koord = [(a, b / np.cos(np.deg2rad(lat0))) for a in off for b in off]
    lat = np.array([lat0 + a for a, _ in koord])
    lon = np.array([lon0 + b for _, b in koord])
    z = np.full(lat.size, 3000.0)
    yeni = okada_ned(kaynak=k, alici_lat=lat, alici_lon=lon, alici_derinlik_m=z)
    eski = _eski(k, lat, lon, z)
    grid_aeqd = _grid_aeqd(k, lat, lon, z)
    gama = yakinsama_rad(lat, lon, lat0_deg=lat0, lon0_deg=lon0)
    rotasyon = 2.0 * np.abs(gama) * np.abs(grid_aeqd).max(axis=1)
    konum = np.abs(grid_aeqd - eski).max(axis=1)
    degisim = np.abs(yeni - eski).max(axis=1)
    assert np.all(degisim <= rotasyon + konum)


def test_kisa_mesafe_catlak_meridyeni_degismez():
    """Near the tensile-crack source ``_CATLAK`` and on its meridian (gamma = 0), 2.1.0 is 2.0.0.

    The comparison is the old equirectangular, unrotated mapping rebuilt from ``ned_metre``;
    within 5 km of the centre and on the meridian it holds to 1e-4 of each receiver's largest
    component (actually ~1e-13).  A disk around the source is not covered: off the meridian the
    convergence rotation is the intended 2.1.0 correction; ``test_ikikm_disi_degisim_siniri``
    bounds it there.
    """
    k = _CATLAK
    off = np.concatenate([np.linspace(0.005, 0.04, 8), -np.linspace(0.005, 0.04, 8)])
    lat = k["kaynak_lat"] + off            # 0.5-4.5 km on the meridian, never the fault centre
    lon = np.full_like(lat, k["kaynak_lon"])
    z = np.full(lat.size, 1000.0)
    yeni = okada_ned(kaynak=k, alici_lat=lat, alici_lon=lon, alici_derinlik_m=z)
    eski = _eski(k, lat, lon, z)
    for i in range(lat.size):
        assert np.abs(yeni[i] - eski[i]).max() <= 1e-4 * np.abs(yeni[i]).max()
