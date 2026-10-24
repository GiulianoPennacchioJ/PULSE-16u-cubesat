"""
PULSE · Fase A · A5.4.3 a) — Slew, aggancio e assestamento (bilancio dei tempi, DR-08)
=====================================================================================

Riusa il modello 1-asse di A5.3 (../A5.3/sim1asse.py: dinamica, ruota con
ritardo 20 ms, controllo PD + anticipo di coppia, giroscopio) e aggiunge la
manovra che PRECEDE la ripresa:

  Notte (FMC, profilo F2, D-044): dal puntamento a nadir il satellite ruota fino
     ad agganciare la linea di vista al bordo della finestra (30° o 45°), con
     angolo, velocità e accelerazione raccordati (polinomio di 5° grado), coppia
     pianificata ≤ 1,0·10⁻³ N·m (D-045) sull'inerzia stimata.
  Giorno (push-broom, assetto fisso): slew di 45° "da fermo a fermo" nel
     riferimento orbitale in 60 s, profilo bang-bang a 1,0·10⁻³ N·m (D-045),
     poi assetto fisso fuori nadir.

Metriche, misurate dalla FINE della manovra:
  - t_APE: da quando l'errore di puntamento resta < 0,1° (DR-15)
  - notte: inizio del primo blocco di 18 scatti consecutivi da 20 ms con mosso
    < 5,2 µrad (DR-10, DR-11) ed errore < 0,1°
  - giorno: da quando la deriva vera su ogni intervallo di 0,79 s resta
    < 0,001°/s (DR-05) ed errore < 0,1°

Casi: inerzia vera 0,64 / 1,14 kg·m² (D-043); controllore con inerzia stimata in
volo +10% / −10% (D-046, dopo il commissioning) e, come stress, con l'inerzia
nominale 0,69 (prima del commissioning); banda 1 rad/s, 10 Hz (D-046);
giroscopio GY2 (classe "Alta qualità" di A5.3, D-050); 5 ripetizioni, caso peggiore.
Uso: python assestamento.py > risultati/assestamento.txt
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'A5.3'))
from sim1asse import DT, FRAME, SMEAR_MAX, GIROSCOPI, MU, A_ORB, linea_di_vista, simula  # noqa: E402

N = np.sqrt(MU / A_ORB**3)
T_PIANO = 1.0e-3            # coppia pianificata per la manovra (N m), D-045
APE = np.radians(0.1)
DERIVA = np.radians(0.001)  # DR-05
T_BANDE = 0.79
SEMI = 5


def nadir(t):
    return np.pi + N * t


def quintica(T, x0, v0, a0, x1, v1, a1, tau):
    """Polinomio di 5° grado con estremi assegnati; restituisce x, v, a in tau."""
    M = np.array([[1, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0], [0, 0, 2, 0, 0, 0],
                  [1, T, T**2, T**3, T**4, T**5], [0, 1, 2*T, 3*T**2, 4*T**3, 5*T**4],
                  [0, 0, 2, 6*T, 12*T**2, 20*T**3]])
    c = np.linalg.solve(M, [x0, v0, a0, x1, v1, a1])
    x = sum(c[i] * tau**i for i in range(6))
    v = sum(i * c[i] * tau**(i - 1) for i in range(1, 6))
    a = sum(i * (i - 1) * c[i] * tau**(i - 2) for i in range(2, 6))
    return x, v, a


def rif_notte(off_nadir_deg, ihat_piano):
    """Riferimento: nadir -> aggancio della linea di vista al bordo della finestra -> F2."""
    # istante del bordo della finestra (linea di vista a off_nadir_deg prima del passaggio)
    tt = np.arange(-60, 0, 1e-3)
    psi = linea_di_vista(tt)
    off = np.degrees(np.abs(psi - nadir(tt)))
    te = tt[np.argmin(np.abs(off - off_nadir_deg))]
    # derivate della linea di vista al bordo
    h = 1e-3
    p0, pm, pp = linea_di_vista(np.array([te - h, te, te + h]))
    dpsi = (pp - p0) / (2 * h); ddpsi = (pp - 2 * pm + p0) / h**2
    x1 = pm - nadir(te); v1 = dpsi - N; a1 = ddpsi
    # durata minima con coppia pianificata ≤ T_PIANO sull'inerzia stimata
    for T in np.arange(5, 200, 0.5):
        tau = np.linspace(0, T, 2001)
        _, _, a = quintica(T, 0, 0, 0, x1, v1, a1, tau)
        if np.abs(a).max() * ihat_piano <= T_PIANO:
            break
    ts = te - T
    t = np.arange(ts - 5.0, -te, DT)           # fino al bordo opposto della finestra
    ref = linea_di_vista(t).copy()
    wr = np.gradient(ref, DT); ar = np.gradient(wr, DT)
    for k, tk in enumerate(t):
        if tk < ts:
            ref[k] = nadir(tk); wr[k] = N; ar[k] = 0.0
        elif tk < te:
            x, v, a = quintica(T, 0, 0, 0, x1, v1, a1, tk - ts)
            ref[k] = nadir(tk) + x; wr[k] = N + v; ar[k] = a
    return t, ref, wr, ar, te, T, np.degrees(abs(x1))


def rif_giorno(angolo_deg=45.0, durata=60.0):
    """Slew bang-bang da fermo a fermo nel riferimento orbitale, poi assetto fisso."""
    th = np.radians(angolo_deg)
    a = 4 * th / durata**2
    t = np.arange(-5.0, durata + 30.0, DT)
    x = np.where(t < 0, 0, np.where(t < durata / 2, 0.5 * a * t**2,
                 np.where(t < durata, th - 0.5 * a * (durata - t)**2, th)))
    v = np.where(t < 0, 0, np.where(t < durata / 2, a * t, np.where(t < durata, a * (durata - t), 0)))
    acc = np.where(t < 0, 0, np.where(t < durata / 2, a, np.where(t < durata, -a, 0)))
    ref = nadir(t) + x; wr = N + v
    return t, ref, wr, acc, durata, a


def tempi(err, t, te, notte):
    i0 = int(np.searchsorted(t, te))
    e = err[i0:]
    fuori = np.where(np.abs(e) >= APE)[0]
    t_ape = 0.0 if fuori.size == 0 else (fuori[-1] + 1) * DT
    if notte:
        m = int(round(FRAME / DT)); nf = e.size // m
        blk = e[:nf * m].reshape(nf, m)
        ok = ((blk.max(1) - blk.min(1)) < SMEAR_MAX) & (np.abs(blk).max(1) < APE)
        for q in range(nf - 18 + 1):
            if ok[q:q + 18].all():
                return t_ape, q * FRAME
        return t_ape, np.nan
    lag = int(round(T_BANDE / DT))
    drift = np.abs(e[lag:] - e[:-lag]) / T_BANDE
    bad = np.where((drift >= DERIVA) | (np.abs(e[lag:]) >= APE))[0]
    return t_ape, (0.0 if bad.size == 0 else (bad[-1] + 1) * DT)


def main():
    arw, bias = GIROSCOPI['Alta qualità']
    casi_ctrl = [('stimata +10%', 1.10), ('stimata −10%', 0.90), ('nominale 0,69 (pre-commissioning)', None)]
    print('Banda 1 rad/s, controllo 10 Hz, giroscopio GY2, caso peggiore su 5 ripetizioni\n')
    for nome_m, notte, arg in [('NOTTE: nadir -> aggancio LOS al bordo 30°', True, 30.0),
                               ('NOTTE: nadir -> aggancio LOS al bordo 45°', True, 45.0),
                               ('GIORNO: slew 45° in 60 s (bang-bang) -> assetto fisso', False, 45.0)]:
        print('=== ' + nome_m)
        for I in (0.64, 1.14):
            for nome_c, f in casi_ctrl:
                ihat = I * f if f else 0.69
                if notte:
                    t, ref, wr, ar, te, T, ang = rif_notte(arg, ihat)
                    extra = f'manovra {ang:.1f}° in {T:.1f} s'
                else:
                    t, ref, wr, ar, te, a = rif_giorno(arg)
                    extra = f'manovra 45° in 60 s, coppia pianificata {a*ihat*1e3:.2f} mN·m'
                pegg = [0.0, 0.0]; hmax = 0.0; cmax = 0.0
                for s in range(SEMI):
                    sg = 1 if s % 2 == 0 else -1
                    err, cop, hw = simula(ref, wr, ar, I, 1.0, 10, arw, sg * bias, 2000 + s, ihat)
                    ta, tb = tempi(err, t, te, notte)
                    pegg[0] = max(pegg[0], ta)
                    pegg[1] = np.nan if (np.isnan(tb) or np.isnan(pegg[1])) else max(pegg[1], tb)
                    hmax = max(hmax, np.abs(hw).max()); cmax = max(cmax, np.abs(cop).max())
                lab = 'primi 0,36 s di scatti buoni' if notte else 'deriva < 0,001°/s'
                print(f'  I vera {I:.2f}, controllore {nome_c:<34} {extra}; coppia max {cmax*1e3:.2f} mN·m, '
                      f'momento max {hmax:.3f} N·m·s -> APE < 0,1° dopo {pegg[0]:.2f} s; {lab} dopo {pegg[1]:.2f} s')
        print()


if __name__ == '__main__':
    main()


def ripuntamento_notte(off_deg=30.0, ihat=1.254):
    """Tempo minimo (coppia pianificata ≤ 1 mN·m su ihat) per passare dalla fine
    dell'inseguimento di un bersaglio (bordo d'uscita della finestra) all'aggancio
    del bersaglio successivo sotto la traccia (bordo d'entrata), con raccordo di
    angolo, velocità e accelerazione. Restituisce durata e distanza minima tra i
    due bersagli lungo la traccia."""
    tt = np.arange(-60, 0, 1e-3)
    psi = linea_di_vista(tt)
    te = tt[np.argmin(np.abs(np.degrees(np.abs(psi - nadir(tt))) - off_deg))]
    h = 1e-3
    def stato(t):
        p0, pm, pp = linea_di_vista(np.array([t - h, t, t + h]))
        return pm - nadir(t), (pp - p0) / (2 * h) - N, (pp - 2 * pm + p0) / h**2
    x1, v1, a1 = stato(te)          # entrata nel bersaglio successivo
    x0, v0, a0 = stato(-te)         # uscita dal bersaglio precedente
    for T in np.arange(5, 400, 0.5):
        tau = np.linspace(0, T, 4001)
        _, _, a = quintica(T, x0, v0, a0, x1, v1, a1, tau)
        if np.abs(a).max() * ihat <= T_PIANO:
            break
    finestra = -2 * te
    vg = 7.375                       # velocità al suolo (km/s), rotazione.py di A5.3
    return T, finestra, (finestra + T) * vg


if __name__ == '__main__':
    print('Ripuntamento notturno tra due bersagli sotto la traccia (stesso satellite):')
    for off in (30.0, 45.0):
        for ih, lab in ((1.254, 'inerzia stimata 1,14 +10%'), (0.704, 'inerzia stimata 0,64 +10%')):
            T, w, d = ripuntamento_notte(off, ih)
            print(f'  finestra {off:.0f}° ({w:.1f} s), {lab}: manovra {T:.1f} s -> bersagli distanti almeno {d:.0f} km lungo traccia')
    vg = 7.375
    print('Giorno, due bersagli sullo stesso lato a 45°: ripresa ~2,2 s (scena 10 km + 0,79 s bande) + slew 60 s + assestamento 3 s'
          f' -> stesso assetto: nessuno slew; lato opposto (90°): slew bang-bang {60*np.sqrt(2):.0f} s')
    print('Limite inferiore (bang-bang ideale): raffica 1 e raffica 2 entrambe al bordo d\'entrata della finestra,')
    print('stessa velocità relativa v -> la velocità passa da v a -v e torna a v: durata 4·v/a_max')
    for off, w_in in ((30.0, 1.090), (45.0, 0.715)):
        v = np.radians(w_in) - N
        for ih in (1.254, 0.704):
            T = 4 * v / (T_PIANO / ih)
            print(f'  bordo {off:.0f}° (LOS {w_in}°/s), inerzia stimata {ih:.2f}: {T:.0f} s -> distanza minima {(T + 0.4) * vg:.0f} km')
