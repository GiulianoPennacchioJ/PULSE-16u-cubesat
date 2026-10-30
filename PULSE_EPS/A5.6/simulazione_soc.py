"""PULSE A5.6.7 - Simulazione dello stato di carica (SoC) della batteria, minuto per minuto.

Geometria: orbita di riferimento, ora del nodo da GMAT (D-103); giorno peggiore dei 2 anni per le ali
(fattore k minimo con rollio fisso ottimo, D-106). Ali: 6 x 21,6 W a Sole perpendicolare a fine vita (D-108).
Batteria: 4S3P 112,3 Wh nominali, 80% a fine vita (D-109). Carichi con margini voce + 20% di sistema
(come orbite_tipo.py, riscaldatori D-100 + D-107).

Regole operative (D-105, D-099, D-101):
  - spinta solo in luce, mai con la radio S in trasmissione, mai da 30 min prima a 5 min dopo una ripresa;
  - la spinta va nei minuti in cui le ali producono di piu' (scelta "golosa" sull'intero giorno);
  - riprese: assetto a nadir con rollio di 45 deg dal lato opposto al Sole per 10 min (caso peggiore per le ali);
  - fuori dalle riprese rollio fisso verso il Sole (D-106).
Rendimenti (stime TBC): MPPT 0,92, cavi 0,98, carica 0,95, scarica 0,95; carica max 0,5 C.
Uso: python simulazione_soc.py
"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from luce_eclisse import sole, una_orbita, illuminazione, PERIODO

DT = 20.0                                     # s
P_PAN, N_PAN = 21.6, 6
CAP_NOM = 112.3; EOL = 0.80
ETA_MPPT, ETA_CAVI, ETA_C, ETA_S = 0.92, 0.98, 0.95, 0.95
SIST = 1.2
m = lambda w, mg: w * (1 + mg) * SIST
BASE = m(4.0, .05) + m(1.0, .05) + m(5.0, .05) + m(0.75, .05) + m(0.3, .05) + m(0.125, .05) + m(0.48, .10) + m(0.4, .05) + m(0.6, .05)
RISC_OP, RISC_RIP, RISC_SAFE = m(3.0, .2), m(4.0, .2), m(2.0, .2)
MOTORE = m(50.0, .05) + m(3.0, .10)
RADIO = m(15.0, .10) + m(3.5, .10)            # TX S + scheda in attesa
RX_S = m(4.0, .10)
GIORNO_RIP = m(5.0, .10) + m(5.0, .10) + m(2.0, .10)    # sensore + FPGA + AI (picco)
NOTTE_RIP = m(2.0, .10) + m(5.0, .10) + m(2.0, .10)
RUOTE = m(16.0, .05)

# ---------------- geometria del giorno peggiore
G = np.loadtxt(os.path.join(os.path.dirname(os.path.abspath(__file__)), "risultati/gmat_ltdn_inclinazione.csv"), delimiter=",")
JD0 = 2461042.0417


def geometria(riga):
    giorno, inc, raan, _ = riga
    jd = JD0 + giorno
    s_dir, s_dist, _ = sole(jd)
    t, u, r, n_hat = una_orbita(jd, raan, inc, passo=DT)
    luce = illuminazione(r, s_dir, s_dist) > 0.5
    zz = r / np.linalg.norm(r, axis=1)[:, None]
    yy = np.repeat(n_hat[None, :], len(r), 0)
    xx = np.cross(yy, zz)
    sx, sy, sz = xx @ s_dir, yy @ s_dir, zz @ s_dir
    if sy.mean() < 0:
        sy = -sy
    return t, u, luce, sx, sy, sz


def cos_ali(sy, sz, phi_deg, luce):
    p = np.radians(phi_deg)
    return np.where(luce, np.clip(np.cos(p) * sz + np.sin(p) * sy, 0, None), 0.0)


def phi_ottimo(sy, sz, luce):
    best = max(range(0, 61), key=lambda ph: cos_ali(sy, sz, ph, luce)[luce].mean())
    return best, cos_ali(sy, sz, best, luce)[luce].mean()


# giorno peggiore (k minimo)
cand = []
for k in range(0, len(G), 5):
    t, u, luce, sx, sy, sz = geometria(G[k])
    ph, kk = phi_ottimo(sy, sz, luce)
    cand.append((kk, k, ph))
K_MIN, IDX, PHI = min(cand)
t1, u1, luce1, sx1, sy1, sz1 = geometria(G[IDX])
N1 = len(t1)


SOC_ON, SOC_OFF = 0.90, 0.80          # D-112: il motore parte solo con SoC >= 90% e si spegne sotto l'80%


def simula(ore_spinta=4.2, n_giorno=1, n_notte=1, stringhe=3, giorni=3, safe=False, regola=False):
    """Restituisce tempo (h), SoC (frazione della capacita' disponibile), potenze."""
    norb = int(round(giorni * 86400 / PERIODO))
    n = norb * N1
    cap = CAP_NOM * EOL * stringhe / 3
    u = np.tile(u1, norb); luce = np.tile(luce1, norb)
    sy = np.tile(sy1, norb); sz = np.tile(sz1, norb)
    orb = np.repeat(np.arange(norb), N1)
    phi = np.full(n, float(PHI))
    carico = np.full(n, BASE + (RISC_SAFE if safe else RISC_OP))
    if safe:
        # safe: ali verso il Sole entro 15 deg, nessuna operazione, magnetorquer accesi
        cs = np.where(luce, np.cos(np.radians(15)), 0.0)
        carico += m(3.0, .10)
        psa = N_PAN * P_PAN * cs
        spinta = np.zeros(n, bool)
    else:
        vieta = np.zeros(n, bool)
        # orbite con riprese: ogni giorno le prime n_giorno orbite "di giorno" e n_notte "di notte", distanziate
        orbite_giorno = norb / giorni
        for g in range(giorni):
            base_o = int(g * orbite_giorno)
            for j in range(n_giorno):
                o = base_o + 2 + 8 * j
                sel = (orb == o)
                # passaggio diurno: u ~ 138 deg (Italia centro, ramo discendente)
                ic = np.where(sel)[0][np.argmin(np.abs(u[sel] - 137.6))]
                w = int(300 / DT)
                rip = slice(ic - w, ic + w)                         # 10 min di ripresa a nadir, rollio 45 deg via dal Sole
                phi[rip] = -45.0
                carico[rip] += GIORNO_RIP + (RISC_RIP - RISC_OP)
                carico[ic - w: ic - w + int(60 / DT)] += RUOTE
                carico[ic + w: ic + w + int(120 / DT)] += RADIO     # allarmi a Fucino
                vieta[ic - int(1800 / DT): ic + w + int(300 / DT)] = True
            for j in range(n_notte):
                o = base_o + 6 + 8 * j
                sel = (orb == o)
                ic = np.where(sel)[0][np.argmin(np.abs(u[sel] - 42.4))]   # Italia centro, ramo ascendente (al buio)
                w = int(300 / DT)
                rip = slice(ic - w, ic + w)
                phi[rip] = -45.0
                carico[rip] += NOTTE_RIP + (RISC_RIP - RISC_OP)
                carico[ic - w: ic - w + int(100 / DT)] += RUOTE
                vieta[ic - int(1800 / DT): ic + w + int(300 / DT)] = True
        # contatti: Svalbard/Fairbanks vicino al punto piu' a nord (u ~ 90 deg), ~4,3 min a orbita (71 min/giorno)
        tx = np.zeros(n, bool)
        for o in range(norb):
            sel = np.where(orb == o)[0]
            ic = sel[np.argmin(np.abs(u[sel] - 90))]
            tx[ic: ic + int(4.3 * 60 / DT)] = True
        carico[tx] += RADIO
        # ricevitore S ~1,3 h/giorno attorno ai contatti
        rx = np.zeros(n, bool)
        for o in range(norb):
            sel = np.where(orb == o)[0]
            ic = sel[np.argmin(np.abs(u[sel] - 90))]
            rx[ic - int(150 / DT): ic] = True
        carico[rx] += RX_S
        psa_tmp = N_PAN * P_PAN * cos_ali(sy, sz, phi, luce)
        # spinta: giorno per giorno, nei minuti permessi con le ali piu' produttive
        spinta = np.zeros(n, bool)
        per_giorno = int(round(ore_spinta * 3600 / DT))
        npg = int(round(n / giorni))
        for g in range(giorni):
            a, b = g * npg, min((g + 1) * npg, n)
            ok = np.where(luce[a:b] & ~vieta[a:b] & ~tx[a:b])[0] + a
            scelti = ok[np.argsort(-psa_tmp[ok])][:per_giorno]
            spinta[scelti] = True
        carico[spinta] += MOTORE
        psa = psa_tmp
    p_bus = psa * ETA_MPPT * ETA_CAVI
    soc = np.zeros(n); e = cap; sciolta = 0.0
    acceso = False; passi_spinta = 0
    for i in range(n):
        car_i = carico[i]
        if spinta[i]:
            s_prev = e / cap
            if regola:
                if not acceso and s_prev >= SOC_ON:
                    acceso = True
                if acceso and s_prev < SOC_OFF:
                    acceso = False
            else:
                acceso = True
            if acceso:
                passi_spinta += 1
            else:
                car_i -= MOTORE
                carico[i] = car_i
        bil = p_bus[i] - car_i
        if bil >= 0:
            dc = min(bil * ETA_C, 0.5 * CAP_NOM * stringhe / 3)       # W in batteria (limite 0,5 C)
            e2 = min(cap, e + dc * DT / 3600)
            sciolta += (bil - (e2 - e) * 3600 / DT / ETA_C) * DT / 3600
            e = e2
        else:
            e = e + bil / ETA_S * DT / 3600
        soc[i] = e / cap
    th = np.arange(n) * DT / 3600
    simula.ore_spinta = passi_spinta * DT / 3600 / giorni
    return th, soc, carico, p_bus, cap, sciolta / giorni


casi = [
    ("Routine, Sole medio (4,2 h di spinta)", dict()),
    ("Emergenza (2+2 riprese)", dict(n_giorno=2, n_notte=2)),
    ("Routine con una stringa guasta", dict(stringhe=2)),
    ("Spinta massima sostenibile (4,9 h)", dict(ore_spinta=4.9)),
    ("Sole alto (7,8 h di spinta)", dict(ore_spinta=7.8)),
    ("Sole alto con regola 90/80% (D-112)", dict(ore_spinta=7.8, regola=True)),
    ("Routine con regola 90/80% (D-112)", dict(regola=True)),
    ("Safe", dict(safe=True)),
]
out = []; p = out.append
p("PULSE A5.6.7 - Simulazione dello stato di carica (3 giorni, giorno peggiore per le ali)")
p("Giorno peggiore: giorno %d dal 1/1/2026, rollio fisso %d deg, k = %.3f" % (G[IDX][0], PHI, K_MIN))
p("Batteria disponibile a fine vita: %.1f Wh (3 stringhe), %.1f Wh (2 stringhe)" % (CAP_NOM * EOL, CAP_NOM * EOL * 2 / 3))
p("")
p("%-40s %10s %12s %12s %12s %10s" % ("Caso", "SoC min", "DoD max", "SoC a fine", "esubero", "spinta"))
p("%-40s %10s %12s %12s %12s %10s" % ("", "%", "% (orbita)", "giorno 3 %", "Wh/giorno", "h/giorno"))
ris = {}
for nome, kw in casi:
    th, soc, car, pb, cap, sc = simula(**kw)
    # DoD per orbita = escursione tra massimo e minimo dentro l'orbita (ultimo giorno)
    # scarica piu' profonda nell'ultimo giorno: calo dal massimo dell'ultima orbita (l'eclisse attraversa u = 0)
    a0 = len(th) - int(86400 / DT)
    dods = [soc[max(0, i - N1):i + 1].max() - soc[i] for i in range(a0, len(th))]
    ris[nome] = (th, soc, car, pb)
    p("%-40s %10.1f %12.1f %12.1f %12.0f %10.2f" % (nome, 100 * soc.min(), 100 * max(dods), 100 * soc[-1], sc, simula.ore_spinta))
p("")
p("DoD max = il calo piu' profondo dal massimo dell'orbita precedente, nell'ultimo giorno (capacita' a fine vita).")
th, soc, car, pb, cap, sc = simula(ore_spinta=7.8)
k0 = np.argmax(soc < 0.5)
p("Sole alto: la batteria scende sotto il 50%% dopo %.1f h; deficit medio %.0f Wh/giorno" % (th[k0], (1 - soc[-1]) * cap / 3))
p("Esubero = energia delle ali che la batteria piena non puo' prendere (margine giornaliero).")
txt = "\n".join(out); print(txt)
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "risultati/simulazione_soc.txt"), "w").write(txt + "\n")

