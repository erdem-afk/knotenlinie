"""Okada 1992 türetilmiş kontrolleri (i)-(vi).

The bodies are the mandatory derived checks (i)-(vi) of the kernel, with (iii), (iv) and (v) replaced in
place by review (no number widened); a kernel that fails any of them is not done.
"""
import numpy as np
import pytest

from knotenlinie.elastik.okada import okada_ned, okada_yerel


def _kaynak(strike, dip, U1, U2, U3, d=1000.0, L=10000.0, W=5000.0):
    return {
        "dogrultu_deg": strike, "egim_deg": dip, "kayma_deg": 0.0,
        "uzunluk_m": L, "genislik_m": W, "ust_derinlik_m": d,
        "kayma_m": 0.0, "acilma_m": 0.0,
        "kaynak_lat": 42.0, "kaynak_lon": 13.0,
    }


def test_i_serbest_yuzey_traksiyon_sifir():
    """(i) at a free surface the traction vanishes for every strike/dip and every case."""
    for strike in (0.0, 45.0, 90.0, 135.0):
        for dip in (10.0, 45.0, 90.0):
            for U1, U2, U3 in ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)):
                kaynak = _kaynak(strike, dip, U1, U2, U3)
                s = np.asarray(okada_ned(kaynak=kaynak, alici_lat=np.array([42.05, 41.95]),
                                         alici_lon=np.array([13.05, 12.95]),
                                         alici_derinlik_m=np.zeros(2)))
                # Voigt order (xx, yy, zz, xy, xz, yz); tension positive
                olcek = 30.0e9 * max(abs(U1), abs(U2), abs(U3))
                assert max(np.abs(s[..., 4]).max(), np.abs(s[..., 5]).max(), np.abs(s[..., 2]).max()) < 1e-9 * olcek


def test_ii_antiplane_iki_boyut_limiti():
    """(ii) a deep, long vertical strike-slip fault approaches the screw-dislocation field."""
    s, d = 1.0, 1000.0
    W, L = 1e5 * d, 1e4 * (1e5 * d)
    tablo = [
        (0.0, 3.1830988618379070e-04),
        (500.0, 2.5464790894703254e-04),
        (1000.0, 1.5915494309189535e-04),
        (5000.0, 1.2242687930145795e-05),
        (-1000.0, 1.5915494309189535e-04),
    ]
    for y, beklenen in tablo:
        u, dud = okada_yerel(np.array([0.0]), np.array([y]), np.array([0.0]),
                             L=L, W=W, ust_derinlik=d, U1=s, U2=0.0, U3=0.0, egim_deg=90.0)
        assert float(dud[0, 0, 1]) == pytest.approx(beklenen, rel=1e-3)
        assert float(dud[0, 0, 1]) > 0.0
        assert u[0, 1] == pytest.approx(0.0, abs=1e-12)
        assert u[0, 2] == pytest.approx(0.0, abs=1e-12)


def _s33(dud):
    from knotenlinie.elastik.cerceve import dud_gerilme, voigt_matris

    return voigt_matris(dud_gerilme(dud))


