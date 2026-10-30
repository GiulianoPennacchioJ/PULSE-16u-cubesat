# A5.P5 - bilancio di nitidezza (MTF) di sistema a Nyquist, canale pan e notturno, con mosso e TDI (stima di Fase A)
import math
J0 = lambda x: sum((-1)**k*(x/2)**(2*k)/math.factorial(k)**2 for k in range(20))
sinc = lambda x: 1.0 if x == 0 else math.sin(x)/x
lam_nm = 600.0
def wfe_fattore(W_nm):                    # perdita di MTF a meta' frequenza di taglio per errore d'onda casuale (Shannon)
    return 1 - (W_nm/(0.18*lam_nm))**2
# --- canale pancromatico (Nyquist 145 c/mm = 0,5 cicli/pixel) ---
ottica = {"centro": (0.259, 0.252), "bordo": (0.240, 0.239), "angolo": (0.214, 0.209)}   # analisi_200_70_3.log (due direzioni)
costr = wfe_fattore(30.0)                 # costruzione e montaggio: ~30 nm rms in piu' (lucidatura + allineamento, TBC)
fuoco = wfe_fattore(29.5)                 # fuoco al limite di DR-03 (+-37 um -> ~29,5 nm di sfocatura)
pixel = 2/math.pi                         # apertura del pixel a Nyquist
diffus = 0.90                             # diffusione di carica / diafonia tra pixel (tipico CMOS 3,45 um, TBC)
jitter = J0(2*math.pi*0.15*0.5)           # DR-02: jitter <= 0,15 pixel di ampiezza
regis = math.exp(-2*math.pi**2*(1/6)**2*0.25)   # riallineamento TDI: residuo <= 1/3 px (DR-26) preso come 2 sigma
v_suolo, gsd = 7.38e3, 1.49               # m/s, m
casi = [  # nome, esposizione ms, passaggi TDI
 ("A: 0,2 ms x 4 passaggi (attuale)", 0.20, 4), ("B: 0,1 ms x 8 passaggi", 0.10, 8),
 ("C: 0,1 ms x 4 passaggi", 0.10, 4), ("D: 0,13 ms x 6 passaggi", 0.133, 6)]
snr_rif = {"inverno scuro": 29*math.sqrt(0.789), "tipico": 73*math.sqrt(0.789)}   # A3 (4 x 0,2 ms) con l'ombra RC (D-089)
print(f"fattori comuni: costruzione {costr:.3f}, fuoco al limite {fuoco:.3f}, pixel {pixel:.3f}, diffusione {diffus:.2f}, jitter {jitter:.3f}, riallineamento TDI {regis:.3f}")
for nome, t, n in casi:
    mosso_px = v_suolo*t*1e-3/gsd
    m_mosso = sinc(math.pi*mosso_px*0.5)
    fps = 20*n/4; gbit = 7.5*fps/20
    snr = {k: v*math.sqrt(n*t/(4*0.2)) for k, v in snr_rif.items()}
    print(f"\n{nome}: mosso {mosso_px:.2f} px -> fattore {m_mosso:.3f}; {fps:.0f} immagini/s, ~{gbit:.1f} Gbit/s in ingresso; "
          f"SNR tipico ~{snr['tipico']:.0f}, inverno scuro ~{snr['inverno scuro']:.0f} (stima a rumore di fotoni)")
    for campo, (a, b) in ottica.items():
        comune = costr*fuoco*pixel*diffus*jitter*regis
        print(f"   {campo}: lungo traccia {a*comune*m_mosso:.3f}, di traverso {b*comune:.3f}")
# --- canale notturno (Nyquist 45 c/mm) ---
ott_n = {"centro": 0.591, "angolo": 0.561}
fmc = sinc(math.pi*(1/3)*0.5)             # DR-10: mosso per scatto < 1/3 px
regn = regis                              # shift-and-add, stesso residuo
for campo, a in ott_n.items():
    print(f"notte {campo}: {a*wfe_fattore(30)*0.98*pixel*0.95*fmc*regn:.3f} (ottica {a}, pixel 11 um, diffusione 0,95, FMC, somma)")
