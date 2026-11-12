"""TR-6a ön kayıt sürüm 2, K3: "0 büyüklük" kuralının Ek 1 önbelleğinde (yalnız olay öncesi, B3 maskeli) doğrulanması.

Bütün önbellek okumaları tr6a_onbellek_kor.oku_sorgu üzerinden yapılır (B3 maskesi). Çıktı yalnız maskeden geçen
satırların özetidir. Her katalog için: satır sayısı, büyüklük türü boş satırlar, büyüklüğü boş satırlar, büyüklüğü
<= 0,05 olan satırlar (türü boş / dolu), türü boş ama büyüklüğü > 0,05 olan satırlar; "0" satırı taşıyan sorgu
sahipleri; Ek 1 Mc kuralı (3 örnek pencere, halka, <= 40 km, >= 50 olay: max MAXC + 0,2) iki süzgeçle yeniden:
(a) Ek 1'deki gibi (süzgeçsiz), (b) önerilen dar kural (türü boş VE büyüklüğü <= 0,05 olan satır atılır).
Kullanım: python3 -I -B tr6a_sifir_buyukluk.py   -> tr6a_sifir_buyukluk.json
"""
# Sürüm 3 (İNCELEME-2 K8): önbellek dizini argümanla ya da TR6A_ONBELLEK ile verilir ve tr6a_onbellek_kor.arsivden_ac
# ile ham arşivden açılmış olmalıdır:  python3 -I -B tr6a_sifir_buyukluk.py <onbellek_dizini>
# (Docstring JSON'a "aciklama" olarak yazıldığı için sürüm 2 metni değiştirilmedi; çıktı bayt bayt aynı kalır.)
import datetime as dt, json, math, os, sys, urllib.parse
from collections import Counter, defaultdict
import numpy as np

BURAYA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURAYA)
import tr6a_onbellek_kor as KOR  # noqa: E402
import tr6_a_kapi as KAPI        # noqa: E402  (maxc, uzaklik_km; ağ kodu çağrılmaz)

SIFIR = 0.05


def main(onb=None):
    onb = KOR.onbellek_dizini(onb)
    sorgular = KOR.sorgu_listesi(onb)
    hav = {o["id"]: o for o in KOR.havuz()}
    ozet = defaultdict(Counter)
    sifir_sahip = defaultdict(Counter)
    ornekler = defaultdict(list)            # (sahip, katalog) -> Mc örnek pencereleri (minmagnitude'suz sorgular)
    sahipsiz = 0
    for s in sorgular:
        if s["sahip"] is None:
            sahipsiz += 1
            continue
        d = KOR.oku_sorgu(s, onb)
        m = d["m"]
        bos_tur = np.array([x == "" for x in d["mtip"]], bool)
        bos_m = np.isnan(m)
        sif = (~bos_m) & (m <= SIFIR)
        c = ozet[s["katalog"]]
        c["sorgu"] += 1
        c["satir"] += len(m)
        c["tur_bos"] += int(bos_tur.sum())
        c["buyukluk_bos"] += int(bos_m.sum())
        c["tur_bos_ve_buyukluk_bos"] += int((bos_tur & bos_m).sum())
        c["sifir_tur_bos"] += int((sif & bos_tur).sum())
        c["sifir_tur_dolu"] += int((sif & ~bos_tur).sum())
        c["tur_bos_buyukluk_pozitif"] += int((bos_tur & ~bos_m & (m > SIFIR)).sum())
        c["negatif_buyukluk"] += int(((~bos_m) & (m < 0)).sum())
        if (sif & bos_tur).any():
            sifir_sahip[s["katalog"]][s["sahip"]] += int((sif & bos_tur).sum())
        q = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(s["url"]).query))
        if s["katalog"] != "KOERI" and "minmagnitude" not in q:
            ornekler[(s["sahip"], s["katalog"])].append(d)

    def mc_kural(parcalar, o, dar):
        mcs, hep = [], []
        for d in parcalar:
            ok = ~np.isnan(d["m"])
            if dar:
                ok &= ~(np.array([x == "" for x in d["mtip"]], bool) & (d["m"] <= SIFIR))
            r = KAPI.uzaklik_km(o["enlem"], o["boylam"], d["la"], d["lo"]) if len(d["m"]) else np.zeros(0)
            mk = ok & (r >= o["halka_km"][0]) & (r <= o["halka_km"][1]) & (d["de"] <= KAPI.DERIN_KM)
            hep.append(d["m"][mk])
            if mk.sum() >= 50:
                mcs.append(KAPI.maxc(d["m"][mk]) + 0.2)
        b = np.concatenate(hep) if hep else np.zeros(0)
        if mcs:
            return round(max(mcs), 2), "max(pencere MAXC+0,2)", int(len(b))
        if len(b) >= 50:
            return round(KAPI.maxc(b) + 0.2, 2), "birleşik", int(len(b))
        if len(b) >= 20:
            return round(KAPI.maxc(b) + 0.3, 2), "birleşik (<50)", int(len(b))
        return None, f"yetersiz ({len(b)})", int(len(b))

    yeniden = []
    for kat, sah in sifir_sahip.items():
        for sid in sorted(sah):
            o = hav[sid]
            par = ornekler.get((sid, kat), [])
            a = mc_kural(par, o, False)
            b = mc_kural(par, o, True)
            yeniden.append(dict(sahip=sid, katalog=kat, ek1_mc=o["ek1_kataloglar"].get(kat, {}).get("mc"),
                                ornek_pencere=len(par), mc_suzgecsiz_maskeli=a[0], mc_dar_kural_maskeli=b[0],
                                dar_kural_mc_yontemi=b[1], dar_kural_ornek_olay=b[2]))
    out = dict(aciklama=__doc__, maske=dict(gun=KOR.MASKE_GUN, L_kat=KOR.MASKE_L), sahipsiz_sorgu=sahipsiz,
               katalog_ozeti={k: dict(v) for k, v in sorted(ozet.items())},
               sifir_satiri_olan_sahipler={k: dict(v) for k, v in sifir_sahip.items()},
               mc_yeniden=yeniden)
    with open(os.path.join(BURAYA, "tr6a_sifir_buyukluk.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(json.dumps({k: v for k, v in out.items() if k != "aciklama"}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
