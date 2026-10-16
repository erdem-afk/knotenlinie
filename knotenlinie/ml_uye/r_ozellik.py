"""R-ortak-kaskad'ın M>=3,1 hücre-gün oranı (ML-artık özelliği); önbellekli."""
from __future__ import annotations

import json
from pathlib import Path
import time

import numpy as np
import pandas as pd

EPOCH_DAY0 = pd.Timestamp('1985-01-01', tz='UTC')


def gun_ts(d):
    return EPOCH_DAY0 + pd.Timedelta(days=int(d))


def r_model(json_yol, raw, grid, ayar_ici=False):
    from knotenlinie.etas_uzun.arayuz import TamGecmis, UzunETAS
    m = UzunETAS(json.loads(Path(json_yol).read_text()), grid, adim=32, nesil=10)
    if ayar_ici:
        # Eğitim özelliği: R'nin ayar penceresi içindeki günlerde (örneklem-içi) oranı. Paket kapısı
        # (ayar_son <= a) yalnız bu örnekte açılır; paket kodu değişmez.
        m.taban.ayar_son = EPOCH_DAY0
    return TamGecmis(m, raw), m


def r_hesapla(json_yol, raw, grid, gunler, yol=None, ilerleme=200, ayar_ici=False):
    """gunler: tam sayı gün no'ları (1985-01-01'den). Dönüş (len, n) float32 oran (olay/gün).

    ``yol`` verilirse ``.npz`` (gunler, oran) önbelleği okunur ya da yazılır.
    """
    gunler = np.asarray(gunler, int)
    if yol is not None and Path(yol).exists():
        with np.load(yol) as z:
            if np.array_equal(z['gunler'], gunler):
                return z['oran']
    tg, _ = r_model(json_yol, raw, grid, ayar_ici)
    edges = np.array([3.1, np.inf])
    out = np.empty((len(gunler), len(grid)), np.float32)
    t0 = time.monotonic()
    for i, d in enumerate(gunler):
        a = gun_ts(d)
        out[i] = tg.beklenen(a, a + pd.Timedelta(days=1), None, grid, edges)[:, 0]
        if ilerleme and i and i % ilerleme == 0:
            print('  R önbellek %d/%d, %.0f s' % (i, len(gunler), time.monotonic() - t0), flush=True)
    if yol is not None:
        Path(yol).parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(yol, gunler=gunler, oran=out)
    return out


class RIndeks:
    """Önbellek dizisinden ``r_fn(a)``; olmayan gün hata (sessiz düşme yok)."""

    def __init__(self, gunler, oran):
        self.pos = {int(g): i for i, g in enumerate(gunler)}
        self.oran = oran

    def __call__(self, a):
        d = int(round((pd.Timestamp(a).tz_convert('UTC') - EPOCH_DAY0) / pd.Timedelta(days=1)))
        return self.oran[self.pos[d]]
