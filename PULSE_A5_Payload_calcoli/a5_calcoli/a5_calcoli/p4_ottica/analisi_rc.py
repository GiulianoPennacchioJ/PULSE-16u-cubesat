# Analisi completa di una variante RC + correttore: MTF (diffrazione + aberrazioni), distorsione, tolleranze, SNR
import sys, json, copy, math; sys.path.insert(0, '.')
import numpy as np, rc
nome = sys.argv[1]; o = json.load(open(f'rc_{nome}.json')); g = json.load(open(f'rc_{nome}_geo.json'))
S = o['S']; F, D = 700.0, 120.0; N = F/D; eps = g['ostr']
deg = lambda mm: np.degrees(np.arctan(mm/F))
tot = 16.7 + 3.0 + 22.5; y0 = -tot/2; pan = (y0, y0 + 16.7); notte = (y0 + 19.7, tot/2); xm = 22.5/2
out = {}
# ---- MTF policromatica da pupilla (autocorrelazione via FFT)
n = 96; gg = (np.arange(n) - (n - 1)/2)*(D/n); X, Y = np.meshgrid(gg, gg); R = np.hypot(X, Y)
A = ((R <= D/2) & (R >= eps*D/2)).astype(float); m = A > 0; pts = np.stack([X[m], Y[m]], axis=1)
def mtf(fx, fy, zi, lams, nu, eps_ovr=None):
    vals = []
    for lam in lams:
        P = np.zeros((n, n), complex)
        if eps_ovr is None:
            w, Q, _ = rc.wfe(S, fx, fy, zi, pts, lam, vettore=False) if False else (None, None, None)
            p, d, L, _ = rc.trace(S, fx, fy, pts, lam)
            # OPD verso il miglior punto (stesso metodo di rc.wfe)
            _, Q, _ = rc.wfe(S, fx, fy, zi, pts, lam)
            r = np.sqrt((p[:,0]-Q[0])**2 + (p[:,1]-Q[1])**2 + (p[:,2]-zi)**2); W = L + r; W -= W.mean()
            P[m] = np.exp(2j*np.pi*W/(lam*1e-3))
        else:
            Rm = (R <= D/2) & (R >= eps_ovr*D/2); P[Rm] = 1.0
        M = 2*n; Pp = np.zeros((M, M), complex); Pp[:n, :n] = P
        otf = np.fft.ifft2(np.abs(np.fft.fft2(Pp))**2); otf = np.abs(otf)/np.abs(otf[0, 0])
        k = nu*lam*1e-3*N*n                               # spostamento in campioni della pupilla
        k0 = int(np.floor(k)); a = k - k0
        mx = (1 - a)*otf[0, k0] + a*otf[0, k0 + 1]; my = (1 - a)*otf[k0, 0] + a*otf[k0 + 1, 0]
        vals.append((mx, my))
    v = np.mean(vals, axis=0); return float(v[0]), float(v[1])
nyq_pan, nyq_n = 1/(2*3.45e-3), 1/(2*11e-3)
LP, LN = (0.48, 0.60, 0.72), (0.50, 0.65, 0.85)
res = {}
for zona, zz, lams, zi, nyq in (('pan', pan, LP, o['zp'], nyq_pan), ('notte', notte, LN, o['zn'], nyq_n)):
    righe = []
    for etich, fx, fy in (('centro', 0, (zz[0] + zz[1])/2), ('bordo', xm, (zz[0] + zz[1])/2), ('angolo', xm, zz[0] if abs(zz[0]) > abs(zz[1]) else zz[1])):
        mx, my = mtf(deg(fx), deg(fy), zi, lams, nyq)
        righe.append((etich, round(mx, 3), round(my, 3)))
    ideale = mtf(0, 0, zi, lams, nyq, eps_ovr=eps); p2 = mtf(0, 0, zi, lams, nyq, eps_ovr=0.30)
    res[zona] = dict(righe=righe, diffrazione_ombra_vera=round(ideale[0], 3), diffrazione_ombra_P2=round(p2[0], 3))
    print(f"MTF ottica a Nyquist {zona} ({nyq:.0f} cicli/mm): {righe}; solo diffrazione con ombra {eps:.2f}: {ideale[0]:.3f}; con ombra 0,30 (ipotesi P2): {p2[0]:.3f}")
out['mtf'] = res
# ---- distorsione (raggio principale a 0,6 um)
dist = []
for fy in (pan[0], 0.0, notte[1]):
    p, d, L, _ = rc.trace(S, deg(xm), deg(fy), np.array([[0.0, 0.0]]), 0.6)
    t = (o['zp'] - p[:,2])/d[:,2]; q = p + t[:,None]*d
    r_real = math.hypot(q[0,0], q[0,1]); r_id = math.hypot(xm, fy)
    dist.append(100*(r_real - r_id)/r_id)
print(f"distorsione agli angoli: {[round(x, 2) for x in dist]} %  (in pixel pan all'angolo: {max(abs(x) for x in dist)/100*math.hypot(xm, tot/2)/3.45e-3:.0f} px)")
out['distorsione_pct'] = dist
# ---- tolleranze: errore d'onda medio sul pan con secondario spostato/decentrato (con rifocalizzazione)
pupil = rc.pupil_grid(D, eps, 14)
def wfe_medio(Sx, zi):
    W = []
    for fx in (0, xm):
        for fy in (pan[0], (pan[0] + pan[1])/2, pan[1]):
            W.append(rc.wfe(Sx, deg(fx), deg(fy), zi, pupil, 0.6)[0]*1e6)
    return np.mean(W)
def best_focus(Sx):
    return min((wfe_medio(Sx, o['zp'] + dz), dz) for dz in np.linspace(-0.3, 0.3, 13))
base = best_focus(S); print(f"riferimento (0,6 um): {base[0]:.1f} nm")
tol = {}
for nomet, campo, val in (('distanza secondario', 'z', 0.01), ('distanza secondario', 'z', 0.03), ('decentramento secondario', 'dx', 0.02), ('decentramento secondario', 'dx', 0.05),
                          ('decentramento lente 1', 'dx', 0.05), ('decentramento lente 1', 'dx', 0.1)):
    Sx = copy.deepcopy(S)
    idx = 1 if 'secondario' in nomet else 2
    if campo == 'z': Sx[1]['z'] -= val
    else:
        for j in ((idx,) if idx == 1 else (2, 3)): Sx[j]['dx'] = val
    w, dz = best_focus(Sx); tol[f'{nomet} {val} mm'] = (round(w, 1), round(dz, 2))
    print(f"{nomet} {val*1000:.0f} um: errore d'onda medio {w:.1f} nm (rifuoco {dz:+.2f} mm)")
out['tolleranze'] = tol
# fuoco: quanto si puo' sbagliare
for dz in (0.02, 0.05, 0.1):
    print(f"sensore fuori fuoco di {dz*1000:.0f} um: {wfe_medio(S, o['zp'] + base[1] + dz):.1f} nm")
json.dump(out, open(f'analisi_{nome}.json', 'w'))
