"""PULSE A5.7.8 - Inerzie di Fase A e verifiche GNC (ruote, gradiente di gravita', modi delle ali). Stima di primo ordine.

Modello: layout L1b + ali W1 con le masse del budget (A5.7.7, baricentro.py); variante con ali S2 (0,30 kg, D-119
opzione scartata) per confronto. Inerzie: scatole omogenee + pezzi del payload come punti, attorno al baricentro.

Verifiche:
1) inerzie (4 casi) e inviluppo di D-043;
2) DR-19/DR-22: momento e coppia degli slew (profilo di DR-19: picco 1,5 deg/s, coppia scalata con l'inerzia),
   FMC notturna (DR-04, 1,47 deg/s inerziali in beccheggio), legge d'imbardata FMC (DR-25, 0,56 deg/s),
   riserva per un'orbita di disturbi (aerodinamica con il braccio di A5.7.7) contro la piramide W3 (D-048);
3) DR-61: gradiente di gravita' con il rollio fisso 31-52 deg, momento per orbita, capacita' dei magnetorquer (DR-23);
4) primo modo flessibile di un'ala a fisarmonica aperta (trave a sbalzo, cerniere rigide: limite superiore) contro la
   banda di controllo di DR-20 (1 rad/s).

Uso: python inerzie_gnc.py  ->  risultati/inerzie_gnc.txt
"""
import os

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(QUI, "baricentro.py"), encoding="utf-8").read().split("\nrighe = []\n")[0]
exec(compile(src, "baricentro.py", "exec"))

MU, RT, H_ORB = 398600.4418, 6378.137, 302.0
N_ORB = np.sqrt(MU / (RT + H_ORB) ** 3)                  # rad/s
P_ORB = 2 * np.pi / N_ORB
B_MIN, B_MAX = 30e-6 * (RT / (RT + H_ORB)) ** 3, 60e-6 * (RT / (RT + H_ORB)) ** 3   # T, dipolo (equatore, polo)
DIP = 2.5                                                # A m2, DR-23
H_NOM, H_GUASTA, T_RUOTA = 0.163, 0.082, 7e-3            # N m s per asse (W3, D-048), coppia classe RWp100
W_SLEW = np.radians(1.5)                                 # rad/s, picco di DR-19
A_SLEW = 1.0e-3 / 1.14                                   # rad/s2 (coppia di DR-19 con I = 1,14)

righe = []
p = lambda s="": (print(s), righe.append(s))
p("PULSE A5.7.8 - Inerzie e verifiche GNC (layout L1b, ali W1, masse del budget; stima di primo ordine)")
p(f"Orbita 302 km: n = {N_ORB:.3e} rad/s, periodo {P_ORB / 60:.1f} min; campo magnetico {B_MIN * 1e6:.0f}-{B_MAX * 1e6:.0f} uT")


def caso(m_ala, stato, iodio, n_lato=3):
    global M_ALA
    vecchio = M_ALA; M_ALA = m_ala
    ym, zm = ugello(n_lato)
    J = inerzie(configura(ym, zm, iodio, "W1", stato, n_lato))
    m, g = baricentro(configura(ym, zm, iodio, "W1", stato, n_lato))
    M_ALA = vecchio
    return J, m, g


p()
p("1) Inerzie (kg m2) attorno al baricentro; X rollio (velocita'), Y beccheggio, Z imbardata (asse lungo)")
tab = {}
for ala, m_ala in (("S1 (0,55 kg/ala, D-119)", 0.55), ("S2 (0,30 kg/ala, confronto)", 0.30)):
    for stato in ("aperte", "chiuse"):
        for nome, f in (("pieno", 1.0), ("vuoto", 0.0)):
            J, m, g = caso(m_ala, stato, f)
            ev, evec = np.linalg.eigh(J)
            ang = np.degrees(np.arccos(min(1.0, max(abs(evec[:, k]) @ np.eye(3)[k] for k in range(3)))))
            tab[(ala, stato, nome)] = J
            p(f"   {ala:28s} ali {stato:6s} {nome:5s}: Ixx {J[0, 0]:.2f} Iyy {J[1, 1]:.2f} Izz {J[2, 2]:.2f}; "
              f"prodotti max {np.max(np.abs(J - np.diag(np.diag(J)))):.3f}; principali {ev[0]:.2f}/{ev[1]:.2f}/{ev[2]:.2f}")
p("   D-043 (inviluppo usato finora): rollio/beccheggio 0,64-1,14, imbardata 0,26-0,55")

