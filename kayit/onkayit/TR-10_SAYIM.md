# TR-10 hedef sayımı ve tasarım (kör): sünme hızındaki yıl ölçekli değişim yakın M≥6 öncesinde olağandışı mı?

Tarih: 12 Kasım 2026. Durum: SAYIM (ön kayıt değil). Sınav koşulmadı: hiçbir sünme serisinin içeriği okunmadı,
hiçbir hız değişimi hesaplanmadı. Erdem'in 12 Kasım talimatıyla (bütün açık adaylar seçimsiz ve elemesiz
ilerletilsin) yapılan 0 € sayım ve güç kapısıdır. Bu belge adayı elemez; sayıları ve kapı durumunu verir.
Kaynak: `research_notes/Fayın anlık durumu gözlem boşlukları/jeodezik_gecici_gravite.md` (JG-2), defter satırı TR-10.
Kod: `kayit/turetme/tr10/tr10_sayim.py` (kesim izleri `tr9/tr9_sayim.py`'den). Özet: `kayit/turetme/tr10/tr10_sayim_ozet.json`.
Ham veri depoda değil, scratch'te (`.../scratchpad/tr10/ham/`):
- ComCat olay listesi (sha256 a1cf1737…);
- USGS indirme sayfası (sha256 74b3eb43…).

## 0. Hüküm

**Kapı: GEÇMEZ.** Ana tanım şu koşullardan oluşur:
- sünme serisi olan kesimin ya da sünme ölçerin ≤ 50 km yakınında M ≥ 6;
- olaydan önce ≥ 5 yıl kayıt;
- seri türü sınırsız: USGS sünme ölçerleri, yayımlanmış InSAR/sünme ölçer serileri ve henüz işlenmemiş LiCSAR
  Sentinel-1 üst sınırı birlikte sayılır.

Bu tanımla 23 olay ve **K = 17** bağımsız küme çıkıyor. Kapı K ≥ 20. Alt tanımlar:
- doğrultu atımlı Mw alt kümesi: K = 11;
- ≤ 30 km: K = 13;
- bugün açık ve sürekli olan tek seri türü (USGS K. Kaliforniya sünme ölçerleri): K = 3.

Eşiğin üstüne çıkan tek varyant M ≥ 5,5 ve ≤ 50 km (K = 21). Bu varyant da üç nedenle güvenilmez:
- Tayvan'daki bindirme ve verev olaylarla dolu;
- LiCSAR serilerinin henüz türetilmesi gerekiyor;
- Chihshang sünme ölçerinin 2003 sonrası sürekliliği doğrulanamadı.

TR-2 dersi gereği eşiği geçmek için varyant seçilmez. Sorunun Marmara'ya aktarılması da bugün mümkün değil:
- Marmara'da ≥ 5 yıllık sünme serisi yok (Kumburgaz akustik 2017–2019, 2 yıl);
- Marmara GNSS 2017+ başka sınav için kör;
- InSAR deniz altındaki CMF'yi görmez.

USGS sünme ölçer arşivi açık ve erişilebilir. Bu da TR-1 → TR-11 dersinin burada da uygulanabileceğini gösteriyor:
olay gerektirmeyen "sünme hızı değişiminin taban dağılımı" ölçümü 0 € ile yapılabilir (§6).

## 1. Kodlanabilir tasarım

### 1.1 Sünme serisi kaynakları

| Kaynak | Kapsam | Erişim (12 Kasım 2026 denemesi) | Not |
|---|---|---|---|
| USGS sünme ölçer arşivi (K. ve Orta Kaliforniya), OFR 2024-1011, 10.3133/ofr20241011 | 47 istasyon: Calaveras 4, Hayward 10, San Andreas 33; ilk gözlem 1966–2009 | **Açık.** İndirme sayfası 200 döndü; 235 dosya bağlantısı (10MIN 30, DAY 26, MIC 40, HDR 29). Bir DAY dosyasına HEAD isteği 200 döndü (46 KB, son değişiklik 2020-07-09). 300 baytlık kısmi istek de 206 döndü ve geçerli gzip içerik geldi. İçerik açılmadı. | 10MIN dosyaları her gün güncelleniyor (son değişiklik 2026-11-11), yani 2026 verisi içeriyor. Sınavda 2025-12-31'de kırpılmalı. Sayfaya göre COVID döneminde bakım aksamış, boşluklar var. SJN1'in boylamı sayfada 0 yazıyor. |
| İsmetpaşa duvar + sünme ölçer, Bilham 2016, 10.1002/2016jb013394 | 1957 duvarı, 1969'dan beri seyrek ölçüm, 2014+ sünme ölçer | Açık değil (makale ekinde olabilir, okunmadı) | Seyrek, yıl ölçekli değil |
| İsmetpaşa InSAR (ERS/Envisat/ALOS): Çakır 2005, 10.1016/j.epsl.2005.06.044; 10.1002/2014gc005307; Kaneko 2013, 10.1029/2012jb009661 | ≈ 1992–2010 | Açık değil | Yıllık örnekleme ancak ortalama hız düzeyinde |
| Chihshang sünme ölçerleri, 10.1016/j.crte.2005.04.018 | 1998+ (ve 1986–1997 aralıklı) | Bilinmiyor | Yayında bir tek olay iddiası var: 1999–2003 arasında sünme hızı azaldı, ardından 2003 Chengkung Mw 6,6 geldi |
| Xianshuihe S1 InSAR, Tong & Chen 2024, 10.1093/gji/ggae310; Li & Bürgmann 2021, 10.1029/2020jb021406 | 2014–2021 | Açık değil | Kesim boyunca hız 30 → 40 → 5 mm/yıl değişiyor (not JG-2) |
| Aceh ALOS + S1, Salman 2026, 10.1038/s43247-026-03951-9 | 2007–2010 ve 2017–2023 (arası boş) | Bilinmiyor | 2013 olayları boşluğa düşüyor |
| Leyte ALOS, Fukushima 2019, 10.1186/s40623-019-1096-5 | 2006–2011 | Bilinmiyor | |
| El Pilar ALOS, Pousse-Beltran 2016, 10.1002/2016jb013121 | 2007–2011 | Bilinmiyor | |
| Chaman S1, Dalaison 2021, 10.1029/2021jb021935 | 2014–2019 | **Açık** (Zenodo 10.5281/zenodo.5221208) | Bu kesimde olay yok |
| İzmit FLATSIM, Neyrinck 2024, 10.1016/j.epsl.2024.119104 | 2016–2021 | Bilinmiyor | Postsismik sünme |
| Marmara Kumburgaz akustik, Yamamoto 2019, 10.1029/2018gl080984 | 2017–2019 | Kısmen | 2 yıl; ≥ 5 yıl şartını sağlamıyor |
| COMET LiCSAR (Sentinel-1) | 2014 sonu/2015+, küresel çerçeveler | **Açık.** Ürün dizini 200 döndü. | Hazır sünme serisi değil; çerçeve başına onlarca GB, LiCSBAS ile işlenmesi gerekiyor. Deniz altını görmez. |
| NISAR | GUNW 2026-08-15'te başladı (defter AV-3) | Açık | 12 Kasım 2026 itibarıyla ≈ 3 ay. ≥ 1,5 yıl ancak 2028 başında, ≥ 5 yıl 2031'de birikir. 2026 olayları zaten kör. |

### 1.2 Olay seçimi

- ComCat, derinlik ≤ 30 km, bitiş 2025-12-31.
- Ana tanım M ≥ 6; varyant M ≥ 5,5.
- Uzaklık:
  - nokta ölçerlerde (sünme ölçer, duvar) ölçere ≤ 50 km (ana) ya da ≤ 30 km;
  - alan serilerinde (InSAR) kesim izine aynı eşikler.
- Kayıt koşulu: seri olaydan en az 5 yıl önce başlamış ve olay anını kapsıyor olmalı. Boşluklu seriler (Aceh) dönem
  dönem ayrı sayılır.
- Mekanizma ana tanımda serbest. Doğrultu atımlı alt küme bilgi satırıdır; TR-2 sınıflaması kullanılır (Mw, ≤ 25 km,
  |rake| ≤ 30° ya da ≥ 150°).

### 1.3 Ölçü

- Her (seri, olay) çifti için:
  - v_önce: olaydan önceki 12 ayın sünme hızı, en küçük kareler eğimiyle. Pencere olaydan 30 gün önce kapanır.
    Böylece öncü ve ön şoklar dışarıda kalır; ayrıca bilgi satırı olarak tutulur.
  - v_taban: ondan önceki 48 ayın hızı.
  - ΔV = v_önce − v_taban.
- Normalleştirme, TR-11'deki taban fikriyle aynı:
  - Aynı serinin olaysız pencerelerinde aynı ΔV hesaplanır. Olaysız pencere: ± 2 yıl içinde 50 km'de M ≥ 5,5 yok ve
    1 yıl içinde 1000 km'de M ≥ 7 yok. İkinci koşul uzak tetikleme kirliliğine karşıdır (Salman 2026, Vavra 2026).
  - r = olaysız pencerelerdeki |ΔV| değerlerinin, olay öncesi |ΔV|'den küçük olanlarının oranı. İki yanlıdır:
    hızlanma ve yavaşlama birlikte sayılır. Chihshang iddiası yavaşlama yönünde.
- Nokta ölçerlerde mevsimsel ve yağış etkisi, komşu istasyonun aynı penceredeki ΔV'siyle ortak-kip düzeltmesi
  yapılarak giderilir.

### 1.4 Kontrol

- Birinci kontrol: olaysız pencere tabanı. Bu, yanlış alarm oranını verir.
- Yer değiştirme kontrolü: olay tarihi aynı serinin olaysız tarihlerine 1000 kez kaydırılır.
- Negatif kontrol: olaydan ≥ 200 km uzaktaki bir serinin aynı penceredeki r değeri. Bu, ortak-kip ve küresel
  etkileri ölçer.

### 1.5 Bağımsızlık birimi

- TR-2 kümeleri (300 km, 1 yıl).
- Her kümeden zamanca ilk olay alınır, en yakın ve en uzun seriyle eşleştirilir.

### 1.6 Hüküm satırı

- Ana ölçü: ortalama r. Tek yanlı test, H1: r̄ > 0,5, α 0,05.
- İkincil ölçü: "olay öncesi |ΔV| olaysız tabanın üst %10'unda" isabet sayısı. Sınama binomla yapılır, p0 = 0,10.
- Hüküm şablonu: "yıl ölçekli sünme hızı değişimi M ≥ 6 öncesinde olaysız tabandan büyük / ayırt edilemez" (r̄ ve
  95% aralığı, küme bootstrap'i).

### 1.7 Güç kapısı: K ≥ 20 (gerekçe)

| K | Güç, sıra ölçüsü H1 r ~ Beta(a,1) (a = 0,4 / 0,5 / 0,7) | İkili, p0 0,10: kritik | Güç p1 = 0,3 / 0,4 |
|---|---|---|---|
| 5 | 0,51 / 0,37 / 0,18 | 3 | 0,16 / 0,32 |
| 10 | 0,76 / 0,57 / 0,26 | 4 | 0,35 / 0,62 |
| 15 | 0,89 / 0,72 / 0,33 | 5 | 0,48 / 0,78 |
| **20** | **0,95 / 0,82 / 0,39** | 5 | **0,76 / 0,95** |
| 30 | 0,99 / 0,93 / 0,51 | 7 | 0,84 / 0,98 |

Not: Beta(a,1) burada küçük r'yi H1 kabul eden bir modeldir. TR-10'da yön r > 0,5'tir; simetrik olduğu için güç
aynıdır.

K = 20'de orta büyüklükte bir etki için (a = 0,5 ya da p1 = 0,3) güç ≥ 0,76. K = 10'da bu güç 0,35–0,57'ye düşer.
TR-1 ve TR-11'in kapısı da 20'dir. Bu turda kaba sayımlar ayrıntılı sayımda hep küçüldüğü için kapıya pay bırakılmalı.

## 2. Sayım (ComCat, bitiş 2025-12-31; olay havuzu, kesim kutularında M ≥ 5,5 ve ≤ 30 km, 322 olay)

| Seri türü | R ≤ 30 km, M ≥ 5,5 | R ≤ 30, M ≥ 6 | R ≤ 50, M ≥ 5,5 | **R ≤ 50, M ≥ 6** | R ≤ 50, M ≥ 6, doğrultu atımlı Mw |
|---|---|---|---|---|---|
| USGS sünme ölçerleri (açık) | N 4 / K 4 | 1 / 1 | 11 / 6 | **4 / 3** | 2 / 2 |
| Yayımlanmış seriler (hepsi) | 9 / 5 | 6 / 5 | 18 / 8 | 9 / 7 | 5 / 4 |
| Yayımlanmış ve sürekli | 8 / 4 | 5 / 4 | 17 / 7 | 8 / 6 | 5 / 4 |
| USGS + yayımlanmış | 13 / 9 | 7 / 6 | 29 / 14 | 13 / 10 | 7 / 6 |
| LiCSAR üst sınırı (S1 2015+, olaylar 2020+, Marmara hariç) | 35 / 9 | 14 / 9 | 40 / 9 | 14 / 9 | 8 / 7 |
| **Hepsi** | 42 / 16 | 18 / 13 | 58 / **21** | **23 / 17** | 12 / 11 |

Her hücre N olay / K bağımsız küme.

USGS ve yayımlanmış seriler kapsamındaki M ≥ 5,5 olaylar (≤ 50 km):

- **Kaliforniya:**
  - Coyote Lake 1979 (ML 5,8);
  - Livermore 1980 (5,8);
  - Coalinga 1983 (ML 6,7, bindirme);
  - Morgan Hill 1984 (ML 6,2);
  - Huron 1985;
  - Tres Pinos 1986;
  - East Foothills 1986;
  - Loma Prieta 1989 (Mw 6,9, verev);
  - Parkfield 2004 (Mw 5,97; sünme ölçerlere 1,6 km);
  - Napa 2014 (Mw 6,0; Hayward ölçerine 25 km).
- **Türkiye:** Orta 2000 (Mwc 6,0). İsmetpaşa InSAR kesimine 25 km, duvara 38 km uzakta. İsmetpaşa'nın InSAR serisi
  1992'den başlıyor; duvar ölçümü seyrek. ComCat mekanizmasına göre doğrultu atımlı değil.
- **Tayvan (Chihshang ölçerine ≤ 50 km):**
  - 2003 Chengkung Mw 6,8 (bindirme);
  - 2006 (iki olay), 2008, 2010, 2016;
  - 2022 Chihshang dizisi (6,5, 6,9 ve artçılar);
  - 2022-03 (6,7);
  - 2025-06, 2025-12.

Seri bitişi doğrulanamadığından Chihshang olaylarının 2003 sonrası kısmı koşulludur.

LiCSAR üst sınırına giren olaylar (S1 2015+, ≥ 5 yıl → 2020+):
- Elazığ 2020 (Mw 6,7);
- Masbate 2020 (6,6) ve 2023 (6,1);
- Luding 2022 (6,6);
- Kale 2024 (6,0);
- Çelikhan 2023-02-06 (mb 6,0). Kahramanmaraş Mw 7,8'in gölgesinde, ama bu kutu-küme kuralıyla yakalanmadı;
- Tayvan 2021–2025 olayları.

Marmara 2025 LiCSAR'dan çıkarıldı, çünkü iz deniz altında.

### 2.1 Kapı

| Tanım | K | Kapı (K ≥ 20) |
|---|---|---|
| Ana: R ≤ 50, M ≥ 6, bütün seri türleri | **17** | **GEÇMEZ** |
| Aynısı, doğrultu atımlı Mw | 11 | GEÇMEZ |
| Bugün açık ve sürekli seri (USGS), R ≤ 50, M ≥ 6 | 3 | GEÇMEZ |
| USGS + yayımlanmış, R ≤ 50, M ≥ 6 | 10 | GEÇMEZ |
| Varyant: R ≤ 50, M ≥ 5,5, bütün seri türleri | 21 | Eşiğin üstünde, ama ana tanım değil (§0) |

Defterdeki kaba "N 5–8" ifadesi, bugün işlenmiş ve erişilebilir seri için doğru (K 3–10). Bütün olası seriler
sayılınca tavan 17.

## 3. Maliyet ve iş yükü

- Para: 0 €.
- USGS bölümü hafif. Yaklaşık 50 dosya ve birkaç MB; okuma, kırpma, ortak-kip düzeltmesi ve sıra hesabı 1–2 gün.
- Yayımlanmış serilerin çoğu açık değil. Yazarlardan istenmesi gerekir; süresi belirsiz.
- LiCSAR bölümü ağır: yaklaşık 9 küme için 9–12 çerçeve, çerçeve başına onlarca GB, LiCSBAS zaman serisi. Toplam
  1–2 hafta işlem ve insan zamanı. Sünme sinyali için çerçeve başına fay ötesi profil çıkarma ayrıca gerekir.

## 4. En büyük üç risk

1. **Olaysız pencere yok, nedensellik ters.** Sünme hızı değişimlerinin baskın açıklaması başka depremlerin
   tetiklemesi ve postsismik sönümdür (Salman 2026, Vavra & Fialko 2026, Liu 2025; not JG-2). Tayvan ve Kaliforniya
   kümelerinde 5 yıllık ön pencereler önceki olayların izleriyle dolu. Bu, TR-1'deki kapanış nedeninin aynısı:
   darboğaz olay değil, temiz karşılaştırma penceresi. Çelikhan 2023 gibi büyük olay gölgesindeki olaylar kutu-küme
   kuralıyla yakalanmıyor.
2. **Güç ve heterojenlik.** K ana tanımda 17, doğrultu atımlıda 11. Örneklem bindirme/verev ağırlıklı (Tayvan,
   Coalinga, Loma Prieta). Seri türleri ayrı ölçü düzeylerinde: nokta sünme ölçerinin 10 dakikalık verisi ile
   InSAR'ın kesim ortalaması aynı r ölçüsüne konunca birim varyansı farklı olur.
3. **Veri erişimi ve sızıntı.**
   - Gerçekten açık ve sürekli olan tek kaynak USGS. Chihshang'ın bitişi doğrulanamadı.
   - LiCSAR serileri henüz türetilmedi ve işleme seçimleri (referans, profil genişliği) sonucu görmeden donmalı.
   - USGS 10MIN dosyaları 2026 verisi içeriyor ve kırpılmalı.
   - Chihshang'daki "olay öncesi yavaşlama" tek olaylı bir iddia. Gerekçe olayıdır, puanlanmamalı.

## 5. Defterle örtüşme (`kayit.py ara`: TR-10, sünme, AV-3, S-7, kilitlenme)

- **AV-3 (aday)**: NISAR + Sentinel-1 ile İzmit/Ganos'ta sünme değişimi. Marmara'ya yönelik ölçümdür; TR-10 ise
  küresel sınavı. Yeniden açma şartı AV-3 ile ortak: NISAR ≥ 1,5 yıl. TR-10'un ≥ 5 yıl şartı NISAR için 2031'e
  denk düşer.
- **S-7 (ayırt edilemez)**: K. Kaliforniya 2004–2014, tekrarlayan depremlerle ölçülen geçicilerin bilgi kazancı
  −0,06 ± 0,12 nat (N 30). TR-10'un USGS bölümü aynı bölge ve aynı fiziksel nicelik (sığ sismik olmayan kayma);
  bağımsız bir doğrulama sayılmaz. Bu yüzden USGS bölümü S-7'ye karşı ancak "farklı ölçer" bilgi satırı olur.
- **TR-1 (güç yok) ve TR-11 (ölçek)**: aynı mantık, GNSS yerine sünme. TR-11 dersi doğrudan aktarılabilir: önce
  olaysız taban.
- **TK-E1 (elendi), FA-6 (elendi)**: Marmara geçicileri ve hazırlık evresi göstergeleri. Aynı mekanizma ailesi; S-7
  gerekçesiyle kapandılar.
- **DK-5 (güç yok)**: sünen kesimlerde 9 kesim ve 16 olay. Aynı kesim evreni, aynı mertebede olay sayısı.

## 6. Yeniden açma şartı (kapının geçmesi için gereken veri)

Aşağıdakilerden biri gerçekleşirse kapı yeniden sayılır:

- (a) Sünen kesimler için açık ve sürekli Sentinel-1 sünme serileri türetilir (LiCSAR/LiCSBAS ya da yayımlanmış
  küresel bir sünme kataloğu) ve olaydan ≥ 5 yıl önce başlayan doğrultu atımlı M ≥ 6 kümeleri 20'ye ulaşır.
  Bugünkü tempo LiCSAR kapsamında 2020–2025 arası 7 doğrultu atımlı küme, yani yılda ≈ 1,2. Bütün serilerle
  doğrultu atımlı K 11'den 20'ye kendiliğinden çıkmak ≈ 2033'e kadar sürer.
- (b) NISAR serisi ≥ 5 yıl olur (≈ 2031). Ara şart ≥ 1,5 yıl, AV-3 ile aynı.
- (c) Yayımlanmış serilerin (Chihshang, Xianshuihe, Aceh, Leyte, El Pilar, İsmetpaşa) sayısal verileri açılır. Bu
  tavanı ana tanımda 17'nin üstüne taşımaz, ama doğrulanmış K'yi 10'dan ≈ 15'e çıkarır.
- Olay gerektirmeyen ara ölçüm (TR-11 benzeri, seçim Erdem'in): USGS'nin 47 sünme ölçerinde 1 yıllık sünme hızı
  değişiminin olaysız taban dağılımı. Bu ölçüm "hangi büyüklükte bir sünme değişimi yıl ölçeğinde olağandışıdır"
  sorusunu bugün 0 € ile yanıtlar. Marmara'da gelecekteki NISAR/akustik serisi için bir eşik verir. İçerik okunmadan
  kapsam: 1966–2025, 33 San Andreas, 10 Hayward, 4 Calaveras istasyonu.

## 7. Körlük beyanı

- ComCat sorguları kesim kutularıyla sınırlandı; hepsi ≤ 2025-12-31 bitişli. Kod `tr2_sayim.sorgu` ile assert eder.
- USGS'den yalnız indirme sayfası (istasyon listesi) alındı. Ek olarak bir DAY dosyasına HEAD isteği ve 300 baytlık
  kısmi istek yapıldı; içerik açılmadı.
- LiCSAR için yalnız ürün dizinine tek bir 200 kontrolü yapıldı.
- Marmara GNSS indirilmedi.
- Hiçbir sünme hızı ya da ΔV hesaplanmadı.
