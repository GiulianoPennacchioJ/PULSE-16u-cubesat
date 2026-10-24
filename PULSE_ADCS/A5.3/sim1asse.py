"""
PULSE · Fase A · A5.3 c) — Simulazione 1-asse (beccheggio) della FMC notturna
==============================================================================

Cosa simula
-----------
Il satellite, visto come un corpo rigido che ruota solo attorno all'asse di
beccheggio, deve tenere il telescopio puntato su un bersaglio a terra mentre
passa sopra di esso (FMC, Forward Motion Compensation). Il moto è controllato
da una ruota di reazione; l'assetto è stimato integrando un giroscopio rumoroso.

Catena simulata (anello chiuso), a passo DT = 1 ms:

    guida (linea di vista) -> controllo PD + anticipo di coppia -> ruota (ritardo)
        -> dinamica  I * dw/dt = coppia ruota + disturbo
        -> giroscopio (rumore + bias) -> stima d'assetto -> controllo ...

Profili di guida (decisione D-044):
  F2  inseguimento continuo dal bordo della finestra a 30° (nominale)
  F1  colpo rapido: assetto fisso, rampa a coppia costante, aggancio alla linea
      di vista 2 s prima del passaggio sul bersaglio (caso di stress)

Uscite per ogni caso (peggiore su 5 ripetizioni con rumore diverso):
  - mosso di ogni scatto da 20 ms sul moto VERO (picco-picco dell'errore di
    puntamento), confrontato con 5,2 µrad (DR-10, D-030)
  - errore di puntamento massimo APE (DR-15, 0,1°)
  - coppia e momento della ruota di picco
  - per F1: tempo dopo l'aggancio per avere 0,36 s di scatti buoni (DR-11)

Ipotesi (approvate in chat il 24/10/2026, registro D-039, D-043, D-044):
  - orbita circolare a 302 km, Terra sferica non rotante, bersaglio sotto la
    traccia (geometria piana nel piano dell'orbita)
  - inerzia vera 0,64 o 1,14 kg m^2 (inviluppo D-043); il controllore usa
    l'inerzia nominale 0,69 kg m^2 (32 kg, caso pieno)
  - ruota di prova classe EarthNext: 7 mN m, 0,1 N m s, ritardo 20 ms (TBC)
  - giroscopio di classe: MEMS (ARW 0,15°/sqrt(h), bias 5°/h) e alta qualità
    (0,01°/sqrt(h), 0,5°/h) — valori tipici, da verificare su datasheet in A5.3 f)
  - star tracker spento durante l'inseguimento (caso peggiore)
  - disturbo costante 1e-5 N m (EarthNext, Tab. 4), da aggiornare in A5.3 d)

Limiti noti (da superare con la 3-assi in Fase B):
  - nessun accoppiamento tra gli assi, nessun prodotto d'inerzia
  - nessun modo flessibile (pannelli), nessun jitter delle ruote
  - bias del giroscopio costante nella finestra, rumore bianco
  - ruota modellata come ritardo del primo ordine, senza quantizzazione

Uso:
    pip install numpy matplotlib numba      (numba facoltativo, ma ~100x più veloce)
    python sim1asse.py                      -> risultati/sim1asse_risultati.csv
                                               risultati/sim1asse_esempio.png
"""
import csv
import itertools
import os

import numpy as np

try:
    from numba import njit
except ImportError:                         # senza numba funziona lo stesso, più lento
    def njit(*args, **kwargs):
        return (lambda f: f) if not (args and callable(args[0])) else args[0]

# ---------------------------------------------------------------- parametri
MU = 398600.4418          # km^3/s^2
RE = 6378.137             # km
A_ORB = 6680.2            # semiasse maggiore medio (km) -> ~302 km (D-012)

DT = 1e-3                 # passo d'integrazione (s)
FRAME = 0.020             # durata di uno scatto notturno (s), D-030
SMEAR_MAX = 5.2e-6        # mosso ammesso per scatto (rad), DR-10
N_FRAMES_OK = 18          # 18 scatti x 20 ms = 0,36 s, DR-11

TAU_W = 0.020             # ritardo della ruota (s), ipotesi TBC
T_MAX = 0.007             # coppia massima ruota di prova (N m)
H_MAX = 0.1               # momento massimo ruota di prova (N m s)
D_DIST = 1e-5             # disturbo costante (N m)
I_HAT = 0.69              # inerzia nominale usata dal controllore (kg m^2)
ZETA = 0.7                # smorzamento del controllo

