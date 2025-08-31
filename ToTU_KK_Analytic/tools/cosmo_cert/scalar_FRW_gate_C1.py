#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, json, os, hashlib
from datetime import datetime
import numpy as np

def sha256_file(path):
    h = hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser(description="C1 scalar gate (skeleton).")
    ap.add_argument("--ops", default="tmp/scalar_ops.npz")
    ap.add_argument("--bg", default="cert/bg/volume.json")
    ap.add_argument("--topo", default="cert/topo/levels.json")
    ap.add_argument("--indices", default="cert/topo/indices.json")
    ap.add_argument("--out", default="cert/cosmo/C1_scalar/C1_scalar_cert.json")
    ap.add_argument("--cs2", type=float, default=1.0)
    args = ap.parse_args()

    pkg = np.load(args.ops, allow_pickle=True)
    meta = json.loads(str(pkg["meta"].tolist()))
    I_bg = json.load(open(args.bg,"r"))
    I_a2 = float(I_bg.get("I_a2", I_bg.get("I_a2_float", 0.0)))

    Z_rad = float(I_a2)
    M2 = 0.0
    cs2 = float(args.cs2)
    g_rad = 0.0

    checks = {
        "Z_pos": (Z_rad > 0.0),
        "M2_nonneg": (M2 >= 0.0),
        "cs2_in_0_1": (0.0 < cs2 <= 1.0 + 1e-12),
        "ward_match": None
    }
    PASS = all(v is True for v in checks.values() if v is not None)

    out = {
        "schema_version": 1,
        "generated_at": datetime.utcnow().isoformat()+"Z",
        "implemented_phys": False,
        "inputs": {
            "ops": {"path": args.ops, "sha256": sha256_file(args.ops)},
            "bg": {"path": args.bg, "sha256": sha256_file(args.bg)},
            "topo": {"path": args.topo, "sha256": sha256_file(args.topo)},
            "indices": {"path": args.indices, "sha256": sha256_file(args.indices)},
        },
        "numbers": {
            "Z_rad": {"value": Z_rad, "err_est": 0.0},
            "M_rad2": {"value": M2, "err_est": 0.0},
            "c_s2": {"value": cs2, "err_est": 0.0},
            "g_rad": {"value": g_rad, "err_est": None},
        },
        "checks": checks,
        "PASS": PASS,
        "meta": {
            "profile_sha256": meta.get("profile_sha256"),
            "n_points": meta.get("n_points"),
            "S_range": [meta.get("S_min"), meta.get("S_max")],
        }
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out,"w") as f: json.dump(out, f, indent=2)
    tag = "[PASS]" if PASS else "[FAIL]"
    print(f"{tag} wrote {args.out}")
    print(f"Z_rad={Z_rad:.6e}, M2={M2:.6e}, c_s^2={cs2:.6e} (skeleton)")
    return 0 if PASS else 1

if __name__=="__main__":
    raise SystemExit(main())
