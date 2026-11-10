"""PULSE A5.7.7 - Baricentro definitivo di Fase A: quattro casi, posizione dell'ugello, verifiche DR-14 / DR-21 / DR-67.

Modello: layout L1b (D-125) con ali W1 (D-126), masse allineate al budget (A5.7.6: star tracker 0,185 kg per testa,
cablaggi 1,03 kg, termico di piattaforma M-24 0,46 kg con radiatore in basso sulla -Y, D-129, e staffe DR-72).
Usa le funzioni di ali_stivaggio.py / layout_bozza.py (stesse scatole, stessi pezzi del payload).

1) Ugello (linea di spinta) sul baricentro ad ali aperte a meta' vita: si spinge sempre ad ali aperte.
2) Quattro casi: ali chiuse/aperte x iodio pieno/vuoto. DR-14 (deployer) vale al lancio (ali chiuse, pieno);
   DR-21 (<= 10 mm dalla linea di spinta, <= 20 mm dal centro di pressione) e DR-67 (+-5,5 mm) valgono ad ali aperte.
3) Centro di pressione (stima di primo ordine, flusso libero molecolare lungo +X): baricentro dell'area frontale
   (faccia +X del corpo + spigoli delle ali aperte, spessore 2 mm). Il rollio fisso (D-106) ruota attorno alla
   velocita' e non sposta il centro di pressione nel riferimento del satellite.
4) Coppie di disturbo in spinta contro l'inviluppo di D-047 (densita' 4,6e-11 kg/m3, Cd 2,2).
5) Sensibilita': masse cresciute del margine di ciascuna voce (D-035); 8 ali (D-127).

Uso: python baricentro.py  ->  risultati/baricentro.txt
"""
import os
import sys

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(QUI, "ali_stivaggio.py"), encoding="utf-8").read().split("righe = []")[0]
exec(compile(src, "ali_stivaggio.py", "exec"))

V_ORB, RHO, CD = 7730.0, 4.6e-11, 2.2      # m/s a 302 km; densita' dimensionante e Cd di D-047
F_SPINTA = 0.55e-3                          # N, REGULUS a 50 W (D-034)
MARGINE = {"Catalogo": 0.05, "Catalogo modificato": 0.10, "Nuovo": 0.20}
MATURITA = {"M-01": "Catalogo", "M-02": "Catalogo", "M-03": "Catalogo", "M-04": "Catalogo modificato", "M-05": "Catalogo",
            "M-06": "Catalogo", "M-07": "Catalogo modificato", "M-08": "Catalogo", "M-09": "Catalogo modificato",
            "M-10": "Catalogo modificato", "M-17": "Catalogo", "M-18": "Catalogo modificato", "M-19": "Catalogo modificato",
            "M-20": "Catalogo", "M-21": "Catalogo modificato", "M-22": "Nuovo", "M-24": "Nuovo", "M-25": "Nuovo"}


def ugello(n_lato=3):
    ym, zm = 0.0, 0.0
    for _ in range(100):
        _, g = baricentro(configura(ym, zm, 0.5, "W1", "aperte", n_lato))
        ym, zm = g[1], g[2]
    return ym, zm


def centro_pressione(n_lato=3):
    a_corpo = 2 * H * 2 * HZ / 1e6                       # m2, faccia +X
    lung = n_lato * 454 + (n_lato - 1) * 5               # mm, apertura di un lato
    a_ala = lung * T_PAN / 1e6                           # m2, spigolo di un lato
    z_ala = HZ + 3
    zcp = 2 * a_ala * z_ala / (a_corpo + 2 * a_ala)
    return 0.0, zcp, a_corpo + 2 * a_ala


