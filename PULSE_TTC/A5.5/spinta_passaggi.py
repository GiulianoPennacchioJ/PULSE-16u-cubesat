import re,datetime as dt,statistics as st
from pathlib import Path
D=str(Path(__file__).resolve().parents[2]/'PULSE_GMAT'/'Output_PULSE')+'/'
fmt='%d %b %Y %H:%M:%S.%f'
def parse(f):
    ev=[]
    for L in open(f):
        p=re.match(r'(\d\d \w{3} \d{4} [\d:.]+)\s+(\d\d \w{3} \d{4} [\d:.]+)',L.strip())
        if p: ev.append((dt.datetime.strptime(p.group(1),fmt),dt.datetime.strptime(p.group(2),fmt)))
    return ev
sats=['PULSE','PULSE2','PULSE3','PULSE4']
T0=dt.datetime(2026,1,1,13);T1=dt.datetime(2026,1,31,13);giorni=(T1-T0).total_seconds()/86400
P=95.6  # periodo orbitale min circa
print('Passaggi sull\'Italia (accessi a 45° ad almeno uno dei 5 bersagli, raggruppati entro 15 min):')
res={}
for s in sats:
    acc=sorted(parse(D+f'{s}_accessi_45deg.txt'))
    passi=[]
    for a,b in acc:
        if passi and (a-passi[-1][1]).total_seconds()<900: passi[-1]=(passi[-1][0],max(b,passi[-1][1]))
        else: passi.append((a,b))
    passi=[p for p in passi if T0<=p[0]<=T1]
    res[s]=passi
n=[len(p)/giorni for p in res.values()]
print(f'  {st.mean(n):.2f} passaggi/giorno per satellite (giorno + notte); durata mediana {st.median((b-a).total_seconds() for p in res.values() for a,b in p):.0f} s')
print('\nTempo libero per la spinta se si vieta di spingere da N minuti prima del passaggio a 5 min dopo:')
for N in (0,15,30,45,60,90):
    free=[]
    for s,passi in res.items():
        blk=[(a-dt.timedelta(minutes=N),b+dt.timedelta(minutes=5)) for a,b in passi]
        # unione
        blk.sort(); u=[]
        for a,b in blk:
            if u and a<=u[-1][1]: u[-1]=(u[-1][0],max(u[-1][1],b))
            else: u.append((a,b))
        busy=sum((min(b,T1)-max(a,T0)).total_seconds() for a,b in u if b>T0 and a<T1)
        free.append(24*(1-busy/((T1-T0).total_seconds())))
    print(f'  N = {N:2d} min: {min(free):5.1f} h/giorno liberi (servono 4,2 h con Sole medio, 7,8 h con Sole alto)')
# Massimo tratto continuo libero tra passaggi
gaps=[]
for s,passi in res.items():
    for i in range(len(passi)-1): gaps.append((passi[i+1][0]-passi[i][1]).total_seconds()/3600)
print(f'\nIntervallo tra due passaggi sull\'Italia: min {min(gaps):.1f} h, mediana {st.median(gaps):.1f} h, max {max(gaps):.1f} h')
