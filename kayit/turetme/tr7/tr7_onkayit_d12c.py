#!/usr/bin/env python3
"""TR-7 ön kayıt sürüm 3, §7.1 D12c (İNCELEME-2 İ2-E2): E1 maskesi (§6.5 madde 1a) birim sınaması, deterministik.

YALNIZ yapay katalog ve dondurulmuş önhesap dosyaları; dalga formu yok, ağa çıkılmaz; yalnız standart kitaplık.

Üç bölüm:
 (1) Elle kurulmuş katalog. Maskelenen saniye kümesi, §6.5.1a'dan ELLE hesaplanıp bu dosyaya sabit olarak yazılmış
     aralıklarla birebir karşılaştırılır. Katalog: M 6,95, 6,99, 7,00 ve 7,9 olaylar (P ve S varışları), tetikleyicinin
     kendisi, tetikleyiciye +3 sn'de M ≥ 7,0 ikinci kimlikli kayıt, Wharton biriminin öteki olayı, W dışında (R'de) bir
     M 6,5 varışı, maskelenmemesi gereken bir M 5,9 olay. Bilinen yanlış kodlar da aynı katalogda değerlendirilir.
 (2) Tohumlu rastgele kataloglar (iki bağımsız tohum). "Koşu kodu" (aralık birleşimi, `maske_araliklari`) ile ondan
     bağımsız yazılmış saniye saniye kaba kuvvet uygulaması (`maske_kaba`) birebir karşılaştırılır; yanlış kodlar da
     kaba kuvvet doğru kümesiyle karşılaştırılır.
 (3) Gerçek varışlar: tetikleyici ve Parkfield pencerelerinin maskesi `tr7_e1_maske.csv`'deki varış anlarından (segment
     orta noktasıyla hesaplanmış) kurulur; W maskeli payı ve K1 aralığının maskeli payı ön kayıttaki değerlerle ±0,001
     içinde karşılaştırılır. W: Marmara'da `tr7_dondurulan_liste.csv`'deki W'lerin birleşimi; Parkfield'da
     `tr7_parkfield_liste.csv`'nin bütün satırlarının W birleşimi (§3.4 önhesabı ile aynı).

Kural (§6.5.1a, E1-C): tetikleyici olayın kendisi ve T0'a ±5 sn içinde M ≥ 7,0 başka kimlikli kaydı dışarıda (Wharton
biriminde öteki olay dahil); M ≥ 7,0: [t_P − 10, t_P + 240] ve [t_S − 10, t_S + 240]; 6,0 ≤ M < 7,0: yalnız
[t_P − 10, t_P + 60]; M < 6,0 maskelenmez.
Bilinen yanlış kodlar: 'kuyruk30' (6,x kuyruğu +30), 'S6x' (6,x'te S de +60 ile; E1-B), 'buyuktur7' (240 sn kuralı
"M > 7,0"), 'ikiz_yok' (ikinci kimlikli kayıt dışlanmaz), 'wharton_dislar' (Wharton'ın öteki olayı da dışlanır).

Kullanım: python3 -I -B tr7_onkayit_d12c.py <tohum1> <tohum2>   (tek satır JSON, stdout)
"""
import csv, datetime as dt, json, os, random, sys

BURADA = os.path.dirname(os.path.abspath(__file__))
KIPLER = ('dogru', 'kuyruk30', 'S6x', 'buyuktur7', 'ikiz_yok', 'wharton_dislar')


# ------------------------------------------------------------------ koşu kodu (aralık birleşimi)
def dislanir(o, tet, kip):
    """o: olay sözlüğü (id, t0, M); tet: tetikleyici (id, t0, digerleri = Wharton birimindeki öteki olay kimlikleri)."""
    if o['id'] == tet['id']:
        return True
    if kip == 'wharton_dislar' and o['id'] in tet.get('digerleri', ()):
        return True
    if kip != 'ikiz_yok' and abs(o['t0'] - tet['t0']) <= 5 and o['M'] >= 7.0:
        return True
    return False


