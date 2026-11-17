# TR-13b ön kayıt, sürüm 3 (donduruldu): büyük doğrultu atımlı depremden 2–3 yıl önce sismisite yerelleşmesi, sınırlı koşu

Tarih: 16 Kasım 2026.
Durum: DONDURULDU (17 Kasım 2026; sürüm 3 + kod incelemesi düzeltmeleri K-1, K-2, K-3; tek koşu bu commit'ten sonra).
Gerçek katalogda hiçbir yerelleşme ölçüsü (V(q), z) hesaplanmadı. Ham arşivlere sha256 ve biçim denetimi yapıldı (§12.6);
ayrıca kod incelemesi sırasında bir kez, istenmeden, hazırlık aşaması gerçek arşivde koştu ve iki olayın sayımı görüldü
(§13 körlük beyanı). Kod incelemesi: `TR-13b_KOD-INCELEME.md` ("düzeltmeyle kabul").
Sürüm 2: `TR-13b_sinirli-kosu_ONKAYIT_surum2.md`; sürüm 1: `…_surum1.md`. İncelemeler: `TR-13b_INCELEME-1.md`
(Z1–Z5, commit d846acf), `TR-13b_INCELEME-2.md` ("düzeltmeyle kabul", commit cb4623a). Bu sürüm INCELEME-2'nin zorunlu
düzeltmeleri D-1…D-5'in hepsini ve öneriler Ö-a, Ö-b'yi işler (§11.2 eşleme tablosu). §3.8, §7.3, §7.4 ve §9.4,
INCELEME-2 §B'deki kesin cümlelerle aynen yazılmıştır.
Dayanaklar: `ESIK-DAYANAGI.md`, `TR-13_SAYIM.md` + Ek 1, `kayit/turetme/tr13/`.

Hesaplar (yalnız yapay ETAS; tek gerçek girdi `tr13_tamsayim.json`'daki üstveri satırları):
- **Başlık sayıları:** `kayit/turetme/tr13b/inc2/tr13b_inc2.py` → `tr13b_inc2.json` (INCELEME-2, tohum 20261122):
  listenin gerçek bileşimi, kendi R'de kalibrasyon, R0 kuralı.
- **Koşu betiği (D-4):** `kayit/turetme/tr13b/tr13b_kosu.py`; yapay sınaması `tr13b_test_yapay.py` (§12).
- Tarihçe: `tr13b_v2_mde.*` (sürüm 2; R = 80 kalibrasyonuyla üretildi, betiği D-2 uyarınca düzeltildi, json yeniden
  üretilmedi), `tr13b_mde.*`, `tr13b_K.*` (sürüm 1), `inc1/`.

## 0. Özet

- **Örneklem (üstveriden tahmin):** ana tasarım 16 olay / 14 küme. Ortak Mc kuralı (§3) Ishigaki 2009'u düşürür
  (N3bg 58 → ≈ 37 < 50; b = 1 varsayımıyla): **15 olay / 13 küme**. Keşif kümeleri (397 Superstition Hills + Hector
  Mine, 979 Ridgecrest, 395 İzmit) dışarıda **K = 10**. Hükmün öznesi bu K = 10 satırıdır. Gerçek sayı koşuda, gerçek
  Mc'lerle belli olur.
- **Bağlayıcı kural R0:** üç dallanmanın (0,4 / 0,6 / 0,8) üçünde de, hem bütün listede (K 13) hem keşif dışı listede
  (K 10) p ≤ 0,05. Plasebo denetimi **bilgi satırıdır**, hükmü bağlamaz (INCELEME-2 §B).
- **MDE: f ≈ 0,40 (bileşim, kendi R'de kalibrasyon; INCELEME-2)**, Monte Carlo hatası ± 0,03. f, önce-penceredeki arka
  planın 2 km'lik kırık bandına taşınan kesridir. Güç: f 0,2'de 0,30, 0,3'te 0,52, 0,4'te 0,80, 0,5'te 0,90, 0,6'da 0,97.
  Yapay yanlış alarm: sinyalsiz 0,020, durağan sürü 0,053, kenar ağ kaybı 0,025.
- **Okuma:** f ≈ 0,40, önce-penceredeki arka planın ortalama %40'ının kırık bandına toplanması, R 80'lik bölgede bant
  payının ≈ %8'den ≈ %18'e (≈ 2,2 kat) çıkması demektir. Sınav yalnız çok büyük ve örneklemin geneline yayılmış bir
  yerelleşmeyi görür. Etki büyüklüğünün literatür kaynağı okunamadı (§4); MDE'nin "kuramın kaç katı" olduğu bilinmiyor.
- **Beklenen bilgi kazancı küçüktür.** En olası sonuç "ayırt edilemez (MDE f ≈ 0,40)"dır ve bu önceden kabul edilir.
  Böyle bir sonuç TR-13'ü "güç yok"tan "büyük ve yaygın etki de görülmedi"ye taşır; BZ20 hakkında hüküm değildir. Bir
  "VAR" şaşırtıcı ve değerli olur, ama yalnız ileriye dönük sınava aday gösterir. Koşmanın maliyeti ≈ 0'dır ve iki
  sonucun anlamı önceden yazılıdır; koşmaya değer olmasının gerekçesi budur.
- **Koşu kodu (D-4)** yazıldı, yalnız yapay katalogla sınandı (§12): sinyalsiz → "ayırt edilemez", f = 0,5 → "VAR",
  bozuk girdi → "veri yok" / "geçersiz", 20 mutasyonun 20'si yakalandı. sha256'lar §12.1'de. Kestirilen tam koşu
  süresi ≈ 20–40 dk (4 çekirdek; §12.3); aşamalı ve kaldığı yerden sürdürülebilir.

## 1. Soru (sınırlı)

Temiz önce-pencereli, referans dönemi dolu, sığ doğrultu atımlı Mw ≥ 6,5 ana şoklardan önceki 3 yılda,
kümesizleştirilmiş arka plan sismisitesinin kesirsel alanı V(0,5), aynı bölgenin önceki 7 yılına göre, ETAS'ın
sinyalsiz ürettiğinden **büyük ölçüde** daha mı küçük (yerelleşme)? Yalnız büyük etkiyi sorar. Tahmin değildir.
"VAR" cümlesi yalnız BZ20'nin keşif olayları dışındaki bölgeler için kurulur.

## 2. Örneklem

- Ana tasarım (TR-13 Ek 1, değiştirilmeden): M ≥ 6,5, Mc = MAXC + 0,2, N3bg ≥ 50, temiz önce-pencere, referans dolu
  (tol 0,3). Liste `tr13_tamsayim.json`'dan (`M ≥ 6,5` ve `ref_gecer["0.3"]`) dosyadaki sırasıyla aynen alınır:
  16 olay, 14 küme. **Olay sırası** i (tohumlar, §3.5) bu 16 satırlık listedeki sıradır (0'dan; düşen olaylar sırayı
  değiştirmez).
- Eşleşik depremsiz kontrol şartı yok; yerine ETAS kalibrasyonu (§3).
- **Keşif kümeleri:** 397 (Superstition Hills 1987 + Hector Mine 1999), 979 (Ridgecrest 2019), 395 (İzmit 1999).
  Bunlar BZ20'nin ya da EGU 2020 özetinin iddiayı kurduğu olaylardır. Ana satırda tutulur ama "VAR" ayrıca bunlar
  dışarıdayken ister.
- **Üstveriden bileşim (b = 1 varsayımıyla; koşuda gerçek sayılarla yeniden kurulur):**

| i | Küme | Olay | R (km) | N3bg (Mc_önce) | Mc_önce / Mc_ref | Mc artışı | doyma sonrası N3bg |
|---|---|---|---|---|---|---|---|
| 0 | 397* | Superstition Hills 1987 | 66,5 | 215 | 2,0 / 1,7 | 0,4 | 86 |
| 1 | 160 | Loma Prieta 1989 | 102,1 | 608 | 1,3 / 1,4 | 0,8 | 96 |
| 2 | 303 | Kobe 1995 | 102,1 | 194 | 2,6 / 2,6 | 0,3 | 97 |
| 3 | 395* | İzmit 1999 | 277,4 | 227 | 2,9 / 2,9 | 0,4 | 90 |
| 4 | 397* | Hector Mine 1999 | 135,8 | 991 | 1,6 / 1,8 | 1,0 | 99 |
| 5 | 1141 | Big Lagoon açığı 2005 | 156,7 | 112 | 2,4 / 2,5 | 0,1 | 89 |
| 6 | (689) | Ishigaki 2009 — **düşer** | 76,7 | 58 | 2,1 / 2,3 | – | ≈ 37 < 50 |
| 7 | 727 | Darfield 2010 | 117,8 | 100 | 2,7 / 2,7 | 0 | 100 |
| 8 | 802 | Cook Boğazı 2013 | 57,7 | 74 | 2,6 / 2,6 | 0 | 74 |
| 9 | 901 | Kumamoto 2016 | 117,8 | 4225 | 0,5 / 0,6 | 1,7 | 84 |
| 10 | 942 | Chiniak açığı 2018 | 425,6 | 575 | 1,8 / 2,1 | 0,8 | 91 |
| 11 | 979* | Ridgecrest 2019 | 135,8 | 576 | 1,4 / 1,4 | 0,8 | 91 |
| 12 | 1139 | Jamaika açığı 2020 | 319,9 | 310 | 2,2 / 2,4 | 0,5 | 98 |
| 13 | 1035 | Gisborne açığı 2021 | 180,7 | 431 | 2,6 / 2,8 | 0,7 | 86 |
| 14 | 1139 | Küba açığı 2024 | 88,5 | 156 | 1,0 / 1,0 | 0,2 | 98 |
| 15 | 1144 | Jan Mayen 2025 | 57,7 | 223 | 1,7 / 1,8 | 0,4 | 89 |

  (* keşif kümesi.) R 57,7–425,6 km.
- **Eksik parça kuralı:** ham arşivde (`tr13-ham`, sha256 listesi `tr13_ham_sha256.txt`) bir olayın önce ya da
  referans penceresinin herhangi bir parçası yoksa o olay "veri yok" sayılır ve düşer; yeni indirme yapılmaz.
  Kaynak: ComCat olaylarında `ham/kat_ComCat_<id>.npz` ([t − 10 y, t), R_ind dairesi); ötekilerde
  `ham/tam3_<servis>_<id>.npz` ([t − 3 y, t), R) + `ham_tam/parca_<servis>_<id>_03…09.npz` ([t − 10 y, t − 3 y), R).
  Biçim denetimi (§12.6): 16 olayın bütün parçaları arşivde var.
- **Ö-a:** Küba 2024'ün referans penceresi Jamaika 2020 Mw 7,7 artçılarının bir kısmını içerebilir (GK74'ün M 7,7
  penceresi ≈ 86 km / ≈ 970 gün). Kural değişmez; koşu her olay için referans penceresindeki en büyük olayı, zamanını ve
  dış merkeze uzaklığını raporlar (`bilgi.ref_en_buyuk`).

## 3. Ölçü ve sınama (önceden sabit; koşu betiği §12 bunu uygular)

Adım sırası, her olay için:
1. Mc_önce ve Mc_ref TR-13 Ek 1'deki gibi (`tr13_tamsayim.json`'daki `mc_once` ve `ref_tam.mc`); **ortak
   Mc_b = max(Mc_önce, Mc_ref)**, önce ve referansa birlikte uygulanır. Süzgeç: [t − 10 y, t), t < 2026-01-01,
   derinlik ≤ 40 km.
2. GK74 m ≥ Mc_b olaylarla, indirilen bütün dairede (ComCat'te R_ind, ötekilerde R) koşulur; önce-pencere
   [t − 3 y, t) arka plan sayısı N3bg R dairesinde sayılır. GK74, §3.1'in derinlik süzgecinden sonra kalan olaylarla koşulur.
3. **Doyma kuralı:** N3bg > 100 ise Mc_b 0,1 artırılır, **GK74 yeniden koşulur**, sayı ≤ 100 olana dek yinelenir. Yükseltilen
   Mc hem önce-pencereye hem referansa uygulanır. Son adımda N3bg < 50 olursa olay düşer. Referans [t − 10 y, t − 3 y)
   arka plan sayısı N3bg + 5'ten azsa olay düşer (alt örnekleme yapılamaz). Gerekçe: güç (sürüm 2 §3.3).
4. Ölçü: dış merkezli eşuzaklık düzlemi, 5 km hücre, V(0,5), referanstan aynı sayıda olayla 200 alt örnek,
   z = (V_önce − ort) / sd; yerelleşme z < 0. BZ20'nin gerekçeli yeniden kurulumudur, aynısı değildir. Gerçek z'nin alt
   örnek tohumu `20261201 + 1000 × olay sırası + 50`.
5. **ETAS sıfır havuzları (D-2, D-4):** Sıfır havuzunun μ'sü her olayın kendi R'sinde, önce-pencere GK74 arka plan
   sayısı gerçek N3bg'ye eşit olacak biçimde kalibre edilir; kalibrasyon ≥ 40 deneme; havuzun ortalama N'si gerçek
   N3bg'nin ±%5'i dışındaysa kalibrasyon bir kez yinelenir, yine dışındaysa dal 2 (geçersiz).
   Uygulama: kalibrasyon iki adımdır (40 deneme μ(N) ile, 40 deneme düzeltilmiş μ ile; tohum
   `20261201 + 1000 i + 10 + dallanma sırası`). Yineleme μ'yü havuzun kendi ortalamasıyla ölçekler (μ × N3bg / ort;
   2000 bölge deneme sayılır) ve havuzu `20261201 + 1000 i + 20 + dallanma sırası` tohumuyla yeniden üretir.
   Sıfır havuzları olay başına ve dallanma başına **tam 2000** bölge, dallanma **0,4, 0,6 ve 0,8** (sıra 0, 1, 2);
   tohum **`20261201 + 1000 × olay sırası + dallanma sırası`**; havuz 4 parçada üretilir, parça p'nin üreteci
   `SeedSequence(tohum, spawn_key=(p,))`. Öteki ETAS parametreleri TR-13 §4.1. Her bölgede hem olay z'si hem plasebo
   z_p'si (önce [t − 6 y, t − 3 y), referans [t − 10 y, t − 6 y)) alınır. En çok olabilirlik dallanma uydurması yapılmaz.
   z'si tanımsız bölge ve önce-pencere arka plan sayısı 50'den az olan bölge, gerçek üyenin seçimiyle aynı biçimde,
   T1/R0 sıfırından ve D-3 verisinden düşer; ikisinin sayısı da raporlanır. z_p'si tanımsız bölge T1/R0 sıfırında
   kalır, yalnız plasebo satırından düşer (gerçek üyede z_p şartı yoktur). Kalibrasyonun ±%5 denetimi süzgeçten önce,
   2000 bölgenin tümünün ortalama N'siyle yapılır. Süzgeçten sonra boş kalan havuz dal 2'dir. (Kod incelemesi §E-1.)
6. **Küme puanı:** küme z = üyelerin z ortalaması. Sıfırda her üye kendi havuzundan bir çekiliş alır, küme içinde
   ortalanır. İki çok olaylı küme: 397 (Superstition Hills + Hector Mine), 1139 (Jamaika + Küba). Bir üye düşerse küme
   kalan üyeyle sürer; küme boşalırsa düşer.
7. **T1:** z̄ = küme z'lerinin ortalaması. Her dallanma d için p_d = P(z̄_sıfır,d ≤ z̄_gözlenen), **200 000 çekiliş**,
   tohum `20260900 + dallanma sırası`. Hem bütün liste (K_ana) hem keşif dışı (K_kd) için, aynı çekilişlerden.
8. Plasebo T1 (z̄_p, dallanma 0,6 sıfırı, bütün liste) hesaplanır ve p_plasebo raporda yazılır; plasebo
   penceresinin arka plan sayısı da yazılır. p_plasebo hükmü değiştirmez.
   (Uygulama: 200 000 çekiliş, tohum 20260909; z_p'si tanımsız üye plasebo satırından düşer.)
9. Monte Carlo hatası: her p için ikiterimli standart hata yazılır; 2000'lik tek havuzda havuz hatası ±0,02–0,03
   (INCELEME-1). p eşiğe ±0,03'ten yakınsa raporda "sınırda" diye işaretlenir; hüküm değişmez. **Koşu bir kez yapılır;
   Monte Carlo yüzünden "sınırda" çıkan p yeniden koşulmaz.**
- Bilgi satırları (hükmü değiştirmez): T2 (küme düzeyinde d = z − z_p, kesin işaret çevirme), T3 (üye z'sinin kendi
  0,6 havuzunun %5 niceliğini aşma sayısı, kesin binom p0 = 0,05), p_plasebo ve plasebo penceresi sayıları, havuz
  niteliği (tanımsız z payı, N < 50 bölge payı, ortalama N), Ö-a satırı, Mc artışları ve düşen olaylar.

## 4. Etki büyüklüğü ve kaynağı

| Kaynak | Değer | Etiket | Durum |
|---|---|---|---|
| BZ20 (GJI 223, 561–583): 5 ana şok öncesi 2–3 yıl yerelleşme; Parkfield'da ters yön | kesirsel alan azalmasının büyüklüğü **okunamadı** | **literatür** | tam metin 403; özetten yalnız yön ve zaman |
| EGU 2023 özeti | 2–10 yıl önce geniş hacimde etkinleşme, 2–3 yıl önce sönme; yer dış merkezi içermeyebilir | **literatür** (özet) | yön ve yer tek anlamlı değil |
| Hasar reolojisi (Ben-Zion ve Zaliapin) | nitel öngörü, sayı yok | **kuram** | nicel değer yok |
| f ≈ 0,2 (TR-13 sayımı, "orta") | bant içi oran ≈ 2,5 kat | **tahmin** (benzetim) | makullük doğrulanamadı |
| Bu taslağın MDE'si | f ≈ 0,40 (bileşim, kendi R'de kalibrasyon; INCELEME-2) | **hesap** (yapay, gerçek bileşim) | §5 |

Etki büyüklüğünün kaynağı olmadığı için "MDE kuramın kaç katı" sorusu yanıtlanamıyor (INCELEME-1 F).

## 5. MDE ve ×0,5 / ×2 duyarlılığı (`inc2/tr13b_inc2.json`, INCELEME-2 §B)

Bileşimde (15 üye, 13 küme, keşif dışı 10), μ kendi R'de kalibre; Monte Carlo hatası red oranlarında ≈ ±0,01–0,015,
güçte ≈ ±0,03:

| Kural | D0 sinyalsiz | D1 sürü | D4 kenar ağ | f 0,2 | 0,3 | 0,4 | 0,5 | 0,6 | MDE f |
|---|---|---|---|---|---|---|---|---|---|
| T1 tek dallanma 0,6, bütün liste (karşılaştırma) | 0,051 | 0,126 | 0,067 | 0,48 | 0,72 | 0,93 | 0,96 | 0,99 | 0,34 |
| **R0 (bağlayıcı)** üç dallanma × (bütün liste ve keşif dışı) | **0,020** | **0,053** | **0,025** | **0,30** | **0,52** | **0,80** | **0,90** | **0,97** | **0,40** |
| R1 R0 + plasebo p > 0,20 (sürüm 2 tam kuralı; kaldırıldı) | 0,014 | 0,035 | 0,018 | 0,25 | 0,43 | 0,68 | 0,72 | 0,75 | yok |
| R1b R0 + plasebo p > 0,05 (kullanılmaz) | 0,018 | 0,047 | 0,022 | 0,29 | 0,50 | 0,78 | 0,85 | 0,90 | 0,43 |
| R3 R0, eşik en kötü bozulmaya göre (kullanılmaz) | 0,019 | 0,050 | 0,023 | 0,29 | 0,51 | 0,80 | 0,89 | 0,97 | 0,40 |
| R4 fark z − z_p ile T1 (bilgi) | 0,028 | 0,029 | 0,030 | 0,15 | 0,22 | 0,42 | 0,51 | 0,66 | > 0,6 |

- **MDE (R0): f ≈ 0,40 (± 0,03).** Sürüm 2'nin "MDE > 0,5" sayısı plasebo kapısının güce koyduğu ≈ 0,75 tavanının
  ürünüydü (INCELEME-2 §B.1); sürüm 2 tablosu `_surum2.md`'de durur.
- **×0,5 / ×2:** yarısı (f 0,2) güç 0,30; iki katı (f 0,8) benzetim aralığının dışında (f 0,6'da zaten 0,97).
  Yarısı için gereken K ölçülmedi; sürüm 1'in K tablosuna göre ≈ 60–80 bölge (**tahmin**).
- **Koşudan önce yeniden hesap (K5):** koşu betiğinin 4. aşaması aynı R0 kuralının gücünü listenin gerçek (R, N3bg)
  değerleriyle yeniden ölçer (dallanma 0,6, ayrı kalibrasyon, üye başına sinyalsiz 200 ve f = 0,2…0,6 için 150 bölge,
  20 000 çekiliş, tohum 20260999; havuz tohumları `20261201 + 1000 i + 60 + k`). Bu değer **yalnız "ayırt edilemez"
  cümlesindeki sayıyı** belirler; hüküm kuralını değiştiremez.
- Bant payı (yapay, R 80, N3bg 100; sürüm 1 hesabı): f = 0 → %8, f = 0,4 → %18 (2,2 kat), f = 0,5 → %20 (2,5 kat).
  Büyük R'li bölgelerde (Chiniak 426 km, Jamaika 320 km) bandın payı daha küçüktür, yani aynı f daha aşırı bir
  yoğunlaşmadır.

## 6. Plasebo denetiminin yapay sınaması

- Sürüm 2 bölüm B (R 80, N3bg 100, K 14 türdeş): denetim sürü ve ağ bozulmasının yanlış alarmını ≈ %30 azaltıyor,
  gücü de ≈ %20–35 düşürüyordu (`_surum2.md` §6).
- **INCELEME-2 (bileşim, kendi R'de kalibrasyon):** denetim seçici değil: R0 reddi içinde plasebonun kestiği pay D0 0,30,
  D1 0,34, D4 0,28, sinyal 0,16–0,23. Ortalama kaymalar (D0'a göre): D1'de z −0,17, z_p −0,15; D4'te z −0,09,
  z_p −0,06. Yani plasebo sinyalsiz, bozulmalı ve sinyalli "VAR"ları aşağı yukarı aynı oranda keser; bu α'yı
  sıkılaştırmanın pahalı bir eşdeğeridir. Bu yüzden bilgi satırıdır (§3.8, §9.4).
- Sürü ve ağ senaryolarının gerçek bölgelerdeki sıklığı ölçülmedi (INCELEME-1'in seçimi).

## 7. Hüküm dalları (sıra kodda sabit; gerçek z'ler 1–2'den sonra hesaplanır)

1. **Veri yok:** ham arşiv sha256'ları `tr13_ham_sha256.txt` ile uyuşmuyor, ya da §2–3 kurallarından sonra keşif dışı
   K < 8. MDE yine yazılır (f ≈ 0,40, INCELEME-2). Keşif dışı K 8 ya da 9 ise koşu sürer; cümlede o K'nin yeniden
   hesaplanan MDE'si kullanılır.
2. **Geçersiz:** koşu betiği yapay girdiyle (her olayın R ve N3bg'si, dallanma 0,6) çalıştırıldığında (a) sinyalsiz
   yapayda R0'ın yanlış alarmı > 0,05 ya da (b) f = 0,4'te R0'ın gücü 0,65'in altında. Gerçek z görülmeden koşar.
   Ayrıca: bir olay ve dallanma için sıfır havuzunun ortalama N'si yinelemeden sonra da gerçek N3bg'nin ±%5'i dışında
   (§3.5).
3. **Büyük etki VAR:** üç dallanmanın üçünde de bütün listede p ≤ 0,05 **ve** üçünde de keşif dışı listede
   p ≤ 0,05. Cümle: "BZ20'nin keşif olayları dışındaki K = … bölgede, ana şoktan önceki 3 yılda kümesizleştirilmiş arka
   plan, ETAS'ın ürettiğinden belirgin biçimde yerelleşmiş. Tahmin ya da alarm iddiası değildir; ileriye dönük sınav ayrı
   ön kayıt ister." p_plasebo ≤ 0,05 ise cümleye eklenir: "Aynı bölgelerin 3 yıl önceki penceresi de ETAS'a göre
   yerelleşmiş görünüyor (p = …); sonuç ETAS dışı durağan bir bozulmadan ayrılamıyor."
4. (Kaldırılır; "ETAS uyumsuzluğu" dalı yoktur.)
5. **Ayırt edilemez (MDE = …):** öteki her durum. Cümle: "Keşif dışı K = …; bu bileşimle görülebilir en küçük etki
   f ≈ … (koşudan önce, listenin gerçek R ve N3bg'siyle yapayda yeniden hesaplanan değer). Daha küçük yerelleşme
   hakkında bilgi yok." (Ön kayıttaki değer: f ≈ 0,40 (bileşim, kendi R'de kalibrasyon; INCELEME-2).)
6. **H0 hükmü yoktur.** z̄ > 0 da "ayırt edilemez"dir.

## 8. Olumsuz sonuç ne söyler, ne söylemez

- Söyler: bu ölçüyle (dış merkezli R = max(2L, 50 km) daire, 5 km hücre, V(0,5), GK74, referans alt örneklemeli z)
  ve ETAS sıfırına göre, önce-penceredeki arka planın ≈ %40'ının kırık bandına toplanması (bant payının ≈ 2,2 kat
  (R 80'de) artması) BZ20'nin keşif olayları **dışındaki** 10 bölgede, ortalama olarak, olağan değildir.
- Söylemez: BZ20 yanlış. BZ20'nin kendi olayları hakkında hiçbir şey; BZ20'nin ölçüsü (voksel, en yakın komşu
  kümesizleştirmesi, seçimsiz bölgesel ızgara, yeniden karıştırılmış katalog anlamlılığı); daha küçük yerelleşme;
  dış merkezi içermeyen yerelleşme; "sönme"; M ≥ 6,0 örneklemi; Marmara.
- Ortalama etki; birkaç bölgeye sınırlı yerelleşme hakkında bilgi yok.
- Bu sonuç BZ20'yi ne doğrular ne çürütür.

## 9. Varsayımdan bağımsız kusurlar ve çözümleri

1. **Yanlış alarm (%13–37 anma):** ETAS'tan olay başına, üç dallanmayla kalibre eşik (§3). ETAS içinde α ≤ 0,05
   (bileşimde R0'ın gerçek α'sı 0,020).
2. **ETAS dışı bozulmalar (sürü, ağ):** R0'ın tutuculuğu (§9.4); yapayda yanlış alarm 0,025–0,053. Kalan risk
   yazılır. Bozulma senaryolarının yoğunluğu INCELEME-1'in ve INCELEME-2'nin seçimidir; gerçek sıklık ölçülmedi.
3. **Ölçü yeniden kurulum:** BZ20 tam metni okunursa dondurmadan önce karşılaştırılır; fark yazılır, ölçü değişmez.
4. Plasebo denetimi yapay sınamada seçici değil (INCELEME-2 §B) ve p > 0,20 kapısı güce ≈ 0,75 tavan koyuyor;
   bu yüzden bilgi satırıdır. ETAS dışı bozulmalara karşı koruma, üç dallanma × iki liste birlikteliğinin tutuculuğudur:
   yapayda yanlış alarm sinyalsiz 0,020, durağan sürüde 0,053, kenar ağ kaybında 0,025. Bozulma yoğunlukları seçimdir;
   gerçek sıklıkları ölçülmedi. Kalan risk budur.
5. **Doyma kuralı** yoğun bölgelerde küçük olayları atar (Kumamoto'da Mc 1,7 birim artar); H0 yönünde.
6. **Temsil:** keşif dışı 10 küme: Yeni Zelanda 3, Kaliforniya 2, Japonya 2, Alaska 1, Karayip 1 (iki olay),
   Jan Mayen 1. Doğu Akdeniz yok. Marmara'ya çevrilmez.
7. **Bölge yarıçapı:** MDE gerçek R'lerle (58–426 km) hesaplandı. Benzetimde öteki fay parçalarının boyu 20–60 km sabit;
   büyük R'li bölgelerde yapı gerçekçi olmayabilir.
8. **Sıfır havuzu ile gerçek üye arasındaki asimetriler (kod incelemesi, `TR-13b_KOD-INCELEME.md` §B):**
   (a) Sıfır havuzunda z'si tanımsız bölge payı ortalama %0,7 (üye başına %0–2,7); bunlar `z_olcu`'nun "referans <
   n + 5" ve "n < 5" kurallarından gelir ve gerçek üyenin "referans arka planı < N3bg + 5 → düşer" kuralının eşidir;
   `tr13_guc.V_q`'nun IndexError'ı 750 yapay bölgede hiç görülmedi. Yanlılık ölçülemeyecek kadar küçüktür.
   (b) Gerçek üye N3bg ≥ 50 şartıyla girer; sıfır havuzu ve D-3 verisi de aynı şartla süzülür. Şartsız sıfır,
   bileşimde R0 yanlış alarmını −0,001 (H0 yönü), bütün üyelerin N3bg'si 55 olduğunda +0,003 ("VAR" yönü) kaydırıyordu.
   (c) Sürüm 3'ün ilk betiği sıfırdan z_p'si tanımsız bölgeleri de atıyordu (havuzun ≈ %10'u, z'leri ortalamadan
   ≈ 0,3 düşük); bu, yanlış alarmı bileşimde 0,016'dan 0,022'ye çıkarıyordu ve D-3'te görünmüyordu. Düzeltildi.
   Düzeltilmiş betikle bileşimde R0: sinyalsiz yanlış alarm 0,018, f = 0,4 gücü 0,78 (havuz 1000, ± 0,003 / ± 0,02);
   başlıktaki 0,020 / 0,80 ile Monte Carlo hatası içinde aynıdır, §0 ve §5 sayıları değiştirilmedi.
9. **Isınma:** yapay bölgede GK74 5 yıllık ısınma dönemini de görür, gerçek katalogda [t − 10 y, t) öncesi yoktur.
   Referans penceresinin ilk aylarında kümesizleştirme biraz farklı olabilir; etkisi ölçülmedi.
   Ayrıca yapay bölgede GK74 R + 30 km'lik dairede koşulur; ComCat dışı gerçek olaylarda yalnız R dairesi indirildi.
   Gerçek biçimli yapay kataloglarla uçtan uca seride (`TR-13b_KOD-INCELEME.md` §D) bu iki farkın net etkisi H0
   yönündedir (sinyalsiz p'ler yukarı kaymış).

## 10. Yeniden açma şartı

(a) BZ20 tam metni meşru yoldan okunur ve ölçü ya da etki büyüklüğü bu taslaktakinden farklıdır. (b) Yazarlardan bağımsız
bir ETAS yanlış alarm sınaması yayımlanır. (c) Daha düşük Mc'li açık bölgesel katalog keşif dışı K'yi ≥ 25'e çıkarır.
(d) "VAR" çıkarsa: ileriye dönük, alarm biçimli ayrı ön kayıt.

## 11. İnceleme eşlemeleri

### 11.1 INCELEME-1

| Madde | Nerede |
|---|---|
| Z1 keşif kümeleri dışarıda, hükmün öznesi | §0, §2, §7.3, §8 |
| Z2 MDE gerçek (R, N3bg) bileşimiyle; başlık; R 58–426 | §0, §2, §5 |
| Z3 çok olaylı küme puanı | §3.6 |
| Z4 tek dallanma kuralı (0,4/0,6/0,8'in üçü); uydurma yok | §3.5, §3.7, §7.3 |
| Z5 plasebo denetimi | §3.8 (INCELEME-2 ile bilgi satırı), §6 |
| Ö1–Ö4 | §2, §3 |

### 11.2 INCELEME-2

| Madde | Nerede |
|---|---|
| D-1 §3.8, §7.3, §7.4, §9.4 kesin cümleler; "MDE > 0,5" yerine f ≈ 0,40; §5'e R0 satırı; §6'ya seçicilik | §3.8, §7.3, §7.4, §9.4 (aynen); §0, §4, §5, §7.5; §5 tablo; §6 |
| D-2 (K1) kendi R'de kalibrasyon, ≥ 40 deneme, ±%5, bir yineleme, sonra dal 2; `tr13b_v2_mde.py` düzeltmesi | §3.5 (aynen), §7.2; `tr13b_v2_mde.py` `kalibre_R`; koşu betiği `kalibre`, `kal_tamam` |
| D-3 (K2) dal 2'nin yapay ölçütü; üye/küme düşme kuralı | §7.2 (aynen), §3.6; koşu betiği aşama 4 |
| D-4 (K3) koşu betiği, D-3 denetimi, sha256; tam 2000; tohumlar; 200 000 çekiliş; tek koşu | §3.5, §3.7, §3.9, §12 |
| D-5 §8'e üç ek | §8 |
| K4 (keşif dışı K 8–9) | §7.1 |
| K5 (MDE yeniden hesabı: betik ve tohum) | §5, §12 |
| Ö-a Küba 2024 referans penceresi | §2, bilgi satırı |
| Ö-b "gerçek sıklık ölçülmedi" | §6, §9.2, §9.4 |

## 12. Koşu betiği (D-4)

### 12.1 Dosyalar ve sha256

| Dosya | sha256 |
|---|---|
| `kayit/turetme/tr13b/tr13b_kosu.py` (koşu betiği; kod incelemesinden sonra) | `d2494e6d37d74803ef569ed97293e1a391192a64fcf0b2cf5712679472d584a0` |
| `kayit/turetme/tr13/tr13_guc.py` (ETAS, GK74 düzlem, V(q), z; değiştirilmedi) | `0223ca7a0b55a26f27c9c04af183cbc53150f07d22141f7e897f6a7201d035b2` |
| `kayit/turetme/tr13/tr13_sayim.py` (gk74, uzak, sabitler; değiştirilmedi) | `d526db7de33a816c6e4217cafb2fa034c4060ff27b9e6b864145388f829fbc9b` |
| `kayit/turetme/tr13b/tr13b_test_yapay.py` (yapay sınama; koşuya girmez) | `3a24af28714eb187a0a3670aa124cc907258ebeb9f605bae6cf6b94e64652fd6` |

Bağımsız kod incelemesi betikte üç değişiklik istedi (K-1, K-2, K-3); yeni sha256 yukarıdadır (eski: `1bc2277b…`) ve
§12.4–12.5 sınamaları yeni betikte yeniden koşuldu (§12.7).

Gerçek kip yalnız bu ön kaydın "Durum:" ile başlayan satırı dondurma sözcüğünü içerdiğinde ve yukarıdaki üç sha256 bu
dosyada yazılı olduğunda çalışır (`dondurulmus_mu`). Kapı `kos()` işlevinin içindedir: içe aktarılarak çağrıldığında da,
gerçek arşiv dizini ya da gerçek sha256 listesi verildiğinde dondurulmamış ön kayıtla hiçbir şey açılmaz ve yazılmaz;
gerçek girdiyle yalnız ön kayıt ayarı (havuz 2000, B_ref 200, 200 000 çekiliş, sınama düğmeleri kapalı; çekirdek sayısı
serbest) kabul edilir. Dondurma satırı tam olarak "Durum: DONDURULDU …" biçiminde yazılır; satırda olumsuzlama bulunmaz.

### 12.2 Aşamalar ve kilit

`python3 -I -B kayit/turetme/tr13b/tr13b_kosu.py kos` → `kayit/turetme/tr13b/kosu/`:
1. girdi: iki arşivin sha256'sı (uyuşmazlık → dal 1); arşivler `/mnt/project-files/turetme/tr13-ham/` + bilinen adla
   doğrudan açılır, dizin taranmaz; gereken üyeler belleğe okunur, diske açılmaz.
2. hazırlık: §3.1–3.3 (yalnız sayı); keşif dışı K < 8 → dal 1.
3. kalibrasyon ve sıfır havuzları (§3.5); ±%5 iki kez tutmazsa → dal 2.
4. D-3 yapay denetimi ve MDE yeniden hesabı (§5, §7.2) → geçmezse dal 2. **Gerçek z bu aşamadan önce hesaplanmaz.**
5. gerçek z ve z_p; `gercek_z.json` bir kez yazılır, kesintiden sonra yeniden hesaplanmaz.
6. T1, R0, bilgi satırları; `tr13b_hukum.json` **bir kez** ("x" kipi) yazılır. Dosya varsa betik hiçbir şey
   hesaplamadan çıkar.
Durum dosyası `kosu/durum.json` her aşamadan sonra; sıfır havuzu parçaları `kosu/havuz/*.npy` tamamlandıkça yazılır.
Kesilen koşu aynı komutla kaldığı yerden sürer (var olan parça yeniden üretilmez; tohumlar sabit olduğundan sonuç
aynıdır).

### 12.3 Süre kestirimi

Listenin üstveri (R, doyma sonrası N) değerleriyle yapay bölge başına süre ölçüldü (B_ref 200, olay ve dallanma başına
6 bölge; `numpy`, tek çekirdek): R ≤ 180 km'de 0,023–0,095 s, Chiniak (426 km) ≈ 0,09 s. Toplam: sıfır havuzları
15 × 3 × 2000 ≈ 3500 s, kalibrasyon ≈ 70 s, D-3 havuzları ≈ 510 s; tek çekirdekte ≈ 4100 s, **4 çekirdekte ≈ 17 dk**;
süreç ek yükü ve ölçüm gürültüsüyle **20–40 dk** beklenir. 2 saatin altında; yine de koşu aşamalı ve sürdürülebilirdir
(§12.2). Gerçek katalogda GK74 ve doyma döngüsü (Kumamoto'da ≈ 17 adım) dakikalar mertebesindedir.

### 12.4 Yapay uçtan uca sınamalar (`tr13b_test_yapay.py uctan`)

Sahte arşiv: gerçek arşivlerle aynı üye adları (`ham/kat_ComCat_…`, `ham/tam3_…`, `ham_tam/parca_…_03…09`,
`ham/sayim_tam_satirlar.json`), sahte sha256 listesi ve sahte `tamsayim.json`; 16 yapay olay (ComCat, ISC, GeoNet
biçimleri; antimeridyen dahil), 14 küme (397 ve 1139 iki üyeli), keşif dışı 11; listeye girmemesi gereken iki satır
(M 6,3; referans geçmiyor). Kataloglar dallanma 0,6 yapay ETAS'tan, [t − 10 y, t), lat/lon ve ms biçiminde. Sınama
ayarı küçüktür (havuz 150, B_ref 50, 40 000 çekiliş, D-3 havuzları 60/50); kalibrasyon gerçekteki gibi 40 + 40.

| Sınama | Girdi | Beklenen | Sonuç |
|---|---|---|---|
| E1 | sinyalsiz | ayırt edilemez | **ayırt edilemez** (dal 5); p bütün 0,145/0,176/0,193, keşif dışı 0,139/0,186/0,210; D-3 yanlış alarm 0,031, f 0,4 gücü 0,89, MDE f ≈ 0,31; gerçek z D-3'ten sonra hesaplandı |
| E2 | f = 0,5 her olayda | VAR | **VAR** (dal 3); bütün p ≤ 0,003 |
| E3a | arşivde bir bayt bozuk | veri yok | **veri yok** (dal 1, sha256); havuz ve z hesaplanmadı |
| E3b | 5 olayda referans parçası eksik | veri yok | **veri yok** (dal 1, keşif dışı K = 6 < 8) |
| E3c | sıfır havuzu μ'sü × 1,4 bozuk | geçersiz | **geçersiz** (dal 2, ±%5 iki kez); z hesaplanmadı |
| E3d | D-3'ün sinyalsiz havuzuna f 0,4 | geçersiz | **geçersiz** (dal 2, D-3 yanlış alarm 0,92); z hesaplanmadı |
| E3e | E3d'nin dizininde ikinci koşu | kilit | hiçbir şey hesaplanmadı, hüküm dosyası bayt bayt aynı |

Yapay sınama ayarında MDE'nin (0,31) başlıktaki 0,40'tan küçük olması beklenir: yapay olayların R'si 58–95 km, keşif
dışı K 11'dir.

### 12.5 Birim sınamaları ve mutasyonlar

Birim sınamaları U1–U14 (sabitler ve tohum formülleri; eşuzaklık izdüşümü; sha256 ayrıştırma ve uyuşmazlık;
hazırlık: pencere sınırları, körlük, ortak Mc, düşme kuralları, doyma ve GK74'ün bağımsız yeniden hesabı; kalibrasyonun
kendi R'yi kullanması ve R 200'de ±%8 isabeti; p yönü, R0, MDE ara değeri; plasebonun hükmü değiştirmemesi ve cümleler;
küme ortalaması; küme yapısı ve keşif dışlama; hüküm kilidi; ±%5 ve D-3 eşikleri): 11 sınama grubunun hepsi geçti.

Mutasyonlar (betiğin kopyasına uygulanır; birim + ilgili uçtan uca sınama): **20 / 20 yakalandı.**

| # | Mutasyon | Yakalayan |
|---|---|---|
| M01 | R0'da iki liste "ve" yerine "veya" | U6, U7 |
| M02 | bütün liste eşiği 0,10 | U6 |
| M03 | kalibrasyon R = 80 (K1 hatası geri) | U5 |
| M04 | plasebo hükmü bağlar | U7 |
| M05 | keşif kümeleri dışlanmaz | U9 |
| M06 | sha256 denetimi atlanır | U3 |
| M07 | hüküm dosyası üzerine yazılabilir | U10 |
| M08 | kilit denetimi kaldırılır | U10 |
| M09 | kuyruk yönü ters | U6 |
| M10 | küme yerine üye ortalaması | U8 |
| M11 | düşme eşiği N3bg < 30 | U4 |
| M12 | D-3 kapısı kaldırılır (gerçek z D-3 başarısızken hesaplanır) | E3d |
| M13 | tohum formülü değişir | U1 |
| M14 | kalibrasyon toleransı ±%10 | U14 |
| M15 | önce-pencere 2 yıl | U4 |
| M16 | veri yok eşiği keşif dışı K < 5 | E3b |
| M17 | ortak Mc = min | U4 |
| M18 | D-3 güç eşiği 0,55 | U14 |
| M19 | doyma eşiği 150 | U4 |
| M20 | körlük süzgeci gevşer (ana şok anı ve sonrası) | U4 |

Yeniden üretim (≈ 18 dk, 4 çekirdek): `python3 -I -B kayit/turetme/tr13b/tr13b_test_yapay.py <karalama> birim`,
`… uctan`, `… mutasyon`. Bu tablodaki sayılar betik sha256'sı `1bc2277b…` (inceleme öncesi) üzerinde üretildi; yeni betikteki yineleme §12.7'dedir.

### 12.6 Gerçek arşivlerde yapılan tek şey

`tr13b_kosu.py bicim`: iki arşivin sha256'sı listeyle uyuşuyor (2e11e7d2…, 7f40414b…); 16 olayın gereken bütün üyeleri
arşivde; örnek npz anahtarları (t, la, lo, de, m) doğru; `sayim_tam_satirlar.json` 16 olayın hepsini içeriyor. Sayı,
Mc, GK74, V(q) ya da z hesaplanmadı.

### 12.7 Kod incelemesinden sonra yeniden koşulan sınamalar (betik sha256 `d2494e6d…`)

İnceleme oturumu kesildiği için son sınamaları kök oturum koştu; betiğe dokunulmadı. Çıktılar `kayit/turetme/tr13b/kodinc/`.

| Sınama | Sonuç |
|---|---|
| Yazarın `birim` (U1–U14, 11 grup) | 11 / 11 geçti (`yazar_birim_yenikod.json`) |
| Yazarın `uctan` (E1–E3e) | 7 / 7 geçti; E1 ayırt edilemez (p bütün 0,195/0,192/0,237; D-3 yanlış alarm 0,025, f 0,4 gücü 0,93, MDE 0,30), E2 VAR (p ≤ 0,008) (`yazar_uctan_yenikod.json`) |
| Yazarın 20 mutasyonu | 20 / 20 yakalandı (`yazar_mutasyon_yenikod.json`) |
| İnceleyenin `birim` Y1–Y6, `uctan` Yu1–Yu4 | 6 / 6, 4 / 4 geçti |
| İnceleyenin 21 mutasyonu | 21 / 21 yakalandı (ikisi ek sınamayla; `test_mutasyon.json`, `test_mutasyon2.json`) |
| Uçtan uca seri, sinyalsiz, 20 liste (küçültülmüş ayar: havuz 100, B_ref 50, 40 000 çekiliş) | 0 / 20 "VAR"; 20'si "ayırt edilemez" (`test_seri_f0.json`) |
| Uçtan uca seri, f = 0,4, 12 liste (aynı ayar) | 9 "VAR", 2 "ayırt edilemez", 1 "geçersiz" (D-3 yanlış alarm 0,056 > 0,05; küçültülmüş havuzun gürültüsü) (`test_seri_f04.json`) |

Seri küçük ayarda koştuğu için 9/12 (0,75) güç kestirimi kabadır (ikiterimli %95 aralık ≈ 0,43–0,95); başlıktaki MDE
f ≈ 0,40 (güç 0,80) ile çelişmez. Gerçek koşuda D-3 kapısı tam ayarla (havuz 200/150) yeniden hesaplanır ve geçmezse
hüküm "geçersiz"dir (dal 2); bu durumda gerçek z hesaplanmaz.

## 13. Körlük ve İstanbul

Gerçek katalogda V(q), Gini ya da z hesaplanmadı; bu ön kayıt için yeni katalog indirilmedi; ham arşivlere sha256 ve
biçim denetimi yapıldı; ana şok sonrası pencere yok.

**Körlük beyanı (kod incelemesi olayı, `TR-13b_KOD-INCELEME.md` §G):** inceleme sırasında, kapının `kos()` içinde
olmaması yüzünden (K-1), eski betik bir kez gerçek arşivde ≈ 5 dakika koştu: sha256 denetimi, hazırlık (ortak Mc, GK74,
doyma, yalnız sayılar) ve yapay kalibrasyon ile 20 yapay havuz parçası. Gerçek katalogda V(q) ya da z hesaplanmadı;
`gercek_z.json` ve hüküm dosyası oluşmadı. Görülen: iki olayın hazırlık satırı (Superstition Hills 1987 N3bg 85, Loma
Prieta 1989 N3bg 94, Mc ve N_plasebo değerleri). Bunlar §2'deki üstveri sayımlarıyla (86, 96) aynı türden bilgidir ve
ölçü hakkında bilgi taşımaz; ölçü, eşikler ve hüküm kuralları bu olaydan sonra değiştirilmedi (kod değişiklikleri
K-1…K-3 yapay asimetri ölçümüne dayanır, bu sayılara değil). Çıktı silindi, commit edilmedi. Sonuç okunurken bu beyan
birlikte okunmalıdır. Koşu betiği t ≥ ana şok ve t ≥ 2026-01-01 olan satırları sayılmadan atar. Bütün
2026 verisi kördür; katalog 2025-12-31'de biter. Sonuç bir olasılık terimi değildir. İstanbul için mutlak olasılık
yazılmaz. İzmit 1999 bir keşif kümesidir ve Marmara terimi değildir.
