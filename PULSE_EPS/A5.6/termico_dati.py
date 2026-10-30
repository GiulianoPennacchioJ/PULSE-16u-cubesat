"""PULSE A5.6.8 - Dati per il modello termico di Giuseppe (D-110): potenza dissipata dai componenti di
Giuliano per modo, e perdite di EPS e batteria in luce e al buio (dalla simulazione A5.6.7, routine).

Ipotesi: potenza elettrica = calore, tranne
  - radio S in trasmissione: esce 31 dBm (1,26 W) di radiofrequenza (A5.5);
  - motore REGULUS: esce la potenza del getto P = T * g0 * Isp / 2 (datasheet: 0,55 mN, 550 s a 50 W).
Valori nominali, senza margini (i margini stanno nel bilancio di potenza).
Uso: python termico_dati.py
"""
import io, contextlib, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

G0 = 9.80665
P_GETTO = 0.55e-3 * G0 * 550 / 2
RF = 10 ** (31 / 10) / 1000

V = {  # voce: (W elettrici, W dissipati)
    "Ruote (4)":            (4.0, 4.0),
    "Ruote, picco slew (2 a 9 W, ~60 s)": (16.0, 16.0),
    "Star tracker (2)":     (1.0, 1.0),
    "Giroscopio":           (5.0, 5.0),
    "Magnetorquer (3)":     (3.0, 3.0),
    "Magnetometro":         (0.75, 0.75),
    "Sensori solari":       (0.3, 0.3),
    "GNSS":                 (0.125, 0.125),
    "Computer di bordo":    (0.4, 0.4),
    "EPS a vuoto":          (0.6, 0.6),
    "Radio UHF (ricezione)": (0.48, 0.48),
    "Radio S, ricezione":   (4.0, 4.0),
    "Radio S, trasmissione": (15.0, 15.0 - RF),
    "Motore REGULUS":       (50.0, 50.0 - P_GETTO),
}
MODI = {
    "Attesa":           ["Ruote (4)", "Star tracker (2)", "Giroscopio", "Magnetometro", "Sensori solari", "GNSS", "Computer di bordo", "EPS a vuoto", "Radio UHF (ricezione)"],
}
B = MODI["Attesa"]
MODI["Ripresa diurna o notturna"] = B
MODI["Spinta"] = B + ["Magnetorquer (3)", "Motore REGULUS"]
MODI["Scarico dati"] = B + ["Radio S, trasmissione"]
MODI["Safe"] = B + ["Magnetorquer (3)"]
MODI["Detumbling"] = [x for x in B if x not in ("Ruote (4)", "Star tracker (2)")] + ["Magnetorquer (3)"]

out = []; p = out.append
p("PULSE A5.6.8 - Dati per il termico (componenti di Giuliano, valori nominali)")
p("Motore: potenza del getto %.2f W su 50 W -> dissipati nel satellite ~%.1f W (rendimento di spinta %.1f%%)" % (P_GETTO, 50 - P_GETTO, 100 * P_GETTO / 50))
p("Radio S: %.2f W di radiofrequenza su 15 W -> dissipati %.1f W" % (RF, 15 - RF))
p("")
p("Potenza dissipata per modo (W), solo apparati di Giuliano:")
for mm, lst in MODI.items():
    p("  %-28s %5.1f W  (%s)" % (mm, sum(V[x][1] for x in lst), ", ".join(lst)))
p("  picchi: ruote negli slew +16 W per ~60 s; ricevitore S +4 W ~1,3 h/giorno attorno ai contatti")

# perdite di EPS e batteria dalla simulazione (routine)
with contextlib.redirect_stdout(io.StringIO()):
    import simulazione_soc as S
th, soc, car, pb, cap, sc = S.simula()
psa = pb / (S.ETA_MPPT * S.ETA_CAVI)
mppt = psa * (1 - S.ETA_MPPT)
cavi = psa * S.ETA_MPPT * (1 - S.ETA_CAVI)
bil = pb - car
dsoc = np.diff(soc, prepend=soc[0])
carica = np.where((bil > 0) & (dsoc > 0), bil * S.ETA_C, 0)
perdita_c = carica * (1 - S.ETA_C) / S.ETA_C
perdita_s = np.where(bil < 0, -bil / S.ETA_S * (1 - S.ETA_S), 0)
luce = psa > 1
p("")
p("Perdite dalla simulazione A5.6.7 (routine, giorno peggiore), W:")
p("  EPS (MPPT 8%%): media in luce %.1f, massimo %.1f" % (mppt[luce].mean(), mppt.max()))
p("  cavi di potenza (2%%): media in luce %.1f, massimo %.1f" % (cavi[luce].mean(), cavi.max()))
p("  batteria in carica (5%%): media in luce %.2f, massimo %.2f" % (perdita_c[luce].mean(), perdita_c.max()))
p("  batteria in scarica (5%%): media al buio %.2f, massimo %.2f" % (perdita_s[~luce].mean(), perdita_s.max()))
p("")
p("Limiti di temperatura:")
p("  Batteria (cella GomSpace NanoPower 2600 mAh, datasheet DS 1017178 rev 2.0): carica 0/+45 C; scarica -20/+60 C;")
p("     stoccaggio -20/+45 C (3 mesi), -20/+20 C (12 mesi). Obiettivo di progetto: 15-20 C (DR-64)")
p("  Motore REGULUS: limiti non pubblicati nel datasheet -> TBD da chiedere a T4i")
p("  Altri (ruote, star tracker, giroscopio, radio S e UHF, OBC, EPS, GNSS): dai datasheet in A5.7 (TBC)")
txt = "\n".join(out); print(txt)
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "risultati/termico_dati.txt"), "w").write(txt + "\n")