INERZIE = (0.64, 1.14)    # inviluppo D-043 (kg m^2)
BANDE = (0.3, 1.0)        # banda del controllo (rad/s)
FREQ_CONTROLLO = (10, 50) # aggiornamento del controllo (Hz)
SEMI = 5                  # ripetizioni con rumore diverso

GIROSCOPI = {             # (ARW in rad/sqrt(s), bias in rad/s)
    'MEMS':         (np.radians(0.15) / 60, np.radians(5.0) / 3600),
    'Alta qualità': (np.radians(0.01) / 60, np.radians(0.5) / 3600),
}

PROFILI = [               # (nome, coppia di rampa N m, istante di aggancio s)
    ('F2', None, None),
    ('F1', 3e-3, -2.0),
    ('F1', 7e-3, -2.0),
]


# ---------------------------------------------------------------- guida
def linea_di_vista(t, a=A_ORB):
    """Angolo inerziale (rad) della linea di vista satellite -> bersaglio.
    Il satellite passa sopra il bersaglio a t = 0."""
    n = np.sqrt(MU / a**3)
    sx, sy = a * np.cos(n * t), a * np.sin(n * t)
    return np.unwrap(np.arctan2(-sy, RE - sx))


def riferimento(nome, coppia_rampa, t_aggancio, t, a=A_ORB):
    """Restituisce angolo, velocità e accelerazione di riferimento."""
    psi = linea_di_vista(t, a)
    w = np.gradient(psi, DT)
    al = np.gradient(w, DT)
    if nome == 'F2':
        return psi, w, al
    # F1: assetto fisso in LVLH (velocità orbitale n), poi rampa con
    # accelerazione costante calcolata sull'inerzia NOMINALE, fino ad agganciare
    # angolo e velocità della linea di vista all'istante t_aggancio.
    n = np.sqrt(MU / a**3)
    j = int(round((t_aggancio - t[0]) / DT))
    alpha = coppia_rampa / I_HAT
    durata = (w[j] - n) / alpha
    t_inizio = t_aggancio - durata
    th0 = psi[j] - n * durata - 0.5 * alpha * durata**2
    ref, wr, ar = psi.copy(), w.copy(), al.copy()
    for k in range(j):
        if t[k] < t_inizio:
            ref[k] = th0 + n * (t[k] - t_inizio); wr[k] = n; ar[k] = 0.0
        else:
            tau = t[k] - t_inizio
            ref[k] = th0 + n * tau + 0.5 * alpha * tau**2
            wr[k] = n + alpha * tau
            ar[k] = alpha
    return ref, wr, ar


# ---------------------------------------------------------------- anello chiuso
@njit(cache=True)
def simula(ref, wr, ar, I, banda, fc, arw, bias, seme, ihat):
    np.random.seed(seme)
    N = ref.size
    Kp = ihat * banda * banda            # guadagni da banda e smorzamento
    Kd = 2.0 * ZETA * ihat * banda
    nc = int(round(1.0 / (fc * DT)))     # passi d'integrazione per ciclo di controllo
    Tc = nc * DT
    sigma = arw / np.sqrt(Tc)            # rumore del giroscopio mediato su Tc

    th = ref[0]; w = wr[0]               # stato vero: parte agganciato e fermo sull'errore
    u = 0.0; uc = 0.0                    # coppia della ruota, coppia comandata
    th_est = th; somma_w = 0.0           # stima d'assetto (solo giroscopio)
    H = 0.0                              # momento totale (cresce solo per il disturbo)
    errore = np.empty(N); coppia = np.empty(N); h_ruota = np.empty(N)
    for k in range(N):
        if k % nc == 0:                  # ciclo di controllo
            w_mis = (somma_w / nc if k > 0 else w) + bias + sigma * np.random.randn()
            somma_w = 0.0
            if k > 0:
                th_est += w_mis * Tc
            uc = ihat * ar[k] + Kp * (ref[k] - th_est) + Kd * (wr[k] - w_mis)
            uc = min(max(uc, -T_MAX), T_MAX)
        u += (uc - u) * DT / TAU_W       # ruota: ritardo del primo ordine
        w += (u + D_DIST) / I * DT       # dinamica:  I dw/dt = coppia + disturbo
        th += w * DT
        somma_w += w
        H += D_DIST * DT
        errore[k] = th - ref[k]
        coppia[k] = u
        h_ruota[k] = H - I * w           # momento della ruota = totale - corpo
    return errore, coppia, h_ruota


def mosso_per_scatto(errore, i0, i1):
    """Picco-picco dell'errore di puntamento in ogni scatto da 20 ms."""
    m = int(round(FRAME / DT))
    nf = (i1 - i0) // m
    e = errore[i0:i0 + nf * m].reshape(nf, m)
    return e.max(1) - e.min(1)


