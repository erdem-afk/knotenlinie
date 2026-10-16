# AB — hesap öncesi sabit kural (ML üyesi)

Yazıldı 2026-10-12, hiçbir 2006–2010 ya da 2011–2015 ML puanlaması yapılmadan. Sonradan değişmez; gerekirse puanlamadan önce tarihli "Ek".

**Çerçeve.** J/R çerçevesi (CSEP İtalya 8993 hücre, [0,30) km, HORUS-Mw, günlük, 0,1 M kutuları 2,95'ten, son kutu +∞). Seçim: ≤2005 eğit, 2006–2010 M≥2,95 logL. Seçilen ≤2010 ile yeniden eğitilir, 2011–2015'te bir kez puanlanır.

**Model.** `HistGradientBoostingRegressor(loss='poisson')`, hücre-gün başına M≥3,1 olay oranı μ. M≥2,95 kutularına GR ile dağıtım: kutu payı 10^(−b(alt−3,1)) − 10^(−b(üst−3,1)); b = R-ortak-kaskad ayar dosyasının b'si (≤2005: `etas_s_le2005.json`; ≤2010: `etas_ortak.json`). ortak-ETAS GrUzat ile aynı yasa.

**İlk tasarımdan sapmalar (gerekçeli).** (1) Özellik eşikleri M≥2,5/3,5 yerine **M≥3,1/3,5**: 2005 öncesi katalog M<3,1'de eksik; 2,5 sayımı eğitimde (≤2005) ve puanlamada (2006+) farklı anlam taşırdı. Hedef de aynı nedenle M≥3,1 (eksiklik çözümü: hedef eşiğini Mc'ye çek, GR ile 2,95'e ölçekle). (2) Eğitim **1995**'ten başlar (1985 HORUS başlangıcı + 10 yıllık pencere). (3) Arka plan KDE (20 km Gauss, M≥3,1) eğitim satırlarında yıl%4 katlı çapraz-uyumla (satırın kendi olayı yoğunluğa girmez); 2006+ günlerde tam ≤ayar KDE'si. (4) Eğitim ağırlıkları ortalama 1'e ölçeklenir (Poisson Newton kararlılığı; ön deneyde ölçeksiz 5x aşırı tahmin).

**Özellikler.** 30 sayım (yarıçap 10/30/100 km × eşik 3,1/3,5 × pencere 1/7/30/365/3650 gün), 50 km içinde son 30 günün en büyük M'si ve yaşı, en yakın M≥4,5 olayın uzaklığı ve yaşı, KDE log oranı. ML-artık: + log(R-ortak-kaskad M≥3,1 hücre-gün oranı) (≤2005 ayarı seçimde, ≤2010 ayarı son kurulumda). Hücre koordinatı özellik değildir.

**Eğitim örneklemesi.** Pozitif hücre-günlerin hepsi (ağırlık 1); günlerin p=0,25'i rastgele seçilir (tohum 20261012) ve o günlerde sıfır hücrelerin q=0,25'i (ağırlık 1/(pq)=16). Olay günleri her halükarda hesaplanır.

**Aday kümesi (sabit, 8).** Varyant ∈ {ML-saf, ML-artık} × K1 (lr .05, yaprak 8, 200 iterasyon, min_yaprak 400), K2 (lr .05, 16, 200, 400), K3 (lr .1, 8, 100, 400), K4 (lr .1, 16, 100, 400); l2=1.

**Seçim kuralı.** 2006–2010 M≥2,95 Poisson logL'i en büyük aday. Seçilen ≤2010 verisiyle aynı ayarlarla yeniden eğitilir (iterasyon sayısı değişmez). 2011–2015 sonucuna göre hiçbir şey değişmez.

**Ölçüm.** ML − ETAS-LM ve − R-ortak-kaskad, M≥2,95/3,95/4,95, U'nun ölçüm koduyla (IG, haftalık blok SE, tek yönlü z, N/S/M); ML'nin olay başına log λ'sının R ve LM ile korelasyonu; özellik önemi (2006–2010 örneğinde permütasyon). Bileşen kabul kuralı bütün deneylerde ortaktır. Sonuç PROVISIONAL (bağımsız skor incelemesi yok).