def kurallar(M, kip):
    """[(faz, kuyruk)] — maskelenen fazlar ve kuyrukları."""
    buyuk = M > 7.0 if kip == 'buyuktur7' else M >= 7.0
    if buyuk:
        return [('P', 240), ('S', 240)]
    if M >= 6.0:
        k = 30 if kip == 'kuyruk30' else 60
        return [('P', k), ('S', k)] if kip == 'S6x' else [('P', k)]
    return []


def maske_araliklari(olaylar, tet, kip='dogru'):
    ar = []
    for o in olaylar:
        if dislanir(o, tet, kip):
            continue
        for faz, k in kurallar(o['M'], kip):
            t = o.get(faz)
            if t is not None:
                ar.append((t - 10, t + k))
    ar.sort()
    out = []
    for a, b in ar:
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return [tuple(x) for x in out]


def saniyeler(araliklar, alan):
    """Tamsayı saniye k, [k, k + 1) bir aralığın içindeyse maskeli; alan: [(a, b)] (R ve W)."""
    s = set()
    for a, b in araliklar:
        for lo, hi in alan:
            for k in range(max(int(a), lo), min(int(b), hi)):
                s.add(k)
    return s


# ------------------------------------------------------------------ bağımsız kaba kuvvet (saniye saniye)
def maske_kaba(olaylar, tet, alan):
    s = set()
    for lo, hi in alan:
        for k in range(lo, hi):
            for o in olaylar:
                if o['id'] == tet['id']:
                    continue
                if o['M'] >= 7.0 and -5 <= o['t0'] - tet['t0'] <= 5:
                    continue
                if o['M'] >= 7.0:
                    if any(o.get(f) is not None and o[f] - 10 <= k and k + 1 <= o[f] + 240 for f in ('P', 'S')):
                        s.add(k)
                        break
                elif o['M'] >= 6.0:
                    if o.get('P') is not None and o['P'] - 10 <= k and k + 1 <= o['P'] + 60:
                        s.add(k)
                        break
    return s


# ------------------------------------------------------------------ (1) elle kurulmuş katalog
# Zamanlar tetikleyici T0'a göre sn. R = [−3600, 0), W = [1000, 2900). Varışlar doğrudan verilir (seyahat süresi
# hesabı bu sınamanın konusu değil; o, gerçek varışlarla bölüm (3)'te denetlenir).
EL_TET = dict(id='TET', t0=0.0, digerleri=('DIGER',))
EL_ALAN = [(-3600, 0), (1000, 2900)]
EL_KATALOG = [
    dict(id='TET', t0=0.0, M=9.0, P=700, S=1300),          # tetikleyicinin kendisi: dışarıda
    dict(id='TET-B', t0=3.0, M=8.9, P=703, S=1303),        # ikinci kimlikli kayıt (+3 sn, M ≥ 7): dışarıda
    dict(id='E695', t0=200.0, M=6.95, P=1100, S=1500),     # 6,x: yalnız P, +60
    dict(id='E699', t0=500.0, M=6.99, P=1400, S=1800),     # 6,x: yalnız P, +60
    dict(id='E700', t0=800.0, M=7.00, P=1700, S=2200),     # 7,00: P ve S, +240
    dict(id='E79', t0=1500.0, M=7.9, P=2500, S=2950),      # S'si W'den sonra (W dışında kalan varış)
    dict(id='DIGER', t0=1600.0, M=8.2, P=2600, S=2850),  # Wharton biriminin öteki olayı: dahil
    dict(id='R65', t0=-1200.0, M=6.5, P=-500, S=-100),     # R içinde 6,x P (W dışında)
    dict(id='E59', t0=600.0, M=5.9, P=1200, S=1600),       # M < 6,0: maskelenmez
]
# §6.5.1a'dan elle: R'de [−510, −440]; W'de [1090, 1160], [1390, 1460], [1690, 1940], [2190, 2440],
# [2490, 2740] ∪ [2590, 2840] ∪ [2840, 3090] → [2490, 2900) (W sonunda kesilir); [2940, 3190] W dışında.
EL_BEKLENEN = [(-510, -440), (1090, 1160), (1390, 1460), (1690, 1940), (2190, 2440), (2490, 2900)]


