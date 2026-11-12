# TR-13 sayım ve güç kapısı: büyük doğrultu atımlı depremlerden 2–3 yıl önce sismisite yerelleşmesi

Tarih: 12 Kasım 2026. Durum: **0 € sayım + yapay güç hesabı (ön kayıt değil)**. Gerçek katalogda hiçbir yerelleşme
ölçüsü (V(q), Gini) hesaplanmadı. Yalnız olay sayısı, Mc ve kümesizleştirilmiş sayı yazıldı. Sorguların bitişi
≤ 2025-12-31 (kod assert eder). İndirilen en geç olay 2025-12-11. Yalnız ana şok **öncesi** pencereler indirildi.
2026 verisi yok, mutlak İstanbul olasılığı yok.

Kod: `kayit/turetme/tr13/tr13_sayim.py` (ana şoklar, katalog, sayım), `tr13_guc.py` (ETAS üreteci ve güç),
`tr13_ozet.py`. Özet: `tr13_ozet.json`. Güç çıktıları: `tr13_guc_*.json`. Ham veri ve sha256:
`tr13_ham_sha256.txt` (arşiv `/mnt/project-files/turetme/tr13-ham/`, sha256 2e11e7d2…).

## 0. Hüküm

**Kapı SINIRDA. Ana tasarımda geçmiyor, yalnız üst sınırda geçiyor. En olası sonuç "güç yok".**

- **Örneklem.** 1980–2025'te 1175 sığ doğrultu atımlı Mw ≥ 6,0 ana şok var. Bunların 348'i M ≥ 6,5. Ana şok
  öncesi 3 yılda, 2L yarıçaplı dairede ≥ 50 kümesizleştirilmiş arka plan olayı olan küme sayısı:
  - Önce-pencere temiz (yani [t − 4 y, t − 2 g] içinde M ≥ 6 yok): **K = 25** (M ≥ 6,5) ve **31** (M ≥ 6,0).
    Bu sayılar tam sayımdır. Kapı (≥ 20) bu üst sınırda geçiyor.
  - Ölçünün kendisi bir referans dönemi ister. [t − 10 y, t − 3 y) aynı Mc ile dolu olmalıdır. Bu şart eklenince
    K **8–12** (M ≥ 6,5) ve **13–17** (M ≥ 6,0) olur. Aralık Mc toleransına (0,1 / 0,3) bağlıdır.
  - Eşleşik depremsiz kontrol penceresi de istenirse K **5** ve **9** olur. Kapı geçmiyor.
- **Güç.** Ölçü, kesirsel alan V(0,5)'in aynı bölgenin referans döneminden çekilen alt örneklere göre z'sidir. ETAS
  sentetiklerinde GK74 kümesizleştirmesiyle bu ölçünün tek pencerelik yanlış alarm oranı %13–16'dır (anma değeri
  %5). Yoğun katalogda bu oran %25–37'ye çıkar.
  - Gücün 0,8 olması için, önce-penceredeki arka plan olaylarının **f ≈ %19–20'sinin** gelecekteki kırık
    bandına (2 km) toplanması gerekir. Bu, K = 20 ve bölge başına 50–100 arka plan olayı içindir. Standartlaştırılmış
    fark d ≈ 0,6'dır.
  - Elde olan gerçekçi K ≈ 12–17'de gereken f ≈ %23–28'dir.
  - İdeal (kâhin) kümesizleştirmeyle gereken f %10–14'e iner.
  - Bölge başına arka plan sayısı ≳ 150'ye çıkınca GK74 hem sayıyı doyuruyor hem sinyali siliyor. O durumda hiçbir
    f'de güç 0,8'e ulaşmıyor.
- **ETAS'ın kendi etkisi.** Sinyalsiz uzun ETAS'ta (6000 y) M ≥ 5,5 olaylardan önceki pencereler yerelleşme
  göstermiyor. Fark rastgele pencerelere göre +0,22 ± 0,11 sd, yani hafif yayılma yönünde. ETAS sahte bir öncül
  yerelleşme üretmiyor. Ama yanlış alarm oranı anma değerinin 2,5–3 katı. Bu yüzden eşik ETAS'tan kalibre
  edilmelidir.
- **Etki büyüklüğünün makullüğü doğrulanamadı.** BZ20'nin tam metni yayıncıda 403 döndü. Kesirsel alan azalmasının
  büyüklüğü, eşik ve yanlış alarm oranı okunamadı. f ≈ 0,2, kırık bandındaki arka plan oranının 3 yıl boyunca
  ≈ 2,5 katına çıkması demektir. Bunun gerçek depremlerde olağan olduğunu gösteren bir sayı bulunamadı.
- **Proje dersi.** Kaba sayımlar ayrıntılı sayımda 3–5 kat küçüldü (ZİNCİR, beş kez). Burada önce-pencere tam
  sayıldı, ama referans dönemi ISC olaylarında yalnız 90 günlük örnekten denetlendi. Gerçek doluluk büyük olasılıkla
  K'yi ana tasarımın da altına indirir.

Aday elenmedi. Yeniden açma şartı §8'de.

## 1. Soru ve neyi ölçmediği

Ben-Zion ve Zaliapin (2020, BZ20) şunu öneriyor: büyük depremlerden ≈ 2–3 yıl önce arka plan sismisitesi ileride
kırılacak fay çevresinde yerelleşir; kesirsel alan azalır. TR-13 sorusu: Mw ≥ 6,5 (gerekirse ≥ 6,0) sığ doğrultu
atımlı ana şoklardan önceki 3 yılda yerelleşme ölçüsü, eşleşik depremsiz pencerelerden ve ETAS sentetiklerinden
ayrışıyor mu? Yanlış alarm oranı da birlikte sorulur.

Bu belge yalnız şunu sorar: soru bugünkü açık veriyle sınanabilir mi? Bunun için iki şey sayılır. Biri, yeterli
olayı olan bağımsız küme sayısı K. Öteki, bu K ile görülebilecek en küçük etki. Bir olasılık terimi önermez.
Marmara'ya terim ancak küresel sınav geçerse gelir. Bu sayım o sınavın kurulabilirliğini ölçer.

## 2. Kaynak tanım (BZ20) ve sonraki çalışmalar

### 2.1 Doğrulanan (OpenAlex özetleri; `kayit/oa.py ozet`)

- **BZ20, GJI 223 (1), 561–583, doi:10.1093/gji/ggaa315.** Açık erişim yok. Üç tamamlayıcı analiz var:
  - (i) arka plan olaylarının ürettiği kaya hasarı;
  - (ii) arka plan sismisitesinin "evolving occupied fractional area" ölçüsü;
  - (iii) olayların kümelere "coalescence"ı.
  - (i) ve (ii) kümesizleştirilmiş katalog kullanır, (iii) bütün katalogu.
  - Bulgu: (ii) Landers 1992, Hector Mine 1999, El Mayor–Cucapah 2010, Ridgecrest 2019 ve Düzce 1999 (hepsi
    M > 7) öncesinde **2–3 yıl önce yerelleşme** gösteriyor. (iii)'te olaylar son 1–2 yılda kümeleşiyor.
  - Karşı örnek: Parkfield 2004 (M 6, sünen kesim) öncesinde tersine "delocalization" var.
  - Örneklem: **5 ana şok + 1 karşıt örnek**.
