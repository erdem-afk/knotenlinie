"""Kanal yüzü testleri: okada_ned sözleşmesi, bilinen cevap ve defter gidiş-dönüşü.

The kernel is built: ``okada_ned`` is checked against ``okada_yerel`` plus an
independently written frame transform; the ledger round trip still uses a synthetic tensor,
which is what the transfer code is written against.
"""
import numpy as np
import pandas as pd
import pytest

from knotenlinie.elastik.okada import kaynak_dogrula, okada_ned, okada_yerel

_DOGRU = {
    "dogrultu_deg": 155.0, "egim_deg": 45.0, "kayma_deg": -90.0,
    "uzunluk_m": 15000.0, "genislik_m": 12000.0, "ust_derinlik_m": 2000.0,
    "kayma_m": 1.0, "kaynak_lat": 42.5, "kaynak_lon": 13.2,
}


def test_kaynak_bilinmeyen_anahtar():
    kotu = dict(_DOGRU)
    kotu["buyukluk"] = 6.0
    with pytest.raises(ValueError) as hata:
        kaynak_dogrula(kotu)
    assert "buyukluk" in str(hata.value)


def test_kaynak_eksik_anahtar():
    kotu = dict(_DOGRU)
    del kotu["ust_derinlik_m"]
    with pytest.raises(ValueError) as hata:
        kaynak_dogrula(kotu)
    assert "ust_derinlik_m" in str(hata.value)


def test_acilma_secmeli():
    tam = dict(_DOGRU)
    tam["acilma_m"] = 0.1
    assert kaynak_dogrula(tam)["acilma_m"] == 0.1


def test_okada_ned_bilinen_cevap():
    """Known answer: okada_ned equals okada_yerel plus the frame transform written out independently.

    The test rebuilds the chain by hand: ``aeqd_metre`` offsets (2.1.0), the strike rotation about the
    vertical (north/east -> along strike / to the right of the strike), ``okada_yerel`` at the
    receiver depth, Hooke's law written out (``sigma = lam tr(eps) I + 2 mu eps``), the rotation of
    the Voigt tensor back to the source grid, and the ``+gamma`` rotation into the receiver's local
    NED, none of it through ``cerceve.dud_gerilme``, ``yerelden_nede`` or
    ``cerceve.yakinsama_rad``.
    """
    from knotenlinie.elastik.cerceve import aeqd_metre

    kaynak = dict(_DOGRU)
    kaynak["acilma_m"] = 0.25
    lat = np.array([42.55, 42.40, 42.62])
    lon = np.array([13.31, 13.05, 13.18])
    z = np.array([3000.0, 8000.0, 500.0])
    sigma = okada_ned(kaynak=kaynak, alici_lat=lat, alici_lon=lon, alici_derinlik_m=z)
    assert sigma.shape == (3, 6)

    S = np.deg2rad(kaynak["dogrultu_deg"])
    n, e = aeqd_metre(lat, lon, lat0_deg=kaynak["kaynak_lat"], lon0_deg=kaynak["kaynak_lon"])
    x = n * np.cos(S) + e * np.sin(S)
    # (kaynak_lat, kaynak_lon) is the rectangle's centre: the upper edge lies W/2 cos(dip) behind it
    y = -n * np.sin(S) + e * np.cos(S) + 0.5 * kaynak["genislik_m"] * np.cos(np.deg2rad(kaynak["egim_deg"]))
    rake = np.deg2rad(kaynak["kayma_deg"])
    u, dud = okada_yerel(x, y, z, L=kaynak["uzunluk_m"], W=kaynak["genislik_m"], ust_derinlik=kaynak["ust_derinlik_m"],
                         U1=kaynak["kayma_m"] * np.cos(rake), U2=kaynak["kayma_m"] * np.sin(rake), U3=0.25,
                         egim_deg=kaynak["egim_deg"])
    lam = mu = 30.0e9
    # the local frame's axes in NED: x along strike, y to the right of the strike, z down
    Rm = np.array([[np.cos(S), np.sin(S), 0.0], [-np.sin(S), np.cos(S), 0.0], [0.0, 0.0, 1.0]])
    # convergence written out (alpha at the centre, beta back from the receiver), no cerceve call
    p1, p2 = np.deg2rad(kaynak["kaynak_lat"]), np.deg2rad(lat)
    dl = np.deg2rad(lon - kaynak["kaynak_lon"])
    alfa = np.arctan2(np.sin(dl) * np.cos(p2), np.cos(p1) * np.sin(p2) - np.sin(p1) * np.cos(p2) * np.cos(dl))
    beta = np.arctan2(-np.sin(dl) * np.cos(p1), np.cos(p2) * np.sin(p1) - np.sin(p2) * np.cos(p1) * np.cos(dl))
    gamma = (beta + np.pi - alfa + np.pi) % (2.0 * np.pi) - np.pi
    for i in range(3):
        eps = 0.5 * (dud[i] + dud[i].T)
        sig_loc = lam * np.trace(eps) * np.eye(3) + 2.0 * mu * eps
        sig_ned = Rm.T @ sig_loc @ Rm                       # source grid
        g = gamma[i]
        Rg = np.array([[np.cos(g), -np.sin(g), 0.0], [np.sin(g), np.cos(g), 0.0], [0.0, 0.0, 1.0]])  # R(+gamma)
        sig_lcl = Rg @ sig_ned @ Rg.T                       # receiver local NED
        beklenen = [sig_lcl[0, 0], sig_lcl[1, 1], sig_lcl[2, 2], sig_lcl[0, 1], sig_lcl[0, 2], sig_lcl[1, 2]]
        assert sigma[i] == pytest.approx(beklenen, rel=1e-12, abs=1e-6)
    assert np.isfinite(sigma).all() and np.abs(sigma).max() > 1e3


