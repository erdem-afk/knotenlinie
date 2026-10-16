import json
import unittest

import numpy as np

from knotenlinie.karsilastir import uzun_ah as AHK
from knotenlinie.karsilastir import uzun_z
from knotenlinie.puan2 import uzun
from tests._veri import kosu_gerek, veri_gerek


class UzunTest(unittest.TestCase):
    @kosu_gerek('AH/OLCUM.json')
    @veri_gerek('ortak/italya_katalog_le2015.csv', 'ortak/italya_izgara.csv', 'diss320/csstop320.geojson',
                'kesik-2015/CPTI15_v4.0_le2015.csv', 'tabanlar/akinci.HAZFX_BPT.italy.10yr.2010-01-01.xml')
    def test_gercek_ah_italya_hazfx_ah_olcumu_ile_ayni(self):
        z = json.loads((uzun_z.Z_DIR / 'OLCUM.json').read_text(encoding='utf-8'))
        ah = json.loads((AHK.AH_DIR / 'OLCUM.json').read_text(encoding='utf-8'))
        beklenen = [s for s in ah['bolgeler']['italya']['satirlar']['2011-2015']
                    if s['hedef'] == 'kumesiz' and s['taban'] == 'HAZFX'][0]
        v = {x[0]: x for x in AHK.VARYANTLAR}
        ad = ah['secili']
        h = AHK.hazirla('italya', 'ayar2010', z['bolgeler']['italya']['secim'])
        model = AHK.model_kur(h, v[ad][1], v[ad][2], ad='AH-' + ad)
        a = AHK.AYARLAR['ayar2010']
        t0, t1 = uzun_z.utc(a['t0']), uzun_z.utc(a['t1'])
        k = int(np.searchsorted(h['edges'], 4.95, side='right') - 1)
        lam_a = model.beklenen(t0, t1, None, h['izgara'], h['edges'])[:, k:].sum(axis=1)
        tb = dict(h['cfg']['tabanlar'])['HAZFX']
        t = uzun_z.taban_yukle('HAZFX', tb)
        lam_r = t.beklenen(t0, t1, None, h['izgara'], t.m_kenarlar).sum(axis=1)
        _, ci, mi = AHK.hedef(h, 'kumesiz')
        aa = uzun.a_uzun(h, 'kumesiz', k)
        r = uzun.satir(lam_a, lam_r, ci, mi, k, len(h['izgara']), 'AH', 'HAZFX', 'italya', 'kumesiz', aa, 200)
        self.assertEqual(r['N'], beklenen['N'])
        self.assertAlmostEqual(r['IG'], beklenen['IG'], places=9)
        self.assertAlmostEqual(r['Lambda_aday'], beklenen['Lambda_aday'], places=9)
        self.assertIsNone(r['SE_HAC'])
        self.assertIsNotNone(r['p_W_tam'])
        self.assertEqual(r['yeni_hukum'], 'başarısızlık')   # IG<0
        self.assertEqual(r['kanit_duzeyi'], 'SP-ic')
        self.assertGreaterEqual(aa['a'], 0.0)


if __name__ == '__main__':
    unittest.main()
