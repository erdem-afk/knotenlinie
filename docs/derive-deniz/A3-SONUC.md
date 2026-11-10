# A3 sonuç: veri yok, kapandı (10 Kasım 2026)

Kural: A3-KURAL.md sürüm 2.1, DONDUR-a3.json (sha256 ad603eb0…afbc, OTS), commit a48c2e9. Koşu dondurmadan sonra.

## Ne oldu
- **FFM uçları** (kural §3, ürünler sabit) hesaplandı: `a3-kosu/ffm_uclar.json`. Hiçbir uç FFM alan kenarına düşmedi.
- **Chignik** sayısal profili okundu: TDEFNODE flt.gmt, φ başlık satırının 3. sayısal alanı (doğrulama: 2. alan / φ = 59–66 mm/yıl yakınsama hızı), 0–60 km düğümleri, 10 km kutular: `a3-kosu/chignik.json`. Okunabilir.
- **Illapel** (Métois 2012 Şekil 8) maske kapısından geçemedi. RGB ≤ 60 kırmızı maskesi eğrinin yanında aynı kırmızıyla yazılmış üç segment etiketini ("Maule segment", "Metropolitan segment", "Atacama segment") çizim alanının içinde yakalıyor. Eğrili 3029 sütunun 870'inde (%28,7) ikinci küme var; eşik %5. Bindirme: `a3-kosu/illapel_maske.png`. Kural §2 gereği eşik değiştirilmedi, olay **okunamaz**.

## Hüküm
§5 adım 1: ana kümede okunabilir olay 3 < 4 → **veri yok**, satır kapanır. Kural §7 bu kapının ya hep ya hiç olduğunu ve gevşetilmeyeceğini önceden yazmıştı.

Hüküm sırası tek ve kesin olduğu için Iquique ve Gorkha sayısallaştırılmadı, T ve p hesaplanmadı. Kısmi bir istatistik raporlanmaz. Mentawai ve Pazarcık satırları da açılmadı.

Defter: bilgi satırı "A3 kilitlenme → kırık ucu: veri yok". v1.3b değişmez, rakip yok, Marmara yan satırı yazılmaz.

## Ders
Olay öncesi, doğrultu boyunca açık kilitlenme profili dünyada yaklaşık 4 olayda var. Bu profillerin üçü yalnız şekil olarak duruyor. Mekanik okuma, şekil tasarımına (aynı renkte etiket) takılabiliyor. Bu soruyu sınamanın yolu sayısal model dosyası yayımlanmış olaylar (Chignik gibi). Bugün bunlar 4'e ulaşmıyor.

Maliyet 0 €.
