"""TR-6a yapay dünya ve §9 adım 2 sınamaları (yalnız yapay veri; numpy + standart kitaplık).

- YapayDunya / YapayKaynak: bilinen yapay sonlu fay(lar), bilinen alıcı tensörleri, Dieterich (1994) oran yanıtı (Aσ,
  τ̇0, adım), bölgede ve/veya lobda GK tipi ikincil diziler, isteğe bağlı ana şok sonrası tamlık kaybı
  Mc(t) = M_ana − 4,5 − 0,75 log10(t / 1 g) ve bölge artçı payı. YapayKaynak, tr6a_kosu.Analiz'in kaynak arayüzünü
  gerçek kaynakla aynı tarih/aşama denetimleriyle (KAT.tarih_denetle, t0 − 30 g aşama sınırı) sağlar.
- yapay_katalog_sinamasi: §9 adım 2 (i) ve (ii); tohum 20261114, ölçüt başına ≥ 20 000 deneme (bağlayıcı).
- tamlik_sinamasi: §9 adım 2 tamlık kaybı sınaması ve yedek merdiveni; tohum 20261115, hücre başına ≥ 20 000 deneme.
- baglayici_sinamalar / gelistirme_sinamalari: bağlayıcı tohumlar yalnız baglayici_sinamalar'da; geliştirme
  bağlayıcı tohumları reddeder (her basamak bir kez koşulur, §9 adım 2).
Kodlayıcı okumaları 14-19 (TR-6a_KODLAYICI-OKUMALARI.md) bu dosyanın sınama kurgusunu tanımlar.
"""
import copy
import datetime as dt
import math
import os
import sys

import numpy as np

BURAYA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURAYA)
import tr6a_onkayit_sayilar as S   # noqa: E402
import tr6a_okada as OK            # noqa: E402
import tr6a_katalog as KAT         # noqa: E402
import tr6a_kosu as KO             # noqa: E402

TOHUM_KATALOG, TOHUM_TAMLIK = 20261114, 20261115
BAGLAYICI_TOHUMLAR = (TOHUM_KATALOG, TOHUM_TAMLIK)
N_BAGLAYICI = 20000
MU = 30e9
GK_d = lambda m: 10 ** (0.1238 * m + 0.983)                                          # noqa: E731
GK_g = lambda m: np.where(m >= 6.5, 10 ** (0.032 * m + 2.7389), 10 ** (0.5409 * m - 0.547))  # noqa: E731
BIN_PAY = (0.4, 0.2, 0.4)       # Mc_h, Mc_h + 0,1 kutuları ve Mc_h + 0,2 üstü (G-R b = 1): MAXC = Mc_h kararlı


def L_wc(M):
    return 10 ** (-3.55 + 0.74 * M)


# ================================================================== yapay sonlu fay ve tensör
def yapay_ffm(la, lo, M, dogrultu=0.0, egim=90.0, rake=180.0, W=20.0, dx=10.0, dz=5.0, ust=0.0):
    """tr6a_ffm.coz biçiminde yapay sonlu fay: alt fay merkezleri ("merkez"), kayma m, moment N·m (μ 30 GPa)."""
    Lf = L_wc(M)
    nx, nz = max(2, int(round(Lf / dx))), max(1, int(round(W / dz)))
    dxx = Lf / nx
    M0 = 10 ** (1.5 * M + 9.1)
    w = np.array([math.sin(math.pi * (i + 0.5) / nx) for i in range(nx)])
    alan = dxx * dz * 1e6
    s0 = M0 / (MU * alan * nz * w.sum())
    f, d = math.radians(dogrultu), math.radians(egim)
    sv = np.array([math.sin(f), math.cos(f)])
    dv = np.array([math.cos(f), -math.sin(f)])        # eğim yönü (yatay)
    alt = []
    for i in range(nx):
        for k in range(nz):
            a = -Lf / 2 + (i + 0.5) * dxx
            et = (k + 0.5) * dz
            xy = a * sv + et * math.cos(d) * dv
            la_, lo_ = OK.aeqd_geri(la, lo, xy[0], xy[1])
            alt.append(dict(segment=1, enlem=float(la_), boylam=float(lo_), derinlik=ust + et * math.sin(d),
                            kayma=float(s0 * w[i]), rake=rake, dogrultu=dogrultu, egim=egim, uzunluk=dxx,
                            genislik=dz, moment=float(MU * s0 * w[i] * alan), koordinat="merkez", satir=len(alt)))
    return dict(bicim="yapay", altfaylar=alt, koordinat="merkez", koordinat_kaynagi="yapay", M0_kaynagi="yapay",
                moment=dict(gecti=True), n_altfay=len(alt), n_segment=1, dikeye_yakin=0)


def tensor_mekanizmadan(dogrultu, egim, rake):
    n, s = OK.alici_vektorleri(dogrultu, egim, rake)
    Mx = np.outer(n, s) + np.outer(s, n)              # DKY (E, N, U)
    return (Mx[2, 2], Mx[1, 1], Mx[0, 0], -Mx[2, 1], Mx[2, 0], -Mx[1, 0])


# ================================================================== yapay liste
def yapay_liste(birimler, havuz_ek=()):
    """birimler: [dict(id, zaman (iso), M, enlem, boylam, uyeler=[(id, zaman, M, la, lo)], mekanizma_sinif,
    kataloglar={k: mc}, ...)]. tr6a_olay_listesi.json'daki alanları (sahte geçerliliği dahil) aynı kurallarla kurar."""
    olaylar, bl = [], []
    for b in birimler:
        uy = b.get("uyeler") or [(b["id"], b["zaman"], b["M"], b["enlem"], b["boylam"])]
        for (i, z, M, la, lo) in uy:
            olaylar.append(dict(id=i, zaman=z, M=M, enlem=la, boylam=lo, L_km=round(L_wc(M), 1), grup=b["id"],
                                mekanizma_sinif=b.get("mekanizma_sinif", "doğrultu atımlı")))
    for (i, z, M, la, lo) in havuz_ek:
        olaylar.append(dict(id=i, zaman=z, M=M, enlem=la, boylam=lo, L_km=round(L_wc(M), 1), grup=i,
                            mekanizma_sinif="doğrultu atımlı"))
    for b in birimler:
        uy = b.get("uyeler") or [(b["id"], b["zaman"], b["M"], b["enlem"], b["boylam"])]
        buyuk = max(uy, key=lambda x: (x[2], x[1]))
        kat = {k: dict(mc=mc, N0_halka=100.0, N0_halka_mc05=50.0, tur="tam sayım", gecersiz_sifir_buyukluk=False,
                       mc_dar_kural=None) for k, mc in b["kataloglar"].items()}
        isc_dus = bool(b.get("isc_kurali_ile_dusen", False))
        bl.append(dict(id=b["id"], uyeler=[x[0] for x in uy], buyuk_uye=buyuk[0], M=buyuk[2], enlem=buyuk[3],
                       boylam=buyuk[4], L_km=round(L_wc(buyuk[2]), 1), halka_km=[0, 0], zaman=uy[0][1], t_s=uy[-1][1],
                       kataloglar=kat, secilebilir_kataloglar=sorted(k for k in kat if not (k == "ISC" and isc_dus)),
                       isc_kurali_ile_dusen=isc_dus, kosu_adayi=True,
                       mekanizma_sinif=b.get("mekanizma_sinif", "doğrultu atımlı")))
    # sahte geçerliliği (tr6a_onkayit_sayilar.aday_listesi ile aynı kural)
    T = dt.datetime.fromisoformat
    for b in bl:
        t0, ts = T(b["zaman"]), T(b["t_s"])
        sahte = []
        for j in range(1, S.SAHTE_J + 1):
            tj = t0 - dt.timedelta(days=S.SAHTE_ILK_G + S.SAHTE_ADIM_G * (j - 1))
            s0, s1 = tj + (ts - t0) + dt.timedelta(days=S.SON_G0), tj + dt.timedelta(days=S.SON_G1)
            ort = [x["id"] for x in olaylar if x["grup"] != b["id"] and T(x["zaman"]) < s1
                   and T(x["zaman"]) + dt.timedelta(days=365) > s0 and S.km(b, x) < 3 * x["L_km"] + 3 * b["L_km"]]
            sahte.append(dict(j=j, t=tj.isoformat(timespec="seconds"), gecerli=not ort, ortusen=ort))
        b["sahte"] = sahte
    olaylar.sort(key=lambda x: x["zaman"])
    return dict(olaylar=olaylar, birimler=sorted(bl, key=lambda x: x["zaman"]))


