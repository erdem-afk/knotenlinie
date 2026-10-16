"""Magnitude of completeness: overall, by hour, by season, after large events.

Overall Mc by two standard methods that must agree within 0.2 magnitude units:
(a) maximum curvature plus the b-value stability criterion (Wiemer & Wyss 2000,
10.1785/0119990114) and (b) the ETAS-D detection edge Mc_inf.  When they disagree the caller gets both and the CLI
stops instead of silently choosing.

By hour the Schuster test (Rydelek & Sacks 1989, 10.1038/337251a0): with phase
``theta_k = 2*pi*hour_k/24``, ``R = |sum_k exp(i theta_k)|/N`` and
``p = exp(-R^2 N)``.  The same test runs on the 365.25-day phase for the season.
Small bins never become a number: below ``N_MIN = 500`` the answer is the string
``YETERSIZ_VERI``.

Uncertainty: Mc carries a seeded bootstrap 95 % interval because downstream steps that depend
on the completeness estimate consume it.

Clean-room implementation from the published equations; no code copied from
pyetas (AGPL), the CRAN ETAS package (GPL) or Zhuang's Fortran sd package.
"""
from __future__ import annotations

import numpy as np

from . import katalog as K

YETERSIZ_VERI = "YETERSIZ_VERI"
N_MIN = 500
UYUM_ESIGI = 0.2


def mc_maximum_egrilik(mags, dm: float = 0.1, baslangic: float = None) -> float:
    """Mc as the mode of the 0.1-degree magnitude histogram (maximum curvature).

    The bins are centred on the magnitude grid (edges at grid - dm/2), so the mode is a grid
    magnitude, the lowest bin centre Aki's binning correction ``mc - dm/2`` expects. Until
    2026-09-29 the edges sat on the grid values and the mode came back half a bin high (2.95 for a
    3.0 cutoff), which biased every b low.
    """
    m = np.asarray(mags, float)
    m = m[np.isfinite(m)]
    if m.size == 0:
        return float("nan")
    lo = float(np.round(np.floor((baslangic if baslangic is not None else m.min()) / dm + 1e-9) * dm, 6))
    kenar = np.arange(lo - dm / 2.0, m.max() + 2 * dm, dm)
    h, e = np.histogram(m, bins=kenar)
    return float(np.round(e[int(np.argmax(h))] + dm / 2.0, 6))


def b_degeri_hizli(mags, mc: float, dm: float = 0.1):
    """Aki-Utsu b and its analytic standard error (Shi & Bolt style)."""
    m = np.asarray(mags, float)
    m = m[m >= mc]
    if m.size < 10:
        return float("nan"), float("nan"), int(m.size)
    ort = m.mean() - (mc - dm / 2.0)
    b = float(np.log10(np.e) / ort)
    sigma = float(np.std(m, ddof=1) / np.sqrt(m.size))
    return b, float(2.3 * b ** 2 * sigma), int(m.size)


#: MBS window: b_ave is the mean b over Mco ... Mco + 0.4, i.e. a 0.5-magnitude span of 0.1 bins.
MBS_PENCERE = 5
#: MBS search span above the maximum-curvature Mc.
MBS_ARAMA = 1.5
YONTEM = ("maximum curvature (Wiemer & Wyss 2000) + b-value stability, MBS "
          "(Cao & Gao 2002; uncertainty criterion of Woessner & Wiemer 2005, 10.1785/0120040007)")


