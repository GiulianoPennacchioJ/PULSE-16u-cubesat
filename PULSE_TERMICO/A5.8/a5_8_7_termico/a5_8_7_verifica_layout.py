# PULSE A5.8.7 - Verifica del termico con il layout di Giuliano (D-125 disposizione L1b, D-126 ali W1).
# Tre controlli chiesti da Giuliano:
#   1) radiatore -Y che vede il retro dell'ala -Y aperta (fattore di vista Monte Carlo);
#   2) interno diviso in due nodi: pila delle schede contro la -Y (computer di bordo, radio S, UHF, PCDU: ~4 W/K
#      prima dei contatti, D-125) e "resto" (motore, ruote, giroscopio, batteria, payload), che arriva al radiatore
#      solo attraverso il telaio;
#   3) ali chiuse sulle facce +-Y che coprono il radiatore dal rilascio all'apertura (da ~30 min a ~4,8 h).
# Usa il modello a nodi di A5.8.3 (stessa cartella). Valori TBC segnati nel testo.
# Uso: python a5_8_7_verifica_layout.py <cartella PULSE_EPS/A5.6>
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a5_8_3_modello_nodi as M
G = np.loadtxt(os.path.join(sys.argv[1], "risultati/gmat_ltdn_inclinazione.csv"), delimiter=",")
sig, K = M.sig, (lambda T: T + 273.15)
W = 226.3

# ---------------- 1) fattore di vista radiatore -> retro dell'ala -Y aperta (D-126) ----------------
def vf_ala(z0, z1, n=400000, seed=3):
    """Radiatore a tutta larghezza sulla -Y tra z0 e z1 (mm); ala -Y nel piano z = +230, da y = -118 a -1490 mm."""
    rng = np.random.default_rng(seed)
    x = rng.uniform(-W/2, W/2, n); z = rng.uniform(z0, z1, n)
    th = np.arcsin(np.sqrt(rng.random(n))); ph = 2*np.pi*rng.random(n)
    d = np.stack([np.sin(th)*np.cos(ph), -np.cos(th), np.sin(th)*np.sin(ph)], 1)
    su = d[:, 2] > 0; t = np.where(su, (230 - z)/np.where(su, d[:, 2], 1), np.inf)
    xh, yh = x + t*d[:, 0], -W/2 + t*d[:, 1]
    return np.mean(su & (np.abs(xh) < W/2) & (yh < -118) & (yh > -118 - 3*454 - 10))

h600 = 60000/W
FV = {"in alto (contro le cerniere)": vf_ala(232 - h600, 232), "al centro": vf_ala(-h600/2, h600/2),
      "in basso (dietro la pila)": vf_ala(-232, -232 + h600)}
F_ALA = max(FV.values())       # caso prudente: radiatore in alto

# ---------------- 2) modello con interno a due nodi ----------------
C_PILA = 1000.0                # J/K: ~0,66 kg di schede + squadrette (stima)
G_PR = float(os.environ.get("G_PR", 1.0))   # pila <-> resto: telaio + irraggiamento interno (TBC)
QUOTA_MPPT = 6.3/8.7           # parte delle perdite in luce che sta nella PCDU (MPPT 6,3 W su 8,7, A5.6.8)

