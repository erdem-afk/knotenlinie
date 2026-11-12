# TR-9 hedef sayımı ve tasarım (kör): artçı cephesi jeodezik kilitli/sünen sınırında mı duruyor?

Tarih: 12 Kasım 2026. Durum: SAYIM (ön kayıt değil). Sınav koşulmadı: hiçbir olayda artçı ucunun konumu ve
uçtan sınıra uzaklık hesaplanmadı. Erdem'in 12 Kasım talimatıyla (bütün açık adaylar seçimsiz ve elemesiz
ilerletilsin) yapılan 0 € sayım ve güç kapısıdır. Bu belge adayı elemez; sayıları ve kapı durumunu verir.
Kaynak: `research_notes/Fayın anlık durumu gözlem boşlukları/nisan_2025_marmara.md` (NA-1), defter satırı TR-9.
Kod: `kayit/turetme/tr9/tr9_sayim.py`. Özet ve olay satırları: `kayit/turetme/tr9/tr9_sayim_ozet.json`.
Ham veri depoda değil, scratch'te: TR-2 ComCat anlık görüntüsü (`.../scratchpad/tr2/ham/`, bitiş 2025-12-31)
yeniden kullanıldı. 31 aday olay için yeni M ≥ 2,5 artçı sorgusu `.../scratchpad/tr9/ham/` altında (dosyaların
toplu sha256'sı 3adb3a14…).

## 0. Hüküm

**Kapı: GEÇMEZ.** Kilitlenme ya da sünme haritası yayımlanmış 22 doğrultu atımlı kesimin 50 km yakınında 31 Mw
6,0–7,2 doğrultu atımlı olay var (25 bağımsız küme). Bunların çoğu kesimin üstünde değil, yanındaki başka bir fayda
(Loma Prieta 1989, El Mayor-Cucapah 2010, Big Bear 1992, Napa 2014). ComCat'te artçı ucu ölçülebilen bağımsız küme
sayısı K = 4 (artçı M ≥ 4, TR-2 tanımı) ya da K = 6 (artçı M ≥ 2,5; yalnız Kaliforniya'da fark ediyor). Kapı
K ≥ 20. İyimser tavan (olay iz üstünde ≤ 15 km, sınır doğrultu boyunca ≤ 3 L, ucu her olayda bölgesel düşük Mc'li
bir katalogla ölçülebilir sayılır) K = 12. M ≥ 5,8 varyantıyla bu tavan ≈ 16 olur. Sınır haritası olaydan önce
yayımlanmış ve künyesi doğrulanmış olaylarla K ≈ 5–8. Geçmemenin üç nedeni var: (1) kilitlenme/sünme haritası olan
kesimler azdır ve üstlerinde M ≥ 6 seyrektir; (2) küresel katalogda artçı ucu ölçülemez; (3) sayısal harita çoğunlukla
açık değildir. Üçüncüsü DD-3'ün kapanış nedeniyle aynı. Nisan 2025 Marmara olayı, ComCat'te 7 artçıyla bu sınavın
içinde de ölçülemiyor. Marmara için sayılan soru, bir sınav değil, NA-1 tipi tek olaylı bir ölçüm olarak kalıyor.

## 1. Kodlanabilir tasarım

Bu tasarım, kapı geçerse dondurulacak tanımların taslağıdır. Sayım yalnız 1.1, 1.3 ve 1.7'yi kullandı.

### 1.1 Kesimler

Kesimler, doğrultu atımlı olan ve kilitlenme/sünme haritası hakemli yayımlanmış olanlardır. Liste §2.1'de, künyeler
OpenAlex ile doğrulandı. İz köşeleri literatürdeki yer adlarından elle yazıldı ve sayısallaştırılmadı (yaklaşık
±10 km). Bu doğruluk 50 km tamponla sayım için yeterli, sınav için değil.

### 1.2 Sınır tanımı (sınav için)

- Sınır, kesim izi üzerinde kilitlenme oranının (ya da yüzey sünme hızının yükleme hızına oranının) 0,5'i geçtiği
  noktadır. Doğrultu boyunca tek boyutlu bir koordinattır.
- Kaynak öncelik sırası:
  1. açık sayısal ızgara;
  2. makaledeki tablo ya da metinde verilen sınır boylamı/enlemi;
  3. şekilden sayısallaştırma (yalnız bilgi satırı; DD-3 dersi gereği ana sınava girmez).
- Sızıntı kuralı: harita olaydan önce yayımlanmış olmalı ve olaydan önceki veriyle kurulmuş olmalı. Olaydan sonra
  yayımlanan haritalar ancak veri penceresi olay öncesinde bitiyorsa ve artçı ya da kosismik veri içermiyorsa kabul
  edilir. Bu koşul bir varyanttır ve yalnız bilgi verir.
- Mikrosismisite ya da tekrarlayan depremle kurulan sünme haritaları ayrı işaretlenir. Bu haritaların sınırı ile
  artçı cephesi aynı sismik ağdan gelir (döngüsellik riski, §4).

### 1.3 Olay seçimi (sayımda kullanılan)

- TR-2 birincil tanımı aynen: ComCat 1976–2025, Mw 6,0–7,2, derinlik ≤ 25 km, mekanizmalı, |rake| ≤ 30° ya da
  ≥ 150°.
- Dış merkez kesim izine ≤ 50 km.
- Sınavda ayrıca şu iki koşul aranır:
  - iz üstünde: ≤ 15 km;
  - en yakın sınır, dış merkezden doğrultu boyunca ≤ 3 L uzakta. L, Wells ve Coppersmith 1994 yeraltı kırık boyudur.

### 1.4 Artçı ucu (TR-2 tanımlarından)

- Artçılar: (t0, t0 + 30 gün], dış merkezden ≤ 3 L, birincilden küçük, ize dik uzaklık ≤ max(15 km, 0,5 L).
- s: artçının iz boyunca konumu.
- Sınıra bakan yan, olay öncesi bilgiyle belirlenir: sınır dış merkezin hangi yanındaysa o yan.
- Uç: o yandaki artçıların s değerinin %95'liği. %95'lik seçildi çünkü en uç tek artçı konum hatasına duyarlıdır.
- Uç ölçülebilirlik koşulu: toplam ≥ 10 artçı ve sınıra bakan yanda ≥ 5 artçı (TR-2'deki n ≥ 10 ile aynı mantık).
- Artçı büyüklük eşiği iki katmanlıdır:
  - (a) küresel tek biçim, M ≥ 4 (ComCat);
  - (b) bölgesel, M ≥ max(Mc_yerel, Mw − 3). Bölgesel kataloglar: AFAD/KOERI, CWA Tayvan, PHIVOLCS, BMKG, ANSS.
    Mc her olay için olaydan önceki 5 yılın kataloğundan, ön kayıtta bulunur.

### 1.5 Ölçü

- D = |s_uç − s_sınır| / L, birimsiz.
- İkincil ölçü D_km; tolerans 5 km, konum hatası ve sınır belirsizliği payı.

### 1.6 Yer değiştirme kontrolü

- Sınır, kesim izi boyunca dış merkezin sınıra bakan yanında [0,5 L, 3 L] aralığında tekdüze kaydırılır (1000 çekiliş).
  Kayma, kesimin haritalı uzunluğuyla sınırlıdır.
- Olay başına sıra: r_i = P(D_kaydırılmış ≤ D_gözlenen). H0 altında r_i ~ U(0,1).
- İkili ölçü: isabet = D ≤ 0,25 L. Olay başına H0 isabet olasılığı p0_i yine kaydırmadan hesaplanır, tipik olarak
  0,15–0,3.
- Negatif kontrol: aynı olaylarda sınırın yerine dış merkezin karşı yanındaki rastgele bir nokta kullanılır. Bu,
  uçların kesime özgü bir noktada mı yoksa herhangi bir noktada mı toplandığını ayırır.

### 1.7 Bağımsızlık birimi

- TR-2 kümeleri: tek bağlantı, 300 km ve 1 yıl.
- İkinci koşul: aynı kesim-sınır çiftine düşen birden çok küme tek birim sayılır (`K_kesim_birimi`). Aynı sınırı iki
  kez sınamak bağımsız bilgi değildir.

### 1.8 Hüküm satırı

- Ana ölçü: ortalama sıra r̄, tek yanlı test, α 0,05, H1 r̄ < 0,5.
- İkincil ölçü: isabet sayısı. Sınama Poisson-binom dağılımıyla yapılır, p0_i ön kayıtta yayımlanır.
- Hüküm şablonu: "artçı uçları kilitlenme sınırına rastgele konumdan yakın durur / ayırt edilemez" (r̄ ve 95% aralığı).
- Marmara 2025 bu sınavın gerekçe olayıdır. Sızıntı nedeniyle puanlanmaz, yalnız bilgi satırı olur.

### 1.9 Güç kapısı: K ≥ 20 (gerekçe)

Kesin binom, tek yanlı α 0,05 (`tr9_sayim.py guc`):

| K | p0 | kritik isabet | güç p1 = 0,4 | p1 = 0,5 | p1 = 0,6 |
|---|---|---|---|---|---|
| 8 | 0,20 | 5 | 0,17 | 0,36 | 0,59 |
| 12 | 0,20 | 6 | 0,33 | 0,61 | 0,84 |
| 15 | 0,20 | 7 | 0,39 | 0,70 | 0,90 |
| **20** | **0,20** | **8** | **0,58** | **0,87** | **0,98** |
| 30 | 0,20 | 11 | 0,71 | 0,95 | 1,00 |

Sıra ölçüsünde H1 r ~ Beta(a, 1) alındı. a = 0,5'te güç: K = 12 için 0,63; K = 15 için 0,72; K = 20 için 0,82.

K ≥ 20 öneriliyor, iki gerekçeyle:

1. "Uçların yarısı sınırda" (p1 0,5) gibi orta büyüklükte bir etki ancak K = 20'de %80 güçle görülür. p0 0,3'e çıkarsa
   K = 20 bile 0,59 güç verir.
2. Bu turda kaba sayımlar ayrıntılı sayımda hep küçüldü (TR-1 60 → 12, TR-2 60–120 → 40). Kapının payı olmalı.

TR-1 ve TR-11'in kapısı da 20'dir.

## 2. Sayım

### 2.1 Kilitlenme/sünme haritası yayımlanmış doğrultu atımlı kesimler (OpenAlex ile doğrulanmış künyeler)

Açık veri sütununda "bilinmiyor", yayımcı sayfasında ya da Zenodo'da sayısal ızgara bulunamadığı anlamına gelir.
Tam metin okunmadı.

| Kesim | Harita künyesi (DOI) | Ne veriyor (özetten) | Sayısal harita açık mı |
|---|---|---|---|
| San Andreas sünen kesimi + Parkfield | Maurer & Johnson 2014, 10.1002/2013jb010741 | Blok modelle kilitlenme, 150 km sünen kesim | Bilinmiyor; UCERF3 sünme tablosu açık (10.3133/ofr20131165) |
| Hayward, Calaveras | Chaussard ve ark. 2015, 10.1002/2015jb012230 | InSAR 1992–2011; sünme 0 ± 2 (K. Calaveras) ile 14 ± 2 mm/yıl; kilitlenme modeli | Bilinmiyor; Bay Area S1 hız haritası Zenodo 10.5281/zenodo.7459716 (2015–2022, ham hız) |
| Hayward (zamana bağlı) | Shirzaei & Bürgmann 2013, 10.1002/jgrb.50149 | 18 yıl InSAR + sünme ölçer | Bilinmiyor |
| Rodgers Creek, Concord–Green Valley, Maacama | UCERF3, 10.3133/ofr20131165 | Alt kesim başına sismik olmayan kayma oranı | Evet (tablo) |
| Imperial | Lindsey & Fialko 2016, 10.1002/2015jb012516 | InSAR + GPS, sünen/kilitli derinlik | Bilinmiyor |
| Superstition Hills | Wei, Sandwell & Fialko 2009, 10.1029/2008jb006135 | Mw 4,7 sessiz kayma; sünme | Bilinmiyor |
| Güney SAF (Coachella) | Vavra & Fialko 2026, 10.1029/2026jb034392 | 2015–2021 sünme, tetiklenmiş | Bilinmiyor |
| KAF İsmetpaşa | Kaneko ve ark. 2013, 10.1029/2012jb009661; Çakır ve ark. 2005, 10.1016/j.epsl.2005.06.044; 2014 PS-InSAR, 10.1002/2014gc005307 | Sünme ≈ 9 mm/yıl, yanal uzanım ≈ 75 km | Bilinmiyor |
| KAF İzmit (1999 sonrası) | Hussain 2016, 10.1002/2015jb012737 | Postsismik sünme; olay öncesi değil | Bilinmiyor |
| KAF Marmara (CMF/Kumburgaz) | Yamamoto 2019, 10.1029/2018gl080984; Lange 2019, 10.1038/s41467-019-11016-z | Deniz tabanı jeodezisi, kısmi sünme | Kısmen (akustik ham veri; defter Y-3) |
| DAF Pütürge | Blétery ve ark. 2020, 10.1029/2020gl087775 | KAF+DAF kilitlenme, DAF heterojen ve sığ (0–5 km) | Bilinmiyor; Elazığ 2020 sonrası yayımlandı |
| Haiyuan (Laohushan) | 10.1029/2020jb021576 (2021); 10.3390/rs13163333 | Sığ sünme, kilitlenme | Kısmen: Zenodo 10.5281/zenodo.8024561 (Tibet blok sınırı kilitlenme modeli, 2023), 10.5281/zenodo.22112396 (2026); içerik okunmadı |
| Xianshuihe | Li & Bürgmann 2021, 10.1029/2020jb021406; Tong & Chen 2024, 10.1093/gji/ggae310 | Birden çok sünen kesim, kilitlenme modeli | Kısmen: Zenodo 10.5281/zenodo.5108951 (GD Xianshuihe kayma hızı); içerik okunmadı |
| Longitudinal Valley (Chihshang) | Thomas ve ark. 2014, 10.1002/2013jb010603; 10.1029/2023jb026843 | Sismik ve sismik olmayan kayma, kilitlenme | Bilinmiyor; 2022 olayı jeodezik verisi Zenodo 10.5281/zenodo.8268096 (olay sonrası) |
| Filipin fayı Leyte | Fukushima ve ark. 2019, 10.1186/s40623-019-1096-5; Duquesnoy 1994, 10.1029/94gl00640 | Sünme 33 ± 11 mm/yıl; 11,08–11,20° K arası kilitli | Bilinmiyor |
| Filipin fayı Masbate | Besana & Ando 2005, 10.1186/bf03351877 | Merkezî Filipin fayında sünme | Bilinmiyor |
| Sumatra fayı Aceh | Ito ve ark. 2012, 10.1029/2011jb008940; Salman ve ark. 2026, 10.1038/s43247-026-03951-9 | Sığ sünme derinliği, kilitlenme; sünen kesim 2013'te Mw 6,1 ile kırıldı | Bilinmiyor |
| Chaman | Dalaison ve ark. 2021, 10.1029/2021jb021935; Fattahi & Amelung 2016, 10.1002/2016gl070121 | Üç sünen kesim (80–130 km) | **Evet**: Zenodo 10.5281/zenodo.5221208 |
| El Pilar | Pousse-Beltran 2016, 10.1002/2016jb013121; Jouanne 2011, 10.1016/j.jog.2010.11.003 | Sünme batıda 25 ± 9, doğuda daha az | Bilinmiyor; 1997 Cariaco'dan sonra keşfedildi |
| Ölü Deniz (havza kenarı) | Hamiel, Bilham & Piatibratova 2025, 10.1029/2024jb030191 | Sığ sismik olmayan deformasyon | Bilinmiyor |
| Derleme | Harris 2017, 10.1002/2016rg000539 | Sünen faylar ve büyük depremler derlemesi (Mw ≤ 6,6 kayıtlı) | Derleme |

22 kesim tabloya alındı. Açık sayısal kilitlenme/sünme ızgarası doğrulanan kesimler yalnız Chaman (Zenodo) ve
UCERF3 tablosunun kapsadığı Kaliforniya alt kesimleri. Haiyuan ve Xianshuihe'de Zenodo kayıtları var, içerikleri
okunmadı.

### 2.2 Olay sayımı (ComCat, bitiş 2025-12-31)

| Aşama | N | Bağımsız küme K | Kesim birimi |
|---|---|---|---|
| TR-2 birincili (Mw 6,0–7,2, ≤ 25 km, doğrultu atımlı) | 1340 | — | — |
| Kesim izine ≤ 50 km | **31** | 25 | 13 kesim |
| Uç ölçülebilir, artçı M ≥ 4 (ComCat, küresel tek biçim) | 5 | **4** | 3 |
| Uç ölçülebilir, artçı M ≥ 3 | 7 | 6 | 5 |
| Uç ölçülebilir, artçı M ≥ 2,5 | 7 | **6** | 5 |
| Tavan: iz üstünde (≤ 15 km), sınır ≤ 3 L, ucu her olayda ölçülebilir sayılır | 13 | **12** | 10 |
| Ek varyant: 5,8 ≤ M < 6,0, iz üstünde ≤ 15 km, doğrultu atımlı (yeni küçük sorgu) | 7 | +4 yeni küme | — |

Uç ölçülebilen olaylar (ComCat), M ≥ 4 ile:
- Imperial Valley 1979 (Mw 6,4);
- El Mayor-Cucapah 2010 (Mw 7,2). Imperial kesimine 43 km uzakta, kendisi Laguna Salada/Cucapah'ta, yani kesim
  üstünde değil;
- Elazığ 2020 (Mw 6,7);
- Tayvan Chihshang 2022 çifti (Mw 6,5 ve 6,9; tek küme).

M ≥ 2,5 eşiğiyle bunlara yalnız Kaliforniya'dan Loma Prieta 1989 ve Big Bear 1992 ekleniyor; ikisi de kesim üstünde
değil.

Tavandaki 13 olay ve olay öncesi harita durumu:

| Olay | Kesim | İze km | M4 artçı (izde) | Olay öncesi harita | Not |
|---|---|---|---|---|---|
| 1979 Imperial Valley Mw 6,4 | Imperial | 2,5 | 20 | Doğrulanamadı | Harita 2016 |
| 1986 El Pilar Mw 6,3 | El Pilar | 3,8 | 2 | Yok | Sünme 2010'da bulundu |
| 1987 Elmore Ranch Mw 6,2 / Superstition Hills Mw 6,6 | Superstition Hills | 3,4 / 6,2 | 16 / 12 | Doğrulanamadı | İlki çapraz fay |
| 1992 Joshua Tree Mw 6,1 | Coachella iz ucu | 6,2 | 18 | — | Kesim üstünde değil (Eureka Peak) |
| 1997 Cariaco Mw 7,0 | El Pilar | 8,9 | 9 | Yok | |
| 2013 Aceh Mw 6,1 | Sumatra Aceh | 5,3 | 7 | Var (Ito 2012) | |
| 2014 Napa Mw 6,0 | Rodgers Creek | 11,3 | 0 | — | Kesim üstünde değil (West Napa) |
| 2017 Ormoc Mw 6,5 | Leyte | 0,8 | 2 | Var (Duquesnoy 1994) | |
| 2020 Elazığ Mw 6,7 | DAF Pütürge | 9,4 | 26 | Doğrulanamadı | Blétery 2020 olaydan sonra |
| 2024 Kale Mw 6,0 | DAF Pütürge | 10,2 | 1 | Var (Blétery 2020) | |
| 2022 Chihshang Mw 6,9 | Longitudinal Valley | 7,7 | 20 | Var (Thomas 2014) | |
| 2025 Marmara Mw 6,2 | KAF Marmara | 3,2 | 7 | Var (Yamamoto 2019) | Gerekçe olayı, puanlanmaz |

M ≥ 5,8 varyantının iz üstündeki doğrultu atımlı ek olayları:
- Coyote Lake 1979 (Calaveras);
- Imperial 1979 artçısı;
- İzmit 1999 artçısı. Sünme 1999 sonrası olduğu için geçersiz;
- Parkfield 2004 (Mw 5,97);
- Masbate 2005;
- Kangding 2014 (Mw 5,9);
- Leyte 2017 artçısı.

Morgan Hill 1984, ComCat'te ML 6,2 olduğu için Mw şartıyla dışarıda kalıyor.

Özet: olay öncesi haritası doğrulanmış, iz üstündeki ve puanlanabilir olaylar Aceh 2013, Ormoc 2017, Kale 2024,
Chihshang 2022 ile M ≥ 5,8 varyantında Parkfield 2004 ve Coyote Lake 1979 (sünme ölçer 1970+). Bu **K ≈ 5–8**
eder.

### 2.3 Kapı

| Tanım | K | Kapı (K ≥ 20) |
|---|---|---|
| ComCat, artçı M ≥ 4 (ana, küresel tek biçim) | 4 | GEÇMEZ |
| ComCat, artçı M ≥ 2,5 | 6 | GEÇMEZ |
| Tavan, bölgesel katalog, iz üstü | 12 | GEÇMEZ |
| Tavan + M ≥ 5,8 | ≈ 16 | GEÇMEZ |
| Olay öncesi harita şartıyla | ≈ 5–8 | GEÇMEZ |

**Sonuç: GEÇMEZ.** En gevşek tanımda bile K 20'nin altında. Gerçek K = 12 ve p0 0,2 alınırsa, p1 0,5'e karşı güç
0,61 olur.

## 3. Maliyet ve iş yükü

- Para: 0 €. Kullanılan kaynaklar: ComCat; AFAD/KOERI ve CWA katalogları (açık); PHIVOLCS ve BMKG (erişim
  denenmedi); CENC (erişimi kısıtlı olabilir, denenmedi).
- İş yükü (kapı geçseydi):
  - sınırların ~12 makaleden okunması: 3–5 gün (çoğu şekilden sayısallaştırma);
  - bölgesel artçı kataloglarının toplanması ve Mc kestirimi: 2–3 gün;
  - kod: 1 gün.

## 4. En büyük üç risk

1. **Sınırın bağımsız olmaması (sızıntı ve döngüsellik).** Haritaların çoğu olaydan sonra yayımlandı (El Pilar,
   Leyte ALOS, DAF, Xianshuihe, Longitudinal Valley 2023). Bazıları mikrosismisite ya da tekrarlayan depremle kuruldu,
   yani artçılarla aynı ağın verisine dayanıyor. Ünlü olayların "kırık sünen kesimde durdu" sonucu özetlerde zaten
   yazılı. Örnek: Elazığ 2020 için Konca 2021 özeti, kırığın zayıf kilitli kesimin yanında başladığını ve güneybatı
   sınırından ≈ 30 km önce durduğunu söylüyor. Sınav tasarımcısı sonucu kısmen biliyor.
2. **Örneklem.** ComCat ile K = 4–6. Bölgesel kataloglarla bile tavan 12–16. Kesimlerin çoğunda M ≥ 6 50 yılda 0–2
   kez oluyor. Uç ölçümü bölgesel kataloglara geçince Mc heterojenleşiyor. Bu, TR-2'nin risk 3'ündeki örnekleme
   sorununun aynısı.
3. **Sınır konumunun belirsizliği etkiyle aynı ölçekte.**
   - Sayısal ızgara yalnız 1–2 kesimde açık. Şekilden okunan sınırın belirsizliği ±5–10 km. Toleransın kendisi
     (0,25 L) 3,5–20 km.
   - Kesim izleri elle yazıldı. İz üstündeki birkaç olay (Napa, Joshua Tree) aslında komşu fayda.
   - Bu DD-3'ün kapanış nedeniyle aynı: "Sayısal kilitlenme ızgaraları açık yayımlanmadıkça koşulamaz."

## 5. Defterle örtüşme (`kayit.py ara`: TR-9, kilitlenme, sünen, DD-3, DK-4, DK-5, DT-1)

- **DD-3 (kapandı, veri yok)**: kilitlenme → kırık sınırı, çok olaylı, dalma-batma; DT-1 ve DK-4 de bunun içine
  birleşti. TR-9 aynı sorunun doğrultu atımlı ve artçılı biçimi. Aynı darboğaza takılıyor: sayısal harita yok.
  TR-9'un farkı, kırık yerine artçı cephesini kullanmasıdır; kırık modeli gerekmiyor.
- **TR-2 (H0)**: artçı tanımları buradan alındı. TR-2 yönü sınadı, TR-9 sınır yerini sınar. TR-2'nin ComCat'te
  ölçemediği Marmara 2025, TR-9'da da ölçülemiyor.
- **S-3 (H0)**: "sünme haritaları D3 koridorlarına düşmüyor" dersi, sünen kesim bilgisinin M7 yerini belirlemediğini
  gösterdi. TR-9 daha dar bir soruyu sınar: büyük kırık değil, M6 artçı cephesi.
- **DK-5 (güç yok)**: 9 kesim ve 16 olayla Hayward tipi moment dengesi. Aynı kesim evreni, aynı güç sorunu. TR-9'un
  olay sayısı (12–16) DK-5'inkiyle aynı mertebede.
- **NA-1 (ölçüm, bekle)**: Marmara 2019/2025 cephesinin Klein sınırına uzaklığı. Bu tek olaylı bir ölçümdür. TR-9
  kapısı geçmese de NA-1 bir tutarlılık ölçümü olarak ayrıca yapılabilir; güç iddiası yoktur.

## 6. Yeniden açma şartı (kapının geçmesi için gereken veri)

Aşağıdakilerden biri gerçekleşirse kapı yeniden sayılır:

- (a) En az 20 bağımsız olay kümesi için olaydan önce yayımlanmış, açık sayısal kilitlenme ya da sünme ızgarası
  bulunur. Örnekler: Sentinel-1 tabanlı küresel tutarlı bir fay sünme veri seti, COMET/LiCSAR türevi bir sünme
  kataloğu ya da UCERF3 benzeri tablonun başka bölgelere genişlemesi.
- (b) Sınav dalma-batmayı da kapsayacak biçimde genişletilir ve DD-3 ile birleştirilir; yine sayısal ızgara şartıyla.
- (c) Marmara ölçümü (NA-1) için defterdeki şart: Klein 2026 hakemli yayımlanır.

Bugünkü tempo: haritalı kesimlerin iz üstünde (≤ 15 km) Mw ≥ 6 doğrultu atımlı olay yılda ≈ 0,26 (50 yılda 13). 20'ye organik yoldan ulaşmak onlarca yıl
sürer. Kapının açılması olay birikmesinden değil, veri yayımlanmasından gelir.

## 7. Körlük beyanı

- ComCat sorgularının hepsi ≤ 2025-12-31 bitişli; kod `tr2_sayim.sorgu` ile assert eder.
- Bu iş için yeni yapılan sorgular:
  - 31 olayın M ≥ 2,5 artçı sorgusu;
  - 5,8 ≤ M < 6,0 küresel listesi;
  - iz üstündeki 14 olayın ayrıntısı.
- Artçı ucunun konumu, D ve r hiçbir yerde hesaplanmadı. Çıktıya yalnız iz üstü artçı sayısı ve "sınıra bakan yanda
  ≥ 5 artçı var mı" bilgisi yazıldı. Bu ikisi tek başına uç konumunu vermez.
- Okunan özetlerin bir kısmı olayların kırık uçlarını anlatıyor (Elazığ 2020, Ormoc 2017, Luding 2022). Bu, risk
  1'deki tasarımcı bilgisi olarak kayda geçer.
- OpenAlex aramalarından birinde 2026 tarihli bir Venezuela depremi başlığı listelendi. Açılmadı ve kullanılmadı.
