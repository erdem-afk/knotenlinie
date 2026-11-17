# TR-13d sayım kuralı (sayımdan ÖNCE yazıldı): açık bölgesel kataloglarla kaç yeni bağımsız küme

Tarih: 17 Kasım 2026. Durum: **sayım kuralı; ön kayıt değil.** 0 €. Bu dosya, hiçbir bölgesel katalog sorgulanmadan
önce commit edilir. Sonuç `TR-13d_SAYIM.md`'de; kod ve json `kayit/turetme/tr13d/`'de; indirilenler
`/mnt/project-files/turetme/tr13d-ham/` altında, sha256 listesiyle. Sonuçtan sonra bu kural değiştirilmez; değişirse
rapor beyan eder.

## 0. Sayımdan önce görülmüş olan

- TR-13'ün yayımlı satırları: `sayim4` (= TR-13 arşivindeki `ham/sayim_tam_satirlar.json`, 1175 ana şok; dosya
  sha256 `tr13_ham_sha256.txt`'deki arşivden okundu) ve `tr13_tamsayim.json`. Bunlardan aday listesi kodla çıkarıldı:
  `kayit/turetme/tr13d/tr13d_aday.py` → `tr13d_aday.json`. Görülen: konum, M, R, küme, küresel katalogdaki N3bg ve Mc.
- TR-13b'nin 15 olayının z'leri ve TR-13c'nin 5 yeni kümesi (847, 854, 910, 911, 1137) ve sayıları.
- **Görülmedi:** hiçbir bölgesel katalog. Erişim denemesi bile bu commit'ten sonra yapılır.
- Gerçek katalogda hiçbir yerelleşme ölçüsü (V(q), Gini, z) hesaplanmaz; `tr13b_kosu.kos()` çağrılmaz.

## 1. Aday listesi (`tr13d_aday.json`; kodla, el sayımı yok)

TR-13 ana şoku, M ≥ 6,0, sığ doğrultu atımlı (TR-13 §3.1), **temiz önce-pencere** (`oncu_M6_kirli` yanlış; kirlilik
ComCat M ≥ 5,5 havuzundan gelir, katalogla düzelmez), TR-13b ön kaydının 14 kümesinde değil
(397, 160, 303, 395, 1141, 689, 727, 802, 901, 942, 979, 1139, 1035, 1144) ve TR-13'te düşmüş:
- **A (arka plan yetersiz):** küresel en iyi katalogda N3bg[Mc] < 50 ya da Mc kestirilemedi: 873 olay.
- **B (referans geçmiyor):** N3bg ≥ 50 ama `ref_gecer["0.3"]` yanlış: 14 olay.

Toplam **887 olay, 488 küme**; M ≥ 6,5'te **212 olay, 164 küme**. TR-13c'nin geçen kümesine düşen adaylar
işaretlenir (`tr13c_kumesi`). Bölge, dış merkezden sabit kutu sırasıyla atanır (`BOLGE` listesi kodda).

## 2. Denenecek açık bölgesel kataloglar (bölge → sıra)

Yalnız resmî, açık, anonim servisler. Kayıt/giriş/kişisel bilgi formu isteyen servise başvurulmaz, bilgi gönderilmez
("erişim kayıt ister" yazılır). 401/403 aşılmaz; 429'da beklenir; genel User-Agent. Bir bölgede listedeki ilk erişilebilir
katalog kullanılır; ikincisi yalnız ilki erişilemezse ya da olayı kapsamıyorsa.

