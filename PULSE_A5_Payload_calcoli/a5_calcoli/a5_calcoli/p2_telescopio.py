# A5.P2 - ingombro del telescopio per confronto con Simera TriScape (dati satnow.com, letti 2026-10-30)
ts100 = dict(D=95, f=580, ingombro=(98, 98, 176), massa=1.1)
ts200 = dict(D=190, f=1067, ingombro=(216, 216, 304), massa=12.1)
D, f = 120, 700  # PULSE (A2)
k = D/ts100["D"]; kf = f/ts100["f"]
print(f"scala apertura {k:.2f}, focale {kf:.2f}")
lato = 98*k; lung = 176*kf
print(f"ingombro scalato da TriScape100: {lato:.0f} x {lato:.0f} x {lung:.0f} mm")
for e in (2.5, 3):
    print(f"massa scalata (esponente {e}): {ts100['massa']*k**e:.1f} kg")
# Faccia a nadir 226 x 226 mm, telescopio + paraluce ~130 mm, 10 mm di bordo strutturale (TBC)
F, T, b = 226, 130, 10
print(f"centrato: cornice {(F-T)/2:.0f} mm, utile ~{(F-T)/2-b:.0f} mm; area libera {(F*F-T*T)/F/F*100:.0f}%")
print(f"spostato su un lato: striscia {F-T-2*b:.0f} x {F-2*b:.0f} mm")
# spostamento del baricentro se il telescopio (2-2,5 kg) e' spostato di (F-T)/2 su ~30 kg
for m in (2.0, 2.5):
    print(f"baricentro: telescopio {m} kg spostato {(F-T)/2:.0f} mm -> {m*(F-T)/2/30:.1f} mm su 30 kg")
# Apertura ridotta per stare in mezza sezione (113 mm): luce persa
print(f"apertura 10 cm: luce {(100/120)**2*100:.0f}% di quella da 12 cm")

# --- Confronto con EarthNext (paper La Marca et al.): TMA fuori asse, f 500 mm, F/6 (D 83 mm), FOV 3 x 1,5 deg, dentro 8U
D_en, f_en = 500/6, 500
kD, kf = D/D_en, f/f_en
print(f"\nEarthNext D {D_en:.0f} mm; scala apertura {kD:.2f}, focale {kf:.2f}")
print(f"8U (226x226x227) scalato: {226*kD:.0f} x {226*kD:.0f} x {227*kf:.0f} mm; volume x{kD**2*kf:.2f} = ~{8*kD**2*kf:.0f}U (limite superiore)")
for occ in (0.5, 0.6):
    print(f"se il telescopio EarthNext occupa il {occ*100:.0f}% degli 8U: ~{8*occ*kD**2*kf:.0f}U")
# Campo PULSE: piano focale 22,5 x 42,2 mm a f 700
import math
print(f"campo PULSE: {math.degrees(22.5/700):.2f} x {math.degrees(42.2/700):.2f} deg, diag {math.degrees(math.hypot(22.5,42.2)/700):.1f}")
# In asse: TriScape200 scalato a PULSE
print(f"TriScape200 scalato: {216*D/190:.0f} x {216*D/190:.0f} x {304*f/1067:.0f} mm")
# Apertura 8,3 cm: diffrazione e luce
for d in (0.083, 0.12):
    print(f"D {d*100:.1f} cm: diffrazione {1.22*0.55e-6/d*302e3:.2f} m, luce {(d/0.12)**2*100:.0f}%")

# --- Paraluce: angolo di esclusione del Sole (raggio che entra da un bordo e tocca il bordo opposto in fondo)
Dap = 130  # apertura del paraluce, mm (stima)
for L in (50, 100, 150, 200):
    print(f"paraluce {L} mm: esclusione ~{math.degrees(math.atan(Dap/L)):.0f} deg dall'asse")
# Angolo minimo Sole-asse ottico in ripresa diurna: 180 - (zenit solare + puntamento fuori nadir)
for zs in (25, 45, 70):
    for off in (0, 30, 45):
        print(f"zenit solare {zs}, fuori nadir {off}: Sole a {180-(zs+off)} deg dall'asse")