# ================================================================== büyüklük üretimi
def buyukluk(rng, n, mc_h, m_ust=8.5):
    """Sürekli büyüklük: [mc_h − 0,05, mc_h + 0,05) %40, [mc_h + 0,05, mc_h + 0,15) %20, ≥ mc_h + 0,15 G-R b = 1 %40."""
    u = rng.random(n)
    m = np.empty(n)
    a = u < BIN_PAY[0]
    b = (u >= BIN_PAY[0]) & (u < BIN_PAY[0] + BIN_PAY[1])
    c = ~(a | b)
    m[a] = mc_h - 0.05 + 0.1 * rng.random(int(a.sum()))
    m[b] = mc_h + 0.05 + 0.1 * rng.random(int(b.sum()))
    m[c] = np.minimum(m_ust, mc_h + 0.15 + rng.exponential(1 / math.log(10), int(c.sum())))
    return m


def rapor(m):
    return np.round(m + 1e-9, 1)


# ================================================================== yapay dünya
class YapayDunya:
    """Birim başına gerçek (bilinen) geometri ve oran modeli. Bir (birim, katalog) için bütün tarih bir kez üretilir
    ve dilimlenir (ön ve son istekler aynı gerçekleşmeden)."""

    def __init__(self, liste, rng, spec):
        """spec: {birim_id: dict(N0, mc_h, dtau ('sifir'|'adim'|'dieterich'), tdot (kPa/yıl), ikincil_bolge,
        ikincil_lob, tamlik (None | dict(ap)), N0_poz, N0_notr, mekanizma (strike, dip, rake), havuz_disi)}"""
        self.liste, self.rng, self.spec = liste, rng, spec
        self.birim = {b["id"]: b for b in liste["birimler"]}
        self.olay = {o["id"]: o for o in liste["olaylar"]}
        self.ffm, self.tensor, self.geo, self.cache = {}, {}, {}, {}
        for o in liste["olaylar"]:
            sp = spec.get(o["grup"], {})
            mek = sp.get("mekanizma", (0.0, 90.0, 180.0))
            self.ffm[o["id"]] = yapay_ffm(o["enlem"], o["boylam"], o["M"], *mek)
        for b in liste["birimler"]:
            mek = spec.get(b["id"], {}).get("mekanizma", (0.0, 90.0, 180.0))
            self.tensor[b["id"]] = [tensor_mekanizmadan(*mek)] * 6

    def geometri(self, u):
        if u in self.geo:
            return self.geo[u]
        b = self.birim[u]
        af = [dict(a, uye=x) for x in b["uyeler"] for a in self.ffm[x]["altfaylar"]]
        izd = OK.altfaylari_izdus(af, b["enlem"], b["boylam"])
        al = OK.alici_sec(self.tensor[u], af)
        G = OK.izgara_hesapla(izd, b["L_km"], {"ana": al["alici"], "ikinci": al["ikinci"]}, r_ic=0.0)
        H = dict(r_k=G["r_k"], tekil=G["tekil"], dA=G["dcff"]["ana"], dB=G["dcff"]["ikinci"])
        M = KO.hucre_maskeleri(H, b["L_km"])
        an = KO._anahtar(G["i"], G["j"])
        o = np.argsort(an)
        self.geo[u] = dict(x=G["x"], y=G["y"], M=M, dA=H["dA"], r_k=G["r_k"], anahtar=an[o], sira=o)
        return self.geo[u]

    def olaylar(self, u, k):
        if (u, k) in self.cache:
            return self.cache[(u, k)]
        b, sp, rng = self.birim[u], self.spec.get(u, {}), self.rng
        g = self.geometri(u)
        M = g["M"]
        mc_h = float(b["kataloglar"][k]["mc"])
        t0, ts = KAT.gun(b["zaman"]), KAT.gun(b["t_s"])
        T0, T1 = t0 - KO.SAHTE_ON_INDIRME_G - 30.0, t0 + 400.0
        ng = max(1, int(M["golge"].sum()))
        rho = sp.get("N0", 40.0) / ng / BIN_PAY[2]                   # hücre başına, taban üstü, /yıl
        w = np.full(len(g["x"]), rho)
        if M["pozitif"].any() and sp.get("N0_poz") is not None:
            w[M["pozitif"]] = sp["N0_poz"] / M["pozitif"].sum() / BIN_PAY[2]
        if M["notr"].any() and sp.get("N0_notr") is not None:
            w[M["notr"]] = sp["N0_notr"] / M["notr"].sum() / BIN_PAY[2]
        # Dieterich adımı: gölge −10, pozitif +10 kPa (yalnız 'adim'/'dieterich'); diğer hücreler 0
        dtau = np.zeros(len(w))
        if sp.get("dtau", "sifir") != "sifir":
            dtau[M["golge"]] = -S.DTAU_ESIK
            dtau[M["pozitif"]] = +S.DTAU_ESIK
        ta = math.inf if sp.get("dtau") != "dieterich" else S.ASIGMA / sp["tdot"] * 365.25
        carp_max = np.exp(np.maximum(dtau, 0) / S.ASIGMA)
        parcalar = []
        for (a, z, carp) in ((T0, t0, np.ones(len(w))), (t0, T1, carp_max)):
            lam = w * carp * (z - a) / 365.25
            n = rng.poisson(lam)
            h = np.repeat(np.arange(len(w)), n)
            t = rng.uniform(a, z, len(h))
            if a >= t0:
                q = np.exp(-dtau[h] / S.ASIGMA)                       # Dieterich: R/r = 1/[(q − 1) e^(−t/t_a) + 1]
                tt = np.maximum(t - ts, 0.0)
                oran = 1.0 / q if not math.isfinite(ta) else 1.0 / ((q - 1) * np.exp(-tt / ta) + 1)
                kabul = rng.random(len(h)) < oran / carp_max[h]
                h, t = h[kabul], t[kabul]
            parcalar.append((h, t))
        h = np.concatenate([p[0] for p in parcalar])
        t = np.concatenate([p[1] for p in parcalar])
        m = buyukluk(rng, len(h), mc_h)
        x = g["x"][h] + rng.uniform(-4.999, 4.999, len(h))
        y = g["y"][h] + rng.uniform(-4.999, 4.999, len(h))
        # ikincil diziler (GK tipi): bölgede (lob dışı) ve/veya lobda
        lobmask = M["golge"] | M["pozitif"] | M["notr"]
        if sp.get("ikincil_bolge") or sp.get("ikincil_lob"):
            ana = m >= mc_h + 0.95
            if sp.get("ikincil_lob") and not sp.get("ikincil_bolge"):
                ana &= lobmask[h]
            if sp.get("ikincil_bolge") and not sp.get("ikincil_lob"):
                ana &= ~lobmask[h]
            ia = np.nonzero(ana)[0]
            na = rng.poisson(0.5 * 10 ** (0.8 * (m[ia] - mc_h - 1.0)))
            src = np.repeat(ia, na)
            if len(src):
                mm = np.minimum(buyukluk(rng, len(src), mc_h), m[src])
                gg = GK_g(m[src]) * 0.9
                dt_ = np.minimum(gg, 0.05 * ((1 - rng.random(len(src))) ** (-1 / 0.1) - 1))
                ang = rng.uniform(0, 2 * math.pi, len(src))
                rr = GK_d(m[src]) * 0.8 * np.sqrt(rng.random(len(src)))
                xa, ya = x[src] + rr * np.cos(ang), y[src] + rr * np.sin(ang)
                ta_ = t[src] + dt_
                hi, hj = OK.hucre_indeksi(xa, ya)
                ka = KO._anahtar(hi, hj)
                pos = np.minimum(np.searchsorted(g["anahtar"], ka), len(g["sira"]) - 1)
                var = g["anahtar"][pos] == ka
                hh = np.where(var, g["sira"][pos], -1)
                tut = var & (ta_ < T1)
                if not sp.get("ikincil_lob"):
                    tut &= ~lobmask[np.maximum(hh, 0)]
                if not sp.get("ikincil_bolge"):
                    tut &= lobmask[np.maximum(hh, 0)]
                h = np.concatenate([h, hh[tut]])
                t = np.concatenate([t, ta_[tut]])
                m = np.concatenate([m, mm[tut]])
                x = np.concatenate([x, xa[tut]])
                y = np.concatenate([y, ya[tut]])
        # ana şok sonrası tamlık kaybı ve bölge artçıları (§9 adım 2 biçimi)
        tm = sp.get("tamlik")
        if tm:
            dis = M["bolge"] & ~lobmask
            idx = np.nonzero(dis)[0]
            on_lob = (h >= 0) & lobmask[np.maximum(h, 0)] & (t >= ts + 30) & (t < t0 + 365)
            n_as = int(round(on_lob.sum() * tm["ap"] / max(1e-9, 1 - tm["ap"]))) if tm["ap"] > 0 else 0
            if n_as and len(idx):
                u_ = rng.random(n_as)
                a_, z_ = 30.0, 365.0
                # (t + 0,05)^−1,1 yoğunluğundan [30, 365) içinde ters CDF ile
                F = lambda q: (q + 0.05) ** -0.1                           # noqa: E731
                ta_ = ((F(a_) - u_ * (F(a_) - F(z_))) ** (-10.0)) - 0.05 + ts
                hh = idx[rng.integers(0, len(idx), n_as)]
                h = np.concatenate([h, hh])
                t = np.concatenate([t, ta_])
                m = np.concatenate([m, buyukluk(rng, n_as, mc_h)])
                x = np.concatenate([x, g["x"][hh] + rng.uniform(-4.999, 4.999, n_as)])
                y = np.concatenate([y, g["y"][hh] + rng.uniform(-4.999, 4.999, n_as)])
            Mana = b["M"]
            gec = t >= ts
            mc_t = np.where(gec, Mana - 4.5 - 0.75 * np.log10(np.maximum(t - ts, 1e-6)), -99.0)
            tut = m >= mc_t
            h, t, m, x, y = h[tut], t[tut], m[tut], x[tut], y[tut]
        la, lo = OK.aeqd_geri(b["enlem"], b["boylam"], x, y)
        o = np.argsort(t, kind="stable")
        d = dict(id=[f"{u}-{k}-{i}" for i in range(len(o))], t=t[o], la=np.asarray(la)[o], lo=np.asarray(lo)[o],
                 de=np.full(len(o), 10.0), m=rapor(m[o]), mtip=np.array(["ml"] * len(o), dtype=object))
        self.cache[(u, k)] = d
        return d


