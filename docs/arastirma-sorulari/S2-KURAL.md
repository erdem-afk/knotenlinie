# S2 ön kaydı: Türkiye için yayımlanmış segment olasılıklarının 2016–2025 karnesi (10 Kasım 2026)

Erdem 10 Kasım 17:28'de 7 sorunun hepsini seçti ("Hepsi"). Bu kural, 2016–2025 hedef kataloğu indirilmeden ve hiçbir skor hesaplanmadan önce yazılıp donduruldu (sha + OTS). Kod (`tools/arastirma/s2_karne.py`) ve literatür tablosu (`S2-literatur_tablosu.json`) kuralla birlikte donar; sha'ları aşağıda.

**Kural kör değil.** Yazar 2016–2025 Türkiye M6+ depremlerini nitel olarak biliyor (Elazığ 2020, Sisam 2020, Kahramanmaraş 2023, Marmara 2025 vb.) ve Marmara'da bu dönemde M7 olmadığını biliyor. Türkiye 2016–2025 mühür açıldığı için geliştirme verisi (7 Kasım). Bu yüzden satırlar "sözde-ileriye dönük, kör değil" düzeyindedir. Türkiye dışı 2026 verisine dokunulmaz (bütün sorgular 2026-01-01T00:00 UTC'de biter).

## Soru

1997–2015 arasında yayımlanmış Türkiye segment tahminleri 2016–2025 depremlerine olay öncesi ne kadar olasılık vermişti? Yenilenme/Coulomb ailesi düzleştirilmiş sismisiteyi ve Poisson tahminini geçti mi?

- **H1:** segment/fizik tahminleri (yenilenme + Coulomb), olay olan segmentlere düzleştirilmiş sismisiteden fazla, olay olmayanlara az olasılık verdi.
- **H0:** vermedi.

## Derleme kuralı (literatür tablosu)

- 1997-01-01 ile 2015-12-31 arasında yayımlanmış, Türkiye'deki bir fay segmenti ya da adı konmuş bir bölge için **sayısal** olasılık (ya da açık "yüklü segment" bayrağı) veren çalışmalar.
- Sayı yalnız **açık erişimle okunabilen** tam metinden ya da yayıncı özetinden alınır ve kaynağıyla yazılır. Bellekten sayı girmez. Okunamayan çalışma "erişilemeyen" listesine yazılır; karneye girmez. Sonradan erişilirse ancak ek kural (EK) ile ve yalnız bilgi satırı olarak eklenir; hüküm satırını değiştirmez.
- 10 Kasım taraması (Crossref, Semantic Scholar, Unpaywall, ORBi; OpenAlex kotası doluydu) sonucu `S2-literatur_tablosu.json`:
  - **Sayısal:** Parsons ve ark. 2000 (Science, Tablo 1: Yalova, Adalar, Marmara ve birleşik; etkileşimli ve arka plan yenilenme; 30 ve 10 yıl; metinde Poisson %15–25), Parsons 2004 (JGR özeti: 2004–2034 bölge Poisson %38, zamana bağlı %44, + gerilme aktarımı %53; İstanbul Poisson %21, zamana bağlı + aktarım %41).
  - **Bayrak:** Hubert-Ferrari ve ark. 2000 (Nature): 160 km'lik Marmara çukuru "yenilmeye yaklaşıyor".
  - **Dışlanan:** Erdik 2004 (kendi segment tablosu açık metinde yok, Parsons'a atıf), Stein 1997 (okunamadı; İzmit 1999'da kırıldı).
  - **Erişilemeyen:** Nalbant 2002 (Doğu Anadolu Coulomb), Pondard 2007, Paradisopoulou 2010 (Batı Türkiye), Bayrak 2015 (Doğu Anadolu), Nalbant 1998, 10.1007/s11069-008-9317-4.
- Sınır (önceden yazılı): erişilebilen sayısal tahminlerin hepsi Marmara'yı kapsıyor. 2016–2025'in büyük depremlerinin çoğu Doğu Anadolu ve Ege'de; oralar için sayısal literatür satırı bu derlemede yok. Karnenin kapsamı bunu açıkça söyler.

## Pencereye çevirme (W = 2016.0–2026.0)

