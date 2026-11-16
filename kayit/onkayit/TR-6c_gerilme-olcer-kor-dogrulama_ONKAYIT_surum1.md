# TR-6c ön kaydı: hız-durum gerilme ölçeri bilinen kosismik Coulomb gölgelerini kör olarak doğru işaretle buluyor mu? (TR-6a'nın ardılı)

Tarih: 16 Kasım 2026. Durum: **TASLAK sürüm 1, bağımsız incelemeye hazır.** Dondurulmadı; kodda
`TR6C_ONKAYIT_SHA = None` olduğu sürece bağlayıcı aşamalar (`--tasarim c sinama --baglayici`, `manifest`, `kos`)
koşmaz.

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
(Kumamoto, Ridgecrest, Tohoku; TR-6a §3.4).

Kullanılan tohumlar (hiçbiri bağlayıcı değil): 7311 (yapay katalog provası), 7312 (tamlık provası), 7400 (H1 bilgi
koşusu), 5, 11, 98, 99 (geliştirme). TR-6a'nın bağlayıcı tohumları (20261114, 20261115), tanının tohumları (601–608) ve
TR-6c'nin bağlayıcı tohumları (20261116, 20261117) kullanılmadı. Kod bu tohumları geliştirme ve provada reddeder.

## C0. Bağlayıcı metinler ve sıra

1. **Bu metin.**
2. **TR-6a ön kaydı**: dondurulmuş gövde (`TR-6a_gerilme-olcer-kor-dogrulama_ONKAYIT.md`'nin ilk 126 740 baytı, sha256
   `41ca1e951d330ab72d106be79bb5f700b415d9574dbddff3da0a12ad73fea94e`) ve Ek 1 (E1.1–E1.4 ve "kapı seçim yanlılığı"
   paragrafı). Dondurulan liste `tr6a_olay_listesi.json` (sha256 `0cde4fa1…048f`) ve `tr6a_onkayit_sayilar.json`
   (sha256 `e39b3252…c4f`) bu metnin de parçasıdır.
3. TR-6a §0'daki sıranın kalanı (İNCELEME-2, İNCELEME-1, `TR-6_SAYIM.md`).

Bu metin yalnız §C1'de sayılan maddeleri değiştirir. Geri kalan her tanım, eşik, tablo, kalıp ve ad TR-6a'daki gibi
geçerlidir. TR-6a kural metinlerindeki "TR-6a" adı "TR-6c" diye, dosya adları §C8'e göre okunur. Metin ile kod
çelişirse metin geçerlidir.

## C1. Değişiklik listesi

| # | Değişen | TR-6a'da | TR-6c'de | Yer |
|---|---|---|---|---|
| D1 | Yapay katalog sınamasının Δτ = 0 ölçütü | koşulsuz P(D), kesin Poisson değerine karşı, 3,5 SE (i); p̂₀ − P(D \| kapı) yalnız (ii)'de | (i) ve (ii)'de aynı ölçüt: p̂₀ − P(D \| kapı, veri var), iki yanlı 3,5 SE; kenar birimi hücrelerinde tek yanlı ölçüt | §C3 |
| D2 | N0 ızgarası | {31,36; 100; 500} | {31,36; 100; 500; 1500; 4500}, iki dünyada | §C3 |
| D3 | Kenar etkisi kuralı | yok | gölge kapı N0'ı > 500 olay/yıl olan küme K'de kalır; sahte oyları kalibrasyona girmez; gölge artış oyu 0 sayılır | §C4 |
| D4 | Tamlık kuralı | A2 ve yedek merdiveni (a)–(d), sınamayla seçilir | (d) baştan ana kuraldır; merdiven yok | §C5 |
| D5 | Tohum ve koşu biçimi | 20261114 / 20261115, tek parça | 20261116 / 20261117; hücre başına 20 parça × 1000 deneme, belirlenimci parça tohumu | §C3 |
| D6 | Dondurma öncesi tam ölçekli prova | yoktu | yapıldı (bağlayıcı olmayan tohumla, hücre başına 20 000 deneme) | §C6 |
| D7 | Dosya adları | `tr6a_*` | `tr6c_*` (kod `tr6a_*.py` içinde `--tasarim c`) | §C8 |

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
- §4.1–§4.6: sayılar, kapı (Aσ = 19 kPa sabit, N0 ≥ 31,36, n_on ≥ 155), koşullu binom oyu, Δτ_est, sahte zaman
  kalibrasyonu (üç sahte zaman, geçerlilik, sahte kapı, J < 30, p₀ > 0,60), kapı seçim yanlılığı paragrafı (Ek 1);