def caso(nome, coppia_rampa, t_aggancio, I, banda, fc, giroscopio, a=A_ORB, ihat=I_HAT, semi=SEMI):
    if nome == 'F2':
        t = np.arange(-23.85, 23.85, DT)             # finestra entro 30° off-nadir
    else:
        t = np.arange(-40.0, 3.0, DT)
    ref, wr, ar = riferimento(nome, coppia_rampa, t_aggancio, t, a)
    arw, b = GIROSCOPI[giroscopio]
    peggiore = {}
    for s in range(semi):
        segno = 1 if s % 2 == 0 else -1
        err, cop, hw = simula(ref, wr, ar, I, banda, fc, arw, segno * b, 1000 + s, ihat)
        r = {'coppia_max_Nm': np.abs(cop).max(), 'momento_max_Nms': np.abs(hw).max()}
        if nome == 'F2':
            i0 = int(round((-20.0 - t[0]) / DT)); i1 = int(round((20.0 - t[0]) / DT))
            sm = mosso_per_scatto(err, i0, i1)
            r.update(mosso_p99_urad=np.percentile(sm, 99) * 1e6,
                     mosso_max_urad=sm.max() * 1e6,
                     scatti_fuori_soglia=(sm > SMEAR_MAX).mean(),
                     ape_max_deg=np.degrees(np.abs(err[i0:i1]).max()))
        else:
            j = int(round((t_aggancio - t[0]) / DT))
            sm = mosso_per_scatto(err, j, len(t))
            ok = sm < SMEAR_MAX
            t_ok = np.nan
            for q in range(len(ok) - N_FRAMES_OK + 1):
                if ok[q:q + N_FRAMES_OK].all():
                    t_ok = q * FRAME; break
            r.update(tempo_assestamento_s=t_ok,
                     ape_max_deg=np.degrees(np.abs(err[j:]).max()))
        for k, v in r.items():           # tengo il caso peggiore sulle ripetizioni
            if k == 'tempo_assestamento_s':
                peggiore[k] = np.nan if (np.isnan(v) or np.isnan(peggiore.get(k, 0.0))) else max(v, peggiore.get(k, 0.0))
            else:
                peggiore[k] = max(v, peggiore.get(k, -np.inf))
    peggiore['ruota_satura_in_momento'] = peggiore['momento_max_Nms'] > H_MAX
    return peggiore, t, ref


def figura_esempio(percorso):
    """Errore di puntamento nel tempo: F2 nominale contro F2 con banda bassa."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    t = np.arange(-23.85, 23.85, DT)
    ref, wr, ar = riferimento('F2', None, None, t)
    arw, b = GIROSCOPI['MEMS']
    fig, ax = plt.subplots(figsize=(8, 4))
    for banda, col in ((1.0, '#1f6fb2'), (0.3, '#c0392b')):
        err, _, _ = simula(ref, wr, ar, 1.14, banda, 10, arw, b, 1000, I_HAT)
        ax.plot(t, np.degrees(err), color=col, lw=1, label=f'banda {banda:.1f} rad/s'.replace('.', ','))
    ax.axhline(0.1, color='0.4', ls='--', lw=0.8); ax.axhline(-0.1, color='0.4', ls='--', lw=0.8)
    ax.set_xlabel('tempo dal passaggio sul bersaglio (s)')
    ax.set_ylabel('errore di puntamento (°)')
    ax.set_title('F2, inerzia vera 1,14 kg·m² (controllore: 0,69), giroscopio MEMS')
    ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(percorso, dpi=150)


def main():
    os.makedirs('risultati', exist_ok=True)
    righe = []
    for (nome, cr, ta), I, banda, giro, fc in itertools.product(PROFILI, INERZIE, BANDE, GIROSCOPI, FREQ_CONTROLLO):
        r, _, _ = caso(nome, cr, ta, I, banda, fc, giro)
        riga = {'profilo': nome if cr is None else f'{nome} {cr:.0e} N m', 'inerzia_vera': I,
                'inerzia_controllore': I_HAT, 'banda_rad_s': banda, 'giroscopio': giro,
                'controllo_Hz': fc, **r}
        righe.append(riga)
        print({k: (round(v, 6) if isinstance(v, float) else v) for k, v in riga.items()})
    campi = sorted({k for r in righe for k in r}, key=lambda k: list(righe[0]).index(k) if k in righe[0] else 99)
    with open('risultati/sim1asse_risultati.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=campi); w.writeheader(); w.writerows(righe)
    figura_esempio('risultati/sim1asse_esempio.png')


if __name__ == '__main__':
    main()
