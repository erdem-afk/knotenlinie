# Kapı eşikleri neye dayanıyor? (16 Kasım 2026; Erdem'in sorusu üzerine)

Kısa cevap: eşiklerin **mekanizması** hesap (tek yanlı α = 0,05, güç 0,80; kesin binom ya da sıra ölçüsü), ama hesaba
giren **etki büyüklüğü literatürden değil, bizim "orta büyüklükte etki" seçimimizden** geliyor. Çünkü bu soruların
hiçbirinde doğrulanmış bir etki büyüklüğü yayımlanmamış (TR-12: 12 öncül iddiadan ölçülen tabanın üstünde doğrulanan
0). "K ≥ 20" bu seçimin karşılığıdır ve beş adayda aynen kullanıldı; ayrıca "kaba sayım gerçek veride 3–5 kat
küçülüyor" payı içerir. Gereken olay sayısı ≈ 1/etki² ile ölçeklenir: etki 2 kat büyük varsayılsaydı kapı ≈ 6–8, yarısı
varsayılsaydı ≈ 75–80 olurdu.

"Güç yok" ne demek: o sayıyla **olumsuz sonuç bilgi taşımaz** (etki var da olsa göremeyebilirdik). Büyük bir etki yine
görülebilirdi. Yani kapı altında kalan aday "yanlış" değil, "bu veriyle ancak büyük etki sınanır" durumundadır.

