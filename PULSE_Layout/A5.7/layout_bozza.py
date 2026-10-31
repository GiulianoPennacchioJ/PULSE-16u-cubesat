"""PULSE A5.7.4 - Bozza di layout (L1): posizione dei componenti, verifica di ingombri e baricentro di primo ordine.

Sistema di riferimento D-114 (Proposta): origine nel centro geometrico; X velocita'/spinta (ugello su -X),
Y lato del Sole, Z zenit (telescopio verso -Z). Involucro tra i binari 226,3 x 226,3 x 454 mm.
Telescopio nell'angolo +X/-Y (D-118, Proposta): colonna 140 x 140, X -26,85..+113,15, Y -113,15..+26,85.

Ogni componente e' una scatola (centro, dimensioni, massa). Il payload viene pezzo per pezzo dal CSV di Giuseppe
(PULSE_payload_masse_posizioni.csv: Z dalla faccia a nadir -> Z - 227; X spostato di +43,15 mm con D-118).
La REGULUS (D-117) e' in due blocchi uguali (2,2 L in tutto -> 94 x 95 x 123 mm ciascuno, TBC), motore e serbatoio
serbatoio sotto il motore sulla -X; ripartizione della massa TBC (motore 1,98 kg, serbatoio a vuoto 1,98 kg + iodio 2,04 kg).
Il blocco motore viene messo con l'ugello sul baricentro a meta' vita (iodio a meta'), iterando.

Stima di primo ordine (TBC): niente M-24 (termico di piattaforma, Giuseppe), niente zavorra, ali chiuse.
Uso: python layout_bozza.py [L1|L1b]  ->  risultati/layout_bozza[_L1b].txt, layout_componenti[_L1b].csv, layout_bozza[_L1b].png
"""
import csv
import os
import sys

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
RIS = os.path.join(QUI, "risultati")
os.makedirs(RIS, exist_ok=True)
H = 226.3 / 2          # mezzo lato (X, Y)
HZ = 454.0 / 2         # mezzo lato lungo (Z)
SPORG = 39.5           # sporgenza laterale massima (D-036)
DX_TEL = H - 70.0      # spostamento del telescopio in X con D-118 (+43,15 mm)
VAR = sys.argv[1] if len(sys.argv) > 1 else "L1"   # L1: schede sulla +Y; L1b: schede contro la -Y (DR-70), IMU sulla +Y
SUF = "" if VAR == "L1" else "_" + VAR

# ---------------------------------------------------------------- payload (Giuseppe), pezzo per pezzo
payload = []
with open(os.path.join(QUI, "..", "..", "PULSE_A5_Payload_calcoli", "PULSE_payload_masse_posizioni.csv"), encoding="utf-8") as f:
    for r in csv.DictReader(f):
        payload.append((r["voce budget"], r["pezzo"], float(r["massa nominale (g)"]) / 1000,
                        float(r["X (mm)"]) + DX_TEL, float(r["Y dal centro faccia (mm)"]), float(r["Z dalla faccia a nadir (mm)"]) - 227.0))

# ---------------------------------------------------------------- componenti come scatole
# (voce, nome, gruppo, massa kg, centro (x, y, z) mm, dimensioni (dx, dy, dz) mm, esterno?)
TEL = ("M-11", "Colonna del telescopio (ingombro, massa nei pezzi)", "Payload", 0.0,
       (H - 70, -H + 70, (-227 + 183) / 2), (140, 140, 410), False)
SCHEDA = ("M-15", "Scheda payload (D-091, ruotata: 60 mm lungo Y)", "Payload", 0.0, (DX_TEL, 60, 103), (100, 60, 100), False)

LMOT = (123, 95, 94)           # blocco motore: profondita' lungo X (ugello), Y, Z  (TBC, ICD T4i)
M_MOT, M_TANK, M_I2 = 1.98, 1.98, 2.04


