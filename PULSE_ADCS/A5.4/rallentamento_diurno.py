"""
PULSE · Fase A · A5.4.4 (GNC) — Valutazione di D-096: rallentamento della scena in ripresa diurna
==================================================================================================
Proposta di Giuseppe (D-096, DR-56): durante ogni scena diurna il satellite ruota all'indietro in
beccheggio a metà della velocità della linea di vista (rispetto al riferimento orbitale), così il
terreno scorre sul sensore a metà velocità (fattore 2).

Riusa il modello 1-asse di A5.3 (stessa dinamica, ruota con ritardo 20 ms, controllo PD + anticipo
di coppia, banda 1 rad/s a 10 Hz come D-046, giroscopio GY2 "Alta qualità") e aggiunge:
  - un fattore di scala del giroscopio (errore relativo sulla velocità misurata), che con la
    rotazione diventa importante per la conoscenza dell'assetto;
  - l'uscita dell'errore di STIMA (assetto stimato - vero), che serve al riallineamento delle bande.

Profilo (beccheggio rispetto al riferimento orbitale, scena centrata sul bersaglio):
  rampa d'ingresso (polinomio di 5° grado, da fermo a  +ω_s·T/2, velocità -ω_s)
  -> tratto a velocità costante -ω_s per la durata della ripresa T
  -> rampa d'uscita (verso l'assetto fisso o dentro lo slew successivo)
Due modi di fare le rampe:
  R1 rampe separate, coppia pianificata ≤ 1 mN·m (regola di D-045) o ≤ 3 mN·m (livello F1, D-044)
  R2 rampa dentro lo slew di 60 s verso il bersaglio (beccheggio in parallelo al rollio)

Metriche dall'inizio del tratto costante:
  assestamento = ultimo istante con |errore| ≥ 0,1° (DR-15) o deriva su 0,79 s ≥ 0,001°/s (DR-05)
  in scena: deriva vera massima, errore massimo, errore di stima sull'intervallo tra le bande
  (2,8 µrad, DR-18), coppia e momento della ruota.
Casi: inerzia vera 0,64 / 1,14 kg·m², controllore con inerzia stimata ±10% e nominale 0,69;
5 ripetizioni, caso peggiore.
Uso: python rallentamento_diurno.py > risultati/rallentamento_diurno.txt
"""
import os
import sys

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'A5.3'))
sys.path.insert(0, QUI)
from sim1asse import DT, MU, A_ORB, RE, TAU_W, T_MAX, D_DIST, ZETA, GIROSCOPI, linea_di_vista, njit  # noqa: E402
from assestamento import quintica  # noqa: E402

N = np.sqrt(MU / A_ORB**3)
VG = 7.375                    # velocità al suolo (km/s), A5.3 rotazione.py
APE = np.radians(0.1)         # DR-15
DERIVA = np.radians(0.001)    # DR-05
SOGLIA_DR18 = 2.8e-6          # rad sull'intervallo tra le bande (DR-18)
T_SCENA0 = 1.30               # s, scena 9,6 km lungo traccia senza rallentamento (D-096)
T_BANDE0 = 0.79               # s, ritardo PAN -> ultima banda senza rallentamento (A2, A5.3)
K = 2.0                       # fattore di rallentamento (D-096)
IHAT_PIANO = 1.254            # inerzia stimata peggiore (1,14 +10%) per pianificare le rampe
SEMI = 5
ARW, BIAS = GIROSCOPI['Alta qualità']


@njit(cache=True)
def simula_sf(ref, wr, ar, I, banda, fc, arw, bias, sf, seme, ihat):
    """Come sim1asse.simula, con fattore di scala del giroscopio e uscita dell'errore di stima."""
    np.random.seed(seme)
    n = ref.size
    Kp = ihat * banda * banda
    Kd = 2.0 * ZETA * ihat * banda
    nc = int(round(1.0 / (fc * DT)))
    Tc = nc * DT
    sigma = arw / np.sqrt(Tc)
    th = ref[0]; w = wr[0]; u = 0.0; uc = 0.0
    th_est = th; somma_w = 0.0; H = 0.0
    err = np.empty(n); err_st = np.empty(n); coppia = np.empty(n); hr = np.empty(n)
    for k in range(n):
        if k % nc == 0:
            w_vera = somma_w / nc if k > 0 else w
            w_mis = (1.0 + sf) * w_vera + bias + sigma * np.random.randn()
            somma_w = 0.0
            if k > 0:
                th_est += w_mis * Tc
            uc = ihat * ar[k] + Kp * (ref[k] - th_est) + Kd * (wr[k] - w_mis)
            uc = min(max(uc, -T_MAX), T_MAX)
        u += (uc - u) * DT / TAU_W
        w += (u + D_DIST) / I * DT
        th += w * DT
        somma_w += w
        H += D_DIST * DT
        err[k] = th - ref[k]
        err_st[k] = (th_est - th) if k % nc == 0 else np.nan   # solo agli istanti di controllo
        coppia[k] = u
        hr[k] = H - I * w
    return err, err_st, coppia, hr


