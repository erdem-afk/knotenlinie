# Türetme zinciri

Her halka: önceki sonuç, ondan çıkan soru, köprü ölçümü, karar. İstem: `kayit/prompt/2026-11-11_fable52-turetme-gorevi.md`.
Köprü ölçümü: iki tohum kümesinin ikisine de atıf yapan iş sayısı k ve Jaccard J (OpenAlex, `kayit/oa.py kopru`);
her ölçümün yanında pozitif kontrol olarak "tahmin sınama × ETAS" (k 154–208, J ≈ 0,06).

## Halka 0 (11 Kasım 2026): başlangıç

Önceki sonuç: 79 aday. Zaman ekseninde olay geçmişine koşullama (FA-1) H0, öncü artış modeli (TK-1) ayırt edilemez,
gevşeme modelleri yarışı (VE-1) veri yok, düşük eşikli katalog (AV-2) güç yok.
Çıkan soru: fayın anlık gerilme ya da kayma durumunu ölçen, daha önce bakılmamış bir gözlem türü var mı ve sınanmış mı?

## Halka 1 (11 Kasım 2026): beş gözlem türünün taraması

Beş kol, Opus alt ajanlarla, OpenAlex. Notlar: `research_notes/Fayın anlık durumu gözlem boşlukları/`.

| Kol | Köprü (× tahmin sınama) | Literatür hükmü | Çıkan aday | Karar |
|---|---|---|---|---|
| Ortam gürültüsüyle sismik hız değişimi | k 6, J 0,0028 (kontrolün 1/23'ü) | Yalnız deprem anı düşüşü ve iyileşme; öncül iddialar tek olaylı. Marmara serisi yayımlanmamış | TR-4 Marmara gürültü tabanı; TR-5 küresel öncül sınavı | Bekle: ölçü en iyi durumda gerilme hızını ölçer; dalga formu işlemesi ağır |
| Ardışık kırılmada komşu segment gecikmesi | k 32, J 0,0127 (1/4'ü) | Sayısal gecikme dağılımı ve puanlı sınav yok | TR-3 gecikme çekirdeği | Kapandı, güç yok: kaba sayımda 1–30 yıl oran artışı 1,14 kat (p ≈ 0,12); gereken olay sayısının 4–20'de biri var |
| Sismisiteden gerilme hızı; tremor | k 61, J 0,024; tremor k 3, J 0,003 | Hepsi geriye dönük, tek olaylı. KAF'ta tremor bulunmamış | TR-6 gerilme ölçerin kör doğrulaması; TR-7 tetiklenmiş tremor taraması | Bekle: çözünürlük 5–25 kPa, Marmara yavaş kaymaları ≲ 1 kPa |
| Nisan 2025 Mw 6,2 doğal deneyi | k 2, J 0,0022 | Kırık doğuya ilerledi, sessiz "Avcılar" kesiminin kenarında durdu; kayma açığı sayısı yok | TR-2 sonraki M≥6'nın yönü; TR-9 artçı cephesi ile jeodezik sınır | TR-2 için önce olay sayımı; TR-9 bekle (2 dizi) |
| Jeodezik geçici ve uydu gravitesi | k 8, J 0,0084; gravite k 0 | Öncül iddiaları 2024–2026'da bağımsız analizde düştü; çok olaylı puanlı sınav yok | TR-1 küresel GNSS hız değişimi sınavı; TR-10 sünme hızı değişimi; TR-8 gravite | TR-1 ÖNE ALINDI; TR-8 elendi (M7 sinyali ölçüm eşiğinin ≈1/125'i); TR-10 bekle |

Neden TR-1: beş kolun ortak bulgusu aynı, hiçbir gözlem türünde yanlış alarm oranı ölçülmüş çok olaylı sınav yok.
TR-1 bunlardan (a) hedef olay sayısı güç kapısını geçebilecek tek aday (kaba sayım 60 olay), (b) verisi açık ve hazır,
(c) fayın kayma durumunu doğrudan ölçen büyüklüğe (yüzey hızı) bakan aday. Ön kayıt: `kayit/onkayit/TR-1_*`.

Kapanmış adayların yeniden açma şartları denetlendi: hiçbiri sağlanmıyor (Y-1: Klein 2026 hakemli değil; FA-3: model
kataloğu kapalı; VE-1: dört tam metinden ikisinin açık bağlantısı var ama okunamadı; S-2: Murru 2016 açık bağlantısı
bulundu, içerik işlenmedi).
