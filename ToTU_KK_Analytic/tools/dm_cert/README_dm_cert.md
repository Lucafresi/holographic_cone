# DM Certs — D0-A (necessità GS-axion)

Esegue un test di solvibilità delle anomalie miste U(1)_X per brana con un **unico** livello CS intero per canale.  
Se NON solvibile, con NFF (niente nuova materia 4D), un **termine Green–Schwarz** è **richiesto** (gs_required=true).

**Input**
- `dm_inputs/U1X_charges.json` — cariche intere per multiplet SM
- `dm_inputs/brane_counts.json` — conteggi per brana dei multiplet (in famiglie)

**Output**
- `cert/DM/axion/anomaly_necessity.json` — report PASS/FAIL (gs_required)

