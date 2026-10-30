"""PULSE A5.6.2 - Deriva secolare dell inclinazione dovuta al Sole (orbita SSO 302 km, LTDN 10:30).
Media dell equazione di Gauss di/dt = r cos(u) W / h su un orbita e su un anno, con il nodo legato al Sole medio.
Non include la Luna (il suo effetto secolare si media sul mese perche il nodo segue il Sole, non la Luna)."""
import numpy as np
MU=398600.4418; MUS=1.32712440018e11; AU=149597870.7
a=6680.2; i=np.radians(96.68); n=np.sqrt(MU/a**3); h=np.sqrt(MU*a)
eps=np.radians(23.44)
# anno di Sole, nodo a LTAN 22:30 (nodo ascendente a 10.5 h * 15 dal Sole medio)
tot=0; N=0
for lam in np.linspace(0,2*np.pi,720,endpoint=False):
    s=np.array([np.cos(lam),np.cos(eps)*np.sin(lam),np.sin(eps)*np.sin(lam)])
    ra=np.arctan2(s[1],s[0])
    O=ra+np.radians(157.5)
    u=np.linspace(0,2*np.pi,360,endpoint=False)
    r=a*np.column_stack([np.cos(O)*np.cos(u)-np.sin(O)*np.sin(u)*np.cos(i),np.sin(O)*np.cos(u)+np.cos(O)*np.sin(u)*np.cos(i),np.sin(u)*np.sin(i)])
    w=np.array([np.sin(O)*np.sin(i),-np.cos(O)*np.sin(i),np.cos(i)])
    rs=s*AU
    d=rs-r
    acc=MUS*(d/np.linalg.norm(d,axis=1)[:,None]**3 - rs/AU**3)
    W=acc@w
    didt=a*np.cos(u)*W/h
    tot+=didt.mean(); N+=1
print('di/dt Sole (deg/anno):',np.degrees(tot/N)*365.25*86400)
