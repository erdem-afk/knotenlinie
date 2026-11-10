# T5 ön kaydı: olay öncesi tehlike modellerinin büyük doğrultu atımlı kırılma karnesi (10 Kasım 2026)

Seçim: Erdem, 10 Kasım 22:45, "hepsini paralel başlatalım". Soru: 2014–2025 büyük doğrultu atımlı depremlerinde, olaydan önce yayımlanmış fay tabanlı tehlike modeli gerçek kırığı (yer ve büyüklük) kendi kaynak kümesinde içeriyor muydu?

**Körlük beyanı (Ek 0):** kör değil. Kahramanmaraş 2023'ün segment modellerini aştığı literatürde biliniyor (Wang–Barbot 2024, Hara–Toda 2026). Kural yazılırken hiçbir olay için kapsama hesaplanmadı; EDSF13 dosyasının alan adları okundu.

## Olay listesi (kodla, nesnel)

USGS ComCat: 2014-01-01 – 2025-12-31, Mw ≥ 6,5, derinlik ≤ 30 km, USGS moment tensörü rake'i 0 ± 30 ya da ±180 ± 30 (en az bir düğüm düzlemi), merkez üssü aşağıdaki modellerden birinin kapsama alanında ve kıyıdan ≤ 20 km. Türkiye dışı 2026 kullanılmaz.

## Olay öncesi modeller (yayım tarihi < olay tarihi)

- ESHM13 / EDSF13 (2013): Avrupa + Türkiye; HM-CFS `MAXMW`, DB-CFS izleri.
- UCERF3 FM3_1 (2013–2014): Kaliforniya; bölüm izleri (OpenSHA). Mmax alanı yok.
- Yeni Zelanda NSHM 2010 (Stirling 2012), Japonya J-SHIS (olay öncesi sürüm), Endonezya 2017 ve diğerleri: yalnız açık, makine okunur kaynak dosyası bulunursa. Bulunamazsa olay "model yok" diye dışarıda kalır ve öyle yazılır.

## Gözlenen kırık

USGS ComCat sonlu fay ürünü (FFM): kayması > 0 olan alt fayların üst kenarları = gözlenen iz; L_obs bunların toplam uzunluğu; Mw_obs USGS.

## Ölçütler

- **K1 (yer):** gözlenen izin model kaynak izlerine ≤ 5 km uzaklıktaki payı ≥ 0,5.
- **K2 (büyüklük, Mmax veren modellerde):** K1'de kesişen kaynakların en büyük Mmax'ı ≥ Mw_obs − 0,2. Mmax vermeyen modelde K2 "uygulanamaz".
- Olay **kaçırıldı** = K1 kaldı ya da K2 kaldı.

## Hüküm

- Ateşleme kapısı: puanlanabilen olay N ≥ 5; değilse "veri yetersiz".
- **H1:** kaçırma payı, p0 = 0,2'ye karşı tek yönlü binom p ≤ 0,05 → "olay öncesi segmentli modeller büyük doğrultu atımlı kırılmaları sistematik olarak küçük/eksik tahmin etmiş".
- **H0:** p > 0,05.
- **Marmara'ya bağ (bilgi satırı, model değiştirmez):** H1 çıkarsa EDSF13 Marmara kaynaklarının MAXMW değerleri ve v1.3b segment Mchar'ları ile bütün-Marmara (Ganos–CMF–PIF) kırılmasının Mw'si yan yana yazılır; v1.7 ortak kırılma dalı için bağlam. v1.3b değişmez, yeni olasılık yazılmaz.

## Sınırlar

N küçük (≈5–10), bir karne, güçlü bir sınav değil. Modellerin çoğu açık makine okunur dosya yayımlamıyor; bu seçim yanlılığı yazılır.
