import sys, json; sys.path.insert(0, '.')
import numpy as np, korsch as K
from scipy.optimize import least_squares
D, EPS, F = 120.0, 0.30, 700.0
pupil = K.pupil_grid(D, EPS, 20)
# campo: rettangolo 1,84 (traverso) x 3,45 gradi (lungo traccia), centrato sull'asse
FX, FY = 0.92, 1.725
campi = [(fx, fy) for fx in np.linspace(0, FX, 3) for fy in np.linspace(-FY, FY, 7)]
nomi = ['c1','c2','c3','k1','k2','k3','z3','zi']
d1 = float(sys.argv[1]) if len(sys.argv) > 1 else 110.0
x0 = np.array([-1/288, -1/90.9, -1/110, -1.0, -2.0, -0.5, 125.0, 2.8])
def sysd(x):
    S = dict(zip(nomi[:7], x[:7])); S['d1'] = d1; return S
def res(x):
    S = sysd(x); r = []
    for fx, fy in campi:
        w, s, Q = K.wfe_rms(S, fx, fy, x[7], pupil)
        r.append(w*1e6 if np.isfinite(w) else 1e4)           # nm
    r.append((K.efl_abs(S) - F)*50)                          # vincolo focale
    return np.array(r)
sol = least_squares(res, x0, x_scale=np.abs(x0)+1e-3, max_nfev=3000)
S = sysd(sol.x); zi = sol.x[7]
print('d1', d1, 'EFL', round(K.efl_abs(S), 2), 'zi', round(zi, 2))
print({k: round(v, 6) for k, v in zip(nomi, sol.x)}, 'R1 R2 R3', [round(1/S[c], 2) for c in ('c1','c2','c3')])
W = res(sol.x)[:-1].reshape(3, 7)
print('WFE nm rms (righe fx 0, 0.46, 0.92; colonne fy -1.725..1.725)'); print(np.round(W, 1))
json.dump(dict(S=S, zi=zi), open(f'sol_d1_{int(d1)}.json', 'w'))
