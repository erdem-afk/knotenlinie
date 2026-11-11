# Kol AV — açık veri envanteri (zaman çözünürlüklü, Marmara/İstanbul) — 11 Kasım 2026

Tür: `veri`. Alt ajan kullanılmadı (bu oturumda Agent aracı yoktu); taramayı ve erişim sınamalarını tek başıma yaptım.
Her "sınandı" satırı 11 Kasım 2026'da bu kapsayıcıdan alınmış gerçek HTTP yanıtıdır. Türkiye dışı 2026 katalog verisi okunmadı.

## (a) Tarama özeti

- Arananlar: NGL, TUSAGA-Aktif, EPOS/EUREF; LiCSAR, EGMS, ASF (Sentinel-1, NISAR); KOERI, AFAD, GEOFON (GF, PZ), EIDA; IOC deniz seviyesi, TUDES, PSMSL; DataCite (GFZ, PANGAEA, SEANOE, INGV) ve Zenodo API'sinde "Marmara", 2023–2026.
- Köprü ölçüsü (kesişim k, Jaccard, pozitif kontrol): **yapılmadı**. Bu kol veri envanteridir; eş-atıf köprüsü ölçülmedi. "Neden yeni" sütunu yalnız Crossref/DataCite aramasına dayanır, sistematik öncül taraması değildir.
- Defter: `kayit.py ara` ile GNSS, InSAR, NGL, şablon, AFAD, KOERI, GONAF, deniz, basınç, DAS, tekrarlayan, yavaş arandı. İlgili kapanmışlar: Y-1, Y-3, DD-2, S-7, EL-1, EL-3, EL-9, KILIT-CMF, GERINIM-V14.

### Envanter (K = bizim kullandığımız; görüş: C=CMF, P=PIF, Ç=Çınarcık, İ=İzmit, G=Ganos)