def mc_wiemer_wyss(mags, dm: float = 0.1, baslangic: float = None, pencere: int = MBS_PENCERE,
                   arama: float = MBS_ARAMA) -> dict:
    """Maximum curvature, then the b-value-stability Mc (MBS).

    Mc is the smallest cutoff Mco from the maximum-curvature Mc up at which
    ``|b_ave - b(Mco)| <= db(Mco)``, with ``b_ave`` the mean Aki b over ``pencere`` successive
    cutoffs from Mco and ``db`` Shi & Bolt's standard error (Woessner & Wiemer 2005). When no
    cutoff in the search span meets it, ``mc`` is None and ``kararli`` False: the catalogue has no
    b-stable tail there. Until 2026-09-29 the criterion was a fixed 5 % band on the next three
    cutoffs and a failed search returned the span's end as Mc (3.75 on the compute server's ML catalogue).
    """
    mc_egri = mc_maximum_egrilik(mags, dm, baslangic)
    m = np.asarray(mags, float)
    adaylar = np.round(np.arange(mc_egri, mc_egri + arama + 1e-9, dm), 6)
    tum = np.round(np.arange(mc_egri, mc_egri + arama + pencere * dm + 1e-9, dm), 6)
    b_seri = [b_degeri_hizli(m, mc - 1e-9, dm) for mc in tum]
    mc_kararli = None
    for i in range(len(adaylar)):
        b0, db0, _n0 = b_seri[i]
        pen = [b_seri[j][0] for j in range(i, i + pencere)]
        if not (np.isfinite(b0) and np.isfinite(db0) and all(np.isfinite(pen))):
            continue
        if abs(float(np.mean(pen)) - b0) <= db0:
            mc_kararli = float(adaylar[i])
            break
    return {"mc": mc_kararli, "kararli": mc_kararli is not None, "mc_maximum_egrilik": mc_egri,
            "b": b_degeri_hizli(m, mc_kararli - 1e-9, dm)[0] if mc_kararli is not None else None,
            "adaylar": adaylar.tolist(), "yontem": YONTEM}


def mc_bootstrap(mags, n_bootstrap: int = 1000, seed: int = 20260929, dm: float = 0.1,
                 baslangic: float = None, tahminci=None) -> dict:
    """Seeded bootstrap 95 % interval of the Mc estimator that is reported.

    The default estimator is the b-value-stability Mc of :func:`mc_wiemer_wyss`, the one
    ``tamlik_ozet`` reports; until 2026-09-29 the interval was drawn from the maximum-curvature
    Mc instead, so the compute-server run gave Mc 2.95 with an interval of [2.05, 2.25].
    """
    if tahminci is None:
        def tahminci(x):
            return mc_wiemer_wyss(x, dm, baslangic)["mc"]
    m = np.asarray(mags, float)
    m = m[np.isfinite(m)]
    rng = np.random.default_rng(seed)
    n = m.size
    if n < 50:
        return {"mc": tahminci(m), "aralik95": [None, None], "n": int(n)}
    deger = np.full(n_bootstrap, np.nan)
    for k in range(n_bootstrap):
        v = tahminci(m[rng.integers(0, n, n)])
        deger[k] = np.nan if v is None else v
    iyi = deger[np.isfinite(deger)]
    kararsiz = int(n_bootstrap - iyi.size)
    if iyi.size == 0:
        return {"mc": None, "aralik95": [None, None], "n": int(n), "n_bootstrap": n_bootstrap,
                "seed": seed, "kararsiz": kararsiz}
    return {"mc": float(np.median(iyi)), "aralik95": [float(np.percentile(iyi, 2.5)),
                                                      float(np.percentile(iyi, 97.5))],
            "n": int(n), "n_bootstrap": n_bootstrap, "seed": seed, "kararsiz": kararsiz}


# --- Schuster and chi-square tests ------------------------------------------

def schuster(faz, per: float, agirlik=None) -> dict:
    """Schuster test for a period.  ``faz`` is in the same unit as ``per``."""
    faz = np.asarray(faz, float)
    faz = faz[np.isfinite(faz)]
    w = np.ones(faz.size) if agirlik is None else np.asarray(agirlik, float)[np.isfinite(faz)]
    if faz.size == 0 or w.sum() <= 0:
        return {"N": 0, "N_eff": 0.0, "R": 0.0, "p": 1.0}
    theta = 2.0 * np.pi * faz / per
    C = float(np.sum(w * np.cos(theta)))
    S = float(np.sum(w * np.sin(theta)))
    toplam = float(w.sum())
    R = float(np.hypot(C, S) / toplam)
    neff = float(toplam ** 2 / np.sum(w ** 2))
    p = float(np.exp(-R ** 2 * neff))
    return {"N": int(faz.size), "N_eff": neff, "R": R, "p": min(1.0, p), "genlik": 2.0 * R}


def chi2_duzenli(sayimlar) -> dict:
    """Pearson chi-square against a uniform bin expectation."""
    from scipy import stats
    o = np.asarray(sayimlar, float)
    if o.sum() <= 0 or o.size < 2:
        return {"chi2": 0.0, "p": 1.0, "dof": max(o.size - 1, 0)}
    e = np.full(o.size, o.sum() / o.size)
    chi2 = float(np.sum((o - e) ** 2 / e))
    return {"chi2": chi2, "dof": int(o.size - 1), "p": float(stats.chi2.sf(chi2, o.size - 1))}