- **EGU 2020 özeti (doi:10.5194/egusphere-egu2020-12056).** Ölçünün en açık tarifi buradadır:
  - "temporal evolution of the fractional volume 0 ≤ V(q) ≤ 1 occupied by the fraction q of active voxels";
  - sayılan olaylar: kümesizleştirilmiş "mainshocks";
  - yöntem: ROC yaklaşımı; ayrıca kayan pencere yoğunluğunun zaman ortalamasına göre Gini katsayısı G;
  - anlamlılık: "reshuffled catalogs" ile, yani ETAS ile değil.
  - Bölgeler: Güney Kaliforniya, Parkfield, İzmit–Düzce çevresi. Doğu Kaliforniya'da dört yerelleşme döngüsü
    Landers, Hector Mine, EMC ve Ridgecrest ile hizalı.
- **EGU 2021 (…-egu21-14086).** Alaska'daki M 7,9 olaylar örnekleme eklenmiş.
- **EGU 2023 (…-egu23-9874).** Güney Kaliforniya'da M > 2 arka plan, Alaska'da M > 4. Yerelleşme–yayılma döngüleri
  M 7'lerden 2–4 yıl önce. Analiz "regional scale, without posterior selection of the examined areas".
  - Önemli: 2–10 yıl önce geniş hacimde göreli etkinleşme var. Bu hacim **ana şok dış merkezini içermeyebilir**.
    Ardından 2–3 yıl önce belirgin bir sönme geliyor ("Mogi donut"a benzer).
  - Yani yerelleşmenin yeri kırık zonu olmak zorunda değil. Bu, ölçünün tanımında açık bir serbestliktir (§7).
- **EGU 2022 (…-egu22-3136) ve Zaliapin & Ben-Zion 2022, SRL (doi:10.1785/0220210127).** ROC çerçevesi
  kümelenme ölçüsü olarak kullanılıyor; ETAS sentetikleri de inceleniyor. Kümesizleştirme, ince etkilerin
  sinyal/gürültü oranı için gerekli bulunuyor. Önerilen yöntem en yakın komşu kümesizleştirmesidir (Zaliapin &
  Ben-Zion 2013). Özetlerde **ETAS'a karşı bir yerelleşme yanlış alarm oranı yok**.
- **Kato & Ben-Zion 2021, Nat. Rev. Earth Environ. (doi:10.1038/s43017-020-00108-w).** Derleme; OpenAlex'te özet
  yok. Projenin notunda "a few years before" ifadesiyle aynı çerçeve var. Nicel değer yok.

### 2.2 Doğrulanamayan (tam metin 403; aşılmadı)

- Voksel ya da hücre boyu, q değeri, kayan pencere uzunluğu, büyüklük eşiği, kümesizleştirme parametreleri ve
  "reshuffled" anlamlılık düzeyi okunamadı. Bölge sınırları ve yerelleşme azalmasının büyüklüğü de okunamadı.
- Denenen yollar: academic.oup.com (makale ve PDF) 403. Unpaywall 422. Semantic Scholar "CLOSED". Yazar sayfası
  bölüm ana sayfasına yönlendirdi. UNR sayfası 404/502. ADS 405.
- Bu yüzden §3–4'teki ölçü BZ20'nin **gerekçeli yeniden kurulumudur, aynısı değildir**.

### 2.3 Sonraki çalışmalar ve eleştiri

- OpenAlex'te BZ20'ye atıf yapan 101 iş var.
  - Doğa katalogunda aynı ölçüyü bağımsız olarak sınayan bir iş bulunamadı.
  - Bulunanlar laboratuvar yerelleşmesi (McBeck vd. 2021, 2023), sentez ve derlemeler (Martínez-Garzón & Poli 2024;
    33 dizi), makine öğrenmesiyle tek olaylı öncül iddiaları ve ilgisiz işler.
  - Makine öğrenmesi işleri: Girona & Drymoni 2024, Ridgecrest ve Anchorage'dan 3 ay önce. Karimpouli vd. 2026,
    beş olay, "when present". Kwiatek vd. 2023, Kahramanmaraş öncesi aylar süren geçici.
- Rundle vd. 2023, EA (doi:10.1029/2022ea002521): özet yalnız "Yes". İçerik okunmadı.
- Yazarlardan bağımsız, açık bir eleştiri ya da yanlış alarm sınaması bulunamadı. Bu bir "yokluk kanıtı" değil,
  OpenAlex başlık/özet taramasının sınırıdır.

## 3. Örneklem sayımı (kodla, açık katalog, anonim, genel User-Agent)

### 3.1 Kurallar

- **Ana şok adayı (ComCat).** 1980-01-01 → 2025-12-31, M ≥ 6,0, derinlik ≤ 30 km. Moment tensörü ya da odak
  mekanizması ürünü olmalı. Toplam 3348 aday. Elemeler:
  - büyüklük türü Mw değil: 97;
  - mekanizma yok: 1;
  - doğrultu atımlı değil: 1801. Ölçüt TR-2 `ss_mi`: herhangi bir düğüm düzleminde |rake| ≤ 30° ya da ≥ 150°.
    Mekanizmalar TR-2 anlık görüntüsünden geldi, 455'i yeni indirildi.
  - **artçı/öncü gölgesi: 274.** Önceki 1 yılda, kendisinden büyük ya da eşit bir olayın 3 L(M_büyük) içinde
    kalan olaylar. Havuz: ComCat M ≥ 5,5, derinlik ≤ 70 km, 1970+, 21 196 olay.
  - Kalan: **1175 ana şok** (M ≥ 6,5: 348; M ≥ 7: 95).
  - Not: Düzce 1999 bu kuralla İzmit'in artçısı sayıldı ve düştü. BZ20 onu ana şok sayıyor. Parkfield 2004
    ComCat'te M < 6,0 olduğu için listede yok.
- **Bölge.** Dış merkezde yarıçapı R = max(2 L, 50 km) olan daire. L, Wells–Coppersmith doğrultu atımlı kırık
  boyudur. Derinlik ≤ 40 km (30 km + konum payı).
- **Pencereler.**
  - Önce-pencere [t − 3 y, t). BZ20'deki "2–3 yıl" buna karşılık gelir.
  - Referans dönemi [t − 10 y, t − 3 y).
  - Sayım tablosu "önceki ≥ 5 y" için ComCat'te ayrıca N5 de yazıldı.
- **Mc.** Bölgedeki olayların MAXC + 0,2'si; ≥ 50 olay gerekir (20–49 olayda MAXC + 0,3). Seçenekler: Mc, Mc + 0,5,
  max(Mc, 3,0), max(Mc, 4,0), max(Mc, 4,5).
