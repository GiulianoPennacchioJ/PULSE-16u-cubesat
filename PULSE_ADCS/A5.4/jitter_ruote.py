"""
PULSE · Fase A · A5.4.5 — Jitter delle ruote di reazione: stima di primo ordine (corpo rigido)
============================================================================================

Una ruota sbilanciata che gira a velocità Ω produce:
  - una forza   F = Us·Ω²   (sbilanciamento statico Us, in kg·m)
  - una coppia  T = Ud·Ω²   (sbilanciamento dinamico Ud, in kg·m²)
Sul satellite rigido (inerzia I, ruota a distanza d dal baricentro) l'oscillazione
d'assetto alla frequenza della ruota ha ampiezza
      θ = (Ud + Us·d) / I
che NON dipende dalla velocità (la coppia cresce con Ω², la risposta di un corpo
libero cala con 1/Ω²). È il valore "di base"; una risonanza della struttura
(telescopio, pannelli) alla stessa frequenza lo moltiplica per il fattore Q.

Confronto con DR-02 (D-053): ampiezza ≤ 0,15 pixel PAN = 0,74 µrad.
Le 4 ruote girano a velocità diverse: somma quadratica (RSS) come stima tipica,
somma lineare come caso peggiore (picchi allineati).

Dati di sbilanciamento (pubblici):
  - CubeSpace CubeWheel Large (Gen 1, 30 mN·m·s): Us < 0,06 g·mm, Ud < 5 g·mm²
  - CubeSpace CW1200 (0,12 N·m·s, classe di W3): Ud < 6,5 g·mm² (Us non dichiarato), 8600 giri/min max
  - NASA GSFC, ruote CubeSat: obiettivo Us < 1,5 g·mm, Ud < 20 g·mm²;
    prototipo con albero 11 g·mm / 52 g·mm²
  - Vectronic VRW-C-05 (0,6 N·m·s, più grande): Us < 3 g·mm, Ud < 100 g·mm²
BCT RWp100 (riferimento D-048): sbilanciamento non pubblicato.
Uso: python jitter_ruote.py > risultati/jitter_ruote.txt
"""
import numpy as np

I_MIN = 0.64                         # inerzia trasversale minima (kg m^2), D-043
LIMITE = 0.15 * 3.45e-6 / 0.70       # DR-02, ampiezza (rad)
CASI = [('ben bilanciata (CubeWheel Large)', 0.06, 5.0),
        ('classe W3 con Us prudente (CW1200 + Us 0,5)', 0.5, 6.5),
        ('obiettivo NASA GSFC CubeSat', 1.5, 20.0),
        ('ruota grande (VRW-C-05)', 3.0, 100.0),
        ('prototipo non bilanciato (GSFC, albero)', 11.0, 52.0)]
DIST = (0.05, 0.10, 0.15)            # distanza ruota-baricentro (m)


def theta(us_gmm, ud_gmm2, d, I=I_MIN):
    return (ud_gmm2 * 1e-9 + us_gmm * 1e-6 * d) / I


def main():
    print(f'Limite DR-02: {LIMITE*1e6:.2f} µrad di ampiezza; inerzia {I_MIN} kg·m²\n')
    print('Ampiezza per ruota e per 4 ruote (RSS | somma lineare), µrad:')
    for nome, us, ud in CASI:
        parti = []
        for d in DIST:
            t1 = theta(us, ud, d)
            parti.append(f'd={d*100:.0f} cm: {t1*1e6:.3f} / {2*t1*1e6:.2f} | {4*t1*1e6:.2f}')
        print(f'  {nome:<45} Us {us} g·mm, Ud {ud} g·mm²  ->  ' + ';  '.join(parti))
    print('\nFattore di risonanza Q ammesso prima di superare DR-02 (4 ruote RSS, d = 10 cm):')
    for nome, us, ud in CASI:
        q = LIMITE / (2 * theta(us, ud, 0.10))
        print(f'  {nome:<45} Q ≤ {q:.1f}')
    print('\nSbilanciamento statico massimo per ruota per rispettare DR-02 con Q = 1 e Ud = 10 g·mm²:')
    for d in DIST:
        for regola, n in (('RSS', 2.0), ('lineare', 4.0)):
            us_max = (LIMITE / n * I_MIN - 10e-9) / d * 1e6
            print(f'  d = {d*100:.0f} cm, somma {regola}: Us ≤ {us_max:.2f} g·mm')
    # dentro una riga (0,2 ms) e dentro uno scatto notturno (20 ms)
    f_max = 8600 / 60
    print(f'\nA {f_max:.0f} Hz (8600 giri/min): in una riga da 0,2 ms il moto è al massimo '
          f'{2*np.pi*f_max*0.2e-3:.3f} × ampiezza; in uno scatto da 20 ms fino a 2 × ampiezza picco-picco')


if __name__ == '__main__':
    main()
