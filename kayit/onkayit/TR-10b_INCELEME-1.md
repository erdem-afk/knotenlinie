DÜZELTMEYLE KABUL

# TR-10b ön kayıt: bağımsız inceleme 1

İncelenen: `TR-10b_sunme-taban-dagilimi_ONKAYIT.md` (TASLAK sürüm 1, 12 Kasım 2026). Dayanaklar: `TR-10b_SAYIM.md`,
`kayit/turetme/tr10b/tr10b_sayim.py`, `tr10b_sayim_ozet.json`, `onkayit_yardimci/` (`listeler.py`, `sim.py`,
`sim2.py`) ve yazarın scratch çıktıları (`ozet_ek.json`, `sim_out.json`, `sim2_out.json`). Karşılaştırma için
`TR-10_SAYIM.md` §1.2–1.3 okundu.

Körlük beyanı (inceleme): hiçbir sünme ölçer veri dosyası (DAY, 10MIN, MIC, CL10, PKF_EQ, HaywardCreep), hiçbir HDR/Notes
dosyası, HDRx.tar ve noise.pdf açılmadı ya da indirilmedi. Okunanlar: yazarın da okuduğu üstveri, yani README (biçim
belgesi, gürültü tablosu, "Comments specific to various creepmeters" bölümü, dosya aralığı listesi), indirme sayfası
anlık görüntüsünün metni, dizin listeleri (yalnız dosya adları) ve SAYIM'ın ComCat önbelleği. Bütün hesaplar yapay
gürültüyle ya da üstveriyle yapıldı. Betikler depo dışında, scratch'teki `inc10b/` dizinindedir (§D). Depoya bu rapor
dışında dosya eklenmedi, taslak değiştirilmedi, `__pycache__` bırakılmadı.

## Hüküm

Tasarım dikkatli, sayım dürüst, sayılar yeniden üretilebiliyor. İki nokta bu hâliyle dondurulursa koşudan sonra pişman
olunur:

- **E1.** HDR mekanik kuralı yazıldığı gibi uygulanırsa kapıyı kendisi kapatabilir. README'nin "Comments" bölümü HDR
  notlarıyla aynı dilde yazılmış. Kural bu metne harfiyen uygulandığında, K listesindeki 30 olayın hiçbirini doğru türde
  ve tarihli olarak üretmiyor. Buna karşılık iki sahte "son veren" olay üretiyor: "removed" sözcüğünün içinde "moved"
  geçiyor, "sensor removed" ve "removed bend" de terk sayılıyor. Bu iki olay B listesinden 3 yer-pencere düşürür (CRR1
  2013 ve 2018, CWN1 2018). Kapı sınırda olduğu için bu kayıp belirleyici olabilir.
- **E2.** Etiket bandı [2,2, 4,6], README modelinin tamamı değildir: yalnız n = 2 olan altı istasyonun genliğidir.
  README modeli, B listesinin gerçek istasyon karışımı için b* ≈ 10 öngörür. Veriler README modeline tam uysa bile etiket
  büyük olasılıkla "README gürültü bandından büyük" çıkar. Hüküm cümlesi okura bunun tersini düşündürür. §13'teki önsel
  gerekçe de bu yanlış okumaya dayanıyor.

İki engelleyici bulgu da metin düzeltmesiyle giderilir. Aşağıdaki düzeltme metinleri işlendikten sonra taslak
dondurulabilir. Yeni bir aday listesi sayımı gerekmiyor. Yalnız bir bilgi satırının alt kümesi bu incelemede önceden
sayıldı (Ö3).

**Denetimde temiz çıkanlar.**
- Kanonik sha256'lar `ozet_ek.json`'dan birebir yeniden üretildi: B_U `17f120d2…`, A_U `c0279490…`, B_R2 `560b49c1…`,
  A_R2 `cc238e03…`.
- Liste sayıları doğru: B 78 / 35 / 62 / 29 / 6; A 38 / 30 / 31 / 25 / 5. Kesim ve epok dökümleri de doğru.
- Kapsama ilişkileri doğru: A_U ⊂ B_U ve B_R2 ⊂ B_U.
- §3 tablosundaki bütün gün sayıları ve okuma aralıkları doğru.
- Veri bağlantıları doğru: 35 istasyonun DAY / 10MIN / MIC bağlantıları 16 / 21 / 29, toplam 66.
- HDR dosyaları doğru: `HDR/` 29 bağlantılı dosya (ayrıca bağlantısız c461), `HDR2025/` 30 dosya. B listesindeki
  35 istasyondan yalnız 21'inin HDR dosyası var.
- F10'un "etkisi 0" savı doğru: K ve D listesinde hiçbir tarih bir epok yılının 1–16 Ekim'ine düşmüyor.
- Pozitif kontrolün deterministik sınırı [4,726, 5,103] ve elle katman formülü d = 5 − ρ̂_H(1/τ₂ + 1/τ₃) (aralık
  [4,49, 5,00]) doğru.
- §10.2.1 ve §10.4.1 tablolarındaki sayılar yazarın çıktılarıyla aynı.
- Metinde mutlak İstanbul ya da Marmara olasılığı yok.

---

## Yazarın işaretlediği yedi nokta: kısa hükümler

| # | Nokta | Hüküm | Ayrıntı |
|---|---|---|---|
| 1 | F1: aday kümesi U mı, R2 mi | **U doğru.** Kapı avcılığı değil | K4 |
| 2 | F5: medyan(d) ∈ [4,85, 5,03] | **Kabul.** Gerçekçi ve mevsimsel sistematik maskelerde doğru kodu düşürmez. Ortalama-medyan karışıklığını yakalamaz | K1 |
| 3 | 5–6 blokla bloklu bootstrap | **Etiket yeterince korunuyor, aralık değil.** Gerçek q95, U'nun üstünde %14–31 sıklıkla kalıyor. K ≤ 3 tanımsız | Ö1 |
| 4 | HDR mekanik kuralı | **Yazıldığı gibi kullanılamaz** | E1 |
| 5 | (a) eşiği 0,48'e karşı 0,5 | **Sorun değil.** 0,479, doğru kodun herhangi bir geçerli maskede erişebileceği kesin üst sınırdır; ancak denetimin gücü düşük | K2 |
| 6 | Arşiv boşlukları doldurmuş olabilir | **Taslakta anılan kaynak yanlış** (sayfanın notu COVID dönemine ait, kullanılan pencerelerin dışında). Asıl risk README "Other comments 1A"da | Ö5 |
| 7 | F7: c₁ 1,732 → 1,78 | **Yerinde.** Bağımsız MC sonuçları: 1,7789 ± 0,0047 (2003), 1,7760 ± 0,0047 (2013), 1,7781 ± 0,0054 (1978) | K3 |

---

## A. Engelleyici bulgular

### E1. HDR mekanik kuralı yanlış "son veren" olay üretiyor, tarihleri tanımıyor, notları yanlış bölüyor

- **Sınama.** README'nin "Comments specific to various creepmeters" bölümü HDR notlarına en yakın üstveri metnidir:
  aynı operatörlerin yazdığı, tarihli, istasyon başına aygıt notları. Bu bölüm körlüğü bozmaz, çünkü yazar onu zaten
  okudu ve K_OLAY listesi ondan çıkarıldı. §6.4.3'teki kural bu metne mekanik olarak uygulandı
  (`inc10b/hdr_kural.py`) ve sonuç K_OLAY listesiyle karşılaştırıldı (`hdr_karsilastir.py`). Bu bölümde açıklaması
  bulunan 30 olay şu sonucu verdi:

  | Okuma | Doğru türde (K) ve tarihli | Yanlış tür (D ya da son veren) | Tarihsiz ya da kaçan | Sahte son veren |
  |---|---|---|---|---|
  | Taslak, harfiyen (üç harfli ay, virgülsüz) | 0 | 1 | 27 | CRR1 1998-02-10, CWN1 2008-05 |
  | Taslak, cömert okuma (tam ay adı, virgül) | 9 | 9 | 10 | CRR1 1998-02-10, CWN1 2012-04-20 |
  | Önerilen kural (aşağıda) | 28 (≤ 1 yıl önceki bir tarihle) | 0 | 2 (XGH1 1997-12, XMM1 1986) | yok |