class YapayKaynak:
    """tr6a_kosu.Analiz kaynak arayüzü; gerçek kaynakla aynı tarih ve aşama denetimleri."""

    def __init__(self, dunya, asama="on"):
        self.d, self.asama, self.istekler = dunya, asama, []

    def ffm(self, uye):
        return copy.deepcopy(self.d.ffm[uye])

    def tensorler(self, b):
        return list(self.d.tensor[b["id"]])

    def katalog(self, b, k, t_bas, t_bit, taban, R_km, merkez, asama):
        t0 = dt.datetime.fromisoformat(b["zaman"])
        if asama != self.asama:
            raise KO.KosuDur(f"aşama uyuşmazlığı: {asama} ≠ {self.asama}")
        sinir = t0 - dt.timedelta(days=30) if asama == "on" else t_bit
        KAT.tarih_denetle(t_bas, t_bit - dt.timedelta(milliseconds=1), sinir)
        self.istekler.append((b["id"], k, t_bas, t_bit, asama))
        d = self.d.olaylar(b["id"], k)
        a, z = KAT.gun(t_bas), KAT.gun(t_bit)
        r = OK.R_DUNYA * np.arccos(np.clip(np.sin(np.radians(merkez[0])) * np.sin(np.radians(d["la"]))
                                           + np.cos(np.radians(merkez[0])) * np.cos(np.radians(d["la"]))
                                           * np.cos(np.radians(d["lo"] - merkez[1])), -1, 1))
        s = (d["t"] >= a) & (d["t"] < z) & (d["m"] >= taban - 1e-9) & (r <= R_km)
        return {kk: (np.asarray(v, dtype=object)[s] if kk in ("id", "mtip") else v[s]) for kk, v in d.items()}


# ================================================================== tek birimlik sınama ortamı
def tek_birim(M=7.8, mc=1.0, la=10.0, lo=20.0, zaman="2010-06-01T00:00:00", mek=(0.0, 90.0, 180.0)):
    b = dict(id="yapay1", zaman=zaman, M=M, enlem=la, boylam=lo, kataloglar={"ISC": mc},
             mekanizma_sinif="doğrultu atımlı")
    return yapay_liste([b]), dict(mekanizma=mek)