- §5 kapılar ve işlem sırası (§C4 kuralının yeri eklenir), testere dişi tablosu, "en zayıf" tanımı;
- §6 eşik tabloları, yorum kuralları, kalıplar, §6.4 kapalı hüküm listesi ve bileşimi;
- §7 ikincil satırlar (D2 satırı yok, §C5), §8 çıktı tablosu;
- §9 adım 3–6 (manifest, körlük okuma kuralları, kod incelemesi, olay sonrası tek indirme, tek koşu), dosya adları §C8;
- §10 beklenti (K_kaba §C5'e göre 28), §11 bilinen zayıflıklar, §12, §13 (Marmara'ya taşıma), §14 yeniden açma şartı;
- Ek 1 E1.4 (a)–(g).

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
   - **Hücreler:** (i) ve (ii) dünyalarında Δτ = 0 ve N0 ∈ {31,36; 100; 500; 1500; 4500} (10 hücre); adım dünyasında
     N0 31,36 (1 hücre). N0, lobun Mc_lob üstü yıllık oranıdır. Yapay dünyada (d)'nin Mc_son eki yüzünden
     Mc_kul = Mc_lob + 0,2 olur; oyun gördüğü oran N0_kul = N0 · 10^−0,2'dir. Kesin değerler N0_kul ve 275 g ile
     hesaplanır.
   - **Deneme sayısı:** hücre başına 20 000; 1000 denemelik 20 parça. Parça p'nin tohumu `(20261116, hücre kodu, p)`'dir
     (hücre kodu `HUCRELER_C` sırası, 1'den). Parça dosyaları diske yazılır. Koşu kesilirse aynı komut kalan parçaları
     koşar. Parçalar belirlenimcidir: aynı parça aynı baytları verir. Parça dosyalarının sha256'ları çıktıya yazılır.
     Çıktı `tr6c_sinama_sonuc.json` bir kez ("x" kipinde) yazılır. Ara parçalara bakılarak hiçbir kural, tohum ya da
     ölçüt değiştirilmez.
   - **Tanımlar** (bir hücrede, n deneme):
     - Gerçek oy yalnız gerçek kapıyı geçen (n_on ≥ 155, Mc_lob) ve gerçek Mc_son'u kestirilebilen denemelerden
       sayılır: P(D | kapı) bu denemelerdeki düşüş oyu payıdır.
     - p̂₀ = ΣS_i / ΣJ_i; J_i i. denemenin geçerli sahte zaman sayısı (sahte kapı ve sahte Mc_son dahil; tek birimde
       havuz geçersizliği yoktur), S_i geçerli sahte düşüş oyu sayısıdır. Gerçek Mc_son'u kestirilemeyen denemenin
       sahte oyları da paydadan çıkar.
     - SE(p̂₀ − P(D | kapı)) = √(SE₀² + SE_D²); SE₀ = sd(S_i − p̂₀ J_i) / (ort(J) √n), SE_D = sd(D) / √n_kapı (TR-6a
       (ii) ile aynı biçim).
   - **Ölçütler:**
     - **C1 (N0 ≤ 500; (i) ve (ii)):** p̂₀ − P(D | kapı), 0'a karşı iki yanlı 3,5 SE içinde.
     - **C1′ (N0 > 500, kenar birimi; (i) ve (ii)):** P(D | kapı) ≤ kesin Poisson P(D | H0) (N0_kul, 275 g) + 3,5 SE,
       SE = √(q(1 − q)/n_kapı), q kesin değer. Tek yanlıdır.
     - **C2 (adım, N0 31,36):** P(D) kesin değerle iki yanlı 3,5 SE içinde (N0_kul 19,79, 275 g: 0,94019).
     - **C3 (adım, N0 31,36):** Δτ_est'in kesin dağılımının medyanı m* (n_on ≥ 1; n_son = 0'da −∞) hesaplanır;
       Δτ_est < m* olan deneme payı kesin P(Δτ_est < m*) ile iki yanlı 3,5 SE içinde (m* = −10,333, olasılık
       0,49688).
   - **Sonuç kuralı:** TR-6a'daki gibi. Bir ölçüt tutmazsa kod hatası aranır; bulunan hata düzeltilir, hata listesi
     commit edilir ve bütün sınama aynı tohumla yeniden koşulur. Hata bulunamazsa TR-6c "koşulmadı (yöntem: yapay
     katalog sınaması)" diye kapanır; olay sonrası veri indirilmez, aday elenmez.
   - **Bilgi satırları** (hükmü değiştirmez): koşulsuz P(D) ve kesin değer (kenar etkisinin büyüklüğü), eşli
     "hat − kümesizleştirmesiz" farkları (D ve A), p̂₀⁺ − P(A | kapı), kümesizleştirmesiz (D4 biçimi) p̂₀ ve P(D | kapı),
     kapı payı, veri yok payı.

