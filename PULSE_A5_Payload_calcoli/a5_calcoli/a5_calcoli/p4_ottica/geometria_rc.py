# Ingombri del Ritchey-Chretien + correttore: secondario, foro del primario, lenti, lunghezza, ombra centrale
import sys, json; sys.path.insert(0, '.')
import numpy as np, rc
o = json.load(open(sys.argv[1])); S = o['S']; F = 700.0
deg = lambda mm: np.degrees(np.arctan(mm/F))
tot = 16.7 + 3.0 + 22.5; xm = 22.5/2
campi = [(deg(fx), deg(fy)) for fx in (-xm, 0, xm) for fy in np.linspace(-tot/2, tot/2, 7)]
pup = rc.pupil_grid(120.0, 0.0, 30); r = np.hypot(pup[:,0], pup[:,1])
eps_list = []
R = np.zeros(len(S)); hole = 0
for fx, fy in campi:
    p, d, L, h = rc.trace(S, fx, fy, pup, 0.6)
    for i, q in enumerate(h): R[i] = max(R[i], np.max(np.hypot(q[:,0], q[:,1])))
    a, b = h[1], h[2]; db = (b - a)/np.linalg.norm(b - a, axis=1)[:,None]
    q0 = a + ((0 - a[:,2])/db[:,2])[:,None]*db; hole = max(hole, np.max(np.hypot(q0[:,0], q0[:,1])))
ostr = max(R[1], hole)/60
print(f"secondario {2*R[1]:.1f} mm, foro del primario {2*hole:.1f} mm -> ombra centrale {ostr:.2f} lineare, {100*ostr**2:.1f}% dell'area (+ ~1% bracci)")
print("lenti (diametro utile):", [round(2*R[i], 1) for i in range(2, len(S), 2)])
zs = [s['z'] for s in S]
print(f"secondario a {-zs[1]:.0f} mm davanti al primario; immagine a {o['zp']:.0f} mm dietro; lunghezza ottica {o['zp'] - zs[1]:.0f} mm (+ spessore primario e paraluce)")
json.dump(dict(sec=2*R[1], foro=2*hole, ostr=ostr, lenti=[2*R[i] for i in range(2, len(S), 2)], lung=o['zp'] - zs[1]), open(sys.argv[1].replace('.json', '_geo.json'), 'w'))
