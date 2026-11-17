#!/usr/bin/env python3
"""TR-13c MDE: yeni listenin (TR-13c sayımında geçen yeni-küme üyeleri) R0 tek liste kuralı için güç eğrisi,
yanlış alarm ve MDE. YALNIZ YAPAY ETAS. Gerçek katalog okunmaz; tek gerçek girdi tr13c_sayim.json'daki (R, N3bg)
sayıları ve TR-13b koşusunun hazırlık sayıları (kosu/durum.json).

Kural: kayit/onkayit/TR-13c_SAYIM-KURALI.md §5. Düzen tr13b_inc2.py'ninkidir (kendi R'de kalibrasyon, üç dallanmalı
sıfır, ayrı kalibre edilmiş dallanma 0,6 verisi, küme yapılı çekiliş); bölge üreteci, kalibrasyon ve süzgeç dondurulmuş
koşu betiğinin kod incelemesi sonrası işlevleri (tr13b_kosu.yapay_bolge B_ref 200, kalibre 40 + 40, sonlu_z).
R0 tek liste: üç dallanmanın üçünde de p <= 0,05 (yeni listede keşif olayı yok).

Bilgi (birleşik liste): TR-13b koşusunun 15 üyesi + yeni üyeler; TR-13b üyelerinin sıfır ve veri havuzları koşunun
kendi yapay havuzlarıdır (kosu/havuz/*.npy; sıfır 2000, veri sinyalsiz 200 ve f 0,2…0,6 için 150). f = 0,1 orada yok.

Kullanım: python3 -I -B tr13c_mde.py <ara_dizin> <cikti.json> [cekirdek=2]
"""
import itertools
import json
import multiprocessing as mp
import os
import sys
import time

import numpy as np

sys.dont_write_bytecode = True
BURA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BURA, "..", "tr13b"))
sys.path.insert(0, os.path.join(BURA, "..", "tr13"))
import tr13b_kosu as K  # noqa: E402

TOHUM = 20261117
DAL = K.DALLANMA
F_LIST = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6)
N0, ND, NF = 400, 300, 150          # sıfır (dallanma başına), veri sinyalsiz, veri f başına
NS, NB = 200000, 20000
KOSU = os.path.join(BURA, "..", "tr13b", "kosu")


def havuz_kos(ara, isler, havuz_ici):
    """isler: [(ad, tohum, R, Nh, dal, f, n, parca)] -> ad -> dizi. Parçalar diske yazılır (sürdürülebilir)."""
    gen = []
    for ad, tohum, R, Nh, dal, f, n, parca in isler:
        for p, k in enumerate(K.parca_boylari(n, parca)):
            if not os.path.exists(os.path.join(ara, f"{ad}_p{p}.npy")):
                gen.append((ad, tohum, p, R, Nh, dal, f, k, K.B_REF))
    for ad, p, arr in havuz_ici.imap_unordered(K._is_havuz, gen, chunksize=1):
        yol = os.path.join(ara, f"{ad}_p{p}.npy")
        np.save(yol + ".tmp.npy", arr)
        os.replace(yol + ".tmp.npy", yol)
    return {ad: np.concatenate([np.load(os.path.join(ara, f"{ad}_p{p}.npy")) for p in range(parca)])
            for ad, tohum, R, Nh, dal, f, n, parca in isler}


def guc(kumeler, sifir, veri, senaryolar, tohum):
    """sifir: d -> {üye: havuz}; veri: senaryo -> {üye: havuz}. Dönüş: senaryo -> R0 red oranı."""
    S = {}
    for di, d in enumerate(DAL):
        z = K.sifir_cekilis(np.random.default_rng(tohum + di), sifir[d], kumeler, NS)[..., 0].mean(1)
        S[d] = np.sort(z)
    out = {}
    rr = np.random.default_rng(tohum + 50)
    for s in senaryolar:
        v = K.sifir_cekilis(rr, veri[s], kumeler, NB)[..., 0].mean(1)
        red = np.ones(NB, bool)
        for d in DAL:
            red &= K.p_vektor(S[d], v) <= K.ALFA
        out[s] = float(red.mean())
    return out


def egri(g, fl):
    fs = [0.0] + list(fl)
    gs = [g["D0"]] + [g[f"f{f}"] for f in fl]
    return K.mde(fs, gs)