| Aday | Kapı | Varsayılan etki ve kaynağı | α / güç | Bulunan | Etki ×2 olsaydı | Etki ×0,5 olsaydı | Elemenin dayanağı |
|---|---|---|---|---|---|---|---|
| TR-1 GNSS hız değişimi öncülü | K ≥ 20 küme | Olay, 10 kontrol arasında sıra ölçüsü; ölçülebilir en küçük AUC 0,68 (δ ≈ 0,65 σ). **Tahmin** (literatürde değer yok) | 0,05 / 0,8 | 11–12 (AUC ≥ 0,73 görülür) | kapı ≈ 6 → geçerdi | ≈ 77 → geçmez | **Varsayıma bağlı.** Ayrıca plasebo 3 olay (gereken 10) ve postsismik kirlenme: bunlar varsayımdan bağımsız |
| TR-2 sonraki M≥6'nın yönü | K ≥ 30 ve görülebilir isabet oranı ≤ 0,70 | 0,5'e karşı 0,70; **tahmin** ("büyük etki") | 0,05 / 0,8 | 40 → koşuldu, H0 (15/40) | – | 0,60 için K ≈ 150 gerekirdi | Koşuldu. "Büyük etki yok" sağlam; küçük etki (0,5–0,6) dışlanmadı |
| TR-3 komşu segment gecikmesi | resmî kapı yok (kaba sayım) | – | – | 10 çift (kıta içi 1) | – | – | **Kaba hesap; resmî güç hesabı yapılmadı** |
| TR-5 / TR-5b sismik hız öncülü | K ≥ 20 ve plasebo ≥ 10 | AUC 0,68 (δ 0,65 σ); tam kuralla δ 1,16 σ. **Tahmin**; kıyas: bir M6'nın deprem anındaki düşüşünün ≈ 1,5 katı | 0,05 / 0,8 | 18 ve 7 | geçerdi | geçmez | **Varsayıma bağlı, 2 olayla kaldı.** 18 kümeyle görülebilir en küçük etki 0,68 σ, 20 ile 0,65 σ: fark anlamsız. Asıl engel maliyet (≈ 2 TB, 6 hafta sunucu) ve plasebo sayısı |
| TR-6a gerilme ölçer kör doğrulama | K ≥ 23 | Gölge lobunda "düşüş oyu" 0,5'e karşı 0,75. **Tahmin** (0,70 → 37; 0,80 → 18) | 0,05 / 0,8 | 29 → kapı geçti | geçer | geçmez (37–90) | Kapıdan değil, yapay yöntem sınamasından kaldı |
| TR-6 (b) Marmara çözünürlüğü | algılanabilir ≤ beklenen sinyal | Beklenen ≤ 6,5 kPa/yıl: **kuram/model** (yavaş kayma gerilmesi); algılanabilir 15–134: katalogdan ölçüm | 0,05 / 0,8 | 2,4–20 kat eksik | yalnız en iyi hücrede sınırda | geçmez | Büyük ölçüde sağlam |
| TR-7 tetiklenmiş tremor | segment başına ≥ 8 tetikleyici, ≥ 2 kPa | Eşik 2 kPa: **literatür** (Parkfield tetiklenme eşiği, Peng 2009; Hill 2013). 8: yanlış alarm oranından binom | 0,05 | 9–12 → geçti | – | ×1/3'te 5–6 (zayıf bant) | Kapıdan değil, pozitif kontrolden kaldı |
| TR-7b ayıklama kuralı | yapay atılma ≤ 0,05, 100 pencere | **Bizim seçimimiz** | – | 0,06 (dört tohumdan birinde) | – | – | **Varsayıma bağlı.** 100 pencere 0,03 ile 0,06'yı ayıramaz |
| TR-8 uydu gravitesi | çözünürlük | Fiziksel: GRACE'in çözdüğü en küçük moment Mw 7'nin 125 katı (**literatür**) | – | 125 kat eksik | geçmez | geçmez | Sağlam |
| TR-9 artçı ucu ile kilitlenme sınırı | K ≥ 20 | İsabet 0,2'ye karşı 0,5; **tahmin** | 0,05 / 0,87 | 4–6 | 0,2'ye karşı 0,8 olsa K ≈ 7 → yine sınırda/geçmez | geçmez | Sağlam (veri yok) |
| TR-10 sünme hızı → yakın M≥6 | K ≥ 20 | İsabet 0,1'e karşı 0,3; **tahmin** | 0,05 / 0,76 | 17; açık veriyle 3 | 17 ile geçerdi, 3 ile geçmez | geçmez | Açık veri engeli sağlam; 20 sayısı varsayım |
| TR-10b sünme ölçer tabanı | ≥ 20 yer, ≥ 40 pencere | Etki yok; %95 değerini kestirmek için kuyrukta ≥ 2 gözlem. **Uzlaşım** | – | 8 yer, 11 pencere | – | – | **Uzlaşıma bağlı**; sayı yine de bilgi satırı olarak yazıldı (3,41 mm/yıl) |
| TR-11 GNSS tabanı | ölçüm, olay kapısı yok | – | – | 665 pencere | – | – | Koşuldu |
| TR-12 yayımlanmış GNSS iddiaları | literatür tablosu | – | – | tabanın üstünde doğrulanan 0 | – | – | Koşuldu |
| TR-13 sismisite yerelleşmesi | K ≥ 20 | Arka plan olaylarının %20'si kırık bandına toplanır: **benzetimden hesap**, makullüğü doğrulanamadı (kaynak okunamadı) | 0,05 / 0,8 | 11–20; kontrol eşleşince 3–7 | kapı ≈ 6–8 → kontrolsüz geçerdi | geçmez | **Varsayıma bağlı.** Ayrıca yanlış alarm oranı %13–37 (anma %5): varsayımdan bağımsız kusur |
| TR-4 Marmara hız tabanı | dönem başına ≥ 10 yer | Etki yok; taban genişliğinin güven aralığı için. **Benzetimden** | – | 9–16 → geçti | – | – | Sürüyor |

## Dürüst özet

1. Ezbere olan kısım: "orta büyüklükte etki" ve ondan çıkan 20. Literatür bize sayı vermedi; biz koyduk ve beş adayda
   aynısını kullandık.
2. Varsayıma bağlı kalan "güç yok" hükümleri: **TR-1, TR-5b, TR-13, TR-10b, TR-7b** (ve 20 sayısı bakımından TR-10).
   Varsayımdan bağımsız sağlam olanlar: TR-8, TR-9, TR-6 (b), TR-10'un açık veri engeli.
3. Sonuç değişir miydi: etkiyi 2 kat büyük varsaysaydık TR-1, TR-5b ve TR-13 kapıyı geçer, koşulurdu. Ama o zaman
   yalnız çok büyük bir etkiyi görebilirdik; "görülmedi" sonucu yine bilgi taşımazdı.
4. Düzeltme: kapıyı "geç / kal" yerine "bu sayıyla görülebilir en küçük etki şudur" diye yazıp, yalnız büyük etkiye
   bakan sınırlı koşular yapmak. Bu, TR-1 ve TR-13 için 0 € ile mümkün; ikisinin de varsayımdan bağımsız kusurları
   (plasebo eksikliği, yanlış alarm oranı) ön kayıtta ayrıca çözülmeli. TR-5b sunucu ister.
