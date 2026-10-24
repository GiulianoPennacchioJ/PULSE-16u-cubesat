"""
PULSE · Fase A · A5.3 f) — Ripresa diurna: confronto tra classi di giroscopio (GY1 contro GY2)
=============================================================================================
Due prove, a supporto delle decisioni D-050 (giroscopio) e D-040 (correzione a bordo delle bande):

1) Errore del giroscopio sull'angolo relativo (formula):  sigma_theta = ARW * sqrt(T)
   sui tre intervalli che contano: bande colore (0,79 s), TDI a 4 passaggi (0,15 s),
   shift-and-add notturno (0,3 s). Soglie: 2,8 µrad (0,8 m, DR-18), 0,3 pixel PAN, 5,2 µrad (DR-10).

2) Moto VERO del satellite in ripresa diurna (simulazione 1-asse, sim1asse.py):
   assetto fermo in LVLH (velocità orbitale costante), controllo chiuso sul giroscopio,
   star tracker spento. Si misura |errore(t + T) - errore(t)| per T = 0,79 s e 0,15 s
   (99° percentile, caso peggiore su 5 ripetizioni e sull'inviluppo d'inerzia), da
   confrontare con DR-05 (deriva ≤ 0,001°/s, cioè ≤ 13,8 µrad in 0,79 s).

Classi usate nella simulazione (come in sim1asse.py):
  'MEMS'          ARW 0,15°/√h, bias 5°/h    -> classe GY1 (STIM300: 0,15°/√h, 0,3°/h)
  'Alta qualità'  ARW 0,01°/√h, bias 0,5°/h  -> prudente per GY2 (CRH03: 0,006°/√h, 0,04°/h)

Uso:  python ripresa_diurna.py   (richiede sim1asse.py nella stessa cartella)
"""
import numpy as np
import sim1asse as S

H_KM = 302.0
IFOV_PAN = 3.45e-6 / 0.70          # rad
SOGLIA_BANDE = 2.8e-6              # rad in 0,79 s (DR-18)
SOGLIA_TDI = 0.3 * IFOV_PAN        # rad in 0,15 s
SOGLIA_NOTTE = 5.2e-6              # rad in 0,3 s (DR-10)

GIROSCOPI_REALI = {                # ARW in °/√h (datasheet)
    'GY1 · Safran STIM300': 0.15,
    'GY2 · Silicon Sensing CRH03': 0.006,
    'GY3 · KVH 1750': 0.012,
}


def errore_relativo(arw_deg_sqrth, T):
    """sigma_theta = ARW * sqrt(T), in rad."""
    return np.radians(arw_deg_sqrth / 60.0) * np.sqrt(T)


def prova_formula(righe):
    righe.append('1) Errore del giroscopio sull\'angolo relativo, sigma = ARW·√T')
    for nome, arw in GIROSCOPI_REALI.items():
        b = errore_relativo(arw, 0.79); t = errore_relativo(arw, 0.15); n = errore_relativo(arw, 0.30)
        righe.append(f'  {nome} (ARW {arw}°/√h): bande 0,79 s {b*1e6:.2f} µrad = {b*H_KM*1e3:.2f} m '
                     f'[{"ok" if b <= SOGLIA_BANDE*1.01 else "NO"}]; TDI 0,15 s {t/IFOV_PAN:.2f} pixel '
                     f'[{"ok" if t <= SOGLIA_TDI else "NO"}]; notte 0,3 s {n*1e6:.2f} µrad '
                     f'[{"ok" if n <= SOGLIA_NOTTE else "NO"}]')
    arw_max = np.degrees(SOGLIA_BANDE / np.sqrt(0.79)) * 60
    righe.append(f'  ARW massimo per DR-18: {arw_max:.4f}°/√h')


def prova_simulazione(righe, durata=200.0, scarto=30.0, semi=5):
    n = np.sqrt(S.MU / S.A_ORB**3)
    t = np.arange(0.0, durata, S.DT)
    ref = n * t; wr = np.full_like(t, n); ar = np.zeros_like(t)
    i0 = int(round(scarto / S.DT))
    righe.append('\n2) Moto vero in ripresa diurna (simulazione 1-asse, 99° percentile, caso peggiore)')
    for giro in ('MEMS', 'Alta qualità'):
        arw, bias = S.GIROSCOPI[giro]
        for banda in (1.0, 0.3, 0.1):
            peggiore = {0.79: 0.0, 0.15: 0.0}
            for I in S.INERZIE:
                for s in range(semi):
                    err, _, _ = S.simula(ref, wr, ar, I, banda, 10, arw, bias, 2000 + s, S.I_HAT)
                    e = err[i0:]
                    for T in peggiore:
                        k = int(round(T / S.DT))
                        d = np.abs(e[k:] - e[:-k])
                        peggiore[T] = max(peggiore[T], np.percentile(d, 99))
            v79 = peggiore[0.79]; v15 = peggiore[0.15]
            deriva = np.degrees(v79 / 0.79)
            righe.append(f'  {giro:13s} banda {banda:.1f} rad/s: 0,79 s → {v79*1e6:6.1f} µrad ({v79*H_KM*1e3:5.2f} m), '
                         f'deriva equivalente {deriva:.5f}°/s [DR-05 {"ok" if deriva <= 0.001 else "NO"}]; '
                         f'0,15 s → {v15*1e6:5.2f} µrad ({v15/IFOV_PAN:.2f} pixel PAN)')


if __name__ == '__main__':
    import os
    os.makedirs('risultati', exist_ok=True)
    righe = []
    prova_formula(righe)
    prova_simulazione(righe)
    testo = '\n'.join(righe)
    print(testo)
    with open('risultati/ripresa_diurna.txt', 'w', encoding='utf-8') as f:
        f.write(testo + '\n')
