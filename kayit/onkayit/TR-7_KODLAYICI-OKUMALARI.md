# TR-7 kodlayıcı okumaları (12 Kasım 2026, veri öncesi)

Kodlayıcının, dondurulmuş ön kaydı (sürüm 3, sha256 df426ffc59793dcb75e5167aca643145d3bd55be3bb4bdcce11f58e1ea544c20,
dondurma notu dahil) `kayit/turetme/tr7/tr7_cekirdek.py`, `tr7_indir.py`, `tr7_kosu.py` ile uygularken yaptığı
okumalar. Hiçbir Marmara ya da Parkfield dalga formu ve hiçbir gerçek StationXML indirilmeden ya da açılmadan yazıldı;
kod yalnız yapay veriyle (`tr7_test_yapay.py`, KD) sınandı. Metin değiştirilmedi. Belirsiz yerlerde en dar ve en tutucu
okuma uygulandı. Kod incelemesi her birini denetler. Kök oturum kaydı "Ek 1" olarak bu dosyaya ekler.

Numaralar koddaki "okuma O-n" göndermeleriyle aynıdır.

## Zarf zinciri (§6.2)

1. **O-1** Bağlayıcı sıra: sürüm 3 > İNCELEME-2 düzeltme metinleri > İNCELEME-1 > SAYIM. Kod yalnız sürüm 3'ün metnini
   uygular; inceleme metinlerine yalnız sürüm 3 sustuğunda başvuruldu (aşağıda yok).
2. **O-2** Hilbert numpy ile (`scipy.signal.hilbert` ile birebir; sınandı). Bant geçiren süzgeç §6.2.3'ün adını verdiği
   obspy `bandpass, corners=4, zerophase=True` (görev metni obspy'yi okuma, yanıt ve seyahat süresiyle sınırlıyordu;
   bağlayıcı metin obspy süzgecini adıyla istediği için metin izlendi).
3. **O-3** Ortalama ve doğrusal eğilim en küçük kareler doğrusuyla (obspy `detrend('demean')` + `detrend('linear')` ile
   birebir; sınandı).
4. **O-4** 1 sn kutusu yalnız bütünüyle örneklerle örtülüyse tanımlıdır; parçanın kenar kırpmasından (10 sn) sonra kısmen
   örtülen ilk ve son kutu kayıtsızdır (NaN).
5. **O-5** Yatay bileşenler yalnız ikisi de varsa, ikisinin de yanıtı varsa ve R ile W örtüleri ikisinde de ≥ %90 ise
   kullanılır; yoksa C yalnız Z'dir. Kullanılan bileşenlerden birinin kayıtsız olduğu saniye C'de kayıtsızdır.
6. **O-6** Algılama, MDA dahil, hep float32'ye yuvarlanmış zarfla yapılır (zarf deposu float32).
7. **O-7** Örtü: [a, b) içindeki tam saniyelerden, bir parçanın örneklerinin [k, k+1)'i bütünüyle örttüğü saniyelerin payı.
   Kanal birleştirme obspy `merge(method=1)` + `split` (O-19).
8. **O-8** σ = 0 olan istasyon (yapay olmayan veride pratikte olmaz) o pencerede aşım üretmez, kayıtlarda işaretlenir; 12
   sınırındaki yeri bir sonraki adaya verilmez ve K0-tam'ı değiştirmez (zarf görülmeden bilinemez). **Riskli: "düşer"in
   yerine istasyon alma okuması da savunulabilir.**
9. **O-9** Küme aralığı I'nın kesiştiği "W", (pencere, segment)'in kullanılan istasyonlarının W'lerinin zarfıdır
   (en erken W başı – en geç W sonu; Wb). MDA başlangıcı da Wb başına görelidir, |W| = |Wb| (O-65).
