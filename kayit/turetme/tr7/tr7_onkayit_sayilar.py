#!/usr/bin/env python3
"""TR-7 ön kayıt sayıları ve dondurulan tarama listesi (yalnız üstveri; dalga formu okunmaz, ağa çıkılmaz).

Girdi (bu dizin): tr7_varlik.csv, tr7_varlik_ozet.json, tr7_istasyon.csv, tr7_tetikleyici.csv;
depo dışı: ComCat önbelleği comcat_m75.csv (sha256 aşağıda denetlenir; tr7_sayim.py'nin çektiği yanıt).
Çıktı: tr7_dondurulan_liste.csv (istasyon × tetikleyici × segment, pencereler), tr7_onkayit_sayilar.json.
Kurallar: kayit/onkayit/TR-7_tetiklenmis-tremor_ONKAYIT.md §3, §4, §8.

Pozitif kontrol (Parkfield) istasyon listesi: NCEDC ve EarthScope fdsnws/station yanıtları (kanal düzeyi, metin,
35,3-36,6° K, 121,3-119,6° B, 2011-03-11T05:00-08:00), Marmara ile aynı seçim kurallarıyla; PB kuyu ağı ve
derinliği >= 50 m olan kanallar dışarıda (Marmara'da kuyu sensörü yok). Çıktı: tr7_parkfield_liste.csv.

Sürüm 2 (İNCELEME-1 E2, E3, Ö3, K7): Marmara listesine her (tetikleyici, segment) içinde segment izine uzaklık
(`iz_km`, `nokta_cizgi`), sıra (`iz_sira`; eşitlikte ağ, istasyon alfabetik) ve `ilk12` sütunları; Parkfield listesine
E2 varlık yoklamasının (`tr7_parkfield_varlik.csv`) `var_R`, `var_W` sütunları ve ikisinde de var olanlar arasında
`iz_sira`/`ilk12`. Listeye satır eklenmez, çıkarılmaz: 12 sınırı koşuda örtüden geçen istasyonlara yeniden uygulanır.
json'a: X_min (α = 0,05 ve 0,05/3), rastlantıyla ≥1 algılama, istasyon sayıları (tümü / 12 sınırıyla), R+W ortalamaları.

Kullanım: python3 -I -B tr7_onkayit_sayilar.py <comcat_m75.csv> [--parkfield <ncedc.txt> <earthscope.txt>] [--yaz]
"""
import csv, datetime as dt, hashlib, json, math, os, sys
from collections import defaultdict

BURADA = os.path.dirname(os.path.abspath(__file__))
COMCAT_SHA = 'ae9117d0fe64aae4be19a45a0151e830bd2b35de40056e3b322a3c4a06833e61'
V_ON, V_ARKA, KUYRUK, BASVURU_S = 5.0, 2.8, 600.0, 3600.0
N_IST = 3
KAHRAMANMARAS = {'us6000jllz', 'us6000jlqa'}                       # bilgi satırı, ana sayıma girmez
WHARTON = ('official20120411083836720_20', 'usp000jhjb')          # tek bağımsız birim
ANA_SEG, IKINCI_SEG = ['S1', 'S2', 'S3'], ['S4', 'S5', 'S6', 'S7']
SON_GUN = dt.datetime(2026, 1, 1)


N_SINIR = 12                                                       # E3: pencere başına ize en yakın en çok 12 istasyon
SEGMENT = {                                                        # tr7_sayim.py ile aynı izler (boylam, enlem)
    'S1': [(26.20, 40.55), (26.90, 40.62), (27.50, 40.80)],
    'S2': [(27.50, 40.80), (28.00, 40.82), (28.60, 40.85), (29.00, 40.83)],
    'S3': [(29.00, 40.83), (29.30, 40.72), (29.90, 40.72)],
    'S4': [(29.90, 40.72), (30.30, 40.70), (30.80, 40.75), (31.20, 40.80)],
    'S5': [(31.20, 40.80), (31.60, 40.73), (32.20, 40.80), (32.60, 40.87)],
    'S6': [(32.60, 40.87), (33.30, 40.90), (34.00, 41.02)],
    'S7': [(30.30, 40.50), (29.50, 40.43), (29.10, 40.42), (28.30, 40.33), (27.50, 40.25), (27.00, 40.10),
           (26.60, 39.70)],
}


