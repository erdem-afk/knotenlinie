# Knotenlinie paneli: iç denetim (11 Kasım 2026)

**Kapsam:** `panel/` altındaki index.html (Yol haritası), rapor.html (Durum raporu), kiyas.html (Kıyas tablosu; DEFTER ve SEYIR JSON blokları ayrıştırıldı), kurulum.html, yol.html. Karşılaştırma: `/tmp/claude/memory/team/silo/*.md`. Dosyaların hiçbiri değiştirilmedi. `panel/hashes.json` ve `panel/rest.txt` panel dosyası değil, çağıranın yardımcı dosyaları; yalnız hash eşleştirmesi için kullanıldı.

**Yöntem:** id/href/data-id taraması (betik), yinelenen id, etiket dengesi, yol.html ↔ index.html satır farkı, hafızadaki 90 civarı commit hash'inin paneldeki bağlamla karşılaştırılması, tüm Marmara/İstanbul ve yüzde ifadelerinin taranması, DEFTER'in (752 satır) tarih ve bölge dökümü. Satır numaraları dosyanın kendi satırları. index.html'de satırlar çok uzun, alıntı o satırın içinden.

**Etiketler:** "açık hata" = metin kendi içinde ya da güncel kayıtla açıkça çelişiyor, önerilen düzeltme verildi. "yoruma açık" = iki okuma mümkün ya da hangisinin doğru olduğunu ben doğrulayamıyorum.

---

## 1. Yapı

