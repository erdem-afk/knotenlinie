# S — hesap öncesi sabit kural

Bu dosya, S'nin geçmiş ölçek hesabı ve 2011–2015 ölçümü çalıştırılmadan yazıldı.
Skor zinciri: R-ortak ETAS → geçmiş toplam oran kalibrasyonu → J günlük çerçevesi → ETAS-LM bilgi kazancı.

**Öğrenme:** 1985–2004 Mc=3,1; 2005 Mc=2,5, HORUS-Mw, [0,30) km. R ile aynı CSEP maskesi, maskenin dışındaki dikdörtgen ebeveynler, Mc(t) kompansatörü, b MLE'si ve iki deterministik başlangıçlı ortak-çekirdek MLE (maksiter=300). KDE adayları R'nin BANTLAR_KM/ZEMIN_PAYLARI: <2001 kurulum, 2001–2005 konumsal log-olabilirlikle seçim, <2006 yeniden kurulum. Hiçbir 2006+ olay parametre/KDE/b ayarına girmez.

**Ölçek:** <2006 donmuş modelle 2006-01-01–2011-01-01 günlük tahmin; M≥3,95, J maskesi ve [0,30) km. Her gün yalnız kesin gün-başı öncesi gözlenen ebeveynler. Kaskad için 32 zaman adımı/10 ek nesil, kaskadsız için 0 ek nesil; aynı parametreler kullanılır.

Her yöntem için c_tüm=N_tüm/Λ_tüm ve c_dış=N_dış/Λ_dış. Dış, [13;13,8]°E×[42;42,6]°N L'Aquila kutusu hariç demektir: olayda kapalı uçlar, integralde bu sınırlarla hizalı bütün hücreler çıkarılır (uçların alanı sıfırdır). Dışlama yalnız kalibrasyon N/Λ hesabındadır; ebeveynler ve kaskad desteği çıkarılmaz. **Ana c=√(c_tüm×c_dış)**. Kaskadsızın c_kaskadsız değeri aynı kuralla ayrı hesaplanır. Sıfır/geçersiz N veya Λ kapıyı kapatır; alternatif ölçek seçilmez. Ölçek bütün son tahmin yüzeyine uygulanır, μ/K veya dallanmayı yeniden ayarlamaz.

**Dört sabit varyant:** (a) R-ortak-kaskad; (b) R-ortak-kaskad×c; (c) R-ortak-kaskadsız; (d) R-ortak-kaskadsız×c_kaskadsız. <2011 parametreleri mevcut R-ortak ayarından aynen alınır. Ölçekler S/OLCEK.json'a yazılıp sabitlenmeden doğrulama koşusu başlatılmaz. 2011–2015 sonucuna göre hiçbir ayar/varyant değişmez; bu pencerenin N/Λ oranı ölçek seçiminde kullanılmaz.

**Ölçüm:** J'nin 2011-01-01–2016-01-01 (üst uç hariç) günlük çerçevesi; M≥3,95 ana, M≥4,95 ek, 0,1 M kutuları, son kutu +∞, 8993 CSEP hücresi. Her varyant − ETAS-LM ve − ortak ETAS: N, Λ, Λ/N, IG, SE, iki yönlü p_T/p_W, N/S/M. S/M=10000 multinomial, tohum=20261005/20261006; N analitik iki Poisson kuyruğu. Holm her eşik/referans/T-W için dört sabit varyant üzerinde; ek eşik keşifseldir. Küme ayrımı J/H4: hemen önceki M≥4,5 olay, ≤30 gün/50 km; integral gruplara dağıtılmaz. Adaptif tahminin N/S/M testleri operasyonel tanıdır; T/W olay-bağımsızlığı varsayımı ihtiyatla okunur.

Yalnız ≤2015 açık dosyalar; kalibrasyon aşamasında ham dosya listesi ≤2010 ile sınırlıdır. 2016+ erişim, yeni indirme, commit/push ve bırakılan arka süreç yok. Skor kodu bağımsız incelemeye kadar PROVISIONAL.
