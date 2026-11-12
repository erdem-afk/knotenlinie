# TR-7 ön kaydı: Marmara ve batı KAF'ta uzak depremlerin yüzey dalgalarıyla tetiklenmiş tremor taraması

Tarih: 12 Kasım 2026. Durum: **TASLAK sürüm 1, incelemeye hazır.** Dondurulmadı; inceleme bulguları işlendikten sonra
"DONDURULDU" başlığıyla commit edilir, ondan sonra metin değişmez, ekler ayrı başlıkla yazılır.
Türediği yer: `kayit/onkayit/TR-7_SAYIM.md` (tasarım §2, sayım §3–§5, Ek 1 veri varlığı yoklaması; K0 GEÇTİ).
Kod: `kayit/turetme/tr7/` içinde `tr7_sayim.py`, `tr7_varlik.py` (sayım) ve bu ön kayıt için `tr7_onkayit_sayilar.py`,
`tr7_onkayit_yapay.py`, `tr7_onkayit_modulasyon.py`. Bu belgedeki her sayı bu betiklerin çıktısından
(`tr7_onkayit_sayilar.json`, `tr7_onkayit_yapay.json`, `tr7_dondurulan_liste.csv`, `tr7_parkfield_liste.csv`) alındı.
Maliyet 0 €. Bu belge yazılırken hiçbir dalga formu indirilmedi ya da açılmadı; yalnız Parkfield için NCEDC ve
EarthScope istasyon üstverisi (kanal düzeyi, metin) çekildi.

## 0. Bağlayıcı metinlerin sırası

Çelişkide sıra: (1) dondurulan liste `tr7_dondurulan_liste.csv` ve `tr7_parkfield_liste.csv` (sha256 §3); (2) bu
belge; (3) `TR-7_SAYIM.md` §2 ve Ek 1. Bu belge SAYIM §2.5–§2.10'un yerine geçer; aradaki farklar §15'te tek tek
yazılı ve gerekçelidir. Metin ile kod çelişirse liste ve bu belgedeki sayısal tanım geçerlidir; koşu kodu listeyi
yeniden kurmaz, okur ve sha256'sını denetler.

## 1. Soru ve neyi ölçmediği

Soru: 2005–2025 arasındaki büyük uzak depremlerin yüzey dalgaları geçerken KAF'ın Marmara kesimlerinde (S1 Ganos–Saros,
S2 Orta Marmara–Adalar, S3 Çınarcık–İzmit) 2–8 Hz'te, birden çok istasyonda tutarlı, yerel depremle açıklanamayan ve
yüzey dalgasının fazına kilitli bir tremor oluşuyor mu? Oluşmuyorsa hangi kaba dinamik gerilmenin üstünde, hangi
genliğin üstünde "görülmedi" denebilir?

Ölçmedikleri: ortam (tetiklenmemiş) tremor; sığ sünme (TR-10'un konusu); tremor ile deprem olasılığı arasındaki bağ;
2026 sonrası. İstanbul için mutlak olasılık bu belgede ve koşu çıktısında hiçbir yerde yazılmaz (§13).

## 2. Önceki bulgular, rakip açıklamalar, önsel

Özetten doğrulanan sayılar (OpenAlex, `kayit/oa.py ozet`; tam metin okunmadı):

| Kaynak | Bulgu | Doğrulama |
|---|---|---|
| Peng vd. 2009, 10.1029/2008jb006049 | Parkfield–Cholame, 2001+ 31 Mw≥7,5 olayın 10'u tetikledi; eşik ~2–3 kPa; tremor Love parçacık hızıyla eş fazlı | özetten doğrulandı. Eşiğin PGV'den hangi bileşenle hesaplandığı ve eşik üstü olaylarda oran: doğrulanamadı |
| Chao vd. 2011, 10.1111/j.1365-246x.2011.05261.x | Tayvan, 45 olayın 9'u; eşik ~0,1 cm/s ≈ 7–8 kPa, "kısmen gürültü düzeyine bağlı"; 10–30 sn dalgalar da tetikleyebiliyor | özetten doğrulandı (bu ön kayıt için yeniden okundu) |
| Chao vd. 2012, 10.1785/0120110151 | Calaveras ve San Jacinto'da 42 olaydan yalnız Denali 2002; Parkfield'da 12; fark yalnız gürültüden değil | özetten doğrulandı; görsel inceleme yöntemi |
| Hill vd. 2013, 10.1785/0120120114 | Tohoku 2011 Parkfield'da (~8200 km) tremor tetikledi; PKD'de kayıtlı; S'de başlıyor, Love'da belirgin, 20–30 sn Rayleigh ile modüle; derinlik 20–30 km; tepe dinamik Coulomb gerilmesi 0,7–10 kPa | özetten doğrulandı |
| Pfohl vd. 2015, 10.1785/0120140312 | Merkezî KAF, ~400 km kesimde 2 yıllık geçici geniş bant ağ; yüzey dalgasıyla tetiklenmiş tremor yok; ortam tremoru benzeri sinyaller istasyonlar arasında tutarsız | özetten doğrulandı. İstasyon sayısı, gürültü düzeyi, incelenen olay listesi ve sayısal eşik: doğrulanamadı |

Rakip açıklamalar ve sınav öncesi güven (yazarın beyanı): (R1) Marmara'nın kilitli derinliğinin altında Parkfield
türü düşük etkin gerilmeli, tetiklenebilir bir kaynak var ve bugünkü yüzey ağının gürültü tabanının üstünde (0,10);
(R2) kaynak yok ya da var ama gürültü tabanının altında (0,80); (R3) kaynak yalnız Tayvan türü yüksek eşikli,
tetikleyici gerilmeleri yetmiyor (0,10). Bu ölçüm R2 ile R3'ü ayıramaz.

## 3. Veri, dondurulan liste, manifest

**3.1 Dondurulan Marmara listesi.** `kayit/turetme/tr7/tr7_dondurulan_liste.csv`, sha256
`c8877cc26996010bc3c7036fd8b761791355cfad5a621dd076ed0429b40bde28`. Üretimi:
`python3 -I -B tr7_onkayit_sayilar.py <comcat_m75.csv> --parkfield <ncedc.txt> <earthscope.txt> --yaz`.
Girdi sha256'ları (ayrıca `tr7_onkayit_sayilar.json` içinde):
- `tr7_varlik.csv` a795a7f98198e6c20b1b24bca282dabb35addc9c50023694379110d8c90d48e8
- `tr7_varlik_ozet.json` 621791d083c071f0c53617a26dd65ae513a9f3a6f20d72140006af17510d174d
- `tr7_istasyon.csv` a7bb0892d3fb19d1ea0b882857bf1be6340ea3600f61586edcf0da56e4050db7
- `tr7_tetikleyici.csv` dec0cdd0b0b441ae792a98564d55164edd2bb858a0b7eebf235e6355f95ceb8c
- ComCat önbelleği `comcat_m75.csv` (depo dışı, `tr7_sayim.py`'nin çektiği yanıt; betik uyuşmazlıkta durur)
  ae9117d0fe64aae4be19a45a0151e830bd2b35de40056e3b322a3c4a06833e61

Kural: Ek 1 yoklamasında "var" çıkan (200, >0 bayt) istasyonlardan, bir (tetikleyici × segment) çiftinde ≥3 istasyon
"var" ise çift listeye girer. İçerik: **71 çift, 17 olay, 475 istasyon-tetikleyici, 884 satır** (SAYIM Ek 1 ile aynı).
Her satır: birim, tetikleyici, T0, M, dış merkez, segment, kaba τ (segment ortası, ×1), Kahramanmaraş bayrağı, ağ,
istasyon, koordinat, yoklama kanalı, dış merkez uzaklığı, başvuru penceresi R ve yüzey dalgası penceresi W. Listeye
istasyon eklenmez; tam taramada yalnız düşebilir (§4.2).

**3.2 Dondurulan Parkfield listesi.** `tr7_parkfield_liste.csv`, sha256
`cba4cea81a4b6b231133a99d0f2d19cce956a950885d7789390504c2aa471a77`. Kaynak: NCEDC ve EarthScope fdsnws/station
(kanal düzeyi, 35,3–36,6° K, 121,3–119,6° B, 2011-03-11T05:00–08:00); yanıt sha256'ları NCEDC
ab9b0d28014f1ef54d569a9aba45e3a47543a73391d559caa4508fc20eaa2e8e, EarthScope
86a5d5bc1729bbbb73b163775ae6566d13a956eb1acc364b4d203ae2bc32566d (yanıtlar depo dışında). Marmara'yla aynı seçim kuralları (Z bileşeni, bant H/B/E/S, alet H/P, ≥20 Hz, ZQ/SY
dışarıda, ize ≤50 km). Ek kural: PB ağı ve derinliği ≥50 m kanallar (kuyu jeofonları) dışarıda, çünkü Marmara
listesinde kuyu sensörü yok. İz (kaba, ±5 km): (120,80° B, 36,20° K) – (120,50; 35,97) – (120,35; 35,83) –
(120,20; 35,65), Hill 2013'ün tremor kesimini (Parkfield'ın 30 km KB'sı ile 40 km GD'su) örter. Sonuç: **56 yüzey
istasyonu** (NC 47, CI 6, BK 2, NP 1); BK.PKD listede. Tohoku'nun iz ortasına uzaklığı 8171 km;
W = 2011-03-11T06:13:38–06:45:02 UTC (iz ortası). Kaba τ (aynı Prag bağıntısıyla) 27,1 kPa; Hill 2013'ün hesapladığı
tepe Coulomb gerilmesi 0,7–10 kPa. Bu fark kaba τ'nun M9'da 3–40 kat fazla olabileceğini gösterir (§12).