def saat_dilimi(df, mc: float, n_min: int = N_MIN) -> dict:
    """Mc per 0.1 magnitude bin by hour of day (Schuster + chi-square)."""
    d = df[df["mag"] >= mc]
    saat = (d["time_utc"].dt.hour + d["time_utc"].dt.minute / 60.0
            + d["time_utc"].dt.second / 3600.0).to_numpy()
    mags = d["mag"].to_numpy()
    cikti = {}
    for alt in np.unique(np.round(mags * 10) / 10):
        sec = mags >= alt - 1e-9
        n = int(sec.sum())
        if n < n_min:
            cikti[f"{alt:.1f}"] = {"N": n, "sonuc": YETERSIZ_VERI}
            continue
        sch = schuster(saat[sec], 24.0)
        sayim, _ = np.histogram(saat[sec], bins=24, range=(0, 24))
        cikti[f"{alt:.1f}"] = {"N": n, "R": sch["R"], "p": sch["p"], "genlik": sch["genlik"],
                               "chi2": chi2_duzenli(sayim)["p"]}
    return cikti


def mevsim_dilimi(df, mc: float, n_min: int = N_MIN) -> dict:
    """Mc per month and the annual Schuster test (365.25-day period)."""
    d = df[df["mag"] >= mc].copy()
    gun = (d["time_utc"].dt.dayofyear - 1 + d["time_utc"].dt.hour / 24.0).to_numpy()
    ay = d["time_utc"].dt.month.to_numpy()
    aylik = {int(a): int((ay == a).sum()) for a in np.unique(ay)}
    sch = schuster(gun, 365.25)
    mc_ay = {}
    for a in np.unique(ay):
        sec = ay == a
        if int(sec.sum()) < n_min:
            mc_ay[int(a)] = YETERSIZ_VERI
        else:
            mc_ay[int(a)] = mc_maximum_egrilik(d["mag"].to_numpy()[sec])
    return {"N": int(len(d)), "schuster": sch, "chi2_ay": chi2_duzenli(list(aylik.values())),
            "aylik_sayi": aylik, "aylik_mc": mc_ay}


PENCERELER = (("0-1s", 0.0, 1 / 24), ("1-6s", 1 / 24, 6 / 24), ("6-24s", 6 / 24, 1.0),
              ("1-7g", 1.0, 7.0), ("7-30g", 7.0, 30.0), (">30g", 30.0, np.inf))


def buyuk_sonrasi(df, mc: float, m_buyuk: float, n_min: int = N_MIN) -> dict:
    """Mc in the declared windows after every M >= M_buyuk event."""
    t = df["gun"].to_numpy(float) if "gun" in df else K.gun(df["time_utc"])
    mags = df["mag"].to_numpy(float)
    buyuk = t[mags >= m_buyuk]
    cikti = {}
    for ad, a, b in PENCERELER:
        mag_pen = []
        for tb in buyuk:
            sec = (t > tb + a) & (t <= tb + b)
            mag_pen.append(mags[sec])
        hepsi = np.concatenate(mag_pen) if mag_pen else np.array([])
        n = int(hepsi.size)
        cikti[ad] = {"N": n, "mc": (mc_maximum_egrilik(hepsi) if n >= n_min else YETERSIZ_VERI)}
    return cikti


#: Width of the completeness windows, years; a window with fewer events is listed, not judged.
PENCERE_YIL = 5
PENCERE_N_MIN = 200


