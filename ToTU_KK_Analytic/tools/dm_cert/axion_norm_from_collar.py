#!/usr/bin/env python3
import json, argparse
from fractions import Fraction

def loadj(p): 
    with open(p,"r") as f: return json.load(f)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--bg", default="cert/bg/volume.json")
    ap.add_argument("--topo", default="cert/topo/levels.json")
    ap.add_argument("--out", default="cert/DM/axion/axion_norm.json")
    args=ap.parse_args()

    bg = loadj(args.bg)
    topo = loadj(args.topo)

    if "I_a2" in bg:
        Ia2 = float(bg["I_a2"])
    else:
        Ia2 = float(bg["I_a2_float"])
    if Ia2 <= 0:
        raise SystemExit("[FAIL] I_a2 must be > 0.")

    Qax = None
    # cerca un intero quantizzato per l'assione
    # convenzione: levels[?].k_axion se presente, altrimenti fallback a 1
    if "levels" in topo:
        for lvl in topo["levels"]:
            if "k_axion" in lvl:
                Qax = int(lvl["k_axion"]); break
    if Qax is None: Qax = 1

    fhat = (Qax**2 / Ia2) ** 0.5

    out = {
      "schema_version": 1,
      "inputs": {"bg": args.bg, "topo": args.topo},
      "I_a2": Ia2,
      "Q_axion": Qax,
      "f_a_hat": fhat,
      "note": "dimensionless collar normalization; physical units attach via common metrology block (no new continuous params)."
    }
    with open(args.out,"w") as f: json.dump(out,f,indent=2)
    print(f"[D1] wrote {args.out}")
    print(f"[D1] f_a_hat = {fhat:.12e}  (Q_axion={Qax}, I_a2={Ia2})")

if __name__=="__main__":
    main()