**Ölçütün gerekçesi (D1).** Ana hüküm P(D)'yi kümesizleştirmesiz kesin Poisson değeriyle değil, aynı işlem zincirinden
geçen sahte pencerelerden kalibre edilen p₀ ile karşılaştırır. Sınanması gereken şey zincirin kendi H0 değeridir:
gerçek ve sahte pencereler aynı yapıda mı ve kalibrasyon kenar etkisini soğuruyor mu. TR-6a'nın (ii) ölçütü bu
karşılaştırmayı zaten yapıyordu; bağlayıcı koşuda N0 500'de p̂₀ 0,461, P(D | kapı) 0,4626, fark −0,0016 idi. TR-6c bu
biçimi (i)'ye de uygular. Kesin Poisson değeri bilgi satırı olarak kalır.

**C1′'nün gerekçesi.** Kenar birimlerinin sahte oyları kalibrasyona girmez (§C4). Bu birimlerde dayanılan özellik
kalibrasyon değil, kenar etkisinin yönüdür: H0'da düşüş oyu olasılığı kesin değerin üstüne çıkmamalıdır. C1′ bunu
sınar. Bu hücrelerde de p̂₀ − P(D | kapı) bilgi olarak yazılır.

**Süre.** Prova ölçümüyle (§C6) bağlayıcı yapay katalog sınaması ≈ 18 saat CPU'dur; çoğu N0 4500 hücrelerindedir.
Tamlık sınaması ≈ 10 dakikadır. Parçalı koşu iki süreçle ve kesintiye dayanıklı yürür.

## C4. Kenar etkisi kuralı (yeni)

**Kural.** Seçilen katalogda gölge lobunun kapı N0'ı (Mc_lob, ön pencere, kümesizleştirilmiş; manifestte yazılı)
**500 olay/yılı aşan** birim "kenar birimi"dir (n_on ≥ 2459). Kenar birimi temsilcisi olan küme "kenar kümesi"dir.
1. Kenar kümesi K_kapı'da kalır. K_kapı, testere dişi ve "en zayıf" sırası değişmez.
2. Kenar kümelerinin sahte oyları J, S ve S⁺'ya girmez (p̂₀ ve p̂₀⁺ öteki kümelerden). Sahte oyları manifestte bilgi
   olarak yazılır.
3. Kenar kümesinin düşüş oyu D, TR-6a'daki gibi kümesizleştirilmiş sayımla verilir.
4. Kenar kümesinin gölge lobu artış oyu A, ana satırda ve gölge lobunu kullanan bütün satırlarda (B1, S2, S3, S4, S5a,
   S5b, D1, D3a, D3b, D4, D5, D6, D7, D8, B4) **0 sayılır**. Özgün A değeri bilgi olarak yazılır. S1 (pozitif lob) ve
   S7 (nötr bölge) oyları değişmez.
5. Kural, işlem sırasında K_kapı sayıldıktan ve çıkarmalar yapıldıktan sonra, p₀ kalibrasyonundan önce uygulanır
   (TR-6a §5: … → K_kapı < 23 denetimi → **kenar kümeleri** → p₀ kalibrasyonu → …). Kenar birimleri ve kümeleri
   manifestte yazılır ve manifest çekirdeğine girer.
6. Satır kapılarında (S5a, D1, …) kenar birimi aynı tanımla, ana gölge kapı N0'ından belirlenir.

Kural hüküm adını değiştirmez. Sonuç dosyası kenar kümelerini, özgün A'larını ve sahte oylarını yazar.