Ja = tab[("S1 (0,55 kg/ala, D-119)", "aperte", "pieno")]
p()
p("2) Ruote (piramide W3: 0,163 N m s per asse, 0,082 con una ruota guasta; coppia 7 mN m per ruota)")
_, _, gv = caso(0.55, "aperte", 0.0)
ym, zm = ugello()
ycp, zcp, area = centro_pressione()
F_aero = 0.5 * RHO * V_ORB ** 2 * CD * area
t_aero = F_aero * np.hypot(gv[1] - ycp, gv[2] - zcp) / 1000
h_ris = t_aero * P_ORB
p(f"   riserva disturbi per un'orbita (aerodinamica {t_aero:.1e} N m x {P_ORB:.0f} s): {h_ris:.3f} N m s (DR-22 usava 0,037)")
for asse, k, w, nome in ((0, "Ixx", W_SLEW, "slew di rollio 45 deg in 60 s (DR-19)"),
                         (1, "Iyy", W_SLEW, "slew di beccheggio 45 deg in 60 s"),
                         (1, "Iyy", np.radians(1.47), "FMC notturna in beccheggio (1,47 deg/s, D-044)"),
                         (2, "Izz", np.radians(0.56), "legge d'imbardata FMC (0,56 deg/s, DR-25)")):
    I = Ja[asse, asse]
    h = I * w
    tq = I * A_SLEW if "slew" in nome else float("nan")
    tot = h + h_ris
    p(f"   {nome:48s}: {k} {I:.2f} -> {h:.3f} N m s (+ riserva = {tot:.3f}); "
      f"nominale {'ok' if tot <= H_NOM else 'NO'}, con ruota guasta {'ok' if tot <= H_GUASTA else 'NO'}"
      + (f"; coppia {tq * 1e3:.1f} mN m" if tq == tq else ""))
I = Ja[0, 0]
for h_disp, lab in ((H_GUASTA - h_ris, "con una ruota guasta"), (H_NOM - h_ris, "nominale")):
    w_max = min(h_disp / I, np.sqrt(np.radians(45) * A_SLEW))   # oltre l'ottimo sqrt(theta*alpha) non conviene
    t45 = np.radians(45) / w_max + w_max / A_SLEW if w_max > 0 else float("inf")
    p(f"   slew di rollio 45 deg {lab}: velocita' max {np.degrees(w_max):.2f} deg/s -> ~{t45:.0f} s (DR-19: 60 s)")
J2 = tab[("S2 (0,30 kg/ala, confronto)", "aperte", "pieno")]
h2 = J2[0, 0] * W_SLEW + h_ris
w2 = min((H_GUASTA - h_ris) / J2[0, 0], np.sqrt(np.radians(45) * A_SLEW))
p(f"   con ali S2: Ixx {J2[0, 0]:.2f}, slew di rollio {J2[0, 0] * W_SLEW:.3f} + riserva = {h2:.3f} N m s "
  f"({'ok' if h2 <= H_GUASTA else 'NO'} con una ruota guasta: 45 deg in ~{np.radians(45) / w2 + w2 / A_SLEW:.0f} s)")

p()
p("3) Gradiente di gravita' con il rollio fisso (DR-61): coppia = 3 n2 (Izz - Iyy) sin(phi) cos(phi)")
for phi in (31, 40, 45, 52):
    t = 3 * N_ORB ** 2 * (Ja[2, 2] - Ja[1, 1]) * np.sin(np.radians(phi)) * np.cos(np.radians(phi))
    p(f"   rollio {phi} deg: {t:.2e} N m -> {t * P_ORB:.3f} N m s per orbita (costante nel riferimento del satellite)")
t_mtq = DIP * B_MIN * 0.5
p(f"   magnetorquer 2,5 A m2: coppia utile media ~{t_mtq:.1e} N m (meta' di m x B a {B_MIN * 1e6:.0f} uT): "
  f"{t_mtq / (3 * N_ORB ** 2 * (Ja[2, 2] - Ja[1, 1]) * 0.5):.0f} volte la coppia di gradiente a 45 deg")
t_sp = F_SPINTA * np.hypot(gv[1] - ym, gv[2] - zm) / 1000
t_gg = 3 * N_ORB ** 2 * (Ja[2, 2] - Ja[1, 1]) * 0.5
p(f"   in spinta (rollio fisso), iodio vuoto: spinta {t_sp:.1e} + aerodinamica {t_aero:.1e} + gradiente {t_gg:.1e} "
  f"= {t_sp + t_aero + t_gg:.1e} N m (DR-21 nuovo: <= 2,3e-5 senza gradiente)")
p(f"   stabilita': asse di inerzia minima = {'Y (normale all orbita)' if Ja[1, 1] < min(Ja[0, 0], Ja[2, 2]) else 'altro'}: "
  "assetto non stabile per gradiente, tenuto dalle ruote (come gia' previsto)")

p()
p("4) Primo modo di un'ala a fisarmonica aperta (trave a sbalzo uniforme, cerniere rigide = limite superiore)")
L = (3 * 454 + 2 * 5) / 1000
b = 0.226
for nome, EI, m_ala in (("S1 FR4 1,6 mm (E ~20 GPa)", 20e9 * b * 1.6e-3 ** 3 / 12, 0.55),
                        ("S2 sandwich 6 mm, pelli CFRP 0,25 mm (E ~70 GPa)", 70e9 * 2 * b * 0.25e-3 * 3e-3 ** 2, 0.30)):
    mu = m_ala / 0.454
    f1 = 1.875 ** 2 / (2 * np.pi) * np.sqrt(EI / (mu * L ** 4))
    p(f"   {nome:48s}: EI {EI:6.2f} N m2, f1 ~{f1:.2f} Hz = {2 * np.pi * f1:.1f} rad/s -> {2 * np.pi * f1 / 1.0:.1f} volte la banda di 1 rad/s")
p("   regola pratica: primo modo >= ~10 volte la banda (>= ~1,6 Hz) per non accoppiarsi al controllo; le cerniere lo abbassano")
open(os.path.join(QUI, "risultati", "inerzie_gnc.txt"), "w", encoding="utf-8").write("\n".join(righe) + "\n")
