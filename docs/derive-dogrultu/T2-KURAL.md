# T2 ön kaydı: sismisite kümelenmesinden kenetlenme, San Andreas'tan Marmara'ya (10 Kasım 2026)

Seçim: Erdem, 10 Kasım 22:45, "hepsini paralel başlatalım". Kaynak: Liu, Ross, Cochran 2022 (Sci. Adv., 10.1126/sciadv.abk1167): orta San Andreas'ta sünme hızı kümelenmemiş deprem payıyla orantılı.

**Körlük beyanı (Ek 0):** kural kör değil. Marmara'da CMF batısının sündüğü, doğusunun kilitli olduğu v1.8'den biliniyor (bu yüzden C kapısı yalnız kontrol). Kural yazılırken hiçbir katalog indirilmedi ve hiçbir kümelenme payı hesaplanmadı. UCERF3 FM3_1 dosyası (sünme payları) okundu: bu hedef değişken, sonuç değil.

## Veri

- **Hedef (sünme payı):** UCERF3 FM3_1 fay bölümlerinin `aseismicSlipFactor` değeri (ASF; Field vd. 2014, OpenSHA `FM3_1.xml`, sha256 dosyada). Kenetlenme c = 1 − ASF.
- **Kaliforniya kataloğu:** USGS ComCat, 1990-01-01 – 2025-12-31, enlem 32–42, boylam −125 – −114, derinlik ≤ 20 km.
- **Marmara kataloğu:** EMSC FDSN (katkıcılar KOERI/AFAD), 2008-01-01 – 2025-12-31, enlem 40,3–41,2, boylam 26,5–30,0, derinlik ≤ 20 km. Türkiye dışı 2026 kullanılmaz (bitiş 2025-12-31).
- **Ortak büyüklük eşiği:** her katalogda Mc = maksimum eğrilik + 0,2 (0,1 kutu); M_th = max(Mc_KA, Mc_MAR), 0,1'e yukarı yuvarlanır, iki kataloğa da uygulanır.

## Yöntem

1. **Kümelenme (Zaliapin–Ben-Zion 2013):** her katalogda bütün bölge için en yakın komşu: η_ij = t_ij · r_ij^1,6 · 10^(−1,0·m_i), t yıl, r episantral km (alt sınır 0,1 km), i < j. Eşik η0: log10 η'ye 2 bileşenli Gauss karışımı, iki ortalama arasındaki yoğunluk kesişimi; uydurma başarısızsa 10^−5. Arka plan = η > η0.
2. **Kutular:** FM3_1'de doğrultu atımlı bölümler (rake 180 ± 30 ya da 0 ± 30, eğim ≥ 70°), yüzey izine yatay uzaklığı ≤ 5 km olan olaylar. Bölüm başına en az 30 olay; azsa bölüm dışarıda.
3. **Kalibrasyon:** yalnız adı "San Andreas" ile başlayan bölümler. ASF_tahmin = kırp(α + β·f_bg, 0, 1), sıradan en küçük kareler.
4. **Transfer (doğrulama):** geri kalan bütün uygun bölümler. Ölçütler: Spearman ρ_v (tek yönlü permütasyon p, 10 000), MAE_model, MAE_sabit (kalibrasyon ortalaması), MAE_sıfır (hepsi kilitli). Bölüm bootstrap'ı ile %90 aralık.
5. **Marmara kutuları:** EDSF13 TRCS996 (Marmara–Saros) ve TRCS013 (Doğu Marmara) izlerinin birleşimi, boylam pencereleri: Ganos 26,95–27,50; Tekirdağ (bilgi) 27,50–27,75; CMF-B (Western High, Orta Havza, Kumburgaz batısı) 27,75–28,40; CMF-D (Kumburgaz doğusu) 28,40–28,75; PIF 28,75–29,20; Çınarcık güney kolu TRCS014 tamamı (bilgi). 5 km koridor, aynı en az 30 olay kuralı.

## Kapılar ve hüküm

- **A (kalibrasyon):** ρ_kal ≥ 0,5 ve β > 0. Geçmezse: H0, "ilişki bu kurulumda yeniden üretilemedi", gerisi bilgi satırı.
- **B (transfer, ateşleme kapısı):** N_doğrulama ≥ 8; ρ_v ≥ 0,4 ve p ≤ 0,05; MAE_model < min(MAE_sabit, MAE_sıfır). N < 8 ise önceden "ayırt edilemez".
- **C (Marmara kontrolü):** ASF_tahmin(CMF-B) − ASF_tahmin(CMF-D) > 0 ve ASF_tahmin(CMF-B) − ASF_tahmin(Ganos) > 0, ikisinin de %90 bootstrap aralığı (Marmara olayları üstünde) sıfırı dışlar.
- **H1:** A, B, C geçer → PIF için ASF_tahmin ve c = 1 − ASF, %90 aralıkla raporlanır; ileri test defterine "T2-PIF bilgi satırı" olarak girer. Simülatör sürümüne (v2.x) yükleme olarak taşınması ayrı, sunucuda bir iş; bu kural onu yapmaz.
- **H0:** herhangi bir kapı kalırsa PIF sayısı verilmez (yalnız bilgi olarak yazılır, kullanılmaz).
- **Bilgi satırları (hükme girmez):** (i) Marmara'da M ≥ 5,5 olaylarının 30 km'sinde 1 yıl dışarıda; (ii) koridor 3 km ve 10 km; (iii) η0 = 10^−5 sabit.

## Sınırlar

ASF bir alan azaltma katsayısıdır, sünme hızı oranı ile birebir aynı değildir. EMSC kataloğu birden çok kurumun ML'sini birleştirir. Kümelenme payı büyük artçı dizilerine duyarlıdır (Marmara'da 2019 ve 2025). v1.3b değişmez.
