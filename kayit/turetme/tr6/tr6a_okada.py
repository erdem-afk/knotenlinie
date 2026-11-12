"""TR-6a: Okada (1992) yarı uzay iç deformasyonu (DC3D sonlu dikdörtgen, DC3D0 nokta kaynak) -> gerinim -> gerilme
-> ΔCFF; ızdüşüm (azimutal eşit uzaklık), 10 km ızgara, kırık izi ve r_k, "tekil yakın alan" kuralı, alıcı düzlem
(medyan tensör / ana şok). Ön kayıt sürüm 3 §3.3, §3.4. Yalnız numpy + standart kitaplık; ağ yok, veri okunmaz.

Okada (1992) DC3D / DC3D0 Fortran altyordamlarının (DCCON0, DCCON1, DCCON2, UA, UB, UC, UA0, UB0, UC0) numpy ile,
noktalar üzerinde vektörleştirilmiş yeniden yazımıdır. Kaynak: Okada, Y. (1992), Internal deformation due to shear
and tensile faults in a half-space, BSSA 82(2), 1018-1040; özgün altyordam yapısı ve değişken adları korunmuştur.
Okada 1992 Tablo 2 sınama değerleri bu oturumda okunamadı (yayımlanmış makale ya da açık kopyası elde değil): ön kayıt
§3.3 yedek kuralı uygulanır ve kayda "Okada 1992 tablo değerleri doğrulanamadı" diye geçer (TABLO_DURUMU). Doğrulama
`dogrulama()` ile 1-9. sınamalar ve tekil noktalarla yapılır.

Uzunluklar km, kayma m; gerilme kPa döner (μ = 30 GPa, ν = 0,25, α = 2/3). Koordinatlar: Okada yerel ekseni x
doğrultu boyunca, y doğrultunun solu (yatay), z yukarı (ortamda z ≤ 0). Kayma: DISL1 = s·cos λ (λ = 0 sol yanal),
DISL2 = s·sin λ (λ = 90 ters), tavan bloğunun taban bloğuna göre hareketi (Aki & Richards).
"""
import math
import numpy as np

TABLO_DURUMU = "Okada 1992 tablo değerleri doğrulanamadı"
MU_PA = 30e9
NU = 0.25
LAM_PA = 2 * MU_PA * NU / (1 - 2 * NU)            # = μ (ν = 0,25)
ALFA = (LAM_PA + MU_PA) / (LAM_PA + 2 * MU_PA)     # = 2/3
MU_SURT = 0.4                                     # etkin sürtünme μ'
HESAP_DERINLIK_KM = 7.5
HUCRE_KM = 10.0
TEKIL_YAKIN_KM = 5.0
IZ_ADIM_KM = 2.0
IZ_PAY = 0.10
R_DUNYA = 6371.0
EPS = 1.0e-6
PI2 = 2.0 * math.pi


class OkadaHata(Exception):
    pass


# ================================================================== DC3D (sonlu dikdörtgen)
def _dccon0(alpha, dip):
    c = dict(alp1=(1 - alpha) / 2, alp2=alpha / 2, alp3=(1 - alpha) / alpha, alp4=1 - alpha, alp5=alpha)
    sd, cd = math.sin(math.radians(dip)), math.cos(math.radians(dip))
    if abs(cd) < EPS:
        cd = 0.0
        sd = 1.0 if sd > 0 else -1.0
    c.update(sd=sd, cd=cd, sdsd=sd * sd, cdcd=cd * cd, sdcd=sd * cd, s2d=2 * sd * cd, c2d=cd * cd - sd * sd)
    return c


def _dccon2(xi, et, q, c, kxi, ket):
    xi = np.where(np.abs(xi) < EPS, 0.0, xi)
    et = np.where(np.abs(et) < EPS, 0.0, et)
    q = np.where(np.abs(q) < EPS, 0.0, q)
    sd, cd = c["sd"], c["cd"]
    v = {}
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        xi2, et2, q2 = xi * xi, et * et, q * q
        r2 = xi2 + et2 + q2
        r = np.sqrt(r2)
        r3 = r * r2
        r5 = r3 * r2
        y = et * cd + q * sd
        d = et * sd - q * cd
        tt = np.where(q == 0, 0.0, np.arctan(xi * et / (q * r)))
        # Kodlayıcı okuması 12: R + ξ ve R + η, ξ < 0 / η < 0 iken (R² − ξ²)/(R − ξ) biçiminde hesaplanır
        # (matematikçe özdeş; kaynağın altında/uzantısında sayısal yok etmeyi önler).
        rxi = np.where(xi < 0, (et2 + q2) / (r - xi), r + xi)
        alx = np.where(kxi, -np.log(r - xi), np.log(rxi))
        x11 = np.where(kxi, 0.0, 1.0 / (r * rxi))
        x32 = np.where(kxi, 0.0, (r + rxi) * x11 * x11 / r)
        ret = np.where(et < 0, (xi2 + q2) / (r - et), r + et)
        ale = np.where(ket, -np.log(r - et), np.log(ret))
        y11 = np.where(ket, 0.0, 1.0 / (r * ret))
        y32 = np.where(ket, 0.0, (r + ret) * y11 * y11 / r)
        ey = sd / r - y * q / r3
        ez = cd / r + d * q / r3
        fy = d / r3 + xi2 * y32 * sd
        fz = y / r3 + xi2 * y32 * cd
        gy = 2 * x11 * sd - y * q * x32
        gz = 2 * x11 * cd + d * q * x32
        hy = d * q * x32 + xi * q * y32 * sd
        hz = y * q * x32 + xi * q * y32 * cd
    v.update(xi=xi, et=et, q=q, xi2=xi2, et2=et2, q2=q2, r2=r2, r=r, r3=r3, r5=r5, y=y, d=d, tt=tt, alx=alx,
             x11=x11, x32=x32, ale=ale, y11=y11, y32=y32, ey=ey, ez=ez, fy=fy, fz=fz, gy=gy, gz=gz, hy=hy, hz=hz)
    return v


def _ua(v, c, d1, d2, d3):
    xi, et, q, r, r3 = v["xi"], v["et"], v["q"], v["r"], v["r3"]
    xi2, q2, tt, alx, ale = v["xi2"], v["q2"], v["tt"], v["alx"], v["ale"]
    x11, y11, y32, y, d = v["x11"], v["y11"], v["y32"], v["y"], v["d"]
    ey, ez, fy, fz, gy, gz, hy, hz = (v[k] for k in ("ey", "ez", "fy", "fz", "gy", "gz", "hy", "hz"))
    a1, a2, sd, cd = c["alp1"], c["alp2"], c["sd"], c["cd"]
    u = np.zeros((12,) + np.shape(xi))
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        xy, qx, qy = xi * y11, q * x11, q * y11
        if d1 != 0:
            du = [tt / 2 + a2 * xi * qy, a2 * q / r, a1 * ale - a2 * q * qy,
                  -a1 * qy - a2 * xi2 * q * y32, -a2 * xi * q / r3, a1 * xy + a2 * xi * q2 * y32,
                  a1 * xy * sd + a2 * xi * fy + d / 2 * x11, a2 * ey, a1 * (cd / r + qy * sd) - a2 * q * fy,
                  a1 * xy * cd + a2 * xi * fz + y / 2 * x11, a2 * ez, -a1 * (sd / r - qy * cd) - a2 * q * fz]
            u += d1 / PI2 * np.array(du)
        if d2 != 0:
            du = [a2 * q / r, tt / 2 + a2 * et * qx, a1 * alx - a2 * q * qx,
                  -a2 * xi * q / r3, -qy / 2 - a2 * et * q / r3, a1 / r + a2 * q2 / r3,
                  a2 * ey, a1 * d * x11 + xy / 2 * sd + a2 * et * gy, a1 * y * x11 - a2 * q * gy,
                  a2 * ez, a1 * y * x11 + xy / 2 * cd + a2 * et * gz, -a1 * d * x11 - a2 * q * gz]
            u += d2 / PI2 * np.array(du)
        if d3 != 0:
            du = [-a1 * ale - a2 * q * qy, -a1 * alx - a2 * q * qx, tt / 2 - a2 * (et * qx + xi * qy),
                  -a1 * xy + a2 * xi * q2 * y32, -a1 / r + a2 * q2 / r3, -a1 * qy - a2 * q * q2 * y32,
                  -a1 * (cd / r + qy * sd) - a2 * q * fy, -a1 * y * x11 - a2 * q * gy,
                  a1 * (d * x11 + xy * sd) + a2 * q * hy,
                  a1 * (sd / r - qy * cd) - a2 * q * fz, a1 * d * x11 - a2 * q * gz,
                  a1 * (y * x11 + xy * cd) + a2 * q * hz]
            u += d3 / PI2 * np.array(du)
    return u


