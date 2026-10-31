# PULSE A5.8.3 - Modello termico a nodi del satellite (Giuseppe, D-110), architettura A2 (D-116), casi D-115.
# Nodi: interno (struttura + elettronica + motore), batteria, radiatore della piattaforma (-Y), 5 coperte MLI esterne
# (+X, -X, +Y, +Z, -Z), ali solari. Telescopio regolato a 20 C dai suoi riscaldatori (D-100): scambia con l'interno.
# Geometria del Sole e dell'ombra con le funzioni di Giuliano (PULSE_EPS/A5.6/luce_eclisse.py), assi S2 (D-114):
# +X velocita', +Y normale all'orbita lato Sole, +Z zenit (asse lungo), telescopio verso -Z.
# Uso: python a5_8_3_modello_nodi.py <cartella PULSE_EPS/A5.6> [area radiatore cm2]
import sys, os, numpy as np
sys.path.insert(0, sys.argv[1])
from luce_eclisse import sole, una_orbita, illuminazione, PERIODO
sig, Re, h = 5.670e-8, 6378.0, 302.0
A_RAD = (float(sys.argv[2]) if len(sys.argv) > 2 else 600.0) * 1e-4

# ---------- fattore di vista piastra -> Terra in funzione dell'angolo tra normale e nadir ----------
def _vf(incl_deg, n=60000, seed=1):
    rng = np.random.default_rng(seed); u = rng.random(n); v = rng.random(n)
    th = np.arcsin(np.sqrt(u)); ph = 2*np.pi*v
    d = np.stack([np.sin(th)*np.cos(ph), np.sin(th)*np.sin(ph), np.cos(th)], 1)
    a = np.radians(incl_deg); R = np.array([[np.cos(a), 0, np.sin(a)], [0, 1, 0], [-np.sin(a), 0, np.cos(a)]])
    return np.mean((d @ R.T)[:, 2] > np.cos(np.arcsin(Re/(Re + h))))
_ang = np.arange(0, 181, 2.0); _F = np.array([_vf(a) for a in _ang])
def vf_terra(cos_nadir): return np.interp(np.degrees(np.arccos(np.clip(cos_nadir, -1, 1))), _ang, _F)

# ---------- geometria e proprieta' (TBC) ----------
L, W = 0.454, 0.2263
FACCE = {  # nome: (normale nel corpo, area MLI m2)
    "+X": ([1, 0, 0], W*W), "-X": ([-1, 0, 0], W*W - 0.096**2), "+Y": ([0, 1, 0], W*L),
    "+Z": ([0, 0, 1], W*W), "-Z": ([0, 0, -1], W*W - np.pi*0.075**2)}
MLI_ALFA, MLI_EPS, MLI_EPS_EFF, MLI_C = 0.40, 0.80, 0.04, 40.0   # strato esterno (tipo kapton alluminato/beta cloth), J/K per faccia
RAD_EPS = 0.85; RAD_C = 300.0; G_RAD = float(os.environ.get("G_RAD", 3.0))   # radiatore Al ~0,33 kg, collegamento all'interno W/K
C_INT, C_BATT, G_BATT = 10000.0, 800.0, 0.5                        # J/K, J/K, W/K
ALI_A, ALI_ALFA, ALI_EPS_F, ALI_EPS_R, ALI_C, G_ALI = 6*W*L, 0.90, 0.85, 0.85, 1200.0, 0.1
ETA_ALI = 0.19                                                     # frazione della luce convertita in elettricita' (celle 28% x impaccamento 0,68)
G_TEL, T_TEL = 0.2, 20.0                                           # telescopio regolato (D-100), attacchi isolati
G_PRAD, T_PRAD = 0.034, -30.0                                      # perdite verso i radiatori del payload (D-095/D-107)
T_RISC_INT, T_RISC_BATT, P_RISC_MAX = 15.0, 15.0, 30.0              # termostati (interno 15-25 C, D-116)
Q_MOT = float(os.environ.get("Q_MOT", 15.0))                        # calore del REGULUS nel satellite (D-115, 15 W TBC)
G_ALI = float(os.environ.get("G_ALI", G_ALI))

AMB = {"caldo": dict(S=1414, alb=0.35, IR=261, alfa_rad=0.35),
       "freddo": dict(S=1322, alb=0.18, IR=218, alfa_rad=0.20)}

