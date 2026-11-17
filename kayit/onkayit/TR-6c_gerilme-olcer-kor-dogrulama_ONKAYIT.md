# TR-6c ön kaydı: hız-durum gerilme ölçeri bilinen kosismik Coulomb gölgelerini kör olarak doğru işaretle buluyor mu? (TR-6a'nın ardılı)

Tarih: 16 Kasım 2026. Durum: **TASLAK sürüm 2, ikinci bağımsız incelemeye hazır.** Dondurulmadı; kodda
`TR6C_ONKAYIT_SHA = None` olduğu sürece bağlayıcı aşamalar (`--tasarim c sinama --baglayici`, `manifest`, `kos`)
koşmaz.

Sürüm 1 (`TR-6c_gerilme-olcer-kor-dogrulama_ONKAYIT_surum1.md`) bağımsız incelemede RET aldı (`TR-6c_INCELEME-1.md`).
Sürüm 2 incelemenin sekiz zorunlu düzeltmesini işler:

| İnceleme | Ne değişti | Yer |
|---|---|---|
| Z1 | C1'in havuzu gerçek koşununki. Gerçek koşunun havuzu artık kapıdan önce kurulur (Z2), C1 de bütün denemelerden havuzlar | §C3, §C3a |
| Z2 | Kapı seçim yanlılığı: yol (a2) seçildi; (a1) ve (b) ile karşılaştırma tablosu. TR-6a Ek 1'in "p̂₀ … soğurur" cümlesi TR-6c'de geçersiz | §C2, §C3a |
| Z3 | Kenar hücrelerinde iki yanlı C1′a ve C1′b eklendi; C1′ yön ölçütü olarak kaldı | §C3 |
| Z4 | "Neden 500" yeniden yazıldı; 316–584 boşluğu beyan edildi | §C4 |
| Z5 | Kenar A'sı Y'nin payından ve paydasından çıkar; S1 / S7 / S2'de kendi lobu > 500 olan küme o satırdan çıkar; körlük cümlesi | §C4, körlük beyanı |
| Z6 | Etki büyüklüğü bölümü | §C11 |
| Z7 | Kenar kümelerinin yanlış H0 oranına etkisi | §C9 madde 9 |
| Z8 | Güncel olmayan cümleler (kod sha'sı, sınama sayısı) | §C6, §C10 |

Ayrıca incelemenin kod önerisi uygulandı: `hucre_parcasi_c` bağlayıcı ve tanı tohumlarını, bağlayıcı kip dışında ve
ön kayıt dondurulmadan önce reddeder (§C10).

Bu belge bir **fark belgesidir**. Soru, veri, kurallar ve hüküm TR-6a'nınkilerdir. Burada yalnız neyin değiştiği ve
neyin aynen kaldığı yazılır; TR-6a metni kopyalanmaz.

**Neden TR-6c.** TR-6a'nın bağlayıcı yöntem sınamasında yapay katalog ölçütü (i)'nin N0 500 hücresi tutmadı (P(D) 0,4686,
beklenen 0,4898, z −6,0). Bağımsız tanı (`TR-6a_SINAMA-TANI.md`) kod hatası bulmadı. Sapma yöntemin kendisinden,
kümesizleştirmenin kısa son pencerede yarattığı kenar etkisinden geliyordu. TR-6a metin gereği "koşulmadı (yöntem: yapay
katalog sınaması)" ile kapandı (`ZINCIR.md` Halka 10). Kusur ölçütün tasarımındaydı: ölçüt beklenen değeri
kümesizleştirmesiz kesin Poisson değerinden alıyordu. Ana hüküm ise P(D)'yi bu değerle değil, sahte pencerelerden
kalibre edilen p₀ ile karşılaştırır. TR-6c aynı soruyu, ölçütü düzeltilmiş ve dondurmadan önce tam ölçekte prova edilmiş
bir yöntem sınamasıyla sorar.

**Körlük beyanı (yazar).** Olay sonrası hiçbir katalog sorgusu yapılmadı, 2026 verisi kullanılmadı. Hiçbir lobda oran
ya da ΔCFF hesaplanmadı. Ek 1 önbelleği ve hiçbir ham katalog dosyası açılmadı. Bu belgedeki her yeni sayı yapay veriden
ya da TR-6a'nın dondurulmuş dosyalarından (`tr6a_onkayit_sayilar.json`, `tr6a_sinama_sonuc.json`, tanı çıktısı) gelir.
TR-6a'nın olay sonrası verisi hiç indirilmediği için TR-6c kördür. Yazarın literatür bilgisi TR-6a'daki gibidir
(Kumamoto, Ridgecrest, Tohoku; TR-6a §3.4). **Kenar kuralının Tohoku'ya etkisi (D değişmez, A sayılmaz, sahte oyu
yoktur) yazar Tohoku'nun bilinen sonucunu bilirken seçildi; R3 bu yüzden reddedildi.** Kural 4'ün A'yı saymaması
Tohoku gölgelerinde bilinen artışı ters yön sayımından çıkarır. Bu H1 lehine bir yöndür ve burada beyan edilir (§C4).

Kullanılan tohumlar (hiçbiri bağlayıcı değil): 7311 (sürüm 1 yapay katalog provası), 7312 (tamlık provası), 7321
(sürüm 2 provası), 7331 (Z2 deneme kayıtları), 7332 (Z2 küme düzeyi benzetim), 7400 (H1 bilgi koşusu), 5, 11, 98, 99
(geliştirme). TR-6a'nın bağlayıcı tohumları (20261114, 20261115), tanının tohumları (601–608) ve TR-6c'nin bağlayıcı
tohumları (20261116, 20261117) kullanılmadı. Kod bu tohumları geliştirme ve provada reddeder.

## C0. Bağlayıcı metinler ve sıra

1. **Bu metin.**
2. **TR-6a ön kaydı**: dondurulmuş gövde (`TR-6a_gerilme-olcer-kor-dogrulama_ONKAYIT.md`'nin ilk 126 740 baytı, sha256
   `41ca1e951d330ab72d106be79bb5f700b415d9574dbddff3da0a12ad73fea94e`) ve Ek 1 (E1.1–E1.4 ve "kapı seçim yanlılığı"
   paragrafı; o paragrafın "p̂₀ … soğurur" cümlesi hariç, §C2). Dondurulan liste `tr6a_olay_listesi.json` (sha256
   `0cde4fa1…048f`) ve `tr6a_onkayit_sayilar.json` (sha256 `e39b3252…c4f`) bu metnin de parçasıdır.
3. TR-6a §0'daki sıranın kalanı (İNCELEME-2, İNCELEME-1, `TR-6_SAYIM.md`).

Bu metin yalnız §C1'de sayılan maddeleri değiştirir. Geri kalan her tanım, eşik, tablo, kalıp ve ad TR-6a'daki gibi
geçerlidir. TR-6a kural metinlerindeki "TR-6a" adı "TR-6c" diye, dosya adları §C8'e göre okunur. Metin ile kod
çelişirse metin geçerlidir.

## C1. Değişiklik listesi

| # | Değişen | TR-6a'da | TR-6c'de | Yer |
|---|---|---|---|---|
| D1 | Yapay katalog sınamasının Δτ = 0 ölçütü | koşulsuz P(D), kesin Poisson değerine karşı, 3,5 SE (i); p̂₀ − P(D \| kapı) yalnız (ii)'de | (i) ve (ii)'de p̂₀ − P(D \| kapı), p̂₀ gerçek koşunun havuzuyla (kapıdan önce), iki yanlı 3,5 SE; kenar hücrelerinde C1′a, C1′, C1′b | §C3 |
| D2 | N0 ızgarası | {31,36; 100; 500} | {28,5; 31,36; 36; 100; 500; 1500; 4500} ve karma λ (20–60), iki dünyada | §C3 |
| D3 | Kenar etkisi kuralı | yok | gölge kapı N0'ı > 500 olan küme K'de kalır; sahte oyları kalibrasyona girmez; gölge artış oyu sayılmaz; S1 / S7 / S2'de kendi lobu > 500 olan küme o satırdan çıkar | §C4 |
| D4 | Tamlık kuralı | A2 ve yedek merdiveni (a)–(d), sınamayla seçilir | (d) baştan ana kuraldır; merdiven yok | §C5 |
| D5 | Tohum ve koşu biçimi | 20261114 / 20261115, tek parça | 20261116 / 20261117; hücre başına 20 parça × 1000 deneme, belirlenimci parça tohumu | §C3 |
| D6 | Dondurma öncesi tam ölçekli prova | yoktu | yapıldı (bağlayıcı olmayan tohumlarla, hücre başına 20 000 deneme) | §C6 |
| D7 | Dosya adları | `tr6a_*` | `tr6c_*` (kod `tr6a_*.py` içinde `--tasarim c`) | §C8 |
| D8 | Kalibrasyon havuzu (TR-6a §4.6) | K_kapı kümelerinin sahte oyları | kapıdan önceki bütün aday kümelerin sahte oyları (kenar kümeleri hariç); her sahte kendi sahte kapısıyla | §C3a |

Hüküm adlarının kapalı listesi değişmez; yeni ad yoktur (§C8).

## C2. Aynen devralınanlar

