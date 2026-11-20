# TR-6c sonucu: sismisiteden gerilme ölçerin küresel kör doğrulaması, 20 Kasım 2026

**Hüküm (dondurulmuş ön kayıt, §C8): GÜÇ YOK (K_kapı 5 < 23). Olay sonrası veri indirilmedi; kör kaldı.**

Manifest: `kayit/turetme/tr6/tr6c_manifest.json` (commit 17fccca7). Sınama: `tr6c_sinama_sonuc.json` (079c05ad).

## Ne oldu

1. Bağlayıcı yapay yöntem sınaması (17 hücre × 20 000 deneme, Okada denetimleri, tamlık basamağı (d)) 19 Kasım'da
   bitti ve tuttu. TR-6a'yı kapatan kenar etkisi TR-6c tasarımında giderilmiş.
2. Manifest aşaması (yalnız olay ÖNCESİ veri: sonlu fay ürünleri ve olay öncesi kataloglar) iki kez biçim
   denetiminde durdu; ikisi de veri öncesi eklerle giderildi (ön kayıt Ek 2: deniz suyu katmanlı 12 sonlu fay ürünü
   ve başlıkta M0 = 0 yazan Van 2011 ürünü; Ek 3: bir ISC yanıtının sonundaki tek "?" satırı). Ayrıntı
   `kayit/onkayit/TR-6c_MANIFEST-DURMA-TANI.md`.
3. Manifest sayımı:

| Basamak | Sayı |
|---|---|
| Aday birim | 81 |
| Veri yok (moment sağlaması) | 2 |
| Arka plan kapısını geçen birim (olay öncesi beklenen sayı N0 ≥ 31,36) | 7 |
| Bağımsız küme | 7; bilinen sonuçlu 2 küme çıkınca **K_kapı = 5** (kapı 23) |

   Hesaplanabilen 72 birimde olay öncesi arka plan sayısının ortancası 2,0; N0 ≥ 10 olan 12, ≥ 17 olan 8 birim var.
   Kalan 5 küme: 3 doğrultu atımlı, 2 ters faylı.

## Okuma

Üstveri sayımı (12 Kasım) 29 küme demişti; gerçek kataloglarla 5 kaldı. Darboğaz, büyük depremlerin lob
bölgelerinde olaydan ÖNCEKİ küçük deprem sayısı: tamlık büyüklüğünün üstünde yeterli arka plan olan yer çok az.
Bu, döngünün ortak dersinin (üstveri sayımı gerçek veride 3–5 kat küçülür) en sert örneği. Yöntem yapay veride
çalışıyor; açık küresel kataloglar onu sınamaya yetmiyor.

"Güç yok" ölçünün yanlış olduğu anlamına gelmez. 5 kümeyle görülebilir en küçük etki: beş kümenin beşinin de
beklenen yönde oy vermesi (p₀ 0,52 iken tek yanlı p ≈ 0,04); yani yalnız "neredeyse her zaman doğru" düzeyinde bir
ölçü görülebilirdi. Etki büyüklüğünün kaynağı: tahmin (ön kayıt §C11).

## Körlük

Olay sonrası kataloglar açılmadı. Aday aynı kör veriyle yeniden açılabilir.

## Ardıl soru

Kapıyı belirleyen N0. Çıkan soru (TR-6d): bölgesel düşük tamlık büyüklüklü kataloglarla (JMA, GeoNet, SCSN/NCSN,
INGV, KOERI) olay öncesi arka plan sayısı N0 ≥ 31 olan küme sayısı 23'ü bulur mu; önce 0 € sayım. TR-13d'deki
benzer sayım 7–8 yeni küme vermişti, yani beklenti düşük; sayım yine de yapılacak (eleme yok).
