# TR-2 ön kayıt incelemesi 1 (bağımsız, kör)

**Hüküm: DÜZELTMEYLE KABUL.** Dört engelleyici bulgu düzeltilmeden metin dondurulmamalı (E1–E4). Bulguların
hiçbiri sınavın koşulmasını engellemiyor. Hepsi sonuç görülmeden metne eklenebilir.

İncelenen: `kayit/onkayit/TR-2_sonraki-M6-yonu_ONKAYIT.md` (commit adf9522), `kayit/onkayit/TR-2_SAYIM.md`,
`kayit/turetme/tr2/tr2_sayim.py` (d7a4e84). Tarih: 11 Kasım 2026.

Körlük beyanı (inceleyici):
- İsabet hesaplanmadı.
- Hiçbir sonraki olayın s işareti hesaplanmadı, okunmadı ya da yazılmadı.
- 2026 verisi sorgulanmadı. ComCat'e hiç sorgu atılmadı.
- Scratch'teki ham veriden yalnız `mutlak_eksen` (|s|, |d|) ile taraf bilgisi taşımayan sayımlar yapıldı.
  Betik: `/tmp/claude-0/-home-user/635decb6-3930-5a4d-9c31-b6f30d64fb94/scratchpad/inceleme/tarafsiz.py`.
  Bu betik kümeden ilk nitelikli birincili seçiyor. Seçim K = 40 veriyor; bu, sayımla tutarlı.
- Anlık görüntünün sha256 değeri doğrulandı. Kayıttaki 07881910…efd59 değeriyle aynı.

Taraf bilgisi taşımayan ek sayımlar (40 seçili küme, aşağıdaki bulgularda kullanıldı):

| Ölçü | Değer |
|---|---|
| İki kümenin ortak "ilk sonraki olayı" | 0 |
| İlk sonraki olayı başka bir kümenin seçili birincili olan küme | 0 |
| İlk sonraki olayı kendi kümesinden bir doğrultu atımlı birincil olan küme | 2 |
| İlk sonraki olayı herhangi bir doğrultu atımlı birincil olan küme | 14 |
| Birincilden sonraki 30 gün içinde, 3 L içinde M ≥ Mw olayı olan seçili birincil (çift/öncü durumu) | **6** |
| İlk sonraki olayı 0,5 L ≤ \|s\| ≤ 1 L aralığında (kırık boyu içinde) olan küme | 6 |
| İlk sonraki olayın büyüklüğü ≥ birincilin Mw'si olan küme | 10 |
| İlk sonraki olayın büyüklük türü Mw olan küme | 39 |
| Birincilden ilk sonraki olaya geçen gün (en küçük / çeyrek / medyan / çeyrek / en büyük) | 31 / 282 / 1285 / 3221 / 4775 |
| Aynı anda iki aday | 0 |

---

## Engelleyici bulgular

### E1. H0 altında isabet olasılığı 0,5 değil. Ortak uzamsal arka plan, ETAS yönüne doğru yanlılık üretir.

**Bulgu.** Hüküm satırı, "yön bilgi taşımaz" durumunda P(isabet) = 0,5 olduğunu varsayıyor. Tanımlar bu varsayımı
dört mekanizmayla bozuyor. Hiçbiri sessiz taraf fiziğine dayanmıyor.

1. **Ortak arka plan.** Artçı bulutu "30 gün içinde, 3 L içinde, M ≥ 4" olan her olaydır. Arka plan sismisitesi
   ayıklanmıyor.
   - Birincilin bir yanında daha etkin bir yapı olabilir: dalma-batma kenarı, üçlü kavşak, komşu dizi.
   - O yan hem 30 günde daha çok "artçı" (yoğun taraf) hem de 15 yılda daha çok M ≥ 6 (sonraki olay) üretir.
   - Havuz da aynı yerden geliyor: mekanizma koşulu yok, derinlik ≤ 40 km.
   - Yön: isabet olasılığı 0,5'in **altına** iner (yoğun taraf, ETAS, H0 yönü).
2. **Çift ya da öncü durumu (6/40 küme).** Birincilden sonraki 30 gün içinde ve 3 L içinde M ≥ Mw bir olay var.
   - Kod bu olayı buluttan atıyor (`m >= b["mw"]`) ama onun artçılarını atmıyor.
   - Böylece yoğun taraf, büyük olayın bulunduğu yan olur. Büyük olayın 30 günden sonraki artçıları da sonraki olay
     havuzuna o yandan girer.
   - Yön: H0 ve ETAS.