def geometria(giorno, assetto, G):
    k = int(np.argmin(np.abs(G[:, 0] - giorno))); _, inc, raan, _ = G[k]
    jd = 2461042.0417 + G[k, 0]
    s_dir, s_dist, _ = sole(jd)
    t, u, r, n_hat = una_orbita(jd, raan, inc, passo=10.0)
    luce = illuminazione(r, s_dir, s_dist)
    zz = r / np.linalg.norm(r, axis=1)[:, None]; yy = np.repeat(n_hat[None, :], len(r), 0)
    if (yy @ s_dir).mean() < 0: yy = -yy
    xx = np.cross(yy, zz)
    sx, sy, sz = xx @ s_dir, yy @ s_dir, zz @ s_dir
    if assetto == "safe":                     # +Z (ali) verso il Sole, assetto inerziale anche al buio
        Zb = np.repeat(s_dir[None, :], len(r), 0)
        Xb = np.cross(yy, Zb); Xb /= np.linalg.norm(Xb, axis=1)[:, None]; Yb = np.cross(Zb, Xb); phi = np.nan
    else:                                     # rollio fisso ottimo verso il Sole (D-106)
        phis = np.radians(np.arange(0, 61, 1))
        Lm = luce > 0.5
        phi = phis[int(np.argmax([np.clip(np.cos(p)*sz + np.sin(p)*sy, 0, None)[Lm].mean() for p in phis]))]
        Xb = xx; Zb = np.cos(phi)*zz + np.sin(phi)*yy; Yb = np.cos(phi)*yy - np.sin(phi)*zz
    beta = np.degrees(np.arcsin(np.clip(sy.mean(), -1, 1)))
    return dict(t=t, luce=luce, s=s_dir, zz=zz, Xb=Xb, Yb=Yb, Zb=Zb, beta=beta, phi=np.degrees(phi) if phi == phi else None,
                cos_sub=np.clip(sz, 0, None))

def flussi(g, n_b, amb, alfa, eps):
    """W/m2 assorbiti da una superficie con normale n_b (nel corpo) lungo l'orbita."""
    n = n_b[0]*g["Xb"] + n_b[1]*g["Yb"] + n_b[2]*g["Zb"]
    cs = np.clip(n @ g["s"], 0, None) * g["luce"]
    F = vf_terra(np.einsum('ij,ij->i', n, -g["zz"]))
    return alfa*amb["S"]*cs + eps*amb["IR"]*F + alfa*amb["S"]*amb["alb"]*F*g["cos_sub"]