def bolum1():
    beklenen = set()
    for a, b in EL_BEKLENEN:
        beklenen.update(range(a, b))
    out = {}
    for kip in KIPLER:
        s = saniyeler(maske_araliklari(EL_KATALOG, EL_TET, kip), EL_ALAN)
        out[kip] = dict(birebir=(s == beklenen), fark_saniye=len(s ^ beklenen))
    out['kaba_kuvvet_birebir'] = maske_kaba(EL_KATALOG, EL_TET, EL_ALAN) == beklenen
    return out


# ------------------------------------------------------------------ (2) tohumlu rastgele kataloglar
def bolum2(tohum, n_katalog=20, n_olay=40):
    rng = random.Random(tohum)
    sonuc = {k: 0 for k in KIPLER}
    for _ in range(n_katalog):
        tet = dict(id='T', t0=0.0, digerleri=('W2',))
        ol = [dict(id='T', t0=0.0, M=9.0, P=rng.randint(500, 900), S=rng.randint(900, 1200))]
        # sınır olayları her katalogda: 7,00; 6,00; 5,99; ikiz; Wharton öteki olayı
        for i, M in enumerate([7.00, 6.00, 5.99, 6.95]):
            P = rng.randint(-3500, 2800)
            ol.append(dict(id=f'B{i}', t0=float(P - 700), M=M, P=P, S=P + rng.randint(150, 500)))
        ol.append(dict(id='IKIZ', t0=float(rng.randint(-5, 5)), M=round(rng.uniform(7.0, 9.0), 2),
                       P=rng.randint(600, 900), S=rng.randint(1000, 2800)))
        ol.append(dict(id='W2', t0=float(rng.randint(60, 7200)), M=8.2, P=rng.randint(600, 2800),
                       S=rng.randint(1000, 3200)))
        for j in range(n_olay):
            P = rng.randint(-4000, 3500)
            ol.append(dict(id=f'O{j}', t0=float(P - rng.randint(300, 900)), M=round(rng.uniform(5.5, 8.5), 2),
                           P=P, S=P + rng.randint(100, 600)))
        alan = [(-3600, 0), (rng.randint(800, 1200), rng.randint(2600, 3100))]
        dogru = maske_kaba(ol, tet, alan)
        for kip in KIPLER:
            s = saniyeler(maske_araliklari(ol, tet, kip), alan)
            sonuc[kip] += (s == dogru)
    return dict(tohum=tohum, n_katalog=n_katalog, birebir_katalog_sayisi=sonuc)


# ------------------------------------------------------------------ (3) gerçek varışlar
def zaman(s):
    s = s.replace('Z', '')
    for f in ('%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S'):
        try:
            return dt.datetime.strptime(s, f)
        except ValueError:
            pass
    raise ValueError(s)


def kesisim(ar, a, b):
    return sum(max(0.0, min(y, b) - max(x, a)) for x, y in ar)


BEKLENEN_GERCEK = {  # ön kayıt §6.5.1a ve D12c satırı
    'official20110311054624120_30|S1': 0.664, 'official20110311054624120_30|S2': 0.654,
    'official20110311054624120_30|S3': 0.645, 'PARKFIELD|PK': 0.578, 'K1': 0.647}
K1 = (dt.datetime(2011, 3, 11, 6, 16, 1), dt.datetime(2011, 3, 11, 6, 31, 48))


