"""PULSE A5.6.2 - Luce ed eclisse sull'orbita di riferimento (D-012).

Calcola, giorno per giorno:
  - deriva dell'ora del nodo discendente (LTDN) con l'inclinazione di bias 96,8 deg
    che cala di ~0,33 deg/anno (MDR, effetto del Sole);
  - angolo beta (Sole rispetto al piano dell'orbita);
  - durata dell'eclisse per orbita (ombra conica: umbra e penombra);
  - posizione dei passaggi sull'Italia rispetto all'eclisse.

Modello: orbita circolare r = a medio (6680,2 km), J2 per la precessione del nodo,
Sole con le formule a bassa precisione dell'Astronomical Almanac, Terra sferica
(R = 6378,137 km), niente atmosfera. Precisione attesa: ~0,1 deg sul beta,
~10 s sull'eclisse. Da verificare con GMAT (EclipseLocator).

Uso: python luce_eclisse.py [anno_inizio]
"""
import sys
import numpy as np

MU = 398600.4418          # km^3/s^2
RE = 6378.137             # km
J2 = 1.08263e-3
RS = 696000.0             # raggio del Sole, km
AU = 149597870.7          # km
A = 6680.2                # km, SMA media (D-012)
I0 = 96.8                 # deg, inclinazione di iniezione con bias (D-012)
DI_DT = -0.33             # deg/anno, deriva dell'inclinazione (MDR); -0,030 dal calcolo in deriva_inclinazione.py
LTDN0 = 10.5              # h, ora del nodo discendente all'inizio (D-012)
ANNI = 2.0                # durata di progetto (D-020)
LAT_ITALIA = (36.6, 42.0, 47.1)   # deg: sud (Pachino), centro, nord (Alto Adige)

N_MOTO = np.sqrt(MU / A**3)                   # rad/s
PERIODO = 2 * np.pi / N_MOTO                  # s
OMEGA_SOLE = 2 * np.pi / (365.2422 * 86400)   # rad/s, moto medio del Sole


def sole(jd):
    """Versore del Sole (ECI, equatore medio) e distanza in km; longitudine media L (deg)."""
    n = jd - 2451545.0
    L = (280.460 + 0.9856474 * n) % 360
    g = np.radians((357.528 + 0.9856003 * n) % 360)
    lam = np.radians(L + 1.915 * np.sin(g) + 0.020 * np.sin(2 * g))
    eps = np.radians(23.439 - 4e-7 * n)
    u = np.array([np.cos(lam), np.cos(eps) * np.sin(lam), np.sin(eps) * np.sin(lam)])
    d = (1.00014 - 0.01671 * np.cos(g) - 0.00014 * np.cos(2 * g)) * AU
    return u, d, L


def raan_rate(i_deg):
    """Precessione del nodo da J2 (rad/s)."""
    return -1.5 * N_MOTO * J2 * (RE / A) ** 2 * np.cos(np.radians(i_deg))


def illuminazione(r_sat, s_dir, s_dist):
    """Frazione del disco solare visibile (1 luce, 0 umbra) con ombra conica."""
    r_sun = s_dir * s_dist
    rel = r_sun[None, :] - r_sat                    # satellite -> Sole
    d_rel = np.linalg.norm(rel, axis=1)
    d_sat = np.linalg.norm(r_sat, axis=1)
    a_s = np.arcsin(RS / d_rel)                     # raggio apparente del Sole
    a_e = np.arcsin(RE / d_sat)                     # raggio apparente della Terra
    cosc = np.einsum('ij,ij->i', -r_sat, rel) / (d_sat * d_rel)
    c = np.arccos(np.clip(cosc, -1, 1))             # distanza angolare dei centri
    f = np.ones(len(r_sat))
    tot = c <= a_e - a_s                            # Sole tutto dietro la Terra
    f[tot] = 0.0
    parz = (c < a_e + a_s) & ~tot
    # area di sovrapposizione di due dischi (approssimazione piana)
    cc, rs, re_ = c[parz], a_s[parz], a_e[parz]
    x = (cc**2 + rs**2 - re_**2) / (2 * cc)
    y = np.sqrt(np.clip(rs**2 - x**2, 0, None))
    area = rs**2 * np.arccos(np.clip(x / rs, -1, 1)) + re_**2 * np.arccos(np.clip((cc - x) / re_, -1, 1)) - cc * y
    f[parz] = 1 - area / (np.pi * rs**2)
    return f


