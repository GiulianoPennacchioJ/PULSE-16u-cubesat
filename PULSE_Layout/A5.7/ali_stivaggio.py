"""PULSE A5.7.5 - Stivaggio e apertura delle ali: baricentro, linea di spinta e inerzie (primo ordine, TBC).

Parte dal layout L1b (D-125, layout_bozza.py) e cambia solo le ali (D-106: aperte con la faccia attiva verso lo
zenit, nel piano che contiene la velocita'; D-108/D-119: 226 x 454 mm, 0,55 kg l'una). Configurazioni:
  W1: 3 + 3 ali a fisarmonica (pila delle schede in fondo alla fetta -X) sulle facce +Y e -Y, cerniera sullo spigolo alto (+Z): aperte si stendono lungo +-Y
      nel piano della faccia +Z;
  W2: come W1 ma cerniera sullo spigolo basso (-Z, lato nadir): aperte nel piano della faccia a nadir;
  W3: 3 ali sulla +Y e 3 sulla +X (nessuna sulla -Y dei radiatori), cerniera in alto: aperte lungo +Y e +X.
Per ognuna: linea di spinta (ugello) sul baricentro AD ALI APERTE a meta' vita (si spinge ad ali aperte), baricentro
a iodio pieno/vuoto, baricentro al lancio (ali chiuse, iodio pieno) contro DR-14, inerzie principali ad ali aperte e
chiuse. Inerzie: scatole omogenee + pezzi del payload come punti (stima di primo ordine). W1 anche con 8 ali.

Uso: python ali_stivaggio.py  ->  risultati/ali_stivaggio.txt
"""
import os
import sys

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.argv = [sys.argv[0], "L1b"]
src = open(os.path.join(QUI, "layout_bozza.py"), encoding="utf-8").read().split("# posizione del motore")[0]
exec(compile(src, "layout_bozza.py (L1b)", "exec"))

T_PAN, PASSO = 2.0, 7.0          # spessore di un'ala (FR4 + celle) e passo nella pila chiusa (con distanziali), mm
M_ALA = 0.55


def ali(conf, stato, n_lato=3):
    out = []
    lati = {"W1": ("+Y", "-Y"), "W2": ("+Y", "-Y"), "W3": ("+Y", "+X")}[conf]
    zc = HZ + 3 if conf in ("W1", "W3") else -HZ - 3
    for lato in lati:
        s = 1 if lato[0] == "+" else -1
        asse = 1 if lato[1] == "Y" else 0
        for i in range(n_lato):
            if stato == "chiuse":
                off = H + 4 + PASSO * (i + 0.5)
                c = [0.0, 0.0, 0.0]; c[asse] = s * off
                d = [226.0, 226.0, 454.0]; d[asse] = T_PAN
            else:
                off = H + 5 + 454 * (i + 0.5) + 5 * i
                c = [0.0, 0.0, zc]; c[asse] = s * off
                d = [226.0, 226.0, T_PAN]; d[asse] = 454.0
            out.append(("M-18", f"ala {lato} n.{i + 1}", "EPS", M_ALA, tuple(c), tuple(d), True))
    return out


SCHEDE = ("Computer di bordo", "Radio S XLink-S", "Radio VHF/UHF", "PCDU (P60), nella pila delle schede")
POS_SCHEDE = {"W1": "sotto", "W2": "sopra", "W3": "sotto"}   # pila delle schede sopra il motore o in fondo alla fetta -X


def configura(ym, zm, iodio, conf, stato, n_lato=3):
    lista = [c for c in piattaforma(ym, zm, iodio) if c[0] != "M-18"]
    if POS_SCHEDE[conf] == "sotto":                      # in fondo alla fetta -X, sempre contro la parete -Y (DR-70)
        zb = -HZ + 3 + 48
        lista = [(c[0], c[1], c[2], c[3], (c[4][0], c[4][1], zb), c[5], c[6]) if c[1] in SCHEDE else c for c in lista]
    return lista + ali(conf, stato, n_lato)


