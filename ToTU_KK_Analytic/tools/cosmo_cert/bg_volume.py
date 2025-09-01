#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, csv, json, os, sys, hashlib
from datetime import datetime
import mpmath as mp

def load_csv(path, scol, acol):
    S, A = [], []
    with open(path, "r", newline="") as f:
        rdr = csv.reader(f)
        for row in rdr:
            if not row or row[0].lstrip().startswith("#"):
                continue
            try:
                s = mp.mpf(row[scol]); a = mp.mpf(row[acol])
            except Exception:
                continue
            S.append(s); A.append(a)
    return S, A

def load_json(path):
    data = json.load(open(path, "r"))
    if "S" in data and "a" in data:
        S = [mp.mpf(x) for x in data["S"]]
        A = [mp.mpf(x) for x in data["a"]]
        return S, A
    if "samples" in data:
        S = [mp.mpf(s) for s,_ in data["samples"]]
        A = [mp.mpf(a) for _,a in data["samples"]]
        return S, A
    raise ValueError("JSON non riconosciuto: usare ('S','a') o 'samples'.")

def trapz_Ia2(S, A):
    terms = []
    for i in range(len(S)-1):
        dS = S[i+1] - S[i]
        terms.append(mp.mpf("0.5")*(A[i]*A[i] + A[i+1]*A[i+1]) * dS)
    return mp.fsum(terms)

def rel_err_refine(S, A):
    I_full = trapz_Ia2(S, A)
    S2, A2 = S[::2], A[::2]
    if len(S2) < 2:
        return mp.mpf("0"), I_full
    I_half = trapz_Ia2(S2, A2)
    denom = max(mp.mpf("1"), abs(I_full))
    return abs(I_full - I_half)/denom, I_full

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def main(argv=None):
    ap = argparse.ArgumentParser(description="Calcola ∫ a(S)^2 dS dal profilo a(S).")
    ap.add_argument("--in", dest="inp", required=True, help="Input (CSV o JSON).")
    ap.add_argument("--format", choices=["csv","json"], required=True)
    ap.add_argument("--scol", type=int, default=0, help="(CSV) colonna S (default 0)")
    ap.add_argument("--acol", type=int, default=1, help="(CSV) colonna a (default 1)")
    ap.add_argument("--prec", type=int, default=160, help="precisione mpmath (default 160)")
    ap.add_argument("--tol", type=float, default=1e-10, help="tolleranza refinement (default 1e-10)")
    ap.add_argument("--out", default="cert/bg/volume.json", help="Output JSON")
    args = ap.parse_args(argv)

    mp.mp.dps = args.prec
    if args.format == "csv":
        S, A = load_csv(args.inp, args.scol, args.acol)
    else:
        S, A = load_json(args.inp)

    if len(S) < 2:
        print("[FAIL] profilo troppo corto (<2).", file=sys.stderr); return 2
    mono = all(S[i+1] > S[i] for i in range(len(S)-1))
    if not mono:
        print("[FAIL] S non strettamente crescente.", file=sys.stderr); return 3
    nonneg = all(a >= 0 for a in A)

    rel_err, I = rel_err_refine(S, A)
    passed = bool(nonneg and rel_err <= mp.mpf(args.tol) and I > 0)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    out = {
        "schema_version": 1,
        "generated_at": datetime.utcnow().isoformat()+"Z",
        "input": {
            "path": args.inp, "format": args.format,
            "sha256": sha256_file(args.inp),
            "n_points": len(S), "s_min": float(S[0]), "s_max": float(S[-1]),
        },
        "checks": {
            "monotone_S": mono, "a_nonneg": nonneg,
            "rel_err_est": float(rel_err), "tol": float(args.tol)
        },
        "I_a2_exact": mp.nstr(I, 50),
        "I_a2_float": float(I),
        "I_a2": float(I),
        "pass": passed
    }
    with open(args.out,"w") as f: json.dump(out, f, indent=2)
    tag = "[OK]" if passed else "[FAIL]"
    print(f"{tag} wrote {args.out}")
    print(f"I_a2 = {mp.nstr(I, 20)}   (rel_err_est={mp.nstr(rel_err,5)})")
    return 0 if passed else 1

if __name__ == "__main__":
    raise SystemExit(main())
