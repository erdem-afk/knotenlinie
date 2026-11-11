# VE-1 Ek 1 adayı: postsismik model parametre tablosu (Y3, Y4, Y6 için)

Tarih: 11 Kasım 2026. Hazırlayan: parametre çıkarma ajanı. Yalnız bu dosya yazıldı; git çalıştırılmadı, GNSS serisi indirilmedi.
Kural: her sayının yanında kaynak yeri ve "tam metin / özet / ikincil" etiketi var. Okunamayan alan **OKUNAMADI** diye yazıldı, tahminle doldurulmadı.

## 0. Erişim özeti (ne okundu, ne okunamadı)

| # | Makale | Tam metin | Ne denendi, sonuç |
|---|---|---|---|
| 1 | Hearn ve diğ. 2009, JGR, 10.1029/2008JB006026 | **OKUNAMADI** | Wiley/AGU PDF ve HTML: HTTP 403 (yayıncı bot koruması, atlatılmadı). ANU deposu (hdl 1885/36510): kopya var ama erişim **2037-12-31'e kadar kısıtlı** (arama sonucu). OpenAlex: `oa_status: closed`. Semantic Scholar: `CLOSED`. Aperta (ULAKBİM) kaydında yalnız künye dosyası var. Yazar sayfasında kopya bulunamadı. Elde: yalnız özet (OpenAlex). |
| 2 | Ergintav ve diğ. 2009, JGR, 10.1029/2008JB006021 | **OKUNAMADI** | Açık kopya var: DSpace@MIT `Herring_Seven years.pdf` (175 KB, CC BY-NC-SA; hdl 1721.1/106538). Üç denemede de HTTP 429 döndü, gövdede "Web Firewall · 429, Retry-After: 900" yazıyordu. Bu bir koruma sayfası; zorlanmadı. Kişisel UA ile yeniden deneme oturumun izin denetiminden de geçmedi. İTÜ Polen (hdl 11527/34825) kaydında dosya yok. Wiley: 403. Elde: özet ve 1 sayfalık Türkçe bildiri özeti (JMO, .doc, yazarlar aynı). 175 KB'lık MIT dosyasının tam makale mi yoksa kısaltılmış bir el yazması mı olduğu da bilinmiyor. |
| 3a | DeVries, Krastev, Meade 2016, G3, 10.1002/2016GC006313 | **OKUNAMADI** | Wiley'de "bronze OA" görünüyor ama `pdfdirect` HTTP 403 (bot koruması). Harvard DASH kopyası (`devries_et_al-2016-geochemistry_geophysics_geosystems.pdf`, 1,72 MB) iki denemede HTTP 429 "Web Firewall" döndü. Elde: özet. |
| 3b | DeVries, Krastev, Dolan, Meade 2017, BSSA, 10.1785/0120160059 | **OKUNAMADI** | OpenAlex ve Semantic Scholar: `closed`. Meade grubunun yayın sayfasında yalnız GeoScienceWorld bağlantısı var, PDF yok. Elde: özet. |
| 4 | Yamasaki, Wright, Houseman 2014, JGR, 10.1002/2013JB010347 | **OKUNDU** | White Rose eprints 80004 (CC BY 3.0), 22 sayfalık yayımlanmış PDF. |
| 5 | Wang, Lorenzo-Martín, Roth 2006, C&G, 10.1016/j.cageo.2005.08.006 | **Makale OKUNAMADI, kod OKUNDU** | GFZpublic PDF (`item_235712_1/.../10168.pdf`): HTTP 403 "Request forbidden by administrative rules". Kod: GFZ "Tool Development Lab" sayfasının işaret ettiği GitHub deposu `pyrocko/fomosto-psgrn-pscmp` (GPL-3.0). `src/psgrn/psgmain.f` ve `examples/psgrn08_input.dat`, `examples/pscmp08_input.dat` dosyaları okundu. |

Sonuç: istenen beş kalemden yalnız Yamasaki 2014'ün tam metni ve PSGRN/PSCMP kodu okunabildi. Hearn 2009, Ergintav 2009 ve iki DeVries makalesi için aşağıdaki sayılar **yalnız özetten**. Ön kayıt kuralı "tam metinden" olduğu için bu sayılar Ek 1'e **olduğu gibi giremez** (bkz. §6).

