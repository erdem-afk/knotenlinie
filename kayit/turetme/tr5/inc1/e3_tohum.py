import importlib.util, sys, json, math
import numpy as np
spec = importlib.util.spec_from_file_location('yp', sys.argv[1]); yp = importlib.util.module_from_spec(spec); spec.loader.exec_module(yp)
snr = 0.577 / math.sqrt(10)
out = {}
for tohum in (11, 22, 33, 44):
    rng = np.random.default_rng(tohum)
    r = yp.E3(snr, [0.0, 2e-4, 8e-4], 200, 16, 2000, rng)
    out[tohum] = {k: (v['ana']['gecme_olasiligi'], v['ana']['dko_medyan_yuzde']) for k, v in r.items()}
    print(tohum, out[tohum], flush=True)
