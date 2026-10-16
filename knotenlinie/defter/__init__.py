"""Common ledger code: schema, writer, reader, Coulomb, provenance.

The code shared by every channel (schema, writer, reader,
Coulomb stress, provenance) is written once, by one hand, before any channel is
built; a channel then writes only its own files.  This package is that code.

Public surface:
  * :mod:`knotenlinie.defter.sema`      schema versions and dispatch
  * :mod:`knotenlinie.defter.yazici`    writer with the acceptance gate and atomic publish
  * :mod:`knotenlinie.defter.okuyucu`   reader that computes Delta-CFS
  * :mod:`knotenlinie.defter.coulomb`   Delta-CFS and the mu' scan
  * :mod:`knotenlinie.defter.kunye`     provenance record
  * :mod:`knotenlinie.defter.geometri`  fault normal/slip vectors and stress resolution

Delta-CFS is never stored; the reader computes it.
"""
from __future__ import annotations

__version__ = "1.0.0"

from .coulomb import B_den_mu, coulomb, coulomb_taramasi, mu_den_B
from .geometri import fay_tablosu_dogrula, fay_tablosu_oku, fay_vektorleri, gerilmeyi_coz
from .kunye import girdi_ozeti, kunye_dogrula, kunye_olustur
from .okuyucu import Defter, oku, tensorden_coz
from .yazici import KabulHatasi, yaz

__all__ = [
    "__version__",
    "fay_vektorleri", "gerilmeyi_coz", "fay_tablosu_oku", "fay_tablosu_dogrula",
    "coulomb", "coulomb_taramasi", "mu_den_B", "B_den_mu",
    "yaz", "KabulHatasi",
    "oku", "Defter", "tensorden_coz",
    "kunye_olustur", "kunye_dogrula", "girdi_ozeti",
]
