"""PULSE A5.7 - Profilo di spinta per orbita (dati per il termico di Giuseppe, A5.8).

Usa la simulazione dello stato di carica di A5.6.7 (PULSE_EPS/A5.6/simulazione_soc.py) senza cambiarla:
il sorgente viene letto e, solo in memoria, si aggiunge la registrazione dei minuti in cui il motore e'
davvero acceso (con la regola D-112 il motore puo' fermarsi anche se la spinta era programmata).

Risultato: minuti di spinta per orbita nell'ultimo giorno simulato, numero di accensioni e durata dei
tratti continui, per Sole medio (4,2 h), limite dei 6 pannelli (4,9 h) e Sole alto (7,8 h chieste).
Ipotesi del modello A5.6.7 (non un piano operativo): spinta solo in luce, nei minuti di massima
produzione delle ali, fuori dalla trasmissione S (D-105) e dal divieto attorno alle riprese (D-099).

Uso: python profilo_spinta.py  ->  risultati/profilo_spinta.txt
"""
import os
import sys

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
A56 = os.path.normpath(os.path.join(QUI, "..", "..", "PULSE_EPS", "A5.6"))
sys.path.insert(0, A56)

src = open(os.path.join(A56, "simulazione_soc.py"), encoding="utf-8").read()
src = src.split('\np("Giorno peggiore')[0]          # solo definizioni, niente stampe e figure di A5.6.7
src = src.split("\ncasi = [")[0]
patch = [
    ("    acceso = False; passi_spinta = 0",
     "    acceso = False; passi_spinta = 0\n    ON = np.zeros(n, bool); simula.ON = ON; simula.orb = orb"),
    ("            if acceso:\n                passi_spinta += 1",
     "            if acceso:\n                passi_spinta += 1\n                ON[i] = True"),
]
for vecchio, nuovo in patch:
    assert vecchio in src, "simulazione_soc.py e' cambiata: aggiornare profilo_spinta.py"
    src = src.replace(vecchio, nuovo)
src = src.replace('os.path.dirname(os.path.abspath(__file__))', repr(A56))
exec(compile(src, "simulazione_soc.py (A5.6.7)", "exec"))

righe = []
p = lambda s="": (print(s), righe.append(s))
p("PULSE A5.7 - Profilo di spinta per orbita (modello A5.6.7, giorno peggiore per le ali)")
p(f"Periodo {PERIODO / 60:.1f} min, luce per orbita {luce1.sum() * DT / 60:.1f} min, passo {DT:.0f} s")

casi = [("Sole medio, 4,2 h", dict(ore_spinta=4.2)),
        ("Limite dei 6 pannelli, 4,9 h", dict(ore_spinta=4.9)),
        ("Sole alto, 7,8 h chieste, regola 90/80% (D-112)", dict(ore_spinta=7.8, regola=True)),
        ("Sole alto, 7,8 h senza regola (la batteria si svuota: caso non reale)", dict(ore_spinta=7.8))]
for nome, kw in casi:
    simula(**kw)
    ON, orb = simula.ON, simula.orb
    norb = orb.max() + 1
    minuti = np.array([ON[orb == o].sum() * DT / 60 for o in range(norb)])
    ultimo = minuti[int(2 * norb / 3):]
    tratti, c = [], 0
    for v in ON:
        if v:
            c += 1
        elif c:
            tratti.append(c * DT / 60)
            c = 0
    accensioni = int((np.diff(ON.astype(int)) == 1).sum())
    p()
    p(f"{nome}: {simula.ore_spinta:.2f} h/giorno effettive; orbite con spinta {int(np.sum(ultimo > 0))}/{len(ultimo)} (ultimo giorno)")
    p("  minuti per orbita: " + " ".join(f"{x:.0f}" for x in ultimo))
    p(f"  accensioni in 3 giorni: {accensioni}; tratti continui min {min(tratti):.1f} / mediana {np.median(tratti):.1f} / max {max(tratti):.1f} min")

os.makedirs(os.path.join(QUI, "risultati"), exist_ok=True)
open(os.path.join(QUI, "risultati", "profilo_spinta.txt"), "w", encoding="utf-8").write("\n".join(righe) + "\n")
