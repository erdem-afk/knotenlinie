#!/usr/bin/env python3
"""S7: tekrarlayan depremlerden ivmelenme kovaryatı ETAS'a bilgi ekliyor mu (ön kayıt ONKAYIT.md sürüm 2).

Kullanım: python3 -I s7.py <cikti_dizini>   (veri/ altından okur, ağ kullanmaz)
"""
import csv, json, math, sys, hashlib
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from scipy.optimize import minimize

BURASI = Path(__file__).resolve().parent
T0 = datetime(1984, 1, 1, tzinfo=timezone.utc)
HUCRE = 0.2
EPS = 0.1  # cm/yıl
MREF, MHEDEF = 2.5, 4.0


def gun(dt):
    return (dt - T0).total_seconds() / 86400.0


def ceyrek_basi(y, q):
    return gun(datetime(y, 3 * (q - 1) + 1, 1, tzinfo=timezone.utc))


CEYREKLER = [(y, q) for y in range(1990, 2015) for q in (1, 2, 3, 4)]
CB = np.array([ceyrek_basi(y, q) for y, q in CEYREKLER] + [ceyrek_basi(2015, 1)])
SECIM = np.array([y <= 2003 for y, q in CEYREKLER]); DOGR = ~SECIM
YIL = np.array([y for y, q in CEYREKLER])


def hucre(lat, lon):
    return (int(math.floor(lat / HUCRE)), int(math.floor(lon / HUCRE)))


def merkez(h):
    return ((h[0] + 0.5) * HUCRE, (h[1] + 0.5) * HUCRE)


def km(lat1, lon1, lat2, lon2):
    k = 111.19
    return np.hypot((np.asarray(lat1) - lat2) * k, (np.asarray(lon1) - lon2) * k * math.cos(math.radians(lat2)))


# ---------------- tekrarlayanlar ----------------
def tekrarlayanlar():
    diziler, cur = [], None
    for ln in open(BURASI / "veri" / "NCA_REPQcat_20210919.txt", encoding="latin1"):
        if ln.startswith("#") and len(ln.split()) >= 14 and ln.split()[1].isdigit():
            cur = []; diziler.append(cur); continue
        p = ln.split()
        if cur is None or len(p) < 18 or not p[0].isdigit() or len(p[0]) != 4:
            continue
        y, mo, d, hh, mm = map(int, p[:5]); sc = float(p[5])
        t = gun(datetime(y, mo, d, hh, mm, tzinfo=timezone.utc)) + sc / 86400
        cur.append((t, float(p[7]), float(p[8]), float(p[13])))
    return [sorted(s) for s in diziler if s]


def kovaryat(diziler):
    t2003 = gun(datetime(2004, 1, 1, tzinfo=timezone.utc))
    izlenen_say, atanmis = {}, {}
    for i, s in enumerate(diziler):
        once = [e for e in s if e[0] < t2003]
        if not once:
            continue
        h = hucre(float(np.median([e[1] for e in once])), float(np.median([e[2] for e in once])))
        atanmis.setdefault(h, []).append(i)
        if len(once) >= 3 and (once[-1][0] - once[0][0]) >= 10 * 365.25:
            izlenen_say[h] = izlenen_say.get(h, 0) + 1
    izlenen = sorted(h for h, n in izlenen_say.items() if n >= 5)
    A = np.zeros((len(izlenen), len(CEYREKLER)))
    for k, h in enumerate(izlenen):
        ilk = []; ev = []
        for i in atanmis[h]:
            s = diziler[i]
            ilk.append(s[0][0])
            for j, e in enumerate(s):
                if j == 0:
                    continue  # gerçek zamanlı: dizinin ilk olayı sayılmaz; j ≥ 1 olaylar öncesinde eş var
                if 0 < e[3] < 3.5:
                    M0 = 10 ** (1.5 * e[3] + 16.1)
                    ev.append((e[0], 10 ** (-2.36) * M0 ** 0.17))
        ilk = np.array(ilk); ev = np.array(ev) if ev else np.zeros((0, 2))
        for q in range(len(CEYREKLER)):
            t = CB[q]
            P = int((ilk < t).sum())
            if P == 0:
                continue
            v12 = ev[(ev[:, 0] >= t - 365.25) & (ev[:, 0] < t), 1].sum() / P / 1.0
            v60 = ev[(ev[:, 0] >= t - 6 * 365.25) & (ev[:, 0] < t - 365.25), 1].sum() / P / 5.0
            A[k, q] = math.log((v12 + EPS) / (v60 + EPS))
    Astar = A - np.median(A, axis=0, keepdims=True)
    return izlenen, A, Astar


