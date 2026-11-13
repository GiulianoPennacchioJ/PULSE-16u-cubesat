"""A6.7 - Risposte di Giuseppe (10/11/2026) alle proposte di Giuliano D-135, D-136, D-137 + nota A5.8.9.
Uso: python a6_7_registro.py <registro_in.xlsx> <registro_out.xlsx>  (base: GitHub 831f10c)"""
import sys, openpyxl
wb = openpyxl.load_workbook(sys.argv[1])
G = '10/11/2026 Giuseppe: '
def riga(foglio, id_):
    for r in wb[foglio].iter_rows(min_row=2):
        if r[0].value == id_: return r
    raise KeyError(id_)
def nota(foglio, id_, col, testo):
    c = riga(foglio, id_)[col]
    c.value = (c.value + ' | ' if c.value else '') + G + testo
D, Q, R = 'Decisioni', 'Requisiti', 'Rischi'
ST, NOTE_D, NOTE_Q, NOTE_R, ST_R = 11, 14, 8, 12, 10
# D-135
riga(D, 'D-135')[ST].value = 'Approvata'
nota(D, 'D-135', NOTE_D, "approvata (opzione A): nessuna riga di zavorra, 0,3 kg sono ~6% dei 4,75 kg di margine di sistema; coerente con D-137 A")
# D-136
riga(D, 'D-136')[ST].value = 'Approvata'
nota(D, 'D-136', NOTE_D, "approvata con una condizione su MR-02: si approva ora la statistica delle nuvole (A6); la nuova forma di MR-02 si decide insieme DOPO i numeri, non e' fissata ora. Esempio di forma da valutare: 48 h dalla prima finestra senza nuvole nel 90% + obiettivo dichiarato 'X% degli eventi entro 48 h dall'evento'. Nella statistica entra anche il degrado con una ruota guasta (D-139, slew 45 gradi in 80 s). DR-59: Giuseppe calcola l'ora del nodo minima accettabile per le riprese diurne d'inverno, Giuliano porta l'offerta dei lanci. Piano B a ~500 km: 3,2 kN s con 28,5 kg contro 2,9 kN s di riserva, da verificare con GMAT (Giuliano). R-27: ok")
# D-137
riga(D, 'D-137')[ST].value = 'Approvata'
nota(D, 'D-137', NOTE_D, "approvata (B1). Verifica di sensibilita': con il centro di pressione 10 mm piu' lontano (34,4 mm) la coppia aerodinamica sale da 8,0e-6 a ~1,1e-5 N m e il totale in spinta (con il gradiente di gravita' di D-139) a ~1,9e-5 N m, ancora entro 2,3e-5. Nessun effetto sul payload (niente riprese in spinta). DR-74 ok")
# D-130: verifica termica del pacchetto finale
nota(D, 'D-130', NOTE_D, "modifica +5 mm in Y accettata. A5.8.9: pacchetto termico finale di Giuliano (A5.7.9) verificato contro A5.8.7: tutti i componenti nei limiti; margine piu' stretto radio S in scarico 8,6 K (41 contro 50 gradi, stima prudente con scarico continuo); magnetometro limiti TBD (a5_8_termico/a5_8_9_pacchetto_finale.py)")
# Requisiti
nota(Q, 'MR-02', NOTE_Q, "D-136 approvata: statistica delle nuvole in A6; la riformulazione si decide insieme dopo i numeri (testo e valore invariati per ora)")
nota(Q, 'DR-21', NOTE_Q, "D-137 approvata: testo e valore riscritti sulla coppia accettati; centro di pressione da rifare in Fase B (con +10 mm la coppia totale resta ~1,9e-5 N m)")
nota(Q, 'DR-59', NOTE_Q, "D-136 approvata: tolleranza da fissare insieme in A6; Giuseppe calcola l'ora del nodo minima per le riprese diurne d'inverno")
# Rischi
nota(R, 'R-08', NOTE_R, "piano D-136 approvato (statistica nuvole, poi forma di MR-02 decisa con i numeri)")
for r in ('R-11', 'R-27'):
    riga(R, r)[ST_R].value = 'In mitigazione'
    nota(R, r, NOTE_R, "piano D-136 approvato -> In mitigazione")
nota(R, 'R-26', NOTE_R, "D-135 e D-137 approvate")
wb.save(sys.argv[2])
print('ok')
