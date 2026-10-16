"""Dieterich (1994): x=gamma*tau_dot, R/r=1/x; Pa ve gün."""
from __future__ import annotations

import numpy as np
from scipy.optimize import minimize


def _pozitif(v, ad):
    a = np.asarray(v, float)
    if np.any(~np.isfinite(a)) or np.any(a <= 0):
        raise ValueError(ad + " sonlu ve pozitif olmalı")
    return a


def gevset(logx, gun, ta):
    """Sabit yüklemede x(t)=1+(x(0)-1) exp(-t/ta), log uzayında."""
    ta = _pozitif(ta, "ta")
    d = np.asarray(gun, float) / ta
    if np.any(~np.isfinite(d)) or np.any(d < 0):
        raise ValueError("süre sonlu ve negatif olmayan olmalı")
    with np.errstate(divide="ignore"):
        return np.logaddexp(np.asarray(logx, float) - d, np.log(-np.expm1(-d)))


def basamak(logx, dcfs_pa, asigma_pa):
    """Ani gerilme basamağı: gamma+ = gamma- exp(-DeltaCFS/Asigma)."""
    s = np.asarray(dcfs_pa, float)
    if np.any(~np.isfinite(s)) or np.any(~np.isfinite(logx)):
        raise ValueError("durum ve gerilme sonlu olmalı")
    return np.asarray(logx, float) - s / _pozitif(asigma_pa, "Asigma")


def oran(logx, gun, ta):
    """Arka plan oranına bölünmüş anlık oran; gerilme gölgesi korunur."""
    return np.exp(-gevset(logx, gun, ta))


def integral(logx, gun, ta):
    """int R/r dt = ta log[1+(exp(dt/ta)-1)/x0], kararlı kapalı çözüm."""
    ta = _pozitif(ta, "ta")
    d = np.asarray(gun, float) / ta
    if np.any(~np.isfinite(d)) or np.any(d < 0):
        raise ValueError("süre sonlu ve negatif olmayan olmalı")
    with np.errstate(divide="ignore"):
        log_em1 = d + np.log(-np.expm1(-d))
    return ta * np.logaddexp(0.0, log_em1 - np.asarray(logx, float))


def basamak_orani(t, dcfs_pa, asigma_pa, tau_dot_pa_gun):
    """Tek basamak: R/r=[1+(exp(-Delta/Asigma)-1)exp(-t/ta)]^-1."""
    ta = _pozitif(asigma_pa, "Asigma") / _pozitif(tau_dot_pa_gun, "tau_dot")
    return oran(basamak(0.0, dcfs_pa, asigma_pa), t, ta)


def geri_kazan(olay_gunleri, sure, dcfs_pa, r_gun):
    """Tek basamak NHPP olaylarından Asigma ve ta MLE; r ve Delta bilinir."""
    t = np.asarray(olay_gunleri, float)
    if not np.isfinite(sure) or sure <= 0 or np.any(t < 0) or np.any(t >= sure):
        raise ValueError("olaylar [0,süre) içinde olmalı")
    _pozitif(r_gun, "r")
    def nll(z):
        a, ta = np.exp(z)
        lx = -dcfs_pa / a
        return float(np.log(r_gun) * -len(t) + gevset(lx, t, ta).sum()
                     + r_gun * integral(lx, sure, ta))
    adaylar = [minimize(nll, np.log([a, ta]), method="L-BFGS-B",
                       bounds=[(np.log(100), np.log(1e7)), (np.log(.01), np.log(1e5))])
               for a, ta in ((20000, 10), (100000, 100), (500000, 1000))]
    res = min(adaylar, key=lambda r: r.fun)
    return {"asigma_pa": float(np.exp(res.x[0])), "ta_gun": float(np.exp(res.x[1])),
            "basari": bool(res.success), "logL": float(-res.fun), "n": len(t)}
