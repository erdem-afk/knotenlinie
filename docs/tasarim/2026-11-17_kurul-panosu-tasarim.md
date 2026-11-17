# Kurul Panosu: ilk tasarım önerisi (reddedildi; yerini kurul-sohbeti.html aldı)

17 Kasım 2026. Yalnız tasarım; hiçbir şey kurulmadı, yayımlanmadı, paylaşılmadı.

## Tek cümle

Sunumdaki "Open Questions Board" slaytını çalışan bir sayfaya çeviriyoruz: hocalar soru sorar, geçmiş işlerimize itiraz eder, birbirleriyle tartışır ve her sorunun beş adımdaki yerini izler. Arkada aynı repo, aynı ön kayıt disiplini, aynı defter çalışır.

## Bileşenler

1. **Kurul panosu (yeni sayfa, İngilizce, yalnız davetli hocalar).** Bölümler:
   - *Ask*: tek kutuluk soru formu (soru, varsa bildiği veri kaynağı, "neyi görürsem ikna olurum").
   - *Questions*: her soru bir kart; durum çizgisi Received → Plan drafted → Plan approved by asker → Frozen → Running → Answered → In ledger. Kartta plan, kod ve sonuç bağlantıları.
   - *Past work*: defterdeki ≈100 fikir, hükmü ve dersiyle, aranabilir. Her satırda "Challenge this" düğmesi.
   - *Discussion*: soru ve geçmiş iş başına yorum; hocalar birbirini görür.
   - *How it works / limits*: sunumdaki "ne yapabiliriz, ne yapamayız" ve "şüphe edilmesi gerekenler" listesi.
2. **Pano verisi.** Sorular, plan onayları, itirazlar sayfanın paylaşımlı veritabanında durur. Durum, hüküm ve cevap alanlarını yalnız biz yazarız; plan onayını yalnız soruyu soran hoca atabilir.
3. **Köprü (pano → proje).** Zamanlanmış bir görev günde bir iki kez panoyu okur; yeni soru, itiraz ya da onay varsa bu projede sana bildirir. Hocanın yazdığı metin veri sayılır, talimat sayılmaz. Hiçbir giriş kendi başına koşu başlatmaz.
4. **Repo.** Her soru için `kayit/kurul/Q-nnn/` (soru.md, onkayit.md, DONDUR sha + OTS, sonuc.md) ve `kayit/adaylar.jsonl` içinde bir satır (kol "KB", soran alanı). Panodaki defter elle değil bu dosyalardan üretilir. Repo zaten herkese açık; `kayit/` henüz main'de değil, önce main'e alınmalı.

## Bir soru nasıl koşuya dönüşür

| Adım | Kim | Ne olur | İnsan kapısı |
|---|---|---|---|
| 1. You ask | Hoca | Formu doldurur | – |
| – | Erdem | Fizibilite kabulü: açık veri var mı, kör sete dokunuyor mu, kaba maliyet. Bilimsel değer yargısı yok; ret olursa gerekçesi de deftere yazılır | **K1** |
| 2. We freeze | Ajanlar | Önce defterde arama (aynı soru koşulmuş mu), sonra ön kayıt taslağı: hipotez, veri, ölçüt, görülebilir en küçük etki, H1/H0 eşikleri | – |
| – | Hoca | Planı panoda okur, yorum yazar, onaylar | **K2** |
| – | Bağımsız inceleyici ajan + dondurma | Mevcut kural: inceleme, sha, zaman damgası | K3 (otomatik) |
| 3. Agents run | Ajanlar | Tek koşu, açık veri | **K4**: yalnız >50 € ya da kör veri gerekiyorsa Erdem |
| 4. Answer | Erdem | Cevabı hocaya gitmeden önce okur | **K5** |
| 5. Ledger | Ajanlar | Deftere ve panoya işlenir; "etki yok" da kayıtlı | – |

## Geçmişi sınama (üç düzey)

