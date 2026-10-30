# A5.P3 - carico di lavoro della scheda di bordo (stime di primo ordine)
import math
mu, Re, a = 398600.4418, 6378.137, 6680.2
v = math.sqrt(mu / a)              # km/s velocita' orbitale
vg = v * Re / a                    # km/s velocita' al suolo
print(f"velocita' al suolo {vg:.3f} km/s")

# GIORNO: sensore 31,4 Mpx letto a 20 fps (somma di 4 passaggi, D-032)
mpx_sens, fps, bit = 31.4, 20, 12
ing = mpx_sens * fps                       # Mpx/s in ingresso
print(f"giorno ingresso {ing:.0f} Mpx/s = {ing*bit/1000:.2f} Gbit/s")
t_scena = 9.7 / vg                         # s per una scena 9,7 km
grezzo = ing * t_scena                     # Mpx letti per scena
print(f"scena: {t_scena:.2f} s, grezzo {grezzo:.0f} Mpx = {grezzo*1.5/1000:.2f} GB (12 bit)")
# uscita dopo la somma: pan 1,5 m + 4 bande a 3 m
pan = vg*1000/1.5 * 6464 / 1e6
col = vg*1000/3.0 * 3232 * 4 / 1e6
print(f"dopo la somma: pan {pan:.1f} + colori {col:.1f} = {pan+col:.1f} Mpx/s = {(pan+col)*bit/1000:.2f} Gbit/s")
scena_somm = (6464*6467 + 4*3232*3233) / 1e6
print(f"scena sommata {scena_somm:.1f} Mpx = {scena_somm*1.5:.0f} MB")
print(f"4 scene grezze {4*grezzo*1.5/1000:.1f} GB, 4 scene sommate {4*scena_somm*1.5:.0f} MB")

# NOTTE: 2048x2048 a 50 fps (scatti da 20 ms), 12 scatti citta' (D-077)
n_mpx = 2048*2048/1e6
print(f"notte ingresso {n_mpx*50:.0f} Mpx/s = {n_mpx*50*bit/1000:.2f} Gbit/s; 12 scatti {12*n_mpx:.1f} Mpx = {12*n_mpx*1.5:.0f} MB")

# AI: rete di segmentazione, ordine di grandezza 50-150 GOP per Mpx (TBC)
for nome, tops in [("VPU tipo Myriad X (~1 TOPS utili)", 1), ("FPGA con acceleratore (~2 TOPS utili)", 2), ("GPU tipo Jetson Orin NX (~20 TOPS utili)", 20)]:
    for gop in (50, 150):
        t = scena_somm * gop / (tops * 1000)
        print(f"  {nome}, {gop} GOP/Mpx: {t:.1f} s per scena, {4*t:.0f} s per 4 scene")
