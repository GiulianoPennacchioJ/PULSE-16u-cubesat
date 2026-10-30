# A5.P7 - sensibilita' del fuoco del telescopio RC (rc_200_70_3.json) a temperatura e umidita' (tracciamento parassiale)
import sys, json, copy; sys.path.insert(0, '.')
import numpy as np, rc
d = json.load(open('rc_200_70_3.json')); S0, zp = d['S'], d['zp']
def fuoco(S):
    p, dd, L, _ = rc.trace(S, 0, 0, np.array([[0.0, 2.0]]), 0.6)     # raggio parassiale a 2 mm
    t = -p[0, 1]/dd[0, 1]; return p[0, 2] + t*dd[0, 2]                # z dove taglia l'asse
f0 = fuoco(S0)
def sposta(mod):
    S = copy.deepcopy(S0); mod(S); return (fuoco(S) - f0)*1000      # um
# 1) distanza primario-secondario +1 um (secondario verso il cielo: z piu' negativo)
k_sp = sposta(lambda S: S[1].update(z=S[1]['z'] - 1e-3))
# 2) dilatazione uniforme degli specchi (raggi di curvatura) di 1 ppm
def scala_specchi(S, e=1e-6):
    for s in S[:2]: s['c'] = s['c']/(1 + e)
k_sp_ppm = sposta(scala_specchi)
# 3) lenti e distanza primario-sensori: il piano dei sensori si muove direttamente (1:1)
print(f"fuoco nominale z = {f0:.3f} mm (piano sensori {zp:.3f})")
print(f"distanza primario-secondario +1 um -> fuoco {k_sp:+.1f} um")
print(f"specchi +1 ppm (raggi) -> fuoco {k_sp_ppm:+.2f} um")
L_sp, L_back = abs(S0[1]['z']), zp + 10           # mm: distanziale del secondario, primario->sensori (con la piastra)
casi = {  # coefficienti di dilatazione (ppm/K)
 "specchi Zerodur 0,05 + tubo carbonio 0,5 + attacco sensori Ti 8,6 (via Invar 1,2 nei 70 mm)": (0.05, 0.5, 1.2),
 "specchi borosilicato 3,3 + tubo carbonio 0,5 + Invar 1,2": (3.3, 0.5, 1.2),
 "specchi Zerodur + tubo carbonio 2,0 (laminato non ottimizzato) + Invar": (0.05, 2.0, 1.2),
 "specchi Zerodur + tubo alluminio 23": (0.05, 23.0, 23.0),
}
budget = 37.0/2                                     # meta' della tolleranza DR-03 al termico, l'altra meta' a montaggio/gravita'
for nome, (am, at, ab) in casi.items():
    s = abs(k_sp*L_sp*at*1e-3 + k_sp_ppm*am - L_back*ab*1e-3)    # um/K (segni: tubo piu' lungo e piano sensori che si allontana)
    print(f"{nome}: {s:.2f} um/K -> escursione ammessa +-{budget/s:.0f} K")
# umidita' del carbonio: rilascio in vuoto (dilatazione da umidita' tipica 20-100 ppm, TBC)
for cme in (20, 50, 100):
    dz = abs(k_sp*L_sp*cme*1e-3)
    print(f"tubo in carbonio che si accorcia di {cme} ppm (umidita' persa in vuoto): fuoco {dz:.0f} um")
# opzione: aste distanziatrici in Invar (1,2 ppm/K, non assorbono umidita') tra primario e secondario, tubo in carbonio solo come guscio
s_inv = abs(k_sp*L_sp*1.2*1e-3 + k_sp_ppm*0.05 - L_back*1.2*1e-3)
print(f"aste Invar + specchi Zerodur + Invar dietro: {s_inv:.2f} um/K -> escursione ammessa +-{budget/s_inv:.0f} K; umidita' 0 um")
m_aste = 4*np.pi*(3.0e-1)**2*(L_sp/10)*8.1/1000
print(f"4 aste Invar diametro 6 mm x {L_sp:.0f} mm: {m_aste*1000:.0f} g")