def una_orbita(jd, raan, inc, passo=2.0):
    """Posizioni su un'orbita che parte dal nodo ascendente (u = 0)."""
    t = np.arange(0, PERIODO, passo)
    u = N_MOTO * t
    O, i = np.radians(raan), np.radians(inc)
    r = A * np.column_stack([
        np.cos(O) * np.cos(u) - np.sin(O) * np.sin(u) * np.cos(i),
        np.sin(O) * np.cos(u) + np.cos(O) * np.sin(u) * np.cos(i),
        np.sin(u) * np.sin(i)])
    n_hat = np.array([np.sin(O) * np.sin(i), -np.cos(O) * np.sin(i), np.cos(i)])
    return t, np.degrees(u), r, n_hat


def u_latitudine(lat, inc, ramo):
    """Argomento di latitudine (deg) a cui si passa per una latitudine: ramo 'asc' o 'disc'."""
    s = np.sin(np.radians(lat)) / np.sin(np.radians(inc))
    u = np.degrees(np.arcsin(s))
    return u if ramo == 'asc' else 180 - u


def main(anno=2026, di_dt=DI_DT):
    jd0 = 2451544.5 + (anno - 2000) * 365.25 + 0.5   # ~1 gennaio dell'anno, 12:00 TT
    jd0 = np.floor(jd0) + 0.5
    giorni = np.arange(0, int(ANNI * 365.25) + 1)
    _, _, L0 = sole(jd0)
    # RAAN iniziale: nodo ascendente alle LTDN0 + 12 h (ora locale media)
    raan = (L0 + (LTDN0 + 12 - 12) * 15) % 360
    righe = []
    for g in giorni:
        jd = jd0 + g
        anni = g / 365.25
        inc = I0 + di_dt * anni
        s_dir, s_dist, L = sole(jd)
        ltan = 12 + ((raan - L + 540) % 360 - 180) / 15
        ltdn = (ltan - 12) % 24
        t, u, r, n_hat = una_orbita(jd, raan, inc)
        beta = np.degrees(np.arcsin(n_hat @ s_dir))
        f = illuminazione(r, s_dir, s_dist)
        dt = t[1] - t[0]
        umbra = np.sum(f == 0) * dt / 60
        penombra = np.sum((f > 0) & (f < 1)) * dt / 60
        ombra = umbra + penombra
        # ingresso e uscita dall'ombra (argomento di latitudine)
        buio = f < 1
        if buio.any():
            idx = np.where(buio)[0]
            # l'arco buio puo' attraversare u = 0: lo ricostruisco come intervallo continuo
            # trova inizio dell'arco: primo campione buio dopo un campione in luce
            trans_in = np.where(buio & ~np.roll(buio, 1))[0]
            trans_out = np.where(~buio & np.roll(buio, 1))[0]
            u_in, u_out = u[trans_in[0]], u[trans_out[0]]
        else:
            u_in = u_out = np.nan
        righe.append((g, inc, ltdn, beta, umbra, penombra, ombra, u_in, u_out))
        # precessione del nodo nel giorno
        raan = (raan + np.degrees(raan_rate(inc)) * 86400) % 360
    return np.array(righe)


