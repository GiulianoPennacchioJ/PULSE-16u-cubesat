# PULSE A5.8.5 - Casi particolari del termico (Giuseppe, D-110): ali solari, detumbling con ali chiuse,
# star tracker, telescopio. Usa il modello a nodi di A5.8.3 (stessa cartella).
# Uso: python a5_8_5_casi_particolari.py <cartella PULSE_EPS/A5.6>
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a5_8_3_modello_nodi as M
G = np.loadtxt(os.path.join(sys.argv[1], "risultati/gmat_ltdn_inclinazione.csv"), delimiter=",")
sig = M.sig

# ---------- 1) ali: temperatura minima al buio e massima in luce ----------
print("1) Ali solari (6 x 226 x 454 mm), radiatore 600 cm2")
for nome, eps_r, alfa, eta in (("retro verniciato (eps 0,85), celle che producono", 0.85, 0.90, 0.19),
                               ("retro verniciato, celle che NON producono (batteria piena)", 0.85, 0.90, 0.0),
                               ("retro in alluminio lucido (eps 0,3), celle che producono", 0.30, 0.90, 0.19),
                               ("retro in alluminio lucido, celle che NON producono", 0.30, 0.90, 0.0)):
    M.ALI_EPS_R, M.ALI_ALFA, M.ETA_ALI = eps_r, alfa, eta
    out = []
    for caso, giorno in (("caldo", 395), ("freddo", 160)):
        g, R = M.simula(giorno, caso, G, giorni=2)
        out.append((R[:, 3].min(), R[:, 3].max()))
    print(f"   {nome}: caldo {out[0][0]:.0f}..{out[0][1]:.0f} C, freddo {out[1][0]:.0f}..{out[1][1]:.0f} C")
M.ALI_EPS_R, M.ALI_ALFA, M.ETA_ALI = 0.85, 0.90, 0.19
dP = 0.0071/2.4*100   # dVmp/dT -7,1 mV/C (Azur 3G30-Adv., D-108) su Vmp ~2,4 V: ~-0,3 %/K (stima, corrente trascurata)
print(f"   potenza delle celle: ~-{dP:.2f} %/K (stima) -> a ~54 C invece di 70 C circa +{dP*16:.0f}% di potenza rispetto a D-108")

# ---------- 2) detumbling con ali chiuse (<= ~4,8 h, D-109), niente riscaldatori ----------
print("\n2) Detumbling con ali chiuse, rotazione casuale, ambiente freddo, senza riscaldatori (batteria non si ricarica)")
ang = np.radians(M._ang); w = np.sin(ang); F_media = np.sum(M._F*w)/np.sum(w)     # vista media della Terra, orientamento casuale
amb = M.AMB["freddo"]; luce = 0.6
def q_abs(alfa, eps): return alfa*amb["S"]*0.25*luce + eps*amb["IR"]*F_media + alfa*amb["S"]*amb["alb"]*F_media*0.5*luce
A_rad = 0.06; Q_int = 10.7 + 0.8 + 3.0*0                       # Giuliano A5.6.8 (detumbling) + perdite batteria
for T0 in (20.0, 10.0):
    Ti, Tr, dt, t = T0, T0 - 3, 10.0, 0.0
    Tmin = Ti
    while t < 4.8*3600:
        q_r = M.G_RAD*(Ti - Tr)
        q_mli = M.MLI_EPS_EFF*0.26*sig*((Ti + 273.15)**4 - (-60 + 273.15)**4)
        q_p = M.G_PRAD*(Ti - M.T_PRAD) + M.G_TEL*(Ti - 0.0)    # telescopio non regolato in detumbling: verso ~0 C
        Ti += dt*(Q_int - q_r - q_mli - q_p)/(M.C_INT + M.C_BATT)
        Tr += dt*(q_r + A_rad*(q_abs(0.20, 0.85) - 0.85*sig*(Tr + 273.15)**4))/M.RAD_C
        t += dt; Tmin = min(Tmin, Ti)
    print(f"   partenza da {T0:.0f} C: dopo 4,8 h interno e batteria a ~{Ti:.1f} C (radiatore {Tr:.0f} C)")

# ---------- 3) star tracker (2 teste ST-16RT2 che sporgono con paraluce, limite +50 C in funzione) ----------
print("\n3) Star tracker: testa montata sul telaio, paraluce esterno (stima a un nodo, caso caldo)")
A_par, A_proj = 0.035, 0.012          # area esterna del paraluce 99 x 120 mm, area proiettata verso il Sole (stima)
amb = M.AMB["caldo"]
for nome, alfa, eps, Gm in (("paraluce nero (alfa 0,9), attacco 0,3 W/K", 0.90, 0.85, 0.3),
                            ("paraluce bianco fuori (alfa 0,35), attacco 0,3 W/K", 0.35, 0.85, 0.3),
                            ("paraluce bianco fuori, attacco 1 W/K", 0.35, 0.85, 1.0)):
    Tint = 23.6; Q_el = 0.5
    Qs = alfa*amb["S"]*A_proj + eps*amb["IR"]*A_par*0.3
    T = 20.0
    for _ in range(2000):                                     # equilibrio con il Sole sul paraluce (caso peggiore)
        T += 0.05*(Qs + Q_el + Gm*(Tint - T) - eps*sig*A_par*(T + 273.15)**4)
    print(f"   {nome}: con il Sole sul fianco del paraluce ~{T:.0f} C (limite +50 C)")

# ---------- 4) telescopio con interno 15-25 C ----------
print("\n4) Telescopio regolato a 20 C (D-100) con l'interno di D-122 (14,3..25,7 C)")
for Ti in (14.3, 25.7):
    q = M.G_TEL*(20 - Ti)
    print(f"   interno {Ti:.1f} C: il telescopio {'perde' if q > 0 else 'riceve'} {abs(q):.1f} W attraverso gli attacchi (0,2 W/K); "
          f"le sue perdite verso lo spazio sono ~2 W medi (D-100): i riscaldatori {'aggiungono' if q > 0 else 'tolgono'} {abs(q):.1f} W "
          f"e restano accesi, la regolazione a 20 C regge")
