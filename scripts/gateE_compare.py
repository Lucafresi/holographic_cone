#!/usr/bin/env python3
import json, argparse, os, sys, math

def ok(a,b,abs_tol,rel_tol):
    diff = abs(a-b)
    return diff <= max(abs_tol, rel_tol*max(abs(a),abs(b))), diff

def main():
    ap = argparse.ArgumentParser(description="Gate-E compare: HOLO vs KK (alpha, C_log).")
    ap.add_argument("--holo", default="cert/holo/fit_gateE.json")
    ap.add_argument("--kk",   default="cert/kk/fit_gateE.json")
    ap.add_argument("--out",  default="cert/compare/compare.json")
    ap.add_argument("--abs_tol", type=float, default=2e-10)
    ap.add_argument("--rel_tol", type=float, default=1e-10)
    args = ap.parse_args()

    with open(args.holo) as f: H = json.load(f)
    with open(args.kk)   as f: K = json.load(f)

    pa, da = ok(H["alpha"],  K["alpha"],  args.abs_tol, args.rel_tol)
    pc, dc = ok(H["C_log"],  K["C_log"],  args.abs_tol, args.rel_tol)

    out = {
        "alpha_holo": H["alpha"], "alpha_kk": K["alpha"], "alpha_diff": da, "alpha_pass": pa,
        "C_log_holo": H["C_log"], "C_log_kk": K["C_log"], "C_log_diff": dc, "C_log_pass": pc,
        "abs_tol": args.abs_tol, "rel_tol": args.rel_tol,
    }
    out["PASS"] = pa and pc

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out,"w") as f: json.dump(out,f,indent=2)
    print(json.dumps(out,indent=2))
    sys.exit(0 if out["PASS"] else 1)

if __name__ == "__main__":
    main()