- **Kusurlar.**
  1. **Alt dizgi eşleşmesi.** "removed" sözcüğünde "moved" geçer, "removed" de son veren listededir. "Sensor failed on
     Feb 10 1998; sensor removed" (CRR1) ve "Site visit removed bend" (CWN1) son veren olay olur. CRR1 aslında
     çalışmayı sürdürdü (2013 ve 2018 B listesinde), CWN1 de öyle (2018 B listesinde). Kural "replace" için
     "replacement batteries", "break" için "breakdown" gibi alt dizgileri de yakalar.
  2. **Son veren tür, yanlışsa geri alınamaz.** Bir istasyonun sonraki bütün pencerelerini düşürür. Doğruysa bir şey
     katmaz, çünkü terk edilmiş ölçerin sonraki pencerelerinde veri yoktur ve §8 doluluk şartı onları zaten düşürür. Ardıl
     kodların HDR dosyaları (XHR3, XPK2, XSJ3) öncülün "abandoned" notunu taşıyabilir. Kural bunu ardılın son veren olayı
     sayar ve XHR3 2018'i düşürür.
  3. **Tarih biçimleri.** Bu metin "June 4, 2003", "March 7, 1996", "Sept 28, 2004", "November 2006", "In June 2004"
     ve "2004 Parkfield (Sept 28)" biçimlerini kullanıyor. Taslağın biçim listesi bunların çoğunu tanımıyor. Sonuçta
     neredeyse her not elle tarihlemeye kalıyor; mekanik kural fiilen elle kurala dönüşüyor.
  4. **Not bölme.** "Bir sonraki tarihli satıra dek sürer" kuralıyla tarihi tanınmayan paragraflar bir önceki notun
     içine kayıyor. Örnek: CWN1'de "May 2008" notu 2012 ve 2013 notlarını yutuyor ve son veren olay 2008-05'e taşınıyor.
     XPK1'de 2004'teki tel kopması 1998-12 tarihli nota yazılıyor. Ayrıca "anahtar sözcük içeren ama tanınan tarihi
     olmayan satır" ifadesi çok anlamlı: çok satırlı bir notun tarihsiz satırı bu tanıma girer mi, girmez mi, belli değil.
  5. **Eksik sözcükler.** Şu README olayları kaçıyor: "touching the invar wire" (XHSW, XPK1 1998), "unreliable"
     (CWC3), "mis-calibration" (XMM1 1993–1996; listede yalnız "recalibrat" var), "caved in" (XHSW, XMR1 2010),
     "pegged / released tension" (XMD1, XMM1, XVA1, WKR1 2004), "tighten" (CWN1 2003), "offline / failed" (XMBC).
     Parkfield 2004 taşmaları "electronics" sözcüğü yüzünden D olayı oluyor ve ana satırda kalıyor.
  6. **Tarihsiz not.** Elle tarihleme için bir geri dönüş kuralı yok. Bir notun tarihi metinden çıkarılamıyorsa ne
     olacağı yazılı değil.
  7. **Uyarlama serbestliği.** §6.4.5 HDR biçimine "uyarlama" izni veriyor ve uyarlamanın sınırını çizmiyor. Uyarlamayı
     yapan kişi, hangi pencerelerin düşeceğini sayabilecek durumdadır. Bu da kapı sınırdayken, veri görülmeden ama kapı
     sayısı görülerek yapılabilecek bir seçimdir.
- **Neden engelleyici.** Kapı sınırda. U listesinin R2'ye eklediği adayların çoğunun verisi beklenmiyor (§4, §13).
  Yalnız README'ye benzer metinden 3 yer-pencere yanlışlıkla düşüyor. Gerçek HDR dosyaları daha uzun ve 2007 sonrası
  bakım notlarıyla dolu olacak.
- **Düzeltme metni (§6.4 madde 3, 5 ve 6'nın yerine):**

  > 3. **Kullanım kuralı (mekanik; README "Comments specific to various creepmeters" bölümünde önceden sınandı,
  >    TR-10b_INCELEME-1 §D).**
  >    - **Not birimi:** boş satırla ya da yalnız `-`, `=`, `*`, `_` ve boşluktan oluşan bir satırla ayrılan paragraf.
  >      Dosyada hiç boş satır yoksa her satır bir nottur. Not, bulunduğu `.hdr1` dosyasının istasyonuna aittir.
  >      `caveat.txt`'teki bir not yalnız metninde kodu (büyük-küçük harf duyarsız) geçen istasyonlara işlenir. Kod
  >      geçmiyorsa not hiçbir istasyona işlenmez, yalnız listelenir.
  >    - **Tarih:** notun metninde en solda başlayan tam tarih. Tam tarih biçimleri büyük-küçük harf duyarsızdır.
  >      "Ay", İngilizce ay adının tam ya da ilk üç harfli biçimidir ("Sept" dahil) ve ardından nokta gelebilir.
  >      Biçimler: YYYY-MM-DD; YYYY/MM/DD; MM/DD/YY ya da MM/DD/YYYY (ABD sırası); "G Ay YYYY"; "Ay G YYYY" ve
  >      "Ay G, YYYY"; "Ay YYYY", "Ay, YYYY" ve "Ay–Ay YYYY" (ilk ayın 1'i); "YYYY GGG", "YYYY.GGG" ve "YYYY:GGG" (yılın
  >      günü). İki haneli yıl > 30 ise 19xx, değilse 20xx alınır. Notta tam tarih yoksa en soldaki yalın dört haneli yıl
  >      (1960–2023) alınır; tarih o yılın 1 Ocak'ıdır. Bir aralık yazılmışsa (ör. "1993 to 1996", "Sept-October 2005")
  >      en soldaki tarih kuralı başlangıcı verir.
  >    - Tarihi 2023-10-16'dan sonra olan notlar anahtar sözcük aranmadan atlanır.
  >    - **K olayı:** notun küçük harfe çevrilmiş metninde şu öneklerden biri bir sözcüğün başında geçiyorsa (önünde harf
  >      ya da rakam yok; sonu serbest): reset, re-set, rezero, re-zero, zero, broke, break, snap, replac, new wire,
  >      new rod, new sensor, new transducer, new lvdt, removed, relocat, reinstall, re-install, reposition, offset,
  >      repair, damage, vandal, collapse, caved, cave-in, cave in, flood, rodent, gopher, out of range, overrange,
  >      over-range, ran out, calibrat, recalibrat, re-calibrat, miscalibrat, mis-calibrat, fail, unreliab, touch,
  >      tighten, loosen, bump, peg, tension, slid, offline, glitch, spurious, bogus, delet, abandon, destroy,
  >      decommission, no longer. "moved" ve "bent" yalnız tam sözcük olarak eşleşir.
  >    - **D olayı:** notta K öneklerinden hiçbiri yoksa ve electronic, dcp, scale factor ya da gain öneklerinden biri
  >      geçiyorsa.
  >    - **HDR adımı "son veren" olay üretmez.** Terk, söküm ya da kalıcı arıza anlatan notlar da yalnız K olayıdır ve
  >      yalnız [w0 − 30 g, T + 15 g] aralığı tarihini içeren pencereleri düşürür. Gerçekten terk edilmiş bir ölçerin
  >      sonraki pencereleri veri olmadığı için §8 şartlarıyla zaten düşer. Son veren olaylar yalnız §6.2'deki dondurulmuş
  >      listedir.
  >    - Olay tarihi notun tarihidir.
  >    - **Tarihsiz not:** K ya da D öneki içeren ama tarihi olmayan not, aynı dosyadaki iki tarih arasındaki aralık
  >      olarak işlenir. Aralığın başı kendisinden önceki son tarihli notun tarihidir; önceki tarihli not yoksa istasyonun
  >      sayfadaki ilk gözlemidir. Aralığın sonu sonraki ilk tarihli notun tarihidir; sonraki tarihli not yoksa
  >      2023-10-16'dır. Bu aralık [w0 − 30 g, T + 15 g] ile kesişen her pencere düşer (D olayında yalnız "D dışarıda"
  >      bilgi satırında düşer). Elle yapılabilecek tek iş, notun kendi metninde açıkça yazan ama ayrıştırıcının tanımadığı
  >      bir tarihi, özgün satırı alıntılayarak yazmaktır. Bu durumda aralık yerine o tarih kullanılır. Başka hiçbir elle
  >      tarihleme ya da yorum yapılmaz.
  > 4. (Mevcut metin, sonuna eklenir:) Rapor ayrıca şu sayıyı yazar: K olayıyla düşen istasyon-pencerelerden kaçının
  >    notunda "creep" ya da "event" sözcüğü de geçiyor. Bu sayı, gerçek bir sünme olayını anlatan notun aygıt olayı
  >    sayılma sıklığını gösterir. Bilgi içindir; kuralı değiştirmez.
  > 5. **Biçim uyumsuzluğu.** HDR biçimi bu kurala uymuyorsa yalnız not birimi (paragraf, satır ya da tablo satırı) ve
  >    tarih tanıma uyarlanabilir. Önek listeleri, tür kuralı ve tarihsiz not kuralı değişmez. Uyarlama yalnız ekler;
  >    tanınan hiçbir biçim çıkarılmaz. Uyarlanmış kural sırasıyla şu adımlardan geçer: (i) kod olarak commit edilir;
  >    (ii) README'nin "Comments specific to various creepmeters" bölümünde yeniden koşulur ve TR-10b_INCELEME-1 §D'deki
  >    K ve D olaylarını aynı tarihlerle yeniden üretir; (iii) ancak bundan sonra HDR dosyalarına uygulanır. Hangi
  >    pencerelerin düştüğü yalnız bu commit edilmiş kodun tek koşusuyla sayılır. Sayım görüldükten sonra kural değişmez.
  > 6. Yanlış pozitifler (ör. "no offset", "calibration confirms") de K sayılır. Bu, sayıyı düşürür ve önceden kabul
  >    edilir (§16).

