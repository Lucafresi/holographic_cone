#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ward check (C3): sotto shift uniforme delle tensioni di brana (Δ, Δ),
il canale tensor non viene sorgentato: g_tensor=0 (ledger).
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
    ap = argparse.ArgumentParser(description="Ward tensor (C3).")
    ap.add_argument("--C3", default="cert/cosmo/C3_tensor/C3_tensor_cert.json")
    ap.add_argument("--vacA", default="cert/topo/brane_vacuum_A.json")
    ap.add_argument("--vacB", default="cert/topo/brane_vacuum_B.json")
    ap.add_argument("--out", default="cert/cosmo/C3_tensor/ward_check.json")
    ap.add_argument("--tol", type=float, default=1e-12)
    args = ap.parse_args()

    C3 = json.load(open(args.C3,"r"))
    A  = json.load(open(args.vacA,"r"))
    B  = json.load(open(args.vacB,"r"))

    dUV = float(B["lambda_UV"]) - float(A["lambda_UV"])
    dIR = float(B["lambda_IR"]) - float(A["lambda_IR"])
    uniform = abs(dUV - dIR) <= args.tol

    g = float(C3.get("numbers",{}).get("g_tensor",{}).get("value", 0.0))
    g_is_zero = abs(g) <= args.tol

    passed = (uniform and g_is_zero)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    out = {
        "schema_version": 1,
        "generated_at": datetime.utcnow().isoformat()+"Z",
        "inputs": {
            "C3": {"path": args.C3, "sha256": sha256_file(args.C3)},
            "vacA": {"path": args.vacA, "sha256": sha256_file(args.vacA)},
            "vacB": {"path": args.vacB, "sha256": sha256_file(args.vacB)},
        },
        "diagnostics": {
            "delta_uniform_UV": dUV,
            "delta_uniform_IR": dIR,
            "g_tensor": g
        },
        "pass": passed,
        "note": "Shift uniforme ⇒ nessuna sorgente tensoriale: g_tensor=0 (ledger)."
    }
    with open(args.out,"w") as f: json.dump(out, f, indent=2)
    print(("[PASS]" if passed else "[FAIL]") + f" wrote {args.out}")
    return 0 if passed else 1

if __name__=="__main__":
    raise SystemExit(main())
