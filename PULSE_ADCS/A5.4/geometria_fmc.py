"""
PULSE · Fase A · A5.4.3 b) — Geometria della FMC notturna ai bordi del campo
============================================================================

La simulazione 1-asse di A5.3 controlla solo il CENTRO dell'immagine (la linea
di vista sul bersaglio). Durante la FMC, però, il satellite si muove rispetto
al suolo e l'immagine del terreno ai BORDI del campo cambia anche se il centro
è fermo:
  - zoom: la distanza dal bersaglio cambia (dR/dt), il terreno si ingrandisce
    o si rimpicciolisce;
  - rotazione attorno all'asse ottico: con il bersaglio di traverso il terreno
    inclinato ruota nell'immagine;
  - piccole deformazioni prospettiche.
Questi effetti sono deterministici (noti da orbita e assetto), ma una
traslazione pura (D-040, riallineamento shift-and-add di D-030) NON li corregge.

Cosa calcola
------------
Per un inseguimento ideale (centro fermo sul bersaglio, nessuna rotazione
comandata attorno all'asse ottico) lo spostamento nell'immagine dei punti a
terra visti agli angoli del campo sCMOS (semi-diagonale 22,8 mrad), lungo:
  - uno scatto da 20 ms (mosso dentro lo scatto, soglia 1/3 pixel = 5,2 µrad)
  - la raffica città 10 x 20 ms = 0,2 s (1x1, soglia 5,2 µrad)
  - la raffica paesi 15 x 20 ms = 0,3 s (2x2, pixel 31,4 µrad, soglia 10,5 µrad)
in funzione dell'istante della raffica rispetto al passaggio più vicino e
dell'angolo di traverso (0°, 30°, 45° off-nadir al passaggio).
Separa la parte di zoom e di rotazione (correggibili con un riallineamento
"di similitudine": traslazione + rotazione + scala) dal residuo prospettico.

Ipotesi: orbita circolare a 302 km, Terra sferica NON rotante (la rotazione
terrestre cambia la velocità al suolo di < 1%, rotazione.py di A5.3), suolo
piatto alla quota del bersaglio (niente rilievo), assetto ideale.
Uso: python geometria_fmc.py > risultati/geometria_fmc.txt
"""
import numpy as np

MU, RE, A = 398600.4418, 6378.137, 6680.2       # km, D-012
N = np.sqrt(MU / A**3)
F = 0.70                                        # focale (m), D-024
PIX = 11e-6 / F                                 # IFOV sCMOS 1x1 (rad), D-026
HALF_DIAG = 1024 * np.sqrt(2) * PIX             # semi-diagonale del campo (rad)
SOGLIA_1x1 = PIX / 3
SOGLIA_2x2 = 2 * PIX / 3
RAFFICHE = [('scatto 20 ms', 0.020, SOGLIA_1x1),
            ('città 10x20 ms (1x1)', 0.200, SOGLIA_1x1),
            ('paesi 15x20 ms (2x2)', 0.300, SOGLIA_2x2)]


def sat(t):
    return A * np.array([np.cos(N * t), np.sin(N * t), 0.0])


def beta_da_offnadir(eta):
    """Angolo al centro della Terra del bersaglio fuori piano per off-nadir eta."""
    if eta == 0:
        return 0.0
    # tan(eta) = RE sin(b) / (A - RE cos(b))  -> soluzione numerica
    from scipy.optimize import brentq
    return brentq(lambda b: np.arctan2(RE * np.sin(b), A - RE * np.cos(b)) - eta, 1e-9, 0.5)


def interseca_sfera(o, d):
    """Primo punto in cui il raggio o + s d incontra la sfera di raggio RE."""
    bq = 2 * o @ d
    cq = o @ o - RE**2
    s = (-bq - np.sqrt(bq**2 - 4 * cq)) / 2
    return o + s * d


def unit(v):
    return v / np.linalg.norm(v)