import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sel = ["Routine, Sole medio (4,2 h di spinta)", "Emergenza (2+2 riprese)", "Routine con una stringa guasta", "Sole alto (7,8 h di spinta)", "Sole alto con regola 90/80% (D-112)"]
fig, ax = plt.subplots(len(sel) + 1, 1, figsize=(9, 10), sharex=True)
th, soc, car, pb = ris[sel[0]]
ax[0].plot(th, pb, "#e67e22", lw=0.8, label="potenza dalle ali al bus")
ax[0].plot(th, car, "#2c3e50", lw=0.8, label="carichi (con margini)")
ax[0].set_ylabel("W"); ax[0].legend(fontsize=7, loc="upper right"); ax[0].set_title("Routine: potenza", fontsize=9, loc="left")
for a, k in zip(ax[1:], sel):
    th, soc, car, pb = ris[k]
    a.plot(th, np.clip(100 * soc, 0, None), "#2471a3", lw=1)
    a.axhline(80, color="0.6", ls="--", lw=0.8); a.axhline(70, color="#c0392b", ls=":", lw=0.8)
    a.set_ylabel("SoC %"); a.set_title(k, fontsize=9, loc="left"); a.set_ylim(max(0, min(60, 100 * soc.min() - 5)), 101)
for a in ax: a.grid(alpha=0.3)
ax[-1].set_xlabel("Ore (3 giorni)")
fig.suptitle("PULSE A5.6.7 - Stato di carica della batteria (capacità a fine vita)")
fig.tight_layout(); fig.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "risultati/figura_soc.png"), dpi=130)
