"""PULSE A5.7 - Verifica di D-116 (Proposta di Giuseppe) sul bilancio di potenza: quanta spinta resta con i
riscaldatori di piattaforma (P-24) accesi.

Usa la simulazione dello stato di carica di A5.6.7 (PULSE_EPS/A5.6/simulazione_soc.py) senza cambiarla: i
riscaldatori sono un carico costante in piu' (giorno e notte, W al bus) sommato ai carichi di base.
Giorno peggiore per le ali (fine maggio, rollio 32 gradi), cioe' la stessa stagione del caso "routine d'estate" di
Giuseppe (A5.8.2): i due casi peggiori coincidono.

Spinta massima sostenibile = il numero piu' alto di ore chieste che la regola di bordo D-112 (motore acceso solo
con SoC >= 90%, spento sotto l'80%) lascia fare per intero, su 3 giorni.

Uso: python riscaldatori_potenza.py  ->  risultati/riscaldatori_potenza.txt
"""
import os
import sys

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
A56 = os.path.normpath(os.path.join(QUI, "..", "..", "PULSE_EPS", "A5.6"))
sys.path.insert(0, A56)
src = open(os.path.join(A56, "simulazione_soc.py"), encoding="utf-8").read()
src = src.split('\np("Giorno peggiore')[0].split("\ncasi = [")[0]
src = src.replace('os.path.dirname(os.path.abspath(__file__))', repr(A56))
exec(compile(src, "simulazione_soc.py (A5.6.7)", "exec"))

BASE0 = BASE
MARGINI = 1.2 * 1.2        # voce "Nuovo" 20% x margine di sistema 20%, come i carichi di A5.6 (D-035)

righe = []
p = lambda s="": (print(s), righe.append(s))
p("PULSE A5.7 - Riscaldatori di piattaforma (D-116) e spinta sostenibile (modello A5.6.7, regola D-112)")
p("Spinta necessaria con Sole medio: 4,2 h/giorno (D-108)")
p()
p(f"{'riscaldatori al bus':>20} {'energia':>12} {'spinta max':>12} {'esito':>10} {'SoC min':>8} {'senza spinta':>13} {'safe':>6}")
for h in (0.0, 1.0, 2.0, 3.0, 4.0, 4.4, 5.0, 6.0, 5.0 * MARGINI, 9.0, 11.0):
    BASE = BASE0 + h
    best, smin = 0.0, float("nan")  # nan = nessuna spinta possibile
    for o in np.arange(0.5, 6.01, 0.1):
        _, soc, *_ = simula(ore_spinta=o, regola=True)
        if simula.ore_spinta >= 0.99 * o:
            best, smin = o, 100 * soc.min()
    _, soc0, *_ = simula(ore_spinta=0.0)
    _, socs, *_ = simula(safe=True)
    BASE = BASE0
    nota = " (5 W con margini)" if abs(h - 5.0 * MARGINI) < 1e-9 else ""
    p(f"{h:>17.1f} W {24 * h:>8.0f} Wh/g {best:>9.1f} h {'ok' if best >= 4.2 - 1e-9 else 'NON basta':>10} "
      f"{smin:>7.0f}% {100 * soc0.min():>12.0f}% {100 * socs.min():>5.0f}%{nota}")
p()
p("senza spinta / safe: SoC minimo su 3 giorni (motore spento), per i casi freddi di D-115 (11 W e 9 W di Giuseppe)")

os.makedirs(os.path.join(QUI, "risultati"), exist_ok=True)
open(os.path.join(QUI, "risultati", "riscaldatori_potenza.txt"), "w", encoding="utf-8").write("\n".join(righe) + "\n")