# Parkfield SAF izi (kaba, ±5 km): Parkfield'ın ~30 km KB'sından Cholame'nin GD'suna (Hill vd. 2013 tremor kesimi)
PARKFIELD_IZ = [(-120.80, 36.20), (-120.50, 35.97), (-120.35, 35.83), (-120.20, 35.65)]


def nokta_cizgi(la, lo, iz):
    k = math.cos(math.radians(la)) * 111.195
    px, py = lo * k, la * 111.195
    en = 1e9
    for (x1, y1), (x2, y2) in zip(iz[:-1], iz[1:]):
        ax, ay, bx, by = x1 * k, y1 * 111.195, x2 * k, y2 * 111.195
        dx, dy = bx - ax, by - ay
        t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
        en = min(en, math.hypot(px - (ax + t * dx), py - (ay + t * dy)))
    return en


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def hav(la1, lo1, la2, lo2):
    p1, p2 = math.radians(la1), math.radians(la2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lo2 - lo1) / 2) ** 2
    return 2 * 6371.0 * math.asin(min(1, math.sqrt(a)))


def birim(olay):
    return 'WHARTON2012' if olay in WHARTON else olay


def bant(n):
    return 'tam' if n >= 8 else ('zayif' if n >= 5 else 'veri yok')


def binom_ust(n, p, x):
    """P(Bin(n, p) >= x)."""
    return sum(math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(x, n + 1))


def cp_ust(f, N, a=0.05):
    """Clopper–Pearson tek yanlı %95 üst sınırı (ikiye bölme, yalnız standart kitaplık)."""
    if f >= N:
        return 1.0
    lo, hi = f / N, 1.0
    for _ in range(200):
        m = (lo + hi) / 2
        # P(Bin(N, m) <= f) = a
        cdf = sum(math.comb(N, k) * m ** k * (1 - m) ** (N - k) for k in range(0, f + 1))
        lo, hi = (m, hi) if cdf > a else (lo, m)
    return (lo + hi) / 2