# ---------------- ComCat ve ETAS ----------------
def comcat():
    t, la, lo, m = [], [], [], []
    for r in csv.DictReader(open(BURASI / "veri" / "comcat.csv")):
        if r.get("type", "earthquake") != "earthquake" or not r["mag"]:
            continue
        dt = datetime.fromisoformat(r["time"].replace("Z", "+00:00"))
        t.append(gun(dt)); la.append(float(r["latitude"])); lo.append(float(r["longitude"])); m.append(float(r["mag"]))
    o = np.argsort(t)
    return np.array(t)[o], np.array(la)[o], np.array(lo)[o], np.array(m)[o]


class ETAS:
    def __init__(self, izlenen, cat):
        self.h = izlenen
        t, la, lo, m = cat
        self.cat = cat
        self.tetik, self.hedef = [], []
        for h in izlenen:
            c = merkez(h)
            tet = np.where(km(la, lo, c[0], c[1]) <= 20.0)[0]
            hed = np.where([hucre(a, b) == h for a, b in zip(la, lo)])[0]
            self.tetik.append(tet); self.hedef.append(hed)

    def fit(self, t_bas, t_son, tohum=1):
        t, la, lo, m = self.cat
        H = len(self.h)
        veri = []
        for k in range(H):
            tet = self.tetik[k]; tet = tet[t[tet] < t_son]
            hed = self.hedef[k]; hed = hed[(t[hed] >= t_bas) & (t[hed] < t_son)]
            dt = t[hed][:, None] - t[tet][None, :]
            msk = dt > 0
            veri.append((tet, hed, np.where(msk, dt, 1.0), msk))

        def nll(x):
            mu = np.exp(x[:H]); K, alpha, c, p = np.exp(x[H]), x[H + 1], np.exp(x[H + 2]), 1 + np.exp(x[H + 3])
            tot = 0.0
            for k, (tet, hed, dt, msk) in enumerate(veri):
                ver = K * 10 ** (alpha * (m[tet] - MREF))
                lam = mu[k] + (msk * ver[None, :] * (dt + c) ** (-p)).sum(1)
                a = np.maximum(t_bas - t[tet], 0.0)
                b = t_son - t[tet]
                integ = ver * ((a + c) ** (1 - p) - (b + c) ** (1 - p)) / (p - 1)
                tot += np.log(lam).sum() - mu[k] * (t_son - t_bas) - integ.sum()
            return -tot
        rng = np.random.default_rng(tohum)
        n_hed = [len(v[1]) for v in veri]
        lo_b = [math.log(1e-6)] * H + [math.log(1e-4), 0.0, math.log(1e-4), math.log(0.01)]
        hi_b = [math.log(10.0)] * H + [math.log(10.0), 2.3, math.log(1.0), math.log(1.0)]
        best = None
        for s in range(5):
            x0 = [math.log(max(n, 1) / (t_son - t_bas) * rng.uniform(0.2, 0.8)) for n in n_hed] + \
                 [math.log(rng.uniform(0.005, 0.05)), rng.uniform(0.6, 1.6), math.log(rng.uniform(0.003, 0.05)), math.log(rng.uniform(0.02, 0.3))]
            x0 = np.clip(x0, lo_b, hi_b)
            r = minimize(nll, x0, method="L-BFGS-B", bounds=list(zip(lo_b, hi_b)), options={"maxiter": 3000})
            if best is None or r.fun < best.fun:
                best = r
        self.x = best.x; self.ll = -best.fun; self.H = H
        return self

    def par(self):
        H = self.H; x = self.x
        return dict(K=float(np.exp(x[H])), alpha=float(x[H + 1]), c=float(np.exp(x[H + 2])), p=float(1 + np.exp(x[H + 3])),
                    mu=[float(v) for v in np.exp(x[:H])])

    def beklenen_ceyrek(self, b):
        """her hücre-çeyrek için M ≥ 4 beklenen sayı; yalnız çeyrek başından önceki tetikleyiciler."""
        t, la, lo, m = self.cat
        pr = self.par(); K, al, c, p = pr["K"], pr["alpha"], pr["c"], pr["p"]
        N = np.zeros((self.H, len(CEYREKLER)))
        for k in range(self.H):
            tet = self.tetik[k]
            ver = K * 10 ** (al * (m[tet] - MREF))
            for q in range(len(CEYREKLER)):
                a, bb = CB[q], CB[q + 1]
                once = t[tet] < a
                integ = (ver[once] * ((a - t[tet][once] + c) ** (1 - p) - (bb - t[tet][once] + c) ** (1 - p)) / (p - 1)).sum()
                N[k, q] = (pr["mu"][k] * (bb - a) + integ) * 10 ** (-b * (MHEDEF - MREF))
        return N


