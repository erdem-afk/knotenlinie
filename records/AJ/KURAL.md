# AJ — hesap öncesi sabit kural (dallanma kısıtlı R)

Yazıldı 2026-10-12, hiçbir kısıtlı ayar kurulmadan, 2006–2010 ya da 2011–2015 AJ puanlaması yapılmadan. Sonradan değişmez;
gerekirse puanlamadan önce tarihli "Ek". Bilinenler bu yazıdan önce: R ≤2005 ayarı (S'nin `etas_s_le2005.json`) dallanma
tavanında (n = 0,999999); R ≤2010 ayarında n = 0,88; AE bütün dış bölge ayarlarının da tavanda olduğunu buldu.

**Çerçeve.** J/R çerçevesi: CSEP İtalya 8993 hücre, [0,30) km, HORUS-Mw, günlük, 0,1 M kutuları 2,95'ten, son kutu +∞. Kaskad
(32 adım, 10 nesil), KDE, b ve Mc(t) R ile aynen; yalnız MLE'nin dallanma oranı kısıtlanır. Seçim ≤2005 ayarıyla; seçilen
≤2010 ayarıyla yeniden kurulur ve 2011–2015'te bir kez puanlanır.

**Model.** R-ortak MLE'si (`tools/etas_uzun/mle.py::Olabilirlik`, dokunulmaz) üzerinde n(θ) = K c^(1−p)/(p−1) · b/(b−α) ≤ n_max.
MLE'nin n'yi doğrudan taşıyan yeniden parametrelendirmesinde (v₁ = logit n) kısıt tek bir kutu sınırıdır: v₁ ≤ logit(n_max);
öteki sınırlar R'nin sınırlarıdır. n_max = "serbest" R'nin kendi sınırıdır (n ≤ 0,999999) ve R'dir (R'nin kayıtlı x'i
başlangıçta alınınca MLE'nin yerinde kaldığı testle gösterilir). Aynı n_max hem ≤2005 hem ≤2010 ayarında kullanılır.

**Adaylar (sabit, 5).** n_max ∈ {0,6; 0,7; 0,8; 0,9; serbest}. Her kısıtlı aday iki sabit başlangıçtan ayarlanır
(R'nin ilgili x'i sınıra kırpılmış; R'nin x'inde n'si 0,9·n_max'a çekilmiş), L-BFGS-B, maksiter 300, ftol 1e-11, gtol 2e-7;
başarılı olanlardan logL'i yüksek olan alınır (hiçbiri başarılı değilse en yüksek logL alınır ve raporda işaretlenir).
Adayların kısıtlı maksimumları kutu sınırında ya da içinde olabilir; sınırda olup olmadığı raporlanır.

**Seçim.** ≤2005 ayarlı her adayın 2006–2010, M≥2,95 Poisson logL'i (log n! hariç; skor defterinden `log_olabilirlik`) en büyük olanı.
Serbest (R) aday olarak yer alır ve kazanırsa AJ = R'dir, raporda öyle yazılır. Seçilen n_max ≤2010 ile yeniden kurulur (başlangıç
R ≤2010 x'i, aynı iki-başlangıç kuralı), 2011–2015'te bir kez puanlanır. 2011–2015 sonucuna göre hiçbir şey değişmez.

**Ölçüm.** AJ − ETAS-LM ve AJ − R-ortak-kaskad, M≥2,95 / 3,95 / 4,95, U'nun ölçüm koduyla (`gunluk_u._satir`): N, Λ'lar, Λ/N,
IG, IG_olay, integral, haftalık blok SE, tek yönlü z, iki yönlü T/W, N/S/M, küme/diğer ayrımı yok (U ile aynı sütunlar).
Hüküm satırı M≥3,95 ve ETAS-LM'ye karşı; M≥2,95 geliştirme, M≥4,95 ek. Bileşen kabul kuralı: R'ye karşı
M≥2,95'te IG>0 ve z>1,645, M≥3,95'te IG>0. Parametre tablosu: R, AJ, ETAS-LM (J).
**E7**: eşit ağırlıklı {AJ'nin seçilen modeli, ETAS-LM} − ETAS-LM, M≥3,95 hüküm, M≥2,95 geliştirme; tek satır,
Holm yok. Yan satır: E7 − R.
Skor defteri `$KNOTENLINIE_RUNS/defter/AJ/` (U biçimi, `Lam495` dahil); defter logL'i koşucununkiyle 1e−9 göreli içinde eşleşir (test).

**Kayıt dışı.** Sonuç görüldükten sonra denenen her şey (başka n_max, ara değerler, başka seçim ölçütü vb.) `AJ/EK-*.md`'de
"kayıt dışı" diye durur ve hükmün yerine geçmez. Sonuç PROVISIONAL: bağımsız skor-kodu incelemesi yok.