def test_iii_ayna_simetrisi():
    """(iii) Mirror parity under y -> -y.  Replaces the original draft of check (iii): reflecting y
    reverses a shear jump (left-lateral becomes right-lateral), so only the opening has the original list.

    With M = diag(1, -1, 1): shear sources (U1 or U2) obey ``u(-y) = -M u(y)`` and
    ``S(-y) = -M S M``; the opening (U3) obeys ``u(-y) = M u(y)`` and ``S(-y) = M S M``.
    Tolerances: 1e-9 |U| m for u and 1e-9 mu |U| for S.  Corollary on y = 0 (away from the fault
    rectangle): for U3, u2 = 0 and sigma_xy = sigma_yz = 0; for U1 and U2, u1 = u3 = 0 and
    sigma_xx = sigma_yy = sigma_zz = sigma_xz = 0.
    """
    M = np.diag([1.0, -1.0, 1.0])
    kw = dict(L=4000.0, W=3000.0, ust_derinlik=500.0, egim_deg=90.0)
    for (U1, U2, U3), s in (((1.0, 0.0, 0.0), -1.0), ((0.0, 1.0, 0.0), -1.0), ((0.0, 0.0, 1.0), 1.0)):
        amp = max(abs(U1), abs(U2), abs(U3))
        u, dud = okada_yerel(np.array([300.0]), np.array([700.0]), np.array([900.0]), U1=U1, U2=U2, U3=U3, **kw)
        u2, dud2 = okada_yerel(np.array([300.0]), np.array([-700.0]), np.array([900.0]), U1=U1, U2=U2, U3=U3, **kw)
        assert u2[0] == pytest.approx(s * (M @ u[0]), abs=1e-9 * amp)
        S1, S2 = _s33(dud)[0], _s33(dud2)[0]
        assert S2 == pytest.approx(s * (M @ S1 @ M), abs=1e-9 * 30.0e9 * amp)
        # y = 0 corollary
        u0, d0 = okada_yerel(np.array([3000.0]), np.array([0.0]), np.array([900.0]), U1=U1, U2=U2, U3=U3, **kw)
        S0 = _s33(d0)[0]
        atol = 1e-9 * 30.0e9 * amp
        if s > 0:
            assert u0[0, 1] == pytest.approx(0.0, abs=1e-9 * amp)
            assert S0[0, 1] == pytest.approx(0.0, abs=atol) and S0[1, 2] == pytest.approx(0.0, abs=atol)
        else:
            assert u0[0, 0] == pytest.approx(0.0, abs=1e-9 * amp) and u0[0, 2] == pytest.approx(0.0, abs=1e-9 * amp)
            for i, j in ((0, 0), (1, 1), (2, 2), (0, 2)):
                assert S0[i, j] == pytest.approx(0.0, abs=atol)


def test_iv_turevler_merkezi_fark():
    """(iv) Derivatives.  Replaces the original draft of check (iv): only the stencil changes, because the
    plain central difference's elementwise truncation error at this h is 9e-5 and cannot pass any correct kernel.

    rel 1e-6, h = 1e-3 max(L, W), the draft check's receiver, the three cases; the stencil is the Richardson
    extrapolation ``(4 D(h/2) - D(h)) / 3`` of the central difference ``D``.  Also the fingerprint that
    the plain central difference's error falls by 4 +- 0.1 when h is halved.
    """
    L, W = 4000.0, 3000.0
    h = 1e-3 * max(L, W)
    P = np.array([2500.0, 2200.0, 1300.0])
    for U in ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)):
        kw = dict(L=L, W=W, ust_derinlik=500.0, U1=U[0], U2=U[1], U3=U[2], egim_deg=90.0)
        _, dud = okada_yerel(P[0:1], P[1:2], P[2:3], **kw)

        def D(adim):
            cik = np.zeros((3, 3))
            for j in range(3):
                a, e = P.copy(), P.copy()
                a[j] += adim
                e[j] -= adim
                ua, _ = okada_yerel(a[0:1], a[1:2], a[2:3], **kw)
                ue, _ = okada_yerel(e[0:1], e[1:2], e[2:3], **kw)
                cik[:, j] = (ua[0] - ue[0]) / (2.0 * adim)
            return cik

        richardson = (4.0 * D(h / 2.0) - D(h)) / 3.0
        assert dud[0] == pytest.approx(richardson, rel=1e-6)
        e1 = np.abs(D(h) - dud[0]).max()
        e2 = np.abs(D(h / 2.0) - dud[0]).max()
        assert e1 / e2 == pytest.approx(4.0, abs=0.1)


