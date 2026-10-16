"""Deney X skor defteri: ortak olay/gün defter biçimini yazar (U için)."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

OLAY_SUTUN = ['zaman', 'enlem', 'boylam', 'mw', 'hucre', 'kutu', 'gun', 'lam']
GUN_SUTUN = ['gun', 'Lam295', 'Lam395']


def olay_cercevesi(hedef, ci, mi, lam, gun_str):
    """M>=2.95 hedef başına bir satır; `lam` o günün hücre/kutu oranı."""
    if not (len(hedef) == len(ci) == len(mi) == len(gun_str) == len(lam)):
        raise ValueError('Defter olay dizileri hizalı değil')
    return pd.DataFrame({
        'zaman': hedef.zaman.dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ').to_numpy(),
        'enlem': hedef.enlem.to_numpy(float),
        'boylam': hedef.boylam.to_numpy(float),
        'mw': hedef.mw.to_numpy(float),
        'hucre': np.asarray(ci, int),
        'kutu': np.asarray(mi, int),
        'gun': np.asarray(gun_str),
        'lam': np.asarray(lam, float),
    })[OLAY_SUTUN]


def gun_cercevesi(gunler, lam295, lam395):
    """Gün başına bir satır; sıfır olaylı günler de dahil."""
    gunler = pd.DatetimeIndex(gunler)
    return pd.DataFrame({'gun': gunler.strftime('%Y-%m-%d').to_numpy(),
                         'Lam295': np.asarray(lam295, float),
                         'Lam395': np.asarray(lam395, float)})[GUN_SUTUN]


def yaz(kok, model, donem, olay, gun):
    """`<model>__<donem>__olay.csv.gz` ve `...__gun.csv.gz` yazar."""
    kok = Path(kok)
    kok.mkdir(parents=True, exist_ok=True)
    yol_olay = kok / f'{model}__{donem}__olay.csv.gz'
    yol_gun = kok / f'{model}__{donem}__gun.csv.gz'
    olay.to_csv(yol_olay, index=False, compression='gzip')
    gun.to_csv(yol_gun, index=False, compression='gzip')
    return yol_olay, yol_gun