def pencere_araliklari(df, mc_baslangic, yil: int = PENCERE_YIL, n_min: int = PENCERE_N_MIN,
                       bas_yil: int = None):
    """The declared completeness windows as one dict per window.

    Five-year windows from the catalogue's first year; the final partial window ends at the
    catalogue's last year (its own window), so every event belongs to exactly one window.  Each
    dict carries the label ``ad``, the first year ``bas_yil``, one past the last year ``bit_yil``,
    the count ``n``, the MBS Mc (``None`` below ``n_min``) and its ``b``.  The ETAS-D detection
    edge is fitted per these windows: the caller turns the year span into day edges, never this
    module.  ``bas_yil`` counts the windows from a declared year instead of the
    catalogue's first year (the ETAS-D model start); events before it are in no
    window.
    """
    y = df["time_utc"].dt.year.to_numpy()
    if bas_yil is not None:
        df = df[y >= int(bas_yil)]
        y = y[y >= int(bas_yil)]
    if y.size == 0:
        return []
    y_min, y_max = (int(y.min()) if bas_yil is None else int(bas_yil)), int(y.max())
    baslangiclar = list(range(y_min, y_max + 1, yil))
    out = []
    for i, a in enumerate(baslangiclar):
        bit = baslangiclar[i + 1] if i + 1 < len(baslangiclar) else y_max + 1
        m = df["mag"].to_numpy(float)[(y >= a) & (y < bit)]
        ad = f"{a}-{min(bit - 1, y_max)}"
        if m.size < n_min:
            out.append({"ad": ad, "bas_yil": a, "bit_yil": bit, "n": int(m.size),
                        "mc": None, "b": None, "yargilanmadi": True})
            continue
        ww = mc_wiemer_wyss(m, baslangic=mc_baslangic)
        out.append({"ad": ad, "bas_yil": a, "bit_yil": bit, "n": int(m.size),
                    "mc": ww["mc"], "b": ww["b"], "yargilanmadi": False})
    return out


def mc_pencereler(df, mc_baslangic: float, yil: int = PENCERE_YIL, n_min: int = PENCERE_N_MIN) -> dict:
    """MBS Mc in the declared completeness windows (counts and Mc only)."""
    return {p["ad"]: {"n": p["n"], "mc": p["mc"], "b": p["b"], "yargilanmadi": p["yargilanmadi"]}
            for p in pencere_araliklari(df, mc_baslangic, yil=yil, n_min=n_min)}


def tamlik_ozet(df, mc_baslangic: float, m_buyuk: float, etasd_mc: float = None,
                seed: int = 20260929, n_min: int = N_MIN) -> dict:
    """Overall Mc plus the hour/season/after-large tables and the summary JSON.

    The reported Mc holds over the whole span: it is the largest of the pooled MBS Mc and the MBS
    Mc of every judged ``PENCERE_YIL``-year window (network growth lowers Mc with time; HORUS's
    Apennine box goes from 3.3 in the 1970s to 1.4 in 2010-2015, compute server 2026-09-29). A judged window
    without a b-stable Mc stops the command.
    """
    ww = mc_wiemer_wyss(df["mag"].to_numpy(), baslangic=mc_baslangic)
    if not ww["kararli"]:
        raise ValueError(f"no b-stable Mc in {ww['adaylar'][0]}..{ww['adaylar'][-1]} (MBS); "
                         f"the catalogue's tail is not Gutenberg-Richter there")
    pencereler = mc_pencereler(df, mc_baslangic)
    kararsiz = [ad for ad, p in pencereler.items() if not p["yargilanmadi"] and p["mc"] is None]
    if kararsiz:
        raise ValueError(f"no b-stable Mc in the completeness windows {kararsiz} (MBS)")
    adaylar = [ww["mc"]] + [p["mc"] for p in pencereler.values() if p["mc"] is not None]
    mc = float(max(adaylar))
    boot = mc_bootstrap(df["mag"].to_numpy(), seed=seed, baslangic=mc_baslangic)
    uyum = None if etasd_mc is None else abs(mc - etasd_mc)
    ozet = {"mc": mc, "mc_genel": ww["mc"], "yontem": ww["yontem"] + "; max over "
            f"{PENCERE_YIL}-year windows", "aralik95_genel": boot["aralik95"],
            "bootstrap_kararsiz": boot.get("kararsiz", 0),
            "b": b_degeri_hizli(df["mag"].to_numpy(float), mc - 1e-9)[0],
            "mc_maximum_egrilik": ww["mc_maximum_egrilik"],
            "mc_etasd": etasd_mc, "uyum_farki": uyum,
            "uyusmuyor": bool(uyum is not None and uyum > UYUM_ESIGI),
            "N_min": n_min, "n": int(len(df))}
    return {"ozet": ozet, "pencereler": pencereler, "saat": saat_dilimi(df, mc, n_min),
            "mevsim": mevsim_dilimi(df, mc, n_min),
            "buyuk_sonrasi": buyuk_sonrasi(df, mc, m_buyuk, n_min)}
