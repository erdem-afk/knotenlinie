"""≤2015 CPTI15 ve DISS 3.2.0 ISS; K9/Okada değişmeden kullanılır."""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

from knotenlinie.diss320.tablo import iss_oku, muhurle
from knotenlinie.defter.geometri import fay_vektorleri, fay_tablosu_dogrula
from knotenlinie.etas.katalog import cpti15_oku, bolge_sec
from knotenlinie.kanal.k9 import aktarim_hesabi
from knotenlinie.kanal.tektonik_kaynak import wc94_saglayici, kayma_gerilme_hizi
from knotenlinie.kanal.tektonik_okada import KAYNAK_ANAHTARLARI, voigt_den_tensor
from knotenlinie.elastik import okada_ned
from knotenlinie.defter.coulomb import coulomb

KUTU = (35., 48., 6., 20.)
SON = pd.Timestamp("2016-01-01T00:00:00Z")
AYAR_SON = pd.Timestamp("2011-01-01T00:00:00Z")


def katalog_oku(yol):
    """Yalnız açıkça kesilmiş CPTI15 dosyası; kör satır sayımı bile yapılmaz."""
    if Path(yol).name != "CPTI15_v4.0_le2015.csv":
        raise ValueError("yalnız CPTI15_v4.0_le2015.csv kabul edilir")
    d, rapor = cpti15_oku(str(yol))
    if rapor["atilan_kesim"]:
        raise ValueError("girdi kör dönem içeriyor; kesilmiş girdi gerekir")
    d = bolge_sec(d, KUTU)
    d = d[d.time_utc >= pd.Timestamp("1985-01-01T00:00:00Z")].copy()
    d = d.rename(columns={"time_utc": "zaman", "lat": "enlem", "lon": "boylam",
                          "mag": "mw", "depth_km": "derinlik"})
    return d.sort_values("zaman", kind="stable").reset_index(drop=True)


def fay_oku(yol):
    """ISS düzlemleri; CSS+ISS çift sayımı yok, 126 ISS ile sınırlı v0."""
    if Path(yol).name != "iss320.geojson":
        raise ValueError("DISS 3.2.0 iss320.geojson gerekir")
    ham, atilan = muhurle(iss_oku(yol))
    if atilan:
        raise ValueError("DISS girdisinde mühürlü kayıt var")
    if any(k["updated_utc"] >= AYAR_SON for k in ham):
        # DISS 3.2.0 2015 vintage: bu bir retrospektif girdidir, ayar tarihinin ürünü değil.
        vintage = "2015-vintage-retrospektif"
    else:
        vintage = "pre2011"
    rows = []
    for k in ham:
        # ISS yüzey dikdörtgeninin dört köşesinin merkezi (derecede düzlemsel v0).
        row = {"id": k["idsource"], "centroid_lat": np.mean([k[a] for a in ("latul", "latur", "latll", "latlr")]),
               "centroid_lon": np.mean([k[a] for a in ("lonul", "lonur", "lonll", "lonlr")]),
               "depth_central_km": (k["mindepth"] + k["maxdepth"]) / 2,
               "strike_central_deg": k["strike"], "dip_central_deg": k["dip"],
               "rake_central_deg": k["rake"], "length_km": k["length"], "width_km": k["width"],
               "slip_mm_yr": (k["srmin"] + k["srmax"]) / 2}
        n, s = fay_vektorleri(k["strike"], k["dip"], k["rake"])
        row.update(dict(zip(("normal_n", "normal_e", "normal_d", "slip_n", "slip_e", "slip_d"), np.r_[n, s])))
        rows.append(row)
    f = fay_tablosu_dogrula(pd.DataFrame(rows))
    f["tau_dot_pa_gun"] = kayma_gerilme_hizi(f.slip_mm_yr, f.width_km, f.length_km) / 365.25
    if np.any(~np.isfinite(f.tau_dot_pa_gun)) or np.any(f.tau_dot_pa_gun <= 0):
        raise ValueError("ISS yükleme hızı sonlu ve pozitif değil")
    f.attrs["vintage"] = vintage
    return f


def k9_basamaklari(gecmis, faylar, mu_prime=.4):
    """M≥5 kaynaklardan K9 basamakları; vektör Okada sonucu K9'a önbellekten verilir."""
    if len(gecmis) and (gecmis.zaman >= SON).any():
        raise ValueError("2016+ kaynak yasak")
    d = gecmis[gecmis.mw >= 5.].rename(columns={"zaman": "time_utc", "enlem": "lat", "boylam": "lon", "mw": "mag"})
    saglayici = wc94_saglayici(faylar)
    cache = {}
    ids = {str(fid): i for i, fid in enumerate(faylar.id)}
    def cekirdek(model, alici, kelvin=True):
        key = tuple(float(model[k]) for k in KAYNAK_ANAHTARLARI)
        if key not in cache:
            cache[key] = voigt_den_tensor(okada_ned(
                kaynak={k: model[k] for k in KAYNAK_ANAHTARLARI},
                alici_lat=faylar.centroid_lat.to_numpy(),
                alici_lon=faylar.centroid_lon.to_numpy(),
                alici_derinlik_m=faylar.depth_central_km.to_numpy() * 1000))
        return cache[key][ids[str(alici["fault_id"])]]
    kanal = aktarim_hesabi(d, faylar, saglayici, cekirdek=cekirdek)
    if not len(kanal):
        return pd.DatetimeIndex([], tz="UTC"), np.zeros((0, len(faylar)))
    kanal["dcfs_pa"] = coulomb(kanal.tau_Pa, kanal.sigma_n_Pa, mu_prime=mu_prime)
    p = kanal.pivot_table(index="time_utc", columns="fault_id", values="dcfs_pa", aggfunc="sum")
    p = p.reindex(columns=faylar.id, fill_value=0).fillna(0).sort_index()
    return pd.DatetimeIndex(p.index), p.to_numpy(float)