- 30 ve 10 yıllık değer birlikte verilmişse (P2000, başlangıç Mayıs 2000): 10. yıldan sonraki koşullu 20 yıllık olasılık p20 = 1 − (1 − P30)/(1 − P10); sabit oranla W'ye: pW = 1 − (1 − p20)^(10/20).
- Yalnız 30 yıllık değer varsa (P2004, 2004–2034; P2000 Poisson): pW = 1 − (1 − P30)^(10/30).
- Merkez değer kullanılır; ± aralıklar bilgi.
- Yayım ile 2016 arasında kırılan segment dışlanır (Marmara'da yok).

Sonuç (yalnız literatür aritmetiği, olay verisi yok): P2000 birleşik etkileşimli pW 0,2525, arka plan 0,2016, Poisson 0,0717; Yalova 0,1174, Adalar 0,1203, Marmara 0,0430; P2004 bölge etkileşimli 0,2225, zamana bağlı 0,1757, Poisson 0,1473; İstanbul etkileşimli 0,1613, Poisson 0,0756.

## Satırlar

### L1 (hüküm): literatür sayısal ailesi, Marmara M≥7

- **Hedef:** USGS ComCat, W içinde, Mw ≥ 7,0, derinlik ≤ 40 km, merkez üssü MARMARA_KUTU (26,5–30,0° D, 40,2–41,2° K) içinde. Olay var/yok, Bernoulli.
- **Skor:** her tahmin satırı için lnL = ln(pW) (olay varsa) ya da ln(1 − pW) (yoksa). Kıyaslar: (a) yenilenme+Coulomb − aynı makalenin yenilenme satırı (Coulomb katkısı), (b) yenilenme − aynı makalenin Poisson satırı (zaman bağımlılığı katkısı), (c) her biri − R1 (düzleştirilmiş sismisite, aynı kutu, M≥7, b = 1 ile M≥6'dan).
- **Ateşleme kapısı (önceden, veriden bağımsız):** tek bir bölge, tek bir ikili sonuç. En yüksek pW 0,2525; olay olmazsa bile bu tahminin kendi altında olaysızlık olasılığı 0,75 > 0,05. Hiçbir satır reddedilemez, satır farkları |Δ| ≤ ≈0,3 nat ve tek gözlem. **L1 önceden "ayırt edilemez" ilan edilir**; yalnız karne (kalibrasyon cezasının işareti ve büyüklüğü) yazılır.

### L2 (bilgi): Coulomb bayrağı

- Hubert-Ferrari 2000 bayrağı MARMARA_KUTU. Hedef: W içinde Türkiye bölgesindeki M≥6 ana şoklar. Bayrağın R1 ağırlıklı alarm payı τ = R1(kutu ∩ bölge)/R1(bölge). İsabet sayısı h; tek taraflı binom p = P(X ≥ h | N, τ). Bilgi satırı.

### K (bilgi): kapsam karnesi

- Her hedef M≥6 ana şok için: derlenmiş sayısal literatür satırı onun segmentini/bölgesini kapsıyor muydu (evet/hayır), erişilemeyen listede o bölgeyi hedefleyen çalışma var mıydı. Sayılar yazılır.

### B1 (hüküm 2): fay tabanlı Poisson − düzleştirilmiş sismisite, Türkiye M≥6

Bu satır literatür tahmininin kendisi değil, aynı ailenin (fay/segment bilgisi) yayımda donmuş açık girdisiyle (EDSF13, 2013) kurulmuş Poisson tahmini. Soru: fay bilgisi Türkiye'nin 2016–2025 M6 depremlerini düzleştirilmiş sismisiteden iyi konumladı mı?

- **Test bölgesi:** Natural Earth 10m (v5.1.2) Türkiye poligonu + 25 km tampon (LAEA, lat0 39, lon0 35); 0,1° hücre (merkez bölgedeyse).
- **Hedefler:** ComCat, W, M ≥ 6,0 (ComCat tercihli büyüklük), derinlik ≤ 40 km; Gardner–Knopoff (1974) pencereleriyle kümesizleştirilmiş (büyükten küçüğe, öncü ve artçı). Sorgu: `https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&starttime=2016-01-01T00:00:00&endtime=2026-01-01T00:00:00&minmagnitude=6.0&minlatitude=33&maxlatitude=44&minlongitude=24&maxlongitude=47&orderby=time-asc`. İndirilen dosyanın sha'sı sonuçta yazılır.
- **R1 (rakip, düzleştirilmiş sismisite):** ComCat 1976–2015, M ≥ 5,0, derinlik ≤ 40 km, kutu 24–47° D, 33–44° K (dosya sha aşağıda), GK kümesizleştirilmiş; her olaya σ 30 km Gauss; yıllık; M≥6'ya b = 1,0. Test bölgesine R1 toplamının %1'i kadar düzgün taban eklenir.
- **R2 (aday, EDSF13 fay Poisson'u):** EDSF13 bileşik fay kaynakları (TOP izleri), izi test bölgesine ≤ 50 km olanlar. Ṁ0 = μ·L·W·ṡ (μ 3·10¹⁰ Pa; L iz uzunluğu; W = (MAXDEPTH − MINDEPTH)/sin(ortalama eğim), eğim alt sınırı sin 0,1; ṡ = (SRMIN + SRMAX)/2). Mmax = MAXMAG > 0 ise o, değilse Wells–Coppersmith (1994) 5,08 + 1,16·log10 L. Kesik üstel b = 1,0, M 5,0–Mmax, moment dengeli; M≥6 oranı iz boyunca 1 km adımla σ 15 km Gauss ile hücrelere. **Hüküm satırında R2 toplamı R1 toplamına ölçeklenir (şekil kıyası)** ve aynı taban eklenir.
  - Gerekçe (kuru koşudan, 1976–2005 girdi / 2006–2015 hedef, bilinen veri): moment dengeli ham R2 Türkiye'de yılda ≈4,7 M≥6 bekliyor, R1 ≈0,28 (×16). Ham kıyas toplam terimi yüzünden yalnız kalibrasyonu ölçer; bu yüzden hüküm şekil kıyası, ham kıyas bilgi satırı.
- **Skor:** ızgara Poisson log olabilirliği, tek büyüklük kutusu, T = 10 yıl. IG = [Σ ln(λA/λB) − (ΛA − ΛB)]/N. SE: olay bootstrap 2000 (tohum 20261110). z = IG/SE, tek taraflı 1,645 (iki taraflı %90). Hüküm: z > 1,645 "aday önde", z < −1,645 "rakip önde", arası "ayırt edilemez".
- **Ateşleme kapısı:** kuru koşuda olay başı log oranın yayılımı ≈1,9 nat. N ≈ 6–10 ana şokta SE ≈ 0,6–0,8, MDE ≈ 1,0–1,3 nat. v1.2'nin Türkiye dışı M6'daki uzamsal kazancı +0,42 nat; bu büyüklükte bir fark **görülemez**. B1 yalnız ≥ ≈1 nat'lık bir farkı yakalar; daha küçük fark "ayırt edilemez" çıkar ve bu sonuç önceden beklenen sonuçtur.
- **Bilgi satırları:** B1k ham (moment dengeli) R2 − R1; B1b karışım 0,5·R1 + 0,5·R2(şekil) − R1; B1c 2023 hariç; B1d kümesizleştirmesiz (tüm M≥6).

## Ne değişmez, sonuç nereye gider

- Nihai Marmara modeli v1.3b değişmez. Bu iş yalnız literatür karnesi ve bir rakip satırıdır.
- Sonuç ileri test defterine **rakip** olarak girer: R2 (EDSF13 fay Poisson'u, şekil) ve R1, 2027 ileri testinde Türkiye M≥6 satırına rakip adayı olarak önerilir; defter sunucuda tutulduğu için satır `S2-DEFTER-SATIRI.json` olarak hazırlanır.
- Hücre oranları ve R1/R2'nin segment olasılıkları depoya yazılmaz, panele olasılık yazılmaz; yalnız log olabilirlik farkları ve literatürün kendi yayımlanmış sayıları yazılır.
- Tek koşu. Koşu sonrası kod hatası bulunursa düzeltilir ve hem ilk hem düzeltilmiş sonuç yazılır.

## Donmuş girdiler (sha256)

| Dosya | sha256 |
|---|---|
| `comcat_1976_2015_m5.csv` (ComCat, 10 Kasım 17:41 UTC indirme; kutu 24–47° D, 33–44° K, M≥5, 1976–2015) | `98d82dbb427d1fcda102bb37368d6752e7398c24ab9c643d82c57cda757bf7dd` |
| `turkiye_ne10m.geojson` (Natural Earth v5.1.2 admin-0, ADM0_A3 = TUR) | `67a62d716d42badeb897bbb9e05061d872fc0495f6d4449349ba7042039b6c63` |
| EDSF13 `DB-CFS-ESRI-shapefile.zip` (proje dosyaları, marmara-girdiler/edsf13) | `da0439f09379abf3799b07b171c5c52033de1c4411afa7aad974d43a663a6ce0` |
| `S2-literatur_tablosu.json` | `ed0512bb283db4cff0f7456d43ef1b39ab6022b2d0d604fde250089bd2d5ef86` |
| `tools/arastirma/s2_karne.py` | `388d2ac15031b74bb1298c2ab8f673fe9d01bc26c569fc571257f9eba5cdc5f3` |