- **Kümesizleştirme.** GK74 pencereleri, öncüler dahil. ComCat'te 10 yıllık R_ind = max(3 L, 75 km) dairesinde
  uygulandı; ISC tam sayımında 3 yıllık R dairesinde.
- **Kataloglar.** Kalifornia SCEDC/NCEDC kataloğu ComCat'in içinde (ci/nc).
  - ComCat: 1175 olayın hepsi, [t − 10 y, t), M ≥ 1,0. 912 olayda R içinde 5 yılda 20'den az olay var; Mc
    kestirilemedi.
  - ISC FDSN: 1157 olay, 90 günlük örnek pencere (merkez t − 2 y). JMA, CWB, ISK (KOERI), AFAD, NOA ve GUC
    katkılarını taşır. JMA'yı da ISC üzerinden aldık.
  - Bölgesel örnekler: EMSC 33, GeoNet 29, INGV 1.
  - Örnekten tahmini N3bg ≥ 25 olan 61 + 6 olayda önce-pencere **tam** indirildi (ISC 60, GeoNet 5, EMSC 1).
  - Bu tam indirmelerin referans dönemi için 90 günlük örnek alındı (merkez t − 6,5 y).
  - Erişim: KOERI zeqdb ve AFAD bu sayımda doğrudan sorgulanmadı. TR-6 Ek 1.2'ye göre KOERI açık ama yavaş, AFAD
    tarihsel sorguya boş dönüyor. JMA yıllık dosyaları açık. CENC kayıt istiyor, atlandı.
- **Arka plan payı.** ComCat tam sayımlarında GK74 sonrası arka plan payı medyan f_bg = 0,204. Bu değer yalnız
  örnekten tahminde çarpan olarak kullanıldı. Tam sayımlar kendi kümesizleştirmesiyle sayıldı.
- **Örnek ile tam sayım uyumu** (aynı olaylar, 61 ISC olayı). Tam/örnek oranı medyan 0,69, %10–%90 aralığı
  [0,05, 2,0]. N3bg ≥ 50 eşiğinde örnekten 38, tamdan 35 olay geçiyor. Tek olay düzeyinde tahmin iki kat hatalı
  olabilir. Örnek N3bg < 25 olup tam sayımda ≥ 50 çıkacak olay olasılığı küçük ama sıfır değil; sayılmadı.
- **Bağımsız küme.** İki ana şokun daireleri örtüşüyorsa (uzaklık ≤ R_i + R_j) ve aralarındaki süre ≤ 10 yılsa
  (önce-pencereleri örtüşür) aynı kümeye girerler (tek bağlantı). 1175 ana şok 538 küme eder; M ≥ 6,5'te 221 küme.
  Örnek: Güney Kaliforniya 1986–1999 (N. Palm Springs, Elmore Ranch, Superstition Hills, Joshua Tree, Landers,
  Hector Mine) tek kümedir.
- **Temiz önce-pencere.** Dairede [t − 4 y, t − 2 g] içinde M ≥ 6,0 yok. 2 günlük kesme, Ridgecrest ve Kumamoto
  tipi hemen öncesindeki öncüleri tutar.
- **Referans şartı.** Mc_ref ≤ Mc_önce + tol ve N_ref,bg ≥ 2 × eşik. tol = 0,1 ya da 0,3. ComCat'te Mc_ref,
  [t − 10 y, t − 5 y)'den alındı. ISC/GeoNet/EMSC'de 90 günlük örnekten.
- **Eşleşik depremsiz kontrol penceresi.** Bitişi t_c = t − 6k y (k = 1…7) olan ve t_c − 10 y ≥ 1975 şartını
  sağlayan pencereler. [t_c − 3 y, t_c + 3 y] içinde dairede M ≥ 5,5 olmamalı. Yalnız havuzdan sayıldı; bu
  pencerelerin katalog doluluğu **ölçülmedi**.

### 3.2 Sayım tablosu (bağımsız küme K; N3bg = önce-pencerede [t − 3 y, t) GK74 sonrası olay)

Hücre biçimi: K (bütün) / temiz / temiz + referans (tol 0,1 ; 0,3) / temiz + kontrol / temiz + referans + kontrol.

| M eşiği | Mc seçeneği | N3bg ≥ 25 | N3bg ≥ 50 | N3bg ≥ 100 | N3bg ≥ 200 |
|---|---|---|---|---|---|
| ≥ 6,5 | Mc | 41 / 29 / 13;17 / 21 / 9 | **36 / 25 / 8;12 / 18 / 5** | 29 / 21 / 7;9 / 14 / 4 | 18 / 13 / 5;7 / 7 / 3 |
| ≥ 6,5 | Mc + 0,5 | 33 / 22 / 14;15 / 15 / 7 | 26 / 19 / 11;11 / 12 / 5 | 17 / 12 / 6;6 / 7 / 3 | 11 / 6 / 6;6 / 3 / 3 |
| ≥ 6,5 | max(Mc, 3,0) | 36 / 22 / 17;18 / 12 / 8 | 24 / 12 / 9;10 / 5 / 3 | 11 / 4 / 2;2 / 3 / 1 | 4 / 1 / 1;1 / 0 / 0 |
| ≥ 6,5 | max(Mc, 4,0) | 13 / 1 / – / 0 / – | 7 / 0 | 2 / 0 | 2 / 0 |
| ≥ 6,0 | Mc | 52 / 39 / 19;23 / 31 / 14 | **40 / 31 / 13;17 / 24 / 9** | 32 / 24 / 11;13 / 18 / 8 | 20 / 15 / 6;8 / 9 / 4 |
| ≥ 6,0 | Mc + 0,5 | 37 / 28 / 19;20 / 21 / 12 | 29 / 22 / 14;14 / 15 / 8 | 19 / 14 / 7;7 / 9 / 4 | 11 / 6 / 6;6 / 3 / 3 |
| ≥ 6,0 | max(Mc, 3,0) | 36 / 23 / 19;20 / 13 / 9 | 24 / 12 / 9;10 / 5 / 3 | 11 / 4 / 2;2 / 3 / 1 | 4 / 1 / 1;1 / 0 / 0 |
| ≥ 6,0 | max(Mc, 4,0) | 16 / 1 | 7 / 0 | 2 / 0 | 2 / 0 |

Okuma:
- **Sabit eşikle global katalog yetmiyor.** Mc ≥ 4,0 sabit eşikte, yani küresel ComCat/ISC tamlığında, temiz küme
  0–1'dir. Soru ancak yerel ağı yoğun bölgelerde sorulabilir: Kaliforniya ve Alaska (ComCat), Japonya, Tayvan,
  Yunanistan, Doğu Anadolu ve Yeni Zelanda (ISC/GeoNet/EMSC).
- **Önce-pencere kirliliği eliyor.** M6 ana şoklar M6'lı bölgelerde oluyor. Temizlik şartı K'nin üçte birini
  düşürüyor (36 → 25).
