# PULSE · A5.7 Layout

Calcoli del passo A5.7 (layout: massa, volume, posizione dei componenti, baricentro e inerzie del satellite; responsabile Giuliano, D-113 Proposta).

## Sistema di riferimento (D-114, Proposta)

- Origine nel **centro geometrico** dell'involucro tra i binari (226,3 × 226,3 × 454 mm).
- **+X** verso la velocità (direzione di spinta; ugello della REGULUS sulla faccia −X).
- **+Y** normale all'orbita, dal lato del Sole (β > 0; faccia −Y dei radiatori del payload, D-095).
- **+Z** verso lo zenit, lungo l'asse lungo; il telescopio guarda verso −Z (faccia a nadir).
- In assetto nominale coincide con il riferimento orbitale di A5.6 (`PULSE_EPS/A5.6/pannelli_config.py`).
- Dati del payload (`PULSE_A5_Payload_calcoli/PULSE_payload_masse_posizioni.csv`, Z dalla faccia a nadir):
  Z satellite = Z CSV − 227 mm; X e Y invariati.

## Sotto-passi (nell'ordine di lavoro approvato il 30/10/2026)

| Sotto-passo | Contenuto | Stato |
|---|---|---|
| A5.7.1 | Responsabili (D-113) e sistema di riferimento (D-114) | Chiuso (decisioni Proposte) |
| A5.7.3 | REGULUS: dimensioni, ugello, calore verso il satellite, temperature, preriscaldamento | Da fare |
| A5.7.2 | Lista componenti di piattaforma: massa, dimensioni e limiti di temperatura dai datasheet | Da fare |
| A5.7.4 | Disposizione interna e facce esterne (bozza subito a Giuseppe per il termico) | Da fare |
| A5.7.5 | Stivaggio delle ali (6, posto per 8) | Da fare |
| A5.7.6 | Bilancio di massa | Da fare |
| A5.7.7 | Baricentro (iodio pieno/vuoto, ali chiuse/aperte) | Da fare |
| A5.7.8 | Inerzie e verifiche GNC (D-043, DR-22, DR-61) | Da fare |
| A5.7.9 | Pacchetto dati per il termico (D-110) | Da fare |
| A5.7.10 | Chiusura: registro, requisiti, rischi, budget, report | Da fare |

## File

| File | Sotto-passo | Cosa fa |
|---|---|---|
| `profilo_spinta.py` | A5.7 (dati per A5.8) | Minuti di spinta per orbita, accensioni e tratti continui per Sole medio, limite dei 6 pannelli e Sole alto, dal modello A5.6.7 (senza cambiarlo) |

Uso: `python profilo_spinta.py`. Risultati in `risultati/`. Richiede numpy e matplotlib (come A5.6, da cui importa).
