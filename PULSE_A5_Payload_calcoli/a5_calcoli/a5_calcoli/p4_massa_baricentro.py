# A5.P4 - massa del payload pezzo per pezzo e baricentro (stima di primo ordine, TBC)
# Telescopio RC + 3 lenti (D-088), vetro + carbonio (D-090). Riferimento: Z = 0 sulla faccia a nadir, verso l'interno;
# Y = 0 al centro della faccia 226 x 226, telescopio spostato contro un lato (D-078) -> asse a Y = -43 mm.
import math, json
VETRO, SILICE, CFRP, AL = 2.53, 2.20, 1.60, 2.70      # g/cm3
def disco(D, t, rho, alleggerito=0.0, foro=0.0):
    v = math.pi/4*(D**2 - foro**2)*t/1000            # cm3 (mm in ingresso)
    return v*rho*(1 - alleggerito)/1000               # kg
def guscio(lato, L, parete, rho):                     # tubo quadrato (mm)
    return 4*lato*L*parete*1e-9*rho*1000
yT = -(226.3/2 - 70)                                   # asse del telescopio
zs = 115.0; zp = zs + 169.5; zi = zp + 78.8            # secondario, primario, piano focale (rc_200_70_3.json)
pezzi = [  # nome, voce budget, massa kg, Z mm, Y mm
 ("primario (124 mm, 20 mm, alleggerito 60%, foro 49 mm)", "M-11", disco(124, 20, VETRO, 0.60, 49), zp + 10, yT),
 ("secondario (56 mm, 9 mm, pieno)", "M-11", disco(56, 9, VETRO), zs, yT),
 ("3 lenti in silice (49 mm, 5 mm)", "M-11", 3*disco(49, 5, SILICE), zp + 40, yT),
]
sp = pezzi[0][2] + pezzi[1][2]
pezzi += [
 ("attacchi flessibili degli specchi (Ti/Invar, 70% degli specchi)", "M-11", 0.7*sp, zp - 30, yT),
 ("cella delle lenti", "M-11", 0.08, zp + 40, yT),
 ("tubo in carbonio 140 x 140 mm, 2 mm, dal secondario al piano focale", "M-11", guscio(140, zi - 100, 2, CFRP), (100 + zi)/2, yT),
 ("2 paratie in carbonio alleggerite", "M-11", 2*0.14*0.14*0.005*0.4*CFRP*1000, (zp + zi)/2, yT),
 ("ragno del secondario + paraluci interni (secondario e foro, R-50)", "M-11", 0.06, zs, yT),
 ("piastra del piano focale (Invar/Ti) per i due sensori", "M-11", 0.10, zi + 5, yT),
 ("viti, inserti, regolazioni", "M-11", 0.25, (100 + zi)/2, yT),
 ("paraluce esterno in carbonio 10 cm, 1 mm, con alette", "M-14", guscio(140, 100, 1, CFRP) + 0.03, 50, yT),
 ("coperchio (piastra alleggerita) + cerniera + motorino + finecorsa", "M-14", 0.18, 5, yT),
 ("sensore diurno + elettronica di prossimita' + custodia", "M-12", 0.25, zi + 20, yT),
 ("sensore notturno + elettronica di prossimita' + custodia", "M-13", 0.22, zi + 20, yT),
 ("scheda FPGA + memoria", "M-15", 0.18, 380, +60),
 ("schedina AI", "M-15", 0.12, 380, +60),
 ("scatola/schermo della scheda (Al)", "M-15", 0.15, 380, +60),
 ("memoria di massa (sulla scheda FPGA, D-086)", "M-16", 0.02, 380, +60),
 ("termico payload: MLI ~0,2 m2, riscaldatori e sensori di temperatura", "M-23", 0.09, (100 + zi)/2, yT),
 ("termico payload: radiatore e treccia termica del sensore notturno", "M-23", 0.09, zi + 30, yT - 60),
]
voci = {}
for n, v, m, z, y in pezzi:
    voci.setdefault(v, []).append(m)
    print(f"{v}  {m*1000:6.0f} g  Z {z:5.0f}  Y {y:5.0f}  {n}")
print()
MARG = {"M-11": 0.20, "M-12": 0.20, "M-13": 0.20, "M-14": 0.20, "M-15": 0.20, "M-16": 0.10, "M-23": 0.20}
tot = totm = 0
for v in sorted(voci):
    m = sum(voci[v]); tot += m; totm += m*(1 + MARG[v])
    print(f"{v}: {m:.2f} kg nominale, {m*(1+MARG[v]):.2f} kg con margine voce {MARG[v]:.0%}")
print(f"payload: {tot:.2f} kg nominale, {totm:.2f} kg con margini voce, {totm*1.2:.2f} kg con margine di sistema 20%")
M = sum(p[2] for p in pezzi); Z = sum(p[2]*p[3] for p in pezzi)/M; Y = sum(p[2]*p[4] for p in pezzi)/M
print(f"baricentro del payload: Z {Z:.0f} mm dalla faccia a nadir (centro satellite 227), Y {Y:.0f} mm")
for Msat in (30.0, 36.0):
    print(f"effetto sul baricentro del satellite ({Msat:.0f} kg) se il resto fosse centrato: Y {M*Y/Msat:+.1f} mm, Z {M*(Z-227)/Msat:+.1f} mm")
# solo la colonna del telescopio (senza scheda): spostamento laterale da compensare
col = [p for p in pezzi if p[1] != "M-15" and p[1] != "M-16"]
mc = sum(p[2] for p in col); yc = sum(p[2]*p[4] for p in col)/mc
print(f"colonna telescopio {mc:.2f} kg a Y {yc:.0f} mm: momento {mc*yc:.0f} kg*mm -> {mc*yc/30:.1f} mm su 30 kg; "
      f"si annulla con {abs(mc*yc)/80:.2f} kg messi a Y +80 mm")
json.dump(dict(voci={v: sum(m) for v, m in voci.items()}, Z=Z, Y=Y, M=M), open('p4_massa_baricentro.json', 'w'))
