# A3 ön kayıt (sürüm 2.1): kilitlenme profili kırığın nerede duracağını önceden söyledi mi? (10 Kasım 2026)

Sürüm 1 bağımsız incelemede RED aldı (LLM okuyucusu kör değil, kontrol tasarımı yanlı, kapsam dışı düşmeleri yanlı, hüküm sırası belirsiz). Sürüm 2 onu yeniden yazdı ve ikinci incelemede KABUL aldı (iki koşulla); 2.1 o incelemenin 5 maddesini işler, başka değişiklik yok.

**Kör değil:** aday tanımı literatür taramasından ve veri envanterinden (A3_envanter, 23 olay) sonra yazıldı. Olay öncesi makalelerin şekilleri, hangi şeklin kullanılacağına karar vermek için görüldü (Métois 2012 Şekil 8, Métois 2013 Şekil 5, Ader 2012 Şekil 5b, Chlieh 2008 Şekil 12); kırık uçları bu şekiller üzerinde işaretlenmedi, hiçbir puan hesaplanmadı. Kırık uçları depremlerden bilindiği için "kırık nerede durdu" bilgisi zaten genel bilgi; korunan şey ölçümün mekanik olması. Türkiye dışı 2026'ya dokunulmaz.

## 1. Olaylar ve profil kaynakları (sabit)
Ana küme (dalma-batma, Mw ≥ 7, olay öncesi yayımlanmış ve doğrultu boyunca kilitlenme profili verilebilen model):
| Olay | Model (yayım < olay) | Profil |
|---|---|---|
| Illapel 2015-09-16 | Métois, Socquet, Vigny 2012 JGR | Şekil 8, kırmızı kalın eğri ⟨Φ⟩(enlem), 0–60 km |
| Iquique 2014-04-01 | Métois ve diğ. 2013 GJI | Şekil 5 sol, tercih edilen (3 levhalı) modelin ⟨Φ⟩(enlem) eğrisi |
| Gorkha 2015-04-25 | Ader ve diğ. 2012 JGR | Şekil 5b harita; doğrultu boyunca 10 km'lik kutularda, MFT izinden kuzeye 0–120 km şerit içindeki maskelenmemiş piksellerin ortalama kilitlenmesi (dik sınır sabit; diğer profillerin 0–60 km derinlik tanımına karşılık) |
| Chignik 2021-07-29 | Drooff ve Freymueller 2021 GRL (Zenodo 7644098, TDEFNODE) | sayısal; 0–60 km derinlikteki düğümlerin doğrultu boyunca 10 km kutu ortalaması |

Duyarlılık satırı (ana istatistiğe girmez): Mentawai 2010-10-25, Chlieh ve diğ. 2008 Şekil 12, F-f ve I-a eğrilerinin ortalaması, en büyüğüne bölünmüş (moment açığı hızı, kilitlenme değil).
Ayrı satır (ana istatistiğe girmez): Pazarcık 2023-02-06, Bletery ve diğ. 2020 Şekil 2, DAF boyunca 0–20 km ortalama; kapsam yalnız DAF doğusu, ölçü dalma-batmayla karşılaştırılamaz.
Çıkarılanlar: Maule (Ruegg 2009 yalnız tekdüze 2B model, doğrultu profili yok), diğer olaylar (olay öncesi model açık erişimde yok). Ek olay eklenmez.

## 2. Mekanik sayısallaştırma
- Eğriler (Illapel, Iquique, Mentawai): şekil sayfası 600 dpi işlenir; eksen kalibrasyonu yalnız eksen etiketlerinin piksel konumlarından (iki enlem, iki kilitlenme değeri); eğri rengi (RGB uzaklığı ≤ 60) piksel maskesiyle seçilir, her sütunda medyan. Belirsizlik bandı ve kesikli eğriler kullanılmaz.
- Harita (Gorkha, Pazarcık): graticule kesişimlerinden doğrusal coğrafi kalibrasyon (≥4 kontrol noktası, artık ≤ 2 piksel olmalı); renk çubuğundan 50 düğümlük renk→değer tablosu, her piksel en yakın renge atanır; beyaz/gri maskeli pikseller atılır.
- Her eğri ve harita için maske bindirme görüntüsü (seçilen pikseller kaynak şeklin üstünde) depoya konur. Eğrili sütunların %5'inden fazlasında ikinci bir piksel kümesi çıkarsa (maske eğri dışı öğe yakalıyor) eşik değiştirilmez; o olay "okunamaz" sayılır.
- Hiçbir adımda değer elle okunmaz. Betik ve kalibrasyon noktaları depoda.