def main():
    comcat = sys.argv[1]
    if sha(comcat) != COMCAT_SHA:
        sys.exit('DUR: ComCat önbelleği sha256 uyuşmuyor')
    ev = {}
    for r in csv.DictReader(open(comcat, encoding='utf-8')):
        ev[r['id']] = dict(t=dt.datetime.strptime(r['time'].replace('Z', ''), '%Y-%m-%dT%H:%M:%S.%f'),
                           la=float(r['latitude']), lo=float(r['longitude']), M=float(r['mag']), yer=r['place'])
    ist = {(r['ag'], r['istasyon']): (float(r['enlem']), float(r['boylam']))
           for r in csv.DictReader(open(os.path.join(BURADA, 'tr7_istasyon.csv'), encoding='utf-8'))}
    oz = json.load(open(os.path.join(BURADA, 'tr7_varlik_ozet.json'), encoding='utf-8'))
    seg_ad = {s.split()[0]: s for s in oz['segment']['x1']}
    tau = {(o, k): t for k, s in seg_ad.items() for o, t, _ in oz['segment']['x1'][s]['olaylar']}

    # ---- 1. dondurulan liste: (tetikleyici, segment) çiftinde 'var' istasyon >= 3
    var = defaultdict(list)
    for r in csv.DictReader(open(os.path.join(BURADA, 'tr7_varlik.csv'), encoding='utf-8')):
        if r['var'] != 'var':
            continue
        for s in r['segment'].split('; '):
            var[(r['tetikleyici'], s)].append(r)
    ciftler = {k: v for k, v in var.items() if len(v) >= N_IST}
    satir = []
    for (o, s), rs in sorted(ciftler.items(), key=lambda kv: (ev[kv[0][0]]['t'], kv[0][1])):
        e = ev[o]
        assert (o, s) in tau, (o, s)
        for r in sorted(rs, key=lambda r: (r['ag'], r['istasyon'])):
            la, lo = ist[(r['ag'], r['istasyon'])]
            d = hav(e['la'], e['lo'], la, lo)
            w0 = e['t'] + dt.timedelta(seconds=d / V_ON)
            w1 = e['t'] + dt.timedelta(seconds=d / V_ARKA + KUYRUK)
            r0 = e['t'] - dt.timedelta(seconds=BASVURU_S)
            assert w1 < SON_GUN
            satir.append(dict(birim=birim(o), tetikleyici=o, t0=e['t'].isoformat(), M=e['M'],
                              ev_enlem=e['la'], ev_boylam=e['lo'], segment=s, tau_kaba_kpa=tau[(o, s)],
                              kahramanmaras=int(o in KAHRAMANMARAS), ag=r['ag'], istasyon=r['istasyon'],
                              ist_enlem=la, ist_boylam=lo, yoklama_kanal=r['kanal'], uzaklik_km=round(d, 1),
                              R_bas=r0.isoformat(), R_son=e['t'].isoformat(),
                              W_bas=w0.isoformat(timespec='seconds'), W_son=w1.isoformat(timespec='seconds')))
    grup = defaultdict(list)
    for x in satir:
        x['iz_km'] = round(nokta_cizgi(x['ist_enlem'], x['ist_boylam'], SEGMENT[x['segment']]), 2)
        grup[(x['tetikleyici'], x['segment'])].append(x)
    for g in grup.values():
        for i, x in enumerate(sorted(g, key=lambda x: (x['iz_km'], x['ag'], x['istasyon'])), 1):
            x['iz_sira'], x['ilk12'] = i, int(i <= N_SINIR)
    ist_tet = {(x['ag'], x['istasyon'], x['tetikleyici']) for x in satir}
    sonuc = dict(girdi_sha256={f: sha(os.path.join(BURADA, f)) for f in
                               ('tr7_varlik.csv', 'tr7_varlik_ozet.json', 'tr7_istasyon.csv', 'tr7_tetikleyici.csv')},
                 comcat_sha256=COMCAT_SHA,
                 liste=dict(cift=len(ciftler), olay=len({o for o, _ in ciftler}), istasyon_tetikleyici=len(ist_tet),
                            satir=len(satir), birim=len({birim(o) for o, _ in ciftler}),
                            ana_birim=len({birim(o) for o, _ in ciftler if o not in KAHRAMANMARAS})))
    rw = [(dt.datetime.fromisoformat(x['W_son']) - dt.datetime.fromisoformat(x['R_bas'])).total_seconds()
          - (dt.datetime.fromisoformat(x['W_bas']) - dt.datetime.fromisoformat(x['R_son'])).total_seconds()
          for x in satir]
    ac = [(dt.datetime.fromisoformat(x['W_son']) - dt.datetime.fromisoformat(x['R_bas'])).total_seconds()
          for x in satir]                                               # R başı – W sonu açıklığı (indirme gövdesi)
    it, ia = {}, {}
    for x, v, a in zip(satir, rw, ac):
        it[(x['ag'], x['istasyon'], x['tetikleyici'])] = v
        ia[(x['ag'], x['istasyon'], x['tetikleyici'])] = a
    sonuc['liste'].update(RW_ortalama_satir_s=round(sum(rw) / len(rw)),
                          RW_ortalama_istasyon_tetikleyici_s=round(sum(it.values()) / len(it)),
                          RW_en_az_s=round(min(rw)), RW_en_cok_s=round(max(rw)),
                          Rbas_Wson_ortalama_satir_s=round(sum(ac) / len(ac)),
                          Rbas_Wson_ortalama_istasyon_tetikleyici_s=round(sum(ia.values()) / len(ia)),
                          Rbas_Wson_en_az_s=round(min(ac)), Rbas_Wson_en_cok_s=round(max(ac)),
                          ilk12_satir=sum(x['ilk12'] for x in satir))
    sonuc['istasyon_sayisi'] = {f'{o}|{s_}': dict(birim=birim(o), tum=len(g), sinirli=min(N_SINIR, len(g)))
                                for (o, s_), g in sorted(grup.items(), key=lambda kv: (ev[kv[0][0]]['t'], kv[0][1]))}

    # ---- 2. ana sayım (K0 önsayımı): Kahramanmaraş dışarıda, Wharton tek birim (τ = birimin en büyüğü)
    def ana_say(carpan_anahtar):
        out = {}
        for k, s in seg_ad.items():
            b = defaultdict(float)
            for o, t, n in oz['segment'][carpan_anahtar][s]['olaylar']:
                if o in KAHRAMANMARAS:
                    continue
                b[birim(o)] = max(b[birim(o)], t)
            ts = sorted(b.values(), reverse=True)
            out[k] = dict(n=len(ts), bant=bant(len(ts)), tau_n=round(ts[-1], 2) if ts else None,
                          tau8=round(ts[7], 2) if len(ts) >= 8 else None,
                          tau5=round(ts[4], 2) if len(ts) >= 5 else None,
                          birimler=sorted(b, key=lambda x: -b[x]),
                          kahramanmaras_bilgi=[o for o, _, _ in oz['segment'][carpan_anahtar][s]['olaylar']
                                               if o in KAHRAMANMARAS])
        return out
    sonuc['K0_on'] = {c: ana_say(c) for c in ('x1', 'x1/3', 'x3')}
    sonuc['K0_on_not'] = 'x3 alt sınırdır (yalnız x1 adayları yoklandı); x1/3 ve x3 bilgi satırıdır.'

    # ---- 3. dışlama cümlesi: n bağımsız tetikleyicide algılama yok -> p_min (algılama olasılığı 0,9 ile)
    sonuc['dislama'] = {n: dict(p_min_tam_algilama=round(1 - 0.05 ** (1 / n), 3),
                                p_min_a90=round(min(1.0, (1 - 0.05 ** (1 / n)) / 0.9), 3)) for n in range(5, 13)}

    # ---- 4. VAR kuralı: algılanan bağımsız tetikleyici X için gereken en küçük X (n, f yanlış algılama / 10n)
    var_tab = {}
    for n in range(5, 13):
        N = 10 * n
        for f in range(0, 6):
            pu = cp_ust(f, N)
            xmin = next((x for x in range(2, n + 1) if binom_ust(n, pu, x) <= 0.05), None)
            var_tab[f'n={n},f={f}'] = dict(N_neg=N, FAR=round(f / N, 3), FAR_ust95=round(pu, 4), X_min=max(2, xmin)
                                           if xmin else None, K2_gecer=f <= math.floor(0.05 * N))
    sonuc['var_kurali'] = var_tab
    # Ö3: özet için kuyruk eşiği 0,05/3 (N = 10n); 'K2' = K2 kalır, None = X yok
    def xmin(n, f, a):
        N = 10 * n
        if f > math.floor(0.05 * N):
            return 'K2'
        pu = cp_ust(f, N)
        x = next((x for x in range(2, n + 1) if binom_ust(n, pu, x) <= a), None)
        return x
    sonuc['X_min_tablo'] = {a_ad: {n: [xmin(n, f, a) for f in range(6)] for n in range(5, 13)}
                            for a_ad, a in (('0.05', 0.05), ('0.05/3', 0.05 / 3))}
    sonuc['rastlanti_en_az_1_FAR005'] = {n: round(1 - 0.95 ** n, 3) for n in range(5, 13)}
    # tek-tetikleyici: rastlantı olasılığı (bilgi)
    sonuc['rastlanti_2_of_8_FAR005'] = round(binom_ust(8, 0.05, 2), 4)

    # ---- 5. pozitif kontrol: Parkfield izi ve istasyonları (Tohoku 2011)
    pk = []
    if '--parkfield' in sys.argv:
        i = sys.argv.index('--parkfield')
        dosyalar = sys.argv[i + 1:i + 3]
        sonuc['parkfield_girdi_sha256'] = {os.path.basename(f): sha(f) for f in dosyalar}
        st = {}
        for fn in dosyalar:
            for sat in open(fn, encoding='utf-8', errors='replace'):
                if sat.startswith('#') or not sat.strip():
                    continue
                f = [x.strip() for x in sat.split('|')]
                net, sta, loc, cha = f[:4]
                la, lo, derin, sr = float(f[4]), float(f[5]), float(f[7] or 0), float(f[14] or 0)
                if net in ('ZQ', 'SY', 'PB') or derin >= 50:
                    continue
                if len(cha) != 3 or cha[2] != 'Z' or cha[0] not in 'HBES' or cha[1] not in 'HP' or sr < 20:
                    continue
                d = nokta_cizgi(la, lo, PARKFIELD_IZ)
                if d > 50:
                    continue
                x = st.setdefault((net, sta), dict(ag=net, istasyon=sta, enlem=la, boylam=lo, kanallar=set(),
                                                   fay_km=round(d, 1)))
                x['kanallar'].add(f'{loc}.{cha}' if loc else cha)
        vr = defaultdict(dict)
        vyol = os.path.join(BURADA, 'tr7_parkfield_varlik.csv')
        sonuc['parkfield_varlik_sha256'] = sha(vyol)
        for r in csv.DictReader(open(vyol, encoding='utf-8')):
            vr[(r['ag'], r['istasyon'])][r['ornek']] = int(r['durum'] == 'var')
        to = ev['official20110311054624120_30']
        for x in sorted(st.values(), key=lambda x: x['fay_km']):
            d = hav(to['la'], to['lo'], x['enlem'], x['boylam'])
            x.update(kanallar=' '.join(sorted(x['kanallar'])), uzaklik_km=round(d, 1),
                     W_bas=(to['t'] + dt.timedelta(seconds=d / V_ON)).isoformat(timespec='seconds'),
                     W_son=(to['t'] + dt.timedelta(seconds=d / V_ARKA + KUYRUK)).isoformat(timespec='seconds'))
            x.update(var_R=vr[(x['ag'], x['istasyon'])]['R'], var_W=vr[(x['ag'], x['istasyon'])]['W'])
            pk.append(x)
        k = 0
        for x in sorted(pk, key=lambda x: (nokta_cizgi(x['enlem'], x['boylam'], PARKFIELD_IZ), x['ag'], x['istasyon'])):
            if x['var_R'] and x['var_W']:
                k += 1
                x['iz_sira'], x['ilk12'] = k, int(k <= N_SINIR)
            else:
                x['iz_sira'], x['ilk12'] = '', 0
        orta = (sum(p[1] for p in PARKFIELD_IZ) / 4, sum(p[0] for p in PARKFIELD_IZ) / 4)
        dmid = hav(to['la'], to['lo'], *orta)
        pgv = 2 * math.pi * 10 ** (to['M'] - 1.66 * math.log10(dmid / 111.195) - 3.3) * 1e-4
        sonuc['parkfield'] = dict(istasyon=len(pk), ag={a: sum(1 for x in pk if x['ag'] == a) for a in
                                                        sorted({x['ag'] for x in pk})},
                                  BK_PKD=any(x['istasyon'] == 'PKD' for x in pk), uzaklik_orta_km=round(dmid),
                                  var_R_ve_W=sum(1 for x in pk if x['var_R'] and x['var_W']),
                                  ilk12=['.'.join((x['ag'], x['istasyon'])) for x in pk if x['ilk12']],
                                  K1_araligi=[(to['t'] + dt.timedelta(seconds=round((to['t'] - to['t'].replace(
                                      microsecond=0)).total_seconds() + dmid / v))).replace(microsecond=0).isoformat()
                                              for v in (4.6, 3.0)],              # saniyeye yuvarlanmış
                                  tau_kaba_kpa=round(30e9 * pgv * 1e-2 / 3500 / 1e3, 2),
                                  W_orta=[(to['t'] + dt.timedelta(seconds=dmid / V_ON)).isoformat(timespec='seconds'),
                                          (to['t'] + dt.timedelta(seconds=dmid / V_ARKA + KUYRUK)).isoformat(
                                              timespec='seconds')])

    js = json.dumps(sonuc, ensure_ascii=False, indent=1, default=str)
    print(js)
    if '--yaz' in sys.argv:
        with open(os.path.join(BURADA, 'tr7_dondurulan_liste.csv'), 'x', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=list(satir[0].keys()))
            w.writeheader()
            w.writerows(satir)
        if pk:
            with open(os.path.join(BURADA, 'tr7_parkfield_liste.csv'), 'x', newline='', encoding='utf-8') as f:
                w = csv.DictWriter(f, fieldnames=list(pk[0].keys()))
                w.writeheader()
                w.writerows(pk)
        with open(os.path.join(BURADA, 'tr7_onkayit_sayilar.json'), 'x', encoding='utf-8') as f:
            f.write(js + '\n')


if __name__ == '__main__':
    main()
