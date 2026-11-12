"""TR-6 (b) katalog indirme: EMSC FDSN olay servisi, Marmara kutusu, 2006-01-01 .. 2025-12-31.

KÖR KURAL: bitiş zamanı sunucu tarafında 2025-12-31T23:59:59 olarak verilir; 2026 olayı istenmez.
İkinci koruma okuma tarafında (tr6_sayim.py) yapılır: zaman >= 2026-01-01 olan satır sayılmadan atılır
ve sayısı yazdırılmaz.

Kullanım: python3 -I -B tr6_indir.py <cikti_dizini>
Her yıl ayrı dosya (emsc_YYYY.txt) ve SHA256 listesi yazar. Anahtar gerekmez.
"""
import hashlib, os, sys, time, urllib.request, urllib.parse

KUTU = dict(minlat=40.2, maxlat=41.3, minlon=26.3, maxlon=30.3)
YILLAR = range(2006, 2026)
SON = "2025-12-31T23:59:59"
URL = "https://www.seismicportal.eu/fdsnws/event/1/query"


def indir(yil, cikti):
    q = dict(KUTU, starttime=f"{yil}-01-01T00:00:00",
             endtime=(SON if yil == 2025 else f"{yil}-12-31T23:59:59"),
             format="text", limit=20000, orderby="time-asc")
    url = URL + "?" + urllib.parse.urlencode(q)
    for i in range(6):
        try:
            with urllib.request.urlopen(url, timeout=180) as r:
                b = r.read()
            break
        except Exception as e:  # ağ hatası: bekle, yeniden dene
            time.sleep(2 ** (i + 1))
    else:
        raise SystemExit(f"{yil}: indirilemedi")
    yol = os.path.join(cikti, f"emsc_{yil}.txt")
    with open(yol, "wb") as f:
        f.write(b)
    return yol, hashlib.sha256(b).hexdigest(), b.count(b"\n") - 1


def main():
    cikti = sys.argv[1]
    os.makedirs(cikti, exist_ok=True)
    satir = []
    for y in YILLAR:
        yol, h, n = indir(y, cikti)
        satir.append(f"{h}  {os.path.basename(yol)}")
        print(y, n, "satır")
    with open(os.path.join(cikti, "SHA256SUMS"), "w") as f:
        f.write("\n".join(satir) + "\n")


if __name__ == "__main__":
    main()
