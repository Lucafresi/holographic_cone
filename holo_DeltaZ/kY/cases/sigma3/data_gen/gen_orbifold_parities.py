import os, csv

# Regola Σ3: doublet-triplet split OK, no U(1)'.
# CSV con header: field,parity  e parità in {++, +-, -+, --}
rows = [
  ("Q", "++"),
  ("uR", "+-"),
  ("dR", "+-"),
  ("L", "++"),
  ("eR", "+-"),
  ("H_doublet_1", "++"),
  ("H_triplet_1", "--"),   # proiettato
  # Nessun U(1)' residuo:
  # ("U1prime_field","++")  # NON INSERIRE
]

dst = os.path.join("holo_DeltaZ","kY","cases","sigma3","data","orbifold_parities.csv")
os.makedirs(os.path.dirname(dst), exist_ok=True)
with open(dst,"w",newline="",encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["field","parity"])
    for r in rows: w.writerow(r)
print("wrote:", dst)