def _iki_kaynak_isi(A, B, n=14):
    """Cross-work int_A [u_A] . (sigma_B nu_A) dS for two sources in a common frame (z down)."""
    from knotenlinie.elastik.cerceve import dud_gerilme, voigt_matris

    def Rz(th):
        c, s = np.cos(th), np.sin(th)
        return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])

    g, w = np.polynomial.legendre.leggauss(n)
    s_ = 0.5 * A["L"] * g
    t_ = 0.5 * A["W"] * (g + 1.0)
    S_, T_ = np.meshgrid(s_, t_, indexing="ij")
    WW = np.outer(0.5 * A["L"] * w, 0.5 * A["W"] * w).ravel()
    dl = np.deg2rad(A["dip"])
    sd, cd = np.sin(dl), np.cos(dl)
    loc = np.stack([S_.ravel(), T_.ravel() * cd, A["d"] + T_.ravel() * sd], axis=-1)   # A's own frame
    RA = Rz(A["th"])
    P = loc @ RA.T
    P[:, :2] += A["O"]
    nup = RA @ np.array([0.0, sd, -cd])
    updip = RA @ np.array([0.0, -cd, -sd])
    ex = RA @ np.array([1.0, 0.0, 0.0])
    salt = A["U"][0] * ex + A["U"][1] * updip + A["U"][2] * nup
    RB = Rz(B["th"])
    lb = (P - np.array([B["O"][0], B["O"][1], 0.0])) @ RB                      # into B's frame
    _, dud = okada_yerel(lb[:, 0], lb[:, 1], lb[:, 2], L=B["L"], W=B["W"], ust_derinlik=B["d"],
                         U1=B["U"][0], U2=B["U"][1], U3=B["U"][2], egim_deg=B["dip"])
    sig = RB @ voigt_matris(dud_gerilme(dud)) @ RB.T                              # (N, 3, 3) global
    t = sig @ nup
    return float(((t @ salt) * WW).sum())


def test_v_karsilikli_is_betti():
    """(v) Reciprocity.  Replaces the original draft of check (v): the single-point cross-work is not
    Betti's theorem, which needs the cross-work integrated over each source surface.

    ``int_A [u_A].(sigma_B nu_A) dS = int_B [u_B].(sigma_A nu_B) dS`` at rel 1e-6, 14 x 14 Gauss-Legendre points,
    on pairs with different dips, strikes, depths, offsets and slip components.
    """
    A = dict(L=4000.0, W=3000.0, d=500.0, dip=60.0, th=np.deg2rad(20.0), O=np.array([0.0, 0.0]), U=(1.0, 0.5, 0.2))
    Bler = (
        dict(L=5000.0, W=2000.0, d=1500.0, dip=35.0, th=np.deg2rad(75.0), O=np.array([14000.0, 9000.0]), U=(-0.7, 1.0, 0.4)),
        dict(L=5000.0, W=2000.0, d=1500.0, dip=90.0, th=np.deg2rad(-50.0), O=np.array([-9000.0, 6000.0]), U=(-0.7, 1.0, 0.4)),
        dict(L=5000.0, W=2000.0, d=1500.0, dip=12.0, th=np.deg2rad(160.0), O=np.array([-12000.0, -6000.0]), U=(0.3, -1.0, 0.4)),
    )
    for B in Bler:
        w_ab = _iki_kaynak_isi(A, B)
        w_ba = _iki_kaynak_isi(B, A)
        assert abs(w_ab) > 1e3
        assert w_ab == pytest.approx(w_ba, rel=1e-6)


def _uc_duzlemi_sureklilik(P, kw, eps=1e-3):
    """|value(P) - mean of the +-eps neighbours along x| for u and dud, relative to the point's own scale."""
    u0, d0 = okada_yerel(P[:, 0], P[:, 1], P[:, 2], **kw)
    ua, da = okada_yerel(P[:, 0] + eps, P[:, 1], P[:, 2], **kw)
    ue, de = okada_yerel(P[:, 0] - eps, P[:, 1], P[:, 2], **kw)
    assert np.isfinite(u0).all() and np.isfinite(d0).all()
    fu = np.abs(u0 - 0.5 * (ua + ue)).max(-1) / (np.abs(u0).max(-1) + 1e-30)
    fd = np.abs(d0 - 0.5 * (da + de)).max((-1, -2)) / (np.abs(d0).max((-1, -2)) + 1e-30)
    return fu.max(), fd.max()