**3.3 Koşu manifesti (dalga formundan önce commit edilir).** Koşu kodu, hiçbir dalga formu istemeden önce şunları üretir
ve commit eder: (a) negatif kontrol pencereleri `tr7_negatif_pencere.csv` (§7.3); (b) yerel katalog ayıklaması için
EMSC (seismicportal fdsnws/event) ve ComCat sorgu yanıtlarının sha256'ları (§6.5); (c) her kanalın StationXML yanıt
özeti (duyarlılık, 0,02 Hz ve 1 Hz'teki yanıt oranı, PGV uygunluğu §6.6) ve sha256; (d) indirme planı (istasyon,
kanal, başlangıç–bitiş, servis). Dalga formu indirildikçe manifest satırı: istek, HTTP kodu, bayt, miniSEED sha256,
örtü kesri. Ham miniSEED depoya girmez, işlendikten sonra silinir (§6.1).

**3.4 Veri sınırı.** Bütün tetikleyiciler ≤ 2025-12-31; listede en geç pencere Kamçatka 2025-07-29. Hiçbir pencere
2026-01-01'i geçemez (negatif kontroller dahil; geçen aday atlanır). Marmara GNSS verisine dokunulmaz.

## 4. Tetikleyici birimleri ve K0

**4.1 Birimler.** Bağımsızlık birimi "birim"dir:
- Wharton Basin 2012 ana şoku (official20120411083836720_20) ile 2 saat sonraki artçısı (usp000jhjb) tek birimdir
  (`WHARTON2012`). Birimde iki pencere vardır; birim, pencerelerinden en az biri bir segmentte ≥3 istasyonla
  taranabiliyorsa o segmentte sayılır, pencerelerinden birinde algılama varsa algılama sayılır; kaba τ'su iki
  olayınkinin büyüğüdür (ana şok).
- Kahramanmaraş 2023'ün iki olayı (us6000jllz, us6000jlqa; bölgesel, 771–800 km) ana sayıma girmez. Aynı kodla
  taranır, ayrı **bilgi satırı** olarak yazılır (süzgeç sızıntısı ve artçı riski). Hiçbir hükmü değiştirmez.
- Listede 16 birim var; 14'ü ana sayıma girer.

**4.2 K0, yeniden sayım.** Tam taramada bir istasyon, bir pencere için şu durumlarda o pencereden düşer: W'nin ya da
R'nin örtüsü <%90 (örtü: Z kanalında, kesintisiz örnek bulunan saniye / pencere saniyesi); StationXML'de yanıt yok;
kırpılma (§6.2). Bir çift ≥3 istasyon şartını kaybederse düşer; yerine istasyon ya da çift alınmaz. K0 bu gerçek
örtüyle yeniden sayılır: segment başına, ≥3 istasyonla taranabilen ana birim sayısı n.
- **n ≥ 8: tam bant. n = 5–7: zayıf bant. n < 5: "veri yok"**; bulgular yine bilgi satırı olarak yazılır, eleme yok.
- Bant, tetikleyici pencerelerinde hiçbir algılama hesaplanmadan önce belirlenir ve dosyaya yazılır.

