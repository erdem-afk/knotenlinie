# TR-10b kodlayıcı okumaları (12 Kasım 2026, veri öncesi)

Kodlayıcının, dondurulmuş ön kaydı (sürüm 2) uygularken yaptığı okumalar. Hiçbir sünme verisi açılmadan yazıldı.
Kod incelemesi her birini denetler. Ek 1 ile değişenler işaretlidir.

1. HDR uyarlaması: tablo satırı not birimidir; üç zaman damgası biçimi eklendi. (Ek 1, E1.2)
2. Tablo başlık satırları ayrı tarihsiz not kalır. (Ek 1, E1.3: bağlayıcı; "başlık katılmış" bilgi satırı)
3. "Ditto" satırları K sayılmaz, çünkü önek listesi değişmez.
4. HDR ve HDR2025 dosyaları ayrı işlenir; olaylar birleştirilir.
5. caveat.txt'de istasyon kodu sözcük sınırıyla aranır. 16 notun hiçbirinde kod geçmiyor.
6. Sayfada olmayan C461 için tarihsiz not başı 1960-01-01 alındı; listelere etkisi yok.
7. Kod B ve A listelerini §4 tablosundan okur. B_R2, A_R2 ve B1 geçmiş 5 y metinde yalnız sha256 olarak yazılı; bunlar
   dondurulmuş `tr10b_listeler.json`'dan okunur. Ön kayıt sha'sı dosyanın ilk 77114 baytı üzerinden denetlenir, böylece
   sona eklenen Ek kabul edilir.
8. MIC okuma aralığı: kodlayıcı dar okumayı ([w0 − 15 g, T + 15 g]) uyguladı. **Ek 1, E1.4 bunu değiştirir:** yalnız MIC
   kaynaklarında [w0 − 90 g, T + 90 g], üst uç 2023-10-16'yı aşamaz; dar okuma bilgi satırı. Kod buna göre düzeltilmelidir.
9. (a) denetiminde x(t)'nin zaman başlangıcı okuma aralığının başı alındı (SAYIM'ın 0,00045 doğrulaması bu başlangıçla).
   w0 başlangıcıyla doğru kod tam maskede 0,0029–0,0096 hata verir ve 0,005 eşiğini aşar; eşik evreye bağlı.
10. Boş satırlar biçim hatası sayılmaz, yalnız sayılır.
11. Aralık dışında "bozuk" sayılan yalnız < 3 alanlı satırdır; sütun 3 aralık dışında hiç ayrıştırılmaz.
12. Geçersiz tarih (yıl tam sayı değil ya da [1960, 2026] dışında, gün yılın uzunluğunu aşıyor) ⌊gün⌋ = 0 gibi koşuyu
    durdurur.
13. Dolgu tanısı: δ, okuma aralığındaki sütun 3 değerlerinde görülen en fazla ondalık basamaktan hesaplanır; aday koşular,
    uç penceresinin geçerli günlerini içeren ve uzunluğu max(15, |V|) olan pencerelerdir, okuma ızgarasıyla sınırlıdır;
    "eğimi sıfır" ölçütü |eğim| < 1e-12.
14. Düşme nedeni önceliği: K → HDR → veri bulunan ilk kaynağın ilk başarısız şartı → indirilemedi / biçim belirsiz →
    kapsam yok.
15. Menteşe modelinde yalnız (w0, T) içindeki tarihli D olayları basamak olarak girer.
16. "D dışarıda", "yalnız telemetri", "R2", "B1 5 y", "HDR uygulanmadan" ve "XDL2 dışarıda" bilgi satırlarında temsilci alt
    küme içinde yeniden seçilir. "Parkfield dışı", "T ≥ 2008" ve "dolgulu dışarıda" satırları mevcut yer-pencereleri süzer.
17. Ana satır ve A satırı N ≥ 2'de her zaman aralık alır; öteki satırlarda N < 20 ise "güç yok". A satırı A'nın kendi
    K'si ≥ 4 ise bloklu, değilse yer bootstrap'ıyla.
18. Kapı altında K ≤ 3 ise kalıptaki [L, U] yer bootstrap aralığıyla doldurulur.
19. Kapı geçmez ve kod denetimi de başarısız olursa hüküm "veri yok" olur; "geçersiz (kod)" yalnız kapı geçtiyse yazılır.
20. Düzeltme turu `--duzeltme-turu` ile verilir. Tur 0 ya da 1'de başarısızlık yalnız `tr10b_denetim_tur<N>.json` yazar
    ve çıkış 3 verir.
21. Tam maskeli bilgi paydası: yer-pencere başına ⌈20000/n⌉ çekiliş, tohum 20261112+2.
22. 144 satırlık denetim bütün 10MIN yer-pencerelerinde yapılır; 10MIN yer-penceresi yoksa 2013 tam maskeli yapay
    pencere kullanılır.
23. README N0 çekilişleri FFT ile yapılır; `pl_seri` ile 1e-9 içinde eşit (sınandı).
24. Biçim belirsiz dosyalar koşudan önce `--bicim-belirsiz` ile verilir.

Kodlayıcının işaretlediği riskli yerler: `oku_dosya` (durma şartları, aralık denetimi, erken `break` olmaması);
`man_sart` / `_man_braket`; `istasyon_penceresi` ve `temsilci`; `pk_gercek` (gerçek Δv'nin hiçbir yere yazılmaması);
işaret dosyalarından sonra istisna tek koşuyu tüketir (bootstrap ve hüküm kurulumu işaretlerden sonra koşuyor);
`bootstrap` (ağırlıklı nicelik, ρ_R paydası); hüküm kalıbı dizgeleri; `dolgu`; `tr10b_hdr.py` düzenli ifadeleri;
`tr10b_indir.py` (tek yeniden deneme turu, manifestin bir kez yazılması).