10. **O-10** Darbe kuralında kayıtsız (NaN) saniye "C ≤ c_p/8" ya da "C ≤ c_p/2" şartını sağlamaz.
11. **O-11** 3a'nın W′_son'u için "kayıtlı" = L tanımlı (5 sn yumuşatmanın NaN yaydığı saniyeler kayıtsız).
12. **O-12** [a, b) maske aralığının eksen saniyesi k'yi maskelemesi: floor(a) ≤ k < ceil(b) (D12c referansıyla aynı).
13. **O-13** Büyüklüğü olmayan katalog kaydı hiçbir maske şartını sağlamaz.
14. **O-18** Sayısallaştırıcı bit sayısı yalnız StationXML DataLogger alanlarında açıkça yazılıysa ("24-bit" gibi)
    okunur; yoksa "bilinmiyor" (b = 24, eşik 10⁶).
15. **O-19** Örnekleme hızı penceresi içinde değişen kanal ("kanal: örnekleme hızı değişken") istasyonu düşürür.
16. **O-20** Uzun periyot yolu kesintisiz parça başına (remove_response + 0,02–0,1 Hz), tam saniyelerde doğrusal ara
    değerle örneklenir; süzgeç geçişinin parça kenarlarında yarattığı bölüm ayrıca atılmaz. **Riskli: boşluğa yakın PGV.**
17. **O-21** Kırpılma, kullanılan her bileşenin W içindeki ham sayımında denetlenir; biri kırpılmışsa istasyon düşer.
18. **O-22** Eksen dizinleri: R saniyeleri [⌈R başı⌉, ⌊R sonu⌋), W saniyeleri [yuvarla(W başı), yuvarla(W sonu)).

## Algılama, maske, ayıklama (§6.3–§6.5)

19. **O-33** Ayıklama nedeni "maske" (§6.5.4, bilgi): maskesiz kurulumda tutarlı olup maskeli saniyelerle kesişen ve maskeli
    kurulumda I′ örtüşen karşılığı olmayan küme sayısı.
20. **O-12a** Negatif pencerelerin E1 olayları manifestteki ComCat yanıtından (M ≥ 6,0, [R başı − 3 sa, W sonu], küresel),
    segment orta noktasına iasp91 varışlarıyla; ikiz kuralı kaydırılmış T0'a uygulanır.
21. **O-62** Katalog yanıtı: EMSC 204 = boş; ComCat boş csv = boş. Servis hatası ya da ayrıştırılamayan katalog koşuyu
    durdurur (sorgular bir kez ve eksiksiz yapılmalı, §6.5.1).

## Modülasyon, τ_ölç, kestirici (§6.4, §6.6, §7.5)

22. **O-14** φ_c için kayıtsız v saniyesi 0 ile doldurulur; L_k'da maskeli ve kayıtsız saniyeler Pearson'dan çıkarılır.
23. **O-15** Dairesel kaydırma `rng.integers(120, |W| − 120)` (üst uç dışlayıcı; referans betiklerle aynı).
24. **O-38** Modülasyon üreteci (`default_rng(20261112 + 3)`) bağlam başına yeniden kurulur: K1 (Tohoku penceresi) ve
    Marmara ayrı. Marmara'da sıra: birim (ana şok T0) → segment S1…S7 → pencere zamanı → küme I′ başı; Kahramanmaraş ve
    S4–S7 dahil bütün sağ kalan kümeler. Bütün algılamalardan sonra hesaplanır.
25. **O-50** Uzun periyot başvuru istasyonu: pencerenin bütün istasyonlarından (12 sınırı dışı, segmentten bağımsız)
    PGV'ye uygun ve örtüden geçen, segment orta noktasına en yakın olan; eşitlikte ağ ve istasyon adı alfabetik.
