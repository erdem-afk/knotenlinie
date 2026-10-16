"""Ledger writer: validate, convert the sign once, gate, publish atomically.

The writer turns one channel's own table into one parquet file plus its provenance
sidecar.  It validates the row schema, converts the channel's declared sign
convention to the stored convention exactly once, runs the acceptance gate *before* touching
the disk, refuses an earthquake-fed channel without a clean seal attestation,
and only then writes both files under ``.tmp`` names and ``os.replace`` s them into
place, so a failure leaves no half-written ledger.
"""
from __future__ import annotations

import json
import os
from typing import Iterable, Optional

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from . import kunye, sema, zaman
from .isaret import isaret_dogrula, isaret_uygula, s3_mi
from .kabul import KabulHatasi, kabul_dogrula, muhur_blogu
from .kod import simdi_utc
from .kunye import girdi_ozeti, girdileri_kaydet

__all__ = ["yaz", "KabulHatasi"]

TEMEL_SUTUNLAR = ("fault_id", "time_utc", "kind", "tau_Pa", "sigma_n_Pa")


def _yollar(yol, kanal: str, kanal_surum: str):
    """Target parquet and sidecar paths; a directory gets <kanal>_<surum> names."""
    yol = os.fspath(yol)
    if os.path.isdir(yol) or yol.endswith(os.sep):
        hedef = os.path.join(yol, f"{kanal}_{kanal_surum}.parquet")
    else:
        hedef = yol
    if not hedef.endswith(".parquet"):
        raise ValueError("defter hedefi .parquet uzantılı olmalı")
    return hedef, hedef[: -len(".parquet")] + ".provenance.json"


def _meta_kur(surum, kanal, kanal_surum, tur, kural, referans_donem, satir, kunye_ad,
              olusturma, uretici):
    """Parquet key-value metadata; every value is a string."""
    meta = {
        sema.SEMA_META_ANAHTARI: str(int(surum)),
        "kanal": str(kanal),
        "kanal_surum": str(kanal_surum),
        "tur": tur,
        "isaret": json.dumps(kural, sort_keys=True),
        "referans_donem": json.dumps(referans_donem, sort_keys=True) if referans_donem is not None else "",
        "birim": sema.BIRIM,
        "kunye": kunye_ad,
        "satir": str(int(satir)),
        "olusturma_utc": olusturma,
    }
    if uretici is not None:
        meta["uretici"] = str(uretici)
    return meta


def _duzenle(df: pd.DataFrame, surum: int) -> pd.DataFrame:
    """Canonical column order; unknown extra columns are kept at the end."""
    bilgi = sema.surum_bilgisi(surum)
    istenen = list(TEMEL_SUTUNLAR)
    istenen += [c for c in bilgi["secmeli"] if c in df.columns]
    istenen += [c for c in bilgi["zorunlu"] if c not in istenen]
    kalan = [c for c in df.columns if c not in istenen]
    return df[istenen + kalan]


def _tablo_yap(df: pd.DataFrame, meta: dict) -> pa.Table:
    """Arrow table with microsecond UTC timestamps and the ledger key-value metadata."""
    tablo = pa.Table.from_pandas(df, preserve_index=False)
    indeks = tablo.schema.get_field_index("time_utc")
    if indeks >= 0:
        alan = tablo.schema.field(indeks)
        if pa.types.is_timestamp(alan.type) and alan.type.tz == "UTC":
            tablo = tablo.set_column(
                indeks, "time_utc", tablo.column(indeks).cast(pa.timestamp("us", tz="UTC"))
            )
    mevcut = dict(tablo.schema.metadata or {})
    mevcut.update({k.encode("utf-8"): v.encode("utf-8") for k, v in meta.items()})
    return tablo.replace_schema_metadata(mevcut)


# The channel IDs that the ledger format reserves for an open pore pressure p (column p_Pa); every
# other channel must leave p_Pa empty.  The reader turns p into ΔCFS with μ = μ'/(1 − B), and each
# such channel stays in its own file (channels are never summed).
ACIK_BASINC_KANALLARI = ("K6", "K13")


