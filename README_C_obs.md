# C_obs — H(z), distanze e check (Etherington, low-z slope)

Pipeline:
  1) C0: Λ4 da invarianti discreti + ∫a^2 → cert/cosmo/Lambda4.json
  2) H(z): tools/cosmo_cert/cobs_hz.py → cert/cosmo/C_obs/H_curve.{json,csv}
  3) Distanze: tools/cosmo_cert/cobs_distances.py → cert/cosmo/C_obs/distances.{json,csv}
Gate:
  - Etherington (D_L = (1+z)^2 D_A): PASS
  - low-z slope (H0): PASS con metrologia osservativa

File chiave già presenti:
  - cert/units/eh_units.json
  - cert/obs/metrology_cosmo.json
  - cert/obs/matter_EH.json
  - cert/cosmo/Lambda4.json
  - cert/cosmo/C_obs/H_curve.json, H_curve.csv
  - cert/cosmo/C_obs/distances.json, distances.csv
