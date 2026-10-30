import re,datetime as dt,statistics as st
from pathlib import Path
D=str(Path(__file__).resolve().parents[2]/'PULSE_GMAT'/'Output_PULSE')+'/'
fmt='%d %b %Y %H:%M:%S.%f'
def parse(f):
    ev={};obs=None
    for L in open(f):
        m=re.match(r'Observer:\s*(\w+)\s*$',L.strip())
        if m: obs=m.group(1); ev[obs]=[]; continue
        p=re.match(r'(\d\d \w{3} \d{4} [\d:.]+)\s+(\d\d \w{3} \d{4} [\d:.]+)\s+([\d.]+)',L.strip())
        if p and obs: ev[obs].append((dt.datetime.strptime(p.group(1),fmt),dt.datetime.strptime(p.group(2),fmt),float(p.group(3))))
    return ev
sats=['PULSE','PULSE2','PULSE3','PULSE4']
allev=[]
for s in sats:
    for k,v in parse(D+f'{s}_contatti_stazioni.txt').items():
        for a,b,d in v: allev.append((s,k,a,b,d))
t0=min(e[2] for e in allev); t1=max(e[3] for e in allev); giorni=(t1-t0).total_seconds()/86400
print(f'periodo {t0:%d %b} – {t1:%d %b %Y}: {giorni:.1f} giorni')
print('\nPer satellite (media al giorno):')
for k in ('Svalbard','Fairbanks','Fucino'):
    e=[x for x in allev if x[1]==k]
    n=len(e)/4/giorni; tot=sum(x[4] for x in e)/4/giorni
    print(f'  {k:9s}: {n:4.1f} contatti/giorno, {tot/60:5.1f} min/giorno, durata mediana {st.median(x[4] for x in e):.0f} s (min {min(x[4] for x in e):.0f}, max {max(x[4] for x in e):.0f})')
e=[x for x in allev]; print(f'  TOTALE   : {len(e)/4/giorni:4.1f} contatti/giorno, {sum(x[4] for x in e)/4/giorni/60:5.1f} min/giorno')
# contatti utili >= 2 min (criterio EarthNext)
u=[x for x in allev if x[4]>=120]
print(f'  solo contatti ≥ 2 min: {len(u)/4/giorni:.1f}/giorno, {sum(x[4] for x in u)/4/giorni/60:.1f} min/giorno')
# minimo giornaliero per satellite
mins=[]
for s in sats:
    d={}
    for x in allev:
        if x[0]==s: d[x[2].date()]=d.get(x[2].date(),0)+x[4]
    full=[v for k,v in d.items() if t0.date()<k<t1.date()]
    mins.append(min(full))
print(f'  giorno peggiore (per satellite): {min(mins)/60:.1f} min')
# overlap stazioni: tempo totale costellazione per stazione (antenna unica)
print('\nCostellazione (4 satelliti) per stazione, min/giorno e sovrapposizioni:')
for k in ('Svalbard','Fairbanks','Fucino'):
    e=sorted((x[2],x[3]) for x in allev if x[1]==k)
    ov=sum(max(0,(min(e[i][1],e[j][1])-max(e[i][0],e[j][0])).total_seconds()) for i in range(len(e)) for j in range(i+1,min(i+5,len(e))))
    print(f'  {k:9s}: {sum((b-a).total_seconds() for a,b in e)/giorni/60:5.1f} min/giorno, sovrapposizioni {ov/giorni/60:.2f} min/giorno')
# esempio capacità
print('\nCapacità di scarico per satellite al giorno (tempo totale × velocità, efficienza 80% TBC):')
T=sum(x[4] for x in allev)/4/giorni
for nome,R in (('UHF 9,6 kbit/s',9.6e3),('S 1 Mbit/s',1e6),('S 2 Mbit/s',2e6),('X 50 Mbit/s',50e6),('X 150 Mbit/s',150e6)):
    print(f'  {nome:15s}: {T*R*0.8/8/1e6:8.1f} MB/giorno')
