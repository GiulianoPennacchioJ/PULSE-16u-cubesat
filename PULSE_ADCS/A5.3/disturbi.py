"""
PULSE · Fase A · A5.3 d) — Coppie di disturbo e momento accumulato (primo ordine)
===================================================================================
Densità:  media dai risultati GMAT di mantenimento (F10.7 = 129, Cd 2,2, A 0,1 m², 30 kg)
          picco con il modello MSIS (pymsis) a 302 km lungo un'orbita SSO 10:30/22:30.
Geometria: orientamento L1 (D-043), faccia 226 × 454 mm sulla velocità.
Bracci: distanza baricentro – linea di spinta e baricentro – centro di pressione, come parametro.
Uso:  pip install numpy pymsis ;  python disturbi.py
"""
from datetime import datetime
import numpy as np

MU = 398600.4418; RE = 6378.137; A_ORB = 6680.2
N = np.sqrt(MU / A_ORB**3); PERIODO = 2 * np.pi / N
V = np.sqrt(MU / A_ORB) * 1e3                    # m/s
CD = 2.2
A_FRONT = 0.103                                  # m², faccia 226 × 454 mm (L1)
A_MAX = 0.115                                    # m², massimo con il satellite inclinato in beccheggio
DI_MAX = 0.589                                   # kg m², differenza d'inerzia massima (36 kg, guscio)
B0 = 3.0e-5                                      # T, dipolo terrestre all'equatore in superficie (approssimato)
DIPOLO = (0.1, 0.01)                             # A m², dipolo residuo (EarthNext, Tab. 4)
SPINTA = (0.55e-3, 1.1e-3)                       # N, REGULUS nominale e inviluppo D-034
BRACCI = (0.005, 0.010, 0.020, 0.045, 0.090)     # m (45/90 mm = limiti del deployer, DR-14)
ORE_SPINTA = 4.2                                 # h al giorno (R-14)


def densita_gmat(file='../../PULSE_GMAT/Output_PULSE/Mantenimento_F129.txt', m=30.0, A=0.1):
    righe = open(file).read().splitlines()[1:]
    dv = np.array([float(r.split()[-2]) for r in righe if r.strip()]) * 1000   # m/s al giorno
    rho = 2 * m * (dv / 86400) / (CD * A * V**2)
    return rho.mean(), rho.max()


def densita_msis(f107, ap):
    import pymsis
    lat = np.linspace(-85, 85, 35); v = []
    for ora in (10.5, 22.5):
        for d in (datetime(2026, 3, 21, 12), datetime(2026, 6, 21, 12), datetime(2026, 12, 21, 12)):
            out = pymsis.calculate(np.array([np.datetime64(d)] * lat.size), np.full(lat.size, (ora - 12) * 15),
                                   lat, np.full(lat.size, 302.0), f107s=np.full(lat.size, f107),
                                   f107as=np.full(lat.size, f107), aps=np.full((lat.size, 7), ap))
            v.append(out[..., pymsis.Variable.MASS_DENSITY].ravel())
    v = np.concatenate(v)
    return v.mean(), v.max()


if __name__ == '__main__':
    print(f'Periodo orbitale {PERIODO:.0f} s, velocità {V:.0f} m/s')
    medio, massimo = densita_gmat()
    print(f'Densità da GMAT (F10.7 = 129): media {medio:.2e}, massima {massimo:.2e} kg/m³')
    for f107, ap in ((129, 15), (181, 50), (250, 50)):
        mm, mx = densita_msis(f107, ap)
        print(f'Densità MSIS F10.7 = {f107}, Ap = {ap}: media {mm:.2e}, massima {mx:.2e} kg/m³')
    print('\nCoppia aerodinamica = 1/2 rho v² Cd A × braccio')
    for rho, nome in ((medio, 'media F129'), (4.6e-11, 'massima F181 Ap50'), (7.5e-11, 'estrema F250 Ap50')):
        F = 0.5 * rho * V**2 * CD * A_MAX
        print(f'  {nome}: forza {F:.2e} N; coppia ' + ', '.join(f'{d*1e3:.0f} mm → {F*d:.1e}' for d in BRACCI))
    print('\nCoppia da spinta = F × braccio')
    for F in SPINTA:
        print(f'  {F*1e3:.2f} mN: ' + ', '.join(f'{d*1e3:.0f} mm → {F*d:.1e} N m' for d in BRACCI))
    print(f'\nGradiente di gravità a 45°: {1.5*N**2*DI_MAX:.1e} N m')
    k = (RE / A_ORB)**3
    print(f'Campo magnetico a 302 km: {B0*k*1e6:.0f} µT (equatore) – {2*B0*k*1e6:.0f} µT (polo)')
    for m in DIPOLO:
        print(f'Dipolo residuo {m} A m²: coppia max {m*2*B0*k:.1e} N m')
    print(f'Pressione solare (0,5 m², riflessione totale, braccio 0,1 m): {1361/3e8*0.5*2*0.1:.1e} N m')
    print('\nMomento accumulato')
    for c in (6.9e-6, 3.1e-5):
        print(f'  aerodinamica {c:.1e} N m costante: {c*PERIODO:.3f} N m s per orbita')
    for c in (1.1e-5, 9.9e-5):
        print(f'  spinta {c:.1e} N m per {ORE_SPINTA} h di fila: {c*ORE_SPINTA*3600:.2f} N m s')
