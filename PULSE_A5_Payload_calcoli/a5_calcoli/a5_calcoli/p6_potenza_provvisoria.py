# A5.6 (richiesta di Giuliano) - potenze provvisorie del payload, TBC fino ad A5.P6/P7
import math
# potenza acceso / standby (W). Fonti: camera Imperx CXP-C6440 con IMX342 5,3 W tip. a 25 fps 12 bit;
# GSENSE400BSI < 0,6 W solo sensore, 0,4 e-/s/pix a -20 C; il resto e' stima di ordine di grandezza
P = {"sensore giorno": (5.0, 0.0), "sensore notte": (2.0, 0.0), "FPGA + memoria": (6.0, 2.0), "chip AI": (2.0, 0.2)}
# tempi per passaggio con riprese (min): sensore acceso, FPGA attiva, AI attiva, FPGA in standby dopo
giorno = dict(sens=8, fpga=10, ai=2)
notte = dict(sens=8, fpga=10, ai=2)
def energia(c, sens):
    return (P[sens][0]*c['sens'] + P["FPGA + memoria"][0]*c['fpga'] + P["chip AI"][0]*c['ai'])/60
eg, en = energia(giorno, "sensore giorno"), energia(notte, "sensore notte")
print(f"energia per passaggio diurno {eg:.2f} Wh, notturno {en:.2f} Wh")
# scarico della coda dalla flash della scheda: FPGA in standby durante i contatti (~2,5 h/giorno, D-084)
scarico = P["FPGA + memoria"][1]*2.5
for nome, ng, nn in (("routine (1 giorno + 1 notte)", 1, 1), ("emergenza (2 giorno + 2 notte)", 2, 2)):
    tot = ng*eg + nn*en + scarico
    print(f"{nome}: riprese {ng*eg + nn*en:.1f} Wh + scarico {scarico:.1f} Wh = {tot:.1f} Wh/giorno")
# riscaldatori (stima): operativo 4 W continui sul telescopio, safe 2 W
for nome, w in (("riscaldatori operativi", 4.0), ("riscaldatori in safe", 2.0)):
    print(f"{nome}: {w} W -> {w*24:.0f} Wh/giorno se sempre accesi")
# coperchio: 2 W per 10 s a movimento, 4 movimenti/giorno
print(f"coperchio: {2*10*4/3600:.3f} Wh/giorno")
# corrente di buio GSENSE400BSI: raddoppia ogni ~6,5 C (regola tipica, TBC) -> temperatura per 3 e-/s (A3)
T = -20 + 6.5*math.log2(3/0.4); print(f"3 e-/s raggiunti a ~{T:.0f} C; a +20 C ~{0.4*2**(40/6.5):.0f} e-/s")
