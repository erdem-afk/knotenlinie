# 1 Ocak 2027 ileri testi: eksikler ve genişletme listesi (17 Kasım 2026)

Kaynak: sunucuda salt okuma denetimi (0 €, hiçbir şey değiştirilmedi, kör veriye bakılmadı; ayrıntılı envanter knotenlinie-depo `/tmp/ileri-test-envanter-2026-11-17.md`), panel, `kayit/adaylar.jsonl` (100 satır). Güç ve süre sayıları tahmindir.

## Kısa cevap

Evet, bir şey kaçırıyoruz. Mühimmatın neredeyse tamamı Marmara M7+ defterinde (19 dondurulmuş model), ama orada yıllık olasılık ≈%1 olduğundan olaysız bir yıl modeller arasında ≈0,001 nat fark üretir; bu defter tek başına onlarca yıl hüküm veremez. Hüküm verebilecek yer (Türkiye geneli M4+, Marmara M5+/M6+) için 2027'ye dondurulmuş tahmin yok. Ayrıca canlı günlük tahminler dışarıdan damgalanmıyor, yani "olaydan önce verildi" bugün kanıtlanamaz.

## Sağlam olanlar

- Marmara M7+ defteri: 19 model dondurulmuş, tahmin dosyaları diskte, sha'lar tutuyor, OTS'lerin hepsi Bitcoin onaylı. Hedef: 5 segment + deniz / İstanbul / hepsi, 1 / 5 / 30 yıl, Mw ≥ 7.
- Küresel RAPOR-5 (2027–2034): dondurulmuş, OTS'li, kuru açılış geçti, Zenodo'da.
- Canlı hatlar (nokta ETAS, Bayes ETAS, CRS+ETAS) 10–17 Kasım her gün hatasız; site dışı yedek her gün başarılı ve canlı çıktıları kapsıyor.

## A. Altyapı açıkları (yeni model değil; 1 Ocak'tan önce kapanmalı)

| # | Açık | Neden önemli | Maliyet / süre |
|---|---|---|---|
| A1 | Canlı günlük çıktılar damgalanmıyor (OTS yok, commit yok); katalog anlık görüntüsü kuralı yok | Damgasız tahmin ileri test kanıtı sayılmaz | 0 €, 1 gün |
| A2 | Referans modeller (Poisson/durağan taban, GEAR1) canlıda aynı biçimde yazılmıyor | Rakip olmadan kazanç hesaplanamaz | 0 €, 1–2 gün |
| A3 | Puanlama kodu `tools/canli/defter.py` son haliyle dondurulmamış; 19 modelle kuru koşu yok; GCMT okuyucusu ve canlı ETAS yıllık puanlama kodu yok | Puanlama kodu veriden sonra yazılırsa sonuç tartışmalı olur | 0 €, 3–4 gün + bağımsız inceleme |
| A4 | Marmara M7+ için hüküm, anlamlılık, durma ve çoklu karşılaştırma kuralı yazılı değil. Tanımsız: v2 ailesi 6 segment (İmralı dahil), gözlem bölgesi 5 segment; episantr mı sentroid mi; derinlik türü; büyüklük ajansı; çok segmentli kırılmanın segmentlere atanması | Olaydan sonra tanımlanan her şey geriye dönük tartışma yaratır | 0 €, 2–3 gün (ön kayıt eki + OTS) |
| A5 | `tools/marmara/teyit2026.py` (Türkiye dışı 2026 okuyucusu) yazılmamış; 5 Ocak'tan önce kod + inceleme + dondurma gerekli | Tek kalan geçmiş kör veri | 0 €, 2–3 gün |
| A6 | 31 OTS pending (Marmara defteri dışı); timer'larda başarısızlık uyarısı yok | Sessiz kesinti kayıp gün demek | 0 €, yarım gün |

## B. Genişletme seçenekleri (yeni tahmin satırları; seçim Erdem'in)

