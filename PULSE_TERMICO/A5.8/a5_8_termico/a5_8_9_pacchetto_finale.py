"""A5.8.9 - Controllo del pacchetto termico finale di Giuliano (A5.7.9) contro i risultati A5.8.7.
Uso: python a5_8_9_pacchetto_finale.py <percorso pacchetto_termico.csv>
Temperature dei nodi: inviluppo dei casi A5.8.7 (motore 15-20 W) e caso di sensibilita' 48,5 W.
Schede della pila: salita locale = calore / conduttanza verso la parete (DR-70, ~1 W/K per scheda, TBC)."""
import csv, sys
NODI = {  # (min, max) in gradi C, da a5_8_7_risultati.txt
    'pila':     {'nom': (7.1, 27.6), 'motore48': (23.4, 36.7)},
    'resto':    {'nom': (14.2, 28.0), 'motore48': (27.3, 35.0)},
    'batteria': {'nom': (15.0, 23.0), 'motore48': (29.2, 32.9)},
}
G_SCHEDA = 1.0  # W/K verso la parete -Y (DR-70)
MODI = ['Ripresa diurna (W nom.)', 'Ripresa notturna (W nom.)', 'Spinta (W nom.)',
        'Scarico dati (W nom.)', 'Riposo / safe (W nom.)']
def nodo(r):
    n = r['componente'].lower()
    if 'batteria' in n: return 'batteria'
    if 'pila' in r['attacco / note'].lower(): return 'pila'
    return 'resto'
for r in csv.DictReader(open(sys.argv[1], encoding='utf-8')):
    if r['componente'].startswith('REGULUS'):
        continue  # limiti dell'unita' verificati da Giuliano (A5.7.1, ICD T4i)
    nd = nodo(r)
    try: tmin, tmax = float(r['T in funzione min (C)']), float(r['T in funzione max (C)'])
    except ValueError:
        print(f"{r['componente'][:40]:40s} limiti TBD"); continue
    p = {m: float(r[m]) for m in MODI}
    salita = (max(p.values()) * 0.92 if nd == 'pila' else 0.0) / G_SCHEDA  # ~8% esce come RF (radio)
    lo, hi = NODI[nd]['nom']; hi48 = NODI[nd]['motore48'][1]
    # in spinta la radio S e' spenta: per il caso 48,5 W la salita locale e' quella del modo spinta
    salita48 = p['Spinta (W nom.)'] / G_SCHEDA if nd == 'pila' else 0.0
    caldo = hi + salita; caldo48 = hi48 + salita48
    print(f"{r['componente'][:40]:40s} {nd:8s} limiti {tmin:5.0f}/{tmax:4.0f} | previsto {lo:5.1f}..{caldo:5.1f} "
          f"(margine {tmax-caldo:5.1f} K caldo, {lo-tmin:5.1f} K freddo) | motore 48,5 W: {caldo48:5.1f}")
