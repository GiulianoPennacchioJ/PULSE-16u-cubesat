# A6.3: TRL delle tecnologie critiche di Giuseppe (approvato 04/11/2026)
import openpyxl, sys
p=sys.argv[1]; wb=openpyxl.load_workbook(p)
TRL={'R-01':('3','telescopio RC: progetto nostro verificato con tracciatore proprio'),
'R-02':('4','sensore notturno GSENSE400BSI: famiglia provata a protoni, modello esatto no'),
'R-03':('3','catena di conferma dei blackout: metodo analizzato, mai provato'),
'R-04':('3','algoritmi AI per i danni: studi solo a terra su xBD'),
'R-09':('8','scheda: FPGA classe Xiphos Q8 e chip AI classe Ubotica con voli alle spalle'),
'R-17':('4','GSENSE400BSI, vedi R-02'),
'R-36':('3','catena di conferma dei blackout, vedi R-03'),
'R-43':('4 (TBC)','coperchio richiudibile: nessun prodotto a catalogo per CubeSat trovato'),
'R-47':('8','chip AI classe Ubotica: Φ-sat-1, Φ-sat-2, CogniSAT-6'),
'R-48':('8','chip AI classe Ubotica: Φ-sat-1, Φ-sat-2, CogniSAT-6'),
'R-49':('3','telescopio RC, vedi R-01'),
'R-52':('4','IMX342 e GSENSE400BSI: nessuna prova di radiazione sul modello esatto')}
ws=wb['Rischi']
for row in ws.iter_rows(min_row=2):
    if row[0].value in TRL:
        v,why=TRL[row[0].value]; row[8].value=v
        row[12].value=(row[12].value or '')+' | 04/11/2026 (A6.3): TRL '+v+', '+why+' (a6_rischi/A6.3_TRL_tecnologie.md)'
wb.save(p); print('ok',len(TRL))
