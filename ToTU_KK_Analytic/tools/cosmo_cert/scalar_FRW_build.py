#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, csv, json, os, hashlib
from datetime import datetime
import mpmath as mp
import numpy as np

def sha256_file(path):
    h = hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

def load_csv(path, scol, acol):
    S,A = [],[]
    with open(path,'r',newline='') as f:
        rdr = csv.reader(f)
        for row in rdr:
            if not row or row[0].lstrip().startswith('#'): continue
            try:
                S.append(mp.mpf(row[scol])); A.append(mp.mpf(row[acol]))
            except Exception:
                continue
    return S,A

def load_json(path):
    data = json.load(open(path,'r'))
    if "S" in data and "a" in data:
        S = [mp.mpf(x) for x in data["S"]]
        A = [mp.mpf(x) for x in data["a"]]
        return S,A
    if "samples" in data:
        S = [mp.mpf(s) for s,_ in data["samples"]]
        A = [mp.mpf(a) for _,a in data["samples"]]
        return S,A
    raise ValueError("JSON non riconosciuto: attesi ('S','a') o 'samples'.")

def trapz_Ia2(S,A):
    tot = mp.mpf('0')
    for i in range(len(S)-1):
        dS = S[i+1]-S[i]
        tot += mp.mpf('0.5')*(A[i]*A[i] + A[i+1]*A[i+1])*dS
    return tot

def main():
    ap = argparse.ArgumentParser(description="Build ops pacchetto radion (skeleton).")
    ap.add_argument("--profile", required=True, help="Profilo a(S): CSV o JSON.")
    ap.add_argument("--format", choices=["csv","json"], required=True)
    ap.add_argument("--scol", type=int, default=0)
    ap.add_argument("--acol", type=int, default=1)
    ap.add_argument("--prec", type=int, default=160)
    ap.add_argument("--out", default="tmp/scalar_ops.npz")
    args = ap.parse_args()
    mp.mp.dps = args.prec

    if args.format=="csv":
        S,A = load_csv(args.profile, args.scol, args.acol)
    else:
        S,A = load_json(args.profile)

    if len(S)<2: raise SystemExit("[FAIL] profilo troppo corto.")
    mono = all(S[i+1]>S[i] for i in range(len(S)-1))
    if not mono: raise SystemExit("[FAIL] S non crescente strettamente.")
    nonneg = all(a>=0 for a in A)
    if not nonneg: print("[WARN] a(S) contiene negatività (ammesso ma sconsigliato).")

    Ia2 = trapz_Ia2(S,A)
    meta = {
        "schema_version": 1,
        "generated_at": datetime.utcnow().isoformat()+"Z",
        "profile_path": args.profile,
        "profile_sha256": sha256_file(args.profile),
        "prec": args.prec,
        "S_min": float(S[0]), "S_max": float(S[-1]),
        "n_points": len(S),
        "I_a2_est": float(Ia2),
    }
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    np.savez(args.out,
             S=np.array([float(s) for s in S], dtype=float),
             a=np.array([float(a) for a in A], dtype=float),
             meta=json.dumps(meta))
    print(f"[OK] wrote {args.out}")
    print(f"I_a2_est ≈ {Ia2}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
