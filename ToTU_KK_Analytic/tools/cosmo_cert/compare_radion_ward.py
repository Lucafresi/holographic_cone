#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, json, os, hashlib
from datetime import datetime

def sha256_file(path):
    h = hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser(description="Ward check (skeleton).")
    ap.add_argument("--C0", default="cert/cosmo/Lambda4.json")
    ap.add_argument("--C1", default="cert/cosmo/C1_scalar/C1_scalar_cert.json")
    ap.add_argument("--out", default="cert/cosmo/C1_scalar/ward_check.json")
    args = ap.parse_args()

    C0 = json.load(open(args.C0,"r"))
    C1 = json.load(open(args.C1,"r"))

    out = {
        "schema_version": 1,
        "generated_at": datetime.utcnow().isoformat()+"Z",
        "implemented": False,
        "inputs": {
            "C0": {"path": args.C0, "sha256": sha256_file(args.C0)},
            "C1": {"path": args.C1, "sha256": sha256_file(args.C1)},
        },
        "numbers": {
            "Lambda4": C0.get("Lambda4"),
            "g_rad": C1.get("numbers",{}).get("g_rad",{}).get("value"),
        },
        "pass": None,
        "note": "Skeleton: implementare δΛ4 + g_rad δφ_bdry ≈ 0 con deformazioni ammesse (ledger)."
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out,"w") as f: json.dump(out, f, indent=2)
    print(f"[INFO] wrote {args.out} (skeleton; no PASS/FAIL)")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
