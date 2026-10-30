# A5.P4 - massa del telescopio dal basso (stima di primo ordine), alluminio vs vetro + carbonio
import math
def disco(D_mm, t_mm, rho, alleggerito):
    v = math.pi * (D_mm/20)**2 * (t_mm/10)          # cm3
    return v * rho * (1 - alleggerito) / 1000        # kg
specchi = {  # diametro, spessore (mm)
    "primario": (125, 21), "secondario": (40, 8), "piano di rinvio": (40, 6), "terziario": (60, 10)}
mat = {
  "A tutto alluminio": dict(rho_sp=2.70, all_sp=0.50, supporti=0.20, rho_str=2.70, parete=1.5, extra=0.15),
  "B vetro + carbonio": dict(rho_sp=2.53, all_sp=0.60, supporti=0.70, rho_str=1.60, parete=2.0, extra=0.25),
}
for nome, m in mat.items():
    sp = sum(disco(D, t, m["rho_sp"], m["all_sp"]) for D, t in specchi.values())
    sup = sp * m["supporti"]                       # attacchi (integrati in Al, flessure Ti/Invar per il vetro)
    tubo = 4*0.14*0.20*m["parete"]/1000 * m["rho_str"]*1000   # tubo 140x140x200 mm
    paratie = 2 * 0.14*0.14*0.005 * 0.4 * m["rho_str"]*1000   # 2 piastre 5 mm alleggerite 60%
    ragno = 0.03
    tot = sp + sup + tubo + paratie + ragno + m["extra"]   # extra: viti, inserti, regolazione fuoco
    print(f"{nome}: specchi {sp:.2f} + supporti {sup:.2f} + tubo {tubo:.2f} + paratie {paratie:.2f} + ragno {ragno:.2f} + varie {m['extra']:.2f} = {tot:.2f} kg")
# rugosita' e luce diffusa: TIS = (4 pi sigma / lambda)^2 per specchio, 4 specchi
for s in (2, 5, 10):
    tis = (4*math.pi*s/550)**2
    print(f"rugosita' {s} nm: luce diffusa {100*tis:.1f}% per specchio, {100*(1-(1-tis)**4):.1f}% con 4 specchi")
# errore di forma ammesso: Marechal, Strehl 0,8 -> lambda/14 rms totale, diviso su 4 specchi (riflessione raddoppia)
wfe = 550/14
print(f"errore d'onda totale ammesso {wfe:.0f} nm rms -> superficie per specchio ~{wfe/2/2:.0f} nm rms (4 specchi, in quadratura, x2 in riflessione)")