- **Referans dönemi asıl darboğaz.** Ağlar zamanla iyileştiği için referans döneminin Mc'si önce-pencereninkinden
  yüksek kalıyor (Mc_önce → Mc_ref): Hector Mine 1,6 → 1,8; EMC 1,6 → 2,0; Chiniak 1,8 → 2,1; Kuzey Ege 2,3 → 3,0;
  Doğanyol 1,5 → 2,5; Jamaika 2,2 → 3,2; Tacikistan 2,7 → 3,8. Bu kayma K'yi yarıdan fazla düşürüyor
  (25 → 8–12).
- Mc + 0,5 referans şartında daha toleranslı. Bu yüzden Mc + 0,5 satırı referanslı sütunda Mc satırından yüksek
  çıkabiliyor.
- **ComCat tek başına:** M ≥ 6,5, N3bg ≥ 50, temiz için K = 8.

### 3.3 Ana tasarımda (M ≥ 6,5 / Mc / N3bg ≥ 50) geçen temiz olaylar (`tr13_ozet.json`, `gecen_N3bg_mc_50`)

Kaliforniya:
- Loma Prieta 1989 (608);
- Superstition Hills 1987 / Hector Mine 1999 (tek küme);
- El Mayor–Cucapah 2010 (687);
- Ridgecrest 2019 (576);
- Big Lagoon açığı 2005 (112).

Alaska:
- Chiniak açığı 2018 (575).

Japonya (ISC):
- Kobe 1995 (194);
- Fukuoka 2005 (233);
- Okinawa 2010 (123);
- Ishigaki 2009 (58);
- Makurazaki 2015 (117);
- Kumamoto 2016 (4225).

Öteki:
- Yunanistan 2014 Kuzey Ege (154) ve 2018 Zakynthos (216);
- Doğu Anadolu: Doğanyol/Sivrice 2020 (281);
- Wenchuan 2008 (164; doğrultu atımlı sayıldı, bindirme ağırlıklı karma);
- Tacikistan 2015 (175);
- Gisborne açığı 2021 (431);
- Jamaika açığı 2020 (310);
- Svalbard 2025 (223);
- Yeni Zelanda: Darfield 2010 (100), Cook Boğazı 2013 (74), Arthur's Pass 1994 (56).

Marmara kutusu (39,5–42,0° K, 26,0–31,5° D):
- **İzmit 1999** (ComCat Mc 2,9, N3bg 227, temiz, referans dolu, kontrol 2) örneklemde.
- 2022 Düzce M 6,1 (örnekten 25) ve 2025 Marmara Ereğlisi M 6,2 (tam sayım 38) eşiğin altında.
- Hiçbiri Marmara terimi değildir.

BZ20'nin olaylarının durumu:
- Hector Mine, EMC ve Ridgecrest var.
- Landers kirli: Joshua Tree M 6,1, iki ay önce, dairede.
- Düzce 1999 artçı kuralıyla dışarıda.

## 4. Güç kapısı (yapay; `tr13_guc.py`)

### 4.1 Üreteç ve ölçü

- **ETAS.**
  - Mc 2,5; b 1; M_max 7,5.
  - Verim 10^(1,0 (m − Mc)); dallanma n = 0,6.
  - Omori p 1,1, c 0,01 g; 50 yıl kesme.
  - Uzay çekirdeği (r² + d²)^(−1,5), d = 0,5 km × 10^(0,5 (m − Mc)).
- **Bölge.** R = 80 km (≈ M 6,7, L ≈ 40 km). Simülasyon dairesi R + 30.
  - 5 yıl ısınma + 10 yıl.
  - Arka planın %60'ı 5 fay çizgisinde (Gauss yarı genişliği 2 km), %40'ı düzgün.
  - İlk fay "gelecek kırık"tır (uzunluk R/2, merkezde).
- **Sinyal.** Önce-pencerede [7 y, 10 y) arka plan olaylarının f kesri kırık çizgisine (2 km) yerleştirilir.
  Artçıları oradan üretilir.
