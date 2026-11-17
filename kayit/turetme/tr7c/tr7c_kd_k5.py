#!/usr/bin/env python3
"""TR-7c §10 adım 2: TR-7'nin KD'si (§7.1) §6.5 madde 3 = K5 ile. YALNIZ YAPAY VERİ (TR-7 `tr7_kosu.py` KD üreteçleri,
100 Hz, değiştirilmeden).

Uygulama: `tr7_kosu.kd_is` ve `kd_bantlar` değiştirilmeden çağrılır; yalnız `tr7_cekirdek.ayikla` bu süreçte
sarmalanır: özgün bayraklar hesaplanır, sonra 'sizinti' bayrağı TR-7c koşu kodunun `ayikla_k5`'inin (K5, istasyonların
≥ yarısı) sonucuyla değiştirilir (TR-7 K0 sonucu 'sizinti_K0' diye saklanır). KD pencerelerinde tetikleyici yoktur:
Q = ∅ alınır (K5'in "Q'da doğru kurulamazsa a = b = 0" kolu; kalıntı şartı sağlanmaz, yalnız ρ kolu çalışır; O-41).

Süre: TR-7 KD 4 çekirdekte 29 304 sn sürdü. Burada yalnız ayıklamaya bağlı satırlar (D1–D3, D7, D7b, D7c, D7d, D15)
ve ölçek `olcek` ile (pencere sayısı × olcek) koşulur; bantlar `kd_bantlar` ile aynen denetlenir, ama n küçüldüğü
için Monte Carlo payı büyüktür (raporda yazılır).

Kullanım: python3 -I -B tr7c_kd_k5.py <çıktı.json> <olcek> <satır adları virgülle, ör. D7,D7c> [ara.jsonl]
"""
import json
import os
import sys
import time

sys.dont_write_bytecode = True
os.environ.setdefault('OMP_NUM_THREADS', '1')
BURA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURA)
import tr7c_kosu as TC  # noqa: E402

K = TC.K
sys.path.insert(0, TC.TR7)
import tr7_kosu as T7  # noqa: E402  (değiştirilmeden; KD üreteçleri)

assert T7.K is K
Q_KD = (0, 0)
_ORJ = K.ayikla


def ayikla_tr7c(ist, kume, maske, yanlis=False):
    b = _ORJ(ist, kume, maske, yanlis)
    k5 = TC.ayikla_k5(ist, kume, maske, Q_KD)
    b['sizinti_K0'] = b['sizinti']
    b['sizinti'] = k5['sizinti']
    b['k5_bayrak'] = k5['k5_bayrak']
    return b


def main():
    cikti, olcek, adlar = sys.argv[1], float(sys.argv[2]), sys.argv[3].split(',')
    ara = sys.argv[4] if len(sys.argv) > 4 else None
    K.ayikla = ayikla_tr7c
    t0 = time.time()
    plan = [x for x in T7.kd_plan(olcek) if x[0] in adlar]
    sonuc = []
    if ara and os.path.exists(ara):
        sonuc = [json.loads(s) for s in open(ara, encoding='utf-8') if s.strip()]
    yapilan = {(r['denetim'], json.dumps(r['ek']), r['tohum']) for r in sonuc}
    for ad, ek, tohum, n in plan:
        if (ad, json.dumps(ek), tohum) in yapilan:
            continue
        t = time.time()
        r = T7.kd_is(ad, ek, tohum, n)
        r['sure_s'] = round(time.time() - t, 1)
        sonuc.append(r)
        if ara:
            with open(ara, 'a', encoding='utf-8') as f:
                f.write(json.dumps(r, ensure_ascii=False, default=float) + '\n')
        print(ad, ek, tohum, n, json.dumps(r['sonuc'], ensure_ascii=False, default=float)[:300], r['sure_s'], flush=True)
    d8 = dict(rms_oran=1.0, pgv_oran=1.0)
    d9 = dict(en_buyuk_fark_s=0.0, sinir_durdurdu=[True])
    d11 = dict(hepsi=True)
    d12c = dict(elle_birebir=dict(dogru=True), rastgele_birebir=[20, 20], gercek_tolerans=True)
    sat = [s for s in T7.kd_bantlar(sonuc, d8, d9, d11, d12c) if s['denetim'] not in ('D8', 'D9', 'D11', 'D12c')]
    tr7 = {s['denetim']: s for s in json.load(open(os.path.join(TC.TR7, 'tr7_kd.json')))['satirlar']}
    for s in sat:
        s['TR7_K0_deger'] = tr7.get(s['denetim'], {}).get('deger')
    out = dict(aciklama='TR-7 KD (§7.1) K5 ile (TR-7c §10 adım 2); yalnız yapay veri; sızıntı bayrağı ayikla_k5 (Q = ∅).',
               kod_sha256={f: TC.sha256_dosya(os.path.join(BURA, f)) for f in ('tr7c_kd_k5.py', 'tr7c_kosu.py')},
               tr7_kosu_sha256=TC.sha256_dosya(os.path.join(TC.TR7, 'tr7_kosu.py')), d2_sha256=TC.D2_SONUC,
               olcek=olcek, satirlar_secilen=adlar, plan=[list(map(str, x)) for x in plan], bantlar=sat,
               gecti=all(s['gecti'] for s in sat if not s['bilgi']), ham=sonuc, sure_s=round(time.time() - t0, 1))
    with open(cikti, 'w', encoding='utf-8') as f:
        f.write(json.dumps(out, ensure_ascii=False, indent=1, default=float) + '\n')
    for s in sat:
        print(('GEÇTİ ' if s['gecti'] else 'KALDI ') + s['denetim'], s['sart'], json.dumps(s['deger'], default=float)[:200])


if __name__ == '__main__':
    main()