def profilo2(g, caso, q_mot):
    """Calore (W) nella pila e nel resto, orbita k. Somma uguale a M.profilo (A5.8.3)."""
    t = g["t"]; L = g["luce"] > 0.5
    i_luce = np.where(L)[0]; meta = i_luce[len(i_luce)//2]
    def P(k):
        pp = np.full(len(t), 0.4 + 0.6 + 0.48)          # computer di bordo, EPS a vuoto, UHF in ricezione
        pr = np.full(len(t), 12.7 - 1.48)               # ruote, star tracker, giroscopio, sensori, GNSS
        if caso in ("caldo", "routine"):
            pp += np.where(L, 6.3, 0.0); pr += np.where(L, 1.4 + 1.0, 1.1)   # MPPT nella PCDU; cavi e batteria nel resto
            dur = 22 if caso == "caldo" else 17
            pr[np.abs(t - t[meta]) < dur*30] += q_mot + 3.0
            if k % 2 == 0: pp[(t > t[meta] + dur*30) & (t < t[meta] + dur*30 + 600)] += 13.7 + 4.0
            if k % 16 == 0: pr[L & (t < t[i_luce[0]] + 600)] += 5.0
        else:
            pp += np.where(L, 4.5*QUOTA_MPPT, 0.0); pr += np.where(L, 4.5*(1 - QUOTA_MPPT), 0.8)
            if caso == "safe": pr += 3.0
            if caso == "freddo" and k % 2 == 0: pp[L & (t > t[meta]) & (t < t[meta] + 600)] += 13.7 + 4.0
        return pp, pr
    return P

def simula2(giorno, caso, g_pila, g_resto, f_ala, q_mot=None, giorni=4, dt=10.0):
    q_mot = M.Q_MOT if q_mot is None else q_mot
    amb = M.AMB["caldo" if caso == "caldo" else "freddo"]
    g = M.geometria(giorno, "safe" if caso == "safe" else "nominale", G)
    q_mli = {f: M.flussi(g, np.array(n), amb, M.MLI_ALFA, M.MLI_EPS) for f, (n, a) in M.FACCE.items()}
    q_rad = M.flussi(g, np.array([0, -1, 0]), amb, amb["alfa_rad"], M.RAD_EPS)
    q_ali = (M.flussi(g, np.array([0, 0, 1]), amb, M.ALI_ALFA - M.ETA_ALI, M.ALI_EPS_F)
             + M.flussi(g, np.array([0, 0, -1]), amb, 0.0, M.ALI_EPS_R))
    k_ra = M.A_RAD*f_ala*M.RAD_EPS*M.ALI_EPS_R*sig      # scambio radiatore <-> retro dell'ala -Y
    P = profilo2(g, caso, q_mot); n = len(g["t"]); norb = int(giorni*86400/M.PERIODO)
    Tp, Ti, Tb, Tr, Ta = 20.0, 20.0, 20.0, 10.0, 20.0; Tm = {f: 0.0 for f in M.FACCE}
    reg = []
    for k in range(norb):
        Pp, Pr = P(k)
        for j in range(n):
            q_m = {f: M.MLI_EPS_EFF*a*sig*(K(Ti)**4 - K(Tm[f])**4) for f, (nb, a) in M.FACCE.items()}
            q_pr = g_pila*(Tp - Tr); q_ir = g_resto*(Ti - Tr); q_pi = G_PR*(Tp - Ti)
            q_b = M.G_BATT*(Ti - Tb); q_a = M.G_ALI*(Ti - Ta)
            q_t = M.G_TEL*(M.T_TEL - Ti); q_p = M.G_PRAD*(Ti - M.T_PRAD)
            q_ra = k_ra*(K(Tr)**4 - K(Ta)**4)
            r_int = np.clip((M.T_RISC_INT - Ti)*20, 0, M.P_RISC_MAX); r_batt = np.clip((M.T_RISC_BATT - Tb)*20, 0, 6.0)
            Tp += dt*(Pp[j] - q_pr - q_pi)/C_PILA
            Ti += dt*(Pr[j] + r_int + q_t + q_pi - sum(q_m.values()) - q_ir - q_b - q_a - q_p)/(M.C_INT - C_PILA)
            Tb += dt*(q_b + r_batt)/M.C_BATT
            Tr += dt*(q_pr + q_ir - q_ra + M.A_RAD*(q_rad[j] - M.RAD_EPS*sig*K(Tr)**4))/M.RAD_C
            Ta += dt*(q_a + q_ra + M.ALI_A*(q_ali[j] - (M.ALI_EPS_F + M.ALI_EPS_R)*sig*K(Ta)**4))/M.ALI_C
            for f, (nb, a) in M.FACCE.items():
                Tm[f] += dt*(q_m[f] + a*(q_mli[f][j] - M.MLI_EPS*sig*K(Tm[f])**4))/M.MLI_C
            if k >= norb - 16:
                reg.append((Tp, Ti, Tb, Tr, Ta, r_int, r_batt, q_ra))
    return np.array(reg)

GIORNO = {"caldo": 395, "routine": 160, "freddo": 160, "safe": 160}
NOME = {"caldo": "caldo (gennaio, 22 min di spinta)", "routine": "routine d'estate (17 min)",
        "freddo": "giorno senza spinta", "safe": "safe (ali al Sole)"}
def riga(caso, gp, gr, fa, q_mot=None):
    R = simula2(GIORNO[caso], caso, gp, gr, fa, q_mot)
    dtt = 10.0/3600
    return (f"pila {R[:,0].min():5.1f}..{R[:,0].max():5.1f} C | resto {R[:,1].min():5.1f}..{R[:,1].max():5.1f} C | "
            f"batteria {R[:,2].min():5.1f}..{R[:,2].max():5.1f} C | riscaldatori {R[:,5].mean() + R[:,6].mean():4.1f} W medi "
            f"({(R[:,5] + R[:,6]).sum()*dtt:4.0f} Wh/g)"), R

# ---------------- 3) ali chiuse: radiatore coperto, rotazione casuale ----------------
def ali_chiuse(amb_nome, T0, ore=4.8, Q_int=10.7 + 0.8, dt=5.0):
    """Interno a un nodo (come A5.8.5); radiatore -Y sotto la pila di 3 ali (strati a ~7 mm), orientamento casuale."""
    amb = M.AMB[amb_nome]; luce = 0.6
    ang = np.radians(M._ang); w = np.sin(ang); F_m = np.sum(M._F*w)/np.sum(w)
    q_out = 0.90*amb["S"]*0.25*luce + 0.85*amb["IR"]*F_m + 0.90*amb["S"]*amb["alb"]*F_m*0.5*luce   # celle verso fuori
    A_ala, C_ala = W*454e-6, 200.0
    e2 = 1/(1/0.85 + 1/0.85 - 1)                     # due superfici affacciate a 7 mm (eps 0,85)
    Ti, Tr = T0, T0 - 3; Ts = [T0 - 10]*3            # ala 1 (verso il corpo), 2, 3 (verso fuori)
    out = {}; t = 0.0
    while t <= ore*3600:
        q_r = M.G_RAD*(Ti - Tr)
        q_mli = M.MLI_EPS_EFF*0.26*sig*(K(Ti)**4 - K(-60)**4)
        q_p = M.G_PRAD*(Ti - Ti) + M.G_TEL*(Ti - 0.0)     # radiatori payload coperti anche loro: niente perdita
        q_r1 = M.A_RAD*e2*sig*(K(Tr)**4 - K(Ts[0])**4)
        q_12 = A_ala*e2*sig*(K(Ts[0])**4 - K(Ts[1])**4); q_23 = A_ala*e2*sig*(K(Ts[1])**4 - K(Ts[2])**4)
        Ti += dt*(Q_int - q_r - q_mli - q_p)/(M.C_INT + M.C_BATT)
        Tr += dt*(q_r - q_r1)/M.RAD_C
        Ts[0] += dt*(q_r1 - q_12)/C_ala; Ts[1] += dt*(q_12 - q_23)/C_ala
        Ts[2] += dt*(q_23 + A_ala*(q_out - 0.85*sig*K(Ts[2])**4))/C_ala
        for h in (0.5, 1, 2, 3, 4.8):
            if abs(t - h*3600) < dt/2: out[h] = (Ti, Tr, Ts[2], q_r)
        t += dt
    return out

if __name__ == "__main__":
    o = []; p = o.append
    p("PULSE A5.8.7 - Verifica del termico con il layout L1b (D-125) e le ali W1 (D-126)")
    p(f"Radiatore {M.A_RAD*1e4:.0f} cm2 sulla -Y (fascia a tutta larghezza alta {h600:.0f} mm), motore {M.Q_MOT:.0f} W (TBC)\n")
    p("1) Fattore di vista radiatore -> retro dell'ala -Y aperta (piano della faccia +Z, cerniera in alto):")
    for nome, f in FV.items(): p(f"   radiatore {nome}: F = {f:.2f}")
    p(f"   nel modello si usa il caso prudente F = {F_ALA:.2f}\n")

    p("2) Interno a due nodi (pila contro la -Y; resto collegato al radiatore solo dal telaio); pila <-> resto "
      f"{G_PR} W/K (TBC)")
    p("   a) controllo: con F = 0 e tutto il calore collegato forte, il modello torna ai valori di A5.8.4")
    for gp, gr in ((4.0, 3.0), (2.0, 3.0), (4.0, 2.0), (4.0, 1.0), (2.0, 1.0)):
        for fa in (0.0, F_ALA):
            p(f"   pila {gp:.0f} W/K, resto {gr:.0f} W/K, ala F={fa:.2f}")
            for caso in ("caldo", "routine", "freddo", "safe"):
                s, _ = riga(caso, gp, gr, fa); p(f"      {NOME[caso]:34s} {s}")
    p("   b) sensibilita' sul calore del motore (pila 4 W/K, resto 2 W/K, ala F prudente), caso caldo:")
    for qm in (20.0, 48.5):
        s, _ = riga("caldo", 4.0, 2.0, F_ALA, qm); p(f"      motore {qm:4.1f} W: {s}")
    _, R = riga("caldo", 4.0, 2.0, F_ALA)
    p(f"   c) scambio radiatore -> ala nel caso caldo: {R[:,7].mean():+.1f} W medi (negativo = il radiatore riceve)")
    p("   d) quanto collegamento serve al resto (motore, ruote, batteria)? pila 4 W/K, ala F prudente")
    for gpr in (0.5, 1.0, 2.0):
        globals()["G_PR"] = gpr
        for gr in (0.3, 0.5, 1.0):
            s15, _ = riga("caldo", 4.0, gr, F_ALA); s20, R20 = riga("caldo", 4.0, gr, F_ALA, 20.0)
            sf, _ = riga("freddo", 4.0, gr, F_ALA)
            p(f"      pila<->resto {gpr} W/K, resto->radiatore {gr} W/K: caldo {s15.split('|')[1].strip()}; "
              f"motore 20 W {s20.split('|')[1].strip()}; senza spinta {sf.split('|')[0].strip()}, {sf.split('|')[3].strip()}")
    globals()["G_PR"] = 1.0
    p("")

    p("3) Ali chiuse dopo il rilascio (rotazione casuale, radiatore e radiatori payload coperti, 11,5 W interni, "
      "senza riscaldatori)")
    for amb in ("freddo", "caldo"):
        for T0 in (10.0, 20.0, 30.0):
            r = ali_chiuse(amb, T0)
            p(f"   ambiente {amb:6s}, partenza {T0:4.0f} C: " + "; ".join(
                f"{h:g} h {v[0]:.1f} C" for h, v in sorted(r.items())) +
              f"  (a 4,8 h: radiatore {r[4.8][1]:.0f} C, ala esterna {r[4.8][2]:.0f} C, al radiatore {r[4.8][3]:.1f} W)")
    txt = "\n".join(o); print(txt)
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "a5_8_7_risultati.txt"), "w").write(txt + "\n")