def analisi(eta_deg, t0, T, dt=1e-3):
    """Spostamento nell'immagine (rad) dei punti d'angolo durante [t0, t0+T]."""
    b0 = beta_da_offnadir(np.radians(eta_deg))
    P0 = RE * np.array([np.cos(b0), 0.0, np.sin(b0)])
    # terna camera iniziale: asse ottico verso il bersaglio, e1 ~ lungo traccia
    r = sat(t0)
    bvec = unit(P0 - r)
    vdir = np.array([-np.sin(N * t0), np.cos(N * t0), 0.0])
    e1 = unit(vdir - (vdir @ bvec) * bvec)
    e2 = np.cross(bvec, e1)
    # punti a terra visti agli 8 punti del bordo (angoli e metà lati) a t0
    dirs = []
    for ang in np.radians(np.arange(0, 360, 45)):
        rad = HALF_DIAG if (round(np.degrees(ang)) % 90 == 45) else 1024 * PIX
        x, y = rad * np.cos(ang), rad * np.sin(ang)
        dirs.append((x, y))
    pts = [interseca_sfera(r, unit(bvec + x * e1 + y * e2)) for x, y in dirs]
    xy0 = np.array(dirs)
    peggiore = 0.0
    k_fin = int(round(T / dt))
    for k in range(1, k_fin + 1):
        t = t0 + k * dt
        r = sat(t)
        bn = unit(P0 - r)
        # trasporto parallelo della terna: nessuna rotazione attorno all'asse ottico
        e1 = unit(e1 - (e1 @ bn) * bn)
        e2 = np.cross(bn, e1)
        bvec = bn
    # coordinate finali
    xy = []
    for P in pts:
        u = unit(P - r)
        xy.append(((u @ e1) / (u @ bvec), (u @ e2) / (u @ bvec)))
    xy = np.array(xy)
    d = xy - xy0
    totale = np.abs(np.hypot(d[:, 0], d[:, 1])).max()
    # scomposizione: d ≈ s*xy0 + rho*J*xy0 (similitudine centrata)
    J = np.column_stack([-xy0[:, 1], xy0[:, 0]])
    M = np.column_stack([xy0.reshape(-1), J.reshape(-1)])
    coef, *_ = np.linalg.lstsq(M, d.reshape(-1), rcond=None)
    s, rho = coef
    res = d.reshape(-1) - M @ coef
    residuo = np.abs(np.hypot(res[0::2], res[1::2])).max()
    R0 = np.linalg.norm(P0 - sat(t0))
    return totale, abs(s) * HALF_DIAG, abs(rho) * HALF_DIAG, residuo, R0


def main():
    print(f'IFOV sCMOS 1x1 {PIX*1e6:.2f} µrad; semi-diagonale campo {HALF_DIAG*1e3:.2f} mrad; '
          f'soglia 1x1 {SOGLIA_1x1*1e6:.2f} µrad, 2x2 {SOGLIA_2x2*1e6:.2f} µrad')
    print('Spostamento massimo dei punti al bordo (µrad) con riallineamento a sola traslazione;\n'
          'tra parentesi: parte di zoom | parte di rotazione | residuo dopo similitudine\n')
    for eta in (0, 30, 45):
        print(f'=== bersaglio a {eta}° di traverso al passaggio')
        for nome, T, soglia in RAFFICHE:
            riga = []
            tmax_ok = None
            for t0c in np.arange(0.0, 40.01, 0.5):        # centro raffica rispetto al passaggio
                tot, z, rot, res, R0 = analisi(eta, t0c - T / 2, T)
                if tot <= soglia:
                    tmax_ok = t0c
                if t0c in (0.0, 2.0, 5.0, 10.0, 20.0, 40.0):
                    riga.append(f'  t={t0c:4.0f} s: {tot*1e6:7.2f} ({z*1e6:6.2f} | {rot*1e6:6.2f} | {res*1e6:5.2f})'
                                f'{"" if tot <= soglia else " >soglia"}')
            # finestra contigua attorno al passaggio
            cont = 0.0
            for t0c in np.arange(0.0, 40.01, 0.1):
                tot, *_ = analisi(eta, t0c - T / 2, T)
                if tot > soglia:
                    break
                cont = t0c
            print(f' {nome}: soglia {soglia*1e6:.1f} µrad; sola traslazione ok entro ±{cont:.1f} s dal passaggio')
            print('\n'.join(riga))
            # con similitudine: residuo massimo su tutta la finestra 30°/45°
            tw = 23.85 if eta <= 30 else 40.0
            worst = max(analisi(eta, t - T / 2, T)[3] for t in np.linspace(0, tw, 25))
            print(f'   con riallineamento di similitudine (traslazione+rotazione+scala): residuo max {worst*1e6:.3f} µrad '
                  f'su ±{tw:.0f} s')
        print()
    # stabilità attorno all'asse ottico (rumore, non geometria)
    print('Stabilità attorno all\'asse ottico (deriva casuale d\'imbardata) che sposta l\'angolo del campo di 1/3 pixel:')
    for nome, T, soglia in RAFFICHE:
        w = soglia / (T * HALF_DIAG)
        print(f'  {nome}: deriva ≤ {np.degrees(w):.3f}°/s')


if __name__ == '__main__':
    main()


# ------------------------------------------------------------------ aggiunte
def velocita_imbardata(eta_deg, T=0.2):
    """Velocità di rotazione della scena attorno all'asse ottico (°/s) al passaggio."""
    _, _, rot, _, _ = analisi(eta_deg, -T / 2, T)
    return np.degrees(rot / HALF_DIAG / T)


def parallasse(eta_deg, T, dh=1.0):
    """Spostamento angolare (rad) in T, al passaggio, di un punto alto dh km
    rispetto al punto del piano sotto di lui (al centro del campo)."""
    b0 = beta_da_offnadir(np.radians(eta_deg))
    P0 = RE * np.array([np.cos(b0), 0.0, np.sin(b0)])
    Ph = P0 * (RE + dh) / RE
    def ang(t):
        r = sat(t)
        u0, uh = unit(P0 - r), unit(Ph - r)
        return np.arccos(np.clip(u0 @ uh, -1, 1)), np.cross(u0, uh)
    a1, c1 = ang(-T / 2); a2, c2 = ang(T / 2)
    # differenza vettoriale delle direzioni relative (piccoli angoli)
    return np.linalg.norm(c2 - c1)


