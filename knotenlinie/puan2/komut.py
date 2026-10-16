"""MC2 yeniden okuma: ``python -m knotenlinie.puan2.komut`` (çıktı ``$KNOTENLINIE_RUNS/MC2/OLCUM.json``).

Ortam: OPENBLAS_NUM_THREADS=1 (dışarıdan). Yeni model koşmaz; defterleri ve AH kodunu okur.
"""
from __future__ import annotations

import os
for _k in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ.setdefault(_k, '1')

import argparse
import hashlib
import resource
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import scipy

from knotenlinie.ortak_zemin.veri import json_yaz

from . import KANIT_DUZEYI, italya, kaliforniya, uzun

KURAL_SHA_ILK = '769540e59c7f78940bba7be47f3fcf32411feff7a4f6e5a4ca86e1ab9c6eef7c'  # Ek 1 öncesi, ölçümün yapıldığı sürüm
from knotenlinie.yollar import KAYIT, KOSU  # noqa: E402

MC2 = KAYIT / 'MC2'        # frozen MC2 rule (provenance hash)
MC2_CIKTI = KOSU / 'MC2'   # new MC2 outputs


def _d(x, k, default=None):
    return default if not isinstance(x, dict) else x.get(k, default)


def duz_satir(s):
    """Rapor tablosu sütunları (MC2 kuralı)."""
    ta = s.get('tutarlilik_aday') or {}
    npo, nnb = ta.get('N_Poisson') or {}, ta.get('N_NBD') or {}
    return dict(
        satir=s['satir'], bolge=s['bolge'], donem=s['donem'], hedef=s.get('hedef'), esik=s['esik'], N=s['N'],
        IG=s['IG'], SE_blok=s['SE_blok'], SE_HAC=s.get('SE_HAC'), SE_HAC7=s.get('SE_HAC7'),
        z_blok=s['z_blok'], z_HAC=s.get('z_HAC'), p_T_iki_yanli=s.get('p_T'), p_W=s.get('p_W'),
        p_W_tam=s.get('p_W_tam'), p_W_perm=s.get('p_W_perm'), W_bag_var=s.get('bag_var'),
        N_Poisson_d1=npo.get('d1'), N_Poisson_d2=npo.get('d2'),
        N_NBD_d1=nnb.get('d1'), N_NBD_d2=nnb.get('d2'),
        S_Poisson=_d(ta.get('S_Poisson'), 'p'), S_ikili=_d(ta.get('S_ikili'), 'p'),
        M_Poisson=_d(ta.get('M_Poisson'), 'p'), IG_ikili=s.get('IG_ikili'),
        eski_hukum=s['eski_hukum'], yeni_hukum=s['yeni_hukum'], kanit_duzeyi=s.get('kanit_duzeyi', KANIT_DUZEYI))


def tablo_md(olcum, cikti):
    """OLCUM.json['tablo'] → okunur Markdown (TABLO.md)."""
    f = lambda x: '–' if x is None else (('%.3g' % x) if isinstance(x, float) else str(x))
    bas = ['satır', 'bölge/hedef', 'eşik', 'N', 'IG', 'SE_blok', 'SE_HAC', 'z_blok', 'z_HAC', 'T p(2y)', 'W p(2y)',
           'N-Poisson (δ1, δ2)', 'N-NBD (δ1, δ2)', 'S-Poisson', 'S-ikili', 'M', 'IG_ikili', 'eski hüküm', 'yeni hüküm',
           'kanıt']
    out = ['# MC2 ölçüm tablosu (OLCUM.json\'dan üretildi)', '', '| ' + ' | '.join(bas) + ' |',
           '|' + '---|' * len(bas)]
    for t in olcum['tablo']:
        sat = [t['satir'], f"{t['bolge']}{'/' + t['hedef'] if t.get('hedef') else ''}", f(t['esik']), f(t['N']),
               f(t['IG']), f(t['SE_blok']), f(t['SE_HAC']), f(t['z_blok']), f(t['z_HAC']), f(t['p_T_iki_yanli']),
               f(t['p_W']), f"{f(t['N_Poisson_d1'])}, {f(t['N_Poisson_d2'])}",
               f"{f(t['N_NBD_d1'])}, {f(t['N_NBD_d2'])}" if t['N_NBD_d1'] is not None else '–',
               f(t['S_Poisson']), f(t['S_ikili']), f(t['M_Poisson']), f(t['IG_ikili']), t['eski_hukum'],
               t['yeni_hukum'], t['kanit_duzeyi']]
        out.append('| ' + ' | '.join(sat) + ' |')
    out += ['', 'Tek yönlü z > 1,645 ⇔ iki yanlı %90 (iki yanlı p < 0,10). IG nat/olay. p_T/p_W: olay-bağımsız iki yanlı',
            'CSEP T/W (kümelenmede iyimser). Uzun vade: SE_blok = olay bootstrap (uzun_z.olay_ig), HAC tanımsız.']
    Path(cikti).write_text('\n'.join(out) + '\n', encoding='utf-8')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--cikti', default=str(MC2_CIKTI / 'OLCUM.json'))
    ap.add_argument('--tekrar', type=int, default=italya.TEKRAR)
    ap.add_argument('--parca', choices=['hepsi', 'italya', 'kaliforniya', 'uzun'], default='hepsi')
    a = ap.parse_args(argv)
    kural = MC2 / 'KURAL.md'
    sonuc = dict(surum=2, kural_SHA256=hashlib.sha256(kural.read_bytes()).hexdigest(),
                 kural_SHA256_ilk=KURAL_SHA_ILK,
                 python=sys.version, numpy=np.__version__, scipy=scipy.__version__, pandas=pd.__version__,
                 tekrar=a.tekrar, tohumlar=dict(S_Poisson=italya.TOHUM_S, M_Poisson=italya.TOHUM_M,
                                                 S_ikili=italya.TOHUM_SI, L_ikili=italya.TOHUM_LI),
                 kanit_duzeyi=KANIT_DUZEYI,
                 durum='bağımsız skor-kodu incelemesi KABUL (ikinci bakış); SP-ic (iç doğrulama), kör hüküm değil')
    satir = []
    if a.parca in ('hepsi', 'italya'):
        r = italya.olc(tekrar=a.tekrar)
        sonuc['italya'] = r
        satir += r['satirlar']
    if a.parca in ('hepsi', 'kaliforniya'):
        r = kaliforniya.olc()
        sonuc['kaliforniya'] = r
        satir += r['satirlar']
    if a.parca in ('hepsi', 'uzun'):
        r = uzun.olc()
        sonuc['uzun_vade'] = r
        satir += r['satirlar']
    sonuc['tablo'] = [duz_satir(s) for s in satir]
    sonuc['rss_byte'] = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    Path(a.cikti).parent.mkdir(parents=True, exist_ok=True)
    json_yaz(a.cikti, sonuc)
    tablo_md(sonuc, Path(a.cikti).with_name('TABLO.md'))
    print(a.cikti)


if __name__ == '__main__':
    main()
