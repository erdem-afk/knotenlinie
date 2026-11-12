"""TR-6 (a) ayağı: bağımsız durum sayımı (yalnız üstveri ve olay sayısı; hiçbir oran değişimi hesaplanmaz).

Havuz: USGS ComCat'te finite-fault ürünü olan, 1990-01-01..2025-12-31, M>=6,0, derinlik <=30 km olaylar
(bağımsız gerilme değişimi = yayımlanmış sonlu fay modelinden Coulomb; kosismik ayak).
Her olay için alıcı halka: episantrdan [L/2 + 10 km, 2L], L = 10**(-3.55 + 0.74 M) km (Wells-Coppersmith 1994,
doğrultu atımlı yüzey kırık boyu; bütün mekanizmalara aynı kaba ölçek). Olaydan önceki 5 yılda bu halkada
ComCat M>=2,5 olay sayısı -> yıllık oran. Gölge lobu payı 0,5 ve arka plan payı 0,5 varsayılır (kaba, beyan):
gölge lobunda yıllık arka plan beklentisi N0 = 0,25 x halka yıllık oranı.
Kapı eşikleri (tr6_sayim.py ile aynı Poisson güç formülü): gölge lobunda Δτ = -10 kPa adımının 1 yılda
%80 güçle (tek yanlı alfa 0,05) görülmesi için gereken N0: Aσ=0,01 MPa -> e^-1 = 0,37 kat düşüş; Aσ=0,05 MPa
-> e^-0,2 = 0,82 kat. Gereken N0 bu betikte hesaplanır.

KÖR KURAL: bütün sorgular 2025-12-31T23:59:59'da biter. Pre-olay pencereleri olaydan öncedir.
Kullanım: python3 -I -B tr6_a_sayim.py <cikti.json> [--yalniz-ozet]
"""
import json, math, sys, time, urllib.request, urllib.parse, datetime as dt

U = "https://earthquake.usgs.gov/fdsnws/event/1/"
SON = "2025-12-31T23:59:59"


def get(path, **q):
    url = U + path + "?" + urllib.parse.urlencode(q)
    for i in range(6):
        try:
            with urllib.request.urlopen(url, timeout=180) as r:
                return r.read().decode()
        except Exception:
            time.sleep(2 ** (i + 1))
    raise SystemExit("ComCat erişilemedi: " + path)


def gereken_n0(oran, za=1.6449, zb=0.8416):
    """N1 = oran*N0 (oran<1). Tek yanlı düşüş sınaması: N0 - N1 >= za*sqrt(N0) + zb*sqrt(N1)."""
    k = (za + zb * math.sqrt(oran)) / (1 - oran)
    return k * k


def kumele(olaylar, km=300.0, gun=1826):
    """Bağımsızlık: 300 km ve 5 yıl içindeki olaylar tek küme (alıcı halkaları ve ön pencereler örtüşür)."""
    def hav(a, b):
        p1, p2 = math.radians(a["enlem"]), math.radians(b["enlem"])
        dl = math.radians(b["boylam"] - a["boylam"])
        return 6371 * math.acos(min(1, math.sin(p1) * math.sin(p2) + math.cos(p1) * math.cos(p2) * math.cos(dl)))
    kl = []
    for e in olaylar:
        t = dt.datetime.fromisoformat(e["zaman"])
        for c in kl:
            if any(hav(e, x) < km and abs((t - dt.datetime.fromisoformat(x["zaman"])).days) < gun for x in c):
                c.append(e)
                break
        else:
            kl.append([e])
    return kl


def ozetle(olaylar):
    esik = {f"Asigma_{a}kPa": gereken_n0(math.exp(-10.0 / a)) for a in (10, 20, 30, 50)}
    ozet = {"havuz": len(olaylar), "golge_N0>=1": sum(1 for o in olaylar if o["golge_N0_yil"] >= 1)}
    for k, v in esik.items():
        sec = [o for o in olaylar if o["golge_N0_yil"] >= v]
        ozet[k] = dict(olay=len(sec), bagimsiz_kume=len(kumele(sec)))
    return esik, ozet


def main():
    out = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[2] == "--yalniz-ozet":   # ComCat'e yeniden gitmeden özetle
        d = json.load(open(out))
        esik, ozet = ozetle(d["olaylar"])
        json.dump(dict(esik_N0=esik, ozet=ozet, olaylar=d["olaylar"]), open(out, "w"), indent=1, ensure_ascii=False)
        print(json.dumps(dict(esik_N0=esik, ozet=ozet), ensure_ascii=False))
        return
    js = json.loads(get("query", format="geojson", starttime="1990-01-01", endtime=SON, minmagnitude=6,
                        maxdepth=30, producttype="finite-fault", orderby="time-asc"))
    olaylar = []
    for f in js["features"]:
        p, g = f["properties"], f["geometry"]["coordinates"]
        t = dt.datetime.fromtimestamp(p["time"] / 1000, dt.timezone.utc).replace(tzinfo=None)
        if t >= dt.datetime(2026, 1, 1):
            continue
        M = p["mag"]
        L = 10 ** (-3.55 + 0.74 * M)
        r1, r2 = L / 2 + 10, 2 * L
        t0 = (t - dt.timedelta(days=1826)).strftime("%Y-%m-%dT%H:%M:%S")
        n = int(get("count", starttime=t0, endtime=t.strftime("%Y-%m-%dT%H:%M:%S"), latitude=g[1],
                    longitude=g[0], minradiuskm=r1, maxradiuskm=r2, minmagnitude=2.5).strip())
        olaylar.append(dict(id=f["id"], zaman=t.isoformat(), M=M, enlem=g[1], boylam=g[0], L_km=round(L, 1),
                            halka_km=[round(r1, 1), round(r2, 1)], on5yil_M25=n, golge_N0_yil=round(0.25 * n / 5, 2)))
        time.sleep(0.2)
    esik, ozet = ozetle(olaylar)
    json.dump(dict(esik_N0=esik, ozet=ozet, olaylar=olaylar), open(out, "w"), indent=1, ensure_ascii=False)
    print(json.dumps(dict(esik_N0=esik, ozet=ozet), ensure_ascii=False))


if __name__ == "__main__":
    main()