3. **Büyük bir ana şokun gölgesindeki birincil.** Birincil, kendisinden büyük bir ana şokun artçısı olabilir.
   Ölçüt §5.5'te 1 yıl ve 3 L; ana tanımda bu birinciller atılmıyor.
   - Bulut, büyük ana şokun süren artçılarıyla kirlenir. Yoğun taraf büyük ana şoka bakar, sonraki olaylar da orada
     yoğunlaşır.
   - Yön: büyük olasılıkla H0. Gölgedeki birincil büyük kırığın ucunda olduğunda ters yön de mümkün.
4. **Dış merkezin konum hatası.** Dış merkez kırık boyunca δ kadar kaymışsa simetrik bir bulut, kaymanın ters
   yanında yoğun görünür. Sessiz taraf böylece kaymanın yönü olur.
   - Hedef kutusu da kayan merkeze göre kurulur. Yoğun yandaki kutu gerçek merkeze δ kadar yaklaşır ve daha çok
     aday yakalar.
   - Yön: H0. Etki küçük, çünkü kutu 0,5 L'den başlıyor.

Yanlılığı H1 yönünde olabilecek iki mekanizma:

5. **Kutunun dış merkeze bağlanması.** Tek yönlü kırılmada kırık, dış merkezden yoğun tarafa uzanır.
   - Yoğun yandaki kutunun 0,5 L–1 L kesimi az önce kırılmış fay parçasıdır. Sessiz yanda böyle bir kesim yoktur.
   - Kırılmış parça gerilimini bıraktıysa, "sonraki olay kırılmamış yandadır" sonucu boşluk fiziği olmadan da çıkar.
   - Bu sayıca sınırlı: ilk sonraki olayların 6/40'ı |s| ≤ 1 L aralığında.
   - Asıl sorun yorum: bkz. Ö1.
6. **Kıyı ile deniz arasındaki tamlık farkı.** M ≥ 4 tamlığı ağa bağlı; M ≥ 6 küresel olarak tam.
   - Algılama yüzünden sessiz görünen taraf, M ≥ 6 süreci açısından rastgele bir yandır.
   - Bu tek başına isabeti 0,5'e **çeker**: etki seyrelir, güç düşer, sahte H1 oluşmaz.
   - Ama tamlık farkı (1)'deki etkin yapıyla çakışıyorsa (deniz tarafında etkin yapı, kıyıda iyi ağ) yön
     belirsizleşir.

"Sonraki olayı olan" koşulu tek başına yanlılık üretmez, çünkü iki yanın kutuları simetrik. Ancak (1) ile
birleştiğinde, etkin yapının bulunduğu yanda olayı olan kümelerin örneklemde fazla temsil edilmesine yol açar.

**Neden önemli.**
- Net yanlılık büyük olasılıkla H1'e **karşı**. Bu yüzden bir H1 hükmü görece korunaklıdır.
- H0 hükmü, §5.6'daki "yoğun taraf lehine" notu ve §4'teki ETAS − taban satırı ise doğrudan şişer. "ETAS yönü doğru
  çıktı" okuması, arka planın asimetrisinden ayrılamaz.
- p0 gerçekte 0,55 olsaydı, X ≥ 26 eşiğinin gerçek yanılma olasılığı 0,05 değil 0,13 olurdu. Yanlılık yukarı yönlü
  olursa H1 de korunaksız kalır.

Önerilen negatif kontrol: tarafları rastgele ama dondurulmuş bir kuralla atamak işe yaramaz. Kural nasıl dondurulursa
dondurulsun, beklenen isabet tanım gereği 0,5 olur ve geometri hakkında hiçbir şey ölçmez. Doğru kontrol, aynı
geometriyi ve aynı sessiz tarafı koruyup yalnız sıra bilgisini bozan **zaman ters çevrimidir**.

**Düzeltme metni (§5'e yeni bilgi satırları; §3'e yorum kuralı):**

