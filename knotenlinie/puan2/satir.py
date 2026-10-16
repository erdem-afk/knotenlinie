"""Bir (aday, taban, eşik) satırı: IG, SE_blok, SE_HAC, T/W iki yanlı, N-Poisson/NBD, ikili IG."""
from __future__ import annotations

import numpy as np
from scipy import stats

from knotenlinie.karsilastir.blok import blok_ozeti
from knotenlinie.karsilastir.puan import eslestirilmis, n_testi
from knotenlinie.skor_defteri import karisim as K

from . import KANIT_DUZEYI
from .hac import hac_ozeti
from .ikili import benzersiz_olay_lam, ikili_logL_defter
from .nbd import nbd_n_testi

N_KUCUK = 30
Z_ESIK = 1.645


def hukum_eski(ig, z_blok):
    if ig is None or z_blok is None:
        return 'belirsiz'
    if ig <= 0:
        return 'başarısızlık'
    return 'başarı' if z_blok > Z_ESIK else 'belirsiz'


def hukum_yeni(ig, z_blok, z_hac, p_t, p_w, n, *, hac_gerekli=True):
    """KURAL.md §5 (+ Ek 1: uzun vadede HAC tanımsız, ``hac_gerekli=False``)."""
    if ig is None or z_blok is None or (hac_gerekli and z_hac is None):
        return 'belirsiz'
    if ig <= 0:
        return 'başarısızlık'
    p = p_w if n < N_KUCUK else p_t
    if p is None:
        return 'belirsiz'
    return 'başarı' if (z_blok > Z_ESIK and (not hac_gerekli or z_hac > Z_ESIK) and p < 0.10) else 'belirsiz'


def kazanc_satiri(k, lam_olay_aday, lam_olay_taban, Lam_aday_gun, Lam_taban_gun, *, gun_lam_etiket=None):
    """``karisim.gun_kazanci`` çıktısı ``k`` + olay λ'ları (eşik maskeli) üzerinden bütün SE/p."""
    D, n, gunler, N = k['D'], k['n'], k['gunler'], k['N']
    blok = blok_ozeti(D, n, gunler, n=N)
    out = dict(N=N, Lambda_aday=k['Lambda_aday'], Lambda_taban=k['Lambda_taban'], IG=k['IG'],
               IG_olay=k['IG_olay'], integral=k['integral'],
               SE_blok=blok['SE_blok'], z_blok=blok['z'], p_tek_blok=blok['p_tek'])
    h = hac_ozeti(D, n, n=N)
    h7 = hac_ozeti(D, n, gecikme=7, n=N)
    h0 = hac_ozeti(D, n, gecikme=0, n=N)
    out.update(SE_HAC=h['SE_HAC'], z_HAC=h['z'], p_tek_HAC=h['p_tek'], gecikme_HAC=h['gecikme'],
               SE_HAC7=h7['SE_HAC'], z_HAC7=h7['z'], SE_gun_iid=h0['SE_HAC'])
    if N >= 2:
        r = eslestirilmis(lam_olay_aday, lam_olay_taban, k['Lambda_aday'], k['Lambda_taban'])
        out.update(T=r.get('T'), p_T=r.get('p_T'), W=r.get('W'), p_W=r.get('p_W'), SE_iid_olay=r.get('SE'),
                   **w_yan(lam_olay_aday, lam_olay_taban, k['Lambda_aday'], k['Lambda_taban']))
    else:
        out.update(T=None, p_T=None, W=None, p_W=None, SE_iid_olay=None, p_W_tam=None, bag_var=None, p_W_perm=None, not_=None)
    out['z_tek_yonlu_blok'] = blok['z']
    out['iki_yanli_p_blok'] = None if blok['p_tek'] is None else float(min(1.0, 2 * blok['p_tek']))
    out['iki_yanli_p_HAC'] = None if h['p_tek'] is None else float(min(1.0, 2 * h['p_tek']))
    out['eski_hukum'] = hukum_eski(k['IG'], blok['z'])
    out['yeni_hukum'] = hukum_yeni(k['IG'], blok['z'], h['z'], out['p_T'], out['p_W'], N)
    out['kanit_duzeyi'] = KANIT_DUZEYI
    return out


