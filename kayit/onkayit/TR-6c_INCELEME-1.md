# TR-6c ön kaydı (TASLAK sürüm 1): bağımsız inceleme 1

16 Kasım 2026. İncelenen: `TR-6c_gerilme-olcer-kor-dogrulama_ONKAYIT.md` (TASLAK sürüm 1, commit be810ff) ve kodun
`--tasarim c` yolu (`tr6a_kosu.py`, `tr6a_yapay.py`, `tr6a_test_yapay.py`, `tr6c_prova_*.json`). Taslağı ve kodu ben
yazmadım. Yalnız yapay veri kullandım. Hiçbir katalog sorgusu yapmadım, hiçbir ham dosya ya da önbellek açmadım.
Bağlayıcı sınamayı koşmadım; `TR6C_ONKAYIT_SHA = None` kaldı. Ön kayıt metnini değiştirmedim; önerilerim aşağıdadır.

İnceleme tohumları: 91011 (küme düzeyi benzetim), 8801 ve 8802 (hücre yeniden koşuları). Prova tohumu 7311'i yalnız
parça baytlarını yeniden üretmek için kullandım. Bağlayıcı (20261114–20261117) ve tanı (601–608) tohumları
kullanılmadı. Betikler ve çıktılar `kayit/turetme/tr6/inc_c/` altındadır (§8).

## 1. Hüküm: RET (sürüm 2 gerekir, sonra ikinci bağımsız inceleme)

Taslağın ana fikri doğrudur. Yöntem sınaması, hükmün gerçekten kullandığı karşılaştırmayı (p̂₀ ile P(D | kapı))
sınamalıdır. Kenar etkisi H1 aleyhinedir ve p₀ = max(0,50; …) tabanı α'yı korur. Benim benzetimimde de yanlış "H1"
oranı modellenen her H0 dünyasında 0,05'in altında kaldı (§3.4). Kod metne uyuyor, prova parçaları bayt bayt yeniden
üretildi.

Yine de metin bu hâliyle dondurulamaz. Nedeni şu: **C1, gerçek koşunun kalibrasyon havuzunu sınamıyor.**
- Metin (§C3) ve kod p̂₀'ı bütün denemelerin sahte oylarından havuzluyor. Buna gerçek kapıyı geçmeyen denemeler de
  dahil.
- Gerçek koşuda ise sahte oylar yalnız K_kapı kümelerinden gelir (TR-6a §4.6).
- Sahte son pencereler gerçek ön pencerenin içindedir. Gerçek kapı yüksek ön sayımları seçtiği için sahte son sayımlar
  da yüksek gelir ve sahte düşüş oyu azalır.
- N0 31,36'da, gerçek koşudaki gibi yalnız kapıyı geçen denemelerin sahteleriyle hesap şunu veriyor:
  - p̂₀ − P(D | kapı) = −0,051 (z −8,3; tohum 8801, 20 000 deneme);
  - −0,044 (z −5,5; tohum 8802, (i));
  - −0,055 (z −7,2; tohum 8802, (ii)).
- Taslağın bu hücredeki "geçti" sonucu (+0,006) bir rastlantıdır. Kapıyı geçemeyen denemelerin sahteleri (p̂₀ ≈ 0,66)
  öteki yöndeki farkı dengeliyor.

Bu bulgu TR-6a Ek 1'in "p̂₀ aynı seçimi taşır ve beklenen değerde yanlılığı soğurur" cümlesini de yanlışlar.
TR-6c §C2 bu cümleyi "aynen devralır". Düzeltmek bir tasarım kararı ister (Z1–Z2) ve 31,36 hücrelerinin yeniden
provasını gerektirir. Prova sonucu bugünden bilinemeyeceği için hükmüm DÜZELTMEYLE KABUL değil, RET'tir.

Ağırlığı abartılmamalıdır. Etki yalnız gerçek oranı kapıya yakın (N0 ≲ 36) kümelerdedir (N0 36'da −0,003, N0 40'ta
+0,005). Önsayım dağılımında yanlış H1 oranı 0,016'dır. 28 kümenin 16'sı kapı sınırında olsa bile 0,034'tür. Ancak
kenar dışı 26 kümenin hepsi kapı sınırında olursa 0,057'ye çıkar (§3.4).

## 2. Zorunlu düzeltmeler (sürüm 2)

**Z1. C1'in havuzu gerçek koşununki olmalı.** §C3 "Tanımlar"daki p̂₀ maddesi şöyle değişmeli:
> "p̂₀ = ΣS_i / ΣJ_i; toplam yalnız gerçek kapıyı geçen (n_on ≥ 155, Mc_lob) ve gerçek Mc_son'u kestirilebilen
> denemeler üzerindendir. Gerçek koşuda sahte oylar yalnız K_kapı kümelerinden gelir (TR-6a §4.6)."

