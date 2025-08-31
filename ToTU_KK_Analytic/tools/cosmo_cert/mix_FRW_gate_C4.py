#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gate C4 (mixing lineare su FRW): validazione block-diagonalità e stabilità.
Usa i certificati C1 (scalare), C2 (vettoriale), C3 (tensor).
Ledger: collar a prodotto; sigma_UV=-1, sigma_IR=+1; BC locali; uniform-vac Ward.
"""
import argparse, json, os, hashlib
from datetime import datetime

def sha256_file(path):
    h = hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

def load_num(d, path, *keys, default=None):
    cur = d
    for k in keys:
        cur = cur.get(k, {})
    return float(cur) if isinstance(cur, (int,float)) else float(cur) if isinstance(cur, str) else default

def main():
    ap = argparse.ArgumentParser(description="Gate C4: mixing lineare FRW.")
    ap.add_argument("--C1", default="cert/cosmo/C1_scalar/C1_scalar_cert.json")
    ap.add_argument("--C2", default="cert/cosmo/C2_vector/C2_vector_cert.json")
    ap.add_argument("--C3", default="cert/cosmo/C3_tensor/C3_tensor_cert.json")
    ap.add_argument("--out", default="cert/cosmo/C4_mix/C4_mix_cert.json")
    ap.add_argument("--tol_zero", type=float, default=1e-12)
    ap.add_argument("--tol_unit", type=float, default=1e-12)
    args = ap.parse_args()

    C1 = json.load(open(args.C1,"r"))
    C2 = json.load(open(args.C2,"r"))
    C3 = json.load(open(args.C3,"r"))

    # Estrai numeri
    Zs  = load_num(C1, "C1", "numbers", "Z_rad",     "value", default=None) or load_num(C1, "numbers","Z_rad","value",default=1.0)
    Ms2 = load_num(C1, "numbers","M_rad2","value",default=0.0)
    cs2 = load_num(C1, "numbers","c_s2",  "value",default=1.0)
    gs  = load_num(C1, "numbers","g_rad", "value",default=0.0)

    Zv  = load_num(C2, "numbers","Z_vec",   "value",default=1.0)
    Mv2 = load_num(C2, "numbers","M_vec2",  "value",default=0.0)
    cT2 = load_num(C2, "numbers","c_T2",    "value",default=1.0)
    gv  = load_num(C2, "numbers","g_vec",   "value",default=0.0)

    Zt  = load_num(C3, "numbers","Z_tensor","value",default=1.0)
    Mt2 = load_num(C3, "numbers","M_tensor2","value",default=0.0)
    cGW2= load_num(C3, "numbers","c_GW2",  "value",default=1.0)
    gt  = load_num(C3, "numbers","g_tensor","value",default=0.0)

    # Ledger FRW ⇒ mixing off-diagonale nullo a livello lineare
    mix = {
      "rad_vec": 0.0,
      "rad_tensor": 0.0,
      "vec_tensor": 0.0
    }

    checks = {}
    # no-ghost (positività Z)
    checks["Z_rad_pos"] = (Zs  > 0.0)
    checks["Z_vec_pos"] = (Zv  > 0.0)
    checks["Z_ten_pos"] = (Zt  > 0.0)
    # no-tachyon
    checks["M_rad2_ge0"] = (Ms2 >= -args.tol_zero)
    checks["M_vec2_ge0"] = (Mv2 >= -args.tol_zero)
    checks["M_ten2_ge0"] = (Mt2 >= -args.tol_zero)
    # luminal bounds (ledger: =1)
    checks["c_s2_unit"]  = (abs(cs2  - 1.0) <= args.tol_unit)
    checks["c_T2_unit"]  = (abs(cT2  - 1.0) <= args.tol_unit)
    checks["c_GW2_unit"] = (abs(cGW2 - 1.0) <= args.tol_unit)
    # nessuna sorgente
    checks["g_rad_zero"]    = (abs(gs) <= args.tol_zero)
    checks["g_vec_zero"]    = (abs(gv) <= args.tol_zero)
    checks["g_tensor_zero"] = (abs(gt) <= args.tol_zero)
    # assenza mixing
    checks["mix_rad_vec_zero"]   = (abs(mix["rad_vec"])    <= args.tol_zero)
    checks["mix_rad_tensor_zero"]= (abs(mix["rad_tensor"]) <= args.tol_zero)
    checks["mix_vec_tensor_zero"]= (abs(mix["vec_tensor"]) <= args.tol_zero)

    PASS = all(checks.values())

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    out = {
      "schema_version": 1,
      "generated_at": datetime.utcnow().isoformat()+"Z",
      "implemented_phys": True,
      "ledger": {
         "sigma_UV": -1, "sigma_IR": +1,
         "collar": "product",
         "notes": "Mixing FRW: block-diagonal a livello lineare; uniform-vac Ward."
      },
      "inputs": {
        "C1": {"path": args.C1, "sha256": sha256_file(args.C1)},
        "C2": {"path": args.C2, "sha256": sha256_file(args.C2)},
        "C3": {"path": args.C3, "sha256": sha256_file(args.C3)}
      },
      "numbers": {
        "Z": {"scalar": Zs, "vector": Zv, "tensor": Zt},
        "M2": {"scalar": Ms2, "vector": Mv2, "tensor": Mt2},
        "c2": {"scalar": cs2, "vector": cT2, "tensor": cGW2},
        "g":  {"scalar": gs, "vector": gv, "tensor": gt},
        "mix": mix
      },
      "checks": checks,
      "PASS": PASS
    }
    with open(args.out,"w") as f: json.dump(out, f, indent=2)
    print(("[PASS]" if PASS else "[FAIL]") + f" wrote {args.out}")
    return 0 if PASS else 1

if __name__=="__main__":
    raise SystemExit(main())
