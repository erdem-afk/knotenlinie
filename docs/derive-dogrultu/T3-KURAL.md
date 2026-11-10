# T3 ön kaydı: kayma öngörülebilirliği, çok olaylı sınav (10 Kasım 2026)

Seçim: Erdem, 10 Kasım 22:45. Kaynaklar: Vavra, Fialko, Bulut 2025 (Kahramanmaraş "gevşek kayma öngörülebilir"), Ulrich vd. 2026 (Mandalay "asgari kayma öngörülebilir"), Shimazaki–Nakata 1980.

**Körlük beyanı (Ek 0):** kör değil. İki kaynak çalışmanın özet sonucu (kayma ≈ ya da > biriken açık) biliniyor. Kural yazılırken hiçbir segment için sayı derlenmedi.

## Soru

Bir segmentte eş-sismik ortalama kayma, son depremden beri biriken açıkla (kayma hızı × geçen süre) mı, yoksa yalnız kırık uzunluğundan gelen ölçek ilişkisiyle mi daha iyi tahmin edilir?

## Veri derleme kuralı

- Birim: olay-segment. Büyük doğrultu atımlı kıta depremleri, Mw ≥ 7,0, 1939–2025 (KAF 1939–1999 dizisi dahil; Türkiye 2016+ verisi mühür açıldığı için geliştirme verisi). Türkiye dışı 2026 yok.
- Her olay-segment için üç sayı, her biri kaynağıyla (makale, tablo/şekil) birlikte:
  1. **t_last:** önceki büyük depremin yılı, **olaydan önce** yayımlanmış bir kaynaktan.
  2. **v:** uzun dönem kayma hızı (mm/yıl), **olaydan önce** yayımlanmış jeolojik ya da jeodezik kaynaktan; birden çoksa aritmetik ortalama.
  3. **D_obs:** segmentin ortalama eş-sismik kayması (yüzey ortalaması ya da sonlu fay modeli ortalaması; olay sonrası kaynak).
- Üçünden biri tam metinden okunamıyorsa segment dışarıda kalır. Sayılar elle derlenir, tablo puanlamadan önce sha256 ile dondurulur (Ek 1).

## Modeller

- **Açık (aday):** D_açık = v × (t_olay − t_last).
- **Ölçek (rakip):** Wells–Coppersmith 1994 doğrultu atımlı, ortalama yer değiştirme – yüzey kırık uzunluğu: log10 AD = −1,70 + 1,04 log10 SRL (SRL = olayın toplam kırık uzunluğu, km).
- Skor: log10(D_obs) için σ = 0,25 sabit Gauss olabilirlik, her iki model için aynı. Fark ΔL = Σ ln L_açık − Σ ln L_ölçek, olay bazında blok bootstrap (aynı olayın segmentleri birlikte).

## Hüküm

- Ateşleme kapısı: en az 6 olay-segment ve en az 3 bağımsız olay; değilse "veri yetersiz".
- **H1:** ΔL > 0 ve %90 bootstrap aralığı sıfırı dışlar → açık tabanlı büyüklük kestirimi Marmara'ya taşınır (bilgi satırı: CMF, PIF, Ganos için son olaydan beri açıkla koşullu Mw aralığı; CMF hızı 11 ± 3 mm/yıl Y1b'den; PIF kayma hızı ölçülemediği için 3 senaryo).
- **H0:** aksi.
- **Bilgi satırları:** oran R = D_obs / D_açık'ın medyanı ve dağılımı (Vavra ve Ulrich'in "≥ 1" bulgusunun çok olaylı karşılığı); σ = 0,15 ve 0,35 duyarlılığı.

v1.3b değişmez; sonuç ileri test defterine bilgi satırı (ya da sunucuda kurulacak rakip moment dalı önerisi) olarak girer.
