"""Okuyucu, mühür kapıları, ızgara ve tamlık testleri (sentetik, bilinen cevaplı)."""
from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from knotenlinie.yan_tezgah import okuyucu as O
from knotenlinie.yan_tezgah.indir import BASLIK, MuhurIhlali


def _yaz(kok: Path, ad: str, satirlar) -> Path:
    yol = Path(kok) / 'deprem' / 'yan-bolge' / 'scsn'
    yol.mkdir(parents=True, exist_ok=True)
    p = yol / ad
    with open(p, 'w', encoding='utf-8') as f:
        f.write(BASLIK + '\n')
        for s in satirlar:
            f.write('|'.join(s) + '\n')
    return p


def _satir(eid, zaman, la, lo, der, mag='l', mw='2.5'):
    return [str(eid), zaman, str(la), str(lo), str(der), 'CI', 'SCEDC', '', '', mag,
            str(mw), 'CI', 'yer', '']


def test_temiz_dosya_okunur():
    with tempfile.TemporaryDirectory() as d:
        _yaz(d, 'ca-scsn_2005.txt', [_satir(1, '2005/01/01 00:00:00.0000', 34.0, -118.0, 10.0),
                                     _satir(2, '2005/06/01 12:00:00.0000', 35.0, -117.0, 5.0)])
        df = O.oku(d, 'scsn')
        assert len(df) == 2
        assert df.zaman.dt.year.unique().tolist() == [2005]
        assert list(df.columns) == ['event_id', 'zaman', 'enlem', 'boylam', 'derinlik',
                                    'mag_type', 'mw', 'source', 'catalog_file']


def test_2021_satiri_muhur_ihlali():
    with tempfile.TemporaryDirectory() as d:
        _yaz(d, 'ca-scsn_2020.txt', [_satir(1, '2020/12/31 23:59:59.0000', 34.0, -118.0, 10.0),
                                     _satir(2, '2021/01/01 00:00:00.0000', 34.0, -118.0, 10.0)])
        with pytest.raises(MuhurIhlali):
            O.oku(d, 'scsn')


def test_dosya_adi_2021_reddedilir():
    with tempfile.TemporaryDirectory() as d:
        _yaz(d, 'ca-scsn_2021.txt', [_satir(1, '2021/02/01 00:00:00.0000', 34.0, -118.0, 10.0)])
        # 2021 adlı dosya hiç listelenmez/açılmaz; okuyucu 'dosya yok' der.
        assert O.dosyalar(Path(d), 'scsn') == []
        with pytest.raises(MuhurIhlali):
            O.oku(d, 'scsn')
        with pytest.raises(MuhurIhlali):
            O.dosyalar(Path(d), 'scsn', son_yil=2021)


def test_bozuk_baslik_reddedilir():
    with tempfile.TemporaryDirectory() as d:
        yol = Path(d) / 'deprem' / 'yan-bolge' / 'scsn'
        yol.mkdir(parents=True)
        (yol / 'ca-scsn_2005.txt').write_text('#EventID | Time | Latitude\n1|2005/01/01|x\n')
        with pytest.raises(MuhurIhlali):
            O.oku(d, 'scsn')


def test_kutu_ve_derinlik_suzgeci():
    with tempfile.TemporaryDirectory() as d:
        _yaz(d, 'ca-scsn_2005.txt', [
            _satir(1, '2005/01/01 00:00:00.0000', 34.0, -118.0, 10.0),   # içeride
            _satir(2, '2005/02/01 00:00:00.0000', 20.0, -118.0, 10.0),   # kutu dışı
            _satir(3, '2005/03/01 00:00:00.0000', 34.0, -118.0, 80.0)])  # derinlik dışı
        df = O.oku(d, 'scsn')
        assert df.event_id.tolist() == ['1']


def test_izgara_kutuyu_dosser():
    for b in ('scsn', 'geonet'):
        g = O.izgara(b)
        la0, la1, lo0, lo1 = O.BOLGELER[b]['kutu']
        assert np.isclose(g.boylam_min.min(), lo0) and np.isclose(g.boylam_max.max(), lo1)
        assert np.isclose(g.enlem_min.min(), la0) and np.isclose(g.enlem_max.max(), la1)
        assert len(g) == round((la1 - la0) / 0.1) * round((lo1 - lo0) / 0.1)


def test_hkj_bilinen_deger():
    # t=0'da M7.1; +1 gün: 7.1-4.5-0.75*log10(1)=2.6; +10 gün: 7.1-4.5-0.75=1.85.
    z = pd.to_datetime(['2005-01-01 00:00:00', '2005-01-02 00:00:00', '2005-01-11 00:00:00'], utc=True)
    df = pd.DataFrame(dict(zaman=z, mw=[7.1, 2.5, 2.5]))
    mc = O.hkj_mc(df)
    assert np.isclose(mc[1], 2.6, atol=1e-9)
    assert np.isclose(mc[2], 1.85, atol=1e-9)
    assert np.isneginf(mc[0])


def test_donem_mc_tek_ve_hedef_kurali():
    z = pd.to_datetime(['2005-01-01', '2007-01-01', '2012-01-01'], utc=True)
    df = pd.DataFrame(dict(zaman=z, mw=[3.0, 3.0, 3.0]))
    t = O.tamlik(df, 2005, 2012, hkj=False)
    # 2005-2009 tek pencere (3 olay < 200) -> MAXC+0.2 = 3.2; hedef = 3.4.
    assert t['hedef'] == 3.4
    assert all(p['mc'] >= 3.2 for p in t['pencereler'])
