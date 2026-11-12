# TR-7 ön kaydı: Marmara ve batı KAF'ta uzak depremlerin yüzey dalgalarıyla tetiklenmiş tremor taraması

Tarih: 12 Kasım 2026. Durum: **DONDURULDU sürüm 3 (12 Kasım 2026; bu commit dondurma kaydıdır) (İNCELEME-1 ve İNCELEME-2 düzeltmeleri işlendi).**
Henüz dondurulmadı; bu metin "DONDURULDU" başlığıyla commit + push edilir, ondan sonra metin değişmez, ekler ayrı
başlıkla yazılır. Üçüncü inceleme turu yoktur (İNCELEME-2 son turdur). Sürüm 2 → 3 değişiklikleri §19'da.
Türediği yerler: `kayit/onkayit/TR-7_SAYIM.md` (tasarım §2, sayım §3–§5, Ek 1; K0 GEÇTİ),
`kayit/onkayit/TR-7_INCELEME-1.md` (DÜZELTMEYLE KABUL; E1–E3, Ö1–Ö8, K1–K7) ve
`kayit/onkayit/TR-7_INCELEME-2.md` (DÜZELTMEYLE KABUL, son tur; İ2-E1–E3, İ2-Ö1–Ö8, K-a–K-g).
Kod (`kayit/turetme/tr7/`): sayım `tr7_sayim.py`, `tr7_varlik.py`; ön kayıt `tr7_onkayit_sayilar.py`,
`tr7_onkayit_yapay.py`, `tr7_onkayit_modulasyon.py`; sürüm 2'de eklenen `tr7_parkfield_varlik.py` (E2),
`tr7_e1_maske.py` (E1), `tr7_negatif_pencere.py` (Ö4), `tr7_onkayit_denetim2.py` ve `tr7_onkayit_denetim2_kos.py`
(yeni yapay denetimler); İNCELEME-1'in betikleri `tr7_inc1_d10.py`, `tr7_inc1_d10b.py`, `tr7_inc1_modv.py`,
`tr7_inc1_modreal.py`, `tr7_inc1_darbe.py` olarak kopyalandı; sürüm 3'te eklenen `tr7_onkayit_sayilar3.py` (n_açık,
p_min, X_min^(0,05/7)), `tr7_onkayit_d12c.py` (D12c), `tr7_onkayit_denetim3.py` ve `tr7_onkayit_denetim3_kos.py` (D15,
D6/D6b ×100 yeniden koşusu); İNCELEME-2'nin betikleri `tr7_inc2_taban.py`, `tr7_inc2_taban_ek.py`; yer tutucu
doldurucu ve denetleyici `tr7_onkayit_doldur.py`. Bu belgedeki her sayı bu betiklerin çıktısından alındı.
Maliyet 0 €. Bu belge yazılırken tek dalga formu erişimi §3.2'deki Parkfield varlık yoklamasıdır (112 satır, 10'ar sn;
yalnız HTTP kodu ve bayt; içerik çözülmedi, diske yazılmadı). Marmara'nın hiçbir dalga formu istenmedi. Sürüm 3 için
hiçbir dalga formu ve hiçbir ağ erişimi yapılmadı (yalnız depodaki dosyalar ve yapay veri).

## 0. Bağlayıcı metinlerin sırası

Çelişkide sıra: (1) **bu metin (sürüm 3)**; §3'te ve §19'da sha256'sı verilen dosyalar (listeler, negatif pencereler,
E1 maske önhesabı, sürüm 3 önhesapları) bu metnin parçasıdır; (2) **İNCELEME-2'nin düzeltme metinleri**, yalnız bu
metnin sustuğu yerde; (3) **İNCELEME-1'in düzeltme metinleri**, yalnız bu metnin ve İNCELEME-2'nin sustuğu yerde;
(4) **`TR-7_SAYIM.md`** §2 ve Ek 1. Bu metnin inceleme metinlerinden bilerek saptığı yerler §17'de gerekçeleriyle
yazılıdır (İNCELEME-1: S1–S10; İNCELEME-2: S11–S13) ve orada bu metin geçerlidir. Bu belge SAYIM §2.5–§2.10'un yerine geçer; farklar §15'te. Metin ile kod
çelişirse metindeki sayısal tanım geçerlidir; koşu kodu listeleri yeniden kurmaz, okur ve sha256'larını denetler.

## 1. Soru ve neyi ölçmediği

Soru: 2005–2025 arasındaki büyük uzak depremlerin yüzey dalgaları geçerken KAF'ın Marmara kesimlerinde (S1 Ganos–Saros,
S2 Orta Marmara–Adalar, S3 Çınarcık–İzmit) 2–8 Hz'te, birden çok istasyonda tutarlı, yerel depremle ve öteki büyük
olayların cisim dalgalarıyla açıklanamayan ve yüzey dalgasıyla eş periyotlu modülasyonlu bir tremor oluşuyor mu?
Oluşmuyorsa hangi kaba dinamik gerilmenin üstünde, hangi genliğin üstünde "görülmedi" denebilir?

Ölçmedikleri: ortam (tetiklenmemiş) tremor; sığ sünme (TR-10'un konusu); tremor ile deprem olasılığı arasındaki bağ;
2026 sonrası. İstanbul için mutlak olasılık bu belgede ve koşu çıktısında hiçbir yerde yazılmaz (§13).

## 2. Önceki bulgular, rakip açıklamalar, önsel

Özetten doğrulanan sayılar (OpenAlex, `kayit/oa.py ozet`; tam metin okunmadı):

| Kaynak | Bulgu | Doğrulama |
|---|---|---|
| Peng vd. 2009, 10.1029/2008jb006049 | Parkfield–Cholame, 2001+ 31 Mw≥7,5 olayın 10'u tetikledi; eşik ~2–3 kPa; tremor Love parçacık hızıyla eş fazlı | özetten doğrulandı. Eşiğin PGV'den hangi bileşenle hesaplandığı ve eşik üstü olaylarda oran: doğrulanamadı |
| Chao vd. 2011, 10.1111/j.1365-246x.2011.05261.x | Tayvan, 45 olayın 9'u; eşik ~0,1 cm/s ≈ 7–8 kPa, "kısmen gürültü düzeyine bağlı"; 10–30 sn dalgalar da tetikleyebiliyor | özetten doğrulandı |
| Chao vd. 2012, 10.1785/0120110151 | Calaveras ve San Jacinto'da 42 olaydan yalnız Denali 2002; Parkfield'da 12; fark yalnız gürültüden değil | özetten doğrulandı; görsel inceleme yöntemi |
| Hill vd. 2013, 10.1785/0120120114 | Tohoku 2011 Parkfield'da (~8200 km) tremor tetikledi; PKD'de kayıtlı; S'de başlıyor, Love'da belirgin, 20–30 sn Rayleigh ile modüle; derinlik 20–30 km; tepe dinamik Coulomb gerilmesi 0,7–10 kPa | özetten doğrulandı |
| Pfohl vd. 2015, 10.1785/0120140312 | Merkezî KAF, ~400 km kesimde 2 yıllık geçici geniş bant ağ; yüzey dalgasıyla tetiklenmiş tremor yok; ortam tremoru benzeri sinyaller istasyonlar arasında tutarsız | özetten doğrulandı. İstasyon sayısı, gürültü düzeyi, incelenen olay listesi ve sayısal eşik: doğrulanamadı |

Rakip açıklamalar ve sınav öncesi güven (yazarın beyanı): (R1) Marmara'nın kilitli derinliğinin altında Parkfield
türü düşük etkin gerilmeli, tetiklenebilir bir kaynak var ve bugünkü yüzey ağının gürültü tabanının üstünde (0,10);
(R2) kaynak yok ya da var ama gürültü tabanının altında (0,80); (R3) kaynak yalnız Tayvan türü yüksek eşikli,
tetikleyici gerilmeleri yetmiyor (0,10). Bu ölçüm R2 ile R3'ü ayıramaz.
(R4) Yüzey dalgalarının tetiklediği kataloglanmamış yerel mikrodepremler (tremor değil). Bu ölçüm R4'ü tremorden
yalnız darbe kuralı kadar ayırır: S–P ≤ 5 sn ve gürültünün ~100 katı olaylar ayrılmaz (D6b).

## 3. Veri, dondurulan dosyalar, manifest

**3.1 Dondurulan Marmara listesi.** `kayit/turetme/tr7/tr7_dondurulan_liste.csv`, sha256
`0f3cbd36876a46354b46355016f949f113ddaadcce4d26b6bc9e7a0b1da4358b` (sürüm 1'deki 19 sütun birebir aynı; sürüm 2
üç sütun ekler, §3.1 sonu). Üretimi: `python3 -I -B tr7_onkayit_sayilar.py <comcat_m75.csv> --parkfield <ncedc.txt>
<earthscope.txt> --yaz` (bu dizinde `tr7_parkfield_varlik.csv` bulunmalı). Girdi sha256'ları (ayrıca
`tr7_onkayit_sayilar.json` içinde; json'un kendi sha256'sı §18):
- `tr7_varlik.csv` a795a7f98198e6c20b1b24bca282dabb35addc9c50023694379110d8c90d48e8
- `tr7_varlik_ozet.json` 621791d083c071f0c53617a26dd65ae513a9f3a6f20d72140006af17510d174d
- `tr7_istasyon.csv` a7bb0892d3fb19d1ea0b882857bf1be6340ea3600f61586edcf0da56e4050db7
- `tr7_tetikleyici.csv` dec0cdd0b0b441ae792a98564d55164edd2bb858a0b7eebf235e6355f95ceb8c
- ComCat önbelleği `comcat_m75.csv` (depo dışı, `tr7_sayim.py`'nin çektiği yanıt; betik uyuşmazlıkta durur)
  ae9117d0fe64aae4be19a45a0151e830bd2b35de40056e3b322a3c4a06833e61
- `tr7_parkfield_varlik.csv` 951d7797fcbb2d4427f43f35e3b0a2ceec46e8a684421f535be70371fd5305d0

Kural: Ek 1 yoklamasında "var" çıkan (200, >0 bayt) istasyonlardan, bir (tetikleyici × segment) çiftinde ≥3 istasyon
"var" ise çift listeye girer. İçerik: **71 çift, 17 olay, 475 istasyon-tetikleyici, 884 satır** (SAYIM Ek 1 ile aynı).
Her satır: birim, tetikleyici, T0, M, dış merkez, segment, kaba τ (segment ortası, ×1), Kahramanmaraş bayrağı, ağ,
istasyon, koordinat, yoklama kanalı, dış merkez uzaklığı, başvuru penceresi R, yüzey dalgası penceresi W ve sürüm 2'de
eklenen **`iz_km`** (istasyonun segment izine uzaklığı, `nokta_cizgi`), **`iz_sira`** (o çiftte ize yakınlık sırası;
eşitlikte ağ, sonra istasyon adı alfabetik) ve **`ilk12`** (sıra ≤ 12). Listeye istasyon eklenmez, listeden satır
silinmez; tam taramada istasyon yalnız düşebilir (§4.2) ve 12 sınırı (§6.0) örtüden geçenlere koşuda yeniden uygulanır.
`ilk12` sütunu yalnız önsayım içindir: 884 satırın 623'ü, 475 istasyon-tetikleyicinin 391'i ilk 12'dedir. S1–S3'ün
34 çiftinden 8'inde 12'den çok istasyon var (en çok: İran 2013 S3'te 59).

**3.2 Dondurulan Parkfield listesi ve varlık yoklaması (E2).** `tr7_parkfield_liste.csv`, sha256
`9dca3380815196a8db15a8a5929441d38dd9b07fd7ed982845543e179957b2b8` (sürüm 1'deki 9 sütun birebir aynı; sürüm 2
`var_R`, `var_W`, `iz_sira`, `ilk12` ekler). Kaynak: NCEDC ve EarthScope fdsnws/station (kanal düzeyi, 35,3–36,6° K,
121,3–119,6° B, 2011-03-11T05:00–08:00); yanıt sha256'ları NCEDC
ab9b0d28014f1ef54d569a9aba45e3a47543a73391d559caa4508fc20eaa2e8e, EarthScope
86a5d5bc1729bbbb73b163775ae6566d13a956eb1acc364b4d203ae2bc32566d (yanıtlar depo dışında). Marmara'yla aynı seçim
kuralları (Z bileşeni, bant H/B/E/S, alet H/P, ≥20 Hz, ZQ/SY dışarıda, ize ≤50 km). Ek kural: PB ağı ve derinliği
≥50 m kanallar (kuyu jeofonları) dışarıda, çünkü Marmara listesinde kuyu sensörü yok. İz (kaba, ±5 km): (120,80° B,
36,20° K) – (120,50; 35,97) – (120,35; 35,83) – (120,20; 35,65), Hill 2013'ün tremor kesimini (Parkfield'ın 30 km KB'sı
ile 40 km GD'su) örter. Sonuç: **56 yüzey istasyonu** (NC 47, CI 6, BK 2, NP 1); BK.PKD listede. Tohoku'nun iz
ortasına (iz köşe ortalaması) uzaklığı 8171 km; W = 2011-03-11T06:13:38–06:45:02 UTC (iz ortası). Kaba τ (aynı Prag
bağıntısıyla) 27,12 kPa; Hill 2013'ün hesapladığı tepe Coulomb gerilmesi 0,7–10 kPa. Bu fark kaba τ'nun M9'da 3–40 kat
fazla olabileceğini gösterir (§12).

**Parkfield varlık yoklaması (dondurmadan önce, 0 €; `tr7_parkfield_varlik.py`).** 56 istasyonun her biri için listedeki
Z kanalından (HHZ > BHZ > EHZ > SHZ) iki 10 sn'lik NCEDC dataselect isteği yapıldı (EarthScope yalnız NCEDC 404 dönerse
denendi): R ortası (2011-03-11T05:16:24–05:16:34) ve iz ortası W ortası (06:29:20–06:29:30). Yalnız HTTP kodu ve bayt
kaydedildi; içerik çözülmedi, diske yazılmadı. Tek akış, istekler arası ≥0,35 sn, genel User-Agent; 429/503 ve 401/403
gelmedi. 112 satır (104 NCEDC 200; 4 istasyonun 8 isteği NCEDC'de 404, EarthScope'ta da 404; toplam 120 HTTP isteği,
503 808 bayt). Çıktılar `tr7_parkfield_varlik.csv` (sha256 §3.1) ve `tr7_parkfield_varlik_ozet.json`
(71be3c1b52d78c6656bf43f64f9dec96b6a33de89b35464e3b3a898b085cce12). Sonuç listeye `var_R` ve `var_W` sütunları olarak
eklendi. **İki örnekte de "var" olan istasyon sayısı 52'dir** (56'dan eksik dördü: NP.PJQC, CI.SMM, CI.SMR, CI.CAR; ikisi
de "yok", "kısıtlı" yok). Sürüm 1 sırasının ilk 12'sinde 11 (eksik NP.PJQC). Sayı ≥ 3 olduğundan ön kayıt bu tasarımla
dondurulabilir. K1 kümesi yalnız bu 52 istasyondur; 12 sınırı (§6.0) bunlardan örtüden geçenlere uygulanır. Varlık
örneğine göre ize en yakın 12'si (`ilk12`): NC.PGH, PHF, PTR, PMM, PAGB, PSN, PMPB, PSM, PPT, PKL, PL11B, PHA (10'u
EHZ/SHZ kısa periyot, PAGB ve PMPB HHZ). Yoklama %90 örtüyü doğrulamaz (§12).

HRSN (BP) kuyu istasyonları için İNCELEME-1'in isteğe bağlı önerdiği ayrı liste ve yoklama bu sürümde yapılmadı (§17 S2).