def main(ara, cikti, cekirdek):
    t0 = time.time()
    os.makedirs(ara, exist_ok=True)
    Y = json.load(open(os.path.join(BURA, "tr13c_sayim.json")))
    L = [z for z in Y["satir"] if z["durum"] == "tamam" and z["yeni_kume"]]
    print("yeni üye", [(z["id"], z["R"], z["N3bg"]) for z in L], flush=True)
    with mp.get_context("fork").Pool(cekirdek) as hv:
        # kalibrasyon: üç sıfır dallanması + veri (0,6, ayrı)
        isler, adlar = [], []
        for j, z in enumerate(L):
            for di, d in enumerate(DAL):
                isler.append((TOHUM + 1000 * j + di, z["R"], z["N3bg"], d, K.KAL_DENEME)); adlar.append((j, d))
            isler.append((TOHUM + 1000 * j + 9, z["R"], z["N3bg"], 0.6, K.KAL_DENEME)); adlar.append((j, "veri"))
        kp = os.path.join(ara, "kal.json")
        if os.path.exists(kp):
            KAL = {tuple(k.split("|")): v for k, v in json.load(open(kp)).items()}
            KAL = {(int(a), b if b == "veri" else float(b)): v for (a, b), v in KAL.items()}
        else:
            KAL = dict(zip(adlar, hv.map(K._is_kal, isler, chunksize=1)))
            json.dump({f"{a}|{b}": v for (a, b), v in KAL.items()}, open(kp, "w"))
        print("kalibrasyon", round(time.time() - t0), "s", flush=True)
        isler = []
        for j, z in enumerate(L):
            for di, d in enumerate(DAL):
                isler.append((f"s{j}_{di}", TOHUM + 1000 * j + 100 + di, z["R"], KAL[(j, d)]["Nh"], d, 0.0, N0, 4))
            isler.append((f"v{j}_D0", TOHUM + 1000 * j + 200, z["R"], KAL[(j, "veri")]["Nh"], 0.6, 0.0, ND, 3))
            for k, f in enumerate(F_LIST):
                isler.append((f"v{j}_f{f}", TOHUM + 1000 * j + 300 + k, z["R"], KAL[(j, "veri")]["Nh"], 0.6, f, NF, 2))
        H = havuz_kos(ara, isler, hv)
    print("havuzlar", round(time.time() - t0), "s", flush=True)
    sifir = {d: {j: K.sonlu_z(H[f"s{j}_{di}"]) for j in range(len(L))} for di, d in enumerate(DAL)}
    sen = ["D0"] + [f"f{f}" for f in F_LIST]
    veri = {s: {j: K.sonlu_z(H[f"v{j}_{s}"]) for j in range(len(L))} for s in sen}
    nit = {L[j]["id"]: dict(R=L[j]["R"], N3bg=L[j]["N3bg"],
                            sifir_ort_N={str(d): round(float(H[f"s{j}_{di}"][:, 2].mean()), 1) for di, d in enumerate(DAL)},
                            veri_ort_N=round(float(H[f"v{j}_D0"][:, 2].mean()), 1),
                            sifir_kalan={str(d): int(len(sifir[d][j])) for d in DAL})
           for j in range(len(L))}
    # ---- (a) yeni liste: her üye kendi kümesi mi? küme yapısı tr13c_sayim'den
    kids = sorted({z["kume"] for z in L})
    kum = [[j for j, z in enumerate(L) if z["kume"] == k] for k in kids]
    Ka = len(kum)
    ga = guc(kum, sifir, veri, sen, TOHUM + 7)
    # ---- (b) yoğun ağ alt listesi
    kb_ids = sorted({z["kume"] for z in L if z["yogun"]})
    kumb = [[j for j, z in enumerate(L) if z["kume"] == k and z["yogun"]] for k in kb_ids]
    gb = ga if kumb == kum else guc(kumb, sifir, veri, sen, TOHUM + 17)
    # ---- duyarlılık: K x 2 ve K x 0,5
    g2 = guc(kum + kum, sifir, veri, sen, TOHUM + 27)
    yar = max(1, Ka // 2)
    alt = list(itertools.combinations(range(Ka), yar))
    gl = [guc([kum[c] for c in a], sifir, veri, sen, TOHUM + 37 + 10 * i) for i, a in enumerate(alt)]
    gh = {s: float(np.mean([g[s] for g in gl])) for s in sen}
    out = dict(tohum=TOHUM, N0=N0, ND=ND, NF=NF, NS=NS, NB=NB, b_ref=K.B_REF, kal_deneme=K.KAL_DENEME,
               uyeler=[dict(id=z["id"], yer=z["yer"], kume=z["kume"], R=z["R"], N3bg=z["N3bg"], yogun=z["yogun"])
                       for z in L],
               havuz_nitelik=nit,
               a=dict(K=Ka, guc=ga, yanlis_alarm=ga["D0"], MDE=egri(ga, F_LIST)),
               b=dict(K=len(kumb), ayni_liste=kumb == kum, guc=gb, yanlis_alarm=gb["D0"], MDE=egri(gb, F_LIST)),
               duyarlilik=dict(K_x2=dict(K=2 * Ka, guc=g2, MDE=egri(g2, F_LIST)),
                               K_x05=dict(K=yar, alt_kume_sayisi=len(alt), guc_ort=gh, MDE=egri(gh, F_LIST))))
    print(json.dumps(out["a"], ensure_ascii=False), json.dumps(out["duyarlilik"], ensure_ascii=False), flush=True)
    # ---- bilgi: birleşik liste (TR-13b koşu üyeleri + yeni)
    try:
        D = json.load(open(os.path.join(KOSU, "durum.json")))
        B = [o for o in D["hazirlik"]["olay"] if o["durum"] == "tamam"]
        hz = os.path.join(KOSU, "havuz")

        def yukle(ad):
            ps = sorted(p for p in range(K.PARCA + 1) if os.path.exists(os.path.join(hz, f"{ad}_p{p}.npy")))
            return np.concatenate([np.load(os.path.join(hz, f"{ad}_p{p}.npy")) for p in ps])

        sifB, verB = {d: {} for d in DAL}, {s: {} for s in ["D0"] + [f"f{f}" for f in K.D3_FLIST]}
        for o in B:
            i = o["sira"]
            for di, d in enumerate(DAL):
                den = 1 if os.path.exists(os.path.join(hz, f"s{i:02d}_{di}_1_p0.npy")) else 0
                sifB[d][("b", i)] = K.sonlu_z(yukle(f"s{i:02d}_{di}_{den}"))
            verB["D0"][("b", i)] = K.sonlu_z(yukle(f"v{i:02d}_0"))
            for k, f in enumerate(K.D3_FLIST):
                verB[f"f{f}"][("b", i)] = K.sonlu_z(yukle(f"v{i:02d}_{k + 1}"))
        for j in range(len(L)):
            for d in DAL:
                sifB[d][("y", j)] = sifir[d][j]
            for s in verB:
                verB[s][("y", j)] = veri[s][j]
        kb = sorted({o["kume"] for o in B})
        kumB = [[("b", o["sira"]) for o in B if o["kume"] == k] for k in kb] + [[("y", j) for j in k] for k in kum]

        def cek(rng, hav, kumeler, nb):
            # sifir_cekilis anahtarları liste indeksiyle kullanır; burada sözlük anahtarlarıyla aynısı
            o = np.zeros((nb, len(kumeler)))
            for c, k in enumerate(kumeler):
                for u in k:
                    h = hav[u]
                    o[:, c] += h[rng.integers(0, len(h), nb), 0]
                o[:, c] /= len(k)
            return o.mean(1)

        S = {d: np.sort(cek(np.random.default_rng(TOHUM + 70 + di), sifB[d], kumB, NS)) for di, d in enumerate(DAL)}
        rr = np.random.default_rng(TOHUM + 80)
        gB = {}
        for s in verB:
            v = cek(rr, verB[s], kumB, NB)
            red = np.ones(NB, bool)
            for d in DAL:
                red &= K.p_vektor(S[d], v) <= K.ALFA
            gB[s] = float(red.mean())
        out["bilgi_birlesik"] = dict(K=len(kumB), uye=len(B) + len(L), guc=gB, yanlis_alarm=gB["D0"],
                                     MDE=egri(gB, K.D3_FLIST),
                                     not_="TR-13b z'leri görüldü; hükme giremez. R0 tek liste. f 0,1 havuzu yok.")
        print("birleşik", json.dumps(out["bilgi_birlesik"], ensure_ascii=False), flush=True)
    except (OSError, KeyError, ValueError) as e:
        out["bilgi_birlesik"] = dict(hata=f"{type(e).__name__}: {e}")
    out["sure_s"] = round(time.time() - t0)
    json.dump(out, open(cikti, "w"), indent=1, ensure_ascii=False, default=float)
    print("bitti", out["sure_s"], "s")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 2)
