import openpyxl, datetime, sys
from copy import copy
p=sys.argv[1]
wb=openpyxl.load_workbook(p)
ws=wb['Decisioni']
src=ws.max_row; r=src+1
row=['D-131',datetime.datetime(2026,10,31),'A6','Giuseppe','Gestione',
 "Regole comuni per valutare i rischi (A): scala a 3 livelli già nel registro, con definizioni scritte. Probabilità (oggi, con le mitigazioni già decise, su 2 anni e 4 satelliti): Bassa < 10%, Media 10–50%, Alta > 50% (soglie convenzionali). Impatto: Bassa = prestazione ridotta ma requisiti rispettati; Media = un DR non rispettato o un pezzo da riprogettare; Alta = un MR non rispettato, perdita di un satellite o del payload, o satellite da riprogettare. Criticità ≥ 6 (rosso): piano di riduzione con responsabile e scadenza, da portare a ≤ 4 alla PDR oppure accettare per iscritto; 3–4 (giallo): mitigazione scritta, ricontrollo a ogni review; 1–2 (verde): accettato. TRL su scala ISO 16290 (ECSS): numero 1–9 con fonte per i rischi tecnologici, \"n.a.\" per gli altri; un pezzo già volato usato in condizioni nuove perde livelli; obiettivo TRL ≥ 6 alla PDR per ogni tecnologia critica.",
 "B: scala 5×5 della norma ECSS-M-ST-80C (da rifare menu, formula e colori e rivalutare tutti i rischi); C: 3×3 ora e 5×5 dalla Fase B",
 "In Fase A le stime sono di primo ordine: 5 livelli darebbero una precisione che i dati non hanno; il file resta com'è (menu, formula, colori). Nel report A6 si indica la corrispondenza con i 5 livelli della norma",
 "Foglio Rischi (colonne Probabilità, Impatto, TRL) per entrambi; valutazione dei rischi di Giuliano",
 None,"Tutti (R-01…R-61)",'Proposta',None,
 "Chat del 31/10/2026 (A6.1); a6_rischi/A6.1_regole_comuni.md",
 "Proposta per Giuliano: le stesse regole valgono per i suoi rischi. Definizioni copiate anche nel foglio Leggimi"]
for c,v in enumerate(row,1):
    cell=ws.cell(r,c,v); s=ws.cell(src,c)
    cell.font=copy(s.font); cell.fill=copy(s.fill); cell.border=copy(s.border); cell.alignment=copy(s.alignment); cell.number_format=s.number_format
ws.row_dimensions[r].height=ws.row_dimensions[src].height
# Leggimi
L=wb['Leggimi']; base=L.max_row+2
lines=[("Scala dei rischi (D-131)",None),
("Probabilità","Oggi, con le mitigazioni già decise, su tutta la missione (2 anni, 4 satelliti). Bassa < 10% · Media 10–50% · Alta > 50%"),
("Impatto","Bassa: prestazione ridotta, requisiti rispettati · Media: un DR non rispettato o un pezzo da riprogettare · Alta: un MR non rispettato, perso un satellite o il payload, o satellite da riprogettare"),
("Criticità","≥ 6 rosso: piano con responsabile e scadenza, ≤ 4 alla PDR o accettato per iscritto · 3–4 giallo: mitigazione scritta · 1–2 verde: accettato"),
("TRL","Scala ISO 16290 (1–9) con fonte; \"n.a.\" se il rischio non è tecnologico; un pezzo già volato usato in condizioni nuove perde livelli; obiettivo ≥ 6 alla PDR")]
hdr=None
for i,(a,b) in enumerate(lines):
    ca=L.cell(base+i,1,a); 
    if b: L.cell(base+i,2,b)
# copy styles from the "Stati" header and a normal row
for i in range(len(lines)):
    for c in (1,2):
        s=L.cell(12 if i==0 else 13,c); d=L.cell(base+i,c)
        d.font=copy(s.font); d.fill=copy(s.fill); d.alignment=copy(s.alignment); d.border=copy(s.border)
wb.save(p); print('ok',r,base)
