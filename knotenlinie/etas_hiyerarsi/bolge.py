"""Çekirdek bölgeleri: SCSN ve GeoNet için R-tipi (dönem Mc'li) ETAS ayarı + Hessian.

`knotenlinie/yan_tezgah/model.py::kur` D1 dalının bölge-bağımsız kopyasıdır; fark: olabilirlik nesnesi
saklanır (Hessian için) ve ızgara/kutu dışarıdan verilebilir. Dondurulmuş paketlere dokunmaz.
Kesme (records/Y/KURAL.md): SCSN 100 km + 365,25 gün, GeoNet 100 km.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from knotenlinie.yan_tezgah import model as YM
from knotenlinie.yan_tezgah import mle as ML
from knotenlinie.yan_tezgah import okuyucu as O
from knotenlinie.yan_tezgah.kesme import BOLGE_KESME
from knotenlinie.ortak_zemin.veri import VERI
from . import cekirdek as C

CIKTI = VERI / 'ortak/hiyerarsi'
YAN = VERI / 'yan'
KESME = dict(BOLGE_KESME)
# bolge -> (ilk tamlik yılı, taban Mc)
AYAR = {'scsn': (None, None), 'geonet': (None, None)}


def katalog(bolge):
    df = O.oku(YAN, bolge)
    return df, O.izgara(bolge), YM.kutu(bolge)


def d1_kur(df, grid, kutu, *, ayar_son, bas_yil=None, taban_mc=None, rmax_km=100.0, tmax_gun=None,
           maks_cift=20_000_000):
    """D1 (dönem Mc'li R-tipi) olabilirlik nesnesi; ayar verisi zaman < ayar_son."""
    son = YM._utc(ayar_son)
    fit = df[df.zaman < son]
    if bas_yil is not None:
        fit = fit[fit.zaman.dt.year >= int(bas_yil)]
    fit = fit.reset_index(drop=True)
    if not len(fit):
        raise ValueError('ayar penceresinde olay yok')
    if (fit.zaman >= son).any():
        raise ValueError('ayar sonrası olay')
    y0 = int(fit.zaman.dt.year.min()) if bas_yil is None else int(bas_yil)
    tm = O.tamlik(fit, y0, int(fit.zaman.dt.year.max()), hkj=False)
    if taban_mc is not None:
        tm = YM._taban_kirp(tm, float(taban_mc))
    mc0 = float(tm['mc_min'])
    mc_olay = np.asarray(tm['donem_mc'], float)
    m_all = fit.mw.to_numpy(float)
    kullan = m_all >= mc_olay - 1e-9
    b = ML.b_ayarla(m_all[kullan], mc_olay[kullan])
    bd = float(b['deger'])
    epoch = YM._utc(fit.zaman.min())
    T = float((son - epoch) / YM.GUN)
    t = ((fit.zaman - epoch) / YM.GUN).to_numpy(float)
    araliklar = YM._araliklar_donem(tm, mc0, bd, epoch, T)
    L = ML.Olabilirlik(t[kullan], m_all[kullan], fit.boylam.to_numpy(float)[kullan],
                       fit.enlem.to_numpy(float)[kullan], bd, T, mc0, mc_olay[kullan],
                       araliklar, grid, kutu, maks_cift=int(maks_cift), rmax_km=rmax_km, tmax_gun=tmax_gun)
    bilgi = dict(pencereler=tm['pencereler'], b=b, ayar_son=son.isoformat(), n_fit=int(kullan.sum()),
                 mc0=mc0, bas_yil=y0, kesme=dict(rmax_km=rmax_km, tmax_gun=tmax_gun), tam_cift=int(L.cift),
                 epoch=epoch.isoformat(), T_gun=T)
    return L, mc0, bilgi


def bolge_ayari(bolge, ayar_son, *, maksiter=400, hessian=True, maks_cift=80_000_000):
    t0 = time.monotonic()
    df, grid, kutu = katalog(bolge)
    bas_yil, taban = AYAR[bolge]
    kes = KESME[bolge]
    L, mc0, bilgi = d1_kur(df, grid, kutu, ayar_son=ayar_son, bas_yil=bas_yil, taban_mc=taban,
                           rmax_km=kes['rmax_km'], tmax_gun=kes['tmax_gun'], maks_cift=maks_cift)
    print(f'{bolge} <{ayar_son}: n={len(L.t)} çift={L.cift} mc0={mc0} b={L.b:.4f} kur={time.monotonic()-t0:.0f}s',
          flush=True)
    fit = ML.ayarla(L, 'ortak', maksiter=int(maksiter))
    print(f'{bolge} MLE: logL={fit["logL"]:.2f} n={fit["dallanma"]:.6f} nit={fit["nit"]} '
          f'basari={fit["basari"]} s={time.monotonic()-t0:.0f}', flush=True)
    kayit = C.bolge_kaydi(f'{bolge}<{ayar_son[:4]}', fit, L, mc0, kovaryans=hessian)
    kayit.update(bolge=bolge, ayar_son=ayar_son, bilgi=bilgi, duvar_saniye=time.monotonic() - t0,
                 baslangic_sonuclari=fit.get('baslangic_sonuclari'))
    return kayit


def yaz(kayit, yol):
    Path(yol).parent.mkdir(parents=True, exist_ok=True)
    Path(yol).write_text(json.dumps(kayit, ensure_ascii=False, indent=1, default=float, allow_nan=False) + '\n')


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--bolge', choices=sorted(AYAR), required=True)
    ap.add_argument('--ayar-son', required=True, help='dışlayıcı sınır, ör. 2006-01-01T00:00:00Z')
    ap.add_argument('--maksiter', type=int, default=400)
    ap.add_argument('--maks-cift', type=int, default=80_000_000)
    ap.add_argument('--cikti', type=Path, default=None)
    a = ap.parse_args(argv)
    k = bolge_ayari(a.bolge, a.ayar_son, maksiter=a.maksiter, maks_cift=a.maks_cift)
    yol = a.cikti or CIKTI / f'cekirdek_{a.bolge}_le{int(a.ayar_son[:4]) - 1}.json'
    yaz(k, yol)
    print(yol, flush=True)


if __name__ == '__main__':
    main()
