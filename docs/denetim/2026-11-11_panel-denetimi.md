# Knotenlinie Paneli denetimi (11 Kasım 2026)

İstek (Erdem, 11 Kasım 17:07): panel kendi içinde ve dışarıya karşı sınansın. Paneli yazmamış bağımsız inceleyiciler kullanıldı. Mutlak İstanbul olasılığı bu belgeye yazılmadı.

Kaynaklar:
- İç sınama: `2026-11-11_panel-ic-denetim.md` (bu klasör).
- Künye sınaması: `2026-11-11_panel-literatur-denetimi.md` (bu klasör).
- Sunucu sınaması (salt okuma): magma-corbasi `docs/denetim/2026-11-11_panel-dis-denetim.md`, commit aa98f9f3, ek fc4f7969.
- knotenlinie dalları: bu oturumda `git cat-file` ve `sha256sum` ile.

## Doğrulananlar

- 137 kısa hash'in 125'i magma-corbasi main'de commit; kalan 12'si DONDUR sha önekleri, 9'u depodaki dosyalarla eşleşti. 3'ü (382a3378, b1b25f3a, d5a5c78d) Ekim kayıtlarında geçiyor, dosyası depoda yok.
- Paneldeki 20 knotenlinie commit'i adı geçen dallarda; adı geçen belge yollarının hepsi var. DONDUR-s4-s7 sha 91506751 tutuyor.
- Zenodo 10.5281/zenodo.24041238 ve 24091998: 7 dosyanın 7'si depoyla md5 aynı. Paneldeki 7 Zenodo kaydı yayımlı.
- OTS Bitcoin onaylı (yerel .ots): mühür, Türkiye ince sınav, RAPOR-5, Marmara v1, v1.2, v1.3, v1.3b, v1.4, nihai, v1.10k, CRS.
- 2026 Türkiye penceresi 9 Kasım 20:29 UTC'de açıldı (ACILIS.json, a325b27f, Erdem'in sözüyle). Canlı hat 2026 verisini puanlamıyor.
- Canlı ETAS (06:15), CRS (06:45), Bayes ETAS (08:15) zamanlayıcıları kurulu, 11 Kasım'da çıkış 0. Canlı zamanlayıcı 9 Kasım 20:30 UTC'de kuruldu, ilk günlük koşu 10 Kasım 06:15.
- `kayit/`: 79 aday, 290 kaynak (panel ile aynı).
- ≈45 atfın hepsi gerçek bir makaleye karşılık geliyor; rapor sekmesindeki 14 DOI çözülüyor.

## Panelde düzeltilenler (önem sırasıyla)

1. Sekme gezintisi yoktu: ana sayfadan Durum raporu, Kıyas tablosu, Kurulum'a ulaşılamıyordu. Dört sayfaya ortak şerit eklendi.
2. Site dışı yedek beş yerde "ertelendi/duruyor": gerçekte restic + Storage Box kurulu, 11 Kasım 03:34 koşusu başarısız (sftp "Failure", restic deposu oluşturulamadı), snapshot 0.
3. Durum raporu v2.1'i üç yerde "koşuyor" gösteriyordu; 10 Kasım'da donduruldu.
4. "İstanbul aralığının %52'si dal içi" v1.3'e ait; v1.3b'de uzamsal %45, dal içi %32.
5. Ana hat kutusu: "nihai 31 Aralık", "1–20 Aralık doğrulama", "simülatör 2027'ye" eskimişti.
6. FA-1 / TK-1 "seçim Erdem'in" → Erdem seçti (11 Kasım 16:15), koşuyor.
7. Defter sürüm sayısı 8 / 10 / 4 → o günkü sayı olarak işaretlendi; sunucu defterinde 11 Kasım'da 19 sürüm.
8. Harcama ≈0,62 € / ≈1 € / ≈5,4 € → `hesap/hetzner.csv` Kasım satırları 28,61 € (sabit giderler hariç).
9. Canlı hat "8 Kasım'dan beri" → 9 Kasım akşamı kuruldu, 10 Kasım'dan beri günlük.
10. "55 gün kaldı" → 1 Ocak 2027.
11. Kıyas orman grafiği TripleS / MPS04 için sızıntılı eski değerleri çiziyordu (+0,444 / +0,613) → sızıntısız +0,28 ± 0,41 / +0,45 ± 0,53.
12. Disk 40 GB / 15 GB boş → 120 GB / ≈38 GB boş; "bu makinede run çıktısı yok" düzeltildi.
13. Kurulum: OpenAlex izni, OPENALEX_API_KEY ve RESTIC_PASSWORD adları, rc-keepalive.
14. Menü ve sıra bölümleri "7 Kasım planı" diye etiketlendi; hk1 ve Türkiye sınavı bitti olarak işlendi.
15. Künye etiketleri: Stockman EarthquakeNPP 2024 (arXiv 2410.08226), Rhoades 2018 = NZ test merkezi özeti; Biondini 2023'e ana şok nüansı eklendi.
16. Yazım: KABÜL, RAPOR-5 tekrarı, "Adalar adaları", "M/12 kuralı", kopuk cümle, "'Sonraki adımlar' sekmesi".

## Yoruma açık (işaretlendi, düzeltilmedi)

- 1999 kayma modeli sayısı: kural 9, uygulama 8 (İzmit 6, Düzce 2) görünüyor.
- "30 yıllık mutlak olasılık literatürde ≈%20–65": kural sınırında. Üst uç Parsons 2000'den (İstanbul'da güçlü sarsıntı, M7 olayı değil), Parsons 2000 listede yok; Erdik 2004 kaynakçada yok (`Erdik_2003` başka makale; doğrusu 10.1016/j.soildyn.2004.04.003).
- Bölge M7 oranı ≈0,021/yıl mutlak bir oran.
- Meghraoui 2012'nin Ganos için 1000 öncesi olay verdiği özetten doğrulanamadı.
- Sun 2026 bilgi tarihi 2026-04-10; Crossref kabul 04-02, çevrim içi 04-15.
- Çağatay 2025 en riskli kesim olarak Orta Yüksek'i gösteriyor.
- Kurt 2023 "44 ek istasyon" özetten doğrulanamadı; Lange 2019 ±1,25'in 1σ olup olmadığı net değil.
- Durum raporu ve Kıyas defteri (752 satır, son 9 Kasım) 10–11 Kasım sonuçlarını içermiyor.
- `yol.html` ana sayfanın 7 Kasım kopyası, bağlantısız.

## Kayıtlarda açık kalanlar (panel hatası değil)

- Yerel .ots yalnız pending: rlmbg-rev31, etasbayes, v1.5–v2.4abc Marmara sürümleri, derive deniz a1/a2/a5, mikrosismisite; knotenlinie dallarındaki DONDUR-s4-s7, derive-dogrultu, a3.
- `hesap/hetzner.csv` sunucuyu cpx02 / 80 GB yazıyor (gerçek cpx22 / 120 GB); Storage Box notu eski.
- "v2.4" adı hem Y1b sürümü (dondurma-v24, 59bd40ba) hem ABC sürümü (v2.4abc) için kullanılmış.
- `kayit/kaynakca.bib`: ≈20 eksik kaynak (Kagan–Jackson 1995, Meghraoui 2012, Çağatay 2025, Chartier 2021 vb.) ve 7 yinelenen anahtar (DeVries_2016, Field_2015, Field_2017, Werner_2011, Zechar_2010, Uchida_2019, Schorlemmer_2005).
- Site dışı yedek çalışmıyor: snapshot 0.
