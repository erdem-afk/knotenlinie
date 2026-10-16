"""K9 -- earthquake-to-earthquake Coulomb transfer.

Each source event gets one or more slip models from :func:`slip_saglayici
<knotenlinie.kanal.tektonik_kaynak.kaynak_slip_saglayici>` (the WC94 scaled rectangle until SRCMOD
lands), the Okada 1992 kernel of ``knotenlinie.elastik`` gives the ``(3, 3)`` NED stress tensor at each
receiver, and the tensor is resolved on **the receiver fault's own DISS plane** -- its normal and
slip unit vectors -- never on an optimally oriented plane and never on Delta-CFS's maximum plane.
Delta-CFS itself is computed by the ledger reader; a channel file stores only ``tau_Pa`` and
``sigma_n_Pa`` in the ledger's sign convention (tension positive, shear along the rake).

The source list comes only from seal-clean catalogs: calibration is every event up to
2015-12-31T23:59:59.999999Z; a blind-window path adds only events strictly after the handover and
strictly before the window.  All receivers are stored for every source, however small the step --
the ledger decides what is negligible, not a threshold in the code.  K9 is used only in the hybrid
ETAS-Coulomb variant (Reverso, Steacy & Marsan 2018) and never enters the ETAS background rate.

Every slip model is a **separate ledger variant** (``k9_v0_wc94``, ``k9_v0_srcmod_<id>``): a
single-model run is labelled as such in its acceptance evidence and its gain may not be reported as
a multi-model gain (several slip models per event).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from typing import Iterable, List, Optional, Sequence

import numpy as np
import pandas as pd

from knotenlinie.defter import fay_tablosu_dogrula, fay_tablosu_oku, gerilmeyi_coz
from knotenlinie.defter.kod import girdi_ozeti
from knotenlinie.kanal.tektonik_defter import is_oku, is_yaz, yaz_kanal
from knotenlinie.kanal.tektonik_kaynak import (
    CPTI15_ADLARI, CPTI15_KAYNAK, KESIM, KesimIhlali, MuhurIhlali, YAN_KAYIT_DIZINI,
    kaynak_listesi, kaynak_slip_saglayici, kaynaklari_coz, kesim_kapisi, muhur_bloku_uret,
    muhur_kok_kapisi,
)
from knotenlinie.yollar import KOSU
from knotenlinie.kanal.tektonik_okada import (
    ElastikYok, alici_noktasi, fay_normal_kayma, gerilme_tensoru,
)

#: Roots whose existing K9 ledgers are historical: a K9 run may add a **new** file name there
#: but never overwrite one.
DONMUS_KOKLER = (str(KOSU / "defter-donmus"),)

#: The sibling manifest that a DISS 3.2.0 fault-table build writes next to ``geometry/``.
_DISS_MANIFEST = "muhur-manifest.json"
_MUHUR_ANI = pd.Timestamp("2021-01-01T00:00:00Z")

KANAL = "K9"
URETICI = "K9/v0: Okada1992 (knotenlinie/elastik) + WC94 source scaling, receiver=DISS plane"
ISARET = {"normal": "tension_positive", "kayma": "rake_positive"}
KANAL_SURUM_ONEK = "k9_v0_"
KABUL_KANIT = (
    "King, Stein & Lin 1994 (10.1785/BSSA0840030935) ve Stein 1999 (10.1038/45144): "
    "alıcı fayın kendi DISS düzleminde Delta-CFS; hesap sunucusu katmanı <=2015 bir Orta Apenin olayının "
    "pozitif Delta-CFS loblarını yayımlanmış artçı dağılımıyla karşılaştırır. "
    "Bu kayıt tek model koşusuysa çok modelli kazanç sayılmaz."
)
_GEcerli_MODEL = re.compile(r"[^0-9A-Za-z_]+")


# --- the channel ---------------------------------------------------------------------------

def model_kanal_surumu(model_id: str) -> str:
    """``k9_v0_<model_id>`` with a filesystem-safe model id."""
    m = _GEcerli_MODEL.sub("_", str(model_id)).strip("_")
    if not m:
        raise ValueError(f"model kimliği boş ya da yalnız geçersiz karakter: {model_id!r}")
    return KANAL_SURUM_ONEK + m


def _olaylar(kaynaklar) -> List[dict]:
    """The source events as plain records (a DataFrame or an iterable of mappings)."""
    if isinstance(kaynaklar, pd.DataFrame):
        df = kaynaklar.copy()
        df["time_utc"] = pd.to_datetime(df["time_utc"], utc=True)
        return df.to_dict("records")
    out = []
    for k in kaynaklar:
        r = dict(k)
        r["time_utc"] = pd.to_datetime(r["time_utc"], utc=True)
        out.append(r)
    return out


def aktarim_hesabi(kaynaklar, alicilar, slip_saglayici, *, cekirdek=None,
                   kelvin: bool = True) -> pd.DataFrame:
    """One row per source event, slip model and receiver fault: the K9 step channel.

    ``cekirdek`` defaults to :func:`knotenlinie.kanal.tektonik_okada.gerilme_tensoru`; tests
    inject a stub so the channel is exercised without ``knotenlinie.elastik``.  Every receiver
    of ``alicilar`` gets a row; an event with no model inside the distance cutoff is skipped
    (its plane is undefined), never given a guessed one.
    """
    cekirdek = cekirdek or gerilme_tensoru
    f = fay_tablosu_dogrula(alicilar.copy() if isinstance(alicilar, pd.DataFrame) else pd.DataFrame(alicilar))
    N, S = fay_normal_kayma(f)
    noktalar = [alici_noktasi(satir) for _, satir in f.iterrows()]
    kayitlar = _olaylar(kaynaklar)

    satirlar: List[dict] = []
    for olay in kayitlar:
        zaman = pd.Timestamp(olay["time_utc"])
        for model in slip_saglayici(olay):
            model_id = str(model.get("model_id", "wc94"))
            mesafe = model.get("mesafe_km")
            for i, nokta in enumerate(noktalar):
                sigma = cekirdek(model, nokta, kelvin=kelvin)
                tau, sn = gerilmeyi_coz(np.asarray(sigma, dtype=np.float64), N[i], S[i])
                satirlar.append({
                    "fault_id": str(nokta["fault_id"]),
                    "time_utc": zaman,
                    "kind": "step",
                    "tau_Pa": float(tau),
                    "sigma_n_Pa": float(sn),
                    "kaynak_id": str(model.get("kaynak_id", olay.get("event_id", ""))),
                    "model_id": model_id,
                    "mesafe_km": float(mesafe) if mesafe is not None else np.nan,
                })
    sutunlar = ("fault_id", "time_utc", "kind", "tau_Pa", "sigma_n_Pa",
                "kaynak_id", "model_id", "mesafe_km")
    df = pd.DataFrame(satirlar, columns=list(sutunlar))
    if len(df):
        # keep microseconds: pandas 2's default nanosecond column overflows for pre-1677 events
        # (CPTI15 starts in 1349), so build the tz-aware column through Python datetimes
        yerel = []
        for z in df["time_utc"]:
            t = pd.Timestamp(z)
            t = t.tz_localize("UTC") if t.tzinfo is None else t.tz_convert("UTC")
            yerel.append(t.to_pydatetime().replace(tzinfo=None))
        df["time_utc"] = pd.Series(np.array(yerel, dtype="datetime64[us]"),
                                   index=df.index).dt.tz_localize("UTC")
    return df


def kabul_kaydi(kanit: Optional[str] = None, *, tur: str = "yayimlanmis",
                tek_model: bool = False) -> dict:
    """The K9 acceptance record; ``kanit`` defaults to the published King/Stein/Stein reading."""
    metin = KABUL_KANIT if kanit is None else str(kanit)
    if tek_model:
        metin += (" TEK MODEL KOŞUSU: bu kanal varyantı tek bir kayma modeliyle üretildi; "
                  "kazancı çok modelli kazanç olarak raporlanamaz.")
    return {"gecti": True, "tur": str(tur), "kanit": metin}


# --- write gate, fault-table gate and input provenance -----------------------------------------

def _defter_hedefi(yol, surum: str) -> str:
    """The parquet path ``yaz_kanal`` will write: a non-``.parquet`` target is a directory."""
    yol = os.fspath(yol)
    if yol.endswith(".parquet"):
        return yol
    return os.path.join(yol, f"{KANAL}_{surum}.parquet")


def _hedef_kapisi(hedef, *, yeniden_yaz: bool = False) -> None:
    """Refuse to overwrite an existing K9 output unless explicitly allowed.

    ``knotenlinie.defter.yazici`` writes through a temp file and ``os.replace``, so it silently replaces
    an existing ledger; this gate is the only overwrite check.  Under a root in
    :data:`DONMUS_KOKLER` a K9 file may only be created (a new name); an existing one is refused
    even with ``yeniden_yaz``.  The target and the frozen roots are compared by
    realpath, so a symlink into a frozen root cannot evade the check.
    """
    mutlak = os.path.realpath(os.fspath(hedef))
    if not os.path.exists(mutlak):
        return
    for kok in DONMUS_KOKLER:
        kok = os.path.realpath(os.fspath(kok))
        if mutlak == kok or mutlak.startswith(kok + os.sep):
            raise ValueError(
                f"{hedef}: dönmüş kök {kok} altında; orada yalnız yeni bir K9 dosya adı "
                "yazılabilir, mevcut dosya üzerine yazılmaz"
            )
    if not yeniden_yaz:
        raise ValueError(
            f"{hedef}: hedef dosya zaten var; üzerine yazmak için --yeniden-yaz gerekir"
        )


def _girdi_kayitlari(kaynaklar, faylar=None, srcmod=None, acilan=None, yan_koku=None) -> List[dict]:
    """Provenance records (basename + sha256 + role) for every file the run reads.

    The ledger provenance ``girdiler`` schema is kept; a record is ``{"yol": basename, "sha256": hex,
    "rol": role}`` so the provenance field carries what the run actually opened, by base name,
    not the full operator path.  When ``acilan`` (the report's opened basenames) is given, only
    the catalogue files it names are hashed, so a glob-refused year file is never opened even for
    the digest.  The CPTI15 binding sidecar is read from ``<yan_koku>/yan-kayit/cpti15/`` (never
    from beside the CSV) and recorded with its own sha256.  A directory ``--srcmod``
    is named but not hashed (it is not a file and its parser does not exist yet).
    """
    izinli_adlar = None if acilan is None else set(acilan)
    kayitlar: List[dict] = []
    for yol in kaynaklari_coz(kaynaklar):
        ad = os.path.basename(os.fspath(yol))
        if izinli_adlar is not None and ad not in izinli_adlar:
            continue
        kayitlar.append({"yol": ad, "sha256": girdi_ozeti(os.fspath(yol)), "rol": "kaynak"})
        if ad in CPTI15_ADLARI and yan_koku is not None:
            yan = os.path.join(os.fspath(yan_koku), YAN_KAYIT_DIZINI, CPTI15_KAYNAK, ad + ".json")
            if os.path.isfile(yan):
                kayitlar.append({"yol": os.path.basename(yan),
                                 "sha256": girdi_ozeti(yan), "rol": "cpti15-sidecar"})
    if faylar is not None:
        kayitlar.append({"yol": os.path.basename(os.fspath(faylar)),
                         "sha256": girdi_ozeti(os.fspath(faylar)), "rol": "faylar"})
    if srcmod is not None and os.path.isfile(os.fspath(srcmod)):
        kayitlar.append({"yol": os.path.basename(os.fspath(srcmod)),
                         "sha256": girdi_ozeti(os.fspath(srcmod)), "rol": "srcmod"})
    return kayitlar


#: The only date spellings a DISS table cell may carry: ``YYYYMMDD`` or an ISO date (time optional).
_FAY_TARIH_DESENI = r"^(\d{8}|\d{4}-\d{2}-\d{2}([T ].*)?)$"


def _fay_tarih_serisi(seri):
    """A ``created``/``updated`` column parsed as UTC timestamps (``YYYYMMDD`` or ISO).

    Any other spelling (an epoch number, a bare year, free text) is ``NaT``: it is never read as a
    date, so an epoch-ms value cannot parse as 1970 and pass as pre-2021.
    """
    metin = seri.astype(str).str.strip()
    gecerli = metin.str.match(_FAY_TARIH_DESENI)
    t = pd.to_datetime(metin.where(gecerli), errors="coerce", format="%Y%m%d", utc=True)
    eksik = t.isna() & gecerli
    if bool(eksik.any()):
        t = t.copy()
        t.loc[eksik] = pd.to_datetime(metin[eksik], errors="coerce", format="ISO8601", utc=True)
    return t


def _fay_tarihleri(yol):
    """Tri-state of the table's dates plus its frame: True (<2021), False (>=2021), None (unknown).

    A parsed 2021+ value is a veto that no manifest can override; an absent or
    unparseable pair is ``None`` (the manifest may then be the only proof).
    """
    try:
        df = pd.read_parquet(os.fspath(yol))
    except Exception:
        return None, None
    if not {"created", "updated"} <= set(df.columns):
        return None, df
    olusma = _fay_tarih_serisi(df["created"])
    guncelleme = _fay_tarih_serisi(df["updated"])
    # the veto runs on every parsed value first, so an unparseable cell elsewhere cannot hide a
    # 2021+ one; only then does any unparseable cell make the state unknown
    if bool((olusma >= _MUHUR_ANI).any() or (guncelleme >= _MUHUR_ANI).any()):
        return False, df
    if olusma.isna().any() or guncelleme.isna().any():
        return None, df
    return True, df


def _fay_surumlu(df) -> bool:
    """True when a version-like column names DISS 3.2.0 (the table's own version proof)."""
    for c in ("version", "surum", "kaynak", "source", "kaynak_surum"):
        if c in df.columns and df[c].astype(str).str.contains("DISS 3.2.0", regex=False).any():
            return True
    return False


def _sha256satiri(sums_yolu, ad: str, beklenen: str) -> bool:
    """True when ``SHA256SUMS`` lists ``ad`` with the ``beklenen`` digest (GNU two-space form)."""
    try:
        with open(sums_yolu, encoding="utf-8") as akis:
            for satir in akis:
                parcalar = satir.rstrip("\n").split("  ")
                if len(parcalar) == 2 and parcalar[1] == ad and parcalar[0] == beklenen:
                    return True
    except OSError:
        return False
    return False


def _diss_manifesti_temiz(yol) -> bool:
    """True when the exact fault-table build layout binds the table to a DISS 3.2.0 manifest.

    Only the published layout is accepted: ``<root>/geometry/sources.parquet``,
    ``<root>/muhur-manifest.json`` and ``<root>/SHA256SUMS``.  The sums must list
    ``geometry/sources.parquet`` with the parquet's sha256 and ``muhur-manifest.json`` with the
    manifest's own sha256; the manifest's ``kural``/``kaynak`` must carry the seal rule and
    ``DISS 3.2.0``.  No parent-directory lookup is done (a stale manifest elsewhere is ignored).
    """
    yol = os.path.realpath(os.fspath(yol))
    if os.path.basename(yol) != "sources.parquet":
        return False
    if os.path.basename(os.path.dirname(yol)) != "geometry":
        return False
    kok = os.path.dirname(os.path.dirname(yol))
    manifest = os.path.join(kok, _DISS_MANIFEST)
    sums = os.path.join(kok, "SHA256SUMS")
    if not (os.path.isfile(manifest) and os.path.isfile(sums)):
        return False
    if not _sha256satiri(sums, "geometry/sources.parquet", girdi_ozeti(yol)):
        return False
    if not _sha256satiri(sums, "muhur-manifest.json", girdi_ozeti(manifest)):
        return False
    try:
        with open(manifest, encoding="utf-8") as akis:
            kayit = json.load(akis)
    except (OSError, ValueError):
        return False
    if not isinstance(kayit, dict):
        return False
    return ("created or updated >= 2021-01-01 dropped" in str(kayit.get("kural", ""))
            and "DISS 3.2.0" in str(kayit.get("kaynak", "")))


def fay_tablosu_kapisi(faylar) -> None:
    """Refuse a fault table that cannot prove it carries no sealed (>=2021) record.

    A 2021+ ``created``/``updated`` value is a veto that no manifest can override.
    Otherwise two proofs are accepted: the table's own cells all before 2021-01-01 plus a version
    column naming DISS 3.2.0, or the exact fault-table build manifest/SHA256SUMS layout.  A table with
    neither is refused by name.
    """
    tarih, df = _fay_tarihleri(faylar)
    if tarih is False:
        raise MuhurIhlali(
            f"{os.path.basename(os.fspath(faylar))}: fay tablosunda 2021 ya da sonrası tarihli "
            "kayıt var; dosya reddedildi"
        )
    if tarih is True and df is not None and _fay_surumlu(df):
        return
    if _diss_manifesti_temiz(faylar):
        return
    raise MuhurIhlali(
        f"{os.path.basename(os.fspath(faylar))}: fay tablosunun 2021 öncesi olduğu "
        "kanıtlanamıyor (created/updated ya da tam muhur-manifest.json/SHA256SUMS düzeni yok); "
        "dosya reddedildi"
    )


def yaz(yol, satirlar: pd.DataFrame, *, kabul, muhur, girdiler: Sequence = (),
        modeller: Optional[Iterable[str]] = None,
        kesim: Optional[str] = None, yeniden_yaz: bool = False) -> List[str]:
    """Publish one ledger file per slip model; a selected subset is labelled single-model.

    ``kesim`` is the cutoff actually used, carried into the acceptance record that
    :func:`knotenlinie.kanal.tektonik_defter.yaz_kanal` already writes (the provenance sidecar has no generic
    slot and ``referans_donem`` has its own fixed meaning, so the acceptance record is the
    honest place for a run-level cutoff; ``kabul_dogrula`` passes the extra key through).
    Every target file is checked through :func:`_hedef_kapisi` before the writer touches it.
    """
    tumu = sorted({str(m) for m in satirlar["model_id"].unique()}) if len(satirlar) else []
    secili = tumu if modeller is None else sorted({str(m) for m in modeller})
    bilinmeyen = sorted(set(secili) - set(tumu))
    if bilinmeyen:
        raise ValueError(f"seçilen model satırlarda yok: {bilinmeyen}; satırlarda: {tumu}")
    tek = len(tumu) == 1 or len(secili) == 1
    kayit = dict(kabul)
    if len(secili) < len(tumu):
        kayit = kabul_kaydi(kayit.get("kanit"), tur=str(kayit.get("tur", "yayimlanmis")),
                            tek_model=True)
    if kesim is not None:
        kayit["kesim_kullanilan"] = str(kesim)
    yollar: List[str] = []
    for m in secili:
        surum = model_kanal_surumu(m)
        hedef = _defter_hedefi(yol, surum)
        _hedef_kapisi(hedef, yeniden_yaz=yeniden_yaz)
        # the sidecar is written beside the parquet by the same atomic step; guard it too
        _hedef_kapisi(hedef[: -len(".parquet")] + ".provenance.json", yeniden_yaz=yeniden_yaz)
        d = satirlar.loc[satirlar["model_id"] == m].reset_index(drop=True)
        yollar.append(yaz_kanal(
            yol, kanal=KANAL, surum=surum, satirlar=d, tur="step",
            isaret=dict(ISARET), girdiler=girdiler, kabul=kayit, uretici=URETICI,
            deprem_girdisi=True, muhur=muhur, referans_donem=None,
        ))
    return yollar


def aktar(kaynaklar, faylar, *, kesim: str = KESIM, srcmod=None, mod: Optional[str] = None,
          cekirdek=None, kelvin: bool = True, muhur=None, _muhursuz_test: bool = False):
    """Compute K9's rows: source list -> one plane per event -> tensor -> receiver resolution.

    The magnitude threshold is the declared :data:`KAYNAK_ESIK_MW` only; no operator-supplied floor
    is accepted here, because a threshold chosen to shape a result would be an undeclared free
    parameter fitted to earthquake data.  The cutoff is refused before any read when it is later than the declared
    :data:`KESIM`; an earlier cutoff is allowed and its use is recorded in the report and in the
    ledger's acceptance record.

    When ``muhur`` (the seal/data root) is given, ``muhur_bloku_uret`` runs and every
    ``--kaynaklar``/``--srcmod`` path must resolve under ``<muhur>/deprem`` **before any catalogue
    is opened**; :func:`fay_tablosu_kapisi` then gates ``--faylar``.  ``muhur`` is also the data root the
    CPTI15 sidecar is read from (``<muhur>/yan-kayit/cpti15/``).  An ordinary caller with
    ``muhur=None`` is refused; only the tests' explicit ``_muhursuz_test=True`` (a test-only
    keyword) may read without a seal root, and it still needs ``muhur`` to find the sidecar.
    """
    kesim_kapisi(kesim)
    if muhur is None and not _muhursuz_test:
        raise MuhurIhlali(
            "aktar: mühür kökü (muhur=) verilmedi; mühürsüz katalog okuma yalnız "
            "_muhursuz_test=True ile (test katmanı)"
        )
    if muhur is not None and not _muhursuz_test:
        muhur_kok_kapisi(kaynaklar, muhur, srcmod=srcmod)
        fay_tablosu_kapisi(faylar)
    f = fay_tablosu_oku(faylar)
    atilan: dict = {}
    kaynak_raporu: dict = {}
    kaynak_df = kaynak_listesi(kaynaklar, kesim=kesim, atilan=atilan, rapor=kaynak_raporu,
                               yan_koku=muhur)
    saglayici = kaynak_slip_saglayici(kaynak_df, f,
                                      mod=mod if mod is not None else ("srcmod" if srcmod else "wc94"),
                                      srcmod_dizin=srcmod)
    bas = time.time()
    df = aktarim_hesabi(kaynak_df, f, saglayici, cekirdek=cekirdek, kelvin=kelvin)
    parametresiz = list(atilan.get("parametresiz", []))
    buyukluksuz = list(atilan.get("buyukluksuz", []))
    katalog = kaynak_raporu.get("katalog") or {}
    parcalar = list(katalog.get("parcalar", []))
    # the reader's own per-catalogue counts; a sealed row raises, so atilan_muhur sums to 0
    atilan_kesim = sum(int(p.get("atilan_kesim", 0) or 0) for p in parcalar)
    muhur_satiri = sum(int(p.get("atilan_muhur", 0) or 0) for p in parcalar)
    rapor = {
        "kaynak_sayisi": int(len(kaynak_df)),
        "alisan_sayisi": int(len(f)),
        "satir": int(len(df)),
        "modeller": sorted({str(m) for m in df["model_id"].unique()}) if len(df) else [],
        "duvar_saniye": round(time.time() - bas, 3),
        "kesim": str(kesim),
        "kesim_kullanilan": kaynak_raporu.get("kesim_kullanilan"),
        "kesim_dar": bool(kaynak_raporu.get("kesim_dar", False)),
        # the per-catalogue report was computed all along and dropped; surface it here.
        # Messages/counts/basenames only, never a cell, as the existing rule requires.
        "kataloglar": parcalar,
        "dosyalar_okunan": [ad for p in parcalar for ad in p.get("acilan", [])],
        "dosyalar_reddedilen": [ad for p in parcalar for ad in p.get("acilmayan", [])],
        "kesimde_kesilen": int(atilan_kesim + int(kaynak_raporu.get("kesim_ustu", 0) or 0)),
        "muhur_satiri": int(muhur_satiri),
        # the source list's drop report: magnitude-less rows are named, never silently lost
        "parametresiz": len(parametresiz),
        "parametresiz_olaylar": parametresiz,
        "buyukluksuz": len(buyukluksuz),
        "buyukluksuz_olaylar": buyukluksuz,
    }
    if muhur is not None:
        # the basename + sha256 of every file this run opened (the ledger's ``girdiler`` schema);
        # built after the reads so a year-refused file is never opened for its digest either.
        rapor["girdiler"] = _girdi_kayitlari(
            kaynaklar, faylar, srcmod, acilan=rapor["dosyalar_okunan"], yan_koku=muhur)
    return df, rapor


# --- CLI ----------------------------------------------------------------------------------

def _kabul_oku(yol) -> dict:
    with open(os.fspath(yol), encoding="utf-8") as akis:
        kayit = json.load(akis)
    if not isinstance(kayit, dict) or "kanit" not in kayit:
        kayit = {"kanit": str(kayit)}
    return kabul_kaydi(kayit.get("kanit"), tur=str(kayit.get("tur", "yayimlanmis")))


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(prog="knotenlinie.kanal.k9", description="K9 depremden depreme aktarım")
    sub = p.add_subparsers(dest="komut", required=True)

    a = sub.add_parser("aktar", help="hesapla; --arac verilirse ara tabloyu yaz")
    a.add_argument("--kaynaklar", nargs="+", required=True, help="katalog yolları/globları")
    a.add_argument("--faylar", required=True)
    a.add_argument("--kesim", default=KESIM)
    a.add_argument("--srcmod", default=None, help="SRCMOD dizini (varsa)")
    a.add_argument("--arac", default=None, help="ara satır tablosu (parquet)")
    a.add_argument("--cikti", default=None, help="defter dizini (yayımlamak için --kabul/--muhur gerekir)")
    a.add_argument("--kabul", default=None, help="kabul kaydı JSON dosyası")
    a.add_argument("--muhur", required=True,
                   help="mühür kökü (scripts/muhur.py çalıştırılır; --kaynaklar altında olmalı)")
    a.add_argument("--model", action="append", default=None, help="yalnız bu model(ler), --cikti ile")
    a.add_argument("--yeniden-yaz", action="store_true",
                   help="var olan hedefin üzerine yaz (dönmüş kökler hariç)")

    y = sub.add_parser("yaz", help="ara tablodan defter dosyalarını yayımla")
    y.add_argument("--arac", required=True)
    y.add_argument("--cikti", required=True)
    y.add_argument("--kabul", required=True)
    y.add_argument("--muhur", required=True)
    y.add_argument("--model", action="append", default=None, help="yalnız bu model(ler)")
    y.add_argument("--yeniden-yaz", action="store_true",
                   help="var olan hedefin üzerine yaz (dönmüş kökler hariç)")

    g = p.parse_args(argv)
    if g.komut == "aktar":
        try:
            df, rapor = aktar(g.kaynaklar, g.faylar, kesim=g.kesim, srcmod=g.srcmod,
                              muhur=g.muhur)
        except KesimIhlali as exc:
            print(f"REDDEDİLDİ: {exc}")
            return 2
        except ElastikYok as exc:
            print(f"DETERMINED-PENDING: {exc}")
            return 3
        print(json.dumps(rapor, ensure_ascii=False, sort_keys=True))
        girdiler = rapor.get("girdiler") or []
        if g.cikti:
            if not g.kabul:
                raise SystemExit("yayımlamak için --kabul zorunlu")
            kabul = _kabul_oku(g.kabul)
            muhur = muhur_bloku_uret(g.muhur)
            yollar = yaz(g.cikti, df, kabul=kabul, muhur=muhur,
                         girdiler=girdiler, modeller=g.model,
                         kesim=rapor.get("kesim_kullanilan"), yeniden_yaz=g.yeniden_yaz)
            for yol in yollar:
                print(yol)
        elif g.arac:
            _hedef_kapisi(g.arac, yeniden_yaz=g.yeniden_yaz)
            is_yaz(g.arac, df, kabul=_kabul_oku(g.kabul) if g.kabul else kabul_kaydi(),
                   girdiler=girdiler, ek=rapor)
        else:
            raise SystemExit("ne --arac ne --cikti verildi; çıktı yazılmadı")
        return 0

    df, meta = is_oku(g.arac)
    ek = meta.get("ek") or {}
    yollar = yaz(g.cikti, df, kabul=_kabul_oku(g.kabul), muhur=muhur_bloku_uret(g.muhur),
                 girdiler=meta["girdiler"], modeller=g.model,
                 kesim=ek.get("kesim_kullanilan"), yeniden_yaz=g.yeniden_yaz)
    for yol in yollar:
        print(yol)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