def durata_rampa(x0, v0, x1, v1, t_piano, ihat=IHAT_PIANO):
    """Durata minima del polinomio di 5° grado con coppia pianificata ≤ t_piano."""
    for T in np.arange(1.0, 200.0, 0.1):
        tau = np.linspace(0, T, 2001)
        _, _, a = quintica(T, x0, v0, 0.0, x1, v1, 0.0, tau)
        if np.abs(a).max() * ihat <= t_piano:
            return T
    return np.nan


def profilo(om, T_rip, T_in, T_out, dopo=15.0, libero=True):
    """Riferimento inerziale di beccheggio: rampa d'ingresso, tratto costante (T_rip + dopo), rampa d'uscita.
    libero=True (R1): si parte da un assetto fisso già inclinato in avanti e si finisce inclinati indietro,
    scelti in modo che la velocità cambi in modo simmetrico (rampa più corta).
    libero=False (R2): la rampa parte dall'assetto dello slew (beccheggio 0) e dura quanto lo slew.
    Restituisce t, ref, wr, ar; t = 0 è l'inizio del tratto costante."""
    x0 = om * T_rip / 2
    T_c = T_rip + dopo
    xs = x0 + om * T_in / 2 if libero else 0.0
    xe = x0 - om * T_c - om * T_out / 2 if libero else 0.0
    t = np.arange(-T_in - 2.0, T_c + T_out + 2.0, DT)
    x = np.full_like(t, xs); v = np.zeros_like(t); a = np.zeros_like(t)
    m = (t >= -T_in) & (t < 0)
    x[m], v[m], a[m] = quintica(T_in, xs, 0, 0, x0, -om, 0, t[m] + T_in)
    m = (t >= 0) & (t < T_c)
    x[m] = x0 - om * t[m]; v[m] = -om
    m = t >= T_c
    x[m] = xe
    m = (t >= T_c) & (t < T_c + T_out)
    x[m], v[m], a[m] = quintica(T_out, x0 - om * T_c, -om, 0, xe, 0, 0, t[m] - T_c)
    return t, N * t + np.pi + x, N + v, a


def metriche(t, err, err_st, T_rip, T_b, dopo=15.0):
    i0 = int(np.searchsorted(t, 0.0))
    lag = int(round(T_BANDE0 / DT))
    e = err[i0:i0 + int(round((T_rip + dopo) / DT))]
    drift = np.abs(e[lag:] - e[:-lag]) / T_BANDE0
    bad = np.where((drift >= DERIVA) | (np.abs(e[lag:]) >= APE))[0]
    t_ass = 0.0 if bad.size == 0 else (bad[-1] + 1) * DT
    j0 = i0 + int(round(t_ass / DT)); j1 = j0 + int(round(T_rip / DT))
    es = err[j0:j1]
    d_scena = np.percentile(np.abs(es[lag:] - es[:-lag]) / T_BANDE0, 99)
    s = err_st[j0:j1]; s = s[~np.isnan(s)]          # un campione ogni 0,1 s (controllo a 10 Hz)
    lb = int(round(T_b / 0.1))
    kb = np.abs(s[lb:] - s[:-lb]) if s.size > lb else np.array([np.nan])
    return t_ass, np.degrees(d_scena), np.degrees(np.abs(es).max()), np.percentile(kb, 99), kb.max()


def caso(om, T_rip, T_in, T_out, I, ihat, sf=0.0, libero=True):
    t, ref, wr, ar = profilo(om, T_rip, T_in, T_out, libero=libero)
    p = dict(t_ass=0.0, deriva=0.0, ape=0.0, kb99=0.0, kbmax=0.0, cop=0.0, h=0.0)
    for s in range(SEMI):
        sg = 1 if s % 2 == 0 else -1
        err, est, cop, hw = simula_sf(ref, wr, ar, I, 1.0, 10, ARW, sg * BIAS, sf, 3000 + s, ihat)
        ta, dd, ap, k99, kmx = metriche(t, err, est, T_rip, K * T_BANDE0)
        fino = t < T_rip + 15.0          # coppia e momento fino alla fine del tratto costante
        cop = cop[fino]; hw = hw[fino]
        for k, v in zip(('t_ass', 'deriva', 'ape', 'kb99', 'kbmax', 'cop', 'h'),
                        (ta, dd, ap, k99, kmx, np.abs(cop).max(), np.abs(hw).max())):
            p[k] = max(p[k], v)
    return p


