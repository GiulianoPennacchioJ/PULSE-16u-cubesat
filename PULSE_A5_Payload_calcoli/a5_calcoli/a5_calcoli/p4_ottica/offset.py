# Korsch con campo spostato da un lato (lungo traccia): pan vicino all'asse, notte piu' lontana.
# Uso: python3 offset.py f1 d1 e yoff   (mm, mm, mm, gradi)
import sys, json; sys.path.insert(0, '.')
import numpy as np, korsch as K
from scipy.optimize import least_squares
from primo_ordine import soluzione
f1, d1, e, yoff = map(float, sys.argv[1:5])
F = 700.0; deg = lambda mm: np.degrees(mm/F)
pan = (yoff, yoff + deg(16.7)); notte = (pan[1] + deg(3.0), pan[1] + deg(3.0) + deg(22.5)); xm = deg(22.5/2)
P = soluzione(f1, d1, e)
pupil = K.pupil_grid(120.0, 0.30, 12)
base = dict(c1=-1/P['R1'], c2=-1/P['R2'], c3=-1/P['R3'], d1=d1, z3=P['z3'])
def mk(x):
    S = dict(base); S.update(k1=x[0], k2=x[1], k3=x[2], c1=base['c1']*x[4], c2=base['c2']*x[5], c3=base['c3']*x[6], z3=base['z3']*x[7]); return S
def pts(z, nx=3, ny=3): return [(fx, fy) for fx in np.linspace(0, xm, nx) for fy in np.linspace(z[0], z[1], ny)]
def res(x, sc):
    S = mk(x); r = []
    for (fx, fy), w8 in [(p, 1.0) for p in pts(pan)] + [(p, 0.3) for p in pts(notte)]:
        w = K.wfe_rms(S, fx*sc, fy*sc, x[3], pupil)[0]; r.append(w8*w*1e6 if np.isfinite(w) else 1e5)
    r.append((K.efl_abs(S) - F)*100); r.append((-S['c1'] + S['c2'] - S['c3'])*1e7)
    return np.array(r)
x = np.array([-1, -2.5, -0.5, P['zi'], 1, 1, 1, 1])
for sc in (0.0, 0.35, 0.7, 1.0):
    x = least_squares(res, x, args=(sc,), max_nfev=800, x_scale=[0.1]*4 + [1e-3]*4).x
S = mk(x); zi = x[3]; pupil2 = K.pupil_grid(120.0, 0.30, 20)
out = dict(S=S, zi=zi, pan=pan, notte=notte, yoff=yoff)
for nome, z in (('pan', pan), ('notte', notte)):
    W = []; SP = []
    for fx, fy in pts(z, 3, 5):
        w, s, Q = K.wfe_rms(S, fx, fy, zi, pupil2); W.append(w*1e6); SP.append(s*1000)
    out[nome] = dict(wfe_max=max(W), wfe_media=float(np.mean(W)), spot_max_um=max(SP))
    print(f"yoff {yoff}: {nome} WFE media {np.mean(W):.1f} max {max(W):.1f} nm (Strehl min {np.exp(-(2*np.pi*max(W)/550)**2):.2f}), spot RMS max {max(SP):.1f} um")
# separazione dei fasci in y tra immagine intermedia e terziario: andata (secondario->terziario) e ritorno (terziario->immagine)
pup = K.pupil_grid(120.0, 0.0, 20); lit = np.hypot(pup[:,0], pup[:,1]) >= 18
zs = np.linspace(10, S['z3'] - 15, 50)
fmax = np.full_like(zs, -1e9); fmin = np.full_like(zs, 1e9); rmin = np.full_like(zs, 1e9); rmax = np.full_like(zs, -1e9); R2 = R3 = 0
for fx, fy in [(a, b) for a in (-xm, 0, xm) for b in np.linspace(pan[0], notte[1], 6)]:
    p, d, L, h = K.trace(S, fx, fy, pup)
    R2 = max(R2, np.max(np.hypot(*h[1][lit][:, :2].T))); R3 = max(R3, np.max(np.hypot(*h[2][lit][:, :2].T)))
    a, b = h[1][lit], h[2][lit]; db = (b - a)/np.linalg.norm(b - a, axis=1)[:,None]
    for i, z in enumerate(zs):
        q = a + ((z - a[:,2])/db[:,2])[:,None]*db; fmax[i] = max(fmax[i], q[:,1].max()); fmin[i] = min(fmin[i], q[:,1].min())
        q = b + ((z - b[:,2])/d[lit,2])[:,None]*d[lit]; rmin[i] = min(rmin[i], q[:,1].min()); rmax[i] = max(rmax[i], q[:,1].max())
sep1 = rmin - fmax; sep2 = fmin - rmax; i = np.argmax(sep1); j = np.argmax(sep2)
print(f"secondario {2*R2:.1f} mm (ostruzione {R2/60:.2f} lin.), terziario {2*R3:.1f} mm, zi {zi:.1f}, z3 {S['z3']:.1f}")
print(f"separazione fasci: ritorno sopra {sep1[i]:.1f} mm a z {zs[i]:.1f}; ritorno sotto {sep2[j]:.1f} mm a z {zs[j]:.1f}")
out.update(R2=R2, R3=R3, sep1=float(sep1[i]), z_sep1=float(zs[i]), sep2=float(sep2[j]), z_sep2=float(zs[j]))
json.dump(out, open(f'off_{int(f1)}_{int(d1)}_{int(e)}_{yoff}.json', 'w'))
