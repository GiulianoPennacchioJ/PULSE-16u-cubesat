"""A6.8 - Ora del nodo discendente (LTDN) minima per le riprese diurne di PULSE (DR-59, D-136).
Altezza del Sole sui bersagli italiani al passaggio diurno (discendente) in funzione dell'LTDN,
poi SNR diurno pancromatico scalato dal modello A3 (somma di 4 passaggi, ombra RC D-089).
Ipotesi: orbita circolare 302 km, i = 96,8 deg; ora solare media del punto sotto il satellite
dalla geometria dell'orbita; equazione del tempo e declinazione da formule NOAA; atmosfera
tau = 0,223 (trasmissione 0,80 a nadir come A3) sul solo percorso del Sole.
SNR ~ radice del segnale (rumore di fotoni), segnale ~ sin(h) * exp(-tau/sin h)."""
import math
Re, h, inc = 6378.137, 302.0, math.radians(96.8)
TAU = -math.log(0.80)
SNR_RIF = {"suolo scuro 5%": 29*math.sqrt(0.789), "suolo medio 15%": 51*math.sqrt(0.789)}  # A3 + RC, Sole a 20 deg
H_RIF = 20.0
BERSAGLI = {"Vetta d'Italia (limite nord)": (47.09, 12.18), "Gemona": (46.28, 13.14), "Aosta": (45.74, 7.32),
            "Norcia": (42.79, 13.09), "Napoli": (40.85, 14.27), "Palermo": (38.12, 13.36)}

def sole(giorno):
    """declinazione (rad) ed equazione del tempo (min) per il giorno dell'anno (NOAA)."""
    g = 2*math.pi/365*(giorno-1)
    eot = 229.18*(0.000075+0.001868*math.cos(g)-0.032077*math.sin(g)-0.014615*math.cos(2*g)-0.040849*math.sin(2*g))
    dec = (0.006918-0.399912*math.cos(g)+0.070257*math.sin(g)-0.006758*math.cos(2*g)+0.000907*math.sin(2*g)
           -0.002697*math.cos(3*g)+0.00148*math.sin(3*g))
    return dec, eot

def ritardo_latitudine(lat):
    """ore di differenza tra l'ora locale del punto sotto il satellite (ramo discendente, emisfero nord) e l'LTDN."""
    u = math.pi - math.asin(math.sin(math.radians(lat))/math.sin(inc))
    dra = math.atan2(math.cos(inc)*math.sin(u), math.cos(u)) - math.pi   # rispetto al nodo discendente
    return ((math.degrees(dra)/15.0 + 12) % 24) - 12

def spostamento_45(lat):
    """ore di anticipo per un bersaglio a 45 deg di traverso verso ovest (angolo al centro della Terra)."""
    eta = math.radians(45)
    lam = math.asin((Re+h)/Re*math.sin(eta)) - eta
    return math.degrees(lam)/math.cos(math.radians(lat))/15.0, lam*Re

def altezza(lat, ltdn, giorno, ovest45=False):
    dec, eot = sole(giorno)
    t = ltdn + ritardo_latitudine(lat) - (spostamento_45(lat)[0] if ovest45 else 0) + eot/60
    H = math.radians(15*(t-12)); f = math.radians(lat)
    return math.degrees(math.asin(math.sin(f)*math.sin(dec)+math.cos(f)*math.cos(dec)*math.cos(H)))

def fattore(hdeg):
    s = lambda x: math.sin(math.radians(x))*math.exp(-TAU/math.sin(math.radians(x)))
    return math.sqrt(s(hdeg)/s(H_RIF))

def hm(x): return f"{int(x)}:{round(x%1*60):02d}"

if __name__ == "__main__":
    print("Ritardo dell'ora locale rispetto all'LTDN sul ramo discendente:")
    for lat in (38, 42, 45, 47): print(f"  lat {lat} N: {ritardo_latitudine(lat)*60:+.1f} min")
    km = spostamento_45(45)[1]
    print(f"Bersaglio a 45 deg di traverso: {km:.0f} km dalla traccia, ora locale {spostamento_45(45)[0]*60:.1f} min prima (lat 45) se a ovest\n")
    # giorno peggiore: cerco il minimo dell'altezza nell'anno per il limite nord a nadir, LTDN 10:30
    gpeg = min(range(1, 366), key=lambda d: altezza(47.09, 10.5, d))
    print(f"Giorno dell'anno con il Sole piu' basso (limite nord, nadir, LTDN 10:30): {gpeg}")
    print("\nCaso peggiore = limite nord d'Italia (47,1 N), giorno", gpeg)
    print(" LTDN  | Sole nadir | Sole 45 ovest | SNR scuro nadir/45W | SNR medio nadir/45W | ombra/altezza nadir/45W")
    for ltdn in (11.0, 10.75, 10.5, 10.25, 56/60+9, 9.75, 9.5, 9.25, 9.0):
        a, b = altezza(47.09, ltdn, gpeg), altezza(47.09, ltdn, gpeg, True)
        s1 = [SNR_RIF["suolo scuro 5%"]*fattore(x) for x in (a, b)]
        s2 = [SNR_RIF["suolo medio 15%"]*fattore(x) for x in (a, b)]
        print(f" {hm(ltdn):5s} | {a:5.1f} deg  | {b:5.1f} deg     | {s1[0]:5.1f} / {s1[1]:5.1f}       | {s2[0]:5.1f} / {s2[1]:5.1f}       | {1/math.tan(math.radians(a)):.1f} / {1/math.tan(math.radians(b)):.1f}")
    print("\nBersagli di prova, giorno", gpeg, "(nadir / 45 deg ovest), SNR suolo scuro:")
    for ltdn in (10.5, 56/60+9, 9.5):
        print(f" LTDN {hm(ltdn)}")
        for n, (lat, lon) in BERSAGLI.items():
            a, b = altezza(lat, ltdn, gpeg), altezza(lat, ltdn, gpeg, True)
            print(f"   {n:30s} Sole {a:5.1f} / {b:5.1f} deg   SNR {SNR_RIF['suolo scuro 5%']*fattore(a):5.1f} / {SNR_RIF['suolo scuro 5%']*fattore(b):5.1f}")
    print(f"\nRiferimento A3+RC a Sole 20 deg: scuro {SNR_RIF['suolo scuro 5%']:.1f}, medio {SNR_RIF['suolo medio 15%']:.1f}")
