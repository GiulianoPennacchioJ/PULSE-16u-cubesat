# PULSE A5.8.2 - Confronto di primo ordine delle architetture termiche (Giuseppe, D-110, casi D-115)
# Modello a UN nodo (interno del satellite) mediato sull'orbita: serve solo a confrontare le opzioni.
# Il modello vero, a nodi e minuto per minuto, e' A5.8.3. Uso: python a5_8_2_architettura.py
import numpy as np
sig = 5.670e-8
# --- calore interno medio sull'orbita (W), da A5.8.1 (dati di Giuliano A5.6.8 + payload, motore 15 W TBC) ---
base, perdite_caldo, perdite_freddo = 12.7, 5.7, 3.1      # perdite EPS+batteria medie sull'orbita (luce 60%)
spinta = (15.0 + 3.0) * 22 / 90.6                          # motore + magnetorquer, 22 min per orbita (D-115)
contatto = 13.7 * 10 / 90.6 + 4.0 * 20 / 90.6              # un contatto di ~10 min nell'orbita + ricevitore S
ripresa = 5.0 * 8 / 90.6                                   # sensore diurno ~8 min
Q = {"caldo": base + perdite_caldo + spinta + contatto + ripresa,
     "freddo operativo": base + perdite_freddo + 0.9,     # giorno senza spinta; contatti mediati sul giorno
     "freddo safe": 15.7 + perdite_freddo,
     "routine d'estate": base + perdite_caldo + (15.0 + 3.0) * 17 / 90.6 + 0.9}   # Sole medio, 17 min/orbita, ambiente freddo
# --- ambiente medio assorbito (W/m2) su un radiatore sulla faccia -Y con il rollio di D-106 (p7_radiatori_rollio.py) ---
def assorbito(alfa, S, IR, alb, cmean, F, eps=0.85, luce=0.6):
    return alfa*S*cmean + eps*IR*F + alfa*S*alb*F*0.5*luce
qa = {"caldo": assorbito(0.35, 1414, 261, 0.35, 0.078, 0.10), "freddo": assorbito(0.20, 1322, 218, 0.18, 0.044, 0.02)}
# --- perdite dalle coperte MLI (~0,26 m2 di corpo coperto, emissivita' efficace 0,04, TBC) ---
def mli(Tint, Tsink): return 0.04 * 0.26 * sig * ((Tint+273.15)**4 - (Tsink+273.15)**4)
A_meno_Y = 0.2263*0.454 - 0.019                            # faccia -Y meno i radiatori del payload (D-095, ~190 cm2)
print("Calore interno medio sull'orbita: " + ", ".join(f"{k} {v:.1f} W" for k, v in Q.items()))
print(f"Ambiente assorbito sul radiatore (-Y, con rollio): caldo {qa['caldo']:.0f} W/m2, freddo {qa['freddo']:.0f} W/m2")
print(f"Area libera sulla faccia -Y dopo i radiatori del payload: {A_meno_Y*1e4:.0f} cm2\n")

def opzione_fissa(nome, Tmax, Tmin, eps=0.85, dT=3.0):
    q_c = eps*sig*(Tmax - dT + 273.15)**4 - qa["caldo"]              # radiatore ~3 K sotto l'interno (TBC)
    A = (Q["caldo"] - mli(Tmax, 0)) / q_c
    out = []
    for caso in ("freddo operativo", "freddo safe", "routine d'estate"):
        q_f = eps*sig*(Tmin - 1 + 273.15)**4 - qa["freddo"]
        risc = max(A*q_f + mli(Tmin, -40) - Q[caso], 0)
        out.append(risc)
    print(f"{nome}: radiatore {A*1e4:.0f} cm2 (+20% di calore {1.2*A*1e4:.0f} cm2); riscaldatori medi: "
          f"freddo operativo {out[0]:.1f} W, safe {out[1]:.1f} W, giorno di routine d'estate {out[2]:.1f} W ({out[2]*24:.0f} Wh/giorno)")
    return A, out

print("A) Scatola isolata (MLI) + radiatore fisso (vernice bianca) + riscaldatori con termostato")
A_A, r_A = opzione_fissa("   interno 15-20 C", 20, 15)
opzione_fissa("   variante interno 15-25 C", 25, 15)

print("\nB) Come A, ma con radiatore a persiane (louver): si chiude da solo quando fa freddo, senza energia")
eps_ap, eps_ch = 0.70, 0.14                                  # efficace aperto / chiuso (tipico, TBC)
q_c = eps_ap*sig*(17 + 273.15)**4 - qa["caldo"]*eps_ap/0.85
A_B = (Q["caldo"] - mli(20, 0)) / q_c
smalt_ch = A_B*(eps_ch*sig*(14 + 273.15)**4 - qa["freddo"]*eps_ch/0.85) + mli(15, -40)
print(f"   radiatore {A_B*1e4:.0f} cm2; a persiane chiuse smaltisce {smalt_ch:.1f} W contro {Q['freddo operativo']:.1f} W prodotti "
      f"-> riscaldatori ~{max(smalt_ch - Q['freddo operativo'], 0):.0f} W")

print("\nC) Pareti che irradiano direttamente (niente MLI, vernici scelte per la media)")
# scatola 226 x 226 x 454 mm: area totale, area proiettata media verso il Sole (~1/4 della totale), vista della Terra pesata
A_tot = 2*0.2263**2 + 4*0.2263*0.454
A_proj = A_tot / 4
AF_terra = 0.2263**2*0.88 + 4*0.2263*0.454*0.31
def T_box(Qi, alfa, S, IR, alb, eps=0.85):
    Qa = alfa*S*A_proj*0.6 + eps*IR*AF_terra + alfa*S*alb*AF_terra*0.3
    return ((Qi + Qa)/(eps*sig*A_tot))**0.25 - 273.15
Tc, Tf = T_box(Q["caldo"], 0.35, 1414, 261, 0.35), T_box(Q["freddo operativo"], 0.20, 1322, 218, 0.18)
r = (Tc + 273.15)/(Tf + 273.15)                              # rapporto fisso: le vernici spostano la media, non l'escursione
Tm = 17 + 273.15
print(f"   con vernice bianca: caldo {Tc:.0f} C, freddo {Tf:.0f} C")
print(f"   con vernici scelte per avere la media a 17 C: caldo {Tm*r**0.5 - 273.15:.0f} C, freddo {Tm/r**0.5 - 273.15:.0f} C "
      f"-> escursione ~{Tm*(r**0.5 - 1/r**0.5):.0f} K contro i 5 K di DR-64")