| # | Ne | Ne ekler | Maliyet / süre | Kör/sızıntı riski | 1 Ocak'a yetişir mi |
|---|---|---|---|---|---|
| B1 | **Türkiye geneli ızgara ileri testi.** M4+ hüküm satırı, M5+ ikinci, M6+ bilgi; 1 gün / 7 gün / 3 ay / 1 yıl; modeller H, düz ETAS, Marmara tipi ETAS; rakip GEAR1 ve Poisson | Hüküm verebilecek tek yer. Mühür sınavında 10 yılda N 883 idi; 1 yılda ≈80–90 hedef, ≈0,2 nat fark görülebilir (tahmin), 3 yılda ≈0,1 | 0–5 €, 1–2 hafta | Düşük. 1 Ocak öncesi her Türkiye verisi artık geliştirme verisi; Türkiye dışı 2026'ya dokunulmaz | Evet |
| B2 | **Marmara ara hedefler** M5+ / M5,5+ / M6+, 1 ve 5 yıl; dondurulmuş modellerden türetilir, yeni fizik yok | M7+'a göre onlarca kat fazla gözlem; Erdem'in "M7 olmazsa M6" hedefiyle aynı | 0 €, 3–4 gün | Düşük; v1.3b değişmez, ek hedef satırı olarak dondurulur | Evet |
| B3 | ETAS + EEPAS karışımı Türkiye rakibi (TK-1 bilgi satırı: karışım − ETAS +0,243 ± 0,087) | Orta vadede (1–5 yıl) tek pozitif işaret; ileri test bunu gerçekten sınar | 0 €, 2–3 gün | Düşük; kazancın kaynağı hız ölçeklemesi olabilir, ön kayıtta yazılır | Evet |
| B4 | Dış referanslar: ESHM20 ve Türkiye 2018 tehlike modeli oranları rakip satır | Mühürde sızıntı yüzünden rakip olamıyorlardı; ileri testte olabilirler. "Resmî modeli geçiyor muyuz" sorusunun tek dürüst cevabı | 0 €, 3–5 gün | Yok (ileriye dönük). Oran dosyalarının açık erişimi doğrulanmadı | Büyük olasılıkla |
| B5 | Topluluk satırı (eşit ağırlıklı ve doğrulama ağırlıklı ortalama), Marmara ve Türkiye | Çoğu ileri testte topluluk tek modeli geçer; ucuz sigorta. Geçmiş veride istif H0 çıkmıştı | 0 €, 1 gün | Yok | Evet |
| B6 | Analog bölgelerde canlı kısa vade (Kaliforniya, İtalya, Yeni Zelanda) | Daha çok olay, yöntemin genel sınavı; Türkiye hedefine katkısı dolaylı. Uzun vadeyi RAPOR-5 zaten kapsıyor | 5–15 €, 1–2 hafta | Türkiye dışı 2026 penceresiyle çakışma riski: ancak 5 Ocak'tan sonra kurulmalı | Hayır (bilerek sonraya) |
| B7 | Skorsuz gölge satırlar: b-pozitif trafik ışığı (TK-2), Güvercin–Barbot Marmara döngü modeli (FA-3) | Güç yok; yalnız kayıt değeri | 0 €, 2 gün | Yok | Evet |

## Öneri

A grubunun tamamı (seçim gerektirmiyor, başlatılıyor). B'den B1 + B2 + B4 + B5: hüküm gücünü M4+ ve M5–M6 hedeflerine taşır, resmî modeli rakip yapar, topluluk satırını ekler. B3 isteğe bağlı (ucuz, ama pozitif işaretin kaynağı şüpheli). B6 5 Ocak'tan sonraya. B7 önemsiz.

Hepsi ön kayıt + bağımsız inceleme + OTS ile dondurulur; v1.3b ve mevcut 19 model değişmez. Marmara olasılıkları yalnız depoda kalır; dışarıya yalnız parmak izi çıkar.
