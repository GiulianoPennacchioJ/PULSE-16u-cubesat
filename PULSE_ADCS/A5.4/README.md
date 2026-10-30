# PULSE · Fase A · A5.4 — Requisiti di stabilità di puntamento

Codici e risultati del passo A5.4. Autore: Giuliano Pennacchio, 24/10/2026.
Decisioni nel registro: D-055 (scopo S3), D-056 (riallineamento geometrico G4, sostituisce D-040),
D-057 (DR-08 riformulato), D-058 (puntamento fuori dalle riprese), D-059 (bilanciamento delle ruote).
Usa il modello 1-asse di `../A5.3/sim1asse.py`.

```bash
pip install -r requirements.txt
python geometria_fmc.py  > risultati/geometria_fmc.txt
python figura_geometria.py                # risultati/geometria_fmc.png
python assestamento.py   > risultati/assestamento.txt
python altri_modi.py     > risultati/altri_modi.txt     # legge ../../PULSE_GMAT/Output_PULSE/PULSE3_contatti_stazioni.txt
python jitter_ruote.py   > risultati/jitter_ruote.txt
python rallentamento_diurno.py > risultati/rallentamento_diurno.txt   # anche risultati/rallentamento_diurno.png
```

| Script | Sotto-passo | Cosa calcola |
|---|---|---|
| `geometria_fmc.py` | A5.4.3 b) | Zoom, rotazione e prospettiva ai bordi del campo durante la FMC notturna; legge d'imbardata; parallasse del rilievo di notte e di giorno (TDI, bande); residuo geometrico della ripresa diurna |
| `figura_geometria.py` | A5.4.3 b) | Figura dello spostamento all'angolo del campo nella raffica città |
| `assestamento.py` | A5.4.3 a) | Slew diurno di 45° e aggancio notturno della linea di vista, assestamento (DR-08), ripuntamento tra due bersagli notturni |
| `altri_modi.py` | A5.4.4 | Perdita di ΔV per errore di spinta; angolo dal nadir delle stazioni e quota di contatto con antenna fissa (durate GMAT); potenza in safe |
| `jitter_ruote.py` | A5.4.5 | Jitter delle ruote a corpo rigido θ = (Ud + Us·d)/I con dati pubblici di sbilanciamento |
| `rallentamento_diurno.py` | A5.4.4 (GNC, 30/10/2026) | Valutazione di D-096: rampe del beccheggio, simulazione 1-asse del rallentamento ×2, conoscenza tra le bande (fattore di scala del giroscopio), scene per passaggio (D-101) |

## Risultati principali

- **Geometria della FMC.** Con riallineamento a sola traslazione, a 30° di traverso l'angolo del campo si sposta di 45 µrad nella raffica città (0,2 s, soglia 5,2) e di 67 µrad nella raffica paesi (0,3 s, soglia 10,5); a nadir va bene solo entro ±0,7 / ±1,1 s dal passaggio. Rotazione della scena 0,39°/s a 30°, 0,56°/s a 45° (= V·tanθ/2R).
- **Rilievo.** Senza DEM il dislivello ammesso è ~50 m per le bande (0,79 s), ~120 m per il TDI (0,15 s), ~300 m per la raffica città. Con un DEM da ~4 m il residuo è < 0,3 µrad.
- **Ripresa diurna ad assetto fisso.** Senza rilievo il residuo geometrico tra righe è < 0,03 pixel: la traslazione basta solo su terreno piatto.
- **DR-08.** Assestamento diurno 1,1–2,6 s (7,1 s prima del commissioning), notturno ~0 s; aggancio notturno 65–112 s prima della finestra.
- **Contatti.** Antenna fissa a nadir: con fascio ±60° resta il 29–37% del tempo di contatto, con ±70° il 97–98%.
- **Rallentamento diurno (D-096, D-101).** Fattibile: coppia ≤ 1,0 mN·m con la rampa dentro lo slew, momento ≤ 0,013 N·m·s, errore in scena ≤ 0,012°; ripresa 4,2 s per scena, +2,1–2,7 s; giorni con ≥ 4 scene 40% → 30%. Il fattore di scala del giroscopio di beccheggio va calibrato in volo a ≤ ~80 ppm (DR-58).
- **Jitter.** Ruote ben bilanciate: 0,03–0,25 µrad (4 ruote) contro 0,74 µrad; il margine si perde con risonanze di Q oltre ~4–20.

## Limiti

Terra sferica non rotante per la geometria; suolo senza rilievo salvo dove indicato; assetto ideale nella parte geometrica;
modello 1-asse per l'assestamento (3-assi in Fase B); jitter a corpo rigido senza modi strutturali; elevazione massima dei
contatti ricavata dalla durata (Terra non rotante).