**3.3 Dondurulan negatif kontrol pencereleri (Ö4; `tr7_negatif_pencere.py`).** `tr7_negatif_pencere.csv`, sha256
`ae4fa9c1d84ff3a461c9659ffc58c5a366f82671e1df74233cb3283253a6a59b`; özet `tr7_negatif_pencere_ozet.json` (ComCat M ≥ 6,5
yanıtlarının sha256'ları içinde). §7.3'teki kuralla, yalnız katalogdan üretildi: 16 birim × 10 + Parkfield 10 =
**170 pencere**; her birimde 10 pencere ±30 gün içinde bulundu (±31–60 genişletmesine gerek olmadı). Koşu kodu bu
listeyi yeniden kurmaz, okur.

**3.4 Dondurulan E1 maske önhesabı (`tr7_e1_maske.py`).** `tr7_e1_maske.csv` (sha256
`aef412df1d805fbbee65c1d4f7a76df67ce9b43ec9ee2a8bb3f1345bffccf391`; olay × pencere × faz, iasp91 varış anları) ve
`tr7_e1_maske_ozet.json` (128720470ea39479108329960f605bc49f3795e19f50c410bfefd1d9b1a13e7c; ComCat M ≥ 6,0 yanıtlarının
sha256'ları, pencere başına maskeli paylar). Önhesap segment orta noktasıyla ve listedeki W'lerin birleşimiyle yapıldı
(17 tetikleyici, 71 pencere-segment + Parkfield). Koşuda tetikleyici ve Parkfield pencerelerinin maskesi bu dosyadaki varış anlarından §6.5.1a kuralıyla
kurulur; negatif pencerelerinki manifestte aynı kodla üretilir (§3.5 b). Sonuçlar §6.5 madde 1a'da.

**3.5 Koşu manifesti (dalga formundan önce commit edilir).** Koşu kodu, hiçbir dalga formu istemeden önce şunları üretir
ve commit eder: (a) §3.1–§3.4 dosyalarının sha256 denetimi; (b) yerel katalog maskesi (§6.5.1) için EMSC (seismicportal
fdsnws/event) ve ComCat sorgu yanıtları, negatif pencereler için E1 sorgu yanıtları (§6.5.1a) ve sha256'ları; (c) her
kanalın StationXML özeti: duyarlılık S, örnekleme hızı, sayısallaştırıcı bit sayısı b (StationXML'de yoksa
"bilinmiyor"), 0,02 Hz ve 1 Hz'teki yanıt oranı ve PGV uygunluğu (§6.6), g(f) = |H(f)|/S değerleri f = 2, 4, 6 ve 8 Hz'te;
g ∉ [0,5, 2] olan kanal sayısı segment başına bilgi satırına yazılır; (d) indirme planı (istasyon, kanal, başlangıç–bitiş,
servis, planlı istek sayısı). Dalga formu indirildikçe manifest satırı: istek, HTTP kodu, bayt, miniSEED sha256, örtü
kesri. Ham miniSEED depoya girmez, işlendikten sonra silinir (§6.1).

**3.6 Veri sınırı.** Bütün tetikleyiciler ≤ 2025-12-31; listede en geç pencere Kamçatka 2025-07-29 (W sonu
2025-07-30T00:27:26). Hiçbir pencere 2026-01-01'i geçemez (negatif kontroller dahil). Bütün katalog sorgularının bitişi
≤ 2025-12-31T23:59:59. Marmara GNSS verisine dokunulmaz.

## 4. Tetikleyici birimleri ve K0

**4.1 Birimler.** Bağımsızlık birimi "birim"dir:
- Wharton Basin 2012 ana şoku (official20120411083836720_20) ile 2 saat sonraki artçısı (usp000jhjb) tek birimdir
  (`WHARTON2012`). Birimde iki pencere vardır; birim, pencerelerinden en az biri bir segmentte ≥3 istasyonla
  taranabiliyorsa o segmentte sayılır, pencerelerinden birinde algılama varsa algılama sayılır. **Birimin kaba τ'su,
  K0-tam'dan sağ çıkan pencerelerindeki olayların kaba τ'larının en büyüğüdür** (Ö1). Önsayımda iki pencere de
  listede olduğundan değer ana şokunkidir (S2'de 9,39 kPa; yalnız artçı kalırsa 3,68 kPa).
- Kahramanmaraş 2023'ün iki olayı (us6000jllz, us6000jlqa; bölgesel, 771–800 km) ana sayıma girmez. Aynı kodla
  taranır, ayrı **bilgi satırı** olarak yazılır (süzgeç sızıntısı ve artçı riski). Hiçbir hükmü değiştirmez.
- Listede 16 birim var; 14'ü ana sayıma girer.

**4.2 K0, yeniden sayım.** Tam taramada bir istasyon, bir pencere için şu durumlarda o pencereden düşer: W'nin ya da
R'nin örtüsü <%90 (örtü: Z kanalında, kesintisiz örnek bulunan saniye / pencere saniyesi); StationXML'de yanıt yok;
kırpılma (§6.2). Bir çift ≥3 istasyon şartını kaybederse düşer; yerine istasyon ya da çift alınmaz. K0 bu gerçek
örtüyle yeniden sayılır: segment başına, ≥3 istasyonla taranabilen ana birim sayısı n. 12 sınırı (§6.0) n'yi
değiştirmez (≥3 şartı sınırdan önce uygulanır). E1 maskesi (§6.5.1a) de n'yi değiştirmez.
- **n ≥ 8: tam bant. n = 5–7: zayıf bant. n < 5: "veri yok"**; bulgular yine bilgi satırı olarak yazılır, eleme yok.
- Bant, tetikleyici pencerelerinde hiçbir algılama hesaplanmadan önce belirlenir ve dosyaya yazılır.

**4.3 Önsayım (yoklamayla; ×1 kaba τ ≥ 2 kPa; Kahramanmaraş hariç, Wharton tek birim; 12 sınırından sonra koddan
yeniden üretildi, `tr7_onkayit_sayilar.json` `K0_on`).**

| Segment | n (×1) | bant | kaba τ₍₈₎ (kPa) | kaba τ₍ₙ₎ (kPa) | ×1/3: n / bant | ×3 (alt sınır): n |
|---|---|---|---|---|---|---|
| S1 Ganos–Saros | 9 | tam | 2,72 | 2,02 | 4 / veri yok | 9 |
| S2 Orta Marmara–Adalar | 8 | tam | 2,75 | 2,75 | 4 / veri yok | 9 |
| S3 Çınarcık–İzmit | 8 | tam | 2,75 | 2,75 | 3 / veri yok | 8 |
| S4 Sapanca–Düzce | 8 | tam | 2,76 | 2,76 | 3 / veri yok | 8 |
| S5 Bolu–Gerede | 6 | zayıf | — | 2,40 | 1 / veri yok | 6 |
| S6 Çerkeş–Tosya | 5 | zayıf | — | 2,44 | 1 / veri yok | 5 |
| S7 Güney kol | 10 | tam | 2,82 | 2,41 | 4 / veri yok | 11 |

**12 sınırı sayıları değiştirmedi:** S1 9, S2 8, S3 8 (×1); ×1/3'te 4, 4, 3. S2 ve S3 sürüm 1'de olduğu gibi 8 birimde,
tam bandın tam sınırındadır. S2/S3'te çift başına istasyon sayısı sınırdan önce 7–59, sınırdan sonra 7–12.
S2 birimleri (kaba τ, kPa): Tohoku 2011 23,25; Kamçatka 2025 12,35; Wharton 2012 9,39; Maule 2010 6,00; İran 2013
4,68; Pakistan 2013 3,97; Nepal 2015 2,82; Chignik 2021 2,75. S3 aynı sekiz birim (Tohoku 23,53 … Chignik 2,75). S1
bunlara Illapel 2015'i (2,02) ekler. Sonuç: **S2 ve S3'te tam taramada tek bir birim düşerse zayıf banda iner.** ×1/3 ile
S1–S3'ün hepsi "veri yok" bandına düşer (en çok 4 birim kalır: Tohoku, Kamçatka, Wharton, Maule). Bu, hükmün kaba τ
ölçeğine ne kadar duyarlı olduğunu önceden gösterir ve §8'deki zorunlu ölçek uyarısıyla yazılır. ×3 sütunu alt sınırdır:
yalnız ×1 adayları yoklandı.

**S5/S6'nın bağımsız satırı (K4): S5 n = 2 (Kamçatka, Chignik), S6 n = 1 (Kamçatka); ikisi de "veri yok".** Tablodaki
S5/S6 bantları yöntem karşılaştırma satırınındır (§8 sonu).

**E1'in önsayıma etkisi (bilgi; n değişmez).** Tohoku'nun S1/S2/S3 pencerelerinin W'si E1 maskesiyle %66/%65/%65
maskelidir (§6.5.1a); birim kural gereği sayılır, ama o birimde algılama şansı öteki birimlerden küçüktür. Bu, "görülmedi"
cümlesinin bilgi satırında maskeli payla birlikte yazılır (§9.1). Bu yüzden "görülmedi" cümlesinin dışlama
olasılığı n_açık ile hesaplanır (§8).

## 5. Pencereler

Her istasyon için, kendi dış merkez uzaklığı Δ (km, küresel büyük daire, R = 6371 km) ile:
- yüzey dalgası penceresi **W = [T0 + Δ/5,0 km/s, T0 + Δ/2,8 km/s + 600 s]** (hız aralığı 2,8–5,0 km/s: Love
  başından Rayleigh kodasına; 600 sn kuyruk). Değerler listede saniyeye yuvarlanmış olarak yazılıdır;
- başvuru penceresi **R = [T0 − 3600 s, T0)** (P varışından tümüyle önce; SAYIM §2.5'in somut okuması);
- indirme dolgusu: [R başı − 600 s, W sonu + 600 s] (süzgeç geçişleri için; dolgu hiçbir istatistiğe girmez).
İstasyon-tetikleyici başına R başı–W sonu açıklığının ortalaması 6314 sn (satır ortalaması 6209; en az 4393, en çok
9050); R ile W'nin yalnız toplamı istasyon-tetikleyici başına 5131 sn (satır başına 5084). W, S ve SS fazlarını dışarıda
bırakır; Hill 2013'te Tohoku'nun S'deki küçük tremor patlaması bu yüzden sayılmaz, Love ile gelen belirgin patlama W
içindedir. Parkfield için aynı formül, Δ istasyon başına. Negatif kontrol pencereleri bu pencerelerin tam gün
kaydırılmışıdır (§7.3).

## 6. İşleme zinciri (bütün sayılar sabit)

**6.0 İstasyon sınırı (Marmara ve Parkfield'da aynı; E3).** Her (pencere, segment) için örtüden geçen (§4.2)
istasyonlardan, o segmentin izine en yakın **en çok 12'si** kullanılır. Uzaklık `tr7_onkayit_sayilar.py`'deki
`nokta_cizgi` ile hesaplanır, eşitlikte ağ ve istasyon adı alfabetik sıralanır. Sınır §6.3, §6.4 (küme istasyonları),
§7.3 ve §7.4'ün hepsine uygulanır; §6.4'ün uzun periyot başvuru istasyonu ve §6.6'nın PGV istasyonları sınırın dışındadır.
Parkfield'da sınır yalnız `var_R = var_W = 1` olan 52 istasyona uygulanır.

**6.1 İndir–zarfla–sil.** obspy (pip, sürüm koşu başında `pip freeze` ile manifeste yazılır), scipy, numpy. Servis:
KO/TL/IJ/6G → KOERI; EIDA ağları → ORFEUS federatör; YH/YL → EarthScope; Parkfield → NCEDC (yoksa EarthScope).
Nezaket: servis başına en çok 2 eşzamanlı akış, aynı akışta istekler arası ≥0,5 sn, genel User-Agent; 429/503'te
Retry-After (yoksa 30 sn × deneme), en çok 2 yeniden deneme; 401/403 "kısıtlı" yazılır, atlatılmaz. Bir istasyonun
seçilen Z kanalıyla aynı konum ve bant kodlu yatay kanallar (N/E ya da 1/2) da istenir. İndirme planı her
(pencere, segment) için `iz_sira` sırasıyla ilerler; bir çiftte örtüden geçen 12 istasyon bulununca o çiftin kalan
istasyonları, başka bir çift için gerekmiyorsa, indirilmez. İşlem bittiğinde ham veri silinir; kalan yalnız aşağıdaki
1 Hz seriler (float32, npz) ve manifesttir. Seriler depo dışında `/mnt/project-files/turetme/tr7-zarf/` altında tutulur
(tahmini ≈ 0,92 GB, Parkfield ile ≈ 1,0 GB: 475 × 11 pencere × 7 seri × 6314 sn × 4 B; 12 sınırıyla 391 istasyon-tetikleyici); depoya yalnız
dosya başına sha256 manifesti girer. **MDA kaydı (K6):** her (segment, negatif pencere, A basamağı) için algılama E/H ve
enjeksiyon başlangıcı depoda `tr7_mda.csv`'ye yazılır. MDA'nın yeniden üretimi yeniden indirme gerektirir; yeniden
indirilen miniSEED'in sha256'sı manifesttekinden farklıysa sonuç "veri değişti" notuyla yazılır.

**6.2 İstasyon düzeyi (her bileşen ayrı).**
1. Ortalama ve doğrusal eğilim çıkarılır; 1/2 bileşenleri StationXML yönelimiyle N/E'ye döndürülür.
2. Kırpılma: W içinde, ham sayımın mutlak en büyük değerine eşit ≥5 ardışık örnek varsa ve bu değer
   ≥ min(10⁶; 0,95 · (2^(b−1) − 1)) sayımsa istasyon o pencereden düşer (b: manifest (c)'deki bit sayısı;
   bilinmiyorsa b = 24, yani eşik 10⁶).
3. Yüksek frekans yolu: sayım / InstrumentSensitivity (m/s). 4 kutuplu Butterworth bant geçiren, ileri-geri (sıfır
   faz; obspy `bandpass, corners=4, zerophase=True`): **2–8 Hz** ve **0,5–1 Hz**. Hilbert zarfı (scipy, kesintisiz
   her parçada ayrı; parçaların ilk ve son 10 sn'si atılır). 1 sn'lik kutularda ortalama → 1 Hz zarf e(t).
4. Uzun periyot yolu: `remove_response(output="VEL", pre_filt=(0.005, 0.01, 0.15, 0.2), water_level=60)`, sonra
   **0,02–0,1 Hz** 4 kutuplu sıfır fazlı Butterworth; N/E → R/T (geri azimut istasyondan dış merkeze); tam saniyelerde
   örneklenir → v_Z, v_R, v_T (1 Hz, m/s).
5. Birleşik zarf C(t) = √(ortalama_bileşen e(t)²) (yatay yoksa yalnız Z). Saklanan seriler: e_Z, e_N, e_E (2–8 Hz),
   C₀,₅₋₁ (0,5–1 Hz birleşik), v_Z, v_R, v_T.
6. L(t) = log10(5 sn merkezli kayan ortalama C). m = medyan(L, R), σ = 1,4826 · MAD(L, R) (R'nin kenardaki 5'er sn'si,
   R'deki maskeli (§6.5.1, 1a) ve kayıtsız saniyeler hariç). σ = 0 olursa istasyon o pencereden düşer. 0,5–1 Hz için
   aynı tanımla L_d, m_d.
7. **Aşım:** W içinde L > m + 4σ olan saniyeler. Aradaki boşluğu ≤20 sn olan aşım saniyeleri tek parçada birleşir.
   Parça, açıklığı ≥30 sn ve aşım saniyesi ≥15 ise "istasyon aşımı"dır. Maskelenen (§6.5.1, 1a) ya da kayıtsız
   saniyeler aşım değildir ve köprülenmez (içinde maskeli ya da kayıtsız saniye bulunan boşluk birleştirilmez).

**6.3 Tutarlılık (segment düzeyi).** Bir (pencere, segment) için, istasyon aşımlarının her biri ±20 sn genişletilince
birbiriyle örtüşen ≥3 farklı istasyonun aşımları bir **küme** kurar (bağlantılı bileşen). Küme aralığı
I = [en erken başlangıç − 60, en geç bitiş + 60] ∩ W; kümenin aşım aralığı I′ = [en erken aşım başı, en geç aşım sonu].
Küme içindeki her istasyon çifti için L serilerinin I üzerindeki (maskeli saniyeler çıkarılarak) Pearson ilişkisinin
gecikme −10…+10 sn (1 sn adım) üzerindeki en büyüğü alınır. **≥3 çiftte ≥0,5** ise küme tutarlıdır. Pencere-segment
için en az bir tutarlı küme ayıklamalardan (§6.5) sağ çıkarsa: **algılama**. Görsel ya da elle seçim yoktur; hiçbir
eşik veriyle ayarlanmaz.

**6.4 Modülasyon ölçüsü (yalnız olumlu iddia için).** Her segment için "uzun periyot başvuru istasyonu": PGV'ye uygun
(§6.6), W ve R örtüsü ≥%90 olan, segment orta noktasına (köşe noktalarının ortalaması) en yakın istasyon. Yoksa
modülasyon "ölçülemedi". φ_c(t) = v_c'nin W üzerindeki analitik sinyalinin fazı (c ∈ {Z, R, T}). L_k(t) = küme
istasyonlarının L'lerinin saniye başına medyanı (maskeli saniyeler çıkarılır). Ölçü:
M = en büyük_{c, s∈{+1,−1}, gecikme 0…10 sn} Pearson(L_k, max(0, s·cos φ_c(t − gecikme))) I üzerinde.
Boş dağılım: üç bileşen birlikte, W uzunluğunda dairesel kaydırma, kaydırma tamsayı ~ U[120, |W| − 120] sn, 1000
kaydırma, üreteç `numpy.random.default_rng(20261112 + 3)` (kümeler birim, segment, zaman sırasıyla). p = (1 + #{M₀ ≥
M}) / 1001. **Modülasyon var: p ≤ 0,01.** Bu ölçü faz kilidini değil, **yüzey dalgasıyla eş periyotlu modülasyonu**
ölçer (Ö2): s ve gecikme araması 20 sn periyotta faz farkının hemen tamamını tarar, dairesel kaydırma boş dağılımı da
"periyot uyuşmuyor" hipotezini sınar. Faz yerine hızın kendisi kullanılmaz: yapay sınamada hız kullanan ilk sürüm sabit
(modülasyonsuz) tremorda %20 yanlış p ≤ 0,01 verdi.

Yapay sınama (`tr7_onkayit_modulasyon.py`, `tr7_onkayit_yapay.json`; İNCELEME-1 `tr7_inc1_modv.py`,
`tr7_inc1_modreal.py`; bu sürüm `tr7_onkayit_denetim2.py` D5b; dispersiyonlu 40→15 sn paket, 200 kaydırma):
p ≤ 0,01 oranı kilitli tremorda A = 0,5 / 0,7 / 1,0 için 1,00 / 1,00 / 1,00 (gerçek zarf zincirinde A = 0,7 / 1 / 2'de
1,00); sabit tremorda 0,00 (A 1 ve 3); rastgele patlamalı tremorda 0,00 (A 1 ve 3); **20 sn sabit periyotlu, dalgaya
kilitli olmayan tremorda 0,36–0,47 (sürüm 2, A = 1 ve 3, iki tohum; İNCELEME-1: 0,33–0,56)** (SNR ile artar; bilinen zayıflık §12). Arama daraltılınca (yalnız s = +1,
gecikme 0–5 sn) kilitsiz A = 1'de 0,31; daraltma sorunu çözmez, metin bu yüzden aramayı değiştirmez.

**6.5 Ayıklama kuralları (tetikleyici, negatif ve Parkfield pencerelerine aynen).**
1. **Katalog maskesi.** Marmara: EMSC (KOERI ve AFAD katkılı) ve ComCat; Parkfield: ComCat. Büyüklük türü serbest.
   Sorgu aralığı [R başı − 1 sa, W sonu]. İki katalogdan herhangi birinde şartı sağlayan her kayıt maskelenir; kayıtlar
   eşleştirilmez (birleşim). Segment izine ≤150 km ve M ≥ 2,0 olan her olay için [t₀, t₀ + d/3 km/s + 60 s]; ≤1000 km ve
   M ≥ 4,0 olan her olay için [t₀, t₀ + d/3 km/s + 180 s] maskelenir (d: olayın ize uzaklığı). Maskeli saniyeler bütün
   istasyonlarda aşım dışıdır. R'deki maskeli ve kayıtsız saniyeler m ve σ hesabından, I'daki maskeli saniyeler Pearson
   ilişkisinden ve L_k'dan çıkarılır. Sorgular bir kez yapılır, sha256'larıyla manifeste girer (§3.5).

1a. **Teleseismik cisim dalgası maskesi (E1; büyüklük ve süre kuralı İNCELEME-1'den saptı, §17 S1).** Her pencere için
   (tetikleyici, negatif ve Parkfield) ComCat'ten [R başı − 3 sa, W sonu] aralığındaki bütün M ≥ 6,0 olaylar alınır;
   tetikleyici olayın kendisi dışarıda kalır (aynı olayın ComCat'teki başka kimlikli kaydı, yani T0'a ±5 sn içinde ve
   M ≥ 7,0 olan kayıt, de tetikleyici sayılır; §3.4 önhesabında bu kural hiçbir kaydı düşürmedi) (Wharton biriminde
   öteki olay dahildir). Her olay için segment orta
   noktasına (Parkfield'da iz köşe ortalamasına) Δ ile `obspy.taup.TauPyModel("iasp91")` üzerinden, olay derinliğinde
   t_P (adı P ile başlayan fazların en erkeni: P, Pdiff, PKP…) ve t_S (adı S ile başlayan fazların en erkeni)
   hesaplanır. Maskelenen aralıklar:
   - **M ≥ 7,0:** [t₀ + t_P − 10 s, t₀ + t_P + 240 s] ve [t₀ + t_S − 10 s, t₀ + t_S + 240 s];
   - **6,0 ≤ M < 7,0:** yalnız [t₀ + t_P − 10 s, t₀ + t_P + 60 s].

   Maske bütün istasyonlarda geçerlidir (§6.5.1'deki maske gibi: aşım değildir, köprülenmez). Sorgu yanıtı sha256'sıyla
   manifeste girer (tetikleyici ve Parkfield pencereleri için §3.4'te donduruldu). Pencere başına maskeli saniye payı
   çıktı tablosuna (§9.1) yazılır. Bu madde birim sayımını (§4.2) değiştirmez.

   Önhesap (§3.4; W'nin maskeli payı, segment orta noktasıyla): **Tohoku S1/S2/S3 %66/%65/%65**, Parkfield W %58 ve K1
   aralığı (§7.2 b) %65 (en uzun açık parça 173–174 sn; K-a, §18); Maule %5; Illapel S1 %10; Kahramanmaraş %9; Kamçatka %4; öteki
   S1–S3 pencereleri %0. Tohoku penceresinde 3 M ≥ 7,0 (Parkfield; Marmara'da 4) ve 25 (Marmara'da 24–25) M 6,0–6,9
   cisim dalgası varışı var. İNCELEME-1'in metni olduğu gibi uygulansaydı (M ≥ 6,0, P ve S, +240 sn) Tohoku'nun bütün
   Marmara pencereleri ve Parkfield K1 penceresi **%100** maskelenirdi (§17 S1).

   K1 aralığında açık parçalar: 06:16:01–06:17:29 (88 sn), 06:18:39–06:18:48, 06:20:57–06:23:51 (174 sn),
   06:25:35–06:26:37 (62 sn) ve 06:31:29–06:31:30. Toplam ~334 sn. Grup hızıyla kaba kestirimde (iz köşe ortalaması,
   Δ = 8171 km) Love başı 4,6–4,4 km/s ile 06:16:00–06:17:21'e düşer ve açıktır. Love'ın 4,2–4,0 km/s bölümü
   (06:18:50–06:20:27) maskelidir. Rayleigh 3,9–3,7 km/s (06:21:19–06:23:12) açıktır. Hill 2013'ün özeti tremor
   patlamalarını fazlarla ilişkilendirir, saat vermez; patlamaların açık parçalara düştüğü **özetten doğrulanamadı**.
   Marmara'da (S2 orta noktası, Δ ≈ 8971 km) Love başı (06:18:54–06:20:23) maskelidir. Açık süre Tohoku S1 / S2 / S3'te
   690 / 712 / 718 sn'dir (%34–35); ≥ 30 sn'lik açık parçalar S2'de 127, 180, 76 ve 263 sn'dir.
2. **Darbe kuralı (kataloglanmamış yerel deprem).** Kümedeki her istasyon için, o istasyonun kümedeki aşım
   parçalarından C'nin (yumuşatılmamış) en büyük değeri c_p en büyük olan parça değerlendirilir; c_p'nin zamanı t_p.
   [t_p − 2, t_p) içinde C ≤ c_p/8 olan bir saniye varsa **ve** (t_p, t_p + 20] içinde C ≤ c_p/2 olan bir saniye varsa o
   istasyon "darbe"dir. İstasyonların ≥ yarısı darbe ise küme atılır.
3. **Sızıntı kuralı (Ö6; değerlendirme saniyeleri İNCELEME-1'den saptı, §17 S8).** Kümedeki her istasyon için, o
   istasyonun kümedeki aşım parçalarının içinde kalan aşım saniyeleri (L > m + 4σ, maskesiz) üzerinde
   Δ_y = medyan(L − m) (2–8 Hz) ve Δ_d = medyan(L_d − m_d) (0,5–1 Hz birleşik zarf) hesaplanır (log10 genlik artışı;
   σ ile bölünmez). Δ_d ≥ Δ_y ise istasyon "sızıntı"dır. İstasyonların ≥ yarısı sızıntı ise küme atılır.

3a. **Taban kayması (Ö4).** Kümedeki istasyonların ≥ yarısında, istasyonun kümedeki aşım parçalarından biri
   W′_son − 60 sn'ye ya da daha sonrasına kadar sürüyorsa küme atılır. W′_son, o istasyonun kendi W'si içinde
   maskelenmemiş (§6.5.1, 1a) ve kayıtlı olan son saniyedir. W sonu maskeli ya da kayıtsızsa W′_son, ondan önceki son
   açık saniyedir. Kural tetikleyici, negatif ve Parkfield pencerelerine aynen uygulanır. (İNCELEME-2: sürüm 2'nin
   "W sonu − 60" tanımı, Tohoku'nun S1–S4 ve S7 pencerelerinde, W'nin son 144–222 sn'si E1 ile maskeli olduğu için hiç
   çalışamazdı.)
4. Ayıklanan küme sayısı ve nedeni (maske, darbe, sızıntı, taban) her pencere için yazılır.

**6.6 Ölçülen dinamik gerilme (karar: ana değer değil, zorunlu ikinci değer).** PGV'ye uygun istasyon: bant kodu B ya
da H, alet kodu H, StationXML yanıt genliği |H(0,02 Hz)| / |H(1 Hz)| ≥ 0,5 (dalga formu görülmeden manifeste yazılır).
Her (pencere, segment) için PGV_ölç = uygun istasyonlarda en büyük_{t∈W} max(|v_Z|, |v_R|, |v_T|) değerlerinin
medyanı; τ_ölç = G · PGV_ölç / c (G 30 GPa, c 3,5 km/s; 1 cm/s ≈ 85,7 kPa). Uygun istasyon yoksa "ölçülemedi"
(yanıt düzeltmesi yapılamadığı açıkça yazılır). Bilgi: yalnız düşey PGV ile τ.

Gerekçe: (i) bant (§4.2) ve hüküm cümlesinin X'i veri görülmeden sabitlenmiş kaba τ'ya bağlı kalmalı, yoksa hangi
tetikleyicinin sayılacağı veriye bakılarak değişir; (ii) yüzeyde ölçülen PGV de 20–30 km derinlikteki fay üstü
gerilmenin kaba bir vekilidir (Hill 2013'te tek olay için 0,7–10 kPa); (iii) yine de literatür eşikleri (Chao 2011:
0,1 cm/s ≈ 7–8 kPa) ölçülmüş PGV'den hesaplanır, bu yüzden τ_ölç hükümde zorunlu ikinci değerdir. Kural (§8):
n_ölç = τ_ölç ≥ 2 kPa olan ana birim sayısı; bant_ölç = aynı bant kuralıyla. Hüküm türü değişmez; ölçek uyarısı §8'de.

## 7. Kapılar ve kontroller (sıra: KD → kod incelemesi → manifest → K1 → K0-tam → K2 ve MDA → tetikleyici pencereleri → hüküm)

**7.1 KD, kod denetimi (yalnız yapay veri).** Kod yalnız yapay veriyle geliştirilir. Koşu kodunun kendisi (aynı
fonksiyonlar, 100 Hz, Butterworth) yapay girdiyle şu denetimlerden geçmelidir; biri kalırsa kod gerçek veri görülmeden
düzeltilir ve "koşu öncesi düzeltme" başlığıyla kayda geçer. Kod metne uygun olduğu hâlde bir denetim kuralın kendisi
yüzünden kalırsa (bağımsız referans betik de aynı sonucu verirse), kural gerçek veri görülmeden, yalnız yapay sonuçlara
dayanarak ve bağımsız bir incelemeden geçerek "koşu öncesi ek" başlığıyla değiştirilebilir. Referans değerler bu ön kayıt
için bağımsız yazılmış `tr7_onkayit_yapay.py` (D1–D3) ve `tr7_onkayit_denetim2.py` (sürüm 2'de eklenenler; toplayıcı
`tr7_onkayit_denetim2_kos.py`, çıktı `tr7_onkayit_denetim2.json` ve D12b'nin ikinci tohumu için `--ek` ile
`tr7_onkayit_denetim2_ek.json`) ve D12c, D15 için İNCELEME-2'nin `tr7_inc2_taban.py`, `tr7_inc2_taban_ek.py`
betikleri (kök oturum `kayit/turetme/tr7/` altına kopyalar) ile önceden hesaplandı (sürüm 3'te D12c'nin referansı
`tr7_onkayit_d12c.py`, D15'inki `tr7_onkayit_denetim3.py`; toplayıcı `tr7_onkayit_denetim3_kos.py`, çıktı
`tr7_onkayit_denetim3.json`): FFT ile |H|² süzgeç, 20 Hz;
durağan Gauss gürültüsü (D7c/D7d'de ayrıca "kentsel": 2–8 Hz gürültüye ≈300 sn'lik rastgele ×exp(0,35 z) genlik
oynaması); 3 istasyon; 100 pencere; iki bağımsız tohum (20261112 + 300 + i ve 4242 + i). Genlik tanımları: **A_etkin**
= tremorun etkin (zarf > 0) örneklerindeki bileşen başına 2–8 Hz RMS / gürültünün bileşen başına 2–8 Hz RMS'i (D2, D3,
D7, D7b, D7c'de); **A_300** = tremorun 300 sn'lik süresi boyunca (sıfır yarım dönemler dahil) aynı RMS (D10, D13, D14;
§7.4). 20 sn yarım sinüs zarfta A_300 = 0,7065 · A_etkin (zarftan hesaplandı). Ani başlangıçlı sinyallerde (D6, D6b, D7d,
D12) genlik başlangıçtan sonraki ilk 5 sn'deki RMS'tir. Her satırda "doğru" iki tohumun değeri, "yanlış" bilinen yanlış
kodun aynı pencerelerdeki değeridir; bant, doğrunun içinde, yanlışın dışında kalacak biçimde konuldu.

| # | Denetim (yapay) | Şart (kabul bandı) | Doğru kod (tohum 1 / 2) | Bilinen yanlış kod |
|---|---|---|---|---|
| D1 | Durağan Gauss, 3 istasyon, 200 pencere, tremor yok | yanlış algılama ≤ 0,01 | 0/200 (İNCELEME-1: 0/400) | — |
| D2 | Aynı, A_etkin basamağı 10^(j/40); 3 istasyon; A50, A90 P'nin log10 A'ya göre doğrusal ara değerlemesiyle | A50 ∈ [0,56, 0,67], A90 ∈ [0,59, 0,72] | A50 ≈ 0,61, A90 ≈ 0,645 (İNCELEME-1: iki tohum, bant içinde) | 3σ: A50 ≈ 0,52; 5σ: ≈ 0,70 (dışarıda) |
| D3 | Aynı, 8 istasyon, 100 pencere | A50 ∈ [0,52, 0,62] | ≈ 0,57 / ≈ 0,565 | — |
| D4 | Modülasyon (dispersiyonlu paket; kilitli tremor A = 0,7, 100 pencere, 1000 kaydırma) | p ≤ 0,01 oranı ≥ 0,90 | 1,00 (200 kaydırmayla) | — |
| D5 | Modülasyon, sabit ve rastgele patlamalı tremor (A = 1 ve 3) | p ≤ 0,01 oranı ≤ 0,05 | 0,00 | hız kullanan ilk sürüm: 0,20 |
| D5b | Modülasyon, 20 sn periyotlu kilitsiz yarım sinüs tremor, A = 1 ve 3, 100 pencere, 200 kaydırma | p ≤ 0,01 oranı ∈ [0,25, 0,65] (şart değil, oran yazılır; dışına düşerse kod incelenir) | A = 1: 0,39 / 0,38; A = 3: 0,47 / 0,36 | boş dağılım dairesel kaydırma yerine faz serisinin karıştırılması: A = 1: 0,88; A = 3: 0,74 |
| D6 | Yapay yerel deprem (ani başlangıç, C ×20 ve ×100 sıçrama, 5 sn e-katlı sönüm), katalogsuz, 100 pencere | **×100'de** algılanmama ya da darbeyle atılma ≥ 0,95; aynı olay katalogdaysa maske ile atılma 1,00. ×20 yalnız bilgidir (olay algılanmadığı için darbe kuralını sınamaz) | ×100: 1,00 / 1,00 (algılama 0,48 / 0,48, algılananların hepsi darbeyle; İNCELEME-2 tohum 777007: 1,00, algılama 0,51); katalogda maske ile 1,00 / 1,00; bilgi ×20: 1,00 / 1,00 (algılama 0,00 / 0,00) | darbe kuralı 5 sn yumuşatılmış C'de: ×100: 0,52 / 0,52 (777007: 0,49) |
| D6b | Yapay yerel deprem; P tepenin 1/4'ü, S–P = 3, 5 ve 8 sn; ×20 ve ×100; katalogsuz; 100 pencere | **×100, S–P = 8: algılanmama ya da darbeyle atılma ≥ 0,90.** ×20 (bütün S–P'ler) ve ×100 S–P 3 / 5 yalnız bilgidir (§17 S9) | ×100, S–P 8: 0,96 / 0,97 (İNCELEME-2 tohum 777001 / 777002: 0,96 / 0,98); bilgi: ×20, S–P 3 / 5 / 8: 1,00 / 1,00 her biri (algılama 0,00–0,03); ×100, S–P 3 / 5: 0,00 / 0,00; 0,29 / 0,27 | yumuşatılmış C: ×100, S–P 8: 0,00 / 0,00 |
| D7 | Yapay tremor A_etkin = 10 (yarım sinüs), 100 pencere; tremor W sonundan ≥ 60 sn önce biter; §6.5'in 2, 3 ve 3a kurallarıyla | darbe, sızıntı ya da taban kaymasıyla atılma ≤ 0,03 | 0,00 / 0,00 (algılama 1,00 / 1,00) | darbe ön şartı c_p/2: 0,08 / 0,11 |
| D7b | Patlamalı tremor (5–15 sn patlamalar, aralıklar üstel ortalama 15 sn, 2 sn kenar yükselmesi), A_etkin = 3, 10 ve 30 | darbe ya da sızıntıyla atılma ≤ 0,03 | A = 3: 0,00 / 0,00; A = 10: 0,00 / 0,00; A = 30: 0,01 / 0,00 | darbe ön şartı c_p/8 yerine c_p/2: A = 3: 0,05 / 0,05; A = 10: 0,05 / 0,09; A = 30: 0,09 / 0,08 |
| D7c | Spektrumu 0,5–8 Hz'te düz tremor, A_etkin = 3 ve 10; Gauss ve kentsel gürültü | sızıntıyla atılma ≤ 0,05 | A = 3 Gauss: 0,00 / 0,00; A = 10 Gauss: 0,00 / 0,00; A = 3 kentsel: 0,00 / 0,00; A = 10 kentsel: 0,00 / 0,00 | İNCELEME-1 metni (Δ küme aralığı I'nın medyanıyla): A = 3 Gauss: 0,44 / 0,42; A = 10 Gauss: 0,22 / 0,24; A = 3 kentsel: 0,09 / 0,14; A = 10 kentsel: 0,14 / 0,17; sürüm 1'in z kuralı: A = 3 Gauss: 0,00 / 0,00; A = 10 Gauss: 0,00 / 0,00; A = 3 kentsel: 0,13 / 0,18; A = 10 kentsel: 0,33 / 0,35. İNCELEME-1 değişkesini ayıran satırlar Gauss satırlarıdır. Kentsel A = 3'te bu değişke bağımsız bir tohumla 0,04 verdi (İNCELEME-2 tohum 777005). |
| D7d | Yapay bölgesel deprem kodası (0,5–8 Hz, genlik ∝ f⁻¹, 1 sn yükselme, 40 sn e-katlı sönüm, ×20); Gauss ve kentsel | sızıntıyla atılma ≥ 0,95 | Gauss: 1,00 / 1,00; kentsel: 1,00 / 1,00 | eşitsizlik ters (Δ_y ≥ Δ_d): Gauss: 0,00 / 0,00; kentsel: 0,00 / 0,00 |
| D8 | Birim: sıfır gürültüye 100 nm/s RMS 2–8 Hz bileşen; bilinen duyarlılık | ölçülen RMS ±%5; §6.6 PGV'si bilinen PAZ yanıtlı 20 sn sinüste ±%5 | — | — |
| D9 | Pencere: bilinen Δ ve T0 | W ve R listedeki değere ±1 sn; 2026 sınırı ihlali kodu durdurur | — | — |
| D10 | Kestirici (§7.5, I′), A_etkin = 3, 100 pencere; sabit ve yarım sinüs tremor | kestirilen / A_300 ∈ [0,90, 1,15] (ikisinde de) | sabit 1,03 / 1,03; yarım sinüs 1,04 / 1,04 | I (±60 sn): sabit 0,87 / 0,87; yarım sinüs 0,88 / 0,88; payda A_etkin: yarım sinüs 0,735 / 0,735 |
| D11 | Bant ve hüküm cümlesi üretici: elle kurulmuş senaryolar (§8'in her dalı, K1'in (a)–(d) dalları ve ölçek uyarısı ön eki dahil) | metin birebir | — | — |
| D12 | 3 istasyon, 100 pencere; W içine eş zamanlı (istasyonlar arası ±2 sn) yapay teleseismik P zarfı: ani başlangıç, C ×5 sıçrama, 60 sn e-katlı sönüm | maskesiz algılanır; olay katalogda (M ≥ 7,0 kuralı, +240 sn) iken maske ile atılma 1,00 | maskesiz algılama 1,00 / 1,00; maske ile atılma 1,00 / 1,00 | maske kuyruğu +60 sn: 0,00 / 0,00 |
| D12b | Aynı, 6,0 ≤ M < 7,0 vekili: C ×2, ×3, ×5 sıçrama, 30 sn e-katlı sönüm; ×5 ve 60 sn sönüm (bilgi) | 30 sn sönümlülerde +60 sn maske ile atılma ≥ 0,95. Bilinen yanlış kodu ayıran satır ×5'tir; ×2 ve ×3 ayırmaz. Kuyruk uzunluğunun asıl denetimi D12c'dir | ×2: 1,00 / 1,00; ×3: 1,00 / 1,00; ×5: 1,00 / 1,00 (İNCELEME-2 tohum 777003: 1,00); bilgi ×5, 60 sn sönüm: 0,00 | maske kuyruğu +30 sn: ×5: 0,38 / 0,32 (777003: 0,32); ×2 ve ×3: 1,00 (ayırmaz) |
| D12c | E1 maskesi birim sınaması (deterministik). Elle kurulmuş katalog: M 6,95, 6,99, 7,00 ve 7,9 olaylar; P ve S varışları; tetikleyicinin kendisi; tetikleyiciye ±5 sn içinde M ≥ 7,0 ikinci kimlikli kayıt; Wharton biriminin öteki olayı; W dışında kalan bir varış. Ayrıca koşu kodu, tetikleyici ve Parkfield pencerelerinin maskesini `tr7_e1_maske.csv`'den segment orta noktasıyla kurar | Elle kurulmuş katalogda maskelenen saniye kümesi, §6.5.1a'dan elle hesaplanan kümeyle birebir aynı. Gerçek varışlarda W maskeli payı ve K1 aralığının maskeli payı ±0,001 içinde: Tohoku S1 / S2 / S3 0,664 / 0,654 / 0,645; Parkfield W 0,578; K1 aralığı [06:16:01, 06:31:48] 0,647 (613 / 947 sn) | — | +30 sn kuyruk, M 6,x S'nin maskelenmesi (Parkfield W 0,791) ya da 7,0 sınırının "> 7,0" yazılması birebir karşılaştırmada kalır |
| D13 | MDA basamak kuralı (§7.4): A_300 basamakları 10^(j/20), yarım sinüs, 3 istasyon, tam ayıklama | A50_basamak ∈ [0,42, 0,48], A90_basamak ∈ [0,44, 0,53] | A50 0,447 / 0,447, A90 0,501 / 0,501 (ara değerlemeyle A50 0,427 / 0,425, A90 0,474 / 0,459) | sürüm 1 basamağı 10^(j/8): A50 = A90 = 0,562 / 0,562 |
| D14 | Yanıtla çarpılmış enjeksiyon (§7.4): kanal yanıtı 4,5 Hz jeofon (g = 0,20 / 0,63 / 0,88 / 0,96, f = 2 / 4 / 6 / 8 Hz); A50 yer biriminde (A_300), iki bağımsız tohumun oranı | A50(tohum 2) / A50(tohum 1) ∈ [0,93, 1,07] ve A50 ∈ [0,55, 0,67] | A50 0,610 / 0,606 (oran 0,994); A90 0,652 / 0,630 | yanıtsız düz enjeksiyon: A50 0,428 / 0,430 (yanıtlının 0,70 katı: A90 bu kadar iyimser çıkar) |
| D15 | Taban kayması (§6.5.3a): tremor yok; 3 istasyon, 100 pencere; 2–8 Hz gürültü W başından 300 sn sonra 900 sn içinde doğrusal ×2'ye yükselir, W sonuna kadar ×2 kalır; (a) maskesiz, (b) W'nin son 120 sn'si maskeli | ayıklamasız algılama ≥ 0,90 ve 3a ile atılma ≥ 0,95, (a)'da ve (b)'de | algılama 1,00; (a): 1,00 / 1,00; (b): 1,00 / 1,00 (İNCELEME-2 `tr7_inc2_taban.py`, tohum 9201 / 9202 ve 9203 / 9204) | 3a yok: atılma 0,00 (darbe ve sızıntıdan sağ 1,00; `tr7_inc2_taban_ek.py`, tohum 9301 / 9302, 50 pencere); sürüm 2'nin "W sonu − 60" tanımı (b)'de: 0,00 / 0,00 |

Bilgi satırları (şart değil): R'den W sonuna doğrusal ×2 yükselen 2–8 Hz gürültü (Ö4), 100 pencere: ayıklamasız
algılama 0,00. Bu eğim W içinde tutarlı küme kuramayacak kadar küçüktür, 3a'yı sınamaz. 3a'nın ayırt edici
denetimi D15'tir. 20 sps BH
benzeri yanıtta (7 Hz'te dik alçak geçiren; g = 1,00 / 1,00 / 0,98 / 0,25) düz enjeksiyonun A50'si yanıtlıdan
0,429 / 0,443 = 0,97 katıdır.

**Sürüm 3 doğrulaması (İNCELEME-2 ile yeni ya da yeniden tanımlanan satırlar; `tr7_onkayit_denetim3_kos.py`, çıktı
`tr7_onkayit_denetim3.json`; iki bağımsız tohum 20261112 + 500 + i ve 6262 + i, 100 pencere; bilinen yanlış kod aynı
pencerelerde).** D6 ×100: algılanmama ya da darbeyle atılma 1,00 / 1,00 (algılama 0,49 / 0,55); katalogda maske ile 1,00 / 1,00; yanlış (yumuşatılmış C) 0,51 / 0,45. D6b ×100, S–P 8: 0,95 / 0,97 (bant ≥ 0,90; ilk tohumun değeri eski ≥ 0,95 bandının tam sınırında, İ2-E2'nin öngördüğü durum); yanlış 0,00 / 0,00. D15 (a) maskesiz: algılama 1,00 / 1,00, 3a (W′_son) ile atılma 1,00 / 1,00; yanlış: 3a yok 0,00 / 0,00. D15 (b) son 120 sn maskeli: algılama 1,00 / 1,00, 3a (W′_son) ile atılma 1,00 / 1,00; yanlış: 3a yok 0,00 / 0,00, sürüm 2'nin "W sonu − 60" tanımı 0,00 / 0,00. D12c (`tr7_onkayit_d12c.py`, rastgele katalog tohumları 20261616 / 6266): elle kurulmuş katalogda maskelenen küme elle hesaplanan kümeyle birebir aynı (bağımsız kaba kuvvet uygulaması da birebir); tohumlu rastgele kataloglarda 20/20 ve 20/20 birebir; gerçek varışlarda Tohoku S1 / S2 / S3 0,665 / 0,654 / 0,645, Parkfield W 0,578, K1 aralığı 0,647 (613 / 947 sn), hepsi ±0,001 içinde. Yanlış kodlar: +30 sn kuyruk (Parkfield W 0,457), M 6,x S'si (Parkfield W 0,791), "> 7,0" (elle katalogda 430 sn fark; Tohoku ve Parkfield pencerelerinde M = 7,0 olay yok), ikiz kaydın dışlanmaması ve Wharton'ın öteki olayının dışlanması: hepsi birebir karşılaştırmada kalır. Doğru kod her satırda bandın içinde, bilinen yanlış kod
bandın dışındadır; hiçbir denetim "bilgi"ye indirilmedi. D15'in (a) satırında sürüm 2 tanımı maskesiz pencerede doğru
kodla aynı sonucu verir (W′_son = W sonu); ayıran (b) satırıdır.

D2'nin bandı (≈ ±%9) eşik çarpanı 4σ yerine 3σ ya da 5σ kullanan bir kodu ayırır (yapayda A50 0,52 / 0,70) ve yanlış
birim ya da yumuşatmasız zarf gibi kaba hataları yakalar. Bağımsız tohumlarla yinelendi (İNCELEME-1 §E: P(0,596) =
0,295 / 0,345 / 0,29; P(0,631) = 0,805 / 0,85 / 0,80). Referans betik `tr7_onkayit_yapay.py` kümeyi komşuluk olarak
kurar; koşu kodu ve `tr7_onkayit_denetim2.py` §6.3'teki bağlantılı bileşeni kullanır. D2 ve D3 bantları bu fark için
yeterince geniştir (K5). Not: SAYIM §2.7'deki "≥30 sn kesintisiz aşım" kuralı 20 sn yarım sinüs modüleli tremoru
A = 1,0'da bile 0/100 algıladı; §6.2 madde 7'deki boşluk köprüleme bu yüzden konuldu (§15).

**7.2 K1, pozitif kontrol: Parkfield–Tohoku 2011.** Kod incelemesinden ve manifestten sonra, Marmara'nın hiçbir dalga
formundan önce. Aynı kod, aynı sabitler; istasyonlar `tr7_parkfield_liste.csv`'de `var_R = var_W = 1` olan 52 istasyon,
12 sınırıyla (§6.0); segment Parkfield izi (§3.2); katalog ComCat; E1 maskesi §3.4'teki önhesaptan.

**K1 sonucu (sıra bağlayıcı).**
- (a) Tohoku penceresinde ≥3 istasyon örtüsü yoksa: **"ölçü sınanamadı (Parkfield verisi yok)"**.
- (b) Tohoku penceresinde, aşım aralığı I′ (§6.3) **[2011-03-11T06:16:01, 06:31:48] UTC** aralığıyla kesişen en az
  bir algılama varsa (§6.3 ve §6.5, E1 maskesi dahil; aralık, iz ortasında T0 + Δ/4,6 km/s ile T0 + Δ/3,0 km/s
  arasıdır, Δ = 8171,4 km, en yakın saniyeye yuvarlanmış; `tr7_onkayit_sayilar.json` `parkfield.K1_araligi`;
  İNCELEME-1'deki 06:16:00 kesilmiş değerdir): **K1 GEÇTİ**. N_PK, ≥ 3 istasyonu kalan Parkfield negatif
  pencerelerinin sayısıdır. f_PK bunlardan W'nin herhangi bir yerinde algılama (§6.3, §6.5) verenlerin sayısıdır.
  N_PK < 5 ise K1 "geçti, ayırt edici değil" yazılır. Ayrıca Parkfield'ın negatif pencerelerinde
  FAR_PK = f_PK / N_PK > 0,30 ise (N_PK = 10'da f_PK ≥ 4) K1 **"geçti, ayırt edici değil"** olarak yazılır ve
  Marmara'da "VAR" hükmü verilemez (en çok "aday").
- (b′) **Belirsiz geçme.** (b)'yi sağlayan kümelerin hepsinde I′ başı şu iki durumdan birindeyse K1 **"geçti,
  belirsiz (cisim dalgası açıklaması dışlanamadı)"** olarak yazılır:
  (i) bir E1 maske aralığının bitişinden sonraki ilk 5 sn içinde (0 ≤ I′ başı − maske sonu ≤ 5 sn);
  (ii) tetikleyicinin kendi PKKP, SKKP, PKKS, PKIKPPKIKP ya da PKPPKP varışının [−10, +120] sn içinde. Varışlar
  iasp91 ile, olay derinliğinde, iz köşe ortalamasına hesaplanır; Parkfield'da PKKP 06:17:29, PKIKPPKIKP 06:25:30
  UTC (öteki üç faz taup'ta bu uzaklıkta yok).

  Bu durumda Marmara verisi indirilir, ama Marmara'da "VAR" verilemez (en çok "aday") ve her "görülmedi" cümlesinin
  sonuna "(K1 yalnız belirsiz geçti)" eklenir. (b′), "geçti, ayırt edici değil" etiketiyle birlikte de yazılabilir.
- (c) Algılama yoksa ve Parkfield MDA'sı (§7.4 yöntemi, Parkfield negatif pencerelerinde) tanımlıysa ve
  A90_PK ≤ 100 µm/s ise: **"ölçü sınanamadı (Tohoku tremoru Parkfield yüzey ağının gürültüsünde görülmedi;
  A90_PK = [..] nm/s)"**.
- (d) Öteki durumlar: **"ölçü sınanamadı (yöntem)"**.

(b) dışındaki her durumda Marmara verisi indirilmez ((b′), (b)'nin bir alt durumudur; Marmara verisi indirilir).

**Uygulama hatası yolu (bir kez).** K1 (c) ya da (d) ile kalırsa ve kodun bu metne aykırı olduğu, K1 verisine
bakılmadan yazılmış bir yapay denetimle gösterilirse, kod bir kez düzeltilir. Düzeltme bağımsız kod incelemesinden
geçer ve K1 bir kez yeniden koşulur. Tanım, eşik, pencere, liste ve birim kuralı değişmez. Bu yol yalnız bir kez
kullanılır ve "K1 sonrası düzeltme" başlığıyla kayda geçer.

**Tanı satırları (K1'i değiştirmez).** Tohoku penceresinde ayıklamadan önceki küme sayısı ve her kümenin atılma nedeni
(maske, darbe, sızıntı, taban); K1'i geçiren her kümenin I′'su içine düşen M 6,0–6,9 P varışları (§3.4) ve
maskelenmeyen M 6,0–6,9 S varışları;
- K1 kümelerinin her biri için I′ başı ile ondan önceki en yakın E1 maske sonu arasındaki süre;
- tetikleyicinin kendi çekirdek fazlarına (b′ ii) en yakın uzaklık;
- BK.PKD'nin (`iz_sira` 14, 12 sınırının dışında; Hill 2013'ün kaydı bildirdiği istasyon) Tohoku penceresindeki
  istasyon aşımları.

HRSN (BP) kuyu koşusu bu sürümde yapılmaz (§17 S2).

**Bilgi satırları (K1'i değiştirmez).** Parkfield modülasyon p'si ("Parkfield modülasyonu geçti" = K1 aralığıyla kesişen
Tohoku kümelerinden en az birinde p ≤ 0,01; K7); Parkfield FAR_PK; tremor genliği A_PK (§7.5); A90_PK; τ_ölç / kaba τ
(Parkfield–Tohoku, §6.6 ile; uygun istasyon yoksa "ölçülemedi"). **Parkfield modülasyonu geçmezse Marmara'da "VAR"
hükmü verilemez, en çok "aday (modülasyon ölçüsü pozitif kontrolde doğrulanmadı)" yazılır.** Parkfield modülasyonu
"ölçülemedi" ise "geçmedi" sayılır.

**7.3 K2, negatif kontrol.** Her birim (Kahramanmaraş bilgi birimleri dahil) için 10 pencere; liste sürüm 2 ile
donduruldu (§3.3). Seçim kuralı: aday kaydırmalar d ∈ {−30, …, −1, +1, …, +30} gün (tam gün: aynı UTC saati, R ve W
birlikte kayar; Wharton'ın iki penceresi aynı d ile), yetmezse d ∈ {−60, …, −31, +31, …, +60}. Üreteç
`numpy.random.default_rng(20261112)`; birimler ana şok T0 sırasıyla; her birim için önce ±1–30 adayları, sonra ±31–60
adayları, ikisi de her birimde sırayla `rng.permutation` ile karıştırılır ve şu şartları sağlayan ilk 10 alınır:
(i) kaydırılmış [min R başı − 3 sa, max W sonu] aralığında ComCat M ≥ 6,5 olay yok; (ii) kaydırılmış W sonu
< 2026-01-01; (iii) kaydırılmış T0'ın yerel gün türü (Pazartesi–Cuma ya da Cumartesi–Pazar; Marmara'da Türkiye,
Parkfield'da ABD Pasifik saati; resmî tatil dikkate alınmaz) tetikleyicininkiyle aynıdır; (iv) kaydırılmış pencerenin
yerel saat farkı (yaz saati durumu), min R başında ve max W sonunda, tetikleyicininkiyle aynıdır. Parkfield için ayrı
üreteç `default_rng(20261112 + 1)`. Bütün birimlerde 10 pencere ±30 gün içinde bulundu (§3.3). Yerel M ≥ 3 olan
pencereler atılmaz: yerel depremler tetikleyici pencerelerinde de §6.5 ile ayıklanır, simetri korunur (§15). Negatif
pencerede örtü kuralı aynıdır; ≥3 istasyonu kalmayan pencere düşer, yerine pencere alınmaz. E1 maskesi negatif
pencerelere de uygulanır (M ≥ 6,5 olaylar seçimde dışlandığından yalnız 6,0 ≤ M < 6,5 olayların P'si).

Segment başına N = kullanılabilir negatif pencere sayısı (ana birimlerin), f = algılama sayısı, FAR = f/N. Wharton
biriminin bir negatif penceresi iki alt pencereden oluşur: N'ye 1 katkı yapar, alt pencerelerden birinde algılama varsa
algılama sayılır. **K2: FAR ≤ 0,05** (f ≤ ⌊0,05 N⌋; N = 80 için f ≤ 4). Kalırsa o segmentin hükmü "ölçü güvenilmez"
olur; eşik değişmez; tetikleyici bulguları bilgi satırı olarak yazılır. **N < 5n ise** o segmentin hükmü "ölçü
güvenilmez (negatif kontrol yetersiz)" olur. Negatif pencereler ve MDA tetikleyici pencerelerinden önce işlenir ve
dosyaya yazılır.

**7.4 Algılanabilir en küçük tremor genliği (MDA).** Koşu sırasında, yalnız negatif kontrol pencerelerine
(tetikleyici pencerelerinin dışında), algılama vermemiş her negatif pencereye ham veri bellekteyken yapay tremor
eklenir. Model: kaynak segment orta noktasının 25 km altında; istasyon i'de genlik A·25/r_i (r_i hiposantr uzaklığı),
varış gecikmesi r_i / 3,5 km/s; üç bileşende eşit RMS, her istasyon ve bileşende bağımsız Gauss gerçekleşmesi, 2–8 Hz
süzülmüş; zarf 300 sn, 20 sn periyotlu yarım sinüs, 10 sn kenar yumuşatma (yapay sınamayla aynı); başlangıç W'nin
göreli konumunda U[60, |W| − 360] sn. Üreteç `default_rng(20261112 + 2)`. Çekiliş sırası: önce Parkfield (negatif
pencereler `tr7_negatif_pencere.csv` sırasıyla, pencere başına üç başlangıç), sonra Marmara (segment S1…S7, birimler ana
şok T0 sırasıyla, pencereler `sira` ile). Her denemede önce başlangıç, sonra istasyon ve bileşen sırasıyla (`iz_sira`;
Z, N, E) Gauss gerçekleşmeleri çekilir. Algılama veren ya da düşen pencere için çekiliş yapılmaz. Parkfield'da her algılama vermemiş negatif
pencereye aynı üreteçle üç ayrı başlangıç çekilir (deneme = pencere × başlangıç); Marmara'da pencere başına bir başlangıç.
**A basamakları 10^(j/20) nm/s, j = 0…100** (1 nm/s – 100 µm/s). Yapay tremor eklenmeden önce, frekans ortamında
kanalın StationXML yanıtının normalize edilmiş karmaşık değeri H(f)/InstrumentSensitivity ile çarpılır; böylece veri ile
yapay sinyal aynı ölçekte kalır (Ö5; D14). Süzgeç ve Hilbert doğrusal olduğundan zarf |a_veri + A·a_yapay| olarak her
basamak için hesaplanır; R'ye ekleme yapılmaz. P(A) = algılama veren deneme payı (segment başına), ana birimlerin
algılama vermemiş negatif pencerelerinden (Parkfield'da denemelerinden) **en az 20** tanesiyle hesaplanır; daha azsa
A90 "belirsiz" yazılır. **A50 ve A90, P ≥ 0,5 ve P ≥ 0,9 olan ve üstündeki bütün basamaklarda da bu şartı sağlayan en
küçük basamaktır** (adım ×1,122). Hiçbir basamak ulaşmazsa "> 100 µm/s". **A, kaynağın tam üstünde (25 km) tremorun
300 sn'lik süresi boyunca (sıfır yarım dönemler dahil) bileşen başına 2–8 Hz RMS'tir (nm/s; A_300).** §7.1'deki yapay A
(A_etkin, etkin örneklerde) ile bağıntı: A_300 = 0,7065 · A_etkin. D2 ve D3 bantları A_etkin ölçeğindedir. MDA algılama
içindir, modülasyon şartını içermez.

**7.5 Tremor genliği kestiricisi (bilgi).** Algılanan kümede istasyon i için a_i = √(max(0, ⟨C²⟩_I′ − ⟨C²⟩_R) · 2/π),
I′ = [kümedeki en erken aşım başı, en geç aşım sonu]; 25 km'ye indirgenmiş a_i · r_i / 25; segment değeri medyan
(A_300 ölçeğinde kestirir; D10). Parkfield'daki A_PK bu tanımla, K1'i geçiren kümeden (birden çoksa en büyüğü).
**Bilgi satırı: her Marmara segmenti için A90(S_k) / A_PK** ("Parkfield'daki Tohoku tremoru bu gürültüde görülür
müydü"). A_PK = 0 ya da tanımsızsa (K1 geçmedi) oran "tanımsız" yazılır.

## 8. Hüküm kuralları (tam sayısal; sıra bağlayıcı)

Tanımlar, segment başına: n (K0-tam ana birim), bant (§4.2), N, f (§7.3), X_alg = algılama veren ana birim sayısı,
X_mod = algılama veren **ve** o algılama kümelerinden en az birinde modülasyon p ≤ 0,01 olan ana birim sayısı.
p_üst = f/N için tek yanlı %95 Clopper–Pearson üst sınırı. X_min(n, f) = P(Bin(n, p_üst) ≥ X) ≤ 0,05 olan en küçük X,
en az 2; X ∈ [2, n] arasında şartı sağlayan yoksa X_min yoktur ve o segmentte "VAR" verilemez. N, o segmentin ana
birimlerinden kullanılabilir negatif pencere sayısıdır (Wharton: §7.3). X_min, algılama FAR'ından hesaplanır ve X_mod'a
uygulanır; bu bilerek tutucu bir seçimdir. Önceden hesaplanmış X_min (`tr7_onkayit_sayilar.json` `X_min_tablo`, N = 10n;
"K2" = K2 kalır):

| n | N | f = 0 | f = 1 | f = 2 | f = 3 | f = 4 | f = 5 |
|---|---|---|---|---|---|---|---|
| 5 | 50 | 2 | 3 | 3 | K2 | K2 | K2 |
| 6 | 60 | 2 | 3 | 3 | 3 | K2 | K2 |
| 7 | 70 | 2 | 3 | 3 | 3 | K2 | K2 |
| 8 | 80 | 2 | 3 | 3 | 3 | 3 | K2 |
| 9 | 90 | 2 | 3 | 3 | 3 | 4 | K2 |
| 10 | 100 | 2 | 3 | 3 | 3 | 4 | 4 |

(FAR = 0,05'te 8 birimde rastlantıyla ≥2 algılama olasılığı 0,057, bu yüzden düz "≥2" yetmez. Kaynak yokken en az bir
algılama olasılığı 1 − 0,95ⁿ: n = 8'de 0,337, n = 9'da 0,370; "aday" hükmü büyük olasılıkla bundan çıkar ve aday kalıbı
bunu taşır.)

**Marmara özeti için kuyruk eşiği 0,05/3 (Ö3).** Özetin "gözlendi" cümlesi için en az bir S1–S3 segmentinde
X_mod ≥ X_min^(0,05/3)(n, f) gerekir (tanım aynı, kuyruk eşiği 0,0167; N = 10n), f = 0…5 sırasıyla:
n = 5: 3, 3, 3, K2, K2, K2; n = 6: 3, 3, 3, 4, K2, K2; n = 7: 3, 3, 4, 4, K2, K2; n = 8: 3, 3, 4, 4, 4, K2;
n = 9: 3, 3, 4, 4, 4, K2; n = 10: 3, 3, 4, 4, 4, 4. Segment satırı 0,05'lik X_min ile yazılır. S1, S2 ve S3 aynı
istasyonları paylaştığı için üç segmentin sınamaları bağımsız değildir; 0,05/3 bu bağımlılıkta da tutucudur.

Sıra:
1. K1 (a), (c) ya da (d) → bütün segmentler **"ölçü sınanamadı ([K1 nedeni])"**.
2. bant = veri yok (n < 5) → **"veri yok"** (bulgular bilgi satırı).
3. N < 5n → **"ölçü güvenilmez (negatif kontrol yetersiz)"** (bulgular bilgi satırı).
4. K2 kaldı → **"ölçü güvenilmez"** (bulgular bilgi satırı).
5. X_min var ve X_mod ≥ X_min(n, f) ve Parkfield modülasyonu geçti ve K1 "ayırt edici değil" değil ve K1 "belirsiz"
   (§7.2 b′) değil ve uzun periyot başvuru istasyonu var → **"tetiklenmiş tremor VAR"**.
6. X_alg ≥ 1 ve 5 sağlanmıyor → **"aday, doğrulanmadı"** (X_alg = 1 ise her durumda bu).
7. X_alg = 0 → **"görülmedi"**.

Dışlama oranı: n birimde algılama yoksa, tetikleyici başına ≥ p_min olasılıkla A90'ı aşan tremor üreten bir
kaynak %95 düzeyinde dışlanır; p_min = (1 − 0,05^(1/n_açık)) / 0,9. n_açık, taranan ana birimlerden W'sinin
maskeli payı (§6.5.1 ve 1a birlikte, segment orta noktasıyla, §9.1) ≤ 0,50 olanların sayısıdır. MDA'nın ölçüldüğü
negatif pencerelerde E1 yalnız M 6,0–6,4 P'lerini kapattığı için, W'sinin yarısından çoğu maskeli bir birim
A90 duyarlılığıyla taranmış sayılmaz. Bu kural n'yi ve bandı değiştirmez. Değerler: n_açık 5 → 0,50; 6 → 0,44;
7 → 0,39; 8 → 0,35; 9 → 0,32; 10 → 0,29. n_açık < 5 ise dışlama cümlesi yerine "dışlama hesaplanmadı (W'si
yarıdan az maskeli birim < 5)" yazılır. Önsayımda Tohoku'nun S1–S3 W'si %65–66 maskeli olduğundan n_açık
S1 / S2 / S3 için 8 / 7 / 7, p_min 0,35 / 0,39 / 0,39'dur. (Koddan: `tr7_onkayit_sayilar3.py`,
`tr7_onkayit_sayilar3.json`; önsayımda §6.5.1'in yerel katalog maskesi henüz yoktur, pay yalnız 1a'dan.)

**Hüküm kalıpları (yalnız bu biçimlerde; köşeli yerler koddan doldurulur):**
- VAR: "S_k: tetiklenmiş tremor VAR. n bağımsız tetikleyicinin X_mod'unda, yerel deprem ve teleseismik cisim dalgası
  maskesi ile darbe/sızıntı/taban ayıklamasından sonra ≥3 istasyonda tutarlı ve yüzey dalgasıyla eş periyotlu
  modülasyonlu (p ≤ 0,01; ölçü faz kilidini 20 sn periyodik, kilitsiz modülasyondan ayıramaz, yapayda yanlış pozitif
  0,33–0,56) 2–8 Hz tremor (tetiklenmiş yerel mikrodeprem kümesi darbe kuralının ayırabildiği kadar dışlandı); negatif kontrolde FAR = f/N; kaba τ ≥ [en küçük algılayan birimin kaba τ'su] kPa
  (ölçülen τ ≥ [..] kPa)."
- Aday: "S_k: aday, doğrulanmadı. [X_alg] tetikleyicide algılama; negatif kontrole göre n tetikleyicide beklenen yanlış
  algılama n·f/N = [..], P(Bin(n, p_üst) ≥ X_alg) = [..]; VAR şartlarından sağlanmayan: [liste]."
- Görülmedi: "S_k: kaba τ ≥ X kPa üstündeki n bağımsız tetikleyicide (n_açık'ının W'si en az yarı yarıya maskesiz)
  tetiklenmiş tremor görülmedi; algılanabilir en küçük genlik A90 = [..] nm/s (25 km'de, 300 sn boyunca 2–8 Hz RMS;
  A50 = [..]); tetikleyici başına ≥ p_min(n_açık) olasılıkla bu genliği aşan tremor üreten bir kaynak %95 düzeyinde
  dışlanır. [bant zayıfsa: 'zayıf bant'.] Ölçek
  uyarısı: kaba τ ×1/3 alınırsa [n₁/₃] birim ≥ 2 kPa ([bant₁/₃]); ölçülen τ ile [n_ölç] birim ≥ 2 kPa ([bant_ölç]);
  Parkfield–Tohoku'da τ_ölç / kaba τ = [..]." Burada X = kaba τ₍ₙ₎ (taranan ana birimlerin en küçük kaba τ'su).
  bant₁/₃ ya da bant_ölç "veri yok" ise cümle "S_k (yalnız kaba τ ölçeğinde):" ile başlar. n_açık < 5 ise dışlama
  yan cümlesinin yerine "dışlama hesaplanmadı (W'si yarıdan az maskeli birim < 5)" yazılır. K1 (b′) ile geçtiyse
  cümlenin sonuna "(K1 yalnız belirsiz geçti)" eklenir (§7.2).
- Veri yok / ölçü güvenilmez / ölçü sınanamadı: o sözcüklerle (parantez içi nedeniyle), ardından bilgi satırları.
- **Zorunlu ×1/3 satırı** (her segment, her hükümde): "Kaba τ ×1/3 alınırsa [n₁/₃] birim ≥ 2 kPa (bant: ..)." ×3
  satırı da yazılır (alt sınır notuyla).

Marmara özeti (S1–S3 birlikte): en az bir segment VAR ve o segmentte X_mod ≥ X_min^(0,05/3) ise "Marmara'da dinamik
gerilmeye duyarlı derin kayma bölgesi gözlendi"; üçü de "görülmedi" ise "bu duyarlılıkla (A90 ve kaba τ değerleriyle)
gözlenmedi"; özete giren bir segmentte "(yalnız kaba τ ölçeğinde)" ön eki varsa özet cümlesi "bu duyarlılıkla (A90 ve
kaba τ değerleriyle; kaba τ ölçeği ×1/3'te ya da ölçülen τ ile veri yok bandında) gözlenmedi" olur; öteki durumlarda
segment satırları özetsiz yazılır. S4–S7 ikinci satırlardır, özete girmez. Her segmentin "VAR" cümlesinin sonuna
"(segment düzeyi α = 0,05; yedi segment için düzeltilmedi; X_min^(0,05/7) = [..], [sağlandı | sağlanmadı])" eklenir.
X_min^(0,05/7) aynı tanımla, kuyruk eşiği 0,00714 ile hesaplanır. N = 10n'de f = 0…5 için: n = 5: 3, 3, 4, K2, K2,
K2; n = 6: 3, 4, 4, 4, K2, K2; n = 7: 3, 4, 4, 4, K2, K2; n = 8: 3, 4, 4, 4, 5, K2; n = 9: 3, 4, 4, 4, 5, K2;
n = 10: 3, 4, 4, 4, 5, 5. (Koddan: `tr7_onkayit_sayilar3.json` `X_min_tablo_005_7`.) S5/S6'da 2005–2008 birimleri (Kashmir 2005,
Kuril 2006, Kuril 2007, Bengkulu 2007; YL verisi, Pfohl 2015'in incelediği veri) ayrı satırda "yöntem karşılaştırması,
bağımsız değil" diye yazılır; S5/S6'nın bağımsız satırı yalnız 2009 sonrası birimlerle (S5: Kamçatka, Chignik, n = 2;
S6: Kamçatka, n = 1) kurulur ve bant kuralına tabidir: önsayımda ikisi de "veri yok". Kahramanmaraş satırları ayrı ve
yalnız bilgi.

**Hüküm ve K1 etiketleri: özet tablo.** Bu tablo §7.2 ve §8'in kurallarını bir arada gösterir, yeni kural içermez;
çelişkide §7.2 ve §8'in metni geçerlidir.

| Durum (kural) | Yazılan kalıp | Marmara koşusuna ve hükmüne etkisi |
|---|---|---|
| K1 (b), (b′) değil, ayırt edici | "K1 GEÇTİ" | Marmara verisi indirilir; §8 sırasının bütün hükümleri verilebilir |
| K1 (b′) | "geçti, belirsiz (cisim dalgası açıklaması dışlanamadı)" | Marmara verisi indirilir; "VAR" verilemez (en çok "aday"); her "görülmedi" cümlesinin sonuna "(K1 yalnız belirsiz geçti)" |
| K1 (b) ve FAR_PK > 0,30 ya da N_PK < 5 | "geçti, ayırt edici değil" ((b′) şartı da sağlanıyorsa iki etiket birlikte yazılır) | Marmara verisi indirilir; "VAR" verilemez (en çok "aday"); (b′) de varsa iki etki birlikte |
| Parkfield modülasyonu geçmedi ya da "ölçülemedi" (bilgi satırı; K1 dalını değiştirmez) | "Parkfield modülasyonu geçmedi" | "VAR" verilemez; en çok "aday (modülasyon ölçüsü pozitif kontrolde doğrulanmadı)" |
| K1 kaldı: (a), (c) ya da (d) | "ölçü sınanamadı (Parkfield verisi yok)" / "ölçü sınanamadı (Tohoku tremoru … görülmedi; A90_PK = [..] nm/s)" / "ölçü sınanamadı (yöntem)" | Marmara verisi indirilmez; bütün segmentler "ölçü sınanamadı ([K1 nedeni])"; (c) ve (d)'de uygulama hatası yolu bir kez |
| Segment: n < 5 | "veri yok" | bulgular bilgi satırı |
| Segment: N < 5n | "ölçü güvenilmez (negatif kontrol yetersiz)" | bulgular bilgi satırı |
| Segment: K2 kaldı | "ölçü güvenilmez" | bulgular bilgi satırı |
| Segment: §8 sıra 5 sağlandı | "tetiklenmiş tremor VAR" (+ "(segment düzeyi α = 0,05; …; X_min^(0,05/7) = [..], [sağlandı \| sağlanmadı])") | özete ancak X_mod ≥ X_min^(0,05/3) ise "gözlendi" olarak girer |
| Segment: X_alg ≥ 1, sıra 5 sağlanmadı | "aday, doğrulanmadı" | özete girmez; segment satırı özetsiz yazılır |
| Segment: X_alg = 0 | "görülmedi" (dışlama p_min(n_açık) ile; n_açık < 5 ise "dışlama hesaplanmadı (W'si yarıdan az maskeli birim < 5)") | S1–S3'ün üçü de "görülmedi" ise özet "bu duyarlılıkla (A90 ve kaba τ değerleriyle) gözlenmedi"; özete giren bir segmentte "(yalnız kaba τ ölçeğinde)" ön eki varsa §8'deki uzun özet cümlesi |

## 9. Çıktı tabloları

`tr7_sonuc.json` ve `tr7_sonuc.md` (tek koşu, "x" kipinde):
1. Birim × segment: birim, olay(lar), T0, M, kaba τ, kaba τ ×1/3, τ_ölç (ve uygun istasyon sayısı), örtüden geçen
   istasyon sayısı ve 12 sınırıyla kullanılan, W'nin ve R'nin maskeli saniye payı (§6.5.1 ve 1a ayrı; payda: segment
   orta noktasıyla, istasyon W'lerinin (R'lerinin) birleşimi), küme sayısı,
   ayıklanan küme (maske / darbe / sızıntı / taban), algılama E/H, modülasyon p, en uzun küme süresi, a (§7.5), o birimin
   negatif pencerelerinde f/10; her algılama kümesi için darbe sayılan istasyon payı ve istasyon başına
   c_p / medyan_I′(C)'nin medyanı (bilgi).
2. Segment: n, n_açık ve p_min(n_açık), bant, n_ölç ve bant_ölç, N, f, FAR, p_üst, X_alg, X_mod, X_min,
   X_min^(0,05/3) ve X_min^(0,05/7), A50, A90 (deneme
   sayısıyla), A90/A_PK, kaba τ₍ₙ₎, ×1/3 ve ×3 satırları, g ∉ [0,5, 2] olan kanal sayısı, hüküm cümlesi.
3. K1 satırı ((a)–(d) dalı) ve Parkfield tanı ve bilgi satırları; KD sonuçları; manifest özeti (istek, HTTP dağılımı,
   bayt, düşen istasyon ve nedeni); negatif pencerelerin gün türü ve yerel saat farkı dağılımı (bilgi).

## 10. Koşu sırası, körlük, tek koşu

1. Bu ön kayıt iki bağımsız incelemeden geçti (İNCELEME-1, İNCELEME-2) ve düzeltildi (sürüm 3); "DONDURULDU"
   başlığıyla commit + push edilir.
2. Kod yazılır; **yalnız yapay veriyle** geliştirilir ve KD (§7.1) geçer. Gerçek hiçbir dalga formu (Parkfield dahil)
   indirilmez. Kod incelemesi yapılır ("koşulabilir" hükmü gerekir).
3. Manifest (§3.5) üretilir ve commit edilir (üstveri ve katalog; dalga formu yok).
4. K1: önce Tohoku penceresi indirilir ve zarflanır (algılama yok). Sonra Parkfield negatif pencereleri indirilir
   ve işlenir (algılama, FAR_PK, MDA). En son Tohoku penceresinde algılama yapılır ve K1 dalı yazılır. (b) ve (b′)
   dışındaki her dalda dur (§7.2).
5. Marmara: önce bütün tetikleyici pencereleri indirilir ve zarflanır (algılama yok); örtü ve K0-tam bandı
   yazılır. Sonra negatif pencereler indirilir ve işlenir; K2 ve MDA yazılır. Sonra tetikleyici pencereleri zarf
   deposundan işlenir. En son hüküm.
6. **Tek koşu (Ö8).** Koşu kodu her aşamanın başında, depodaki `kayit/turetme/tr7/TR7_KOSU_DURUM.json`
   dosyasına aşama adını yazar, commit ve push eder. Push başarısızsa aşama başlamaz. Aşamalar sırayla şunlardır:
   manifest, K1-indirme, K1-negatif, K1-algılama, Marmara-indirme, Marmara-negatif, Marmara-algılama, hüküm.
   Aynı bilgi depo dışında bir bekçi dosyasına (`TR7_GERCEK_KOSU_BASLADI`) da yazılır. **Algılama aşamaları**
   K1-negatif, K1-algılama, Marmara-negatif ve Marmara-algılama'dır. Bunlardan birine bir kez girilmişse koşu, §7.2'deki
   uygulama hatası yolu dışında yeniden başlatılmaz. Bir algılama aşamasında duran koşu, durma nedeni kayda
   geçtikten sonra kaldığı pencereden sürdürülür; o ana dek yazılmış algılama ve MDA satırları yeniden hesaplanmaz.
   Algılama aşamalarından önce duran koşu kaldığı aşamadan sürdürülür. Her iki durumda da kod değişikliği yalnız
   indirme ve ayrıştırma katmanında yapılabilir ve "koşu öncesi düzeltme" başlığıyla yazılır. Çıktı ne olursa olsun
   yazılır.
   - **Servis hatası** (5xx, zaman aşımı; 204/404 değil): payın paydası manifest (d)'deki planlı istek sayısıdır. Pay
     %10'u aşarsa koşu, hiçbir algılama hesaplanmadan durur ve tek bir yeniden deneme turu yapılır. Yeniden deneme
     turundan sonra pay hâlâ %10'dan büyükse eksik istasyon-pencereler örtü kuralıyla (§4.2) düşer ve koşu sürer.
   - **Biçim hatası:** miniSEED ya da StationXML ayrıştırılamazsa ve payı (payda: HTTP 200 dönen istasyon-pencere
     sayısı) %1'i aşarsa, ya da §3'teki herhangi bir dosyanın sha256'sı uyuşmazsa, koşu hiçbir algılama hesaplanmadan
     durur; "veri yok" yazılmaz; yukarıdaki sürdürme kuralı geçerlidir.
   - **Servis ve biçim hatası için ortak (İNCELEME-2):** Paylar her indirme yapan aşama (K1-indirme, K1-negatif,
     Marmara-indirme, Marmara-negatif) için ayrı hesaplanır. Bir algılama aşamasında "hiçbir algılama hesaplanmadan
     durur", "o aşamanın kalan pencereleri işlenmeden durur" demektir.
   - Herhangi bir algılama değeri görüldükten sonraki her kod değişikliği "koşu sonrası değişiklik" başlığıyla yazılır;
     tanım, eşik, liste ya da birim kuralı değişmez.

Körlük beyanı (sürüm 3'te değişmedi; sürüm 3 için hiçbir dalga formu erişimi yapılmadı): Ek 1 yoklamasında 935 adet 10 sn'lik Marmara isteği, sürüm 2 için 112 satırlık (120 HTTP isteği)
Parkfield yoklaması yapıldı; ikisinde de yalnız HTTP kodu ve bayt sayıldı, içerik çözülmedi ve diske yazılmadı. SAYIM
§4'teki iki erişim denemesinin içeriği de açılmadı. Bugüne dek hiçbir Marmara ya da Parkfield dalga formu işlenmedi. E1
ve negatif pencere önhesapları yalnız katalogdan. Yazar Kahramanmaraş'ın başka bölgelerde tremor tetiklediğini (Inbal
2024; Yao 2024) ve Hill 2013'ü literatürden biliyor; Marmara için yayımlanmış bir tremor gözlemi bulunamadı (SAYIM §8).

## 11. Önceden beyan edilen beklenti

En olası sonuç **"görülmedi"**dir ve bu önceden kabul edilir; ölçümün asıl ürünü A90 ve hangi kaba τ'nun üstünde kaç
bağımsız tetikleyici tarandığıdır. Yazarın sınav öncesi güveni (Marmara özeti): görülmedi (tam ya da zayıf bant) 0,50;
aday 0,10; VAR 0,03; ölçü sınanamadı (K1 kalır) 0,25; veri yok ya da ölçü güvenilmez 0,12. Sürüm 1'e göre "ölçü
sınanamadı" yükseltildi: E1 maskesi K1 aralığının %65'ini kapatıyor (en uzun açık parça 173–174 sn) ve K1 artık
zamanlı. Açık ~334 sn'lik K1 parçalarından Love başına (88 sn) ve Rayleigh başına (174 sn) düşenler sınamayı taşır. K1'in
"belirsiz" geçmesi (b′) ayrı bir olasılık olarak beklenir. S2
ve S3 tam bandın tam sınırında olduğundan (n = 8) zayıf banda inme olasılığı yüksektir. Yapay sınamaya göre durağan
gürültüde A50 bileşen başına gürültü RMS'inin ~0,6 katıdır (A_etkin; A_300 ölçeğinde ~0,43); gerçek kentsel gürültü
durağan olmadığı için σ ve dolayısıyla A90 daha büyük çıkacaktır. Mutlak A90 değeri önceden kestirilmedi.

## 12. Bilinen zayıflıklar

- **Kültürel gürültü.** S2/S3 istasyonlarının çoğu KO yüzey istasyonudur; 2–8 Hz gürültü yüksek ve gündüz/gece,
  hafta içi/sonu değişkendir. Negatif kontrol aynı UTC saatini, gün türünü ve yaz saati durumunu eşler (§7.3); resmî
  tatiller eşlenmez. S2'nin 4 biriminde (Tohoku, Maule, Nepal, Chignik) R yerel sabah artışının içinde, W sonrasında;
  taban kayması kuralı (§6.5.3a) yalnız W′_son − 60 sn'ye kadar süren aşımları atar, W içinde sönen bir yükselişi
  atmaz. Yapayda W içinde ×2 yükselen gürültü, 3a olmadan %100 tutarlı küme verir. 3a bunları atar (D15). W içinde yükselip
  yine W içinde sönen bir artış atılmaz; negatif kontrol bunu yalnız aynı saat, gün türü ve yaz saati eşlemesi kadar
  ölçer.
- **Teleseismik cisim dalgaları (E1).** Maske M ≥ 7,0 için P ve S'yi 240 sn, 6,0 ≤ M < 7,0 için yalnız P'yi 60 sn
  kapatır. Daha uzun P kodası ya da görünür S veren bir M 6,x olay maske dışında kalan bir kümeyi açıklayabilir:
  yapayda C ×5, 60 sn sönümlü bir P +60 sn maskeyle 0,00 oranında atılır (D12b). Tohoku penceresinde Parkfield'da
  25 M 6,0–6,9 varışı var. Bu risk K1 tanı satırıyla görünür kılınır, giderilmez. +60 sn kuyruk M 6,x için pP, sP ve
  PcP'yi örter (73–81°'de P'den 7–16 sn sonra). PP'yi (P'den 164–183 sn sonra) örtmez. Tetikleyicinin kendi geç çekirdek
  fazları (PKKP, P′P′) maskelenmez. M ≥ 8,5 tetikleyicilerde bunlar W içindedir: Tohoku–Parkfield PKKP 06:17:29,
  PKIKPPKIKP 06:25:30; Tohoku–S2 PKKP 06:17:13, SKKP/PKKS 06:20:48–52, PKIKPPKIKP 06:25:17. K1'de (b′) ile görünür
  kılınır; Marmara'da bilgi satırına yazılır.
- **Tetiklenmiş mikrodepremlilik (R4).** Darbe kuralı S–P ≤ 5 sn'lik güçlü yerel depremleri atmaz. Tetiklenmiş
  olanlar negatif pencerelerde bulunmaz, FAR'a girmez. "VAR" bu kaynağı tümüyle dışlamaz.
- **Kuyu sensörü yok.** GONAF kuyu sismometreleri açık FDSN'de yok (yalnız gerinimölçer). Parkfield pozitif kontrolü
  bu yüzden kuyu istasyonlarını dışarıda bırakır; Hill 2013 tremoru PKD'de, Peng 2009 Cholame'de büyük ölçüde HRSN
  kuyularında gördü. Parkfield kırsal, Marmara kentseldir: K1'in geçmesi duyarlılığın eşit olduğu anlamına gelmez;
  duyarlılık A90 ve A90/A_PK ile ölçülür. K1 (c) bu farkı ayrı bir sonuç olarak yazar.
- **İstasyon sayısı.** 12 sınırı (§6.0) Parkfield ile Marmara'yı ve Marmara birimlerini birbirine yaklaştırır, ama
  7–11 istasyonlu pencereler kalır; yanlış algılama olasılığı birimler arasında yine biraz farklıdır, binom şartı (§8)
  tek p varsayar.
- **6G, TL, 1O, TU verisinin yokluğu.** 6G'nin 2015 sonrası, TL ve 1O/TU'nun hiçbir isteği gelmedi (Ek 1); kısıtlı mı
  yok mu ayrılamadı. S2/S3 pratikte yalnız KO ile taranır.
- **Tek 10 sn varlık örneği.** Marmara'da her istasyon W'nin ortasındaki tek bir 10 sn'lik örnekle, Parkfield'da R ve W
  ortasındaki iki örnekle "var" sayıldı; %90 örtü doğrulanmadı. S2 ve S3'te tek birim düşmesi bandı değiştirir.
- **Kaba τ.** Prag bağıntısı ders kitabından, özetten doğrulanmadı; M>8 doygunluğu yok sayılıyor; ×1/3'te S1–S3 "veri
  yok" bandına düşer. Parkfield–Tohoku'da kaba τ 27 kPa iken Hill 2013'ün Coulomb gerilmesi 0,7–10 kPa: kaba τ
  büyük olaylarda büyük olasılıkla fazladır. Ölçek uyarısı bu yüzden hüküm cümlesinin içindedir (§8).
- **Pencere S'yi dışlar** (W 5,0 km/s'de başlar); S ile tetiklenen tremor sayılmaz.
- **Modülasyon ölçüsü** faz kilidini 20 sn periyodik, kilitsiz modülasyondan ayıramaz (yapayda %33–56, SNR ile
  artar); sabit ya da rastgele patlamalı zarflarda yanlış pozitif vermez.
- **Kanal yanıtı ve genlik ölçeği (Ö5).** S1–S3'te kısa periyot kanal yok. BH kanallarında 6–8 Hz yumuşatma süzgecine
  yakın. Enjeksiyon yanıttan geçirildiği için A90 bu yüzden iyimser değildir; mutlak genlik yine de yalnız duyarlılık
  bölmesine dayanır. Parkfield'ın ilk 12'sinin 10'u kısa periyot (EHZ/SHZ); doğal frekansları 2–8 Hz'in altındaysa
  sorun küçüktür.
- **Darbe kuralı** ani kenarlı, yüksek SNR'li patlamalı tremoru atabilir (İNCELEME-1: kutu biçimli A = 10'da 8/40);
  2 sn kenar yükselmeli patlamalarda D7b A = 3: 0,00 / 0,00; A = 10: 0,00 / 0,00; A = 30: 0,01 / 0,00. Kataloglanmamış, çok güçlü (×100) ve S–P ≤ 5 sn'lik yerel
  depremleri atmaz (D6b bilgi satırı: S–P 3: 0,00 / 0,00, S–P 5: 0,29 / 0,27; §17 S9).
- **Çoklu karşılaştırma.** S1–S3 istasyon paylaşır (Tohoku'da S2/S3 ortak 5, Nepal'de 8); özet için 0,05/3 kuyruk eşiği
  (§8) tutucudur ama bağımlılığı modellemez.
- **Kaynak modeli** (25 km derinlik, 1/r, Q yok) kabadır; A90 bir karşılaştırma ölçüsüdür, kaynak genliği değildir.
- Segment izleri elle sayısallaştırılmış (±5–10 km); orta nokta köşe ortalamasıdır; E1 maskesi segment orta noktasıyla
  hesaplanır (istasyonlar arası varış farkı birkaç saniye, maske payı −10 sn).
- Pfohl 2015'in istasyon sayısı, olay listesi ve gürültü düzeyi doğrulanamadı; S5/S6 karşılaştırması bu yüzden yalnız
  niteldir.

## 13. İstanbul'a bağ

Mutlak olasılık ya da olasılık çarpanı yazılmaz. Sonucun Marmara'ya anlamı yalnız şu iki cümleden biridir:
"dinamik gerilmeye duyarlı derin kayma bölgesi gözlendi" ya da "bu duyarlılıkla (A90, kaba τ, n) gözlenmedi". "Gözlendi"
yeni bir gözlem türü açar (tremor kataloğu, göç, ortam tremoru araması), zaman eksenine dolaylı bağlıdır ve tek başına
hiçbir tehlike sonucuna taşınmaz. "Gözlenmedi", bugünkü yüzey istasyonlarıyla tremor ölçerli izleme yolunun bu genlik
düzeyinde kapalı olduğunu söyler; kuyu sensörleri için yolu açık bırakır ve kaynağın yokluğu anlamına gelmez.

## 14. Yeniden açma şartı

Hüküm "görülmedi", "veri yok", "ölçü güvenilmez" ya da "ölçü sınanamadı" ise şu durumlardan biri yeni ön kayıtla
yeniden açar: (a) Marmara'da açık erişimli kuyu sismometresi verisi (GONAF ya da benzeri) ≥5 tetikleyiciyi kapsar;
(b) 6G, TL ya da 1O verisi açılır ve S2/S3'te ≥8 birimi ≥3 istasyonla örter; (c) 2026 sonrası bir tetikleyici
Marmara'da kaba τ ×1/3 ≥ 2 kPa verir (2026 bugün kördür, bu ön kayıtta kullanılmaz); (d) K1 kaldıysa, kuyu
istasyonlarına (HRSN/BP, PB) izin veren, başka bir Parkfield tetikleyicisini kullanan ya da algılayıcıyı değiştiren yeni
bir tasarım, yalnız yeni bir ön kayıtla. Böyle bir tasarımın ilk adayı Parkfield–Denali 2002'dir (Peng vd. 2008,
10.1029/2008gl036080: 2–8 Hz, birçok istasyonda tutarlı zarf, yüzey dalgasıyla eş periyot, Love ile uyarılmış). 2002'nin
sürekli veri varlığı bu ön kayıtta yoklanmadı.

## 15. SAYIM'dan sapmalar (veri görülmeden, gerekçeli)

1. Aşım: "≥30 sn kesintisiz" yerine boşluk ≤20 sn köprüleme, açıklık ≥30 sn ve ≥15 aşım saniyesi. Yapay sınamada eski
   kural modüleli tremoru A = 1,0'da 0/100 algıladı; yeni kural A50 ≈ 0,61'de algılıyor, tremorsuz 200 pencerede 0.
2. Modülasyon: "ilişki ≥0,3 ya da aşım W içinde" yerine faz temelli ölçü ve dairesel kaydırma boş dağılımı; yalnız
   olumlu iddia için şart, algılama için değil. Eski "W içinde başlar ve biter" seçeneği hemen her aşımda sağlanırdı.
3. Yerel deprem: "±60 sn ve 150 km içinde herhangi bir olay varsa aşım atılır" yerine büyüklüğe bağlı zaman maskesi;
   Parkfield'ın yoğun mikrodepremliliğinde eski kural K1'i olanaksız kılabilirdi. Darbe kuralı 1 Hz çözünürlüğe
   uyarlandı (eski "yükselme <2 sn" 5 sn yumuşatılmış seride hiç tetiklenemezdi).
4. Sızıntı: niteliksel "hızlı yükselirse" yerine log10 artışı karşılaştırması (§6.5.3).
5. Negatif kontrol: yerel M ≥ 3 içeren pencereler atılmaz (simetri); yalnız küresel M ≥ 6,5 dışlanır.
6. R penceresi [T0 − 3600, T0); R örtüsü de ≥%90 şartı.
7. Ana değer kaba τ; ölçülen τ zorunlu ikinci değer (SAYIM §2.1 "koşuda ölçülenle değiştirilir" diyordu).
8. "VAR" için ≥2 yerine X_min(n, f) (FAR'a bağlı binom şartı) ve modülasyon şartı.
9. Hüküm bandı Kahramanmaraş hariç ve Wharton tek birimle sayılır (kök oturum kararları 1–2).
10. Teleseismik cisim dalgası maskesi, taban kayması kuralı ve pencere başına 12 istasyon sınırı (İNCELEME-1).

## 16. Doğrulanamayanlar

Peng 2009 eşiğinin hangi PGV tanımından geldiği ve eşik üstü olaylarda tetikleme oranı; Pfohl 2015'in istasyon sayısı,
olay listesi, gürültü düzeyi ve eşiği; Parkfield'ı Tohoku'da tetikleyen tremorun 2–8 Hz genliği (A_PK koşuda ölçülür);
Prag Ms bağıntısının katsayıları (ders kitabı); Tohoku'da Parkfield yüzey istasyonlarının %90 örtüsü (yalnız iki 10
sn'lik örnek yoklandı: 52/56 "var"); teleseismik M 6,x P'nin 2–8 Hz'te Parkfield ve Marmara'da görünür olup olmadığı;
KOERI'nin 2'den fazla eşzamanlı akışa izni (kullanılmayacak); tetikleyicinin kendi PKKP ve P′P′ fazlarının 2–8 Hz'te
Parkfield ve Marmara'da görünür olup olmadığı. 2012 tarihli DOI'siz "Searching for Tectonic Tremor on
the North Anatolian Fault" kaydı okunamadı (SAYIM §8).

## 17. İnceleme metinlerinden sapmalar ve uygulanmayanlar

S1–S10 sürüm 2'nin İNCELEME-1'den sapmalarıdır; İNCELEME-2 hepsini kabul etti (S1 ve S9 eklerle; ekler sürüm 3'te
işlendi). S11–S13 sürüm 3'ün İNCELEME-2 metninden yalnız yerleşim ve tekrar bakımından ayrıldığı yerlerdir; hiçbir
eşik, tanım ya da kural değişmedi.

İNCELEME-1'in bütün bulguları işlendi (§18). Düzeltme metninden bilerek sapılan ya da uygulanmayan yerler:

- **S1 (E1, büyüklük ve süre kuralı) — İNCELEME-2: KABUL, İ2-Ö1 ekleriyle.** İNCELEME-1'in metni (M ≥ 6,0 bütün olaylar,
  P ve S, [−10, +240] sn) olduğu gibi uygulandığında ComCat'teki Tohoku artçıları (penceresinde 17 M 6,1–6,7 ve 2 M ≥ 7,7)
  yüzünden **Tohoku'nun Marmara pencereleri (S1–S4, S7) ve Parkfield K1 penceresi %100 maskelenir** (`tr7_e1_maske_ozet.json`,
  `E1-lit`). O zaman K1 (b) veri görülmeden olanaksızdır ve K1 her durumda "ölçü sınanamadı" verir; ayrıca Tohoku birimi
  hiç taranmadan n'de sayılır. İnceleme notundaki beklenti ("Love ve Rayleigh'in ana bölümü açık kalır") yalnız iki büyük
  artçıyı hesaba katmıştı. Sürüm 2'nin işleyen kuralı (E1-C): M ≥ 7,0 için metin aynen (P ve S, +240); 6,0 ≤ M < 7,0 için
  yalnız P, +60 sn. Gerekçe: teleseismik S'nin soğurulması P'ninkinden çok büyüktür (t*_S ≈ 4 t*_P), 2–8 Hz'te M < 7
  olaylarının S'si beklenmez; M 6,x P vekili (C ×2–×5, 30 sn sönüm) yapayda +60 sn ile atılır (D12b). Bedeli: Tohoku W'sinin
  %65'i, K1 aralığının %65'i maskeli kalır (İNCELEME-2: KABUL, İ2-Ö1 ekleriyle; sürüm 3'te K1 (b′), açık parçalar,
  D12c, §14 (d) Denali 2002 ve n_açık). Seçenekler ve önhesapları (W maskeli payı Parkfield / Tohoku S2; K1 aralığı;
  en uzun açık K1 parçası):

  | Değişke | Kural | Parkfield W | Tohoku S2 W | K1 aralığı | En uzun açık (K1) |
  |---|---|---|---|---|---|
  | E1-lit (İNCELEME-1) | M ≥ 6,0, P ve S, +240 | %100 | %100 | %100 | 0 sn |
  | E1-B | M ≥ 7,0 +240; 6,0–6,9 P ve S +60 | %79 | %83 | %82 | 77 sn |
  | **E1-C (sürüm 2)** | M ≥ 7,0 P ve S +240; 6,0–6,9 yalnız P +60 | %58 | %65 | %65 | 173 sn |
  | E1-A | yalnız M ≥ 7,0, P ve S +240 | %28 | %38 | %26 | 670 sn |

  E1-A, inceleme notunun beklediği durumdur ama M 6,x P'leri maskesiz bırakır (D12b: C ×2, 30 sn sönümlü maskesiz bir P
  0,96 / 0,93 (ayıklamadan sağ: 1,00 / 1,00) oranında tutarlı küme verir). Hiçbir değişke Tohoku'yu K1 için temiz bir pencere yapmaz; temiz bir
  pozitif kontrol başka bir Parkfield tetikleyicisi gerektirir ve bu yeni bir ön kayıttır (§14 d).
- **S2 (E2, kuyu listesi).** İsteğe bağlı HRSN (BP) kuyu listesi ve yoklaması yapılmadı; bu sürümün dalga formu erişim
  yetkisi 56 yüzey istasyonunun 112 isteğiyle sınırlıydı. E3'ün kuyu tanı satırı bu yüzden kaldırıldı. Yoklama 52/56 verdiği
  için PB/BP'yi K1'e alan bir seçenek metni gerekmedi.
- **S3 (E3, K1 aralığı).** "Kümesi … aralığıyla kesişen" ifadesindeki küme aralığı, I ile I′ arasındaki belirsizliği
  kapatmak için I′ (aşım aralığı) olarak tanımlandı; I'nın ±60 sn'si aralığı yapay olarak genişletirdi. Aralığın başı
  06:16:00 yerine 06:16:01 (en yakın saniye; inceleme kesmişti).
- **S4 (K1 ile E3 (c) çelişkisi).** K1'in "P(A) en az 20 negatif pencereyle" şartı, Parkfield'ın 10 negatif penceresiyle
  hiç sağlanamaz ve E3 (c)'yi olanaksız kılardı. Parkfield'da pencere başına üç enjeksiyon başlangıcı (en çok 30 deneme)
  konuldu (§7.4).
- **S5 (Ö4, negatif pencereler).** Seçim koşuya bırakılmadı, sürüm 2 ile katalogdan üretilip donduruldu (§3.3); yaz saati
  şartı pencerenin iki ucunda denetlenir; ±31–60 genişletme kümesi her birimde her zaman çekilir (üreteç akışı sonuçtan
  bağımsız). Bütün birimlerde ±30 gün yetti.
- **S6 (D. tablo, nokta 6: kırpılma).** İnceleme yalnız bit sayısının manifeste yazılmasını önerdi; sürüm 2 bunu eşiğe de
  bağladı (§6.2.2), yoksa kayda geçen bit sayısı hiçbir kuralı değiştirmezdi.
- **S7 (Ö2, D5b).** İnceleme D5b için "şart yok, beklenen 0,3–0,6" dedi; sürüm 2 bir bilgi bandı koydu ([0,25, 0,65]): şart
  değildir, dışına düşen oran kod incelemesini tetikler.
- **S8 (Ö6, sızıntı kuralının değerlendirme saniyeleri).** İNCELEME-1'in metni Δ'yı küme aralığı I'nın medyanıyla
  tanımlıyordu. Yapayda bu tanım İNCELEME-1'in kendi D7c denetimini geçemedi: 0,5–8 Hz düz tremorda sızıntıyla atılma
  0,09–0,44 (şart ≤ 0,05). Nedeni: I, aşımın ±60 sn'sini ve yarım sinüsün sıfır yarım dönemlerini içerir; medyan
  tremorsuz saniyelere düşer, Δ_y ile Δ_d'nin karşılaştırması yazı turaya döner. Sürüm 2 aynı karşılaştırmayı
  istasyonun aşım saniyelerinde yapar (§6.5.3): D7c 0,00, D7d 1,00. Sürüm 1'in z kuralı Gauss
  gürültüde D7c'yi geçer ama kentsel gürültüde geçemez (kentsel gürültüde 0,13–0,35).
- **S9 (Ö6, D6b genliği).** İNCELEME-1 D6b'nin genliğini belirtmedi; sürüm 2 şartı D6'nın ×20'siyle koymuştu
  (İNCELEME-2 İ2-E2: ×20'de olay algılanmadığı için şart darbe kuralını sınamıyordu; sürüm 3'te şart ×100, S–P 8'de,
  bant ≥ 0,90). ×100'de
  (bilgi) darbe kuralı S–P = 3 ve 5 sn'lik yerel depremleri atmaz (S–P 3: 0,00 / 0,00, S–P 5: 0,29 / 0,27): P'nin kodası S tepesinden önceki 2 sn'de
  C'yi c_p/8'in üstünde tutar. Böyle bir olay 2–8 Hz'te gürültünün ~100 katıdır; Marmara ve Parkfield katalog
  tamlığında (M ≈ 1,5–2) katalog maskesine (§6.5.1) girmesi beklenir, ama kural kataloglanmamış böyle bir olayı
  atmaz. Kural değiştirilmedi: kenarı tepeye değil başlangıca bakan bir darbe kuralı yarım sinüs tremoru atar.
- **S10 (bant sıkılaştırma).** D7 ve D7b'nin bandı ≤ 0,05 yerine ≤ 0,03: bilinen yanlış kod (darbe ön şartı c_p/2) ≤ 0,05
  bandının içine düşebiliyordu (0,05–0,09).

İNCELEME-2'nin bütün bulguları (İ2-E1–E3, İ2-Ö1–Ö8, K-a–K-g) işlendi (§19). Yerleşim ve tekrar farkları:

- **S11 (İ2-E3, §10 madde 6).** Düzeltme metni maddenin "ilk dört cümlesinin" yerine geçer. Sürüm 2'nin ardından gelen
  iki cümlesi ("Bu aşamalardan önce duran bir koşu … sürdürülür." ve "Bunun için kod değişikliği gerekiyorsa …
  yazılır.") düzeltme metninin son iki cümlesiyle aynı şeyi söylediği ve "bu aşamalar" göndermesi değiştiği için
  silindi; "Çıktı ne olursa olsun yazılır." kaldı.
- **S12 (İ2-E3, servis ve biçim hatası).** Her iki alt maddeye eklenecek metin, iki kez yazılmasın diye iki alt maddenin
  hemen altında tek bir "Servis ve biçim hatası için ortak" alt maddesi olarak yazıldı; metin harfiyen aynıdır.
- **S13 (İ2-Ö1 b, İ2-Ö2).** (b′)'nin "VAR verilemez" ve "(K1 yalnız belirsiz geçti)" sonuçları, §7.2'deki metne ek
  olarak §8 sıra 5'e ve "görülmedi" kalıbının sonuna da yazıldı; n_açık < 5 durumunun cümlesi "görülmedi" kalıbına da
  yazıldı. "(b) dışındaki her durumda Marmara verisi indirilmez" cümlesine (b′)'nin (b)'nin alt durumu olduğu eklendi.
  §8 sonuna kuralları bir arada gösteren bir özet tablo kondu (yeni kural yok); tabloda §7.2'deki "(b′), 'geçti,
  ayırt edici değil' etiketiyle birlikte de yazılabilir" cümlesi, takdir bırakmamak için "iki şart da sağlanıyorsa iki
  etiket birlikte yazılır" diye okunur.

## 18. Sürüm 1 → 2 değişiklik listesi

| Bulgu (İNCELEME-1) | Ne değişti | Bölüm |
|---|---|---|
| E1 | Teleseismik cisim dalgası maskesi (madde 1a; büyüklük/süre kuralı §17 S1), maske önhesabı dondu, D12/D12b, maskeli pay çıktıda, K1 tanı satırı | §3.4, §6.5.1a, §7.1, §7.2, §9.1, §12, §17 |
| E2 | Parkfield varlık yoklaması: 52/56 R ve W'de var; liste `var_R`/`var_W` ile yeniden üretildi; K1 kümesi 52 istasyon | §3.2, §7.2, §10, §16 |
| E3 | 12 istasyon sınırı (liste `iz_km`/`iz_sira`/`ilk12`; önsayım değişmedi); K1 (a)–(d) dalları, zamanlı geçme şartı, FAR_PK > 0,30 kuralı, uygulama hatası yolu, tanı satırları | §3.1, §4.2, §4.3, §6.0, §6.1, §7.2, §8 |
| Ö1 | Wharton τ'su sağ kalan pencerelerden; ölçek uyarısı "görülmedi" kalıbının içinde; "(yalnız kaba τ ölçeğinde)" ön eki ve özet cümlesi | §4.1, §8 |
| Ö2 | "fazına kilitli" → "eş periyotlu modülasyonlu" ve yapay yanlış pozitif oranı; D5b; §12 oranı | §6.4, §7.1, §8, §12 |
| Ö3 | X_min yoksa VAR yok; N tanımı ve Wharton negatif penceresi; N < 5n kuralı; özet için 0,05/3; n = 6, 7 satırları; aday kalıbı | §7.3, §8 |
| Ö4 | Negatif pencerelerde gün türü ve yaz saati eşleme, ±60 genişletme, liste dondu; taban kayması 3a; D7 3a ile; rampa bilgi satırı | §3.3, §6.5.3a, §7.1, §7.3, §12 |
| Ö5 | Enjeksiyon yanıtla çarpılır; manifestte örnekleme hızı ve g(f); D14; §12 kısa periyot maddesi değişti | §3.5, §7.4, §7.1, §12 |
| Ö6 | Darbe kuralında en büyük c_p'li parça; sızıntı log10 artışıyla, istasyonun aşım saniyelerinde (§17 S8); D6b (§17 S9), D7b, D7c, D7d; "kural kalırsa" yolu | §6.5.2–3, §7.1, §12, §17 |
| Ö7 | A_300 tanımı; kestirici I′; D10 yeni bant | §7.1, §7.4, §7.5 |
| Ö8 | Aşama durumu depoda `TR7_KOSU_DURUM.json`, her aşama commit; sürdürme kuralı; paydalar; ikinci turdan sonrası | §10 |
| K1 | D2 ara değerleme; MDA basamağı 10^(j/20), "üstündeki bütün basamaklarda" kuralı, ≥20 deneme; D13 | §7.1, §7.4 |
| K2 | PGV bileşenleri v_Z, v_R, v_T | §6.6 |
| K3 | Katalog birleşimi, sorgu aralığı, maskeli saniyelerin m/σ/Pearson/L_k'dan çıkarılması | §6.2.6, §6.3, §6.4, §6.5.1 |
| K4 | S5/S6 bağımsız satırı n = 2 / 1, "veri yok" | §4.3, §8 |
| K5 | Referans betik komşuluk / koşu kodu bağlantılı bileşen notu | §7.1 |
| K6 | `tr7_mda.csv` ve yeniden üretim notu | §6.1 |
| K7 | R başı–W sonu açıklığı 6314 (istasyon-tetikleyici) / 6209 (satır); A_PK tanımsızsa oran tanımsız; "Parkfield modülasyonu geçti" tanımı | §5, §7.2, §7.5 |
| D, nokta 6 | Sayısallaştırıcı bit sayısı manifestte ve kırpılma eşiğinde | §3.5, §6.2.2 |
| — | §0 öncelik sırası; durum satırı; §17 sapmalar | §0, başlık, §17 |

Dosyalar (sürüm 1 → sürüm 2 sha256):
- `tr7_dondurulan_liste.csv`: c8877cc26996010bc3c7036fd8b761791355cfad5a621dd076ed0429b40bde28 →
  0f3cbd36876a46354b46355016f949f113ddaadcce4d26b6bc9e7a0b1da4358b (3 sütun eklendi; satırlar ve eski sütunlar aynı)
- `tr7_parkfield_liste.csv`: cba4cea81a4b6b231133a99d0f2d19cce956a950885d7789390504c2aa471a77 →
  9dca3380815196a8db15a8a5929441d38dd9b07fd7ed982845543e179957b2b8 (4 sütun eklendi)
- `tr7_onkayit_sayilar.json`: 90ad2f69cb0f8ac1dcfe39fd7617f9323491b850b96ce408e2a29bde90cc3807 →
  be439bf6dec47e309671c382325f5266b69ee60949cb4cdac2d920c630452728
  (`K0_on` ve `var_kurali` sürüm 1 ile aynı)
- Yeni: `tr7_parkfield_varlik.csv` 951d7797fcbb2d4427f43f35e3b0a2ceec46e8a684421f535be70371fd5305d0,
  `tr7_parkfield_varlik_ozet.json` 71be3c1b52d78c6656bf43f64f9dec96b6a33de89b35464e3b3a898b085cce12,
  `tr7_negatif_pencere.csv` ae4fa9c1d84ff3a461c9659ffc58c5a366f82671e1df74233cb3283253a6a59b,
  `tr7_negatif_pencere_ozet.json` 16ac030f9370bc528dd0bf9669328bada317acf50481d7db76680e1b5adbcbc8,
  `tr7_e1_maske.csv` aef412df1d805fbbee65c1d4f7a76df67ce9b43ec9ee2a8bb3f1345bffccf391,
  `tr7_e1_maske_ozet.json` 128720470ea39479108329960f605bc49f3795e19f50c410bfefd1d9b1a13e7c,
  `tr7_onkayit_denetim2.json` 8d9dd1644344f5c68e01b1a5a6dd664285542a52fabc2fc48b03ee8864410b0e,
  `tr7_onkayit_denetim2_ek.json` (D12b ikinci tohum) d304e4363021c911bf126d85d857867e1e90eeeffc54906cf0c91cc5ba4ff8be

Not (İNCELEME-2 K-a): E1 önhesabında K1 aralığı 06:16:00 ile hesaplandı; 06:16:01 ile maskeli pay 0,647, en uzun açık
parça 173–174 sn (değişmez).

## 19. Sürüm 2 → 3 değişiklik listesi

| Bulgu (İNCELEME-2) | Ne değişti | Bölüm |
|---|---|---|
| İ2-E1 | 3a W′_son tanımıyla (maskeli ya da kayıtsız W sonu); §12 kültürel gürültü maddesine D15 cümlesi | §6.5.3a, §12 |
| İ2-E2 | D6 ve D6b şartı ×100'e (D6b S–P 8, bant ≥ 0,90); D12b ayırt edici satır notu; yeni D12c (deterministik E1 maske sınaması) ve D15 (3a); "bilgi satırları" ilk cümlesi; referans betik cümlesi; sürüm 3 doğrulaması (iki yeni tohum) | §7.1 |
| İ2-E3 | §10 madde 4 ve 5 (önce yalnız indirme ve zarflama, sonra negatif pencereler, en son algılama); madde 6 (aşama başında commit + push, push olmazsa aşama başlamaz; K1-negatif ve Marmara-negatif ayrı algılama aşamaları; pencereden sürdürme); servis ve biçim hatası payları aşama başına | §10, §17 S11–S12 |
| İ2-Ö1 | (a) K1 açık parçaları ve faz kestirimleri; (b) K1 (b′) "geçti, belirsiz"; (c) üç tanı satırı (BK.PKD dahil, K-d); (d) pP/sP/PcP/PP ve tetikleyicinin çekirdek fazları; (e) §14 (d) Denali 2002; (f) §11 beklenti | §6.5.1a, §7.2, §8, §11, §12, §14 |
| İ2-Ö2 | n_açık ve p_min(n_açık); "görülmedi" kalıbı; §4.3 cümlesi; §9.2 sütunu; koddan S1 / S2 / S3: n_açık 8 / 7 / 7, p_min 0,35 / 0,39 / 0,39 | §4.3, §8, §9.2 |
| İ2-Ö3 | Tetikleyicinin kendi PKKP ve P′P′ fazları: (b′ ii), §12, §16 | §7.2, §12, §16 |
| İ2-Ö4 | E1'in "ikiz kayıt" kuralı metne girdi | §6.5.1a |
| İ2-Ö5 | Rakip açıklama R4; VAR kalıbı; §9.1 darbe sütunu; §12 maddesi | §2, §8, §9.1, §12 |
| İ2-Ö6 | Segment "VAR" cümlesine 0,05/7 eki; X_min^(0,05/7) tablosu koddan (İNCELEME-2 tablosuyla aynı); §9.2 sütunu | §8, §9.2 |
| İ2-Ö7 | N_PK ve f_PK tanımı; N_PK < 5 → "ayırt edici değil" | §7.2 |
| İ2-Ö8 | Parkfield modülasyonu "ölçülemedi" → "geçmedi" | §7.2 |
| K-a | §18 notu; açık parça 173–174 sn | §6.5.1a, §11, §18 |
| K-b | Zarf deposu ≈ 0,92 GB, Parkfield ile ≈ 1,0 GB | §6.1 |
| K-c | MDA üretecinin çekiliş sırası | §7.4 |
| K-d | BK.PKD tanı satırı (İ2-Ö1 c) | §7.2 |
| K-e | Maskeli pay paydası | §9.1 |
| K-f | D7c satırına not | §7.1 |
| K-g | Değişiklik gerekmez (İNCELEME-2) | — |
| — | Durum satırı, §0 öncelik sırası (sürüm 3 > İNCELEME-2 > İNCELEME-1 > SAYIM), §17 S11–S13, §8 hüküm özet tablosu | başlık, §0, §8, §17 |

Dondurulan veri dosyaları sürüm 2 ile aynıdır (sha256'lar §3 ve §18'deki gibi; sürüm 3 bunları yeniden üretmedi ve
değiştirmedi). Sürüm 3'te eklenen ya da değişen dosyalar (sha256):
- `tr7_onkayit_sayilar3.py` 5b2c07a9a11b0d21581592b9b9b990cdf3860e4a7f248c335b72e7f96353809c
- `tr7_onkayit_sayilar3.json` 0ca41dcc21d47f92775613dc10889ee34d2398713b866d23689072d38784e4bd
- `tr7_onkayit_d12c.py` 1ca3678d4e6ea879778d9335437231cd6895aea7f25900ac06aced31a9d75ad2
- `tr7_onkayit_denetim3.py` 0b4d6f90e5f429da3d585eab83b6bdeafcd9b6b57b707c6448e46831f4192fae
- `tr7_onkayit_denetim3_kos.py` 6d8902dcc30f3a177088e44ef80a88248b547db70a2b4e3097721bf2fad938ef
- `tr7_onkayit_denetim3.json` b574bde6c763cb3a45770693fac6296a8b6d27511b8fb823f85caf59fa4515b2
- `tr7_inc2_taban.py` 43cab6187e3fabd3a6ea28776ae21de309fe3924d9fc2dbfeab8c53c4a3d085b
- `tr7_inc2_taban_ek.py` 7e73fc5fed62eb1706b33ca321a739413e4f70bb7a787ee20f9e9ebdf254cdff
- `tr7_onkayit_doldur.py` 2e8142a5ae12c3ceb95c030128c051c72ad2a1ca541662ff20f175efbdcc5b87 (değişti: sürüm 3 yer tutucuları ve `--denetle`)


---

## Dondurma notu (12 Kasım 2026, hiçbir Marmara ya da Parkfield dalga formu işlenmeden)

Bu sürüm, iki bağımsız incelemenin (İNCELEME-1, İNCELEME-2) bütün düzeltmeleri işlenerek donduruldu. Dondurma anına kadar yalnız 10 saniyelik veri varlığı yoklamaları (HTTP kodu ve bayt sayısı) yapıldı; hiçbir dalga formu çözülmedi.

**Tek açıklama (İ2-Ö2'nin boş bıraktığı yer):** iki penceresi olan Wharton 2012 birimi, n_açık sayımında iki pencerenin İKİSİNDE de maskeli pay ≤ 0,50 ise "açık" sayılır. Önsayımda iki pencerenin maskeli payı 0,000 olduğundan sayılar değişmez.

---

## Ek 1 (12 Kasım 2026, veri öncesi)

Bu ek dondurulmuş gövdeyi değiştirmez. **Gövde, bu dosyanın ilk 97 178 baytıdır** (sha256
df426ffc59793dcb75e5167aca643145d3bd55be3bb4bdcce11f58e1ea544c20). Koşu kodu (`tr7_kosu.py`, `ONKAYIT_N = 97178`)
sha'yı yalnız bu baytlar üzerinden denetler. Ek yazıldığı anda hiçbir Marmara ya da Parkfield dalga formu ve hiçbir
gerçek StationXML indirilmemiş ya da açılmamıştır. Kaynaklar: `TR-7_KODLAYICI-OKUMALARI.md` ve bağımsız kod incelemesi
`TR-7_KOD-INCELEME.md` (hüküm DÜZELTMEYLE KABUL).

**E1.1 Kodlayıcı okumalarının bağlayıcılığı.** Kod incelemesinin KABUL dediği okumalar koddaki biçimiyle bağlayıcıdır.
Aşağıdaki okumalar metnin sustuğu yerleri doldurur ve böyle bağlayıcıdır:
- O-8: σ = 0 olan istasyonun 12 sınırındaki yeri bir sonraki adaya verilmez; K0-tam'ı değiştirmez; istasyon aşım
  üretmez.
- O-9, O-65: Küme aralığının kesiştiği "W" ve MDA başlangıcının göreli olduğu "W", (pencere, segment)'in kullanılan
  istasyonlarının W'lerinin zarfıdır (en erken W başı – en geç W sonu).
- O-19: Örnekleme hızı pencere içinde değişen kanal istasyonu o pencereden düşürür ("kanal" nedeniyle yazılır).
- O-20: Uzun periyot yolu kesintisiz parça başına uygulanır, parça kenarı ayrıca atılmaz.
- O-25: D12'nin "maskesiz algılanır" şartı ≥ 0,95 oranıdır.
- O-31: KD referans betiklerinin sha256'ları: `tr7_onkayit_yapay.py` c77ffc0b…abb0, `tr7_onkayit_denetim2.py`
  dcf4acc5…8998.
- O-37: Wharton'ın negatif penceresi tek deneme alır; deneme o segmentte taranmış en erken alt pencereye eklenir.
- O-38: Modülasyon üreteci `default_rng(20261112 + 3)` K1'de ve Marmara'da ayrı ayrı kurulur. Marmara'da sıra: birim
  (ana şok T0) → segment S1…S7 → pencere zamanı → küme I′ başı; S4–S7 ve Kahramanmaraş dahil.
- O-49: Birimin τ_ölç'ü pencerelerinin τ_ölç'lerinin en büyüğüdür (kaba τ kuralının eşi). Ölçülemeyen birim n_ölç'te
  "≥ 2 kPa değil" sayılır.
- O-52: Sıra 5'in "uzun periyot başvuru istasyonu var" şartı, algılama veren pencerelerden en az birinde başvuru
  istasyonu bulunmasıdır.

**E1.2 O-44'ün yerine (kod incelemesi D1).** §7.4 "algılama vermemiş her negatif pencereye" der. Bu yüzden Kahramanmaraş
bilgi birimlerinin algılama vermemiş negatif pencereleri de MDA çekilişi alır. Sıra: ana şok T0'ına göre öteki
birimlerin arasında. Denemeleri `tr7_mda.csv`'ye yazılır. P(A), A50 ve A90 yalnız ana birimlerden hesaplanır. MDA
üreteci tektir: K1-negatif'te başlar, Marmara-negatif'e son durumundan taşınır.

**E1.3 Hüküm kalıpları (O-54, O-55).** Kalıplar §8'deki gibi doldurulur. Sayıdan sonraki ekler metindeki biçimde kalır
("3'unda", "7'ının"); dil düzeltmesi yapılmaz. Sayı biçimi: τ 2 ondalık, olasılık 3 ondalık, A 3 anlamlı basamak,
ondalık virgül. Aday kalıbının "[liste]"si koddaki sabit ifadelerden oluşur:
- "X_min yok"
- "X_mod ≥ X_min(n, f) (X_mod = a, X_min = b)"
- "Parkfield modülasyonu geçmedi (modülasyon ölçüsü pozitif kontrolde doğrulanmadı)"
- "K1 ayırt edici değil"
- "K1 yalnız belirsiz geçti"
- "uzun periyot başvuru istasyonu yok"

Kod incelemesi kalıp üreticisini metinden bağımsız yeniden yazdı. D11'in 13 cümlesinde ve 3000 rastgele senaryoda
çıktı birebir aynıydı.

**E1.4 Kodlayıcının bulduğu ve düzelttiği KD hatası.** Kodlayıcı, KD'nin yapay sinyal üreticisinde genliğin yerine A = 1
kullanıldığını kendisi buldu ve gerçek veri görülmeden düzeltti. Bu bir koşu öncesi düzeltmedir. Sinyal birim genlikle
üretilir, genlik yalnız zarf birleştirmede uygulanır (`kd_istasyonlar(…, 1.0)` ve `kd_pencere(st, A)`). Tam KD bu
düzeltilmiş kodla koşulur.

**E1.5 D6 ×100 ve bandı.**

*Durum.* Kodlayıcının 12 pencerelik ara denemesinde D6 ×100 değeri 0,917 çıktı (bant ≥ 0,95). Algılanan 5 kümeden
birinde, 3 istasyonun 2'sinde tepe başlangıçtan bir saniye sonra düştü. O tepenin önceki saniyesinde süzgeç öncülü
c_p/8'i aştı.

*Neden.* Metnin adıyla istediği süzgeç (obspy `bandpass, corners=4, zerophase=True`, §6.2.3) sıfır fazlıdır, yani
nedensel değildir. Ani bir başlangıçtan önce enerji sızdırır (öncül). Başlangıçtan önceki saniyede tepe oranının
medyanı bu süzgeçle 0,12'dir. §7.1'in referans betiği FFT |H|² yaklaşımıyla 0,09 verir. D6'nın ≥ 0,95 bandı referans
betiğin süzgeciyle konmuştu. Fark kodda değil, referansla metnin süzgeci arasındadır.

*Karar (kök oturum).*
1. Tam KD bir kez koşulur.
2. D6 ×100 bantta kalırsa konu kapanır.
3. Kalmazsa §7.1'in "koşu öncesi ek" yolu uygulanır. Süzgeç değişmez: nedensel ya da tek geçişli bir süzgece
   geçilmez, metnin adıyla istediği sıfır fazlı süzgeç korunur. Değişen yalnız D6 bandıdır; bant bu öncül için
   gerekçeli olarak yeniden tanımlanır. Yeni bant aşağıdaki ölçüme dayanır ve bağımsız incelemeden geçer.

*Ölçüm (kod incelemesi; KD tohumlarından bağımsız tohumlar 777100 ve 777101, 50'şer pencere).* Sonuçlar
`TR-7_KOD-INCELEME.md`'de ve aşağıda (E1.5a).

**E1.6 Koşu planı.** Aşamalar birden çok oturuma yayılabilir. Her aşama şu sırayla yürür:
1. `baslat <aşama>`
2. Durum dosyası commit + push edilir.
3. `kos <aşama>`
4. Çıktılar ve durum dosyası commit + push edilir.

Hiçbir aşama iki kez koşulmaz. Tek istisna §7.2'nin uygulama hatası yoludur: yalnız K1-algılama'da ve bir kez. Duran
aşama `durdu --neden` ile kayda geçer, sonra `baslat <aşama> --surdur` → commit + push → `kos <aşama>` ile kaldığı
pencereden sürer.

Aşama sırası:

| # | Aşama | Not |
|---|---|---|
| 0 | KD | Aşama değildir. Tam ölçek, bu kodla; `tr7_kd.json` commit edilir |
| 1 | manifest | |
| 2 | K1-indirme | |
| 3 | K1-negatif | |
| 4 | K1-algılama | |
| 5 | Marmara-indirme | Yalnız K1 (b) ya da (b′) ise |
| 6 | Marmara-negatif | Yalnız K1 (b) ya da (b′) ise. Öncesinde yerel diskte ≥ 12 GB boş alan; `TR7_HAM_DIZIN` depo dışı bir yerel dizine |
| 7 | Marmara-algılama | Yalnız K1 (b) ya da (b′) ise |
| 8 | hüküm | |

Kod KD'nin bu kodla (sha256 eşleşmesiyle) ve tam ölçekte koşulduğunu denetler. Kod KD'den sonra değişirse KD yeniden
koşulur.

**E1.7 Süre (ölçülen; kod incelemesi).** Süzgeç uygulaması obspy ile bit düzeyinde aynı ama 2–8 Hz'te 5–20 kat hızlı
(kod incelemesi D4). KD işleri 1,7–2,3 kat hızlandı. Kestirimler E1.5a'nın altında.

**E1.5a D6 ×100 ölçümü ve önerilen bant (kod incelemesi; yalnız yapay veri).** Koşu kodunun kendi D6 işi
(`kd_is('D6', (0, 100.0, 0.0), tohum, 50)`) iki bağımsız tohumla koşuldu.

| Tohum | Pencere | Algılama | Algılananda darbeyle atılma | D6 ×100 değeri | Bilinen yanlış kod (yumuşatılmış C) | Katalogda maskeyle atılma |
|---|---|---|---|---|---|---|
| 777100 | 50 | 0,50 | 0,96 | 0,98 | 0,50 | 1,00 |
| 777101 | 50 | 0,50 | 1,00 | 1,00 | 0,50 | 1,00 |

D6 ×100 değeri "algılanmama ya da darbeyle atılma" oranıdır. Toplam: 100 pencerede 99/100 = 0,99. Kodlayıcının 12
penceresiyle birlikte 110/112 = 0,982.

Değerlendirme:
- Gerçek oran p ≈ 0,98 ise, 100 pencerelik bir tohumun < 0,95 çıkma olasılığı ≈ %2'dir. İki tohumdan birinin bandın
  dışına düşme olasılığı ≈ %4'tür.
- Kodlayıcının 0,917'si 12 pencerelik bir örnektir. 100 pencereli ölçümle uyumludur (11/12).

Öneri:
- Tam KD'de D6 ×100 ≥ 0,95 olursa konu kapanır (E1.5 karar 2).
- Olmazsa "koşu öncesi ek" ile bant **≥ 0,85** olarak yeniden tanımlanır, iki tohumda da. Gerekçe:
  - Doğru kod p ≈ 0,98 iken bu bandın altına düşme olasılığı yok denecek kadar azdır. Kötümser p = 0,92 ile bile ≈ %0,2'dir.
  - Bilinen yanlış kod (yumuşatılmış C) 0,45–0,52 verir ve 0,33'ten fazla farkla bandın dışında kalır. Bant ayırt
    ediciliğini korur.
  - Bu değer D6b'nin bandıyla (≥ 0,90) aynı mantıktadır. Sıfır fazlı süzgecin öncülü D6b'de zaten bu payla
    karşılanmıştı.
- Katalogda maskeyle atılma şartı (1,00) değişmez.

**E1.7a Süre kestirimleri (ölçülen, ölçeklenmiş; yeni kod; makine paylaşımlıyken 2 süreç).**
- **Tam KD: ≈ 15 saat CPU.** 4 boş çekirdekte ≈ 4–5 saat, 2 süreçte ≈ 7–8 saat. Ölçüm: D2 ≈ 11 sn/pencere, D3 ≈ 31,
  D6 ≈ 6,3, D6b ≈ 6,8, D7 ailesi ≈ 8,8, D10 ≈ 8,6, D13 ≈ 6,7, D4/D5 ≈ 1,7; pencere sayılarıyla çarpıldı. Eski kodla
  aynı işler 1,7–2,3 kat uzundu.
- **MDA: ≈ 9 saat tek süreç.** Ölçüm: 12 istasyonlu tek deneme 34 sn + ham verinin yeniden okunması ≈ 11 sn. Gerçek
  W ×1,3 ile ≈ 55 sn/deneme. Sayı: Marmara ≈ 590 deneme (Kahramanmaraş dahil), Parkfield ≤ 30. Eski kodla ≈ 20 saatti.
  Koşutlama yazılmadı.
- **İndirme:** ölçülmedi, ölçülemez (gerçek servis yok). Hacim kestirimi kodlayıcınındır: ham ≈ 8–10 GB. Hız
  servise bağlıdır. Nezaket kuralı: servis başına 2 akış, istekler arası ≥ 0,5 sn.
