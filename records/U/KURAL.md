# U — hesap öncesi sabit kural

Bu dosya, 2011–2015 defterleri üretilmeden ve hiçbir topluluk 2011–2015'te puanlanmadan yazıldı. 2006–2010 defterleri de henüz üretilmemişti. Sonuçtan sonra değişmez; SHA256'sı `OLCUM.json` ve `AGIRLIK.json` içinde kayıtlıdır.

**Skor zinciri.** Beş modelin 2006–2010 ve 2011–2015 günlük tahminleri → skor defteri → 2006–2010'da M≥2,95 logL'iyle seçilen simplex ağırlıkları → 2011–2015'te topluluk − ETAS-LM (M≥3,95 hüküm, M≥2,95 geliştirme) ve topluluk − R-ortak-kaskad.

**Çerçeve.** J/R çerçevesi: CSEP İtalya 8993 hücre, [0,30) km, HORUS-Mw, günlük, 0,1 M kutuları (2,95'ten 8,95'e, son kutu +∞), her UTC günü yalnız gün başından önceki olaylar geçmişte. Eşikler M≥2,95 (geliştirme), M≥3,95 (hüküm), M≥4,95 (ek).

**Modeller ve kurulum sonları.**

- *2006–2010 (son=2006).* R-ortak-kaskad: S'nin ≤2005 ayarı (`etas_s_le2005.json`). R-lm-kaskad: aynı akışla (S/KURAL, `tools/etas_uzun/olcek.kur`) LM biçimli çekirdek (γ=0), ≤2005 MLE. ortak-ETAS: `ayar_tabani("italya", son="2006-01-01")`. N-ortak-kaskad: N'nin Mc=2,5 tamlık kuralı ≤2005 kataloğa uygulanır (kabul edilen en uzun son blok: yalnız 2005, 321 olay), ortak çekirdek MLE, KDE 2005 içi yarı bölmeyle, 32 adım/10 nesil kaskad. ETAS-LM: Tablo 1 sabitleri; arka plan Eq.3, 1985–2004 M≥3,1 ve 2005 M≥2,5 olayları, her Mc=3,1 olayı 10^(Mc−2,5) ağırlıkla (b_ref=1, eksik alt-M temsili), 10. komşu ve en az 1,1 km bant (J'nin varsayımı aynen); tetikleme geçmişi 2005-01-01'den (Mc=2,5 tamlığının başladığı yıl).
- *2011–2015 (son=2011).* R/S/J/N'deki ≤2010 kurulumları aynen: `etas_ortak.json`, `etas_lm.json`, J'nin ETASLM'i (2005-04-16 başlangıcı), `mc25/etas_ortak.json` kaskadı, `ayar_tabani("italya", son="2011-01-01")`.
- *ortak-ETAS M<3,1.* Taban Mc=3,1'dir. 2,95–3,15 kutuları için tabanın [Mc,+∞) hücre oranı kendi b'siyle GR ile uzatılır (`GrUzat`); Mc üstündeki kutular tabanın kendi çıktısıyla birebir aynıdır. ortak-ETAS topluluk üyesidir, hüküm referansı değildir.

**Üç topluluk (sabit).** T1 = {R-ortak-kaskad, ETAS-LM}; T2 = {R-ortak-kaskad, ortak-ETAS, N-ortak-kaskad} (LM'siz); T3 = beş modelin hepsi. Başka topluluk, alt küme ya da varyant eklenmez; üyeyi ağırlığı sıfıra inen modelden ayıklamak da yoktur.

**Ağırlık kuralı.** λ = Σ w_k λ_k, w simplex üstünde (w_k ≥ 0, Σ w_k = 1), 2006–2010 M≥2,95 Poisson logL'ini en büyükleyen (SLSQP, başlangıç eşit ağırlık). Eşit ağırlık önceden yazılmış ikinci satırdır. Birincil satır en-iyi ağırlıklı topluluktur; eşit ağırlık duyarlılık satırıdır. Ağırlıklar 2006–2010 defterleri üretilince `AGIRLIK.json`'a yazılır, 2011–2015 defterleri ondan sonra üretilir ve ağırlıklar 2011–2015 sonucuna göre değişmez. Başka hiçbir ayar, eşik ya da varyant seçimi 2011–2015'e bakılarak yapılmaz.

**Ölçüm (2011–2015, yalnız defterlerden).** Her topluluk (iki ağırlık kuralı) − ETAS-LM ve − R-ortak-kaskad; eşikler M≥2,95, M≥3,95, M≥4,95 (ek). Raporlanan: N, Λ_aday, Λ_taban, IG, IG_olay, integral, haftalık blok SE'si (`blok_ozeti`) ve tek yönlü z, p_tek; iki yönlü eşleştirilmiş T/W ek tanı olarak. N/S/M: N iki Poisson kuyruğu, S ve M tek alt kuyruk, 10000 tekrar, tohum 20261005/20261006; test eşik başına o eşiğin alt yüzeyinde yapılır. Holm: her (eşik, taban, ağırlık kuralı) için üç topluluk üstünde, p_tek ile. Üyelerin tek başına satırları (model − ETAS-LM, model − R) bileşen bağlamı içindir.

**Tanı satırı (seçim için kullanılmaz).** R-ortak-kaskad yüzeyi c = Λ_LM/Λ_R (2006–2010 defterlerinden, eşik başına) ile çarpılıp ETAS-LM'ye karşı IG ve z.

**Bileşen kabul kuralı**: bir bileşen, 2011–2015'te R-ortak-kaskad'a karşı M≥2,95'te IG>0 ve z>1,645, M≥3,95'te IG>0 verirse finalist modele girer. Hüküm satırı ETAS-LM'ye karşıdır: birincil T1/T2/T3 − ETAS-LM, M≥3,95. M≥3,95'te z>1,645 olan topluluk "ETAS-LM'yi geçti" ilan edilmez; bu bir geliştirme penceresi ölçümüdür (kör hüküm değil) ve bağımsız skor-kodu incelemesine kadar PROVISIONAL'dır.

**Kapılar.** Yalnız ≤2015 açık dosyalar. 2016+ ve 2021+ erişim yok. Yeni indirme yok. Yerel makinede tek ağır süreç, ≤4 GB. Defter logL farkı koşucununkiyle 1e−9 göreli içinde eşleşmek zorundadır (testle gösterilir).
