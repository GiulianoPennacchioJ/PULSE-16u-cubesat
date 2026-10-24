"""PULSE · A5.4 — Figura: spostamento al bordo del campo nella raffica città (0,2 s),
riallineamento a sola traslazione, in funzione dell'istante della raffica.
Uso: python figura_geometria.py -> risultati/geometria_fmc.png"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from geometria_fmc import analisi, SOGLIA_1x1

t = np.arange(0, 23.9, 0.5)
fig, ax = plt.subplots(figsize=(7.2, 4.0))
for eta, col in ((0, '#1f6fb2'), (30, '#d97706'), (45, '#b91c1c')):
    tot = [analisi(eta, x - 0.1, 0.2)[0] * 1e6 for x in t]
    res = [analisi(eta, x - 0.1, 0.2)[3] * 1e6 for x in t]
    ax.plot(t, tot, color=col, lw=1.8, label=f'{eta}° di traverso, sola traslazione')
    ax.plot(t, res, color=col, lw=1.0, ls='--', label=f'{eta}°, con similitudine (zoom + rotazione)')
ax.axhline(SOGLIA_1x1 * 1e6, color='0.25', lw=1, ls=':')
ax.text(23.5, SOGLIA_1x1 * 1e6 + 1.5, 'soglia 1/3 pixel (5,2 µrad)', ha='right', fontsize=8, color='0.25')
ax.set_xlabel('istante della raffica dal passaggio più vicino (s)')
ax.set_ylabel('spostamento all\'angolo del campo (µrad)')
ax.set_xlim(0, 23.85); ax.set_ylim(0, 105)
ax.grid(alpha=0.25); ax.legend(fontsize=7, ncol=3, loc='upper center', bbox_to_anchor=(0.5, -0.2), frameon=False)
for s in ('top', 'right'):
    ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig('risultati/geometria_fmc.png', dpi=200)
