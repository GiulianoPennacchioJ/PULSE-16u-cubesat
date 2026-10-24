"""PULSE · A5.3 c) parte 1 — Cinematica del passaggio sul bersaglio, slew e rampa FMC.
Terra sferica non rotante, orbita circolare a 302 km. Uso: python cinematica.py
"""
import numpy as np
mu=398600.4418; Re=6378.137; a=6680.2
n=np.sqrt(mu/a**3)
def pass_geom(eta0_deg, dt=0.01, T=200):
    # Terra sferica non rotante, orbita circolare nel piano x-z inerziale.
    # bersaglio a terra con offset di traverso tale che l'off-nadir minimo sia eta0
    eta0=np.radians(eta0_deg)
    # angolo al centro di traverso lambda: sin(eta)= Re sin(lam)/rho ; risolvo numericamente
    from scipy.optimize import brentq
    def offnad(lam):
        s=np.array([a,0,0]); g=Re*np.array([np.cos(lam),np.sin(lam),0])
        d=g-s; return np.arccos(np.dot(-s,d)/np.linalg.norm(s)/np.linalg.norm(d))
    lam=brentq(lambda l: offnad(l)-eta0,0,0.5) if eta0>0 else 0.0
    t=np.arange(-T,T,dt)
    # satellite in piano x-y? usare: orbita nel piano x-z, bersaglio spostato in y
    sat=a*np.stack([np.cos(n*t),np.zeros_like(t),np.sin(n*t)],1)
    g=Re*np.array([np.cos(lam),np.sin(lam),0.0])
    d=g-sat; rng=np.linalg.norm(d,axis=1); u=d/rng[:,None]
    nad=-sat/a
    eta=np.degrees(np.arccos(np.sum(u*nad,1)))
    # velocità angolare inerziale della linea di vista
    du=np.gradient(u,dt,axis=0); w=np.linalg.norm(np.cross(u,du),axis=1)
    alpha=np.abs(np.gradient(w,dt))
    return t,eta,np.degrees(w),np.degrees(alpha),rng
for e0 in (0,30,45):
    t,eta,w,al,rng=pass_geom(e0)
    out=[f"off-nadir min {e0}°: velocità LOS al centro {w[len(t)//2]:.3f}°/s, max {w.max():.3f}°/s"]
    for lim in (30,45):
        m=eta<=lim
        if m.any():
            out.append(f"  finestra entro {lim}°: {t[m][-1]-t[m][0]:.1f} s; LOS al bordo {w[m][0]:.3f}°/s; accel. max in finestra {al[m].max():.2e}°/s²")
    print('\n'.join(out))
I=np.array([0.64,1.14])
print('n orbitale °/s',np.degrees(n))
# FMC: momento a 1,4°/s
wf=np.radians(1.399)
print('h FMC min/max',I*wf)
# slew bang-bang 45° e 30°
for th in (30,45):
  for ts in (120,60,30):
    T=4*np.radians(th)*I/ts**2; wp=2*np.radians(th)/ts
    print(f"slew {th}° in {ts}s: coppia {T[0]:.2e}–{T[1]:.2e} N·m, picco {np.degrees(wp):.2f}°/s, h {I[0]*wp:.3f}–{I[1]*wp:.3f} N·m·s")
# swing FMC breve: rampa con coppia T fino a 1,4°/s
for T in (1e-3,3e-3,7e-3):
    tr=I*wf/T; thr=np.degrees(0.5*wf*tr)
    print(f"rampa FMC con {T:.0e} N·m: durata {tr[0]:.1f}–{tr[1]:.1f} s, angolo spazzato {thr[0]:.1f}–{thr[1]:.1f}°")