- **Ölçü (BZ20'nin gerekçeli yeniden kurulumu).**
  - Kümesizleştirilmiş olaylar 5 km hücrelere sayılır.
  - V(0,5) = olayların yarısını içeren en az hücre sayısının bölgedeki hücre sayısına oranı.
  - z = (V_önce − ort(V_ref,alt)) / sd(V_ref,alt). Burada V_ref,alt, referans döneminden aynı sayıda olay
    çekilerek hesaplanır; B = 200 çekiliş.
  - Yerelleşme z < 0 demektir.
  - Hücre boyu, q ve standartlaştırma bizim seçimimizdir (§2.2).
- **Sınama.** K bölgenin ortalama z'si, sinyalsiz ETAS z'lerinden K'lık ortalamaların %5 niceliğiyle kıyaslanır
  (tek yanlı α 0,05). Etki d = (E[z|f] − E[z|0]) / sd(z|0).
- **Kalibrasyon ve tekrar.** μ, önce-penceredeki arka plan sayısı N3bg hedefe gelecek biçimde ölçeklendi.
  Sinyalsiz 400, her f için 200 bölge kullanıldı. Tohum 20261112.
- **Kümesizleştirme.** GK74 (gerçek veride kullanılacak olan) ya da "kâhin" (ETAS'ın gerçek arka plan etiketi;
  ideal üst sınır).

### 4.2 Sonuç

| N3bg hedef (gerçekleşen) | Kümesizl. | sd(z\|0) | Yanlış alarm z < −1,645 (z < −2,326) | f_min güç 0,8: K = 10 / 15 / 20 / 30 | d (f = 0,2) |
|---|---|---|---|---|---|
| 25 (27) | GK74 | 1,51 | 0,145 (0,065) | 0,34 / 0,28 / 0,26 / 0,23 | −0,42 |
| 50 (54) | GK74 | 1,38 | 0,128 (0,065) | 0,26 / 0,23 / **0,20** / 0,17 | −0,61 |
| 100 (101) | GK74 | 1,66 | 0,155 (0,078) | 0,29 / 0,23 / **0,19** / 0,12 | −0,58 |
| 200 (141) | GK74 | 2,24 | 0,253 (0,158) | yok / yok / yok / yok | −0,37 |
| 400 (127) | GK74 | 2,30 | 0,368 (0,248) | yok | −0,13 |
| 25 (22) | kâhin | 1,38 | 0,115 (0,058) | 0,27 / 0,23 / 0,19 / 0,16 | −0,65 |
| 50 (50) | kâhin | 1,33 | 0,115 (0,045) | 0,18 / 0,15 / 0,14 / 0,11 | −0,97 |
| 100 (101) | kâhin | 1,44 | 0,078 (0,020) | 0,13 / 0,11 / 0,10 / 0,09 | −1,33 |
| 200 (204) | kâhin | 1,54 | 0,140 (0,058) | 0,09 / 0,08 / 0,075 / 0,05 | −2,16 |

- **Yanlış alarm.** Tek pencerede anma değeri %5'tir. ETAS + GK74'te oran %13–16, yoğun katalogda %25–37 çıkıyor.
  sd(z|0) 1,3–2,3, yani alt örnekleme varyansı ETAS kümelenmesini taşımıyor. Eşik mutlaka ETAS'tan kalibre
  edilmelidir. "Reshuffled catalog" anlamlılığı (BZ20 özeti) bu yüzden iyimser olabilir. Bu bir çıkarımdır;
  tam metin okunmadı.
- **GK74 doyması.** Yoğun katalogda büyük olayların GK74 pencereleri (M 6'da ≈ 54 km, ≈ 1 yıl) bölgeyi siliyor.
  Arka plan sayısı hedefin altında kalıyor (200 → 141, 400 → 127). Kırık bandındaki yoğun arka plan da küçük
  olayların pencereleriyle "küme" sayılıp atılıyor. Sonuç: sinyal yok oluyor (d −0,1/−0,4).
  **Kümesizleştirme seçimi sonucu belirliyor.** BZ20'nin en yakın komşu yöntemi burada sınanmadı.
- **K ve d.** Normal yaklaşımla K = 20'de d_min = (1,645 + 0,842)/√20 = 0,56. Benzetimde f = 0,2 için
  d = −0,61 ve güç 0,82 (N3bg 50); tutarlı.
- **ETAS'ın ana şok öncesi etkisi.** 6000 yıl, 920 917 olay. M ≥ 5,5, merkeze ≤ 40 km, bir yıl içindeki
  tekrarlar atılınca 241 hedef. z_hedef ortalaması −0,02, rastgele 399 pencere −0,38 (sd 1,63). Fark +0,22 ± 0,11 sd,
  yani yayılma yönünde. Yanlış alarm hedef öncesinde 0,12, rastgelede 0,20. Basamaklanma tek başına öncül
  yerelleşme üretmiyor. Ama rastgele pencerelerin ortalaması sıfır değil: katalog sonu kenar etkisi var ve gerçek
  "t'de biten" pencerelerde de bulunur.

### 4.3 Etki büyüklüğü makul mü

- Gereken f ≈ 0,2, arka plan olaylarının beşte birinin 3 yıl boyunca kırık bandına göç etmesi demektir. Benzetimde
  bandın payı ≈ %12'den ≈ %30'a çıkıyor, yani bant içi oran ≈ 2,5 kat.
- BZ20'nin bildirdiği kesirsel alan azalmasının büyüklüğü okunamadı.
- EGU 2023 özeti yerelleşmenin dış merkezi içermeyebileceğini, 2–3 yıl önce ise "sönme" olduğunu söylüyor. Yani
  sinyalin yönü ve yeri bile tek anlamlı değil.
- Hüküm: **makullük doğrulanamadı; gereken etki büyük.**

## 5. Kapı hükmü

Kapı önerisi: K ≥ 20 bağımsız küme ve güç ≥ 0,8'e karşılık gelen etki makul. Üç kademe (TR-10b kuralı):
- **GEÇER:** ana tasarımda ve katı tasarımda geçer.
- **SINIRDA:** ana tasarımda geçmez ama üst sınırda geçer.
- **GEÇMEZ:** üst sınırda da geçmez.

Tanımlar:
- **Ana tasarım:** ölçünün kurulabildiği en gevşek tam şartlar. M ≥ 6,5, Mc, N3bg ≥ 50, temiz önce-pencere,
  referans dolu (tol 0,3).
- **Üst sınır:** referans şartı yok.
- **Katı tasarım:** Mc + 0,5 ve eşleşik kontrol.

| | M ≥ 6,5 | M ≥ 6,0 | Kapı |
|---|---|---|---|
| Üst sınır (temiz, referanssız) | 25 | 31 | geçer |
| Ana (temiz + referans, tol 0,3; tol 0,1) | 12; 8 | 17; 13 | **geçmez** |
| Katı (Mc + 0,5, referans, kontrol) | 5 | 8 | geçmez |
| Güç: K = 20'de f_min (GK74, N3bg 50–100) | 0,19–0,20 | – | makullük doğrulanamadı |
| Güç: elde olan K ≈ 12–17'de f_min | 0,23–0,28 | – | büyük etki |

**Hüküm: SINIRDA.** Ana tasarımda geçmiyor (M ≥ 6,0'a inilse de 17 < 20), yalnız üst sınırda geçiyor. Güç tarafı
da ancak büyük bir etkiyi görebiliyor. Proje dersi (üstveri ve örnek sayımları gerçekte 3–5 kat küçülür) burada da
geçerli. Önce-pencere tam sayıldı, ama referans dönemi ISC olaylarında yalnız 90 günlük örnekten denetlendi.
**En olası sonuç beyanı: TR-13 bugünkü açık veriyle "güç yok" verir. Bir koşu yapılırsa da etki büyük değilse
"ayırt edilemez" verir.** Bu önceden kabul edilir.

## 6. Benzer kapanmış adaylardan farkı (`kayit.py ara yerelleşme | öncü | ETAS`)

- **TK-E4 (elendi; PI, RTL, AMR, nowcasting).** Aynı aile: büyük depremden önce sismisite deseni, geriye dönük
  ve serbest parametreli. Dersi: AMR istatistiksel olarak anlamsız (Hardebeck 2008), bağımsız ileriye dönük skor
  yok.
  - TR-13'ün farkı: zamansal hızlanma ya da sessizlik değil, kümesizleştirilmiş arka planın **uzaysal** dağılımı.
    Arkasında yıl ölçekli açık bir kuramsal öngörü (hasar reolojisi) var.
  - Ders aynen geçerli: serbest seçimler (§7) sabitlenmeden yapılacak her sınama AMR'nin akıbetine açık.
- **FA-6 (elendi; hazırlık evresi göstergeleriyle alarm).** Boşluk değil hükmüyle kapandı (hazırlık × ETAS k = 64).
  S-7 ve DT-2 aynı mekanizmayı kapattı.
  - TR-13 farkı: öncü ya da ön kayma değil, yıl ölçekli arka plan geometrisi. FA-6'nın taradığı gün–ay ölçekli
    hazırlık evresinin dışında.
  - DT-2 (kümelenme → PIF kenetlenmesi, H0, ters işaret) bir kümelenme ölçüsünün aktarımının tutmadığını gösterdi.
- **TK-1 (ayırt edilemez; EEPAS, 1–5 yıl).** Orta vadeli öncü ölçeklemesi. Etkin N ≈ 40 ile 0,45 nat altı
  görülemedi; ölçülen hız ölçeklemesiydi.
  - TR-13'te etkin birim daha da az (K ≈ 8–25). Aynı biçim burada da: yalnız büyük etki görülebilir.
- **DK-3 (H0) ve ETAS-TABAN.** ETAS'ın yeteceği dersi. Bu sayımın ETAS kısmı bununla tutarlı: ETAS sahte öncül
  yerelleşme üretmiyor. Ama yanlış alarm anma değerinin 2,5–3 katı.
- **TR-15 (aday; öncü dizilerinde 1/t).** Aynı kuramsal kaynaktan, ama gün ölçeği. TR-13'ün (iii)
  "coalescence" son 1–2 yıl parçası onunla örtüşüyor; burada sayılmadı.
- **TR-1, TR-5b, TR-10b (güç yok / veri yok).** Aynı başarısızlık biçimi: kirlenmemiş karşılaştırma penceresi ve
  doluluk. TR-13'te karşılığı "temiz önce-pencere + dolu referans dönemi".
- **Projede benzeri olmayan yanı.** Ölçü katalogdan hesaplanır, alet verisi gerektirmez, 0 € ile koşulabilir.

## 7. Tasarım serbestliği ve ön kayıtta sabitlenecekler

Ölçünün en az 12 serbest seçimi var. İkili bile olsalar 2¹² çatal eder. BZ20'nin tam metni okunamadığı için çoğu
kaynaktan sabitlenemiyor. Hepsi ön kayıtta tek değere bağlanmalı.

1. **Ana şok tanımı.** M eşiği (6,5 / 6,0), Mw şartı, derinlik, mekanizma ölçütü ve artçı kuralı. Düzce 1999
   örneği: bu kuralla düştü.
2. **Bölge.** Dış merkezde 2 L daire mi, fay boyunca dikdörtgen mi, BZ20 gibi "seçimsiz bölgesel ızgara" mı?
   Sonuncusunda K tanımı değişir.
3. **Pencereler.** Önce-pencere 2, 3 ya da 2–3 yıl. Referans uzunluğu 7 yıl mı, uzun dönem ortalaması mı? Önce
   pencereden son 2 gün ya da son 1 yıl dışlanacak mı ("coalescence" ile karışmasın diye)?
4. **Mc.** MAXC + 0,2, Mc + 0,5 ya da sabit eşik. Önce ve referans dönemi için ortak Mc.
5. **Kümesizleştirme.** GK74, Reasenberg ya da en yakın komşu (BZ20), ve parametreleri. §4.2 gösterdi ki bu seçim
   sonucu tek başına belirliyor.
6. **Ölçü.** V(q) ve q değeri, Gini G ya da ROC alanı.
7. **Hücre boyu.** 2, 5 ya da 10 km; voksel mi, alan mı.
8. **Standartlaştırma.** Referans alt örneklemesi, zaman serisi z'si ya da ETAS z'si.
9. **Yerelleşmenin yeri.** Bölge geneli V(q) mı, kırık zonuna göreli pay mı? EGU 2023'e göre sinyal dış merkezi
   içermeyebilir.
10. **Yön.** Yalnız yerelleşme mi (tek yanlı), yoksa "sönme" de mi sayılacak?
11. **Sınama istatistiği ve eşik.** Ortalama z, medyan ya da işaret sınaması. Eşik ETAS'tan kalibre edilir.
    Anma değeri %5 kullanılamaz (§4.2).
12. **Kontrol pencereleri ve ETAS.** Eşleşik depremsiz pencerelerin seçimi; ETAS parametreleri bölge başına mı
    uydurulur, sabit mi alınır?
- Ek olarak temiz pencere ve referans doluluk kuralları ile katalog öncelik sırası (ComCat → ISC → bölgesel)
  sabitlenmeli.

Önerim: BZ20'nin tam metni meşru yoldan okunmadan ön kayıt yazılmasın (VE-1 dersi: parametre tablosu ön kayıttan
önce okunur). Okunursa 2, 5, 6, 7 ve 9 maddeleri kaynaktan sabitlenir.

## 8. Yeniden açma şartı ve sonraki adım

Aday elenmedi; SINIRDA. Yeniden açma ya da ön kayda geçme şartlarından biri gerekir:
- (a) **Referans dönemi tam sayımı.** Yalnız üst sınırda geçen temiz olaylar (≈ 30–45) için ISC/GeoNet/EMSC [t − 10 y, t − 3 y)
  tam indirmesi; 0 €, ≈ 1–2 saat. Bu sayım temiz + referans + kontrol şartıyla **K ≥ 20** verirse ön kayıt
  yazılabilir. Bu bir "aşama 0"dır; TR-5b'deki gibi ön kayıttan önce koşulur.
- (b) **BZ20 tam metni** meşru yoldan okunur (açık arşiv, yazar kopyası, kurum erişimi). Hücre, q, pencere ve
  kümesizleştirme sabitlenir. Bildirilen azalmanın büyüklüğü f'ye çevrilir. f ≤ f_min(K) çıkarsa güç tarafı geçer.
- (c) Yazarlardan bağımsız bir çalışma, ölçünün ETAS'a karşı yanlış alarm oranını yayımlarsa. Sayısal
  karşılaştırma olabilmesi için bu oranın ölçüsü ya bizim ölçümüzle aynı olmalı ya da ona çevrilebilmeli.
- (d) Daha düşük Mc'li açık bölgesel katalog kapsamı artarsa. Örnek: JMA birleşik doğrudan; Tayvan, Yunanistan ya da
  Türkiye 1990'lar sayısallaştırılmış. M ≥ 6,0, N3bg ≥ 50 temiz + referans şartında K ≥ 20 olmalı.
- Marmara'ya terim: yalnız küresel sınav (ön kayıtlı, ETAS'a karşı) geçerse. Mutlak İstanbul olasılığı yazılmaz.

## 9. Körlük beyanı ve metin–kod notları

- Okunanlar: ComCat ana şok listesi ve mekanizmalar; ana şok öncesi daire katalogları. ComCat [t − 10 y, t);
  ISC/GeoNet/EMSC örnekleri ve [t − 3 y, t) tam önce-pencere.
- Hiçbir ana şok sonrası pencere indirilmedi. TR-6a/TR-2/TR-7 olay sonrası pencerelerine dokunulmadı.
- **Gerçek veride V(q), G, z hesaplanmadı.** Yalnız sayı, Mc ve GK74 arka plan sayısı.
- 2026 verisi yok. Kod assert eder ve okuyucu ≥ 2026-01-01 satırını atar. 2025-12-24 Taitung ana şoku listede,
  çünkü önce-penceresi 2025'te biter.
- OpenAlex anahtarı yazdırılmadı. Atıf listesi için OpenAlex açık API'si anahtarsız kullanıldı. Hiçbir isteğe kişi
  ya da proje adı konmadı.

Metin–kod notları:
- GK74 öncüleri de aynı pencereyle atar. Bağımlı olay küme başı olmaz.
- Örnekten tahminde f_bg = 0,204 (ComCat medyanı) sabit çarpandır.
- ISC tam sayımında GK74 yalnız R dairesinde ve 3 yılda uygulandı (kenar payı yok). ComCat'te R_ind ve 10 yılda.
  Bu iki katalog arasında küçük bir tutarsızlıktır.
- "En iyi katalog" N3bg_mc'ye göre seçildi. Öteki Mc seçenekleri aynı katalogdan alınır.
- `tr13_ozet.json` içindeki `guc_parametre` son okunan dosyanın (kâhin) parametreleridir. GK74 koşularının
  parametreleri `tr13_guc_gk_*.json` içindedir.
- Benzetim gerçek veriden uydurulmadı. Değerler yaygın Kaliforniya ETAS aralığından seçildi; bölge başına uydurma
  ön kayıt işidir.

## 10. En büyük üç zayıflık

1. **Ölçü bizim yeniden kurulumumuz.** BZ20'nin tam tanımı okunamadı. Hücre, q, pencere ve kümesizleştirme
   değişince güç sonuçları değişir. Özellikle GK74 yerine en yakın komşu kümesizleştirmesiyle, ve yoğun
   katalogda, sonuç farklı olabilir.
2. **K sayımı üst sınıra yakın.** Önce-pencere tam sayıldı, ama ISC olaylarında referans dönemi ve kontrol
   pencereleri 90 günlük örnekten ya da yalnız M ≥ 5,5 havuzundan denetlendi. Mc'nin MAXC + 0,2 kuralı karışık ağlı
   bölgelerde (açık deniz, Japonya'nın kıyı ağı) iyimserdir. Ayrıca ISC ve ComCat farklı yöntemlerle sayıldı.
3. **Bağımsızlık ve temsil.** Geçen kümelerin yarısı Kaliforniya, Japonya ve Tayvan. Mekanizma ölçütü gevşek
   (karma Wenchuan ve Kahramanmaraş). Okyanus transform faylarının neredeyse hiçbiri geçmiyor. Sonuç "yoğun ağlı
   kıta ve yay içi doğrultu atımlı faylar" örneklemidir; Marmara'nın denizaltı fayına doğrudan çevrilmez.

## Ek 1 (12 Kasım 2026): referans ve kontrol tam sayımı

Yeniden açma şartı (a) koşuldu (0 €). Gövde değiştirilmedi. Kod `kayit/turetme/tr13/tr13_tamsayim.py`, çıktı
`tr13_tamsayim.json`. Ham veri `/mnt/project-files/turetme/tr13-ham/tr13_tamsayim_ham_2026-11-12.tar.gz`
(32 852 266 B, sha256 `7f40414b65d79da0e8161ee24f68a4e90e5ae2412bb53a6ef7793027267efc63`; içerik `ham_tam/`:
527 yıllık parça `parca_<servis>_<id>_<j>.npz`, 540 ham FDSN yanıtı, indirme günlüğü, json kopyası).

### E1.1 Ne yapıldı

- **Hedef.** §3.2'deki temiz ve N3bg ≥ 50 (Mc) olaylar: 41 olay, 31 küme (M ≥ 6,5: 25 küme). `sayim4.json`'dan
  aynen alındı (sha256 0ae42bc0…). Temiz sayıları (25 / 31) yeniden üretildi.
- **Kurallar değişmedi.** Mc = MAXC + 0,2 (20–49 olayda + 0,3), GK74, tol 0,1 / 0,3, referans şartı
  Mc_ref ≤ Mc_önce + tol ve N_ref,bg ≥ 100, kontrol eşleme tanımı (t_c = t − 6k y, havuzda [t_c − 3 y, t_c + 3 y]
  içinde M ≥ 5,5 yok, t_c − 10 y ≥ 1975). Kod, uygun k sayısının §3'teki `kontrol_pencere_havuz` ile aynı
  olduğunu assert eder.
- **Referans dönemi.** ISC / GeoNet / EMSC olaylarında (25 olay) [t − 10 y, t − 3 y) R dairesinde yıl yıl TAM
  indirildi (M ≥ Mc_önce − 0,3). Mc_ref bu 7 yılın MAXC + 0,2'si; GK74 bu pencerede, R dairesinde (ISC tam3 ile
  aynı yöntem). ComCat olaylarının referansı zaten tamdı; değerleri değişmedi.
- **Kontrol doluluğu (yeni ölçülen).** Gövde doluluğu tanımlamamıştı. Hedefle aynı kural uygulandı: kontrolün
  önce-penceresi [t_c − 3 y, t_c) için Mc_c ≤ Mc_önce + tol ve N3bg_c (m ≥ Mc_önce) ≥ 50; kontrolün kendi
  referansı [t_c − 10 y, t_c − 3 y) için hedefteki referans şartı. Ana satır ikisini birden ister ("dolu");
  yalnız önce-pencere şartı ayrıca yazıldı. ComCat'te kontrol penceresi hedefle aynı biçimde (R_ind, 10 y, M ≥ 1,0,
  Mc 5 y kuralı, Mc_ref [t_c − 10 y, t_c − 5 y)). 77 uygun kontrol penceresinin hepsi indirildi; önce-penceresi
  tol 0,3'te dolu olmayanın referansı indirilmedi (sonucu değiştirmez).
