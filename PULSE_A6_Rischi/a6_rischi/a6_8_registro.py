"""A6.8 - D-140 (ora del nodo minima per le riprese diurne) + DR-59, R-11, R-04.
Uso: python a6_8_registro.py <registro_in.xlsx> <registro_out.xlsx>  (base: GitHub b61b53b)"""
import sys, copy, datetime, openpyxl
wb = openpyxl.load_workbook(sys.argv[1])
ws = wb['Decisioni']
ultima = max(r for r in range(2, ws.max_row + 1) if ws.cell(r, 1).value)
assert ws.cell(ultima, 1).value == 'D-139', ws.cell(ultima, 1).value
n = ultima + 1
riga = ['D-140', datetime.datetime(2026, 11, 13), 'A6', 'Giuseppe', 'Orbita',
 "Ora del nodo discendente minima per le riprese diurne (B): LTDN mai prima delle 9:30 per tutta la vita operativa. Con la deriva di D-103 (−34 min in 2 anni) vuol dire iniezione non prima delle 10:04, cioè −26 min di tolleranza verso il presto rispetto alle 10:30. Verso il tardi il payload non pone limiti (Sole più alto); il limite alto lo fissa Giuliano (potenza, eclissi, nuvole)",
 "A: mai prima delle 9:56 (nessuna tolleranza verso il presto, iniezione ≥ 10:30); C: mai prima delle 9:15 (iniezione ≥ 9:49, −41 min; anche Aosta a nadir sotto SNR 20 per 28 giorni, minimo 15,8, ombre ~5 volte l'altezza)",
 "Caso peggiore 25 dicembre al confine nord (47,1° N): sul ramo discendente l'ora locale sull'Italia è più tarda dell'LTDN (+21 min a 38° N, +29 min a 47° N), un bersaglio a 45° verso ovest −16 min. SNR pancromatico su suolo scuro (A3, 4 passaggi, ombra RC): 10:30 → 23,9 a nadir; 9:56 → 21,8 / 20,5 a 45°; 9:30 → 19,5 / 17,7 (sotto 20 solo al confine nord a 45°, fino a 45 giorni d'inverno; Aosta a nadir mai). Ombre 3,9–4,3 volte l'altezza. Dà margine al lancio (R-11) pagando solo d'inverno nel nord; riserva: 6 passaggi invece di 4 (+22% di SNR, +50% di dati alla scheda)",
 "DR-59 (valore basso), MR-11 (tolleranza dell'ora del nodo), requisito di lancio, R-11 (offerta dei lanci), R-04 (campagna AI con SNR fino a ~18 e ombre fino a 4 volte), DR-13 (se servono 6 passaggi)",
 'DR-59, MR-11, LR-01', 'R-11, R-04', 'Proposta', None,
 'Chat del 13/11/2026 (A6.8); a6_rischi/a6_8_ora_nodo.py, a6_8_risultati.txt, A6.8_ora_nodo_DR-59.md',
 "Proposta: fissa il valore basso di DR-59 (requisito di Giuliano) e la tolleranza di lancio. Stima di primo ordine (rumore di fotoni, cielo sereno, atmosfera τ 0,223 sul percorso del Sole); nessun requisito di SNR diurno: soglia di giudizio da confermare con la campagna AI di R-04"]
for c, v in enumerate(riga, 1):
    cell = ws.cell(n, c); src = ws.cell(ultima, c)
    cell.value = v
    if src.has_style: cell._style = copy.copy(src._style)
ws.row_dimensions[n].height = ws.row_dimensions[ultima].height
def nota(foglio, id_, col, testo, stato=None, valore=None):
    for r in wb[foglio].iter_rows(min_row=2):
        if r[0].value == id_:
            r[col].value = (r[col].value + ' | ' if r[col].value else '') + '13/11/2026 Giuseppe: ' + testo
            if stato: r[5].value = stato
            if valore: r[3].value = valore
            return
    raise KeyError(id_)
nota('Requisiti', 'DR-59', 8, "D-140 (Proposta): valore basso 9:30 (lato payload); limite alto da Giuliano. Valore precedente: Tolleranza TBD (A6); con 96,8° GMAT dà 10:30 → 9:56 in 2 anni",
     stato='TBC', valore="LTDN ≥ 9:30 per tutta la vita (D-140, Proposta), quindi iniezione ≥ 10:04 con la deriva di D-103 (−34 min in 2 anni); limite alto TBD (Giuliano)")
nota('Rischi', 'R-11', 12, "D-140 (Proposta): tolleranza dell'ora del nodo all'iniezione −26 min verso il presto (≥ 10:04) lato payload; manca il limite alto di Giuliano")
nota('Rischi', 'R-04', 12, "D-140: con LTDN fino a 9:30 la campagna AI deve includere scene invernali con SNR ~18 e ombre fino a ~4 volte l'altezza")
wb.save(sys.argv[2]); print('ok, riga', n)
