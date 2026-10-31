"""PULSE A5.7.2 - Lista dei componenti di piattaforma (Giuliano): massa, ingombro e limiti di temperatura.

Base per il layout (A5.7.4: le posizioni si aggiungono li') e per il modello termico di Giuseppe (D-110, A5.8).
Valori di catalogo dei prodotti di riferimento (classe), con la fonte; "TBD" dove la fonte non da' il dato.
Decisioni: D-048..D-051 (ADCS), D-082/D-084 (TT&C), D-104 (OBC, PCDU), D-109 (batteria), D-117 (REGULUS),
D-119 (ali S1), D-120 (telaio T1), D-121 (valori di riferimento di OBC, batteria, PCDU, meccanismi).

Uso: python componenti_piattaforma.py  ->  risultati/componenti_piattaforma.csv e .txt
"""
import csv
import os

# id budget, componente, quantita', massa unitaria kg, ingombro mm (X x Y x Z o descrizione),
# T in funzione (min, max) C, T da spento / sopravvivenza (min, max) C, fonte
C = [
    ("M-01", "Ruota di reazione (classe BCT RWp100)", 4, 0.330, "70 x 70 x 25", (-20, 60), (-30, 70),
     "BCT Reaction Wheels 2025 (colonne della tabella incerte: TBC)"),
    ("M-02", "Star tracker ST-16RT2 con paraluce grande", 2, 0.235, "99 x 120 (paraluce grande); 62 x 56 x 38 senza", (-40, 50), (-40, 95),
     "Rocket Lab ST-16RT2 (satnow)"),
    ("M-03", "Giroscopio / IMU (inviluppo KVH 1750)", 1, 0.700, "88,9 x 88,9 x 73,7", (-40, 75), (-50, 85),
     "NovAtel IMU-KVH1750"),
    ("M-04", "Magnetorquer (barra, classe >= 2,5 A m2)", 3, 0.200, "13 x 13 x 152", (-20, 60), None,
     "Classe NewSpace NCTR (limiti); massa prudente di classe (budget)"),
    ("M-05", "Magnetometro (classe NewSpace NMRM)", 1, 0.085, "99 x 43 x 17", None, None,
     "NewSpace: solo prova di accettazione -25/+70 C"),
    ("M-06", "Sensore solare grossolano (classe NewSpace)", 6, 0.035, "34 x 32 x 20", (-25, 50), None,
     "NewSpace NCSS-SA05 -25/+50, NFSS-411 -25/+70: si usa il piu' stretto"),
    ("M-07", "Ricevitore GNSS (classe piNAV-NG) + antenna", 1, 0.075, "71,1 x 45,7 x 11 (ricevitore)", (-40, 85), (-55, 100),
     "Skyfox piNAV-NG (satnow)"),
    ("M-08", "REGULUS-50-I2 Large (motore + serbatoio, pieno)", 1, 6.000, "2 blocchi, sezione ~94 x 95, 2,2U in tutto", (-25, 70), (-40, 80),
     "T4i; Bellomo et al. 2021 (ambiente attorno all'unita'; prova -40/+80)"),
    ("M-09", "Radio S XLink-S", 1, 0.200, "90 x 65 x 25,3", (-20, 50), None, "IQ spacecom XLink-S (satnow)"),
    ("M-09", "Radio VHF/UHF di riserva (classe ISIS TRXVU)", 1, 0.075, "96 x 90 x 15", (-10, 45), None, "ISIS TRXVU brochure"),
    ("M-10", "Antenne: 2 patch S + antenna VHF/UHF dispiegabile", 1, 0.189, "patch <= 60 / 80 x 80 x 9; AntS 98 x 98 x 7", None, None,
     "ISIS (limiti TBD)"),
    ("M-17", "Computer di bordo (classe ISIS iOBC)", 1, 0.100, "96 x 90 x 12,4", (-25, 65), None, "ISIS iOBC brochure"),
    ("M-18", "Ala solare 226 x 454 mm, substrato FR4/Al (S1)", 6, 0.550, "226 x 454 x ~2", (-40, 80), None,
     "Classe AAC Photon / ISIS: 5,0-5,5 kg/m2 con celle; 9 celle Azur 3G30-Advanced (D-108)"),
    ("M-19", "Batteria Li-ion 4S3P, 12 celle 18650 2,6 Ah", 1, 0.750, "~93 x 86 x 62 (stima)", (0, 45), (-20, 45),
     "Celle GomSpace (carica 0/+45, scarica -20/+60, stoccaggio 3 mesi); massa scalata da GomSpace BPX (500 g per 8 celle)"),
    ("M-20", "PCDU classe GomSpace P60 (base + 2 ACU + 2 PDU)", 1, 0.282, "92 x 88,9 x 28,9", (-35, 85), None,
     "GomSpace P60: <80 g + 54 g/ACU + 47 g/PDU; limiti del P60 Dock"),
    ("M-21", "Telaio 16U (classe EnduroSat, Al 6082, con viti)", 1, 2.500, "226,3 x 226,3 x 454", None, None,
     "EnduroSat 16U Structure"),
    ("M-22", "Meccanismi delle ali (2 cerniere + 1 sgancio per ala)", 6, 0.060, "-", None, None,
     "Stima di primo ordine, nessuna fonte con massa: TBC"),
]

qui = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(qui, "risultati"), exist_ok=True)
fmt = lambda t: "TBD" if t is None else f"{t[0]:+d} / {t[1]:+d}"
with open(os.path.join(qui, "risultati", "componenti_piattaforma.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["voce budget", "componente", "quantita", "massa unitaria (kg)", "massa (kg)", "ingombro (mm)",
                "T in funzione min (C)", "T in funzione max (C)", "T spento min (C)", "T spento max (C)", "fonte"])
    for v, n, q, m, d, to, ts, s in C:
        w.writerow([v, n, q, m, round(q * m, 3), d,
                    *(to if to else ("TBD", "TBD")), *(ts if ts else ("TBD", "TBD")), s])

righe = ["PULSE A5.7.2 - Componenti di piattaforma (Giuliano): massa e limiti di temperatura", ""]
righe.append(f"{'voce':5} {'componente':52} {'q':>2} {'kg':>6}  {'in funzione C':>13}  {'spento C':>11}")
for v, n, q, m, d, to, ts, s in C:
    righe.append(f"{v:5} {n[:52]:52} {q:>2} {q * m:6.3f}  {fmt(to):>13}  {fmt(ts):>11}")
tot = sum(q * m for _, _, q, m, *_ in C)
righe += ["", f"Massa nominale dei componenti di piattaforma elencati: {tot:.2f} kg (iodio compreso)",
          "Limiti piu' stretti in funzione: radio VHF/UHF -10/+45 C, carica della batteria 0/+45 C, star tracker +50 C"]
open(os.path.join(qui, "risultati", "componenti_piattaforma.txt"), "w", encoding="utf-8").write("\n".join(righe) + "\n")
print("\n".join(righe))
