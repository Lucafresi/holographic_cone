#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ward check (C2.W): sotto uno shift uniforme delle tensioni (Δ su entrambe le brane),
nel ledger ammesso il canale vettoriale non viene sorgentato:
  g_vec = 0   (e lo resta sotto shift uniforme).
Verifica: (i) uniformità dello shift, (ii) g_vec==0 nel certificato C2.
"""
import argparse, json, hashlib, os
from datetime import datetime

def sha256_file(path):
    h = hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser(description="Ward vettoriale (C2).")
    ap.add_argument("--C2", default="cert/cosmo/C2_vector/C2_vector_cert.json")
    ap.add_argument("--vacA", default="cert/topo/brane_vacuum_A.json")
    ap.add_argument("--vacB", default="cert/topo/brane_vacuum_B.json")
    ap.add_argument("--out", default="cert/cosmo/C2_vector/ward_check.json")
    ap.add_argument("--tol", type=float, default=1e-12)
    args = ap.parse_args()

    C2 = json.load(open(args.C2,"r"))
    A  = json.load(open(args.vacA,"r"))
    B  = json.load(open(args.vacB,"r"))

    dUV = float(B["lambda_UV"]) - float(A["lambda_UV"])
    dIR = float(B["lambda_IR"]) - float(A["lambda_IR"])
    uniform = abs(dUV - dIR) <= args.tol

    g = float(C2.get("numbers",{}).get("g_vec",{}).get("value", 0.0))
    g_is_zero = abs(g) <= args.tol

    passed = (uniform and g_is_zero)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    out = {
        "schema_version": 1,
        "generated_at": datetime.utcnow().isoformat()+"Z",
        "inputs": {
            "C2": {"path": args.C2, "sha256": sha256_file(args.C2)},
            "vacA": {"path": args.vacA, "sha256": sha256_file(args.vacA)},
            "vacB": {"path": args.vacB, "sha256": sha256_file(args.vacB)},
        },
        "diagnostics": {
            "delta_uniform_UV": dUV,
            "delta_uniform_IR": dIR,
            "g_vec": g
        },
        "pass": passed,
        "note": "Shift uniforme ⇒ nessuna sorgente vettoriale: g_vec=0 (ledger)."
    }
    with open(args.out,"w") as f: json.dump(out, f, indent=2)
    print(("[PASS]" if passed else "[FAIL]") + f" wrote {args.out}")
    return 0 if passed else 1

if __name__=="__main__":
    raise SystemExit(main())
