import ephem, math as m, datetime as dt
import numpy as np
M0=7.0  # nW/cm2/sr: luna piena allo zenit, suolo 0,15, senza atmosfera (A3)
def mag(a): return 0.026*abs(a)+4e-9*a**4   # Allen, relativo alla piena
res={}
for lat,lmst in [(36,22+10/60),(42,22+5/60),(47,22+1/60)]:
    lon=12.5
    obs=ephem.Observer(); obs.lat=str(lat); obs.lon=str(lon); obs.pressure=0
    vals=[];fr=[]
    d0=dt.datetime(2027,1,1)
    for k in range(730):
        t=d0+dt.timedelta(days=k)+dt.timedelta(hours=lmst-lon/15)
        obs.date=t
        mo=ephem.Moon(obs); su=ephem.Sun(obs)
        alt=m.degrees(mo.alt)
        # phase angle from elongation
        elong=m.degrees(ephem.separation(mo,su))
        alpha=180-elong
        if alt<=0: M=0.0
        else:
            am=1/ (m.sin(m.radians(alt))+0.50572*(alt+6.07995)**-1.6364)
            M=M0*10**(-0.4*mag(alpha))*m.sin(m.radians(alt))*0.8**am
        vals.append(M); fr.append(mo.phase)
    v=np.array(vals)
    res[lat]=v
    print(f"lat {lat}: notti con luna sopra orizzonte {np.mean(v>0)*100:.0f}%  M>0.5 {np.mean(v>0.5)*100:.0f}%  M>1 {np.mean(v>1)*100:.0f}%  M>2.5 {np.mean(v>2.5)*100:.0f}%  M>4 {np.mean(v>4)*100:.0f}%  max {v.max():.2f}  p90 {np.percentile(v,90):.2f}")
    print('   notti/mese M>1:',np.mean(v>1)*30.4, ' M>2.5:',np.mean(v>2.5)*30.4)
# per stagione a 42
v=res[42]; days=[dt.date(2027,1,1)+dt.timedelta(days=k) for k in range(730)]
for name,months in [('inverno',(12,1,2)),('primavera',(3,4,5)),('estate',(6,7,8)),('autunno',(9,10,11))]:
    sel=np.array([d.month in months for d in days])
    print(name,'max',v[sel].max().round(2),'M>2.5 %',(np.mean(v[sel]>2.5)*100).round(0))
np.save('/tmp/claude-0/a4/M42.npy',v)
