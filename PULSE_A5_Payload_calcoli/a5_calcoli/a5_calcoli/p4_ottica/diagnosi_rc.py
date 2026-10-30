import sys, json; sys.path.insert(0, '.')
import numpy as np, rc
o = json.load(open(sys.argv[1])); v = o['v']; T = 5.0
S = [dict(z=0.0, c=v['c1'], k=v['k1'], tipo='M'), dict(z=-v['d1'], c=v['c2'], k=v['k2'], tipo='M'),
     dict(z=v['zl1'], c=v['a1'], tipo='L', mezzo='silice'), dict(z=v['zl1']+T, c=v['a2'], tipo='L', mezzo='aria'),
     dict(z=v['zl2'], c=v['a3'], tipo='L', mezzo='silice'), dict(z=v['zl2']+T, c=v['a4'], tipo='L', mezzo='aria')]
pu = rc.pupil_grid(120, 0.38, 20)
F = 700
for fy_mm in (0, 10, 20):
    fy = np.degrees(np.arctan(fy_mm/F))
    row = []
    for lam in (0.48, 0.6, 0.72):
        best = min((rc.wfe(S, 0, fy, v['zp']+dz, pu, lam)[0]*1e6, dz) for dz in np.linspace(-0.6, 0.6, 25))
        row.append(f"{lam}: {best[0]:.0f} nm @ dz {best[1]:+.2f}")
    # colore laterale: posizione Q per colore
    Qs = [rc.wfe(S, 0, fy, v['zp'], pu, lam)[1][1] for lam in (0.48, 0.6, 0.72)]
    print(f"campo y {fy_mm} mm: ", '; '.join(row), f"| colore laterale {1000*(max(Qs)-min(Qs)):.1f} um")