- **Ek düzeltme (§11 madde 9'a yeni bilgi satırı):** "HDR olayları uygulanmadan (yalnız §6.1–6.3 listeleri): q50,
  q95 |Δv| [L, U]. HDR'nin düşürdüğü pencereler sakin pencerelerdir; okunmaları TR-10 körlüğünü bozmaz."
- **Ek düzeltme (§16 madde 9'un yerine):** "HDR kuralı. Önek kuralı yanlış pozitif üretir ve sayıyı düşürür. README
  metninde önceden sınandı: K listesinin 30 olayından 28'ini en çok 1 yıl önceki bir tarihle yakalıyor ve hiç sahte son
  veren olay üretmiyor. HDR dosyalarında bunun ne kadar tuttuğu bilinmiyor. Notlar gerçek sünme olaylarını da anlatabilir
  ve bu notların düşürdüğü pencereler tabanı küçültür; madde 4'teki sayaç bunu gösterir. HDR notlarını okumak, seri
  görülmeden yapılan sınırlı bir körlük bozulmasıdır. Notlardaki kayma ve hız ifadeleri kullanılmaz."

### E2. Etiket bandı README modeli değil; README modeli bu karışım için "büyük" öngörüyor

- **Bulgu.** Bant [2,2, 4,6], README tablosunda n = 2,00 olan altı istasyonun rastgele yürüyüş genliğidir. Tablodaki 18
  istasyonun 12'sinde n > 2'dir. B listesinde README tablosunda kodu bulunan 11 istasyon var: CRR1, CWN1, WKR1, X461,
  XGH1, XMD1, XMM1, XSC1, XSH1, XTA1, XVA1. Bunlar 24 istasyon-pencere taşır (B_R2 42'nin 24'ü, B_U 78'in 24'ü).
  `tr10b_sayim.pl_seri` ve `dv_uc` ile, tam maskede, 2013 ızgarasında, istasyon başına 1500 çekilişle hesaplanan
  beklentiler:

  | İstasyon (n, A) | README modeli q95|Δv| (mm/yıl) |
  |---|---|
  | XSC1 (2,27, 1,44); XGH1 (2,23, 1,49); CRR1 (2,00, 2,20) | 3,6; 3,8; 3,8 |
  | XMM1 (2,00, 2,64); XVA1 (2,00, 2,85) | 4,6; 5,0 |
  | CWN1 (2,45, 2,18); WKR1 (2,36, 2,96); XTA1 (2,71, 2,19) | 7,5; 8,9; 10,7 |
  | X461 (2,74, 4,33); XMD1 (2,57, 6,47); XSH1 (2,53, 8,94) | 22,3; 25,6; 33,2 |
  | **24 istasyon-pencerelik havuz** | **q50 2,3; q95 18,0; b* = 18,0 / 1,78 = 10,1; κ 8,0** |

  §10.4.1'deki yapay etiket tablosuna göre b = 9'da etiket %93–100 olasılıkla "büyük" çıkar. Yani veriler README
  modeline tam uysa da hüküm cümlesi "taban README gürültü bandından büyük" der. Okur bunu "taban README modelinden
  büyük" diye anlar. §13'teki gerekçe ("büyük 0,40; README kestirimleri Coalinga ve 1992–1995'i modelden çıkardı") da bu
  karışıklığa dayanıyor. Gerçekte "büyük" etiketinin ana nedeni n > 2 istasyonlarının karışımda bulunmasıdır.
- **Neden engelleyici.** Hüküm cümlesinin ilk sözcükleri etikettir. Etiket bu adla yayımlanırsa düzeltilemez bir yanlış
  okuma doğar. Etiketin adını ve README ile karşılaştırma satırını koşudan önce sabitlemek gerekir.
- **Düzeltme metni (§10.4 "Etiket" maddesinin yerine):**

  > - **Etiket (b* ile; yalnız kapı geçtiyse ve K ≥ 4 ise, §9.3):**
  >   - b*_L > 4,6 ise "taban, README'nin n = 2 istasyonlarının genlik aralığından büyük";
  >   - b*_U < 2,2 ise "taban, README'nin n = 2 istasyonlarının genlik aralığından küçük";
  >   - öteki durumlarda "taban, README'nin n = 2 istasyonlarının genlik aralığında".
  >   - Aralık [2,2, 4,6], README gürültü tablosunda indisi n = 2,00 olan altı istasyonun (XMM1, XVA1, XPK1, CRR1,
  >     CWC3, XMR1) rastgele yürüyüş genliğidir. Bu aralık README modelinin tamamı **değildir**. Tablodaki 18
  >     istasyonun 12'sinde n > 2'dir ve uç ölçüsünde bunların q95|Δv|'si 3,6–33 mm/yıl'dır.
  > - **README modeli satırı (ana satırın parçası; etiket değildir).** ρ_R = q95_ölçülen,R / q95_N0,R.
  >   - Alt küme R: temsilci istasyonunun kodu README tablosundaki 18 koddan biriyle birebir aynı olan B yer-pencereleri.
  >     Ardıl kodlar (XPK2, XSJ3, XHR3) öncülünün parametrelerini almaz.
  >   - q95_N0,R: §11 madde 9'daki README N0 çekilişlerinin (yer-pencere başına 2000, gerçek maske,
  >     `default_rng(20261112 + 3)`) birleşiminin %95 niceliği.
  >   - Aralık: aynı bloklu bootstrap yinelemelerinde hesaplanır. Pay ve payda aynı yer-pencerelerden (tekrarlarıyla)
  >     alınır.
  >   - Okuma: ρ_R,U < 1 ise "README modelinin öngördüğünden küçük"; ρ_R,L > 1 ise "README modelinin öngördüğünden
  >     büyük"; öteki durumlarda "README modeliyle uyumlu".
  >   - R'de 20'den az yer-pencere varsa satır "güç yok" yazar ve nokta değeri verir.
  > - **Önceden hesaplanan beklenti** (TR-10b_INCELEME-1 E2; tam maske, 2013 ızgarası). B listesinde README tablosunda
  >   kodu bulunan 24 istasyon-pencere için README modeli q95|Δv| ≈ 18,0 mm/yıl (b* ≈ 10,1, κ ≈ 8) öngörür. Veriler
  >   README modeline tam uysa bile b* etiketi büyük olasılıkla "aralığından büyük" çıkar. Bu etiket bir model uyumu
  >   hükmü olarak okunmaz; README ile karşılaştırma ρ_R satırıdır.

- **Düzeltme metni (§12 "Kapı geçti" kalıbının ilk köşeli parantezinin yerine):** "TR-10b: [taban, README'nin n = 2
  istasyonlarının genlik aralığından büyük | aralığında | aralığından küçük]; README modeline göre [küçük | uyumlu |
  büyük] (ρ_R = [..] [L, U], yer-pencere [N_R])."