---

## 1. Hearn, McClusky, Ergintav, Reilinger 2009 (M1 adayı)

| Parametre | Değer | Birim | Kaynak yeri | Tam metin / özet |
|---|---|---|---|---|
| Yöntem | 3B viskoelastik sonlu eleman | – | Özet, 1. cümle: "using a three-dimensional viscoelastic finite element method" | özet |
| Uydurulan veri dönemi | 1999–2003 | yıl | Özet: "We have modeled postseismic deformation from 1999 to 2003" | özet |
| Erken dönem mekanizması | kararlı sürtünmeli afterslip, kırılma üzerinde ve altında | – | Özet: "principally due to stable frictional afterslip on and below the Izmit earthquake rupture" | özet |
| Afterslip sürtünme parametresi (ör. (a−b)σ) | **OKUNAMADI** | – | – | – |
| Afterslip derinlik aralığı | **OKUNAMADI** ("on and below the rupture" dışında sayı yok) | km | – | – |
| Afterslip zaman sabiti | **OKUNAMADI** (özet yalnız "within the first few months" diyor) | gün | – | – |
| Doğrusal viskoz (Maxwell) viskozite, alt kabuk ve/veya üst manto | 2–5 × 10^19 | Pa s | Özet: "with a viscosity of the order of 2 to 5 × 10^19 Pa s improves the models' fit to later GPS site velocities" | özet |
| Burgers: birinci (geçici) viskozite, mantoda | 2–5 × 10^19 | Pa s | Özet: "A Burger's body rheology with two characteristic viscosities (2 to 5 × 10^19 Pa s and at least 2 × 10^20 Pa s) in the mantle" | özet |
| Burgers: ikinci (kalıcı) viskozite, mantoda | ≥ 2 × 10^20 (**tek yönlü sınır**) | Pa s | aynı cümle | özet |
| Hangi viskozite Kelvin, hangisi Maxwell elemanında | **OKUNAMADI** (özet eleman adı vermiyor; "geçici = düşük, kalıcı = yüksek" eşlemesi olağan ama makaleden doğrulanmadı) | – | – | – |
| Kelvin kayma modülü ya da μ_K/μ_M oranı | **OKUNAMADI** | – | – | – |
| Elastik üst kabuk kalınlığı | **OKUNAMADI** | km | – | – |
| Katman derinlikleri ve elastik modüller | **OKUNAMADI** | km, GPa | – | – |
| Viskoz katmanın hangisi (alt kabuk mu, manto mu) | Doğrusal modelde "lower crust and/or upper mantle"; Burgers önerisi "in the mantle" | – | Özet | özet |
| "Tercih edilen" tek model | **OKUNAMADI**. Özet bir aralık ve bir tek yönlü sınır veriyor, tek bir "preferred" set adlandırmıyor | – | – | – |

