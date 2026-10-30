"""A5.5.3 - Geometria dei contatti: distanza e perdita in funzione dell'elevazione, costo ADCS del puntamento della stazione."""
import numpy as np, re, datetime as dt, statistics as st
Re=6378.137; h=302.0; mu=398600.4418; a=Re+h
v=np.sqrt(mu/a); w=v/a  # rad/s velocità angolare orbitale
def rng(el):  # distanza obliqua [km] a elevazione el [deg]
    e=np.radians(el); return np.sqrt(a**2-(Re*np.cos(e))**2)-Re*np.sin(e)
def nadir(el): e=np.radians(el); return np.degrees(np.arcsin(Re*np.cos(e)/a))
print(f'velocità orbitale {v:.3f} km/s; limbo terrestre a {np.degrees(np.arcsin(Re/a)):.1f}° dal nadir')
print('\n1) Distanza e perdita in più rispetto allo zenit')
for el in (10,20,30,45,60,90):
    r=rng(el); print(f'  elev {el:2d}°: nadir {nadir(el):5.1f}°, distanza {r:6.0f} km, perdita in più {20*np.log10(r/h):5.1f} dB')
print('\n2) Velocità angolare della linea di vista verso la stazione (passaggio allo zenit, Terra ferma)')
# geometria piana nel piano orbitale: satellite a raggio a, stazione a Re; angolo centrale lam
lam=np.linspace(-0.4,0.4,40001)
x=a*np.sin(lam); y=a*np.cos(lam)-Re
ang=np.arctan2(x,y)  # angolo LOS rispetto alla verticale locale della stazione (inerziale ~)
# rate in terna orbita (nadir-pointing): angolo LOS dal nadir del satellite
off=np.arctan2(Re*np.sin(lam),a-Re*np.cos(lam))
t=lam/w
rate_body=np.gradient(off,t); rate_in=np.gradient(off+lam,t)
mask=np.degrees(np.abs(off))<=nadir(10)
print(f'  rispetto al nadir (rotazione in più rispetto alla terna orbitale): max {np.degrees(np.max(np.abs(rate_body[mask]))):.2f}°/s')
print(f'  inerziale (cosa vedono le ruote): max {np.degrees(np.max(np.abs(rate_in[mask]))):.2f}°/s')
I=1.14; print(f'  momento con I = {I} kg·m²: {I*np.max(np.abs(rate_in[mask])):.3f} N·m·s (FMC D-044: 0,029)')
acc=np.gradient(rate_body,t); print(f'  accelerazione max {np.degrees(np.max(np.abs(acc[mask]))):.3f}°/s², coppia {I*np.max(np.abs(acc[mask])):.2e} N·m')
