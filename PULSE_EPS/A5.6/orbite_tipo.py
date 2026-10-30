"""PULSE A5.6.3 - Orbite tipo (profilo minuto per minuto) e giorni tipo (energia giornaliera).

Orbita: periodo 90,56 min, luce 54,5 min, eclisse 36,0 min (D-102). t = 0 all'uscita dall'ombra.
Consumi: modi_potenza.py (budget P-01...P-23, D-097, D-100, D-104).
Margini: per voce come D-035 (catalogo 5%, catalogo modificato 10%, nuovo 20%) + 20% di sistema.
Uso: python orbite_tipo.py   -> risultati/orbite_tipo.txt, risultati/figura_orbite_tipo.png
"""
import numpy as np

PER, LUCE = 90.56, 54.56           # min (D-102)
ECL = PER - LUCE
DT = 1 / 60                        # passo di 1 s, in minuti
t = np.arange(0, PER, DT)
SIST = 0.20

# apparato: (W, margine voce)
A = {
    "base":        (12.655, None),   # dettaglio sotto
    "magnetorquer": (3.0, 0.10), "motore": (50.0, 0.05), "radioS": (15.0, 0.10), "rxS": (4.0, 0.10),
    "sens_giorno": (5.0, 0.10), "sens_notte": (2.0, 0.10), "fpga": (5.0, 0.10), "ai": (2.0, 0.10),
    "scheda_attesa": (3.5, 0.10), "risc_media": (2.0, 0.20), "risc_extra": (2.0, 0.20),  # 4 W a coperchio aperto = media + extra
    "risc_safe": (1.0, 0.20), "ruote_picco": (16.0, 0.05),
}
BASE = {  # W, margine
    "ruote": (4.0, 0.05), "star_tracker": (1.0, 0.05), "giroscopio": (5.0, 0.05), "magnetometro": (0.75, 0.05),
    "sensori_solari": (0.3, 0.05), "gnss": (0.125, 0.05), "radio_uhf_rx": (0.48, 0.10), "obc": (0.4, 0.05), "eps": (0.6, 0.05),
}
BASE_NOM = sum(v[0] for v in BASE.values())
BASE_MARG = sum(v[0] * (1 + v[1]) for v in BASE.values())


def profilo(eventi, base=True, risc="risc_media"):
    """eventi: lista di (apparato, inizio_min, fine_min). Restituisce potenza nominale e con margini nel tempo."""
    pn = np.zeros_like(t); pm = np.zeros_like(t)
    if base:
        pn += BASE_NOM; pm += BASE_MARG
    if risc:
        pn += A[risc][0]; pm += A[risc][0] * (1 + A[risc][1])
    for nome, a, b in eventi:
        w, m = A[nome]
        s = (t >= a) & (t < b)
        pn[s] += w; pm[s] += w * (1 + m)
    return pn, pm * (1 + SIST)


def detumbling_base():
    """Detumbling: senza ruote e star tracker."""
    return BASE_NOM - 5.0, BASE_MARG - 5.0 * 1.05


# ---------------- orbite tipo
O = {}
O["O1 Attesa"] = profilo([])
# O2 ripresa diurna: centro del passaggio 17 min dopo l'uscita dall'ombra (A5.6.2: 10-25 min)
c = 17.0
O["O2 Ripresa diurna"] = profilo([
    ("ruote_picco", c - 5, c - 4),                     # slew di 60 s verso il primo bersaglio (D-045)
    ("ruote_picco", c - 2, c - 1.7), ("ruote_picco", c + 0.5, c + 0.8), ("ruote_picco", c + 3, c + 3.3),  # rampe tra bersagli (D-101)
    ("sens_giorno", c - 4, c + 4), ("risc_extra", c - 4, c + 4),   # sensore e coperchio aperto ~8 min (D-097)
    ("fpga", c - 4, c + 6), ("ai", c + 4, c + 6),                  # FPGA 10 min, AI 2 min
    ("radioS", c + 6, c + 8), ("scheda_attesa", c + 6, c + 8),      # allarmi a Fucino ~2 min (D-081)
])
# O3 ripresa notturna, caso peggiore: tutto dentro l'eclisse; riprese che finiscono 24 min prima dell'uscita,
# contatto con Svalbard 5 min dopo per 6 min, ancora al buio (A5.6.2: passaggio 0-15 min prima dell'uscita al centro Italia)
fine = PER - 24
O["O3 Ripresa notturna"] = profilo([
    ("ruote_picco", fine - 10, fine - 8.3),                         # aggancio della linea di vista (65-112 s, A5.4)
    ("sens_notte", fine - 8, fine), ("risc_extra", fine - 8, fine),
    ("fpga", fine - 8, fine + 2), ("ai", fine, fine + 2),
    ("radioS", fine + 5, fine + 11), ("scheda_attesa", fine + 5, fine + 11),
])
O["O4a Spinta solo in luce"] = profilo([("motore", 0, LUCE), ("magnetorquer", 0, LUCE)])
O["O4b Spinta su tutta l'orbita"] = profilo([("motore", 0, PER), ("magnetorquer", 0, PER)])
O["O4c Spinta su tutta l'orbita + contatto al buio"] = profilo([
    ("motore", 0, PER), ("magnetorquer", 0, PER),
    ("radioS", LUCE + 10, LUCE + 16), ("scheda_attesa", LUCE + 10, LUCE + 16)])