- **Körlük.** Bütün parçalar ana şoktan önce biter; indirilen en geç olay 2022-03-09. 2026 verisi yok. Gerçek
  katalogda V(q), Gini, z hesaplanmadı; yalnız sayı, Mc, GK74 sayısı. Servisler ISC, GeoNet, EMSC, ComCat;
  anonim, genel User-Agent; 401/403 yok, 429 yok.

### E1.2 Kesin K (bağımsız küme; N3bg ≥ 50, Mc)

| Satır | M ≥ 6,5 tol 0,1 | M ≥ 6,5 tol 0,3 | M ≥ 6,0 tol 0,1 | M ≥ 6,0 tol 0,3 |
|---|---|---|---|---|
| Temiz (üst sınır) | 25 | 25 | 31 | 31 |
| Temiz + referans, ilk sayım (90 g örnek) | 8 | 12 | 13 | 17 |
| **Temiz + referans dolu (tam)** | **11** | **14** | **16** | **20** |
| Temiz + referans + kontrol, yalnız havuz (eski tanım) | 8 | 9 | 13 | 15 |
| Temiz + referans + kontrol önce-penceresi dolu | 5 | 6 | 9 | 11 |
| **Temiz + referans + eşleşik kontrol dolu (tam)** | **3** | **4** | **4** | **7** |

