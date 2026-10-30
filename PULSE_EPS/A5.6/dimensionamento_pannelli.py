"""PULSE A5.6.6 - Dimensionamento dei pannelli con una cella reale.

Cella di riferimento: Azur Space 3G30-Advanced (datasheet bdb_00010894-02-00):
  77,55 cm2, BOL 3,08 W (29,0%), a 5E14 e/cm2 Pmp 2,85 W (Vmp 2,247 V, Imp 1,270 A),
  dVmp/dT -7,1 mV/C, dImp/dT +0,62 mA/C (colonna 5E14). CIC 13,1 g.
Pannello: 226 x 454 mm (come una faccia laterale), 9 celle (3 x 3) -> impaccamento 0,68.
Configurazione D-106 (Proposta): ali a zenit + rollio fisso, k caso peggiore 0,575.
Uso: python dimensionamento_pannelli.py
"""
import numpy as np

# --- cella a fine vita, in temperatura
VMP, IMP, PMP_5E14 = 2.247, 1.270, 2.85
T_OP = 70.0                     # C, temperatura di lavoro delle ali (come EarthNext, WCT 70 C) - TBC
dV, dI = -7.1e-3, 0.62e-3
fT = (VMP + dV * (T_OP - 28)) * (IMP + dI * (T_OP - 28)) / (VMP * IMP)
F_ALTRO = 0.98 * 0.97           # UV/contaminazione 2%; disaccoppiamento celle e cavi 3%
P_CELLA = PMP_5E14 * fT * F_ALTRO
N_CELLE = 9
P_PAN = N_CELLE * P_CELLA
A_PAN = 0.226 * 0.454
K = 0.575                        # D-106, caso peggiore nei 2 anni
XE, XD = 0.65, 0.85
LUCE_H = 54.56 / 60
ORB = 1440 / 90.56
E_ECL = 12.2                     # Wh/orbita al buio con margini (attesa, A5.6.3, con D-107)
ATTESA_W = 20.29                 # W con margini (con D-107)
SPINTA_EXTRA_W = (50 * 1.05 + 3 * 1.10) * 1.2    # motore + magnetorquer, margini voce + sistema
ALTRO_GIORNO = (5.2 + 28.9 + 6.9)                # Wh/giorno: riprese routine + contatti + RX S (A5.6.3)

out = []; p = out.append
p("PULSE A5.6.6 - Pannelli con cella Azur 3G30-Advanced")
p("Cella: 5E14 e/cm2 -> %.2f W; a %.0f C fattore %.3f; altre perdite %.3f -> %.2f W per cella" % (PMP_5E14, T_OP, fT, F_ALTRO, P_CELLA))
p("Pannello 226x454 mm con %d celle: %.1f W a incidenza normale (%.0f W/m2 di pannello)" % (N_CELLE, P_PAN, P_PAN / A_PAN))
p("Con k = %.3f: %.1f W medi in luce per pannello" % (K, P_PAN * K))
p("")
for nome, e_giorno in (("Sole medio (routine)", 809.0), ("Sole alto", 1050.0)):
    e_orb = e_giorno / ORB
    psa = (E_ECL / XE + (e_orb - E_ECL) / XD) / LUCE_H
    p("%-22s Psa %.1f W -> pannelli necessari %.2f" % (nome, psa, psa / (P_PAN * K)))
p("")
p("Ore di spinta al giorno sostenibili, per numero di pannelli (bilancio energetico per orbita, con margini):")
for n in (5, 6, 7, 8):
    psa = n * P_PAN * K
    e_luce_max = XD * (psa * LUCE_H - E_ECL / XE)          # Wh/orbita disponibili per i carichi in luce
    libero = e_luce_max - ATTESA_W * LUCE_H - ALTRO_GIORNO / ORB
    ore = max(libero, 0) / SPINTA_EXTRA_W * ORB
    p("  %d pannelli: Psa %.1f W -> spinta sostenibile %.1f h/giorno (servono 4,2 Sole medio, 7,8 Sole alto)" % (n, psa, ore))
p("")
p("Massa delle celle (CIC 13,1 g): %.0f g per pannello; substrato, cerniere e cavi da A5.7 (TBD)" % (13.1 * N_CELLE))
txt = "\n".join(out); print(txt)
open("risultati/dimensionamento_pannelli.txt", "w").write(txt + "\n")
