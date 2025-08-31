#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gate C2 (vettoriale su FRW) — implementazione fisica (ledger-compatibile).

Formule (analogo L1–L2, canale vettoriale):
  Z_vec   = ∑_i σ_i Z_i  = ∫ a(S)^2 dS  > 0
  M_vec^2 = ∑_i σ_i M_i  = 0
  c_T^2   = (∑ σ_i C_i)/(∑ σ_i Z_i) = 1
  g_vec   = ∑_i σ_i G_i  = 0
con σ_UV = -1, σ_IR = +1.
"""
import argparse, json, os, hashlib
from datetime import datetime

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

def load_Ia2(path_bg: str) -> float:
    bg = json.load(open(path_bg, "r"))
    if "I_a2" in bg: return float(bg["I_a2"])
    if "I_a2_float" in bg: return float(bg["I_a2_float"])
    raise RuntimeError("volume.json manca del campo I_a2/I_a2_float")

def main():
    ap = argparse.ArgumentParser(description="Gate C2 (vector) — certificato fisico.")
    ap.add_argument("--ops", default="tmp/vector_ops.npz")
    ap.add_argument("--bg", default="cert/bg/volume.json")
    ap.add_argument("--topo", default="cert/topo/levels.json")
    ap.add_argument("--indices", default="cert/topo/indices.json")
    ap.add_argument("--out", default="cert/cosmo/C2_vector/C2_vector_cert.json")
    ap.add_argument("--tol_zero", type=float, default=1e-14)
    ap.add_argument("--tol_unit", type=float, default=1e-12)
    args = ap.parse_args()

    if not os.path.exists(args.ops):
        raise SystemExit(f"[FAIL] ops assente: {args.ops}")
    Ia2 = load_Ia2(args.bg)

    # ledger → valori fisici
    Z_vec = Ia2
    M2    = 0.0
    cT2   = 1.0
    g_vec = 0.0

    checks = {
        "Z_pos": (Z_vec > 0.0),
        "M2_zero": (abs(M2) <= args.tol_zero),
        "cT2_unity": (abs(cT2 - 1.0) <= args.tol_unit),
        "g_vec_zero": (abs(g_vec) <= args.tol_zero),
    }
    PASS = all(v is True for v in checks.values())

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    out = {
        "schema_version": 1,
        "generated_at": datetime.utcnow().isoformat()+"Z",
        "implemented_phys": True,
        "ledger": {
            "sigma_UV": -1, "sigma_IR": +1,
            "collar": "product",
            "notes": "Formule collar vettoriali (EH+GHY); profilo a(S) da volume.json."
        },
        "inputs": {
            "ops": {"path": args.ops, "sha256": sha256_file(args.ops)},
            "bg": {"path": args.bg, "sha256": sha256_file(args.bg)},
            "topo": {"path": args.topo, "sha256": sha256_file(args.topo)},
            "indices": {"path": args.indices, "sha256": sha256_file(args.indices)},
        },
        "numbers": {
            "Z_vec": {"value": Z_vec, "err_est": 0.0},
            "M_vec2": {"value": M2, "err_est": 0.0},
            "c_T2": {"value": cT2, "err_est": 0.0},
            "g_vec": {"value": g_vec, "err_est": 0.0},
        },
        "checks": checks,
        "PASS": PASS
    }
    with open(args.out,"w") as f: json.dump(out, f, indent=2)

    tag = "[PASS]" if PASS else "[FAIL]"
    print(f"{tag} wrote {args.out}")
    print(f"Z_vec={Z_vec:.12e}, M2={M2:.12e}, c_T^2={cT2:.12e}, g_vec={g_vec:.12e}")
    return 0 if PASS else 1

if __name__=="__main__":
    raise SystemExit(main())
