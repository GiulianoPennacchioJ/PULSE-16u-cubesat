import sys, json; sys.path.insert(0, '.')
import numpy as np, korsch as K
from scipy.optimize import least_squares
from primo_ordine import soluzione
f1, d1, e = map(float, sys.argv[1:4])
P = soluzione(f1, d1, e)
pupil = K.pupil_grid(120.0, 0.30, 20)
FX, FY = 0.92, 1.725
campi = [(fx, fy) for fx in np.linspace(0, FX, 3) for fy in np.linspace(0, FY, 4)]
base = dict(c1=-1/P['R1'], c2=-1/P['R2'], c3=-1/P['R3'], d1=d1, z3=P['z3'])
def mk(x, libero):
    S = dict(base); S['k1'], S['k2'], S['k3'] = x[0], x[1], x[2]
    if libero:
        S['c1'], S['c2'], S['c3'], S['z3'] = base['c1']*x[4], base['c2']*x[5], base['c3']*x[6], base['z3']*x[7]
    return S
def res(x, libero, campi):
    S = mk(x, libero); r = []
    for fx, fy in campi:
        w, s, Q = K.wfe_rms(S, fx, fy, x[3], pupil)
        r.append(w*1e6 if np.isfinite(w) else 1e5)
    r.append((K.efl_abs(S) - 700)*20)
    if libero:   # Petzval nullo mantenuto
        r.append((-S['c1'] + S['c2'] - S['c3'])*1e6)
    return np.array(r)
best = None
for k0 in ([-0.9, -2.5, -0.6], [-1.0, -3.0, -0.3], [-0.8, -2.0, -0.8]):
    x0 = np.array(k0 + [P['zi']])
    s1 = least_squares(res, x0, args=(False, [(0, 0)]), max_nfev=400)
    s2 = least_squares(res, s1.x, args=(False, campi), max_nfev=800)
    if best is None or s2.cost < best.cost: best = s2
x0 = np.concatenate([best.x, [1, 1, 1, 1]])
s3 = least_squares(res, x0, args=(True, campi), max_nfev=2000, x_scale=[1, 1, 1, 10, .01, .01, .01, .01])
S = mk(s3.x, True); zi = s3.x[3]
grid = [(fx, fy) for fx in (0, 0.46, 0.92) for fy in (0, 0.43, 0.86, 1.29, 1.725)]
W = np.array([K.wfe_rms(S, fx, fy, zi, pupil)[0]*1e6 for fx, fy in grid]).reshape(3, 5)
print(f"f1 {f1} d1 {d1} e {e}: EFL {K.efl_abs(S):.1f}  zi {zi:.2f}  R {1/S['c1']:.1f} {1/S['c2']:.1f} {1/S['c3']:.1f}  k {S['k1']:.3f} {S['k2']:.3f} {S['k3']:.3f}  z3 {S['z3']:.1f}")
print("WFE nm rms, righe traverso 0/0,46/0,92 gradi, colonne lungo traccia 0..1,725 gradi"); print(np.round(W, 1))
json.dump(dict(S=S, zi=zi), open(f'sol_{int(f1)}_{int(d1)}_{int(e)}.json', 'w'))
