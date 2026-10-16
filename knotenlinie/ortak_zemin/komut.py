"""Ortak zemin üretim komutları; bütün çıktı yolları açıkça seçilebilir."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .ayar import ayarla
from .dogrulama import dogrula
from .veri import VERI, kataloglari_yaz, json_yaz, sha256
from knotenlinie.yollar import KOSU


def readme_yaz(ortak):
    ortak = Path(ortak)
    names = ['italya_katalog_le2015.csv', 'italya_izgara.csv', 'etas_italya_le2010.json',
             'etas_italya_le2005.json', 'kataloglar.json', 'dogrulama_italya_2011_2015.json',
             'dogrulama_italya_2011_2015_m3.95_inf.json']
    rows = ['| Dosya | SHA256 |', '|---|---|']
    rows += [f'| `{name}` | `{sha256(ortak / name)}` |' for name in names if (ortak / name).exists()]
    text = '''# Ortak zemin (deney T) — ≤2015 katalog / ≤2010 düz ETAS

İtalya: HORUS 1960–2015 homojen Mw, CSEP İtalya XML mask=1 desteği,
0≤derinlik≤70 km. HORUS'a ayrıca ML→Mw dönüşümü yapılmaz.

Katalog sütunları `zaman,enlem,boylam,derinlik,mw`; UTC ISO zaman, derinlik km.
Hücreler `boylam_min,boylam_max,enlem_min,enlem_max`, alt dahil/üst hariç,
CSV satır sırası modelin oran satır sırasıdır. `kataloglar.json` ham girdi
SHA256'larını, okuyucu raporunu, destek/sığlık kesimlerini ve sayımları saklar.

```python
import numpy as np
import pandas as pd
from knotenlinie.ortak_zemin.veri import katalog_oku, VERI
from knotenlinie.ortak_zemin.arayuz import model_yukle
ortak = VERI / 'ortak'
katalog = katalog_oku(ortak / 'italya_katalog_le2015.csv')
izgara = pd.read_csv(ortak / 'italya_izgara.csv')
model = model_yukle('italya', ortak)
a = pd.Timestamp('2011-01-01', tz='UTC')
b = a + pd.Timedelta(days=1)
gecmis = katalog[katalog.zaman < a]
orani = model.beklenen(a, b, gecmis, izgara, np.array([4.95, np.inf]))
# Orani: (hücre, büyüklük), bu örnekte günlük M≥4.95 beklenen sayısı.
```

`knotenlinie.ortak_zemin.arayuz.beklenen(...)` aynı imzayla bölgeyi tam/alt hücre
desteğinden seçer. Açık seçim için `model_yukle('italya').beklenen` tercih
edilir. Geçmişte başlangıç anı/future satır varsa (Mc altında olsa bile) hata
verir; çalışma okuyucusu ≤2015 kapısını korur. Önceki ayar başlangıcından eski
olaylar ve Mc altı olaylar modelde anne olmaz. Eş zamanlı olaylar anne değildir.
Son büyüklük kenarı +inf olabilir; Mc altına ekstrapolasyon yoktur.

## Zamansal ayar tabanları

```python
from knotenlinie.ortak_zemin.arayuz import ayar_tabani
ayar = ayar_tabani(son="2006-01-01")  # ızgaradan bölge seçen .beklenen(...)
dogrulama = ayar_tabani(son="2011-01-01")
# Açık bölge: ayar_tabani("italya", son="2006-01-01")
```

Deneyler bileşen ağırlıklarını **2006–2010** olaylarında ilk modelle seçer,
**2011–2015** doğrulamasında ağırlıkları sabit tutup ikinci modeli kullanır.
≤2010 modeli 2006–2010'da kullanmak ayar sızıntısıdır; arayüz ayar bitişinden
önce tahmini reddeder. Geçmiş her gün gün-başı öncesi gözlenen olayları içerir,
ETAS parametreleri ve arka plan sabittir. Bu dosyalar ağırlıkları seçmez.

Arka plan km'de izotropik **Gauss KDE + düzgün zemin**dir. Her Gauss kutuya
koşullanır; analitik CDF hücre kütlesi 0.1° parça-sabit yoğunluğa çevrilir.
MLE'deki olay yoğunluğu ve tahmin hücre integrali aynı yüzeydendir. Bantlar
5/10/20/40/80 km, düzgün kütle payları %0.1/0.5/1/2/5/10; yalnız zamansal
holdout konum olabilirliğiyle seçilir, sonra yeniden kurulur:

- ≤2010: KDE ≤2005'ten; bant/zemin **2006–2010**'dan; yeniden kurulum ≤2010.
- ≤2005: sızıntısız iç kat; KDE ≤2000'den, seçim **2001–2005**'ten, yeniden
  kurulum ≤2005. 2006–2010 bant/zemin seçimine de girmez.

Seçilen (bant,zemin): ≤2005 İtalya (20 km,%5);
≤2010 İtalya (10 km,%1). `arka_plan.secim` bütün adayları,
kesim zamanlarını ve sayımlarını saklar. Kütle dış dikdörtgende bir; hedef
maskeye kesildiğinde tekrar normalize edilmez. Zemin gizli floor değildir.

Parametre JSON'ları `knotenlinie.etas.model.mle_uzay_zaman` olabilirliğinin çıktısını,
KDE yüzeyini, metriği, Mc/tamlık pencerelerini, b'yi, başlangıç yılını ve gerçek dallanmayı
içerir. b'nin `dm` değeri yalnız Mc üstü ayar verisinden ölçülür: bütün
olayların uyduğu en kaba ondalık ızgara (1..1e-6); hiçbiri uymuyorsa dm=0.
`b.cozunurluk` ızgara uyumlarını, örnek sayısını ve en küçük farkı kaydeder.
İtalya dm=0.01; varsayılan 0.1 düzeltmesi kullanılmaz.
`gr_ayar_paylari` büyük-M ekstrapolasyonunun gözlenen ayar payına oranını verir.
Eski-b parametreleri `eski-b/` arşivindedir, aktif taban değildir.
İtalya 1985 başlangıcı Mc=3.1 korunmuştur.
Ayar aralıkları [başlangıç,son) olup son=2006 veya 2011'dir; hiçbir ileri
olay Mc/b/KDE/ETAS seçimine girmez. Çift bütçesi aşılırsa Mc yükseltilmez.
2011–2015 tamlık/b/parametre seçimine girmez.
Log10 üretkenlik α'sı için sonsuz GR dallanması
`K*c**(1-p)/(p-1)*b/(b-alpha)`; α<b gerekir. α<β kontrolü bunun yerine geçmez.
Yeni serbest MLE İtalya ≤2005 sonunda süperkritik çıktı. Aynı
olabilirlik `knotenlinie/ortak_zemin/mle.py` ile SLSQP altında α≤b−1e−6 ve
n≤1−1e−6 kısıtlarında yeniden optimize edildi; K sonradan kırpılmadı.
Bu sonuç n≈0.999999 ile **aktif sınırdadır**, sağlam biçimde alt-kritik
olduğu iddia edilmez; doğal serbest Hessian std'si sınırda güven aralığı değildir.
İtalya ≤2010 n=0.803499. `*_serbest.json` ve `*_deneme_*.json` tanıdır,
taban olarak yüklenmez. `knotenlinie/etas/` değişmedi.

Tahmin sabit gün-başı geçmişinden **doğrudan** tetikleme integrali + KDE
arka planıdır. Gelecekteki kız olayları eklenmez; günlük çağrıda yalnız önceki
günlerden gözlenenler eklenir. Uzayda midpoint değil mevcut gerçek hücre
integrali kullanılır, dışarı taşan kütle geri normalize edilmez. Her model
kendi sabit ayar metriğini kullanır. Yeni arka planın boş hücresi yoktur;
ölçümde eski ham histogram boşluğu ayrıca sayılır ve en küçük λ raporlanır.

**Açık bilimsel kapı:** olaylar maskeli bölgededir ama değiştirilmemiş mevcut
MLE telafi integrali bölgenin dış dikdörtgeni üstündedir. Tahmin hedef maskeye
kesilir. Böylece maskesiz MLE'den maskeli tahmine geçiş eksik olaylı dış alanı
içerir; bu JSON'lar tam maskeli MLE veya kör önkayıt dondurması değildir.
Tam maskeli kompansatör ayarı ayrı skor-kodu görevi/incelemesi gerektirir.
Bütün deneyler bu **aynı geçici tabanı** kullanabilir; yerleşik modeli geçtiği
iddia edilmez. Bağımsız skor-kodu incelemesi ayrıca yapılır.

Doğrulama JSON'ları 2011-01-01–2016-01-01 (son hariç), 1826 günlük bağımsız
hücre Poisson logL, log(n!) dahil ve tek [4.95,+inf) büyüklük kutusu verir.
Ek İtalya `dogrulama_italya_2011_2015_m3.95_inf.json` satırı [3.95,+inf)
ile seçilmiş bileşenin doğrulamasında kullanılır.
Bileşen ağırlık **seçimi** bu doğrulamada değil, 2006–2010 bölmesindedir.
İtalya [4.95,+inf) satırı yalnız önceki teslimle süreklilik içindir.
Bu mekânsal+sayısal satırdır; CSEP'in 0.1M çoklu kutulu logL'si değildir. Farklı kutu düzeninde sayılar yeniden skorlanır.
Gün içi gözlenen olay tetikleyici olarak aynı güne sokulmaz. Ayar bu doğrulama
sonuçlarına göre seçilmez. `IG/SE/p=null`: bu dosyalar taban satırıdır.

CSEP XML deney H'nin 2026-10-05 indirmesidir (scripts/tabanlar_indir.py):
https://raw.githubusercontent.com/cseptesting/italy2010_experiment/ecb696c3ee06f2bb6a38c7c275d8486fcb6e505b/models/akinci.HAZFX_BPT.italy.10yr.2010-01-01.xml
Girdi SHA256: c0235baa6c9b579b45accd2e0ec9f25758ca43364cd724a1cd10999ebc74effe.
HORUS kaynak kaydı indirme MANIFEST.jsonl dosyasındadır;
`kataloglar.json` bu teslimin ham dosya hashlarını ayrıca sabitler.

## Teslim hashları

'''
    (ortak / 'README.md').write_text(text + '\n'.join(rows) + '\n', encoding='utf-8')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('adim', choices=['katalog', 'ayar', 'dogrulama', 'readme'])
    parser.add_argument('--ortak', type=Path, default=VERI / 'ortak')
    parser.add_argument('--bolge', choices=['italya'], default='italya')
    parser.add_argument('--horus', type=Path, default=VERI / 'kesik-2015/horus')
    parser.add_argument('--csep', type=Path,
                        default=VERI / 'tabanlar/akinci.HAZFX_BPT.italy.10yr.2010-01-01.xml')
    parser.add_argument('--maks-cift', type=int, default=None,
                        help='Tüm çiftler; varsayılan İtalya 30m')
    parser.add_argument('--maksiter', type=int, default=400)
    parser.add_argument('--son', choices=['2006-01-01', '2011-01-01', 'ikisi'], default='ikisi')
    parser.add_argument('--mc-alt', type=float)
    parser.add_argument('--olcum', type=Path,
                        default=KOSU / 'T/OLCUM2.json')
    args = parser.parse_args(argv)
    names = [args.bolge]
    if args.adim == 'katalog':
        kataloglari_yaz(args.horus, args.csep, args.ortak)
    elif args.adim == 'ayar':
        ends = ['2006-01-01', '2011-01-01'] if args.son == 'ikisi' else [args.son]
        for end in ends:
            for name in names:
                ayarla(name, args.ortak, son=end, maks_cift=args.maks_cift,
                       maksiter=args.maksiter, mc_alt=args.mc_alt)
    elif args.adim == 'dogrulama':
        rows = []
        for name in names:
            rows.append(dogrula(name, args.ortak))
            if name == 'italya':
                rows.append(dogrula(name, args.ortak, m_kenarlar=(3.95, float('inf'))))
        args.olcum.parent.mkdir(parents=True, exist_ok=True)
        json_yaz(args.olcum, {'deney': 'T', 'olcumler': rows,
                             'bilesen_m_alt': {'italya': 3.95},
                             'agirlik_ayar_baslangic': '2006-01-01',
                             'agirlik_ayar_bitis_haric': '2011-01-01',
                             'agirlik_ayar_tabani_son': '2006-01-01',
                             'dogrulama_tabani_son': '2011-01-01',
                             'kor_pencere_okundu': False,
                             'bagimsiz_inceleme': 'b ve arka plan düzeltildi; aynı inceleyicinin yeniden kontrolü bekleniyor'})
    else:
        readme_yaz(args.ortak)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
