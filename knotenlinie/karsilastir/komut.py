"""Küçük sentetik prova ve yalnız kesik CPTI15 ile İtalya iç doğrulaması."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .kosucu import IZGARA, SUTUNLAR, Model, kos, karsilastir, katalog_kontrol
from .puan import PuanHatasi, log_olabilirlik, eslestirilmis, tutarlilik
from .tabanlar import csep_xml

from knotenlinie.yollar import VERI  # noqa: E402

KESIK = VERI / 'kesik-2015'
CSEP_DOSYALAR = {
    'HAZFX-BPT': 'akinci.HAZFX_BPT.italy.10yr.2010-01-01.xml',
    'TripleS-CPTI': 'zechar.TripleS-CPTI.italy.10yr.2010-01-01.xml',
    'MPS04': 'meletti.MPS04.italy.10yr.2010-01-01.xml',
}


def json_temiz(x):
    """Standart JSON; NaN/inf yerine ölçülemedi etiketi/null."""
    if isinstance(x, dict):
        return {k: json_temiz(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [json_temiz(v) for v in x]
    if isinstance(x, (np.bool_, bool)):
        return bool(x)
    if isinstance(x, (float, np.floating)):
        return float(x) if np.isfinite(x) else None
    if isinstance(x, np.integer):
        return int(x)
    return x


def sentetik():
    """Bilinen Poisson dünyası: doğru uzaysal model ve tam eşitlik."""
    rng = np.random.default_rng(20261005)
    dogru = np.array([[3200.0, 800.0], [800.0, 200.0]])
    taban = np.full((2, 2), 1250.0)
    n = rng.poisson(dogru)
    a, b = np.repeat(dogru.ravel(), n.ravel()), np.repeat(taban.ravel(), n.ravel())
    iyi = eslestirilmis(a, b, dogru.sum(), taban.sum())
    esit = eslestirilmis(a, a, dogru.sum(), dogru.sum())
    return dict(kip='sentetik; gerçek olay yok', tohum=20261005, gozlem=n.tolist(),
                dogru_logL=log_olabilirlik(dogru, n), taban_logL=log_olabilirlik(taban, n),
                daha_iyi=iyi, esit=esit, tutarlilik=tutarlilik(dogru, n, tekrar=999))


def cpti_prova(yol):
    """CPTI MwDef ve DepDef (eksikse DepIns); yalnız 2011–2015."""
    yol = Path(yol).resolve()
    if yol != (KESIK / 'CPTI15_v4.0_le2015.csv').resolve():
        raise PuanHatasi('Prova yalnız kesik-2015 CPTI15 kaynağını açar')
    raw = pd.read_csv(yol)
    if raw.Year.isna().any() or (raw.Year >= 2016).any():
        raise PuanHatasi('Kesik CPTI15 dosyası zaman kapısını geçmedi')
    raw = raw[(raw.Year >= 2011) & (raw.MwDef >= 4.95)].copy()
    z = pd.to_datetime(dict(year=raw.Year, month=raw.Mo, day=raw.Da,
                            hour=raw.Ho, minute=raw.Mi, second=raw.Se), utc=True)
    k = pd.DataFrame(dict(zaman=z, enlem=raw.LatDef, boylam=raw.LonDef,
                          derinlik=raw.DepDef.fillna(raw.DepIns), mw=raw.MwDef))
    return katalog_kontrol(k)


def prova(dizin, *, tekrar=999, gear1_modul=None):
    katalog = cpti_prova(KESIK / 'CPTI15_v4.0_le2015.csv')
    tabanlar = {ad: csep_xml(Path(dizin) / f, sure_yil=10) for ad, f in CSEP_DOSYALAR.items()}
    referans = tabanlar['HAZFX-BPT']
    modeller = [Model(ad, model.beklenen) for ad, model in tabanlar.items()]
    gear_durum = ('GEAR1 bölgesel M>=4.95 provasından çıkarıldı; yayımlanan sürüm '
                  'yalnız M>=5.95 ve 1977–2013 kalibrasyonlu. Ayrı ikincil satır gerekir.')
    if gear1_modul:
        gear_durum += ' --gear1-modul bu düşük eşikli provada yüklenmez.'
    kosular = kos(modeller, '2011-01-01T00:00:00Z', '2016-01-01T00:00:00Z',
                  katalog, referans.izgara, referans.m_kenarlar)
    rows = {}
    for ad, k in kosular.items():
        rows[ad] = dict(logL_gunluk=k.logL, N=int(k.gozlem.sum()), beklenen=float(k.beklenen.sum()),
                        tutarlilik=k.tutarlilik(tekrar=tekrar),
                        hazfx_karsisi=karsilastir(k, kosular['HAZFX-BPT']))
    return dict(kip='İtalya 2011–2015 iç doğrulama; hüküm değil', baslangic='2011-01-01', bitis='2016-01-01 (hariç)',
                izgara_hucre=len(referans.izgara), m_kutu=len(referans.m_kenarlar) - 1,
                derinlik='[0,30) km', katalog='CPTI15_v4.0_le2015 MwDef; DepDef, eksikse DepIns',
                katalog_hedef_adayi=len(katalog), gear1=gear_durum, modeller=rows,
                kaynak_metadata={ad: m.metadata for ad, m in tabanlar.items()})


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('kip', choices=['sentetik', 'prova'])
    ap.add_argument('--taban-dizin', default=str(VERI / 'tabanlar'))
    ap.add_argument('--tekrar', type=int, default=999)
    ap.add_argument('--gear1-modul', help='Eski seçenek; M>=4.95 provasında yüklenmez')
    ap.add_argument('--cikti', required=True)
    args = ap.parse_args()
    s = sentetik() if args.kip == 'sentetik' else prova(args.taban_dizin, tekrar=args.tekrar, gear1_modul=args.gear1_modul)
    p = Path(args.cikti)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(json_temiz(s), ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    print(p)


if __name__ == '__main__':
    main()
