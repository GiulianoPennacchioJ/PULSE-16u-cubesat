"""PULSE A5.6.5 - Configurazione dei pannelli solari.

Per ogni giorno dei 2 anni (ora del nodo da GMAT, D-103) calcola la direzione del Sole nel
riferimento orbitale locale (assetto L1 = nadir, D-043, usato anche in spinta, D-068) e da li':
  - fattore di illuminazione k (media del coseno sul tempo di luce) di varie facce/ali;
  - area di pannello necessaria;
  - area frontale aggiunta (drag) per le ali orientabili;
  - Sole sulla faccia dei radiatori (D-095) con rollio di 45 deg e in safe.

Riferimento orbitale locale: X = velocita', Y = normale all'orbita (lato del Sole, beta > 0), Z = zenit.
Uso: python pannelli_config.py
"""
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from luce_eclisse import sole, una_orbita, illuminazione, A, PERIODO

# ---------------- ipotesi di primo ordine (TBC fino ad A5.6.6)
W_M2 = 270.0       # W/m2 di pannello a incidenza normale, fine vita, a temperatura (stima: celle tripla giunzione
                   # ~29,5% BOL, impaccamento 0,80, temperatura -7%, degrado 2 anni -5%, UV/montaggio -3%)
XE, XD = 0.65, 0.85   # rendimenti batteria->carico in eclisse e pannello->carico in luce (SMAD, MPPT)
LUCE_H, ECL_H = 54.56 / 60, 36.0 / 60     # D-102
# energia per orbita con margini (orbite_tipo.py): attesa al buio 11,3 Wh; carico in luce dai giorni tipo
E_ECL = 11.3
GIORNI = {"Routine": 775.0, "Sole alto": 1016.0}   # Wh/giorno con margini (A5.6.3)
ORB = 1440 / 90.56

G = np.loadtxt(os.path.join(os.path.dirname(__file__), "risultati/gmat_ltdn_inclinazione.csv"), delimiter=",")
jd0 = 2461042.0417   # 1 gen 2026 13:00 UTC

conf = {"zenit": [], "ram": [], "scia": [], "normale lato Sole": [], "normale lato opposto": [],
        "zenit + rollio ottimo fisso": [], "zenit + rollio che insegue il Sole (asse X)": [], "ala orientabile (asse Y)": []}
phi_best = []
front = []         # area frontale relativa dell'ala orientabile (|cos tra normale e velocita'|)
rad_roll, rad_roll_min, rad_safe = [], [], []
betas = []
for k in range(0, len(G), 5):
    giorno, inc, raan, ltdn = G[k]
    jd = jd0 + giorno
    s_dir, s_dist, _ = sole(jd)
    t, u, r, n_hat = una_orbita(jd, raan, inc, passo=10.0)
    f = illuminazione(r, s_dir, s_dist)
    luce = f > 0.5
    # versori locali
    zz = r / np.linalg.norm(r, axis=1)[:, None]
    yy = np.repeat(n_hat[None, :], len(r), 0)
    xx = np.cross(yy, zz)
    sx, sy, sz = xx @ s_dir, yy @ s_dir, zz @ s_dir
    if sy.mean() < 0:            # Y verso il lato del Sole
        sy = -sy
    betas.append(np.degrees(np.arcsin(sy.mean())))
    L = luce
    c = lambda v: np.clip(v, 0, None)[L].mean()
    conf["zenit"].append(c(sz)); conf["ram"].append(c(sx)); conf["scia"].append(c(-sx))
    conf["normale lato Sole"].append(c(sy)); conf["normale lato opposto"].append(c(-sy))
    # rollio fisso ottimo: normale nel piano Y-Z inclinata di phi verso il Sole
    phis = np.radians(np.arange(0, 61, 1))
    vals = [c(np.cos(p) * sz + np.sin(p) * sy) for p in phis]
    conf["zenit + rollio ottimo fisso"].append(max(vals)); phi_best.append(np.degrees(phis[int(np.argmax(vals))]))
    conf["zenit + rollio che insegue il Sole (asse X)"].append(c(np.sqrt(sy**2 + sz**2) * (sz > -0.0) + 0 * sz))
    # ala con asse di rotazione Y: segue il Sole nel piano X-Z; al buio e oltre l'orizzonte messa di taglio
    inplane = np.sqrt(sx**2 + sz**2)
    conf["ala orientabile (asse Y)"].append(c(np.hypot(inplane * 0 + np.sqrt(sx**2 + sz**2), 0) * 1.0))
    front.append((np.abs(sx) / np.maximum(inplane, 1e-9))[L].mean())
    # radiatori: faccia -Y. Rollio di 45 deg attorno a X che porta la faccia verso lo zenit
    n_rad = np.array([0, -np.cos(np.radians(45)), np.sin(np.radians(45))])
    cr = n_rad[0] * sx + n_rad[1] * sy + n_rad[2] * sz
    rad_roll.append(((cr > 0) & L).mean() * PERIODO / 60)        # minuti per orbita SE il rollio durasse tutto il giro
    rad_roll_min.append(np.degrees(np.arccos(np.clip(cr[L].max(), -1, 1))))
    # safe: normale dei pannelli (zenit) sul Sole entro 15 deg -> la faccia -Y e' a 90 deg dal Sole +/- 15 deg
    rad_safe.append(90 - 15)