def test_okada_ned_skaler_alici_alti_vektor():
    s = okada_ned(kaynak=dict(_DOGRU), alici_lat=42.55, alici_lon=13.31, alici_derinlik_m=3000.0)
    assert s.shape == (6,)
    d = okada_ned(kaynak=dict(_DOGRU), alici_lat=np.array([42.55]), alici_lon=np.array([13.31]),
                  alici_derinlik_m=np.array([3000.0]))
    assert d.shape == (1, 6)
    assert d[0] == pytest.approx(s, rel=1e-14)


def test_kayma_bilesenleri_fay_vektorleri_ile_ayni():
    """The slip vector rebuilt from (U1, U2) equals ``fay_vektorleri(...)[1] * kayma_m`` to 1e-12.

    ``okada_yerel``'s U1 is along strike and U2 along the up-dip direction; both axes are
    taken here from ``yerel_cerceve`` (x strike, y DOWN-dip, so up-dip is ``-y``).
    """
    from knotenlinie.defter.geometri import fay_vektorleri
    from knotenlinie.elastik.cerceve import yerel_cerceve
    from knotenlinie.elastik.okada import kayma_bilesenleri

    for dogrultu in (0.0, 37.0, 155.0, 290.0):
        for egim in (10.0, 45.0, 90.0):
            for rake in (-135.0, -90.0, 0.0, 30.0, 90.0, 180.0):
                kaynak = dict(_DOGRU, dogrultu_deg=dogrultu, egim_deg=egim, kayma_deg=rake, kayma_m=1.7)
                U1, U2, U3 = kayma_bilesenleri(kaynak)
                assert U3 == 0.0
                R = yerel_cerceve(dogrultu, egim)
                yeniden = U1 * R[0] - U2 * R[1]
                _, slip = fay_vektorleri(dogrultu, egim, rake)
                assert yeniden == pytest.approx(slip * 1.7, abs=1e-12)
    assert kayma_bilesenleri(dict(_DOGRU, acilma_m=0.4))[2] == 0.4


def test_okada_ned_normal_gerilme_cekme_pozitif():
    """A pure opening (tension positive) at the source centre gives compression across the opened plane."""
    kaynak = dict(_DOGRU, kayma_m=0.0, acilma_m=1.0, egim_deg=90.0)
    # a receiver just beside the fault plane at the centre depth: opening pushes the walls apart,
    # so the stress normal to the plane at the wall is compressive (negative)
    S = np.deg2rad(kaynak["dogrultu_deg"])
    sag = np.array([-np.sin(S), np.cos(S)])          # the right of the strike direction, horizontal
    from knotenlinie.elastik.cerceve import ned_metre

    lat0, lon0 = kaynak["kaynak_lat"], kaynak["kaynak_lon"]
    kuzey, dogu = 300.0 * sag
    lat = lat0 + np.rad2deg(kuzey / 6371000.0)
    lon = lon0 + np.rad2deg(dogu / (6371000.0 * np.cos(np.deg2rad(lat0))))
    zc = kaynak["ust_derinlik_m"] + 0.5 * kaynak["genislik_m"]
    s = okada_ned(kaynak=kaynak, alici_lat=lat, alici_lon=lon, alici_derinlik_m=zc)
    n = np.array([sag[0], sag[1], 0.0])
    sigma_n = n @ np.array([[s[0], s[3], s[4]], [s[3], s[1], s[5]], [s[4], s[5], s[2]]]) @ n
    assert sigma_n < 0.0


def test_defter_gidis_donusu(tmp_path, kabul):
    """A synthetic K9 step written through knotenlinie.defter survives; the reader's ΔCFS is coulomb."""
    tau = np.array([-12.5, 3.25])
    sigma_n = np.array([7.5, -2.0])
    tensor = {
        "s_xx_Pa": [1.0, -2.0], "s_yy_Pa": [2.0, -3.0], "s_zz_Pa": [3.0, -4.0],
        "s_xy_Pa": [0.1, -0.2], "s_xz_Pa": [0.2, -0.3], "s_yz_Pa": [0.3, -0.4],
    }
    satirlar = pd.DataFrame({
        "fault_id": ["F1", "F2"],
        "time_utc": pd.to_datetime(["2024-01-01T00:00:00Z", "2024-01-01T00:00:00Z"]),
        "kind": ["step", "step"],
        "tau_Pa": tau,
        "sigma_n_Pa": sigma_n,
    })
    for ad, deger in tensor.items():
        satirlar[ad] = deger
    from knotenlinie.defter import coulomb, oku, yaz

    hedef = tmp_path / "k9_v1.parquet"
    yaz(hedef, kanal="K9", kanal_surum="v1", satirlar=satirlar, kabul=kabul,
        isaret={"normal": "tension_positive", "kayma": "rake_positive"}, uretici="test@elastik")
    d = oku(hedef)
    for ad, deger in tensor.items():
        assert list(d.satirlar[ad]) == list(deger)
    beklenen = coulomb(d.satirlar["tau_Pa"].to_numpy(), d.satirlar["sigma_n_Pa"].to_numpy(), mu_prime=0.4)
    assert d.cfs[0.4] == pytest.approx(beklenen)
    assert d.cfs[0.4][0] == pytest.approx(tau[0] + 0.4 * sigma_n[0])
    # the default sign declaration (tension positive, rake positive) is the identity: nothing was flipped on the way in
    assert d.meta["isaret"] == {"normal": "tension_positive", "kayma": "rake_positive"}
