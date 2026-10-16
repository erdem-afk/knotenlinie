"""Gerçek ortak tabanla küçük kontrol; tam F2 ölçümü değildir."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import time

import numpy as np
import pandas as pd

from .dalga2 import ORTAK_DIZINI, RAPOR_DIZINI, alici_paylari, melez
from .girdi import AYAR_SON, fay_oku, k9_basamaklari
from .italya import crs_gunluk
from .ortak_taban import TopluOrtak, OrtakCRS
from knotenlinie.yollar import VERI


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ortak', type=Path, default=ORTAK_DIZINI)
    parser.add_argument('--fay', type=Path, default=VERI / 'diss320/iss320.geojson')
    args = parser.parse_args(argv)
    from knotenlinie.ortak_zemin.arayuz import model_yukle, omori_kutle
    from knotenlinie.ortak_zemin.veri import katalog_oku
    before = time.monotonic()
    taban = model_yukle('italya', args.ortak)
    d = katalog_oku(args.ortak/'italya_katalog_le2015.csv')
    h = d[(d.zaman >= taban.baslangic) & (d.zaman < AYAR_SON) & (d.mw >= taban.mc)]
    h = pd.concat([h.tail(4), h[h.mw >= 5.].tail(4)]).drop_duplicates().sort_values('zaman').reset_index(drop=True)
    batch = TopluOrtak(taban, h, omori_kutle)
    f = fay_oku(args.fay)
    days = pd.date_range(AYAR_SON, periods=3, freq='D')
    e = batch.gunluk(days)
    ts, ds = k9_basamaklari(h, f)
    ri = crs_gunluk(days, ts, ds, 100000., f.tau_dot_pa_gun.to_numpy())
    expected = melez(e, batch.arka_plan, ri, alici_paylari(taban.izgara, f), .25)
    m = OrtakCRS(taban, f, asigma_pa=100000., agirlik=.25)
    max_base, max_mix = 0., 0.
    for i, a in enumerate(days):
        z = a+pd.Timedelta(days=1)
        base = taban.beklenen(a, z, h, taban.izgara, [taban.mc, np.inf])[:, 0]
        mix = m.beklenen(a, z, h, taban.izgara, [taban.mc, np.inf])[:, 0]
        np.testing.assert_allclose(e[i], base, atol=1e-14, rtol=2e-12)
        np.testing.assert_allclose(expected[i], mix, atol=1e-14, rtol=2e-12)
        max_base = max(max_base, float(np.abs(e[i]-base).max()))
        max_mix = max(max_mix, float(np.abs(expected[i]-mix).max()))
    files = [args.ortak/x for x in ('italya_katalog_le2015.csv', 'etas_italya_le2010.json', 'italya_izgara.csv')]+[args.fay]
    result = dict(durum='gecti', kapsam='yalnız sekize kadar ayar ebeveyni ve üç gün; F2 IG ölçümü değil',
                  ebeveyn=len(h), hucre=len(taban.izgara), gun=len(days),
                  alici=len(f), kaynak_zamani=len(ts),
                  max_mutlak_fark_etas=max_base, max_mutlak_fark_melez=max_mix,
                  duvar_saniye=time.monotonic()-before,
                  girdi=[dict(yol=str(p), sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files])
    (RAPOR_DIZINI/'DENEME2.json').write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n')
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
