"""Tempo di contatto con Fucino che resta dopo l'ultima ripresa di un passaggio sull'Italia (per DR-48 di Giuseppe)."""
import re,datetime as dt,statistics as st
from pathlib import Path
D=str(Path(__file__).resolve().parents[2]/'PULSE_GMAT'/'Output_PULSE')+'/'
fmt='%d %b %Y %H:%M:%S.%f'
def parse(f):
    ev={};obs=None
    for L in open(f):
        m=re.match(r'Observer:\s*(\w+)\s*$',L.strip())
        if m: obs=m.group(1); ev[obs]=[]; continue
        p=re.match(r'(\d\d \w{3} \d{4} [\d:.]+)\s+(\d\d \w{3} \d{4} [\d:.]+)',L.strip())
        if p and obs: ev[obs].append((dt.datetime.strptime(p.group(1),fmt),dt.datetime.strptime(p.group(2),fmt)))
    return ev
R=4.305e6
for ang in ('30','45'):
  for fase,cond in (('notte',lambda t:t.hour>=19),('giorno',lambda t:t.hour<19)):
    res=[];miss=0
    for s in ('PULSE','PULSE2','PULSE3','PULSE4'):
        acc=parse(D+f'{s}_accessi_{ang}deg.txt'); fu=parse(D+f'{s}_contatti_stazioni.txt')['Fucino']
        ev=sorted(x for v in acc.values() for x in v if cond(x[0]))
        passi=[]
        for a,b in ev:
            if passi and (a-passi[-1][1]).total_seconds()<900: passi[-1]=(passi[-1][0],max(b,passi[-1][1]))
            else: passi.append((a,b))
        for a,b in passi:
            c=[f for f in fu if f[0]<=b+dt.timedelta(minutes=10) and f[1]>=a]
            if not c: miss+=1; continue
            res.append((c[0][1]-b).total_seconds())
    pos=[x for x in res if x>0]
    print(f'{ang}° {fase}: {len(res)+miss} passaggi; Fucino in vista dopo l\'ultima ripresa nel {100*len(pos)/(len(res)+miss):.0f}% dei casi; '
          f'residuo min {min(pos):.0f} s, mediana {st.median(pos):.0f} s, max {max(pos):.0f} s; '
          f'con 60 s per l\'AI e 10 s di aggancio restano in mediana {max(0,(st.median(pos)-70))*R/8/1e6:.0f} MB '
          f'(minimo {max(0,min(pos)-70)*R/8/1e6:.0f} MB)')
