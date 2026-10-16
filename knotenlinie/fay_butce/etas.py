"""Ortak ETAS'ın yalnız uzaysal arka planını fay şekliyle değiştir."""
from __future__ import annotations

import importlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar
from scipy.stats import t as student_t

from .butce import yillik, izgara_dogrula, kenarlar_dogrula
from .veri import fay_oku, kaynak_kapisi, DISS_SHA256

AYAR_SON = pd.Timestamp('2011-01-01', tz='UTC')
ACIK_SON = pd.Timestamp('2016-01-01', tz='UTC')


def _aralik(baslangic, bitis):
    bas, son = pd.Timestamp(baslangic), pd.Timestamp(bitis)
    if bas.tzinfo is None or son.tzinfo is None or not bas < son:
        raise ValueError('UTC ve pozitif zaman aralığı gerekli')
    return bas, son


def _dizi(a):
    a = np.asarray(a, float)
    if not np.isfinite(a).all() or np.any(a < 0):
        raise ValueError('beklenen sayılar sonlu ve negatif olmayan olmalı')
    return a


def degistir(taban, arka_plan, sekil, agirlik):
    """Tetikleme korunur; her büyüklük kutusunun arka plan toplamı aynıdır."""
    a, bg, u = _dizi(taban), _dizi(arka_plan), _dizi(sekil)
    if (a.ndim != 2 or a.shape != bg.shape or u.shape != (len(a),)
            or np.any(bg > a + 1e-12) or not np.isfinite(agirlik)
            or not 0 <= agirlik <= 1 or u.sum() <= 0):
        raise ValueError('ETAS arka planı/şekli/ağırlığı geçersiz')
    if agirlik == 0:
        return a.copy()
    fay = (u / u.sum())[:, None] * bg.sum(axis=0)[None, :]
    return np.maximum(a-bg, 0) + (1-agirlik)*bg + agirlik*fay


class OrtakTaban:
    """Saf ETAS'ta boş geçmiş çağrısı tam arka plandır; yeniden ayar yok."""
    def __init__(self, model):
        self.model = model

    def beklenen(self, *args):
        return self.model.beklenen(*args)

    def arka_plan_beklenen(self, bas, son, gecmis, izgara, kenarlar):
        if hasattr(self.model, 'arka_plan_beklenen'):
            return self.model.arka_plan_beklenen(bas, son, gecmis, izgara, kenarlar)
        return self.model.beklenen(bas, son, gecmis.iloc[:0], izgara, kenarlar)


class ETASFay:
    """Taban nesnesi beklenen(...) ve arka_plan_beklenen(...) sunar.

    İki çağrı aynı ETAS ayarını kullanmalıdır. Fay oranı yalnız sabit şekildir;
    mu, GR büyüklük dağılımı, tüm tetikleme ve geçmiş aynen tabanda kalır.
    """
    def __init__(self, taban, faylar, *, agirlik, sigma_km, b=1., sekil_esik=4.95):
        if not np.isfinite(agirlik) or not 0 <= agirlik <= 1:
            raise ValueError('ağırlık [0,1] olmalı')
        if not np.isfinite(sigma_km) or sigma_km <= 0:
            raise ValueError('sigma pozitif olmalı')
        self.taban, self.faylar = taban, faylar.copy(deep=True)
        self.agirlik, self.sigma_km = agirlik, sigma_km
        self.b, self.sekil_esik, self._cache = b, sekil_esik, None

    def sekil(self, izgara):
        key = izgara[['boylam_min','boylam_max','enlem_min','enlem_max']].to_numpy(float).tobytes()
        if self._cache is None or self._cache[0] != key:
            # Mmax ve moment bütçesi ağırlıkları; test büyüklük kutularından bağımsız.
            raw = yillik(self.faylar, izgara, [self.sekil_esik, np.inf],
                         sigma_km=self.sigma_km, b=self.b).ravel()
            if raw.sum() <= 0:
                raise ValueError('bölgede fay bütçesi sıfır')
            self._cache = (key, raw/raw.sum())
        return self._cache[1]

    def beklenen(self, baslangic, bitis, gecmis, izgara, m_kenarlar):
        bas, son = _aralik(baslangic, bitis)
        kaynak_kapisi(self.faylar, son-pd.Timedelta(nanoseconds=1))
        if len(gecmis) and (pd.to_datetime(gecmis.zaman, utc=True) >= bas).any():
            raise ValueError('ETAS geçmişinde tahmin başlangıcı veya sonrası var')
        a = self.taban.beklenen(bas, son, gecmis, izgara, m_kenarlar)
        if self.agirlik == 0:
            return _dizi(a).copy()
        bg = self.taban.arka_plan_beklenen(bas, son, gecmis, izgara, m_kenarlar)
        return degistir(a, bg, self.sekil(izgara), self.agirlik)


