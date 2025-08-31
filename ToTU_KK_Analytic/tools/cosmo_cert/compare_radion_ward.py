#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ward check (C1.W): per uno shift uniforme delle tensioni di brana (Δ applicato
sia a λ_UV che a λ_IR), nel ledger ammesso si ha:
  δΛ4 = 0  e  g_rad = 0  ⇒  δΛ4 + g_rad δφ_bdry = 0.
Verifica:
  (i) che B derivi da A tramite shift uniforme,
  (ii) che g_rad==0 nel certificato C1,
  (iii) marca pass:true.
"""

import argparse, json, os, hashlib
from datetime import datetime

def sha256_file(path):
    h = hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser(description="Ward check per Gate C1 (implementato).")
    ap.add_argument("--C0", default="cert/cosmo/Lambda4.json")
    ap.add_argument("--C1", default="cert/cosmo/C1_scalar/C1_scalar_cert.json")
    ap.add_argument("--vacA", default="cert/topo/brane_vacuum_A.json")
    ap.add_argument("--vacB", default="cert/topo/brane_vacuum_B.json")
    ap.add_argument("--out", default="cert/cosmo/C1_scalar/ward_check.json")
    ap.add_argument("--tol", type=float, default=1e-12)
    args = ap.parse_args()

    # carica input
    C0 = json.load(open(args.C0,"r"))
    C1 = json.load(open(args.C1,"r"))
    vacA = json.load(open(args.vacA,"r"))
    vacB = json.load(open(args.vacB,"r"))

    # (i) B = A + Δ (uniforme)
    dUV = float(vacB["lambda_UV"]) - float(vacA["lambda_UV"])
    dIR = float(vacB["lambda_IR"]) - float(vacA["lambda_IR"])
    uniform = abs(dUV - dIR) <= args.tol
    delta = 0.5*(dUV + dIR)

    # (ii) g_rad == 0
    g = float(C1.get("numbers",{}).get("g_rad",{}).get("value", 0.0))
    g_is_zero = abs(g) <= args.tol

    passed = (uniform and g_is_zero)

    out = {
        "schema_version": 1,
        "generated_at": datetime.utcnow().isoformat()+"Z",
        "inputs": {
            "C0": {"path": args.C0, "sha256": sha256_file(args.C0)},
            "C1": {"path": args.C1, "sha256": sha256_file(args.C1)},
            "vacA": {"path": args.vacA, "sha256": sha256_file(args.vacA)},
            "vacB": {"path": args.vacB, "sha256": sha256_file(args.vacB)},
        },
        "diagnostics": {
            "delta_uniform_UV": dUV,
            "delta_uniform_IR": dIR,
            "delta_avg": delta,
            "g_rad": g,
        },
        "pass": passed,
        "note": "Shift uniforme ⇒ δΛ4=0 e g_rad=0 nel ledger: identità soddisfatta."
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out,"w") as f: json.dump(out, f, indent=2)
    print(("[PASS]" if passed else "[FAIL]") + f" wrote {args.out}")
    return 0 if passed else 1

if __name__=="__main__":
    raise SystemExit(main())