İkincil kaynak notu (tam metinden, ama Hearn'ün kendisi değil): Yamasaki 2014, §1, s. 3678: "Analysis of these data by Hearn et al. [2009] concluded that a power law or Burger's body rheology was needed to explain both the interseismic and postseismic GPS velocities." Bu cümle sayı vermiyor.

**Tek set çıkarılabiliyor mu? HAYIR.**
- Tam metin okunamadı. Elastik kalınlık, katman yapısı, Kelvin modülü ve afterslip parametrelerinin hepsi eksik.
- Özetteki viskoelastik bilgi bir aralık (2–5 × 10^19) ve bir tek yönlü sınır (≥ 2 × 10^20). INCELEME-2 Y3'ün önerdiği kural ("tek yönlü sınırda makalenin ileri modelde kullandığı değer, yoksa sınırın kendisi") tam metin olmadan uygulanamaz, çünkü makalenin kullandığı değer bilinmiyor.
- Aralığın geometrik ortası hesaplanabilir (√(2×5) × 10^19 ≈ 3,2 × 10^19 Pa s). Ama bu yalnız bir aritmetik işlem; makalenin "tercih edilen" değeri değildir. Ek 1'e "makale değeri" diye yazılmamalı.

**2017 sonrası veriye uydurulmadı mı? EVET, uydurulmadı (özet düzeyinde teyit).** Model 1999–2003 verisine kurulmuş, yayım 2009 (Crossref ilk çevrimiçi 2009-08-25, INCELEME-2).

---

## 2. Ergintav ve diğ. 2009 (M3 adayı)

| Parametre | Değer | Birim | Kaynak yeri | Tam metin / özet |
|---|---|---|---|---|
| Veri | sürekli ve kampanya GPS | – | Özet: "continuously recorded and survey mode GPS observations" | özet |
| Veri dönemi | "nearly 7 years" postsismik (1999 sonrası) | yıl | Özet, 1. cümle. Kesin ilk/son epok **OKUNAMADI** | özet |
| Zaman fonksiyonu türü | logaritmik terimler dizisi (üstel değil) | – | Özet: "We use a sequence of logarithmic time functions to fit GPS site motions" | özet |
| Terim sayısı | en çok 3 | – | Özet: "Up to three logarithmic terms" | özet |
| Bozunma sabitleri | 1; 150; 3500 | gün | Özet: "with decay constants of 1, 150, and 3500 days are necessary to fit all the transient motion observed at the continuous GPS stations" | özet |
| Sabitler sabitlendi mi, kestirildi mi | **OKUNAMADI** | – | – | – |
| Fonksiyonun tam biçimi (ör. A·ln(1 + t/τ)) | **OKUNAMADI** (biçim makalede denklem olarak olmalı; doğrulanmadı) | – | – | – |
| İstasyon başına genlikler (A_i) | **OKUNAMADI** | mm | – | – |
| 1 günlük terim yorumu | sığ, hızlı afterslip (yakın alan, faya paralel bileşen) | – | Özet: "The first term is required for the component of site motion parallel to the NAF at near-field sites strongly implicating rapid, shallow afterslip" | özet |
| 150 ve 3500 günlük terim yorumu | ya yerel derin afterslip ya da alt kabuk/üst manto viskoelastik gevşemesi; makale ayırmıyor | – | Özet: "suggestive of either localized, deep afterslip or viscoelastic relaxation of the upper mantle and/or lower crust" | özet |
| Afterslip uzamsal dağılımı (fay yüzeyinde kayma, derinlik aralığı) | **OKUNAMADI**. Özette ters çözülmüş bir afterslip dağılımından söz edilmiyor | – | – | – |
| 7 yıl sonra fay boyunca göreli postsismik hız | ~10–12 | mm/yıl | Özet: "reaches ∼10–12 mm/a, roughly 50% of the steady state interseismic rate" | özet |
| En yüksek postsismik hız bölgesi | kırılmalara 40 km içinde | km | Özet | özet |

**Tek set çıkarılabiliyor mu? HAYIR (şimdilik).**
- Bozunma sabitleri (1, 150, 3500 gün) tek değerli. Ama model kurmak için gereken genlikler ve fonksiyon biçimi okunamadı.
- Daha önemli bir sorun da var. Özete göre Ergintav 2009 **istasyon zaman serilerine kinematik log fonksiyonları uyduruyor**. Uzun terimlerin kaynağını (derin afterslip mi, viskoelastik mi) açık bırakıyor. INCELEME-2 Y6'daki "Ergintav 2009'un afterslip dağılımı × logaritmik zaman fonksiyonu (elastik Green fonksiyonu)" tarifi, makalede ayrı bir afterslip **dağılımı** bulunduğunu varsayıyor. Bu varsayım özetle desteklenmiyor. Tam metin okunmadan M3'ün PSCMP ile nasıl kurulacağı yazılamaz.
- Olası seçenek (öneri, karar değil): makalede istasyon başına log genlik tablosu varsa M3, PSCMP'siz bir kinematik dışdeğerleme olarak kurulabilir: her ortak istasyonda log terimlerinin 2009–2016 ile 2017–2023 türevleri farkı. Bu yalnız makalede genlik verilen istasyonlar için çalışır, ve VE-1 listesindeki istasyonlarla örtüşmesi bilinmiyor.

**2017 sonrası veriye uydurulmadı mı? EVET, uydurulmadı (özet düzeyinde teyit).** Veri "nearly 7 years", yayım 2009 (ilk çevrimiçi 2009-07-09). TASLAK-2'deki "1999–2006" ifadesinin bitiş yılı tam metinden doğrulanmadı.

---

## 3. DeVries, Krastev, Meade 2016 G3 (M4 adayı) ve DeVries, Krastev, Dolan, Meade 2017 BSSA

### 3a. G3 2016 (10.1002/2016GC006313)

| Parametre | Değer | Birim | Kaynak yeri | Tam metin / özet |
|---|---|---|---|---|
| Yapı | elastik üst kabuk + Burgers reolojili viskoelastik manto | – | Özet: "an elastic upper crust coupled to a viscoelastic Burgers rheology mantle" | özet |
| Maxwell viskozitesi η_M | 4 × 10^18 – 1 × 10^19 | Pa s | Özet: "Maxwell (ηM = 4 × 10^18−1 × 10^19 Pa s)" | özet |
| Kelvin viskozitesi η_K | 1 × 10^18 – 1 × 10^19 | Pa s | Özet: "Kelvin (ηK = 1 × 10^18−1 × 10^19 Pa s)" | özet |
| Viskozitelerin kaynağı | 1999 öncesi ve sonrası jeodezi çalışmaları (makalenin kendi uydurması değil) | – | Özet: "constrained by studies of geodetic observations before and after the 1999 Izmit earthquake" | özet |
| "Tercih edilen" tek η_M, η_K | **OKUNAMADI** | Pa s | – | – |
| Elastik üst kabuk kalınlığı | **OKUNAMADI** | km | – | – |
| Kelvin modülü / oran, elastik modüller | **OKUNAMADI** | – | – | – |
| Kaynak olaylar | 1939'dan bu yana NAF büyük deprem dizisi (8 olay, MW > 6,7) | – | Özet | özet |

### 3b. BSSA 2017 (10.1785/0120160059)

| Parametre | Değer | Birim | Kaynak yeri | Tam metin / özet |
|---|---|---|---|---|
| Yapı | iki katman: "schizosphere" (elastik) ve "plastosphere" (Burgers) | – | Özet: "simple two-layer structure (schizosphere and plastosphere) and a Burgers rheology" | özet |
| log10 η_M | ≈ 18,6 – 19,0 (η_M ≈ 4,0 × 10^18 – 1,0 × 10^19) | log10 Pa s | Özet: "Maxwell viscosity log10 ηM≈18.6–19.0 Pa·s" | özet |
| log10 η_K | ≈ 18,0 – 19,0 (η_K ≈ 1 × 10^18 – 1 × 10^19) | log10 Pa s | Özet: "Kelvin viscosity log10 ηK≈18.0–19.0 Pa·s" | özet |
| "Best-fit viscosity structures" | çoğul olarak anılıyor; tek değer **OKUNAMADI** | – | Özet: "For the best-fit viscosity structures, central NAF slip-deficit rates reach 22 mm/yr" | özet |
| Schizosphere kalınlığı (elastik katman) | **OKUNAMADI** | km | – | – |
| Kelvin modülü / oran | **OKUNAMADI** | – | – | – |
| Deprem geçmişi | Anadolu'da son 2000 yıl | yıl | Özet: "including the last 2000 yrs of earthquake history across Anatolia" | özet |
| Uydurulan GPS verisi | 1999 öncesi on yılın kampanya GPS hızları + 7 yıllık sürekli postsismik veri | – | Özet: "campaign-mode Global Positioning System (GPS) velocities from the decade prior to the 1999 Mw 7.4 Izmit earthquake and seven years of continuously recorded postseismic deformation" | özet |
| Kesin son epok | **OKUNAMADI** (7 yıl → ~2006, çıkarım) | – | – | – |

Not (özetten, hesap): BSSA aralıkları G3 aralıklarıyla aynı. 10^18,6 ≈ 4,0 × 10^18, yani G3'ün η_M alt sınırı, BSSA'nın log aralığının alt ucuyla örtüşüyor. Buna göre G3 viskozitelerini büyük olasılıkla BSSA'daki blok modelinden alıyor. Bunu tam metin doğrulamadı.

Geometrik orta (yalnız aritmetik, makale değeri değil): η_M = 10^18,8 ≈ 6,3 × 10^18 Pa s; η_K = 10^18,5 ≈ 3,2 × 10^18 Pa s. İki makalede de aynı sonuç çıkıyor.

**Tek set çıkarılabiliyor mu? HAYIR.**
- İki viskozite için özette yalnız aralık var. Geometrik orta kuralı uygulanabilir ama makalenin "best-fit" değeri değildir.
- Burgers modelini PSGRN'de kurmak için gereken elastik katman (schizosphere) kalınlığı ve Kelvin/Maxwell modül oranı (PSGRN'deki `alpha`) özette yok. Bunlar olmadan model tanımsız.
- Ayrıca G3 modeli 1939–1999 dizisinin tamamıyla kurulmuş; yalnız 1999 kaynaklarıyla koşulursa makaledeki modelle aynı olmaz (INCELEME-2 Y4, değişmedi).