def _logL(olay, toplam):
    if np.any(olay <= 0):
        return -np.inf
    return float(np.log(olay).sum()-toplam)


def ayarla(olay_taban, olay_fay, toplam_taban, toplam_fay, *, baslangic, bitis):
    """Sadece ≤2010 günlük tahminleriyle sigma ve konveks w seçimi."""
    _, son = _aralik(baslangic, bitis)
    if son > AYAR_SON:
        raise ValueError('ayar ≤2010 olmalı')
    a = _dizi(olay_taban)
    if a.ndim != 1 or not len(a) or np.any(a <= 0):
        raise ValueError('ayar olayı ve sonlu taban skoru gerekli')
    rows = []
    for sigma, f in olay_fay.items():
        f = _dizi(f)
        if f.shape != a.shape:
            raise ValueError('ayar adayının olay şekli farklı')
        nt, nf = float(_dizi(toplam_taban)), float(_dizi(toplam_fay[sigma]))
        def L(w):
            return _logL((1-w)*a+w*f, (1-w)*nt+w*nf)
        fit = minimize_scalar(lambda w: -L(w), bounds=(0,1), method='bounded',
                              options={'xatol':1e-10})
        w = max((0., 1., float(fit.x)), key=L)
        if L(w)-L(0) <= 1e-10:
            w = 0.
        rows.append(dict(sigma_km=float(sigma), agirlik=w, logL=L(w), delta_logL=L(w)-L(0)))
    if not rows or not any(np.isfinite(r['logL']) for r in rows):
        raise ValueError('sonlu ayar adayı yok')
    return dict(max(rows, key=lambda r:r['logL']), adaylar=rows)


def olcum(olay_model, olay_taban, toplam_model, toplam_taban):
    """Poisson farkı ve eşleştirilmiş iki yönlü T-test; olay bağımsızlığı varsayılır."""
    a, b = _dizi(olay_model), _dizi(olay_taban)
    nm, nt = float(_dizi(toplam_model)), float(_dizi(toplam_taban))
    if a.ndim != 1 or a.shape != b.shape or len(a) == 0 or np.any(b <= 0):
        raise ValueError('ölçüm için eşlenmiş olaylar ve pozitif taban gerekli')
    n = len(a)
    if np.any(a == 0):
        return dict(N=n, IG='-inf', SE=None, p=None, delta_logL='-inf',
                    beklenen_toplam=nm, beklenen_taban=nt, integral_farki=nt-nm)
    log = np.log(a)-np.log(b)
    ig = float((log.sum()+nt-nm)/n)
    se = float(np.std(log, ddof=1)/np.sqrt(n)) if n > 1 else None
    p = (float(2*student_t.sf(abs(ig/se), n-1)) if se and se > 0
         else (1. if ig == 0 and n > 1 else (0. if n > 1 else None)))
    return dict(N=n, IG=ig, SE=se, p=p, delta_logL=ig*n,
                olay_log_farki=float(log.sum()), integral_farki=nt-nm,
                beklenen_toplam=nm, beklenen_taban=nt)


