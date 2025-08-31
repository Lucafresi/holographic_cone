#!/usr/bin/env python3
import json, argparse, sys
from fractions import Fraction

def load_json(path):
    with open(path,"r") as f: return json.load(f)

def effective_level(kappa, mod):
    if mod is None: return kappa
    # riportiamo kappa in [0, mod-1]
    return ((kappa % mod) + mod) % mod

def main(argv=None):
    ap = argparse.ArgumentParser(description="Compute Λ4 from discrete invariants: Λ4 = Q_inv / ∫a^2.")
    ap.add_argument("--volume", default="cert/bg/volume.json")
    ap.add_argument("--levels", default="cert/topo/levels.json")
    ap.add_argument("--indices", default="cert/topo/indices.json")
    ap.add_argument("--out",     default="cert/cosmo/Lambda4.json")
    args = ap.parse_args(argv)

    vol = load_json(args.volume)
    I_a2 = float(vol.get("I_a2", 0.0))
    if not (I_a2 > 0.0):
        print("[FAIL] I_a2 must be > 0.", file=sys.stderr); sys.exit(2)

    levels = load_json(args.levels).get("levels", [])
    indices = load_json(args.indices).get("indices", [])

    # map by name
    L = {d["name"]: (int(d["kappa"]), (int(d["mod"]) if d.get("mod") is not None else None)) for d in levels}
    I = {d["name"]: Fraction(d["I"]).limit_denominator() for d in indices}

    # sanity: names must match subset
    missing_in_I = [n for n in L.keys() if n not in I]
    if missing_in_I:
        print(f"[FAIL] Missing indices for: {missing_in_I}", file=sys.stderr); sys.exit(3)

    Q_inv = Fraction(0,1)
    breakdown = []
    for name, (kappa, mod) in L.items():
        kap_eff = effective_level(kappa, mod)
        term = Fraction(kap_eff, 1) * I[name]
        Q_inv += term
        breakdown.append({
            "name": name,
            "kappa": kappa,
            "mod": mod,
            "kappa_eff": kap_eff,
            "I": str(I[name]),
            "contrib": str(term)
        })

    Lambda4 = float(Q_inv) / I_a2
    out = {
        "I_a2": I_a2,
        "Q_inv_exact": str(Q_inv),
        "Q_inv_float": float(Q_inv),
        "Lambda4": Lambda4,
        "breakdown": breakdown,
        "notes": "Λ4 computed from discrete invariants only; independent of brane vacua (decoupling)."
    }
    with open(args.out, "w") as f: json.dump(out, f, indent=2)
    print(f"[OK] wrote {args.out}")
    print(f"[OK] Λ4 = {Lambda4:.12e}  (Q_inv = {float(Q_inv):.6g},  I_a2 = {I_a2:.6g})")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
