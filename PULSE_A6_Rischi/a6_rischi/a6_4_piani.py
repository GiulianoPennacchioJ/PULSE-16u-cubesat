# A6.4: piani per i rischi rossi (D-133), deroga TRL della catena dei blackout, nuovo DR-73 (approvati da Giuseppe 04/11/2026)
import openpyxl, datetime, sys
from copy import copy
p=sys.argv[1]; wb=openpyxl.load_workbook(p)
def add(ws,vals):
    src=ws.max_row; r=src+1
    for c,v in enumerate(vals,1):
        cell=ws.cell(r,c,v); s=ws.cell(src,c)
        cell.font=copy(s.font); cell.fill=copy(s.fill); cell.border=copy(s.border); cell.alignment=copy(s.alignment); cell.number_format=s.number_format
    return r
D=wb['Decisioni']; Q=wb['Requisiti']; R=wb['Rischi']
assert not any(x[0] in('D-133','DR-73') for x in list(D.iter_rows(min_row=2,values_only=True))+list(Q.iter_rows(min_row=2,values_only=True)))
add(D,['D-133',datetime.datetime(2026,11,4),'A6','Giuseppe','AI / Dati',
"Piani di riduzione dei rischi rossi di Giuseppe (obiettivo ≤ 4 alla PDR, D-131). (1) Una sola campagna di prova della catena dei blackout su notti passate, a inizio Fase B: blackout reali con immagini VIIRS giornaliere (Black Marble) e nuvole Meteosat delle stesse notti; taratura della soglia del 70% sulle curve vere; nebbia invernale in Pianura Padana confrontata con i bollettini meteo degli aeroporti (Milano, Bologna, Verona); criterio di successo TBD (es. ≥ 90% di casi corretti). Se il prodotto nebbia non basta: \"non confermabile\" automatico in Pianura Padana da novembre a febbraio senza indizi chiari. (2) Campagna AI in Fase B: rete addestrata su xBD e valutata su disastri italiani portati a 1,5 m (es. Norcia 2016, Emilia-Romagna 2023), con requisito di precisione degli allarmi (DR-73) e livello di fiducia per ogni allarme. (3) Deroga: la catena dei blackout può arrivare alla PDR sotto TRL 6 (atteso 4–5), perché servono immagini notturne vere a 5 m che si avranno solo in volo; rete di sicurezza: etichetta \"non confermabile\" e conferma a terra (D-065)",
"Piani separati per R-03, R-34 e R-36; nessuna deroga (catena a TRL 6 prima della PDR, non raggiungibile senza dati di volo)",
"Una campagna sola copre tre rischi rossi con gli stessi dati; la deroga è dichiarata ora invece di emergere in review",
"Piano di Fase B (dati VIIRS, Meteosat, bollettini aeroportuali, immagini di disastri italiani), nuovo DR-73",
"MR-06, MR-07, MR-08, DR-73","R-03, R-04, R-34, R-36",'Approvata',None,
"Chat del 04/11/2026 (A6.4); a6_rischi/A6.4_mappa_rischi_piani.md",
"Riguarda solo la parte di Giuseppe. Il piano per R-23 (iodio, Entrambi) è proposto a Giuliano nella nota del rischio"])
add(Q,['DR-73','Derivato',
"La rete AI di bordo deve segnalare i danni diurni con una precisione degli allarmi (quota di allarmi che corrispondono a un danno vero) non inferiore alla soglia, e ogni allarme deve portare un livello di fiducia.",
"Precisione ≥ TBD% (da fissare in Fase B con la Protezione Civile), misurata su xBD e su disastri italiani a 1,5 m",
"Test AI su dataset (xBD + immagini di disastri italiani portate a 1,5 m), poi prova sul chip vero (Fase B)",
'TBD','D-133 (A6.4)','Giuseppe',
"Nato per ridurre R-04 (falsi allarmi). Discende da MR-06"])
P={'R-03':'Campagna di prova unica della catena dei blackout su notti passate (D-133, inizio Fase B)',
'R-36':'Taratura della soglia del 70% nella campagna di prova dei blackout (D-133)',
'R-34':'Nebbia invernale in Pianura Padana confrontata con i bollettini aeroportuali nella campagna di D-133; ripiego: "non confermabile" automatico in Pianura Padana da novembre a febbraio senza indizi chiari',
'R-04':'Campagna AI su xBD e disastri italiani a 1,5 m, requisito di precisione DR-73 (D-133)',
'R-23':'Proposta A6.4 (da confermare con Giuliano): analisi del getto con i dati T4i e dei voli REGULUS (Giuliano) e sensibilità degli specchi al deposito (Giuseppe) in Fase B; il coperchio è già chiuso in spinta (D-079)'}
for x in R.iter_rows(min_row=2):
    k=x[0].value
    if k in P:
        x[6].value=(x[6].value or '')+'; '+P[k]
        if k!='R-23': x[7].value='Fase B (D-133)'
        x[12].value=(x[12].value or '')+' | 04/11/2026 (A6.4): piano per portarlo a ≤ 4 alla PDR'+(' (D-133)' if k!='R-23' else ', proposta per Giuliano')
wb.save(p); print('ok')