def yaz(yol, *, kanal: str, kanal_surum: str, satirlar, isaret=None, referans_donem=None,
        girdiler: Iterable = (), kabul, deprem_girdisi: bool = False, muhur=None,
        uretici: Optional[str] = None, sema_surum: Optional[int] = None) -> str:
    """Publish one channel/version ledger file plus its provenance sidecar.

    ``satirlar`` carries the channel's own-convention ``tau_Pa`` and ``sigma_n_Pa``
    (plus optional ``p_Pa`` and the optional six-component tensor); the stored
    columns are always in the stored convention.
    """
    if not isinstance(satirlar, pd.DataFrame):
        satirlar = pd.DataFrame(satirlar)
    df = satirlar.copy()

    eksik = [c for c in TEMEL_SUTUNLAR if c not in df.columns]
    if eksik:
        raise ValueError(f"defter satırlarında eksik sütun: {eksik}")
    for ad in ("tau_Pa", "sigma_n_Pa"):
        if not pd.api.types.is_numeric_dtype(df[ad]):
            raise ValueError(f"{ad} sayısal değil; birim Pa olarak verilmeli")
        if df[ad].isna().any():
            raise ValueError(f"{ad} zorunlu alanda NaN var")
    if df["fault_id"].isna().any() or df["time_utc"].isna().any():
        raise ValueError("fault_id ve time_utc boş olamaz")
    df["time_utc"] = zaman.utc_yap(df["time_utc"])

    turler = sorted({str(t) for t in df["kind"]})
    if len(turler) != 1:
        raise ValueError(f"bir dosyada tek tür olmalı; bulunan: {turler}")
    tur = zaman.tur_dogrula(turler[0])

    if "p_Pa" in df.columns:
        if not pd.api.types.is_numeric_dtype(df["p_Pa"]):
            raise ValueError("p_Pa sayısal değil; Pa olarak verilmeli")
        if kanal not in ACIK_BASINC_KANALLARI and df["p_Pa"].notna().any():
            raise ValueError(f"p_Pa yalnız {ACIK_BASINC_KANALLARI} kanallarında dolu olabilir")

    tensor_var = [c for c in sema.TENSOR_SUTUNLARI if c in df.columns]
    if tensor_var and len(tensor_var) != len(sema.TENSOR_SUTUNLARI):
        raise ValueError("tensör sütunları altı bileşenin tümü ya da hiçbiri olmalı")
    if tensor_var:
        for c in sema.TENSOR_SUTUNLARI:
            if not pd.api.types.is_numeric_dtype(df[c]):
                raise ValueError(f"{c} sayısal değil; Pa olarak verilmeli")
        dolu = df[list(sema.TENSOR_SUTUNLARI)].notna()
        if not (dolu.all(axis=1) | ~dolu.any(axis=1)).all():
            raise ValueError("tensör satırları yarım; altı bileşen birlikte dolu ya da boş olmalı")

    kural = isaret_dogrula(isaret)
    if tensor_var and not s3_mi(kural):
        raise ValueError(
            "tensör sütunları saklama kuralında saklanır; tensörle birlikte yalnız varsayılan "
            "işaret beyanı kabul edilir, çünkü tensörün kendi işaret kuralı iki eksenle "
            "sessizce çevrilemez"
        )
    tau3, sn3 = isaret_uygula(df["tau_Pa"].to_numpy(), df["sigma_n_Pa"].to_numpy(), kural)
    df["tau_Pa"] = tau3          # conversion happened exactly once, here
    df["sigma_n_Pa"] = sn3

    kabul_dogrulanmis = kabul_dogrula(kabul)
    muhur_blogu(deprem_girdisi, muhur)

    surum = sema.guncel_surum() if sema_surum is None else int(sema_surum)
    bilgi = sema.surum_bilgisi(surum)
    if uretici is not None:
        df["uretici"] = str(uretici)
    eksik = [c for c in bilgi["zorunlu"] if c not in df.columns]
    if eksik:
        raise ValueError(f"şema v{surum} için eksik sütun: {eksik}")

    df = _duzenle(df, surum)
    girdi_kayitlari = girdileri_kaydet(girdiler)

    hedef, kunye_yolu = _yollar(yol, kanal, kanal_surum)
    kok = os.path.dirname(os.path.abspath(hedef))
    os.makedirs(kok, exist_ok=True)
    gecici, gecici_kunye = hedef + ".tmp", kunye_yolu + ".tmp"
    olusturma = simdi_utc()
    meta = _meta_kur(surum, kanal, kanal_surum, tur, kural, referans_donem, len(df),
                     os.path.basename(kunye_yolu), olusturma, uretici)

    try:
        pq.write_table(_tablo_yap(df, meta), gecici)
        ozet = girdi_ozeti(gecici)
        rec = kunye.kunye_olustur(
            kanal=kanal, kanal_surum=kanal_surum, sema_surum=surum,
            defter_dosya=os.path.basename(hedef), defter_sha256=ozet, satir=len(df),
            tur=tur, isaret=kural, referans_donem=referans_donem, girdiler=girdi_kayitlari,
            kabul=kabul_dogrulanmis, deprem_girdisi=deprem_girdisi, muhur=muhur,
            uretici=uretici, olusturma_utc=olusturma,
        )
        kunye.kunye_yaz(gecici_kunye, rec)
    except BaseException:
        for g in (gecici, gecici_kunye):
            if os.path.exists(g):
                os.remove(g)
        raise
    os.replace(gecici, hedef)
    os.replace(gecici_kunye, kunye_yolu)
    return hedef
