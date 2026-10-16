"""S günlük ölçeğinin tam Poisson skoru, IG ve sabit Holm4 ailesi."""
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
from knotenlinie.karsilastir.kosucu import Model, kos, karsilastir
from knotenlinie.karsilastir.gunluk_s import olcekle, ozetle, VARIANTS, REFS
from knotenlinie.karsilastir.puan import holm
from knotenlinie.ortak_zemin.veri import IZGARA


class TestGunlukS(unittest.TestCase):
    def setUp(self):
        self.grid = pd.DataFrame([[12.,12.1,40.,40.1]],columns=IZGARA)
        self.edges = np.array([3.95,4.95,np.inf])
        # İlk gün aynı hücre/M kutusunda n=2: n! ölçekten etkilenmemeli.
        self.cat = pd.DataFrame(dict(zaman=pd.to_datetime(['2011-01-01T01:00:00Z','2011-01-01T02:00:00Z','2011-01-02T01:00:00Z','2011-01-02T02:00:00Z'],utc=True),
                                    boylam=[12.05]*4,enlem=[40.05]*4,derinlik=[10.]*4,mw=[4.,4.,5.,5.]))
        settings = dict(sinir=(12.,12.1,40.,40.1),baslangic_yil=1985,derinlik_max=30)
        def base(a,z,h,g,e):
            self.assertTrue((h.zaman < a).all())
            return np.array([[1.,2.]]) if a.day == 1 else np.array([[2.,1.]])
        def scaled(a,z,h,g,e): return .5*base(a,z,h,g,e)
        self.runs = kos([Model('raw',base,True,settings),Model('scaled',scaled,True,settings)],
                        '2011-01-01T00:00:00Z','2011-01-03T00:00:00Z',self.cat,self.grid,self.edges,bolge='italya',derinlik=(0,30))

    def test_poisson_olcek_ve_integral_bilinen(self):
        raw, direct = self.runs['raw'], self.runs['scaled']
        analytical = olcekle(raw,.5,'scaled')
        np.testing.assert_allclose(analytical.beklenen,direct.beklenen)
        np.testing.assert_allclose(analytical.olay_oranlari,direct.olay_oranlari)
        self.assertAlmostEqual(analytical.logL,direct.logL,places=12)
        self.assertAlmostEqual(raw.logL,-6.-2*np.log(2),places=12)
        pair = karsilastir(analytical,raw)
        self.assertAlmostEqual(pair['IG'],np.log(.5)+3/4,places=12)
        self.assertAlmostEqual(pair['IG'],(direct.logL-raw.logL)/4,places=12)
        self.assertEqual(raw.beklenen.sum(),6.)  # özgün yüzey değiştirilmedi
        for c in (0,-1,np.inf,np.nan):
            with self.assertRaises(ValueError): olcekle(raw,c,'bad')

    def test_sabit_n_sekli_ayni(self):
        a = self.runs['raw'].tutarlilik(tekrar=100,tohum=20261005)
        b = olcekle(self.runs['raw'],.5,'s').tutarlilik(tekrar=100,tohum=20261005)
        for field in ('S','M'):
            self.assertEqual(a[field]['p'],b[field]['p'])
        self.assertNotEqual(a['N']['alt_kuyruk'],b['N']['alt_kuyruk'])
        self.assertEqual(b['S']['tohum'],20261005)
        self.assertEqual(b['M']['tohum'],20261006)

    def test_dort_varyant_iki_esik_holm(self):
        raw = self.runs['raw']
        runs = {name:olcekle(raw,c,name) for name,c in zip(VARIANTS,(1.,.5,.8,.6))}
        runs.update({name:olcekle(raw,c,name) for name,c in zip(REFS,(.7,1.1))})
        with patch('knotenlinie.karsilastir.gunluk_s.tek_model_ozeti',side_effect=lambda r,n:dict(N=len(r.olaylar),Lambda=float(r.beklenen.sum()))):
            rows = ozetle(runs,self.grid,self.edges,self.cat,10)
        self.assertEqual([r['M_alt'] for r in rows],[3.95,4.95])
        self.assertEqual([rows[i]['modeller'][VARIANTS[0]]['N'] for i in range(2)],[4,2])
        for row in rows:
            self.assertEqual(set(row['ciftler']),set(VARIANTS))
            for ref in REFS:
                for field in ('p_T','p_W'):
                    pairs = [row['ciftler'][name][ref] for name in VARIANTS]
                    np.testing.assert_allclose([p[field+'_Holm4'] for p in pairs],holm([p[field] for p in pairs]))
                groups = row['ciftler'][VARIANTS[0]][ref]['ayristirma']['gruplar']
                self.assertEqual(groups['kumelenme']['N'],1)
                self.assertEqual(groups['geri_kalan']['N'],row['modeller'][VARIANTS[0]]['N']-1)


if __name__ == '__main__': unittest.main()
