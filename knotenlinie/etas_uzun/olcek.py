"""R'nin geçmiş pencerede sabit toplam ölçeği; doğrulama burada okunmaz."""
import numpy as np
import pandas as pd
from knotenlinie.etas import model as M
from knotenlinie.etas_uzun.mle import Olabilirlik, ayarla, b_ayarla
from knotenlinie.etas_uzun.maske import maskeli_hist
from knotenlinie.ortak_zemin.arka_plan import BANTLAR_KM, ZEMIN_PAYLARI
from knotenlinie.ortak_zemin.arayuz import utc
from knotenlinie.ortak_zemin.veri import hucre_indeks
from .arayuz import ebeveynler, UzunETAS

AYAR_SON = '2006-01-01T00:00:00Z'
OLCEK_SON = '2011-01-01T00:00:00Z'
KUTU = (13., 13.8, 42., 42.6)


def kde_sec(d, grid, kutu):
    """R ile aynı adaylar; ≤2000/2001–2005 iç bölmesi."""
    end, split = utc(AYAR_SON), utc('2001-01-01T00:00:00Z')
    if not len(d) or (d.zaman >= end).any() or (hucre_indeks(d, grid) < 0).any():
        raise ValueError('KDE yalnız maskede <2006 hedefler')
    train, hold = d[d.zaman < split], d[d.zaman >= split]
    if not len(train) or not len(hold):
        raise ValueError('KDE iç bölmesi boş')
    trials = []
    for h in BANTLAR_KM:
        for eps in ZEMIN_PAYLARI:
            hist = maskeli_hist(train, grid, kutu, h, eps)
            u = M.arka_plan_degeri(hold.boylam.to_numpy(), hold.enlem.to_numpy(), hist)
            trials.append(dict(bant_km=h, zemin_payi=eps, logL_konum=float(np.log(u).sum())))
    best = max(trials, key=lambda r: r['logL_konum'])
    hist = maskeli_hist(d, grid, kutu, best['bant_km'], best['zemin_payi'])
    hist['secim'] = dict(kurulum_bitis_haric=split.isoformat(), secim_bitis_haric=end.isoformat(),
                        kurulum_n=len(train), secim_n=len(hold), yeniden_kurulum_n=len(d),
                        yeniden_kurulum_max_zaman=d.zaman.max().isoformat(), en_iyi=best, adaylar=trials)
    return hist


def kur(raw, grid, maksiter=300):
    """1985–2005 tam maskeli R-ortak MLE; gelecek girdi reddedilir."""
    epoch, end = utc('1985-01-01T00:00:00Z'), utc(AYAR_SON)
    if (raw.zaman >= end).any():
        raise ValueError('MLE girdisi <2006 olmalı')
    box = (grid.enlem_min.min(), grid.enlem_max.max(), grid.boylam_min.min(), grid.boylam_max.max())
    d = ebeveynler(raw, box, end)
    target = d[hucre_indeks(d, grid) >= 0].reset_index(drop=True)
    mc = np.where(target.zaman < utc('2005-01-01T00:00:00Z'), 3.1, 2.5)
    bmeta = b_ayarla(target.mw.to_numpy(), mc)
    hist = kde_sec(target, grid, box)
    t = ((d.zaman-epoch)/pd.Timedelta(days=1)).to_numpy(float)
    T = float((end-epoch)/pd.Timedelta(days=1))
    change = float((utc('2005-01-01T00:00:00Z')-epoch)/pd.Timedelta(days=1))
    u = M.arka_plan_degeri(d.boylam.to_numpy(), d.enlem.to_numpy(), hist)
    L = Olabilirlik(t, d.mw.to_numpy(), d.boylam.to_numpy(), d.enlem.to_numpy(), bmeta['deger'], T, change, grid, box, u)
    fit = ayarla(L, 'ortak', maksiter=maksiter)
    fit.update(mc=2.5, b=bmeta, baslangic_yili=1985, ayar_baslangic=epoch.isoformat(), ayar_bitis=end.isoformat(),
               ayar_max_zaman=d.zaman.max().isoformat(), ayar_n=len(d), hedef_n=len(target), dis_ebeveyn_n=len(d)-len(target),
               kutu=box, arka_plan=hist, metrik=M.yerel_metrik(box).kayit(), normalizasyon=M.NORMALIZASYON,
               uzay_ayar_destegi='CSEP İtalya maskesi; dış dikdörtgen yalnız ebeveyn erişim sınırı',
               maske_kenar=L.mask.kenar,
               tamlik=dict(donemler=[dict(bas='1985-01-01', son='2005-01-01', Mc=3.1),
                                     dict(bas='2005-01-01', son='2006-01-01', Mc=2.5)],
                           referans_Mc=2.5, eksik_ebeveyn='impute edilmez; gözlenen-ebeveyn koşullu ETAS'))
    return fit