def profilo(g, caso):
    """Calore interno (W) nel tempo dell'orbita, per orbita k."""
    t = g["t"]; L = g["luce"] > 0.5
    i_luce = np.where(L)[0]; meta = i_luce[len(i_luce)//2]
    def P(k):
        p = np.full(len(t), 12.7)
        if caso in ("caldo", "routine"):
            p += np.where(L, 7.7 + 1.0, 1.1)                        # perdite EPS e batteria (A5.6.7)
            dur = 22 if caso == "caldo" else 17
            sp = np.abs(t - t[meta]) < dur*30
            p[sp] += Q_MOT + 3.0                                    # motore (D-115) + magnetorquer
            if k % 2 == 0: p[(t > t[meta] + dur*30) & (t < t[meta] + dur*30 + 600)] += 13.7 + 4.0   # contatto ~10 min
            if k % 16 == 0: p[L & (t < t[i_luce[0]] + 600)] += 5.0  # una ripresa diurna al giorno
        elif caso == "freddo":                                      # giorno senza spinta (attesa)
            p += np.where(L, 4.5, 0.8)
            if k % 2 == 0: p[L & (t > t[meta]) & (t < t[meta] + 600)] += 13.7 + 4.0
        elif caso == "safe":
            p += 3.0 + np.where(L, 4.5, 0.8)                        # magnetorquer + perdite
        return p
    return P

def simula(giorno, caso, G, giorni=4, dt=10.0):
    amb = AMB["caldo" if caso == "caldo" else "freddo"]
    g = geometria(giorno, "safe" if caso == "safe" else "nominale", G)
    q_mli = {f: flussi(g, np.array(n), amb, MLI_ALFA, MLI_EPS) for f, (n, a) in FACCE.items()}
    q_rad = flussi(g, np.array([0, -1, 0]), amb, amb["alfa_rad"], RAD_EPS)
    alfa_ali = ALI_ALFA - ETA_ALI
    q_ali = flussi(g, np.array([0, 0, 1]), amb, alfa_ali, ALI_EPS_F) + flussi(g, np.array([0, 0, -1]), amb, 0.0, ALI_EPS_R)
    P = profilo(g, caso); n = len(g["t"]); norb = int(giorni*86400/PERIODO)
    Ti, Tb, Tr, Ta = 20.0, 20.0, 10.0, 20.0; Tm = {f: 0.0 for f in FACCE}
    K = lambda T: T + 273.15
    reg = []
    for k in range(norb):
        Pk = P(k)
        for j in range(n):
            q_m = {f: MLI_EPS_EFF*a*sig*(K(Ti)**4 - K(Tm[f])**4) for f, (nb, a) in FACCE.items()}
            q_r = G_RAD*(Ti - Tr); q_b = G_BATT*(Ti - Tb); q_a = G_ALI*(Ti - Ta)
            q_t = G_TEL*(T_TEL - Ti); q_p = G_PRAD*(Ti - T_PRAD)
            r_int = np.clip((T_RISC_INT - Ti)*20, 0, P_RISC_MAX); r_batt = np.clip((T_RISC_BATT - Tb)*20, 0, 6.0)
            dTi = (Pk[j] + r_int + q_t - sum(q_m.values()) - q_r - q_b - q_a - q_p) / C_INT
            dTb = (q_b + r_batt) / C_BATT
            dTr = (q_r + A_RAD*(q_rad[j] - RAD_EPS*sig*K(Tr)**4)) / RAD_C
            dTa = (q_a + ALI_A*(q_ali[j] - (ALI_EPS_F + ALI_EPS_R)*sig*K(Ta)**4)) / ALI_C
            for f, (nb, a) in FACCE.items():
                Tm[f] += dt*(q_m[f] + a*(q_mli[f][j] - MLI_EPS*sig*K(Tm[f])**4)) / MLI_C
            Ti += dt*dTi; Tb += dt*dTb; Tr += dt*dTr; Ta += dt*dTa
            if k >= norb - 16:
                reg.append((Ti, Tb, Tr, Ta, r_int, r_batt, Pk[j], *[Tm[f] for f in FACCE],
                            q_r, sum(q_m.values()), q_a, q_t, q_p, q_b))
    R = np.array(reg)
    return g, R

if __name__ == "__main__":
    G = np.loadtxt(os.path.join(sys.argv[1], "risultati/gmat_ltdn_inclinazione.csv"), delimiter=",")
    # giorni scelti: caldo = gennaio con beta massimo; freddo = maggio-giugno con eclisse piu' lunga (D-102)
    gennaio = [d for d in G[:, 0] if (d % 365.25) < 31]
    CASI = [("caldo", "caldo (gennaio, 22 min di spinta per orbita)", None),
            ("routine", "routine d'estate (17 min di spinta, ambiente freddo)", 160),
            ("freddo", "freddo operativo (giorno senza spinta)", 160),
            ("safe", "freddo safe (ali verso il Sole)", 160)]
    print(f"Radiatore della piattaforma sulla -Y: {A_RAD*1e4:.0f} cm2; calore del motore {Q_MOT:.1f} W; attacchi delle ali {G_ALI} W/K\n")
    for caso, nome, giorno in CASI:
        if giorno is None:
            betas = []
            for d in gennaio[::5]:
                gg = geometria(d, "nominale", G); betas.append((gg["beta"], d))
            giorno = max(betas)[1]
        g, R = simula(giorno, caso, G)
        dtt = 10.0/3600
        print(f"{nome}: giorno {giorno:.0f}, beta {g['beta']:.1f} gradi, rollio {g['phi'] if g['phi'] is not None else 'safe'}")
        print(f"  interno {R[:,0].min():.1f}..{R[:,0].max():.1f} C (media {R[:,0].mean():.1f}); batteria {R[:,1].min():.1f}..{R[:,1].max():.1f} C; "
              f"radiatore {R[:,2].min():.1f}..{R[:,2].max():.1f} C; ali {R[:,3].min():.0f}..{R[:,3].max():.0f} C")
        print(f"  calore interno medio {R[:,6].mean():.1f} W; riscaldatori: interno {R[:,4].mean():.1f} W medi ({R[:,4].sum()*dtt:.0f} Wh/giorno), "
              f"batteria {R[:,5].mean():.2f} W medi; picco {(R[:,4] + R[:,5]).max():.1f} W")
        nf = 7 + len(FACCE)
        print(f"  dove va il calore (W medi): radiatore {R[:,nf].mean():.1f}, coperte MLI {R[:,nf+1].mean():.1f}, ali {R[:,nf+2].mean():.1f}, "
              f"telescopio {-R[:,nf+3].mean():.1f}, radiatori payload {R[:,nf+4].mean():.1f}")
        print("  coperte MLI esterne: " + ", ".join(f"{f} {R[:,7+i].min():.0f}..{R[:,7+i].max():.0f} C" for i, f in enumerate(FACCE)))