def sayilar(izlenen, cat, mmin=MHEDEF, haric=None):
    t, la, lo, m = cat
    n = np.zeros((len(izlenen), len(CEYREKLER)))
    idx = {h: k for k, h in enumerate(izlenen)}
    for i in np.where(m >= mmin)[0]:
        h = hucre(la[i], lo[i])
        if h not in idx or t[i] < CB[0] or t[i] >= CB[-1]:
            continue
        q = int(np.searchsorted(CB, t[i], side="right") - 1)
        n[idx[h], q] += 1
    return n


def poisson_ll(n, lam):
    from scipy.special import gammaln
    return n * np.log(lam) - lam - gammaln(n + 1)


def ig_jk(n, N0, N1, msk):
    """IG (nat/olay) ve yıl jackknife SE; msk: dahil hücre-çeyrekler (H×Q)."""
    d = (poisson_ll(n, N1) - poisson_ll(n, N0))
    yillar = sorted(set(YIL[msk.any(0)]))
    tot_n = n[msk].sum()
    IG = d[msk].sum() / tot_n if tot_n else float("nan")
    loo = []
    for y in yillar:
        mk = msk & (YIL[None, :] != y)
        nn = n[mk].sum()
        loo.append(d[mk].sum() / nn if nn else np.nan)
    loo = np.array(loo); k = len(loo)
    SE = math.sqrt((k - 1) / k * np.nansum((loo - np.nanmean(loo)) ** 2))
    return float(IG), float(SE), int(tot_n)