def model_kur(p, grid, kaskad=True):
    return UzunETAS(p, grid, adim=32, nesil=10 if kaskad else 0)


def dis_maskeleri(events, grid, kutu=KUTU):
    """Kapalı olay kutusu; alan integrali için hizalı hücrelerin tümü."""
    x0, x1, y0, y1 = kutu
    g = np.round(grid[['boylam_min', 'boylam_max', 'enlem_min', 'enlem_max']].to_numpy(float), 12)
    overlap = (g[:, 0] < x1) & (g[:, 1] > x0) & (g[:, 2] < y1) & (g[:, 3] > y0)
    inside = (g[:, 0] >= x0) & (g[:, 1] <= x1) & (g[:, 2] >= y0) & (g[:, 3] <= y1)
    if np.any(overlap != inside):
        raise ValueError('L\'Aquila kutusu hücre sınırlarıyla hizalı değil')
    x, y = np.round(events.boylam.to_numpy(float), 12), np.round(events.enlem.to_numpy(float), 12)
    event_inside = (x >= x0) & (x <= x1) & (y >= y0) & (y <= y1)
    return ~event_inside, ~inside


def geometrik_olcek(n_all, lam_all, n_out, lam_out):
    vals = np.asarray([n_all, lam_all, n_out, lam_out], float)
    if not np.isfinite(vals).all() or (vals <= 0).any() or n_out > n_all or lam_out > lam_all+1e-10:
        raise ValueError('Ölçek N/Λ pozitif, sonlu ve dış≤tüm olmalı')
    all_c, out_c = float(n_all/lam_all), float(n_out/lam_out)
    return dict(tum=dict(N=int(n_all), Lambda=float(lam_all), c=all_c),
                LAquila_dis=dict(N=int(n_out), Lambda=float(lam_out), c=out_c),
                c=float(np.sqrt(all_c*out_c)), kural='sqrt(c_tum*c_LAquila_dis)')


def olcek_hesapla(run, grid):
    if utc(run.cerceve[0]) != utc(AYAR_SON) or utc(run.cerceve[1]) != utc(OLCEK_SON):
        raise ValueError('Ölçek yalnız 2006–2010 penceresinde')
    if (run.olaylar.zaman >= utc(OLCEK_SON)).any() or (run.olaylar.mw < 3.95-1e-12).any():
        raise ValueError('Ölçek hedefi <2011 M≥3.95 olmalı')
    out_events, out_cells = dis_maskeleri(run.olaylar, grid)
    return geometrik_olcek(len(run.olaylar), run.beklenen.sum(), int(out_events.sum()), run.beklenen[out_cells].sum())


class Olcekli:
    """Son oran yüzeyine sabit çarpan; çekirdek/kaskad parametresi değişmez."""
    def __init__(self, model, c):
        if not np.isfinite(c) or c <= 0:
            raise ValueError('Ölçek pozitif/sonlu olmalı')
        self.model, self.c = model, float(c)

    def beklenen(self, a, z, h, grid, edges):
        return self.c*self.model.beklenen(a, z, h, grid, edges)
