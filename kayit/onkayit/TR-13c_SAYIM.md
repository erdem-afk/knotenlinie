# TR-13c sayımı: Mw ≥ 6,0'a inince kaç yeni bağımsız küme, MDE kaç

Tarih: 17 Kasım 2026. 0 €. Ön kayıt değil. Kural, sayımdan önce yazıldı: `TR-13c_SAYIM-KURALI.md` (commit d4fb000).
Kod ve json: `kayit/turetme/tr13c/` (`tr13c_sayim.py` → `tr13c_sayim.json`, `tr13c_ek.json`; `tr13c_mde.py` →
`tr13c_mde.json`). Gerçek katalogda V(q), Gini ya da z hesaplanmadı. `tr13b_kosu.kos()` çağrılmadı. Yalnız hazırlık
işlevleri (`hazirla`, `katalog`, `arsiv_oku`) değiştirilmeden içe aktarıldı. İki ham arşivin sha256'sı uyuştu.

## Hüküm

**Yeni K = 5 (a), 5 (b).** R0 tek liste kuralıyla benzetim aralığında güç 0,80'e ulaşılmıyor. Güç f 0,6'da 0,58, f 0,2'de
0,15. Bu yüzden **MDE > 0,6.** Yanlış alarm 0,029. **f ≈ 0,2'ye inmiyor.** Dal (kural §6): **MDE > 0,39 → TR-13c ön
kaydı yazılmaz.** M ≥ 6,0'a inmek bu açık veriyle K'yi yetecek kadar büyütmüyor. Aday elenmedi. Bu bir H0 değildir.

## Sayım (ana liste: 6,0 ≤ M < 6,5 ve ref_gecer[0,3]; 11 olay)

| Olay | Bölge | Küme | R km | Mc önce / ref / ortak / son | N3bg | N_ref | Durum |
|---|---|---|---|---|---|---|---|
| Yakutat 2014 | Alaska | 847 yeni | 50 | 1,6 / 1,3 / 1,6 / 1,8 | 100 | 306 | geçti |
| South Napa 2014 | Kaliforniya | 854 yeni | 50 | 1,4 / 1,4 / 1,4 / 2,1 | 81 | 161 | geçti |
| Mutatá 2016 | Kolombiya | 910 yeni | 50 | 1,9 / 1,9 / 1,9 / 1,9 | 56 | 142 | geçti |
| Kurayoshi 2016 | Japonya | 911 yeni | 50 | 0,7 / 0,7 / 0,7 / 1,5 | 86 | 220 | geçti |
| Tacikistan 2017 | Tacikistan | 1102 yeni | 50 | 2,6 / 2,7 / 2,7 / 2,7 | 42 | 113 | düştü: N3bg < 50 |
| Doğanyol 2024 | Türkiye (Doğu Anadolu) | 1137 yeni | 50 | 1,4 / 1,6 / 1,6 / 1,7 | 85 | 194 | geçti |
| North Palm Springs 1986 | Kaliforniya | 397 TR-13b | 50 | 2,0 / 1,7 / 2,0 / 2,5 | 86 | 161 | geçti (geliştirme) |
| Elmore Ranch 1987 | Kaliforniya | 397 TR-13b | 50 | 1,8 / 1,9 / 1,9 / 2,4 | 82 | 133 | geçti (geliştirme) |
| Joshua Tree 1992 | Kaliforniya | 397 TR-13b | 50 | 2,2 / 2,0 / 2,2 / 2,4 | 86 | 126 | geçti (geliştirme) |
| Kumamoto öncü 2016 | Japonya | 901 TR-13b | 50 | 0,5 / 0,6 / 0,6 / 1,8 | 92 | 400 | geçti (geliştirme) |
| Ridgecrest öncü 2019 | Kaliforniya | 979 TR-13b | 50 | 1,4 / 1,3 / 1,4 / 1,7 | 89 | 271 | geçti (geliştirme) |

- Geçen 10 olaydan 5'i TR-13b kümelerinde (397, 901, 979). Bunlar geliştirme verisidir ve K'ye girmez. Doğrudan çakışma
  denetimi kümelerle tutarlı: yeni beş olayın hiçbiri TR-13b'nin 16 olayıyla çakışmıyor (uzaklık ≤ R_i + R_j, |Δt| ≤ 10 y).
- **(a) yeni K = 5:** 847, 854, 910, 911, 1137. **(b) yoğun ağ (ortak Mc ≤ 2,5) K = 5.** Aynı beş küme; ölçüt hiçbirini
  ayırmadı. Bölge adıyla okunursa klasik yoğun ağ bölgesi yalnız 2 küme (Napa, Kurayoshi), Alaska ile 3. Bu bir bilgi
  satırıdır, kural değil.
- Bütün yeni olayların R'si 50 km'dir (taban yarıçap). Hepsi tek üyeli kümedir.

Bilgi satırları (K'ye girmez):
- (i) ref_gecer[0,3] yanlış olan üç olay: Minto 1995 (474) N3bg 67 / N_ref 74 ve Hualien 2022 (1174) N3bg 79 / N_ref 84
  §3 adımlarını **geçerdi**. Lixouri 2014 (959) ortak Mc 3,5 ile N3bg 17'ye iner ve düşer. TR-13b'nin §2 süzgeci
  (N_ref,bg ≥ 100) kaldırılsaydı K 7 olurdu. Bu MDE dalını değiştirmez (aşağıda K × 2 satırı).
- (ii) Ek tarama: örnekten tahminli üç olay ISC'den tam indirildi (`/mnt/project-files/turetme/tr13c-ham/`, sha256
  `tr13c_ham_sha256.txt`; 30 istek, 401/403/429 yok). Sonuç: Düzce 2022 N3bg 34 → düştü; Japonya 2012 ve Palu 2012
  referans şartını sağlamadı (N3bg 16). Genişletilmiş K da 5.