def riassunto(R, anno, di_dt):
    g, inc, ltdn, beta, umbra, pen, ombra, u_in, u_out = R.T
    per = PERIODO / 60
    out = []
    p = out.append
    p("PULSE A5.6.2 - Luce ed eclisse (orbita D-012, inizio 1/1/%d, %.1f anni, di/dt = %+.3f deg/anno)" % (anno, ANNI, di_dt))
    p("Periodo orbitale: %.2f min; orbite al giorno: %.2f" % (per, 1440 / per))
    p("Precessione J2 a i = 96,68 deg: %.4f deg/giorno (Sole medio 0,9856)" % (np.degrees(raan_rate(96.68)) * 86400))
    p("")
    p("Deriva dell'ora del nodo discendente (LTDN), inclinazione %.1f -> %.2f deg:" % (inc[0], inc[-1]))
    for anni in (0, 0.5, 1.0, 1.5, 2.0):
        k = min(int(anni * 365.25), len(g) - 1)
        h = ltdn[k]
        p("  dopo %.1f anni: LTDN %02d:%02d (i = %.2f deg)" % (anni, int(h), round((h % 1) * 60) % 60, inc[k]))
    k_max = np.argmax(np.abs(ltdn - 10.5))
    p("  scostamento massimo da 10:30: %+.0f min (giorno %d)" % ((ltdn[k_max] - 10.5) * 60, g[k_max]))
    p("")
    p("Angolo beta: da %.1f a %.1f deg (|beta| medio %.1f)" % (beta.min(), beta.max(), np.abs(beta).mean()))
    p("Ombra per orbita (umbra + penombra): min %.1f  max %.1f  media %.1f min" % (ombra.min(), ombra.max(), ombra.mean()))
    p("  di cui penombra: %.2f-%.2f min (trascurabile per la potenza)" % (pen.min(), pen.max()))
    p("Luce per orbita: min %.1f  max %.1f min; frazione di luce %.1f-%.1f %%" % (
        per - ombra.max(), per - ombra.min(), 100 * (1 - ombra.max() / per), 100 * (1 - ombra.min() / per)))
    p("Orbite senza eclisse: %d giorni su %d" % (np.sum(ombra == 0), len(g)))
    p("Ore di luce al giorno: %.1f-%.1f h; ore di buio %.1f-%.1f h" % (
        (per - ombra.max()) / per * 24, (per - ombra.min()) / per * 24, ombra.min() / per * 24, ombra.max() / per * 24))
    p("")
    p("Per mese (primo anno / secondo anno): beta medio, ombra media per orbita")
    mesi = ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"]
    for m in range(12):
        sel1 = (g >= m * 30.44) & (g < (m + 1) * 30.44)
        sel2 = (g >= 365.25 + m * 30.44) & (g < 365.25 + (m + 1) * 30.44)
        s2 = " %5.1f deg %5.1f min" % (beta[sel2].mean(), ombra[sel2].mean()) if sel2.any() else ""
        p("  %s  %5.1f deg %5.1f min  |%s" % (mesi[m], beta[sel1].mean(), ombra[sel1].mean(), s2))
    p("")
    # posizione dei passaggi sull'Italia: arco d'ombra in u (centro tra ingresso e uscita)
    p("Passaggi sull'Italia rispetto all'eclisse (u = argomento di latitudine, 0 = nodo ascendente):")
    p("  ingresso nell'ombra u = %.0f-%.0f deg, uscita u = %.0f-%.0f deg" % (
        np.nanmin(u_in), np.nanmax(u_in), np.nanmin(u_out), np.nanmax(u_out)))
    for nome, ramo in (("giorno (ramo discendente)", 'disc'), ("notte (ramo ascendente)", 'asc')):
        p("  %s:" % nome)
        for lat in LAT_ITALIA:
            uu = u_latitudine(lat, 96.68, ramo)
            # minuti dall'uscita dall'ombra (luce) o dall'ingresso (buio)
            d_out = ((uu - u_out) % 360) / 360 * per
            d_in = ((uu - u_in) % 360) / 360 * per
            if ramo == 'disc':
                p("    lat %4.1f N: u = %5.1f deg, %4.1f-%4.1f min dopo l'uscita dall'ombra, %4.1f-%4.1f min prima del prossimo ingresso" % (
                    lat, uu, d_out.min(), d_out.max(), (per - d_in).min(), (per - d_in).max()))
            else:
                p("    lat %4.1f N: u = %5.1f deg, %4.1f-%4.1f min dopo l'ingresso nell'ombra, %4.1f-%4.1f min prima dell'uscita" % (
                    lat, uu, d_in.min(), d_in.max(), (ombra - d_in).min(), (ombra - d_in).max()))
    return "\n".join(out)


if __name__ == "__main__":
    import os
    anno = int(sys.argv[1]) if len(sys.argv) > 1 else 2026
    os.makedirs("risultati", exist_ok=True)
    for nome, di in (("MDR", -0.33), ("calcolata", -0.030)):
        R = main(anno, di)
        testo = riassunto(R, anno, di)
        print(testo + "\n")
        with open("risultati/luce_eclisse_%s.txt" % nome, "w") as fh:
            fh.write(testo + "\n")
        np.savetxt("risultati/luce_eclisse_%s.csv" % nome, R, delimiter=",", fmt="%.4f",
                   header="giorno,inclinazione_deg,LTDN_h,beta_deg,umbra_min,penombra_min,ombra_min,u_ingresso_deg,u_uscita_deg")
