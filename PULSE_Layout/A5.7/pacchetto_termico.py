"""PULSE A5.7.9 - Pacchetto dati per il termico (D-110): componenti di Giuliano con posizione finale, attacco,
potenza dissipata per modo e limiti di temperatura, in un unico file.

Fonti: posizioni e masse da risultati/layout_componenti_W1_ali_aperte.csv (layout L1b + ali W1, masse del budget,
A5.7.7); potenze nominali per modo dal foglio Potenza del budget (P-01...P-22); limiti di temperatura da
componenti_piattaforma.py (A5.7.2). Le potenze di una voce con piu' pezzi sono divise in parti uguali.
Motore: nel modo spinta la voce vale 50 W d'ingresso, di cui ~48,5 W diventano calore; quanto entra nel satellite
dall'attacco e' TBC (15 W nel modello di Giuseppe, R-57). Radio S: in scarico 15 W d'ingresso, ~13,7 W di calore.

Uso: python pacchetto_termico.py [budget]  ->  risultati/pacchetto_termico.csv e .md
"""
import csv
import os
import sys

import openpyxl

QUI = os.path.dirname(os.path.abspath(__file__))
BUD = sys.argv[1] if len(sys.argv) > 1 else os.path.join(QUI, "..", "..", "PULSE_Budget_FaseA.xlsx")
MODI = ["Ripresa diurna", "Ripresa notturna", "Spinta", "Scarico dati", "Riposo / safe"]
pot = {}
for r in openpyxl.load_workbook(BUD)["Potenza"].iter_rows(min_row=2, max_row=26, values_only=True):
    if r[0]:
        pot[r[0]] = [v or 0.0 for v in r[4:9]]

# componente nel CSV di layout -> (voce di potenza, frazione, limiti in funzione, limiti da spento, attacco/faccia)
TAB = {
    "REGULUS: blocco motore (ugello su -X)": ("P-08", 1.0, (-25, 70), (-40, 80), "fetta -X, sporge 37 mm; staffa >= 1 W/K alla parete -Y (DR-72); radiatore dell'ugello su -X"),
    "REGULUS: serbatoio dello iodio": ("P-08", 0.0, (-25, 70), (-40, 80), "fetta -X sotto il motore; riscaldato dall'unita' (linea ~95 C)"),
    "Batteria 4S3P (sotto la pila delle schede)": ("P-19", 1.0, (0, 45), (-20, 45), "fetta +Y sotto l'IMU (carica 0/+45, scarica -20/+60); riscaldatore 6 W di riserva"),
    "PCDU (P60), nella pila delle schede": ("P-20", 1.0, (-35, 85), None, "pila delle schede, di taglio contro la parete -Y (DR-70, ~1 W/K per scheda)"),
    "Computer di bordo": ("P-17", 1.0, (-25, 65), None, "pila delle schede contro la -Y (DR-70)"),
    "Radio S XLink-S": ("P-09S", 1.0, (-20, 50), None, "pila delle schede contro la -Y (DR-70)"),
    "Radio VHF/UHF": ("P-09U", 1.0, (-10, 45), None, "pila delle schede contro la -Y (DR-70)"),
    "IMU (inviluppo KVH 1750)": ("P-03", 1.0, (-40, 75), (-50, 85), "fetta +Y a meta' altezza"),
    "Star tracker 1 (paraluce corto, verso +Z)": ("P-02", 0.5, (-40, 50), (-40, 95), "testa sotto la faccia +Z, paraluce che sporge"),
    "Star tracker 2 (paraluce corto, verso +Z)": ("P-02", 0.5, (-40, 50), (-40, 95), "testa sotto la faccia +Z, paraluce che sporge"),
    "Gruppo 4 ruote in piramide (ingombro TBC)": ("P-01", 1.0, (-20, 60), (-30, 70), "fondo della fetta +Y (picco +16 W per ~60 s negli slew)"),
    "Magnetorquer X": ("P-04", 1 / 3, (-20, 60), None, "fascia sopra il telescopio"),
    "Magnetorquer Y": ("P-04", 1 / 3, (-20, 60), None, "fascia sopra il telescopio"),
    "Magnetorquer Z": ("P-04", 1 / 3, (-20, 60), None, "angolo -X/+Y, verticale"),
    "Magnetometro (lontano dalla REGULUS)": ("P-05", 1.0, None, None, "fascia sopra il telescopio verso +X (prova -25/+70)"),
    "Ricevitore GNSS": ("P-07", 1.0, (-40, 85), (-55, 100), "fetta -X, angolo +Y"),
}
# radio: P-09 = 0,48 W di ricezione UHF sempre + 15 W di S in scarico
p09 = pot["P-09"]
pot["P-09U"] = [min(v, 0.48) for v in p09]
pot["P-09S"] = [v - 0.48 for v in p09]