**Neden gerekli.** Kümesizleştirme kısa son pencerede (275 g) uzun ön pencerede (1796 g) olduğundan göreli olarak daha
az olay siler. Bunun iki nedeni vardır: pencere sonundaki olaylar sonraki büyük olaylarla silinemez ("gelecek
kesmesi") ve son pencerenin önündeki tampon kısadır. n_son göreli olarak şişer: H0'da düşüş oyu azalır, artış oyu artar.
Etki N0 ile hızla büyür (§C6 tablosu: (i) dünyasında hat − kümesizleştirmesiz D farkı N0 31,36 / 100 / 500 / 1500 / 4500'de −0,001 / −0,002 / −0,017 / −0,066 / −0,171; hat koşulsuz P(D) − kesin Poisson: +0,004 / −0,006 / −0,013 / −0,064 / −0,174).

Tek birimli yapay dünyada sahte pencereler aynı yapıdadır ve p̂₀ etkiyi soğurur (C1; §C6). Gerçek koşuda ise p̂₀ bütün
kümelerin sahte oylarından havuzlanır ve p₀ = max(0,50; …) alt sınırını taşır. Bu yüzden yüksek N0'lı birkaç kümenin
kayması havuzda soğurulmaz. Önsayımda kaba N0'ı 500'ü aşan iki temsilci var: 2003 Tokachi-oki (583,7) ve 2011 Tohoku
(4501,4). Tohoku'nun hiç geçerli sahte zamanı yoktur (TR-6a §4.6).
- Düşüş oyu yönünde kayma H1 aleyhinedir: α korunur, güç düşer (§C7).
- Artış oyu yönünde kayma ters yön notunu ("gölgede anlamlı artış", TR-6a §6.1) şişirir. Bu not H0 ve ayırt edilemez
  hükümlerine eklenen bir cümledir ve R3 açıklamasını destekler. Kural 4 bunu kapatır.
- Kenar birimlerinin sahte oyları da aynı kaymayı taşır (düşük D′, yüksek A′). Havuza girerlerse p̂₀ düşer, p̂₀⁺
  yükselir; bileşim gerçek kümelerle uyuşmadığında (Tohoku gibi sahtesiz kümeler) bu kalibrasyonu bozar. Kural 2
  kalibrasyonu kenar etkisi ihmal edilebilir kümelere sınırlar.

**Seçimin yapay veriyle gerekçesi.** Üç seçenek prova verisiyle (§C6; tohum 7311, hücre başına 20 000 deneme)
karşılaştırıldı:
- **(R2) Kenar birimi kümesizleştirmesiz (D4) oyla oy verir.** (i) dünyasında D4 oyu yansızdır, ama (ii) dünyasında
  (lobda ikincil diziler) H1 yönüne kayar: kapıyı geçen denemelerde D4 P(D | kapı) N0 100 / 500 / 1500 / 4500'de 0,504 / 0,515 / 0,534 / 0,536, kesin değer 0,468 / 0,486 / 0,492 / 0,495 (fark +0,036 / +0,029 / +0,042 / +0,041; SE ≈ 0,0035). (i) dünyasında aynı satır 0,464 / 0,490 / 0,494 / 0,492'dir. Lobdaki kümelenme ayıklanmayınca aşırı saçılım düşüş oyunu
  artırır (TR-6a §4.3). Gerçek lobların kümelenmesi bu yapay dünyanınkinden güçlüdür ve kenar birimlerinin çoğunda
  kalibrasyon yoktur. **Reddedildi:** α riski.
- **(R3) Kenar birimi "veri yok (kenar etkisi)" olur, K ondan sonra sayılır.** α ve ters yön güvenlidir, ama K'yi
  düşürür. K_kaba 28 ve yazar önseli P(K < 23) ≈ 0,75 iken (§C9) bir ya da iki kümenin kaybı hükmü "güç yok"a
  çevirebilir (§C7 tablosu: K_kapı 23'te bir küme kaybı gücü 0'a indirir). Ayrıca Tohoku'nun bilinen sonucu H1
  aleyhinedir; onu kural gereği bile çıkarmak, yazarın bildiği bir H1 lehine seçim olurdu. **Reddedildi.**
- **(R1′) Seçilen: küme kalır, D değişmez, A 0, sahte oyları kalibrasyona girmez.** D yönündeki kayma tutucudur; C1′
  bunu her iki dünyada sınar. H1 dünyasında kenar etkisi oyu etkilemez: kalıcı −10 kPa'da N0 500 / 1500 / 4500'de hat
  ve kümesizleştirmesiz düşüş oyu payı 400 / 300 / 150 denemede 1,000'dır (tohum 7400, bilgi). Güç kaybı yalnız
  yanlış loblu (H0 düzeyindeki) kenar kümelerinden gelir (§C7).

**Neden 500.** Tolerans 0,02'dir; TR-6a'nın tamlık ölçütündeki yanlılık payıyla aynıdır. (i) dünyasında |hat − ham| D
farkı N0 500'de 0,017 (SE 0,002), 1500'de 0,066'dır. Izgarada toleransı aşmayan en büyük N0 500'dür. (ii) dünyasında hat P(D) − kesin
N0 500'de −0,020'dir; sınır toleransın kıyısındadır (§C9 madde 3). Sınır kapı N0'ına
(Mc_lob) uygulanır. Oy Mc_kul ≥ Mc_lob ile sayıldığından oyun gördüğü oran kapı N0'ından küçük ya da ona eşittir. Bu
yüzden sınır tutucu yöndedir: kural gerekenden fazla birime uygulanabilir, azına uygulanmaz.

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

Bunlar kümesizleştirmesiz değerlerdir. Hattın gerçek H0 değeri yüksek N0'da kenar etkisiyle daha düşüktür (§C4, §C6);
ana hükmün karşılaştırması p₀ iledir, bu tablolar bilgi ve güç hesabı içindir.

## C6. Dondurma öncesi tam ölçekli prova

TR-6a'nın dersi: yöntem sınaması dondurmadan önce tam ölçekte koşulur. §C3'ün bütün yapay katalog hücreleri ve tamlık
sınaması, bağlayıcı olmayan tohumlarla ve bağlayıcı koşuyla aynı kodla, hücre başına 20 000 denemeyle koşuldu:
`tr6a_kosu.py --tasarim c sinama --prova --tohum 7311 --deneme 20000` (yapay katalog, parça tohumu (7311, hücre kodu,
p)) ve tamlık için `tr6a_yapay.tamlik_prova_c(7312, 20000)`. Çıktılar `kayit/turetme/tr6/tr6c_prova_<hücre>.json` ve
`tr6c_prova_tamlik.json`'dur.

**Sonuç: 11 hücrenin hepsi ve tamlık sınaması geçti.** Prova, çalışma dizinindeki iki sürücü ve iki işçi betiğiyle
koşuldu. Betikler aynı işlevleri (`hucre_parcasi_c`, `prova_c`, `tamlik_prova_c`) çağırır; parça tohumu ve dosya
biçimi komuttakiyle aynıdır. Koşu ortada makine yeniden başlayınca kesildi. Yarım parçalar silindi, yalnız eksik
parçalar yeniden koşuldu. Kesintiden önce yazılmış üç parça (i:31,36, ii:100 ve adım hücrelerinin 0. parçası) son kodla
yeniden üretildi ve bayt bayt aynı çıktı. Özetler bütün parçalar bittikten sonra son kodla bir kez yazıldı;
`kod_sha256` alanı bugünkü `tr6a_yapay.py` / `tr6a_kosu.py` ile aynıdır.

Yapay katalog (tohum 7311, hücre başına 20 000 deneme, veri yok payı her hücrede 0):

| Hücre | Ölçüt | Değer | Beklenen | SE | z | Kapı payı | P(D) koşulsuz / kesin | hat − ham D | hat − ham A | p̂₀⁺ − P(A \| kapı) |
|---|---|---|---|---|---|---|---|---|---|---|
| i:31,36 | C1 | +0,0059 | 0 | 0,0059 | +0,99 | 0,466 | 0,4464 / 0,4426 | −0,0009 | −0,0018 | −0,0081 |
| i:100 | C1 | +0,0087 | 0 | 0,0041 | +2,14 | 1 | 0,4622 / 0,4682 | −0,0019 | +0,0017 | −0,0090 |
| i:500 | C1 | +0,0019 | 0 | 0,0041 | +0,45 | 1 | 0,4730 / 0,4862 | −0,0171 | +0,0158 | −0,0006 |
| i:1500 | C1′ | 0,4283 | ≤ 0,4920 | 0,0035 | −18,0 | 1 | 0,4283 / 0,4920 | −0,0658 | +0,0654 | +0,0016 |
| i:4500 | C1′ | 0,3214 | ≤ 0,4954 | 0,0035 | −49,2 | 1 | 0,3214 / 0,4954 | −0,1707 | +0,1763 | −0,0042 |
| ii:31,36 | C1 | +0,0067 | 0 | 0,0057 | +1,18 | 0,514 | 0,4428 / 0,4426 | −0,0229 | +0,0069 | −0,0089 |
| ii:100 | C1 | −0,0014 | 0 | 0,0041 | −0,34 | 1 | 0,4671 / 0,4682 | −0,0371 | +0,0220 | −0,0006 |
| ii:500 | C1 | −0,0035 | 0 | 0,0041 | −0,87 | 1 | 0,4658 / 0,4862 | −0,0495 | +0,0412 | +0,0029 |
| ii:1500 | C1′ | 0,4253 | ≤ 0,4920 | 0,0035 | −18,9 | 1 | 0,4253 / 0,4920 | −0,1083 | +0,1026 | +0,0038 |
| ii:4500 | C1′ | 0,3267 | ≤ 0,4954 | 0,0035 | −47,7 | 1 | 0,3267 / 0,4954 | −0,2097 | +0,2095 | +0,0058 |
| adım:31,36 | C2: P(D) | 0,93735 | 0,94019 | 0,0017 | −1,69 | | | | | |
| adım:31,36 | C3: P(Δτ_est < m*) | 0,49415 | 0,49688 | 0,0035 | −0,77 | | | | | |

Okuma:
- C1 en büyük |z| 2,14'tür (i:100). Bu, 3,5 sınırının altında ama 10 C1/C1′ satırı içinde beklenenden biraz büyüktür.
  Aynı hücrede p̂₀⁺ − P(A | kapı) −2,2 SE'dir. İkisi aynı yönde, sahte pencerelerin gerçek pencereye göre çok az
  daha "düşüşçü" olduğunu gösterir. Bunu kod hatası olarak okumak için bir dayanak bulmadım; bağlayıcı koşuda aynı
  hücreye bakılmalıdır.
- Kenar hücrelerinde (C1′) de kalibrasyon kenar etkisini soğurur: hücre içi p̂₀ − P(D | kapı) i:1500 −0,0014
  (z −0,35), i:4500 +0,0031 (z +0,79), ii:1500 −0,0027 (z −0,67), ii:4500 −0,0063 (z −1,62). Kenar kuralı bu soğurmaya
  dayanmaz, çünkü gerçek koşuda kenar birimleri kendi sahteleriyle değil havuzla karşılaştırılır (§C4).
- (ii)'de hat − ham farkı küçük N0'da da 0,02'yi aşar (−0,023 / −0,037). Bu kenar etkisi değil, ham (D4) oyun lob içi
  kümelenmeyle yukarı kaymasıdır (§C4 R2). (ii)'nin kenar etkisinin ölçüsü hat P(D) − kesindir: −0,001 / −0,020 /
  −0,067 / −0,169 (N0 100 / 500 / 1500 / 4500).

Tamlık ((d), tohum 7312, 96 hücre × 20 000): geçti. En büyük fark +0,0038 (M7, Mc 1, N0 4500, aσ 0; eşik 0,02).
12 hücrenin bütün denemeleri veri yoktur (geçer sayılır); ortalama veri yok payı 0,232.

H1 bilgisi (tohum 7400, (i) dünyası, kalıcı −10 kPa): N0 500 / 1500 / 4500'de 400 / 300 / 150 denemede hat ve
kümesizleştirmesiz düşüş oyu payı 1,000, artış oyu payı 0,000.

## C7. Güç kaybı

p₀ = max(0,50; …) alt sınırı yüzünden kenar etkisi α'yı bozmaz: H0'da düşüş oyu olasılığı 0,50'nin altına iner,
eşik yerinde kalır. Bedeli güçtür. Hesap (`guc_kaybi_c`, `tr6c_prova_bilgi.json` `guc`):
- TR-6a §4.5 tasarım dünyası: K = 23, c(23; 0,50) = 16, küme başına oy olasılığı p₁ = 0,75 = f · P_D1 + (1 − f) · w,
  f = 0,549 (doğru loblu küme payı).
- m kümede yanlış loblu (H0 düzeyindeki) oy olasılığı w, (i) dünyasının hat − ham D farkı kadar düşer: küme başına
  Δp = (1 − f) · fark. H1 tarafı değişmez (§C6 H1 bilgisi).
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
  0,804 → ≈ 0,79'dur (m = 2, 1500 ile 4500 satırları arası).
- 500'ün altındaki bütün kümeler kural dışıdır. En kötü durumda (23 kümenin hepsi N0 ≈ 500) güç 0,778'dir.
- Karşılaştırma (R3, "veri yok"): K = 23'te tek bir kümenin düşmesi K'yi 22'ye indirir ve hüküm "güç yok" olur (güç
  0). K_kapı 24'te iki küme kaybı aynı sonucu verir. R1′'nün kaybı bunun yanında küçüktür.
- Kalibrasyon kaybı (TR-6a §4.6: p̂₀ gürültüsü yüzünden p₀ > 0,50) bu tabloya eklenmez; TR-6a'daki gibidir. Kenar
  kümelerinin sahte oyları havuzdan çıkınca (§C4 kural 2) p̂₀ kenar kaymasıyla aşağı çekilmez, ama J azalır (§C9
  madde 8).

Ters yön notu ("gölgede anlamlı artış"; `ters_yon_alfa_c`, H0 artış oyu olasılığı 0,47): kenarsız gerçek α 0,0245.
Kural olmasaydı artış kayması m kümede bunu büyütürdü: N0 4500'de m = 1 / 2 / 5 / 23 için 0,029 / 0,034 / 0,053 /
0,399; N0 1500'de 0,026 / 0,028 / 0,033 / 0,090. Kural 4 kenar kümelerinde A'yı 0 saydığı için bu kayma ortadan kalkar.
500'ün altında kalan kayma en kötü durumda (m = 23, N0 500) α'yı 0,035'e çıkarır; 0,05'in altındadır.

## C8. Kapı, hüküm adları, yeniden açma ve koşu sırası

- **Kapı:** K ≥ 23, aynen (TR-6a §5). K_kapı < 23 ise olay sonrası veri indirilmez, hüküm "güç yok", aday elenmez.
- **Hüküm adları:** TR-6a §6.4'ün kapalı listesi aynen: "koşulmadı (yöntem: Okada sınaması | yapay katalog sınaması |
  tamlık sınaması)", "güç yok", "güç yok (ölçü yanlı)", "H1", "H0", "ayırt edilemez" ve düşürücü, niteleyici ve
  ekleri. Yeni ad gerekmedi: kenar etkisi kuralı ne kümeyi düşürür ne hükmü niteler. (d)'nin "veri yok (tamlık
  kestirilemedi)" düşmesi Ek 1 E1.3'teki gibi "güç yok" cümlesine neden olarak yazılır. TR-6c hükmü "TR-6c: <ad>"
  diye anılır.
