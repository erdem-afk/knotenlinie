#!/usr/bin/env python3
"""TR-10b, Ek 1 E1.3 "başlık katılmış" bilgi satırının HDR olay tablosu (yalnız üstveri; hükmü değiştirmez).

Bağlayıcı HDR okuması (`tr10b_hdr.py`, E1.2–E1.3) tablo başlık satırlarını ("Possible Offsets:", "Known Offsets:" …)
ayrı TARİHSİZ not olarak işler. E1.3'ün öteki okuması: başlık, hemen ardından gelen ilk tablo satırına katılır.
Bu betik `tr10b_hdr.py`'yi DEĞİŞTİRMEDEN içe aktarır (sha256'sı Ek 1 E1.2'de kayıtlı); yalnız not birimini şu
kuralla değiştirir:

  Uyarlanmış not biriminde (tr10b_hdr.notlara_bol_uyarli) tablo satırı OLMAYAN bir not, aynı paragrafta (arada boş
  satır ya da ayraç satırı olmadan) hemen ardından gelen notun ilk satırı bir TABLO SATIRIYSA, o nota katılır.
  Katılan notun satır numarası başlığın satır numarasıdır; tarihi, kuralın değişmemiş "en soldaki tam tarih"
  ilkesiyle tablo satırının zaman damgasıdır.

Önek listeleri, tür kuralı, tarih tanıma ve tarihsiz not kuralı değişmez. HDR dosyaları (üstveri) bağlayıcı HDR
adımında açılmış olan dosyalardır; manifest sha256'larıyla denetlenir. Hiçbir sünme verisi açılmaz.

Kullanım (depo kökünden):
  python3 -I -B kayit/turetme/tr10b/tr10b_hdr_baslik.py <hdr_dizini> <tr10_ham> [--cikti <csv>]
Çıktı varsayılanı kayit/turetme/tr10b/tr10b_hdr_olaylar_baslik_katilmis.csv ("x" kipinde). Ayrıca B listesine
etkisini yazar (E1.3: B 47 yer-pencere / 25 yer).
"""
import datetime as dt
import json
import os
import sys

BURA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURA)
import tr10b_hdr as H  # noqa: E402  (değiştirilmez)
import tr10b_listeler as TL  # noqa: E402

HK = H.HK
CIKTI = os.path.join(BURA, "tr10b_hdr_olaylar_baslik_katilmis.csv")


def notlara_bol_baslik_katilmis(satirlar):
    notlar = H.notlara_bol_uyarli(satirlar)
    out = []
    i = 0
    while i < len(notlar):
        bas, p = notlar[i]
        if (i + 1 < len(notlar) and not H.TABLO_SATIRI.match(p[0])):
            bas2, p2 = notlar[i + 1]
            ara = satirlar[bas + len(p):bas2]
            if H.TABLO_SATIRI.match(p2[0]) and not ara and bas + len(p) == bas2:
                out.append((bas, p + p2))
                i += 2
                continue
        out.append((bas, p))
        i += 1
    return out


def kur():
    HK.notlara_bol = notlara_bol_baslik_katilmis
    HK.tarih = H.tarih_uyarli


def uygula(hdr_dizin, tr10_ham, manifest=H.MANIFEST):
    T = TL.listeleri_yukle()
    ilk = {k: dt.date.fromisoformat(v["ilk"]) for k, v in T["istasyon"].items()}
    for s in H.KS.sayfa_istasyonlar(tr10_ham):
        ilk.setdefault(s["kod"], s["ilk"])
    eski = H.uyarlamayi_kur
    H.uyarlamayi_kur = kur
    try:
        ol, _, _ = H.uygula(hdr_dizin, manifest, None, ilk)
    finally:
        H.uyarlamayi_kur = eski
        H.uyarlamayi_kur()
    return ol, H.etki(ol, T["listeler"], T["istasyon"])


def main():
    a = sys.argv[1:]
    cikti = a[a.index("--cikti") + 1] if "--cikti" in a else CIKTI
    ol, e = uygula(a[0], a[1])
    metin = H.csv_metni(ol)
    with open(cikti, "x", encoding="utf-8") as f:
        f.write(metin)
    print(json.dumps({ad: dict(yp=v["K_sonrasi"]["yer_pencere"], yer=v["K_sonrasi"]["yer"],
                               K_dusen=v["K_dusen"]) for ad, v in e.items()}, ensure_ascii=False, indent=1))
    print("yazıldı:", cikti)


if __name__ == "__main__":
    main()
