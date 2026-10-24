"""
PULSE · Fase A · A5.3 e) — Scarico magnetico delle ruote durante la spinta
==========================================================================
Confronto tra dipoli dei magnetorquer (1,2 / 2,0 / 2,5 A m²) su un giorno di operazioni:
4,2 h di spinta continua e poi solo disturbo aerodinamico.

Modello (primo ordine):
  - orbita circolare SSO, 302 km, inclinazione 96,8°; Terra che ruota
  - campo magnetico: dipolo inclinato di 9,6° (B = 30 µT all'equatore in superficie)
  - assetto fisso in LVLH (X velocità, Z nadir, Y = Z × X); corpo = LVLH
  - disturbo = coppia costante in un asse del corpo (spinta disallineata + aerodinamica,
    D-047) + dipolo residuo 0,1 A m² fisso nel corpo
  - le ruote assorbono la coppia esterna:  dh/dt = T_disturbo + T_magnetica
  - legge di scarico a prodotto vettoriale: m = B × u / |B|², con u = −(T_stimata + K·h),
    limitata per asse a ±m_max (il vettore viene scalato)
  - niente accoppiamenti giroscopici, niente modi di ripresa (F2) durante la spinta
Uscita: momento massimo delle ruote nel giorno, da confrontare con la capacità della piramide W3.
Uso:  python desaturazione.py
"""
import numpy as np

MU = 398600.4418; RE = 6378.137; A = 6680.2; INC = np.radians(96.8)
N = np.sqrt(MU / A**3); WE = 7.2921159e-5
B0 = 3.0e-5; TILT = np.radians(9.6)
DT = 2.0; GIORNO = 86400.0; ORE_SPINTA = 4.2
K = 1.0 / 900.0                       # 1/s: tempo di scarico di ~15 min
M_RES = np.array([0.1, 0.1, 0.1]) / np.sqrt(3)   # dipolo residuo 0,1 A m² (direzione arbitraria)

CAPACITA = {'W3 nominale': 0.163, 'W3 con una ruota guasta': 0.082}
RISERVA_FMC = 0.030                   # da lasciare libera per FMC o slew


def campo_lvlh(t):
    u = N * t                                            # argomento di latitudine
    raan = 0.0
    r_eci = A * np.array([np.cos(raan) * np.cos(u) - np.sin(raan) * np.sin(u) * np.cos(INC),
                          np.sin(raan) * np.cos(u) + np.cos(raan) * np.sin(u) * np.cos(INC),
                          np.sin(u) * np.sin(INC)])
    v_eci = A * N * np.array([-np.cos(raan) * np.sin(u) - np.sin(raan) * np.cos(u) * np.cos(INC),
                              -np.sin(raan) * np.sin(u) + np.cos(raan) * np.cos(u) * np.cos(INC),
                              np.cos(u) * np.sin(INC)])
    th = WE * t                                           # asse del dipolo che ruota con la Terra
    m_hat = -np.array([np.sin(TILT) * np.cos(th), np.sin(TILT) * np.sin(th), np.cos(TILT)])
    r = np.linalg.norm(r_eci); rh = r_eci / r
    B = B0 * (RE / r)**3 * (3 * np.dot(m_hat, rh) * rh - m_hat)
    z = -rh; x = v_eci / np.linalg.norm(v_eci); y = np.cross(z, x)
    return np.array([np.dot(B, x), np.dot(B, y), np.dot(B, z)])


def giorno(m_max, T_spinta, T_aria, asse):
    e = np.zeros(3); e[asse] = 1.0
    h = np.zeros(3); hmax = 0.0; hmax_spinta = 0.0
    for t in np.arange(0.0, GIORNO, DT):
        B = campo_lvlh(t)
        Tc = (T_spinta if t < ORE_SPINTA * 3600 else 0.0) + T_aria
        T_dist = Tc * e + np.cross(M_RES, B)
        u = -(Tc * e + K * h)                             # coppia magnetica desiderata
        m = np.cross(B, u) / np.dot(B, B)
        s = np.abs(m).max() / m_max
        if s > 1: m = m / s
        h = h + (T_dist + np.cross(m, B)) * DT
        hn = np.linalg.norm(h); hmax = max(hmax, hn)
        if t < ORE_SPINTA * 3600: hmax_spinta = max(hmax_spinta, hn)
    return hmax


if __name__ == '__main__':
    casi = [('G2 (D-047): spinta 1,1e-5 + aria 6,9e-6 N m', 1.1e-5, 6.9e-6),
            ('Baricentro a 20 mm (stress R-26): spinta 2,2e-5 + aria 1,4e-5 N m', 2.2e-5, 1.4e-5)]
    nomi_assi = {1: 'beccheggio (Y)', 2: 'imbardata (Z)'}
    print(f'Spazio per i disturbi: W3 nominale {CAPACITA["W3 nominale"]-RISERVA_FMC:.3f} N m s, '
          f'con una ruota guasta {CAPACITA["W3 con una ruota guasta"]-RISERVA_FMC:.3f} N m s\n')
    for nome, Ts, Ta in casi:
        print(nome)
        for asse in (1, 2):
            riga = []
            for m_max in (1.2, 2.0, 2.5):
                riga.append(f'{m_max} A m² → {giorno(m_max, Ts, Ta, asse):.3f}')
            print(f'  coppia su {nomi_assi[asse]}: momento massimo nel giorno  ' + ' | '.join(riga) + ' N m s')