righe = []
p = lambda s="": (print(s), righe.append(s))
p("PULSE A5.7.7 - Baricentro di Fase A (layout L1b, ali W1, masse del budget A5.7.6; stima di primo ordine)")
for n_lato in (3, 4):
    ym, zm = ugello(n_lato)
    ycp, zcp, area = centro_pressione(n_lato)
    p()
    p(f"=== {2 * n_lato} ali ===")
    p(f"Ugello (linea di spinta) a X -{H + 37:.0f} (sporge 37 mm da -X), Y {ym:+.1f}, Z {zm:+.1f} mm")
    p(f"Centro di pressione (stima): Y {ycp:+.1f}, Z {zcp:+.1f} mm; area frontale {area:.4f} m2")
    p(f"{'caso':26s} {'massa':>6s} {'X':>7s} {'Y':>7s} {'Z':>7s} {'linea':>7s} {'CP':>7s}  verifiche")
    for stato in ("chiuse", "aperte"):
        for nome, f in (("pieno", 1.0), ("vuoto", 0.0)):
            m, g = baricentro(configura(ym, zm, f, "W1", stato, n_lato))
            d_l = np.hypot(g[1] - ym, g[2] - zm)
            d_cp = np.hypot(g[1] - ycp, g[2] - zcp)
            if stato == "chiuse":
                ok = abs(g[0]) <= 45 and abs(g[1]) <= 45 and abs(g[2]) <= 90
                v = f"DR-14 {'ok' if ok else 'NO'}" + (" (lancio)" if f == 1.0 else " (solo riferimento)")
            else:
                v = (f"DR-21 linea {'ok' if d_l <= 10 else 'NO'}, CP {'ok' if d_cp <= 20 else 'NO (>20)'}; "
                     f"DR-67 {'ok' if d_l <= 5.5 else 'NO'}")
            p(f"ali {stato}, iodio {nome:5s}      {m:6.2f} {g[0]:+7.1f} {g[1]:+7.1f} {g[2]:+7.1f} {d_l:7.1f} {d_cp:7.1f}  {v}")
    # coppie in spinta (ali aperte, caso peggiore iodio vuoto)
    m, g = baricentro(configura(ym, zm, 0.0, "W1", "aperte", n_lato))
    F_aero = 0.5 * RHO * V_ORB ** 2 * CD * area
    t_sp = F_SPINTA * np.hypot(g[1] - ym, g[2] - zm) / 1000
    t_ae = F_aero * np.hypot(g[1] - ycp, g[2] - zcp) / 1000
    p(f"Coppie in spinta, iodio vuoto: spinta {t_sp:.1e} N m + aerodinamica {t_ae:.1e} N m (resistenza {F_aero:.1e} N) "
      f"= {t_sp + t_ae:.1e} N m; inviluppo D-047 2,3e-5 N m (1,1 mN x 10 mm + aerodinamica + magnetica)")
    if n_lato == 3:
        dz = None
        for zb in np.arange(0, 0.6, 0.01):          # zavorra in fondo (Z -220) che porterebbe il CP entro 20 mm
            def conf(ym_, zm_, f, st="aperte"):
                lst = configura(ym_, zm_, f, "W1", st, n_lato)
                return lst + [("zav", "zavorra", "Struttura", zb, (0, 0, -220), (1, 1, 1), False)]
            y2, z2 = 0.0, 0.0
            for _ in range(60):
                _, g2 = baricentro(conf(y2, z2, 0.5)); y2, z2 = g2[1], g2[2]
            _, gv = baricentro(conf(y2, z2, 0.0))
            if np.hypot(gv[1] - ycp, gv[2] - zcp) <= 20:
                dz = zb; break
        p(f"Zavorra in fondo (Z -220 mm) che porterebbe il baricentro entro 20 mm dal CP per tutta la vita: "
          f"{dz:.2f} kg nominali" if dz is not None else "Zavorra: oltre 0,6 kg")
        # sensibilita': masse cresciute del margine
        def cresciute(lst):
            return [(c[0], c[1], c[2], c[3] * (1 + MARGINE.get(MATURITA.get(c[0], ""), 0.0)), c[4], c[5], c[6]) for c in lst]
        _, g0 = baricentro(configura(ym, zm, 0.5, "W1", "aperte"))
        _, g1 = baricentro(cresciute(configura(ym, zm, 0.5, "W1", "aperte")))
        p(f"Sensibilita' (masse di piattaforma cresciute del margine di voce, payload invariato): baricentro a meta' vita "
          f"si sposta di Y {g1[1] - g0[1]:+.1f} Z {g1[2] - g0[2]:+.1f} mm")
open(os.path.join(QUI, "risultati", "baricentro.txt"), "w", encoding="utf-8").write("\n".join(righe) + "\n")