def _ub(v, c, d1, d2, d3):
    xi, et, q, r, r3 = v["xi"], v["et"], v["q"], v["r"], v["r3"]
    xi2, q2, tt, ale = v["xi2"], v["q2"], v["tt"], v["ale"]
    x11, y11, y32, y, d = v["x11"], v["y11"], v["y32"], v["y"], v["d"]
    ey, ez, fy, fz, gy, gz, hy, hz = (v[k] for k in ("ey", "ez", "fy", "fz", "gy", "gz", "hy", "hz"))
    a3, sd, cd, sdsd, cdcd, sdcd = c["alp3"], c["sd"], c["cd"], c["sdsd"], c["cdcd"], c["sdcd"]
    u = np.zeros((12,) + np.shape(xi))
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        rd = np.where(d < 0, (xi2 + y * y) / (r - d), r + d)     # okuma 12: R² − D² = ξ² + y²
        d11 = 1.0 / (r * rd)
        aj2 = xi * y / rd * d11
        aj5 = -(d + y * y / rd) * d11
        if cd != 0:
            x = np.sqrt(xi2 + q2)
            ai4 = np.where(xi == 0, 0.0,
                           1.0 / cdcd * (xi / rd * sdcd +
                                         2 * np.arctan((et * (x + q * cd) + x * (r + x) * sd) /
                                                       (xi * (r + x) * cd))))
            ai3 = (y * cd / rd - ale + sd * np.log(rd)) / cdcd
            ak1 = xi * (d11 - y11 * sd) / cd
            ak3 = (q * y11 - y * d11) / cd
            aj3 = (ak1 - aj2 * sd) / cd
            aj6 = (ak3 - aj5 * sd) / cd
        else:
            rd2 = rd * rd
            ai3 = (et / rd + y * q / rd2 - ale) / 2
            ai4 = xi * y / rd2 / 2
            ak1 = xi * q / rd * d11
            ak3 = sd / rd * (xi2 * d11 - 1)
            aj3 = -xi / rd2 * (q2 * d11 - 0.5)
            aj6 = -y / rd2 * (xi2 * d11 - 0.5)
        xy = xi * y11
        ai1 = -xi / rd * cd - ai4 * sd
        ai2 = np.log(rd) + ai3 * sd
        ak2 = 1.0 / r + ak3 * sd
        ak4 = xy * cd - ak1 * sd
        aj1 = aj5 * cd - aj6 * sd
        aj4 = -xy - aj2 * cd + aj3 * sd
        qx, qy = q * x11, q * y11
        if d1 != 0:
            du = [-xi * qy - tt - a3 * ai1 * sd, -q / r + a3 * y / rd * sd, q * qy - a3 * ai2 * sd,
                  xi2 * q * y32 - a3 * aj1 * sd, xi * q / r3 - a3 * aj2 * sd, -xi * q2 * y32 - a3 * aj3 * sd,
                  -xi * fy - d * x11 + a3 * (xy + aj4) * sd, -ey + a3 * (1.0 / r + aj5) * sd,
                  q * fy - a3 * (qy - aj6) * sd,
                  -xi * fz - y * x11 + a3 * ak1 * sd, -ez + a3 * y * d11 * sd, q * fz + a3 * ak2 * sd]
            u += d1 / PI2 * np.array(du)
        if d2 != 0:
            du = [-q / r + a3 * ai3 * sdcd, -et * qx - tt - a3 * xi / rd * sdcd, q * qx + a3 * ai4 * sdcd,
                  xi * q / r3 + a3 * aj4 * sdcd, et * q / r3 + qy + a3 * aj5 * sdcd, -q2 / r3 + a3 * aj6 * sdcd,
                  -ey + a3 * aj1 * sdcd, -et * gy - xy * sd + a3 * aj2 * sdcd, q * gy + a3 * aj3 * sdcd,
                  -ez - a3 * ak3 * sdcd, -et * gz - xy * cd - a3 * xi * d11 * sdcd, q * gz - a3 * ak4 * sdcd]
            u += d2 / PI2 * np.array(du)
        if d3 != 0:
            du = [q * qy - a3 * ai3 * sdsd, q * qx + a3 * xi / rd * sdsd, et * qx + xi * qy - tt - a3 * ai4 * sdsd,
                  -xi * q2 * y32 - a3 * aj4 * sdsd, -q2 / r3 - a3 * aj5 * sdsd, q * q2 * y32 - a3 * aj6 * sdsd,
                  q * fy - a3 * aj1 * sdsd, q * gy - a3 * aj2 * sdsd, -q * hy - a3 * aj3 * sdsd,
                  q * fz + a3 * ak3 * sdsd, q * gz + a3 * xi * d11 * sdsd, -q * hz + a3 * ak4 * sdsd]
            u += d3 / PI2 * np.array(du)
    return u


def _uc(v, c, z, d1, d2, d3):
    xi, et, q, r, r2, r3, r5 = v["xi"], v["et"], v["q"], v["r"], v["r2"], v["r3"], v["r5"]
    xi2, et2, q2 = v["xi2"], v["et2"], v["q2"]
    x11, x32, y11, y32, y, d = v["x11"], v["x32"], v["y11"], v["y32"], v["y"], v["d"]
    a4, a5 = c["alp4"], c["alp5"]
    sd, cd, sdsd, cdcd, sdcd = c["sd"], c["cd"], c["sdsd"], c["cdcd"], c["sdcd"]
    u = np.zeros((12,) + np.shape(xi))
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        cc = d + z
        x53 = (8 * r2 + 9 * r * xi + 3 * xi2) * x11 * x11 * x11 / r2
        y53 = (8 * r2 + 9 * r * et + 3 * et2) * y11 * y11 * y11 / r2
        h = q * cd - z
        z32 = sd / r3 - h * y32
        z53 = 3 * sd / r5 - h * y53
        y0 = y11 - xi2 * y32
        z0 = z32 - xi2 * z53
        ppy = cd / r3 + q * y32 * sd
        ppz = sd / r3 - q * y32 * cd
        qq = z * y32 + z32 + z0
        qqy = 3 * cc * d / r5 - qq * sd
        qqz = 3 * cc * y / r5 - qq * cd + q * y32
        xy, qy = xi * y11, q * y11
        qr = 3 * q / r5
        cdr = (cc + d) / r3
        yy0 = y / r3 - y0 * cd
        if d1 != 0:
            du = [a4 * xy * cd - a5 * xi * q * z32,
                  a4 * (cd / r + 2 * qy * sd) - a5 * cc * q / r3,
                  a4 * qy * cd - a5 * (cc * et / r3 - z * y11 + xi2 * z32),
                  a4 * y0 * cd - a5 * q * z0,
                  -a4 * xi * (cd / r3 + 2 * q * y32 * sd) + a5 * cc * xi * qr,
                  -a4 * xi * q * y32 * cd + a5 * xi * (3 * cc * et / r5 - qq),
                  -a4 * xi * ppy * cd - a5 * xi * qqy,
                  a4 * 2 * (d / r3 - y0 * sd) * sd - y / r3 * cd - a5 * (cdr * sd - et / r3 - cc * y * qr),
                  -a4 * q / r3 + yy0 * sd + a5 * (cdr * cd + cc * d * qr - (y0 * cd + q * z0) * sd),
                  a4 * xi * ppz * cd - a5 * xi * qqz,
                  a4 * 2 * (y / r3 - y0 * cd) * sd + d / r3 * cd - a5 * (cdr * cd + cc * d * qr),
                  yy0 * cd - a5 * (cdr * sd - cc * y * qr - y0 * sdsd + q * z0 * cd)]
            u += d1 / PI2 * np.array(du)
        if d2 != 0:
            du = [a4 * cd / r - qy * sd - a5 * cc * q / r3,
                  a4 * y * x11 - a5 * cc * et * q * x32,
                  -d * x11 - xy * sd - a5 * cc * (x11 - q2 * x32),
                  -a4 * xi / r3 * cd + a5 * cc * xi * qr + xi * q * y32 * sd,
                  -a4 * y / r3 + a5 * cc * et * qr,
                  d / r3 - y0 * sd + a5 * cc / r3 * (1 - 3 * q2 / r2),
                  -a4 * et / r3 + y0 * sdsd - a5 * (cdr * sd - cc * y * qr),
                  a4 * (x11 - y * y * x32) - a5 * cc * ((d + 2 * q * cd) * x32 - y * et * q * x53),
                  xi * ppy * sd + y * d * x32 + a5 * cc * ((y + 2 * q * sd) * x32 - y * q2 * x53),
                  -q / r3 + y0 * sdcd - a5 * (cdr * cd + cc * d * qr),
                  a4 * y * d * x32 - a5 * cc * ((y - 2 * q * sd) * x32 + d * et * q * x53),
                  -xi * ppz * sd + x11 - d * d * x32 - a5 * cc * ((d - 2 * q * cd) * x32 - d * q2 * x53)]
            u += d2 / PI2 * np.array(du)
        if d3 != 0:
            du = [-a4 * (sd / r + qy * cd) - a5 * (z * y11 - q2 * z32),
                  a4 * 2 * xy * sd + d * x11 - a5 * cc * (x11 - q2 * x32),
                  a4 * (y * x11 + xy * cd) + a5 * q * (cc * et * x32 + xi * z32),
                  a4 * xi / r3 * sd + xi * q * y32 * cd + a5 * xi * (3 * cc * et / r5 - 2 * z32 - z0),
                  a4 * 2 * y0 * sd - d / r3 + a5 * cc / r3 * (1 - 3 * q2 / r2),
                  -a4 * yy0 - a5 * (cc * et * qr - q * z0),
                  a4 * (q / r3 + y0 * sdcd) + a5 * (z / r3 * cd + cc * d * qr - q * z0 * sd),
                  -a4 * 2 * xi * ppy * sd - y * d * x32 + a5 * cc * ((y + 2 * q * sd) * x32 - y * q2 * x53),
                  -a4 * (xi * ppy * cd - x11 + y * y * x32)
                  + a5 * (cc * ((d + 2 * q * cd) * x32 - y * et * q * x53) + xi * qqy),
                  -et / r3 + y0 * cdcd - a5 * (z / r3 * sd - cc * y * qr - y0 * sdsd + q * z0 * cd),
                  a4 * 2 * xi * ppz * sd - x11 + d * d * x32 - a5 * cc * ((d - 2 * q * cd) * x32 - d * q2 * x53),
                  a4 * (xi * ppz * cd + y * d * x32) + a5 * (cc * ((y - 2 * q * sd) * x32 + d * et * q * x53)
                                                          + xi * qqz)]
            u += d3 / PI2 * np.array(du)
    return u


def _kxi_ket(xi, et, q):
    r12 = np.sqrt(xi[0] ** 2 + et[1] ** 2 + q ** 2)
    r21 = np.sqrt(xi[1] ** 2 + et[0] ** 2 + q ** 2)
    r22 = np.sqrt(xi[1] ** 2 + et[1] ** 2 + q ** 2)
    kxi = [(xi[0] < 0) & (r21 + xi[1] < EPS), (xi[0] < 0) & (r22 + xi[1] < EPS)]
    ket = [(et[0] < 0) & (r12 + et[1] < EPS), (et[0] < 0) & (r22 + et[1] < EPS)]
    return kxi, ket