- **Oku ve itiraz et**: itiraz kayda girer, yazılı cevap döner; haklıysa hüküm satırı düzeltilir ve düzeltme görünür kalır.
- **Yeniden koşu iste**: seçtikleri bir sonucu temiz kurulumdan yeniden koşarız, sonucu eskisinin yanına yazarız. Sunumdaki 6. şüpheyi ("dışarıdan kimse kodu yeniden koşmadı") kısmen kapatır; tam kapanması için koşuyu bizden bağımsız biri yapmalı.
- **Kendin koş**: repo ve adım adım talimat.

## Yetkiler

- Hoca: her şeyi okur, soru sorar, yorum yazar, yalnız kendi sorusunun planını onaylar. Durum, hüküm, defter ve repoya yazamaz; ajanlara doğrudan komut veremez.
- Erdem: sahip; K1, K4, K5.
- Ajanlar: plan, koşu, durum ve cevap yazar; kör set ve bütçe kuralları aynen geçerli.

## Riskler ve dürüst sınırlar

1. **Dış hesap.** Hocalar ODTÜ'den, bizim organizasyonun dışında; e-posta davetiyle girerler ve büyük olasılıkla bir claude.ai hesabı gerekir. Davetli dış kullanıcının forma yazabildiğini henüz denemedim; kurmadan önce bir test hesabıyla sınanmalı. Tutmazsa B seçeneğine düşülür.
2. **"Sorgusuz koşarız" vaadi ile K1.** Kapı yalnız fizibiliteye bakar. Yine de bir hoca bunu "sorumu eledi" diye okuyabilir; bu yüzden ret gerekçesi panoda açık yazılır.
3. **Mutlak olasılıklar.** Sunumdaki kural panoda da geçerli: İstanbul/segment olasılık rakamı gösterilmez. İç panel paylaşılmaz.
4. **Kör setler.** Kör veri isteyen soru reddedilmez; ön kayıtla 2027 penceresine bağlanır.
5. **Ad ve itibar.** Slayt "soru ve yazar açık defterde kalır" diyor. Hocanın adı ancak açık rızasıyla dışarıya açık deftere girmeli; varsayılan yalnız pano içi.
6. **Kapasite.** "Haftalar içinde cevap" vaadi için aynı anda en çok üç açık soru; fazlası sırada görünür.
7. **Proje kuralı.** "Tek artifact" kuralına istisna gerekir: bu ikinci bir sayfa. İç panel Türkçe, iç işleyiş ve harcama içeriyor; hocalara o gösterilmemeli.
8. **Alan dışı sorular.** Betonarme sorularında veri ve boru hattı yok; ilk böyle soru yavaş gider ve bunu baştan söylemek gerekir.

## Seçenekler

- **A. Tam etkileşimli pano (öneri).** Yukarıdaki her şey tek sayfada.
- **B. Salt okunur pano + e-posta.** Hocalar izler ve okur; soru ve itiraz sana e-postayla gelir, panoya biz işleriz. Hesap riski yok, ama "ortak istişare" zayıf kalır.
- **C. GitHub Issues/Discussions.** Kayıt en şeffaf, kurulum en ucuz; ama inşaat hocalarının GitHub kullanması beklenmez.

Öneri: A, dış hesap sınaması tutmazsa B.

## Aşamalar

- **v0**: iskelet, geçmiş defter, soru formu; seninle iç deneme (bir sahte soru beş adımı baştan sona geçer).
- **v1**: ilk davetli hocanın ilk gerçek sorusu; sunumda canlı gösterilebilir.
- **v2**: diğer hocalar, tartışma ve yeniden koşu istekleri.

## Erdem'den beklenen kararlar

1. A, B ya da C?
2. Pano dili İngilizce mi (sunumla aynı), yoksa iki dilli mi?
3. Hoca adları dışarıya açık defterde mi, yalnız pano içinde mi?
4. Geçmiş işlerden hepsi mi görünsün (≈100 fikir), yoksa bir seçki mi?
5. Pano hocayla görüşmeden önce hazır mı olsun (canlı gösterim), sonra mı?
