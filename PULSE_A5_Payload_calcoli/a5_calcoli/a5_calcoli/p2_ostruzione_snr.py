# Effetto dell'ombra dello specchietto (Korsch in asse) sull'SNR notturno di A3
import math
k = 30.7      # e-/s per 1 nW/cm2/sr, pixel 11 um (A3)
rn, dk = 1.6, 3.0  # rumore di lettura e-, corrente di buio e-/s (A3)
def snr(L, b, n, t=0.02, tau=1.0):
    px = b*b
    s = L*k*t*px*tau*n
    rumore = math.sqrt(s + dk*t*px*n + n*(rn*b)**2)   # binning digitale: rumore lettura x b
    return s/rumore
tau = 1 - 0.085 - 0.01   # specchietto ~35/120 mm (8,5%) + bracci (~1%) -> 0,905 (stima)
print(f"trasmissione relativa {tau:.3f}")
for nome, L, b, n in [("paese 2x2, 15 scatti", 5, 2, 15), ("paese 3x3, 10 scatti", 5, 3, 10), ("quartiere 1x1, 10 scatti", 20, 1, 10)]:
    print(f"{nome}: SNR {snr(L,b,n):.2f} -> {snr(L,b,n,tau=tau):.2f}")
for n in range(15, 21):
    print(f"paese 2x2, {n} scatti ({n*20} ms, +20% = {n*20*1.2:.0f} ms): SNR {snr(5,2,n,tau=tau):.2f}")
for n in range(10, 13):
    print(f"quartiere 1x1, {n} scatti ({n*20} ms): SNR {snr(20,1,n,tau=tau):.2f}")
