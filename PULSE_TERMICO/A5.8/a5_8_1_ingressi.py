# PULSE A5.8.1 - Dati di partenza del termico dell'intero satellite (Giuseppe, D-110)
# 1) ambiente orbitale per i casi caldo e freddo; 2) calore prodotto per modo e dove va; 3) quanto calore del motore
# REGULUS resta dentro il satellite (stima dal suo radiatore sull'ugello). Uso: python a5_8_1_ingressi.py
# Fonti: dati di Giuliano per il termico (PULSE_EPS/A5.6/termico_dati.py, A5.6.8), D-102 (eclisse), A5.6.2 (beta),
# Bellomo et al. 2022, CEAS Space J. 14:79-90 (REGULUS), datasheet GomSpace NanoPower 2600 mAh e BPX.
import numpy as np
sig = 5.670e-8

# ---------- 1) ambiente (valori di progetto, TBC) ----------
AMB = {   # nome: (Sole W/m2, albedo, IR Terra W/m2, eclisse min, beta gradi, vernice bianca alfa)
    "Caldo":  (1414, 0.35, 261, 34.7, 32, 0.35),   # gennaio (perielio), fine vita (vernice ingiallita), Terra calda
    "Freddo": (1322, 0.18, 218, 36.0, 11, 0.20),   # giugno-luglio (afelio), inizio vita, Terra fredda, eclisse piu' lunga
}
# albedo e IR: valori tipici per orbite molto inclinate (Gilmore, Spacecraft Thermal Control Handbook), TBC
# eclisse: GMAT 34,7-36,0 min (D-102); beta: 18,6-31,9 (GMAT) e 10,6-26,2 gradi (Python, altra deriva), A5.6.2
print("1) Ambiente di progetto")
for k, (S, a, ir, ecl, b, al) in AMB.items():
    print(f"  {k:7s} Sole {S} W/m2, albedo {a}, IR Terra {ir} W/m2, eclisse {ecl} min, beta {b} gradi, alfa vernice {al}")

# ---------- 3) motore REGULUS: calore che resta dentro ----------
P_in, T_thr, Isp, g0 = 50.0, 0.55e-3, 550.0, 9.80665
P_getto = T_thr * Isp * g0 / 2                         # potenza portata via dal getto
mdot = T_thr / (Isp * g0); n_ioni = mdot / (126.9 * 1.6605e-27)
P_ioniz = n_ioni * 10.45 * 1.602e-19                   # energia di ionizzazione portata via (iodio, 10,45 eV), tutto ionizzato
Q_motore = P_in - P_getto - P_ioniz                    # calore prodotto dall'unita'
# radiatore sull'ugello (paper: tutto il calore "caldo" esce da li'); faccia ~96 x 96 mm, ~275 C nel caso caldo (Tab. 3)
A_ugello, eps_ug = 0.096**2, (0.6, 0.85)
T_rad = 276 + 273.15
Q_rad = [e * sig * A_ugello * T_rad**4 for e in eps_ug]
print(f"\n3) REGULUS: getto {P_getto:.2f} W, ionizzazione {P_ioniz:.2f} W -> calore {Q_motore:.1f} W su {P_in:.0f} W "
      f"(rendimento di spinta {P_getto/P_in*100:.1f}%)")
print(f"   radiatore sull'ugello a ~276 C (96 x 96 mm, emissivita' 0,6-0,85): {Q_rad[0]:.0f}-{Q_rad[1]:.0f} W verso lo spazio")
Q_reg_int = (8.0, 15.0, 20.0)                          # TBC: calore verso il satellite (elettronica RF + linea dello iodio)
print(f"   calore che entra nel satellite dall'attacco: {Q_reg_int[0]:.0f}-{Q_reg_int[2]:.0f} W (centrale {Q_reg_int[1]:.0f} W), TBC "
      f"(stima: {Q_motore:.0f} W meno quanto esce dall'ugello; da chiedere a T4i)")

# ---------- 2) calore per modo ----------
# Apparati di Giuliano: potenza dissipata da A5.6.8 (termico_dati.py), radio S gia' senza 1,26 W di RF.
# Motore: Giuliano conta tutti i 48,5 W come dissipati nel satellite; qui si separa la quota che il radiatore
# sull'ugello butta direttamente nello spazio (sezione 3): due ipotesi, 15 W (stima, 8-20 TBC) e 48,5 W (tutto dentro).
GIUL = {"Attesa": 12.7, "Ripresa diurna": 12.7, "Ripresa notturna": 12.7, "Spinta": 64.2 - (50 - P_getto),
        "Scarico dati": 26.4, "Safe": 15.7, "Detumbling": 10.7}
PAYL = {  # calore del payload che resta nell'interno (sensore diurno); il resto va ai radiatori D-095 o al telescopio
    "Attesa": (0, 0, 3.0), "Ripresa diurna": (5.0, 7.0, 4.0), "Ripresa notturna": (0, 9.0, 4.0), "Spinta": (0, 0, 3.0),
    "Scarico dati": (0, 3.5, 3.0), "Safe": (0, 0, 2.0), "Detumbling": (0, 0, 2.0)}   # (interno, radiatori payload, telescopio)
EPS_LUCE, BATT = 6.3 + 1.4, 1.05      # A5.6.7: MPPT 8% + cavi 2% (media in luce), batteria 5% (media)
print("\n2) Calore per modo (W, nominali, senza margini; dati di Giuliano A5.6.8 + payload)")
print(f"  {'Modo':17s} {'Giuliano':>8s} {'payload int.':>12s} {'EPS+batt':>8s} {'INTERNO mot.15':>14s} {'INTERNO mot.48,5':>16s} {'radiat. payload':>15s} {'telescopio':>10s}")
for m in GIUL:
    g = GIUL[m]; pi, pr, pt = PAYL[m]; perd = EPS_LUCE + BATT
    mot = (Q_reg_int[1], 50 - P_getto) if m == "Spinta" else (0, 0)
    print(f"  {m:17s} {g:8.1f} {pi:12.1f} {perd:8.1f} {g+pi+perd+mot[0]:14.1f} {g+pi+perd+mot[1]:16.1f} {pr:15.1f} {pt:10.1f}")
print("  EPS+batt = perdite medie in luce della simulazione A5.6.7 (MPPT 6,3 + cavi 1,4 + batteria ~1 W); al buio solo batteria ~1,1 W")
print("  picchi (Giuliano): ruote negli slew +16 W per ~60 s; ricevitore S +4 W per ~1,3 h/giorno attorno ai contatti")
