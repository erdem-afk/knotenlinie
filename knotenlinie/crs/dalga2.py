"""Ortak, donmuş ETAS'a CRS ekle; toplu günlük oranlar ve ≤2010 seçim."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from scipy.special import gammaln, softmax

from knotenlinie.etas.model import yerel_metrik
from .arayuz import buyukluk_paylari, gecmis_dogrula, pencere_dogrula
from .girdi import AYAR_SON, SON, KUTU, k9_basamaklari
from .italya import crs_gunluk, sayim

from knotenlinie.yollar import KOSU, VERI  # noqa: E402

RAPOR_DIZINI = KOSU / "F"
ORTAK_DIZINI = VERI / "ortak"


def izgara_dogrula(izgara):
    """CSEP maskesi eski 1° prototip kutusuna kesilmez (batı sınırı 5.5°)."""
    cols = ["boylam_min", "boylam_max", "enlem_min", "enlem_max"]
    g = izgara[cols].astype(float)
    if (g.empty or not np.isfinite(g.to_numpy()).all()
            or (g.boylam_max <= g.boylam_min).any()
            or (g.enlem_max <= g.enlem_min).any() or g.duplicated().any()):
        raise ValueError("ızgara boş/geçersiz/tekrarlı")
    return g


def alici_paylari(izgara, faylar, sigma_km=30.):
    """İlk sürümün 30 km alıcı karışımı; ETAS arka planını yeniden kurmaz."""
    g = izgara_dogrula(izgara)
    if not np.isfinite(sigma_km) or sigma_km <= 0 or faylar.empty:
        raise ValueError("alıcılar ve sigma geçersiz")
    met = yerel_metrik(KUTU)
    x, y = met.km((g.boylam_min+g.boylam_max).to_numpy()/2,
                  (g.enlem_min+g.enlem_max).to_numpy()/2)
    fx, fy = met.km(faylar.centroid_lon.to_numpy(), faylar.centroid_lat.to_numpy())
    if not np.isfinite(np.r_[fx, fy]).all():
        raise ValueError("alıcı koordinatları sonlu olmalı")
    return softmax(-((x[:, None]-fx)**2+(y[:, None]-fy)**2)/(2*sigma_km**2), axis=1)


def melez(etas, arka_plan, oranlar, pay, agirlik):
    """Tetiklemeye dokunma: λ_mix=λ_ETAS+w B (R−1); B ortak tabanın kendisi."""
    e, b = np.asarray(etas, float), np.asarray(arka_plan, float)
    r, q = np.asarray(oranlar, float), np.asarray(pay, float)
    if (e.ndim != 2 or b.shape != (e.shape[1],) or q.ndim != 2
            or q.shape[0] != e.shape[1] or r.shape != (e.shape[0], q.shape[1])):
        raise ValueError("toplu melez biçimleri uyuşmuyor")
    if (not 0 <= agirlik <= 1 or not all(np.isfinite(x).all() for x in (e, b, r, q))
            or any((x < 0).any() for x in (e, b, r, q))
            or not np.allclose(q.sum(axis=1), 1., rtol=0., atol=1e-12)
            or np.any(e < b[None, :]-1e-12)):
        raise ValueError("ortak ETAS/arka plan/alıcı oranı geçersiz")
    # Null aynen döner; toplama/çıkarma yuvarlamasından yapay IG çıkmaz.
    if agirlik == 0:
        return e.copy()
    tetikleme = np.maximum(e-b[None, :], 0.)
    return tetikleme+b[None, :]*((1-agirlik)+agirlik*(r @ q.T))


def skor_ozeti(aday_olay, taban_olay, toplam_aday, toplam_taban):
    """Tam integral terimli IG; SE olay log-oranı örneklem sapması / sqrt(N)."""
    a, b = np.asarray(aday_olay, float), np.asarray(taban_olay, float)
    if (a.ndim != 1 or a.shape != b.shape or not np.isfinite(np.r_[a, b]).all()
            or (a <= 0).any() or (b <= 0).any()
            or not np.isfinite([toplam_aday, toplam_taban]).all()
            or min(toplam_aday, toplam_taban) < 0):
        raise ValueError("olay oranları pozitif, toplamlar sonlu olmalı")
    n = len(a)
    if n == 0:
        return dict(N=0, IG=None, SE=None, p=None, GA95=None, sebep="N=0")
    x = np.log(a)-np.log(b)
    integral = -(toplam_aday-toplam_taban)/n
    ig = float(x.mean()+integral)
    se = float(np.std(x, ddof=1)/np.sqrt(n)) if n > 1 else None
    if se is None:
        p, ga = None, None
    elif se == 0:
        p = 1. if ig == 0 else 0.
        ga = [ig, ig]
    else:
        p = float(2*stats.t.sf(abs(ig/se), n-1))
        h = float(stats.t.ppf(.975, n-1)*se)
        ga = [ig-h, ig+h]
    return dict(N=n, IG=ig, SE=se, p=p, GA95=ga, IG_olay=float(x.mean()),
                integral_terimi=float(integral), p_yontemi="iki yönlü eşleştirilmiş T",
                sebep=None if n > 1 else "N<2")


def olc(katalog, izgara, faylar, *, baslangic, m0, b, arka_plan,
        etas_blok, asigmalar=(30000., 100000., 300000.),
        agirliklar=(0., .1, .25, .5, 1.), blok_gun=32, kaynak_hesabi=k9_basamaklari):
    """Donmuş ortak taban callback'i ile ölç; burada ETAS ayarı/KDE yok.

    etas_blok(gunler): Mc üzeri (gün,hücre) oranı. Ortak uzay çekirdekleri
    bir kez önhesaplanır; knotenlinie.crs.italya.etas_gunluk gibi toplu yol kullanılır.
    arka_plan: aynı tabanın Mc üzeri günlük arka plan hücre kütlesi.
    Callback yalnız gün başı geçmişi kullanmalı; bu sözleşme bağlayıcıda doğrulanır.
    """
    a, _ = pencere_dogrula(baslangic, SON)
    if a != a.normalize() or a >= AYAR_SON:
        raise ValueError("ayar başlangıcı ≤2010 UTC gece yarısı olmalı")
    if not np.isfinite([m0, b]).all() or b <= 0 or m0 > 4.95:
        raise ValueError("Mc≤4.95 ve b>0 gerekir")
    if blok_gun < 1 or int(blok_gun) != blok_gun:
        raise ValueError("blok gün pozitif tamsayı olmalı")
    if (not asigmalar or not np.isfinite(asigmalar).all() or min(asigmalar) <= 0
            or not agirliklar or 0. not in agirliklar
            or not np.isfinite(agirliklar).all() or min(agirliklar) < 0 or max(agirliklar) > 1):
        raise ValueError("Aσ>0; ağırlık [0,1], null aday zorunlu")
    d = gecmis_dogrula(katalog, SON)
    # Ortak tabanın başlangıç/Mc kuralı CRS replay'e de uygulanır.
    d = d[(d.zaman >= a) & (d.mw >= m0)].copy()
    g = izgara_dogrula(izgara)
    gunler = pd.date_range(a, SON-pd.Timedelta(days=1), freq="D")
    pay = alici_paylari(g, faylar)
    ts, ds = kaynak_hesabi(d, faylar)
    ratios = [crs_gunluk(gunler, ts, ds, s, faylar.tau_dot_pa_gun.to_numpy())
              for s in asigmalar]
    adaylar = [(s, w) for s in asigmalar for w in agirliklar]
    arka_plan = np.asarray(arka_plan, float)
    if arka_plan.shape != (len(g),) or not np.isfinite(arka_plan).all() or (arka_plan < 0).any():
        raise ValueError("ortak arka plan biçimi/değeri geçersiz")
    # Boş hücre cezaları tam, fakat CRS kompansatörü alıcı boyutuna indirgenir:
    # Σ_cell B_cell Σ_fault pay_cell,fault R_fault = (B @ pay) @ R.
    alici_arka_plan = arka_plan @ pay
    ayar_ll = np.zeros(len(adaylar)); val_ll = np.zeros(len(adaylar))
    toplam = np.zeros(len(adaylar)); olay = [[] for _ in adaylar]
    taban_olay = []; taban_toplam = 0.; taban_ll = 0.
    n_ayar = 0; esik_ayar = max(4., m0)
    pay_ayar = buyukluk_paylari([esik_ayar, np.inf], m0, b)[0]
    pay_val = buyukluk_paylari([4.95, np.inf], m0, b)[0]
    for start in range(0, len(gunler), blok_gun):
        days = gunler[start:start+blok_gun]
        e = np.asarray(etas_blok(days), float)
        if e.shape != (len(days), len(g)):
            raise ValueError("ortak taban blok biçimi yanlış")
        train = days < AYAR_SON
        nt = sayim(d, g, days, esik_ayar)[train]
        nv = sayim(d, g, days, 4.95)[~train]
        n_ayar += int(nt.sum())
        if (not np.isfinite(e).all() or (e < 0).any()
                or np.any(e < arka_plan[None, :]-1e-12)):
            raise ValueError("ortak taban arka planından küçük/geçersiz")
        base_sum = e.sum(axis=1)
        def seyrek(rates, counts, total):
            if ((rates <= 0) & (counts > 0)).any():
                return -float("inf")
            return float((counts*np.log(rates)).sum()-total-gammaln(counts+1).sum())
        # Aynı hücre/günde iki olay, T testinde de iki ayrı eşleşmedir.
        ti, tc = np.nonzero(nt); vi, vc = np.nonzero(nv)
        train_idx = np.flatnonzero(train)[ti]
        val_idx = np.flatnonzero(~train)[vi]
        bt = e[train_idx, tc]*pay_ayar; bv = e[val_idx, vc]*pay_val
        base_total = float(base_sum[~train].sum()*pay_val)
        taban_olay.extend(np.repeat(bv, nv[vi, vc]).tolist())
        taban_toplam += base_total
        taban_ll += seyrek(bv, nv[vi, vc], base_total)
        for si, _ in enumerate(asigmalar):
            ri = ratios[si][start:start+len(days)]
            rt_crs = (ri[train_idx]*pay[tc]).sum(axis=1)
            rv_crs = (ri[val_idx]*pay[vc]).sum(axis=1)
            crs_sum = ri @ alici_arka_plan
            trigger_t = np.maximum(e[train_idx, tc]-arka_plan[tc], 0.)
            trigger_v = np.maximum(e[val_idx, vc]-arka_plan[vc], 0.)
            trigger_sum = np.maximum(e-arka_plan[None, :], 0.).sum(axis=1)
            for wi, w in enumerate(agirliklar):
                i = si*len(agirliklar)+wi
                rt = bt if w == 0 else (trigger_t+arka_plan[tc]*((1-w)+w*rt_crs))*pay_ayar
                rv = bv if w == 0 else (trigger_v+arka_plan[vc]*((1-w)+w*rv_crs))*pay_val
                mix_sum = trigger_sum+(1-w)*arka_plan.sum()+w*crs_sum
                st = float(base_sum[train].sum()*pay_ayar) if w == 0 else float(
                    mix_sum[train].sum()*pay_ayar)
                sv = base_total if w == 0 else float(mix_sum[~train].sum()*pay_val)
                ayar_ll[i] += seyrek(rt, nt[ti, tc], st)
                val_ll[i] += seyrek(rv, nv[vi, vc], sv)
                toplam[i] += sv
                olay[i].extend(np.repeat(rv, nv[vi, vc]).tolist())
    if not np.isfinite(ayar_ll).any():
        raise ValueError("hiçbir aday ayar olaylarını desteklemiyor")
    sec = int(np.argmax(ayar_ll))  # yalnız ≤2010; eşitlik ilk aday/null lehine
    tarama = [dict(asigma_pa=s, agirlik=w, logL_ayar=float(ayar_ll[i]))
              for i, (s, w) in enumerate(adaylar)]
    sonuc = dict(aday="ETAS+CRS", bolge="italya", taban="ortak ETAS (deney T)",
                 durum="olculdu", dogrulama=[AYAR_SON.isoformat(), SON.isoformat()],
                 esik_mw=4.95, izgara_hucre=len(g), izgara="CSEP İtalya 0.1°",
                 ayar_baslangic=a.isoformat(), ayar_son=AYAR_SON.isoformat(),
                 esik_ayar_mw=esik_ayar, n_ayar=n_ayar, Mc=m0, b=b,
                 crs_secili=tarama[sec], asigma_tanimlanabilir=adaylar[sec][1] != 0,
                 beklenen_toplam=float(toplam[sec]), beklenen_taban=taban_toplam,
                 logL=float(val_ll[sec]), logL_taban=taban_ll,
                 kaynak_zaman_sayisi=len(ts), alici_sayisi=len(faylar),
                 tarama=tarama, secim="yalnız ≤2010 Poisson skor argmax; doğrulama seçmez")
    sonuc.update(skor_ozeti(olay[sec], taban_olay, toplam[sec], taban_toplam))
    # İlk sürümde sabitlenmiş alternatif; hiçbir validation optimizasyonu yok.
    if (100000., .25) in adaylar:
        i = adaylar.index((100000., .25))
        alt = skor_ozeti(olay[i], taban_olay, toplam[i], taban_toplam)
        alt.update(asigma_pa=100000., agirlik=.25, beklenen_toplam=float(toplam[i]),
                   logL=float(val_ll[i]), rol="önceden sabit tanı; seçilmiş aday değil")
        sonuc["sabit_100kpa_w025"] = alt
    return sonuc


def girdi_kontrol(ortak=ORTAK_DIZINI):
    """Eksik ortak girdiyi adlandır; eski skora geri düşme."""
    gereken = [Path(ortak)/s for s in ("italya_katalog_le2015.csv", "etas_italya_le2010.json",
                                       "italya_izgara.csv")]
    eksik = [str(p) for p in gereken if not p.is_file()]
    return gereken, eksik


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ortak", type=Path, default=ORTAK_DIZINI)
    parser.add_argument("--kontrol", action="store_true", help="yalnız girdi kapısını kaydet")
    parser.add_argument("--tam", action="store_true", help="tam 1985–2015 toplu ölçüm")
    parser.add_argument("--fay", type=Path, default=VERI / 'diss320/iss320.geojson')
    parser.add_argument("--blok-gun", type=int, default=32)
    args = parser.parse_args(argv)
    if args.kontrol == args.tam:
        parser.error('--kontrol ya da --tam seçin')
    gereken, eksik = girdi_kontrol(args.ortak)
    sonuc = dict(aday="ETAS+CRS", bolge="italya", taban="ortak ETAS (deney T)",
                 durum="girdi_bekleniyor" if eksik else "baglayici_bekleniyor",
                 N=None, IG=None, SE=None, p=None, beklenen_toplam=None,
                 beklenen_taban=None, esik_mw=4.95,
                 dogrulama=[AYAR_SON.isoformat(), SON.isoformat()],
                 eksik_girdiler=eksik,
                 sebep="Ortak taban olmadan gerçek F2 ölçümü yapılmaz; null değerler sıfır kazanç değildir.",
                 girdi=[dict(yol=str(p), sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                        for p in gereken if p.is_file()])
    if args.tam and not eksik:
        import time
        from knotenlinie.ortak_zemin.arayuz import model_yukle, omori_kutle
        from knotenlinie.ortak_zemin.veri import katalog_oku
        from .ortak_taban import TopluOrtak
        from .girdi import fay_oku
        before = time.monotonic()
        taban = model_yukle('italya', args.ortak)
        if sonuc['girdi'][0]['sha256'] != taban.p['katalog_sha256']:
            raise ValueError('katalog SHA256 ortak parametrelerle uyuşmuyor')
        toplu = TopluOrtak(taban, katalog_oku(gereken[0]), omori_kutle)
        f = fay_oku(args.fay)
        sonuc = olc(toplu.katalog, toplu.izgara, f, baslangic=taban.baslangic,
                    m0=toplu.m0, b=toplu.b, arka_plan=toplu.arka_plan,
                    etas_blok=toplu.gunluk, blok_gun=args.blok_gun)
        sonuc.update(ortak_dallanma=taban.p['dallanma'],
                     ortak_taban_durumu=taban.p['durum'],
                     ortak_uzay_ayar_destegi=taban.p['uzay_ayar_destegi'],
                     duvar_saniye=time.monotonic()-before,
                     girdi=[dict(yol=str(p), sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                            for p in gereken+[args.fay]],
                     baglayici='T DuzETAS._arka_plan/_mekan + etas_gunluk; T omori_kutle aynen',
                     bagimsiz_inceleme='F2 yeni skor kodu incelemesi bekliyor')
    (RAPOR_DIZINI/"OLCUM2.json").write_text(
        json.dumps(sonuc, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in sonuc.items() if k not in ('girdi', 'tarama')},
                     ensure_ascii=False, indent=2))
    return 0 if sonuc['durum'] == 'olculdu' else 2


if __name__ == "__main__":
    raise SystemExit(main())
