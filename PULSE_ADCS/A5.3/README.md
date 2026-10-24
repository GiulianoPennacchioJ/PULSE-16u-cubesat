# PULSE · Fase A · A5.3 — Dimensionamento ADCS (analisi di primo ordine)

Codici e risultati del sotto-passo A5.3 (b, c, d, e). Autore: Giuliano Pennacchio, 24/10/2026.
Decisioni di riferimento nel registro: D-039 (metodo 1-asse), D-043 (orientamento L1 e inerzie),
D-044 (profilo FMC F2, F1 come stress), D-045 (slew 45° in ≤ 60 s),
D-046 (controllo K3), D-047 (baricentro), D-048 (ruote W3), D-049 (magnetorquer M3).

## Installazione

```bash
pip install -r requirements.txt     # numba è facoltativo ma rende la simulazione ~100x più veloce
```

## Script

| Script | Sotto-passo | Cosa calcola | Uscita |
|---|---|---|---|
| `inerzie.py` | A5.3 b) | Inviluppo d'inerzia del 16U (30–36 kg, caso pieno e guscio) per i layout L1/L2/L3 | `risultati/inerzie.txt` |
| `cinematica.py` | A5.3 c) | Finestre di ripresa, velocità e accelerazione della linea di vista, slew, rampe FMC | `risultati/cinematica.txt` |
| `rotazione.py` | A5.3 c) | Effetto della rotazione terrestre (velocità a terra, deriva laterale) e dell'eccentricità | `risultati/rotazione.txt` |
| `sim1asse.py` | A5.3 c) | Simulazione 1-asse in anello chiuso della FMC notturna, 48 combinazioni | `risultati/sim1asse_risultati.csv`, `risultati/sim1asse_esempio.png` |
| `sensibilita.py` | A5.3 c) | Inerzia nota al controllore, banda intermedia, quota minima | `risultati/sensibilita.txt` |
| `disturbi.py` | A5.3 d) | Densità (GMAT e MSIS), coppie di disturbo, momento accumulato. Legge `../../PULSE_GMAT/Output_PULSE/Mantenimento_F129.txt` | `risultati/disturbi.txt` |
| `desaturazione.py` | A5.3 e) | Scarico magnetico delle ruote in un giorno (4,2 h di spinta) con dipoli 1,2 / 2,0 / 2,5 A·m² | `risultati/desaturazione.txt` |

```bash
python inerzie.py > risultati/inerzie.txt
python cinematica.py > risultati/cinematica.txt
python rotazione.py > risultati/rotazione.txt
python sim1asse.py
python sensibilita.py
python disturbi.py > risultati/disturbi.txt
python desaturazione.py > risultati/desaturazione.txt
```

I semi del generatore casuale sono fissi: rilanciando si ottengono gli stessi numeri.

## Modello della simulazione 1-asse

Catena in anello chiuso, passo 1 ms:

```
guida (linea di vista) → controllo PD + anticipo di coppia → ruota (ritardo 20 ms)
   → dinamica  I·dω/dt = coppia ruota + disturbo
   → giroscopio (rumore bianco + bias) → stima d'assetto → controllo
```

- **Guida.** Angolo inerziale della linea di vista verso un bersaglio sotto la traccia.
  F2: inseguimento dal bordo della finestra a 30°. F1: assetto fisso, rampa a coppia costante, aggancio 2 s prima del passaggio.
- **Controllo.** `u = Î·α_ref + Kp·(θ_ref − θ_stimato) + Kd·(ω_ref − ω_misurato)`, con `Kp = Î·ωb²`, `Kd = 2·ζ·Î·ωb`, ζ = 0,7.
  Î = 0,69 kg·m² è l'inerzia *nominale* che il controllore conosce; quella vera è 0,64 o 1,14 kg·m².
- **Ruota di prova.** 7 mN·m, 0,1 N·m·s (classe EarthNext), ritardo del primo ordine di 20 ms (TBC).
- **Giroscopio.** MEMS (ARW 0,15°/√h, bias 5°/h) e alta qualità (0,01°/√h, 0,5°/h): valori tipici di classe, da verificare sui datasheet in A5.3 f).
  Star tracker spento durante l'inseguimento: l'assetto viene solo dall'integrazione del giroscopio.
- **Disturbo.** 10⁻⁵ N·m costante (EarthNext, Tab. 4), da aggiornare in A5.3 d).

**Metriche.** Il mosso di ogni scatto da 20 ms è il picco-picco dell'errore di puntamento *vero* (non stimato),
confrontato con 5,2 µrad (DR-10). APE = errore massimo nella finestra (DR-15, 0,1°).
Per ogni combinazione si riporta il caso peggiore su 5 ripetizioni con rumore diverso.

## Limiti (da superare con la simulazione 3-assi in Fase B)

Un solo asse: niente accoppiamenti tra gli assi né prodotti d'inerzia; niente modi flessibili dei pannelli
né jitter delle ruote; bias costante nella finestra; Terra sferica non rotante (effetto sulla velocità a terra < 1%,
vedi `rotazione.py`); bersaglio solo sotto la traccia.

## Risultati principali

- **F2 rispetta DR-10** con banda 1 rad/s su tutto l'inviluppo: mosso peggiore 2,2–3,7 µrad (MEMS) e ≤ 0,5 µrad (alta qualità) contro 5,2 µrad.
- Con banda 0,3 rad/s e inerzia vera molto più alta di quella nominale (1,14 contro 0,69) il 10% degli scatti esce dalla soglia e l'APE arriva a 0,22°; con l'inerzia nota il problema sparisce.
- Con il giroscopio MEMS e lo star tracker spento l'APE resta 0,067–0,078°, vicino al limite di 0,1°.
- F1 a 3 mN·m si assesta in 0–4 s; F1 a 7 mN·m pianificato sull'inerzia nominale satura la ruota se l'inerzia vera è massima.
- Coppia F2 ≤ 1,2 mN·m, momento ≤ 0,030 N·m·s.
- **Disturbi (d).** Densità dimensionante 4,6·10⁻¹¹ kg/m³ (MSIS, F10.7 181, Ap 50). La spinta disallineata domina: 1,1·10⁻⁵ N·m con baricentro a 10 mm, 9,9·10⁻⁵ N·m al limite del deployer (90 mm). Disturbi fino a 10⁻⁴ N·m non cambiano il mosso delle riprese.
- **Scarico (e).** Con baricentro a 10 mm il momento massimo nel giorno è 0,045 N·m·s con 2,0 o 2,5 A·m²; con baricentro a 20 mm 0,154 (2,0 A·m²) e 0,116 (2,5 A·m²). La coppia sull'asse di imbardata è la più difficile da scaricare.
