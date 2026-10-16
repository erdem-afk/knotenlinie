"""Okada 1985 Table 2, "Checklist for numerical calculations" — a manual transcription.

Source: Okada, Y. (1985), Surface deformation due to shear and tensile faults in a half-space,
BSSA 75(4), 1135-1154, Table 2 on journal page 1149. Transcribed on 2026-10-03 from the page
rendered at 220 dpi and
checked value by value against a 400 dpi render; the text layer of that page is unusable (OCR
noise), so nothing here comes from it.

The paper's own note (p. 1150, below its equation (42)): case 1 is a point source, cases 2-4
finite rectangles; the medium is lambda = mu in every case; values are in units of U*dSigma
(U times the source area element) for case 1 and in units of U for the others, where U is U1,
U2 or U3 (one component at a time, unit size). The receiver is on the free surface. The
geometry is given in Okada 1985's own frame and parameters (x, y, d, delta, L, W, as in the
table's footnotes a-d); mapping them to ``okada_yerel``'s frame and ``ust_derinlik`` is read from
the paper's figure of the source geometry by the kernel task, not assumed here. Okada 1992 has
no numerical table (its Table 2 holds formulas), so these surface values are the paper check
for the internal-field kernel at the free surface.

Every value is kept as the printed string so the check can use the printed precision: four
significant figures. A computed value matches when it rounds to the printed one (within half a
unit of the last printed digit); a printed 0 matches when the computed value is zero to
rounding (|value| <= 1e-12 times the case's largest printed magnitude).
"""

SUTUNLAR = ("ux", "uy", "uz", "dux/dx", "dux/dy", "duy/dx", "duy/dy", "duz/dx", "duz/dy")

# geometry per case: receiver (x, y) on z = 0, reference depth d, dip delta (deg), L, W
GEOMETRI = {
    1: {"tur": "nokta", "x": 2.0, "y": 3.0, "d": 4.0, "delta_deg": 70.0},
    2: {"tur": "dikdortgen", "x": 2.0, "y": 3.0, "d": 4.0, "delta_deg": 70.0, "L": 3.0, "W": 2.0},
    3: {"tur": "dikdortgen", "x": 0.0, "y": 0.0, "d": 4.0, "delta_deg": 90.0, "L": 3.0, "W": 2.0},
    4: {"tur": "dikdortgen", "x": 0.0, "y": 0.0, "d": 4.0, "delta_deg": -90.0, "L": 3.0, "W": 2.0},
}

# TABLO[case][slip] = nine printed values in SUTUNLAR order; slip is "strike" (U1),
# "dip" (U2) or "tensile" (U3)
TABLO = {
    1: {
        "strike": ("-9.447E-4", "-1.023E-3", "-7.420E-4", "-2.286E-4", "-1.425E-4", "-2.051E-4",
                   "-3.007E-4", "-6.259E-5", "-1.693E-4"),
        "dip": ("-1.172E-3", "-2.082E-3", "-2.532E-3", "-1.526E-4", "-3.544E-4", "+6.983E-4",
                "-1.154E-3", "+8.707E-4", "-6.345E-4"),
        "tensile": ("-3.572E-4", "+3.531E-4", "-2.007E-4", "-1.360E-4", "+5.073E-4", "-6.773E-5",
                    "+6.811E-4", "+7.541E-5", "+8.104E-4"),
    },
    2: {
        "strike": ("-8.689E-3", "-4.298E-3", "-2.747E-3", "-1.220E-3", "+2.470E-4", "-8.191E-3",
                   "-5.814E-4", "-5.175E-3", "+2.945E-4"),
        "dip": ("-4.682E-3", "-3.527E-2", "-3.564E-2", "-8.867E-3", "-1.519E-4", "+4.057E-3",
                "-1.035E-2", "+4.088E-3", "+2.626E-3"),
        "tensile": ("-2.660E-4", "+1.056E-2", "+3.214E-3", "-5.655E-4", "+1.993E-3", "-1.066E-3",
                    "+1.230E-2", "-3.730E-4", "+1.040E-2"),
    },
    3: {
        "strike": ("0", "+5.253E-3", "0", "0", "-1.864E-2", "-2.325E-3", "0", "0", "+2.289E-2"),
        "dip": ("0", "0", "0", "0", "+2.748E-2", "0", "0", "0", "-7.166E-2"),
        "tensile": ("+1.223E-2", "0", "-1.606E-2", "-4.182E-3", "0", "0", "-2.325E-3", "-9.146E-3",
                    "0"),
    },
    4: {
        "strike": ("0", "-1.303E-3", "0", "0", "+2.726E-3", "+7.345E-4", "0", "0", "-4.422E-3"),
        "dip": ("0", "0", "0", "0", "+5.157E-3", "0", "0", "0", "-1.901E-2"),
        "tensile": ("+3.507E-3", "0", "-7.740E-3", "-1.770E-3", "0", "0", "-7.345E-4", "-1.843E-3",
                    "0"),
    },
}


def yarim_birim(basili):
    """Half a unit of the last printed digit of a printed value ("-1.220E-3" -> 5e-7)."""
    s = basili.strip().lstrip("+-")
    if s == "0":
        return 0.0
    mantis, us = s.upper().split("E")
    ondalik = len(mantis.split(".")[1]) if "." in mantis else 0
    return 0.5 * 10.0 ** (int(us) - ondalik)


def eslesir(hesap, basili, olcek):
    """True iff ``hesap`` rounds to the printed value (``olcek`` = the case's largest |value|)."""
    if basili.strip() == "0":
        return abs(hesap) <= 1e-12 * olcek
    return abs(hesap - float(basili)) <= yarim_birim(basili)
