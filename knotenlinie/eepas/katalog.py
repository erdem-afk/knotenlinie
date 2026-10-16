"""Kesik CPTI15+ISIDe birleştirme; Mw dönüşümü yalnız <=2010 eşleşmelerinden."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from knotenlinie.etas import katalog as K
from knotenlinie.etas.tamlik import mc_wiemer_wyss
from .model import zaman_gun

from knotenlinie.yollar import VERI as _KOK  # noqa: E402

VERI = _KOK / 'kesik-2015'
AYAR_SONU = pd.Timestamp('2011-01-01',tz='UTC')
KESIM = pd.Timestamp('2016-01-01',tz='UTC')


def eslestir(cpti, iside):
    """CPTI başına tek ISIDe: <=90 saniye, <=30 km; zaman farkı sonra uzaklık."""
    ct,it = zaman_gun(cpti.time_utc),zaman_gun(iside.time_utc)
    order = np.argsort(it)
    used = set()
    pairs = []
    for ci in np.argsort(ct):
        left,right = np.searchsorted(it[order],[ct[ci]-90/86400,ct[ci]+90/86400])
        cand = order[left:right]
        cand = np.array([v for v in cand if v not in used],int)
        if len(cand)==0:
            continue
        dlat = iside.lat.to_numpy()[cand]-cpti.lat.iloc[ci]
        dlon = (iside.lon.to_numpy()[cand]-cpti.lon.iloc[ci])*np.cos(np.deg2rad(cpti.lat.iloc[ci]))
        dist = 111.195*np.hypot(dlat,dlon)
        ok = cand[dist<=30]
        if len(ok):
            j = min(ok,key=lambda z:abs(it[z]-ct[ci]))
            used.add(int(j))
            pairs.append((int(ci),int(j)))
    return pairs


def donusum_ayarla(cpti, iside, pairs, n_min=30):
    """Robust Theil–Sen; küçük eşleşme örneklemi/uzak ekstrapolasyon raporda görünür."""
    out = {}
    for tur in ('ML','Md'):
        pts = [(iside.mag.iloc[i],cpti.mag.iloc[c]) for c,i in pairs
               if iside.mag_type.iloc[i]==tur and cpti.time_utc.iloc[c]<AYAR_SONU
               and iside.time_utc.iloc[i]<AYAR_SONU]
        if len(pts)<n_min:
            raise ValueError('%s Mw dönüşümü için yalnız %d ayar eşleşmesi; >=%d gerekli'%(tur,len(pts),n_min))
        x,y = np.asarray(pts).T
        slope,intercept,lo,hi = stats.theilslopes(y,x,alpha=.95)
        if not .3<slope<2:
            raise ValueError('%s Mw dönüşümü eğimi kullanılamıyor'%tur)
        resid = y-(intercept+slope*x)
        out[tur] = {'egim':float(slope),'sabit':float(intercept),'n':len(x),
                    'egim95':[float(lo),float(hi)],'rms':float(np.sqrt(np.mean(resid**2))),
                    'girdi_aralik':[float(x.min()),float(x.max())]}
    return out


def italya_oku(veri=VERI):
    """Sadece adı/sözleşmesi <=2015 olan hazır dosyalar; 2016+ keşfi yok."""
    veri = Path(veri)
    c,cr = K.cpti15_oku(str(veri/'CPTI15_v4.0_le2015.csv'))
    if cr['atilan_kesim']:
        raise ValueError('Kesik CPTI dosyasında yasak dönem sızıntısı; dur')
    # CPTI'nin düşük büyüklük tarihsel tamlığı yok: 1985 öncesi bu uygulamada kullanılmaz.
    c = c.loc[c.time_utc>=pd.Timestamp('1985-01-01',tz='UTC')].reset_index(drop=True)
    paths = [str(veri/'iside'/('iside_%d.txt'%y)) for y in range(1985,2016)]
    i,ir = K.iside_oku(paths)
    if ir['atilan_kesim']:
        raise ValueError('Kesik ISIDe dosyasında yasak dönem sızıntısı; dur')
    c = c.loc[np.isfinite(c.mag)&np.isfinite(c.lon)&np.isfinite(c.lat)].reset_index(drop=True)
    i = i.loc[np.isfinite(i.mag)&np.isfinite(i.lon)&np.isfinite(i.lat)].reset_index(drop=True)
    pairs = eslestir(c,i)
    conv = donusum_ayarla(c,i,pairs)
    # Yüksek büyüklükte CPTI Mw öncelikli; aynı olay iki kez sayılmaz.
    used = {j for _,j in pairs}
    i = i.loc[~i.index.isin(used)].copy()
    accepted = i.mag_type.isin(['Mw','ML','Md'])
    unsupported = int((~accepted).sum())
    i = i.loc[accepted].copy()
    i['mw'] = i.mag.to_numpy(float)
    for tur,q in conv.items():
        mask = i.mag_type==tur
        i.loc[mask,'mw'] = q['sabit']+q['egim']*i.loc[mask,'mag']
    c['mw'] = c.mag.to_numpy(float)
    df = pd.concat([c,i],ignore_index=True)
    df = df.rename(columns={'time_utc':'zaman','lat':'enlem','lon':'boylam','depth_km':'derinlik'})
    df['derinlik'] = df.derinlik.fillna(10.)
    cols = ['zaman','enlem','boylam','derinlik','mw']
    # Yalnız ilan edilen İtalya kaba kutusu.
    la0,la1,lo0,lo1 = K.BOLGELER['italy']
    mask = (df.enlem>=la0)&(df.enlem<la1)&(df.boylam>=lo0)&(df.boylam<lo1)
    return df.loc[mask,cols].sort_values('zaman').reset_index(drop=True), {
        'donusum':conv,'eslesme':len(pairs),'desteksiz_tur_atilan':unsupported,
        'cpti':cr,'iside':ir,'not':'Kalibre ML/Md proxy Mw; küçük olaylara ekstrapolasyon belirsiz.'}


def oncu_esigi(df):
    """Ayar dönemi on yıllık dilimlerinin en yüksek MBS Mc'si +0.2 güven payı."""
    cuts = ((1985,1995),(1995,2005),(2005,2011))
    rows = []
    for start,end in cuts:
        # Doğrulama büyüklük dağılımına bakılmaz.
        d = df.loc[(df.zaman>=pd.Timestamp('%d-01-01'%start,tz='UTC'))&
                   (df.zaman<pd.Timestamp('%d-01-01'%end,tz='UTC'))]
        if len(d)<500:
            raise ValueError('Tamlık diliminde <500 olay')
        r = mc_wiemer_wyss(d.mw.to_numpy(float))
        if r['mc'] is None:
            raise ValueError('Kararlı öncü tamlık eşiği yok: %d–%d'%(start,end-1))
        rows.append({'baslangic':start,'bitis':end-1,'n':len(d),'mc':r['mc']})
    m0 = float(np.ceil((max(r['mc'] for r in rows)+.2)*10-1e-9)/10)
    return m0, {'m0':m0,'dilimler':rows,'kural':'max(ayar dilimleri MBS Mc)+0.2; 0.1 M yukarı yuvarlama',
                 'hedef_oncu_farki':4.95-m0,'iki_birim_oncu_acigi':4.95-m0<1.8}


def kesik_oku(yol):
    """Deney E/H'nin yalnız açık kesik normalize CSV'si; adında le2015 şart."""
    path = Path(yol)
    if 'le2015' not in path.stem:
        raise ValueError('Yalnız açıkça le2015 olarak teslim edilmiş normalize katalog okunur')
    df = pd.read_csv(path,dtype={'zaman':str})
    df['zaman'] = pd.to_datetime(df.zaman,utc=True)
    if df.zaman.isna().any() or (df.zaman>=KESIM).any():
        raise ValueError('Kesik katalog zaman kapısı ihlali; dur')
    return df[['zaman','enlem','boylam','derinlik','mw']]