| # | Veri seti | URL | Erişim (sınama) | Lisans | Zaman, örnekleme | Görüş | Boyut | Gecikme | K |
|---|---|---|---|---|---|---|---|---|---|
| 1 | NGL günlük GNSS konum (tenv3, IGS20) | geodesy.unr.edu/gps_timeseries/IGS20/tenv3/IGS20/ISTA.tenv3 | Açık, 200; ISTA 1,9 MB indirildi | Açık, atıf (Blewitt 2018) | Günlük. 40–41,6°K, 26–31,2°D kutusunda 28 istasyon. Çoğu TUSAGA istasyonu 2009-01 → 2023-05/2024-01, ≈2500 çözüm (≈%48 doluluk) | Karadan; İ, G iyi; C, P, Ç yalnız uzak alan | ≈0,5 MB/istasyon | ISTA 2026-10-24, QIBP 2026-10-17, ORE1 2026-10-10 (≈2–4 hafta). **Diğer 25 istasyon 2024-01-30'da ya da daha önce bitiyor** | Hayır |
| 2 | TUSAGA-Aktif RINEX | tusaga-aktif.gov.tr | Kayıt + ücret (site metni: "bedeli karşılığında"); 200 | Ticari | 1 s / 30 s, 2009+ | 146 istasyon | – | Gerçek zamanlı | Hayır |
| 3 | EPOS GNSS ürün portalı | gnssproducts.epos.ubi.pt | Ana sayfa 200; denediğim istasyon API yolu 404. Türkiye istasyonu içeriği **doğrulanamadı** | CC-BY (portal) | Günlük | ? | – | ? | Hayır |
| 4 | EUREF EPN | epncb.oma.be | 200 | Açık | Günlük; Marmara'da ISTA, TUBI (TUBI NGL'de 2023-06'da bitiyor) | Uzak alan | – | Gün | Hayır |
| 5 | COMET LiCSAR interferogramları | gws-access.jasmin.ac.uk/public/nceo_geohazards/LiCSAR_products/ | Açık, 200. Çerçeve 036D_04976_131313: 1725 interferogram, 2015-03-13 → 2025-10-28 | Açık, atıf | 6–12 gün | Kara: İ, G; deniz yok | GeoTIFF, çerçeve başına onlarca GB | Bu çerçevede ≈1 yıl geride | Evet |
| 6 | LiCSBAS zaman serisi | (yazılım; hazır ürün yok) | Kendi koşumuz gerekir; hazır tektonik zaman serisi ürünü bulamadım | GPL | – | Kara | – | – | Hayır |
| 7 | EGMS | egms.land.copernicus.eu | 200. Sayfa "Copernicus participating countries" diyor; Türkiye'nin kapsam dışında olduğunu biliyorum ama harita üzerinden **doğrulayamadım** | – | – | – | – | – | Hayır |
| 8 | ASF Sentinel-1 SLC (HyP3 ile kendi işleme) | api.daac.asf.alaska.edu/services/search/param | Arama açık, 200: 28,9°D 40,8°K noktasında 1761 SLC. İndirme Earthdata kaydı ister | Copernicus açık | 6–12 gün, 2014+ | Kara | SLC ≈4–8 GB | Gün | Hayır |
| 9 | **NISAR** (L-bant) | aynı API, `dataset=NISAR` | Arama açık, 200. Aynı noktada 15 GUNW (2026-08-15 → 2026-10-09), 17 RSLC, 17 GSLC (→ 2026-10-26); iz 28, 36, 137; artan + azalan | NASA açık (Earthdata kaydı) | 12 gün | Kara: İ, G; bitki örtüsünde S1'den iyi | GUNW ≈2,3 GB; RSLC ≈14 GB | ≈2–4 hafta | Hayır |
| 10 | KOERI katalog (zeqdb) | koeri.boun.edu.tr/sismo/zeqdb/ | Açık, form sorgusu 200. 1995 Marmara kutusu: 868 olay, mod M 2,7 (Mc ≈ 2,9 kaba). Sunucu yavaş: 2005/2015/2024 sorguları yarım kesildi | Atıf (KO) | 1900+; olay | Hepsi | KB–MB | Dakika (son24saat.xml 200) | Kısmen (ISC üzerinden) |
| 11 | KOERI FDSN event | eida.koeri.boun.edu.tr/fdsnws/event/1/ | **404, servis yok** | – | – | – | – | – | – |
| 12 | AFAD olay API | deprem.afad.gov.tr/apiv2/event/filter | 200 ama **yalnız son ≈12 gün döndü** (31 Eki 2026 öncesi boş; 1990, 2005, 2015, 2024, 2025 sorguları `[]`). Son 10 günde Marmara kutusu 32 olay, M 0,9–3,2. Tarihsel katalog için web arayüzü (event-catalog, 200) ya da TDVMS (kayıt) | Atıf (TU) | Arayüzde 1900+ | Hepsi | – | Dakika | Hayır |
| 13 | GFZ homojen Marmara kataloğu (Wollin/Becker) | doi 10.5880/gfz.4.2.2023.002 (2006–2020, 13 812 olay); 10.5880/gfz.itsj.2025.003 (2021–2023, 2 242 olay) | Açık, DOI 200. Dosya bağlantısı JS ile yükleniyor, **dosyayı indiremedim** | CC-BY 4.0 | 2006–2023, olay | Hepsi | MB | Yıllar (son: 2023) | Kısmen (GFZ tekrarlayan katalogları) |
| 14 | Fabisch 2026 dizi kataloğu (GONAF + derin öğrenme) | doi 10.5880/gfz.itsj.2026.001 | Açık (CC-BY 4.0); dosya indirilmedi | CC-BY 4.0 | 2016-06 → 2023-12; altı dizi (ML 4,0–5,7), ana şok çevresi pencereler | C, P, Ç | MB | – | Hayır |
| 15 | Núñez-Jara 2026: 2025 Mw 6,3 Orta Marmara gelişmiş katalog + 2019 Silivri | doi 10.5880/gfz.itsj.2026.002 | Açık (CC-BY 4.0); dosya indirilmedi | CC-BY 4.0 | 2019 ve 2025 dizileri | C | MB | – | Hayır |
| 16 | Konca vd. ML kataloğu 2020–2022 | doi 10.5281/zenodo.18734686 | Açık, 0,24 MB | (Zenodo) | 2020–2022 | Marmara Denizi | 0,24 MB | – | Hayır |
| 17 | MARSITE OBS mikrodepremleri (Tary vd.) | doi 10.5281/zenodo.23192641 | Açık | CC-BY 4.0 | 2013-10 → 2014-09 | Batı/orta Marmara | 109 MB + 2 xlsx | – | Hayır |
| 18 | 23 Nisan 2025 depremi veri seti (Ertuncay vd.) | doi 10.5281/zenodo.16421725 | Açık | CC-BY 4.0 | hypoDD artçı + yer hareketi | C | 45 MB | – | Hayır |
| 19 | 18–20 Ağustos 2026 Adalar dizisi (Eytemiz, Sözbilir) | doi 10.5281/zenodo.22150675 | **Kısıtlı** | – | 3 gün | P/Adalar | – | – | Hayır |
| 20 | KOERI sürekli dalga formu (KO) | eida.koeri.boun.edu.tr/fdsnws/dataselect/1/ | **Açık**, 200: 2026-11-01 20 s HHZ tüm ağ 208 KB indirildi. Kutuda KO 77, 6G 28, TL 16, IJ 8 istasyon. Kullanılabilirlik: ISK HHZ 2011-10 → bugün, SLVT/YLV HHZ 2013-11 → bugün, hepsi OPEN. Tek tek istekler 204 dönebiliyor (boşluk: YLV 21 963 parça) | Atıf (KO) | 100 Hz; 2010–11+ | Kıyı çevresi | Tahminim ≈10–20 MB/kanal/gün | ≈1 gün | Hayır |
| 21 | AFAD sürekli (TU), TDVMS | tdvms.afad.gov.tr | 200, kayıt ister; sınanmadı | – | – | – | – | – | Hayır |
| 22 | GONAF (GF) ve PIRES (PZ), GEOFON | geofon.gfz.de/fdsnws | Üstveri açık; dataselect **403**, `restrictedStatus="closed"` (2010 ve 2024 ikisi de) | Kapalı | GF 2012+, PZ 2006+ | P, Ç (en iyi) | – | – | Hayır |
| 23 | GONAF gerinim/basınç | aynı | Kanallar üstveride var (ERDK, UDEB: HS1–3, LS1–3, HYD, LDD), veri **kapalı** | Kapalı | – | Doğu Marmara | – | – | Hayır |
| 24 | EMSO/MAREGAMI taban basıncı + akıntı | doi 10.17882/78928 (SEANOE) | Açık | CC-BY 4.0 | Kampanya dönemi (sürekli değil) | Orta Marmara | – | Yok | Kısmen (SEANOE) |
| 25 | INGV SN-4 deniz tabanı (CTD, akıntı, bulanıklık) | 10.13127/md/mar-sn4-2013-* ve -2009-* | DataCite kaydı var; dosya sınanmadı | – | 2009–10, 2013–14 | İzmit Körfezi girişi | – | Yok | Hayır |
| 26 | DAS: Marmara Denizi (Ji Zhang) | 10.5281/zenodo.15791919 (+ "Continuous" 1–6) | Açık | CC0 | Altı olay + kısa sürekli parçalar | Denizaltı kablosu; yeri belgelenmemiş | 14,2 GB (tek zip) | Yok | Hayır |
| 27 | DAS: İstanbul karanlık fiber 2023 (Bowden vd.) | 10.5281/zenodo.18894807; 10.7914/kfkm-x182 | Açık | CC-BY 4.0 | 2023-02, olay dosyaları | Şehir içi | 201 MB/dosya | Yok | Hayır |
| 28 | IOC deniz seviyesi (Yalova, İstanbul, M. Ereğlisi, Erdek, Şile) | ioc-sealevelmonitoring.org/bgraph.php?code=yalo&output=tab | Açık, 200; Yalova 30 s radar, son veri 11 Kas 2026. 2012 için "NO DATA" (arşiv derinliği belirsiz) | Açık | 30 s | Kıyı | KB/gün | Dakika | Hayır |
| 29 | TUDES (HGM) | tudes.harita.gov.tr | Bağlantı kurulamadı (000) | – | – | – | – | – | Hayır |
| 30 | PSMSL | psmsl.org | 403 (bot engeli; zorlanmadı) | – | Aylık | – | – | – | Hayır |