class TekBirimSinama:
    """Bir yapay birimin geometrisi bir kez kurulur; her denemede yeni katalog gerçekleşmesi ile bütün hat
    (yerleştirme, Mc_lob, kapı, Mc_son, kümesizleştirme, oy, sahte kalibrasyon) koşulur."""

    def __init__(self, M=7.8, mc=1.0, mek=(0.0, 90.0, 180.0), log=None, kural="A2"):
        self.liste, self.mek = tek_birim(M=M, mc=mc, mek=mek)
        self.u = self.liste["birimler"][0]["id"]
        d0 = YapayDunya(self.liste, np.random.default_rng(0), {self.u: dict(mekanizma=mek)})
        self.an = KO.Analiz(self.liste, YapayKaynak(d0, "on"), kural=kural, log=log or (lambda *a: None))
        self.an.hazirla(havuz_R_A=False)
        self.d0 = d0
        g = d0.geometri(self.u)
        self.geo = g
        self.B = self.an.B[self.u]
        assert np.array_equal(self.B["M"]["golge"], g["M"]["golge"]), "yapay ve hat lob tanımı ayrıştı"

    def deneme(self, rng, sp, sahte=True, nk=False, ham=False):
        """ham=True (TR-6c): aynı gerçekleşmede kümesizleştirmesiz (D4 biçimi) gerçek ve sahte oylar da yazılır; gerçek
        son pencerenin Mc_son'u kestirilemezse (yedek (d)) r["veri_yok"] = True döner ve oy sayılmaz."""
        d = YapayDunya.__new__(YapayDunya)
        d.liste, d.rng, d.spec = self.liste, rng, {self.u: dict(sp, mekanizma=self.mek)}
        d.birim, d.olay, d.ffm, d.tensor = self.d0.birim, self.d0.olay, self.d0.ffm, self.d0.tensor
        d.geo, d.cache = self.d0.geo, {}
        an, B = self.an, self.B
        B["kat"] = {}
        B["durum"] = "hazır"
        an.kaynak = YapayKaynak(d, "on")
        an.son_eklendi = False
        an.on_katalog()
        an.katalog_secimi()
        k = B["secim"]
        kp = B["kapi"][k]["golge"]
        r = dict(N0_kapi=kp["N0"], mc_lob=kp["mc_lob"], kapi=kp["N0"] >= KO.ESIK[19.0])
        if sahte:
            so = an.sahte_oylari(B, k)
            r["sahte"] = [(x["D"], x["A"]) for x in so if x["gecerli"]]
            if ham:
                r["sahte_ham"] = []
                for x in so:
                    if x["gecerli"]:
                        oh = an.lob_oyu(B, k, "golge", an.pencere(B, "sahte", x["j"]), x["mc_kul"], kumesiz=False)
                        r["sahte_ham"].append((oh["D"], oh["A"]))
        if nk:
            r["nk"] = an.nk_oyu(B, k)
        plan = [dict(birim=self.u, katalog=k, t_bas=KAT.zaman(B["t0"]).isoformat(timespec="milliseconds"),
                     t_bit=KAT.zaman(B["son_bit"]).isoformat(timespec="milliseconds"), taban=B["kat"][k]["taban"],
                     R_km=B["R_sorgu"], merkez=[B["la"], B["lo"]])]
        an.son_ekle(plan, YapayKaynak(d, "son"))
        P = an.pencere(B, "gercek")
        ms, _ = an.mc_son(B, k, P, kp["mc_lob"])
        if ham and ms is None:                          # Ek 1 E1.3 (d): birim "veri yok (tamlık kestirilemedi)"
            r.update(veri_yok=True, D=None, A=None)
            return r
        mk = KO.mc_kul(kp["mc_lob"], ms)
        o = an.lob_oyu(B, k, "golge", P, mk)
        r.update(D=o["D"], A=o["A"], n_on=o["n_on"], n_son=o["n_son"], mc_kul=mk, mc_son=ms,
                 dtau=(None if o["ln_oran"] is None else S.ASIGMA * o["ln_oran"]))
        if ham:
            oh = an.lob_oyu(B, k, "golge", P, mk, kumesiz=False)
            r.update(veri_yok=False, D_ham=oh["D"], A_ham=oh["A"], n_on_ham=oh["n_on"], n_son_ham=oh["n_son"])
        if sp.get("pozitif"):
            mlp = B["kapi"][k]["pozitif"]["mc_lob"]
            op = an.lob_oyu(B, k, "pozitif", P, KO.mc_kul(mlp, ms))
            r.update(A_poz=op["A"])
        return r


def _oran_se(x):
    x = np.asarray(x, float)
    return float(x.mean()), float(x.std(ddof=1) / math.sqrt(len(x))) if len(x) > 1 else float("nan")


def yapay_katalog_sinamasi(tohum, n, N0lar=(31.36, 100.0, 500.0), log=print, M=7.8):
    """§9 adım 2 (i) ve (ii). Ölçüt: 3,5 SE (kodlayıcı okumaları 14-17)."""
    rng = np.random.default_rng(tohum)
    T = TekBirimSinama(M=M)
    oy = S.Oy(40000)
    t_on, t1, t2 = S.T_ON_G / 365.25, S.SON_G0 / 365.25, S.SON_G1 / 365.25
    out = dict(tohum=tohum, deneme=n, olcutler=[], lob_hucre=int(T.B["M"]["golge"].sum()))
    ok = True

    def olcut(ad, deger, beklenen, se, bilgi=None):
        nonlocal ok
        z = (deger - beklenen) / se if se > 0 else 0.0
        g = abs(z) <= 3.5
        ok &= g
        out["olcutler"].append(dict(ad=ad, deger=round(deger, 5), beklenen=round(beklenen, 5), se=round(se, 5),
                                    z=round(z, 2), gecti=bool(g), bilgi=bilgi))
        log(f"  {ad}: {deger:.4f} beklenen {beklenen:.4f} (z {z:+.2f}) {'GEÇTİ' if g else 'TUTMADI'}")

    # (i) lobda saf Poisson, bölgede ikincil diziler
    for N0 in N0lar:
        D, Dk = [], []
        for _ in range(n):
            r = T.deneme(rng, dict(N0=N0, dtau="sifir", ikincil_bolge=True), sahte=True)
            D.append(r["D"])
            if r["kapi"]:
                Dk.append(r["D"])
        m_, se = _oran_se(D)
        bek = oy.olasilik(N0 * t_on, N0 * (t2 - t1), -1)
        olcut(f"(i) Δτ = 0, N0 {N0:g}: P(D)", m_, bek, math.sqrt(bek * (1 - bek) / n),
              bilgi=dict(kapi_kosullu_PD=(round(float(np.mean(Dk)), 4) if Dk else None), kapi_gecen=len(Dk)))
    N0 = 31.36
    D, dl = [], []
    for _ in range(n):
        r = T.deneme(rng, dict(N0=N0, dtau="adim", ikincil_bolge=True), sahte=False)
        D.append(r["D"])
        if r["dtau"] is not None:
            dl.append(r["dtau"])
    m_, se = _oran_se(D)
    lam = S.dieterich_N(N0, t1, t2, -S.DTAU_ESIK, S.ASIGMA, math.inf)
    bek = oy.olasilik(N0 * t_on, lam, -1)
    olcut("(i) kalıcı −10 kPa, N0 31,36: P(D)", m_, bek, math.sqrt(bek * (1 - bek) / n), bilgi=dict(tablo=0.987))
    alt = float(np.mean(np.asarray(dl) < -10.23))
    olcut("(i) Δτ_est medyanı: −10,23'ün altındaki pay", alt, 0.5, 0.5 / math.sqrt(len(dl)),
          bilgi=dict(medyan=round(float(np.median(dl)), 3), tablo=-10.23, n=len(dl)))
    # (ii) lobda GK tipi ikincil diziler
    for N0 in N0lar:
        Dg, Ss, Js = [], [], []
        for _ in range(n):
            r = T.deneme(rng, dict(N0=N0, dtau="sifir", ikincil_bolge=True, ikincil_lob=True), sahte=True)
            Ss.append(sum(x[0] for x in r["sahte"]))
            Js.append(len(r["sahte"]))
            if r["kapi"]:
                Dg.append(r["D"])
        Ss, Js = np.array(Ss, float), np.array(Js, float)
        if Js.sum() == 0 or len(Dg) < 2:
            olcut(f"(ii) N0 {N0:g}: p̂₀ beklenen değeri", float("nan"), 0.0, 1.0)
            continue
        p0b = Ss.sum() / Js.sum()
        se0 = float(np.std(Ss - p0b * Js, ddof=1) / (Js.mean() * math.sqrt(len(Js))))
        pd_, sed = _oran_se(Dg)
        olcut(f"(ii) N0 {N0:g}: p̂₀ beklenen değeri − gerçek P(D) (kapı koşullu)", p0b - pd_, 0.0,
              math.sqrt(se0 ** 2 + sed ** 2), bilgi=dict(p0_sapka=round(p0b, 4), P_D=round(pd_, 4), J=int(Js.sum())))
    out["gecti"] = bool(ok)
    out["ozet"] = "; ".join(f"{o['ad']} z {o['z']}" for o in out["olcutler"] if not o["gecti"]) or "hepsi tuttu"
    return out


# ================================================================== tamlık sınaması (histogram düzeyi)
def _bin_payi(v, mc_t):
    """Kutu [v − 0,05, v + 0,05) içindeki G-R (b = 1) kütlesinin Mc(t) üstündeki payı."""
    lo, hi = v - 0.05, v + 0.05
    c = np.clip(mc_t, lo, hi)
    return (10 ** (-(c - lo)) - 10 ** (-(hi - lo))) / (1 - 10 ** (-(hi - lo)))


