#!/usr/bin/env python3
"""TR-7c koşu kodu için D-8 ve E-2 değerlerinin koşudan ÖNCE dondurulması (yalnız kombinatorik hesap).

D-8 (aynen): "(c), (d) ve (e) cümlelerinin sonuna '(ayırt edilemez: gerçekleşen n_P, n_N ile, q 0,1'de görülebilir en
küçük s = [..] (m_t 0,8) / [..] (m_t 0,5))' eklenir. Değerler `tr7c_inc1.json` `esik.MDE_tablosu_q0.1`'den okunur;
tabloda olmayan n'ler için aynı işlevle (`tr7c_inc1.py` `esik`) koşudan önce hesaplanıp dondurulur."
E-2 (aynen, son cümle): "k_koşu < 10 ise k_koşu ile hesaplanan güç (s 0,7, q 0,1; `tr7c_inc1.json`
`esik.D1_kref_guc_s0.7_q0.1` işlevi) bilgi olarak eklenir."

`tr7c_inc1.py` (sha256 c809ce97…58a8) DEĞİŞTİRİLMEDEN modül olarak yüklenir. `esik()` içindeki `guc` ve `mde_ikiye`
yerel işlevlerdir (dışarıdan çağrılamaz); aşağıdaki iki işlev onların satır satır kopyasıdır (aynı çağrılar, aynı
argümanlar). Doğruluk denetimi: inc1 json'undaki bütün hücreler (MDE 21 hücre, k 7 hücre) yeniden üretilir ve birebir
karşılaştırılır; biri uyuşmazsa çıktı yazılmaz.

Hesaplanan: n_P 8…10 × n_N 20…29 (D-1 gereği n_N ≤ 29; n_P < 8 ya da n_N < 20 dal (a)'dır ve D-8 eki almaz) ve
k 0…10 (E-2; işlevin varsayılanlarıyla n_P 10, n_N 30, yani `esik.D1_kref_guc_s0.7_q0.1` ile aynı tanım).
Ağ isteği yok, dalga formu yok. Kullanım: python3 -I -B tr7c_mde_ek.py <çıktı.json>
"""
import hashlib
import importlib.util
import json
import os
import sys

sys.dont_write_bytecode = True
os.environ.setdefault('OMP_NUM_THREADS', '1')
BU = os.path.dirname(os.path.abspath(__file__))
INC1_PY = os.path.join(BU, 'inc1', 'tr7c_inc1.py')
INC1_JSON = os.path.join(BU, 'inc1', 'tr7c_inc1.json')
INC1_PY_SHA = 'c809ce9755058fcba4f92c84cebf8e7cfadeb5cf055b8f0b8320e2e7499d58a8'
INC1_JSON_SHA = '4974dbe66163b49ba8c1b7dab699121c45cdce5aa1fba53c0cb1b0791d912974'


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()


def yukle():
    if sha(INC1_PY) != INC1_PY_SHA or sha(INC1_JSON) != INC1_JSON_SHA:
        raise SystemExit('tr7c_inc1.py ya da tr7c_inc1.json sha256 uyuşmuyor')
    spec = importlib.util.spec_from_file_location('tr7c_inc1', INC1_PY)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    M = yukle()

    # --- tr7c_inc1.py esik() içindeki yerel işlevlerin kopyası (değiştirilmeden)
    def guc(s, q, mt, nP=10, nN=30, kref=None):
        pm, pn = M.sabit_model(s, q, mt, 0.05, nP)
        if kref is not None:
            pm2, pn2 = [], []
            for k in range(nP):
                if k < kref:
                    pm2.append(pm[k]); pn2.append(pn[k])
                else:
                    pm2.append(0.0); pn2.append(pm[k] + pn[k])
            pm, pn = pm2, pn2
        return M.p_d30m3(pm, pn, [q] * nN, r=q, cp=M.cp_ust_scipy)

    def mde_ikiye(q, mt, nP, nN):
        lo, hi = 0, 100
        if guc(1.0, q, mt, nP, nN) < 0.80:
            return None
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if guc(mid / 100, q, mt, nP, nN) >= 0.80:
                hi = mid
            else:
                lo = mid
        return hi / 100
    # ---

    inc1 = json.load(open(INC1_JSON))['esik']
    mde = {}
    for nP in (8, 9, 10):
        for nN in range(20, 30):
            mde[f'nP{nP}_nN{nN}'] = dict(mt08=mde_ikiye(0.1, 0.8, nP, nN), mt05=mde_ikiye(0.1, 0.5, nP, nN))
            print(nP, nN, mde[f'nP{nP}_nN{nN}'], flush=True)
    kg = {f'k{k}': dict(mt08=round(guc(0.7, 0.1, 0.8, kref=k), 4), mt05=round(guc(0.7, 0.1, 0.5, kref=k), 4))
          for k in range(0, 11)}
    # yeniden üretim denetimi: inc1 json'undaki bütün hücreler
    uyusmayan = []
    for anahtar, v in inc1['MDE_tablosu_q0.1'].items():
        nP, nN = anahtar[2:].split('_nN')
        nP, nN = int(nP), int(nN)
        hesap = mde.get(anahtar) if nN <= 29 else dict(mt08=mde_ikiye(0.1, 0.8, nP, nN),
                                                        mt05=mde_ikiye(0.1, 0.5, nP, nN))
        if hesap != v:
            uyusmayan.append((anahtar, v, hesap))
    for anahtar, v in inc1['D1_kref_guc_s0.7_q0.1'].items():
        if kg[anahtar] != v:
            uyusmayan.append((anahtar, v, kg[anahtar]))
    if uyusmayan:
        raise SystemExit(f'inc1 json yeniden üretilemedi: {uyusmayan}')
    out = dict(not_='TR-7c D-8 ve E-2 değerleri; koşudan önce dondurulur. tr7c_inc1.py esik() işlevleriyle.',
               girdi_sha256={'tr7c_inc1.py': INC1_PY_SHA, 'tr7c_inc1.json': INC1_JSON_SHA},
               yeniden_uretim='inc1 json esik.MDE_tablosu_q0.1 (21 hücre) ve D1_kref_guc_s0.7_q0.1 (7 hücre) birebir',
               MDE_q01=mde, k_guc_s07_q01=kg)
    with open(sys.argv[1], 'x', encoding='utf-8') as f:
        f.write(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