- **Düzeltme metni (§13 ikinci ve üçüncü maddenin yerine; önsel sayılar yazarındır, yazar dondurmadan önce
  değiştirebilir):**

  > - **Kapı geçerse b* etiketi:** aralıktan büyük 0,55; aralıkta 0,40; küçük 0,05. Gerekçe: README modeli, B
  >   listesinin README'de bulunan istasyon karışımı için b* ≈ 10 öngörür (INCELEME-1 E2). Sakin pencere seçimi ve
  >   küçük örneklem değeri aşağı çeker. Bloklu aralığın genişliği "aralıkta" yönüne iter.
  > - **README modeli satırı:** küçük 0,50; uyumlu 0,40; büyük 0,10. README'nin n > 2,5 istasyonlarının (XSH1, XMD1,
  >   X461, XTA1) genlikleri büyük olasılıkla geçici olayları da taşıyor; sakin pencere seçimi bunları dışarıda bırakır.
  > - **Büyüklük:** b ≈ 3 ise q95|Δv| ≈ 5,3 mm/yıl. README modeli bu karışım için ≈ 18 mm/yıl öngörür. Önsel beklenti
  >   ikisinin arasıdır. Sünen istasyonların hızı 7–21 mm/yıl olduğundan 5,3 mm/yıl hızın %25–75'i demektir.

---

## B. Önemli bulgular

### Ö1. 5–6 blokla bloklu aralık: etiket korunuyor, aralığın kendisi yukarı yönde dar; K ≤ 3 tanımsız

- **Yapay denetim** (`inc10b/blok.py`, `etiket.py`; bağımsız Gauss |Δv|; kesim başına genlik, b_k = b·exp(s·z);
  300 tekrar, B = 1000):

  | Kesim yapısı | s (log-sd) | Gerçek q95, U'nun üstünde | Gerçek q95, L'nin altında | U / L medyanı |
  |---|---|---|---|---|
  | 21, 10, 4, 4, 2 (K = 5) | 0 / 0,3 / 0,6 | %25 / %26 / %23 | %3 / %1 / %1 | 1,47 / 1,73 / 2,36 |
  | 21, 19, 8, 6, 4, 4 (K = 6) | 0 / 0,3 / 0,6 | %20 / %14 / %15 | %1 / %1 / %0 | 1,41 / 1,66 / 2,24 |
  | 21, 12, 8 (K = 3) | 0 / 0,3 / 0,6 | %31 / %31 / %30 | %9 / %2 / %0 | 1,33 / 1,52 / 1,86 |

  Yanlış etiket olasılığı (bant içindeki gerçek değerlerde): b = 2,5'te yanlış "küçük" K = 5 için %5–7, K = 6 için
  %1–3. b = 4,0'da yanlış "büyük" ≤ %0,7. Bandın genişliği etiketi koruyor. Ancak "%90 aralık" ifadesi yanıltıcı:
  gerçek q95'in U'nun üstünde kalma olasılığı nominal %5 değil, %14–31'dir. Kaynağı, q95'in küçük örneklemde aşağı
  yanlı olması ve az blokla yüzdelik yöntemin kesikliliğidir.
- **Tanımsız durumlar.** K = 1'de bloklu aralığın genişliği sıfırdır; etiket sıfır genişlikli bir aralıkla verilir.
  K = 3'te yalnız 10 farklı çekiliş bileşimi vardır. Kapı yer ≥ 20 ve yer-pencere ≥ 40 ister, blok sayısı istemez.
  Parkfield'dan (≈ 10 yer) ve Hayward'dan (≈ 9 yer) sonra kalan kesimlerin verisi beklenmediği için K = 3–4 olasıdır.
- **Düzeltme metni (§9.3'e, "Ana: fay kesimi bloklu bootstrap" maddesinden sonra eklenir):**

  > - **Blok sayısı şartı.** Bloklu aralık ve b* etiketi yalnız K ≥ 4 blokta verilir. K ≤ 3 ise ana satır "blok
  >   yetersiz (K = [K])" yazar. Nokta değerler ve yer bootstrap'ının aralığı bilgi olarak verilir, etiket konmaz.
  >   Chihshang satırı da aynı kurala uyar.
  > - **Kapsama notu.** 5–6 blokla yüzdelik bloklu aralık nominal %90'dan dardır. TR-10b_INCELEME-1 Ö1'in yapay
  >   denetiminde gerçek q95, üst sınırın üstünde %14–26 (K = 5–6), alt sınırın altında %0–3 sıklıkla kaldı. Aralık
  >   her yerde "nominal %90" diye yazılır.
  > - Bir nicelik yinelemelerin %10'undan fazlasında tanımsızsa (ör. sünen katman boş) o niceliğin aralığı verilmez,
  >   "güç yok" yazılır.

- **Düzeltme metni (§12 "Yanlış alarm ölçeği cümlesi"nin yerine):**

  > "Orta Kaliforniya sünme ölçerlerinde, önceden tanımlı sakinlik kuralı B'yi geçen 5 yıllık pencerelerde 2 yıllık
  > sünme hızı değişimi %5 sıklıkla [q95] mm/yıl'ı (sünen ölçerlerde hızın %[r95]'ini) aşar. Bloklu üst sınır [U]
  > mm/yıl'dır (nominal %90). Yer-pencerelerin %[p_PKF]'i Parkfield'da, %[p_0818]'i 2008–2018 epoklarındadır. Sakin
  > pencere seçimi ve küçük örneklem bu değeri aşağı çeker. Bu yüzden [q95], koşulsuz yanlış alarm eşiğinin alt
  > kestirimidir. [U] mm/yıl'dan küçük bir değişim bu tür bir ölçerde tek başına olağandışı sayılmaz. Daha büyük bir
  > değişimin olağandışı olduğu ise bu ölçümden çıkmaz."