## MDE (yalnız yapay ETAS; R0 tek liste, üç dallanma)

| Liste | K | Yanlış alarm | f 0,1 | 0,2 | 0,3 | 0,4 | 0,5 | 0,6 | MDE |
|---|---|---|---|---|---|---|---|---|---|
| **(a) = (b) yeni** | 5 | 0,029 | 0,09 | 0,15 | 0,22 | 0,28 | 0,31 | 0,58 | **> 0,6** |
| K × 2 (duyarlılık) | 10 | 0,026 | 0,12 | 0,24 | 0,36 | 0,50 | 0,52 | 0,85 | 0,58 |
| K × 0,5 (10 alt küme ort.) | 2 | 0,035 | 0,06 | 0,09 | 0,13 | 0,15 | 0,19 | 0,32 | > 0,6 |
| Bilgi: TR-13b 15 olayı + yeni 5 (birleşik) | 18 | 0,025 | – | 0,43 | 0,77 | 0,94 | 0,96 | 0,99 | 0,32 |

- Yöntem: `tr13b_inc2.py` düzeni ve dondurulmuş betiğin `yapay_bolge` (B_ref 200), `kalibre` (40 + 40) ve `sonlu_z`
  işlevleri. Sıfır üye ve dallanma başına 400, veri sinyalsiz 300, f başına 150, 200 000 / 20 000 çekiliş, tohum
  20261117. Monte Carlo hatası güçte ≈ ±0,04. f 0,4–0,5 arasındaki düzlük bu gürültüdendir.
- **Kalibrasyon tutmuyor (önemli).** R = 50 km'de yapay ETAS + GK74 arka plan sayısı ≈ 55–70'te doyuyor. μ büyütülünce
  sayı artmıyor. ±%5 yinelemesinden sonra da hedef N3bg 81–100 olan dört üyede havuz ortalaması 41–72'de kaldı. Yalnız
  Mutatá (56) tuttu (`tr13c_mde.json` `kalibrasyon_yineleme`). Bunun iki sonucu var:
  - Yukarıdaki güç, gerçekte olduğundan daha az olaylı bölgelerle hesaplandı. Güç biraz kötümser olabilir.
    Yinelemesiz ilk hesapta (`tr13c_mde_yinelemesiz.json`) güç f 0,6'da 0,68, K × 2 ile MDE 0,53 çıktı. Dal aynı.
  - Dondurulmuş TR-13b kuralları aynen uygulansaydı bu dört üye kalibrasyon şartında (§3.5, dal 2 "geçersiz") takılırdı.
    M 6,0–6,49 olaylarının R'si 50 km olduğundan bu bir rastlantı değildir. **Mevcut ölçü ve üreteç bu olaylar için
    yapısal olarak uygun değil.**
- Birleşik satır yalnız bilgidir: TR-13b z'leri görüldü, hükme giremez. TR-13b üyelerinin havuzları koşunun kendi
  yapay havuzlarıdır (`kosu/havuz`). Burada f 0,1 havuzu yoktur.
- Etki büyüklüğünün kaynağı: f ≈ 0,2 **tahmindir** (TR-13 benzetimi). Literatürden sayı okunamadı.

## Öneri

TR-13c ön kaydı yazılmaz. Neden çift:
- K küçük: yeni 5 küme var. Süzgeç gevşetilse 7, iki katına çıksa bile MDE ≈ 0,55–0,6.
- Yeni olayların hepsi R = 50 km'lik bölgeler. Bunlarda yapay üreteç gerçek N3bg'yi kuramıyor.

Birleşik liste (K 18) f ≈ 0,3'ü görebilirdi, ama 15 üyesinin z'si görüldüğü için bağımsız bir sınav olmaz. TR-13
ailesinde bir sonraki adım olay sayısı değil, (1) BZ20'nin kendi ölçüsü (en yakın komşu kümesizleştirmesi) ve (2)
küçük R'de doymayan bir kümesizleştirme olmalıdır. Bu iki noktadan biri çözülmeden M ≥ 6,0 genişlemesi bilgi getirmez.

## Körlük ve sapmalar

- Gerçek katalogda yalnız sayı, Mc, GK74 sayısı ve doyma adımı hesaplandı. 2026 verisi yok, ana şok sonrası pencere
  yok, Marmara GNSS'e dokunulmadı, İstanbul için olasılık yazılmadı. Düzce 2022 yalnız sayıldı; Marmara terimi değildir.
- Kuraldan sapmalar (beyan):
  - MDE betiğine ±%5 yinelemesi sonuç görüldükten sonra eklendi. Kural §5 bunu açıkça yazmıyordu; dondurulmuş §3.5'te
    vardı. İki sonuç da yazıldı, dal değişmedi.
  - Kural yazılmadan önce ham arşiv dizini bir kez `ls` ile listelendi. Bilinen iki dosya adı dışında içerik okunmadı.
