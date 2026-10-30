"""PULSE A5.6.3 - Tabella modi x apparati (potenza nominale, W).
Valori dal file dei budget (foglio Potenza, P-01...P-23) e valori provvisori TBC per OBC ed EPS.
Uso: python modi_potenza.py"""
# apparato: (W, nota)
APP = {
    "Ruote (4)":            4.0,    # P-01, < 1 W ciascuna a regime (picco 9 W in accelerazione)
    "Star tracker (2)":     1.0,    # P-02
    "Giroscopio":           5.0,    # P-03 (inviluppo KVH 1750)
    "Magnetorquer (3)":     3.0,    # P-04, solo quando accesi
    "Magnetometro":         0.75,   # P-05
    "Sensori solari":       0.3,    # P-06
    "GNSS":                 0.125,  # P-07
    "Motore REGULUS":       50.0,   # P-08 (potenza d'ingresso nominale, 20-60 W)
    "Radio VHF/UHF (RX)":   0.48,   # P-09 sempre in ascolto
    "Radio S (TX+RX)":      15.0,   # P-09 durante i contatti
    "Sensore diurno":       5.0,    # P-12
    "Sensore notturno":     2.0,    # P-13
    "Scheda (ripresa)":     7.0,    # P-15 FPGA 5 + AI 2
    "Scheda (attesa)":      3.5,    # P-15 durante lo scarico (D-092, D-097)
    "Riscaldatori payload (picco)": 4.0,  # P-23, coperchio aperto (D-100, D-107)
    "Riscaldatori payload (media)": 3.0,  # P-23, operazioni (D-100 + 1 W di sopravvivenza D-107)
    "Riscaldatori payload (safe)":  2.0,  # P-23, safe (D-100 + D-107)
    "OBC (TBC)":            0.4,    # classe ISIS iOBC, 400 mW medi
    "EPS a vuoto (TBC)":    0.6,    # classe GomSpace P60 (ACU + PDU), 600 mW in attesa
    "Termico piattaforma (TBD)": 0.0,  # riscaldatori batteria: da A5.6.6
}
BASE = ["Ruote (4)", "Star tracker (2)", "Giroscopio", "Magnetometro", "Sensori solari", "GNSS",
        "Radio VHF/UHF (RX)", "OBC (TBC)", "EPS a vuoto (TBC)", "Termico piattaforma (TBD)"]
MODI = {
    "Attesa (riposo in operazioni)": BASE + ["Riscaldatori payload (media)"],
    "Ripresa diurna":   BASE + ["Sensore diurno", "Scheda (ripresa)", "Riscaldatori payload (picco)"],
    "Ripresa notturna": BASE + ["Sensore notturno", "Scheda (ripresa)", "Riscaldatori payload (picco)"],
    "Spinta":           BASE + ["Magnetorquer (3)", "Motore REGULUS", "Riscaldatori payload (media)"],
    "Scarico dati":     BASE + ["Radio S (TX+RX)", "Scheda (attesa)", "Riscaldatori payload (media)"],
    "Spinta + scarico": BASE + ["Magnetorquer (3)", "Motore REGULUS", "Radio S (TX+RX)", "Scheda (attesa)", "Riscaldatori payload (media)"],
    "Safe":             BASE + ["Magnetorquer (3)", "Riscaldatori payload (safe)"],
    "Detumbling":       [a for a in BASE if a not in ("Ruote (4)", "Star tracker (2)")] + ["Magnetorquer (3)", "Riscaldatori payload (safe)"],
}
MARG = 1.2 * 1.10   # stima: margine voce medio ~10% + margine di sistema 20% (D-035); il conto vero e' nel file dei budget
righe = []
for m, lst in MODI.items():
    w = sum(APP[a] for a in lst)
    righe.append((m, w, w * MARG))
    print("%-32s %6.1f W nominali  ~%5.1f W con margini" % (m, w, w * MARG))
print("Base sempre accesa (piattaforma): %.2f W" % sum(APP[a] for a in BASE))