Aşağıdakiler TR-6a sürüm 3 + Ek 1'deki gibidir; sayı ve tablolarıyla:
- §1 soru ve hüküm satırı (tek yanlı kesin binom, α 0,05, p₀ = max(0,50; ⌈100 p̂₀⌉/100), J < 30'da taban 0,52);
- §2 rakip açıklamalar ve önseller;
- §3.1 havuz, birimler, dondurulan liste ve sha256'ları; tarih kuralı (en geç sorgu bitişi 2025-12-05; hiçbir sorgu
  2025-12-31'i aşmaz); katalog kuralı;
- §3.2 olay grupları; §3.3 gerilme kaynağı, Okada, alıcı düzlem (Ek 1 E1.1 ve E1.2 dahil); §3.4 loblar (−10 kPa,
  20 km–2L), bilinen kümelerin çıkarılması (Kumamoto, Ridgecrest çıkar; Tohoku kalır);
- §3.5 olay seçimi, büyüklük kuralları, katalog seçimi, ISC kuralı, MAXC, Mc_lob, Mc_kul (tamlık kuralı §C5'te);
- §3.6 kümesizleştirme: Gardner–Knopoff, yalnız lob içi, pencereler ve 730 g ön tampon **değiştirilmedi** (neden §C4);
- §3.7 kümeleme, temsilci, son pencere kesmesi, T_son < 60 g çıkarması;
- §4.1–§4.5: sayılar, kapı (Aσ = 19 kPa sabit, N0 ≥ 31,36, n_on ≥ 155), koşullu binom oyu, Δτ_est;
- §4.6 sahte zaman kalibrasyonu: üç sahte zaman, pencereleri, geçerlilik, sahte kapı, J < 30, p₀ > 0,60 aynen.
  **Değişen tek şey hangi kümelerin sahte oy verdiğidir** (§C3a);
- §5 kapılar ve işlem sırası (§C3a ve §C4 kurallarının yeri eklenir), testere dişi tablosu, "en zayıf" tanımı;
- §6 eşik tabloları, yorum kuralları, kalıplar, §6.4 kapalı hüküm listesi ve bileşimi;
- §7 ikincil satırlar (D2 satırı yok, §C5), §8 çıktı tablosu;
- §9 adım 3–6 (manifest, körlük okuma kuralları, kod incelemesi, olay sonrası tek indirme, tek koşu), dosya adları §C8;
- §10 beklenti (K_kaba §C5'e göre 28), §11 bilinen zayıflıklar, §12, §13 (Marmara'ya taşıma), §14 yeniden açma şartı;
- Ek 1 E1.4 (a)–(g).

**Devralınmayan cümle.** TR-6a Ek 1'in kapı seçim yanlılığı paragrafındaki "p̂₀ aynı seçimi taşır ve beklenen değerde
yanlılığı soğurur" cümlesi **TR-6c'de geçersizdir**. İNCELEME-1 bunun TR-6a'nın havuzu için yanlış olduğunu gösterdi
(§C3a): sahte son pencereler gerçek ön pencerenin içindedir, gerçek kapı yüksek ön sayımı seçer, bu yüzden kapıyı
geçen kümelerin sahteleri gerçek oydan ≈ 0,05–0,07 daha az "düşüşçü"dür. TR-6c bu cümlenin yerine §C3a'yı koyar.

## C3. Yöntem sınaması (TR-6a §9 adım 2'nin yerine)

Kod yalnız yapay veriyle sınanır (`kayit/turetme/tr6/`, numpy + standart kitaplık, `python3 -I -B`). Üç sınama
sırayla, bir kez koşulur. Komut: `tr6a_kosu.py --tasarim c sinama --baglayici --parca-dizini <dizin>`.

1. **Okada doğrulaması:** TR-6a Ek 1 E1.1 ölçütüyle, aynen. Tutmazsa "koşulmadı (yöntem: Okada sınaması)".
2. **Tamlık sınaması:** yalnız (d) kuralı (§C5), TR-6a §9 adım 2'nin 96 hücrelik ızgarası, Ek 1 E1.3'ün ölçütü
   (veri yok olmayan denemelerde koşullu P(D) − kesin Poisson H0 ≤ 0,02 + 3,5 SE_ek; bütün denemeleri veri yok olan
   hücre geçer). Tohum **20261117**, hücre başına 20 000 deneme. Tutmazsa "koşulmadı (yöntem: tamlık sınaması)";
   yedek basamak yoktur.
3. **Yapay katalog sınaması.** Tohum **20261116**.
   - **Dünya.** TR-6a'daki tek birim: M 7,8 doğrultu atımlı yapay sonlu fay, Mc_halka 1,0, gölge lobu 1408 hücre,
     bölge 4426 hücre, kural (d) (T_son 275 g, π = 275/2071). Her denemede yeni katalog gerçekleşmesiyle bütün hat
     koşulur: yerleştirme, Mc_lob, kapı, Mc_son, kümesizleştirme, oy, üç sahte zaman (sahte kapı ve sahte Mc_son
     dahil).
     - (i) lobda saf Poisson, bölgede GK tipi ikincil diziler;
     - (ii) lobda da ikincil diziler;
     - "adım": (i) dünyası, lobda kalıcı −10 kPa Dieterich adımı.
   - **Hücreler** (17; `HUCRELER_C` sırası, hücre kodu 1'den):
     - (i) ve (ii) dünyalarında Δτ = 0 ve N0 ∈ {31,36; 100; 500; 1500; 4500} (kod 1–10);
     - adım dünyasında N0 31,36 (kod 11);
     - (i) ve (ii)'de kapı çevresi N0 28,5 ve 36 (kod 12–15). 28,5'te denemelerin ≈ %11'i kapıyı geçer, 36'da ≈ %95'i;
     - (i) ve (ii)'de **karma** hücre (kod 16–17): her denemede gerçek oran λ, [20, 60] aralığında log-düzgün çekilir.
       Gerçek koşunun havuzu farklı oranlı kümelerin karışımıdır; bu hücre §C3a'nın karışımda da tuttuğunu sınar.

     N0, lobun Mc_lob üstü yıllık oranıdır. Yapay dünyada (d)'nin Mc_son eki yüzünden Mc_kul = Mc_lob + 0,2 olur; oyun
     gördüğü oran N0_kul = N0 · 10^−0,2'dir. Kesin değerler N0_kul ve 275 g ile hesaplanır.
   - **Deneme sayısı:** hücre başına 20 000; 1000 denemelik 20 parça. Parça p'nin tohumu `(20261116, hücre kodu, p)`'dir.
     Parça dosyaları diske yazılır. Koşu kesilirse aynı komut kalan parçaları koşar. Parçalar belirlenimcidir: aynı
     parça aynı baytları verir. Parça dosyalarının sha256'ları çıktıya yazılır. Çıktı `tr6c_sinama_sonuc.json` bir kez
     ("x" kipinde) yazılır. Ara parçalara bakılarak hiçbir kural, tohum ya da ölçüt değiştirilmez.
   - **Tanımlar** (bir hücrede, n deneme):
     - Gerçek oy yalnız gerçek kapıyı geçen (n_on ≥ 155, Mc_lob) ve gerçek Mc_son'u kestirilebilen denemelerden
       sayılır: P(D | kapı) bu denemelerdeki düşüş oyu payıdır.
     - **p̂₀ = ΣS_i / ΣJ_i, toplam bütün n deneme üzerindendir** (gerçek kapıyı geçmeyen ve gerçek Mc_son'u
       kestirilemeyen denemeler dahil). J_i, i. denemenin geçerli sahte zaman sayısıdır (sahte kapı ve sahte Mc_son
       dahil; tek birimde havuz geçersizliği yoktur). S_i geçerli sahte düşüş oyu sayısıdır. Bu, gerçek koşunun
       havuzudur: gerçek koşuda sahte oylar kapıdan önceki bütün aday kümelerden gelir (§C3a). Bir hücre, aynı
       oranlı aday kümelerin bir evrenidir.
     - SE(p̂₀ − P(D | kapı)) = √(SE₀² + SE_D²); SE₀ = sd(S_i − p̂₀ J_i) / (ort(J) √n), SE_D = sd(D) / √n_kapı (TR-6a
       (ii) ile aynı biçim).
   - **Ölçütler:**
     - **C1 (N0 ≤ 500 ve karma; (i) ve (ii)):** p̂₀ − P(D | kapı), 0'a karşı iki yanlı 3,5 SE içinde.
     - **C1′a (N0 > 500; (i) ve (ii)):** C1'in kendisi (iki yanlı).
     - **C1′ (N0 > 500; (i) ve (ii)):** P(D | kapı) ≤ kesin Poisson P(D | H0) (N0_kul, 275 g) + 3,5 SE,
       SE = √(q(1 − q)/n_kapı), q kesin değer. Tek yanlıdır; yön ölçütüdür.
     - **C1′b (N0 > 500; yalnız (i)):** kümesizleştirmesiz (D4 biçimi) P(D | kapı), kesin Poisson P(D | H0) ile iki
       yanlı 3,5 SE içinde (SE = sd(D4) / √n_kapı). (ii)'ye uygulanmaz: orada D4 oyu lob içi kümelenmeyle +0,03–0,04
       yukarı kayar (§C4 R2).
     - **C2 (adım, N0 31,36):** P(D) kesin değerle iki yanlı 3,5 SE içinde (N0_kul 19,79, 275 g: 0,94019).
     - **C3 (adım, N0 31,36):** Δτ_est'in kesin dağılımının medyanı m* (n_on ≥ 1; n_son = 0'da −∞) hesaplanır;
       Δτ_est < m* olan deneme payı kesin P(Δτ_est < m*) ile iki yanlı 3,5 SE içinde (m* = −10,333, olasılık
       0,49688).
   - **Sonuç kuralı:** TR-6a'daki gibi. Bir ölçüt tutmazsa kod hatası aranır; bulunan hata düzeltilir, hata listesi
     commit edilir ve bütün sınama aynı tohumla yeniden koşulur. Hata bulunamazsa TR-6c "koşulmadı (yöntem: yapay
     katalog sınaması)" diye kapanır; olay sonrası veri indirilmez, aday elenmez.
   - **Bilgi satırları** (hükmü değiştirmez): kapı koşullu havuzla p̂₀ − P(D | kapı) (sürüm 1 / TR-6a havuzu),
     koşulsuz P(D) ve kesin değer (kenar etkisinin büyüklüğü), eşli "hat − kümesizleştirmesiz" farkları (D ve A),
     p̂₀⁺ − P(A | kapı), kümesizleştirmesiz (D4 biçimi) p̂₀ ve P(D | kapı), kapı payı, veri yok payı.

**Ölçütün gerekçesi (D1).** Ana hüküm P(D)'yi kümesizleştirmesiz kesin Poisson değeriyle değil, aynı işlem zincirinden
geçen sahte pencerelerden kalibre edilen p₀ ile karşılaştırır. Sınanması gereken şey zincirin kendi H0 değeridir:
gerçek ve sahte pencereler aynı yapıda mı ve kalibrasyon kenar etkisini ve kapı seçimini soğuruyor mu. Bunun için C1'in
havuzu gerçek koşunun havuzu olmalıdır (İNCELEME-1 Z1). Sürüm 2'de gerçek koşunun havuzu kapıdan önce kurulduğu için
(§C3a), C1 de bütün denemelerden havuzlar. Kesin Poisson değeri bilgi satırı olarak kalır.

**C1′a / C1′ / C1′b'nin gerekçesi.** Kenar birimlerinin sahte oyları kalibrasyona girmez (§C4). Bu birimlerde dayanılan
özellik kenar etkisinin yönüdür: H0'da düşüş oyu olasılığı kesin değerin üstüne çıkmamalıdır (C1′). Ama C1′ tek başına
çok zayıftır: hat N0 1500'de 0,064, 4500'de 0,174 aşağıda olduğu için, +0,076 ve +0,186'ya kadar yukarı kayma yaratan bir
kod hatası bile C1′'yü geçerdi (İNCELEME-1 §3.3). C1′a aynı hattın kendi sahteleriyle tutarlılığını, C1′b
kümesizleştirmesiz oyun kesin değere uyduğunu sınar. İkisi ≈ 0,012–0,014'lük kaymaları görür.

**Süre.** Bağlayıcı yapay katalog sınaması ≈ 19 saat CPU'dur (çoğu N0 4500 hücrelerinde; yeni altı hücre ≈ 0,3 saat).
Tamlık sınaması ≈ 10 dakikadır. Parçalı koşu iki süreçle ve kesintiye dayanıklı yürür.

## C3a. Kalibrasyon havuzu kapıdan önce (yeni; İNCELEME-1 Z2, yol (a2))

**Kural.** Manifestte, TR-6a §4.6'nın sahte oyları **K_kapı kümelerinden değil, kapıdan önceki bütün aday kümelerden**
alınır:
1. Kalibrasyon kümeleri: katalog seçimi olan bütün hazır birimlerin küme seti (§3.7 kümelemesi), §3.4 ve §3.7
   çıkarmalarından sonra, **gerçek kapı uygulanmadan**. Kenar kümeleri (§C4) hariç. Liste manifestte
   (`kalibrasyon_kumeleri`) ve manifest çekirdeğinde yazılır.
2. Her kalibrasyon kümesinin temsilcisi için TR-6a §4.6'nın üç sahte zamanı ve geçerlilik kuralları aynen uygulanır;
   sahte kapı (n_on' ≥ 155) dahil.
3. p̂₀ = ΣD′ / J ve p̂₀⁺ = ΣA′ / J bu havuzdan; p₀ kuralı (taban 0,50, J < 30'da 0,52, p₀ > 0,60) aynen.
4. Kalibrasyon kümesi olup K_kapı'da olmayan kümelerin yalnız olay öncesi sahte oyları sayılır. Bu kümeler için olay
   sonrası veri indirilmez. Ön indirme zaten bütün adaylar için [t0 − 3621 g, t0 − 30 g) aralığını kapsar; yeni indirme
   gerekmez.

**Neden doğru.** Bir kümenin gerçek oyu "gerçek kapı geçti" koşuluyla sayılır. Gerçek kapı ön pencerenin sayımına
bakar ve yüksek sayımı seçer. Bu da gerçek oyu düşüş yönüne iter: kapı sınırında P(D | kapı) ≈ 0,55'tir, koşulsuz
değer ≈ 0,44'tür. Sahte zamanın oyu da kendi sahte kapısıyla sayılır ve yapısı gerçek oyunkiyle aynıdır (ön pencere,
kapı, son pencere). Bu yüzden her oran λ için P(D′ | sahte kapı) = P(D | gerçek kapı) olur. Sorun, sahtelerin yalnız
gerçek kapıyı geçen kümelerden alınmasındaydı. Sahte son pencereler gerçek ön pencerenin içindedir ([t0 − 1035 g,
t0 − 30 g)). Gerçek kapıyı geçmiş bir kümenin sahte son sayımları da yüksektir ve sahte düşüş oyu azalır. Sahteleri
kapıdan önce bütün adaylardan almak bu ikinci koşullamayı kaldırır. Kapı sınırında kapıyı geçemeyen kümelerin
sahteleri (≈ 0,66) geçenlerinkini (≈ 0,48) dengeler. Bir kümenin sahtelerinin geçerli olma olasılığı da gerçek kapıdan
geçme olasılığıyla aynıdır. Böylece havuzun oran bileşimi K_kapı'nınkiyle aynı ağırlıkları taşır.

Yapay kanıt (`tr6c_z2.py kayit`, tohum 7331, λ başına 6000 deneme; (i) dünyası; tam tablo `tr6c_z2_secim.json`
üretiminin girdisidir):

| λ | kapı payı | P(D \| kapı) | p̂₀, yalnız kapıyı geçenler (TR-6a / sürüm 1) | p̂₀, bütün adaylar (a2) |
|---|---|---|---|---|
| 28,5 | 0,106 | 0,662 | 0,516 | 0,639 |
| 30 | 0,268 | 0,581 | 0,515 | 0,598 |
| 31,36 | 0,464 | 0,554 | 0,480 | 0,545 |
| 33 | 0,720 | 0,518 | 0,476 | 0,507 |
| 36 | 0,951 | 0,454 | 0,451 | 0,458 |
| 40 | 0,999 | 0,445 | 0,444 | 0,444 |
| 52 | 1 | 0,457 | 0,460 | 0,460 |

**Yolun seçimi.** Üç yol, aynı deneme kayıtlarından kurulan küme düzeyi bir benzetimle karşılaştırıldı
(`tr6c_z2.py secim`, tohum 7332, senaryo başına 20 000 tekrar):
- **v1 (sürüm 1, karşılaştırma için):** kapı 31,36; havuz yalnız kapıyı geçenlerden.
- **(a1)** kapı N0 alt sınırı 40 (gerçek ve sahte kapı). Önsayımda K_kaba 28'den **24**'e iner (kapı N0'ı 34,3 / 36,8 /
  37,6 / 39,9 olan dört küme çıkar). K ≥ 23 kapısı geçilir. Görülebilir en küçük p₁ K 24'te ≈ 0,76 (§C11).
- **(a2)** kapı 31,36; havuz kapıdan önce bütün adaylardan (bu bölüm).
- **(b)** v1 + İNCELEME-1'in önerdiği taban kuralı: kapıyı geçen kenar dışı kümelerin yarısından fazlasının kapı N0'ı
  < 40 ise p₀ tabanı 0,52.

Benzetimin kurgusu:
- Her senaryo bir küme oranları listesidir. Her kümeye kendi λ'sından rastgele bir deneme kaydı atanır; aynı
  gerçekleşmedeki gerçek ve sahte oy ilişkisi korunur.
- Kapı, p₀ (`KO.p0_kestir`), testere dişi (`KO.testere`), "en zayıf" sırası ve K < 23 → "güç yok" kodun
  işlevleridir.
- Kenar kümeleri (kapı N0 > 500) her zaman geçer; H0 düşüş olasılıkları prova hattından alınır.
- Güç: tasarım H1 dünyası. Kapıyı geçen her kümede f = 0,549 olasılıkla D ~ Bern(0,987), yoksa H0 kaydının D'si.
- Önsayım: 28 kümenin kaba N0'ı gerçek λ sayıldı. Kapı altı adaylar yalnız sayı olarak bilinir: 17,08–31,36 arasında
  6 küme, 17,08 altında 32 birim. Bunlara 17,5–30 ve 6–14 aralıklarında log eşit oranlar verildi (25 küme).

Yanlış "H1" oranı (H0; (i) / (ii)), K ortalaması (en sağdaki sütun v1 / a1 / a2 / b):

| Senaryo | v1 | (a1) | **(a2)** | (b) | K |
|---|---|---|---|---|---|
| önsayım (28 + kapı altı adaylar) | 0,011 / 0,012 | 0,014 / 0,015 | **0,010 / 0,013** | 0,011 / 0,013 | 28,1 / 24,8 / 28,1 / 28,1 |
| önsayım, en büyük 23 küme | 0,013 / 0,016 | 0,012 / 0,016 | **0,013 / 0,014** | 0,014 / 0,016 | 23,3 / 23,0 / 23,3 / 23,3 |
| önsayım + 20 kapı yakını aday (λ 28,5–34,5) | 0,016 / 0,016 | 0,016 / 0,018 | **0,015 / 0,015** | 0,015 / 0,015 | 37,6 / 24,9 / 37,6 / 37,6 |
| 60 aday λ 31,36 + 2 kenar (K ≈ 30) | **0,075** / 0,040 | güç yok (K ≈ 2) | **0,042 / 0,026** | **0,053** / 0,024 | 29,8 / 2,0 / 29,9 / 29,9 |
| 50 aday λ 28,5–36 + 2 kenar | 0,033 / 0,026 | güç yok (K ≈ 3) | **0,025 / 0,022** | 0,021 / 0,016 | 29,7 / 2,5 / 29,8 / 29,7 |
| 60 aday λ 40 + 2 kenar ((a1) kapısının eşi) | 0,005 / 0,008 | 0,049 / **0,058** | **0,004 / 0,007** | 0,004 / 0,006 | 62 / 30,5 / 62 / 62 |
| 60 aday λ 31,36 + aşırı saçılım (gerçek ve sahte +0,03) | **0,097** / **0,059** | güç yok | **0,046 / 0,031** | **0,075** / 0,043 | ≈ 30 |
| 60 aday λ 31,36 + uyuşmazlık (yalnız gerçek +0,02) | **0,104** / **0,058** | güç yok | **0,057** / 0,036 | **0,072** / 0,041 | ≈ 30 |
| önsayım, aşırı saçılım +0,03 | 0,020 / 0,024 | 0,025 / 0,027 | **0,020 / 0,022** | 0,021 / 0,024 | 28 / 25 / 28 / 28 |
| önsayım, uyuşmazlık +0,02 | 0,020 / 0,022 | 0,024 / 0,027 | **0,018 / 0,023** | 0,019 / 0,021 | 28 / 25 / 28 / 28 |
| kapı altı aday yok (yalnız 28 küme) | 0,012 / 0,014 | 0,015 / 0,016 | **0,011 / 0,013** | 0,011 / 0,013 | 27,8 / 24,8 / 27,8 / 27,8 |
| kapı altı adaylar 3 kat | 0,011 / 0,014 | 0,014 / 0,019 | **0,012 / 0,012** | 0,012 / 0,013 | 28,6 / 24,8 / 28,6 / 28,6 |

Güç (tasarım H1 dünyası; (i) / (ii)):

| Senaryo | v1 | (a1) | **(a2)** | (b) |
|---|---|---|---|---|
| önsayım | 0,801 / 0,814 | 0,751 / 0,760 | **0,797 / 0,806** | 0,801 / 0,812 |
| önsayım, en büyük 23 küme | 0,726 / 0,739 | 0,719 / 0,738 | **0,720 / 0,737** | 0,723 / 0,740 |
| önsayım + 20 kapı yakını aday | 0,909 / 0,917 | 0,749 / 0,762 | **0,896 / 0,904** | 0,911 / 0,915 |
| 60 aday λ 31,36 + 2 kenar | 0,859 / 0,873 (α 0,075) | 0 (güç yok) | **0,703 / 0,740** | 0,832 / 0,843 (α 0,053) |

Okuma ve seçim:
- **Hiçbir yol bütün satırlarda ≤ 0,05 değildir.** (a2), kalibre edilmemiş bir uyuşmazlık eklenmeyen bütün
  senaryolarda ≤ 0,05'tir (en kötü 0,046). Tek aşan satır "bütün adaylar kapı sınırında + yalnız gerçek pencerede
  +0,02 uyuşmazlık"tır: 0,057, (i). Bu, kapı yanlılığına kalibrasyonun soğurmadığı ayrı bir yanlılığın eklendiği uç
  bir birleşimdir. İNCELEME-1 §3.4'e göre böyle bir uyuşmazlık ≈ 0,03'ü aşarsa her tasarımda α 0,05'i aşar (§C9 madde 4).
- **(a1) kusuru gidermez, taşır.** Kapı 40'ta, oranı 40 civarındaki kümeler aynı seçimi yaşar: λ 40'ta P(D | kapı 40)
  0,533, kapıyı geçenlerin p̂₀'ı 0,485. "60 aday λ 40" satırında α 0,049 / 0,058'dir. Ayrıca K'yi önsayımda 28'den
  24,8'e indirir ve gücü 0,80'den 0,75'e düşürür.
- **(b) kapıya yakın kümeler azınlıkta iken korumaz.** Kuralın eşiği "yarıdan fazla"dır. Ama yanlılığı yalnız kapıyı
  geçen kümelerin ne kadarının sınırda olduğu değil, sınırdakilerin ne kadar yanlı olduğu belirler. "60 aday λ 31,36"
  satırında 0,053, aşırı saçılımla 0,075'tir.
- **(a2) en az güç kaybettiren güvenli yoldur.** Önsayım dünyasında v1'e göre kaybı 0,004 / 0,008'dir (0,801 → 0,797;
  0,814 → 0,806). "60 aday λ 31,36" satırındaki güç düşüşü (0,86 → 0,70) bir kayıp değildir: v1'in oradaki gücü
  α'nın 0,075'e çıkmasından gelir. (a2) orada p₀'ı gerçek H0 düzeyine (≈ 0,55) çeker; p₀ = 0,50 payı 0,65'ten
  0,22'ye iner.
- **(a2) seçildi.** Seçim yalnız yapay veriye ve olay öncesi önsayıma dayanır.

**Benzetimin sınırları.**
- Kümenin kaba N0'ı gerçek λ sayıldı. Kapı altı adayların oranları bilinmiyor, varsayıldı. Ama "kapı altı aday yok"
  ve "3 kat" satırları sonucu değiştirmiyor.
- J, yapay dünyanın küme başına üç sahtesidir. Havuz olayı geçersizliği yoktur.
- Kapı altı kümelerin gerçek sahte geçerlilik oranı manifestte görülecek; J önsayımdaki 61'in birkaç üstüne çıkabilir.
- Benzetim kayıtları tek birimli yapay dünyadandır. Lob geometrisi ve Mc ayrıntıları kümeden kümeye değişmez.

## C4. Kenar etkisi kuralı (yeni)

**Kural.** Seçilen katalogda gölge lobunun kapı N0'ı (Mc_lob, ön pencere, kümesizleştirilmiş; manifestte yazılı)
**500 olay/yılı aşan** birim "kenar birimi"dir (n_on ≥ 2459). Kenar birimi temsilcisi olan küme "kenar kümesi"dir.
1. Kenar kümesi K_kapı'da kalır. K_kapı, testere dişi ve "en zayıf" sırası değişmez.
2. Kenar kümelerinin sahte oyları J, S ve S⁺'ya girmez (kalibrasyon havuzu §C3a). Sahte oyları manifestte bilgi
   olarak yazılır.
3. Kenar kümesinin düşüş oyu D, TR-6a'daki gibi kümesizleştirilmiş sayımla verilir.
4. **Kenar kümesinin gölge lobu artış oyu sayılmaz.** Ana satırda ve gölge lobunu kullanan bütün satırlarda (B1, S3,
   S4, S5a, S5b, D1, D3a, D3b, D4, D5, D6, D7, D8, B4) A, Y'nin hem payından hem paydasından çıkar. Ters yön eşiği
   c⁺(K − m; p₀⁺) ile hesaplanır (m: satırdaki kenar kümesi sayısı). Özgün A bilgi olarak yazılır. Sürüm 1'de A 0
   sayılıyordu ve paydada kalıyordu; bu, ters yön notunu yalnız zorlaştırıyordu (İNCELEME-1 Z5).
5. Kural, işlem sırasında K_kapı sayıldıktan ve çıkarmalar yapıldıktan sonra, p₀ kalibrasyonundan önce uygulanır
   (TR-6a §5: … → K_kapı < 23 denetimi → **kenar kümeleri** → **kalibrasyon havuzu (§C3a)** → p₀ kalibrasyonu → …).
   Kenar birimleri ve kümeleri manifestte yazılır ve manifest çekirdeğine girer.
6. Satır kapılarında (S5a, D1, …) kenar birimi aynı tanımla, ana gölge kapı N0'ından belirlenir.
7. **Kontrol satırları (yeni).** S1'de pozitif lobunun, S7'de nötr bölgesinin kapı N0'ı 500'ü aşan küme o satırdan
   çıkar; K⁺ ve K_nt onsuz sayılır. S2'de gölge lobunun kapı N0'ı 500'ü aşan küme (kenar kümesi) S2'den çıkar; K_nk
   onsuz sayılır. Gerekçe: kenar etkisi pozitif lobda artış oyunu şişirir (S1 kolay tutar), nötr bölgede ve S2'de
   düşüş oyunu bastırır (S7 ve S2 düşüş uyarısı zor tetiklenir). Üçü de H1'i düşüren denetimlerdir ve kenar etkisi
   hepsini H1 lehine zayıflatır. Tamlık elemesinden (Ek 1 E1.3) sonra K⁺, K_nt ve S2 aynı süzgeçle yeniden kurulur.

Kural hüküm adını değiştirmez. Sonuç dosyası kenar kümelerini, özgün A'larını ve sahte oylarını yazar.

**Neden gerekli.** Kümesizleştirme kısa son pencerede (275 g) uzun ön pencerede (1796 g) olduğundan göreli olarak daha
az olay siler. Bunun iki nedeni vardır: pencere sonundaki olaylar sonraki büyük olaylarla silinemez ("gelecek
kesmesi") ve son pencerenin önündeki tampon kısadır. n_son göreli olarak şişer: H0'da düşüş oyu azalır, artış oyu artar.
Etki N0 ile hızla büyür. Sürüm 1 provasında (i) dünyasında hat − kümesizleştirmesiz D farkı N0 31,36 / 100 / 500 /
1500 / 4500'de −0,001 / −0,002 / −0,017 / −0,066 / −0,171'dir. Hat koşulsuz P(D) − kesin Poisson farkı aynı N0'larda
+0,004 / −0,006 / −0,013 / −0,064 / −0,174'tür.

Tek birimli yapay dünyada sahte pencereler aynı yapıdadır ve p̂₀ etkiyi soğurur (C1, C1′a). Gerçek koşuda ise p̂₀ bütün
kalibrasyon kümelerinin sahte oylarından havuzlanır ve p₀ = max(0,50; …) alt sınırını taşır. Bu yüzden yüksek N0'lı
birkaç kümenin kayması havuzda soğurulmaz.
- Önsayımda kaba N0'ı 500'ü aşan iki temsilci var: 2003 Tokachi-oki (583,7) ve 2011 Tohoku (4501,4). Tohoku'nun hiç
  geçerli sahte zamanı yoktur (TR-6a §4.6).
- Bu bir **beklentidir**. TR-6c manifesti olay öncesi veriyi TR-6a önsayımından aylar sonra yeniden indirecek;
  kataloglar arada güncellenmiş olabilir. Kural yalnız manifestteki sayıya bakar; kenar üyeliği önsayımdan farklı
  çıkabilir.

Kaymanın sonuçları:
- Düşüş oyu yönünde kayma H1 aleyhinedir: α korunur, güç düşer (§C7).
- Artış oyu yönünde kayma ters yön notunu ("gölgede anlamlı artış", TR-6a §6.1) şişirir. Kural 4 kenar A'sını
  sayımdan çıkarır.
- Kenar birimlerinin sahte oyları da aynı kaymayı taşır (düşük D′, yüksek A′). Kural 2 onları kalibrasyondan çıkarır.

**Seçimin yapay veriyle gerekçesi.** Üç seçenek sürüm 1 prova verisiyle karşılaştırıldı (§C6; tohum 7311, hücre başına
20 000 deneme):
- **(R2) Kenar birimi kümesizleştirmesiz (D4) oyla oy verir.** (i) dünyasında D4 oyu yansızdır, ama (ii) dünyasında
  (lobda ikincil diziler) H1 yönüne kayar.
  - (ii)'de kapıyı geçen denemelerde D4 P(D | kapı), N0 100 / 500 / 1500 / 4500 için 0,504 / 0,515 / 0,534 / 0,536'dır.
    Kesin değer 0,468 / 0,486 / 0,492 / 0,495'tir (fark +0,036 / +0,029 / +0,042 / +0,041; SE ≈ 0,0035).
  - (i) dünyasında aynı satır 0,464 / 0,490 / 0,494 / 0,492'dir.
  - Lobdaki kümelenme ayıklanmayınca aşırı saçılım düşüş oyunu artırır (TR-6a §4.3). Gerçek lobların kümelenmesi bu
    yapay dünyanınkinden güçlüdür ve kenar birimlerinin çoğunda kalibrasyon yoktur.
  - **Reddedildi:** α riski.
- **(R3) Kenar birimi "veri yok (kenar etkisi)" olur, K ondan sonra sayılır.** α ve ters yön güvenlidir, ama K'yi
  düşürür.
  - K_kaba 28 ve yazar önseli P(K < 23) ≈ 0,75 iken (§C9) bir ya da iki kümenin kaybı hükmü "güç yok"a çevirebilir
    (§C7: K_kapı 23'te bir küme kaybı gücü 0'a indirir).
  - Ayrıca Tohoku'nun bilinen sonucu H1 aleyhinedir; onu kural gereği bile çıkarmak, yazarın bildiği bir H1 lehine
    seçim olurdu.
  - **Reddedildi.**
- **(R1′) Seçilen: küme kalır, D değişmez, A sayılmaz, sahte oyları kalibrasyona girmez.**
  - D yönündeki kayma tutucudur; C1′ bunu her iki dünyada sınar.
  - H1 dünyasında kenar etkisi oyu etkilemez: kalıcı −10 kPa'da N0 500 / 1500 / 4500'de hat ve kümesizleştirmesiz
    düşüş oyu payı 400 / 300 / 150 denemede 1,000'dır (tohum 7400, bilgi).
  - Güç kaybı yalnız yanlış loblu (H0 düzeyindeki) kenar kümelerinden gelir (§C7).

**Neden 500.** 500, beş noktalı yapay ızgaradan (31,36 / 100 / 500 / 1500 / 4500) seçilmiş bir sayıdır.
- Dayanağı bir tolerans değil, iki şeydir: kaymanın yönü (H0'da düşüş oyu azalır, α korunur) ve p₀ tabanı.
- Ölçü dünyaya göre değişir:
  - (i)'de hat − ham D farkı N0 500'de 0,017, 1500'de 0,066'dır.
  - (ii)'de hat − kesin farkı N0 100'de −0,001, 500'de −0,020 (± 0,0035), 1500'de −0,067'dir.
  - Sürüm 1'in "toleransı (0,02) aşmayan en büyük N0" cümlesi bu yüzden tutarsızdı: (ii)'nin ölçüsüyle sınır 100
    olurdu.
- 500'ün altında kalan kümelerin kayması tutucu yöndedir ve α'yı bozmaz. Bedeli güçtür (§C7: en kötü durumda 0,804 →
  0,778).
- **Önsayımda kapı N0'ları 316,3 ile 583,7 arasında boşluk bırakır. Bu aralıktaki her sınır aynı iki kümeyi
  (Tokachi-oki, Tohoku) kenar yapar. Sınır yazar bunu bilirken seçildi.**
- Sınır kapı N0'ına (Mc_lob) uygulanır. Oy Mc_kul ≥ Mc_lob ile sayıldığından oyun gördüğü oran kapı N0'ından küçük ya
  da ona eşittir. Bu yüzden kural gerekenden fazla birime uygulanabilir, azına uygulanmaz.

## C5. Tamlık kuralı: (d) ana kuraldır

TR-6a'nın bağlayıcı tamlık sınamasında A2 ve yedek (a)–(c) tutmadı (en büyük fark +0,54); Ek 1'in (d) basamağı tuttu
(+0,0025; `tr6a_sinama_sonuc.json`). TR-6c'de (d) baştan ana kuraldır; merdiven yoktur. Kural, TR-6a §9 adım 2 (c) ve
Ek 1 E1.3'teki gibidir:
- son pencere [t_s + 90 g, son pencere sonu); tek olaylı ve kesilmemiş pencerede T_son = 275 g,
  **π = 275/2071 = 0,13279**;
- Mc_son alt pencereleri [90, 180) ve [180, 365), ek +0,4 (Mc_son = MAXC + 0,4);
- bir Mc_son penceresinde hiçbir birleşim 50 olaya ulaşmazsa Mc_son kestirilmez: gerçek son pencerede küme "veri yok
  (tamlık kestirilemedi)" olur ve K_kapı Ek 1 E1.3'teki gibi yeniden sayılır; sahte zamanda o sahte oy geçersizdir; S2'de
  küme S2'den düşer;
- §3.7'nin T_son < 60 g ölçütü 90 g başlangıcıyla uygulanır: önsayımda 2004 Sumatra kümesi T_son 1,6 g ile çıkar,
  **K_kaba 29 → 28** (`tr6a_onkayit_sayilar.json` `onsayim.19.yedek_c`);
- sahte son pencereler [t'_j + (t_s − t0) + 90 g, t'_j + e); S2'nin "son" penceresi [t0 − 305 g + (t_s − t0),
  t0 − 30 g);
- D2 satırı yoktur.

TR-6a §4.3 ve §4.5'in Poisson tabloları 335 g penceresi içindi. (d) penceresiyle (275 g, ΔMc = 0) kesin değerler
(`tr6c_prova_bilgi.json`):

H0 (kümesizleştirmesiz Poisson, 275 g son pencere, 1796 g ön pencere, ΔMc = 0):

| N0 (olay/yıl) | 17,08 | 31,36 | 50 | 111,2 | 300 | 1000 | 4500 |
|---|---|---|---|---|---|---|---|
| P(D \| H0) | 0,4372 | 0,4574 | 0,4658 | 0,4766 | 0,4857 | 0,4922 | 0,4963 |
| P(A \| H0) | 0,4436 | 0,4546 | 0,4645 | 0,4766 | 0,4858 | 0,4922 | 0,4963 |

Kalıcı −10 kPa (Aσ 19 kPa, Dieterich adımı), P(D):

| N0 | ΔMc 0 | ΔMc 0,2 | ΔMc 0,5 |
|---|---|---|---|
| 31,36 | 0,9795 | 0,9402 | 0,8422 |
| 50 | 0,9958 | 0,9798 | 0,9119 |
| 111,2 | 1,0000 | 0,9992 | 0,9853 |

Bunlar kümesizleştirmesiz değerlerdir. Hattın gerçek H0 değeri yüksek N0'da kenar etkisiyle daha düşüktür (§C4, §C6).
Kapı sınırında ise kapı seçimiyle daha yüksektir (§C3a). Ana hükmün karşılaştırması p₀ iledir; bu tablolar bilgi ve
güç hesabı içindir.

## C6. Dondurma öncesi tam ölçekli prova

TR-6a'nın dersi: yöntem sınaması dondurmadan önce tam ölçekte koşulur. §C3'ün bütün yapay katalog hücreleri ve tamlık
sınaması, bağlayıcı olmayan tohumlarla ve bağlayıcı koşuyla aynı kodla, hücre başına 20 000 denemeyle koşuldu.

**Komutlar ve dosyalar.**

| Prova | Tohum | Hücreler | Çıktı |
|---|---|---|---|
| Sürüm 1 provası, yeniden özetlenmiş | 7311 (yapay katalog) | 11 eski hücre | `tr6c_prova_<hücre>.json` |
| Tamlık | 7312 | 96 | `tr6c_prova_tamlik.json` |
| Sürüm 2'nin değişen ve yeni hücreleri | 7321 | 10 hücre (aşağıda) | `tr6c_prova_t7321_<hücre>.json` |
| Tablolar | | | `tr6c_prova_bilgi.json` |

- Parçalar, `hucre_parcasi_c`'yi doğrudan çağıran iki işçi betiğiyle koşuldu. Parça tohumu ve dosya biçimi
  `--tasarim c sinama --prova` komutundakiyle aynıdır. Özetler bütün parçalar bittikten sonra `prova_c` ile bir kez
  yazıldı.
- Sürüm 2, eski hücrelerin parça kodunu ve parça baytlarını değiştirmedi (yeni hücreler sona eklendi; karma dalı
  yalnız karma hücrede çalışır). Bu yüzden tohum 7311'in 220 parçası sürüm 2 ölçütleriyle yeniden özetlendi.
- `kod_sha256` alanları bu özetlerin yazıldığı kodu gösterir (İNCELEME-1 Z8: sürüm 1 özetlerinin sha'sı, İNCELEME-1'in
  `tr6a_kosu.py` değişikliğinden sonra güncel değildi).
- Sürüm 1'in 7311 provasına sürüm 1 makine kesintisi ve yeniden üretim beyanı (bayt bayt aynı) aynen geçerlidir;
  İNCELEME-1 altı parçayı bağımsız olarak yeniden üretti.
- Tohum 7321'de ii:1500'ün 16. parçası iki işçi tarafından iki kez yazıldı. Parçalar belirlenimci olduğu için içerik
  aynıdır.

**Sonuç: tohum 7321'in 10 hücresi, tohum 7311'in 11 hücresi ve tamlık sınaması sürüm 2 ölçütleriyle geçti.**

Sürüm 2'nin değişen ve yeni hücreleri (tohum 7321, hücre başına 20 000 deneme, veri yok payı her hücrede 0):

| Hücre | Ölçüt | Değer | Beklenen | SE | z | Kapı payı | p̂₀ (a2) / P(D \| kapı) | Bilgi: kapı koşullu havuz p̂₀ − P(D \| kapı) (z) |
|---|---|---|---|---|---|---|---|---|
| i:28,5 | C1 | +0,0124 | 0 | 0,0120 | +1,03 | 0,109 | 0,643 / 0,631 | −0,107 (−7,6) |
| ii:28,5 | C1 | +0,0030 | 0 | 0,0108 | +0,27 | 0,133 | 0,637 / 0,634 | −0,101 (−8,1) |
| i:31,36 | C1 | +0,0013 | 0 | 0,0059 | +0,23 | 0,468 | 0,544 / 0,542 | −0,056 (−9,0) |
| ii:31,36 | C1 | +0,0018 | 0 | 0,0057 | +0,31 | 0,514 | 0,535 / 0,533 | −0,052 (−8,8) |
| i:36 | C1 | −0,0047 | 0 | 0,0042 | −1,13 | 0,952 | 0,458 / 0,463 | −0,011 (−2,7) |
| ii:36 | C1 | +0,0017 | 0 | 0,0041 | +0,42 | 0,961 | 0,457 / 0,455 | −0,004 (−0,9) |
| i:karma | C1 | +0,0015 | 0 | 0,0053 | +0,29 | 0,591 | 0,465 / 0,464 | −0,008 (−1,5) |
| ii:karma | C1 | −0,0037 | 0 | 0,0053 | −0,69 | 0,595 | 0,466 / 0,470 | −0,013 (−2,4) |
| i:1500 | C1′a | −0,0002 | 0 | 0,0041 | −0,05 | 1 | 0,426 / 0,426 | aynı (kapı payı 1) |
| i:1500 | C1′ | 0,4264 | ≤ 0,4920 | 0,0035 | −18,6 | | | |
| i:1500 | C1′b | 0,4920 | 0,4920 | 0,0035 | 0,00 | | | |
| ii:1500 | C1′a | −0,0024 | 0 | 0,0041 | −0,60 | 1 | 0,421 / 0,423 | aynı |
| ii:1500 | C1′ | 0,4231 | ≤ 0,4920 | 0,0035 | −19,5 | | | |

Sürüm 1 provası, sürüm 2 ölçütleriyle (tohum 7311):

| Hücre | Ölçüt | Değer | Beklenen | z | Not |
|---|---|---|---|---|---|
| i:31,36 | C1 | +0,0059 | 0 | +0,99 | kapı koşullu havuzla −0,052 (z −8,3) |
| ii:31,36 | C1 | +0,0067 | 0 | +1,18 | kapı koşullu havuzla −0,044 (z −7,5) |
| i:100 / i:500 | C1 | +0,0087 / +0,0019 | 0 | +2,14 / +0,45 | kapı payı 1; iki havuz aynı |
| ii:100 / ii:500 | C1 | −0,0014 / −0,0035 | 0 | −0,34 / −0,87 | |
| i:1500 | C1′a / C1′ / C1′b | −0,0014 / 0,4283 / 0,4941 | 0 / ≤ 0,4920 / 0,4920 | −0,35 / −18,0 / +0,59 | |
| i:4500 | C1′a / C1′ / C1′b | +0,0031 / 0,3214 / 0,4921 | 0 / ≤ 0,4954 / 0,4954 | +0,79 / −49,2 / −0,94 | |
| ii:1500 | C1′a / C1′ | −0,0027 / 0,4253 | 0 / ≤ 0,4920 | −0,67 / −18,9 | |
| ii:4500 | C1′a / C1′ | −0,0063 / 0,3267 | 0 / ≤ 0,4954 | −1,62 / −47,7 | |
| adım:31,36 | C2 / C3 | 0,93735 / 0,49415 | 0,94019 / 0,49688 | −1,69 / −0,77 | |

Okuma:
- **Kapı seçim yanlılığı gerçektir ve (a2) havuzu onu soğurur.**
  - Kapı koşullu (TR-6a / sürüm 1) havuzla fark 28,5'te ≈ −0,10, 31,36'da ≈ −0,05'tir (z −7,5 … −9).
  - (a2) havuzuyla aynı hücreler |z| ≤ 1,03'tür.
  - Karma hücrelerde (λ 20–60 karışımı) (a2) +0,0015 / −0,0037'dir. Kapı koşullu havuz −0,008 / −0,013'tür (z −1,5 /
    −2,4).
- **Kenar hücrelerinde** C1′a ve C1′b dar ölçütlerdir ve tutar: |z| ≤ 1,62 ve ≤ 0,94. C1′ yön ölçütü olarak tutar.
- **i:100'ün z'si** 2,14 (tohum 7311). İNCELEME-1'in bağımsız koşusunda +0,96 (tohum 8801). 20 C1 / C1′a satırı
  içinde en büyük |z| budur; olağandışı değildir (İNCELEME-1 §4 madde 1).
- **(ii)'de hat − ham farkı** küçük N0'da da 0,02'yi aşar (−0,023 / −0,037). Bu kenar etkisi değil, ham (D4) oyun lob içi
  kümelenmeyle yukarı kaymasıdır (§C4 R2). (ii)'nin kenar etkisinin ölçüsü hat P(D) − kesindir: −0,001 / −0,020 /
  −0,067 / −0,169 (N0 100 / 500 / 1500 / 4500).
- **i:500 hücresi kenar dışı sınaması için tam temsilî değildir.** Denemelerin kapı N0'ı 500 civarında dalgalanır;
  gerçek koşuda yaklaşık yarısı kenar sayılırdı (İNCELEME-1 §4 madde 2). Bilgi olarak yazılır.

Tamlık ((d), tohum 7312, 96 hücre × 20 000): geçti. En büyük fark +0,0038 (M7, Mc 1, N0 4500, aσ 0; eşik 0,02).
12 hücrenin bütün denemeleri veri yoktur (geçer sayılır); ortalama veri yok payı 0,232. Tamlık kodu sürüm 2'de
değişmedi.

H1 bilgisi (tohum 7400, (i) dünyası, kalıcı −10 kPa): N0 500 / 1500 / 4500'de 400 / 300 / 150 denemede hat ve
kümesizleştirmesiz düşüş oyu payı 1,000, artış oyu payı 0,000.

## C7. Güç kaybı

p₀ = max(0,50; …) alt sınırı yüzünden kenar etkisi α'yı bozmaz: H0'da düşüş oyu olasılığı 0,50'nin altına iner,
eşik yerinde kalır. Bedeli güçtür. Hesap (`guc_kaybi_c`, `tr6c_prova_bilgi.json` `guc`):
- TR-6a §4.5 tasarım dünyası: K = 23, c(23; 0,50) = 16, küme başına oy olasılığı p₁ = 0,75 = f · P_D1 + (1 − f) · w,
  f = 0,549 (doğru loblu küme payı).
- m kümede yanlış loblu (H0 düzeyindeki) oy olasılığı w, (i) dünyasının hat − ham D farkı kadar düşer: küme başına
  Δp = (1 − f) · fark. H1 tarafı değişmez (§C6 H1 bilgisi). Bu bir modeldir, ölçüm değildir.
- Kenarsız güç 0,8037'dir.

| N0 (yapay kapı oranı) | küme başına Δp | m = 1 | m = 2 | m = 5 | m = 23 |
|---|---|---|---|---|---|
| 31,36 | −0,0004 | 0,8036 | 0,8036 | 0,8034 | 0,8025 |
| 100 | −0,0008 | 0,8036 | 0,8035 | 0,8031 | 0,8010 |
| 500 | −0,0077 | 0,8026 | 0,8015 | 0,7983 | 0,7783 |
| 1500 | −0,0297 | 0,7996 | 0,7954 | 0,7826 | 0,6988 |
| 4500 | −0,0770 | 0,7930 | 0,7820 | 0,7473 | 0,5068 |

Okuma:
- Önsayımda kapı N0'ı 500'ü aşan iki temsilci vardır (Tokachi-oki ≈ 584, Tohoku ≈ 4501). Bu ikisi için kayıp
  0,804 → ≈ 0,79'dur (m = 2, 1500 ile 4500 satırları arası). İNCELEME-1'in bağımsız hesabı 0,7977 → 0,7899'dur.
- 500'ün altındaki bütün kümeler kural dışıdır. En kötü durumda (23 kümenin hepsi N0 ≈ 500) güç 0,778'dir.
- Karşılaştırma (R3, "veri yok"): K = 23'te tek bir kümenin düşmesi K'yi 22'ye indirir ve hüküm "güç yok" olur (güç
  0). K_kapı 24'te iki küme kaybı aynı sonucu verir. R1′'nün kaybı bunun yanında küçüktür.
- w'nin 0,2–0,4 olduğu dünyada (gölgede gerçek artış, TR-6a §4.5) temel güç zaten 0,80'in altındadır; kenar kaybı onun
  üstüne eklenir.
- **§C3a'nın bedeli:** önsayım dünyasında v1'e göre 0,004 ((i)) ve 0,008 ((ii)); K ve kapı değişmez (§C3a tablosu).
- Kalibrasyon gürültüsünün bedeli (TR-6a §4.6: p̂₀ gürültüsü yüzünden p₀ > 0,50) bu tabloya eklenmez; §C3a'nın
  benzetimi onu içerir.

Ters yön notu ("gölgede anlamlı artış"; `ters_yon_alfa_c`, H0 artış oyu olasılığı 0,47): kenarsız gerçek α 0,0245.
Kural olmasaydı artış kayması m kümede bunu büyütürdü: N0 4500'de m = 1 / 2 / 5 / 23 için 0,029 / 0,034 / 0,053 /
0,399; N0 1500'de 0,026 / 0,028 / 0,033 / 0,090. Kural 4 kenar kümelerinin A'sını saymadığı için bu kayma ortadan
kalkar. 500'ün altında kalan kayma en kötü durumda (m = 23, N0 500) α'yı 0,035'e çıkarır; 0,05'in altındadır.

## C8. Kapı, hüküm adları, yeniden açma ve koşu sırası

- **Kapı:** K ≥ 23, aynen (TR-6a §5). K_kapı < 23 ise olay sonrası veri indirilmez, hüküm "güç yok", aday elenmez.
  "Güç yok", bu veriyle yalnız büyük bir etkinin sınanabileceği anlamına gelir (§C11).
- **Hüküm adları:** TR-6a §6.4'ün kapalı listesi aynen: "koşulmadı (yöntem: Okada sınaması | yapay katalog sınaması |
  tamlık sınaması)", "güç yok", "güç yok (ölçü yanlı)", "H1", "H0", "ayırt edilemez" ve düşürücü, niteleyici ve
  ekleri. Yeni ad gerekmedi: ne kenar kuralı ne kalibrasyon havuzu kümeyi düşürür ya da hükmü niteler. (d)'nin "veri
  yok (tamlık kestirilemedi)" düşmesi Ek 1 E1.3'teki gibi "güç yok" cümlesine neden olarak yazılır. TR-6c hükmü
  "TR-6c: <ad>" diye anılır. "H0" hükmü kenar kümesi sayısıyla birlikte yazılır (§C9 madde 9).
- **Yeniden açma:** TR-6a §14 aynen. TR-6c "koşulmadı (yöntem: …)" ile kapanırsa yeniden açma yine ancak ayrı bir ön
  kayıtla olur ve o ön kayıt da yöntem sınamasını dondurmadan önce tam ölçekte prova eder. TR-6a'nın kapanışı
  ("koşulmadı (yöntem: yapay katalog sınaması)") değişmez; TR-6c onun yeniden koşulması değil, ardılıdır.
- **Koşu sırası:**
  1. Bu taslak ikinci kez bağımsız incelenir; bulgular işlenir. Metin "DONDURULDU" diye commit + push edilir. Kodda
     `TR6C_ONKAYIT_SHA` ve `TR6C_GOVDE_BAYT` dondurulan gövdeyle doldurulur (ayrı commit).
  2. Bağlayıcı yöntem sınaması bir kez: `python3 -I -B kayit/turetme/tr6/tr6a_kosu.py --tasarim c sinama --baglayici
     --parca-dizini <dizin>` (tohum 20261116 ve 20261117). Kod TR-6a gövdesini ve TR-6c gövdesini sha256 ile, kod ve
     ön kaydın commit + push edildiğini git ile denetler. Çıktı `tr6c_sinama_sonuc.json`, commit + push.
  3–6. TR-6a §9 adım 3–6, `--tasarim c` ile:
     - manifest (`tr6c_manifest.json`, `tr6c_on_ham_sha256.txt`);
     - bağımsız kod incelemesi (`TR-6c_KOD-INCELEME.md`); §C3a havuzunu, §C4 kuralını ve `--tasarim c` yollarını
       özellikle denetler;
     - olay sonrası tek indirme (`tr6c_son_ham_sha256.txt`, `tr6c_son_kayit.json`);
     - tek koşu (`tr6c_sonuc.json`, `tr6c_sonuc.md`, işaret `TR6C_OLAY_SONRASI_OYLAR_SAYILDI`).
- Ham arşiv dizini TR-6a'nınkiyle aynıdır (`/mnt/project-files/turetme/tr6a-ham/`); TR-6c dizinleri `on_`/`son_`
  önekli ve zaman damgalıdır. TR-6a'nın olay sonrası verisi yoktur; TR-6c'nin manifesti olay öncesi veriyi yeniden
  indirir.

## C9. Bilinen zayıflıklar

TR-6a §11'in 18 maddesi aynen geçerlidir. Özellikle ve yeni olarak:
1. **K'nin 23'ün altına düşme olasılığı yüksek (TR-6a'dan).** (d) ile K_kaba 28'dir (TR-6a 29).
   - Kaba N0'lar yarıya inerse K 19, Mc + 0,5 ile 11 olur (TR-6a §10; (d)'nin Sumatra çıkarması bunları bir
     azaltabilir).
   - Gerçek lob tanımı, lob Mc'si ve (d)'nin Mc_son eki (+0,4) K'yi ve oyun gördüğü oranı aşağı çeker.
   - Yazarın önseli **P(K < 23) ≈ 0,75** (TR-6a: 0,7). En olası sonuç "güç yok"tur; bu durumda olay sonrası veri
     indirilmez ve aday elenmez (§C11).
   - §C3a K'yi değiştirmez.
2. **Kenar etkisi yöntemde kalır.** §3.6 pencereleri değiştirilmedi. Tanının V2–V4 biçimleri (uzun ön tampon,
   kesintisiz kümesizleştirme) etkiyi ancak kısmen giderir (N0 1500'de z ≈ −4 kalıyordu). §C4 etkiyi ortadan
   kaldırmaz, yönünü tutucu tarafta tutar ve kalibrasyondan ayırır. Bedeli güçtür (§C7).
3. **Kenar sınırı yapay dünyaya dayanır.**
   - Etkinin büyüklüğü gerçek kümelenmeye, Mc_kul'a ve lob geometrisine bağlıdır. Yapay dünyanın lob içi kümelenmesi
     zayıftır.
   - Kural tek bir sayıya (kapı N0 500) bağlanır. 500'ün hemen altındaki bir kümede kalan kayma −0,013 ((i)) ile
     −0,020 ((ii)) arasıdır (hat P(D) − kesin).
   - Sınır, önsayımın 316–584 boşluğuna düşer (§C4).
4. **Kalibrasyonun soğurmadığı yanlılık.**
   - Risk 6 sınanmadı (TR-6a kod incelemesi): lobdaki ana şok artçıları ve büyük artçıların GK pencereleri gerçek son
     pencereyi boşaltabilir (H1 lehine). Sahte zamanlarda büyük ana şok olmadığından p̂₀ bunu soğurmaz. Korumalar S7,
     S1 ve D4'tür.
   - Bu türden bir uyuşmazlık δ ≈ 0,03'ü aşarsa her tasarımda α 0,05'i aşar (İNCELEME-1 §3.4). Bütün adaylar kapı
     sınırındayken δ 0,02 bile (a2)'de α'yı 0,057'ye çıkarır (§C3a).
   - Bu yanlılık kenar etkisinin tersi yöndedir; ikisinin toplamı bilinmez.
5. **(d)'nin oy oranı bedeli.** Yapay dünyada Mc_kul = Mc_lob + 0,2'dir; oyun gördüğü oran kapı oranının %63'üdür.
   Kapıyı sınırda geçen bir lobda kalıcı −10 kPa'da düşüş oyu olasılığı 0,987'den (TR-6a §4.5, 335 g, ΔMc 0) 0,940'a
   iner (§C3, C2). Gerçek veride ΔMc daha büyük olabilir (TR-6a §6.2 kural 6, etkin N0 cümlesi).
6. **Bağlayıcı sınama uzun sürer** (≈ 19 saat CPU). Parçalı ve belirlenimci yapıldı; kesinti sonucu değiştirmez.
7. **Kenar kümelerinin artış oyu sayılmaz.** O kümelerde gerçek bir artış görülemez; ters yön notu ve S2'nin artış
   yönü onlar olmadan karar verir. S1, S7 ve S2 de kenar lobları olmadan sayılır (§C4 kural 7); K⁺, K_nt ve K_nk
   azalabilir ve "koşulamadı" olasılığı artar.
8. **Kalibrasyon havuzunun bileşimi değişti (§C3a).**
   - Kenar kümelerinin sahteleri çıkar: önsayımda Tokachi-oki'nin 3 geçerli sahte zamanı (J 64 → 61; Tohoku'nun
     yoktur).
   - Kapı altı adayların sahteleri girer; bunların çoğu sahte kapıdan geçmez.
   - J'nin değeri manifestte görülecek.
   - Havuzun doğruluğu, kapı altı kümelerin sahte pencerelerinin K_kapı kümelerininkiyle aynı yapıda olmasına
     dayanır (aynı katalog kuralları, aynı lob ve Mc kuralları). Kapı altı kümelerde katalog ve Mc daha kötü olabilir.
     Bu fark p̂₀'ı iki yönde de kaydırabilir; yapay dünya bunu sınamaz.
9. **Kenar kümeleri yanlış H0 oranını büyütür (İNCELEME-1 Z7).**
   - p₁ = 0,75 dünyasında (f 0,549) yanlış H0 (X ≤ h) oranı K 23'te kenarsız 0,043'tür.
   - Önsayımın iki kenar kümesiyle 0,045, beş Tohoku benzeri kümeyle 0,059'dur (K 28'de 0,031 / 0,033 / 0,042).
   - "H0 (büyük etki yok)" hükmü kenar kümesi sayısıyla birlikte okunur.