- **Yeniden açma:** TR-6a §14 aynen. TR-6c "koşulmadı (yöntem: …)" ile kapanırsa yeniden açma yine ancak ayrı bir ön
  kayıtla olur ve o ön kayıt da yöntem sınamasını dondurmadan önce tam ölçekte prova eder. TR-6a'nın kapanışı
  ("koşulmadı (yöntem: yapay katalog sınaması)") değişmez; TR-6c onun yeniden koşulması değil, ardılıdır.
- **Koşu sırası:**
  1. Bu taslak en az bir kez bağımsız incelenir; bulgular işlenir. Metin "DONDURULDU" diye commit + push edilir. Kodda
     `TR6C_ONKAYIT_SHA` ve `TR6C_GOVDE_BAYT` dondurulan gövdeyle doldurulur (ayrı commit).
  2. Bağlayıcı yöntem sınaması bir kez: `python3 -I -B kayit/turetme/tr6/tr6a_kosu.py --tasarim c sinama --baglayici
     --parca-dizini <dizin>` (tohum 20261116 ve 20261117). Kod TR-6a gövdesini ve TR-6c gövdesini sha256 ile, kod ve
     ön kaydın commit + push edildiğini git ile denetler. Çıktı `tr6c_sinama_sonuc.json`, commit + push.
  3–6. TR-6a §9 adım 3–6, `--tasarim c` ile: manifest (`tr6c_manifest.json`, `tr6c_on_ham_sha256.txt`), bağımsız kod
     incelemesi (`TR-6c_KOD-INCELEME.md`; §C4 kuralını ve `--tasarim c` yollarını özellikle denetler), olay sonrası tek
     indirme (`tr6c_son_ham_sha256.txt`, `tr6c_son_kayit.json`), tek koşu (`tr6c_sonuc.json`, `tr6c_sonuc.md`, işaret
     `TR6C_OLAY_SONRASI_OYLAR_SAYILDI`).