Kullandıklarımız (ISC, EMSC, ComCat, GCMT, EPICA, AHEAD, EDSF13, SRCMOD, Elliott/Sun 2026, Kurt 2023, LiCSAR, SEANOE/PANGAEA akustik, GFZ tekrarlayan) yeniden sınanmadı.

Üç bulgu:
1. **NGL Marmara için gerçek zamanlı değil.** TUSAGA istasyonlarının NGL'ye akışı Ocak 2024'te kesilmiş; yalnız ISTA, QIBP, ORE1 sürüyor. NGL ile ileriye dönük izleme yapılamaz, yalnız 2009–2023 geriye dönük.
2. **En iyi veri kapalı.** PIF/Çınarcık'ı gören tek ağ (GONAF/PIRES, gerinim dahil) GEOFON'da kapalı. Açık olan türev kataloglar (Fabisch 2026, Becker 2023/2025).
3. **KOERI sürekli dalga formu açık ve günceldir** (2011+). Kendi katalog genişletmemiz için tek gerçek açık kaynak bu.

## (b) Aday tablosu

| | AV-1 | AV-2 | AV-3 |
|---|---|---|---|
| Ad | NGL günlük serilerinde yıl ölçekli hız değişimi var mı (Marmara) | Düşük Mc'li Marmara kataloğu ETAS'ı iyileştiriyor mu | NISAR + S1 ile İzmit/Ganos sünme hızında yıl ölçekli değişim |
| Soru | 2009–2023 arasında ortak mod çıkarıldıktan sonra istasyon çiftlerinin hızı sabit mi? | Mc ≈2,1'den ≈1,0–1,5'e inince M≥4 için günlük/aylık log skor artıyor mu? | Karadaki sünen kesimlerde hız değişimi ölçülebiliyor mu, M≥4 hızıyla ilişkili mi? |
| Neden yeni (en yakın işler) | Ergintav 2014 (10.1002/2014GL060985) hız alanı verir, zaman değişimi sınamaz. Bedford 2020 (10.1038/s41586-020-2212-1) ve Bletery 2023 (10.1126/science.adg2565) dalma-batma/küresel. Marmara günlük serilerinde ön kayıtlı geçici taraması bulamadım | Mancini 2022 (10.1029/2022JB025202) Kaliforniya/İtalya'da yararı sınırlı buldu. Becker 2023 (10.1029/2022gl101471) ve Fabisch 2026 (10.1029/2026jb034241) katalog üretir, tahmin puanlamaz. Marmara için log skorlu sınama bulamadım | Lazecký 2020 (10.3390/rs12152430), Morishita 2020 (10.3390/rs12030424) araç. NISAR Marmara verisi Ağustos 2026'da başladı; yayımlanmış iş olamaz |
| Zaman ekseni | Yıl; yalnız varlık sınaması, tahmin değil | Gün–ay; M≥4 (M6+ için N yok) | Yıl; M≥4 |
| H1 / H0 | H1: en az bir çiftte ≥2 mm/yıl kalıcı (≥1 yıl) hız değişimi. H0: sabit hız + renkli gürültü | H1: düşük Mc'li ETAS, standart ETAS'tan ≥0,1 nat/olay iyi. H0: fark yok | H1: hız değişimi > gürültü. H0: sabit |
| Rakip | Sabit hız + mevsimsel + renkli gürültü modeli | Aynı ETAS, Mc 2,5 (KOERI/Becker) | Sabit hız |
| Hedef küme, kaba N | ≈20 istasyon, ≈190 çift, 15 yıl | Marmara M≥4, 2012–2026: tahminim 30–60 (**sayılmadı**) | – |
| Güç | Ölçtüm: ISTA günlük artık saçılım D 2,6 mm, K 2,1 mm; yıllık ortalama artığın sd'si 1,4 mm. Tek istasyonda ≈2–3 mm/yıl altı görülmez. Karada beklenen geçici sinyal bunun altında olabilir; **güç zayıf** | N 30–60 ile 0,1 nat/olay farkı sınırda; önce güç hesabı | Bugün yok (veri 3 ay) |
| Sızıntı | Düşük (geriye dönük; kural önce dondurulur) | Orta: katalog üretimi hedef olayları görür; pencere ayrımı şart | Düşük |
| Veri | Açık (envanter 1), ≈15 MB | Aşama 0: envanter 13, 14, 16 (MB). Aşama 1: envanter 20; 30 istasyon × 3 kanal × 15 yıl ≈ TB ölçeği | Envanter 5, 8, 9 |
| Maliyet/süre | 0 €, 1–2 gün | Aşama 0: 0 €, 2–3 gün. Aşama 1: makine kiralamadan yapılamaz | 0 € şimdi; 2028'de yeniden bak |
| Tür | veri/istatistik | veri → istatistik | veri |
| Hüküm | **Öner (dar)**: ucuz, olumsuz sonuç da kayda değer. S-7'den farkı: çarpan sınamıyor, yalnız sinyalin varlığını ölçüyor | **Öner, yalnız aşama 0**: hazır kataloglarla 2020–2023'te Mc etkisini ölç; yarar yoksa aşama 1 açılmaz | **Bekle**: ≥1,5 yıl NISAR birikene dek; kural şimdi dondurulabilir |