**4.3 Önsayım (yoklamayla; ×1 kaba τ ≥ 2 kPa, birim kuralıyla).**

| Segment | n (×1) | bant | kaba τ₍₈₎ (kPa) | kaba τ₍ₙ₎ (kPa) | ×1/3: n / bant | ×3 (alt sınır): n |
|---|---|---|---|---|---|---|
| S1 Ganos–Saros | 9 | tam | 2,72 | 2,02 | 4 / veri yok | 9 |
| S2 Orta Marmara–Adalar | 8 | tam | 2,75 | 2,75 | 4 / veri yok | 9 |
| S3 Çınarcık–İzmit | 8 | tam | 2,75 | 2,75 | 3 / veri yok | 8 |
| S4 Sapanca–Düzce | 8 | tam | 2,76 | 2,76 | 3 / veri yok | 8 |
| S5 Bolu–Gerede | 6 | zayıf | — | 2,40 | 1 / veri yok | 6 |
| S6 Çerkeş–Tosya | 5 | zayıf | — | 2,44 | 1 / veri yok | 5 |
| S7 Güney kol | 10 | tam | 2,82 | 2,41 | 4 / veri yok | 11 |

S2 birimleri (kaba τ, kPa): Tohoku 2011 23,25; Kamçatka 2025 12,35; Wharton 2012 9,39; Maule 2010 6,00; İran 2013
4,68; Pakistan 2013 3,97; Nepal 2015 2,82; Chignik 2021 2,75. S3 aynı sekiz birim (Tohoku 23,53 … Chignik 2,75). S1
bunlara Illapel 2015'i (2,02) ekler. Sonuç: **S2 ve S3 tam bandın tam sınırında**; tam taramada tek bir birim düşerse
zayıf banda iner. ×1/3 ile S1–S3'ün hepsi "veri yok" bandına düşer (en çok 4 birim kalır: Tohoku, Kamçatka, Wharton,
Maule). Bu, hükmün kaba τ ölçeğine ne kadar duyarlı olduğunu önceden gösterir ve §8'deki zorunlu ×1/3 satırıyla
yazılır. ×3 sütunu alt sınırdır: yalnız ×1 adayları yoklandı.

## 5. Pencereler

Her istasyon için, kendi dış merkez uzaklığı Δ (km, küresel büyük daire, R = 6371 km) ile:
- yüzey dalgası penceresi **W = [T0 + Δ/5,0 km/s, T0 + Δ/2,8 km/s + 600 s]** (hız aralığı 2,8–5,0 km/s: Love
  başından Rayleigh kodasına; 600 sn kuyruk). Değerler listede saniyeye yuvarlanmış olarak yazılıdır;
