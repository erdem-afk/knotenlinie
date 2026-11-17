# TR-6c ön kaydı, ikinci bağımsız inceleme (İNCELEME-2)

Tarih: 17 Kasım 2026. İncelenen: `TR-6c_gerilme-olcer-kor-dogrulama_ONKAYIT.md` TASLAK sürüm 2 (commit'ler 2278efa,
fcda444, de9ed97), `tr6a_kosu.py` / `tr6a_yapay.py` `--tasarim c` yolları, `tr6c_z2.py`, `tr6c_z2_secim.json`,
`tr6c_prova_t7321_*.json`. İnceleyen İNCELEME-1'i de yazdı; yazarın sayılarına güvenilmedi, ana iddialar bağımsız
betiklerle yeniden kuruldu (`kayit/turetme/tr6/inc_c2/`). Yalnız yapay veri kullanıldı; olay sonrası gerçek veri
indirilmedi; bağlayıcı sınama koşulmadı; `TR6C_ONKAYIT_SHA = None` kaldı; ön kayıt metni değiştirilmedi.

## Hüküm: DÜZELTMEYLE KABUL

(a2) yolu doğru ve yeterlidir: kapı seçim yanlılığını tek birimli dünyada ve küme düzeyinde ölçülebilir biçimde soğurur,
C1 artık gerçek koşunun havuzunu sınar. Kod metne uyar; iki kritik kalibrasyon yolu (N1, N3) ve üç küçük yol (N4, N7, N8)
sınamalarca korunmuyordu, bu incelemede bir sınama eklenerek korundu. Aşağıdaki dört cümle metne **aynen** eklenmeden
dondurma yapılmaz (Z9–Z12). Dördü de beyan ve düzeltmedir; kural, eşik ve tohum değişmez, yeni prova gerekmez.

### Zorunlu düzeltmeler (kesin cümleler)