- **Düzeltme metni (§12 "Kapı geçti" kalıbında "aralık fay kesimi bloklu bootstrap, %90" yerine):** "aralık fay kesimi
  bloklu bootstrap, yüzdelik, nominal %90 (5–6 blokla gerçek kapsama daha düşük)".

### Ö2. Sakin pencere seçimi ve küçük örneklem yanlılığı hüküm cümlelerine tam yansımıyor

- **Bulgu.** §16 madde 3 yanlılığı doğru yazıyor: "Koşulsuz yanlış alarm ölçeği bundan büyük olabilir". Ancak hüküm
  kalıpları "depremsiz pencerelerde" diyor. Pencereler depremsiz değildir, kural B'yi geçen pencerelerdir (Ö3). Ayrıca
  §16 madde 14 Chihshang karşılaştırmasının yalnız "içinde" yönüne yanlı olduğunu söylüyor. Oysa taban sakin seçimden ve
  N ≈ 40'tan dolayı küçük olduğu için "üstünde" okuması da kolaylaşıyor. Net yön bilinmiyor.
- **Düzeltme metni (§12 Chihshang cümlesinin yerine; Ö4 ile birlikte):**

  > "Bilgi: Chihshang 2003 iddiası (−8 mm/yıl, r = −0,43; bindirme fayı, farklı alet dönemleri) bu sakin tabanda |r|
  > ölçüsüyle [tabanın üstünde | içinde | sınırda] (P_r = [..] [L, U]). Taban sakin pencerelerden ve küçük örneklemle
  > kestirildiği için 'üstünde' okuması koşulsuz tabana genellenemez. Pencere uzunluğu farkı ters yönde, 'içinde'
  > yönüne iter."