- başvuru penceresi **R = [T0 − 3600 s, T0)** (P varışından tümüyle önce; SAYIM §2.5'in somut okuması);
- indirme dolgusu: [R başı − 600 s, W sonu + 600 s] (süzgeç geçişleri için; dolgu hiçbir istatistiğe girmez).
Listede R+W ortalaması 6314 sn (en az 4393, en çok 9050). W, S ve SS fazlarını dışarıda bırakır; Hill 2013'te
Tohoku'nun S'deki küçük tremor patlaması bu yüzden sayılmaz, Love ile gelen belirgin patlama W içindedir.
Parkfield için aynı formül, Δ istasyon başına. Negatif kontrol pencereleri bu pencerelerin tam gün kaydırılmışıdır (§7.3).

## 6. İşleme zinciri (bütün sayılar sabit)

**6.1 İndir–zarfla–sil.** obspy (pip, sürüm koşu başında `pip freeze` ile manifeste yazılır), scipy, numpy. Servis:
KO/TL/IJ/6G → KOERI; EIDA ağları → ORFEUS federatör; YH/YL → EarthScope; Parkfield → NCEDC (yoksa EarthScope).
Nezaket: servis başına en çok 2 eşzamanlı akış, aynı akışta istekler arası ≥0,5 sn, genel User-Agent; 429/503'te
Retry-After (yoksa 30 sn × deneme), en çok 2 yeniden deneme; 401/403 "kısıtlı" yazılır, atlatılmaz. Bir istasyonun
seçilen Z kanalıyla aynı konum ve bant kodlu yatay kanallar (N/E ya da 1/2) da istenir. İşlem bittiğinde ham veri
silinir; kalan yalnız aşağıdaki 1 Hz seriler (float32, npz) ve manifesttir. Seriler depo dışında
`/mnt/project-files/turetme/tr7-zarf/` altında tutulur (tahmini ≈0,9 GB: 475 × 11 pencere × 7 seri × ortalama 6314 sn
× 4 B); depoya yalnız dosya başına sha256 manifesti girer.

**6.2 İstasyon düzeyi (her bileşen ayrı).**
1. Ortalama ve doğrusal eğilim çıkarılır; 1/2 bileşenleri StationXML yönelimiyle N/E'ye döndürülür.
2. Kırpılma: W içinde, ham sayımın mutlak en büyük değerine eşit ≥5 ardışık örnek varsa ve bu değer ≥10⁶ sayımsa
   istasyon o pencereden düşer.
3. Yüksek frekans yolu: sayım / InstrumentSensitivity (m/s). 4 kutuplu Butterworth bant geçiren, ileri-geri (sıfır
   faz; obspy `bandpass, corners=4, zerophase=True`): **2–8 Hz** ve **0,5–1 Hz**. Hilbert zarfı (scipy, kesintisiz
   her parçada ayrı; parçaların ilk ve son 10 sn'si atılır). 1 sn'lik kutularda ortalama → 1 Hz zarf e(t).
4. Uzun periyot yolu: `remove_response(output="VEL", pre_filt=(0.005, 0.01, 0.15, 0.2), water_level=60)`, sonra
   **0,02–0,1 Hz** 4 kutuplu sıfır fazlı Butterworth; N/E → R/T (geri azimut istasyondan dış merkeze); tam saniyelerde
   örneklenir → v_Z, v_R, v_T (1 Hz, m/s).
5. Birleşik zarf C(t) = √(ortalama_bileşen e(t)²) (yatay yoksa yalnız Z). Saklanan seriler: e_Z, e_N, e_E (2–8 Hz),
   C₀,₅₋₁ (0,5–1 Hz birleşik), v_Z, v_R, v_T.
6. L(t) = log10(5 sn merkezli kayan ortalama C). m = medyan(L, R), σ = 1,4826 · MAD(L, R) (R'nin kenardaki 5'er sn'si
   hariç). σ = 0 olursa istasyon o pencereden düşer.
7. **Aşım:** W içinde L > m + 4σ olan saniyeler. Aradaki boşluğu ≤20 sn olan aşım saniyeleri tek parçada birleşir.
   Parça, açıklığı ≥30 sn ve aşım saniyesi ≥15 ise "istasyon aşımı"dır. Maskelenen (§6.5) ya da kayıtsız saniyeler
   aşım değildir ve köprülenmez.

**6.3 Tutarlılık (segment düzeyi).** Bir (pencere, segment) için, istasyon aşımlarının her biri ±20 sn genişletilince
birbiriyle örtüşen ≥3 farklı istasyonun aşımları bir **küme** kurar (bağlantılı bileşen). Küme aralığı
I = [en erken başlangıç − 60, en geç bitiş + 60] ∩ W. Küme içindeki her istasyon çifti için L serilerinin I üzerindeki
Pearson ilişkisinin gecikme −10…+10 sn (1 sn adım) üzerindeki en büyüğü alınır. **≥3 çiftte ≥0,5** ise küme
tutarlıdır. Pencere-segment için en az bir tutarlı küme ayıklamalardan (§6.5) sağ çıkarsa: **algılama**. Görsel ya da
elle seçim yoktur; hiçbir eşik veriyle ayarlanmaz.

**6.4 Modülasyon ölçüsü (yalnız olumlu iddia için).** Her segment için "uzun periyot başvuru istasyonu": PGV'ye uygun
(§6.6), W ve R örtüsü ≥%90 olan, segment orta noktasına (köşe noktalarının ortalaması) en yakın istasyon. Yoksa
modülasyon "ölçülemedi". φ_c(t) = v_c'nin W üzerindeki analitik sinyalinin fazı (c ∈ {Z, R, T}). L_k(t) = küme
istasyonlarının L'lerinin saniye başına medyanı. Ölçü:
M = en büyük_{c, s∈{+1,−1}, gecikme 0…10 sn} Pearson(L_k, max(0, s·cos φ_c(t − gecikme))) I üzerinde.
Boş dağılım: üç bileşen birlikte, W uzunluğunda dairesel kaydırma, kaydırma tamsayı ~ U[120, |W| − 120] sn, 1000
kaydırma, üreteç `numpy.random.default_rng(20261112 + 3)` (kümeler birim, segment, zaman sırasıyla). p = (1 + #{M₀ ≥
M}) / 1001. **Modülasyon var: p ≤ 0,01.** Faz yerine hızın kendisi kullanılmaz: yapay sınamada (aşağıda) hız
kullanan ilk sürüm sabit (modülasyonsuz) tremorda %20 yanlış p ≤ 0,01 verdi, çünkü yalnız paketle eş zamanlılığı
ölçüyordu.

Yapay sınama (`tr7_onkayit_modulasyon.py`, `tr7_onkayit_yapay.json`; dispersiyonlu 40→15 sn paket, 200 kaydırma):
p ≤ 0,01 oranı kilitli tremorda A = 0,5 / 0,7 / 1,0 için 1,00 / 1,00 / 1,00; sabit tremorda 0,00 (A 1 ve 3); rastgele
patlamalı tremorda 0,00 (A 1 ve 3); **20 sn sabit periyotlu ama dalgaya kilitli olmayan tremorda 0,35** (bilinen zayıflık
§12: ölçü kilitlenmeyi tesadüfi 20 sn periyodikliğinden ayıramaz).

**6.5 Ayıklama kuralları (tetikleyici ve negatif pencerelere aynen).**
1. **Katalog maskesi.** Marmara: EMSC (KOERI ve AFAD katkılı) ve ComCat; Parkfield: ComCat. Büyüklük türü serbest.
   Segment izine ≤150 km ve M ≥ 2,0 olan her olay için [t₀, t₀ + d/3 km/s + 60 s]; ≤1000 km ve M ≥ 4,0 olan her olay
   için [t₀, t₀ + d/3 km/s + 180 s] maskelenir (d: olayın ize uzaklığı). Maskeli saniyeler bütün istasyonlarda aşım
   dışıdır. Sorgular bir kez yapılır, sha256'larıyla manifeste girer (§3.3).
2. **Darbe kuralı (kataloglanmamış yerel deprem).** Kümedeki her istasyon aşımında C'nin (yumuşatılmamış) en büyük
   değeri c_p, zamanı t_p. [t_p − 2, t_p) içinde C ≤ c_p/8 olan bir saniye varsa **ve** (t_p, t_p + 20] içinde
   C ≤ c_p/2 olan bir saniye varsa o istasyon aşımı "darbe"dir. İstasyonların ≥ yarısı darbe ise küme atılır.
3. **Sızıntı kuralı.** Küme aralığında her istasyon için z_y(t) = (L − m)/σ (2–8 Hz) ve z_d(t) aynı tanımla 0,5–1 Hz
   birleşik zarftan. medyan_I z_d ≥ medyan_I z_y ise istasyon "sızıntı"dır. İstasyonların ≥ yarısı sızıntı ise küme atılır.
4. Ayıklanan küme sayısı ve nedeni her pencere için yazılır.

**6.6 Ölçülen dinamik gerilme (karar: ana değer değil, zorunlu ikinci değer).** PGV'ye uygun istasyon: bant kodu B ya
da H, alet kodu H, StationXML yanıt genliği |H(0,02 Hz)| / |H(1 Hz)| ≥ 0,5 (dalga formu görülmeden manifeste yazılır).
Her (pencere, segment) için PGV_ölç = uygun istasyonlarda en büyük_{t∈W} max(|v_Z|, |v_N|, |v_E|) değerlerinin
medyanı; τ_ölç = G · PGV_ölç / c (G 30 GPa, c 3,5 km/s; 1 cm/s ≈ 85,7 kPa). Uygun istasyon yoksa "ölçülemedi"
(yanıt düzeltmesi yapılamadığı açıkça yazılır). Bilgi: yalnız düşey PGV ile τ.

Gerekçe: (i) bant (§4.2) ve hüküm cümlesinin X'i veri görülmeden sabitlenmiş kaba τ'ya bağlı kalmalı, yoksa hangi
tetikleyicinin sayılacağı veriye bakılarak değişir; (ii) yüzeyde ölçülen PGV de 20–30 km derinlikteki fay üstü
gerilmenin kaba bir vekilidir (Hill 2013'te tek olay için 0,7–10 kPa); (iii) yine de literatür eşikleri (Chao 2011:
0,1 cm/s ≈ 7–8 kPa) ölçülmüş PGV'den hesaplanır, bu yüzden τ_ölç hükümde zorunlu ikinci değerdir. Kural (§8):
n_ölç = τ_ölç ≥ 2 kPa olan ana birim sayısı; bant_ölç = aynı bant kuralıyla. bant_ölç, kaba banttan düşükse hüküm
cümlesine "(ölçülen τ ile yalnız n_ölç birim ≥ 2 kPa; bant_ölç)" eki zorunludur. Bant ve hüküm türü değişmez.

## 7. Kapılar ve kontroller (sıra: KD → kod incelemesi → K1 → K0-tam → K2 ve MDA → tetikleyici pencereleri → hüküm)

**7.1 KD, kod denetimi (yalnız yapay veri).** Kod yalnız yapay veriyle geliştirilir. Koşu kodunun kendisi (aynı
fonksiyonlar, 100 Hz, Butterworth) yapay girdiyle şu denetimlerden geçmelidir; biri kalırsa kod gerçek veri görülmeden
düzeltilir ve "koşu öncesi düzeltme" başlığıyla kayda geçer. Referans değerler bu ön kayıt için bağımsız yazılmış
`tr7_onkayit_yapay.py` ile önceden hesaplandı (FFT ile |H|² süzgeç, 20 Hz; durağan Gauss gürültüsü, 20 sn yarım sinüs
modüleli 300 sn tremor; A = tremorun etkin örneklerindeki bileşen başına 2–8 Hz RMS / gürültünün bileşen başına RMS'i).

| # | Denetim (yapay) | Şart | Önceden hesaplanan |
|---|---|---|---|
| D1 | Durağan Gauss, 3 istasyon, 200 pencere, tremor yok | yanlış algılama ≤ 0,01 | 0/200 |
| D2 | Aynı, A basamağı 10^(j/40); 3 istasyon | A50 ∈ [0,56, 0,67], A90 ∈ [0,59, 0,72] | A50 ≈ 0,61, A90 ≈ 0,65 (100 Hz'te de 0,61) |
| D3 | Aynı, 8 istasyon, 100 pencere | A50 ∈ [0,52, 0,62] | ≈ 0,57 |
| D4 | Modülasyon (dispersiyonlu paket; kilitli tremor A = 0,7, 100 pencere, 1000 kaydırma) | p ≤ 0,01 oranı ≥ 0,90 | 1,00 (200 kaydırmayla) |
| D5 | Modülasyon, sabit ve rastgele patlamalı tremor (A = 1 ve 3) | p ≤ 0,01 oranı ≤ 0,05 | 0,00 |
| D6 | Yapay yerel deprem (ani başlangıç, C ×20 sıçrama, 5 sn e-katlı sönüm) A ≫ eşik, katalogsuz, 100 pencere | darbe kuralıyla atılma ≥ 0,95; aynı olay katalogdaysa maske ile 1,00 | — (yeni) |
| D7 | Yapay tremor A = 10 (yarım sinüs), 100 pencere | darbe ya da sızıntıyla atılma ≤ 0,05 | — (yeni) |
| D8 | Birim: sıfır gürültüye 100 nm/s RMS 2–8 Hz bileşen; bilinen duyarlılık | ölçülen RMS ±%5; §6.6 PGV'si bilinen PAZ yanıtlı 20 sn sinüste ±%5 | — |
| D9 | Pencere: bilinen Δ ve T0 | W ve R listedeki değere ±1 sn; 2026 sınırı ihlali kodu durdurur | — |
| D10 | Genlik kestirici (§7.5) sabit tremor A/N = 3 | kestirilen / gerçek ∈ [0,85, 1,15] | — |
| D11 | Bant ve hüküm cümlesi üretici: elle kurulmuş 6 senaryo (§8'in her dalı) | metin birebir | — |

D2'nin bandı (≈ ±%9) eşik çarpanı 4σ yerine 3σ ya da 5σ kullanan bir kodu ayırır (yapayda A50 0,52 / 0,70) ve yanlış
birim ya da yumuşatmasız zarf gibi kaba hataları yakalar. Doğru kodun bandın dışına düşme payı küçüktür: 200 pencerede
geçiş dik (A 0,596'da 0,31, 0,631'de 0,81) ve sonuç örneklemeden bağımsız (100 Hz, 60 pencere: 0,596'da 0,28, 0,631'de
0,82). Yine de D2'nin bandı tek gerçekleşmeye dayanır; kod incelemesi aynı denetimi bağımsız tohumla yinelemelidir. Not (önceden doğrulandı): SAYIM §2.7'deki "≥30 sn kesintisiz aşım"
kuralı 20 sn yarım sinüs modüleli tremoru A = 1,0'da bile 0/100 algıladı; §6.2 madde 7'deki boşluk köprüleme bu
yüzden konuldu (§15).

**7.2 K1, pozitif kontrol: Parkfield–Tohoku 2011.** Kod incelemesinden sonra, Marmara'nın hiçbir dalga formundan
önce. Aynı kod, aynı sabitler; istasyonlar `tr7_parkfield_liste.csv`; segment Parkfield izi (§3.2); katalog ComCat.
**Geçme şartı: Tohoku penceresinde ≥3 istasyonla taranabilirlik ve en az bir algılama (§6.3 + §6.5).** Kalırsa ya
da ≥3 istasyon örtüsü sağlanamazsa koşu durur, Marmara verisi indirilmez, TR-7 hükmü "ölçü sınanamadı" olur. Eşik,
pencere, istasyon kuralı değiştirilip yeniden denenmez; yalnız yeni bir ön kayıt açılabilir. Bilgi satırları
(K1'i değiştirmez): Parkfield modülasyon p'si; Parkfield'da 10 negatif pencerenin algılama oranı (Cholame ortam tremoru
yüzünden yüksek olabilir, bu yüzden şart değil); yalnız ize en yakın 10 istasyonla algılama; tremor genliği A_PK
(§7.5); Parkfield MDA'sı (§7.4 yöntemiyle). **Parkfield modülasyonu p > 0,01 çıkarsa Marmara'da "VAR" hükmü
verilemez, en çok "aday (modülasyon ölçüsü pozitif kontrolde doğrulanmadı)" yazılır.**

**7.3 K2, negatif kontrol.** Her birim (Kahramanmaraş bilgi birimleri dahil) için 10 pencere. Aday kaydırmalar
d ∈ {−30, …, −1, +1, …, +30} gün (tam gün: aynı UTC saati, R ve W birlikte kayar; Wharton'ın iki penceresi aynı d ile).
Üreteç `numpy.random.default_rng(20261112)`; birimler ana şok T0 sırasıyla; her birim için `rng.permutation` ile
adaylar sıralanır ve şu şartları sağlayan ilk 10 alınır: kaydırılmış [min R başı − 3 sa, max W sonu] aralığında ComCat
M ≥ 6,5 olay yok; kaydırılmış W sonu < 2026-01-01. Parkfield için ayrı üreteç `default_rng(20261112 + 1)`. Liste
dalga formundan önce commit edilir. Yerel M ≥ 3 olan pencereler atılmaz: yerel depremler tetikleyici pencerelerinde
de §6.5 ile ayıklanır, simetri korunur (§15). Negatif pencerede örtü kuralı aynıdır; ≥3 istasyonu kalmayan pencere
düşer, yerine pencere alınmaz.

Segment başına N = kullanılabilir negatif pencere sayısı (ana birimlerin), f = algılama sayısı, FAR = f/N.
**K2: FAR ≤ 0,05** (f ≤ ⌊0,05 N⌋; N = 80 için f ≤ 4). Kalırsa o segmentin hükmü "ölçü güvenilmez" olur; eşik
değişmez; tetikleyici bulguları bilgi satırı olarak yazılır. Negatif pencereler ve MDA tetikleyici pencerelerinden önce
işlenir ve dosyaya yazılır.

**7.4 Algılanabilir en küçük tremor genliği (MDA).** Koşu sırasında, yalnız negatif kontrol pencerelerine
(tetikleyici pencerelerinin dışında), algılama vermemiş her negatif pencereye ham veri bellekteyken yapay tremor
eklenir. Model: kaynak segment orta noktasının 25 km altında; istasyon i'de genlik A·25/r_i (r_i hiposantr uzaklığı),
varış gecikmesi r_i / 3,5 km/s; üç bileşende eşit RMS, her istasyon ve bileşende bağımsız Gauss gerçekleşmesi, 2–8 Hz
süzülmüş; zarf 300 sn, 20 sn periyotlu yarım sinüs, 10 sn kenar yumuşatma (yapay sınamayla aynı); başlangıç W'nin
göreli konumunda U[60, |W| − 360] sn. Üreteç `default_rng(20261112 + 2)`. A basamakları 10^(j/8) nm/s, j = 0…40
(1 nm/s – 100 µm/s). Süzgeç ve Hilbert doğrusal olduğundan zarf |a_veri + A·a_yapay| olarak her basamak için hesaplanır;
R'ye ekleme yapılmaz. P(A) = algılama veren pencere payı (segment başına). **A50 ve A90 = P ≥ 0,5 ve P ≥ 0,9 olan en
küçük basamak** (yukarı yuvarlanır; adım ×1,33). Hiçbir basamak ulaşmazsa "> 100 µm/s". A, kaynağın tam üstünde
(25 km) bileşen başına 2–8 Hz RMS'tir (nm/s). Kısa periyotlu ve jeofon kanallarında doğal frekansın altında
duyarlılık bölmesi genliği küçük gösterir (§12). MDA algılama içindir, modülasyon şartını içermez.

**7.5 Tremor genliği kestiricisi (bilgi).** Algılanan kümede istasyon i için a_i = √(max(0, ⟨C²⟩_I − ⟨C²⟩_R) · 2/π),
25 km'ye indirgenmiş a_i · r_i / 25; segment değeri medyan. Parkfield'daki A_PK bu tanımla. **Bilgi satırı: her
Marmara segmenti için A90(S_k) / A_PK** ("Parkfield'daki Tohoku tremoru bu gürültüde görülür müydü").

## 8. Hüküm kuralları (tam sayısal; sıra bağlayıcı)

Tanımlar, segment başına: n (K0-tam ana birim), bant (§4.2), N, f (§7.3), X_alg = algılama veren ana birim sayısı,
X_mod = algılama veren **ve** o algılama kümelerinden en az birinde modülasyon p ≤ 0,01 olan ana birim sayısı.
p_üst = f/N için tek yanlı %95 Clopper–Pearson üst sınırı. X_min(n, f) = P(Bin(n, p_üst) ≥ X) ≤ 0,05 olan en küçük X,
en az 2. Önceden hesaplanmış örnekler (`tr7_onkayit_sayilar.json`):

| n | N | f = 0 | f = 1 | f = 2 | f = 3 | f = 4 | f = 5 |
|---|---|---|---|---|---|---|---|
| 8 | 80 | 2 | 3 | 3 | 3 | 3 | K2 kalır |
| 9 | 90 | 2 | 3 | 3 | 3 | 4 | K2 kalır |
| 10 | 100 | 2 | 3 | 3 | 3 | 4 | 4 |
| 5 | 50 | 2 | 3 | 3 | K2 kalır | K2 kalır | K2 kalır |

(FAR = 0,05'te 8 birimde rastlantıyla ≥2 algılama olasılığı 0,057; bu yüzden düz "≥2" yetmez.)

Sıra:
1. K1 kaldı → bütün segmentler **"ölçü sınanamadı"**.
2. bant = veri yok (n < 5) → **"veri yok"** (bulgular bilgi satırı).
3. K2 kaldı → **"ölçü güvenilmez"** (bulgular bilgi satırı).
4. X_mod ≥ X_min(n, f) ve Parkfield modülasyonu geçti ve uzun periyot başvuru istasyonu var →
   **"tetiklenmiş tremor VAR"**.
5. X_alg ≥ 1 ve 4 sağlanmıyor → **"aday, doğrulanmadı"** (X_alg = 1 ise her durumda bu).
6. X_alg = 0 → **"görülmedi"**.

Dışlama oranı: n birimde algılama yoksa, tetikleyici başına ≥ p_min olasılıkla A90'ı aşan tremor üreten bir kaynak %95
düzeyinde dışlanır; p_min = (1 − 0,05^(1/n)) / 0,9. Değerler: n 5 → 0,50; 6 → 0,44; 7 → 0,39; 8 → 0,35; 9 → 0,32;
10 → 0,29.

**Hüküm kalıpları (yalnız bu biçimlerde; köşeli yerler koddan doldurulur):**
- VAR: "S_k: tetiklenmiş tremor VAR. n bağımsız tetikleyicinin X_mod'unda, yerel deprem maskesi ve darbe/sızıntı
  ayıklamasından sonra ≥3 istasyonda tutarlı ve yüzey dalgası fazına kilitli (p ≤ 0,01) 2–8 Hz tremor; negatif
  kontrolde FAR = f/N; kaba τ ≥ [en küçük algılayan birimin kaba τ'su] kPa (ölçülen τ ≥ [..] kPa)."
- Aday: "S_k: aday, doğrulanmadı. [X_alg] tetikleyicide algılama; VAR şartlarından sağlanmayan: [liste]."
- Görülmedi: "S_k: kaba τ ≥ X kPa üstündeki n bağımsız tetikleyicide tetiklenmiş tremor görülmedi; algılanabilir en
  küçük genlik A90 = [..] nm/s (25 km'de, 2–8 Hz RMS; A50 = [..]); tetikleyici başına ≥ p_min olasılıkla bu genliği
  aşan tremor üreten bir kaynak %95 düzeyinde dışlanır. [bant zayıfsa: 'zayıf bant'.] Ölçülen τ ile [n_ölç] birim
  ≥ 2 kPa." Burada X = kaba τ₍ₙ₎ (taranan ana birimlerin en küçük kaba τ'su).
- Veri yok / ölçü güvenilmez / ölçü sınanamadı: o sözcüklerle, ardından bilgi satırları.
- **Zorunlu ×1/3 satırı** (her segment, her hükümde): "Kaba τ ×1/3 alınırsa [n₁/₃] birim ≥ 2 kPa (bant: ..)." ×3
  satırı da yazılır (alt sınır notuyla).

Marmara özeti (S1–S3 birlikte): en az bir segment VAR ise "Marmara'da dinamik gerilmeye duyarlı derin kayma bölgesi
gözlendi"; üçü de "görülmedi" ise "bu duyarlılıkla (A90 ve kaba τ değerleriyle) gözlenmedi"; öteki durumlarda segment
satırları özetsiz yazılır. S4–S7 ikinci satırlardır, özete girmez. S5/S6'da 2005–2008 birimleri (Kashmir 2005,
Kuril 2006, Kuril 2007, Bengkulu 2007; YL verisi, Pfohl 2015'in incelediği veri) ayrı satırda "yöntem karşılaştırması,
bağımsız değil" diye yazılır; S5/S6'nın bağımsız satırı yalnız 2009 sonrası birimlerle (S5: Kamçatka, Chignik; S6:
Kamçatka) kurulur ve bant kuralına tabidir. Kahramanmaraş satırları ayrı ve yalnız bilgi.

## 9. Çıktı tabloları

`tr7_sonuc.json` ve `tr7_sonuc.md` (tek koşu, "x" kipinde):
1. Birim × segment: birim, olay(lar), T0, M, kaba τ, kaba τ ×1/3, τ_ölç (ve uygun istasyon sayısı), örtüden geçen
   istasyon sayısı, küme sayısı, ayıklanan küme (maske / darbe / sızıntı), algılama E/H, modülasyon p, en uzun küme
   süresi, a (§7.5), o birimin negatif pencerelerinde f/10.
2. Segment: n, bant, n_ölç ve bant_ölç, N, f, FAR, p_üst, X_alg, X_mod, X_min, A50, A90, A90/A_PK, kaba τ₍ₙ₎, ×1/3 ve ×3
   satırları, hüküm cümlesi.
3. K1 satırı ve Parkfield bilgi satırları; KD sonuçları; manifest özeti (istek, HTTP dağılımı, bayt, düşen istasyon
   ve nedeni); negatif pencerelerin hafta içi/sonu dağılımı (bilgi).

## 10. Koşu sırası, körlük, tek koşu

1. Bu ön kayıt incelenir, düzeltilir, dondurulur, commit + push edilir.
2. Kod yazılır; **yalnız yapay veriyle** geliştirilir ve KD (§7.1) geçer. Gerçek hiçbir dalga formu (Parkfield dahil)
   indirilmez. Kod incelemesi yapılır ("koşulabilir" hükmü gerekir).
3. Manifest (§3.3) üretilir ve commit edilir (üstveri ve katalog; dalga formu yok).
4. K1: Parkfield indirilir ve işlenir. Kalırsa dur (§7.2).
5. Marmara: indir–zarfla–sil; önce örtü ve K0-tam bandı yazılır, sonra negatif pencereler, K2 ve MDA yazılır, sonra
   tetikleyici pencereleri işlenir, en son hüküm.
6. Tek koşu. Çıktı ne olursa olsun yazılır. Koşu kodu başlangıçta depo dışında bir bekçi dosyası
   (`TR7_GERCEK_KOSU_BASLADI`) oluşturur; dosya varsa yeniden koşmaz. İndirme hatası: istasyon-pencere düzeyinde
   kayda geçer; servis hatası (5xx, zaman aşımı; 204/404 değil) payı %10'u aşarsa koşu, hiçbir algılama hesaplanmadan
   durur ve tek bir yeniden deneme turu yapılır. **Biçim hatası koşuyu durdurur**: miniSEED ya da StationXML
   ayrıştırılamazsa (istasyon-pencerelerin >%1'i) ya da liste/Parkfield listesi sha256'sı uyuşmazsa, hiçbir algılama
   hesaplanmadan durur; "veri yok" yazılmaz. Herhangi bir algılama değeri görüldükten sonraki her kod değişikliği
   "koşu sonrası değişiklik" başlığıyla yazılır; tanım, eşik, liste ya da birim kuralı değişmez.

Körlük beyanı: Ek 1 yoklamasında 935 adet 10 sn'lik istek yapıldı; yalnız HTTP kodu ve bayt sayıldı, içerik çözülmedi
ve diske yazılmadı. SAYIM §4'teki iki erişim denemesinin içeriği de açılmadı. Bugüne dek hiçbir Marmara ya da Parkfield
dalga formu işlenmedi. Yazar Kahramanmaraş'ın başka bölgelerde tremor tetiklediğini (Inbal 2024; Yao 2024) ve Hill
2013'ü literatürden biliyor; Marmara için yayımlanmış bir tremor gözlemi bulunamadı (SAYIM §8).

## 11. Önceden beyan edilen beklenti

En olası sonuç **"görülmedi"**dir ve bu önceden kabul edilir; ölçümün asıl ürünü A90 ve hangi kaba τ'nun üstünde kaç
bağımsız tetikleyici tarandığıdır. Yazarın sınav öncesi güveni (Marmara özeti): görülmedi (tam ya da zayıf bant) 0,55;
aday 0,10; VAR 0,03; ölçü sınanamadı (K1 kalır) 0,20; veri yok ya da ölçü güvenilmez 0,12. S2 ve S3 tam bandın tam
sınırında olduğundan (n = 8) zayıf banda inme olasılığı yüksektir. Yapay sınamaya göre durağan gürültüde A50 bileşen
başına gürültü RMS'inin ~0,6 katıdır; gerçek kentsel gürültü durağan olmadığı için σ ve dolayısıyla A90 daha büyük
çıkacaktır. Mutlak A90 değeri önceden kestirilmedi.

## 12. Bilinen zayıflıklar

- **Kültürel gürültü.** S2/S3 istasyonlarının çoğu KO yüzey istasyonudur; 2–8 Hz gürültü yüksek ve gündüz/gece,
  hafta içi/sonu değişkendir. Negatif kontrol aynı UTC saatindedir; hafta günü eşlenmez, 2016 öncesinde yaz saati
  geçişi ±30 gün içinde yerel saati 1 sa kaydırabilir.
- **Kuyu sensörü yok.** GONAF kuyu sismometreleri açık FDSN'de yok (yalnız gerinimölçer). Parkfield pozitif kontrolü
  bu yüzden kuyu istasyonlarını dışarıda bırakır; yine de Parkfield kırsal, Marmara kentseldir: K1'in geçmesi
  duyarlılığın eşit olduğu anlamına gelmez; duyarlılık A90 ve A90/A_PK ile ölçülür.
- **6G, TL, 1O, TU verisinin yokluğu.** 6G'nin 2015 sonrası, TL ve 1O/TU'nun hiçbir isteği gelmedi (Ek 1); kısıtlı mı
  yok mu ayrılamadı. S2/S3 pratikte yalnız KO ile taranır.
- **Tek 10 sn varlık örneği.** Listedeki her istasyon W'nin ortasındaki tek bir 10 sn'lik örnekle "var" sayıldı;
  %90 örtü doğrulanmadı. S2 ve S3'te tek birim düşmesi bandı değiştirir.
- **Kaba τ.** Prag bağıntısı ders kitabından, özetten doğrulanmadı; M>8 doygunluğu yok sayılıyor; ×1/3'te S1–S3 "veri
  yok" bandına düşer. Parkfield–Tohoku'da kaba τ 27 kPa iken Hill 2013'ün Coulomb gerilmesi 0,7–10 kPa: kaba τ
  büyük olaylarda büyük olasılıkla fazladır. ×1/3 satırı bu yüzden zorunludur.
- **Pencere S'yi dışlar** (W 5,0 km/s'de başlar); S ile tetiklenen tremor sayılmaz.
- **Modülasyon ölçüsü** kilitlenmeyi tesadüfi 20 sn periyodikliğinden ayıramaz (yapayda %35); sabit ya da rastgele
  patlamalı zarflarda yanlış pozitif vermez.
- **Kısa periyotlu kanallar.** 2–8 Hz genliği yalnız duyarlılık bölmesiyle; jeofonlarda doğal frekansın altında genlik
  küçük görünür, A90 bu kanallarda iyimser olabilir.
- **Kaynak modeli** (25 km derinlik, 1/r, Q yok) kabadır; A90 bir karşılaştırma ölçüsüdür, kaynak genliği değildir.
- Segment izleri elle sayısallaştırılmış (±5–10 km); orta nokta köşe ortalamasıdır.
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
istasyonlarına izin veren ya da algılayıcıyı değiştiren yeni bir tasarım, yalnız yeni bir ön kayıtla.

## 15. SAYIM'dan sapmalar (veri görülmeden, gerekçeli)

1. Aşım: "≥30 sn kesintisiz" yerine boşluk ≤20 sn köprüleme, açıklık ≥30 sn ve ≥15 aşım saniyesi. Yapay sınamada eski
   kural modüleli tremoru A = 1,0'da 0/100 algıladı; yeni kural A50 ≈ 0,61'de algılıyor, tremorsuz 200 pencerede 0.
2. Modülasyon: "ilişki ≥0,3 ya da aşım W içinde" yerine faz temelli ölçü ve dairesel kaydırma boş dağılımı; yalnız
   olumlu iddia için şart, algılama için değil. Eski "W içinde başlar ve biter" seçeneği hemen her aşımda sağlanırdı.
3. Yerel deprem: "±60 sn ve 150 km içinde herhangi bir olay varsa aşım atılır" yerine büyüklüğe bağlı zaman maskesi;
   Parkfield'ın yoğun mikrodepremliliğinde eski kural K1'i olanaksız kılabilirdi. Darbe kuralı 1 Hz çözünürlüğe
   uyarlandı (eski "yükselme <2 sn" 5 sn yumuşatılmış seride hiç tetiklenemezdi).
4. Sızıntı: niteliksel "hızlı yükselirse" yerine medyan z karşılaştırması.
5. Negatif kontrol: yerel M ≥ 3 içeren pencereler atılmaz (simetri); yalnız küresel M ≥ 6,5 dışlanır.
6. R penceresi [T0 − 3600, T0); R örtüsü de ≥%90 şartı.
7. Ana değer kaba τ; ölçülen τ zorunlu ikinci değer (SAYIM §2.1 "koşuda ölçülenle değiştirilir" diyordu).
8. "VAR" için ≥2 yerine X_min(n, f) (FAR'a bağlı binom şartı) ve modülasyon şartı.
9. Hüküm bandı Kahramanmaraş hariç ve Wharton tek birimle sayılır (kök oturum kararları 1–2).

## 16. Doğrulanamayanlar

Peng 2009 eşiğinin hangi PGV tanımından geldiği ve eşik üstü olaylarda tetikleme oranı; Pfohl 2015'in istasyon sayısı,
olay listesi, gürültü düzeyi ve eşiği; Parkfield'ı Tohoku'da tetikleyen tremorun 2–8 Hz genliği (A_PK koşuda ölçülür);
Prag Ms bağıntısının katsayıları (ders kitabı); Tohoku'da Parkfield yüzey istasyonlarının veri varlığı (yoklanmadı:
K1'in en büyük riski); KOERI'nin 2'den fazla eşzamanlı akışa izni (kullanılmayacak). 2012 tarihli DOI'siz "Searching
for Tectonic Tremor on the North Anatolian Fault" kaydı okunamadı (SAYIM §8).