def test_uc_duzlemi_ve_levha_uzantisi_sureklilik():
    """End-plane and edge-plane continuity: kills the mutants that remove the paper's branch rules (ii) and (iv).

    The field is continuous across the end planes x = +-L/2 away from the fault rectangle, so on them
    (xi = 0, rule ii) and on the fault plane extended below the lower edge (xi = q = 0, eta < 0, rule iv)
    the value equals the mean of the +-1e-3 m neighbours along x, to 1e-6 relative, with no NaN.
    """
    L, W, ust = 4000.0, 3000.0, 800.0
    rng = np.random.default_rng(5)
    for egim in (30.0, 60.0, 85.0, 89.0):
        dl = np.deg2rad(egim)
        ya, za = W * np.cos(dl), ust + W * np.sin(dl)
        for xe in (-0.5 * L, 0.5 * L):
            P = np.c_[np.full(200, xe), rng.uniform(-6000.0, 6000.0, 200), rng.uniform(0.0, 9000.0, 200)]
            # keep 50 m off the fault's end edge (the segment from the upper to the lower corner)
            t = np.clip(((P[:, 1]) * np.cos(dl) + (P[:, 2] - ust) * np.sin(dl)), 0.0, W)
            dist = np.hypot(P[:, 1] - t * np.cos(dl), P[:, 2] - ust - t * np.sin(dl))
            P = P[dist > 50.0]
            # rule (iv): the fault plane continued below the lower edge, at t = 300 and 1500 m
            ek = np.array([[xe, ya + tt * np.cos(dl), za + tt * np.sin(dl)] for tt in (300.0, 1500.0)])
            P = np.vstack([P, ek])
            for U in ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)):
                kw = dict(L=L, W=W, ust_derinlik=ust, U1=U[0], U2=U[1], U3=U[2], egim_deg=egim)
                fu, fd = _uc_duzlemi_sureklilik(P, kw)
                assert fu < 1e-6 and fd < 1e-6, (egim, xe, U, fu, fd)
def test_vi_sifir_kayma():
    """(vi) zero slip gives exactly zero u and dud."""
    u, dud = okada_yerel(np.array([100.0, 300.0]), np.array([200.0, -500.0]), np.array([50.0, 0.0]),
                         L=1000.0, W=800.0, ust_derinlik=100.0, U1=0.0, U2=0.0, U3=0.0, egim_deg=90.0)
    assert np.array_equal(u, np.zeros_like(u))
    assert np.array_equal(dud, np.zeros_like(dud))


# ---------------------------------------------------------------------------------------------
# Further checks written with the kernel.  Checks (iii), (iv) and (v) above are the
# reviewed versions, which replace the original draft checks.
# ---------------------------------------------------------------------------------------------

_LAME = 30.0e9


def _gerilme3(dud):
    from knotenlinie.elastik.cerceve import dud_gerilme, voigt_matris

    return voigt_matris(dud_gerilme(dud))


def test_denge_gerilme_diverjansi_sifir():
    """The stress field is in equilibrium: d sigma_ij / d x_j = 0 inside the medium (all cases, dip 45)."""
    P = np.array([2500.0, 2200.0, 1300.0])
    h = 4.0
    for U in ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)):
        kw = dict(L=4000.0, W=3000.0, ust_derinlik=500.0, U1=U[0], U2=U[1], U3=U[2], egim_deg=45.0)

        def sig(p):
            _, dd = okada_yerel(p[0:1], p[1:2], p[2:3], **kw)
            return _gerilme3(dd)[0]

        div = np.zeros(3)
        for j in range(3):
            a, e = P.copy(), P.copy()
            a[j] += h
            e[j] -= h
            div += (sig(a)[:, j] - sig(e)[:, j]) / (2.0 * h)
        assert np.abs(div).max() < 3e-4 * np.abs(sig(P)).max() / 1000.0


