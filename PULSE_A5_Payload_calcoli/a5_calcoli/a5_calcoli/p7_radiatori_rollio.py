# A5.P7 bis - radiatori del payload (D-095) con l'assetto di D-106 (Giuliano): ali a zenit, rollio fisso ottimo
# verso il Sole in attesa e in spinta (31-52 gradi), nadir per le riprese.
# Usa le funzioni di Giuliano (PULSE_EPS/A5.6/luce_eclisse.py: Sole, orbita, ombra) e il modello di p7_radiatori_stima.py.
# Uso: python p7_radiatori_rollio.py <cartella PULSE_EPS/A5.6>
# Riferimento locale (come pannelli_config.py): X velocita', Y normale all'orbita lato Sole, Z zenit.
# Radiatori sulla faccia -Y. Rollio phi verso il Sole (ali verso Y): la normale -Y diventa (0, -cos phi, sin phi),
# cioe' si inclina verso lo ZENIT (vede MENO Terra, ma puo' vedere il Sole).
import sys, os, numpy as np
sys.path.insert(0, sys.argv[1])
from luce_eclisse import sole, una_orbita, illuminazione, PERIODO
sig, Re, h = 5.670e-8, 6378.0, 302.0
eps, alfa, IR, S, alb = 0.85, 0.20, 237.0, 1361.0, 0.30     # come p7_radiatori_stima.py
def vf_terra(incl_deg, n=200000, seed=1):
    rng = np.random.default_rng(seed); u = rng.random(n); v = rng.random(n)
    th = np.arcsin(np.sqrt(u)); ph = 2*np.pi*v
    d = np.stack([np.sin(th)*np.cos(ph), np.sin(th)*np.sin(ph), np.cos(th)], 1)
    a = np.radians(incl_deg); R = np.array([[np.cos(a), 0, np.sin(a)], [0, 1, 0], [-np.sin(a), 0, np.cos(a)]])
    return np.mean((d @ R.T)[:, 2] > np.cos(np.arcsin(Re/(Re + h))))
G = np.loadtxt(os.path.join(sys.argv[1], "risultati/gmat_ltdn_inclinazione.csv"), delimiter=",")
jd0 = 2461042.0417
righe = []
for k in range(0, len(G), 5):
    giorno, inc, raan, ltdn = G[k]
    s_dir, s_dist, _ = sole(jd0 + giorno)
    t, u, r, n_hat = una_orbita(jd0 + giorno, raan, inc, passo=10.0)
    L = illuminazione(r, s_dir, s_dist) > 0.5
    zz = r / np.linalg.norm(r, axis=1)[:, None]; yy = np.repeat(n_hat[None, :], len(r), 0); xx = np.cross(yy, zz)
    sx, sy, sz = xx @ s_dir, yy @ s_dir, zz @ s_dir
    if sy.mean() < 0: sy = -sy
    beta = np.degrees(np.arcsin(sy.mean()))
    phis = np.radians(np.arange(0, 61, 1))
    phi = phis[int(np.argmax([np.clip(np.cos(p)*sz + np.sin(p)*sy, 0, None)[L].mean() for p in phis]))]
    cr = -np.cos(phi)*sy + np.sin(phi)*sz                      # coseno Sole-normale del radiatore
    c = np.where(L, np.clip(cr, 0, None), 0)
    righe.append((giorno, beta, np.degrees(phi), (c > 0).mean()*PERIODO/60, np.degrees(np.arccos(c.max())) if c.max() > 0 else 90,
                  c.mean(), vf_terra(90 + np.degrees(phi))))
R = np.array(righe)
print(f"beta {R[:,1].min():.1f}-{R[:,1].max():.1f} gradi; rollio ottimo {R[:,2].min():.0f}-{R[:,2].max():.0f} gradi")
print(f"vista della Terra del radiatore in attesa: {R[:,6].min():.2f}-{R[:,6].max():.2f} (a nadir 0,31)")
print(f"Sole sul radiatore in attesa: {R[:,3].min():.0f}-{R[:,3].max():.0f} min per orbita, angolo minimo dalla normale {R[:,4].min():.0f}-{R[:,4].max():.0f} gradi")
print(f"coseno medio sull'orbita: {R[:,5].min():.3f}-{R[:,5].max():.3f}")
# flusso medio assorbito sull'orbita (W/m2): Sole + IR Terra + albedo (luce ~60% dell'orbita, albedo dimezzato come in p7)
def assorbito(cmean, F, luce=0.6):
    return alfa*S*cmean + eps*IR*F + alfa*S*alb*F*0.5*luce
