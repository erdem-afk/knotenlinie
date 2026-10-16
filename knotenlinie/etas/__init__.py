"""Catalog-only baselines for Knotenlinie.

This package implements the non-ML catalogue baselines that physical channels are
compared against:

* **ETAS** (Ogata 1988, 1998), with the triggering kernel not replaced by a physical
  kernel;
* **background / triggered separation** by stochastic declustering (Zhuang,
  Ogata & Vere-Jones 2002);
* **ETAS-D**, the plain ETAS plus a detection probability (hour of day,
  day of week, day of year, and a rate-dependent incompleteness after large
  events; Omi et al. 2014, Hainzl 2016).

Everything is fitted on catalogs up to the 2015-12-31 cutoff only and frozen for
the blind test; the frozen model definition records the fit span, the data and the
parameters.  No pretrained product is used, so nothing trained on 2016–2020 can
enter by construction.

Clean-room implementation from the equations published in Ogata 1988/1998,
Zhuang et al. 2002, Omi et al. 2014 and Hainzl 2016; no code copied from the pyetas package
(AGPL), the CRAN ETAS package (GPL) or Zhuang's Fortran sd package.

The detection terms of ETAS-D are a *detection* model, not a stress modulation.  The
ETAS baseline parameters are not the parameter budget of the physical response terms:
that budget limits the physical response terms (Aσ and ṡr) to at most two free numbers;
the ETAS baseline has its own parameters and nobody should read them as part of that budget.
"""

__version__ = "0.1.0"