O["O5 Safe"] = profilo([("magnetorquer", 0, PER)], risc="risc_safe")

out = []; p = out.append
p("PULSE A5.6.3 - Orbite tipo (luce 0-%.1f min, eclisse %.1f-%.1f min)" % (LUCE, LUCE, PER))
p("Base sempre accesa: %.2f W nominali (%.2f W con margine voce)" % (BASE_NOM, BASE_MARG))
p("")
p("%-46s %9s %9s %10s %10s %10s" % ("Orbita", "Pmax nom", "Pmax marg", "E orbita", "E eclisse", "P media"))
p("%-46s %9s %9s %10s %10s %10s" % ("", "W", "W", "Wh (marg)", "Wh (marg)", "W (marg)"))
ris = {}
for k, (pn, pm) in O.items():
    e_tot = pm.sum() * DT / 60
    e_ecl = pm[t >= LUCE].sum() * DT / 60
    ris[k] = (pn.max(), pm.max(), e_tot, e_ecl)
    p("%-46s %9.1f %9.1f %10.1f %10.1f %10.1f" % (k, pn.max(), pm.max(), e_tot, e_ecl, e_tot / PER * 60))

# ---------------- giorni tipo (energia con margini)
def m(nome):
    w, mg = A[nome]; return w * (1 + mg)

E_ATTESA_ORA = (BASE_MARG + m("risc_media"))                         # W con margine voce
inc_giorno = (m("sens_giorno") * 8 + m("fpga") * 10 + m("ai") * 2 + m("risc_extra") * 8 + m("ruote_picco") * 1.9) / 60   # Wh
inc_notte = (m("sens_notte") * 8 + m("fpga") * 10 + m("ai") * 2 + m("risc_extra") * 8 + m("ruote_picco") * 1.7) / 60
CONTATTI_MIN = 71                                                     # A5.5
RX_S_ORE = 1.3                                                        # P-09: ricevitore S attorno ai contatti
giorni = {"Routine (1+1, spinta 4,2 h)": (1, 1, 4.2), "Emergenza (2+2, spinta 4,2 h)": (2, 2, 4.2),
          "Sole alto (1+1, spinta 7,8 h)": (1, 1, 7.8), "Caso peggiore (2+2, spinta 7,8 h)": (2, 2, 7.8)}
p("")
p("Giorni tipo: energia giornaliera con margini voce + 20% di sistema")
p("%-36s %9s %9s %9s %9s %9s %10s %9s" % ("Giorno", "attesa", "riprese", "spinta", "contatti", "RX S", "TOTALE Wh", "media W"))
gris = {}
for k, (ng, nn, ore) in giorni.items():
    e_att = E_ATTESA_ORA * 24
    e_rip = ng * inc_giorno + nn * inc_notte
    e_sp = (m("motore") + m("magnetorquer")) * ore
    e_ct = (m("radioS") + m("scheda_attesa")) * CONTATTI_MIN / 60
    e_rx = m("rxS") * RX_S_ORE
    tot = (e_att + e_rip + e_sp + e_ct + e_rx) * (1 + SIST)
    gris[k] = tot
    f = 1 + SIST
    p("%-36s %9.0f %9.1f %9.0f %9.1f %9.1f %10.0f %9.1f" % (k, e_att * f, e_rip * f, e_sp * f, e_ct * f, e_rx * f, tot, tot / 24))
p("")
p("Per confronto, energia nominale (senza margini) della routine: %.0f Wh/giorno" % (
    (BASE_NOM + 2) * 24 + (5 * 8 + 5 * 10 + 2 * 2 + 2 * 8) / 60 + (2 * 8 + 5 * 10 + 2 * 2 + 2 * 8) / 60 + 53 * 4.2 + 18.5 * 71 / 60 + 4 * 1.3))
txt = "\n".join(out); print(txt)
import os; os.makedirs("risultati", exist_ok=True)
open("risultati/orbite_tipo.txt", "w").write(txt + "\n")

# ---------------- figura
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
chiavi = ["O1 Attesa", "O2 Ripresa diurna", "O3 Ripresa notturna", "O4a Spinta solo in luce",
          "O4c Spinta su tutta l'orbita + contatto al buio", "O5 Safe"]
fig, ax = plt.subplots(len(chiavi), 1, figsize=(8, 10), sharex=True)
for a, k in zip(ax, chiavi):
    pn, pm = O[k]
    a.axvspan(LUCE, PER, color="0.85", lw=0)
    a.plot(t, pn, "#2471a3", lw=1.2, label="nominale")
    a.plot(t, pm, "#c0392b", lw=1, ls="--", label="con margini")
    a.set_ylabel("W"); a.set_title(k, fontsize=9, loc="left"); a.grid(alpha=0.3)
    a.set_ylim(0, max(pm.max() * 1.15, 30))
ax[0].legend(fontsize=7, loc="upper right")
ax[-1].set_xlabel("Minuti dall'uscita dall'ombra (grigio = eclisse, 36 min)")
fig.suptitle("PULSE A5.6.3 - Orbite tipo: potenza richiesta nel giro")
fig.tight_layout(); fig.savefig("risultati/figura_orbite_tipo.png", dpi=130)
