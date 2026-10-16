"""ETAS arka planını CRS ile modüle eden ortak, geçmişe-koşullu arayüz."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.special import ndtr, softmax

from knotenlinie.etas.model import yerel_metrik, mekan_olcegi, mekan_kutu_integrali, _omori_ilke
from .girdi import KUTU, SON, AYAR_SON, k9_basamaklari
from .oran import basamak, gevset, integral


@dataclass
class Model:
    """Ayar yalnız ≤2010; ETAS tetikleme korunur, CRS yalnız arka planı değiştirir."""
    parametre: dict
    ayar: pd.DataFrame
    faylar: pd.DataFrame
    m0: float = 4.0
    b: float = 1.0
    asigma_pa: float = 100000.0
    agirlik: float = 0.0
    sigma_km: float = 30.0

    def __post_init__(self):
        self.ayar = gecmis_dogrula(self.ayar, AYAR_SON)
        if self.ayar.empty:
            raise ValueError("ayar kataloğu boş")
        p = self.parametre
        if not all(np.isfinite(p[k]) for k in ("mu", "K", "c", "D", "p", "q", "alpha", "gamma")):
            raise ValueError("ETAS parametreleri sonlu olmalı")
        if not np.isfinite([self.m0, self.b, self.asigma_pa, self.agirlik, self.sigma_km]).all():
            raise ValueError("CRS parametreleri sonlu olmalı")
        if not all(p[k] > 0 for k in ("mu", "K", "c", "D")):
            raise ValueError("ETAS parametreleri pozitif olmalı")
        if p["p"] <= 1 or p["q"] <= 1 or not 0 <= p["alpha"] < self.b or not np.isfinite(p["gamma"]):
            raise ValueError("ETAS p,q>1 ve 0≤alpha<b gerekir")
        if not (0 <= self.agirlik <= 1 and self.asigma_pa > 0 and self.sigma_km > 0 and self.b > 0):
            raise ValueError("CRS parametreleri geçersiz")
        self._uzay_cache = {}
        self._k9_cache = None

    def uzay(self, izgara, gecmis):
        """KDE arka plan hücre kütlesi, alıcı payı ve tam ETAS hücre integrali."""
        g = izgara_dogrula(izgara)
        met = yerel_metrik(KUTU)
        x0, y0 = met.km(g.boylam_min.to_numpy(), g.enlem_min.to_numpy())
        x1, y1 = met.km(g.boylam_max.to_numpy(), g.enlem_max.to_numpy())
        tx, ty = met.km(self.ayar.boylam.to_numpy(), self.ayar.enlem.to_numpy())
        bx0, bx1, by0, by1 = met.kutu_km()
        s = self.sigma_km
        norm = (ndtr((bx1-tx)/s)-ndtr((bx0-tx)/s)) * (ndtr((by1-ty)/s)-ndtr((by0-ty)/s))
        u = np.mean(((ndtr((x1[:, None]-tx)/s)-ndtr((x0[:, None]-tx)/s))
                     * (ndtr((y1[:, None]-ty)/s)-ndtr((y0[:, None]-ty)/s))) / norm, axis=1)
        alan = (x1-x0)*(y1-y0) / ((bx1-bx0)*(by1-by0))
        u = .95 * u + .05 * alan  # önceden sabitlenmiş pozitif destek
        fx, fy = met.km(self.faylar.centroid_lon.to_numpy(), self.faylar.centroid_lat.to_numpy())
        pay = softmax(-(((x0+x1)[:, None]/2-fx)**2 + ((y0+y1)[:, None]/2-fy)**2)/(2*s*s), axis=1)
        hx = gecmis.boylam.to_numpy(float); hy = gecmis.enlem.to_numpy(float)
        key = (g.to_numpy(float).tobytes(), hx.tobytes(), hy.tobytes(), gecmis.mw.to_numpy(float).tobytes())
        if key not in self._uzay_cache:
            di = mekan_olcegi(self.parametre["D"], self.parametre["gamma"], gecmis.mw.to_numpy(), self.m0)
            kernel = np.empty((len(gecmis), len(g)))
            for i, row in enumerate(g.itertuples(index=False)):
                box = (row.enlem_min, row.enlem_max, row.boylam_min, row.boylam_max)
                kernel[:, i] = mekan_kutu_integrali(hx, hy, di, self.parametre["q"], box, metrik=met)
            self._uzay_cache = {key: np.maximum(kernel, 0.)}
        return u, pay, self._uzay_cache[key]

    def crs_integrali(self, baslangic, bitis, gecmis):
        """Yalnız t<başlangıç basamakları replay edilir; gelecek kaynak yok."""
        buyuk = gecmis.loc[gecmis.mw >= 5.]
        key = buyuk[["zaman", "enlem", "boylam", "mw", "event_id"]].to_json(date_format="iso")
        if self._k9_cache is None or self._k9_cache[0] != key:
            zaman, ds = k9_basamaklari(buyuk, self.faylar)
            self._k9_cache = (key, zaman, ds)
        _, zaman, ds = self._k9_cache
        return durum_integrali(baslangic, bitis, zaman, ds, self.asigma_pa,
                               self.faylar.tau_dot_pa_gun.to_numpy())

    def beklenen(self, baslangic, bitis, gecmis, izgara, m_kenarlar):
        """[başlangıç,bitiş) hücre×büyüklük; pencere içi olaylar kullanılmaz."""
        a, z = pencere_dogrula(baslangic, bitis)
        h = gecmis_dogrula(gecmis, a)
        h = h.loc[h.mw >= self.m0].copy()
        u, pay, kernel = self.uzay(izgara, h)
        dt = (z-a).total_seconds()/86400
        ages = np.array([(a-t).total_seconds()/86400 for t in h.zaman])
        p = self.parametre
        omori = (_omori_ilke(ages+dt, p["c"], p["p"])[0]
                 - _omori_ilke(ages, p["c"], p["p"])[0])
        trig = (p["K"]*10**(p["alpha"]*(h.mw.to_numpy()-self.m0))*omori) @ kernel
        modulation = dt if self.agirlik == 0 else ((1-self.agirlik)*dt + self.agirlik*(pay @ self.crs_integrali(a, z, h)))
        out = (p["mu"]*u*modulation + trig)[:, None] * buyukluk_paylari(m_kenarlar, self.m0, self.b)[None, :]
        if np.any(~np.isfinite(out)) or np.any(out < 0):
            raise ValueError("beklenen oran sonlu ve negatif olmayan değil")
        return out


def durum_integrali(baslangic, bitis, zaman, ds, asigma_pa, tau_dot):
    """Çoklu basamakta durum taşır; doğrusal basamak-oranı toplamı değildir."""
    ta = asigma_pa / np.asarray(tau_dot, float)
    lx = np.zeros_like(ta)
    zaman = pd.DatetimeIndex(zaman)
    ds = np.asarray(ds, float)
    if ds.shape != (len(zaman), len(ta)) or not zaman.is_monotonic_increasing:
        raise ValueError("basamak biçimi/sırası geçersiz")
    if len(zaman) and (zaman >= baslangic).any():
        raise ValueError("gelecek basamak kullanılamaz")
    once = zaman[0] if len(zaman) else baslangic
    for t, s in zip(zaman, ds):
        lx = basamak(gevset(lx, (t-once).total_seconds()/86400, ta), s, asigma_pa)
        once = t
    lx = gevset(lx, (baslangic-once).total_seconds()/86400, ta)
    return integral(lx, (bitis-baslangic).total_seconds()/86400, ta)


def gecmis_dogrula(d, baslangic):
    zorunlu = ["zaman", "enlem", "boylam", "derinlik", "mw"]
    if not set(zorunlu) <= set(d.columns):
        raise ValueError("geçmiş sütunları eksik")
    h = d.copy()
    # Ortak arayüz zaten UTC Timestamp alır; kör/mühürlü zamanlar hata olur, filtrelenmez.
    if not isinstance(h.zaman.dtype, pd.DatetimeTZDtype):
        raise ValueError("geçmiş zamanları UTC timezone-aware olmalı")
    if h.zaman.isna().any() or (h.zaman >= SON).any() or (h.zaman >= baslangic).any():
        raise ValueError("geçmişte kör/gelecek/geçersiz zaman")
    if not np.isfinite(h[["enlem", "boylam", "mw"]].to_numpy(float)).all():
        raise ValueError("geçmiş konum/büyüklük sonlu olmalı")
    if "event_id" not in h:
        h["event_id"] = ["crs-"+str(i) for i in range(len(h))]
    return h.sort_values("zaman", kind="stable").reset_index(drop=True)


def pencere_dogrula(a, z):
    a, z = pd.Timestamp(a), pd.Timestamp(z)
    if a.tzinfo is None or z.tzinfo is None or not a < z or z > SON:
        raise ValueError("UTC pencere ve bitiş≤2016-01-01 gerekir")
    return a.tz_convert("UTC"), z.tz_convert("UTC")


def izgara_dogrula(g):
    g = g[["boylam_min", "boylam_max", "enlem_min", "enlem_max"]].astype(float)
    if not np.isfinite(g.to_numpy()).all() or (g.boylam_max <= g.boylam_min).any() or (g.enlem_max <= g.enlem_min).any():
        raise ValueError("ızgara kenarları geçersiz")
    if (g.boylam_min < KUTU[2]).any() or (g.boylam_max > KUTU[3]).any() or (g.enlem_min < KUTU[0]).any() or (g.enlem_max > KUTU[1]).any():
        raise ValueError("ızgara İtalya v0 kutusunun dışında")
    return g


def buyukluk_paylari(kenarlar, m0, b):
    k = np.asarray(kenarlar, float)
    if k.ndim != 1 or len(k) < 2 or np.any(np.isnan(k)) or np.any(np.diff(k) <= 0) or k[0] < m0:
        raise ValueError("büyüklük kenarları artan ve ≥m0 olmalı")
    return 10**(-b*(k[:-1]-m0)) - 10**(-b*(k[1:]-m0))


_MODEL = None


def kur(model):
    """Koşucu ölçülmüş parametre ve açık girdilerle modeli bağlar; gizli okuma yok."""
    global _MODEL
    _MODEL = model


def yukle(parametre_yolu, ayar, faylar):
    """italya.py'nin ayar JSON'u ile ortak arayüzü bağla."""
    p = json.loads(Path(parametre_yolu).read_text())
    if p["ayar_son"] != AYAR_SON.isoformat():
        raise ValueError("parametre ayar kesimi uyuşmuyor")
    model = Model(p["etas"], ayar, faylar, b=p["b"], asigma_pa=p["asigma_pa"], agirlik=p["agirlik"])
    kur(model)
    return model


def beklenen(baslangic, bitis, gecmis, izgara, m_kenarlar):
    """Ortak deney H imzası; önce kur(Model(...)) ya da yukle(...) çağırılır."""
    if _MODEL is None:
        raise RuntimeError("CRS modeli bağlı değil; kur/yukle çağırın")
    return _MODEL.beklenen(baslangic, bitis, gecmis, izgara, m_kenarlar)
