# S7 sonucu: asismik kayma geçicileri M≥4 oranını ETAS'ın üstünde artırıyor mu

**Özet (10 Kasım 2026, ön kayıt DONDUR-s4-s7 sha 91506751…, OTS; iki koşu, hata düzeltmesi yalnız bir ek satırda; 0 €)**
- Hüküm: **ayırt edilemez.** Doğrulama 2004–2014 (19 hücre, 30 M≥4 hedef, 11 yıl; ateşleme kapısı açık):
  IG = −0,058 ± 0,118 nat/olay. Nokta tahmini ETAS'ın lehine.
- β seçimde (1990–2003, 96 hedef) +0,67: ivmelenen hücrelerde M≥4 oranı yüksekti (profil olabilirlikte
  β = 0'a göre ≈ +12 nat). Bu ilişki doğrulamaya taşınmadı.
- Ek satırlar hepsi negatif: ham A −0,071 ± 0,108; M≥5 sonrası 1 yıl/30 km pencereleri hariç −0,092 ±
  0,125 (N 19); 2004 Parkfield dizisi hariç −0,153 ± 0,111 (N 25; koşu 1'de hatalı −0,183); M≥5 hedef 4 olay, IG −0,28 (güç yok).
- Marmara'ya bağ: CMF'de bir sünme hızlanması görülürse ETAS üstüne çarpan uygulamak için Kaliforniya'da
  sınanmış dayanak yok. İleri test defterine yalnız bilgi satırı; İstanbul olasılığına yayılmaz.

## Koşu

`python3 -I s7.py cikti` → `cikti/sonuc.json` (kod sha256, izlenen hücre listesi ve sha256'sı içinde),
günlük `kosu1.log`. Koşu 2 (hata düzeltmesi, aşağıda): `cikti/sonuc.json`, `kosu2.log`; koşu 1 çıktısı
`cikti/sonuc_kosu1.json`. İki koşu yalnız Parkfield ek satırında farklı.

ComCat sorgusu: `https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&starttime=<yıl>-01-01&endtime=<yıl+1>-01-01&minlatitude=35.2&maxlatitude=38.8&minlongitude=-123.3&maxlongitude=-120.2&minmagnitude=2.5&orderby=time-asc`
(yıl yıl, 2014 bitişi 2014-12-31T23:59:59) ve iki ek kutu (aşağıda). `veri/comcat.csv` sha256 8dafa142….

## SAPMA (hata düzeltmesi, koşudan önce)

1. Ön kayıttaki indirme kutusu (35,2–38,8 K, 123,3–120,2 B) "izlenen alanın her yönde 0,3°
   genişletilmişi" diye tanımlıydı, ama izlenen 19 hücreden ikisi kutunun dışında çıktı (Long Valley
   37,7 K 118,9 B; Mendocino 40,3 K 124,5 B). Tanımın kendisine uymak için bu iki hücrenin ±0,3° kutuları
   ayrıca indirildi (6 489 olay). Hücre listesi hedeflere bakmadan, yalnız tekrarlayan kataloğundan çıktı.
2. Aki–Utsu ΔM: ön kayıt değer vermiyor; katalog hassasiyeti 0,01 alındı (b = 0,999, 4 720 olay).
3. İncelemeci tur 1'de ≤2003 ile 17 hücre saymıştı; kod 19 buldu. Hücre listesi yalnız tekrarlayan
   kataloğundan çıkar (ComCat kutuları etkilemez); sonuç incelemesi ≤2003 kuralıyla bağımsız olarak 19
   buldu (tüm katalogla 31). Kodun sayımı esas alındı.

## Hata düzeltmesi (sonuç incelemesinden sonra, koşu 2)

Parkfield ek satırı koşu 1'de dizinin olaylarını yalnız gözlenen sayımdan siliyor, aynı hücre-çeyreklerin
beklenen değerlerini bırakıyordu (dengesiz, IG'yi aşağı çeker). Ön kayıttaki "dizi hariç" ifadesine uygun
olarak koşu 2'de, M≥5 satırındaki gibi, merkezi episantra ≤ 30 km olan hücrelerin ilk 90 günle kesişen
çeyrekleri maskelendi: −0,183 ± 0,119 → −0,153 ± 0,111 (N 25). Hüküm ve diğer bütün sayılar aynı.

Ön kayıtta yazmayan küçük ayrıntılar (etkisi önemsiz): 58 "quarry blast" satırı ayıklandı; ETAS
optimizasyonunda α ≥ 0, c ≤ 1 gün, p ≤ 2 sınırları; pencereler 365,25 günlük yıl. ΔM = 0,1 ile (katalog
büyüklüklerinin %17'si tek ondalıklı) b 0,905, β 0,52, IG −0,059 ± 0,088: hüküm değişmez.

## Model ayrıntıları

ETAS (1985–2003, izlenen hücreler, M≥2,5): K 0,0098, α 0,63, c 0,0030 gün, p 1,027; μ_h 1,8·10⁻⁶ –
0,032/gün. M≥4 beklenen/gözlenen: seçim 52,4 / 96, doğrulama 36,0 / 30. ETAS seçimde M≥4'ü düşük
tahmin ediyor (düşük α ve b ≈ 1 ile M≥4 ekstrapolasyonu); β'nın seçimde pozitif çıkması bu açığın bir
kısmını taşıyor olabilir.

A* doğrulama ortalaması −0,05, sd 0,65 (hücreler arası medyan çıkarıldığı için ortalama ≈ 0).

## Yorum

Hüküm H1 değil. "Asismik geçici" yorumu yazılmaz. Seçimdeki pozitif β, doğrulamada kazanca dönüşmedi;
Parkfield 2004 dizisini çıkarınca IG daha da düşüyor (−0,15), yani dizideki artçı oranını kısmen
yakalıyor, başka yerde zarar veriyor. Güç: N = 30 ile SE ≈ 0,12; H1 için IG > +0,24 gerekirdi, bundan küçük etki görülemez (Uchida 2016
etkisinin nat cinsinden karşılığı hesaplanmadı).

## Defter

Bilgi satırı: "S7 asismik geçici (K. Kaliforniya, 2004–2014): ayırt edilemez, IG −0,06 ± 0,12, β +0,67."

## Sonuç incelemesi

Bağımsız alt ajan: KABUL. Koşu 1 yeniden üretildi (sonuc.json birebir aynı); ayrıştırma (7 713 dizi, 27 674
olay), gerçek zamanlı kural, P paydası, pencereler, A*, ETAS integrali (quad ile 1e-12), β uydurması,
jackknife ve hüküm mantığı ön kayıtla uyumlu. Tek hata Parkfield ek satırı (yukarıda düzeltildi).
Hükmün sağlamlığı: IG − 2·SE = −0,29; bulunan hiçbir sorun ±0,24 sınırına yaklaşmıyor.