def piattaforma(ym, zm, iodio):
    xm = -H + LMOT[0] / 2 - 37.0                          # sporge di 37 mm dalla faccia -X (fetta di 86 mm, D-118)
    lista = [
        ("M-08", "REGULUS: blocco motore (ugello su -X)", "Propulsione", M_MOT, (xm, ym, zm), LMOT, False),
        ("M-08", "REGULUS: serbatoio dello iodio", "Propulsione", M_TANK + M_I2 * iodio, (xm, ym, zm - 100), LMOT, False),
        ("M-19", "Batteria 4S3P (sotto la pila delle schede)", "EPS", 0.75, (43, 70, -79), (93, 86, 62), False),
        ("M-20", "PCDU (P60), nella pila delle schede", "EPS", 0.282, (25, 97.5, 3), (92, 29, 89), False),
        ("M-03", "IMU (inviluppo KVH 1750)", "GNC", 0.70, (-H + 37 + 1, -66, 182), (74, 89, 89), False),
        ("M-02", "Star tracker 1 (paraluce corto, verso +Z)", "GNC", 0.235, (-70, 70, 193), (56, 62, 68), False),
        ("M-02", "Star tracker 2 (paraluce corto, verso +Z)", "GNC", 0.235, (75, 58, 193), (62, 56, 68), False),
        ("M-01", "Gruppo 4 ruote in piramide (ingombro TBC)", "GNC", 1.32, (43, 70, -170), (130, 80, 110), False),
        ("M-04", "Magnetorquer X", "GNC", 0.20, (37.6, -105, 192), (152, 13, 13), False),
        ("M-04", "Magnetorquer Y", "GNC", 0.20, (-10, -43, 215), (13, 140, 13), False),
        ("M-04", "Magnetorquer Z", "GNC", 0.20, (-100, 100, 0), (13, 13, 152), False),
        ("M-05", "Magnetometro (lontano dalla REGULUS)", "GNC", 0.085, (80, -50, 212), (43, 99, 17), False),
        ("M-07", "Ricevitore GNSS", "Avionica e TT&C", 0.024, (-70, 85, 100), (71, 46, 11), False),
        ("M-07", "Antenna GNSS (+Z)", "Avionica e TT&C", 0.051, (-70, 100, HZ + 5), (40, 40, 10), True),
        ("M-17", "Computer di bordo", "Avionica e TT&C", 0.10, (25, 34.2, 3), (90, 12.4, 96), False),
        ("M-09", "Radio S XLink-S", "Avionica e TT&C", 0.20, (25, 53.7, 3), (90, 25.3, 65), False),
        ("M-09", "Radio VHF/UHF", "Avionica e TT&C", 0.075, (25, 74.5, 3), (90, 15, 96), False),
        ("M-10", "Patch S a nadir (striscia a L)", "Avionica e TT&C", 0.05, (-70, 70, -HZ - 5), (60, 60, 10), True),
        ("M-10", "Patch S a zenit (accanto al telescopio)", "Avionica e TT&C", 0.05, (-70, -40, HZ + 5), (80, 80, 9), True),
        ("M-10", "Antenna VHF/UHF dispiegabile (AntS)", "Avionica e TT&C", 0.089, (43, -43, HZ + 4), (98, 98, 7), True),
        ("M-06", "Sensori solari (6 facce, centro medio)", "GNC", 0.21, (0, 0, 0), (1, 1, 1), True),
        ("M-21", "Telaio 16U", "Struttura", 2.50, (0, 0, 0), (1, 1, 1), False),
        ("M-22", "Meccanismi delle ali (verso +Z)", "Struttura", 0.36, (40, 40, 200), (1, 1, 1), True),
        ("M-18", "3 ali chiuse sulla faccia +Y", "EPS", 1.65, (0, H + 8, 0), (226, 12, 454), True),
        ("M-18", "3 ali chiuse sulla faccia +X", "EPS", 1.65, (H + 8, 0, 0), (12, 226, 454), True),
        ("M-25", "Cablaggi (5%, al centro)", "Struttura", 1.01, (0, 0, 0), (1, 1, 1), False),
    ]
    if VAR == "L1b":
        # pila delle schede nella fetta -X, sopra il motore, di taglio contro la parete -Y (radiatore, DR-70);
        # schede nel piano Y-Z (90 mm lungo Y), impilate lungo X; IMU al posto delle schede sulla +Y
        zb, yb = zm + 47 + 3 + 48, -H + 2 + 45
        nuovi = {
            "Computer di bordo": ((-104.8, yb, zb), (12.4, 90, 96)),
            "Radio S XLink-S": ((-85.35, yb, zb), (25.3, 90, 65)),
            "Radio VHF/UHF": ((-64.5, yb, zb), (15, 90, 96)),
            "PCDU (P60), nella pila delle schede": ((-41.5, yb + 1, zb), (29, 92, 89)),
            "IMU (inviluppo KVH 1750)": ((25, 70, 3), (89, 74, 89)),
        }
        out = []
        for c in lista:
            if c[1] in nuovi:
                c = (c[0], c[1], c[2], c[3], nuovi[c[1]][0], nuovi[c[1]][1], c[6])
            out.append(c)
        lista = out
    return lista


