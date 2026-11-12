#!/usr/bin/env python3
"""TR-4 İNCELEME-1 (Z5): bir istasyon-günün (4 saat × 3 bileşen, 100 sn^-1) TR-5b §3.2-3.3 ön işlem ve saatlik ÇİF süresinin
kaba ölçümü, yapay gürültüyle, yalnız numpy, tek çekirdek. miniSEED çözme ve germe dahil değildir.
Kullanım: python3 -I -B inc1_islem_suresi.py   Çıktı: ekrana (süre, sn/istasyon-gün; C ve A için toplam saat).
"""
import time
import numpy as np

FS0, FS, H = 100.0, 20.0, 3600
n0 = int(FS0 * H); n = int(FS * H); L = 1200                        # ±60 sn, 20 sn^-1


def saat(x):
    x = x - x.mean(); t = np.arange(len(x)); x = x - np.polyval(np.polyfit(t, x, 1), t)
    w = np.hanning(int(0.1 * len(x))); k = len(w) // 2; x[:k] *= w[:k]; x[-k:] *= w[-k:]
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / FS0)
    X[f > 8.5] = 0; m = (f > 8) & (f <= 8.5); X[m] *= 0.5 * (1 + np.cos(np.pi * (f[m] - 8) / 0.5))
    y = np.fft.irfft(X[: n // 2 + 1], n) * (n / n0)                # 20 sn^-1
    Y = np.fft.rfft(y); g = np.fft.rfftfreq(n, 1 / FS)
    rms = np.sqrt(np.sum(np.abs(Y[(g >= .5) & (g <= 2)]) ** 2))
    a = np.zeros_like(g); a[(g >= .5) & (g <= 2)] = 1
    for lo, hi, yon in ((.4, .5, 1), (2.0, 2.1, -1)):
        m = (g >= lo) & (g < hi); a[m] = 0.5 * (1 - np.cos(np.pi * (g[m] - lo) / 0.1)) if yon == 1 else 0.5 * (1 + np.cos(np.pi * (g[m] - lo) / 0.1))
    return np.fft.irfft(np.exp(1j * np.angle(Y)) * a, n), rms


def gun(rng):
    out = []
    for _ in range(4):
        z, e, nn = (saat(rng.standard_normal(n0))[0] for _ in range(3))
        F = [np.fft.rfft(v, 2 * n) for v in (z, e, nn)]
        for i, j in ((0, 1), (0, 2), (1, 2)):
            c = np.fft.irfft(F[i] * np.conj(F[j]), 2 * n); c = np.concatenate([c[-L:], c[:L + 1]])
            out.append(c / np.sqrt(np.sum(z ** 2) * np.sum(e ** 2)))
    return out


rng = np.random.default_rng(1)
gun(rng); t0 = time.time(); K = 5
for _ in range(K): gun(rng)
s = (time.time() - t0) / K
print(f'sn/istasyon-gün {s:.2f}; C 35 020 gün: {35020 * s / 3600:.1f} saat; A 53 150 gün: {53150 * s / 3600:.1f} saat')
