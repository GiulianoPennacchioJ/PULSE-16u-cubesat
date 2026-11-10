"""PULSE A5.7.10 - Figura del layout finale di Fase A (L1b con ali W1, D-125/D-126/D-137): pila delle schede in fondo
alla fetta -X contro la -Y, motore con l'ugello sul baricentro ad ali aperte a meta' vita, masse del budget.
Riusa le scatole di baricentro.py e il disegno di layout_bozza.py (4 sezioni + vista da +Y).

Uso: python figura_finale.py  ->  risultati/layout_finale.png e layout_componenti_finale.csv
"""
import csv
import os

QUI = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(QUI, "baricentro.py"), encoding="utf-8").read().split("\nrighe = []\n")[0]
exec(compile(src, "baricentro.py", "exec"))

ym, zm = ugello()
comp = [TEL, SCHEDA] + [c for c in configura(ym, zm, 0.5, "W1", "chiuse") if c[0] != "M-18"]
with open(os.path.join(RIS, "layout_componenti_finale.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["voce", "componente", "gruppo", "massa (kg)", "X (mm)", "Y (mm)", "Z (mm)", "dX (mm)", "dY (mm)", "dZ (mm)", "esterno"])
    for c in comp:
        w.writerow([c[0], c[1], c[2], round(c[3], 3), *[round(v, 1) for v in c[4]], *c[5], "si" if c[6] else "no"])

lb = open(os.path.join(QUI, "layout_bozza.py"), encoding="utf-8").read()
tail = lb[lb.index("# ---------------------------------------------------------------- disegno"):]
for a, b in (("baricentro(piattaforma(ym, zm, 0.5))", 'baricentro(configura(ym, zm, 0.5, "W1", "aperte"))'),
             ('a.text(H + 3, 0, "ali chiuse +X", rotation=90, va="center", fontsize=7, color=MUTED)', "pass"),
             ('"radiatori −Y"', '"ali chiuse e radiatori −Y"'),
             ('f"layout_bozza{SUF}.png"', '"layout_finale.png"'),
             ('c[0] not in ("M-18", "M-10")', 'c[0] not in ("M-18", "M-10", "M-24")'),
             ('fig, ax = plt.subplots(1, 5, figsize=(20, 6.4), gridspec_kw={"width_ratios": [1, 1, 1, 1, 1.25]})',
              'fig = plt.figure(figsize=(12, 9.6)); gs = fig.add_gridspec(2, 3, width_ratios=[1, 1, 1.05]); '
              'ax = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, 0]), '
              'fig.add_subplot(gs[1, 1]), fig.add_subplot(gs[:, 2])]'),
             ('fig.legend(loc="lower center", ncol=6, frameon=False, fontsize=8)', 'fig.legend(loc="lower center", ncol=3, frameon=False, fontsize=8)'),
             ('fig.tight_layout(rect=(0, 0.06, 1, 0.95))', 'fig.tight_layout(rect=(0, 0.07, 1, 0.96))'),
             ('f"PULSE A5.7.4 · Bozza di layout {VAR} (sistema D-114, telescopio D-118; stima di primo ordine, TBC)"',
              '"PULSE A5.7 · Layout di Fase A: L1b con ali W1, masse del budget (sistema D-114; primo ordine, TBC)"'),
             ('"baricentro a metà vita = linea di spinta"', '"baricentro ad ali aperte a metà vita = linea di spinta"')):
    assert a in tail, a
    tail = tail.replace(a, b)
exec(compile(tail, "layout_bozza.py (disegno)", "exec"))
print(f"ugello Y {ym:+.1f} Z {zm:+.1f} mm; figura in risultati/layout_finale.png")