- Duyarlılık (kural değil): ISC'de Mc_ref ComCat'teki gibi yalnız [t − 10 y, t − 5 y)'den alınırsa temiz + referans
  10 / 14 / 13 / 19 olur.
- Tam referans sayımı K'yi örnek tahmine göre **artırdı** (+2–3 küme). Örnek iki yönde de yanılmıştı:
  - örnekte düşüp tamda geçen: Cook Boğazı, Kolombiya, Tacikistan 2017, Küba 2024, Jan Mayen (tol 0,1); tol 0,3'te
    ayrıca Ishigaki, Jamaika 2020, Doğanyol 2024;
  - örnekte geçip tamda düşen: Okinawa (tol 0,3), Kefalonya 2014 (Mc_ref 2,2 → 3,5), Hualien (N_ref 859 → 72).
  Ders "3–5 kat küçülür" bu adımda tutmadı. Ama kontrol doluluğu ölçülünce K 4–7'ye düştü.

### E1.3 Kümeler ve bölge dağılımı

Temiz + referans dolu, M ≥ 6,0, tol 0,3 (20 küme):
- Kaliforniya 5: Loma Prieta 1989; Güney Kaliforniya 1986–1999 kümesi; South Napa 2014; Ridgecrest 2019;
  Big Lagoon açığı 2005.
