"""PULSE A5.7.6 - Bilancio di massa: totali per sottosistema, massa secca e bagnata, sensibilita'.

Legge PULSE_Budget_FaseA.xlsx (foglio Massa, Liste, Parametri) e rifa' i conti delle formule del file
(massa nominale = quantita' x massa unitaria; margine della voce dalla maturita' (D-035); cablaggi = 5% della somma
delle altre voci nominali; margine di sistema 20%), cosi' da controllarle senza Excel e aggiungere:
- ripartizione per sottosistema, nominale e con margini;
- massa secca (senza iodio, 2,04 kg da D-117) e bagnata;
- sensibilita': 8 ali (D-127), cablaggi sulla sola massa secca, deployer da 24 kg (R-11);
- confronto con la massa usata nel modello di layout (layout_bozza.py / ali_stivaggio.py).

Uso: python massa_bilancio.py [percorso del budget]  ->  risultati/massa_bilancio.txt
"""
import os
import sys
from collections import OrderedDict

import openpyxl

QUI = os.path.dirname(os.path.abspath(__file__))
F = sys.argv[1] if len(sys.argv) > 1 else os.path.join(QUI, "..", "..", "PULSE_Budget_FaseA.xlsx")
wb = openpyxl.load_workbook(F)
par = {r[0].value: r[1].value for r in wb["Parametri"].iter_rows(min_row=2) if r[0].value}
MARG_SIS, QUOTA_CAB = par["Margine di sistema (massa e potenza)"], par["Cablaggi, quota minima della massa secca nominale"]
OBIETTIVO, MASSIMO = par["Obiettivo di massa al rilascio"], par["Massimo di massa al rilascio"]
lis = {r[0].value: r[1].value for r in wb["Liste"].iter_rows(min_row=2, max_row=4) if r[0].value}
IODIO = 2.04                                    # kg, D-117 (11.000 N s / 550 s)

voci = []
for r in wb["Massa"].iter_rows(min_row=2, max_row=26):
    if not r[0].value:
        continue
    idv, sub, nome, q, mu, mat = r[0].value, r[1].value, r[2].value, r[4].value, r[5].value, r[7].value
    voci.append([idv, sub, nome, q, mu, mat, lis[mat]])
nom = lambda v: v[3] * v[4]
cab = [v for v in voci if v[0] == "M-25"][0]
altre = [v for v in voci if v[0] != "M-25"]


def totali(voci_, quota=QUOTA_CAB, base_secca=False):
    somma = sum(nom(v) for v in voci_ if v[0] != "M-25")
    m_cab = quota * (somma - (IODIO if base_secca else 0))
    n = somma + m_cab
    mv = sum(nom(v) * (1 + v[6]) for v in voci_ if v[0] != "M-25") + m_cab * (1 + cab[6])
    return n, mv, mv * (1 + MARG_SIS), m_cab


righe = []
p = lambda s="": (print(s), righe.append(s))
n, mv, tot, m_cab = totali(voci)
p("PULSE A5.7.6 - Bilancio di massa (dal file dei budget; stima di Fase A)")
p(f"Voci: {len(voci)}; cablaggi {m_cab:.3f} kg ({QUOTA_CAB:.0%} della somma nominale delle altre voci, iodio compreso)")
p()
p(f"{'sottosistema':16s} {'nominale':>9s} {'con margine':>12s} {'quota':>6s}")
sub = OrderedDict()
for v in voci:
    m = m_cab if v[0] == "M-25" else nom(v)
    s = sub.setdefault(v[1], [0.0, 0.0]); s[0] += m; s[1] += m * (1 + v[6])
for k, (a, b) in sub.items():
    p(f"{k:16s} {a:8.2f}  {b:11.2f}  {a / n:6.1%}")
p(f"{'TOTALE':16s} {n:8.2f}  {mv:11.2f}")
p()
p(f"Massa nominale bagnata {n:.2f} kg, di cui iodio {IODIO:.2f} kg -> massa secca nominale {n - IODIO:.2f} kg")
p(f"Con i margini delle voci {mv:.2f} kg; margine di sistema {MARG_SIS:.0%} = {mv * MARG_SIS:.2f} kg")
p(f"Massa al rilascio con margini: {tot:.2f} kg -> riserva {OBIETTIVO - tot:.2f} kg sull'obiettivo di {OBIETTIVO} kg, "
  f"{MASSIMO - tot:.2f} kg sul massimo di {MASSIMO} kg (D-036)")
p(f"Margine complessivo rispetto al nominale: {tot / n - 1:.1%}")
p()
p("Sensibilita':")
v8 = [list(v) for v in voci]
for v in v8:
    if v[0] in ("M-18", "M-22"):
        v[3] = 8
n8, mv8, tot8, _ = totali(v8)
p(f"  8 ali (D-127, R-56): nominale {n8:.2f} kg, al rilascio {tot8:.2f} kg ({tot8 - tot:+.2f} kg) -> "
  f"{'entro' if tot8 <= OBIETTIVO else 'oltre'} l'obiettivo")
ns, mvs, tots, cabs = totali(voci, base_secca=True)
p(f"  cablaggi sul 5% della sola massa secca: {cabs:.3f} kg, al rilascio {tots:.2f} kg ({tots - tot:+.2f} kg): il file e' prudente")
p(f"  deployer da 24 kg (es. QuadPack, R-11): nominale {n:.2f} kg {'sotto' if n <= 24 else 'sopra'}, "
  f"con i margini {tot:.2f} kg {'sotto' if tot <= 24 else 'sopra'} ({tot - 24:+.2f} kg)")
p()
p("Confronto con il modello di layout (A5.7.4-A5.7.5, layout L1b + ali W1): 21,24 kg nominali; differenze da allineare in A5.7.7:")
p("  star tracker 0,235 -> 0,185 kg per testa (D-123, -0,10 kg); termico di piattaforma M-24 0,46 kg non ancora nel modello;")
p(f"  cablaggi {m_cab:.2f} kg (nel modello 1,01 kg)")
os.makedirs(os.path.join(QUI, "risultati"), exist_ok=True)
open(os.path.join(QUI, "risultati", "massa_bilancio.txt"), "w", encoding="utf-8").write("\n".join(righe) + "\n")
