import re,glob,datetime as dt,statistics as st
from pathlib import Path
D=str(Path(__file__).resolve().parents[2]/'PULSE_GMAT'/'Output_PULSE')+'/'
fmt='%d %b %Y %H:%M:%S.%f'
def parse(f,suffix=''):
    ev={};obs=None
    for L in open(f):
        m=re.match(r'Observer:\s*(\w+)\s*$',L.strip())
        if m: obs=m.group(1); ev[obs]=[]; continue
        p=re.match(r'(\d\d \w{3} \d{4} [\d:.]+)\s+(\d\d \w{3} \d{4} [\d:.]+)',L.strip())
        if p and obs: ev[obs].append((dt.datetime.strptime(p.group(1),fmt),dt.datetime.strptime(p.group(2),fmt)))
    return ev
sats=['PULSE','PULSE2','PULSE3','PULSE4']
acc={s:{**parse(D+f'{s}_accessi_30deg.txt'),**parse(D+f'{s}_accessi_45deg.txt')} for s in sats}
con={s:parse(D+f'{s}_contatti_stazioni.txt') for s in sats}
print('stazioni nei file:',list(con['PULSE'].keys()))
night=lambda t: 19<=t.hour<=23
# A) scarico nello stesso passaggio da Fucino
res=[];wait_main=[]
for s in sats:
  for o,ev in acc[s].items():
    if not o.endswith('30'): continue
    for a,b in ev:
      if not night(a): continue
      fu=[c for c in con[s]['Fucino'] if c[1]>b and c[0]<b+dt.timedelta(minutes=15)]
      res.append((fu[0][1]-b).total_seconds() if fu else None)
      nxt=min(c[0] for k in ('Svalbard','Fairbanks') for c in con[s][k] if c[0]>b)
      wait_main.append((nxt-b).total_seconds()/3600)
ok=[x for x in res if x is not None]
print(f'\nA) accessi notturni 30° (4 sat): {len(res)}; con Fucino ancora visibile dopo la ripresa: {len(ok)} ({100*len(ok)/len(res):.0f}%)')
if ok: print(f'   tempo di contatto Fucino rimasto dopo la fine ripresa: min {min(ok):.0f} s, mediana {st.median(ok):.0f} s, max {max(ok):.0f} s')
print(f'   attesa fino al primo contatto Svalbard/Fairbanks: mediana {st.median(wait_main):.1f} h, max {max(wait_main):.1f} h')
# B) seconda ripresa col satellite successivo (stesso bersaglio, cono 45°, entro 40 min)
tot=0;two=0;gaps=[];cmd=[]
for i,s in enumerate(sats):
  for o,ev in acc[s].items():
    if not o.endswith('30'): continue
    base=o[:-2]
    for a,b in ev:
      if not night(a): continue
      tot+=1
      cand=[(s2,x) for s2 in sats if s2!=s for x in acc[s2][base+'45'] if dt.timedelta(minutes=5)<x[0]-a<dt.timedelta(minutes=40)]
      if cand:
        two+=1; s2,(a2,b2)=min(cand,key=lambda z:z[1][0]); gaps.append((a2-a).total_seconds()/60)
        # contatto Fucino del secondo satellite che inizia prima della sua ripresa
        f2=[c for c in con[s2]['Fucino'] if c[0]<a2 and c[1]>a2-dt.timedelta(minutes=15)]
        fu1=[c for c in con[s]['Fucino'] if c[1]>b and c[0]<b+dt.timedelta(minutes=15)]
        if f2 and fu1:
          cmd.append((a2-max(b,fu1[0][0])).total_seconds()/60)  # minuti tra dato a terra (inizio possibile) e ripresa sat2
print(f'\nB) accessi notturni a 30° con seconda ripresa possibile (altro satellite, ≤45°, entro 40 min): {two}/{tot} = {100*two/tot:.0f}%')
if gaps: print(f'   intervallo tra le due riprese: min {min(gaps):.1f} max {max(gaps):.1f} min')
if cmd: print(f'   casi con Fucino visibile a entrambi: {len(cmd)}; tempo disponibile tra dato a terra e seconda ripresa: min {min(cmd):.1f}, mediana {st.median(cmd):.1f}, max {max(cmd):.1f} min')
# B2) stesso conto partendo da accessi 45° (dubbi anche su prime riprese degradate)
tot=0;two=0
for s in sats:
  for o,ev in acc[s].items():
    if not o.endswith('45'): continue
    for a,b in ev:
      if not night(a): continue
      tot+=1
      if any(dt.timedelta(minutes=5)<x[0]-a<dt.timedelta(minutes=40) for s2 in sats if s2!=s for x in acc[s2][o]): two+=1
print(f'   partendo da accessi a 45°: {two}/{tot} = {100*two/tot:.0f}%')
print('\nC) dettaglio attesa dopo ripresa notturna 30° (minuti) fino a inizio contatto, per stazione:')
for k in ('Fucino','Svalbard','Fairbanks'):
    w=[]
    for s in sats:
      for o,ev in acc[s].items():
        if not o.endswith('30'): continue
        for a,b in ev:
          if not night(a): continue
          n=[c for c in con[s][k] if c[1]>b]
          w.append(max(0,(n[0][0]-b).total_seconds()/60) if n else None)
    w=[x for x in w if x is not None]
    print(f'  {k:9s}: min {min(w):.1f}  mediana {st.median(w):.1f}  max {max(w):.1f}')
# durata contatti Svalbard dopo il passaggio notturno
d=[]
for s in sats:
  for o,ev in acc[s].items():
    if not o.endswith('30'): continue
    for a,b in ev:
      if not night(a): continue
      n=[c for c in con[s]['Svalbard'] if c[1]>b][0]; d.append((n[1]-n[0]).total_seconds())
print(f'  durata del contatto Svalbard successivo: min {min(d):.0f} s mediana {st.median(d):.0f} s max {max(d):.0f} s')
# buco massimo per satellite e dove cade
for s in sats[:1]:
    allc=sorted(c for k in ('Svalbard','Fairbanks') for c in con[s][k])
    gaps=[(allc[i+1][0]-allc[i][1],allc[i][1]) for i in range(len(allc)-1)]
    g=max(gaps); print(f'  buco max {s} (Svalbard+Fairbanks): {g[0].total_seconds()/3600:.1f} h, inizia {g[1]} UTC')