def _kenar_tekil(xi, et, q):
    return (q == 0) & (((xi[0] * xi[1] <= 0) & (et[0] * et[1] == 0)) |
                       ((et[0] * et[1] <= 0) & (xi[0] * xi[1] == 0)))


def dc3d(alpha, x, y, z, depth, dip, al1, al2, aw1, aw2, disl1, disl2, disl3):
    """Okada (1992) DC3D. x, y, z dizileri (z ≤ 0). Dönüş: (u (12, N), tekil (N,)). u sırası: UX, UY, UZ, UXX,
    UYX, UZX, UXY, UYY, UZY, UXZ, UYZ, UZZ (UXY = ∂ux/∂y). Tekil noktalarda (fay kenarı) u = 0 ve tekil = True."""
    x, y, z = (np.atleast_1d(np.asarray(a, float)) for a in (x, y, z))
    if np.any(z > 0):
        raise OkadaHata("z > 0 (ortam dışı)")
    c = _dccon0(alpha, dip)
    sd, cd = c["sd"], c["cd"]
    u = np.zeros((12,) + x.shape)
    xi = [x - al1, x - al2]
    xi = [np.where(np.abs(a) < EPS, 0.0, a) for a in xi]
    tekil = np.zeros(x.shape, bool)
    for kaynak in ("gercek", "imge"):
        d = depth + z if kaynak == "gercek" else depth - z
        p = y * cd + d * sd
        q = y * sd - d * cd
        et = [p - aw1, p - aw2]
        q = np.where(np.abs(q) < EPS, 0.0, q)
        et = [np.where(np.abs(a) < EPS, 0.0, a) for a in et]
        tekil |= _kenar_tekil(xi, et, q)
        kxi, ket = _kxi_ket(xi, et, q)
        for k in range(2):
            for j in range(2):
                v = _dccon2(xi[j], et[k], q, c, kxi[k], ket[j])
                dua = _ua(v, c, disl1, disl2, disl3)
                du = np.empty_like(dua)
                if kaynak == "gercek":
                    for i in (0, 3, 6, 9):
                        du[i] = -dua[i]
                        du[i + 1] = -dua[i + 1] * cd + dua[i + 2] * sd
                        du[i + 2] = -dua[i + 1] * sd - dua[i + 2] * cd
                    du[9:12] = -du[9:12]
                else:
                    dub = _ub(v, c, disl1, disl2, disl3)
                    duc = _uc(v, c, z, disl1, disl2, disl3)
                    for i in (0, 3, 6, 9):
                        du[i] = dua[i] + dub[i] + z * duc[i]
                        du[i + 1] = ((dua[i + 1] + dub[i + 1] + z * duc[i + 1]) * cd
                                     - (dua[i + 2] + dub[i + 2] + z * duc[i + 2]) * sd)
                        du[i + 2] = ((dua[i + 1] + dub[i + 1] - z * duc[i + 1]) * sd
                                     + (dua[i + 2] + dub[i + 2] - z * duc[i + 2]) * cd)
                    du[9] += duc[0]
                    du[10] += duc[1] * cd - duc[2] * sd
                    du[11] += -duc[1] * sd - duc[2] * cd
                u += du if j + k != 1 else -du
    tekil |= ~np.all(np.isfinite(u), axis=0)
    u[:, tekil] = 0.0
    return u, tekil


# ================================================================== DC3D0 (nokta kaynak)
def _dccon1(x, y, d, c):
    x = np.where(np.abs(x) < EPS, 0.0, x)
    y = np.where(np.abs(y) < EPS, 0.0, y)
    d = np.where(np.abs(d) < EPS, 0.0, d)
    sd, cd = c["sd"], c["cd"]
    v = {}
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        p = y * cd + d * sd
        q = y * sd - d * cd
        s = p * sd + q * cd
        t = p * cd - q * sd
        xy, x2, y2, d2 = x * y, x * x, y * y, d * d
        r2 = x2 + y2 + d2
        r = np.sqrt(r2)
        r3 = r * r2
        r5 = r3 * r2
        r7 = r5 * r2
        a3 = 1 - 3 * x2 / r2
        a5 = 1 - 5 * x2 / r2
        b3 = 1 - 3 * y2 / r2
        c3 = 1 - 3 * d2 / r2
        qr = 3 * q / r5
        qrx = 5 * qr * x / r2
        uy = sd - 5 * y * q / r2
        uz = cd + 5 * d * q / r2
        vy = s - 5 * y * p * q / r2
        vz = t + 5 * d * p * q / r2
        wy = uy + sd
        wz = uz + cd
    v.update(x=x, y=y, d=d, p=p, q=q, s=s, t=t, xy=xy, x2=x2, y2=y2, d2=d2, r2=r2, r=r, r3=r3, r5=r5, r7=r7,
             a3=a3, a5=a5, b3=b3, c3=c3, qr=qr, qrx=qrx, uy=uy, uz=uz, vy=vy, vz=vz, wy=wy, wz=wz)
    return v


def _ua0(v, c, p1, p2, p3):
    g = v.__getitem__
    x, y, d, p, q, s, t, xy, x2 = g("x"), g("y"), g("d"), g("p"), g("q"), g("s"), g("t"), g("xy"), g("x2")
    r3, r5, a3, a5, qr, qrx = g("r3"), g("r5"), g("a3"), g("a5"), g("qr"), g("qrx")
    uy, uz, vy, vz, wy, wz = g("uy"), g("uz"), g("vy"), g("vz"), g("wy"), g("wz")
    a1, a2, sd, cd, s2d, c2d = c["alp1"], c["alp2"], c["sd"], c["cd"], c["s2d"], c["c2d"]
    u = np.zeros((12,) + np.shape(x))
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        if p1 != 0:
            du = [a1 * q / r3 + a2 * x2 * qr, a1 * x / r3 * sd + a2 * xy * qr, -a1 * x / r3 * cd + a2 * x * d * qr,
                  x * qr * (-a1 + a2 * (1 + a5)), a1 * a3 / r3 * sd + a2 * y * qr * a5,
                  -a1 * a3 / r3 * cd + a2 * d * qr * a5,
                  a1 * (sd / r3 - y * qr) + a2 * 3 * x2 / r5 * uy, 3 * x / r5 * (-a1 * y * sd + a2 * (y * uy + q)),
                  3 * x / r5 * (a1 * y * cd + a2 * d * uy),
                  a1 * (cd / r3 + d * qr) + a2 * 3 * x2 / r5 * uz, 3 * x / r5 * (a1 * d * sd + a2 * y * uz),
                  3 * x / r5 * (-a1 * d * cd + a2 * (d * uz - q))]
            u += p1 / PI2 * np.array(du)
        if p2 != 0:
            du = [a2 * x * p * qr, a1 * s / r3 + a2 * y * p * qr, -a1 * t / r3 + a2 * d * p * qr,
                  a2 * p * qr * a5, -a1 * 3 * x * s / r5 - a2 * y * p * qrx, a1 * 3 * x * t / r5 - a2 * d * p * qrx,
                  a2 * 3 * x / r5 * vy, a1 * (s2d / r3 - 3 * y * s / r5) + a2 * (3 * y / r5 * vy + p * qr),
                  -a1 * (c2d / r3 - 3 * y * t / r5) + a2 * 3 * d / r5 * vy,
                  a2 * 3 * x / r5 * vz, a1 * (c2d / r3 + 3 * d * s / r5) + a2 * 3 * y / r5 * vz,
                  a1 * (s2d / r3 - 3 * d * t / r5) + a2 * (3 * d / r5 * vz - p * qr)]
            u += p2 / PI2 * np.array(du)
        if p3 != 0:
            du = [a1 * x / r3 - a2 * x * q * qr, a1 * t / r3 - a2 * y * q * qr, a1 * s / r3 - a2 * d * q * qr,
                  a1 * a3 / r3 - a2 * q * qr * a5, -a1 * 3 * x * t / r5 + a2 * y * q * qrx,
                  -a1 * 3 * x * s / r5 + a2 * d * q * qrx,
                  -a1 * 3 * xy / r5 - a2 * x * qr * wy, a1 * (c2d / r3 - 3 * y * t / r5) - a2 * (y * wy + q) * qr,
                  a1 * (s2d / r3 - 3 * y * s / r5) - a2 * d * qr * wy,
                  a1 * 3 * x * d / r5 - a2 * x * qr * wz, -a1 * (s2d / r3 - 3 * d * t / r5) - a2 * y * qr * wz,
                  a1 * (c2d / r3 + 3 * d * s / r5) - a2 * (d * wz - q) * qr]
            u += p3 / PI2 * np.array(du)
    return u