def sovrapposizioni(comp):
    box = [c for c in comp if not c[6] and c[5] != (1, 1, 1)]
    out = []
    for i in range(len(box)):
        for j in range(i + 1, len(box)):
            a1 = np.array(box[i][4]) - np.array(box[i][5]) / 2; b1 = np.array(box[i][4]) + np.array(box[i][5]) / 2
            a2 = np.array(box[j][4]) - np.array(box[j][5]) / 2; b2 = np.array(box[j][4]) + np.array(box[j][5]) / 2
            ov = np.minimum(b1, b2) - np.maximum(a1, a2)
            if np.all(ov > 0.5):
                out.append(f"{box[i][1]} <-> {box[j][1]}")
    for c in box:
        lo = np.array(c[4]) - np.array(c[5]) / 2; hi = np.array(c[4]) + np.array(c[5]) / 2
        if lo[2] < -HZ - 0.5 or hi[2] > HZ + 0.5 or lo[1] < -H - 0.5 or hi[1] > H + 0.5 or hi[0] > H + 0.5:
            out.append(f"{c[1]} fuori dall'involucro")
    return out


def inerzie(comp):
    m, g = baricentro(comp)
    J = np.zeros((3, 3))
    for c in comp:
        r = (np.array(c[4]) - g) / 1000; d = np.array(c[5]) / 1000; mm = c[3]
        Jc = mm / 12 * np.diag([d[1] ** 2 + d[2] ** 2, d[0] ** 2 + d[2] ** 2, d[0] ** 2 + d[1] ** 2])
        J += Jc + mm * (r @ r * np.eye(3) - np.outer(r, r))
    for pz in payload:
        r = (np.array(pz[3:6]) - g) / 1000
        J += pz[2] * (r @ r * np.eye(3) - np.outer(r, r))
    return J


righe = []
p = lambda s="": (print(s), righe.append(s))
p("PULSE A5.7.5 - Ali: baricentro, linea di spinta e inerzie (layout L1b, stima di primo ordine, TBC)")
p(f"Pila chiusa: {T_PAN} mm per ala, passo {PASSO} mm -> 3 ali {3 * PASSO + 4:.0f} mm, 4 ali {4 * PASSO + 4:.0f} mm "
  f"dalla faccia (+ sgancio, TBC) contro {SPORG} mm (D-036)")
for conf, n in (("W1", 3), ("W2", 3), ("W3", 3), ("W1", 4)):
    ym, zm = 0.0, 0.0
    for _ in range(80):
        _, g = baricentro(configura(ym, zm, 0.5, conf, "aperte", n))
        ym, zm = g[1], g[2]
    p()
    p(f"{conf} con {2 * n} ali: linea di spinta (ugello) a Y {ym:+.1f} Z {zm:+.1f} mm (baricentro ad ali aperte, meta' vita)")
    for nome, f in (("iodio pieno", 1.0), ("iodio vuoto", 0.0)):
        m, g = baricentro(configura(ym, zm, f, conf, "aperte", n))
        p(f"   ali aperte, {nome}: baricentro Y {g[1]:+6.1f} Z {g[2]:+6.1f} mm -> {np.hypot(g[1] - ym, g[2] - zm):4.1f} mm dalla linea")
    m, g = baricentro(configura(ym, zm, 1.0, conf, "chiuse", n))
    ok = abs(g[0]) <= 45 and abs(g[1]) <= 45 and abs(g[2]) <= 90
    p(f"   al lancio (ali chiuse, pieno): {m:.2f} kg, baricentro X {g[0]:+5.1f} Y {g[1]:+5.1f} Z {g[2]:+5.1f} mm -> DR-14 {'ok' if ok else 'NO'}")
    sv = sovrapposizioni([TEL, SCHEDA] + configura(ym, zm, 0.5, conf, "aperte", n))
    p(f"   motore da Z {zm - 47:+.0f} a {zm + 47:+.0f} mm, serbatoio da {zm - 147:+.0f} a {zm - 53:+.0f} mm; pila delle schede "
      f"{POS_SCHEDE[conf]} (contro la -Y); ingombri: {'nessun conflitto' if not sv else '; '.join(sv)}")
    for stato in ("aperte", "chiuse"):
        J = inerzie(configura(ym, zm, 1.0, conf, stato, n))
        prod = max(abs(J[0, 1]), abs(J[0, 2]), abs(J[1, 2]))
        p(f"   inerzie ali {stato:6s} (pieno): Ixx {J[0, 0]:.2f}  Iyy {J[1, 1]:.2f}  Izz {J[2, 2]:.2f} kg m2; prodotto max {prod:.3f}")
