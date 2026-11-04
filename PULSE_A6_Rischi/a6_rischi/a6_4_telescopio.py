# A6.4: D-132 strategia TRL del telescopio (scelta di Giuseppe 04/11/2026)
import openpyxl, datetime, sys
from copy import copy
p=sys.argv[1]; wb=openpyxl.load_workbook(p); ws=wb['Decisioni']
assert not any(r[0]=='D-132' for r in ws.iter_rows(min_row=2,values_only=True))
src=ws.max_row; r=src+1
row=['D-132',datetime.datetime(2026,11,4),'A6','Giuseppe','Payload',
"Strategia per portare il telescopio RC (D-088, TRL 3 oggi) a TRL 5–6 alla PDR (A): progetto nostro rifatto con programma ottico professionale in Fase B; specchi, lenti e montaggio affidati a una ditta ottica; modello di prova (specchi Zerodur + aste Invar + attacchi) provato in termo-vuoto e vibrazione in Fase B. Massa e volume restano quelli di A5 (~2,4 kg con sensori, paraluce e coperchio; colonna 14 × 14 cm)",
"B: telescopio a catalogo classe Simera MultiScape200 (TRL 9, 12,1 kg, 216 × 216 × 304 mm: massa con margini da ~27 a ~39 kg, oltre i 36 kg del deployer); C: progetto nostro senza modello di prova prima della PDR (TRL 3–4 alla PDR, deroga scritta)",
"Unica opzione che tiene massa e volume di A5 e arriva a TRL 5–6 entro la PDR; il catalogo non entra nel limite di massa",
"Piano di Fase B (costo e tempi del modello di prova), budget di massa invariato",
"DR-03, DR-53, DR-57","R-01, R-49, R-50",'Approvata',None,
"Chat del 04/11/2026 (A6.4); a6_rischi/A6.3_TRL_tecnologie.md, A6.4_mappa_rischi_piani.md",
"Riguarda solo il payload. Controllo di coerenza: MultiScape200 scalato col cubo dell'apertura (200 mm dal nome, TBC) ≈ 2,6 kg contro 2,4 kg nostri (M-11…M-14)"]
for c,v in enumerate(row,1):
    cell=ws.cell(r,c,v); s=ws.cell(src,c)
    cell.font=copy(s.font); cell.fill=copy(s.fill); cell.border=copy(s.border); cell.alignment=copy(s.alignment); cell.number_format=s.number_format
for x in wb['Rischi'].iter_rows(min_row=2):
    if x[0].value in ('R-01','R-49'):
        x[12].value=(x[12].value or '')+' | 04/11/2026 (D-132): modello di prova del telescopio in Fase B (termo-vuoto e vibrazione) per arrivare a TRL 5–6 alla PDR'
wb.save(p); print('ok',r)
