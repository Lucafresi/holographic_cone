# Cosmology Certificates — C0 (Λ₄)
Tool per calcolare Λ₄ da invarianti discreti e certificare il decoupling da shift uniforme delle tensioni.
- `lambda4_from_discrete.py` legge `cert/topo/{levels,indices}.json` e `cert/bg/volume.json` → scrive `cert/cosmo/Lambda4.json`.
- `decoupling_uniform_vacuum_test.py` verifica Λ₄ invariata tra `brane_vacuum_A.json` e `brane_vacuum_B.json`.