**Z9 (§C3a "Kural" maddesi 1'in sonuna):**
> Kalibrasyon kümesinin temsilcisi, TR-6a §3.7'deki gibi kümenin zamanca ilk birimidir ve gerçek kapıdan bağımsız
> seçilir. Bir K_kapı kümesi, kapı altı bir birimle tek bağlantıyla birleşirse havuza K_kapı temsilcisinin değil,
> birleşik kümenin ilk biriminin sahte oyları girer. Önsayımda üç K_kapı kümesi böyledir (usp000hrw0 → usp000hhuc,
> us6000jllz → us60007ewc, nc75095651 → nc73821036); bu kümelerin ilk birimlerinin kaba N0'ı 1,35 / 14,03 / 17,85'tir
> ve sahteleri havuza neredeyse hiç girmez. "Havuzun oran bileşimi K_kapı'nınkiyle aynı ağırlıkları taşır" cümlesi bu
> yüzden yaklaşıktır. Farklar manifestte `kumeler` ile `kalibrasyon_kumeleri` karşılaştırılarak okunur.

**Z10 (§C9 madde 8'e yeni alt madde):**
> Katalog seçimi (§3.5: gölge kapı N0'ı en büyük katalog) da ön pencerenin sayımına bakan bir seçimdir ve gerçek
> kapıyla aynı yönde çalışır: seçilen katalogda ön sayım yukarı, sahte son sayımlar da yukarı oynar; gerçek düşüş oyu
> artar, sahte düşüş oyu azalır. Bu, kataloglar arası sayım farkının rastgele kısmıyla orantılıdır ve (a2) onu
> soğurmaz; tek kataloglu yapay dünya bunu sınamaz. Yönü H1 lehinedir.

**Z11 (§C3a "Okuma ve seçim"in üçüncü maddesindeki "bir kayıp değildir" cümlesinin yerine):**
> "60 aday λ 31,36" satırındaki güç düşüşünün (0,86 → 0,70) bir kısmı α'nın 0,075'ten 0,042'ye inmesidir, bir kısmı
> gerçek kayıptır: (a2) orada p̂₀'ın gürültüsüyle p₀ > 0,60 payını 0,03'ten 0,14'e çıkarır (aşırı saçılımla 0,28) ve bu
> denemeler "güç yok (ölçü yanlı)" olur. Önsayım dünyasında bu pay 0,01'dir.

**Z12 (§C10 sınama sayısı):** "68 sınama" → "69 sınama (İNCELEME-2 `test_kalibrasyon_havuzu_kapi_alti_c` ekledi)".

## 1. (a2) gerekçesi ve C1 (soru 1)

**Mantık.** Gerçek oy "gerçek kapı geçti" koşuluyla, her sahte oy "kendi sahte kapısı geçti" koşuluyla sayılır; ikisi
aynı yapıdadır (ön pencere sayımı → kapı → son pencere). Sahtelerin seçimi artık gerçek kapıdan bağımsızdır, bu yüzden
sürüm 1'in ikinci koşullaması (sahte son pencere gerçek ön pencerenin içinde) ortadan kalkar. Her oranda bir sahtenin
geçerlilik olasılığı gerçek kapıdan geçme olasılığına eşittir; karışımda havuz oranları K_kapı ile aynı ağırlıklarla
temsil eder (Z9'daki istisnayla). Gerekçe doğrudur.

**Bağımsız deneme kayıtları** (`inc_c2_kayit.py`, tohum 8811, (i) dünyası; yazarın `tr6c_z2.py`'sinden bağımsız):

| λ | deneme | kapı payı | p̂₀ (a2, bütün denemeler) | P(D \| kapı) | C1 farkı | SE (metin formülü) | z | v1 havuzuyla fark |
|---|---|---|---|---|---|---|---|---|
| 28,5 | 5000 | 0,100 | 0,6265 | 0,6248 | +0,0018 | 0,0247 | +0,07 | −0,123 |
| 31,36 | 15000 | 0,470 | 0,5441 | 0,5422 | +0,0019 | 0,0068 | +0,28 | −0,057 |
| 33 | 5000 | 0,711 | 0,4987 | 0,5151 | −0,0164 | 0,0097 | −1,69 | −0,050 |

- Yazarın §C3a tablosu ve 7321 provası (28,5 / 31,36 / 36 / karma, |z| ≤ 1,13) ile uyumlu. 33'teki −0,016 yazarın
  −0,011'iyle aynı yönde ve tek başına anlamlı değil; 36 ve karma hücreler işareti tutmuyor. Gürültü olarak okudum,
  ama "kapı sınırının hemen üstünde 0,01 düzeyinde bir artık" dışlanmış değildir (bağlayıcı sınamada C1 3,5 SE ile
  görmez).
- **C1 artık gerçek koşunun havuzunu sınıyor.** Kapı sınırı hücrelerinde (28,5 / 31,36) v1 havuzu −0,06 … −0,12 sapar,
  (a2) havuzu sapmaz; C1 sürüm 1 havuzuna dönen bir kod hatasını görür (N10 mutantı yakalandı).
- **Eşli SE.** Metnin SE'si sahte ile gerçek arasındaki deneme içi kovaryansı yok sayar. Eşli (deneme başına fark)
  SE'yi hesapladım: 0,0249 / 0,0070 / 0,0098; metin formülüyle aradaki fark ≤ %3. Önemsiz.

**Küme düzeyi α, "60 aday λ 31,36 + 2 kenar"** (`inc_c2_alfa.py`, kendi kayıtlarım, tohum 8812, 20 000 tekrar; kapı altı
6–14 kümeleri yok, kenar H0 D'si prova hattından; p₀, testere, kritik değer incelenen kodun işlevleri):

| | v1 | (a2) | (a2) ölçü yanlı payı |
|---|---|---|---|
| δ 0 | 0,062 | **0,035** | 0,137 |
| δ 0,02 (yalnız gerçek) | 0,085 | **0,051** | 0,138 |

Yazar: v1 0,075 / 0,104, (a2) 0,042 / **0,057**. Benimki sistematik olarak biraz düşük (kapı altı kümeleri yok, farklı
kayıt), ama sıralama ve büyüklük aynı: (a2) uyuşmazlıksız ≤ 0,05, kapı sınırında δ 0,02 ile 0,05 civarı. 0,057 satırı
uç bir birleşimdir (60 kümenin hepsi tam kapı sınırında artı kalibre edilmemiş bir uyuşmazlık), §C3a ve §C9 madde 4'te
açıkça beyan edilmiştir; önsayım dünyasında aynı uyuşmazlık 0,018'dir. Kabul edilebilir.

## 2. Yazarın işaretlediği üç nokta (soru 2)

1. **Kapı altı kümelerin sahte pencerelerinin aynı yapıda sayılması.** §C9 madde 8 bunu beyan ediyor. Gerçek etki
   küçük olmalı: önsayımda kapı altı kümelerin büyük çoğunluğunun sahteleri sahte kapıdan geçmez (benzetimde J
   önsayımda 77,6 → 78,3; önsayım 61), yani kötü katalog/Mc'li kapı altı kümeler havuza zaten az girer. Ek koşul
   gerekmez. Ama aynı türden ve beyan edilmemiş bir seçim var: **katalog seçimi** (Z10).
2. **Benzetim varsayımları.** `tr6c_z2.py`'yi okudum; hata bulmadım. Kaba N0 = gerçek λ, havuz geçersizliği yok
   (J 78 ↔ önsayım 61), lob/Mc kümeden kümeye sabit; hepsi metinde ("Benzetimin sınırları") yazılı. Bağımsız
   yeniden kurulumum (yukarıda) aynı sonuca varıyor.
3. **`kalibrasyon_kumeleri`'nin yeni `kume_seti` çağrısı.** Gerçek kaygı. `inc_c2_kume.py` dondurulan listenin 74
   kosu_adayı birimini kümeledi: kapı birimleri 41 → 35 küme, kalibrasyon 62 küme. Üç K_kapı kümesinin temsilcisi
   değişir (Z9'daki liste); iki kümeye (us20003k7a, us1000i2gt) üye eklenir, temsilci aynı kalır. Kenar kümelerinin
   temsilcisi değişmez. Sonuç: üç K_kapı kümesinin (kapı N0 39,9 / 147,8 / 52,5) kendi sahteleri havuza girmez, yerine
   neredeyse hiç geçmeyen kapı altı temsilcilerin sahteleri girer. Bu üçü kapı sınırından uzaktır (orada sahte ≈ gerçek),
   J ≈ 61'den en çok ~6–9 geçerli sahte eksilir; p̂₀'a etkisi ±0,01'in altında beklenir. Kodun seçimi (ilk birim,
   kapıdan bağımsız) istatistik olarak savunulabilir; metnin "aynı ağırlıklar" cümlesi ise yaklaşıktır → Z9 beyanı.
   Kod değişikliği önermiyorum: "K_kapı temsilcisini kullan" kuralı birimi gerçek kapıya göre seçerdi.

## 3. Z3–Z8 (soru 3)

- **Z1/Z2:** (a2) ile Z1'in amacı (C1'in havuzu = gerçek koşunun havuzu) sağlanmış; Z1'i benim önerdiğim biçimde
  (kapı koşullu) uygulamamak bu yüzden doğru. Kapı koşullu fark bilgi satırı olarak kalmış.
- **Z3:** C1′a (iki yanlı, (i) ve (ii)) ve C1′b (yalnız (i), D4 ↔ kesin) metinde ve kodda; N11 mutantı (C1′b'yi (ii)'ye
  uygulamak) yakalandı (bkz. §5).
- **Z4:** "Neden 500" yeniden yazılmış; 316–584 boşluğu ve "yazar bunu bilirken seçti" cümlesi var.
- **Z5:** Kenar A'sı pay ve paydadan çıkıyor (`A = None`, `K_Y`, `c⁺(K − m)`); S1/S7/S2 süzgeci ve tamlık
  elemesinden sonra yeniden kurulumu var; Tohoku körlük cümlesi var.
- **Z6:** §C11 var. **Z7:** §C9 madde 9 (0,043 / 0,045 / 0,059). **Z8:** sha ve sayı cümleleri güncel (Z12 hariç).
- **Yeni serbestlik:** bulmadım. (a2) havuzunun bütün parçaları (liste, sıra, temsilci kuralı, sahte kapısı) manifest
  çekirdeğindeki `kalibrasyon_kumeleri` ile olay sonrası veriden önce sabitlenir; olay sonrası veri kalibrasyon
  kümeleri için indirilmez. Kapı altı kümelerin sayısı ve J'si önceden bilinmiyor ama kuralla belirleniyor.

## 4. 4500 hücrelerinin yeniden özetlenmesi (soru 4)

Kabul edilebilir. Gerekçe:
- Sürüm 2 eski hücrelerin parça kodunu değiştirmedi (karma dalı yalnız karma hücrede; yeni hücreler sona eklendi).
  Bunu bağımsız olarak sınadım: bugünkü kodla tohum 7311 parçaları yeniden üretildi ve kayıtlı sha256'larla
  karşılaştırıldı (sonuç aşağıda, `inc_c2_parca.json`).
- Kenar hücrelerinde kapı payı 1'dir: (a2) havuzu ile kapı koşullu havuz aynıdır; değişen yalnız ölçütün adı (C1′a)
  ve C1′b'dir, ikisi de aynı parça sütunlarından hesaplanır.
- Prova bağlayıcı değildir; i:1500 ve ii:1500 yeni tohum 7321 ile de koşuldu ve geçti.
- Bağlayıcı sınama yeni tohumla bütün hücreleri yeniden koşar.

(Bu denetimin çıktısı yazılamadı: inceleme oturumu makinenin yeniden başlamasıyla kesildi ve sürdürülemedi. İNCELEME-1'de aynı kodla altı prova parçası yeniden üretilmiş ve sha256'ları kayıtlı değerlerle aynı çıkmıştı; 4500 hücresi parçalarının bu turdaki bayt denetimi tamamlanmadı. Not kök oturumca eklendi, 17 Kasım 2026.)

## 5. Kod metne uyuyor mu (soru 5)

Kalibrasyon havuzu, kenar A'sı, S1/S7/S2 süzgeci, `K_Y`, C1/C1′a/C1′b, karma hücre ve bağlayıcı koruma satır satır
okundu; metinle çelişki bulmadım.

**Mutasyon sınaması** (`inc_c2_mutasyon.py`, 14 mutant, `TTasarimC` sınıfı; çıktı `inc_c2_mutasyon_once.json` ve
`inc_c2_mutasyon_sonra.json`):

| Mutant | Önce (yazarın 68 sınaması) | Sonra (69) |
|---|---|---|
| N1 havuz kapıdan sonra (v1'e dönüş) | **kaçtı** | yakalandı |
| N2 kenar kümeleri havuzdan çıkmaz | yakalandı | yakalandı |
| N3 havuz yalnız K_kapı kümelerinden | **kaçtı** | yakalandı |
| N4 manifest çekirdeğinde kalibrasyon listesi yok | **kaçtı** | yakalandı |
| N5 S1/S7 süzgeci hep çıkarır | yakalandı | yakalandı |
| N6 S2'de kenar kümesi kalır | yakalandı | yakalandı |
| N7 p_Y paydası K | **kaçtı** | yakalandı |
| N8 ters yön eşiği c⁺(K) | **kaçtı** | yakalandı |
| N9 tamlık elemesinden sonra S7 süzgeci yok | kaçtı | kaçtı |
| N10 C1 havuzu kapı koşullu | yakalandı | yakalandı |
| N11 C1′b (ii)'ye de | yakalandı | yakalandı |
| N12 karma aralığı 30–60 | yakalandı | yakalandı |
| N13 bağlayıcı parça koruması yok | yakalandı | yakalandı |
| N14 kenar A'sı 0 | yakalandı | yakalandı |

Önce 8/14, sonra 13/14. N1 ve N3 kritiktir: (a2)'nin tamamını sessizce geri alan ya da yarıya indiren bir hata
sınamalardan geçiyordu. N9 kaçıyor: tamlık elemesi yalnız gerçek Mc_son'u kestirilemeyen bir küme varken çalışır ve
yapay sınama dünyası bunu kenar nötr bölgesiyle birlikte kurmuyor. Kod okuması doğru (`_kontrol_kenar_disi` K⁺ ve
K_nt'de iki yerde de var); TR-6c kod incelemesinde (§C8 adım 4) elle denetlenmesini öneririm, zorunlu değil.
"Önce" sütununun M0–N7 satırları makine yeniden başlamadan önceki günlükten alınmıştır (hata satırları kayboldu).

**Eklenen sınama** `test_kalibrasyon_havuzu_kapi_alti_c` (`tr6a_test_yapay.py`, `TTasarimC`): yapay çok birimli
dünyada kapı altı kümelerin (y26–y28) `kalibrasyon_kumeleri`'nde olduğunu, K_kapı'da olmadığını, sahteleri geçerli
yapıldığında J ve S'ye girdiğini, manifest çekirdeğinin listeyi taşıdığını ve p_Y'nin paydasının K_Y olduğunu sınar.
Yazarın sınamaları kapı altı kümelerin sahteleri hiç geçmeyen bir dünyada koşuyordu; v1'e dönüş (N1) ve havuzu
yalnız K_kapı'dan kurmak (N3) J ve S'yi değiştirmediği için görünmüyordu.

**Bütün sınamalar:** `python3 -I -B kayit/turetme/tr6/tr6a_test_yapay.py` → 69 sınama, OK (202 s). Kod (`tr6a_kosu.py`,
`tr6a_yapay.py`) bu incelemede değiştirilmedi; yalnız sınama dosyasına bir sınama eklendi.

## Ek: dosyalar

- `kayit/turetme/tr6/inc_c2/inc_c2_kume.py`, `inc_c2_kume.json`: dondurulan listenin kalibrasyon / K_kapı kümelemesi.
- `inc_c2_kayit.py`, `inc_c2_kayit_i_{28.5,31.36,33}.json`: bağımsız deneme kayıtları (tohum 8811).
- `inc_c2_alfa.py`, `inc_c2_alfa_i_31.36_60.json`: küme düzeyi α (tohum 8812).
- `inc_c2_mutasyon.py`, `inc_c2_mutasyon_once.json`, `inc_c2_mutasyon_sonra.json`.
- `inc_c2_parca.json`: tohum 7311 parçalarının bayt yeniden üretimi.
- Kullanılan tohumlar: 8811, 8812 (ne bağlayıcı ne tanı tohumu).