Kodda `hucre_ozeti_c` içindeki `_fark_se(c["SD"][var], c["J"][var], c["D"][kv])` çağrısı
`_fark_se(c["SD"][kv], c["J"][kv], c["D"][kv])` olmalı. Aynı değişiklik bilgi satırlarındaki üç `_fark_se`
çağrısına da yapılmalı. N0 ≥ 100 hücrelerinde kapı payı 1'dir; bu değişiklik oralarda sonucu değiştirmez.

**Z2. Kapı seçim yanlılığı açıkça ele alınmalı ve 31,36 hücreleri yeniden prova edilmeli.** Z1'den sonra i:31,36 ve
ii:31,36 hücrelerinde C1 tutmaz. Ölçütü bu hücrelere göre gevşetmek, başarısız hücreye göre ölçüt uydurmak olur. Yazar
dondurmadan önce şu yollardan birini seçmeli ve bağlayıcı olmayan tohumla yeniden prova etmelidir:
- (a) Tasarım değişikliği: kapı sayımı ya da sahte pencereler, sahte son pencereler gerçek kapı penceresinin içinde
  kalmayacak biçimde yeniden tanımlanır. Ardından Z1'li C1, 31,36 hücrelerinde de prova edilir.
- (b) Kabul ve sınır: §C2'deki devralma listesine "TR-6a Ek 1 kapı seçim yanlılığı paragrafının 'p̂₀ … soğurur' cümlesi
  geçersizdir" yazılır. Kapı sınırındaki artık (+0,05) ve onun α'ya etkisi tablo olarak verilir (§3.4'teki benim
  tablom kullanılabilir). Kapıya yakın küme payı yüksekken α'yı ≤ 0,05'te tutan, önceden yazılmış bir kural eklenir.
  Örneğin: ana kümelerin yarısından fazlasının kapı N0'ı < 40 ise p₀ tabanı 0,52 olur. Bu kuralın α'sı da hesapla
  gösterilir. 31,36 hücrelerinde C1, kapı koşullu havuzla bilgi satırı olur ve bunun gerekçesi metne yazılır.

Seçim yazarındır. İki yolda da TR-6a Ek 1 cümlesinin TR-6c'de geçerli olmadığı açıkça yazılmalıdır.

**Z3. Kenar hücrelerinde iki yanlı ölçüt eklenmeli (C1′ tek başına çok zayıf).** C1′, P(D | kapı) ≤ kesin + 3,5 SE
koşuludur. Hat zaten 0,064 (N0 1500) ile 0,174 (N0 4500) aşağıda olduğu için, bu kadar büyük bir yukarı kayma
yaratan bir kod hatası bile C1′'yü geçer. §C3 "Ölçütler"e şunlar eklenmeli:
> "**C1′a (N0 > 500; (i) ve (ii)):** C1'in kendisi (kapı koşullu havuzla p̂₀ − P(D | kapı), iki yanlı 3,5 SE).
> **C1′b (N0 > 500; yalnız (i)):** kümesizleştirmesiz (D4 biçimi) P(D | kapı), kesin Poisson P(D | H0) (N0_kul,
> 275 g) ile iki yanlı 3,5 SE içinde. C1′ yön ölçütü olarak kalır."

Prova verisiyle bu ölçütler tutar:
- C1′a: z −0,35 / +0,79 / −0,67 / −1,62;
- C1′b: z +0,59 (i:1500), −0,94 (i:4500).

C1′b (ii)'ye uygulanmaz, çünkü orada D4 oyu kümelenmeyle yukarı kayar (+0,03–0,04).

**Z4. "Neden 500" paragrafı dürüstçe yeniden yazılmalı.**
- Paragraf (i)'de hat − ham farkını (0,017), (ii)'de hat − kesin farkını (−0,020 ± 0,0035) kullanıyor. Sonra
  "toleransı aşmayan en büyük N0" diyor. Bu ölçüyle (ii)'de sınır 100 olurdu.
- Doğrusu şudur: 500, 5 noktalı ızgaradan seçilmiş bir sayıdır. Dayanağı tolerans değil, kaymanın yönü ve p₀ tabanıdır.
- Paragrafa şu cümle eklenmeli: "Önsayımda kapı N0'ları 316,3 ile 583,7 arasında boşluk bırakır. Bu aralıktaki her
  sınır aynı iki kümeyi (Tokachi-oki, Tohoku) kenar yapar. Sınır yazar bunu bilirken seçildi."

**Z5. Kural 4 (A = 0) tek yönlüdür; kontrol satırları da aynı kenar etkisini taşır.**
- Ters yön notu: kenar kümelerinde A'yı 0 sayıp paydada tutmak, ters yön notunu ("gölgede anlamlı artış", rakip
  açıklama R3) yalnız zorlaştırır. Yazar Tohoku gölgelerinde artışın bilindiğini biliyor (TR-6a §3.4, R3 gerekçesi).
  Kural 4 bu bilinen A = 1'i sayımdan siler. Önerilen metin:
  > "Kenar kümeleri gölge artış oyunu kullanan sayımlardan (Y, ters yön notu, S2 artış yönü) hem paydan hem paydadan
  > çıkar; ters yön eşiği c⁺(K − m; p₀⁺) ile hesaplanır. Özgün A bilgi olarak yazılır."