def test_v_ek_paralel_dikey_betti():
    """(v-extra) Betti's reciprocal theorem with the cross-work integrated over each fault surface.

    ``W_AB = int_A du_A . (sigma_B nu) dS`` equals ``W_BA = int_B du_B . (sigma_A nu) dS`` for two
    vertical faults (different length, width, depth, offset and slips), ``du = U1 x + U2 up + U3 nu``
    with ``nu = +y``.  It catches a wrong global sign, a wrong factor and a wrong relative sign
    between U1, U2 and U3 in the kernel.  Gauss-Legendre with 12 x 12 nodes (the faces are
    >= 15 km apart, the integrand is smooth).
    """
    A = dict(L=4000.0, W=3000.0, d=500.0, U=(1.0, 0.5, 0.2))
    B = dict(L=5000.0, W=2000.0, d=1500.0, U=(-0.7, 1.0, 0.4))
    X0, Y0 = 20000.0, 6000.0           # B's centre relative to A's, in A's frame
    n = 12
    g, w = np.polynomial.legendre.leggauss(n)

    def isi(kaynak, ofset, diger, diger_ofset):
        """int over `kaynak`'s plane of du_kaynak . (sigma_diger nu) dS."""
        xs = ofset[0] + 0.5 * kaynak["L"] * g
        zs = kaynak["d"] + 0.5 * kaynak["W"] * (g + 1.0)
        XX, ZZ = np.meshgrid(xs, zs, indexing="ij")
        WW = np.outer(0.5 * kaynak["L"] * w, 0.5 * kaynak["W"] * w)
        _, dud = okada_yerel(XX.ravel() - diger_ofset[0], np.full(XX.size, ofset[1] - diger_ofset[1]), ZZ.ravel(),
                             L=diger["L"], W=diger["W"], ust_derinlik=diger["d"],
                             U1=diger["U"][0], U2=diger["U"][1], U3=diger["U"][2], egim_deg=90.0)
        s = _gerilme3(dud)                                    # (N, 3, 3)
        t = s[:, :, 1]                                        # traction on nu = +y
        U1, U2, U3 = kaynak["U"]
        entegrand = U1 * t[:, 0] - U2 * t[:, 2] + U3 * t[:, 1]   # up = -z
        return float((entegrand * WW.ravel()).sum())

    w_ab = isi(A, (0.0, 0.0), B, (X0, Y0))
    w_ba = isi(B, (X0, Y0), A, (0.0, 0.0))
    assert abs(w_ab) > 1e3 and abs(w_ba) > 1e3
    assert w_ab == pytest.approx(w_ba, rel=1e-6)


def test_yon_isaretleri_fiziksel():
    """The documented signs: U1 left-lateral, U2 reverse (the block at y > 0 rises), U3 opening."""
    kw = dict(L=20000.0, W=10000.0, ust_derinlik=1000.0, egim_deg=90.0)
    yer = (np.array([0.0, 0.0]), np.array([1500.0, -1500.0]), np.array([0.0, 0.0]))
    u, _ = okada_yerel(*yer, U1=1.0, U2=0.0, U3=0.0, **kw)        # block at y > 0 moves +x
    assert u[0, 0] > 0.0 > u[1, 0]
    u, _ = okada_yerel(*yer, U1=0.0, U2=1.0, U3=0.0, **kw)        # reverse: y > 0 side rises (z is down)
    assert u[0, 2] < 0.0 < u[1, 2]
    u, _ = okada_yerel(*yer, U1=0.0, U2=0.0, U3=1.0, **kw)        # opening pushes the +y side to +y
    assert u[0, 1] > 0.0 > u[1, 1]


def test_orta_nokta_ucta_yarim():
    """The fault is centred on x = 0: the antiplane gradient at its end plane is half the mid-length one."""
    d = 1000.0
    W, L = 1e5 * d, 1e4 * (1e5 * d)
    kw = dict(L=L, W=W, ust_derinlik=d, U1=1.0, U2=0.0, U3=0.0, egim_deg=90.0)
    _, orta = okada_yerel(np.array([0.0]), np.array([0.0]), np.array([0.0]), **kw)
    _, uc = okada_yerel(np.array([0.5 * L]), np.array([0.0]), np.array([0.0]), **kw)
    assert float(uc[0, 0, 1]) == pytest.approx(0.5 * float(orta[0, 0, 1]), rel=1e-3)