- Ham arşiv dizini TR-6a'nınkiyle aynıdır (`/mnt/project-files/turetme/tr6a-ham/`); TR-6c dizinleri `on_`/`son_`
  önekli ve zaman damgalıdır. TR-6a'nın olay sonrası verisi yoktur; TR-6c'nin manifesti olay öncesi veriyi yeniden
  indirir.

## C9. Bilinen zayıflıklar

TR-6a §11'in 18 maddesi aynen geçerlidir. Özellikle ve yeni olarak:
1. **K'nin 23'ün altına düşme olasılığı yüksek (TR-6a'dan).** (d) ile K_kaba 28'dir (TR-6a 29). Kaba N0'lar yarıya
   inerse 19, Mc + 0,5 ile 11 olur (TR-6a §10; (d)'nin Sumatra çıkarması bunları bir azaltabilir). Gerçek lob tanımı,
   lob Mc'si ve (d)'nin Mc_son eki (+0,4) K'yi ve oyun gördüğü oranı aşağı çeker. Yazarın önseli **P(K < 23) ≈ 0,75**
   (TR-6a: 0,7). En olası sonuç "güç yok"tur; bu durumda olay sonrası veri indirilmez ve aday elenmez.
2. **Kenar etkisi yöntemde kalır.** §3.6 pencereleri değiştirilmedi. Tanının V2–V4 biçimleri (uzun ön tampon,
   kesintisiz kümesizleştirme) etkiyi ancak kısmen giderir (N0 1500'de z ≈ −4 kalıyordu). §C4 etkiyi ortadan
   kaldırmaz, yönünü tutucu tarafta tutar ve kalibrasyondan ayırır. Bedeli güçtür (§C7).
3. **Kenar sınırı yapay dünyaya dayanır.** Etkinin büyüklüğü gerçek kümelenmeye, Mc_kul'a ve lob geometrisine
   bağlıdır. Yapay dünyanın lob içi kümelenmesi zayıftır. Kural tek bir sayıya (kapı N0 500) bağlanır; 500'ün hemen
   altındaki bir kümede kalan kayma −0,013 ((i)) ile −0,020 ((ii)) arasıdır (hat P(D) − kesin, §C6); bu toleransın sınırındadır.
4. **Risk 6 (TR-6a kod incelemesi) sınanmadı.** Lobdaki ana şok artçıları ve büyük artçıların GK pencereleri gerçek
   son pencereyi boşaltabilir (H1 lehine). Sahte zamanlarda büyük ana şok olmadığından p̂₀ bunu soğurmaz. Korumalar
   S7, S1 ve D4'tür. Bu yanlılık kenar etkisinin tersi yöndedir; ikisinin toplamı bilinmez.
5. **(d)'nin oy oranı bedeli.** Yapay dünyada Mc_kul = Mc_lob + 0,2'dir; oyun gördüğü oran kapı oranının %63'üdür.
   Kapıyı sınırda geçen bir lobda kalıcı −10 kPa'da düşüş oyu olasılığı 0,987'den (TR-6a §4.5, 335 g, ΔMc 0) 0,940'a
   iner (§C3, C2). Gerçek veride ΔMc daha büyük olabilir (TR-6a §6.2 kural 6, etkin N0 cümlesi).
6. **Bağlayıcı sınama uzun sürer** (≈ 18 saat CPU). Parçalı ve belirlenimci yapıldı; kesinti sonucu değiştirmez.
7. **Kenar kümelerinin artış oyu sıfırlanır.** Bu, ters yön notunu ve S2'nin artış yönünü tutucu yapar; o kümelerde
   gerçek bir artış görülemez.
8. **Kalibrasyondan çıkarılan sahte oylar J'yi düşürür.** Önsayımda Tokachi-oki'nin 3 geçerli sahte zamanı vardır;
   kural J'yi 64'ten 61'e indirir (Tohoku'nun zaten yoktur). J < 30 dalı daha olası değildir.

## C10. Kod, sınamalar ve yeniden üretim

Kod kopyalanmadı. TR-6c, `tr6a_kosu.py` ve `tr6a_yapay.py` içinde `--tasarim c` seçeneğidir:
- `tr6a_kosu.py`: `tasarim_sec("c")` dosya yollarını `tr6c_*`'ye, tamlık kuralını `("yedek_d",)`'ye çevirir;
  `onkayit_uyusmuyor()` TR-6c'de TR-6a gövdesini de denetler ve TASLAK'ta durur; `Analiz.kenar_birimleri`,
  `Analiz._kenar_A` ve `manifest` içindeki kalibrasyon süzgeci §C4'ü uygular (yalnız `TASARIM == "c"` iken);
  `N0_UST_C = 500.0`; `sinama --prova | --baglayici | --gelistirme`, `--hucreler`, `--parca-dizini`, `--yaz`.
- `tr6a_yapay.py`: `TekBirimSinama(kural=…)`, `deneme(…, ham=True)` (kümesizleştirmesiz eşli oylar ve (d)'nin veri
  yok dalı), `hucre_parcasi_c`, `hucre_ozeti_c`, `hucre_kos_c`, `prova_c`, `baglayici_sinamalar_c`,
  `tamlik_prova_c`, `kesin_c`, `dtau_kesin_c`, `guc_kaybi_c`, `ters_yon_alfa_c`, `tohum_denetle_c`.
- `Analiz.kapi_degerleri` yalnız tek birim provasında (`yalniz_golge`) gölge dışı lobların kapısını atlar; gölge
  sayıları aynıdır.

**TR-6a bit düzeyinde korunur.** Varsayılan tasarım "a"dır. Değişiklikten önceki HEAD kodu ile yeni kod aynı sabit
tohumlarla koşuldu: çok birimli yapay dünyada manifest + oylar + hüküm, yapay katalog sınaması (tohum 77, n 40), tek
birim deneme dizisi ve bir tamlık hücresi bayt bayt aynı çıktıyı verdi. Bu dört özet `tr6a_test_yapay.py`
`TTasarimC.test_tr6a_bit_duzeyi` içinde sabittir.

**Sınamalar:** `python3 -I -B kayit/turetme/tr6/tr6a_test_yapay.py` → 62 sınama, hepsi geçti (≈ 2 dakika). Yeni `TTasarimC` sınıfı (8 sınama):
TR-6a bit düzeyi; `--tasarim c` yolları ve TASLAK durdurması; tohum yasakları; parça belirlenimciliği ve (d) penceresi;
ölçüt aritmetiği (C1 ve C1′); kesin değerler (`kesin_c`, `dtau_kesin_c` ile 200 000 denemelik Monte Carlo); güç ve
ters yön hesabı; kenar kuralı (kenar kümesi K'de kalır, sahte oyları J'ye girmez, ana ve gölge türevi satırlarda A = 0,
S1 ve S7 değişmez; sınır sonsuza çekilince sınama yakalar; TR-6a kipinde kural yoktur).

Yeniden üretim (deponun kökünde):

```
python3 -I -B kayit/turetme/tr6/tr6a_test_yapay.py
python3 -I -B kayit/turetme/tr6/tr6a_kosu.py --tasarim c sinama --prova --tohum 7311 --deneme 20000 \
    --parca-dizini <geçici_dizin> --yaz            # ≈ 18 saat CPU; --hucreler ile hücre hücre
# tamlık provası: python3 -I -B -c "import sys; sys.path.insert(0,'kayit/turetme/tr6'); import tr6a_yapay as Y; Y.tamlik_prova_c(7312, 20000)"
# §C5 / §C7 tabloları: tr6a_yapay.prova_bilgi_c('kayit/turetme/tr6', h1_bilgi) → tr6c_prova_bilgi.json
```
