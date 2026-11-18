# TR-7c sonucu: kör Parkfield kontrolü (K1c), tek koşu, 18 Kasım 2026

**Hüküm (dondurulmuş karar metni, dal (c), kalan (iv)):** "ölçü sınanamadı (algılayıcı kör olaylarda tetiklenmiş
tremoru tetikleyici genliğinden ayıramadı) (kalan: (iv))"; ayırt edilemez, görülebilir en küçük duyarlılık
s = 0,58 (m_t 0,8) / 0,77 (m_t 0,5). **Marmara dalga formu indirilmedi, Marmara kör kaldı.**

Hüküm dosyası: `kayit/turetme/tr7c/kosu/tr7c_k1c_hukum.json` (commit 34ee163). Koşu defteri:
`kayit/turetme/tr7c/kosu/KOSU-DEFTERI.md`. Koşu dondurması a278070; kod sha c86d8b9b…

## Sayılar

| Ölçüt (Z3) | Sonuç | Geçti mi |
|---|---|---|
| (i) pozitif olaylarda algılama | X_P = 9 / 10 (eşik X_min 4, ⌈n_P/2⌉ 5) | evet |
| (ii) yanlış alarm oranı | FAR_PK = 0,086 (10 / 116 pencere; sınır 0,30) | evet |
| (iii) pozitif − negatif ayrımı | X_N = 5 / 29; tek yanlı Fisher p = 8,0 × 10⁻⁵ (sınır 0,05) | evet |
| (iv) modülasyon, ≥ 3 pozitif olayda p ≤ 0,01 | ölçülebilen 4 olay; p = 0,018, 0,048, 0,17, 0,89; geçen 0 | **hayır** |

- Duyarlılık kestirimi ŝ = 0,88 (alt sınır 0,52). Kuril 2007 çıkarılınca (i)–(iii) aynen geçiyor (Fisher p 2,0 × 10⁻⁴).
- A50_PK 10,0, A90_PK 20,0, A_PK 33,1 (TR-7 birimleriyle).
- Modülasyonun ölçülememe nedeni: 2001–2005 pozitif olaylarında uzun dönem başvuru kanalı yok (6 olayda `ref` boş);
  başvuru kanalı olan 4 pozitif olayın hiçbiri 0,01 eşiğini geçmedi (en iyisi Şili 2010, p 0,018).
- k (modülasyonu ölçülebilir olay sayısı): üstveriden 10 beklenmişti, koşuda 5 gerçekleşti. k_koşu ile (iv)'ün gücü
  s 0,7'de 0,61 (m_t 0,8) / 0,24 (m_t 0,5): bu şart baştan düşük güçlüydü (bilgi satırı).
- Genliği eşlenmiş 4 negatif olayda modülasyon ölçülemedi (etiket "genlik" yok).

## Okuma

Algılayıcı (sabit sızıntı kuralı K5 ile) kör olaylarda tetiklenmiş tremor bildirilen olayları bildirilmeyenlerden
açıkça ayırıyor: 9/10'a karşı 5/29. TR-7'deki tasarım kusuru (tutarlı kümelerin sızıntı kuralıyla silinmesi) giderilmiş
görünüyor. Düşen şart, algılanan şeyin tremor olduğunu yüzey dalgası fazına kilitlenmeyle doğrulayan modülasyon
şartı. Bu şart iki nedenle sınanamadı: eski olaylarda başvuru kanalı yok, ve ölçülebilen olaylarda etki 0,01 eşiğine
ulaşmıyor. Dondurulmuş metne göre bu "var" ya da "yok" değil, "ölçü sınanamadı"dır; (c) dalında uygulama hatası yolu
yoktur, yeniden koşu yapılmaz.

## Koşu kaydı

- Dört aşama Hetzner makinesinde, her `baslat` commit'i `kos`tan önce GitHub'da doğrulandı (E-3).
- Bir dış kesinti: K1c-negatif 06:37Z'de sunucu güncellemesinin servis yeniden başlatmasıyla öldü; çıktı yazılmadan,
  sonuç görülmeden. `durdu` kaydı 2742932e, sürdürme c090bbca (E-1).
- Not: K1c-algılama `kos` komutu 18:31:01Z → 18:33:51Z sürdü (pozitif birimlerin algılaması + modülasyon + hüküm).
- Harcama: makine kirası içinde (ek ücret yok).

## Körlük durumu

Parkfield'ın 39 kör kontrol birimi artık görülmüş veridir (geliştirme verisi). Marmara tremor verisi açılmadı.

## Ardıl soru (başarısızlığın biçiminden)

Ayırma var, doğrulama yok. Çıkan soru: tremor kimliğini faz modülasyonu yerine başvuru kanalı gerektirmeyen bir
ölçütle (çok istasyonlu zarf tutarlılığı / yavaşlık, ya da bağımsız tremor kataloğuyla çakışma) doğrulayan ölçü
sınanabilir mi. Yeni bir kör kontrol kümesi gerekir (Parkfield harcandı): Cascadia, Japonya (Nankai) ya da Tayvan
tetiklenmiş tremor listeleri. Aday TR-7d; önce 0 € üstveri sayımı.