def test_kenar_dogrultusu_uzantisinda_sonlu():
    """Receivers on the extensions of the edges and on the fault plane are finite (no singular value leaks out)."""
    d, L, W = 1000.0, 4000.0, 3000.0
    for egim in (90.0, 60.0):
        for U in ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)):
            x = np.array([-0.5 * L, 0.5 * L, -0.5 * L - 700.0, 0.5 * L + 700.0, 0.0, 0.0, 0.0])
            y = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
            z = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 400.0, 0.0])
            u, dud = okada_yerel(x, y, z, L=L, W=W, ust_derinlik=d, U1=U[0], U2=U[1], U3=U[2], egim_deg=egim)
            assert np.isfinite(u).all() and np.isfinite(dud).all()


def _kaynak_duzlemi_noktasi(egim, z, ust=1000.0):
    """The y of the point of the fault plane at depth z (the plane runs from the upper edge at y = 0)."""
    return (z - ust) / np.tan(np.deg2rad(egim)) if egim != 90.0 else 0.0


def test_levha_uzerinde_iki_yanin_ortalamasi():
    """Rule (i): on the fault surface (q = 0, away from its edges) the displacement along the slip is the
    mean of the two sides, the other components are continuous (Okada p. 1034)."""
    L, W, ust = 4000.0, 3000.0, 1000.0
    for egim in (90.0, 60.0):
        z = ust + 0.5 * W * np.sin(np.deg2rad(egim))
        y0 = _kaynak_duzlemi_noktasi(egim, z, ust)
        # the unit normal of the plane in this frame: (0, -sin, cos) up to sign; step along it by eps
        n = np.array([np.sin(np.deg2rad(egim)), -np.cos(np.deg2rad(egim))])      # (dy, dz) normal to the plane
        eps = 1e-3
        for U in ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)):
            kw = dict(L=L, W=W, ust_derinlik=ust, U1=U[0], U2=U[1], U3=U[2], egim_deg=egim)
            u0, _ = okada_yerel(np.array([300.0]), np.array([y0]), np.array([z]), **kw)
            ua, _ = okada_yerel(np.array([300.0]), np.array([y0 + eps * n[0]]), np.array([z + eps * n[1]]), **kw)
            ue, _ = okada_yerel(np.array([300.0]), np.array([y0 - eps * n[0]]), np.array([z - eps * n[1]]), **kw)
            assert u0[0] == pytest.approx(0.5 * (ua[0] + ue[0]), abs=1e-4)
            # and the jump across it is the unit slip vector: |u(+) - u(-)| = 1 m
            assert np.linalg.norm(ua[0] - ue[0]) == pytest.approx(1.0, abs=1e-2)
            # the sign: hanging wall (the side of nu, n above) minus foot wall is the slip vector
            # U1 along strike + U2 up-dip (0, -cos, -sin in x, y, z-down) + U3 along nu = (0, sin, -cos)
            dr = np.deg2rad(egim)
            sapma = U[0] * np.array([1.0, 0.0, 0.0]) + U[1] * np.array([0.0, -np.cos(dr), -np.sin(dr)]) \
                + U[2] * np.array([0.0, np.sin(dr), -np.cos(dr)])
            assert ua[0] - ue[0] == pytest.approx(sapma, abs=1e-2)