def bande_diurne(eta_deg, ritardo, pix):
    """Ripresa diurna push-broom ad assetto fisso (rollio eta, nessuna FMC):
    errore di registrazione residuo, dopo la traslazione, tra due righe del
    sensore che vedono lo stesso suolo a 'ritardo' secondi di distanza.
    Restituisce il residuo massimo al bordo della strisciata (rad) e in pixel."""
    b0 = beta_da_offnadir(np.radians(eta_deg))
    half_swath = 3232 * 3.45e-6 / F                  # semi-strisciata PAN (rad), D-024
    # direzioni nel riferimento LVLH ruotato col satellite: x lungo traccia, z verso nadir
    eta = np.radians(eta_deg)
    def camera(t):
        r = sat(t); zn = -unit(r)
        xv = np.array([-np.sin(N * t), np.cos(N * t), 0.0])
        yc = np.cross(zn, xv)
        bvec = unit(np.cos(eta) * zn + np.sin(eta) * yc * np.sign(b0 if b0 else 1) * -1)
        if eta_deg == 0:
            bvec = zn
        e1 = unit(xv - (xv @ bvec) * bvec); e2 = np.cross(bvec, e1)
        return r, bvec, e1, e2
    phi = ritardo * 7.375 / ( np.linalg.norm(sat(0)) - RE) / 2   # metà separazione lungo traccia (rad)
    r0, b, e1, e2 = camera(0.0)
    out = []
    for y in (0.0, half_swath, -half_swath):
        P = interseca_sfera(r0, unit(b + 2 * phi * e1 + y * e2)) # riga "avanti" (bordo del campo) a t = 0
        # trova t in cui la riga sull'asse ottico (angolo 0) vede P: caso asimmetrico, il peggiore
        lo, hi = 0.0, 2 * ritardo
        for _ in range(60):
            mid = (lo + hi) / 2
            r, bb, f1, f2 = camera(mid)
            u = unit(P - r)
            if (u @ f1) / (u @ bb) > 0.0:
                lo = mid
            else:
                hi = mid
        r, bb, f1, f2 = camera(lo)
        u = unit(P - r)
        out.append((u @ f2) / (u @ bb) - y)
    res = max(abs(out[1] - out[0]), abs(out[2] - out[0]))
    return res, res / pix


def main2():
    print('\nVelocità di rotazione della scena attorno all\'asse ottico al passaggio (da compensare con l\'imbardata):')
    for eta in (0, 30, 45):
        print(f'  {eta}° di traverso: {velocita_imbardata(eta):.3f}°/s')
    print('\nParallasse del rilievo (punto 1 km sopra il piano del bersaglio), al passaggio:')
    for eta in (0, 30, 45):
        for nome, T, soglia in RAFFICHE[1:]:
            p = parallasse(eta, T)
            print(f'  {eta}°, {nome}: {p*1e6:.1f} µrad per km di dislivello -> dislivello ammesso senza DEM '
                  f'{soglia/p*1000:.0f} m')
    print('\nRipresa diurna ad assetto fisso: residuo geometrico di registrazione al bordo della strisciata, dopo la traslazione')
    pan = 3.45e-6 / F; col = 2 * pan
    for eta in (0, 30, 45):
        r1, p1 = bande_diurne(eta, 0.15, pan)
        r2, p2 = bande_diurne(eta, 0.79, col)
        print(f'  {eta}°: TDI 0,15 s {r1*1e6:.2f} µrad = {p1:.3f} pixel PAN; bande 0,79 s {r2*1e6:.2f} µrad = {p2:.3f} pixel colore')


if __name__ == '__main__':
    main2()


def main3():
    """Parallasse del rilievo nella ripresa diurna (assetto fisso): le righe del
    sensore vedono lo stesso suolo da direzioni diverse a distanza di 0,15 s (TDI)
    e fino a 0,79 s (bande). Un punto più alto del piano di riferimento si sposta."""
    pan = 3.45e-6 / F
    soglie = [('TDI 4 passaggi, 0,15 s', 0.15, 0.3 * pan, '0,3 pixel PAN picco-picco (D-053)'),
              ('bande RGB-NIR, 0,79 s', 0.79, 2 * pan / 3, '1/3 pixel colore')]
    print('\nParallasse del rilievo nella ripresa diurna (1 km di dislivello rispetto al piano di riferimento):')
    for eta in (0, 30, 45):
        for nome, T, soglia, sd in soglie:
            p = parallasse(eta, T)
            print(f'  {eta}°, {nome}: {p*1e6:.1f} µrad/km = {p*1e6/ (pan*1e6):.1f} pixel PAN per km; '
                  f'dislivello ammesso con sola traslazione {soglia/p*1000:.0f} m (soglia {sd})')
    print('  Con DEM a bordo (errore verticale tipico ≤ 4 m, Copernicus GLO-30): residuo bande '
          f'{parallasse(0, 0.79)*4e-3*1e6:.2f} µrad, TDI {parallasse(0, 0.15)*4e-3*1e6:.3f} µrad a nadir')


if __name__ == '__main__':
    main3()