def _ub0(v, c, z, p1, p2, p3):
    g = v.__getitem__
    x, y, d, p, q, xy, x2, y2, d2 = g("x"), g("y"), g("d"), g("p"), g("q"), g("xy"), g("x2"), g("y2"), g("d2")
    r, r2, r3, r5, a3, a5, qr, qrx = g("r"), g("r2"), g("r3"), g("r5"), g("a3"), g("a5"), g("qr"), g("qrx")
    uy, uz, vy, vz, wy, wz = g("uy"), g("uz"), g("vy"), g("vz"), g("wy"), g("wz")
    a3_, sd, sdcd, sdsd = c["alp3"], c["sd"], c["sdcd"], c["sdsd"]
    u = np.zeros((12,) + np.shape(x))
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        cc = d + z
        rd = np.where(d < 0, (x2 + y2) / (r - d), r + d)        # okuma 12: R² − D² = x² + y²
        d12 = 1.0 / (r * rd * rd)
        d32 = d12 * (2 * r + d) / r2
        d33 = d12 * (3 * r + d) / (r2 * rd)
        d53 = d12 * (8 * r2 + 9 * r * d + 3 * d2) / (r2 * r2 * rd)
        d54 = d12 * (5 * r2 + 4 * r * d + d2) / r3 * d12
        fi1 = y * (d12 - x2 * d33)
        fi2 = x * (d12 - y2 * d33)
        fi3 = x / r3 - fi2
        fi4 = -xy * d32
        fi5 = 1.0 / (r * rd) - x2 * d32
        fj1 = -3 * xy * (d33 - x2 * d54)
        fj2 = 1.0 / r3 - 3 * d12 + 3 * x2 * y2 * d54
        fj3 = a3 / r3 - fj2
        fj4 = -3 * xy / r5 - fj1
        fk1 = -y * (d32 - x2 * d53)
        fk2 = -x * (d32 - y2 * d53)
        fk3 = -3 * x * d / r5 - fk2
        if p1 != 0:
            du = [-x2 * qr - a3_ * fi1 * sd, -xy * qr - a3_ * fi2 * sd, -cc * x * qr - a3_ * fi4 * sd,
                  -x * qr * (1 + a5) - a3_ * fj1 * sd, -y * qr * a5 - a3_ * fj2 * sd, -cc * qr * a5 - a3_ * fk1 * sd,
                  -3 * x2 / r5 * uy - a3_ * fj2 * sd, -3 * xy / r5 * uy - x * qr - a3_ * fj4 * sd,
                  -3 * cc * x / r5 * uy - a3_ * fk2 * sd,
                  -3 * x2 / r5 * uz + a3_ * fk1 * sd, -3 * xy / r5 * uz + a3_ * fk2 * sd,
                  3 * x / r5 * (-cc * uz + a3_ * y * sd)]
            u += p1 / PI2 * np.array(du)
        if p2 != 0:
            du = [-x * p * qr + a3_ * fi3 * sdcd, -y * p * qr + a3_ * fi1 * sdcd, -cc * p * qr + a3_ * fi5 * sdcd,
                  -p * qr * a5 + a3_ * fj3 * sdcd, y * p * qrx + a3_ * fj1 * sdcd, cc * p * qrx + a3_ * fk3 * sdcd,
                  -3 * x / r5 * vy + a3_ * fj1 * sdcd, -3 * y / r5 * vy - p * qr + a3_ * fj2 * sdcd,
                  -3 * cc / r5 * vy + a3_ * fk1 * sdcd,
                  -3 * x / r5 * vz - a3_ * fk3 * sdcd, -3 * y / r5 * vz - a3_ * fk1 * sdcd,
                  -3 * cc / r5 * vz + a3_ * a3 / r3 * sdcd]
            u += p2 / PI2 * np.array(du)
        if p3 != 0:
            du = [x * q * qr - a3_ * fi3 * sdsd, y * q * qr - a3_ * fi1 * sdsd, cc * q * qr - a3_ * fi5 * sdsd,
                  q * qr * a5 - a3_ * fj3 * sdsd, -y * q * qrx - a3_ * fj1 * sdsd, -cc * q * qrx - a3_ * fk3 * sdsd,
                  x * qr * wy - a3_ * fj1 * sdsd, qr * (y * wy + q) - a3_ * fj2 * sdsd,
                  cc * qr * wy - a3_ * fk1 * sdsd,
                  x * qr * wz + a3_ * fk3 * sdsd, y * qr * wz + a3_ * fk1 * sdsd, cc * qr * wz - a3_ * a3 / r3 * sdsd]
            u += p3 / PI2 * np.array(du)
    return u


def _uc0(v, c, z, p1, p2, p3):
    g = v.__getitem__
    x, y, d, p, q, s, t, x2, y2, d2 = (g(k) for k in ("x", "y", "d", "p", "q", "s", "t", "x2", "y2", "d2"))
    r2, r3, r5, a3, a5, qr, qrx = g("r2"), g("r3"), g("r5"), g("a3"), g("a5"), g("qr"), g("qrx")
    a4, a5_ = c["alp4"], c["alp5"]
    sd, cd, sdcd, sdsd, s2d, c2d = c["sd"], c["cd"], c["sdcd"], c["sdsd"], c["s2d"], c["c2d"]
    u = np.zeros((12,) + np.shape(x))
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        cc = d + z
        q2 = q * q
        r7 = r5 * r2
        a7 = 1 - 7 * x2 / r2
        b5 = 1 - 5 * y2 / r2
        b7 = 1 - 7 * y2 / r2
        c5 = 1 - 5 * d2 / r2
        c7 = 1 - 7 * d2 / r2
        d7 = 2 - 7 * q2 / r2
        qr5 = 5 * q / r2
        qr7 = 7 * q / r2
        dr5 = 5 * d / r2
        if p1 != 0:
            du = [None] * 12
            du[0] = -a4 * a3 / r3 * cd + a5_ * cc * qr * a5
            du[1] = 3 * x / r5 * (a4 * y * cd + a5_ * cc * (sd - y * qr5))
            du[2] = 3 * x / r5 * (-a4 * y * sd + a5_ * cc * (cd + d * qr5))
            du[3] = a4 * 3 * x / r5 * (2 + a5) * cd - a5_ * cc * qrx * (2 + a7)
            du[4] = 3 / r5 * (a4 * y * a5 * cd + a5_ * cc * (a5 * sd - y * qr5 * a7))
            du[5] = 3 / r5 * (-a4 * y * a5 * sd + a5_ * cc * (a5 * cd + d * qr5 * a7))
            du[6] = du[4]
            du[7] = 3 * x / r5 * (a4 * b5 * cd - a5_ * 5 * cc / r2 * (2 * y * sd + q * b7))
            du[8] = 3 * x / r5 * (-a4 * b5 * sd + a5_ * 5 * cc / r2 * (d * b7 * sd - y * c7 * cd))
            du[9] = 3 / r5 * (-a4 * d * a5 * cd + a5_ * cc * (a5 * cd + d * qr5 * a7))
            du[10] = 15 * x / r7 * (a4 * y * d * cd + a5_ * cc * (d * b7 * sd - y * c7 * cd))
            du[11] = 15 * x / r7 * (-a4 * y * d * sd + a5_ * cc * (2 * d * cd - q * c7))
            u += p1 / PI2 * np.array(du)
        if p2 != 0:
            du = [None] * 12
            du[0] = a4 * 3 * x * t / r5 - a5_ * cc * p * qrx
            du[1] = -a4 / r3 * (c2d - 3 * y * t / r2) + a5_ * 3 * cc / r5 * (s - y * p * qr5)
            du[2] = -a4 * a3 / r3 * sdcd + a5_ * 3 * cc / r5 * (t + d * p * qr5)
            du[3] = a4 * 3 * t / r5 * a5 - a5_ * 5 * cc * p * qr / r2 * a7
            du[4] = 3 * x / r5 * (a4 * (c2d - 5 * y * t / r2) - a5_ * 5 * cc / r2 * (s - y * p * qr7))
            du[5] = 3 * x / r5 * (a4 * (2 + a5) * sdcd - a5_ * 5 * cc / r2 * (t + d * p * qr7))
            du[6] = du[4]
            du[7] = 3 / r5 * (a4 * (2 * y * c2d + t * b5) + a5_ * cc * (s2d - 10 * y * s / r2 - p * qr5 * b7))
            du[8] = 3 / r5 * (a4 * y * a5 * sdcd - a5_ * cc * ((3 + a5) * c2d + y * p * dr5 * qr7))
            du[9] = 3 * x / r5 * (-a4 * (s2d - t * dr5) - a5_ * 5 * cc / r2 * (t + d * p * qr7))
            du[10] = 3 / r5 * (-a4 * (d * b5 * c2d + y * c5 * s2d) - a5_ * cc * ((3 + a5) * c2d + y * p * dr5 * qr7))
            du[11] = 3 / r5 * (-a4 * d * a5 * sdcd - a5_ * cc * (s2d - 10 * d * t / r2 + p * qr5 * c7))
            u += p2 / PI2 * np.array(du)
        if p3 != 0:
            du = [None] * 12
            du[0] = 3 * x / r5 * (-a4 * s + a5_ * (cc * q * qr5 - z))
            du[1] = a4 / r3 * (s2d - 3 * y * s / r2) + a5_ * 3 / r5 * (cc * (t - y + y * q * qr5) - y * z)
            du[2] = -a4 / r3 * (1 - a3 * sdsd) - a5_ * 3 / r5 * (cc * (s - d + d * q * qr5) - d * z)
            du[3] = -a4 * 3 * s / r5 * a5 + a5_ * (cc * qr * qr5 * a7 - 3 * z / r5 * a5)
            du[4] = 3 * x / r5 * (-a4 * (s2d - 5 * y * s / r2) - a5_ * 5 / r2 * (cc * (t - y + y * q * qr7) - y * z))
            du[5] = 3 * x / r5 * (a4 * (1 - (2 + a5) * sdsd) + a5_ * 5 / r2 * (cc * (s - d + d * q * qr7) - d * z))
            du[6] = du[4]
            du[7] = 3 / r5 * (-a4 * (2 * y * s2d + s * b5)
                              - a5_ * (cc * (2 * sdsd + 10 * y * (t - y) / r2 - q * qr5 * b7) + z * b5))
            du[8] = 3 / r5 * (a4 * y * (1 - a5 * sdsd) + a5_ * (cc * (3 + a5) * s2d - y * dr5 * (cc * d7 + z)))
            du[9] = 3 * x / r5 * (-a4 * (c2d + s * dr5) + a5_ * (5 * cc / r2 * (s - d + d * q * qr7) - 1 - z * dr5))
            # Kodlayıcı okuması 2: bu terimin (UC0, açılma, UYZ) bellekten yazılan biçimi ∂/∂z tutarlılığını
            # bozuyordu; (α − (1 − α)) katsayısı UC0[9:12] = ∂(UC0 yer değiştirmesi)/∂z koşulundan (sayısal türevle
            # 1e-10 içinde) belirlendi. Yer değiştirme terimleri değişmedi.
            du[10] = 3 / r5 * ((a5_ - a4) * (d * b5 * s2d - y * c5 * c2d)
                               + a5_ * (cc * ((3 + a5) * s2d - y * dr5 * d7) - y * (1 + z * dr5)))
            du[11] = 3 / r5 * (-a4 * d * (1 - a5 * sdsd)
                               - a5_ * (cc * (c2d + 10 * d * (s - d) / r2 - q * qr5 * c7) + z * (1 + c5)))
            u += p3 / PI2 * np.array(du)
    return u