def bolum3():
    liste = list(csv.DictReader(open(os.path.join(BURADA, 'tr7_dondurulan_liste.csv'), encoding='utf-8')))
    pen = {}
    for r in liste:
        k = f"{r['tetikleyici']}|{r['segment']}"
        p = pen.setdefault(k, dict(R0=zaman(r['R_bas']), W0=zaman(r['W_bas']), W1=zaman(r['W_son'])))
        p['W0'], p['W1'] = min(p['W0'], zaman(r['W_bas'])), max(p['W1'], zaman(r['W_son']))
    pk = list(csv.DictReader(open(os.path.join(BURADA, 'tr7_parkfield_liste.csv'), encoding='utf-8')))
    t0 = zaman(next(r['t0'] for r in liste if r['tetikleyici'] == 'official20110311054624120_30'))
    pen['PARKFIELD|PK'] = dict(R0=t0 - dt.timedelta(seconds=3600), W0=min(zaman(x['W_bas']) for x in pk),
                               W1=max(zaman(x['W_son']) for x in pk))
    olay = {}
    for r in csv.DictReader(open(os.path.join(BURADA, 'tr7_e1_maske.csv'), encoding='utf-8')):
        k = 'PARKFIELD|PK' if r['segment'] == 'PK' else f"{r['tetikleyici']}|{r['segment']}"
        o = olay.setdefault(k, {}).setdefault(r['olay'], dict(id=r['olay'], M=float(r['M']), t0=0.0))
        o[r['faz']] = zaman(r['varis'])
    sonuc = {}
    for kip in KIPLER:
        d = {}
        for k in list(BEKLENEN_GERCEK):
            if k == 'K1':
                continue
            p = pen[k]
            ref = p['W0']
            ol = [dict(id=o['id'], M=o['M'], t0=1e9,           # csv'de tetikleyici ve ikizi zaten yok
                       **{f: (o[f] - ref).total_seconds() for f in ('P', 'S') if f in o})
                  for o in olay.get(k, {}).values()]
            ar = maske_araliklari(ol, dict(id='-', t0=0.0), kip)
            a0, w1 = (p['R0'] - ref).total_seconds(), (p['W1'] - ref).total_seconds()
            ar = [x for x in ar if kesisim([x], a0, w1) > 0]
            d[k] = round(kesisim(ar, 0.0, w1) / w1, 3)
            if k == 'PARKFIELD|PK':
                ka, kz = (K1[0] - ref).total_seconds(), (K1[1] - ref).total_seconds()
                d['K1'] = round(kesisim(ar, ka, kz) / (kz - ka), 3)
                d['K1_maskeli_s'] = round(kesisim(ar, ka, kz))
                d['K1_uzunluk_s'] = round(kz - ka)
        d['hepsi_tolerans_icinde'] = all(abs(d[k] - v) <= 0.001 + 1e-9 for k, v in BEKLENEN_GERCEK.items())
        sonuc[kip] = d
    return sonuc


def main():
    t1, t2 = int(sys.argv[1]), int(sys.argv[2])
    b1 = bolum1()
    b2 = [bolum2(t1), bolum2(t2)]
    b3 = bolum3()
    gecti = (b1['dogru']['birebir'] and b1['kaba_kuvvet_birebir']
             and all(x['birebir_katalog_sayisi']['dogru'] == x['n_katalog'] for x in b2)
             and b3['dogru']['hepsi_tolerans_icinde'])
    yanlis_ayrildi = {k: (not b1[k]['birebir']) or any(x['birebir_katalog_sayisi'][k] < x['n_katalog'] for x in b2)
                      or not b3[k]['hepsi_tolerans_icinde'] for k in KIPLER if k != 'dogru'}
    print(json.dumps(dict(denetim='D12c', tohumlar=[t1, t2], elle_katalog=b1, rastgele_katalog=b2, gercek_varis=b3,
                          dogru_kod_bantta=gecti, yanlis_kod_bant_disinda=yanlis_ayrildi), ensure_ascii=False))


if __name__ == '__main__':
    main()
