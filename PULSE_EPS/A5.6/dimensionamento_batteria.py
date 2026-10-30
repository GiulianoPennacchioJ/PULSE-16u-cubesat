"""PULSE A5.6.6 - Dimensionamento della batteria.

Energia chiesta alla batteria nel caso peggiore: orbita O3 (ripresa notturna e contatto al buio), 16,9 Wh
con margini (A5.6.3). La spinta si programma nella parte centrale della luce, dove le ali producono di piu'
(D-105): in quei minuti la batteria non scarica (da verificare in A5.6.7).
Cella di riferimento: Li-ion 18650 da 2,6 Ah (classe GomSpace NanoPower), 3,6 V nominali -> 9,36 Wh.
Configurazione 4S (12-16,8 V, bus non regolato come EarthNext).
Uso: python dimensionamento_batteria.py
"""
E_CARICO = 16.9          # Wh al buio, O3, con margini (con D-107)
ETA_SCARICA = 0.90       # batteria -> carichi (convertitori e cavi), stima
FADE_EOL = 0.80          # capacita' a fine vita (perdita 20% in ~11.600 cicli), stima TBC
CELLA_WH = 2.6 * 3.6
S = 4
E_BATT = E_CARICO / ETA_SCARICA
out = []; p = out.append
p("PULSE A5.6.6 - Batteria")
p("Energia da dare al buio: %.1f Wh ai carichi -> %.1f Wh dalla batteria (rendimento %.2f)" % (E_CARICO, E_BATT, ETA_SCARICA))
p("Stringa 4S: %.1f Wh; capacita' a fine vita %.0f%%" % (S * CELLA_WH, FADE_EOL * 100))
for npar in (2, 3, 4):
    c = S * npar * CELLA_WH
    dod = E_BATT / (c * FADE_EOL)
    dod_g = E_BATT / (c * (npar - 1) / npar * FADE_EOL)
    p("  4S%dP: %5.1f Wh, %2d celle -> profondita' di scarica a fine vita %.0f%%; con una stringa guasta %.0f%%" % (
        npar, c, S * npar, 100 * dod, 100 * dod_g))
p("")
p("Autonomia in detumbling dopo il rilascio (16,7 W con margini, ali chiuse, batteria piena all'80%):")
for npar in (2, 3, 4):
    c = S * npar * CELLA_WH
    p("  4S%dP: %.1f h" % (npar, c * 0.8 * ETA_SCARICA / 16.7))
txt = "\n".join(out); print(txt)
open("risultati/dimensionamento_batteria.txt", "w").write(txt + "\n")