> 8. **Negatif kontrol: zaman ters çevrimi.**
>    - Seçilmiş 40 kümenin her biri için aynı birincil, aynı doğrultu (stk), aynı sessiz taraf ve aynı hedef
>      kutusu kullanılır (0,5 L ≤ |s| ≤ 5 L, |d| ≤ max(L, 30 km)).
>    - "Önceki olay": aynı havuzdan (M ≥ 6, derinlik ≤ 40 km), [max(t0 − 15 yıl, 1976-01-01), t0 − 30 gün]
>      aralığında kutuya düşen olayların zamanca **en sonuncusu**.
>    - İsabet_ters: önceki olayın s işareti sessiz tarafın işaretine eşitse 1.
>    - K_ters ve X_ters yazılır. Ayrıca tek yanlı kesin binomla iki test yapılır: p = 0,5'e karşı üst kuyruk ve
>      alt kuyruk.
>    - Bu satır ileri sınavla aynı koşuda, aynı kodla hesaplanır.
> 9. **Çift ya da öncü:** birincilden sonraki 30 gün içinde, 3 L içinde M ≥ Mw olayı olan kümeler (sayımda 6/40)
>    çıkarıldığında X ve K.
>
> **Yorum kuralı (§3'e eklenir; hükmü değiştirmez, hükmün adını niteler):**
> - Hüküm H1 ise ve zaman ters çevrimi de p = 0,5'i üst kuyrukta α 0,05 ile reddediyorsa, hüküm "H1 (sıraya özgü
>   değil, statik geometriyle ayırt edilemez)" diye yazılır ve §8'e hiçbir şey taşınmaz.
> - Hüküm H0 ise ya da ters yön notu düşüldüyse, ve zaman ters çevrimi alt kuyrukta p = 0,5'i reddediyorsa, bu sonuç
>   "arka plan asimetrisiyle ayırt edilemez" diye yazılır. ETAS lehine okunmaz.
> - Gerekçe: H0 altında P(isabet) = 0,5 varsayımı, ortak arka plan ve çift/öncü durumları yüzünden ETAS yönüne
>   kayabilir. Ters çevrim aynı geometride bu kaymayı ölçer.

### E2. §4'teki boşluk − taban satırı, §3'ün hükmüyle çelişebilir.

**Bulgu.** Boşluk modeli sabit q = 0,65. Bu durumda boşluk − taban farkı, X'in tekdüze bir fonksiyonudur:
X·ln 1,3 + (K − X)·ln 0,7.

Hesap: K = 40, tohum 20261111, 10 000 yinelemeli küme bootstrap'i, %2,5–97,5 yüzdelik aralık.
- Aralık sıfırı yalnız X ≥ 30 iken dışlıyor.
- X 26–29 aralığında §3 "H1" diyecek, §4 ise "boşluk − taban ayrışmaz" diyecek.
- Örnek: X = 26 için fark +1,83 nat, aralık [−1,89, +5,54].

**Neden önemli.** Okur iki satırı birbirine karşı kullanabilir. Bu sonuç sonrası anlatı seçimine kapı açar.

