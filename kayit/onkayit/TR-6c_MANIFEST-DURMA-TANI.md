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

## Karar ve uygulama (19 Kasım 2026)

Ön kayıt Ek 2 (dosyanın sonuna; gövdenin ilk 66 337 baytı ve sha256 `172b2ebd…aa6c` değişmedi):
- **E2.1** (commit ad7e4602): bant dışı alt fay, ürünün kendi `.fsp` hız-yoğunluk tablosunda kendi katmanının
  ρ·Vs²'sinin √10 katı içindeyse tutarlı. Medyan koşulu aynı. 12 su katmanlı ürün geçer.
- **E2.2** (commit 46044c36): başlık M0'ı açıkça 0 ise §3.3 sağlaması tutmaz -> VeriYok (usp000j9rr, Van 2011, koşu
  adayı, "veri yok" olur). Yazılmamış M0'da davranış aynı. Bu madde ayrı commit'tir; geri alınmak istenirse
  `git revert 46044c36` yalnız onu kaldırır (Van o zaman manifesti yine durdurur).
- Tarama son durumu: 149 geçer, 4 VeriYok (moment sağlaması), 2 veri yok (dosya yok); durduran ürün yok. Eski kodla
  geçen 137 ürünün `coz` çıktısı yeni kodla JSON olarak aynı.
- Sınamalar: `tr6a_test_yapay.py` 71 sınama geçti (69 + 2 yeni). Kapılar: `git_denetle` (13 dosya),
  `onkayit_uyusmuyor() = False`, `sinama_degerlendir -> (None, 'yedek_d')`.
- Bağlayıcı sınama: değişen işlevler bağlayıcı yolda çağrılmaz (taslak + `sys.setprofile` denemesi: Okada, 17 hücre
  parçası, tamlık (d); hiçbir `tr6a_ffm` çerçevesi çalışmadı). Yeniden koşulmaz; sonuç kuralı yalnız tutmayan ölçütte
  işler. `tr6c_sinama_sonuc.json`'daki `tr6a_ffm.py` sha'sı (`60871db7…`) yeni sha'dan (`b13b5957…`) farklıdır; manifest
  `girdi.kod` yeni sha'yı yazar; kod incelemesi (§C12 adım 5) bunu Ek 2 ile birlikte denetler.

## Manifesti yeniden başlatmadan önce

1. Sunucudaki depo kopyasını (`~/tr7c-repo`) bu dalın HEAD'ine getirin (`git pull --ff-only`); `git_denetle`
   `tr6a_ffm.py`'nin HEAD ile aynı ve push edilmiş olmasını ister.
2. Yeni (boş) bir ham dizinle başlatın (varsayılan: zaman damgalı `on_…`). Yarım kalan
   `on_20261119T123202Z` (yalnız usp0005w12 ürünü) kayıt olarak kalabilir; `--ham-dizin` ile sürdürmek de §C12'ye
   uygundur (indirme kayıtları koddan bağımsızdır).
