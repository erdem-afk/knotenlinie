"""Yıllık MAXC + sabit Mc'de kümülatif GR uyumu; yalnız ≤2010."""
import numpy as np
import pandas as pd
from knotenlinie.ortak_zemin.ayar import b_ayarla


def tani(katalog):
    if katalog.empty or (katalog.zaman >= pd.Timestamp('2011-01-01', tz='UTC')).any():
        raise ValueError('Tamlık yalnız ≤2010')
    rows = []
    for year in range(1985, 2011):
        d = katalog[katalog.zaman.dt.year == year]
        m = d.mw.to_numpy(float)
        positive = m[m > 0]
        h, e = np.histogram(positive, np.arange(.05, 9.06, .1))
        maxc = float(e[h.argmax()]+.05) if len(positive) else None
        s = m[m >= 2.5]
        b = b_ayarla(s, 2.5) if len(s) >= 100 else None
        if b:
            thresholds = np.round(np.arange(2.5, 9.01, .1), 2)
            obs = np.array([(s >= z-1e-10).sum() for z in thresholds])
            pred = len(s)*10**(-b['deger']*(thresholds-2.5))
            R = float(100*(1-np.abs(obs-pred).sum()/obs.sum()))
        else:
            R = None
        rows.append(dict(yil=year, N=len(s), sifir_buyukluk=int((m == 0).sum()),
                         MAXC=maxc, Mc_MAXC_artı_02=maxc+.2 if maxc is not None else None,
                         b=b, GR_uyum_yuzde=R,
                         oran_25_31=float(len(s)/max(1,(m >= 3.1).sum())),
                         kabul=bool(b and maxc+.2 <= 2.5+1e-10 and R >= 90)))
    bad = [r['yil'] for r in rows if not r['kabul']]
    start = max(bad)+1 if bad else 1985
    if start > 2005:
        raise ValueError('Mc2.5 kabul edilen eğitim ≤2005 KDE bölmesine erişmiyor')
    return dict(yillik=rows, baslangic_yili=start, mc=2.5,
                kural='N≥100; MAXC+0.2≤2.5; kümülatif GR R≥90%; 2010’a kadar kabul edilen en uzun ardışık son blok',
                notu='Mw>0 MAXC; sıfır/missing büyüklükler frekans tepesine konmaz. GR uyumu tamlık kanıtı değildir; büyük diziler/ağ ve Mw ölçeği değişimleri etkileyebilir.')
