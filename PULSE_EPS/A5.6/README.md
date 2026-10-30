# PULSE · A5.6 Potenza

Calcoli del passo A5.6 (bilancio di potenza ed EPS di piattaforma, responsabile Giuliano, D-087).

| File | Sotto-passo | Cosa fa |
|---|---|---|
| `luce_eclisse.py` | A5.6.2 | Angolo beta, ombra per orbita, deriva dell'LTDN e posizione dei passaggi sull'Italia su 2 anni (dal 1/1/2026), nei due casi di deriva dell'inclinazione |
| `deriva_inclinazione.py` | A5.6.2 | Deriva secolare dell'inclinazione dovuta al Sole (media dell'equazione di Gauss) |
| `figura_luce.py` | A5.6.2 | Figura LTDN, beta e ombra |
| `gmat_blocchi_A5_6_2.txt` | A5.6.2 | Blocchi GMAT di verifica (eclipse locator e inclinazione media giornaliera) |

Uso: `python luce_eclisse.py 2026`, poi `python figura_luce.py`. Risultati in `risultati/`.
Richiede numpy e matplotlib.
