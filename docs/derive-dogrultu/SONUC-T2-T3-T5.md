# T2, T3, T5 sonuçları (10–11 Kasım 2026)

Kurallar: `T2-KURAL.md`, `T3-KURAL.md`, `T5-KURAL.md` (dondurma cda6638, `DONDUR-derive-dogrultu.json` + OTS). Kod ve çıktılar `kosu/`. Harcama 0 € (makine kiralanmadı). Türkiye dışı 2026 verisi kullanılmadı. v1.3b değişmedi; hiçbir olasılık yazılmadı.

## Özet

| Sınav | Hüküm | Tek cümle |
|---|---|---|
| T2 kümelenme → PIF kenetlenmesi | **H0** (A kapısı kaldı) | San Andreas'ta arka plan payı ile sünme payı ilişkisi bu kurulumda **ters işaretli** çıktı (ρ_kal −0,47, β < 0); PIF sayısı verilmez. |
| T3 kayma öngörülebilirliği | **veri yetersiz** (2 bağımsız olay < 3) | 8 segment okunabildi; bilgi olarak açık modeli ölçek modelini ΔL +8,7 nat geçiyor ama bütün fark Mandalay'dan, %90 aralık sıfırı içeriyor. R medyanı 1,69 (8 segmentin 7'si ≥ 1). |
| T5 tehlike modeli karnesi | **H0** | 5 puanlanabilir olayda 2 kaçırma (Ridgecrest yer, Pazarcık büyüklük), pay 0,40, binom p 0,26 (p0 0,2). |

## T2 (kural birebir)

