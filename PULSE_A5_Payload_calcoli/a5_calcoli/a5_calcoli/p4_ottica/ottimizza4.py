# Ottimizzazione con i due sensori nel campo. Disposizione 'centro' o 'pan_in_asse'.
import sys, json; sys.path.insert(0, '.')
import numpy as np, korsch as K
from scipy.optimize import least_squares
from primo_ordine import soluzione
f1, d1, e = map(float, sys.argv[1:4]); lay = sys.argv[4]
F = 700.0; deg = lambda mm: np.degrees(mm/F)
pan_w, pan_h, gap, ng = 22.3, 16.7, 3.0, 22.5          # mm (A2)
if lay == 'centro':
    tot = pan_h + gap + ng; y0 = -tot/2
    pan = (y0, y0+pan_h); notte = (y0+pan_h+gap, tot/2)
else:   # pan centrato sull'asse
    pan = (-pan_h/2, pan_h/2); notte = (pan_h/2+gap, pan_h/2+gap+ng)
fx_max = deg(pan_w/2)
def punti(z, n):
    return [(fx, fy) for fx in np.linspace(0, fx_max, 3) for fy in np.linspace(deg(z[0]), deg(z[1]), n)]
P = soluzione(f1, d1, e)
pupil = K.pupil_grid(120.0, 0.30, 16)
base = dict(c1=-1/P['R1'], c2=-1/P['R2'], c3=-1/P['R3'], d1=d1, z3=P['z3'])
def mk(x):
    S = dict(base)
    S.update(k1=x[0], k2=x[1], k3=x[2], c1=base['c1']*x[4], c2=base['c2']*x[5], c3=base['c3']*x[6], z3=base['z3']*x[7])
    return S
def res(x, cp, cn):
    S = mk(x); r = []
    for fx, fy in cp:
        w = K.wfe_rms(S, fx, fy, x[3], pupil)[0]; r.append(w*1e6 if np.isfinite(w) else 1e5)
    for fx, fy in cn:   # notte: pixel 11 um, conta meno (peso 0,3)
        w = K.wfe_rms(S, fx, fy, x[3], pupil)[0]; r.append(0.3*w*1e6 if np.isfinite(w) else 1e5)
    r.append((K.efl_abs(S) - F)*100); r.append((-S['c1'] + S['c2'] - S['c3'])*1e7)
    return np.array(r)
x = np.array([-1, -2.5, -0.5, P['zi'], 1, 1, 1, 1])
for sc in (0.0, 0.3, 0.6, 0.85, 1.0):
    cp = [(a*sc, b*sc) for a, b in punti(pan, 4)]; cn = [(a*sc, b*sc) for a, b in punti(notte, 4)]
    s = least_squares(res, x, args=(cp, cn), max_nfev=1500, x_scale=[0.1, 0.1, 0.1, 0.1, 1e-3, 1e-3, 1e-3, 1e-3]); x = s.x
S = mk(x); zi = x[3]
pupil2 = K.pupil_grid(120.0, 0.30, 24)
out = dict(S=S, zi=zi, lay=lay, pan=pan, notte=notte)
for nome, z in (('pan', pan), ('notte', notte)):
    W = []; SP = []
    for fx, fy in punti(z, 5):
        w, s, Q = K.wfe_rms(S, fx, fy, zi, pupil2); W.append(w*1e6); SP.append(s*1000)
    out[nome] = dict(wfe_max=max(W), wfe_media=float(np.mean(W)), spot_rms_max_um=max(SP))
    strehl = np.exp(-(2*np.pi*max(W)/550)**2)
    print(f"{lay} {nome}: WFE media {np.mean(W):.1f} nm, max {max(W):.1f} nm (Strehl min {strehl:.2f}), spot RMS max {max(SP):.1f} um")
print(f"EFL {K.efl_abs(S):.1f}  zi {zi:.2f}  R {1/S['c1']:.1f} {1/S['c2']:.1f} {1/S['c3']:.1f}  k {S['k1']:.3f} {S['k2']:.3f} {S['k3']:.3f}  z3 {S['z3']:.1f}")
json.dump(out, open(f'sol_{lay}_{int(f1)}_{int(d1)}_{int(e)}.json', 'w'))
