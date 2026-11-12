# TR-10b ön kayıt sürüm 2: İNCELEME-1 Ö6 (TR-10 olay öncesi pencereleriyle örtüşme) ve K5 (≤ 3 km yer kümeleri)
# sayılarının yeniden üretimi. Yalnız üstveri: SAYIM'ın ComCat önbelleği ve indirme sayfası koordinatları
# (inc1_listeler.py çıktısı üzerinden). Hiçbir veri dosyası okunmaz.
#
# TR-10 (TR-10_SAYIM §1.2–1.3): olay M ≥ 5,5 (varyant; ana M ≥ 6), derinlik ≤ 30 km, ölçere ≤ 50 km;
# olay öncesi pencere: v_önce 12 ay + v_taban 48 ay, olaydan 30 gün önce kapanır → [E − 30 g − 60 ay, E − 30 g].
#
# Kullanım (depo kökünden):
#   python3 -I -B kayit/turetme/tr10b/onkayit_yardimci/inc1_tr10_ortusme.py <ham_dizin> <inc1 listeler.json>
import datetime as dt
import json
import os
import sys

BURA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(BURA))
import tr10b_sayim as KS  # noqa: E402
T2 = KS.T2

ham, lj = sys.argv[1:3]
d = json.load(open(lj, encoding="utf-8"))["sonuc"]
ist = d["INC1_ist"]
E, sha = KS.olaylar(ham)
print("ComCat sha256", sha, "olay", len(E))


def ay_cikar(t, n):
    y, m = divmod(t.year * 12 + t.month - 1 - n, 12)
    return dt.date(y, m + 1, min(t.day, 28))


for ad in ("B_U", "A_U"):
    print(f"\n{ad}: TR-10 olay öncesi pencereleriyle örtüşen okuma aralıkları")
    n = 0
    for kod, Y, *_ in d["INC1_listeler"][ad]:
        P = KS.pencere(Y)
        s = ist[kod]
        for e in E:
            if e["m"] < 5.5 or e["z"] > 30:
                continue
            son = e["t"] - dt.timedelta(days=30)
            bas = ay_cikar(son, 60)
            a, b = max(bas, P["ilk"]), min(son, P["son"])
            if a > b:
                continue
            km = T2.mesafe_az(s["lat"], s["lon"], e["lat"], e["lon"])[0]
            if km <= 50:
                n += 1
                print(f"  {kod} {Y}: {e['t']} M{e['m']} {e['yer']} {km:.1f} km; TR-10 penceresi {bas} → {son}; "
                      f"örtüşme {a} → {b} ({(b - a).days + 1} g ≈ {((b - a).days + 1) / 30.44:.1f} ay)")
    print("  toplam:", n)

# K5: birbirine ≤ 3 km olan yerler ve tek bağlantılı kümeler (veri öncesi; B_U ve A_U yerleri)
for ad in ("B_U", "A_U"):
    yerler = {}
    for kod, Y, tur, kes, site in d["INC1_listeler"][ad]:
        yerler.setdefault(site, set()).add(kod)
    S = sorted(yerler)
    xy = {s_: tuple(map(float, s_.split(","))) for s_ in S}
    ata = {s_: s_ for s_ in S}

    def kok(x):
        while ata[x] != x:
            x = ata[x]
        return x
    ciftler = []
    for i, a in enumerate(S):
        for b in S[i + 1:]:
            km = T2.mesafe_az(*xy[a], *xy[b])[0]
            if km <= 3.0:
                ciftler.append((sorted(yerler[a]), sorted(yerler[b]), round(km, 2)))
                ata[kok(a)] = kok(b)
    print(f"\n{ad}: yer {len(S)}; ≤ 3 km çiftleri {len(ciftler)}; tek bağlantılı küme {len({kok(s_) for s_ in S})}")
    for c in ciftler:
        print("  ", c)
