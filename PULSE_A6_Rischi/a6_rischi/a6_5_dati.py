# A6.5: righe dati del payload nel budget (caso routine di A5.P1, p1_volumi.py)
import openpyxl, sys
p=sys.argv[1]; wb=openpyxl.load_workbook(p); ws=wb['Dati']
V={'D-01':(3.15,3,'Calcolo','A5.P1 / D-071',"Scena 1×1 compressa 2:1 senza perdita (grezza 6,3 MB). Routine 3 scene/notte; emergenza 4 (A5.P1)"),
'D-02':(1.6,0,None,None,"Binning 2×2: usato per i paesi quando serve (D-077); non nel caso routine"),
'D-03':(0.7,0,None,None,"Binning 3×3: riserva (D-077); non nel caso routine"),
'D-04':(31.4,1,'Calcolo','A5.P1 / D-071, D-072',"Scena 9,7 × 9,7 km pan + RGB-NIR, 12 bit, compressa 4:1 quasi senza perdita (grezza 125,4 MB). Routine 1 scena/giorno; primi 3 mesi e emergenza 4"),
'D-05':(0.48,4,'Calcolo','MR-09, DR-35, DR-42',"Media di 2 allarmi diurni (ritaglio 1 × 1 km senza perdita 0,67 MB + vettore 20 kB) e 2 notturni (ritaglio 2 × 2 km 0,26 MB + vettore). Emergenza: 40 diurni + fino a 96 notturni"),}
for row in ws.iter_rows(min_row=2):
    k=row[0].value
    if k in V:
        d,u,o,rf,n=V[k]; row[3].value=d; row[4].value=u
        if o: row[6].value=o
        if rf: row[7].value=rf
        row[8].value=n+' | 04/11/2026 (A6.5)'
wb.save(p); print('ok')
