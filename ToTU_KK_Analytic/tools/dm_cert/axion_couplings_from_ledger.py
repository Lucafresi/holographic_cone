#!/usr/bin/env python3
import json, argparse
from fractions import Fraction
from collections import defaultdict

# SM content per famiglia (base integrale)
SM = [
  {"name":"Q_L",   "dim3":3, "dim2":2, "Y":Fraction(1,6),  "rep3":"3",    "rep2":"2"},
  {"name":"u_R^c", "dim3":3, "dim2":1, "Y":Fraction(-2,3), "rep3":"3bar", "rep2":"1"},
  {"name":"d_R^c", "dim3":3, "dim2":1, "Y":Fraction(1,3),  "rep3":"3bar", "rep2":"1"},
  {"name":"L_L",   "dim3":1, "dim2":2, "Y":Fraction(-1,2), "rep3":"1",    "rep2":"2"},
  {"name":"e_R^c", "dim3":1, "dim2":1, "Y":Fraction(1,1),  "rep3":"1",    "rep2":"1"}
]
def is_fund3(r): 
    return (r=="3") or (r=="3bar")
def is_doublet(r): 
    return (r=="2")

def loadj(p): 
    with open(p,"r") as f: return json.load(f)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--charges", default="dm_inputs/U1X_charges.json")
    ap.add_argument("--brane",   default="dm_inputs/brane_counts.json")
    ap.add_argument("--norm",    default="cert/DM/axion/axion_norm.json")
    ap.add_argument("--out",     default="cert/DM/axion/axion_couplings.json")
    args=ap.parse_args()

    charges = loadj(args.charges)["per_multiplet"]
    branes  = loadj(args.brane)
    Nfam    = int(branes["N_families_total"])
    # Conteggio totale (somma UV+IR) per ogni multiplet:
    total = defaultdict(int)
    for side in ("UV","IR"):
        for k,v in branes["per_brane"][side].items():
            total[k] += int(v)

    # Coefficienti anomali (totali sul 4D effettivo):
    C = defaultdict(Fraction)
    for fam in SM:
        name=fam["name"]; mult = total[name] * fam["dim3"]*fam["dim2"]
        qx = Fraction(charges[name],1)
        Y  = fam["Y"]
        if is_fund3(fam["rep3"]):
            C["aGG"] += mult * qx          # SU(3)^2-U(1)_X
        if is_doublet(fam["rep2"]):
            C["aWW"] += mult * qx          # SU(2)^2-U(1)_X
        C["aYY"]     += mult * (Y*Y) * qx  # U(1)_Y^2-U(1)_X
        C["aXXX"]    += mult * (qx*qx*qx)  # U(1)_X^3
        C["agrav"]   += mult * qx          # grav^2-U(1)_X  (stessa combinazione di aWW+aGG ma pesa tutte le rep)

    # Normalizzazione dal collar
    norm = loadj(args.norm)
    fhat = float(norm["f_a_hat"])

    # output: interi/razionali in base integrale + versioni “adimensionali” g_hat = C/fhat
    def frac2s(x: Fraction): return f"{x.numerator}/{x.denominator}"

    out = {
      "schema_version": 1,
      "inputs": {
        "charges_file": args.charges,
        "brane_counts_file": args.brane,
        "norm_file": args.norm
      },
      "coeff_integer_basis": {k: frac2s(v) for k,v in C.items()},
      "f_a_hat": fhat,
      "g_hat": { k: float(C[k]) / fhat for k in C }
    }
    with open(args.out,"w") as f: json.dump(out,f,indent=2)
    print(f"[D2] wrote {args.out}")
    print("[D2] integer-basis C:", {k: frac2s(v) for k,v in C.items()})
    print("[D2] g_hat (dimensionless):", {k: f"{float(C[k])/fhat:.6e}" for k in C})

if __name__=="__main__":
    main()
