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
sats=['PULSE','PULSE2','PULSE3','PULSE4']
for fase,cond in (('notte',lambda t:t.hour>=19),('giorno',lambda t:t.hour<19)):
    ov=0;n=0;gap={'Svalbard':[],'Fairbanks':[],'Fucino':[]}
    for s in sats:
        acc=parse(D+f'{s}_accessi_45deg.txt'); con=parse(D+f'{s}_contatti_stazioni.txt')
        for o,ev in acc.items():
            for a,b in ev:
                if not cond(a): continue
                n+=1
                if any(c[0]<b and c[1]>a for c in con['Fucino']): ov+=1
                for k in gap:
                    nx=[c for c in con[k] if c[0]>=b]
                    if nx: gap[k].append((nx[0][0]-b).total_seconds()/60)
    print(f'{fase}: {n} accessi a 45°; Fucino in vista DURANTE la ripresa: {ov} ({100*ov/n:.0f}%)')
    for k,g in gap.items(): print(f'   prossimo contatto {k:9s} dopo la ripresa: min {min(g):5.1f}  mediana {st.median(g):6.1f} min')
# frazione del tempo di contatto che cade su contatti che iniziano entro 15 min da una ripresa (potenziale conflitto con assetto di ripresa)