def baricentro(comp):
    m = sum(c[3] for c in comp) + sum(p[2] for p in payload)
    r = sum(c[3] * np.array(c[4]) for c in comp) + sum(p[2] * np.array(p[3:6]) for p in payload)
    return m, r / m


# posizione del motore: ugello sul baricentro a meta' vita (iterazione di punto fisso)
ym, zm = 0.0, 0.0
for _ in range(50):
    m, g = baricentro(piattaforma(ym, zm, 0.5))
    ym, zm = g[1], g[2]
comp = [TEL, SCHEDA] + piattaforma(ym, zm, 0.5)

righe = []
p = lambda s="": (print(s), righe.append(s))
p(f"PULSE A5.7.4 - Bozza di layout {VAR} (stima di primo ordine, TBC)")
p(f"Linea di spinta (ugello) a Y {ym:+.1f} mm, Z {zm:+.1f} mm: e' il baricentro a meta' vita")
for nome, f in (("iodio pieno", 1.0), ("meta' vita", 0.5), ("iodio vuoto", 0.0)):
    m, g = baricentro(piattaforma(ym, zm, f))
    d = np.hypot(g[1] - ym, g[2] - zm)
    p(f"  {nome:12s}: massa {m:5.2f} kg, baricentro X {g[0]:+6.1f} Y {g[1]:+6.1f} Z {g[2]:+6.1f} mm; "
      f"distanza dalla linea di spinta {d:4.1f} mm (D-047 <= 10); DR-14 {'ok' if abs(g[0]) <= 45 and abs(g[1]) <= 45 and abs(g[2]) <= 90 else 'NO'}")

# verifiche geometriche: involucro e sovrapposizioni tra scatole interne
p()
p("Verifiche di ingombro (scatole interne; pareti e attacchi esclusi):")
interni = [c for c in comp if not c[6] and c[5] != (1, 1, 1)]


def lim(c):
    cc, dd = np.array(c[4]), np.array(c[5]) / 2
    return cc - dd, cc + dd


fuori = []
for c in interni:
    a, b = lim(c)
    sx = max(-H - a[0], b[0] - H, 0); sy = max(-H - a[1], b[1] - H, 0); sz = max(-HZ - a[2], b[2] - HZ, 0)
    if max(sx, sy, sz) > 0.5:
        fuori.append(f"  {c[1]}: sporge {max(sx, sy):.0f} mm di lato, {sz:.0f} mm in Z (limite di lato {SPORG} mm)")