def tamlik_hucresi(rng, n, M_ana, Mc_lob, N0, ap, kural, oy_tablosu, bolge_carpani=1.0, ayrinti=False):
    """Bir hücre: Mc_halka = Mc_lob − 0,2 (taban Mc_lob − 0,25), G-R b = 1; lobda saf Poisson arka plan (ön pencere
    tam, son pencerede Mc(t) kesimi); bölge = lob + (bolge_carpani − 1) × lob kadar başka arka plan + Omori artçıları
    (bölge son penceresinin algılama öncesi payı ap). Kodlayıcı okuması 18: bolge_carpani = 1 (bölge arka planı = lob
    arka planı). Mc_lob ve Mc_son tr6a_katalog'un kendi işlevleriyle (MAXC, alt pencere birleştirme) hesaplanır.
    Dönüş: düşüş oyu oranı."""
    mc_h = round(Mc_lob - 0.2, 2)
    kut = np.round(mc_h + 0.1 * np.arange(0, 60), 2)
    pk = 10 ** (-(kut - 0.05 - (mc_h - 0.05))) * (1 - 10 ** -0.1)       # G-R kutu olasılıkları (taban mc_h − 0,05)
    oran_taban = N0 * 10 ** (Mc_lob - 0.05 - (mc_h - 0.05))          # Mc_lob üstü N0 -> taban üstü oran /yıl
    S0 = KAT.SON_BASLANGIC_G[kural]
    pens = KAT.alt_pencereler(0.0, 365.0, kural)
    dtg = 0.05
    beklenen_lob, beklenen_as = [], []
    w_as_top = 0.0
    tg_all = np.arange(S0, 365.0, dtg) + dtg / 2
    was_all = (tg_all + 0.05) ** -1.1
    was_all /= was_all.mean()
    for (a, b) in pens:
        tg = np.arange(a, b, dtg) + dtg / 2
        mc_t = M_ana - 4.5 - 0.75 * np.log10(tg)
        frac = _bin_payi(kut[None, :], mc_t[:, None])                       # (zaman, kutu)
        lob = oran_taban / 365.25 * dtg * (pk[None, :] * frac).sum(0)
        was = (tg + 0.05) ** -1.1 / ((tg_all + 0.05) ** -1.1).mean()
        as_ = oran_taban * bolge_carpani / 365.25 * dtg * (ap / max(1e-12, 1 - ap)) \
            * (was[:, None] * pk[None, :] * frac).sum(0) if ap > 0 else np.zeros(len(kut))
        as_ = as_ + (bolge_carpani - 1.0) * lob
        beklenen_lob.append(lob)
        beklenen_as.append(as_)
        w_as_top += float(was.sum())
    on_bek = oran_taban * S.T_ON_G / 365.25 * pk
    T_son = 365.0 - S0
    pi = T_son / (S.T_ON_G + T_son)
    D = np.zeros(n, np.int8)
    ok = np.ones(n, bool)
    for i in range(n):
        h_on = rng.poisson(on_bek)
        mcl, _ = KAT.mc_lob(np.repeat(kut, h_on), mc_h)
        hl = [rng.poisson(x) for x in beklenen_lob]
        ha = [rng.poisson(x) for x in beklenen_as]
        hist = [(kut, l + a) for l, a in zip(hl, ha)]
        ms, _ = KAT.mc_son_hist(hist, mcl, KAT.MC_SON_EK[kural], veri_yok=kural in KAT.TAMLIK_VERI_YOK)
        if ms is None:                                  # Ek 1 E1.3 (d): birim "veri yok (tamlık kestirilemedi)"
            ok[i] = False
            continue
        mk = KO.mc_kul(mcl, ms)
        ust = kut >= mk - 1e-6
        n_on = int(h_on[ust].sum())
        n_son = int(sum(l[ust].sum() for l in hl))
        nn = n_on + n_son
        if nn:
            D[i] = n_son <= oy_tablosu.b_dus[nn] if abs(oy_tablosu.pi - pi) < 1e-12 else KAT.oy(n_on, n_son, pi)[0]
    if ayrinti:
        n_ok = int(ok.sum())
        return dict(P_D=(float(D[ok].mean()) if n_ok else None), n_ok=n_ok, veri_yok_payi=1.0 - n_ok / n)
    return float(D[ok].mean()) if ok.any() else float("nan")


def tamlik_sinamasi(tohum, n, log=print, kurallar=KO.TAMLIK_KURALLARI, hucreler=None, bolge_carpani=1.0,
                    hepsi=False):
    """§9 adım 2: ızgara M_ana {7; 7,5; 8; 9} × Mc_lob {1; 1,8; 3} × N0 {31,36; 100; 500; 4500} × ap {0; 0,9}.
    Ölçüt: düşüş oyu oranı − kesin Poisson H0 ≤ 0,02 her hücrede. Yedekler sırayla; tutan ilk bağlayıcı; her basamak
    bir kez, aynı tohumla."""
    oy = {335: S.Oy(60000, S.T_ON_G, 335), 275: S.Oy(60000, S.T_ON_G, 275)}
    if hucreler is None:
        hucreler = [(Ma, Mc, N0, ap) for Ma in (7.0, 7.5, 8.0, 9.0) for Mc in (1.0, 1.8, 3.0)
                    for N0 in (31.36, 100.0, 500.0, 4500.0) for ap in (0.0, 0.9)]
    out = dict(tohum=tohum, deneme=n, basamaklar={}, secilen=None, bolge_carpani=bolge_carpani)
    for kural in kurallar:
        rng = np.random.default_rng(tohum)
        Ts = 365 - KAT.SON_BASLANGIC_G[kural]
        o = oy[Ts]
        sat = {}
        en_kotu = -1.0
        for (Ma, Mc, N0, ap) in hucreler:
            r = tamlik_hucresi(rng, n, Ma, Mc, N0, ap, kural, o, bolge_carpani, ayrinti=True)
            p0 = o.olasilik(N0 * S.T_ON_G / 365.25, N0 * Ts / 365.25, -1)
            ad = f"M{Ma:g} Mc{Mc:g} N0={N0:g} ap{ap:g}"
            if r["n_ok"] == 0:                                   # Ek 1 E1.3 (d): hücrenin bütün denemeleri veri yok
                sat[ad] = dict(P_D=None, P_D_poisson=round(p0, 4), fark=None, n_ok=0, veri_yok_payi=1.0, gecti=True)
                continue
            p = r["P_D"]
            fark = p - p0
            # Ek 1 E1.3: koşullu (veri yok olmayan denemelerde) fark; n_ok < n iken yalnız fazladan örnekleme
            # hatası kadar (3,5 SE_ek) pay; n_ok = n iken §9 adım 2'nin ölçütüyle aynıdır.
            q = min(max(p, 0.25), 0.75)
            se_ek = math.sqrt(max(0.0, q * (1 - q) / r["n_ok"] - q * (1 - q) / n))
            esik = 0.02 + 3.5 * se_ek
            en_kotu = max(en_kotu, fark)
            sat[ad] = dict(P_D=round(p, 4), P_D_poisson=round(p0, 4), fark=round(fark, 4), n_ok=r["n_ok"],
                           veri_yok_payi=round(r["veri_yok_payi"], 4), esik=round(esik, 4), gecti=fark <= esik)
        gec = all(x["gecti"] for x in sat.values())
        out["basamaklar"][kural] = dict(hucreler=sat, en_buyuk_fark=round(en_kotu, 4), gecti=gec,
                                        gecmeyen=[k for k, x in sat.items() if not x["gecti"]],
                                        veri_yok_payi_ort=round(float(np.mean([x.get("veri_yok_payi", 0.0)
                                                                               for x in sat.values()])), 4))
        log(f"  tamlık {kural}: en büyük fark {en_kotu:+.4f} {'GEÇTİ' if gec else 'TUTMADI'}")
        if gec and out["secilen"] is None:
            out["secilen"] = kural
            if not hepsi:
                break
    out["ozet"] = ("seçilen " + out["secilen"]) if out["secilen"] else "hiçbir basamak tutmadı"
    return out