- Kataloglar: ComCat Kaliforniya 1990–2025, M ≥ 2,2: 128.885 olay; EMSC Marmara 2008–2025: 4.477 olay. Mc_KA = 0,9 + 0,2 = 1,1; Mc_MAR = 2,0 + 0,2 = 2,2 → **M_th 2,2**.
- ZBZ eşiği (GMM kesişimi): η0_KA 1,96·10⁻⁶, η0_MAR 1,50·10⁻⁵. Bütün bölge arka plan payı KA 0,51, Marmara 0,68.
- Kutular: 14 San Andreas (kalibrasyon), 107 doğrulama bölümü (yalnız 18'inde ASF > 0).
- **A:** ρ_kal −0,47, β −0,47 → kaldı. B de kaldı (ρ_v 0,18, p 0,03; MAE_model 0,25 > MAE_sıfır 0,058). C kaldı (CMF-B − CMF-D +0,01, %90 [−0,02, +0,04]).
- Marmara ham arka plan payları (bilgi, ASF'ye çevrilmez çünkü A kaldı): Ganos 0,86, Tekirdağ 0,61, CMF-B 0,40, CMF-D 0,42, PIF 0,66, Çınarcık 0,61. CMF-B ile CMF-D ayırt edilemiyor; bilinen batı sünmesi bu ölçüyle görünmüyor.
- Bilgi satırları (artçı dışlama, 3/10 km koridor, η0 = 10⁻⁵): hepsinde A ters işaretli, hüküm değişmez.
- Ders: Liu–Ross–Cochran ilişkisi ham ZBZ payı + UCERF3 ASF ile yeniden üretilemedi; ilişki muhtemelen tekrarlayan küçük depremler ve onların özel kümelenme ayrımına bağlı. Marmara'ya taşınamaz.

## T3 (kural birebir, tablo puanlamadan önce donduruldu: `kosu/t3/T3-TABLO.json`, sha d44303ed…, OTS, commit 2d48a19)

| Olay | Segment | t_last | v (mm/yıl) | D_obs (m) | D_açık (m) | D_ölçek (m) | R |
|---|---|---|---|---|---|---|---|
| Pazarcık 2023 | Amanos | 1872 | 4,61 | 2,0 | 0,70 | 7,78 | 2,87 |
| Pazarcık 2023 | Erkenek | 1893 | 9,26 | 3,7 | 1,20 | 7,78 | 3,07 |
| Elbistan 2023 | Çardak | 584 | 2,5 | 4,7 | 3,60 | 3,66 | 1,31 |
| Elbistan 2023 | Göksun | 584 | 2,5 | 4,0 | 3,60 | 3,66 | 1,11 |
| Mandalay 2025 | 1839 kesimi | 1839 | 23 | 3,87 | 4,28 | 12,26 | 0,90 |
| Mandalay 2025 | 1930 kesimi | 1930 | 20 | 2,26 | 1,90 | 12,26 | 1,19 |
| Mandalay 2025 | 1946 kesimi | 1946 | 23 | 3,77 | 1,82 | 12,26 | 2,07 |
| Mandalay 2025 | 1956 kesimi | 1956 | 23 | 3,67 | 1,59 | 12,26 | 2,31 |

- Kapı: 8 segment ≥ 6 ama bağımsız olay 2 (Pazarcık–Elbistan ikizi tetiklenmiş tek dizi sayıldı, ihtiyatlı okuma) → **veri yetersiz**.
- Bilgi: ikiz iki olay sayılırsa kapı açılır; σ 0,25'te ΔL +8,71 nat (Kahramanmaraş bloğu +0,02, Mandalay +8,69), olay bootstrap'ı %90 [−0,001, +17,4] → yine H0. σ 0,15: +24,2; σ 0,35: +4,4; aralıklar aynı biçimde sıfırda.
- Kahramanmaraş'ta iki model eşit; açık modelin üstünlüğü yalnız Wells–Coppersmith'in 480 km'lik kırıkta 12 m öngörmesinden geliyor.
- **R medyanı 1,69, aralık 0,90–3,07, payı ≥ 1 olan 0,875**: Vavra ve Ulrich'in "kayma ≥ biriken açık" bulgusu çok olaylı derlemede de duruyor. Bu bir alt sınır okuması, nokta kestirimi değil.
- Dışarıda kalanlar (`T3-TABLO.json` → `disarida`): Pazarcık segmenti (1513 atfı okuduğum tam metinde yalnız olay sonrası kaynaklarda; Ambraseys 1989 OUP'tan indirilemedi), İzmit 1999 (Stein 1997, Barka 1996/2002 tam metin kapalı), Düzce, KAF 1939–1967 (olay öncesi hız yok), Kunlun/Denali/Palu/Maduo.
- **Sapma notları (Ek):** (1) t_last ve v sayıları, okuduğum tam metnin olay öncesi kaynağa açık atfıyla alındı (ikincil aktarım), kaynakların kendisi okunmadı. (2) Mandalay v, kaynak başına aritmetik ortalama yerine Ulrich'in olay öncesi aralığı kapsayan değerleri (20/23). (3) Mandalay D_obs Ulrich Şekil 2b'den okundu (±0,05 m).
- Marmara bilgi satırı (CMF/PIF Mw aralığı) yalnız H1'de yazılacaktı; yazılmadı.

## T5 (kural birebir)

ComCat 2014–2025, Mw ≥ 6,5, derinlik ≤ 30 km: 289 olay, kıyıdan ≤ 20 km 90, doğrultu atımlı (USGS MT) 40. Açık, makine okunur olay öncesi model alanında olanlar:

| Olay | Mw | Model | K1 payı | K1 | Kesişen en büyük Mmax | K2 | Kaçırıldı |
|---|---|---|---|---|---|---|---|
| Ridgecrest 2019 | 7,1 | UCERF3 FM3_1 | 0,32 | kaldı | — | uygulanamaz | **evet** |
| Elazığ 2020 | 6,7 | ESHM13 | 0,76 | geçti | 7,42 | geçti | hayır |
| Pazarcık 2023 | 7,8 | ESHM13 | 0,69 | geçti | 7,47 | **kaldı** | **evet** |
| Elbistan 2023 | 7,5 | ESHM13 | 0,64 | geçti | 7,68 | geçti | hayır |
| Kumamoto 2016 | 7,0 | J-SHIS Y2014 (Aralık 2014 sürümü) | 0,54 | geçti | 8,2 (Mj) | geçti | hayır |

- N 5 (kapı açık), kaçırma 2, pay 0,40, tek yönlü binom p 0,26 → **H0**. Bilgi (kayma ≥ %10 maks): aynı sonuç.
- Puanlanamayanlar: Monte Cristo 2020, Samothraki 2014, Lefkada 2015 (USGS FFM yok); Palu, Maduo, Mandalay, Filipinler, Çin, Tacikistan olayları (açık olay öncesi model dosyası yok). Seçim yanlılığı: karne yalnız açık dosya yayımlayan modellerle sınırlı.
- J-SHIS büyüklükleri Mj; Mw ile doğrudan aynı değil (Kumamoto K2 sonucu bundan etkilenmez, pay 1,2).
- Marmara bağı yalnız H1'de yazılacaktı. Not (hükme girmez): ESHM13'ün Pazarcık'ı 0,3 birim küçük tahmin etmesi, çok segmentli kırılma dalının (v1.7) neden ayrıca taşındığını hatırlatıyor.

## Defter

Üç sınavdan hiçbiri H1 değil; ileri test defterine olasılık ya da yeni rakip girmez. Defter satırı önerisi `DEFTER-ONERI.json` (yalnız bilgi satırı, sunucu oturumunda işlenir).
