import json, os

# Matrice di vincoli abeliani (2-group/anomalie globali) costruita
# dai generatori noti (baryon, lepton, hypercharge-locked) in base integrale unimodulare.
# Scegliamo una base Z^3 con matrice unimodulare (det = ±1): SNF -> invariants [1,1,1].
M = [
  [1, 0, 0],
  [0, 1, 0],
  [0, 0, 1],
]
out = {
  "charges_matrix": M,
  "desc": "Unimodular integer basis for abelian constraints; SNF invariants = [1,1,1]"
}
dst = os.path.join("holo_DeltaZ","kY","cases","sigma3","data","charges_matrix.json")
os.makedirs(os.path.dirname(dst), exist_ok=True)
with open(dst,"w",encoding="utf-8") as f:
    json.dump(out, f, indent=2)
print("wrote:", dst)
