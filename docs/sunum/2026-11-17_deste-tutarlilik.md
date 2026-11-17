# Hoca destesi: sayı ve harita tutarlılığı (17 Kasım 2026)

Deste: https://claude.ai/artifact/7tYJryMAAh5TS3wpk8Eh11 (sürüm 19). Değişen slaytlar: years (9), cmf (10), reading (15), istanbul (2).

## 1. Defter sayıları (kayit/adaylar.jsonl, dal claude/project-thread-hjup0f 9be668d, 100 satır)
Durum: kapandi 41, kapali-sartli 1 (K10), elendi 28, rakip 11, aday 10, kosuyor 4, birlesti 5.
Tek tanım: "closed after work" = kapandi + kapali-sartli = **42**. "Worked through" = 42 + 11 rakip = **53**.
- Slayt 9: 41 → 42; döküm 18 H0, 8 güç yok, 8 veri yok, 4 ayırt edilemez, 4 diğer; 5 birleşti.
- Slayt 15: 53 = 42 + 11. "16 / 10" tüm defter: güç yok 16 = 8 kapandı + 4 elendi + 4 aday; veri yok 10 = 8 kapandı + 2 elendi. Slaytta "Of the 42 closed, 8 and 8 (16 and 10 across all 100 ideas)".

## 2. 1912 Mürefte izi
Ayrı açık iz dosyası yok. Kaynak Aksoy vd. 2010, Geology 38(11) 991–994, doi:10.1130/G31447.1 (yazar kopyası web.itu.edu.tr/~cakirz/papers/Aksoy_etal_2010.pdf): 9 Ağustos Mw ≈7,4, 120 ± 30 km; karada 45 km (N68°E, Saros–Gaziköy), denizde Gaziköy → Orta Havza 65 km (N88°E), Saros Körfezi'nde ≥40 km; 13 Eylül Mw 6,8, ≈37 km Saros.
Modelin izi (magma-corbasi docs/tasarim/2026-11-08_marmara/02-segment-B-KURAL.md, tools/marmara/segment.py:66–72): EDSF13 TRCS996 (→TRCS013) boyunca 26,85°E'den doğuya 90 ve 120 km (eşit ağırlık); uçlar ≈40,60°N 26,85°E → ≈40,81°N 27,92°E / ≈40,835°N 28,27°E. 13 Eylül: 26,49–26,85°E.
Ekran önerisi: EDSF13 geometrisi (CC BY 4.0) üzerinde bu aralık, etiket "1912 rupture ≈90–120 km (Aksoy et al. 2010)", doğu ucu bant olarak.

## 3. İzmit büyüklüğü
Mw 7,6: GCMT 081799A (M0 2,88e20 N·m, Ms 7,8), USGS ComCat usp0009d4z 7,6 mwc. 7,4: ilk raporlar ve Barka vd. 2002 başlığı; kayma modelleri 7,4–7,5; Marmara segment modeli İzmit karakteristik büyüklüğü 7,4 (tools/marmara/segment.py:42). Deste artık **Mw 7,6** diyor; video da 7,6 kullanmalı.

## 4. CMF sünme/kilit sınırı
magma-corbasi docs/sonuc/2026-11-10_cmf-kilitlenme.md:10: Western High ve Kumburgaz batısı yüzeyde 10–15 mm/yıl sünüyor, Kumburgaz doğusu sünmüyor.
- Kumburgaz Havzası 28,51–28,535°E, 40,87°N: 0,80 ± 1,25 mm/yıl, kilitli (Sakic 2016, Lange 2019).
- Western High: 10,7 ± 4,7 mm/yıl (Yamamoto 2019).
- Diğerleri: Özbey 2021 28,2°E doğusu kilitli; Klein 2026 28,6°E'ye kadar sünme; Becker 2023 tekrarlayanlar 27,7–28,1°E.
Ekran: keskin çizgi gerekiyorsa ≈28,5°E; dürüst gösterim 28,2–28,6°E geçiş bandı. Not: modeldeki CMF/PIF sınırı 28,7926°E yalnız segment kesimi, sünme sınırı değil.

## 5. Sun 2026 GNSS lisansı
Zenodo 10.5281/zenodo.19501626 (Sun 2025, "GNSS velocity field and earthquake catalog in Turkiye", v2): **CC BY 4.0**, 792 istasyon (GNSS_Turkey.dat). Makale Sun vd. 2026, JGR Solid Earth 131, e2025JB031692. Dosya derleme: Kurt vd. 2023 (Zenodo 7916022, CC BY 4.0) + Karakhanyan 2013 + Djamour 2011. Ekran künyesi: "GNSS: Sun et al. 2026 (Zenodo, CC BY 4.0), compiled from Kurt et al. 2023 and others".