# ================================================================== bağlayıcı ve geliştirme sınamaları
def baglayici_sinamalar(log=print):
    """§9 adım 2 bağlayıcı: Okada doğrulaması, yapay katalog (20261114, 20 000) ve tamlık (20261115, 20 000)."""
    ok = OK.dogrulama(log=log)
    yk = yapay_katalog_sinamasi(TOHUM_KATALOG, N_BAGLAYICI, log=log)
    tm = tamlik_sinamasi(TOHUM_TAMLIK, N_BAGLAYICI, log=log)
    return dict(okada=ok, yapay_katalog=yk, tamlik=tm, baglayici=True)


def gelistirme_sinamalari(tohum=7, n=400, log=print, okada=True, katalog=True, tamlik=True, hucreler=None):
    if tohum in BAGLAYICI_TOHUMLAR:
        raise ValueError("geliştirme bağlayıcı tohumları kullanamaz (§9 adım 2: her basamak bir kez)")
    out = dict(baglayici=False, tohum=tohum, deneme=n)
    if okada:
        out["okada"] = OK.dogrulama(log=log)
    if katalog:
        out["yapay_katalog"] = yapay_katalog_sinamasi(tohum, n, log=log)
    if tamlik:
        out["tamlik"] = tamlik_sinamasi(tohum + 1, n, log=log, hucreler=hucreler)
    return out


# ================================================================== TR-6c yöntem sınaması (tasarım c)
# TR-6c_gerilme-olcer-kor-dogrulama_ONKAYIT.md §C3. Tamlık kuralı (d) ana kuraldır (merdiven yok). Yapay katalog
# sınamasının Δτ = 0 ölçütü (i) ve (ii) dünyalarında aynı biçimdedir: p̂₀ (sahte pencerelerden, havuzlanmış S/J) − gerçek
# P(D | kapı, veri var) iki yanlı 3,5 SE içinde. Hücreler 1000 denemelik parçalara bölünür; parça p'nin tohumu
# (tohum, hücre kodu, p)'dir, böylece hücreler ayrı ayrı ve kesintiden sonra kaldığı yerden koşulabilir.
TOHUM_KATALOG_C, TOHUM_TAMLIK_C = 20261116, 20261117
BAGLAYICI_TOHUMLAR_C = (TOHUM_KATALOG_C, TOHUM_TAMLIK_C)
TANI_TOHUMLARI = tuple(range(601, 609))
KURAL_C = "yedek_d"
N0_IZGARA_C = (31.36, 100.0, 500.0, 1500.0, 4500.0)
PARCA_C = 1000
HUCRELER_C = tuple([f"i:{x:g}" for x in N0_IZGARA_C] + [f"ii:{x:g}" for x in N0_IZGARA_C] + ["adim:31.36"])
HUCRE_KODU_C = {h: i + 1 for i, h in enumerate(HUCRELER_C)}
ALAN_C = ("kapi", "veri_yok", "D", "A", "Dh", "Ah", "J", "SD", "SA", "SDh", "SAh", "n_on", "n_son", "n_on_h", "n_son_h")


def tohum_denetle_c(tohum, baglayici):
    """Geliştirme ve prova bağlayıcı (TR-6a ve TR-6c) ve tanı (601–608) tohumlarını kullanamaz; bağlayıcı TR-6c koşusu
    yalnız 20261116 (katalog) ve 20261117 (tamlık) ile."""
    if baglayici:
        if tohum not in BAGLAYICI_TOHUMLAR_C:
            raise ValueError("TR-6c bağlayıcı tohumu 20261116 ya da 20261117 olmalı")
        return
    if tohum in BAGLAYICI_TOHUMLAR + BAGLAYICI_TOHUMLAR_C + TANI_TOHUMLARI:
        raise ValueError("geliştirme/prova bağlayıcı ya da tanı tohumu kullanamaz")


def hucre_spec_c(ad):
    dunya, n0 = ad.split(":")
    N0 = float(n0)
    if dunya == "i":
        return N0, dict(N0=N0, dtau="sifir", ikincil_bolge=True)
    if dunya == "ii":
        return N0, dict(N0=N0, dtau="sifir", ikincil_bolge=True, ikincil_lob=True)
    if dunya == "adim":
        return N0, dict(N0=N0, dtau="adim", ikincil_bolge=True)
    raise ValueError(ad)


_T_C = {}


def tek_birim_c():
    if "T" not in _T_C:
        T = TekBirimSinama(M=7.8, kural=KURAL_C)
        T.an.yalniz_golge = True
        _T_C["T"] = T
    return _T_C["T"]


def hucre_parcasi_c(ad, tohum, parca, n=PARCA_C):
    """Bir parçanın deneme kayıtları (ALAN_C sütunları) ve Δτ_est değerleri."""
    T = tek_birim_c()
    _, sp = hucre_spec_c(ad)
    rng = np.random.default_rng([tohum, HUCRE_KODU_C[ad], parca])
    sahte = not ad.startswith("adim")
    sat, dl = [], []
    for _ in range(n):
        r = T.deneme(rng, sp, sahte=sahte, ham=True)
        s, sh = r.get("sahte", []), r.get("sahte_ham", [])
        if r["veri_yok"]:
            sat.append([int(r["kapi"]), 1, -1, -1, -1, -1, len(s), sum(x[0] for x in s), sum(x[1] for x in s),
                        sum(x[0] for x in sh), sum(x[1] for x in sh), -1, -1, -1, -1])
            dl.append(None)
            continue
        sat.append([int(r["kapi"]), 0, r["D"], r["A"], r["D_ham"], r["A_ham"], len(s), sum(x[0] for x in s),
                    sum(x[1] for x in s), sum(x[0] for x in sh), sum(x[1] for x in sh), r["n_on"], r["n_son"],
                    r["n_on_ham"], r["n_son_ham"]])
        dl.append(r["dtau"])
    return dict(hucre=ad, tohum=tohum, parca=parca, n=n, alan=list(ALAN_C), satir=sat, dtau=dl)


def _fark_se(S_, J_, x):
    """p̂₀ = ΣS/ΣJ (havuzlanmış) ile ortalama x arasındaki fark ve SE (TR-6a (ii) ile aynı biçim)."""
    S_, J_, x = (np.asarray(a, float) for a in (S_, J_, x))
    if J_.sum() == 0 or len(x) < 2:
        return None
    p0b = S_.sum() / J_.sum()
    se0 = float(np.std(S_ - p0b * J_, ddof=1) / (J_.mean() * math.sqrt(len(J_))))
    pd_ = float(x.mean())
    sed = float(x.std(ddof=1) / math.sqrt(len(x)))
    return p0b, pd_, p0b - pd_, math.sqrt(se0 ** 2 + sed ** 2)


def kesin_c(N0_kul, T_son=275.0, yon=-1, lam_son=None):
    """Kesin Poisson oy olasılığı, (d) penceresi (T_son 275 g), N0_kul (Mc_kul üstü oran)."""
    L = N0_kul * (S.T_ON_G + T_son) / 365.25
    nmax = int(L + 12 * math.sqrt(L) + 40)
    oy = _OY_C.get((nmax, T_son)) or _OY_C.setdefault((nmax, T_son), S.Oy(nmax, S.T_ON_G, T_son))
    return oy.olasilik(N0_kul * S.T_ON_G / 365.25, (N0_kul * T_son / 365.25) if lam_son is None else lam_son, yon)