def dc3d0(alpha, x, y, z, depth, dip, pot1, pot2, pot3):
    """Okada (1992) DC3D0 nokta kaynak (POT = moment/μ = kayma × alan). Dönüş (u (12, N), tekil (N,))."""
    x, y, z = (np.atleast_1d(np.asarray(a, float)) for a in (x, y, z))
    if np.any(z > 0):
        raise OkadaHata("z > 0 (ortam dışı)")
    c = _dccon0(alpha, dip)
    u = np.zeros((12,) + x.shape)
    v = _dccon1(x, y, depth + z, c)
    tekil = v["r"] == 0
    ua = _ua0(v, c, pot1, pot2, pot3)
    u[:9] -= ua[:9]
    u[9:] += ua[9:]
    v = _dccon1(x, y, depth - z, c)
    ua = _ua0(v, c, pot1, pot2, pot3)
    ub = _ub0(v, c, z, pot1, pot2, pot3)
    uc = _uc0(v, c, z, pot1, pot2, pot3)
    du = ua + ub + z * uc
    du[9:] += uc[:3]
    u += du
    tekil |= ~np.all(np.isfinite(u), axis=0)
    u[:, tekil] = 0.0
    return u, tekil


# ================================================================== gerilme ve dönüşümler
def gradyan(u12):
    """(12, N) -> G (N, 3, 3), G[i, j] = ∂u_i/∂x_j."""
    G = np.empty(u12.shape[1:] + (3, 3))
    G[..., :, 0] = np.moveaxis(u12[3:6], 0, -1)
    G[..., :, 1] = np.moveaxis(u12[6:9], 0, -1)
    G[..., :, 2] = np.moveaxis(u12[9:12], 0, -1)
    return G


def gerilme_tensoru(G, mu=MU_PA, lam=LAM_PA):
    e = 0.5 * (G + np.swapaxes(G, -1, -2))
    tr = np.trace(e, axis1=-2, axis2=-1)
    return lam * tr[..., None, None] * np.eye(3) + 2 * mu * e


def eksenler(dogrultu):
    """Okada yerel eksenlerinin DKY (doğu-kuzey-yukarı) birim vektörleri: satırlar x (doğrultu), y (sol), z."""
    f = math.radians(dogrultu)
    return np.array([[math.sin(f), math.cos(f), 0.0], [-math.cos(f), math.sin(f), 0.0], [0.0, 0.0, 1.0]])


def alici_vektorleri(dogrultu, egim, rake):
    """§3.3 madde 9: n̂ tavan bloğuna doğru (yukarı normal), kayma cos λ ŝ − sin λ d̂ (DKY)."""
    f, d, l = math.radians(dogrultu), math.radians(egim), math.radians(rake)
    s = np.array([math.sin(f), math.cos(f), 0.0])
    dd = np.array([math.cos(d) * math.cos(f), -math.cos(d) * math.sin(f), -math.sin(d)])
    n = np.array([math.sin(d) * math.cos(f), -math.sin(d) * math.sin(f), math.cos(d)])
    return n, math.cos(l) * s - math.sin(l) * dd


def dcff(sigma_enu, dogrultu, egim, rake, mu_s=MU_SURT):
    """ΔCFF = Δτ + μ' Δσ_n (çekme pozitif). sigma (…, 3, 3) DKY. Dönüş (Δτ, Δσ_n, ΔCFF), sigma birimiyle."""
    n, k = alici_vektorleri(dogrultu, egim, rake)
    t = sigma_enu @ n
    tau = t @ k
    sn = t @ n
    return tau, sn, tau + mu_s * sn


def altfay_gerilme(af, E, N, U):
    """Tek alt fayın DKY noktalarındaki (km; altfay referansına göre değil, ortak düzlemde) gerilmesi, kPa.
    af: dict(e, n (km, izdüşüm düzleminde alt fay referans noktası), derinlik (km, referans), uzunluk, genislik,
    dogrultu, egim, rake, kayma (m), aw1, aw2, al1, al2)."""
    R = eksenler(af["dogrultu"])
    dx, dy = E - af["e"], N - af["n"]
    x = R[0, 0] * dx + R[0, 1] * dy
    y = R[1, 0] * dx + R[1, 1] * dy
    lam = math.radians(af["rake"])
    u, tek = dc3d(ALFA, x, y, U, af["derinlik"], af["egim"], af["al1"], af["al2"], af["aw1"], af["aw2"],
                  af["kayma"] * math.cos(lam), af["kayma"] * math.sin(lam), 0.0)
    G = gradyan(u) * 1e-3                       # m / km -> boyutsuz
    S = gerilme_tensoru(G) / 1e3                # Pa -> kPa
    S = np.einsum("ki,...kl,lj->...ij", R, S, R)   # yerel -> DKY: Rᵀ S R
    return S, tek


# ================================================================== izdüşüm ve ızgara
def aeqd_ileri(la0, lo0, la, lo):
    """Azimutal eşit uzaklık (küre, R 6371 km): merkez (la0, lo0) -> (x doğu, y kuzey) km."""
    p0, l0 = math.radians(la0), math.radians(lo0)
    p, l = np.radians(np.asarray(la, float)), np.radians(np.asarray(lo, float))
    c = np.sin(p0) * np.sin(p) + np.cos(p0) * np.cos(p) * np.cos(l - l0)
    ang = np.arccos(np.clip(c, -1, 1))
    az = np.arctan2(np.cos(p) * np.sin(l - l0), np.cos(p0) * np.sin(p) - np.sin(p0) * np.cos(p) * np.cos(l - l0))
    rr = R_DUNYA * ang
    return rr * np.sin(az), rr * np.cos(az)


def aeqd_geri(la0, lo0, x, y):
    p0, l0 = math.radians(la0), math.radians(lo0)
    x, y = np.asarray(x, float), np.asarray(y, float)
    ang = np.hypot(x, y) / R_DUNYA
    az = np.arctan2(x, y)
    p = np.arcsin(np.clip(np.sin(p0) * np.cos(ang) + np.cos(p0) * np.sin(ang) * np.cos(az), -1, 1))
    l = l0 + np.arctan2(np.sin(az) * np.sin(ang) * np.cos(p0), np.cos(ang) - np.sin(p0) * np.sin(p))
    return np.degrees(p), (np.degrees(l) + 540.0) % 360.0 - 180.0


def hucre_indeksi(x, y, h=HUCRE_KM):
    """Kodlayıcı okuması 7: dış merkez (0, 0) bir hücrenin merkezidir; hücre (i, j) merkezi (i h, j h)."""
    return np.floor(np.asarray(x) / h + 0.5).astype(np.int64), np.floor(np.asarray(y) / h + 0.5).astype(np.int64)


def izdusum_dogrultusu(la0, lo0, la, lo, dogrultu):
    """Coğrafi doğrultunun izdüşüm düzlemindeki karşılığı (kodlayıcı okuması 8): alt fay merkezinden doğrultu
    yönünde 1 km ötedeki nokta izdüşürülür."""
    f = math.radians(dogrultu)
    d = 1.0 / R_DUNYA
    p, l = math.radians(la), math.radians(lo)
    p2 = math.asin(math.sin(p) * math.cos(d) + math.cos(p) * math.sin(d) * math.cos(f))
    l2 = l + math.atan2(math.sin(f) * math.sin(d) * math.cos(p), math.cos(d) - math.sin(p) * math.sin(p2))
    x1, y1 = aeqd_ileri(la0, lo0, la, lo)
    x2, y2 = aeqd_ileri(la0, lo0, math.degrees(p2), math.degrees(l2))
    return math.degrees(math.atan2(float(x2 - x1), float(y2 - y1))) % 360.0


def altfaylari_izdus(altfaylar, la0, lo0):
    """FFM alt faylarını (tr6a_ffm biçimi) izdüşüm düzlemine taşır; Okada referansını kurar."""
    out = []
    for a in altfaylar:
        e, n = aeqd_ileri(la0, lo0, a["enlem"], a["boylam"])
        dg = izdusum_dogrultusu(la0, lo0, a["enlem"], a["boylam"], a["dogrultu"])
        L, W = a["uzunluk"], a["genislik"]
        if a["koordinat"] == "merkez":
            aw1, aw2 = -W / 2, W / 2
        elif a["koordinat"] == "ust_kenar":
            aw1, aw2 = -W, 0.0
        else:
            raise OkadaHata(f"alt fay koordinat anlamı bilinmiyor: {a['koordinat']}")
        out.append(dict(e=float(e), n=float(n), derinlik=a["derinlik"], uzunluk=L, genislik=W, dogrultu=dg,
                        egim=a["egim"], rake=a["rake"], kayma=a["kayma"], al1=-L / 2, al2=L / 2, aw1=aw1, aw2=aw2,
                        uye=a.get("uye")))
    return out


def dikdortgen_kose(af):
    R = eksenler(af["dogrultu"])
    sd, cd = math.sin(math.radians(af["egim"])), math.cos(math.radians(af["egim"]))
    k = []
    for xi in (af["al1"], af["al2"]):
        for et in (af["aw1"], af["aw2"]):
            yl, zl = et * cd, -af["derinlik"] + et * sd
            e = af["e"] + xi * R[0, 0] + yl * R[1, 0]
            n = af["n"] + xi * R[0, 1] + yl * R[1, 1]
            k.append((e, n, zl))
    return np.array(k)


def dikdortgene_uzaklik(af, E, N, U):
    """Noktaların (km) alt fay dikdörtgenine 3B uzaklığı."""
    R = eksenler(af["dogrultu"])
    sd, cd = math.sin(math.radians(af["egim"])), math.cos(math.radians(af["egim"]))
    dx, dy, dz = E - af["e"], N - af["n"], U + af["derinlik"]
    xl = R[0, 0] * dx + R[0, 1] * dy
    yl = R[1, 0] * dx + R[1, 1] * dy
    et = yl * cd + dz * sd                       # düzlem içi eğim boyu koordinatı
    nn = -yl * sd + dz * cd                      # düzleme dik
    xi_k = np.clip(xl, af["al1"], af["al2"])
    et_k = np.clip(et, af["aw1"], af["aw2"])
    return np.sqrt((xl - xi_k) ** 2 + (et - et_k) ** 2 + nn ** 2)


