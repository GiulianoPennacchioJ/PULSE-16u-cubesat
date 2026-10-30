"""Stima di primo ordine: passaggi diurni per satellite sull'Italia e scene possibili per passaggio.
Orbita circolare 302 km, i 96,8°, eliosincrona (nodo che segue il Sole), LTAN 22:30 -> passaggio diurno discendente ~10:30.
Italia approssimata con un poligono semplice; un punto è 'raggiungibile' se a <= 310 km dalla traccia (45° off-nadir, A1)."""
import numpy as np
Re=6378.137; h=302; a=Re+h; mu=398600.4418
n=np.sqrt(mu/a**3); i=np.radians(96.8); wE=7.2921159e-5
# poligono Italia (lat, lon) grossolano: penisola + isole maggiori
pts=np.array([(46.5,7.0),(47.0,10.5),(46.6,13.7),(45.6,13.8),(44.0,12.6),(41.9,16.1),(40.1,18.5),(39.0,17.1),(38.0,15.6),
              (36.7,15.1),(37.5,12.4),(38.2,12.7),(38.9,8.4),(41.2,8.2),(41.3,9.6),(40.5,9.8),(43.8,10.2),(44.2,8.0),(44.5,6.8)])
# griglia di punti di terra dentro il bounding box filtrati con matplotlib path
from matplotlib.path import Path
P=Path(pts[:,[1,0]])
lon,lat=np.meshgrid(np.arange(6.5,18.6,0.25),np.arange(36.5,47.1,0.25))
g=np.c_[lon.ravel(),lat.ravel()]; g=g[P.contains_points(g)]
G=np.radians(g)
gx=np.cos(G[:,1])*np.cos(G[:,0]); gy=np.cos(G[:,1])*np.sin(G[:,0]); gz=np.sin(G[:,1])
dt=10.0; T=30*86400; t=np.arange(0,T,dt)
# RAAN iniziale scelto per avere ~10:30 locale al nodo discendente: in terna Terra fissa conta solo la longitudine
# del nodo, che si sposta di -wE*t + precessione; la precessione SSO segue il Sole: tempo locale costante.
# Per l'Italia basta: passaggi diurni = ramo discendente. Modello: nodo ascendente alla longitudine L0 - (wE - wS)*t
wS=2*np.pi/(365.2422*86400)
u=n*t
L0=np.radians(0.0)
Om=L0-(wE-wS)*t
x=np.cos(Om)*np.cos(u)-np.sin(Om)*np.sin(u)*np.cos(i)
y=np.sin(Om)*np.cos(u)+np.cos(Om)*np.sin(u)*np.cos(i)
z=np.sin(u)*np.sin(i)
desc=np.cos(u)*np.sin(i)<0   # ramo discendente (dz/dt<0)
lam_max=310/Re   # angolo centrale di 310 km
# per ogni istante: punti di Italia raggiungibili
c=np.outer(x,gx)+np.outer(y,gy)+np.outer(z,gz)
reach=(c>np.cos(lam_max))
any_=reach.any(axis=1)
# raggruppo in passaggi
idx=np.where(any_ & desc)[0]
passes=[];cur=[idx[0]]
for k in idx[1:]:
    if k-cur[-1]>6: passes.append(cur);cur=[k]
    else: cur.append(k)
passes.append(cur)
dur=[(p[-1]-p[0])*dt for p in passes]
# lunghezza lungo traccia utile = durata * velocità al suolo
vg=n*Re
L=[d*vg for d in dur]
sc=[1+int(l//450) for l in L]   # bersagli distanti >=450 km lungo traccia (D-045)
print(f'Passaggi diurni sull\'Italia per satellite (30 giorni, raggio 310 km): {len(passes)/30:.2f} al giorno')
print(f'  tratto utile lungo traccia: mediana {np.median(L):.0f} km, max {max(L):.0f} km')
print(f'  scene per passaggio (bersagli a >= 450 km): distribuzione {np.bincount(sc)[1:]} per 1,2,3,...')
print(f'  scene massime al giorno per satellite: media {sum(sc)/30:.1f}')
days=np.floor(np.array([p[0] for p in passes])*dt/86400).astype(int)
per_day=np.bincount(days,weights=sc,minlength=30)
print(f'  per giorno: min {per_day.min():.0f}, mediana {np.median(per_day):.0f}, max {per_day.max():.0f}')
print(f'  giorni con almeno 4 scene possibili: {np.mean(per_day>=4)*100:.0f}%')
