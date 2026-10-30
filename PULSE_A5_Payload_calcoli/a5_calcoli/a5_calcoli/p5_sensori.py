# A5.P5 - confronto sensori diurni candidati con il telescopio RC (D-088): f 700 mm, D 120 mm, ombra lineare 0,45
import numpy as np
F, D, h, eps, lam = 700.0, 120.0, 302e3, 0.448, 0.60e-3   # mm, mm, m, -, mm (centro banda pan)
def mtf_ostruita(nu):
    # MTF di diffrazione di una pupilla anulare (O'Neill), nu in cicli/mm
    fc = D/(F*lam); x = nu/fc
    def A(x):
        x = np.clip(x, 0, 1); return (2/np.pi)*(np.arccos(x) - x*np.sqrt(1 - x*x))
    a = A(x); b = eps**2*A(x/eps) if x <= eps else 0.0
    xe = x
    if xe <= (1 - eps)/2: c = -2*eps**2
    elif xe >= (1 + eps)/2: c = 0.0
    else:
        chi = np.arccos((1 + eps**2 - 4*xe*xe)/(2*eps))
        c = -2*eps**2 + (2/np.pi)*(eps*np.sin(chi) + (1 + eps**2)/2*chi - (1 - eps**2)*np.arctan((1 + eps)/(1 - eps)*np.tan(chi/2)))
    return (a + b + c)/(1 - eps**2)
campo_pan = (22.3, 16.7)        # mm, area corretta del telescopio per il pancromatico (traverso x lungo traccia)
cand = [  # nome, pixel um, colonne, righe, fps max, potenza W (solo sensore o camera), nota spazio
 ("Sony IMX342 (baseline A2)", 3.45, 6480, 4870, 69.7, "5,3 W camera", "commerciale, nessuna prova spaziale nota"),
 ("Gpixel GMAX3265", 3.2, 9344, 7000, 71, "2,1 W sensore", "commerciale; Gpixel fa versioni su misura"),
 ("Teledyne e2v Emerald 67M USV", 2.5, 8192, 8192, 65, "n.d.", "versione 'space screened' U1/U3, prove SEL/SEFI"),
 ("ams CMV12000 (riferimento)", 5.5, 4096, 3072, 300, "n.d.", "molto usato in volo, provato a protoni"),
]
print(f"{'sensore':32s} {'GSD m':>6s} {'swath km':>8s} {'pixel usati':>13s} {'Q':>5s} {'MTF ott':>7s} {'MTF sis':>7s} {'luce/px':>7s} {'Gbit/s@20fps':>12s}")
for nome, p, nc, nr, fps, pw, nota in cand:
    gsd = p*1e-3/F*h
    uc = min(nc, int(campo_pan[0]/(p*1e-3))); ur = min(nr, int(campo_pan[1]/(p*1e-3)))   # finestra nell'area corretta
    sw = uc*gsd/1000
    nyq = 1/(2*p*1e-3); Q = lam*1e3*F/D/p
    mo = mtf_ostruita(nyq); ms = mo*0.636     # rivelatore sinc a Nyquist = 2/pi
    luce = (p/3.45)**2
    rate = uc*ur*12*20/1e9
    print(f"{nome:32s} {gsd:6.2f} {sw:8.1f} {uc:6d}x{ur:<6d} {Q:5.2f} {mo:7.3f} {ms:7.3f} {luce:7.2f} {rate:12.1f}   {pw}; {nota}")
print("controllo: MTF di diffrazione a 145 c/mm con ombra 0,45 (analisi_rc 0,262):", round(mtf_ostruita(145), 3))