def kirik_izi(altfaylar_izd, pay=IZ_PAY, adim=IZ_ADIM_KM):
    """§3.4: üye başına, kayması en büyük alt fay kaymasının ≥ %10'u olan alt fayların yüzey izdüşümü, ≤ 2 km aralıklı
    nokta örneklemesi; üyeler birleştirilir. Dönüş (M, 2) km."""
    noktalar = []
    uyeler = sorted({a.get("uye") for a in altfaylar_izd}, key=str)
    for u in uyeler:
        af_u = [a for a in altfaylar_izd if a.get("uye") == u]
        smax = max(a["kayma"] for a in af_u)
        for a in af_u:
            if a["kayma"] < pay * smax or a["kayma"] <= 0:
                continue
            k = dikdortgen_kose(a)
            o, ex, ey = k[0, :2], k[2, :2] - k[0, :2], k[1, :2] - k[0, :2]
            nx = max(1, int(math.ceil(np.hypot(*ex) / adim)))
            ny = max(1, int(math.ceil(np.hypot(*ey) / adim)))
            ua, ub = np.meshgrid(np.linspace(0, 1, nx + 1), np.linspace(0, 1, ny + 1))
            noktalar.append(o + ua.reshape(-1, 1) * ex + ub.reshape(-1, 1) * ey)
    return np.vstack(noktalar) if noktalar else np.zeros((0, 2))


def en_yakin_uzaklik(px, py, iz, parca=4096):
    """Noktaların iz nokta kümesine yatay uzaklığı (km)."""
    px, py = np.asarray(px, float).ravel(), np.asarray(py, float).ravel()
    out = np.full(px.shape, np.inf)
    for i in range(0, len(px), parca):
        a, b = px[i:i + parca, None], py[i:i + parca, None]
        for j in range(0, len(iz), 4096):
            d = np.hypot(a - iz[None, j:j + 4096, 0], b - iz[None, j:j + 4096, 1]).min(axis=1)
            out[i:i + parca] = np.minimum(out[i:i + parca], d)
    return out


def izgara_hesapla(altfaylar_izd, L_km, alicilar, r_ic=20.0, derinlik=HESAP_DERINLIK_KM, log=None):
    """§3.3-§3.4: 10 km ızgara, r_k, bölge, tekil yakın alan ve her alıcı için ΔCFF (kPa).
    alicilar: {ad: (doğrultu, eğim, rake)}. r_ic: hesaplanan en küçük r_k (D3a için 5 km verilir).
    Dönüş dict: i, j, x, y, r_k, tekil (bool), dcff {ad: dizi}, iz (noktalar)."""
    iz = kirik_izi(altfaylar_izd)
    if len(iz) == 0:
        raise OkadaHata("kırık izi boş")
    R = 2 * L_km + float(np.hypot(iz[:, 0], iz[:, 1]).max()) + HUCRE_KM
    n = int(math.ceil(R / HUCRE_KM))
    ii, jj = np.meshgrid(np.arange(-n, n + 1), np.arange(-n, n + 1), indexing="ij")
    ii, jj = ii.ravel(), jj.ravel()
    x, y = ii * HUCRE_KM, jj * HUCRE_KM
    on = np.hypot(x, y) <= R
    ii, jj, x, y = ii[on], jj[on], x[on], y[on]
    rk = en_yakin_uzaklik(x, y, iz)
    sec = (rk >= r_ic) & (rk <= 2 * L_km)
    ii, jj, x, y, rk = ii[sec], jj[sec], x[sec], y[sec], rk[sec]
    U = np.full(x.shape, -derinlik)
    tekil = np.zeros(x.shape, bool)
    S = np.zeros(x.shape + (3, 3))
    for k, a in enumerate(altfaylar_izd):
        if a["kayma"] <= 0:
            continue
        tekil |= dikdortgene_uzaklik(a, x, y, U) < TEKIL_YAKIN_KM
        s, tek = altfay_gerilme(a, x, y, U)
        tekil |= tek
        S += s
        if log and k % 50 == 0:
            log(f"  okada {k}/{len(altfaylar_izd)}")
    if not np.all(np.isfinite(S)):
        raise OkadaHata("ızgarada sonlu olmayan gerilme")
    dc = {ad: dcff(S, *ab)[2] for ad, ab in alicilar.items()}
    return dict(i=ii, j=jj, x=x, y=y, r_k=rk, tekil=tekil, dcff=dc, iz=iz, sigma=S)


# ================================================================== alıcı düzlem (§3.3 karar 6)
def tensor_dky(mrr, mtt, mpp, mrt, mrp, mtp):
    """r yukarı, t güney, p doğu -> DKY (doğu, kuzey, yukarı) moment tensörü."""
    return np.array([[mpp, -mtp, mrp], [-mtp, mtt, -mrt], [mrp, -mrt, mrr]], float)


def skaler_moment(mrr, mtt, mpp, mrt, mrp, mtp):
    return math.sqrt((mrr ** 2 + mtt ** 2 + mpp ** 2 + 2 * (mrt ** 2 + mrp ** 2 + mtp ** 2)) / 2)


def normal_kaymadan(n, s):
    """(n̂, kayma) -> (doğrultu, eğim, rake); n̂ yukarı çevrilir (kayma da)."""
    n, s = np.asarray(n, float) / np.linalg.norm(n), np.asarray(s, float) / np.linalg.norm(s)
    if n[2] < 0:
        n, s = -n, -s
    egim = math.degrees(math.acos(min(1.0, max(-1.0, n[2]))))
    dog = math.degrees(math.atan2(-n[1], n[0])) % 360.0
    if egim < 1e-9:
        dog = 0.0
    f, dd = math.radians(dog), math.radians(egim)
    sv = np.array([math.sin(f), math.cos(f), 0.0])
    dv = np.array([math.cos(dd) * math.cos(f), -math.cos(dd) * math.sin(f), -math.sin(dd)])
    rake = math.degrees(math.atan2(-float(s @ dv), float(s @ sv)))
    return dog, egim, rake


def dugum_duzlemleri(M):
    """Medyan tensör (iz çıkarılmış) -> (düzlemler [(n, s, (doğrultu, eğim, rake))×2], çift kuvvet payı)."""
    M = np.asarray(M, float)
    M = M - np.trace(M) / 3 * np.eye(3)
    w, V = np.linalg.eigh(M)
    o = np.argsort(w)[::-1]
    w, V = w[o], V[:, o]
    T, P = V[:, 0], V[:, 2]
    dc_payi = 1 - 2 * abs(w[1]) / max(abs(w[0]), abs(w[2]))
    n1, n2 = (T + P) / math.sqrt(2), (T - P) / math.sqrt(2)
    return [(n1, n2, normal_kaymadan(n1, n2)), (n2, n1, normal_kaymadan(n2, n1))], float(dc_payi)


def ffm_ortalama_duzlem(altfaylar):
    """Moment ağırlıklı ortalama düzlem: yukarı normallerin ağırlıklı vektör ortalaması (doğrultu ve eğim) ve
    (cos λ, sin λ) ağırlıklı vektör ortalaması (rake). Ağırlık alt fay momenti (yoksa kayma × alan)."""
    nv, rv, = np.zeros(3), np.zeros(2)
    for a in altfaylar:
        w = a.get("moment") or a["kayma"] * a["uzunluk"] * a["genislik"]
        n, _ = alici_vektorleri(a["dogrultu"], a["egim"], a["rake"])
        nv += w * n
        rv += w * np.array([math.cos(math.radians(a["rake"])), math.sin(math.radians(a["rake"]))])
    nv /= np.linalg.norm(nv)
    dog, egim, _ = normal_kaymadan(nv, np.array([0.0, 0.0, 1.0]) if abs(nv[2]) < 1 else np.array([1.0, 0, 0]))
    return dog, egim, math.degrees(math.atan2(rv[1], rv[0])), nv


def yardimci_duzlem(dogrultu, egim, rake):
    n, s = alici_vektorleri(dogrultu, egim, rake)
    return normal_kaymadan(s, n)


def alici_sec(tensorler, altfaylar, en_az=5):
    """§3.3 karar 6. tensorler: [(mrr, mtt, mpp, mrt, mrp, mtp)], tercihli tensörler. Dönüş dict."""
    dog0, egim0, rake0, nff = ffm_ortalama_duzlem(altfaylar)
    sonuc = dict(tensor_sayisi=len(tensorler), cift_kuvvet_payi=None)
    if len(tensorler) >= en_az:
        A = np.array([np.array(t, float) / skaler_moment(*t) for t in tensorler])
        med = np.median(A, axis=0)
        M = tensor_dky(*med)
        dz, dc = dugum_duzlemleri(M)
        sonuc["cift_kuvvet_payi"] = round(dc, 6)
        if dc >= 0.5:
            k = max(range(2), key=lambda i: abs(float(dz[i][0] @ nff)))
            sonuc.update(kaynak="medyan", alici=dz[k][2], ikinci=dz[1 - k][2])
            return sonuc
        sonuc["not"] = "çift kuvvet payı < 0,5: medyan tensör kullanılmadı"
    sonuc.update(kaynak="ana şok", alici=(dog0, egim0, rake0), ikinci=yardimci_duzlem(dog0, egim0, rake0))
    return sonuc


# ================================================================== doğrulama (§3.3 sınamaları 1-9, tekil)
def _rastgele_noktalar(rng, n, af, derin_max=30.0, kutu=40.0, uzak=0.3):
    out = []
    while sum(len(o) for o in out) < n:
        x = rng.uniform(-kutu, kutu, 4 * n)
        y = rng.uniform(-kutu, kutu, 4 * n)
        z = -rng.uniform(0.2, derin_max, 4 * n)
        d = _yerel_uzaklik(af, x, y, z)
        ok = d > uzak
        out.append(np.stack([x[ok], y[ok], z[ok]], 1))
    return np.vstack(out)[:n]


