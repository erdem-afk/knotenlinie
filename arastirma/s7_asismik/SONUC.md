# S7 sonucu: asismik kayma geçicileri M≥4 oranını ETAS'ın üstünde artırıyor mu

**Özet (10 Kasım 2026, ön kayıt DONDUR-s4-s7 sha 91506751…, OTS; tek koşu; 0 €)**
- Hüküm: **ayırt edilemez.** Doğrulama 2004–2014 (19 hücre, 30 M≥4 hedef, 11 yıl; ateşleme kapısı açık):
  IG = −0,058 ± 0,118 nat/olay. Nokta tahmini ETAS'ın lehine.
- β seçimde (1990–2003, 96 hedef) +0,67: ivmelenen hücrelerde M≥4 oranı yüksekti (profil olabilirlikte
  β = 0'a göre ≈ +12 nat). Bu ilişki doğrulamaya taşınmadı.
- Ek satırlar hepsi negatif: ham A −0,071 ± 0,108; M≥5 sonrası 1 yıl/30 km pencereleri hariç −0,092 ±
  0,125 (N 19); 2004 Parkfield dizisi hariç −0,183 ± 0,119 (N 25); M≥5 hedef 4 olay, IG −0,28 (güç yok).
- Marmara'ya bağ: CMF'de bir sünme hızlanması görülürse ETAS üstüne çarpan uygulamak için Kaliforniya'da
  sınanmış dayanak yok. İleri test defterine yalnız bilgi satırı; İstanbul olasılığına yayılmaz.

## Koşu

`python3 -I s7.py cikti` → `cikti/sonuc.json` (kod sha256, izlenen hücre listesi ve sha256'sı içinde),
günlük `kosu1.log`.

ComCat sorgusu: `https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&starttime=<yıl>-01-01&endtime=<yıl+1>-01-01&minlatitude=35.2&maxlatitude=38.8&minlongitude=-123.3&maxlongitude=-120.2&minmagnitude=2.5&orderby=time-asc`
(yıl yıl, 2014 bitişi 2014-12-31T23:59:59) ve iki ek kutu (aşağıda). `veri/comcat.csv` sha256 8dafa142….

## SAPMA (hata düzeltmesi, koşudan önce)

1. Ön kayıttaki indirme kutusu (35,2–38,8 K, 123,3–120,2 B) "izlenen alanın her yönde 0,3°
   genişletilmişi" diye tanımlıydı, ama izlenen 19 hücreden ikisi kutunun dışında çıktı (Long Valley
   37,7 K 118,9 B; Mendocino 40,3 K 124,5 B). Tanımın kendisine uymak için bu iki hücrenin ±0,3° kutuları
   ayrıca indirildi (6 489 olay). Hücre listesi hedeflere bakmadan, yalnız tekrarlayan kataloğundan çıktı.
2. Aki–Utsu ΔM: ön kayıt değer vermiyor; katalog hassasiyeti 0,01 alındı (b = 0,999, 4 720 olay).
3. İncelemeci tur 1'de ≤2003 ile 17 hücre saymıştı; kod 19 buldu. Fark ikinci ek kutudaki iki hücre
   olabilir; kural metnine göre kodun sayımı esas alındı.

## Model ayrıntıları

ETAS (1985–2003, izlenen hücreler, M≥2,5): K 0,0098, α 0,63, c 0,0030 gün, p 1,027; μ_h 1,8·10⁻⁶ –
0,032/gün. M≥4 beklenen/gözlenen: seçim 52,4 / 96, doğrulama 36,0 / 30. ETAS seçimde M≥4'ü düşük
tahmin ediyor (düşük α ve b ≈ 1 ile M≥4 ekstrapolasyonu); β'nın seçimde pozitif çıkması bu açığın bir
kısmını taşıyor olabilir.

A* doğrulama ortalaması −0,05, sd 0,65 (hücreler arası medyan çıkarıldığı için ortalama ≈ 0).

## Yorum

Hüküm H1 değil. "Asismik geçici" yorumu yazılmaz. Seçimdeki pozitif β, doğrulamada kazanca dönüşmedi;
Parkfield 2004 dizisini çıkarınca IG daha da düşüyor (−0,18), yani dizideki artçı oranını kısmen
yakalıyor, başka yerde zarar veriyor. Güç: N = 30 ile SE ≈ 0,12; Uchida 2016 ölçeğinde (≈ +0,3 nat)
bir etki görülürdü, küçük etki görülemez.

## Defter

Bilgi satırı: "S7 asismik geçici (K. Kaliforniya, 2004–2014): ayırt edilemez, IG −0,06 ± 0,12, β +0,67."
