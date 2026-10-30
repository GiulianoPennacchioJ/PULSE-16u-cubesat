"""PULSE A5.6.2 - Analisi dei report GMAT (inclinazione media giornaliera ed eclipse locator)
e confronto con luce_eclisse.py. Uso: python confronto_gmat.py"""
import numpy as np, re, datetime as dt

MESI = {m: i + 1 for i, m in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split())}
def data(s):
    g, m, a, h = s.split()[:4]
    hh, mm, ss = h.split(":")
    return dt.datetime(int(a), MESI[m], int(g), int(hh), int(mm)) + dt.timedelta(seconds=float(ss))

def jd(t):
    return (t - dt.datetime(2000, 1, 1, 12)).total_seconds() / 86400 + 2451545.0

out = []; p = out.append
# ---------- inclinazione e ora del nodo
rig = [l for l in open("gmat/PULSE_inclinazione_2anni.txt") if re.match(r"\d\d \w\w\w \d{4}", l)]
T = np.array([jd(data(l[:24])) for l in rig])
v = np.array([[float(x) for x in l[24:].split()] for l in rig])
inc, raan, sma = v[:, 0], v[:, 1], v[:, 2]
anni = (T - T[0]) / 365.25
pend = np.polyfit(anni, inc, 1)[0]
n = T - 2451545.0
L = (280.460 + 0.9856474 * n) % 360                     # longitudine media del Sole (~AR del Sole medio)
ltdn = ((raan - L + 540) % 360 - 180) / 15 + 12 - 12    # ora locale del nodo ascendente - 12 h
ltdn = (ltdn + 24) % 24
p("PULSE A5.6.2 - Verifica GMAT (Sole + Luna, JGM3 4x4, senza resistenza dell'aria)")
p("Inclinazione media (Brouwer): inizio %.4f, fine %.4f deg; min %.4f, max %.4f" % (inc[0], inc[-1], inc.min(), inc.max()))
p("Deriva lineare dell'inclinazione: %+.4f deg/anno  (MDR -0,33; calcolo Python -0,030)" % pend)
p("SMA media: %.2f-%.2f km" % (sma.min(), sma.max()))
p("Ora del nodo discendente (LTDN, Sole medio):")
for a in (0, 0.5, 1, 1.5, 2):
    k = min(int(round(a * 365.25)), len(T) - 1)
    p("  dopo %.1f anni: %02d:%02d" % (a, int(ltdn[k]), round(ltdn[k] % 1 * 60) % 60))
p("  scostamento da 10:30 a fine missione: %+.0f min (nota: l'LTDN iniziale da RAAN 78,7 deg e' %02d:%02d)" % (
    (ltdn[-1] - 10.5) * 60, int(ltdn[0]), round(ltdn[0] % 1 * 60)))
# ---------- eclissi
ev = {}
for l in open("gmat/PULSE_eclissi_2anni.txt"):
    if re.match(r"\d\d \w\w\w \d{4}", l):
        c = l.split()
        num, tot, corpo = int(c[-2]), float(c[-1]), c[-4]
        if corpo == "Earth":
            ev[num] = (data(l[:24]), tot)
nums = sorted(ev)
tini = np.array([jd(ev[k][0]) for k in nums]); dur = np.array([ev[k][1] for k in nums]) / 60
dur = dur[1:-1]; tini = tini[1:-1]               # tolgo la prima e l'ultima, tagliate dall'intervallo
luna = sum(1 for l in open("gmat/PULSE_eclissi_2anni.txt") if " Luna " in l)
p("")
p("Eclissi della Terra: %d (esclusi i due estremi tagliati); eventi con la Luna: %d" % (len(dur), luna))
p("Ombra per orbita (umbra + penombra): min %.2f  max %.2f  media %.2f min" % (dur.min(), dur.max(), dur.mean()))
# confronto con Python (caso calcolato), giorno per giorno
R = np.loadtxt("risultati/luce_eclisse_calcolata.csv", delimiter=",")
g_gmat = tini - tini[0]
d_py = np.interp(g_gmat, R[:, 0], R[:, 6])
diff = (dur - d_py) * 60
p("Differenza GMAT - Python (caso -0,030 deg/anno): media %+.0f s, min %+.0f s, max %+.0f s" % (diff.mean(), diff.min(), diff.max()))
R2 = np.loadtxt("risultati/luce_eclisse_MDR.csv", delimiter=",")
d2 = np.interp(g_gmat, R2[:, 0], R2[:, 6])
p("Differenza GMAT - Python (caso MDR -0,33 deg/anno): media %+.0f s, min %+.0f s, max %+.0f s" % (
    ((dur - d2) * 60).mean(), ((dur - d2) * 60).min(), ((dur - d2) * 60).max()))
p("")
p("Per mese: ombra media e massima per orbita (min)")
t0 = dt.datetime(2026, 1, 1)
mesi = np.array([(t0 + dt.timedelta(days=x)).year * 12 + (t0 + dt.timedelta(days=x)).month for x in g_gmat])
for m in np.unique(mesi):
    s = mesi == m
    p("  %d-%02d  media %.2f  max %.2f" % (m // 12 if m % 12 else m // 12 - 1, m % 12 or 12, dur[s].mean(), dur[s].max()))
txt = "\n".join(out); print(txt)
open("risultati/confronto_gmat.txt", "w").write(txt + "\n")
np.savetxt("risultati/gmat_ltdn_inclinazione.csv", np.column_stack([anni * 365.25, inc, raan, ltdn]), delimiter=",",
           fmt="%.5f", header="giorno,INC_deg,RAAN_deg,LTDN_h")
