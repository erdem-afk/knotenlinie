# TR-7c koşu dondurması eki: TASLAK

Durum: TASLAK. Bu dosya koşu dondurmasının işareti değildir; dondurma satırını koordinatör ana ön kayda
(`TR-7c_tetiklenmis-tremor_ONKAYIT.md`) yazar. Karar metnine dokunulmadı.

Tarih: 18 Kasım 2026. Dayanaklar:
- `TR-7c_KOD-INCELEME.md` (DÜZELTMEYLE KABUL; §D, §F, §G, §I);
- `TR-7c_KODLAYICI-OKUMALARI.md` §11;
- `kayit/turetme/TASIMA-2026-11-17.md`.

**Kapı için önemli.** Kapı (`kosu_dondurulmus_mu`) yalnız ana ön kayıt dosyasını okur. Bu ekte yazılı iki kod sha256'sının
(§5) kapının gördüğü metne girmesi için ikisinden biri yapılmalıdır:
- ek, ana dosyanın sonuna (§7 başlığından sonra; §0–§6 gövdesi değişmeden) eklenir;
- ya da iki sha256 "Durum:" satırına tam (64 karakter) yazılır.

Bu ek ayrı dosyada kaldıkça kapı kapalı kalır.

## 1. Kod incelemesi §D: KMS-1…KMS-10 ek cümleleri (aynen)

Kaynak: `TR-7c_KOD-INCELEME.md` §D. Tırnak içindeki metin değiştirilmeden alındı; başlıklar yalnız etikettir.

**KMS-1 (belirteç).**
> "Koşu dondurmasının belirteci, metnin 'Durum:' satırında geçen 'KOŞU DONDURULDU' dizesidir; §10 madde 5'teki
> 'Durum: DONDURULDU …' bu dize olarak okunur. Koşu kodu gerçek kipte ancak şunların hepsi sağlanınca çalışır: bu dize
> 'Durum:' satırında; §0–§6 gövdesinin sha256'sı 8761573150be97dca99590283d7e3cecc3ddf0067804945966773f5276f69f18;
> `tr7c_kosu.py` ve `tr7c_mde_ek.py`'nin bu ekte yazılı sha256'ları; D-2'nin üç dosyası; repo girdileri
> (`tr7b_sayim.json`, `ustveri/tr7c_ustveri.json`, `tr7_parkfield_liste.csv`, `inc1/tr7c_inc1.json`,
> `tr7c_mde_ek.json`); TR-7 motoru `tr7_kosu.py` (ce439a4797fd1992ddd68de734ee842b146bd6f13155ba6151769bceb26a9005) ve
> `tr7_indir.py` (0763f46da14b2a12f5268937dc6e479dbfd1bc54c3c3ba93d700914dc4b91f2f)."

**KMS-2 (modülasyon üreteç sırası).**
> "Parkfield modülasyon ölçüsünün üreteci `default_rng(20261112 + 3)` tek bir örnektir ve 39 birimin (10 P olayı, 29 N
> birimi) algılama satırları yazıldıktan sonra bir kez kurulur. Algılama kümeleri (ayıklamadan sağ çıkan ve K1b
> aralığıyla kesişen kümeler) birimler T0 sırasıyla, P ve N iç içe (Vanuatu 2009 birimi N 27'nin T0'ıyla), birim içinde
> I′ başı ve eşitlikte I′ sonu sırasıyla işlenir. Bilgi birimleri (Kunlun 2001, Tonga 2006) ve rastgele negatif
> pencereler akışa girmez. Başvuru kanalı olmayan ya da M'si hesaplanamayan küme üreteçten sayı çekmez. Her küme 1000
> dairesel kaydırma kullanır; kaydırma `integers(120, |W_başvuru| − 120)`'dir (TR-7 §6.4). Bu sıra sonuç görüldükten
> sonra değiştirilmez."

**KMS-3 (modülasyonun zamanı).**
> "Modülasyon ölçüsü K1c-algılama aşamasında, 29 N biriminin ve 10 P olayının algılama satırları yazıldıktan sonra ve
> Z3/Z4'ten önce hesaplanır; ara sonuç dosyaya yazılmaz, yalnız hüküm dosyasında yer alır."

