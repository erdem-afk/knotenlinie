#!/usr/bin/env python3
"""TR-13 yeniden açma şartı (a): temiz olaylar için referans dönemi ve eşleşik kontrol pencerelerinin TAM sayımı (0 €).

Kurallar TR-13_SAYIM.md §3.1'den AYNEN alınır; yalnız örnek yerine tam veriyle sayılır:
  * Hedef olaylar: tr13_sayim.py say çıktısında (sayim4.json) M >= 6,0, N3bg_en_iyi[mc] >= 50, önce-pencere temiz.
  * Mc = MAXC + 0,2 (>= 50 olay; 20–49 olayda MAXC + 0,3). Referans şartı: Mc_ref <= Mc_önce + tol ve
    N_ref,bg >= 2 x 50, tol 0,1 / 0,3. GK74 (tr13_sayim.gk74).
  * ComCat olayları: referans zaten tamdı (kat_ComCat, [t-10y, t), R_ind, Mc_ref = [t-10y, t-5y) MAXC+0,2);
    değer sayim4.json'dan aynen alınır.
  * ISC/GeoNet/EMSC olayları: referans [t-10y, t-3y) R dairesinde, yıl yıl TAM indirilir (en küçük büyüklük
    Mc_önce - 0,3, tam3 ile aynı biçim). Mc_ref bu 7 yılın MAXC + 0,2'si; GK74 bu pencerede, R dairesinde
    (ISC tam3 sayımıyla aynı yöntem).
  * Eşleşik kontrol penceresi (tanım aynen): bitişi t_c = t - 6k y (k = 1..7), t_c - 10 y >= 1975,
    [t_c - 3 y, t_c + 3 y] içinde dairede (R) havuzda M >= 5,5 yok. YENİ olan yalnız doluluğun ölçülmesidir:
    kontrolün önce-penceresi [t_c-3y, t_c) ve kendi referansı [t_c-10y, t_c-3y) hedefle AYNI kuralla sayılır:
      önce dolu:  Mc_c <= Mc_önce + tol ve N3bg_c(m >= Mc_önce) >= 50
      ref dolu:   Mc_c,ref <= Mc_önce + tol ve N_ref,bg,c(m >= Mc_önce) >= 100
    ComCat'te kontrol penceresi hedefle aynı biçimde (R_ind, 10 y, M >= 1,0, Mc 5 y ve [t_c-10, t_c-5) kuralı).
  * Bütün pencereler t'ye hizalı yıllık parçalardır: parça j = [t-(j+1)y, t-jy). Hedef referansı j = 3..9,
    kontrol k önce-penceresi j = 6k..6k+2, kontrol referansı j = 6k+3..6k+9.

KÖRLÜK (kod uygular): bütün sorgular ana şok zamanından ÖNCE biter ve <= 2025-12-31 (getir assert eder);
2026+ satır sayılmaz. Gerçek katalogda yerelleşme ölçüsü (V(q), Gini, z) HESAPLANMAZ; yalnız sayı, Mc, GK74 sayısı.

Kullanım (python3 -I -B):
  tr13_tamsayim.py indir <ham> <sayim4.json> <yeni_ham> [evre...]    evre: ref kontrol_ref kontrol_diger
  tr13_tamsayim.py say   <ham> <sayim4.json> <yeni_ham> <cikti.json>
"""
import calendar
import json
import os
import sys
import threading
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

sys.dont_write_bytecode = True
BURA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURA)
import tr13_sayim as T  # noqa: E402

import numpy as np  # noqa: E402

YIL = T.YIL_MS
ESIK = 50
TOLLAR = (0.1, 0.3)
LIMIT = 20000
T1975 = calendar.timegm((1975, 1, 1, 0, 0, 0)) * 1000
REF_J = range(3, 10)


def hedefler(sayim):
    S = json.load(open(sayim))["satir"]
    return [z for z in S if z["M"] >= 6.0 and (z["N3bg_en_iyi"]["mc"] or 0) >= ESIK and not z["oncu_M6_kirli"]]


def servis_of(z):
    return "ComCat" if z["en_iyi"] == "ComCat" else z["en_iyi"].replace("_tam3", "")


