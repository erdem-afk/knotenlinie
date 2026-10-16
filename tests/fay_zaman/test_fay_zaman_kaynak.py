"""Kaynak tablosu: son olay ayrıştırma ve moment bölüşümü."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from shapely.geometry import box

from knotenlinie.fay_zaman import kaynak as k
from tests._veri import veri_gerek


@pytest.mark.parametrize('metin,yil', [('21 May 2003', 2003.388), ('26 Sep 1997 (2/2)', 1997.735),
                                       ('21 Jul 365', 365.555), ('16 Dec 1857 (1/2)', 1857.958)])
def test_son_olay_ayristirma(metin, yil):
    assert k.son_olay_yili(metin) == pytest.approx(yil, abs=1e-3)


@pytest.mark.parametrize('metin', ['Unknown', 'unknown', '800 B.C-1030 A.D.', '530-900 A.D.',
                                   'Before 1273 A.D.', None, ''])
def test_son_olay_belirsiz_none(metin):
    assert k.son_olay_yili(metin) is None


def test_moment_dagit_iss_ebeveyni_dusurur_ve_sifira_kirpar():
    def satir(i, kat, a, s, e=None):
        return dict(id=i, ad=i, katman=kat, poligon=box(0, 0, 1, 1), alan_km2=a, kayma_mm_yil=s,
                    mmax=6.5, son_yil=np.nan, ebeveyn=e, kaynak_son=None)
    t = pd.DataFrame([satir('C1', 'CSS', 1000.0, 1.0), satir('I1', 'ISS', 100.0, 1.0, 'C1'),
                      satir('C2', 'CSS', 100.0, 1.0), satir('I2', 'ISS', 400.0, 1.0, 'C2')])
    r = k.moment_dagit(t).set_index('id')
    assert r.loc['C1', 'mdot'] == pytest.approx(3e10 * 900e6 * 1e-3, rel=1e-12)   # 1000−100 km²
    assert r.loc['I1', 'mdot'] == pytest.approx(3e10 * 100e6 * 1e-3, rel=1e-12)
    assert r.loc['C2', 'mdot'] == 0.0                                           # ISS > CSS → 0
    # toplam, ISS ≤ CSS iken korunur
    assert r.loc[['C1', 'I1'], 'mdot'].sum() == pytest.approx(r.loc['C1', 'mdot_ham'], rel=1e-12)


@veri_gerek('diss320/csstop320.geojson', 'diss320/csspln320.geojson', 'diss320/iss320.geojson',
            'kesik-2015/CPTI15_v4.0_le2015.csv')
def test_zaman_kesimi_gercek_veride():
    t06, g06 = k.italya(2006.0)
    t11, g11 = k.italya(2011.0)
    # sonraki depremle tanımlanmış kaynaklar kesimde düşer (Paganica, Emilia)
    assert 'ITIS131' in g06['iss_dusen_sonraki_olay'] and 'ITIS131' not in g11['iss_dusen_sonraki_olay']
    assert 'ITIS134' in g11['iss_dusen_sonraki_olay']
    iss = t11[t11.katman == 'ISS']
    assert (iss.son_yil.dropna() < 2011.0).all()
    iss06 = t06[t06.katman == 'ISS']
    assert (iss06.son_yil.dropna() < 2006.0).all()
