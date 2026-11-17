"""TR-7c İNCELEME-2: sürüm 2 (41d2ff5 + b6a3e86) için doğrulama hesabı. Yalnız metin karşılaştırması ve kombinatorik.

Ağ isteği yok, dalga formu yok. INCELEME-1'in `tr7c_inc1.py`'si değiştirilmeden modül olarak yüklenir (Fisher, X_min).
  1 d_aynen    : INCELEME-1 §9'daki D-1…D-10 alıntı bloklarının sürüm 2'de birebir (boşluk normalleştirilerek) bulunması;
                 Z1–Z8'in de hâlâ birebir olması.
  2 dal_v2     : Z4 + D-7 okuma kuralıyla bütün tamsayı ızgarası (n_P 0–10, n_N 0–29, N_PK 0–120, f ≤ N_PK,
                 M_ölç ≤ X_P, M_mod ≤ M_ölç, MDA, A90). (b) içinde D-9/D-10/(b′) etiketleri dal değil, yalnız VAR'ı engeller.
Kullanım: python3 -I -B tr7c_inc2.py
"""
import importlib.util, json, math, os, re, sys
sys.dont_write_bytecode = True
BU = os.path.dirname(os.path.abspath(__file__))
TR7C = os.path.dirname(BU)
KOK = os.path.dirname(os.path.dirname(os.path.dirname(TR7C)))
spec = importlib.util.spec_from_file_location('inc1', os.path.join(TR7C, 'inc1', 'tr7c_inc1.py'))
I1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(I1)
ONK = os.path.join(KOK, 'kayit', 'onkayit', 'TR-7c_tetiklenmis-tremor_ONKAYIT.md')
INC1 = os.path.join(KOK, 'kayit', 'onkayit', 'TR-7c_INCELEME-1.md')


def d_aynen():
    inc = open(INC1, encoding='utf-8').read()
    onk = I1.norm(open(ONK, encoding='utf-8').read())
    bol = inc.split('## 9. Zorunlu düzeltmeler')[1].split('## 10.')[0]
    parca = re.split(r'\n\*\*(D-\d+)\b[^\n]*\n', '\n' + bol)
    out = {}
    for i in range(1, len(parca), 2):
        bloklar = [I1.norm(b) for b in re.findall(r'((?:^>.*\n?)+)', parca[i + 1], flags=re.M)]
        # D-8 iki blok; ">\n" ile ayrılmış tek alıntıyı iki cümleye böl
        cumleler = []
        for b in bloklar:
            cumleler += [c.strip() for c in re.split(r'(?<=")\s(?=")', b) if c.strip()]
        out[parca[i]] = [dict(uzunluk=len(c), birebir=c in onk) for c in cumleler]
    return out


def dal_v2():
    xm = {}
    ii_say = {}
    for nP in range(0, 11):
        for NPK in range(0, 121):
            for f in range(0, NPK + 1):
                ii = NPK >= 5 and f / NPK <= 0.30
                x = I1.xmin(nP, f, NPK, cp=I1.cp_ust_scipy) if nP >= 2 else None
                for XP in range(nP + 1):
                    i = x is not None and XP >= max(math.ceil(nP / 2), x)
                    ii_say[(nP, XP, i, ii)] = ii_say.get((nP, XP, i, ii), 0) + 1
    def m_say(XP):
        return {(False, False): sum(Mo + 1 for Mo in range(0, min(2, XP) + 1)),
                (True, False): 3 * max(0, XP - 2), (True, True): sum(Mo - 2 for Mo in range(3, XP + 1))}
    sira = dict.fromkeys('abcde', 0); toplam = 0; bos = 0; cift = 0; e2_d = 0; e2_a = 0; e_ikinci = 0
    for nP in range(11):
        for XP in range(nP + 1):
            MS = m_say(XP)
            for nN in range(30):
                for XN in range(nN + 1):
                    iii = nP > 0 and I1.fisher_ok(XP, nP, XN, nN)
                    a = nP < 8 or nN < 20
                    for i in (False, True):
                        for ii in (False, True):
                            c1 = ii_say.get((nP, XP, i, ii), 0)
                            if not c1:
                                continue
                            for (m3, iv), c2 in MS.items():
                                if not c2:
                                    continue
                                for mda in (False, True):
                                    for a90 in (False, True):
                                        w = c1 * c2; toplam += w
                                        b = (not a) and i and ii and iii and iv
                                        c = (not a) and i and ii and m3 and ((not iii) or (not iv))
                                        d = (not a) and ((not i) or (not ii)) and mda and a90
                                        e = not (a or b or c or d)
                                        # D-7: ikinci cümle yalnız (a) yok ve (i),(ii) varken
                                        e2 = (not a) and i and ii and (not m3)
                                        hangi = [k for k, v in zip('abcde', (a, b, c, d, e)) if v]
                                        if not hangi:
                                            bos += w
                                        elif len(hangi) > 1:
                                            cift += w
                                        else:
                                            sira[hangi[0]] += w
                                        if e2 and hangi != ['e']:
                                            e2_d += w
                                        if e2:
                                            e_ikinci += w
    return dict(toplam_nokta=toplam, dal=sira, hicbir_dal=bos, birden_cok_dal=cift,
                d7_ikinci_cumle_e_disinda=e2_d, d7_ikinci_cumle_e_icinde=e_ikinci)


def main():
    out = dict(not_='TR-7c İNCELEME-2; ağ isteği ve dalga formu yok.',
               girdi_sha256={os.path.relpath(p, KOK): I1.sha(p) for p in (ONK, INC1, os.path.join(TR7C, 'inc1', 'tr7c_inc1.py'))},
               z_aynen_v2=None, d_aynen=d_aynen(), dal_v2=dal_v2())
    I1.ONK = ONK
    out['z_aynen_v2'] = I1.z_aynen()
    json.dump(out, open(os.path.join(BU, 'tr7c_inc2.json'), 'w'), ensure_ascii=False, indent=1, sort_keys=True)
    print(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True))


if __name__ == '__main__':
    sys.exit(main())
