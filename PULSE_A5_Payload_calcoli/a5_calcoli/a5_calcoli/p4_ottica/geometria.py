# Ingombri: diametri degli specchi, foro del primario, immagine intermedia, posizione dello specchio di rinvio con foro
import sys, json; sys.path.insert(0, '.')
import numpy as np, korsch as K
sol = json.load(open(sys.argv[1])); S = sol['S']; zi = sol['zi']
F = 700.0; deg = lambda mm: np.degrees(mm/F)
pan, notte = sol['pan'], sol['notte']
ymin, ymax = deg(min(pan[0], notte[0])), deg(max(pan[1], notte[1])); xm = deg(22.5/2)
campi = [(fx, fy) for fx in np.linspace(-xm, xm, 5) for fy in np.linspace(ymin, ymax, 9)]
pup = K.pupil_grid(120.0, 0.0, 28)                       # pupilla piena per i bordi
r = np.hypot(pup[:,0], pup[:,1]); eps = 0.30
lit = r >= eps*60
R1o = R2 = R3 = 0; fwd = []; ret = []
zs = np.linspace(S['k1']*0 + 15, S['z3'] - 10, 60)
rf = np.zeros_like(zs); rr = np.full_like(zs, 1e9); Rprim_hole = 0
for fx, fy in campi:
    p, d, L, h = K.trace(S, fx, fy, pup)
    R1o = max(R1o, np.max(np.hypot(h[0][:,0], h[0][:,1])))
    R2 = max(R2, np.max(np.hypot(h[1][lit,0], h[1][lit,1])))
    R3 = max(R3, np.max(np.hypot(h[2][lit,0], h[2][lit,1])))
    # fascio secondario -> terziario (in avanti, +z)
    a, b = h[1][lit], h[2][lit]; db = (b - a); db /= np.linalg.norm(db, axis=1)[:,None]
    t0 = (0 - a[:,2])/db[:,2]; q0 = a + t0[:,None]*db
    Rprim_hole = max(Rprim_hole, np.max(np.hypot(q0[:,0], q0[:,1])))
    for i, z in enumerate(zs):
        t = (z - a[:,2])/db[:,2]; q = a + t[:,None]*db
        rf[i] = max(rf[i], np.max(np.hypot(q[:,0], q[:,1])))
        t = (z - b[:,2])/d[lit,2]; q = b + t[:,None]*d[lit]
        rr[i] = min(rr[i], np.min(np.hypot(q[:,0], q[:,1])))
i = np.argmax(rr - rf)
print(f"diametri utili: primario {2*R1o:.1f} mm, secondario {2*R2:.1f} mm (ostruzione lineare {R2/60:.2f}, area {(R2/60)**2*100:.1f}%), terziario {2*R3:.1f} mm")
print(f"foro del primario >= {2*Rprim_hole:.1f} mm")
print(f"specchio di rinvio: miglior posizione z = {zs[i]:.1f} mm, foro {2*rf[i]:.1f} mm, fascio di ritorno libero dentro {2*rr[i]:.1f} mm -> {'OK' if rr[i] >= rf[i] else 'TAGLIA il fascio'}")
# perdita di luce se il foro taglia il fascio di ritorno
loss = []
for fx, fy in campi:
    p, d, L, h = K.trace(S, fx, fy, pup)
    b = h[2][lit]; t = (zs[i] - b[:,2])/d[lit,2]; q = b + t[:,None]*d[lit]
    loss.append(np.mean(np.hypot(q[:,0], q[:,1]) < rf[i]))
print(f"luce persa nel foro del rinvio: max {100*max(loss):.1f}%, media {100*np.mean(loss):.1f}%")
print(f"immagine finale a z = {zi:.1f}: distanza laterale dopo il rinvio ~{zs[i]-zi:.0f} mm; terziario a {S['z3']-zs[i]:.0f} mm dal rinvio")
print(f"lunghezze: secondario a {S['d1']:.0f} mm davanti al primario, terziario a {S['z3']:.0f} mm dietro (srotolato)")
