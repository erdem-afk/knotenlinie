"""Shared elastic kernels: Okada 1992 rectangular dislocations and the frame helpers.

clean-room implementation from the equations published in Okada 1992 (BSSA 82(2),
1018-1040, DOI 10.1785/bssa0820021018); no code copied from cutde (MIT) or any other
Okada implementation.

This package computes **displacement and its spatial derivatives, hence strain and stress**
(λ = μ = 30 GPa).  It does **not** resolve a tensor onto a fault and does **not** compute
ΔCFS: that is ``knotenlinie.defter.geometri.gerilmeyi_coz`` and ``knotenlinie.defter.coulomb``,
the project's only implementation.  It never writes a ledger file.  Its consumer in this release
is the earthquake-to-earthquake Okada transfer of the CRS layer (``knotenlinie.kanal.k9``).
Sign convention: tension positive, shear along the DISS rake, NED frame; the stress output is the
ledger writer's ``s_xx_Pa … s_yz_Pa`` Voigt order.

Okada 1992 is built clean-room from the paper's Tables 6-9 and checked against all 81
finite-source values of Okada 1985 Table 2: ``okada_yerel`` takes a required ``egim_deg`` and
refuses receivers above the surface, ``okada_ned`` is the transfer call.

2.1.0 (okada-ned on the sphere): ``okada_ned`` projects receivers with the azimuthal-equidistant
``cerceve.aeqd_metre`` and rotates each NED tensor into the receiver's local NED by
``cerceve.yakinsama_rad``; both are public names.

The surface-load kernels (Boussinesq, Farrell 1972) of the earlier load channels are not part
of this release (the load channels are documented as measured negative results).
"""
from __future__ import annotations

__version__ = "2.1.0"

from .cerceve import (
    aeqd_metre,
    dud_gerilme,
    fay_gerilmesi,
    ned_metre,
    nede_yerel,
    yakinsama_rad,
    yerel_cerceve,
    yerelden_nede,
)
from .okada import okada_ned, okada_yerel
from .sabitler import E, G, LAM, MU, NU

__all__ = [
    "__version__",
    "LAM", "MU", "NU", "E", "G",
    "ned_metre", "aeqd_metre", "yakinsama_rad", "yerel_cerceve", "yerelden_nede", "nede_yerel",
    "dud_gerilme",
    "fay_gerilmesi",
    "okada_yerel", "okada_ned",
]