q_nadir = assorbito(0, 0.31)
q_att = [assorbito(cm, F) for cm, F in zip(R[:,5], R[:,6])]
print(f"\ncalore assorbito medio sull'orbita: a nadir {q_nadir:.0f} W/m2; in attesa con rollio {min(q_att):.0f}-{max(q_att):.0f} W/m2")
def T_eq(Q, A, qa):
    return ((Q/A + qa)/(eps*sig))**0.25 - 273.15
for nome, Q, A in (("sensore notturno spento (solo ~0,5 W dall'interno), 100 cm2", 0.5, 0.0100),
                   ("scheda spenta (~0,5 W dall'interno), 90 cm2", 0.5, 0.0090)):
    print(f"{nome}: equilibrio in attesa a nadir {T_eq(Q, A, q_nadir):.0f} C, con rollio {min(T_eq(Q, A, q) for q in q_att):.0f}..{max(T_eq(Q, A, q) for q in q_att):.0f} C")
# picco: Sole all'angolo minimo
cmax = np.cos(np.radians(R[:,4].min()))
print(f"picco di Sole sul radiatore (angolo {R[:,4].min():.0f} gradi): {alfa*S*cmax:.0f} W/m2 -> sensore {alfa*S*cmax*0.01:.2f} W, scheda {alfa*S*cmax*0.009:.2f} W")
# ripresa notturna: radiatore del sensore a nadir (F 0,31), parte dalla temperatura raggiunta in attesa
C = 0.15*900   # J/K sensore + radiatore + collegamento, stima
q0 = eps*sig*(263.15)**4 - eps*IR*0.31
print(f"\nripresa notturna a nadir: il radiatore a -10 C smaltisce {q0*0.01:.2f} W (carico 1,1 W, x1,5 1,65 W)")
for incl, nome in ((45, "rollio 45 gradi verso il lato del Sole (radiatore verso la Terra)"), (135, "rollio 45 gradi verso il lato opposto (radiatore verso lo zenit)")):
    F = vf_terra(incl); q = eps*sig*(263.15)**4 - eps*IR*F
    dT = max(1.65 - q*0.01, 0)*600/C
    print(f"ripresa notturna {nome}: F {F:.2f}, smaltisce {q*0.01:.2f} W a -10 C; con 1,65 W per 10 min sale di ~{dT:.1f} K (capacita' ~{C:.0f} J/K)")
# temperatura da spenti con perdita proporzionale alla differenza con l'interno (G = 0,5 W / 30 K, interno 20 C)
from scipy.optimize import brentq
G_c = 0.5/30.0
def T_spento(A, qa, Tint=20.0, G=G_c):
    f = lambda T: A*(eps*sig*(T + 273.15)**4 - qa) - G*(Tint - T)
    return brentq(f, -150, 50)
print("\ncon perdita verso l'interno proporzionale (G 0,017 W/K, interno 20 C):")
for nome, A in (("sensore notturno spento, 100 cm2", 0.0100), ("scheda spenta, 90 cm2", 0.0090)):
    print(f"  {nome}: a nadir {T_spento(A, q_nadir):.0f} C, in attesa con rollio {T_spento(A, min(q_att)):.0f}..{T_spento(A, max(q_att)):.0f} C")
for Tmin in (-30, -20):
    P = [A*(eps*sig*(Tmin + 273.15)**4 - min(q_att)) - G_c*(20 - Tmin) for A in (0.0100, 0.0090)]
    print(f"  riscaldatore per non scendere sotto {Tmin} C in attesa (caso freddo): sensore {P[0]:.1f} W, scheda {P[1]:.1f} W")
