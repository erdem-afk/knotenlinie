# TR-13b sonucu: büyük doğrultu atımlı depremden önceki 3 yılda sismisite yerelleşmesi (sınırlı koşu)

Tek koşu: 17 Kasım 2026, 12:24–12:47 UTC, 0 €. Ön kayıt: `kayit/onkayit/TR-13b_sinirli-kosu_ONKAYIT.md` (donduruldu,
commit 41efef8). Betik sha256 `d2494e6d…`. Çıktı: `kosu/tr13b_hukum.json`, `kosu/gercek_z.json`, `kosu/durum.json`.

## Hüküm (bağlayıcı)

**Ayırt edilemez (dal 5).** Keşif dışı K = 10 küme; bu bileşimle görülebilir en küçük etki **f ≈ 0,39** (arka planın bu
kesri kırık bandına toplanırsa güç 0,80; koşudan önce, gerçek R ve N3bg ile yapayda yeniden hesaplandı). Daha küçük
yerelleşme hakkında bilgi yok. Bu bir H0 değildir.

| | z̄ (küme ortalaması) | p, dallanma 0,4 | 0,6 | 0,8 |
|---|---|---|---|---|
| Bütün liste (13 küme, 15 olay) | −0,44 | 0,205 | 0,239 | 0,288 |
| Keşif dışı (10 küme) | −0,60 | 0,141 | 0,182 | 0,217 |

Kural R0 her iki listede üç dallanmada da p ≤ 0,05 isterdi; hiçbiri sağlanmadı. Negatif z yerelleşme yönüdür: ortalama
iddianın yönünde ama ETAS'ın kendi ürettiği dağılımın içinde. Yapay denetim (D-3) geçti: yanlış alarm 0,016, f = 0,4
gücü 0,84. Girdi sha256'ları uyuştu; 16 olaydan biri (Jan Mayen 2025) "referans arka planı < N + 5" kuralıyla düştü; üstveri tahmininde düşeceği
öngörülen Ishigaki 2009 ise N3bg = 50 ile tam sınırda kaldı. Keşif dışı küme sayısı yine 10.

## Bilgi satırları (hükmü değiştirmez)

- Olay başına z: Küba 2024 −3,9; Kumamoto 2016 −2,7; Darfield (Methven) 2010 −2,6; Akashi (Kobe) 1995 −1,4; Ishigaki
  2009 −1,1; İzmit 1999 −0,9; Superstition Hills 1987 −0,2; Cook Boğazı 2013 +0,1; Gisborne 2021 +0,1;
  Jamaika 2020 +0,4; Chiniak 2018 +0,4; Ridgecrest 2019 +0,8; Hector Mine 1999 +0,9; Loma Prieta 1989 +1,2; Big Lagoon
  2005 +1,8. Üç olay güçlü negatif, geri kalanı sıfır çevresinde: ortak bir kayma değil, dağınık bir tablo.
- İddianın kendi keşif olayları (İzmit, Hector Mine, Ridgecrest) bu ölçüyle öne çıkmıyor (−0,9, +0,9, +0,8). Ölçü
  BZ20'nin birebir yeniden kurulumu değildir (§9.3), bu yüzden "iddia çürüdü" denemez.
- Küba 2024'ün referans penceresi Jamaika 2020 artçılarını içerebilir (ön kayıt Ö-a); en negatif z'nin bir kısmı bundan
  gelebilir.
- T3 (üyenin kendi sıfır havuzunun %5 niceliğini aşması): 15 üyeden 1; binom p 0,54.
- T2 (z − z_p, 9 küme, işaret çevirme): p 0,029. Plasebo penceresi yapay sınamada seçici çıkmadığı için ön kayıtta
  bilgi satırına indirilmişti; plasebo z'leri −4,4 ile +5,9 arasında dağılıyor ve plasebo T1 p'si 0,92. Bu satır tek
  başına okunmaz; üç bilgi satırından biri ve düzeltmesizdir.

## Ne söyler, ne söylemez

Söyler: bu ölçüyle, 10 bağımsız kümede, arka planın ≈ %40'ından fazlasının kırık bandına toplandığı bir yerelleşme
yok. Söylemez: daha küçük bir yerelleşmenin olmadığını; Marmara için bir şey (Doğu Akdeniz'den keşif dışı olay yok);
bir olasılık terimi değildir.

## Başarısızlığın biçimi ve çıkan soru

Biçim: örneklem. Ortalama doğru yönde, üç olay güçlü, ama 10 kümeyle yalnız çok büyük etki görülebiliyor. Etkiyi
yarıya indirmek (f ≈ 0,2) için ≈ 40 küme gerekir. Çıkan aday **TR-13c**: aynı dondurulmuş ölçü ve kodla, büyüklük
eşiği Mw 6,5'ten 6,0'a indirilerek ve yoğun ağ bölgelerine (Kaliforniya, Japonya, Yeni Zelanda, İtalya, İzlanda)
sınırlanarak K büyütülebilir mi; TR-13 sayımı M ≥ 6,0'da 31 küme vermişti, ortak Mc ve doyma kurallarıyla kaç kaldığı
0 € sayımla ölçülmeli. Bu koşuda görülen 15 olay TR-13c'de geliştirme verisi sayılır, hüküm yalnız yeni olaylardan
okunur.
