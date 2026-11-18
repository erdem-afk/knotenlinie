# TR-7c koşu kodu: kod incelemesi 2 (yalnız b0f70642… → c86d8b9b… farkı)

Tarih: 18 Kasım 2026. İncelenen: `git diff 7dd7c68 cd6b6bb -- kayit/turetme/tr7c/tr7c_kosu.py` (c86d8b9b17ae…), yeni
`tr7c_prova.py` (+ json), `TR-7c_KOSU-DONDURMA-EKI.md` (taslak), `TR-7c_KODLAYICI-OKUMALARI.md` §11. Dayanılan:
`tr7/tr7_kosu.py` (`onkosul`, `baslat`, `kos`, `durdu`, `git_dogrula`; değiştirilmedi).

Kısıtlar: ağ isteği yapılmadı; gerçek veri açılmadı; `/mnt/project-files` altında hiçbir dosya açılmadı; karar metnine,
inceleme dosyalarına ve TR-7/TR-7b dosyalarına dokunulmadı. Koda dokunulmadı: `tr7c_kosu.py` c86d8b9b… olarak kalır.

Sınamalarım: `kayit/turetme/tr7c/kodinc/tr7c_kodinc2.py` (+ `tr7c_kodinc2.json`, mutasyon parçaları
`tr7c_kodinc2.json.mut.jsonl`).
- Süreçte denetim kancası vardır. Her soket olayı, `/mnt/project-files` altında her açma, `tr7c/kosu/`'ya her yazma ve
  dizin kurma, her alt süreç reddedilir.
- Hiçbir soket açılmaz. Düğmenin kancası (`_prova_kancasi`) doğrudan çağrılarak sınanır; sahte sunucu kurulmaz.
- Aşama gövdesi (`_asama_govde`) saplanır. Saat denetlenir (her çağrıda 1 sn ilerler).
- Dondurulmuş kapı ya ön kaydın geçici bir kopyasıyla ya da `kosu_dondurulmus_mu` saplanarak kurulur.

## Hüküm

**DONDURULABİLİR; koda düzeltme gerekmez.** Dondurma ekine §E'deki altı cümle aynen girmelidir. E-4 ve E-5, ilk
incelemenin §I.1 ve §I.5 cümlelerinin yerini alır: ikisi de artık doğru değil (§D). §E.3 (kiralık makine) için
koordinatörün bir kalıntı riski açıkça kabul etmesi gerekir.

## A. Fark algılama hesabına dokunuyor mu? (1)

**Dokunmuyor.** Farkın hunk'ları şunlardır:
- belge başı ve `import contextlib`;
- `gercek_kapi`'nın prova kolu ve KURU PROVA bloğu;
- aşama protokolü bloğu;
- `modulasyon_turu` çıktısındaki `konum` alanı (yalnız çıktı);
- `k1c_kos`: `durum_yaz` bayrağı ve dizin şartının `gercek_yol_mu` yerine `_cikti_mi` olması;
- `GercekOrtam`, `asama_kos`/`_asama_govde`;
- manifest'te `katalog/` dizini (P-1) ve `taban` geçişi;
- lp `taban` geçişi ve `main`.

Algılama, K5 (`ayikla_k5`, `k5_ist`), MDA, `modulasyon_kume`, üreteç sırası, `k1c_hesap`, D30M3, `k1c_dal`, etiketler
ve E-1/E-2 değişmedi.

`k1c_kos`'taki şart gerçek kipte daha sıkıdır. Önce `kosu/` altı ya da bir gerçek kök de kabul ediliyordu; şimdi dizin
tam olarak `kosu/` olmalıdır.

Algılama aşamasının sürdürülmesi belirlenimcidir. MDA üretecinin durumu her pencereden sonra jsonl'e yazılır ve
oradan yüklenir. Modülasyon üreteci bütün algılama satırlarından sonra bir kez kurulur. Hüküm dosyası `x` kipiyle tek
kez yazılır.

Kodlayıcının "KD, TR-7b §11.2, m_f ve duman yeniden koşulmadı" gerekçesi bu yüzden doğrudur.

## B. Kuru prova düğmesi (2)