righe_csv = []
with open(os.path.join(QUI, "risultati", "layout_componenti_W1_ali_aperte.csv"), encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r["componente"] in TAB:
            pid, fr, top, tsp, att = TAB[r["componente"]]
            w = [round(v * fr, 3) for v in pot[pid]]
            righe_csv.append([r["voce"], r["componente"], r["massa (kg)"], r["X (mm)"], r["Y (mm)"], r["Z (mm)"],
                              r["dX (mm)"], r["dY (mm)"], r["dZ (mm)"], *w,
                              *(top if top else ("TBD", "TBD")), *(tsp if tsp else ("TBD", "TBD")), att])
mancano = set(TAB) - {r[1] for r in righe_csv}
assert not mancano, mancano
intest = ["voce", "componente", "massa (kg)", "X (mm)", "Y (mm)", "Z (mm)", "dX (mm)", "dY (mm)", "dZ (mm)",
          *[f"{m} (W nom.)" for m in MODI], "T in funzione min (C)", "T in funzione max (C)",
          "T spento min (C)", "T spento max (C)", "attacco / note"]
with open(os.path.join(QUI, "risultati", "pacchetto_termico.csv"), "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows([intest] + righe_csv)

md = ["# PULSE A5.7.9 - Pacchetto dati per il termico (componenti di Giuliano)", "",
      "Sistema D-114 (origine nel centro geometrico, X velocità, Y lato Sole, Z zenit); layout L1b + ali W1, masse del budget "
      "(A5.7.7). Potenze nominali dal foglio Potenza del budget, senza margini. Motore in spinta: 50 W d'ingresso, ~48,5 W di "
      "calore, di cui all'interno dall'attacco TBC (15 W nel modello termico, R-57). Radio S in scarico: 15 W d'ingresso, ~13,7 W di calore.", "",
      "| Componente | Centro X / Y / Z (mm) | " + " | ".join(MODI) + " | In funzione (°C) | Attacco |",
      "|---|---|" + "---|" * len(MODI) + "---|---|"]
for r in righe_csv:
    md.append(f"| {r[1]} | {r[3]} / {r[4]} / {r[5]} | " + " | ".join(f"{v:g}" for v in r[9:14])
              + f" | {r[14]} / {r[15]} | {r[18]} |")
tot = [sum(r[9 + k] for r in righe_csv) for k in range(5)]
md += ["", "Totale nominale dei componenti elencati (W): " + ", ".join(f"{m} {t:.1f}" for m, t in zip(MODI, tot))
       + "; in piu' 0,3 W dei 6 sensori solari sulle facce esterne (P-06) -> attesa 12,7 W come in A5.6.8",
       "", "Facce esterne: -Y radiatore di piattaforma 600 cm² in basso (D-129) + sensore notturno ~125 cm² in alto (D-130); "
       "+Y e -Y ali chiuse (3 per lato, cerniere sullo spigolo +Z, DR-69); -X ugello e radiatore del motore; +Z star tracker, "
       "patch S, antenna GNSS, UHF; -Z apertura del telescopio e patch S. MLI del telescopio staccata di qualche mm dal pannello del radiatore."]
open(os.path.join(QUI, "risultati", "pacchetto_termico.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
print("\n".join(md))
