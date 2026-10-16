"""İnceleme H düzeltmeleri: bağımsız sentetik kaynak/günlük hedef cevapları (İtalya)."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from knotenlinie.karsilastir import Model, kos, karsilastir, PuanHatasi, csep_xml, gectik, IzgaraTabani
from knotenlinie.karsilastir.komut import json_temiz, prova
from tests.karsilastir.test_karsilastir import izgara, katalog, statik, XML


class KosucuDuzeltTest(unittest.TestCase):
    def setUp(self):
        self.g = izgara()
        self.m = [4.95,5.05,np.inf]
        self.k = katalog([
            ['2010-12-31T23:59:59Z',40.5,10.5,70,4.],
            ['2011-01-01T12:00:00Z',40.5,10.5,10,5.],
            ['2011-01-02T12:00:00Z',40.5,11.5,10,6.],
        ])

    def run_models(self, models, k=None, **kwargs):
        return kos(models, '2011-01-01T00:00:00Z', '2011-01-03T00:00:00Z',
                   self.k if k is None else k, self.g, self.m, **kwargs)

    def test_zero_rate_on_either_or_both_sides_continues_and_serializes(self):
        s = self.run_models([statik('ok', np.ones((2,2))),
                             statik('TripleS', [[0,1],[1,1]]),
                             statik('HAZFX', [[1,1],[1,0]])])
        pairs = [('ok','TripleS'), ('TripleS','ok'), ('TripleS','HAZFX'), ('ok','ok')]
        r = [karsilastir(s[a], s[b]) for a,b in pairs]
        for row in r[:3]:
            self.assertEqual(row['durum'], 'tanımsız')
            self.assertIsNone(row['IG'])
            self.assertIsNone(row['p_T'])
            self.assertIsNone(row['p_W'])
            self.assertEqual(row['N'], 2)
            self.assertIn('sıfır oran', row['sebep'])
        self.assertEqual(r[-1]['IG'], 0)
        json.dumps(json_temiz(r), allow_nan=False)
        self.assertEqual(s['TripleS'].logL, -np.inf)
        self.assertEqual(s['HAZFX'].logL, -np.inf)

    def test_depth_identity_and_mismatched_integral(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'forecast.xml'
            p.write_text(XML)
            taban = csep_xml(p, sure_yil=10)
        s = self.run_models([statik('aday',np.ones((2,2))), Model('csep',taban.beklenen)])
        kimlik = karsilastir(s['aday'],s['csep'])['karsilastirma_kimligi']
        self.assertEqual(kimlik['taban_derinlik']['derinlik_min'],0)
        self.assertEqual(kimlik['taban_derinlik']['derinlik_max'],30)
        self.assertIn('CSEP',kimlik['taban_derinlik']['derinlik_tanimi'])
        with self.assertRaisesRegex(PuanHatasi,'integral'):
            self.run_models([Model('csep',taban.beklenen)],derinlik=(0,40))

    def test_explicit_depth_required_by_baseline_metadata(self):
        meta = dict(derinlik_min=0,derinlik_max=40,derinlik_acik_gerekli=True,
                    derinlik_tanimi='taban D<=40; hedef [0,40)')
        model = Model('derin',statik('x',np.ones((2,2))).beklenen,taban_metadata=meta)
        with self.assertRaisesRegex(PuanHatasi,'açıkça'):
            self.run_models([model])
        with self.assertRaisesRegex(PuanHatasi,'italya'):
            self.run_models([statik('aday',np.ones((2,2)))],bolge='baska')
        k = self.k.copy()
        k.loc[1,'derinlik'], k.loc[2,'derinlik'] = 30, 40
        s = self.run_models([model, statik('aday',np.ones((2,2)))], k,derinlik=(0,40))
        self.assertEqual(s['derin'].gozlem.sum(),1)
        self.assertIn('<=40',karsilastir(s['aday'],s['derin'])['karsilastirma_kimligi']['taban_derinlik']['derinlik_tanimi'])

    def test_history_filters_are_per_candidate_not_target_filters(self):
        extra = katalog([
            ['1984-12-31T23:59:59Z',40.5,10.5,10,4],
            ['1985-01-01T00:00:00Z',40.5,10.5,10,4],
            ['2010-12-31T22:00:00Z',40.5,10.5,70.01,4],
            ['2010-12-31T22:00:00Z',40.5,12,10,4],
            ['2010-12-31T22:00:00Z',41,10.5,10,4],
        ])
        k = pd.concat([extra,self.k],ignore_index=True)
        seen = {'c':[], 'f':[]}
        def expected(name):
            def call(a,b,past,g,m):
                seen[name].append(past.copy())
                return np.ones((2,2))
            return call
        def settings(year):
            return dict(sinir=(10,12,40,41),baslangic_yil=year,derinlik_max=70)
        self.run_models([Model('c',expected('c'),True,settings(2010)),
                         Model('f',expected('f'),True,settings(1985))],k)
        self.assertEqual([len(x) for x in seen['c']],[1,2])
        self.assertEqual([len(x) for x in seen['f']],[2,3])
        self.assertEqual(seen['c'][0].mw.tolist(),[4.])
        self.assertEqual(seen['c'][0].derinlik.tolist(),[70.])
        for samples in seen.values():
            self.assertTrue((samples[0].zaman < pd.Timestamp('2011-01-01',tz='UTC')).all())

    def test_dynamic_missing_and_invalid_history_settings_fail_closed(self):
        for ayar in (None, {}, dict(sinir=(10,12,40,41),baslangic_yil=1985,derinlik_max=71)):
            with self.assertRaises(PuanHatasi):
                self.run_models([Model('x',lambda *args: np.ones((2,2)),True,ayar)])

    def test_prova_excludes_gear1_without_loading_module_and_keeps_zero_rows(self):
        baseline = IzgaraTabani('test',self.g,np.array(self.m),np.array([[0.,1.],[1.,1.]]),
                                dict(derinlik_min=0,derinlik_max=30))
        with patch('knotenlinie.karsilastir.komut.cpti_prova',return_value=self.k), \
                patch('knotenlinie.karsilastir.komut.csep_xml',return_value=baseline):
            r = prova('unused',tekrar=1,gear1_modul='does.not.exist')
        self.assertEqual(set(r['modeller']),{'HAZFX-BPT','TripleS-CPTI','MPS04'})
        self.assertIn('1977–2013',r['gear1'])
        self.assertIn('yüklenmez',r['gear1'])
        for row in r['modeller'].values():
            self.assertEqual(row['hazfx_karsisi']['durum'],'tanımsız')
        json.dumps(json_temiz(r),allow_nan=False)

    def test_full_verdict_needs_plain_etas_in_same_holm_family(self):
        names = ['italya_hazfx','italya_triples','italya_etas']
        c = {k:dict(IG=.1,p_T=.001) for k in names}
        t = {k:dict(gecti=True) for k in ['italya']}
        s = gectik(c,t)
        self.assertTrue(s['gectik'])
        np.testing.assert_allclose(list(s['p_T_holm'].values()),[.003]*3)
        c['italya_etas'] = dict(IG=0,p_T=1)
        self.assertFalse(gectik(c,t)['gectik'])
        c['italya_etas'] = dict(IG=None,p_T=None)
        self.assertFalse(gectik(c,t)['gectik'])
        del c['italya_etas']
        with self.assertRaises(PuanHatasi):
            gectik(c,t)


if __name__ == '__main__':
    unittest.main()
