# Kol TK — zamana bağlı tetiklenme ve kısa–orta vade öncü sinyalleri (11 Kasım 2026)

Not: Bu oturumda alt ajan aracı yoktu; tarama tek elden yapıldı (Crossref, OpenCitations, WebSearch). OpenAlex kredisi harcanmadı.
"Özetten" = yalnız özet okundu; "başlıktan" = yalnız künye doğrulandı. Tam metin okunan tek iş: Biondini 2023 (açık PDF).

## (a) Tarama özeti

Altı aile tarandı: öncü şok ayrımı, orta vade hızlanma/sessizlik, geodezik geçiciler, sinirsel nokta süreçleri, yük modülasyonu, sismik olmayan öncüler. 56 DOI doi.org üzerinden çözdürüldü (`TK.doi.txt`).

Köprü ölçüleri (OpenCitations v2, `bosluk_olc_v3.py`; tohum kümesine atıf yapan işlerin kesişimi):

| Köprü | Küme boyları | k | Jaccard | Not |
|---|---|---|---|---|
| EEPAS × Marmara | 162 / 625 | 2 | 0,0025 | İkisi de genel derleme (Tiampo 2012, Mangira 2019); uygulama yok |
| EEPAS × Türkiye (istatistik) | 162 / 512 | **0** | 0 | |
| EEPAS × ETAS (pozitif kontrol) | 162 / 2102 | 85 | 0,039 | |
| EEPAS × CSEP (pozitif kontrol) | 162 / 194 | 34 | 0,106 | |
| b-trafik ışığı × Marmara | 406 / 625 | 9 | 0,0088 | Kesişim: hazırlık süreci makaleleri; kural uygulaması yok |
| b-trafik ışığı × Türkiye | 406 / 512 | 15 | 0,017 | |
| Öncü–ETAS sapması × Marmara | 143 / 625 | 10 | 0,013 | Durand 2020, Martínez-Garzón 2024/2026 |
| Sinirsel nokta süreci × Marmara | 56 / 625 | **0** | 0 | (Alhan–Khabat 2026 ön baskısı OpenCitations'ta henüz yok) |
| Ön-kayma × Marmara | 116 / 625 | 1 | 0,0014 | |
| ETAS × Marmara (pozitif kontrol) | 2102 / 625 | 15 | 0,0055 | Alanın kendisi seyrek; k≤2 "boşluk", k≈10 "değinilmiş" okunmalı |

Aile başına ileriye dönük kanıt durumu:

1. **b-değeri trafik ışığı.** Gulia–Wiemer 2019: 58 dizide geriye dönük %95. Ridgecrest sözde-ileriye sınavı (Gulia 2020) Dascher-Cousineau 2020 tarafından parametre seçimine duyarlı bulundu (yorum/yanıt 2021). van der Elst 2021 (özetten): yansız kestirimde sinyal küçülüyor, "gerçek zamanlı alarm için fazla ince olabilir". Lombardi 2022/2024 (başlıktan): İtalya'da b anomali anlamlılığı tartışmalı. Gulia 2024 (özetten): b-pozitifli otomatik sürüm, yine geriye dönük, +6 dizi. Bağımsız ileriye dönük skor bu taramada bulunamadı. Türkiye/Marmara'ya kural olarak uygulanmış iş bulunamadı.
2. **Öncülerin ETAS'tan sapması.** Seif 2018, Petrillo–Lippiello 2020 (özetten: ETAS öncü sayısını az kestiriyor), Moutote 2021 (özetten: 53 ana şokun 10'unda anormal etkinlik, yalnız 3'ü ana şoka özgü). Marmara: Durand 2020 (2019 Silivri, M4,7 → M5,8; şablon eşleştirmeyle iki ölçekli hazırlık, geriye dönük tek olay). Nisan 2025 M6,2 dizisi için ETAS/b sınavı içeren hakemli iş bulunamadı (Martínez-Garzón 2026 Science, özetten: 15 yılda doğuya ilerleyen M>5 dizisi, betimsel).
3. **Orta vade.** EEPAS: Yeni Zelanda, Kaliforniya, Japonya, İtalya'da kurulmuş. İtalya (Biondini 2023, tam metin): 2012–21 sözde-ileriye, M≥5,0, N=27; 3 ayda ETAS, 6 ay–10 yılda EEPAS önde; fark yalnız 5 ve 10 yılda anlamlı, yalnız ana şoklarda hiçbir vadede anlamlı değil. Yeni Zelanda/Kaliforniya CSEP ileriye dönük sayıları (Rhoades 2018, Schneider 2014, Strader 2017) ödeme duvarı nedeniyle okunamadı; **sayısal üstünlük iddiası doğrulanamadı**. PI: RELM'e girdi (Holliday 2007), sonucu Zechar 2013'te (başlıktan; okunmadı, sıralama bu dosyada iddia edilmiyor). AMR: Hardebeck 2008 istatistiksel olarak anlamsız. RTL ve nowcasting için bağımsız ileriye dönük skor bulunamadı; nowcasting Türkiye kentlerine uygulanmış (Devi 2026, başlıktan), skorlanmamış. **Türkiye'de EEPAS uygulaması bulunamadı** (k=0; WebSearch boş). Bu, yokluğun kanıtı değil, bu taramanın sonucudur.
4. **Geodezik geçiciler.** Bedford 2020 ve Bletery–Nocquet 2023 geriye dönük yığma; Bletery–Nocquet 2025 (özetten) ortak-mod süzgecinin sinyali sildiğini kabul ediyor, tartışma açık. Bradley–Hubbard eleştirisi hakemli değil (blog), DOI yok. Marmara: Martínez-Garzón 2019, Bocchini 2022, Neyrinck 2024 — toplam bir avuç (≤5) geçici. "Durand 2022" künyesi bu taramada bulunamadı.
5. **Makine öğrenmesi.** RECAST (özetten): üstünlük yalnız eğitim kümesi >10⁴ olayda. Stockman 2023 (özetten): M3+ hedefte ETAS ile denk; kazanç eksik katalog toleransından. Alhan–Khabat 2026 (ön baskı, özetten): Marmara'da sızıntı denetimli ETAS×ML melezi ETAS üstüne sıralama becerisi eklemiyor; olabilirlik üstünlüğü puanlama yapıntısı; 2025 M6,2 hücresi üst %1–2'de ama ≈220 benzer alarm boş.
6. **Yük modülasyonu.** Martínez-Garzón 2023 (özetten): Armutlu hidrotermal alanında 6 ay, mikrosismisite, 30–300 nanogerinim. Büyüklük ve bölge dar.
7. **Sismik olmayan öncüler.** İleriye dönük hakemli skor bulunamadı (radon için Woith 2015 derlemesi var; başlıktan, içeriği okunmadı). Aday yok.

## (b) Aday tablosu

### TK-1 — EEPAS-Türkiye/Marmara: orta vade (1–5 yıl) ön kayıtlı sözde-ileriye sınav — **öner**

- **Soru:** "Her deprem ölçeğine göre bir öncüdür" modeli, Türkiye'de 1 ve 5 yıl vadede canlı ETAS'ın çok yıllık benzetim tahminini ve durağan düzleştirilmiş sismisiteyi log skorda geçiyor mu?
- **Neden yeni:** Türkiye'de kurulmamış (köprü k=0). En yakın işler: Biondini 2023 İtalya (10.1093/gji/ggad123), Rhoades 2007 Kaliforniya (10.1785/gssrl.78.1.110), Rastin 2021 (10.3390/app112110215). ETAS-TABAN kapanışından farkı: arka plan/tetiklenme payı ağırlığı değil, yıl–on yıl ölçekli ayrı bir çekirdek (öncü büyüklüğü → ana şok büyüklüğü, süre, alan).
- **Zaman ekseni:** yıl; hedef M≥5 (sınanabilir), M6+ yalnız ölçekleme ile dışa uzatma (sınanamaz).
- **Sınama:** Parametreler ≤31.12.2015 kataloğuyla dondurulur (girdi M≥3,0; ψ ölçekleme katsayıları ya yayımlanmış değerlerden aktarılır ya da ≤2015'te uydurulur; ikisi ayrı ön kayıt). Hedef: Türkiye 2016–25 M≥4,95, N≈90–100; 2020 ve 2023 kümeleri yüzünden etkin N≈40–50. Vadeler 3 ay / 1 yıl / 5 yıl. Rakipler: durağan düzleştirilmiş sismisite, canlı ETAS (benzetimle), ETAS+EEPAS karışımı. H1: 1 yılda en iyi rakibe göre ≥ +0,3 nat/olay; H0: ≤0. Rapor ayrı: tüm hedefler ve yalnız ana şoklar.
- **Güç (tek yanlı %5, normal yaklaşım):** δ=0,3 nat, σ=1,0–1,5: N=95 → 0,90–0,62; N=40 → 0,60–0,35. δ=0,5: N=40 → 0,94–0,68. δ=0,1 hiçbir N'de >0,25. Yani yalnız İtalya'daki uzun vade büyüklüğünde bir etki ayırt edilir; küçük etki "ayırt edilemez" çıkar. Yalnız Marmara (M≥3,95, onlarca olay): δ=0,3'te 0,25–0,6 → Marmara karar kümesi olamaz, yalnız aktarım denetimi. M≥6 (≈10 olay): güç ≤0,3, ön kayıtta "raporlanır, hüküm verilmez".
- **Sızıntı riski:** katalog büyüklük homojenleştirmesi sonradan değişmiş olabilir (dondurulmuş anlık görüntü şart); ψ katsayılarını 2016+ veriye bakarak seçmek; 2023 dizisinin skoru tek başına sürüklemesi (S-7 ve CRS-ETAS dersleri: tek dizi çıkarılınca sonuç ayrıca raporlanır).
- **Veri:** AFAD/KOERI kataloğu, projede mevcut; açık. Kod: Chung 2025 açık Python gerçeklemesi (arXiv 2512.13064; depo adresi doğrulanmadı), Biondini Matlab'ı.
- **Maliyet/süre:** 0 €, 3–5 gün. **Tür:** istatistik.
- **Hüküm:** öner. Gerekçe: kolun tek gerçek boşluğu, veri hazır, güç Türkiye ölçeğinde sınırda ama var. Beklenti düşük tutulmalı: İtalya'da ana şoklarda kazanç anlamsızdı. 8 Kasım "yeni istatistik adayı açılmaz" kararıyla çelişip çelişmediğine Erdem karar vermeli.

### TK-2 — b-pozitif trafik ışığı ve öncü–ETAS sapması: Türkiye M≥5,5 dizilerinde gölge kural — **bekle**

- **Soru:** Otomatik b-pozitif kuralı (Gulia 2024) bir M≥5,5 sonrası "daha büyüğü gelir" olasılığını canlı ETAS'ın verdiğinden iyi ayırıyor mu?
- **Neden yeni:** Türkiye'de kural olarak uygulanmamış; en yakın: Gulia 2024 (10.1785/0220240163), van der Elst 2021 (10.1029/2020jb021027), Durand 2020 (10.1785/0220200110).
- **Zaman ekseni:** gün–hafta; M6+ sonrası.
- **Sınama/güç:** Türkiye 2016–25 M≥5,5 dizisi ≈25–30; taban oran ≈%5 ile beklenen "daha büyüğü geldi" sayısı 1–2. Bu sayıyla güç ≤0,15: **önceden ayırt edilemez**. Ayrıca kural 10 km içinde yüzlerce Mc üstü olay ister; Marmara açık denizinde 2019 dizisi bunu zor karşılar. 2019 ve 2025 iki olay, sınav değil anekdot.
- **Veri:** KOERI/AFAD, açık. **Maliyet:** 0 €, 2 gün (kuralı dondurmak). **Tür:** istatistik.
- **Hüküm:** bekle. Kural şimdi dondurulup ileri test defterine skorsuz gölge satırı olarak yazılabilir; hüküm ancak ≥10 pozitif dizi birikince (Türkiye'de on yıllar; küresel havuz gerekir, o da kör veri kuralına takılır).

## (c) Elenenler

| Kimlik | Fikir | Neden |
|---|---|---|
| TK-E1 | Marmara kuyu gerinimi / yavaş kayma geçicileri → olasılık çarpanı | S-7 ile aynı mekanizma; yeniden açma şartı (bağımsız doğrulama seti) sağlanmıyor: Marmara'da ≤5 geçici, güç yok |
| TK-E2 | Sinirsel nokta süreci (RECAST türü) Marmara | Alhan–Khabat 2026 aynı soruyu sızıntı denetimiyle sordu: ETAS üstüne sıralama becerisi yok; RECAST >10⁴ olay ister |
| TK-E3 | Deniz seviyesi/atmosfer basıncı ortak değişkeni | %10–20 hız modülasyonu ≈0,005 nat/olay bilgi kazancı demek; M≥3,95'te güç ≈0,05; DD-5 ile aynı sonuç, M6+ zaman eksenine dokunmaz |
| TK-E4 | PI, RTL, AMR, nowcasting Türkiye | Hiçbiri bağımsız ileriye dönük testte tabanı geçmedi (AMR çürütüldü); nowcasting yenilenme türü, projede BPT zaten Poisson'a yenildi |
| TK-E5 | Doğuya ilerleyen M>5 göçü (Martínez-Garzón 2026) ve ay ölçekli hazırlık geçicileri (Kwiatek 2023, Picozzi 2023) | Geriye dönük, 1–5 olay; kural yazılsa bile N yok |
| — | Elektromanyetik, radon, termal | İleriye dönük hakemli skor bulunamadı |

## (d) Dürüst sınır

- Bu kolda yıl ölçeğinde çalıştığı ileriye dönük gösterilmiş yöntem yok. EEPAS'ın en iyi yayımlanmış sonucu sözde-ileriye, N=27, ana şoklarda anlamsız.
- TK-1 olumlu çıksa bile sınanan şey M≥5'tir; M6+ ve M7+ için söylenebilecek olan ölçekleme varsayımıdır, kanıt değil.
- EEPAS'ın Yeni Zelanda/Kaliforniya CSEP sayıları okunamadı; "CSEP'te ETAS'ı geçti" cümlesi bu dosyada kurulmuyor.
- Etkin N (kümelenme sonrası) kabaca tahmin edildi; ön kayıttan önce gerçek katalogdan sayılmalı. σ=1,0–1,5 nat/olay varsayımdır.
- Türkiye'de EEPAS yokluğu üç araçla arandı; Türkçe tezler ve bildiriler taranmadı.
