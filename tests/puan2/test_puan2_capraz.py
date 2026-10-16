"""pyCSEP kuruluysa (ör. pyCSEP kurulu ayrı bir ortamda) çapraz kontrol; yoksa bilinen cevaplı testler yeter (atlanır)."""
import unittest

try:
    import csep  # noqa: F401
    VAR = True
except Exception:  # pragma: no cover
    VAR = False


@unittest.skipUnless(VAR, 'pyCSEP kurulu değil: formül testleri test_puan2_nbd/ikili/hac içinde')
class CaprazTest(unittest.TestCase):
    def test_capraz(self):
        from knotenlinie.puan2 import capraz_pycsep
        o = capraz_pycsep.kos()
        self.assertLessEqual(o['nbd_N_max_rel'], 1e-6)
        self.assertEqual(o['ikili_L']['p_pycsep'], o['ikili_L']['p_biz'])


if __name__ == '__main__':
    unittest.main()
