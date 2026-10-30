# Disegno in sezione del telescopio scelto (raggi in 3 campi) e verifica finale con l'ombra vera
import sys, json; sys.path.insert(0, '.')
import numpy as np, rc, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
o = json.load(open(sys.argv[1])); g = json.load(open(sys.argv[1].replace('.json', '_geo.json'))); S = o['S']; F = 700.0
deg = lambda mm: np.degrees(np.arctan(mm/F))
eps = g['ostr']; pupil = rc.pupil_grid(120.0, eps, 22)
tot = 16.7 + 3.0 + 22.5; y0 = -tot/2; pan = (y0, y0 + 16.7); notte = (y0 + 19.7, tot/2); xm = 22.5/2
for nome, z, lams, zi in (('pan', pan, (0.48, 0.6, 0.72), o['zp']), ('notte', notte, (0.5, 0.65, 0.85), o['zn'])):
    W = []
    for fx in np.linspace(0, xm, 3):
        for fy in np.linspace(z[0], z[1], 5):
            Q0 = None
            for lam in lams:
                w, Q, P = rc.wfe(S, deg(fx), deg(fy), zi, pupil, lam, Q=Q0); Q0 = Q if Q0 is None else Q0; W.append(w*1e6)
    W = np.array(W)
    print(f"{nome} (ombra vera {eps:.2f}): errore d'onda medio {W.mean():.1f} nm, massimo {W.max():.1f} nm, Strehl medio {np.exp(-(2*np.pi*W.mean()/550)**2):.2f}, minimo {np.exp(-(2*np.pi*W.max()/550)**2):.2f}")
fig, ax = plt.subplots(figsize=(11, 4.2))
def profilo(s, R):
    y = np.linspace(-R, R, 200); c, k = s['c'], s.get('k', 0.0)
    zz = c*y**2/(1 + np.sqrt(np.maximum(1 - (1 + k)*c**2*y**2, 1e-9))); return s['z'] + zz, y
Rs = [60, g['sec']/2] + [r/2 + 2 for r in g['lenti'] for _ in (0, 1)]
for i, s in enumerate(S):
    zz, y = profilo(s, Rs[i])
    if i == 0:
        m = np.abs(y) >= g['foro']/2; ax.plot(np.where(m, zz, np.nan), y, 'k', lw=2.5)
    else:
        ax.plot(zz, y, 'k' if s['tipo'] == 'M' else 'tab:blue', lw=2.5 if s['tipo'] == 'M' else 1.5)
col = {0: 'tab:green', 1: 'tab:orange', 2: 'tab:red'}
yy = np.linspace(-60, 60, 9); yy = yy[np.abs(yy) >= eps*60 + 1]
for j, fy in enumerate((pan[0], 0.0, notte[1])):
    pu = np.stack([np.zeros_like(yy), yy], axis=1)
    p, d, L, h = rc.trace(S, 0, deg(fy), pu, 0.6)
    start = h[0] - 250*np.array([0, np.tan(np.radians(deg(fy))), 1.0])
    pts = [start] + h + [p + ((o['zp'] - p[:,2])/d[:,2])[:,None]*d]
    for k_ in range(len(yy)):
        ax.plot([q[k_, 2] for q in pts], [q[k_, 1] for q in pts], color=col[j], lw=0.6)
ax.axvline(o['zp'], color='gray', ls=':'); ax.text(o['zp'] + 2, 50, 'sensori', fontsize=8)
ax.set_xlabel('mm lungo l\'asse (0 = vertice del primario; la luce arriva da sinistra)'); ax.set_ylabel('mm')
ax.set_title('PULSE: Ritchey-Chrétien 12 cm + correttore a 3 lenti, f 700 mm, campo 3,9°')
ax.set_aspect('equal'); ax.set_xlim(-260, o['zp'] + 20); ax.set_ylim(-70, 70)
plt.tight_layout(); plt.savefig(sys.argv[2], dpi=150); print('disegno salvato')
