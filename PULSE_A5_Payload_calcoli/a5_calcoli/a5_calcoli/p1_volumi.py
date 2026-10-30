# A5.P1 - volumi dati per prodotto (stime di primo ordine)
B12 = 12/8  # byte per pixel a 12 bit
MB = 1e6
# Diurno: pan 1,5 m, swath 9,7 km (6464 px), RGB-NIR 3,0 m (4 bande)
gsd_p, gsd_m, sw = 1.5, 3.0, 9.7e3
def scena_diurna(L_km, bit=12):
    L = L_km*1e3
    pan = 6464 * (L/gsd_p)
    ms = 4 * 3232 * (L/gsd_m)
    return pan*bit/8/MB, ms*bit/8/MB
for L in (9.7, 20):
    for bit in (12, 14):
        p, m = scena_diurna(L, bit)
        print(f"scena diurna 9,7 x {L} km, {bit} bit: pan {p:.1f} MB + RGB-NIR {m:.1f} MB = {p+m:.1f} MB")
# Ritagli diurni (pan + 4 bande)
for lato in (1, 2):
    n = lato*1e3
    p = (n/gsd_p)**2*B12/MB; m = 4*(n/gsd_m)**2*B12/MB
    print(f"ritaglio diurno {lato}x{lato} km: {p:.2f} + {m:.2f} = {p+m:.2f} MB")
# Notte (A3): 2048^2 12 bit, binning
for b in (1, 2, 3):
    print(f"scena notturna bin {b}x{b}: {(2048/b)**2*B12/MB:.2f} MB")
z = (2000/4.8)**2*B12/MB
print(f"ritaglio notturno 2x2 km a 4,8 m: {z:.3f} MB; celle 2x2 km in una scena 9,8 km: {(9.8/2)**2:.0f} -> {(9.8/2)**2*z:.1f} MB")
# Frame intero per calibrazione
print(f"frame diurno intero 6464x4852: {6464*4852*B12/MB:.1f} MB; notturno 2048^2: {2048**2*B12/MB:.1f} MB")
# Compressione
p, m = scena_diurna(9.7)
for r in (2, 4, 8):
    print(f"scena diurna 9,7 km compressa {r}:1 -> {(p+m)/r:.1f} MB; notte 1x1 -> {6.29/r:.2f} MB")
# DEM Italia
A = 302e3*1e6
for res in (30, 90):
    print(f"DEM Italia {res} m, 16 bit: {A/res**2*2/MB:.0f} MB")
# Telemetria payload
camp = 100*2  # 100 parametri x 2 byte
base = camp*0.1*86400/MB
rip = camp*10*600/MB
print(f"telemetria: base 0,1 Hz {base:.1f} MB/g + riprese 10 Hz 10 min {rip:.1f} MB/g")

# --- Dopo le decisioni D-068 (compressione mista), D-069 (scene dimostratore), D-070 (ritaglio diurno 1 km)
print("\n=== Volumi al giorno per satellite (MB) ===")
scena_g = 125.4/4          # scena diurna quasi senza perdita 4:1
notte = 6.29/2             # scena notturna 1x1 senza perdita 2:1
rit_g = 1.33/2 + 0.02      # ritaglio diurno 1 km senza perdita + vettore 20 kB
rit_n = 0.26 + 0.02        # ritaglio notturno 2 km (A4: non compresso) + vettore
tm = 3.0                   # telemetria payload (stima)
casi = {
 "routine tipico":      dict(sg=1, ag=2*1,  sn=3, zn=2),
 "primi 3 mesi tipico": dict(sg=4, ag=2*4,  sn=3, zn=2),
 "emergenza (peggiore)":dict(sg=4, ag=10*4, sn=4, zn=24*4),
}
for k, c in casi.items():
    g = c["sg"]*scena_g + c["ag"]*rit_g
    n = c["sn"]*notte + min(c["zn"]*rit_n, c["sn"]*6.29)
    print(f"{k}: diurno {g:.0f} + notturno {n:.0f} + telemetria {tm:.0f} = {g+n+tm:.0f} MB")
# Calibrazione al commissioning (stima): 60 frame diurni + 100 notturni, senza perdita
cal = 60*47.0/2 + 100*6.29/2
print(f"calibrazione commissioning: {cal/1e3:.2f} GB per satellite")
# Caricamenti all'anno (stima)
lo = 4*22 + 4*30 + 12*5 + 6*5
hi = 4*22 + 4*30 + 12*20 + 6*50
print(f"caricamenti: {lo}-{hi} MB/anno; pacchetto massimo ~50 MB")
# Memoria di massa (stima)
fissi_lo, fissi_hi = 0.2+0.075+0.27+0.03+0.05, 1.0+0.67+0.27+0.12+0.2
coda = 3*170/1e3
buf = 4*125.4/1e3
print(f"contenuti fissi {fissi_lo:.1f}-{fissi_hi:.1f} GB; coda 3 giorni {coda:.2f} GB; buffer grezzi {buf:.2f} GB; calibrazione {cal/1e3:.1f} GB")
tot = fissi_hi + coda + buf + cal/1e3
print(f"totale caso alto {tot:.1f} GB; x2 margine {2*tot:.1f} GB; scene diurne compresse in 32 GB: {32e3/scena_g:.0f}")
