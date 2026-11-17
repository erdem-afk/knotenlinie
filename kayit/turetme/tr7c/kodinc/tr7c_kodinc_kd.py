#!/usr/bin/env python3
"""TR-7c KOD İNCELEMESİ (§E): kodlayıcının `tr7c_kd_k5.py`'sini (değiştirilmeden) bir denetim kancası altında koşar.

Kanca: her soket çağrısı, `/mnt/project-files` altındaki her açma girişimi ve her alt süreç REDDEDİLİR ve sayılır.
YALNIZ YAPAY VERİ (TR-7 KD üreteçleri). Sürdürülebilir: ara jsonl (dördüncü argüman) her işten sonra yazılır.

Kullanım (depo kökünden):
  python3 -I -B kayit/turetme/tr7c/kodinc/tr7c_kodinc_kd.py <çıktı.json> <olcek> <satırlar> <ara.jsonl> [parça i/n]
  parça i/n: planın yalnız (sıra % n == i) işlerini koşar (iki çekirdeğe bölmek için); birleştirme `--birlestir`
  ile aynı ara jsonl'ler verilerek yapılır:
  python3 -I -B .../tr7c_kodinc_kd.py --birlestir <çıktı.json> <olcek> <satırlar> <ara1.jsonl> [<ara2.jsonl> ...]
"""
import json
import os
import sys
import time

sys.dont_write_bytecode = True
os.environ.setdefault('OMP_NUM_THREADS', '1')
YASAK = '/mnt/project-files'
ENGEL = []


def _kanca(olay, args):
    if olay.startswith('socket.'):
        ENGEL.append(olay)
        raise PermissionError('KOD İNCELEMESİ: ağ yasak')
    if olay in ('subprocess.Popen', 'os.system', 'os.posix_spawn', 'os.exec'):
        ENGEL.append(olay)
        raise PermissionError('KOD İNCELEMESİ: alt süreç yasak')
    if olay == 'open' and args and isinstance(args[0], (str, bytes, os.PathLike)):
        p = os.path.abspath(os.fsdecode(args[0]))
        if p == YASAK or p.startswith(YASAK + os.sep):
            ENGEL.append(p)
            raise PermissionError('KOD İNCELEMESİ: gerçek veri yolu yasak')


sys.addaudithook(_kanca)
TR7C = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, TR7C)
import tr7c_kd_k5 as KD  # noqa: E402  (kodlayıcının betiği, değiştirilmeden)

T7, TC = KD.T7, KD.TC


def kos(ara, olcek, adlar, parca=None):
    KD.K.ayikla = KD.ayikla_tr7c
    plan = [x for x in T7.kd_plan(olcek) if x[0] in adlar]
    if parca:
        i, n = parca
        plan = [x for j, x in enumerate(plan) if j % n == i]
    yapilan = set()
    if os.path.exists(ara):
        for s in open(ara, encoding='utf-8'):
            if s.strip():
                r = json.loads(s)
                yapilan.add((r['denetim'], json.dumps(r['ek']), r['tohum']))
    for ad, ek, tohum, n in plan:
        if (ad, json.dumps(ek), tohum) in yapilan:
            continue
        t = time.time()
        r = T7.kd_is(ad, ek, tohum, n)
        r['sure_s'] = round(time.time() - t, 1)
        with open(ara, 'a', encoding='utf-8') as f:
            f.write(json.dumps(r, ensure_ascii=False, default=float) + '\n')
            f.flush()
            os.fsync(f.fileno())
        print(ad, ek, tohum, n, r['sure_s'], flush=True)


def birlestir(cikti, olcek, adlar, aralar):
    sonuc, gor = [], set()
    for a in aralar:
        for s in open(a, encoding='utf-8'):
            if s.strip():
                r = json.loads(s)
                k = (r['denetim'], json.dumps(r['ek']), r['tohum'])
                if k not in gor:
                    gor.add(k)
                    sonuc.append(r)
    plan = [x for x in T7.kd_plan(olcek) if x[0] in adlar]
    eksik = [x for x in plan if (x[0], json.dumps(x[1]), x[2]) not in gor]
    d8 = dict(rms_oran=1.0, pgv_oran=1.0)
    d9 = dict(en_buyuk_fark_s=0.0, sinir_durdurdu=[True])
    d11 = dict(hepsi=True)
    d12c = dict(elle_birebir=dict(dogru=True), rastgele_birebir=[20, 20], gercek_tolerans=True)
    # kd_bantlar sıra bağımlı: plan sırasına koy
    sira = {(x[0], json.dumps(x[1]), x[2]): j for j, x in enumerate(plan)}
    sonuc.sort(key=lambda r: sira.get((r['denetim'], json.dumps(r['ek']), r['tohum']), 10 ** 6))
    sat = [s for s in T7.kd_bantlar(sonuc, d8, d9, d11, d12c) if s['denetim'] not in ('D8', 'D9', 'D11', 'D12c')]
    tr7 = {s['denetim']: s for s in json.load(open(os.path.join(TC.TR7, 'tr7_kd.json')))['satirlar']}
    for s in sat:
        s['TR7_K0_deger'] = tr7.get(s['denetim'], {}).get('deger')
    out = dict(aciklama='TR-7c kod incelemesi §E: TR-7 KD (§7.1) K5 ile, tam ölçek; yalnız yapay veri; '
                        'sızıntı bayrağı ayikla_k5 (Q = ∅, kodlayıcının tr7c_kd_k5.py sarmalayıcısı değiştirilmeden).',
               kod_sha256={f: TC.sha256_dosya(os.path.join(TR7C, f)) for f in ('tr7c_kd_k5.py', 'tr7c_kosu.py')},
               bu_betik_sha256=TC.sha256_dosya(os.path.abspath(__file__)),
               tr7_kosu_sha256=TC.sha256_dosya(os.path.join(TC.TR7, 'tr7_kosu.py')), d2_sha256=TC.D2_SONUC,
               olcek=olcek, satirlar_secilen=adlar, eksik_is=[list(map(str, x)) for x in eksik], bantlar=sat,
               gecti=all(s['gecti'] for s in sat if not s['bilgi']) and not eksik, ham=sonuc,
               hesap_sure_s=round(sum(r.get('sure_s', 0) for r in sonuc), 1), engellenen=ENGEL)
    with open(cikti, 'w', encoding='utf-8') as f:
        f.write(json.dumps(out, ensure_ascii=False, indent=1, default=float) + '\n')
    for s in sat:
        print(('GEÇTİ ' if s['gecti'] else 'KALDI ') + s['denetim'], s['sart'], json.dumps(s['deger'], default=float)[:200])
    print('eksik iş:', len(eksik), 'engellenen:', len(ENGEL))


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == '--birlestir':
        birlestir(a[1], float(a[2]), a[3].split(','), a[4:])
    else:
        p = tuple(int(x) for x in a[4].split('/')) if len(a) > 4 else None
        kos(a[3], float(a[1]), a[2].split(','), p)