def _goreli(a, b, genel=False):
    """Göreli fark: yer değiştirme (3) ve türevler (9) ayrı; nokta başına (genel=False) ya da nokta kümesi üzerinden
    en büyük mutlak değere göre (genel=True). İki grubun büyüğü döner."""
    out = 0.0
    for sl in (slice(0, 3), slice(3, 12)):
        d, r = np.abs(a[sl] - b[sl]), np.abs(b[sl])
        out = max(out, float((d.max(axis=0) / r.max(axis=0)).max()) if not genel else float(d.max() / r.max()))
    return out


def _yerel_uzaklik(af, x, y, z):
    sd, cd = math.sin(math.radians(af["dip"])), math.cos(math.radians(af["dip"]))
    dz = z + af["depth"]
    et = y * cd + dz * sd
    nn = -y * sd + dz * cd
    return np.sqrt((x - np.clip(x, af["al1"], af["al2"])) ** 2 + (et - np.clip(et, af["aw1"], af["aw2"])) ** 2
                   + nn ** 2)


def _u(af, x, y, z, disl):
    return dc3d(ALFA, x, y, z, af["depth"], af["dip"], af["al1"], af["al2"], af["aw1"], af["aw2"], *disl)


def _sigma_yerel(af, x, y, z, disl):
    u, t = _u(af, x, y, z, disl)
    return gerilme_tensoru(gradyan(u) * 1e-3), u, t