26. **O-51** L_k ile ölçü I ∩ (başvuru istasyonunun W'si) üzerinde; < 3 sn kalırsa ya da yatay ve düşey v yoksa
    "ölçülemedi". Yalnız Z varsa yalnız Z bileşeniyle.
27. **O-49** τ_ölç penceresi: segment listesindeki (12 sınırı dışı) PGV'ye uygun ve örtüden geçen istasyonların PGV'lerinin
    medyanı. Birimin τ_ölç'ü pencerelerinin en büyüğü (kaba τ kuralının eşi); ölçülemeyen birim n_ölç'te "≥ 2 kPa değil"
    sayılır.
28. **O-17** Kestiricide maskeli ve kayıtsız saniyeler ⟨C²⟩_I′ ve ⟨C²⟩_R'den çıkarılır; A_PK, K1 kümelerinin en büyüğü.

## MDA (§7.4)

29. **O-16** 20'den az denemede A50 de A90 da "belirsiz" yazılır (metin yalnız A90 der).
30. **O-44** Tek MDA üreteci `default_rng(20261112 + 2)`: K1-negatif'te başlar; her (pencere, segment) satırından sonraki
    durumu `tr7_mda.jsonl`'e yazılır ve Marmara-negatif bu durumdan sürer (aynı çekiliş dizisi). Marmara sırası:
    segment S1…S7 → ana birimler T0 sırasıyla → `sira`. Kahramanmaraş negatifleri algılanır (bilgi K2), çekiliş almaz.
31. **O-37** Wharton biriminin negatif penceresi (iki alt pencere, algılama yok) tek deneme alır; deneme o segmentte
    taranmış en erken alt pencereye (ana şokunkine) eklenir.
32. **O-46** 1/2 kanallarda N bileşenine birinci, E'ye ikinci yatay kanalın yanıtı uygulanır (döndürme sonrası yaklaşık).
33. **O-47** Enjeksiyon için ham veri yeniden okunur: verinin analitik sinyali yalnız Wb ± 5 sn'de tutulur; yapay sinyal
    bileşenin ilk parçasından son parçasına kesintisiz ızgarada üretilir, yanıtla çarpılır, parçalara bölünür ve zincirden
    geçer. R'ye ekleme yapılmaz.
34. **O-45** Marmara-negatif'te çekiliş sırası segment-önce olduğundan, MDA gerektiren negatif pencerelerin ham verisi
    aşamanın sonuna dek zarf deposunun yanında (`/mnt/project-files/turetme/tr7-zarf/ham/`) tutulur; gerekmeyenlerinki
    algılamadan hemen sonra silinir. **Riskli: tepe disk kullanımı (aşağıda).**

## K1 (§7.2)

35. **O-35** K1 aralığının iki ucu da dahil: epoch'ta [06:16:01, 06:31:49); I′ = [a, b) bununla kesişirse "kesişir".
36. **O-40** (c)'nin "algılama yoksa"sı Tohoku penceresinde hiçbir sağ kalan küme olmamasıdır; K1 aralığı dışında
    algılama varsa dal (d).
37. **O-41** (b′)(i) birleştirilmemiş tek tek E1 aralıklarının bitişleriyle; (ii) iz köşe ortalamasında, Tohoku
    derinliği `tr7_tetikleyici.csv`'den (29 km; dosyanın sha256'sı §3'te). taup'ta olmayan faz atlanır.
38. **O-42** "Ayırt edici değil" yalnız (b)/(b′) dallarında yazılır. Parkfield modülasyonu yalnız K1 aralığıyla kesişen
    kümelerde hesaplanır.

## K0-tam, K2, hüküm (§4.2, §7.3, §8)

39. **O-34** K0-tam ×3 sütunu yalnız listedeki birimlerden sayılır (alt sınır); önsayımın ×3'ünden S2 ve S7'de birer
    birim (us20003k7a, listede yok) ve yuvarlamayla 0,01 kPa farklıdır. ×1 ve ×1/3 önsayımı birebir yeniden üretir (sınandı).
40. **O-36** Marmara negatif pencereleri yalnız K0-tam'da o segmentte taranan birimler için işlenir; Wharton alt
    penceresi, karşılık gelen tetikleyici penceresi o segmentte taranmışsa.
41. **O-48** n_açık: birimin o segmentteki bütün liste pencereleri taranmış ve her birinin W maskeli payı ≤ 0,50 ise
    (dondurma notu: Wharton'da iki pencere). Pay, kullanılan (≤ 12) istasyonların W birleşimi üzerinden.
42. **O-52** Sıra 5'in "uzun periyot başvuru istasyonu var" şartı: algılama veren pencerelerden en az birinde başvuru
    istasyonu vardı.
43. **O-53** VAR'daki "kaba τ ≥" algılayan (X_alg) birimlerin en küçük kaba τ'su; "ölçülen τ ≥" algılayan birimlerin
    ölçülmüş τ_ölç'lerinin en küçüğü, yoksa "(ölçülen τ ölçülemedi)".
44. **O-54** Kalıp doldurma: "= [..]" ile biten simgeler (n·f/N, P(Bin(n, p_üst) ≥ X_alg), A90, A50, A90_PK) etiket
    olarak kalır; öteki değişkenler (n, X_mod, n_açık) sayıyla değişir, ekleri metindeki gibi kalır ("3'unda", "7'ının").
    "[bant zayıfsa: 'zayıf bant'.]" → " Zayıf bant." Sayısal olmayan A90'da "nm/s" yazılmaz; A50 metindeki gibi birimsiz.
    Biçim: τ 2 ondalık, olasılık 3 ondalık, A 3 anlamlı basamak (≥ 1000'de onluğa yuvarlanır: 1259 → 1260), ondalık virgül.
    "(K1 yalnız belirsiz geçti)" ve "(segment düzeyi α …)" cümlenin son noktasından önce eklenir.
45. **O-55** Aday kalıbının "sağlanmayan" listesi sabit ifadelerdir: "X_min yok"; "X_mod ≥ X_min(n, f) (X_mod = a,
    X_min = b)"; "Parkfield modülasyonu geçmedi (modülasyon ölçüsü pozitif kontrolde doğrulanmadı)"; "K1 ayırt edici
    değil"; "K1 yalnız belirsiz geçti"; "uzun periyot başvuru istasyonu yok".
46. **O-56** S5/S6: hüküm satırı 2009 sonrası birimlerle (n, N, f, X'ler ve MDA denemeleri yalnız onlardan); bütün
    birimlerle aynı hesap "Yöntem karşılaştırması, bağımsız değil" satırı olarak.
47. **O-57** K1 kalırsa (a/c/d) Marmara verisi indirilmediği için ×1/3 ve ×3 satırları önsayımdan yazılır ve öyle işaretlenir.

## İndirme, hata payları, aşama mekanizması (§3.5, §6.1, §10)

48. **O-26** Planlı istek sayısı (servis payının paydası) manifestin ilk istek kümesidir: her segmentte ilk 12, tetikleyici
    pencerelerinde PGV'ye uygun bütün istasyonlar, Parkfield'da BK.PKD. Yerine alınan adaylar paydaya girmez (tutucu).
49. **O-27** Pay, istasyon-pencere başına son durumla hesaplanır. Yeniden deneme turu yalnız servis hatalı olanları ister.
50. **O-28** Biçim payı aşamanın bütün indirmeleri bittikten sonra, hiçbir algılamadan önce bir kez denetlenir (pencere
    başına denetim sürdürmede kilitlenirdi). **O-29** Bu yüzden algılama aşamalarında önce bütün pencereler indirilir.
51. **O-30** Kod commit/push yapmaz: `baslat` durum dosyasına aşamayı yazar ve durur; `kos` önce `git` ile durum dosyasının
    izlendiğini, HEAD ile aynı olduğunu, HEAD'de aşamayı "başladı" gösterdiğini ve HEAD'in uzak dalda olduğunu
    (`ls-remote` + `merge-base --is-ancestor`) doğrular.
52. **O-31** KD referans betiklerinden `tr7_onkayit_yapay.py` ve `tr7_onkayit_denetim2.py`'nin sha256'sı metinde yok;
    depodaki hâlleri kodda sabitlendi.
53. **O-32** Girdi denetimi §3'te sha256'sı yazılı depo içi dosyaların hepsini kapsar (`tr7_tetikleyici.csv`,
    `tr7_varlik.csv`, `tr7_varlik_ozet.json`, `tr7_parkfield_varlik_ozet.json` dahil). Depo dışı `comcat_m75.csv` koşu
    kodunca okunmaz.
54. **O-63** Parkfield StationXML ve dalga formu: NCEDC, 204/404 dönerse EarthScope.
55. **O-66** Kısıtlı (401/403) ya da yok (204/404) dönen istasyon örtüden düşen gibi sayılır; o segmentte 12'ye
    ulaşılmadıysa sıradaki aday istenir.

## KD (§7.1)

56. **O-23** KD pencereleri: 600 sn ön ve 620 sn arka dolgu (zincirin parça kenarı kırpması dolguya düşer).
57. **O-24** D8: 5 Hz sinüste ölçülen RMS = medyan(C)/√2; PGV, bilinen PAZ'lı (120 sn) 20 sn sinüsle.
58. **O-25** D12'nin "maskesiz algılanır"ı ≥ 0,95 olarak denetlenir.
59. **O-39** D9: Δ istasyon ve dış merkez koordinatlarından yeniden hesaplanır (listedeki `uzaklik_km` 0,1 km'ye yuvarlı;
    onunla en büyük fark 1,001 sn çıkıyordu, koordinatlarla 0,997 sn).

## Kod incelemesi için riskli yerler

- O-8 (σ = 0 istasyonu yerine aday alınmaz), O-20 (LP yolunda kenar geçişi), O-45 (ham verinin Marmara-negatif sonuna dek
  tutulması: tepe ≈ negatif pencerelerin ham hacmi, kestirim 8–11 GB, `/mnt/project-files` rclone bağlamasında; bağlamanın
  yerel önbelleği yerel diski doldurabilir).
- **Tam KD'nin süresi ≈ 20 saat (4 çekirdek).** Pencere başına ≈ 25–50 sn'nin çoğu obspy `bandpass`'in (sosfilt) 100 Hz ×
  6720 sn × 3 bileşen × 2 bant üzerindeki maliyeti; metin 100 Hz ve Butterworth'u bağladığı için kısaltılmadı. Bu oturumda
  tam KD koşulmadı; her KD işi bir pencereyle koşuldu (hata yok), seçili işler orta ölçekte koşuldu (rapor).
- **D6 ×100 sınırda olabilir.** 12 pencerelik ara denemede 0,917 (bant ≥ 0,95): algılanan 5 kümeden birinde 3
  istasyonun 2'sinde tepe başlangıçtan bir saniye sonra düştü ve önceki saniyenin süzgeç öncülü c_p/8'i aştı. Koşu
  zinciri (obspy `bandpass corners=4`, bant dönüşümlü Butterworth) başlangıçtan önceki saniyede tepe oranının medyanını
  0,12 verir; referans betiğin FFT |H|² yaklaşımı (yüksek ve alçak geçirenin çarpımı) 0,09 verir. Fark kodun değil
  referansla metnin süzgeci arasındadır; tam KD karar verir (kalırsa §7.1 "koşu öncesi ek" yolu).
- **MDA süresi.** Gerçek ölçekte deneme başına kaba kestirim 1–3 dk (12 istasyon × 3 bileşen × 101 basamak); ≈ 570 deneme
  sırayla (üreteç sırası) ≈ 10–30 saat tek çekirdek. Üreteç durumları önceden benzetilerek koşutlanabilir; yapılmadı.
- `mda_deneme` her A basamağında bütün istasyonların L'sini ve kümelerini yeniden kurar (doğru ama yavaş; KD'nin süresinin
  çoğu D13/D14 ve modülasyon işleri).
- Modülasyon üretecinin bağlam başına yeniden kurulması (O-38) ve MDA üretecinin aşamalar arası taşınması (O-44).
- Kalıp doldurma politikası (O-54) ve aday listesi ifadeleri (O-55): metin "yalnız bu biçimlerde" der; D11 bunları elle
  yazılmış beklenen cümlelerle karşılaştırır, ama beklenen cümleler de kodlayıcınındır.
- Uçtan uca prova yalnız tek segmentte (S2) ve 2 birimle; Wharton iki-pencere kuralları, S5/S6 bağımsız satırı ve
  Kahramanmaraş bilgi satırları uçtan uca yolda koşmadı (birim düzeyinde K0 ve D11 ile sınandı).