p()
p("D-043 (inviluppo usato in A5.3-A5.4): rollio/beccheggio 0,64-1,14 kg m2, imbardata 0,26-0,55 kg m2")
open(os.path.join(QUI, "risultati", "ali_stivaggio.txt"), "w", encoding="utf-8").write("\n".join(righe) + "\n")

# ---------------------------------------------------------------- figura: W1 e W2 viste da +X (lungo la velocita')
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

INK, MUTED, GRID = "#1f1f1e", "#6b6a64", "#e4e3dd"
C_ALA, C_RAD, C_TEL, C_MOT = "#eda100", "#2a78d6", "#9ec5f4", "#eb6834"
fig, ax = plt.subplots(2, 1, figsize=(12, 6.4))
for a, conf in zip(ax, ("W1", "W2")):
    zc = HZ + 3 if conf == "W1" else -HZ - 3
    a.add_patch(Rectangle((-H, -HZ), 2 * H, 2 * HZ, fc="#f4f3ef", ec=INK, lw=1.2))
    a.add_patch(Rectangle((-H - 4, -HZ + 20), 4, 2 * HZ - 40, fc=C_RAD, ec="none"))
    a.annotate("radiatori sulla −Y", xy=(-H - 4, 60), xytext=(-H - 330, 120), fontsize=8, color=INK,
               arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    a.add_patch(Rectangle((-H, -HZ), 140, 410, fc=C_TEL, ec="none", alpha=0.6))
    a.text(-H + 70, -HZ + 205, "tel.", ha="center", fontsize=7, color=INK)
    a.annotate("", xy=(-H + 70, -HZ - 70), xytext=(-H + 70, -HZ), arrowprops=dict(arrowstyle="->", color=MUTED))
    a.text(-H + 78, -HZ - 60, "nadir", fontsize=7, color=MUTED)
    for s in (1, -1):
        for i in range(3):
            y0 = s * (H + 5 + 459 * i)
            a.add_patch(Rectangle((min(y0, y0 + s * 454), zc - 1), 454, 2.5, fc=C_ALA, ec=C_ALA, lw=2))
        a.plot([s * H], [zc], "o", color=INK, ms=4)
    a.text(H + 700, zc + (25 if conf == "W1" else -45), "3 ali (faccia attiva verso +Z)", ha="center", fontsize=8, color=INK)
    a.text(-H - 700, zc + (25 if conf == "W1" else -45), "3 ali", ha="center", fontsize=8, color=INK)
    a.set_xlim(-1550, 1550); a.set_ylim(-320, 300); a.set_aspect("equal")
    tit = {"W1": "W1 · cerniere sullo spigolo alto (+Z)", "W2": "W2 · cerniere sullo spigolo basso (−Z, nadir)"}[conf]
    a.set_title(tit, fontsize=9, color=INK, loc="left")
    a.set_xlabel("Y (mm, lato Sole →)"); a.set_ylabel("Z (mm, zenit ↑)"); a.grid(color=GRID, lw=0.5)
fig.suptitle("PULSE A5.7.5 · Ali aperte viste lungo la velocità (+X): apertura di ~1,37 m per lato", fontsize=11, color=INK, x=0.01, ha="left")
fig.tight_layout(rect=(0, 0, 1, 0.94))
fig.savefig(os.path.join(QUI, "risultati", "ali_stivaggio.png"), dpi=150)

# ---------------------------------------------------------------- posizioni della configurazione scelta (W1, D-126) per il termico
import csv
ym, zm = 0.0, 0.0
for _ in range(80):
    _, g = baricentro(configura(ym, zm, 0.5, "W1", "aperte"))
    ym, zm = g[1], g[2]
for stato in ("aperte", "chiuse"):
    with open(os.path.join(QUI, "risultati", f"layout_componenti_W1_ali_{stato}.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["voce", "componente", "gruppo", "massa (kg)", "X (mm)", "Y (mm)", "Z (mm)", "dX (mm)", "dY (mm)", "dZ (mm)", "esterno"])
        for c in [TEL, SCHEDA] + configura(ym, zm, 0.5, "W1", stato):
            w.writerow([c[0], c[1], c[2], round(c[3], 3), *[round(v, 1) for v in c[4]], *c[5], "si" if c[6] else "no"])