def kontrol_k(z, H):
    """Tanım aynen (tr13_sayim.say): uygun k listesi."""
    Ht, Hla, Hlo = H
    yakin = Ht[T.uzak(z["enlem"], z["boylam"], Hla, Hlo) <= z["R"]]
    ks = []
    for k in range(1, 8):
        tc = z["t"] - 6 * k * YIL
        if tc - T.ONCE_YIL * YIL < T1975:
            break
        if not np.any((yakin >= tc - T.PRE_YIL * YIL) & (yakin <= tc + 3 * YIL)):
            ks.append(k)
    return ks


def havuz(ham):
    H = T.havuz_oku(ham)
    return (np.array([h[0] for h in H], float), np.array([h[1] for h in H]), np.array([h[2] for h in H]))


def mmin_of(z):
    return 1.0 if servis_of(z) == "ComCat" else max(-1.0, round(z["mc_en_iyi"] - 0.3, 1))


def _daire(srv, z, t0, t1, mmin, onb, derin=0):
    """[t0, t1) R dairesi (ComCat'te R_ind); satır sayısı limite ulaşırsa zaman ikiye bölünür."""
    assert t1 <= z["t"] and t1 <= T.BITIS_MS + 1000, "KÖRLÜK"
    if srv == "ComCat":
        q = dict(format="csv", latitude=f"{z['enlem']:.4f}", longitude=f"{z['boylam']:.4f}",
                 maxradiuskm=f"{z['R_ind']:.1f}", starttime=T.iso(t0), endtime=T.iso(t1 - 1000),
                 minmagnitude=f"{mmin:.1f}", eventtype="earthquake", orderby="time-asc", limit=LIMIT)
        metin = T.getir(T.SERVIS[srv] + "?" + urllib.parse.urlencode(q), onb)
        n_satir = max(0, len([s for s in metin.splitlines() if s.strip()]) - 1)
        d = T.comcat_csv(metin)
    else:
        q = dict(format="text", latitude=f"{z['enlem']:.4f}", longitude=f"{z['boylam']:.4f}",
                 maxradius=f"{z['R'] / 111.195:.4f}", starttime=T.iso(t0), endtime=T.iso(t1 - 1000),
                 minmagnitude=f"{mmin:.1f}")
        if srv != "GeoNet":
            q["limit"] = LIMIT
        metin = T.getir(T.SERVIS[srv] + "?" + urllib.parse.urlencode(q), onb, zaman_asimi=900)
        n_satir = len([s for s in metin.splitlines() if s.strip() and not s.startswith("#")])
        d = T.fdsn_text(metin)
    if n_satir >= LIMIT:
        assert derin < 8, "bölme sınırı"
        orta = (t0 + t1) // 2
        return T.birlestir([_daire(srv, z, t0, orta, mmin, onb, derin + 1),
                            _daire(srv, z, orta, t1, mmin, onb, derin + 1)])
    return d


def parca(yh, z, j, indir=True):
    srv = servis_of(z)
    fn = os.path.join(yh, f"parca_{srv}_{z['id']}_{j:02d}.npz")
    if os.path.exists(fn):
        return dict(np.load(fn))
    if not indir:
        return None
    t1 = int(z["t"] - j * YIL)
    t0 = int(z["t"] - (j + 1) * YIL)
    assert t0 >= T1975 - YIL, "1975 öncesi parça istenmez"
    d = _daire(srv, z, t0, t1, mmin_of(z), os.path.join(yh, "onbellek_" + srv + "_tam"))
    tmp = f"{fn}.{os.getpid()}_{threading.get_ident()}.tmp.npz"   # aynı parçayı iki iş parçacığı isteyebilir
    np.savez_compressed(tmp, **d)
    os.replace(tmp, fn)
    print(srv, z["id"], z["zaman"][:10], "j", j, len(d["t"]), flush=True)
    return d


def parcalar(yh, z, js, indir=True):
    ds = []
    for j in js:
        d = parca(yh, z, j, indir)
        if d is None:
            return None
        ds.append(d)
    return T.birlestir(ds)