out = []; p = out.append
p("PULSE A5.6.5 - Configurazione dei pannelli (assetto L1 a nadir, 2 anni, ora del nodo da GMAT)")
p("Angolo beta: %.1f-%.1f deg" % (min(betas), max(betas)))
p("")
p("Fattore k = coseno medio sul tempo di luce (1 = pannello sempre perpendicolare al Sole)")
for kk, v in conf.items():
    p("  %-30s min %.3f  media %.3f" % (kk, min(v), np.mean(v)))
p("  rollio fisso ottimo: %.0f-%.0f deg verso il lato del Sole" % (min(phi_best), max(phi_best)))
p("  ala orientabile: area frontale media in luce = %.0f%% dell'area dell'ala (drag)" % (100 * np.mean(front)))
p("")
p("Potenza da pannello necessaria in luce: Psa = (E_ecl/Xe + E_luce/Xd) / T_luce (SMAD), Xe=%.2f Xd=%.2f" % (XE, XD))
area_n = {}
for g, e in GIORNI.items():
    e_orb = e / ORB
    psa = (E_ECL / XE + (e_orb - E_ECL) / XD) / LUCE_H
    area_n[g] = psa / W_M2
    p("  %-10s %.1f Wh/orbita -> Psa = %.1f W -> area a incidenza normale %.3f m2 (a %d W/m2)" % (g, e_orb, psa, psa / W_M2, W_M2))
p("")
p("Area di pannello necessaria per configurazione (caso peggiore di k nei 2 anni)")
pan = 0.226 * 0.454
for kk in ("zenit", "zenit + rollio ottimo fisso", "zenit + rollio che insegue il Sole (asse X)", "ala orientabile (asse Y)"):
    km = min(conf[kk])
    for g in GIORNI:
        a = area_n[g] / km
        p("  %-30s %-10s k=%.3f  area %.2f m2  = %.1f pannelli da 226x454 mm" % (kk, g, km, a, a / pan))
p("  (faccia a zenit del corpo: 226x226 mm = %.3f m2, in parte occupata da star tracker e antenna)" % (0.226**2))
p("")
p("Sole sulla faccia dei radiatori (normale all'orbita, lato opposto al Sole, D-095):")
p("  assetto nominale: mai (beta sempre > 0)")
p("  con rollio di 45 deg verso il lato opposto al Sole: Sole visibile in %.0f-%.0f%% del tempo di luce;" % (
    100 * min(rad_roll) / LUCE_H / 60, 100 * max(rad_roll) / LUCE_H / 60))
p("     angolo minimo tra Sole e normale del radiatore %.0f-%.0f deg; durata = tempo passato in rollio (ripresa diurna, ~8 min/passaggio)" % (
    min(rad_roll_min), max(rad_roll_min)))
p("  in safe (pannelli a zenit verso il Sole entro 15 deg): Sole a >= 75 deg dalla normale del radiatore")
txt = "\n".join(out); print(txt)
open(os.path.join(os.path.dirname(__file__), "risultati/pannelli_config.txt"), "w").write(txt + "\n")