def _y_wilcoxon(lam_a, lam_t, Ta, Tt):
    a, b = np.asarray(lam_a, float), np.asarray(lam_t, float)
    n = len(a)
    return np.log(a) - np.log(b) - (Ta - Tt) / n


def w_perm(y):
    """Bağ-düzeltmeli (ortalama rank) işaret-çevirme permütasyonu, iki yanlı, tam sayım (n<=20).
    Sıfırlar atılır (zero_method='wilcox'). Dönüş p ya da None."""
    y = np.asarray(y, float)
    y = y[y != 0]
    n = len(y)
    if n < 1 or n > 20:
        return None
    r = stats.rankdata(np.abs(y))
    obs = r[y > 0].sum()
    ort = r.sum() / 2.0
    bits = (np.arange(2 ** n)[:, None] >> np.arange(n)) & 1
    t = bits @ r
    return float(np.mean(np.abs(t - ort) >= abs(obs - ort) - 1e-9))


def w_yan(lam_a, lam_t, Ta, Tt):
    """YAN SÜTUN (hükme girmez): exact W, bağ bayrağı, bağ-düzeltmeli permütasyon p.
    scipy exact bağsız veri varsayar; bağ varsa exact geçersizdir."""
    a = np.asarray(lam_a, float)
    n = len(a)
    if n < 2 or n > 50:
        return dict(p_W_tam=None, bag_var=None, p_W_perm=None, not_=None)
    y = _y_wilcoxon(lam_a, lam_t, Ta, Tt)
    nz = np.abs(y[y != 0])
    bag = bool(len(np.unique(np.round(nz, 12))) < len(nz) or (y == 0).any())
    p_exact = w_tam(lam_a, lam_t, Ta, Tt)
    return dict(p_W_tam=p_exact, bag_var=bag, p_W_perm=w_perm(y),
                not_='bağ var, exact geçersiz' if bag else None)


def w_tam(lam_a, lam_t, Ta, Tt):
    """Küçük N için scipy exact Wilcoxon (YAN SÜTUN); `puan.eslestirilmis` ile aynı y; başarısızsa None."""
    a, b = np.asarray(lam_a, float), np.asarray(lam_t, float)
    n = len(a)
    if n < 2 or n > 50:
        return None
    y = _y_wilcoxon(a, b, Ta, Tt)
    if np.all(y == 0):
        return 1.0
    try:
        return float(stats.wilcoxon(y, zero_method='wilcox', correction=False,
                                    alternative='two-sided', method='exact').pvalue)
    except Exception:
        return None


def n_testleri(Lam, N, a):
    """Poisson ve NBD (δ1, δ2); a=None ise NBD yok."""
    p = n_testi(Lam, N)
    out = dict(N_Poisson=dict(d1=p['ust_kuyruk'], d2=p['alt_kuyruk'], gecti=p['gecti']))
    if a is None:
        out['N_NBD'] = None
    else:
        q = nbd_n_testi(Lam, N, a=a)
        out['N_NBD'] = dict(d1=q['ust_kuyruk'], d2=q['alt_kuyruk'], gecti=q['gecti'], varyans=q['varyans'], a=a)
    return out


def ikili_ig(defterler, agirliklar, taban, alt):
    """Hücre-gün-kutu ikili logL farkı (aday − taban)/N; defterden tam (simülasyonsuz)."""
    lam_o, Lam_g, mask = K.bilesen(defterler, agirliklar, alt)
    ref = defterler[0].olay
    sec = ref.loc[mask]
    lam_t = taban.lam()[mask]
    ln_a = ikili_logL_defter(benzersiz_olay_lam(sec['gun'], sec['hucre'], sec['kutu'], lam_o[mask]),
                             float(Lam_g.sum()))
    ln_t = ikili_logL_defter(benzersiz_olay_lam(sec['gun'], sec['hucre'], sec['kutu'], lam_t),
                             float(K._gun_vektoru(taban, alt).sum()))
    N = int(mask.sum())
    return dict(lnL_ikili_aday=ln_a, lnL_ikili_taban=ln_t, IG_ikili=(ln_a - ln_t) / N if N else None,
                max_lam_olay=float(max(lam_o[mask].max(), lam_t.max())) if N else None)
