"""TR-6 (b) katalog indirme: KOERI zeqdb (Boğaziçi Ü. Kandilli Rasathanesi), Marmara kutusu, 2006..2025.

KÖR KURAL: her sorgunun bitişi en geç 2025-12-31'dir; 2026 olayı istenmez. Okuma tarafında (tr6_sayim.py)
ikinci koruma: zaman >= 2026-01-01 olan satır sayılmadan atılır, sayısı yazdırılmaz.
Yıl başına bir sorgu. Sayfa 'Liste sonu' işaretini ve 'Bulunan: N' sayısını taşır; ayrıştırılan satır
sayısı N'ye eşit değilse ya da işaret yoksa yıl yeniden indirilir (sunucu yarım kesebiliyor).

Kullanım: python3 -I -B tr6_indir_koeri.py <cikti_dizini> [yil ...] [--aylik]
"""
import hashlib, os, re, subprocess, sys, time, urllib.request, urllib.parse

KUTU = dict(EnMin="40.20", EnMax="41.30", BoyMin="26.30", BoyMax="30.30")
URL = "http://www.koeri.boun.edu.tr/sismo/zeqdb/submitRecSearchT.asp"
SATIR = re.compile(r"^\s*\d{6}\t\d{14}\t\d{4}\.\d\d\.\d\d\t")  # sekmeyle ayrılmış; boş alan olabilir


def ayristir(metin):
    duz = re.sub(r"<[^>]+>", "\n", metin)
    m = re.search(r"Bulunan:\s*(\d+)", duz)
    n_beyan = int(m.group(1)) if m else -1
    satirlar = [s.strip("\r\n ") for s in duz.splitlines() if SATIR.match(s)]
    return n_beyan, satirlar, ("Liste sonu" in duz)


def indir(yil, a0="01", a1="12", g1="31"):
    q = dict(bYear=yil, bMont=a0, bDay="01", eYear=yil, eMont=a1, eDay=g1, MAGMin="0.0", MAGMax="9.0",
             DerMin="0", DerMax="500", Tip="Deprem", ofName="tr6.txt", **KUTU)
    url = URL + "?" + urllib.parse.urlencode(q)
    for i in range(10):
        try:
            # curl: sunucu yarım bağlantıda asılı kalabiliyor; -m ile kesin üst süre
            metin = subprocess.run(["curl", "-sS", "-m", "900", url], capture_output=True, check=True,
                                   timeout=960).stdout.decode("latin-1")
            n, s, son = ayristir(metin)
            if son and n == len(s):
                return s
            print(yil, "eksik sayfa", n, len(s), son, file=sys.stderr)
        except Exception as e:
            print(yil, "hata", type(e).__name__, getattr(e, "stderr", b"")[:200], file=sys.stderr)
        time.sleep(10 * (i + 1))
    raise SystemExit(f"{yil}-{a0}: tam indirilemedi")


def indir_aylik(yil):
    """Sunucu büyük yanıtları yarıda kesiyor (IncompleteRead) ve eşzamanlı sorgularda düşüyor: yılı çeyreklere
    bölerek, tek akışta indir."""
    import calendar
    s = []
    for a0 in (1, 4, 7, 10):
        a1 = a0 + 2
        g = calendar.monthrange(yil, a1)[1]
        s += indir(yil, f"{a0:02d}", f"{a1:02d}", f"{g:02d}")
        print(yil, a0, "çeyrek tamam", file=sys.stderr, flush=True)
    return s


def main():
    cikti = sys.argv[1]
    aylik = "--aylik" in sys.argv
    yillar = [int(a) for a in sys.argv[2:] if a != "--aylik"] or list(range(2006, 2026))
    assert max(yillar) <= 2025, "2026 kör"
    os.makedirs(cikti, exist_ok=True)
    for y in yillar:
        s = indir_aylik(y) if aylik else indir(y)
        b = ("\n".join(s) + "\n").encode("utf-8")
        yol = os.path.join(cikti, f"koeri_{y}.txt")
        with open(yol, "wb") as f:
            f.write(b)
        with open(os.path.join(cikti, "SHA256SUMS_koeri"), "a") as f:
            f.write(f"{hashlib.sha256(b).hexdigest()}  koeri_{y}.txt\n")
        print(y, len(s), "satır", flush=True)


if __name__ == "__main__":
    main()
