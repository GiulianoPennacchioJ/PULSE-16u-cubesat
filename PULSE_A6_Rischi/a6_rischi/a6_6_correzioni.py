# A6.6: correzioni ai requisiti (approvate da Giuseppe 04/11/2026)
import openpyxl, sys
p=sys.argv[1]; wb=openpyxl.load_workbook(p); Q=wb['Requisiti']
T=' | 04/11/2026 (A6.6): '
C={ # id: (nuovo valore o None, nuovo stato o None, nota)
'DR-12':('≥ ~10 immagini/s con rallentamento ×2 (D-096); il sensore IMX342 arriva a ~70 (D-093)','Approvato','valore riscritto: con il rallentamento di D-096 bastano ~10 immagini/s invece di ~20'),
'DR-46':('Spinta vietata da N = 30 min (TBC, D-099) prima di una ripresa pianificata',None,'N dato dal termico del payload (D-099: +1–2 K sul telescopio in 30 min); proposta, da confermare con Giuliano'),
'MR-09':(None,'Approvato','formato vettore + ritaglio definito da DR-35 e DR-42 (A4, A5)'),
'DR-51':(None,'Approvato','modo degradato deciso con D-085 (approvata); la verifica resta il test di guasto in Fase C'),
'DR-52':(None,'Approvato','valori chiusi da D-086 (approvata); verifica in Fase B/C'),
'DR-53':(None,'Approvato','MTF calcolato 0,13–0,17 sopra 0,12 (A5.P4, D-088); misura in laboratorio in Fase C'),
'DR-55':(None,'Approvato','verificato in A5.P7 e con D-130 (radiatore ~125 cm²); prova in termo-vuoto in Fase C'),
'DR-57':(None,'Approvato','D-098 e D-099 (approvate): ±11 K, +1–2 K in 30 min dopo la spinta'),
'DR-64':(None,'Approvato','15–25 °C approvato con D-116; verificato nel modello A5.8 (D-128)'),
'DR-68':(None,'Approvato','tetto approvato con D-116; routine 1,1 W contro 2,8 W (D-128)'),
'DR-70':(None,'Approvato','600 cm² approvato con D-122, posizione D-129'),
'MR-06':(None,None,'soglia in Fase B: arriverà da DR-73 (precisione degli allarmi)'),
'MR-08':(None,None,'soglia in Fase B (con la campagna di prova di D-133)'),
'MR-10':(None,None,'soglia in Fase B (errore di ortorettifica, legato a DR-16 e DR-26)'),
}
for row in Q.iter_rows(min_row=2):
    k=row[0].value
    if k=='DR-13':
        row[3].value=row[3].value.replace('Ingresso ~7,5 Gbit/s di giorno (628 Mpx/s)','Ingresso ~3,7 Gbit/s di giorno (314 Mpx/s, ~10 immagini/s con rallentamento, D-096/D-101)')
        row[8].value=(row[8].value or '')+T+'ingresso diurno ricalcolato a ~10 immagini/s (era 7,5 Gbit/s a 20 immagini/s); resta TBC fino alla prova sulla scheda'
        assert '3,7' in row[3].value
    if k in C:
        v,s,n=C[k]
        if v: row[3].value=v
        if s: row[5].value=s
        row[8].value=(row[8].value or '')+T+n
wb.save(p); print('ok')
