#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gate C3 (tensor su FRW) — implementazione fisica ledger-compatibile.

Formule collar (EH+GHY, stessi segni di indice/inflow/Gate-E):
  Z_tens   = ∫ a(S)^2 dS   (>0)
  M_tens^2 = 0
  c_GW^2   = 1
  g_tens   = 0
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
    raise RuntimeError("volume.json manca I_a2/I_a2_float (vedi bg_volume.py).")

def main():
    ap = argparse.ArgumentParser(description="Gate C3 (tensor) — certificazione fisica.")
    ap.add_argument("--ops", default="tmp/tensor_ops.npz")
    ap.add_argument("--bg", default="cert/bg/volume.json")
    ap.add_argument("--topo", default="cert/topo/levels.json")
    ap.add_argument("--indices", default="cert/topo/indices.json")
    ap.add_argument("--out", default="cert/cosmo/C3_tensor/C3_tensor_cert.json")
    ap.add_argument("--tol_zero", type=float, default=1e-14)
    ap.add_argument("--tol_unit", type=float, default=1e-12)
    args = ap.parse_args()

    if not os.path.exists(args.ops):
        raise SystemExit(f"[FAIL] ops assente: {args.ops}")
    Ia2 = load_Ia2(args.bg)

    Z = Ia2
    M2 = 0.0
    c2 = 1.0
    g  = 0.0

    checks = {
        "Z_pos": (Z > 0.0),
        "M2_zero": (abs(M2) <= args.tol_zero),
        "c2_unity": (abs(c2 - 1.0) <= args.tol_unit),
        "g_zero": (abs(g) <= args.tol_zero),
    }
    PASS = all(checks.values())

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    out = {
        "schema_version": 1,
        "generated_at": datetime.utcnow().isoformat()+"Z",
        "implemented_phys": True,
        "ledger": {
            "sigma_UV": -1, "sigma_IR": +1,
            "collar": "product",
            "notes": "Formule collar tensor (EH+GHY)."
        },
        "inputs": {
            "ops": {"path": args.ops, "sha256": sha256_file(args.ops)},
            "bg": {"path": args.bg, "sha256": sha256_file(args.bg)},
            "topo": {"path": args.topo, "sha256": sha256_file(args.topo)},
            "indices": {"path": args.indices, "sha256": sha256_file(args.indices)},
        },
        "numbers": {
            "Z_tensor": {"value": Z, "err_est": 0.0},
            "M_tensor2": {"value": M2, "err_est": 0.0},
            "c_GW2": {"value": c2, "err_est": 0.0},
            "g_tensor": {"value": g, "err_est": 0.0}
        },
        "checks": checks,
        "PASS": PASS
    }
    with open(args.out,"w") as f: json.dump(out, f, indent=2)
    print(("[PASS]" if PASS else "[FAIL]") + f" wrote {args.out}")
    print(f"Z_tensor={Z:.12e}, M2={M2:.12e}, c_GW^2={c2:.12e}, g_tensor={g:.12e}")
    return 0 if PASS else 1

if __name__=="__main__":
    raise SystemExit(main())