def scene_per_passaggio(spaziature):
    """Stessa stima di primo ordine di PULSE_TTC/A5.5/scene_diurne.py (D-072), con spaziatura variabile."""
    from matplotlib.path import Path
    Re = 6378.137; a = Re + 302; n = np.sqrt(398600.4418 / a**3); inc = np.radians(96.8); wE = 7.2921159e-5
    pts = np.array([(46.5, 7.0), (47.0, 10.5), (46.6, 13.7), (45.6, 13.8), (44.0, 12.6), (41.9, 16.1), (40.1, 18.5),
                    (39.0, 17.1), (38.0, 15.6), (36.7, 15.1), (37.5, 12.4), (38.2, 12.7), (38.9, 8.4), (41.2, 8.2),
                    (41.3, 9.6), (40.5, 9.8), (43.8, 10.2), (44.2, 8.0), (44.5, 6.8)])
    P = Path(pts[:, [1, 0]])
    lon, lat = np.meshgrid(np.arange(6.5, 18.6, 0.25), np.arange(36.5, 47.1, 0.25))
    g = np.c_[lon.ravel(), lat.ravel()]; g = np.radians(g[P.contains_points(g)])
    gx = np.cos(g[:, 1]) * np.cos(g[:, 0]); gy = np.cos(g[:, 1]) * np.sin(g[:, 0]); gz = np.sin(g[:, 1])
    dt = 10.0; t = np.arange(0, 30 * 86400, dt); wS = 2 * np.pi / (365.2422 * 86400)
    u = n * t; Om = -(wE - wS) * t
    x = np.cos(Om) * np.cos(u) - np.sin(Om) * np.sin(u) * np.cos(inc)
    y = np.sin(Om) * np.cos(u) + np.cos(Om) * np.sin(u) * np.cos(inc)
    z = np.sin(u) * np.sin(inc)
    desc = np.cos(u) * np.sin(inc) < 0
    reach = ((np.outer(x, gx) + np.outer(y, gy) + np.outer(z, gz)) > np.cos(310 / Re)).any(axis=1)
    idx = np.where(reach & desc)[0]
    passes = []; cur = [idx[0]]
    for k in idx[1:]:
        if k - cur[-1] > 6:
            passes.append(cur); cur = [k]
        else:
            cur.append(k)
    passes.append(cur)
    L = np.array([(p[-1] - p[0]) * dt * n * Re for p in passes])
    days = np.floor(np.array([p[0] for p in passes]) * dt / 86400).astype(int)
    out = {}
    for sp in spaziature:
        sc = 1 + (L // sp).astype(int)
        per_day = np.bincount(days, weights=sc, minlength=30)
        out[sp] = (sc.mean(), (sc >= 4).mean(), per_day.mean(), (per_day >= 4).mean())
    return out


def main():
    om_nadir = 0.5 * (np.degrees(np.gradient(linea_di_vista(np.arange(-0.01, 0.0101, DT)), DT))[10] - np.degrees(N))
    geometrie = [('nadir', om_nadir), ('45° di traverso', 0.50), ('45° lungo traccia', 0.35)]
    T_rip0 = T_SCENA0 + T_BANDE0
    T_rip = K * T_rip0
    print('=== 1) Cinematica del rallentamento (fattore 2)')
    print(f'Ripresa senza rallentamento: scena {T_SCENA0} s + bande {T_BANDE0} s = {T_rip0:.2f} s')
    print(f'Ripresa con rallentamento:   scena {K*T_SCENA0:.1f} s + bande {K*T_BANDE0:.2f} s = {T_rip:.2f} s '
          f'(D-096 conta solo la scena: {K*T_SCENA0:.1f} s)')
    for nome, om in geometrie:
        print(f'  {nome:18s} ω_s = {om:.3f}°/s: rotazione in ripresa {om*T_rip:.2f}° '
              f'(solo scena {om*K*T_SCENA0:.2f}°); momento a 1,14 kg·m² {1.14*np.radians(om):.4f} N·m·s '
              f'(+ orbitale {1.14*N:.4f})')

    print('\n=== 2) Rampe: durata minima con coppia pianificata (inerzia stimata 1,254 kg·m²)')
    rampe = {}
    for nome, om in geometrie:
        x0 = np.radians(om) * T_rip / 2
        for tp in (1e-3, 3e-3):
            Ti = 1.5 * np.radians(om) * IHAT_PIANO / tp      # velocità a gradino "liscio": a_max = 1,5·ω/T
            rampe[(nome, tp)] = (Ti, Ti)
            Tfermo = durata_rampa(0, 0, x0, -np.radians(om), tp)
            print(f'  {nome:18s} {tp*1e3:.0f} mN·m: rampa {Ti:.1f} s (assetto di partenza {np.degrees(x0)+om*Ti/2:.1f}° in avanti); '
                  f'partendo da beccheggio 0 sarebbero {Tfermo:.1f} s')
        tau = np.linspace(0, 60, 2001)
        _, _, a = quintica(60.0, 0, 0, 0, x0, -np.radians(om), 0, tau)
        print(f'  {nome:18s} rampa dentro lo slew di 60 s: coppia pianificata {np.abs(a).max()*IHAT_PIANO*1e3:.3f} mN·m')

    print('\n=== 3) Simulazione in anello chiuso (banda 1 rad/s, 10 Hz, GY2, 5 ripetizioni, caso peggiore)')
    casi_ctrl = [('stimata +10%', 1.10), ('stimata −10%', 0.90), ('nominale 0,69 (pre-commissioning)', None)]
    riass = {}
    for nome, om in geometrie:
        for var, tp in (('R1 1 mN·m', 1e-3), ('R1 3 mN·m', 3e-3), ('R2 in slew 60 s', None)):
            if tp is None:
                Ti = To = 60.0
            else:
                Ti, To = rampe[(nome, tp)]
            print(f'--- {nome}, {var}: ingresso {Ti:.1f} s, ripresa {T_rip:.2f} s')
            for I in (0.64, 1.14):
                for nc, f in casi_ctrl:
                    ih = I * f if f else 0.69
                    p = caso(np.radians(om), T_rip, Ti, To, I, ih, libero=tp is not None)
                    riass[(nome, var, I, nc)] = p
                    print(f'  I {I:.2f}, controllore {nc:<34} assestamento {p["t_ass"]:.2f} s; in scena deriva (99%) '
                          f'{p["deriva"]:.5f}°/s, errore max {p["ape"]:.4f}°; coppia {p["cop"]*1e3:.2f} mN·m, '
                          f'momento {p["h"]:.3f} N·m·s')

    print('\n=== 4) Conoscenza dell\'assetto tra le bande (DR-18: 2,8 µrad a 1 sigma, come in A5.3 f)')
    print('  Con il rallentamento l\'intervallo tra la PAN e l\'ultima banda raddoppia (0,79 -> 1,58 s) e il giroscopio')
    print('  misura una rotazione 12 volte più veloce: pesano di più rumore (ARW·√T) e fattore di scala (fs·ω·T).')
    om = geometrie[0][1]
    for lab, w_in, T in (('assetto fisso', N, T_BANDE0), ('rallentamento nadir', N + np.radians(om), K * T_BANDE0)):
        for arw_lab, arw in (('CRH03 0,006°/√h', 0.006), ('prudente 0,01°/√h', 0.01)):
            e_arw = np.radians(arw / 60) * np.sqrt(T)
            resto = np.sqrt(max(SOGLIA_DR18**2 - e_arw**2, 0))
            print(f'  {lab:20s} ω {np.degrees(w_in):.3f}°/s, T {T:.2f} s, {arw_lab}: ARW {e_arw*1e6:.2f} µrad -> '
                  f'fs ammesso {resto/(w_in*T)*1e6:6.0f} ppm (da solo {SOGLIA_DR18/(w_in*T)*1e6:.0f} ppm)')
    print('  Dati CRH03 (datasheet rev 4): fattore di scala ±0,15–0,3% sulla temperatura (1500–3000 ppm), non linearità 0,02–0,05%')
    print('  Verifica in simulazione (nadir, R1 3 mN·m, I 1,14), differenza di errore di stima su 1,58 s, 99° percentile:')
    Ti, To = rampe[('nadir', 3e-3)]
    for sf in (0.0, 1e-4, 5e-4, 1.5e-3, 3e-3):
        p = caso(np.radians(om), T_rip, Ti, To, 1.14, 1.254, sf)
        print(f'    fs {sf*1e6:5.0f} ppm: {p["kb99"]*1e6:5.1f} µrad (atteso solo fs: {sf*(N+np.radians(om))*K*T_BANDE0*1e6:5.1f}); '
              f'deriva vera rispetto al profilo fs·ω = {np.degrees(sf*(N+np.radians(om))):.5f}°/s')
    arw_max = np.degrees(SOGLIA_DR18 / np.sqrt(K * T_BANDE0)) * 60
    print(f'  ARW massimo per 2,8 µrad su {K*T_BANDE0:.2f} s: {arw_max:.4f}°/√h (su 0,79 s era 0,0108)')

    print('\n=== 5) Tempo aggiunto per scena e scene per passaggio (D-072)')
    for nome, om in geometrie:
        for var in ('R1 1 mN·m', 'R1 3 mN·m', 'R2 in slew 60 s'):
            ta = max(riass[(nome, var, I, nc)]['t_ass'] for I in (0.64, 1.14) for nc, _ in casi_ctrl[:2])
            ta_pre = max(riass[(nome, var, I, nc)]['t_ass'] for I in (0.64, 1.14) for nc, _ in casi_ctrl)
            if var.startswith('R2'):
                agg = (T_rip - T_rip0) + ta
                print(f'  {nome:18s} {var}: +{agg:.1f} s per scena (ripresa +{T_rip-T_rip0:.1f} s, assestamento in più {ta:.2f} s; '
                      f'pre-commissioning {ta_pre:.2f} s) -> +{agg*VG:.0f} km tra due bersagli con slew')
            else:
                tp = 1e-3 if '1 mN' in var else 3e-3
                Ti, To = rampe[(nome, tp)]
                ciclo = Ti + ta + T_rip + To
                print(f'  {nome:18s} {var}: bersagli successivi senza slew: rampa {Ti:.1f} + assestamento {ta:.2f} + ripresa '
                      f'{T_rip:.1f} + rampa {To:.1f} = {ciclo:.1f} s ({ciclo*VG:.0f} km) contro {T_rip0:.1f} s ({T_rip0*VG:.0f} km)')
    sp = scene_per_passaggio((450.0, 450.0 + (T_rip - T_rip0 + 0.5) * VG, 500.0))
    for k, (m, f4, d, g4) in sp.items():
        print(f'  spaziatura {k:.0f} km: scene per passaggio in media {m:.2f} (4 nel {f4*100:.0f}% dei passaggi); '
              f'{d:.1f} al giorno, ≥ 4 nel {g4*100:.0f}% dei giorni')

    # figura del caso nadir, R2 e R1 3 mN·m, inerzia 1,14
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
    for var, Ti, col in (('R1 3 mN·m', rampe[('nadir', 3e-3)][0], '#1f6fb2'), ('R2 in slew 60 s', 60.0, '#c0392b')):
        t, ref, wr, ar = profilo(np.radians(om_nadir), T_rip, Ti, rampe[('nadir', 3e-3)][1], dopo=0.0)
        err, _, _, _ = simula_sf(ref, wr, ar, 1.14, 1.0, 10, ARW, BIAS, 0.0, 3000, 1.254)
        if var.startswith('R2'):
            t, ref, wr, ar = profilo(np.radians(om_nadir), T_rip, Ti, Ti, dopo=0.0, libero=False)
            err, _, _, _ = simula_sf(ref, wr, ar, 1.14, 1.0, 10, ARW, BIAS, 0.0, 3000, 1.254)
        ax[0].plot(t, np.degrees(wr - N), color=col, lw=1.2, label=var)
        ax[1].plot(t, np.degrees(err) * 1e3, color=col, lw=0.8, label=var)
    for a_ in ax:
        a_.axvspan(0, T_rip, color='0.85', zorder=0); a_.grid(alpha=0.3); a_.legend()
    ax[0].set_ylabel('beccheggio rispetto\nall\'orbita (°/s)')
    ax[1].set_ylabel('errore di puntamento\nvero (millesimi di °)')
    ax[1].set_xlabel('tempo dall\'inizio della ripresa (s); in grigio la ripresa')
    ax[1].set_xlim(-25, T_rip + 25)
    ax[0].set_title('Rallentamento ×2 a nadir, inerzia vera 1,14 kg·m², controllore 1,254')
    fig.tight_layout(); fig.savefig(os.path.join(QUI, 'risultati', 'rallentamento_diurno.png'), dpi=150)


if __name__ == '__main__':
    main()
