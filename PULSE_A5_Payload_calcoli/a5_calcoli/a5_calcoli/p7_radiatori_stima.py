# A5.6/A5.P7 - stima preliminare (TBC) delle superfici dei radiatori del payload, per la scelta delle facce (Giuliano)
# Faccia proposta: faccia laterale 226 x 454 dalla parte opposta al Sole (normale all'orbita, SSO 10:30/22:30): niente Sole diretto
import numpy as np
sig, Re, h = 5.670e-8, 6378.0, 302.0
def vf_terra(incl_deg, n=400000, seed=1):
    # fattore di vista verso la Terra di una piastra; incl = angolo tra normale e nadir (90 = faccia laterale, 180 = zenit)
    rng = np.random.default_rng(seed); u = rng.random(n); v = rng.random(n)
    th = np.arcsin(np.sqrt(u)); ph = 2*np.pi*v                     # campionamento coseno-pesato
    d = np.stack([np.sin(th)*np.cos(ph), np.sin(th)*np.sin(ph), np.cos(th)], 1)
    a = np.radians(incl_deg); R = np.array([[np.cos(a), 0, np.sin(a)], [0, 1, 0], [-np.sin(a), 0, np.cos(a)]])
    d = d @ R.T                                                     # z locale -> normale della piastra; nadir = +z globale
    rho = np.arcsin(Re/(Re + h))
    return np.mean(d[:, 2] > np.cos(rho))
F_lat, F_zen = vf_terra(90), vf_terra(180)
print(f"fattore di vista Terra: faccia laterale {F_lat:.2f}, zenit {F_zen:.2f}")
eps, alfa, IR, S, alb = 0.85, 0.20, 237.0, 1361.0, 0.30   # vernice bianca (fine vita TBC), IR terrestre, Sole, albedo medio
def area(Q, Tc, F, sole=0.0, albedo_on=False):
    T = Tc + 273.15
    q = eps*sig*T**4 - eps*IR*F - alfa*S*sole - (alfa*S*alb*F*0.5 if albedo_on else 0)
    return Q/q, q
casi = [
 # nome, potenza W, temperatura radiatore C, faccia, quando
 ("sensore notturno (sensore 0,6 W + perdite verso l'interno ~0,5 W)", 1.1, -10, "laterale", "notte"),
 ("  idem con margine x1,5", 1.65, -10, "laterale", "notte"),
 ("scheda payload: media con il calore di picco assorbito dalla massa (~2 W in contatto)", 2.0, 30, "laterale", "giorno"),
 ("  idem con margine x1,5 (3 W)", 3.0, 30, "laterale", "giorno"),
 ("scheda payload senza accumulo (picco 6 W)", 6.0, 30, "laterale", "giorno"),
]
for nome, Q, Tc, faccia, quando in casi:
    F = F_lat if faccia == "laterale" else F_zen
    A, q = area(Q, Tc, F, albedo_on=(quando == "giorno"))
    lato = np.sqrt(A)*1000
    print(f"{nome}: {Q} W a {Tc} C -> {q:.0f} W/m2 netti, area {A*1e4:.0f} cm2 (~{lato:.0f} x {lato:.0f} mm)")
# accumulo della scheda: 6 W per 10 min in ~0,45 kg (Al + circuito, c ~ 900 J/kg/K)
print(f"scheda senza radiatore: 6 W x 600 s su {0.45*900:.0f} J/K -> +{6*600/(0.45*900):.0f} K a passaggio")
for nome, F in (("laterale", F_lat), ("zenit", F_zen)):
    print(f"faccia {nome}: sensore notturno x1,5 {area(1.65, -10, F)[0]*1e4:.0f} cm2, scheda x1,5 {area(3.0, 30, F, albedo_on=True)[0]*1e4:.0f} cm2")
print("faccia laterale 226 x 454 mm = 1026 cm2; zenit 226 x 226 = 511 cm2")
