#!/usr/bin/env python3
"""TR-5b İNCELEME-2: pilot P1 hacmi, kontrol düzeyinde P1 (1. adayın BÜTÜN istasyonları) ile istasyon düzeyi (en yakın
istasyon) karşılaştırması. Vekil: her volkaniksiz olayın 1. adayı (gerçek seçim aşama 0'da). Varsayımlar
`tr5b_liste_s2.py` hacim_hesap ile aynı (1,3 bayt/örnek, 4 saat/gün, 3 bileşen, en düşük >= 10 sps).
Kullanım: python3 -I -B inc2_p1_hacim.py
"""
import collections, datetime as dt, json, os

BURASI = os.path.dirname(os.path.abspath(__file__))
L = json.load(open(os.path.join(os.path.dirname(BURASI), 'tr5b_liste_s2.json')))['olaylar']
D = dt.date.fromisoformat


def hacim(kal):
    pen = collections.defaultdict(list); sps = {}; mk = {}
    for s, m, r, a, b in kal: pen[s].append((D(a), D(b))); sps[s] = r; mk[s] = m
    tb = collections.Counter(); ig = 0
    for s, iv in pen.items():
        m = []
        for x, y in sorted(iv):
            if m and x <= m[-1][1] + dt.timedelta(days=1): m[-1][1] = max(m[-1][1], y)
            else: m.append([x, y])
        n = sum((y - x).days + 1 for x, y in m); ig += n
        tb[mk[s]] += n * 4 * 3600 * sps[s] * 1.3 * 3 / 1e12
    return dict(istasyon=len(pen), istasyon_gunu=ig, TB=round(sum(tb.values()), 4),
                merkez_TB={k: round(v, 4) for k, v in tb.most_common()})


ana = [r for r in L if not r['volkanik']][:24]
yakin, hepsi = [], []
for r in ana:
    c = r['kontrol'][0]
    s0 = min(c['istasyon'], key=lambda s: s['uzaklik_km'])
    yakin.append((s0['ist'], s0['merkez'], s0['sps_min'], *r['pencere']))
    hepsi += [(s['ist'], s['merkez'], s['sps_min'], *r['pencere']) for s in c['istasyon']]
out = dict(istasyon_duzeyi_en_yakin=hacim(yakin), kontrol_duzeyi_butun_istasyonlar=hacim(hepsi))
json.dump(out, open(os.path.join(BURASI, 'inc2_p1_hacim.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
