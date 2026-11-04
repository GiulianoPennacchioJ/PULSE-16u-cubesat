# PULSE A5.8.8 - Risposte a Giuliano su D-129 (radiatore di piattaforma in basso sulla -Y) e radiatori del payload
# con le ali W1 aperte (D-126):
#   1) radiatore di piattaforma in basso (Z -227..+38 mm): caso di progetto con fattore di vista 0,10;
#   2) MLI del telescopio dietro il radiatore in basso (D-100): quanto calore perde il telescopio;
#   3) radiatore del sensore notturno in alto (Z +166 mm, CSV del payload) sotto il retro dell'ala -Y aperta;
#   4) scheda payload (D-091, ora sul lato +Y): se scarica nell'interno senza radiatore proprio.
# Usa a5_8_7_verifica_layout.py e a5_8_3_modello_nodi.py (stessa cartella). Valori TBC segnati nel testo.
# Uso: python a5_8_8_radiatori_payload.py <cartella PULSE_EPS/A5.6>
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a5_8_7_verifica_layout as V
M = V.M; sig = M.sig; W = 226.3
o = []; p = o.append
p("PULSE A5.8.8 - Radiatore di piattaforma in basso (D-129) e radiatori del payload sotto l'ala -Y aperta (D-126)\n")

def vf(x0, x1, z0, z1, n=600000, seed=5):
    """Piastra sulla -Y (x, z in mm) -> retro dell'ala -Y aperta (piano z = +230, y da -118 a -1490 mm)."""
    rng = np.random.default_rng(seed)
    x = rng.uniform(x0, x1, n); z = rng.uniform(z0, z1, n)
    th = np.arcsin(np.sqrt(rng.random(n))); ph = 2*np.pi*rng.random(n)
    d = np.stack([np.sin(th)*np.cos(ph), -np.cos(th), np.sin(th)*np.sin(ph)], 1)
    su = d[:, 2] > 0; t = np.where(su, (230 - z)/np.where(su, d[:, 2], 1), np.inf)
    xh, yh = x + t*d[:, 0], -W/2 + t*d[:, 1]
    return np.mean(su & (np.abs(xh) < W/2) & (yh < -118) & (yh > -118 - 3*454 - 10))

# ---------- 1) radiatore di piattaforma in basso ----------
F_basso = vf(-W/2, W/2, -227, 38)
p(f"1) Radiatore di piattaforma in basso (Z -227..+38 mm): fattore di vista verso l'ala {F_basso:.2f} (prudente in A5.8.7: 0,22)")
p("   Punto di progetto (pila 4, pila<->resto 1, resto->parete 1 W/K, motore 15 W):")
RAD = {}
for caso in ("caldo", "routine", "freddo", "safe"):
    s, R = V.riga(caso, 4.0, 1.0, F_basso); RAD[caso] = R[:, 3]
    p(f"      {V.NOME[caso]:34s} {s}")
s, _ = V.riga("caldo", 4.0, 1.0, F_basso, 20.0); p(f"      {'caldo con motore 20 W':34s} {s}")

# ---------- 2) MLI del telescopio dietro il radiatore in basso ----------
A_tel = 0.140*0.265            # parte della colonna (140 mm) affacciata al radiatore (265 mm di altezza)
p(f"\n2) Telescopio (20 C, D-100) dietro il radiatore in basso: superficie affacciata {A_tel*1e4:.0f} cm2")
for caso, Tr in RAD.items():
    q = [e*A_tel*sig*(293.15**4 - (Tr + 273.15)**4) for e in (0.03, 0.05)]
    p(f"   {V.NOME[caso]:34s} radiatore {Tr.min():5.1f}..{Tr.max():5.1f} C -> il telescopio perde {q[0].mean():.2f} W "
      f"(MLI eps* 0,03) / {q[1].mean():.2f} W (0,05) medi")
p("   confronto: riscaldatori del telescopio ~2 W medi (D-100). Serve un distacco tra MLI e pannello (niente contatto)")

# ---------- 3) radiatore del sensore notturno sotto l'ala ----------
F_sens = vf(-7, 93, 116, 216)  # 100 x 100 mm attorno a X +43, Z +166 (CSV del payload: Z 393 mm dalla faccia a nadir)
p(f"\n3) Radiatore del sensore notturno in alto (X -7..+93, Z +116..+216 mm): fattore di vista verso l'ala {F_sens:.2f}")
for caso in ("caldo", "routine"):
    g = M.geometria(V.GIORNO[caso], "nominale", V.G)
    R = V.simula2(V.GIORNO[caso], caso, 4.0, 1.0, F_basso, giorni=3)
    n = len(g["t"]); Ta = R[-n:, 4]; buio = g["luce"][:n] < 0.5; Tw = Ta[buio].mean()
    amb = M.AMB["caldo" if caso == "caldo" else "freddo"]
    q0 = 0.85*sig*263.15**4 - 0.85*amb["IR"]*0.31                       # a -10 C, a nadir, senza ala
    q1 = q0 - F_sens*0.85*0.85*sig*(Tw + 273.15)**4                      # con il retro dell'ala davanti
    p(f"   {V.NOME[caso]}: ala al buio {Tw:.0f} C medi (in luce fino a {Ta.max():.0f} C)")
    p(f"      a -10 C smaltisce {q0:.0f} W/m2 senza ala, {q1:.0f} W/m2 con l'ala -> 100 cm2 {q1*0.01:.2f} W; "
      f"area per 1,1 W {1.1/q1*1e4:.0f} cm2, per 1,65 W (x1,5) {1.65/q1*1e4:.0f} cm2")

# ---------- 4) scheda payload senza radiatore proprio ----------
# P-15: ripresa FPGA 5 + AI 2 W per ~10 min a passaggio; scarico 3,5 W per ~71 min/giorno (D-092); spenta altrimenti.
E = 4*10/60*7.0 + 71/60*3.5
p(f"\n4) Scheda payload (ora sul lato +Y): energia ~{E:.1f} Wh/giorno (4 riprese da 10 min a 7 W + scarico 3,5 W) "
  f"= {E/24:.2f} W medi (TBC: numero di riprese al giorno)")
p(f"   picco 7 W per 10 min nella massa della scheda (~405 J/K, p7): +{7*600/405:.0f} K al massimo per ripresa")
orig = V.profilo2
for extra in (0.5, 1.0):
    V.profilo2 = (lambda ex: (lambda g, caso, q: (lambda P: (lambda k: (P(k)[0], P(k)[1] + ex)))(orig(g, caso, q))))(extra)
    a, _ = V.riga("caldo", 4.0, 1.0, F_basso); b, _ = V.riga("caldo", 4.0, 1.0, F_basso, 20.0)
    p(f"   scheda +{extra:.1f} W medi nell'interno: caldo {a.split('|')[1].strip()}; con motore 20 W {b.split('|')[1].strip()}")
V.profilo2 = orig
p("   nei casi freddi la scheda puo' essere spenta: riscaldatori invariati (P-24 1,1 / 5,9 W resta prudente)")

txt = "\n".join(o); print(txt)
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "a5_8_8_risultati.txt"), "w").write(txt + "\n")
