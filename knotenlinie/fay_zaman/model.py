"""Fay tabanlı zamana bağlı uzun vade modeli (AH).

Katmanlar: (1) fay katmanı — kaynak başına moment dengeli M ≥ M_MIN_FAY oranı,
karakteristik (YC85-tipi) ya da kesik GR; BPT açıksa son olayı ayar tarihinde
bilinen ISS'lerde Mmax−0,5…Mmax aralığındaki orana g = P_BPT/P_Poisson uygulanır;
(2) arka plan — Z2'nin modeli (Weichert toplam × Z şekli). Çifte sayım kuralı:
M ≥ M_MIN_FAY kutularında arka planın bölge toplamı W_j'den fay katmanının
(Poisson-eşdeğer, ızgara içi) toplamı F_j düşülür; F_j > W_j ise fay katmanı
W_j'ye ölçeklenir (toplam ≤ Weichert; bağlaşım üst sınır olduğundan). BPT
çarpanı bu eşitlemeden sonra uygulanır, yani zaman bağımlılığı toplamı
değiştirebilir.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from knotenlinie.fay_zaman import bpt as bptm
from knotenlinie.fay_zaman import moment as mom
from knotenlinie.fay_zaman.izdusum import Izgara

M_MIN_FAY = 5.45        # "M ≥ 5,5" kutusunun alt kenarı
ALFA = 0.5              # aperiyodiklik (ortak sınıf parametresi)
KAR_GENISLIK = 0.5      # karakteristik aralık: Mmax−0,5 … Mmax
YIL_GUN = 365.25


def yil_float(ts):
    t = pd.Timestamp(ts)
    return t.year + (t.dayofyear - 1) / 366.0 + (t.hour / 24.0) / 366.0


class FayKatmani:
    """Kaynak tablosu + hücre payları; MFD ve zaman bağımlılığı varyantla seçilir."""

    def __init__(self, tablo, izgara, *, mfd, b, bpt=False, alfa=ALFA, m_min=M_MIN_FAY):
        if mfd not in ('gr', 'kar'):
            raise ValueError('mfd gr/kar olmalı')
        self.izgara = izgara.reset_index(drop=True)
        self.mfd, self.b, self.bpt, self.alfa, self.m_min = mfd, float(b), bool(bpt), float(alfa), m_min
        g = Izgara(self.izgara)
        self.kaynaklar = []
        atilan = dict(mmax_alt=0, izgara_disi=0, moment_sifir=0)
        for r in tablo.itertuples(index=False):
            if r.mdot <= 0:
                atilan['moment_sifir'] += 1
                continue
            if r.mmax <= self.m_min + 1e-9:
                atilan['mmax_alt'] += 1
                continue
            idx, pay, disari = g.paylar(r.poligon)
            if len(idx) == 0:
                atilan['izgara_disi'] += 1
                continue
            pr = mom.parcalar(mfd, self.m_min, float(r.mmax), self.b)
            S = mom.olcek(pr, r.mdot)
            kar_alt = max(self.m_min, float(r.mmax) - KAR_GENISLIK)
            lam_kar = float(S * sum(mom.parca_integral(p, kar_alt, r.mmax) for p in pr))
            self.kaynaklar.append(dict(id=r.id, katman=r.katman, idx=idx, pay=pay, disari=disari,
                                       parcalar=pr, S=S, mmax=float(r.mmax), kar_alt=kar_alt,
                                       lam_kar=lam_kar, son_yil=r.son_yil, mdot=r.mdot))
        self.atilan = atilan

    def kutu(self, kenarlar):
        """Kaynak başına (yıllık kutu sayısı, karakteristik kısım) listesi."""
        out = []
        for s in self.kaynaklar:
            toplam = mom.kutu_sayilari(s['parcalar'], s['S'], kenarlar, lo=self.m_min, hi=s['mmax'])
            kar = mom.kutu_sayilari(s['parcalar'], s['S'], kenarlar, lo=s['kar_alt'], hi=s['mmax'])
            out.append((toplam, kar))
        return out

    def carpanlar(self, bas_yil, sure_yil):
        """Kaynak başına g (BPT kapalı / son olay yok → 1)."""
        g = np.ones(len(self.kaynaklar))
        if not self.bpt:
            return g
        for i, s in enumerate(self.kaynaklar):
            if s['katman'] == 'ISS' and np.isfinite(s['son_yil']) and s['lam_kar'] > 0:
                e = bas_yil - s['son_yil']
                if e >= 0:
                    g[i] = bptm.carpan(1.0 / s['lam_kar'], self.alfa, e, sure_yil)
        return g

    def hucre_dizisi(self, kenarlar, bas_yil, sure_yil):
        """(Poisson-eşdeğer, zaman bağımlı) hücre×kutu beklenen sayılar (süre dahil)."""
        n, k = len(self.izgara), len(kenarlar) - 1
        poi, td = np.zeros((n, k)), np.zeros((n, k))
        g = self.carpanlar(bas_yil, sure_yil)
        for s, (toplam, kar), gi in zip(self.kaynaklar, self.kutu(kenarlar), g):
            poi[s['idx']] += s['pay'][:, None] * toplam[None, :] * sure_yil
            td[s['idx']] += s['pay'][:, None] * ((toplam - kar) + gi * kar)[None, :] * sure_yil
        return poi, td


class FayZaman:
    """Ortak model arayüzü: beklenen(baslangic, bitis, gecmis, izgara, m_kenarlar)."""

    def __init__(self, katman, arka_plan, ad='AH', kapak=True, pay_ust=0.9):
        self.katman, self.arka_plan, self.ad, self.kapak = katman, arka_plan, ad, kapak
        self.pay_ust = float(pay_ust)
        self.metadata = dict(mfd=katman.mfd, bpt=katman.bpt, b=katman.b, alfa=katman.alfa,
                             atilan=katman.atilan, kaynak_sayisi=len(katman.kaynaklar))
        self.son_tani = {}

    def beklenen(self, baslangic, bitis, gecmis, izgara, m_kenarlar):
        bas, son = pd.Timestamp(baslangic), pd.Timestamp(bitis)
        sure = (son - bas).total_seconds() / (86400.0 * YIL_GUN)
        bg = self.arka_plan.beklenen(baslangic, bitis, gecmis, izgara, m_kenarlar).copy()
        poi, td = self.katman.hucre_dizisi(m_kenarlar, yil_float(bas), sure)
        W, F = bg.sum(axis=0), poi.sum(axis=0)
        olcek = np.ones_like(W)
        act = F > 0
        if self.kapak:
            olcek[act] = np.minimum(1.0, self.pay_ust * W[act] / F[act])
        else:
            olcek[act] = 1.0
        # arka plan: W − olcek·F (kapakta tam W'ye iner); şekil değişmez
        fac = np.ones_like(W)
        pos = W > 0
        fac[pos] = np.maximum(W[pos] - olcek[pos] * F[pos], 0.0) / W[pos]
        out = bg * fac[None, :] + td * olcek[None, :]
        self.son_tani = dict(W=W.tolist(), F=F.tolist(), olcek=olcek.tolist(), fac=fac.tolist(),
                             td_toplam=float((td * olcek[None, :]).sum()), poi_toplam=float(poi.sum()))
        return out