_OY_C = {}
MC_FARKI_C = 0.2      # yapay dünyada Mc_kul − Mc_lob = (MAXC + 0,4) − (MAXC + 0,2): N0_kul = N0 · 10^(−0,2)


def dtau_kesin_c(N0_kul, lam_son, T_son=275.0):
    """Δτ_est = Aσ ln[(n_son/T_son)/(n_on/T_on)] dağılımının kesin medyanı m* ve P(Δτ_est < m*) (n_on ≥ 1)."""
    mu_on = N0_kul * S.T_ON_G / 365.25
    a = np.arange(max(1, int(mu_on - 12 * math.sqrt(mu_on))), int(mu_on + 12 * math.sqrt(mu_on) + 20))
    b = np.arange(0, int(lam_son + 12 * math.sqrt(lam_son) + 20))
    lp = lambda k, mu: -mu + k * math.log(mu) - np.array([math.lgamma(x + 1) for x in k])   # noqa: E731
    pa, pb = np.exp(lp(a, mu_on)), np.exp(lp(b, lam_son))
    with np.errstate(divide="ignore"):
        v = S.ASIGMA * (np.log(b[None, :] / T_son) - np.log(a[:, None] / S.T_ON_G))
    w = pa[:, None] * pb[None, :]
    v, w = v.ravel(), w.ravel() / w.sum()
    o = np.argsort(v, kind="stable")
    c = np.cumsum(w[o])
    med = float(v[o][np.searchsorted(c, 0.5)])
    return med, float(w[v < med].sum())


def hucre_ozeti_c(ad, parcalar):
    """Bir hücrenin bütün parçalarından özet ve ölçütler (§C3)."""
    X = np.array([s for p in parcalar for s in p["satir"]], dtype=float)
    c = {k: X[:, i] for i, k in enumerate(ALAN_C)}
    n = len(X)
    N0, _ = hucre_spec_c(ad)
    N0k = N0 * 10 ** (-MC_FARKI_C)
    var = c["veri_yok"] == 0
    kv = var & (c["kapi"] == 1)
    T = tek_birim_c()
    pi = T.B["pi"]
    o = dict(hucre=ad, deneme=n, parca=len(parcalar), tohum=parcalar[0]["tohum"], N0=N0, N0_kul=round(N0k, 3),
             veri_yok_payi=round(float(1 - var.mean()), 5), kapi_payi=round(float((c["kapi"][var] == 1).mean()), 5),
             olcutler=[])

    def olcut(ad_, deger, beklenen, se, bilgi=None):
        z = (deger - beklenen) / se if se > 0 else 0.0
        o["olcutler"].append(dict(ad=ad_, deger=round(deger, 5), beklenen=round(beklenen, 5), se=round(se, 5),
                                  z=round(z, 2), gecti=bool(abs(z) <= 3.5), bilgi=bilgi))

    if ad.startswith("adim"):
        lam = S.dieterich_N(N0k, KAT.SON_BASLANGIC_G[KURAL_C] / 365.25, S.SON_G1 / 365.25, -S.DTAU_ESIK, S.ASIGMA, math.inf)
        bek = kesin_c(N0k, lam_son=lam)
        pd_ = float(c["D"][var].mean())
        olcut("kalıcı −10 kPa: P(D)", pd_, bek, math.sqrt(bek * (1 - bek) / int(var.sum())))
        dl = np.array([x for p in parcalar for x in p["dtau"] if x is not None], float)
        med, q = dtau_kesin_c(N0k, lam)
        olcut("Δτ_est: kesin medyanın altındaki pay", float(np.mean(dl < med)), q,
              math.sqrt(q * (1 - q) / len(dl)), bilgi=dict(medyan=round(float(np.median(dl)), 3),
                                                            kesin_medyan=round(med, 3), n=len(dl)))
        o["gecti"] = all(x["gecti"] for x in o["olcutler"])
        return o
    f = _fark_se(c["SD"][var], c["J"][var], c["D"][kv])
    if f is None:
        olcut("p̂₀ − P(D | kapı)", float("nan"), 0.0, 1.0)
    else:
        p0b, pd_, d_, se = f
        olcut("p̂₀ − P(D | kapı)", d_, 0.0, se, bilgi=dict(p0_sapka=round(p0b, 5), P_D_kapi=round(pd_, 5),
                                                         J_ort=round(float(c["J"][var].mean()), 4)))
    # bilgi satırları
    bilgi = dict(P_D=round(float(c["D"][var].mean()), 5), P_A=round(float(c["A"][var].mean()), 5),
                 P_D_kesin=round(kesin_c(N0k), 5), P_A_kesin=round(kesin_c(N0k, yon=+1), 5),
                 P_D_kapi=round(float(c["D"][kv].mean()), 5), P_A_kapi=round(float(c["A"][kv].mean()), 5),
                 P_Dh_kapi=round(float(c["Dh"][kv].mean()), 5), P_Ah_kapi=round(float(c["Ah"][kv].mean()), 5))
    for ad_, S_, x in (("A", "SA", "A"), ("Dh", "SDh", "Dh"), ("Ah", "SAh", "Ah")):
        f = _fark_se(c[S_][var], c["J"][var], c[x][kv])
        bilgi[f"p0_sapka_{ad_}_eksi_P_kapi"] = None if f is None else dict(
            p0=round(f[0], 5), P=round(f[1], 5), fark=round(f[2], 5), se=round(f[3], 5), z=round(f[2] / f[3], 2))
    for ad_, x, y in (("D", "D", "Dh"), ("A", "A", "Ah")):
        dd = c[x][kv] - c[y][kv]
        bilgi[f"kenar_{ad_}_hat_eksi_ham"] = dict(fark=round(float(dd.mean()), 5),
                                                 se=round(float(dd.std(ddof=1) / math.sqrt(len(dd))), 5))
    bilgi["artik_n_son_eksi_pi_n"] = round(float((c["n_son"][kv] - pi * (c["n_on"][kv] + c["n_son"][kv])).mean()), 3)
    bilgi["n_on_ort"], bilgi["n_son_ort"] = round(float(c["n_on"][kv].mean()), 2), round(float(c["n_son"][kv].mean()), 2)
    bilgi["sahte_gecerli_ort"] = round(float(c["J"][var].mean()), 4)
    o["bilgi"] = bilgi
    o["gecti"] = all(x["gecti"] for x in o["olcutler"])
    return o


