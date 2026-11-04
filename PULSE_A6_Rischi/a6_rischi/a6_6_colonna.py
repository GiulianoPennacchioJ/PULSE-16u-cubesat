# A6.6: colonna "Discende da" nel foglio Requisiti (D-134, scelta A di Giuseppe 04/11/2026)
import openpyxl, datetime, sys
from copy import copy
p=sys.argv[1]; wb=openpyxl.load_workbook(p); Q=wb['Requisiti']
col=Q.max_column+1; assert Q.cell(1,col-1).value=='Note', Q.cell(1,col-1).value
h=Q.cell(1,col,'Discende da'); s=Q.cell(1,col-1)
for a in ('font','fill','border','alignment'): setattr(h,a,copy(getattr(s,a)))
Q.column_dimensions[openpyxl.utils.get_column_letter(col)].width=18
PAR={'DR-01':'MR-03','DR-03':'MR-03','DR-09':'MR-04, MR-07, MR-08','DR-12':'MR-03','DR-13':'MR-03, MR-04',
'DR-31':'MR-07, MR-08','DR-32':'MR-07, MR-08','DR-33':'MR-07','DR-34':'MR-07','DR-38':'MR-03','DR-43':'MR-02',
'DR-51':'MR-02','DR-52':'MR-07, MR-10','DR-53':'MR-03','DR-54':'MR-12','DR-55':'MR-04','DR-57':'MR-03',
'DR-64':'MR-12','DR-68':'MR-11','DR-70':'MR-12','DR-73':'MR-06',
'DR-14':'MR-13','DR-16':'MR-10','DR-21':'MR-11','DR-26':'MR-03, MR-10','DR-35':'MR-07, MR-09','DR-36':'MR-07',
'DR-37':'MR-03, MR-12','DR-42':'MR-06, MR-09','DR-44':'MR-06','DR-45':'MR-02','DR-46':'MR-02','DR-48':'MR-02','DR-56':'MR-03'}
n=0
for row in Q.iter_rows(min_row=2):
    rid=row[0].value
    if not rid: continue
    c=Q.cell(row[0].row,col); src=Q.cell(row[0].row,col-1)
    for a in ('font','fill','border','alignment'): setattr(c,a,copy(getattr(src,a)))
    if rid.startswith(('MR','LR')): c.value='—'
    elif rid in PAR:
        c.value=PAR[rid]+(' (proposta, da confermare con Giuliano)' if row[7].value=='Entrambi' else ''); n+=1
# decisione D-134
D=wb['Decisioni']; assert not any(r[0]=='D-134' for r in D.iter_rows(min_row=2,values_only=True))
srcr=D.max_row; r=srcr+1
vals=['D-134',datetime.datetime(2026,11,4),'A6','Giuseppe','Gestione',
"Tracciabilità dei requisiti (A): nuova colonna \"Discende da\" in fondo al foglio Requisiti, con il requisito di missione (MR) da cui discende ogni DR; per MR e LR \"—\". La tabella a croci MR × DR per la PRR si ricava da questa colonna. Compilata per i DR di Giuseppe (21) e, come proposta, per i 13 \"Entrambi\"; i DR di Giuliano li collega lui",
"B: foglio nuovo \"Matrice\" a croci (ogni DR da scrivere in due posti); C: colonna Note (non filtrabile)",
"Un solo posto da aggiornare, nessuna copia che diverge; si filtra con un clic",
"Foglio Requisiti (colonna J aggiunta in fondo, le altre invariate); lavoro di Giuliano sui suoi DR",
None,None,'Proposta',None,"Chat del 04/11/2026 (A6.6); a6_rischi/A6.6_matrice_requisiti.md",
"Proposta per Giuliano: cambia la struttura del foglio Requisiti che usa anche lui"]
for i,v in enumerate(vals,1):
    cell=D.cell(r,i,v); s=D.cell(srcr,i)
    for a in ('font','fill','border','alignment','number_format'): setattr(cell,a,copy(getattr(s,a)))
wb.save(p); print('ok col',col,'DR collegati',n)