| Bölge | Katalog (sıra) |
|---|---|
| Japonya | JMA birleşik hiposantr kataloğu (yıllık dosyalar, data.jma.go.jp) |
| Tayvan | CWA; erişilemezse JMA (kapsam kenarı) |
| Kanada (BC) | NRCan FDSN event |
| Türkiye | AFAD olay servisi; KOERI. **Marmara kutusu (39,5–42,0° K, 26,0–31,5° D): yalnız ≤ 2025 ve yalnız sayı; Marmara terimi değildir** |
| Yunanistan-Ege | NOA FDSN event; AUTH |
| İtalya-Adriyatik | INGV FDSN (ISIDe) |
| İzlanda | IMO (açık sorgu servisi) |
| İran-Kafkas | IRSC |
| Yeni Zelanda | GeoNet FDSN (TR-13'te yalnız örnek/kısmi tam kullanıldı; burada tam) |
| Svalbard-Jan Mayen | NNSN (Bergen) FDSN event |
| Şili-Arjantin | CSN |
| Kuzey And | SGC (Kolombiya) FDSN |
| Meksika | SSN (UNAM) |
| Kaliforniya, ABD iç batı, Alaska | **Yeni katalog yok:** NCEDC/SCEDC/AEC/UU/MB zaten ComCat içinde; TR-13 ComCat tam sayımı aynen geçerli (N3bg Mc arttıkça artamaz) |
| Çin-Tibet | CENC kayıt ister (TR-13 §3.1); denenmez |
| Öteki (okyanus sırtları, Pasifik adaları, Endonezya, Filipinler, PNG, Myanmar, Orta Asya, Altay, Kamçatka, Orta Amerika, Karayip, Peru-Bolivya, Afrika, Avustralya) | Açık, makineyle sorgulanabilir bölgesel katalog bilinmiyor: **"katalog yok / denenmedi"** yazılır |

## 3. Sayım ("geçti" = TR-13b §3.1–3.3 aynen)

Her aday ve kullanılan katalog için, dış merkez ve t `sayim4`'ten:
1. İndirme: [t − 10 y, t), R dairesi, büyüklük alt sınırı yok (servis izin verdiği kadar), bitiş < t ve ≤ 2025-12-31.
   Ana şok sonrası hiçbir veri istenmez. 2026 satırı okunurken atılır.
2. Mc_önce = [t − 3 y, t) MAXC + 0,2 (R dairesi, derinlik ≤ 40 km; ≥ 50 olay; 20–49 olayda + 0,3; < 20 → "düşer: Mc
   kestirilemedi"); Mc_ref aynı kuralla [t − 10 y, t − 3 y).
3. §3.1–3.3 (`tr13b_kosu.hazirla` değiştirilmeden): Mc_b = max(Mc_önce, Mc_ref); süzgeç [t − 10 y, t), derinlik
   ≤ 40 km; GK74 m ≥ Mc_b ile indirilen dairede (R); N3bg = [t − 3 y, t) arka planı; N3bg > 100 iken Mc_b += 0,1 ve GK74
   yeniden; son N3bg < 50 → düşer; referans [t − 10 y, t − 3 y) arka planı < N3bg + 5 → düşer.
4. **Geçti** = 3'ün sonunda "tamam". Bilgi sütunu (geçti tanımına girmez): TR-13b §2 süzgeci (Mc_ref ≤ Mc_önce + 0,3 ve
   referans arka planı (m ≥ Mc_önce) ≥ 100).
5. Büyüklük türü (ML, MJMA, Md, Mw …) katalogda nasılsa öyle kullanılır; **dönüştürme yapılmaz** (ölçü yalnız Mc üstü
   olay sayısına bakar); her katalog için tür beyan edilir.
6. Kaba ön eleme (yalnız indirme yükünü azaltmak için, sonucu değiştirmez): [t − 3 y, t) R dairesinde toplam olay < 50
   ise N3bg < 50 kesindir → "düşer" (N3bg ≤ toplam).

## 4. K ve okuma

- **Yeni küme** = TR-13b'nin 14 kümesinde olmayan TR-13 kümesi (`kume`, TR-13 tek bağlantı kuralı). Ayrıca TR-13b'nin 16
  olayıyla doğrudan çakışma (uzaklık ≤ R_i + R_j, |Δt| ≤ 10 y) kodla denetlenir.
- **Birincil K (bağlar):** en az bir **M ≥ 6,5** üyesi geçen yeni küme sayısı.
- **İkincil K (yazılır):** M ≥ 6,0 üyesi geçen yeni küme sayısı; ayrıca TR-13c'nin 5 kümesiyle birleşimi.
- Bölge tablosu: aday olay/küme, katalog, erişim, geçen olay/küme.

## 5. Görülebilir en küçük etki (yalnız kaba ölçekleme; **tahmindir**, yapay hesap yapılmaz)

TR-13c_SAYIM'daki K–MDE ilişkisi: K 10 → 0,39 (büyük R, TR-13b bileşimi) ya da 0,58 (R = 50 km, TR-13c K × 2),
K 18 → 0,32. Kaba ölçek MDE ∝ 1/√K:
- MDE(K) ≈ 0,39 √(10/K) (iyimser) … 0,58 √(10/K) (R = 50 km ağırlıklıysa).
- f ≈ 0,25 için K ≈ 24 (iyimser) … 54; f ≈ 0,2 için K ≈ 38 … 84. K 18 → 0,32 noktasından: f 0,25 → K ≈ 29, f 0,2 → K ≈ 46.
- Kaynak: f ≈ 0,2 TR-13 benzetimindeki **tahmin**dir (ESIK-DAYANAGI); ×0,5 / ×2 duyarlılığı: K ∝ 1/f², yani etki
  yarıya inerse K 4 katı, iki katına çıkarsa K/4 gerekir.
- R = 50 km'lik (M < 6,5) üyelerde yapay üretecin kalibre edilemediği (TR-13c) ayrıca yazılır.

## 6. Dal kuralı (birincil K bağlar; ikincil K yazılır)

- **Yeni K ≥ 20:** TR-13d ön kaydı önerilir (ayrı iş; burada yazılmaz).
- **10 ≤ yeni K ≤ 19:** TR-13b benzeri sınırlı koşu seçeneği, §5'teki kaba MDE ile yazılır.
- **Yeni K < 10:** aday durur.
- Hiçbir aday elenmez. Bu bir H0 ya da yerelleşme hükmü değildir.

## 7. Körlük

2026 ve sonrası veri yok; ana şok sonrası pencere yok; Marmara GNSS'e dokunulmaz; İstanbul için olasılık yazılmaz;
dış servislere e-posta, ad ya da proje bilgisi gönderilmez. Alt ajan yok. Harcama 0 €.
