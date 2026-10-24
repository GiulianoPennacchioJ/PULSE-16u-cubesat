"""PULSE · A5.3 c) — Effetto della rotazione terrestre e dell'eccentricità
(velocità a terra e deriva laterale della traccia). Uso: python rotazione.py
"""
import numpy as np
mu=398600.4418; Re=6378.137; a=6680.2; inc=np.radians(96.8); wE=7.2921159e-5
n=np.sqrt(mu/a**3); h=a-Re
for lat_deg in (36,42,47):
    lat=np.radians(lat_deg)
    # azimut della traccia (da nord), orbita retrograda
    saz=np.cos(inc)/np.cos(lat); az=np.arcsin(saz)
    vg=n*Re                       # velocità del punto sub-satellite, Terra ferma (km/s)
    vN=vg*np.cos(az); vE=vg*np.sin(az)        # passaggio ascendente (verso nord)
    vEarth=wE*Re*np.cos(lat)
    for name,sN in (('ascendente (notte)',1),('discendente (giorno)',-1)):
        vrel=np.array([sN*vN, vE*(1 if sN>0 else 1) - vEarth])  # componente est: la traccia va verso ovest in entrambi
        vrel=np.array([sN*vN, -abs(vE) - vEarth])
        sp=np.linalg.norm(vrel)
        # angolo di deriva laterale: tra direzione della traccia (Terra ferma) e moto relativo
        v0=np.array([sN*vN,-abs(vE)])
        crab=np.degrees(np.arccos(np.dot(v0,vrel)/np.linalg.norm(v0)/sp))
        print(f"lat {lat_deg}° {name}: v suolo Terra ferma {vg:.3f}, con rotazione {sp:.3f} km/s ({(sp/vg-1)*100:+.1f}%), deriva laterale {crab:.2f}°, spostamento laterale in 0,79 s {np.sin(np.radians(crab))*sp*0.79*1000:.0f} m")
# effetto eccentricità sulla quota
e=0.0011
print('quota min/max per e', a*(1-e)-Re, a*(1+e)-Re)
