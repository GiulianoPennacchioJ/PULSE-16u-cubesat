# A5.P7 - bilancio termico semplice del telescopio (stima di Fase A, TBC con modello termico in Fase B)
import math
sig = 5.670e-8; T = 293.15                 # telescopio tenuto a ~20 C
A_ap = math.pi*0.065**2                    # apertura (paraluce 130 mm)
eps_cav = 0.85                             # emissivita' effettiva della cavita' (interno nero)
# l'apertura guarda la Terra (faccia a nadir): IR terrestre 237 W/m2, fattore di vista ~0,9 dentro il paraluce (stima)
for nome, F, albedo in (("notte, coperchio aperto", 0.9, 0.0), ("giorno, coperchio aperto", 0.9, 0.3*1361*0.5)):
    q = A_ap*(eps_cav*sig*T**4 - eps_cav*237*F - 0.2*albedo*F)
    print(f"{nome}: perdita netta dall'apertura {q:.1f} W")
A_mli = 4*0.14*0.41                        # superficie laterale della colonna
for e_mli in (0.01, 0.03):                 # emissivita' effettiva MLI (0,01 buona, 0,03 piccola e con forature)
    for Tint in (283.15, 273.15):          # interno del satellite 10 C o 0 C (stima, dipende dal termico di Giuliano)
        q = A_mli*e_mli*sig*(T**4 - Tint**4)
        print(f"MLI e* {e_mli}, interno {Tint-273.15:.0f} C: perdita {q:.2f} W")
q_cop = A_ap*0.05*sig*(T**4 - 200**4)      # coperchio chiuso: foglio basso emissivo verso lo spazio/Terra (stima)
print(f"coperchio chiuso: perdita ~{q_cop:.2f} W")
# costante di tempo del telescopio: 1,6 kg (vetro + carbonio + Ti, c ~ 800 J/kg/K), conduttanza verso il satellite 0,1-0,3 W/K (attacchi isolati)
for G in (0.1, 0.3):
    print(f"conduttanza {G} W/K: costante di tempo {1.6*800/G/3600:.1f} h; motore che scalda l'interno di +5 K -> +{5:.0f} K a regime, ~{5*(1-math.exp(-0.5*3600*G/(1.6*800))):.1f} K dopo 30 min")