## C10. Kod, sınamalar ve yeniden üretim

Kod kopyalanmadı. TR-6c, `tr6a_kosu.py` ve `tr6a_yapay.py` içinde `--tasarim c` seçeneğidir.

`tr6a_kosu.py`:
- `tasarim_sec("c")` dosya yollarını `tr6c_*`'ye, tamlık kuralını `("yedek_d",)`'ye ve çıktı adını (`AD`) "TR-6c"ye
  çevirir. `AD`, İNCELEME-1'de eklendi.
- `onkayit_uyusmuyor()` TR-6c'de TR-6a gövdesini de denetler ve TASLAK'ta durur.
- §C3a: `manifest` içinde, yalnız `TASARIM == "c"` iken `kalibrasyon_kumeleri` (kapıdan önceki küme seti, kenar
  hariç) ve bu havuzdan p̂₀; liste manifest çekirdeğinde.
- §C4:
  - `Analiz.kenar_birimleri`;
  - `Analiz._kenar_A` (kenar A'sı `None`: sayılmaz);
  - `satir_istatistigi` (Y ve paydası `K_Y` yalnız sayılan A'lardan);
  - `hukum_kur` (ters yön eşiği c⁺(K_Y; p₀⁺));
  - `Analiz._kontrol_kenar_disi` (S1 / S7 süzgeci, manifest ve tamlık elemesinde);
  - `_nk_kumeleri` (kenar kümesi S2'den çıkar);
  - `N0_UST_C = 500.0`.
- `sinama --prova | --baglayici | --gelistirme`, `--hucreler`, `--parca-dizini`, `--yaz`.

`tr6a_yapay.py`:
- `TekBirimSinama(kural=…)`; `deneme(…, ham=True)` (kümesizleştirmesiz eşli oylar ve (d)'nin veri yok dalı).
- `HUCRELER_C` (17 hücre; sürüm 2'nin 6 hücresi sona eklendi, eski hücrelerin kodu ve parça baytları değişmedi),
  `KARMA_C`.
- `hucre_parcasi_c`. Bağlayıcı ve tanı tohumlarını `baglayici=True` dışında reddeder. `baglayici=True` iken
  `TR6C_ONKAYIT_SHA` boşsa da reddeder.
- `hucre_ozeti_c` (C1 bütün denemelerden; C1′a, C1′, C1′b; kapı koşullu havuz bilgi satırı), `hucre_kos_c`,
  `prova_c`, `baglayici_sinamalar_c`, `tamlik_prova_c`, `kesin_c`, `dtau_kesin_c`, `guc_kaybi_c`, `ters_yon_alfa_c`,
  `tohum_denetle_c`.

`tr6c_z2.py` (yeni): §C3a'nın yapay kanıtı (`kayit`: λ ızgarasında deneme kayıtları; `secim`: küme düzeyi benzetim,
dört tasarım).

`Analiz.kapi_degerleri` yalnız tek birim provasında (`yalniz_golge`) gölge dışı lobların kapısını atlar; gölge
sayıları aynıdır.

**TR-6a bit düzeyinde korunur.** Varsayılan tasarım "a"dır. Bütün sürüm 2 değişiklikleri `TASARIM == "c"` koşuluna
bağlıdır. Tek istisna `satir_istatistigi`dir: o da bütün A'lar sayılırken (TR-6a) aynı çıktıyı verir ve `K_Y` anahtarını
yalnız bir A sayılmadığında yazar. `TTasarimC.test_tr6a_bit_duzeyi` dört özeti sabit tutar ve geçer.

**Sınamalar:** `python3 -I -B kayit/turetme/tr6/tr6a_test_yapay.py` → 68 sınama, hepsi geçti (≈ 2 dakika; sürüm 1'de 62, İNCELEME-1'den sonra 66). Sürüm 2'nin eklediği ve değiştirdiği
sınamalar:
- kenar kuralı: A sayılmaz, Y'nin paydası `K_Y`, y05 S2'de yok, `kalibrasyon_kumeleri` havuzu ve J'si;
- `test_kenar_A_paydasi_ve_kontrol_suzgeci` (yeni);
- `test_baglayici_parca_korumasi` (yeni);
- C1′a / C1′ / C1′b adları ve (ii)'de C1′b'nin olmaması;
- bütün denemelerden havuz (veri yok denemesi dahil) ve kapı koşullu havuz bilgi satırı;
- karma hücre;
- 17 hücrelik sabitler.

Yeniden üretim (deponun kökünde):

```
python3 -I -B kayit/turetme/tr6/tr6a_test_yapay.py
python3 -I -B kayit/turetme/tr6/tr6c_z2.py kayit i 7331 6000 <dizin>/z2_kayit_i.json      # ≈ 25 dk
python3 -I -B kayit/turetme/tr6/tr6c_z2.py kayit ii 7331 6000 <dizin>/z2_kayit_ii.json    # ≈ 30 dk
python3 -I -B kayit/turetme/tr6/tr6c_z2.py secim <dizin>/z2_kayit_i.json <dizin>/z2_kayit_ii.json 20000 7332 \
    kayit/turetme/tr6/tr6c_z2_secim.json                                                  # ≈ 1 dk
python3 -I -B kayit/turetme/tr6/tr6a_kosu.py --tasarim c sinama --prova --tohum 7321 --deneme 20000 \
    --parca-dizini <geçici_dizin> --hucreler i:31.36,ii:31.36,i:28.5,ii:28.5,i:36,ii:36,i:karma,ii:karma,i:1500,ii:1500
# --yaz özetleri tr6c_prova_<hücre>.json adıyla yazar; depodaki 7321 özetleri tr6c_prova_t7321_<hücre>.json adıyla
# saklandı (7311 özetleri tr6c_prova_<hücre>.json'da kaldı). ≈ 2,5 saat CPU (çoğu i:1500 ve ii:1500)
```

## C11. Etki büyüklüğü: kaynağı, görülebilir en küçük etki ve olumsuz sonucun anlamı (yeni; İNCELEME-1 Z6)

**Kaynak.** p₁ = 0,75 (kapıdan geçen bir kümenin gölge lobunda düşüş oyu olasılığı) **bizim tahminimizdir**,
literatürden alınmış değildir.
- Literatürde doğrulanmış küresel bir değer yoktur. Bildirilen bulgular gölgelerde artışı da içerir (Mallman & Zoback
  2007; Hardebeck & Harris 2025).
- Fiziksel karşılığı TR-6a §4.5'teki dünyadır: kümelerin f ≈ 0,55'inde lob doğru yerdedir ve kalıcı −10 kPa vardır
  (P_D 0,987). Kalanında oy H0 düzeyindedir (w ≈ 0,46).
- Hainzl vd.'nin CV ≈ 1 bulgusu yüzünden bu iyimser bir dünyadır.
- Aynı tahmin `kayit/turetme/ESIK-DAYANAGI.md` tablosunda TR-6a satırında yazılıdır.

**Görülebilir en küçük etki** (tek yanlı kesin binom, α 0,05, güç 0,80; `inc_c_alfa.py` `mde`, K 24 (a1)'in önsayım K'si):

| K | 23 | 24 | 25 | 28 | 30 | 35 | 40 |
|---|---|---|---|---|---|---|---|
| en küçük p₁, p₀ 0,50 | 0,749 | 0,760 | 0,770 | 0,730 | 0,718 | 0,707 | 0,698 |
| en küçük p₁, p₀ 0,52 | 0,788 | 0,760 | 0,770 | 0,763 | 0,749 | 0,734 | 0,722 |

f cinsinden (w 0,457, P_D 0,987): p₀ 0,50'de K 23 için f ≥ 0,55, K 28 için f ≥ 0,51. §C3a, kapı sınırındaki kümelerde
p₀'ı gerçek H0 düzeyine (≈ 0,55'e kadar) çıkarabilir. O zaman görülebilir en küçük p₁ bu tablonun p₀ 0,52 satırından
da yüksektir.

**Kapı altı (K < 23): yalnız büyük etki.** K < 23'te olay sonrası veri indirilmez ve aday elenmez (§C8). Bilgi olarak,
o K'lerle görülebilecek en küçük etki (p₀ 0,50): K 22 / 19 / 15 / 11 / 8 için p₁ ≥ 0,778 / 0,788 / 0,843 / 0,857 / 0,896 (c 16 / 14 / 12 / 9 / 7). K 19 ve 11, TR-6a §10'un "kaba N0 yarıya" ve "Mc + 0,5" K'leridir. Bu sayılar hüküm vermez; "güç yok"un ne kadar büyük bir
etkiyi dışarıda bıraktığını söyler.

**Duyarlılık (×0,5 / ×2).**
- Etki (p₁ − 0,50) yarıya inerse (p₁ 0,625; f ≈ 0,27): güç 0,80 için K ≈ 102 gerekir (kalıcı olarak 111). Önsayımda
  K_kaba 28'dir; bu etki bu sınavla görülemez.
- Etki iki katına çıkarsa (p₁ → 1,0; bütün loblar doğru ve P_D ≈ 1): K ≈ 5–8 yeter. K ≥ 23 kapısı zaten geçilir.
- Ara değerler: p₁ 0,70 → K 37 (kalıcı 42); 0,80 → 18; 0,875 → 11.

**Olumsuz sonuç ne söyler.**
- "H0", K 23'te yalnız p₁ ≥ 0,75'i dışlar (K 28'de ≥ 0,73'ü). 0,55–0,70 arasındaki küçük ve orta etkileri dışlamaz.
- Kenar kümeleri bu dışlamayı biraz zayıflatır (§C9 madde 9: yanlış H0 0,043 → 0,045).
- "Ayırt edilemez", etkinin yokluğu hakkında bilgi taşımaz.
- "Güç yok" (K_kapı < 23; yazar önseli ≈ 0,75) bir eleme değildir. Bu veriyle yalnız büyük bir etkinin sınanabileceğini
  söyler ve sınamayı yapmaz.
- Bu sayılar `kayit/turetme/ESIK-DAYANAGI.md` tablosundaki TR-6a satırıyla aynıdır (0,70 → 37, 0,80 → 18).
