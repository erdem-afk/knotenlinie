# İNCELEME-1 (TR-10b_INCELEME-1.md §D) betiğinin kopyası; özgün yer: scratchpad/inc10b/a_sinir.py.
# Değişiklik yalnız yol düzeltmesi (depo içinden çalışsın diye); hesap aynen.
# (a) gürültüsüz dizide, uç penceresinde >=10 gün şartıyla erişilebilecek en büyük |Δv-Δv0| (her uçta en uç medyanlar)
import sys, itertools
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__)))))
import numpy as np, tr10b_sayim as K
for Y in (1973, 1978, 1998, 2003, 2008, 2013, 2018):
    P, n, i0, iH, iT = K.gunler(Y); t = np.arange(n)/365.25
    x = (3+7*t+4*np.maximum(0,t-iH/365.25)+2*np.sin(2*np.pi*t+1)+0.7*np.cos(4*np.pi*t)+3*(np.arange(n)>=iH-200))
    g = 4-3/((iH-i0)/365.25)
    t2, t3 = (iT-iH)/365.25, (iH-i0)/365.25
    ext = {}
    for i in (i0, iH, iT):
        v = np.sort(x[i-15:i+16])
        # 10 günlük alt kümede medyan = 5. ve 6. sıradakilerin ortalaması; en küçük ve en büyük erişilebilir medyan
        ext[i] = (0.5*(v[4]+v[5]), 0.5*(v[-5]+v[-6]))
    best = 0
    for a, b, c in itertools.product((0,1),(0,1),(0,1)):
        u0, uH, uT = ext[i0][a], ext[iH][b], ext[iT][c]
        best = max(best, abs((uT-uH)/t2-(uH-u0)/t3-g))
    # yalnız tek yanlı bitişik 10 gün (taslağın 'en kötü maske'si)
    best2 = 0
    for a, b, c in itertools.product((0,1),(0,1),(0,1)):
        us = []
        for i, s in zip((i0,iH,iT),(a,b,c)):
            us.append(np.median(x[i-15:i-5] if s==0 else x[i+6:i+16]))
        best2 = max(best2, abs((us[2]-us[1])/t2-(us[1]-us[0])/t3-g))
    print(Y, "en kötü (herhangi 10 gün):", round(best,3), " tek yanlı bitişik:", round(best2,3))