def test_kural_cizgilerinde_surekli():
    """Rules (ii)-(iv): on the end planes, and on the extensions of the edges, the field is the continuous
    limit of its neighbours (Okada pp. 1034-1037): the value at the special line equals the mean of
    four neighbours a distance eps away (second-order agreement)."""
    L, W, ust = 4000.0, 3000.0, 1000.0
    eps = 0.05
    for egim in (90.0, 60.0):
        zalt = ust + W * np.sin(np.deg2rad(egim))
        yalt = W * np.cos(np.deg2rad(egim))
        # (point, the two coordinate axes perpendicular to the special line)
        durumlar = [
            ((2000.0, yalt, zalt + 2000.0), (0, 1)),        # below the lower end corner on the end plane
            ((-3000.0, 0.0, ust), (1, 2)),                  # the upper edge extended along strike
            ((-3000.0, yalt, zalt), (1, 2)),                # the lower edge extended along strike
            ((2000.0, 0.0, ust - 500.0), (0, 1)),           # above the upper end corner, end plane
        ]
        for (p, eksenler) in durumlar:
            for U in ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)):
                kw = dict(L=L, W=W, ust_derinlik=ust, U1=U[0], U2=U[1], U3=U[2], egim_deg=egim)
                P = np.array(p)
                u0, d0 = okada_yerel(P[0:1], P[1:2], P[2:3], **kw)
                ort_u = np.zeros(3)
                ort_d = np.zeros((3, 3))
                for ax in eksenler:
                    for s in (1.0, -1.0):
                        Q = P.copy()
                        Q[ax] += s * eps
                        uq, dq = okada_yerel(Q[0:1], Q[1:2], Q[2:3], **kw)
                        ort_u += uq[0] / 4.0
                        ort_d += dq[0] / 4.0
                assert np.isfinite(u0).all() and np.isfinite(d0).all()
                assert u0[0] == pytest.approx(ort_u, abs=1e-4 * max(1e-3, np.abs(u0).max()), rel=1e-4)
                assert d0[0] == pytest.approx(ort_d, abs=1e-4 * max(1e-9, np.abs(d0).max()), rel=1e-4)


def test_kural_ii_uc_duzlemi_koseye_yakin():
    """Rule (ii) (xi = 0, I4 = 0): half a metre beyond the lower end corner, on the end plane of a dipping
    fault, the field equals the mean of its two neighbours across the plane (the field is continuous
    there; ``I4`` alone jumps by pi/cos^2 and must be set to zero, not left to the arctangent)."""
    L, W, ust, egim = 4000.0, 3000.0, 1000.0, 60.0
    zalt = ust + W * np.sin(np.deg2rad(egim))
    yalt = W * np.cos(np.deg2rad(egim))
    P = np.array([0.5 * L, yalt + 0.4, zalt + 0.3])
    eps = 0.01
    for U in ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)):
        kw = dict(L=L, W=W, ust_derinlik=ust, U1=U[0], U2=U[1], U3=U[2], egim_deg=egim)
        u0, d0 = okada_yerel(P[0:1], P[1:2], P[2:3], **kw)
        ua, da = okada_yerel(P[0:1] + eps, P[1:2], P[2:3], **kw)
        ue, de = okada_yerel(P[0:1] - eps, P[1:2], P[2:3], **kw)
        assert u0[0] == pytest.approx(0.5 * (ua[0] + ue[0]), rel=1e-3, abs=1e-6)
        assert d0[0] == pytest.approx(0.5 * (da[0] + de[0]), rel=1e-2, abs=1e-5 * np.abs(d0).max())


def test_korumalar_egim_zorunlu_ve_yuzey_ustu():
    """``egim_deg`` is required and must satisfy 0 < egim_deg <= 90; receivers above the surface are refused."""
    a = (np.array([0.0]), np.array([0.0]), np.array([0.0]))
    kw = dict(L=1000.0, W=800.0, ust_derinlik=100.0, U1=1.0, U2=0.0, U3=0.0)
    with pytest.raises(TypeError, match="egim_deg"):
        okada_yerel(*a, **kw)
    for kotu in (0.0, -10.0, 90.5, 120.0):
        with pytest.raises(ValueError, match="egim_deg"):
            okada_yerel(*a, egim_deg=kotu, **kw)
    with pytest.raises(ValueError, match="z < 0"):
        okada_yerel(a[0], a[1], np.array([-1.0]), egim_deg=60.0, **kw)
    with pytest.raises(ValueError, match="alici_derinlik_m"):
        okada_ned(kaynak=_kaynak(10.0, 45.0, 1.0, 0.0, 0.0), alici_lat=42.0, alici_lon=13.0, alici_derinlik_m=-5.0)