**Düzeltme metni (§4'ün sonuna):**

> Öncelik: Karar yalnız §3'ün binom satırıyla verilir. Boşluk − taban satırı X'in tekdüze bir dönüşümüdür. K = 40'ta
> bootstrap aralığı yalnız X ≥ 30 iken sıfırı dışlar (önceden hesaplandı). X 26–29 aralığında "H1, log skor
> aralığı sıfırı içeriyor" diye birlikte yazılır. Bu durum H1'i zayıflatmaz ve güçlendirmez. Bu bölümdeki
> "ayrışır" sözcüğü yalnız ETAS ile ilgili iki satır için yorum taşır.

### E3. ETAS yönü satırı tek anlamlı değil.

**Bulgu.**
- (a) **Arka plan terimi tanımsız.** "Arka plan iki kutuda eşit sayılır" deniyor, ama formülde arka plan terimi yok.
  - Eşit bir μ eklenirse p_i, μ'nün büyüklüğüne bağlı olarak 0,5'e çekilir.
  - Eklenmezse cümle anlamsız kalır.
- (b) **Zaman çekirdeği yok.** Bu savunulabilir: Omori integrali iki taraf için ortaktır ve oranda büyük ölçüde
  sadeleşir. Ama tam sadeleşmez, çünkü 1. günde ve 29. günde gelen artçıların ağırlığı farklıdır. Bu ihmal açıkça
  yazılmalı.
- (c) **Izgara tanımsız.** Izgaranın kökeni, hücre merkezi kuralı, izdüşüm ve r'nin hangi düzlemde ölçüldüğü
  yazılmamış. 2 km ızgarada etki küçük, ama iki kodlayıcının birebir aynı p_i'yi üretmesi için gerekli.
- (d) **"Tarafsızlar dahil" belirsiz.** Kapsam açık değil: |s| < 5 km olan artçılar mı, yoksa PCA'ya giren her artçı
  mı (≤ 3 L, M ≥ 4, M < Mw)?
- (e) **Birincilin katkısı.** Birincil dış merkezde nokta kaynak olarak, simetrik biçimde girer. Bu yüzden yalnız
  seyreltir. Bu bilinçli bir seçim olarak yazılmalı.
- (f) **"Küresel ETAS çalışmalarındaki olağan değerler" kaynaksız.** SAYIM §5 ya uydurma (1976–1999) ya da yayımlanmış
  bir parametre seti öneriyordu. Ön kayıt ikisini de yapmıyor.
  - q = 1,5 Zhuang–Ogata tipindeki (r² + d²)^(−q) çekirdeğinde makul bir değer.
  - Verim üssü α = 1,0 (log10 tabanında) da makul.
  - Ama bunlar "seçilmiş değerler" diye yazılmalı, "olağan" diye değil.
- (g) **Sonraki olayın ETAS'ta yeri.** Sonraki olayın büyüklüğü ve havuz tanımı (M ≥ 6, mekanizma serbest) ETAS'ta
  yer almıyor. Bu doğru, çünkü oran sadeleşiyor. Not edilmeli.

Sabit 0,65'lik boşluk modeli savunulabilir. Önceden konmuş, tek parametreli bir alternatiftir; 0,5 ile H0'ın
alternatifi 0,70 arasında durur. Yalnız E2'deki öncelik notu gerekli.

**Düzeltme metni (§4'teki ETAS maddesinin yerine):**

> - ETAS yönü: p_i = R_sessiz / (R_sessiz + R_yoğun), sonra [0,05, 0,95] aralığına kırpılır. **Arka plan terimi
>   yoktur.** Simetrik bir arka plan yalnız p_i'yi 0,5'e çeker; bilinçli olarak eklenmez.
>   - j kümesi: birincil ve onun 30 günlük artçı bulutu. Bulut, sınav tanımındaki PCA girdisinin tamamıdır:
>     (t0, t0 + 30 gün], dış merkezden ≤ 3 L, M ≥ 4, M < Mw. |s| < 5 km olanlar da dahildir.
>   - R_taraf = Σ_j 10^(1,0·(M_j − 4)) · Σ_hücre (r_jh² + d_j²)^(−1,5) · 4 km².
>   - d_j = max(5 km, 0,5·L(M_j)). L Wells–Coppersmith ile hesaplanır. Birincil için M_j = Mw.
>   - Koordinatlar: birincilin dış merkezine göre `eksen_bilesen` ile (s, d) km. j olayları da aynı fonksiyonla
>     (s_j, d_j') koordinatlarına taşınır. r_jh, bu düzlemde Öklid uzaklığıdır.
>   - Hücreler: s = ±(0,5 L + 1 + 2k) km ve d = −D + 1 + 2m km (D = max(L, 30 km)). Merkezi kutunun içinde kalan
>     hücreler alınır.
>   - Zaman çekirdeği kullanılmaz. Omori integrali iki tarafta ortaktır. j'ler arasındaki zaman farkı ihmal edilir.
>   - Parametreler (üs 1,5; verim üssü 1,0 log10 tabanında; d_j kuralı) **seçilmiştir, uydurulmamıştır**.
>     Zhuang–Ogata tipi küresel ETAS çekirdekleriyle aynı mertebededir.
>   - p_i değerleri, isabet kodu çalışmadan önce `kayit/turetme/tr2/tr2_etas_p.csv` dosyasına yazılır ve commit
>     edilir. Dosyadaki sütunlar: küme, birincil id, p_i. Dosya sonraki olayla ilgili hiçbir bilgi içermez.

### E4. Koşunun determinizmi ve sızıntı yüzeyi: isabet öncesi bir manifest dondurulmalı.

**Bulgu.**
- Anlık görüntü sha256 ile sabitlenmiş; doğrulandı. Ancak sha, tar.gz dosyasının baytlarını tanımlar. Kod dizinden
  okuyor ve bunu doğrulamıyor.
- Kodun "K = 40 değilse durur" kuralı var, ama durduktan sonra ne olacağı yazılmamış.
- "Kümeden zamanca ilk nitelikli birincil" ve "zamanca ilk sonraki olay" seçimleri henüz kodlanmamış. Bunlar isabet
  koduyla aynı adımda yazılacak.
- "Tek koşu" kuralı, koşu sırasında bulunan bir hatanın ne olacağını söylemiyor.
- Yazar 1999 İzmit–Düzce ve 2025 olaylarını tanıyor. Bu küçük bir risk.

**Neden önemli.** Kodlama serbestliği en çok son adımda kalıyor: hangi birincil, hangi sonraki olay, hangi stk. Bu
seçimler isabetten önce, taraf bilgisi olmadan sabitlenebilir. Sabitlenirse isabet, beş satırlık bir fonksiyona
iner.

**Düzeltme metni (§6 adım 2'nin önüne yeni adım; adım 4'e ek):**

> 2a. **İsabet öncesi manifest.** İsabet kodu yazılmadan önce `tr2_manifest.csv` üretilir ve commit edilir.
> - Satır başına alanlar: küme, birincil id, t0, Mw, L, stk (seçilen düğüm düzlemi), sessiz tarafın işareti (+1
>   ya da −1; bu bilgi yalnız artçılardan gelir), n+ + n−, |A|, ilk sonraki olayın id'si, |s|/L, |d|, aday sayısı,
>   ilk önceki olayın id'si (E1 için).
> - Manifest sonraki olayın s işaretini İÇERMEZ.
> - Manifest, `tar.gz` açıldıktan sonra her dosyanın sha256 değerini listeleyen bir dosya ile birlikte üretilir.
>   Koşu kodu bu listeyi doğrular.
> - Koşu kodu yalnız manifestteki id'leri kullanır. İsabet, manifestteki stk ve dış merkezle `eksen_bilesen`
>   üzerinden hesaplanır.
>
> 4 (ek). Koşu bir istisnayla durursa:
> - Yalnız istisnanın doğrudan nedeni düzeltilir. Düzeltmenin farkı kayda geçer.
> - Manifest değişmez.
> - Herhangi bir isabet ya da X değeri görüldükten sonra yapılan her kod değişikliği, sonuçla birlikte "koşu
>   sonrası değişiklik" başlığında yazılır.
>
> K doğrulaması başarısız olursa sınav koşulmaz. Kayıt "anlık görüntüden yeniden üretilemedi" olarak kapanır.
> Yeni bir ComCat sorgusu yapılmaz.

---

## Önemli bulgular

### Ö1. H1 "boşluk" diye okunamaz. Kırılma yönü ile kırılmış parçanın gölgesi ayrılmıyor.

**Bulgu.**
- Sessiz taraf, dış merkeze göre tanımlanıyor. SAYIM §2'ye göre olayların yarısında |A| ≥ 0,5. Bunun önemli bir
  bölümü tek yönlü kırılmanın izi olabilir.
- §5.1 ve §5.2 bunu bilgi satırı olarak alıyor, ama hükmün adı "sessiz taraf (boşluk)".
- Araştırma notu NA-2 boşluğu "kırık ucunun önündeki taraf" diye tanımlıyordu. Tek yönlü kırılmada bu, tam tersine
  **yoğun** tarafın ucudur.
- Yani sınav, notun kurduğu hipotezle aynı yönü sınamıyor olabilir.

**Düzeltme metni (§3'ün sonuna):**

> Hükmün adı "sessiz taraf"tır. "Kırılmamış komşu segment (boşluk)" yorumu ancak iki koşul birlikte sağlanırsa
> yazılır:
> - (i) §5.1'de isabet oranı u/L medyanının altında ve üstünde aynı yöndedir (ikisi de > 0,5);
> - (ii) §5.2'deki ağırlık merkezi tanımında X/K ≥ 0,6'dır.
>
> Aksi halde H1 "dış merkezin arkası" diye yazılır ve kırılma yönüyle ayırt edilemez sayılır. Bu ayrım §8'deki
> aktarım için de koşuldur.

### Ö2. Güç kapısı ve "sınırda geçti" ifadesi

**Bulgu.** Eşikler doğru (tablo aşağıda).
- K = 40 için X ≥ 26, gerçek tek yanlı büyüklük 0,040.
- X ≤ 22, p = 0,70 altında 0,032.
- En küçük ölçülebilir oran (güç 0,80) 0,698.
- "Sınırda" ifadesi dürüst.

Görüşüm: Sınavı koşmak savunulabilir. "Güç yok" denmemeli. Üç gerekçe var.
1. **Sınırın kaynağı kesiklilik.** Kapının yalnız K = 40'ta geçmesi binomun kesikliliğinden kaynaklanıyor, gerçek
   bir güç sınırından değil.
   - K = 39'un gerçek büyüklüğü 0,027, K = 40'ınki 0,040. K = 40 rastlantıyla α'ya yakın bir kritik değere sahip.
   - Kesikliliği olmayan (normal yaklaşım) en küçük ölçülebilir oran K 39–41 için hep ≈ 0,69. Yani gerçek güç üç K'de
     de neredeyse aynı.
   - Kapı "sınırda" değil, "kesikli testin şansıyla eşikte". Kural önceden konmuştu ve K anlık görüntüyle
     kilitlendi; kapıyı kapatmak için bir dayanak yok.
2. **Asıl risk güç değil, geçerlilik.** p0 gerçekte 0,5 olmayabilir (E1). Bunun çaresi kontroldür, koşmamak değil.
3. **Beklenen sonuç açıkça yazılmalı.** Gerçek etki 0,65 ise sonuç olasılıkları: H1 0,57, H0 0,12, ayırt edilemez
   0,31. Bu durum yazılı olmalı.

Kapının kökeni de belirsiz. Kapı eşiği (≤ 0,70) ilk kez SAYIM belgesinde, K ile aynı commit'te (d7a4e84) görülüyor.
Kapının sayımdan önce konduğu depodan doğrulanamıyor.

**Düzeltme metni (§3, güç kapısı paragrafının sonuna):**

> Eşikte geçişin nedeni binomun kesikliliğidir: kesin testin K = 40'taki gerçek büyüklüğü 0,040, K = 39'daki 0,027.
> Kesiklilik olmasaydı en küçük ölçülebilir oran K 39–41 için ≈ 0,69 olurdu. Kapı eşiği (K ≥ 30, ≤ 0,70) sayımla
> aynı commit'te (d7a4e84) yazıldı. Taraf bilgisi taşımadığı için körlüğü bozmaz, ama "önceden" sayılmaz. Önceden
> hesaplanan sonuç olasılıkları:
>
> | Gerçek p | H1 | Ayırt edilemez | H0 |
> |---|---|---|---|
> | 0,50 | 0,04 | 0,18 | 0,78 |
> | 0,60 | 0,32 | 0,37 | 0,31 |
> | 0,65 | 0,57 | 0,31 | 0,12 |
> | 0,70 | 0,81 | 0,16 | 0,03 |

### Ö3. §7'nin son cümlesi doğrulanamıyor.

**Bulgu.** "Ana tanım ... sayımdan önce yazılmış çerçevedir" deniyor.
- Tanımların sayısal değerleri depoda ilk kez sayımla aynı commit'te görülüyor: 0,5–5 L, 15 yıl, 300 km, 30 km
  tabanı.
- NA-2 notunda pencere "X km/10 yıl" diye açık bırakılmış.
- Varyant sayıları tanım dondurulmadan görüldü. Bu taraf bilgisi taşımadığı için körlüğü bozmaz, ama cümle
  kanıtlanmamış bir sırayı ileri sürüyor.

**Düzeltme metni:**

> Ana tanım varyant sayımlarıyla aynı commit'te (d7a4e84) yazıldı. Varyant sayıları ana tanım seçilmeden önce
> görülmüş olabilir. Seçim taraf bilgisi olmadan yapıldı. Kapıyı geçen başka varyantlar (|A| ≥ 0,2, λ oranı 1,5,
> n ≥ 8) da vardı ve ana tanım bunların arasından K'si en büyük olan değil.

### Ö4. §8'deki İstanbul bağı ve §1'deki dil

**Bulgu.**
- (a) §8'deki "İstanbul 30 yıl aralığının ≈ %46'sı" kaynaksız. Yalnız NA-2 notunda geçiyor; ön kayıtta ne olduğu
  açıklanmıyor. Okurun aklına "TR-2 belirsizliğin %46'sını çözer" gibi bir anlam gelebilir.
- (b) KOERI ile asimetri ölçmek, sınavın tanımını değiştirmek demek. Sınavdaki tanım ComCat'te M ≥ 4. 2025 olayının
  ComCat'te yalnız 6 yanlı artçısı var ve tanımla ölçülemiyor. SAYIM risk 3 bunu belirtiyor, ön kayıt söylemiyor.
- (c) §1'deki "kırık doğuya ilerleyip sessiz kesimin kenarında durdu" cümlesi bir yorumu olgu gibi sunuyor. Ayrıca
  "sessiz kesim" ifadesi sismik boşluk ya da kilitli kesim anlamında kullanılıyor; sınavdaki "sessiz taraf" (az
  artçı) ile karışıyor.
- (d) §1'deki "puanlı çok olaylı sınavı yok" ifadesi bir literatür taramasının sonucu. Şöyle yazılmalı: "bulamadık".
- (e) §1'deki "köprü k 2, J 0,0022" açıklamasız jargon.

Mutlak İstanbul olasılığı yazılmıyor. Bu doğru.

**Düzeltme metni (§8'in yerine):**

> H1 çıkarsa ve Ö1'in iki koşulu sağlanırsa, ileri test defterine bir rakip terim aday olarak girer. Terim yalnız
> oran olarak cevap verir: "sıradaki M ≥ 6 hangi yanda daha olası". Mutlak olasılık yazılmaz.
> - Marmara 2025 bu sınavın tanımıyla (ComCat M ≥ 4) ölçülemiyor. KOERI'nin düşük Mc'li kataloğuyla hesaplanacak
>   asimetri farklı bir tanımdır. Aktarım, bu ölçek farkının ayrı bir doğrulamasını gerektirir: aynı küresel
>   olaylarda ComCat M ≥ 4 ile yerel katalogdan elde edilen sessiz tarafın uyuşma oranı.
> - Bu doğrulama yapılmadan Marmara'ya yalnız "küresel örneklemde sessiz taraf lehine bir eğilim var" cümlesi
>   taşınır.
> - H0 ya da ayırt edilemez çıkarsa Marmara'ya hiçbir şey taşınmaz.
> - Bu sınav zaman eksenini daraltmaz; yalnız uzamsal eksene dokunur.
>
> (§1) "...Nisan 2025 Marmara Mw 6,2 olayının artçıları yerel kataloglarda doğuya yığıldı. Bu, 'sıradaki olay az
> artçılı tarafta' anlatısını besledi. Bulabildiğimiz kadarıyla bu savın puanlı, çok olaylı bir sınavı yok."

### Ö5. Bağımsızlık ve aynı sonraki olay

**Bulgu.** Tanımda iki boşluk var:
- Aynı M ≥ 6 olayı iki kümenin "ilk sonraki olayı" olabilir: kümeler 300 km ve 1 yıl ile ayrılır, ama kutular
  390 km'ye, pencere 15 yıla uzar.
- Bir kümenin sonraki olayı başka bir kümenin birincili olabilir.

Taraf bilgisi taşımayan sayım (bu inceleme):
- Ortak ilk sonraki olay 0.
- Başka bir seçili birincil olan ilk sonraki olay 0.
- 2 kümenin ilk sonraki olayı kendi kümesindeki bir birincil.
- Yani anlık görüntüde sorun yok, ama kural yazılı değil.

Ayrıca aynı levha sınırında (örneğin Kuzey Anadolu) 50 yıl içinde birden çok küme olabilir. Bunlar zayıf biçimde
bağımlıdır; binom bunu yok sayar.

**Düzeltme metni (§2'ye):**

> Bir M ≥ 6 olayı birden çok kümenin ilk sonraki olayıysa, yalnız zamanca ilk birincilin kümesi için sayılır.
> Diğer kümeler o olay olmadan yeniden değerlendirilir (sıradaki aday). Anlık görüntüde bu durum taraf bilgisi
> olmadan sayıldı: 0 küme. Manifest (E4) bunu doğrular. Aynı levha sınırındaki kümeler arası zayıf bağımlılık
> modellenmez; bu bir sınırdır (§7).

---

## Küçük bulgular

### K1. 30. gün sınırı çakışıyor.

Artçı aralığı (t0, t0 + 30 gün], sonraki olay aralığı [t0 + 30 gün, ...]. Tam 30. günde gelen bir M ≥ 6 olay iki
aralığa da girer.

Düzeltme: "Sonraki olay aralığı (t0 + 30 gün, min(t0 + 15 yıl, 2025-12-31)]".

### K2. §2'nin özeti iki koşulu atlıyor.

Havuzda büyüklük türü serbest ve mekanizma koşulu yok. Özete şu eklenmeli: "havuz: büyüklük türü ve mekanizma
serbest". Ölçüm: ilk sonraki olayların 39/40'ı Mw. Kodda ayrıca kaba enlem filtresi var (`|Δenlem| > 8°`). Bu filtre
kutudan geniş olduğu için zararsız, ama kodun bir parçası olarak anılmalı.

### K3. İşaret kuralı yazılmalı.

"s işareti, sessiz tarafın hesaplandığı stk ile ve aynı `eksen_bilesen` fonksiyonuyla (dış merkez kökenli)
hesaplanır." Eşitlik durumu yok, çünkü |s| ≥ 0,5 L > 0 ve |A| ≥ 1/3. Bu da yazılmalı.

### K4. §5.6'daki ters yön notu E1'e en açık satır.

Düzeltme: "Bu not, E1'deki zaman ters çevrimi alt kuyrukta da anlamlıysa 'arka planla ayırt edilemez' diye yazılır."

### K5. §5.7 (Türkiye) tek bir olay.

Düzce'nin isabeti ya da ıskası tek başına yorumlanmamalı. Düzeltme: "Sonucu yalnız anılır; hiçbir Marmara cümlesine
dayanak olmaz."

### K6. Eksik bilgi satırları

Aşağıdakiler taraf bilgisi taşımadan manifeste konabilir ve isabet oranı her alt grupta ayrı yazılabilir:
- İlk sonraki olayın |s|/L ≤ 1 olması (6/40).
- Sonraki olayın büyüklüğünün ≥ Mw olması (10/40).
- Sonraki olayın kendisinin doğrultu atımlı bir birincil olması (14/40).

Bu satırlar hükmü değiştirmez.

### K7. §2'deki gerekçe sayıları

"K 39: 0,715" kodun 0,001 adımlı aramasından geliyor; kesin değer 0,714. Sorun değil, ama tablodaki tutarlılık için
"(0,001 adımla)" eklenebilir.

---

## Kendi hesabım: kesin binom eşikleri (tek yanlı α 0,05)

H1 eşiği c: P(X ≥ c | 0,5) ≤ 0,05 olan en küçük c. H0 eşiği h: P(X ≤ h | 0,70) ≤ 0,05 olan en büyük h. Ters yön
eşiği t: P(X ≤ t | 0,5) ≤ 0,05 olan en büyük t.

| K | H1: X ≥ c | P(X ≥ c \| 0,5) | P(X ≥ c−1 \| 0,5) | H0: X ≤ h | P(X ≤ h \| 0,7) | Ters: X ≤ t | Güç 0,60 / 0,65 / 0,70 | En küçük ölçülebilir oran (güç 0,80) |
|---|---|---|---|---|---|---|---|---|
| 38 | 25 | 0,0365 | 0,0717 | 21 | 0,0388 | 13 | 0,290 / 0,534 / 0,774 | — |
| 39 | 26 | 0,0266 | 0,0541 | 22 | 0,0500* | 13 | 0,248 / 0,487 / 0,740 | 0,714 |
| **40** | **26** | **0,0403** | 0,0769 | **22** | **0,0320** | **14** | **0,317 / 0,572 / 0,807** | **0,698** |
| 41 | 27 | 0,0298 | 0,0586 | 23 | 0,0414 | 14 | 0,275 / 0,526 / 0,776 | 0,706 |
| 42 | 27 | 0,0442 | 0,0821 | 23 | 0,0264 | 15 | 0,345 / 0,608 / 0,836 | — |

\* K = 39'da 0,04999…; eşiğin tam üstünde.

K = 40 için hüküm olasılıkları:

| Gerçek p | P(H1) | P(ayırt edilemez) | P(H0) |
|---|---|---|---|
| 0,50 | 0,040 | 0,175 | 0,785 |
| 0,60 | 0,317 | 0,372 | 0,311 |
| 0,65 | 0,572 | 0,304 | 0,124 |
| 0,70 | 0,807 | 0,161 | 0,032 |

p0'daki sapmanın H1 eşiğine etkisi (K = 40, X ≥ 26):

| Gerçek p0 | P(X ≥ 26) |
|---|---|
| 0,52 | 0,068 |
| 0,55 | 0,133 |
| 0,58 | 0,232 |

Sonuç: Ön kayıttaki eşikler (X ≥ 26 H1, X ≤ 22 H0, X ≤ 14 ters yön), en küçük ölçülebilir oran 0,699 ve
güç değerleri (0,32 / 0,57 / 0,81) doğru.
