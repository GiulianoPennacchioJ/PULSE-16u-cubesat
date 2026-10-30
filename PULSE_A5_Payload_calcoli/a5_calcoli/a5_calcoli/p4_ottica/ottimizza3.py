# Ottimizzazione a passi: campo che cresce gradualmente (0,5 -> 1 -> 1,5 -> 1,96 gradi di semi-diagonale)
import sys, json; sys.path.insert(0, '.')
import numpy as np, korsch as K
from scipy.optimize import least_squares
from primo_ordine import soluzione
f1, d1, e = map(float, sys.argv[1:4])
P = soluzione(f1, d1, e)
pupil = K.pupil_grid(120.0, 0.30, 16)
base = dict(c1=-1/P['R1'], c2=-1/P['R2'], c3=-1/P['R3'], d1=d1, z3=P['z3'])
def mk(x):
    S = dict(base)
    S.update(k1=x[0], k2=x[1], k3=x[2], c1=base['c1']*x[4], c2=base['c2']*x[5], c3=base['c3']*x[6], z3=base['z3']*x[7])
    return S
def res(x, campi):
    S = mk(x); r = []
    for fx, fy in campi:
        w = K.wfe_rms(S, fx, fy, x[3], pupil)[0]
        r.append(w*1e6 if np.isfinite(w) else 1e5)
    r.append((K.efl_abs(S) - 700)*100)
    r.append((-S['c1'] + S['c2'] - S['c3'])*1e7)      # Petzval nullo
    return np.array(r)
x = np.array([-1, -2.5, -0.5, P['zi'], 1, 1, 1, 1])
for scala in (0.0, 0.25, 0.5, 0.75, 1.0):
    campi = [(0, 0)] + [(0.92*scala*a, 1.725*scala*b) for a in (0, 0.5, 1) for b in (0, 0.5, 1) if (a, b) != (0, 0)]
    s = least_squares(res, x, args=(campi,), max_nfev=1500, x_scale=[0.1, 0.1, 0.1, 0.1, 1e-3, 1e-3, 1e-3, 1e-3])
    x = s.x
    print(f"scala {scala}: max WFE {max(res(x, campi)[:-2]):.1f} nm, EFL {K.efl_abs(mk(x)):.2f}")
S = mk(x); zi = x[3]
pupil2 = K.pupil_grid(120.0, 0.30, 24)
grid = [(fx, fy) for fx in (0, 0.46, 0.92) for fy in (0, 0.43, 0.86, 1.29, 1.725)]
W = np.array([K.wfe_rms(S, fx, fy, zi, pupil2)[0]*1e6 for fx, fy in grid]).reshape(3, 5)
print(f"f1 {f1} d1 {d1} e {e}: EFL {K.efl_abs(S):.1f}  zi {zi:.2f}  R {1/S['c1']:.1f} {1/S['c2']:.1f} {1/S['c3']:.1f}  k {S['k1']:.3f} {S['k2']:.3f} {S['k3']:.3f}  z3 {S['z3']:.1f}")
print("WFE nm rms, righe traverso 0/0,46/0,92 gradi, colonne lungo traccia 0..1,725 gradi"); print(np.round(W, 1))
json.dump(dict(S=S, zi=zi), open(f'sol_{int(f1)}_{int(d1)}_{int(e)}.json', 'w'))