**KMS-4 (Q'nun bitişi).**
> "K5'in Q aralığı bir penceredeki bütün istasyonlar için aynıdır: Q = [⌊T0 + t_P⌋, Wb başı); t_P iz köşe
> ortalamasında (35,9125° K, 120,4625° B) iasp91 ile, ComCat tetikleyici kaydının derinliğinde en erken P fazıdır; Wb
> başı kullanılan (12 sınırından sonraki) istasyonların W başlarının en erkenidir. Maskeli ve kayıtsız saniyeler
> `_k1_kalinti`'nin kendi kuralıyla düşer. Rastgele negatif pencerelerde aynı tanım, kaydırılmış T0 ile kullanılır."

**KMS-5 (X_min ve K2).**
> "Z3 (i)'deki X_min(n_P, f_PK), TR-7 §8'in binom tanımıdır: p_üst = f_PK/N_PK'nin Clopper–Pearson tek yanlı %95 üst
> sınırı, X_min = P(Bin(n_P, p_üst) ≥ X) ≤ 0,05 olan en küçük X ∈ [2, n_P]; yoksa (i) sağlanmaz. TR-7'nin Marmara
> tarafındaki K2 kapısı K1c'de uygulanmaz; K1c'nin FAR şartı Z3 (ii)'dir. Bu, INCELEME-1 güç ızgarasının ve §7
> tablolarının tanımıdır."

**KMS-6 (D-9'da "ölçülemeyen").**
> "D-9'daki 'modülasyonu ölçülemeyen olay', dört olaydan §5 madde 4'ün ölçülebilirlik tanımını sağlamayanlardır:
> taranmayan, K1b ile kesişen ve ayıklamadan sağ çıkan kümesi olmayan, E-1 başvuru kanalı olmayan ya da M'si
> hesaplanamayan olay. Sayı K1c satırına, her olayın nedeni hüküm dosyasına yazılır. Ne sayı ne neden etiketi ya da dalı
> değiştirir; etiketi yalnız p ≤ 0,01 veren bir küme tetikler."

**KMS-7 (N 27/N 28 ayrı bilgi satırı).**
> "D-1'in bilgi satırı ('iki olay ayrı sayılarak hesaplanan Z3 (iii)') bu koşuda hesaplanmaz, çünkü N 27 ve N 28 için
> ayrı K1b, W ve E1 tanımı koşudan önce dondurulmadı; sonuç raporunda 'hesaplanmadı (ayrı pencere tanımı yok)' diye
> anılır ve sonradan hesaplanmaz. Dal değişmez."

**KMS-8 (uygulama hatası yolu).**
> "TR-7 §7.2'nin uygulama hatası yolu bu koşu kodunda yazılmadı. K1c (d) ya da (e) dalından sonra bir uygulama hatası
> bulunursa ilk hüküm dosyası silinmez ve üzerine yazılmaz; düzeltme ayrı bir bağımsız kod incelemesinden geçer;
> ikinci hüküm ayrı adla (`tr7c_k1c_hukum_2.json`) bir kez yazılır ve iki hüküm birlikte yayımlanır. Yol bir kez
> kullanılır; (a), (b) ve (c) dallarında yoktur. Tanım, eşik, pencere, liste, sızıntı kuralı, üreteç sırası ve
> E-2'nin örtü eksikliği 'uygulama hatası' sayılmaz."

**KMS-9 (KD'de Q).**
> "§10 adım 2'deki 'TR-7'nin KD'si K5 ile', KD pencerelerinde tetikleyici olmadığı için Q = ∅ ile koşulur; K5'in
> kalıntı kolu orada çalışmaz, yalnız ρ kolu çalışır. K5'in Q doğrulu kalıntı kolu TR-7b §11.2 satırlarıyla (iki tohum,
> 38/38 Tur 2 ile birebir) sınanmış sayılır. KD satırları bu koşu kodunun `ayikla_k5`'iyle tam ölçekte koşuldu
> (`kodinc/tr7c_kodinc_kd.json`)."

**KMS-10 (kuyu sınıfı bilgi satırı).**
> "Z4'ün 'liste sınıfına karşı kuyu sınıfı' bilgi satırı bu koşuda hesaplanmaz: kuyu sınıfı için pencere, indirme ve
> kod koşudan önce dondurulmadı. Sonuç raporunda 'hesaplanmadı' diye anılır. Hesaplanacaksa yalnız K1c hüküm dosyası
> yazıldıktan sonra, ayrı incelenmiş kodla ve yalnız bilgi olarak yapılır; hiçbir dalı ya da etiketi değiştirmez."


## 2. Kod incelemesi §I: ek cümleler (aynen)

Kaynak: `TR-7c_KOD-INCELEME.md` §I. Değiştirilmeden alındı.

1. (A23) "Durum dosyası `kayit/turetme/tr7c/kosu/TR7C_KOSU_DURUM.json`'dur; §10 madde 6'daki
   `kayit/turetme/tr7c/TR7C_KOSU_DURUM.json` bu yol olarak okunur. Durum dosyası yalnız 'başladı / tamamlandı / hata',
   zaman ve dosya sha256'larını taşır."
2. (§B.4) "Bir aşama kesilirse sürdürmeden önce durma nedeni (teknik çöküşün ileti metni ve saat) durum dosyasına
   elle ve commit ile yazılır; jsonl satırları ve üreteç durumu kaldığı yerden sürer. K1c-algılama aşamasından sonra
   koşu yalnız teknik çöküşle durur. Teknik çöküşü gidermek için yapılan kod değişikliği yalnız okuma/ayrıştırma
   katmanına dokunabilir, `TR-7c_KOD-INCELEME` biçiminde ayrıca incelenir ve sha256'sı deftere yazılır."
3. (A25) "Kunlun 2001 ve Tonga 2006 bilgi satırları E1 maskesi olmadan hesaplanır (USTVERI'de bu iki olayın E1 satırı
   yoktur); yalnız bilgi olarak yazılır ve hiçbir dalı ya da etiketi değiştirmez."
4. (Ö-i) "`_rho` eşit L değerlerine ortalama sıra yerine konum sırası verir; bu K5'in D-2 ile dondurulmuş davranışıdır
   ve değiştirilmez. Sürekli L'de Spearman ile farkı yoktur."
5. (§G) "İndirme planı TR-7 motorunun 12-istasyon kuralıyladır; istek sayısı ≈ 2000–2800 + E-1 istekleri
   kestirilir; koşu kodu kör olaylarda W, R ve aradaki Q dışında ve 2026 ve sonrasında hiçbir dalga formu istemez."

Kodlayıcı notları (cümleleri değiştirmez, yalnız kodun davranışını yazar):
- **Durum dosyası.** Aşama kayıtları yalnız `durum`, `zaman` ve `sha256` alanlarını taşır. Durum değerleri
  "başladı", "tamamlandı" ve "hata"dır. Dosyada ayrıca bir `durmalar` listesi vardır. Her durma kaydı aşamayı,
  türünü, ileti metnini ve saati taşır:
  - tür `kod`: aşamanın koşu kodu tarafından hata ile durdurulması;
  - tür `elle`: `durdu --neden`.

  Durma kayıtlarında sayı yazılmaz. Bu liste ek cümle 2'nin istediği durma nedeni kaydıdır.
- **Sürdürme.** Algılama aşamasında sürdürme ancak aşamanın son durumundan sonra yazılmış bir `elle` kayıtla olur
  (`baslat <aşama> --surdur`).
- **Ek cümle 5'teki "W, R ve aradaki Q".** İstek aralığı istasyon başına [R başı − 600 sn, W sonu + 600 sn]'dir. İki
  yandaki 600 sn Hilbert kenar dolgusudur (kod incelemesi §G ilk madde). Dolgu kör olayın kendi pencere tanımının
  parçasıdır, başka bir olaya uzanmaz.

## 3. Kod incelemesi §F: m_t bilgi cümlesi (aynen)

> "Bilgi (dal değiştirmez; Z7, D-3): Tohoku duman sınamasında K5'ten sağ çıkan 3 W kümesinin hiçbiri modülasyonda
> p ≤ 0,01 vermedi (en küçük p 0,083). Tek olaylık, tremor olduğu doğrulanmamış bu gözlem m_t'yi ölçmez, ama m_t 0,8
> varsayımını desteklemez (üç bağımsız kümede hiç geçmeme olasılığı m_t 0,8'de 0,008, m_t 0,5'te 0,13). Kör koşunun
> gücü bu yüzden m_t 0,5 sütunuyla okunmalıdır: görülebilir en küçük s ≈ 0,77; m_t 0,4'te ≈ 0,96; m_t ≤ 0,3'te s = 1
> bile 0,80 güç vermez. 'Ölçü sınanamadı (… kalan: (iv))' sonucu öncelikle modülasyon ölçüsünün gerçek tremorda düşük
> geçme olasılığının işareti olarak okunur; Parkfield'da tetiklenmiş tremorun yokluğu ya da algılayıcının tremoru
> görmediği diye okunmaz."

## 4. Yazarın sınav öncesi beklentisi (Ö-j): TASLAK, yazarın onayına

**Zamanlama beyanı.** Bu beyan Tohoku duman sınamasının sonucu (K5'ten sağ çıkan 3 W kümesi; modülasyonda hiçbiri
p ≤ 0,01 vermedi, en küçük p 0,083) ve m_f ölçümü (m_f = 0,025; Clopper–Pearson %95 üst sınırı 0,044) görüldükten
SONRA yazıldı. Kör Parkfield olaylarının (10 P, 29 N birimi) ve Marmara'nın hiçbir dalga formu görülmeden yazıldı.
Bu yüzden m_t'ye dair beklenti bağımsız değildir; §3'teki bilgi cümlesinden etkilenmiştir.

Taslağı kodlayıcı önerir. Yazar onaylar ya da değiştirir. Dondurma satırından önce yazılan değer geçerlidir; sonra
değişmez. Biçim TR-7 §11 ve TR-7b §10 biçimidir. Dallar karar metni §7'deki sıranın dallarıdır.

| Dal | Olasılık |
|---|---|
| (a) "ölçü sınanamadı (Parkfield verisi yok)" | 0,03 |
| (b) "ölçü sınandı" (etiketli ya da etiketsiz) | 0,30 |
| — bunun içinde D-10 "Parkfield modülasyonu geçmedi" etiketsiz | 0,10 |
| — bunun içinde D-10 etiketli | 0,20 |
| (c) "ölçü sınanamadı (algılayıcı … ayıramadı)"; çoğunlukla kalan (iv) | 0,40 |
| (d) "ölçü sınanamadı (kör Parkfield olaylarında … karşılamadı …)" | 0,15 |
| (e) "ölçü sınanamadı (yöntem)" ya da "(modülasyon ölçülemedi)" | 0,12 |
| Toplam | 1,00 |

Ek beklenti: (b) çıkarsa D-9 "genlik karıştırıcısı dışlanmadı" etiketinin de yazılma olasılığı ≈ 0,25.

Gerekçe (kısa):
- m_f 0,025 düşük. Z3 (ii) bu yüzden kolay sağlanır.
- Duman sonucu m_t'nin 0,5 ya da altında olduğunu düşündürür. Bu yüzden (iv) sık düşer ve (c) en olası daldır.
- Veri eksikliği (a) beklenmez: üstveri yoklamasında k = 10, n_P = 10, n_N = 29. Kuru prova S3, olayların bir
  kısmı boş kalsa da (b)/(c) dallarına ulaşıldığını gösterdi.

## 5. Son sha256 tablosu

Kapının denetlediği dosyalar (kapı yalnız ana ön kayıt dosyasını okur; iki kod sha256'sı oraya girmelidir):

| Dosya | sha256 | Kapıda |
|---|---|---|
| `kayit/turetme/tr7c/tr7c_kosu.py` | c86d8b9b17ae17e8fa67a12ff945a90df791dc0bfd6b548e1f2d3cbaac20a5b2 | ön kayıt metninde tam yazılı olmalı |
| `kayit/turetme/tr7c/tr7c_mde_ek.py` | 4876dcbee8ce455c221efa4782e4af0047e5ade2f7b84eb985f9eb127873e910 | ön kayıt metninde tam yazılı olmalı |
| `kayit/turetme/tr7b/tr7b_yapay2.py` (K5; D-2) | ae995ba8802a934577cbf26051229360bcfb1a85d5d4d7dc16d358dfeaef437f | koda gömülü |
| `kayit/turetme/tr7b/tr7b_yapay.py` (K5; D-2) | e92715318e21a0200b66e3c130853f73cbc382b0398aef561619fcbe1bb74374 | koda gömülü |
| `kayit/turetme/tr7/tr7_cekirdek.py` (K5; D-2) | 4a1b9131603d0f3d519cacb183fdbcccc106157b66392bf2d09350c9f49206f6 | koda gömülü |
| `kayit/turetme/tr7/tr7_kosu.py` (TR-7 motoru; K-2) | ce439a4797fd1992ddd68de734ee842b146bd6f13155ba6151769bceb26a9005 | koda gömülü |
| `kayit/turetme/tr7/tr7_indir.py` (TR-7 motoru; K-2) | 0763f46da14b2a12f5268937dc6e479dbfd1bc54c3c3ba93d700914dc4b91f2f | koda gömülü |
| `kayit/turetme/tr7b/tr7b_sayim.json` | 55318360214f96237802346d84a501e6c6964116906332362e704e3b0e5e5114 | koda gömülü |
| `kayit/turetme/tr7c/ustveri/tr7c_ustveri.json` | ed8cf3c63cc89609ed4bc865df788bc94c4f6fab40168f7985dd99d2d66ead8c | koda gömülü |
| `kayit/turetme/tr7/tr7_parkfield_liste.csv` | 9dca3380815196a8db15a8a5929441d38dd9b07fd7ed982845543e179957b2b8 | koda gömülü |
| `kayit/turetme/tr7c/inc1/tr7c_inc1.json` | 4974dbe66163b49ba8c1b7dab699121c45cdce5aa1fba53c0cb1b0791d912974 | koda gömülü |
| `kayit/turetme/tr7c/tr7c_mde_ek.json` | e759176ec28f0b4a9f18fed47bddfe1ed7f43a52fa24ed994c5d2a1d062c3b3d | koda gömülü |
| ön kayıt §0–§6 gövdesi ('\n## 0. ' → '\n## 7. ') | 8761573150be97dca99590283d7e3cecc3ddf0067804945966773f5276f69f18 | koda gömülü |

Kapıda olmayan, kayıt için dosyalar:

| Dosya | sha256 |
|---|---|
| `kayit/turetme/tr7c/tr7c_test_yapay.py` | 814732246f2b4422843f7ee6d8b87df1863f0046cc3be01cafcba968cc9de48b |
| `kayit/turetme/tr7c/tr7c_test_yapay.json` | (koşu sürüyor) |
| `kayit/turetme/tr7c/tr7c_prova.py` | bb573f3bc255ac4e1ce30388085e921f4a65e61341445e5116bc991b586e4ec7 |
| `kayit/turetme/tr7c/tr7c_prova.json` | 3daaf90ecc32fef7ccb77ee89e3dfeebee26ee6d12460b75ed1c946743d566e3 |
| `kayit/turetme/tr7c/kodinc/tr7c_kodinc.py` (değişmedi) | 03e479639222ba184a0dcd1b51a046ac2990da266fb35235378eb8ba31e31c06 |
| `kayit/turetme/tr7c/tr7c_kodinc_yeniden.json` (incelemeci takımının yeni kodda koşusu) | (koşu sürüyor) |
| `kayit/turetme/tr7c/tr7c_kd_k5.py` (değişmedi) | 77aeab9951972d7cc2580bd8e6fab95f8dc96dfa67218c8aea998b2076fc2a64 |
| `kayit/turetme/tr7c/kodinc/tr7c_kodinc_kd.py` (değişmedi) | ae3feb2f40314926642c1b81469256a1c02ea6d6026b60dd0160853294537d63 |
| `kayit/turetme/tr7c/kodinc/tr7c_kodinc_kd.json` | abd774cbcbe790b128cb2c0c3713e42095851a850db485349b73b83eca05ce99 |
| `kayit/turetme/tr7c/tr7c_mf.json` | 5c014eae0308288002d42b9b2245a5b85eed5c0cf0724d6748b0c8659f3c3fd7 |
| `kayit/turetme/tr7c/tr7c_duman.json` | 11aaa0a04ac4ce562e1f271a4ea20e0cbd334e3330a5f2b7e3d95270e085acb6 |
| `kayit/turetme/tr7c/tr7c_tr7b112_20261117.json` | 7e18100546b88267aa108e25d1b15f067c2fe2bcbe545296234a1b421d54a1af |
| `kayit/turetme/tr7c/tr7c_tr7b112_9393.json` | 52d3833f78c0f6d49b32d243fac840d6b5876f1b1a5b99e8951e108f09165ddf |

`tr7c_kosu.py`'nin önceki değerleri geçersizdir: 345dc176… (ilk teslim) ve b0f70642… (K-1…K-3 sonrası). c86d8b9b…
değeri §B.4 aşama protokolünü, kuru prova düğmesini, TR-7c'nin kendi isteklerinde `taban` geçişini ve P-1
düzeltmesini içerir. Algılama, K5, MDA ve modülasyon hesabı değişmedi. Tek değişiklik: modülasyon başvuru çıktısına
`konum` alanı eklendi; bu yalnız çıktıdır.

## 6. Sonuç özetleri

**Kodlayıcının sınamaları (`tr7c_test_yapay.py`, c86d8b9b… üzerinde).**
(Koşu sürüyor; sonuç bu taslağa eklenecek.)

**İncelemecinin takımı (`kodinc/tr7c_kodinc.py`, değiştirilmeden, c86d8b9b… üzerinde).**
(Koşu sürüyor; sonuç bu taslağa eklenecek.)

**KD (K5 ile).**
- İncelemecinin tam ölçek koşusu (b0f70642… üzerinde): 12/12 bant; eksik iş 0. K5 değerleri TR-7'nin K0 tam ölçek
  değerleriyle birebir aynı.
- Kodlayıcının 0,25 ölçek koşusu: aynı 5 satır; sonuç aynı.
- Ayrışma sayımı (ölçek 0,05): 1268 kümenin 0'ında K5 ile K0 ayrıştı.
- c86d8b9b… üzerinde yeniden koşulmadı. Gerekçe: aradaki değişiklikler algılama ve K5 kodunu değiştirmedi (git
  farkıyla doğrulandı).

**TR-7b §11.2 satırları.** İki tohumda 38/38, Tur 2 ile birebir (`tr7c_tr7b112_20261117.json`,
`tr7c_tr7b112_9393.json`).

**m_f.** 0,025; Clopper–Pearson %95 üst sınırı 0,044 (`tr7c_mf.json`).

**Tohoku duman sınaması.** K5'ten sağ çıkan 3 W kümesi; modülasyonda hiçbiri p ≤ 0,01 vermedi (en küçük p 0,083).
Bilgi satırıdır, dal değiştirmez (`tr7c_duman.json`; §3).

**Kuru prova (§B.3; `tr7c_prova.py`, `tr7c_prova.json`): 99/99.**

Gerçek G/Ç katmanı uçtan uca koşuldu: manifest → K1c-indirme → K1c-negatif → K1c-algılama. Sahte FDSN sunucusu
yalnız 127.0.0.1'deydi. Veri tamamen yapaydı: 20 Hz miniSEED ve StationXML; istasyon adları gerçek. Her senaryo
dört aşamanın hepsini `baslat` → `kos` protokolüyle koştu. Bütün parçalarda engellenen gerçek erişim 0'dı.

| Parça | Geçen | Sonuç |
|---|---|---|
| düğme | 15/15 | Gerçek kipte düğme kapalı; kapı açıkken prova reddedilir; 127.0.0.1 dışı URL, depo içi ya da /mnt dizini reddedilir; taban ve P-1 geri alma mutasyonları yakalanır |
| S1 (tremor var) | 25/25 | dal (b) "ölçü sınandı"; X_P 10/10, X_N 0/29, f_PK 1/10; M_mod 10; E-1 başvurusu BK.PKD HHZ 00, 3 bileşen (K-3: iki konumlu PKD'de 00 seçildi) |
| S2 (ayırt etmeyen) | 26/26 | dal (c), kalan (iii); "genlik karıştırıcısı dışlanmadı"; X_N 29/29 |
| S3 (eksik veri ve arızalar) | 33/33 | dal (b); n_P 9, n_N 27; k_koşu 6 < 10, güç notu 0,75/0,35; 204, 404, 429, zaman aşımı ve boş yanıtlar beklendiği gibi işlendi; iki kesme ve sürdürme; 4 durma kaydı (aşama başına kod + elle) |

Prova sırasında bulunan iki gerçek kusur kod incelemesinin bulgusu değildir; ikisi de c86d8b9b… içinde
düzeltildi:
- **P-1.** `katalog/` dizini yoktu. İlk ComCat yanıtı yazılamadı ve manifest ilk sorguda durdu. Gerçek koşu da
  durdurulurdu.
- **taban.** TR-7c'nin kendi istekleri `taban` almıyordu: ComCat tetikleyici ve M ≥ 6,5 sorguları, lp
  StationXML ve lp dataselect. Bu istekler provada gerçek sunuculara gidecekti; bekçi bunu yakaladı. Gerçek kipte
  `taban` None'dır; davranış değişmedi.

**Kapının sınama yolu ile gerçek yolu nasıl ayrılır.**
- Gerçek yol: `gercek_kapi` önce `kosu_dondurulmus_mu`'yu çağırır. Kapı kapalıysa `GercekKipReddedildi` yükseltir.
- Sınama yolu: yalnız `prova_ac(Prova(...))` bağlamında açılır. `gercek_kapi` her çağrıda `prova_denetle`'yi
  çağırır, sonra 'prova' döner; dondurmaya bakmaz. `prova_denetle` şunları ister:
  - kapı KAPALI olmalı; dondurulmuş metinle prova açılmaz;
  - her URL http://127.0.0.1:<port> olmalı; anahtarlar TR-7'nin SERVIS ve KATALOG anahtarlarıyla aynı olmalı;
  - çıktı dizinleri deponun, gerçek köklerin ve /mnt'nin dışında olmalı.
- Denetim kancası yalnız izinli (127.0.0.1, port) çiftlerine bağlantı açar. Bunun nedeni bulut kabının HTTPS
  vekilinin de 127.0.0.1'de olmasıdır.
- Prova kipi git doğrulamasını atlar, zaman aşımlarını ve bekleme sürelerini kısaltır.
- Hesap, eşikler, Ayar (mod_n 1000, MDA 3) ve aşama protokolü gerçek kipteki gibidir.
- Prova gerçek kip kapısını hiç açmadı. Kapının gerçek yolu (dondurma satırı ile sha denetimi) provada hiç
  sınanmadı; o yol yapay sınamaların kapı grubuyla sınanır.

## 7. İndirme planı ve koşu yeri

İndirme planı (kod incelemesi §G düzeltmesiyle; repo içi sayım, ağ yok):
- Dalga formu: ≈ 2000–2800 dataselect isteği, artı E-1 uzun dönem için ≈ 40–120 istek.
- Üstveri: ≈ 335 ComCat isteği ve ≈ 1950–2014 StationXML isteği. `lp_adaylari_manifest`, tetikleyici pencereleri
  başına liste istasyonlarında ≈ 1882 istek yapar; provada 2014 sayıldı.
- NCEDC'nin 204 döndürdüğü istasyon EarthScope'tan yeniden istenir. Eksik istasyonlarda istek sayısı bu yüzden iki
  katına çıkar.
- Hacim ≈ 2–4 GB. Süre: indirme ≈ 1,5–2,5 sa, MDA ≈ 6–7 sa (TR-7'nin 2–3 sn/istek ölçüsüyle).
- 7300 istek, 7–10 GB ve 11–14 sa üst sınırdır; plan bunu aşmaz.

Kör pencere kuralları:
- İstekler yalnız [R başı − 600 sn, W sonu + 600 sn] aralığındadır.
- Bitiş 2026-01-01'den öncedir.
- Marmara için hiçbir istek kurulmaz (O-30).

Koşu yeri: kiralık Hetzner makinesi `knotenlinie-turetme`. Yazılım: Python 3.13.18, numpy 2.5.3, scipy 1.18.1,
obspy 1.5.1. Ayrıntı: `kayit/turetme/TASIMA-2026-11-17.md`. Koşudan önce makinede şunlar sağlanmalı:
- `ZARF_KOK` (`/mnt/project-files/turetme/tr7c-zarf`) var ve `is` kullanıcısı yazabiliyor. Ham negatif mseed MDA
  bitene dek tutulur; birkaç GB gerekir.
- `git_dogrula` için upstream'i olan, push edebilen bir depo. Makinedeki depo git paketinden klonlandı. Bu yol
  provada sınanmadı (prova git doğrulamasını atlar).
- `pip freeze` bir alt süreçle koşar.
- **10 dakikalık cron bekçisi TR-7c aşamalarını yeniden başlatmamalı.** Bir aşama SIGKILL ile ölürse (ya da makine
  yeniden başlarsa), durum dosyasında aşama 'başladı' kalır ve durma kaydı yazılmaz. Bu durumda yeni bir `kos`
  kaldığı yerden sürer; elle durma kaydı istenmez. TR-7'nin `kos`'u da böyledir. Algılama aşamaları bu yüzden
  bekçisiz, elle koşulmalıdır. Kesilirse önce `durdu <aşama> --neden "..."`, commit + push, sonra `baslat <aşama>
  --surdur` yapılmalıdır. Kod bunu bu sürümde zorlamaz (§9).

Komut sırası (her aşama için):
1. `python3 -I -B kayit/turetme/tr7c/tr7c_kosu.py baslat <aşama>`, sonra commit + push.
2. `python3 -I -B kayit/turetme/tr7c/tr7c_kosu.py kos <aşama>`, sonra çıktılar ve durum dosyası commit + push.

Aşamalar sırasıyla: manifest → K1c-indirme → K1c-negatif → K1c-algılama.

## 8. Kapının aradığı "Durum:" satırı ve sha listesi

Kapı (`kosu_dondurulmus_mu`) ana ön kayıt dosyasında şunları denetler:
1. Dosyada "Durum:" ile başlayan İLK satırda `KOŞU DONDURULDU` dizesi geçer. Satır bugün 3. satırdır ve
   "Durum: KARAR METNİ DONDURULDU (…" ile başlar. Yeni dize bu satıra yazılmalı ya da bu satırdan önce yeni bir
   "Durum:" satırı olarak eklenmelidir.
2. §0–§6 gövdesinin sha256'sı 8761573150be97dca99590283d7e3cecc3ddf0067804945966773f5276f69f18'dir. Gövde,
   '\n## 0. ' ile '\n## 7. ' arasıdır. Dondurma satırı ve ek bu aralığın dışında kalmalıdır.
3. `tr7c_kosu.py` ve `tr7c_mde_ek.py`'nin sha256'ları metnin herhangi bir yerinde tam (64 onaltılık karakter)
   geçer.
4. Koda gömülü sha256'lar (§5'teki "koda gömülü" satırları) diskteki dosyalarla aynıdır.

Önerilen biçim (tek satır; tarih ve sha'lar dondurma anında yazılır):

```
Durum: KOŞU DONDURULDU (<GG Ay YYYY>; tr7c_kosu.py c86d8b9b17ae17e8fa67a12ff945a90df791dc0bfd6b548e1f2d3cbaac20a5b2; tr7c_mde_ek.py 4876dcbee8ce455c221efa4782e4af0047e5ade2f7b84eb985f9eb127873e910; ek: TR-7c_KOSU-DONDURMA-EKI.md) — KARAR METNİ DONDURULDU (17 Kasım 2026; …)
```

Bu satır karar metninin 3. satırının yerine geçer; satırın öteki bilgisi korunur. Bu ekin kendisi kapıya girmez.
Ekin §1–§4 içeriği ön kayda taşınacaksa '## 7. ' başlığından sonra eklenir.

## 9. Açık kalanlar

1. **Dondurma satırı ve ekin yeri.** Koordinatör yazar. Bu taslak karar metnine dokunmadı.
2. **Ö-j.** Taslaktır; yazarın onayı ya da değişikliği gerekir.
3. **SIGKILL sonrası sürdürme.** Kod, 'başladı'da kalmış bir algılama aşamasının elle durma kaydı olmadan yeniden
   `kos` edilmesini engellemez. Davranış TR-7 ile aynıdır, istenen de buydu. İşletim kuralı olarak §7'ye yazıldı:
   bekçisiz, elle koşu. Kodla zorlanacaksa sha değişir ve sınamalarla kuru prova yeniden koşulmalıdır.
4. **Hetzner önkoşulları.** `ZARF_KOK` izinleri, git upstream ve push yetkisi, `git_dogrula`'nın gerçek yolu.
   Hiçbiri provada sınanmadı.
5. **Yeniden koşulmayanlar.** KD, TR-7b §11.2, m_f ve duman c86d8b9b… üzerinde yeniden koşulmadı. Algılama ve K5
   hesabı değişmedi (§5).
6. **Önceden kalanlar.** D2, D3 ve D8 yoklamaları yapılmadı (karar metni §15). KMS-7 ve KMS-10 bilgi satırları
   hesaplanmaz. Marmara bağlantısı yazılmadı (O-30); K1c (b) çıkarsa ayrı kod ve ikinci kod incelemesi gerekir.
