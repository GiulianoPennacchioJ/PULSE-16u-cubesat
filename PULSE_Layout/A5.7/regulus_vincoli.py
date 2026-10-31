"""PULSE A5.7.3 - REGULUS: vincoli geometrici e di baricentro (stima di primo ordine, TBC).

Riferimento D-114 (Proposta): origine nel centro geometrico, X velocita'/spinta (ugello su -X),
Y lato del Sole, Z zenit. Telescopio (D-078, D-088): colonna 140 x 140 mm, asse a Y = -43 mm, X = 0,
da Z = -227 (coperchio) a Z = +183 mm (sensori).

1) Spazio tra la colonna del telescopio e la faccia -X, dove deve stare il blocco motore perche' la
   linea di spinta passi vicino al baricentro (D-047: <= 10 mm), con telescopio centrato in X o spostato
   contro la faccia +X; con e senza la sporgenza massima di 39,5 mm (D-036).
2) Massa di iodio (impulso totale / (Isp g0)) e spostamento del baricentro a fine vita in funzione
   della distanza del serbatoio dalla linea di spinta.
"""
import os

G0 = 9.80665
LATO = 226.3          # mm, involucro tra i binari (X e Y)
TEL = 140.0           # mm, colonna del telescopio
SPORG = 39.5          # mm, sporgenza massima (D-036)
I_TOT = 11000.0       # N s, REGULUS-50-I2 Large (D-034)
ISP = 550.0           # s, a 50 W (datasheet T4i)
M_SAT = 30.0          # kg, riferimento di D-043 / A5.P4

righe = []
p = lambda s="": (print(s), righe.append(s))
p("PULSE A5.7.3 - REGULUS: spazio sulla faccia -X e baricentro con il consumo dello iodio")
p()
p("1) Profondita' disponibile per il blocco motore tra la faccia -X e il telescopio (lungo X)")
for nome, x_tel in (("telescopio centrato in X (oggi, D-078)", 0.0),
                    ("telescopio contro la faccia +X", LATO / 2 - TEL / 2)):
    x_min_tel = x_tel - TEL / 2
    dentro = x_min_tel - (-LATO / 2)
    p(f"   {nome}: colonna da X {x_min_tel:+.1f} a {x_tel + TEL / 2:+.1f} mm -> {dentro:.1f} mm dentro, "
      f"{dentro + SPORG:.1f} mm con la sporgenza di {SPORG} mm (pareti e telaio esclusi, TBC)")
p()
m_i = I_TOT / (ISP * G0)
p(f"2) Iodio a bordo: {I_TOT:.0f} N s / ({ISP:.0f} s x {G0} m/s^2) = {m_i:.2f} kg")
p(f"   Spostamento del baricentro a serbatoio vuoto (satellite {M_SAT:.0f} kg pieno):")
for d in (0, 20, 40, 70, 100):
    s = m_i * d / (M_SAT - m_i)
    p(f"   serbatoio a {d:3d} mm dalla linea di spinta: {s:4.1f} mm da inizio a fine vita "
      f"(+/-{s / 2:.1f} mm se a meta' vita il baricentro e' sulla linea)")

qui = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(qui, "risultati"), exist_ok=True)
open(os.path.join(qui, "risultati", "regulus_vincoli.txt"), "w", encoding="utf-8").write("\n".join(righe) + "\n")
