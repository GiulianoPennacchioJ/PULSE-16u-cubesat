"""Figura A5.6.2: LTDN, inclinazione e ombra per orbita - Python (due casi di deriva) e GMAT."""
import numpy as np, re, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
fig, ax = plt.subplots(3, 1, figsize=(8, 8.5), sharex=True)
for nome, col, lab in (("MDR", "#c0392b", "Python, di/dt = -0,33°/anno (MDR)"),
                       ("calcolata", "#2471a3", "Python, di/dt = -0,030°/anno")):
    R = np.loadtxt("risultati/luce_eclisse_%s.csv" % nome, delimiter=",")
    g = R[:, 0] / 30.44
    ax[0].plot(g, R[:, 2], col, lw=1.2, label=lab)
    ax[1].plot(g, R[:, 1], col, lw=1.2)
    ax[2].plot(g, R[:, 6], col, lw=1.2)
G = np.loadtxt("risultati/gmat_ltdn_inclinazione.csv", delimiter=",")
ax[0].plot(G[:, 0] / 30.44, G[:, 3], "k", lw=2, label="GMAT (Sole + Luna, J2-J4)")
ax[1].plot(G[:, 0] / 30.44, G[:, 1], "k", lw=2)
# ombra GMAT: una media al giorno
import datetime as dt
MESI = {m: i + 1 for i, m in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split())}
t, d = [], []
for l in open("gmat/PULSE_eclissi_2anni.txt"):
    if re.match(r"\d\d \w\w\w \d{4}", l) and " Earth " in l:
        c = l.split()
        t0 = dt.datetime(int(c[2]), MESI[c[1]], int(c[0]))
        t.append((t0 - dt.datetime(2026, 1, 1)).days + 0.0); d.append(float(c[-1]) / 60)
t, d = np.array(t), np.array(d)
k = d > 10
ax[2].plot(t[k] / 30.44, d[k], "k.", ms=1, label="GMAT")
ax[2].set_ylim(33, 37)
ax[0].set_ylabel("LTDN (ore)"); ax[0].axhline(10.5, color="0.6", lw=0.8, ls="--"); ax[0].legend(fontsize=8)
ax[1].set_ylabel("Inclinazione media (°)")
ax[2].set_ylabel("Ombra per orbita (min)"); ax[2].set_xlabel("Mesi dall'inizio (1 gennaio 2026)")
for a in ax: a.grid(alpha=0.3)
fig.suptitle("PULSE A5.6.2 - Luce ed eclisse: Python e verifica GMAT (2 anni)")
fig.tight_layout(); fig.savefig("risultati/figura_luce_eclisse.png", dpi=130)