# ------------------------------------------------------------------ ölçüler (yalnız sayı, Mc, GK74 sayısı)
def mc_kural(m):
    if m.size >= 50:
        return round(T.maxc(m) + 0.2, 2)
    if m.size >= 20:
        return round(T.maxc(m) + 0.3, 2)
    return None


def pencere_olc(z, d, t0, t1):
    """R dairesi, derinlik <= 40 km, [t0, t1); GK74 bu pencerenin indirilen verisinde (R dairesi)."""
    mc0 = z["mc_en_iyi"]
    sec = (d["t"] >= t0) & (d["t"] < t1)
    dd = {k: v[sec] for k, v in d.items()}
    r = T.uzak(z["enlem"], z["boylam"], dd["la"], dd["lo"])
    ic = (r <= z["R"]) & (dd["de"] <= T.DERIN_MAX + 10)
    m = dd["m"][ic]
    mc = mc_kural(m)
    bg = T.gk74(dd["t"], dd["la"], dd["lo"], dd["m"])
    ust = dd["m"] >= mc0 - 1e-6
    kesik = bool(m.size and abs(T.maxc(m) - round(float(m.min()), 1)) < 1e-6)
    return dict(n=int(m.size), mc=mc, Nbg_mc_once=int((ic & ust & bg).sum()), N_mc_once=int((ic & ust).sum()),
                maxc_alt_sinirda=kesik)


def ref_tam(yh, z, indir=False):
    srv = servis_of(z)
    if srv == "ComCat":
        r = z.get("ref") or {}
        return dict(tur="ComCat tam (sayim4, değişmedi)", mc=r.get("mc_ref"), Nbg_mc_once=r.get("Nrefbg_mc"))
    d = parcalar(yh, z, REF_J, indir)
    if d is None:
        return None
    o = pencere_olc(z, d, z["t"] - 10 * YIL, z["t"] - 3 * YIL)
    o["tur"] = f"{srv} tam [t-10y, t-3y), R"
    # duyarlılık (kural değil): Mc_ref ComCat'teki gibi yalnız [t-10y, t-5y)'den
    sec = (d["t"] < z["t"] - 5 * YIL)
    rr = T.uzak(z["enlem"], z["boylam"], d["la"][sec], d["lo"][sec])
    o["mc_eski5_duyarlilik"] = mc_kural(d["m"][sec][(rr <= z["R"]) & (d["de"][sec] <= T.DERIN_MAX + 10)])
    return o


def ref_gecer(z, r, tol, n_ref=2 * ESIK):
    if not r or r.get("mc") is None or z["mc_en_iyi"] is None:
        return False
    return r["mc"] <= z["mc_en_iyi"] + tol and (r.get("Nbg_mc_once") or 0) >= n_ref


def kontrol_olc(yh, z, k, indir=False, ref_de=True):
    """Kontrol penceresi k: önce [t_c-3y, t_c), referans [t_c-10y, t_c-3y)."""
    srv = servis_of(z)
    tc = z["t"] - 6 * k * YIL
    mc0 = z["mc_en_iyi"]
    if srv == "ComCat":
        d = parcalar(yh, z, range(6 * k, 6 * k + 10), indir)
        if d is None:
            return None
        oc = dict(z, t=tc)
        c = T.olc(oc, d)   # tr13_sayim.olc: Mc 5 y (R), mc_eski5 = [t_c-10y, t_c-5y)
        r = T.uzak(z["enlem"], z["boylam"], d["la"], d["lo"])
        ic = (r <= z["R"]) & (d["de"] <= T.DERIN_MAX + 10)
        bg = T.gk74(d["t"], d["la"], d["lo"], d["m"])   # 10 y, R_ind (ComCat kuralı)
        ust = d["m"] >= mc0 - 1e-6
        w3 = (d["t"] >= tc - 3 * YIL) & (d["t"] < tc)
        w10 = d["t"] < tc - 3 * YIL
        return dict(k=k, t_c=T.iso(tc)[:10],
                    once=dict(mc=c.get("mc"), Nbg_mc_once=int((ic & w3 & ust & bg).sum())),
                    ref=dict(mc=c.get("mc_eski5"), Nbg_mc_once=int((ic & w10 & ust & bg).sum())))
    d = parcalar(yh, z, range(6 * k, 6 * k + 3), indir)
    if d is None:
        return None
    once = pencere_olc(z, d, tc - 3 * YIL, tc)
    out = dict(k=k, t_c=T.iso(tc)[:10], once=once, ref=None)
    if not ref_de or not (once["mc"] is not None and once["mc"] <= mc0 + max(TOLLAR)
                          and once["Nbg_mc_once"] >= ESIK):
        out["ref_indirilmedi"] = "önce-penceresi tol 0,3'te dolu değil" if ref_de else "evre dışı"
        return out
    d2 = parcalar(yh, z, range(6 * k + 3, 6 * k + 10), indir)
    if d2 is None:
        return out
    out["ref"] = pencere_olc(z, d2, tc - 10 * YIL, tc - 3 * YIL)
    return out