## 3. Kırık uçları
USGS sonlu fay modeli; ürünler sabit, erişim 2026-11-10: Illapel us20003k7a, Iquique usc000nzvd, Gorkha us20002926, Chignik ak0219neiszm_2, Pazarcık us6000jllz_1, Mentawai usp000hnj4. Başka sürüm kullanılmaz. Doğrultu ekseni: kayma ağırlıklı ortalama doğrultu, kayma ağırlıklı merkezden geçen büyük çember. Alt faylar bu eksene izdüşürülür; birikimli moment %5 ve %95 konumları iki uç (x1, x2), L = x2 − x1. Bir uç FFM alanının kenar satırına/sütununa düşüyorsa o uç "alan sınırıyla kesilmiş" diye işaretlenir ve olduğu gibi kullanılır. Profil aynı eksene izdüşürülür (enlem eğrileri için profil noktası, enlem çizgisinin USGS Slab2'nin 30 km izohipsiyle kesişimi; Slab2 erişilemezse FFM merkezinin boylamı).

## 4. İstatistik
- Olay e için uç değeri: S_e = [c̄(x1) + c̄(x2)]/2, c̄ = uç çevresinde ±20 km ortalama.
- Boş hipotez: aynı L uzunluklu kırık, iki ucu da [a + 20 km, b − 20 km] içinde kalacak biçimde tekdüze rastgele yerleşir ([a, b] model kapsamı; ±20 km pencere de kapsamda kalır). (b − a) − L < L olan olayda boş dağılım neredeyse tek noktaya çöker; böyle bir olay sayısallaştırmadan önce "bilgisiz" diye dışarı alınır. E0[S_e] ve dağılımı bu yerleşimden (Monte Carlo, 10^5, tohum 20261110).
- Ana istatistik: T = olaylara eşit ağırlıklı ortalama (S_e − E0[S_e]). p: aynı Monte Carlo'dan, olaylar bağımsız, tek yönlü (T küçük).
- Ucu model kapsamı dışında kalan olay tümüyle dışarı alınır (tek uç kalsa da), sayısı raporlanır.

## 5. Hüküm sırası (tek ve kesin)
1. Veri yok: okunabilir olay < 4 ya da uç < 8 → "veri yok", kapanır.
2. Destekleyici bilgi: p < 0,05 ve T ≤ −0,2.
3. Ters yönde: T ≥ +0,2.
4. Aksi halde ayırt edilemez.
Bu bir bilgi satırıdır; rakip sürüm kurulmaz, v1.3b değişmez.

## 6. Marmara yan satırı (sezgisel, boyut uyumsuz)
Yalnız sözle: sonuç destekleyiciyse "CMF batısındaki kısmen sünen kesim kırık durdurucu adayı" notu v1.7 ortak kırılma payının yanına bilgi olarak yazılır. Yüzey sünme hızı / blok hızı oranı derinlik ortalamalı kilitlenmeyle aynı nicelik değildir; sayısal taşıma yapılmaz.

## 7. Kısıtlar
N küçük (4 olay, 8 uç), güç zayıf; profiller farklı yöntemlerden (enlem eğrisi, harita kutusu, sayısal düğüm); Chignik sayısal, diğerleri şekilden. Dalma-batmadan doğrultu atımlı faya aktarım varsayımdır. "Veri yok" kapısı fiilen ya hep ya hiç: ana kümede tam 4 olay ve 8 uç gerekir, tek bir olayın düşmesi (okunamaz, bilgisiz ya da kapsam dışı) satırı kapatır. Bu eşik sonradan gevşetilmez.