**2017 sonrası veriye uydurulmadı mı? EVET, uydurulmadı (özet düzeyinde teyit).** BSSA özeti uydurulan veriyi "1999 öncesi on yıl + 7 yıl sürekli postsismik" diye tanımlıyor. G3 viskozitelerini bu çalışmalardan alıyor. Yayım tarihleri: G3 2016-07-17, BSSA 2016-11-29 (ilk çevrimiçi; INCELEME-2). G3 özetindeki "By 2023 ..." ifadesi bir **öngörü**, veri değil; körlük beyanı için ilgili (Y13-iii).

---

## 4. Yamasaki, Wright, Houseman 2014 (M2, yalnız kayıt için): tam metinden

| Parametre | Değer | Birim | Kaynak yeri | Tam metin / özet |
|---|---|---|---|---|
| Reoloji | doğrusal Maxwell (tek viskoz mekanizma), geçici reoloji yok | – | §1, s. 3679: "in the context of a Maxwell-type viscoelasticity"; Özet: "elastic above Maxwell viscoelastic layers" | tam metin |
| Yöntem | 3B sonlu eleman, periyodik deprem döngüsü, sonsuz uzun düşey sağ yanal fay | – | §1, §3; Şekil 3 | tam metin |
| Uzunluk ölçeği L0 = alan kalınlığı | 40 | km | Tablo 1; §3, s. 3681 | tam metin |
| Elastik katman kalınlığı H | 12 (H′ = 0,3) | km | Tablo 1; s. 3682: "H′ is assumed to be 0.3 (H = 12 km)" | tam metin |
| Fay derinliği D | 16 (D′ = 0,4) | km | Tablo 1; s. 3681: "we set D′ = 0.4 (D = 16 km)" | tam metin |
| Kayma modülü μ (her yerde sabit) | 3,0 × 10^10 | Pa | Tablo 1 | tam metin |
| Poisson oranı ν | 0,25 | – | Tablo 1; s. 3681 | tam metin |
| Elastik katmanın viskozitesi | η′ = 10^20 (fiilen elastik) | boyutsuz | s. 3681: "η′ (= η/η0 = 10^20 ...) that deformation is in essence purely elastic" | tam metin |
| Deprem tekrar süresi Δt | 200 | yıl | Tablo 1; §5, s. 3692 | tam metin |
| Kayma / deprem | 3–6 (2Sx) | m | Tablo 1 | tam metin |
| Uzak alan göreli hız | 22,5 ± 7,5 | mm/yıl | §5, s. 3692; Şekil 11 yazısı (s. 3693) | tam metin |
| Viskozite ölçeği η0 = μΔt | ~2 × 10^20 (±2 kat belirsiz) | Pa s | §5, s. 3692: "η0 = μΔt = ~ 2 × 10^20 Pa s ... uncertain by about a factor of 2" | tam metin |
| **Tercih edilen model A**: blok tipi zayıf zon | η′ = 1, ηw′ = 0,01, ΘB′ = 0,3, ΩB′ = 1,0 | boyutsuz | §5, s. 3692: "The block-type LWZ model with η′ = 1, ηw′ = 0.01, ΘB′ = 0.3, and ΩB′ = 1.0 (corresponding to ΘB = 12 km and ΩB = 40 km ...) almost explains the data"; Şekil 11a–b | tam metin |
| A: zayıf zon genişliği ΩB | 40 | km | aynı; Şekil 11 yazısı | tam metin |
| A: zayıf zon kalınlığı ΘB (elastik katmanın tabanından ölçülür, yani 12–24 km derinlik) | 12 | km | Şekil 11 yazısı; §3, s. 3683: "vertical thickness measured from the base of the elastic layer" | tam metin (derinlik aralığı bu iki ifadeden hesaplandı) |
| A: zayıf zon viskozitesi | ~2,0 × 10^18 | Pa s | Şekil 11 yazısı (s. 3693); §7 Sonuçlar, s. 3696: "implying viscosity ~ 2 × 10^18 Pa s" | tam metin |
| Arka plan viskozitesi | ~2,0 × 10^20; sonuç cümlesinde "≥ 2 × 10^20" | Pa s | Şekil 11 yazısı (s. 3693); §7, s. 3696: "implying viscosities ≥ 2 × 10^20 Pa s" | tam metin |
| **Tercih edilen model B**: daha dar, daha zayıf blok | ηw′ = 0,005, ΩB′ = 0,6 → ΩB = 24 km, ΘB = 12 km, ~10^18 Pa s | km, Pa s | §5, s. 3692; Şekil 11c–d (s. 3693) | tam metin |
| **Tercih edilen model C**: Gauss tipi zayıf zon | ΩG = 40 km, ΘG = 12 km, ~2 × 10^18 Pa s | km, Pa s | Şekil 11e–f yazısı | tam metin |
| Uydurulan veri | sismik öncesi hızlar 1988–1997 (McClusky 2000) + depremden **6 ay sonraki** postsismik hızlar (Ergintav 2009'un 6 aylık uydurmalarından, Şubat 2000); yalnız 30,27° D'nin 50 km içindeki istasyonlar, faya paralel bileşen | – | §2, s. 3679–3680; Şekil 1–2 | tam metin |

**Tek set çıkarılabiliyor mu? HAYIR, kesin değil.** Şekil 11 yazısı "The preferred model has a weak zone width of ΩB = 40 or 24 km" diyerek iki blok modelini (A, B) ve bir Gauss modelini (C) birlikte "preferred" sayıyor. Özet de viskoziteyi "~10^18 ± 0.3 Pa s" diye bir aralık olarak veriyor. A, metindeki "almost explains the data" cümlesi ve Sonuçlar bölümündeki (§7) 2 × 10^18 yüzünden en çok anılan set. Ama makale tek bir set adlandırmıyor.

**PSGRN/PSCMP ile kurulabilir mi? HAYIR.** Model, faydan yanal olarak sınırlı bir zayıf zon (40 ya da 24 km genişlik) içeriyor. PSGRN yalnız yatay katmanlı yapı kabul ediyor (katman satırı = derinlik + özellikler, §5). Bu yüzden **M2 düşer**. Bu sonuç ön kayda "kurulamıyorsa" diye değil, "düşer" diye yazılmalı (INCELEME-2 Y4).

**2017 sonrası veriye uydurulmadı mı? EVET, uydurulmadı (tam metinden teyit).** Veri 1988–1997 ve 1999 sonrası ilk 6 ay.

---

## 5. PSGRN/PSCMP (Wang, Lorenzo-Martín, Roth 2006)

| Kalem | Değer | Kaynak yeri | Tam metin / kod |
|---|---|---|---|
| Resmî indirme adresi | GFZ "Tool Development Lab" sayfası (`gfz.de/en/section/physics-of-earthquakes-and-volcanoes/infrastructure/tool-development-lab`) indirme bağlantısı olarak GitHub'ı veriyor: `https://github.com/pyrocko/fomosto-psgrn-pscmp` (GPL-3.0). GFZ sunucusunda ayrı bir dosya bulunamadı. Eski bir GFZ FTP dizini (`ftp.gfz-potsdam.de/pub/home/turk/wang/`) yalnız bir arama özetinde geçti, doğrulanmadı. | GFZ sayfası (WebFetch, 11.11.2026) | sayfa |
| Depodaki sürüm | PSGRN "Version 2008", "July 2008"; girdi dosyaları `psgrn08` / `pscmp08`, "Last modified: Potsdam, July, 2008" | `src/psgrn/psgmain.f` satır 34, 41; `examples/psgrn08_input.dat` başlığı | kod |
| Desteklenen reolojiler (2008 sürümü) | **Burgers var.** Elastik, Maxwell ve SLS (standart doğrusal katı) Burgers'in özel durumları olarak tanımlı | `psgrn08_input.dat`: "Burgers rheology [a Kelvin-Voigt body (mu1, eta1) and a Maxwell body (mu2, eta2) in series connection] for relaxation of shear modulus is implemented. No relaxation of compressional modulus is considered." Özel durumlar: "(1) Elastic: eta1 and eta2 <= 0 ... (2) Maxwell body: eta1 <= 0 ... or alpha = 1 ... (3) Standard-Linear-Solid: eta2 <= 0" | kod |
| Burgers parametreleri | eta1 = geçici viskozite (Kelvin-Voigt sönümleyicisi); eta2 = kalıcı viskozite (Maxwell sönümleyicisi); alpha = mu1/(mu1+mu2), 0 < alpha ≤ 1. Gerilmesiz modül mu2, Vs ve ρ'dan türetilir | aynı dosya; `psgmain.f` alpha denetimi: `if(alf(i).gt.1.d0.or.alf(i).le.0.d0) stop` | kod |
| Burgers hangi sürümden beri | **OKUNAMADI.** 2008 sürümünde olduğu kesin. 2006 makalesinin (ilk sürüm) Burgers içerip içermediği makale okunamadığı için doğrulanmadı | – | – |
| PSGRN girdisi | gözlem derinliği, okyanus/kıta anahtarı; yatay uzaklık örneklemesi (nr, r1, r2, oran); kaynak derinlik örneklemesi (nzs, zs1, zs2); zaman örneklemesi (nt, 2'nin kuvveti; pencere [gün]); dalga sayısı integrali doğruluğu; gravite etkisi çarpanı (0–1); çıktı dizini ve dosya adları; katman sayısı ve her satırda `no depth[km] vp[km/s] vs[km/s] rho[kg/m^3] eta1[Pa*s] eta2[Pa*s] alpha` | `psgrn08_input.dat` | kod |
| PSCMP girdisi | PSGRN Green fonksiyonu dizini; gözlem noktaları (düzensiz enlem/boylam listesi, 1B profil ya da 2B ızgara); çıktı seçenekleri (yer değiştirme, gerilme, eğim, geoid, gravite, InSAR LOS, Coulomb); zaman serisi ve "snapshot" zamanları [gün]; dikdörtgen alt faylar: köşe enlem/boylam/derinlik, uzunluk, genişlik, doğrultu, eğim, yama sayıları, **başlangıç zamanı [gün]**, yama başına doğrultu/eğim kayması ve açılma [m] | `pscmp08_input.dat` | kod |
| Yanal heterojenlik | yok. Model yalnız katman satırlarından oluşuyor (yatay katmanlı yarı uzay) | `psgrn08_input.dat` "GLOBAL MODEL PARAMETERS" | kod |
| Afterslip için kullanılabilir özellik | Her alt fayın kendi `start_time` [gün] değeri var. Kinematik afterslip zamana yayılmış alt olaylar olarak girilebilir (INCELEME-2 Y6'daki seçeneklerden biri) | `pscmp08_input.dat` RECTANGULAR SUBFAULTS bölümü | kod |

Ön kayda yazılacak sürüm önerisi: "PSGRN/PSCMP 2008 (pyrocko/fomosto-psgrn-pscmp, commit hash dondurmada yazılır)". Commit hash'i bu iş kapsamında alınmadı, çünkü GitHub API bu oturumda bu depo için kapalı.

---

## 6. Toplu hüküm (Y3 / Y4 / Y6 açısından)

| Model | Makale | Tam metin okundu mu | Tek set var mı | 2017 sonrası veriye uydurulmadı (teyit düzeyi) | PSGRN/PSCMP ile kurulabilir mi |
|---|---|---|---|---|---|
| M1 | Hearn 2009 | hayır | **hayır** (aralık + tek yönlü sınır; elastik yapı, Kelvin modülü, afterslip yok) | evet (özet: 1999–2003) | Burgers desteklenir; parametreler eksik |
| M2 | Yamasaki 2014 | **evet** | hayır, kesin değil (3 "preferred" varyant) | evet (tam metin: 1988–97 + ilk 6 ay) | **hayır, düşer** (yanal zayıf zon) |
| M3 | Ergintav 2009 | hayır | hayır (τ = 1/150/3500 gün tek değerli; genlikler ve afterslip dağılımı yok) | evet (özet: ~7 yıl) | belirsiz: özete göre makale kinematik log uyduruyor, afterslip dağılımı vermiyor olabilir |
| M4 | DeVries 2016 G3 (+ 2017 BSSA) | hayır | hayır (yalnız aralıklar; elastik kalınlık ve alpha yok) | evet (BSSA özeti: 1999 öncesi on yıl + 7 yıl) | Burgers desteklenir; parametreler eksik |

**Sonuç:** Bugünkü erişimle **hiçbir model için Ek 1'e girecek tam ve tek bir parametre vektörü yok.** Okunabilen tek makale (Yamasaki 2014) zaten araç kısıtı yüzünden düşüyor. TASLAK-2'nin "En az bir model kalmazsa iş `veri-yok` ile kapanır" kuralı bugün harfiyen uygulanırsa sonuç `veri-yok` olur. Bu kararı ajan değil, kayıt sahibi verir. İki yol var:
1. Hearn 2009, Ergintav 2009 ve DeVries 2016/2017 tam metinleri bir insan tarafından tarayıcıdan ya da kurum erişimiyle indirilip `kayit/` altına konur, tablo tam metinden yeniden doldurulur. Ergintav ve DeVries G3 için açık kopyalar var (MIT DSpace, Harvard DASH); engel yalnız bu oturumdaki otomatik isteklere uygulanan hız sınırı.
2. Özetten alınan aralıklarla (geometrik orta) bir "özet düzeyi" set ön kayda açıkça bu etiketle yazılır. Eksik parametreler (elastik kalınlık, alpha) için ayrı, makaleden bağımsız ve önceden yazılmış bir kural konur. Bu, Y3'ün "tam parametre vektörü, makale sayfası/tablo" şartını karşılamaz. İnceleyicinin kabulü gerekir.

---

## 7. Dürüst sınır

- Hearn 2009, Ergintav 2009, DeVries 2016 ve DeVries 2017'nin tam metinlerini **okumadım**. Bu makalelerden gelen her sayı özetten, ya da Yamasaki 2014 için tam metinden alındı. "Tercih edilen model", elastik katmanlar, Kelvin modülü, afterslip sürtünmesi ve derinlik aralığı gibi istenen kalemlerin çoğu bu yüzden boş.
- Engeller: Wiley/AGU HTTP 403, GFZpublic HTTP 403 ("administrative rules"); MIT DSpace ve Harvard DASH "Web Firewall 429, Retry-After 900". Hiçbirini atlatmaya çalışmadım. DSpace'e toplam 3 (MIT) ve 2 (Harvard) istek gitti. Kişisel bir User-Agent ile yeniden deneme oturumun izin denetiminden geçmedi. Unpaywall API'sine istek atmadım (görev metnindeki yönerge gereği). Açık kopya araması için OpenAlex ve Semantic Scholar meta veri API'lerini e-posta göndermeden kullandım.
- Ergintav 2009'un MIT kopyası 175 KB. Tam makale mi yoksa kısaltılmış bir el yazması mı olduğunu bilmiyorum.
- Özetteki sayılar OpenAlex'in yeniden kurduğu özet metninden alındı ("10^19" gibi üsler orada "1019" diye düzleşmiş; bağlamdan 10^19 diye okudum). Yayıncı sayfasındaki özetle karakter karakter karşılaştırmadım.
- Yamasaki 2014'te "zayıf zon 12–24 km derinlikte" ifadesi makalede tek cümle olarak geçmiyor. H = 12 km ile "ΘB, elastik katmanın tabanından ölçülür" ifadesini birleştirerek ben hesapladım.
- PSGRN/PSCMP için yalnız GitHub'daki pyrocko paketini okudum (2008 sürümü). Wang'ın daha yeni bir sürümü (ör. 2019/2020) olup olmadığını doğrulamadım. GFZ sayfası da yalnız bu depoyu veriyor.
- Geometrik orta değerleri benim aritmetik hesabım; hiçbir makalede "tercih edilen" diye geçmiyor.
- Crossref tarihlerini yeniden çekmedim, INCELEME-2'deki tabloyu aktardım.
