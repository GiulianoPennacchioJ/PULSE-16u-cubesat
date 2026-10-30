import re,glob,datetime as dt,math,statistics as st,sys
from pathlib import Path
D=str(Path(__file__).resolve().parents[2]/'PULSE_GMAT'/'Output_PULSE')+'/'
lon={'Aosta':7.32,'Gemona':13.14,'Napoli':14.27,'Norcia':13.09,'Palermo':13.36}
lat={'Aosta':45.74,'Gemona':46.28,'Napoli':40.85,'Norcia':42.79,'Palermo':38.12}
fmt='%d %b %Y %H:%M:%S.%f'
def eot(d):  # equazione del tempo [min], formula NOAA
    g=2*math.pi/365*(d.timetuple().tm_yday-1+(d.hour-12)/24)
    return 229.18*(0.000075+0.001868*math.cos(g)-0.032077*math.sin(g)-0.014615*math.cos(2*g)-0.040849*math.sin(2*g))
rows=[]
for f in sorted(glob.glob(D+'PULSE*_accessi_*deg.txt')):
    sat=re.search(r'(PULSE\d?)_',f).group(1); ang=re.search(r'(\d+)deg',f).group(1)
    obs=None
    for L in open(f):
        m=re.match(r'Observer:\s*(\w+?)(30|45)\s*$',L.strip())
        if m: obs=m.group(1); continue
        p=re.match(r'(\d\d \w{3} \d{4} [\d:.]+)\s+(\d\d \w{3} \d{4} [\d:.]+)\s+([\d.]+)',L.strip())
        if p and obs:
            a=dt.datetime.strptime(p.group(1),fmt); b=dt.datetime.strptime(p.group(2),fmt)
            mid=a+(b-a)/2
            lmst=(mid.hour+mid.minute/60+mid.second/3600+lon[obs]/15)%24
            last=(lmst+eot(mid)/60)%24
            rows.append((sat,ang,obs,mid,lmst,last,float(p.group(3))))
def hm(h): return f'{int(h):02d}:{int(round((h%1)*60))%60:02d}' if round((h%1)*60)<60 else f'{int(h)+1:02d}:00'
night=[r for r in rows if r[4]>18]
day=[r for r in rows if r[4]<18]
print('accessi totali',len(rows),'notte',len(night),'giorno',len(day))
for ang in ('30','45'):
    n=[r for r in night if r[1]==ang]
    print(f'\n== Notte, cono {ang}°: {len(n)} accessi (4 sat, Gen 2026)')
    print(' ora solare media (centro accesso): min %s  max %s  mediana %s'%(hm(min(r[4] for r in n)),hm(max(r[4] for r in n)),hm(st.median(r[4] for r in n))))
    print(' ora solare vera:                   min %s  max %s'%(hm(min(r[5] for r in n)),hm(max(r[5] for r in n))))
    utc=[r[3].hour+r[3].minute/60 for r in n]
    print(' UTC: min %s max %s ; CET(+1) %s–%s ; CEST(+2) %s–%s'%(hm(min(utc)),hm(max(utc)),hm(min(utc)+1),hm(max(utc)+1),hm(min(utc)+2),hm(max(utc)+2)))
    for o in lon:
        x=[r[4] for r in n if r[2]==o]
        if x: print(f'   {o:8s} lat {lat[o]:5.2f}: LMST {hm(min(x))}–{hm(max(x))} (n={len(x)})')
d=[r for r in day if r[1]=='30']
print('\nGiorno 30°: LMST %s–%s'%(hm(min(r[4] for r in d)),hm(max(r[4] for r in d))))
