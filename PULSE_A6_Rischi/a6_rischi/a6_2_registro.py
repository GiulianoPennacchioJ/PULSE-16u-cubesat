# A6.2: rivalutazione dei rischi con le regole di D-131 (approvata da Giuseppe il 04/11/2026)
import openpyxl, sys
p=sys.argv[1]; wb=openpyxl.load_workbook(p)
T="04/11/2026 (A6.2, D-131): "
G="Giuseppe"; E_="Entrambi"
# ID: (P, I, Stato, TRL, motivo)  -- None = invariato
R={
'R-01':('Bassa','Alta','In mitigazione','A6.3','telescopio RC già posizionato nel layout L1b (D-088, D-118, D-125); si chiude a fine A5.7'),
'R-02':('Bassa','Alta','In mitigazione','A6.3','SNR ≥ 10 con riserva 3×3 (A3); i resti stanno in R-19, R-20, R-50'),
'R-03':('Media','Alta','In mitigazione','n.a.','metodo A4 completo ma non ancora provato su casi reali'),
'R-04':('Media','Alta','Aperto','A6.3','nessuna prova su dati ancora'),
'R-09':('Bassa','Media','In mitigazione','A6.3','accensione solo intorno alle riprese; calore della scheda nell\'interno (D-130)'),
'R-16':('Media','Bassa','In mitigazione','n.a.','fondo lunare misurato e tolto (D-063); al massimo ~2 notti al mese sopra 2,5 nW'),
'R-17':('Media','Media','Aperto','A6.3','seconda fonte Teledyne Emerald (D-094): non si resta senza sensore, si perde un po\' di SNR'),
'R-18':(None,None,None,'n.a.',None),
'R-19':('Media','Media','Aperto','n.a.','si verifica solo con immagini reali (Fase B o commissioning)'),
'R-20':('Media','Media','Aperto','n.a.','riserva 3×3 del 23% sopra la soglia; analisi di luce parassita in Fase B'),
'R-22':('Bassa','Media','Chiuso','n.a.','chiuso: IMX342 fino a ~70 fps (D-093) e con il rallentamento (D-096) ne servono ~10'),
'R-24':('Bassa','Media','In mitigazione','n.a.','telescopio isolato, +1–2 K in 30 min (D-099); interno 18–25 °C nel caso caldo (D-128)'),
'R-30':('Media','Media','Aperto','n.a.','fenomeno certo; il riferimento alla stessa ora lo copre solo in parte'),
'R-31':(None,None,None,'n.a.',None),
'R-32':('Media','Media','Aperto','n.a.','pesa nei primi mesi, finché l\'archivio PULSE non cresce'),
'R-33':('Media','Bassa','Aperto','n.a.','finanziamento dei prodotti incerto; le mappe già scaricate restano valide; verifica spostata in Fase B'),
'R-34':('Media','Alta','Aperto','n.a.','nebbia frequente in Pianura Padana d\'inverno; un falso blackout alla Protezione Civile pesa'),
'R-35':('Media','Bassa','Aperto','n.a.','con incertezza alta l\'allarme diventa "non confermabile", non falso'),
'R-36':('Media','Alta','Aperto','n.a.','soglia tarata su ipotesi; serve la taratura su blackout reali'),
'R-41':(None,None,None,'n.a.',None),
'R-42':(None,None,None,'n.a.',None),
'R-43':(None,None,None,'A6.3',None),
'R-47':(None,None,None,'A6.3',None),
'R-48':('Media','Media','Aperto','A6.3','in 2 anni qualche inversione di bit è quasi certa; il riavvio automatico limita il danno'),
'R-49':('Bassa','Media','In mitigazione','A6.3','aste in Invar (D-098); resta la deriva con la temperatura (±11 K)'),
'R-50':(None,None,None,'n.a.',None),
'R-51':(None,None,None,'n.a.','invariato, da rivedere con D-130 (scheda sul lato +Y senza radiatore proprio)'),
'R-52':(None,None,None,'A6.3',None),
'R-55':('Bassa','Media','In mitigazione','n.a.','riscaldatori di sopravvivenza (D-107)'),
'R-57':(None,None,None,'n.a.','si chiude con il documento d\'interfaccia di T4i'),
'R-58':('Bassa','Media','In mitigazione','n.a.','routine d\'estate 1,1 W contro il tetto di 2,8 W (DR-68, D-128)'),
# Entrambi: proposta di Giuseppe, da confermare con Giuliano
'R-05':(None,None,None,'n.a.',None),
'R-07':('Bassa','Media','In mitigazione','n.a.','A5.6: stato di carica ≥ 79,6%; resta il Sole alto (R-56)'),
'R-21':('Bassa','Media','In mitigazione','n.a.','modello geometrico (D-056), giroscopio ~1 µrad contro 5,2 di soglia'),
'R-23':('Media','Alta','Aperto','n.a.','nessuna analisi del getto ancora; serve in Fase B'),
'R-26':('Bassa','Alta','In mitigazione','n.a.','layout L1b con ugello sul baricentro e ±5,5 mm (D-124, D-125)'),
'R-29':(None,None,None,'n.a.',None),
'R-37':('Media','Bassa','Aperto','n.a.','~11 scene a notte con priorità a città e zone a rischio (D-083); VIIRS come base'),
'R-38':(None,None,None,'n.a.',None),
'R-39':('Bassa','Bassa','In mitigazione','n.a.','striscia libera nel layout; si può chiudere a fine A5.7'),
'R-44':(None,None,None,'n.a.',None),
'R-53':(None,None,None,'n.a.',None),
'R-54':('Media','Bassa','In mitigazione','n.a.','la correlazione tra bande corregge le scene con contorni (D-101)'),
}
ws=wb['Rischi']; n=0
for row in ws.iter_rows(min_row=2):
    rid=row[0].value
    if rid not in R: continue
    P,I,S,TRL,why=R[rid]; who=row[9].value
    if P: row[3].value=P
    if I: row[4].value=I
    if S: row[10].value=S
    if TRL: row[8].value=TRL
    if rid=='R-33': row[7].value='Fase B'
    if why:
        tag=T+('proposta da confermare con Giuliano, ' if who==E_ else '')
        old=row[12].value or ''
        row[12].value=(old+' | ' if old else '')+tag+why
    n+=1
# D-038 superata
ws=wb['Decisioni']
for row in ws.iter_rows(min_row=2):
    if row[0].value=='D-038':
        row[11].value='Superata'; row[12].value='D-110, D-113'
        row[14].value=(row[14].value or '')+' | 04/11/2026 (A6.2): chiusa da D-110 (termico) e D-113 (struttura, computer di bordo, cablaggi), entrambe approvate'
wb.save(p); print('rischi aggiornati',n)