def dogrulama(tohum=20261112, n_nokta=200, log=None):
    """§3.3 doğrulama listesinin tamamı. Dönüş dict(gecti: bool, sinamalar: {...}). Her sınama en büyük göreli
    sapmayı ve eşiği yazar."""
    rng = np.random.default_rng(tohum)
    out = {}

    def kayit(ad, deger, esik, ek=None):
        g = bool(deger <= esik)
        r = dict(deger=float(deger), esik=esik, gecti=g)
        if ek:
            r.update(ek)
        out[ad] = r
        if log:
            log(f"  {ad}: {deger:.3e} (eşik {esik:g}) {'GEÇTİ' if g else 'GEÇMEDİ'}")

    turler = {"dogrultu": (1.0, 0.0, 0.0), "egim": (0.0, 1.0, 0.0), "acilma": (0.0, 0.0, 1.0)}
    W, L = 10.0, 16.0
    s1 = s2 = s3 = s4 = s5 = s5u = s6 = s7 = s3r = s6r = s5u_g = s5u40_g = 0.0
    for dip in (30.0, 70.0, 90.0):
        af = dict(depth=12.0, dip=dip, al1=-L / 2, al2=L / 2, aw1=-W / 2, aw2=W / 2)
        for tur, disl in turler.items():
            P = _rastgele_noktalar(rng, n_nokta, af)
            x, y, z = P.T
            # 1. yüzeyde çekme sıfır
            S, _, _ = _sigma_yerel(af, x, y, np.zeros_like(z), disl)
            s1 = max(s1, float(np.max(np.abs(S[:, [0, 1, 2], [2, 2, 2]]).max(axis=1) /
                                      np.abs(S).reshape(len(x), -1).max(axis=1))))
            # 2. denge: merkezi farkla div σ
            h = 5e-4
            div = np.zeros((len(x), 3))
            grad_olcek = np.zeros(len(x))
            for k, (ex, ey, ez) in enumerate(((h, 0, 0), (0, h, 0), (0, 0, h))):
                Sp, _, _ = _sigma_yerel(af, x + ex, y + ey, z + ez, disl)
                Sm, _, _ = _sigma_yerel(af, x - ex, y - ey, z - ez, disl)
                dS = (Sp - Sm) / (2 * h * 1e3)          # Pa / m
                div += dS[:, :, k]
                grad_olcek = np.maximum(grad_olcek, np.abs(dS).reshape(len(x), -1).max(axis=1))
            s2 = max(s2, float(np.max(np.abs(div).max(axis=1) / grad_olcek)))
            # 4. analitik türev ve sayısal türev
            u0, _ = _u(af, x, y, z, disl)
            h4 = 1e-4
            num = np.zeros((9, len(x)))
            for k, (ex, ey, ez) in enumerate(((h4, 0, 0), (0, h4, 0), (0, 0, h4))):
                up, _ = _u(af, x + ex, y + ey, z + ez, disl)
                um, _ = _u(af, x - ex, y - ey, z - ez, disl)
                num[3 * k:3 * k + 3] = (up[:3] - um[:3]) / (2 * h4)
            ana = u0[3:12]
            s4 = max(s4, float(np.max(np.abs(num - ana).max(axis=0) / np.abs(ana).max(axis=0))))
            # 3. fay düzleminin iki yanında süreksizlik = birim kayma (yerel x, eğim yukarı, normal)
            sd, cd = math.sin(math.radians(dip)), math.cos(math.radians(dip))
            xi = rng.uniform(af["al1"] + 0.1 * L, af["al2"] - 0.1 * L, n_nokta)
            et = rng.uniform(af["aw1"] + 0.1 * W, af["aw2"] - 0.1 * W, n_nokta)
            nvec = np.array([0.0, -sd, cd])          # yukarı normal (tavan bloğu)
            yd, zd = et * cd, -af["depth"] + et * sd
            e = 1e-6 * W
            beklenen = disl[0] * np.array([1.0, 0, 0]) + disl[1] * np.array([0.0, cd, sd]) + disl[2] * nvec

            def fark(xx, yy, zz, ee):
                up, _ = _u(af, xx, yy + ee * nvec[1], np.minimum(zz + ee * nvec[2], 0.0), disl)
                um, _ = _u(af, xx, yy - ee * nvec[1], zz - ee * nvec[2], disl)
                return (up[:3] - um[:3]).T
            f1, f2 = fark(xi, yd, zd, e), fark(xi, yd, zd, 2 * e)
            s3 = max(s3, float(np.max(np.abs(f1 - beklenen))))
            s3r = max(s3r, float(np.max(np.abs(2 * f1 - f2 - beklenen))))
            # 6. fay dışı süreklilik (düzlem uzantısı, kenardan ≥ 0,05 W)
            xi6 = np.concatenate([rng.uniform(af["al2"] + 0.05 * W, af["al2"] + 2 * W, n_nokta // 2),
                                  rng.uniform(af["al1"] - 2 * W, af["al1"] - 0.05 * W, n_nokta - n_nokta // 2)])
            et6 = rng.uniform(af["aw1"], af["aw2"], n_nokta)
            yd6, zd6 = et6 * cd, -af["depth"] + et6 * sd
            f1, f2 = fark(xi6, yd6, zd6, e), fark(xi6, yd6, zd6, 2 * e)
            s6 = max(s6, float(np.max(np.abs(f1))))
            s6r = max(s6r, float(np.max(np.abs(2 * f1 - f2))))
            # 7. üst üste binme: dört eş parça
            parca = np.zeros_like(u0)
            for a1, a2 in ((af["al1"], 0.0), (0.0, af["al2"])):
                for w1, w2 in ((af["aw1"], 0.0), (0.0, af["aw2"])):
                    up, _ = dc3d(ALFA, x, y, z, af["depth"], dip, a1, a2, w1, w2, *disl)
                    parca += up
            S_tek = gerilme_tensoru(gradyan(u0))
            S_par = gerilme_tensoru(gradyan(parca))
            g7 = max(float(np.max(np.abs(parca[:3] - u0[:3])) / np.abs(u0[:3]).max()),
                     float(np.max(np.abs(S_par - S_tek)) / np.abs(S_tek).max()))
            s7 = max(s7, g7)
            # 5. nokta kaynak sınırı (0,01 km; noktalar kaynaktan ≥ 1 km, okuma 4) ve uzak alan (20 L ≤ r ≤ 60 L)
            hk = 0.01
            P5 = _rastgele_noktalar(rng, n_nokta, dict(depth=12.0, dip=dip, al1=0, al2=0, aw1=0, aw2=0), uzak=1.0)
            x5, y5, z5 = P5.T
            ufs, _ = dc3d(ALFA, x5, y5, z5, af["depth"], dip, -hk / 2, hk / 2, -hk / 2, hk / 2, *disl)
            ups, _ = dc3d0(ALFA, x5, y5, z5, af["depth"], dip, *[dd * hk * hk for dd in disl])
            s5 = max(s5, _goreli(ufs, ups))
            for carpan, ad in ((20, "20"), (40, "40")):
                rr = rng.uniform(carpan * L, 3 * carpan * L if carpan == 20 else carpan * L * 1.01, n_nokta)
                th = rng.uniform(0, 2 * math.pi, n_nokta)
                xu, yu, zu = rr * np.cos(th), rr * np.sin(th), -rng.uniform(0, 30.0, n_nokta)
                uf, _ = _u(af, xu, yu, zu, disl)
                upn, _ = dc3d0(ALFA, xu, yu, zu, af["depth"], dip, *[dd * L * W for dd in disl])
                g = _goreli(uf, upn, genel=True)
                if ad == "20":
                    s5u = max(s5u, _goreli(uf, upn))
                    s5u_g = max(s5u_g, g)
                else:
                    s5u40_g = max(s5u40_g, g)
    # tanı (okuma 6): uzak alanda sonlu kaynak, alanı 20 × 20 nokta kaynağa bölünmüş DC3D0 toplamıyla karşılaştırılır
    tani_int = 0.0
    for dip in (30.0, 90.0):
        for disl in turler.values():
            rr = rng.uniform(20 * L, 60 * L, 60)
            th = rng.uniform(0, 2 * math.pi, 60)
            xu, yu, zu = rr * np.cos(th), rr * np.sin(th), -rng.uniform(0, 30.0, 60)
            uf, _ = dc3d(ALFA, xu, yu, zu, 12.0, dip, -L / 2, L / 2, -W / 2, W / 2, *disl)
            acc = np.zeros_like(uf)
            sd, cd = math.sin(math.radians(dip)), math.cos(math.radians(dip))
            m = 20
            for xi in (np.arange(m) + 0.5) / m * L - L / 2:
                for et in (np.arange(m) + 0.5) / m * W - W / 2:
                    u, _ = dc3d0(ALFA, xu - xi, yu - et * cd, zu, 12.0 - et * sd, dip,
                                 *[dd * L * W / m / m for dd in disl])
                    acc += u
            tani_int = max(tani_int, _goreli(uf, acc, genel=True))
    out["bilgi_uzak_alan_nokta_integrali"] = dict(deger=tani_int, not_="20×20 nokta kaynak toplamı; orta nokta "
                                                  "kuralı hatası ≈ (1/20)² mertebesinde dört kutup terimi")
    kayit("1_yuzey_cekme", s1, 1e-8)
    kayit("2_denge", s2, 1e-5)
    kayit("3_kayma_sureksizligi", s3, 1e-6,
          dict(tani_richardson=s3r, not_="harfiyen ölçüt ±ε farkının doğrusal terimini (2ε ∂u/∂n) taşır; "
               "okuma 5: 2Δ(ε) − Δ(2ε) bu terimi kaldırır (Ek 1 kararı)"))
    kayit("4_sayisal_turev", s4, 1e-6)
    kayit("5_nokta_kaynak_001km", s5, 1e-4)
    kayit("5_uzak_alan_20L", s5u, 1e-3,
          dict(tani_genel_normal_20_60L=s5u_g, tani_genel_normal_40L=s5u40_g,
               not_="sonlu boyut (dört kutup) terimi (L/r)² ile azalır; okuma 6 (Ek 1 kararı)"))
    kayit("6_fay_disi_sureklilik", s6, 1e-6, dict(tani_richardson=s6r))
    kayit("7_ust_uste_binme", s7, 1e-10)
    # nokta kaynağın kendi tutarlılığı (bilgi; 5. sınamanın bağımsızlığı için): yüzey çekmesi ve sayısal türev
    af0 = dict(depth=12.0, dip=50.0, al1=-1, al2=1, aw1=-1, aw2=1)
    P = _rastgele_noktalar(rng, n_nokta, af0)
    x, y, z = P.T
    b1 = b4 = 0.0
    for disl in turler.values():
        u0, _ = dc3d0(ALFA, x, y, np.zeros_like(z), 12.0, 50.0, *disl)
        S = gerilme_tensoru(gradyan(u0))
        b1 = max(b1, float(np.max(np.abs(S[:, [0, 1, 2], [2, 2, 2]]).max(axis=1) /
                                  np.abs(S).reshape(len(x), -1).max(axis=1))))
        u0, _ = dc3d0(ALFA, x, y, z, 12.0, 50.0, *disl)
        num = np.zeros((9, len(x)))
        for k, (ex, ey, ez) in enumerate(((1e-4, 0, 0), (0, 1e-4, 0), (0, 0, 1e-4))):
            up, _ = dc3d0(ALFA, x + ex, y + ey, z + ez, 12.0, 50.0, *disl)
            um, _ = dc3d0(ALFA, x - ex, y - ey, z - ez, 12.0, 50.0, *disl)
            num[3 * k:3 * k + 3] = (up[:3] - um[:3]) / 2e-4
        b4 = max(b4, float(np.max(np.abs(num - u0[3:]).max(axis=0) / np.abs(u0[3:]).max(axis=0))))
    out["bilgi_nokta_kaynak_ozdenetim"] = dict(yuzey_cekme=b1, sayisal_turev=b4)
    # 8. yönelim ve simetri
    out.update(_sinama8(kayit))
    # 9. ΔCFF izdüşümü
    s = 1.0
    sg = np.zeros((3, 3)); sg[0, 1] = sg[1, 0] = s
    a = dcff(sg, 0.0, 90.0, 180.0)
    sg2 = np.zeros((3, 3)); sg2[0, 0] = s
    b = dcff(sg2, 0.0, 90.0, 180.0)
    sg3 = np.zeros((3, 3)); sg3[0, 2] = sg3[2, 0] = s
    c = dcff(sg3, 0.0, 30.0, 90.0)
    s9 = max(abs(a[0] + s), abs(a[1]), abs(b[0]), abs(b[1] - s), abs(c[0] + 0.5 * s),
             abs(c[1] - s * math.sin(math.radians(60))))
    kayit("9_dcff_izdusumu", s9, 1e-12)
    # tekil noktalar
    out.update(_tekil_sinamasi(kayit))
    out["tablo_durumu"] = TABLO_DURUMU
    out["gecti"] = all(v["gecti"] for k, v in out.items() if isinstance(v, dict) and "gecti" in v)
    return out


def _sinama8(kayit):
    """8. Düşey sağ yanal fay, 0-15 km, boy 30 km; doğrultu 0, 90, 225; alıcı kaynakla aynı, μ' = 0, 7,5 km."""
    sonuc = {}
    xs = np.array([30.0, -30.0, 0.0, 0.0, 22.0, -22.0, 22.0, -22.0, 9.0, -9.0, 9.0, -9.0])
    ys = np.array([0.0, 0.0, 15.0, -15.0, 13.0, 13.0, -13.0, -13.0, 21.0, 21.0, -21.0, -21.0])
    taus, sns = {}, {}
    for dog in (0.0, 90.0, 225.0):
        af = dict(e=0.0, n=0.0, derinlik=15.0, uzunluk=30.0, genislik=15.0, dogrultu=dog, egim=90.0, rake=180.0,
                  kayma=1.0, al1=-15.0, al2=15.0, aw1=0.0, aw2=15.0)
        R = eksenler(dog)
        E = xs * R[0, 0] + ys * R[1, 0]
        N = xs * R[0, 1] + ys * R[1, 1]
        S, _ = altfay_gerilme(af, E, N, np.full(len(xs), -HESAP_DERINLIK_KM))
        tau, sn, _ = dcff(S, dog, 90.0, 180.0, mu_s=0.0)
        taus[dog], sns[dog] = tau, sn
    t = taus[0.0]
    m = np.abs(t).max()
    isaret = (t[0] > 0 and t[1] > 0 and t[2] < 0 and t[3] < 0)
    kayit("8a_isaret_uc_pozitif_yan_negatif", 0.0 if isaret else 1.0, 0.5,
          dict(tau_uc=[float(t[0]), float(t[1])], tau_yan=[float(t[2]), float(t[3])]))
    # simetri: (x, y) ↔ (−x, y) ve (x, −y)
    simx = max(abs(t[0] - t[1]), abs(t[4] - t[5]), abs(t[6] - t[7]), abs(t[8] - t[9]), abs(t[10] - t[11]))
    simy = max(abs(t[2] - t[3]), abs(t[4] - t[6]), abs(t[5] - t[7]), abs(t[8] - t[10]), abs(t[9] - t[11]))
    sn = sns[0.0]
    simn = max(abs(sn[0] + sn[1]), abs(sn[4] + sn[5]), abs(sn[6] + sn[7]), abs(sn[8] + sn[9]), abs(sn[10] + sn[11]))
    kayit("8b_simetri", max(simx, simy, simn) / m, 1e-8)
    don = max(float(np.max(np.abs(taus[d] - taus[0.0]))) for d in (90.0, 225.0)) / m
    don = max(don, max(float(np.max(np.abs(sns[d] - sns[0.0]))) for d in (90.0, 225.0)) / np.abs(sns[0.0]).max())
    kayit("8c_dondurme", don, 1e-8)
    return sonuc


def _tekil_sinamasi(kayit):
    """Tekil kümeler: fay kenarları, kenar uzantıları, fay düzlemi; ≥ 50 nokta. Hepsi sonlu ya da 'tekil' işaretli."""
    af = dict(depth=12.0, dip=40.0, al1=-8.0, al2=8.0, aw1=-5.0, aw2=5.0)
    sd, cd = math.sin(math.radians(40)), math.cos(math.radians(40))
    pts = []
    for xi in np.linspace(-8, 8, 9):
        for et in (-5.0, 5.0):
            pts.append((xi, et))                  # alt ve üst kenar
    for et in np.linspace(-5, 5, 7):
        for xi in (-8.0, 8.0):
            pts.append((xi, et))                  # yan kenarlar
    for xi in (-20.0, -12.0, 12.0, 20.0):
        for et in (-5.0, 5.0):
            pts.append((xi, et))                  # kenar uzantıları (doğrultu yönünde)
    for et in (-9.0, -7.0, 7.0, 9.0):
        for xi in (-8.0, 8.0):
            pts.append((xi, et))                  # kenar uzantıları (eğim yönünde)
    for xi in (-4.0, 0.0, 4.0):
        for et in (-2.0, 0.0, 2.0):
            pts.append((xi, et))                  # fay düzlemi içi
    pts = np.array(pts)
    xi, et = pts[:, 0], pts[:, 1]
    x, y, z = xi, et * cd, -af["depth"] + et * sd
    ok = z <= 0
    x, y, z = x[ok], y[ok], z[ok]
    sonlu, n_tek = True, 0
    for disl in ((1.0, 0, 0), (0, 1.0, 0), (0, 0, 1.0)):
        u, tek = dc3d(ALFA, x, y, z, af["depth"], af["dip"], af["al1"], af["al2"], af["aw1"], af["aw2"], *disl)
        sonlu &= bool(np.all(np.isfinite(u)))
        n_tek = int(tek.sum())
    kayit("tekil_noktalar_sonlu", 0.0 if sonlu else 1.0, 0.5, dict(nokta=int(len(x)), tekil_isaretli=n_tek))
    return {}


if __name__ == "__main__":
    import json
    import sys
    r = dogrulama(log=print)
    print(json.dumps(dict(gecti=r["gecti"], tablo=r["tablo_durumu"]), ensure_ascii=False))
    sys.exit(0 if r["gecti"] else 1)