def kontrol_dolu(z, c, tol, ref_sart=True):
    if not c:
        return False
    o = c["once"]
    ok = o.get("mc") is not None and o["mc"] <= z["mc_en_iyi"] + tol and (o.get("Nbg_mc_once") or 0) >= ESIK
    if ref_sart:
        ok = ok and ref_gecer(z, c.get("ref"), tol)
    return ok


# ------------------------------------------------------------------ indirme evreleri
def indir(ham, sayim, yh, evreler):
    os.makedirs(yh, exist_ok=True)
    Z = hedefler(sayim)
    H = havuz(ham)
    print("hedef olay", len(Z), "küme", len({z["kume"] for z in Z}), flush=True)

    def guvenli(f, *a):
        try:
            return f(*a)
        except Exception as e:  # noqa  (hata yazılır; önbellek sayesinde yeniden koşulur)
            print("HATA", a[1]["id"] if len(a) > 1 else "", type(e).__name__, e, flush=True)
            return None

    if "ref" in evreler:
        hed = [z for z in Z if servis_of(z) != "ComCat"]
        print("evre ref", len(hed), flush=True)
        with ThreadPoolExecutor(3) as ex:
            list(ex.map(lambda z: guvenli(ref_tam, yh, z, True), hed))
    if "kontrol_ref" in evreler or "kontrol_diger" in evreler:
        ref_ok = {z["id"]: ref_gecer(z, ref_tam(yh, z), max(TOLLAR)) for z in Z}
        isler = []
        for z in Z:
            if ("kontrol_ref" in evreler and ref_ok[z["id"]]) or ("kontrol_diger" in evreler and not ref_ok[z["id"]]):
                isler += [(z, k) for k in kontrol_k(z, H)]
        print("evre kontrol", evreler, "pencere", len(isler), flush=True)
        # ComCat hızlı, ötekiler yavaş: önce ComCat dışı (3 iş parçacığı)
        with ThreadPoolExecutor(3) as ex:
            list(ex.map(lambda zk: guvenli(kontrol_olc, yh, zk[0], zk[1], True), isler))
    print("bitti", evreler, flush=True)


# ------------------------------------------------------------------ sayım
def bolge(z):
    la, lo, y = z["enlem"], z["boylam"], z["yer"]
    if 30 <= la <= 42 and -126 <= lo <= -114 or "California" in y or "B.C." in y:
        return "Kaliforniya"
    if "Alaska" in y:
        return "Alaska"
    if "Idaho" in y:
        return "ABD iç"
    if "Japan" in y or (24 <= la <= 36 and 122 <= lo <= 136 and "Taiwan" not in y):
        return "Japonya"
    if "Taiwan" in y:
        return "Tayvan"
    if "New Zea" in y:
        return "Yeni Zelanda"
    if "Greece" in y or "Gre" in y:
        return "Yunanistan"
    if "Turkey" in y or (36 <= la <= 42 and 26 <= lo <= 45):
        return "Türkiye"
    if "China" in y:
        return "Çin"
    if "Tajik" in y:
        return "Tacikistan"
    if "Jamaica" in y or "Cuba" in y or "Bartolom" in y:
        return "Karayip"
    if "Colombia" in y:
        return "Kolombiya"
    if "Svalbard" in y or "Olonkinbyen" in y:
        return "Jan Mayen/Svalbard"
    return y


