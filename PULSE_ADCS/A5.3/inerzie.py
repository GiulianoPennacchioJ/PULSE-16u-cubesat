"""PULSE · A5.3 b) — Inviluppo d'inerzia del 16U (D-043).
Caso pieno (massa uniforme nel volume) e caso guscio (massa sulle pareti), 30–36 kg,
per i tre orientamenti L1/L2/L3. Uso: python inerzie.py
"""
import numpy as np
L,S=0.454,0.2263   # lato lungo, lato corto (m), involucro EXOpod Nova
def solid(m,a,b,c): return np.array([m/12*(b*b+c*c), m/12*(a*a+c*c), m/12*(a*a+b*b)])
def shell(m,a,b,c):
    # massa uniforme sulle 6 facce (scatola a parete sottile)
    A=np.array([b*c,b*c,a*c,a*c,a*b,a*b]); sig=m/A.sum(); I=np.zeros(3)
    dims=np.array([a,b,c])
    for k,(n,sgn) in enumerate([(0,1),(0,-1),(1,1),(1,-1),(2,1),(2,-1)]):
        mf=sig*A[k]; d=dims.copy(); off=np.zeros(3); off[n]=sgn*dims[n]/2; d[n]=0
        # piastra con dimensioni d (una nulla), centrata in off
        Ic=mf/12*np.array([d[1]**2+d[2]**2, d[0]**2+d[2]**2, d[0]**2+d[1]**2])
        Ip=mf*np.array([off[1]**2+off[2]**2, off[0]**2+off[2]**2, off[0]**2+off[1]**2])
        I+=Ic+Ip
    return I
lay={'L1 asse lungo a nadir (Z)':(S,S,L),'L2 asse lungo di traverso (Y)':(S,L,S),'L3 asse lungo lungo traccia (X)':(L,S,S)}
for name,(a,b,c) in lay.items():
    print(name, 'area frontale (faccia normale a X) m2 =', round(b*c,4))
    for m in (30,32,36):
        print('  m=%d  pieno [Ix rollio, Iy beccheggio, Iz imbardata] ='%m, np.round(solid(m,a,b,c),3), ' guscio =', np.round(shell(m,a,b,c),3))
# pannelli: 1 kg totali su due ali, centroide a 0,226 m dall'asse, larghezza ala 0,226
mp=1.0; w=0.2263
print('pannelli 1 kg: dI su ciascuno dei due assi normali alla direzione delle ali ~', round(mp*(w**2/12+w**2),4))
# accoppiamento FMC x orbita, con differenze d'inerzia
n=1.1563e-3; wf=np.radians(1.399)
for name,(a,b,c) in lay.items():
    I=solid(32,a,b,c); print(name,'dI max',round(max(I)-min(I),3),'coppia giroscopica wf*n*dI', '%.2e'%(wf*n*(max(I)-min(I))))
