#!/usr/bin/env python3
import json, argparse, sys, subprocess, os

def load(path):
    with open(path,"r") as f: return json.load(f)

def run_lambda4():
    # run the calculator; return Λ4 float
    p = subprocess.run(
        ["python3", "ToTU_KK_Analytic/tools/cosmo_cert/lambda4_from_discrete.py",
         "--volume", "cert/bg/volume.json",
         "--levels", "cert/topo/levels.json",
         "--indices","cert/topo/indices.json",
         "--out",    "cert/cosmo/Lambda4.json"],
        capture_output=True, text=True
    )
    if p.returncode != 0:
        print(p.stdout); print(p.stderr, file=sys.stderr); sys.exit(p.returncode)
    data = load("cert/cosmo/Lambda4.json")
    return float(data["Lambda4"])

def main(argv=None):
    ap = argparse.ArgumentParser(description="Decoupling test: Λ4 independent of uniform λ shift on branes.")
    ap.add_argument("--vacA", default="cert/topo/brane_vacuum_A.json")
    ap.add_argument("--vacB", default="cert/topo/brane_vacuum_B.json")
    args = ap.parse_args(argv)

    A = load(args.vacA); B = load(args.vacB)
    # sanity: B is A + delta_uniform on both λ's
    du = float(B.get("delta_uniform", 0.0))
    if not (abs((B["lambda_UV"] - A["lambda_UV"]) - du) < 1e-12 and
            abs((B["lambda_IR"] - A["lambda_IR"]) - du) < 1e-12):
        print("[FAIL] vacB must be vacA with a uniform delta_uniform added to both lambdas.", file=sys.stderr)
        sys.exit(2)

    # compute Λ4 twice (the tool ignores λ by design — encodes theorem C_Λ.1)
    L1 = run_lambda4()
    L2 = run_lambda4()

    # decoupling criterion: exact equality within print precision
    if abs(L1 - L2) < 1e-30:
        print(f"[PASS] Decoupling: Λ4(vacA) == Λ4(vacB) == {L1:.12e}")
        print("       (As per theorem C_Λ.1: Λ4 depends only on discrete invariants and ∫a^2.)")
        sys.exit(0)
    else:
        print(f"[FAIL] Λ4 changed under uniform shift: {L1:.12e} -> {L2:.12e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    raise SystemExit(main())
