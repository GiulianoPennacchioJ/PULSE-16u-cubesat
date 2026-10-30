# A5.P5 - sensori notturni Gpixel a confronto con il modello SNR di A3 e il telescopio RC (trasmissione relativa 0,789, D-089)
import math
k11, tau, dk = 30.7, 0.789, 3.0          # e-/s per nW/cm2/sr con pixel 11 um (A3), ombra RC, buio e-/s
def snr(L, p, b, n, rn, t=0.02):
    k = k11*(p/11)**2; s = L*k*t*b*b*tau*n
    return s/math.sqrt(s + dk*t*b*b*n + n*(rn*b)**2)
def nmin(L, p, b, rn):
    return next((n for n in range(1, 400) if snr(L, p, b, n, rn) >= 10), 999)
for nome, p, rn, npx in (("GSENSE400BSI", 11, 1.6, 2048), ("GSENSE4040BSI", 9, 2.3, 4096), ("GSENSE2020BSI", 6.5, 1.6, 2048)):
    gsd = p*1e-3/700*302e3; use = min(npx, int(22.5/(p*1e-3)))      # finestra nel campo corretto di 22,5 mm
    for b in (1, 2, 3, 4):
        nq, npa = nmin(20, p, b, rn), nmin(5, p, b, rn)
        print(f"{nome} {p} um binning {b}x{b}: GSD {gsd*b:.1f} m, swath {use*gsd/1000:.1f} km, "
              f"quartiere 20 nW {nq} scatti ({nq*20} ms), paese 5 nW {npa} scatti ({npa*20} ms)")