- Kontrol satırları (H1'i düşürenler):
  - Kenar etkisi pozitif lobda artış oyunu şişirir: S1 kolay tutar.
  - Nötr bölgede ve S2'de düşüş oyunu bastırır: S7 ve S2 düşüş uyarısı zor tetiklenir.
  - Üçü de H1'i düşüren denetimlerdir; kenar etkisi hepsini H1 lehine zayıflatır.
  - Önerilen metin:
    > "S1'de pozitif lobunun, S7'de nötr bölgesinin, S2'de gölge lobunun kapı N0'ı 500'ü aşan küme o satırdan çıkar;
    > K⁺, K_nt ve K_nk onsuz sayılır."
- Körlük beyanına şu cümle eklenmeli:
  > "Kenar kuralının Tohoku'ya etkisi (D değişmez, A sayılmaz, sahte oyu yoktur) yazar Tohoku'nun bilinen sonucunu
  > bilirken seçildi; R3 bu yüzden reddedildi."

**Z6. Etki büyüklüğü bölümü eklenmeli** (§7'deki metin, "§C11"). Taslakta p₁ = 0,75'in kaynağı, görülebilir en küçük
etki, ×0,5 ve ×2 duyarlılığı ve olumsuz sonucun anlamı yoktur. p₁ yalnız §C7'de geçer ve orada da "tasarım dünyası"
diye geçer.

**Z7. §C9'a yeni zayıflık eklenmeli.** Kenar kümeleri H0 hükmünün yanlış oranını büyütür:
> "p₁ = 0,75 dünyasında (f 0,549) yanlış H0 (X ≤ h) oranı K 23'te kenarsız 0,043'tür. Önsayımın iki kenar kümesiyle
> 0,045, beş Tohoku benzeri kümeyle 0,059'dur. 'H0 (büyük etki yok)' hükmü kenar kümesi sayısıyla birlikte okunur."

**Z8. Güncel olmayan cümleler düzeltilmeli.**
- §C6'nın "`kod_sha256` alanı bugünkü kodla aynıdır" cümlesi artık doğru değil. Bu incelemede `tr6a_kosu.py`
  değişti (yalnız çıktı adları, §5.3). `tr6a_yapay.py` değişmedi ve prova parçaları bayt bayt yeniden üretildi.
- §C10'daki "62 sınama" artık 66'dır.

## 3. Soru 1: TR-6c kusuru gideriyor mu?

### 3.1 Ölçüt değişikliği (D1) uydurma mı?

D1'in kendisi uydurma değildir:
- Ana hüküm P(D)'yi kesin Poisson değeriyle değil, p₀ ile karşılaştırır.
- TR-6a'nın (ii) ölçütü zaten bu biçimdeydi.
- Bu seçenek tanıda (`TR-6a_SINAMA-TANI.md` §7) bağlayıcı sonuçtan önce de vardı.
- Bağlayıcı tohum değişti ve dondurmadan önce tam ölçekte prova yapıldı.

Ama iki yönden başarısız hücreye göre biçimlenmiştir:
- **Kenar hücreleri** (N0 > 500) yalnız tek yanlı C1′ alır ve C1′ neredeyse hiçbir şeyi sınamaz (Z3). Kenar etkisini
  "tutucu" diye kabul etmek α için doğrudur (§3.4). Ama ölçüt, H1 yönündeki 0,06–0,17'ye kadar bir kod hatasını
  göremez.
- **i:500 hücresi** (TR-6a'nın tutmayan hücresi) artık C1'le geçiyor, çünkü p̂₀ kenar etkisini taşıyor. Hat koşulsuz
  P(D) − kesin değeri benim yeniden koşumda −0,0166 (z −4,7) çıktı. Bu, TR-6a ölçütüyle yine tutmazdı. TR-6c bunu
  bilerek kabul ediyor. Kabul açıkça yazılmış; bunda sorun görmüyorum.

### 3.2 C1 kalibrasyonu sınıyor mu?

- **N0 ≥ 100'de evet.** Kapı payı 1'dir, iki havuz aynıdır. Benim yeniden koşularım (tohum 8801, hücre başına 20 000
  deneme, yazarın işlevleriyle):

  | Hücre | p̂₀ − P(D \| kapı) | z | D4 P(D \| kapı) − kesin (z) | hat P(D \| kapı) − kesin (z) |
  |---|---|---|---|---|
  | i:100 | +0,0039 | +0,96 | −0,0037 (−1,05) | −0,0069 (−1,97) |
  | ii:100 | −0,0081 | −1,99 | +0,0354 (+10,0) | +0,0051 (+1,43) |
  | i:500 | +0,0022 | +0,53 | +0,0003 (+0,09) | −0,0166 (−4,68) |

- **N0 31,36'da hayır** (§1, Z1–Z2):

  | Hücre (tohum, n) | kapı payı | p̂₀ bütün denemeler − P(D \| kapı) | p̂₀ kapıyı geçenler − P(D \| kapı) | p̂₀ kapıyı geçmeyenler |
  |---|---|---|---|---|
  | i:31,36 (8801, 20 000) | 0,477 | +0,0050 (z +0,85) | **−0,0510 (z −8,27)** | – |
  | i:31,36 (8802, 12 000) | 0,465 | +0,0106 (z +1,38) | **−0,0443 (z −5,50)** | 0,659 |
  | ii:31,36 (8802, 12 000) | 0,518 | −0,0004 (z −0,06) | **−0,0547 (z −7,22)** | 0,675 |
  | i:36 (8802, 12 000) | 0,951 | +0,0033 | −0,0034 (z −0,62) | 0,647 |
  | i:40 (8802, 12 000) | 0,999 | +0,0054 | +0,0053 (z +1,01) | – |

  Kapı sınırındaki gerçek H0 düşüş oyu olasılığı 0,531–0,538'dir; 0,50 tabanının üstündedir. Gerçek koşunun havuzu
  bunu 0,48–0,49'a çeker.

### 3.3 C1′ ne kadar zayıf?

Prova verisiyle C1′'nün geçirdiği en büyük yukarı kayma:
- N0 1500'de: 0,4920 + 3,5 · 0,0035 − 0,4283 = **+0,076**;
- N0 4500'de: **+0,186**.

Yani C1′ yalnız kenar etkisinin işaretini ters çeviren kaba bir hatayı yakalar. Z3'teki iki yanlı ölçütler aynı
hücrelerde ≈ 0,012–0,014'lük kaymaları görür. Prova verisiyle tutarlar.

### 3.4 Yanlış "H1" oranı her senaryoda ≤ %5 mi? (`inc_c_alfa.py`, 200 000 tekrar)

Modelin kurgusu:
- Küme düzeyinde gerçek ve sahte oylar kullanılır.
- Kümeler önsayımın 28 kümesidir (Sumatra (d) ile çıkar); J'ler önsayımdaki `sahte_gecerli` değerleridir.
- p₀, testere dişi ve "en zayıf" sırası kodun işlevleriyle (`KO.p0_kestir`, `KO.testere`) hesaplanır.
- H0 oy olasılıkları prova hat değerlerinden alınır ve log N0'da ara değerlenir.

| Senaryo | K | J | yanlış H1 | "güç yok (ölçü yanlı)" |
|---|---|---|---|---|
| (i) Poisson hat, sahte = gerçek | 28 | 61 | 0,011 | 0,014 |
| aynı, TR-6a havuzu (kenar sahteleri dahil) | 28 | 64 | 0,011 | 0,010 |
| (ii) Poisson hat | 28 | 61 | 0,012 | 0,014 |
| aşırı saçılım φ 5 (0,5151; TR-6a §4.3 en kötü hücre) | 28 | 61 | 0,029 | 0,095 |
| φ 5 + gerçek pencere sahteden 0,02 "düşüşçü" | 28 | 61 | 0,043 | 0,096 |
| kenar kümeleri 0,50, öteki 0,5151 | 28 | 61 | 0,034 | 0,096 |
| K 23, (i) / (ii) / φ 5 / φ 5 + 0,02 | 23 | 47 | 0,013 / 0,013 / 0,026 / 0,038 | 0,021 / 0,023 / 0,105 / 0,105 |
| J yarıya (J < 30 dalı), φ 5 | 28 | 20 | 0,013 | 0,163 |
| kapı sınırında 4 küme (gerçek 0,538, sahte 0,487; §3.2) | 28 | 61 | 0,016 | 0,019 |
| kapı sınırında 10 / 16 küme | 28 | 61 | 0,024 / 0,034 | 0,026 / 0,031 |
| K 23, kapı sınırında 10 / 16 küme | 23 | 48–51 | 0,027 / 0,039 | 0,054 / 0,050 |
| kenar dışı 26 kümenin hepsi kapı sınırında | 28 | 61 | **0,057** | 0,041 |

Kalibrasyonun soğurmadığı bir uyuşmazlık δ olsun (gerçek pencere sahteden δ kadar "düşüşçü"; örneğin Risk 6 ya da
kapı seçimi). Bu durumda α:
- sahte 0,50 iken δ 0,03'te 0,043, δ 0,04'te 0,054;
- sahte 0,5151 iken δ 0,03'te 0,051.

Okuma:
- **Modellenen her H0 dünyasında α ≤ 0,05'tir. Tek istisna, bütün kümelerin kapı sınırında olduğu dünyadır (0,057).**
- α'yı koruyan şey kalibrasyon değil, 0,50 tabanıdır. Kalibrasyonun işi aşırı saçılımda p₀'ı yükseltmektir.
- Kenar sahtelerinin havuzdan çıkması α'yı değiştirmiyor (0,011 / 0,011).
- Gerçek veride gerçek pencereye özgü ve sahte pencerelerde olmayan bir yanlılık ≈ 0,03'ü aşarsa α 0,05'i aşar.
  Risk 6 (ana şok artçıları, §C9 madde 4) bu türdendir ve sınanmamıştır.

### 3.5 R1′ hükmü tek yönlü yanlılaştırır mı?

Evet, H0 yönüne. Yön α için güvenlidir, ama dört yerde bedeli vardır:
1. **Düşüş oyu (D).** H0'da aşağı kayar. Yanlış H1 azalır, güç düşer. §C7'nin tablosu doğrudur: önsayım için 0,804 →
   ≈ 0,79.
2. **Yanlış H0 hükmü (p₁ 0,75 dünyası, `inc_c_alfa.py` `yanlis_H0`):**
   - K 23: kenarsız 0,043; önsayımdaki iki kenar kümesiyle (N0 584 → w 0,470; N0 4500 → w 0,321) 0,045; beş Tohoku
     benzeri kümeyle 0,059;
   - K 28: sırasıyla 0,031 / 0,033 / 0,042.
   - Bu bir H0 lehine yanlılıktır ve Z7 olarak yazılmalıdır.
3. **Ters yön notu.** A = 0 kuralıyla yalnız zorlaşır (Z5).
4. **H1 düşürücü kontroller (S1, S2 düşüş, S7).** Kenar etkisiyle zayıflar: H1 lehine (Z5). Ana sınamanın α'sını
   bozmaz, çünkü düşürücüler H1 yaratamaz. Ama artefakt koruması zayıflar.

## 4. Yazarın işaretlediği yedi nokta

1. **i:100 (z +2,14).**
   - Benim bağımsız koşum (tohum 8801, 20 000): +0,0039 (z +0,96). İkisinin birleşimi ≈ +0,006 (z ≈ 2,2) çıkar.
   - Yön tutucudur: sahteler biraz daha "düşüşçü", p₀ yukarı.
   - Altı C1 hücresi arasında en büyük |z|'nin ≥ 2,14 çıkma olasılığı ≈ 0,18'dir; olağandışı değildir.
   - ii:100'de benim koşum −0,0081 (z −1,99) verdi, yani ters yön. Sistematik bir işaret görmüyorum.
   - Gerçek kayma +0,006 olsa bile, bağlayıcı koşuda bu hücrenin |z| > 3,5 çıkma olasılığı ≈ %3'tür.
2. **500 sınırı (ii)'de kıyıda.** Hat − kesin −0,020 ± 0,0035; i:500'de benim koşum −0,0166. Sınırın ölçüsü tutarsız
   yazılmış (Z4). Ayrıca i:500 hücresinin kendisi sınırın üstünde durur: denemelerin kapı N0'ı 500 civarında
   dalgalanır, gerçek koşuda yaklaşık yarısı kenar sayılırdı. Bu hücre "kenar dışı" sınaması için temsilî değildir
   (bilgi olarak yazılmalı).
3. **(ii)'de hat − ham farkının yorumu.** Doğrudur. ii:100'de D4 P(D | kapı) − kesin = +0,035 (z +10). Hat ise kesine
   yakındır (+0,005). Fark kenar etkisinden değil, D4'ün kümelenmeyle yukarı kaymasından gelir. Bu yüzden (ii)'de
   kenar etkisinin ölçüsü hat − kesin olmalıdır. Ama o zaman "Neden 500" (ii)'de bu ölçüyle yazılmalıdır (Z4).
4. **C1′'nün zayıflığı.** §3.3: +0,076 / +0,186'ya kadar yukarı kayma geçer. Düzeltme Z3.
5. **Kenar kuralının koddaki yeri.**
   - Manifest sırası: kenar sahte oylardan sonra hesaplanıyor, p₀'dan önce süzülüyor. K_kapı < 23'te de kenar
     listesi yazılıyor; zararsız.
   - `_kenar_A`: yalnız `GOLGE_LOBLARI` (golge, D3a, D3b, D5, D8) ve temsilciye göre çalışıyor. D1, D4, D6, S5a, S5b,
     B1 ve B4 `lob="golge"` ile geçiyor; S3, S4 ve D7 ana satırdan türüyor.
   - S2: `_nk_kumeleri` içinde uygulanıyor. `tamlik_eleme` yeniden kurarken `_kenar` önceden atanmış oluyor.
   - Metinle uyumlu. Ancak yazarın sınaması yalnız D4, D1, S3 ve S4'e bakıyordu. M3, M4 ve M5 mutantları bu yüzden
     yakalanmıyordu (§5.2); düzelttim.
   - Kenar birimi ana gölge kapı N0'ından belirleniyor. S1 ve S7 lobları için ayrı kenar tanımı yok (Z5).
6. **Güç modeli varsayımı.** §C7 şunları varsayar: kenar etkisi yalnız yanlış loblu kümelerde w'yi (i)'nin hat − ham
   farkı kadar düşürür; f 0,549 sabittir; w H0 düzeyindedir. Bu bir modeldir, ölçüm değildir. Benim hesabım (§3.5)
   aynı varsayımla 0,7977 → 0,7899 (iki kenar kümesi) verdi; §C7 ile tutarlı. w'nin 0,2–0,4 olduğu dünyada (gölgede
   gerçek artış, TR-6a §4.5) temel güç zaten 0,80'in altındadır; §C7 bunu söylemeli.
7. **Tarih.**
   - Taslak tarihi (16 Kasım 2026) commit tarihiyle uyumlu. ZINCIR Halka 10'un 12 Kasım tarihli "TR-6c açıldı"
     kaydıyla çelişki yok.
   - TR-6c manifesti olay öncesi veriyi TR-6a önsayımından aylar sonra yeniden indirecek. Kataloglar o arada
     güncellenmiş olabilir. Bu, kapı N0'larını ve kenar üyeliğini değiştirebilir.
   - Kural yalnız manifestteki sayıya dayandığı için körlüğü bozmaz. Ama §C4'ün "Tokachi-oki ve Tohoku" cümlesi
     önsayıma dayanan bir beklentidir; manifest farklı çıkarabilir. Metin bunu söylemeli.
   - 2025-12-31 sınırı ve 2025-12-05 en geç sorgu bitişi değişmeden geçerli.

## 5. Soru 3: kod metne uyuyor mu?

### 5.1 Uyum

Kod metne uyuyor:
- `--tasarim c` yolları ve TASLAK durdurması çalışıyor.
- Tohum yasakları çalışıyor.
- Parça tohumu `(tohum, hücre kodu, parça)` biçiminde.
- C1, C1′, C2 ve C3 aritmetiği metindeki gibi.
- C2 ve C3 beklenen değerleri metindeki sayılarla birebir: N0_kul 19,787; 0,94019; m* −10,333; 0,49688.
- Kenar kuralının satır listesi ve S2'deki uygulaması metne uyuyor.

Prova parçalarını bugünkü kodla yeniden ürettim (`inc_c_parca_sha.py`, tohum 7311): i:100 p0 ve p19, ii:100 p0,
adım:31,36 p0, i:31,36 p0, i:500 p7. Altısının sha256'sı da `tr6c_prova_*.json` `parca_sha256` ile **aynı**. Yazarın
kesinti ve yeniden üretim beyanı doğrulandı.

Metinle kod arasında tek tasarım farkı yok. Z1 metinle birlikte değişmelidir; kodu ben değiştirmedim, çünkü metin
böyle diyor.

### 5.2 Mutasyon sınaması (`inc_c_mutasyon.py`, yazarın `TTasarimC` sınıfı)

Önce, yazarın sınamalarıyla 18 mutantın 5'i yakalandı: M1, M2, M6, M11, M12. Benim eklemelerimden sonra 18'in 18'i
yakalanıyor (`inc_c_mutasyon_once.json`, `inc_c_mutasyon_sonra.json`).

| Mutant | Önce | Sonra |
|---|---|---|
| M1 kenar sınırı 500 → 5000 | yakalandı (yalnız hücre ölçütü yoluyla) | yakalandı |
| M2 `>` → `≥ 2 ×` | yakalandı | yakalandı |
| M3 A = 0 satır listesi yalnız ana gölge (D3a/D3b/D5/D8 dışarıda) | **kaçtı** | yakalandı |
| M4 S2'de kenar A sıfırlanmaz | **kaçtı** | yakalandı |
| M5 kenar kuralı D'yi de sıfırlar | **kaçtı** | yakalandı |
| M6 kenar sahteleri p̂₀'a girer | yakalandı | yakalandı |
| M7 manifest çekirdeğinde kenar listesi yok | **kaçtı** | yakalandı |
| M8 C1 eşiği 3,5 → 2,0 | **kaçtı** | yakalandı |
| M9 C1′ tek yanlı → iki yanlı | **kaçtı** | yakalandı |
| M10 C1′ hiç tutmamaz | **kaçtı** | yakalandı |
| M11 kenar hücre sınırı 500 → 1500 | yakalandı | yakalandı |
| M12 bağlayıcı katalog tohumu TR-6a'nınki | yakalandı | yakalandı |
| M13 parça tohumu hücre kodunu içermez | **kaçtı** | yakalandı |
| M14 hücre kodu sırası değişir | **kaçtı** | yakalandı |
| M15 parça boyu 1000 → 500 | **kaçtı** | yakalandı |
| M16 yapay Mc farkı 0,2 → 0 | **kaçtı** | yakalandı |
| M17 SE₀ paydasında ort(J) yok | **kaçtı** | yakalandı |
| M18 bağlayıcı deneme 20 000 → 2000 | **kaçtı** | yakalandı |

Kaçan mutantların hiçbiri prova sayılarını değiştirmiyordu; yani bir kod hatası değil, sınama boşluğuydu. M8, M9,
M10 ve M17 bağlayıcı sınamanın geçti/tutmadı kararını doğrudan değiştirir. M13 ve M14 bağlayıcı baytları değiştirir.

### 5.3 Yaptığım kod düzeltmeleri (önemli; hesap değişmedi)

1. **Çıktı adı.** TR-6c kipinde üç çıktı "TR-6a" diyordu:
   - `tr6c_sonuc.md` başlığı "# TR-6a sonuç" idi;
   - "koşulmadı" hüküm cümlesi "TR-6a koşulmadı: …" idi;
   - işaret dosyası "TR-6a olay sonrası oylar sayıldı" idi.

   Kapanmış bir sınavın adıyla bağlayıcı çıktı yazılmış olurdu. Bu §C0 ve §C8'e aykırıdır. `tr6a_kosu.py`'ye `AD`
   eklendi ("TR-6a"; `tasarim_sec("c")` "TR-6c" yapar). TR-6a kipinde çıktılar bayt bayt aynıdır
   (`test_tr6a_bit_duzeyi` geçiyor).
2. **Sonuç dosyasında kenar bilgisi.** §C4 "Sonuç dosyası kenar kümelerini, özgün A'larını … yazar" diyor. JSON bunu
   `oylar` ve `m_etkin` içinde taşıyordu, `tr6c_sonuc.md` ise taşımıyordu. TR-6c kipinde md'ye bir "Kenar kümeleri"
   satırı eklendi.
3. **Sınamalar** (`tr6a_test_yapay.py`, `TTasarimC`; 4 yeni sınama, kenar sınamasında genişletme):
   - kenar kuralı bütün gölge türevi satırlarda ve S2'de; D ve özgün A sayımlardan yeniden türetilir; manifest
     çekirdeği; md;
   - sınır ve satır listesi sabitleri; `_kenar_A` birim sınaması;
   - C1, C1′ geçti/tutmadı eşikleri ve SE biçimi;
   - parça şeması, hücre kodları, sabitler ve C2/C3 beklenen değerleri;
   - çıktı adı.

Sınamalar: `python3 -I -B kayit/turetme/tr6/tr6a_test_yapay.py` → **66 sınama, hepsi geçti** (≈ 2 dk; önce 62).

`tr6a_yapay.py` değişmedi. `tr6a_kosu.py`'nin sha256'sı değişti; prova özetlerinin `kod_sha256` alanı bu yüzden artık
güncel değil (Z8). Bağlayıcı koşu dondurulan koda göre zaten yeniden koşulacak.

Kod önerisi (bağlayıcı değil): `hucre_parcasi_c` bağlayıcı tohumları reddetmiyor. Biri dondurmadan önce bağlayıcı
parçaları üretip bakabilir. `hucre_kos_c(…, baglayici=True)` dışından çağrıda 20261116 ve 20261117'yi reddetmek
ucuz bir korumadır.

## 6. Soru 4: körlük

- **Kapı ve manifest yalnız olay öncesi veriyle mi?** Evet:
  - Kenar birimi, manifestteki ön pencere kapı N0'ından belirleniyor (`kenar_birimleri(N0)`).
  - Kenar listesi manifest çekirdeğine giriyor.
  - Olay sonrası veri yalnız `kos` aşamasında `son_ekle` ile ekleniyor.
  - Ek 1 E1.3 (d)'nin olay sonrası bölge Mc_son'una bakması TR-6a'dan devralınan ve metinde yazılı bir kuraldır.
- **Taslak bilinen sonuca dayanarak kural seçiyor mu?** Kısmen, ve beyan eksik:
  - R3'ün reddi açıkça Tohoku'nun bilinen H1 aleyhine sonucuna dayanır. Yön H1 aleyhine olduğu için kabul edilebilir
    ve beyan edilmiştir.
  - Kural 4 ise aynı yazarın bildiği Tohoku gölge artışını ters yön sayımından siler. Bu H1 lehinedir ve beyan
    edilmemiştir (Z5).
  - 500 sınırı önsayımın 316–584 boşluğuna düşer (Z4).
  - Bu seçimlerin hiçbiri olay sonrası veriye dayanmıyor. Ama "ezbere" görünmemeleri için gerekçeleri metinde
    yazılmalı.
- Olay sonrası veri hiç indirilmedi. Ben de indirmedim.

## 7. Soru 5: etki büyüklüğü. Önerilen §C11 metni (Z6)

> ## C11. Etki büyüklüğü: kaynağı, görülebilir en küçük etki ve olumsuz sonucun anlamı
>
> **Kaynak.** p₁ = 0,75 (kapıdan geçen bir kümenin gölge lobunda düşüş oyu olasılığı) **bizim tahminimizdir**,
> literatürden alınmış değildir. Literatürde doğrulanmış küresel bir değer yoktur. Bildirilen bulgular gölgelerde
> artışı da içerir (Mallman & Zoback 2007; Hardebeck & Harris 2025). Fiziksel karşılığı TR-6a §4.5'teki dünyadır:
> kümelerin f ≈ 0,55'inde lob doğru yerde ve kalıcı −10 kPa (P_D 0,987), kalanında H0 düzeyi (w ≈ 0,46). Hainzl vd.'nin
> CV ≈ 1 bulgusu yüzünden bu iyimser bir dünyadır.
>
> **Görülebilir en küçük etki** (tek yanlı kesin binom, α 0,05, güç 0,80):
>
> | K | 23 | 25 | 28 | 30 | 35 | 40 |
> |---|---|---|---|---|---|---|
> | en küçük p₁, p₀ 0,50 | 0,749 | 0,770 | 0,730 | 0,718 | 0,707 | 0,698 |
> | en küçük p₁, p₀ 0,52 | 0,788 | 0,770 | 0,763 | 0,749 | 0,734 | 0,722 |
>
> f cinsinden (w 0,457, P_D 0,987): p₀ 0,50'de K 23 için f ≥ 0,55, K 28 için f ≥ 0,51.
>
> **Duyarlılık.**
> - Etki (p₁ − 0,50) yarıya inerse (p₁ 0,625; f ≈ 0,27): güç 0,80 için K ≈ 102 gerekir (kalıcı olarak 111).
>   Önsayımda K_kaba 28'dir; bu etki bu sınavla görülemez.
> - Etki iki katına çıkarsa (p₁ → 1,0; bütün loblar doğru ve P_D ≈ 1): K ≈ 5–8 yeter, K ≥ 23 kapısı zaten geçilir.
> - Ara değerler: p₁ 0,70 → K 37 (kalıcı 42); 0,80 → 18; 0,875 → 11.
>
> **Olumsuz sonuç ne söyler.**
> - "H0", K 23'te yalnız p₁ ≥ 0,75'i dışlar (K 28'de ≥ 0,73'ü). 0,55–0,70 arasındaki küçük ve orta etkileri dışlamaz.
> - Kenar kümeleri bu dışlamayı biraz zayıflatır (§C9: yanlış H0 0,043 → 0,045).
> - "Ayırt edilemez", etkinin yokluğu hakkında bilgi taşımaz.
> - "Güç yok" (K_kapı < 23; yazar önseli ≈ 0,75) bir eleme değildir. Bu veriyle yalnız büyük bir etkinin
>   sınanabileceğini söyler ve sınamayı yapmaz.
> - Bu sayılar `kayit/turetme/ESIK-DAYANAGI.md` tablosundaki TR-6a satırıyla aynıdır (0,70 → 37, 0,80 → 18).

## 8. Dosyalar ve yeniden üretim (deponun kökünde)

- `python3 -I -B kayit/turetme/tr6/inc_c/inc_c_alfa.py 200000 > kayit/turetme/tr6/inc_c/inc_c_alfa.json`:
  yanlış H1 ve H0 oranı, uyuşmazlık tablosu, MDE (≈ 3 s).
- `python3 -I -B kayit/turetme/tr6/inc_c/inc_c_hucre.py <hücre> 20000 <çıktı>`: i:31,36, i:100, ii:100 ve i:500
  hücrelerinin tohum 8801 ile yeniden koşusu. Kapı koşullu havuz ve D4 ölçütü ekleriyle → `inc_c_hucre_*.json`
  (hücre başına 3–40 dk).
- `python3 -I -B kayit/turetme/tr6/inc_c/inc_c_kapi.py <i|ii> <N0> 12000 8802 <çıktı>`: kapı seçimi ve sahte havuz
  → `inc_c_kapi_*.json` (N0 31,36; 36; 40).
- `python3 -I -B kayit/turetme/tr6/inc_c/inc_c_parca_sha.py <geçici_dizin> i:100:0 i:100:19 ii:100:0 adim:31.36:0
  i:31.36:0 i:500:7` → `inc_c_parca_sha.jsonl`.
- `python3 -I -B kayit/turetme/tr6/inc_c/inc_c_mutasyon.py <geçici_dizin> <çıktı> TTasarimC` →
  `inc_c_mutasyon_once.json` (eklemelerden önce) ve `inc_c_mutasyon_sonra.json`.
- `python3 -I -B kayit/turetme/tr6/tr6a_test_yapay.py` → 66 sınama.