- **Düzeltme metni (§16 madde 14'ün yerine):** "Chihshang karşılaştırılabilirliği zayıf ve yanlılığı iki yönlü. (i)
  Bindirme fayı, farklı aletler, 7 y ve 3–4 y pencereler: uzun pencerenin gürültüsü küçük olduğundan karşılaştırma
  'içinde' yönüne yanlıdır. (ii) Taban, sakin pencerelerden ve N ≈ 40'la kestirildiği için küçüktür: bu da 'üstünde'
  yönüne yanlıdır. Net yön bilinmez."
- **Düzeltme metni (§16 madde 3'ün son cümlesine eklenir):** "Küçük örneklemde q95'in aşağı yanlılığı (§10.4.1) da
  aynı yöndedir. İki yanlılık birbirini götürmez, toplanır. Hüküm kalıpları bu yüzden q95'i bir alt kestirim olarak
  yazar (§12)."

### Ö3. §7'deki "yalnız örneklem boyunu etkiler" cümlesi yanlış; B, ardıl-sismik pencereleri içeriyor

- **Bulgu.** B ile A yalnız sayı bakımından ayrışmaz, farklı pencereleri seçer. B'nin içerip A'nın dışladığı pencereler:
  1. [w0 − 2 y, T + 2 y] içinde, 5L(M) ile 50 km arasında M 5,0–5,7 olayı olan pencereler. T'den sonraki dönemde B2
     yalnız M ≥ 5,5'i dışladığı için orada M 5,0–5,4.
  2. 5L(M) ile 150 km arasında M 6,0–6,5 olayı olan pencereler. 5L(M) bu büyüklüklerde 70–144 km'dir.
  3. w0'dan 2–5 yıl önceki M ≥ 6 olayların ardıl-sismik dönemine düşen pencereler. A Ş2'nin geriye bakışı 5 yıl, B1'inki
     2 yıldır.

  En büyük etki üçüncü türde. B'nin 2013 epoğundaki Parkfield pencereleri (2008-10 → 2013-10) 2003 San Simeon ve 2004
  Parkfield olaylarından 4–10 yıl sonraya düşüyor. Ardıl kaymanın sönümü bu dönemde sistematik bir yavaşlama (negatif
  Δv) üretebilir. Bu inceleme, SAYIM kodunun `degerlendir`'iyle, B1'in geriye bakışını 5 yıla uzatan alt kümeyi U
  kapsamında saydı (`inc10b/ek_liste.py`): 52 istasyon-pencere, 39 yer-pencere, 25 yer, 6 kesim. Bu alt kümede 2013
  epoğunun 20 yer-penceresi 4'e, Parkfield 21'den 11'e iniyor.
- **Düzeltme metni (§7 "Yazılış sırası" paragrafında "Bu seçim tabanın büyüklüğünü değil, yalnız örneklem boyunu
  etkiler." cümlesinin yerine):**

  > "Bu seçim yalnız örneklem boyunu değil, hangi pencerelerin girdiğini de değiştirir. B, A'nın dışladığı üç tür
  > pencereyi içerir: (i) 5L(M) ile 50 km arasında M 5,0–5,7 olayı olanlar; (ii) 5L(M) ile 150 km arasında M 6,0–6,5
  > olayı olanlar; (iii) w0'dan 2–5 yıl önceki M ≥ 6 olayların ardıl-sismik dönemine düşenler. Örneğin B'nin 2013
  > epoğundaki Parkfield pencereleri 2003 San Simeon ve 2004 Parkfield'dan 4–10 yıl sonradır. B tabanı bu yüzden A
  > tabanından büyük olabilir; ardıl kaymanın sönümü ayrıca işaretli Δv'yi negatife çekebilir. Seçim hiçbir sünme verisi
  > görülmeden yapıldığı için bu bir veri yanlılığı değil, bir tanım farkıdır. A satırı ve 'B1 geçmiş 5 y' bilgi satırı
  > (§11) farkı gösterir."

- **Düzeltme metni (§11 madde 9'a yeni bilgi satırı):**

  > - **B1 geçmiş 5 y:** B1'in zaman aralığı [w0 − 5 y, T]; B2 ve B3 aynı. Aday alt kümesi önceden sayıldı (U kapsamı,
  >   `tr10b_sayim.degerlendir(kapsam_sen="U", kurallar={"B1": dict(B1, once=5), "B2": B2, "B3": B3})`): 52
  >   istasyon-pencere, 39 yer-pencere, 25 yer, 6 kesim. Kanonik sha256
  >   `33b8eafab4782c417c70f55a1606aecdf4fb1466e2c96817a53f2ef453d20b52`. Koşu bu alt kümeyi B listesinin içinden
  >   bu sha256'yla seçer; sakinliği yeniden hesaplamaz.

- **Düzeltme metni (§11 madde 7'nin yerine):** "Epok dökümü (B): her epok için N, q50 ve q95 |Δv|, işaretli Δv medyanı
  ve hızlanan/yavaşlayan pay; bloklu aralık."

### Ö4. Chihshang oranı r_c, ön kaydın r tanımıyla aynı değil (0,36 değil 0,43)

- **Bulgu.** r = Δv / v₅'tir ve v₅ penceredeki ortalama hızdır. Taban 3 y, yakın dönem 2 y ağırlıklıdır. Chihshang
  için −8/22 = −0,36 değeri tabana bölünmüş orandır. Aynı tanımla v₅ = (3·22 + 2·14)/5 = 18,8 mm/yıl ve
  r_c = −8 / 18,8 = −0,43 çıkar. Taslağın eşiği |r| ≥ 0,36 bu yüzden karşılaştırmayı "içinde" yönüne kaydırıyor.
- **Düzeltme metni (§10.5 ilk iki maddenin yerine):**

  > - İddia: Lee vd. 2005 (10.1016/j.crte.2005.04.018). 2003 Chengkung Mw 6,6–6,8 öncesinde 1990–1997 ortalaması
  >   22 mm/yıl, 2000–2003 ortalaması 14 mm/yıl: Δv_c = −8 mm/yıl. Bu ön kaydın r tanımıyla (payda pencere ortalama
  >   hızı, taban 3 y ve yakın dönem 2 y ağırlıklı) r_c = −8 / ((3·22 + 2·14)/5) = −8 / 18,8 = −0,43. (−8/22 = −0,36
  >   tabana bölünmüş orandır ve r ile aynı tanım değildir.) Bindirme fayı; dönemler farklı aletlerle (yüzey ölçümü ve
  >   sünme ölçeri) ve farklı uzunluklarda (7 y ve 3–4 y) ölçülmüş.
  > - **Birincil:** P_r = (sünen katmanda |r| ≥ 0,43 olan yer-pencere sayısı) / (sünen katmandaki yer-pencere sayısı).

  §12 Chihshang cümlesinde "−%36" yerine "r = −0,43" yazılır (Ö2'deki metin).

### Ö5. Boşluk doldurma: taslağın anlattığı risk kullanılan pencerelere uymuyor; asıl risk başka yerde

- **Bulgu.** §16 madde 7 ve SAYIM §2.5 indirme sayfasındaki notu anıyor. Sayfa metnine göre bu not COVID dönemine aittir:
  "During the COVID pandemic … long gaps … the offset … estimated by least squares regression assuming a constant
  rate". Kullanılan son gün ise 2018-10-16. Bu not hiçbir kullanılan pencereye uymaz. Asıl risk README "Other comments
  1A"dadır: "there were no telemetried data and the data in the telemetry files are actually micrometer measurements
  or data digitized from paper records". Erken DAY dosyaları seyrek mikrometre okumalarının günlüğe ara değerlenmiş
  hâli olabilir. Bu durumda doluluk şartı gerçek ölçüm olmayan günlerle geçilir ve u(P) bir doğrusal ara değer olur.
  §8.2'nin ≤ 90 gün ve ≥ 12 ölçüm şartları da atlanmış olur. Bu durumdaki pencerelere örnekler: CRR1 1973 ve 1978,
  XGH1 1978, Hayward 1973. Pencerenin uç değerleri doğrusal dolguya düşerse Δv sıfıra çekilir. Bu da tabanı küçültür.
- **Düzeltme metni (§8.1'e eklenir):**

  > - **Doğrusal dolgu tanısı (bilgi; ana satırı ve kapıyı değiştirmez).** Günlük katmanda en az 15 ardışık geçerli
  >   günlük bir koşu, kendi en küçük kareler doğrusuna göre en büyük mutlak artığı ≤ 0,6·δ ise "doğrusal dolgu"
  >   sayılır. δ, o dosyanın kayma sütununda görülen en küçük ondalık adımdır (ör. iki ondalıkta 0,01 mm). Bir uç
  >   penceresinin ([P − 15 g, P + 15 g]) bütün geçerli günleri böyle bir koşunun içindeyse yer-pencere "dolgulu"
  >   işaretlenir. Eğimi sıfır olan koşular ayrıca sayılır. Kural değerin yönüne ve büyüklüğüne bakmaz. Kapı adımı
  >   dolgulu yer-pencerelerin sayısını kaynak türüne ve epoğa göre yazar; değer yazmaz. §11 madde 9'a "dolgulu
  >   yer-pencereler dışarıda" bilgi satırı eklenir. Dolgulu yer-pencerelerin payı %20'yi aşarsa ana hüküm cümlesine
  >   "(yer-pencerelerin %[..]'inde uç değeri doğrusal dolgudan; Δv sıfıra yanlı olabilir)" eklenir.

- **Düzeltme metni (§16 madde 7'nin yerine):** "Arşivin dolgu ve uzlaştırması. Sayfadaki 'sabit hız varsayımıyla
  ötelenme' notu COVID dönemine aittir; kullanılan pencerelerin dışında kalır. README'ye göre ise erken telemetri
  dosyalarındaki bazı veriler mikrometre ölçümleri ya da kâğıttan sayısallaştırılmış kayıtlardır. Bunlar günlüğe ara
  değerlenmişse doluluk ve boşluk kuralları bunu göremez ve Δv sıfıra çekilir. Dolgu tanısı (§8.1) bunu bilgi
  satırıyla gösterir, düzeltmez."

### Ö6. TR-10 körlüğüyle sınırlı ama gerçek bir örtüşme var

- **Bulgu.** TR-10'un olay öncesi penceresi [E − 61 ay, E − 30 g]'dür (TR-10_SAYIM §1.3: 48 ay v_taban ve 12 ay
  v_önce). 1983-05-02 Coalinga depremleri (M 6,7 ve aynı gün M 5,5) CRR1, XGH1, XMP1 ve XMP2'ye 44–46 km uzaklıktadır.
  Derinlikleri ≤ 30 km olduğu için TR-10'un ana tanımına girerler. Bu dört istasyonun 1978 epoğu okuma aralığı
  (1973-09-16 → 1978-10-16), TR-10'un Coalinga penceresiyle (≈ 1978-04 → 1983-04) ≈ 6,5 ay örtüşür. Örtüşen kısım
  v_taban döneminin başıdır; v_önce'ye dokunmaz. SAYIM'ın ComCat dosyasıyla yapılan denetime göre B_U ve A_U
  listelerinde başka örtüşme yok: M ≥ 5,5, derinlik ≤ 30 km, ≤ 50 km (`inc10b`, satır içi betik). SAYIM §9'daki "TR-10b'nin
  sakin pencereleri TR-10'un olay pencerelerinin tümleyenidir" savı bu yüzden tam değil. §0 F12'nin gerekçesi bu tek
  istisnayla geçerli.
- **Düzeltme metni (§16'ya yeni madde):**

  > 16. **TR-10 körlüğüyle sınırlı örtüşme.** 1983 Coalinga (M 6,7 ve M 5,5; CRR1, XGH1, XMP1 ve XMP2'ye 44–46 km)
  >     için TR-10'un olay öncesi penceresi ≈ 1978-04 → 1983-04'tür. Bu dört istasyonun 1978 epoğu okuma aralığı onunla
  >     ≈ 6,5 ay örtüşür. Örtüşen kısım TR-10'un 48 aylık taban döneminin başıdır; 12 aylık olay öncesi dönemine dokunmaz.
  >     Aday listesinde başka örtüşme yoktur. Pencereler listede kalır. TR-10 yeniden açılırsa Coalinga'nın bu dört
  >     istasyonla çiftleri "taban döneminin ilk ≈ 6,5 ayı TR-10b'de görüldü" notunu taşır.

  (Seçenek: bu üç 1978 yer-penceresi listeden çıkarılabilir. Kapı sınırda olduğu ve örtüşme yalnız taban döneminde
  kaldığı için önerilmez.)

### Ö7. Biçim hatası koşuyu durdurur; düzeltme körlüğü bozabilir (Bilham'ın Hayward 10MIN dosyaları)

- **Bulgu.** §5'e göre biçim hatası koşuyu durdurur, düzeltme "Δv hesaplanmadan" yapılır. Ama düzeltmeyi yapan kişi
  dosyanın satırlarına bakar ve kayma sütununu görür. README, Bilham'ın Hayward ölçerlerini (CPP1, CTM1, COZ1, CHP1,
  CFW1) arşivin dışında sayıyor. Sayfada bu ölçerlerin 10MIN bağlantıları var, ama biçimleri belgelenmemiş. Bu
  istasyonlar B listesinin Hayward yer-pencerelerinin büyük bölümünü taşıyor. Biçim hatası en çok bu dosyalarda
  beklenir.
- **Düzeltme metni (§5'e eklenir):**

  > - **Biçim keşfi (körlüğü koruyarak).** Okuyucu bir dosyada kurala uymayan ilk satırda durduğunda yalnız şunları
  >   yazar: dosya adı, satır numarası, alan sayısı, her alan için tür deseni (tam sayı / ondalık / metin) ve sütun
  >   1–2'nin değerleri. Sütun 3 ve sonrasının değeri yazılmaz, `***` ile maskelenir. Koşu öncesi düzeltme yalnız bu
  >   çıktıya dayanır. Gerekirse ilk 5 sayısal satır aynı maskeyle gösterilir. Kayma değerlerine bakılarak yapılan
  >   hiçbir düzeltme kabul edilmez. Bu tür bir gereksinim doğarsa dosya "biçim belirsiz" nedeniyle düşer ve sayılır.

---

## C. Küçük bulgular

### K1. F5: pozitif kontrol eşiği [4,85, 5,03] (yazarın 2. noktası)

- **Doğru kodu düşürür mü?** Gerçekçi maskelerde 20'li medyanın %0,1–99,9 aralığı en kötü rejimde [4,903, 5,006]'dır;
  eşiğin içinde kalır. "En kötü maske" ise her uçta yanı bağımsız seçiyor; bu gerçekçi değil. H ve T aynı takvim
  gününe (1 Ekim) düştüğü için mevsimsel ya da bakıma bağlı sistematik bir maske iki uçta da aynı yana kayar. Yalnız
  "sonra" yanı için d ≈ 5 − 0,11(1/τ₂ + 1/τ₃) + 0,11/τ₂ ≈ 4,96, yalnız "önce" yanı için d ≈ 5 − 0,11/τ₂ ≈ 4,95 olur.
  5,03'ü aşmak için H'de "önce", T'de "sonra" yanına kaymış maskelerin çoğunlukta olması gerekir; bunun fiziksel bir
  nedeni yok. Üst kenar (gerçekçi payı 0,024) alt kenardan daha dar. Taslak yalnız alt kenarı tartışıyor; ama sistematik
  maskeler üst kenarı zorlamıyor. Eşik kabul edilir.
- **Yanlış kodu geçirir mi?** Evet, üç tür yanlış kodu geçirir: u(P)'yi medyan yerine ortalamayla alan kod (d ≈ 4,956),
  ±15 yerine ±20–30 günlük uç penceresi kullanan kod ve menteşeyi birkaç gün kaydıran kod. Bunların gerçek Δv'ye etkisi
  ortalama-medyan karışıklığı dışında küçüktür. Ortalama ise sıçramalara (glitch) karşı sağlamlığı kaldırır ve (a) ile
  (b) bunu yakalamaz.
- **Düzeltme metni (§10.2 (a) maddesine eklenir):**

  > - (a3) Medyan denetimi: x = 3 mm sabit; yalnız T gününde x = 503 mm (tam maske, günlük katman, dosya yolundan).
  >   |Δv| ≤ 10⁻⁶ mm/yıl olmalıdır. (u'yu ortalamayla alan bir kod ≈ 8,06 mm/yıl verir.)
  > - (a4) Gün kayması denetimi (tam maske, günlük katman, dosya yolundan): x = 10·1{gün ≥ H} için Δv = −10/τ₃;
  >   x = 10·1{gün ≥ H + 1 g} için Δv = +10/τ₂. İkisinde de |hata| ≤ 10⁻⁶ mm/yıl olmalıdır. Bir günlük kayma bu iki
  >   değerden birini öbürüne çevirir.

- **Düzeltme metni (§10.3 ikinci maddeye eklenir):** "ρ, günlük değere eklenir. 10MIN'de değer önce günlük medyana
  indirgenir, sonra ρ eklenir. ρ gün tarihinde, t = (gün − w0)/365,25 ile hesaplanır. (ρ 10 dakikalık satırlara
  eklenirse uçtaki günün ρ'su 0,219 mm'ye çıkar ve deterministik alt sınır 4,708'e iner; şart 1'in 4,72'si bu durumda
  doğru kodu düşürebilir.)"

### K2. (a) eşiği 0,5 ile en kötü maske 0,48 (yazarın 5. noktası)

- **Bulgu.** Gürültüsüz (a) serisinde, her uç penceresinde ≥ 10 gün şartını sağlayan **herhangi** bir maskeyle
  erişilebilecek en büyük |Δv − Δv₀| hesaplandı (`inc10b/a_sinir.py`). Hesap, her uçta 31 günün sıralı değerlerinden
  10'lu alt kümelerin uç medyanlarıyla yapıldı. Sonuç: 1973 0,479; 1978, 1998, 2003, 2018 0,468; 2008 0,462; 2013
  0,479 mm/yıl. 0,5'lik eşik bu yüzden doğru kodu hiçbir maskede düşüremez. Buna karşılık bu denetimin yanlış kodu
  yakalama gücü düşüktür. Gün kayması ve ortalama-medyan hataları K1'deki (a3) ve (a4) ile yakalanır. n ≤ 100'de %99
  niceliği fiilen en büyük değerdir.
- **Düzeltme metni (§10.2 (a) "Gerçek maskelerde" satırının yerine):** "Gerçek maskelerde: |Δv − Δv₀|'nin en büyüğü
  ≤ 0,50 mm/yıl. (Uç penceresinde ≥ 10 gün şartıyla doğru kod bu sınırı aşamaz: kullanılan epoklarda herhangi bir
  maskede erişilebilen en büyük hata 0,462–0,479 mm/yıl'dır; TR-10b_INCELEME-1 K2.)"

### K3. c₁ ve κ başvuru değeri (yazarın 7. noktası)

- **Bulgu.** Bağımsız MC (tohum 8128, 100 000 çekiliş, tam maske, saf RW, b = 1) sonuçları: q95|Δv| 1978'de
  1,7781 ± 0,0054, 2003'te 1,7789 ± 0,0047, 2013'te 1,7760 ± 0,0047 (MC hatası 200 yeniden örneklemden). Yazarın
  değerleri 1,7805 ve 1,7748. 1,732, 4000 çekilişlik MC'nin beklenen hatası (≈ ±0,027) içinde, ≈ 1,8 sd altta kalan
  bir sapmadır. c₁ = 1,78 doğru. κ'nın Gauss değeri 1,95996 / 0,67449 = 2,906'dır; MC sonuçları 2,898–2,932. Taslağın
  2,93'ü MC gürültüsüdür.
- **Düzeltme metni (§10.4):** c₁ cümlesine "(MC hatası ±0,005; 1978, 2003, 2013 ızgaraları 1,775–1,781 arasında;
  bütün epoklarda aynı sabit kullanılır)" eklenir. κ maddesinde "2,93" yerine "2,91 (Gauss, analitik:
  1,960 / 0,674)" yazılır ve okuma kuralı "κ_L > 2,91" olur.

### K4. F1: U listesi doğru seçim; metindeki döküm eksik (yazarın 1. noktası)

- **Hüküm.** Kapı gerçek veriyle uygulandığına göre U daha az yanlıdır. R2 bir kapsam modelidir; README'nin 2013
  anlık görüntüsü eksikse gerçek pencereleri dışlar. U'nun eklediği adaylar Δv görülmeden seçildi. Veri yoksa doluluk
  şartıyla düşerler. U'nun seçilmesinin nedeni R2'nin sınırda kalmasıdır ve bu §0'da açıkça yazılı. Seçim Δv'ye değil,
  yalnız kapının geçme olasılığına dokunur. Bu yüzden kapı avcılığı sayılmaz. R2 alt kümesi zaten bilgi satırı olarak
  yazılıyor (§11 madde 9).
- **Eksik.** §4'ün anlatımında XHR1 2018 yok.
- **Düzeltme metni (§4'teki "U'nun R2'ye eklediği adayların çoğunun…" cümlesinin yerine):** "U, R2'ye 36
  istasyon-pencere (21 yer-pencere) ekler: HW* elle ölçerlerinin 1973 ve 2003–2013 pencereleri (20), HLC1, HLD1 ve
  SHR2'nin 2013–2018 pencereleri (6), TWR1 ve XPH1'in 2013–2018 pencereleri (4), XDL2 2013 ve 2018 (2), BIT1, XMP1 ve
  XMP2 1998 (3) ve XHR1 2018 (1). XHR1 dışındakilerin hepsi README dosya aralıklarının dışındadır. XHR1'in README'de
  aralığı yoktur."
- **XDL2.** README durum sütununda "Semi-abandoned, doesn't measure creep" yazıyor. Liste bağlayıcı olduğu için XDL2
  listede kalır. **Düzeltme (§11 madde 9'a):** "XDL2 dışarıda (README durumu: 'doesn't measure creep')".

### K5. Yer sayımı ve yakın yerler

- **Bulgu.** Koordinatı 3 ondalığa dek aynı olmayan ama birbirine ≤ 3 km olan yerler var. Hayward kentinde HWR1/HWR2,
  HWE1/HWW1 ve HWP1/CHP1 birbirine 0,9–2,5 km. Ayrıca HLC1–HLD1 1,7 km, SJN1–XSJ3 2,1 km, CRR1–XGH1 2,2 km, XMD1–XMM1
  2,3 km, XPK2–XTA1 1,9 km ve XPK2–XVA1 2,9 km. Bunlar aynı yağışı ve aynı yerel olayları paylaşır. Bloklu bootstrap
  bunu aralıkta karşılar, kapının "yer ≥ 20" sayısı ise karşılamaz.
- **Düzeltme metni (§10.1'e eklenir):** "Kapı adımı ayrıca, birbirine ≤ 3 km olan yerleri tek bağlantılı kümeleyerek
  'yer kümesi' sayısını bilgi olarak yazar. Kapı yer sayısıyla uygulanır. Küme sayısı 20'nin altındaysa ana hüküm
  cümlesine '(≤ 3 km'de kümelenince [..] yer kümesi)' eklenir."

### K6. README N0 bilgi satırının tanımı

- **Düzeltme metni (§11 madde 9, "README N0 beklentisi" maddesine eklenir):** "Eşleşme yalnız kodun birebir aynı
  olmasıyla yapılır; ardıl kodlar (XPK2, XSJ3, XHR3) öncülün parametrelerini almaz. Güç yasası serisi okuma aralığının
  başında sıfırdan başlar (`pl_seri`). n > 2'de sonuç başlangıç seçimine bağlıdır; bu yazılır. Aynı oran yalnız
  T ≥ 2008 alt kümesi için de yazılır, çünkü README tablosu 2004 öncesi veriden kestirildi."

### K7. Tek koşu işaret dosyası yalnız scratch'te

- **Bulgu.** `TR10B_GERCEK_DV_HESAPLANDI` veri dizininde, yani depo dışındaki scratch'te oluşturuluyor. Yeni bir indirme
  dizini bu korumayı kendiliğinden atlatır.
- **Düzeltme metni (§14 madde 6, ikinci alt maddenin yerine):** "Ana ölçü hesaplanmadan hemen önce iki işaret dosyası
  `x` kipinde oluşturulur: veri dizininde ve depoda (`kayit/turetme/tr10b/TR10B_GERCEK_DV_HESAPLANDI`). Depodaki
  dosya, manifest sha256'sını ve oluşturulma zamanını taşır. Koşu kodu başlangıçta iki yeri de denetler; biri varsa
  durur. Depodaki işaret dosyası çıktılarla aynı commit'te commit edilir."

### K8. Metin ayrıntıları

- §2.3'teki "2024 ve sonrasının hiçbir satırı ayrıştırılmaz" ifadesi şöyle düzeltilir: "2024 ve sonrasının hiçbir
  satırının ilk iki sütundan sonrası ayrıştırılmaz". Satırın atlanacağını anlamak için tarih ayrıştırılmak zorunda.
  §5'e şu eklenir: "Okuma aralıkları dışındaki satırlarda yalnız ilk iki alan denetlenir. Bu satırlarda sütun 3'ün sayı
  olmaması koşuyu durdurmaz, 'aralık dışı bozuk' diye sayılır."
- §10.2 (b) yapay 10MIN dosyası günde bir satırla yazılıyor; gerçek dosyada günde 144 satır var. Düzeltme: "En az bir
  10MIN yer-penceresinde yapay seri günde 144 satırla (10 dakikada bir, aynı günlük değere ±0,01 mm beyaz gürültü
  eklenmiş) yazılır. Günlük medyana indirgemenin sonucu, günde bir satırlık yazımın sonucuyla |fark| ≤ 0,005 mm/yıl
  içinde eşleşmelidir."
- §6.4 madde 2: `HDR/` dizininde bağlantısız bir `c461.hdr1` de var. Madde 2.1'in "sayfada bağlantısı olan 29" ifadesi
  doğru; açıklık için "(bağlantısız `c461.hdr1` okunmaz)" eklenir.

---

## D. Yapay hesapların ve üstveri denetimlerinin özeti (yeniden üretim)

Betikler scratch'teki `inc10b/` dizinindedir. Hepsi `python3 -I -B` ile koşuldu, `tr10b_sayim.py`'yi değiştirmeden
içe aktarır ve yalnız yapay gürültü ya da üstveri kullanır.

| Betik | Ne yapar | Sonuç |
|---|---|---|
| `hdr_kural.py`, `hdr_karsilastir.py` | Taslağın §6.4.3 kuralını README "Comments" bölümüne uygular | Harfiyen okumada 0/30 doğru, cömert okumada 9/30; sahte son veren olaylar CRR1 ve CWN1 |
| `hdr_kural3.py` | Önerilen kuralı (E1) aynı metne uygular ve K_OLAY ile karşılaştırır | 28/30 (≤ 1 yıl önceki tarihle); kaçan XGH1 1997-12 ve XMM1 1986; sahte son veren yok. Uyarlama denetiminin (E1 madde 5(ii)) başvuru çıktısı budur |
| satır içi | README modeli q95, B listesi karışımı (pl_seri, tam maske, 2013, 1500/istasyon, tohum 99) | 24 istasyon-pencere: q95 18,0, b* 10,1, κ 8,0 |
| `blok.py` | Bloklu yüzdelik aralığın kapsaması (tohum 31) | Gerçek q95 U'nun üstünde: K = 5'te %23–26, K = 6'da %14–20, K = 3'te %30–31 |
| `etiket.py` | Bant içi gerçek değerde yanlış etiket (tohum 57) | Yanlış "küçük" (b = 2,5): %1–7; yanlış "büyük" (b = 4,0): ≤ %0,7 |
| `a_sinir.py` | (a) serisinde herhangi bir ≥ 10 günlük maskeyle erişilebilen en büyük hata | 0,462–0,479 mm/yıl |
| `c1.py` | c₁ ve κ, 100 000 çekiliş (tohum 8128) | 1,7760–1,7789 ± 0,005; κ 2,906–2,916 |
| `ek_liste.py` | B1 geçmiş 5 y alt kümesi (SAYIM `say` aynen, yalnız sonuç ekli) | 52 / 39 / 25 / 6; sha256 `33b8eafa…d20b52` |
| satır içi | TR-10 olay öncesi pencereleriyle örtüşme (ComCat önbelleği; M ≥ 5,5, derinlik ≤ 30 km, ≤ 50 km) | Yalnız Coalinga 1983 × {CRR1, XGH1, XMP1, XMP2} 1978 |
| satır içi | Liste sha256'ları, sayılar, bağlantı ve HDR dosya sayıları, §3 gün sayıları, yakın yer çiftleri | Bkz. Hüküm "temiz çıkanlar" ve K5 |
