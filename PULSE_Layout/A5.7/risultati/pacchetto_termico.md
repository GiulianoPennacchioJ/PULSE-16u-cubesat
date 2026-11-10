# PULSE A5.7.9 - Pacchetto dati per il termico (componenti di Giuliano)

Sistema D-114 (origine nel centro geometrico, X velocità, Y lato Sole, Z zenit); layout L1b + ali W1, masse del budget (A5.7.7). Potenze nominali dal foglio Potenza del budget, senza margini. Motore in spinta: 50 W d'ingresso, ~48,5 W di calore, di cui all'interno dall'attacco TBC (15 W nel modello termico, R-57). Radio S in scarico: 15 W d'ingresso, ~13,7 W di calore.

| Componente | Centro X / Y / Z (mm) | Ripresa diurna | Ripresa notturna | Spinta | Scarico dati | Riposo / safe | In funzione (°C) | Attacco |
|---|---|---|---|---|---|---|---|---|
| REGULUS: blocco motore (ugello su -X) | -88.7 / 3.9 / 30.5 | 0 | 0 | 50 | 0 | 0 | -25 / 70 | fetta -X, sporge 37 mm; staffa >= 1 W/K alla parete -Y (DR-72); radiatore dell'ugello su -X |
| REGULUS: serbatoio dello iodio | -88.7 / 3.9 / -69.5 | 0 | 0 | 0 | 0 | 0 | -25 / 70 | fetta -X sotto il motore; riscaldato dall'unita' (linea ~95 C) |
| Batteria 4S3P (sotto la pila delle schede) | 43 / 70 / -79 | 0 | 0 | 0 | 0 | 0 | 0 / 45 | fetta +Y sotto l'IMU (carica 0/+45, scarica -20/+60); riscaldatore 6 W di riserva |
| PCDU (P60), nella pila delle schede | -41.5 / -65.2 / -176.0 | 0.6 | 0.6 | 0.6 | 0.6 | 0.6 | -35 / 85 | pila delle schede, di taglio contro la parete -Y (DR-70, ~1 W/K per scheda) |
| IMU (inviluppo KVH 1750) | 25 / 70 / 3 | 5 | 5 | 5 | 5 | 5 | -40 / 75 | fetta +Y a meta' altezza |
| Star tracker 1 (paraluce corto, verso +Z) | -70 / 70 / 193 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | -40 / 50 | testa sotto la faccia +Z, paraluce che sporge |
| Star tracker 2 (paraluce corto, verso +Z) | 75 / 58 / 193 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | -40 / 50 | testa sotto la faccia +Z, paraluce che sporge |
| Gruppo 4 ruote in piramide (ingombro TBC) | 43 / 70 / -170 | 4 | 4 | 4 | 4 | 4 | -20 / 60 | fondo della fetta +Y (picco +16 W per ~60 s negli slew) |
| Magnetorquer X | 37.6 / -105 / 192 | 0 | 0 | 1 | 0 | 1 | -20 / 60 | fascia sopra il telescopio |
| Magnetorquer Y | -10 / -43 / 215 | 0 | 0 | 1 | 0 | 1 | -20 / 60 | fascia sopra il telescopio |
| Magnetorquer Z | -100 / 100 / 0 | 0 | 0 | 1 | 0 | 1 | -20 / 60 | angolo -X/+Y, verticale |
| Magnetometro (lontano dalla REGULUS) | 80 / -50 / 212 | 0.75 | 0.75 | 0.75 | 0.75 | 0.75 | TBD / TBD | fascia sopra il telescopio verso +X (prova -25/+70) |
| Ricevitore GNSS | -70 / 85 / 100 | 0.125 | 0.125 | 0.125 | 0.125 | 0.125 | -40 / 85 | fetta -X, angolo +Y |
| Computer di bordo | -104.8 / -66.2 / -176.0 | 0.4 | 0.4 | 0.4 | 0.4 | 0.4 | -25 / 65 | pila delle schede contro la -Y (DR-70) |
| Radio S XLink-S | -85.3 / -66.2 / -176.0 | 0 | 0 | 0 | 15 | 0 | -20 / 50 | pila delle schede contro la -Y (DR-70) |
| Radio VHF/UHF | -64.5 / -66.2 / -176.0 | 0.48 | 0.48 | 0.48 | 0.48 | 0.48 | -10 / 45 | pila delle schede contro la -Y (DR-70) |

Totale nominale dei componenti elencati (W): Ripresa diurna 12.4, Ripresa notturna 12.4, Spinta 65.4, Scarico dati 27.4, Riposo / safe 15.4; in piu' 0,3 W dei 6 sensori solari sulle facce esterne (P-06) -> attesa 12,7 W come in A5.6.8

Facce esterne: -Y radiatore di piattaforma 600 cm² in basso (D-129) + sensore notturno ~125 cm² in alto (D-130); +Y e -Y ali chiuse (3 per lato, cerniere sullo spigolo +Z, DR-69); -X ugello e radiatore del motore; +Z star tracker, patch S, antenna GNSS, UHF; -Z apertura del telescopio e patch S. MLI del telescopio staccata di qualche mm dal pannello del radiatore.