## (c) Elenenler

- **AV-4 Deniz seviyesi/atmosfer yükü modülasyonu** (IOC + ERA5). Gelgit ≈0 sonucu defterde; Marmara'da mevsimsel yük kPa düzeyinde, IOC arşivi 2012'de boş. Elendi.
- **AV-5 GONAF gerinim ölçerle yavaş kayma izleme** (Martínez-Garzón 2019, 10.1016/j.epsl.2019.01.001). Veri kapalı (403). Elendi; açılma şartı GFZ'nin veriyi açması.
- OBS (envanter 17), DAS (26, 27), EMSO basınç (24): kampanya verisi, yıl ölçekli süreklilik yok. EL-9 ile aynı sonuç; aday yazılmadı.
- AFAD API ile 1990+ katalog: API tarihsel veri döndürmedi; KOERI zeqdb + GFZ homojen katalog yeterli.

## (d) Dürüst sınır

- Hiçbir aday M6+/M7+ zamanını daraltmaz; üçü de M≥4 ya da yalnız sinyal varlığı üzerinedir. Marmara'da aletsel M6+ sayısı güç hesabına yetmez.
- AFAD ve KOERI için Mc'yi ölçmedim (yalnız KOERI 1995 için kaba mod). "Mc ≈2,1" Becker/Wollin kataloğu için hatırladığım değerdir, doğrulanmadı.
- GFZ katalog dosyalarını indiremedim (sayfa JS ile yükleniyor); "açık" hükmü lisans ve DOI çözümüne dayanır.
- EGMS'nin Türkiye'yi kapsamadığı ve LiCSBAS için hazır ürün olmadığı kendi bilgimdir, sınanmadı.
- AV-2'deki olay sayısı ve dalga formu hacmi tahmindir.
- Okunmayan makaleler: Fabisch 2026, Mancini 2022, Bedford 2020, Bletery 2023, Becker 2023 yalnız başlık/özet düzeyinde (Crossref kaydı) kullanıldı.