p("\n".join(fuori) if fuori else "  nessun componente fuori dall'involucro")
sov = []
for i in range(len(interni)):
    for j in range(i + 1, len(interni)):
        a1, b1 = lim(interni[i]); a2, b2 = lim(interni[j])
        ov = np.minimum(b1, b2) - np.maximum(a1, a2)
        if np.all(ov > 0.5):
            sov.append(f"  {interni[i][1]}  <->  {interni[j][1]}: {ov[0]:.0f} x {ov[1]:.0f} x {ov[2]:.0f} mm")
p("Sovrapposizioni:\n" + "\n".join(sov) if sov else "  nessuna sovrapposizione tra le scatole")
p()
p("Distanze utili:")
mag = [c for c in comp if c[0] == "M-05"][0][4]
p(f"  magnetometro - blocco motore REGULUS (magneti del motore, D-117): {np.linalg.norm(np.array(mag) - np.array([-H + LMOT[0] / 2 - 37, ym, zm])):.0f} mm")
tank = np.array([0, ym, zm - 100])
p(f"  serbatoio - linea di spinta: {100:.0f} mm (DR-67 chiede <= ~70 mm: vedi spostamento del baricentro sopra)")
open(os.path.join(RIS, f"layout_bozza{SUF}.txt"), "w", encoding="utf-8").write("\n".join(righe) + "\n")