- Japonya 4: Kobe 1995; Ishigaki 2009 (yalnız tol 0,3); Kumamoto 2016; Kurayoshi 2016.
- Yeni Zelanda 3: Darfield 2010; Cook Boğazı 2013; Gisborne açığı 2021 (yalnız tol 0,3).
- Alaska 2: Yakutat 2014; Chiniak açığı 2018 (yalnız tol 0,3).
- Türkiye 2: İzmit 1999 (ComCat); Doğanyol 2024 M 6,0 (yalnız tol 0,3; 2020 olayı düştü).
- Birer: Kolombiya 2016 (Mutatá); Tacikistan 2017 M 6,0 (2015 M 7,2 düştü); Karayip (Küba açığı 2024 M 6,8;
  Jamaika 2020 yalnız tol 0,3); Jan Mayen 2025 (gövdede "Svalbard").
- M ≥ 6,5, tol 0,3 (14): yukarıdakilerden Napa, Kurayoshi, Yakutat, Doğanyol, Kolombiya ve Tacikistan çıkar.
  tol 0,1'de ayrıca Ishigaki, Chiniak ve Gisborne çıkar (11).

Temiz + referans + eşleşik kontrol dolu:
- M ≥ 6,0, tol 0,3 (7): Kobe (k = 1), Kumamoto 6,2 (k = 1), Darfield (k = 1), Cook Boğazı (k = 1, 2, 3),
  Yakutat (k = 3), South Napa (k = 1), Ridgecrest (k = 1, 2, 3, 5). Japonya 2, Yeni Zelanda 2, Kaliforniya 2,
  Alaska 1.
- M ≥ 6,5, tol 0,3 (4): Kobe, Darfield, Cook Boğazı, Ridgecrest. tol 0,1'de Kobe düşer (3).
- M ≥ 6,0, tol 0,1 (4): Darfield, Cook Boğazı, Kumamoto, Ridgecrest.

### E1.4 Hangi kümeler neden düştü

Referans şartında (Mc_önce → Mc_ref; ağ zamanla iyileşiyor):
- Fukuoka 2005 0,6 → 1,3; Okinawa 2010 2,2 → 2,6; Makurazaki 2015 1,6 → 2,1; El Mayor–Cucapah 1,6 → 2,0;
  Kuzey Ege 2014 2,3 → 2,9; Zakynthos/Kefalonya kümesi 2,1 → 3,5 ve 2,4 → 3,0; Wenchuan 2,9 → 3,3;
  Doğanyol 2020 1,5 → 2,6 (küme 2024 olayıyla kalır); Tacikistan 2015 2,7 → 3,6.
- Arka plan yetmiyor (N_ref,bg < 100): Arthur's Pass 1994 (82), Minto 1995 (74), Hualien 2022 (72), Stanley
  2020 (51; Mc_ref yok).

Kontrol şartında (referansı dolu 20 kümeden 13'ü):
- Uygun kontrol penceresi hiç yok (bölgede her 6 y'lık dilimde M ≥ 5,5 var): Loma Prieta, Güney Kaliforniya
  kümesi, Chiniak, Gisborne, Big Lagoon.
- Kontrol penceresi var ama eski dönem katalog boş ya da Mc yüksek: İzmit (k = 1 referansı Mc 4,3; k = 2 Mc 4,1),
  Ishigaki (Mc 3,0), Kolombiya (k = 1 referansı Mc 2,9), Kurayoshi (k = 1, 2 referansı Mc 1,6–1,7 > 1,0),
  Tacikistan 2017 (Mc 3,6), Doğanyol 2024 (Mc 2,6), Küba 2024 (N3bg ≤ 18), Jan Mayen (k = 1 referansı 2,2 > 1,7 + 0,3).
- Kontrolün 1990 öncesine düşen pencereleri ISC'de hemen her yerde boş ya da Mc ≥ 2,6.

### E1.5 Kapı hükmü

- Şart (a) "temiz + referans + kontrol ile K ≥ 20" ister. Kesin değer **3–7**. **Şart (a) sağlanmadı.**
- Ana tasarım (M ≥ 6,5, tol 0,3, temiz + referans) **14 < 20**: geçmez. Tek 20, en gevşek hücrede (M ≥ 6,0,
  tol 0,3, kontrolsüz) tam sınırda; duyarlılıkla 19'a iner ve iki üyesi (Küba 2024 Mc 1,0; Ishigaki) kırılgandır.
- §5 hükmü (SINIRDA, üst sınırda geçer) değişmez; ön kayıt yazılmaz. Eşleşik kontrol isteyen her tasarım bugünkü
  açık veriyle **güç yok** verir. Kontrolsüz tasarım ise ancak M ≥ 6,0 ve tol 0,3 ile K ≈ 20'ye ulaşır.

### E1.6 Kalan zayıf yerler

1. **Mc_ref 7 yıllık MAXC'tır.** Ağın değiştiği dönemlerde MAXC en kalabalık dönemi gösterir. Küba 2024'te 7 yıl
   1,0 verir, [t − 10, t − 5) ise 2,2. MAXC + 0,2 karışık ağlarda iyimserdir; ±1 küme oynar.
2. **Kontrol doluluğu tanımı bizim aynamızdır.** Gövde tanımlamamıştı. Yalnız önce-pencere şartıyla K 5–11,
   kontrolün kendi referansıyla 3–7. Her iki tanımda da 20'den çok uzak.
3. **ComCat ile ISC farklı sayılıyor.** ComCat'te GK74 R_ind ve 10 y'da, Mc 5 y'dan; ISC'de R ve pencere başına.
   Değiştirilmedi.
4. **Örnekten N3bg < 25 olup tamda ≥ 50 çıkabilecek olaylar** yine sayılmadı (gövde §3.1).
5. **Temsil.** Kontrollü 7 küme Japonya, Yeni Zelanda, Kaliforniya ve Alaska'dadır. Doğu Akdeniz ve Türkiye'den
   hiçbiri yok; İzmit kontrol penceresinin 1980'lerdeki katalog boşluğuyla düşer.
6. Kodda bir yarış hatası (iki iş parçacığı aynı parçayı yazıyordu) 3 parçayı eksik bıraktı. Düzeltildi; bütün
   parçalar önbellekten yeniden kuruldu ve eskileriyle bire bir aynı çıktı.
