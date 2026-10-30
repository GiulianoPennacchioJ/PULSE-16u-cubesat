# A5.P6 - potenza del payload per modo operativo ed energia al giorno (sostituisce p6_potenza_provvisoria.py)
# Riferimenti di classe: scheda FPGA Xiphos Q8 (Zynq UltraScale+ ZU7EG, 5 W tipici, 3,5-25 W, 56 g, in volo dal 2020);
# chip AI Ubotica CogniSAT-XE1 (Movidius Myriad 2, 2 W tipici, 5 W max, 80 g, TRL 9);
# camera Imperx con IMX342 5,3 W a 25 fps (con slow-down D-096 bastano ~10 immagini/s: 5 W prudente);
# GSENSE400BSI < 0,6 W solo sensore (+ elettronica di lettura ~1,4 W, stima).
modi = ["Ripresa diurna", "Ripresa notturna", "Spinta", "Scarico dati", "Riposo / safe"]
voci = {  # W per modo, nello stesso ordine
 "P-12 sensore diurno":   [5.0, 0, 0, 0, 0],
 "P-13 sensore notturno": [0, 2.0, 0, 0, 0],
 "P-14 coperchio":        [0, 0, 0, 0, 0],      # 2 W per ~10 s a movimento: energia trascurabile
 "P-15 scheda FPGA":      [5.0, 5.0, 0, 3.5, 0],
 "P-15 chip AI":          [2.0, 2.0, 0, 0, 0],
}
marg = {"P-12 sensore diurno": .10, "P-13 sensore notturno": .10, "P-14 coperchio": .20, "P-15 scheda FPGA": .10, "P-15 chip AI": .10}
print("modo".ljust(18), *[m[:14].rjust(15) for m in modi])
for v, w in voci.items(): print(v.ljust(18), *[f"{x:15.1f}" for x in w])
tot = [sum(w[i] for w in voci.values()) for i in range(5)]
totm = [sum(w[i]*(1 + marg[v]) for v, w in voci.items()) for i in range(5)]
print("totale nominale".ljust(18), *[f"{x:15.1f}" for x in tot])
print("con margini voce".ljust(18), *[f"{x:15.1f}" for x in totm])
print("con +20% sistema".ljust(18), *[f"{x*1.2:15.1f}" for x in totm])
# energia al giorno per satellite (min): sensore acceso 8, FPGA 10, AI 2 per passaggio; scarico 71 min/giorno (D-092)
eg = (5*8 + 5*10 + 2*2)/60; en = (2*8 + 5*10 + 2*2)/60; es = 3.5*71/60
print(f"\nper passaggio: diurno {eg:.2f} Wh, notturno {en:.2f} Wh; scarico {es:.2f} Wh/giorno; coperchio {2*10*4/3600:.3f} Wh/giorno")
for nome, ng, nn in (("routine 1+1", 1, 1), ("emergenza 2+2", 2, 2)):
    print(f"{nome}: {ng*eg + nn*en + es:.1f} Wh/giorno (senza riscaldatori P-23, che arrivano da A5.P7)")
print(f"media su 24 h routine: {(eg + en + es)/24:.2f} W")
