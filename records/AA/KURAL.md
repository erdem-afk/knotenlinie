# AA: STEP tipi günlük model, hesap öncesi sabit kural

Bu dosya, hiçbir model 2006–2010 ya da 2011–2015 üstünde puanlanmadan önce yazıldı (yazıldığında yalnız ≤2005 ayar verisinde kurulum duman testi yapılmıştı; ayar kataloğunun dışında hiçbir olay puanlanmadı). Sonuçtan sonra değişmez; gerekirse puanlamadan önce tarihli "Ek" satırı eklenir. SHA256'sı `OLCUM.json`'da kayıtlıdır.

**Skor zinciri.** STEP üyesi → skor defteri (2006–2010, 2011–2015) → ETAS-LM ve R-ortak-kaskad'a karşı IG, ve Topluluk 2 kuralının E1 karışımı ({R, LM, STEP}, eşit ağırlık, ek satır).

**Çerçeve.** Ortak günlük çerçeve: CSEP İtalya 8993 hücre, [0,30) km, HORUS-Mw, günlük, 0,1 M kutuları 2,95'ten, son kutu +∞; her UTC günü yalnız gün başından önceki olaylar. Eşikler M≥2,95 (geliştirme), M≥3,95 (hüküm), M≥4,95 (ek). Bölme: ≤2005 ile kur, 2006–2010 M≥2,95 logL'iyle hiperparametre seç, ≤2010 ile yeniden kur, 2011–2015'te bir kez puanla.

## Model (kaynaklar bellekten uyarlama; özgün STEP kodu ve Lolli–Gasperini tablosu erişilemedi)

*Girdi olayları.* Katalog `ortak/italya_katalog_le2015.csv`; 1985-01-01 sonrası, kutu içi, derinlik [0,30), Mw≥Mc=3,1 (R/LM'nin ≤2005 tamlık eşiği). Ayar için yalnız ayar sonundan önceki olaylar.

*Diziler (nedensel).* Olaylar zaman sırasıyla işlenir. Bir olay, kendisinden kesin büyük, Gardner–Knopoff (1974) zaman penceresi (Uhrhammer: log T = 0,5409 M − 0,547 gün, M≥6,5 için 0,032 M + 2,7389) ve uzay penceresi (log R = 0,1238 M + 0,983 km) içindeki bir ana şokun dizisine atanır (birden çoksa en büyük ana şok). Atanamayan ve M≥Mseq olan olay yeni ana şoktur. Atanamayan her olay (ana şoklar dahil) arka plan olayıdır.

*(a) Arka plan.* Arka plan olaylarının günlük oranı μ (M≥3,1), Aki–Utsu b (0,1 kutu düzeltmeli), GR ile 2,95'e uzatma; uzay yüzeyi `tools/ortak_zemin/arka_plan.py: arka_plan_sec` (T/R'nin Gauss KDE'si, bant ve zemin payı kendi tutulmuş-konum bölmesiyle seçilir). Zamandan bağımsız.

*(b) Genel model.* Reasenberg–Jones (1989): λ(t,M)=10^(a+b(Mm−M))(t+c)^−p. (a,b,p,c) tüm ayar dizilerinden, artçıları [Mc, Mm] aralığına kesilmiş Poisson olabilirliğinin L-BFGS-B maksimumudur (üç başlangıç; sınırlar a∈[−4,1], b∈[0,6;1,5], p∈[0,6;1,6], c∈[1e−4,1] gün). Dizi gözlem uzunluğu min(T_GK, ayar sonu − ana şok). Tahmin kutularında kesilmemiş RJ kullanılır. Lolli ve Gasperini (2003) İtalya genel değerleriyle (anımsanan: a≈−1,66, b≈0,96, p≈0,93–0,96, c≈0,01 gün; doğrulanamadı) karşılaştırma raporda, a'nın kesilmiş-olabilirlik tanımı farkı notuyla.

*(c) Diziye özgü.* Üye sayısı n ≥ n_min olan dizi için üç model: genel (0 serbest), yalnız-a (p, c, b genel; a kapalı biçimde), (a,p) (c, b genel; p sınırlı 1B optimizasyon). Her gün başı gözlem uzunluğuyla olabilirlikler hesaplanır, Akaike ağırlıkları exp(−AIC/2) normalize edilir; dizinin oranı ağırlıklı toplamdır. n < n_min ise yalnız genel.

*(d) Uzay.* Dizi içinde ana şok çekirdeği ve üye (artçı) bulutu: f(r) ∝ 1/(r²+d²), [−2R_GK, 2R_GK]² kutusuna kesilmiş ve kutuda normalize edilmiş; d = max(1 km, L/2), L Wells–Coppersmith (1994) log L = −2,44 + 0,59 M. Dizi yüzeyi (1−ω)·K_ana + ω·ortalama(K_üye), ω = n/(n+n0). Kutu hücre dışına taşarsa kütle kaybolur (yeniden normalize edilmez). Hücre kütleleri kapalı biçimdedir (atan + Gauss–Legendre).

*Tahmin.* λ(hücre, kutu) = μ·gün·KDE_hücre·GR_arkaplan(kutu) + Σ_diziler A_dizi·uzay_dizi(hücre)·[10^(−b lo) − 10^(−b hi)], A = Σ_k w_k 10^(a_k + b Mm) ∫ (t+c)^−p_k dt, dizi penceresi T_GK ile kesilir. Arka plan ile diziler toplanır.

## Hiperparametre seçimi (yalnız 2006–2010, M≥2,95 logL, ≤2005 kurulum)

Önceden listelenmiş 12 kombinasyon: Mseq ∈ {3,5; 4,0; 4,5} × n_min ∈ {8; 20} × n0 ∈ {5; 20}. En yüksek logL kazanır; eşitlikte listedeki ilk. Seçilen kombinasyon ≤2010 ile aynen yeniden kurulur (genel RJ, arka plan, KDE yeniden kestirilir); başka hiçbir ayar 2011–2015'e bakılarak değişmez.

## Ölçüm (2011–2015, yalnız defterlerden)

STEP − ETAS-LM ve STEP − R-ortak-kaskad (`U/` defterleri `$KNOTENLINIE_RUNS/defter/U/`); eşikler M≥2,95/3,95/4,95; N, Λ_aday, Λ_taban, IG, IG_olay, integral, haftalık blok SE (`blok_ozeti`), tek yönlü z, p_tek; N/S/M (`tutarlilik`, 10000 tekrar, tohum 20261005, eşik başına alt yüzey). Bileşen kabul kuralı: R-ortak-kaskad'a karşı M≥2,95'te IG>0 ve z>1,645, M≥3,95'te IG>0. Çeşitlilik: olay başına log λ'nın STEP ile R-ortak-kaskad ve ETAS-LM arasındaki Pearson ve Spearman korelasyonları (M≥2,95 ve M≥3,95 olayları, 2011–2015) ve her modelin günlük Λ'sının korelasyonu. Ek satır (Topluluk 2 kuralının E1'i, Holm uygulanmaz): eşit ağırlıklı {R-ortak-kaskad, ETAS-LM, STEP} − ETAS-LM, M≥3,95 ve M≥2,95.

**Hüküm sınırı.** M≥3,95'te z>1,645 görülse bile bu bir geliştirme penceresi ölçümüdür, kör hüküm değil; bağımsız skor-kodu incelemesine kadar PROVISIONAL.

**Kapılar.** Yalnız ≤2015 açık dosyalar; 2016+ ve 2021+ erişim yok; indirme yok; yerel makinede tek ağır süreç, ≤4 GB; defter logL farkı koşucununkiyle 1e−9 göreli içinde (testle).
