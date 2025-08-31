#!/usr/bin/env python3
import json, argparse, sys

def load_json(p):
    with open(p,"r") as f: return json.load(f)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--norm",  default="cert/DM/axion/axion_norm.json",
                    help="File con f_a_hat (adimensionale)")
    ap.add_argument("--units", default="cert/units/eh_units.json",
                    help="File con Mpl_reduced_GeV")
    ap.add_argument("--out",   default="cert/DM/axion/f_a_GeV.json")
    args = ap.parse_args()

    norm  = load_json(args.norm)
    units = load_json(args.units)

    if "f_a_hat" not in norm:
        print("[ERR] f_a_hat mancante in", args.norm, file=sys.stderr)
        sys.exit(1)
    if "Mpl_reduced_GeV" not in units:
        print("[ERR] Mpl_reduced_GeV mancante in", args.units, file=sys.stderr)
        sys.exit(1)

    f_a_hat = float(norm["f_a_hat"])
    Mpl     = float(units["Mpl_reduced_GeV"])
    f_a_GeV = f_a_hat * Mpl  # nessun ad-hoc

    out = {
        "schema_version": 1,
        "f_a_hat": f_a_hat,
        "Mpl_reduced_GeV": Mpl,
        "f_a_GeV": f_a_GeV,
        "note": "EH→GeV via Mpl_reduced; nessun ad-hoc."
    }
    with open(args.out,"w") as f: json.dump(out, f, indent=2)
    print(f"[OK] wrote {args.out}")
    print(f"[OK] f_a = {f_a_GeV:.6e} GeV   (f_a_hat={f_a_hat:.6e}, Mpl={Mpl:.6e} GeV)")

if __name__=="__main__":
    main()