with open(os.path.join(RIS, f"layout_componenti{SUF}.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["voce", "componente", "gruppo", "massa (kg)", "X (mm)", "Y (mm)", "Z (mm)", "dX (mm)", "dY (mm)", "dZ (mm)", "esterno"])
    for c in comp:
        w.writerow([c[0], c[1], c[2], round(c[3], 3), *[round(v, 1) for v in c[4]], *c[5], "si" if c[6] else "no"])

# ---------------------------------------------------------------- disegno: 3 sezioni orizzontali + vista laterale
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

COL = {"Payload": "#2a78d6", "Propulsione": "#eb6834", "GNC": "#1baf7a", "EPS": "#eda100",
       "Avionica e TT&C": "#6250d6", "Struttura": "#898781"}
INK, MUTED, GRID = "#1f1f1e", "#6b6a64", "#e4e3dd"
plt.rcParams.update({"font.size": 8, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED})
CORTI = {"M-01": "ruote", "M-02": "star tracker", "M-03": "IMU", "M-19": "batteria", "M-20": "PCDU", "M-17": "OBC",
         "M-05": "magnetometro", "M-07": "GNSS", "M-15": "scheda payload", "M-11": "telescopio", "M-04": "MTQ"}


def etichetta(c):
    if c[0] == "M-08":
        return "motore" if "motore" in c[1] else "serbatoio"
    if c[0] == "M-09":
        return "radio S" if "XLink" in c[1] else "UHF"
    return CORTI.get(c[0], "")


def scatola(a, c, i, j, testo=True, ruota=False):
    cc, dd = c[4], c[5]
    a.add_patch(Rectangle((cc[i] - dd[i] / 2, cc[j] - dd[j] / 2), dd[i], dd[j], fc=COL[c[2]], ec="white", lw=1.2,
                          alpha=0.22 if c[0] == "M-11" else 0.75))
    lab = etichetta(c)
    if testo and lab and min(dd[i], dd[j]) >= 12:
        rot = 90 if (dd[j] > 2.2 * dd[i] and dd[i] < 40) else 0
        a.text(cc[i], cc[j], lab, ha="center", va="center", fontsize=7, color=INK, rotation=rot)


disegnabili = [c for c in comp if c[5] != (1, 1, 1) and c[0] not in ("M-18", "M-10") and c[0] != "M-07" or c[1] == "Ricevitore GNSS"]
fig, ax = plt.subplots(1, 5, figsize=(20, 6.4), gridspec_kw={"width_ratios": [1, 1, 1, 1, 1.25]})
_, gm = baricentro(piattaforma(ym, zm, 0.5))
for a, zc, tit in zip(ax[:4], (195, 95, 0, -170), ("Sezione a Z +195 mm (verso zenit)", "Sezione a Z +95 mm",
                                                     "Sezione a Z 0 (centro)", "Sezione a Z −170 mm (verso nadir)")):
    a.add_patch(Rectangle((-H, -H), 2 * H, 2 * H, fill=False, ec=INK, lw=1.2))
    for c in disegnabili:
        lo, hi = c[4][2] - c[5][2] / 2, c[4][2] + c[5][2] / 2
        if lo <= zc <= hi:
            scatola(a, c, 0, 1)
    if zc == 0:
        a.plot(gm[0], gm[1], marker="+", ms=12, mew=2, color=INK)
        a.annotate("", xy=(-H - 37 - 30, ym), xytext=(-H - 37, ym), arrowprops=dict(arrowstyle="->", color=COL["Propulsione"], lw=1.6))
    a.text(H + 3, 0, "ali chiuse +X", rotation=90, va="center", fontsize=7, color=MUTED)
    a.text(0, H + 4, "ali chiuse +Y", ha="center", fontsize=7, color=MUTED)
    a.text(0, -H - 12, "radiatori −Y", ha="center", fontsize=7, color=MUTED)
    a.set_xlim(-H - 75, H + 20); a.set_ylim(-H - 20, H + 18); a.set_aspect("equal")
    a.set_title(tit, fontsize=9, color=INK, loc="left"); a.set_xlabel("X (mm, velocità →)"); a.set_ylabel("Y (mm, lato Sole ↑)")
    a.grid(color=GRID, lw=0.5)
a = ax[4]
a.add_patch(Rectangle((-H, -HZ), 2 * H, 2 * HZ, fill=False, ec=INK, lw=1.2))
for c in sorted(disegnabili, key=lambda c: c[4][1]):          # dal fondo (-Y) verso chi guarda (+Y)
    scatola(a, c, 0, 2, testo=c[0] in ("M-08", "M-11", "M-15", "M-01", "M-03", "M-19"))
a.plot(gm[0], gm[2], marker="+", ms=12, mew=2, color=INK)
a.annotate("", xy=(-H - 37 - 30, zm), xytext=(-H - 37, zm), arrowprops=dict(arrowstyle="->", color=COL["Propulsione"], lw=1.6))
a.text(-H - 70, zm + 10, "getto", fontsize=7, color=INK)
a.text(0, HZ + 6, "faccia +Z (zenit): ST, patch S, GNSS, UHF", ha="center", fontsize=7, color=MUTED)
a.text(0, -HZ - 16, "faccia −Z (nadir): apertura, patch S", ha="center", fontsize=7, color=MUTED)
a.set_xlim(-H - 75, H + 20); a.set_ylim(-HZ - 25, HZ + 20); a.set_aspect("equal")
a.set_title("Vista da +Y (tutto proiettato)", fontsize=9, color=INK, loc="left")
a.set_xlabel("X (mm, velocità →)"); a.set_ylabel("Z (mm, zenit ↑)"); a.grid(color=GRID, lw=0.5)
for nome, colr in COL.items():
    if nome != "Struttura":
        ax[0].plot([], [], "s", color=colr, alpha=0.75, ms=9, label=nome)
ax[0].plot([], [], "+", color=INK, ms=10, mew=2, label="baricentro a metà vita = linea di spinta")
fig.legend(loc="lower center", ncol=6, frameon=False, fontsize=8)
fig.suptitle(f"PULSE A5.7.4 · Bozza di layout {VAR} (sistema D-114, telescopio D-118; stima di primo ordine, TBC)",
             fontsize=11, color=INK, x=0.01, ha="left")
fig.tight_layout(rect=(0, 0.06, 1, 0.95))
fig.savefig(os.path.join(RIS, f"layout_bozza{SUF}.png"), dpi=150)