### Y1 · YÜKSEK · Sekme gezintisi hiç yok; index.html öteki dosyalara bağlanmıyor
- Beş dosyanın hiçbirinde başka bir panel dosyasına bağlantı yok (`rapor.html`, `kiyas.html`, `kurulum.html`, `yol.html` dizgeleri hiçbir href'te, iframe'de ya da JS'de geçmiyor). index.html'deki tek dış bağlantı Google Fonts.
- Panel metni ise sekme varmış gibi yazıyor: index.html 231 "Durum raporu ve Kıyas tablosu **sekmeleri** 9 Kasım'a güncellendi", 489 "Ayrıntı **Kurulum sekmesinde**", 649 "Kurulum sekmesi 7 Kasım anlık görüntüsüdür"; rapor.html 229 civarı (Özet) "Ayrıntı **ana sayfada**, 'Açılmış veri envanteri' bölümünde". Hafıza MEMORY.md 4: "sekmeler: Durum raporu, Kıyas tablosu, Kurulum, Yol haritası".
- Sonuç: yayımlanan artifact'ın ana sayfasını açan kişi öteki üç sekmeye ulaşamaz.
- **Açık hata.** Düzeltme: index.html'in başına (ve diğer üç sayfaya) dört bağlantılı ortak bir sekme şeridi eklemek: `<nav><a href="rapor.html">Durum raporu</a> <a href="kiyas.html">Kıyas tablosu</a> <a href="kurulum.html">Kurulum</a> <a href="index.html">Yol haritası</a></nav>`.

### Y2 · ORTA · yol.html, index.html'in 7 Kasım sürümü; tabloda beşinci, erişilemeyen ve eskimiş bir sayfa
- Satır farkı: yol.html'deki 576 satırın 563'ü index.html'de aynen var. Ayrılan 13 satırın hepsi 7 Kasım planı: C "≈15 Kasım" mühür, E "20–31 Aralık", "Küresel ön kayıt (RAPOR-5) 15 Aralık dondurması sürer", ladder "dondurma 15 Aralık", hk1 notu "Başlamadı. En geç 23 Kasım'da başlamalı", "Türkiye, 2016 ve sonrası: mühürlü". index.html bunlara ek olarak 270 civarı yeni satır içeriyor (yıl ölçeği, literatür, envanter, demir, kilit-yollar, araştırma, Bayes ETAS, derive).
- İki dosyanın `<title>`'ı da "Yol haritası". Bağlantı yok, ama dosya yayımlanmış durumda. Biri sekme şeridi eklerken yanlışlıkla yol.html'e bağlarsa okuyucu 7 Kasım planını görür.
- **Yoruma açık** (silinmesi mi, "arşiv: 7 Kasım" diye etiketlenmesi mi gerektiği ekibin kararı). Önerim: yayımdan kaldırmak ya da başlığı "Yol haritası (7 Kasım arşivi)" yapmak.

### Y3 · DÜŞÜK · index.html çift sarmalanmış belge
- 1. satırda tam bir `<!doctype html><html><head>…</head><body>` iskeleti var, 2–882 satırlarda ikinci bir `<!doctype html><html lang="tr"><head>…<title>` ile ayrı bir tam belge, 884'te `</body></html>`. İki doctype, iç içe html/head/body var: HTML olarak geçersiz. Tarayıcılar hoşgörüyle işliyor, başlık da gösteriliyor. kiyas.html aynı iskeleti kullanıyor ama içinde yalnız gövde parçası var, orada sorun yok.
- **Yoruma açık:** dosya büyük olasılıkla yayımlanmış hâliyle indirildi ve iskeleti yayım katmanı ekledi. Kaynak dosyada 1. ve 884. satırlar yoksa sorun yok.

### Y4 · DÜŞÜK · İç çapalar ve id'ler: kırık yok
- Statik `href="#…"` çapalarının hepsi aynı dosyada karşılığını buluyor (index 13, rapor 10, yol 6 farklı çapa).
- JS data-id başvuruları (index.html 836–877): P aşamalarındaki ve Y yolundaki hk1, hk2, hk3, hk4, hk5, hk6, hk7, bb1–bb6 maddelerinin hepsi M dizisinde tanımlı. `bag` alanındaki kimlikler `byId` ile süzülüyor. Kırık başvuru yok.
- "Yinelenen id" çıktısındaki `${m.id}` ve `${id}` yalnız şablon dizgeleri (796/877, 809/863), çalışma anında farklı değer alıyor. Gerçek yineleme yok.
- Atlama menüsü (index.html 457–471) içeriğin başında değil, sonunda (yıl-ölçeği…derive kutularından sonra). #turkiye, #literatur ve #derive-* alt kutuları menüde yok. Kozmetik, düşük.
- kiyas.html'deki dört iç sekme (Kıyas / Mühür / İlerleme / Sıra) çalışıyor. Ama 264 "Sırada ne olduğu **'Sonraki adımlar'** sekmesinde" diyor, sekmenin adı "Sıra". **Açık hata.** Düzeltme: "'Sıra' sekmesinde".

---

## 2. Aynı sayının ya da olgunun farklı yazılması

### T1 · YÜKSEK · İleri test defterindeki sürüm sayısı dört farklı değer alıyor
- index.html 172 (E hücresi): "İleri test defteri **8 sürüm**: v1.3b (NİHAİ), v1.3, v1, v2, v1.4, v2.1, v1.5, v2.2".
- index.html 269: "İleri test defteri **10 sürüm**".
- index.html 376 (D5 kartı): "defterdeki **10+ sürüm**".
- index.html 384 (D5 sonucu): "**17 sürümün** eşit ağırlıklı karışımında".
- rapor.html 422: "Rakipler aynı defterde: v1, v1.3, v1.4, v2" (4).
- Hafıza: "Defter 6 sürüm" → "8 sürüm" → "10 sürüm" (kronolojik). Paneldeki rakip sürümleri sayınca 10'dan çok çıkıyor: v1.6, v1.6b, K4', v1.7, v1.8, v2.3, v1.9, v1.9m, v2.4, v2.4abc, v1.10k, CRS-S, Bayes ETAS, S2 haritaları.
- **Açık hata** (sayılar eskimiş). Düzeltme: tek bir "defter sürüm sayısı (11 Kasım): N" satırı, 172 ve 269'daki sayılar "o tarihte" diye işaretlenmeli. N'yi depodan sayamadım; D5'in 17'si en güncel aday.

### T2 · YÜKSEK · Harcama toplamları birbirini tutmuyor; bütçe tavanına yaklaşılması hiçbir yerde görünmüyor
- index.html 169 (B hücresi), aynı hücrede iki farklı değer: "Marmara harcaması **≈2,4 € / 30 €**. Olasılıklar özel kayıtta. Marmara hattı harcaması **≈1 €**."
- index.html 182: "Bütçe: ≤30 € (… harcanan **≈0,62 €**)". Bu satır 7 Kasım'dan beri değişmemiş, yol.html'de de aynı.
- rapor.html 452: "Marmara hattı harcaması **≈5,4 €**".
- Panelin kendi verdiği tek tek maliyetler: v2.1 7,08 €, v2.2 2,50 €, S5 ABC 9,37 €, deniz tabanı kolu ≈3,13 €, simülatör (MCQsim + v2) ≈2,8 €, Bayes ETAS 0,21 €, D4 0,21 €, mühür 0,125 €. Toplam ≈25 €, yani "≤30 €" Marmara bütçesine yaklaşıyor.
- Hafıza: "Kasım toplamı ≈30 €", "ay toplamı 19,09 €", "ay 28,88 €", "Hetzner Kasım toplamı ≈16,2 €".
- **Açık hata.** Düzeltme: 169 ve 182'deki eski tutarları kaldırıp tek bir satır yazmak: "Kasım harcaması (11 Kasım): ≈29–30 € (Hetzner); Marmara hattı ≈25 €; tavan 100 €". Kesin rakamı Hetzner faturasından almak gerekir, ben doğrulayamıyorum.

### T3 · ORTA · 1999 kayma modeli sayısı: 8 mi, 9 mu?
- index.html 169: "1999 için eşit ağırlıklı topluluk (**İzmit 6, Düzce 2** model)" (= 8). rapor.html 431: "1999 için **8** kayma modelinin eşit ortalaması".
- index.html 180 (M7 kuralları): "1999 için **9** temiz kayma modelinin eşit ağırlıklı ortalaması (Hayes 2017 hariç)". Hafıza turkiye-muhur-kurallari ve turkiye-fizik-girdileri de 9 diyor ("6 İzmit ve 3 Düzce modeli, Konca 2010"). marmara-girdi-kaynaklari ise "aynada Düzce için yalnız DELO + BIRG var" diyor (→ 8).
- **Yoruma açık.** Kural 9 diyor, uygulamada 8 model kullanılmış görünüyor. 180'e "(uygulamada 8: aynada Düzce için yalnız 2 model)" notu eklenmeli.

### T4 · ORTA · kiyas.html orman grafiği İtalya TripleS ve MPS04 için sızıntılı eski satırları çiziyor
- kiyas.html 552–553: `TripleS · İtalya (N=7) v:0.444, se:0.386` ve `MPS04 · İtalya (N=7) v:0.613, se:0.545`.
- Aynı sayfa 238: "AH (sızıntısız) **+0,28 ± 0,41 / +0,45 ± 0,53**; sızıntılı eski satır: +0,44 / +0,61". Aynı grafikteki HAZFX satırı ise "(N=7, sızıntısız)" −0,507 olarak çizilmiş.
- **Açık hata.** Düzeltme: `v:0.28, se:0.41` ve `v:0.45, se:0.53` (etiket "sızıntısız").

### T5 · ORTA · İstanbul aralığının "en büyük kaynağı" için nihai sürümün yerine eski sürümün payı yazılmış
- rapor.html 232 (Özet "Tavan"): "İstanbul 30 yıl aralığının **%52'si** dal içi parametrelerden". index.html 172: "en büyük kaynak artık dal içi parametreler (%52…)".
- Bu oran v1.3'e ait (DEFTER 8 Kasım: "parametre %52, uzamsal %22, tekrar %15, zaman %11"). Nihai v1.3b için panelin kendisi başka oran veriyor: index.html 254 ve 327'de "uzamsal %45, dal içi %32, tekrar %13, zaman %10". Hafıza (v1.6) da "İstanbul dal içi %32" diyor. index.html 268 ve araştırma kartları (314, 372, 405, 424, 451) ise "uzamsal %46" yazıyor, bu da v1.5 rakibinin payı.
- **Açık hata** (rapor.html 232). Düzeltme: "Nihai v1.3b'de İstanbul 30 yıl aralığının en büyük kaynakları uzamsal eksen (%45) ve dal içi parametreler (%32)". %46'ların yanına "(v1.5)" yazılmalı ya da hepsi %45 yapılmalı.

### T6 · ORTA · Canlı hattın başlama tarihi: 8 Kasım mı, 9 Kasım mı?
- rapor.html 422: "Canlı hat **8 Kasım'dan beri** günlük çalışıyor". index.html 229: "Canlı hattın dünya çıktısı … yalnız **8 Kasım'dan beri** var".
- kiyas.html, İlerleme/Sıra tablosu: "**9 Kasım** · 2026 Türkiye penceresi açıldı, **canlı hat kuruldu**". index.html 172: zamanlayıcının kuruluşu v1.4 (9 Kasım) paragrafının içinde.
- Hafıza bunun ikisine de karşı (bkz. E2).
- **Yoruma açık.** Kod 8 Kasım'da hazır, zamanlayıcı 9 Kasım'da kurulmuş olabilir. Tek bir ifadeye indirilmeli.

### T7 · ORTA · Site dışı yedek ve depo boyutları dört farklı değer alıyor
- kurulum.html 107: "13 GB koşu çıktısı bu sunucunun **40 GB** hacminde"; 110: "diskte yaklaşık **15 GB boş**". index.html 631: "≈15 GB boş"; 693: "**13 GB** çıktının site dışı yedeği".
- index.html 649 ve rapor.html 449: "/srv/depo (**≈31 GB**)".
- index.html 633: "Bu makinede **veri ve run çıktıları da yok**". Bu, kurulum.html 107 ("13 GB koşu çıktısı bu sunucunun 40 GB hacminde … Çözüldü") ile çelişiyor.
- Hafıza: "Depo hacmi **120 GB**'a büyütüldü (11 Kasım; **80→120**…; /srv/depo **40 GB boş**)". Görev metni "40→120" diyor, hafıza "80→120" yazıyor; hafızanın kendi içinde de belirsizlik var.
- kurulum.html 108: yedek hacmi "≈**1,1 €/ay**". Hafıza: "knotenlinie-yedek 20 GB volume … ≈**0,9 €/ay**".
- **Açık hata** (633 kurulumla çelişiyor, boyutlar eskimiş). Düzeltme: "knotenlinie-depo: /srv/depo 120 GB hacim (11 Kasım), ≈40 GB boş; koşu çıktıları burada".

### T8 · DÜŞÜK · Küresel H − GEAR1 satırları yan yana açıklamasız duruyor
- index.html 476 (merdiven): "buradayız … +0,121 ± 0,024". index.html 485: "+0,153 ± 0,024 (N 533; eski satır +0,121)". rapor.html SVG (≈340): "H − GEAR1, küresel M≥5,95, **2014–15**: +0,175 ± 0,035, N 228". Panelin öteki yerleri "2014–20: +0,146 (N 725)" diyor.
- Bunlar farklı ölçümler: +0,121 kör, +0,153 geliştirme; 2014–15 eski iç test, 2014–20 yeniden kurulum. Ama rapor.html'deki "2014–15" satırı, aynı sayfadaki "2014–20" satırıyla yan yana duruyor ve tek fark pencere adı.
- **Yoruma açık.** SVG başlığına "(eski harita, Ekim)" eklenmeli.

### T9 · DÜŞÜK · Alp–Himalaya kuşağı değeri bağlamsız
- rapor.html 252 (kıyas tablosu): "Alp–Himalaya kuşağında yalnız **+0,038**". rapor.html 253 ve 410: "kuşak içinde **−0,044 (N 81)**". index.html 583 (7 Kasım "Neyi göze alıyoruz"): "kuşak içi −0,044, N 81". index.html 486: "+0,038".
- Biri kör 2021–25 alt kümesi, öteki 2014–20 geliştirme ölçümü olabilir; pencere yazılmamış.
- **Yoruma açık.** Her iki değerin yanına pencere yazılmalı.

### T10 · DÜŞÜK · Öteki küçük sayı farkları
- 4. basamak beklenen hüküm süresi: kiyas.html 428 "≈6,2 yıl", rapor.html 422 "≈6,3 yıl" (güç %78 / 0,781 tutuyor). **Yoruma açık**, yuvarlama olabilir.
- S1 ve S6 aynı kural hash'ini taşıyor (index.html 328 ve 329, "Kural 4e71914"). Hafıza bu hash'i yalnız S1 için yazıyor. Ortak ön kayıt olabilir. **Yoruma açık.**
- v1.5/v2.2'de 18872d36: hafıza "main 18872d36", panel (index.html 172) "kural 18872d36". Hash aynı, rolü farklı yazılmış. **Yoruma açık**, düşük.
- Panelin içinde hafızadaki öteki hash'lerin hepsi aynı iddiayla eşleşiyor (≈90 hash karşılaştırıldı).

---

## 3. Eskimiş durumlar

### E1 · YÜKSEK · 2026 Türkiye penceresi: panel "açıldı" diyor, hafıza "Erdem'in satırını bekliyor" diyor
- index.html 172: "2026 Türkiye penceresi **9 Kasım'da açıldı** (ACILIS.json, a325b27f)". index.html 599: "Türkiye, 2026 (1 Ocak – 9 Kasım) | **açıldı (9 Kasım)** | … açılış kaydı ACILIS.json (a325b27f)". kiyas.html Sıra tablosu: "9 Kasım · 2026 Türkiye penceresi açıldı". rapor.html (Kurallar): "Türkiye 2016–2025 ve 2026 artık geliştirme verisi".
- Hafıza MEMORY.md (Sonuçlar): "2026 Türkiye penceresi: sızıntı yok (DEGERLENDIRME.md) ama **açılış Erdem'in satırını bekliyor** ("2026 Türkiye penceresini aç"). Sunucu izin denetimi kart onayını saymaz". a325b27f hafızanın hiçbir yerinde geçmiyor.
- **Yoruma açık ama kritik.** Panel doğruysa hafıza düzeltilmeli. Hafıza doğruysa panel açılmamış bir veriyi açılmış gösteriyor ve 2026 Türkiye verisinin geliştirmede kullanılması kör veri ihlali sayılır. Depoda ACILIS.json ve a325b27f'nin gerçekten var olup olmadığına bakılmalı.

### E2 · YÜKSEK · Canlı ETAS zamanlayıcısı: panel "kuruldu" diyor, hafıza "izin bekliyor" diyor
- index.html 172: "canlı hat zamanlayıcısı **kuruldu** (her gün 06:15 UTC, ETAS ebeveynleri EMSC'den)". index.html 257: "canlı ETAS 06:15 değişmedi". rapor.html 422: "Canlı hat 8 Kasım'dan beri günlük çalışıyor".
- Hafıza: "İleri test boru hattı + canlı ETAS kodu tools/canli (ef5ac979, inceleme KABUL); **systemd timer izin bekliyor** ("canlı hat zamanlayıcısını kur")". Hafıza aynı paragrafta CRS (06:45) ve Bayes (08:15) zamanlayıcılarının kurulduğunu ayrıca yazıyor; ana canlı ETAS (06:15) için böyle bir kayıt yok.
- **Yoruma açık ama kritik.** CRS ve Bayes kancaları "canlı ETAS'ın sha'ları değişmedi" diye ana hatta dayanıyor. Ana hat koşmuyorsa ikisi de boşa çalışıyor olabilir. Sunucuda `systemctl list-timers` ile denetlenmeli.

### E3 · YÜKSEK · Site dışı yedek panelin her yerinde "ertelendi" ya da "açık"; hafızada kurulmuş
- kurulum.html 108: "**Ertelendi** · Site dışı yedek … Yapılacak: Erdem bir Hetzner Storage Box ya da B2 hesabı açıp … 15 Aralık dondurmasından önce yapılması iyi olur."
- index.html 489: "Ertelendi: site dışı yedek". 693/698 (hk7): "13 GB çıktının site dışı yedeği (**ertelendi**) … Erdem hesabı açınca kurulacak". 649: "Storage Box BX11 açık, ama /srv/depo (≈31 GB) aktarımı sunucunun izin denetiminde **duruyor**".
- rapor.html 449 (Açık kararlar): "Storage Box BX11 açık; … aktarımı … **duruyor**. Çözüm … yalnız Erdem'in bilgisayarından yapılabiliyor."
- Hafıza (Altyapı): "Site dışı yedek (10–11 Kasım): **restic + Storage Box u714492** … tools/yedek/yedek.sh … Timer her gün 03:30 UTC … Parola Doppler RESTIC_PASSWORD … İlk gece (11 Kasım) yol hatası yüzünden başarısız; 12 Kasım koşusu bekleniyor."
- **Açık hata.** Düzeltme (dört yerde): "Site dışı yedek kuruldu (10–11 Kasım): restic → Storage Box u714492, günlük 03:30 UTC; ilk gece yol hatasıyla başarısız (28ed01dd ile düzeltildi), 12 Kasım koşusu bekleniyor."

### E4 · YÜKSEK · v2.1 rapor.html'de hâlâ "koşuyor"; 10 Kasım'da dondurulmuş
- rapor.html 231: "v2.1 kalibrasyonu **koşuyor**". 434 (Sırada ne var): "v2.1: simülatör segment kalibrasyonu (**koşuyor**)". 451 (Açık kararlar): "v2.1 kalibrasyonu: 4×CPX62'de **koşuyor**, tavan 15 €".
- index.html 172 ve hafıza: "v2.1 DONDURULDU (10 Kasım, 43f04335) … 7,08 €, kiralık sunucu kalmadı".
- **Açık hata.** Düzeltme: "v2.1 donduruldu (10 Kasım, 43f04335, 7,08 €): ileri test rakibi." Durum raporunun bütünü 9 Kasım'da kalmış. v1.5–v2.4abc, CRS, Bayes ETAS, derive ve yıl ölçeği işlerinin hiçbiri rapor.html'de yok.

### E5 · YÜKSEK · index.html "Ana hat" kutusundaki takvim nihai dondurmayla çelişiyor
- 163 başlık: "Ana hat: Marmara M7+ tahmini **31 Aralık 2026'ya**". 172 "Ne zaman" sütunu: "v1 donduruldu 8 Kasım; **nihai 31 Aralık**". Aynı hücrenin içinde ise "NİHAİ DONDURMA ÖNE ÇEKİLDİ (9 Kasım, 3af37f9e …)".
- 171 (D): "15–30 Kasım (tahmin): 2019 ve 2025 olaylarının gerilme etkisi … **1–20 Aralık: dört doğrulama** (aşağıda) ve topluluk ağırlıkları". Dört doğrulama 8 Kasım'da puanlandı (169: "PUANLANDI (8 Kasım, f9d581c8…)").
- 169 (B): "8–14 Kasım (tahmin)" ve "Aralık doğrulaması sınayacak".
- 178: "Deprem döngüsü simülatörü **2027'ye**: 7 haftada kalibre edilemez". MCQsim 8 Kasım'da koştu; v2, v2.1, v2.2, v2.3 ve v2.4abc donduruldu.
- **Açık hata.** Düzeltmeler: 163 "Ana hat: Marmara M7+ (nihai v1.3b 9 Kasım'da donduruldu; ileri test 1 Ocak 2027)"; 172 "v1 8 Kasım; nihai 9 Kasım (31 Aralık'tan öne çekildi)"; 171 "Doğrulamalar 8 Kasım'da puanlandı"; 178 "Simülatör 8–11 Kasım'da koşuldu (v2–v2.4abc, defterde rakip)".

### E6 · ORTA · FA-1 ve TK-1 "Seçim Erdem'in" diye kalmış; aynı kutu "koşuyor" diyor
- index.html 143 (FA-1 Durum): "Seçim Erdem'in. Önerim: ilk bu". 144 (TK-1): "Seçim Erdem'in. 8 Kasım … kararıyla çelişebilir".
- index.html 158: "FA-1 ve TK-1 **Erdem'in seçimiyle sunucuda koşuyor**". Hafıza (ortak-kayit-defteri): "Erdem 11 Kasım 16:15 kartta 'FA-1 ve TK-1 paralel' seçti; ikisi sunucuda /srv/depo/wt-fa1, wt-tk1".
- **Açık hata.** Düzeltme (143 ve 144): "Erdem seçti (11 Kasım 16:15): sunucuda koşuyor (ön kayıt, kod, kuru koşu)". 146'daki FA-2 "Seçim Erdem'in" doğru kalır.

### E7 · ORTA · Menü, sıra ve yol bölümleri 7 Kasım planında kalmış (15 Aralık, 23 Kasım, 2027 takvimi)
- index.html 657 hk1 adı: "H ve GEAR1'i yeniden kur, **15 Aralık'ta dondur**". Notu ise "BİTTİ (9 Kasım)". 661 sınav notu: "Ön kayıt metni hâlâ eski modeli ve 0,693'ü anıyor" (çözüldü; rapor.html 423 "Çözüldü (9 Kasım)").
- 837–838 (Sıra): "Şimdi → 15 Aralık", "**38 gün**", "Yeniden kurulum en geç 23 Kasım'da başlar". 852: "Türkiye sınavı · **senin kararın**" (mühür 7 Kasım'da açıldı). 843–850: bb4 ve bb5 "Nisan → Eylül 2027"de; bu işler 10 Kasım'da yapıldı (723 ve 729 notları). Hafızadaki "TAKVİM BEKLEMESİ YOK" kuralıyla da çelişiyor.
- 868 (Önerilen yol): "Küresel haritayı 15 Aralık'ta dondur". 576: "**15 Aralık dondurması** kaçarsa ilk ileri test kanıtımız bir yıl gecikir". 583: "Normal fay zaafı (−0,178) da ilk düzeltilecek yer" (487: tekrarlanmadı, −0,085).
- 709 bb2 simülatör: "2–4 ay, 100–500 €, … bb1 geçerse"; simülatör hattı zaten koştu.
- rapor.html 405–407 (Uzun vade planı): "H ve GEAR1 … **15 Aralık'ta dondur**", "Normal fay zaafı: −0,178'i … yeniden ölç". 379 (L6 satırı) "Yeniden kurulumun ilk bakacağı yer".
- kurulum.html 108: "15 Aralık dondurmasından önce".
- 566'daki "Önceki öneri (7 Kasım sabahı)" başlığı yalnız #yol bölümünü tarihliyor; #menu, #sira, hk1 adı ve rapor planı tarihsiz.
- **Açık hata** (en azından hk1 adı, 838 ve 852). Düzeltme: hk1 adı "H ve GEAR1'i yeniden kur ve dondur ✓ (9 Kasım)"; P[0] "9 Kasım'da tamamlandı"; Türkiye sınavı "7 Kasım'da yapıldı"; menü/sıra bölümlerinin başına "7 Kasım planı, arşiv" notu.

### E8 · ORTA · kurulum.html bütünüyle 7 Kasım anlık görüntüsü
- Ağ izin listesi: "api.hetzner.cloud ve api.doppler.com". Hafıza buna api.openalex.org'u da ekliyor.
- Doppler secret listesinde OPENALEX_API_KEY ve RESTIC_PASSWORD yok; hafızada ikisi de var.
- rc-keepalive (9 Kasım, Restart=always, 2 dk izleyici, 4 GB swap) ve sshd'nin yalnız anahtarla girişe kapatılması yazılmamış.
- Disk 40 GB / 15 GB boş (bkz. T7). Yedek "Ertelendi" (bkz. E3).
- Zotero MCP "Açık" doğru (hafıza: "Zotero MCP yok"). Ama `kayit/kaynakca.bib` BibTeX çözümü (11 Kasım) yazılmamış.
- index.html 649 bunun anlık görüntü olduğunu söylüyor, kurulum.html'in kendisi ise "Çalışıyor / Çözüldü" etiketleriyle güncelmiş gibi duruyor.
- **Açık hata.** Düzeltme: başlığa "7 Kasım; güncelleme 11 Kasım" eklenmeli; disk, yedek, izin listesi ve secret listesi güncellenmeli.

### E9 · ORTA · "Son güncelleme" tarihleri sekmeden sekmeye değişiyor
- index.html 134: "son güncelleme **11 Kasım**". rapor.html 216: "Durum raporu · **9 Kasım**". kiyas.html 118: "Cetvel, Sıra ve defter **9 Kasım**; Mühür sekmesi 29 Ekim; ufuk tabloları 23 Ekim gecesi; İlerleme 29 Ekim". kurulum.html 45: "**7 Kasım**". yol.html: 7 Kasım.
- kiyas.html'deki DEFTER JSON'u 752 satır; son tarih 2026-11-09 (555 satır ≤29 Ekim + 197 satır 30 Ekim–9 Kasım; index.html 231 ve hafızadaki 197 satırla tutuyor). 10–11 Kasım sonuçlarının hiçbiri (v1.5'ten v2.4abc'ye, S1–S7, CRS, Bayes, derive) defterde yok.
- Hafıza: "Panel tek kaynak; HER cevaptan önce oku". İki sekmenin 2 gün geride olması bu kuralı zayıflatıyor.
- **Açık hata** (eskimiş). Önerim: her sekmenin başına aynı biçimde "Son güncelleme: GG Ay" yazmak ve rapor ile kiyas'ı 11 Kasım'a getirmek.

### E10 · DÜŞÜK · Öteki eskimiş ifadeler
- rapor.html 422: "Pencere açılır … **55 gün kaldı**". Bu sayı 7 Kasım'dan hesaplanmış; sayfa tarihi 9 Kasım'a göre 53, bugüne göre 51. **Açık hata.** Düzeltme: sabit gün sayısı yerine "1 Ocak 2027" yazmak.
- rapor.html 379: "Fay kilitlenmesi … Yok. Tek sayı bölgesel toplam c ≈ 0,75 (hakemsiz) | ölçülmedi". Panelin öteki yerleri: K4' c ≈ 0,34 (index.html 255), v1.8 CMF kısmen kilitli, Y1b CMF 11 ± 3 mm/yıl. **Açık hata** (eskimiş).
- index.html 485: "RAPOR-5 ön kaydı dondurma incelemesinde"; 488: "H/GEAR1 yeniden kurulum sürüyor … harcama ≈0 €". İkisi de "7 Kasım ilerlemesi" başlığı altında, yani tarihli. Ama aynı listede 485 "kuruldu", 488 "sürüyor" diyor. **Yoruma açık.**
- index.html 452 (Kaliforniya K5): "K5 OTS Bitcoin onayı bekliyor". Hafıza da "K5 OTS upgrade bekliyor" diyor; tutarlı, yalnız tarih izlenmeli.
- kiyas.html Sıra tablosu: "v1.4 ve v2 **bilgi satırı** olarak donduruldu". index.html 172 ve hafıza: v1.4 "ileri test **rakibi**", v2 "aday değil, ileri test defterinde". **Yoruma açık.**
- "ots upgrade" bekleyişi (rapor.html 422 ve 450, index.html 662) hafızayla tutarlı ("kalan ots upgrade"). Bunu eskimiş saymadım.
- Zotero: kurulum "Açık", hafıza "Zotero MCP yok". Tutarlı.
- Hafıza tarafında eskimiş olanlar (panel doğru): MEMORY.md'de "DERIVE DOĞRULTU ATIMLI … seçim bekliyor", "DERIVE KALİFORNİYA … seçim bekliyor", "YENİ ARAŞTIRMA SORULARI … Erdem seçimi bekliyor". Konu dosyaları ve panel (index.html 432, 452, 325) bunların koşulup kapandığını söylüyor. derive-deniz-tabani.md'deki "Panel … henüz A3/A4 sonucuyla güncellenmedi" notu da eskimiş; panel 405–406'da güncel.

---

## 4. Kurallara aykırılık (mutlak olasılık)

### K1 · ORTA · Literatürdeki mutlak 30 yıllık olasılık aralığı panelde yazılı
- index.html 177 (ve yol.html'de aynı satır): "Dürüst sınır: tarih bilinemez. 30 yıllık **mutlak olasılık literatürde ≈%20–65** (Parsons 2004, Erdik 2004, Murru 2016 vb.)".
- Bu kendi tahminimiz değil, genel literatür atfı. Ama İstanbul/Marmara M7 için mutlak bir yüzde aralığı veriyor, 16 Ekim taahhüdünün ("bu sayfaya tek şehir ya da tek deprem olasılığı yazılmaz", index.html 183) sınırında duruyor.
- **Yoruma açık.** Ayrıca işaretlendi. Sıkı okumada "literatürdeki aralık geniş; fark çoğunlukla model seçiminden" yeterli.

### K2 · ORTA · Marmara bölgesi için mutlak yıllık M7 oranı yazılı
- index.html 172: "Bölge M7 oranı ayarlardan bağımsız (**≈0,021/yıl**)". Bu, bölge düzeyinde mutlak bir orandır; 30 yıllık bölge olasılığına doğrudan çevrilebilir (≈%47). Göreli oran değil.
- Hafıza da aynı sayıyı yazıyor ("bölge M7 oranı 0,021/yıl, H1 ile uyumlu"), yani ekip bunu kabul etmiş görünüyor.
- **Yoruma açık.** Tek şehir olasılığı değil, ama kuralın amacına göre "tarihsel katalogla uyumlu" demek yeterli olabilir.

### K3 · DÜŞÜK · DEFTER'de segment başına simüle ortalama tekrar süreleri
- kiyas.html DEFTER (8 Kasım satırları): "simülatör tekrar istatistiği IZMIT … μ_sim **88 yıl**", "GANOS … 135 yıl", "PIF … 370 yıl", "ÇINARCIK … 1 162 yıl", "İMRALI … 983 yıl".
- Olasılık değil, kalibrasyonsuz simülatör çıktısı (v2 "segment düzeyinde kullanılamaz"). Ama segment başına mutlak tekrar süresi veriyor.
- **Yoruma açık**, düşük.
- Kontrol edildi, ihlal yok: oranlar (v1.x/v1.3b, 0,51, 1,78, 0,93 vb.), %10–90 genişlik oranları, varyans payları (%), ortak kırılma payları (≈0,70, f ≈ 0,10, %66–78) ve kilitlenme sonsalları (PIF tam kilit 0,71) göreli ya da koşullu nicelikler. DEFTER'de iki satır (12 Ekim, "AI Marmara M≥7 olasılığı") sayının panelden çıkarıldığını açıkça yazıyor. Panelde mutlak İstanbul ya da tek şehir olasılığı bulmadım. Hafızadaki "envanter doc'unda 0,26–0,36 gibi sayılar var; kopyalama" uyarısındaki sayılar panelde yok.

---

## 5. Biçim

### B1 · DÜŞÜK · Yazım hatası "KABÜL"
- index.html 327: "İnceleme dondurma öncesi RED → **KABÜL**, sonrası **KABÜL**". **Açık hata.** Düzeltme: "KABUL" (iki yerde).

### B2 · DÜŞÜK · Yinelenen sözcük
- index.html 182: "Küresel ön kayıt (RAPOR-5) **RAPOR-5 dondurması** 9 Kasım'a öne çekildi". **Açık hata.** Düzeltme: "Küresel ön kayıt (RAPOR-5) dondurması 9 Kasım'a öne çekildi".

### B3 · DÜŞÜK · Hücrelerde artık plan cümleleri ve kopuk ifadeler
- index.html 172 (E hücresi) uzun sonuç metninden sonra 7 Kasım planının cümleleriyle bitiyor: "… Simülatör işi ≈2,8 €. **Segment başına 1, 5, 30 yıllık olasılık ve belirsizlik aralığı; aralığın hangi varsayımdan geldiği. İnceleme, zaman damgası. 1 Ocak 2027'den itibaren ileri test kaydı.**" Ayrıca hücrenin içinde sıra kronolojik değil: v2.1, v1.5 ve v2.2 (10 Kasım), MCQsim ve v2'den (8–9 Kasım) önce geliyor. **Açık hata** (artık metin silinmeli).
- index.html 169 (B hücresi) da sonuçlardan sonra plan cümleleriyle bitiyor: "(1) İstatistik tabanı ETAS: … yeniden kurulur … (2) Segment yenilenmesi …". İçinde iki harcama değeri var (T2). **Açık hata.**
- index.html 228: "… kurulmadı:** (10 Kasım'daki v1.5 ayrı bir iş: Marmara paleosismik.) bunlar unutulmuş değildi" — parantezden sonra cümle küçük harfle başlıyor, kopuk. Düzeltme: "Bunlar unutulmuş değildi (10 Kasım'daki v1.5 ayrı bir iştir: Marmara paleosismik)."
- index.html 276: "**Adalar adaları** faya 2–5 km". Düzeltme: "Adalar faya 2–5 km" ya da "Prens Adaları faya 2–5 km".
- index.html 600: "Okuyucu (**M/12 kuralı**)". Öteki yerlerde "kural 12 Ek 3" yazıyor (229). Muhtemelen yazım hatası. Aynı satırda "v1.2 uzamsal ekseninin **teyidine** harcanır", 262 ve 266'da "yalnız bilgi satırı; hiçbir sonucu İstanbul'u değiştiremez". **Yoruma açık.**
- index.html 774: "Veriler çoğu zaman zaman damgasız" — virgül eksik. Düzeltme: "Veriler çoğu zaman, zaman damgası taşımıyor".
- index.html 280: "gel-git" (TDK: "gelgit"; sayfanın kendisi de başka yerlerde "gelgit" kullanıyor).
- kiyas.html 410: "2,95 ≤ M **<** 3,95" ham `<` ile yazılmış. HTML5 bunu metin olarak işliyor, ama `&lt;` olmalı.
- Adlandırma tutarsız: rapor.html `<h1>` "Operation Knotenlinie", kiyas.html "Operasyon Knotenlinie". Merdivenin 5. basamağı rapor/kiyas'ta "İstanbul", index'te "M6+/M7+ ve Marmara". 2. basamak rapor'da "farkı ayıramadık. Bu, puanların tam eşit olduğunu kanıtlamaz", kiyas'ta "en iyi modelle aynı puanı aldık" (kiyas.html 139); kiyas'taki ifade fazla güçlü. Düşük.
- Etiket dengesi beş dosyada da temiz (betikle denetlendi). Yinelenen paragraf bulunmadı (70 karakterden uzun cümlelerde tam yineleme yok).

---

## En önemli 15 bulgu (özet)

1. **Y1 (yüksek):** Sekme gezintisi yok. index.html rapor, kıyas ve kurulum sayfalarına hiç bağlanmıyor, ama metin "sekme" diye bunlara başvuruyor.
2. **E1 (yüksek):** 2026 Türkiye penceresi panelde "9 Kasım'da açıldı (ACILIS.json, a325b27f)" (index 172, 599; kiyas), hafızada "açılış Erdem'in satırını bekliyor". Kör veri açısından kritik, depodan doğrulanmalı.
3. **E2 (yüksek):** Canlı ETAS zamanlayıcısı panelde "kuruldu, 06:15 UTC" (index 172, 257; rapor 422), hafızada "systemd timer izin bekliyor".
4. **E3 (yüksek):** Site dışı yedek kurulum 108, index 489/693/649 ve rapor 449'da "ertelendi/duruyor". Hafızaya göre 10–11 Kasım'da restic + Storage Box u714492 olarak kuruldu (03:30 timer).
5. **T1 (yüksek):** Defter sürüm sayısı 8 (index 172), 10 (269), 10+ (376), 17 (384), 4 (rapor 422).
6. **T2 (yüksek):** Harcama: "≈2,4 € / 30 €" ve "≈1 €" aynı hücrede (index 169), "≈0,62 €" (182), "≈5,4 €" (rapor 452). Panelin kendi tek tek tutarları Marmara için ≈25 € ediyor; hafızada Kasım ≈30 €. ≤30 € bütçeye yaklaşıldığı hiçbir yerde görünmüyor.
7. **E4 (yüksek):** rapor.html v2.1'i üç yerde "koşuyor" diye gösteriyor (231, 434, 451); v2.1 10 Kasım'da dondu. Durum raporu 9 Kasım'da kalmış.
8. **E5 (yüksek):** index "Ana hat" kutusu: başlıkta ve sütunda "nihai 31 Aralık" yazıyor, aynı hücre "nihai 9 Kasım" diyor. D satırında "1–20 Aralık dört doğrulama" yazıyor, doğrulamalar 8 Kasım'da yapıldı. "Simülatör 2027'ye" yazıyor, simülatör koştu (163, 169, 171, 172, 178).
9. **T4 (orta, açık hata):** kiyas.html orman grafiği (552–553) TripleS ve MPS04 için sızıntılı eski değerleri (+0,444 / +0,613) çiziyor; tablo sızıntısız +0,28 / +0,45 diyor.
10. **T5 (orta):** rapor Özet "aralığın %52'si dal içi" v1.3'e ait. Nihai v1.3b'de panelin kendi sayısı uzamsal %45 / dal içi %32.
11. **E6 (orta):** FA-1/TK-1 tabloda "Seçim Erdem'in" diye kalmış (143–144); aynı kutu (158) ve hafıza Erdem'in 16:15'te seçtiğini, işlerin koştuğunu söylüyor.
12. **T3 (orta):** 1999 kayma modeli sayısı 8 (index 169, rapor 431) ve 9 (index 180, hafıza kuralı).
13. **T7 / E8 (orta):** Depo diski 40 GB / 15 GB boş (kurulum, index 631) vs hafızada 120 GB / 40 GB boş. Çıktı boyutu 13 GB vs ≈31 GB. index 633 "bu makinede run çıktısı yok" kurulumla çelişiyor. Yedek ücreti 1,1 vs 0,9 €/ay. kurulum.html bütünüyle 7 Kasım'da kalmış.
14. **K1 / K2 (orta, yoruma açık):** Literatürden mutlak 30 yıllık olasılık "≈%20–65" (index 177, yol.html) ve mutlak bölge oranı "≈0,021/yıl" (index 172). Tek şehir olasılığı değil, ama kuralın sınırında.
15. **Y2 + E7 (orta):** yol.html index.html'in 7 Kasım kopyası (563/576 satır aynı) ve erişilemiyor. index'in menü, sıra ve yol bölümleri ile rapor'un plan bölümü hâlâ "15 Aralık dondurması", "23 Kasım", "38 gün", "Türkiye sınavı senin kararın" ve 2027 takvimi diyor.

Küçük açık hatalar: "KABÜL" (index 327, iki kez), "RAPOR-5) RAPOR-5" (182), "Adalar adaları" (276), "55 gün kaldı" (rapor 422, 7 Kasım'a göre hesaplanmış), "'Sonraki adımlar' sekmesi" (kiyas 264, sekmenin adı "Sıra").
