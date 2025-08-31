#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C2 builder: prepara un file 'ops' (hashabile) e stima grezza di ∫ a(S)^2 dS
dalla curva a_profile (CSV), senza dipendenze esterne.
"""
import argparse, csv, json, os, hashlib
from datetime import datetime

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

def trapz_int_a2(csv_path: str, scol: int, acol: int):
    S, A = [], []
    with open(csv_path, "r") as f:
        r = csv.reader(f)
        header = next(r, None)
        for row in r:
            if not row: continue
            S.append(float(row[scol])); A.append(float(row[acol]))
    if len(S) < 2:
        return 0.0, 0
    I = 0.0
    for i in range(len(S)-1):
        a2i = A[i]*A[i]; a2j = A[i+1]*A[i+1]
        dS = S[i+1]-S[i]
        I += 0.5*(a2i + a2j)*dS
    return I, len(S)

def main():
    ap = argparse.ArgumentParser(description="C2 builder (vector FRW).")
    ap.add_argument("--profile", default="cert/bg/a_profile.csv")
    ap.add_argument("--format", default="csv")
    ap.add_argument("--scol", type=int, default=0)
    ap.add_argument("--acol", type=int, default=1)
    ap.add_argument("--out", default="tmp/vector_ops.npz")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    I_est, npts = trapz_int_a2(args.profile, args.scol, args.acol)
    payload = {
        "schema_version": 1,
        "generated_at": datetime.utcnow().isoformat()+"Z",
        "profile": args.profile,
        "sha256_profile": sha256_file(args.profile),
        "n_points": npts,
        "I_a2_est_trapz": I_est
    }
    # salviamo JSON, estensione .npz è solo convenzione di naming
    with open(args.out, "w") as f:
        json.dump(payload, f, indent=2)
    print("[OK] wrote", args.out)
    print(f"I_a2_est ≈ {I_est}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