def gunluk(taban, adaylar, katalog, izgara, kenarlar, baslangic, bitis, *, hucre_esleyici=None):
    """Bir günlük öngörü; o günün olayları yalnız skor, ertesi gün geçmişidir.

    Hücre tahminleri biriktirilmez; sadece olay hücresi değerleri ve tam bölge
    integralleri tutulur. Adaylar sigma -> normalize hücre şekli sözlüğüdür.
    """
    bas, son = _aralik(baslangic, bitis)
    if son > ACIK_SON:
        raise ValueError('iç doğrulama koşucusu kör pencereyi açmaz')
    times = pd.to_datetime(katalog.zaman, utc=True)
    if (times >= ACIK_SON).any():
        raise ValueError('katalogda kör/mühürlü satır var; kullanmayın')
    if times.isna().any():
        raise ValueError('geçersiz katalog zamanı')
    grid, edges = izgara_dogrula(izgara), kenarlar_dogrula(kenarlar)
    # Olay -> hücre eşlemesi bir kez; dışarıda kalanlar ayrıca raporlanır.
    cells, mags = [], []
    for r in katalog.itertuples(index=False):
        if not np.isfinite([r.boylam,r.enlem,r.mw]).all():
            raise ValueError('geçersiz olay koordinatı/büyüklüğü')
        ix = np.flatnonzero((grid[:,0]<=r.boylam)&(r.boylam<grid[:,1])
                            &(grid[:,2]<=r.enlem)&(r.enlem<grid[:,3]))
        cells.append(int(ix[0]) if len(ix)==1 else -1)
        mags.append(int(np.searchsorted(edges,r.mw,side='right')-1))
    cells, mags = np.asarray(cells), np.asarray(mags)
    if hucre_esleyici is not None:
        cells = np.asarray(hucre_esleyici(katalog,izgara),int)
        if cells.shape != (len(katalog),):
            raise ValueError('hücre eşleyici boyutu farklı')
    valid = (cells>=0)&(mags>=0)&(mags<len(edges)-1)
    event_base, event_fay = [], {s:[] for s in adaylar}
    event_mw = []
    total_base, total_fay = 0., {s:0. for s in adaylar}
    for t0 in pd.date_range(bas, son, freq='D', inclusive='left'):
        t1 = min(t0+pd.Timedelta(days=1), son)
        past = katalog.loc[times<t0]
        a = _dizi(taban.beklenen(t0,t1,past,izgara,edges))
        bg = _dizi(taban.arka_plan_beklenen(t0,t1,past,izgara,edges))
        target = np.flatnonzero((times>=t0)&(times<t1)&valid)
        i, j = cells[target], mags[target]
        event_base.extend(a[i,j].tolist())
        event_mw.extend(katalog.iloc[target].mw.to_numpy(float).tolist())
        total_base += float(a.sum())
        for s, u in adaylar.items():
            pred = degistir(a,bg,u,1.)
            event_fay[s].extend(pred[i,j].tolist())
            total_fay[s] += float(pred.sum())
    window = (times>=bas)&(times<son)&(katalog.mw>=edges[0])
    return dict(olay_taban=np.asarray(event_base), olay_mw=np.asarray(event_mw),
                olay_fay={s:np.asarray(v) for s,v in event_fay.items()},
                toplam_taban=total_base, toplam_fay=total_fay,
                dis=int((window&~valid).sum()))


def ortak_yukle(yol):
    """Deney T'nin gerçek modelini yükle; tarih/hash/alt-kritiklik kapıları."""
    from knotenlinie.ortak_zemin.arayuz import model_yukle
    p = json.loads(Path(yol).read_text(encoding='utf-8'))
    if pd.to_datetime(p['ayar_bitis'], utc=True) > AYAR_SON:
        raise ValueError('ortak ETAS ayarı ≤2010 değil')
    return model_yukle(p['bolge'], ortak=Path(yol).parent)


def ayar_oku(yol):
    """Dondurulmuş ortak taban fabrikası ve D2 ağırlığını yükle; ayar yapmaz."""
    d = json.loads(Path(yol).read_text(encoding='utf-8'))
    mod, fonk = d['etas_fabrika'].split(':')
    taban = OrtakTaban(getattr(importlib.import_module(mod), fonk)(d['etas_yolu']))
    fay = fay_oku(d['fay_yolu'], surum=d['surum'], en_gec=d['kaynak_en_gec'],
                  beklenen_sha256=DISS_SHA256)
    return ETASFay(taban,fay,agirlik=d['agirlik'],sigma_km=d['sigma_km'],
                   b=d.get('b',1.),sekil_esik=d.get('sekil_esik',4.95))
