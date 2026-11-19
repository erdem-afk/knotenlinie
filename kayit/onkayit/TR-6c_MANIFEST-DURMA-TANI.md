# TR-6c manifest durması: tanı (ara durum, 19 Kasım 2026)

Yalnız olay ÖNCESİ veri ve kaynak modelleri kullanıldı. Olay sonrası hiçbir katalog sorgusu yapılmadı; hiçbir lobda
sayı, oran ya da ΔCFF hesaplanmadı. Manifest aşaması yeniden başlatılmadı.

## Durma

`python3 -I -B -u kayit/turetme/tr6/tr6a_kosu.py --tasarim c manifest` (Hetzner, 2026-11-19T12:32Z, ham dizin
`/mnt/project-files/turetme/tr6a-ham/on_20261119T123202Z`) ilk aday birimde (usp0005w12, 1993 Hokkaido Nansei-oki)
`tr6a_ffm.BicimHata: birim denetimi: 22 alt fayda rijitlik [0,3; 300] GPa dışında, medyan 67.5 GPa` ile durdu.

## Tanı (doğrulandı)

- Ürün `urn:usgs-product:us:finite-fault:usp0005w12:1539796033250`; `.param` sha256 `7416c23c…432e`, `.fsp` sha256
  `8a76d7ef…1353` (sunucudaki arşivle ve ayrı indirmeyle bayt bayt aynı).
- `.param` başlığı koordinat anlamını yazmıyor; `.fsp` "center" yazıyor: Ek 1 E1.2 (i′) ile `.fsp` okunur (263 alt fay).
- Takılan 22 satır iki segmentin EN ÜST sırasıdır (`.fsp` merkez derinliği 1,625 km; `.param` 0,6 km). İma edilen
  rijitlik her satırda aynı: 1,02e−4 GPa = 1,02e5 Pa.
- Ürünün kendi hız-yoğunluk tablosunun ilk katmanı deniz suyudur: 0–2,71 km, Vp 1,50, **Vs 0,01 km/s, ρ 1,02 g/cm³**.
  ρ·Vs² = 1020 × 10² = 1,02e5 Pa. Moment sütunu = katman μ × kayma × alan; `.param` ile `.fsp` aynı değerleri taşır.
  Bu bir birim kayması ya da yuvarlama değil, ürünün kendi (su katmanlı) rijitlik modelidir.
- Bu 22 satırın moment payı toplamın 3,5e−7'sidir; moment sağlaması (toplam / başlık Mo) tutar.
- Moment sütunu ΔCFF'ye girmez: Okada kaynağı kayma (m) ve μ = 30 GPa ile kurulur. Moment yalnız (1) birim denetiminde,
  (2) moment sağlamasında, (3) `ffm_ortalama_duzlem`'in alıcı düzlem ağırlığında kullanılır.

## Tarama (155 havuz olayının hepsi; manifestin indireceği ürünler)

Ürünler USGS'ten (yalnız olay ayrıntısı + sonlu fay dosyaları, genel User-Agent) karalama dizinine indirildi ve
dondurulmuş `tr6a_ffm.coz` (`arsivden_oku` ile aynı çağrı) uygulandı:

| sonuç | sayı |
|---|---|
| geçti | 137 |
| veri yok (ürün dosyası yok) | 2 |
| VeriYok (moment sağlaması, oran 0) | 3 |
| BicimHata: birim denetimi, su katmanı | 12 |
| BicimHata: "başlıkta M0 yok" (`.fsp` başlığı `Mw = 0  Mo = 0 Nm`) | 1 |

- Su katmanı (12): usp00047gj, usp00050sq, **usp0005w12**, usp000c2ka, usp000db93, usp000ensm, **usp000exfn**,
  **usp000jr83**, usc000phx5, us20002das, us10004u1y, **us6000dg77** (kalın: koşu adayı birim, 4). Hepsinde takılan
  satırların ima ettiği μ 1,02e−4 GPa ve hepsi ürünün kendi tablosundaki Vs 0,01 / ρ 1,02 katmanında.
- M0 = 0 (1): **usp000j9rr** (2011 Van, koşu adayı). `.fsp` başlığı "Mw = 0  Mo = 0 Nm" yazıyor; alt fay momentleri
  toplamı 5,9e19 N·m; `.param` başlığında M0 yok.
- Koşu adayı olmayan 8 olayda durma olmaz (`_R_A` BicimHata'yı yakalar, R_A None yazılır); adaylardaki 5 ürün koşuyu
  sırayla durdururdu.

## Sonraki adım

Karar, ön kayıt eki ve kod düzeltmesi: bu dosyanın sonundaki "Karar" bölümü (yazılacak).
