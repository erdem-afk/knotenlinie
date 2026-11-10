# A3 ön kayıt: kilitlenme haritaları kırığın nerede duracağını önceden söyledi mi? (10 Kasım 2026)

Kör değil: aday tanımı literatür taramasından, veri envanteri (A3_envanter, 23 olay) bu kuraldan önce çıkarıldı. Hiçbir kırık ucu kilitlenme haritası üzerinde okunmadı, hiçbir puan hesaplanmadı. Türkiye dışı 2026 olaylarına dokunulmaz.

## Olay kümesi (sabit)
Mw ≥ 7, 2005–2025, olaydan ÖNCE yayımlanmış kilitlenme modeli olan ve modelin tam metni/verisi açık erişimde okunabilen olaylar. Envantere göre: Maule 2010 (Ruegg 2009), Iquique 2014 (Métois 2013), Illapel 2015 (Métois 2012; Vigny 2009 yedek), Gorkha 2015 (Ader 2012), Mentawai 2010 (Chlieh 2008), Chignik 2021 (Drooff ve Freymueller 2021, sayısal TDEFNODE), Pazarcık 2023 (Bletery 2020; Cavalié ve Jónsson 2014 yedek). N = 7 olay, 14 kırık ucu (1 doğrultu atımlı). Elazığ 2020 (Mw 6,7) eşik altında, dışarıda. Ek olay eklenmez.

## Noktalar
- Kırık ucu: USGS sonlu fay modeli (FFM) alt fayları doğrultu boyunca sıralanır; birikimli moment %5 ve %95'e ulaştığı doğrultu konumları iki uçtur. Nokta, o konumda en büyük kaymalı derinlik satırının alt fay merkezi.
- Kontrol: her olay için 4 nokta, merkezden ±(L/2 + 200 km) doğrultu aralığında tekdüze rastgele (tohum 20261110), uçlara 30 km'den yakın olanlar yeniden çekilir; derinlik satırı aynı (doğrusal uzatma).
- Toplam 14 uç + 28 kontrol = 42 nokta, karıştırılır, olay ve tür bilgisi silinir.

## Okuma (kör protokol)
Ayrı bir okuyucu (yeni ajan) yalnız nokta listesini (enlem, boylam) ve olay öncesi makalenin kilitlenme şeklini alır; noktaların ne olduğu söylenmez. Her nokta için kilitlenme sınıfı: 0–0,2 / 0,2–0,4 / 0,4–0,6 / 0,6–0,8 / 0,8–1 ya da "kapsam dışı". Sınıf ortası sayı olarak kullanılır. Chignik'te değer sayısal dosyadan, aynı nokta listesiyle okunur. Okuyucu olayı tanıyabilir (Maule gibi); bu sınır olarak yazılır.

## Puan ve hüküm
- Ana istatistik: uçlardaki ortalama kilitlenme − kontrollerdeki ortalama (kapsam dışı noktalar düşer). Tek yönlü permütasyon testi, olay içinde etiket karıştırma, 10.000 permütasyon.
- Ateşleme kapısı: N 14 uç, güç zayıf. Bu satır HÜKÜM DEĞİL, BİLGİ satırıdır; p < 0,05 ve fark ≤ −0,2 ise "destekleyici bilgi", değilse "ayırt edilemez".
- Yan bilgi: lojistik P(dur | c), tek parametre; Marmara'ya taşıma yalnız bilgi: CMF batısı sünen kesim (c ≈ yüzey sünmesi 10–15 mm/yıl / blok hızı) için P(dur) yazılır, v1.7 f ile karşılaştırılır. Rakip sürüm kurulmaz; v1.3b değişmez.
- Doğrultu atımlı tek olay (Pazarcık) ayrıca satır olarak verilir, istatistiğe dahil.

## Kapanış koşulu
Okuyucu 42 noktanın %50'sinden fazlasını "kapsam dışı" derse satır "veri yok" olarak kapanır.