def say(ham, sayim, yh, cikti):
    Z = hedefler(sayim)
    H = havuz(ham)
    satir = []
    eksik = []
    for z in Z:
        r = ref_tam(yh, z)
        if r is None:
            eksik.append(("ref", z["id"]))
        ks = kontrol_k(z, H)
        kon = []
        for k in ks:
            c = kontrol_olc(yh, z, k)
            if c is None:
                eksik.append((f"kontrol k={k}", z["id"]))
            kon.append(c if c else dict(k=k, indirilmedi=True))
        assert len(ks) == z["kontrol_pencere_havuz"], (z["id"], ks, z["kontrol_pencere_havuz"])
        ro = z.get("ref") or {}
        satir.append(dict(
            id=z["id"], zaman=z["zaman"][:10], M=z["M"], yer=z["yer"], bolge=bolge(z), kume=z["kume"],
            R_km=z["R"], katalog=servis_of(z), mc_once=z["mc_en_iyi"], N3bg_mc=z["N3bg_en_iyi"]["mc"],
            ref_ilk=dict(tur=ro.get("tur"), mc=ro.get("mc_ref"), Nbg=ro.get("Nrefbg_mc")), ref_tam=r,
            ref_gecer={str(t): ref_gecer(z, r, t) for t in TOLLAR}, kontrol_havuz_k=ks, kontrol=kon,
            kontrol_dolu_once={str(t): [c["k"] for c in kon if not c.get("indirilmedi") and
                                        kontrol_dolu(z, c, t, False)] for t in TOLLAR},
            kontrol_dolu={str(t): [c["k"] for c in kon if not c.get("indirilmedi") and kontrol_dolu(z, c, t)]
                          for t in TOLLAR}))
    tablo = {}
    for Mmin in (6.5, 6.0):
        A = [s for s in satir if s["M"] >= Mmin]

        def K(sec):
            return len({s["kume"] for s in sec})
        row = dict(temiz=K(A), temiz_kontrol_havuz=K([s for s in A if s["kontrol_havuz_k"]]))
        for t in TOLLAR:
            ts = str(t)
            ref = [s for s in A if s["ref_gecer"][ts]]
            row[f"temiz_ref_tol{t}"] = K(ref)
            row[f"duyarlilik_temiz_ref_mc_eski5_tol{t}"] = K([s for s in A if ref_gecer(
                dict(mc_en_iyi=s["mc_once"]), dict(s["ref_tam"], mc=s["ref_tam"].get("mc_eski5_duyarlilik",
                                                                                     s["ref_tam"]["mc"])), t)])
            row[f"temiz_kontrol_once_dolu_tol{t}"] = K([s for s in A if s["kontrol_dolu_once"][ts]])
            row[f"temiz_kontrol_dolu_tol{t}"] = K([s for s in A if s["kontrol_dolu"][ts]])
            row[f"temiz_ref_kontrol_havuz_tol{t}"] = K([s for s in ref if s["kontrol_havuz_k"]])
            row[f"temiz_ref_kontrol_once_dolu_tol{t}"] = K([s for s in ref if s["kontrol_dolu_once"][ts]])
            row[f"temiz_ref_kontrol_dolu_tol{t}"] = K([s for s in ref if s["kontrol_dolu"][ts]])
        tablo[f"M>={Mmin}"] = row
    kumeler = {}
    for s in satir:
        k = kumeler.setdefault(s["kume"], dict(kume=s["kume"], bolge=s["bolge"], olaylar=[]))
        k["olaylar"].append(s["id"])
    out = dict(tarih="2026-11-12", kurallar=__doc__, esik_N3bg=ESIK, hedef_olay=len(satir),
               hedef_kume=len(kumeler), eksik=eksik, tablo=tablo, kumeler=list(kumeler.values()), satir=satir)
    json.dump(out, open(cikti, "w"), indent=1, ensure_ascii=False, default=float)
    print(json.dumps(tablo, indent=1))
    print("eksik", len(eksik), eksik[:20])


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "indir":
        indir(a[1], a[2], a[3], a[4:] or ["ref", "kontrol_ref", "kontrol_diger"])
    elif a and a[0] == "say":
        say(a[1], a[2], a[3], a[4])
    else:
        print(__doc__)
