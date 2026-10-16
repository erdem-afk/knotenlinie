"""Küçük ölçekte (yerel makine) 1° İtalya iç doğrulaması; günlük açık-geçmiş koşullaması."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import time
import numpy as np
import pandas as pd
from scipy.special import gammaln

from knotenlinie.etas.model import mle_temporal, _omori_ilke
from .arayuz import Model, buyukluk_paylari
from .girdi import katalog_oku, fay_oku, k9_basamaklari, KUTU, AYAR_SON
from .oran import gevset, basamak, integral


def izgara_uret(adim=1.):
    if adim <= 0:
        raise ValueError("ızgara adımı pozitif olmalı")
    lat = np.r_[np.arange(KUTU[0], KUTU[1], adim), KUTU[1]]
    lon = np.r_[np.arange(KUTU[2], KUTU[3], adim), KUTU[3]]
    return pd.DataFrame([(x, xx, y, yy) for y, yy in zip(lat[:-1], lat[1:])
                         for x, xx in zip(lon[:-1], lon[1:])],
                        columns=["boylam_min", "boylam_max", "enlem_min", "enlem_max"])


def sayim(katalog, izgara, gunler, esik):
    """Hücre ve gün Poisson sayımı; kenarlar yarı açık, dışarıdaki olay hata."""
    n = np.zeros((len(gunler), len(izgara)), dtype=int)
    a, z = gunler[0], gunler[-1]+pd.Timedelta(days=1)
    for r in katalog[(katalog.zaman >= a) & (katalog.zaman < z) & (katalog.mw >= esik)].itertuples():
        mask = ((izgara.boylam_min <= r.boylam) & (izgara.boylam_max > r.boylam)
                & (izgara.enlem_min <= r.enlem) & (izgara.enlem_max > r.enlem))
        idx = np.flatnonzero(mask)
        if len(idx) != 1:
            raise ValueError("olay tek bir hücreye düşmedi")
        i = int((r.zaman-a).total_seconds()//86400)
        n[i, idx[0]] += 1
    return n


def poisson_logl(beklenen, n):
    """Tam Poisson skor; boş hücrelerin cezası da var, sıfır oran uydurulmaz."""
    lam, n = np.asarray(beklenen, float), np.asarray(n, float)
    if lam.shape != n.shape or np.any(~np.isfinite(lam)) or np.any(~np.isfinite(n)) or np.any(lam < 0) or np.any(n < 0) or np.any(n != np.floor(n)):
        raise ValueError("Poisson girdileri geçersiz")
    if np.any((lam == 0) & (n > 0)):
        return -float("inf")
    mask = n > 0
    return float((n[mask]*np.log(lam[mask])).sum()-lam.sum()-gammaln(n+1).sum())


def bilgi_kazanci(aday, taban, n):
    """[sum n log(aday/taban) - sum(aday-taban)] / N, nat/olay."""
    N = np.asarray(n).sum()
    if N <= 0:
        raise ValueError("olaysız pencerede olay başına skor tanımsız")
    return (poisson_logl(aday, n)-poisson_logl(taban, n))/float(N)


def crs_gunluk(gunler, zaman, ds, asigma, tau_dot):
    """Her günün başlangıç durumu: önceki gerçek basamaklar, o günkü olaylar yok."""
    ta = asigma / np.asarray(tau_dot, float)
    lx = np.zeros(len(ta)); j = 0
    once = min(gunler[0], zaman[0]) if len(zaman) else gunler[0]
    out = np.empty((len(gunler), len(ta)))
    for i, a in enumerate(gunler):
        while j < len(zaman) and zaman[j] < a:
            lx = basamak(gevset(lx, (zaman[j]-once).total_seconds()/86400, ta), ds[j], asigma)
            once = zaman[j]; j += 1
        lx = gevset(lx, (a-once).total_seconds()/86400, ta); once = a
        out[i] = integral(lx, 1., ta)
    return out


def etas_gunluk(model, katalog, izgara, gunler, omori_kutle=None):
    """Ortak arayüzle aynı günlük beklenti; çekirdekler yalnız bir kez hesaplanır."""
    h = katalog[katalog.mw >= model.m0].copy()
    u, pay, kernel = model.uzay(izgara, h)
    p = model.parametre
    t = np.array([(z-gunler[0]).total_seconds()/86400 for z in h.zaman])
    ages = np.arange(len(gunler))[:, None]-t[None, :]
    mask = ages > 0
    ages = np.maximum(ages, 0.)
    if omori_kutle is None:
        I = (_omori_ilke(ages+1., p["c"], p["p"])[0]-_omori_ilke(ages, p["c"], p["p"])[0])*mask
    else:
        # Ortak tabanın kararlı integralini aynen kullan; parametreler değişmez.
        I = omori_kutle(ages, ages+1., p["c"], p["p"])*mask
    I *= p["K"]*10**(p["alpha"]*(h.mw.to_numpy()-model.m0))[None, :]
    return p["mu"]*u[None, :] + I @ kernel, u, pay


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    from knotenlinie.yollar import KOSU, VERI
    parser.add_argument("--katalog", default=str(VERI / "kesik-2015/CPTI15_v4.0_le2015.csv"))
    parser.add_argument("--fay", default=str(VERI / "diss320/iss320.geojson"))
    parser.add_argument("--cikti", required=True, help="$KNOTENLINIE_RUNS altında yeni koşu dizini")
    parser.add_argument("--adim", type=float, default=1.)
    parser.add_argument("--gear1-gunluk", help="aynı grid hücrelerinde M≥4.95 günlük beklenen .npy")
    args = parser.parse_args(argv)
    out = Path(args.cikti)
    try:
        out.resolve().relative_to(KOSU.resolve())
    except ValueError:
        raise ValueError("çıktı $KNOTENLINIE_RUNS altında olmalı") from None
    out.mkdir(parents=True, exist_ok=True)
    bas = time.monotonic()
    d = katalog_oku(args.katalog); f = fay_oku(args.fay)
    ayar = d[(d.zaman < AYAR_SON) & (d.mw >= 4.)].copy()
    b = float(np.log10(np.e)/(ayar.mw.mean()-4.+.005))
    a = pd.Timestamp("1985-01-01T00:00:00Z")
    t = np.array([(z-a).total_seconds()/86400 for z in ayar.zaman])
    fit = mle_temporal(t, ayar.mw.to_numpy(), 4., b, 0., (AYAR_SON-a).total_seconds()/86400, maksiter=300)
    if not fit["basari"]:
        raise RuntimeError("ETAS temporal ayarı yakınsamadı")
    p = dict(fit["parametreler"], D=10., q=1.5, gamma=.5)
    model = Model(p, ayar, f, b=b)
    g = izgara_uret(args.adim)
    gunler = pd.date_range(a, "2015-12-31T00:00:00Z", freq="D")
    etas, u, pay = etas_gunluk(model, d, g, gunler)
    zaman, ds = k9_basamaklari(d, f)
    train = gunler < AYAR_SON
    n_train = sayim(d, g, gunler, 4.)
    # CRS Asigma ve ağırlık yalnız ≤2010 M≥4.0 skorunda seçilir; w=0 açık null.
    adaylar = []; eniyi = None
    for asigma in (30000., 100000., 300000.):
        ratios = crs_gunluk(gunler, zaman, ds, asigma, f.tau_dot_pa_gun.to_numpy())
        fark = p["mu"] * u[None, :] * (ratios @ pay.T - 1.)
        for w in (0., .1, .25, .5, 1.):
            forecast = etas + w*fark
            score = poisson_logl(forecast[train], n_train[train])
            adaylar.append({"asigma_pa": asigma, "agirlik": w, "logL_ayar": score})
            if eniyi is None or score > eniyi["logL_ayar"]:
                eniyi = dict(adaylar[-1]); secili = forecast.copy()
    validate = ~train
    fraction = buyukluk_paylari([4.95, np.inf], 4., b)[0]
    n = sayim(d, g, gunler, 4.95)[validate]
    e = etas[validate]*fraction; crs = secili[validate]*fraction
    dallanma = p["K"]*p["c"]**(1-p["p"])/(p["p"]-1)*b/(b-p["alpha"])
    sonuc = {"kapsam": "retrospektif İtalya dikdörtgeni; CSEP grid değil",
             "izgara_adim_derece": args.adim,
             "etas_sonsuz_uzay_zaman_dallanma": dallanma,
             "uretim_kapisi": "yalnız prototip; ortak taban, CSEP grid ve bağımsız inceleme bekliyor",
             "ayar": "1985-01-01 / 2010-12-31", "dogrulama": "2011-01-01 / 2015-12-31",
             "esik_mw": 4.95, "n_ayar_m4": int(n_train[train].sum()), "n_dogrulama": int(n.sum()),
             "alici_sayisi": len(f), "kaynak_sayisi": int((d.mw>=5).sum()), "kaynak_zaman_sayisi": len(zaman),
             "hucre_sayisi": len(g), "etas": p, "b": b, "crs_secili": eniyi,
             "logL_etas": poisson_logl(e, n), "logL_etas_crs": poisson_logl(crs, n),
             "beklenen_etas": float(e.sum()), "beklenen_etas_crs": float(crs.sum()),
             "ig_crs_eksi_etas_nat_olay": bilgi_kazanci(crs, e, n),
             "ig_crs_eksi_gear1_nat_olay": None,
             "gear1_durum": "M≥4.95 ortak grid günlük kütlesi verilmedi; deney A yerel alt kenarı 5.95, ekstrapolasyon yok",
             "girdi": [{"yol": path, "sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest()}
                        for path in (args.katalog, args.fay)], "tarama": adaylar}
    # Tanı amaçlı sabit alternatif; validation'dan seçim yapılmaz.
    alt = crs_gunluk(gunler, zaman, ds, 100000., f.tau_dot_pa_gun.to_numpy())
    sabit = (etas+.25*p["mu"]*u[None, :]*(alt @ pay.T-1.))[validate]*fraction
    sonuc["ig_sabit_100kpa_w025_eksi_etas"] = bilgi_kazanci(sabit, e, n)
    sonuc["logL_sabit_100kpa_w025"] = poisson_logl(sabit, n)
    sonuc["beklenen_sabit_100kpa_w025"] = float(sabit.sum())
    # Validation yılları tanı için; ağırlık/Asigma yeniden seçilmez.
    sonuc["yillik"] = []
    for yil in range(2011, 2016):
        mask = gunler[validate].year == yil
        sayi = int(n[mask].sum())
        sonuc["yillik"].append({"yil": yil, "n": sayi,
            "ig_secili_eksi_etas": bilgi_kazanci(crs[mask], e[mask], n[mask]) if sayi else None,
            "ig_sabit_eksi_etas": bilgi_kazanci(sabit[mask], e[mask], n[mask]) if sayi else None})
    if args.gear1_gunluk:
        gear = np.load(args.gear1_gunluk, allow_pickle=False)
        if gear.shape == (len(g),):
            gear = np.broadcast_to(gear, n.shape)
        sonuc["ig_crs_eksi_gear1_nat_olay"] = bilgi_kazanci(crs, gear, n)
        sonuc["gear1_durum"] = "aynı günlük grid kütlesi verildi; GEAR1 veri bağımlılığı retrospektif"
    sonuc["duvar_saniye"] = time.monotonic()-bas
    sonuc["fit"] = fit
    (out/"sonuc.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=2, allow_nan=False))
    (out/"parametre.json").write_text(json.dumps({"ayar_son": AYAR_SON.isoformat(), "etas": p, "b": b,
                                                  "asigma_pa": eniyi["asigma_pa"], "agirlik": eniyi["agirlik"]}, indent=2))
    g.to_csv(out/"izgara.csv", index=False)
    np.savez_compressed(out/"gunluk.npz", etas=e, etas_crs=crs, sayim=n, sabit=sabit)
    print(json.dumps({k: v for k, v in sonuc.items() if k not in ("tarama", "fit", "girdi")}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
