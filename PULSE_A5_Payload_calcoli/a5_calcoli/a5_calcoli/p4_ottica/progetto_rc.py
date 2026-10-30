# Progetto del telescopio PULSE: Ritchey-Chretien (2 specchi) + correttore di campo a lenti in silice fusa.
# Campo completo: sensore pan 22,3 x 16,7 mm + spazio 3 mm + sensore notte 22,5 x 22,5 mm, affiancati lungo traccia.
# Uso: python3 progetto_rc.py f1 b nlenti   (focale del primario mm, immagine dietro il primario mm, 2 o 3 lenti)
import sys, json; sys.path.insert(0, '.')
import numpy as np, rc
from scipy.optimize import least_squares
f1, b, NL = float(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3])
F, D, T = 700.0, 120.0, 5.0
deg = lambda mm: np.degrees(np.arctan(mm/F))
tot = 16.7 + 3.0 + 22.5; y0 = -tot/2
pan = (y0, y0 + 16.7); notte = (y0 + 19.7, tot/2); xm = 22.5/2
m = F/f1; d1 = (m*f1 - b)/(1 + m); s, sp = f1 - d1, d1 + b; R2 = 2/(1/s - 1/sp)
# variabili: c1, c2 (x1e-3), k1, k2, d1, curvature lenti (x1e-3), z prima lente, spazi tra lenti, spazio all'immagine, fuoco notte
nomi = ['c1', 'c2', 'k1', 'k2', 'd1'] + [f'a{i}' for i in range(2*NL)] + ['z1'] + [f'g{i}' for i in range(NL - 1)] + ['gi', 'dzn']
x0 = [-1e3/(2*f1), -1e3/R2, -1.05, -3.0, d1] + [0.0]*(2*NL) + [b - 15 - NL*(T + 10)] + [10.0]*(NL - 1) + [12.0, 0.0]
lo = [-np.inf]*5 + [-30]*(2*NL) + [-40] + [3.0]*(NL - 1) + [8.0, -2]
hi = [np.inf]*5 + [30]*(2*NL) + [b] + [60.0]*(NL - 1) + [40.0, 2]
def sistema(x):
    v = dict(zip(nomi, x))
    S = [dict(z=0.0, c=v['c1']*1e-3, k=v['k1'], tipo='M'), dict(z=-v['d1'], c=v['c2']*1e-3, k=v['k2'], tipo='M')]
    z = v['z1']
    for i in range(NL):
        S += [dict(z=z, c=v[f'a{2*i}']*1e-3, tipo='L', mezzo='silice'), dict(z=z + T, c=v[f'a{2*i+1}']*1e-3, tipo='L', mezzo='aria')]
        z += T + (v[f'g{i}'] if i < NL - 1 else 0)
    zp = z + v['gi']; return v, S, zp, zp + v['dzn']
LP, LN = (0.48, 0.60, 0.72), (0.50, 0.65, 0.85)
def campi(z, nx=3, ny=3, sc=1.0):
    return [(deg(fx)*sc, deg(fy)*sc) for fx in np.linspace(0, xm, nx) for fy in np.linspace(z[0], z[1], ny)]
pupil = rc.pupil_grid(D, 0.38, 12)
def res(x, sc):
    v, S, zp, zn = sistema(x); r = []
    for gruppo, lams, zi, w8 in ((pan, LP, zp, 1.0), (notte, LN, zn, 0.3)):
        for fx, fy in campi(gruppo, sc=sc):
            Q0 = None
            for lam in lams:
                w, Q, P = rc.wfe(S, fx, fy, zi, pupil, lam, Q=Q0, vettore=True)
                if Q0 is None: Q0 = Q
                r.extend(np.where(np.isfinite(w), w8*w*1e6, 1e3))
    r.append((rc.efl(S) - F)*20)
    return np.array(r)
x = np.array(x0)
for sc in (0.0, 0.3, 0.6, 0.8, 1.0):
    sol = least_squares(res, x, args=(sc,), bounds=(lo, hi), x_scale='jac', max_nfev=400); x = sol.x
    rr = res(x, sc); print(f"  scala {sc}: WFE rms tot {np.sqrt(np.sum(rr[:-1]**2)/ (len(rr)//len(pupil) or 1)):.0f}, EFL {rc.efl(sistema(x)[1]):.1f}", flush=True)
v, S, zp, zn = sistema(x)
pupil2 = rc.pupil_grid(D, 0.38, 20)
out = dict(v={k: float(val) for k, val in v.items()}, f1=f1, b=b, NL=NL, S=S, zp=zp, zn=zn)
print(f"f1 {f1} b {b} lenti {NL}: EFL {rc.efl(S):.1f}, d1 {v['d1']:.1f}, R1 {1e3/v['c1']:.1f}, R2 {1e3/v['c2']:.1f}, k1 {v['k1']:.3f}, k2 {v['k2']:.3f}, fuoco pan z {zp:.1f}, notte z {zn:.1f}")
print("  superfici lenti (z, R):", [(round(s_['z'], 1), round(1/s_['c'], 1) if abs(s_['c']) > 1e-7 else 'piano') for s_ in S[2:]])
for nome, gruppo, lams, zi in (('pan', pan, LP, zp), ('notte', notte, LN, zn)):
    W = []
    for fx, fy in campi(gruppo, 3, 5):
        Q0 = None
        for lam in lams:
            w, Q, P = rc.wfe(S, fx, fy, zi, pupil2, lam, Q=Q0); Q0 = Q if Q0 is None else Q0; W.append(w*1e6)
    W = np.array(W); st = np.exp(-(2*np.pi*W.max()/550)**2)
    print(f"  {nome}: errore d'onda RMS medio {W.mean():.1f} nm, massimo {W.max():.1f} nm (Strehl min a 550 nm {st:.2f})")
    out[nome] = dict(wfe_media=float(W.mean()), wfe_max=float(W.max()))
json.dump(out, open(f'rc_{int(f1)}_{int(b)}_{NL}.json', 'w'))