Sınama (D1–D8, 10/10):
- **D1.** Dondurulmuş (gerçekten açık kapılı) geçici ön kayıtla `prova_ac` reddedilir. Bugünkü metinle açılır.
- **D2, D2b.** Prova açıkken koşu dondurulursa `gercek_kapi` bir sonraki çağrıda reddeder. `_PROVA` elle kurulsa da
  (`prova_ac` atlanarak) sonuç aynıdır. Bunun nedeni şudur: prova kolu her çağrıda `prova_denetle` ile kapıyı yeniden
  okur. **Düğme koşu dondurmasından sonra hiçbir yoldan çalışmaz; dondurma kapısını atlatmak için kullanılamaz.**
- **D3.** Taban URL denetimi. 11 kötü biçim, `servis` ve `katalog` alanlarının ikisinde de reddedilir:
  - `https://127.0.0.1:…`;
  - `localhost`, `127.0.0.2`, `[::1]`, `0.0.0.0`;
  - `2130706433` (127.0.0.1'in onluk yazımı);
  - portsuz `127.0.0.1`;
  - kullanıcı bilgisiyle gizlenmiş dış ad (`…@service.ncedc.org`);
  - parça işaretiyle gizlenmiş dış ad (`…#@127.0.0.1`);
  - portlu dış ad ve `ftp`.

  Eksik ya da fazla anahtar da reddedilir.
- **D4.** Prova dizini şunlardan biri olamaz:
  - depo içi bir dizin ya da `kosu/`;
  - bir gerçek kök (ZARF_KOK ya da Marmara kökü);
  - `/mnt` ya da altında bir dizin;
  - `/mnt/project-files`'a giden bir sembolik bağ ya da onun altı.
- **D5.** Prova kancası yalnız izinli (127.0.0.1, port) çiftine bağlantı ve ad çözümü verir. Şunlar reddedilir: aynı
  adresin başka portu (vekil), dış IP, Unix soketi, dış adın çözümü, `gethostbyname`, `sendto`. Prova kapalıyken kanca
  etkisizdir.
- **D6.** Provada `GercekOrtam`'ın zarf, ham, katalog ve çıktı yolları prova dizinlerindedir.
  `TR7_HAM_DIZIN=/mnt/project-files/…` olsa da öyledir. Servis ve katalog prova tabanıdır; git doğrulaması kapalıdır.
- **D6b.** Prova dışında `GercekOrtam` kapı kapalıyken kurulamaz. Dondurulmuş kipte ZARF_KOK, `kosu/`, git doğrulaması
  AÇIK ve `taban None` (gerçek uçlar) ile kurulur.
- **D7.** Provada `k1c_kos(gercek=True)` şu dizinlerin hiçbiriyle koşmaz: `kosu/`, `kosu/` altı, ZARF_KOK, prova dışı
  bir dizin.
- **D8.** Provada manifest'in ilk ComCat isteği `http://127.0.0.1:9/comcat?…` adresine gider ve `katalog/` dizini
  kurulur (taban ve P-1).

**Gerçek sunucuya ya da gerçek köklere giden bir kod yolu bulmadım.** Provada bütün URL'ler `go.servis`/`go.katalog`
tabanından kurulur. TR-7c'nin dört kendi çağrısı ve TR-7 motorunun çağrıları `taban=o.servis/o.katalog` taşır. Bütün
yollar `_cikti()` ve `self.zarf` üzerindendir.

Kalan risk koddan değil, kasıttan gelir. İki durum vardır:
- 127.0.0.1'de gerçek bir FDSN hizmetini aktaran ayrı bir süreç;
- prova dizinine elle kopyalanmış gerçek zarf ya da miniSEED.

Kod bunları ayırt edemez. Koşu dondurmasından önce kör olayların verisi indirilmemiş olduğundan ikinci durumun
malzemesi yoktur. E-2 cümlesi bu riski işletim kuralıyla kapatır.

## C. Aşama protokolü ve durma kaydı (3)

Sınama (P1–P12, 20/20):
- **Sıra.** Sıra dışı `baslat` reddedilir, bilinmeyen aşama da. `kos` önceki aşama tamamlanmamışsa reddeder.
- **Başlatma ve tek koşu.** İkinci `baslat` ('başladı' iken) reddedilir. Tamamlanmış aşama yeniden başlatılamaz
  (`--surdur` ile de). `baslat` kaydı `tr7c_kosu.py`'nin sha256'sını taşır ve sonradan kod değişirse `kos` reddeder.
- **Hata ve durma kaydı.**
  - Gövde hatası durum 'hata' ve `kod` türünde bir durma kaydı (ileti ve saat) yazar.
  - 'hata'daki aşama `baslat` olmadan koşulamaz.
  - Algılama aşamasına `--surdur` olmadan yeniden girilemez.
  - Yalnız `kod` durma kaydıyla `--surdur` reddedilir; boş durma nedeni de reddedilir.
  - Yeni bir kesintiden sonra eski `elle` kayıt yetmez.
- **Durum dosyası.** Aşama kayıtları yalnız durum, zaman ve sha256 taşır; durma kayıtları yalnız aşama, tür, neden ve
  zaman.

**TR-7 ile tutarlılık.**
- `onkosul`'un sıra, tek koşu ve algılama aşamasına `--surdur` kuralları TR-7 ile aynıdır.
- TR-7c iki yerde daha sıkıdır:
  - sürdürme, aşamanın son durumundan SONRA yazılmış bir `elle` kayıt ister (TR-7 o aşama için herhangi bir durmayı
    yeterli sayar);
  - `kos` her `Exception`'ı yakalayıp kayda geçirir (TR-7 yalnız dört türü yakalar).
- TR-7'den eksik olanlar:
  - 'sürdürülüyor' durumu ve önceki aşama kaydının `onceki` alanında saklanması yoktur (`durmalar` listesi geçmişi
    taşır);
  - `kos`, `git_dogrula` sonucunu (head ve uzak commit) durum dosyasına yazmaz.

  İkisi de dal ya da hesap değiştirmez. Kod düzeltmesi önermiyorum.

**SIGKILL ('başladı'da kalan aşama).** Sınamamda P9 kodun bugünkü davranışını bilgi olarak kaydeder: yeniden `kos`
elle kayıt istemeden sürer. TR-7 de böyledir. Değerlendirmem:
- **Körlük sorunu değil.** Kod sha256'sı kapıyla ve `kos`'un denetimiyle kilitlidir. Sürdürme belirlenimcidir (MDA
  üreteci durumu jsonl'dedir). Hüküm `x` ile bir kez yazılır. Kesintisiz koşu ile sürdürülmüş koşu aynı hükmü verir.
  Kesintide görülebilecek kısmi jsonl satırları, kayda geçmiş bir durmada da görülür.
- **Tek koşu sorunu değil.** Sürdürme zaten izinlidir.
- **Bir kayıt (izlenebilirlik) açığıdır.** §10 madde 6'nın "durma nedeni kayda geçer" kuralını kod zorlamaz. İşletim
  kuralı (E-1) yeterlidir, şu şartla: algılama aşamaları hiçbir otomatik bekçi ya da yeniden başlatıcı altında
  koşulmaz.

Saniye çözünürlüğü yüzünden bir kenar durum vardır. `durdu`, `baslat --surdur` ve yeni bir çöküş aynı saniyede olursa
eski `elle` kayıt yeterli sayılır (zaman karşılaştırması `>=`). Arada commit ve push olduğu için gerçek koşuda bu
olmaz. Önemsiz buluyorum.

## D. Dondurma eki taslağı (4)

- **Aynen mi?** Evet. KOD-INCELEME §D'nin 10 cümlesi ve §F'nin cümlesi ekin §1 ve §3'üyle karakteri karakterine aynı.
  §I'nın 5 cümlesi ekin §2'siyle aynı. Programla karşılaştırıldı.
- **sha tablosu.** §5'in 26 satırının hepsi diskle aynı. Koda gömülü değerler de diskle aynı: D-2, girdiler, TR-7
  motoru, §0–§6 gövdesi `8761573150be…`.
- **"Durum:" satırı.**
  - Ekin §8'deki biçimini ön kaydın geçici bir kopyasının 3. satırına yazdım; `kosu_dondurulmus_mu` → (True,
    'tamam'). Bu satırdan önce yeni bir "Durum:" satırı eklemek de kapıyı açar.
  - İki biçim kapıyı açmaz:
    - satır `**Durum:**` gibi Markdown'la ya da girintiyle başlarsa;
    - `KOŞU DONDURULDU` dosyadaki ilk "Durum:" satırında değil de sonraki bir satırdaysa.

  Kapı yalnız satır başında `Durum:` ile başlayan ilk satıra bakar. E-6 bunu yazar.
- **Ekin başı yanlış.** "Bu ek ayrı dosyada kaldıkça kapı kapalı kalır" cümlesi doğru değil. İki sha256 "Durum:"
  satırındaysa ek ayrı dosyada kalabilir; kapı açılır (yukarıda sınandı). Ama o zaman ekin kendisi hiçbir sha256'yla
  bağlanmamış olur, oysa bağlayıcı cümleleri (KMS-1…10) taşıyor. E-6, ekin sha256'sının da Durum satırına yazılmasını
  ister.
- **§I.1 artık doğru değil.** Durum dosyası "yalnız 'başladı / tamamlandı / hata', zaman ve dosya sha256'larını"
  taşımıyor; ayrıca `durmalar` listesini taşıyor. E-4 yerine geçer.
- **§I.5 ve ekin §7'si eksik.** "Plan 7300'ü aşmaz" cümlesi yanlış. İlk incelemenin §G'sindeki bu kestirim benimdi.
  - NCEDC'nin 204 döndürdüğü her istasyon EarthScope'tan yeniden istenir (ekin §7'si bunu kendisi yazıyor).
  - Hiçbir istasyon örtüden geçemezse bir pencerede bütün liste istasyonları iki kez istenir.
  - En kötü durum ≈ 2 × (1882 + 5440) ≈ 14 650 dataselect + ≈ 2014 StationXML + ≈ 335 ComCat + E-1 ≈ 17 000 istek.
  - Provada S1 tam bu durumu yaşadı: 16 911 istek, 14 562'si dataselect. Sahte sunucu çoğu istasyona 204 döndürdü.
  - Süre ≈ 9–14 sa (2–3 sn/istek). 2026 ve sonrasına ya da kör pencere dışına istek yine yoktur. E-5 yerine geçer.
- **Ö-j.** Biçim TR-7 §11 biçimindedir. Olasılıklar 1,00 eder; (b)'nin alt satırları 0,10 + 0,20 = 0,30. Zamanlama
  beyanı (duman ve m_f'ten sonra, kör veriden önce) dürüsttür.

  Eksik bir şart var: Ö-j'nin yazarın onayladığı son biçimi, dondurma satırını taşıyan commit'ten ÖNCE ya da aynı
  commit'te ön kayda (ya da sha256'sı Durum satırına giren eke) girmelidir. Bu şart E-6'dadır.

## E. Koşu dondurması ekine aynen girecek cümleler

**E-1 (SIGKILL; ekin §7 son maddesinin ve §9.3'ün yerine).**
> "Bir aşama süreç öldürülerek ya da makine yeniden başlayarak kesilirse (durum dosyasında aşama 'başladı'da kalır,
> kod durma kaydı yazılmaz) aynı aşama yeniden `kos` edilmeden önce `durdu <aşama> --neden "<kesintinin saati ve
> nedeni>"` yazılır, durum dosyası commit + push edilir ve aşama `baslat <aşama> --surdur` ile yeniden başlatılır. Kod
> bu sırayı bu sürümde zorlamadığı için K1c-negatif ve K1c-algılama hiçbir otomatik bekçi ya da yeniden başlatıcı
> altında koşulmaz. Bu sıranın dışındaki her yeniden `kos` sapma olarak olay kaydına ve sonuç raporuna yazılır; hüküm
> dosyası değişmez (jsonl'den sürdürme belirlenimcidir)."

**E-2 (kuru prova).**
> "Kuru prova (`prova_ac`) yalnız koşu dondurmasından önce ve yalnız yapay veri sunan bir sahte sunucuyla
> (`tr7c_prova.py`) koşulur. Prova sunucusu gerçek bir FDSN ya da katalog hizmetini aktarmaz, önbelleğe alınmış gerçek
> veri sunmaz; prova dizinlerine gerçek zarf ya da miniSEED konmaz. Koşu dondurmasından sonra düğme kodla kapalıdır
> (`prova_denetle` her çağrıda kapıyı yeniden okur ve dondurulmuş metinle reddeder); dondurmadan sonra hiçbir prova
> koşulmaz."

**E-3 (koşu yeri: kiralık makine, çıplak depo; (5)).**
> "Koşu kiralık makinede yapılır. Orada `git_dogrula`'nın uzak dalı makinedeki çıplak depodur; bu yalnız 'durum
> dosyası commit edildi' denetimidir, dış zaman damgası değildir. §10 madde 6'nın dış zaman damgası şöyle sağlanır: her
> aşamanın `baslat` commit'i, o aşamanın `kos` komutundan ÖNCE git paketiyle bulut oturumuna alınır ve aynı commit
> kimliğiyle GitHub'daki koşu dalına push edilir; bulut oturumu push'u `git ls-remote` ile doğrular, commit kimliğini
> ve push'un UTC saatini koşu defterine yazar; `kos` ancak bu doğrulamadan sonra başlatılır. Aşamanın çıktıları ve
> 'tamamlandı' ya da 'hata' durum dosyası da aynı yolla, bir sonraki `baslat`'tan önce GitHub'a push edilir. `kos`'un
> GitHub push'undan önce başladığı ya da GitHub'da 'başladı' kaydı olmayan bir aşamanın çıktısının bulunduğu her durum
> sapmadır; olay kaydına ve sonuç raporuna yazılır."

Değerlendirme (eke girmez):
- **Neyi karşılar.** Bu sıra §10 madde 6'nın amacını, kurallara uyan her aşama için karşılar: aşamanın başladığı,
  makinenin denetimi dışında bir yerde (GitHub ve bulut oturumunun defteri) koşudan önce zaman damgalıdır.
- **Neyi karşılamaz.** GitHub uzak dalı varken `git_dogrula`, push edilmemiş bir 'başladı' kaydıyla `kos`'u teknik
  olarak engellerdi. Çıplak depoyla bu engel kalkar. Makinede, `baslat` hiç push edilmeden yapılıp silinmiş gizli bir
  koşu kodla tespit edilemez; yalnız işletim kuralı ve yukarıdaki sapma kaydı ona karşıdır.
- **Kabul.** Bu kalıntı risk tasarım düzeyindedir; koordinatörün açıkça kabul etmesi gerekir. Kodla küçültülebilir:
  `kos` başında bulut oturumunun verdiği commit kimliğini argüman olarak isteyip HEAD ile karşılaştırmak. Bu sha256'yı
  değiştirir; bu incelemede yapmadım.

**E-4 (ilk incelemenin §I.1'inin yerine).**
> "Durum dosyası `kayit/turetme/tr7c/kosu/TR7C_KOSU_DURUM.json`'dur; §10 madde 6'daki
> `kayit/turetme/tr7c/TR7C_KOSU_DURUM.json` bu yol olarak okunur. Aşama kayıtları yalnız 'başladı / tamamlandı /
> hata', zaman ve dosya sha256'larını taşır; `durmalar` listesi her durma için yalnız aşamayı, türü ('kod' ya da
> 'elle'), ileti metnini ve saati taşır. Durum dosyasına hiçbir sonuç sayısı yazılmaz; elle yazılan durma nedeni de
> sonuç sayısı içermez."

**E-5 (ilk incelemenin §I.5'inin ve ekin §7 "7300 … aşmaz" cümlesinin yerine).**
> "İndirme planı TR-7 motorunun 12-istasyon kuralıyladır: bir pencerede istasyonlar iz sırasıyla istenir, 12 istasyon
> örtüden geçince durulur; NCEDC'nin 204 döndürdüğü istasyon EarthScope'tan yeniden istenir. İstek sayısı istasyonların
> çoğunda veri varsa ≈ 2000–2800 dataselect, hiçbirinde yoksa en çok ≈ 14 650 dataselect isteğidir; bunlara ≈ 2014
> StationXML, ≈ 335 ComCat ve E-1 için ≈ 40–120 istek eklenir (en kötü durumda toplam ≈ 17 000; kuru provada 16 911).
> Koşu kodu kör olaylarda istasyon başına [R başı − 600 sn, W sonu + 600 sn] dışında ve 2026 ve sonrasında hiçbir
> dalga formu istemez."

**E-6 (dondurma satırı).**
> "Dondurma satırı ön kayıt dosyasında satır başında, Markdown imi ve girinti olmadan 'Durum:' ile başlayan İLK
> satırdır ve 'KOŞU DONDURULDU' dizesini, `tr7c_kosu.py` (c86d8b9b17ae17e8fa67a12ff945a90df791dc0bfd6b548e1f2d3cbaac20a5b2)
> ve `tr7c_mde_ek.py` (4876dcbee8ce455c221efa4782e4af0047e5ade2f7b84eb985f9eb127873e910) sha256'larını tam olarak ve,
> ek ayrı dosyada kalıyorsa, ekin (`TR-7c_KOSU-DONDURMA-EKI.md`, yazarın onayladığı Ö-j dahil son biçimi) sha256'sını
> taşır. Ek ve Ö-j, dondurma satırını taşıyan commit'ten önce ya da aynı commit'te yazılır; o commit'ten sonra
> değişmez."

## F. Mutasyonlar (26; 25 yakalandı, 1 eşdeğer)

Kodlayıcının 45 mutasyonundan farklıdır. Hepsi yalnız fark üzerindedir. İki parçada koşuldu; ara sonuç her
mutasyondan sonra jsonl'e yazıldı.

Kapsanan konular:
- **Düğme:** prova kolunun yeniden denetlememesi; dondurmaya bakmaması; /mnt denetimi; provada gerçek zarf kökü; ham
  dizinin `TR7_HAM_DIZIN`'i dinlemesi; `_cikti`'nın `kosu/` olması; `k1c_kos` dizin şartının gevşemesi; prova dışında
  git doğrulamasının kapanması.
- **Taban:** host, port, https ve localhost denetimleri; manifest isteğinin `taban` almaması.
- **Kanca:** 127.0.0.1'in her portu; ad çözümünün serbest olması.
- **Aşama sırası:** `baslat` ve `kos`'ta.
- **Tek koşu.**
- **Durma kaydı:** `--surdur`'suz giriş; kod durmasının yetmesi; eski elle kaydın yetmesi; hata yolunda kaydın
  yazılmaması; boş neden.
- **`kos`'un kod değişikliğini reddetmemesi.**
- **`baslat`'ın 'başladı'yı yeniden yazması.**

Yakalanmayan tek mutasyon "`kos`, 'hata'daki aşamayı `baslat`'sız koşar"dır. Bu mutasyon eşdeğerdir. 'hata' kaydı
sha256 taşımaz, bu yüzden `kos`'un kod denetimi aynı yerde reddeder (P6b ve P7d yine geçer). Davranış değişmez; kod
düzeltmesi gerekmez.

Engellenen girişler: iki mutant (`_cikti` → `kosu/` ve gevşek `k1c_kos` dizin şartı) gerçek `kosu/` dizinini kurmaya
çalıştı. Denetim kancası bunu engelledi; dizin yoktur. Ana koşuda engellenen giriş 0.

## G. sha256'lar

| Dosya | sha256 |
|---|---|
| `kayit/turetme/tr7c/tr7c_kosu.py` (değişmedi; incelenen) | c86d8b9b17ae17e8fa67a12ff945a90df791dc0bfd6b548e1f2d3cbaac20a5b2 |
| `kayit/turetme/tr7c/tr7c_mde_ek.py` (değişmedi) | 4876dcbee8ce455c221efa4782e4af0047e5ade2f7b84eb985f9eb127873e910 |
| `kayit/turetme/tr7c/kodinc/tr7c_kodinc2.py` | cbb25303c34d263a95f7539db7d96436fbe9056ed63c4d7d6f650094639cd5fa |
| `kayit/turetme/tr7c/kodinc/tr7c_kodinc2.json` | 39e7b8e221567d07b48803d814044c65c2a405069099ce46610f873edf7b1e1d |
| `kayit/turetme/tr7c/kodinc/tr7c_kodinc2.json.mut.jsonl` | 21680c23b1fa622add7545cd709673d06f7e5697e9360be49d1c82d462ad70e2 |

Kod değişmediği için kodlayıcının 124 sınaması ile benim 74 sınamamın yeniden koşulması gerekmedi. Kodlayıcı ikisini
de c86d8b9b… üzerinde koştu (124/124 ve 45/45; 74/74 ve 31/31). Sınamalar `python3 -I -B
kayit/turetme/tr7c/kodinc/tr7c_kodinc2.py <çıktı> [--parca i/n]` ile yeniden koşulur.