def main(cikti):
    cikti = Path(cikti); cikti.mkdir(parents=True, exist_ok=True)
    out = {"kod_sha256": hashlib.sha256(open(__file__, "rb").read()).hexdigest()}
    diz = tekrarlayanlar()
    out["dizi_sayisi"] = len(diz); out["olay_sayisi"] = sum(len(s) for s in diz)
    izlenen, A, Astar = kovaryat(diz)
    out["izlenen_hucreler"] = [list(merkez(h)) for h in izlenen]
    out["izlenen_sha256"] = hashlib.sha256(json.dumps(out["izlenen_hucreler"]).encode()).hexdigest()
    cat = comcat()
    n4 = sayilar(izlenen, cat)
    # ateşleme kapısı (yalnız sayı)
    N_dogr = int(n4[:, DOGR].sum()); yil_dogr = sorted(set(YIL[DOGR][n4[:, DOGR].sum(0) > 0].tolist()))
    out["N_dogrulama"] = N_dogr; out["hedef_yillari"] = yil_dogr; out["N_secim"] = int(n4[:, SECIM].sum())
    kapi = N_dogr >= 20 and len(yil_dogr) >= 5
    out["atesleme_kapisi_acik"] = kapi
    json.dump(out, open(cikti / "sonuc.json", "w"), indent=1)
    print("kapı:", N_dogr, len(yil_dogr), kapi, "seçim N:", out["N_secim"], flush=True)

    # b (Aki–Utsu, ΔM = 0,01), izlenen hücreler, 1984–2003
    t, la, lo, m = cat
    hset = set(izlenen)
    sel = np.array([hucre(a, b_) in hset for a, b_ in zip(la, lo)]) & (t < gun(datetime(2004, 1, 1, tzinfo=timezone.utc))) & (m >= MREF)
    b = math.log10(math.e) / (m[sel].mean() - (MREF - 0.005))
    out["b"] = b; out["b_n"] = int(sel.sum())

    et = ETAS(izlenen, cat).fit(gun(datetime(1985, 1, 1, tzinfo=timezone.utc)), gun(datetime(2004, 1, 1, tzinfo=timezone.utc)))
    out["etas"] = et.par(); out["etas_ll"] = et.ll
    N0 = et.beklenen_ceyrek(b)
    out["beklenen_vs_gozlenen"] = {"secim": [float(N0[:, SECIM].sum()), int(n4[:, SECIM].sum())],
                                   "dogrulama": [float(N0[:, DOGR].sum()), N_dogr]}

    def beta_fit(X):
        f = lambda be: -poisson_ll(n4[:, SECIM], N0[:, SECIM] * np.exp(be * X[:, SECIM])).sum()
        from scipy.optimize import minimize_scalar
        r = minimize_scalar(f, bounds=(-5, 5), method="bounded")
        prof = {f"{v:+.2f}": float(-f(v)) for v in np.linspace(-1, 1, 9)}
        return float(r.x), prof
    beta, prof = beta_fit(Astar); out["beta"] = beta; out["beta_profil"] = prof
    N1 = N0 * np.exp(beta * Astar)
    msk = np.zeros_like(n4, bool); msk[:, DOGR] = True
    IG, SE, N = ig_jk(n4, N0, N1, msk)
    out["IG"] = IG; out["SE"] = SE
    if not kapi:
        hk = "ayirt edilemez (kapi kapali, bilgi satiri)"
    elif IG - 2 * SE > 0 and beta > 0:
        hk = "H1"
    elif IG + 2 * SE < 0:
        hk = "H0 lehine"
    else:
        hk = "ayirt edilemez"
    out["hukum"] = hk

    # ek satırlar
    bh, _ = beta_fit(A); N1h = N0 * np.exp(bh * A)
    out["ham_A"] = dict(zip(["IG", "SE", "N"], ig_jk(n4, N0, N1h, msk)), beta=bh)
    # M ≥ 5 pencereleri dışlanmış
    big = np.where(m >= 5.0)[0]
    msk5 = msk.copy()
    for k, h in enumerate(izlenen):
        c = merkez(h)
        for i in big:
            if km(la[i], lo[i], c[0], c[1]) <= 30:
                for q in range(len(CEYREKLER)):
                    if CB[q] < t[i] + 365.25 and CB[q + 1] > t[i]:
                        msk5[k, q] = False
    out["M5_pencereleri_harici"] = dict(zip(["IG", "SE", "N"], ig_jk(n4, N0, N1, msk5)))
    # Parkfield 2004 (ilk 90 gün, 30 km): olay kaldırılarak sayım
    tp = gun(datetime(2004, 9, 28, 17, 15, tzinfo=timezone.utc))
    pk = (abs(t - tp) < 1e9) & (t >= tp) & (t < tp + 90) & (km(la, lo, 35.815, -120.374) <= 30)
    cat_np = (t[~pk], la[~pk], lo[~pk], m[~pk])
    n4p = sayilar(izlenen, cat_np)
    out["parkfield2004_harici"] = dict(zip(["IG", "SE", "N"], ig_jk(n4p, N0, N1, msk)))
    n5 = sayilar(izlenen, cat, 5.0)
    out["M5_hedef"] = {"N_dogrulama": int(n5[:, DOGR].sum()),
                       "IG": ig_jk(n5, N0 * 10 ** (-b), N1 * 10 ** (-b), msk)[0] if n5[:, DOGR].sum() else None}
    out["Astar_dogrulama_ozet"] = {"ort": float(Astar[:, DOGR].mean()), "sd": float(Astar[:, DOGR].std())}
    json.dump(out, open(cikti / "sonuc.json", "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("N_dogrulama", "b", "beta", "IG", "SE", "hukum", "ham_A", "M5_pencereleri_harici", "parkfield2004_harici", "beklenen_vs_gozlenen")}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