def hucre_kos_c(ad, tohum, n, parca_dizini, log=print, baglayici=False):
    """Hücreyi parça parça koşar; var olan parça dosyalarını yeniden kullanır (kesintiye dayanıklı). Dönüş özet."""
    import json
    tohum_denetle_c(tohum, baglayici)
    os.makedirs(parca_dizini, exist_ok=True)
    k = -(-n // PARCA_C)
    parcalar = []
    for p in range(k):
        yol = os.path.join(parca_dizini, f"{ad.replace(':', '_')}_t{tohum}_p{p:03d}.json")
        if os.path.exists(yol):
            with open(yol, encoding="utf-8") as f:
                x = json.load(f)
        else:
            x = hucre_parcasi_c(ad, tohum, p)
            with open(yol + ".tmp", "w", encoding="utf-8") as f:
                json.dump(x, f)
            os.replace(yol + ".tmp", yol)
            log(f"  {ad} parça {p + 1}/{k} yazıldı")
        parcalar.append(x)
    return hucre_ozeti_c(ad, parcalar)


def _parca_yolu(parca_dizini, ad, tohum, p):
    return os.path.join(parca_dizini, f"{ad.replace(':', '_')}_t{tohum}_p{p:03d}.json")


def prova_c(tohum, n, hucreler, parca_dizini, cikti_dizini=None, log=print, ara=None):
    """Dondurma öncesi tam ölçekli prova (bağlayıcı olmayan tohum). Parçalar hücreler arasında sırayla (önce bütün
    hücrelerin 0. parçası, sonra 1. ...) koşulur ve dosyaya yazılır; var olan parça yeniden koşulmaz. Bir hücrenin bütün
    parçaları bitince özeti cikti_dizini/tr6c_prova_<hücre>.json'a yazılır. ara: her turdan sonra ara özet yolu."""
    import json
    tohum_denetle_c(tohum, False)
    os.makedirs(parca_dizini, exist_ok=True)
    k = -(-n // PARCA_C)
    for p in range(k):
        for ad in hucreler:
            yol = _parca_yolu(parca_dizini, ad, tohum, p)
            if os.path.exists(yol):
                continue
            x = hucre_parcasi_c(ad, tohum, p)
            with open(yol + ".tmp", "w", encoding="utf-8") as f:
                json.dump(x, f)
            os.replace(yol + ".tmp", yol)
            log(f"  {ad} parça {p + 1}/{k}")
        if ara:
            oz = {}
            for ad in hucreler:
                ps = [json.load(open(_parca_yolu(parca_dizini, ad, tohum, q), encoding="utf-8")) for q in range(p + 1)]
                oz[ad] = hucre_ozeti_c(ad, ps)
            with open(ara, "w", encoding="utf-8") as f:
                json.dump(oz, f, ensure_ascii=False, indent=1)
    out = {}
    for ad in hucreler:
        ps = [json.load(open(_parca_yolu(parca_dizini, ad, tohum, q), encoding="utf-8")) for q in range(k)]
        o = hucre_ozeti_c(ad, ps)
        o["parca_sha256"] = [KO.sha256_dosya(_parca_yolu(parca_dizini, ad, tohum, q)) for q in range(k)]
        out[ad] = o
        if cikti_dizini:
            with open(os.path.join(cikti_dizini, f"tr6c_prova_{ad.replace(':', '_')}.json"), "w",
                      encoding="utf-8") as f:
                f.write(KO.json_metni(dict(o, baglayici=False, kod_sha256=KO.kod_sha())))
    return out


def _pbinom_ust(c, ps):
    """P(Σ Bernoulli(p_i) ≥ c), kesin (Poisson-binom)."""
    f = np.zeros(len(ps) + 1)
    f[0] = 1.0
    for p in ps:
        f[1:] = f[1:] * (1 - p) + f[:-1] * p
        f[0] *= (1 - p)
    return float(f[c:].sum())


def guc_kaybi_c(kenar, K=23, p1=0.75, f=None, m_liste=(1, 2, 5, 23)):
    """§C7: tasarım dünyasında (küme başına oy olasılığı p1 = f·P_D1 + (1 − f)·w) yanlış loblu kümelerin H0 düzeyindeki
    oy olasılığı w, kenar etkisiyle w + kenar olur (P_D1 değişmez; yüksek N0'da kalıcı −10 kPa'da hat ve ham oy 1,000).
    m küme etkilenirse güç P(X ≥ c(K; 0,50)). f: TR-6a §4.5 (w = H0 düzeyi, K 23, p₀ 0,50) 0,549.
    Ayrıca kural "veri yok" (m küme düşer) karşılaştırması: K − m < 23 ise güç 0 (hüküm "güç yok")."""
    f = 0.549 if f is None else f
    c = S.kritik(K, 0.50)
    d = (1 - f) * kenar
    out = dict(K=K, c=c, f=f, kume_basina_dp=round(d, 5), guc_kenarsiz=round(_pbinom_ust(c, [p1] * K), 4))
    for m in m_liste:
        if m > K:
            continue
        out[f"m{m}"] = dict(guc_hat=round(_pbinom_ust(c, [p1] * (K - m) + [p1 + d] * m), 4),
                            guc_veri_yok=(round(_pbinom_ust(S.kritik(K - m, 0.50), [p1] * (K - m)), 4)
                                          if K - m >= S.K_ALT else 0.0))
    return out


def ters_yon_alfa_c(kenar_A, K=23, pA=None, m_liste=(1, 2, 5, 23)):
    """§C4: H0'da gölge artış oyu olasılığı pA (kenarsız); m kümede pA + kenar_A. Ters yön notunun gerçek α'sı
    P(Y ≥ c(K; 0,50))."""
    c = S.kritik(K, 0.50)
    pA = 0.47 if pA is None else pA
    out = dict(K=K, c=c, pA=pA, alfa_kenarsiz=round(_pbinom_ust(c, [pA] * K), 4))
    for m in m_liste:
        if m <= K:
            out[f"m{m}"] = round(_pbinom_ust(c, [pA] * (K - m) + [min(1.0, pA + kenar_A)] * m), 4)
    return out


def tamlik_prova_c(tohum, n, log=print):
    """Tamlık sınaması, yalnız (d) kuralı (TR-6c'de ana kural; merdiven yok), §9 adım 2 ızgarası ve Ek 1 E1.3 ölçütü."""
    tohum_denetle_c(tohum, False)
    return tamlik_sinamasi(tohum, n, log=log, kurallar=(KURAL_C,))


# ================================================================== çok birimli yapay dünya (uçtan uca hat sınaması)
def coklu_dunya(tohum=5, n_gecen=26, n_dusuk=3, dtau="adim", N0=60.0, N0_dusuk=8.0, M=7.0, ozel=True, tamlik=None):
    """Birbirinden > 300 km uzak birimler (her biri ayrı küme). Özel birimler: bilinen sonuçlu (us20005iis, çıkar),
    Tohoku kimliği (kalır), iki üyeli grup, son penceresi havuz olayıyla 29 g'ye kesilen (çıkar) ve 69 g'ye kesilen
    (kalır) birimler. Dönüş (liste, spec, dunya)."""
    rng = np.random.default_rng(tohum)
    t = dt.datetime(2004, 1, 1)
    bl, spec, ek = [], {}, []
    adlar = [f"y{i:02d}" for i in range(n_gecen + n_dusuk)]
    if ozel:
        adlar[0], adlar[1] = S.BILINEN_CIKAN[0], S.BILINEN_KALAN[0]
    for i, ad in enumerate(adlar):
        z = t + dt.timedelta(days=97 * i)
        la, lo = -30.0 + 2.2 * (i % 25), -170.0 + 13.0 * i % 340
        b = dict(id=ad, zaman=z.isoformat(), M=M, enlem=la, boylam=lo, kataloglar={"ISC": 2.0, "ComCat": 2.5},
                 mekanizma_sinif=("doğrultu atımlı" if i % 3 else MEGATHRUST_AD))
        if ozel and i == 2:
            z2 = z + dt.timedelta(days=2)
            b["uyeler"] = [(ad, z.isoformat(), M, la, lo), (ad + "b", z2.isoformat(), M - 0.3, la + 0.3, lo)]
        if ozel and i in (3, 4):
            gun_ = 60 if i == 3 else 100
            ek.append((f"havuz{i}", (z + dt.timedelta(days=gun_)).isoformat(), 6.1, la + 0.25, lo + 0.25))
        bl.append(b)
        spec[ad] = dict(N0=(N0_dusuk if i >= n_gecen else N0), dtau=dtau, ikincil_bolge=True, N0_poz=30.0,
                        N0_notr=50.0, tamlik=tamlik)
    liste = yapay_liste(bl, havuz_ek=ek)
    for o in liste["olaylar"]:
        spec.setdefault(o["grup"], dict(N0=5.0))
    return liste, spec, YapayDunya(liste, rng, spec)


MEGATHRUST_AD = "ters, düşük eğimli (megathrust dahil)"
